---
id: PL-8044
family: plan
kind: map
title: WK-1178 — the failed-authentication audit (FD-1727) — the refusal's audit row survives the 401, the workspace-less failures counted, and slice SL-8045 — Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: a3fc2e8dd384de6abf909f662f43011b8078fb4e
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-8045, FD-1727]
---

# PL-8044 — WK-1178: the failed-authentication audit (Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5. WK-1178 is the
> standing maintenance Work and has no single map plan; this delta cuts one new slice, `SL-8045`,
> and changes no other slice. DP-1 to DP-4 are ruled, by the maintainer (by delegation) directly, in
> `to-lead.md` "2026-10-14 12:18:57 BST" item (1); that entry is the record and no decision-maker
> `RL-` is filed. The plan stays `draft` until the slice's activation commit. Required sub-skill
> for the executor: `subagent-driven-development` or `executing-plans`.
> Bound skills: `spec-change` (the spec text lands first, in the slice's commit),
> `fastapi-service`, `python-package`, `python-test`, `dev-commands`, `git-hygiene`.

Working ids PL 8044 and SL 8045, reserved by the lead in `eta.md`, "2026-10-14 12:07:20 BST lead:
RESERVED working ids PL 8044 + SL 8045 = the FD 8036 fix". Written 2026-10-14 (from 12:07 BST) by
the planner (planner-fd8036). Evidence was read at `origin/main` `a3fc2e8d`. The auditor's run
(below) ran at `8eaf6d5f`; `git diff --stat 8eaf6d5f a3fc2e8d` over `backend/src/app/auth`,
`backend/src/app/api/deps.py`, `backend/src/app/db/session.py`, `backend/src/app/platform/audit.py`,
`backend/src/app/observability/metrics.py`, `backend/tests/test_auth_keys.py`,
`docs/specs/07-platform.md` and `docs/specs/06-governance.md` prints nothing, so the run and every
line number below hold at both trees.

## Goal

Done means: a failed authentication that resolves to a workspace leaves exactly one
`principal.auth_failed` Audit Event in that workspace, committed even though the request's own unit
of work rolls back with the 401, written in its own unit of work after the auth unit has rolled
back (DP-1 (i)); if that write fails, the caller gets a `5xx`, never a silent `401` (DP-2 F1);
**every** failure, keyed or not and the bearer path included, is counted in
`gip_auth_failures_total{reason}` over a closed set of exactly eight labels, and a workspace-less
failure keeps a `WARNING` log line with no secret (DP-3 B); `07` FR-392 carries a dated amendment
and `06` FR-368 a dated pointer (DP-4 (a)); and the two tests that were green only because they
caught the raise inside the unit are replaced by HTTP reds, each red on `main` by its cause. One
slice, `SL-8045`.

## Authority

- **The run order:** the maintainer's (by delegation) entry in `to-lead.md`, "2026-10-14 11:08:32
  BST — Failed-auth audit rollback: auditor run GO; NFR-519's "delivered" re-opened pending it;
  SL-1455 T3 noted (re lead 11:08)", item 2, verbatim:
  "2. **The failed-auth audit candidate: GO for an auditor RUN** over HTTP: a bad API key against a
  protected route → 401 → read `audit_events` (expect the FR-392 / 06 FR-368 row; the candidate says
  it is absent). Also run an expired key and a revoked key, each a separate run. If confirmed:
  - an FD, owner WK-1178, **fixed in P2** (a security audit trail, pre-freeze, small). The auditor
    proposes severity; I expect at least MEDIUM, and HIGH if no other record of failed attempts
    exists (check `gip_http_requests_total` 401s and any auth-failure counter or log line).
  - The fix is a DESIGN choice and goes to the planner as a DP: the failure audit committed in its
    OWN transaction independent of the request's unit of work, versus an outbox, versus writing
    before the raise in a committed sub-unit. The test asserts the row SURVIVES the request's
    rollback.
  - It rides D17."
- **The scope:** the entry "2026-10-14 11:11:50 BST — NFR-519 hold RELEASED (letter reading
  correct); the failed-auth FD scope set (re lead 11:11)", verbatim:
  "**NFR-519 → DELIVERED, hold released.** Its full text (06:738), "Audit writes never fail silently:
  an audit write failure rolls back the domain change (R2)", governs a FAILING audit WRITE. Here the
  write succeeds and is discarded by the request's rollback, with no domain change. The breach is
  FR-392's (07:76), not NFR-519's. My 11:08:32 re-opening is withdrawn: I reasoned from the spirit of
  the title before reading the row. Add `req("NFR-519")` to test_deployments.py:540-570 in the marker
  batch, as first ruled.
  **The failed-auth FD (D17, owner WK-1178, FIXED IN P2), its scope on the read (the run confirms):**
  1. **The defect:** require_caller's unit_of_work (deps.py:240-242) rolls back the flushed
  failure-audit row when authenticate_api_key raises (session.py:69-78), so a keyed-workspace failed
  authentication leaves NO audit row.
  2. **The green-by-construction test:** test_auth_keys.py:205-212 puts pytest.raises INSIDE the
  unit_of_work, which swallows the exception and COMMITS, unlike production. The fix's red must use
  production's shape (the exception escapes the unit of work, or a real HTTP 401), red on main by
  cause. The current test is corrected, not kept beside it.
  3. **Workspace-less failures (malformed key, unknown prefix, wrong secret) have NO record beyond a
  log warning**, and there is no 401 or auth-failure counter. FR-392 says "Failed authentication …
  audited", unqualified. Where a failure with no workspace is recorded (a platform-scope audit
  stream, or a labelled counter plus a structured log) is a DESIGN DP for the planner, ruled before
  the build.
  4. **Spec cross-reference:** FR-392 cites 06 FR-368, which does not name failed authentication.
  The fix slice adds a dated clarification (on FR-368 or FR-392, the planner's recommendation) so
  the two agree.
  Severity: the auditor proposes after the run. On your read the HIGH condition ("no other record of
  failed attempts") holds, so I expect HIGH."
- **The rulings:** the maintainer's (by delegation) entry "2026-10-14 12:18:57 BST — PL 8044/SL 8045
  (failed-auth fix) and PL 8016 re-cut DPs RULED by me directly (no DM needed); superuser finding
  folded into FD 8038 / S-b (re lead 12:18:08)", item (1), verbatim:
  "**(1) PL 8044/SL 8045 @dc1c9bc6: all four as recommended; this entry is the record (cite it in the
  plan's Ruled column, no separate RL):**
  - **DP-1 (i):** a separate unit_of_work opened after the auth unit rolls back. The red asserts the
    row SURVIVES the request's 401 in production shape (a real HTTP 401, the exception escaping).
  - **DP-2 F1:** if the failure-audit write itself fails → 5xx, never a silent 401. That is
    consistent with "audit never fails silently"; it is counted.
  - **DP-3 B:** `gip_auth_failures_total{reason}` with a CLOSED label set (exactly the 8 named; a
    test asserts no other label value can be emitted, and no key material, prefix or principal in any
    label) + a WARNING log line without secrets. A/C/D rejected for flood/oracle risk, agreed. The
    bearer path's INFO-only log (service.py:116-118) is raised to WARNING and counted under the same
    metric.
  - **DP-4 (a):** the dated 07 FR-392 amendment + the 06 FR-368 pointer, with the T-text as in the
    plan.
  - **R9:** the vacuous `test_no_audit_event_contains_a_key_secret` (0 events in production shape)
    becomes a red that FIRST produces failure events, then asserts no secret. Good."
- **Severity:** no later entry in `to-lead.md` names FD 8036 (`grep -n 8036` over the file prints
  nothing at 12:10 BST). The lead's reservation records it as "proposed HIGH" (`eta.md`,
  "2026-10-14 11:54:58 BST lead: RESERVED working id FD 8036"). This plan assumes no severity; the
  slice is fixed in P2 either way (11:11:50).
- **NFR-519:** released by 11:11:50. This slice names it in no marker and does not regress it: the
  business path keeps `audit.record`'s same-transaction rule unchanged, and DP-2 (F1) makes a
  failing *failure-audit* write a `5xx`.

## The run (auditor-failauth)

`/home/puzhenhao1989/.claude/jobs/b6860f8f/tmp/failauth/result-89961209.txt`, "run 89961209 at
2026-10-14T10:52:59+00:00; origin/main=8eaf6d5f", three runs against `GET /api/v1/environments`:

| Run | Response | `audit_events` total before → after | Metric after | Log |
|---|---|---|---|---|
| unknown key | `401 API_KEY_INVALID` | 576 → 576 | `gip_http_requests_total{…,status="4xx"} 1.0` | one `WARNING` `app.auth` line, `"action":"principal.auth_failed","reason":"invalid key"` |
| expired key | `401 API_KEY_EXPIRED` | 576 → 576 | the same, `4xx` | no auth line (the row was attempted and rolled back) |
| revoked key | `401 API_KEY_INVALID` | 576 → 576 | the same, `4xx` | no auth line |

The expired and revoked keys belong to a seeded account in a known workspace, so each run should
have written one row. It wrote none.

## Premises (read at `a3fc2e8d`)

- **P1 — the write.** `authenticate_api_key` (`backend/src/app/auth/service.py:175-253`) calls
  `_audit_auth_failure` before each `raise _unauthenticated(…)`: malformed key `:180-184`, unknown
  prefix or wrong secret `:190-196` (one branch, so the prefix is no oracle, `:190-192`), archived
  or missing account `:198-206`, revoked `:209-216`, expired `:217-224`, environment not granted
  `:229-236`. `_audit_auth_failure` (`:85-106`) calls `audit.record` when a workspace is known and
  logs a `WARNING` otherwise (`:95-97`). The detail strings are "malformed key", "invalid key",
  "service account archived", "key revoked", "key expired", "environment not granted".
- **P2 — the rollback.** `require_caller` (`backend/src/app/api/deps.py:203-242`) runs
  `authenticate_api_key` inside `async with database.unit_of_work()` (`:240-241`), and the bearer
  path the same way (`:234-235`). `Database.unit_of_work` (`backend/src/app/db/session.py:68-78`) is
  `session.begin()`: "Commits once on clean exit; rolls back everything on any exception". The 401
  raised inside the unit rolls back the flushed audit row.
- **P3 — the audit sink.** `audit.record` (`backend/src/app/platform/audit.py:53-140`) refuses
  without an open transaction (`:71-76`), takes a transaction-scoped advisory lock per workspace
  (`:78-86`, `pg_advisory_xact_lock`), reads the chain head and appends (`:88-138`). It has no
  commit and no `try/except` (module docstring `:6-9`). `audit_events.workspace_id` is
  `nullable=False` (`backend/src/app/db/models.py:217`); the chain is per workspace (`06` FR-372).
- **P4 — the bearer path.** `authenticate_bearer` (`service.py:109-118`) logs a rejected token at
  `INFO` (`:116`) and raises with no audit attempt and no workspace. FR-392's "Failed
  authentication" covers it; the auditor's limb 3 list did not name it.
- **P5 — the metric.** `gip_http_requests_total` labels status by class
  (`backend/src/app/observability/metrics.py:121`, `status=f"{status_code // 100}xx"`), so a 401 is
  indistinguishable from any 4xx. No auth-failure counter exists. The precedent for a named counter
  in a spec row is FR-452's `gip_rate_limit_unenforced_total` (`07-platform.md:183`;
  `metrics.py:66-71`).
