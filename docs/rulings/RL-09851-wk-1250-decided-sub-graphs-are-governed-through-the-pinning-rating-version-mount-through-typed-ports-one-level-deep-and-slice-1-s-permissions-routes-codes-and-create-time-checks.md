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

Citations in this section were read at `7c354305`. **Every "built", "exists", "absent" or
"unbuilt" claim below rests on a reading of the module that owns the concept.** The
"Presence and absence, as verified" table records each one: the symbol and file:line for a
presence, and for an absence the command run and the owning module read. *(Amended after
`auditor-plans`' audit of `8bad4f3d`. That head called the structural diff "unbuilt" on the
strength of a grep for names the code does not use. It is built. See DP-1 item 3.)*

### Presence and absence, as verified

| Claim | Verdict | How it was verified at `7c354305` |
|---|---|---|
| FR-219's structural diff | **built** | `AlgorithmDiff` (`packages/model-schema/src/model_schema/rating.py:539`) and `diff_algorithms(old, new)` (`:569`), read in full. It diffs two **algorithm** versions: steps added, removed and changed field by field, table and lookup references re-pointed, and the input contract and outputs. It is served by `diff_between` (`backend/src/app/platform/rating_algorithms.py:135-141`). It has no sub-graph limb: it never reads `sub_graphs`. |
| The persisted `structural_diff` evidence | **unbuilt** | `RatingVersionEvidence.structural_diff_blob` (`rating.py:125`) is `str \| None = None`. The owning module, `backend/src/app/platform/rating_versions.py`, was read at its evidence write in `submit_for_review` (`:250-300`). It writes only `golden_quotes` and `regression_suite_run_id` (`:294-298`). `git grep -n 'structural_diff_blob' 7c354305 -- backend/src 'packages/*/src'` prints only `rating.py:125`. Its owner is WK-673 (`RL-1184` E4; `RL-1290`). |
| A sub-graph pin on a Rating Version | **absent** | `Pins` (`rating.py:63-77`), read: `rate_tables`, `models`, `reference_tables`, `custom_objectives`, and nothing else. PL-1254 Task 2 adds `Pins.sub_graphs`. |
| `SubGraphRef`'s fields | **present** | `rating.py:340-350`: `ref: ArtifactRef` and `mount_point: str`, and nothing else. |
| `compile_bundle` reading sub-graphs | **absent** | `compile_bundle` (`packages/pricing-core/src/pricing_core/rating/compile.py:425-492`), read in full: `all_refs` (`:467-472`) is the four `Pins` lists, and the maturity loop is `:473-481`. `git grep -n 'sub_graphs' 7c354305 -- packages/pricing-core/src/pricing_core/rating/compile.py` → rc 1. |
| `compile_bundle` checking that each step's own reference is pinned | **absent** | The same reading. It refuses a version with no `algorithm_ref` or no `pins` (`RATING_VERSION_UNPINNED`, `:434-443`), and resolves **only the pins**. It never compares a `table`, `lookup` or `model_call` step's reference with them. At scoring, `runtime.py`'s `_decision_table_node` reads `payloads.get(ref)` for a `table` step (`packages/pricing-core/src/pricing_core/rating/runtime.py:190-230`). This is an observation about algorithms, reported to the lead as a candidate finding and not ruled here. For fragments it is ruled: DP-1 item 6 (i). |
| A route or code path that changes a Rating Version's pins | **absent** | The owning API module, `backend/src/app/api/models.py`, read at its rating-version routes (`:1113` GET list, `:1139` GET one, `:1161` POST create, `:1189` POST submit, `:1233` POST compile, and `:1265`-`:1328` regression runs). There is no PUT or PATCH. `git grep -n 'rating-versions' 7c354305 -- backend/src/app/api` finds no other router. The owning service, `backend/src/app/platform/rating_versions.py`, was read: `create_rating_version` (`:202`) builds the row with no `pins` (`:226-234`), and the file's only `pins` code is the read at `:113`. `git grep -n -E '\bpins\b' 7c354305 -- backend/src` finds no other writer of the `RatingVersionRow.pins` column (`models.py:1912`). |
| A deploy route | **absent** | `git ls-tree --name-only 7c354305 backend/src/app/api/` lists no deployments module, and `git grep -n -i deploy 7c354305 -- backend/src/app/api` finds no route. `backend/src/app/api/score.py:133-139` says "`live` is a property of a Deployment (FR-238), which is WK-674's". PL-1237 Task 2 (`docs/plans/PL-01237-…md:768-790`) builds `POST /api/v1/environments/{env}/deployments`. |
| A spec constraint on sub-graph nesting | **absent** | The spec suite owns it. `git grep -n -i -E 'sub-graph\|sub_graph\|subgraph' 7c354305 -- docs/specs` gives six hits, all in `03` (`:63`, `:86`, `:87`, `:276`, `:1046`, `:1171`). Each was read: the Quote Context term, FR-217, FR-218, the §4.1 example, the DAG designer view, and `OQ-617`. None of them constrains nesting. |
| `06` FR-385's `expedited` in the approval policy | **absent** | The owning module, `packages/model-schema/src/model_schema/approvals.py`, was read at `ApprovalPolicy` (`:125`). Its fields (`:128-135`) are `policies` and `submitter_may_approve`, and it is `extra="forbid"`. `git grep -n -i expedited 7c354305 -- packages backend/src` → rc 1. |
| `sub_graph` is a valid reference type | **present** | `ARTIFACT_TYPES` (`packages/model-schema/src/model_schema/refs.py:20-28`) includes `"sub_graph"`. |
| A live-code test that the exemption is read | **present, for `rating_algorithm`** | `test_a_rating_algorithm_pin_compiles_regardless_of_status` (`packages/pricing-core/tests/test_rating_compile_bundle.py:193`) and `test_the_algorithm_maturity_check_would_be_caught_if_removed` (`:213`). The status-column tripwires are `test_rate_table_version_row_has_no_status_column` and `test_rating_algorithm_row_has_no_status_column` (`backend/tests/test_rating_version_compile.py:247`, `:269`). |
| The interim purpose guard | **present** | `_check_purpose_mount`, `packages/pricing-core/src/pricing_core/rating/score.py:393-405`. Its docstring says `compile_bundle` never reads `sub_graphs`. Not `backend/src/app/api/score.py`, which is a different module. |
| The maturity exemption | **present** | `_MATURITY_CHECK_EXEMPT = frozenset({"rate_table", "rating_algorithm"})`, `compile.py:314`, applied at `:453` and `:475`. |
| `requires()` admits only workspace-wide grants | **present** | `requires` (`backend/src/app/api/authz.py:54-76`) calls `rbac.require_permission` with no `resource`. `_covers` (`backend/src/app/platform/rbac.py:205-217`) returns `False` for a scoped assignment when `resource is None`. |
| A `parent_id` on the rating artifacts | **absent** | `git show 7c354305:backend/src/app/db/models.py \| grep -n parent_id` → one hit, `:824`. That is outside `RatingAlgorithmRow` (`:1926`) and `RateTableVersionRow` (`:1984`). |
| The Regression Suite registry is unique per algorithm | **present** | `RegressionSuiteRow.__table_args__` (`models.py:2060-2065`): `UniqueConstraint("workspace_id", "algorithm_slug", name="uq_regression_suites_algorithm")`. |

