"""Loading tasks and grading an agent's work.

Each task lives in tasks/<id>/:
    task.json   {"title", "stresses": [...]}  (the harness part the task was designed to stress)
    issue.md    the issue text the agent receives, written like a real bug report
    repo/       the starting code; repo/tests/ holds the tests the agent can see and run
    hidden/     extra tests the agent never sees, covering everything the issue asks for
    solution/   a reference fix (files overlaid on repo/), used only to validate the task

Grading copies the agent's workspace, puts back the original tests/ (so editing
tests cannot help), adds the hidden tests, and runs them all. Solved = all pass.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .tools import run_pytest

TASKS_DIR = Path(__file__).resolve().parent.parent / "tasks"


@dataclass
class Task:
    id: str
    title: str
    issue: str
    stresses: list[str]
    dir: Path


def load_tasks(selected: list[str] | None = None) -> list[Task]:
    tasks = []
    for d in sorted(p for p in TASKS_DIR.iterdir() if (p / "task.json").exists()):
        meta = json.loads((d / "task.json").read_text(encoding="utf-8"))
        issue = (d / "issue.md").read_text(encoding="utf-8").strip()
        task = Task(d.name, meta["title"], issue, meta.get("stresses", []), d)
        if not selected or any(task.id.startswith(s) for s in selected):
            tasks.append(task)
    return tasks


def prepare_workspace(task: Task, dest: Path) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(task.dir / "repo", dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    return dest


def grade(task: Task, workspace: Path) -> tuple[bool, bool, str]:
    """Returns (solved, visible_tests_pass, pytest output of the full grading run)."""
    with tempfile.TemporaryDirectory(prefix="grade-") as tmp:
        g = Path(tmp) / "repo"
        shutil.copytree(workspace, g, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        shutil.rmtree(g / "tests", ignore_errors=True)
        shutil.copytree(task.dir / "repo" / "tests", g / "tests")
        visible_code, _ = run_pytest(g, "tests")
        for f in (task.dir / "hidden").glob("*.py"):
            shutil.copy(f, g / "tests" / f.name)
        code, out = run_pytest(g, "tests")
        return code == 0, visible_code == 0, out
