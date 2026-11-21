"""Run every memory strategy through the eight-week scenario and grade each task.

    python run.py                          # all five strategies, seeds 1-3
    python run.py --seeds 1                # one seed (a quick first look)
    python run.py --strategies oracle      # the answerability check
    python run.py --list-models

Results go to results/<model>/. Each answer is saved the moment it is graded, and every model call
that maintains memory is cached, so if the run stops, the same command picks up where it left off.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from memlab.grade import grade  # noqa: E402
from memlab.llm import LLM, Usage, load_env  # noqa: E402
from memlab.scenario import SESSIONS, SHOP, Task, generate  # noqa: E402
from memlab.strategies import MAIN, STRATEGIES, Strategy, parse_json, tokens  # noqa: E402

SYSTEM = (
    f"You are the operations assistant for {SHOP}, a small online shop selling baking supplies. "
    "You only know what is in your memory below. Use the most recent information; ignore anything "
    "that has been replaced, has expired, or that someone asked to be deleted. If your memory does "
    "not contain the answer, use null. Never guess."
)


class Cache:
    """Model replies and embeddings, keyed by what was asked, so a rerun costs nothing."""

    def __init__(self, folder: Path, llm: LLM, seed: int):
        folder.mkdir(parents=True, exist_ok=True)
        self.llm, self.seed = llm, seed
        self.text_path = folder / "replies.jsonl"
        self.vec_path = folder / "embeddings.jsonl"
        self.text = self._load(self.text_path)
        self.vecs = self._load(self.vec_path)

    @staticmethod
    def _load(path: Path) -> dict:
        out = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                out[row["key"]] = row["value"]
        return out

    @staticmethod
    def _append(path: Path, key: str, value) -> None:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"key": key, "value": value}) + "\n")

    def get_or_call(self, strategy: Strategy, session: int, prompt: str) -> str:
        key = f"{strategy.name}|{self.seed}|{session}|{hashlib.sha1(prompt.encode()).hexdigest()[:16]}"
        if key not in self.text:
            self.text[key] = self.llm.chat([{"role": "user", "content": prompt}], strategy.upkeep)
            self._append(self.text_path, key, self.text[key])
        return self.text[key]

    def embed(self, strategy: Strategy, label, texts: list[str]) -> list[list[float]]:
        key = f"{self.seed}|{label}|{hashlib.sha1(chr(0).join(texts).encode()).hexdigest()[:16]}"
        if key not in self.vecs:
            vectors = self.llm.embed(texts, strategy.upkeep)
            self.vecs[key] = [[round(x, 5) for x in v] for v in vectors]
            self._append(self.vec_path, key, self.vecs[key])
        return self.vecs[key]


def answer(llm: LLM, strategy: Strategy, task: Task) -> dict:
    context = strategy.context(task)
    usage = Usage()
    started = time.monotonic()
    reply = llm.chat([
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"{context}\n\n---\nToday is {task.day:%A %d %B %Y}.\nTask: {task.prompt}\n"
                                    f'Reply with JSON only, in this shape: {{"{task.field}": ...}}'},
    ], usage)
    parsed = parse_json(reply, default={}, want="object")
    value = parsed.get(task.field) if isinstance(parsed, dict) else None
    verdict = grade(task, value)
    return {
        "strategy": strategy.name, "seed": int(task.id[1:].split("-")[0]), "task_id": task.id,
        "fact": task.fact, "category": task.category, "session": task.session,
        "age": task.session - task.stated_session, "expected": task.expected, "answer": value,
        "verdict": verdict, "ok": verdict == "ok", "context_tokens_est": tokens(SYSTEM + context),
        "prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens,
        "cached_tokens": usage.cached_tokens, "seconds": round(time.monotonic() - started, 1), "reply": reply,
    }


def run_one(llm: LLM, out: Path, seed: int, name: str, done: set) -> None:
    scenario = generate(seed)
    todo = [t for t in scenario.tasks if (name, t.id) not in done]
    audit_done = (name, f"audit-{seed}") in done
    if not todo and audit_done:
        return
    strategy = STRATEGIES[name](llm, Cache(out / "cache", llm, seed))
    trace = []
    print(f"\n{name}  seed {seed}: {len(todo)} tasks to answer")
    for s in range(SESSIONS):
        strategy.observe(scenario.sessions[s])
        snap = strategy.snapshot()
        if snap:
            trace.append(f"## Day {s + 1} ({scenario.days[s]:%a %d %b})\n\n{snap}\n")
        for task in [t for t in todo if t.session == s]:
            row = answer(llm, strategy, task)
            with (out / "runs.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
            print(f"  {'ok  ' if row['ok'] else 'FAIL'}  day {s + 1:>2}  {task.fact:<15} {row['verdict']:<13} "
                  f"expected={task.expected!r:<28} got={row['answer']!r}  ({row['prompt_tokens']:,} tokens)")
    if trace:
        (out / "memory").mkdir(exist_ok=True)
        (out / "memory" / f"{name}-seed{seed}.md").write_text(
            f"# {name}, seed {seed}: the memory at the end of each day\n\n" + "\n".join(trace), encoding="utf-8")
    if not audit_done:
        stored = strategy.stored()
        row = {
            "strategy": name, "seed": seed, "task_id": f"audit-{seed}", "audit": True,
            "deleted_data_still_stored": [x for x in scenario.forget if x in stored],
            "stored_tokens_est": tokens(stored),
            "upkeep_calls": strategy.upkeep.calls, "upkeep_embed_calls": strategy.upkeep.embed_calls,
            "upkeep_prompt_tokens": strategy.upkeep.prompt_tokens,
            "upkeep_completion_tokens": strategy.upkeep.completion_tokens,
        }
        with (out / "runs.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3])
    ap.add_argument("--strategies", nargs="+", default=MAIN, choices=list(STRATEGIES))
    ap.add_argument("--list-models", action="store_true")
    args = ap.parse_args()

    load_env(ROOT / ".env")
    llm = LLM.from_env()
    if args.list_models:
        print("\n".join(llm.list_models()))
        return

    out = ROOT / "results" / llm.model.replace("/", "_").replace("models_", "")
    out.mkdir(parents=True, exist_ok=True)
    (out / "model.txt").write_text(llm.model + "\n", encoding="utf-8")
    lock = out / ".lock"
    if lock.exists() and time.time() - lock.stat().st_mtime < 6 * 3600:
        raise SystemExit(f"Another run seems to be using {out} (delete {lock} if not).")
    lock.write_text(str(os.getpid()))
    try:
        done = set()
        if (out / "runs.jsonl").exists():
            for line in (out / "runs.jsonl").read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                done.add((r["strategy"], r["task_id"]))
        for seed in args.seeds:
            for name in args.strategies:
                run_one(llm, out, seed, name, done)
    finally:
        lock.unlink(missing_ok=True)
    print(f"\nDone. Next: python report.py  ({out})")


if __name__ == "__main__":
    main()
