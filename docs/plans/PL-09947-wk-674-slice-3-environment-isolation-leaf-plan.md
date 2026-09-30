---
id: PL-9947
family: plan
kind: leaf
title: WK-674 Slice 3 — Environment isolation (FR-430, FR-431, register F54 and F48, NFR-496 prod-sampling limb): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: 11c76b6c83647c512796fedb9c0143927dcd78cb
phase: P2
work: WK-674
slice: SL-1257
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1306, PL-1303, RL-1184, RL-1232, RL-1236, RL-1263, RL-1311]
---

# WK-674 Slice 3 — Environment isolation: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` and `python-test` (every task), `fastapi-service` (Tasks 3–6) and `dev-commands` (the migration, the gate and the gate slot), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make each Environment **its own**: a Service Account holds one key per granted Environment,
a value set for one Environment changes no other, a client's request rate is bounded by a
counter every replica shares, a settings override that cannot be honoured stops the process
at startup, and the Premium Ladder is actually proved to reconcile — on every quote outside
`prod`, and on a configured sample in `prod`.

**Architecture.** The Settings resolver gains an **Environment setting** layer, between the
process override and the workspace setting, for keys that declare they may vary per
Environment (`RL-1311`). Its rows are keyed by the Environment's identity (WK-674 Slice 2's
`EnvironmentRow`), written through an audited, `admin:manage_settings`-guarded route. Key
issuance mints one key per granted Environment. A fixed-window Redis counter, keyed by
Environment and Service Account, bounds each client. A new startup check reads every
`GIP_SETTING_*` override before the app serves. `reconcile_ladder` is made to apply every
recorded operation, and scoring asserts it at a per-Environment sampling rate that is itself
an Environment setting.

**Tech Stack:** Pydantic v2, FastAPI, SQLAlchemy 2.x async, Alembic, Redis (the existing
broker/cache instance, per tenant, ADR-710), pytest. No new dependency: no `uv.lock` or
`pyproject.toml` change.

**Spec:**
- [`../specs/07-platform.md`](../specs/07-platform.md) §3.5 — **FR-430** (`07:141`, as amended
  by `RL-1184` E7), **FR-431** (`07:142`); §3.8 — **FR-446** (`07:172`, amended by `RL-1311`),
  **FR-447** (`07:173`); §4.2 (`07:245-259`), §4.3 (`07:261-275`), §4.4 (`07:277-292`); §5.1
  (`07:304-311`); §5.2 (`07:382-383`). Line numbers are at the tree above; WK-674 Slice 2 edits
  `07` §4.2 and §5.1 before this slice runs, so the executor re-reads them.
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) — **FR-248** (`03:155`), **NFR-496**
  (`03:1157`, the prod-sampling limb), **NFR-499** (`03:1160`, the per-client rate-limit limb).
