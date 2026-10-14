---
id: PL-8044
family: plan
kind: map
title: WK-1178 — the failed-authentication audit (FD 8036) — the refusal's audit row survives the 401, the workspace-less failures counted, and slice SL-8045 — Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: a3fc2e8dd384de6abf909f662f43011b8078fb4e
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-8045]                # FD 8036 is a working id, cited in the body until minted
---

# PL-8044 — WK-1178: the failed-authentication audit (Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5. WK-1178 is the
> standing maintenance Work and has no single map plan; this delta cuts one new slice, `SL-8045`,
> and changes no other slice. It is `draft` while DP-1 to DP-4 are open, and it decides none of
> them. Required sub-skill for the executor: `subagent-driven-development` or `executing-plans`.
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
- **Severity:** no later entry in `to-lead.md` names FD 8036 (`grep -n 8036` over the file prints
  nothing at 12:10 BST). The lead's reservation records it as "proposed HIGH" (`eta.md`,
  "2026-10-14 11:54:58 BST lead: RESERVED working id FD 8036"). This plan assumes no severity; the
  slice is fixed in P2 either way (11:11:50).
- **NFR-519:** released by 11:11:50. This slice names it in no marker and does not regress it: the
  business path keeps `audit.record`'s same-transaction rule unchanged, and DP-2 decides what a
  failing *failure-audit* write does.

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

All four go to the decision-maker; the planner recommends and does not rule. DP-3 changes what
FR-392 means, so it is a spec decision.