- **P6 — the green-by-construction tests.** `test_a_failed_authentication_is_audited`
  (`backend/tests/test_auth_keys.py:198-212`) catches the raise inside the unit (`:201-203`), so the
  unit commits and the row survives. `test_no_audit_event_contains_a_key_secret` (`:216-238`) has
  the same shape (`:224-226`); in production's shape its `for` loop runs over zero events and
  passes vacuously.
- **P7 — the spec.** `07` FR-392 (`docs/specs/07-platform.md:76`): "Failed authentication, key
  creation/rotation/revocation, and session anomalies are audited (`06` FR-368)." `06` FR-368
  (`docs/specs/06-governance.md:154`) lists governed state changes, "written in the same
  transaction as the change (R2)", and does not name failed authentication. `06` NFR-519
  (`:738`) governs a failing audit write.
- **P8 — who can write a keyed-workspace failure row.** Every keyed-workspace branch (`:198-236`) is
  reached only after a prefix match **and** a correct secret (`:190`). A stranger without a real
  key reaches only the workspace-less branches.
- **P9 — the HTTP harness.** `backend/tests/test_workspace_switch.py:25-27` builds
  `TestClient(create_app(api_settings), raise_server_exceptions=False)` and sends
  `Authorization: ApiKey …` (`:108`). The reds use the same harness.

