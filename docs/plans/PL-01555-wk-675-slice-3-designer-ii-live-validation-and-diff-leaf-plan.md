---
id: PL-1555
family: plan
kind: leaf
title: WK-675 Slice 3 — Designer II, live validation and diff (FR-212, FR-214, FR-215, FR-219, FR-223, FR-227, FR-244, FR-246, FR-24): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-09            # original date 2026-10-05, set at the draft; minted 2026-10-09
owner: planner
tree: 9489405370a1ce06c2b985ad88c7d471438febb1
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1286, PL-1371, PL-1364, SL-1367, FD-1335, FD-1366, FD-1374, RL-1263, SL-1387, SL-1340, SL-1341, SL-1389]
---

# PL-1555 — WK-675 Slice 3: Designer II, live validation and diff, leaf plan

*(Minted 2026-10-09 as PL-1555 from working id 9578, in the D3 batch mint; citations of the ids minted in this batch, and of ids already minted on main (RL-1474, RL-1475, RL-1473, RL-1445, PL-1476, SL-1477, FD-1437, RL-1438), are re-pointed outside quotes, quoted text and quoted channel entries stay as quoted, and cites of PL 9576, PL 9574, SL 9577 and SL 9575 stay working ids.)*

This plan is filed under working id 9578. Its `SL-` row under WK-675 in
[`../roadmap.md`](../roadmap.md) is slice working id 9581, `draft`. That row is filed in the
WK-675 S4 plan PR (PL-1557, working id), which carries the rows for S4, S3, S13 and S14. The
lead reserved both ids on 2026-10-05 and mints both at the merge turn. Written by the planner
(planner-675) on the lead's prep-wave brief of 2026-10-05, section AW. Evidence was read at
origin/main `137bc817` (tree `94894053`); the clock read 2026-10-05 17:09:40 BST during the
read.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds:
> - `test-driven-development`: every acceptance item is seen red, by its cause, before the
>   code that turns it green;
> - `python-test`: the `req` marker and negative tests;
> - `python-package`: Tasks 1 and 2 (model-schema and pricing-core);
> - `fastapi-service`: Tasks 4 and 5;
> - `contract-schema` and `contract-guard`: the regenerated contract and the untyped-body
>   guards;
> - `spec-change`: Tasks 2 and 4, with the decision-maker's texts byte for byte;
> - `vue-frontend`, `vue-best-practices` and `vue-testing-best-practices`: Tasks 6 and 7;
> - `dev-commands`: the two-half gate;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The
> executor is spawned from `.claude/roles/executor.md`.

## Goal

While an actuary edits a graph in the DAG designer, the designer asks the server whether the
graph would save. Each issue the server names is drawn on the step it names, before any save:
a cycle on each step that lies on it, an unresolved reference on the consuming step, a type
mismatch on its step. An issue that no step owns is shown on the graph. The actuary can also
overlay the structural diff against another version of the same algorithm. The rules are
defined once, on the server; the frontend re-implements none of them.

**Architecture.** Backend first, in one commit with its spec texts:
- `ValidationIssue` moves from `pricing_core/rating/compile.py` to `model-schema`, unchanged.
  `AlgorithmValidationReport` is new beside it (RL 9767 items 2 and 4).
- `RatingAlgorithm`'s graph invariants become one function, `graph_invariant_issues`, that
  returns every breach detectable on the graph as it stands, located, in today's order. The
  model validator calls it and raises on the first, with today's exception classes, so save
  is unchanged (RL-1474 item 2).
- `POST /api/v1/rating-algorithms/validate` takes a `RatingAlgorithmDraft` (built in S2) and
  answers 200 with the report (RL-1474 items 3, 5 and 6). `03` gains its FR, its §5.1 row and
  a §4.1 paragraph, and `00` FR-24 records the discharge (RL-1474 T1–T4).
- FD-1437 limbs (2) and (3): a mode mismatch at compile is refused as
  `MODEL_REFERENCE_MODE_INCONSISTENT`, not `BUNDLE_COMPILE_FAILED`, with RL 9758 T1 applied;
  and a listed, counted sweep of the bare `ValueError`s that reach compile's generic fallback.
- `GET /api/v1/rating-algorithms/{slug}@{version}/diff` gets the response model it already
  returns, `AlgorithmDiff`, so the overlay has a generated type (DP-S3-1).

Then the frontend, on S2's files:
- `validateRatingAlgorithm` and `getAlgorithmDiff` in `frontend/src/api/ratingAlgorithms.ts`;
- `useGraphValidation`, a composable that calls the route as the draft changes (debounced,
  stale calls aborted);
- `StepNode.vue` shows its issues; a graph-issues panel shows the issues with no `step_id`;
- `DiffOverlay.vue` marks added and changed nodes and lists removed steps.

**Tech stack:** Python 3.12, FastAPI, Pydantic v2, pytest; Vue 3 `<script setup lang="ts">`,
Vite, Vitest with happy-dom, `@vue-flow/core` (added by S2), and the generated client.

**Spec, map plan and rulings:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md): §3.1 (FR-212 `:81`,
  FR-214, FR-215, FR-219 `:88`); §3.2 (FR-223 `:109`, FR-227 `:113`); §3.5 (FR-244 `:146`,
  FR-246 `:148`); §4.1 (`RatingAlgorithm`, the paragraph ending `:287-289`); §5.1 (`:895-896`;
  owned codes from `:928`); §5.3's DAG designer row (`:1231`) and its *Interaction
  requirement* (`:1238-1241`);
