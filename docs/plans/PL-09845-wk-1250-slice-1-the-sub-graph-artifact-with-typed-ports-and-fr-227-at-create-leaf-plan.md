---
id: PL-9845
family: plan
kind: leaf
title: WK-1250 Slice 1 — The sub-graph as a stored, versioned artifact, with typed ports and FR-227 at create (FR-217's artifact limb): leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: e9263283177e5e1c1205ba48d0e41c2a1483f83c
phase: P2
work: WK-1250
supersedes: [PL-1278]
superseded_by: ~
corrected_by: []
relates: [PL-1254, PL-1278, RL-1309, FD-1241, RL-1242, RL-1263, PL-1299, FD-1297, PL-1237, PL-1267, PL-1268]
---

# WK-1250 Slice 1 — The sub-graph as a stored, versioned artifact, with typed ports and FR-227 at create (FR-217's artifact limb): leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` (Tasks 2–6), `python-test` (every task), `fastapi-service` (Task 6) and `dev-commands` (the gate), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make a sub-graph a **stored, versioned, immutable artifact** that a later slice can pin and
inline:
- a `model-schema` shape with **typed input and output ports**;
- a table and four routes;
- create-time validation that includes **FR-227's result-type check**;
- an Audit Event on every write;
- a resolver for `sub_graph:slug@version`.

This slice does **not** pin, inline, compile or score a sub-graph (Slice 2), and it does not
touch FR-218's purpose mount (Slice 3).

**Why this plan supersedes PL-1278.** RL-1309 ruled PL-1278's open decision points and the map's
DP-1, DP-3 and DP-4. Its rulings change this slice's acceptance and write set:
- DP-3 (a) types the ports, which PL-1278 wrote as bare names;
- DP-S1-4 (a) puts FR-227's result-type check at create, through a `pricing-core` refactor that
  PL-1278 excluded ("`pricing-core` gains no import and no code", PL-1278:273);
- RL-1309's *Acceptance* adds four cases.

A plan is frozen by family (`document-ids.md` :49, :69; check 34; `CLAUDE.md` §2), and a
material acceptance or write-set change is carried by a superseding plan, not a delta. The
maintainer's entries in `to-lead.md`, the lead's local channel file, are:
- "2026-09-30 14:44:36 BST — DECISION: RL-1309's plan follow-ons are NOT in-place edits (plans
  are frozen as a family); use dispatch-record deltas";
- "2026-09-30 14:46:03 BST — confirmed: WK-1250 S1 gets a NEW leaf plan superseding PL-1278". The Work's scope is unchanged: FR-217's
artifact limb is still the only requirement this slice delivers.

**Architecture.** The closest precedent is the Rating Algorithm: one row per version, its
validated content stored as JSONB (`RatingAlgorithmRow`, `backend/src/app/db/models.py:1926-1954`),
and a thin router (`backend/src/app/api/rating_algorithms.py`) over a service module
(`backend/src/app/platform/rating_algorithms.py`). The sub-graph differs from it in four ways:
- every write records an Audit Event in the same transaction, after
  `backend/src/app/platform/objectives.py:238-250` (`rating_algorithms.py` and `rate_tables.py`
  record none, premise f);
- the fragment declares **typed ports** (RL-1309 DP-3 item 1);
- it carries no `sub_graphs` of its own (DP-4);
- its output ports are type-checked at create by a `pricing-core` entry point that the result-type
  check's refactor exposes (DP-S1-4).

**Tech Stack:** Pydantic v2 (`model-schema`), `pricing-core`, FastAPI, SQLAlchemy 2.x async,
Alembic, pytest. No new dependency.

**Spec:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md):
  - §3.1 **FR-217** (`03:86` at the tree above) and **FR-212** (`03:81`);
  - §3.2 **FR-227** (`03:113`), whose text is "type compatibility is checked at save time";
  - §4, a new subsection (Task 1);
  - §5.1 (`03:742-769`), four new rows (Task 1).
- [`../specs/00-overview.md`](../specs/00-overview.md):
  - §2, the glossary, which gains **Sub-graph**;
  - FR-4 (`00:208`) and FR-16 (`00:220`).
- [`../specs/06-governance.md`](../specs/06-governance.md):
  - FR-343 (`06:79`), FR-345 (`06:81`) and FR-368 (`06:154`);
  - §4.1's permission catalogue: the `rating:read` row (`06:278`) and the "Coarse write rights"
    note (`06:304-306`). Both are widened (Task 1).
- [`../process/retrofit-impossible.md`](../process/retrofit-impossible.md) `:25`, `:26` and
  `:31`: audit in the caller's transaction, immutability, and RBAC from the first endpoint.

