# Ported from the LNG project dashboard, feat/gui-iteration @ e19d975, 2026-11-17
"""Results gallery: every PNG a findings row points at, grouped by finding, newest first.

    python scripts/results_gallery.py --out <index.html>      # static index (image links relative to the file)

The live dashboard (scripts/fit_dashboard.py) serves the same gallery at /results, rebuilt on every page load,
so a result folder that lands with a PNG appears without any registration step.

Resolution rule (the findings-register rule of docs/findings.md turned into code): every backticked token of a
row's Evidence column is resolved against the repo root; `{a,b}` braces are expanded; a bare file name is looked
up in the folders the same row named before it.  A path under `docs/results/` is climbed to its result folder
(`<date>_<hash...>`, the naming rule) and every PNG under that folder belongs to the row.  A path elsewhere
(`docs/figures/`, `docs/data/figures/`) contributes only the named file (or the PNGs of a named directory).

Page order: result folders with PNGs but no row yet ("not yet in the register", newest first), the presentation
set (the curated paper figures, captions from their README table), the findings newest first (date, then
F-number), the test-article and data figure sets, and last the folders named only in a Status cell (superseded).
The page has a sidebar index, topic filter chips and a sort toggle (newest first / by topic), all client-side.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = Path("docs/findings.md")
RESULTS = Path("docs/results")
FIXED_GROUPS = (  # (title, directory, README with a `| `figure` | message | ... |` table or None, topic, kind)
    ("Presentation set", Path("docs/figures/presentation"), Path("docs/figures/presentation/README.md"),
     "Presentation", "presentation"),
    ("Test-article figures", Path("docs/figures/test_article"), None, "Test article", "fixed"),
    ("Data figures", Path("docs/data/figures"), None, "Data", "fixed"),
)
TOPIC_NAMES = {
    "calibration": "Calibration", "topology_comparison": "Topology comparison", "topology": "Topology",
    "probe_plane": "Probe plane", "sampling_line": "Sampling line", "sensitivity": "Sensitivity",
    "quadrature": "Quadrature", "mechanism_validation": "Mechanism", "figures": "Data", "test_article": "Test article",
    "presentation": "Presentation",
}
RESULT_FOLDER = re.compile(r"^\d{4}-\d{2}-\d{2}_")
ROW = re.compile(r"^\|\s*(F\d+)\s*\|")
TOKEN = re.compile(r"`([^`]+)`")
BRACE = re.compile(r"\{([^{}]*)\}")


@dataclass
class Finding:
    fid: str
    date: str
    text: str
    evidence: str
    status: str
    pngs: list[Path] = field(default_factory=list)   # relative to root
    folders: list[Path] = field(default_factory=list)  # result folders claimed (relative to root)

    @property
    def number(self) -> int:
        return int(self.fid[1:])


@dataclass
class Group:
    title: str                       # heading
    caption: str                     # full text under the heading (finding text + status + evidence)
    images: list[tuple[Path, str]]   # (path relative to root, caption)
    anchor: str
    kind: str = "finding"            # latest | presentation | finding | fixed | superseded
    topic: str = ""                  # filter chip label
    date: str = ""                   # YYYY-MM-DD for the sort toggle
    status: str = ""                 # quotable | provisional | data question | "" (badge)
    superseded: bool = False
    label: str = ""                  # short sidebar label
    folder: str = ""                 # result folder path(s) shown in monospace
    lead: str = ""                   # first sentence of the finding, shown open; the rest collapsed


def parse_findings(text: str) -> list[Finding]:
    """The F-rows of the findings table, in file order.  A row's Finding cell may contain '|' (joined back)."""
    out = []
    for line in text.splitlines():
        if not ROW.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        out.append(Finding(fid=cells[0], date=cells[1], text=" | ".join(cells[2:-2]), evidence=cells[-2],
                           status=cells[-1]))
    return out


def expand_braces(token: str) -> list[str]:
    m = BRACE.search(token)
    if not m:
        return [token]
    return [x for alt in m.group(1).split(",") for x in expand_braces(token[:m.start()] + alt.strip() + token[m.end():])]


def result_folder(rel: Path) -> Path | None:
    """The `<date>_<hash>` folder containing rel (relative to root) if rel lies under docs/results, else None."""
    parts = rel.parts
    if parts[:2] != RESULTS.parts:
        return None
    for k in range(2, len(parts)):
        if RESULT_FOLDER.match(parts[k]):
            return Path(*parts[:k + 1])
    return None


