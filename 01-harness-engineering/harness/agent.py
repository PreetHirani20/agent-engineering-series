"""The agent loop, with each of the six harness parts behind a switch.

    instructions   minimal one-liner          vs  a workflow, rules and a definition of done
    tools          read/write whole files     vs  paged reads, search, exact edits, finish
    context        append everything forever  vs  repo map up front, capped and elided outputs
    loop           stop on first text reply   vs  nudges, malformed-call recovery, budget warnings
    memory         nothing                    vs  notes + a status block re-shown every step
    verification   trust the model            vs  tests must pass before finish; tests read-only

Everything else (model, temperature, tasks, step budget) is identical.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .llm import LLM, Usage
from .tools import ToolBox, ToolError, run_pytest, summarize_pytest

PARTS = ("instructions", "tools", "context", "loop", "memory", "verification")

MAX_TOOL_OUTPUT = 8000  # chars kept per tool result when context is managed
KEEP_RECENT_OUTPUTS = 6  # older tool results are elided when context is managed
MAX_VERIFY_REJECTIONS = 3
MAX_NUDGES = 3


@dataclass(frozen=True)
class HarnessConfig:
    name: str
    instructions: bool = False
    tools: bool = False
    context: bool = False
    loop: bool = False
    memory: bool = False
    verification: bool = False
    max_steps: int = 30

    def parts_on(self) -> list[str]:
        return [p for p in PARTS if getattr(self, p)]


@dataclass
class RunResult:
    task_id: str
    harness: str
    repeat: int
    solved: bool = False
    visible_tests_pass: bool = False
    end_reason: str = ""
    steps: int = 0
    llm_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    peak_prompt_chars: int = 0
    seconds: float = 0.0
    files_changed: list[str] = field(default_factory=list)
    verification_rejections: int = 0
    blocked_test_edits: int = 0
    nudges: int = 0
    error: str = ""


# ---------------------------------------------------------------- instructions

MINIMAL_SYSTEM = (
    "You are a helpful coding assistant with tools for working with a code repository. "
    "Solve the user's issue."
)


def structured_system(cfg: HarnessConfig) -> str:
    finish = (
        "call `finish` with a one-line summary"
        if cfg.tools
        else "reply with a one-line summary and no tool call"
    )
    explore = (
        "look at the repository tree, then use `search` to find the code the issue is about"
        if cfg.tools
        else "list the files and read the ones the issue is about"
    )
    notes = " Write that checklist into your notes with `update_notes` and tick items off as you go." if cfg.memory else ""
    return f"""You are a careful software engineer working in a small Python repository. Resolve the issue by changing the code.

How to work:
1. Orient: {explore}. The root cause may be in a different file from the one the issue mentions.
2. Reproduce: run the tests and read what fails.
3. Make a checklist of every requirement in the issue, including each edge case and example it mentions.{notes}
4. Fix the root cause with small, targeted changes. Keep everything that already works working.
5. Verify: run the tests again. The existing tests do not cover every requirement, so for anything they miss, add a small test file of your own at the repository root (for example `test_issue_checks.py`) and run it.
6. When every checklist item is handled and all tests pass, {finish}.

