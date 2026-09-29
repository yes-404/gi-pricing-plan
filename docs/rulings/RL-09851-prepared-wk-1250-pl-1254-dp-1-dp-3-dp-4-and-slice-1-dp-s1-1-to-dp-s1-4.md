---
id: RL-9851
family: ruling
title: PREPARED, NOT RULED — WK-1250, PL-1254 DP-1, DP-3 and DP-4, and Slice 1's DP-S1-1 to DP-S1-4
status: draft                  # PREPARED, NOT RULED — see the banner; RL's §1.2 subset has no draft (reported to the lead)
created: 2026-09-30
owner: decision-maker
tree: aa14e90dd77c7461aa35cc6461557b129959463f
phase: P2
work: WK-1250
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1254, FR-217, FR-20, FR-1186]
---

# RL-9851 (working id) — PREPARED, NOT RULED: WK-1250, PL-1254 DP-1, DP-3, DP-4 and DP-S1-1 to DP-S1-4

> **Nothing in this record is ruled.** It was prepared at medium effort, under the
> maintainer's decision by delegation (lead channel, 2026-09-30 00:42 BST, "the DM PREPARES
> the blocked rulings"). It carries evidence, options and **provisional** recommendations
> only. Do not rely on it.
> - No slice may activate on it: SL for WK-1250 Slice 1 stays `draft`.
> - No plan's decision-point row is resolved by it.
> - No spec is amended by it.
>
> The ruling is a later pass at effort high, which re-reads this record and then confirms or
> revises it.

## Evidence

