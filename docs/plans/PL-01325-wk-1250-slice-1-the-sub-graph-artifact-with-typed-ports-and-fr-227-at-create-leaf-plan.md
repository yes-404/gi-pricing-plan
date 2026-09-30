---
id: PL-1325
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
maintainer's entries are cited by their headers in `~/gi-pricing-plan.local/channel/to-lead.md`.
That file is the lead's local channel file. It is outside the repository and is not a governed
record. Its headers give provenance only, and this plan states each rule's operative content
itself. The entries:
- "2026-09-30 14:44:36 BST — DECISION: RL-1309's plan follow-ons are NOT in-place edits (plans
  are frozen as a family); use dispatch-record deltas";
- "2026-09-30 14:46:03 BST — confirmed: WK-1250 S1 gets a NEW leaf plan superseding PL-1278".

The Work's scope is unchanged: FR-217's artifact limb is still the only requirement this slice
delivers.

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

- **`compile.py` has one writer at a time, in the maintainer's order** (`~/gi-pricing-plan.local/channel/to-lead.md`,
  "2026-09-30 10:53:10 BST — DECISION: condition/clamp FD (B) — HIGH on independent
  reproduction; owner and order; two small items"): the
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
| `docs/specs/03-rating-engine.md` §5.1 | four rows appended to the REST table | WK-674 S2 (a deployment-history `GET`, `PL-1237:773-774`), WK-674 S6 (a routing route, `PL-1237:977-978`), WK-673 S4 and S7 (`PL-1267:527`, `:589`), and #977's column slice | **Serialises** (RL-1263:100-104): an existing spec section that is not on the registry list. The one exception is a dispatch record that names the path together with the check that no existing definition is edited by both |
| `docs/specs/03-rating-engine.md` §4 | a new subsection | WK-674 S2 and S6 (new subsections, `PL-1237:772`, `:977`) | **Serialises** (RL-1263:100-104), for the same reason. The slice that merges second numbers its subsection after the first's, and never reuses a number (`CLAUDE.md` §5) |
| `packages/model-schema/src/model_schema/graph_errors.py` | new: `GraphCycleError`, `GraphUnresolvedRefError` (Task 2) | none | Not shared |
| `packages/model-schema/src/model_schema/rating.py` | `_graph_invariants`: the undefined-value raise (`:418-421`) and the cycle raise (`:439`) changed to the new classes, with messages unchanged (Task 7). Also a graph helper, only if Task 2 must promote one | WK-673 edits other definitions in `rating.py` (`PL-1267:316-318`) | **An existing-definition edit.** It serialises unless the dispatch record names the path with the check that no definition is edited by both |
| `backend/tests/test_rating_algorithms.py` | four characterisation tests appended, one of them `xfail(strict=True)` until Task 7 (N1 and M1; Task 5) | any slice adding tests there | Appended tests only; no existing test is edited |
| `backend/src/app/platform/rating_algorithms.py` | `_parse_algorithm` (`:25-52`) edited: its mapping is extracted into a public function that it calls, with identical behaviour (Task 5, B1) | any slice editing `_parse_algorithm` or the rating-algorithm save path | **An existing-definition edit, not on the registry list.** It serialises unless the dispatch record names it |
| `docs/specs/03-rating-engine.md` §2 | one glossary row | none found | Not shared |
| `docs/specs/00-overview.md` §2 | one glossary row | WK-673 S1, if it adds a term (`PL-1267:469`) | Shared only if WK-673 S1 adds a term |
| `docs/specs/06-governance.md` §4.1 | the `rating:read` row and the "Coarse write rights" note widened (Task 1) | WK-690 S3 (its `custom_objective:author` row, `PL-1268:491-493`) | **A shared section.** Decided at dispatch on the diffs |
| `scripts/generate-contracts.py` | one entry in the slug → symbol map (`:39-101`) | any slice registering a generated shape | **Not on the registry list.** It serialises unless the dispatch record names the path |
| `packages/model-schema/src/model_schema/__init__.py` | exports added | any slice exporting a shape | **Not on the registry list**, as above |

**The existing definitions this slice edits** (W3 of the plan audit), in full:
- `compile.py`'s `_producer_types` and `_check_result_types`, whose signatures are kept (Task 4);
- `rating_algorithms.py`'s `_parse_algorithm`, whose behaviour is kept (Task 5), and the
  extracted `graph_validation_error`, switched to the typed signal (Task 7);
- `model_schema/rating.py`'s `_graph_invariants`, the raises at `:418-421` and `:439` only (Task 7);
- `03` §2, §4 and §5.1; `00` §2; `06` §4.1's `rating:read` row and "Coarse write rights" note;
- `scripts/generate-contracts.py`'s map, and `model_schema/__init__.py`'s exports (appends to
  existing definitions).

