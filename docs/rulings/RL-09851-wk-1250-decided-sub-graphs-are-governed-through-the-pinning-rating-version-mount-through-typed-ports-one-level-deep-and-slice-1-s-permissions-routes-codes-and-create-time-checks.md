---
id: RL-9851
family: ruling
title: WK-1250 decided — sub-graphs are governed through the pinning Rating Version, mount through typed ports one level deep, and Slice 1's permissions, routes, codes and create-time checks
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 7c354305247236be1a3a50150c9c17b0134c4c5e
phase: P2
work: WK-1250
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1254, PL-1278, FR-217, FR-20, FR-1186, FR-227, RL-1184, RL-1290]
---

# RL-9851 — WK-1250 decided: PL-1254 DP-1, DP-3, DP-4 and PL-1278 DP-S1-1 to DP-S1-4

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). The session's
own `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`.

The record was prepared at effort `medium` (PR #938, head `f09be926`, "PREPARED, NOT
RULED"). Its evidence and its prepared recommendations are kept below, unchanged except where
marked, because they record what was believed before this pass. **The decisions are in
"Ruled".** Where a ruling departs from a prepared recommendation, it says so and why. It keeps
the working id 9851; the id is minted at the lead's merge turn.

**Not to be confused with `RL-1291`.** `RL-1291` (#956) decided a *different* "DP-S1-1": WK-690
Slice 1's (`PL-1268`), `work: WK-690`. The DP-S1-1 to DP-S1-4 here are WK-1250 Slice 1's, in
`PL-1278` (the leaf plan first read as working id 9820, #929; `git show origin/main:docs/INDEX.md
| grep '^| PL-1278 '` resolves it). The maintainer endorsed ruling these on their own merits.

**DP-2 is not ruled here.** It blocks Slices 2 and 3 only, and was not prepared.

## Evidence

**Trees.**
- *Re-verified 2026-09-30 at `7c354305` for this ruling:* `git diff --stat 0bc69b5b 7c354305
  -- packages backend docs/specs docs/plans/PL-01254* docs/plans/PL-01278*` prints nothing, so
  every file:line below, read at `aa14e90d` and refreshed at `0bc69b5b`, still holds at the
  ruling tree. The facts this pass added are cited at `7c354305` in "Ruled".
- Specs and code: `origin/main` at `aa14e90dd77c7461aa35cc6461557b129959463f`.
- Slice 1 leaf plan: **PL-1278** (PR #929; first read on `origin/wk1250-s1-leaf` at
  `a706430671bef6592930110e1a392dab4b8f7646`, before it minted).
- *Refreshed 2026-09-30 at origin/main `0bc69b5b`.* The leaf plan is cited as PL-1278 by
  section heading. `compile.py`, `rating.py`, `approvals.py`, `06`, the rating and
  regression-suite routes, and `03` above `:1180` are unchanged between `aa14e90d` and
  `0bc69b5b` (`git diff --stat`), so every file:line below still holds.

**Where the questions are.**
- The map plan is `docs/plans/PL-01254-wk-1250-sub-graph-composition-and-mta-cancellation-pricing-map-plan.md`.
  Its rows are DP-1 at `:210`, DP-2 at `:211`, DP-3 at `:212` and DP-4 at `:213`.
- PL-1278's rows are DP-S1-1 to DP-S1-4, under §Scope, "Decision points".
- The leaf plan is written on the map's recommendations DP-1 (b), DP-3 (a) and DP-4 (a) (the
  same subsection's preamble), and names every step that changes if a ruling differs.
- Every row is kind "decision point", and every "Resolved by" cell is empty.

**Premises verified at `aa14e90d`.**

| Premise | Status | Evidence |
|---|---|---|
| The maturity exemption | CONFIRMED | `packages/pricing-core/src/pricing_core/rating/compile.py:314`: `_MATURITY_CHECK_EXEMPT = frozenset({"rate_table", "rating_algorithm"})`. It is applied at `:453` (the algorithm) and `:475` (each pin). The rationale (RL-856, RL-859) is at `:289-312`. The map plan cites only the `rate_table` member; `rating_algorithm` is also exempt. |
| Sub-graph types | CONFIRMED, with a correction | `packages/model-schema/src/model_schema/rating.py:205-244` holds `InputContractField` and `AlgorithmOutput`, not sub-graph types. `SubGraphRef` is at `:340-350` and has only `ref` and `mount_point`. `Pins` has no sub-graph key. |
| Governed Artifact | CONFIRMED | `06` §2 `:64` enumerates Governed Artifacts, and Sub-graph is not among them. `06` §3.3 `:119` strikes the Rate Table Version row: "not a Governed Artifact. Its diffs reach approval inside the Rating Version row's rate table diffs". `:120`: the Rating Version evidence is "Structural diff; rate table diffs; …", with **no sub-graph diffs**. |
| FR-20 | CONFIRMED, relocated | FR-20 is defined in `00-overview.md:224` ("Enforced at transition time"). `03:399-401` is §4.3's invariant "every pin resolves to an artifact whose status is `approved` or better (FR-20)". That invariant already disagrees with the permanent `rate_table` and `rating_algorithm` exemptions (`03:128`, FR-1186). |
| The FR-1186 revisit trigger | CONFIRMED | `03:128`: "a Rate Table Version pinned by more than one Rating Version in practice". |
| Routes | CONFIRMED | `backend/src/app/api/rating_algorithms.py:48,68` pass `caller.workspace_id`. The permissions are `rating:read` and `rating:write`, through `requires()`, which accepts workspace-wide assignments only. |
| Structural validation at save | CONFIRMED | `03:81`, FR-212: "Cycles, orphaned steps, and references to undefined Derived Values are rejected at save time, not at scoring time." |
| The diff | CONFIRMED | `03:88`, FR-219: the structural diff covers "steps added/removed/changed, tables re-pointed". Nothing covers sub-graphs. |
| Versions | CONFIRMED | `00:280`, ID-2: `version: int` starts at 1, rises per parent, and is never reused. |
| Nesting | NOT FOUND | No spec constrains nesting. Sub-graphs are named only in `03` (`:63`, `:86`, `:87`, `:276`, `:1046`, `:1171`). |
| The mount point | DIFFERS from what DP-3 assumes | `03:276`'s example `{"ref": "sub_graph:ncd-ladder@4", "mount_point": "s_ncd"}` names a `mount_point` that is no step in that example. The parent's graph invariants never read `sub_graphs`. |

**A closer precedent than either plan cites.** The Regression Suite:
- It is a versioned rating artifact that is "never approvable" (the deputy's DP-S2-1 (A);
  `backend/src/app/platform/regression_suites.py:3-4`).
- It is created through a single `POST /regression-suites/{slug}/versions`
  (`backend/src/app/api/regression_suites.py:1-6`), with server numbering `1 + max(version)`
  (`platform/regression_suites.py:86-90`).
- A lost race maps to `VALIDATION_FAILED` 409 (`:69`, the `IntegrityError` mapping at
  `:11-12`), and the create is audited (`:140`).

~~**Stale in the leaf plan.** It read its tree at `25b0ead2`, before #933. Its `models.py`
lines are 6 lower than at `aa14e90d` (for example `RatingAlgorithmRow` is now `:1926`), and
the migration head is now `d7e2a9b5c418`, not `a71c3e95d204`. The plan's re-point procedure
covers the second point, but both premises are stale as written.~~
*No longer holds (2026-09-30, at `0bc69b5b`).* PL-1278 was re-derived before it minted. Its
§Status and §Scope, "Premises re-derived at the tree above", now give `RatingAlgorithmRow` at
`models.py:1926-1954` and the migration head as `d7e2a9b5c418` (premise i), which match main.

## DP-1: is a sub-graph version a Governed Artifact?

| | Option | For | Against |
|---|---|---|---|
| (a) | Its own approval: a `06` §3.3 row, a §4.2 `sub_graph` policy, and a maturity check | Every change is approved on its own | An approval path and a gate for an artifact that prices nothing until a Rating Version pins it. It departs from both ungoverned precedents (Rate Table Version, Rating Algorithm). |
| (b) | Not governed on its own, like a Rate Table Version. Its change reaches approval inside the pinning Rating Version's evidence, and each version carries a change note | Matches FR-1186 and RL-859. There is one approval per change: the act `06` already approves. | Needs `sub_graph` in `_MATURITY_CHECK_EXEMPT`, and a clarification of the FR-20 invariant at `03:400-401`. |
| (c) | Governed only as a purpose (MTA or cancellation) sub-graph | — | Splits one artifact kind by its use. |

**Prepared recommendation (superseded by "Ruled"): (b), as the planner recommends, with two conditions the planner did not state.**

1. **(b) has no mechanism yet.** The rate-table precedent works because `06` §3.3 `:120`
   names "rate table diffs" in the Rating Version evidence. For sub-graphs, the ruling must
   add:
   - a "sub-graph diffs" item to that evidence, and the matching §4.2 evidence key if one is
     needed;
   - the widening of FR-219's structural diff to "sub-graphs re-pointed or changed";
   - the WK-1250 slice that builds both.

   Without these, (b) exempts sub-graphs from approval rather than routing them through it.
2. **FR-1186's revisit trigger is met by design.** A sub-graph exists to be shared: FR-217's
   example is `ncd-ladder@4`. So the analogy to a Rate Table Version is weakest exactly where
   FR-1186 said to revisit. The provisional answer is that (b) still holds:
   - each Rating Version's evidence diffs against its own predecessor, so every Rating Version
     that adopts a changed sub-graph shows the re-point in its own approval;
   - sharing multiplies reviews and loses none.

   The high pass should confirm this against FR-257's evidence definition before it rules.

Also, the FR-20 invariant clarification should cover all three exemptions (`rate_table`,
`rating_algorithm` and `sub_graph`), not only the new one. That fixes an existing
disagreement as well as preventing a new one.

**Interaction with `ApprovalPolicy`, added 2026-09-30 at the lead's request.** Verified at
`aa14e90d`.
- **The model is closed.** `ApprovalPolicy` and `ApprovalPolicyEntry` are
  `extra="forbid"` (`packages/model-schema/src/model_schema/approvals.py:111-128`).
- **Three `06` §4.2 keys are not modelled.**
  - `expedited` (`06:329`, FR-385 at `06:181`) and `escalation` (`06:314`) are absent.
    `git grep -n expedited -- packages backend` finds nothing, so FR-385 is unbuilt.
  - `separation_of_duties` is modelled only as the flat `submitter_may_approve` field
    (`approvals.py:134-145`).
  - *(2026-09-30)* This gap has since been filed as FD-1281 (merged by #947, 2026-09-30).
- **The evidence floor.** `EVIDENCE_FLOOR`'s `rating_version` entry is `("structural_diff",
  "regression_run", "dislocation_run")` (`approvals.py:101-108`).
- **What each option touches.**
  - **DP-1 (a)** would add a `sub_graph` entry to `DEFAULT_POLICY` and possibly to
    `EVIDENCE_FLOOR`, both in `approvals.py`.
  - **DP-1 (b)'s "sub-graph diffs" evidence** touches the same file, if it becomes its own
    evidence key rather than part of `structural_diff`.
  - **OQ-1234's prepared option (b)** (#935, working id 9901, at `aa38bd4f`; unchanged in substance at `4fc680ed`, 2026-09-30) adds a
    skip-permission field to the environment-qualified `deployment` entry of
    `ApprovalPolicyEntry`.
- **The consequence.** Whichever of these rulings lands, it changes a closed model that
  already omits three keys that §4.2 publishes. The high pass should rule them against one
  another, not separately.
- **The provisional preference.** Under (b), fold sub-graph diffs into `structural_diff`
  (FR-219 widened). That adds no new key to `approvals.py`, and leaves `ApprovalPolicy`'s
  shape to OQ-1234 and FR-385.

## DP-3: how does a sub-graph connect at its mount point?

| | Option | For | Against |
|---|---|---|---|
| (a) | An explicit port contract: named inputs and outputs, a parent→port map, and inlined node ids namespaced by mount point | A mismatched mount is refused at compile time, and the trace stays attributable (FR-258) | New contract surface in `model-schema` |
| (b) | Splice: node ids are copied into the parent and wired by name | Least new shape | A name clash becomes a silent rewire, which is a mispricing path |
| (c) | A separate ZEN evaluation per sub-graph | Isolation | Not the inlining FR-217 names, and it adds a second evaluation to scoring |

**Prepared recommendation (superseded by "Ruled"): (a), as the planner recommends, with one addition.** The contract must also
define **how the parent's save-time validation sees port outputs**:
- `_graph_invariants` ignores `sub_graphs` today, so a parent that consumes a value only its
  sub-graph produces would be refused as unresolved;
- `03:276`'s `mount_point` names no step in its own example.

The ruling should therefore settle two things:
- whether `mount_point` names a parent step or is a free label;
- that the parent's invariants treat the mounted sub-graph's declared outputs as produced.

This is Slice 1's contract, not only Slice 2's inliner.

## DP-4: may a sub-graph mount sub-graphs?

| | Option | For | Against |
|---|---|---|---|
| (a) | No: depth 1, refused at validation | The pin set and trace stay flat. No requirement or workflow needs nesting (none found in `00`, `03`, `06` or `07`). | A later need is a spec change |
| (b) | Yes, to a fixed depth, with cycle detection | Some reuse | Cycle detection and nested namespacing with no consumer |
| (c) | Yes, unbounded | — | As (b), plus no bound on the size of the pin set or the trace |

**Prepared recommendation (superseded by "Ruled"): (a), as the planner recommends.** The refusal should be a named shape
invariant in `model-schema`, so that DP-S1-4 (a) covers it at create time.

## DP-S1-1: permission

| | Option | For | Against |
|---|---|---|---|
| (a) | `rating:write` for the writes and `rating:read` for the reads, through `requires()`. No new permission or scope. | Follows the precedent of the Regression Suite rows. Authoring is a workspace-wide act. | A principal scoped to one Rating Algorithm (`06` FR-345) cannot even read a sub-graph that its algorithm mounts. |
| (b) | New `sub_graph:read` and `sub_graph:write` | Separate grant | Adds catalogue entries (RL-1236) for a separation nobody has asked for |
| (c) | (a), plus `ScopeType.SUB_GRAPH` | Fine-grained | A scope with no consumer before a designer exists |

**Prepared recommendation (superseded by "Ruled"): (a).** State the scoped-principal consequence in the ruling as accepted. Also
widen the catalogue *text* at `06:265` (the `rating:read` scope) and `06:287-288` (the
`rating:write` scope) to name sub-graphs. Neither line names them today, and neither names
regression suites. That is a text edit under RL-1236, not a new name.

## DP-S1-2: storage, numbering and routes

| | Option | For | Against |
|---|---|---|---|
| (a) | One table `sub_graph_versions`, unique on `(workspace_id, slug, version)`. Server max+1 numbering, 409 on a race. `POST /sub-graphs` (v1) plus `POST /sub-graphs/{slug}/versions` (next), `GET /sub-graphs/{slug}@{version}`, and a paginated version list | No gaps (ID-2) and no container state | Two create routes for one act |
| (b) | Two tables, the rate-table layout | — | A registry table that holds nothing |
| (c) | As (a), but the client supplies `version` | Matches the rating-algorithm form | Two authors can both pick the same number |
| (d) | **Not in the plan.** The Regression Suite form: one `POST /sub-graphs/{slug}/versions` creates v1 or the next, with server `1 + max(version)`, a 409 on a race, and one audit event | The nearest precedent (an unapproved, versioned rating artifact) already built and tested. One create route. | That precedent uses a registry table plus a versions table, so only its route form, not its storage, carries over. |

**Prepared recommendation (superseded by "Ruled"): (a)'s single table, with (d)'s single create route.** This departs from the
planner in the route count only. One act gets one route, and it matches the most similar
existing artifact. The high pass should check that `00` §5.1's URL rules (`00:314-321`, "Sub-
resources nest one level maximum") and the §5.1 table in `03` accept creating a slug's first
version through `/{slug}/versions`. The Regression Suite row already does this.

## DP-S1-3: error codes

| | Option | For | Against |
|---|---|---|---|
| (a) | Reuse `RATING_GRAPH_CYCLIC`, `RATING_GRAPH_UNRESOLVED_REF` (`03:771-779`), `VALIDATION_FAILED` (also 409 on a race, as at `platform/regression_suites.py:69`), and `NOT_FOUND` | Clients already handle them. The `instance` path names the artifact. | A client cannot tell a sub-graph refusal from an algorithm refusal by code alone |
| (b) | New `SUB_GRAPH_*` codes owned by `03` §5.1 | Distinct codes | They differ only by artifact |

**Prepared recommendation (superseded by "Ruled"): (a), as the planner recommends.** DP-4 (a)'s depth refusal then carries
`VALIDATION_FAILED`.

## DP-S1-4: create-time validation depth

| | Option | For | Against |
|---|---|---|---|
| (a) | Shape invariants only, in `model-schema`. The five expression checks run on the inlined algorithm at compile (Slice 2). | Keeps `pricing-core` out of Slice 1 | A non-deterministic fragment is saved and refused only when a mounting algorithm compiles, and Slice 2 must prove that refusal |
| (b) | Generalise the helpers to run the context-free checks at create | Stricter | Touches `compile.py`, which Slice 2 rewrites |
| (c) | Wrap the fragment in a synthetic algorithm | — | The result-type checks run against an invented input contract |

**Prepared recommendation (superseded by "Ruled"): (a), as the planner recommends.** It fits FR-212's actual clauses: FR-212
(`03:81`) requires *cycles, orphaned steps and undefined references* to be rejected at save,
and those are shape invariants that (a) keeps at create. The expression checks are not among
FR-212's clauses. The ruling should say so explicitly, so that (a) is not later read as a
breach of "rejected at save time".

## DP-2 (not prepared here)

DP-2 blocks only Slices 2 and 3, and it shares no evidence with the rows above beyond
`SubGraphRef` (`rating.py:340-350`). It is left for its own preparation.

## Ruled

Citations in this section were read at `7c354305`.

### DP-1 — option (b): a sub-graph version is not a Governed Artifact; its change is approved inside the pinning Rating Version

1. **No approval of its own.** A Sub-graph Version has no status and no approval lifecycle,
   as a Rate Table Version (`03` FR-1186) and a Rating Algorithm (`RL-859`) have none. It is
   not added to `06` §2's Governed Artifact list (`06-governance.md:64`), gets no `06` §3.3
   row and no §4.2 `DEFAULT_POLICY` entry. Each version is immutable once created and carries
   a required change note, as FR-229 requires of a Rate Table Version (`03:120`).
2. **The mechanism — what makes (b) route through approval, not around it.** The change
   reaches approval through the Rating Version that pins it (PL-1254 Task 2 adds the pin,
   `Pins.sub_graphs`). That Rating Version's approval sees it three ways, all of which exist
   or are owned today:
   - **The structural diff.** `03` FR-219 (`03:88`) is widened: the structural diff between
     two Rating Versions also lists **each sub-graph pin added, removed or re-pointed**, and
     for a re-point it carries **the structural diff between the two sub-graph versions**
     (steps added, removed or changed inside the fragment). It is part of the existing
     `structural_diff` evidence kind, so no new evidence key is added to
     `EVIDENCE_FLOOR` (`approvals.py:106`) or to `06` §4.2. `06` §3.3's Rating Version row
     (`06:120`) names it in its "Structural diff" item.
   - **The regression suite and the dislocation run** (`03` FR-257, `03:174`). Both are run
     per Rating Version, so every Rating Version that adopts a changed sub-graph shows the
     change's effect on its own golden quotes and its own portfolio.
3. **Who builds the diff.** The structural diff is unbuilt, and it is **WK-673's**: `RL-1184`
   E4 names WK-673 as `structural_diff`'s owner, and `RL-1290` restates it at this tree
   (`rating.py:125` holds only an optional `structural_diff_blob`, and `git grep -n -i
   'def structural\|StructuralDiff' -- packages backend/src` prints nothing). So:
   **whichever of WK-673's structural diff and WK-1250 Slice 2's sub-graph pin lands second
   carries the sub-graph limb.** If Slice 2 lands second, it extends the diff. If WK-673 lands
   second, its diff covers `Pins.sub_graphs`. Neither may close while the other has landed and
   the limb is missing. FR-219's widening is written into `03` in Slice 2's spec change, with
   the pin it describes.
4. **FR-1186's revisit trigger is met by design, and (b) still holds.** A sub-graph exists to
   be shared (FR-217's `ncd-ladder`), which is FR-1186's revisit condition ("pinned by more
   than one Rating Version in practice"). The answer is that sharing multiplies reviews and
   loses none. Each adopting Rating Version is approved against its own predecessor, with
   the re-point in its diff and its own regression and dislocation evidence. A sub-graph
   version that no approved Rating Version pins prices nothing.
5. **FR-20 and the maturity gate.** `03` §4.3's invariant "every pin resolves to an
   artifact whose status is `approved` or better (FR-20)" (`03:399-401`) already disagrees
   with the two exemptions in force (`_MATURITY_CHECK_EXEMPT = frozenset({"rate_table",
   "rating_algorithm"})`, `compile.py:314`). Slice 2's spec change restates it by class, not by
   list: *every pin to an artifact that has an approval lifecycle resolves to `approved` or
   better (FR-20); a pin to an artifact that has none (Rate Table Version, Rating Algorithm,
   Sub-graph Version) is governed by the pinning Rating Version's own approval.* In the same
   slice, `sub_graph` joins `_MATURITY_CHECK_EXEMPT`, with a comment citing this record and a
   tripwire test in the form of `test_rate_table_version_row_has_no_status_column`: it fails
   the day a `status` column is added to the sub-graph table, and names this record.

### DP-3 — option (a): an explicit, typed port contract, with the fragment's own names namespaced

1. **The sub-graph declares its ports.** Its input ports each have a `name` and a declared
   type. Its output ports reuse `AlgorithmOutput` (`rating.py`: `name`, `type:
   RatingResultType`, `required`), so the float refusal and FR-227's result-type
   vocabulary are the ones algorithms already use. Slice 1 may not define a second
   result-type vocabulary. An input port's type uses the same `RatingResultType`, because
   the value that feeds it is a parent step's result.
2. **`mount_point` is the mount's own identifier, not a parent step.** It is unique among the
   parent's `step_id`s and its other mounts. It namespaces the inlined steps and attributes
   them in the trace (FR-258). The `03:276` example, which names `"s_ncd"` and no step called
   that, is consistent with this reading. The example's value is left as it is.
3. **The mount maps names explicitly.** The parent's mount maps each input port to a parent
   value, and each output port to the parent name it produces. On inlining, **every name
   internal to the fragment is namespaced by the mount point**. Only the mapped port names
   meet the parent's namespace, so a fragment's intermediate name can never silently rewire a
   parent value (option (b)'s failure).
4. **The parent's save-time invariants see the mount.** `03` §4.1's invariants
   (`03:280-282`, FR-212) treat a mount as a node: its mapped outputs are *produced* by it,
   its mapped inputs are *consumed* by it, and acyclicity and "produced by exactly one
   upstream step" count it. Without this, a parent that consumes a value only its mount
   produces is refused as unresolved.
5. **Where each half lands.** The sub-graph's ports are part of Slice 1's shape. The mount's
   port map on `SubGraphRef` (`rating.py:340-350`, today `ref` and `mount_point` only) and
   item 4's invariants land in Slice 2, with the pin and the inliner, because until then
   nothing mounts and `score.py`'s purpose guard refuses sub-graph use
   (`score.py:393-405`). Checking a mount's port map against the pinned version's declared
   ports is a compile-time check, in Slice 2.

### DP-4 — option (a): depth 1

A sub-graph mounts nothing. The Slice 1 shape has **no `sub_graphs` field** and is
`extra="forbid"`, so a fragment carrying one is refused by construction at create, with
`VALIDATION_FAILED` (DP-S1-3). Slice 2's compiler refuses a nested mount again, by cause, in
case a fragment reaches it by another path. Nesting later is a spec change: no requirement or
workflow in `00`, `03`, `06` or `07` needs it (prepared evidence, "Nesting").

### DP-S1-1 — option (a): `rating:write` and `rating:read`, workspace-wide

1. The two write routes require `rating:write`, and the two read routes `rating:read`, through
   `requires()`. No new permission and no new scope type. This is the precedent of `03`
   §5.1's Regression Suite rows (`03:756-757`).
2. **The scoped-principal consequence is accepted.** `requires()` admits only a
   workspace-wide assignment, so a principal scoped to a named Rating Algorithm (`06`
   FR-345) can neither read nor author a sub-graph through these routes. That is correct for
   authoring: a sub-graph may be mounted by any algorithm in the workspace, so authoring one
   is a workspace-wide act. For reading, compile and score resolve a pinned sub-graph through
   the artifact resolver, not these routes, so a scoped principal's compile is not blocked.
   A designer view that shows a scoped author a mounted fragment (WK-675) is a later spec
   change if it is needed.
3. **The catalogue text is widened, not renamed** (`RL-1236` governs the names). In Slice 1's
   spec change, the `rating:read` row (`06:265`, "Reading Rating Algorithms, Rate Tables,
   Rating Versions and scoring traces") and the `rating:write` note (`06:287-288`) name
   sub-graphs. Neither names regression suites today either, so the same edit adds them.

### DP-S1-2 — option (a), as the planner recommends: one table, server numbering, two create routes

**This departs from the prepared recommendation**, which preferred the Regression Suite's
single create route.
1. **Storage.** One table, `sub_graph_versions`: one row per version, content as JSONB, and
   unique on `(workspace_id, slug, version)`. There is no registry table, because a sub-graph
   has no container-level state.
2. **Numbering.** The server numbers each version as the current maximum plus one. The unique
   constraint turns a race into `VALIDATION_FAILED` 409, in the form of
   `objectives.py:229-236` and `regression_suites.py`'s `_next_version`. Versions are
   gap-free and never reused (`00` ID-2).
3. **Routes**, all within `00` §5.1's one-level nesting rule:
   `POST /api/v1/sub-graphs` creates version 1 of a new slug and returns 409 if the slug
   exists; `POST /api/v1/sub-graphs/{slug}/versions` creates the next version and returns
   `NOT_FOUND` if the slug does not exist; `GET /api/v1/sub-graphs/{slug}@{version}`; and
   `GET /api/v1/sub-graphs/{slug}/versions`, cursor-paginated.
4. **Why two create routes.** A sub-graph slug is a free name in the workspace. With a single
   create route, an author who creates `ncd-ladder`, unaware that one exists, silently
   publishes version 5 of someone else's fragment, and every Rating Version that later
   re-points to "the latest" inherits it. Two routes make the intent explicit: *new* is
   refused on a clash, and *revise* is refused on an unknown slug. The Regression Suite does
   not have this problem, because its registry is unique per algorithm
   (`regression_suites.py:8-12`), so its one route cannot collide by name.
5. **`00` FR-4's `parent_id`.** No column. The predecessor of `@n` is `@n-1` under ID-2's
   per-slug numbering, as it is for Rating Algorithm and Rate Table Version rows, which carry
   none either (PL-1278 DP-S1-2's note). This record does not widen that existing gap and
   does not rule on it.

### DP-S1-3 — option (a): reuse `03` §5.1's codes

A cycle is `RATING_GRAPH_CYCLIC`. A consumed name that nothing produces, or an unproduced
output port, is `RATING_GRAPH_UNRESOLVED_REF`. **An output port whose producing step's type is
incompatible is `RATING_TYPE_MISMATCH`** (added by DP-S1-4 below; `03` §5.1 already owns it,
`03:772`). Any other shape refusal is `VALIDATION_FAILED`: a duplicate `step_id`, a
`sub_graphs` field (DP-4), an `input` or `output` step, or an empty change note. An unknown
`slug@version` is `NOT_FOUND`, a lost numbering race is 409 `VALIDATION_FAILED`, and a
create on an existing slug is 409 `VALIDATION_FAILED`. No new codes: the `instance` path
already names the artifact.

### DP-S1-4 — option (a), with FR-227's result-type check at create

**This departs from the prepared recommendation and the planner's (a) in one check.** Both
tested (a) against FR-212's clauses only. **FR-227 (`03:113`) also binds at save:** "Every
step declares its result type, and type compatibility is checked **at save time**." A
sub-graph's steps are steps. Deferring its type check to compile would breach FR-227 for
every fragment, so:
1. **At create, in Slice 1:** the shape invariants (FR-212: cycles, orphaned steps,
   undefined references, inside the fragment and against its ports), **and FR-227's
   result-type compatibility**. Each output port's declared type is checked against its
   producing step's result type. This is the check `_check_result_types`
   (`compile.py:114-139`) already makes against an algorithm's declared outputs. It is
   context-free and needs no parent. Slice 1 reuses that logic through a fragment entry point
   in `pricing-core`, never a copy (`CLAUDE.md` §2's rule against defining a thing twice
   applies to checks as much as to shapes). This brings `pricing-core` into Slice 1, which the
   planner preferred to avoid. FR-227 decides it.
2. **At compile, on the inlined algorithm, in Slice 2:** the other four checks —
   determinism (FR-216, which names no moment), division guards (FR-274), scale cap (FR-275)
   and vocabulary (FR-276). Each of the last three names bundle compilation itself (FR-240,
   `03:137`). A fragment with a non-deterministic expression is therefore saved and refused
   when any algorithm that mounts it is compiled, and Slice 2's gate proves that refusal
   red-first.
3. **This is not a breach of "rejected at save time".** FR-212's save-time clauses and
   FR-227's are enforced at create. The four deferred checks are compile-time by their own
   requirements.

## What it obliges

- **This commit:** this record only. No spec text changes here, because PL-1254 and PL-1278
  schedule each spec change in the slice that builds it ("The spec change first" in each
  Task), and a spec describing a pin, a route or a port before its slice would state
  something false at its own tree.
- **PL-1254 and PL-1278 (the planner's files, not edited here):** the "Resolved by" cells of
  DP-1, DP-3, DP-4 and DP-S1-1 to DP-S1-4 cite this record once it is minted. Two changes
  against the plans as written: **DP-S1-4's FR-227 check at create**, which brings
  `pricing-core` into Slice 1 (PL-1278 §Scope, `:183` and `:273`, say it gains no code), and
  **DP-1's structural-diff limb**, which PL-1254 Task 2 does not list.
- **WK-1250 Slice 1 (PL-1278):** in its spec change, `03` §2's term, §4's data contract
  (DP-3 items 1-2 ports, DP-4, the change note), §5.1's four routes (DP-S1-2, with DP-S1-1's
  permissions and DP-S1-3's codes), and `06`'s catalogue text (DP-S1-1 item 3). Its code
  holds the create-time checks of DP-S1-4 item 1.
- **WK-1250 Slice 2 (PL-1254 Task 2):** `03` §4.3's FR-20 restatement and `sub_graph` in
  `_MATURITY_CHECK_EXEMPT` with its tripwire (DP-1 item 5); FR-219's widening and its limb of
  the diff, if WK-673's diff has landed (DP-1 item 3); DP-3 items 3-5; and DP-S1-4 item 2.
- **WK-673:** if its structural diff lands after Slice 2's pin, it covers `Pins.sub_graphs`
  (DP-1 item 3). The lead carries this to WK-673's plan.

## Acceptance — the violation that must become detectable

Each is shown failing on deliberately broken input (`CLAUDE.md` §13), in the slice named.
- *Slice 1:* a fragment whose output port's declared type is incompatible with its
  producing step's result type is refused at create with `RATING_TYPE_MISMATCH` (FR-227).
- *Slice 1:* a fragment carrying `sub_graphs` is refused at create with `VALIDATION_FAILED`
  (DP-4).
- *Slice 1:* `POST /api/v1/sub-graphs` on an existing slug is refused with 409, and
  `POST /api/v1/sub-graphs/{slug}/versions` on an unknown slug with `NOT_FOUND` (DP-S1-2).
- *Slice 2:* a parent that consumes a port output its mount does not map is refused at save
  with `RATING_GRAPH_UNRESOLVED_REF`, and one that consumes a mapped output is accepted
  (DP-3 item 4).
- *Slice 2:* a fragment's internal name equal to a parent name does not rewire the parent
  after inlining. A test with a deliberate clash shows the parent value unchanged (DP-3
  item 3).
- *Slice 2:* a fragment with a non-deterministic expression, saved at create, is refused
  when a mounting algorithm is compiled (DP-S1-4 item 2).
- *Whichever of Slice 2 and WK-673 lands second:* two Rating Versions that differ only in a
  sub-graph pin produce a structural diff that names the re-point and the inner step
  changes. With the limb removed, the test fails (DP-1 item 3).
- *Slice 2:* the tripwire fails when a `status` column is added to the sub-graph table
  (DP-1 item 5).