def pngs_under(root: Path, rel: Path) -> list[Path]:
    return sorted(p.relative_to(root) for p in (root / rel).rglob("*.png"))


def resolve_evidence(evidence: str, root: Path) -> tuple[list[Path], list[Path]]:
    """(pngs, result folders) a row's Evidence cell points at, both relative to root, in order, deduplicated."""
    bases: list[Path] = []     # directories named so far in this row (for bare names), relative to root
    pngs: list[Path] = []
    folders: list[Path] = []

    def add(rel: Path):
        rf = result_folder(rel)
        if rf is not None:
            if rf not in folders:
                folders.append(rf)
            for p in pngs_under(root, rf):
                if p not in pngs:
                    pngs.append(p)
        elif (root / rel).is_dir():
            for p in pngs_under(root, rel):
                if p not in pngs:
                    pngs.append(p)
        elif rel.suffix.lower() == ".png" and rel not in pngs:
            pngs.append(rel)

    for raw in TOKEN.findall(evidence):
        for token in expand_braces(raw):
            token = token.strip().rstrip(";,")
            if not token or "<" in token or token == "W":
                continue
            rel = Path(token)
            candidates = [rel] if (root / rel).exists() else []
            if not candidates and not rel.is_absolute():
                for base in bases:
                    for anc in (base, *base.parents):
                        if anc == Path(".") or (anc.parts[:1] != ("docs",)):
                            break
                        if (root / anc / rel).exists():
                            candidates.append(anc / rel)
                            break
                    if candidates:
                        break
            if not candidates:
                continue
            hit = candidates[0]
            d = hit if (root / hit).is_dir() else hit.parent
            if d not in bases:
                bases.insert(0, d)  # the most recently named folder is tried first
            add(hit)
    return pngs, folders


def load_findings(root: Path = ROOT) -> list[Finding]:
    rows = parse_findings((root / FINDINGS).read_text(encoding="utf-8"))
    for r in rows:
        r.pngs, r.folders = resolve_evidence(r.evidence, root)
    rows.sort(key=lambda r: (r.date, r.number), reverse=True)
    return rows


def unclaimed_folders(rows: list[Finding], root: Path = ROOT) -> list[tuple[Path, float, str | None]]:
    """Result folders holding PNGs that no row's Evidence claims: (relative path, newest PNG mtime, superseded-by),
    newest first.  A folder named only in a Status cell (e.g. F25 "supersedes `2026-10-26_ab7d032/`") is
    superseded by that row and goes to the bottom of the gallery instead of the top."""
    claimed = {f for r in rows for f in r.folders}
    superseded = {Path(raw.strip()).name: r.fid for r in rows for raw in TOKEN.findall(r.status)
                  if RESULT_FOLDER.match(Path(raw.strip()).name)}
    seen: dict[Path, float] = {}
    for p in (root / RESULTS).rglob("*.png"):
        rel = p.relative_to(root)
        rf = result_folder(rel)
        if rf is None or rf in claimed:
            continue
        seen[rf] = max(seen.get(rf, 0.0), p.stat().st_mtime)
    return [(f, m, superseded.get(f.name)) for f, m in sorted(seen.items(), key=lambda kv: -kv[1])]


def readme_captions(readme: Path) -> dict[str, str]:
    """`stem -> caption` from a README table whose first cell is the backticked figure stem."""
    caps = {}
    if not readme.is_file():
        return caps
    for line in readme.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].startswith("`"):
            stem = cells[0].strip("`")
            caps[stem] = cells[1] + (f"  [{cells[3]}]" if len(cells) >= 4 and cells[3].startswith("F") else "")
    return caps


def topic_of(folder: Path | None, pngs: list[Path]) -> str:
    """Topic label from the result folder's parent directory, else from the first PNG's directory."""
    if folder is not None:
        return TOPIC_NAMES.get(folder.parts[2], folder.parts[2]) if len(folder.parts) > 3 else "Baseline"
    if pngs:
        return TOPIC_NAMES.get(pngs[0].parent.name, pngs[0].parent.name)
    return ""


