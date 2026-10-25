# Same model, two harnesses

The code behind the blog post **"Harness Engineering: Why the Same Model Performs Differently in Different Agents"**.

One model. Twenty small coding tasks. Two agent harnesses that differ only in the code *around* the model. Each harness gets the same model, the same temperature, the same tasks and the same 30-step budget.

## The six parts of a harness

Each part is a switch in [`harness/agent.py`](harness/agent.py):

| Part | Naive harness | Engineered harness |
|---|---|---|
| **Instructions** | "You are a helpful coding assistant. Solve the user's issue." | A workflow (orient, reproduce, checklist, fix, verify), rules, and a definition of done |
| **Tool design** | `read_file` (whole file), `write_file` (whole file), `run_tests` (raw output) | Paged, line-numbered `read_file`; `search`; exact `edit_file`; short test output; errors that say what to try next; an explicit `finish` |
| **Context assembly** | Issue text only; every tool output kept forever | Issue plus a repo map up front; tool outputs capped; old outputs elided |
| **Control loop** | Stops at the first reply without a tool call; a malformed tool call crashes the run | Nudges when the model talks instead of acting; malformed calls become error messages; repeat-call and step-budget warnings |
| **Memory and state** | None | A notes tool for a requirements checklist, plus a status block (step, files changed, last test result, notes) shown every turn |
| **Verification** | Trust the model when it says it's done | The harness runs the tests before accepting "done"; existing test files are read-only |

Ablation runs (`--ablation`) switch one part at a time, so you can see which part carries the gap.

## The tasks

Twenty small Python repos in [`tasks/`](tasks/), each written like a real bug report or feature request: slug cleanup, money rounding, an LRU cache, a one-line bug in an 858-line file, a log parser next to a 375 KB log, a regression trap, a rename across six files, and more.

Each task has:

- `issue.md`: what the agent is told.
- `repo/`: the starting code, with tests the agent can see and run.
- `hidden/`: extra tests the agent never sees. They check only what the issue asks for.
- `solution/`: a reference fix, used only to check the task is fair.

A run counts as **solved** only if the original tests and the hidden tests all pass. Test files are restored before grading, so editing a test never helps.

`python validate_tasks.py` checks that every starting repo fails and every reference solution passes.

## Run it yourself

New to Python or API keys? Follow [GUIDE.md](../GUIDE.md) step by step. The short version:

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # macOS/Linux: cp .env.example .env, then add your key
python selftest.py                # checks the plumbing with a fake model, no key needed
python validate_tasks.py          # checks the tasks are fair
python run.py                     # naive vs engineered, 20 tasks
python run.py --ablation          # plus the 12 one-part-at-a-time variants
python report.py                  # results.md and report.html
```

Any OpenAI-compatible API works: Gemini, Groq, OpenRouter, OpenAI, or a local Ollama model. Runs are saved as they finish, so you can stop and resume.

## Results

| Model | Harness | Solved | Median tokens / task | Worst task (tokens) |
|---|---|---|---|---|
| Gemini 3.5 Flash-Lite | naive | 20/20 | 17,992 | 1,683,859 (task 08) |
| Gemini 3.5 Flash-Lite | engineered | 20/20 | 37,344 | 127,801 (task 10) |
| Gemma 4 26B-A4B | naive | 14/16 | 36,451 | |
| Gemma 4 26B-A4B | engineered | 16/16 | 70,710 | |

Gemma is scored on the 16 tasks both harnesses completed. Tasks 07, 08, 17 and 19 hit free-tier rate limits for at least one harness, so they are excluded for both.

What the harness changed:

- **Context:** on task 08 the naive agent read a 375 KB log and kept it in every later request: 1.68M tokens against 32K for the engineered agent, with the same model and the same outcome.
- **Control loop:** in all of Gemma's naive failures, the reply began "Now I will implement...", ran past the 8,192-token output limit mid-thought, and was cut off before any tool call. The naive loop treated that as "done". The engineered loop checks the stop reason and asks for a smaller step; that fired in 7 of 17 Gemma runs, and all 7 were solved.
- **Instructions:** the naive agent wrote to the test file in 20/20 Flash-Lite runs. The engineered agent edited an existing test 0 times in 37 runs.
- **Cost:** the engineered harness used about 2× the median tokens, but it avoided the 52× worst case.

Each model's folder in [`results/`](results/) has `results.md`, `report.html`, `runs.jsonl` and a readable trace of every run under `traces/`.

## Limits

- Twenty tasks is small. Treat the numbers as a demonstration, not a benchmark.
- I wrote the tasks, knowing what each harness part is for. The hidden tests only check what each issue asks for, and every task is validated against a reference fix, but task selection still shapes the results.
- The naive harness is the harness I would have written on day one. It is not a straw man, but it is not tuned either.
- Agent-written code runs on your machine via pytest, inside a scratch copy of each task. The tasks are tiny and use only the standard library, but it is still code a model wrote.
