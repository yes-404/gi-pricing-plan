---
id: FD-1727
family: finding
title: A failed API-key authentication writes its audit row and then raises inside the unit of work that discards it, so FR-392's failed-authentication audit is unmet and no per-attempt record exists
status: closed
created: 2026-10-14
owner: auditor
tree: 8eaf6d5f9cd4204e1e077b44069d4afd395f1461
corrected_by: []
relates: [WK-1178, FR-392, FR-368, FR-389, NFR-519, P2]
---

# FD-1727 — a failed API-key authentication leaves no audit row

*(Minted 2026-10-14 as FD-1727 from working id 8036, in the D17 batch mint PR.)*

*(Filed under working id 8036, reserved by the lead in `eta.md`, line stamped "2026-10-14 11:54:58 BST"; a minter folds it
into the docs batch. The code was read at `origin/main` `4420f91fa4112a1fcabcae23d3d50a1ad4fcbb59` and the HTTP runs were
made at `origin/main` `8eaf6d5f9cd4204e1e077b44069d4afd395f1461`, both from a clean detached `git worktree`, never from the
root checkout. `git diff --stat 4420f91f 8eaf6d5f` over `backend/src/app/auth`, `backend/src/app/api/deps.py`,
`backend/src/app/db/session.py`, `backend/src/app/platform/audit.py`, `backend/src/app/observability/metrics.py` and
`backend/tests/test_auth_keys.py` is empty, so every line cite below holds at both trees.)*

## Authority

The audit run was ordered by the maintainer (by delegation), `to-lead.md`, "2026-10-14 11:08:32 BST", item 2, verbatim:
*"The failed-auth audit candidate: GO for an auditor RUN over HTTP: a bad API key against a protected route → 401 → read
`audit_events` (expect the FR-392 / 06 FR-368 row; the candidate says it is absent). Also run an expired key and a revoked
key, each a separate run. If confirmed: an FD, owner WK-1178, **fixed in P2** (a security audit trail, pre-freeze, small).
The auditor proposes severity; I expect at least MEDIUM, and HIGH if no other record of failed attempts exists (check
`gip_http_requests_total` 401s and any auth-failure counter or log line). The fix is a DESIGN choice and goes to the planner
as a DP: the failure audit committed in its OWN transaction independent of the request's unit of work, versus an outbox,
versus writing before the raise in a committed sub-unit. The test asserts the row SURVIVES the request's rollback."*

The scope was set by the maintainer (by delegation), `to-lead.md`, "2026-10-14 11:11:50 BST", which also withdrew the
NFR-519 limb of the 11:08:32 entry. The four numbered points, verbatim:
*"1. **The defect:** require_caller's unit_of_work (deps.py:240-242) rolls back the flushed failure-audit row when
authenticate_api_key raises (session.py:69-78), so a keyed-workspace failed authentication leaves NO audit row.
2. **The green-by-construction test:** test_auth_keys.py:205-212 puts pytest.raises INSIDE the unit_of_work, which swallows
the exception and COMMITS, unlike production. The fix's red must use production's shape (the exception escapes the unit of
work, or a real HTTP 401), red on main by cause. The current test is corrected, not kept beside it.
3. **Workspace-less failures (malformed key, unknown prefix, wrong secret) have NO record beyond a log warning**, and there
is no 401 or auth-failure counter. FR-392 says "Failed authentication … audited", unqualified. Where a failure with no
workspace is recorded (a platform-scope audit stream, or a labelled counter plus a structured log) is a DESIGN DP for the
planner, ruled before the build.
4. **Spec cross-reference:** FR-392 cites 06 FR-368, which does not name failed authentication. The fix slice adds a dated
clarification (on FR-368 or FR-392, the planner's recommendation) so the two agree."*

## Finding

**Proposed severity: HIGH, owner WK-1178, fixed in P2** (the auditor proposes; the lead and the maintainer (by delegation)
rule). Four limbs, below as sections; a limb is a clause of this finding and not a finding of its own.

`07-platform.md` FR-392 (row at `:76`): *"Failed authentication, key creation/rotation/revocation, and session anomalies are
audited (`06` FR-368)."* The row carries no dated amendment (`git grep -n "FR-392" origin/main -- docs`: the row, a redirect
and two citations). For an API key whose presented credential identifies a workspace, the audit row is written and then
discarded by the rollback of the unit of work that the failure itself raises through. The row never reaches the table.

