---
id: FD-9692
family: finding
title: Three 03 §5.3 views (the rating version list, the regression suite and Deployments) are owned by no Work, plan, ruling or closure
status: active
created: 2026-09-29
owner: auditor
tree: f0c3d197f5d89863efc647a2d7c1a6994b74dd63
corrected_by: []
relates: [WK-675, WK-674]
---

# FD-9692 — Three 03 §5.3 views have no owner

## Finding

`03-rating-engine.md` §5.3 lists seven frontend views (`03:1044` to `:1050`). WK-675's roadmap
row (`docs/roadmap.md:691`) names four: the DAG designer, the rate table editor, the quote
sandbox and the dislocation views. **The other three have no owner:** the rating version list
(`/rating`, `03:1044`), the regression suite (`/rating/:slug/v/:version/tests`, `03:1048`) and
Deployments (`/rating/environments`, `03:1050`, which overlaps `07:386`'s `/admin/environments`).
**Proposed by the auditor; the disposition is the lead's.** FD-9692 is a working id, minted at
the records PR. Read at `origin/main` `f0c3d197`, 2026-09-29.

## Evidence

1. **The predicate, run verbatim.** It is the one the WK-675 map plan (PR #920, working id 9681) states, run from a
   detached worktree at `f0c3d197`:
   `grep -rn -E 'rating/environments|/rating\`|Rating version list|Regression suite view|/v/:version/tests|Deployments view|admin/environments' docs --include=*.md`
   prints **five** lines, not four: `07-platform.md:386`, `03-rating-engine.md:1044`, `:1048`,
   `:1050`, and `docs/findings/register.md:61` (F-W9-3). The fifth is a false positive: the
   `/rating\`` alternative matches `pricing_core/rating\`` in prose about `compile.py`. **None of
   the five assigns the frontend limb of any of the three views to a Work.**
2. **A wider sweep** over `docs/roadmap.md`, `docs/plans`, `docs/rulings`, `docs/closures`,
   `docs/ledgers`, `docs/workflows`, `docs/process` and `docs/open-questions.md`, for
   `version list`, `regression.suite (view|screen|UI|page)`, `deployments? (view|screen|page|UI)`,
   `environments? (view|page|screen)`, `/admin/environments` and `rollback control` (the command
   is `grep -rn -i -E` with that alternation over those paths), finds no line that assigns a view.
3. **One near miss, stated so that it is not read as ownership.** `PL-1237` (WK-674's map plan),
   Task 2, adds a `GET` for deployment history "which FR-382 and the view at `03:847`
   (`03:1050` at `9cd179cb`) need and `03` §5.1 lacks". That is the **backend** limb the
   Deployments view consumes. WK-674 owns that route; nothing owns the view.
4. **`00` §5.6's canonical route table (`00:404` to `:407`) lists four rating views** (designer,
   editor, sandbox, dislocation) and none of the three. FR-25 (a registered route is reachable from
   the entry by following links) therefore has no anchor for them.
5. **Why it matters now.** `RFC-1248` Part 2 and `CLAUDE.md` §14: an accepted proposal becomes an
   owned record, and "unowned" is not a permitted state. `WF-699` D1 to D5 and E5, and `WF-701` A5,
   exercise regression and deployment steps whose UIs these views are.

## Disposition

Proposed by the auditor; the verdict is the lead's. Route the owning decision to the
decision-maker as one `RL-`: (a) fold the three views into WK-675 (a scope change to a `WK-`
row, which is the maintainer's), (b) a new Work, or (c) declare each view's Contents cell
declared-prose, or out of Phase 2, with a dated line.

**Event that next confirms or discharges it:** each of `/rating`,
`/rating/:slug/v/:version/tests` and `/rating/environments` has a named owner in the roadmap or
in a ruling.

Ownership shape: event
