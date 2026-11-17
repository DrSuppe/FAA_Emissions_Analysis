# Spec: FAA project dashboard (architect, 2026-11-17)

## Goal
http://127.0.0.1:8771/ is the one place the user looks for this project: what changed, the paper drafts, the
diff between the user's live Overleaf paper and the agent's ideal version, open decisions, and the task list.
A port of the LNG dashboard (source of truth: the running copy in
`/Users/timkayser/Documents/ProgrammSupport/PyCharm/EMISSIONS/LNG/.claude/worktrees/gui-iteration/scripts/`,
branch feat/gui-iteration @ e19d975). Same look, same file formats, so the two projects feel identical.

## Scope (five tabs now; the rest later)
| Tab | Route | Source module (LNG) | Reads |
|---|---|---|---|
| What changed | `/` | dashboard_changes.py | `docs/dashboard/changes.yaml`, `docs/findings.md` |
| Paper | `/paper` | fit_dashboard.paper_page | `docs/paper_sections/*.md` |
| Paper diff | `/paper-diff` | paper_diff.py | `papers/FAA_emissions_paper` (clone, read-only, `origin/main`) vs `docs/paper_ideal/main.tex`; checks in `docs/paper_ideal/checks.json` |
| Decisions | `/decisions` | decisions_page.py | `docs/paper_tracking/decisions.md` |
| ToDo | `/todo` | todo_page.py | `docs/paper_tracking/todo.md` |

Dropped for now (not ported): Compute, Results gallery tab, Board (science board), `/plot.png`, the running
strip (`dashboard_running.py`, `watch_fits.py`), `compute_control.sh`. `results_gallery.py` is ported only as a
library because `dashboard_changes` imports `load_findings`, `lead_sentence`, `nav_bar`; its `/results` route
and `/img` stay available (harmless) but the tab is hidden until a results folder exists.

## Contracts and invariants
1. Stdlib + PyYAML only; no matplotlib import (the plot route is gone). Server binds 127.0.0.1 only.
2. `ROOT = Path(__file__).resolve().parents[1]` everywhere. Every `MAIN_CHECKOUT` constant becomes
   `/Users/timkayser/Documents/ProgrammSupport/PyCharm/EMISSIONS/FAA/FAA_Emissions_Analysis` (the
   worktree-vs-main fallback logic stays as in LNG).
3. `PAPER_REPO = ROOT / "papers/FAA_emissions_paper"`. The paper repo is only ever fetched and read, never
   written, never pushed. The user edits the paper in Overleaf; the agent's version lives in
   `docs/paper_ideal/` in this repo.
4. `/file` and `/img` confine paths to the repo (same tests as LNG).
5. Default port 8771 (LNG keeps 8770). Title prefix "FAA".
6. File formats unchanged from LNG: changes.yaml fields, decisions.md `## Dn title` blocks with
   `status/owner/blocks/options/recommendation` lines, todo.md pipe table, findings.md pipe table.
7. Nothing in `scripts/` imports from the LNG tree; the port is a copy, not a path reference.

## File layout (this repo)
`scripts/fit_dashboard.py`, `scripts/dashboard_changes.py`, `scripts/dashboard_md.py`, `scripts/decisions_page.py`,
`scripts/todo_page.py`, `scripts/paper_diff.py`, `scripts/results_gallery.py` (library), `tests/test_dashboard.py`,
`docs/dashboard/changes.yaml`, `docs/findings.md`, `docs/paper_tracking/{decisions,todo}.md`, `docs/paper_ideal/`,
`docs/paper_sections/`, `papers/FAA_emissions_paper` (git-ignored clone), `coordination/` (git-ignored).

## Acceptance
- `python3 scripts/fit_dashboard.py --port 8771` serves all five tabs with HTTP 200 and the FAA content
  (the three seed cards, D1-D8, T1-T9, the ideal main.tex diff against origin/main with zero hunks on day one).
- `pytest tests/test_dashboard.py` passes: cards sorted and rendered; a findings row without a card gets an auto
  card; markdown renderer on headings/list/table/code; `/file` refuses paths outside the repo; decisions parse
  gives status/owner; todo rows grouped by owner.
- `grep -rn LNG scripts/` returns nothing except the provenance comment at the top of each ported file.
- README gains a "Dashboard" section: start command, port, what each tab reads, restart procedure.

## Open decisions
None for the port. Science board and compute pages: added when results exist (user 2026-11-17).

## Roles for this project (architect's recommendation, 2026-11-17)
Light: the architect (this session) owns the spec, decisions, paper text in `docs/paper_ideal/`, and merges.
Coders and a verifier are spawned per unit of work. No standing CTO session until model calibration runs
start producing a compute queue; revisit then.