Everything else this slice writes is a new file, or an append to a registry file.

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
   - **The request shapes are published too** (N5 of the re-audit):
     `docs/contracts/schemas/generated/sub-graph-create.schema.json` (`SubGraphCreate`) and
     `sub-graph-body.schema.json` (`SubGraphBody`) exist. The routes take a `dict` body (B1), so
     OpenAPI shows the request bodies as open objects, as it does for `POST /rating-algorithms`.
     The reason for publishing them anyway: WK-675's designer is the first client that authors a
     sub-graph, and `CLAUDE.md` §2 forbids it to hand-write the request type. A schema it can
     generate from is the only way it gets one.
   - `outputs`' items take their schema from `AlgorithmOutput`'s, and `inputs`' items carry
     `name` and `type` (DP-3 item 1).
   - `git grep -n -E '^class (SubGraph|SubGraphBody|SubGraphCreate|SubGraphInputPort)\(' -- packages backend/src`
     prints **exactly four** lines, all in `packages/model-schema/src/model_schema/sub_graphs.py`.
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
   `backend/tests/test_sub_graphs_api.py` (the route). **Every test carries
   `@pytest.mark.req("FR-217")`, and the type-check tests also carry `@pytest.mark.req("FR-227")`.**
   Each case, with its route code (RL-1309 DP-S1-3):
   - a step consumes a name that is neither a declared input port nor produced by a step:
     `RATING_GRAPH_UNRESOLVED_REF`, naming it;
   - a declared output port that no step produces: `RATING_GRAPH_UNRESOLVED_REF`, naming it.
     The shape's message for this case says "undefined value", so the shared mapper (Task 5)
     returns this code (see Task 2);
   - **an output port whose declared type is incompatible with its producing step's result
     type: `RATING_TYPE_MISMATCH`** (FR-227, `03:113`; RL-1309 *Acceptance*, Slice 1). The
     case uses an **`expression` step** with `result_type: "string"` producing an output port
     declared `money_minor`. `compile.py`'s `_compatible` (`:106-111`), called as it stands,
     refuses that pair. The `pricing-core` test also asserts the issue's **`step_id`** (the
     producing step) and **`field == "outputs"`** (N3 of the re-audit). A **new** algorithm-path
     test, `test_an_algorithm_type_mismatch_reports_the_output_step`, asserts the output step's
     `step_id` and `field == "outputs"`. It is new because acceptance 6 forbids changed lines in
     existing tests. Together they prove "behaviour unchanged".
     **Scope (W1 of the plan audit):** FR-227 at create covers only
     producers whose type is known at save, which are an `expression` step's `result_type` and
     an input port's declared type (the rule of `_producer_types`, `compile.py:84-103`). An
     output port produced by a `table`, `lookup` or `model_call` step is not type-checked at
     create, exactly as for an algorithm today. Its type is known only against the pinned
     artifact, at compile;
   - a step that is neither reachable from an input port nor contributing to an output port
     (FR-212's orphan rule, restated for ports): `VALIDATION_FAILED`;
   - a step that produces an input port's name without consuming it: `VALIDATION_FAILED`.
     The input port is that name's first producer, so this is FR-212's "produced by exactly one"
     rule. A step that consumes the port name and re-produces it (the clamp chain) is accepted;
   - a cycle: `RATING_GRAPH_CYCLIC`;
   - two steps with the same `step_id`: `VALIDATION_FAILED`;
   - a body carrying `sub_graphs`: `VALIDATION_FAILED` (DP-4). The shape test also asserts the
     error's `loc` is `("sub_graphs",)` and its type is `extra_forbidden`;
   - an `input` or `output` step inside the fragment: `VALIDATION_FAILED`, because the ports
     replace them;
   - an empty `change_note`: `VALIDATION_FAILED` (DP-1 item 1).

   Each route refusal is a 422, except the create-route cases in 5.
4a. **The code the client sees, per refusal** (the maintainer's note on B1). The owning catalogue
    is `03` §5.1's "Error codes owned by this module" (`03:771-779`) for the rating codes, and
    `backend/src/app/errors.py`'s `_GENERIC_ERROR_CODES` (`:368-370`, "raised by the shared
    request machinery") for the generic ones. Every code below is already registered:
    `RATING_GRAPH_CYCLIC`, `RATING_GRAPH_UNRESOLVED_REF` and `RATING_TYPE_MISMATCH` at
    `errors.py:288-290`, and `VALIDATION_FAILED` and `NOT_FOUND` in the generic set. No code is
    added (RL-1309 DP-S1-3). Each row has one test in `backend/tests/test_sub_graphs_api.py`,
    red first, asserting the HTTP status **and** the problem body's `code`:

    | Refusal | Client sees | Owning catalogue | How the parse path produces it | Test |
    |---|---|---|---|---|
    | A cycle among the fragment's steps | 422 `RATING_GRAPH_CYCLIC` | `03` §5.1 | `SubGraphBody`'s validator raises `GraphCycleError`, a `ValueError` subclass, whose message contains "cycle" (Task 2). Through Task 6, the extracted mapper's substring match on "cycle" returns the code. From Task 7, `graph_validation_error` reads the class from `exc.errors()`: an error whose `type` is `"value_error"` and whose `ctx["error"]` is a `GraphCycleError` | `test_a_cyclic_fragment_is_refused_rating_graph_cyclic` |
    | A step consumes a name no step and no input port produces | 422 `RATING_GRAPH_UNRESOLVED_REF` | `03` §5.1 | the validator raises `GraphUnresolvedRefError`, whose message contains "consumes undefined value". The substring carries it through Task 6, and the class from Task 7 | `test_an_unresolved_consume_is_refused_rating_graph_unresolved_ref` |
    | An output port no step produces | 422 `RATING_GRAPH_UNRESOLVED_REF` | `03` §5.1 | the validator raises `GraphUnresolvedRefError`, whose message contains "undefined value" (Task 2). Through Task 6 that substring gives the code; from Task 7 the class alone does | `test_an_unproduced_output_port_is_refused_rating_graph_unresolved_ref` |
    | An output port's declared type incompatible with its expression producer's `result_type` | 422 `RATING_TYPE_MISMATCH` | `03` §5.1 | the parse succeeds; `fragment_output_type_issues` (Task 4) returns the issue, and `raise_first_issue` raises it with the issue's own code | `test_an_output_port_type_mismatch_is_refused_rating_type_mismatch` |
    | Any other shape refusal: a duplicate `step_id`, a broken re-production chain, an orphan step, a `sub_graphs` field, an `input` or `output` step, an empty `change_note`, or a JSON object missing a required field | 422 `VALIDATION_FAILED` | generic | the mapper's fall-through: through Task 6, when neither "cycle" nor "undefined value" is in the message; from Task 7, when no error carries a graph-error class | `test_a_shape_refusal_is_validation_failed` (parametrised, one case per cause) |
    | A body that is not a JSON object (for example an array or a string) | 422 `VALIDATION_FAILED` | generic | FastAPI refuses it against the `dict[str, Any]` annotation before the handler runs. `errors.py`'s request-validation handler (`:438-465`) returns `VALIDATION_FAILED` | `test_a_non_object_body_is_validation_failed` |
    | `POST /api/v1/sub-graphs` on an existing slug, or a lost numbering race | 409 `VALIDATION_FAILED` | generic | the service's pre-check, or the unique constraint's `IntegrityError`, raises `PlatformError("VALIDATION_FAILED", …, 409, …)` (the form of `objectives.py:229-236`) | `test_create_on_an_existing_slug_is_409`, `test_a_lost_numbering_race_is_409` |
    | `POST /api/v1/sub-graphs/{slug}/versions` on an unknown slug; `GET` of an unknown version | 404 `NOT_FOUND` | generic | the service raises `PlatformError("NOT_FOUND", …, 404, …)` | `test_versions_on_an_unknown_slug_is_not_found`, `test_get_of_an_unknown_version_is_not_found` |

    **The typed signal** (FD working id 9948, fixed by Task 7). The two graph-error classes
    live in a new `packages/model-schema/src/model_schema/graph_errors.py`: `GraphCycleError`
    and `GraphUnresolvedRefError`, both `ValueError` subclasses.
    - **Task 2 creates the module**, and `SubGraphBody`'s validator raises both classes. Its
      messages keep "cycle" and "undefined value", and Task 2's shape tests assert the class
      (`isinstance(err["ctx"]["error"], GraphCycleError)`), never the message text.
    - **Task 7 edits only two things.** First, `RatingAlgorithm._graph_invariants`' two raises:
      the undefined-value raise (`rating.py:418-421`, message at `:419`) and the cycle raise
      (`:439`), with messages unchanged. Second, the mapper's body, which from then on reads
      the class from `exc.errors()` and never reads `str(exc)`.
    - **Through Task 6**, the extracted mapper still matches substrings, unchanged. The
      messages carry the codes on both paths. So every row of this table holds at every task
      boundary, first by the substring, then by the class.
    - **The FR-214 raise stays a plain `ValueError`** (`rating.py:406-408`, "declared output …
      has no output step"). It maps to `VALIDATION_FAILED` before and after Task 7, and a
      characterisation test pins that (Task 5).
    - **The asymmetry is deliberate.** A fragment's unproduced output port maps to
      `RATING_GRAPH_UNRESOLVED_REF`, while an algorithm's FR-214 maps to `VALIDATION_FAILED`.
      - In an algorithm, FR-214 is a wiring rule about **output steps**: a declared output
        lacks the step that emits it. The value reference itself is checked separately, when
        that output step consumes a name. An undefined name there is already
        `RATING_GRAPH_UNRESOLVED_REF`, at `:418-421`.
      - A fragment has no output steps; its ports replace them (acceptance 4). So an output
        port *is* the reference to a named value, and a port whose name no step produces is
        the same defect as a consume of an undefined value. RL-1309 DP-S1-3 names that code.
      - The fragment rule is therefore the analogue of `:418-421`, not of FR-214. Changing
        FR-214's code would change an existing algorithm response, which this slice does not
        do.

    **Precedence, stated so a body with two defects has one answer.** The shape refusals come
    first: a body that fails parsing never reaches the type check. Within the mapper, a
    `GraphCycleError` wins over a `GraphUnresolvedRefError`, which wins over the fall-through.
    That is the order `_parse_algorithm` uses today, so it is unchanged. **That order is not
    observable between two graph errors.** A `model_validator` stops at its first raise, so
    pydantic reports one `ValueError` from it. Which graph error a body with two defects
    reports is decided by the order of the checks inside the validator, not by the mapper. The
    mapper's order matters only if one `ValidationError` carries errors from different
    validators. A test posts a body that has a cycle and a type mismatch together, and
    asserts `RATING_GRAPH_CYCLIC`.
5. **The two create routes and immutability** (`00` FR-4; RL-1309 DP-S1-2), red first:
   - `POST /api/v1/sub-graphs` on a slug that exists returns **409** `VALIDATION_FAILED`, and
     the stored content is byte-identical afterwards;
   - `POST /api/v1/sub-graphs/{slug}/versions` on an unknown slug returns **`NOT_FOUND`**;
   - the server assigns versions as the current maximum plus one. **A lost race is a 409**, in
     the form of `objectives.py:229-236`. It is tested by inserting a row carrying the version the
     service is about to write, between its read of the maximum and its flush (a test double on
     the read), so the unique constraint fires and the service maps the `IntegrityError` to 409;
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
13. **MERGE-ACK.** Before the lead merges, the maintainer's **MERGE-ACK** naming the PR's full head
    SHA is recorded in the lead's local channel file `~/gi-pricing-plan.local/channel/to-lead.md`,
    as `.claude/roles/lead.md:156-157` (rule 4) names. It is never posted on the PR. The slice's
    clean audit is filed. A Slice closes on a clean audit and the lead's merge (`CLAUDE.md` §13).

## Global Constraints

- **Spec first** (`CLAUDE.md` §0): Task 1 lands before any code.
- **No hand-written shape that `model-schema` owns** (`CLAUDE.md` §2). `SubGraphInputPort`,
  `SubGraphBody`, `SubGraphCreate` and `SubGraph` are declared once, in `model-schema`. Output ports
  reuse `AlgorithmOutput`, and there is **no second result-type vocabulary** (RL-1309 DP-3
  item 1).
- **`pricing-core` changes only in `compile.py`'s two type-check functions, one new public entry
  point, and new tests** (RL-1309 DP-S1-4 item 3). `compile_bundle`, the other checks and
  `_compatible` are untouched. `.importlinter` keeps `pricing-core` standalone.
- **One mapping from a shape refusal to its code, never a copy** (B1 of the plan audit). The
  routes take the raw JSON body (`dict[str, Any]`), as `POST /rating-algorithms` does
  (`backend/src/app/api/rating_algorithms.py:35`). The service parses it through a mapper
  extracted from `_parse_algorithm` (`backend/src/app/platform/rating_algorithms.py:25-52`),
  which both artifacts then call. The reason: a typed FastAPI body would be refused by
  FastAPI's request validation (`backend/src/app/errors.py:438-465`) as `VALIDATION_FAILED`
  before the service runs. The codes RL-1309 DP-S1-3 names, `RATING_GRAPH_CYCLIC` and
  `RATING_GRAPH_UNRESOLVED_REF`, could then never be returned (Task 5).
- **That mapping's defect is fixed in this slice's last task** (FD working id 9948, LOW, owned
  by WK-1250 Slice 1). This supersedes N2's "record the limitation only".
  - **The defect.** Today's mapper matches substrings of `str(exc)`, and pydantic's message
    echoes the offending `input_value`. So a refusal whose echoed input contains "cycle" maps
    to `RATING_GRAPH_CYCLIC`, whatever its cause: for example an unknown field named
    `cycle_note`. auditor-plans reproduced this on `main`. It is a wrong code on a refusal, so
    it fails closed.
  - **The fix.** This slice extracts the mapper anyway, so Task 7, its last code task, switches
    it to the typed signal (acceptance 4a) as the same writer.
  - **Until then**, the mis-map is pinned only as a known bug, never as expected behaviour: its
    characterisation case is `xfail(strict=True)` (Task 5), and Task 7 turns it green.
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
| a | No sub-graph table, route or service exists | `git grep -n -i 'sub_graph\|subgraph' -- backend/src ':(glob)packages/*/src/**'` prints 8 lines, none under `backend/src`: `model_schema/__init__.py:282,669`, `model_schema/rating.py:340,343,390`, `model_schema/refs.py:25`, and `pricing_core/rating/score.py:399,401` |
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
- [ ] Confirm the resolutions of map DP-1, DP-3, DP-4 and DP-S1-1 to DP-S1-4 **by record id**
  (RL-1309) in the ledger, and stop if any differs from **Decision points**.
- [ ] Confirm the dispatch record's RL-1263 write-set check, and its gate-slot rule.
- [ ] **Spike the typed signal; do not assume it** (`library-spike`). At this tree's pydantic
  version, assert that a `ValueError` subclass raised inside a `model_validator(mode="after")`
  surfaces in `ValidationError.errors()` as `type == "value_error"`, with the instance at
  `ctx["error"]`, on the model and on a subclass model. Quote the script and its output in the
  ledger. auditor-plans observed this at pydantic 2.13.5; the executor re-proves it at the
  dispatch tree. If it does not hold, stop and report: the alternative, a `PydanticCustomError`
  with its own `type`, changes Tasks 2 and 7.
- [ ] **At the second merge**, if the other lane's slice merges first: merge `origin/main` in,
  re-point `down_revision` to one head, regenerate `docs/contracts/` and `docs/INDEX.md` (never
  hand-merged), and re-run Task 8's full gate.

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

### Task 2: `model-schema` — `SubGraphInputPort`, `SubGraphBody`, `SubGraphCreate`, `SubGraph` and the contract

**Files:** Create `packages/model-schema/src/model_schema/sub_graphs.py`,
`packages/model-schema/src/model_schema/graph_errors.py` (`GraphCycleError` and
`GraphUnresolvedRefError`, both `ValueError` subclasses with no body beyond a docstring) and
`packages/model-schema/tests/test_sub_graph.py`. Modify `packages/model-schema/src/model_schema/__init__.py`
(the exports, beside `SubGraphRef` at `:282` and `:669`) and `scripts/generate-contracts.py`
(register `"sub-graph": "SubGraph"`, `"sub-graph-create": "SubGraphCreate"` and
`"sub-graph-body": "SubGraphBody"` at `:39-101`; acceptance 2). Regenerate `docs/contracts/`.

**Interfaces:**
- Produces:
  - `SubGraphInputPort`: `name: str` and `type: RatingResultType`;
  - `SubGraphBody`: `inputs: list[SubGraphInputPort]`, `outputs: list[AlgorithmOutput]`,
    `steps: list[RatingStep]` and `change_note: str` (non-empty);
  - `SubGraphCreate(SubGraphBody)`, which adds `slug: Slug`. It is the request body of
    `POST /api/v1/sub-graphs`, whose path carries no slug (B2 of the plan audit).
    `POST /api/v1/sub-graphs/{slug}/versions` takes `SubGraphBody`, with the slug from its path;
  - `SubGraph(SubGraphCreate)`, which adds `version: int`. It is the stored and returned shape.

  All four are `frozen=True, extra="forbid"`, and the fragment's invariants are validated once,
  on `SubGraphBody`.

- [ ] **Red first:** acceptance 4's shape-level cases, plus one positive test that the Task 1
  example parses. **Predicted red:** `ImportError` on `model_schema.sub_graphs` for every test.
- [ ] Implement.
  - The invariant check reuses `_produced_by` and `_consumed_by` (premise e). The rules, each
    worded so that the shared mapper (Task 5) returns the code acceptance 4 names:
    - **An input port is a producer** of its name. A step that consumes a name produced by no
      step and no input port is refused by raising `GraphUnresolvedRefError`, with a message
      containing "consumes undefined value" in `_graph_invariants`' own wording. It maps to
      `RATING_GRAPH_UNRESOLVED_REF`.
    - **Each output port must be produced by a step.** One that is not is refused by raising
      `GraphUnresolvedRefError("output port {name!r} is an undefined value: no step produces it (FR-212)")`.
      It maps to `RATING_GRAPH_UNRESOLVED_REF`. The message keeps "undefined value" because
      the substring mapper carries it through Task 6.
    - **Re-producing an input port's name** follows `_graph_invariants`' chain rule, with the
      port as the first producer. A step that produces the name without consuming it is refused
      ("do not form a single re-production chain"), which maps to `VALIDATION_FAILED`.
    - **FR-212's orphan rule, restated for ports:** a step that is not reachable from any input
      port and contributes to no output port is refused, which maps to `VALIDATION_FAILED`.
    - A cycle raises `GraphCycleError`, with a message containing "cycle", which maps to
      `RATING_GRAPH_CYCLIC`.
    - Every other refusal raises a plain `ValueError`, which maps to `VALIDATION_FAILED`.
  - The shape tests assert the class of each graph refusal
    (`isinstance(err["ctx"]["error"], GraphUnresolvedRefError)`), and a plain `ValueError` for
    the others, never the message text.
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
`_producer_types`, `_check_result_types` and the new public functions named below. Add new tests only to
`packages/pricing-core/tests/test_rating_compile.py`.

**Interfaces:**
- Produces, in `compile.py` (B3 of the plan audit):
  - **`producer_types(steps: Sequence[RatingStep], typed_names: Mapping[str, str]) -> dict[str, str]`**,
    the shared core of `_producer_types`;
  - **`output_type_issues(producer_types: Mapping[str, str], outputs: Sequence[tuple[str, str, str, str]]) -> list[ValidationIssue]`**,
    the shared core of `_check_result_types`. Each tuple is (the step id to report, the output's
    name, its declared type, the name that feeds it), and each issue carries that step id and
    `field="outputs"`, as today's issue does (`compile.py:129-137`) (N3 of the re-audit).
    - The wrapper `_check_result_types(algo)` builds the tuples from `algo`'s output steps, and
      **keeps both of today's skips**: an output step whose name is not declared, and one that
      consumes nothing (`declared is None or not consumed`, `:124`). It passes the output
      step's `step_id`.
    - For a fragment, the step id is the producing step's id;
  - **`fragment_output_type_issues(steps: Sequence[RatingStep], input_ports: Sequence[SubGraphInputPort], output_ports: Sequence[AlgorithmOutput]) -> list[ValidationIssue]`**,
    the fragment entry point, which Task 5's create path calls.

  All three are public and added to `__all__`, and none begins `_check_`. The #967 slice's
  closure test (its acceptance 3c (ii)) reds any module-level `_check_*` function missing from
  its registries. `ALGORITHM_CHECKS` is typed `Callable[[RatingAlgorithm], list[ValidationIssue]]`.
  So **`_check_result_types(algo: RatingAlgorithm)` keeps its signature** as a thin wrapper over
  `output_type_issues`, and stays registered. **`_producer_types(algo)`** stays as a thin wrapper
  over `producer_types`. The names are proposals, and the ledger records the names used.

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
- [ ] Add `fragment_output_type_issues`. It builds `producer_types` from the steps plus the
  input ports' declared types, and applies `output_type_issues` to the output ports, issuing
  `RATING_TYPE_MISMATCH` with the port name.
  - **The producing step's id.** In the same pass over `steps`, the function builds a
    `name → step_id` map. It uses the same last-in-list-order-wins rule as `producer_types`,
    so the id reported is that of the step whose type was compared.
  - Every tuple carries a step id, so the id slot is `str`. An output port whose name only an
    input port produces is refused earlier, by Task 2's rule that each output port is produced
    by a step: `GraphUnresolvedRefError`, so 422 `RATING_GRAPH_UNRESOLVED_REF` (4a's
    unproduced-port row). No `None` path reaches this function (X1 and X2 of the re-audit).
  - The `pricing-core` test asserts the id on a two-step fragment, so the wrong step would
    fail it.
- [ ] Green. Run acceptance 6: the existing tests pass unmodified. **Run the #967 slice's closure
  test 3c**, which must pass with `_check_result_types` still registered and no new `_check_*`
  function. Commit: `refactor(rating): FR-227's result-type check over steps and declared outputs, and a fragment entry point (WK-1250 S1)`.

### Task 5: The service and the resolver

**Files:** Create `backend/src/app/platform/sub_graphs.py` and
`backend/tests/test_sub_graphs_service.py`.

**Interfaces:**
- Consumes: `SubGraphInputPort`, `SubGraphBody`, `SubGraphCreate` and `SubGraph` (Task 2);
  `SubGraphVersionRow` (Task 3); `fragment_output_type_issues` (Task 4); `audit.record`
  (`audit.py:52`).
- Modifies: `backend/src/app/platform/rating_algorithms.py`. `_parse_algorithm`'s
  `ValidationError` → `PlatformError` mapping (`:34-52`: "cycle" → `RATING_GRAPH_CYCLIC`,
  "undefined value" → `RATING_GRAPH_UNRESOLVED_REF`, otherwise `VALIDATION_FAILED`) is
  extracted into a public `graph_validation_error(exc: ValidationError, *, artifact: str) -> PlatformError`.
  `_parse_algorithm` calls it with `artifact="rating algorithm"`, and the sub-graph service with
  `artifact="sub-graph"`. This is one mapping, never a second copy (B1).
  - **What `artifact` parameterises** (N1 of the re-audit): only two strings. The fall-through
    title, "Rating algorithm is invalid" (`:52`), becomes f"{artifact.capitalize()} is invalid",
    and the cyclic detail, "A rating algorithm is a directed acyclic graph (FR-212)." (`:41`),
    becomes f"A {artifact} is a directed acyclic graph (FR-212).". Every other string is fixed,
    and so is the match order: the cyclic title "Rating graph is cyclic", the undefined-value
    title "Rating graph references an undefined value", and its detail "Every consumed value is
    produced by a step (FR-212).". With `artifact="rating algorithm"`, every string is
    byte-identical to today's. `_issues_to_error(algorithm)` (`:58-69`) is split the same way. Its tail, which maps the first
  `ValidationIssue` of a list to a `PlatformError`, becomes a public
  `raise_first_issue(issues: list[ValidationIssue]) -> None`. It raises for the first issue,
  and **on an empty list it returns without raising** (N4 of the re-audit), as `_issues_to_error`
  does today when `validate_algorithm` returns nothing (`:61-62`). `_issues_to_error` calls
  `raise_first_issue(validate_algorithm(algorithm))`, and the sub-graph service calls it for the
  `RATING_TYPE_MISMATCH` refusal.
- Produces:
  - `create_sub_graph(database, workspace_id, actor, content: dict[str, Any]) -> SubGraph`:
    parses `content` as `SubGraphCreate` through `graph_validation_error`, and writes version 1,
    with a 409 if the slug exists;
  - `create_version(database, workspace_id, actor, slug, content: dict[str, Any]) -> SubGraph`:
    parses `content` as `SubGraphBody` the same way, and writes the maximum plus one, with
    `NOT_FOUND` for an unknown slug;
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
  - Before writing, call `fragment_output_type_issues` and refuse on its first issue, through
    `raise_first_issue`.
  - **Characterisation first, then the extraction** (N1 of the re-audit). Today
    `backend/tests/test_rating_algorithms.py` covers only the cyclic branch (`:86`) and the
    unguarded-division issue path (`:105`). So, **before** extracting, add four tests to that
    file (new tests only; it joins the write set):
    - `test_an_undefined_value_is_refused_with_rating_graph_unresolved_ref`: 422, `code`
      `RATING_GRAPH_UNRESOLVED_REF`, and the title and detail above;
    - `test_another_shape_refusal_is_validation_failed`: for example a duplicate `step_id`; 422,
      `code` `VALIDATION_FAILED`, title "Rating algorithm is invalid";
    - `test_an_unknown_field_named_cycle_note_is_validation_failed`: an algorithm body carrying
      an extra field `cycle_note`; 422, `code` `VALIDATION_FAILED`. It is marked
      `@pytest.mark.xfail(strict=True, reason="FD working id 9948: str(exc) substring match mis-maps to RATING_GRAPH_CYCLIC")`,
      so it does **not** pin the bug as behaviour. A sub-graph twin in
      `backend/tests/test_sub_graphs_api.py` carries the same mark. Task 7 turns both green and
      removes both marks;
    - `test_a_declared_output_without_an_output_step_is_validation_failed`: the FR-214 raise
      (`rating.py:406-408`); 422, `code` `VALIDATION_FAILED` (M1 of the re-audit). It stays
      green through Task 7, which leaves that raise a plain `ValueError`.

    Each asserts the status, `code`, `title` and `detail` exactly. The first, second and fourth
    are **green before** the extraction and **green after**, as are the two existing tests. The
    third is `XFAIL` before and after. That proves every branch of
    the mapping keeps its behaviour. The ledger quotes both runs.
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
  documented codes. **The body is `dict[str, Any]`**, as `POST /rating-algorithms` takes it
  (`api/rating_algorithms.py:35`), so that the service's mapper, not FastAPI's request
  validation, chooses the code (B1). OpenAPI therefore shows the two request bodies as open
  objects, as it does for `POST /rating-algorithms`. The request shapes are published as JSON
  Schemas through `generate-contracts.py`'s registry instead (acceptance 2, N5).
- [ ] Regenerate the contracts, confirm `--check` exits 0, and run the authorisation sweep and
  `backend/tests/test_demo_guide.py`.
- [ ] Green, and commit.

### Task 7: The typed-signal fix (FD working id 9948) — the last code task

**Files:**
- Modify `packages/model-schema/src/model_schema/rating.py`, only two raises in
  `_graph_invariants`. The undefined-value raise (`:418-421`) raises `GraphUnresolvedRefError`,
  and the cycle raise (`:439`) raises `GraphCycleError`, both with unchanged messages. The
  FR-214 raise (`:406-408`) is not touched.
- Modify `backend/src/app/platform/rating_algorithms.py`, only `graph_validation_error`'s body.
- In the tests, remove the two `xfail` marks from Task 5, and add the model-schema class test
  below.
- `graph_errors.py` and `sub_graphs.py` exist from Task 2 and are not edited here. The signal
  was proven in Task 0.

- [ ] **Red first:** the two `xfail(strict=True)` cases report `XFAIL`. **Remove the marks
  first**, and they go red: `RATING_GRAPH_CYCLIC` where `VALIDATION_FAILED` is expected. That
  red is the proof.
- [ ] Rewrite `graph_validation_error` to walk `exc.errors()`. A `GraphCycleError` maps to
  `RATING_GRAPH_CYCLIC`, then a `GraphUnresolvedRefError` to `RATING_GRAPH_UNRESOLVED_REF`, and
  anything else to `VALIDATION_FAILED`. Titles and details are as Task 5 fixed them. It never
  reads `str(exc)`.
- [ ] Green:
  - the two formerly-xfail cases;
  - every acceptance 4a row;
  - `test_rating_algorithms.py`'s four characterisation tests (the FR-214 case still
    `VALIDATION_FAILED`) and its two existing tests;
  - `packages/model-schema/tests/test_rating_algorithm.py`, unchanged;
  - a new model-schema test asserting the class of the `:418-421` and `:439` raises, and that
    the FR-214 raise is not a graph-error class.
- [ ] Commit: `fix(rating): map graph refusals on a typed signal, not str(exc) (FD working id 9948, WK-1250 S1)`.

### Task 8: The gate and the ledger

- [ ] Run `tests/test_repository_invariants.py`, the migration round trip, then the full
  two-half gate under a gate slot. Quote every rc, the `N passed` line and `HEAD`.
- [ ] The ledger records:
  - the tree, and premises a–n with m mapped;
  - the red-first quotes;
  - RL-1309 as the ruling;
  - the name of Task 4's entry point;
  - FR-217's partial verdict (acceptance 11);
  - the names of `graph_validation_error` and `raise_first_issue`, if they differ from the
    proposals;
  - any re-pointed `down_revision`;
  - FD working id 9948's fix: the two formerly-xfail cases green, with the red quoted when the
    marks were removed.
- [ ] The MERGE-ACK (acceptance 13).

## Hand-off

Slice 2 (the pin and the inlining) starts after this slice closes. It consumes `resolve_ref`,
`SubGraph` and the typed ports from here, and it builds on Task 4's refactor rather than undoing
it: the inlined algorithm goes through the algorithm path (RL-1309 DP-S1-4 item 2). Slice 2's
leaf plan carries these:
- RL-1309's DP-1 items 3 and 5;
- DP-1 item 6's G1, G2 and G4. G1 is narrowed to `SubGraphRef` against `Pins.sub_graphs`, and
  reuses PL-1299's `check_step_refs_pinned` (FD-1297) over the inlined algorithm.
  - **G1's objective clause** stays Slice 2's: an unapproved custom objective reached through an
    inlined `model_call` is refused at compile. This is the maintainer's entry in
    `~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 10:06:52 BST — DECISION (maintainer by delegation): owner of #938 G1's objective clause; …",
    as RL-1309's G1 records it.
  - **The "built once" rule** (RL-1309, G1): whichever Work lands the transitive model →
    objective compile check first builds it, and the other calls it and never copies it. The
    builder records its symbol and file in its slice ledger;
- DP-3 items 3–5;
- DP-S1-4 item 6, the four checks on the inlined algorithm, where a fragment with a
  non-deterministic expression is refused at compile, red first;
- the whichever-lands-second rule with WK-673 Slice 5. If Slice 5 merged first, Slice 2's test
  asserts the diff limb in the **persisted** evidence. If Slice 2 merged first, Slice 5 carries
  the re-point case;
- the gate on the diff limb. **Slice 2 does not dispatch until an in-repo record carries the
  limb verbatim, citing RL-1309**: WK-673's Slice 5 leaf plan, or a WK-673 slice ledger's Task
  0, whichever lands first. A local file does not satisfy it. This is the maintainer's entry in
  `~/gi-pricing-plan.local/channel/to-lead.md`, "2026-09-30 14:47:19 BST — RL-1309:309-311's gate: NO, a local delta file doesn't satisfy it;
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
  `fragment_output_type_issues` and the service functions.
- **Open:** nothing is open for the decision-maker. RL-1309, #969 and this plan are unminted.
