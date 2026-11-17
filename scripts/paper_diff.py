# Ported from the LNG project dashboard, feat/gui-iteration @ e19d975, 2026-11-17
"""Paper diff guide: GitHub-style diff of the live Overleaf paper against the local ideal paper.

Spec: docs/specs/dashboard.md.  Library plus CLI.

    compute(live_tex, ideal_tex) -> [Hunk]       line diff (difflib), blank/whitespace-only differences ignored
    render_html(hunks, checks, meta) -> str       split view >= 1200 px, unified below
    python scripts/paper_diff.py --out guide.html [--ideal docs/paper_ideal/main.tex] [--live-file x.tex]

Why this design: a hunk is identified by the hash of its *ideal-side* text, so a tick survives line drift and
rebases as long as the proposed text is unchanged.  Pure deletions have no ideal text and hash the live text
with a "del:" prefix.  The ideal's `% why:` / `% src:` / `% bib-add:` / `% known-undefined:` comment lines are
metadata: they are removed before diffing and shown as the hunk note instead.
Stdlib only.  The paper repo papers/FAA_emissions_paper is only ever read (fetch + show + archive), never written.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_REPO = ROOT / "papers/FAA_emissions_paper"
IDEAL_DIR = ROOT / "docs/paper_ideal"
META_RE = re.compile(r"^\s*%\s*(why|src|bib-add|known-undefined)\s*:", re.I)
SECTION_RE = re.compile(r"\\(?:sub)*section\*?\s*\{(.*)\}")
CONTEXT = 2
NOTE_REACH = 3        # non-blank unchanged units a note block may sit above its hunk


@dataclass
class Hunk:
    id: str
    kind: str                      # add | del | change
    live_lines: list[str]
    ideal_lines: list[str]         # without meta comment lines
    note: list[str] = field(default_factory=list)   # the why/src comment lines, verbatim
    section: str = ""
    live_line: int = 1             # 1-based approximate line in the live paper
    ctx_before: list[str] = field(default_factory=list)
    ctx_after: list[str] = field(default_factory=list)


def norm(s: str) -> str:
    return " ".join(s.split())


def split_ideal(ideal_tex: str) -> tuple[list[str], list[list[str]]]:
    """-> (ideal lines without meta comments, notes[i] = meta lines that preceded kept line i; notes[-1] = trailing)."""
    lines, notes, pending = [], [], []
    for ln in ideal_tex.splitlines():
        if META_RE.match(ln):
            pending.append(ln)          # verbatim: indentation is restored exactly by the rebase
        else:
            lines.append(ln)
            notes.append(pending)
            pending = []
    notes.append(pending)       # trailing meta lines (bib-add, known-undefined) sit after the last line
    return lines, notes


def hunk_id(ideal_lines: list[str], live_lines: list[str]) -> str:
    t = norm(" ".join(ideal_lines))
    if not t:
        t = "del:" + norm(" ".join(live_lines))
    return hashlib.sha1(t.encode("utf-8")).hexdigest()


BREAK_RE = re.compile(r"^\s*\\(begin|end|item|section|subsection|subsubsection|paragraph|caption|label|usepackage|"
                      r"documentclass|newcommand|renewcommand|title|author|date|maketitle|input|include|"
                      r"bibliographystyle|bibliography|addbibresource|centering|hline|toprule|midrule|bottomrule|"
                      r"includegraphics|newpage|clearpage)\b")
END_RE = re.compile(r"^\s*\\(?!item\b|caption\b)(begin|end|section|subsection|subsubsection|paragraph|label|usepackage|"
                    r"documentclass|newcommand|renewcommand|title|author|date|maketitle|input|include|"
                    r"bibliographystyle|bibliography|addbibresource|centering|hline|toprule|midrule|bottomrule|"
                    r"includegraphics|newpage|clearpage)\b")


def is_comment(line: str) -> bool:
    return line.lstrip().startswith("%")


def reflow(lines: list[str], notes: list[list[str]] | None = None):
    """Join the physical lines of one paragraph into one unit, so re-wrapping text is not a difference.
    A unit ends at a blank line, after a structural command line (\\begin, \\end, \\section, ...) or a line ending
    in `\\\\`; a structural command or \\item starts a new unit.  -> (units, index of each unit's first line, notes)."""
    units, first, un, prev_end = [], [], [], True
    for i, ln in enumerate(lines):
        n = list(notes[i]) if notes else []
        s = norm(ln)
        if is_comment(ln):                      # a comment line is a unit of its own, never joined with text
            units.append(s), first.append(i), un.append(n)
            prev_end = True
            continue
        if not s:
            units.append(""), first.append(i), un.append(n)
            prev_end = True
            continue
        if prev_end or BREAK_RE.match(ln):
            units.append(s), first.append(i), un.append(n)
        else:
            units[-1] += " " + s
            un[-1] += n
        prev_end = bool(END_RE.match(ln)) or s.endswith("\\\\")
    return units, first, un


def compute(live_tex: str, ideal_tex: str) -> list[Hunk]:
    """Hunks of live -> ideal.  Comment-only lines are ignored on both sides (the ideal's why/src lines become the
    hunk note), paragraphs are re-flowed to one unit per paragraph, blank-line and whitespace changes are ignored."""
    live_all = live_tex.splitlines()
    li = [i for i, ln in enumerate(live_all) if not is_comment(ln)]
    live, lfirst, _ = reflow([live_all[i] for i in li])
    lnum = [li[f] + 1 for f in lfirst]                      # live line number of every unit
    raw, rnotes = split_ideal(ideal_tex)
    kept, knotes, carry = [], [], []
    for ln, n in zip(raw, rnotes[:-1]):
        carry = carry + n
        if is_comment(ln):
            continue
        kept.append(ln), knotes.append(carry)
        carry = []
    trailing = carry + rnotes[-1]
    ideal, _, notes = reflow(kept, knotes)
    sm = difflib.SequenceMatcher(None, live, ideal, autojunk=False)
    groups: list[list[int]] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if groups and all(not live[k] for k in range(groups[-1][1], i1)) \
                and all(not ideal[k] for k in range(groups[-1][3], j1)):
            groups[-1][1], groups[-1][3] = i2, j2
        else:
            groups.append([i1, i2, j1, j2])
    heading, sec_at = "", []
    for ln in live:
        m = SECTION_RE.search(ln)
        if m:
            heading = m.group(1)
        sec_at.append(heading)
    changed = {k for g in groups for k in range(g[2], g[3])}
    hunks, seen = [], {}
    for i1, i2, j1, j2 in groups:
        a, b = live[i1:i2], ideal[j1:j2]
        if all(not x for x in a + b):
            continue
        ctx_after = live[i2:i2 + CONTEXT]
        while a and not a[0]:                              # leading blank units: the hunk starts after them
            a, i1 = a[1:], i1 + 1
        while a and not a[-1]: a = a[:-1]
        while b and not b[0]: b = b[1:]
        while b and not b[-1]: b = b[:-1]
        note = [n for k in range(j1, min(j2 if b else j1 + 1, len(notes))) for n in notes[k]]
        k, crossed, blank = j1 - 1, 0, False
        while k >= 0:
            # Inside one blank-line-free block (a table, a list) walk up to its first note block, through changed
            # units that carry no note of their own; beyond a blank line reach at most NOTE_REACH units and never
            # through another hunk.  A changed unit with its own note belongs to its own hunk: stop.
            if notes[k] and (k not in changed or not ideal[k]):
                note = notes[k] + note
                break
            if k in changed and (blank or notes[k]):
                break
            if not ideal[k]:
                blank = True
            elif blank:
                crossed += 1
                if crossed > NOTE_REACH:
                    break
            k -= 1
        if j2 >= len(ideal):
            note += trailing
        n_ = len(live)
        line = lnum[i1] if i1 < n_ else (lnum[-1] + 1 if lnum else 1)
        sec = sec_at[min(i1, n_ - 1)] if n_ else ""
        hid = hunk_id(b, a)
        seen[hid] = seen.get(hid, 0) + 1
        if seen[hid] > 1:                                    # identical text twice: ordinal in document order
            hid = hashlib.sha1(f"{hid}#{seen[hid]}".encode()).hexdigest()
        hunks.append(Hunk(hid, "add" if not a else "del" if not b else "change", a, b, note, sec, line,
                          live[max(0, i1 - CONTEXT):i1], ctx_after))
    return hunks


def trailing_notes(ideal_tex: str) -> list[str]:
    return split_ideal(ideal_tex)[1][-1]


def conflict_lines(ideal_tex: str) -> list[int]:
    return [i + 1 for i, ln in enumerate(ideal_tex.splitlines()) if ln.startswith("<<<<<<<")]


# ---------------------------------------------------------------- rendering
TOKEN_RE = re.compile(r"(\s+|\\[a-zA-Z]+)")


def _tokens(text: str) -> list[str]:
    return [t for t in TOKEN_RE.split(text) if t]


def word_diff(a: str, b: str) -> tuple[str, str]:
    """HTML for the old and new text with changed word runs wrapped in <del>/<ins> (whitespace-insensitive match)."""
    ta, tb = _tokens(a), _tokens(b)
    k = lambda T: [" " if t.isspace() else t for t in T]  # noqa: E731
    sm = difflib.SequenceMatcher(None, k(ta), k(tb), autojunk=False)
    oa, ob = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        sa, sb = html.escape("".join(ta[i1:i2])), html.escape("".join(tb[j1:j2]))
        if tag == "equal":
            oa.append(sa), ob.append(sb)
        else:
            if sa.strip():
                oa.append(f"<del>{sa}</del>")
            else:
                oa.append(sa)
            if sb.strip():
                ob.append(f"<ins>{sb}</ins>")
            else:
                ob.append(sb)
    return "".join(oa), "".join(ob)


def _ctx(lines: list[str]) -> str:
    return f'<pre class="ctx">{html.escape(chr(10).join(lines))}</pre>' if lines else ""


def render_hunk(h: Hunk, checks: dict, interactive: bool) -> str:
    c = checks.get(h.id, {})
    done = bool(c.get("checked"))
    a, b = "\n".join(h.live_lines), "\n".join(h.ideal_lines)
    if h.kind == "change":
        ha, hb = word_diff(a, b)
    else:
        ha, hb = html.escape(a), html.escape(b)
    left = f'<pre class="side del">{ha}</pre>' if h.live_lines else '<pre class="side empty"></pre>'
    right = f'<pre class="side add">{hb}</pre>' if h.ideal_lines else '<pre class="side empty"></pre>'
    note = "".join(f"<div>{html.escape(n.lstrip('% ').strip())}</div>" for n in h.note)
    first = norm(" ".join(h.ideal_lines or h.live_lines))[:110]
    chk = (f'<input type="checkbox" class="tick" {"checked" if done else ""} onchange="tick(this)">'
           if interactive else "")
    copy = (f'<button class="cp" onclick="cp(this)" data-text="{html.escape(chr(10).join(h.ideal_lines), quote=True)}"'
            f'>copy ideal text</button>' if h.ideal_lines else "")
    sec = html.escape(h.section) if h.section else "(preamble)"
    return (f'<div class="hunk {"done" if done else "open"}" id="h{h.id[:10]}" data-id="{h.id}">'
            f'<div class="hh">{chk}<span class="k {h.kind}">{h.kind}</span><b>{sec}</b>'
            f'<span class="ln">live line {h.live_line}</span>{copy}'
            f'<span class="one">{html.escape(first)}</span></div>'
            f'<div class="body">{f"<div class=note>{note}</div>" if note else ""}'
            f'{_ctx(h.ctx_before)}<div class="cols">{left}{right}</div>{_ctx(h.ctx_after)}</div></div>')


CSS = """
:root{--line:#d0d7de;--mute:#57606a}
.pd{font-family:-apple-system,Segoe UI,sans-serif;font-size:13.5px;max-width:2400px}
.pd .head{background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px 16px;margin:0 0 12px;line-height:1.6}
.pd .head code{background:#f1f1f1;padding:0 4px;border-radius:3px}
.pd .banner{background:#ffebe9;border:1px solid #ff8182;color:#82071e;padding:8px 14px;border-radius:6px;margin:6px 0}
.pd .okb{color:#1a7f37}
.pd .filt button{border:1px solid var(--line);background:#fff;border-radius:14px;padding:2px 12px;cursor:pointer;margin-right:6px}
.pd .filt button.on{background:#1a5fb4;color:#fff;border-color:#1a5fb4}
.pd .hunk{background:#fff;border:1px solid var(--line);border-radius:6px;margin:0 0 12px;overflow:hidden}
.pd .hh{background:#f6f8fa;padding:6px 12px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;border-bottom:1px solid var(--line)}
.pd .hh .ln{color:var(--mute);font-size:12px} .pd .hh .cp{margin-left:auto;cursor:pointer}
.pd .k{font-size:11px;padding:1px 8px;border-radius:9px;font-weight:600}
.pd .k.add{background:#dafbe1;color:#1a7f37} .pd .k.del{background:#ffebe9;color:#cf222e} .pd .k.change{background:#fff8c5;color:#7d4e00}
.pd .note{padding:6px 12px;background:#fff8e6;border-bottom:1px solid var(--line);font-size:12.5px;color:#533f03}
.pd pre{margin:0;font:12px/1.5 ui-monospace,Menlo,monospace;white-space:pre-wrap;word-break:break-word;padding:6px 12px}
.pd pre.ctx{color:var(--mute);background:#fafbfc}
.pd .cols{display:grid;grid-template-columns:1fr}
.pd pre.del{background:#ffebe9} .pd pre.add{background:#dafbe1} .pd pre.empty{display:none}
.pd del{background:#ffc1c0;text-decoration:none} .pd ins{background:#aceebb;text-decoration:none}
@media(min-width:1000px){.pd .cols{grid-template-columns:repeat(2,minmax(0,1100px))} .pd pre.empty{display:block;background:#f6f8fa}
 .pd pre.side{border-right:1px solid var(--line)}}
.pd .one{display:none;color:var(--mute);font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:60%}
.pd .hunk.done .body{display:none} .pd .hunk.done .one{display:inline} .pd .hunk.done .hh{background:#eef7f0}
.pd .hunk.done .cp{display:none} .pd.f-open .hunk.done,.pd.f-ticked .hunk.open{display:none}
"""

JS = """
function cnt(){var h=document.querySelectorAll('.pd .hunk:not(.bib)'),d=document.querySelectorAll('.pd .hunk.done:not(.bib)');
 var e=document.getElementById('cnt'); if(e)e.textContent=d.length+' / '+h.length;
 var b=document.querySelectorAll('.pd .hunk.bib'),bd=document.querySelectorAll('.pd .hunk.bib.done');
 var f=document.getElementById('bcnt'); if(f)f.textContent=bd.length+' / '+b.length;}
function tick(el){var h=el.closest('.hunk'),on=el.checked;h.classList.toggle('done',on);h.classList.toggle('open',!on);cnt();
 fetch('/paper-diff/check',{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({hunk_id:h.dataset.id,checked:on})}).then(function(r){if(!r.ok)alert('saving the tick failed');})
  .catch(function(){alert('saving the tick failed');});}
function cp(b){var t=b.dataset.text,o=b.textContent;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(
 function(){b.textContent='copied';setTimeout(function(){b.textContent=o},1200)},
 function(){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove();});}
function filt(m,b){var p=document.querySelector('.pd');p.classList.remove('f-open','f-ticked');if(m!='all')p.classList.add('f-'+m);
 document.querySelectorAll('.pd .filt button').forEach(function(x){x.classList.toggle('on',x===b)});}
cnt();filt('open',document.querySelector('.pd .filt button'));
"""


def order_hunks(hunks: list[Hunk], checks: dict) -> list[Hunk]:
    """Open hunks first in file order, then the ticked ones by tick time, latest first.  checks[id]["when"] is the
    ISO time stamped by set_check at tick time (lexicographic order = time order).  A tick without a "when" predates
    the timestamps: it sorts after every timed tick, in file order (sorted() is stable)."""
    done = [h for h in hunks if checks.get(h.id, {}).get("checked")]
    openh = [h for h in hunks if not checks.get(h.id, {}).get("checked")]
    timed = sorted((h for h in done if checks[h.id].get("when")), key=lambda h: checks[h.id]["when"], reverse=True)
    untimed = [h for h in done if not checks[h.id].get("when")]
    return openh + timed + untimed


def render_body(hunks: list[Hunk], checks: dict, meta: dict) -> str:
    interactive = not meta.get("standalone")
    ticked = sum(1 for h in hunks if checks.get(h.id, {}).get("checked"))
    conf = meta.get("conflicts") or []
    if conf:
        rb = (f'<div class="banner">Rebase conflict markers in the ideal at line(s) '
              f'{", ".join(map(str, conf[:20]))}: resolve them in docs/paper_ideal/main.tex.</div>')
    else:
        rb = '<span class="okb">no conflict markers</span>'
    err = f'<div class="banner">live fetch: {html.escape(meta["error"])}</div>' if meta.get("error") else ""
    link = ('<a href="/paper-diff/latexdiff.pdf" target="_blank">latexdiff PDF</a> (built on demand, up to 3 min)'
            if interactive else "")
    head = (f'<div class="head"><b>Live</b> <code>{html.escape(str(meta.get("live_commit", "?")))}</code> '
            f'{html.escape(str(meta.get("live_date", "")))} &nbsp; <b>BASE</b> <code>{html.escape(str(meta.get("base", "?"))[:7])}</code>'
            f' &nbsp; <b>ideal</b> modified {html.escape(str(meta.get("ideal_mtime", "?")))} &nbsp; '
            f'<b>ticked</b> <span id="cnt">{ticked} / {len(hunks)}</span> &nbsp; <b>rebase</b> {rb} &nbsp; {link}{err}'
            f'<div class="filt"><button onclick="filt(\'open\',this)">open</button>'
            f'<button onclick="filt(\'ticked\',this)">ticked</button><button onclick="filt(\'all\',this)">all</button></div></div>')
    body = "".join(render_hunk(h, checks, interactive) for h in order_hunks(hunks, checks)) or \
        '<div class="head">No differences: the live paper equals the ideal.</div>'
    return f'<div class="pd">{head}{body}{meta.get("extra", "")}</div><script>{JS}</script>'


def render_html(hunks: list[Hunk], checks: dict, meta: dict) -> str:
    """Standalone page (CLI)."""
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>Paper diff</title><style>'
            f'body{{margin:16px;background:#f5f6f8}}{CSS}{EXTRA_CSS}</style></head><body>{render_body(hunks, checks, meta)}</body></html>')