**What this plan implements.** WK-1250's map plan, **PL-1254**, Task 1 — "Slice 1: the
sub-graph as a stored, versioned artifact (FR-217's artifact limb)" (`PL-1254:260-286`). It
carries **RL-1309** (branch `dm-prep-b-wk1250`, read at
`e6a754310323459b0836952ef02fef99f1b9b5e8`; it mints in batch 3) as its ruling. PL-1278 is
superseded. What PL-1278 already verified still stands where no ruling changed it, and every
premise below is re-read at this plan's tree.

## Status

The status is the `status:` field in the header, and nothing else. Activation is that field's
flip only, and its facts (the date, the dispatch, the gate slot) are recorded in the dispatch
record and quoted in the ledger's Task 0, never added here. This is the maintainer's entry "2026-09-30 14:48:52 BST —
DECISIONS: check 34 is vacuous on real trees → a new FD (MEDIUM, WK-1170); PL-1299 accepted;
the activation practice from now on", item (3). Filed 2026-09-30 against the tree above under **working id 9845**.
- **Working id.** A sweep of `\b984[0-9]\b` over every `origin/*` branch and every open PR's
  head, over the open PR titles, and over the local `eta.md` "Working ids held" table (the
  lead's handover file, outside the repository) found 9840 to 9842 in use, and 9845 free.
- **Mint turn.** It is minted at its merge turn. In the same PR, PL-1278 takes the one change
  check 34 allows a frozen plan: `superseded_by: [<this plan's id>]`, with `status: superseded`
  moved forward.
- **When it can push.** It is pushed only after batch 3 puts RL-1309 on `main`, since check 32
  resolves every `RL-1309` token against `docs/INDEX.md`.

**Activation needs, in order:**
1. RL-1309 on `main`. It rules every decision point this slice depends on (**Decision points**,
   below).
2. PL-1254 `active`, and WK-1250's `SL-` rows cut. Both are the lead's, per PL-1254's own
   *Activation* (`PL-1254:341-351`). This PR adds no `SL-` row.
3. **The WK-1178 fix slice (PL-1299) and the #967 code slice (#969, plan working id 9833)
   merged** (the order in **Dependencies**).
4. A free RL-1263 gate slot, and the lead's dispatch record carrying the write-set check
   (**File contention**, below).

### Dependencies

- **`compile.py` has one writer at a time, in the maintainer's order** (to-lead.md
  "2026-09-30 10:53:10 BST — DECISION: condition/clamp FD (B) — HIGH on independent
  reproduction; owner and order; two small items", in the lead's local channel file): the
  WK-1178 fix slice (PL-1299) → the #967 code slice (plan working id 9833) → **this slice** →
  Slice 2. This slice's `compile.py` region (Task 4) is edited after both WK-1178 slices merge.
- **The #967 structure this slice builds on.** After the #967 code slice:
  - the four string checks are one registry over one enumerator of authored expression fields;
  - `_check_result_types` sits in that slice's `ALGORITHM_CHECKS` tuple;
  - its closure test (that plan's acceptance 3c) reds any module-level `_check_*` function that
    is not registered, and any check that reads an expression field itself.

  So Task 4's refactor keeps `_check_result_types` registered in `ALGORITHM_CHECKS`. The new
  public entry point is **not** named `_check_*`, and it reads result types, never an
  expression field. Task 0 re-reads `compile.py` at the dispatch tree and maps every premise
  below to the post-#967 names.
- **No WK-674 dependency.** PL-1254's Task 1 says "Depends on: nothing in WK-1250". The WK-674
  tenancy dependency is dropped (`PL-1254:274`, N1). Workspace scoping is RBAC scope, and it
  exists today: `caller.workspace_id` in `backend/src/app/api/rating_algorithms.py:48,68`.
  "After WK-674" is bare sequencing, and RL-1263 item 5 lifts it.

### File contention under RL-1263's option (c)

Two concurrent build slices "may not both change the same **existing** function, class, method,
spec section, or policy table". A small set of registry files is exempt for append-only edits:
- `backend/src/app/db/models.py`, for a new class appended;
- `backend/src/app/main.py`, for a router registration;
- `backend/migrations/versions/`, for a new revision file;
- the generated files, exactly `docs/contracts/openapi/generated.json`,
  `docs/contracts/schemas/generated/` and `docs/INDEX.md`.

The list is `RL-1263:104-116`, as corrected at 23:20:11 BST. At the second merge, the later slice
merges `main` in, re-points `down_revision` to one head, regenerates the generated files and
re-runs its full gate. Each row below was read at the tree above.

| This slice's path | What it does there | Also changed by | Under option (c) |
|---|---|---|---|
| `packages/pricing-core/src/pricing_core/rating/compile.py` | `_producer_types` (`:84-103`) and `_check_result_types` (`:114-139`) refactored; one new public fragment entry point (Task 4) | the WK-1178 fix slice (PL-1299) and the #967 code slice (plan working id 9833); Slice 2 (`compile_bundle`) | **Serialised by the maintainer's order** (**Dependencies**). This slice is never in the file at the same time as any of them |
| `packages/pricing-core/tests/test_rating_compile.py` | new tests only | the #967 code slice (appended tests) | Serialised by the same order |
| `backend/migrations/versions/` | one new revision, `down_revision` = the head at dispatch (`d7e2a9b5c418` at the tree above) | WK-674 S2, WK-673 S4 | **Exempt.** The second to merge re-points to one head |
| `backend/src/app/db/models.py` | appends `SubGraphVersionRow` at the end of the file | WK-674 S2, WK-673 S4 (new rows); WK-674 S2a (existing classes' metadata, PL-1303) | **Exempt** for this slice's append |
| `backend/src/app/main.py` | one router import beside `:34`, one `include_router` in `:136-147` | WK-673 S4 | **Exempt** |
| the generated contracts; `docs/INDEX.md` | regenerated | any slice that adds a shape, route or record | **Exempt**, never hand-merged |
| `docs/specs/03-rating-engine.md` §5.1 | four rows appended to the REST table | WK-674 S2 (a deployment-history `GET`), WK-673 S4 and S7, and #977's column slice | **A shared section.** RL-1263:100 decides it at dispatch, on the actual diffs |
| `docs/specs/03-rating-engine.md` §4 | a new subsection | WK-674 S2 and S6 (new subsections) | **A shared section.** The second to merge takes the next free number and never reuses one (`CLAUDE.md` §5) |
| `docs/specs/03-rating-engine.md` §2 | one glossary row | none found | Not shared |
| `docs/specs/00-overview.md` §2 | one glossary row | WK-673 S1, if it adds a term (`PL-1267:469`) | Shared only if WK-673 S1 adds a term |
| `docs/specs/06-governance.md` §4.1 | the `rating:read` row and the "Coarse write rights" note widened (Task 1) | WK-690 S3 (its `custom_objective:author` row, `PL-1268:491-493`) | **A shared section.** Decided at dispatch on the diffs |
| `scripts/generate-contracts.py` | one entry in the slug → symbol map (`:39-101`) | any slice registering a generated shape | **Not on the registry list.** It serialises unless the dispatch record names the path |
| `packages/model-schema/src/model_schema/__init__.py` | exports added | any slice exporting a shape | **Not on the registry list**, as above |
| `packages/model-schema/src/model_schema/rating.py` | only if a graph helper must be promoted (Task 2) | WK-673 (`PL-1267:316-318`) | Shared only if Task 2 promotes a helper |

**Not in this slice's set:** `compile_bundle`, `score.py`, `TraceStep`, `runtime.py`, any
`approvals.py`, `errors.py`, `conftest*.py`, and any `pyproject.toml` or `uv.lock`.

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means the
failing run is quoted in the ledger with its failing assert line **and the cause the step
predicts**. A failure for any other cause is a plan defect, reported and not worked around.

1. **Spec** (Task 1).
   - `03` gains the `SubGraph` subsection: the shape, its typed ports, its invariants and an
     example. It also gains four §5.1 rows, with DP-S1-1's permissions and DP-S1-3's codes.
   - `00` §2 gains **Sub-graph**.
   - `06` §4.1's `rating:read` row and "Coarse write rights" note name sub-graphs and regression
     suites (RL-1309 DP-S1-1 item 3; widened, not renamed).
   - Nothing else goes to `06`: no §2 Governed Artifact entry, no §3.3 row and no §4.2 policy
     (RL-1309 DP-1 item 1).
   - FR-217 and FR-218 are **not** reworded. If the executor believes either needs a change, it
     stops and reports.
   - `python3 scripts/audit-docs.py` exits 0.
2. **Contract.**
   - `uv run python scripts/generate-contracts.py --check` exits 0.
   - `docs/contracts/schemas/generated/sub-graph.schema.json` has the properties `slug`,
     `version`, `inputs`, `outputs`, `steps` and `change_note`, and no `sub_graphs`.
   - `outputs`' items take their schema from `AlgorithmOutput`'s, and `inputs`' items carry
     `name` and `type` (DP-3 item 1).
   - `git grep -n -E '^class (SubGraph|SubGraphBody|SubGraphInputPort)\(' -- packages backend/src`
     prints **exactly three** lines, all in `packages/model-schema/src/model_schema/sub_graphs.py`.
     Any other count fails.
3. **Migration (FR-417).**
   - One new Alembic revision creates the table.
   - `upgrade head`, `downgrade -1` and `upgrade head` again all exit 0 against a scratch
     database (the `dev-commands` DSN).
   - `uv run pytest tests/test_repository_invariants.py -q` passes.
   - A second insert of the same `(workspace_id, slug, version)` raises `IntegrityError` at the
     database.
4. **Create-time refusals (FR-217, FR-212, FR-227), red first, one test per cause**, in
   `packages/model-schema/tests/test_sub_graph.py` (shape), the new tests in
   `packages/pricing-core/tests/test_rating_compile.py` (the type check) and
   `backend/tests/test_sub_graphs_api.py` (the route). Each case, with its route code (RL-1309
   DP-S1-3):
   - a step consumes a name that is neither a declared input port nor produced by a step:
     `RATING_GRAPH_UNRESOLVED_REF`, naming it;
   - a declared output port that no step produces: `RATING_GRAPH_UNRESOLVED_REF`, naming it;
   - **an output port whose declared type is incompatible with its producing step's result
     type: `RATING_TYPE_MISMATCH`** (FR-227, `03:113`; RL-1309 *Acceptance*, Slice 1). The
     compatibility rule is `compile.py`'s `_compatible` (`:106-111`), called as it stands;
   - a cycle: `RATING_GRAPH_CYCLIC`;
   - two steps with the same `step_id`: `VALIDATION_FAILED`;
   - a body carrying `sub_graphs`: `VALIDATION_FAILED` (DP-4). The shape test also asserts the
     error's `loc` is `("sub_graphs",)` and its type is `extra_forbidden`;
   - an `input` or `output` step inside the fragment: `VALIDATION_FAILED`, because the ports
     replace them;
   - an empty `change_note`: `VALIDATION_FAILED` (DP-1 item 1).

   Each route refusal is a 422, except the create-route cases in 5.
5. **The two create routes and immutability** (`00` FR-4; RL-1309 DP-S1-2), red first:
   - `POST /api/v1/sub-graphs` on a slug that exists returns **409** `VALIDATION_FAILED`, and
     the stored content is byte-identical afterwards;
   - `POST /api/v1/sub-graphs/{slug}/versions` on an unknown slug returns **`NOT_FOUND`**;
   - the server assigns versions as the current maximum plus one. A lost race is a 409 (the form
     of `objectives.py:229-236`);
   - the authorisation sweep (`backend/tests/test_api_authorisation_sweep.py`) lists no `PUT`,
     `PATCH` or `DELETE` on `/sub-graphs`.
6. **The refactor preserves the algorithm path.** `validate_algorithm`'s existing tests in
   `packages/pricing-core/tests/test_rating_compile.py` pass **unmodified**. `git diff
   origin/main...HEAD` shows no removed or changed line in the existing tests of that file.
   After the #967 code slice, its closure tests (the enumerator and the check registry) pass
   unchanged, with `_check_result_types` still registered.
7. **Audit** (`06` FR-368; retrofit-impossible `:25`), red first.
   - Every successful write leaves exactly one Audit Event, with `action == "sub_graph.created"`
     and `entity_ref == "sub_graph:<slug>@<version>"`, in the same transaction.
   - **Broken-input proof:** with the `audit.record` call removed locally, the test goes red on
     a count of 0. That edit is never committed.
   - A refused write leaves no event and no row.
8. **Permission** (`06` FR-343), red first, per route.
   - A principal without `rating:write` (writes) or `rating:read` (reads) gets 403.
   - A principal whose only assignment is scoped to a named Rating Algorithm gets 403 too,
     because `_covers` returns `False` when no resource is named
     (`backend/src/app/platform/rbac.py:205-216`). RL-1309 DP-S1-1 item 2 accepts this.
   - The authorisation sweep passes with the four routes in it.
9. **Workspace scoping** (`06` FR-345, `00` FR-16). A sub-graph in workspace A is **404, not
   403**, to a caller in workspace B, and is absent from B's list. Mirror
   `backend/tests/test_api_jobs.py:173`.
10. **Resolver.** `resolve_ref(session, *, workspace_id, ref: ArtifactRef)` returns exactly the
    addressed version. An unknown slug, an unknown version, a ref of another type and another
    workspace's ref are each refused, by cause. It is **not** wired into the compile resolver
    (`backend/src/app/platform/rating_versions.py:417`); that is Slice 2's.
11. **Coverage.** `uv run python scripts/req-coverage.py` lists the new tests against FR-217 and
    FR-227. The ledger records FR-217's verdict as **the artifact limb delivered; the pin and
    inlining limbs not started, owned by Slice 2**.
12. **The gate.** The full two-half gate (`CLAUDE.md` §11) exits 0 on the committed tree. It
    runs under a gate slot, per the dispatch record's slot rule. The ledger quotes every rc, the
    `N passed` line and `HEAD`, and compares `N passed` with `origin/main`'s.
    `backend/tests/test_demo_guide.py` passes with the new §5.1 rows present in the generated
    contract.
13. **Item 11.** Before the lead merges, the maintainer's **MERGE-ACK** naming the PR's full head
    SHA is recorded in the lead's local channel file `~/gi-pricing-plan.local/channel/to-lead.md`,
    as `.claude/roles/lead.md:156-157` (rule 4) names. It is never posted on the PR. The slice's
    clean audit is filed. A Slice closes on a clean audit and the lead's merge (`CLAUDE.md` §13).

## Global Constraints

- **Spec first** (`CLAUDE.md` §0): Task 1 lands before any code.
- **No hand-written shape that `model-schema` owns** (`CLAUDE.md` §2). `SubGraph`,
  `SubGraphBody` and `SubGraphInputPort` are declared once, in `model-schema`. Output ports
  reuse `AlgorithmOutput`, and there is **no second result-type vocabulary** (RL-1309 DP-3
  item 1).
- **`pricing-core` changes only in `compile.py`'s two type-check functions, one new public entry
  point, and new tests** (RL-1309 DP-S1-4 item 3). `compile_bundle`, the other checks and
  `_compatible` are untouched. `.importlinter` keeps `pricing-core` standalone.
- **Every write emits its Audit Event in the caller's transaction** (`06` FR-368;
  `backend/src/app/platform/audit.py:52-75`).
- **RBAC in the backend on every request** (`06` FR-343): `rating:write` and `rating:read`
  through `requires()`.
- **A version is immutable** (`00` FR-4). There is no update route and no update code path.
- **Every row carries a `workspace_id`; a workspace is not a tenant** (`00` FR-16).
- **The migration chain has exactly one head** (`07` FR-417).
- **Registry files are edited append-only** (RL-1263, option (c)).
- **Do not build ahead of the phase.** This slice builds no frontend view (that is WK-675's), no
  pin, no inlining, and no mount port map. The mount port map is Slice 2's (RL-1309 DP-3 item 5).

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.1 | FR-217 | **The artifact limb only.** The pin and the inlining are Slice 2's |
| `03` §3.2 | FR-227 | **For a fragment's output ports**, checked at create (RL-1309 DP-S1-4). The algorithm path is unchanged |

The slice also honours, without owning them: `00` FR-4, `00` FR-16, `03` FR-212, `06` FR-343,
`06` FR-345, `06` FR-368 and `07` FR-417.

**Not in this slice:**
- **Slice 2:**
  - `Pins.sub_graphs`, the compile resolver's `sub_graph` branch, the inlining, the mount port
    map and namespacing (RL-1309 DP-3 items 3–5), `bundle_hash`, and FR-258's inlined steps;
  - the FR-20 restatement (DP-1 item 5), the diff limb (DP-1 item 3), and guards G1, G2 and G4
    (DP-1 item 6);
  - the four expression checks on the inlined algorithm (DP-S1-4 item 6).
- **Slice 3:** FR-218's purpose mount, and `RL-1242`'s retirement.
- **WK-674 Slice 2:** G3, the deploy route.
- **WK-675:** the designer's sub-graph view.

### Premises, read at the tree above (`e9263283`)

The backend and `model-schema` files this plan cites are unchanged since PL-1278's tree
`4f5da864`: `git diff --stat 4f5da864 e9263283 -- backend/src packages/model-schema/src
scripts/generate-contracts.py backend/migrations/versions` prints nothing for them. Only
`pricing_core/data/*`, `03`, `00` and `06` moved, and each spec cite below is re-pinned.

| # | Premise | Evidence |
|---|---|---|
| a | No sub-graph table, route or service exists | `git grep -n -i 'sub_graph\|subgraph' -- backend/src packages/*/src` prints 8 lines, none under `backend/src`: `model_schema/__init__.py:282,669`, `model_schema/rating.py:340,343,390`, `model_schema/refs.py:25`, and `pricing_core/rating/score.py:399,401` |
| b | `SubGraphRef` is `ref: ArtifactRef` plus `mount_point: str`, frozen and `extra="forbid"` | `packages/model-schema/src/model_schema/rating.py:340-351`, `:390` |
| c | `"sub_graph"` is a legal `ArtifactRef` type | `packages/model-schema/src/model_schema/refs.py:25` |
| d | `AlgorithmOutput` is `name`, `type: RatingResultType` and `required`, and `RatingResultType` is `Annotated[str, AfterValidator(_reject_float_type)]` | `rating.py:235`, `:238-244`. So output ports reuse it, and input ports use `RatingResultType` (RL-1309 DP-3 item 1) |
| e | The graph-invariant helpers are module functions over a step list | `_produced_by` and `_consumed_by` (`rating.py:357-370`), used by `RatingAlgorithm._graph_invariants` (`:392`) |
| f | Neither the rating-algorithm nor the rate-table write path records an Audit Event; custom objectives do | `grep -n 'audit\.'` over the two service modules prints nothing; `objectives.py:238` |
| g | `requires(permission)` passes no resource | `backend/src/app/api/authz.py:54-77`; `rbac.py:205-216` |
| h | `rating:read` and `rating:write` exist | `packages/model-schema/src/model_schema/permissions.py:47-48` |
| i | The migration chain's single head is `d7e2a9b5c418` | a scan of every `revision` and `down_revision` under `backend/migrations/versions/` (48 files) |
| j | The generated-contract registry is a slug → symbol map | `scripts/generate-contracts.py:39-101` |
| k | `03` §4's last subsection is §4.10, and §5.1 has no sub-graph row | `grep -n '^### 4\.' docs/specs/03-rating-engine.md` (§4.10 at `:696`); `03:742-769` |
| l | `00` §2 has no "Sub-graph" term | `grep -n -i 'sub-graph' docs/specs/00-overview.md` prints nothing |
| m | The result-type check's shape, which Task 4 refactors | `_producer_types(algo)` (`compile.py:84-103`) types `RatingInputStep`s from `algo.input_contract` and `RatingExpressionStep`s from `result_type`. `_compatible(producer, declared)` (`:106-111`). `_check_result_types(algo)` (`:114-139`) walks `RatingOutputStep`s against `algo.outputs`. `validate_algorithm` calls it (`:261-275`) |
| n | `06` §4.1's `rating:read` row and the "Coarse write rights" note | `06:278` and `06:304-306`. RL-1309 cites them as `06:265` and `:287-288` at its tree `7c354305` |

The executor re-reads each premise at its own tree, **after both WK-1178 slices merge**, maps m
to the post-#967 names, and stops on any premise that no longer holds ([`README.md`](README.md)
convention 4).

### Decision points

Every decision point that bears on this slice is ruled; none is open. The rows below are the rulings, not open questions.

| Decision | Ruling (RL-1309) | Where it acts |
|---|---|---|
| Map DP-1 | **(b).** A Sub-graph Version is not a Governed Artifact. It has no status and no approval lifecycle, and a required change note. Its change reaches approval inside the Rating Version that pins it | Task 1 (nothing to `06` §2, §3.3 or §4.2), Task 2 (the change note) |
| Map DP-3 | **(a).** Typed ports: output ports reuse `AlgorithmOutput`, and an input port is a `name` plus a `RatingResultType`. The fragment's own names are namespaced at inlining (Slice 2) | Tasks 1–2; the port map is Slice 2's |
| Map DP-4 | **(a).** Depth 1. The shape has no `sub_graphs` field and is `extra="forbid"` | Task 2 |
| DP-S1-1 | **(a).** `rating:write` and `rating:read` through `requires()`, workspace-wide. The scoped-principal consequence is accepted. `06`'s catalogue text is widened, not renamed | Tasks 1 and 6 |
| DP-S1-2 | **(a).** One table, `sub_graph_versions`. The server numbers versions (maximum plus one). Two create routes (new: 409 on a clash; revise: `NOT_FOUND` on an unknown slug), a read and a cursor-paginated list. No `parent_id` | Tasks 1, 3, 5 and 6 |
| DP-S1-3 | **(a).** `03` §5.1's codes, with `RATING_TYPE_MISMATCH` for an output-port type mismatch | Tasks 1 and 6 |
| DP-S1-4 | **(a), with FR-227's result-type check at create**, through a refactor of `_producer_types` and `_check_result_types` that lands in this slice. The other four checks run on the inlined algorithm at compile, in Slice 2 | Task 4 |

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree, and `git branch --show-current` is the slice branch,
  cut from `main` **after** the WK-1178 fix slice and the #967 code slice merged.
- [ ] `uv sync --all-packages` (`dev-commands`).
- [ ] Re-derive premises a–n at that tree, mapping m to the post-#967 structure, and record each
  result in the ledger. Check the migration head again (premise i). If a revision has merged
  since, this slice's `down_revision` names the new head.
- [ ] `gh pr list --state open`, and read anything that rules on FR-217, FR-227, sub-graphs, the
  permission catalogue, `03` §4–§5.1 or `compile.py` ([`README.md`](README.md) convention 4).
  Name the SHA read. Re-point #969 (plan working id 9833) to its id if it has minted.
- [ ] Confirm the dispatch record's RL-1263 write-set check, and its gate-slot rule.
- [ ] **At the second merge**, if the other lane's slice merges first: merge `origin/main` in,
  re-point `down_revision` to one head, regenerate `docs/contracts/` and `docs/INDEX.md` (never
  hand-merged), and re-run Task 7's full gate.

### Task 1: Spec — `03` §2, §4 and §5.1; `00` §2; `06` §4.1's catalogue text

**Files:** Modify `docs/specs/03-rating-engine.md` (§2, a new §4 subsection, §5.1),
`docs/specs/00-overview.md` (§2) and `docs/specs/06-governance.md` (§4.1: the `rating:read` row
and the "Coarse write rights" note).

- [ ] `00` §2: add **Sub-graph**: "A reusable, versioned fragment of a Rating Algorithm (`03`
  FR-217), with declared, typed input and output ports, mounted by a parent algorithm and
  inlined into the parent's Bundle. It holds no premium on its own." Place it in the table's
  existing order. `00:161` is **Rating Algorithm**.
- [ ] `03` §2: a one-line **Sub-graph** row pointing at `00` §2, in the form other `03` rows use
  when they restate a `00` term.
- [ ] `03` §4, a new subsection taking the next free number (§4.11 at the tree above; see
  **File contention**): `SubGraph`. It carries the typed ports, the invariants of acceptance 4 as
  prose (including FR-227's output-port check), "mounts nothing" (DP-4), the required change
  note, an example, and a dated note citing FR-217 and RL-1309:

  ```json
  {
    "slug": "ncd-ladder",
    "version": 4,
    "inputs": [{"name": "ncd_years", "type": "int"}],
    "outputs": [{"name": "ncd_factor", "type": "decimal", "required": true}],
    "steps": [
      {"step_id": "s_ncd", "type": "table", "label": "NCD ladder",
       "rate_table_ref": "rate_table:ncd@2", "key_expr": ["ncd_years"],
       "consumes": "ncd_years", "produces": "ncd_factor"}
    ],
    "change_note": "Step-back after one claim is two years, not three."
  }
  ```

  **Re-verify every literal before it enters the spec** ([`README.md`](README.md) convention 1):
  - the port type values against `RatingResultType`'s accepted words;
  - `required` against `AlgorithmOutput`;
  - the step's fields against `RatingTableStep` (`rating.py:283-288`) and the §4.1 example's
    table step (`03:262-264`).

  The slug `ncd-ladder` and `@4` are `WF-699` B7's
  (`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:62`).
- [ ] `03` §5.1: four rows, in DP-S1-2's form, with DP-S1-1's permissions, each carrying its
  status codes and FR-217:
  - `POST /api/v1/sub-graphs` (201; 409 on an existing slug);
  - `POST /api/v1/sub-graphs/{slug}/versions` (201; `NOT_FOUND` on an unknown slug);
  - `GET /api/v1/sub-graphs/{slug}@{version}`;
  - `GET /api/v1/sub-graphs/{slug}/versions` (cursor-paginated).

  No new error code is added (DP-S1-3).
- [ ] `06` §4.1 (DP-S1-1 item 3): widen, and do not rename, the `rating:read` row (`06:278`)
  and the "Coarse write rights" note (`06:304-306`) so that each also names sub-graphs and
  regression suites.
- [ ] `python3 scripts/audit-docs.py`, quoting the rc. Commit:
  `docs(specs): 03 SubGraph with typed ports and §5.1 routes, 00 §2 Sub-graph, 06 §4.1 catalogue text (FR-217, WK-1250 S1)`.

### Task 2: `model-schema` — `SubGraph`, `SubGraphBody`, `SubGraphInputPort` and the contract

**Files:** Create `packages/model-schema/src/model_schema/sub_graphs.py` and
`packages/model-schema/tests/test_sub_graph.py`. Modify `packages/model-schema/src/model_schema/__init__.py`
(the exports, beside `SubGraphRef` at `:282` and `:669`) and `scripts/generate-contracts.py`
(register `"sub-graph": "SubGraph"` at `:39-101`). Regenerate `docs/contracts/`.

**Interfaces:**
- Produces:
  - `SubGraphInputPort`: `name: str` and `type: RatingResultType`;
  - `SubGraphBody`: `inputs: list[SubGraphInputPort]`, `outputs: list[AlgorithmOutput]`,
    `steps: list[RatingStep]` and `change_note: str` (non-empty);
  - `SubGraph(SubGraphBody)`, which adds `slug: Slug` and `version: int`.

  All three are `frozen=True, extra="forbid"`.

- [ ] **Red first:** acceptance 4's shape-level cases, plus one positive test that the Task 1
  example parses. **Predicted red:** `ImportError` on `model_schema.sub_graphs` for every test.
- [ ] Implement.
  - The invariant check reuses `_produced_by` and `_consumed_by` (premise e). Declared input
    ports count as produced names, and declared output ports must each be produced by exactly
    one step.
  - The cycle check reuses `_graph_invariants`' method. If a helper must be promoted into a
    module function, promote it and keep `RatingAlgorithm`'s behaviour identical:
    `packages/model-schema/tests/test_rating_algorithm.py` passes unchanged.
  - The checks read `consumes` and `produces` only, as `_graph_invariants` does.
  - **The type check is not here.** It is Task 4's, in `pricing-core`, where FR-227's rule
    already lives.
- [ ] Green. Regenerate the contracts, confirm `--check` exits 0, and run the contract guard.
  Check acceptance 2's count.
- [ ] Commit.

### Task 3: The table and its migration

**Files:** Modify `backend/src/app/db/models.py`, with `SubGraphVersionRow` **appended at the
end of the file** and no existing class edited. Create one Alembic revision and
`backend/tests/test_migration_sub_graphs.py`.

- [ ] **Red first:** acceptance 3's constraint test. **Predicted red:** `UndefinedTable`.
- [ ] The row, per DP-S1-2 (a):
  - `id` (uuid7, as `RatingAlgorithmRow` at `models.py:1936`), `workspace_id`, `slug`
    (`String(64)`), `version` (`Integer`), `content` (`JSONB`), `change_note` (`Text`, not
    null), `created_at` and `created_by`;
  - `UniqueConstraint("workspace_id", "slug", "version", name="uq_sub_graph_versions_slug_version")`,
    and an index on `(workspace_id, slug)`;
  - **no `updated_at` and no `parent_id`** (`00` FR-4; RL-1309 DP-S1-2 item 5).
- [ ] The revision: its `down_revision` is the head Task 0 found. The downgrade drops the table.
  Round-trip it per acceptance 3.
- [ ] Green, and commit.

### Task 4: `pricing-core` — the FR-227 refactor and the fragment entry point (RL-1309 DP-S1-4)

**Files:** Modify `packages/pricing-core/src/pricing_core/rating/compile.py`, limited to
`_producer_types`, `_check_result_types` and one new public function. Add new tests only to
`packages/pricing-core/tests/test_rating_compile.py`.

**Interfaces:**
- Produces: a public
  `check_fragment_output_types(steps: list[RatingStep], input_ports: Mapping[str, str], output_ports: list[AlgorithmOutput]) -> list[ValidationIssue]`
  in `compile.py`, added to `__all__`. The name is a proposal: it must **not** begin `_check_`,
  so that the #967 closure test does not require it in a registry. The ledger records the name
  used. Task 5's create path calls it.

- [ ] **Red first:** acceptance 4's `RATING_TYPE_MISMATCH` case against the new entry point.
  **Predicted red:** `ImportError`, because the function does not exist.
- [ ] Refactor, per RL-1309 DP-S1-4 item 2:
  - `_producer_types` becomes a function over the steps plus a mapping of already-typed names.
    For an algorithm those names are its input contract; for a fragment they are its input
    ports.
  - `_check_result_types` becomes a function over those producer types plus the declared
    outputs, which it reaches through the algorithm's output steps.
  - The algorithm path calls the new forms with the algorithm's own inputs and outputs, so its
    behaviour is unchanged. `_check_result_types` stays registered where the #967 slice put it.
  - `_compatible` (`:106-111`) is called as it is.
- [ ] Add `check_fragment_output_types`. It maps each output port to its producing step's type
  and applies `_compatible`, issuing `RATING_TYPE_MISMATCH` with the port name.
- [ ] Green. Run acceptance 6: the existing tests pass unmodified, and the #967 closure tests
  pass. Commit: `refactor(rating): FR-227's result-type check over steps and declared outputs, and a fragment entry point (WK-1250 S1)`.

### Task 5: The service and the resolver

**Files:** Create `backend/src/app/platform/sub_graphs.py` and
`backend/tests/test_sub_graphs_service.py`.

**Interfaces:**
- Consumes: `SubGraph`, `SubGraphBody` and `SubGraphInputPort` (Task 2); `SubGraphVersionRow`
  (Task 3); `check_fragment_output_types` (Task 4); `audit.record` (`audit.py:52`).
- Produces:
  - `create_sub_graph(database, workspace_id, actor, slug, body) -> SubGraph`: version 1, with a
    409 if the slug exists;
  - `create_version(database, workspace_id, actor, slug, body) -> SubGraph`: the maximum plus
    one, with `NOT_FOUND` for an unknown slug;
  - `get_version(database, workspace_id, slug, version) -> SubGraph`;
  - `list_versions(database, workspace_id, slug, cursor, limit)`, using `app.api.pagination`'s
    page type;
  - `resolve_ref(session, *, workspace_id, ref: ArtifactRef) -> SubGraph`, in the form of
    `objectives.resolve_ref` (`objectives.py:400`).

- [ ] **Red first:** acceptance 5 (the create routes' 409 and `NOT_FOUND`, and unchanged
  content), 7 (audit) and 10 (the resolver, each refusal by cause). **Predicted red:**
  `ImportError` on `app.platform.sub_graphs`.
- [ ] Implement, mirroring `objectives.py:225-250`: flush, catch `IntegrityError` as 409, then
  `audit.record(..., action="sub_graph.created", entity_ref=f"sub_graph:{slug}@{version}")`,
  inside `database.unit_of_work()`.
  - Before writing, call `check_fragment_output_types` and refuse on its first issue.
  - The `after` payload carries `change_note`, `inputs` and `outputs`.
- [ ] Acceptance 7's broken-input proof: remove the `audit.record` call locally, run the test,
  quote the red, and restore the call. The broken state is never committed.
- [ ] Green, and commit.

### Task 6: The routes

**Files:** Create `backend/src/app/api/sub_graphs.py` and `backend/tests/test_sub_graphs_api.py`.
Modify `backend/src/app/main.py`: an import beside `:34`, and an `include_router` in
`:136-147`. Regenerate the generated contracts.

- [ ] **Red first:** acceptance 4 through the route (each code per DP-S1-3), 5, 8 (a 403 per
  route, unscoped and scoped) and 9 (a 404 across workspaces). **Predicted red:** 404 on every
  route, because no route is mounted. Write the cross-workspace test to assert 200 in workspace
  A first.
- [ ] Implement in `rating_algorithms.py`'s form: `requires(Permission.RATING_WRITE)` for the two
  creates, `requires(Permission.RATING_READ)` for the two reads, and `problems(...)` for the
  documented codes. The body is `SubGraphBody`, typed.
- [ ] Regenerate the contracts, confirm `--check` exits 0, and run the authorisation sweep and
  `backend/tests/test_demo_guide.py`.
- [ ] Green, and commit.

### Task 7: The gate and the ledger

- [ ] Run `tests/test_repository_invariants.py`, the migration round trip, then the full
  two-half gate under a gate slot. Quote every rc, the `N passed` line and `HEAD`.
- [ ] The ledger records:
  - the tree, and premises a–n with m mapped;
  - the red-first quotes;
  - RL-1309 as the ruling;
  - the name of Task 4's entry point;
  - FR-217's partial verdict (acceptance 11);
  - any re-pointed `down_revision`.
- [ ] Item 11 (acceptance 13).

## Hand-off

Slice 2 (the pin and the inlining) starts after this slice closes. It consumes `resolve_ref`,
`SubGraph` and the typed ports from here, and it builds on Task 4's refactor rather than undoing
it: the inlined algorithm goes through the algorithm path (RL-1309 DP-S1-4 item 2). Slice 2's
leaf plan carries these:
- RL-1309's DP-1 items 3 and 5;
- DP-1 item 6's G1, G2 and G4. G1 is narrowed to `SubGraphRef` against `Pins.sub_graphs`, and
  reuses PL-1299's `check_step_refs_pinned` (FD-1297) over the inlined algorithm;
- DP-3 items 3–5;
- DP-S1-4 item 6, the four checks on the inlined algorithm, where a fragment with a
  non-deterministic expression is refused at compile, red first;
- the whichever-lands-second rule with WK-673 Slice 5. If Slice 5 merged first, Slice 2's test
  asserts the diff limb in the **persisted** evidence. If Slice 2 merged first, Slice 5 carries
  the re-point case;
- the gate on the diff limb. **Slice 2 does not dispatch until an in-repo record carries the
  limb verbatim, citing RL-1309**: WK-673's Slice 5 leaf plan, or a WK-673 slice ledger's Task
  0, whichever lands first. A local file does not satisfy it. This is the maintainer's entry
  "2026-09-30 14:47:19 BST — RL-1309:309-311's gate: NO, a local delta file doesn't satisfy it;
  an IN-REPO carrier is needed".

## Self-review

- **Against RL-1309's Slice 1 obligations** (*What it obliges*, "WK-1250 Slice 1"):
  - the spec change: `03` §2's term, §4's contract (DP-3 items 1–2, DP-4, the change note),
    §5.1's four routes with DP-S1-1's permissions and DP-S1-3's codes, and `06`'s catalogue
    text → Task 1 and acceptance 1;
  - the code: the DP-S1-4 refactor and the create-time checks → Tasks 2, 4 and 5, and acceptance
    4 and 6;
  - RL-1309's Slice 1 *Acceptance*: `RATING_TYPE_MISMATCH` at create, and the `validate_algorithm`
    tests unmodified → acceptance 4 and 6. `sub_graphs` → `VALIDATION_FAILED` → acceptance 4.
    The two create routes' 409 and `NOT_FOUND` → acceptance 5.
- **Against PL-1278, what carries over unchanged:** the table, the audit, the permissions, the
  workspace scoping, the resolver, the migration, the coverage and the gate. The changes are the
  typed ports, FR-227 at create with its `pricing-core` refactor, the added acceptance, the `06`
  catalogue text, and the re-derived contention and order.
- **FR-217 read to its clauses** (`03:86`): "reusable fragments" → the stored artifact;
  "versioned artifacts" → DP-S1-2 and acceptance 5; "referenced by the parent" → the resolver;
  "inlined at bundle time" → Slice 2.
- **FR-227 read to its clause** (`03:113`): "type compatibility is checked at save time" → Task
  4 and acceptance 4, for a fragment's output ports.
- **Literals** were read at the tree above (premises). The names the executor adds are
  proposals, named once each: `SubGraph`, `SubGraphBody`, `SubGraphInputPort`,
  `SubGraphVersionRow`, `sub_graph_versions`, `sub_graph.created`,
  `check_fragment_output_types` and the service functions.
- **Open:** nothing is open for the decision-maker. RL-1309, #969 and this plan are unminted.
