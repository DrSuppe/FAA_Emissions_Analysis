"""Dashboard pages (spec docs/specs/dashboard.md): cards, markdown, /file confinement, decisions and todo parsing."""
from __future__ import annotations

import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import dashboard_changes as dc  # noqa: E402
import dashboard_md as md  # noqa: E402
import decisions_page as dp  # noqa: E402
import fit_dashboard as fd  # noqa: E402
import results_gallery as rg  # noqa: E402
import todo_page as tp  # noqa: E402

import pytest  # noqa: E402

FINDINGS = """| # | Date | Finding | Evidence | Status |
|---|---|---|---|---|
| F1 | 2026-10-01 | The first thing we learned is that the model reproduces the fuel effect on CO2. More text. | `docs/results/a/2026-10-01_abc1234/` | **quotable** |
| F2 | 2026-10-02 | The second finding is covered by a curated card and must not get an auto card here. | `docs/results/a/2026-10-02_abc1234/` | provisional |
"""


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "docs/results/a/2026-10-01_abc1234").mkdir(parents=True)
    (tmp_path / "docs/results/a/2026-10-01_abc1234/p.png").write_bytes(b"\x89PNG")
    (tmp_path / "docs/results/a/2026-10-02_abc1234").mkdir(parents=True)
    (tmp_path / "docs/findings.md").write_text(FINDINGS, encoding="utf-8")
    (tmp_path / "docs/dashboard").mkdir(parents=True)
    (tmp_path / "docs/dashboard/changes.yaml").write_text("""
- {date: 2026-10-03, time: "09:00", title: Older card, summary: s1, status: done}
- {date: 2026-10-05, time: "08:00", title: Newer card, summary: s2, status: running, finding: F2,
   numbers: ["a: 1"], table: {columns: [x, y], rows: [[1, 2]]},
   links: [{label: pic, path: docs/results/a/2026-10-01_abc1234/p.png}, {label: gone, path: docs/nope.png}]}
""", encoding="utf-8")
    return tmp_path


def test_curated_cards_sorted_and_rendered(tmp_path):
    root = _repo(tmp_path)
    cards = dc.all_cards(root)
    titles = [c["title"] for c in cards]
    assert titles.index("Newer card") < titles.index("Older card")
    html_ = dc.render_card(next(c for c in cards if c["title"] == "Newer card"), root, {})
    assert "running" in html_ and "<table" in html_ and "a: 1" in html_
    assert "/img?path=docs/results/a/2026-10-01_abc1234/p.png" in html_      # PNG -> thumbnail
    assert "gone: not yet merged" in html_                                    # missing file does not fail


def test_finding_without_card_gets_auto_card(tmp_path):
    root = _repo(tmp_path)
    auto = [c for c in dc.all_cards(root) if c.get("auto")]
    assert [c["finding"] for c in auto] == ["F1"]                             # F2 is named by a curated card
    assert "reproduces the fuel effect" in auto[0]["summary"]
    assert any("p.png" in lk["path"] for lk in auto[0]["links"])
    assert "F1" in dc.render_changes(root)


def test_shipped_changes_yaml_has_the_seed_cards():
    cards = dc.load_curated(REPO)
    assert len(cards) >= 3
    assert "GT2027 abstract accepted" in {c["title"] for c in cards}
    assert all(c["status"] in dc.STATUSES for c in cards)
    assert all(c.get("date") and c.get("title") and c.get("summary") for c in cards)


def test_nav_bar_has_exactly_the_five_tabs():
    bar = rg.nav_bar("changes")
    for label in ("What changed", "Paper", "Paper diff", "Decisions", "ToDo"):
        assert f">{label}</a>" in bar
    assert bar.count("<a ") == 5 and "FAA" in bar


def test_markdown_renderer_sample():
    src = """# Title

Some **bold**, *ital*, `a<b` and [link](http://x.y) with <script>.

- one
  - nested
- two

1. first
2. second

| a | b |
|---|---|
| 1 | 2 |

```
code <x>
```

---
"""
    h = md.render(src)
    assert "<h1>Title</h1>" in h and "<strong>bold</strong>" in h and "<em>ital</em>" in h
    assert "<code>a&lt;b</code>" in h and '<a href="http://x.y">link</a>' in h
    assert "<script>" not in h and "&lt;script&gt;" in h
    assert "<ul><li>one<ul><li>nested</li></ul></li><li>two</li></ul>" in h
    assert "<ol><li>first</li><li>second</li></ol>" in h
    assert "<table><tr><th>a</th><th>b</th></tr><tr><td>1</td><td>2</td></tr></table>" in h
    assert "<pre><code>code &lt;x&gt;</code></pre>" in h and "<hr>" in h


@pytest.fixture()
def server(tmp_path, monkeypatch):
    root = _repo(tmp_path)
    (root / "docs/notes.md").write_text("# Hello\n", encoding="utf-8")
    (root / "docs/data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (root / "docs/secret.py").write_text("x = 1\n", encoding="utf-8")
    outside = tmp_path.parent / "outside_secret.json"
    outside.write_text("{}", encoding="utf-8")
    (root / "docs/link.json").symlink_to(outside)
    monkeypatch.setattr(fd, "ROOT", root)
    fd.Handler.cfg = {"gallery_refresh": 0}
    srv = ThreadingHTTPServer(("127.0.0.1", 0), fd.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _get(url):
    try:
        with urllib.request.urlopen(url) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, ""


def test_file_route_confinement_and_suffixes(server):
    assert _get(server + "/file?path=docs/notes.md")[0] == 200
    assert "<h1>Hello</h1>" in _get(server + "/file?path=docs/notes.md")[1]
    assert _get(server + "/file?path=docs/data.csv") == (200, "a,b\n1,2\n")
    for bad in ("docs/secret.py", "../outside_secret.json", "/etc/hosts", "docs/link.json", "docs/missing.md", "", "docs/%00.md"):
        assert _get(server + "/file?path=" + bad)[0] == 404, bad


def test_removed_routes_are_gone(server):
    for path in ("/compute", "/board", "/plot.png"):
        assert _get(server + path)[0] == 404, path


def test_pages_render_with_nav_and_missing_files(server):
    for path in ("/", "/results", "/paper"):
        code, body = _get(server + path)
        assert code == 200, path
        assert "What changed" in body and "ToDo" in body and "FAA" in body
    assert "not yet merged" in _get(server + "/paper")[1]                      # no sections in the temp repo


def test_decisions_parse_gives_status_and_owner_for_d1():
    decisions, _ = dp.parse((REPO / dp.REL).read_text(encoding="utf-8"))
    d1 = next(d for d in decisions if d["title"].startswith("D1 "))
    assert d1["status"] == "proposed" and d1["owner"] == "user"
    assert len(decisions) >= 8


def test_todo_rows_grouped_by_owner():
    rows = tp.parse((REPO / tp.REL).read_text(encoding="utf-8"))
    assert any(r["id"] == "T1" and r["owner"] == "user" for r in rows)
    assert {r["owner"] for r in rows} <= set(tp.OWNERS)
    body = tp.render_body("| id | owner | status | item | since | source |\n|---|---|---|---|---|---|\n"
                          "| T1 | user | open | a | 2026-11-17 | x |\n| T2 | CEO | open | b | 2026-11-17 | y |\n")
    assert body.index("T1") < body.index("T2")                                 # user group first
