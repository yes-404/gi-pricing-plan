---
id: PL-9456
family: plan
kind: leaf
title: WK-674 Slice 3 — Environment isolation, the environment half (FR-430, FR-431, FR-446, FR-447, FR-452 scoring limb; register F54 and F48): superseding leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-10
owner: planner
tree: 3519a919e30aa6993d40b22df212dd57bbd4a685
phase: P2
work: WK-674
slice: SL-1257
supersedes: [PL-1342]
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1537, PL-1348, PL-1544, RL-1311, RL-1347, RL-1184, RL-1236, RL-1263, RL-1445, RL-1301, FD-1320, SL-1256, SL-1345, SL-1258]
---

# PL-9456 — WK-674 Slice 3 — Environment isolation, the environment half: superseding leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package`, `python-test` and `test-driven-development` (every task), `fastapi-service` (Tasks 3–5), `dev-commands` (the migration, the gate and the slot wrapper) and `git-hygiene`. It is spawned from `.claude/roles/executor.md` and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Authority, and what this plan replaces

- **The ruling:** the maintainer's entry "2026-10-10 03:10:58 BST — RULING: WK-674 S3 = (a), a superseding leaf plan for the environment half, drafted now; plus a deploy-path critical-path statement. A-3 author start noted", item 1: "An opus planner drafts the superseding leaf plan for SL-1257's environment half (FR-430, FR-431, F54/F48 as still applicable). It takes account of the SL-1345 ladder carve-out and the FR-452 split, quotes the current spec text, and is in L5 form (relates: the WK-674 plan; supersedes: PL-1342 for that half). Draft branch only; it rides a docs batch. Its DPs come to me."
- **Why a leaf plan under L5.** `docs/plans/README.md:17-21` says that from the 2026-10-08 11:51:58 BST entry "no per-slice leaf plan is filed after that entry". This slice was never dispatched. The entry "2026-10-08 11:53:19 BST — L5 transition RULED: per-slice plans drafted before 11:51:58 MINT AS-IS" kept `PL-1342` (quoted at `PL-1537:64-67`). The 03:10:58 ruling replaces that plan by this one, as a replan (`.claude/skills/writing-plans/SKILL.md:30-37`: "a true replan still uses `supersedes:`"). The slice still closes under L1 (a'): one PR, one `LG-`, and the `SL-` status line.
- **What is superseded.** `PL-1342` (draft, `tree: 11c76b6c`) had two halves. **The ladder half** (its Acceptance 10, Task 6, DP-S3-1, premise g) was carved out to `SL-1345` on "2026-09-30 23:57:25 BST — DECISION on the S3 halt: (A) carve the ladder half into its own slice …" (`docs/roadmap.md:1016`). It was delivered under `PL-1348`, and `SL-1345` is `closed` (`docs/roadmap.md:1028`). That half is not this plan's and is not restated. **The environment half** (its Acceptance 1–9, 11, 12 and Tasks 0–5, 7) is restated here, re-derived at `3519a919`. Where this plan and `PL-1342` differ, this plan governs. `PL-1342` is frozen and is not edited; it takes `superseded_by:` at this plan's mint (`document-ids.md` §1.5).

## Goal

Make each Environment **its own**. A Service Account holds one key per granted Environment. A value set for one Environment changes no other. `/score` callers are rate-limited by a counter that every replica shares. An override that cannot be honoured stops the process at startup.

**Architecture.** The Settings resolver gains an **Environment setting** layer between the process override and the workspace setting, for keys that declare it (`RL-1311`). Its rows are keyed by `EnvironmentRow`'s id (`backend/src/app/db/models.py:2415`). They are written by an audited `PUT /api/v1/environments/{slug}/settings`, guarded by `admin:manage_settings`. Key issuance and rotation act per Environment. A rate-limit module counts `POST /api/v1/score` in Redis, exactly as `RL-1347` rules: per (Environment, Principal), a fixed one-second window, fail open. A new startup check validates every `GIP_SETTING_*` override against `REGISTRY` (FD-1320).

**Tech Stack:** Pydantic v2, FastAPI, SQLAlchemy 2.x async, Alembic, `redis.asyncio` (the existing tenant Redis, `config.py:124` `redis_url`), Prometheus client (existing), pytest. No new dependency, and no change to `uv.lock` or `pyproject.toml`.

**Spec (quoted verbatim at `3519a919`):**
- `07` §3.5 **FR-430** (`07-platform.md:141`): "Environments have independent Service Account scopes, rate limits, and monitoring configuration. A `uat` key can never score against `prod`. **Amended 2026-09-28 (`RL-1184` E7): one key per granted environment.** A Service Account granted several environments (FR-389) holds one key for each. Creation mints one key per granted environment, and rotation and revocation act on the key of one named environment. A leaked key is then confined to its own environment, the boundary ADR-710 draws. Owner: WK-674. Register row F54 records that today only the first granted environment gets a key."
- `07` §3.5 **FR-431** (`:142`): "Environment configuration (rate limits, sampling rates, feature flags) is a Setting resolved by the precedence in §3.8 and is audited on change."
- `07` §3.8 **FR-446** (`:172`), its amendment: "**Amended 2026-09-30 (`OQ-1235`, `RL-1311`): four layers.** The precedence is **process environment variable (`GIP_SETTING_<KEY>`) → Environment setting → workspace setting → platform default**. An Environment setting is a value for one Environment (FR-428) and applies to requests tagged with that Environment. Each setting declares which levels it may be set at: workspace only (the default), workspace or Environment, or Environment only. A write at a level the setting does not permit is refused with `SETTING_INVALID`. **The process environment variable never supplies an Environment-only setting:** one present at startup prevents startup with a message naming the key (FR-447), and one seen at resolve is skipped and logged as a warning. … An Environment setting is validated at write against the setting's declared type and constraints, as a workspace setting is, guarded by `admin:manage_settings`, and audited on change with the environment, key, old value and new value (FR-431). Inspection takes an optional Environment and reports every layer's candidate. Owner: WK-674 Slice 3."
- `07` §3.8 **FR-447** (`:173`): "Settings are typed and validated at startup; an invalid setting prevents startup with a clear message rather than failing at first use."
- `07` §3.9 **FR-452** (`:183`), the scoring limb as `RL-1347` amended it: "`POST /api/v1/score` counts requests in a shared Redis counter, one per (Environment, Principal) per fixed one-second window. The Environment is the one the presented key was verified for, and it is empty for a bearer caller. … The limit is the Service Account's own `rate_limit_rps` when it is set. Otherwise it is the Setting `scoring.default_client_rate_limit_rps`, resolved by §3.8 with the caller's Environment and declared for workspace or Environment scope (FR-446; FR-431). That Setting is unset by default. With no limit, the request is admitted without a counter call. Over the limit, the request is refused with `429 RATE_LIMITED` and `Retry-After: 1`, after authentication and authorisation and before any scoring. If the counter is unavailable, the request is admitted (fail open), logged, and counted on `gip_rate_limit_unenforced_total` by Environment. `/score/batch` and `/score/compare` are not counted. The management-API limit is not delivered by this clause and has no owner yet."
- `03` §9 **NFR-499** (`03-rating-engine.md:1404`), the limb this slice serves: "the scoring API authenticates per Consumer System with scoped credentials and per-client rate limits".
- Shapes and interfaces this slice amends: `07` §4.2 (`:245-265`), §4.3 (`:267-281`), §4.4 (`:283-299`), §5.1 (`:313`, `:316-318`), §5.2 (`:390-391`).

## Status

Drafted 2026-10-10 against the tree above under **working id 9456**, which the lead reserved after free-checking it ("0 on all origin refs + eta.md", the lead's brief `brief-planner-wk674s3-replan-2026-10-10.md`). The id is minted in the docs batch that carries this plan. Draft branch `draft/pl-9456-wk674-s3-env`, no PR.

**Activation needs, in order.** Each is a command with an expected output, run at the dispatch tree.
1. **This plan minted, and `PL-1342` carries `superseded_by:` it.** `git grep -n 'superseded_by' -- docs/plans/PL-01342-*.md` prints this plan's minted id.
2. **`SL-1256` and `SL-1345` closed.** For each, `awk '/^id: SL-1256$/,/^status:/' docs/roadmap.md | tail -1` (and the same for `SL-1345`) prints `status: closed`. Both are met at `3519a919` (`docs/roadmap.md:994-996` and `:1028`).
3. **`RL-1311` and `RL-1347` on main.** `ls docs/rulings/RL-01311-* docs/rulings/RL-01347-*` lists two files. Met at `3519a919`.
4. **DP-S3E-1 and DP-S3E-2 ruled** (the table below), each quoted in the dispatch record. DP-S3E-3 is non-blocking.
5. **A lane under `RL-1445`.** The write-set check below has been re-run against every branch in flight at the GO, and its result is quoted in the GO.
6. **The lead's GO.**

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means the failing run is quoted in the `LG-` with its failing assert line **and the cause the step predicts**. A failure for any other cause is a plan defect, not a pass (README convention 2). "Red on broken input" means: the guard is green; it is then deliberately disabled; the test is shown red with the predicted cause; and the guard is restored.

1. **Spec first, through `spec-change`.** `python3 scripts/audit-docs.py` exits 0 on the spec commit. Each `07` edit is a dated note, and no example block is rewritten (the precedent is `07:261-265`, "The example above is not rewritten"):
   - §4.3: a Service Account carries a **key set, one per granted Environment**, each key with its own `environment`, dates and rotation state. FR-430 is cited as `RL-1184` E7 amends it. The creation response's shape is as DP-S3E-1 rules.
   - §4.4: the resolution's `candidates` gain an `environment_setting` source (`RL-1311` item 2), and the request takes an optional Environment.
   - §4.2: the `settings` object (`:255-257`) is replaced by a pointer to the Environment-setting rows of §4.4. Its keys `trace_sampling_rate`, `rate_limit_rps` and `shadow` were example names. The registry's names are the contract: `rating.trace_sample_rate` (`backend/src/app/platform/settings.py:196`) and `scoring.default_client_rate_limit_rps` (`RL-1347` rule 2).
   - §5.1: the `PUT /api/v1/environments/{name}/settings` row (`:313`) becomes `{slug}` (the 2026-10-03 note at `:264`: "every `{env}` path parameter … name[s]" the slug). A `GET /api/v1/environments/{slug}/settings` row is appended (effective values with every candidate). The rotate row (`:317`) takes the Environment it rotates, as DP-S3E-2 rules.
   - §5.2: `get(key, workspace_id)` (`:391`) gains `environment: str | None = None`.
   - FR-452: the management-API limb gets the pointer DP-S3E-3 rules. FR-430, FR-431, FR-446 and FR-447 are **not** reworded. If one needs rewording, the executor stops and reports.
2. **Contract.** `SettingSource.ENVIRONMENT_SETTING = "environment_setting"` is added to **`model_schema`'s** enum (`packages/model-schema/src/model_schema/settings.py:27-32`, today `ENV`, `WORKSPACE`, `DEFAULT`), between `ENV` and `WORKSPACE` (`RL-1311` item 2). The backend's other enum (`backend/src/app/config.py:41-46`, `ENVIRONMENT = "environment"`) is not touched, and no new code imports it. `git grep -n -E 'from app\.config import .*SettingSource' -- backend/src/app/platform backend/src/app/api` prints nothing new. `uv run python scripts/generate-contracts.py --check` exits 0. The contract guard passes, and its output is quoted.
3. **Migration (FR-417).** One revision. Its `down_revision` is the head at the executor's tree: `f3a7c1d9e2b4` at `3519a919` (`backend/migrations/versions/f3a7c1d9e2b4_rate_table_diff_cells_job_kind.py:23`), re-pointed at merge (`RL-1263`). It creates `environment_settings`: `environment_id` (an FK to `environments`), `key`, `value` JSONB, `updated_by`, `updated_at`, and a unique `(environment_id, key)`. The round trip `upgrade` / `downgrade -1` / `upgrade` exits 0. **Existing keys are not backfilled**, because a secret is shown once (FR-389). An account granted several Environments before this slice keeps its one key, and gets the others at its next rotation of each Environment. A test asserts that existing `api_keys` rows are unchanged by the upgrade.
4. **One key per granted Environment (FR-430, register F54).** Each case is red first, appended to `backend/tests/test_api_service_accounts.py` (mirror its fixtures):
   - Creating an account granted `dev` and `uat` mints **two** keys, one per Environment, and the response carries each secret once (shape per DP-S3E-1). Predicted red: one key, for `environments[0]` (`backend/src/app/api/service_accounts.py:194`).
   - Rotation names one Environment and acts on **that** key only. The other key's `expires_at` is unchanged. Predicted red: `:261` rotates `account.environments[0]`, and the route takes no Environment (`:232-235`).
   - Revoking by prefix revokes one key. The account's other key still authenticates.
   - **A key the platform issued for `dev` is refused once `dev` leaves the grant.** The test reaches `ENVIRONMENT_SCOPE_DENIED` (`backend/src/app/auth/service.py:217`, `:224`) with that key. No route narrows a grant at `3519a919` (the only writer of `environments` is `service_accounts.py:187`), so the test narrows the grant through the session and says so. In the same test, a `dev` key scores against `dev`'s live Deployment and never `uat`'s, when the two differ (`score.py:186-194`).
5. **The Environment-setting layer (`RL-1311` items 1, 2, 3, 5).** Each case is red first, in a new `backend/tests/test_settings_environment.py`:
   - `SettingDefinition` (`platform/settings.py:44`, no scope field today) gains a scope: workspace only (the default), workspace or Environment, or Environment only. `rating.trace_sample_rate` and `scoring.default_client_rate_limit_rps` are declared workspace-or-Environment. No other registry key changes scope.
   - A key set for `uat` changes the effective value in `uat` only. Its resolution reports `environment_setting`, and `prod` still reports `workspace` or `default`.
   - For a workspace-or-Environment key, `GIP_SETTING_<KEY>` wins over an Environment setting in every Environment.
   - A workspace-only key written for an Environment is refused with `SETTING_INVALID`. An Environment-only key written at workspace level is refused with `SETTING_INVALID`.
   - An Environment-setting write validates with the key's `coerce` first. An ill-typed value and an out-of-range value are each refused with `SETTING_INVALID`, and nothing is written.
   - With no Environment in the call, the Environment layer is skipped. Inspection with an Environment reports every candidate, the Environment setting included.
   - `PUT /api/v1/environments/{slug}/settings` uses the `ManageSettings` dependency (`admin:manage_settings`, `RL-1236` DP-D; mirror `backend/src/app/api/settings.py:72-78`). A caller without it gets 403 `PERMISSION_DENIED`. The `GET` uses `ReadSettings`, as `api/settings.py:63-64` does.
   - **Audit (FR-431).** Every Environment-setting write commits with one Audit Event that names the Environment, the key, and the old and new values. Mirror the `audit.record` call of `api/settings.py:90-100` (action `setting.updated`), with the Environment added. Red on broken input: with that `audit.record` call patched to a no-op, the test is red.
   - **The monitoring-configuration limb** (DP-S3-3, ruled (a) by the maintainer on 2026-09-30 15:13:26 BST, quoted at `PL-1342:407`): `score.py:485-486` resolves `rating.trace_sample_rate` with `caller.workspace_id` only. It passes `caller.environment` after this slice. The behavioural case: with `uat`'s rate `1.0` and the workspace rate `0.0`, a scored quote in `uat` is sampled. Predicted red: it is not, because the workspace rate is read. Red on broken input: with the key forced to workspace-only scope and the value written at workspace level, `prod` changes too.
6. **Environment-only keys and the process layer (`RL-1311` item 3a).** Red first, with a **test-registered** Environment-only key. (Slice 6 declares the real FR-270 and FR-271 flags: `PL-1537` R6.1.) A `GIP_SETTING_<KEY>` present at startup stops the process with a message naming the key and the rule. A variable set after startup is skipped at resolve: the source stays `environment_setting` or `default`, and a warning is logged. With the refusal and the skip removed, the flag resolves on in every Environment, and the tests fail.
7. **FR-447's override validation (FD-1320).** The register's event, verbatim (`docs/findings/register.md:222`, Decision cell): "Event: Slice 3's merge, its red-first acceptance being an unknown key, an ill-typed value and an Environment-only key each refusing startup in the real `create_app` lifespan with the database." Each of the three is red first, through the real `create_app` lifespan with the database, not `load_settings()` alone. The check is new. At `3519a919` the only reader of `setting_overrides` is `_env_candidate` (`platform/settings.py:331-332`), and the lifespan (`main.py:79-92`) runs only the round-trip and tenant checks. The check is a function in `platform/settings.py`, called from the lifespan. It reads `Settings.setting_overrides` (`config.py:241-249`) against `REGISTRY` (`platform/settings.py:110`) and coerces each value with its definition's `coerce`.
8. **The scoring rate limit (FR-452's scoring limb, NFR-499, register F48; `RL-1347` rules 1–6).** `RL-1347`'s Acceptance cases 1–9 hold, each with the red its text names. They run against a real Redis (CI's Redis 7, the local compose Redis). Cases 1 and 2 use two `create_app` instances sharing one Redis, with the clock injected. Case 9 (the limiter's p50 and p99 over 10,000 calls) is **measured and quoted**, not gated, in the slot of item 9. Names: `rate_limit_rps` is carried on `AuthenticatedIdentity` (`auth/service.py:40`) and on `Caller` (`api/deps.py:60-70`). `PlatformError` (`errors.py:423`) gains a response-header carrier, which its handler (`errors.py:595`) writes. The Redis client is built in the lifespan (`main.py:79`) and stored on `app.state` beside `:175-182`. The counter `gip_rate_limit_unenforced_total` goes in `observability/metrics.py`. 429 goes in `/score`'s OpenAPI responses, and the contract is regenerated (FR-451). **The management-API limb is not built here** (`PL-1537` R4.1: Slice 4 reuses this slice's counter "under a separate key and limit"). So the module takes the key's route class as a parameter, and this slice passes only `score`.
9. **The gate, in a gate slot.** Every run of a whole test directory or package suite, and the gate itself, uses the dev-commands slot wrapper verbatim, plus `LOKY_MAX_CPU_COUNT=4`. Report `uptime` at each grant. Only named single test files or node ids are exempt. The full two-half gate (`CLAUDE.md` §11) exits 0, with every rc, the `N passed` line and `HEAD` quoted against main's.
10. **Close (L1 (a')).** One PR carries the code, tests, spec change, the `SL-1257` status line and one `LG-`, whose scope section quotes this plan's Scope. The maintainer's MERGE-ACK names the PR's full head SHA. The slice's clean audit is filed. FD-1320 is discharged at the merge.

## Global Constraints

- **Money is integer minor units** (`CLAUDE.md` §7). Nothing here touches a premium.
- **`pricing-core` gains no FastAPI, SQLAlchemy or Redis import** (`CLAUDE.md` §2). This slice edits no `pricing-core` file.
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2). `SettingSource` is declared once, in `model_schema`.
- **The migration chain has exactly one head** (`07` FR-417).
- **Do not build ahead of the phase** (`CLAUDE.md` §9). No monitor (WK-687), no FR-270 or FR-271 flag (Slice 6), no management-API limit (Slice 4).
- **An Environment-only key is never supplied by the process layer** (`RL-1311` item 3a).
- **Quote inputs are never logged** (`03` NFR-499). The rate-limit warning carries the error type and the Environment only (`RL-1347` rule 5).

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `07` §3.5 | FR-430 | Whole: one key per granted Environment (F54); independent rate limits (with FR-452); the monitoring-configuration limb (DP-S3-3 (a)) |
| `07` §3.5 | FR-431 | Whole: Environment configuration as a Setting, resolved by §3.8, audited on change |
| `07` §3.8 | FR-446 | The Environment-setting layer and the scope rule, as `RL-1311` amended it |
| `07` §3.8 | FR-447 | The override half: FD-1320's startup validation (Acceptance 7) |
| `07` §3.9 | FR-452 | The scoring limb only (`RL-1347`). The management-API limb is `SL-1258`'s (`PL-1537` R4.1) |
| `03` §9 | NFR-499 | The per-client rate-limit limb (register F48) |

**Carried obligations placed here:** register F54 (Acceptance 4), register F48 (Acceptance 8), `RL-1311` items 1, 2, 3, 3a and 5 (Acceptance 2, 5 and 6), FD-1320 (Acceptance 7), and `RL-1347` in full (Acceptance 8).

**Not in this slice, each with its place:**
- **NFR-496's prod-sampling limb and FR-248** are delivered, not open. `03:1401` carries "*(Amended 2026-10-01, `PL-1348` (SL-1345) …)*: … The check runs on every scored quote in every Environment and is never sampled (FR-248)". In the code, `reconcile_ladder` (`packages/pricing-core/src/pricing_core/rating/ladder.py:404`) is called at `rating/score.py:897`, and `ladder_check_version` is stamped at `:868`. The `SL-1257` title still names that limb (`docs/roadmap.md:998`). The Hand-off routes the annotation.
- **FR-452's management-API limb:** `SL-1258` (`docs/roadmap.md:1020`).
- **FR-270 and FR-271 and their flags:** Slice 6. **Monitors:** WK-687. **The switch:** Slice 5.
- **A route to change an account's granted Environments:** none exists, and FR-430 does not ask for one.

### What changed from `PL-1342`'s environment half

| `PL-1342` | Here | Why |
|---|---|---|
| Acceptance 10, Task 6, DP-S3-1, premise g (the ladder) | removed | `SL-1345` (closed) delivered them |
| DP-S3-2 open | **ruled**: `RL-1347` in full (Acceptance 8) | `docs/roadmap.md:1018` |
| FR-452 not in scope | its scoring limb in scope, its management limb named as `SL-1258`'s | `RL-1347`; `PL-1537` R4.1 |
| FD "9881", working id | **FD-1320** | minted (`register.md:222`) |
| `test_service_accounts.py` | `backend/tests/test_api_service_accounts.py` | the file at `3519a919` |
| `service_accounts.py:180`, `:246`; `score.py:399-400` | `:194`, `:261`; `score.py:485-486` | re-derived after S2 |
| Alembic head `d7e2a9b5c418` | `f3a7c1d9e2b4` | re-derived |
| the creation response and rotate's Environment unaddressed | DP-S3E-1 and DP-S3E-2 | found at this tree (premise a) |

### Premises re-derived at `3519a919`

| # | Premise | Evidence (`git -C <worktree> grep -n …` unless stated) | Holds? |
|---|---|---|---|
| a | Creation and rotation each mint one key, for the first Environment | `service_accounts.py:194` `generated = generate_key(body.environments[0])`; `:261` `generate_key(account.environments[0])`; rotate takes `account_id`, `caller`, `database`, `overlap_days` (`:232-235`); revoke `:290-296`; `CreatedServiceAccount.key: str` (`:94-100`); `RL-1301` A.6's check at `:128-133`, called at `:166` and `:245` | yes: F54 reproduces |
| b | The grant check exists; no route narrows a grant | `auth/service.py:217` `if parsed.environment not in set(account.environments):`, `:224`; the only writer of `.environments` is `service_accounts.py:187` | yes |
| c | Three resolver layers, no scope | `platform/settings.py:3` (docstring), `:359` `_resolution` (ENV → WORKSPACE → DEFAULT), `:292-293` `resolve(session, settings, workspace_id, key)`, `:44` `SettingDefinition` (fields `key, type, default, description, constraints, feature_flag`); `REGISTRY` `:110`, 16 keys by `grep -c -E '^\s+key="' backend/src/app/platform/settings.py` | yes |
| d | Two `SettingSource` enums | `model_schema/settings.py:27-32`; `backend/src/app/config.py:41`, `:44` | yes |
| e | No startup validation of overrides | readers of `setting_overrides`: `platform/settings.py:332` only (`git grep -n -E 'setting_overrides\|GIP_SETTING' -- backend/src`); lifespan `main.py:79-92` | yes: FD-1320 reproduces |
| f | No rate limiter | `git grep -n -E 'rate_limit_rps\|RATE_LIMITED' -- backend packages`: migration `6db3b9464e98_…py:46`; `service_accounts.py:65`, `:90`, `:113`, `:189`; `db/models.py:436`; `errors.py:66`; `backend/tests/test_model_jobs.py:967`, `:978`, `:1000` (an upstream provider's 429) | yes: F48 reproduces |
| g | Environments exist; no settings rows or route | `db/models.py:2415` `EnvironmentRow`, table `environments`; routes `api/environments.py:39-89` (GET, POST, PATCH `/{slug}`, POST `/{slug}/retire`); `git grep -n -E 'environment_settings\|EnvironmentSetting' -- backend/src` prints nothing | yes |
| h | Trace sampling ignores the Environment | `api/score.py:485-486` `settings_service.resolve(session, settings, caller.workspace_id, "rating.trace_sample_rate")`; `caller.environment` comes from the key (`auth/service.py:238`) | yes |
| i | Alembic head | `f3a7c1d9e2b4` (`…/f3a7c1d9e2b4_rate_table_diff_cells_job_kind.py:23-24`): the one revision that no file names as `down_revision`, with both quote styles matched | re-derive at the executor's tree |
| j | The ladder half is delivered | `rating/ladder.py:404`, `rating/score.py:868`, `:897`; `model_schema/scoring.py:201` `ladder_check_version` | yes: out of scope |

The executor re-reads each premise at its own tree and stops on any that no longer holds.

### Write set and contention (`RL-1263` as amended by `RL-1445`)

`RL-1445` (2026-10-05): at most three build slices at once, one full gate at a time. Same-Work concurrency is allowed only with resolved file sets and no plan dependency. Inside WK-674 this slice runs alone: `SL-1258` depends on it (`PL-1537` row 1). The in-flight branches below were read at 2026-10-10 03:16 BST with `git diff --name-only origin/main...<branch>`, filtered to this write set. `gh pr list --state open` printed 0 PRs.

| Path | This slice | In flight at `3519a919` | Rule |
|---|---|---|---|
| `docs/specs/07-platform.md` §4.2–§4.4, §5.1, §5.2, FR-452 | dated notes (Acceptance 1) | none | not shared |
| `packages/model-schema/src/model_schema/settings.py` | `ENVIRONMENT_SETTING` | none | an edit to an existing enum: serialise with any later editor |
| `backend/src/app/platform/settings.py` | scope, `resolve`'s Environment, the write path, the override check, the new key | none | serialise with any later editor |
| `backend/src/app/api/settings.py`, new `api/environment_settings.py` (or routes in `api/environments.py`) | inspection with an Environment; the PUT/GET | none | `environments.py` is also `SL-1260`'s, later in this Work |
| `backend/src/app/api/service_accounts.py`, `auth/service.py`, `api/deps.py` | keys per Environment; `rate_limit_rps` on the identity | none | serialise with any later editor |
| `backend/src/app/api/score.py` | the limiter dependency; the sampling call site | none | named in `RL-1263` item 4: serialise |
| `backend/src/app/errors.py` (`PlatformError`, its handler) | the header carrier: **an edit to an existing class** | `sl-1388` @`648ee30e`, `sl-1463` @`e0e12dd8`, `sl-1466` @`0f6fa5b6`, `sl-1389` @`b43db0f0` and `sl-1536` @`649e7e54` each append error codes | name-disjoint only if none of them edits `PlatformError` or the handler: the lead checks at the GO; otherwise serialise |
| `backend/src/app/main.py` | the override check (a lifespan hook) and the Redis client on `app.state` | the four WK-673 / A-2 / A-3 branches add a router registration | the hook is registry-exempt. The `app.state` line is "no other change" only if the lead's dispatch record names it (`RL-1263` :89–100) |
| `backend/src/app/observability/metrics.py` | one counter | none | not shared |
| `backend/src/app/db/models.py` | `EnvironmentSettingRow` appended | the same four branches append | append: exempt |
| `backend/migrations/versions/` | one revision | the same four branches add `b8d2f4a6c0e1` | new file: exempt. Re-point `down_revision` at the second merge |
| `docs/contracts/` (generated), `docs/INDEX.md` | regenerated | — | exempt |
| `docs/skills-map.md` Redis row | already amended by `RL-1347` | — | verify only |

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S3E-1 | **The creation response's shape when an account holds several keys.** `CreatedServiceAccount.key: str` (`service_accounts.py:94-100`) carries one secret. FR-430 needs one per Environment. Nine backend test files name the route (`git grep -l -E 'service-accounts\|CreatedServiceAccount' -- backend/tests` at `3519a919`). The exit demo's step S1 reads the key (`PL-1544:377`) | (a) replace `key` by `keys: [{environment, prefix, key}]`: one shape, but it breaks every caller; (b) add `keys` always, and keep `key` only when exactly one Environment is granted (`null` otherwise), with a §4.3 dated note; (c) keep `key` as the first Environment's secret, beside `keys` | **(b).** It is additive, so a one-Environment caller (the demo, and most tests) is unchanged in either merge order. A several-Environment caller gets no "first" secret, which is the F54 behaviour this slice removes. (c) keeps F54's "first" semantics alive in the contract | decision point | yes: Tasks 1 and 4 | *open*: the maintainer |
| DP-S3E-2 | **How rotation names its Environment.** FR-430: "rotation and revocation act on the key of one named environment". The rotate route takes none (`:232-235`) | (a) a required `environment` in the rotate body; (b) required only when more than one is granted, otherwise defaulted | **(a).** It is FR-430 read literally, with no special case. The cost is one field in the existing rotate tests | decision point | yes: Tasks 1 and 4 | *open*: the maintainer |
| DP-S3E-3 | **FR-452 says "The management-API limit … has no owner yet" (`07:183`).** The owner was named on 2026-10-09 (`docs/roadmap.md:1020`; `PL-1537` R4.1) | (a) this slice's `07` commit adds a dated pointer: "placed in WK-674 Slice 4 (`SL-1258`), `PL-1537` R4.1"; (b) leave it for `SL-1258` to replace when it delivers the limb | **(a).** This slice edits `07` first, and a stale "no owner" sentence misleads every reader until Slice 4 merges | spec wording | no: Task 1 applies (a) unless ruled otherwise | *open*: the maintainer |

DP-S3-3 (`PL-1342`) stays as ruled: (a), by the maintainer's entry "2026-09-30 15:13:26 BST — DECISIONS: the reconcile_ladder FD (MEDIUM, WK-674 S3); DP-S3-3 → (a), ruled by me as scope". DP-S3-2 is `RL-1347`. DP-S3-1 is `RL-1346`, which belongs to `SL-1345`.

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree, and `git branch --show-current` is the slice branch. Run `uv sync --all-packages`.
- [ ] Run the six activation needs; **stop on any unmet one**.
- [ ] Re-derive premises a–j at the executor's tree and quote each one.
- [ ] `gh pr list --state open`. Read anything that rules on settings, keys, rate limits, `errors.py`'s `PlatformError` or `score.py`, and name the SHA read.
- [ ] Create the `LG-` (working id from the lead). Its scope section quotes this plan's Scope and the GO header.

### Task 1: Spec (`07` §4.2–§4.4, §5.1, §5.2, FR-452)

- [ ] Make Acceptance 1's edits through `spec-change`, with DP-S3E-1, DP-S3E-2 and DP-S3E-3 as ruled.
- [ ] `python3 scripts/audit-docs.py` (in a slot, per Acceptance 9). Commit.

### Task 2: `model-schema` — `SettingSource`

- [ ] Red first: a model-schema test that `SettingSource` orders `ENV`, `ENVIRONMENT_SETTING`, `WORKSPACE`, `DEFAULT`. Predicted failure: `AttributeError`, no such member.
- [ ] Add the member. Regenerate; run `--check` and the contract guard; commit.

### Task 3: The migration, the scope and the startup check (FD-1320, `RL-1311` 3a)

- [ ] Red first: Acceptance 7's three cases and Acceptance 6's startup case, each through the real `create_app` lifespan. Predicted failure: the app starts.
- [ ] The revision (Acceptance 3), with the round trip.
- [ ] `SettingDefinition`'s scope (default workspace only), and the override check called from the lifespan. Green; commit.

### Task 4: The Environment-setting layer and keys per Environment (FR-431, FR-446, FR-430, F54)

- [ ] Red first: Acceptance 5 (including the `score.py:485-486` call site), Acceptance 6's resolve-time skip, and Acceptance 4.
- [ ] The resolver's Environment argument (none skips the layer); inspection; `EnvironmentSettingRow`; the audited PUT and the GET; the two keys declared workspace-or-Environment.
- [ ] Create, rotate and revoke per Environment, with DP-S3E-1's response and DP-S3E-2's rotate field. Green; commit.

### Task 5: The scoring rate limit (FR-452 scoring limb, NFR-499, F48; `RL-1347`)

- [ ] Red first: `RL-1347` Acceptance cases 1–8, each by the cause it names. Two of them: case 1 with the counter per-process admits 6; case 7 with the `except RedisError` removed fails with 500.
- [ ] The rate-limit module under `backend/src/app/platform/` (route class a parameter, `score` the only caller). Then `scoring.default_client_rate_limit_rps` in `REGISTRY`, `rate_limit_rps` on the identity and on `Caller`, the header carrier, the lifespan client with 50 ms timeouts, the metric, and 429 in `/score`'s OpenAPI with the contract regenerated. Green; commit.
- [ ] Case 9, measured in a slot: p50 and p99 over 10,000 limiter calls, with `uptime`, quoted in the `LG-`.

### Task 6: The gate and the close

- [ ] The full two-half gate through the slot wrapper (Acceptance 9). Quote every rc, `N passed`, `HEAD` and `uptime`.
- [ ] The `LG-`: the tree, the premises, every red quote, the DP resolutions, FD-1320 discharged at merge, and the `SL-1257` status line. Then Acceptance 10.

## Hand-off (not this plan's writes)

- **At the mint (the batch minter):** `PL-1342` takes `superseded_by: [<this plan's id>]` (`document-ids.md` §1.5). The lead lists this plan on WK-674's roadmap row.
- **The `SL-1257` row** (the planner re-cuts on replan, `document-ids.md` §1.6; proposed here, applied in the batch): one dated line saying the leaf plan is this plan, and that the title's "NFR-496 prod-sampling limb" was delivered by `SL-1345` (`03:1401`). The title itself is not edited.
- **Slice 4** reuses this slice's counter for FR-452's management limb (`PL-1537` R4.1). **Slice 6** declares FR-270's and FR-271's flags Environment-only on this slice's scope, and inherits Acceptance 6's refusal and skip.
- **The exit demo (b)** (`PL-1544`): under DP-S3E-1 (b), step S1 is unchanged. Under (a), its script reads `keys[0].key`, and the lead tells PL-1544's executor.

## Self-review

- **Scope against the ruling:** FR-430, FR-431, F54 and F48 (Acceptance 4, 5, 8) are "as still applicable", with the ladder carve-out applied (§"Not in this slice") and the FR-452 split applied (Acceptance 8, Scope). The current spec text is quoted verbatim at `3519a919` (§Spec).
- **Against `PL-1237` Task 3's items** (via `PL-1342`'s self-review): the §4.3 spec change first (Acceptance 1); one key per Environment and the refused `dev` key (Acceptance 4); Environment configuration as an audited Setting behind `admin:manage_settings` (Acceptance 5); the shared Redis counter with two replicas (Acceptance 8); and the monitoring limb with `uat` leaving `prod` unchanged (Acceptance 5). The NFR-496 item is delivered elsewhere and stated so.
- **Every ruling applied at all four site classes:** `RL-1311` (narrative, the write set, Tasks 2–4, Acceptance 2, 5, 6); `RL-1347` (narrative, the write set, Task 5, Acceptance 8); FD-1320 (Task 3, Acceptance 7, quoted); DP-S3-3 (Task 4, Acceptance 5).
- **Literals checked at `3519a919`:** every path, line and symbol in the premises table, read by `git grep -n` and `sed -n` at that tree. `test_settings_environment.py` and `api/environment_settings.py` are new names. A counted figure carries its predicate (premise c).
- **Ids listed individually:** FR-430, FR-431, FR-446, FR-447, FR-452, NFR-499 (in scope); FR-248, NFR-496, FR-270, FR-271, FR-389, FR-417, FR-428, FR-451 (cited). No range is used.
- **Open:** DP-S3E-1, DP-S3E-2 and DP-S3E-3, for the maintainer.
