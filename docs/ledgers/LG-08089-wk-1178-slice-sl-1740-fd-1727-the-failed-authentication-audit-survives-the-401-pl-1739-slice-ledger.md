---
id: LG-8089
family: ledger
title: WK-1178 slice SL-1740 — FD-1727, the failed-authentication audit row survives the 401 and every failure is counted (PL-1739), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-17
owner: executor
tree: 2859fcc7545a7d974a0fb2ef19676aa7c3f4ca80
phase: P2
work: WK-1178
slice: SL-1740
plans: [PL-1739]
corrected_by: []
relates: [PL-1739, FD-1727, SL-1455, LG-1760, RL-1685, FR-392, FR-368, NFR-519]
---

# LG-8089 — WK-1178 slice SL-1740: the failed-authentication audit

Executed by executor-1740b from PL-1739. Base: `origin/main` `9c602fec` (SL-1455, #1323) merged
into the prep branch at `95ccb7c6` (tree `2859fcc7`). Times are BST.

**GO:** `to-lead.md` "2026-10-17 14:39:20 BST — Maintainer: GO SL-1740 (PL-1739) with a widened
pre-build check". **Activation basis:** PL-1739 Activation 1 (DPs ruled, 12:18:57 on 2026-10-14), 2
(FD-1727 on main, #1307), 3 (census clean at `9c602fec`), 4 (this ledger's activation commit).

## Delta 2026-10-17 14:41:18 — DP-1 re-ruled for the API-key path (named delta, no new PL)

The maintainer's entry "2026-10-17 14:41:18 BST — SL-1740 DP-1 RE-RULED for the API-key path → (b)
on the request session; the bearer path unchanged" (`to-lead.md`), read in full:

- **API-key path → (b):** on `AuthenticationFailed`, `await session.rollback()`, write the failure
  row on the **same request session**, `await session.commit()`, then raise the 401. A commit
  failure propagates as a 5xx (DP-2 F1). (a) refused (a second unit breaks SL-1455's one-connection
  rule); (c) refused (can lose the row, FR-368).
- **Bearer path:** DP-1 (i) stands: its own `unit_of_work`, after the auth unit has rolled back.
- **Evidence required:** real-HTTP red-first for both branches; an audit-write failure → 5xx; the
  checkout count of a failed API-key request if SL-1455 left a pattern.

**P2 is stale at `9c602fec`.** The seat's P1–P6 table (from-lead, "executor-1740 released", 14:40:45):

| P | Plan said (at `a3fc2e8d`) | At `9c602fec` |
|---|---|---|
| P1 | `authenticate_api_key` calls `_audit_auth_failure` before each raise | **Holds.** `auth/service.py:178-260`, six calls before raises `:184..233`. |
| P2 | `require_caller` runs both auth paths in `unit_of_work`; the 401 rolls the flushed row back | **Stale.** The API-key path no longer uses `unit_of_work`: `resolve_caller` (`api/deps.py:229-286`) authenticates on the request-scoped `database.session()` (`deps.py:102-111`, no `begin()`), so the row was lost by close-without-commit, not rollback. Only the bearer path still uses `unit_of_work` (`deps.py:266`). `require_caller` (`:288`) only closes the session. |
| P3 | `audit.record` needs an open transaction, never commits | **Holds.** `platform/audit.py:71` `in_transaction()`, flush `:142`, no commit; `workspace_id` NOT NULL `db/models.py:217`. Consequence for (b): after `rollback()` the session has no transaction until its next statement, so the write follows `await session.begin()`. |
| P4 | Bearer path logs INFO and has no workspace | **Holds.** |
| P5 | No auth-failure counter | **Holds.** |
| P6 | `test_auth_keys.py` audit tests catch inside `unit_of_work` | **Holds, and unrepresentative.** |

**Second site the plan did not name.** `api/deps.py` also authenticates in the identity-only
dependency (bearer and API key, each inside its own `unit_of_work`, `deps.py:~143-154`). It has no
request session, so DP-1 (i) applies as ruled and both branches there record in a unit of their own
through the same helper. Flagged to the lead for confirmation; (b)'s one-connection reasoning does not
arise there.

## Tasks

- [x] Activation commit (PL-1739 and the roadmap row set `active`).
- [x] Task 1 — spec: `07` FR-392 amended, `06` FR-368 pointed. T1's "its own transaction, committed
  after the request's own unit of work has rolled back" is worded for both mechanisms (the API-key
  row is written on the request session after its rollback).
- [x] Task 2 — reds: `backend/tests/test_auth_failure_audit.py` (R1–R10 adapted; R8 gains the commit
  limb; R11 the checkout/check-in count). `test_auth_keys.py` `test_a_failed_authentication_is_audited`
  and `test_no_audit_event_contains_a_key_secret` deleted, replaced by R1–R3 and R9, which go through
  real HTTP, so the row has to survive the 401 itself.
- [x] Task 3 — implementation: `AuthFailureReason`, `AuthenticationFailed`, `record_auth_failure`
  (`auth/service.py`); the catch in `resolve_caller` and the identity dependency (`api/deps.py`);
  `gip_auth_failures_total` (`observability/metrics.py`).
- [x] The DB runs (2026-10-17, small-test slot, per-worktree DB from template `gipricing`, dropped rc 0
  both times). Window 1, 18:15:34–18:16:19 BST: RED with `backend/src` from `96ee0572^`,
  `test_auth_failure_audit.py` **13 failed, 2 passed** (rc 1; both R11 tests among the failures);
  GREEN at head, `test_auth_keys.py` **18 passed** (rc 0), `test_auth_failure_audit.py` 6 failed / 9
  passed (rc 1). Five were a test defect (the file read `prometheus_client`'s default `REGISTRY`, not
  `app.observability.metrics.REGISTRY`; fixed in the import). The sixth was a new success-path R11
  test on `GET /environments`: `{'checkouts': 3}`, `assert 3 == 1`, because that route's handler opens
  its own sessions; the success-path total of 1 is `test_score_request_cost.py`'s (`MAX_CHECKOUTS`, on
  `/score`), so the test was removed and the failing-path `checkouts == 2` kept. Window 2,
  18:16:55–18:17:11 BST: the file at that tree **14 passed, 1 failed** (the removed test), rc 1.
  The file after the removal was not re-run (no window left): owed to the gate.
