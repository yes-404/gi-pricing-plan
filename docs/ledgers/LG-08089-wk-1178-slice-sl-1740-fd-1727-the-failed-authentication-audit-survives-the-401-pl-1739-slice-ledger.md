---
id: LG-8089
family: ledger
title: WK-1178 slice SL-1740 — FD-1727, the failed-authentication audit row survives the 401 and every failure is counted (PL-1739), slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-17
owner: executor
tree: bf7686504d7b11954760de0440ed56608c722655
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
  The file after the removal was not re-run (no window left): owed to the gate. *(Discharged: window 3 below, 16 passed; and the proof gate ran it, no failure in it. Auditor-1740, 2026-10-17.)*
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

## Gate, 2026-10-17 (isolated proof-pair gate-1; read by auditor-1740 from `scratch/sl1740-gate/`)

Gate head `7f9b5b5303d984b356592de886259cf80e536477`, tree `401152b5fd1e35a70d40d232503936c5d043c364`
(`gate.log` START line), START 19:13:41Z → END 20:19:26Z. ruff, mypy, import_linter, req_coverage, contracts, FE
lint / type-check / build rc 0; `audit_docs` rc 1 (`FAILED (1): check 31: gap in the full allocation between
1771 and 8089`, a working-id artefact); pytest rc 1, `15 failed, 5942 passed, 6 skipped`; `pnpm test` rc 1
(`1 failed | 115 passed`, FR-1530 only); demo designed stop 20:19:19Z, rc 0. Of the 15: 13 are the root-`tests/`
docs-tooling cascade of the check-31 line; 2 were slice-caused
(`test_auth_oidc.py::test_rejection_reasons_are_not_returned_to_the_caller`,
`test_worker_raise_sites.py::test_every_quote_input_coded_raise_site_in_the_backend_is_accounted_for`), fixed
test-only at `0724b8e9` (above) and accepted by the maintainer, "2026-10-17 21:24:40 BST" (no re-gate; the
PR's CI is the remaining proof). FR-1530 is a main flake (FD 8103), counted against neither slice.

## Audit

*(Written by `auditor-1740`, 2026-10-17 (TZ=Europe/London), on head `0724b8e9543fe0560d862aa5abf3a2286c29112b`
tree `bf7686504d7b11954760de0440ed56608c722655`, range `origin/main...0724b8e9`. Code read-only; no test run by
the auditor; the gate is the lead's.)*

**1. Change set** (`git diff --stat origin/main...0724b8e9`, 13 paths, +763 -125): `api/deps.py`,
`auth/service.py`, `observability/metrics.py`; tests `test_auth_failure_audit.py` (new), `test_auth_keys.py`,
`test_auth_oidc.py`, `test_worker_raise_sites.py`; specs `06` (FR-368 pointer), `07` (FR-392); PL-1739 delta,
roadmap, INDEX, this ledger. Nothing outside scope. `7f9b5b53..0724b8e9` (gate head to head) touches only
`test_auth_oidc.py`, `test_worker_raise_sites.py` and this ledger (`git diff --stat`), so the gate ran all `src`.

**2. Obligations, derived from PL-1739's Acceptance Standard, FD-1727's Disposition and the rulings first:**
- **Acc. 3, spec first:** FR-392 amendment `4dfdd9f0` and the activation `28f63769` are ancestors of the first
  `backend/src` commit `96ee0572` (`merge-base --is-ancestor` rc 0 each); FR-392 names `gip_auth_failures_total`
  (`07-platform.md:76`). **Met.**
- **Acc. 5:** `git grep test_a_failed_authentication_is_audited HEAD -- backend/tests` prints nothing; the
  new file's only `unit_of_work` is the fixture setup (`:78`), no `pytest.raises` inside a unit. **Met.**
- **Acc. 6:** `git grep audit.record HEAD -- auth/service.py` prints one line, `:150` inside
  `record_auth_failure`. **Met.**
- **FD Disposition, "the `principal.auth_failed` row survives the request's rollback":** R1, R2, R3 (x2) assert
  a real HTTP 401 and exactly one row with the reason in `after` (R1 also the trace id); read the asserts at
  `:135-185`. API-key branch: `deps.py` `rollback` / `begin` / `record_auth_failure` / `commit` then raise,
  as ruled 14:41:18 (DP-1 (b)). **Met.**
- **Limb 3, counted by reason, closed label set:** `AuthFailureReason` has 8 members; R5, R6, R7, R10 (set equal
  to `EIGHT_REASONS`, no key material in labels). Workspace-less failures write no row, a WARNING and a count.
  **Met.**
- **DP-2 F1, a lost write is a 5xx:** R8 (audit raises: >=500, still counted) and R8 commit-limb (>=500, no
  row); the code has no `try/except` around the write. **Met.**
- **R11, one connection:** failing path max held 1, total 2; `/score` success total 1, max held 1;
  `/environments` max held 1. Window 3: 16 passed. **Met.**
- **Limb 4, FR-392 / FR-368 cross-reference:** `06-platform` FR-368 pointed, FR-392 amended. **Met.**
- **Acc. 1, 2:** check 31 is the one audit-docs failure, as expected; DP rulings quoted above. **Met.**
- **Acc. 4, per-test red-on-main by cause, and R4 / R8 / R10 breakers:** the ledger carries one aggregate
  (`13 failed, 2 passed`, window 1), no per-test causes and no breaker runs. **Delivered but evidence thin**
  (finding B1).
- **Acc. 7, full gate at the slice head:** gate ran at `7f9b5b53`, not `0724b8e9`; the delta is two test files,
  accepted without re-gate by the maintainer (21:24:40). **Met by ruling**, PR CI outstanding.
- **Second site (`require_identity`, `deps.py:149-168`, used by `/me`):** both branches changed, no test in the
  new file reaches them (finding B2). **Delivered but untested.**

**3. The 401 body, re-read independently (bearer and API-key).** `AuthenticationFailed.__init__`
(`auth/service.py:107-127`) calls `PlatformError.__init__` with the fixed title `Authentication failed` and the
fixed detail; `reason` and `workspace_id` are instance attributes. `to_problem` (`errors.py:476-486`) emits only
`type`, `title`, `status`, `code`, `detail`, `instance`, `errors` (empty, never set here), `trace_id`;
`_handle_platform_error` (`:498`) adds `exc.headers` (empty). All seven raise sites (`service.py:178, 244, 253,
257, 265, 269, 277`) pass the reason only as the enum argument. No other consumer of `.reason` outside
`auth/service.py` reads an `AuthenticationFailed`. **No response body or header carries the failure reason.**
Residual, pre-existing and unchanged from `origin/main`: the `code` differs by case (`TOKEN_EXPIRED`,
`API_KEY_EXPIRED`, `ENVIRONMENT_SCOPE_DENIED`, `API_KEY_INVALID`, `UNAUTHENTICATED`), so the code coarsely
discloses expired / scope-denied; the diff keeps each code exactly (compare the removed `_unauthenticated(...)`
arguments). Not a regression of this slice.

**4. The two fix commits (`0724b8e9`).** `test_rejection_reasons_are_not_returned_to_the_caller` is stricter than
before (status 401 and `reason.value` absent from the whole serialised body, for every reason) but now runs on
the exception object, not on a real HTTP response (B3). `_SITES`: the `_unauthenticated` entry was removed with
a comment; the census no longer sees the fixed-detail built in `AuthenticationFailed.__init__`.

**5. Findings.**
- **B1 (LOW):** Acc. 4's per-test red-by-cause and breaker evidence is not in the ledger. Owner: the lead
  decides: accept the aggregate or add a table before close.
- **B2 (MEDIUM, delivered but untested):** the identity-only dependency's two catch-and-record sites
  (`require_identity`, `/me`) have no test; a regression there (row lost, counter missing) would pass. Owner:
  the lead decides: a test now, or a deferral row owned by WK-1178.
- **B3 (LOW, observation):** the security guard on the 401 body no longer exercises the real response path; a
  future handler that adds the reason to a problem extension would not fail it. R1 to R3 assert on status and
  code only. Owner: lead decides whether to file.
- **B4 (LOW, observation):** `test_worker_raise_sites` no longer covers the 401 detail text; the fixed-detail
  rule for auth refusals now rests on one `__init__` and the test in B3.
- **B5 (LOW, fixed here):** front-matter `tree:` was the base-merge tree `2859fcc7`; set to `bf768650...`. The
  "owed to the gate" line is discharged (note added); a Gate section added. Task 4 stays open until the lead's
  closing acts.

**6. Proposed verdict:** all FD-1727 obligations delivered and evidenced except B1 (thin) and B2 (untested
second site); no requirement without a verdict. Proposal only; the lead adopts, amends or rejects.
MERGE-ACK: not yet given. Status left `active`.