| DP | Question | Options | Recommendation | Kind | Blocking? | Resolved by |
|---|---|---|---|---|---|---|
| **DP-1** | How does a keyed-workspace failure's audit row survive the 401? | **(i) Its own committed unit of work.** `authenticate_api_key` stops writing; it raises `AuthenticationFailed`, a `PlatformError` subclass carrying the 401 fields plus `workspace_id` and `reason`. `require_caller` wraps each auth `async with` in `try/except AuthenticationFailed`: **after** the auth unit has rolled back, it opens `database.unit_of_work()`, calls `audit.record` (its transaction rule holds), commits, and re-raises. Costs: one extra transaction per keyed failure, sequential, never two connections at once; the auth function's callers in tests no longer see a row (only the HTTP or `require_caller` shape does, which is the point). No lock-order risk: the auth unit holds no advisory lock when it exits. **(i-a) the same, but `_audit_auth_failure` opens a second session inline** while the auth session is still open: two pooled connections per failure, and the write happens before the rollback it must survive. **(ii) Outbox.** An outbox row in the auth unit is rolled back with it, so it needs its own transaction anyway, which is (i) plus a new Job kind, a handler, a broker hop and a delayed row whose `at` is the worker's time. **(iii) Commit-then-reraise in the same unit.** `require_caller` catches the failure inside the `async with`, lets the unit commit, and raises after. One transaction, no new session. Cost: it commits whatever else the auth unit flushed. At this tree the failure branches flush nothing else (`last_used_at` is set only on success, `:238-239`), but nothing enforces that, and a later write before a refusal would be committed by the refusal. | **(i).** The committed transaction contains the audit row and nothing else, by construction, which no future edit to the auth branches can break. It also keeps `audit.record` exactly as it is (P3), so R2 and NFR-519 are untouched on the business path. (iii) is equally small but rests on an unchecked invariant; (ii) solves nothing (i) does not. | design | **yes** — every red below is written against it | the decision-maker's `RL-` |
| **DP-2** | If the failure-audit write itself fails (database down, constraint), what does the caller get? | **(F1) Fail closed, loud:** the exception escapes; the response is the platform's 5xx problem response, and the error handler logs it. No `try/except` around the write, as `audit.py` `:6-9` requires of every audit write. **(F2) Keep the 401, log `ERROR` and count it:** the refusal is unchanged and the lost row is counted. A swallowed audit failure, which `audit.py` `:6-9` calls "the one outcome the requirement forbids". **(F3) Retry, then F1 or F2.** More code, and the database being down fails the auth lookup itself first. | **(F1).** The request is refused either way, so no access is granted; the only change is that a lost audit row is visible as a 5xx, never silent (NFR-519's word). A caller cannot choose when the database fails, so the 5xx is no oracle for which check failed. | design | **yes** — the response code is a public behaviour | the same `RL-` |
| **DP-3** | Where is a workspace-less failure recorded (malformed key, unknown prefix or wrong secret, archived account with no account row, a rejected bearer token)? | **(A) A platform-scope audit chain.** A nullable or sentinel `workspace_id` and a platform chain. Costs: a migration and FR-417's one-head census; `verify_chain`, export and FR-372 all change; one advisory-lock key serialises every garbage request on the internet behind every other (P3), and the table grows at the attacker's rate. `service.py:90-93` already refuses "inventing one to hold an event". **(B) A labelled counter plus the structured log.** `gip_auth_failures_total{reason}` counts **every** failure, keyed or not; a workspace-less failure also keeps its structured `WARNING` line (trace id, action, reason; the bearer path's `INFO` at `:116` is raised to the same form). A keyed failure also writes its audit row (DP-1). Bounded cardinality, no storage at the attacker's rate. Cost: the durable record of a workspace-less failure is the log's retention and the metric, not the audit export; FR-392 must say so. **(C) B plus a non-chained `auth_failures` table.** A queryable record. Costs: a migration, a retention and purge rule, a size cap or rate limit against flooding, and a decision on which attacker-supplied text may be stored (R3: never a secret). **(D) Split by cause.** A wrong secret against a real prefix is audited in that key's workspace (the key row knows it); the rest go to B. Costs: the write makes "wrong secret" slower than "unknown prefix", recreating the prefix oracle that `:190-192` refuses unless the write leaves the response path; and anyone holding a prefix (audited by prefix, FR-375) can append rows to that workspace's chain at will, contending its lock. **Sub-question, the reason labels:** a closed set, never input: `malformed_key`, `invalid_key` (unknown prefix and wrong secret, one label, as `:190-192` requires), `account_archived`, `key_revoked`, `key_expired`, `environment_not_granted`, `bearer_expired`, `bearer_rejected`. | **(B), with all eight labels**, including `account_archived` and `environment_not_granted`. The counter then totals every 401 `require_caller` raises, so an alert on it covers keyed and workspace-less failures in one series. (B) is the only option that adds no storage an unauthenticated caller can fill. The audit export keeps holding what a workspace owner can act on: failures by a real key of theirs. | design (spec change) | **yes** — the 11:11:50 entry, item 3: "ruled before the build" | the same `RL-` |
| **DP-4** | Where does the clarification land? | **(a) A dated amendment on `07` FR-392** (the rule: scope, own transaction, the counter) **and a dated pointer line on `06` FR-368.** **(b) Amend `06` FR-368 to name failed authentication.** FR-368's sentence is "written in the same transaction as the change (R2)", and a failed authentication has no change and is deliberately written in its own transaction, so the row would contradict its own requirement. | **(a).** FR-392 owns the rule; FR-368 points at it and says why R2's clause does not govern it. | spec placement | **yes** — the slice's first commit applies it | the same `RL-` |

## The spec text (T-text), PROPOSED, applied in the slice's commit, not here

Written for DP-1 (i), DP-2 (F1), DP-3 (B) and DP-4 (a). If the ruling differs, the `RL-` carries the
replacement text and the slice applies that. `<date>`, the FD id and the `RL-` id are filled in the
slice's commit. This plan does not edit `docs/specs/`.

**T1 — a dated amendment appended to `07` FR-392's cell (`docs/specs/07-platform.md:76`):**

> *Amended `<date>` (FD-`<n>`, RL-`<n>`):* **A failed authentication is recorded whether or not it
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

1. Read the `RL-` that rules DP-1 to DP-4 and quote each ruling into the `LG-`.
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
beside it"). Each red's failure on `main` is quoted in the `LG-` by its cause.

| # | Test | Red on `main`, by cause |
|---|---|---|
| R1 | A revoked key → HTTP `401`; the key's workspace then holds **exactly one** `principal.auth_failed` row, `after == {"reason": "key revoked"}`, and its `trace_id` equals the response's `x-trace-id`. | `0 != 1`: the row was flushed in the auth unit and rolled back with the 401 (P2). |
| R2 | The same for an expired key: `after == {"reason": "key expired"}`, response code `API_KEY_EXPIRED`. | `0 != 1`, the same cause. |
| R3 | The same for an archived account (`"service account archived"`) and for a key presented for an environment not granted (`"environment not granted"`), one test each. | `0 != 1`, the same cause. |
| R4 | **Guard:** a valid key → `200`, and the workspace holds **no** `principal.auth_failed` row. | Green on `main` (success never writes). Shown red on a planted breaker that records unconditionally; the `LG-` quotes it. |
| R5 | Under DP-3 (B): a malformed key, an unknown prefix and a wrong secret each → `401`, and `gip_auth_failures_total{reason="malformed_key"}` / `{reason="invalid_key"}` rise by exactly 1 per request (read with `REGISTRY.get_sample_value` before and after); `audit_events` total is unchanged. | `None`: the metric does not exist (P5). |
| R6 | Under DP-3 (B): R1's and R2's requests also raise `{reason="key_revoked"}` and `{reason="key_expired"}` by 1. | `None`, the same cause. |
| R7 | Under DP-3 (B): a rejected bearer token → `401`, `{reason="bearer_rejected"}` rises by 1, and the `app.auth` line is a `WARNING` with `action` and `reason` (Task 0 item 2 decides the harness). | `None`, the same cause. |
| R8 | **Guard**, under DP-2 (F1): with `audit.record` patched to raise, a revoked key → a `5xx` problem response, not `401`. | Green on `main` (the raise escapes the auth unit). Shown red on a planted breaker that wraps the write in `try/except`; the `LG-` quotes it. |
| R9 | `test_no_audit_event_contains_a_key_secret` (`:216-238`) moves to the HTTP shape and first asserts exactly one event, then that the secret is in neither `after` nor `before`. | `0 != 1` (P6: today, in production's shape, its loop runs over nothing). |

Under another DP-3 ruling, R5 to R7 are rewritten from the `RL-` before Task 3, and the `LG-` says
which rows changed.

### Task 3 — the implementation (for the recommended rulings)

1. `backend/src/app/auth/service.py`: an `AuthenticationFailed(PlatformError)` carrying
   `workspace_id: UUID | None` and `reason` (the closed label set). Every branch of P1 raises it
   instead of calling `_audit_auth_failure`; the bearer branch (P4) raises it too. A function
   `record_auth_failure(database, exc)` increments the counter, and then either opens
   `database.unit_of_work()` and calls `audit.record` with today's arguments (`:98-106`, `after`
   unchanged), or logs today's `WARNING`. `_audit_auth_failure` is removed. The module docstring's
   FR-392 sentence (`:8-9`) and `_audit_auth_failure`'s docstring reasoning move to the new function.
2. `backend/src/app/api/deps.py:232-242`: each auth `async with` sits inside `try / except
   AuthenticationFailed as exc: await record_auth_failure(database, exc); raise`, the `except`
   outside the `async with`, so the auth unit has rolled back first.
3. `backend/src/app/observability/metrics.py`: `auth_failures = Counter("gip_auth_failures_total",
   …, ("reason",), registry=REGISTRY)`, in the form of `:66-71`.

### Task 4 — the gate and the closing acts

The full gate, both halves (CLAUDE.md §11), in a granted slot; the `LG-` names the tree. The `LG-`
quotes each red and each breaker by cause, the RL's rulings, and the FD the merge discharges.
`SL-8045`'s closing lines on `docs/roadmap.md` in the slice PR.

## The write set

`docs/specs/07-platform.md` (FR-392's cell only), `docs/specs/06-governance.md` (FR-368's cell
only), `backend/src/app/auth/service.py`, `backend/src/app/api/deps.py`,
`backend/src/app/observability/metrics.py`, `backend/tests/test_auth_failure_audit.py` (new),
`backend/tests/test_auth_keys.py` (`:198-212` deleted, `:216-238` moved to the new file), the
slice's `LG-` under `docs/ledgers/`, `docs/roadmap.md` (the `SL-8045` row's closing lines only),
and `docs/INDEX.md` (regenerated). No migration, no `model-schema` change, no contract change: the
401's problem body is unchanged.

