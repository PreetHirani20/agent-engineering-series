"""Turn results/<model>/runs.jsonl into results.md and report.html.

    python report.py                 # newest results folder
    python report.py results/<name>  # a specific one
"""

from __future__ import annotations

import html
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from harness.agent import PARTS  # noqa: E402
from harness.tasks import load_tasks  # noqa: E402

ORDER = ["naive", "engineered"] + [f"naive+{p}" for p in PARTS] + [f"engineered-no-{p}" for p in PARTS]


def load_runs(results_dir: Path) -> list[dict]:
    rows = {}
    for line in (results_dir / "runs.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        rows[(r["harness"], r["task_id"], r["repeat"])] = r  # a re-run replaces the old row
    return list(rows.values())


def summarize(runs: list[dict]) -> dict[str, dict]:
    by = defaultdict(list)
    for r in runs:
        by[r["harness"]].append(r)
    out = {}
    for h, rs in by.items():
        n = len(rs)
        ends = defaultdict(int)
        for r in rs:
            ends[r["end_reason"]] += 1
        out[h] = {
            "runs": n,
            "solved": sum(r["solved"] for r in rs),
            "rate": sum(r["solved"] for r in rs) / n,
            "steps": sum(r["steps"] for r in rs) / n,
            "tokens": sum(r["prompt_tokens"] + r["completion_tokens"] for r in rs) / n,
            "median_tokens": statistics.median(r["prompt_tokens"] + r["completion_tokens"] for r in rs),
            "peak_kb": max(r["peak_prompt_chars"] for r in rs) / 1024,
            "seconds": sum(r["seconds"] for r in rs) / n,
            "ends": dict(sorted(ends.items(), key=lambda kv: -kv[1])),
        }
    return out


def ordered(names) -> list[str]:
    return sorted(names, key=lambda h: ORDER.index(h) if h in ORDER else 99)


def paired_runs(runs: list[dict]) -> tuple[list[dict], list[str]]:
    """Keep only tasks that every harness completed (no API failure), so the comparison is like for like."""
    harnesses = {r["harness"] for r in runs}
    ok = defaultdict(set)
    for r in runs:
        if r["end_reason"] != "api_error":
            ok[r["task_id"]].add(r["harness"])
    tasks = {r["task_id"] for r in runs}
    excluded = sorted(t for t in tasks if ok[t] != harnesses)
    return [r for r in runs if r["task_id"] not in excluded], excluded


def build_report(results_dir: Path) -> str:
    runs, excluded = paired_runs(load_runs(results_dir))
    stats = summarize(runs)
    model = (results_dir / "model.txt").read_text(encoding="utf-8").splitlines()[0]
    tasks = {t.id: t for t in load_tasks()}
    task_ids = sorted({r["task_id"] for r in runs})
    harnesses = ordered(stats)
    repeats = max(r["repeat"] for r in runs)

    md = [f"# Results: {model}", "",
          f"{len(task_ids)} tasks, {repeats} run(s) per task per harness, temperature 0.", ""]
    if excluded:
        md += [f"Excluded because at least one harness could not complete them due to API errors or rate limits "
               f"(not counted for any harness): {', '.join(excluded)}.", ""]
    md += [
          "| Harness | Solved | Avg steps | Median tokens / task | Mean tokens / task | Peak context | How runs ended |",
          "|---|---|---|---|---|---|---|"]
    for h in harnesses:
        s = stats[h]
        ends = ", ".join(f"{k} {v}" for k, v in s["ends"].items())
        md.append(f"| {h} | **{s['solved']}/{s['runs']}** ({s['rate']:.0%}) | {s['steps']:.1f} | "
                  f"{s['median_tokens']:,.0f} | {s['tokens']:,.0f} | {s['peak_kb']:.0f} KB | {ends} |")

    head = [h for h in ("naive", "engineered") if h in stats]
    if head:
        md += ["", "## Per task", "", "| Task | Stresses | " + " | ".join(head) + " |",
               "|---|---|" + "---|" * len(head)]
        for tid in task_ids:
            cells = []
            for h in head:
                rs = [r for r in runs if r["harness"] == h and r["task_id"] == tid]
                ok = sum(r["solved"] for r in rs)
                cells.append(("✅" if ok == len(rs) else "❌" if ok == 0 else "◐") + f" {ok}/{len(rs)}")
            stresses = ", ".join(tasks[tid].stresses) if tid in tasks else ""
            md.append(f"| {tid} | {stresses} | " + " | ".join(cells) + " |")

    def ablation(prefix: str, base: str, title: str) -> None:
        names = [f"{prefix}{p}" for p in PARTS if f"{prefix}{p}" in stats]
        if not names or base not in stats:
            return
        b = stats[base]["rate"]
        md.extend(["", f"## {title}", "", "| Harness | Solved | Change vs " + base + " |", "|---|---|---|"])
        for h in names:
            s = stats[h]
            md.append(f"| {h} | {s['solved']}/{s['runs']} ({s['rate']:.0%}) | {(s['rate'] - b) * 100:+.0f} pts |")

    ablation("naive+", "naive", "Add one part to the naive harness")
    ablation("engineered-no-", "engineered", "Remove one part from the engineered harness")

    text = "\n".join(md) + "\n"
    (results_dir / "results.md").write_text(text, encoding="utf-8")
    (results_dir / "report.html").write_text(render_html(model, stats, harnesses, len(task_ids), repeats, text), encoding="utf-8")
    return text


def bar_chart(title: str, stats: dict, names: list[str], highlight: str) -> str:
    """Horizontal bars of solve rate, 0-100% axis. One hue for the highlighted harness, grey for the rest."""
    row, label_w, plot_w = 34, 210, 420
    h = row * len(names) + 40
    parts = [f'<figure><figcaption>{html.escape(title)}</figcaption>'
             f'<svg viewBox="0 0 {label_w + plot_w + 90} {h}" role="img" aria-label="{html.escape(title)}">']
    for x in (0, 25, 50, 75, 100):
        gx = label_w + plot_w * x / 100
        parts.append(f'<line x1="{gx}" x2="{gx}" y1="4" y2="{h - 26}" class="grid"/>'
                     f'<text x="{gx}" y="{h - 8}" class="tick" text-anchor="middle">{x}%</text>')
    for i, name in enumerate(names):
        s = stats[name]
        y = 8 + i * row
        w = max(2, plot_w * s["rate"])
        cls = "bar hi" if name == highlight or name == "engineered" else "bar"
        tip = f"{name}: {s['solved']}/{s['runs']} solved, {s['steps']:.1f} steps, {s['tokens']:,.0f} tokens avg"
        parts.append(
            f'<g><title>{html.escape(tip)}</title>'
            f'<text x="{label_w - 10}" y="{y + 15}" class="lbl" text-anchor="end">{html.escape(name)}</text>'
            f'<path class="{cls}" d="M{label_w},{y + 3} h{w - 4} a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-{w - 4} z"/>'
            f'<text x="{label_w + w + 8}" y="{y + 16}" class="val">{s["solved"]}/{s["runs"]}</text></g>')
    parts.append("</svg></figure>")
    return "".join(parts)


def render_html(model: str, stats: dict, harnesses: list[str], n_tasks: int, repeats: int, md: str) -> str:
    charts = []
    main = [h for h in ("naive", "engineered") if h in stats]
    if main:
        charts.append(bar_chart(f"Tasks solved: same model ({model}), two harnesses", stats, main, "engineered"))
    add = [h for h in ["naive"] + [f"naive+{p}" for p in PARTS] if h in stats]
    if len(add) > 1:
        charts.append(bar_chart("Starting from naive, add one part", stats, add, ""))
    rem = [h for h in ["engineered"] + [f"engineered-no-{p}" for p in PARTS] if h in stats]
    if len(rem) > 1:
        charts.append(bar_chart("Starting from engineered, remove one part", stats, rem, "engineered"))

    rows = "".join(
        f"<tr><td>{html.escape(h)}</td><td><b>{stats[h]['solved']}/{stats[h]['runs']}</b></td>"
        f"<td>{stats[h]['rate']:.0%}</td><td>{stats[h]['steps']:.1f}</td><td>{stats[h]['median_tokens']:,.0f}</td><td>{stats[h]['tokens']:,.0f}</td>"
        f"<td>{html.escape(', '.join(f'{k} {v}' for k, v in stats[h]['ends'].items()))}</td></tr>"
        for h in harnesses)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Harness Results</title>
<style>
:root {{ --surface:#fcfcfb; --ink:#0b0b0b; --ink-2:#52514e; --muted:#8a8984; --grid:#e6e5e1; --hi:#2a78d6; --base:#b9b8b2; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --surface:#1a1a19; --ink:#f0efec; --ink-2:#c3c2b7; --muted:#8f8e88; --grid:#33322f; --hi:#3987e5; --base:#5f5e59; }} }}
:root[data-theme="dark"] {{ --surface:#1a1a19; --ink:#f0efec; --ink-2:#c3c2b7; --muted:#8f8e88; --grid:#33322f; --hi:#3987e5; --base:#5f5e59; }}
body {{ background:var(--surface); color:var(--ink); font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; margin:0; padding:32px 16px; }}
main {{ max-width:760px; margin:0 auto; }}
h1 {{ font-size:22px; margin:0 0 4px; }} .sub {{ color:var(--ink-2); margin:0 0 28px; }}
figure {{ margin:0 0 36px; }} figcaption {{ font-weight:600; margin-bottom:8px; }}
svg {{ width:100%; height:auto; }}
.grid {{ stroke:var(--grid); stroke-width:1; }} .tick {{ fill:var(--muted); font-size:11px; }}
.lbl {{ fill:var(--ink-2); font-size:13px; }} .val {{ fill:var(--ink); font-size:13px; font-weight:600; }}
.bar {{ fill:var(--base); }} .bar.hi {{ fill:var(--hi); }}
table {{ border-collapse:collapse; width:100%; font-size:13px; }}
th,td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--grid); }} th {{ color:var(--ink-2); font-weight:600; }}
details {{ margin-top:28px; }} pre {{ white-space:pre-wrap; font-size:12px; color:var(--ink-2); }}
</style></head><body><main>
<h1>Same model, different harness</h1>
<p class="sub">{html.escape(model)} · {n_tasks} tasks · {repeats} run(s) each · temperature 0</p>
{''.join(charts)}
<table><thead><tr><th>Harness</th><th>Solved</th><th>Rate</th><th>Avg steps</th><th>Median tokens</th><th>Mean tokens</th><th>How runs ended</th></tr></thead>
<tbody>{rows}</tbody></table>
<details><summary>Full results (markdown)</summary><pre>{html.escape(md)}</pre></details>
</main></body></html>"""


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        dirs = [d for d in (ROOT / "results").iterdir() if (d / "runs.jsonl").exists()]
        target = max(dirs, key=lambda d: (d / "runs.jsonl").stat().st_mtime)
    print(build_report(target))
    print(f"Wrote {target / 'results.md'} and {target / 'report.html'}")
