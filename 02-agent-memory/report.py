"""Turn results/<model>/runs.jsonl into results.md and report.html.

    python report.py                 # newest results folder
    python report.py results/<name>  # a specific one
"""

from __future__ import annotations

import html
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from memlab.strategies import MAIN  # noqa: E402

CATEGORIES = [
    ("recall", "Recall", "a fact said once, never changed"),
    ("update", "Update", "a fact that changed; only the newest value is right"),
    ("expired", "Expired", "an offer or code that has ended"),
    ("deleted", "Deleted", "a customer asked us to delete their number"),
]
ERRORS = ["outdated", "not-forgotten", "missing", "mixed-up", "wrong"]
AGES = [(0, 7, "under 8 days"), (8, 20, "8 to 20 days"), (21, 99, "21+ days")]


def load(results_dir: Path) -> tuple[list[dict], list[dict]]:
    rows = {}
    for line in (results_dir / "runs.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        rows[(r["strategy"], r["task_id"])] = r  # a re-run replaces the old row
    tasks = [r for r in rows.values() if not r.get("audit")]
    audits = [r for r in rows.values() if r.get("audit")]
    return tasks, audits


def pct(rows: list[dict]) -> str:
    return f"{sum(r['ok'] for r in rows) / len(rows):.0%} ({sum(r['ok'] for r in rows)}/{len(rows)})" if rows else "-"


def summarize(tasks: list[dict], audits: list[dict]) -> dict[str, dict]:
    by = defaultdict(list)
    for r in tasks:
        by[r["strategy"]].append(r)
    aud = defaultdict(list)
    for a in audits:
        aud[a["strategy"]].append(a)
    out = {}
    for name in [n for n in MAIN + ["oracle"] if n in by]:
        rs = by[name]
        seeds = sorted({r["seed"] for r in rs})
        answer_tokens = sum(r["prompt_tokens"] + r["completion_tokens"] for r in rs)
        upkeep = sum(a["upkeep_prompt_tokens"] + a["upkeep_completion_tokens"] for a in aud[name])
        errors = defaultdict(int)
        for r in rs:
            if not r["ok"]:
                errors[r["verdict"]] += 1
        out[name] = {
            "rows": rs, "n": len(rs), "ok": sum(r["ok"] for r in rs), "seeds": seeds,
            "acc": sum(r["ok"] for r in rs) / len(rs),
            "by_cat": {c: [r for r in rs if r["category"] == c] for c, _, _ in CATEGORIES},
            "by_age": {label: [r for r in rs if r["category"] == "recall" and lo <= r["age"] <= hi] for lo, hi, label in AGES},
            "tokens_per_task": answer_tokens / len(rs),
            "upkeep_per_seed": upkeep / max(1, len(aud[name])),
            "total_per_seed": (answer_tokens + upkeep) / len(seeds),
            "upkeep_calls": sum(a["upkeep_calls"] for a in aud[name]) / max(1, len(aud[name])),
            "forgot": sum(not a["deleted_data_still_stored"] for a in aud[name]),
            "audits": len(aud[name]),
            "stored": sum(a["stored_tokens_est"] for a in aud[name]) / max(1, len(aud[name])),
            "errors": dict(errors),
        }
    return out


def markdown(stats: dict, model: str) -> str:
    names = list(stats)
    lines = [f"# Results: {model}", ""]
    lines += ["| Strategy | Tasks right | " + " | ".join(t for _, t, _ in CATEGORIES)
              + " | Tokens per task | Upkeep tokens per seed | Total tokens per seed | Deleted number gone from memory |",
              "|---|---|" + "---|" * len(CATEGORIES) + "---|---|---|---|"]
    for n in names:
        s = stats[n]
        lines.append(f"| {n} | {pct(s['rows'])} | " + " | ".join(pct(s["by_cat"][c]) for c, _, _ in CATEGORIES)
                     + f" | {s['tokens_per_task']:,.0f} | {s['upkeep_per_seed']:,.0f} | {s['total_per_seed']:,.0f} | "
                     + (f"{s['forgot']}/{s['audits']} seeds" if s["audits"] else "-") + " |")
    lines += ["", "Categories: " + "; ".join(f"**{t}**: {d}" for _, t, d in CATEGORIES) + ".", ""]
    lines += ["## Recall by how long ago the fact was said", "",
              "| Strategy | " + " | ".join(label for _, _, label in AGES) + " |", "|---|" + "---|" * len(AGES)]
    for n in names:
        lines.append(f"| {n} | " + " | ".join(pct(stats[n]["by_age"][label]) for _, _, label in AGES) + " |")
    lines += ["", "## How each strategy got tasks wrong", "",
              "| Strategy | " + " | ".join(ERRORS) + " |", "|---|" + "---|" * len(ERRORS)]
    for n in names:
        lines.append(f"| {n} | " + " | ".join(str(stats[n]["errors"].get(e, 0)) for e in ERRORS) + " |")
    lines += ["", "- **outdated**: gave a value that used to be right.",
              "- **not-forgotten**: gave the phone number the customer asked us to delete.",
              "- **missing**: said it didn't know.", "- **mixed-up**: gave the other customer's postcode.",
              "- **wrong**: anything else.", ""]
    tasks = sorted({(r["seed"], r["session"], r["task_id"]) for s in stats.values() for r in s["rows"]})
    lines += ["## Every task", "", "| Task | Day | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    idx = {(n, r["task_id"]): r for n in names for r in stats[n]["rows"]}
    for seed, session, tid in tasks:
        cells = []
        for n in names:
            r = idx.get((n, tid))
            cells.append("-" if r is None else ("ok" if r["ok"] else r["verdict"]))
        lines.append(f"| {tid} | {session + 1} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


# Cool palette: deep ink blue, teal and sage on a pale grey-green page.
CSS = """
:root{--bg:#EEF3F1;--card:#F8FBFA;--ink:#14324A;--muted:#5B7083;--line:#CBD8D4;--teal:#0F7C7C;--sage:#8FB3A5;
--plum:#7A3E72;--mustard:#C9A227;--slate:#9AA8B5;--violet:#5E5AA8}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "Segoe UI",system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:32px 16px}h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:32px 0 10px}
.sub{color:var(--muted);margin:0 0 20px}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:14px 0}
table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600}.bar{height:16px;border-radius:3px;background:var(--teal)}.row{display:grid;grid-template-columns:150px 1fr 70px;gap:10px;align-items:center;margin:7px 0}
.stack{display:flex;height:16px;border-radius:3px;overflow:hidden;background:#E2EAE7}.legend span{display:inline-flex;align-items:center;gap:6px;margin-right:14px;font-size:13px;color:var(--muted)}
.legend i{width:11px;height:11px;border-radius:2px;display:inline-block}
"""
ERR_COLORS = {"outdated": "var(--mustard)", "not-forgotten": "var(--plum)", "missing": "var(--slate)",
              "mixed-up": "var(--violet)", "wrong": "#4A5A6A"}


def html_report(stats: dict, model: str) -> str:
    names = [n for n in stats if n != "oracle"]
    h = [f"<!doctype html><meta charset=utf-8><title>Agent memory results</title><style>{CSS}</style><main>",
         f"<h1>What should a long-running agent remember?</h1><p class=sub>{html.escape(model)} · "
         f"{len(stats[names[0]]['seeds'])} seeds × {stats[names[0]]['n'] // len(stats[names[0]]['seeds'])} tasks per strategy</p>"]
    h.append("<div class=card><h2 style=margin-top:0>Tasks answered correctly</h2>")
    for n in names:
        s = stats[n]
        h.append(f"<div class=row><b>{n}</b><div class=bar style='width:{s['acc'] * 100:.1f}%'></div><span>{s['acc']:.0%}</span></div>")
    h.append("</div><div class=card><h2 style=margin-top:0>By kind of memory task</h2><table><tr><th>Strategy</th>"
             + "".join(f"<th>{t}</th>" for _, t, _ in CATEGORIES) + "</tr>")
    for n in names:
        h.append(f"<tr><td><b>{n}</b></td>" + "".join(f"<td>{pct(stats[n]['by_cat'][c])}</td>" for c, _, _ in CATEGORIES) + "</tr>")
    h.append("</table></div><div class=card><h2 style=margin-top:0>Why answers were wrong</h2><div class=legend>"
             + "".join(f"<span><i style='background:{c}'></i>{e}</span>" for e, c in ERR_COLORS.items()) + "</div>")
    for n in names:
        s = stats[n]
        segs = "".join(f"<div style='width:{s['errors'].get(e, 0) / s['n'] * 100:.1f}%;background:{c}'></div>"
                       for e, c in ERR_COLORS.items())
        h.append(f"<div class=row><b>{n}</b><div class=stack>{segs}</div><span>{s['n'] - s['ok']} wrong</span></div>")
    top = max(stats[n]["total_per_seed"] for n in names)
    h.append("</div><div class=card><h2 style=margin-top:0>Tokens per seed (answering + keeping memory)</h2>")
    for n in names:
        s = stats[n]
        h.append(f"<div class=row><b>{n}</b><div class=bar style='width:{s['total_per_seed'] / top * 100:.1f}%;background:var(--violet)'></div>"
                 f"<span>{s['total_per_seed'] / 1000:,.0f}K</span></div>")
    h.append("</div><div class=card><h2 style=margin-top:0>Asked to delete a phone number: is it gone?</h2><table>"
             "<tr><th>Strategy</th><th>Gone from memory</th><th>Memory size at the end</th></tr>")
    for n in names:
        s = stats[n]
        h.append(f"<tr><td><b>{n}</b></td><td>{s['forgot']}/{s['audits']} seeds</td><td>{s['stored']:,.0f} tokens</td></tr>")
    h.append("</table></div></main>")
    return "\n".join(h)


def main() -> None:
    if len(sys.argv) > 1:
        results_dir = Path(sys.argv[1])
    else:
        results_dir = max((p for p in (ROOT / "results").iterdir() if (p / "runs.jsonl").exists()),
                          key=lambda p: (p / "runs.jsonl").stat().st_mtime)
    tasks, audits = load(results_dir)
    stats = summarize(tasks, audits)
    model = (results_dir / "model.txt").read_text(encoding="utf-8").strip()
    (results_dir / "results.md").write_text(markdown(stats, model), encoding="utf-8")
    (results_dir / "report.html").write_text(html_report(stats, model), encoding="utf-8")
    print(markdown(stats, model).split("## Every task")[0])


if __name__ == "__main__":
    main()
