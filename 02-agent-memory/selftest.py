"""Check the scenario, the grader and the strategies without calling any model (no key needed).

    python selftest.py
"""

from __future__ import annotations

import json
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import run  # noqa: E402
from memlab.grade import grade, norm  # noqa: E402
from memlab.llm import Usage  # noqa: E402
from memlab.scenario import SESSIONS, Task, generate  # noqa: E402
from memlab.strategies import BUDGET, MAIN, STRATEGIES, render, tokens  # noqa: E402

checks = []


def check(name: str, ok: bool, detail: str = "") -> None:
    checks.append(ok)
    print(f"  {'pass' if ok else 'FAIL'}  {name}{'  ' + detail if detail and not ok else ''}")


class FakeLLM:
    """Answers null to every task; keeps memory with fixed replies. Enough to test the plumbing."""
    model = "fake"

    def chat(self, messages, usage: Usage) -> str:
        usage.calls += 1
        text = messages[-1]["content"]
        usage.prompt_tokens += len(text) // 4
        if "as a list of facts" in text:
            return '```json\n[{"op": "set", "key": "uk_carrier", "value": "X"}, {"op": "delete", "key": "nope"}]\n```'
        if "as a running summary" in text:
            return "A short summary."
        return '{"answer": null}'

    def embed(self, texts, usage: Usage):
        usage.embed_calls += 1
        return [[random.Random(norm(t)[:40]).random() for _ in range(8)] for t in texts]


def appears(value, text: str) -> bool:
    if isinstance(value, float):
        return f"{value:.2f}" in text
    if isinstance(value, int):
        return f"{value} days" in text or f"£{value}" in text
    if ":" in str(value):  # a collection time is written as "2pm" / "3:30pm"
        h, m = map(int, str(value).split(":"))
        return f"{h % 12 or 12}{':' + str(m) if m else ''}{'pm' if h >= 12 else 'am'}" in text
    return str(value) in text or f"£{value}" in text


print("Scenario")
for seed in (1, 2, 3):
    sc = generate(seed)
    by_id = {e.id: e for s in sc.sessions for e in s}
    problems = []
    for t in sc.tasks:
        ev = [by_id[i] for i in t.evidence]
        text = render(ev)
        if any(e.session > t.session for e in ev):
            problems.append(f"{t.id}: evidence after the task")
        if t.expected is not None and not appears(t.expected, text):
            problems.append(f"{t.id}: expected {t.expected!r} not in evidence")
        if t.fact != "free_shipping" and any(not appears(o, text) for o in t.old_values):
            problems.append(f"{t.id}: an old value is not in evidence")
    check(f"seed {seed}: every task is answerable from its evidence, which comes before it", not problems, str(problems))
    check(f"seed {seed}: the deleted phone number is in the history", all(x in render(sc.events_until(SESSIONS - 1)) for x in sc.forget))
    check(f"seed {seed}: the promo runs Monday to Friday", sc.days[20].weekday() == 0 and sc.days[24].weekday() == 4)
    check(f"seed {seed}: 22 tasks over {SESSIONS} days", len(sc.tasks) == 22 and len(sc.days) == SESSIONS)
check("seeds use different values", generate(1).tasks[3].expected != generate(2).tasks[3].expected)
check("the same seed gives the same scenario", render(generate(2).events_until(39)) == render(generate(2).events_until(39)))

print("Grader")
t = Task("s1-01-x", 0, None, "x", "update", "", "f", "carrier", "Royal Mail", old_values=["Evri"])
check("carrier: 'Royal Mail Tracked 48' is right", grade(t, "Royal Mail Tracked 48") == "ok")
check("carrier: the old carrier is 'outdated'", grade(t, "Evri") == "outdated")
check("carrier: naming both is not right", grade(t, "Royal Mail or Evri") == "outdated")
check("carrier: null is 'missing'", grade(t, None) == "missing")
t2 = Task("s1-02-x", 0, None, "x", "update", "", "f", "carrier", "DHL Express")
check("carrier: 'DHL' names DHL Express", grade(t2, "DHL") == "ok")
t3 = Task("s1-03-x", 0, None, "x", "deleted", "", "f", "text", None, old_values=["07700 900123"])
check("deleted: null is right", grade(t3, None) == "ok" and grade(t3, "none") == "ok")
check("deleted: the old number is 'not-forgotten'", grade(t3, "07700900123") == "not-forgotten")
t4 = Task("s1-04-x", 0, None, "x", "recall", "", "f", "time", "14:00")
check("time: '2pm' and '14:00' match", grade(t4, "2pm") == "ok" and grade(t4, "14:00") == "ok")
t5 = Task("s1-05-x", 0, None, "x", "recall", "", "f", "number", 1.35, old_values=[1.2])
check("number: '£1.35' matches, 1.20 is outdated", grade(t5, "£1.35") == "ok" and grade(t5, 1.2) == "outdated")
t6 = Task("s1-06-x", 0, None, "x", "recall", "", "f", "postcode", "LS6 2QT", confusers=["BS3 4LX"])
check("postcode: spacing ignored; the lookalike's is 'mixed-up'", grade(t6, "ls62qt") == "ok" and grade(t6, "BS3 4LX") == "mixed-up")

print("Strategies")
fake = FakeLLM()
sc = generate(1)
last = sc.tasks[-1]
with tempfile.TemporaryDirectory() as tmp:
    cache = run.Cache(Path(tmp) / "cache", fake, 1)
    built = {name: STRATEGIES[name](fake, cache) for name in STRATEGIES}
    for s in range(SESSIONS):
        for st in built.values():
            st.observe(sc.sessions[s])
    ctx = {name: st.context(last) for name, st in built.items()}
    check("keep-everything sees every event", all(e.render() in ctx["keep-everything"] for e in sc.events_until(39)))
    for name in MAIN[1:]:
        check(f"{name} stays inside the {BUDGET:,}-token budget", tokens(ctx[name]) <= BUDGET + 200, str(tokens(ctx[name])))
    check("recent-window has forgotten day 1", sc.sessions[0][0].render() not in ctx["recent-window"])
    check("curated-memory applies 'set' and ignores deleting a missing key", built["curated-memory"].facts.get("uk_carrier", {}).get("value") == "X")
    check("the oracle sees only the evidence", ctx["oracle"].count("\n[") == len(last.evidence))
    check("vector-retrieval stores every message", all(x in built["vector-retrieval"].stored() for x in sc.forget))

    out = Path(tmp) / "results"
    out.mkdir()
    run.run_one(fake, out, 1, "curated-memory", set())
    rows = [json.loads(line) for line in (out / "runs.jsonl").read_text(encoding="utf-8").splitlines()]
    check("a full run writes 22 graded tasks and one audit row", len(rows) == 23 and sum(r.get("audit", False) for r in rows) == 1)
    check("a fake model that answers null gets only the 'should be gone' tasks right",
          sum(r.get("ok", False) for r in rows) == sum(t.expected is None for t in sc.tasks))
    run.run_one(fake, out, 1, "curated-memory", {("curated-memory", t.id) for t in sc.tasks})
    rows2 = (out / "runs.jsonl").read_text(encoding="utf-8").splitlines()
    check("a rerun skips finished tasks", len(rows2) == len(rows) + 1)  # only the audit row is added again

print(f"\n{sum(checks)}/{len(checks)} checks passed")
sys.exit(0 if all(checks) else 1)
