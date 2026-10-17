---
id: RL-8057
family: ruling
title: PL 8054 DP-1 and DP-2 decided (a) and (a) — the comparison version is picked from the Rating Version list route, which gets its §5.1 row first; the sandbox compare shows only what this quote shows
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-16
owner: decision-maker
tree: 0877e6e7a756c4621890713a4d3b016e75e33654
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1546, PL-1286, SL-1550, SL-1552, SL-1557, RL-1261, RL-1473, FD-1283, FR-262, FR-219, FR-440]
---

# RL 8057 — PL 8054's two decision points: DP-1 (a), with a spec row first; DP-2 (a)

Filed under **working id 8057**, reserved by the lead in `~/gi-pricing-plan.local/handover/eta.md`,
entry "2026-10-16 09:42:47 BST — Lead: RESERVED RL 8057 = the ruling on PL 8054 DP-1
(comparison-version choice) + DP-2 (RL-1261:100-104 "edited, no effect on this quote") for
SL-1550 (decision-maker-8054)". Written 2026-10-16 by the decision-maker (seat
decision-maker-8054). It rules the two blocking decision points of PL 8054 (working id; branch
`pl-1550-lanec-s7-test-design-2026-10-16` at `88e86e1a6f0e7d419d179d57677456fd3c075754`,
§"Decision points", its lines 242-251). **It does not edit PL 8054**; the planner applies it.

## Verified first, at `origin/main` 0877e6e7a756c4621890713a4d3b016e75e33654

Every line below was read at that tree with `git show origin/main:<path>`.

1. **FR-262** (`docs/specs/03-rating-engine.md:183`): *"score an arbitrary quote against any
   accessible Rating Version and see the full trace inline, alongside the same quote scored
   against a comparison version with a step-by-step difference. … The Quote Sandbox view is
   WK-675's."* It asks for a difference of the two **scorings** of one quote. It does not ask
   for a difference of the two algorithm definitions.
2. **The compare route** (`03:1060`): `POST /api/v1/score/compare`, `rating:read`; *"Any
   compiled version may be named, `draft` included"*; 404 and 409 `BUNDLE_COMPILE_FAILED`
   name their side. The side prefix is `backend/src/app/api/score.py:455-457`
   (`_naming_side`). PL 8054's DP-1 premise that the picker need not filter by compile state
   holds: an uncompiled pick answers 409 naming `comparison`.
3. **§4.10** (`03:914-954`): `unchanged` counts the steps whose traces are identical. RL-1261's
   amendment (`03:953`) says *"The request and response shapes do not change"*.