## Decision points

All four are ruled by the maintainer (by delegation) directly, in the entry quoted under
*Authority* ("2026-10-14 12:18:57 BST", item (1): "all four as recommended; this entry is the
record"). No decision-maker `RL-` is filed. The options not taken are removed here; they stand in
this file at `dc1c9bc6`.

| DP | Question | Ruling | Why | Kind | Blocking? | Ruled |
|---|---|---|---|---|---|---|
| **DP-1** | How does a keyed-workspace failure's audit row survive the 401? | **(i) Its own committed unit of work.** `authenticate_api_key` stops writing; it raises `AuthenticationFailed`, a `PlatformError` subclass carrying the 401 fields plus `workspace_id` and `reason`. `require_caller` wraps each auth `async with` in `try/except AuthenticationFailed`: **after** the auth unit has rolled back, it opens `database.unit_of_work()`, calls `audit.record` (its transaction rule holds), commits, and re-raises. One extra transaction per keyed failure, sequential, never two connections at once; no lock-order risk, because the auth unit holds no advisory lock when it exits. The red asserts the row survives a real HTTP `401`, the exception escaping (R1 to R3). | The committed transaction contains the audit row and nothing else, by construction, which no future edit to the auth branches can break. `audit.record` stays exactly as it is (P3), so R2 and NFR-519 are untouched on the business path. | design | no — ruled | the maintainer (by delegation), `to-lead.md` "2026-10-14 12:18:57 BST", item (1), DP-1 |
| **DP-2** | If the failure-audit write itself fails (database down, constraint), what does the caller get? | **(F1) Fail closed, loud:** the exception escapes; the response is the platform's `5xx` problem response, and the error handler logs it. No `try/except` around the write, as `audit.py` `:6-9` requires of every audit write. The failure is still counted: the counter is incremented before the write (Task 3 item 1), so a `5xx` from a lost row is one `gip_auth_failures_total` increment (R8). | The request is refused either way, so no access is granted; a lost audit row is visible as a `5xx`, never a silent `401` (NFR-519's word). A caller cannot choose when the database fails, so the `5xx` is no oracle for which check failed. | design | no — ruled | the same entry, item (1), DP-2 |
| **DP-3** | Where is a workspace-less failure recorded (malformed key, unknown prefix or wrong secret, archived account with no account row, a rejected bearer token)? | **(B) A labelled counter plus the structured log.** `gip_auth_failures_total{reason}` counts **every** failure, keyed or not. Its one label is `reason`, a **closed set of exactly eight** values, never input: `malformed_key`, `invalid_key` (unknown prefix and wrong secret, one label, as `:190-192` requires), `account_archived`, `key_revoked`, `key_expired`, `environment_not_granted`, `bearer_expired`, `bearer_rejected`. No other label value can be emitted, and no key material, prefix or principal appears in any label (R10). A workspace-less failure also keeps its structured `WARNING` line (trace id, action, reason; no secret, R10). The bearer path's `INFO`-only log (`service.py:116-118`) is raised to `WARNING` and counted under the same metric (R7). A keyed failure also writes its audit row (DP-1). | The counter totals every 401 `require_caller` raises, so one series covers keyed and workspace-less failures. It adds no storage an unauthenticated caller can fill; A, C and D are rejected for flood and oracle risk (the ruling: "A/C/D rejected for flood/oracle risk, agreed"). | design (spec change) | no — ruled | the same entry, item (1), DP-3 |
| **DP-4** | Where does the clarification land? | **(a) A dated amendment on `07` FR-392** (the rule: scope, own transaction, the counter) **and a dated pointer line on `06` FR-368**, with T1 and T2 below as written. | FR-392 owns the rule; FR-368 points at it and says why R2's clause does not govern it: FR-368's rows are "written in the same transaction as the change (R2)", and a failed authentication has no change. | spec placement | no — ruled | the same entry, item (1), DP-4 |

