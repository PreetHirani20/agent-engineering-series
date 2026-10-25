"""Check the harness plumbing with a scripted fake model. No API key needed.

    python selftest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from harness.agent import RunResult, build_view, run_agent  # noqa: E402
from harness.configs import CONFIGS  # noqa: E402
from harness.tasks import grade, load_tasks, prepare_workspace  # noqa: E402


class ScriptedLLM:
    """Replays a fixed list of replies, ignoring what it is shown."""

    model = "scripted"

    def __init__(self, replies):
        self.replies = list(replies)
        self.seen: list[list[dict]] = []

    def chat(self, messages, tools, usage):
        self.seen.append(messages)
        usage.calls += 1
        reply = self.replies.pop(0) if self.replies else {"role": "assistant", "content": "done"}
        return {**reply, "_finish_reason": "stop"}


def call(name, **args):
    return {"role": "assistant", "content": "", "tool_calls": [
        {"id": f"c_{name}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]}


def text(t):
    return {"role": "assistant", "content": t}


def run(cfg_name, replies, task_prefix="01"):
    task = load_tasks([task_prefix])[0]
    with tempfile.TemporaryDirectory() as tmp:
        ws = prepare_workspace(task, Path(tmp) / "ws")
        llm = ScriptedLLM(replies)
        result = RunResult(task.id, cfg_name, 1)
        try:
            run_agent(CONFIGS[cfg_name], llm, task.issue, ws, result)
        except Exception as exc:
            result.end_reason = f"crash:{type(exc).__name__}"
        result.solved, _, _ = grade(task, ws)
        return result, llm


def main():
    task = load_tasks(["01"])[0]
    fixed = (task.dir / "solution" / "textutils.py").read_text(encoding="utf-8")
    original = (task.dir / "repo" / "textutils.py").read_text(encoding="utf-8")
    checks = []

    # 1. Naive harness: whole-file write, then a text reply ends the run.
    r, _ = run("naive", [call("read_file", path="textutils.py"), call("write_file", path="textutils.py", content=fixed), text("Fixed.")])
    checks.append(("naive: write_file + text reply solves", r.solved and r.end_reason == "finished"))

    # 2. Naive harness stops on a text reply that only announces a plan.
    r, _ = run("naive", [text("I'll look at textutils.py and fix it.")])
    checks.append(("naive: stops on first text reply", r.end_reason == "finished" and not r.solved))

    # 3. Naive harness crashes on malformed tool arguments.
    bad = {"role": "assistant", "content": "", "tool_calls": [{"id": "x", "type": "function", "function": {"name": "read_file", "arguments": "{path: textutils.py"}}]}
    r, _ = run("naive", [bad])
    checks.append(("naive: malformed JSON crashes the loop", r.end_reason.startswith("crash")))

    # 4. Engineered: exact edit, tests, finish -> verified and solved.
    r, _ = run("engineered", [
        call("search", pattern="def slugify"),
        call("edit_file", path="textutils.py", old_text=original, new_text=fixed),
        call("run_tests"),
        call("finish", summary="Rewrote slugify."),
    ])
    checks.append(("engineered: edit + finish solves", r.solved and r.end_reason == "finished"))

    # 5. Engineered: finish before fixing is rejected by verification.
    r, llm = run("engineered", [call("finish", summary="done"), call("edit_file", path="textutils.py", old_text=original, new_text=fixed), call("finish", summary="done")])
    checks.append(("engineered: premature finish rejected, then accepted", r.verification_rejections == 1 and r.solved))

    # 6. Engineered: editing a test file is blocked.
    r, _ = run("engineered", [call("edit_file", path="tests/test_textutils.py", old_text="hello-world", new_text="x")])
    checks.append(("engineered: test files are read-only", r.blocked_test_edits == 1))

    # 7. Engineered: malformed JSON is reported back, not a crash.
    r, llm = run("engineered", [bad, call("finish", summary="x")])
    shown = json.dumps(llm.seen[1])
    checks.append(("engineered: malformed JSON becomes an error message", "not a valid JSON object" in shown))

    # 8. Engineered: a text reply gets a nudge instead of ending the run.
    r, llm = run("engineered-no-verification", [text("I will now fix it."), call("finish", summary="x")])
    checks.append(("engineered: text reply is nudged", r.nudges == 1 and "call `finish`" in json.dumps(llm.seen[1])))

    # 9. Managed context: old large outputs are elided, a status block is appended.
    history = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
    for i in range(10):
        history.append({"role": "assistant", "content": "", "tool_calls": [{"id": str(i), "type": "function", "function": {"name": "read_file", "arguments": "{}"}}]})
        history.append({"role": "tool", "tool_call_id": str(i), "content": "x" * 20000})
    view = build_view(CONFIGS["engineered"], history, "STATUS")
    tool_sizes = [len(m["content"]) for m in view if m["role"] == "tool"]
    checks.append(("context: old outputs elided, recent ones capped", max(tool_sizes[:4]) < 300 and max(tool_sizes) <= 8200))
    checks.append(("memory: status block is the last message", view[-1]["content"] == "STATUS"))
    raw = build_view(CONFIGS["naive"], history, None)
    checks.append(("naive context: everything kept", sum(len(m.get("content") or "") for m in raw) >= 200000))

    # 10. Large file: designed read_file pages; basic read_file returns everything.
    r, llm = run("engineered", [call("read_file", path="units.py"), call("finish", summary="x")], "07")
    checks.append(("tools: read_file pages long files", "Continue with start_line=251" in json.dumps(llm.seen[1])))

    width = max(len(n) for n, _ in checks)
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name.ljust(width)}")
    failed = sum(not ok for _, ok in checks)
    print(f"\n{len(checks) - failed}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
