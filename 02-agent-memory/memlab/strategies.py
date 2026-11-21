"""Five ways to give a long-running agent a memory.

Every strategy sees the same events, one working day at a time (`observe`), and must produce
the text the model sees when it gets a task (`context`). All but "keep everything" work inside
the same budget: about 6,000 tokens of context per task.

    keep-everything   the full history, every message and tool output
    recent-window     only the most recent messages that fit the budget
    rolling-summary   the model rewrites a running summary each day, plus recent messages
    vector-retrieval  every message is embedded; the most similar ones are retrieved per task
    curated-memory    the model keeps a list of facts and sets, replaces or deletes them each day

`stored()` returns everything the strategy would carry forward, so we can check what it forgot.
"""

from __future__ import annotations

import json
import math
import re

from .llm import LLM, Usage
from .scenario import SHOP, Event, Task

BUDGET = 6000  # tokens of memory per task, for every strategy except keep-everything
RECENT = 3000  # the part of the budget the hybrid strategies spend on recent messages


def tokens(text: str) -> int:
    return len(text) // 4  # a rough count, good enough to enforce a budget


def render(events: list[Event]) -> str:
    return "\n".join(e.render() for e in events)


def recent(events: list[Event], budget: int) -> list[Event]:
    """The newest events that fit in `budget` tokens, oldest first."""
    out, used = [], 0
    for e in reversed(events):
        used += tokens(e.render())
        if used > budget:
            break
        out.append(e)
    return out[::-1]


# What to keep and what to forget. The summary and the curated memory get the same rules,
# so the only difference between them is the shape of the memory.
POLICY = """What to keep: anything the shop will need again. Policies and settings, prices, account
numbers, contacts, customer details, and any instruction that applies "from now on".
What to forget: routine chatter and tool output that won't matter later; the old value of anything
that has been replaced (keep only the new one); offers and rules that have expired; and anything a
person asks you to delete or stop storing. Keep exact values (numbers, codes, emails, postcodes)."""


class Strategy:
    name = ""

    def __init__(self, llm: LLM, cache: "Cache"):
        self.llm, self.cache = llm, cache
        self.events: list[Event] = []
        self.upkeep = Usage()  # tokens spent maintaining memory, separate from answering

    def observe(self, day: list[Event]) -> None:
        self.events.extend(day)

    def context(self, task: Task) -> str:
        raise NotImplementedError

    def stored(self) -> str:
        raise NotImplementedError

    def snapshot(self) -> str:
        """The memory itself (not the recent window), for the trace."""
        return ""


class KeepEverything(Strategy):
    name = "keep-everything"

    def context(self, task):
        return "Everything you have seen so far:\n" + render(self.events)

    def stored(self):
        return render(self.events)


class RecentWindow(Strategy):
    name = "recent-window"

    def context(self, task):
        return "Your most recent messages (older ones are gone):\n" + render(recent(self.events, BUDGET))

    def stored(self):
        return render(recent(self.events, BUDGET))


class RollingSummary(Strategy):
    name = "rolling-summary"
    WORDS = 600

    def __init__(self, llm, cache):
        super().__init__(llm, cache)
        self.summary = "(empty)"

    def observe(self, day):
        super().observe(day)
        prompt = (
            f"You maintain the long-term memory of the operations assistant for {SHOP}, a small online shop, "
            f"as a running summary. It is the only record of anything older than the last day or two.\n\n"
            f"{POLICY}\n\nCurrent summary:\n{self.summary}\n\nToday's messages:\n{render(day)}\n\n"
            f"Rewrite the summary so it includes anything new worth keeping. At most {self.WORDS} words. "
            "Reply with the new summary only."
        )
        self.summary = self.cache.get_or_call(self, day[0].session, prompt).strip() or self.summary

    def context(self, task):
        return (f"Your memory (a summary of everything before):\n{self.summary}\n\n"
                f"Your most recent messages:\n{render(recent(self.events, RECENT))}")

    def stored(self):
        return self.summary + "\n" + render(recent(self.events, RECENT))

    def snapshot(self):
        return self.summary