- The ruling this slice executes: **`RL-1311`** (OQ-1235 decided; #939, minted in mint batch 3,
  #992). **At the tree above it is not yet on `main`**; it resolves when batch 3 merges.

**What this plan implements.** WK-674's map plan **PL-1237**, **Task 3 — "Slice 3:
environment isolation"** (`PL-1237:828-870` at the tree above), whose slice row is
**SL-1257**. It follows **WK-674 Slice 2** (`PL-1306`), which creates the Environment record
this slice keys everything on.

## Status

Filed 2026-09-30 against the tree above, under **working id 9947** (checked free by the
lead and recorded in `eta.md`'s "Working ids held"). The id is minted at this PR's merge turn.

**Activation needs, in order** (activation is the `status:` flip only; the facts of each need
met live in the dispatch record, quoted in the slice ledger's Task 0 — the maintainer's entry
headed
`2026-09-30 14:48:52 BST — DECISIONS: check 34 is vacuous on real trees → a new FD (MEDIUM, WK-1170); PL-1299 accepted; the activation practice from now on`,
item (3)):
1. **`RL-1311` on `main`** (mint batch 3 merged).
2. **WK-674 Slice 2 closed** — in the lane A order **S2a → the validation-rule fix slice
   (#978) → S2 → S3** (the maintainer's entry headed
   `2026-09-30 11:56:33 BST — DECISIONS: slice order after the split; FR-384 confirmed; FR-383 and FR-385 owners`
   for the first three; this slice follows S2 by `PL-1237`'s Sequencing).
3. **DP-S3-1, DP-S3-2 and DP-S3-3 below resolved.**
4. **The lead's go.**

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means
the failing run is quoted in the ledger with its failing assert line **and the cause the
step predicts**; a failure for any other cause is a plan defect. "Red on broken input" means
the guard is green, then deliberately disabled, the test shown red with the predicted cause,
and the guard restored.

1. **Spec, first, through `spec-change`.** `python3 scripts/audit-docs.py` exits 0 on each
   spec commit. `07`:
   - §4.3's `ServiceAccount` shows a **key set, one per granted Environment**, each with its
     own rotation state, with a dated note citing FR-430 as `RL-1184` E7 amends it;
   - §4.4's resolution shape gains the `environment_setting` candidate (`RL-1311` item 2) and an
     optional Environment in the request;
   - §5.2's `get(key, workspace_id)` gains `environment: str | None = None`;
   - §5.1: the rotate row takes the Environment it rotates; the
     `PUT /api/v1/environments/{…}/settings` row (`07:307` at the tree above) uses the path
     parameter Slice 2 settled (the Environment slug), and a `GET` of an Environment's
     settings with their sources is appended;
   - §4.2's example `settings` object is replaced by a pointer to the Environment-setting rows
     of §4.4, with a dated note: its keys (`trace_sampling_rate`, `rate_limit_rps`, `shadow`)
     were example names, and the registry's names (`rating.trace_sample_rate`,
     `backend/src/app/platform/settings.py:196`) are the contract.
   FR-446 already carries `RL-1311`'s dated clause (that ruling's commit); the executor
   verifies it and does not reword it. FR-430, FR-431, FR-447, FR-248, NFR-496 and NFR-499 are
   **not** reworded; if one needs it, the executor stops and reports.
2. **Contract.** `SettingSource.ENVIRONMENT_SETTING = "environment_setting"` is added to
   **`model_schema`'s** enum (`packages/model-schema/src/model_schema/settings.py:27-32`),
   ordered between `ENV` and `WORKSPACE` (`RL-1311` item 2). The backend's **other**
   `SettingSource` (`backend/src/app/config.py:41-46`, whose `ENVIRONMENT = "environment"` names
   a startup-configuration layer) is **not touched and not imported** by any new code:
   `git grep -n -E 'from app\.config import .*SettingSource' -- backend/src/app/platform backend/src/app/api`
   prints nothing new. `uv run python scripts/generate-contracts.py --check` exits 0; the
   contract guard passes, quoted.
3. **Migration (FR-417).** One revision; `down_revision` is the head at the executor's tree
   (re-pointed at merge, RL-1263). It creates `environment_settings` (`environment_id` FK to
   Slice 2's `environments`, `key`, `value` JSONB, `updated_by`, `updated_at`; unique
   `(environment_id, key)`). Round trip `upgrade`/`downgrade -1`/`upgrade` exits 0, and
   `tests/test_repository_invariants.py` passes. **Existing keys are not backfilled**: a key's
   secret is shown once (FR-389), so no migration can mint one; an account granted several
   Environments before this slice keeps its one key and gets the others at its next per-
   Environment rotation. A migration test asserts existing `api_keys` rows are unchanged.
4. **One key per granted Environment (FR-430, register F54), each red first**, in
   `backend/tests/test_service_accounts.py` (append; mirror its fixtures):
   - creating an account granted `dev` and `uat` mints **two** keys, one per Environment, and
     the creation response carries each secret once; **the old one-key behaviour fails this
     assertion** (predicted red at the tree above: one key, for `environments[0]`,
     `backend/src/app/api/service_accounts.py:180`);
   - rotating names one Environment and acts on **that** Environment's key only; the other's
     `expires_at` is unchanged (predicted red: `:246` rotates `environments[0]` and shortens
     every unrevoked key);
   - revoking by prefix revokes one key, and the account's other key still authenticates;
   - **a legitimately issued `dev` key is refused once `dev` leaves the account's grant**: the
     refusal branch (`backend/src/app/auth/service.py:214-224`, `ENVIRONMENT_SCOPE_DENIED`) is
     reached by a key the platform issued, not a forged one. (At the tree above no route
     narrows an account's Environments, so the test narrows it through the service layer and
     says so.) And a `dev` key scores against `dev`'s live Deployment, never `uat`'s, when the
     two differ (the Environment comes from the key, Slice 2's resolution).
5. **The Environment-setting layer** (`RL-1311` items 1, 2, 3 and 5; its Acceptance), each red
   first, in `backend/tests/test_settings_environment.py`:
   - `SettingDefinition` gains a scope — workspace only (the default), workspace or
     Environment, Environment only — and **each key this slice makes per-Environment declares
     it** (DP-S3-2 and DP-S3-3 name them; `rating.trace_sample_rate` and the new
     ladder-sampling key at least);
   - a key set for `uat` changes the effective value in `uat` only; its resolution reports
     `environment_setting` as the source, and `prod` still reports `workspace` or `default`;
   - for a workspace-or-Environment key, a process override (`GIP_SETTING_<KEY>`) wins over an
     Environment setting in every Environment the process serves;
   - a workspace-only key written for an Environment is refused with `SETTING_INVALID`;
   - with no Environment in the request, the Environment layer is skipped;
   - inspection with an Environment reports every candidate, the Environment setting included;
   - the write route is guarded by `admin:manage_settings` (`RL-1236` DP-D): a caller without
     it is refused with 403 `PERMISSION_DENIED`;
   - **the audit** (FR-431): every Environment-setting write commits with one Audit Event
     naming the Environment, the key, and the old and new values. Red on broken input: with
     the `audit.record` call patched to a no-op, the test is red.
6. **Environment-only keys and the process layer** (`RL-1311` item 3a), red first, with a
   **test-registered** Environment-only key (Slice 6 declares the real FR-270/FR-271 flags):
   a `GIP_SETTING_<KEY>` present at startup stops the process with a message naming the key
   and the rule; a variable set after startup is skipped at resolve (the source stays
   `environment_setting` or `default`) and a warning is logged. With the refusal and the skip
   removed, the flag resolves on in every Environment, and the tests fail.
7. **FR-447's startup validation of the overrides — FD 9881** (auditor's finding, **MEDIUM**,
   "Deferred with an owner: WK-674 Slice 3. Event that discharges it: Slice 3's merge"; #965,
   working id 9881, head `304f6dc3dcf072a1db5b67d9afe230411c30cdfc`; cited by PR until it
   mints). Its red-first acceptance, verbatim, each written to fail on `origin/main` first:
   > - an **unknown** override key refuses startup, naming the key;
   > - an **ill-typed or out-of-range** override value refuses startup with a clear message;
   > - an **Environment-only key** present as a process override refuses startup (#939's rule 3a);
   > - the acceptance runs the **real `create_app` lifespan with the database**, not `load_settings()`
   >   alone, because that is the path FR-447 names, and the one whose failure to refuse is measured
   >   above.

   The check is **new** (FD 9881: "none exists to extend, and `require_startable` and the
   lifespan's two checks do not touch overrides"); it reads `Settings.setting_overrides`
   (`backend/src/app/config.py:242-249`) against `REGISTRY`
   (`backend/src/app/platform/settings.py:110`) and coerces each value with its
   definition's `coerce`.
8. **Per-client rate limit shared across replicas (NFR-499's limit; register F48, `RL-1184`
   E6 "a shared Redis counter, per tenant")**, red first: two app instances (two `TestClient`s
   over two `create_app` calls sharing one Redis) together admit at most the account's
   `rate_limit_rps` requests in one window; the next is refused with 429 `RATE_LIMITED`
   (`backend/src/app/errors.py:58`, raised nowhere at the tree above). **A single-process
   test proves nothing here** (F48: an in-process limiter "is not a limit"), so the test
   asserts the two instances share the count. Red on broken input: with the counter made
   per-process, the pair admits twice the limit. The counter's key and fallback are DP-S3-2's.
9. **FR-430's monitoring-configuration limb**, per DP-S3-3: setting the limb's key in `uat`
   leaves `prod`'s resolved value unchanged. Red on broken input: with the key's scope forced
   to workspace-only and the value written at workspace level, `prod` changes too.
10. **NFR-496's prod-sampling limb, on a reconciliation that actually reconciles (FR-248).**
    - **Premise** (at the tree above): `reconcile_ladder`
      (`packages/pricing-core/src/pricing_core/money.py:55-70`) checks only that the first
      rung equals `risk_premium_minor` and that every value is an `int`; its caller,
      `packages/pricing-core/src/pricing_core/rating/score.py:738`, runs it on every quote,
      and its result reaches only the trace (`:741-745`); `LADDER_RECONCILIATION_FAILED`
      (`errors.py:326`) is raised nowhere. So an off-by-one-penny ladder passes today.
    - **Red first:** a ladder whose last rung is off by one penny is **passed** by today's
      `reconcile_ladder` (the predicted red); then `reconcile_ladder` applies every recorded
      operation from `risk_premium_minor` and requires `payable_premium` to the penny, as
      FR-248 says, and the same ladder is refused.
    - **Sampling:** the assertion runs at a per-Environment rate, a new workspace-or-
      Environment key (name proposed: `rating.ladder_reconciliation_sample_rate`, default
      `1.0`, so every quote is checked until an Environment setting lowers it). In `uat`, an
      off-by-one-penny ladder is caught **on the first quote**; in `prod` with the rate set
      to `0.1`, the assertion runs on a seeded sample. The sampling decision is taken in the
      backend and passed into `pricing-core`, which stays free of settings and FastAPI
      (`CLAUDE.md` §2).
    - **What a failure does** is DP-S3-1's.
11. **The gate, in a gate slot.** Every run of a whole test directory or package suite, the
    gate, or a multi-database sweep — by the executor or the auditor — runs inside a gate slot,
    `flock -w 1800 -E 99 /tmp/slots/gate-1 <cmd>` or `gate-2`, **with no `--`**, with
    `LOKY_MAX_CPU_COUNT=4 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2` set and `uptime` reported
    at each grant; only named single test files or node ids are exempt (the maintainer's
    entries headed
    `2026-09-30 11:42:08 BST — two decisions: the escaped-pipe checker blindness → a LOW FD; box load → heavy audit runs take a gate slot`
    and `2026-09-30 11:43:28 BST — the slot rule, tightened: suite-level runs count`). The
    full two-half gate (`CLAUDE.md` §11) exits 0, with every rc, the `N passed` line and
    `HEAD` quoted against main's.
12. **Item 11** (`PL-1237` Tasks preamble): the maintainer's MERGE-ACK, naming the PR's full
    head SHA, recorded in the lead's channel file, never posted on the PR; and the slice's
    clean audit filed.

## Global Constraints

- **Money is integer minor units** (`CLAUDE.md` §7): the reconciliation compares integers.
- **`pricing-core` gains no FastAPI, SQLAlchemy or Redis import** (`CLAUDE.md` §2).
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2): the key-set
  shape and `SettingSource` are declared once.
- **The migration chain has exactly one head** (`07` FR-417).
- **Build ahead of the phase is forbidden** (`CLAUDE.md` §9): no monitor (WK-687), no
  FR-270/FR-271 flag (Slice 6), no notification.
- **An Environment-only key is never supplied by the process layer** (`RL-1311` item 3a).

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `07` §3.5 | FR-430 | Whole: one key per granted Environment (F54); independent rate limits (with NFR-499); the monitoring-configuration limb, per DP-S3-3 |
| `07` §3.5 | FR-431 | Whole: Environment configuration as a Setting, resolved by §3.8's precedence, audited on change |
| `07` §3.8 | FR-446 | The Environment-setting layer and the scope rule, as `RL-1311` amended it |
| `07` §3.8 | FR-447 | The override half: FD 9881's startup validation (Acceptance 7) |
| `03` §3.6 | FR-248 | The reconciliation made real, and asserted per the sampling rate |
| `03` §9 | NFR-496 | The prod-sampling limb (`CR-1212` G4 (a)) |
| `03` §9 | NFR-499 | The per-client rate-limit limb (register F48) |

**Carried obligations placed here:** register F54 (Acceptance 4); register F48 (Acceptance 8);
`RL-1311` items 1, 2, 3, 3a and 5 (Acceptance 2, 5, 6); FD 9881 (Acceptance 7); `RL-1232`
DP-2's per-Environment default-off setting **as `RL-1311` bounds it** — this slice builds the
scope machinery and proves it on a test-registered Environment-only key; the FR-270/FR-271
flags themselves are declared by Slice 6 (`RL-1311` item 3, "Slice 6 declares the two flags").

**Not in this slice:** FR-270 and FR-271 and their flags (Slice 6); monitors (WK-687); the
switch (Slice 5); a route to change an account's granted Environments (none exists at the
tree above, and FR-430 does not require one).

### Premises re-derived at the tree above

| # | Premise | Evidence | Status |
|---|---|---|---|
| a | Key issuance mints one key, for the first granted Environment | `backend/src/app/api/service_accounts.py:180` (create), `:246` (rotate), both `generate_key(...environments[0])`; revoke by prefix `:275-316`; register F54 (`docs/findings/register.md:95`) | reproduces F54 |
| b | The key's Environment is checked against the grant | `backend/src/app/auth/service.py:214-224` (`ENVIRONMENT_SCOPE_DENIED`) | reachable only by a forged key today |
| c | The resolver has three layers | `backend/src/app/platform/settings.py:359-386` (`_resolution`: env → workspace → default); `SettingSource` `packages/model-schema/src/model_schema/settings.py:27-32` | the base for `RL-1311` |
| d | Two different `SettingSource` enums exist | model-schema's (c) and `backend/src/app/config.py:41-46` (`ENVIRONMENT = "environment"`) | must not be conflated (`RL-1311` item 2) |
| e | Nothing validates overrides at startup | `Settings.setting_overrides` (`config.py:242-249`) is read only by `platform/settings.py:332` (`_env_candidate`); `load_settings` validates `Settings` fields and `require_startable()` only | reproduces FD 9881 |
| f | No rate limiter exists | `git grep -n -E 'rate_limit_rps\|RATE_LIMITED' -- backend packages` at the tree above: the migration `6db3b9464e98_…py:46`, `service_accounts.py:65`, `:90`, `:113`, `:175`, `db/models.py:400`, `errors.py:58`, and three `test_model_jobs.py` lines where 429 is an upstream provider's | reproduces F48 |
| g | The ladder check is shallow and never fails anything | `pricing_core/money.py:55-70`; `pricing_core/rating/score.py:738`, `:741-745`; `LADDER_RECONCILIATION_FAILED` raised nowhere | **a defect this slice closes** (Acceptance 10) |
| h | No monitoring-configuration key exists | `git grep -n -i monitor -- backend/src/app` at the tree above: 8 hits, none a setting; `REGISTRY` (`settings.py:112-257`) has 16 keys, none for monitoring | the base for DP-S3-3 |
| i | The only Environment-level setting route is specified, not built | `07:307`; `git grep -n -E '/environments' -- backend/src` prints nothing at the tree above | Slice 2 builds `/environments`; this slice builds its settings route |
| j | The Alembic head | `d7e2a9b5c418` (Slice 1) at the tree above; Slice 2a and Slice 2 each append one revision first | re-derive at the executor's tree |

The executor re-reads each at its own tree — which is after Slices 2a, the validation-rule
fix and 2 have merged — and stops on any that no longer holds.

### Write set, and RL-1263

Lane A runs **S2a → the validation-rule fix → S2 → S3**, one at a time, so this slice never
builds concurrently with S2a or S2; it is written against their merged code. The paths it
shares with them are listed so the executor re-reads them after they land; concurrency is
checked at dispatch only against the lane-B slice then in flight.

| Path | This slice | Shared with | RL-1263 |
|---|---|---|---|
| `uv.lock`, any `pyproject.toml` | nothing | WK-690 S1 | not shared |
| `docs/specs/07-platform.md` §4.2, §4.3, §4.4, §5.1, §5.2 | spec change (Acceptance 1) | S2 (§4.2 note, §5.1 rows) — earlier in lane A | sequential; re-read after S2 |
| `packages/model-schema/src/model_schema/settings.py` | `ENVIRONMENT_SETTING`; the key-set shape | none found | an edit to an existing enum: serialises with any in-flight slice editing it |
| `backend/src/app/platform/settings.py` | the scope, the resolver's Environment argument, the Environment write path | none found | serialises with any in-flight slice editing it |
| `backend/src/app/api/settings.py` | inspection with an Environment | none found | as above |
| `backend/src/app/config.py` (`load_settings`) or `backend/src/app/main.py` lifespan | FD 9881's startup check | S1 (done), S2a/S2 (none planned) | `main.py` is registry-exempt only for an added hook |
| `backend/src/app/api/service_accounts.py` (`:58-66`, `:140-316`) | one key per Environment | **S2** (#971 A.6's Environment-slug check at `:63`, `:180`, `:246`) | sequential; this slice edits S2's version of the same lines |
| `backend/src/app/auth/service.py` | none planned (the refusal branch is only reached by tests) | — | — |
| new: an Environment-settings router, a rate-limit module, their tests | created | — | not shared |
| `backend/src/app/api/score.py` / the scoring path | the rate-limit dependency; the sampling decision passed down | S2 (default-live, trace link), WK-1250, WK-673, WK-675 S7b (RL-1263 item 4 names `score.py`) | serialises with any in-flight slice editing it |
| `packages/pricing-core/src/pricing_core/money.py`, `…/rating/score.py` (`:738`) | the real reconciliation; the sampled call | WK-690 S1 edits `pricing_core/data/*` only (not these files) | an edit to existing functions; serialises only with a slice editing these two files |
| `backend/src/app/db/models.py` | `EnvironmentSettingRow` appended | S2a (status metadata), S2 (appends) — earlier | append: registry-exempt |
| `backend/migrations/versions/` | one revision | S2a, S2, WK-1250 S1 | append: exempt; re-point `down_revision` |
| `docs/contracts/` generated outputs, `docs/INDEX.md` | regenerated | — | exempt |

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S3-1 | **What does a failed ladder reconciliation do at scoring?** FR-248 says it is "asserted at scoring time in `dev`/`uat` and sampled in `prod`"; `LADDER_RECONCILIATION_FAILED` is registered (`errors.py:326`) and raised nowhere; the spec does not say whether an asserted failure refuses the quote | (a) Refuse the quote with `LADDER_RECONCILIATION_FAILED` (500, a platform fault), and record it; (b) serve the quote, record the failure on the trace and in the log, and alert; (c) refuse outside `prod`, record-and-serve in `prod` | **(a).** A ladder that does not reconcile is a premium the platform cannot explain (NFR-496: "no rounding is applied more than once … to the penny"); serving it is the silent mispricing `CLAUDE.md` §2 warns of. (c) would make `prod` the one place a wrong premium is returned | decision point | yes — Task 6 | *open* — for the decision-maker at medium effort (rating correctness, not governance evidence) |
| DP-S3-2 | **The rate-limit counter's key and limit.** NFR-499 asks "per-client rate limits"; FR-430 asks "independent … rate limits" per Environment; F48 fixes the mechanism (a shared Redis counter, per tenant); `rate_limit_rps` is optional on an account (`service_accounts.py:65`) | (a) One counter per (Environment, Service Account), limit the account's `rate_limit_rps`; an account without one is unlimited; (b) as (a), with an Environment setting `scoring.default_client_rate_limit_rps` (workspace or Environment scope) as the limit for accounts without their own; (c) a per-Environment aggregate cap as well as the per-client counter | **(b).** Keying by Environment makes the limits independent per Environment (FR-430); the per-account value is NFR-499's per-client limit; and the Environment default closes the "no limit at all" case for accounts created without one, while staying a Setting (FR-431). (c) is a capacity control no requirement asks for | decision point | yes — Task 5 | *open* — for the decision-maker at medium effort |
| DP-S3-3 | **What is FR-430's "monitoring configuration" in Phase 2?** No monitoring-configuration key exists (premise h), and the monitors are WK-687's (Phase 4); `PL-1237` Task 3 limits this slice to "the per-environment *configuration* only" | (a) The per-Environment trace sampling rate, `rating.trace_sample_rate` (`settings.py:196`, the input `05` monitors read), declared workspace-or-Environment, plus the scope mechanism for WK-687 to declare its own keys; (b) new monitoring keys now; (c) the mechanism only, with no key declared | **(a).** It is the one monitoring input configured today, it is named by FR-431 ("sampling rates"), and it gives the limb's test a real key. (b) builds ahead of Phase 4 (`CLAUDE.md` §9); (c) leaves the limb with nothing to prove | scope | yes — Task 4 | *open* — for the lead to route |

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch;
  `uv sync --all-packages`.
- [ ] Confirm `RL-1311` is on `main`, Slices 2a, the validation-rule fix and 2 are closed, and
  DP-S3-1 to DP-S3-3 have resolvers; **stop if not**.
- [ ] Re-derive premises a–j at the executor's tree (after S2); quote each.
- [ ] `gh pr list --state open`; read anything ruling on settings, keys, rate limits or the
  ladder; name the SHA read. Run the write-set check against the lane-B slice in flight.
- [ ] Create the slice ledger (`LG-`, working id); its Task 0 quotes the dispatch record.

### Task 1: Spec — `07` §4.2–§4.4, §5.1, §5.2

- [ ] Acceptance 1's edits through `spec-change`; `python3 scripts/audit-docs.py`; commit.

### Task 2: `model-schema` — `SettingSource`, the key set

- [ ] Red first: a model-schema test that `SettingSource` orders `ENV`, `ENVIRONMENT_SETTING`,
  `WORKSPACE`, `DEFAULT`; predicted failure: no such member.
- [ ] Add the member, and the key-set shape of §4.3; regenerate; `--check`; the contract guard;
  commit.

### Task 3: The migration and the startup check (FD 9881, `RL-1311` 3a)

- [ ] Red first: Acceptance 7's four cases through the real `create_app` lifespan with the
  database, and Acceptance 6's startup case; predicted failure: the app starts.
- [ ] The revision (Acceptance 3); round trip.
- [ ] The new startup check; green; commit.

### Task 4: The Environment-setting layer (FR-431, FR-446, `RL-1311`)

- [ ] Red first: Acceptance 5's cases and Acceptance 6's resolve-time skip; Acceptance 9's
  monitoring-limb case (per DP-S3-3).
- [ ] The scope on `SettingDefinition`; the resolver's Environment argument (the request's
  Environment; none skips the layer); inspection; the audited write route
  (`PUT`/`GET /api/v1/environments/{slug}/settings`, `admin:manage_settings`).
- [ ] Declare the scope of each key made per-Environment; green; commit.

### Task 5: Keys per Environment (F54) and the rate limit (F48)

- [ ] Red first: Acceptance 4 and Acceptance 8.
- [ ] Create, rotate and revoke per Environment; the shared counter and its dependency on the
  scoring routes (per DP-S3-2); green; commit.

### Task 6: The ladder reconciliation and its sampling (FR-248, NFR-496)

- [ ] Red first: Acceptance 10's off-by-one ladder, passed by today's check.
- [ ] `reconcile_ladder` applies every operation; the sampling rate key; the backend's
  sampling decision passed into scoring; the failure as DP-S3-1 rules; green; commit.

### Task 7: The gate and the ledger

- [ ] The full two-half gate in a gate slot (Acceptance 11); quote every rc, `N passed`,
  `HEAD`, `uptime`.
- [ ] The ledger: the tree, the premises, every red quote, the DP resolutions, FD 9881
  discharged at merge.
- [ ] Item 12.

## Hand-off

Slice 4 (the deployment path) follows. Slice 6 declares FR-270's and FR-271's flags
Environment-only on this slice's scope machinery, and inherits Acceptance 6's refusal and skip.

## Self-review

- **Scope against the map:** `PL-1237` Task 3's items — the §4.3 spec change first, one key
  per Environment, the refused `dev` key, environment configuration as a Setting guarded by
  `admin:manage_settings` with a full Audit Event, NFR-499's shared Redis counter, the
  monitoring-configuration limb, NFR-496's prod-sampling limb — are Acceptance 1, 4, 5, 8, 9
  and 10. Its gate items — the two-replica test, the old one-key behaviour failing, the `uat`
  monitoring value leaving `prod` unchanged, the off-by-one ladder caught in `uat` on the
  first quote — are Acceptance 8, 4, 9 and 10.
- **`RL-1311` applied where it operates:** items 1 and 5 (Acceptance 5, Task 4), 2 (Acceptance
  2, Task 2), 3 (Acceptance 5), 3a (Acceptance 6, Task 3); its Acceptance bullets for Slice 3
  are Acceptance 5 and 6.
- **FD 9881** quoted verbatim (Acceptance 7) and placed in Task 3.
- **One premise found that changes the map's NFR-496 limb:** the reconciliation it asks to
  sample is shallow at the tree above (premise g), so the map's own broken-input case (an
  off-by-one-penny ladder) would pass. Acceptance 10 makes the check real first; DP-S3-1 asks
  what a failure does.
- **Counts** carry their tree and predicate (premises f and h).
- **Open:** DP-S3-1, DP-S3-2 (decision-maker, medium), DP-S3-3 (the lead routes it).
