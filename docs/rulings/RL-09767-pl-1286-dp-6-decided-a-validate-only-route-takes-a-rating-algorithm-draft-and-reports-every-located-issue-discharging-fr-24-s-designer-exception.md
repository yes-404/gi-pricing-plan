---
id: RL-9767
family: ruling
title: PL-1286 DP-6 decided — a validate-only route takes a RatingAlgorithmDraft and reports every located issue through the server's own checks, discharging FR-24's designer exception
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-01
owner: decision-maker
tree: 8bd782acbbdde8e3b4195b5a0acb89183b5a0253
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1286, FR-24, FR-212, FR-214, FR-219, FR-223, FR-227, FR-244, FR-246, FR-276, FD-1335, FD-1366, FD-1374]
---

# RL-9767 — PL-1286 DP-6 decided: a validate-only route takes a `RatingAlgorithmDraft` and reports every located issue through the server's own checks, discharging `00` FR-24's designer exception

## How this was ruled

**Ruled 2026-10-01 10:12 BST at effort `medium`** by the decision-maker session
`dm-675dp56`, on the same commission as RL 9766 (working id), which rules DP-5. That record's
*How this was ruled* section gives the effort check and the commission. **Working id 9767**,
allocated by the lead. It is minted at its merge turn, and every `RL-<this>` placeholder
below is then this record's minted id.

**Evidence tree:** origin/main `1dd5e264` (tree `8bd782ac`), unchanged between 10:08 and
10:12 BST. **Not touched:** DP-3 (`OQ-1223`) and DP-7 (`OQ-1285`), held until Saturday's
scope freeze.

## The question

`PL-1286` DP-6 (`PL-1286`:245 at this tree). The designer's on-node live validation is one
of `00` FR-24's seven exceptions. It stays binding until it is discharged, either by a
numbered requirement or by a cell declared exhaustive (`docs/specs/00-overview.md:229`). What
discharges it, and how does the view validate a graph before save? It gates Slice 3's leaf
plan going `active`.

## Evidence at `1dd5e264`

- **The obligation.** `03` §5.3's *Interaction requirement* (`03-rating-engine.md:1101-1104`):
  an invalid graph must be "*visibly* invalid before save — a step referencing an undefined
  value shows the error on the node, not in a save-time toast". The designer cell names
  "cycles, unresolved refs, type mismatches" (`:1094`).
- **Save today.** `POST /rating-algorithms` (`backend/src/app/api/rating_algorithms.py:28-50`)
  takes `body: dict[str, Any]` and returns `dict[str, Any]`. It is one of FD-1366's five untyped request bodies. The service (`backend/src/app/platform/rating_algorithms.py`):
  - `_parse_algorithm` (`:68-73`) parses `RatingAlgorithm` and maps a shape refusal with
    `graph_validation_error` (`:32-65`);
  - `_issues_to_error` (`:89-91`) runs `validate_algorithm` and **refuses on the first
    issue only** (`raise_first_issue`, `:76-86`).
- **The graph invariants live in the shape, not in a function.** `RatingAlgorithm`
  (`packages/model-schema/src/model_schema/rating.py:374`) enforces FR-212 and FR-214 in a
  `model_validator`. That validator **raises on the first breach** (`:400-470`):
  - `GraphUnresolvedRefError` names the step only inside its message;
  - `GraphCycleError` names no step at all;
  - the other breaches (an output with no output step, an ambiguous producer, an orphan)
    raise a plain `ValueError`, which save maps to `VALIDATION_FAILED`.
  The two error classes are in `model_schema/graph_errors.py:11-16`.
- **The deeper checks return located issues.** `validate_algorithm(algo: RatingAlgorithm)
  -> list[ValidationIssue]` (`packages/pricing-core/src/pricing_core/rating/compile.py:366-392`)
  runs `STRING_CHECKS` and `ALGORITHM_CHECKS` (`:359-363`: result types, input-bound scale,
  clamp placement). `ValidationIssue` (`compile.py:60-72`) is `{code, message, step_id,
  field}`, a pricing-core class. `rate_tables/operations.py:57` imports it from there.
  `03` §5.2 shows the signature (`:907`).