## The spec text (T-text), as ruled, applied in the slice's commit, not here

Written for DP-1 (i), DP-2 (F1), DP-3 (B) and DP-4 (a), all four ruled; DP-4's ruling keeps it as
written ("with the T-text as in the plan", 12:18:57 item (1)). `<date>` and the FD id are filled in
the slice's commit; no `RL-` id is cited, because the rulings are the 12:18:57 entry and PL-8044
carries them. This plan does not edit `docs/specs/`.

**T1 — a dated amendment appended to `07` FR-392's cell (`docs/specs/07-platform.md:76`):**

> *Amended `<date>` (FD-`<n>`, PL-8044):* **A failed authentication is recorded whether or not it
> reaches a workspace, and its record survives the refusal.** A failure whose credential resolves to
> a workspace (an API key that is revoked, expired, belongs to an archived Service Account, or was
> presented for an environment the account is not granted) writes one `principal.auth_failed` Audit
> Event in that workspace, with the reason in `after`, **in its own transaction, committed after
> the request's own unit of work has rolled back**. `06` R2's same-transaction clause does not
> govern it: there is no change for it to share a transaction with. A failure that resolves to no
> workspace (a malformed key, an unknown prefix or a wrong secret, a rejected bearer token) writes
> no Audit Event, because the chain is per workspace (`06` FR-372) and the caller reached none; it is
> logged as a structured `WARNING` with `trace_id`, `action` and `reason`. **Every** failure
> increments `gip_auth_failures_total{reason}`, whose `reason` is a closed set: `malformed_key`,
> `invalid_key`, `account_archived`, `key_revoked`, `key_expired`, `environment_not_granted`,
> `bearer_expired`, `bearer_rejected`. An unknown prefix and a wrong secret share `invalid_key`, so
> the label is no oracle. If the failure's own audit write fails, the request fails with a `5xx`,
> never a silent `401` (NFR-519).

