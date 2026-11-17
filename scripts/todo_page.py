# Ported from the LNG project dashboard, feat/gui-iteration @ e19d975, 2026-11-17
"""ToDo page: renders docs/paper_tracking/todo.md (table: id, owner, status, item, since, source) grouped by owner.

Library plus CLI:  python scripts/todo_page.py --out todo.html [--md path] [--show open|all]
Status open | doing | done; owners user | CEO (user first).  Default view hides done rows (?show=all shows them).
"""
from __future__ import annotations

import argparse
import html
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_CHECKOUT = Path("/Users/timkayser/Documents/ProgrammSupport/PyCharm/EMISSIONS/FAA/FAA_Emissions_Analysis")
REL = Path("docs/paper_tracking/todo.md")
COLS = ("id", "owner", "status", "item", "since", "source")
OWNERS = ("user", "CEO")
BADGES = {"open": "st-open", "doing": "st-doing", "done": "st-decided"}


def parse(md: str) -> list[dict]:
    """Rows of the markdown table in file order; header and separator lines are skipped."""
    rows = []
    for line in md.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < len(COLS) or cells[0].lower() == "id" or set(cells[0]) <= set("-: "):
            continue
        d = dict(zip(COLS, cells))
        d["status"] = d["status"].lower()
        rows.append(d)
    return rows


CSS = """
.tp{font-family:-apple-system,Segoe UI,sans-serif;font-size:13.5px;max-width:2400px}
.tp .head{background:#fff;border:1px solid #d0d7de;border-radius:8px;padding:10px 16px;margin:0 0 12px;line-height:1.6}
.tp .card{background:#fff;border:1px solid #d0d7de;border-radius:8px;padding:8px 16px;margin:0 0 8px;line-height:1.55}
.tp h3{margin:14px 0 6px;font-size:15px}
.tp .badge{display:inline-block;border-radius:12px;padding:1px 10px;font-size:12px;margin-right:8px;border:1px solid}
.tp .st-open{background:#eaeef2;color:#424a53;border-color:#afb8c1}
.tp .st-doing{background:#fff8c5;color:#7d4e00;border-color:#d4a72c}
.tp .st-decided{background:#dafbe1;color:#116329;border-color:#4ac26b}
.tp .meta{color:#57606a;font-size:12px}
.tp .sort a{margin-left:8px;padding:1px 8px;border:1px solid #d0d7de;border-radius:10px;text-decoration:none;color:#0969da}
.tp .sort a.on{background:#0969da;color:#fff;border-color:#0969da}
"""


def render_body(md_text: str, mtime: float | None = None, show: str = "open") -> str:
    rows = parse(md_text)
    show = show if show in ("open", "all") else "open"
    e = html.escape
    stamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M") if mtime else "unknown"
    n_open = sum(r["status"] != "done" for r in rows)
    head = (f'<div class="head"><b>ToDo</b> &middot; {len(rows)} listed, {n_open} not done &middot; '
            f'<code>todo.md</code> modified {stamp}<span class="sort"> &middot; show:' + "".join(
                f'<a class="{"on" if m == show else ""}" href="/todo?show={m}">{lab}</a>'
                for m, lab in (("open", "open and doing"), ("all", "all"))) + "</span></div>")
    owners = list(OWNERS) + sorted({r["owner"] for r in rows} - set(OWNERS))
    out = []
    for o in owners:
        grp = [r for r in rows if r["owner"] == o and (show == "all" or r["status"] != "done")]
        if not grp:
            continue
        out.append(f"<h3>{e(o)} ({len(grp)})</h3>")
        for r in grp:
            out.append(f'<div class="card"><span class="badge {BADGES.get(r["status"], "st-open")}">{e(r["status"])}</span>'
                       f'<b>{e(r["id"])}</b> {e(r["item"])} <span class="meta">&middot; since {e(r["since"])} '
                       f'&middot; {e(r["source"])}</span></div>')
    if not out:
        out.append('<div class="card">nothing to show</div>')
    return f'<style>{CSS}</style><div class="tp">{head}{"".join(out)}</div>'


def render(md_text: str, mtime: float | None = None, show: str = "open") -> str:
    return ('<!doctype html><html><head><meta charset="utf-8"><title>ToDo</title></head>'
            f'<body style="background:#f6f8fa;margin:16px">{render_body(md_text, mtime, show)}</body></html>')


def find_md() -> Path:
    for base in (MAIN_CHECKOUT, ROOT):  # main checkout first: it holds the live file
        if (base / REL).exists():
            return base / REL
    return ROOT / REL


def page_body(show: str = "open") -> str:
    p = find_md()
    if not p.exists():
        return f'<div class="tp"><div class="head">{html.escape(str(REL))} not found</div></div>'
    return render_body(p.read_text(encoding="utf-8"), p.stat().st_mtime, show)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", default=None)
    ap.add_argument("--show", default="open")
    a = ap.parse_args(argv)
    p = Path(a.md) if a.md else find_md()
    Path(a.out).write_text(render(p.read_text(encoding="utf-8"), p.stat().st_mtime, a.show), encoding="utf-8")
    print(f"wrote {a.out} from {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