# ---------------------------------------------------------------- live text, checks, latexdiff
_last_fetch = 0.0
_live_cache: dict = {}
_latexdiff_cache: dict = {}


NOT_INIT = "paper submodule not initialised: run git submodule update --init papers/FAA_emissions_paper"


def _git(*args, repo: Path = PAPER_REPO, timeout=60) -> subprocess.CompletedProcess:
    if not (Path(repo) / ".git").exists():     # an empty submodule folder would make git walk up into the model repo
        raise RuntimeError(NOT_INIT)
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=timeout)


def fetch_live(repo: Path = PAPER_REPO, ref: str = "origin/main", min_interval: float = 60.0) -> dict:
    """{text, commit, date, error}: fetch at most once per min_interval seconds, fall back to the last text."""
    global _last_fetch
    err = ""
    try:
        if time.time() - _last_fetch >= min_interval:
            _last_fetch = time.time()
            r = _git("fetch", "-q", "origin", repo=repo)
            if r.returncode:
                err = "git fetch failed: " + r.stderr.strip()
        r = _git("show", f"{ref}:main.tex", repo=repo)
        if r.returncode:
            raise RuntimeError(r.stderr.strip() or "git show failed")
        c = _git("log", "-1", "--format=%h|%cs", ref, repo=repo).stdout.strip().split("|")
        _live_cache.update(text=r.stdout, commit=c[0], date=c[-1] if len(c) > 1 else "")
    except Exception as e:  # noqa: BLE001
        err = (err + " " if err else "") + str(e)
    return {"text": _live_cache.get("text"), "commit": _live_cache.get("commit", "?"),
            "date": _live_cache.get("date", ""), "error": err}


