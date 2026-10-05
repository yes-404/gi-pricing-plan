---
id: PL-9599
family: plan
kind: leaf
title: WK-1178 — Option A slice A-1, FD 9995 in full, the Peril Structure approval path and the compile resolver's peril branch (FR-191, FR-351, FR-355, FR-363, FR-237, FR-20): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: planner
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1356, PL-1408, SL-1409, RL-1301, RL-1263, PL-1371, CR-1212]
---

# PL 9599 (working id) — WK-1178: Option A slice A-1, FD 9995 in full: the Peril Structure approval path and the compile resolver's peril branch, leaf plan

Filed under working id 9599 (this plan) and slice working id 9600 (its `SL-` row under
WK-1178 in [`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead in
`~/gi-pricing-plan.local/handover/eta.md` (rows "SL 9600 / PL 9599", 5 Oct 16:46:27). The
same PR carries the row of A-2's slice, working id 9598, whose plan is PL 9597 (working id,
its own draft PR). Nothing here is minted.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `fastapi-service` (the carry and the resolver's
> `PlatformError`s), `spec-change` (Task 5, only where the ruling carries text),
> `dev-commands` (the two-half gate, the alembic DSN) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

A Peril Structure reaches `approved` only through `06`'s approval workflow, and a Rating
Version that pins one compiles when it is `approved` and is refused when it is not.
`api/approvals.py`'s `_carry_to_the_artifact` gains the peril call, and
`backend/src/app/platform/perils.py` gains `apply_approval_decision`, the writer of
`approved` on the decision path. `_Resolver.resolve` in
`backend/src/app/platform/rating_versions.py` gains a `peril_structure` branch, so the
stale "has no backend table yet (Phase 2)" message stops describing Peril Structures.
`PL 9683`'s Acceptance 7, which asserts that message as FD 9995's tripwire, is flipped in
the commit that adds the branch. This discharges FD 9995 (#980) in full.

**Architecture:** the perils module gains the seam every approvable type already has, an
`apply_approval_decision` that `_carry_to_the_artifact` drives inside its existing
`approval_decision()` block. `objectives.apply_approval_decision`
(`backend/src/app/platform/objectives.py:795`) is the model, and SL-1409's
`validation_rules.apply_approval_decision` the newest instance. The submit half already
exists: `perils.submit_for_review` (`perils.py:277`) moves `reconciled → review` and calls
`approvals.submit`. The resolver branch reads the row by ref and returns
`ResolvedArtifact(status=row.status, payload=to_structure(row).model_dump(mode="json"))`
(`to_structure`, `perils.py:64`). `compile_bundle`'s existing maturity loop
(`packages/pricing-core/src/pricing_core/rating/compile.py:624`, over `all_refs` built at
`:618`) then refuses anything not in `_APPROVED_OR_BETTER` (`:404`), because
`peril_structure` is not in `_MATURITY_CHECK_EXEMPT` (`:431`). No `compile.py` change is
needed for that refusal.

**Tech Stack:** Python 3.12, FastAPI + Pydantic v2, SQLAlchemy 2 async, PostgreSQL 16 (the
`approval_guard()` trigger; `peril_structures` is in its population,
`backend/tests/test_approval_guard.py` `EXPECTED_GUARDED`), pytest.

**Spec, finding and decision:**
- FD 9995 (working id; #980 @`9074f155`), `docs/findings/FD-09995-a-peril-structure-has-no-approval-path-and-the-compile-resolver-has-no-peril-branch-so-the-day-one-is-added-an-unapproved-peril-can-be-pinned.md`
  on that branch, §"Disposition": *"It is discharged in full when a peril approval path and
  the resolver branch land together and the tripwire is replaced by a positive test that an
  unapproved peril is refused at compile."* **That sentence is this slice's scope.**
- [`../specs/02-modelling.md`](../specs/02-modelling.md) FR-190, FR-191 (`02:296-297`);
- [`../specs/06-governance.md`](../specs/06-governance.md) FR-351, FR-355, FR-363 and its
  Peril Structure evidence row (`06:118`, *"Per-peril model approvals; reconciliation
  result within tolerance (`02` FR-190)"*), FR-386, and §4.2's floor note (`06:405-408`,
  *"`peril_structure` has an **empty** floor … because its reconciliation half is enforced
  structurally and its per-peril approvals half is unqueryable"*);
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) FR-237 (`03:134`) and
  [`../specs/00-overview.md`](../specs/00-overview.md) FR-20 (maturity at compile).

## The maintainer's decisions this plan rests on, quoted

From `~/gi-pricing-plan.local/channel/to-lead.md`, the entry headed *"2026-10-05 16:43:31
BST — THE MAINTAINER'S DECISION (asked live): G2 takes OPTION A, WF-699's literal Peril
Structure path is BUILT IN P2; and the FD 9605 approval, now on the record"*, read in full
by this planner. Verbatim:

> THE MAINTAINER, asked live with the sizing memo's two options (handover/sizing-g2-peril-path-2026-10-05.md, read at cdaaa573): "A: build it in P2". So G2 (CR-1212 :62-69, "WF-699 end to end") stands as written, no amendment, and the exit demo walks WF-699's trigger (:19), precondition (:28), B4 (:59, a model_call referencing the Peril Structure) and C1 (:70, pinning it).

> 1. Four serial build slices under WK-1178, as sized: A-1 FD 9995 in full (the peril approval carry plus the _Resolver peril branch; it flips PL 9683's Acceptance 7); A-2 GLM via model_call (FD 9605); A-3 Peril Structure scoring (compile resolves and maturity-checks the component models; the runtime calls assemble_risk_premium, fixing the bare KeyError on payload["fit_result"] at runtime.py:540); A-4 the demo scope on PL 9624/PL 9629 (a severity GLM, the peril structure, reconcile, approve, the B4 model_call, the C1 pin). About 5 executor-days likely (3.5–8), a chain after PL 9683 and PL 9649.
> 2. SEVERITY: FD 9995 → HIGH, deadline before the P2 exit demo (now a G2 blocker). FD 9605 (#1172, the GLM model_call refusal) → HIGH, the same. Both take lanes under my 13:12:56 priority rule.
> 3. Planning starts now: leaf plans for A-1..A-4, red first, with contention against the in-flight plans.

> 5. RISK, recorded: the sizing fits before the 4 Nov code freeze only on "3 lanes every day" (about 2 days spare at best). The maintainer has said the VM may be shut down from when the weekly allowance runs out until the reset (10 Oct 01:59 UTC); lost days come out of that slack. The Friday 9 Oct checkpoint re-checks the fit with measured progress.

FD 9995's owner and tripwire rest on the maintainer's entry of 2026-09-30 11:25:33 BST, as
FD 9995 quotes it: *"perils: LOW FD with a named owner and a tripwire"*, the owner rule *"If
no P2 Work schedules it, the owner is WK-1178, with the trigger 'before any resolver
branch'"*, and the tripwire *"that fails if `_Resolver` resolves peril_structure while
`_carry_to_the_artifact` has no peril branch (or perils.py has no approved writer on the
decision path)"*. Item 2 above raises its severity to HIGH; the owner stays WK-1178.

**Dated note, 2026-10-05 (written 17:05:11 BST, pre-mint): DP-1 to DP-3 accepted.** From the
same file, the entry headed *"2026-10-05 17:02:50 BST — A-1/A-2 plans and batch 5 noted; the
model_call ROUNDING is fixed IN A-2 by declared result type, not worked around in A-3"*, read
in full by this planner. Verbatim, its A-1 paragraph:

> A-1 (#1177 PL 9599): its DPs at the plan's recommendations, DP-1 (a) FR-363 per-peril approvals enforced at approval, DP-2 (a) supersede the earlier approved version, DP-3 (b) a named interim refusal until A-3: ACCEPTED (no DM needed; each is a choice inside settled scope).

The same entry rules that A-2 settles the `model_call` rounding at the root, and that A-3
*"composes frequency × severity on Decimals and rounds once, at the money step"*. It does not
change this slice's scope: DP-3 (b)'s interim branch refuses before any value is produced.

## Status

`draft`. **The three decision points are ruled** (§"Decision points"): the maintainer (by
delegation) accepted each at the plan's recommendation in the 17:02:50 BST entry quoted above,
with no decision-maker ruling (dated note, 2026-10-05). The plan moves to `active` only
through a separate activation PR, after every activation need below holds. That PR carries
the `SL-` row's status flip and this plan's.

### Activation needs, in order

1. **FD 9995 minted**, at HIGH with the deadline "before the P2 exit demo" (item 2 above).
   The finding at #980 still reads "Severity: low"; its mint applies item 2.
2. **PL 9683's slice merged** (the FD 9708 fix, #1140, lane C). It adds
   `backend/tests/test_rating_version_create_pins.py`, whose
   `test_a_peril_structure_pin_is_stored_and_compile_reports_no_resolver` (its Acceptance 7)
   this slice flips, and it is the only route that writes a `peril_structure` pin
   (`_PIN_TYPES`, its Task 2). Without it there is no Acceptance 7 to flip and no HTTP way to
   pin a peril.
3. **PL 9649's slice merged** (the FR-240 family fix, #1152). It edits `_Resolver.resolve`
   (a `factor` branch, and the `model` branch carries the model's Factors) and
   `compile_bundle`. This slice edits the same method. The maintainer's item 1 orders the
   chain "after PL 9683 and PL 9649".
4. **A ruling on DP-1 to DP-3** (a dated `RL-`, written by a decision-maker). Where the
   ruling and this plan differ, the ruling wins, and the dispatch record names each
   difference at every site it operates ([`README.md`](README.md) rule 5).
   *Dated note, 2026-10-05 (pre-mint): **held.** The 17:02:50 BST entry accepted DP-1 (a),
   DP-2 (a) and DP-3 (b) "(no DM needed; each is a choice inside settled scope)", so no
   `RL-` is written. The ruling and this plan do not differ; the dispatch record cites the
   entry by its header.*
5. **The lane and the dispatch GO.** A HIGH G2 blocker takes the first build lane that frees
   once its plan is active (the maintainer's 13:12:56 BST priority rule, item 2 above). This
   slice is the first of the serial chain A-1 → A-2 → A-3 → A-4 (item 1). The lead's
   dispatch record writes `RL 9620`'s same-Work conditions (a) and (b) for every WK-1178
   slice in flight beside it (§"Write set").

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red
first" means the named test was run and failed **for the stated cause** before the code that
turns it green; a failure with the right status and a different cause is a plan defect
([`README.md`](README.md) rule 2). Each red is recorded in the slice's ledger with the
failure line as printed.

1. **The generic decide carries a Peril Structure (FR-351, FR-355).** In
   `backend/tests/test_api_approvals.py`, `_AFTER["peril_structure"]` becomes
   `_moves("approved", "review", "reconciled")` and `_MOVE_ACTION` gains
   `"peril_structure": lambda to: f"peril_structure.{to}"`. The four `peril_structure` cases
   of `test_a_decision_moves_the_version_as_fr_355_says_and_records_it_truly` then pass:
   two approvals move the structure to `approved`; one of two leaves it `review`; reject and
   request-changes move it to `reconciled`. **Red first, by its cause:** at `137bc817`,
   `_AFTER["peril_structure"]` is `dict.fromkeys(_OUTCOMES, "review")` (`:1049`), the gap
   pinned as behaviour; with the new expectation the `approve` case fails on
   `assert … == expected` with `'review' == 'approved'`.
2. **`reconciled`, never `draft`, on a non-approval.** `review → reconciled` is the only
   backward edge in `VALID_PERIL_STRUCTURE_TRANSITIONS`
   (`packages/model-schema/src/model_schema/perils.py:118-131`; its comment: "`review →
   reconciled`, never `review → draft`"). The carry writes `reconciled` for `rejected` and
   `changes_requested`, and the reconciliation stays on the row. Covered by item 1's
   `reject` and `request_changes` cases.
3. **Every transition is audited.** Each move writes one `peril_structure.<status>` Audit
   Event with `before.status`, `after.status` and `after.approval_request_id`. Covered by
   item 1's `_decision_moves` assertion.
4. **An earlier approved version is superseded** (DP-2 (a)).
   `test_approving_a_peril_structure_supersedes_the_earlier_approved_version` in the new
   module `backend/tests/test_peril_structure_approval.py`: `ps@1` approved through the
   workflow, then `ps@2` approved; `ps@1` reads `superseded` and carries one
   `peril_structure.superseded` event. Red first: at the base `ps@2` stays `review`
   (no carry), so the test fails on `ps@2`'s status.
5. **Per-peril model approvals are enforced at approval** (DP-1 (a)).
   `test_a_peril_structure_with_an_unapproved_component_is_refused_at_approve` (new
   module): a structure whose one peril's `frequency_model` is `fitted`, not approved,
   submitted and decided `approve`, answers `422` with `code == "EVIDENCE_INCOMPLETE"`
   and a detail naming the component's ref; the structure and the request stay `review`,
   and no `approval_decisions` row survives (the decision rolls back with the carry, as
   SL-1409's Acceptance 6). The control,
   `test_a_peril_structure_whose_components_are_all_approved_is_approved`, passes. Red
   first: at the base decide returns `200` and the structure stays `review`.
6. **The resolver resolves a Peril Structure, and maturity refuses an unapproved one
   (FR-237, FR-20; FD 9995's positive test).**
   `test_an_unapproved_peril_structure_pin_is_refused_at_compile` (new module), parametrised
   over `reconciled` and `review`: a structure in that status pinned through
   `POST /api/v1/rating-versions` (`pins.models = ["peril_structure:<slug>@1"]`) compiles to
   a failed Job with `error["code"] == "PIN_NOT_APPROVED"` and the ref in its message. The
   same structure approved through the workflow then recompiles to `succeeded`, and the
   Bundle's `resolved_payloads["peril_structure:<slug>@1"]["status"] == "approved"`. Red
   first: at the base every case fails `NOT_FOUND` with "has no backend table yet".
7. **PL 9683's Acceptance 7 is flipped, in the commit that adds the branch.**
   `test_a_peril_structure_pin_is_stored_and_compile_reports_no_resolver` in
   `backend/tests/test_rating_version_create_pins.py` (added by PL 9683's slice) is renamed
   `test_a_peril_structure_pin_is_stored_and_compile_names_the_missing_structure`. It pins
   `peril_structure:motor-perils@1`, which no row holds, and now asserts `NOT_FOUND` with
   the ref in the message and **without** "has no backend table yet". Its docstring names
   FD 9995's discharge and this plan. Red first: with the new assertion and no branch, it
   fails on the absent-phrase check. *(Its first cause is a missing row, which is why it
   still fails; item 6 is the positive test FD 9995 asks for.)*
8. **The stale message is gone for every type.** After the branch, the resolver's final
   `NOT_FOUND` (`rating_versions.py:550-555` at `137bc817`) no longer says "no backend table
   yet (Phase 2)": it says the compile resolver has no branch for `<type>`. Check:
   `git grep -n "no backend table yet" -- backend/src` prints nothing. *(The other
   fall-through types are those no branch handles at the merge tree; PL 9649 adds `factor`
   and WK-1250 S2 adds `sub_graph`, so the set is re-read at dispatch.)*
9. **No `approved` writer outside the decision path.** `git grep -n
   "PerilStructureStatus.APPROVED" -- backend/src` prints only lines inside
   `perils.apply_approval_decision`, and `approval_guard()`'s trigger still refuses a direct
   write: the existing `backend/tests/test_approval_guard_trigger.py` passes unchanged with
   `peril_structures` in `EXPECTED_GUARDED`.
10. **The interim score refusal names its cause** (DP-3 (b)). Between this slice and A-3, a
    `model_call` step with a `peril_structure_ref` compiles once the structure is approved,
    and its scoring reads `payload["fit_result"]` (`runtime.py:540`), a `KeyError` the `zen`
    binding reports only as a generic node error (`_model_call_failure`'s docstring,
    `runtime.py:94`). `test_a_peril_structure_model_call_is_refused_with_a_named_reason` in
    `packages/pricing-core/tests/test_rating_runtime.py` (appended): the handler returns the
    `MODEL_CALL_ERROR_KEY` sentinel whose message names the ref and "A-3", and `score_one`
    raises `MODEL_CALL_FAILED`. Red first: at the base the handler raises `KeyError:
    'fit_result'`. **A-3 replaces this branch and this test.**
11. **The gate.** The full two-half gate (`CLAUDE.md` §11) passes on the merge tree, run
    once, holding the one gate slot (`RL 9620` as corrected at 15:27:25 BST). The ledger
    records each rc and the tree.
12. **The write set.** `git diff --stat origin/main...HEAD` names only §"Write set"'s paths,
    recorded in the ledger.

## Global Constraints

- **Money and maths are untouched**; this slice changes governance and compile resolution.
- **No pandas** (`CLAUDE.md` §3).
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2): the
  resolver's payload is `PerilStructure.model_dump`, through `to_structure`.
- **The approval guard is preserved** (`RL-1301` A.4): `approved` and `superseded` are
  written inside `_carry_to_the_artifact`'s existing `approval_decision()` block; no new
  site enters `approval_decision()`.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13): items 1, 4–8 and
  10 are each red first.
- **Shared files** (`RL-1263`, amended by `RL 9620`): two concurrent build slices may not
  both change the same existing function, class, spec section or policy table.
  `docs/INDEX.md` is a registry: regenerate, never hand-merge.
- **No spec text is written by this slice unless a ruling carries it verbatim** (Task 5).

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `02` | FR-191 | A Peril Structure is approvable in its own right: the decision moves it | `req("FR-191")` on items 1, 4, 5 |
| `02` | FR-190 | The reconciliation stays the approval's evidence; a non-approval returns to `reconciled`, keeping it | `req("FR-190")` on item 1's non-approval cases (existing parametrised test) |
| `06` | FR-351 | One uniform lifecycle; only decide + the carry move a structure to `approved` | existing marker on item 1; `req("FR-351")` on item 9's grep test if written as one |
| `06` | FR-355 | Non-approvals return the structure to its pre-submission state, `reconciled` | existing marker on item 1 |
| `06` | FR-363 | The Peril Structure evidence row's "per-peril model approvals" is enforced at approval (DP-1) | `req("FR-363")` on item 5 |
| `03` | FR-237 | A `peril_structure` pin resolves at compile | `req("FR-237")` on items 6, 7 |
| `00` | FR-20 | Maturity is the compile-time gate for a peril pin | `req("FR-20")` on item 6 |
| `03` | FR-255 | A `model_call` over a Peril Structure fails with a typed, reasoned error until A-3 | `req("FR-255")` on item 10 |

Out of scope, named so no reader assumes it: resolving and maturity-checking a structure's
**component models at compile**, and scoring a Peril Structure through
`assemble_risk_premium` (both A-3, SL 9596 / PL 9595, working ids); GLM scoring through
`model_call` (A-2, SL 9598 / PL 9597, FD 9605); the demo's severity model, structure and
pin (A-4); the double-count design point (the maintainer's item 4, ruled before A-4).

### Task 0 at planning time (read, not run)

Read at `137bc817` by this planner; no code was run and no database was queried.

| # | Fact | Where | Consequence |
|---|---|---|---|
| 0.1 | `perils.py` writes `DRAFT` (`:124`), `RECONCILED` (`:256`), `REVIEW` (`:338`), never `APPROVED` | `backend/src/app/platform/perils.py` | the carry is the first writer of `approved` |
| 0.2 | `_carry_to_the_artifact` (`api/approvals.py:529`) calls modelling, objectives, metrics, validation_rules, rating_versions and deployments; its docstring (`:536-538`) says a Peril Structure "gain[s] one with the slice that builds" it | `backend/src/app/api/approvals.py` | one call added; the docstring corrected |
| 0.3 | `_resolve_the_artifact` already calls `perils_service.resolve_artifact_ref` (`:489`), and `perils.resolve_artifact_ref` (`perils.py:431`) checks status since 2026-09-28 | same | submission needs no change |
| 0.4 | `_AFTER["peril_structure"] = dict.fromkeys(_OUTCOMES, "review")` (`:1049`); `_MOVE_ACTION` has no peril row (`:1056-1065`); the table-case fixture builds a structure with `perils=[]` (`:221-231`) | `backend/tests/test_api_approvals.py` | item 1's red; an empty structure passes DP-1 (a) vacuously |
| 0.5 | `peril_structures` is in `EXPECTED_GUARDED` | `backend/tests/test_approval_guard.py:28-38` | the trigger already refuses a write outside the decision path |
| 0.6 | `_Resolver.resolve` (`rating_versions.py:446`) has branches for `rating_algorithm`, `model` (`:464`), `rate_table`, `reference_table`, `custom_objective`, then `NOT_FOUND` "has no backend table yet (Phase 2)" (`:550-555`) | `backend/src/app/platform/rating_versions.py` | the branch goes before the final raise |
| 0.7 | `peril_structure` is not in `_MATURITY_CHECK_EXEMPT` (`compile.py:431`); `_APPROVED_OR_BETTER = {"approved", "live", "retired"}` (`:404`) | `packages/pricing-core/src/pricing_core/rating/compile.py` | item 6's refusal needs no `compile.py` edit; `superseded` is refused too, as for a Model |
| 0.8 | Models supersede earlier approved versions automatically on approval (`_supersede_earlier_versions`, `modelling.py:1393`) | `backend/src/app/platform/modelling.py` | DP-2's option (a) has a precedent |
| 0.9 | `_model_call_handler` (`runtime.py:512`) takes `step.peril_structure_ref` (`:535`) and reads `payload["fit_result"]` (`:540`) | `packages/pricing-core/src/pricing_core/rating/runtime.py` | DP-3; A-3 replaces it |

### Write set, and its contention (`RL-1263`, `RL 9620`)

"Edited" means an existing definition changes; "added" means a new definition in an
existing file.

| Path | Change |
|---|---|
| `backend/src/app/platform/perils.py` | added: `apply_approval_decision`, `_target_status`, `_supersede_earlier_versions` *(DP-2 a)*, `_require_approved_components` *(DP-1 a)*, `load_structure_by_ref` (the resolver's read) |
| `backend/src/app/api/approvals.py` | edited: `_carry_to_the_artifact` (`:529`): one `perils_service.apply_approval_decision` call inside the existing block; its docstring (`:536-538`) |
| `backend/src/app/platform/rating_versions.py` | edited: `_Resolver.resolve` (`:446`): one `peril_structure` branch before the final `NOT_FOUND`, and that raise's message (`:550-555`) |
| `packages/pricing-core/src/pricing_core/rating/runtime.py` | *(DP-3 b)* edited: `_model_call_handler` (`:512`): one early `_model_call_failure` for a `peril_structure_ref` step |
| `backend/tests/test_api_approvals.py` | edited: `_AFTER["peril_structure"]` (`:1049`), `_MOVE_ACTION` (`:1056`, one entry) |
| `backend/tests/test_rating_version_create_pins.py` (added by PL 9683's slice) | edited: its Acceptance 7 test, renamed and re-asserted (item 7) |
| `backend/tests/test_peril_structure_approval.py` | added (new module: items 4, 5, 6) |
| `packages/pricing-core/tests/test_rating_runtime.py` | *(DP-3 b)* appended: item 10's test |
| `docs/specs/06-governance.md` | *(DP-1 a, only as the ruling words it)* §4.2's floor note (`:405-408`) |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated |

**Not written:** `packages/pricing-core/src/pricing_core/rating/compile.py`,
`packages/model-schema/` (the status enum and the transition table already hold
`approved` and `superseded`), `backend/src/app/db/models.py` (no migration: the `CHECK` at
`models.py:1671` already admits both statuses), any `frontend/src` file.

**Contention.** Classes are `no_shared_files`' keys in
`docs/process/delivery-process.core.json`: `registry_exempt_append_only` (with its
`generated` list) is **exempt**; `forbidden` **SERIALISES**; `other_shared_path`
**SERIALISES unless a dispatch record names the path and its check**. **Snapshot: open
PRs at `137bc817`, 2026-10-05 between 16:52 and 17:20 BST; each plan's write set read from
its branch at the head named.** `PL-1371` §5 rule 4 (`:290-294`) serialises
`approvals.py` and `compile_bundle` outright for the pairs it names.

| Other slice (lane; Work; source read) | Shared path | Them | Us | Class → consequence |
|---|---|---|---|---|
| **PL 9649**, the FR-240 family fix (#1152 @`df8ba756`; WK-673) | `rating_versions.py` `_Resolver.resolve` | a `factor` branch; the `model` branch carries Factors | a `peril_structure` branch; the final raise's message | same method → **SERIALISE**: activation need 3 (this slice after it) |
| | `api/approvals.py` | read only (`apply_approval_decision` call site) | `_carry_to_the_artifact` | no shared write |
| **PL 9683**, the FD 9708 fix (#1140 @`f18549bb`; WK-1178) | `backend/tests/test_rating_version_create_pins.py` | adds the module and Acceptance 7 | edits Acceptance 7's test | **plan dependency** (activation need 2): this slice consumes its output, so they never overlap (`RL 9620` (b)) |
| | `rating_versions.py` | `create_rating_version` | `_Resolver.resolve` | different definitions; serial anyway by the dependency |
| **PL 9616**, the FD-1416 fix (#1168 @`0b60c81b`; WK-1178) | `api/approvals.py` | `_detail`, `submit_for_approval`, `decide_request`, `withdraw_request`, `list_requests` | `_carry_to_the_artifact` | `other_shared_path`, name-disjoint → ALLOWED one-sided **only** with the dispatch record naming the path and its check; **same Work**, so `RL 9620` (a) and (b) are written: (b) neither consumes the other's output |
| **WK-1250 S2**, PL 9610 (#1170 @`ca407ed9`; WK-1250) | `rating_versions.py` `_Resolver` | a `sub_graph` branch before the final `NOT_FOUND` | a `peril_structure` branch there; the raise's message | same method, adjacent hunks → **SERIALISE**; the second to merge re-reads the final raise (item 8) |
| **A-2**, PL 9597 (working id; WK-1178) | `rating_versions.py` `_Resolver.resolve` (`model` branch); `runtime.py` `_model_call_handler` | the GLM's Factors/Bandings/Groupings; the GLM branch | the peril branch; DP-3's early refusal | same methods → **SERIALISE**: A-1 then A-2 (the maintainer's item 1) |
| **A-3**, PL 9595 (working id; WK-1178) | `runtime.py` `_model_call_handler`; `test_rating_runtime.py` | replaces DP-3's branch and item 10's test | adds them | **plan dependency**: A-3 consumes this slice's output |
| **PL 9776**, F35 (#1051 @`ecbb82ab`; WK-1178) | `runtime.py` | `to_wire`, `_expression_node`, `_decision_table_node`, `_constraint_node`, `CompiledBundle`, `load_bundle` | `_model_call_handler` *(DP-3 b)* | `other_shared_path`, name-disjoint → ALLOWED one-sided with the dispatch record; same Work → `RL 9620` (a), (b) written |
| **PL 9688**, the FD 9707 fix (#1145 @`2f3269c8`; WK-673) | `runtime.py`; `test_rating_runtime.py` | `_decision_table_node`; edits `test_lookup_step_wire_translation_matches_by_key` | `_model_call_handler`; one appended test | name-disjoint → ALLOWED one-sided with the dispatch record |
| **PL 9609**, WK-1250 S3 (#1173 @`7c8736fd`) | `runtime.py` | `CompiledBundle`, `load_bundle` | `_model_call_handler` | name-disjoint → ALLOWED one-sided with the dispatch record |
| **PL 9713**, WK-675 S2 (#1131 @`c66300e5`) | `docs/specs/06-governance.md` | one mention, read | §4.2 note *(DP-1 a)* | the dispatch re-reads it; different sections expected |

Every other open plan (#1113 PL 9728, #1127 PL 9716, #1138 PL 9689, #1146 PL 9662, #1161
PL 9624, #1164 PL 9629, #1165 PL 9617) names none of this write set (each plan file read
from its branch at the snapshot above, grepped for every path in the table).

### Size

Small to medium: about one executor day (the sizing memo's A-1 row, 0.75 / 1 / 1.5). Five
tasks after Task 0, no migration, one full two-half gate run. The backend tests need
Postgres and MinIO (real compile Jobs); no NFR measurement, so the slice need not run
exclusive.

## Decision points

*Dated note, 2026-10-05 (pre-mint):* **all three are ruled**, each at its recommendation, by
the maintainer (by delegation) in the 17:02:50 BST entry quoted in §"The maintainer's
decisions this plan rests on, quoted". The Recommendation column is now the ruling. The text
below was written before the ruling and is kept as written.

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-1** | `06` FR-363's Peril Structure evidence is *"Per-peril model approvals; reconciliation result within tolerance"* (`06:118`), and §4.2's note calls the first half *"unqueryable"* (`06:405-408`). With an approval path built, is it enforced? | (a) at the carry: approving refuses `422 EVIDENCE_INCOMPLETE`, naming each component model (`frequency_model`, `severity_model`, `burning_cost_model`, `excess_model`) not `approved`, `live` or `retired`; the note gets a dated amendment; (b) not at approval; A-3's compile check is the only gate | **(a)**: approval and compile are different gates (`06`'s evidence; `03`'s FR-20 maturity). Under (b), between this slice and A-3 a structure over an unapproved model compiles, the hazard FD 9995 names. (a) follows SL-1409's `_require_executed_dry_run` (a check at the carry that rolls the decision back) | decision-maker | Task 3, item 5, Task 5 |
| **DP-2** | Approving `ps@n` while `ps@m` (m < n) is `approved` | (a) supersede every earlier approved version automatically, as `_supersede_earlier_versions` does for a Model; (b) leave both `approved` | **(a)**: the transition table mirrors the Model's "deliberately" (`model_schema/perils.py:108-110`), and two approved versions leave nothing to say which one a Rating Version means (`modelling.py:1397-1399`) | decision-maker | Task 3, item 4 |
| **DP-3** | Between this slice and A-3, an approved Peril Structure compiles into a `model_call`, and its score fails as a generic engine error (0.9) | (a) leave it: fail-closed, A-3 replaces it within the chain; (b) one early `_model_call_failure` naming the ref and A-3, red first (item 10); (c) refuse at compile | **(b)**: FR-255 types every scoring error; one branch in `_model_call_handler`, which A-3 rewrites anyway. (c) edits `compile_bundle`, which `PL-1371` §5 rule 4 serialises outright | decision-maker | Task 4, item 10 |

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm activation needs 1–4 on `origin/main`: FD 9995 minted (HIGH); PL
  9683's and PL 9649's slices merged; the ruling minted. Re-read every line cite in this
  plan at the dispatch tree, re-anchoring by symbol.
- [ ] **Step 2:** Re-derive the resolver's fall-through set: the `if ref.type == …`
  branches of `_Resolver.resolve` at the dispatch tree, and record them in the ledger
  (item 8's message names "`<type>`", not a list).
- [ ] **Step 3:** Re-read the write set of every slice in flight (open PRs and `eta.md`'s
  lanes) against §"Write set", and give the lead the `RL 9620` (a)/(b) lines for each
  same-Work pair.

### Task 1: The approval reds (items 1, 4, 5)

**Files:** Modify `backend/tests/test_api_approvals.py`; Create
`backend/tests/test_peril_structure_approval.py`.

- [ ] **Step 1:** Change `_AFTER["peril_structure"]` to `_moves("approved", "review",
  "reconciled")` and add `_MOVE_ACTION["peril_structure"]`. Run
  `uv run pytest backend/tests/test_api_approvals.py -k "fr_355 and peril_structure" -q`.
  **Expected red: `approve`, `reject` and `request_changes`**, each on the status
  assertion (`'review' == …`). `first_of_two` expects `review` and stays green.
- [ ] **Step 2:** In the new module, build structures through the service
  (`perils.create_structure`, `record_reconciliation`, `submit_for_review`), not by inserting
  rows, so the request is real. Component models come from the `_fitted_gbm` neighbour the
  backend tests already use, approved with `approved_rows.mark_approved` (a test-only write
  under the guard, `backend/tests/approved_rows.py`). Write item 4's and item 5's tests.
  Expected red: `ps@2` stays `review`; decide returns `200`.
- [ ] **Step 3:** Commit (red): `test: FD 9995 — a peril structure decision moves nothing (FR-191, FR-355)`.

### Task 2: The compile reds (items 6, 7)

**Files:** Modify `backend/tests/test_peril_structure_approval.py`,
`backend/tests/test_rating_version_create_pins.py`.

- [ ] **Step 1:** Item 6's test: create the structure, pin it through
  `POST /api/v1/rating-versions` (PL 9683's route), compile with `_run_compile_job`
  (`backend/tests/test_rating_version_compile.py`). Expected red: `NOT_FOUND`, "has no
  backend table yet", for every status.
- [ ] **Step 2:** Item 7: rename and re-assert PL 9683's Acceptance 7 test. Expected red on
  the absent-phrase assertion.
- [ ] **Step 3:** Commit (red): `test: FD 9995 — a peril pin cannot be resolved at compile (FR-237, FR-20)`.

### Task 3: The carry (items 1–5, 9)

**Files:** Modify `backend/src/app/platform/perils.py`, `backend/src/app/api/approvals.py`.

- [ ] **Step 1:** `perils.apply_approval_decision(session, *, workspace_id, actor, request)
  -> PerilStructureRow | None`, the shape of `objectives.apply_approval_decision`
  (`objectives.py:795-862`): `None` for another type or a missing row (FR-386's tolerance,
  as there); `_target_status` maps `approved → APPROVED`, `rejected` and
  `changes_requested → RECONCILED`, anything else `None`; the move is checked against
  `VALID_PERIL_STRUCTURE_TRANSITIONS`; one audit event per move.
- [ ] **Step 2:** *(DP-1 a)* `_require_approved_components(session, *, workspace_id, row)`
  before the move to `APPROVED`: for each peril in `to_structure(row).perils`, each set
  component ref must load a Model whose status is `approved`, `live` or `retired`.
  `_model_refs` (`perils.py:577`) lists `frequency_model`, `severity_model` and
  `burning_cost_model` only; the large-loss `excess_model`
  (`model_schema/perils.py:161`, on the peril's `large_loss`, `:229`) is read beside it,
  and a test case covers it; otherwise `PlatformError(
  "EVIDENCE_INCOMPLETE", …, 422, <the refs>)`. The raise rolls the decision back with the
  carry.
- [ ] **Step 3:** *(DP-2 a)* `_supersede_earlier_versions`, the shape of the Model's
  (`modelling.py:1393`), on the move to `APPROVED`.
- [ ] **Step 4:** In `_carry_to_the_artifact`, add `await
  perils_service.apply_approval_decision(...)` inside the `approval_decision()` block, after
  `metrics_service`, and correct the docstring's "a Peril Structure … gain one" sentence.
- [ ] **Step 5:** Run Task 1's tests; green. Run `backend/tests/test_approval_guard.py` and
  `test_approval_guard_trigger.py`; green unchanged. Commit:
  `fix: a peril structure is approved through the approval workflow (FD 9995; FR-191, FR-355, FR-363)`.

### Task 4: The resolver branch and the interim refusal (items 6–8, 10)

**Files:** Modify `backend/src/app/platform/perils.py`,
`backend/src/app/platform/rating_versions.py`; *(DP-3 b)*
`packages/pricing-core/src/pricing_core/rating/runtime.py`,
`packages/pricing-core/tests/test_rating_runtime.py`.

- [ ] **Step 1:** `perils.load_structure_by_ref(session, *, workspace_id, slug, version)`;
  in `_Resolver.resolve`, before the final raise:

  ```python
  if ref.type == "peril_structure":
      structure_row = await perils_service.load_structure_by_ref(
          session, workspace_id=workspace_id, slug=ref.slug, version=ref.version
      )
      if structure_row is None:
          raise PlatformError("NOT_FOUND", "Peril Structure not found", 404, f"{ref}")
      return ResolvedArtifact(
          status=structure_row.status,
          payload=perils_service.to_structure(structure_row).model_dump(mode="json"),
      )
  ```

  and change the final raise's detail to name the missing branch for `ref.type`.
- [ ] **Step 2:** Run Task 2's tests; green. Commit:
  `fix: compile resolves a peril structure pin and maturity-checks it (FD 9995; FR-237, FR-20)`.
  This is the commit that flips PL 9683's Acceptance 7 (item 7), as its docstring says.
- [ ] **Step 3:** *(DP-3 b)* Item 10's test, red first (`KeyError: 'fit_result'`), then in
  `_model_call_handler`, before `payload["fit_result"]`:
  `if step.peril_structure_ref is not None: return _model_call_failure(step, …)` naming the
  ref and "scoring a Peril Structure is slice A-3 (PL 9595, working id)". Green. Commit:
  `fix: a peril structure model_call fails with a named reason until A-3 (FR-255)`.

### Task 5: The spec text, verbatim from the ruling (DP-1 a only)

- [ ] **Step 1:** If the ruling carries a dated amendment to `06` §4.2's note (`:405-408`),
  apply it verbatim under `spec-change`, run `python3 scripts/audit-docs.py`, and commit.
  If the ruling carries none, this task is empty and the ledger says so.
  *Dated note, 2026-10-05 (pre-mint): the 17:02:50 BST acceptance carries no text for the
  note, though DP-1 (a)'s option says "the note gets a dated amendment". As written, this
  task is empty, and `06` §4.2 keeps calling the per-peril half "unqueryable" (`06:407` at
  `137bc817`) after this slice enforces it. Reported to the lead for a worded text before
  activation; this planner writes none.*

### Task 6: The gate and the ledger (items 11, 12)

- [ ] **Step 1:** The full two-half gate through the gate-runner, holding the one gate slot.
  Record each rc and the tree.
- [ ] **Step 2:** In the slice's `LG-` ledger: every red with its printed line, Task 0
  Step 2's fall-through set, and `git diff --stat origin/main...HEAD` against
  §"Write set".

## Hand-off

1. The lead mints PL 9599 and SL 9600 at the merge turn and dispatches only after
   §"Activation needs" hold, in a separate activation PR.
2. When this slice merges, FD 9995's event is discharged (its §"Disposition": the approval
   path and the resolver branch land together, and the tripwire is replaced by the positive
   test, item 6); the auditor closes it.
3. A-2 (PL 9597, working id) runs next in the chain; A-3 (PL 9595, working id) replaces
   DP-3's interim branch and item 10's test.
4. PL 9683's Acceptance 7 is rewritten here, as that plan's DP-5 (a) provides. Its plan file
   is not edited.

## Self-review

1. **Coverage of FD 9995's Disposition, clause by clause.** "a peril approval path": Task 3,
   items 1–5. "the resolver branch": Task 4 Step 1, item 6. "land together": one slice. "the
   tripwire is replaced by a positive test that an unapproved peril is refused at compile":
   item 6 (the positive test) and item 7 (the tripwire flipped). The stale message
   (FD 9995 fact 2): item 8. "No backend writer of `approved`": item 9.
2. **Coverage of the maintainer's A-1 line** ("the peril approval carry plus the _Resolver
   peril branch; it flips PL 9683's Acceptance 7"): Task 3, Task 4, item 7.
3. **Every open design choice is a DP with an owner** (DP-1 to DP-3). No spec text is
   written without a ruling (Task 5). *(Dated note, 2026-10-05: all three ruled at the
   recommendation, 17:02:50 BST entry.)*
4. **Repository literals read at `137bc817`:** every line in §"Task 0 at planning time" and
   §"Write set"; `_AFTER` and `_MOVE_ACTION` (`test_api_approvals.py:1044-1065`);
   `EXPECTED_GUARDED` (`test_approval_guard.py:28-38`); `objectives.apply_approval_decision`
   (`objectives.py:795-862`); `_supersede_earlier_versions` (`modelling.py:1393`).
   PL 9683's Acceptance 7 test was read on its branch at `f18549bb`.
5. **What was not executed.** No test or code was run. The code samples are sketches against
   names read at `137bc817`; a sample that does not run as written is a plan defect to report,
   not to work around.