### DP-1 — option (b): a sub-graph version is not a Governed Artifact; its change is approved inside the pinning Rating Version

1. **No approval of its own.** A Sub-graph Version has no status and no approval lifecycle,
   just as a Rate Table Version (`03` FR-1186) and a Rating Algorithm (`RL-859`) have none.
   It is not added to `06` §2's Governed Artifact list (`06-governance.md:64`). It gets no
   `06` §3.3 row and no §4.2 `DEFAULT_POLICY` entry. Each version is immutable once created
   and carries a required change note, as FR-229 requires of a Rate Table Version (`03:120`).
2. **The mechanism, which routes the change through approval rather than around it.** The
   change reaches approval through the Rating Version that pins it (PL-1254 Task 2 adds the
   pin). That Rating Version's approval sees the change in three ways:
   - **The structural diff.** FR-219 (`03:88`) is widened: the diff also lists **each
     sub-graph mount or pin added, removed or re-pointed**, and for a re-point it carries
     **the step-level diff between the two sub-graph versions**. It stays inside the existing
     `structural_diff` evidence kind, so no new key is added to `EVIDENCE_FLOOR`
     (`approvals.py:106`) or `06` §4.2.
   - **The regression suite.** It is run per Rating Version (`03` FR-257, `03:174`).
   - **The dislocation run.** It is also run per Rating Version (`03` FR-257). So every Rating
     Version that adopts a changed sub-graph shows the change's effect on its own golden
     quotes and its own portfolio.