4. **RL-1261:101-104** (`docs/rulings/RL-01261-…`; PL 8054 and the lead's brief cite it as `:100-104`), verbatim: *"A step whose definition changed
   but whose trace is identical for this quote stays counted in `unchanged`, as today, because
   the diff lists what this quote shows. Whether the view should also show 'edited, no effect
   on this quote' is a view design question for WK-675's map plan."*
5. **§5.3** (`03:1408`, `:1410`): the **DAG designer** row carries *"structural diff overlay
   against another version"*; the **Quote sandbox** row carries *"side-by-side compare against
   another version"*. The overlay is built: `frontend/src/components/dag/DiffOverlay.vue`
   with its test, over FR-219's route (`frontend/src/api/ratingAlgorithms.ts`), delivered
   by SL-1557 (`PL-1556` Task 7).
6. **The list route DP-1 (a) reads.** `GET /api/v1/rating-versions` exists:
   `backend/src/app/api/models.py:1106-1129`, `rating:read`, `responses=problems(401, 403)`,
   rows filtered by `RatingVersionRow.workspace_id == caller.workspace_id`, ordered by
   `RatingVersionRow.version`, every status, no pagination, returning `list[RatingVersion]`.
   Its docstring: *"The Phase 1b rating versions the demo seeds (FR-440, W7-5). … The full
   `03` surface stays Phase 2."* The client is `frontend/src/api/ratingVersions.ts:7`
   (`listRatingVersions`), used by `frontend/src/views/DemoView.vue:72`. It is in
   `docs/contracts/openapi/generated.json` `paths["/api/v1/rating-versions"].get`.
7. **That route has no `03` §5.1 row.** This command prints nothing at the tree:

   ```
   git grep -nE '`?GET`? *\| *`/api/v1/rating-versions`? *\|' origin/main -- docs/specs
   ```

   §5.1 has `POST /api/v1/rating-versions` (`03:1050`) and the two single-version
   reads (`:1051`, `:1052`), not the list. `FD-1283` item 8 recorded the same gap (*"no `GET`
   list route"*), and `PL-1286:313` (S10, `SL-1552`, `status: draft` at `docs/roadmap.md:1546`)
   owns *"a new `03` FR and the §5.1 row for a `GET` list route over Rating Versions, in the
   same commit as its code"*. **PL 8054's DP-1 row calls the route "already generated and
   used", which is true, but does not say it is undeclared.** That is the one premise this
   ruling corrects.

## Ruled

### DP-1 — decided (a), with one spec row first

**Ruling.** The comparison version is chosen from a select fed by `listRatingVersions`: every
version except the one in view, "No comparison" first and selected, as PL 8054 §"The design"
states. **Before the picker's code, SL-1550 lands T1 below in `03` §5.1, in the same commit
as the code that first calls the route from the sandbox** (`CLAUDE.md` §0: a capability not
yet specified is a spec change first; §2: spec and code in one commit).

**Why (a).** FR-262 says *"any accessible Rating Version"*. The list route returns the
caller's workspace's versions under `rating:read`, and the compare route resolves both refs
in the same workspace under the same permission, so the list is that set (item 6). (b) makes
discovery the actuary's problem and turns every typo into a 404. (c) adds router state FR-262
does not ask for; a linkable comparison can come later as its own row without removing
anything (a) builds.

**Why the spec row, and why now.** S7 would be the first view to depend on the list route
for a spec'd capability rather than for the Phase 1b demo. A view built on a route the spec
does not declare is the gap `FD-1283` was filed for. Waiting for S10 is not an option: the
reverse-ladder order puts S10 after S7 (`PL-1546:66`), and S10 may be cut. So the row lands
with its first spec'd consumer. **T1 records the route as it is; it changes no behaviour and
no shape.** It is the same move `RL-1473` made for the by-id read (`03:1052`: *"records an
existing route"*).

**T1 — the `03` §5.1 row, verbatim**, inserted directly above the
`GET /api/v1/rating-versions/{slug}@{version}` row (`03:1051`):

```
| `GET` | `/api/v1/rating-versions` | List the caller's workspace's Rating Versions, every status, ordered by `version` (FR-262: the Quote Sandbox's comparison picker); requires `rating:read`. **200** with a `RatingVersion[]` (§4.3), unpaginated; 401; 403. Built in Phase 1b (FR-440); records an existing route, declared 2026-10-16 (RL 8057, working id), owner WK-675. S10 (`SL-1552`) amends this row with its own FR and the list view's needs; it does not add a second row |
```

The executor writes `RL-8057`'s minted id in place of "RL 8057, working id" if this record is
minted before SL-1550's PR; otherwise the mint rewrites it.

**What T1 does not decide.** Pagination, filtering by status or slug, and sort order across
slugs stay S10's (`PL-1286:313`). If S10 changes the response shape, S10 keeps the S7 picker
test green or updates it in the same commit.

### DP-2 — decided (a); RL-1261's question is answered, not carried

**Ruling.** The sandbox compare view lists `diff.steps` and nothing else. A step whose
definition changed but whose trace is identical for this quote is **not** shown as a row. The
step table's caption reads **`{n} steps unchanged for this quote`**, exactly as PL 8054
writes it. **This answers `RL-1261:100-104` for WK-675: no, the sandbox does not show "edited,
no effect on this quote".** No open question is raised; nothing is carried.

**(a) is consistent with FR-262 and RL-1261 as written** (the lead's question):

- FR-262 asks for *"a step-by-step difference"* of *"the same quote scored against a comparison
  version"* (item 1). That is the trace diff. A step with an identical trace for this quote has
  no difference to show.
- RL-1261 keeps such a step in `unchanged` *"because the diff lists what this quote shows"*
  (item 4), and leaves only the view question open. The caption's *"for this quote"* states
  that scope in the view, so the count is not read as "no definition changed".
- The definition-level difference already has its view: §5.3's DAG designer *"structural diff
  overlay against another version"* (item 5), built. An actuary who needs "what was edited"
  reads it there. Showing it in the sandbox too would put FR-219's answer in two views.
- `PL-1286` Acceptance item 8 (`:131-133`) bars rendering `own_change: false` as
  "unchanged" or "not edited". The caption is not a `StepChange` label: it counts the steps
  that are **not** in `diff.steps`. Item 8 holds; PL 8054 Acceptance 2's grep is scoped to
  `stepChange.ts` and stays the check.

**Why not (b) or (c).** (b) adds a second fetch per compare: FR-219's route takes **algorithm**
refs (`/api/v1/rating-algorithms/{slug}@{version}/diff?against=`, `against` required in
`generated.json`), so the view first reads each side's `RatingVersion.algorithm_ref`. That is a
different design from S7's row, and it duplicates item 5's overlay. (c) changes `TraceDiff`,
which `RL-1261` (item 3) fixes, and needs a `03` §4.10 amendment and a backend slice; neither is
in S7's row.

**No spec change for DP-2.** §4.10 and FR-262 are unchanged.

## What it obliges

- **The planner** applies both rulings to PL 8054 before activation. **DP-1**: add T1 as the
  first step of the task that adds the picker (the spec row and the code in one commit), and
  add to Acceptance that this command prints T1's row and only it:

  ```
  git grep -nE '^\| `GET` \| `/api/v1/rating-versions` \|' -- docs/specs/03-rating-engine.md
  ```
 Correct DP-1's premise to say the route is undeclared until T1. **DP-2**:
  no design change; cite this record where PL 8054 names `RL-1261:100-104` (its Context 5 and
  its self-review line).
- **SL-1550's executor** lands T1 verbatim, in the commit that first calls `listRatingVersions`
  from `QuoteSandboxView.vue`, and runs `python3 scripts/audit-docs.py` on it under the
  gate-2 flock.
- **S10 (`SL-1552`)**: its spec-first task becomes *amend* T1's row and add its FR, not add a
  row. Its plan is not cut yet (`PL-1546` does not pre-cut S10), so its planner reads this
  record when it cuts it. No frozen plan is edited.
- **`FD-1283`** is not discharged by this record: its list-view limb (the `/rating` view) is
  still S10's.

## Acceptance — the violation that must become detectable

The violation: **the sandbox compare view ships on a route the spec does not declare, or it
shows a row or a label that claims more than this quote's traces show, and no check fails.**
Each item names its broken input. The SL-1550 `LG-` shows each red before it is filed
(`CLAUDE.md` §13).

1. **T1 is in the spec (DP-1).** *Violation: the picker calls `listRatingVersions` and `03`
   §5.1 has no list row.* Check: the grep in "What it obliges" prints T1's row. Broken input:
   at `origin/main` 0877e6e7 it prints nothing (rc 1, run 2026-10-16 for this record).
2. **The picker offers the accessible set minus the version in view (DP-1).** *Violation: the
   version in view is offered, or "No comparison" is not the first option.* PL 8054's test C1
   asserts the options' text in order; it reds on a breaker that drops the `comparable` filter.
3. **Only `diff.steps` become rows (DP-2).** *Violation: the view adds a row for a step that is
   not in `diff.steps`.* PL 8054's test B5 asserts exactly 5 body rows, in
   fixture order; it reds on a breaker that appends one row.
4. **The caption is scoped to this quote (DP-2).** *Violation: the caption reads
   `{n} steps unchanged` without "for this quote".* B5 asserts the table's accessible name contains
   `11 steps unchanged for this quote`; it reds on a breaker that drops "for this quote".
