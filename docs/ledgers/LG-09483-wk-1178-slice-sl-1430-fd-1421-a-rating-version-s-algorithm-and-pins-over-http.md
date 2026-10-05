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

### Task 5 (RL-1428's three texts) — MINT-ARTIFACT CORRECTION

RL-1428 lines 150 and 166 (T2 and T3), and line 143's text (T1), carry "RL-1428), FD-1421.)": the mint replaced the
working id "RL 9695 (working id)" with "RL-1428)" and left the closing ")" of the old parenthesis. The maintainer (by
delegation) ruled, in the `to-lead.md` entry headed `2026-10-05 22:44:21 BST — RL-1428's T-texts: the stray ")" is a MINT ARTIFACT; apply with it removed`, that the ONE stray ")" is removed
when the texts land: "(… <date>, RL-1428, FD-1421.)", with `<date>` the commit date (2026-10-05). Everything else is
byte for byte. RL-1428 itself stays unedited.

The three find strings each occurred once in `docs/specs/03-rating-engine.md` before the edit (a script asserted it).
After the edit, by `grep -cF` over that file: the stray form `RL-1428), FD-1421.)` **0**; `*(Amended 2026-10-05,
RL-1428, FD-1421.)*` **2** (T1 at §5.1's create row, T3 at FR-237); `*(Discharged 2026-10-05, RL-1428, FD-1421.)*` **1**
(T2 at §4.3's note).

### Task 2 — the typed request

`RatingVersionCreate` is added after `RatingVersion` in `model_schema/rating.py` with `_PIN_TYPES` (DP-3 (a)); exported in
`__init__.py`; `GENERATED_SHAPES` and `ONE_SIDED_SLUGS` each gain `rating-version-create`. **Slug narrowing:** `slug` is
`Slug` (as `RatingVersion.slug`), where the route-local class used `str`; a slug the old body took and the stored shape
refuses would already have failed `to_schema` on read, so the boundary now refuses what could never be read back.

**Step 4 red, recorded out of order.** The `ONE_SIDED_SLUGS` entry was written before the run, because gate-1 was held
(S7) and no run was allowed. When the slots freed, the entry was reverted and `uv run pytest -q backend/tests/test_contracts.py
-k one_sided` printed: `AssertionError: a schema present on exactly one side must declare that in ONE_SIDED_SLUGS (OQ-649
(b)): ['rating-version-create']`, `FAILED …::test_every_one_sided_slug_is_declared`, `1 failed, 153 deselected`. The entry
was restored; `generate-contracts.py` wrote `rating-version-create.schema.json` and `openapi/generated.json`;
`generate-contracts.py --check`: `46 generated contracts match the models`; `pytest -q backend/tests/test_contracts.py`:
`152 passed, 2 skipped`.

### Task 3 — the service and the route

Service takes `algorithm_ref`, `pins`, `model_reference_mode`; stores them; the audit `after` carries them. The FR-223
check runs when `algorithm_ref` resolves (DP-1 (a)), after `flush()` and before `audit.record` (it reads the stored row via
`to_schema`; the caller's unit of work rolls the row back on the 422). `MODEL_REFERENCE_MODE_INCONSISTENT` is appended to
`RATING_ERROR_CODES`, the only change to that set, as the corrected STOP (ii) allows. `03:929-936` is untouched. Route-local
`RatingVersionCreate` removed; the handler docstring now says the algorithm and pins are declared and the shape checked here.
`grep -rn RatingVersionCreate backend/src` prints the import and the handler annotation. Per Task 5, RL-1428's T1-T3 land in
this commit.

Green: `pytest -q backend/tests/test_rating_version_create_pins.py`: `14 passed`; `test_rating_versions.py`: `43 passed`;
`test_rating_version_compile.py`: `20 passed`. `ruff check` on the changed files is clean (one `I001` fixed; the new test file
formatted). FR-223's `03:109` is NOT edited: RL 9758 mints first as RL-1438 (maintainer by delegation, relayed by the lead),
then T1 is applied byte for byte from the minted record.