## Evidence

One section per limb.

### Limb 1 — the rollback defect

The path, route to rollback, at `4420f91f`:

1. `backend/src/app/api/deps.py:240-242` (`require_caller`): `async with database.unit_of_work() as session:` then
   `identity = await authenticate_api_key(session, api_key)`. This is a unit of work around authentication only, not the
   route's.
2. `backend/src/app/auth/service.py:175` `authenticate_api_key` calls `_audit_auth_failure` (`:85-110`), which calls
   `audit.record(session, …)` (`:103`), and then raises `_unauthenticated(…)`, still inside the `async with` of step 1:
   `:184` (malformed), `:196` (unknown prefix or wrong secret), `:206` (archived account), `:216` (revoked), `:224`
   (expired, `API_KEY_EXPIRED`), `:236` (environment not granted).
3. `backend/src/app/platform/audit.py` `record` has "no `commit()` here" (module docstring `:7`) and ends in a `flush`
   (`:139-142`). It joins the caller's transaction by design (`:64-70`: "this must join the transaction that is already
   open").
4. `backend/src/app/db/session.py:69-78` `unit_of_work`: `async with self._sessionmaker() as session, session.begin():
   yield session`, documented "Commits once on clean exit; rolls back everything on any exception". The `PlatformError`
   leaves the `async with` of step 1, and the transaction, with the audit row in it, rolls back.

Nothing between the flush and the raise commits. The 401 reaches the caller; the row does not reach `audit_events`.

**The runs.** Three separate runs, each with a fresh `uvicorn app.main:create_app --factory` over a scratch database
`gipricing_failauth_89961209` (created `-T gipricing`, `alembic upgrade head`, dropped at the end), at `8eaf6d5f`, one
workspace `01a13a0b-65e7-77c2-8544-3269df56a6ff`, one `GET /api/v1/environments` with `Authorization: ApiKey <key>` each.
Setup, not under test: the workspace, a Service Account and its keys were inserted by `setup.py` using the service's own
`generate_key` and the row shape of `backend/tests/test_auth_keys.py` `_account_with_key`; the expired key has `expires_at`
in the past and the revoked key has `revoked_at` set. The failing authentication is the only thing done over HTTP.

| Run | Response | `audit_events` for the workspace, before → after | `audit_events` total, before → after | Other record |
|---|---|---|---|---|
| (a) unknown, well-formed key | 401 `API_KEY_INVALID` | 0 → 0 | 576 → 576 | log line `WARNING app.auth "authentication failed" action=principal.auth_failed reason="invalid key"` (no workspace, so no audit by design, limb 3) |
| (b) expired key | 401 `API_KEY_EXPIRED` | 0 → 0 | 576 → 576 | none: no `app.auth` line; the generic `app.request status 401` line and the uvicorn access line only |
| (c) revoked key | 401 `API_KEY_INVALID` | 0 → 0 | 576 → 576 | same as (b) |

Runs (b) and (c) reach `audit.record` with a known workspace (`service.py:216-222`, `:224-230`): the row was flushed and then
rolled back. A first attempt used `GET /api/v1/service-accounts`, which answers 405 before authentication, so it measured
nothing and is discarded; its logs were deleted. The run record is `~/.claude/jobs/b6860f8f/tmp/failauth/result-89961209.txt`
with `run.sh`, `setup.py` and the three server logs beside it; no key secret is in it (the request line is redacted to the
first 14 characters; the keys file was deleted).

**Every other record of a failed attempt**, searched for as the 11:08:32 entry required:

- `gip_http_requests_total` (`backend/src/app/observability/metrics.py:51-55`) is labelled `route`, `method`, `status`, and
  the status is `f"{status_code // 100}xx"` (`:121`). A failed authentication is a `4xx` increment on the route, shared with
  every other 4xx. After each run: `gip_http_requests_total{method="GET",route="/api/v1/environments",status="4xx"} 1.0`.
  There is no 401 series.
