---
id: PL-8342
family: plan
kind: map
title: WK-1178 — one stdlib table-row parser, so an escaped pipe no longer hides a declared endpoint or stops the phase report (FD-1484), SL-8343 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8342
owner: planner
tree: dae9637ea6f6a56f6502e9db70392cdfb2f3983d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1484, CR-823, RL-982]
---

# PL-8342 — WK-1178: one table-row parser (SL 8343, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds one slice row, SL 8343, and edits no filed plan.
> The executor's skills are `superpowers:test-driven-development`, `.claude/skills/python-test`,
> `.claude/skills/python-package`, `.claude/skills/docs-audit` and `git-hygiene`. PL 8342, SL 8343 and
> LG 8344 are working ids reserved by the lead.

## Authority

- **The user's decision.** The maintainer's entry "2026-11-05 09:58:58 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`: "AND FD-1484 (8 h) are coded and merged before Thu 12 —
  the two are no longer carried". This **replaces** item (8) of "2026-11-05 09:51:53 GMT" on the carry.
  That item's other limb stands and is not this plan's: "a dated line on each essay records the carrier
  as closed-unmerged".
- **The route, closed, verbatim** (the essay's *Acceptance*, on "2026-09-30 11:49:44 BST"): "a stdlib-only
  `packages/model-schema/src/model_schema/table_rows.py`, the one source of the row-splitting logic,
  modelled on `register-lint.py`'s `_split_row`. The scripts load it by path via `importlib`; the backend
  (`guide.py`) imports it normally; `docs.yml` is unchanged."; "**every idiom migrates to it**"; "**'Never a
  fourth' means the row-splitting logic**, not a count of regexes".
- **The test that holds the route:** "a test fails if `table_rows.py` imports anything outside the stdlib:
  an AST walk … **red first on a planted `import pydantic`** … The docs gate itself is proven by running
  `audit-docs.py` under a bare `python3` with no project packages".
- **The dead carrier.** The essay's owner was #977's slice. #977 is closed unmerged (triage §3), so this
  plan is the carrier.
- **The timing.** The essay: the `--phase P2` fix "lands before the P2 exit review". The §14 review is Mon
  16–Tue 17 Nov 2026 and the demo Wed 18 Nov.
- **The triage** (`b28ba8e9454c`) §3, Slice T.

## Goal

A table cell holding `\|` is read as one cell, by one parser, everywhere. The three hidden routes become
visible to `scope-audit`, `audit-docs` and the demo guide, and `doc-index.py --phase P2` runs. FD-1484
closes.

## Evidence at `dae9637e`

Cites were read at `origin/main` `dae9637ea6f6a56f6502e9db70392cdfb2f3983d`. **Items marked RUN were run
by the planner**, read-only (`/tmp/plan-slices/p6.py`; `doc-index.py` through the gate-2 flock).

- **The red is live (RUN).** `python3 scripts/doc-index.py --phase P2`: `ValueError: findings/register.md:
  parsed 352 of 362 data row(s) — coverage mismatch (RL-982 acceptance item 2)`. `declared_endpoints("DATA")`
  39, `("GOV")` 23: the essay's "to 40" and "to 25" are the targets at this tree. The three cut cells
  (RUN): `01-data-management.md:878`, `06-governance.md:610`, `:614`, each captured up to `\`, and each
  has moved since the essay.
- **The one logic that is right:** `scripts/register-lint.py:165-170` `_split_row`, placeholder form, and
  `:126` `_UNESCAPED_PIPE`. `doc-index.py:477` has its own `_UNESCAPED_PIPE`, and `:1061` is the plain split
  that raises.
- **Every site, at this tree** (`git grep -n -E '\.split\("\|"\)|\.split\(.\|.\)|\(\?<!\\\\\)\\\|' origin/main --
  scripts backend/src packages tests backend/tests`, and `git grep -n -E '\(\[\^\|\]\+\)'`):

| Site | Form | Reads |
|---|---|---|
| `scripts/scope-audit.py:68`, `scripts/audit-docs.py:299`, `backend/src/app/demo/guide.py:64` | the `([^\|]+)` regex | a §5.1 row |
| `backend/src/app/demo/guide.py:87` | plain split | a table |
| `scripts/audit-docs.py:353`, `:394`, `:578`, `:4153` | plain split | tables |
| `scripts/audit-docs.py:636`, `:642` | lookbehind: a **count** and an offender search | the cell-count check |
| `scripts/_docid.py:1611` | plain split | a table |
| `scripts/doc-index.py:477`, `:1061` | regex; plain split | the register |
| `scripts/register-lint.py:126`, `:165-170` | the model | the register |
| `tests/test_audit_docs_ids.py:2451`, `:2500` | lookbehind split | tests |
| `tests/test_findings_ids.py:157`, `tests/test_permission_parity.py:62`, `backend/tests/test_contracts.py:263` | plain split | tests |

  **Fifteen script and source sites, three of which are duplicates by a stated choice** (`audit-docs.py:295-298`,
  `guide.py:60-63`, whose comments must go), and five test sites.
- **`audit-docs.py:636-642` is not a splitter of cells to read.** It *enforces* that a pipe inside a code
  span is escaped. It counts separators, and it is the check that makes `\|` the convention. It moves to the
  shared pattern, not to a behaviour change.
- **The bare-`python3` gate.** `.github/workflows/docs.yml:68,76,80` run the scripts under a plain `python3`.
  `model_schema/__init__.py` imports pydantic, so `import model_schema.table_rows` fails there: hence the
  ruled load-by-path.
- **`docs.yml`'s `paths` (`:16-18`) do not name `packages/model-schema/…/table_rows.py`.** The ruling says
  `docs.yml` is unchanged. So an edit to `table_rows.py` alone fires `python`, whose suite holds the
  `test_audit_docs_*` files, and not `docs`. Named in Hand-off, not changed.
- **Three routes will surface.** Rows that no checker ever read now reach `audit-docs`'s endpoint checks and
  `req-coverage`-adjacent figures. `dossiers` and `dependencies` were unpublished at the essay's tree
  (`[False, False]`), `lineage` published. **A new red in `audit-docs` after migration is the finding working,
  not a slice defect**, and R3 says what to do with it.
- **Spec rows.** 32 rows in `docs/specs/` hold `\|` (RUN), against the essay's 28.

## Decision points

**Both ruled** (the entry "2026-11-05 10:36:35 GMT"): DP-P1 (a), row by row; DP-P2 (a); the Wed 12:00 fallback is R3 alone. That
entry also says "T folded": T's commits ride this branch and this gate (PL 8330). The table is kept as the record.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-P1 | A newly visible route fails a check (declared, unbuilt, out of phase). What then? | (a) **Stop and report each with its check line;** the lead rules, row by row, as a spec correction or a dated exception, in this slice's PR. (b) Exempt them in the checker to keep the migration green. A check that hides a declared route is this finding again. | **(a).** |
| DP-P2 | What does `split_row` return for an escaped pipe: `\|` as written, or a bare pipe? | (a) **`\|`, as `_split_row` does:** the ruled model, and the register's byte-compare behaviour stays. A caller wanting display text unescapes. (b) A bare pipe. Cleaner for a reader; changes every register comparison. | **(a).** |

The route is ruled. DP-P1's (a) is what the essay's "a false completeness figure" implies; it is a DP only
because its outcome may need the maintainer. **The fallback** for the Wed 12:00 line: R3 alone (`doc-index.py`
on the shared logic) discharges the `--phase P2` limb in about 1 h, as the triage notes.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's merge tree.
Items 1 and 2 apply to this plan; A1 to A11 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing line
   except check 31 / check 32 lines naming working ids 8342, 8343 or 8344. After the mint, `audit-docs.py` and
   `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no line that
   stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only the Write set below. `.github/`
  is not in it.
- **A2. Red first, by cause.** LG 8344 quotes, from the slice's named base: `parsed 352 of 362` (or the count
  at the base, named); `declared_endpoints` 39 and 23; the demo guide's declared count; and T1 to T4's reds.