**Shared paths for the lead's census:** `backend/src/app/api/deps.py` and
`backend/src/app/observability/metrics.py` with any open slice touching `require_caller` or adding
a metric; `docs/specs/07-platform.md` and `docs/specs/06-governance.md` with any open spec slice
(different rows; a re-merge, not a conflict, unless a row is shared).

**Out of scope:** FR-392's "session anomalies" and the key creation, rotation and revocation
audits (not named by FD 8036); `_select_workspace`'s `403` (authorisation, not authentication);
the alert rule on the new counter (FR-443's observability Work).

## Acceptance Standard

1. **This delta passes the docs checks on its own branch**, check 31's working-id lines excepted:
   `python3 scripts/audit-docs.py` exits 0 apart from them.
2. **DP-1 to DP-4 each carry a ruling** in the decision-maker's `RL-` before Task 2 is committed;
   the `LG-` quotes each.
3. **Spec first:** in the slice PR, `git log --format=%s origin/main..<slice head> -- docs/specs`
   names a commit earlier than every commit touching `backend/src`, and `git grep -n
   "gip_auth_failures_total" <slice head> -- docs/specs/07-platform.md` finds FR-392's amendment
   (under DP-3 (B)).
4. **The reds:** `uv run pytest -q backend/tests/test_auth_failure_audit.py
   backend/tests/test_auth_keys.py` exits 0 at the slice head, and the `LG-` quotes R1, R2, R3, R5,
   R6, R7 and R9 red on `main` by the causes in the table, and R4's and R8's breakers red.
5. **No in-unit catch remains for the audit claim:** `git grep -n "test_a_failed_authentication_is_audited"
   <slice head> -- backend/tests` prints nothing, and `git grep -n -A3 "unit_of_work" <slice head>
   -- backend/tests/test_auth_failure_audit.py` shows no `pytest.raises` inside a unit.
6. **The write leaves the auth unit:** `git grep -n "audit.record" <slice head> --
   backend/src/app/auth/service.py` prints only the line inside `record_auth_failure`.
7. **The full gate, both halves** (CLAUDE.md §11) at the slice head, in a granted slot; the `LG-`
   names the tree.

## Activation

`SL-8045` is GO-able when all of these hold:

1. **DP-1 to DP-4 ruled** in one `RL-`.
2. **FD 8036 minted** (D17), so the `LG-` can name what the merge discharges.
3. **The shared-path census** above, against whatever is open at GO.
4. **This delta set `active`** in the slice's activation commit, and the lead's GO. Merged before
   the 4 Nov code freeze (fixed in P2, 11:08:32 item 2).
