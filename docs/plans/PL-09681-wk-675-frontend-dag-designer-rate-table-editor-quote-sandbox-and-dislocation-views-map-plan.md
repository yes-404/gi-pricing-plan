---
id: PL-9681
family: plan
kind: map
title: WK-675 — Frontend: DAG designer, rate table editor, quote sandbox and dislocation views: map plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-29
owner: planner
tree: f0c3d197f5d89863efc647a2d7c1a6994b74dd63
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1172, RL-1184, CR-1212, CR-1243, CR-1247, PL-1213, PL-1237, OQ-550, OQ-1223, OQ-1231]
---

# WK-675 — Frontend: DAG designer, rate table editor, quote sandbox and dislocation views: map plan

> **For agentic workers:** this is a **map plan**. It cuts WK-675 into slices and fixes their
> scope, order, dependencies and gates. It carries no code steps. Each slice gets its own leaf
> plan (`kind: leaf`) before it starts, and the executor works from the leaf plan with
> `subagent-driven-development` or `executing-plans`. **Working id `9681`**; minted at this
> PR's merge turn with `python3 scripts/doc-id.py next --ref origin/main`.
> **`status: draft`: two decision points block its freeze** (see *Decision points*).

## Goal

Build the four rating-engine views WK-675's roadmap row names: the **DAG designer**, the
**rate table editor**, the **quote sandbox with its ladder waterfall and compare**, and the
**dislocation views** (`03` §5.3). Each is built on routes that a backend Work has delivered
or delivers, and none hand-writes a shape (`CLAUDE.md` §2, §3). The Work is done when every
id in **Scope** has a verdict and every *Acceptance Standard* item below holds.

