---
id: LG-8369
family: ledger
title: SL-8368 — POST /api/v1/models/{id}/archive requires model:fit, not model:submit (FD-8366)
status: active
created: 2026-11-05
owner: executor
tree: e760450ec280c0ba5b84e91cb6c130d5419e0f95
phase: P2
work: WK-1178
slice: SL-8368
plans: []
corrected_by: []
relates: [FD-8366]
---

# LG-8369 — SL-8368: archive requires `model:fit`, not `model:submit`

**GO:** the lead's ruling "2026-11-05 14:05:07 GMT" (option (a), conditional): fix = the permission and its test; red first; the state guard proven on an `approved` model; a dated line on `02` §5.1's archive row. Brief of record sha256 prefix `d7521045e7d7`.
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

`06` §4.1 (DP-A): `model:fit` is the Model write right; `model:submit` is "submitting a Model … for approval". The route `POST /api/v1/models/{id}/archive` (`backend/src/app/api/models.py` `archive_model`) and `backend/src/app/platform/modelling.py` `archive` both checked `model:submit`. Requirement: FR-202 (lifecycle; the archive edge is `draft | fitted | superseded → archived`). `SubmitModels` and `submit_for_review`'s check (modelling.py, the other `Permission.MODEL_SUBMIT`) are unchanged.

Who gains and loses (`model_schema/permissions.py` `BUILTIN_ROLES`): `analyst` (fit, no submit) GAINS archive; `pricing_actuary` (both) unchanged; no built-in role LOSES it. Only a stored custom role with `model:submit` and without `model:fit` would lose it; none is seeded. No spec row or test relied on the loss.

Existing fixtures: `test_model_lifecycle.py` and `test_model_nfrs.py` call `service.archive` with principals holding `analyst` + `pricing_actuary`, which hold `model:fit`; none was changed.

### Task list

1. Red first (commit 69d391f9, then 15993936 and a528160b): three tests in `backend/tests/test_api_model_lifecycle.py`, on the real route.
2. The two edits (commit fc1566c7): `caller: FitModels` on `archive_model`; `Permission.MODEL_FIT` in `archive`; docstring line in `archive`; the dated line on `02` §5.1's archive row.
3. Test fix (commit e760450e): the superseded case carries that version's `If-Match` (see Build log).

### Gate

Not run by the executor (the gate is the lead's). Targeted runs only, in the granted DB window, `-k archiv` on `backend/tests/test_api_model_lifecycle.py`; see the Build log. Not run: `test_model_lifecycle.py` (service-level archive tests, DB-backed) and the rest of the file; `audit-docs`, `req-coverage`, `generate-contracts --check` (the `archive_model` docstring was left untouched on purpose, since route docstrings feed the generated OpenAPI).

### Audit

(The auditor's. A requested dated note on FD-8366: the superseded trace, by citation: new compiles refuse a `superseded` pin (`pricing_core/rating/compile.py` `_APPROVED_OR_BETTER`, `PIN_NOT_APPROVED` at the peril-component check and the algorithm pin check); a compiled Bundle carries the model inline and a deployment binds the Bundle hash (`platform/rating_versions.py` model resolver; `platform/deployments.py` `_approved_compiled_version`); archive changes `status` only, so the row still resolves; `/predict` refuses an archived model (`SCOREABLE_MODEL_STATUSES`). The deployment path was read by citation, not proven by a test.)

### Build log

- 2026-11-05 15:47–15:50 UTC, window "gate D, stage pytest", head a528160b (tests only, permission still `model:submit`), `-k archiv`: `3 failed, 1 passed, 8 deselected in 55.45s`, rc=1. FAILED: `test_archiving_requires_model_fit_and_not_model_submit`, `test_an_approved_model_is_refused_archive_by_state_not_permission[permissions0]` (fit only), `test_a_superseded_model_is_archived_by_a_fit_holder`. Passed: the both-permissions approved case (409 already, on main). The captured log of the last failure reads `permission denied … "permission":"model:submit"` then `403`. The red summary was tailed to 40 lines, so the first two failures' assert lines are not quoted.
- 2026-11-05 15:50:47–15:53:31 UTC, head fc1566c7 (permission edit): `1 failed, 3 passed, 8 deselected in 20.13s`, rc=1. The superseded test got `409` on `/archive`: its `If-Match` came from `GET /models/{slug}` (the latest version, v2) while the archived row is v1, a stale write. A defect in the test, not the code; it also masked the superseded case in the red run, whose 403 came from the permission.
- 2026-11-05 15:53:42–15:54:22 UTC, head e760450e (test passes `?version=`): `4 passed, 8 deselected in 22.03s`, rc=0.
- Window ends (both runs): template guard `alembic_version=1 environments=3 tenant_marker=1` at start and end; `-n 11 dbsize` 0 at start and end; `-n 0 dbsize` 56 at start and end; `gipricing_sl8368_win` rows 0 and `gipricing_sld_gate` rows 1 at END. The red run set no `GIP_GATE_SLOT` (the lead read `PUBSUB CHANNELS` empty, to-lead 15:49:09); both green runs set `GIP_GATE_SLOT=/tmp/slots/window-8368` on the inner command. Scripts: `~/gi-pricing-plan.local/scratch/sl8368/win.sh`.
- The superseded state is reached through `_supersede_earlier_versions` by approving the model and then a next version, but `_next_version_of` inserts that second version row (it is not refitted).
- `ruff check` on the test file: rc=0. `ruff format --check`: the file was not format-clean on main (about 14 older hunks); only my hunks were hand-formatted. `mypy` on the single test file reports errors of the same kind on lines that predate this slice.
- 2026-11-05 17:26 UTC, audit fix (to-lead "2026-11-05 17:20:43 GMT"): added `test_a_model_in_review_is_refused_archive_by_state` to `backend/tests/test_api_model_lifecycle.py`: a fitted model is submitted through `POST /models/{id}/submit` (state `review`, asserted), a `model:fit` caller archives it, and the route answers 409 `VALIDATION_FAILED` with the status still `review`. This is what makes "an `approved` or `review` model is refused" in the `02` §5.1 dated line true by a test and not by the transition table alone. **OWED to a DB window, not run:** the test is DB-backed, so neither its green run nor the planted removal of the state guard (`_require_transition` in `archive`, expected red: 200 and status `archived`) was run. The red re-run at `a528160b` stays owed in that same window. `ruff check` on the file: rc=0; `ruff format --check` on the file reports the same older hunks, none in the new test.

## PRs

(none — the slice ends unpushed.)
