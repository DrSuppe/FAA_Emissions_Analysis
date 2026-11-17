# Ported from the LNG project dashboard, feat/gui-iteration @ e19d975, 2026-11-17
"""Small markdown -> HTML renderer for the dashboard's Paper page (stdlib only).

Covers what docs/paper_sections/*.md and the paper review use: `#`..`####` headings, paragraphs, `-` / `1.`
lists (one level of nesting by indent), `**bold**`, `*italic*`, inline code, fenced code blocks, pipe tables,
links `[t](u)`, horizontal rules.  Everything is HTML-escaped first; unknown syntax falls through as text.
"""
from __future__ import annotations

import html
import re

_CODE = re.compile(r"`([^`]+)`")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITAL = re.compile(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])")
_LIST = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
_HEAD = re.compile(r"^(#{1,4})\s+(.*?)\s*#*\s*$")
_RULE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def inline(text: str) -> str:
    """Lift code spans out (literal), escape, then links / bold / italic, then put the code spans back."""
    spans: list[str] = []

    def lift(m):
        spans.append(f"<code>{html.escape(m.group(1), quote=False)}</code>")
        return f"\x00{len(spans) - 1}\x00"

    s = html.escape(_CODE.sub(lift, text), quote=False)

    def link(m):
        url = m.group(2)
        if url.lower().startswith("javascript:"):
            return m.group(0)
        return f'<a href="{html.escape(url, quote=True)}">{m.group(1)}</a>'

    s = _LINK.sub(link, s)
    s = _BOLD.sub(r"<strong>\1</strong>", s)
    s = _ITAL.sub(r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], s)


def _cells(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def _list_html(items: list[tuple[int, str, str]]) -> str:
    """items = (indent, marker, text); items indented deeper than the first nest under the item before them."""
    base = items[0][0]
    tag = "ol" if items[0][1][0].isdigit() else "ul"
    out, i = [f"<{tag}>"], 0
    while i < len(items):
        txt = items[i][2]
        i += 1
        sub = []
        while i < len(items) and items[i][0] > base:
            sub.append(items[i])
            i += 1
        out.append(f"<li>{inline(txt)}{_list_html(sub) if sub else ''}</li>")
    out.append(f"</{tag}>")
    return "".join(out)


def render(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    para: list[str] = []

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(p.strip() for p in para))}</p>")
            para.clear()

    while i < n:
        ln = lines[i]
        if ln.strip().startswith("```"):
            flush()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(buf), quote=False)}</code></pre>")
            continue
        if not ln.strip():
            flush()
            i += 1
            continue
        m = _HEAD.match(ln)
        if m:
            flush()
            lv = len(m.group(1))
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>")
            i += 1
            continue
        if _RULE.match(ln):
            flush()
            out.append("<hr>")
            i += 1
            continue
        if "|" in ln and i + 1 < n and "|" in lines[i + 1] and _SEP.match(lines[i + 1]):
            flush()
            head = _cells(ln)
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_cells(lines[i]))
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f"<table><tr>{th}</tr>{tb}</table>")
            continue
        if _LIST.match(ln):
            flush()
            items: list[tuple[int, str, str]] = []
            while i < n:
                m = _LIST.match(lines[i])
                if m:
                    items.append((len(m.group(1).expandtabs(4)), m.group(2), m.group(3)))
                    i += 1
                elif lines[i].strip() and lines[i].startswith((" ", "\t")) and items:   # continuation line
                    ind, mk, tx = items[-1]
                    items[-1] = (ind, mk, tx + " " + lines[i].strip())
                    i += 1
                else:
                    break
            out.append(_list_html(items))
            continue
        para.append(ln)
        i += 1
    flush()
    return "\n".join(out)
