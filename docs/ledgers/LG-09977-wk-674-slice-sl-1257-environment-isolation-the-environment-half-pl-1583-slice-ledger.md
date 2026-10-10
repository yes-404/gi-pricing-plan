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
4. **STOP:** `backend/tests/test_deployment_route_types.py::test_the_route_set_is_pinned` (WK-674 S2's pin, `len(expected) == 7`) fails on the two new settings routes; the file is outside PL-1583's write set. Reported to the lead with options; untouched.

### Gate

Not yet run.

### Audit

Not yet run.

### Build log

- 2026-10-10: worktree `.claude/worktrees/sl-1257`, branch `sl-1257-wk674-s3-env`, from `14fa6fb3`. First commit: PL-1583 `draft → active`, SL-1257 `draft → active`, this ledger.

## PRs

None yet.