**Architecture.** This is a map plan, per `docs/process/delivery-process.md` §5 step 2, in the
form of `PL-1237` (WK-674's map plan). The views are Vue 3 SFCs under `frontend/src/views/`,
routed in `frontend/src/router/index.ts`, consuming the generated client in
`frontend/src/api/generated` only. **The design direction for the designer is fixed by spike
F2** (the deputy's decision of 2026-09-28 12:13:47 BST, amended 12:25:21 BST, both by the
maintainer's delegation): Vue Flow is adopted under five conditions. Its research record is PR
#834 (`p2-f2-rs` at `45e818b7`, open at this tree), which quotes the decision whole. The five
conditions are requirements of the designer slices, listed under *Carried obligations*.

**Tech Stack.** Vue 3 (`<script setup lang="ts">` only), Vite, Pinia, Tailwind, ECharts
through `vue-echarts` (present: `frontend/package.json:20,24`). **Two new dependencies:**
`@vue-flow/*` (the designer; absent from `package.json` and `pnpm-lock.yaml` at this tree) and
`@tanstack/vue-table` (the rate table editor's grid; absent). Each lands with its
`docs/skills-map.md` entry and `03` §8 row in the same PR, with its licence (`CLAUDE.md` §10;
F2 condition 4).

**Spec.** The sections the executors read with their leaf plan:

- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md): §5.3 (`03:1040-1057`, the
  views and the *Interaction requirement*), §5.1 (`03:739-853`, the routes each view
  consumes), §3's FRs listed under **Scope**, §4.10 (`StepChange`, `own_change`).
- [`../specs/00-overview.md`](../specs/00-overview.md): FR-24 (`00:228`, a §5.3 Contents cell
  binds nothing, with seven named exceptions), FR-25 (every registered route reachable by
  links), NFR-463 (`00:529`, WCAG 2.2 AA and an accessible table for every chart), FR-10 and
  FR-21 (money is never a float), §5.6 (the canonical route table), and OQ-550 (`00:552`).
- [`../workflows/`](../workflows/): `WF-699` A1–A6, B1–B8, D6–D8; `WF-701` A5, A6.

## Acceptance Standard

These conditions are for the Work as a whole. Each leaf plan states its own conditions for its
slice. Every command runs in the executor's own worktree against the range
`origin/main...HEAD`.

1. **Every decision point below is ruled** by a filed `RL-` before the slice it blocks starts:
   `git grep -n 'OQ-550\|OQ-1223\|OQ-1231' docs/open-questions.md` shows each `closed`, citing
   its `RL-`. DP-4, DP-5 and DP-6 are each an `RL-` with its spec amendment in the same commit.
2. **The four views' routes are registered and reachable** (FR-25):
   `grep -nE 'rating/:slug/v/:version/(design|tables/:tableSlug|sandbox|dislocation)' frontend/src/router/index.ts`
   prints four lines, and `pnpm --dir frontend test` passes the route-graph test
   (`frontend/src/router/__tests__/routeGraph.test.ts`) with each route reachable from `/`.
3. **Each FR in Scope has a test naming it.** A view limb is tested in the frontend, in this
   repo's convention of the id in the test name: for each id,
   `grep -rlE '<id>[^0-9]' frontend/src --include=*.test.ts` prints at least one file
   (`req-coverage.py` does not read the frontend, so this is the predicate). A backend route
   this Work adds (DP-4, DP-6, F-W10-3, and S7b if DP-2 rules (b)) carries its
   `@pytest.mark.req` marker, and `uv run python scripts/req-coverage.py` counts it.
4. **No hand-written API shape:** every rating type a view uses is imported from
   `frontend/src/api/generated`, and `RatingAlgorithm` (and each shape a view reads) is in
   `docs/contracts/openapi/generated.json`'s `components.schemas`. At this tree it is not
   (only the `RatingVersion*` shapes are). `uv run python scripts/generate-contracts.py
   --check` rc 0.
5. **Every chart has its accessible table** (NFR-463), in the form DP-1 rules, and each new
   chart's table is asserted under test with the column-by-name reader the ruling names.
6. **The designer's keyboard node navigator is verified** against WCAG 2.2 AA by the
   `accessibility-tester` agent, its report cited in the slice's ledger (F2 condition 2).
7. **The bundle stays split** (F2 condition 3): `@vue-flow` and `@tanstack/vue-table` sit in
   lazy chunks with `manualChunks` entries, and each slice's PR reports the shared entry
   chunk's size change from `pnpm --dir frontend build`.
8. **`own_change: false` is never rendered as "unchanged" or "not edited"** (the WK-672
   hand-off, `PL-1213`): a compare-view test with an edited step whose input also moved
   asserts the rendered label.
9. **The owed register rows are resolved:** `python3 scripts/register-owed.py WK-675` prints no
   row without a resolution, and F39, F-W10-1 and F-W10-3 (see *Carried obligations*) each
   carry a dated resolution.
10. **The gate is green:** the two-half gate of `CLAUDE.md` §11 at the Work's last slice head,
    and the four docs checks rc 0.

## Global Constraints

- **Vue 3 Composition API with `<script setup lang="ts">` only**; never Options API, JSX or
  React (`CLAUDE.md` §3).
- **Never hand-write an API type**; generate it from OpenAPI (`CLAUDE.md` §3; ADR-704's
  one-way flow, `CLAUDE.md` §2).
- **Money is integer minor units or a decimal string, never a float** (`00` FR-10, FR-21); the
  editor's decimal input and every rendered premium follow `vue-frontend`'s rules.
- **WCAG 2.2 AA, and an accessible tabular equivalent for every chart** (`00` NFR-463).
- **Every registered route is reachable by links from the entry** (`00` FR-25).
- **One slice at a time** (`delivery-process.md` §8).
- **A new dependency changes `docs/skills-map.md` and the spec's §8 in the same PR** (`CLAUDE.md`
  §10).

## Scope

### The four views, and the requirements each carries

Derived from `03` §5.3 and the §3 FRs, not from recollection (`CLAUDE.md` §13). **`00` FR-24
makes each §5.3 Contents cell prose that binds nothing**, except its seven named exceptions,
one of which is here (the designer's on-node live validation). So each view's obligations are
its FR ids, that exception, the *Interaction requirement* paragraph (`03:1052-1055`), and the
cross-cutting FR-25 and NFR-463.

| View (route, `03` §5.3) | FRs it serves | Backend it consumes, and its state at `f0c3d197` |
|---|---|---|
| **DAG designer** (`/rating/:slug/v/:version/design`, `03:1045`) | FR-212, FR-213, FR-214, FR-215, FR-219, FR-220, FR-221, FR-222, FR-223, FR-225, FR-226, FR-227, FR-244, FR-246, FR-276; FR-217 and FR-218 (the mount, with WK-1250); the FR-24 exception. `WF-699` B2–B5 and B8 exercise the step types | Save `POST /api/v1/rating-algorithms` (`rating_algorithms.py:29`) and diff (`:54`) exist (WK-669, closed). **Loading an algorithm has no route** (DP-4). Sub-graph mounting waits on **WK-1250** (`draft`) |
| **Rate table editor** (`/rating/:slug/v/:version/tables/:tableSlug`, `03:1046`) | FR-228, FR-229, FR-230, FR-231, FR-232, FR-233, FR-234, FR-235, FR-1186 | Diff, bulk, import, export and seed exist (WK-670, closed). **The manual-edit route `POST /api/v1/rate-tables/{slug}/versions` (`03:745`) is absent, and its owner is this Work** (F-W10-3). **Reading cells has no route** (DP-4). The exposure-weight column waits on F-W10-2 |
| **Quote sandbox** (`/rating/:slug/v/:version/sandbox`, `03:1047`) | FR-213, FR-247, FR-248, FR-249, FR-251, FR-252, FR-255, FR-256, FR-258, **FR-262's view limb** | `POST /api/v1/score` (`score.py:277`, WK-671) and `POST /api/v1/score/compare` (`score.py:331`, WK-672) exist. OQ-1231 decides whether the compare route changes |
| **Dislocation** (`/rating/:slug/v/:version/dislocation`, `03:1049`) | FR-263, FR-264, FR-265, FR-266 | **Absent.** WK-673 builds `POST` and `GET /api/v1/dislocation-runs` and registers `DislocationRun` for generation (Slice 4 of #844, WK-673's map plan, working id 9101, `p2-wk673-map` at `59d11c49`, open) |

**FR-262** is WK-675's by `RL-1172` item 5 and `CR-1243` (the WK-672 close): the backend limb
is delivered; the view limb is this Work's, and FR-262 is delivered only when both have landed.

### Not WK-675's: three §5.3 views no Work owns

`03` §5.3 lists seven views. WK-675's row names four. **The other three are owned by no
roadmap row, plan, ruling or closure at `f0c3d197`**, and this plan does not fold them in,
because that would be scope the roadmap does not give this Work:

- **Rating version list** (`/rating`, `03:1044`);
- **Regression suite** (`/rating/:slug/v/:version/tests`, `03:1048`);
- **Deployments** (`/rating/environments`, `03:1050`), which also overlaps `07`'s
  `/admin/environments` view (`07:386`).

The predicate: `grep -rn -E 'rating/environments|/rating\`|Rating version list|Regression suite view|/v/:version/tests|Deployments view|admin/environments' docs --include=*.md`
prints five lines, `03:1044`, `:1048`, `:1050`, `07:386` and `docs/findings/register.md:61`. The
last is a false positive: it matches "/rating\`" inside "`pricing_core/rating\``". WK-674's map
plan (`PL-1237` Task 2, `:774`) adds only the **backend** `GET` for deployment history, not the
view. **Raised as a finding**, which auditor-row8 files (working id 9692), with the owning
decision routed by the lead (`RFC-1248` Part 2: nothing unowned).

**A consequence for FR-25:** with no rating version list, a designer or sandbox route needs
another path from the entry. Until one is owned, each view's slice links to its route from the
existing `RatingVersionView` (`/rating-versions/:id`, `frontend/src/router/index.ts:235`),
which is reachable today. DP-5 decides how a slug-and-version route and that UUID route meet.

## Decision points

Each is the decision-maker's to rule, as an `RL-` (`document-ids.md` §1.6). The options and
recommendations are the planner's proposal, not a ruling.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| **DP-1 = OQ-550** | How does `ChartFigure` relate a row's values to its columns? (`00:552`; re-opened 2026-09-28 as **WK-675's entry decision, due at this map plan**, `RL-1184` E10) | (a) positional rows with the two W6b-9 checks; (b) rows keyed by column name, checked by the type system; (c) a column descriptor, rows staying domain objects | **(b).** It makes misalignment a compile error at the one moment the cost is lowest: 13 call sites today (`git grep -n '<ChartFigure' -- 'frontend/src/*.vue'`), and this Work adds at least four charts. (c) also removes the transcription step, but it makes `ChartFigure` generic, which is the largest change, for a smaller further gain | decision point | **yes**: the plan's freeze, and **Slice 1** (the migration) and every chart slice after it (S6's waterfall, S8's dislocation charts) | decision-maker, by `RL-` |
| **DP-2 = OQ-1231** | Is `StepChange.own_change` derived from the traces (a) or from step-definition equality by `step_id` across the two compiled algorithms (b)? (gated *Before WK-675's map plan* on #917, `wk1178-oq-1231-1233` at `a95622cc`, open) | as the OQ states them | the OQ's own recommendation is (b); the decision-maker rules it | decision point | **yes**: **this plan's freeze**, since (b) adds a backend slice to the route WK-672 delivered (`score.py:331`, `diff_traces`). The compare slice is sized both ways below | decision-maker, by `RL-` (working id 9691, in progress) |
| **DP-3 = OQ-1223** | How does an ordinal categorical input take part in a `monotone` property? | as the OQ states them | the OQ's own recommendation is (a), "when the rate-table editor introduces the order" | decision point | no — resolved before Slice 5's leaf plan goes `active`. Until then, a categorical `monotone` is refused before generation (the OQ's stated interim) | decision-maker, by `RL-` |
| **DP-4** | The views need read routes **declared nowhere and built nowhere**: an algorithm by `{slug}@{version}` (the designer's load), and a rate table's cells and a version's table list (the editor). Who adds them? | (a) **this Work**: each route is spec-changed first by the decision-maker and built in the slice whose view consumes it, as F-W10-3 already makes this Work own `POST /rate-tables/{slug}/versions`; (b) a WK-1178 backend slice before WK-675; (c) leave the views to compose reads from existing routes | **(a).** The consuming view is the only place the route's shape is known; F-W10-3 is the precedent; (c) is impossible for the designer, since no route returns an algorithm's graph | scope | no — resolved before Slice 2's and Slice 4's leaf plans go `active`. Until then, no read route is added | decision-maker, by `RL-` |
| **DP-5** | §5.3 routes address a version as `:slug/v/:version`, but the backend reads a Rating Version only by UUID (`GET /rating-versions/{id}`, `models.py:1139`), a Phase 1b route in no §5.1 | (a) add `{slug}@{version}` read routes, the form `03` §5.1 already uses for algorithms and tables; (b) change the §5.3 and `00` §5.6 routes to `/rating-versions/:id/...` | **(a).** It matches every other versioned route in `03` §5.1 and keeps `00` §5.6's four canonical routes unchanged | decision point | no — resolved before Slice 2's leaf plan goes `active`. Until then, views are linked from `/rating-versions/:id` | decision-maker, by `RL-` |
| **DP-6** | The designer's **on-node live validation** is an FR-24 exception, binding until discharged at this view's slice plan (`00:228`). What discharges it, and how does the view validate before save? | (a) raise it as a numbered `03` FR, served by a **validate-only route** that runs the server's own checks (spec change: the FR plus the route); (b) raise the FR, and re-implement the cycle, reference and type checks in the frontend; (c) declare the cell exhaustive and validate on save only | **(a).** (b) defines the validation rules twice, the divergence `CLAUDE.md` §2 forbids; (c) fails the *Interaction requirement* that an invalid graph be "visibly invalid before save" | decision point | no — resolved before Slice 3's leaf plan goes `active`. Until then, the FR-24 exception stays binding and undischarged | decision-maker, by `RL-` |

**The freeze.** This plan stays `draft` until DP-1 and DP-2 are ruled. DP-1 decides Slice 1's
content; DP-2 decides whether the compare view is one slice or two. DP-3 to DP-6 each block
only their slice's leaf plan, which does not go `active` until its DP is ruled.

## Carried obligations

**Spike F2's five conditions** (the deputy's decision of 2026-09-28 12:13:47 BST and its
12:25:21 BST amendment; quoted whole in PR #834), each a requirement of the designer slices:

1. **`RatingAlgorithm` reaches the generated OpenAPI before any designer code** (Slice 2's
   first task). The spike's hand-written local type is not carried over.
2. **A keyboard node navigator is an acceptance requirement**, verified by
   `accessibility-tester` against WCAG 2.2 AA (Slice 2).
3. **The bundle stays split**, `@vue-flow` in the lazy designer chunk with a `manualChunks`
   entry; the deltas are this Work's baseline (Slice 2, then every slice's PR).
4. **Vue Flow is a new dependency**: `docs/skills-map.md` and `03` §8 change in the same PR,
   with its licence (Slice 2).
5. **Pan and zoom are re-measured on the dev build** if the RS record measured the production
   build (N=5, load < 12); and, per the 12:25:21 amendment, **wheel zoom is re-measured with
   an input source faster than one event per ~30 ms**, or the slice states that the harness
   cannot (Slice 2).

**The WK-672 hand-off** (`PL-1213`, quoted in `c9f50232`'s body): `own_change: false` means
"no own change attributable from the traces" and is **never rendered as "unchanged" or "not
edited"** (Slice 7).

**Register rows** (`docs/findings/register.md` at `f0c3d197`):
- **F-W10-3** (L67): the manual-edit route, owner "the WK-675 rate-table editor slice" →
  **Slice 4**. `register-owed.py WK-675` prints this row.
- **F-W10-1** (L62): the rate-table diffs, bulk operations and import/export UI; `CR-1212`
  gave it to WK-675 ("the rate-table editor slice") and it was accepted, but the register cell
  still names W10-2/W10-3 → **Slice 5**. *Listed for the auditor's register pass: the cell is
  stale, so `register-owed.py` misses it.*
- **F39** (L81): "diagnose what opens the socket", owner "the frontend workstream"; `CR-1212`
  gave it to WK-675 → **Slice 1**. *Same register-pass note.*
- **F-W10-2** (L64): the exposure weights the diff route does not pass. `CR-1212` gave it to
  **WK-673**, and the maintainer accepted that, but WK-673's draft map plan (#844, working id
  9101, at `59d11c49`) did not carry it: `grep -c F-W10-2` over that plan file prints 0.
  **Decided by the lead, 2026-09-29 19:04Z:** WK-673's plan takes F-W10-2 at its rework. The
  editor's exposure-weight column (Slice 5) **depends on that WK-673 slice** and ships with
  the weights, not as "weights unavailable".

## Tasks

**Each row is one task, cut as one slice**, and gets its own leaf plan (`kind: leaf`) before
it starts; the leaf plan carries the files, interfaces and test steps. One slice at a time
(`delivery-process.md` §8). Every slice's leaf plan names its FRs, its negative tests, and its
FR-25 and NFR-463 obligations.

| Slice | Content | Depends on | Size band (days: likely / worst) |
|---|---|---|---|
| **S1 — Chart foundation** | Apply DP-1's ruling to `ChartFigure` and migrate its 13 call sites; F39's socket diagnosis | DP-1 | 1 / 2 |
| **S2 — Designer I: canvas, inspector, load, save** | F2 conditions 1–5; `RatingAlgorithm` and the load route (DP-4, DP-5) generated; the Vue Flow canvas with typed nodes (FR-212, FR-215), the node inspector per step type (FR-213 inputs, FR-214 outputs, FR-215, FR-220 `table`'s pinned table and banding reference, FR-221 `lookup`'s as-at date source, FR-225 `constraint`'s `reason_code`, FR-226 `output`'s explicit rounding, and `expression` steps: the expression text with FR-244's function vocabulary, as the engine in use supports it (FR-276)); on each `model_call` step, the **Rating Version's** model reference mode shown read-only, not chosen per step (FR-222 records it on the version, and FR-223 requires every step's `mode` to equal it, refusing a mismatch with `MODEL_REFERENCE_MODE_INCONSISTENT`), the keyboard node navigator, save through `POST /rating-algorithms`; FR-25 link from `RatingVersionView` | DP-4, DP-5 | 1 / 2 |
| **S3 — Designer II: live validation and diff** | DP-6's discharge: the numbered FR and the validate route; errors on the node before save (FR-212, FR-223, FR-227), including `expression` steps, whose grammar (FR-244) and closed inputs (FR-246) the validate route checks; the structural diff overlay (FR-219) | S2, DP-6 | 1 / 2 |
| **S4 — Editor I: grid and manual edit** | `@tanstack/vue-table` (new dependency); the cell and table-list read routes (DP-4); the typed grid (FR-228), paged through the cell read route for either storage, and above FR-232's threshold (default 250 000 cells, `storage: parquet`) the grid still pages with no Job, and the slice states that bound under test (FR-232); the manual-edit route (F-W10-3; FR-229's required change note, FR-231's confirmation diff, FR-234's validation errors shown on the cell); no approval state on a Rate Table Version (FR-1186); inline decimal editing (FR-10, FR-21) | DP-4 | 1 / 2 |
| **S5 — Editor II: diff shading, bulk, import, export** | Diff-vs-previous and diff-vs-seed shading (FR-230, FR-231), handling the diff route's **202 with a Job** when either version is `storage: parquet` (FR-232, `03:748`): the view polls the Job and renders the same artifact; the exposure-weight column (F-W10-2); bulk-operation dialog (FR-233); CSV import confirmation and export (FR-235); DP-3's order; F-W10-1 | S4, DP-3; **WK-673's F-W10-2 slice** (#844, at its rework) | 1 / 2 |
| **S6 — Sandbox: form, waterfall, trace** | The quote form from the input contract (FR-213), scoring the version in view through an explicit `rating_version_ref` (FR-251, the what-if path that makes FR-262's "any accessible Rating Version" work); the ladder waterfall (FR-247, FR-248) as a chart with its table, including the optional `instalment_loading` rung when present (FR-252) and the per-peril risk-premium components among the outputs (FR-249); a **declined** quote rendered as a successful result with `outcome: declined`, its plural `decline_reasons` and the ladder still shown (FR-256); each typed per-quote error rendered distinctly: contract violation, reference miss, table miss, constraint decline, model failure (FR-255); the trace timeline (FR-258); the waterfall **one click from any traced quote** (`03:1054-1055`, FR-25) | S1 | 1 / 2 |
| **S7 — Sandbox compare** | FR-262's view limb over `POST /score/compare`; the `own_change` rendering rule | S6; **DP-2** | (a) 1 / 2 · (b) see S7b |
| *S7b — Compare backend* | **Only if DP-2 rules (b):** `own_change` from step-definition equality across the two compiled algorithms, in `diff_traces` and the route, with the generated contract and a negative test on a masked edit; before S7 | DP-2 = (b) | 1 / 2 |
| **S8 — Dislocation views** | The change histogram (FR-263), segment grid (FR-264), attribution waterfall (FR-266), largest movers with drill-down to individual quotes (FR-263; the §5.3 cell says "traces", and FR-263's word governs), the run cited as a persisted artifact by its id (FR-265), each chart with its table | **WK-673's Slice 4** (routes and generated `DislocationRun`); S1 | 1 / 2 |
| **S9 — Designer III: sub-graph mounting** | Mounting a pinned sub-graph in the designer (FR-217, FR-218's authoring view) | **WK-1250** (inlining and the mount declaration); S3 | 1 / 2 |

**The band, re-derived from this cut.** The frontend bands are 0.75 / 1 / 2 days per slice
(best / likely / worst), from the §5a sizing at
`~/gi-pricing-plan.local/scratch/planner-wk674-2/p2-sizing.md` (sha256
`ee99405376e1eb2d107d622488d2d4ad2687d822e8893045a08425df073664af`), relayed to the maintainer
as inputs, not a plan change. That file gave WK-675 a provisional 6–10 slices and 5 / 9 / 22
days.

| DP-2 ruling | Slices | Best (×0.75) | Likely (×1) | Worst (×2) |
|---|---|---|---|---|
| (a), the trace rule stays | 9 | 6.75 | 9 | 18 |
| (b), definition equality | 10 (with S7b) | 7.5 | 10 | 20 |

**S2 and S4 carry more than a typical slice:** S2 holds spike F2's five conditions as well as
the canvas, and S4 a new dependency as well as two backend routes. Their leaf plans confirm the
cut or split them, and the band moves with any split.

## Sequencing

- **The Work's place in P2** is `CR-1212` Proposal 2's accepted order: WK-674, then WK-673,
  then WK-675. This plan does not change it.
- **Inside the Work:** S1 → S2 → S3 → S4 → S5 → S6 → (S7b) → S7 → S8 → S9.
  - S1 comes first because DP-1's ruling changes every chart after it.
  - S8 and S9 are last because they wait on other Works: WK-673's Slice 4 and WK-1250.
  - If WK-673 or WK-1250 lands earlier, S8 or S9 may move up; that is the lead's call at
    dispatch, one slice at a time.

## Status

`draft` at `f0c3d197`. It goes `active` when DP-1 and DP-2 are ruled and the lead accepts it.
The maintainer then activates WK-675 on it.

## Self-review

- **Spec coverage, by enumeration, not by the scope list itself.** `03` §3 was read in full,
  each id against the four views: FR-212 to FR-276, FR-1186 and FR-1221 (the section's own
  ids, `03:75-228`).
  - **Placed**, each in the slice its row names:
    - S2: FR-214, FR-220, FR-221, FR-222, FR-223, FR-225, FR-226, and the `expression`
      authoring of FR-244 with FR-276;
    - S3: FR-244 and FR-246's validation;
    - S4 and S5: FR-232;
    - S6: FR-249, FR-251, FR-252, FR-255 and FR-256;
    - the rest as *Scope*'s table lists them.
  - **No limb in these four views, so not in scope:**
    - FR-216 (evaluation order) and FR-245 (`Decimal` arithmetic in the engine; the views
      follow FR-10 and FR-21);
    - FR-224 and FR-257 (approval gates; the approvals view is `06`'s);
    - FR-236 (rateable or diagnostic);
    - FR-237 to FR-243 (the Rating Version, its lifecycle and the bundle: backend, or the
      unowned version-list view);
    - FR-250 (scoring against the version live in an environment: WK-671's route, while the
      sandbox scores an explicit version, FR-251);
    - FR-253 and FR-254 (batch scoring: no view here);
    - FR-259 (production trace sampling: backend; the sandbox's trace is FR-258's, on
      request);
    - FR-260, FR-261 and FR-1221 (the Regression suite view, unowned);
    - FR-267 to FR-272 (deployment: WK-674's backend, and the Deployments view, unowned);
    - FR-273 to FR-275 (the engine boundary and compile-time checks: backend).
- **Placeholders:** none. Every open choice is a numbered decision point with options and a
  recommendation.
- **Literals** were read at `f0c3d197`: the routes (`03:743-768`), the router
  (`router/index.ts:235`), the dependencies (`package.json:20,24`), and the generated
  components (`RatingAlgorithm` absent). Open PRs that rule on this subject were read at their
  heads: #917 `a95622cc`, #844 `59d11c49`, #845 `f0573718` and #834 `45e818b7`.
