# Ported from the LNG project dashboard, feat/gui-iteration @ e19d975, 2026-11-17
"""FAA project dashboard: one local page for what changed, the paper, the paper diff, decisions and the task list.

    python3 scripts/fit_dashboard.py [--host 127.0.0.1] [--port 8771] [--gallery-refresh 300]

Open http://127.0.0.1:<port>/ (binds 127.0.0.1 by default; the dashboard has NO authentication, so keep it local).
Spec: docs/specs/dashboard.md.  Pages (all rebuilt from files on every load):
  /            What changed: cards from docs/dashboard/changes.yaml plus an auto card for every docs/findings.md row
               that no curated card names (scripts/dashboard_changes.py).
  /paper       the paper sections rendered from docs/paper_sections/*.md.
  /paper-diff  GitHub-style diff of the live Overleaf paper (clone papers/FAA_emissions_paper, origin/main, only
               fetched and read) against docs/paper_ideal/main.tex, with tick boxes (scripts/paper_diff.py);
               POST /paper-diff/check writes docs/paper_ideal/checks.json; /paper-diff/latexdiff.pdf is the latexdiff.
  /decisions   docs/paper_tracking/decisions.md (scripts/decisions_page.py).
  /todo        docs/paper_tracking/todo.md grouped by owner (scripts/todo_page.py).
  /file?path=<repo-relative .md/.csv/.json/.yaml/.txt> serves text (.md rendered), confined to the repo.
  /results     results gallery of scripts/results_gallery.py (route kept, tab hidden until a results folder exists);
               /img?path=<repo-relative png> serves PNGs under the repo only.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dashboard_changes  # noqa: E402
import dashboard_md  # noqa: E402
import decisions_page  # noqa: E402
import todo_page  # noqa: E402
import paper_diff  # noqa: E402
import results_gallery  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FILE_SUFFIXES = {".md": "text/html; charset=utf-8", ".csv": "text/plain; charset=utf-8",
                 ".json": "text/plain; charset=utf-8", ".yaml": "text/plain; charset=utf-8",
                 ".yml": "text/plain; charset=utf-8", ".txt": "text/plain; charset=utf-8"}
PAGE_CSS = """
.page{max-width:1300px;margin:0 auto;padding:16px 24px 60px}
.page.wide{max-width:2400px}
.card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin:0 0 12px}
.card h2{font-size:14px;margin:0 0 8px;color:#444}
.chg{background:#fff;border:1px solid var(--line);border-left:5px solid #999;border-radius:8px;padding:10px 16px;margin:0 0 10px}
.chg.done{border-left-color:#2e8b57} .chg.running{border-left-color:#1a5fb4} .chg.draft{border-left-color:#d69e2e}
.chg.waiting{border-left-color:#999} .chg.auto{opacity:.85}
.chg h3{font-size:15px;margin:0 0 4px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.chg h3 small{color:var(--mute);font-weight:normal;font-size:12px;margin-left:auto}
.st{font-size:11px;padding:1px 8px;border-radius:9px;font-weight:600;background:#eee;color:#555}
.st.done{background:#e3f4e8;color:#1e6b34} .st.running{background:#e6eefb;color:#1e4b8f} .st.draft{background:#fff2d8;color:#8a5a00}
.fid{font-size:12px;color:#1e4b8f;font-weight:600} .sum{margin:2px 0 6px;font-size:13.5px} .nums{margin:2px 0 6px;font-size:12.5px;color:#333}
table.ct,.md table{border-collapse:collapse;margin:6px 0;font-size:12.5px} table.ct td,table.ct th,.md td,.md th{border:1px solid var(--line);padding:3px 8px;text-align:left}
.thumbs{display:flex;gap:10px;flex-wrap:wrap;margin:6px 0} .thumb{display:block;width:260px;font-size:11px;color:#555}
.thumb img{width:260px;border:1px solid var(--line);border-radius:4px;background:#fff;display:block} .links{font-size:12.5px;margin:4px 0 0}
.miss{color:#9b1c1c;font-size:12px} .fig2{max-width:100%;border:1px solid var(--line);border-radius:4px}
.md{font-size:13.5px;line-height:1.5;max-width:960px} .md pre{background:#f4f4f4;padding:8px;border-radius:6px;overflow:auto;font-size:12px}
.md h1{font-size:20px} .md h2{font-size:17px;color:#222} .md h3{font-size:15px} .md code{background:#f1f1f1;padding:0 3px;border-radius:3px}
.note{color:var(--mute);font-size:12px;margin:8px 0 0}
"""



def shell(title: str, active: str, body: str, refresh: int | None, extra: str = "") -> str:
    meta = f'<meta http-equiv="refresh" content="{refresh}">' if refresh else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>FAA {html.escape(title)}</title>{meta}'
            f"<style>{results_gallery.STYLE}{PAGE_CSS}</style></head><body>"
            f'{results_gallery.nav_bar(active, extra)}<div class="page{" wide" if active in ("paperdiff", "decisions", "todo") else ""}">{body}</div></body></html>')


def changes_page(refresh: int | None) -> str:
    return shell("what changed", "changes", dashboard_changes.render_changes(ROOT), refresh,
                 f'<small>{time.strftime("%H:%M:%S")}</small>')


def paper_page(refresh: int | None) -> str:
    return shell("paper", "paper", dashboard_changes.render_paper(ROOT), refresh, f'<small>{time.strftime("%H:%M:%S")}</small>')


class Handler(BaseHTTPRequestHandler):
    server_version = "FAADashboard/1"
    cfg: dict = {}

    def _send(self, body: bytes, ctype: str, code: int = 200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/paper"):
            try:
                refresh = self.cfg["gallery_refresh"] or None
                page_html = changes_page(refresh) if path == "/" else paper_page(refresh)
                self._send(page_html.encode(), "text/html; charset=utf-8")
            except Exception as e:  # noqa: BLE001
                self._send(f"page failed: {e}".encode(), "text/plain", 500)
        elif path == "/paper-diff":
            try:
                self._send(shell("paper diff", "paperdiff", paper_diff.page_body(), None).encode(), "text/html; charset=utf-8")
            except Exception as e:  # noqa: BLE001
                self._send(f"page failed: {e}".encode(), "text/plain", 500)
        elif path == "/decisions":
            try:
                self._send(shell("decisions", "decisions", decisions_page.page_body(parse_qs(urlparse(self.path).query).get("sort", ["critical"])[0]), None).encode(), "text/html; charset=utf-8")
            except Exception as e:  # noqa: BLE001
                self._send(f"page failed: {e}".encode(), "text/plain", 500)
        elif path == "/todo":
            try:
                self._send(shell("todo", "todo", todo_page.page_body(parse_qs(urlparse(self.path).query).get("show", ["open"])[0]), None).encode(), "text/html; charset=utf-8")
            except Exception as e:  # noqa: BLE001
                self._send(f"page failed: {e}".encode(), "text/plain", 500)
        elif path == "/paper-diff/latexdiff.pdf":
            pdf, err = paper_diff.latexdiff_pdf()
            if pdf:
                self._send(pdf, "application/pdf")
            else:
                self._send(err.encode(), "text/plain; charset=utf-8", 500)
        elif path == "/file":
            self._send_file(parse_qs(urlparse(self.path).query).get("path", [""])[0])
        elif path == "/results":
            try:
                body = results_gallery.render_html(results_gallery.build_groups(ROOT),
                                                   lambda p: f"/img?path={p.as_posix()}", home="/",
                                                   refresh=self.cfg["gallery_refresh"])
                self._send(body.encode(), "text/html; charset=utf-8")
            except Exception as e:  # noqa: BLE001
                self._send(f"gallery failed: {e}".encode(), "text/plain", 500)
        elif path == "/img":
            self._send_image(parse_qs(urlparse(self.path).query).get("path", [""])[0])
        else:
            self._send(b"not found", "text/plain", 404)

    def _send_image(self, rel: str):
        """A PNG under the repo root only: the resolved path must stay inside ROOT (no `..`, no symlink escape)."""
        try:
            target = (ROOT / rel).resolve()
            ok = bool(rel) and target.suffix.lower() == ".png" and target.is_file() and ROOT in target.parents
        except (ValueError, OSError):  # e.g. a NUL byte in the query path
            ok = False
        if ok:
            self._send(target.read_bytes(), "image/png")
        else:
            self._send(b"not found", "text/plain", 404)

    def _send_file(self, rel: str):
        """A text file under the repo root: allowed suffixes only, resolved path must stay inside ROOT.
        .md is rendered as a page, the others are sent as text/plain."""
        try:
            target = (ROOT / rel).resolve()
            ok = bool(rel) and target.suffix.lower() in FILE_SUFFIXES and target.is_file() and ROOT in target.parents
        except (ValueError, OSError):
            ok = False
        if not ok:
            self._send(b"not found", "text/plain", 404)
            return
        text = target.read_text(encoding="utf-8", errors="replace")
        if target.suffix.lower() == ".md":
            body = shell(target.name, "changes", f'<div class="card"><p class="note">{html.escape(rel)}</p>'
                         f'<div class="md">{dashboard_md.render(text)}</div></div>', None)
            self._send(body.encode(), FILE_SUFFIXES[".md"])
        else:
            self._send(text.encode(), FILE_SUFFIXES[target.suffix.lower()])

    def do_POST(self):  # noqa: N802
        if urlparse(self.path).path == "/paper-diff/check":
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                hid = str(req["hunk_id"])
                if not re.fullmatch(r"[0-9a-f]{40}", hid):
                    raise ValueError("bad hunk_id")
                paper_diff.set_check(hid, bool(req.get("checked")))
                self._send(b'{"ok": true}', "application/json")
            except Exception as e:  # noqa: BLE001
                self._send(f"check failed: {e}".encode(), "text/plain", 400)
            return
        self._send(b"not found", "text/plain", 404)

    def log_message(self, fmt, *args):  # quiet: no per-request log lines
        return


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--host", default="127.0.0.1",
                    help="address to bind (default 127.0.0.1, this machine only); 0.0.0.0 makes the dashboard reachable "
                         "on the LAN WITHOUT any authentication")
    ap.add_argument("--port", type=int, default=8771)
    ap.add_argument("--gallery-refresh", type=int, default=300, help="page reload interval in seconds (0: none)")
    a = ap.parse_args(argv)
    Handler.cfg = {"gallery_refresh": a.gallery_refresh}
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    shown = "127.0.0.1" if a.host in ("0.0.0.0", "") else a.host
    print(f"dashboard at http://{shown}:{a.port}/ ; Ctrl-C to stop", flush=True)
    if a.host not in ("127.0.0.1", "localhost", "::1"):
        print(f"WARNING: bound to {a.host}: reachable from the network, no authentication", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