- **A3. The parser.** T1: a table of rows, escaped pipe in the first, middle and last cell, a code span, an
  empty cell, no trailing pipe: cells as `_split_row` gives them.
- **A4. Stdlib only.** T2: the AST walk over `table_rows.py` against `sys.stdlib_module_names`, **red on a
  planted `import pydantic`**, the plant quoted in the LG and not committed.
- **A5. The bare gate.** In a clean environment, `env -i PATH=/usr/bin:/bin python3 -I scripts/audit-docs.py`
  reaches the script's checks with no `ModuleNotFoundError`, quoted. Same for `doc-index.py --check`,
  `doc-id.py check` and `scope-audit.py`. A count that fails only on working ids is not a failure of this item.
- **A6. One logic.** `git grep -n -E '\.split\(.\|.\)|\(\[\^\|\]\+\)|\(\?<!\\\\\)\\\|' -- scripts backend/src
  packages tests backend/tests` prints only `table_rows.py` and its tests, each other hit named in the LG
  with why (A6's exception list is expected to be empty). `register-lint.py`'s `_split_row` delegates.
- **A7. The figures.** `declared_endpoints("DATA")` 40, `("GOV")` 25; GOV published unchanged at this
  tree's number; the demo guide's declared count up by three, the "63 of 148" line of `CR-718` being a frozen
  record that is not edited; `python3 scripts/doc-index.py --phase P2` rc 0 with the coverage assertion
  intact (362 of 362, or the count at the head).
- **A8. Nothing else moved.** `python3 scripts/doc-index.py` at the head regenerates `docs/INDEX.md` with a diff
  limited to this slice's ids; `register-lint.py` and `register-owed.py review` print the same rows as at
  base, the LG quoting both.
- **A9. The surfaced routes,** as DP-P1 rules, each row listed.
- **A10. The GREEN set and the gate.** `guide.py` and every script's tests by import closure (common seat brief,
  item 29), commands and list in the LG; the 8 docs-audit pytest files among them. **The full code gate, both
  halves, SOLO**, green at the re-merged head, every rc quoted. `generate-contracts.py --check` rc 0.