def read_checks(ideal_dir: Path | None = None) -> dict:
    ideal_dir = ideal_dir or IDEAL_DIR
    try:
        return json.loads((ideal_dir / "checks.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def write_checks(checks: dict, ideal_dir: Path | None = None) -> None:
    ideal_dir = ideal_dir or IDEAL_DIR
    ideal_dir.mkdir(parents=True, exist_ok=True)
    tmp = ideal_dir / "checks.json.tmp"
    tmp.write_text(json.dumps(checks, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, ideal_dir / "checks.json")


def set_check(hunk_id: str, checked: bool, ideal_dir: Path | None = None) -> dict:
    checks = read_checks(ideal_dir)
    e = checks.get(hunk_id, {})
    e.update(checked=bool(checked), when=time.strftime("%Y-%m-%dT%H:%M:%S"))
    e.setdefault("note", "")
    checks[hunk_id] = e
    write_checks(checks, ideal_dir)
    return checks


def build_meta(live: dict, ideal_dir: Path, ideal_tex: str) -> dict:
    mt = ""
    try:
        mt = time.strftime("%Y-%m-%d %H:%M", time.localtime((ideal_dir / "main.tex").stat().st_mtime))
    except OSError:
        pass
    try:
        base = (ideal_dir / "BASE").read_text().strip()
    except OSError:
        base = "?"
    return {"live_commit": live["commit"], "live_date": live["date"], "base": base, "ideal_mtime": mt,
            "conflicts": conflict_lines(ideal_tex), "error": live.get("error", "")}


def page_body(repo: Path = PAPER_REPO, ideal_dir: Path | None = None) -> str:
    """Body (and CSS) of the dashboard tab."""
    ideal_dir = ideal_dir or IDEAL_DIR
    live = fetch_live(repo)
    try:
        ideal_tex = (ideal_dir / "main.tex").read_text(encoding="utf-8")
    except OSError:
        return f'<style>{CSS}</style><div class="pd"><div class="banner">{html.escape(str(ideal_dir / "main.tex"))} does not exist yet.</div></div>'
    if live["text"] is None:
        return f'<style>{CSS}</style><div class="pd"><div class="banner">live paper unavailable: {html.escape(live["error"])}</div></div>'
    hunks = compute(live["text"], ideal_tex)
    meta = build_meta(live, ideal_dir, ideal_tex) | {"extra": build_extras(live["text"], ideal_tex, repo, hunks, ideal_dir=ideal_dir,
                                                                 checks=read_checks(ideal_dir), live_commit=live["commit"])}
    return f"<style>{CSS}{EXTRA_CSS}</style>" + render_body(hunks, read_checks(ideal_dir), meta)


BIB_KEY_RE = re.compile(r"^\s*@[a-zA-Z]+\s*\{\s*([^,\s]+)\s*,", re.M)


def bib_new_entries(paper_bib: str, addition_bib: str) -> str:
    """Only the entries of addition_bib whose key is not in paper_bib (BibTeX aborts on repeated keys)."""
    have = {k.lower() for k in BIB_KEY_RE.findall(paper_bib)}
    starts = [m for m in re.finditer(r"^\s*@[a-zA-Z]+\s*\{", addition_bib, re.M)]
    out = []
    for i, m in enumerate(starts):
        chunk = addition_bib[m.start():starts[i + 1].start() if i + 1 < len(starts) else len(addition_bib)]
        k = BIB_KEY_RE.match(chunk)
        if k and k.group(1).lower() not in have:
            have.add(k.group(1).lower())
            out.append(chunk.rstrip() + "\n")
    return "\n".join(out)


def latexdiff_pdf(repo: Path = PAPER_REPO, ideal_dir: Path | None = None) -> tuple[bytes | None, str]:
    """(pdf bytes, "") or (None, error text).  Cached by (live text hash, ideal mtime)."""
    ideal_dir = ideal_dir or IDEAL_DIR
    live = fetch_live(repo)
    if live["text"] is None:
        return None, "live paper unavailable: " + live["error"]
    ideal = ideal_dir / "main.tex"
    if not ideal.is_file():
        return None, f"{ideal} does not exist"
    key = (hashlib.sha1(live["text"].encode()).hexdigest(), ideal.stat().st_mtime)
    if key in _latexdiff_cache:
        return _latexdiff_cache[key]
    for tool in ("latexdiff", "latexmk"):
        if not shutil.which(tool):
            return None, f"{tool} not found on PATH"
    d = Path(tempfile.mkdtemp(prefix="paperdiff_"))
    try:
        if not (Path(repo) / ".git").exists():
            return None, NOT_INIT
        ga = subprocess.Popen(["git", "-C", str(repo), "archive", "origin/main"], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        tar = subprocess.run(["tar", "-x", "-C", str(d)], stdin=ga.stdout, capture_output=True, timeout=120)
        ga.stdout.close()
        gerr = ga.stderr.read().decode(errors="replace")
        if ga.wait() or tar.returncode:
            return None, "git archive failed: " + gerr + tar.stderr.decode(errors="replace")
        figs = ROOT / "docs/paper_draft/figures"
        (d / "Figures").mkdir(exist_ok=True)
        for f in figs.glob("*"):
            if f.suffix.lower() in (".png", ".pdf") and not (d / "Figures" / f.name).exists():
                shutil.copy(f, d / "Figures" / f.name)
        add = ROOT / "docs/paper_draft/addition/refs_addition.bib"
        if add.is_file() and (d / "references.bib").is_file():
            paper_bib = (d / "references.bib").read_text(encoding="utf-8", errors="replace")
            with open(d / "references.bib", "a", encoding="utf-8") as fh:
                fh.write("\n" + bib_new_entries(paper_bib, add.read_text(encoding="utf-8")))
        (d / "live.tex").write_text(live["text"], encoding="utf-8")
        shutil.copy(ideal, d / "ideal.tex")
        ld = subprocess.run(["latexdiff", "live.tex", "ideal.tex"], cwd=d, capture_output=True, text=True, timeout=120)
        if not ld.stdout.strip():
            return None, "latexdiff produced no output:\n" + ld.stderr[-2000:]
        (d / "diff.tex").write_text(ld.stdout, encoding="utf-8")
        try:
            r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "diff.tex"], cwd=d,
                               capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            return None, "latexmk timed out after 180 s"
        pdf = d / "diff.pdf"
        if pdf.is_file() and pdf.stat().st_size > 0:
            res = (pdf.read_bytes(), "")
        else:
            log = (d / "diff.log").read_text(errors="replace")[-2500:] if (d / "diff.log").is_file() else ""
            res = (None, "latexmk failed (rc %s):\n%s\n%s" % (r.returncode, r.stdout[-1500:], log))
        if res[0]:
            _latexdiff_cache[key] = res
        return res
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------- figures and bibliography sections
# Spec: docs/specs/paper_diff_figures_bib.md.  Read-only views; the pure functions take injected texts so the tests
# need neither network nor the paper repo.
ADD_DIR = ROOT / "docs/paper_draft/addition"
FIG_DIRS = [ROOT / "docs/paper_draft/figures", ROOT / "docs/figures/paper"]
THUMB_DIR = Path(tempfile.gettempdir()) / "paper_diff_thumbs"
FIG_ENV_RE = re.compile(r"\\begin\{(figure\*?)\}(.*?)\\end\{\1\}", re.S)
GFX_RE = re.compile(r"\\includegraphics\s*(?:\[([^\]]*)\])?\s*\{([^}]*)\}")
FLAG_RE = re.compile(r"not yet verified|to be confirmed|unverified|preprint|publication status", re.I)
CITE_RE = re.compile(r"\\(?:cite[a-z]*|parencite|textcite|footcite|nocite)\*?\s*(?:\[[^\]]*\]\s*)*\{([^}]*)\}")


def strip_comments(tex: str) -> str:
    """Remove `%` comments (full-line and trailing; an escaped \\% is kept)."""
    return "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in tex.splitlines())


def _braced(s: str, start: int) -> tuple[str, int]:
    """Text of the balanced {...} group whose `{` is at s[start]; -> (inner, index after the closing brace)."""
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:i], i + 1
    return s[start + 1:], len(s)


@dataclass
class Fig:
    file: str
    options: str
    label: str
    caption: str
    number: int            # running figure number (the printed Fig. n); 0 outside a figure environment


def figures_in(tex: str) -> list[Fig]:
    """Every \\includegraphics of the text in document order, with its figure number, label and caption."""
    t = strip_comments(tex)
    envs = [(m.start(), m.end(), m.group(2)) for m in FIG_ENV_RE.finditer(t)]
    out = []
    for g in GFX_RE.finditer(t):
        n = next((i + 1 for i, (a, b, _) in enumerate(envs) if a <= g.start() < b), 0)
        label = caption = ""
        if n:
            body = envs[n - 1][2]
            lm = re.search(r"\\label\s*\{([^}]*)\}", body)
            label = lm.group(1).strip() if lm else ""
            cm = re.search(r"\\caption\s*(?:\[[^\]]*\])?\s*\{", body)
            if cm:
                caption = norm(_braced(body, cm.end() - 1)[0])
        out.append(Fig(g.group(2).strip(), norm(g.group(1) or ""), label, caption, n))
    return out


def find_sources(dirs=None) -> dict[str, str]:
    """basename -> model-repo path (relative to ROOT where possible); the first directory wins."""
    src: dict[str, str] = {}
    for d in (FIG_DIRS if dirs is None else dirs):
        for f in sorted(Path(d).glob("*")):
            if f.is_file():
                try:
                    p = str(f.relative_to(ROOT))
                except ValueError:
                    p = str(f)
                src.setdefault(f.name, p)
    return src


def figure_rows(live_tex: str, ideal_tex: str, live_files: set[str] | None = None, sources: dict | None = None,
                hunks: list | None = None) -> list[dict]:
    """The figure table: one dict per figure occurrence, ideal order first, live-only appended.
    live_files = names in the live tree (as 'Figures/x.pdf'); None = unknown (column shows '?').
    Matching: same file path (n-th occurrence against n-th occurrence), then same label with a different file."""
    sources = sources or {}
    ide, liv = figures_in(ideal_tex), figures_in(live_tex)
    used: set[int] = set()

    def mk(i: Fig | None, l: Fig | None, status: str) -> dict:
        ref = i or l
        why = ""
        if status == "live only" and hunks:
            for h in hunks:
                if any(l.file in x for x in h.live_lines) and h.note:
                    why = " ".join(n.lstrip("% ").strip() for n in h.note)
                    break
        known = live_files is not None
        return {"no": i.number if i else 0, "live_no": l.number if l else 0, "file": ref.file,
                "live_file": l.file if l else "", "options": i.options if i else "",
                "live_options": l.options if l else "", "label": ref.label, "caption": ref.caption[:90],
                "status": status, "why": why,
                "in_repo": (ref.file in live_files) if known else None,
                "source": sources.get(Path(ref.file).name)}

    rows: list[dict | None] = []
    for i in ide:
        m = next((k for k, l in enumerate(liv) if k not in used and l.file == i.file), None)
        if m is None:
            rows.append(None)
            continue
        used.add(m)
        rows.append(mk(i, liv[m], "same" if liv[m].options == i.options else "options changed"))
    for r_i, i in enumerate(ide):
        if rows[r_i] is not None:
            continue
        m = next((k for k, l in enumerate(liv) if k not in used and i.label and l.label == i.label), None)
        if m is not None:
            used.add(m)
            rows[r_i] = mk(i, liv[m], "file changed")
        else:
            rows[r_i] = mk(i, None, "ideal only")
    return rows + [mk(None, l, "live only") for k, l in enumerate(liv) if k not in used]


# --- thumbnails
def _git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def live_tree(repo: Path = PAPER_REPO, ref: str = "origin/main") -> dict[str, str]:
    """{'Figures/x.pdf': blob sha} of the live tree (one ls-tree call); raises RuntimeError if unavailable."""
    r = _git("ls-tree", "-r", ref, "--", "Figures/", repo=repo)
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or "git ls-tree failed")
    out = {}
    for ln in r.stdout.splitlines():
        meta, _, name = ln.partition("\t")
        out[name] = meta.split()[2]
    return out


def _thumb_png(data: bytes, suffix: str, key: str) -> Path | None:
    """Small PNG of a figure file, cached by content key.  PDF page 1 via pdftoppm, rasters via PIL, else sips."""
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    out = THUMB_DIR / f"{key}.png"
    if out.is_file() and out.stat().st_size:
        return out
    suffix = suffix.lower()
    with tempfile.TemporaryDirectory(prefix="pdthumb_") as td:
        src = Path(td) / f"in{suffix}"
        src.write_bytes(data)
        try:
            if suffix == ".pdf":
                exe = shutil.which("pdftoppm") or "/opt/homebrew/bin/pdftoppm"
                subprocess.run([exe, "-png", "-r", "30", "-f", "1", "-l", "1", "-singlefile", str(src),
                                str(Path(td) / "t")], capture_output=True, timeout=30, check=True)
                shutil.copy(Path(td) / "t.png", out)
            elif suffix in (".png", ".jpg", ".jpeg"):
                try:
                    from PIL import Image
                    with Image.open(src) as im:
                        im.thumbnail((220, 220))
                        im.convert("RGB").save(out, "PNG")
                except ImportError:
                    subprocess.run(["sips", "-Z", "220", "-s", "format", "png", str(src), "--out", str(out)],
                                   capture_output=True, timeout=30, check=True)
            else:
                return None
        except (OSError, subprocess.SubprocessError):
            return None
    return out if out.is_file() else None


def _read_blobs(repo: Path, shas: list[str]) -> dict[str, bytes]:
    """One `git cat-file --batch` call for all blobs."""
    if not shas:
        return {}
    p = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"], input="".join(s + "\n" for s in shas).encode(),
                       capture_output=True, timeout=120)
    buf, pos, out = p.stdout, 0, {}
    for s in shas:
        nl = buf.find(b"\n", pos)
        if nl < 0:
            break
        head = buf[pos:nl].split()
        if len(head) < 3 or head[1] != b"blob":
            pos = nl + 1
            continue
        n = int(head[2])
        out[s] = buf[nl + 1:nl + 1 + n]
        pos = nl + 1 + n + 1
    return out


