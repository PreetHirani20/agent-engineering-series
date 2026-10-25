"""Check every task is fair before spending API calls on it.

For each task: the untouched repo must FAIL grading (there is a real bug), and
the repo with the reference solution applied must PASS grading (the task is
solvable and the hidden tests only ask for what the issue says).

    python validate_tasks.py
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from harness.tasks import grade, load_tasks, prepare_workspace  # noqa: E402
from harness.tools import run_pytest  # noqa: E402


def main() -> int:
    bad = 0
    tasks = load_tasks(sys.argv[1:] or None)
    for task in tasks:
        problems = []
        with tempfile.TemporaryDirectory() as tmp:
            ws = prepare_workspace(task, Path(tmp) / "before")
            solved, _, _ = grade(task, ws)
            if solved:
                problems.append("the starting repo already passes grading")
            vis_code, _ = run_pytest(ws, "tests")
            if vis_code == 0:
                problems.append("note: visible tests pass at the start (agent cannot reproduce from tests alone)")

            ws2 = prepare_workspace(task, Path(tmp) / "after")
            for f in (task.dir / "solution").rglob("*"):
                if f.is_file():
                    dest = ws2 / f.relative_to(task.dir / "solution")
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(f, dest)
            solved, _, out = grade(task, ws2)
            if not solved:
                problems.append("the reference solution FAILS grading:\n" + out[-2000:])
        hard = [p for p in problems if not p.startswith("note:")]
        bad += bool(hard)
        status = "BAD " if hard else "ok  "
        print(f"{status} {task.id:<30} {task.title}")
        for p in problems:
            print(f"       - {p}")
    print(f"\n{len(tasks) - bad}/{len(tasks)} tasks valid")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