- `git grep -n "auth_fail\|principal.auth_failed" origin/main -- backend/src` finds no auth-failure counter; the only
  consumers of `principal.auth_failed` are the six `_audit_auth_failure` calls and the log line in `:96`.
- The only log line naming an authentication failure is `service.py:96`, reached only when no workspace is determinable.
  A keyed-workspace failure logs nothing of its own.

So for a keyed-workspace failure the whole record of an attempt is one 4xx tick and one request line carrying a trace id, with
no principal, no workspace, no reason. That is the HIGH condition the 11:08:32 entry set.

### Limb 2 — the test that is green by construction

`backend/tests/test_auth_keys.py:205-212` `test_a_failed_authentication_is_audited`, marked `req("FR-392")`:
`pytest.raises(PlatformError)` is the *inner* block, inside `async with database.unit_of_work() as session:`. The exception
is caught before the context manager exits, so `unit_of_work` sees a clean exit and **commits**; the test then reads the row
through a separate `database.session()`. Production lets the exception escape the `async with` (`deps.py:240-242`) and
rolls back. The test exercises a path production does not take, and it passes on exactly the code that loses the row.

The fix's red must have production's shape: either `pytest.raises` *outside* `async with database.unit_of_work()`, or a real
HTTP 401 through the app (as the runs above). It must be red on `main` for the cause: the missing row after the exception
escapes, not an unrelated failure. The current test is **corrected, not kept beside it**: leaving an inner-`raises` test
alongside would keep a passing test that cannot fail on this defect. (Ruling: the 11:11:50 entry, point 2.)

### Limb 3 — workspace-less failures and the missing counter

`service.py:85-98` skips the audit when `workspace_id is None`, with a stated reason (the log is chained per workspace and
inventing one would corrupt a real chain) and logs a WARNING instead. That covers the malformed key (`:181`) and the unknown
prefix or wrong secret (`:193`). Run (a) shows the result: a WARNING line and nothing else. FR-392 says "Failed authentication
… audited", unqualified, so this is either a gap in the code or a carve-out the spec never stated. There is also no
authentication-failure counter or 401 series.

**Where the record goes is a DESIGN DP for the planner, ruled before the build. Options only; no pick:**

- **A. A platform-scope audit stream:** a chain with a reserved workspace id for credential failures. It gives an audit
  row for every failure, but it conflicts with the per-workspace chaining that `audit.py` and `service.py:90-94` protect
  and needs a spec decision on a non-workspace chain.
- **B. A labelled counter plus the structured log:** e.g. `gip_auth_failures_total{reason, credential_kind}` with a
  bounded reason set, and the existing log line with `trace_id`. No new store; it also supplies the missing counter.
  Weaker as evidence than an audit row.
- **C. B plus a durable table**, e.g. `auth_failures`, not hash-chained, with a retention rule. A durable per-attempt
  record without touching the audit chain; a new data contract and a retention decision.
- **D. Split by cause:** B for a failure with no determinable workspace (an unauthenticated caller has no tenant), and
  limb 1's audit row for every failure with one. It matches what the code already assumes.

Two questions for the DP whichever option it takes: the counter's reason labels must stay a bounded set (`metrics.py`
documents that every label is bounded so nothing discloses which resources exist); and `service account archived` (`:206`)
and `environment not granted` (`:236`) share the code path, so they belong in the same fix.

### Limb 4 — the FR-392 ↔ 06 FR-368 cross-reference

FR-392 ends "(`06` FR-368)". `06-governance.md` FR-368 (row at `:154`) reads: *"Every governed state change, permission
change, acknowledgement, approval decision, deployment, rollback, suppression, and data purge emits an Audit Event, written
in the same transaction as the change (R2)."* It lists no failed authentication, and "in the same transaction as the change"
cannot describe a failure that has no change: following R2 here is the defect (limb 1). Neither row carries a dated
amendment. (NFR-519, `06:738`, "an audit write failure rolls back the domain change (R2)", is not breached: it governs a
failing audit write, and the maintainer (by delegation) withdrew that limb at 11:11:50. This finding does not name it.)