- [ ] Task 4 — gate, closing acts, audit.

## Build log

- 2026-10-17 — pure checks only (no DB): `ruff check` on the changed files and `mypy` on the changed
  `src` files; results in the report.
- Bearer note: a rejected token resolves to no workspace (the user is never looked up), so the bearer
  branch writes no audit row, only the counter and the WARNING; "the row survives" is therefore
  asserted for the API-key branch, and the bearer test asserts no row and one count.
- R11 note: the failure path takes **two sequential** checkouts (the rollback returns the
  connection; the audit write takes another), never two held at once. `test_score_request_cost.py`'s
  `MAX_CHECKOUTS == 1` is for the success path; R11 asserts the maximum held at once is 1.

## R11 refinement, 2026-10-17 18:20 BST (the maintainer's ruling to the lead, relayed in the executor-1740d brief)

The removed success-path R11 test is restored as two: `/score` success asserts total checkouts 1 and
max held 1 (SL-1455's rule); `GET /environments` success asserts max held 1 only, because that route
opens its own sessions and three sequential checkouts are legal (the rule is concurrency). The
failing-path asserts (max held 1, total 2) are unchanged.

DB window 3 (2026-10-17, small-test slot, per-worktree DB, dropped rc 0): `test_auth_failure_audit.py`
at this tree, **16 passed** (rc 0), in 11.35 s.

2026-10-17 21:23 BST, executor-1740f, on the maintainer's ruling "2026-10-17 21:20:40 BST" (to-lead.md), test-only, at 7f9b5b53:

1. `test_auth_oidc.py::test_rejection_reasons_are_not_returned_to_the_caller`: security read first. The 401 is `AuthenticationFailed.__init__` (`backend/src/app/auth/service.py:107-127`, `super().__init__(code, "Authentication failed", 401, "The credential presented was not accepted. Quote the trace id when reporting it.")`); the reason is only an attribute for `record_auth_failure`. Bearer raise at service.py:178, API-key raises at 244, 253, 257, 265, 269, 277: none passes reason text into the body (code and detail identical to origin/main's `_unauthenticated`). Re-pointed from `_unauthenticated().to_problem()` (asserts on detail: no "signature", no "expired") to `AuthenticationFailed("UNAUTHENTICATED", reason).to_problem()` for every `AuthFailureReason`, same two detail asserts plus status 401 and `reason.value` absent from the whole serialised body (stronger). 10 passed, rc 0.
2. `test_worker_raise_sites.py::_SITES`: the census differs by one key, `(service.py, _unauthenticated, <dynamic>)`, gone because the helper was replaced; the refusals remain, raised as `AuthenticationFailed` at the lines above, whose fixed detail is built in `__init__` through `super().__init__` (outside `_CALLEES`). Entry removed with a comment. 3 passed, rc 0.
3. `RatingDesignView.test.ts` --maxWorkers=2, solo, no vitest running: sl-1547 (4c45b8f2) 7 passed rc 0; this tree (7f9b5b53) first run 1 failed/6 passed rc 1 (FR-1530: `Unable to find a label with the text of: input step Driver age (s_in_age)`), reruns 7 passed twice.

## PRs

Not opened yet; the lead opens the PR.
