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
relates: [PL-1237, PL-1306, PL-1303, RL-1184, RL-1301, RL-1232, RL-1236, RL-1263, RL-1311, RL-1329, FD-1336, FD-1330, OQ-1316, OQ-1334, PL-1325, PL-1327]
---

# WK-674 Slice 3 — Environment isolation: leaf plan

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
- The second ruling this slice executes: **`RL-1329`** (DP-S3-5 decided; drafted under working
  id 9963, minted in mint batch 9, #1013), and the three records it binds this slice to:
  **`FD-1336`** (drafted as working id 9949: the vacuous check, the 4 dp drift, float money in
  the builder; HIGH, owner this slice), **`FD-1330`** (drafted as working id 9967: the clamp
  attributed to `office_premium`; MEDIUM, owner this slice) and **`OQ-1334`** (the merge gate,
  below). Each is read at `origin/main` `8cef871d4ec30869dc3ef20559f3cac64e239a5c`; the section
  *RL-1329 alignment* below carries every citation made at that tree. `03` FR-240 (`03:137`),
  FR-247 (`03:154`), FR-273 (`03:222`) and §4.4 (`03:414`) are read there too.

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
3. **DP-S3-1 and DP-S3-2 below resolved** (DP-S3-3 and DP-S3-5 are resolved).
4. **The lead's go.**

**Merge needs, beyond Acceptance 12** (a merge gate, not an activation need):
- **S3 does not merge until OQ-1334 is ruled (a), or (d) is ruled as the interim.** Source:
  `docs/roadmap.md`'s gate row "Before WK-674 Slice 3 merges" (`roadmap.md:1561` at
  `8cef871d`) and its dated note (`:1570`): "Slice 3's dispatch record carries that Slice 3 does
  not merge until OQ-1334 is ruled (a), or (d) is ruled as the interim." The row gates the
  merge, not the start: declared `decimal` outputs are out of this slice's scope (`RL-1329` §4).

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
   **`RL-1329`'s spec work** (verified at `8cef871d`): its own commits already added FR-240's
   dated clause (`03:137`), FR-248's dated clause (`03:155`), `LADDER_CLAMP_UNPLACEABLE` to §5.1's
   owned codes (`03:783`) and §4.4's dated note; the executor verifies each and does not reword
   it. This slice adds, in its spec commit:
   - **§4.4's example replaced** (`03:414`), in the same commit as the contract change of
     Task 6, "as the dated note added there" by `RL-1329` says — so this edit moves to Task 6's
     contract commit, not Task 1's;
   - **the OQ-1316 cross-reference note, byte-identical on both mirrors**: appended to the
     question cell of OQ-1316's row in `docs/open-questions.md` (`:138` at `8cef871d`) and to its
     row in `03` §10 (`03:1194` at `8cef871d`; the lead's brief said `~:1190`, re-verified), the
     text exactly:
     `*Cross-reference (added YYYY-MM-DD by WK-674 Slice 3, RL-1329): if this question is decided (a), an intermediate rounding recorded as its own ladder rung, RL-1329 §5 R0's "round appears only on the last rung" must be amended by that ruling.*`
     with `YYYY-MM-DD` the commit's date. Its content is `RL-1329`'s observation (`:953-956`
     at `8cef871d`, "This ruling interacts with OQ-1316"); the note carries it to the question
     it bears on. The row's status stays open. Command: `python3 scripts/audit-docs.py` exits
     0, and `grep -c -F "<the note, verbatim>" docs/open-questions.md
     docs/specs/03-rating-engine.md` prints `1` for each file.
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
    > *Superseded in part, 2026-09-30, by `RL-1329` ("What this record supersedes in the S3
    > plan", read at `8cef871d`).* Four sub-bullets below — **the signature changes**, **the
    > risk premium's source and check**, **the four operation kinds** and **the comparison** —
    > are replaced by `RL-1329` §5 (*Inputs*, R0–R4) and §3 (six kinds), and are marked
    > *superseded* where they stand. The **never sampled** sub-bullet's conclusion stands; its
    > rationale "it is integer arithmetic over a handful of rungs" becomes "exact decimal
    > arithmetic, in a context of at least 100 digits, over a handful of rungs". Everything
    > else in this item stands, as `RL-1329` says: the corrected premise; the false-positive
    > control (extended by item 13's stop counts); the call-site red case with `trace=True` and
    > the untraced failure's signal; the property red case; the raise-site census (the message
    > carries rung names and the difference, now a decimal string in minor units); and
    > `ladder_check_version`, whose value `2` means `RL-1329`'s predicate over `RL-1329`'s
    > shape (`RL-1329` §3). Item 13 is the acceptance for the superseded parts.
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
    - *(Superseded by `RL-1329` §5 Inputs — see the note above.)* **The signature changes** (auditor-close1255 M1). `reconcile_ladder` receives the
      **recorded operations** — each `LadderRung`'s `operation`
      (`LadderOperation`: `kind`, `factor`, `amount_minor`, `mode`, `dp`;
      `packages/model-schema/src/model_schema/scoring.py:108-135`) — and the **real** risk
      premium, the algorithm's own risk-premium output, never the first rung. **Its inputs and
      comparison, exactly** (auditor-close1255 N2, against `_build_ladder`,
      `packages/pricing-core/src/pricing_core/rating/score.py:551-624`):
      - *(Superseded by `RL-1329` §5 R1 and R2.)* **the risk premium's source and check.** The first rung carries **no** recorded
        operation (`operation = None`); its value is `_round_minor(raw, mode)` of the value the
        algorithm's `risk_premium_minor` output step consumes (for example `1304.8` → `1305`).
        So the check takes that **unrounded** output value and the step's declared rounding
        mode, rounds it once with that mode, and requires the first rung's `value_minor` to
        equal the result;
      - *(Superseded by `RL-1329` §3 and §5 R3–R4: six kinds, replayed on unrounded values.)* **the four operation kinds** (`LadderOperationKind`,
        `packages/model-schema/src/model_schema/scoring.py:63`), each replayed from the
        previous rung's replayed value: `multiply` → `apply_factor(prev, Decimal(factor), mode)`
        (`pricing_core/money.py:33`), whose `mode` takes the short names of `RoundingMode`
        (`money.py:20`: `half_even`, `half_up`, `ceiling`, `floor`, `down`), the same strings
        the operation records; `add` → `prev + amount_minor`; `round` at `dp = 0` → `prev`
        unchanged (a whole number of minor units is its own rounding); `none` → `prev`
        unchanged (the `constraints` rung, whose `applied` codes explain nothing numeric);
      - *(Superseded by `RL-1329` §5 R2–R4.)* **the comparison:** every replayed value equals that rung's recorded `value_minor`,
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
      it is ~~integer arithmetic~~ exact decimal arithmetic, in a context of at least 100
      digits, over a handful of rungs (`RL-1329`'s restated rationale) — and `rating.trace_sample_rate` governs
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
13. **`RL-1329` in full** — S3's acceptance, by the maintainer's decision relayed by the lead on
    2026-09-30 (~22:3x BST). **Every item of `RL-1329`'s section "Acceptance — the violation that
    must become detectable" (items 1–13) is an acceptance item of this slice, red first on
    `origin/main`** as that section requires ("S3 carries each item red first, shown failing on
    `origin/main`"), each in a named test the ledger quotes with its failing assert line. The
    record's text is the authority; the clauses below restate the ones that carry a number or a
    stop, **quoted from `RL-1329` at `8cef871d`**, and where this restatement and the record
    differ, the record wins.
    - **(a) The golden-rung stop predicate** (`RL-1329` Acceptance 8, second count, "ruled on the
      third re-audit, R1 … the **exact** form below is in force", as amended at the mint on the
      maintainer's entry "2026-09-30 17:14:16 BST"). For rung `i` of a golden quote, `new_i` is
      this slice's ruled value and `base_i` the baseline value; "the baseline is `origin/main`'s
      builder run on the same golden contexts at S3's base tree". **The slice stops if:**
      - on a `multiply` rung: **`|base_i − new_i| > 5 × 10⁻⁵ · |base_{i−1}| + (e_apply + e_ruled)`**
        minor units, where `base_{i−1}` is the previous rung in the baseline ladder;
      - on an `add` or a `round` rung, and on the first rung: **`|base_i − new_i| > e_apply +
        e_ruled`**, where on the first rung `e_apply` is the error of today's single rounding;
      - on a `constraints` rung where a clamp binds: **`new_i` is not exactly the bound**.

      `e` is "0.5 for a `half_*` mode, and 1 for `ceiling`, `floor` and `down`"; `e_apply` is that
      of the rounding today's builder applied (the step's mode passed to `apply_factor`, or to
      `_round_minor`), `e_ruled` that of the rung's declared `RoundSpec`. **"The comparison is
      evaluated in integers and `Decimal`, never in float."** The rung kind is the **baseline**
      ladder's recorded kind, because the bound is derived from the baseline's own mechanism
      (`RL-1329`: "Today's rung is `apply_factor(base_{i−1}, q_i)`"). **Any exceedance is
      reported to the maintainer, "with no looser fallback"**, and the slice stops. Command: the
      false-positive control's test (Task 6), which prints the exceedance count and the maximum
      tightness `(|diff| − (e_apply + e_ruled)) / (5 × 10⁻⁵ · |base_{i−1}|)` per rung kind, and
      exits non-zero on any exceedance. **Red on broken input:** with one baseline rung of one
      golden quote shifted to its bound + 1 minor unit, the test is shown red naming that rung.
    - **(b) The report line.** "if [`5 × 10⁻⁵ · |base_{i−1}| / |new_i|`] exceeds 2 × 10⁻⁴ on a
      golden quote (a factor below about 0.25), S3 reports it to the maintainer before it
      continues." The same test prints this ratio's maximum and the count above 2 × 10⁻⁴; a
      count above 0 halts the task until the maintainer's reply is quoted in the ledger.
    - **(c) The golden payable stop** (`RL-1329` Acceptance 8, first count, and §4): "golden
      quotes whose payable changes" — **a count above 0 stops the slice**, reported to the lead.
      The executor never edits a fixture and never edits a stored suite version; a re-baseline,
      if the lead routes one, is a **new** suite version whose `change_note` cites `RL-1329`, and
      "any golden re-baseline is dated and needs the maintainer's ACK".
    - **(d) Directed-mode tightness** (the 17:14:16 BST entry, as `RL-1329` quotes it): **"If
      S3's golden set contains a directed-mode rung, S3's first run records its tightness as the
      first measurement."** The bound is "validated on half_even only; directed modes are
      covered by derivation, not measurement". The ledger records, from the first run, either
      the directed-mode rungs' count and maximum tightness per mode, or the count `0` with the
      predicate that found none (every golden rung's declared and applied mode, verbatim).
    - **(e) Post-clamp served outputs, exact and rounded once, both cases** (`RL-1329` §4 C2 and
      Acceptance 13; the maintainer's entry "2026-09-30 16:41:11 BST — RL 9963 C2: declared
      outputs keep the POST-clamp served value; the acceptance is NOT widened"). Each declared
      output is served as "the engine's exact `string()` value of the output step's source …
      rounded once with that step's own `RoundSpec`", never the float and never a second rounding.
      - **clamped:** on FD-1330's min-premium quote, `/score` serves `office_premium_minor` =
        **5000**, the `constraints` rung's `value_minor` and the bound, not the office rung's
        1436. `RL-1329` says this case "is green today and must stay green", so **its red
        first is against a planted mutation**: a `_build_outputs` that serves the rung's
        `value_minor` gives 1436, and the test is shown red on it;
      - **unclamped:** the served output equals its ladder rung's `value_minor` exactly. Its red
        first on `origin/main` is the exact value: `RL-1329` Acceptance 1's
        `outputs["office_premium_minor"]` = **67358** (today 67357), and `FD-1336`'s
        served-outputs case, a scratch algorithm declaring `instalment_loading_minor`: **69402**
        after, **69399** today, with every `multiply`-kind rung output covered and
        `ipt_and_fees_minor` and `constraints_minor` kept as green controls (`FD-1336`
        *Disposition*, "Served outputs");
      - a test asserts the served value is built from the exact string read, not from the float,
        and a declared non-rung `money_minor` output is served as an integer from the exact
        string, red first because today it is the float from `result` (`RL-1329` S6).
    - **(f) The rest of `RL-1329`'s acceptance, by item:** 1 the realistic-scale red case
      through `score_one` with `trace=True` (61234.5 → 70726), and the auditor's case (60000.4 →
      69402) at unit level; 2 the scale sweep through a real ZEN evaluation, 1e3–1e7, 0–6
      optional rungs, float32 risk, ≥ 200 quotes per cell, **at least two recorded seeds**, one
      mixed-operation run, 100 % reconciled, **and the same sweep red over `origin/main`'s
      builder**; 3 the six planted-defect controls; 4 the near-tie prices 1235, not 1234, and a
      test fails if `_build_ladder` receives only floats (this is also `FD-1336` limb 3's one
      input-level test, scoped to `_build_ladder`, not the module, because `score.py` uses
      `float` legitimately for the elapsed-time parse); 5 the contract, with
      `PositionalDecimalStr` red first on `Decimal("0.0000001")`, `Decimal("1.2E-28")` and
      `Decimal("1E+1")`; 6 the three §5 shapes; 7 the re-derivation test's `round` branch
      (`test_rating_score.py:224-225` at `8cef871d`) replaced by R4 (`FD-1336`'s F4); 8 the
      false-positive control's three stop counts, of which (a)–(c) above are two, the third
      being "quotes on which a clamp's comparison and disposition disagree" (a count above 0
      stops the slice for the lead); 9 `scripts/bench-rating.py` before and after, in the
      ledger, no budget changed; 10 the binding clamp (`FD-1330`), including a `max` clamp and a
      step declaring both bounds, the replacement of
      `test_a_clamp_overrides_the_ladder_and_is_recorded_on_the_constraints_rung`
      (`test_rating_score.py:262` at `8cef871d`), and the placement refusal with
      `LADDER_CLAMP_UNPLACEABLE` on its three algorithms, both at save and by `compile_bundle`,
      with `_check_clamp_placement` registered in `ALGORITHM_CHECKS` so #967's closure test (ii)
      passes, and the count of committed fixture algorithms and reachable stored bundles it
      refuses (above 0 stops the slice); 11 the engine-precision guard on `zen-engine` 0.53.0;
      12 the release-note line in the squash-commit body and the ledger; 13 is (e) above.
    - **(g) `FD-1330`'s factor.** `FD-1330`'s acceptance says the office rung keeps "`multiply`
      factor **1.1000**"; `RL-1329` records the factor unquantised ("×1.1", "never quantised to
      4 dp"). **`RL-1329` governs**: the test asserts `Decimal(factor) == Decimal("1.1")` and
      that the recorded string carries no 4 dp padding.

## Global Constraints

- **Money is integer minor units, or `Decimal` in the rating path — never float** (`CLAUDE.md`
  §7). ~~the reconciliation compares integers.~~ *(Superseded 2026-09-30 by `RL-1329`:)* the
  reconciliation compares integers at the payable and the displays (R2, R4), and exact decimals
  on the chain (R1, R3); every value crossing the binding for ladder or payable arithmetic is the
  engine's `string()`, never the float (FR-273's string limb).
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
| `03` §3.4 | FR-240 | `RL-1329`'s dated clause: a clamp the ladder cannot place is refused at save and at compile, `LADDER_CLAMP_UNPLACEABLE` (Acceptance 13 (f), item 10) |
| `03` §3.6 | FR-247 | The `constraints` rung records a binding clamp as `clamp` (`FD-1330`; Acceptance 13 (f), item 10) |
| `03` §3.6 | FR-248 | As amended by `RL-1329`: exact unrounded values, true operations, one rounding (Acceptance 13) |
| `03` §3.8 | FR-261 | The "ladder reconciles" property takes the scoring-time verdict with its independent inputs, never rebuilding the anchors from the ladder it checks (`RL-1329` "What it obliges") |
| `03` §3.11 | FR-273 | The string limb: ladder, payable and declared `money_minor` outputs read through `string()`, never the float (`FD-1336` limb 3; Acceptance 13 (e), (f) item 4) |

**Carried obligations placed here:** register F54 (Acceptance 4); register F48 (Acceptance 8);
`RL-1311` items 1, 2, 3, 3a and 5 (Acceptance 2, 5, 6); FD 9881 (Acceptance 7); `RL-1232`
DP-2's per-Environment default-off setting **as `RL-1311` bounds it** — this slice builds the
scope machinery and proves it on a test-registered Environment-only key; the FR-270/FR-271
flags themselves are declared by Slice 6 (`RL-1311` item 3, "Slice 6 declares the two flags").
**Also placed here (2026-09-30, `RL-1329` alignment):** `RL-1329` in full (Acceptance 13, Task
6); `FD-1336` limb 1 — `reconcile_ladder` runs on every scored quote in every Environment, never
sampled, with the NFR-496 prod-sampling limb decoupled, and the write-set additions its
*Disposition* names (`pricing_core/__init__`, `rating/properties.py`, the census tests; all
already in the table below) — and limbs 2 and 3 and F4 (Acceptance 13 (f), items 1–4 and 7);
`FD-1330`, the clamp attributed to `constraints` (Acceptance 13 (f), item 10, and (g)); the
OQ-1316 cross-reference note (Acceptance 1); and OQ-1334's merge gate (Status).

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

### Write set added by `RL-1329`, and its contention (at `8cef871d`)

`RL-1329` ("What it obliges", "S3's write set gains") adds the rows below; each cell was read at
`origin/main` `8cef871d4ec30869dc3ef20559f3cac64e239a5c`. **#967's code slice has merged**
(`3a5f7cd5`, #1012): `ALGORITHM_CHECKS` exists (`compile.py:247`), `validate_algorithm` runs it
(`:253`, `:277`), and `RATING_ERROR_CODES` is `errors.py:297`. So `RL-1329`'s ordering
condition ("S3's `compile.py` edit starts only after #967's code slice has merged", and the same
for `errors.py`) is **met at this tree**; the executor re-verifies it in Task 0.

| Path | This slice | Existing definitions edited |
|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | **appends** `_check_clamp_placement(algo: RatingAlgorithm) -> list[ValidationIssue]` and **one entry** to `ALGORITHM_CHECKS` (`:247`); one import from `rating/ladder.py` | the `ALGORITHM_CHECKS` tuple (one entry), the import block. The check reads only `on_violation`, `consumes`, `produces` of a `constraint` step and the output steps' `output_name` and `consumes` (#967's closure 3c (i)) |
| `packages/pricing-core/src/pricing_core/rating/ladder.py` | **new**: `_RUNG_ORDER`, `_output_steps_by_name` and the `<rung>_minor` naming, moved out of `score.py`; imports only `model_schema` | — (new file) |
| `packages/pricing-core/src/pricing_core/rating/score.py` | the mapping moved out (`_RUNG_ORDER` `:226`, `_output_steps_by_name` `:576`); `_build_ladder` (`:582`), `_round_minor` (`:566`), `_build_outputs` (`:657`), the `reconcile_ladder` call (`:769`), and the "Ladder construction" docstring (`:62-103`) | all of these (existing definitions) |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | `to_wire` (`:344`)'s generated `string()` read; `_constraint_node` (`:264`)'s `__before`, `__min`, `__max` reads | `to_wire`, `_constraint_node` |
| `packages/model-schema/src/model_schema/money.py` | **new** `PositionalDecimalStr`, beside `DecimalStr` (`:85`); `DecimalStr` and `Relativity` (`:94`) untouched | none (an addition) |
| `packages/model-schema/src/model_schema/scoring.py` | `LadderOperationKind` (`:63`), `LadderOperation` (`:108`), `LadderRung` (`:127`) per `RL-1329` §3, beside the plan's `Trace.ladder_check_version` | those three, plus `Trace` (already in the table above) |
| `docs/contracts/schemas/scoring.schema.json` (hand-authored) | `RL-1329` §3's fields, and the invariant text (`:60`) | the ladder definitions (already a row above) |
| `backend/tests/test_contracts.py` | the contract guard run; a comparison added only if the guard needs one | only if a comparison is added |
| `backend/src/app/errors.py` | **one member** `LADDER_CLAMP_UNPLACEABLE` appended to `RATING_ERROR_CODES` (`:297`) | that frozenset (one member) |
| `packages/pricing-core/tests/test_rating_score.py` | the re-derivation test's `round` branch (`:224-225`) replaced by R4; `test_a_clamp_overrides_the_ladder_and_is_recorded_on_the_constraints_rung` (`:262`) replaced; new tests | those two tests |
| `packages/pricing-core/tests/test_rating_compile.py`, `backend/tests/test_rating_algorithms.py` | the placement refusal's tests, **appended** | none |
| `docs/specs/03-rating-engine.md` §4.4 (`:414`) | the example replaced (Task 6's contract commit) | §4.4 |
| `docs/specs/03-rating-engine.md` §10 (`:1194`) and `docs/open-questions.md` (`:138`) | the OQ-1316 note appended to one row in each | OQ-1316's two mirror rows |

**Against WK-690 Slice 2** (`PL-1327:90-129`, its write set, measured by it at `11c76b6c`).
It writes `pricing_core/modelling/` (`objectives.py`, the new `expression_objective.py`,
`errors.py`), `model_schema/objectives.py`, `model_schema/__init__.py`, the hand-authored
`docs/contracts/schemas/objective-certificate.schema.json`, `scripts/bench-model.py`,
`docs/specs/02-modelling.md`, and `backend/tests/test_contracts.py` "if the guard needs a new
comparison". **The one possible shared existing file is `backend/tests/test_contracts.py`**,
and only if both slices add a comparison there; each would add its own function, and no
existing function is edited by both, which the dispatch record must name with that check
(`RL-1263`'s exception). `model_schema/__init__.py` is shared only if this slice exports
`PositionalDecimalStr`; the plan does not need it to (the ladder fields import it from
`model_schema.money`), and **if the executor adds an export, that row serialises**. The generated
contracts and `docs/INDEX.md` are exempt. **Also:** WK-690 S2's Task 6 is an NFR-476 timing
measurement that "runs alone" (`RL-1263` item 3), and this slice's `bench-rating.py` run
(Acceptance 13 (f), item 9) is a measurement too, so **the two measurements never share a
window**, and neither runs beside the other slice's build.

**Against WK-1250 Slice 1** (`PL-1325:141-175`, its contention table; `:176-186`, the existing
definitions it edits). It edits `compile.py`'s `_producer_types` and `_check_result_types`
(kept registered in `ALGORITHM_CHECKS`, with its signature, `PL-1325:132`, `:660-664`) and adds
public entry points to `compile.py`'s `__all__`; it also edits `rating_algorithms.py`'s
`_parse_algorithm`, `model_schema/rating.py`'s `_graph_invariants`, `model_schema/__init__.py`,
`03` §2, §4 (a new subsection) and §5.1, and `scripts/generate-contracts.py`. Its set
excludes "`compile_bundle`, `score.py`, `TraceStep`, `runtime.py`, any `approvals.py`,
`errors.py`" (`PL-1325:186-187`). **Shared file: `compile.py`.** No function is edited by
both: this slice appends one new function and edits the `ALGORITHM_CHECKS` tuple and the
import block; WK-1250 S1 edits `_producer_types`, `_check_result_types` and `__all__`, and
does not plan to edit the tuple. **The tuple and the import block are the lines at risk**: if
WK-1250 S1's diff touches either, the two serialise. **Shared file: `03`.** Sections are
disjoint (this slice: §3.6's FR-248 clause, §9's NFR-496 clause, §4.4, §4.5's note, §10's
OQ-1316 row; WK-1250 S1: §2, §4's new subsection, §5.1). §4.4 and §4.5 are existing
subsections inside §4, where WK-1250 S1 adds a new one, so that pair is checked on the actual
diffs at dispatch. `model_schema/__init__.py` as above. `test_rating_compile.py` and
`test_rating_algorithms.py`: appended tests on both sides, no existing test edited.
**Verdict for the lead:** this slice can build beside WK-690 S2, provided the dispatch
record names `test_contracts.py` with the no-shared-definition check and keeps the two
measurements apart. Beside WK-1250 S1, the only shared definitions possible are the
`ALGORITHM_CHECKS` tuple and `compile.py`'s import block. The dispatch record names them and
checks both diffs. If either slice's actual diff edits a definition the other edits, they
serialise (`RL-1263`: "any other shared path serialises unless the lead's dispatch record names
the path and the check").

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S3-1 | **What does a failed ladder reconciliation do at scoring?** The check runs on every scored quote in every Environment (FR-248 and NFR-496 as this slice's dated clauses amend them, on the maintainer's decision `2026-09-30 15:17:54 BST — audit round-up: decisions`); `LADDER_RECONCILIATION_FAILED` is registered (`errors.py:326`) and raised nowhere; the spec does not say whether a failed check refuses the quote | (a) Refuse the quote with `LADDER_RECONCILIATION_FAILED` (500, a platform fault), and record it; (b) serve the quote, record the failure on the trace (when there is one) and in the log, and alert; ~~(c) refuse outside `prod`, record-and-serve in `prod`~~ *(withdrawn 2026-09-30: it reintroduces the `prod` special case the maintainer's decision removed; auditor-close1255 N4)* | **(a).** A ladder that does not reconcile is a premium the platform cannot explain (NFR-496: "no rounding is applied more than once … to the penny"); serving it is the silent mispricing `CLAUDE.md` §2 warns of, and a refusal is also the one signal that surfaces an untraced failure without a log search | decision point | yes — Task 6 | *open* — for the decision-maker at medium effort (rating correctness, not governance evidence) |
| DP-S3-2 | **The rate-limit counter's key and limit.** NFR-499 asks "per-client rate limits"; FR-430 asks "independent … rate limits" per Environment; F48 fixes the mechanism (a shared Redis counter, per tenant); `rate_limit_rps` is optional on an account (`service_accounts.py:65`) | (a) One counter per (Environment, Service Account), limit the account's `rate_limit_rps`; an account without one is unlimited; (b) as (a), with an Environment setting `scoring.default_client_rate_limit_rps` (workspace or Environment scope) as the limit for accounts without their own; (c) a per-Environment aggregate cap as well as the per-client counter | **(b).** Keying by Environment makes the limits independent per Environment (FR-430); the per-account value is NFR-499's per-client limit; and the Environment default closes the "no limit at all" case for accounts created without one, while staying a Setting (FR-431). (c) is a capacity control no requirement asks for. **Also to rule: the window and the Redis-outage behaviour** (auditor-close1255 L3). Window: a fixed one-second window (`INCR` + `EXPIRE`) is the simplest shared counter; a sliding window is fairer at the boundary and costs a sorted set per key. Outage: **fail open** (serve, log and count each unlimited request) keeps scoring available when the cache is down (`03` NFR-497's availability target), at the cost of no limit during the outage; **fail closed** (refuse with 503) keeps the limit and turns a cache outage into a pricing outage. Planner's input: fixed window, fail open with the event logged and counted — a rate limit protects capacity, and an outage of the limiter should not take pricing down with it | decision point | yes — Task 5 | *open* — for the decision-maker at medium effort |
| DP-S3-3 | **What is FR-430's "monitoring configuration" in Phase 2?** No monitoring-configuration key exists (premise h), and the monitors are WK-687's (Phase 4); `PL-1237` Task 3 limits this slice to "the per-environment *configuration* only" | (a) The per-Environment trace sampling rate, `rating.trace_sample_rate` (`settings.py:196`, the input `05` monitors read), declared workspace-or-Environment, plus the scope mechanism for WK-687 to declare its own keys; (b) new monitoring keys now; (c) the mechanism only, with no key declared | **(a).** It is the one monitoring input configured today, it is named by FR-431 ("sampling rates"), and it gives the limb's test a real key. (b) builds ahead of Phase 4 (`CLAUDE.md` §9); (c) leaves the limb with nothing to prove | scope | yes — Task 4 | **Resolved (a), ruled by the maintainer as scope** (`2026-09-30 15:13:26 BST — DECISIONS: the reconcile_ladder FD (MEDIUM, WK-674 S3); DP-S3-3 → (a), ruled by me as scope`): `rating.trace_sample_rate`, workspace-or-Environment, plus the mechanism; anything wider is `05`'s, spec only (`CLAUDE.md` §0). No decision-maker ruling is needed |
| DP-S3-5 | **How does the premium ladder record each rung so that it shows the true operations and still reconciles to the penny?** (Raised by auditor-close1255's N5, folded into `FD-1336` as limb 2; routed by the maintainer to a fresh high-effort decision-maker.) *Row added 2026-09-30: the plan at `06e3e896` did not carry it as a row.* | as posed in `RL-1329` §1: (a) build each rung from the previous rounded rung; (b) a final residual `adjust`; the maintainer's steer (exact unrounded values, true factors, one rounding) | — (the planner's input predates the row) | decision point | yes — Task 6 | **Resolved by `RL-1329`** (minted from working id 9963): neither (a) nor (b); the steer adopted with three departures (the string read, the 10⁻²⁶ per-rung tolerance, `divide`) and the `clamp` kind. Its acceptance is this slice's Acceptance 13 |
| DP-S3-6 | **Which stop bound applies to a rung that is `none` in the baseline ladder** (the `office_premium` checkpoint when unchanged, `constraints` when no clamp binds)? `RL-1329` Acceptance 8 names bounds for `multiply`, `add`, `round`, the first rung and a binding clamp, and is silent on `none` | (a) the bound of the nearest earlier rung that is not `none`, because a `none` rung copies its predecessor's value in both ladders (`RL-1329` §2 step 3; `score.py`'s checkpoint convention), so its difference is its predecessor's; (b) exact equality with the predecessor's difference, `abs(base_i − new_i) == abs(base_{i−1} − new_{i−1})`, which is what (a) implies and is stricter | **(b)**: it follows from the construction without a new constant, and a violation would mean the rung is not a copy, which R1 should already refuse | decision point | no — resolved at Task 6 step "the false-positive control"; **default (b)** until ruled, and the ledger records the count of baseline `none` rungs | *open* — for the decision-maker at medium effort |

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
- [ ] Re-verify the `RL-1329` write-set rows at the executor's tree: `ALGORITHM_CHECKS` exists
  in `compile.py` and `validate_algorithm` runs it (the ordering condition), `RATING_ERROR_CODES`
  in `errors.py`, and every line cited "at `8cef871d`". Record OQ-1334's state (the merge gate).

### Task 1: Spec — `07` §4.2–§4.4, §5.1, §5.2

- [ ] Acceptance 1's edits through `spec-change`, including the OQ-1316 note on both mirrors
  (its `grep -c -F` prints `1` per file) and not §4.4's example (Task 6);
  `python3 scripts/audit-docs.py`; commit.

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
- [ ] **`RL-1329`, red first on `origin/main`** (Acceptance 13), in this order, each commit
  green on its own:
  1. **The contract:** `PositionalDecimalStr` in `model_schema/money.py` (red first on the
     three values of Acceptance 13 (f), item 5); `RL-1329` §3's fields on `LadderOperation` and
     `LadderRung`, the hand-authored `scoring.schema.json` in step, `generate-contracts.py
     --check` and the contract guard quoted; **§4.4's example replaced in this commit**; commit.
  2. **The mapping moved:** `pricing_core/rating/ladder.py` created with `_RUNG_ORDER`,
     `_output_steps_by_name` and the naming; `score.py` imports it; no behaviour change (the
     existing suite green, quoted); commit.
  3. **The reads:** `to_wire`'s `string()` read and `_constraint_node`'s `__before`, `__min`,
     `__max` reads (`runtime.py`); commit with the tests of Acceptance 13 (f), items 4 and 11.
  4. **The builder, `_build_outputs` and the predicate:** `RL-1329` §2, §4 and §5 in
     `score.py`, `reconcile_ladder` and every caller (`score.py:769`, `properties.py:303`,
     `pricing_core/__init__.py:31` at `8cef871d`); the FR-261 property takes the scoring-time
     verdict with its independent inputs; red first for Acceptance 13 (e) and (f), items 1–3,
     6, 7 and 10; the docstrings (`score.py:62-103`, `model_schema/scoring.py`'s
     `LadderOperation` and module docstrings); commit.
  5. **The placement refusal:** `_check_clamp_placement` appended to `compile.py`,
     one entry in `ALGORITHM_CHECKS`, `LADDER_CLAMP_UNPLACEABLE` appended to
     `RATING_ERROR_CODES`; red first on the three algorithms, at save and at `compile_bundle`;
     the refused-fixture count; commit.
  6. **The sweep and the false-positive control:** Acceptance 13 (f), item 2's sweep (≥ 2 seeds,
     and red over `origin/main`'s builder); the three stop counts with (a)–(d), DP-S3-6's rule
     applied to baseline `none` rungs; any count above 0 stops the task for the lead or, for (a)
     and (b), the maintainer; commit.
  7. **The bench** (`scripts/bench-rating.py` before and after, in a solo window, `RL-1263`
     item 3) and the release-note line drafted for the squash body and the ledger (Acceptance 13
     (f), items 9 and 12).

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
- **`RL-1329` alignment (2026-09-30, at `8cef871d`)**, on the lead's brief: Acceptance 13 is
  `RL-1329` in full, with its stop predicate, report line, golden payable stop, directed-mode
  clause and served-output cases quoted from the record; Acceptance 10's superseded parts are
  marked as `RL-1329`'s supersede table names them; the Global Constraints money line restated;
  `FD-1336` (limbs 1–3, F4 and served outputs) and `FD-1330` placed; the OQ-1316 note
  (Acceptance 1); OQ-1334's merge gate (Status); the added write set with its contention against
  WK-690 S2 (`PL-1327`) and WK-1250 S1 (`PL-1325`); DP-S3-5 recorded as resolved; DP-S3-6
  raised (the baseline `none` rung, on which `RL-1329` is silent). Three places where the
  record and the brief's paraphrase differed, `RL-1329` followed: the directed-mode clause is
  conditional ("If S3's golden set contains a directed-mode rung"); the clamped served-output
  case is green on `origin/main` and red first only against a planted mutation; and `FD-1330`'s
  "1.1000" is `RL-1329`'s unquantised "×1.1".
- **Open:** DP-S3-1 and DP-S3-2, each for the decision-maker at medium effort; DP-S3-6,
  non-blocking with a default.