3. **Who builds which half.** The table above splits the diff into a built computation and an
   unbuilt persistence:
   - **Computing the sub-graph limb is WK-1250 Slice 2's.** Widening `AlgorithmDiff` and
     `diff_algorithms` (`model-schema`) to cover sub-graph mounts and pins, with the inner
     step diff, lands **with the pin, in Slice 2**. Slice 2 does this whatever WK-673's state
     is, because it creates the thing to be diffed.
   - **Persisting the diff as evidence is WK-673's.** WK-673 writes the `structural_diff`
     evidence blob at submission and registers its verifier (`RL-1184` E4). Its obligation is
     to persist the **whole** diff the computation returns, never a hand-picked subset of its
     fields. Then the sub-graph limb reaches the approver without WK-673 naming it.
   - **"Whichever lands second" on this split.** If Slice 2 lands first, WK-673 persists a
     diff that already carries the limb, and WK-673's persistence test includes a sub-graph
     re-point. If WK-673 lands first, Slice 2's widening flows into the persisted blob, and
     Slice 2's test asserts the limb **in the persisted evidence**, not only in the function's
     return value.
   - **The maintainer's condition.** Before Slice 2 is dispatched, both WK-673's plan and
     PL-1254 Task 2 carry this limb. The first is the lead's to route, the second the
     planner's.