**T2 — a dated pointer appended to `06` FR-368's cell (`docs/specs/06-governance.md:154`):**

> *Pointer added `<date>` (FD-`<n>`):* failed authentication is audited under `07` FR-392, which
> states its scope (failures that resolve to a workspace) and its own-transaction rule. It is not a
> governed state change, so this row's same-transaction clause (R2) does not govern it.

## Tasks

### SL-8045 — the slice row

The row is in `docs/roadmap.md` under WK-1178. One PR, one `LG-`, per Lean P2 L1.

### Task 0 — the readiness reads (no code)

1. Quote the rulings of DP-1 to DP-4 and R9 into the `LG-` from the 12:18:57 entry, item (1)
   (quoted under *Authority*); no `RL-` exists to read.
2. Confirm the harness of P9 against the `database` and `workspace_id` fixtures the reds need (the
   app and the fixtures must point at one database), and whether `create_app(api_settings)` has an
   OIDC verifier that refuses a garbage bearer token. If it has none, R7's bearer limb is a
   `require_caller`-level test instead, and the `LG-` says so.
3. The shared-path census (below) against whatever is open at GO.

### Task 1 — the spec (first commit, `spec-change`)

Apply T1 and T2 as ruled. Run `python3 scripts/audit-docs.py` once, through gate-2.

