---
id: LG-9977
family: ledger
title: WK-674 slice SL-1257 — environment isolation, the environment half (PL-1583), slice ledger
status: active
created: 2026-10-10
owner: executor
tree: 14fa6fb3d5b7097a829343e38cb5f20afbd0d2e2
phase: P2
work: WK-674
slice: SL-1257
plans: [PL-1583]
corrected_by: []
relates: [PL-1583, PL-1342, RL-1311, RL-1347, RL-1445, FD-1320, FR-430, FR-431, FR-446, FR-447, FR-452, NFR-499]
---

# LG-9977 — WK-674 slice SL-1257: environment isolation, the environment half

*(LG-9977 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-wk674s3` from PL-1583, base `origin/main` `14fa6fb3d5b7097a829343e38cb5f20afbd0d2e2`.
Times are BST (`TZ=Europe/London date`) unless marked.

**GO:** `to-lead.md` "2026-10-10 21:38:39 BST — DISPATCH GO: SL-1455 (Task 0; FD-1411's NFR-489 HTTP remedy) and WK-674 S3 (PL-1583); OP-1455-M1/M2/M3; the register :293 record", item 6: "GO WK-674 S3 (PL-1583), needs 1–5 MET as quoted. Conditions: re-point the alembic down_revision at merge to main's head then (b8d2f4a6c0e1, or d4e81b7a2c95 if WK-675 S4 merges first), with heads = 1 and upgrade/downgrade run at the head. Real Redis for the RL-1347 cases (Redis down = STOP). The contract change regenerates on the merge base. SL-1600's errors.py adjacency: the second merger re-reads. It serialises with SL-1455 on score.py, deps.py, auth/service.py and main.py's lifespan, in item 4's order." Item 4 (OP-1455-M3 (a)): "WK-674 S3 merges BEFORE SL-1455's Task 4 sweep, so the sweep measures /score with the Redis limiter, the exit-tree path. Trigger for (b): if S3 is not merged when SL-1455's Tasks 1–3 are ACK-ready, SL-1455 sweeps then, and S3's ACK re-runs the 200 rps arm pair (×3) and shows it in budget."
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's row is `#### SL-1257 — Slice 3: environment isolation (FR-430, FR-431, register F54 and F48, NFR-496 prod-sampling limb)` in `docs/roadmap.md`, under PL-1583 (which supersedes PL-1342 for the environment half). Requirement ids covered: FR-430, FR-431, FR-446, FR-447, FR-452 (the scoring limb only), NFR-499 (the per-client rate-limit limb); register F54, F48; FD-1320 (discharged at merge). Not in scope: the ladder half (SL-1345, closed), FR-452's management-API limb (SL-1258), FR-270/271 flags (Slice 6).

**DP rulings, verbatim** (`to-lead.md`, "2026-10-10 03:23:31 BST — R1 CONFIRMED (my 03:10:58 premise corrected); PL 9456 DPs ruled; R2 (§12 row 2) goes to the USER"): "DP-S3E-1 (b) additive (`keys` always; `key` only when exactly one Environment is granted; no break to the 9 test files or PL-1544 S1). DP-S3E-2 (a), rotation always names its Environment (FR-430 literally). DP-S3E-3 (a), S3's 07 commit adds the dated pointer on FR-452 to SL-1258 / R4.1. All three ADOPTED".

**Lane / serial sets (activation need 5), from the planner's go-request draft §3**, read at origin/main `31b88780`:

| In flight | Intersection | Rule | Result |
|---|---|---|---|
| SL-1600 `sl-1600-input-free-error` | `errors.py`: imports, a NEW function `_field_error_message` after `_handle_platform_error`, one line in `_handle_validation_error` | name-disjoint only if none edits `PlatformError` or the handler | name-disjoint, line-adjacent; the second to merge re-reads; `merge-tree` rc checked at its turn |
| WK-675 S3 `sl-1557-wk675-s3` | none (specs `00`/`03` only) | — | concurrent OK |
| WK-675 S4 `sl-1559-wk675-s4` | `db/models.py` (append), `migrations/versions/` (new `d4e81b7a2c95` after `b8d2f4a6c0e1`) | append / new file: exempt; re-point `down_revision` at the second merge; `alembic heads` = one | concurrent OK |
| SL-1455 (PL-1454, not started) | `api/score.py`, `api/deps.py`, `auth/service.py`, `main.py` lifespan | RL-1263 item 4: serialise | SERIALISE (S3 first, per the GO item 4) |
| G2 chain | behavioural only (PL-1544 S1 reads `key`) | — | concurrent OK; assert a one-Environment create still returns `key` |

### Task list

Premise i (Alembic head) re-derived at base `14fa6fb3`: one head, `b8d2f4a6c0e1` (54 revisions; the revision no `down_revision` names).

- [x] Task 0: preconditions, premises a–j at this tree (a–i hold at `14fa6fb3`; head `b8d2f4a6c0e1`) — `cfa62a66`
- [x] Task 1: spec (`07` §4.2–§4.4, §5.1, §5.2, FR-452 pointer) — `1586b7db`
- [x] Task 2: `SettingSource.ENVIRONMENT_SETTING` — `c2b9dc8f`. Red: `AttributeError: type object 'SettingSource' has no attribute 'ENVIRONMENT_SETTING'` (`packages/model-schema/tests/test_settings.py`, rc 1); green rc 0; `generate-contracts.py --check` rc 0; `backend/tests/test_contracts.py` 156 passed.
- [~] Task 3: migration `c5a91e7d3b26` (down_revision `b8d2f4a6c0e1`), `SettingScope`, `validate_setting_overrides`, lifespan hook — `87dc0fc3`. Non-DB tests red (collection `ImportError: cannot import name 'SettingScope'`), then green (7 passed). **Owed for the slot:** the three lifespan tests, migration round trip, `api_keys` unchanged.
- [~] Task 4: key set per Environment — `7e7a2928`; Environment-setting PUT/GET, audit, trace-sampling call site — `37fd9e90`. **Owed for the slot:** everything DB-backed in `test_settings_environment.py`, `test_api_service_accounts.py` (new cases + the 3 edited rotate calls), `test_score.py` (edited multi-environment test, new parametrised sampling test), `test_environments.py` (edited rotate call).
- [~] Task 5: `platform/rate_limit.py`, `RateLimiter`, header carrier on `PlatformError`, `gip_rate_limit_unenforced_total`, lifespan Redis client (50 ms timeouts), `rate_limit_rps` on identity and `Caller`, 429 in `/score` OpenAPI, contracts regenerated — `aafa2b36`, contracts commit after. **Owed for the slot:** `backend/tests/test_score_rate_limit.py` (cases 1–8; case 9 with `GIP_MEASURE_RATE_LIMIT=1`).
- [ ] Task 6: gate and close.

**Deviations (named, not silent).**
1. Tasks 4 and 5: the production code for the key set, the header carrier and the limiter was written before its DB/Redis-backed test, and those tests are not yet run. The red proofs are owed in the slot: run each new test file at the parent version of the touched source file (`git show origin/main:<path>`), quote the failing assertion, restore.
2. `scoring.default_client_rate_limit_rps` is declared in Task 3's commit, not Task 5's, so the scope assertion (exactly two workspace-or-Environment keys) is green at one commit.
3. `ConfigInvalidError` (existing) is the startup refusal; the `_parse_env` detail no longer echoes the raw value or `str(exc)`.
4. **Route pin, resolved (A)** by the maintainer, `to-lead.md` "2026-10-10 23:55:18 BST — WK-674 S3 @9e14e79f: (A) ADOPTED for the route pin; the red proofs owed in the slot". `backend/tests/test_deployment_route_types.py` joined the write set for the pin only: the seven S2 rows stay exact, `SETTINGS_ROUTES` holds the two settings routes (citing PL-1583 :68 and `07` :319–320), and the assert is `live == union` with `len(union) == 9`. Red once, planted: with the `GET` row deleted from `SETTINGS_ROUTES` the pin fails (`assert 8 == 9`, rc 1); restored, rc 0 (`-k route_set_is_pinned`, small-test slot).

### Gate

**Run 1, head `ae6d9fda`, gate-1, 10:41–11:32 BST (2026-10-11): INVALID.** Script `~/gi-pricing-plan.local/handover/sl1257-slot.sh`, output `~/gi-pricing-plan.local/handover/sl1257-slot.out`, stage logs `/tmp/tmp.2TNUHpAE0d`. Cause: the script ran `alembic -c backend/alembic.ini` but `alembic.ini` is at the repository root (rc 255, "No 'script_location'"), so the per-worktree database cloned from the template was never migrated to this tree. Every DB-backed result is void: pytest 167 failed / 12 errors, none classifiable as a code red (missing-table class). The script is fixed (alembic run from the root via `uv run --directory`, plus `upgrade head` after `createdb`; `alembic heads` = `c5a91e7d3b26`, one head). A re-run at the same head is queued by the lead. **Standing preflight added** (to-lead 2026-10-11 item 3): before any pytest stage the slot script aborts with rc 4/5/6 and the reason unless postgres, redis and minio report healthy, `alembic upgrade head` exits 0, and `alembic heads` shows exactly one head, `c5a91e7d3b26`. Checked by `bash -n` and, against the dev stack, the three health states and the head value; the abort branches have not been exercised on broken input.

Valid facts from run 1: ruff, mypy, import-linter, req-coverage and contracts rc 0. audit-docs rc 1 = check 32 (LG-9977 unresolved in INDEX) and check 39 (INDEX stale), both mint artefacts. Frontend: install, generate, lint, type-check, build rc 0; fe_test 3 failures, all in `DagDesigner.test.ts` (FD-1611, WK-675's, not this slice's). Case 9 (`GIP_MEASURE_RATE_LIMIT=1 -k case_9`, 1 of 10 collected): calls=10000, p50 0.523 ms, p99 1.420 ms. T5 red against parent source (score, deps, auth/service, errors, main at `origin/main`): 9 errors `'State' object has no attribute 'rate_limiter'` (valid). T4 red against parent `service_accounts.py`: `test_key_lifecycle_is_audited_by_prefix_never_by_value` failed (partly valid: unmigrated database).

### Audit

Not yet run.

### Build log

- 2026-10-10: worktree `.claude/worktrees/sl-1257`, branch `sl-1257-wk674-s3-env`, from `14fa6fb3`. First commit: PL-1583 `draft → active`, SL-1257 `draft → active`, this ledger.

## PRs

None yet.