def status_class(status: str) -> str:
    s = status.lower()
    for key in ("quotable", "provisional", "data question"):
        if key in s:
            return key
    return ""


def lead_sentence(text: str, limit: int = 220) -> str:
    """First sentence (up to the first '. ' after at least 40 characters), cut at `limit`."""
    m = re.search(r"(?<=.{40})\.\s", text)
    lead = text[:m.end() - 1] if m else text
    return lead if len(lead) <= limit else lead[:limit].rsplit(" ", 1)[0] + " ..."


def build_groups(root: Path = ROOT) -> list[Group]:
    rows = load_findings(root)
    groups: list[Group] = []
    tail: list[Group] = []
    for folder, mtime, by in unclaimed_folders(rows, root):
        g = Group(
            title=folder.name + ("  (superseded by " + by + ")" if by else "  (not yet in the register)"),
            caption=(f"Named only in the Status cell of {by} (superseded); kept for the record."
                     if by else "PNGs present, no docs/findings.md row points here yet") +
                    f"; newest PNG {time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))}.",
            images=[(p, p.relative_to(folder).as_posix()) for p in pngs_under(root, folder)],
            anchor=f"folder-{folder.as_posix().replace('/', '-')}",
            kind="superseded" if by else "latest", topic=topic_of(folder, []),
            date=folder.name[:10], superseded=bool(by), label=folder.name, folder=folder.as_posix())
        (tail if by else groups).append(g)
    fixed = []
    for title, d, readme, topic, kind in FIXED_GROUPS:
        if not (root / d).is_dir():
            continue
        caps = readme_captions(root / readme) if readme else {}
        imgs = [(p, f"{p.name}: {caps[p.stem]}" if p.stem in caps else p.name) for p in pngs_under(root, d)]
        fixed.append(Group(title=title, caption=f"README: {readme.as_posix()}" if readme else "", images=imgs,
                           anchor=f"fixed-{d.as_posix().replace('/', '-')}", kind=kind, topic=topic,
                           date="", label=title, folder=d.as_posix()))
    groups += [g for g in fixed if g.kind == "presentation"]
    for r in rows:
        if not r.pngs:
            continue
        folder = r.folders[0] if r.folders else None
        topic = topic_of(folder, r.pngs)
        groups.append(Group(
            title=f"{r.fid}  {topic}  {r.date}",
            caption=r.text, images=[(p, p.name) for p in r.pngs], anchor=r.fid, kind="finding", topic=topic,
            date=r.date, status=status_class(r.status), superseded="SUPERSEDED" in r.status,
            label=f"{r.fid} {topic}",
            folder=", ".join(f.as_posix() for f in r.folders) or ", ".join(sorted({p.parent.as_posix() for p in r.pngs})),
            lead=lead_sentence(r.text)))
        groups[-1].caption = f"{r.text}\n\nStatus: {r.status}\nEvidence: {r.evidence}"
    groups += [g for g in fixed if g.kind != "presentation"]
    return groups + tail


