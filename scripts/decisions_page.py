# Ported from the LNG project dashboard, feat/gui-iteration @ e19d975, 2026-11-17
"""Decisions page: renders docs/paper_tracking/decisions.md as one card per decision.

Library plus CLI:  python scripts/decisions_page.py --out decisions.html [--md path]
Format: `## Dn Title` blocks of `key: value` lines (status, owner, blocks, options, question, recommendation), then a
final `## Decided ...` section of `- ` bullets.  Parser rules: a line `key: value` with a known key starts a field, any
other non-empty line continues the previous field; text before the first `##` is ignored.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_CHECKOUT = Path("/Users/timkayser/Documents/ProgrammSupport/PyCharm/EMISSIONS/FAA/FAA_Emissions_Analysis")
REL = Path("docs/paper_tracking/decisions.md")
KEYS = ("status", "owner", "blocks", "options", "question", "recommendation")
CRITICAL = re.compile(r"round|figure|layout|originality", re.I)
BADGES = {"open": "st-open", "proposed": "st-proposed", "decided": "st-decided"}

_H2 = re.compile(r"^##\s+(.*?)\s*$", re.M)
_FIELD = re.compile(r"^(%s):\s*(.*)$" % "|".join(KEYS), re.I)


def parse(md: str) -> tuple[list[dict], list[str]]:
    """-> (decisions in file order, decided bullets).  Each decision: title, plus the KEYS as strings ('' if absent)."""
    parts = _H2.split(md)  # [preamble, title1, body1, title2, body2, ...]
    decisions: list[dict] = []
    decided: list[str] = []
    for title, body in zip(parts[1::2], parts[2::2]):
        if title.lower().startswith("decided"):
            decided += [m.group(1).strip() for m in re.finditer(r"^\s*[-*]\s+(.*\S)\s*$", body, re.M)]
            continue
        d = {k: "" for k in KEYS}
        d["title"] = title
        cur = None
        for line in body.splitlines():
            m = _FIELD.match(line.strip())
            if m:
                cur = m.group(1).lower()
                d[cur] = m.group(2).strip()
            elif line.strip() and cur:
                d[cur] += " " + line.strip()
        d["status"] = d["status"].lower().split()[0] if d["status"] else "open"
        decisions.append(d)
    return decisions, decided


def is_critical(d: dict) -> bool:
    return bool(CRITICAL.search(d["blocks"]))


def number(d: dict) -> float:
    """D-number from the title ('D35.2 ...' -> 35.2); titles without one sort last."""
    m = re.match(r"D(\d+)(?:\.(\d+))?", d["title"])
    return float(f"{m.group(1)}.{(m.group(2) or '0').zfill(3)}") if m else float("inf")


def ordered(decisions: list[dict], mode: str = "critical") -> list[dict]:
    """mode 'critical': path-critical first, file order within (the default since 2026-11-11);
    'status': open before proposed before decided, number within; 'number': ascending D-number.
    Sorts are stable, so file order holds for ties."""
    if mode == "number":
        return sorted(decisions, key=number)
    if mode == "status":
        rank = {"open": 0, "proposed": 1, "decided": 2}
        return sorted(decisions, key=lambda d: (rank.get(d["status"], 0), number(d)))
    return sorted(decisions, key=lambda d: not is_critical(d))


CSS = """
.dp{font-family:-apple-system,Segoe UI,sans-serif;font-size:13.5px;max-width:2400px}
.dp .head{background:#fff;border:1px solid #d0d7de;border-radius:8px;padding:10px 16px;margin:0 0 12px;line-height:1.6}
.dp .card{background:#fff;border:1px solid #d0d7de;border-radius:8px;padding:10px 16px;margin:0 0 10px;line-height:1.55}
.dp .card.crit{border-left:4px solid #bf8700}
.dp h3{margin:0 0 4px;font-size:15px}
.dp .badge{display:inline-block;border-radius:12px;padding:1px 10px;font-size:12px;margin-right:8px;border:1px solid}
.dp .st-open{background:#eaeef2;color:#424a53;border-color:#afb8c1}
.dp .st-proposed{background:#fff8c5;color:#7d4e00;border-color:#d4a72c}
.dp .st-decided{background:#dafbe1;color:#116329;border-color:#4ac26b}
.dp .meta{color:#57606a;margin:2px 0}
.dp .rec{background:#fff8c5;border:1px solid #d4a72c;border-radius:6px;padding:6px 10px;margin:6px 0 0}
.dp ul{margin:4px 0 0 18px;padding:0}
.dp .sort a{margin-left:8px;padding:1px 8px;border:1px solid #d0d7de;border-radius:10px;text-decoration:none;color:#0969da}
.dp .sort a.on{background:#0969da;color:#fff;border-color:#0969da}
"""


def _card(d: dict) -> str:
    e = html.escape
    st = d["status"]
    cls = BADGES.get(st, "st-open")
    crit = is_critical(d)
    rows = [f'<div class="meta">owner: <b>{e(d["owner"] or "-")}</b> &middot; blocks: {e(d["blocks"] or "-")}</div>']
    for k in ("options", "question"):
        if d[k]:
            rows.append(f'<div class="{k}"><b>{k}:</b> {e(d[k])}</div>')
    if d["recommendation"]:
        rows.append(f'<div class="rec"><b>recommendation:</b> {e(d["recommendation"])}</div>')
    return (f'<div class="card{" crit" if crit else ""}"><h3><span class="badge {cls}">{e(st)}</span>{e(d["title"])}'
            f'{" <span class=meta>(path-critical)</span>" if crit else ""}</h3>{"".join(rows)}</div>')


def render_body(md_text: str, mtime: float | None = None, sort: str = "critical") -> str:
    decisions, decided = parse(md_text)
    sort = sort if sort in ("critical", "status", "number") else "critical"
    stamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M") if mtime else "unknown"
    n_open = sum(d["status"] != "decided" for d in decisions)
    head = (f'<div class="head"><b>Decisions</b> &middot; {len(decisions)} listed, {n_open} not decided &middot; '
            f'<code>decisions.md</code> modified {stamp} &middot; <a href="/paper-diff">back to paper diff</a>'
            f'<span class="sort"> &middot; sort:' + "".join(
                f'<a class="{"on" if m == sort else ""}" href="/decisions?sort={m}">{label}</a>'
                for m, label in (("critical", "path-critical first"), ("status", "open / decided"), ("number", "number"))) + "</span></div>")
    cards = "".join(_card(d) for d in ordered(decisions, sort))
    dec = ""
    if decided:
        dec = ('<h3>Decided this week</h3><div class="card"><ul>'
               + "".join(f"<li>{html.escape(x)}</li>" for x in decided) + "</ul></div>")
    return f'<style>{CSS}</style><div class="dp">{head}{cards}{dec}</div>'


def render(md_text: str, mtime: float | None = None) -> str:
    """Standalone HTML document."""
    return ('<!doctype html><html><head><meta charset="utf-8"><title>Decisions</title></head>'
            f'<body style="background:#f6f8fa;margin:16px">{render_body(md_text, mtime)}</body></html>')


def find_md() -> Path:
    for base in (ROOT, MAIN_CHECKOUT):
        if (base / REL).exists():
            return base / REL
    return ROOT / REL


def page_body(sort: str = "critical") -> str:
    p = find_md()
    if not p.exists():
        return f'<div class="dp"><div class="head">{html.escape(str(REL))} not found</div></div>'
    return render_body(p.read_text(encoding="utf-8"), p.stat().st_mtime, sort)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", default=None)
    a = ap.parse_args(argv)
    p = Path(a.md) if a.md else find_md()
    Path(a.out).write_text(render(p.read_text(encoding="utf-8"), p.stat().st_mtime), encoding="utf-8")
    print(f"wrote {a.out} from {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
