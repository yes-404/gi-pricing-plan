---
id: PL-1476
family: plan
kind: leaf
title: WK-675 Slice 2 — Designer I, canvas, inspector, load and save (FR-212, FR-213, FR-214, FR-215, FR-220, FR-221, FR-222, FR-223, FR-225, FR-226, FR-244): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-06            # original date 2026-10-05, set at the draft; minted 2026-10-06
owner: planner
tree: 88d114fc44b9a77a57f29ca30bc3ee5d693085f8
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1286, PL-1368, SL-1369, PL-1371, RS-1269, FD-1366, RL-1263, PL-1364, SL-1367, SL-1391, SL-1409, PL-1408]
---

# PL-1476 — WK-675 Slice 2: Designer I, canvas, inspector, load and save, leaf plan

*(Minted 2026-10-06 as PL-1476 from working id 9713, in the B2+B3 batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

This plan is filed under working id 9713. Its `SL-` row under WK-675 in
[`../roadmap.md`](../roadmap.md) is slice working id 9711, `draft`. The lead reserved both
(`eta.md`, 2026-10-05 12:55:02 and 12:56:24 BST) and mints both at the merge turn. The working
ids then survive only in this paragraph and in branch and file names. Written by the planner
(planner-675s2) on the lead's brief of 2026-10-05 (`brief-plan-wk675s2-2026-10-05.md`), for
the third build lane. Evidence was read at origin/main `caa4e411`, tree `88d114fc`, at
2026-10-05 12:00–13:05 BST.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`: every acceptance item is seen red, by its cause, before the
>   code that turns it green;
> - `python-test`: the `req` marker and negative tests;
> - `python-package`: Task 1's model-schema change;
> - `fastapi-service`: Tasks 2–4;
> - `contract-schema` and `contract-guard`: the regenerated contract and the untyped-body
>   guard;
> - `spec-change`: Tasks 3, 4 and 6, with the DM's texts byte for byte;
> - `vue-frontend` and `vue-best-practices`: Tasks 6–10;
> - `vue-testing-best-practices`: the frontend tests;
> - `dev-commands`: the two-half gate and the pnpm install;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The
> executor is spawned from `.claude/roles/executor.md`.

## Goal

An actuary opens `/rating/:slug/v/:version/design` from a Rating Version's page. The view
resolves the version by its own `slug@version`, loads the algorithm it pins, draws it as a
Vue Flow graph with one typed node per step, and edits each step in an inspector built for
that step type. The actuary moves through the graph by keyboard alone, and saves the edit as
a new algorithm version through a typed `POST /api/v1/rating-algorithms`. `RatingAlgorithm`
reaches the generated OpenAPI first, before any designer code (spike F2, condition 1).

**Architecture.** The backend change is small and comes first:
- two reads by `slug@version`: the algorithm (RL-1475 item 1) and the Rating Version
  (RL-1473);
- a typed save, whose body is `RatingAlgorithmDraft`, a new model-schema type. The handler
  validates it into `RatingAlgorithm` through the existing `graph_validation_error` path, so
  every FR-212 save code is unchanged (DP-S2-1);
- a typed 201, `RatingAlgorithmSaved` (DP-S2-2).

The frontend gets:
- `@vue-flow/core`, in its own lazy chunk;
- a pure `graph.ts`, which derives edges, graph order and layout from `consumes` and
  `produces`;
- `StepNode.vue`, the canvas node;
- `StepInspector.vue`, one form section per step type;
- `NodeNavigator.vue`, the keyboard path;
- `DagDesigner.vue`, which composes them;
- `RatingDesignView.vue`, the route.

The canvas draws edges from the step data and edits no edge itself. A step's inputs change in
the inspector's `consumes` field. Drag-to-connect, with `isValidConnection`, arrives with S3's
live validation.

**Tech stack:** Python 3.12, FastAPI, Pydantic v2, pytest; Vue 3 `<script setup lang="ts">`,
Vite, Vitest with happy-dom, `@vue-flow/core` 1.48.2 (MIT, the version RS-1269 measured,
`RS-1269`:116), and the generated client (`openapi-typescript`).

**Spec, map plan, spike record and rulings:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md):
  - §3.1 (FR-212, FR-213, FR-214, FR-215; `03:81-84`);
  - §3.2 (FR-220, FR-221, FR-222, FR-223, FR-225, FR-226; `03:106-112`);
  - §3.5 (FR-244, `03:146`);
  - §4.1 and §4.3;
  - §5.1 (`03:893-917`);
  - §5.3's DAG designer row and its *Interaction requirement* (`03:1231`, `03:1238-1241`);
  - §8's Vue Flow row (`03:1314`);
- [`../specs/00-overview.md`](../specs/00-overview.md): FR-24 (`00:235`), FR-25 (`00:236`),
  NFR-463 (`00:540`), FR-10, FR-21;
- `PL-1286` (WK-675's map plan, `draft`): S2's row (`:304`), *Carried obligations* (spike
  F2's five conditions, `:256-272`), DP-4 and DP-5 (`:243-244`), and the contention table
  (`:396-412`);
- `RS-1269` (`docs/research/RS-01269-wk-675-vue-flow-designer-at-200-steps.md`): the F2
  decision and its 12:25:21 BST amendment (`:311-353`), the harness (`:126-152`) and the
  bundle method (`:280-293`);
- the rulings, all unminted, with their working ids: RL-1473 (DP-5; #1055 @`39bd865b`);
  RL-1474 (DP-6; #1055, the same head); RL-1475 (DP-4's texts; #1067 @`96fa35bf`); RL-1438
  (FR-223's check point; #1061). Each was read to its last dated amendment at those heads;
- `FD-1366` (`docs/findings/FD-01366-untyped-json-request-bodies-publish-open-objects-fd-1335-s-request-side-twin.md`),
  *Disposition* (`:70-80`), rule (ii).

## The decisions this plan rests on, quoted

1. **FD-1366's per-route hold, rule (ii)** (the maintainer, after 09:01 BST on 2026-10-01;
   `~/gi-pricing-plan.local/handover/holds-2026-10-01.md`:5): *"(ii) a slice that EDITS one
   of those handlers (e.g. WK-675 S2 on POST /rating-algorithms) does NOT wait: it TYPES the
   body in the same slice (wires the existing shape, e.g. RatingAlgorithm) and removes that
   entry from UNTYPED_REQUEST_PENDING in the same commit"*.
2. **DP-S2-1 and DP-S2-2**, decided by the maintainer (by delegation) in the `to-lead.md` entry stamped
   **2026-10-05 12:59:02 BST**, as the lead relayed them. DP-S2-1 is option (a), under rule
   (ii), with four conditions. DP-S2-2 is `RatingAlgorithmSaved{id: UUID, slug, version}`,
   the same wire, typed, and the `03:895` §5.1 row stands unchanged. See *Decision points*.
3. **Lanes A and C both touch `03`**: option (b), run both, decided by the maintainer (by delegation) in the
   `to-lead.md` entry stamped **2026-10-05 13:00:09 BST**, item 8, as the lead relayed it.
   See *Write set, and its contention*.
4. **DP-S2-3**: option (a), decided by the maintainer (by delegation), item 10 of the `to-lead.md` entry
   headed *"2026-10-05 13:03:23 BST — #1066 (FD-1416 mint) at a202f030: NO ACK YET, one false cite in the body; then decisions 10 and 11"*: *a "no algorithm pinned"
   state plus an empty canvas, saved through the typed POST, with no re-pinning*. Option (c)
   is refused for S2, because `examples/fremtpl2/seed.py` is SL-1409's, and seeding a real
   algorithm is exit-demo work after SL-1409 merges.

## Status

`draft`. Every decision point is decided: DP-S2-1, DP-S2-2, DP-S2-3 and DP-L (above). The
plan moves to `active` only through a separate activation PR, after every
activation need below holds.

### Activation needs, in order

1. **RL-1474 (#1055) minted.** It is the ruling that defines
   `RatingAlgorithmDraft`. DP-S2-1 condition 1 requires that limb to sit in a **minted**
   ruling before the executor touches the route. Either RL-1474 mints, or a decision-maker
   adopts the limb in a minted record. #1055 is in the mint queue after SL-1409, #1048 and
   #1113 (the lead, 2026-10-05).
2. **RL-1473 (#1055) and RL-1475 (#1067) minted.** S2 applies RL-1473
   T1 and T2 and RL-1475 T1 and T2 byte for byte, and each text cites `RL-<this>`. An
   unminted record is a stop (RL-1473, *Spec changes*, last paragraph). If a minted text
   differs from the head cited above, the minted text governs and the dispatch record names
   each difference.
3. **The lane A/C conditions written into both dispatch records** (DP-L, below): each side's
   hunks and anchors, the rows between them, merge-tree rc 0 on the second merge, and gates
   that never run at the same time.
4. **Task 0 re-run at the dispatch tree**, with every row as expected or its delta named.
5. **The maintainer's agreement** to this plan, as a dated line, and **the lead's go**,
   recorded in a separate activation PR. That PR sets this plan and SL-1477 `active`.

**Lane C's order since filing** (pre-mint, 2026-10-05). WK-675 is off G2's critical path
(`to-lead.md` entry headed *"2026-10-05 13:05:42 BST — RULING (the maintainer, by delegation): G2's "in Phase 1b's form" = a scripted HTTP journey plus a served page; WK-675 is OFF G2's critical path"*),
so a HIGH G2-blocking fix whose plan is active takes lane C before this slice: the FD-1421 fix
(PL-1429, working id) first (entry headed *"2026-10-05 13:12:56 BST — DECISIONS 15 and 16; CORRECTION to my 13:03:23 item 11; a priority rule for HIGH G2 blockers"*),
and the FR-240 family fix (PL-1471, working id) if lane C frees first (entry headed
*"2026-10-05 14:28:35 BST — PL 9649 / SL 9647 (the FR-240 fix, #1152 @dc13400e): DP-5 OK; DP-6 scoped; lane placement"*).
No activation need changes. The dispatch record names the order that holds at dispatch.

## Acceptance Standard

Each item is checked by a command run from the repository root on the slice's merge tree.
"Red first" means:
- the named test was run and failed **for the stated cause** before the code that turns it
  green;
- a failure with the right status and a different cause is a plan defect
  ([`README.md`](README.md) convention 2);
- every red is recorded in the slice's ledger, with the failure line as printed.

1. **Save codes unchanged under the typed body** (DP-S2-1 condition 2). These tests in
   `backend/tests/test_rating_algorithms.py` pass unmodified:
   - `test_a_cyclic_algorithm_is_refused_at_save_time`, which asserts code
     `RATING_GRAPH_CYCLIC`;
   - `test_an_undefined_value_is_refused_with_rating_graph_unresolved_ref`, which asserts code
     `RATING_GRAPH_UNRESOLVED_REF` and its title and detail;
   - `test_another_shape_refusal_is_validation_failed`;
   - `test_a_declared_output_without_an_output_step_is_validation_failed`.

   The new `test_the_typed_save_body_keeps_the_graph_codes` asserts both codes by `code`,
   never by status alone. **Broken input:** the body typed `RatingAlgorithm`. All of them go
   red with `VALIDATION_FAILED`, and the ledger records each.
   Command: `uv run pytest backend/tests/test_rating_algorithms.py -q`.
   *(The maintainer's (by delegation) condition reads `RATING_UNRESOLVED_REF`. `03`'s code, verified at
   `caa4e411`, is `RATING_GRAPH_UNRESOLVED_REF` (`03:844`, `03:928`;
   `backend/src/app/errors.py:308`). This plan uses that spelling.)*
2. **The save route is typed** (FD-1366 rule (ii)). `test_the_save_route_publishes_typed_bodies`
   asserts two things in `app.openapi()`:
   - `POST /api/v1/rating-algorithms`'s request body is a `$ref` to `RatingAlgorithmDraft`;
   - its 201 response is a `$ref` to `RatingAlgorithmSaved`.

   Red first on `main`: the body is `{"additionalProperties": true, "type": "object"}`
   (`FD-1366`:48). If `UNTYPED_REQUEST_PENDING` exists on the dispatch tree (the SL-1367
   guard), the `POST /rating-algorithms` entry is gone from it in the same commit, and the
   guard's "a typed route still listed fails" check is green. If it does not exist, the
   ledger says so.
3. **The algorithm read** (RL-1475, *Acceptance* 1). Under `test_rating_algorithms.py`, with
   `@pytest.mark.req("FR-<a>")`:
   - a saved algorithm reads back equal to what was saved;
   - an unknown version, and another workspace's version, each answer 404 `NOT_FOUND`;
   - a principal without `rating:read` gets 403;
   - the 200 response is a `$ref` to `RatingAlgorithm`.
4. **The Rating Version read by `slug@version`** (RL-1473, *Acceptance* 1–5). Under
   `backend/tests/test_rating_versions.py`, with `@pytest.mark.req("FR-<new>")`, RL-1473's
   id:
   - **order:** by pair answers 200 and by id still answers 200. Broken input: by-id
     registered first gives 422;
   - **whose version:** the version is read by its own number, and the algorithm's number
     answers 404. Broken input: resolve by `algorithm_ref`;
   - **isolation:** another workspace's pair answers 404 `NOT_FOUND`;
   - **permission:** a principal without `rating:read` gets 403;
   - **contract:** the 200 response is a `$ref` to `RatingVersion`.
5. **The contract.** Both of these exit 0:
   - `uv run python scripts/generate-contracts.py --check`;
   - `pnpm --dir frontend generate:api` (DP-S2-1 condition 3).

   `RatingAlgorithm`, `RatingAlgorithmDraft` and `RatingAlgorithmSaved` are keys of
   `generated.json` `components.schemas`, and each is absent on `main`:
   `python3 -c "import json;s=json.load(open('docs/contracts/openapi/generated.json'))['components']['schemas'];print([k in s for k in ('RatingAlgorithm','RatingAlgorithmDraft','RatingAlgorithmSaved')])"`
   prints `[True, True, True]`.
6. **The spec texts are applied byte for byte.** RL-1473 T1 and T2 and RL-1475 T1 and T2 are
   in `03`, each found exactly once:
   - `grep -c 'Read one Rating Algorithm version (FR-' docs/specs/03-rating-engine.md`
     prints 1;
   - `grep -c 'Read one Rating Version by its' docs/specs/03-rating-engine.md` prints 1, and
     `grep -c 'is addressed by its' docs/specs/03-rating-engine.md` prints at least 1 (T1's
     FR).

   `python3 scripts/audit-docs.py` exits 0.
7. **The designer loads and renders** (FR-212, FR-215, FR-<a>, FR-<new>).
   `frontend/src/views/__tests__/RatingDesignView.test.ts` asserts each of these:
   - the generated-type client is called with the slug and version from the URL
     (RL-1473 *Acceptance* 6);
   - the algorithm is read through the version's `algorithm_ref`;
   - one node renders per step, each carrying its `step_id` and type;
   - a version whose `algorithm_ref` is `None` shows the "pins no algorithm" status text and
     an empty canvas whose save body has the version's `slug` and `version` 1, and makes
     no algorithm read (DP-S2-3 (a)).

   Command: `pnpm --dir frontend test -- RatingDesignView`.
8. **Graph derivation.** `frontend/src/components/dag/__tests__/graph.test.ts` covers:
   - edges from producer to consumer, one per consumed name;
   - graph order for the twelve-step fixture;
   - an unresolved name drawing no edge;
   - a cycle not looping `graphOrder` forever.
9. **The inspector per step type.** `frontend/src/components/dag/__tests__/StepInspector.test.ts`
   has one test per step type, each named for its FR:
   - FR-213: the `input` step edits its input-contract field;
   - FR-220: a `table` step chooses its rate table from the version's `pins.rate_tables`
     only;
   - FR-221: a `lookup` step's `as_at` is a required, explicit field;
   - FR-222 and FR-223: a `model_call` step shows the **version's** `model_reference_mode`
     read-only and offers no mode control, and a loaded step whose `mode` differs is
     flagged;
   - FR-225: an empty `reason_code` blocks save on a `constraint` step;
   - FR-226: an `output` step requires rounding mode and `dp`;
   - FR-244: an `expression` step edits `expr` as text with no function picker.
10. **Keyboard navigator** (spike F2 condition 2). `NodeNavigator.test.ts` asserts:
    - arrow keys move through the steps in graph order;
    - Home and End jump to the first and last step;
    - typing a `step_id` prefix jumps to the step;
    - Enter selects the step and opens its inspector;
    - Delete asks before removing the step.

    `accessibility-tester` verifies the designer against WCAG 2.2 AA. Its report is quoted in
    the ledger with no open finding, or with each finding carried as an `FD-` candidate to the
    lead.
11. **Save from the view** (FR-212, DP-S2-2). `RatingDesignView.test.ts` asserts three
    things:
    - save posts the edited draft with the version field the actuary set;
    - a 201 shows "Saved as `<slug>@<version>`";
    - a 409 or 422 problem is shown with its `code` and `detail`, and never as a generic error.
12. **FR-25.** `pnpm --dir frontend test -- reachability` passes with the new route
    registered and **not** whitelisted. `RatingVersionView.vue` links to it, and the test
    `RatingVersionView.test.ts` asserts the link's `href`.
13. **Bundle stays split** (F2 condition 3). The built `dist/assets/` has a chunk named
    `vueflow-*.js`, and no `@vue-flow` module is in `index-*.js`. The PR body lists each
    changed chunk raw and gzip, before and after, with the shared entry chunk always shown
    (`PL-1368` Task 6 Step 2's method). The figures are WK-675's baseline.
14. **The dependency is recorded** (F2 condition 4). `frontend/package.json` pins
    `@vue-flow/core`. `03` §8's Vue Flow row and `docs/skills-map.md`'s Vue Flow row each
    state the package, the version and the licence (MIT). All three land in the same commit.
15. **Pan and zoom re-measured** (F2 condition 5 and its 12:25:21 amendment). The ledger
    records RS-1269's harness re-run on the **dev build** against `RatingDesignView` at 200
    steps, N=5, load < 12, in both forms:
    - pan-drag fps and programmatic zoom fps;
    - wheel zoom driven faster than one event per 30 ms.

    Each figure carries its build, its input interval and the clock times. Where the harness
    cannot do the second form, the ledger says so in one sentence, with the reason.
16. **The full gate, both halves** (`CLAUDE.md` §11), every command rc 0 on the merge tree,
    run through `gate-runner` in a held gate slot. Lane A's gate and this one never overlap
    (DP-L).

## Global Constraints

- **Vue 3 Composition API with `<script setup lang="ts">` only.** Never Options API, JSX or
  React (`CLAUDE.md` §3).
- **Never hand-write an API type** (`CLAUDE.md` §3). Response types alias
  `components["schemas"]` from `@/api/generated/schema`. The save body aliases
  `requestComponents["schemas"]["RatingAlgorithmDraft"]` from
  `@/api/generated/schema.requests` (OQ-655 (c), the `modelSpecs.ts:3-15` precedent). The
  spike's hand-written local type is not carried over (F2 condition 1).
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2).
  `RatingAlgorithmDraft` holds the field set once, and `RatingAlgorithm` is its subclass
  (RL-1474 item 1).
- **Money is integer minor units, or a decimal string; never a float** (`00` FR-10, FR-21).
  Every decimal in the inspector is edited and sent as a string: an input contract's
  `min`/`max`, a `clamp_bounds` value, a rounding `dp` (an integer).
- **WCAG 2.2 AA** (`00` NFR-463). A keyboard path reaches every node (F2 condition 2).
- **No rule is re-implemented in the frontend** (RL-1474, Ruled, item 2 and *What it
  obliges*). S2 shows no graph validation of its own: no cycle check and no reference check.
  On-node live validation is S3's, and `00` FR-24's DAG designer exception stays binding and
  undischarged until S3.
- **No function picker** (`PL-1286` S2; FR-276). An `expression` is edited as text. Its
  vocabulary is checked on the server at save (`EXPRESSION_INVALID_VOCABULARY`, FR-244).
- **One slice at a time within the Work. At most two build slices at once, from different
  Works, each holding a gate slot, with no shared files except as a dispatch record names**
  (`delivery-process.md` §8; `RL-1263`; `delivery-process.core.json`
  `guards.parallelism.build_slices_across_works`).

## Scope

### Requirement coverage, each id individually

| Id | What S2 does with it |
|---|---|
| FR-212 | the canvas draws the DAG; save keeps its codes under the typed body (Acceptance 1); save from the view (Acceptance 11) |
| FR-213 | the `input` step's inspector edits its input-contract field (name, type, nullability, range or domain, description) |
| FR-214 | the outputs panel lists the declared outputs; the `output` step's inspector names one |
| FR-215 | each node shows its `step_id` and label; an existing step's `step_id` is read-only in the inspector; renaming a label never changes it |
| FR-220 | the `table` step's rate table is chosen from the version's `pins.rate_tables`; the key expressions, including a banding reference, are text |
| FR-221 | the `lookup` step's `as_at` is a required, explicit field, with no default of "now" |
| FR-222 | the `model_call` step's model or peril-structure reference, and its feature map |
| FR-223 | the version's `model_reference_mode` is shown read-only on each `model_call` step; a new step takes it; a loaded step that differs is flagged. The check itself is compilation's (RL-1438), not S2's |
| FR-225 | the `constraint` step's `reason_code` is required |
| FR-226 | the `output` step's rounding mode and `dp` are required |
| FR-244 | the `expression` step's `expr` is edited as text; no picker |
| FR-237 | the version is read by its `slug@version` (RL-1473) and its pins are read from it (RL-1475 item 3) |
| FR-440 | the by-id read's §5.1 row (RL-1473 T2), unless RL 9907's WK-1178 slice applied it first |
| FR-24 | **not discharged here**: the designer's on-node live validation is S3's (RL-1474) |
| FR-25 | the new route is reachable from `RatingVersionView` (Acceptance 12) |
| NFR-463 | the keyboard navigator and the WCAG 2.2 AA check (Acceptance 10); S2 adds no chart |
| FR-10 | decimals as strings in the inspector |
| FR-21 | the same |

The new FRs that RL-1475 T1 and RL-1473 T1 create take their ids when S2 applies them. This
plan cites them as `FR-<a>` (the algorithm read) and `FR-<new>` (the version address).

**Out of S2, named so nothing is assumed:**
- FR-219's diff overlay, FR-227's type errors and DP-6's validate route are S3's;
- sub-graph mounting (FR-217, FR-218) is S9's: `sub_graphs` is carried through a save
  unchanged;
- re-pinning a Rating Version to a saved algorithm has no route. RL-1438 item 2 binds the
  slice that adds one;
- the rate table editor is S4's.

### Task 0 at planning time (measured, not asserted)

Run at `caa4e411`, 2026-10-05 12:05–13:05 BST, in the worktree `.claude/worktrees/pl-9713`.

| # | Precondition | Command | Result at `caa4e411` |
|---|---|---|---|
| 0.1 | `RatingAlgorithm` absent from the generated contract | the `python3 -c` of Acceptance 5 | `[False, False, False]` |
| 0.2 | the save route untyped, both sides | `sed -n 28,50p backend/src/app/api/rating_algorithms.py` | `body: dict[str, Any]`, `-> dict[str, Any]` (`:34`, `:37`) |
| 0.3 | the untyped-body guard not yet on `main` | `grep -rn UNTYPED_REQUEST_PENDING backend scripts` | no hit (SL-1367 is `draft`) |
| 0.4 | no Vue Flow dependency | `grep -c vue-flow frontend/package.json` | `0` |
| 0.5 | one `manualChunks` entry | `grep -n manualChunks -A4 frontend/vite.config.ts` | `echarts` only (`:26-30`) |
| 0.6 | no `/rating/` route | `grep -n 'path: "/rating' frontend/src/router/index.ts` | no hit; `/rating-versions/:id` at `:235` |
| 0.7 | the graph-code tests exist and pass | `uv run pytest backend/tests/test_rating_algorithms.py -q` | not run at planning time (no DB stack in this worktree); the executor runs it and records `N passed` |
| 0.8 | `03` §5.1's header has no `Permission` column | `grep -n '^\| Method \| Path \| Purpose \|$' docs/specs/03-rating-engine.md` | present: the three-cell forms of every RL text apply |
| 0.9 | the RL texts' anchors are each found once | `grep -c` on each anchor in *Task 3* and *Task 4* | 1 each (`03:895`, `:896`, `:897`, `:908`, `:140`, `:88`) |
| 0.10 | the demo seed writes no algorithm | `grep -n 'algorithm_ref\|rating-algorithms' examples/fremtpl2/seed.py` | no hit (DP-S2-3) |
| 0.11 | the S2-relevant rulings are unminted | `gh pr view 1055 1067 --json state` | both OPEN, draft |

At dispatch, the executor re-runs each row at the dispatch tree. Any change is named in the
ledger before Task 1.

### Write set, by file and symbol, at `caa4e411`

| Path | Symbol or region | Change |
|---|---|---|
| `packages/model-schema/src/model_schema/rating.py` | `RatingAlgorithm` (`:375`) | its six fields and `model_config` move to a new `RatingAlgorithmDraft` directly above it; `RatingAlgorithm(RatingAlgorithmDraft)` keeps `_graph_invariants`, `_reachable` and `_reaches_output` unchanged |
| the same | new `RatingAlgorithmSaved` | `{id: UUID, slug: Slug, version: int}`, frozen |
| `packages/model-schema/src/model_schema/__init__.py` | import block and `__all__` | `RatingAlgorithmDraft` and `RatingAlgorithmSaved` appended |
| `packages/model-schema/tests/test_rating_algorithm_draft.py` | new | Task 1's tests |
| `backend/src/app/api/rating_algorithms.py` | `create_rating_algorithm` (`:28-50`); new `get_rating_algorithm` | the body is `RatingAlgorithmDraft`, the response `RatingAlgorithmSaved`; the new read is after the diff route |
| `backend/src/app/platform/rating_algorithms.py` | `create_algorithm` (`:94`) | **not edited**: it keeps `content: dict[str, Any]`, and the handler passes `body.model_dump(mode="json", exclude_unset=True)` |
| `backend/src/app/api/models.py` | new `get_rating_version_by_ref` between `list_rating_versions` (`:1117`) and `get_rating_version` (`:1143`) | added, registered before the by-id read |
| `backend/tests/test_rating_algorithms.py` | new tests | Acceptance 1–3 |
| `backend/tests/test_rating_versions.py` | new tests | Acceptance 4 |
| `backend/tests/test_contracts.py` | `UNTYPED_REQUEST_PENDING`, only if SL-1367 has landed | the `POST /rating-algorithms` entry removed |
| `docs/specs/03-rating-engine.md` | §3.1 (end, before `### 3.2`); §3.4 (after FR-243, `:140`); §5.1 (before `:897`, and after `:908`); §8's Vue Flow row (`:1314`) | RL-1475 T1 and T2 and RL-1473 T1 and T2 verbatim; one §8 cell edited (Task 6) |
| `docs/skills-map.md` | the Vue Flow row (`:121`) | package, version and licence added |
| `docs/contracts/openapi/generated.json` | generated | regenerated |
| `frontend/package.json`, `frontend/pnpm-lock.yaml` | dependencies | `@vue-flow/core` `1.48.2` |
| `frontend/vite.config.ts` | `manualChunks` (`:26-30`) | a `vueflow` arm |
| `frontend/src/api/ratingAlgorithms.ts` | new | `getRatingAlgorithm`, `saveRatingAlgorithm` |
| `frontend/src/api/ratingVersions.ts` | new `getRatingVersionByRef` | added |
| `frontend/src/components/dag/graph.ts` and its test | new | pure derivations |
| `frontend/src/components/dag/StepNode.vue`, `StepInspector.vue`, `NodeNavigator.vue`, `DagDesigner.vue`, and their tests | new | the designer |
| `frontend/src/views/RatingDesignView.vue` and its test | new | the route's view |
| `frontend/src/router/index.ts` | `routes` | one lazy route, `rating-design` |
| `frontend/src/views/RatingVersionView.vue` and its test | the template | one link to the designer |
| the ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | registry |

**No `GENERATED_SHAPES` slug is added.** The three shapes reach `generated.json` through the
routes, and no client needs a standalone schema file. `scripts/generate-contracts.py` and
`ONE_SIDED_SLUGS` are not touched, so `PL-1286`'s row on `GENERATED_SHAPES` (`:402`) reads
"exempt" for S2. RL-1474 leaves this choice to the leaf plan (*What it obliges*).

### Write set, and its contention (`RL-1263`)

Classes are those of `docs/process/delivery-process.core.json`
`guards.parallelism.build_slices_across_works.no_shared_files`:
- `registry_exempt_append_only` (**exempt**), with its `generated` list and its
  `packages/*/src/*/__init__.py#__all__` key (**`__all__` name-disjoint**, amended 2026-10-05
  09:44:39 BST);
- `forbidden` (**SERIALISES**);
- `other_shared_path` (**SERIALISES unless a dispatch record names the path and its check**,
  called here **ALLOWED one-sided**, where only one slice edits the shared symbol).

**Against lane B, `SL-1409`** (in flight; `origin/sl-1409-validation-rule-approval-through-the-workflow`,
`git diff --name-only origin/main...origin/sl-1409-validation-rule-approval-through-the-workflow`,
read 2026-10-05 12:20 BST, 35 paths):

| Shared path | SL-1409 | S2 | Class |
|---|---|---|---|
| `docs/contracts/openapi/generated.json` | regenerated | regenerated | exempt (`generated`) |
| `docs/INDEX.md` | regenerated | regenerated | exempt (`generated`) |
| `packages/model-schema/src/model_schema/__init__.py` | appends its own names | appends `RatingAlgorithmDraft`, `RatingAlgorithmSaved` | `__all__` name-disjoint (no name added by both) |

Every other SL-1409 path is disjoint from S2. That includes `backend/src/app/errors.py`,
`docs/specs/01-data-management.md`, `docs/specs/06-governance.md`,
`packages/model-schema/src/model_schema/approvals.py` and `validation.py`, and the `frontend/`
rule files. S2 edits none of them, and adds no error code.

**Against lane B's next slice, PL-1454 / SL-1455** (working ids, #1113 @`a80f8d7d`,
§"Write set, and its contention" read at that head): it edits `score.py`, `db/session.py`,
`config.py`, `api/deps.py`, `api/authz.py`, `auth/service.py`, `main.py` (only under its
DP-4 (a)), `scripts/bench-rating.py` and `scripts/demo.py` (only under its DP-6 (a)). S2
touches none of them. It edits `docs/specs/03-rating-engine.md` and `00-overview.md` **only
under its DP-3 (b) or DP-5**. If either is ruled in, the shared `03` section is named at both
dispatches, and the pair serialises unless the sections differ.

