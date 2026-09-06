---
id: PL-757
family: plan
kind: leaf
title: W32-10 — untested behaviour: execution ledger
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-10-untested-behaviour-ledger.md
---

# W32-10 — untested behaviour: execution ledger

What executing
[`PL-00758-untested-wk-692-behaviour-implementation-plan.md`](PL-00758-untested-wk-692-behaviour-implementation-plan.md) actually
did, on 2026-08-24, the day after the plan was written.

The plan is **not** edited to agree with this file — [`README.md`](README.md) has that rule.
Where the plan was wrong, this record says so and the correction lives here.

**Executed in an isolated worktree**, three tasks concurrently, against the shared compose
database. It is the first of the five closure slices and was run first for the reason the
[closure proposal](PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md) gives: it touches nothing the other four
touch, and it removes a false-evidence problem before more work is planned against the same
suite.

---

## Result

| | Before | After |
|---|---|---|
| Tests exercising **any** Alembic migration | 0 | **8** |
| Tests over the EBM predict route via HTTP | 1 (a 403) | **3** |
| Assertions that can distinguish the exposure share from the row-count share | 0 | **2** (both backends) |
| Deliberate-breakage proofs recorded | — | **8** |

No requirement id was allocated. Every marker names one that already existed.

---

## The finding that justified the slice, now demonstrated rather than argued

The plan's case was that `0.0 < wide.omitted.exposure_share < 0.5`
(`packages/pricing-core/tests/test_gbm.py:1847`) passes identically under the row-count
definition W32-5 replaced, so the requirement's whole content was untested. Task 3 mutated
`diagnostics.py:1055` back to the row-count definition and ran both tests together:

```
E       assert 0.0049504950495049506 == 0.009900990099009901 ± 9.9e-09
FAILED packages/pricing-core/tests/test_gbm.py::test_the_omitted_share_is_exposure_and_not_row_count[xgboost]
FAILED packages/pricing-core/tests/test_gbm.py::test_the_omitted_share_is_exposure_and_not_row_count[lightgbm]
================= 2 failed, 2 passed, 116 deselected in 5.15s ==================
```

The `2 passed` are the pre-existing assertion, **green against the bug it was written to
catch**. That is the evidence, and it is why this slice was not skippable.

---

## Task 1 — the dataset-owner backfill is exercised

`backend/tests/test_migration_dataset_owner.py`, 8 tests, all marked `FR-82`. **`8 passed
in 3.17s`.** The migration file itself is untouched.