class CuratedMemory(Strategy):
    name = "curated-memory"
    MAX_FACTS = 80

    def __init__(self, llm, cache):
        super().__init__(llm, cache)
        self.facts: dict[str, dict] = {}  # key -> {"value": ..., "since": "Mon 07 Sep"}

    def listing(self) -> str:
        if not self.facts:
            return "(empty)"
        return "\n".join(f"- {k}: {v['value']} (since {v['since']})" for k, v in self.facts.items())

    def observe(self, day):
        super().observe(day)
        prompt = (
            f"You maintain the long-term memory of the operations assistant for {SHOP}, a small online shop, "
            f"as a list of facts. Each fact has a short key and a value. It is the only record of anything "
            f"older than the last day or two.\n\n{POLICY}\n\nCurrent facts:\n{self.listing()}\n\n"
            f"Today's messages:\n{render(day)}\n\n"
            "Reply with JSON only: a list of changes to make, for example\n"
            '[{"op": "set", "key": "uk_carrier", "value": "..."}, {"op": "delete", "key": "..."}]\n'
            '"set" adds a fact or replaces the value of an existing key. Reuse the existing key when a fact '
            f"changes. Use [] if nothing changes. Keep at most {self.MAX_FACTS} facts."
        )
        reply = self.cache.get_or_call(self, day[0].session, prompt)
        since = f"{day[0].day:%a %d %b}"
        for op in parse_json(reply, default=[], want="list") or []:
            if not isinstance(op, dict) or not op.get("key"):
                continue
            key = str(op["key"]).strip()
            if op.get("op") == "delete":
                self.facts.pop(key, None)
            elif op.get("op") == "set" and op.get("value") is not None:
                value = re.sub(r"(\s*\(since [^)]*\))+\s*$", "", str(op["value"]))  # models echo the date back
                self.facts[key] = {"value": value, "since": since}

    def context(self, task):
        return (f"Your memory (facts you chose to keep):\n{self.listing()}\n\n"
                f"Your most recent messages:\n{render(recent(self.events, RECENT))}")

    def stored(self):
        return self.listing() + "\n" + render(recent(self.events, RECENT))

    def snapshot(self):
        return self.listing()


class VectorRetrieval(Strategy):
    name = "vector-retrieval"
    CHUNK = 600  # tokens per chunk; long tool outputs are split, each piece keeps its header

    def __init__(self, llm, cache):
        super().__init__(llm, cache)
        self.chunks: list[tuple[Event, str, list[float]]] = []

    @classmethod
    def split(cls, e: Event) -> list[str]:
        text = e.render()
        if tokens(text) <= cls.CHUNK:
            return [text]
        head, *lines = text.split("\n")
        pieces, cur = [], []
        for line in lines:
            cur.append(line)
            if tokens("\n".join(cur)) > cls.CHUNK:
                pieces.append(head + "\n" + "\n".join(cur))
                cur = []
        if cur:
            pieces.append(head + "\n" + "\n".join(cur))
        return pieces

    def observe(self, day):
        super().observe(day)
        texts = [(e, t) for e in day for t in self.split(e)]
        vectors = self.cache.embed(self, day[0].session, [t for _, t in texts])
        self.chunks.extend((e, t, v) for (e, t), v in zip(texts, vectors))

    def context(self, task):
        window = recent(self.events, RECENT)
        in_window = {e.id for e in window}
        q = self.cache.embed(self, f"q-{task.id}", [task.prompt])[0]
        ranked = sorted((c for c in self.chunks if c[0].id not in in_window), key=lambda c: -cosine(q, c[2]))
        picked, used = [], 0
        for c in ranked:
            if used + tokens(c[1]) > BUDGET - RECENT:
                break
            picked.append(c)
            used += tokens(c[1])
        picked.sort(key=lambda c: (c[0].session, c[0].id))
        return (f"Your memory (older messages retrieved because they look relevant to this task):\n"
                f"{chr(10).join(c[1] for c in picked)}\n\nYour most recent messages:\n{render(window)}")

    def stored(self):
        return "\n".join(c[1] for c in self.chunks)


class Oracle(Strategy):
    """Not a real strategy: only the messages that answer the task. Checks every task is answerable."""
    name = "oracle"

    def context(self, task):
        by_id = {e.id: e for e in self.events}
        return "The relevant messages:\n" + render([by_id[i] for i in task.evidence])

    def stored(self):
        return ""


STRATEGIES = {c.name: c for c in [KeepEverything, RecentWindow, RollingSummary, VectorRetrieval, CuratedMemory, Oracle]}
MAIN = ["keep-everything", "recent-window", "rolling-summary", "vector-retrieval", "curated-memory"]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)) or 1)


def parse_json(text: str, default=None, want: str = "list"):
    """Pull a JSON list (or object) out of a model reply (models like ```json fences)."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    pairs = [("[", "]"), ("{", "}")]
    for opener, closer in (pairs if want == "list" else pairs[::-1]):
        start, end = text.find(opener), text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                continue
    return default
