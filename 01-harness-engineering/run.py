"""Run the experiment: every task through every chosen harness, same model.

    python run.py                          # naive vs engineered, all tasks, once
    python run.py --repeats 3              # three runs each (temperature 0 is not fully deterministic)
    python run.py --ablation               # also the one-part-at-a-time variants (12 more harnesses)
    python run.py --tasks 01 07            # only tasks whose id starts with 01 or 07
    python run.py --list-models            # what models your API key can use

Runs are saved as they finish, so you can stop with Ctrl+C and run the same
command again to continue where you left off.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import os
import sys
import tempfile
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Scratch copies live in the system temp folder: sync tools (OneDrive, Dropbox)
# can lock or remove files inside a synced project folder mid-run.
WORK = Path(tempfile.gettempdir()) / "harness-engineering-work"
sys.path.insert(0, str(ROOT))

from harness.agent import RunResult, result_dict, run_agent  # noqa: E402
from harness.configs import ADD_ONE, CONFIGS, REMOVE_ONE  # noqa: E402
from harness.llm import LLM, load_env  # noqa: E402
from harness.tasks import grade, load_tasks, prepare_workspace  # noqa: E402

write_lock = threading.Lock()


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9.+-]+", "-", text).strip("-").lower()


def write_trace(path: Path, history: list[dict], result: RunResult, grade_output: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.with_suffix(".json").write_text(
        json.dumps({"result": result_dict(result), "messages": history, "grading": grade_output}, indent=1),
        encoding="utf-8",
    )
    out = [f"# {result.task_id} / {result.harness} / run {result.repeat}",
           f"solved={result.solved} end={result.end_reason} steps={result.steps} "
           f"tokens={result.prompt_tokens}+{result.completion_tokens}", ""]
    for m in history:
        role = m["role"].upper()
        if m.get("content"):
            text = m["content"] if len(m["content"]) < 3000 else m["content"][:3000] + "\n...[trace truncated]"
            out += [f"## {role}", "```", text, "```"]
        for tc in m.get("tool_calls") or []:
            args = tc["function"]["arguments"]
            args = args if len(args) < 1500 else args[:1500] + "...[trace truncated]"
            out += [f"## {role} -> {tc['function']['name']}", "```json", args, "```"]
    out += ["## GRADING", "```", grade_output[-3000:], "```"]
    path.with_suffix(".md").write_text("\n".join(out), encoding="utf-8")


def run_one(llm, cfg, task, repeat, results_dir: Path) -> dict:
    ws = prepare_workspace(task, WORK / results_dir.name / slug(cfg.name) / f"{task.id}-r{repeat}")
    result = RunResult(task_id=task.id, harness=cfg.name, repeat=repeat)
    history: list[dict] = []
    try:
        history = run_agent(cfg, llm, task.issue, ws, result)
    except Exception as exc:  # the naive loop is allowed to crash; that is a result too
        result.end_reason = "harness_crash"
        result.error = f"{type(exc).__name__}: {exc}"
        traceback.print_exc(limit=1)
    result.solved, result.visible_tests_pass, grade_out = grade(task, ws)
    write_trace(results_dir / "traces" / slug(cfg.name) / f"{task.id}-r{repeat}", history, result, grade_out)
    row = result_dict(result)
    with write_lock:
        with (results_dir / "runs.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    mark = "PASS" if result.solved else "fail"
    print(f"  {mark}  {cfg.name:<26} {task.id:<28} r{repeat}  {result.end_reason:<20} "
          f"steps={result.steps:<3} tokens={result.prompt_tokens + result.completion_tokens:,}")
    shutil.rmtree(ws, ignore_errors=True)
    return row


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    load_env(ROOT / ".env")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harness", nargs="+", default=["naive", "engineered"], choices=sorted(CONFIGS))
    ap.add_argument("--ablation", action="store_true", help="add the 12 one-part-at-a-time variants")
    ap.add_argument("--tasks", nargs="*", help="task id prefixes (default: all)")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1, help="parallel runs (keep 1 on free tiers)")
    ap.add_argument("--tag", help="results folder name (default: the model name)")
    ap.add_argument("--list-models", action="store_true")
    args = ap.parse_args()

    llm = LLM.from_env()
    if args.list_models:
        print("\n".join(llm.list_models()))
        return

    harnesses = list(dict.fromkeys(args.harness + ((ADD_ONE + REMOVE_ONE) if args.ablation else [])))
    tasks = load_tasks(args.tasks)
    results_dir = ROOT / "results" / slug(args.tag or llm.model)
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "model.txt").write_text(f"{llm.model}\n{llm.base_url}\ntemperature={llm.temperature}\n", encoding="utf-8")

    # One runner per results folder. Two at once (e.g. a laptop waking from sleep
    # while you restart the run) would overwrite each other's work.
    lock = results_dir / ".lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError:
        raise SystemExit(f"Another run seems to be using {results_dir}. If none is running, delete {lock} and retry.")
    try:
        run_jobs(args, llm, harnesses, tasks, results_dir)
    finally:
        lock.unlink(missing_ok=True)


def run_jobs(args, llm, harnesses, tasks, results_dir: Path) -> None:
    done = set()
    runs_file = results_dir / "runs.jsonl"
    if runs_file.exists():
        for line in runs_file.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["harness"], r["task_id"], r["repeat"]))

    jobs = [(CONFIGS[h], t, k) for k in range(1, args.repeats + 1) for t in tasks for h in harnesses
            if (h, t.id, k) not in done]
    print(f"Model: {llm.model}  |  {len(tasks)} tasks x {len(harnesses)} harnesses x {args.repeats} repeats"
          f"  |  {len(jobs)} runs to do ({len(done)} already saved in {results_dir.relative_to(ROOT)})")

    if args.workers > 1:
        with ThreadPoolExecutor(args.workers) as pool:
            list(pool.map(lambda j: run_one(llm, *j, results_dir), jobs))
    else:
        for job in jobs:
            run_one(llm, *job, results_dir)

    from report import build_report
    print()
    print(build_report(results_dir))


if __name__ == "__main__":
    main()
