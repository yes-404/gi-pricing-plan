---
id: LG-9483
family: ledger
title: WK-1178 slice SL-1430 — FD-1421, a Rating Version's algorithm and pins over HTTP (PL-1429), task ledger
status: active
created: 2026-10-05
owner: executor
tree: 52c153cd1dcf7eb8a716559216a30b245dd6a7e2
phase: P2
work: WK-1178
slice: SL-1430
plans: [PL-1429]
corrected_by: []
relates: [RL-1428, RL-1263, FD-1421, FD-1425, FR-237, FR-223, WK-1178]
---

# WK-1178 slice SL-1430 — FD-1421, a Rating Version's algorithm and pins over HTTP

Executed from `PL-1429` by `executor-sl1430` (Sonnet 5.5). Branch
`sl-1430-fd-1421-rating-version-algorithm-and-pins`, worktree `.claude/worktrees/sl-1430`, from `origin/main`
`52c153cd1dcf7eb8a716559216a30b245dd6a7e2` (#1220, the activation). This record is under working id LG 9483 and mints
later. The dispatch record is the lead's local file
`gi-pricing-plan.local/handover/DISPATCH-WK-1178-SL1430-2026-10-05.md`; it is not in the repository. Stamps are BST.

FD-1425 is OPEN (its wiring limb is SL-1436's). Nothing in this slice bears on an approval.

## Tasks

### Task 0 — preconditions

**Dispatch tree.** `52c153cd1dcf7eb8a716559216a30b245dd6a7e2`, author date `2026-10-05T22:40:59+01:00`.
`uv sync --all-packages` ran. Test database `gipricing_sl-1430_db8a5a62`, made with `docker exec gi-pricing-postgres-1
createdb -U gipricing -T gipricing …` and migrated with `alembic upgrade head`.

**Rows 0.1–0.11** re-run on that tree: all match. Line-number differences only: row 0.7's predicate prints
`rating_versions.py:110` and the two seed lines (`examples/fremtpl2/model.py:396`, `:397`); the plan expected `:113` too.
Row 0.10: the three find strings occur once each (`03:908`, `:436`, `:134`). Row 0.11:
`MODEL_REFERENCE_MODE_INCONSISTENT` is at `03:109` and `03:936` and in no code, so Task 3 Step 5 and Task 5 Step 3 apply.

**RL-1428 against its draft** (`RL-9695` at `614ad96b`, by `git diff` of the two blobs): id substitutions, the three
amendments the plan names, and the CR-838 correcting-record bullet. The T1–T3 find and replace strings are unchanged.
RL-1428 lines 150 and 166 carry `<date>` and an unbalanced ")" in "RL-1428), FD-1421.)". The lead sent it to the
maintainer (by delegation); **T-texts are not applied until the lead relays the ruling.**

**Trial merge-tree with S7** (Step 5): not yet run for real. A first run at an empty branch (equal to `origin/main`)
against `origin/sl-1391-…` (`386f4d54`) exited 1 on `docs/INDEX.md` only (S7's branch is behind main); `03` auto-merged.
The real trial waits for S7's pushed head and this slice's `03` edits.

### Task 1 — the tests, red first

Module `backend/tests/test_rating_version_create_pins.py`, as PL-1429 Task 1 Step 1 gives it. Literals checked against the
source before the run: `AuditEventRow.action`, `.entity_ref`, `.after` exist (`db/models.py:226-230`); the helpers
`_empty_pins`, `_run_compile_job`, `_minimal_algorithm`, `_headers`, `_table`, `valid_algorithm`, `_fitted_gbm` exist.
No literal was corrected.

Run at the dispatch tree, before any code change (`OMP_NUM_THREADS=1 nice -n 19 uv run pytest -q
backend/tests/test_rating_version_create_pins.py`): **13 failed, 1 passed**.

- Control passes: `test_a_version_created_without_algorithm_or_pins_is_refused_at_compile`.
- `test_the_create_body_is_the_model_schema_type`: `AttributeError: module 'model_schema' has no attribute 'RatingVersionCreate'`.
- `test_model_reference_mode_inconsistent_is_registered_and_owned`: `AssertionError: assert 'MODEL_REFERENCE_MODE_INCONSISTENT' in frozenset({…})`.
- The four `test_a_pin_of_another_type_is_refused[…]` cases and `test_an_algorithm_ref_of_another_type_is_refused`:
  `AssertionError: assert 'EXTRA_FORBIDDEN' == 'VALUE_ERROR'`.
- `test_a_mode_mismatch_is_refused_at_create`: `assert 'VALIDATION_FAILED' == 'MODEL_REFERENCE_MODE_INCONSISTENT'`.
- `test_a_version_created_with_its_algorithm_and_pins_compiles_over_http`, `test_an_unknown_algorithm_is_refused_at_compile`,
  `test_an_unapproved_model_pin_is_refused_at_compile_and_compiles_after_approval`,
  `test_a_peril_structure_pin_is_stored_and_compile_reports_no_resolver`,
  `test_the_creation_event_records_the_declared_pins`: `assert 422 == 201` on the create (a `VALIDATION_FAILED` 422 on
  `algorithm_ref` and `pins`).