- **A11. FD closing act in the FD-1842 form, in the slice's own PR, by the slice's auditor:** FD-1484's `status:
  closed`, `relates:` gaining the slice's ids, a `***Resolved <date>***` paragraph naming the delivered remedy,
  its reds, its LG, the secondary instance and the figures, the same on the register row, and the PR number and
  squash at the merge's date of record. **The LG Audit section, with the lead's adoption, lands in the audit's
  own commit**, and `docs/INDEX.md` is regenerated after the closing acts (common seat brief, item 17).

## Global Constraints

- **G1. `table_rows.py` is stdlib-only and imports nothing from `model_schema`.** It lives in that package by
  ruling, and `model_schema/__init__.py` does not import it.
- **G2. Load by path, once per script,** by one small helper or each script's existing loader pattern
  (`register-owed.py` loads `register-lint.py` this way). A script does not import `model_schema`.
- **G3. `docs.yml` is unchanged** (ruled).
- **G4. No behaviour change but the fix.** A row with no escaped pipe parses exactly as before, proven by A8.
- **G5. Frozen records are not edited.** `CR-718`, `CR-823` and filed plans stand. Spec text is unchanged unless
  DP-P1 rules a row.
- **G6. Red first, by cause. No test is removed or weakened** (common seat brief, item 13). A test's splitter
  moving to the shared one keeps its asserts.

## Needs

No DB, no Redis, no docker, nothing on the NFR VM. `audit-docs.py`, `doc-index.py`, `register-lint.py` through the
gate-2 flock or `run-heavy.sh --light`. Tests by `run-small.sh`, at most three files a call. `guide.py`'s test is
DB-free if its fixture is; else the gate proves it.

## Tasks

### SL 8343 — one row parser

**The row.** Last-2 in the 09:58:58 order. WK-1178. One `sonnet` executor. Requirements: none by id: tooling; the
figures it corrects are §13 evidence. Register: FD-1484 (MEDIUM), closing at the merge (A11). Depends on: the GO; a gate slot. **Size:** 8 h. SOLO gate about 2.5 h, not counted. Merged before Thu 12 Nov 2026;
still red at Wed 11 Nov 12:00 → the exception list, with the fallback's 1 h limb still landing before the exit
review.

**R1 — the module, red first.** `packages/model-schema/tests/test_table_rows.py`:

- **T1** `test_split_row_keeps_an_escaped_pipe_inside_its_cell`, A3's table.
- **T2** `test_table_rows_imports_only_the_stdlib`.
- **T3** `test_a_script_loads_it_by_path_with_no_project_packages`: `subprocess` under `sys.executable -I -S` with
  a small program that loads the file by path and calls `split_row`.

**Green:** `packages/model-schema/src/model_schema/table_rows.py`:

```python
"""One table row, split (FD-1484). Stdlib only: `scripts/` load this file by path, under a bare
`python3` with no project packages, so it imports nothing from `model_schema` or beyond."""

from __future__ import annotations

import re
from typing import Final

__all__ = ["UNESCAPED_PIPE", "cell_count", "is_table_row", "split_row"]

#: A pipe that separates cells: not the `\|` markdown uses for a pipe inside one.
UNESCAPED_PIPE: Final = re.compile(r"(?<!\\)\|")