### Task 2 — the reds, committed before the implementation

A new file `backend/tests/test_auth_failure_audit.py`, every test `@pytest.mark.req("FR-392")`,
every test through the HTTP harness (P9), never `authenticate_api_key` inside a unit of work.
`test_auth_keys.py:198-212` is **deleted** (R1 replaces it; 11:11:50 item 2: "corrected, not kept
beside it"), and `:216-238` is **deleted** (R9 replaces it in the new file; 12:18:57 item (1),
R9). Each red's failure on `main` is quoted in the `LG-` by its cause.

| # | Test | Red on `main`, by cause |
|---|---|---|
| R1 | A revoked key → a real HTTP `401` (the exception escaping the auth unit, DP-1 (i)); the row **survives** it: the key's workspace then holds **exactly one** `principal.auth_failed` row, `after == {"reason": "key revoked"}`, and its `trace_id` equals the response's `x-trace-id`. | `0 != 1`: the row was flushed in the auth unit and rolled back with the 401 (P2). |
| R2 | The same for an expired key: `after == {"reason": "key expired"}`, response code `API_KEY_EXPIRED`. | `0 != 1`, the same cause. |
| R3 | The same for an archived account (`"service account archived"`) and for a key presented for an environment not granted (`"environment not granted"`), one test each. | `0 != 1`, the same cause. |
| R4 | **Guard:** a valid key → `200`, and the workspace holds **no** `principal.auth_failed` row. | Green on `main` (success never writes). Shown red on a planted breaker that records unconditionally; the `LG-` quotes it. |
| R5 | A malformed key, an unknown prefix and a wrong secret each → `401`, and `gip_auth_failures_total{reason="malformed_key"}` / `{reason="invalid_key"}` rise by exactly 1 per request (read with `REGISTRY.get_sample_value` before and after); `audit_events` total is unchanged. | `None`: the metric does not exist (P5). |
| R6 | R1's and R2's requests also raise `{reason="key_revoked"}` and `{reason="key_expired"}` by 1. | `None`, the same cause. |
| R7 | A rejected bearer token → `401`, `{reason="bearer_rejected"}` rises by 1, and the `app.auth` line is a `WARNING` (no longer `INFO`, 12:18:57 DP-3) with `action` and `reason` (Task 0 item 2 decides the harness). | `None`, the same cause; and the line is `INFO` (`service.py:116-118`). |
| R8 | **Guard**, DP-2 (F1): with `audit.record` patched to raise, a revoked key → a `5xx` problem response, not `401`, and `{reason="key_revoked"}` still rises by 1 ("it is counted"). | The counter limb: `None` on `main`, the metric does not exist (P5). The `5xx` limb is green on `main` (the raise escapes the auth unit), so it is shown red on a planted breaker that wraps the write in `try/except`; the `LG-` quotes it. |
| R9 | `test_no_audit_event_contains_a_key_secret` (`:216-238`) moves to the HTTP shape and is no longer vacuous: it **first produces** the four keyed failure events (a revoked, an expired, an archived-account and a not-granted key, each through HTTP, each key's full token and secret known to the test), asserts **exactly four** `principal.auth_failed` rows exist, and **only then** asserts that no key's secret, and no full token, appears in any of those rows' `after`, `before` or any other text column. | `0 != 4` (P6: today, in production's shape, no event is produced, so the old loop ran over nothing). |
| R10 | **The closed label set**, DP-3 (B). After driving every failure path R1 to R3, R5 and R7 cover (each with a known key prefix, secret, key id and Service Account id and name): (a) every `gip_auth_failures_total` sample read from `REGISTRY.collect()` has the label keys `{"reason"}` exactly, and its `reason` value is one of the eight named, and the set of reason values in the code (the `AuthFailureReason` type, Task 3 item 1) equals those eight exactly; (b) passing any other value to `record_auth_failure` raises and adds no sample; (c) no label value, and no `app.auth` `WARNING` line captured by `caplog` in the run, contains any key's secret, full token or prefix, the key id, or the Service Account's id or name. | The metric is absent from `REGISTRY` and the reason type does not exist (P5). Shown red also on a planted breaker that labels with the raw detail string or the key prefix; the `LG-` quotes it. |

