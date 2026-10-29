---
id: PL-1927
family: plan
kind: map
title: WK-1178 — the open-HIGH slices. FD-1729 split into S1a and S1b (SL-1771 re-cut), FD-1610 limb 2 as S2 (trace the dropped feature_map keys, then refuse a dropped required input), FD-1754's unread GBM Factor types as S4 — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — L1: draft→active rides each slice's PR
created: 2026-10-25             # drafted 2026-10-25 under working id 8227
owner: planner
tree: ff976406f1bf133cfe040d2c44d383011503988a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1769, SL-1771, FD-1729, FD-1610, SL-1541, FD-1754, SL-1758, PL-1856, SL-1569, FR-44, FR-222, FR-239, FR-240]
---

# PL-1927 — WK-1178: the open-HIGH slices S1a, S1b, S2 and S4 (a dated Work-plan delta)

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

**S1c** (FD-1951; row 5's dated line, 2026-10-26)

20. **Reds by cause, in S1c's `LG-`** (`head=` first, `rc=` last), each on S1c's base (`eaddb4d9` or
    later main) in a throwaway `postgres:16-alpine` with the role planted, before the fix: (a1)
    `ALTER ROLE gip_app CREATEROLE` and (a2) `ALTER ROLE gip_app_login CREATEROLE` — startup does not
    refuse; (b1) a pre-planted `gip_app` with `CREATEROLE` keeps it after the base
    `app-login-role.sql`; (b2) a pre-planted membership `WITH INHERIT FALSE, SET TRUE` keeps its
    options after the base SQL; and one red per medium DP-S1c-1 takes in. Each turns green at the
    head: startup refuses (a1) and (a2) naming the route, and `app-login-role.sql` resets (b1) and (b2).
21. **Two controls, not reds:** `GRANT gipricing TO gip_app_login WITH ADMIN OPTION` and the
    admin-only `GRANT gipricing TO gip_app_login WITH ADMIN TRUE, INHERIT FALSE, SET FALSE` are both
    refused at the base already, through `pg_has_role(…, 'MEMBER')`: on PostgreSQL 16 any
    `pg_auth_members` row counts as MEMBER, the admin-only form included (measured 2026-10-26 by
    the lead's and the maintainer's probes, see the dated line under S1c-4). The `LG-` records
    both refused at base and head.
22. `git grep -n "rolcreaterole" -- backend/src/app/db/immutability.py` prints a hit,
    inside `P_OWN` or a constant defined beside it and imported by the tests;
    `git grep -n "WITH INHERIT TRUE, SET FALSE\|NOCREATEROLE" -- deploy/postgres/app-login-role.sql`
    prints the membership line and an `ALTER ROLE gip_app` line.
23. `FR-44` (`01-data-management.md:106`) carries a dated line naming SL 8266 (its minted id after
    the mint) and the two routes; `uv run python scripts/req-coverage.py` exits 0.
24. The full gate, both halves, rc table all 0 (or under seat brief item 31's 1(f) form only), at
    the slice head; **the gate-cover rule for a role-changing slice:** after the last re-merge of
    main, the full backend suite runs on the login role at the re-merged head before the PR, its
    summary line and rc in the `LG-` (a patch-id cover is not enough; S1a's #1398 precedent).
25. DP-S1c-1 carries a dated ruling, and every medium has its place: a step with its red here
    (item 20), or a "carried by FD-1951 to <owner>" line in FD-1951's close.
26. S1c's squash merge on `main` is dated on or before 2026-10-31 (`git log -1 --format=%cI <squash
    sha>`).

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

*(Delta, row 3 (S1a), second line, dated 2026-10-25 from 23:06 GMT, by the planner (seat
plan-8227d), on the maintainer's entry "2026-10-25 23:04:28 GMT — Maintainer: S1a pre-gate proof
RED — RULED option (a) at the HELPER level; SL-1553 throwaway GRANT for `test_regression_runs.py`"
in `~/gi-pricing-plan.local/channel/to-lead.md`, item (A), beside the 22:43:58 GMT entry above:
**the fixtures task in this row was under-scoped.** The pre-gate proof at df215d55 was "665
failed, 2179 passed, 51 errors" rc 1. The ruling fixes it at the helper: `ensure_workspace`,
`seed_builtin_roles` and the five small seed helpers go through the one owner seam in conftest_db,
with their call sites unchanged (the rest of item (A) is the ruling's). The S1a ledger LG 8237 carries
the dated line "pre-gate proof at df215d55: 665 F / 51 E, all seed-path or owner-only classes;
fixed at the helper". The row and the line above are unchanged.)*

*(Delta, row 4 (S1b), dated 2026-10-25 from 23:02 GMT, by the planner (seat plan-8227d), on the
maintainer's entry "2026-10-25 22:56:19 GMT — Maintainer: S2 gate head 42e237d5 noted; PL 8205 dry
run accepted; S1b O1–O6 RULED; S1a push note" in `~/gi-pricing-plan.local/channel/to-lead.md`, item
(3) O1 (a): a plan defect, in the ruling's words, **"R-b1/R-b5/R-b6 cannot be red by cause after
S1a's flip; red form = owner-DSN run"** — the three cause-reds run with `GIP_TEST_APP_DATABASE_URL`
set to the owner DSN in the throwaway (red) and the default (green). **S1b's ledger is LG 8248**
(reserved in `eta.md`, 22:46:21 UTC); its SL working id is reserved at S1b's GO (O6). The plan
body is untouched.)*

*(Delta, row 5 (S1c), dated 2026-10-26 from 13:08 GMT, by the planner (seat plan-fd1951), on the
maintainer's entry "2026-10-26 11:38:32 GMT — Maintainer: postgres-pro review STOP — RULED (b): S1b
proceeds on its ruled refusal set; the two HIGH concerns (CREATEROLE, ADMIN OPTION) and the five
same-class mediums become ONE new FD, HIGH, owner WK-1178, fix-before-close, a red-first follow-up
slice under PL-1927 before the P2 code freeze; the whole review goes into LG 8248 as a dated section"
in `~/gi-pricing-plan.local/channel/to-lead.md`, condition (i) ("a follow-up slice under PL-1927 (a
dated PL delta row, **SL reserved at that row**) that widens `P_OWN` to read `rolcreaterole` and
`admin_option`, converges `gip_app` (`NOCREATEROLE`, and `WITH INHERIT TRUE, SET FALSE` on the
membership), amends FR-44 by a dated line, and proves each refusal red-first on a planted role —
**deadline Fri 31 Oct**"), owed after that day's PRs by the entries "2026-10-26 12:41:12 GMT" and
"2026-10-26 13:03:18 GMT": **a new row 5, S1c — FD-1951: the CREATEROLE and ADMIN OPTION routes
(red-first).** Its slice is **SL 8266** (reserved in `~/gi-pricing-plan.local/handover/eta.md`,
13:05:37 UTC); its ledger: **LG reserved at S1c's GO**. Work **WK-1178**; **deadline Fri 31 Oct
2026** *[Correction 2026-10-29: the weekday is Saturday (2026-10-31); the date governs.]* (inside the P2 code-complete ETA, before the Wed 4 Nov freeze). The row, in the table's
columns: Order 5; Scope (what the `LG-` quotes) Tasks S1c-0 to S1c-6 below; Requirements `01` §3:
FR-44; Depends on S1b merged (#1399, `eaddb4d9`), DP-S1c-1 ruled, a granted throwaway DB window in a
no-gate gap, a gate slot for the full gate; Lane A (backend db, `deploy/`); DB **yes** (throwaway
`postgres:16-alpine` only for the planted roles); Size 1 day, 1½ if DP-S1c-1 takes every medium in.
The SL row mints at S1c's turn, in S1c's own PR, under WK-1178 in `docs/roadmap.md` §6. Rows 1 to 4,
their dated lines and the plan body are unchanged.)*

*Closed 2026-10-29: merged as #1405 (squash 7ceff4a1, merge 36); SL-1962 / LG-1964; FD-1951 closed; residuals FD-1963 (WK-1178, by Thu 12 Nov 2026) and FD-1965 (the seed-fixture slice).*

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

### S1c — FD-1951: the CREATEROLE and ADMIN OPTION routes (red-first)

*(Added by row 5's dated line, 2026-10-26.)* Every red is seen red **by its cause** on a **planted**
role in a throwaway `postgres:16-alpine` (`127.0.0.1` only, `rm -fv` after, the window's two zeros,
seat brief item 23), its line in S1c's `LG-` before the fix; the planted statement runs as the
throwaway's superuser. The owner role is `gipricing`.

- [ ] **S1c-0.** Re-read at S1c's base (S1b merged, `eaddb4d9` or later main): `P_OWN`
  (`backend/src/app/db/immutability.py:42-57`), `deploy/postgres/app-login-role.sql:1-19`, FR-44
  (`01-data-management.md:106`, with its 2026-10-26 amendment) and FD-1951 whole. Record in the
  `LG-` the base's `pg_roles` / `pg_auth_members` read-back of the provisioned throwaway (FD-1951's
  two queries), which shows neither route.
- [ ] **S1c-1. (a) `P_OWN` sees CREATEROLE.** Reds first, each planted after a clean
  provision and `alembic upgrade head`, each a startup that **does not refuse** at the base:
  (a1) `ALTER ROLE gip_app CREATEROLE`; (a2) `ALTER ROLE gip_app_login CREATEROLE`. The two ADMIN
  forms (the plain `… WITH ADMIN OPTION`, and `… WITH ADMIN TRUE, INHERIT FALSE, SET FALSE`) are
  **controls**, not reds: on PostgreSQL 16 both count as `pg_has_role(…, 'MEMBER')`, so the base
  already refuses them; record both refused at base and head (acceptance 21). Then widen `P_OWN`:
  a reachable role (`pg_has_role(current_user, r.oid, 'MEMBER')`) with `r.rolcreaterole`. The
  refusal message names the route (`createrole`),
  never a credential. Tests in `backend/tests/test_application_role.py`, `req` marker FR-44, each
  reading the constant `P_OWN`, never a copy. Green: (a1) and (a2) refused, the provisioned state
  passes.
- [ ] **S1c-2. (b) `app-login-role.sql` converges `gip_app` and the membership.** Reds first:
  (b1) pre-plant `CREATE ROLE gip_app NOLOGIN CREATEROLE` (and `CREATEDB`, `REPLICATION`) before
  the SQL runs: the base SQL leaves them; (b2) pre-plant `GRANT gip_app TO gip_app_login WITH
  INHERIT FALSE, SET TRUE`: the base SQL's plain `GRANT` leaves those options. Then add, after the
  create block: `ALTER ROLE gip_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
  NOBYPASSRLS;` and replace the membership with `GRANT gip_app TO gip_app_login WITH INHERIT TRUE,
  SET FALSE;` (the login role never needs `SET ROLE gip_app`; with SET false it cannot assume an
  attribute of `gip_app` that membership does not pass on). Read back `rolcreaterole`, `rolcreatedb`,
  `rolreplication` for both roles and `inherit_option`, `set_option`, `admin_option` from
  `pg_auth_members`, before and after, in the `LG-`. Test in
  `backend/tests/test_provision_app_role.py`, `req` FR-44. The SQL stays idempotent: a second run
  is a no-op, shown by the same read-back.
- [ ] **S1c-3. (c) FR-44's dated line.** Append to FR-44 (`01-data-management.md:106`) a line
  *(Amended <date>, WK-1178 SL 8266, on FD-1951.)* naming the two routes: startup also refuses a
  reachable role with CREATEROLE and an ADMIN OPTION on an owner-reachable role; the provisioner
  converges `gip_app` and states the membership `WITH INHERIT TRUE, SET FALSE` — plus one clause per
  medium DP-S1c-1 takes in. The spec commit lands before or with the code commit
  (`spec-change`); `req-coverage.py` rc 0.
- [ ] **S1c-4. (d) The five same-class mediums — DP-S1c-1 (open).** The decision is the
  maintainer's; each is either a step here, with its red on a planted role, or "carried by FD-1951
  to <owner>". The planner's recommendation, one line why each:
  1. **Predefined roles** (`pg_write_all_data`, `pg_execute_server_program`,
     `pg_write_server_files`, `pg_read_server_files`) — **in S1c**: one more disjunct in the same
     predicate and the same test file; red `GRANT pg_write_all_data TO gip_app_login`, not refused
     at base. It bypasses the grant map outright, the FD-1729 class exactly.
  2. **`pg_parameter_acl` / `session_replication_role`** — **in S1c**: a startup refusal when
     `has_parameter_privilege(current_user, 'session_replication_role', 'SET')` is true for the
     connection role; red `GRANT SET ON PARAMETER session_replication_role TO gip_app_login`. It
     switches the origin-only triggers off without ownership, the route FR-44's trigger layer
     depends on not existing.
  3. **Trigger-function and schema ownership** — **in S1c**: `P_OWN`'s ownership disjunct also
     reads `pg_proc.proowner` for the pinned guard functions and `pg_namespace.nspowner` for
     `public`; reds `ALTER FUNCTION <one pinned guard>() OWNER TO gip_app` and `ALTER SCHEMA public
     OWNER TO gip_app`. Same query, same test; the md5 pin only catches a replaced body at the next
     start.
  4. **Membership and role-setting reset** — **split**: the settings reset (`ALTER ROLE gip_app_login
     RESET ALL`, `VALID UNTIL 'infinity'`, `CONNECTION LIMIT -1`, the same for `gip_app`) **in S1c**,
     one line each in the file S1c-2 already edits, red a planted `ALTER ROLE gip_app_login SET
     search_path = shadow, public`; the strip of other memberships **carried by FD-1951 to WK-1178**, because
     revoking memberships the deployer granted can break an operator's setup and the startup refusal
     already catches every owner-reachable one.
  5. **The PUBLIC revoke** — **in S1c**, test only: the exact grant-map test also asserts that
     `PUBLIC` holds no privilege on any `public` table (read from `pg_class.relacl` via
     `aclexplode`, grantee 0), red `GRANT UPDATE ON jobs TO PUBLIC` in a rolled-back transaction;
     no migration, because nothing grants PUBLIC anything today (fails closed).
  If the ruling carries any item, FD-1951's close line names it with its owner and a new `FD-`
  holds it; FD-1951 does not close with a limb in no record.
  *(Ruled 2026-10-26, on the maintainer's entry "2026-10-26 13:12:34 GMT — DP-S1c-1 RULED" in
  `~/gi-pricing-plan.local/channel/to-lead.md`: the recommendation above is adopted on all five. Items 1, 2, 3
  and 5 are IN, each with its red. Item 4 is SPLIT, with two binding lines: the `RESET ALL` line carries a
  comment that it discards an operator's role settings, and S1c's `LG-` quotes `pg_db_role_setting` for both
  roles before and after, on the throwaway. The membership strip is CARRIED by FD-1951 to WK-1178. Its `FD-`
  (MEDIUM, owner WK-1178) is minted in S1c's own PR, so FD-1951 closes in that PR with the limb in a record.
  Acceptance 21 is accepted: the plain `WITH ADMIN OPTION` grant is the control, refused at the base and at the
  head, and the red by cause is `WITH ADMIN TRUE, INHERIT FALSE, SET FALSE`. Added by the lead; the text above is
  unchanged.)*
  *(Corrected 2026-10-26, on the maintainer's entry "2026-10-26 13:50:37 GMT" (Q2): the admin-only
  form is NOT red. Measured on PostgreSQL 16.15, a throwaway `postgres:16-alpine` (the lead's probe,
  reproduced by the maintainer): `GRANT owner_grp TO gip_app_login WITH ADMIN TRUE, INHERIT FALSE,
  SET FALSE` gives `pg_auth_members` admin t / inherit f / set f and `pg_has_role('gip_app_login',
  'owner_grp', 'MEMBER')` = t (USAGE f, SET f). The plain `WITH ADMIN OPTION` grant also gives
  MEMBER = t. So the base `P_OWN` already refuses both. In this unmerged delta, acceptance 20 drops
  (a3) as a red, acceptance 21 names both forms as controls, acceptance 22 drops `admin_option`, and
  S1c-1 widens `P_OWN` by CREATEROLE only. FD-1951's HIGH-2 is refuted by the same probe (its
  dated correction); its residual is CREATEROLE plus the five mediums. Edited in place by the lead,
  disclosed here.)*
- [ ] **S1c-5.** `PL-1769` Task 6 again (the compose run on a separate project and a fresh volume),
  because S1c edits `deploy/`, as S1b-3 did.
- [ ] **S1c-6.** The full gate, both halves; after the last re-merge of main, the full backend
  suite on the login role at the re-merged head before the PR (a role-changing slice: a patch-id
  cover is not enough); `req-coverage.py`; the `LG-` with every red and green line.

**Write set (S1c).** `backend/src/app/db/immutability.py` (and `session.py` only if the refusal's
message is built there), `deploy/postgres/app-login-role.sql`, `backend/tests/test_application_role.py`,
`backend/tests/test_provision_app_role.py`, `docs/specs/01-data-management.md` (FR-44's line),
S1c's `LG-` and SL row, FD-1951's close in place and its register row. No migration unless
DP-S1c-1 rules otherwise.

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

## Delta, row 6 (S1d) — FD-1965: the seed fixture migrates its own scratch database (test-only, red-first)

*(Delta, row 6 (S1d), dated 2026-10-29 from 17:24 GMT, by the planner (seat plan-seedfix, Opus 5.5,
effort medium), on the maintainer's entries "2026-10-29 14:21:02 GMT" item 2 ((2'): *"Fix
**red-first in its own small test-only slice tomorrow, Fri 30 am** (not riding the beat slice — one
thing per slice): the fixture also sets `GIP_MIGRATION_DATABASE_URL` to the scratch database as the
owner role; red = the three tests with data present and the env pointing elsewhere; green = the three
passing; plus a control that the fixture refuses when no migration URL can be formed. Its SL/LG
reserved after S1c's ids."*), "2026-10-29 14:22:02 GMT" (the ids), "2026-10-29 14:42:55 GMT" (the
one-file `ruff format` fix rides this slice "as a named, separate commit"), "2026-10-29 17:11:12 GMT"
item (1) (*"the data goes in a throwaway checkout, never a slice worktree"*) and "2026-10-29 17:14:18
GMT" (*"the seed-fixture slice = a dated delta row in PL-1927 (FD-1965 is S1c's follow-on; relates:
PL-1927, WK-1178), no new PL"*), all in `~/gi-pricing-plan.local/channel/to-lead.md`: **a new row 6,
S1d — FD-1965: the seed fixture migrates its own scratch database.** Its slice is **SL 8278** and its
ledger **LG 8279** (working ids; minted in merge order at the slice's turn). Work **WK-1178**; relates
PL-1927, WK-1178; the finding `FD-1965` (minted by #1405, squash `7ceff4a1`) is its specification —
its Finding, Evidence and Remedy sections. **Tree read:** `origin/main`
`7ceff4a16829c63f20f0cdbb56fafae22657c1ab`; `examples/` and `backend/migrations/` are unchanged from
`447bcfd6`. The row, in the table's columns: Order 6; Scope (what the `LG-` quotes) Tasks S1d-0 to
S1d-7 below; Requirements: none amended (the tests carry their existing markers, FR-31 and FR-32;
no spec change); Depends on #1405 merged (met, `7ceff4a1`), DP-S1d-1 and DP-S1d-2 ruled, the template
rebuild (to-lead "2026-10-29 17:24:25 GMT") reported, a granted DB window in a no-gate gap (seat brief items 12, 32); Lane examples (test-only); DB **yes**, the shared
server, S1d-5 only; Size ½ day. The SL row mints at S1d's turn, in S1d's own PR, under WK-1178 in
`docs/roadmap.md` §6. Rows 1 to 5, their dated lines and the plan body are unchanged.)*

**Evidence at `7ceff4a1`.**
- **E-d1.** `backend/migrations/env.py:31–38`: `_migration_url = load_settings().migration_database_url`;
  `None` → `RuntimeError("GIP_MIGRATION_DATABASE_URL is not set: …")`. No fallback (FD-1729).
- **E-d2.** `examples/fremtpl2/test_seed.py:120–165` (`scratch_seed`): the scratch name
  `scratch_sl1409c_<hex8>`; the admin URL is a literal,
  `postgresql+asyncpg://gipricing:gipricing@localhost:5432/postgres` (:139); only `GIP_DATABASE_URL` is
  set (:151); `uv run alembic upgrade head` runs with `env=dict(os.environ)` (:152–158); the skip is
  :135–136 (no `data/freMTPL2freq.arff`).
- **E-d3, wider than migration.** `examples/fremtpl2/seed.py:448–466`: the seed itself reads
  `settings.migration_database_url` and runs `grant_demo_principals` (workspace, built-in roles, users,
  role assignments, in one committed unit of work) on **that** database. So with the variable pointing
  elsewhere, the seed **writes the demo principals into the foreign database**. The fix covers it,
  because the seed runs in-process after the fixture's `monkeypatch.setenv`. **Confirmed** by the
  maintainer's read-only read at to-lead "2026-10-29 17:24:25 GMT" (and the lead's own read, from-lead
  "2026-10-29 17:23:56 GMT"): the template `gipricing` held `workspaces` 3 (created_at
  14:28:30.294 / 14:28:37.721 / 14:28:45.353 UTC, the three seed tests of the 14:28 proof at
  `18728e68`), `users` 7, `role_assignments` 30, `workspace_members` 21, `roles` 18, beside the migrations-only
  `alembic_version` 1, `environments` 3 (seeded by migration `c4a81f6d2e95`:108–115, to-lead
  "2026-10-29 17:27:58 GMT") and `tenant_marker` 1. The 17:24:25 entry grants the template rebuild and
  rules that the template is never named by a URL a seat sets (its rule 1).
- **E-d4.** The three tests: `test_the_seed_reruns_against_a_seeded_database` (:168),
  `test_every_seeded_ingestion_run_balances_its_rows` (:191; FR-32, FR-31),
  `test_a_small_seed_is_refused_for_its_degenerate_fit` (:235).
- **E-d5, CI.** `.github/workflows/python.yml:21,59` filter on `examples/**` and `backend/**`;
  `pyproject.toml` `testpaths` includes `examples/fremtpl2`; CI has no `.arff`, so it skips the three
  and runs the rest of the file. `frontend.yml`'s paths match neither changed file.
- **E-d6.** `backend/tests/test_transformations.py`: `git show origin/main:backend/tests/test_transformations.py
  | uv run ruff format --check --stdin-filename backend/tests/test_transformations.py -` reads rc 1 at
  `7ceff4a1` (#1405 edited the file and did not carry the format fix; process-backlog row
  "2026-10-29 14:44 GMT").

**Decision points (S1d).** S1d stays unstarted while either is open.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S1d-1 | What is "no migration URL can be formed" when the admin URL is a literal (E-d2), so the case is unreachable today? | (a) a module-level helper `_scratch_owner_url(admin, name)` on `sqlalchemy.engine.make_url(admin).set(database=name)`, refusing by name when the admin URL has no user, password or host, called before `CREATE DATABASE`; the control calls it with such a URL · (b) the admin URL from a new env var, the literal as default; the control unsets it · (c) no control; the case recorded as unreachable | **(a)**: the only reachable failure is a malformed admin URL, and (a) tests exactly that, DB-free and data-free, in CI; (b) adds configuration for a fixed value; (c) drops a ruled control | decision point | yes (S1d-3) | |
| DP-S1d-2 | Which gate? (seat brief item 30: outside `docs/` → the full code gate by default) | (G1) the full code gate, both halves · (G2) the narrow cover below | **(G2)**; (G1) if G2 is not granted | decision point | yes (S1d-6) | |

**DP-S1d-2 (G2), the narrow cover, proposed.** Two test files change. Nothing imports a test file, so
`test_seed.py`'s import closure is itself (seat brief item 29), and a format-only commit leaves the
AST unchanged (DP-T27-6's criterion, applied unstripped). (i) `uv run ruff check .` rc 0 and
`uv run ruff format --check` on the two files rc 0; (ii) `ast.dump` of
`backend/tests/test_transformations.py` byte-equal before/after the format commit (script and both
digests in the `LG-`); (iii) `examples/fremtpl2/test_seed.py` whole through `run-small.sh` with **no**
data (the CI form: the three skip, the control runs); (iv) the DB window, S1d-5; (v) item 30's docs
half (the gate-2 checks and the eight docs-audit pytest files via `run-small.sh`; at an unminted head
their failures are the 13-id 1(f) set, md5 `3de106a91734`, and after the mint 0); (vi) PR CI: python,
docs, history-policy (frontend does not fire, E-d5). G2 lapses to G1 if the slice's own diff
(`origin/main...<slice branch>`) touches `conftest*.py`, `env.py` or `seed.py`.

**Write set (S1d).** `examples/fremtpl2/test_seed.py`; `backend/tests/test_transformations.py`
(format only, its own commit); `LG 8279`; the SL row; FD-1965's close in place and its register row.
No production, spec or migration file.

- [ ] **S1d-0. Base.** Branch from `origin/main` at or after `7ceff4a1`. Re-read E-d1 to E-d4 at the
  base; quote `git diff --name-only 7ceff4a1..<base> -- examples/ backend/migrations/` (non-empty →
  re-read and report before S1d-1). Run E-d6's format check at the base: rc 1 → S1d-6's format commit
  is owed; rc 0 → it is dropped and the `LG-` says why.
- [ ] **S1d-1. The throwaway checkout.** A `git worktree add` of the base under the executor's own
  scratch dir, never the slice worktree; `uv sync --all-packages --frozen` there; the two `.arff` in
  **its** `examples/fremtpl2/data/` (fetch or copy). At END, `git -C <slice wt> status --ignored --
  examples/fremtpl2/data` quoted: no `.arff`.
- [ ] **S1d-2. Reds R1–R3 (inside the S1d-5 window).** In the throwaway at the base, data present,
  `GIP_MIGRATION_DATABASE_URL` on the **foreign** database `scratch_pl8278_foreign` (at head; never the
  template, E-d3): the three tests (E-d4) by node id, each failing by cause `UndefinedTableError:
  relation "role_assignments" does not exist`, the three FAILED lines verbatim in the `LG-`. The
  foreign database's `select count(*) from workspaces where name = 'freMTPL2 demo'` before and after:
  after > before is the E-d3 red, quoted. **O1 (observation):** the same three with the variable unset
  fail at the fixture with `CalledProcessError`, env.py's `RuntimeError` in the captured stderr; one
  line quoted.
- [ ] **S1d-3. The fix (on DP-S1d-1; (a) shown).** In `test_seed.py`: `_scratch_owner_url(admin: str,
  name: str) -> str` on `make_url`, raising `RuntimeError("scratch_seed cannot form the owner URL for
  <name> …; it refuses rather than migrate an inherited GIP_MIGRATION_DATABASE_URL")` when the admin
  URL has no user, password or host. The fixture calls it **before** `CREATE DATABASE` and sets
  **both** `GIP_DATABASE_URL` and `GIP_MIGRATION_DATABASE_URL` to the result (owner role `gipricing`,
  as today's URL). Commit: `test(examples): the seed fixture migrates and seeds its own scratch
  database (FD-1965)`.
- [ ] **S1d-4. Control C1.** `test_the_scratch_fixture_refuses_when_no_owner_url_can_be_formed`, a
  `req` marker the file already carries for the seed path (the executor confirms it at the base): with
  `GIP_MIGRATION_DATABASE_URL` deleted (`monkeypatch.delenv(..., raising=False)`), the helper given
  `postgresql+asyncpg:///postgres` raises `RuntimeError` matching `cannot form the owner URL`. **Red on
  broken input:** the guard deleted (one edit, assert count 1) → C1 fails `DID NOT RAISE`; restored →
  passes; both lines in the `LG-`.
- [ ] **S1d-5. The DB window (the lead's written grant; load1 and `free -g` at start, item 15).** On
  the shared server (the fixture's admin URL is that server's, E-d2; the condition of "2026-10-29
  14:22:02 GMT" applies): `select datname from pg_database order by 1` before; create
  `scratch_pl8278_foreign` from the rebuilt template (`createdb -T gipricing scratch_pl8278_foreign`,
  17:24:25 rule 1; the template's non-empty-table list quoted first and refused unless it is
  exactly `alembic_version=1 environments=3 tenant_marker=1`, the list as amended at to-lead
  "2026-10-29 17:27:58 GMT"); S1d-2's
  reds at the base; then in the throwaway at the head the **greens**: G1, the three pass with the same
  foreign URL set and the foreign demo-row count before = after; G2, the three pass with the variable
  unset. Drop `scratch_pl8278_foreign`; `select datname` after = before (no `scratch_sl1409c_*` or
  `scratch_pl8278_*` left); the shared `gipricing` database never written; redis db 11, 12 or 13
  (item 33), `dbsize` 0 after FLUSHDB; the window's two zeros (item 23).
  (Amended 2026-10-29 by the lead, on to-lead "2026-10-29 17:32:19 GMT": the window's databases are
  named `scratch_s1d_*` — the foreign database is `scratch_s1d_foreign`, not `scratch_pl8278_foreign` —
  dropped at END; the window is ≤ 60 min, in a no-gate gap with all three slots free at start, and the
  template's non-empty-table list is quoted before and after.)
- [ ] **S1d-6. The format commit, then the gate.** If S1d-0 read rc 1: `uv run ruff format
  backend/tests/test_transformations.py` alone in its own commit, `style(backend): ruff format
  backend/tests/test_transformations.py (process-backlog 2026-10-29 14:44 GMT)`; `ast.dump` equal
  before/after. Then the gate DP-S1d-2 rules.
- [ ] **S1d-7. Records.** `LG 8279` (`docs/_templates/LG.md`; scope = this row; every red/green line
  with `head=` first and `rc=` last, item 37); the SL row; FD-1965 closed in place and its register
  row; the mint of SL 8278 / LG 8279 at S1d's turn (items 17, 19, 26).

**Acceptance (S1d)** — the plan's Acceptance Standard rules apply (the merge tree, the range
`origin/main...<slice branch>` named, red by the stated cause at the base, its line in `LG 8279`
before the fix):

- **d1.** `git diff --name-only origin/main...<slice branch>` lists only
  `examples/fremtpl2/test_seed.py`, `backend/tests/test_transformations.py` (only if S1d-0 read rc 1)
  and files under `docs/`.
- **d2.** `git log --format=%s origin/main..<slice branch> -- backend/tests/test_transformations.py`
  prints exactly one subject, beginning `style(backend): ruff format`, and its `git show --stat`
  lists that one file.
- **d3.** `LG 8279` carries R1–R3 red by cause `UndefinedTableError: relation "role_assignments" does
  not exist` at the base (data present, the migration URL on `scratch_pl8278_foreign`), each with its
  node id, and the foreign demo-row count rising.
- **d4.** `LG 8279` carries G1 (the three passed, same foreign URL, foreign demo-row count before =
  after) and G2 (the three passed, variable unset) at the head, in the throwaway checkout.
- **d5.** `uv run pytest -q examples/fremtpl2/test_seed.py -k owner_url` passes with no data present
  (C1); `LG 8279` carries C1's mutation red (`DID NOT RAISE`) and its restore green.
- **d6.** `grep -n 'GIP_MIGRATION_DATABASE_URL' examples/fremtpl2/test_seed.py` shows the fixture
  setting it, and the helper call precedes `CREATE DATABASE` in `scratch_seed` (read the lines).
- **d7.** `uv run ruff check .` rc 0; `uv run ruff format --check examples/fremtpl2/test_seed.py
  backend/tests/test_transformations.py` rc 0.
- **d8.** The window's read-backs in `LG 8279`: `pg_database` names before = after, no
  `scratch_pl8278_*` or `scratch_sl1409c_*` left; redis `dbsize` 0 on the seat's db; no `.arff` under
  the slice worktree.
- **d9.** The gate DP-S1d-2 rules: its END row and rc files in `LG 8279`; after the mint, audit-docs,
  doc-index `--check` and register-lint exit 0; PR CI python, docs and history-policy green.
- **d10.** FD-1965 reads closed in place and in `docs/findings/register.md`, naming the slice's minted
  `SL-` id.

**Constraints (S1d).** Two DSNs (FD-1729; `dev-commands` "Two DSNs"): migrations run as the owner,
`gipricing`. The template `gipricing` is migrations-only (`dev-commands`): no red, green or proof in
S1d points `GIP_MIGRATION_DATABASE_URL` at it. No data in a slice worktree (17:11:12 item (1)). No
production or spec change: `examples/fremtpl2/seed.py`, `backend/src/**`, `env.py` and `docs/specs/**`
are outside the write set. The DB window is the lead's to grant in writing, never beside a held gate
(items 12, 32).

**Hand-off (S1d).** E-d3's template pollution is confirmed and its rebuild granted (to-lead
"2026-10-29 17:24:25 GMT"); S1d's window starts only after that rebuild reports. FD-1965's widening
by annotation (that entry's rule 3) rides the next docs batch, not this row. Not this row:
which gate step should run `ruff format --check` (the process-backlog row's second limb).

**Self-review (S1d).** Every 14:21:02 (2') clause has a place: the fixture sets the migration URL to
its scratch database as the owner role (S1d-3, d6); red = the three with data present and the env
elsewhere (S1d-2, d3); green = the three passing (S1d-5, d4); the refusal control (S1d-4,
DP-S1d-1, d5); its own small test-only slice (the row, d1). The 14:42:55 format fix is a named,
separate commit, dropped only on a base reading rc 0 (S1d-0, S1d-6, d2). The data rule: S1d-1, d8.
One departure from the brief's wording, named: the red's "other at-head database" is a disposable one,
not the template, because of E-d3. The open choices are DP-S1d-1 and DP-S1d-2, never a silent pick;
S1d-3 and S1d-4 follow DP-S1d-1 (a) and change with the ruling.