def split_row(line: str) -> list[str]:
    """Cells of a markdown table row, stripped, an escaped `\\|` kept as written."""
    return [cell.strip() for cell in UNESCAPED_PIPE.split(line.strip().strip("|"))]


def cell_count(line: str) -> int:
    """The separators' count less one, as `audit-docs.py`'s cell-count check reads it."""
    return len(UNESCAPED_PIPE.findall(line)) - 1
```

**This regex form loses a trailing `\|`** (RUN: `| a | b\|c | d\|` gives `['a', 'b\\|c', 'd\\']`, because
`strip("|")` eats that pipe), so T1's trailing case is red on it, and the delivered body takes `_split_row`'s
placeholder form, as ruled. The sketch above shows the intent, not the final body.
`is_table_row` is whatever the three regexes' prefix needs, once.

**R2 — the three copies.** `scope-audit.py:68`, `audit-docs.py:299`, `guide.py:64`: a helper in `table_rows.py`,
`endpoint_row(line) -> tuple[str, str] | None`, the method cell and the path cell, from `split_row`. `guide.py`
imports it normally; the comment at `:60-63` goes, as does `audit-docs.py:295-298`'s. **T4**, `tests/`: the three
rows at `01:878`, `06:610`, `:614` each yield their full path through `declared_endpoints`, by `req`-free test.
**Red:** the cut cell.

**R3 — `doc-index.py`.** `:477`, `:1061` on the shared logic. A7's `--phase P2`. If the slice must be cut, this
commit alone is the fallback.

**R4 — the rest.** `register-lint.py` (`_split_row` and `_UNESCAPED_PIPE` delegate, keeping their names for its
importers), `audit-docs.py:353,394,578,636,642,4153`, `_docid.py:1611`, `guide.py:87`, and the five test sites, one
commit each family. Run the docs checks after each.

**R5 — the surfaced routes.** `audit-docs.py` at the head; A9 under DP-P1. **G.** Full code gate, both halves, SOLO.
CI from the three-dot diff: `python`, `docs`, `history-policy`.

### Write set

- `packages/model-schema/src/model_schema/table_rows.py` (new), `packages/model-schema/tests/test_table_rows.py`
  (new).
- `scripts/audit-docs.py`, `scripts/scope-audit.py`, `scripts/doc-index.py`, `scripts/register-lint.py`,
  `scripts/_docid.py`, `backend/src/app/demo/guide.py`.
- `tests/test_audit_docs_ids.py`, `tests/test_findings_ids.py`, `tests/test_permission_parity.py`,
  `backend/tests/test_contracts.py`, one new test under `tests/` (T4).
- Any spec row DP-P1 rules.
- LG 8344 under `docs/ledgers/`.
- At the mint: the SL 8343 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, FD-1484's essay and
  `docs/findings/register.md` (A11).

### Files shared with other groups

**T:** `register-owed.py` reads `register_lint.parse_register`; T edits `register-owed.py` only, and this slice
`register-lint.py`. No textual collision. **T is folded here** (10:36:35): this branch carries PL 8330's commits and one gate covers both. **C:**
`backend/tests/test_contracts.py` is read by C's contract change, one line here. **H:** `tests/` different files.
**Every plan's mint touches `docs/INDEX.md`**, which `doc-index.py` regenerates: re-merge after R3 changes nothing
in its output by A8. **Serial with nobody for building; the gate is serial, last.**

## Hand-off (not this plan's writes)

- The GO: the maintainer. The gate slot, the row and the mint: the lead. The LG: the executor. A11:
  the auditor.
- **The dated lines of 09:51:53 (8)**, recording #977 and #982 as closed unmerged on FD-1484's and FD-1338's essays,
  are the docs batch's, not this slice's; A11's paragraph must not contradict them.
- **FD-1482's register tail** names "the WK-1178 slice that carries RL-1483", and #977 was that carrier too (triage,
  "out of scope"). It is not in this plan.
- **For a later record:** `docs.yml`'s paths omit `table_rows.py` (Evidence), by a ruling that predates the file.

## Self-review

1. **Every cite was read** at `dae9637e`; the marked items were run. 2. **Requirement ids:** none apply; no range.
3. **Placeholders:** `is_table_row` is defined by the three regexes it replaces. `split_row`'s final body is the
ruled placeholder form. 4. **The red is by cause.** 5. **The route is carried verbatim;** only
two genuine choices are DPs. 6. **The essay's figures are re-read:** 39 and 23 hold; the rows moved. 7. **Calendar:**
12 Nov 2026 is a Thursday, 11 Nov a Wednesday.