STYLE = """
:root{--bg:#f7f7f5;--ink:#222;--mute:#666;--line:#ddd;--side:240px}
*{box-sizing:border-box} body{font-family:-apple-system,Helvetica,Arial,sans-serif;margin:0;color:var(--ink);background:var(--bg)}
a{color:#1a5fb4;text-decoration:none} a:hover{text-decoration:underline}
.top{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line);padding:10px 20px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.top h1{font-size:18px;margin:0 14px 0 0} .top .tabs a{padding:5px 10px;border-radius:6px;margin-right:4px}
.top .tabs a.on{background:#e8eef7;font-weight:600} .top small{color:var(--mute)}
.chips{display:flex;gap:6px;flex-wrap:wrap} .chip{font-size:12px;padding:3px 9px;border:1px solid #bbb;border-radius:12px;background:#fff;cursor:pointer}
.chip.on{background:#1a5fb4;color:#fff;border-color:#1a5fb4} .sort{font-size:12px;color:var(--mute)} .sort select{font-size:12px}
.wrap{display:flex} .side{width:var(--side);flex:none;position:sticky;top:52px;height:calc(100vh - 52px);overflow:auto;padding:12px 10px;border-right:1px solid var(--line);background:#fff;font-size:12px}
.side h4{margin:10px 0 4px;color:var(--mute);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.04em}
.side a{display:block;padding:2px 6px;border-radius:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis} .side a:hover{background:#eef;text-decoration:none}
.side .hid{display:none}
main{flex:1;min-width:0;padding:10px 24px 60px}
section{margin:0 0 10px;padding:14px 16px;background:#fff;border:1px solid var(--line);border-radius:8px}
section.hid{display:none} section.superseded{opacity:.75}
section h2{font-size:15px;margin:0 0 4px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.badge{font-size:11px;padding:1px 7px;border-radius:9px;border:1px solid transparent;font-weight:600}
.badge.quotable{background:#e3f4e8;color:#1e6b34;border-color:#bfe3c9} .badge.provisional{background:#fff2d8;color:#8a5a00;border-color:#f3dca8}
.badge.data-question{background:#e6eefb;color:#1e4b8f;border-color:#c5d6f2} .badge.grey{background:#eee;color:#555}
.badge.latest{background:#fde2e2;color:#9b1c1c}
.path{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:var(--mute);margin:0 0 6px;word-break:break-all}
.lead{font-size:13px;margin:0 0 6px} details{font-size:12px;color:#444;margin:0 0 8px} summary{cursor:pointer;color:#1a5fb4}
details pre{white-space:pre-wrap;font-family:inherit;margin:6px 0 0;background:#f4f4f4;padding:8px;border-radius:6px}
.grid{display:flex;flex-wrap:wrap;gap:12px} figure{margin:0;width:360px}
figure img{width:360px;border:1px solid var(--line);background:#fff;border-radius:4px} figure img:hover{box-shadow:0 2px 10px rgba(0,0,0,.18)}
figcaption{font-size:11px;color:#555;margin-top:2px;word-break:break-word}
.count{font-size:11px;color:var(--mute);font-weight:normal}
.runrow{flex-basis:100%;display:flex;gap:10px;flex-wrap:wrap;font-size:12px}
.runstrip{padding:2px 9px;border-radius:9px;border:1px solid var(--line);background:#fafafa;color:#333}
.runstrip.live{background:#e3f4e8;border-color:#bfe3c9;color:#1e6b34} .runstrip.paused{background:#eee;color:#777}
.runbar{display:inline-flex;align-items:center;gap:6px;text-decoration:none;color:#1e6b34}.runbar .bar{display:inline-block;width:90px;height:6px;background:#dde;border-radius:3px;overflow:hidden}.runbar .bar i{display:block;height:100%;background:#2e9e50}
.runstrip.idle{color:var(--mute)} .runstrip code{font-size:12px}
"""

SCRIPT = """
(function(){
  const secs=[...document.querySelectorAll('main section')], main=document.querySelector('main');
  const links={}; document.querySelectorAll('.side a[data-for]').forEach(a=>links[a.dataset.for]=a);
  let topic='all';
  function apply(){
    secs.forEach(s=>{const on=topic==='all'||s.dataset.topic===topic; s.classList.toggle('hid',!on);
      if(links[s.id]) links[s.id].classList.toggle('hid',!on);});
    document.querySelectorAll('.chip').forEach(c=>c.classList.toggle('on',c.dataset.topic===topic));
  }
  document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{topic=c.dataset.topic;apply();});
  const order={latest:0,presentation:1,finding:2,fixed:3,superseded:4};
  document.getElementById('sort').onchange=e=>{
    const by=e.target.value, list=secs.slice();
    if(by==='topic') list.sort((a,b)=>(a.dataset.topic.localeCompare(b.dataset.topic))||(b.dataset.date.localeCompare(a.dataset.date)));
    else list.sort((a,b)=>(order[a.dataset.kind]-order[b.dataset.kind])||(b.dataset.date.localeCompare(a.dataset.date)));
    list.forEach(s=>main.appendChild(s));
  };
  apply();
})();
"""


TABS = (("changes", "/", "What changed"), ("paper", "/paper", "Paper"),
        ("paperdiff", "/paper-diff", "Paper diff"), ("decisions", "/decisions", "Decisions"),
        ("todo", "/todo", "ToDo"))   # /results stays routable but has no tab until a results folder exists (spec)