### Task 3 — the implementation (as ruled)

1. `backend/src/app/auth/service.py`: an `AuthenticationFailed(PlatformError)` carrying
   `workspace_id: UUID | None` and `reason: AuthFailureReason`, a `StrEnum` whose members are
   exactly the eight DP-3 labels, so no other value can reach the label. Every branch of P1 raises
   it instead of calling `_audit_auth_failure`; the bearer branch (P4) raises it too, and its `INFO`
   line (`:116-118`) is removed in favour of the `WARNING` below. A function
   `record_auth_failure(database, exc)` refuses a reason that is not an `AuthFailureReason` member,
   increments the counter with `reason.value` (first, so a failing write is still counted, DP-2),
   and then either opens `database.unit_of_work()` and calls `audit.record` with today's arguments
   (`:98-106`, `after` unchanged), with no `try/except` around it (DP-2 F1), or logs a `WARNING`
   with `trace_id`, `action` and `reason`, never the presented credential. `_audit_auth_failure` is removed. The module docstring's
   FR-392 sentence (`:8-9`) and `_audit_auth_failure`'s docstring reasoning move to the new function.
2. `backend/src/app/api/deps.py:232-242`: each auth `async with` sits inside `try / except
   AuthenticationFailed as exc: await record_auth_failure(database, exc); raise`, the `except`
   outside the `async with`, so the auth unit has rolled back first.
3. `backend/src/app/observability/metrics.py`: `auth_failures = Counter("gip_auth_failures_total",
   …, ("reason",), registry=REGISTRY)`, in the form of `:66-71`.

### Task 4 — the gate and the closing acts

The full gate, both halves (CLAUDE.md §11), in a granted slot; the `LG-` names the tree. The `LG-`
quotes each red and each breaker by cause, the 12:18:57 rulings, and the FD the merge discharges.
`SL-8045`'s closing lines on `docs/roadmap.md` in the slice PR.

## The write set

`docs/specs/07-platform.md` (FR-392's cell only), `docs/specs/06-governance.md` (FR-368's cell
only), `backend/src/app/auth/service.py`, `backend/src/app/api/deps.py`,
`backend/src/app/observability/metrics.py`, `backend/tests/test_auth_failure_audit.py` (new),
`backend/tests/test_auth_keys.py` (`:198-212` deleted, `:216-238` deleted and replaced by R9 in the new file), the
slice's `LG-` under `docs/ledgers/`, `docs/roadmap.md` (the `SL-8045` row's closing lines only),
and `docs/INDEX.md` (regenerated). No migration, no `model-schema` change, no contract change: the
401's problem body is unchanged.

**Shared paths for the lead's census:** `backend/src/app/api/deps.py` and
`backend/src/app/observability/metrics.py` with any open slice touching `require_caller` or adding
a metric; `docs/specs/07-platform.md` and `docs/specs/06-governance.md` with any open spec slice
(different rows; a re-merge, not a conflict, unless a row is shared).