Both shapes the plan asked for were built: five resolution and negative cases over a `pg_temp`
shadow `datasets` table running `_BACKFILL` verbatim — imported via `spec_from_file_location`,
never pasted — and the `nullable=False` refusal through **real alembic** against a per-test
scratch database (`CREATE DATABASE` on an AUTOCOMMIT engine, `GIP_DATABASE_URL` monkeypatched,
`command.upgrade` wrapped in `asyncio.to_thread` for `env.py`'s import-time `asyncio.run`). The
plan allowed the scratch database to be dropped as too costly; it was not, so **no §13 verdict
is owed against the refusal branch** — it is tested.

### Mutation proofs

| # | Mutation to the loaded SQL | Caught by | Verbatim |
|---|---|---|---|
| A | `\|\| '@%'` → `\|\| '%'` (widen) | `test_a_slug_that_prefixes_another_does_not_borrow_its_owner` | `AssertionError: assert UUID('01a032e1-…') is None` → `2 failed, 6 passed` |
| B | `AND a.action = 'dataset.created'` removed | `test_an_unfiltered_backfill_would_be_caught` | `AssertionError: assert UUID('01a032e2-…') is None` → `1 failed, 7 passed` |
| C | `ORDER BY a.sequence ASC` → `ORDER BY a.at ASC` | `test_the_earliest_creation_event_wins_by_sequence` | `AssertionError: assert UUID('01a032e3-196c-7c08-…') == UUID('01a032e3-196c-7d87-…')` → `1 failed, 7 passed` |
| D | `\|\| '@%'` → `\|\| '@1'` (narrow) | `test_any_version_in_the_ref_resolves` | `AssertionError: assert None == UUID('01a032e3-52e7-…')` → `3 failed, 5 passed` |
| E | the orphan dataset withdrawn from the refusal fixture | `test_an_unresolvable_dataset_stops_the_migration` | `Failed: DID NOT RAISE DBAPIError` → `1 failed, 7 deselected` |

C, D and E are beyond the plan's two required proofs. E matters on its own: it proves the
refusal is caused by the broken input rather than by the migration always raising.

### The plan's Step 3 claimed a proof it does not have

Step 3 says planting the two inconsistent `entity_ref` shapes proves "removing either one fails
here". **It does not.** `dataset:<uuid>@1` and `dataset:<slug>` are each excluded by the `LIKE`
independently, so mutation B leaves `test_the_inconsistent_refs_are_not_picked_up` green. The
test was kept — it pins both real-world ref shapes — with a docstring claiming only what it
proves, and the action filter was given its own seeding (a `dataset.archived` event at
`dataset:motor-ad@2`) inside `test_an_unfiltered_backfill_would_be_caught`, which is what makes
mutation B bite. **Verdict: the plan was wrong about the mechanism, the guard is real and is now
proven by a different test.**

### The migration's stale anchors, noted and not fixed

The comment at `82edffbe1dce_dataset_owner.py:27-36` cites three
`backend/src/app/platform/datasets.py` anchors that have all moved. The behaviour described is
unchanged; only the line numbers rotted, and a tests-only slice does not edit a merged
migration.

- `:191` → **`:205`** — `entity_ref=f"dataset:{slug}@1"` (`dataset.created`)
- `:868` → **`:951`** — `entity_ref=f"dataset:{dataset_id}@1"` (`dataset.subject_purged`, the id
  where the rest write the slug)
- `:271` → **`:293`** — `entity_ref=f"dataset:{slug}"` (`dataset.dictionary_updated`, no
  `@version`)

### `test_database_url` is collected as a test if imported under its own name

`from backend.tests.conftest_db import test_database_url` makes pytest collect it — it passes,
returning a `str`, with a `PytestReturnNotNoneWarning`. Imported aliased as `_test_database_url`.
Worth knowing before another module imports it at module scope.

---

## Task 2 — the EBM prediction route over HTTP

`backend/tests/test_prediction.py`, +76 lines, two tests added:
`test_an_ebm_scores_over_http` (`FR-180`, `FR-140`, `FR-193`) and
`test_the_ebm_refusal_reaches_the_client_by_name` (`FR-180`, `FR-193`). **`18 passed,
2 warnings in 25.29s`** over the whole file.

**No production defect.** The route carries the EBM's per-row numbers, `model_type == "ebm"`,
and the named refusal (`unavailable` / `model_type_has_no_interval`, `level` null, all bounds
null) to the wire.

### The plan's blocker did not exist — premise disproved, edit not made

The plan called a `blob_bucket` mismatch in `backend/tests/conftest.py`'s `api_settings` a
blocker to be fixed before Step 1. The edit was made, then tested by removing it again: **both
tests still pass, `2 passed in 9.04s`.** The reason is in the code the plan itself quotes —
`_score_ebm` (`backend/src/app/platform/prediction.py:429`) takes no `blob_store`, because an
EBM's fit result *is* its model (ADR-705). There is no artifact fetch on this arm, so the two
buckets never meet. `conftest.py` — a fixture shared by 16 test modules — was reverted to its
committed state.

### The plan's drafted test could not catch the failure its own docstring named

Test 1 as drafted compares the HTTP body against `service.predict_rows` called in the test body.
Both sides go through the same service, so **any mutation inside the service moves expected and
actual together and the `pytest.approx` comparison still passes** — including "returns the
intercept for every row", which the plan's docstring names as the thing this test must catch.

One line closes it, and it is that line rather than the approx comparison that the second
mutation trips:

```python
assert body["rows"][0]["expected"] != body["rows"][1]["expected"]
```

The approx comparison still earns its place — it proves route and service agree, which is what
HTTP adds — but it cannot stand alone.

### Mutation proofs

| # | Mutation | Verbatim |
|---|---|---|
| 1 | `prediction.py:160`, `elif isinstance(spec, EbmSpec):` → `… and False:` — dispatch falls to the GLM arm | `FAILED … test_an_ebm_scores_over_http - AssertionError` · `FAILED … test_the_ebm_refusal_reaches_the_client_by_name - AssertionError: {"type":"…/internal-error"…}` → `2 failed, 16 deselected` |
| 2 | `prediction.py:474`, EBM returns the intercept for every row | `E   assert 2.000000001299177 != 2.000000001299177` → `1 failed, 1 passed, 16 deselected` |

Mutation 1 terminates at `prediction.py:169, assert isinstance(fit, GlmFitResult)` and reaches
the client as a 500 `INTERNAL_ERROR`. Mutation 2 was added by execution, for the reason above.

---

## Task 3 — the partial-dependence share is exposure, not rows

`packages/pricing-core/tests/test_gbm.py`, +87 lines, no deletions. Three edits: `**over`
keyword forwarding on the `_diagnose` **test helper** (`:599`, the plan's one sanctioned
non-test change), the `_capped_book()` fixture (`:1827`), and
`test_the_omitted_share_is_exposure_and_not_row_count` (`:1897`) parametrised over both
backends, markers `FR-175` + `FR-181` stacked. **`FR-174` was not added**, per
the plan's explicit instruction.

The fixture is `heavy_a` 2 rows × 100.0, `heavy_b` 2 rows × 100.0, `common_light` 400 rows ×
0.01, with the exposure in `exposure_years` — the column `_spec` declares as its `log_column`
offset, which is what `_weights` reads first. The test asserts the exposure share
**`4.0 / 404.0 = 0.009900990099009901`** and explicitly rejects the row-count share
**`2 / 404 = 0.0049504950495049506`**. `omitted.levels == 1` under both definitions, so the
share is the only separator. A guard line asserts `_weights(spec, frame).sum() == approx(404.0)`
to catch a wrong exposure column, wrong values, or an undeclared offset.

Pre-implementation failure, confirming the helper gap the plan predicted:

```
E       TypeError: _diagnose() got an unexpected keyword argument 'max_partial_dependence_levels'
====================== 2 failed, 118 deselected in 3.37s =======================
```

Final: `4 passed, 116 deselected in 3.34s` for the new test and the pre-existing one together.

---

## An operational note for concurrent slices

`conftest_db`'s session-end `empty_the_database` raised a `DeadlockDetectedError` once, caused
by a concurrent agent's session holding locks on the shared database. **Teardown only, no test
affected, did not recur.** W32-6 avoided this by giving each concurrent slice its own database
(`gip_w32_6`); this slice did not, and the deadlock is the cost. Worth doing next time three
tasks share a worktree.