**FD-1416** (filed as working id 9752; minted by #1066 at `99afcde2`, after this plan's evidence tree `caa4e411`): the four `to_dict` approval routes' responses are held. S2
reads none of them and does not touch `approvals.py`, so the hold does not apply. S7 in the
brief is lane A's WK-673 S7. Its leaf plan has not been pushed, but its row (`roadmap.md`:828)
and `PL-1267` Slice 7 (`:587-600`) name no approval route, so it does not touch them either
from the record.

**Against lane A, WK-673 S7 (`SL-1391`)**, from its row (`roadmap.md`:828) and `PL-1267`
Slice 7 (`:587-600`). Its leaf plan branch `pl-9716-wk673-s7-leaf` was not on origin at
2026-10-05 12:40 BST (`git ls-remote --heads origin 'pl-9716*'` printed nothing), so this
comparison is re-read at dispatch.

| Shared path | SL-1391 | S2 | Class |
|---|---|---|---|
| `docs/specs/03-rating-engine.md` §5.1 | edits the existing row `GET /api/v1/rate-tables/{slug}@{version}/diff?against=` (`:904`): the portfolio parameter and its refusal | adds RL-1475 T2's row before `:897`, and RL-1473 T2's two rows after `:908` | **SERIALISES** under `forbidden` (same spec section) → **run both by DP-L (b)**, under `other_shared_path` |
| `docs/specs/03-rating-engine.md` §3 | FR-231's dated clarification, §3.3 | new FRs at the end of §3.1 and after FR-243 in §3.4 | different subsections; named in both dispatch records under DP-L |
| `backend/src/app/api/rate_tables.py`, `platform/rate_tables.py` | edited | not touched | disjoint |
| `docs/contracts/openapi/generated.json`, `docs/INDEX.md` | regenerated | regenerated | exempt |
| `packages/model-schema/src/model_schema/__init__.py` | if it appends names | appends two | `__all__` name-disjoint |

**DP-L, the lane A/C row adjacency** (the maintainer's (by delegation) decision, item 8). Neither of S2's insertion
points is adjacent to SL-1391's edited row. Each has unchanged rows between it and that row at
`caa4e411`:
- **RL-1475 T2** inserts between `:896` (`rating-algorithms/{slug}@{version}/diff`) and `:897`
  (`POST /api/v1/sub-graphs`). Seven unchanged rows, `:897`–`:903`, separate it from `:904`.
  They are `POST /sub-graphs`, `POST /sub-graphs/{slug}/versions`,
  `GET /sub-graphs/{slug}@{version}`, `GET /sub-graphs/{slug}/versions`,
  `POST /rate-tables/{slug}/versions`, `POST /rate-tables/{slug}/seed-from-model` and
  `POST /rate-tables/{slug}@{version}/bulk-operation`.
- **RL-1473 T2** inserts between `:908` (`POST /api/v1/rating-versions`) and `:909`
  (`POST /api/v1/rating-versions/{id}/compile`). Four unchanged lines, `:905`–`:908`,
  separate it from `:904`. They are the CSV export, the XLSX export, the import and
  `POST /rating-versions`.

Both dispatch records list each side's hunks and these anchors. The second slice to merge:
1. merges `origin/main`;
2. re-runs `git merge-tree --write-tree origin/main HEAD` and reads rc 0 before using the
   tree (memory: check merge-tree's exit code first);
3. regenerates the generated files;
4. re-runs the full gate.

**The two gates never run at the same time.**

`frontend/src/router/index.ts` `routes` is not edited by SL-1391, SL-1409 or PL-1454 (none
names a frontend route), so S2 holds it exclusively.

### Size

Twelve tasks. Tasks 1–5 are backend and contract work of about one day; Tasks 6–11 are the
designer, the larger part. `PL-1286` (`:347-349`) flags S2 as heavier than a typical slice.
This plan keeps the cut, because (a′)'s pre-authorised split is not needed: the two read
routes are small and sit beside existing handlers. The band is **1.5 / 2 / 4 days**
(×0.75 / ×1 / ×2 on 2 days). If Task 10 or 11 overruns by a day, the lead may cut the
designer view out into an S2b under (a′); the backend half then merges first.

## Decision points

| DP | Question | Options | Recommendation | Blocking? | Resolved by |
|---|---|---|---|---|---|
| **DP-S2-1** | What type does `POST /rating-algorithms` take, now that S2 types it under FD-1366 rule (ii)? A `RatingAlgorithm` body runs the shape's validator before the handler, so a cycle or an unresolved reference would come back as a generic 422 `VALIDATION_FAILED` (`errors.py` `_handle_validation_error`, `:460-475`), not as `RATING_GRAPH_CYCLIC` or `RATING_GRAPH_UNRESOLVED_REF` (`platform/rating_algorithms.py:32-73`) | (a) `RatingAlgorithmDraft`, validated into `RatingAlgorithm` by the handler's existing path; (b) `RatingAlgorithm`, accepting the code change; (c) `RatingAlgorithm` with a request-validation hook that maps the two graph errors back | (a) | was yes | **Decided (a)**, the maintainer (by delegation), 2026-10-05 12:59:02 BST, with four conditions: (1) the type comes from a **minted** ruling, RL-1474, or a DM's minted adoption of the limb (Activation need 1); (2) broken-input reds asserted by code (Acceptance 1); (3) the guard entry, the contract and `generate:api`, all in one commit (Acceptance 2 and 5); (4) the moved limb recorded both ways (Hand-off item 1) |
| **DP-S2-2** | The 201 response's type (today `dict[str, Any]`, `{id, slug, version}`) | (i) a new `RatingAlgorithmSaved {id, slug, version}`; (ii) the saved `RatingAlgorithm` | (i) | no | **Decided (i)**, the maintainer (by delegation), 2026-10-05 12:59:02 BST: the same wire, typed. The `03:895` §5.1 row stands unchanged |
| **DP-S2-3** | A Rating Version whose `algorithm_ref` is `None`. That includes the only version the freMTPL2 seed writes (Task 0.10). What does the designer show? | (a) a "no algorithm pinned" state, plus an empty canvas pre-filled with the version's slug and algorithm version 1; save creates it, and a 409 is shown; nothing re-pins the version; (b) the state only, with no authoring; (c) seed an algorithm and its `algorithm_ref` (touches `examples/fremtpl2/seed.py`, SL-1409's path, and the G2 demo work) | **(a)**: the smallest change that makes the view usable, with no new route, and re-pinning stays out | was yes | **Decided (a)**, the maintainer (by delegation), 2026-10-05 13:03:23 BST, item 10. (c) is refused for S2: `seed.py` is SL-1409's, and seeding a real algorithm is exit-demo work after SL-1409 merges |
| **DP-L** | Lanes A and C both edit `03` §5.1 | (a) serialise; (b) run both, with dispatch records naming the hunks; (c) S2 without its rows (forbidden by `CLAUDE.md` §2) | (b) | was yes | **Decided (b)**, the maintainer (by delegation), 2026-10-05 13:00:09 BST, item 8, with four conditions (see *Contention*) |

**Choices this plan makes itself** (no spec leaves them open, or a ruling already covers them):
- **The save's version number.** The form is pre-filled with the loaded algorithm's version
  plus one, and the actuary may change it. The server already refuses an existing
  `slug@version` with 409 (`create_algorithm`, `:110-121`), and the view shows it. RL-1475
  T1's text, *"edits it into a new algorithm version, never in place"*, is met by
  construction.
- **The canvas edits no edge.** Edges are derived from `consumes` and `produces`. Connecting
  by drag needs `isValidConnection` to say whether a connection is valid, which is FR-212's
  check and S3's to serve (RL-1474). Building it here would define the check twice.
- **Persisted content is the dump of the typed body**, `model_dump(mode="json",
  exclude_unset=True)`, so what is stored is what the client sent, normalised only by the
  shape's own serialisers (an `ArtifactRef` to its canonical string). Acceptance 3's
  round-trip test pins it.
- **No `GENERATED_SHAPES` slug** (see *Write set*).

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Re-run every row of *Task 0 at planning time* at the dispatch tree. Record
  each command and its output in the ledger.
- [ ] **Step 2:** Confirm that RL-1474, RL-1473 and RL-1475 are minted. Record their minted
  ids, and diff each minted text against the head this plan cites
  (`git diff 39bd865b <mint> -- docs/rulings/`, and the same for `96fa35bf`). A difference
  in a text S2 applies is named in the ledger, and the minted text governs.
- [ ] **Step 3:** Read the lane A dispatch record's hunks. Re-read
  `origin/pl-9716-wk673-s7-leaf` or its merged plan, and confirm that SL-1391's `03` edits are
  only those in the contention table. A further `03` §5.1 edit is a stop, reported to the
  lead.
- [ ] **Step 4:** Check whether RL 9907's WK-1178 slice has already applied the by-id
  `GET /api/v1/rating-versions/{id}` row: `grep -c 'Read one Rating Version by .id., the handle' docs/specs/03-rating-engine.md`.
  If it prints 1, Task 4 applies only the `slug@version` row. Check whether the `Permission`
  column has landed: `grep -n 'Purpose . Permission' docs/specs/03-rating-engine.md`.
  If it prints a line, every row is applied in its four-cell form.
- [ ] **Step 5:** `uv sync --all-packages` and
  `pnpm --dir frontend install --frozen-lockfile` in the slice worktree (`dev-commands`).

### Task 1: `RatingAlgorithmDraft` and `RatingAlgorithmSaved` (model-schema)

**Files:**
- Modify: `packages/model-schema/src/model_schema/rating.py:375-392`
- Modify: `packages/model-schema/src/model_schema/__init__.py` (import block, `__all__`)
- Create: `packages/model-schema/tests/test_rating_algorithm_draft.py`

**Interfaces:**
- Produces: `RatingAlgorithmDraft` (fields `slug`, `version`, `input_contract`, `outputs`,
  `steps`, `sub_graphs`; frozen; `extra="forbid"`; **no** graph validator).
  `RatingAlgorithm(RatingAlgorithmDraft)` behaves exactly as today.
  `RatingAlgorithmSaved(id: UUID, slug: Slug, version: int)`.

- [ ] **Step 1: Write the failing tests**

```python
"""RatingAlgorithmDraft is RatingAlgorithm's field set without its invariants (RL-1474 item 1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema import RatingAlgorithm, RatingAlgorithmDraft, RatingAlgorithmSaved


def _cyclic() -> dict:
    """Two expression steps that consume each other's product: a cycle, nothing else wrong."""
    return {
        "slug": "cyc",
        "version": 1,
        "input_contract": [{"name": "x", "type": "decimal"}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor"}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "x", "input_name": "x",
             "on_missing": "error", "produces": "x"},
            {"step_id": "s_a", "type": "expression", "label": "a", "expr": "x + b",
             "result_type": "decimal", "consumes": ["x", "b"], "produces": "a"},
            {"step_id": "s_b", "type": "expression", "label": "b", "expr": "a",
             "result_type": "decimal", "consumes": ["a"], "produces": "b"},
            {"step_id": "s_out", "type": "output", "label": "out",
             "output_name": "payable_premium_minor",
             "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["a"], "produces": "payable_premium_minor"},
        ],
    }


@pytest.mark.req("FR-212")
def test_the_draft_accepts_a_graph_the_algorithm_refuses() -> None:
    RatingAlgorithmDraft.model_validate(_cyclic())
    with pytest.raises(ValidationError):
        RatingAlgorithm.model_validate(_cyclic())


@pytest.mark.req("FR-212")
def test_the_field_set_is_written_once() -> None:
    assert issubclass(RatingAlgorithm, RatingAlgorithmDraft)
    assert RatingAlgorithm.model_fields.keys() == RatingAlgorithmDraft.model_fields.keys()


@pytest.mark.req("FR-212")
def test_the_draft_still_refuses_an_unknown_field() -> None:
    with pytest.raises(ValidationError):
        RatingAlgorithmDraft.model_validate({**_cyclic(), "cycle_note": "x"})


def test_the_saved_shape_is_the_201_wire() -> None:
    saved = RatingAlgorithmSaved.model_validate(
        {"id": "01a04394-338b-7651-9e42-c73ee70396f8", "slug": "motor-gb", "version": 2}
    )
    assert saved.model_dump(mode="json") == {
        "id": "01a04394-338b-7651-9e42-c73ee70396f8", "slug": "motor-gb", "version": 2,
    }
```

The fixture's step fields are verified against `rating.py:259-339` at `caa4e411`. If
`money_minor` or `decimal` is not an accepted `type` for `InputContractField` or
`AlgorithmOutput` on the dispatch tree, mirror `valid_algorithm()` in
`backend/tests/test_rating_algorithms.py:64` instead of inventing one (`README.md`
convention 3).

- [ ] **Step 2: Run them to see them fail.**
  `uv run pytest packages/model-schema/tests/test_rating_algorithm_draft.py -q`. Expected:
  collection fails with `ImportError: cannot import name 'RatingAlgorithmDraft'`. Any other
  cause is a plan defect.
- [ ] **Step 3: Implement.** In `rating.py`, directly above `class RatingAlgorithm`:

```python
class RatingAlgorithmDraft(BaseModel):
    """A Rating Algorithm's field set, without its graph invariants (03 §4.1; RL-1474 item 1).

    The body of `POST /rating-algorithms` (WK-675 S2) and of S3's validate route: a graph
    that breaks an invariant reaches the handler, which validates it into `RatingAlgorithm`
    and refuses with the invariant's own code, not a generic request-validation 422.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: Slug
    version: int = Field(ge=1)
    input_contract: list[InputContractField]
    outputs: list[AlgorithmOutput]
    steps: list[RatingStep]
    sub_graphs: list[SubGraphRef] = Field(default_factory=list)


class RatingAlgorithmSaved(BaseModel):
    """The 201 of `POST /rating-algorithms`: the saved version's id and address (DP-S2-2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    slug: Slug
    version: int = Field(ge=1)
```

  Change `class RatingAlgorithm(BaseModel):` to `class RatingAlgorithm(RatingAlgorithmDraft):`.
  Delete its `model_config` and its six field lines, and keep its docstring, validator and
  helpers unchanged. Import `UUID` if `rating.py` does not already. Append both names to
  `__init__.py`'s import from `.rating` and to `__all__`, and to nothing else.
- [ ] **Step 4: Run the tests to see them pass, and the existing ones stay green.**
  Run `uv run pytest packages/model-schema -q` and
  `uv run pytest backend/tests/test_sub_graphs*.py -q`. `SubGraphBody` calls
  `RatingAlgorithm._reachable` and `_reaches_output` (`sub_graphs.py:118`, `:122`), so they
  must still resolve.
- [ ] **Step 5: Commit.** `feat(model-schema): RatingAlgorithmDraft and RatingAlgorithmSaved (WK-675 S2, RL-<9767 minted>)`

### Task 2: The typed save route (FD-1366 rule (ii); DP-S2-1, DP-S2-2)

**Files:**
- Modify: `backend/src/app/api/rating_algorithms.py:28-50`
- Modify: `backend/tests/test_rating_algorithms.py` (new tests at the end)
- Modify, only if present: `backend/tests/test_contracts.py` `UNTYPED_REQUEST_PENDING`

**Interfaces:**
- Consumes: `RatingAlgorithmDraft`, `RatingAlgorithmSaved` (Task 1).
- Produces: `POST /api/v1/rating-algorithms`, with body `RatingAlgorithmDraft` and 201
  `RatingAlgorithmSaved`.

- [ ] **Step 1: Write the failing tests**

```python
@pytest.mark.req("FR-212")
def test_the_save_route_publishes_typed_bodies(app) -> None:
    operation = app.openapi()["paths"]["/api/v1/rating-algorithms"]["post"]
    body = operation["requestBody"]["content"]["application/json"]["schema"]
    created = operation["responses"]["201"]["content"]["application/json"]["schema"]
    assert body == {"$ref": "#/components/schemas/RatingAlgorithmDraft"}
    assert created == {"$ref": "#/components/schemas/RatingAlgorithmSaved"}


@pytest.mark.req("FR-212")
def test_the_typed_save_body_keeps_the_graph_codes(
    api_client, workspace_id, principal, grant
) -> None:
    """DP-S2-1 condition 2: the codes, never the status alone."""
    cyclic = valid_algorithm()
    cyclic["steps"][6]["consumes"] = ["risk_premium_minor", "expense_factor", "cycle_val"]
    cyclic["steps"][7] = {
        "step_id": "s_minprem", "type": "constraint", "label": "Cycle",
        "condition": "true", "on_violation": "clamp", "reason_code": "CYCLE",
        "consumes": ["office_premium_minor"], "produces": "cycle_val",
    }
    unresolved = valid_algorithm()
    unresolved["steps"][6]["consumes"] = [
        "risk_premium_minor", "expense_factor", "commission_factor",
    ]
    assert _post(api_client, workspace_id, principal, grant, cyclic).json()["code"] == (
        "RATING_GRAPH_CYCLIC"
    )
    assert _post(api_client, workspace_id, principal, grant, unresolved).json()["code"] == (
        "RATING_GRAPH_UNRESOLVED_REF"
    )


@pytest.mark.req("FR-212")
def test_the_save_answers_the_typed_201(api_client, workspace_id, principal, grant) -> None:
    response = _post(api_client, workspace_id, principal, grant, valid_algorithm())
    assert response.status_code == 201, response.text
    assert set(response.json()) == {"id", "slug", "version"}
```

  The two broken bodies are the existing tests' own (`:141-158`, `:237-248`). The `app`
  fixture is the one `test_rating_versions.py:423` uses. Mirror it if its name differs.
- [ ] **Step 2: Run to see the first test fail by its cause.**
  `uv run pytest backend/tests/test_rating_algorithms.py -q -k "typed or publishes"`.
  Expected: `test_the_save_route_publishes_typed_bodies` fails because `body` is an inline
  open object, not a `$ref`. The other two pass on `main`: they are the regression net
  that broken input must turn red (Step 4).
- [ ] **Step 3: Implement**

```python
@router.post(
    "/rating-algorithms",
    summary="Create or version a Rating Algorithm",
    status_code=status.HTTP_201_CREATED,
    responses=problems(401, 403, 422, 409),
)
async def create_rating_algorithm(
    body: RatingAlgorithmDraft,
    caller: RatingWriteDep,
    database: DatabaseDep,
) -> RatingAlgorithmSaved:
    """**201** with the saved slug and version, once save-time validation passes.

    The body is a `RatingAlgorithmDraft` (03 §4.1): the field set without the graph
    invariants, so a cyclic or unresolved graph reaches save-time validation and is refused
    with its named code (FR-212), not with a generic request-validation 422. The deeper
    checks in `pricing-core` (FR-216/227/273/274/275/276) follow.
    """
    assert caller.principal.id is not None
    row = await service.create_algorithm(
        database,
        caller.workspace_id,
        caller.principal.id,
        body.model_dump(mode="json", exclude_unset=True),
    )
    return RatingAlgorithmSaved(id=row.id, slug=row.slug, version=row.version)
```

  Import `RatingAlgorithmDraft` and `RatingAlgorithmSaved` from `model_schema`. Drop `Any`
  from the `typing` import if no other annotation in the file uses it. After Task 3, the
  diff route still does. If `UNTYPED_REQUEST_PENDING` exists, remove its
  `POST /rating-algorithms` entry in this commit.
- [ ] **Step 4: Broken input, red by cause.** Temporarily change the annotation to
  `body: RatingAlgorithm` and rerun `uv run pytest backend/tests/test_rating_algorithms.py -q`.
  Expected: `test_the_typed_save_body_keeps_the_graph_codes`,
  `test_a_cyclic_algorithm_is_refused_at_save_time` and
  `test_an_undefined_value_is_refused_with_rating_graph_unresolved_ref` fail with code
  `VALIDATION_FAILED`, where the tests expect the graph code. Paste the three failure lines
  into the ledger, then revert the annotation.
- [ ] **Step 5: Green.** Run the whole file, plus `uv run pytest backend/tests/test_contracts.py -q`.
- [ ] **Step 6: Commit.** This commit holds Task 2, Task 5's contract regeneration and the
  guard-entry removal together (DP-S2-1 condition 3). Commit after Task 5.

### Task 3: The algorithm read by `slug@version` (RL-1475 T1, T2)

**Files:**
- Modify: `docs/specs/03-rating-engine.md` (§3.1 end; §5.1 before `:897`)
- Modify: `backend/src/app/api/rating_algorithms.py` (a new route after `algorithm_diff`)
- Modify: `backend/tests/test_rating_algorithms.py`

**Interfaces:**
- Consumes: `service.get_algorithm(database, workspace_id, slug, version) -> RatingAlgorithm`
  (`platform/rating_algorithms.py:135`).
- Produces: `GET /api/v1/rating-algorithms/{slug}@{version}`, which returns 200
  `RatingAlgorithm`.

- [ ] **Step 1: Spec first.** Apply RL-1475 T1 (the last row of §3.1, on the line before the
  blank line preceding `### 3.2 Rating step types`) and T2 (immediately before the row that
  begins `| `POST` | `/api/v1/sub-graphs` |`) **byte for byte, from the minted record**. Fill
  `RL-<this>`, `FR-<a>` (the next integer from `python3 scripts/doc-id.py next`, the single
  global sequence of `document-ids.md`:179, coordinated with the lead, who is the sole
  allocator) and `<date>`, and change nothing else.
  If an anchor is not found exactly once, stop and report to the lead. Run
  `python3 scripts/audit-docs.py`.
- [ ] **Step 2: Write the failing tests** (RL-1475 *Acceptance* 1):

```python
@pytest.mark.req("FR-<a>")
def test_a_saved_algorithm_reads_back_by_slug_at_version(
    api_client, workspace_id, principal, grant
) -> None:
    saved = _post(api_client, workspace_id, principal, grant, valid_algorithm())
    assert saved.status_code == 201, saved.text
    read = api_client.get(
        "/api/v1/rating-algorithms/motor-gb@1", headers=_headers(principal, workspace_id)
    )
    assert read.status_code == 200, read.text
    assert RatingAlgorithm.model_validate(read.json()) == RatingAlgorithm.model_validate(
        valid_algorithm()
    )


@pytest.mark.req("FR-<a>")
def test_an_unknown_algorithm_version_is_not_found(
    api_client, workspace_id, principal, grant
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    read = api_client.get(
        "/api/v1/rating-algorithms/motor-gb@99", headers=_headers(principal, workspace_id)
    )
    assert read.status_code == 404, read.text
    assert read.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-<a>")
def test_the_algorithm_read_publishes_rating_algorithm(app) -> None:
    operation = app.openapi()["paths"]["/api/v1/rating-algorithms/{slug}@{version}"]["get"]
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema == {"$ref": "#/components/schemas/RatingAlgorithm"}
```

  Add the **isolation** test (another workspace's `motor-gb@1` answers 404 `NOT_FOUND`) and
  the **permission** test (a principal with no role answers 403) by mirroring the existing
  cross-workspace and no-grant tests in `backend/tests/test_sub_graphs*.py`. `grep -n
  'another_workspace\|403' backend/tests/test_sub_graphs*.py` finds them. Do not invent a
  second workspace fixture (`README.md` convention 3). Replace `FR-<a>` with the minted id.
- [ ] **Step 3: Run to see them fail by cause.** The read tests fail with **404 from the
  router** (no route matches `GET`, and the body's `detail` is FastAPI's "Not Found", not a
  problem `code`). The contract test fails with `KeyError` on the path.
- [ ] **Step 4: Implement**

```python
@router.get(
    "/rating-algorithms/{slug}@{version}",
    summary="Read one Rating Algorithm version",
    responses=problems(401, 403, 404, 422),
)
async def get_rating_algorithm(
    slug: str, version: int, caller: RatingReadDep, database: DatabaseDep
) -> RatingAlgorithm:
    """**200** with the saved algorithm (FR-<a>); another workspace's is a **404**."""
    return await service.get_algorithm(database, caller.workspace_id, slug, version)
```

- [ ] **Step 5: Green**, plus a broken-input check: return `RatingAlgorithmDraft` from the
  handler. The contract test fails with the wrong `$ref`. Record it, and revert.
- [ ] **Step 6: Commit** `feat(rating): GET /rating-algorithms/{slug}@{version} (FR-<a>, RL-<9753>)`.

### Task 4: The Rating Version read by `slug@version` (RL-1473 T1, T2)

**Files:**
- Modify: `docs/specs/03-rating-engine.md` (§3.4 after FR-243, `:140`; §5.1 after `:908`)
- Modify: `backend/src/app/api/models.py` (a new route between `:1135` and `:1138`)
- Modify: `backend/tests/test_rating_versions.py`

**Interfaces:**
- Consumes: `rating_versions_service.resolve_rating_version_ref(session, *, workspace_id, ref: ArtifactRef)`
  (`platform/rating_versions.py:169`) and `rating_versions_service.to_schema(row)` (`:93`).
- Produces: `GET /api/v1/rating-versions/{slug}@{version}`, which returns 200 `RatingVersion`.

- [ ] **Step 1: Spec first.** Apply RL-1473 T1 (after the row that begins `| **FR-243** |`)
  and T2 (after the row that begins `| `POST` | `/api/v1/rating-versions` |`), byte for byte
  from the minted record, in the three-cell or four-cell form that Task 0 Step 4 found.
  Apply the by-id row only if Task 0 Step 4 printed 0. Run `python3 scripts/audit-docs.py`.
- [ ] **Step 2: Write the failing tests** (RL-1473 *Acceptance* 1–5):

```python
@pytest.mark.req("FR-<new>")
def test_a_rating_version_reads_by_its_own_slug_at_version(
    api_client, workspace_id, principal, grant, database
) -> None:
    import asyncio

    from app.api.deps import DEV_PRINCIPAL_HEADER

    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}
    model_ref = ArtifactRef(type="model", slug="fremtpl2-glm", version=1)
    rating_id = asyncio.get_event_loop().run_until_complete(
        _draft(database, workspace_id, principal, model_ref)
    )
    asyncio.get_event_loop().run_until_complete(
        _set_algorithm_ref(database, rating_id, "rating_algorithm:fremtpl2-demo@5")
    )

    by_pair = api_client.get("/api/v1/rating-versions/fremtpl2-demo@1", headers=headers)
    assert by_pair.status_code == 200, by_pair.text
    assert by_pair.json()["id"] == str(rating_id)

    by_id = api_client.get(f"/api/v1/rating-versions/{rating_id}", headers=headers)
    assert by_id.status_code == 200, by_id.text

    by_algorithm_number = api_client.get(
        "/api/v1/rating-versions/fremtpl2-demo@5", headers=headers
    )
    assert by_algorithm_number.status_code == 404, by_algorithm_number.text
    assert by_algorithm_number.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-<new>")
def test_the_rating_version_read_publishes_rating_version(app) -> None:
    operation = app.openapi()["paths"]["/api/v1/rating-versions/{slug}@{version}"]["get"]
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema == {"$ref": "#/components/schemas/RatingVersion"}
```

  `_set_algorithm_ref` is a new helper in the test file. It opens
  `database.unit_of_work()`, loads the `RatingVersionRow` by id, and sets `row.algorithm_ref`
  to the string. `create_rating_version` has no `algorithm_ref` parameter
  (`platform/rating_versions.py:230-238`). Add the **isolation** test (another workspace's
  `fremtpl2-demo@1` answers 404 `NOT_FOUND`, the same body as an unknown pair) and the
  **permission** test (403 without `rating:read`) by mirroring
  `test_an_unknown_rating_version_id_is_a_404_over_http` (`:235`) and the module's existing
  no-grant test.
- [ ] **Step 3: Run to see them fail by cause.** `/rating-versions/fremtpl2-demo@1` answers
  **422** from the by-id handler (`uuid_parsing` on `rating_version_id`). That is RL-1473's
  proved routing trap, so a 404 here is a different cause and a plan defect.
- [ ] **Step 4: Implement**, registered before `get_rating_version`:

```python
@router.get(
    "/rating-versions/{slug}@{version}",
    summary="Get a rating version by its slug@version",
    responses=problems(401, 403, 404, 422),
)
async def get_rating_version_by_ref(
    slug: str,
    version: int,
    caller: Annotated[Caller, Depends(requires(Perm.RATING_READ))],
    database: DatabaseDep,
) -> RatingVersion:
    """**200** with the version its own `slug@version` names (FR-<new>, RL-<9766>).

    Registered before the by-id read: `{rating_version_id}` matches any one segment,
    `fremtpl2-demo@1` included, and would answer 422.
    """
    async with database.session() as session:
        row = await rating_versions_service.resolve_rating_version_ref(
            session,
            workspace_id=caller.workspace_id,
            ref=ArtifactRef(type="rating_version", slug=slug, version=version),
        )
        return rating_versions_service.to_schema(row)
```

  If `ArtifactRef` is not already imported in `models.py`'s `from model_schema import (...)`
  block (`:77`), add it there.
- [ ] **Step 5: Broken input, red by cause.** Move the new route below
  `get_rating_version`, and the pair test fails with 422 `uuid_parsing`. Record it, and
  restore. Then resolve by `algorithm_ref` instead (filter on `RatingVersionRow.algorithm_ref`
  in a scratch edit): the "whose version" assertion fails. Record it, and revert.
- [ ] **Step 6: Green.** Run `uv run pytest backend/tests/test_rating_versions.py -q`.
- [ ] **Step 7: Commit** `feat(rating): GET /rating-versions/{slug}@{version} (FR-<new>, RL-<9766>)`.

### Task 5: The contract and the generated client (DP-S2-1 condition 3)

**Files:** `docs/contracts/openapi/generated.json` (generated).

- [ ] **Step 1:** `uv run python scripts/generate-contracts.py`, then
  `uv run python scripts/generate-contracts.py --check` (exit 0).
- [ ] **Step 2:** `pnpm --dir frontend generate:api` (exit 0). Then confirm all three names
  exist: `grep -c 'RatingAlgorithmDraft\|RatingAlgorithmSaved\|RatingAlgorithm:' frontend/src/api/generated/schema.d.ts`
  prints at least 3. The directory is VCS-ignored and not committed.
- [ ] **Step 3:** Run Acceptance 5's `python3 -c`, which must print `[True, True, True]`.
- [ ] **Step 4: Commit** Tasks 2 and 5 together (Task 2 Step 6):
  `feat(rating): type POST /rating-algorithms (FD-1366 rule (ii); DP-S2-1, DP-S2-2)`.

### Task 6: The dependency, the chunk and the records (F2 conditions 3 and 4)

**Files:** `frontend/package.json`, `frontend/pnpm-lock.yaml`, `frontend/vite.config.ts:26-30`,
`docs/specs/03-rating-engine.md:1314`, `docs/skills-map.md:121`.

- [ ] **Step 1:** `pnpm --dir frontend add @vue-flow/core@1.48.2`. Use exactly the version
  RS-1269 measured. A later version is a new measurement, not this one.
- [ ] **Step 2:** In `manualChunks` (`vite.config.ts:26-30`), make this the function's
  first statement, and leave the existing ECharts `return` unchanged after it. Keep the
  function form (`:24-25`):

```ts
if (/node_modules[\\/]@vue-flow[\\/]/.test(id)) return "vueflow";
```

- [ ] **Step 3: `03` §8 row** (`spec-change`; a tech dependency changes). Replace the Vue Flow
  row's first cell, `**Vue Flow (frontend)**`, with
  `**Vue Flow (frontend)**: `@vue-flow/core` 1.48.2, MIT (adopted 2026-09-28, `RS-1269` F2; added in WK-675 Slice 2)`.
  The other cells stay as they are. Then, in `docs/skills-map.md:121`, append to the row's
  notes cell: ` **Adopted:** `@vue-flow/core` 1.48.2, MIT, WK-675 S2 (`RS-1269` F2).` Both
  edits go in this commit with `package.json` (F2 condition 4; `CLAUDE.md` §10). Run
  `python3 scripts/audit-docs.py`.
- [ ] **Step 4: Commit** `build(frontend): @vue-flow/core 1.48.2 in its own chunk; 03 §8 and skills-map (RS-1269 F2)`.

### Task 7: The API modules and `graph.ts`

**Files:**
- Create: `frontend/src/api/ratingAlgorithms.ts`
- Modify: `frontend/src/api/ratingVersions.ts`
- Create: `frontend/src/components/dag/graph.ts`, `frontend/src/components/dag/__tests__/graph.test.ts`

**Interfaces:**
- Produces:
  - `getRatingAlgorithm(slug: string, version: number): Promise<RatingAlgorithm>`;
  - `saveRatingAlgorithm(body: RatingAlgorithmDraft): Promise<RatingAlgorithmSaved>`;
  - `getRatingVersionByRef(slug: string, version: number): Promise<RatingVersion>`;
  - `names(v): string[]`, `edgesOf(steps): FlowEdge[]`, `graphOrder(steps): string[]` and
    `layout(steps): Record<string, { x: number; y: number }>`;
  - `parseRef(ref: string): { type: string; slug: string; version: number }`.

- [ ] **Step 1: The API modules**

```ts
// frontend/src/api/ratingAlgorithms.ts
import { request } from "./client";
import type { components } from "./generated/schema";
import type { components as requestComponents } from "./generated/schema.requests";

export type RatingAlgorithm = components["schemas"]["RatingAlgorithm"];
export type RatingAlgorithmSaved = components["schemas"]["RatingAlgorithmSaved"];
/** The save body: the permissive generated set, since a defaulted field may be omitted (OQ-655 (c)). */
export type RatingAlgorithmDraft = requestComponents["schemas"]["RatingAlgorithmDraft"];
export type RatingStep = RatingAlgorithmDraft["steps"][number];

export function getRatingAlgorithm(slug: string, version: number): Promise<RatingAlgorithm> {
  return request<RatingAlgorithm>(
    `/rating-algorithms/${encodeURIComponent(slug)}@${version}`,
  );
}

export function saveRatingAlgorithm(
  body: RatingAlgorithmDraft,
  idempotencyKey: string,
): Promise<RatingAlgorithmSaved> {
  return request<RatingAlgorithmSaved>("/rating-algorithms", {
    method: "POST",
    body,
    idempotencyKey,
  });
}
```

```ts
// appended to frontend/src/api/ratingVersions.ts
/** The version its own `slug@version` names (RL-1473): the address the §5.3 routes use. */
export function getRatingVersionByRef(slug: string, version: number): Promise<RatingVersion> {
  return request<RatingVersion>(`/rating-versions/${encodeURIComponent(slug)}@${version}`);
}
```

  Check `RequestOptions` (`client.ts:33-48`) for the `method` and `body` field names, and
  mirror an existing POST caller (`grep -n 'method: "POST"' frontend/src/api/*.ts`).
- [ ] **Step 2: The failing `graph.test.ts`.** The fixture is
  `valid_algorithm()`'s twelve steps, transcribed into a `fixtures.ts` in the same
  `__tests__` directory, typed `RatingAlgorithmDraft`. The tests:
  - `edgesOf` gives one edge per (producer, consumer, name), `id` `${source}->${target}:${name}`;
  - a consumed name with no producer draws no edge;
  - `graphOrder` on the fixture equals the steps' declared order, because the fixture is
    already topological. Pin the array;
  - `graphOrder` on two steps that consume each other returns both, so it terminates and
    appends the cycle in declared order;
  - `layout` puts every step in a column equal to its longest-path depth, and is
    deterministic (two calls are deep-equal);
  - `parseRef("rating_algorithm:motor-gb@14")` gives
    `{ type: "rating_algorithm", slug: "motor-gb", version: 14 }`.

  Run `pnpm --dir frontend test -- graph`. Expected: fail to import `../graph`.
- [ ] **Step 3: Implement `graph.ts`**

```ts
import type { RatingStep } from "@/api/ratingAlgorithms";

export interface FlowEdge { id: string; source: string; target: string; label: string }

export function names(value: string | string[] | undefined): string[] {
  if (value === undefined) return [];
  return Array.isArray(value) ? value : [value];
}

/** One edge per consumed name, from its first producer. Draws; never validates (S3 does). */
export function edgesOf(steps: readonly RatingStep[]): FlowEdge[] {
  const producer = new Map<string, string>();
  for (const step of steps) {
    for (const name of names(step.produces)) {
      if (!producer.has(name)) producer.set(name, step.step_id);
    }
  }
  const edges: FlowEdge[] = [];
  for (const step of steps) {
    for (const name of names(step.consumes)) {
      const source = producer.get(name);
      if (source === undefined || source === step.step_id) continue;
      edges.push({ id: `${source}->${step.step_id}:${name}`, source, target: step.step_id, label: name });
    }
  }
  return edges;
}

/** Kahn's order, ties by declared position; steps left on a cycle are appended in declared order. */
export function graphOrder(steps: readonly RatingStep[]): string[] {
  const ids = steps.map((s) => s.step_id);
  const incoming = new Map(ids.map((id) => [id, 0]));
  const out = new Map<string, string[]>(ids.map((id) => [id, []]));
  for (const e of edgesOf(steps)) {
    incoming.set(e.target, (incoming.get(e.target) ?? 0) + 1);
    out.get(e.source)?.push(e.target);
  }
  const order: string[] = [];
  const ready = ids.filter((id) => incoming.get(id) === 0);
  while (ready.length > 0) {
    const id = ready.shift() as string;
    order.push(id);
    for (const next of out.get(id) ?? []) {
      const left = (incoming.get(next) ?? 0) - 1;
      incoming.set(next, left);
      if (left === 0) ready.splice(insertionIndex(ready, next, ids), 0, next);
    }
  }
  return order.concat(ids.filter((id) => !order.includes(id)));
}

function insertionIndex(ready: string[], id: string, ids: string[]): number {
  const at = ids.indexOf(id);
  const index = ready.findIndex((r) => ids.indexOf(r) > at);
  return index === -1 ? ready.length : index;
}

const COLUMN = 260;
const ROW = 120;

export function layout(steps: readonly RatingStep[]): Record<string, { x: number; y: number }> {
  const depth = new Map<string, number>();
  const edges = edgesOf(steps);
  for (const id of graphOrder(steps)) {
    const parents = edges.filter((e) => e.target === id).map((e) => depth.get(e.source) ?? 0);
    depth.set(id, parents.length === 0 ? 0 : Math.max(...parents) + 1);
  }
  const rows = new Map<number, number>();
  const at: Record<string, { x: number; y: number }> = {};
  for (const id of graphOrder(steps)) {
    const column = depth.get(id) ?? 0;
    const row = rows.get(column) ?? 0;
    rows.set(column, row + 1);
    at[id] = { x: column * COLUMN, y: row * ROW };
  }
  return at;
}

export function parseRef(ref: string): { type: string; slug: string; version: number } {
  const match = /^([a-z_]+):([^@]+)@(\d+)$/.exec(ref);
  if (match === null) throw new Error(`not an artifact reference: ${ref}`);
  return { type: match[1] as string, slug: match[2] as string, version: Number(match[3]) };
}
```

  On a cycle, a step's depth reads its parents before they are set and takes 0 for them.
  That is acceptable for a drawing of a graph that save will refuse. Pin it with one test,
  so that a change is deliberate.
- [ ] **Step 4: Green**, `pnpm --dir frontend test -- graph` and `pnpm --dir frontend type-check`.
- [ ] **Step 5: Commit** `feat(frontend): rating algorithm API and DAG graph derivation (WK-675 S2)`.

### Task 8: `StepNode.vue` and `StepInspector.vue` (FR-213, FR-215, FR-220, FR-221, FR-222, FR-223, FR-225, FR-226, FR-244)

**Files:** `frontend/src/components/dag/StepNode.vue`, `StepInspector.vue`, and
`__tests__/StepInspector.test.ts`.

**Interfaces:**
- `StepNode` props: `{ data: { step: RatingStep } }` (Vue Flow's custom-node `data`). It
  renders the type badge, the label, `step_id` and the produced names.
- `StepInspector` props:
  `{ step: RatingStep; isNew: boolean; inputContract: InputContractField[]; rateTablePins: string[]; versionMode }`, where `versionMode` is the generated `RatingVersion["model_reference_mode"]`.
  It emits `update:step` (a new step object, never a mutation) and
  `update:inputContract`. It exposes `problems: ComputedRef<string[]>`, the required-field
  gaps that block save in the view, such as an empty `reason_code`. These are presence
  checks of fields the shape requires. They are not graph rules, and they repeat no
  server check.

  `InputContractField` aliases `components["schemas"]["InputContractField"]`. If the name
  is absent from `generated.json` after Task 5, alias it as
  `RatingAlgorithm["input_contract"][number]`.

- [ ] **Step 1: The failing tests**, one per row of Acceptance 9, each named with its FR, for
  example `it("FR-220: a table step chooses its rate table from the version's pins only")`.
  Use `@testing-library/vue` and `user-event`, as `RatingVersionView.test.ts` does. Key
  assertions:
  - **FR-220:** the rate-table control is a `<select>` whose options are exactly
    `rateTablePins`, and no free-text table field exists;
  - **FR-221:** clearing `as_at` makes `problems` contain `as_at is required (FR-221)`;
  - **FR-222/223:** `screen.getByText(/Model reference mode: exact \(set on the Rating Version, FR-223\)/)`,
    and `screen.queryByRole("combobox", { name: /mode/i })` is `null`. A step whose `mode` is
    `approximation` while `versionMode` is `exact` shows `role="status"` text naming
    both modes. When `isNew` is true, the emitted step has `mode === versionMode`;
  - **FR-225:** an empty `reason_code` puts `reason_code is required (FR-225)` in `problems`;
  - **FR-226:** the rounding `mode` is a `<select>` over `half_even`, `half_up`, `ceiling` and
    `floor`. These are read from the generated `RoundSpec["mode"]` union through a typed
    const array whose `satisfies` clause pins it, as `modelSpecs.ts` does. `dp` is required;
  - **FR-244:** `expr` is a `<textarea>`, and no element has a name matching `/function/i`;
  - **FR-215:** when `isNew` is false, the `step_id` input is `readonly`; editing the label
    emits a step with the same `step_id`;
  - **FR-213:** an `input` step shows its `input_contract` entry (matched by `input_name`)
    with type, nullable, min, max, domain and description. Editing `min` emits the string
    typed in, never a number (FR-10).
- [ ] **Step 2: Run to see each fail on the missing component.**
  `pnpm --dir frontend test -- StepInspector`.
- [ ] **Step 3: Implement.** One `<section>` per `step.type`, selected by `v-if` on the
  discriminant, with labelled controls (`<label for>`), and no `v-html`. Every edit emits
  `{ ...step, field: value }`. `StepNode.vue` uses `Handle` from `@vue-flow/core` with
  `:connectable="false"`. Its root carries `:aria-label="`${step.type} step ${step.label} (${step.step_id})`"`.
- [ ] **Step 4: Green.** Run `pnpm --dir frontend test -- StepInspector`, then lint and
  type-check.
- [ ] **Step 5: Commit** `feat(frontend): DAG step node and per-type inspector (FR-213, FR-215, FR-220, FR-221, FR-222, FR-223, FR-225, FR-226, FR-244)`.

### Task 9: `NodeNavigator.vue` and `DagDesigner.vue` (F2 condition 2)

**Files:** `frontend/src/components/dag/NodeNavigator.vue`, `DagDesigner.vue`, and
`__tests__/NodeNavigator.test.ts`.

**Interfaces:**
- `NodeNavigator` props: `{ steps: RatingStep[]; selected: string | null }`. It emits
  `select(stepId)` and `remove(stepId)`. It is a `role="listbox"` with
  `aria-activedescendant`, its options in `graphOrder`.
- `DagDesigner` props: `{ draft: RatingAlgorithmDraft; versionMode; rateTablePins: string[] }`.
  It emits `update:draft`. It composes `<VueFlow>` (nodes from `layout`, edges from `edgesOf`,
  `:nodes-connectable="false"`), `NodeNavigator`, `StepInspector` and an add-step menu. The
  add-step menu has one entry per step type, read from the generated `RatingStep["type"]`
  union through a pinned const array. It also exposes `problems`, the union over the steps.

- [ ] **Step 1: The failing navigator tests** (Acceptance 10's list). Use
  `user.keyboard("{ArrowDown}")`, `{Home}`, `{End}`, `{Enter}` and `{Delete}`. Typing `s_o`
  moves to `s_out`. For Delete, assert that a confirmation (`role="alertdialog"`) appears
  and that `remove` is emitted only after confirm.
- [ ] **Step 2: Fail, then implement `NodeNavigator.vue`.** Implement the roving active
  option, a typeahead buffer cleared after 500 ms, and the confirm dialog.
- [ ] **Step 3: `DagDesigner.vue`.** Import `@vue-flow/core/dist/style.css` and
  `theme-default.css` here, so the CSS rides in the lazy chunk. On `select`, call
  `useVueFlow().fitView({ nodes: [id], duration: 0 })`, so a keyboard selection brings the
  node into view. View-level tests stub `VueFlow` (`global.stubs`), because happy-dom has no
  layout engine. The canvas itself is measured in Task 11, not unit-tested here.
- [ ] **Step 4: Green; commit** `feat(frontend): DAG designer and keyboard node navigator (RS-1269 F2 condition 2)`.

### Task 10: `RatingDesignView.vue`, the route and the FR-25 link

**Files:** `frontend/src/views/RatingDesignView.vue` and its test;
`frontend/src/router/index.ts`; `frontend/src/views/RatingVersionView.vue` and its test.

- [ ] **Step 1: The failing view tests.** Mock `@/api/ratingVersions` and
  `@/api/ratingAlgorithms` as `RatingVersionView.test.ts:6-10` does, and stub
  `DagDesigner`'s `VueFlow`. Assert each of these:
  - `getRatingVersionByRef` is called with `("fremtpl2-demo", 1)` from props `slug` and
    `version` (RL-1473 *Acceptance* 6, test named `FR-<new>: …`);
  - `getRatingAlgorithm` is called with the parsed `algorithm_ref` (`FR-<a>: …`);
  - one node per step is rendered;
  - save calls `saveRatingAlgorithm` with the draft and the version field (pre-filled to the
    loaded version plus 1), then shows `Saved as motor-gb@2`;
  - a rejected save with
    `ProblemError({ code: "RATING_GRAPH_CYCLIC", detail: "…" })` shows both strings in
    `role="alert"`;
  - save is disabled while `problems` is non-empty.
- [ ] **Step 2: Implement.** `props: { slug: string; version: string }`, with the route
  `props` function converting `version` to a number. The steps, in order:
  1. resolve the pair;
  2. if `algorithm_ref` is set, `parseRef` it and load the algorithm;
  3. keep a `ref<RatingAlgorithmDraft>`;
  4. mount `DagDesigner` through `defineAsyncComponent(() => import("@/components/dag/DagDesigner.vue"))`,
     so that `@vue-flow` stays in the lazy chunk even if another view imports the view;
  5. save with an idempotency key from `crypto.randomUUID()`, regenerated after each
     response.
- [ ] **Step 3: DP-S2-3 (a)** (decided, 13:03:23 BST). When `algorithm_ref` is `None`:
  - show `role="status"` text: "This Rating Version pins no algorithm yet. Saving creates
    `<slug>@1`; pinning it to the version is not part of this view.";
  - start from an empty draft with `slug` = the version's slug, `version` = 1, and empty
    lists;
  - make no `getRatingAlgorithm` call.

  The save goes through the typed POST, and a 409 for an existing `<slug>@1` is shown as in
  Step 1. Nothing re-pins the version. `examples/fremtpl2/seed.py` is not touched. A test
  pins this (Acceptance 7).
- [ ] **Step 4: The route**, after `rating-version` (`router/index.ts:240`):

```ts
{
  path: "/rating/:slug/v/:version/design",
  name: "rating-design",
  component: () => import("@/views/RatingDesignView.vue"),
  meta: { requiresAuth: true },
  props: (route) => ({ slug: String(route.params.slug), version: String(route.params.version) }),
},
```

- [ ] **Step 5: The FR-25 link.** In `RatingVersionView.vue`, add
  `<RouterLink :to="`/rating/${rating.slug}/v/${rating.version}/design`">Open in the designer</RouterLink>`
  beside the status. Extend `RatingVersionView.test.ts` to assert its `href`. The test's
  `RouterLink` stub must pass `to` through: render `<a :href="to"><slot /></a>` with
  `props: ["to"]`. Run `pnpm --dir frontend test -- reachability`. It must pass with no
  whitelist change, because the reachability graph reads the view sources'
  `RouterLink :to`. If the template-literal form is not resolved by `routeGraph`, read
  `frontend/src/router/__tests__/routeGraph.ts`, and use the form it resolves (the
  `DemoView.vue:224` precedent is a template literal).
- [ ] **Step 6: Green; commit** `feat(frontend): /rating/:slug/v/:version/design (FR-25, FR-<new>, FR-<a>)`.

### Task 11: The measurements (F2 conditions 2, 3 and 5)

- [ ] **Step 1: Bundle delta** (Acceptance 13). Build `origin/main` in a scratch worktree
  and the slice head in this one, each with `pnpm --dir frontend build`. Record Vite's chunk
  table from both, and put every changed `dist/assets/*.js` chunk, raw and gzip, before and
  after, in the PR body and the ledger. Always include `index-*.js`. Confirm that
  `grep -l '@vue-flow' dist/assets/index-*.js` prints nothing. Compare the designer chunk
  with RS-1269's 49,445 B gzip (`:324`), and report the difference, not a verdict.
- [ ] **Step 2: Pan and zoom on the dev build** (Acceptance 15). Restore the spike harness
  from `a3862e01` (`pw/fps2.mjs`, `pw/run.sh`; `git show a3862e01:pw/fps2.mjs >
  $CLAUDE_JOB_DIR/tmp/pw/fps2.mjs`), outside the repository tree. Point it at
  `vite --port 5391 --strictPort` serving the slice head, on `/rating/<slug>/v/<n>/design`,
  with a 200-step algorithm saved through the API. Generate it as RS-1269 did (`:100-112`).
  Measure:
  - pan-drag;
  - programmatic zoom (`setViewport(…, {duration: 3000})`);
  - wheel zoom, driven through CDP `Input.dispatchMouseEvent` at a fixed 8 ms interval,
    which is faster than the one event per ~30 ms the amendment names.

  Run N=5 per form at load < 12 (`uptime` before each run). Record each run's start and end
  BST, the load, the fps and the event interval achieved. If the harness cannot drive wheel
  events faster than one per 30 ms on this box, record the measured interval and that
  sentence (F2's 12:25:21 point (3)).
- [ ] **Step 3: Accessibility** (Acceptance 10). Delegate to `accessibility-tester`, naming
  the route, the navigator and the inspector, against WCAG 2.2 AA. Quote its report in the
  ledger. Each finding is fixed in this slice or sent to the lead as an `FD-` candidate.
  None is waived silently.
- [ ] **Step 4:** These steps measure and need no gate slot. They must not run inside
  another lane's gate window (`delivery-process.core.json`
  `guards.parallelism.measurement_step_runs_alone`). Check the slots first.

### Task 12: The gate and the ledger

- [ ] **Step 1: The full gate, both halves** (`CLAUDE.md` §11), delegated to `gate-runner`
  in a held gate slot, after confirming that lane A's gate is not running (DP-L). Every
  command has rc 0. Record the per-command table and the tree.
- [ ] **Step 2: Self-check Acceptance 1–16**, command by command. Paste each output into
  the ledger.
- [ ] **Step 3: Open the PR**, naming the range `origin/main...HEAD`, the bundle delta and the
  measurements, and stating which FD-1366 case applied (rule (ii), and whether the guard
  entry existed).

## Hand-off

1. **To S3's leaf plan, or its dispatch record if S3's plan is frozen first** (DP-S2-1
   condition 4): *"`RatingAlgorithmDraft` (RL-1474 item 1's type limb) was built in WK-675
   S2 (PL-1476), with `RatingAlgorithm` as its subclass and the save route typed by it. S3
   does not re-add it. S3 still owns RL-1474 items 2–7 (the breach-returning invariant
   function, `ValidationIssue`'s move, `AlgorithmValidationReport`, and the validate route)
   and T1–T4, including T3's §4.1 paragraph that names the type. Until S3 applies T3, the
   type is published in the contract with no §4.1 prose. S2's own plan records this."* The
   lead copies this line into S3's dispatch record at S3's dispatch. The planner writes it
   into S3's leaf plan when that is drafted.
2. **To the lead, for `PL-1286`:** DP-4's and DP-5's *Resolved by* cells cite RL-1475 and
   RL-1473 once minted. `PL-1286` is the planner's file, and it is not edited here.
3. **To the auditor at slice close:** FD-1366's `POST /rating-algorithms` entry is
   discharged by rule (ii) in this slice. The finding's register row names the S2 PR.
4. **To S4 onwards:** a view at `/rating/:slug/v/:version/…` resolves the pair through
   `getRatingVersionByRef` and acts by `id`, with no second lookup (RL-1473, *What it
   obliges*). S4 reads the version's tables from `pins.rate_tables` (RL-1475 item 3).
5. **To the lead, a record defect, not an edit:** `PL-1368` (S1's leaf plan) still reads
   `status: active`, while SL-1369 is `closed`.

## Self-review

- **Ruling coverage, by site class** (`README.md` convention 5). The rulings and decisions
  were found by diffing the ruling files against `origin/main`, not by listing headings. Each
  appears in the narrative, Files, Steps and Acceptance:
  - RL-1475 item 1, T1 and T2: *Architecture*; Task 3's Files; Task 3 Steps 1–5;
    Acceptance 3 and 6;
  - RL-1473 T1 and T2 and Acceptance 1–6: *Architecture*; Task 4's Files; Task 4 Steps 1–5;
    Task 10 Step 1; Acceptance 4, 6 and 7;
  - RL-1474 item 1, as a type only: Task 1; Hand-off 1; Global Constraints;
  - RL-1438: FR-223's row in *Scope*; Task 8 Step 1;
  - DP-S2-1 conditions 1–4: Activation need 1; Acceptance 1, 2 and 5; Task 2 Step 4;
    Task 5 Step 4; Hand-off 1;
  - DP-S2-2: Task 1; Task 2 Step 3; Acceptance 2;
  - DP-S2-3 (a): *The decisions*, item 4; Status; the DP table; Task 10 Step 3; Acceptance 7;
  - DP-L: *Contention*; Activation need 3; Task 12 Step 1; Acceptance 16;
  - F2 conditions 1–5: Acceptance 5, 10, 13, 14 and 15; Tasks 5, 6, 9 and 11.
- **Literals verified at `caa4e411`:** the route paths, handler names and lines
  (`rating_algorithms.py:28-73`, `models.py:1112-1160`), `create_algorithm` and
  `get_algorithm` (`platform/rating_algorithms.py:94`, `:135`), `resolve_rating_version_ref`
  and `to_schema` (`rating_versions.py:169`, `:93`), `create_rating_version`'s parameters
  (`:230-238`), the step classes and their literals (`rating.py:271-339`), `InputContractField`
  (`:207`), `RoundSpec`'s modes (`:255`), `ArtifactRef`'s type `rating_algorithm` and
  `rating_version` (`refs.py`'s `ARTIFACT_TYPES`), the error codes
  (`errors.py:307-308`), the test names in `test_rating_algorithms.py` (`:128-290`), the
  router lines (`router/index.ts:232-240`), `vite.config.ts:24-30`, `package.json` scripts
  (`:9-18`), and `ratingVersions.ts`'s pattern.
  **Not verified:** whether `InputContractField` and `RoundSpec` keep those names in the
  generated schema after Task 5 (Task 8 gives the fallback); Vue Flow 1.48.2's exact
  `fitView` option names (Task 9 Step 3 names the call, and the type-check decides); and
  whether `routeGraph` resolves a template-literal `:to` (Task 10 Step 5 names the fallback).
- **Spec coverage, by enumeration.** S2's row in `PL-1286` (`:304`) was read clause by
  clause. F2 conditions 1–5 map to Acceptance 5, 10, 13, 14 and 15; the canvas and typed
  nodes to Tasks 8 and 9; the inspector's seven step types to Task 8; the read-only mode to
  FR-223's row; the navigator to Task 9; the save to Task 2 and Task 10; and the FR-25 link
  to Task 10. "No function picker" is in Global Constraints and Acceptance 9.
- **Placeholders:** `FR-<a>`, `FR-<new>`, `RL-<9753>`, `RL-<9766>` and `RL-<9767 minted>`
  stand for ids that exist only at mint or apply time. Each is named in Task 0 Step 2 or in
  the step that fills it. No other placeholder remains.
- **Rulings re-checked before the PR:** open PRs at `072c56e1`, 2026-10-05 12:15 BST; working ids as
  then (`gh pr list --state open`, 34 open). It was re-read for this plan's subject: #1055 @`39bd865b`, #1067 @`96fa35bf`,
  #1061 (RL-1438) and #1059 (FD-1437). FD-1437's limbs (2) and (3) are S3's (RL-1438, *What
  it obliges*). #1113 @`a80f8d7d` is lane B. Nothing else rules on the designer, the save
  route or the two reads.
- **Pre-mint check of 2026-10-05 15:26 BST, at `origin/main` `809a3794`.** No backend,
  frontend, package or script file changed since `caa4e411`, so every code line above holds.
  In `03` only line 136 changed, in place; every `03` line cited is unmoved, and each anchor
  that Tasks 3 and 4 name is found once (`grep -cF` = 1). #1055 is still at `39bd865b` and
  #1067 at `96fa35bf`, both unminted. FD-1416 minted as FD-1416 (#1066), so its paragraph and
  *The decisions* item 4's header are re-pointed. Lane C's order is recorded under the
  activation needs. The G2 ruling changes no task: S2 was never a G2 prerequisite, and item 4
  already leaves the seeded algorithm to the exit demo.