def nav_bar(active: str, extra: str = "", strip: str = "") -> str:
    """Top bar with the five dashboard tabs; `strip` is the 'running now' row shown under them on every page."""
    tabs = "".join(f'<a href="{href}" class="{"on" if active == key else ""}">{label}</a>' for key, href, label in TABS)
    row = f'<div class="runrow">{strip}</div>' if strip else ""
    return f'<div class="top"><h1>FAA</h1><span class="tabs">{tabs}</span>{extra}{row}</div>'


def render_html(groups: list[Group], img_src, home: str | None = None, refresh: int | None = None,
                strip: str = "") -> str:
    """img_src(rel path) -> URL for the <img>; home = link back to the dashboard (live page) or None (static)."""
    topics = sorted({g.topic for g in groups if g.topic})
    chips = '<span class="chips"><span class="chip on" data-topic="all">all</span>' + "".join(
        f'<span class="chip" data-topic="{html.escape(t)}">{html.escape(t)}</span>' for t in topics) + "</span>"
    sort = ('<span class="sort">sort <select id="sort"><option value="newest">newest first</option>'
            '<option value="topic">by topic</option></select></span>')
    n_img = sum(len(g.images) for g in groups)
    stamp = (f'<small>{n_img} figures in {len(groups)} groups, built {time.strftime("%Y-%m-%d %H:%M")} '
             f'from docs/findings.md</small>')
    head = f'<meta http-equiv="refresh" content="{refresh}">' if refresh else ""
    top = (nav_bar("results", chips + sort + stamp, strip) if home is not None else
           f'<div class="top"><h1>FAA results gallery</h1>{chips}{sort}{stamp}</div>')

    side = []
    for heading, kinds in (("Just landed", ("latest",)), ("Paper figures", ("presentation",)),
                           ("Findings, newest first", ("finding",)), ("Reference sets", ("fixed",)),
                           ("Superseded", ("superseded",))):
        items = [g for g in groups if g.kind in kinds]
        if items:
            side.append(f"<h4>{heading}</h4>" + "".join(
                f'<a href="#{html.escape(g.anchor)}" data-for="{html.escape(g.anchor)}" title="{html.escape(g.lead or g.title)}">'
                f'{html.escape(g.label or g.title)} <span class="count">{len(g.images)}</span></a>' for g in items))

    body = []
    for g in groups:
        badge = ""
        if g.status:
            badge += f'<span class="badge {g.status.replace(" ", "-")}">{html.escape(g.status)}</span>'
        if g.superseded:
            badge += '<span class="badge grey">superseded</span>'
        if g.kind == "latest":
            badge += '<span class="badge latest">new, no row yet</span>'
        figs = "".join(
            f'<figure><a href="{html.escape(img_src(p))}" target="_blank"><img loading="lazy" '
            f'src="{html.escape(img_src(p))}" alt="{html.escape(p.name)}"></a>'
            f"<figcaption>{html.escape(cap)}</figcaption></figure>" for p, cap in g.images)
        text = ""
        if g.lead:
            text = (f'<p class="lead">{html.escape(g.lead)}</p><details><summary>full finding, status, evidence</summary>'
                    f"<pre>{html.escape(g.caption)}</pre></details>")
        elif g.caption:
            text = f'<p class="lead" style="color:#666">{html.escape(g.caption)}</p>'
        body.append(
            f'<section id="{html.escape(g.anchor)}" class="{g.kind}{" superseded" if g.superseded else ""}" '
            f'data-topic="{html.escape(g.topic)}" data-date="{g.date}" data-kind="{g.kind}">'
            f'<h2>{html.escape(g.title)} {badge} <span class="count">{len(g.images)} fig.</span></h2>'
            f'<p class="path">{html.escape(g.folder)}</p>{text}<div class="grid">{figs}</div></section>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>FAA results gallery</title>{head}'
            f"<style>{STYLE}</style></head><body>{top}<div class=\"wrap\"><nav class=\"side\">{''.join(side)}</nav>"
            f"<main>{''.join(body)}</main></div><script>{SCRIPT}</script></body></html>")


def write_static(out: Path, root: Path = ROOT) -> int:
    groups = build_groups(root)
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(groups, lambda p: os.path.relpath(root / p, out.parent)), encoding="utf-8")
    return sum(len(g.images) for g in groups)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="HTML file to write (image links relative to it)")
    a = ap.parse_args(argv)
    n = write_static(Path(a.out))
    print(f"wrote {a.out}: {n} figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
