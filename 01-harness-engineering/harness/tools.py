"""The tools the model can call, in two designs.

BASIC is what most first agents ship with: read a whole file, write a whole
file, run the tests. DESIGNED is the same capability shaped for a model:
line-numbered paged reads, search, small exact edits, short test output,
errors that say what to do next, and an explicit `finish`.
"""

from __future__ import annotations

import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {"__pycache__", ".pytest_cache", ".git"}
READ_PAGE_LINES = 250
TEST_TIMEOUT = 90


class ToolError(Exception):
    pass


def run_pytest(workdir: Path, target: str = "") -> tuple[int, str]:
    """Run pytest in `workdir`. Returns (exit_code, combined output)."""
    cmd = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-o", "pythonpath=.", "-rN"]
    cmd += ["-q", "--tb=short"] if target != "__verbose__" else ["-v"]
    if target and target != "__verbose__":
        cmd.append(target)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    try:
        proc = subprocess.run(
            cmd, cwd=workdir, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=TEST_TIMEOUT, env=env,
        )
    except subprocess.TimeoutExpired:
        return 124, f"Tests timed out after {TEST_TIMEOUT}s (infinite loop?)"
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def summarize_pytest(output: str) -> str:
    """Pull the final '3 passed, 1 failed' style line out of pytest output."""
    for line in reversed(output.splitlines()):
        if re.search(r"\b(passed|failed|error|no tests ran)\b", line):
            return line.strip(" =")
    return "no summary"