def add_thumbnails(rows: list[dict], tree: dict[str, str] | None, repo: Path = PAPER_REPO) -> None:
    """Set row['thumb_live'], row['thumb_ideal'] (PNG paths or None) and row['differs'] in place.
    Live thumbnails come from the live blob, ideal ones from the model-repo source (shown only when it differs)."""
    tree = tree or {}
    need = {}
    for r in rows:
        sha = tree.get(r["live_file"] or r["file"])
        if sha and not (THUMB_DIR / f"git-{sha}.png").is_file():
            need[sha] = r["live_file"] or r["file"]
    try:
        blobs = _read_blobs(repo, list(need))
    except (OSError, subprocess.SubprocessError):
        blobs = {}
    for r in rows:
        lname = r["live_file"] or r["file"]
        sha = tree.get(lname) if r["status"] != "ideal only" or lname in tree else None
        r["thumb_live"], r["thumb_ideal"], r["differs"] = None, None, False
        if sha:
            tp = THUMB_DIR / f"git-{sha}.png"
            if tp.is_file():
                r["thumb_live"] = tp
            elif sha in blobs:
                r["thumb_live"] = _thumb_png(blobs[sha], Path(lname).suffix, f"git-{sha}")
        src = ROOT / r["source"] if r["source"] else None
        if src and src.is_file() and r["status"] != "live only":
            data = src.read_bytes()
            r["differs"] = (not sha) or _git_blob_sha(data) != sha
            if r["differs"]:
                r["thumb_ideal"] = _thumb_png(data, src.suffix, f"file-{hashlib.sha1(data).hexdigest()}")