- [`../specs/00-overview.md`](../specs/00-overview.md): FR-24 (`:235`), NFR-463;
- `PL-1286` (WK-675's map plan, `draft`): S3's row (`:305`), DP-6 (`:245`) and the contention
  table (`:396-397`);
- `PL-1371` §3.3 (S3: "RL 9767 to mint; carries FD 9759; never concurrent with a
  `compile.py` editor") and §5 rule 4;
- the rulings and finding, all unminted, with their working ids, each read to its last dated
  amendment at the head named: RL-1474 (DP-6; #1055 @`07d9d230`); RL-1438 (FR-223's check
  point; #1061 @`2e7eff8c`); FD-1437 (#1059 @`3621fe7b`); RL-1445 (RL-1263 amended; #1162
  @`381254c3`);
- S2's leaf plan, PL-1476 (#1131 @`c66300e5`): the files S3 builds on and its
  Hand-off item 1;
- `FD-1335` *Disposition* item 5 (the per-route hold); `PL-1364`'s
  `UNTYPED_2XX_PENDING_PART_B` list, which names the diff route.

## The decisions this plan rests on, quoted

1. **DP-6, RL-1474, Ruled:** *"(a), with the body the plan did not name."* The
   route, its body, its response and its permission are those of RL-1474's table, quoted in
   Task 4.
2. **FD 9759's owner and discharge** (the maintainer's entry headed "2026-10-01 10:22:24 BST",
   as FD 9759 quotes it): *"Owner: the WK-675 slice that builds RL 9767's validate route (S3's
   leaf), NOT WK-1178."* Limb (2) as amended by the entry headed "2026-10-01 10:30:00 BST —
   ACCEPTANCE: RL 9770 (NFR-490's statistic = p99) as the spec interpretation; FD-1437 limb (2)
   discharged at the compile site alone; #1060 audit noted": *"limb (2) is discharged by the
   compile-site typed error alone; the validate-route clause falls away"*. The lead's holds
   register, under *WK-675 S3 dispatch-record lines*, now reads the same: "(2) a typed error
   → MODEL_REFERENCE_MODE_INCONSISTENT at the compile site alone, red first", corrected at
   2026-10-05 17:22:00 BST and citing the 10:30:00 entry. The register and this plan agree.
   *(Dated note, 2026-10-05, written 17:32:47 BST, pre-mint: this said the register "still
   reads 'at compile AND in the validate route' … that line predates the 10:30:00 entry, and
   this plan follows the entry". The register was corrected at 17:22:00, and the fix is
   ordered by the entry headed "2026-10-05 17:30:02 BST — Rulings: T2 routing (RL 9562 mints
   ahead of PL 9560); _NUMERIC FD go; WK-675 DP-S3-1 (a) with the FD-1335 reading;
   DP-S13-1 (a′)", item 6: "PL 9578 :111-113 stale "compile AND validate": the planner fixes
   it pre-mint. Yes.")*
3. **RL 9758 (working id), Ruled, item 3:** *"Algorithm save (`POST
   /api/v1/rating-algorithms`) and RL-1474's validate route do not check
   FR-223."*
4. **The S3 dispatch-record lines in the lead's holds register** (the maintainer, 2026-10-01):
   *"No concurrency on pricing_core/rating/compile.py's import block … S3 is never concurrent
   with a slice editing compile.py."* And: *"RL 9767's C: SubGraphBody's parallel
   _graph_invariants (sub_graphs.py:62-151); the statics stay reachable."*
5. **S2's Hand-off item 1** (PL-1476), which this plan carries: *"`RatingAlgorithmDraft`
   (RL-1474 item 1's type limb) was built in WK-675 S2 (PL-1476), with `RatingAlgorithm` as
   its subclass and the save route typed by it. S3 does not re-add it. S3 still owns RL-1474
   items 2–7 (the breach-returning invariant function, `ValidationIssue`'s move,
   `AlgorithmValidationReport`, and the validate route) and T1–T4, including T3's §4.1
   paragraph that names the type."*

## Status

`draft`. DP-S3-1 and DP-S3-2 (below) are decided by the maintainer (by delegation), recorded in RL 9543 (working id): DP-S3-1 (a), DP-S3-2 (a). The
plan moves to `active` only through a separate activation PR, after every activation need
below holds.

*Dated note, 2026-10-05 (written 18:40:25 BST, pre-mint): P-texts of RL-1554
applied 2026-10-05. RL-1554 (working id; #1198 at `0e872448d7dde4d652ae15bafa097983909441bc`), §"The plan texts" lines 232–247 and its "Amendment, 2026-10-05 17:42
BST" (lines 323–340), gives P7 and P8 for this plan; P9 and P10 are discharged by that
amendment and are not applied. Counts (Python `str.count` over this file): P7 (Status) and P8
(activation need 4, appended) each find 1 before and 0 after, new text 0 before and 1 after.
P8 carries the `PL-1364` guard dependency of RL-1554 item 7: `backend/tests/test_contracts.py`'s
pending list holds 11 entries if S3 dispatches before `SL-1367`, and the second of the two to
dispatch carries the delta.*

### Activation needs, in order

1. **RL-1474 minted.** S3 applies its T1–T4 byte for byte, and each text
   cites `RL-<this>`. An unminted text is a stop.
2. **RL-1438 and FD-1437 minted.** S3 applies RL-1438
   T1 byte for byte and discharges FD-1437 limbs (2) and (3).
3. **S2 (SL-1477, PL-1476) merged.** S3 consumes S2's output: `RatingAlgorithmDraft`, the
   designer components and `ratingAlgorithms.ts`. So under RL-1445 condition (b), S2 and S3
   never run at the same time.
4. **DP-S3-1 and DP-S3-2 decided**, each by a dated line. Decided (RL-1554). The dispatch record names `backend/tests/test_contracts.py` as shared with `SL-1367`; whichever of S3 and `SL-1367` dispatches second carries the pending-list delta (11 entries if S3 is first; RL-1554 item 7).
5. **No slice editing `compile.py` in flight** (decision 4; `PL-1371` §5 rule 4): WK-673 S3
   (`SL-1387`), WK-1250 S2 (`SL-1340`) and WK-1250 S3 (`SL-1341`), and any other slice whose
   dispatch record names `pricing_core/rating/compile.py`.
6. **Task 0 re-run at the dispatch tree**, with every row as expected or its delta named.
7. **The maintainer's agreement** to this plan, as a dated line, and **the lead's go**,
   recorded in a separate activation PR. That PR sets this plan and SL-1556 `active`.

## Acceptance Standard

Each item is checked by a command run from the repository root on the slice's merge tree.
"Red first" means:
- the named test was run and failed **for the stated cause** before the code that turns it
  green;
- a failure with the right status and a different cause is a plan defect
  ([`README.md`](README.md) convention 2);
- every red is recorded in the slice's ledger, with the failure line as printed.

Every backend test of the validate route carries `@pytest.mark.req("FR-<new>")`, the id T1
takes when applied. Items 1–11 are RL-1474's own acceptance items, in its numbering.

1. **Cycle, located** (RL-1474 acceptance 1). A two-step cycle with a third step downstream
   answers 200, and the set of `RATING_GRAPH_CYCLIC` issues' `step_id`s is exactly the two
   cycle steps. The test asserts that set, never the list's length. **Broken input:** (i) the
   handler body typed `RatingAlgorithm`, and the request answers 422; (ii) the cycle set
   computed as every step Kahn's sort leaves unordered, and the downstream step appears.
   Command: `uv run pytest backend/tests/test_rating_algorithm_validate.py -q`.
2. **The check order and its skips** (RL-1474 acceptance 1a). A duplicated `step_id` yields
   that one issue only (`VALIDATION_FAILED`, carrying the duplicated id), even when the draft
   also has a cycle. A cycle plus two non-chained producers of one name yields no
   ambiguous-producer issue. **Broken input:** run every check unconditionally; both cases go
   red. Command: `uv run pytest packages/model-schema/tests/test_graph_invariant_issues.py -q`.
3. **Unresolved reference, located** (RL-1474 acceptance 2). 200, code
   `RATING_GRAPH_UNRESOLVED_REF`, the consuming step's `step_id`. Command as item 1.
4. **All, not the first** (RL-1474 acceptance 3). A draft with an unresolved reference and an
   orphan step reports both. **Broken input:** return after the first breach. Command as
   item 2.
5. **Deeper check, located** (RL-1474 acceptance 4). The `RATING_TYPE_MISMATCH` fixture of
   `packages/pricing-core/tests/test_rating_compile.py` (the `s_clamp` case) is reported on
   `s_clamp` through the route. Command as item 1.
6. **One definition (parity)** (RL-1474 acceptance 5). For every invalid-algorithm fixture
   in `backend/tests/test_rating_algorithms.py`, the report's first issue has the code that
   `POST /api/v1/rating-algorithms` refuses the same body with. A valid fixture gives an empty
   list and then saves with 201. The test is parametrized over the fixtures by name, so a new
   save fixture is picked up. Command as item 1.
7. **Save unchanged** (RL-1474 acceptance 6). `test_rating_algorithms.py`,
   `packages/model-schema/tests/test_rating_algorithm.py` and the sub-graph tests pass
   **unmodified** (`git diff --stat origin/main...HEAD` shows no line removed from them).
   Command: `uv run pytest backend/tests/test_rating_algorithms.py backend/tests/test_sub_graphs.py packages/model-schema/tests/test_rating_algorithm.py -q`.
8. **Nothing persisted** (RL-1474 acceptance 7). The `rating_algorithms` row count and the
   audit-event count are the same before and after a validate call. Command as item 1.
9. **Permission** (RL-1474 acceptance 8). A principal with `rating:read` and not
   `rating:write` gets 403. **Broken input:** the dependency `RatingReadDep`. Command as
   item 1.
10. **Malformed body** (RL-1474 acceptance 9). A step missing a required field answers 422
    `VALIDATION_FAILED`, with a field error whose location begins `steps.<index>.`. Command
    as item 1.
11. **Contract** (RL-1474 acceptance 10). In `docs/contracts/openapi/generated.json`, the
    validate operation's request body and 200 response are `$ref`s to `RatingAlgorithmDraft`
    and `AlgorithmValidationReport`, and `uv run python scripts/generate-contracts.py --check`
    exits 0. *(Checked at Task 4's commit, Step 5a; dated note, 2026-10-05.)*
12. **Frontend, before save** (RL-1474 acceptance 11). A designer test whose name contains
    `FR-<new>` asserts that an unresolved reference is rendered on its node, and that no
    save call was made. **Broken input:** render issues only from a save refusal; the test
    goes red. Command: `pnpm --dir frontend test -- DagDesigner`.
13. **Frontend, graph-level issue.** An issue with no `step_id` (a declared output with no
    output step, FR-214) is shown in the graph-issues panel, inside `role="status"`, and in
    no toast. Command as item 12.
14. **Frontend, no rule of its own.** `git grep -n -E 'RATING_GRAPH_CYCLIC|RATING_GRAPH_UNRESOLVED_REF|topolog|kahn' -- frontend/src ':!frontend/src/api/generated'`
    prints nothing. A code is only ever displayed from a report. (The pattern is a proxy; the
    review reads `useGraphValidation.ts` and `graph.ts` for any check of consumes against
    produces.)
15. **Frontend, stale calls.** Three draft changes within the debounce window make one
    request; a change while a request is in flight aborts it, and the older response never
    overwrites the newer report. Command: `pnpm --dir frontend test -- useGraphValidation`.
16. **FD-1437 limb (2): compile names the code** (RL-1438 acceptance 1). An `approximation`
    version pinning an algorithm with an `exact` `model_call` step fails compilation with
    `MODEL_REFERENCE_MODE_INCONSISTENT`, and the message names the step. At the pure level,
    `test_a_mode_mismatch_is_refused_at_compile`
    (`packages/pricing-core/tests/test_rating_compile_bundle.py:235`) is tightened to
    `pytest.raises(CodedError, match=r"^MODEL_REFERENCE_MODE_INCONSISTENT: ")`. Over HTTP, a
    test in the style of `test_a_step_ref_the_pins_do_not_carry_is_refused_over_http`
    (`backend/tests/test_rating_pin_membership_api.py:36`) asserts
    `job_row.error["code"] == "MODEL_REFERENCE_MODE_INCONSISTENT"`. **Red on main:**
    `BUNDLE_COMPILE_FAILED`. Commands:
    `uv run pytest packages/pricing-core/tests/test_rating_compile_bundle.py -q` and
    `uv run pytest backend/tests/test_rating_mode_mismatch_api.py -q`.
17. **Compile, agreeing** (RL-1438 acceptance 2). The same version with a matching step
    compiles. Command as item 16.
18. **Spec and code agree** (RL-1438 acceptance 3). A test reads `03` §5.1's owned-code list
    (the paragraph beginning `**Error codes owned by this module:**`) and imports
    `RATING_ERROR_CODES`, and asserts `MODEL_REFERENCE_MODE_INCONSISTENT` is in both. **Red on
    main:** the code is absent from `RATING_ERROR_CODES`. Command:
    `uv run pytest backend/tests/test_errors.py -q`.
19. **No save-time mode check** (RL-1438 acceptance 4). Saving the mismatching algorithm
    through `POST /api/v1/rating-algorithms` answers 201. Command as item 16's second.
20. **FD-1437 limb (3): the sweep is listed and counted.** The ledger carries a table: one
    row per raise site that can reach `compile_rating_version`'s generic fallback
    (`backend/src/app/platform/rating_versions.py`, the `except ValueError` in
    `compile_rating_version`), each with its file and symbol, and either the named code it now
    carries or the reason `BUNDLE_COMPILE_FAILED` is right for it. The count is printed by the
    predicate in Task 3, verbatim, at the slice's tree.
21. **The diff route is typed** (DP-S3-1, if (a)). In `generated.json`, the 200 response of
    `GET /api/v1/rating-algorithms/{slug}@{version}/diff` is a `$ref` to `AlgorithmDiff`. If
    `UNTYPED_2XX_PENDING_PART_B` exists in `backend/tests/test_contracts.py`, its entry for
    that route is removed in the same commit, and the guard is shown red with the entry kept.
    Command: `uv run pytest backend/tests/test_contracts.py -q`. *(Dated note, 2026-10-05,
    pre-mint, on the 17:30:02 BST entry's item 4: this holds in the slice's **first** commit
    (Task 0A), before any frontend code consumes the route, with `generate-contracts --check`
    exiting 0 at that commit. The ledger records that commit's SHA, its position (first) and
    the `--check` rc.)*
22. **The diff overlay** (FR-219). With a second version chosen, nodes in `added_steps` carry
    an "added" marker and nodes in `changed_steps` a "changed" marker, each as text and not
    colour alone; `removed_steps` and re-pointed tables are listed in the overlay panel.
    Command: `pnpm --dir frontend test -- DiffOverlay`.
23. **Accessibility** (NFR-463). The issue and diff markers have a text channel, the issue
    count is announced through `aria-live="polite"`, and `NodeNavigator`'s option names
    include the step's issue count. Command: `pnpm --dir frontend test -- NodeNavigator`.
24. **The gate, both halves**, at the slice's tree, every command rc 0 (`CLAUDE.md` §11),
    and `python3 scripts/audit-docs.py` clean.

## Global Constraints

- **Vue 3 Composition API with `<script setup lang="ts">` only** (`CLAUDE.md` §3).
- **Never hand-write an API type** (`CLAUDE.md` §3). `AlgorithmValidationReport`,
  `ValidationIssue` and `AlgorithmDiff` alias `components["schemas"]` from
  `@/api/generated/schema`.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2).
  `ValidationIssue` moves; it is not copied. `pricing_core.rating.compile` keeps the name
  importable (RL-1474, *What it obliges*), so
  `packages/pricing-core/src/pricing_core/rate_tables/operations.py:57` does not break.
- **No rule is re-implemented in the frontend** (RL 9767 item 2, T1: "the frontend
  re-implements none of them").
- **`pricing-core` stays importable standalone** with zero FastAPI, SQLAlchemy or Redis
  dependencies (`CLAUDE.md` §2). The new model-schema function imports nothing from
  `pricing-core`.
- **The decision-maker's texts are applied byte for byte** (RL-1474 and RL-1438, *Spec
  changes*): any executor wording is a stop, and an anchor not found exactly once is a stop.
- **WCAG 2.2 AA** (`00` NFR-463): no state is shown by colour alone.
- **Concurrency** (`RL-1263` as amended by RL-1445): at most three build slices;
  **one full gate at a time on this VM**; same-Work concurrency only under RL-1445 conditions
  (a) and (b); never concurrent with a `compile.py` editor (decision 4).

## Scope

### Requirement coverage, each id individually

| Id | What S3 does with it |
|---|---|
| FR-<new> | created by RL-1474 T1 and delivered: the validate route and the designer's on-node rendering (Acceptance 1–15) |
| FR-24 | the `03` DAG designer's on-node live validation exception is discharged (RL-1474 T4) |
| FR-212 | cycles, unresolved references, ambiguous producers and orphans, each located (Acceptance 1–4) |
| FR-214 | a declared output with no output step, reported with no `step_id` and shown on the graph (Acceptance 2, 13) |
| FR-215 | a duplicated `step_id`, reported first and alone (Acceptance 2) |
| FR-219 | the structural diff overlay over the existing route (Acceptance 21, 22) |
| FR-223 | not in the validate route (RL-1438 item 3); compile names `MODEL_REFERENCE_MODE_INCONSISTENT` (Acceptance 16–19); RL-1438 T1 applied |
| FR-227 | type mismatches, through `validate_algorithm`, located (Acceptance 5) |
| FR-244 | the expression checks `validate_algorithm` runs (the `STRING_CHECKS` over every authored string), reported through the route |
| FR-246 | **not delivered here.** The route reports what `validate_algorithm` checks; FR-246's declared-inputs rule is unenforced there (`FD-1374`, MEDIUM, owner WK-1178, remedy PL 9776). When that remedy lands, the route reports it with no change here (RL-1474, *Not decided here*). `PL-1286`'s S3 row names FR-246; this is the ruling's narrowing, recorded for the auditor |
| FR-240 | compile's check of FR-223 now refuses with the named code |
| FR-403 | the `rating.compile` Job's error code carries `MODEL_REFERENCE_MODE_INCONSISTENT` |
| NFR-463 | text channels for issues and diff markers; the live count (Acceptance 23) |

**Out of S3, named so nothing is assumed:**
- sub-graph validation (`SubGraphBody` keeps its own `_graph_invariants`; RL-1474 item 2,
  finding C) and sub-graph mounting (S9);
- the structural diff attached to an approval request (FR-219's second clause): WK-673 S5
  (`SL-1389`);
- drag-to-connect on the canvas: DP-S3-2;
- a list of an algorithm's versions: none exists in `03` §5.1; the overlay takes a version
  number (see *Choices*).

### Task 0 at planning time (measured, not asserted)

Run at `137bc817`, 2026-10-05, in `.claude/worktrees/planner-675-s3`. Rows that depend on S2
can only be re-run after S2 merges.

| # | Precondition | Command | Result at `137bc817` |
|---|---|---|---|
| 0.1 | `ValidationIssue` defined once, in pricing-core | `git grep -n 'class ValidationIssue' -- packages` | `pricing_core/rating/compile.py:60` only |
| 0.2 | its importers | `git grep -n 'import ValidationIssue\|ValidationIssue,' -- packages backend/src` | `rate_tables/operations.py:57`, `backend/src/app/platform/rating_algorithms.py:21` |
| 0.3 | the invariants block | `grep -n '_graph_invariants\|def _reachable\|def _reaches_output' packages/model-schema/src/model_schema/rating.py` | `:395`, `:479`, `:499` |
| 0.4 | `SubGraphBody` calls the statics | `grep -n 'RatingAlgorithm._rea' packages/model-schema/src/model_schema/sub_graphs.py` | `:118`, `:122` |
| 0.5 | the mode check is a bare `ValueError` | `sed -n 173,184p packages/model-schema/src/model_schema/rating.py` | `raise ValueError(` at `:181` |
| 0.6 | compile calls it after `validate_algorithm` | `grep -n 'validate_algorithm(algorithm)\|check_model_reference_mode(' packages/pricing-core/src/pricing_core/rating/compile.py` | `:611`, `:614` |
| 0.7 | the code is not in the registry | `grep -c MODEL_REFERENCE_MODE_INCONSISTENT backend/src/app/errors.py` | `0` |
| 0.8 | the code is in `03`'s owned list | `grep -n MODEL_REFERENCE_MODE_INCONSISTENT docs/specs/03-rating-engine.md` | `:109` (FR-223) and `:936` (owned list from `:928`) |
| 0.9 | the diff route is untyped | `sed -n 53,68p backend/src/app/api/rating_algorithms.py` | `-> dict[str, Any]`; `diff_between` returns `.model_dump()` (`platform/rating_algorithms.py:163`) |
| 0.10 | the RL texts' anchors, each once | `grep -cF` on each anchor (RL-1474 T1–T4, RL-1438 T1) | 1 each (`03:88`, `:896`, `:289`, `00:235`, `03:109`) |
| 0.11 | `03` §5.1's header has no `Permission` column | `grep -c '^\| Method \| Path \| Purpose \|$' docs/specs/03-rating-engine.md` | `1`: T2's three-cell form applies |
| 0.12 | S2 has merged | `git log --oneline origin/main -- frontend/src/components/dag/DagDesigner.vue` | **no commit** (S2 is #1131, open): activation need 3 |
| 0.13 | the untyped-2xx guard list | `grep -n UNTYPED_2XX_PENDING_PART_B backend/tests/test_contracts.py` | no hit (`SL-1367` is `draft`) |

At dispatch, the executor re-runs each row at the dispatch tree. Any change is named in the
ledger before Task 1.

### Write set, by file and symbol, at `137bc817`

| Path | Symbol or region | Change |
|---|---|---|
| `packages/model-schema/src/model_schema/rating.py` | new `ValidationIssue`, `AlgorithmValidationReport`, `graph_invariant_issues`; `RatingAlgorithm._graph_invariants` (`:395-476`) | the class moves in; the invariants body moves into the function; the validator raises on its first issue; `_reachable` and `_reaches_output` stay static methods of `RatingAlgorithm` |
| `packages/model-schema/src/model_schema/__init__.py` | import block and `__all__` | `ValidationIssue`, `AlgorithmValidationReport`, `graph_invariant_issues` appended |
| `packages/model-schema/tests/test_graph_invariant_issues.py` | new | Acceptance 2, 4 |
| `packages/pricing-core/src/pricing_core/rating/compile.py` | import block; `class ValidationIssue` (`:60-72`); `compile_bundle` (`:614`); `__all__` | the class removed and re-imported from `model_schema`, kept in `__all__`; the mode check wrapped (Task 2) |
| `packages/pricing-core/tests/test_rating_compile_bundle.py` | `test_a_mode_mismatch_is_refused_at_compile` (`:235`) | tightened (Acceptance 16) |
| `backend/src/app/errors.py` | `RATING_ERROR_CODES` (`:309`) | `MODEL_REFERENCE_MODE_INCONSISTENT` added |
| `backend/tests/test_errors.py` | new test | Acceptance 18 |
| `backend/src/app/api/rating_algorithms.py` | new `validate_rating_algorithm`; `algorithm_diff` (`:53-68`) | the route added; the diff's return type (DP-S3-1) |
| `backend/src/app/platform/rating_algorithms.py` | new `validate_draft`; `diff_between` (`:157-163`) | the logic; `diff_between` returns `AlgorithmDiff` |
| `backend/tests/test_rating_algorithm_validate.py` | new | Acceptance 1, 3, 5, 6, 8–10 |
| `backend/tests/test_rating_mode_mismatch_api.py` | new | Acceptance 16, 19 |
| `backend/tests/test_contracts.py` | `UNTYPED_2XX_PENDING_PART_B`, only if it exists | the diff entry removed |
| `docs/specs/03-rating-engine.md` | §3.1 after FR-219; §3.2 FR-223's cell; §4.1 after `:289`; §5.1 after `:896` | RL-1474 T1–T3 and RL-1438 T1, verbatim |
| `docs/specs/00-overview.md` | FR-24's second cell (`:235`) | RL-1474 T4, verbatim |
| `docs/contracts/openapi/generated.json` | generated | regenerated |
| `frontend/src/api/ratingAlgorithms.ts` | S2's module | `validateRatingAlgorithm`, `getAlgorithmDiff` |
| `frontend/src/components/dag/useGraphValidation.ts` and its test | new | Task 6 |
| `frontend/src/components/dag/StepNode.vue`, `NodeNavigator.vue`, `DagDesigner.vue` and their tests | S2's components | issues rendered; the overlay composed |
| `frontend/src/components/dag/GraphIssues.vue`, `DiffOverlay.vue` and their tests | new | Tasks 6 and 7 |
| the ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | registry |

**No `GENERATED_SHAPES` slug is added** (RL-1474 leaves it to this plan). The three shapes
reach `generated.json` through the routes, and no client needs a standalone schema file, as
in S2.

### Write set, and its contention (`RL-1263`, as amended by RL-1445)

Classes are those of `docs/process/delivery-process.core.json`
`guards.parallelism.build_slices_across_works.no_shared_files`.

| Shared path | Other slice | Class |
|---|---|---|
| `pricing_core/rating/compile.py` (import block, `compile_bundle`) | WK-673 S3 (`SL-1387`), WK-1250 S2 (`SL-1340`), WK-1250 S3 (`SL-1341`) | **SERIALISES outright** (`PL-1371` §5 rule 4; decision 4) |
| `model_schema/rating.py` `RatingAlgorithm` | WK-1250 S2/S3 if either edits it (re-read their leaf plans PL 9610, #1170, and PL 9609, #1173, at dispatch); WK-673 S5 (`SL-1389`) if it edits `diff_algorithms` | `forbidden` if the same class or function: **SERIALISES** |
| `model_schema/rating.py`, other classes | WK-673 S7 (`SL-1391`, `PL-1419`, merged to main at `4d3be141` after this plan's evidence tree): `RateTableDiff` (`PL-1419` write set) and a new `RateTableDiffCell` | different classes from S3's (`RatingAlgorithm`, `ValidationIssue`, the report): not `forbidden`; the dispatch record names the classes, and the second to merge re-gates |
| `03` §3.1 (T1) | WK-1250 S3 (FR-218); WK-673 S5 (§3.1 as needed) | **SERIALISES** with whichever shares the section (`PL-1286` `:397`) |
| `03` §3.2 (FR-223's cell) | none named at `137bc817` | exclusive; re-read at dispatch |
| `03` §4.1 (T3) | WK-1250 S2/S3 if either adds §4.1 prose | re-read at dispatch |
| `03` §5.1 (T2) | WK-674 S2 and S6; WK-1250 S1 (closed); WK-673 S4 and S7 (`PL-1419`); WK-675 S4 (DP-4 rows) | **SERIALISES** (`PL-1286` `:396`) unless a dispatch record names both hunks, as DP-L did for S2 |
| `00` FR-24's cell (T4) | none named | exclusive |
| `backend/src/app/errors.py` `RATING_ERROR_CODES` | any slice adding a rating code | `forbidden` (same existing object): serialise if both add |
| `backend/src/app/api/rating_algorithms.py`, `platform/rating_algorithms.py` | none in flight at `137bc817` (S2 edits them, and S2 precedes S3) | exclusive |
| `frontend/src/components/dag/*` | none outside WK-675 | exclusive |
| `generated.json`, `docs/INDEX.md` | any | exempt (`generated`) |
| `model_schema/__init__.py` `__all__` | any | name-disjoint (the 2026-10-05 09:44:39 BST amendment) |
| `backend/tests/test_contracts.py` `UNTYPED_2XX_PENDING_PART_B` | FD-1335 Part B's slices | not registry-exempt: **SERIALISES** with a slice editing that list |

**Same-Work pairs** (RL-1445 condition (b)): S3 consumes S2's output, so S2 → S3 serialise.
S3 and S4 (PL-1557, working id) share no source file named here except `03` §5.1, and
neither consumes the other's output. They may overlap only if the dispatch record names both
§5.1 hunks and their anchors. The second to merge merges `origin/main`, reads
`git merge-tree --write-tree origin/main HEAD` rc 0 before using the tree, regenerates the
generated files and re-runs the full gate. Gates never overlap: one full gate at a time.

### Size

Nine tasks. Tasks 1–5 are backend and spec work of about a day; Tasks 6–7 are the frontend.
`PL-1286` sizes S3 at 1 / 2 days; FD 9759's two limbs and the diff typing add about half a
day. The band is **1 / 1.5 / 3 days** (×0.75 / ×1 / ×2 on 1.5).

## Decision points

| DP | Question | Options | Recommendation | Blocking? | Resolved by |
|---|---|---|---|---|---|
| **DP-S3-1** | The overlay consumes `GET /rating-algorithms/{slug}@{version}/diff`, whose 200 is untyped (`dict[str, Any]`) and is one of `FD-1335` Part B's twelve. *Disposition* item 5: "Any of the 12 that a WK-675 slice consumes … is fixed **before that slice dispatches**." Who types it? | (a) S3 types it in-slice, `-> AlgorithmDiff` (the class `diff_between` already builds), removing its pending entry if present, the same form as FD-1366 rule (ii) for an edited handler; (b) S3 waits for WK-1178's Part B fix of this route; (c) the overlay leaves S3 for a later slice | **(a).** The handler already returns `AlgorithmDiff.model_dump()`, so the wire does not change, and S3 already edits this module. (b) adds a WK-1178 slice to S3's critical path for a one-line change; (c) splits FR-219's view from the slice `PL-1286` gave it | **yes** — before activation | the maintainer (by delegation), since item 5 names "before that slice dispatches" and (a) reads it as "in the dispatching slice" |
| **DP-S3-2** | S2's plan says drag-to-connect "arrives with S3's live validation". `PL-1286`'s S3 row does not name it. Is it in S3? | (a) not in S3: edges still change only through the inspector's `consumes` field; (b) in S3: a drag appends the source's produced name to the target's `consumes`, `isValidConnection` refuses nothing, and the route reports the result | **(a).** No FR requires it, the row does not name it, and (b) widens the slice. With live validation, (b) can be added later without a rule on the client | no — default (a) applies unless decided otherwise before activation | the maintainer (by delegation) |

**Choices this plan makes itself** (no spec leaves them open, or a ruling gives them to the
leaf plan):
- **Call frequency** (RL 9767, *Not decided here*: "S3's leaf plan's to state"). The
  composable waits **400 ms** after the last draft change, then calls the route; a new change
  aborts any call in flight through `AbortController`; a response is applied only if its
  sequence number is the latest. No NFR is set.
- **Save stays enabled** while issues are shown. Save is unchanged (T1: "Save is unchanged
  and still refuses on the first issue with its code"), and the server is the authority.
- **The overlay's other version** is a number input, defaulting to the loaded version minus
  one (hidden when the version is 1); a 404 is shown as "version not found". `03` §5.1 has no
  route listing an algorithm's versions, and S3 adds none.
- **The invariant function's name and home:** `graph_invariant_issues(draft:
  RatingAlgorithmDraft) -> list[ValidationIssue]` in `model_schema/rating.py`, beside the
  class.
- **The mode-check typing:** `compile_bundle` catches the `ValueError` from
  `check_model_reference_mode` and re-raises it through `_raise_named`
  (`compile.py:538`), the mechanism every other compile refusal already uses. The
  model-schema function is not edited, so its other callers are unaffected. RL-1438 leaves the
  design to the build; this is the smallest that uses the existing path.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Re-run every Task 0 row at the dispatch tree; record each result in the
  ledger.
- [ ] **Step 2:** Read the minted RL-1474, RL-1438 and FD-1437. Replace `RL-<9767>`,
  `RL-<9758>` and `FD-<9759>` in this plan's commands with the minted ids in the ledger. If a
  minted text differs from the heads cited above, the minted text governs; name each
  difference.
- [ ] **Step 3:** Read S2's merged code: `RatingAlgorithmDraft` and `RatingAlgorithm` in
  `rating.py`, `ratingAlgorithms.ts`, `DagDesigner.vue`, `StepNode.vue`, `NodeNavigator.vue`.
  Record their exact prop and export names. If any differs from Task 6's *Consumes*, the
  merged code governs.

### Task 0A: The diff route typed; the contract and the client (DP-S3-1) — the slice's FIRST commit

*Dated note, 2026-10-05 (written 17:35:08 BST, pre-mint): this task was Task 5, and it now
runs first, after Task 0 (which commits nothing) and before Task 1's `model-schema` commit.
The other tasks keep their numbers. The move makes the plan meet, literally, the entry
headed "2026-10-05 17:30:02 BST — Rulings: T2 routing (RL 9562 mints ahead of PL 9560); _NUMERIC FD go; WK-675 DP-S3-1 (a) with the FD-1335 reading; DP-S13-1 (a′)", item 4, whose dated line reads verbatim:*

> The DATED LINE, by the maintainer (by delegation): "FD-1335 item 5 (:333-335, 'fixed before that slice dispatches') is read, for the consuming slice's OWN route only, as satisfied when that slice types the route in its FIRST commit, before any frontend code consumes the route, with generate-contracts --check green at that commit. The hold stays as written for every other route of the 12 and for any slice that does not type the route itself. Precedent: FD-1366 rule (ii)."

*Why it can run first:*
- *It depends only on `AlgorithmDiff`, already on main
  (`packages/model-schema/src/model_schema/rating.py:541` at `4d3be141`), and on the existing
  handler and service: `algorithm_diff` (`backend/src/app/api/rating_algorithms.py:53-68`)
  and `diff_between` (`backend/src/app/platform/rating_algorithms.py:157`, returning
  `diff_algorithms(base, current).model_dump()` at `:163`).*
- *It uses nothing Tasks 1 to 4 add.*
- *No frontend code consumes the route until Task 7 (`getAlgorithmDiff`).*
- *`generate-contracts --check` is green at this commit (Step 2).*
- *It types only this slice's own route: the validate route is new and typed at birth in
  Task 4, so it is not one of `FD-1335`'s twelve.*
- *Its contract check covers only the diff route. The validate route's check (Acceptance 11)
  moves to Task 4 Step 5a, because that route does not exist yet.*

- [ ] **Step 1 (if DP-S3-1 (a)):** `algorithm_diff` returns `AlgorithmDiff`, and
  `diff_between` returns the `AlgorithmDiff` it builds instead of `.model_dump()`. If
  `UNTYPED_2XX_PENDING_PART_B` exists, remove the diff entry and see its guard red with the
  entry kept (Acceptance 21).
- [ ] **Step 2:** `uv run python scripts/generate-contracts.py`, then `--check` exits 0;
  `pnpm --dir frontend generate:api`. Check Acceptance 21 with:

```bash
python3 -c "import json;d=json.load(open('docs/contracts/openapi/generated.json'))['paths'];print(d['/api/v1/rating-algorithms/{slug}@{version}/diff']['get']['responses']['200']['content']['application/json']['schema'])"
```

  Expected: one `$ref`, to `AlgorithmDiff`.
- [ ] **Step 3: Commit**, the slice's first: `feat(rating): type the algorithm diff response; regenerate the contract (FD-1335 item 5, DP-S3-1)`.

### Task 1: `ValidationIssue`, `AlgorithmValidationReport` and `graph_invariant_issues` (model-schema)

**Files:**
- Modify: `packages/model-schema/src/model_schema/rating.py` (`RatingAlgorithm._graph_invariants`, `:395-476` at `137bc817`)
- Modify: `packages/model-schema/src/model_schema/__init__.py`
- Create: `packages/model-schema/tests/test_graph_invariant_issues.py`

**Interfaces:**
- Produces: `ValidationIssue` (`code: str`, `message: str`, `step_id: str | None = None`,
  `field: str | None = None`, frozen; moved unchanged); `AlgorithmValidationReport`
  (`issues: list[ValidationIssue]`, frozen, `extra="forbid"`);
  `graph_invariant_issues(draft: RatingAlgorithmDraft) -> list[ValidationIssue]`.

- [ ] **Step 1: The failing tests**, using the algorithm payload helpers the existing
  `test_rating_algorithm.py` uses:

```python
import pytest
from model_schema import RatingAlgorithmDraft, graph_invariant_issues


@pytest.mark.req("FR-215")
def test_a_duplicate_step_id_is_the_only_issue_even_with_a_cycle() -> None:
    draft = RatingAlgorithmDraft.model_validate(_with_duplicate_and_cycle())
    issues = graph_invariant_issues(draft)
    assert [(i.code, i.step_id) for i in issues] == [("VALIDATION_FAILED", "s_dup")]


@pytest.mark.req("FR-212")
def test_a_cycle_names_only_the_steps_on_it() -> None:
    draft = RatingAlgorithmDraft.model_validate(_two_cycle_with_downstream())
    cyclic = {i.step_id for i in graph_invariant_issues(draft) if i.code == "RATING_GRAPH_CYCLIC"}
    assert cyclic == {"s_a", "s_b"}


@pytest.mark.req("FR-212")
def test_no_ambiguous_producer_issue_after_a_cycle() -> None:
    draft = RatingAlgorithmDraft.model_validate(_cycle_and_two_producers())
    assert all("re-production chain" not in i.message for i in graph_invariant_issues(draft))


@pytest.mark.req("FR-212")
def test_every_breach_is_reported_not_the_first() -> None:
    draft = RatingAlgorithmDraft.model_validate(_unresolved_and_orphan())
    codes = [(i.code, i.step_id) for i in graph_invariant_issues(draft)]
    assert ("RATING_GRAPH_UNRESOLVED_REF", "s_consumer") in codes
    assert ("VALIDATION_FAILED", "s_orphan") in codes


@pytest.mark.req("FR-214")
def test_a_declared_output_without_an_output_step_has_no_step_id() -> None:
    draft = RatingAlgorithmDraft.model_validate(_output_without_step())
    issue = graph_invariant_issues(draft)[0]
    assert issue.step_id is None and "FR-214" in issue.message
```

  Each `_…` helper returns a JSON dict built from the module's existing valid payload, with
  the one change its name states. Write them in the test file.
- [ ] **Step 2: Run to see each fail** on `ImportError: cannot import name
  'graph_invariant_issues'`. `uv run pytest packages/model-schema/tests/test_graph_invariant_issues.py -q`.
- [ ] **Step 3: Implement.** Move `ValidationIssue` from `compile.py:60-72` into `rating.py`,
  above `RatingAlgorithmDraft`, unchanged. Add `AlgorithmValidationReport`. Write
  `graph_invariant_issues` from the body of `_graph_invariants`, in today's order, appending
  an issue where today's code raises:
  1. duplicate `step_id`: one `VALIDATION_FAILED` per duplicated id, with that `step_id`;
     **return** the list;
  2. FR-214: one `VALIDATION_FAILED` per output, `step_id=None`, today's message;
  3. unresolved reference: one `RATING_GRAPH_UNRESOLVED_REF` per consuming step and name,
     with the consuming `step_id`, today's message; no edge for it;
  4. cycle: after Kahn's sort, if steps remain, compute the steps **on** a cycle (a step that
     reaches itself through `dependencies`, self-edges excluded as today) and add one
     `RATING_GRAPH_CYCLIC` per such step, message `"step {id!r} lies on a cycle (FR-212)"`;
  5. ambiguous producer, **only if there was no cycle**: one `VALIDATION_FAILED` per later
     producer that does not consume the name, with its `step_id`, today's message;
  6. orphan, always: one `VALIDATION_FAILED` per orphan, with its `step_id`, today's message.

  `_graph_invariants` becomes: `issues = graph_invariant_issues(self)`; if none, return
  `self`; else raise on `issues[0]` — `GraphCycleError("the rating DAG contains a cycle
  (FR-212)")` for `RATING_GRAPH_CYCLIC`, `GraphUnresolvedRefError(issues[0].message)` for
  `RATING_GRAPH_UNRESOLVED_REF`, and `ValueError(issues[0].message)` otherwise. The cycle
  message is today's, so the save path's text does not change. `_reachable` and
  `_reaches_output` stay static methods of `RatingAlgorithm`, and `graph_invariant_issues`
  calls them as `RatingAlgorithm._reachable(...)`, as `sub_graphs.py:118` does.
- [ ] **Step 4: Green**, then `uv run pytest packages/model-schema -q` (one package, not the
  suite) with every existing test unmodified.
- [ ] **Step 5: Broken input** (Acceptance 2, 4): drop step 1's `return` and step 5's guard;
  see both order tests red; restore. Then make the function return after its first issue; see
  the all-breaches test red; restore. Record the three reds.
- [ ] **Step 6: Commit** `feat(model-schema): graph_invariant_issues, ValidationIssue and AlgorithmValidationReport (RL-<9767> items 2 and 4)`.

### Task 2: pricing-core imports `ValidationIssue`; the mode mismatch is named at compile (FD-1437 limb 2; RL-1438 T1)

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/compile.py` (import block; `:60-72`; `compile_bundle` `:614`)
- Modify: `packages/pricing-core/tests/test_rating_compile_bundle.py` (`:235`)
- Modify: `backend/src/app/errors.py` (`RATING_ERROR_CODES`, `:309`)
- Modify: `backend/tests/test_errors.py`
- Create: `backend/tests/test_rating_mode_mismatch_api.py`
- Modify: `docs/specs/03-rating-engine.md` (FR-223's cell, `:109`)

- [ ] **Step 1: The failing tests.** Tighten the pure test:

```python
@pytest.mark.req("FR-223")
async def test_a_mode_mismatch_is_refused_at_compile() -> None:
    """FR-223: a model_call mode disagreeing with the version fails compilation, named."""
    version = _version().model_copy(update={"model_reference_mode": "approximation"})
    with pytest.raises(CodedError, match=r"^MODEL_REFERENCE_MODE_INCONSISTENT: .*'s_model'"):
        await compile_bundle(version, _resolver())
```

  Use the `model_call` step id the module's `_version()` fixture pins; read it first and put
  it in the pattern. Add the HTTP test in `test_rating_mode_mismatch_api.py`, built on
  `test_a_step_ref_the_pins_do_not_carry_is_refused_over_http`
  (`backend/tests/test_rating_pin_membership_api.py:36`), importing `_handlers` and
  `_run_compile_job` by name as that module does. No route writes `model_reference_mode`
  (RL-1438 item 2), so the test sets it on the row before compiling, then asserts
  `job_row.status is JobStatus.FAILED` and
  `job_row.error["code"] == "MODEL_REFERENCE_MODE_INCONSISTENT"`. A second test saves the
  mismatching algorithm and asserts 201 (Acceptance 19). In `test_errors.py`:

```python
@pytest.mark.req("FR-223")
def test_the_mode_code_is_owned_in_the_spec_and_registered() -> None:
    spec = Path("docs/specs/03-rating-engine.md").read_text(encoding="utf-8")
    owned = spec.split("**Error codes owned by this module:**", 1)[1].split("\n\n", 1)[0]
    assert "`MODEL_REFERENCE_MODE_INCONSISTENT`" in owned
    assert "MODEL_REFERENCE_MODE_INCONSISTENT" in RATING_ERROR_CODES
```

  Resolve the path from the repository root as the module's other file reads do.
- [ ] **Step 2: Run each red, by its cause.** The pure test: `CodedError` not raised (a bare
  `ValueError`). The HTTP test: `BUNDLE_COMPILE_FAILED`. The registry test: the second assert.
- [ ] **Step 3: Implement.** In `compile.py`, delete the class body at `:60-72`, add
  `from model_schema import ValidationIssue` in the import block, and keep
  `"ValidationIssue"` in `__all__`. Replace `:614` with:

```python
    try:
        check_model_reference_mode(version, algorithm)
    except ValueError as exc:
        _raise_named("MODEL_REFERENCE_MODE_INCONSISTENT", str(exc))
```

  Add `"MODEL_REFERENCE_MODE_INCONSISTENT"` to `RATING_ERROR_CODES` beside
  `"BUNDLE_COMPILE_FAILED"`, under the existing `# Bundle compilation (W9-3).` comment. Apply
  RL-1438 T1 to FR-223's cell byte for byte: the find string `(`02` OQ-575, decided
  2026-08-17.) |` is replaced by `(`02` OQ-575, decided 2026-08-17.) ` followed by T1's block,
  with `<date>` and `RL-<this>` filled.
- [ ] **Step 4: Green.** Run the three files named in Step 1, and
  `uv run pytest packages/pricing-core/tests/test_rating_compile.py packages/pricing-core/tests/test_rating_compile_bundle.py -q`.
- [ ] **Step 5: Commit** `fix(rating): name MODEL_REFERENCE_MODE_INCONSISTENT at compile (FD-<9759> limb 2; RL-<9758> T1)`.

### Task 3: The bare-`ValueError` sweep (FD-1437 limb 3)

- [ ] **Step 1: List the candidates.** At the slice's tree, run and paste verbatim into the
  ledger:

```bash
git grep -n -E 'raise (ValueError|[A-Za-z]*Error)\(|_raise_named\(' -- \
  packages/pricing-core/src/pricing_core/rating/compile.py \
  packages/model-schema/src/model_schema/rating.py
```

  Then, for each function `compile_bundle` calls (read its body at the tree), name whether it
  can raise a `ValueError` that is not a `CodedError`: `RatingAlgorithm.model_validate`
  (a pydantic `ValidationError` is a `ValueError`), `check_model_reference_mode` (now named,
  Task 2), `check_step_refs_pinned`, `validate_algorithm`, `to_jdm`, `bundle_hash`, and the
  `Bundle(...)` construction.
- [ ] **Step 2: Write the table** (Acceptance 20): one row per site that can reach the
  `except ValueError` in `backend/src/app/platform/rating_versions.py`
  `compile_rating_version`, with file, symbol, today's outcome, and either the named code it
  now carries or why `BUNDLE_COMPILE_FAILED` is right. State the count. A site that should
  carry a named code and has none in `03` §5.1 is **not** fixed here: it is recorded for the
  auditor as a finding candidate.
- [ ] **Step 3:** No code change unless Step 2 names one that maps to an existing owned code.
  Any such change gets a red-first test in `test_rating_compile_bundle.py`.

### Task 4: The validate route, spec first (RL-1474 T1–T4; items 3, 5, 6)

**Files:**
- Modify: `docs/specs/03-rating-engine.md` (§3.1 after `| **FR-219** |`; §4.1 after the paragraph ending `and unreferenced by an `output` (FR-212).`; §5.1 after the `…/diff?against=` row)
- Modify: `docs/specs/00-overview.md` (FR-24's second cell)
- Modify: `backend/src/app/api/rating_algorithms.py`; `backend/src/app/platform/rating_algorithms.py`
- Create: `backend/tests/test_rating_algorithm_validate.py`

**The route, as RL-1474 rules it:**

| Method, path | Request body | 2xx response | Permission |
|---|---|---|---|
| `POST /api/v1/rating-algorithms/validate` | `RatingAlgorithmDraft` | **200** `AlgorithmValidationReport` | `rating:write` |

- [ ] **Step 1: Apply T1–T4 byte for byte.** T1 takes the next free requirement id in `03`;
  record it in the ledger and use it for `FR-<new>` everywhere below. Use T2's three-cell form
  if Task 0.11 still reads `1`, else the four-cell form. If S2's RL-1475 T1 row now follows
  FR-219, T1 still goes **immediately after** the FR-219 row, as its anchor says; record that
  the row is then not the table's last (T1's "as the last row" is placement prose, not the
  anchor).
- [ ] **Step 2: The failing tests** (Acceptance 1, 3, 5, 6, 8, 9, 10), each
  `@pytest.mark.req("FR-<new>")`, using the module fixtures `test_rating_algorithms.py` uses.
  The parity test:

```python
@pytest.mark.req("FR-<new>")
@pytest.mark.parametrize("name", INVALID_SAVE_FIXTURES)
def test_the_first_reported_issue_is_the_code_save_refuses_with(api_client, headers, name) -> None:
    body = INVALID_SAVE_FIXTURES[name]()
    saved = api_client.post("/api/v1/rating-algorithms", json=body, headers=headers)
    report = api_client.post("/api/v1/rating-algorithms/validate", json=body, headers=headers)
    assert report.status_code == 200
    assert report.json()["issues"][0]["code"] == saved.json()["code"]
```

  `INVALID_SAVE_FIXTURES` is a dict, name → payload builder, collected in the new module from
  the payloads `test_rating_algorithms.py`'s refusal tests build. The 422 test asserts
  `body["errors"][0]["loc"]` (or the field-error key `_handle_validation_error` emits; read
  it at the tree) starts with `["body", "steps", 0]`.
- [ ] **Step 3: Red,** each on 404 (no route).
- [ ] **Step 4: Implement.** In `platform/rating_algorithms.py`:

```python
def validate_draft(draft: RatingAlgorithmDraft) -> AlgorithmValidationReport:
    """FR-<new>: every issue saving `draft` would refuse on, located; nothing persisted."""
    issues = graph_invariant_issues(draft)
    if issues:
        return AlgorithmValidationReport(issues=issues)
    algorithm = RatingAlgorithm.model_validate(draft.model_dump(mode="json", exclude_unset=True))
    return AlgorithmValidationReport(issues=validate_algorithm(algorithm))
```

  In `api/rating_algorithms.py`, register the route **before** any `{slug}@{version}` route
  with the same method, so `validate` is never read as a slug:

```python
@router.post(
    "/rating-algorithms/validate",
    summary="Validate an unsaved Rating Algorithm without saving it",
    responses=problems(401, 403, 422),
)
async def validate_rating_algorithm(
    body: RatingAlgorithmDraft,
    caller: RatingWriteDep,
) -> AlgorithmValidationReport:
    """**200** with every located issue (FR-<new>); nothing is persisted or audited."""
    return service.validate_draft(body)
```

  The handler takes no `DatabaseDep`: it reads and writes nothing (Acceptance 8).
- [ ] **Step 5: Green;** then Acceptance 7's unmodified suites. Broken input for Acceptance 1
  and 9 as stated there; record each red.
- [ ] **Step 5a:** *(Added 2026-10-05, pre-mint; moved from the old Task 5 Step 2 when that
  task became Task 0A.)* `uv run python scripts/generate-contracts.py`, then `--check` exits
  0; `pnpm --dir frontend generate:api`. Check Acceptance 11 with:

```bash
python3 -c "import json;d=json.load(open('docs/contracts/openapi/generated.json'))['paths'];v=d['/api/v1/rating-algorithms/validate']['post'];print(v['requestBody']['content']['application/json']['schema'],v['responses']['200']['content']['application/json']['schema'])"
```

  Expected: two `$ref`s, to `RatingAlgorithmDraft` and `AlgorithmValidationReport`.
- [ ] **Step 6: Commit** (one commit with Step 1's spec texts, `CLAUDE.md` §2)
  `feat(rating): POST /rating-algorithms/validate, discharging FR-24's designer exception (RL-<9767>)`.

### Task 5: moved to Task 0A (dated pre-mint note)

*Dated note, 2026-10-05 (pre-mint): this task now runs first, as Task 0A (§"Task 0A"), on the
entry headed "2026-10-05 17:30:02 BST — Rulings: T2 routing (RL 9562 mints ahead of PL 9560); _NUMERIC FD go; WK-675 DP-S3-1 (a) with the FD-1335 reading; DP-S13-1 (a′)", item 4. Its text moved there unchanged, except two things:*
- *its check now covers only the diff route;*
- *the validate route's contract check (Acceptance 11) moved to Task 4 Step 5a.*

*The number 5 is kept, not reused.*

### Task 6: Live validation in the designer (FR-<new>, FR-24)

**Files:** `frontend/src/api/ratingAlgorithms.ts`;
`frontend/src/components/dag/useGraphValidation.ts`, `GraphIssues.vue`, and S2's
`StepNode.vue`, `NodeNavigator.vue`, `DagDesigner.vue`; their tests under
`frontend/src/components/dag/__tests__/`.

**Interfaces:**
- Consumes (S2, re-read in Task 0 Step 3): `DagDesigner` props
  `{ draft: RatingAlgorithmDraft; versionMode; rateTablePins: string[] }`, emitting
  `update:draft`; `StepNode` props `{ data: { step: RatingStep } }`; `NodeNavigator` props
  `{ steps: RatingStep[]; selected: string | null }`; `request` with `signal`
  (`frontend/src/api/client.ts:37-47`).
- Produces:
  - `validateRatingAlgorithm(body: RatingAlgorithmDraft, signal?: AbortSignal): Promise<AlgorithmValidationReport>`;
  - `useGraphValidation(draft: MaybeRefOrGetter<RatingAlgorithmDraft>, delayMs = 400): { issues: Ref<ValidationIssue[]>; pending: Ref<boolean>; byStep: ComputedRef<Map<string, ValidationIssue[]>>; graphLevel: ComputedRef<ValidationIssue[]> }`;
  - `StepNode`'s `data` gains `issues: ValidationIssue[]`;
  - `GraphIssues` props `{ issues: ValidationIssue[]; pending: boolean }`.

- [ ] **Step 1: The API function.**

```ts
export type AlgorithmValidationReport = components["schemas"]["AlgorithmValidationReport"];
export type ValidationIssue = components["schemas"]["ValidationIssue"];

export function validateRatingAlgorithm(
  body: RatingAlgorithmDraft,
  signal?: AbortSignal,
): Promise<AlgorithmValidationReport> {
  return request<AlgorithmValidationReport>("/rating-algorithms/validate", {
    method: "POST",
    body,
    ...(signal ? { signal } : {}),
  });
}
```

- [ ] **Step 2: The failing composable tests** (Acceptance 15), with `vi.useFakeTimers()` and
  `@/api/ratingAlgorithms` mocked: three changes within 400 ms → one call; a change during a
  pending call → the first call's `signal.aborted` is `true`; a late older response does not
  replace `issues`.
- [ ] **Step 3: Implement `useGraphValidation`.** `watch(() => toValue(draft), …, { deep: true,
  immediate: true })`; on each change clear the timer, abort the controller, and after
  `delayMs` call with a fresh controller and a sequence number; apply the result only when the
  number is the latest; swallow `AbortError`. `byStep` groups by `step_id`; `graphLevel` keeps
  `step_id === null`. No check of the draft's content happens here.
- [ ] **Step 4: The failing designer tests** (Acceptance 12, 13, 23), stubbing `VueFlow` as
  S2's view tests do:
  - `it("FR-<new>: an unresolved reference is shown on its node before save")`: the mocked
    route returns a `RATING_GRAPH_UNRESOLVED_REF` issue on `s_b`; after the timers run, the
    `s_b` node contains the issue's message and `saveRatingAlgorithm` was not called;
  - a graph-level issue renders in `GraphIssues` inside `role="status"`;
  - the live region `aria-live="polite"` reads `2 issues`;
  - `NodeNavigator`'s option for `s_b` has an accessible name ending `, 1 issue`.
- [ ] **Step 5: Implement.** `DagDesigner` calls `useGraphValidation(() => props.draft)` and
  passes `byStep.get(id) ?? []` into each node's `data.issues`. `StepNode` renders, when
  issues exist, a text badge `⚠ {n}` with `aria-hidden="true"` on the glyph and the messages in
  a list below the label, the node's `aria-label` extended with `, {n} issue(s)`, and an
  `invalid` class that adds a border **and** keeps the text. `GraphIssues.vue` lists
  `graphLevel` issues by message and code. Add the `issues` count to `NodeNavigator`'s option
  name.
- [ ] **Step 6: Green;** `pnpm --dir frontend lint` and `type-check`; commit
  `feat(frontend): live graph validation on the designer's nodes (FR-<new>, FR-24)`.

### Task 7: The structural diff overlay (FR-219)

**Files:** `frontend/src/api/ratingAlgorithms.ts`; `frontend/src/components/dag/DiffOverlay.vue`
and its test; `DagDesigner.vue`; `StepNode.vue`.

**Interfaces:**
- Produces: `getAlgorithmDiff(slug: string, version: number, against: number): Promise<AlgorithmDiff>`;
  `DiffOverlay` props `{ slug: string; version: number }`, emitting `diff(value: AlgorithmDiff | null)`;
  `StepNode`'s `data` gains `diffMark: "added" | "changed" | null`.

- [ ] **Step 1: The API function.**

```ts
export type AlgorithmDiff = components["schemas"]["AlgorithmDiff"];

export function getAlgorithmDiff(slug: string, version: number, against: number): Promise<AlgorithmDiff> {
  return request<AlgorithmDiff>(
    `/rating-algorithms/${encodeURIComponent(slug)}@${version}/diff?against=${against}`,
  );
}
```

- [ ] **Step 2: The failing tests** (Acceptance 22): with the call mocked to return
  `added_steps: ["s_new"]`, `changed_steps: [{ step_id: "s_rate", field: "rate_table_ref", … }]`,
  `removed_steps: ["s_old"]`, the `s_new` node reads "added", `s_rate` reads "changed", and the
  panel lists `s_old` under "Removed" and the re-pointed table; a 404 shows "version not
  found"; clearing the input emits `diff(null)` and removes every marker.
- [ ] **Step 3: Implement** `DiffOverlay.vue`: a labelled `<input type="number" min="1">`
  defaulting to `version - 1` (the control is absent when `version` is 1), a "Compare" button,
  and the panel. `DagDesigner` maps the emitted diff to each node's `diffMark`. `StepNode`
  renders the mark as a text chip, "added" or "changed", beside the label.
- [ ] **Step 4: Green;** lint and type-check; commit
  `feat(frontend): structural diff overlay in the designer (FR-219)`.

### Task 8: Accessibility check (NFR-463)

- [ ] **Step 1:** Delegate a check of the designer, with issues and with the overlay shown,
  to the `accessibility-tester` agent against WCAG 2.2 AA: keyboard path, the live region, the
  text channel of every marker, contrast of the `invalid` border. Record its findings in the
  ledger; fix any AA failure in this slice.

### Task 9: The gate and the ledger

- [ ] **Step 1: The full gate, both halves** (`CLAUDE.md` §11), delegated to `gate-runner`,
  in the single gate window (RL-1445: one full gate at a time). Every command has rc 0.
  Record the per-command table and the tree.
- [ ] **Step 2: Self-check Acceptance 1–24**, command by command, pasting each output into the
  ledger.
- [ ] **Step 3: Open the PR**, naming the range `origin/main...HEAD`, FD-1437's sweep count,
  DP-S3-1's applied option, and whether `UNTYPED_2XX_PENDING_PART_B` existed.

## Hand-off

1. **To the lead, for `PL-1286`:** DP-6's *Resolved by* cell cites RL-1474 once minted.
   `PL-1286` is the planner's file and is not edited here.
2. **To the auditor at slice close:** FD-1437 limbs (2) and (3) are discharged here (limb (1)
   is RL-1438); its register row names the S3 PR. `FD-1335`'s diff-route entry is discharged
   if DP-S3-1 is (a), by Task 0A, the slice's first commit (dated note, 2026-10-05). FR-246 is **not** delivered by S3 (*Scope*): its verdict is "deferred
   with an owner", `FD-1374`'s WK-1178 remedy.
3. **To S9 (sub-graph mounting):** the validate route checks algorithms only; sub-graph
   validation keeps `SubGraphBody`'s own invariants (RL-1474 finding C).
4. **To the lead, a record line:** S3's dispatch record quotes the maintainer's entry of
   2026-10-01 10:30:00 BST for FD-1437 limb (2) (at the compile site alone). The holds
   register's *WK-675 S3 dispatch-record lines* already agree, corrected at 2026-10-05
   17:22:00 BST. *(Dated note, 2026-10-05, pre-mint: this item said the register "still
   say[s] 'at compile AND in the validate route'". It no longer does. The fix is the same
   one, ordered at 17:30:02 BST item 6.)*

## Self-review

- **Ruling coverage, by site class** (`README.md` convention 5). Each ruling appears in the
  narrative, Files, Steps and Acceptance:
  - RL-1474 items 1–7 and T1–T4: *Architecture*; item 1 as S2's (decision 5); items 2 and 4:
    Task 1; items 3, 5, 6: Task 4; item 7: *Scope* FR-223 row; T1–T4: Task 4 Step 1;
    acceptance 1–11: Acceptance 1–12;
  - RL-1474 finding C: Task 1 Step 3; *Out of S3*; Hand-off 3;
  - RL-1438 items 1–4, T1 and acceptance 1–4: Task 2; Acceptance 16–19;
  - FD-1437 limbs (2) and (3), with the 10:30:00 amendment: decision 2; Tasks 2 and 3;
    Acceptance 16–20; Hand-off 2 and 4;
  - RL-1445: Global Constraints; *Contention*; Activation need 3; Task 9;
  - `FD-1335` item 5: DP-S3-1; Task 0A (the first commit; was Task 5, dated note
    2026-10-05); Acceptance 21.
- **Literals verified at `137bc817`:** `ValidationIssue` (`compile.py:60-72`), its importers
  (`operations.py:57`, `platform/rating_algorithms.py:21`), `_graph_invariants`
  (`rating.py:395-476`), `_reachable` (`:479`), `_reaches_output` (`:499`),
  `check_model_reference_mode` (`:173`), `compile_bundle` (`compile.py:573`, `:611`, `:614`),
  `_raise_named` (`:538`), `CodedError` (`safe_error.py:64`), `RATING_ERROR_CODES`
  (`errors.py:309`), the diff handler (`api/rating_algorithms.py:53-68`) and `diff_between`
  (`platform/rating_algorithms.py:157-163`), `AlgorithmDiff` (`rating.py:541`),
  `request`'s `signal` (`client.ts:47`), the compile-Job test precedent
  (`test_rating_pin_membership_api.py:36-61`), and every spec anchor in Task 0.10.
  **Not verified:** S2's merged prop and export names (Task 0 Step 3 re-reads them); the
  `_version()` fixture's `model_call` step id (Task 2 Step 1 reads it); the exact field-error
  key of a 422 (Task 4 Step 2 reads it).
- **Spec coverage, by enumeration.** `PL-1286`'s S3 row (`:305`) read clause by clause:
  "DP-6's discharge: the numbered FR and the validate route" → Task 4; "errors on the node
  before save (FR-212, FR-223, FR-227)" → Tasks 1, 4, 6 (FR-223 by RL 9758 item 3: not on the
  node, at compile); "including `expression` steps, whose grammar (FR-244) and closed inputs
  (FR-246) the validate route checks" → FR-244 through `validate_algorithm`, FR-246 deferred
  (*Scope*); "the structural diff overlay (FR-219)" → Tasks 5 and 7. `PL-1371`'s "carries FD
  9759" → Tasks 2 and 3.
- **Placeholders:** `FR-<new>` (T1's id, taken at apply time), `RL-<this>`, `<date>`,
  `RL-<9767>`, `RL-<9758>` and `FD-<9759>` (minted ids). Each is filled in Task 0 Step 2 or
  Task 4 Step 1. No other placeholder remains.
- **Rulings re-checked before the PR:** open PRs on 2026-10-05, read for this plan's subject:
  #1055 @`07d9d230` (RL-1474), #1061 @`2e7eff8c` (RL-1438), #1059 @`3621fe7b` (FD-1437),
  #1162 @`381254c3` (RL-1445), #1131 @`c66300e5` (S2). Nothing else found rules on the
  validate route, the diff route or the designer's validation.