class ToolBox:
    def __init__(self, workspace: Path, design: str, protect_tests: bool, memory: bool):
        self.root = workspace.resolve()
        self.design = design  # "basic" | "designed"
        self.protect_tests = protect_tests
        self.memory = memory
        self.protected = {p for p in self._all_files() if p.startswith("tests/")}
        # State the harness can read (used by memory + verification + metrics).
        self.files_changed: list[str] = []
        self.last_test_summary = "tests not run yet"
        self.notes = ""
        self.finished = False
        self.finish_summary = ""
        self.blocked_test_edits = 0

    # ---------- helpers ----------

    def _all_files(self) -> list[str]:
        out = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                out.append(Path(dirpath, name).relative_to(self.root).as_posix())
        return out

    def _resolve(self, path: str) -> Path:
        full = (self.root / path).resolve()
        if self.root not in full.parents and full != self.root:
            raise ToolError(f"Path {path!r} is outside the repository.")
        return full

    def _rel(self, full: Path) -> str:
        return full.relative_to(self.root).as_posix()

    def _check_writable(self, rel: str) -> None:
        if self.protect_tests and rel in self.protected:
            self.blocked_test_edits += 1
            raise ToolError(
                f"{rel} is a test file and is read-only. Fix the code under test, not the test. "
                "You may add new test files of your own."
            )

    def _did_you_mean(self, path: str) -> str:
        close = difflib.get_close_matches(path, self._all_files(), n=3, cutoff=0.4)
        return f" Did you mean: {', '.join(close)}?" if close else " Use list_files to see what exists."

    def _mark_changed(self, rel: str) -> None:
        if rel not in self.files_changed:
            self.files_changed.append(rel)

    # ---------- schemas ----------

    def schemas(self) -> list[dict]:
        def fn(name, description, props=None, required=None):
            return {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": props or {},
                        "required": required or [],
                    },
                },
            }

        s = {"type": "string"}
        i = {"type": "integer"}
        tools = self._basic_schemas(fn, s) if self.design == "basic" else self._designed_schemas(fn, s, i)
        if self.memory:
            tools.append(
                fn(
                    "update_notes",
                    "Replace your working notes. Keep a short checklist of the requirements in the issue and "
                    "mark each one done as you go. Your notes are shown to you at every step.",
                    {"notes": s},
                    ["notes"],
                )
            )
        return tools

    @staticmethod
    def _basic_schemas(fn, s) -> list[dict]:
        return [
            fn("list_files", "List files in the repository."),
            fn("read_file", "Read a file.", {"path": s}, ["path"]),
            fn("write_file", "Write content to a file.", {"path": s, "content": s}, ["path", "content"]),
            fn("run_tests", "Run the tests."),
        ]

    @staticmethod
    def _designed_schemas(fn, s, i) -> list[dict]:
        return [
            fn(
                "list_files",
                "Show the repository tree with the line count of each file. Call this first to orient yourself.",
                {"directory": {**s, "description": "Sub-directory to list. Default: whole repo."}},
            ),
            fn(
                "read_file",
                f"Read a file with line numbers, at most {READ_PAGE_LINES} lines per call. For long files, "
                "use `search` to find the right place, then read that range.",
                {
                    "path": s,
                    "start_line": {**i, "description": "1-based first line. Default 1."},
                    "end_line": {**i, "description": "Last line to show (inclusive)."},
                },
                ["path"],
            ),
            fn(
                "search",
                "Search all files for a regular expression. Returns path:line: text for each match. "
                "Use it to find where a function is defined or used.",
                {"pattern": s, "path": {**s, "description": "Limit to this file or directory."}},
                ["pattern"],
            ),
            fn(
                "edit_file",
                "Replace one exact snippet in a file. `old_text` must appear exactly once (include a few "
                "surrounding lines to make it unique; copy indentation exactly, without line-number prefixes). "
                "Prefer this over rewriting files.",
                {"path": s, "old_text": s, "new_text": s},
                ["path", "old_text", "new_text"],
            ),
            fn(
                "create_file",
                "Create a NEW file (fails if it already exists; use edit_file for existing files).",
                {"path": s, "content": s},
                ["path", "content"],
            ),
            fn(
                "run_tests",
                "Run pytest. Returns a pass/fail summary and short tracebacks for failures.",
                {"path": {**s, "description": "Optional test file or directory. Default: all tests."}},
            ),
            fn(
                "finish",
                "Call when the issue is fully resolved and the tests pass. This ends the task.",
                {"summary": {**s, "description": "One or two sentences on what you changed and why."}},
                ["summary"],
            ),
        ]

    # ---------- dispatch ----------

    def call(self, name: str, args: dict) -> str:
        handler = getattr(self, f"{self.design}_{name}", None) or getattr(self, f"any_{name}", None)
        if handler is None:
            raise ToolError(f"Unknown tool {name!r}.")
        return handler(**args)

    # ---------- basic tools ----------

    def basic_list_files(self) -> str:
        return "\n".join(self._all_files())

    def basic_read_file(self, path: str) -> str:
        return self._resolve(path).read_text(encoding="utf-8")

    def basic_write_file(self, path: str, content: str) -> str:
        full = self._resolve(path)
        self._check_writable(self._rel(full))
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        self._mark_changed(self._rel(full))
        return "OK"

    def basic_run_tests(self) -> str:
        _, out = run_pytest(self.root, "__verbose__")
        self.last_test_summary = summarize_pytest(out)
        return out

    # ---------- designed tools ----------

    def designed_list_files(self, directory: str = "") -> str:
        base = self._resolve(directory or ".")
        lines = []
        for rel in self._all_files():
            full = self.root / rel
            if base != self.root and base not in full.parents:
                continue
            try:
                n = sum(1 for _ in full.open(encoding="utf-8", errors="replace"))
            except OSError:
                n = 0
            size = full.stat().st_size
            tag = "  [read-only]" if self.protect_tests and rel in self.protected else ""
            lines.append(f"{rel}  ({n} lines, {size:,} bytes){tag}")
        return "\n".join(lines) or "(empty)"

    def designed_read_file(self, path: str, start_line: int = 1, end_line: int | None = None) -> str:
        full = self._resolve(path)
        if not full.is_file():
            raise ToolError(f"No file named {path!r}.{self._did_you_mean(path)}")
        lines = full.read_text(encoding="utf-8", errors="replace").splitlines()
        total = len(lines)
        start = max(1, int(start_line or 1))
        end = min(total, int(end_line) if end_line else start + READ_PAGE_LINES - 1)
        end = min(end, start + READ_PAGE_LINES - 1)
        if start > total:
            return f"{path} has only {total} lines."
        body = "\n".join(f"{n:>5}  {lines[n - 1][:400]}" for n in range(start, end + 1))
        footer = f"\n[{path}: lines {start}-{end} of {total}"
        footer += f". Continue with start_line={end + 1}]" if end < total else "]"
        return body + footer

    def designed_search(self, pattern: str, path: str = "") -> str:
        try:
            rx = re.compile(pattern)
        except re.error as exc:
            raise ToolError(f"Invalid regex: {exc}. Escape special characters like ( ) [ ] .")
        base = self._resolve(path or ".")
        hits = []
        for rel in self._all_files():
            full = self.root / rel
            if base != self.root and full != base and base not in full.parents:
                continue
            try:
                for n, line in enumerate(full.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if rx.search(line):
                        hits.append(f"{rel}:{n}: {line.strip()[:200]}")
            except OSError:
                continue
        if not hits:
            return f"No matches for {pattern!r}."
        more = f"\n[{len(hits) - 50} more matches not shown; narrow the pattern or path]" if len(hits) > 50 else ""
        return "\n".join(hits[:50]) + more

    def designed_edit_file(self, path: str, old_text: str, new_text: str) -> str:
        full = self._resolve(path)
        rel = self._rel(full)
        if not full.is_file():
            raise ToolError(f"No file named {path!r}.{self._did_you_mean(path)}")
        self._check_writable(rel)
        text = full.read_text(encoding="utf-8")
        count = text.count(old_text)
        if count == 0:
            stripped = re.sub(r"^\s*\d+  ", "", old_text, flags=re.M)
            hint = (
                " It looks like you included line-number prefixes from read_file; remove them."
                if stripped != old_text and text.count(stripped) == 1
                else " Re-read the exact lines with read_file and copy them exactly, including indentation."
            )
            raise ToolError(f"old_text was not found in {rel}.{hint}")
        if count > 1:
            raise ToolError(f"old_text appears {count} times in {rel}. Include more surrounding lines so it is unique.")
        new = text.replace(old_text, new_text, 1)
        full.write_text(new, encoding="utf-8")
        self._mark_changed(rel)
        first = new[: new.index(new_text) if new_text else 0].count("\n") + 1
        lines = new.splitlines()
        lo, hi = max(1, first - 2), min(len(lines), first + new_text.count("\n") + 2)
        snippet = "\n".join(f"{n:>5}  {lines[n - 1]}" for n in range(lo, hi + 1))
        return f"Edited {rel}. The changed region now reads:\n{snippet}"

    def designed_create_file(self, path: str, content: str) -> str:
        full = self._resolve(path)
        rel = self._rel(full)
        if full.exists():
            raise ToolError(f"{rel} already exists. Use edit_file to change it.")
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        self._mark_changed(rel)
        return f"Created {rel} ({content.count(chr(10)) + 1} lines)."

    def designed_run_tests(self, path: str = "") -> str:
        code, out = run_pytest(self.root, path)
        self.last_test_summary = summarize_pytest(out)
        if code == 0:
            return f"All tests passed ({self.last_test_summary})."
        lines = out.splitlines()
        if len(lines) > 80:
            out = "\n".join(lines[:60] + [f"... [{len(lines) - 80} lines omitted] ..."] + lines[-20:])
        return f"TESTS FAILING ({self.last_test_summary})\n{out}"

    def designed_finish(self, summary: str = "") -> str:
        self.finished = True
        self.finish_summary = summary
        return "Finish requested."

    def any_update_notes(self, notes: str) -> str:
        if not self.memory:
            raise ToolError("Unknown tool 'update_notes'.")
        self.notes = notes.strip()[:2000]
        return "Notes saved."
