---
id: FD-2079
family: finding
title: POST /api/v1/models/{id}/archive checks model:submit; the spec's value is model:fit (FR-202, 06 §4.1)
status: closed
created: 2026-11-07   # original date 2026-11-05, set at the draft; working id 8366, minted 2026-11-07
owner: auditor
tree: 2f108b1eda22a4835279cee9b4c9e305babe3662
corrected_by: []
relates: [WK-1178, SL-2080, SL-2011, FR-202, FR-343, RL-1483, FD-1482]
---

# FD-2079 — The archive route checks `model:submit`; the spec's value is `model:fit`

*(Minted 2026-11-07 as FD-2079 from working id 8366, in the PR of SL-2080, with the mint tool of record `mint-repoint.py`; SL-2080 is working id 8368 and LG-2081 working id 8369. Drafted by aud-sl8368 and adopted by the lead, from-lead "2026-11-05 17:20:17 GMT". `tree` is the `origin/main` tree the finding was read at, `2f108b1e`.)*

## Finding

**Severity: low** (the maintainer's entry "2026-11-05 12:14:32 GMT" (1)(i), proposed in the register row). At `origin/main` `2f108b1eda22a4835279cee9b4c9e305babe3662`, `POST /api/v1/models/{model_id}/archive` (`backend/src/app/api/models.py`, `archive_model`) took `caller: SubmitModels`, and the service it calls (`backend/src/app/platform/modelling.py`, `archive`) checked `Permission.MODEL_SUBMIT`. `06` §4.1 (DP-A, `RL-1236`) makes `model:fit` the Model write right and describes `model:submit` as "submitting a Model … for approval"; archiving retires a model, it does not put one in front of an approver. SL-2011's `Permission` column (RL-1483 item 1) records `model:fit` for the row (`02` §5.1) and lists the disagreement in its ledger. A spec/code disagreement, ruled for the spec.

The defect is a mis-assigned permission, not a missing guard: the route was guarded, by the wrong constant. The consequence before the fix: a caller holding `model:fit` without `model:submit` (the built-in `analyst`) could not archive its own draft, fitted or superseded model; a custom role holding `model:submit` without `model:fit` could.

## Evidence

- `models.py` `archive_model` and `modelling.py` `archive` both read `MODEL_SUBMIT`; `submit_for_review` (`modelling.py`, the other `Permission.MODEL_SUBMIT` site, off this path) is correctly `model:submit`. The route reaches one dependency and one service check: the ruling's "one permission constant" holds.
- Roles, `packages/model-schema/src/model_schema/permissions.py` `BUILTIN_ROLES`: `analyst` holds `model:fit`; `pricing_actuary` = analyst + `model:submit`; the other four hold neither. No built-in role loses archive under the fix; `analyst` gains it.
- Found by SL-2011's column (cell vs code) and then by the pin (`backend/tests/test_route_permission_pin.py`, SL-8370), which is red on it until the fix merges.

## Dated note (2026-11-05, on the maintainer's "2026-11-05 14:07:26 GMT"): the superseded trace

Recorded as a trace, not a finding. The question the widening raises is whether a `superseded` model, now archivable by an `analyst`, can be one a live Rating Version relies on. By citation, at `origin/main` `2f108b1e`:

- New compiles refuse a `superseded` pin: `pricing_core/rating/compile.py` `_APPROVED_OR_BETTER`; `PIN_NOT_APPROVED` at the peril-component check and at the algorithm pin check.
- A compiled Bundle carries the model inline, and a deployment binds the Bundle hash: `platform/rating_versions.py` (the model resolver) and `platform/deployments.py` `_approved_compiled_version`.
- `archive` changes `status` only (`modelling.py` `archive`), so the row still resolves for a Bundle that names it.
- `/predict` refuses an archived model: `SCOREABLE_MODEL_STATUSES` (`packages/model-schema/.../modelling.py`).

**The deployment path was read by citation, not proven by a test.** The `approved` case, the one a live Rating Version can reference directly, is proven by test: `VALID_MODEL_TRANSITIONS` has no `approved → archived` edge, and SL-2080's `test_an_approved_model_is_refused_archive_by_state_not_permission` (fit-only and both) asserts 409 `VALIDATION_FAILED` with the status unchanged.

## Disposition

Fixed by SL-2080 (`sl-8368-archive-permission` @1fedb56f, tree 199aa6c6): `archive_model` takes the existing `FitModels`, `archive` checks `Permission.MODEL_FIT`, tests prove both directions on the real route; `SubmitModels` and every other route unmoved. The red re-run at a528160b, owed when this was drafted on 2026-11-05, was done in the window of 2026-11-05 17:43–17:45 UTC and is quoted in LG-2081's Build log: three reds, each by cause. The spec cell lands on `sl-8361-permission-column`; SL-2080's own §5.1 dated line is replaced by one sentence on the state guard at the re-merge.

## Decision

***Resolved 2026-11-07*** — closed in place 2026-11-07 by the executor, as the closing act of the mint of SL-2080 (WK-1178, LG-2081; this PR; its number, squash commit and merge date are written at the merge's date-of-record). The remedy in Disposition is delivered and tested both ways on the real route; the gate evidence is in LG-2081.
