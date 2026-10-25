---
id: PL-8227
family: plan
kind: map
title: WK-1178 — the open-HIGH slices. FD-1729 split into S1a and S1b (SL-1771 re-cut), FD-1610 limb 2 as S2 (trace the dropped feature_map keys, then refuse a dropped required input), FD-1754's unread GBM Factor types as S4 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides each slice's PR
created: 2026-10-25             # filed under working id 8227
owner: planner
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1769, SL-1771, FD-1729, FD-1610, SL-1541, FD-1754, SL-1758, PL-1856, SL-1569, FR-44, FR-222, FR-239, FR-240]
---

# PL 8227 — WK-1178: the open-HIGH slices S1a, S1b, S2 and S4 (a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md`
> §1.6, PL row: one plan per Work, slices as rows, no per-slice leaf; a change is one dated delta, a
> new `PL-` that `relates:` the Work's plan). WK-1178 has no Work plan, so, as `PL-1769` and `PL-1856`
> did, this delta `relates:` the records it builds on. It cuts **four slice rows**: S1a and S1b
> (a re-cut of `SL-1771`, whose plan `PL-1769` stays frozen and unedited), S2 and S4. **S3** (PL-1856
> slice B) is already planned in `PL-1856` and is **not** in this delta. REQUIRED SUB-SKILL:
> subagent-driven-development (recommended) or executing-plans, task by task; steps use checkbox
> (`- [ ]`) syntax. Each executor also binds:
> - `test-driven-development`: every red is seen red **by its cause** at the slice's base, its line
>   in the `LG-` before the fix;
> - `python-test`: the `req` marker on every new test, and the negative tests;
> - `python-package`: `pricing-core` stays standalone (ADR-703), `model-schema` owns every shape;
> - `spec-change`: every task headed "spec" lands before or with the code (`CLAUDE.md` §0);
> - `contract-schema` and `contract-guard`: S2's `TraceStep` field;
> - `postgres-pro` (evidence only) and `dev-commands` (the two DSNs, the DB window): S1a and S1b;
> - `git-hygiene`.
>
> Each executor is spawned from `.claude/roles/executor.md` and reads
> [`README.md`](README.md)'s five unchecked conventions before the first step.

