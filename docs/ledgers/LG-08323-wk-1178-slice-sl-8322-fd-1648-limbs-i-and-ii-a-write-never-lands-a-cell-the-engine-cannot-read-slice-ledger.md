---
id: LG-8323
family: ledger
title: WK-1178 slice SL-8322 — FD-1648 limbs (i) and (ii): a write never lands a cell the engine cannot read (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-05
owner: executor
tree: 880a22f9           # sl-8322-r1-rate-table-cells head this was written against (base a459d49a, tree 259f0b25)
slice: SL-8322
phase: P2
work: WK-1178
plans: [PL-8321]
corrected_by: []
relates: [FD-1648, FD-1767, FD-1780, FD-1781, PL-8321, FR-234, FR-214, FR-222, FR-261]
---

# LG-8323 — WK-1178 slice SL-8322 (R1): a write never lands a cell the engine cannot read

**GO:** to-lead "2026-11-05 10:41:08 GMT" (plan R revised @dbe20ec5 accepted, split into R1 and R2), amended by the lead's dated line of 10:43:54 GMT: the plan head is a459d49a, tree 259f0b25, no scope change.
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

`PL-8321`, R1 (SL 8322), items A1 to A11. Requirements: `03` FR-234 (spec text amended first), FR-214 (guard only), FR-222, FR-261. FD-1648 gains limbs (i) and (ii) and **stays open** (closes at R2); FD-1767, FD-1780, FD-1781 close at the audit. Limb (iii) and score-time behaviour are R2's and untouched here.

Write set: the plan's R1 write set, plus **one line** in `packages/pricing-core/tests/test_quote_input_raise_sites.py` (`_INPUT_FREE`), by the lead's OK of this date: the new compile-time raise site `_refuse_unparseable_cells` names the table ref, key values and stored cell text (configuration, no quote input), and the registry test fails without the entry.

### Task list

- **R1.0** spec text first (A2), commit `ca959718`, alone: FR-234 clause, `RATE_TABLE_CELL_UNPARSEABLE` in `03` §5.2.
- **R1.1** limb (i) (A4): red `7098ddc2`, green `ddec9ebc`.
- **R1.2** limb (ii) (A5): red `a1423996`, green `7fb22005` (with R1.3).
- **R1.3** compile backstop (A6): red `28b8c29d`, green `7fb22005`.
- **R1.4** goldens T8 (A7), **R1.5** FD-1767 guard T9 (A8), **R1.6** FD-1780 T10 (A9), **R1.7** FD-1781 T11 (A10): tests `68cb58df`, guard-type correction `55ec1bcd`, green `1f7338a9`, wrap `880a22f9`.

**Write paths verified by reading** (A5): import (`_checked_import`, operations.py), manual edit (`apply_cell_edits`), uplift, uplift by filter, floor and cap, rebase (all via `_validate_result`), and seed (`seed_from_model`). Every one ends in `validate_rate_table` and so in `_value_issue`, the one choke point. Rebase and seed write only computed fixed-point text (limb (i)), so no input reaches them that the new check could refuse: T3's refusal cases cover import, edit, uplift, uplift by filter and floor/cap; rebase and seed are covered by limb (i)'s tests, as the test docstring says.

**Departures and notes**
- T3 over the "seven paths": five carry refusal cases; rebase and seed cannot hold unreadable text after limb (i) (above).
- T9 (FD-1767 guard) declares `decimal`, not `relativity`/`percentage`: the compiler widens `int`/`count` only into `decimal` (`_WIDENING`); the first draft was refused at compile with `RATING_TYPE_MISMATCH` (commit `55ec1bcd`).
- T10: with two NaN the collision check now passes, and the model then refuses the NaN by name in the banding (`FactorResolutionError`, null band). A `Decimal('NaN')` reaching that fixture's banding panics inside the engine (`pyo3_runtime.PanicException`); that is a separate, pre-existing defect (score-time, R2's area), so T10 asserts the collision check on `float` NaN at `predict`, and `_same_value` itself on `float` and `Decimal`.
- Route-level tests (`backend/tests/test_api_rate_tables.py`: manual edit and import) are DB-lane: written, **not run here**; proved in the gate.
- A compile-time table with blob cells (no inline `rows`) is skipped by the backstop.

### Gate

(owed: the SOLO full gate, the lead's.)

Small runs, `run-small.sh`, tree = the worktree `sl-8322` at the commit named, load1 < 6:
- `ruff check .` rc 0; `mypy` "Success: no issues found in 252 source files" rc 0; `lint-imports` "Contracts: 4 kept, 0 broken." rc 0 (head 55ec1bcd + the edits of `1f7338a9`/`880a22f9`).
- test_rate_table_bulk_ops 84 passed; test_rate_table_operations 60 passed; test_rating_compile_fr240 28 passed; test_rating_column_collision 13 passed; test_testing 37 passed; test_rating_score_batch_outputs 55 passed; test_quote_input_raise_sites 19 passed.

### Audit

(the auditor's.)

### Build log

- **2026-11-05 10:46 GMT** branch `sl-8322-r1-rate-table-cells` from a459d49a; spec first (`ca959718`).
- **Red lines, by cause** (base = the commit before each fix):
  - T1/T2 at `7098ddc2`: `5 failed, 47 passed in 8.85s`; `AssertionError: ... {'relativity': '1E+2'} != {'relativity': '100'}`; likewise `'1E+3'` and `'1.36E-7'`.
  - T3 at `a1423996`: `15 failed, 67 passed in 3.60s`; each `Failed: DID NOT RAISE ValueError` (5 paths x 3 cells `1E+2`, `1.36E-7`, `.5`); the control cases `1.36e-7`, `1_000`, `5.` pass.
  - T4 at `28b8c29d`: `3 failed, 25 passed in 3.52s`; `Failed: DID NOT RAISE ValueError` for `1E+2`, `1.36E-7`, `.5`; controls pass.
  - T10 at `68cb58df`: `2 failed, 10 passed in 5.53s`; `AssertionError: assert 'MODEL_CALL_FEATURE_COLLISION' != 'MODEL_CALL_FEATURE_COLLISION'` (float and Decimal NaN).
  - T11 at `68cb58df`: `2 failed, 35 passed in 31.55s`; `TypeError: x` propagates (case property and monotone sweep).
- **Green lines:** T1/T2 `52 passed` (`ddec9ebc`); T3/T4 `82 passed` and `28 passed` (`7fb22005`); T10 `13 passed`, T11 `37 passed`, raise-sites `19 passed` (`1f7338a9` + one `_INPUT_FREE` line).
- **Guards, green at base:** T9 `55 passed` (it touches no changed path); T8's first test compares the old expression against the new on every non-exponent value of a 1 200-value seeded fixture.
- Logs: `~/gi-pricing-plan.local/scratch/sl-8322-r1/`.

## PRs

(none: the slice ends unpushed; the lead pushes.)