4. **FR-1186's revisit trigger is met by design, and (b) still holds.** A sub-graph exists to
   be shared (FR-217's `ncd-ladder`). That is FR-1186's revisit condition: "pinned by more
   than one Rating Version in practice". But sharing multiplies reviews and loses none. Each
   adopting Rating Version is approved against its own predecessor, with the re-point in its
   diff and its own regression and dislocation evidence. A sub-graph version that no approved
   Rating Version pins prices nothing (item 6).
5. **FR-20 and the maturity gate.** `03` §4.3's invariant "every pin resolves to an artifact
   whose status is `approved` or better (FR-20)" (`03:399-401`) already disagrees with the two
   exemptions in force (`compile.py:314`). **A future spec change, in Slice 2**, restates it by
   class, not by list: *every pin to an artifact that has an approval lifecycle resolves to
   `approved` or better (FR-20); a pin to an artifact that has none (Rate Table Version,
   Rating Algorithm, Sub-graph Version) is governed by the pinning Rating Version's own
   approval.* In the same slice, `sub_graph` joins `_MATURITY_CHECK_EXEMPT` with a comment
   citing this record. **That alone does nothing** unless the maturity loop reads sub-graph
   pins, so Slice 2 also adds `Pins.sub_graphs` to `all_refs` (`compile.py:467-472`). See
   guard (iv).
6. **The approval guards that make (b) safe. Each is built and proved red on broken input**
   (the maintainer's G1 to G4, accepted as required). Each names **one** owner.
   - **(i) G1 — a sub-graph reaches scoring only through the Rating Version's pins.**
     *Owner: WK-1250 Slice 2.* `compile_bundle` refuses a `SubGraphRef` whose version is not
     in the Rating Version's `Pins.sub_graphs`, and never inlines it. Every artifact
     reference inside an inlined fragment — `table`, `lookup` and `model_call` — resolves
     **only against the pinning Rating Version's pins**. A fragment reference not among them
     is refused at compile. It is never left for scoring to meet as a missing payload.
     - This reference check runs over the whole inlined algorithm. So it also covers the
       algorithm's own steps, which today are not checked at compile (the table above). If
       the lead routes that algorithm-level gap elsewhere, Slice 2 still covers the
       fragment's steps.
     - Because a fragment's `model_call` can reach a model only through a pin, FR-240's "no
       unapproved custom objective transitively reachable" sees every objective a fragment
       can reach. That check's owner is the rating Work that PL-1276 DP-2 (b) moves FR-240
       clauses (4) to (6) to (`PL-1276:166`, `:234`: "WK-1178, or a Work the maintainer
       names"). This record does not move it.
     - *Stated, not widened:* `POST /api/v1/score/compare` may name any compiled version,
       `draft` included (`03:760`). That is the existing rule for every pin, it prices nothing
       live, and this ruling does not change it.
   - **(ii) G2 — a change of pin is a new Rating Version that needs its own approval.**
     *Owner: WK-1250 Slice 2*, the slice that first gives `Pins` a sub-graph list. Pins are
     fixed once a Rating Version leaves `draft` (`00` FR-4; `03` FR-237), and an approval is
     pinned to the exact version (`06` FR-356). **Today this is vacuous.** No route or code
     path writes a Rating Version's pins at all (the table above). Slice 2 proves the guard
     over every pin write path at its own tree: a change to the pins of a non-`draft` Rating
     Version is refused, and a re-point is only possible as a new version, whose own
     submission carries the diff.
   - **(iii) G3 — a sub-graph is never deployed without an approved Rating Version.**
     *Owner: WK-674 Slice 2*, one owner, for three reasons:
     - it builds the only deploy route, `POST /api/v1/environments/{env}/deployments`, which
       "applies the `prod` approval (FR-267)" (`PL-1237` Task 2, `:768-790`);
     - FR-267 (`03:195`) gives the structure: "A **Deployment** binds an `approved` Rating
       Version to an Environment";
     - `sub_graph` is already a valid reference type (`refs.py:20-28`), so the negative test
       needs nothing from WK-1250 and is provable at WK-674 Slice 2's own tree, whichever Work
       lands first.

     The test: a deploy request naming a `sub_graph` reference, or any reference that is not
     a `rating_version`, is refused. **Unprovable today:** there is no deploy route in
     `backend/src` (the table above).
   - **(iv) G4 — the exemption is read, and a status column trips it.** *Owner: WK-1250
     Slice 2.*
     - (a) `Pins.sub_graphs` joins `all_refs` (`compile.py:467-472`), so the maturity loop
       actually resolves sub-graph pins.
     - (b) A live-code test shows the exemption is read, in the form of
       `test_the_algorithm_maturity_check_would_be_caught_if_removed`
       (`packages/pricing-core/tests/test_rating_compile_bundle.py:213`). With `sub_graph`
       removed from `_MATURITY_CHECK_EXEMPT`, a sub-graph pin is refused.
     - (c) A tripwire in the form of `test_rate_table_version_row_has_no_status_column`
       (`backend/tests/test_rating_version_compile.py:247`) fails the day a `status` column
       is added to the sub-graph table, and names this record.

### DP-3 — option (a): an explicit, typed port contract, with the fragment's own names namespaced

1. **The sub-graph declares its ports.**
   - **Output ports** reuse `AlgorithmOutput` (`rating.py`: `name`, `type: RatingResultType`,
     `required`), so the float refusal and FR-227's result-type vocabulary are the ones
     algorithms already use.
   - **Input ports** have a `name` and a `RatingResultType`, because the value that feeds one
     is a parent step's result.
   - Slice 1 may not define a second result-type vocabulary.
2. **`mount_point` is the mount's own identifier, not a parent step.** It is unique among the
   parent's `step_id`s and its other mounts. It namespaces the inlined steps and attributes
   them in the trace (FR-258). The `03:276` example names `"s_ncd"` with no step called that,
   which fits this reading, and it is left as it is.
3. **The mount maps names explicitly.** The parent's mount maps each input port to a parent
   value, and each output port to the parent name it produces. On inlining, **every name
   internal to the fragment is namespaced by the mount point**. Only the mapped port names
   meet the parent's namespace, so a fragment's intermediate name can never silently rewire a
   parent value (option (b)'s failure).
4. **The parent's save-time invariants see the mount.** `03` §4.1's invariants
   (`03:280-282`, FR-212) treat a mount as a node:
   - its mapped outputs are *produced* by it;
   - its mapped inputs are *consumed* by it;
   - acyclicity and "produced by exactly one upstream step" count it.

   Without this, a parent that consumes a value only its mount produces is refused as
   unresolved.
5. **Where each half lands.** The sub-graph's ports are part of Slice 1's shape. Two things
   land in Slice 2, with the pin and the inliner: the mount's port map on `SubGraphRef`
   (today `ref` and `mount_point` only, per the table above), and item 4's invariants. Until
   then nothing mounts: `compile_bundle` never reads `sub_graphs`, and
   `packages/pricing-core/src/pricing_core/rating/score.py`'s `_check_purpose_mount`
   (`:393-405`) is the interim guard. Checking a mount's port map against the pinned
   version's declared ports is a compile-time check, in Slice 2.

### DP-4 — option (a): depth 1

A sub-graph mounts nothing. The Slice 1 shape has **no `sub_graphs` field** and is
`extra="forbid"`, so a fragment carrying one is refused by construction at create, with
`VALIDATION_FAILED` (DP-S1-3). Slice 2's compiler refuses a nested mount again, by cause, in
case a fragment reaches it by another path. Nesting later is a spec change: no requirement or
workflow in `00`, `03`, `06` or `07` needs it (prepared evidence, "Nesting").

### DP-S1-1 — option (a): `rating:write` and `rating:read`, workspace-wide

1. The two write routes require `rating:write` and the two read routes `rating:read`, through
   `requires()`. No new permission and no new scope type. This is the precedent of `03`
   §5.1's Regression Suite rows (`03:756-757`).
2. **The scoped-principal consequence is accepted.** `requires()` admits only a
   workspace-wide assignment (the table above). So a principal scoped to a named Rating
   Algorithm (`06` FR-345) can neither read nor author a sub-graph through these routes.
   - *Authoring:* that is correct. Any algorithm in the workspace may mount a sub-graph, so
     authoring one is a workspace-wide act.
   - *Reading:* compile and score resolve a pinned sub-graph through the artifact resolver,
     not these routes, so a scoped principal's compile is not blocked.
   - A designer view that shows a scoped author a mounted fragment (WK-675) is a later spec
     change, if one is needed.
3. **The catalogue text will be widened, not renamed** (`RL-1236` governs the names). **This is
   a future spec change, made in Slice 1's spec change, and not made by this record.** The
   `rating:read` row (`06:265`, "Reading Rating Algorithms, Rate Tables, Rating Versions and
   scoring traces") and the `rating:write` note (`06:287-288`) will name sub-graphs.
   Neither names regression suites at `7c354305` either, so the same edit adds them.

### DP-S1-2 — option (a), as the planner recommends: one table, server numbering, two create routes

**This departs from the prepared recommendation**, which preferred the Regression Suite's
single create route.
1. **Storage.** One table, `sub_graph_versions`, with one row per version and the content as
   JSONB. It is unique on `(workspace_id, slug, version)`. There is no registry table, because
   a sub-graph has no container-level state.
2. **Numbering.** The server assigns the current maximum plus one. The unique constraint turns
   a race into `VALIDATION_FAILED` 409, in the form of `objectives.py:229-236` and
   `regression_suites.py`'s `_next_version`. The numbers are gap-free and never reused (`00`
   ID-2).
3. **Routes**, all within `00` §5.1's one-level nesting rule:
   - `POST /api/v1/sub-graphs` creates version 1 of a new slug, and returns 409 if the slug
     exists.
   - `POST /api/v1/sub-graphs/{slug}/versions` creates the next version, and returns
     `NOT_FOUND` for an unknown slug.
   - `GET /api/v1/sub-graphs/{slug}@{version}` reads one version.
   - `GET /api/v1/sub-graphs/{slug}/versions` lists them, cursor-paginated.
4. **Why two create routes.** A sub-graph slug is a free name in the workspace. With a single
   create route, an author who creates `ncd-ladder` without knowing one exists silently
   publishes version 5 of someone else's fragment. Two routes make the intent explicit: *new*
   is refused on a clash, and *revise* is refused on an unknown slug. The Regression Suite
   does not have this problem: its registry is unique per algorithm (the table above), so its
   one route cannot collide by name.
5. **`00` FR-4's `parent_id`.** No column is added. The predecessor of `@n` is `@n-1` under
   ID-2's per-slug numbering, as for Rating Algorithm and Rate Table Version rows, which carry
   none either (the table above). This record does not widen that gap and does not rule on
   it.

### DP-S1-3 — option (a): reuse `03` §5.1's codes

| Refusal | Code |
|---|---|
| A cycle | `RATING_GRAPH_CYCLIC` |
| A consumed name nothing produces, or an unproduced output port | `RATING_GRAPH_UNRESOLVED_REF` |
| An output port whose producing step's type is incompatible (DP-S1-4) | `RATING_TYPE_MISMATCH`, which `03` §5.1 already owns (`03:772`) |
| Any other shape refusal: a duplicate `step_id`, a `sub_graphs` field (DP-4), an `input` or `output` step, or an empty change note | `VALIDATION_FAILED` |
| An unknown `slug@version` | `NOT_FOUND` |
| A lost numbering race, or a create on an existing slug | 409 `VALIDATION_FAILED` |

No new codes are added, because the `instance` path already names the artifact.

### DP-S1-4 — option (a), with FR-227's result-type check at create, through a refactor that lands in Slice 1

**This departs from the prepared recommendation and from the planner's (a) in one check.**
Both tested (a) against FR-212's clauses only. **FR-227 (`03:113`) also binds at save**:
"Every step declares its result type, and type compatibility is checked **at save time**." A
sub-graph's steps are steps. Deferring their type check to compile would breach FR-227 for
every fragment.

1. **The check cannot be reused as it stands.** `_check_result_types`
   (`compile.py:114-139`) takes a `RatingAlgorithm`. It walks its `RatingOutputStep`s against
   `algo.outputs`, and gets producer types from `_producer_types` (`compile.py:84-103`),
   which types `RatingInputStep`s from `algo.input_contract` and `RatingExpressionStep`s from
   `result_type`. A fragment has neither input nor output steps (DP-S1-3 refuses both); it
   has ports. *(Corrected after the audit. `8bad4f3d` called the check "context-free", with
   "no parent" needed, and reusable as it stood.)*
2. **The refactor, which lands in Slice 1.** Slice 1 separates both functions' logic from
   their `RatingAlgorithm` input:
   - `_producer_types` becomes a function over the steps plus a mapping of already-typed names
     (the algorithm's input contract, or the fragment's input ports).
   - `_check_result_types` becomes a function over those producer types plus the declared
     outputs (the algorithm's `outputs`, reached through its output steps, or the fragment's
     output ports).
   - The algorithm path calls the new functions with the algorithm's own inputs and outputs,
     so its behaviour is unchanged. `validate_algorithm`'s tests in
     `packages/pricing-core/tests/test_rating_compile.py` pass unmodified.
   - One new public entry point checks a fragment's output ports, and Slice 1's create path
     calls it.
   - `_compatible` (`compile.py:106-111`) is called as it is.
   - Slice 2's inliner builds on this refactor and does not undo it. The inlined algorithm
     goes through the algorithm path.
3. **The ruled `pricing-core` write set for Slice 1** (for `RL-1263`'s comparison with WK-690
   Slice 1):
   - `packages/pricing-core/src/pricing_core/rating/compile.py`, limited to
     `_producer_types`, `_check_result_types` and one new public fragment entry point.
     `compile_bundle` and the other four checks are untouched.
   - `packages/pricing-core/tests/test_rating_compile.py`, for new tests only.

   No other `pricing-core` file is in the set. `PL-1268` (WK-690) names no `compile.py`
   (`git show 7c354305:docs/plans/PL-01268-…md | grep -c compile.py` prints `0`). Its
   `pricing-core` files are under `data/`, `modelling/`, `rating/runtime.py` and
   `safe_error.py`, so the two write sets do not meet on this evidence.
4. **Why this is not option (c).** Option (c) wraps the fragment in a synthetic
   `RatingAlgorithm`. It invents an input contract and output steps the fragment does not have,
   and then runs all five checks against that fiction. The refactor invents nothing. It runs
   **one** check, FR-227's, over the fragment's **own declared ports**. The prepared record's
   objection to (c), "result-type checks would pass or fail on fiction", therefore does not
   apply.
5. **Why this beats (a) alone.** (a) alone saves every fragment without FR-227's check, which
   breaches a numbered requirement that binds at save. The cost of meeting it is a bounded,
   behaviour-preserving refactor of two private functions in a file Slice 2 edits later.
   Slice 2 edits another region of that file, `compile_bundle`, and does so after Slice 1
   closes, since it depends on Slice 1. The two slices are never in the file at once.
6. **At compile, on the inlined algorithm, in Slice 2**, the other four checks run:
   - **determinism** (FR-216, which names no moment);
   - **division guards** — FR-274: "bundle compilation (FR-240) rejects an unguarded one";
   - **scale cap** — FR-275: "Bundle compilation checks that no rate table value, constant,
     or intermediate requires a decimal scale beyond `rust_decimal`'s limit";
   - **vocabulary** — FR-276: "Bundle compilation resolves every function name against the
     engine's real vocabulary".

   So a fragment with a non-deterministic expression is saved, and is refused when any
   algorithm that mounts it is compiled. Slice 2's gate proves that refusal red-first.
7. **This is not a breach of "rejected at save time".** FR-212's save-time clauses and
   FR-227's are both enforced at create. The four deferred checks are compile-time checks by
   their own requirements, or by none.

## What it obliges

- **This commit:** this record only. There is no spec text here. PL-1254 and PL-1278 schedule
  each spec change in the slice that builds it ("The spec change first" in each Task), and a
  spec that described a pin, a route or a port before its slice would state something false
  at its own tree.
- **PL-1254 and PL-1278 (the planner's files, not edited here):**
  - the "Resolved by" cells of DP-1, DP-3, DP-4 and DP-S1-1 to DP-S1-4 cite this record once
    it is minted;
  - PL-1278 carries **DP-S1-4's refactor and the Slice 1 `pricing-core` write set**. Today
    PL-1278 says `pricing-core` gains no code (§Scope, `:183` and `:273`);
  - PL-1254 Task 2 carries **DP-1 item 3's diff limb** and **DP-1 item 6's guards (i), (ii)
    and (iv)**, before Slice 2 is dispatched.
- **WK-673's plan (the lead routes it):** DP-1 item 3's persistence clause, before WK-1250
  Slice 2 is dispatched.
- **WK-674 Slice 2 (`PL-1237` Task 2; the lead routes it to the planner):** DP-1 item 6
  (iii), G3. The deploy route refuses a `sub_graph` reference, proved red.
- **The lead:** the algorithm-level observation in the table above (compile does not check a
  step's reference against the pins) is offered as a candidate finding. It is not ruled
  here.
- **WK-1250 Slice 1 (PL-1278):**
  - its spec change: `03` §2's term; §4's data contract (DP-3 items 1-2, DP-4, the change
    note); §5.1's four routes (DP-S1-2, with DP-S1-1's permissions and DP-S1-3's codes); and
    `06`'s catalogue text (DP-S1-1 item 3);
  - its code: the DP-S1-4 refactor and the create-time checks.
- **WK-1250 Slice 2 (PL-1254 Task 2):**
  - DP-1 item 5: the FR-20 restatement and the exemption;
  - DP-1 item 3: `diff_algorithms` widened;
  - DP-1 item 6: guards (i) G1, (ii) G2 and (iv) G4;
  - DP-3 items 3 to 5;
  - DP-S1-4 item 6.

## Acceptance — the violation that must become detectable

Each check is shown failing on deliberately broken input (`CLAUDE.md` §13), in the slice
named.

**Slice 1:**
- A fragment whose output port's declared type is incompatible with its producing step's
  result type is refused at create with `RATING_TYPE_MISMATCH` (FR-227). The existing
  `validate_algorithm` tests pass unmodified after the refactor.
- A fragment carrying `sub_graphs` is refused at create with `VALIDATION_FAILED` (DP-4).
- `POST /api/v1/sub-graphs` on an existing slug is refused with 409, and
  `POST /api/v1/sub-graphs/{slug}/versions` on an unknown slug with `NOT_FOUND` (DP-S1-2).

**Slice 2:**
- A parent that consumes a port output its mount does not map is refused at save with
  `RATING_GRAPH_UNRESOLVED_REF`, and one that consumes a mapped output is accepted (DP-3
  item 4).
- A fragment's internal name equal to a parent name does not rewire the parent after
  inlining. A test with a deliberate clash shows the parent value unchanged (DP-3 item 3).
- A fragment with a non-deterministic expression, saved at create, is refused when a
  mounting algorithm is compiled (DP-S1-4 item 6).
- `diff_algorithms` over two algorithms that differ only in a sub-graph mount or pin names
  the re-point and the inner step changes. With the limb removed, the test fails (DP-1
  item 3).
- G1: a `SubGraphRef` whose version is not in `Pins.sub_graphs` is refused at compile, and the
  bundle contains none of its steps. A fragment whose `table`, `lookup` or `model_call`
  reference is not among the Rating Version's pins is refused at compile.
- G2: a change to the pins of a non-`draft` Rating Version is refused, through every pin write
  path at Slice 2's tree.
- G4 (a) and (b): with `sub_graph` removed from `_MATURITY_CHECK_EXEMPT`, an unapproved-status
  sub-graph pin is refused. This proves the loop reads `Pins.sub_graphs`.
- G4 (c): the tripwire fails when a `status` column is added to the sub-graph table.

**Whichever of Slice 2 and WK-673 lands second:**
- The **persisted** `structural_diff` evidence of a Rating Version whose only change is a
  sub-graph re-point carries the limb (DP-1 item 3).

**WK-674 Slice 2:**
- G3: a deploy request naming a `sub_graph` reference, or any reference that is not a
  `rating_version`, is refused. This is unprovable before that slice, because no deploy route
  exists.