Rules:
- Never edit the existing files in tests/. They define correct behaviour; change the code under test instead.
- Keep public function names and signatures unless the issue says otherwise.
- Standard library only.
- Act through tool calls. Do not describe a change you intend to make; make it."""


# ---------------------------------------------------------------- context

def first_user_message(cfg: HarnessConfig, issue: str, toolbox: ToolBox) -> str:
    if not cfg.context:
        return issue
    tree = toolbox.designed_list_files()
    extra = "\nFiles marked [read-only] cannot be changed." if cfg.verification else ""
    return f"<issue>\n{issue.strip()}\n</issue>\n\nRepository (path, size):\n{tree}{extra}"


def _cap(text: str) -> str:
    if len(text) <= MAX_TOOL_OUTPUT:
        return text
    head, tail = text[: MAX_TOOL_OUTPUT - 2000], text[-1500:]
    return f"{head}\n\n... [{len(text) - len(head) - len(tail):,} characters omitted by the harness; read a smaller range] ...\n\n{tail}"


def build_view(cfg: HarnessConfig, history: list[dict], status: str | None) -> list[dict]:
    """Decide what the model sees this turn. History itself is never modified."""
    view = [{k: v for k, v in m.items() if not k.startswith("_")} for m in history]
    if cfg.context:
        tool_idx = [i for i, m in enumerate(view) if m["role"] == "tool"]
        # Everything before the Kth-most-recent tool result counts as "old".
        cutoff = tool_idx[-KEEP_RECENT_OUTPUTS] if len(tool_idx) > KEEP_RECENT_OUTPUTS else 0
        for i, m in enumerate(view):
            if m["role"] == "tool":
                if i < cutoff and len(m["content"]) > 300:
                    first = m["content"].splitlines()[0][:120]
                    m["content"] = f"[older output elided by the harness: {first} ... re-run the tool if you need it]"
                else:
                    m["content"] = _cap(m["content"])
            elif m["role"] == "assistant" and m.get("tool_calls") and i < cutoff:
                m["tool_calls"] = [_shrink_call(tc) for tc in m["tool_calls"]]
    if status:
        view.append({"role": "user", "content": status})
    return view


def _shrink_call(tc: dict) -> dict:
    """Old write/edit calls can carry whole files in their arguments; keep only the shape."""
    try:
        args = json.loads(tc["function"]["arguments"])
    except (json.JSONDecodeError, TypeError):
        return tc
    for k in ("content", "old_text", "new_text"):
        if isinstance(args.get(k), str) and len(args[k]) > 300:
            args[k] = args[k][:150] + f"... [{len(args[k])} chars elided]"
    return {**tc, "function": {**tc["function"], "arguments": json.dumps(args)}}


# ---------------------------------------------------------------- memory

def status_block(cfg: HarnessConfig, tb: ToolBox, step: int) -> str | None:
    if not cfg.memory:
        return None
    return (
        f"[Harness status: step {step} of {cfg.max_steps}]\n"
        f"Files you have changed: {', '.join(tb.files_changed) or 'none yet'}\n"
        f"Last test run: {tb.last_test_summary}\n"
        f"Your notes:\n{tb.notes or '(empty; use update_notes to keep a requirements checklist)'}"
    )


# ---------------------------------------------------------------- verification

def verify(tb: ToolBox) -> tuple[bool, str]:
    code, out = run_pytest(tb.root)
    tb.last_test_summary = summarize_pytest(out)
    if code == 0:
        return True, ""
    lines = out.splitlines()
    if len(lines) > 60:
        out = "\n".join(lines[:40] + ["..."] + lines[-20:])
    return False, (
        f"The harness ran the test suite before accepting your result, and it is failing "
        f"({tb.last_test_summary}). The task is not done. Fix the failures, then finish again.\n\n{out}"
    )


# ---------------------------------------------------------------- the loop

def run_agent(cfg: HarnessConfig, llm: LLM, issue: str, workspace: Path, result: RunResult) -> list[dict]:
    """Run one task. Mutates `result`; returns the full transcript for the trace file."""
    tb = ToolBox(workspace, "designed" if cfg.tools else "basic", protect_tests=cfg.verification, memory=cfg.memory)
    system = structured_system(cfg) if cfg.instructions else MINIMAL_SYSTEM
    history: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": first_user_message(cfg, issue, tb)},
    ]
    usage = Usage()
    schemas = tb.schemas()
    recent_calls: list[str] = []
    awaiting_confirm = False
    started = time.monotonic()

    def done(reason: str) -> list[dict]:
        result.end_reason = reason
        result.llm_calls = usage.calls
        result.prompt_tokens = usage.prompt_tokens
        result.completion_tokens = usage.completion_tokens
        result.files_changed = tb.files_changed
        result.blocked_test_edits = tb.blocked_test_edits
        result.seconds = round(time.monotonic() - started, 1)
        return history

    for step in range(1, cfg.max_steps + 1):
        result.steps = step
        view = build_view(cfg, history, status_block(cfg, tb, step))
        result.peak_prompt_chars = max(result.peak_prompt_chars, sum(len(json.dumps(m)) for m in view))
        try:
            reply = llm.chat(view, schemas, usage)
        except Exception as exc:  # provider errors, context overflow, etc.
            result.error = f"{type(exc).__name__}: {str(exc)[:500]}"
            return done("api_error")
        history.append(reply)
        calls = reply.get("tool_calls") or []

        # ---- the model answered in text, with no tool call
        if not calls:
            if reply.get("_finish_reason") == "length" and cfg.loop:
                result.nudges += 1
                history.append({"role": "user", "content": "Your last reply was cut off for being too long. Make smaller changes (use edit_file for small edits)."})
                continue
            if cfg.verification:
                ok, msg = verify(tb)
                if ok:
                    return done("finished")
                if result.verification_rejections >= MAX_VERIFY_REJECTIONS:
                    return done("verification_failed")
                result.verification_rejections += 1
                history.append({"role": "user", "content": msg})
                continue
            if not cfg.loop:
                return done("finished")
            if cfg.tools:  # a finish tool exists, so plain text means "not done yet"
                if result.nudges >= MAX_NUDGES:
                    return done("stalled")
                result.nudges += 1
                history.append({"role": "user", "content": "You replied without calling a tool. If the issue is fully resolved, call `finish`. Otherwise continue with your next tool call."})
                continue
            if awaiting_confirm:
                return done("finished")
            awaiting_confirm = True
            result.nudges += 1
            history.append({"role": "user", "content": "Is the issue fully resolved and verified? If yes, reply with your final summary and no tool call. If not, continue with tool calls."})
            continue

        awaiting_confirm = False
        finish_requested = False
        for tc in calls:
            name = tc["function"]["name"]
            raw_args = tc["function"]["arguments"]
            output = _execute(cfg, tb, name, raw_args)
            if cfg.loop:
                sig = f"{name}:{raw_args}"
                recent_calls.append(sig)
                if recent_calls[-3:] == [sig] * 3:
                    output += "\n\n[Harness: you have made this exact call three times in a row. Try a different approach.]"
                left = cfg.max_steps - step
                if left <= 5:
                    output += f"\n\n[Harness: {left} steps left. Prioritise finishing a working fix.]"
            if name == "finish" and tb.finished:
                finish_requested = True
                if cfg.verification:
                    ok, msg = verify(tb)
                    if ok:
                        output = "Accepted: all tests pass."
                    else:
                        tb.finished = False
                        finish_requested = False
                        output = msg
                        if result.verification_rejections >= MAX_VERIFY_REJECTIONS:
                            history.append({"role": "tool", "tool_call_id": tc["id"], "content": output})
                            return done("verification_failed")
                        result.verification_rejections += 1
            history.append({"role": "tool", "tool_call_id": tc["id"], "content": output})

        if finish_requested:
            return done("finished")

    return done("max_steps")


def _execute(cfg: HarnessConfig, tb: ToolBox, name: str, raw_args: str) -> str:
    if not cfg.loop:
        # The way most first loops are written: parse and call, report exceptions as text.
        args = json.loads(raw_args or "{}")  # a malformed call crashes the run, as it would in a naive loop
        try:
            return str(tb.call(name, args))
        except Exception as exc:
            return f"Error: {exc}"
    try:
        args = json.loads(raw_args or "{}")
        if not isinstance(args, dict):
            raise ValueError("arguments must be a JSON object")
    except (json.JSONDecodeError, ValueError) as exc:
        return f"Error: your arguments for {name} were not a valid JSON object ({exc}). Send the call again with valid JSON."
    try:
        return str(tb.call(name, args))
    except ToolError as exc:
        return f"Error: {exc}"
    except TypeError as exc:
        params = next((s["function"]["parameters"]["properties"] for s in tb.schemas() if s["function"]["name"] == name), {})
        return f"Error: bad arguments for {name} ({exc}). Expected parameters: {', '.join(params) or 'none'}."
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}"


def result_dict(r: RunResult) -> dict:
    return asdict(r)