- **The route can't take `RatingAlgorithm` as its body.** FastAPI validates the body before
  the handler runs, so a cyclic or unresolved graph is refused by the shape's validator. It
  never reaches the handler, and it comes back as a generic request-validation 422
  (`backend/src/app/errors.py:455-470`), not as an issue on a step. **The plan's option (a)
  works only with a body type that does not enforce the invariants.** The plan does not say
  this.
- **The request-validation problem locates field errors.** `_handle_validation_error`
  (`errors.py:455-470`) drops the leading `body` segment. A field error in step 3 therefore
  reads `steps.3.<field>`.
- **The type gap.** At this tree `docs/contracts/openapi/generated.json`
  `components.schemas` holds the step classes and `AlgorithmOutput` but not
  `RatingAlgorithm` (F2 condition 1 is S2's). Neither `RatingAlgorithmDraft`,
  `AlgorithmValidationReport` nor `rating-algorithms/validate` exists anywhere in
  `packages/`, `backend/`, `docs/` or `frontend/src` (grep, 10:1x BST).
- **FR-223 has no code path at save.** `MODEL_REFERENCE_MODE_INCONSISTENT` (FR-223,
  `03:109`) is emitted nowhere in `backend/src` or `packages/*/src`. The check,
  `check_model_reference_mode` (`rating.py:172`), raises a bare `ValueError` at compile
  (`compile.py:614`). It needs the Rating Version, which an algorithm save does not have.

## Options

| | Option | Assessment |
|---|---|---|
| (a) | A numbered `03` FR, served by a validate-only route running the server's own checks (the plan's (a)) | The rules stay defined once. It needs a body type without the invariants, located graph issues, and a model-schema response, none of which exists yet. |
| (b) | The FR, with the cycle, reference and type checks re-implemented in the frontend (the plan's (b)) | Two definitions of the save rules, the divergence `CLAUDE.md` §2 forbids. The expression checks (FR-244, FR-276) cannot be re-implemented without the engine. |
| (c) | Declare the cell exhaustive and validate on save only (the plan's (c)) | Fails the *Interaction requirement*: an error appears only at save. |
| (d) | *(not in the plan)* A `dry_run` flag on `POST /rating-algorithms` | One route with two 2xx meanings (201 saved, 200 not saved), on a handler under FD-1366's per-route hold. Save also still reports only the first issue. |
| (e) | *(not in the plan)* Save each edit as a new algorithm version | Versions are immutable. It writes one version per keystroke and still reports one issue. |
| (f) | *(not in the plan)* Run `pricing-core` in the browser (Pyodide) | One definition, but a new runtime dependency of tens of MB in the designer chunk, against F2 condition 3's bundle split. |

## Ruled

**(a), with the body the plan did not name.** `03` gains a numbered FR (T1) that discharges
`00` FR-24's `03` DAG designer exception (T4). The FR is served by
**`POST /api/v1/rating-algorithms/validate`**:

1. **The body is `RatingAlgorithmDraft`**, a new `model-schema` type with the field set of
   `RatingAlgorithm` and none of its graph invariants. `RatingAlgorithm` becomes
   `RatingAlgorithmDraft` plus the invariants, as a subclass in
   `packages/model-schema/src/model_schema/rating.py`, so the field set is written once.
2. **The invariants become one function returning every breach detectable on the graph as
   it stands, located.** *(Amended 2026-10-01 10:23 BST, auditor-1055 findings A and B: this
   item said "every located breach", and a cycle named "every step that the topological sort
   leaves unordered".)* `RatingAlgorithm`'s validator calls the function and raises on the
   first breach it returns, with the same exception classes it raises today, so
   `graph_validation_error` and every save code are unchanged. The validate route calls the
   same function and reports all the breaches it returns. **The checks run in today's order
   (`packages/model-schema/src/model_schema/rating.py:395-475`), and the issues are returned
   in that order.** Acceptance 5's first-issue parity depends on it:
   1. **Duplicate `step_id`** (FR-215, `:397-399`): one `VALIDATION_FAILED` issue per
      duplicated id, carrying that `step_id`. **It stops the remaining graph checks.** Every
      later check keys steps by `step_id` (`dependencies`, `step_by_id`), so duplicates would
      collapse and the later results would be wrong.
   2. **A declared output with no output step** (FR-214): one `VALIDATION_FAILED` issue per
      output, with no `step_id`. The checks continue.
   3. **Unresolved reference** (FR-212): one `RATING_GRAPH_UNRESOLVED_REF` issue per
      consuming step and name, carrying the consuming step's `step_id`. The checks continue.
      An unresolved name adds no dependency edge.
   4. **Cycle** (FR-212): one `RATING_GRAPH_CYCLIC` issue per step **on** a cycle, meaning a
      step that reaches itself through the dependency edges (a step's edge to itself stays
      excluded, as today). A step that the sort leaves unordered only because it is
      downstream of a cycle gets no issue. This set is not computed today, because the
      validator raises a `GraphCycleError` that names no step. The function computes it from
      the unordered steps.
   5. **Ambiguous producer** (FR-212, `:444-455`): one `VALIDATION_FAILED` issue per later
      producer that does not consume the name, carrying its `step_id`. **Skipped after a
      cycle.** It orders producers by topological position, which does not exist then.
   6. **Orphan** (FR-212): one `VALIDATION_FAILED` issue per orphan step, carrying its
      `step_id`. It runs after a cycle as well, because reachability needs no order.

   **"Defined once" holds for algorithms only** (finding C). `SubGraphBody` has its own
   parallel `_graph_invariants` (`packages/model-schema/src/model_schema/sub_graphs.py:62-151`),
   which calls `RatingAlgorithm._reachable` and `_reaches_output` (`:118`, `:122`). The
   extraction keeps those two callable from there, and S3's leaf plan names that. Sub-graph
   validation is not part of this route.
3. **Once the invariants hold, the route runs `validate_algorithm`** on the
   `RatingAlgorithm` and appends its issues. Its checks read a valid graph, so until the
   invariants hold, the report carries the graph issues only.
4. **The response is `AlgorithmValidationReport`**, a new `model-schema` type,
   `{"issues": [ValidationIssue, …]}`. `ValidationIssue` **moves** from
   `pricing_core/rating/compile.py:60` to `model-schema` unchanged
   (`{code, message, step_id, field}`). `pricing-core` imports it from there, so it is not
   defined twice, and `03` §5.2's signatures do not change.
5. **200 whether or not issues are found.** The report is the resource. An empty `issues`
   list means save-time validation would pass. A **422** `VALIDATION_FAILED` with field-level
   errors answers only a body that is not a `RatingAlgorithmDraft`. Its `field` begins
   `steps.<index>.`, so the view can still place it on a node.
6. **`rating:write`.** The route exists for authoring, and only an author can save what it
   validates. It writes nothing, persists nothing and records no audit event.
7. **FR-223 is out of the route.** It needs the Rating Version, and its code is emitted
   nowhere today (Evidence; FD 9759, working id). *(Reworded 2026-10-01 10:23 BST, on the
   lead's note.)* The reasoning: S2 shows a `model_call` step's mode read-only from the
   version (`PL-1286` S2), so the designer should not introduce a mismatch while editing.
   This is an inference, not a guarantee. A mismatch arises where a version pins an
   algorithm, and that check stays FR-223's, at compile.

**Why.** (a) is the only option that keeps one definition of the save rules and still shows
an error on the node before save. Without points 1 and 2, the route's body type would refuse
the very graphs it exists to report on, or it would echo save's first-issue-only refusal. Both
fail the *Interaction requirement*. Points 1, 2 and 4 each make one existing definition
reachable from a second caller. None adds a second definition.

**The route this ruling creates, and its types.**

| Method, path | Request body | 2xx response | Permission |
|---|---|---|---|
| `POST /api/v1/rating-algorithms/validate` | `RatingAlgorithmDraft`, **new**, `packages/model-schema/src/model_schema/rating.py` (the base class of `RatingAlgorithm`, `:374`) | **200** `AlgorithmValidationReport`, **new**, same file; its items are `ValidationIssue`, **moved** from `packages/pricing-core/src/pricing_core/rating/compile.py:60` into the same file | `rating:write` |

No `dict[str, Any]` appears in the signature. The path does not clash: `POST
/rating-algorithms` has no suffix, the diff route and DP-4's coming load route are `GET`, and
`validate` contains no `@`.

**Not decided here.**

- **The FR-223 code gap** (`MODEL_REFERENCE_MODE_INCONSISTENT` is specified and never
  emitted) is being filed separately as FD 9759 (working id).
- **FR-246's declared-inputs rule** is unenforced (`FD-1374`, open; FD 9773 (working id)
  when ruled). The route
  reports what `validate_algorithm` checks, so when that rule is enforced there, the route
  reports it with no change here.
- **How often the designer calls the route** (debounce, cancellation of stale calls) is S3's
  leaf plan's to state. No NFR is set here.

## Spec changes this ruling requires

These are applied by **Slice 3's spec-first step** under `.claude/skills/spec-change`, in the
same commit as the route's code and tests (`CLAUDE.md` §2). They are not applied in this
commit, and `PL-1286` is not edited. Placement was read at origin/main `1dd5e264`, and
re-read at main `ef5dc6e7` on 2026-10-05: each anchor below is found there exactly once,
and each line hint is main's.

Placeholders: `RL-<this>` is this record's minted id. `FR-<new>` is the requirement id minted
for T1 when it is applied. `<date>` is the date of the applying commit. Nothing else in a
text is a placeholder.

**T1 — `03` §3.1, a new FR.** Placement: `docs/specs/03-rating-engine.md`, §3.1 *Rating
algorithms*. **Insert one new row immediately after the row that begins `| **FR-219** |`**
(`:88`), as the last row of that table. Nothing is struck.

```text
| **FR-<new>** | **The designer validates a graph before save through the server's own checks, and shows each issue on the step it names.** *(Added <date>, `RL-<this>`, `PL-1286` DP-6; discharges `00` FR-24's `03` DAG designer exception.)* `POST /api/v1/rating-algorithms/validate` takes an unsaved algorithm as a `RatingAlgorithmDraft` (§4.1) and answers **200** with an `AlgorithmValidationReport` listing the issues that saving the same algorithm would refuse on: every breach of the graph invariants (FR-212, FR-214, FR-215) detectable on the graph as it stands, in the order §4.1 states, and, once those invariants hold, every issue `validate_algorithm` returns (§5.2; FR-227 and the expression checks of §3.5). Each issue carries its code, a message, and the `step_id`, and the field where there is one, that it is located on. A cycle names each step that lies on it, not the steps merely downstream of it; an issue no single step owns carries no `step_id`. An empty list means save-time validation would pass. The rules are defined once: the route and save run the same functions, and the frontend re-implements none of them. Save is unchanged and still refuses on the first issue with its code. Validation requires `rating:write`, and it writes nothing, persists nothing and records no audit event. The DAG designer calls the route as the graph changes and renders each located issue on its node before save (§5.3, *Interaction requirement*); an issue without a `step_id` is shown on the graph, never only in a save-time toast. FR-223's mode check is not part of this route: it needs the Rating Version, and the designer shows a `model_call` step's mode read-only from the version. |
```

**T2 — `03` §5.1, one row.** Placement: the §5.1 table. **Insert this row immediately
after the row that begins `| `GET` | `/api/v1/rating-algorithms/{slug}@{version}/diff?against=` |`**
(`:896`). Nothing is struck.

If RL 9907 (working id)'s `Permission` column has not landed in `03` §5.1 when this row is applied, the row is applied in its three-cell form:

```text
| `POST` | `/api/v1/rating-algorithms/validate` | Validate an unsaved algorithm without saving it (FR-<new>); requires `rating:write`. The body is a `RatingAlgorithmDraft` (§4.1). **200** with an `AlgorithmValidationReport`, whose `issues` list is empty when save-time validation would pass; 401; 403; **422** `VALIDATION_FAILED` with field-level errors only for a body that is not a `RatingAlgorithmDraft`. Nothing is persisted. **Added <date>** (`RL-<this>`) |
```

If RL 9907 (working id)'s `Permission` column has landed in `03` §5.1 when this row is applied, the row carries a fourth cell, `rating:write`, and is applied in its four-cell form instead:

```text
| `POST` | `/api/v1/rating-algorithms/validate` | Validate an unsaved algorithm without saving it (FR-<new>); requires `rating:write`. The body is a `RatingAlgorithmDraft` (§4.1). **200** with an `AlgorithmValidationReport`, whose `issues` list is empty when save-time validation would pass; 401; 403; **422** `VALIDATION_FAILED` with field-level errors only for a body that is not a `RatingAlgorithmDraft`. Nothing is persisted. **Added <date>** (`RL-<this>`) | `rating:write` |
```

*(The four-cell form was added 2026-10-01 10:28 BST, on finding F-3.)*

**The permission names exist** (pasted on the maintainer's addition, 2026-10-01 10:28 BST). Run at origin/main `1dd5e264`:
`git grep -n -E 'RATING_(READ|WRITE) = ' origin/main -- packages/model-schema/src/model_schema/permissions.py`
and `` git grep -n -E '^> \| `rating:(read|write)` \|' origin/main -- docs/specs/06-governance.md ``.
The second command's hits are rows of `06` §4.1's *Built and now specified* table, which starts at `06:260`. That table "has exactly one row per member of `model_schema.Permission`". Output, verbatim:

```text
origin/main:packages/model-schema/src/model_schema/permissions.py:47:    RATING_READ = "rating:read"
origin/main:packages/model-schema/src/model_schema/permissions.py:48:    RATING_WRITE = "rating:write"
origin/main:docs/specs/06-governance.md:278:> | `rating:read` | Reading Rating Algorithms, Sub-graphs, Regression Suites, Rate Tables, Rating Versions and scoring traces |  |
origin/main:docs/specs/06-governance.md:279:> | `rating:write` | Writing Rating Algorithms and Rate Tables, and creating a Rating Version (`RL-1236` DP-A) |  |
```

**T3 — `03` §4.1, a dated note.** Placement: §4.1 `RatingAlgorithm`. **Insert one new
paragraph, preceded by a blank line, immediately after the paragraph ending
`and unreferenced by an `output` (FR-212).`** (`:287-289`), and before `### 4.2`. Nothing
is struck.

```text
*(Added <date>, `RL-<this>`.)* **`RatingAlgorithmDraft`** is the same field set without the invariants above. It is the body of `POST /api/v1/rating-algorithms/validate`, so a graph that breaks an invariant reaches the validator and is reported, rather than refused before it (FR-<new>). `RatingAlgorithm` is `RatingAlgorithmDraft` plus the invariants, defined in `model-schema` as its subclass, so the field set is written once. The invariants are one function returning every breach detectable on the graph as it stands, located, in this order: a duplicate `step_id` (FR-215), which stops the other checks because each of them keys steps by `step_id`; a declared output with no output step (FR-214); an unresolved reference, located on the consuming step; a cycle, one issue per step that lies on it; an ambiguous producer, skipped after a cycle because it needs the topological order; and an orphan step. `RatingAlgorithm`'s validator calls it and raises on the first, with the codes save answers today, and the validate route calls it and reports them all (FR-<new>). `SubGraphBody` keeps its own parallel invariants (§4.11), so this single definition covers algorithms only. **`AlgorithmValidationReport`** is `{"issues": [ValidationIssue, …]}`. A `ValidationIssue` is `{"code", "message", "step_id", "field"}`, the last two nullable; it is defined in `model-schema`, from which `pricing-core`'s `validate_algorithm` and `validate_rate_table` (§5.2) take it.
```

**T4 — `00` FR-24, a dated amendment.** Placement:
`docs/specs/00-overview.md`, the FR-24 row (`:235`). The text is **appended** to the end of
the second cell, after `rests on the `02` §5.3 Peril structure library precedent alone.` and
one space, before the closing ` |`. Nothing is struck.

```text
**Amended <date> (`RL-<this>`): the `03` DAG designer's on-node live validation is discharged** by `03` FR-<new>, raised as a numbered requirement and served by a validate-only route. The other exceptions' state is unchanged by this line.
```

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop. If a text's anchor is not found exactly once, that is a stop too, reported to the lead; the executor does not re-word it.

## What it obliges

- **This commit:** this record only.
- **`PL-1286`, the planner's file, is not edited here.** DP-6's *Resolved by* cell cites this
  record once it is minted.
- **Slice 3 (WK-675)**, in one commit with T1–T4:
  - **model-schema:** add `RatingAlgorithmDraft`; make `RatingAlgorithm` its subclass;
    extract the invariants into one breach-returning function, in item 2's order and with
    its skips; move `ValidationIssue`; add `AlgorithmValidationReport`. Export all three
    from `model_schema/__init__.py`. Keep `RatingAlgorithm._reachable` and
    `_reaches_output` callable from `SubGraphBody` (`sub_graphs.py:118`, `:122`), and name
    that in the leaf plan;
  - **pricing-core:** import `ValidationIssue` from `model-schema`. `compile.py` keeps the
    name importable, so `rate_tables/operations.py:57` does not break;
  - **backend:** the handler is typed `body: RatingAlgorithmDraft` and
    `-> AlgorithmValidationReport`. It sits in `backend/src/app/api/rating_algorithms.py`,
    with its logic in `backend/src/app/platform/rating_algorithms.py`.
    **`create_rating_algorithm` (`api/rating_algorithms.py:34`) is not edited.** Under FD-1366's per-route hold, a slice that edits that handler types it in the same
    slice. If S3 must edit it, S3 types it;
  - `docs/contracts/` is regenerated. Whether the new shapes also get a `GENERATED_SHAPES`
    slug is the leaf plan's call, under `PL-1286`'s contention row for that table;
  - **frontend:** the designer renders each located issue on its node through the generated
    client and keeps no validation rule of its own.
- **Contention** (`PL-1286` *Sequencing*): T1 is in `03` §3.1, T2 in §5.1 and T3 in §4.1.
  Each serialises with the slices that table names. T4 is in `00` §3, which no table row
  names. The executor merges `origin/main` first.
- **Context for the lead, not ruled here:** S2's save goes through `POST
  /rating-algorithms`, one of FD-1366's five untyped routes. Under that
  finding's per-route hold (i), S2 waits until the route is typed.

## Acceptance — the violation that must become detectable

The violation: **an invalid graph that the designer shows as valid before save, or a rule
that validation and save apply differently.** Each backend test carries
`@pytest.mark.req("FR-<new>")` and is shown red on deliberately broken input.

1. **Cycle, located.** A two-step cycle with a third step downstream of it answers 200, and
   only those two steps carry `RATING_GRAPH_CYCLIC`. *(Amended 2026-10-01 10:28 BST, F-4.)*
   Orphan issues may also appear after a cycle, so the test asserts the set of
   `RATING_GRAPH_CYCLIC` issues, never that the whole list has two entries. Broken input: type the body
   `RatingAlgorithm`, and the request answers 422. A second broken input names the whole
   unordered set, and the downstream step is then reported too.
1a. *(Added 2026-10-01 10:23 BST, findings A and B.)* **The check order and its skips.** A
   duplicated `step_id` gives that one issue only, with the duplicated `step_id`, even when
   the draft also has a cycle. A cycle plus two non-chained producers of one name gives no
   ambiguous-producer issue. Broken input: run every check unconditionally, and both cases
   fail.
2. **Unresolved reference, located.** A step consuming an unproduced name answers 200 with
   `RATING_GRAPH_UNRESOLVED_REF` and that step's `step_id`.
3. **All, not the first.** A draft with two independent breaches reports both. Broken input:
   stop at the first breach.
4. **Deeper check, located.** The `RATING_TYPE_MISMATCH` fixture of
   `packages/pricing-core/tests/test_rating_compile.py` (the `s_clamp` case, `:402`) is
   reported on `s_clamp`.
5. **One definition (parity).** For every invalid-algorithm fixture the save tests use, the
   report's first issue has the code that `POST /rating-algorithms` refuses the same body
   with. A valid fixture gives an empty list and saves with 201.
6. **Save unchanged.** The existing save and sub-graph tests pass unmodified. Sub-graphs
   share `graph_validation_error`.
7. **Nothing persisted.** The `rating_algorithms` row count is the same before and after a
   validate call.
8. **Permission.** A principal with `rating:read` but not `rating:write` gets 403.
9. **Malformed body.** A step missing a required field answers 422 `VALIDATION_FAILED`, with
   a field error beginning `steps.<index>.`.
10. **Contract.** The operation's request body and 200 response in `generated.json` are
    `$ref`s to `RatingAlgorithmDraft` and `AlgorithmValidationReport`, not open objects, and
    `uv run python scripts/generate-contracts.py --check` exits 0.
11. **Frontend.** A designer test (id `FR-<new>` in its name) asserts that an unresolved
    reference is rendered on its node before any save call is made.

## Amendment, 2026-10-01 10:23 BST: auditor-1055's findings A, B and C, and the FR-223 wording

*By the decision-maker session `dm-675dp56` (effort `medium`), on the lead's adoption of
auditor-1055's three LOW findings on `03d838a8`. This is one dated pass, folded with RL 9766
(working id)'s T2 amendment. The ruled option is unchanged: (a), with the
`RatingAlgorithmDraft` body.*

- **A: the duplicate `step_id` breach** (FR-215, `rating.py:397-399`) is now named. Item 2.1
  reports it with the duplicated `step_id`, and it stops the remaining graph checks, because
  each of them keys steps by `step_id`.
- **B: "every breach" was overstated.**
  - Item 2, T1 and T3 now say "every breach detectable on the graph as it stands".
  - They state today's check order: duplicate id, FR-214, unresolved reference, cycle,
    ambiguous producer, orphan.
  - The ambiguous-producer check is skipped after a cycle.
  - A cycle names the steps on it, not the steps merely downstream of it.
  - Acceptance item 1 is tightened, and item 1a is added.
- **C: "defined once" holds for algorithms only.** `SubGraphBody` keeps its parallel
  invariants (`sub_graphs.py:62-151`) and calls `RatingAlgorithm._reachable` and
  `_reaches_output` (`:118`, `:122`). The extraction keeps them callable, and S3's leaf plan
  names it (item 2, *What it obliges*, T3).
- **FR-223 (item 7).** "The designer cannot author a mismatch" is reworded as reasoning: it
  is an inference, because a mismatch arises where a version pins an algorithm. The code gap
  is cited as FD 9759 (working id).

T1 and T3 above are rewritten in full. The byte-for-byte sentence stands unchanged. T2 and
T4 are unchanged.

## Amendment, 2026-10-01 10:28 BST: T2's four-cell form (F-3), acceptance item 1 (F-4), two locators

*By the decision-maker session `dm-675dp56` (effort `medium`), on auditor-1055's scoped
re-check as the lead adopted it at 10:27 BST. The ruled option is unchanged.*

- **F-3.** T2 now gives the validate row in a three-cell and a four-cell form
  (`rating:write`), chosen by whether RL 9907 (working id)'s `Permission` column has landed.
  The permission names are proved by the grep pasted in T2.
- **F-4.** Acceptance item 1 asserts that only the two cycle steps carry
  `RATING_GRAPH_CYCLIC`. Orphan issues may also appear after a cycle, so a test must not
  assert the whole list.
- **Locators.** The invariant block is `rating.py:395-475` (was `:395-470`). The
  ambiguous-producer block starts at `:444` (was `:445`).

*2026-10-01 10:44 BST: "FD 9779 (working id)" is re-pointed to `FD-1366`, its minted id, and added to `relates:`. No other change (decision-maker `dm-675dp56`, on the lead's order).*

## Amendment, 2026-10-05: citations re-read at main `ef5dc6e7`, before mint

Citation and currency update only. Nothing ruled above changes (decision-maker `dm-amend-2`,
on the lead's brief of 2026-10-05 10:50 BST, which adopted the batch-2 triage).

- **FD 9773 (working id) is re-pointed to `FD-1374`**, its minted id (its own record names
  working id 9773), and `FD-1374` is added to `relates:`. It is still `active`.
- **T1 to T4 re-read at `ef5dc6e7`.** T1's FR-219 row is still `:88`, the last row of
  §3.1. T2's `…/diff?against=` row moved `:780` → `:896`. T3's paragraph moved
  `:280-282` → `:287-289` and still precedes `### 4.2` (`:291`). T4's FR-24 row moved
  `:229` → `:235`, and its anchor sentence occurs once there. `03` §5.1's header is still
  `| Method | Path | Purpose |`, so T2's three-cell form is the one that applies today.
- **The Evidence section is a dated reading at `1dd5e264`** and resolves there. It is not
  rewritten. At `ef5dc6e7` its moved cites are: `00` FR-24 `:229` → `:235`; `03` §5.3
  `:1094` → `:1231` and `:1101-1104` → `:1238-1241`; §5.2's `validate_algorithm`
  signature `:907` → `:1027`; `RatingAlgorithm` `model_schema/rating.py:374` → `:375`, its
  validator `:400-470` and `:395-475` → `:396-476`, `:397-399` → `:398-400`;
  `check_model_reference_mode` `rating.py:172` → `:173`; `errors.py:455-470` → `:460-475`.
  `03:109` (FR-223), `compile.py:60-72`, `:366-392` and `:614`,
  `api/rating_algorithms.py:28-50`, `graph_errors.py:11-16`, `sub_graphs.py:62-151` and
  `rate_tables/operations.py:57` are unchanged.
- **The pasted `06` permission rows** are verbatim output at `1dd5e264` and stay as
  quoted. At `ef5dc6e7` they are `06-governance.md:280-281`, and both names still exist.
- **`status:` is `active`, not `draft`.** `document-ids.md` §1.2a gives a ruling the subset
  `active`, `superseded`, `retired`, and `audit-docs.py` check 33 refused `draft`. The
  working-id rulings of batch 1 (#977, #979) carry `active` in the same form.
- `tree:` stays `8bd782ac`, the tree of `1dd5e264` that the Evidence was read at, as
  `RL-1407` keeps its own evidence tree. `created:` changes at the mint.

## Amendment, 2026-10-05 15:29 BST: citations re-read at main `809a3794`, before mint

Citation update only. Nothing ruled above changes (decision-maker `dm-premint2`, on the
lead's prep-wave brief of 2026-10-05, section M).

- **T1 to T4 re-read at `809a3794`.** Each anchor is found exactly once, at the line the
  amendment above gives: `| **FR-219** |` at `03:88`, the `…/diff?against=` row at `:896`,
  T3's paragraph ending `and unreferenced by an `output` (FR-212).` at `:287-289` (before
  `### 4.2` at `:291`), and T4's anchor sentence in the FR-24 row at `00:235`. `03` §5.1's
  header is still `| Method | Path | Purpose |`, so T2's three-cell form still applies.
- **Moved since `ef5dc6e7`:** `_handle_validation_error`, the Evidence's `errors.py:455-470`,
  is now `errors.py:468-483` (eight lines were inserted at `:191`); the pasted `06`
  permission rows are now `06-governance.md:281-282`, and `RATING_READ` and `RATING_WRITE`
  are now `permissions.py:48-49`. Both names still exist. `06` §4.1's table starts at
  `:262`. The other cites the amendment above gives are unchanged at `809a3794`.