**Out of scope:** FR-392's "session anomalies" and the key creation, rotation and revocation
audits (not named by FD-1727); `_select_workspace`'s `403` (authorisation, not authentication);
the alert rule on the new counter (FR-443's observability Work).

## Acceptance Standard

1. **This delta passes the docs checks on its own branch**, check 31's working-id lines excepted:
   `python3 scripts/audit-docs.py` exits 0 apart from them.
2. **DP-1 to DP-4 each carry a ruling**, the maintainer's (by delegation) entry "2026-10-14 12:18:57
   BST" item (1); the `LG-` quotes each before Task 2 is committed.
3. **Spec first:** in the slice PR, `git log --format=%s origin/main..<slice head> -- docs/specs`
   names a commit earlier than every commit touching `backend/src`, and `git grep -n
   "gip_auth_failures_total" <slice head> -- docs/specs/07-platform.md` finds FR-392's amendment.
4. **The reds:** `uv run pytest -q backend/tests/test_auth_failure_audit.py
   backend/tests/test_auth_keys.py` exits 0 at the slice head, and the `LG-` quotes R1, R2, R3, R5,
   R6, R7, R8 (its counter limb), R9 and R10 red on `main` by the causes in the table, and R4's,
   R8's and R10's breakers red.
5. **No in-unit catch remains for the audit claim:** `git grep -n "test_a_failed_authentication_is_audited"
   <slice head> -- backend/tests` prints nothing, and `git grep -n -A3 "unit_of_work" <slice head>
   -- backend/tests/test_auth_failure_audit.py` shows no `pytest.raises` inside a unit.
6. **The write leaves the auth unit:** `git grep -n "audit.record" <slice head> --
   backend/src/app/auth/service.py` prints only the line inside `record_auth_failure`.
7. **The full gate, both halves** (CLAUDE.md §11) at the slice head, in a granted slot; the `LG-`
   names the tree.

## Self-review

- **Coverage of the 12:18:57 rulings (item (1)).** DP-1 (i) → the DP table, Task 3 items 1-2, R1 to
  R3 (a real HTTP `401`, the row survives), Acceptance 6. DP-2 F1 → Task 3 item 1 (no `try/except`,
  counted first), R8, T1's last sentence. DP-3 B → Task 3 items 1 and 3 (`AuthFailureReason`, the
  counter), R5 to R7, R10 (no other label value, no key material, prefix or principal in a label or
  the `WARNING` line), the bearer `INFO` raised to `WARNING` (Task 3 item 1, R7). DP-4 (a) → T1 and
  T2 kept as written, Task 1, Acceptance 3. R9 → R9 produces four events first, then asserts no
  secret; Acceptance 4.
- **No open option remains.** The DP table carries the ruled option only; "Under DP-3 (B)", "for
  the recommended rulings", "PROPOSED" and every reference to a decision-maker `RL-` are gone. The
  rejected options stand at `dc1c9bc6`.
- **Activation.** Need 1 reads "DPs ruled — MET, 12:18:57"; FD-1727's minting, the census and the
  lead's GO remain open. `SL-8045`'s row in `docs/roadmap.md` says the same.
- **Literals.** The `file:line` locators are those read at `a3fc2e8d` (*Premises*);
  `service.py:116-118` (the ruling's locator for the bearer log) was re-read at `a3fc2e8d` for this
  amendment: `:116` is the `_log.info("bearer token rejected", …)` call, `:117-118` the raise.
- **Type consistency.** `AuthenticationFailed`, `AuthFailureReason`, `record_auth_failure` and
  `gip_auth_failures_total` are spelled the same in the DP table, Task 3, R5 to R10 and the
  Acceptance Standard.

## Activation

`SL-8045` is GO-able when all of these hold:

1. **DPs ruled — MET, 12:18:57**: DP-1 to DP-4 and R9, the maintainer's (by delegation) entry
   "2026-10-14 12:18:57 BST" item (1) in `to-lead.md`, quoted under *Authority*.
2. **FD-1727 minted** (D17), so the `LG-` can name what the merge discharges.
3. **The shared-path census** above, against whatever is open at GO.
4. **This delta set `active`** in the slice's activation commit, and the lead's GO. Merged before
   the 4 Nov code freeze (fixed in P2, 11:08:32 item 2).
