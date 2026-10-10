---
id: PL-1342
family: plan
kind: leaf
title: WK-674 Slice 3 — Environment isolation (FR-430, FR-431, register F54 and F48, NFR-496 prod-sampling limb): leaf plan
status: superseded                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: 11c76b6c83647c512796fedb9c0143927dcd78cb
phase: P2
work: WK-674
slice: SL-1257
supersedes: []
superseded_by: PL-1583
corrected_by: []
relates: [PL-1237, PL-1306, PL-1303, RL-1184, RL-1301, RL-1232, RL-1236, RL-1263, RL-1311]
---

# PL-1342 — WK-674 Slice 3 — Environment isolation: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` and `python-test` (every task), `fastapi-service` (Tasks 3–6) and `dev-commands` (the migration, the gate and the gate slot), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make each Environment **its own**: a Service Account holds one key per granted Environment,
a value set for one Environment changes no other, a client's request rate is bounded by a
counter every replica shares, a settings override that cannot be honoured stops the process
at startup, and the Premium Ladder is actually proved to reconcile — on every scored quote,
in every Environment.

**Architecture.** The Settings resolver gains an **Environment setting** layer, between the
process override and the workspace setting, for keys that declare they may vary per
Environment (`RL-1311`). Its rows are keyed by the Environment's identity (WK-674 Slice 2's
`EnvironmentRow`), written through an audited, `admin:manage_settings`-guarded route. Key
issuance mints one key per granted Environment. A Redis counter shared by every replica
bounds each client; its key, its window and what it does when Redis is unavailable are
DP-S3-2's. A new startup check reads every
`GIP_SETTING_*` override before the app serves. `reconcile_ladder` is made to apply every
recorded operation, and scoring asserts it on **every** quote in every Environment, never
sampled; `rating.trace_sample_rate` governs trace persistence only (the maintainer's
decision, `2026-09-30 15:17:54 BST — audit round-up: decisions`).

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
  (`03:1157`, the prod-sampling limb, decoupled by the maintainer's decision below), **NFR-499** (`03:1160`, the per-client rate-limit limb).
- The ruling this slice executes: **`RL-1311`** (OQ-1235 decided; #939, minted in mint batch 3,
  #992). **At the tree above it is not yet on `main`**; it resolves when batch 3 merges.

**What this plan implements.** WK-674's map plan **PL-1237**, **Task 3 — "Slice 3:
environment isolation"** (`PL-1237:828-870` at the tree above), whose slice row is
**SL-1257**. It follows **WK-674 Slice 2** (`PL-1306`), which creates the Environment record
this slice keys everything on.

## Status

Filed 2026-09-30 against the tree above, under **working id 9947** (checked free by the
lead and recorded in `eta.md`'s "Working ids held"). The id is minted at this PR's merge turn.

**Minted 2026-09-30 as PL-1342** (`python3 scripts/doc-id.py next --ref 71b672205f7212008d0ff00b5cbc4810b56f12e6` printed `1342`, and the lead allocated it in mint batch 12). It was filed under working id 9947, and this body keeps that id as written. Its last audit, auditor-close1255's delta audit of `27ab8c00..06e3e896`, was NOT CLEAN on finding **N5**: the ladder replay in Acceptance 10 (the four operation kinds and the comparison) and Task 6. **N5 is superseded by `RL-1329`**, and the replay text here is not operative. The operative text is in WK-674 S3's dispatch record and its ledger's Task 0.

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
3. **DP-S3-1 and DP-S3-2 below resolved** (DP-S3-3 is resolved).
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
   verifies it and does not reword it. **FR-248 (`03:155`) and NFR-496 (`03:1157`) each gain a
   dated clause**, citing the maintainer's entry headed
   `2026-09-30 15:17:54 BST — audit round-up: decisions`:
   the reconciliation runs on every scored quote in every Environment and is never sampled,
   superseding their "sampled in `prod`"; the trace-sampling rate governs trace persistence
   only. NFR-499 (`03:1160`) is not touched: its "sampled traces" are trace persistence, not
   the reconciliation. `PL-1237`'s own "sampled in `prod`" wording is frozen (`document-ids.md`
   §1.5) and is superseded by this plan's delta, not edited. FR-430, FR-431 and FR-447 are
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
     it** (DP-S3-2 and DP-S3-3 name them; `rating.trace_sample_rate` at least);
   - a key set for `uat` changes the effective value in `uat` only; its resolution reports
     `environment_setting` as the source, and `prod` still reports `workspace` or `default`;
   - for a workspace-or-Environment key, a process override (`GIP_SETTING_<KEY>`) wins over an
     Environment setting in every Environment the process serves;
   - a workspace-only key written for an Environment is refused with `SETTING_INVALID`;
   - **an Environment-only key written at workspace level is refused with `SETTING_INVALID`**
     (`RL-1311` item 3; auditor-close1255 M4 (i));
   - **an Environment-setting write validates with the key's `coerce`** before it writes
     (`RL-1311` item 5): an ill-typed value and an out-of-range value are each refused with
     `SETTING_INVALID`, and nothing is written (M4 (ii));
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
9. **FR-430's monitoring-configuration limb** — **DP-S3-3 ruled (a) by the maintainer, as
   scope** (`2026-09-30 15:13:26 BST — DECISIONS: the reconcile_ladder FD (MEDIUM, WK-674 S3); DP-S3-3 → (a), ruled by me as scope`): in Phase 2 the limb is the existing `rating.trace_sample_rate`
   (`backend/src/app/platform/settings.py:196`), declared workspace-or-Environment, plus the
   scope mechanism; anything wider is `05`'s, spec only (`CLAUDE.md` §0). Each red first:
   - setting the key in `uat` leaves `prod`'s resolved value unchanged. Red on broken input:
     with the key's scope forced to workspace-only and the value written at workspace level,
     `prod` changes too;
   - **the call site uses the request's Environment** (auditor-close1255 M3): at the tree
     above, trace sampling resolves the rate with the workspace only
     (`backend/src/app/api/score.py:399-400`, `settings_service.resolve(session, settings,
     caller.workspace_id, "rating.trace_sample_rate")`), and `resolve`
     (`backend/src/app/platform/settings.py:292`) takes no Environment. Both change: `resolve`
     gains the Environment argument of Acceptance 5, and the call site passes the caller's
     Environment. Behavioural case: with `uat`'s rate set to `1.0` and the workspace rate
     `0.0`, a scored quote in `uat` is sampled — predicted red at the tree above: it is not,
     because the workspace rate is read.
10. **NFR-496, on a reconciliation that actually reconciles, on every quote (FR-248).**
    - **Premise, corrected** (at the tree above; filed as a finding, working id 9949, "vacuous",
      **MEDIUM**, owner WK-674 Slice 3, by the maintainer's entry headed
      `2026-09-30 15:13:26 BST — DECISIONS: the reconcile_ladder FD (MEDIUM, WK-674 S3); DP-S3-3 → (a), ruled by me as scope`):
      `packages/pricing-core/src/pricing_core/rating/score.py:737` sets
      `risk_premium_minor = ladder_steps[0][1]` and `:738` passes it to `reconcile_ladder`,
      whose first-rung check (`packages/pricing-core/src/pricing_core/money.py:55-70`) then
      compares that value **with itself**; the rest of the check is int-ness. So
      `ladder_reconciled` is True on every trace whose rungs are integers (it reaches only the
      trace, `:741-745`, `Trace.ladder_reconciled`,
      `packages/model-schema/src/model_schema/scoring.py:168`), and
      `LADDER_RECONCILIATION_FAILED` (`backend/src/app/errors.py:326`) is raised nowhere. An
      off-by-one-penny ladder passes today.
    - **The signature changes** (auditor-close1255 M1). `reconcile_ladder` receives the
      **recorded operations** — each `LadderRung`'s `operation`
      (`LadderOperation`: `kind`, `factor`, `amount_minor`, `mode`, `dp`;
      `packages/model-schema/src/model_schema/scoring.py:108-135`) — and the **real** risk
      premium, the algorithm's own risk-premium output, never the first rung. **Its inputs and
      comparison, exactly** (auditor-close1255 N2, against `_build_ladder`,
      `packages/pricing-core/src/pricing_core/rating/score.py:551-624`):
      - **the risk premium's source and check.** The first rung carries **no** recorded
        operation (`operation = None`); its value is `_round_minor(raw, mode)` of the value the
        algorithm's `risk_premium_minor` output step consumes (for example `1304.8` → `1305`).
        So the check takes that **unrounded** output value and the step's declared rounding
        mode, rounds it once with that mode, and requires the first rung's `value_minor` to
        equal the result;
      - **the four operation kinds** (`LadderOperationKind`,
        `packages/model-schema/src/model_schema/scoring.py:63`), each replayed from the
        previous rung's replayed value: `multiply` → `apply_factor(prev, Decimal(factor), mode)`
        (`pricing_core/money.py:33`), whose `mode` takes the short names of `RoundingMode`
        (`money.py:20`: `half_even`, `half_up`, `ceiling`, `floor`, `down`), the same strings
        the operation records; `add` → `prev + amount_minor`; `round` at `dp = 0` → `prev`
        unchanged (a whole number of minor units is its own rounding); `none` → `prev`
        unchanged (the `constraints` rung, whose `applied` codes explain nothing numeric);
      - **the comparison:** every replayed value equals that rung's recorded `value_minor`,
        and the last equals `payable_premium` — to the penny, integers throughout.
    - **False-positive control, required** (N2 (c)): **every existing scoring fixture and every
      committed regression suite still reconciles under the real check.** Run over the
      fixtures that `score_one` tests use, and over the golden quotes of each committed
      `RegressionSuite` (FR-261's property). A fixture that fails is either a real defect,
      reported as a finding, or a check defect; it is never "fixed" by editing the fixture.
      auditor-close1255 prototyped the replay on one fixture and reproduced
      `1305 → 1436 → 1436 → 1507 → 1507`. Every caller changes with it:
      `pricing_core/rating/score.py:738`, the FR-261 "ladder reconciles" property
      (`pricing_core/rating/properties.py:41` import, `:303` call), the export
      (`pricing_core/__init__.py:31`), and `score.py:99-105`'s docstring, which calls the
      check "shallow — first-rung and int-ness only".
    - **Red first, through the call site** (the maintainer, relayed by the lead): `score_one`
      **with `trace=True`** on a one-penny-off ladder produces `ladder_reconciled` **False** (or
      DP-S3-1's refusal). Predicted red at the tree above: it is True. (`ladder_reconciled` lives
      only on `Trace`, `packages/model-schema/src/model_schema/scoring.py:168`, which is built
      only when a trace is requested, `score.py:741-745`; auditor-close1255 N3.) **An untraced
      failure** — `trace=False`, or a trace not persisted — surfaces by DP-S3-1's ruling: under
      (a) the refusal is the signal; under (b) the logged event (rung names and minor-unit
      difference, no quote input) is enough, and a test asserts it is emitted with
      `trace=False`. A unit test of `reconcile_ladder` on the same
      ladder sits beside it, but the call-site case is the proof.
    - **Red first, the property:** the FR-261 property over a planted off-by-one ladder fails
      (predicted red at the tree above: it passes, via the same vacuous check).
    - **Red first, the raise site's message** (NFR-499, `RL-917`): if DP-S3-1 rules a refusal,
      `LADDER_RECONCILIATION_FAILED` is raised at a **new** site, and its message and detail
      carry **no quote input** — only the rung names and the minor-unit difference. The two
      census tests list it among the input-free codes:
      `backend/tests/test_worker_raise_sites.py` (`_QUOTE_INPUT_CODES`, `:36-39`) and
      `packages/pricing-core/tests/test_quote_input_raise_sites.py`. Red first: a message that
      carries an input value fails the census.
    - **The trace flag records which check produced it — no back-fill of "verified".** Stored
      traces are write-once (`UPDATE` is revoked on `scoring_traces`), so a flag already stored
      cannot be corrected. `Trace` gains **`ladder_check_version`**
      (`packages/model-schema/src/model_schema/scoring.py`, beside `ladder_reconciled`), **and
      the hand-authored contract `docs/contracts/schemas/scoring.schema.json` gains it by hand,
      beside `ladder_reconciled`** (`:66` in `required`, `:88` its property), since that file is
      hand-authored and the contract guard compares the two — as `Job.platform_build` needed in
      Slice 1 (`LG-1262` Task 2); auditor-close1255 N1:
      absent or `1` means "first rung and int-ness only, before this slice — **not** a
      reconciliation"; `2` means FR-248's full check. A dated `03` §4.5 note says so. **Why a
      field and not a note alone:** deployments upgrade at different times, so a reader cannot
      tell from a trace's date which check produced its flag; the field says so on the record
      itself. (Accepted as the plan's choice by the lead, the maintainer's "the plan says
      which".) Red first: a new trace carries `ladder_check_version = 2`.
    - **Never sampled** (auditor-close1255 M2, **decided by the maintainer**,
      `2026-09-30 15:17:54 BST — audit round-up: decisions`):
      the fixed `reconcile_ladder` runs on **every** scored quote in **every** Environment —
      it is integer arithmetic over a handful of rungs — and `rating.trace_sample_rate` governs
      only whether a trace is persisted. So no Environment, however named, can switch the
      FR-248/NFR-496 check off, "`prod`" needs no definition, and no sampling key is added.
      **Red first:** with `rating.trace_sample_rate` set to `0`, `score_one` on a one-penny-off
      ladder still yields not-reconciled (or DP-S3-1's refusal). Predicted red at the tree
      above: it yields `ladder_reconciled = True`. The docstrings that say otherwise are
      corrected in the same commit: `pricing_core/money.py:63` ("asserted continuously in
      non-prod and sampled in prod") and `pricing_core/rating/score.py:99-105`.
    - **What a failure does** is DP-S3-1's.
11. **The gate, in a gate slot.** Every run of a whole test directory or package suite, the
    gate, or a multi-database sweep — by the executor or the auditor — uses **the dev-commands
    slot wrapper verbatim** (`.claude/skills/dev-commands/SKILL.md:122-171`, which exports
    `GIP_GATE_SLOT`), **plus `LOKY_MAX_CPU_COUNT=4`**, and reports `uptime` at each grant; only
    named single test files or node ids are exempt (the maintainer's entry headed
    `2026-09-30 13:24:18 BST — DATED CORRECTION to my slot-rule entries (11:42:08 and 11:43:28): use the dev-commands wrapper verbatim`,
    which supersedes the `flock -w 1800 -E 99 …` form of the 11:42:08 and 11:43:28 entries).
    The full two-half gate (`CLAUDE.md` §11) exits 0, with every rc, the `N passed` line and
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
| `03` §3.6 | FR-248 | The reconciliation made real, on every scored quote; a dated clause for "never sampled" |
| `03` §9 | NFR-496 | The prod-sampling limb (`CR-1212` G4 (a)), decoupled: every quote, every Environment (the 15:17:54 BST decision); a dated clause |
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
| g | The ladder check is **vacuous** and never fails anything | `pricing_core/rating/score.py:737` passes the first rung as the risk premium, so `money.py:55-70`'s first-rung check compares a value with itself; `:738`, `:741-745`; `LADDER_RECONCILIATION_FAILED` raised nowhere. Filed as a finding, working id 9949 (MEDIUM, owner this slice) | **a defect this slice closes** (Acceptance 10) |
| h | No monitoring-configuration key exists | `git grep -n -i monitor -- backend/src/app \| wc -l` at the tree above prints `9`, none a setting (corrected from 8 on auditor-close1255 L4); `REGISTRY` (`settings.py:112-257`) has 16 keys, none for monitoring | the base for DP-S3-3 |
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
| `backend/src/app/platform/settings.py` | the scope, `resolve`'s Environment argument (`:292`), the Environment write path | none found | serialises with any in-flight slice editing it |
| `backend/src/app/api/settings.py` | inspection with an Environment | none found | as above |
| `backend/src/app/config.py` (`load_settings`) or `backend/src/app/main.py` lifespan | FD 9881's startup check | S1 (done), S2a/S2 (none planned) | `main.py` is registry-exempt only for an added hook |
| `backend/src/app/api/service_accounts.py` (`:58-66`, `:140-316`) | one key per Environment | **S2** (`RL-1301` A.6's Environment-slug check at `:63`, `:180`, `:246`) | sequential; this slice edits S2's version of the same lines |
| `backend/src/app/auth/service.py` | none planned (the refusal branch is only reached by tests) | — | — |
| new: an Environment-settings router, a rate-limit module, their tests | created | — | not shared |
| `backend/src/app/api/score.py` / the scoring path | the rate-limit dependency; the trace-sampling call site (`:399-400`) passing the Environment | S2 (default-live, trace link), WK-1250, WK-673, WK-675 S7b (RL-1263 item 4 names `score.py`) | serialises with any in-flight slice editing it |
| `docs/specs/03-rating-engine.md` §3.6 (FR-248, `:155`), §9 (NFR-496, `:1157`) | dated clauses (Acceptance 1) | WK-690 S1 (§3.5, FR-244), WK-1250 S1 (§4, §5.1), WK-1178 fix slice (§5.1 catalogue) | section-disjoint rows; checked at dispatch against the actual diffs (the 10:24:00 BST rule) |
| `packages/pricing-core/src/pricing_core/money.py` (`reconcile_ladder`, `:55-70`), `…/rating/score.py` (`:99-105` docstring, `:736-745`), `…/rating/properties.py` (`:41`, `:303`), `…/__init__.py` (`:31`) | the new signature and every caller | WK-690 S1 edits `pricing_core/data/*` only (not these files) | edits to existing functions; serialise only with a slice editing these files |
| `packages/model-schema/src/model_schema/scoring.py` (`Trace`, `ladder_reconciled` `:168`), the regenerated contract, and the **hand-authored** `docs/contracts/schemas/scoring.schema.json` (`:66`, `:88`) | `ladder_check_version` | any in-flight slice editing `model_schema/rating.py`, `model_schema/scoring.py` or the trace shape (WK-1250 S1 and S2's trace work) | an edit to an existing class: **serialises** with those |
| `backend/tests/test_worker_raise_sites.py` (`:36-39`), `packages/pricing-core/tests/test_quote_input_raise_sites.py` | the census of the new raise site | none found | not shared |
| `backend/src/app/db/models.py` | `EnvironmentSettingRow` appended | S2a (status metadata), S2 (appends) — earlier | append: registry-exempt |
| `backend/migrations/versions/` | one revision | S2a, S2, WK-1250 S1 | append: exempt; re-point `down_revision` |
| `docs/contracts/` generated outputs, `docs/INDEX.md` | regenerated | — | exempt |

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S3-1 | **What does a failed ladder reconciliation do at scoring?** The check runs on every scored quote in every Environment (FR-248 and NFR-496 as this slice's dated clauses amend them, on the maintainer's decision `2026-09-30 15:17:54 BST — audit round-up: decisions`); `LADDER_RECONCILIATION_FAILED` is registered (`errors.py:326`) and raised nowhere; the spec does not say whether a failed check refuses the quote | (a) Refuse the quote with `LADDER_RECONCILIATION_FAILED` (500, a platform fault), and record it; (b) serve the quote, record the failure on the trace (when there is one) and in the log, and alert; ~~(c) refuse outside `prod`, record-and-serve in `prod`~~ *(withdrawn 2026-09-30: it reintroduces the `prod` special case the maintainer's decision removed; auditor-close1255 N4)* | **(a).** A ladder that does not reconcile is a premium the platform cannot explain (NFR-496: "no rounding is applied more than once … to the penny"); serving it is the silent mispricing `CLAUDE.md` §2 warns of, and a refusal is also the one signal that surfaces an untraced failure without a log search | decision point | yes — Task 6 | *open* — for the decision-maker at medium effort (rating correctness, not governance evidence) |
| DP-S3-2 | **The rate-limit counter's key and limit.** NFR-499 asks "per-client rate limits"; FR-430 asks "independent … rate limits" per Environment; F48 fixes the mechanism (a shared Redis counter, per tenant); `rate_limit_rps` is optional on an account (`service_accounts.py:65`) | (a) One counter per (Environment, Service Account), limit the account's `rate_limit_rps`; an account without one is unlimited; (b) as (a), with an Environment setting `scoring.default_client_rate_limit_rps` (workspace or Environment scope) as the limit for accounts without their own; (c) a per-Environment aggregate cap as well as the per-client counter | **(b).** Keying by Environment makes the limits independent per Environment (FR-430); the per-account value is NFR-499's per-client limit; and the Environment default closes the "no limit at all" case for accounts created without one, while staying a Setting (FR-431). (c) is a capacity control no requirement asks for. **Also to rule: the window and the Redis-outage behaviour** (auditor-close1255 L3). Window: a fixed one-second window (`INCR` + `EXPIRE`) is the simplest shared counter; a sliding window is fairer at the boundary and costs a sorted set per key. Outage: **fail open** (serve, log and count each unlimited request) keeps scoring available when the cache is down (`03` NFR-497's availability target), at the cost of no limit during the outage; **fail closed** (refuse with 503) keeps the limit and turns a cache outage into a pricing outage. Planner's input: fixed window, fail open with the event logged and counted — a rate limit protects capacity, and an outage of the limiter should not take pricing down with it | decision point | yes — Task 5 | *open* — for the decision-maker at medium effort |
| DP-S3-3 | **What is FR-430's "monitoring configuration" in Phase 2?** No monitoring-configuration key exists (premise h), and the monitors are WK-687's (Phase 4); `PL-1237` Task 3 limits this slice to "the per-environment *configuration* only" | (a) The per-Environment trace sampling rate, `rating.trace_sample_rate` (`settings.py:196`, the input `05` monitors read), declared workspace-or-Environment, plus the scope mechanism for WK-687 to declare its own keys; (b) new monitoring keys now; (c) the mechanism only, with no key declared | **(a).** It is the one monitoring input configured today, it is named by FR-431 ("sampling rates"), and it gives the limb's test a real key. (b) builds ahead of Phase 4 (`CLAUDE.md` §9); (c) leaves the limb with nothing to prove | scope | yes — Task 4 | **Resolved (a), ruled by the maintainer as scope** (`2026-09-30 15:13:26 BST — DECISIONS: the reconcile_ladder FD (MEDIUM, WK-674 S3); DP-S3-3 → (a), ruled by me as scope`): `rating.trace_sample_rate`, workspace-or-Environment, plus the mechanism; anything wider is `05`'s, spec only (`CLAUDE.md` §0). No decision-maker ruling is needed |

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch;
  `uv sync --all-packages`.
- [ ] Confirm `RL-1311` is on `main`, Slices 2a, the validation-rule fix and 2 are closed, and
  DP-S3-1 and DP-S3-2 have resolvers; **stop if not**.
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

- [ ] Red first: Acceptance 5's cases (including M4's two) and Acceptance 6's resolve-time
  skip; Acceptance 9's monitoring-limb cases, including the call site passing the Environment
  (`backend/src/app/api/score.py:399-400`).
- [ ] The scope on `SettingDefinition`; the resolver's Environment argument (the request's
  Environment; none skips the layer); inspection; the audited write route
  (`PUT`/`GET /api/v1/environments/{slug}/settings`, `admin:manage_settings`).
- [ ] Declare the scope of each key made per-Environment; green; commit.

### Task 5: Keys per Environment (F54) and the rate limit (F48)

- [ ] Red first: Acceptance 4 and Acceptance 8.
- [ ] Create, rotate and revoke per Environment; the shared counter and its dependency on the
  scoring routes (per DP-S3-2); green; commit.

### Task 6: The ladder reconciliation, on every quote (FR-248, NFR-496)

- [ ] Red first: Acceptance 10's off-by-one ladder through `score_one` (the flag is True
  today), the FR-261 property, and the census of the raise site.
- [ ] `reconcile_ladder`'s new signature and every caller; the real risk premium;
  `ladder_check_version` on `Trace`, the regenerated contract, and the hand edit of
  `docs/contracts/schemas/scoring.schema.json` (`:66`, `:88`) with the contract guard quoted;
  the dated `03` §4.5 note; the false-positive control over every fixture and committed
  regression suite; the check on every quote,
  whatever the trace-sampling rate (red first with the rate at `0`); the dated FR-248 and
  NFR-496 clauses were made in Task 1; the docstrings; the failure as DP-S3-1 rules; green;
  commit.

### Task 7: The gate and the ledger

- [ ] The full two-half gate through the dev-commands slot wrapper with
  `LOKY_MAX_CPU_COUNT=4` (Acceptance 11); quote every rc, `N passed`, `HEAD`, `uptime`.
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
  monitoring-configuration limb, NFR-496's prod-sampling limb (decoupled to every quote by the
  maintainer's 15:17:54 BST decision) — are Acceptance 1, 4, 5, 8, 9 and 10. Its gate items —
  the two-replica test, the old one-key behaviour failing, the `uat` monitoring value leaving
  `prod` unchanged, the off-by-one ladder caught on the first quote — are Acceptance 8, 4, 9
  and 10.
- **`RL-1311` applied where it operates:** items 1 and 5 (Acceptance 5, Task 4), 2 (Acceptance
  2, Task 2), 3 (Acceptance 5), 3a (Acceptance 6, Task 3); its Acceptance bullets for Slice 3
  are Acceptance 5 and 6.
- **FD 9881** quoted verbatim (Acceptance 7) and placed in Task 3.
- **One premise found that changes the map's NFR-496 limb:** the reconciliation it asks to
  sample is vacuous at the tree above (premise g), so the map's own broken-input case (an
  off-by-one-penny ladder) would pass. Acceptance 10 makes the check real first; DP-S3-1 asks
  what a failure does.
- **Counts** carry their tree and predicate (premises f and h).
- **auditor-close1255's audit of `0149e3f2`** (NOT CLEAN, adopted by the lead): M1 (the
  signature change and every caller, Acceptance 10, Write set), M2 (**decided by the maintainer at 15:17:54 BST: decoupled, every quote, no DP-S3-4**;
  Acceptance 1's dated clauses, Acceptance 10's rate-`0` case), M3 (the call site and `resolve`'s signature, Acceptance 9, Write set),
  M4 (Acceptance 5's two cases), L1 (Acceptance 11's wrapper), L2 (`RL-1301` cited and in
  `relates:`), L3 (DP-S3-2's window and outage; the Architecture no longer fixes a window),
  L4 (premise h's count).
- **The maintainer's 15:13:26 BST entry:** DP-S3-3 resolved (a); the finding filed as
  working id 9949, cited in prose (premise g, Acceptance 10); and, relayed by the lead, the
  call-site red case and `ladder_check_version` with its reason (Acceptance 10).
- **auditor-close1255's re-audit of `0149e3f2..27ab8c00`** (M1–M4 and L1–L4 closed; N1–N4
  adopted by the lead): N1 (the hand-authored `scoring.schema.json`, Acceptance 10, Task 6,
  Write set), N2 (the check's inputs and comparison, the four kinds and the mode names, and the
  false-positive control, Acceptance 10, Task 6), N3 (`trace=True` for the call-site case, and
  an untraced failure's signal), N4 (DP-S3-1's premise refreshed, option (c) withdrawn).
- **Open:** DP-S3-1 and DP-S3-2, each for the decision-maker at medium effort.
