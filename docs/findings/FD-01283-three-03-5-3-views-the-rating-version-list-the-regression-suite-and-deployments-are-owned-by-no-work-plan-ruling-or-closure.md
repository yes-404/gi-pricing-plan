---
id: FD-1283
family: finding
title: Three 03 §5.3 views (the rating version list, the regression suite and Deployments) are owned by no Work, plan, ruling or closure
status: active
created: 2026-09-30
owner: auditor
tree: 880feb499eddb9e854c525770e95fb19373a2311
corrected_by: []
relates: [WK-675, WK-674, WK-673, WK-1250, RL-1263]
---

# FD-1283 — Three 03 §5.3 views have no owner

*First filed 2026-09-29 as a working-id draft on #921; `created:` is the date the id is to be minted against (2026-09-30), so that `created` is non-decreasing with the number (check 31).*

## Finding

`03-rating-engine.md` §5.3 lists seven frontend views (`03:1045` to `:1051`). WK-675's roadmap
row (`docs/roadmap.md:820`) names four: the DAG designer, the rate table editor, the quote
sandbox and the dislocation views. **The other three have no owner:** the rating version list
(`/rating`, `03:1045`), the regression suite (`/rating/:slug/v/:version/tests`, `03:1049`) and
Deployments (`/rating/environments`, `03:1051`, which overlaps `07:392`'s `/admin/environments`).
**Proposed by the auditor; the disposition is the lead's.** FD-1283 was filed as working id 9692 and minted at #921's mint turn (2026-09-30). First read at `origin/main` `f0c3d197`, 2026-09-29; **re-verified at `880feb49`,
2026-09-30** (evidence items 1 and 7; the finding stands, its line numbers moved by one to six).

## Evidence

1. **The predicate, run verbatim.** It is the one the WK-675 map plan (PR #920, working id 9681) states, run from a
   detached worktree at `f0c3d197`:
   `grep -rn -E 'rating/environments|/rating\`|Rating version list|Regression suite view|/v/:version/tests|Deployments view|admin/environments' docs --include=*.md`
   prints **five** lines at `f0c3d197`, and **five again at `880feb49`** once this FD and its register row
   are excluded: `07-platform.md:392`, `03-rating-engine.md:1045`, `:1049`, `:1051`, and
   `docs/findings/register.md:61` (F-W9-3). (At `f0c3d197` these were `07:386`, `03:1044`, `:1048`, `:1050`.) The fifth is a false positive: the
   `/rating\`` alternative matches `pricing_core/rating\`` in prose about `compile.py`. **None of
   the five assigns the frontend limb of any of the three views to a Work.**
2. **A wider sweep** over `docs/roadmap.md`, `docs/plans`, `docs/rulings`, `docs/closures`,
   `docs/ledgers`, `docs/workflows`, `docs/process` and `docs/open-questions.md`, for
   `version list`, `regression.suite (view|screen|UI|page)`, `deployments? (view|screen|page|UI)`,
   `environments? (view|page|screen)`, `/admin/environments` and `rollback control` (the command
   is `grep -rn -i -E` with that alternation over those paths), finds no line that assigns a view.
3. **One near miss, stated so that it is not read as ownership.** `PL-1237` (WK-674's map plan),
   Task 2, adds a `GET` for deployment history "which FR-382 and the view at `03:847`
   (`03:1051` at `880feb49`; `03:1050` at `9cd179cb`) need and `03` §5.1 lacks". That is the **backend** limb the
   Deployments view consumes. WK-674 owns that route; nothing owns the view.
4. **`00` §5.6's canonical route table (`00:404` to `:407`) lists four rating views** (designer,
   editor, sandbox, dislocation) and none of the three. FR-25 (a registered route is reachable from
   the entry by following links) therefore has no anchor for them.
5. **The one route that exists is a different path.** `frontend/src/router/index.ts:235` registers
   `/rating-versions/:id` (`RatingVersionView`, `:238`), the Phase 1b demo detail view. It is not
   `/rating`, and it is not the list view. It bears on option (a) below and on FR-25: it is the only
   rating-version entry today.
6. **Why it matters now.** Each of the three is a row of `03` §5.3 with a route, and FR-25 requires
   every registered route to be reachable from the entry by links. `WF-699` D1 to D5 (regression
   runs) and `WF-701` A1, B1, C1 and H3 (deploy, shadow, rollback) exercise the regression and
   deployment steps whose UIs two of these views are. (`WF-701` A5 is the quote sandbox and
   `WF-699` E5 the approver's inline review; neither is one of the three.)

7. **Re-check at `880feb49` (2026-09-30): nothing has picked any of the three up.**
   - **`PL-1267`** (WK-673, merged) — its Not-in-scope paragraph gives the Dislocation view to
     WK-675 and says "this Work ships no frontend". The only `version list` hit is a negative test
     that a subset bundle is never listed (`RL-1264`), not a view.
   - **`PL-1268`** (WK-690) — owns `02`'s Custom objective library authoring view only.
   - **`PL-1278`** (WK-1250 Slice 1) — a backend artifact plan; no view.
   - **`PL-1237`** (WK-674) — unchanged: the backend `GET` for deployment history only (item 3).
   - **#920** (WK-675's map plan, the #920 plan (working id 9681), still `draft` and the PR still open, branch
     `wk675-map-plan`) — its "Not WK-675's" section (lines 137 to 154 of the plan) **declines**
     the three views, and its Scope list marks FR-237 to FR-243, FR-260/261/1221 and FR-267 to
     FR-272 "unowned" (lines 284 to 291). It routes the owning decision to the lead and cites this
     finding as working id 9692.
   - **`docs/roadmap.md`** — WK-675's row (`:820`) is unchanged, and no row names `/rating`,
     `/rating/:slug/v/:version/tests` or `/rating/environments`. The wider sweep of item 2 was
     re-run over `docs/roadmap.md docs/plans docs/rulings docs/closures docs/ledgers
     docs/workflows docs/process docs/open-questions.md docs/research` with the same alternation
     and finds no view assignment.
   - **`RL-1261`** (OQ-1231, own_change) and **`RL-1263`** (parallel start) are both merged and
     neither mentions the three views. `RL-1263` matters for the Options below.
8. **What each view needs from the backend, read at `880feb49`.** These decide the weighing.
   - **Rating version list:** `03` §5.1 has `POST /rating-versions` and `POST …/{id}/compile`
     (`03:753`, `:754`) and **no `GET` list route**; the by-id read is a Phase 1b route in no §5.1
     row (the #920 plan (working id 9681) DP-5). The view has **no backend** today, and the spec does not declare one.
   - **Regression suite:** the backend exists, `GET /rating-versions/{id}/regression-runs/{run_id}`
     and `…/cases` (`03:762`, `:763`) and `GET /regression-suites/{slug}@{version}` (`03:757`),
     built by WK-672. The view has its backend; only the frontend limb is unowned.
   - **Deployments:** WK-674 builds `POST` deploy, rollback and shadow (`03:766` to `:768`) and,
     per `PL-1237` Task 2, the history `GET`. `07`'s `/admin/environments` (`07:392`) is a
     second view over the same data; neither view has an owner, and the router has no
     `environments` route (`grep -n environments frontend/src/router/index.ts` prints nothing).
   - **Adjacent, not this finding's scope:** `07` §5.3's other rows (`/jobs`, `/jobs/:id`,
     `/admin/service-accounts`, `/admin/settings`, `07:388` to `:394`) returned no hit in
     `docs/roadmap.md` for `service-accounts`, `/admin/settings`, `jobs view`, `job detail` or `/jobs`.
     I did not establish their owner (a router or `WK-664` reading was not done); the lead may want
     the same predicate run over them.

## Options — for the maintainer's placement call

**The auditor prepares this; the auditor decides nothing.** Placement is a scope question, the
maintainer's (`document-ids.md` §1.7). It gates WK-675's map plan, and the scope freeze is
Sat 2026-10-03 (`docs/roadmap.md`, the P2 freeze block). Candidates, per view:

| Candidate | Spec fit (`03` §5.3, Contents cell) | File contention (`RL-1263` option (c)) | Scope freeze |
|---|---|---|---|
| **A. Fold into WK-675** (a `WK-` row scope change) | Best for all three: it is `03` §5.3's frontend Work, and its routes share the `/rating` tree, the router and the generated client with the four views | WK-675 is one slice at a time (`delivery-process.md` §8) and its frontend slices are serial with each other, so no contention inside it. Its view slices are expected to add routes to `frontend/src/router/index.ts` (an inference from the #920 plan (working id 9681), not stated there), a shared path outside the registry list, so it would serialise against any other frontend Work | Adds no new Work, so the freeze is met; but adds slices to a Work already at 9 slices, 9 / 18 days likely / worst (the #920 plan (working id 9681)) |
| **B. New Work** (P2) | Same fit as A for the views, and cleaner ownership | A second frontend Work editing `router/index.ts` serialises against WK-675, and cannot start until a gate slot is free (`RL-1263`) | **A new Work after Sat 2026-10-03 is refused by the freeze**; before it, a new `WK-` row and map plan are needed, with CR-1212's ordering left unchanged |
| **C. WK-673 (dislocation)** | Poor: `PL-1267` says it ships no frontend | n/a | n/a |
| **D. WK-674 (deployment)** | Fair for Deployments only: the same Work builds its history `GET`; `PL-1237` does not build a view | Its slices are backend-heavy, and it edits `main.py` (a registry file, exempt) and the `Environment` contract | Adds frontend to a backend Work already carrying the F1 obligation and NFR limbs |
| **E. Out of P2, with a dated line** | Acceptable only if the exit demo does not need the view | none | Met by definition; but `WF-699` D1 to D5 and `WF-701` A1, B1, C1 and H3 name the regression and deployment steps, and G2 is "from one command to a served page, in Phase 1b's form" (`docs/roadmap.md`, G2), which is a demo run, not a UI walk-through |

**Per view.**

1. **Rating version list (`/rating`).** Candidates: A, B, E. It needs a **new backend list route**
   that `03` §5.1 does not declare (item 8), so placing it anywhere is a spec change first
   (`CLAUDE.md` §0). It is also the entry point for FR-25: without it the designer, editor and
   sandbox have no path from the entry (the #920 plan (working id 9681), "A consequence for FR-25").
2. **Regression suite (`/rating/:slug/v/:version/tests`).** Candidates: A, B, E. Backend is built,
   so this is the cheapest of the three: one page over three existing `GET`s (item 8).
3. **Deployments (`/rating/environments`, with `07:392`'s `/admin/environments`).** Candidates: A, B,
   D, E. Two spec rows describe one screen over one dataset; the maintainer should also say whether
   both routes stand (an `OQ-` or spec change, not this finding).

**Recommendation (the auditor's, not a decision).**
- **Rating version list and Regression suite: option A (WK-675)**, as two further slices after S6
  and before S8/S9 in the #920 plan's (working id 9681) order, so no slice waits on another Work. Rationale: they share
  the `/rating/:slug` route tree, the generated client and the router; a second frontend Work would
  serialise against WK-675 on `router/index.ts` under `RL-1263`, buying no parallelism; and the
  list view is the FR-25 entry the other four need. **Precondition:** a spec change first, for the
  missing `GET` list route (item 8).
- **Deployments: option A too, but last in WK-675's order, or E if the maintainer prefers to hold
  WK-675's budget.** Rationale: its backend is WK-674's, which lands first (`CR-1212` Proposal 2's
  order, WK-674 then WK-673 then WK-675), so it has no wait; it is the view G2's deploy step most
  needs, so E carries the highest risk of the three. Splitting it out is the cost-saving lever, not
  the other two.
- **The budget consequence is the maintainer's to see:** three added slices at the frontend band of
  0.75 / 1 / 2 days (the #920 plan (working id 9681)) move WK-675 from 9 slices, 6.75 / 9 / 18 days to 12 slices,
  9 / 12 / 24 days, before any leaf-plan split of S2 or S4. That arithmetic is the plan's own band
  applied to three slices, not a re-estimate.
- **Not recommended:** B, because the freeze leaves no room to cut a new Work's map plan and
  gate-slot sequencing costs more than the slices; C, because `PL-1267` disowns the frontend.

## Disposition

Proposed by the auditor; the verdict is the lead's. **The lead routes it.** Placement is a scope
question, and scope is the maintainer's (`document-ids.md` §1.7: a scope question goes to the
maintainer, as an `RL-` or an `RFC-`): (a) fold the three views into WK-675, which is a scope
change to a `WK-` row, (b) a new Work, or (c) place them out of Phase 2 with a dated line.
Declaring a view's Contents cell declared-prose (`00` FR-24) is a spec question, and the
decision-maker's. This finding decides none of these.

**Event that next confirms or discharges it:** each of `/rating`,
`/rating/:slug/v/:version/tests` and `/rating/environments` has a named owner in the roadmap or a
ruling.

## Decision (2026-09-30)

**The maintainer ruled, by delegation: option A for all three views.** Recorded from
`~/gi-pricing-plan.local/channel/to-lead.md`, the entry "2026-09-30 05:28:45 BST — SCOPE DECISION:
#921 …, the three unowned `03` §5.3 rating views go to WK-675 (option A)", which rests on this
essay's Options at `b6f8161d`, re-verified at `880feb49`, **as corrected by** the entry "2026-09-30
05:29:29 BST — DATED CORRECTION to "SCOPE DECISION: #921" (05:28:45): the slice count only". Both are
channel entries, not merged records; the ruling record is the mint turn's.

- **Owner: WK-675**, with the three views as three new slices. The finding's confirming event
  (each route has a named owner) is met once WK-675's plan (#920) carries them.
- **Order inside WK-675:** the Rating version list, then the Regression suite, after S6 and before
  S8/S9; the Deployments view last, after WK-674's deployment-history `GET` has landed.
  **Corrected 2026-09-30 by the maintainer** (`~/gi-pricing-plan.local/channel/to-lead.md`, the entry
  "2026-09-30 05:34:33 BST — SCOPE DECISION: #920 DP-4, option (a); the S12 order corrected; the S11
  run-list route covered"): S12 (Deployments) waits on **SL-1260**, WK-674's last slice (FR-269 rollback
  via SL-1259, FR-271 shadow via SL-1260), not on the history `GET` alone, because `03:1051` requires the
  rollback control and the shadow configuration. **The full view ships, not a partial one.** The planner
  re-derives the order at #920's revision (that is the #920 plan's (working id 9681) DP-4's interaction).
- **Spec first (`CLAUDE.md` §0):** `03` §5.1 has no `GET` list route for rating versions (item 8).
  The Version-list slice's first task is that spec change, a new FR and the §5.1 row, in the same
  commit as its code. It is not built ahead of its spec.
- **Budget:** #920 absorbs the three slices at its revision, **from 10 to 13 slices**, about 9.75 / 13 / 26
  days at the plan's per-slice band (exact figure per the planner's re-derivation on #920). The
  maintainer's first entry said 9 to 12 and 9 / 12 / 24; his **dated correction** supersedes the count
  only, because the #920 plan (working id 9681) already has 10 slices with `RL-1261`'s S7b. The Options above quoted 9 slices
  because they read the #920 plan's (working id 9681) row (a) (DP-2 as it then stood); `RL-1261` has since ruled (b).
- **Why A, and not E for Deployments** (the entry's reason, summarised): the three are specified P2
  views, so dropping one is a scope cut and the standing instruction is to complete works, not trim
  them; G2's deploy step is a scripted journey, so E was possible but not needed; with two lanes under
  `RL-1263` the extra three likely days are absorbed, and one frontend Work keeps one router owner.
- **Adjacent, not decided here:** `07` §5.3's other views have their own finding.

Ownership shape: event