**Proposed clarification text** — PROPOSED here only; `docs/specs/` is not edited by this finding. The fix slice lands it
by the spec-change procedure, the planner choosing the row (FR-392 is recommended: it is the claim, and FR-368 is a list of
governed changes). Append to `07-platform.md` FR-392:

> *(Clarified <date> by the maintainer (by delegation), on <ruling id>.)* **A failed authentication is audited in its own
> committed transaction, independent of the request's unit of work, in the workspace of the credential presented when that
> workspace is determinable; a failure with no determinable workspace is recorded as `<the limb-3 DP's ruling>`. The
> reference to `06` FR-368 names the audit mechanism and its chain, not a listed event class.**

and, on `06-governance.md` FR-368, a pointer line:

> *(Clarified <date> by the maintainer (by delegation), on <ruling id>.)* **A failed authentication is an Audit Event under
> `07` FR-392, written outside the request's transaction: the one case of this row with no change for the event to share a
> transaction with.**

## The fix, for the planner (a DP; the auditor's options and lean only)

Limb 1's fix is a design choice and goes to the planner as a DP, ruled before the build. The options named by the
11:08:32 entry, with their costs:

- **(i) The failure audit in its own transaction on its own session**, committed before the raise:
  `async with database.unit_of_work() as audit_session: await audit.record(audit_session, …)` inside
  `_audit_auth_failure` (or in `require_caller`), the authentication session untouched. Smallest change; `audit.record`
  still joins an open transaction, and `unit_of_work` supplies one, so the per-workspace advisory lock and chain
  (`audit.py` `pg_advisory_xact_lock`) behave as for any other write. Cost: one extra connection per failed attempt, and a
  rule for an audit-write failure inside the failure path (fail closed with a 5xx, or still answer 401 and log).
- **(ii) An outbox:** write a row in the same transaction and let a relay produce the audit event. The row rolls back with
  the raise like the audit row does, so it needs its own commit anyway and adds machinery without removing the problem.
- **(iii) Write before the raise in a committed sub-unit:** catch the `PlatformError` in `require_caller`, commit, re-raise.
  Changes the shared `unit_of_work` contract (commit-on-exception) for every caller, or needs a second variant of it.

**The auditor's lean, not a recommendation to the planner's decision: (i).** It touches one function, keeps one audit write
path, and is the form the 11:08:32 entry names first.

**The test that must hold:** with `pytest.raises` outside `async with database.unit_of_work()` (or through a real HTTP
request to a protected route), a revoked key and an expired key each leave exactly one `principal.auth_failed` row in the
key's workspace with the reason in `after`, and the row is still there after the request's rollback. It is red on `main` for
that cause. Negatives: a successful authentication writes no failure row; limb 3's mechanism, whichever the DP picks, is
exercised for a malformed key and an unknown prefix. This replaces `test_auth_keys.py:205-212` (limb 2).

## Severity

**HIGH (proposed).** The keyed-workspace failures — revoked, expired, archived account, environment not granted — leave no
audit row (three runs), and they leave nothing else but one generic 4xx tick (no 401 series, no auth-failure counter, no
log line of their own). A key-guessing or stolen-key probe against a known workspace is invisible to that workspace's audit
trail, a security control that FR-392 requires and the suite shows green. Not CRITICAL: no data is exposed and no
authorisation is bypassed; the error runs toward lost evidence.

## Disclosure

During the setup of the runs one command began with `cd /tmp`, against the auditor charter's no-`cd` rule; the harness reset
the working directory in the same call, no state was affected, and every other command used `git -C`, `uv run --directory`
and absolute paths. Recorded here because the charter asks that a slip be stated, not omitted.

## Disposition

Carry forward, owner WK-1178: fixed in P2 (D17), as set by the maintainer (by delegation) at "2026-10-14 11:11:50 BST".
It needs a resolution before any P3 start (`CLAUDE.md` §14). The event that next confirms or discharges it is the fix's
merge, with the red shown on the base tree by its cause: the `principal.auth_failed` row survives the request's rollback.
Limb 3's mechanism and limb 1's option are the planner's DPs, ruled before the build; limb 4's text lands with the fix by
the spec-change procedure. The severity is proposed here and awaits the ruling.