# --- bibliography
@dataclass
class BibEntry:
    key: str
    type: str
    fields: dict
    raw: str
    items: list = field(default_factory=list)   # [(field name as written, value text, "brace" | "quote" | "bare")]


def parse_bib_list(text: str) -> list[BibEntry]:
    """Small regex parser, every entry in file order (a repeated key stays: BibTeX stops on it).
    Field values: braced (balanced), quoted or bare; `fields` holds whitespace-normalised values."""
    starts = list(re.finditer(r"^[ \t]*@([a-zA-Z]+)\s*\{", text, re.M))
    out: list[BibEntry] = []
    for i, m in enumerate(starts):
        typ = m.group(1).lower()
        if typ in ("comment", "string", "preamble"):
            continue
        chunk = text[m.start():starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        km = BIB_KEY_RE.match(chunk)
        if not km:
            continue
        body = chunk[km.end():]
        fields, items, pos = {}, [], 0
        while True:
            fm = re.compile(r"([A-Za-z][\w-]*)\s*=\s*").search(body, pos)
            if not fm or fm.end() >= len(body):
                break
            p = fm.end()
            if body[p] == "{":
                val, pos = _braced(body, p)
                kind = "brace"
            elif body[p] == '"':
                q = body.find('"', p + 1)
                q = q if q > 0 else len(body)
                val, pos = body[p + 1:q], q + 1
                kind = "quote"
            else:
                val = re.match(r"[^,\n}]*", body[p:]).group(0)
                pos = p + len(val)
                kind = "bare"
            fields.setdefault(fm.group(1).lower(), norm(val))
            items.append((fm.group(1), val.strip() if kind == "bare" else val, kind))
        out.append(BibEntry(km.group(1), typ, fields, chunk.rstrip() + "\n", items))
    return out


def parse_bib(text: str) -> dict[str, BibEntry]:
    """{lower-case key: BibEntry}, the first entry of a repeated key wins."""
    out: dict[str, BibEntry] = {}
    for e in parse_bib_list(text):
        out.setdefault(e.key.lower(), e)
    return out


def cited_keys(tex: str) -> dict[str, str]:
    """{lower-case key: key as written} cited by the text (comments ignored)."""
    out = {}
    for m in CITE_RE.finditer(strip_comments(tex)):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k != "*":
                out.setdefault(k.lower(), k)
    return out


def _doi(e: BibEntry) -> str:
    d = e.fields.get("doi", "").lower().strip()
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", d)


def _title_key(e: BibEntry) -> str:
    return re.sub(r"[^a-z0-9]", "", e.fields.get("title", "").lower())[:60]


# --- bibliography: entry-level diff of the live references.bib against the ideal (spec docs/specs/paper_diff_bib_ideal.md)
@dataclass
class BibCard:
    kind: str                 # add | change | delete
    key: str
    live: BibEntry | None
    ideal: BibEntry | None
    changes: list = field(default_factory=list)     # [(field, live value, ideal value)]: changed, added or removed fields
    unchanged: list = field(default_factory=list)   # [(field, value)]
    reason: str = ""          # delete cards: duplicate of KEY / uncited / corrections file / repeated key
    id: str = ""


REPEATED = "repeated key (BibTeX stops: 'Repeated entry')"


def bib_cards(live_bib: str, ideal_bib: str, reasons: dict | None = None) -> list[BibCard]:
    """One card per differing entry: add and change cards in the order of the ideal bib, then the delete cards in the
    order of the live bib.  A key repeated in the live bib gives a delete card for every copy after the first.
    reasons = {lower-case key: why the ideal dropped it} (from bib_report.json)."""
    reasons = reasons or {}
    live_list, ideal = parse_bib_list(live_bib), parse_bib(ideal_bib)
    first: dict[str, BibEntry] = {}
    extra: list[BibEntry] = []
    for e in live_list:
        if e.key.lower() in first:
            extra.append(e)
        else:
            first[e.key.lower()] = e
    cards = []

    def mk(kind, key, live, idl, **kw):
        cid = hashlib.sha1(f"bib:{kind}:{key.lower()}:{norm((idl or live).raw)}".encode()).hexdigest()
        return BibCard(kind, key, live, idl, id=cid, **kw)

    for lk, ie in ideal.items():
        le = first.get(lk)
        if le is None:
            cards.append(mk("add", ie.key, None, ie))
            continue
        names = list(dict.fromkeys(n.lower() for n, _, _ in ie.items)) + [n for n in le.fields if n not in ie.fields]
        ch = [(n, le.fields.get(n, ""), ie.fields.get(n, "")) for n in names if le.fields.get(n) != ie.fields.get(n)]
        if le.type != ie.type:
            ch.insert(0, ("(entry type)", le.type, ie.type))
        if ch:
            cards.append(mk("change", ie.key, le, ie, changes=ch,
                            unchanged=[(n, ie.fields[n]) for n in names if n in ie.fields and le.fields.get(n) == ie.fields[n]]))
    for lk, le in first.items():
        if lk not in ideal:
            cards.append(mk("delete", le.key, le, None, reason=reasons.get(lk, "not in the ideal bib")))
    for le in extra:
        cards.append(mk("delete", le.key, le, None, reason=REPEATED))
    return cards


def _bib_field_rows(c: BibCard) -> str:
    rows = []
    for n, old, new in c.changes:
        if old and new:
            ha, hb = word_diff(old, new)
            rows.append(f'<tr><td>{html.escape(n)}</td><td class="del">{ha}</td><td class="add">{hb}</td></tr>')
        elif new:
            rows.append(f'<tr><td>{html.escape(n)}</td><td class="empty"></td><td class="add">{html.escape(new)}</td></tr>')
        else:
            rows.append(f'<tr><td>{html.escape(n)}</td><td class="del">{html.escape(old)}</td><td class="empty"></td></tr>')
    unch = "".join(f"<div><code>{html.escape(n)}</code> {html.escape(v[:160])}</div>" for n, v in c.unchanged)
    return (f'<table class="bf"><thead><tr><th>field</th><th>live</th><th>ideal</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
            + (f'<details class="bu"><summary>{len(c.unchanged)} unchanged fields</summary>{unch}</details>' if c.unchanged else ""))


def render_bib_card(c: BibCard, checks: dict, interactive: bool) -> str:
    done = bool(checks.get(c.id, {}).get("checked"))
    chk = (f'<input type="checkbox" class="tick" {"checked" if done else ""} onchange="tick(this)">' if interactive else "")
    if c.kind == "add":
        body = f'<pre class="side add">{html.escape(c.ideal.raw)}</pre>'
        btn = _copy_btn(c.ideal.raw, "copy entry")
        one = c.ideal.fields.get("title", "")
    elif c.kind == "change":
        body = _bib_field_rows(c)
        btn = _copy_btn(c.ideal.raw, "copy ideal entry")
        one = ", ".join(n for n, _, _ in c.changes)
    else:
        body = (f'<div class="note">delete key <code>{html.escape(c.key)}</code>: {html.escape(c.reason)}</div>'
                f'<details class="bu"><summary>live entry</summary><pre class="side del">{html.escape(c.live.raw)}</pre></details>')
        btn = ""
        one = c.reason
    return (f'<div class="hunk bib {"done" if done else "open"}" id="b{c.id[:10]}" data-id="{c.id}">'
            f'<div class="hh">{chk}<span class="k {"del" if c.kind == "delete" else c.kind}">{c.kind}</span>'
            f'<b>{html.escape(c.key)}</b>{btn}<span class="one">{html.escape(one[:110])}</span></div>'
            f'<div class="body">{body}</div></div>')


def read_bib_report(ideal_dir: Path) -> dict:
    try:
        return json.loads((ideal_dir / "bib_report.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def render_bib_diff(cards: list[BibCard], checks: dict, meta: dict) -> str:
    """The Bibliography section.  meta: live_commit, error, report (bib_report.json), stale (list of notes), missing
    ([{key, live, ideal, in_ideal_bib}]), interactive."""
    rep = meta.get("report") or {}
    inter = meta.get("interactive", True)
    n = {k: sum(1 for c in cards if c.kind == k) for k in ("add", "change", "delete")}
    ticked = sum(1 for c in cards if checks.get(c.id, {}).get("checked"))
    banners = "".join(f'<div class="banner">{html.escape(m)}</div>' for m in
                      ([f"live bibliography unavailable: {meta['error']}"] if meta.get("error") else []) + list(meta.get("stale") or []))
    head = (f'<div class="sub"><b>Live</b> <code>{html.escape(str(meta.get("live_commit", "?")))}</code> &nbsp; '
            f'<b>ideal bib built on</b> <code>{html.escape(str(rep.get("live_commit", "?")))}</code> {html.escape(str(rep.get("built", "")))}'
            f' &nbsp; <b>done</b> <span id="bcnt">{ticked} / {len(cards)}</span> bib hunks &nbsp; '
            f'{n["add"]} add, {n["change"]} change, {n["delete"]} delete</div>')
    body = "".join(render_bib_card(c, checks, inter) for c in cards) or '<p>No differences: the live bibliography equals the ideal.</p>'
    once = rep.get("cited_once") or []
    once_h = "".join(f'<tr><td><code>{html.escape(x["key"])}</code></td><td>{html.escape(x["sentence"])}</td></tr>' for x in once)
    miss = meta.get("missing") or []
    miss_h = "".join(
        f'<tr><td><code>{html.escape(m["key"])}</code></td><td>{" + ".join(w for w, on in (("live", m["live"]), ("ideal", m["ideal"])) if on)}</td>'
        f'<td>{"yes" if m["in_ideal_bib"] else "<b class=no>no</b>"}</td></tr>' for m in miss)
    return (f'<div class="sec" id="bib"><h2>Bibliography</h2>{banners}{head}{body}'
            f'<details class="bu"><summary>Cited once ({len(once)}): sources to drop when space is short</summary>'
            f'<table class="ft"><thead><tr><th>key</th><th>sentence of the ideal text</th></tr></thead><tbody>{once_h}</tbody></table></details>'
            f'<details class="bu"><summary>Cited but not in the live bib ({len(miss)}): BibTeX warnings</summary>'
            f'<table class="ft"><thead><tr><th>key</th><th>cited by</th><th>in the ideal bib</th></tr></thead><tbody>{miss_h}</tbody></table></details></div>')


def bib_section(live_tex: str, ideal_tex: str, live_bib: str, ideal_dir: Path, live_commit: str = "?", error: str = "",
                checks: dict | None = None, interactive: bool = True) -> str:
    """HTML of the Bibliography section from the live bib and docs/paper_ideal/references.bib (+ bib_report.json)."""
    ibp = ideal_dir / "references.bib"
    ideal_bib = _read_text(ibp)
    if ideal_bib is None:
        return (f'<div class="sec" id="bib"><h2>Bibliography</h2><div class="banner">{html.escape(str(ibp))} does not exist: '
                f'run python scripts/paper_ideal_bib.py</div></div>')
    rep = read_bib_report(ideal_dir)
    reasons = {d["key"].lower(): d["reason"] for d in rep.get("deleted", [])}
    cards = bib_cards(live_bib, ideal_bib, reasons)
    stale = []
    if rep.get("live_commit") and live_commit not in ("?", rep["live_commit"]):
        stale.append(f"ideal bib built on live {rep['live_commit']}, live is now {live_commit}: rerun scripts/paper_ideal_bib.py")
    try:
        if (ideal_dir / "main.tex").stat().st_mtime > ibp.stat().st_mtime + 1:
            stale.append("docs/paper_ideal/main.tex is newer than references.bib: rerun scripts/paper_ideal_bib.py")
    except OSError:
        pass
    have = set(parse_bib(live_bib))
    ib = set(parse_bib(ideal_bib))
    ci, cl = cited_keys(ideal_tex), cited_keys(live_tex)
    miss = [{"key": ci.get(k) or cl[k], "live": k in cl, "ideal": k in ci, "in_ideal_bib": k in ib}
            for k in sorted(set(ci) | set(cl)) if k not in have]
    if rep.get("ideal_cites_missing"):
        stale.append("the ideal text cites keys that the ideal bib lacks (fix the \\cite or the bib): "
                     + ", ".join(rep["ideal_cites_missing"]))
    meta = {"live_commit": live_commit, "error": error, "report": rep, "stale": stale, "missing": miss, "interactive": interactive}
    return render_bib_diff(cards, checks or {}, meta)


def _copy_btn(text: str, label: str) -> str:
    return f'<button class="cp" onclick="cp(this)" data-text="{html.escape(text, quote=True)}">{html.escape(label)}</button>'


def _thumb_tag(p: Path | None, label: str) -> str:
    import base64
    if p and Path(p).is_file():
        b = base64.b64encode(Path(p).read_bytes()).decode()
        return f'<figure class="th"><img src="data:image/png;base64,{b}" alt=""><figcaption>{label}</figcaption></figure>'
    return f'<figure class="th"><div class="grey">{label}</div></figure>'


STATUS_CLS = {"same": "ok", "options changed": "warn", "file changed": "warn", "ideal only": "new", "live only": "gone"}


def render_figures(rows: list[dict], tree_error: str = "") -> str:
    cnt: dict[str, int] = {}
    for r in rows:
        cnt[r["status"]] = cnt.get(r["status"], 0) + 1
    summ = ", ".join(f"{v} {k}" for k, v in cnt.items())
    err = f'<div class="banner">paper repo tree unavailable: {html.escape(tree_error)}</div>' if tree_error else ""
    tr = []
    for r in rows:
        st, src = r["status"], r["source"]
        if st == "live only":
            fname, opts = html.escape(r["live_file"]), html.escape(r["live_options"])
        else:
            fname, opts = html.escape(r["file"]), html.escape(r["options"])
            if st == "options changed":
                opts = f'<del>{html.escape(r["live_options"])}</del> &rarr; <ins>{opts}</ins>'
            if st == "file changed":
                fname = f'<del>{html.escape(r["live_file"])}</del> &rarr; <ins>{fname}</ins>'
        if r["in_repo"] is None:
            repo = "?"
        elif r["in_repo"]:
            repo = "yes"
        else:
            repo = '<b class="no">NO</b>' + (" (upload needed)" if st == "ideal only" else "")
        actionable = st in ("ideal only", "file changed", "options changed") or r["in_repo"] is False
        srcs = cb = ""
        if actionable and st != "live only":
            srcs = (f'<div class="src">source <code>{html.escape(src)}</code></div>' if src
                    else '<div class="src">no source found</div>')
            cb = _copy_btn(src, "copy source path") if src else ""
        why = (f'<div class="src">removed in the ideal{": " + html.escape(r["why"]) if r["why"] else ""}</div>'
               if st == "live only" else "")
        gone = "missing in paper repo"
        live_t = _thumb_tag(r.get("thumb_live"), gone if r["in_repo"] is False or st == "ideal only" else "live")
        if r.get("differs"):
            th = live_t + _thumb_tag(r.get("thumb_ideal"), "ideal")
        elif st == "ideal only":
            th = _thumb_tag(r.get("thumb_ideal"), "ideal (not in paper repo)" if r.get("thumb_ideal") else gone)
        else:
            th = live_t
        no = r["no"] or "-"
        if r["live_no"] and r["live_no"] != r["no"]:
            no = f'{no} (live {r["live_no"]})'
        tr.append(f'<tr><td>{no}</td><td><code>{fname}</code></td><td><code>{opts}</code></td>'
                  f'<td>{html.escape(r["label"])}<div class="cap">{html.escape(r["caption"])}</div></td>'
                  f'<td><span class="k {STATUS_CLS[st]}">{st}</span>{why}</td><td>{repo}{srcs}{cb}</td>'
                  f'<td class="ths">{th}</td></tr>')
    return (f'<div class="sec" id="figures"><h2>Figures ({len(rows)})</h2><div class="sub">{html.escape(summ)}</div>{err}'
            f'<table class="ft"><thead><tr><th>no.</th><th>file</th><th>options</th><th>label, caption</th><th>status</th>'
            f'<th>in paper repo</th><th>thumbnail</th></tr></thead><tbody>{"".join(tr)}</tbody></table></div>')


def _read_text(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return None


def build_extras(live_tex: str, ideal_tex: str, repo: Path = PAPER_REPO, hunks: list | None = None,
                 ref: str = "origin/main", ideal_dir: Path | None = None, checks: dict | None = None,
                 interactive: bool = True, live_commit: str = "?") -> str:
    """HTML of the Figures and Bibliography sections (reads the live tree and bib from the paper repo, read-only)."""
    tree, terr = None, ""
    try:
        tree = live_tree(repo, ref)
    except Exception as e:  # noqa: BLE001
        terr = str(e)
    rows = figure_rows(live_tex, ideal_tex, None if tree is None else set(tree), find_sources(), hunks)
    try:
        add_thumbnails(rows, tree, repo)
    except Exception as e:  # noqa: BLE001
        terr = (terr + " " if terr else "") + f"thumbnails: {e}"
    live_bib, berr = "", ""
    try:
        r = _git("show", f"{ref}:references.bib", repo=repo)
        if r.returncode:
            raise RuntimeError(r.stderr.strip() or "git show failed")
        live_bib = r.stdout
    except Exception as e:  # noqa: BLE001
        berr = str(e)
    return render_figures(rows, terr) + bib_section(live_tex, ideal_tex, live_bib, ideal_dir or IDEAL_DIR, live_commit,
                                                    berr, checks, interactive)


EXTRA_CSS = """
.pd .sec{background:#fff;border:1px solid var(--line);border-radius:6px;margin:18px 0 12px;padding:6px 16px 14px;max-width:2200px}
.pd .sec h2{margin:8px 0 2px} .pd .sec h3{margin:16px 0 6px} .pd .sub{color:var(--mute);margin-bottom:8px}
.pd table.ft{border-collapse:collapse;width:100%} .pd .ft th,.pd .ft td{border-bottom:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}
.pd .ft th{background:#f6f8fa} .pd .ft .cap,.pd .ft .src{color:var(--mute);font-size:12px} .pd .no{color:#cf222e}
.pd .k.ok{background:#dafbe1;color:#1a7f37} .pd .k.warn{background:#fff8c5;color:#7d4e00}
.pd .k.new{background:#ddf4ff;color:#0550ae} .pd .k.gone{background:#ffebe9;color:#cf222e}
.pd .ths{white-space:nowrap} .pd figure.th{display:inline-block;margin:0 8px 0 0;vertical-align:top;text-align:center}
.pd figure.th img{max-width:220px;max-height:220px;border:1px solid var(--line)} .pd figure.th figcaption{font-size:11px;color:var(--mute)}
.pd .grey{background:#e6e8eb;color:var(--mute);width:150px;height:60px;display:flex;align-items:center;justify-content:center;font-size:11px;text-align:center}
.pd .cpbox{border:1px solid var(--line);border-radius:4px;margin:0 0 8px;overflow:hidden}
.pd .cpbox .hh{background:#f6f8fa;padding:4px 10px;display:flex;gap:10px;align-items:center}
.pd table.bf{border-collapse:collapse;width:100%} .pd .bf th,.pd .bf td{border-bottom:1px solid var(--line);padding:4px 10px;text-align:left;vertical-align:top;font:12px/1.5 ui-monospace,Menlo,monospace;white-space:pre-wrap;word-break:break-word}
.pd .bf th{background:#f6f8fa} .pd .bf td.del{background:#ffebe9} .pd .bf td.add{background:#dafbe1} .pd .bf td.empty{background:#f6f8fa}
.pd details.bu{margin:6px 12px;font-size:12.5px} .pd details.bu div{padding:1px 0;color:var(--mute)} .pd .sec>details.bu{margin:10px 0 0}
.pd .cpbox>.cp{float:right;margin:4px} .pd .md code{background:#f1f1f1;padding:0 3px;border-radius:3px}
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="standalone HTML to write")
    ap.add_argument("--ideal", default=str(IDEAL_DIR / "main.tex"))
    ap.add_argument("--paper-repo", default=str(PAPER_REPO), help="paper repo to read (read-only); default papers/FAA_emissions_paper")
    ap.add_argument("--live-file", help="read the live text from this file instead of origin/main")
    a = ap.parse_args(argv)
    ideal_path = Path(a.ideal)
    if a.live_file:
        live = {"text": Path(a.live_file).read_text(encoding="utf-8"), "commit": a.live_file, "date": "", "error": ""}
    else:
        live = fetch_live(Path(a.paper_repo))
        if live["text"] is None:
            raise SystemExit("live paper unavailable: " + live["error"])
    ideal_tex = ideal_path.read_text(encoding="utf-8")
    hunks = compute(live["text"], ideal_tex)
    meta = build_meta(live, ideal_path.parent, ideal_tex) | {"standalone": True,
                                                              "extra": build_extras(live["text"], ideal_tex, Path(a.paper_repo), hunks, ideal_dir=ideal_path.parent,
                                                              interactive=False, live_commit=live["commit"])}
    Path(a.out).write_text(render_html(hunks, {}, meta), encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
