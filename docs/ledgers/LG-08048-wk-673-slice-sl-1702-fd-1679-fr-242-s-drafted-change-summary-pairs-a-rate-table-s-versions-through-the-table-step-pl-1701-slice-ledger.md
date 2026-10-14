---
id: LG-8048
family: ledger
title: WK-673 slice SL-1702 — FD-1679, FR-242's drafted change summary pairs a rate table's versions through the table step and refuses no pin set (PL-1701), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-14
owner: executor
tree: 171d685260893d17947aa5638e74ade9c4e6d94c
phase: P2
work: WK-673
slice: SL-1702
plans: [PL-1701, PL-1677, PL-1267]
corrected_by: []
relates: [PL-1701, PL-1677, SL-1702, SL-1678, LG-1681, RL-1707, FD-1679, RL-1538, RL-1498, FR-242, FR-219, FR-231, FR-232, FR-237, FR-1399]
---

# LG-8048 — WK-673 slice SL-1702: the drafted change summary pairs rate tables through the `table` step

**GO:** the lead's relay, from-lead to `executor-sl1702`, "GO for SL-1702 (PL-1701), from the maintainer's to-lead '2026-10-14 13:32:07 BST'", build from `3ac63e35`, gate ALONE after SL-1695's, at load1 < 6 with all three locks, the demo `wf-699` with the frontend, pytest timeout 5400 s. The maintainer's entry itself is in `to-lead.md` (local, not in the repository); this record quotes the lead's relay of it, not the entry.
**MERGE-ACK:** not yet given.
**Audit:** not yet written; the auditor writes it.

## Tasks

### Scope

`docs/roadmap.md`, heading *"SL-1702 — WK-673 fix slice — RL-1707 / FD-1679: FR-242's drafted change summary pairs a rate table's versions through the `table` step that names them, and refuses no pin set"*, Work `WK-673`, plan `PL-1701` (a dated delta to `PL-1267`), ruling `RL-1707`. The row's body is not copied here; read it at that heading.

Requirements: `03` FR-242 (drafting limb: T1 and T2); FR-219, FR-231, FR-232, FR-237, FR-1399 read only. Discharges FD-1679's remaining limb, DP-P1. On the G2 path: merges before `SL-1543`.

Rulings in force, from `PL-1701`'s Decision points: DP-1 (a), DP-2 (a), DP-4 (a) and DP-5 (a), all ruled by the maintainer (by delegation), "2026-10-14 10:00:17 BST" (B). DP-5 (a) is set semantics: a ref listed twice is the ref once. The closing PR also sets `PL-1677` `closed` and carries FD-1679's register annotation: the maintainer (by delegation), to-lead "2026-10-14 12:02:46 BST" item (2), as `PL-1701`'s Task 5 quotes it.

### Task list

| Task | Plan step | Acceptance check | State |
|---|---|---|---|
| 0 | `PL-1701` Task 0 | LG scaffold, SL row `active`, plan `active` | done at `171d6852` (scaffold in this commit's successor) |
| 2 | `PL-1701` Task 2 | R1–R9, E8, U1, U2 red on the base by their causes | done at `65daf404`, re-run at `3ac63e35` (Build log) |
| 1 | `PL-1701` Task 1 | T1 and T2 verbatim | done at `af96ea6f`, checked by script (Build log) |
| 3 | `PL-1701` Task 3 | pairing, shape, guard removed; both files green; broken-input proof | code at `d87770c4`; green runs and proof are the gate window's (Gate) |
| 4 | `PL-1701` Task 4 | generated contract | `1ed595d5`; frontend client and type-check at the gate |
| 5 | `PL-1701` Task 5 | gate, closing acts | pending |

**Renamed tests (DP-2 (a)), old → new.** SL-1678's three functions were already flipped and renamed in the prep commit `65daf404`; the old names and old asserts are in `LG-1681`'s Task list. The prep file defines `test_r3_a_candidate_adding_a_second_version_names_it_alone` (parametrized `two_then_one` / `one_then_two`), `test_r3_a_candidate_dropping_one_of_two_baseline_versions_names_it_alone`; `_assert_refused` is deleted.

### Gate

Not yet run. The gate runs ALONE in the lead's gate-1 window; its first step, step 0, is the broken-input proof (below), then the full two-half gate on `origin/main...HEAD`. The rc table goes here.

**Broken-input proof (`PL-1701` Task 3 Step 6), step 0 of the gate script.** In `pair_rate_tables`, replace `if previous is not None:` by `if False:`; run both test files; R1, R2, R5 and R6 must FAIL and E1 must PASS; restore; run again green; the tree is clean before the full gate. Both runs are recorded below once made.

(not yet run)

### Audit

Not yet written.

### Build log

- **2026-10-14, prep (`65daf404`, re-pointed at `3ac63e35`).** Worktree `.claude/worktrees/sl-1702`, branch `sl-8003-wk673-dpp1-fix`. `git merge-tree --write-tree origin/main HEAD` rc 0; `origin/main` merged (`50d95b2c`). `RL-9996` → `RL-1707` in the two test files (4 occurrences). Reds run on the base through `run-small.sh`, one file per call, against the per-worktree database `gipricing_sl-1702_8a302640`, created with `createdb -T gipricing` and `alembic upgrade head` (disclosed to the maintainer by the lead; its keep-or-drop ruling is the lead's):
  - route file: 11 failed, 10 passed. R1, R2, R3 (three cases), R4, R5, R8, R9: `assert 409 == 200`, the detail naming FD-1679 (R8 and R9: "at versions 1 and 1"). R6: `assert 1 == 2` on the length. R7: `assert [None, None] == ['t', 't']`. E8, E1 and the first-version test pass.
  - draft file: U1 and U2 fail with `ValidationError` on `RateTableChange.step_id`, `Extra inputs are not permitted`, at `test_change_summary_draft.py:149` and `:166`.
- **2026-10-14, Task 1 (`af96ea6f`).** T1 and T2 applied with `<date>` = 2026-10-14, `<RL>` = RL-1707, `<SL>` = SL-1702. Checked by script against the whitespace-normalised blockquotes of `RL-1707` §"DP-T": both are found verbatim in `03-rating-engine.md`.
- **2026-10-14, Task 3 (`d87770c4`).** `pair_rate_tables`, `_table_refs`, `_entry_order` in `change_summary.py`; `RateTableChange.step_id`; `_rate_table_pins` replaces `_pins_by_slug`; the docstring sentence replaced. Premises read for this edit at `3ac63e35`: a–d, f, g, h (the code replaced); i, j, k–q not re-read. `git grep -n FD-1679 -- backend/src` prints nothing. A first `ruff format` run over `backend/src` and `packages` reformatted 86 files; all were reverted with `git checkout` before any commit, and the edits re-applied.
- **2026-10-14, Task 4 (`1ed595d5`).** `scripts/generate-contracts.py` wrote `docs/contracts/openapi/generated.json` only: two hunks in `RateTableChange`, the `step_id` property (`anyOf` string / null, not in `required`) and the description text.
- **2026-10-14, activation (`171d6852`).** SL-1702 row and `PL-1701` `active`.

## PRs

Not yet opened.
