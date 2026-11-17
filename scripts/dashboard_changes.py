# Ported from the LNG project dashboard, feat/gui-iteration @ e19d975, 2026-11-17
"""'What changed' cards and the Paper page body for scripts/fit_dashboard.py (stdlib + PyYAML).

Two card sources, merged and sorted newest first (date, then time), spec docs/specs/dashboard.md:
  1. curated cards in docs/dashboard/changes.yaml
  2. one auto card per docs/findings.md row whose F-id no curated card names
A linked file that does not exist is shown as "not yet merged" instead of failing the page.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import yaml

import dashboard_md
import results_gallery

CHANGES = Path("docs/dashboard/changes.yaml")
STATUSES = ("done", "running", "draft", "waiting")
FIG2_DIR = Path("docs/figures/paper")
PAPER_SECTIONS = Path("docs/paper_sections")
PAPER_REVIEW = Path("docs/paper_review_2026-10-25.md")


def load_curated(root: Path) -> list[dict]:
    """Cards from changes.yaml; a missing file or a malformed entry is skipped, never raised."""
    p = root / CHANGES
    if not p.is_file():
        return []
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or []
    except yaml.YAMLError:
        return []
    cards = []
    for c in data if isinstance(data, list) else []:
        if isinstance(c, dict) and c.get("title"):
            c = dict(c)
            c["date"] = str(c.get("date", ""))
            c["time"] = str(c.get("time", "00:00"))
            c.setdefault("status", "done")
            cards.append(c)
    return cards


def auto_cards(root: Path, curated: list[dict]) -> list[dict]:
    """A card for every findings row that no curated card names: nothing in the register goes missing."""
    named = {str(c["finding"]).strip() for c in curated if c.get("finding")}
    cards = []
    try:
        rows = results_gallery.load_findings(root)
    except (OSError, ValueError):
        return []
    for r in rows:
        if r.fid in named:
            continue
        links = [{"label": f.name, "path": f.as_posix()} for f in r.folders[:1]]
        if r.pngs:
            links.insert(0, {"label": r.pngs[0].name, "path": r.pngs[0].as_posix()})
        cards.append({"date": r.date, "time": "00:00", "title": f"{r.fid} (from the findings register)",
                      "summary": results_gallery.lead_sentence(r.text), "links": links, "finding": r.fid,
                      "status": "done", "auto": True})
    return cards


def all_cards(root: Path) -> list[dict]:
    cur = load_curated(root)
    cards = cur + auto_cards(root, cur)
    cards.sort(key=lambda c: (c["date"], c["time"]), reverse=True)
    return cards


def folder_anchors(root: Path) -> dict[str, str]:
    """result folder (posix, relative) -> gallery anchor: the F-id of the row that claims it."""
    try:
        return {f.as_posix(): r.fid for r in results_gallery.load_findings(root) for f in r.folders}
    except (OSError, ValueError):
        return {}


def _link_html(link: dict, root: Path, anchors: dict[str, str]) -> str:
    label = html.escape(str(link.get("label") or link.get("path", "")))
    raw = str(link.get("path", ""))
    p = Path(raw)
    if p.is_absolute():       # absolute folders; show them repo-relative when possible
        try:
            p = p.relative_to(root)
        except ValueError:
            return f'<span class="miss">{label} (outside the repo)</span>'
    rel = p.as_posix()
    target = root / p
    if not target.exists():
        return f'<span class="miss">{label}: not yet merged</span>'
    q = html.escape(rel, quote=True)
    if target.is_dir():
        anchor = anchors.get(rel.rstrip("/")) or "folder-" + rel.rstrip("/").replace("/", "-")
        return f'<a class="lnk" href="/results#{html.escape(anchor)}">{label} (folder)</a>'
    if p.suffix.lower() == ".png":
        return (f'<a class="thumb" href="/img?path={q}" target="_blank"><img loading="lazy" src="/img?path={q}" '
                f'alt="{label}"><span>{label}</span></a>')
    return f'<a class="lnk" href="/file?path={q}">{label}</a>'


def render_card(c: dict, root: Path, anchors: dict[str, str]) -> str:
    status = c.get("status", "done") if c.get("status") in STATUSES else "done"
    badge = f'<span class="st {status}">{status}</span>'
    fid = f' <span class="fid">{html.escape(str(c["finding"]))}</span>' if c.get("finding") else ""
    nums = "".join(f"<li>{html.escape(str(n))}</li>" for n in c.get("numbers") or [])
    table = ""
    t = c.get("table")
    if isinstance(t, dict) and t.get("columns"):
        th = "".join(f"<th>{html.escape(str(x))}</th>" for x in t["columns"])
        tr = "".join("<tr>" + "".join(f"<td>{html.escape(str(x))}</td>" for x in row) + "</tr>"
                     for row in t.get("rows") or [])
        table = f'<table class="ct"><tr>{th}</tr>{tr}</table>'
    links = [_link_html(lk, root, anchors) for lk in c.get("links") or [] if isinstance(lk, dict)]
    thumbs = "".join(x for x in links if 'class="thumb"' in x)
    others = " &nbsp; ".join(x for x in links if 'class="thumb"' not in x)
    return (f'<div class="chg {status}{" auto" if c.get("auto") else ""}"><h3>{html.escape(str(c["title"]))}{fid} {badge}'
            f'<small>{html.escape(c["date"])} {html.escape(c["time"]) if c["time"] != "00:00" else ""}</small></h3>'
            f'<p class="sum">{html.escape(str(c.get("summary", "")))}</p>'
            + (f'<ul class="nums">{nums}</ul>' if nums else "") + table
            + (f'<div class="thumbs">{thumbs}</div>' if thumbs else "")
            + (f'<p class="links">{others}</p>' if others else "") + "</div>")


def render_changes(root: Path) -> str:
    anchors = folder_anchors(root)
    return "".join(render_card(c, root, anchors) for c in all_cards(root)) or "<p>no cards yet</p>"


# ---------------------------------------------------------------- Paper page

def fig2_files(root: Path) -> list[Path]:
    """Fig. 2 candidates, best first: a final fig2_network.png wins, then drafts by draft number, newest first."""
    d = root / FIG2_DIR
    final = d / "fig2_network.png"
    drafts = []
    for p in d.glob("fig2_network_draft*.png"):
        m = re.search(r"draft(\d+)", p.name)
        drafts.append((int(m.group(1)) if m else -1, p))
    ordered = [p for _, p in sorted(drafts, reverse=True)]
    return ([final] if final.is_file() else []) + ordered


def fig2_caption(root: Path) -> str:
    """The Message cell of the fig2 row of docs/figures/paper/README.md ('' when absent)."""
    readme = root / FIG2_DIR / "README.md"
    if not readme.is_file():
        return ""
    for ln in readme.read_text(encoding="utf-8").splitlines():
        cells = dashboard_md._cells(ln) if ln.lstrip().startswith("|") else []
        if len(cells) >= 2 and cells[0].strip("` ").startswith("fig2"):
            return cells[1]
    return ""


def render_paper(root: Path) -> str:
    files = fig2_files(root)
    out = ['<div class="card"><h2>Figure 2: reactor network</h2>']
    if files:
        cur = files[0].relative_to(root).as_posix()
        out.append(f'<a href="/img?path={html.escape(cur)}" target="_blank"><img class="fig2" '
                   f'src="/img?path={html.escape(cur)}" alt="{html.escape(files[0].name)}"></a>')
        out.append(f'<p class="note">Showing <code>{html.escape(files[0].name)}</code>.</p>')
        if len(files) > 1:
            older = " &nbsp; ".join(f'<a href="/img?path={html.escape(p.relative_to(root).as_posix())}" target="_blank">'
                                    f"{html.escape(p.stem.replace('fig2_network_', ''))}</a>" for p in files[1:])
            out.append(f'<p class="note">Older: {older}</p>')
    else:
        out.append('<p class="miss">no Figure 2 yet: not yet merged</p>')
    cap = fig2_caption(root)
    if cap:
        out.append(f'<div class="md">{dashboard_md.inline(cap)}</div>')
    out.append("</div>")
    docs = sorted((root / PAPER_SECTIONS).glob("*.md")) + [root / PAPER_REVIEW]
    for p in docs:
        rel = p.relative_to(root).as_posix() if p.exists() else p.name
        body = dashboard_md.render(p.read_text(encoding="utf-8")) if p.is_file() else '<p class="miss">not yet merged</p>'
        out.append(f'<div class="card"><h2>{html.escape(rel)}</h2><div class="md">{body}</div></div>')
    return "".join(out)