**Trees.**
- Specs and code: `origin/main` at `aa14e90dd77c7461aa35cc6461557b129959463f`.
- Slice 1 leaf plan (working id 9820, PR #929): `origin/wk1250-s1-leaf` at
  `a706430671bef6592930110e1a392dab4b8f7646`, file
  the one plan file that branch adds under `docs/plans/` (slug `wk-1250-slice-1-the-sub-graph-artifact-leaf-plan`).

**Where the questions are.**
- The map plan is `docs/plans/PL-01254-wk-1250-sub-graph-composition-and-mta-cancellation-pricing-map-plan.md`.
  Its rows are DP-1 at `:210`, DP-2 at `:211`, DP-3 at `:212` and DP-4 at `:213`.
- The leaf plan's rows are DP-S1-1 to DP-S1-4 at `:334-337`.
- The leaf plan is written on the map's recommendations DP-1 (b), DP-3 (a) and DP-4 (a)
  (`:326-331`), and names every step that changes if a ruling differs.
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

**Stale in the leaf plan.** It read its tree at `25b0ead2`, before #933. Its `models.py`
lines are 6 lower than at `aa14e90d` (for example `RatingAlgorithmRow` is now `:1926`), and
the migration head is now `d7e2a9b5c418`, not `a71c3e95d204`. The plan's re-point procedure
covers the second point, but both premises are stale as written.

## DP-1: is a sub-graph version a Governed Artifact?

| | Option | For | Against |
|---|---|---|---|
| (a) | Its own approval: a `06` §3.3 row, a §4.2 `sub_graph` policy, and a maturity check | Every change is approved on its own | An approval path and a gate for an artifact that prices nothing until a Rating Version pins it. It departs from both ungoverned precedents (Rate Table Version, Rating Algorithm). |
| (b) | Not governed on its own, like a Rate Table Version. Its change reaches approval inside the pinning Rating Version's evidence, and each version carries a change note | Matches FR-1186 and RL-859. There is one approval per change: the act `06` already approves. | Needs `sub_graph` in `_MATURITY_CHECK_EXEMPT`, and a clarification of the FR-20 invariant at `03:400-401`. |
| (c) | Governed only as a purpose (MTA or cancellation) sub-graph | — | Splits one artifact kind by its use. |

**Provisional: (b), as the planner recommends, with two conditions the planner did not state.**

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

## DP-3: how does a sub-graph connect at its mount point?

| | Option | For | Against |
|---|---|---|---|
| (a) | An explicit port contract: named inputs and outputs, a parent→port map, and inlined node ids namespaced by mount point | A mismatched mount is refused at compile time, and the trace stays attributable (FR-258) | New contract surface in `model-schema` |
| (b) | Splice: node ids are copied into the parent and wired by name | Least new shape | A name clash becomes a silent rewire, which is a mispricing path |
| (c) | A separate ZEN evaluation per sub-graph | Isolation | Not the inlining FR-217 names, and it adds a second evaluation to scoring |

**Provisional: (a), as the planner recommends, with one addition.** The contract must also
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

**Provisional: (a), as the planner recommends.** The refusal should be a named shape
invariant in `model-schema`, so that DP-S1-4 (a) covers it at create time.

## DP-S1-1: permission

| | Option | For | Against |
|---|---|---|---|
| (a) | `rating:write` for the writes and `rating:read` for the reads, through `requires()`. No new permission or scope. | Follows the precedent of the Regression Suite rows. Authoring is a workspace-wide act. | A principal scoped to one Rating Algorithm (`06` FR-345) cannot even read a sub-graph that its algorithm mounts. |
| (b) | New `sub_graph:read` and `sub_graph:write` | Separate grant | Adds catalogue entries (RL-1236) for a separation nobody has asked for |
| (c) | (a), plus `ScopeType.SUB_GRAPH` | Fine-grained | A scope with no consumer before a designer exists |

**Provisional: (a).** State the scoped-principal consequence in the ruling as accepted. Also
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

**Provisional: (a)'s single table, with (d)'s single create route.** This departs from the
planner in the route count only. One act gets one route, and it matches the most similar
existing artifact. The high pass should check that `00` §5.1's URL rules (`00:314-321`, "Sub-
resources nest one level maximum") and the §5.1 table in `03` accept creating a slug's first
version through `/{slug}/versions`. The Regression Suite row already does this.

## DP-S1-3: error codes

| | Option | For | Against |
|---|---|---|---|
| (a) | Reuse `RATING_GRAPH_CYCLIC`, `RATING_GRAPH_UNRESOLVED_REF` (`03:771-779`), `VALIDATION_FAILED` (also 409 on a race, as at `platform/regression_suites.py:69`), and `NOT_FOUND` | Clients already handle them. The `instance` path names the artifact. | A client cannot tell a sub-graph refusal from an algorithm refusal by code alone |
| (b) | New `SUB_GRAPH_*` codes owned by `03` §5.1 | Distinct codes | They differ only by artifact |

**Provisional: (a), as the planner recommends.** DP-4 (a)'s depth refusal then carries
`VALIDATION_FAILED`.

## DP-S1-4: create-time validation depth

| | Option | For | Against |
|---|---|---|---|
| (a) | Shape invariants only, in `model-schema`. The five expression checks run on the inlined algorithm at compile (Slice 2). | Keeps `pricing-core` out of Slice 1 | A non-deterministic fragment is saved and refused only when a mounting algorithm compiles, and Slice 2 must prove that refusal |
| (b) | Generalise the helpers to run the context-free checks at create | Stricter | Touches `compile.py`, which Slice 2 rewrites |
| (c) | Wrap the fragment in a synthetic algorithm | — | The result-type checks run against an invented input contract |

**Provisional: (a), as the planner recommends.** It fits FR-212's actual clauses: FR-212
(`03:81`) requires *cycles, orphaned steps and undefined references* to be rejected at save,
and those are shape invariants that (a) keeps at create. The expression checks are not among
FR-212's clauses. The ruling should say so explicitly, so that (a) is not later read as a
breach of "rejected at save time".

## DP-2 (not prepared here)

DP-2 blocks only Slices 2 and 3, and it shares no evidence with the rows above beyond
`SubGraphRef` (`rating.py:340-350`). It is left for its own preparation.

## Ruled

**Nothing.** This section is held for the high-effort pass.

## What it obliges

**Nothing yet.** If the high pass confirms the provisional answers, it obliges the following.
- **DP-1:**
  - a spec change adding sub-graph diffs to `06` §3.3's Rating Version evidence and widening
    FR-219;
  - the FR-20 invariant clarification at `03:400-401`, covering all three exemptions;
  - `sub_graph` added to `_MATURITY_CHECK_EXEMPT`;
  - a named slice that builds the diff.
- **DP-3:** the port contract, including the parent's view of port outputs, specified in `03`
  §4 before Slice 1 builds the shape.
- **DP-S1-1:** the catalogue text edits at `06:265` and `06:287-288`.
- **DP-S1-2:** `03` §5.1 route rows in the Regression Suite form.
- **The leaf plan (working id 9820):** re-read at the ruling tree, because its `models.py`
  lines and migration head are stale.

## Acceptance — the violation that must become detectable

**Not set, because nothing is ruled.** Under the provisional answers:
- A sub-graph re-pointed between two Rating Versions appears in the second one's approval
  evidence. If it is absent, a test fails.
- A sub-graph that mounts a sub-graph is refused at create with `VALIDATION_FAILED`.
- A parent that consumes a port output its mount does not declare is refused at save with
  `RATING_GRAPH_UNRESOLVED_REF`.

Each must be shown failing on a deliberately broken input (CLAUDE.md §13).