Filed under **working id 8227**, reserved by lead 28 for seat planner-8227 (brief
`handover/brief-planner-8227-2026-10-25.md`; reservation noted with no objection at the maintainer's
entry "2026-10-25 11:42:00 GMT"). **The slice rows have no working ids**: the `SL-` and `LG-` ids are
**to reserve at GO**, one pair per slice, by the lead (see "Hand-off"). Written 2026-10-25 by the
planner (seat planner-8227, Opus 5.5, effort medium). **Tree read:** `origin/main`
`ff976406f1bf133cfe040d2c44d383011503988a` (#1369). Every `file:line` below is at that tree unless
marked otherwise; each executor re-reads its own at its base (Task 0 of its slice).

## Authority

Read in full in `~/gi-pricing-plan.local/channel/to-lead.md` on 2026-10-25 between 11:41 and 11:47 GMT.

- **"2026-10-25 11:40:12 GMT — Maintainer: FD-1610 limb 2 — (d) now, then (c) gated on a zero
  exposure query, one slice S2; open-HIGH triage accepted; R-close acceptance line"**, by the
  maintainer, verbatim (items 1 to 3; item 4, R-close, is the auditor's and not this plan's):
  > - **FD-1610 limb 2 — ruled (d) then (c), in one slice S2, in that order.** (d) first: every `feature_map` key the runtime drops at `runtime.py:760-761` is recorded in the trace as an additive field; price and hash unchanged (FR-239 holds by construction). Then (c): a dropped key that feeds a **required** model input raises a coded, input-free scoring error — **only after the essay's exposure query returns 0** stored Rating Versions whose `model_call` keys exceed their context, run on the real DB inside a granted window and its result line in the LG with `head=`. If the query returns > 0, S2 stops after (d) and the (c) decision comes back to me with the hit list. (a) is refused (a silent drop in a pricing path), (b) is wider than the compile rule enforces.
  > - **Conditions:** red first for both parts (a pre-SL-1541 bundle with an unmapped required key scores green on base, must refuse after (c)); a dated line under `03` FR-222 for the refusal and one for the trace field; if the trace shape is a `model-schema` type, the field is added there and `docs/contracts/` regenerated, never hand-written. **S2 runs after SL-1569 merges**, and the lead reads SL-1569's diff for `runtime.py` before ordering S2 — the planner's "not verified" stays open until then.
  > - **Triage accepted:** S1 (FD-1729 = SL-1771, critical path, DB windows in no-gate gaps, merge before 4 Nov), S3 (PL-1856 slice B, cut it), S4 (FD-1754 probe), FD-1495 carried, FD-1836/FD-1411 under RL 8218. One WK-1178 plan delta for S1's split and S2/S4 as new slices — bring the GO requests after the gate chain as planned.
- **The triage proposal** the entry accepts: `~/gi-pricing-plan.local/scratch/hifd-proposal-2026-10-25.md`
  (seat planner-hifd, at `ff976406`), §2 S1, S2 and S4 and §3's order. Where this plan departs from
  it, the departure is named in place (S1's compose run, DP-S1; the settings row, S1a's spec touch).
- **The remedies already ruled for FD-1729**: `PL-1769` (frozen, `active`), its S-b tasks 0 to 7 and
  Acceptance 8 to 13, with DP-14 to DP-22 ruled at the maintainer's (by delegation) entries
  "2026-10-14 12:18:57 BST", "12:42:33 BST", "13:21:41 BST" and "13:27:39 BST". This delta
  **re-cuts** those tasks into two slices; it changes no ruled remedy.
- **Lean P2 L1** (the maintainer's entry "2026-10-08 11:51:58 BST" as corrected at "12:02:08 BST"):
  `draft` → `active` rides each slice's PR.

## Goal

Every open HIGH finding the triage left without a live slice gets a slice row a fresh executor can
start from at its GO, sequenced against today's queue:

- **FD-1729** (HIGH; the application connects as the superuser table owner, so FR-44's privilege
  layer is inert): `SL-1771` re-cut into **S1a** (the login role, the two DSNs, the fixtures as the
  login role, the grants red first in one migration) and **S1b** (the startup refusal, the
  trigger-tamper proof, the exact grant map). Both merged before the **4 Nov P2 code freeze**.
- **FD-1610 limb 2** (HIGH, latent; `runtime.py:758-762` drops a `feature_map` key that is not in
  the scoring context, silently): **S2**, (d) then (c), exactly as 11:40:12 orders.
- **FD-1754's open limb** (HIGH; "interaction, spline, polynomial and expression Factors on a GBM,
  unread"): **S4**, a probe, then the refusal set extended only if a type misprices silently.

## Evidence at `ff976406` (read for this plan)

- **E1, the drop.** `packages/pricing-core/src/pricing_core/rating/runtime.py:758-762`, in the
  `model_call` handler: `feature_row = {feature_slug: context[graph_name] for graph_name,
  feature_slug in step.feature_map.items() if graph_name in context}`; `context` is
  `request.input` without `"$nodes"` (`:755`). A refusal from the handler goes out as data through
  `_model_call_failure` (`:120`), because the zen binding swallows a handler's exception
  (`:126-133`); a coded error inside the handler reaches the quote as `MODEL_CALL_FAILED` naming
  the code, as `MODEL_CALL_FEATURE_COLLISION` does (`PredictionError` at `:837-842`, caught at
  `:775`, re-coded at `:785-789`).
- **E2, "required".** `compile.py:958` `check_model_call_coverage` (FR-240, `RL-1523`) takes a
  model's required inputs as `required_model_inputs(pin.factors, order)`
  (`modelling/factors.py:505`) with `order` the fit result's `feature_order`, and refuses an unmapped
  one with `MODEL_CALL_FEATURE_MAP_INVALID`. The runtime has no such check: a bundle compiled before
  `SL-1541` (whose inliner renamed `feature_map` values, FD-1610 limb 1) or built on a path that
  skipped compile can carry a key no step produces.
- **E3, the trace is a model-schema type.** `model_schema/scoring.py:172` `TraceStep` (`step_id`,
  `type`, `label`, `consumed`, `produced`, `matched`, `violation`, `elapsed_us`) inside `Trace`
  (`:192`). It is built in one place, `pricing_core/rating/score.py:847` `_build_trace`, from the
  engine trace and the inlined algorithm; `consumed` is the engine entry's `input`. It is stored
  whole (`backend/src/app/platform/traces.py:121`, `:253`, `trace.model_dump_json()`). Its
  hand-authored contract is `docs/contracts/schemas/scoring.schema.json`; the generated ones are
  `docs/contracts/schemas/generated/score-comparison.schema.json` and
  `docs/contracts/openapi/generated.json`. `trace_diff.py:20` `_COMPARED` lists the compared
  fields, typed by `scoring.py:231` `TraceStepField`; `03` §4.10 (`:954`) says `elapsed_us` "is
  recorded and never compared".
- **E4, stored bundles.** `rating_versions.bundle` is `JSONB`, nullable (`backend/src/app/db/models.py:2328`).
  The precedent exposure read is `LG-1608` (SL-1541) `:91-92`: read-only `select` against the dev DB
  `gipricing` in `gi-pricing-postgres-1`. FD-1610's essay (`:83`) states the query's predicate in
  words only ("every stored Rating Version whose `model_call` keys exceed what its context can
  hold"), so S2 writes it (Task S2-C0).
- **E5, the GBM refusal set.** `modelling/factors.py:533-547` `gbm_transformed_factors`, the one
  definition: `factor.type in (FactorType.BANDING, FactorType.GROUPING)` at `:546`; used by the
  compile check (`compile.py`, `check_model_call_gbm_factors`) and the save check
  (`backend/src/app/platform/rating_algorithms.py`). `FactorType` (`model_schema/modelling.py:89`)
  also has `INTERACTION`, `SPLINE`, `POLYNOMIAL`, `EXPRESSION` (and `IDENTITY`, `OFFSET`). Tests:
  `packages/pricing-core/tests/test_rating_gbm_banded_refusal.py` and
  `backend/tests/test_rating_gbm_banded_save.py`, the second **without a database** (its `:6`).
- **E6, the settings row.** `git grep -n "GIP_DATABASE_URL\|database_url" -- docs/specs` prints
  0 lines at `ff976406`: no spec row names a DSN today. The proposal's "a `07` FR-447
  settings-table row" therefore has no row to amend; `PL-1769` Step 7.1's own rule stands ("the
  census decides whether `07-platform.md` also names the DSN").
- **E7, today's queue, read-only** (`git diff --name-only origin/main...origin/<branch> -- ':!docs'`,
  each at the remote head read on 2026-10-25 ~11:45 GMT):
  - `sl-1569-wk1178-decimal-outputs` @`aab18283`: `model_schema/scoring.py` (hunks at `Trace` and
    `ScoringResult`), `pricing_core/rating/score.py` (hunks at `:794-866` and `:1024-1110`, beside
    `_build_trace` at `:847`), `rating/ladder.py`, `backend/src/app/api/score.py`,
    `backend/src/app/platform/traces.py`, `backend/tests/test_contracts.py`, and tests. **It lists
    no `runtime.py` at that head**; the lead's read of its `runtime.py` diff (11:40:12) is still the
    lead's to do at its merge head.
  - `draft/pl-8205` @`4c86ee9d`: docs only; its plan's write set names
    `model_schema/rating.py`, `test_graph_invariant_issues.py`, `MountInspector.vue` and the
    generated client.
  - `sl-1552-wk675-s10` @`6cdec296`: frontend only (`RatingVersionListView.vue`,
    `api/environments.ts`). `sl-1553-wk675-s11` @`03b087c0`: docs only.
  - `sl-8166-wk1178-pl8162-a` (#1368, PL-1856 slice A, its slice id minted on that branch, not yet on `main`) @`ce6eb64e`:
    `model_schema/modelling.py`, `model_schema/diagnostics.py`, `model_schema/__init__.py`,
    `pricing_core/modelling/{glm,diagnostics,comparison}.py`, tests and frontend; **not**
    `modelling/factors.py`.
  - `sl-8185-wk1178-fd8177-scoped-writes` @`3bf60a96`: `backend/src/app/api/{authz,datasets,validation}.py`,
    `backend/src/app/platform/{datasets,validation}.py`, and tests.

## Decision points

Two open choices, each with a recommendation. Neither blocks S4; DP-S1 blocks S1a's GO, DP-S2 blocks
S2's GO. The plan stays `draft` while either is open.

### DP-S1 — where the compose run on a fresh volume goes

S1a changes what the application connects as (`config.py`'s default DSN, compose's environment, the
CI DSN: `PL-1769` Task 2), so after S1a merges, a stack brought up from `main` connects as
`gip_app_login`. The proposal put the compose run (`PL-1769` Task 6) in S1b.
- **(i) As proposed: S1b.** S1a is smaller. Between the two merges, `main` carries a deploy change no
  fresh-volume run has proved, and the shared stack comes up from tools-main fast-forwarded to `main`
  (seat brief item 20).
- **(ii) S1a runs it; S1b re-runs it only if S1b edits `deploy/`.** The slice that changes the DSN
  proves it. S1a grows by one DB-window step.

**Recommendation: (ii).** A deploy change merged unproved is the class the run exists to stop, and
item 20 makes `main` the stack's source. `PL-1769` Step 1.5 (compose binds to `127.0.0.1`, a
`deploy/` edit applied to the shared stack only as a GO-time act the maintainer names) goes with
S1b under either option.

### DP-S2 — the two new names, and whether the trace field is compared

The 11:40:12 ruling fixes the behaviour and leaves the names open.
- **The code** for (c): (i) `MODEL_CALL_REQUIRED_INPUT_ABSENT`, raised inside the handler and
  surfaced through `_model_call_failure` as `MODEL_CALL_FEATURE_COLLISION` is (E1); (ii) no new code,
  `MODEL_CALL_FAILED` with the cause in words. **Recommendation: (i)**: the precedent of FD-1753's
  backstop, and a code a test can assert by cause.
- **The field** for (d): (i) `TraceStep.dropped_inputs: list[str] | None = None`, set only on a
  `model_call` step, the dropped graph names sorted; (ii) the same under `matched`, with no schema
  change. **Recommendation: (i)**: 11:40:12 requires the field on the model-schema type when the
  trace is one, and E3 says it is.
- **Comparison:** (i) not compared, a dated line in `03` §4.10 beside `elapsed_us`'s ("derived from
  the algorithm's `feature_map` and `consumed`, both already compared"); (ii) added to `_COMPARED`
  and `TraceStepField`. **Recommendation: (i)**: a change in the dropped set is already a change in
  `consumed` or in the algorithm, which the diff reports; (ii) changes `TraceStepField`'s published
  literal for no new information.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root, at the slice
PR's merge tree, with the range `origin/main...<slice branch>` named. "Red" means seen red **by the
stated cause** at the slice's base, its line verbatim in the slice's `LG-` (with `head=` first and
`rc=` last, seat brief item 37) before the fix; a matching failure with a different cause is a plan
defect, reported to the lead.

**This delta**

1. At the branch head, `python3 scripts/audit-docs.py` (one gate-2 docs check) prints no line naming
   this file except check 31's working-id lines for 8227, and check 28 does not name it;
   `python3 scripts/doc-index.py --check` exits 0. After minting, audit-docs, doc-index `--check`
   and register-lint exit 0.
2. No requirement range: `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no
   line that stands for a set of ids.

**S1a** (FD-1729, part 1)

3. `PL-1769` Acceptance 8's items that are S1a's (Task 0's census and its copy, Task 3.2's red list
   with its class per line, Task 5.1's census diff, Task 1.3's before/after `\du` and grant
   read-backs, the proof run's two exit codes, both 0, the rollback rehearsal's `\du`, the
   non-default `GIP_APP_DB_PASSWORD` line with no value, `OWNER_FIXTURE_USERS` each by full node id
   with its label, and `git grep -nE 'test_owner_database_url\(|owner_database\b' -- backend/tests`
   with its output) are in S1a's `LG-`.
4. `PL-1769` Acceptance 10 holds: `git grep -nE "gipricing:gipricing" -- backend/src` prints
   nothing, and `git grep -n "migration_database_url" -- backend/migrations/env.py` prints a hit.
5. Exactly one new file under `backend/migrations/versions/`, every `GRANT` in it commented with a
   test from the red list and its census row; `alembic heads` prints one head.
6. Under DP-S1 (ii): `PL-1769` Acceptance 11 (the compose run's end state, `pg_stat_activity` showing
   only `gip_app_login` for the application, no `permission denied` in the logs) is in S1a's `LG-`.
7. `dev-commands` documents both variables; the full gate rc table, both halves, is all 0.

**S1b** (FD-1729, part 2)

8. R-b1, R-b1b, R-b2, R-b5, R-b6 and the four trigger-tamper routes (`PL-1769` Task 4.1), and the
   compose-bind red (Step 1.5), red on S1b's base (S1a merged) by cause, in S1b's `LG-`.
9. `PL-1769` Acceptance 9 holds: `uv run pytest backend/tests/test_application_role.py
   backend/tests/test_artifact_immutability.py backend/tests/test_provision_app_role.py -q` green;
   `git grep -n "pg_has_role" -- backend/src` prints exactly one hit, in `app/db/immutability.py`,
   with `'MEMBER'`; the pinned trigger-hash test green; the exact grant map grants no `DELETE` on
   `jobs` or `outbox` unless the `LG-` records a caller.
10. `FR-44` (`01-data-management.md:106`) carries `PL-1769` Step 7.1's dated line, completed with the
    date and both slice ids; the postgres-pro review is in the `LG-`; the full gate rc table is all 0.
11. S1b's squash merge on `main` is dated before 2026-11-04 (`git log -1 --format=%cI <squash sha>`).

**S2** (FD-1610 limb 2)

12. **(d) red.** A new test in `packages/pricing-core/tests/test_rating_runtime.py` scores a bundle
    whose `model_call` `feature_map` carries a key no step produces; at the base its trace step has
    no field for the dropped key (`AttributeError` or `ValidationError` on the name DP-S2 rules).
    After (d): the step's field lists exactly that key; the same quote's premium and the bundle's
    `content_hash` equal the base's (asserted, not read off a log).
13. **(d) no reprice.** `uv run python scripts/generate-contracts.py --check` exits 0 with the field
    in `scoring.py`, in `docs/contracts/schemas/scoring.schema.json` and in the regenerated files;
    `backend/tests/test_contracts.py` green; the golden replay (`pricing_core/rating/golden.py`'s
    committed quotes) scores identically on base and head.
14. **(c) exposure gate.** S2's `LG-` carries, with `head=` first, the exposure query's command, its
    predicate's broken-input proof (a constructed row it counts as 1), and its result line on the dev
    DB `gipricing` inside a window the lead granted in writing. **If the count is > 0, S2's `LG-`
    ends after (d) with the hit list sent to the maintainer, and items 15 and 16 do not apply.**
15. **(c) red.** A bundle built without compile (as a pre-SL-1541 one was) whose `feature_map` key for
    a **required** input (E2's definition) names no produced value scores a price at the base, and
    after (c) fails the quote with the DP-S2 code, the message naming the step and the graph name and
    no quote value (NFR-499). A dropped key that feeds **no** required input still scores, its price
    unchanged, its key in the trace field (the (c)/(d) boundary, its own test).
16. `packages/pricing-core/tests/test_quote_input_raise_sites.py` is in S2's small runs and green
    (seat brief item 11); the new code is in `03` §5's catalogue.
17. `03` FR-222 carries **two dated lines**, one for the trace field (d) and one for the refusal (c),
    and §4.5's example or note names the field; under DP-S2 comparison (i), §4.10 carries its dated
    line. `git log --reverse --format='%h %s' origin/main..<S2 head> -- docs/specs/` shows each
    spec commit before or with its code commit.

**S4** (FD-1754's open limb)

18. **The probe.** A parametrised test over `FactorType.INTERACTION`, `SPLINE`, `POLYNOMIAL` and
    `EXPRESSION`, on both GBM backends (`xgboost`, `lightgbm`), fits a GBM on one Factor of that type
    and compares the `model_call` premium with `predict_gbm(..., factors=<the real Factors>)` on the
    same quote. Its result per type and backend (equal, a loud error, or a silent difference with
    both numbers) is in S4's `LG-`, run on S4's base.
19. **If a type differs silently:** it is added at `factors.py:546`, and the probe's case for it
    becomes the red (at the base: a price that differs, no error) turned green as a refusal with
    `MODEL_CALL_GBM_TRANSFORMED_FACTOR` at compile and at save
    (`test_rating_gbm_banded_refusal.py` and `test_rating_gbm_banded_save.py` each gain the case);
    `03` FR-222's 2026-10-16 "Known gap" gains a dated line naming the type.
    **If none differs silently:** the probe stays as a regression test, no source or spec changes,
    and the `LG-` says the limb is discharged by the probe's node ids. A loud error (not a price) is
    recorded and routed by the lead, not fixed here.

## Global Constraints

- **FR-239: no stored bundle reprices by omission.** (d) changes no price and no `content_hash`
  (Acceptance 12, 13). (c) changes a stored bundle's result from a price to a refusal, so it is built
  only on a zero exposure count (Acceptance 14), as 11:40:12 orders.
- **One contract, one way** (`CLAUDE.md` §2): the trace field is defined once, in `model-schema`;
  `docs/contracts/` changes only through `scripts/generate-contracts.py` (the hand-authored
  `scoring.schema.json` through `contract-schema`); `frontend/src/api/generated/` is regenerated,
  never committed or hand-written.
- **NFR-499:** the refusal's message, and the trace field, name authored identifiers (step id, graph
  name), never a quote value. The trace field lists names only.
- **`pricing-core` stays standalone** (ADR-703): S2 and S4 add no backend import to it.
- **DB windows** (S1a, S1b, S2's exposure query) run only in a **no-gate gap**, granted by the lead in
  writing, load1 and free memory printed at start (seat brief items 12, 15, 32); redis db 11, 12 or
  13 only (item 33); every window ends with the two quoted zeros (item 23). The exposure query is
  **read-only** (`select` only).
- **`deploy/`** is edited by S1a and S1b only, never beside another slice's `deploy/` edit; the
  shared stack comes up only from tools-main (seat brief item 20).
- **Money is untouched**; no float reaches a price.
- **A test that goes red unmutated where this plan predicts green is a defect, not a test to adjust**
  (seat brief item 13): STOP to the lead.
- **The barred word.** Write "the maintainer (by delegation)".

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Lane | DB | Size |
|---|---|---|---|---|---|---|---|
| 1 | **S4** — FD-1754: the four unread GBM Factor types | Tasks S4-0 to S4-3 | `03` §3: FR-222 (the 2026-10-16 amendment), FR-240 (its 2026-10-16 amendment) | PL-1856 slice A (#1368) merged | B (pricing-core modelling) | no | ½ day |
| 2 | **S2** — FD-1610 limb 2: (d) trace the dropped keys, then (c) refuse a dropped required input | Tasks S2-0 to S2-C3 | `03` §3: FR-222, FR-239, FR-240 (read: E2's definition); `03` §4.5, §4.10; NFR-499 | SL-1569 merged, and the lead's read of its `runtime.py` diff (11:40:12); DP-S2 ruled; a granted DB window for S2-C0 | B (rating) | S2-C0 only, read-only | 1 day |
| 3 | **S1a** — FD-1729 part 1: the login role, the two DSNs, the fixtures, the grants | Tasks S1a-0 to S1a-6 (`PL-1769` S-b Tasks 0, 1.1 to 1.4, 2, 3, 5.1, 5.3, and 6 under DP-S1 (ii)) | `01` §3: FR-44 | DP-S1 ruled; `PL-1769`'s SL-1771 activation needs (SL-1770 merged; the `SL-1455` NFR session finished; DP-15's target and the non-default password named at the GO); SL 8185's and SL-1569's DB windows done; re-merged onto SL 8185 | A (backend db, `deploy/`) | **yes**, no-gate gaps | 1 day |
| 4 | **S1b** — FD-1729 part 2: the startup refusal, the tamper proof, the exact grant map | Tasks S1b-0 to S1b-4 (`PL-1769` S-b Tasks 1.5, 4, 5.2, 7; 6 again only if S1b edits `deploy/`) | `01` §3: FR-44 | S1a merged; a gate slot for the full gate; **merged before the 4 Nov code freeze** | A | **yes** | 1 day |

*(Delta, row 1 (S4), dated 2026-10-25 from 23:02 GMT, by the planner (seat plan-8227d), on the
maintainer's entry "2026-10-25 22:43:58 GMT — Maintainer: S2 @84aadaec ACCEPTED (LG 8241, format
split); RULING — S2 and S4 each get an SL working id + roadmap row at mint (L1), PL 8227 rows carry
the LG pointer" in `~/gi-pricing-plan.local/channel/to-lead.md`: **S4's slice is SL 8245 and its
ledger LG 8242** (reserved in `~/gi-pricing-plan.local/handover/eta.md`, 22:41:48 and 22:45:24
UTC). The SL row mints at S4's turn, in S4's own PR, as a one-line row under WK-1178 in
`docs/roadmap.md` §6. This row's scope is unchanged.)*

*(Delta, row 2 (S2), dated 2026-10-25 from 23:02 GMT, by the planner (seat plan-8227d), on the same
22:43:58 GMT entry: **S2's slice is SL 8244 and its ledger LG 8241** (reserved in `eta.md`, 22:39:42
and 22:45:24 UTC). The SL row mints at S2's turn, in S2's own PR, under WK-1178 in
`docs/roadmap.md` §6; the old spike S2 row there stays as it is, a tombstone. This row's scope is
unchanged.)*

*(Delta, row 3 (S1a), dated 2026-10-25 from 23:02 GMT, by the planner (seat plan-8227d), on the same
22:43:58 GMT entry ("S1a/S1b: same treatment when they reach a ledger (S1a has LG 8237 → reserve its
SL now too)"): **S1a's slice is SL 8246 and its ledger LG 8237** (reserved in `eta.md`, 21:08:30
and 22:45:24 UTC). The SL row mints at S1a's turn, in S1a's own PR, under WK-1178 in
`docs/roadmap.md` §6. This row's scope is unchanged.)*

*(Delta, row 4 (S1b), dated 2026-10-25 from 23:02 GMT, by the planner (seat plan-8227d), on the
maintainer's entry "2026-10-25 22:56:19 GMT — Maintainer: S2 gate head 42e237d5 noted; PL 8205 dry
run accepted; S1b O1–O6 RULED; S1a push note" in `~/gi-pricing-plan.local/channel/to-lead.md`, item
(3) O1 (a): a plan defect, in the ruling's words, **"R-b1/R-b5/R-b6 cannot be red by cause after
S1a's flip; red form = owner-DSN run"** — the three cause-reds run with `GIP_TEST_APP_DATABASE_URL`
set to the owner DSN in the throwaway (red) and the default (green). **S1b's ledger is LG 8248**
(reserved in `eta.md`, 22:46:21 UTC); its SL working id is reserved at S1b's GO (O6). The plan
body is untouched.)*

**Order and serialisation against today's queue (E7).**
- **S4** edits `modelling/factors.py` and two test files. Slice A (#1368) does not touch `factors.py`, but it
  edits `model_schema/modelling.py` (where `FactorType` lives) and the GLM fit beside it; S4 runs
  after slice A (#1368) merges, as the proposal and 11:40:12 order, so its probe fits on the families
  slice A (#1368) lands. Disjoint from SL-1569, PL 8205, SL-1552/1553 and SL 8185. May run beside S2 (their
  files are disjoint unless S4's set grows, which touches `03` FR-222's row: a re-merge, line
  conflict only).
- **S2** edits `model_schema/scoring.py`, `rating/score.py`, `rating/runtime.py`, the hand-authored
  `scoring.schema.json`, the generated contracts and `03`. **SL-1569 edits `scoring.py` and
  `score.py` too** (hunks beside `_build_trace`) and regenerates the contracts, so S2 starts from a
  base that includes SL-1569's merge and re-runs `generate-contracts.py` after any later re-merge,
  never hand-merging a generated file. PL 8205's slice edits `model_schema/rating.py` and regenerates
  the contracts: whichever of S2 and it merges second re-runs the generator. Disjoint from
  SL-1552/1553 (frontend, docs) and SL 8185.
- **S1a and S1b** edit `backend/src/app/db/session.py`, `backend/src/app/config.py`,
  `backend/migrations/`, `deploy/`, `scripts/provision-app-role.py`, CI `python.yml`, the test
  conftest and the 37 `test_database_url()` users (`PL-1769` Task 3.1). **SL 8185** edits backend
  auth and dataset routes, not these files, but it and SL-1569 hold DB windows; S1a takes its windows
  after theirs and re-merges onto SL 8185 first (proposal §3). SL-1569's `backend/src/app/platform/traces.py`
  edit is not in S1's write set. No other slice in today's queue edits `deploy/`.
- **Critical path.** S1a then S1b, two DB-window days, against the 4 Nov freeze. If the window queue
  slips, the lead reserves S1a's window now (the proposal's deadline note).

### S4 — FD-1754's unread GBM Factor types

- [ ] **S4-0. Re-read** E5 at the base (slice A (#1368) merged): `gbm_transformed_factors`, its two callers,
  and how `fit_gbm` builds the frame for each of the four types (`modelling/gbm.py`,
  `modelling/factors.py`). Read `to-lead.md` from 11:40:12 for new rulings.
- [ ] **S4-1. The probe (red or regression).** `packages/pricing-core/tests/test_rating_gbm_banded_refusal.py`
  gains the parametrised probe of Acceptance 18: per type and backend, fit, compile a `model_call`
  over the fitted Model, score one quote, and compare with `predict_gbm(..., factors=<real>)`. Mirror
  the file's existing fixtures; do not reinvent them. Run through `run-small.sh` (one file). Record
  each case's verdict in the `LG-` with both numbers.
- [ ] **S4-2. Only for a silent difference:** the spec line first (`03` FR-222, a dated line under the
  2026-10-16 "Known gap": the type joins banded and grouped, same code, same scope); then the type
  added at `factors.py:546` and its docstring; then the save case in
  `backend/tests/test_rating_gbm_banded_save.py` (no DB, E5). Re-run both files and
  `test_quote_input_raise_sites.py` (seat brief item 11, if a raise site changes).
- [ ] **S4-3. Close.** `ruff check .`, the gate, the `LG-` with every red and green line.

**Write set (S4).** `test_rating_gbm_banded_refusal.py`; and only under S4-2: `modelling/factors.py`,
`backend/tests/test_rating_gbm_banded_save.py`, `docs/specs/03-rating-engine.md` FR-222's row. The
`LG-`, the roadmap row.

### S2 — FD-1610 limb 2: (d), then (c)

- [ ] **S2-0. Re-read** E1 to E3 at the base (SL-1569 merged), and confirm by a test that the trace
  entry's `input` equals the handler's `request.input` keys (bar `"$nodes"`), so a dropped set
  computed from `consumed` in `_build_trace` equals the set `runtime.py:758-762` drops. If it does
  not, STOP to the lead: (d) then needs the handler to report the set, which is a design change.
- [ ] **S2-D1. Spec (d).** `03` FR-222, a dated line (on 11:40:12): a `model_call` step's trace
  records each `feature_map` key that was not in the scoring context, by graph name; the price and
  the hash are unchanged. `03` §4.5 names the field; §4.10 per DP-S2. `docs/contracts/schemas/scoring.schema.json`
  gains the field (`contract-schema`).
- [ ] **S2-D2. Red (d)** per Acceptance 12, in `test_rating_runtime.py`; run it, record it.
- [ ] **S2-D3. Code (d).** The field on `TraceStep` (`model_schema/scoring.py`, default `None`);
  `_build_trace` (`score.py:847`) sets it on each `RatingModelCallStep`: the sorted keys of
  `step.feature_map` not in `consumed`, `None` when there are none. Regenerate the contracts
  (`scripts/generate-contracts.py`) and the frontend client. Green: Acceptance 12 and 13
  (`test_rating_runtime.py`, `test_trace_diff.py`, `packages/model-schema/tests/test_scoring_compare.py`
  via `run-small.sh`; `backend/tests/test_contracts.py` in the gate). Commit (d) on its own.
- [ ] **S2-C0. The exposure query (gate for (c)).** A read-only script under the slice's job tmp (not
  committed) reads `select id, status, bundle::text from rating_versions where bundle is not null`
  through `docker exec gi-pricing-postgres-1 psql -U gipricing -At` on the dev DB `gipricing`, and
  for each bundle's inlined algorithm counts the `model_call` steps with a `feature_map` key that no
  earlier step `produces` and the input contract does not supply (the context the ordered chain can
  hold, FD-1425). It prints two counts: any such key (the 11:40:12 gate), and the subset feeding a
  required input (E2). First its broken-input proof: one constructed bundle with a stray key,
  counted 1. Then the real run, in the granted window. The `LG-` line: `head=<40-char sha>`, the
  command, `rows=<n> hits=<n> required_hits=<n>`, `rc=`. **hits > 0 → STOP: S2 closes after (d), the
  hit list goes to the maintainer through the lead.**
- [ ] **S2-C1. Spec (c)** (only on hits = 0). `03` FR-222, a second dated line: at score time, a
  `model_call` key that is absent from the context and maps to a required input (FR-240's
  definition) fails the quote with the DP-S2 code, naming the step and the graph name, never a value;
  a key that maps to no required input is recorded (S2-D1) and scores as before. The code joins
  `03` §5's catalogue beside `MODEL_CALL_FEATURE_COLLISION`.
- [ ] **S2-C2. Red (c)** per Acceptance 15, both cases, in `test_rating_runtime.py`; record them.
- [ ] **S2-C3. Code (c).** At bundle load, per `model_call` step, the set of graph names whose mapped
  feature is a required input (`required_model_inputs` over the pin's Factors and `feature_order`, as
  `check_model_call_coverage` computes it; a peril structure per component). In the handler, a name
  of that set absent from `context` raises the coded error, surfaced through `_model_call_failure`.
  Green: Acceptance 15 and 16 through `run-small.sh` (`test_rating_runtime.py`,
  `test_quote_input_raise_sites.py`, `test_rating_mounted_model_call.py`); `ruff check .`; the gate;
  the `LG-`.

**Write set (S2).** `model_schema/scoring.py`; `pricing_core/rating/score.py`;
`pricing_core/rating/runtime.py` (C3 only); `docs/contracts/schemas/scoring.schema.json`; the
generated contracts; `docs/specs/03-rating-engine.md` (FR-222's row, §4.5, §4.10, §5); the three test
files named above; the `LG-`, the roadmap row.

### S1a — FD-1729 part 1 (`PL-1769` S-b, re-cut)

Each step below is `PL-1769`'s, executed as written there at S1a's base; this delta only places it.

- [ ] **S1a-0.** `PL-1769` Task 0 (the census, Steps 0.1 and 0.2), at the GO tree.
- [ ] **S1a-1.** Task 1, Steps 1.1 to 1.4 (the login-role file, `scripts/provision-app-role.py`, the
  apply to the target the GO names, the rollback stated and rehearsed).
- [ ] **S1a-2.** Task 2 (the two DSNs, the census applied).
- [ ] **S1a-3.** Task 3 (the fixtures' default flips; the red run in a gate slot in a no-gate gap).
- [ ] **S1a-4.** Task 5, Steps 5.1 and 5.3 (the census diff, the one migration from the red list;
  the suite again, no `permission denied`).
- [ ] **S1a-5.** Under DP-S1 (ii): Task 6 (the compose run on a separate project and a fresh volume).
- [ ] **S1a-6.** `dev-commands` documents both variables; if the census finds a spec that names the
  DSN (E6: none at `ff976406`), its dated line; the full gate; the `LG-`.

**Write set (S1a).** `PL-1769`'s S-b write set, less `backend/tests/test_application_role.py`,
`Database.assert_least_privilege()` and Step 1.5's compose bind.

### S1b — FD-1729 part 2 (`PL-1769` S-b, re-cut)

- [ ] **S1b-0.** Re-read at S1b's base (S1a merged); Task 0's census is S1a's `LG-`, not re-run.
- [ ] **S1b-1.** Task 4 (`test_application_role.py` reds first, then
  `Database.assert_least_privilege()`).
- [ ] **S1b-2.** Task 5, Step 5.2 (the exact grant map test).
- [ ] **S1b-3.** Task 1, Step 1.5 (compose binds to `127.0.0.1`, its red; applied to the shared stack
  only as the GO-time act the maintainer names); then Task 6 again because this edits `deploy/`.
- [ ] **S1b-4.** Task 7 (`FR-44`'s dated line naming both slices, the postgres-pro review, the full
  gate); the `LG-`.

## Hand-off (not this plan's writes)

- **Ids at GO.** The lead reserves an `SL-` and an `LG-` working id per slice at its GO (S4, S2, S1a,
  S1b). **`SL-1771`'s re-cut** is the lead's call at S1a's GO: the planner recommends `SL-1771` keeps
  S1a's scope (its id is already cited by FD-1729's register row and `PL-1769`) and S1b takes a new
  `SL-`; the planner then edits `SL-1771`'s roadmap block (a `draft` row, never dispatched) and cuts
  S1b's, in S1a's PR (`document-ids.md` §1.6 SL row).
- **The Work's roadmap row** lists this delta (L5); that line is the lead's, not the planner's
  (`planner.md` Tools: the planner writes only the `SL-` rows it cuts).
- **The GO requests** come after the gate chain, as 11:40:12 orders. S4's has no open need but
  slice A (#1368); S2's needs DP-S2, SL-1569's merge and the lead's `runtime.py` read; S1a's needs DP-S1 and
  `PL-1769`'s activation needs.
- **Not this plan:** S3 (`PL-1856` slice B, already planned); R-close (the auditor's, 11:40:12 item 4);
  FD-1495's carry; FD-1836 and FD-1411 (RL 8218).

## Self-review

- Every 11:40:12 condition on S2 has a place: (d) first and additive (S2-D1 to D3,
  Acceptance 12 and 13); price and hash unchanged (Acceptance 12, 13); (c) only on a zero
  query on the real DB in a granted window with `head=` (S2-C0, Acceptance 14); > 0 stops after (d)
  (S2-C0); red first for both (S2-D2, S2-C2); two dated FR-222 lines (S2-D1, S2-C1); the field in
  model-schema with regenerated contracts (S2-D3); after SL-1569 and the lead's read (the table).
- S1's split moves no ruled remedy: every `PL-1769` S-b task lands in exactly one of S1a and S1b
  (Tasks 0, 1.1-1.4, 2, 3, 5.1, 5.3 in S1a; 1.5, 4, 5.2, 7 in S1b; 6 per DP-S1) — listed by task,
  each named.
- S4 builds nothing unless the probe shows a silent misprice (Acceptance 19), as the proposal and the
  register's "unread" limb ask.
- Two departures from the proposal, each named: the compose run's slice (DP-S1) and the settings
  row that does not exist (E6).
- The open names are DP-S2, never a silent pick; the code and field names in the tasks are the
  recommendations and change with the ruling.
