---
id: PL-1286
family: plan
kind: map
title: WK-675 — Frontend: DAG designer, rate table editor, quote sandbox and dislocation views: map plan
status: active                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: 880feb499eddb9e854c525770e95fb19373a2311
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1172, RL-1184, RL-1261, RL-1263, FD-1283, FD-1284, OQ-1285, CR-1212, CR-1243, CR-1247, PL-1213, PL-1237, PL-1254, PL-1267, RS-1269, OQ-550, OQ-1223, OQ-1231]
---

# WK-675 — Frontend: DAG designer, rate table editor, quote sandbox and dislocation views: map plan

First filed 2026-09-29 as working id 9681; `created` re-dated so the id sequence stays non-decreasing (check 31).
Minted as `PL-1286` at #920's merge turn, 2026-09-30, with `python3 scripts/doc-id.py next --ref origin/main` at `6943e664` printing 1285; the open question this PR raises took 1285, because doc-id orders the family `OQ` before `PL` on the same `created` date (working id 9681 before the mint).

> **For agentic workers:** this is a **map plan**. It cuts WK-675 into slices and fixes their
> scope, order, dependencies and gates. It carries no code steps. Each slice gets its own leaf
> plan (`kind: leaf`) before it starts, and the executor works from the leaf plan with
> `subagent-driven-development` or `executing-plans`. **Minted as `PL-1286`**
> at this PR's merge turn (working id 9681).
> **`status: draft` while DP-1 (OQ-550, the decision-maker's) or any other open DP has no
> resolver** (see *Decision points*).
>
> **Revised 2026-09-30 by the planner (planner-maps), on the lead's instructions, while
> `draft`.** The draft was written at `f0c3d197`, and this revision brings it to origin/main
> `880feb49`:
> 1. **Citations refreshed.** #834 is `RS-1269` (its F2 decision is quoted at
>    `RS-1269`:311-353; the salvage ref's `a6f41714` is on origin, `RS-1269`:395-402), which
>    replaces the old head `45e818b7`, whose draft text still asked the lead to push that
>    ref (the two carried RS-1269 lows). #844 is `PL-1267`, #845 is `RL-1264`, and #917 is
>    merged. Every `03` and `07` line locator is re-read.
> 2. **DP-2 is ruled** by `RL-1261` (b), so S7b is required and the Work is 10 slices.
> 3. **Three slices are added (S10–S12)** for the three unowned `03` §5.3 views, by the
>    maintainer's scope decision on `FD-1283` (2026-09-30 05:28:45 BST) and its dated
>    count correction (05:29:29 BST). The Work is 13 slices, 9.75 / 13 / 26 days.
> 4. **Sequencing is re-derived** under `RL-1263`: real cross-Work dependencies only, and
>    the (c) contention table against `PL-1237`, `PL-1254`, `PL-1267`, `PL-1268` and
>    `PL-1278`.
> 5. **DP-4 is ruled (a)** by the maintainer's scope decision of 2026-09-30 05:34:33 BST, which
>    also accepts S12's wait on SL-1260 (the full view) and covers S11's possible run-list
>    route under (a). (a′) is pre-authorised if S2 or S4 splits: 13 slices, up to 15 at
>    that point (before item 6; superseded by item 6's sizing).
> 6. **S13 (Jobs) and S14 (Job detail)** are added by the maintainer's #949 decision (option D,
>    2026-09-30 05:35:06 BST): 15 slices, 11.25 / 15 / 30 days. Settings and System status are
>    placed in P3, with a recommended owner. DP-7, `OQ-1285` (working id 9871 before the
>    mint), is raised for the decision-maker. **Sizing now: 15 slices base (11.25 / 15 / 30
>    days), up to 17 if S2 and S4 both split under (a′).**

## Goal

Build the four rating-engine views WK-675's roadmap row names: the **DAG designer**, the
**rate table editor**, the **quote sandbox with its ladder waterfall and compare**, and the
**dislocation views** (`03` §5.3); and, by the maintainer's scope decision of 2026-09-30
05:28:45 BST on `FD-1283` (option A), the other three §5.3 views: the **Rating version
list**, the **Regression suite** view and the **Deployments** view; and, by the maintainer's
scope decision of 2026-09-30 05:35:06 BST on `FD-1284` (option D), `07` §5.3's **Jobs**
and **Job detail** views. Each is built on routes that a backend Work has delivered
or delivers, and none hand-writes a shape (`CLAUDE.md` §2, §3). The Work is done when every
id in **Scope** has a verdict and every *Acceptance Standard* item below holds.

**Architecture.** This is a map plan, per `docs/process/delivery-process.md` §5 step 2, in the
form of `PL-1237` (WK-674's map plan). The views are Vue 3 SFCs under `frontend/src/views/`,
routed in `frontend/src/router/index.ts`, consuming the generated client in
`frontend/src/api/generated` only. **The design direction for the designer is fixed by spike
F2** (the deputy's decision of 2026-09-28 12:13:47 BST, amended 12:25:21 BST, both by the
maintainer's delegation): Vue Flow is adopted under five conditions. Its research record is
`RS-1269` (merged from #834 as `2f24fcba`), which quotes the decision and its amendment whole
(`RS-1269`:311-353). The spike's code is at the salvage ref `refs/salvage/2026-09-28/spike-f2`,
whose current value `a6f41714` is on origin (`RS-1269`:395-402). The five
conditions are requirements of the designer slices, listed under *Carried obligations*.

**Tech Stack.** Vue 3 (`<script setup lang="ts">` only), Vite, Pinia, Tailwind, ECharts
through `vue-echarts` (present: `frontend/package.json:20,24`). **Two new dependencies:**
`@vue-flow/*` (the designer; absent from `package.json` and `pnpm-lock.yaml` at this tree) and
`@tanstack/vue-table` (the rate table editor's grid; absent). Each lands with its
`docs/skills-map.md` entry and `03` §8 row in the same PR, with its licence (`CLAUDE.md` §10;
F2 condition 4).

**Spec.** The sections the executors read with their leaf plan:

- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md): §5.3 (`03:1041-1058`, the
  views and the *Interaction requirement*), §5.1 (`03:740-854`, the routes each view
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
2. **The nine views' routes are registered and reachable** (FR-25):
   `grep -nE 'rating/:slug/v/:version/(design|tables/:tableSlug|sandbox|dislocation|tests)' frontend/src/router/index.ts`
   prints five lines; `grep -nE 'path: "/(rating|rating/environments|jobs|jobs/:id)",' frontend/src/router/index.ts`
   prints four (the router writes `path: "…"`, double-quoted);
   `frontend/src/router/__tests__/reachability.test.ts` no longer whitelists
   `/models/:slug/backtests/:backtestId`; and `pnpm --dir frontend test` passes the route-graph test
   (`frontend/src/router/__tests__/routeGraph.test.ts`) with each route reachable from `/`.
3. **Each FR in Scope has a test naming it.** A view limb is tested in the frontend, in this
   repo's convention of the id in the test name: for each id,
   `grep -rlE '<id>[^0-9]' frontend/src --include=*.test.ts` prints at least one file
   (`req-coverage.py` does not read the frontend, so this is the predicate). A backend route
   this Work adds (DP-4, DP-6, F-W10-3, and S7b, which `RL-1261` makes this Work's) carries its
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
- **One slice at a time within the Work** (`delivery-process.md` §8, as amended by `RL-1263`:
  at most two build slices at once, from different Works).
- **A new dependency changes `docs/skills-map.md` and the spec's §8 in the same PR** (`CLAUDE.md`
  §10).

## Scope

### The four views, and the requirements each carries

Derived from `03` §5.3 and the §3 FRs, not from recollection (`CLAUDE.md` §13). **`00` FR-24
makes each §5.3 Contents cell prose that binds nothing**, except its seven named exceptions,
one of which is here (the designer's on-node live validation). So each view's obligations are
its FR ids, that exception, the *Interaction requirement* paragraph (`03:1053-1056`), and the
cross-cutting FR-25 and NFR-463.

| View (route, `03` §5.3) | FRs it serves | Backend it consumes, and its state at `880feb49` |
|---|---|---|
| **DAG designer** (`/rating/:slug/v/:version/design`, `03:1046`) | FR-212, FR-213, FR-214, FR-215, FR-219, FR-220, FR-221, FR-222, FR-223, FR-225, FR-226, FR-227, FR-244, FR-246; FR-217 and FR-218 (the mount, with WK-1250); the FR-24 exception. `WF-699` B2–B5 and B8 exercise the step types | Save `POST /api/v1/rating-algorithms` (`rating_algorithms.py:29`) and diff (`:54`) exist (WK-669, closed). **Loading an algorithm has no route** (DP-4). Sub-graph mounting waits on **WK-1250** (`draft`) |
| **Rate table editor** (`/rating/:slug/v/:version/tables/:tableSlug`, `03:1047`) | FR-228, FR-229, FR-230, FR-231, FR-232, FR-233, FR-234, FR-235, FR-1186 | Diff, bulk, import, export and seed exist (WK-670, closed). **The manual-edit route `POST /api/v1/rate-tables/{slug}/versions` (`03:746`) is absent, and its owner is this Work** (F-W10-3). **Reading cells has no route** (DP-4). The exposure-weight column waits on F-W10-2 |
| **Quote sandbox** (`/rating/:slug/v/:version/sandbox`, `03:1048`) | FR-213, FR-247, FR-248, FR-249, FR-251, FR-252, FR-255, FR-256, FR-258, **FR-262's view limb** | `POST /api/v1/score` (`score.py:277`, WK-671) and `POST /api/v1/score/compare` (`score.py:331`, WK-672) exist. OQ-1231 decides whether the compare route changes |
| **Dislocation** (`/rating/:slug/v/:version/dislocation`, `03:1050`) | FR-263, FR-264, FR-265, FR-266 | **Absent.** WK-673 builds `POST` and `GET /api/v1/dislocation-runs` and registers `DislocationRun` for generation (Slice 4 of `PL-1267`, WK-673's map plan, merged as `dd25db94`, `draft`) |

**FR-262** is WK-675's by `RL-1172` item 5 and `CR-1243` (the WK-672 close): the backend limb
is delivered; the view limb is this Work's, and FR-262 is delivered only when both have landed.

### The other three §5.3 views: WK-675's by the maintainer's scope decision

`03` §5.3 lists seven views. WK-675's roadmap row names four. The other three were owned by no
roadmap row, plan, ruling or closure at `f0c3d197`, and the first draft of this plan did not
fold them in:

- **Rating version list** (`/rating`, `03:1045`);
- **Regression suite** (`/rating/:slug/v/:version/tests`, `03:1049`);
- **Deployments** (`/rating/environments`, `03:1051`), which also overlaps `07`'s
  `/admin/environments` view (`07:392`).

The predicate: `grep -rn -E 'rating/environments|/rating\`|Rating version list|Regression suite view|/v/:version/tests|Deployments view|admin/environments' docs --include=*.md --exclude='*wk-675-frontend*'`
(the exclude leaves out this plan, which quotes the pattern) prints five lines at `880feb49`, `03:1045`, `:1049`, `:1051`, `07:392` and `docs/findings/register.md:61`. The
last is a false positive: it matches "/rating\`" inside "`pricing_core/rating\``". WK-674's map
plan (`PL-1237` Task 2, `:774`) adds only the **backend** `GET` for deployment history, not the
view. It was raised as `FD-1283` (#921, auditor-docs).
**The maintainer's scope decision, by delegation, 2026-09-30 05:28:45 BST** ("SCOPE DECISION:
#921 [FD-1283], the three unowned `03` §5.3 rating views go to WK-675 (option A)",
to-lead.md):
all three are **WK-675's**, as three new slices, **S10**, **S11** and **S12** (appended, so the
slice numbers other records cite stay fixed). The Version-list slice's first task is the `03`
§5.1 list-`GET` spec change, a new FR plus the §5.1 row, in the same commit as its code.

### `07` §5.3's platform views: Jobs and Job detail here, the other three placed in P3

`FD-1284` (#949) traced `07` §5.3's platform views, which no Work owned. **The
maintainer's scope decision, by delegation, 2026-09-30 05:35:06 BST** (to-lead.md, "2026-09-30 05:35:06 BST — SCOPE DECISION: #949 [FD-1284], the `07` §5.3 platform views, option D (split by view)"), option D, splits them by view:

- **Jobs** (`/jobs`, `07:390`) and **Job detail** (`/jobs/:id`, `07:391`) are **WK-675's**, as
  **S13** and **S14** (appended). No spec change is needed: every route is declared
  (`07:301-305`) and built (`backend/src/app/api/jobs.py:105-317`, through the `/{job_id}/events` handler). They are bound by FR-402's UI
  limb ("viewable in the UI with the `trace_id`", `07:91`) and FR-401 (cancellation, `07:90`).
  S13 closes `reachability.test.ts`'s waiting exception and corrects its comment
  (`frontend/src/router/__tests__/reachability.test.ts:33` cites FR-24 for "the jobs view is a
  later phase"; the decision records that as a mis-cite).
- **Service accounts** (`07:393`) goes to **WK-676** in P3, by a dated roadmap line (the lead's).
- **Settings** (`07:394`) and **System status** (`07:395`) go to P3, to "a P3 platform Work, or
  WK-1251"; the planner names which. **Recommendation: a new P3 platform-administration Work,
  not WK-1251.** WK-1251 is *Production packaging and supply chain*: it owns FR-432 (container
  images), FR-433 (the Helm chart), FR-438 (signed images with an SBOM), NFR-530, NFR-533 and
  NFR-461 (`roadmap.md`, `### WK-1251`). Those are build- and deploy-time. The two views are runtime administration:
  Settings reads FR-446's effective value and its source, and System status reads FR-443's
  metrics and FR-444's health endpoints. Each needs a spec change first (no status route; no
  cache hit rate emitted). Folding them into WK-1251 would give a packaging Work a UI and two
  spec changes it does not otherwise need. WK-1251 is the fallback if the maintainer prefers no
  new Work, only because it is P3's one platform-shaped Work; the others are governance.
  NFR-527 ("queue depth and wait time are observable"), which System status would display, is
  not WK-1251's: the same roadmap section says NFR-526, NFR-527 and NFR-536 are measured under
  WK-1178 in P2. Creating a Work is the maintainer's scope decision, and the roadmap line is the
  lead's.
- **`/admin/environments` beside `/rating/environments`** is not decided there. It is filed as
  **DP-7 = `OQ-1285`**, owned by WK-675, for the decision-maker.

**A consequence for FR-25:** until S10's rating version list lands, a designer or sandbox route
needs another path from the entry. Until then, each view's slice links to its route from the
existing `RatingVersionView` (`/rating-versions/:id`, `frontend/src/router/index.ts:235`),
which is reachable today. DP-5 decides how a slug-and-version route and that UUID route meet.

## Decision points

Each is the decision-maker's to rule, as an `RL-` (`document-ids.md` §1.6). The options and
recommendations are the planner's proposal, not a ruling.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| **DP-1 = OQ-550** | How does `ChartFigure` relate a row's values to its columns? (`00:552`; re-opened 2026-09-28 as **WK-675's entry decision, due at this map plan**, `RL-1184` E10) | (a) positional rows with the two W6b-9 checks; (b) rows keyed by column name, checked by the type system; (c) a column descriptor, rows staying domain objects | **(b).** It makes misalignment a compile error at the one moment the cost is lowest: 13 call sites today (`git grep -n '<ChartFigure' -- 'frontend/src/*.vue'`), and this Work adds at least four charts. (c) also removes the transcription step, but it makes `ChartFigure` generic, which is the largest change, for a smaller further gain | decision point | **yes**: the plan's freeze, and **Slice 1** (the migration) and every chart slice after it (S6's waterfall, S8's dislocation charts) | decision-maker, by `RL-` |
| **DP-2 = OQ-1231** | Is `StepChange.own_change` derived from the traces (a) or from step-definition equality by `step_id` across the two compiled algorithms (b)? (gated *Before WK-675's map plan* by #917, merged as `90675848`) | as the OQ states them | the OQ's own recommendation was (b) | decision point | was **yes**, for this plan's freeze; now ruled | **`RL-1261`: (b)**, merged as `46188a88`. OQ-1231 is decided in both mirrors (`docs/open-questions.md:136`, `03:1179`). WK-675 builds it in **S7b**, with `RL-1261`'s five named negative tests |
| **DP-3 = OQ-1223** | How does an ordinal categorical input take part in a `monotone` property? | as the OQ states them | the OQ's own recommendation is (a), "when the rate-table editor introduces the order" | decision point | no — resolved before Slice 5's leaf plan goes `active`. Until then, a categorical `monotone` is refused before generation (the OQ's stated interim) | decision-maker, by `RL-` |
| **DP-4** | The views need read routes **declared nowhere and built nowhere**: an algorithm by `{slug}@{version}` (the designer's load), and a rate table's cells and a version's table list (the editor). Who adds them? | (a) **this Work**: each route is spec-changed first by the decision-maker and built in the slice whose view consumes it, as F-W10-3 already makes this Work own `POST /rate-tables/{slug}/versions`; (b) a WK-1178 backend slice before WK-675; (c) leave the views to compose reads from existing routes | **(a).** The consuming view is the only place the route's shape is known; F-W10-3 is the precedent; (c) is impossible for the designer, since no route returns an algorithm's graph | scope | ruled | **(a), by the maintainer's scope decision, by delegation** (to-lead.md, "2026-09-30 05:34:33 BST — SCOPE DECISION: #920 DP-4, option (a); the S12 order corrected; the S11 run-list route covered"). Each missing read route gets a spec change first (a new FR plus its `03` §5.1 row) and is built in the WK-675 slice that consumes it: the algorithm-by-`{slug}@{version}` load in **S2**, the rate-table cells and a version's table list in **S4**. **(a′) is pre-authorised as a fallback:** if S2's or S4's leaf plan must split, the split, or one read-routes slice before S2, needs no further scope call; the planner records it at that leaf plan's ACK |
| **DP-5** | §5.3 routes address a version as `:slug/v/:version`, but the backend reads a Rating Version only by UUID (`GET /rating-versions/{id}`, `models.py:1139`), a Phase 1b route in no §5.1 | (a) add `{slug}@{version}` read routes, the form `03` §5.1 already uses for algorithms and tables; (b) change the §5.3 and `00` §5.6 routes to `/rating-versions/:id/...` | **(a).** It matches every other versioned route in `03` §5.1 and keeps `00` §5.6's four canonical routes unchanged | decision point | no — resolved before Slice 2's leaf plan goes `active`. Until then, views are linked from `/rating-versions/:id` | decision-maker, by `RL-` |
| **DP-6** | The designer's **on-node live validation** is an FR-24 exception, binding until discharged at this view's slice plan (`00:228`). What discharges it, and how does the view validate before save? | (a) raise it as a numbered `03` FR, served by a **validate-only route** that runs the server's own checks (spec change: the FR plus the route); (b) raise the FR, and re-implement the cycle, reference and type checks in the frontend; (c) declare the cell exhaustive and validate on save only | **(a).** (b) defines the validation rules twice, the divergence `CLAUDE.md` §2 forbids; (c) fails the *Interaction requirement* that an invalid graph be "visibly invalid before save" | decision point | no — resolved before Slice 3's leaf plan goes `active`. Until then, the FR-24 exception stays binding and undischarged | decision-maker, by `RL-` |
| **DP-7 = OQ-1285** | Is `03` §5.3's Deployments view (`/rating/environments`, `03:1051`) a duplicate of `07` §5.3's Environments view (`/admin/environments`, `07:392`)? Both name the live deployments and the shadow configuration, and `00` §5.6 lists only `/admin/*` for environments (`00:413`) | (a) one view at the canonical `/admin/environments`; (b) two views split by concern: deployment actions under `/rating`, environment administration under `/admin`, with a `00` §5.6 row added; (c) both as written | **(a)**, as `docs/open-questions.md` records it: it agrees with `00` §5.6 as written, and shadow configuration is an administration setting (`PL-1237` Task 6). (c) defines one control twice | decision point | no — resolved before S12's leaf plan goes `active` | decision-maker, by `RL-` (raised on the maintainer's #949 decision) |

**The freeze.** DP-2 is ruled (`RL-1261`) and DP-4 is ruled (a) (the maintainer, 2026-09-30
05:34:33 BST). **DP-1 is open, and it is the decision-maker's**: OQ-550, prepared in #936
(`dm-prep-b-oq550`, open, "PREPARED, NOT RULED"). This plan stays `draft` until DP-1 and every
other open DP has a resolver (DP-3, DP-5, DP-6, DP-7: each the decision-maker's). DP-1 decides Slice
1's content; DP-2's ruling makes the compare work two slices, S7b then S7. DP-3, DP-5 and DP-6
each also block only their slice's leaf plan, which does not go `active` until its DP is
ruled.

## Carried obligations

**Spike F2's five conditions** (the deputy's decision of 2026-09-28 12:13:47 BST and its
12:25:21 BST amendment; quoted whole in `RS-1269`:311-353), each a requirement of the designer slices:

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
  **WK-673**, and the maintainer accepted that. **Decided by the lead, 2026-09-29 19:04Z:**
  WK-673's plan takes F-W10-2 at its rework. It did: `PL-1267` carries it as **Slice 7**
  (merged as `dd25db94`; Slice 7 waits on its DP-5). The editor's exposure-weight column
  (Slice 5) **depends on `PL-1267` Slice 7** and ships with the weights, not as "weights
  unavailable".

## Tasks

**Each row is one task, cut as one slice**, and gets its own leaf plan (`kind: leaf`) before
it starts; the leaf plan carries the files, interfaces and test steps. One slice at a time
(`delivery-process.md` §8). Every slice's leaf plan names its FRs, its negative tests, and its
FR-25 and NFR-463 obligations.

| Slice | Content | Depends on | Size band (days: likely / worst) |
|---|---|---|---|
| **S1 — Chart foundation** | Apply DP-1's ruling to `ChartFigure` and migrate its 13 call sites; F39's socket diagnosis | DP-1 | 1 / 2 |
| **S2 — Designer I: canvas, inspector, load, save** | F2 conditions 1–5; `RatingAlgorithm` and the load route (DP-4, DP-5) generated; the Vue Flow canvas with typed nodes (FR-212, FR-215), the node inspector per step type (FR-213 inputs, FR-214 outputs, FR-215, FR-220 `table`'s pinned table and banding reference, FR-221 `lookup`'s as-at date source, FR-225 `constraint`'s `reason_code`, FR-226 `output`'s explicit rounding, and `expression` steps, taken as text (FR-244). A function the engine does not support surfaces through DP-6's validate route (S3), and S2 offers **no function picker** unless a later leaf plan finds a generated source for the engine's vocabulary, since a hard-coded list would define that vocabulary twice (`CLAUDE.md` §2; FR-276)); on each `model_call` step, the **Rating Version's** model reference mode shown read-only, not chosen per step (FR-222 records it on the version, and FR-223 requires every step's `mode` to equal it, refusing a mismatch with `MODEL_REFERENCE_MODE_INCONSISTENT`), the keyboard node navigator, save through `POST /rating-algorithms`; FR-25 link from `RatingVersionView` | DP-4, DP-5 | 1 / 2 |
| **S3 — Designer II: live validation and diff** | DP-6's discharge: the numbered FR and the validate route; errors on the node before save (FR-212, FR-223, FR-227), including `expression` steps, whose grammar (FR-244) and closed inputs (FR-246) the validate route checks; the structural diff overlay (FR-219) | S2, DP-6 | 1 / 2 |
| **S4 — Editor I: grid and manual edit** | `@tanstack/vue-table` (new dependency); the cell and table-list read routes (DP-4); the typed grid (FR-228), paged through the cell read route for either storage, and above FR-232's threshold (default 250 000 cells, `storage: parquet`) the grid still pages with no Job, and the slice states that bound under test (FR-232); the manual-edit route (F-W10-3; FR-229's required change note, FR-231's confirmation diff, FR-234's validation errors shown on the cell); no approval state on a Rate Table Version (FR-1186); inline decimal editing (FR-10, FR-21) | DP-4 | 1 / 2 |
| **S5 — Editor II: diff shading, bulk, import, export** | Diff-vs-previous and diff-vs-seed shading (FR-230, FR-231), handling the diff route's **202 with a Job** when either version is `storage: parquet` (FR-232, `03:749`): the view polls the Job and renders the same artifact; the exposure-weight column (F-W10-2); bulk-operation dialog (FR-233); CSV import confirmation and export (FR-235); DP-3's order; F-W10-1 | S4, DP-3; **`PL-1267` Slice 7** (WK-673's F-W10-2 slice) | 1 / 2 |
| **S6 — Sandbox: form, waterfall, trace** | The quote form from the input contract (FR-213), scoring the version in view through an explicit `rating_version_ref` (FR-251, the what-if path that makes FR-262's "any accessible Rating Version" work); the ladder waterfall (FR-247, FR-248) as a chart with its table, including the optional `instalment_loading` rung when present (FR-252) and the per-peril risk-premium components among the outputs (FR-249); a **declined** quote rendered as a successful result with `outcome: declined`, its plural `decline_reasons` and the ladder still shown (FR-256); each typed per-quote error rendered distinctly: contract violation, reference miss, table miss, constraint decline, model failure (FR-255); the trace timeline (FR-258); the waterfall **one click from any traced quote** (`03:1055-1056`, FR-25) | S1 | 1 / 2 |
| **S7 — Sandbox compare** | FR-262's view limb over `POST /score/compare`; the `own_change` rendering rule | S6; S7b | 1 / 2 |
| **S7b — Compare backend** | **`RL-1261` (DP-2 = (b)):** `diff_traces` takes both algorithms and derives `own_change` from step-definition equality by `step_id`, agreeing with `diff_algorithms` except for `note`; the route passes each side's `CompiledBundle.algorithm`; `StepChange`'s docstring and field description (`packages/model-schema/src/model_schema/scoring.py:196-214`) and the generated contract change with it; `RL-1261`'s five negative tests, each shown red on broken input; before S7 | `RL-1261` | 1 / 2 |
| **S8 — Dislocation views** | The change histogram (FR-263), segment grid (FR-264), attribution waterfall (FR-266), largest movers with drill-down to individual quotes (FR-263; the §5.3 cell says "traces", and FR-263's word governs), the run cited as a persisted artifact by its id (FR-265), each chart with its table | **`PL-1267` Slice 4** (WK-673's routes and generated `DislocationRun`); S1 | 1 / 2 |
| **S9 — Designer III: sub-graph mounting** | Mounting a pinned sub-graph in the designer (FR-217, FR-218's authoring view) | **WK-1250** (`PL-1254`; inlining and the mount declaration); S3 | 1 / 2 |
| **S10 — Rating version list** (`/rating`, `03:1045`; `FD-1283`, option A) | **First task, spec first (`CLAUDE.md` §0):** a new `03` FR and the §5.1 row for a `GET` list route over Rating Versions, in the same commit as its code. Then the view: versions by status, **live-in-environment badges**, effective dates (`03:1045`); each row links to the version's `:slug/v/:version` routes, which **removes the interim FR-25 path** through `RatingVersionView` | S6 (order); DP-5 (the rows' route form); **WK-674 Slice 2, SL-1256** (a live badge needs the Deployment record: nothing is `live` without it, `PL-1267` premise j) | 1 / 2 |
| **S11 — Regression suite view** (`/rating/:slug/v/:version/tests`, `03:1049`; `FD-1283`, option A) | Golden quotes with pass/fail and actual-vs-expected, property assertion results with counterexamples (FR-260, FR-261, FR-1221), over WK-672's routes (`03:756-763`). **Both run reads need a `run_id`, and no route lists a version's runs**: the leaf plan establishes whether the version's evidence gives the run id; **if not, the run-list read route is added under DP-4 (a), spec first (a new FR plus its §5.1 row), in S11**, with no new scope call (the maintainer's 05:34:33 entry) | S10 (order); DP-5 | 1 / 2 |
| **S12 — Deployments view** (`/rating/environments`, `03:1051`; `FD-1283`, option A) | Per-environment live version, deployment history, rollback control, shadow configuration (`03:1051`; FR-267, FR-269, FR-271). The overlap with `07`'s `/admin/environments` (`07:392`) is resolved in its leaf plan | **WK-674's last slice, SL-1260**, and so SL-1256 (history `GET`, live version) and SL-1259 (rollback, FR-269) before it; shadow configuration is FR-271, SL-1260. **The full view; no partial Deployments view ships** (the maintainer's dated correction to the 05:28:45 order, in the 05:34:33 entry); S11 (order) | 1 / 2 |
| **S13 — Jobs** (`/jobs`, `07:390`; `FD-1284`, option D) | The filterable list with kind, status, progress bars, submitter and duration, live over the SSE stream (`GET /api/v1/jobs` and `/jobs/{id}/events`, `07:301, 305`); FR-25 link from the entry; **removes the `reachability.test.ts` exception** for `/models/:slug/backtests/:backtestId` (reachable through a Job's result link) and **corrects its FR-24 comment** (`:33`). New functions in `frontend/src/api/jobs.ts`; no backend change | S4 (order: before S5, the first slice that renders a Job) | 1 / 2 |
| **S14 — Job detail** (`/jobs/:id`, `07:391`; `FD-1284`, option D) | Parameters, progress stages, logs with `trace_id` (FR-402's UI limb, `07:91`; `GET /jobs/{id}/logs`), the result link, the cancel action (FR-401, `POST /jobs/{id}/cancel`), error detail. The logs render nothing FR-402 excludes (no secrets, no full quote inputs) | S13 | 1 / 2 |

**The band, re-derived from this cut.** The frontend bands are 0.75 / 1 / 2 days per slice
(best / likely / worst), from the §5a sizing at
`~/gi-pricing-plan.local/scratch/planner-wk674-2/p2-sizing.md` (sha256
`ee99405376e1eb2d107d622488d2d4ad2687d822e8893045a08425df073664af`), relayed to the maintainer
as inputs, not a plan change. That file gave WK-675 a provisional 6–10 slices and 5 / 9 / 22
days.

| DP-2 ruling | Slices | Best (×0.75) | Likely (×1) | Worst (×2) |
|---|---|---|---|---|
| ~~(a), the trace rule stays~~ | ~~9~~ | ~~6.75~~ | ~~9~~ | ~~18~~ |
| **(b), definition equality — ruled, `RL-1261`** | 10 (with S7b) | 7.5 | 10 | 20 |
| **(b), plus #921's three views (S10–S12)** | 13 | 9.75 | 13 | 26 |
| **plus #949's two views (S13, S14)** | **15** | **11.25** | **15** | **30** |

*(Dated 2026-09-30.) The maintainer's scope decision (to-lead.md, "2026-09-30 05:28:45 BST —
SCOPE DECISION: #921 …") first sized the absorbed Work as "9 to 12, sized 9 / 12 / 24
days". That count predates counting S7b, which `RL-1261` requires. The maintainer's dated
correction (to-lead.md, "2026-09-30 05:29:29 BST — DATED CORRECTION to "SCOPE DECISION: #921"
(05:28:45): the slice count only") reads it as **from 10 to 13 slices**, at this plan's
per-slice band: **9.75 / 13 / 26 days** (13 × 0.75 / 1 / 2). Under DP-4 (a) and before #949, the
Work was 13 slices, up to 15 if S2 and S4 each split under the pre-authorised (a′) (the
maintainer's 05:34:33 BST entry asks the planner to state these figures).
**Current sizing: 15 slices base (11.25 / 15 / 30 days), up to 17 if S2 and S4 both split under
(a′).** With S13 and S14 (the maintainer's 05:35:06 BST entry on #949, option D), the Work is **15
slices: 11.25 / 15 / 30 days**. It is **16 slices (12 / 16 / 32 days)** if one of S2 or S4
splits, or one read-routes slice is added, under (a′); and **17 slices (12.75 / 17 / 34 days)**
if both split. The entry's "16 under (a′)" is the one-split case.*

**S2 and S4 carry more than a typical slice:** S2 holds spike F2's five conditions as well as
the canvas, and S4 a new dependency as well as two backend routes. Their leaf plans confirm the
cut or split them, and the band moves with any split.

## Sequencing

*(Re-derived 2026-09-30 at `880feb49`, under `RL-1263` and the maintainer's 2026-09-29
22:46:27 BST item 5, which relaxed `CR-1212` Proposal 2's Work order to real dependencies.)*

- **The Work's place in P2.** `CR-1212`'s "WK-674, then WK-673, then WK-675" is lifted as
  bare sequencing. WK-675 waits on another Work only where a slice needs a named slice or
  artifact:

  | WK-675 slice | Needs | Why |
  |---|---|---|
  | S5 | `PL-1267` Slice 7 (WK-673, F-W10-2) | the exposure-weight column |
  | S8 | `PL-1267` Slice 4 (WK-673) | the `dislocation-runs` routes and generated `DislocationRun` |
  | S9 | WK-1250 (`PL-1254`; its Slice 1 is `PL-1278`) | the sub-graph artifact, inlining and the mount |
  | S10 | WK-674 Slice 2, SL-1256 | a live-in-environment badge needs a Deployment |
  | S12 | WK-674 Slices 2, 5 and 6: SL-1256, SL-1259, SL-1260 | history and live version; rollback (FR-269); shadow configuration (FR-271) |

  S1–S4, S6, S7b, S7, S11, S13 and S14 need nothing from another Work: the job routes are
  declared and built.
- **Inside the Work:** S1 → S2 → S3 → S4 → S13 → S14 → S5 → S6 → S7b → S7 → S10 → S11 → S8 → S9 → S12.
  - S1 comes first because DP-1's ruling changes every chart after it.
  - **S13 and S14 come before S5**, the first slice that renders a Job (the diff route's 202,
    FR-232). After them, S5, S8 and S11 link a Job to its detail page instead of each building
    its own progress display, and the exit demo's long regression run has visible progress.
    No dependency forces this. They need nothing from another Work or from S1–S4, so the lead
    may dispatch them earlier.
  - S10 and S11 follow S6 and precede S8 and S9, as the maintainer's 05:28:45 entry orders.
    Nothing forces a change. S10 could run earlier, since it needs only SL-1256, DP-5 and
    its own spec change, and running it earlier would end the interim FR-25 path through
    `RatingVersionView` sooner. That is a preference, not a dependency, and the order stands.
  - S8 and S9 wait on WK-673's Slice 4 and WK-1250. If either lands earlier, S8 or S9 may
    move up; that is the lead's call at dispatch, one slice at a time.
  - **S12 is last, and it waits on WK-674's last slice.** The entry says "after WK-674's
    history GET" (SL-1256). The view's `03:1051` row also needs rollback control (SL-1259)
    and shadow configuration (SL-1260), so S12 starts after SL-1260 merges. **Accepted by the
    maintainer** as a dated correction to the 05:28:45 order (the 05:34:33 BST entry): S12
    waits on SL-1260, and it is the full view; no partial Deployments view ships.

**Contention under `RL-1263` (c)** (two concurrent build slices may not change the same
existing function, class, method, spec section or policy table; the registry files are exempt
for append-only edits). Read at `880feb49` against the merged plans. A pair marked
**serialise** does not run concurrently; the second merges `origin/main` first.

| WK-675 slice | Shared path | Other Work's slice | Kind |
|---|---|---|---|
| S2 (DP-4 load, DP-5), S3 (DP-6 validate route), S4 (DP-4 reads, the manual-edit row), S10 (list `GET`), S11 (if a runs-list route is needed) | `03` §5.1 | WK-674 Slices 2 and 6 (`PL-1237`:773-774, :977-979); WK-1250 Slice 1 (`PL-1278`:381; `PL-1254`:266); WK-673 Slices 4 and 7 (`PL-1267`:526-527, :589) | **serialise** |
| S3 (DP-6's new FR) | `03` §3.1 or §3.5, wherever the FR is placed | WK-1250 Slice 3 (FR-218, §3.1, `PL-1254`:317-318); WK-673 Slice 5 (§3.1 as needed, `PL-1267`:423); WK-690 Slice 1 (FR-244, §3.5, `PL-1268`:424-428) | **serialise** with whichever shares the section |
| S10 (its new FR) | `03` §3.4 (Rating versions) | WK-674 Slice 6 (the FR-241 cross-reference in §3.4, `PL-1237`:976) | **serialise** |
| S7b | `03` §5.2 (`diff_traces`'s signature, `03:903`) | WK-1250 Slice 2 (`PL-1254`:292-293); WK-673 Slice 1 (`PL-1267`:466) | **serialise** |
| S7b | `03` §4.10 | none | exclusive |
| any slice adding a `03` §4 contract (none planned) | a new §4 subsection (the §4.11 numbering) | WK-674 Slices 2 and 6 (`PL-1237`:772, :977); WK-1250 Slice 1's §4.11 (`PL-1278`:381) | **serialise**, if a leaf plan adds one |
| S2 (making `RatingAlgorithm` generated) | `scripts/generate-contracts.py` `GENERATED_SHAPES`; `backend/tests/test_contracts.py` `ONE_SIDED_SLUGS` | WK-1250 Slice 1 (`PL-1278`:424-427); WK-673 Slices 1 and 4 (`PL-1267`:471, :529-531) | **serialise**, if S2 registers a slug; exempt if only `generated.json` changes |
| S7b | `trace_diff.py` `diff_traces`; `backend/src/app/api/score.py` `score_compare`; `model_schema/scoring.py` `StepChange` | WK-674 Slices 2 and 5 edit `/score`'s path, not `score_compare` (`PL-1237`:785, :919); WK-1250 Slice 2 may change `TraceStep`, a different class | no conflict. S7b does not edit `pricing_core/rating/score.py`, `TraceStep` or `compile_bundle` (`RL-1261`:113-118), so `PL-1267`'s file table over-lists it. After WK-1250 Slice 2, S7b's `step_id` matching must handle inlined, namespaced step ids |
| S4 | `backend/src/app/api/rate_tables.py`, `backend/src/app/platform/rate_tables.py` | WK-673 Slice 7 edits `rate_table_diff` and `diff` (`PL-1267`:591-594) | new functions: no conflict, unless S4 edits a shared helper |
| S2, S3 | `backend/src/app/api/rating_algorithms.py` | WK-1250 Slice 1 copies its pattern only (`PL-1278`:30-33) | no conflict |
| S1 | `ChartFigure` and its call sites | WK-690 Slice 5 adds a caller (`PL-1268`:541-547) | ordered: whichever lands second migrates or uses the new API |
| every view slice | `frontend/src/router/index.ts` `routes` | WK-690 Slice 5 extends the existing `/objectives` view, and would edit `routes` only if it adds a child route | within WK-675, serial anyway; against WK-690 Slice 5, **serialise** if its leaf plan adds a route |
| any | `permissions.py`, `approvals.py` | WK-690 Slice 3; WK-674 Slice 2; WK-673 Slice 5 | WK-675 edits neither: no conflict |
| S13, S14 | `frontend/src/api/jobs.ts` (`getJob` and the poll helper) | WK-690 Slice 5, if its certification view uses the poll helper (`02` FR-146's 202) | new functions: no conflict; **serialise** only if either edits the poll helper |
| S13, S14 | `frontend/src/router/index.ts` `routes` (`/jobs`, `/jobs/:id`) and `reachability.test.ts` | none: WK-675 is the one router owner | exclusive |
| any | `db/models.py`, `main.py`, `backend/migrations/versions/`, the generated files | several | exempt (append-only) |

## Status

`draft` at `880feb49`. DP-2 is ruled (`RL-1261`) and DP-4 is ruled (a) (the maintainer,
2026-09-30 05:34:33 BST). It stays `draft` while DP-1 (OQ-550, the decision-maker's, #936) or
any other open DP has no resolver, and goes `active` when they do and the maintainer's WK-675
map acceptance line is given.
The maintainer then activates WK-675 on it.

## Self-review

- **Spec coverage, by enumeration, not by the scope list itself.** `03` §3 was read in full,
  each id against the four views (the first draft's scope): FR-212 to FR-276, FR-1186 and FR-1221 (the section's own
  ids, `03:75-228`).
  - **Placed**, each in the slice its row names:
    - S2: FR-214, FR-220, FR-221, FR-222, FR-223, FR-225, FR-226, and the `expression`
      authoring of FR-244, as text;
    - S3: FR-244 and FR-246's validation;
    - S4 and S5: FR-232;
    - S6: FR-249, FR-251, FR-252, FR-255 and FR-256;
    - the rest as *Scope*'s table lists them.
  - **No limb in these four views, so not in scope:**
    - FR-216 (evaluation order) and FR-245 (`Decimal` arithmetic in the engine; the views
      follow FR-10 and FR-21);
    - FR-224 and FR-257 (approval gates; the approvals view is `06`'s);
    - FR-236 (rateable or diagnostic);
    - FR-237 to FR-243 (the Rating Version, its lifecycle and the bundle: backend; the
      version-list view is now S10, which reads them);
    - FR-250 (scoring against the version live in an environment: WK-671's route, while the
      sandbox scores an explicit version, FR-251);
    - FR-253 and FR-254 (batch scoring: no view here);
    - FR-259 (production trace sampling: backend; the sandbox's trace is FR-258's, on
      request);
    - FR-260, FR-261 and FR-1221: their view limb is now **S11**;
    - FR-267 to FR-272: WK-674's backend; their view limb (FR-267, FR-269, FR-271) is now
      **S12**;
    - FR-273 to FR-276 (the engine boundary and compile-time checks, including FR-276's check
      of the expression vocabulary against the engine in use: backend).
- **Placeholders:** none. Every open choice is a numbered decision point with options and a
  recommendation.
- **Literals** were read at `f0c3d197`: the routes (`03:744-769`), the router
  (`router/index.ts:235`), the dependencies (`package.json:20,24`), and the generated
  components (`RatingAlgorithm` absent). Open PRs that rule on this subject were read at their
  heads: #917 `a95622cc`, #844 `59d11c49`, #845 `f0573718` and #834 `45e818b7`. **Refreshed at
  `880feb49` (2026-09-30):** all four have merged — #917 as `90675848`, #844 as `PL-1267`
  (`dd25db94`), #845 as `RL-1264` (`843c3495`), #834 as `RS-1269` (`2f24fcba`) — and the
  locators above are re-read there.
