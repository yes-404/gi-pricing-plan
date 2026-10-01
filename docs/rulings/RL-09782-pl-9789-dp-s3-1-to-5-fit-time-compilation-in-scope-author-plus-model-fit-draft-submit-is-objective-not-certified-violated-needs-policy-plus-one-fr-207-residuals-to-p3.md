---
id: RL-9782
family: ruling
title: PL 9789 DP-S3-1 to DP-S3-5 decided — fit-time compilation in scope, author plus model:fit, a draft submit is OBJECTIVE_NOT_CERTIFIED, violated needs policy plus one, FR-207's residuals to P3
status: draft                  # active → superseded | retired (§1.2a) — draft until the lead mints
created: 2026-10-01
owner: decision-maker
tree: 101e32dc5baf8edeb986063b680ccec31e5ba724
phase: P2
work: WK-690
slice: SL-1273
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1268, RL-1265, RL-1305, RL-1263, FD-1349, FR-144, FR-146, FR-150, FR-152, FR-163, FR-207, FR-366, FR-367, FR-449]
---

# RL 9782 (working id) — PL 9789 DP-S3-1 to DP-S3-5 decided

## How this was ruled

Ruled at effort `medium` by the decision-maker session `dm-9789dp`, on the maintainer's
order of 2026-10-01 ("NOW … medium DM passes for … PL 9789 DP-S3-1..5 (if Kind is
decision-maker)"). Started 2026-10-01 07:58 BST; evidence read at `origin/main`
`101e32dc5baf8edeb986063b680ccec31e5ba724`. The plan is PL 9789 (working id) on draft PR
#1037, branch `wk690-s3-leaf-plan`, head `2323b5447a420e2344c3c6339507795f980b33cb`, file
`docs/plans/PL-09789-wk-690-slice-3-the-expression-kind-through-the-platform-behind-the-flag-leaf-plan.md`
(cited below as `PL 9789:<line>` at that head). The plan is frozen by family and is not
edited; every delta is stated here for the dispatch record to carry.

**Kind check.** PL 9789's decision-point table (`PL 9789:330-337`) gives DP-S3-1 to DP-S3-5
the kind *decision point* and the resolver "decision-maker, its own `RL-` (pending)". All
five are ruled here. **DP-S3-6** is kind *scope*, resolver the lead (`PL 9789:337`), and is
not ruled here. DP-3 of `PL-1268` is `RL-1265`'s and is not reopened.

**The parity ruling this depends on.** The lead's brief first said a concurrent session was
ruling the WK-1178 permission-parity check as RL 9856. The lead corrected that at
2026-10-01, in a message this session received by 08:04 BST, and the repository agrees: working id 9856 was minted on
2026-09-30 as `RL-1305` (`status: active`, by #989, `e9263283`), its `06` §4.1 amendment is
applied on main, and PR #942 is `CLOSED`. DP-S3-2 is ruled against `RL-1305` as decided and
is **not conditional**. What remains unbuilt is the WK-1178 parity-check **slice**
(`PL-1279`), and that is a sequencing dependency of Task 3, stated under DP-S3-2.

## Premises re-verified at `101e32dc`

`git diff --stat 9b0fb97c 101e32dc -- backend/src packages docs/specs/02-modelling.md
docs/specs/06-governance.md docs/specs/07-platform.md backend/tests/test_custom_objectives.py`
prints nothing, so the plan's premises (a)–(u) were measured on the same content these
rulings read. Each premise a ruling depends on was opened again:

| # | Premise | At `101e32dc` | Used by |
|---|---|---|---|
| b | create and derive both take `FitModels` | `backend/src/app/api/custom_objectives.py:76` (`FitModels = … requires(Perm.MODEL_FIT)`), create `:235-238`, derive `:296-299`; certify `:320-323` also `FitModels` | DP-S3-2 |
| — | a service-layer check exists and counts | `backend/src/app/platform/rbac.py:274` `require_permission(session, *, workspace_id, principal, permission, …)`; `RL-1305` "Ruled" D1 item 3: "A service-layer check counts" | DP-S3-2 |
| n | submission's stand-in | `submit_for_review` is at `backend/src/app/platform/objectives.py:558` (the plan says `:556`; the function is at `:558` at both `9b0fb97c` and `101e32dc`, so this is a two-line citation slip, not drift). The `VALIDATION_FAILED` 409 is the transition check that follows the `model:submit` check | DP-S3-3 |
| — | a failed certificate leaves the objective `draft` | `record_certificate`, same file: `row.status = (ObjectiveStatus.DRAFT if failed else ObjectiveStatus.CERTIFIED).value` | DP-S3-3 |
| — | the problem shape forbids extensions | `packages/model-schema/src/model_schema/problem.py`: `ProblemDetail` and `FieldError` both `ConfigDict(frozen=True, extra="forbid")`; `FieldError` is `field`, `code`, `message` | DP-S3-3 |
| m | no two-approver rule | `backend/src/app/platform/approvals.py:225` `submit`; `:286` `approvers_required=entry.approvers_required`, from the policy only | DP-S3-4 |
| — | **a template already certifies `violated`** | `packages/pricing-core/src/pricing_core/modelling/objectives.py:408-412` (`_quantile_hess`): "this template certifies `convexity: violated` and needs a declared strategy and a second Approver"; `_convexity_check` `:1278-1300` emits `CheckStatus.VIOLATED` for any template. **`PL-1268`'s requirement table says the two-approver rule "is first reachable by an `expression` objective". That is false at this tree:** the quantile template reaches it, and nothing enforces the second Approver for it today | DP-S3-4 |
| — | the fit's status gate | `compile_objective` `packages/pricing-core/src/pricing_core/modelling/objectives.py:730-744` refuses a non-template with `OBJECTIVE_KIND_NOT_ENABLED`; the status gate is separate, `pricing_core/modelling/gbm.py:532-538`, over `FITTABLE_OBJECTIVE_STATUSES` = {`certified`, `review`, `approved`} (`model_schema/objectives.py:177-179`) | DP-S3-1 |
| h | Slice 2's compiler | `compile_expression_objective` `pricing_core/modelling/expression_objective.py:292-302`, keyword-only, `derived: Derived \| None = None` ("derived here from `loss`" when absent), `inverse_link: Literal["exp", "logistic"] = "exp"` | DP-S3-1 |
| p | FR-207's residuals | `02` FR-207 (`docs/specs/02-modelling.md:370`), its 2026-08-25 amendment: "The `Model` field records what the `GlmSpec` field declares", owner WK-690 | DP-S3-5 |

## Ruled

Each decision states its rationale and the red step that must fail at the base first;
the Acceptance section below collects the red steps.

### DP-S3-1 — fit-time compilation of an `expression` objective: **(a), in scope**

**Ruled (a)**, with two clauses the plan's text leaves open.

- `compile_objective` dispatches `kind: expression` to `compile_expression_objective`. **It
  passes the artifact's stored `derived` block and never derives at fit time.** FR-144 says
  the gradient and hessian are derived "at authoring time … stored … reviewed as part of
  approval, and compiled … at fit time". What the Approver read is the stored text, so the
  fit compiles that text. `compile_expression_objective`'s `derived=None` path, which
  re-derives from `loss`, is never taken from `compile_objective`. An expression artifact
  with `derived` null that reaches it is refused by name. This is unreachable through the
  lifecycle (DP-S3-3 refuses certify before derivation), and is defence for a hand-built
  artifact.
- **The status gate is unchanged and kind-agnostic.** The plan's question and Acceptance
  say "an approved `expression` objective". The fit gate is `FITTABLE_OBJECTIVE_STATUSES`
  (`certified`, `review`, `approved`), and this slice adds no kind-specific narrowing:
  that would be a new rule with no FR behind it. The acceptance test uses an `approved`
  objective, as planned, and one `certified` case pins the parity with templates.
- `inverse_link` is set by the same function that certification uses to read the link
  (PL 9789 Risk 5), so certify and fit cannot disagree. A link other than log or logit is
  refused by name at both.

**Why.** FR-144 is in WK-690's core scope (`PL-1268` Scope table, row FR-144, slices 1, 2, 3),
and `PL-1268` Slice 3 registers `OBJECTIVE_NONFINITE_DERIVATIVE` "where the fit job
surfaces it", which presumes a fit. Slices 4 and 5 fit nothing, so under (b) FR-144's
"compiled at fit time" has no owner in the Work. (c), the GLM arm, is DP-S3-5's question.

**Red first.** `-k compile_dispatch` fails at the base with `OBJECTIVE_KIND_NOT_ENABLED`
raised by `compile_objective` (`objectives.py:740`). A second test fails if the stored
`derived` text is ignored: an artifact whose stored hessian differs from the one SymPy
would re-derive (`hessian_strategy` held fixed) must fit with the stored one, asserted on
the kernel's output at a seeded grid. A test that fails for any other reason is not the
red step.

### DP-S3-2 — how `custom_objective:author` is checked: **(b), author in addition to `model:fit`, on create and derive**

**Ruled (b).** Create keeps its `model:fit` route dependency and, for `kind: expression`,
calls `rbac.require_permission(…, permission=Permission.CUSTOM_OBJECTIVE_AUTHOR)` in the
handler before the flag is resolved. **Derive keeps `model:fit` and gains
`requires(Permission.CUSTOM_OBJECTIVE_AUTHOR)` as a second route dependency.** Template
create, certify (`FitModels`) and submit (`SubmitModels`) are unchanged. Versioning is a
create with an existing slug (`02` §5.1 note: `POST /custom-objectives` "allocates a
version"); no route is added.

**Why not the plan's (a).** (a) gives create the conjunction (`model:fit` and author) and
derive the author permission alone. The same principal can then derive an objective they
could not have created, which is two rules for one act. FR-366's own text settles which
rule is right: what FR-367 adds is "an *additional* control, never the only one", and its
first half, "`model:fit` governs Custom Objectives", is not withdrawn. So the author
permission is added to `model:fit`, never substituted for it. (b) also leaves
`test_deriving_without_model_fit_is_refused` (`backend/tests/test_custom_objectives.py:617`)
true and unchanged. (c) adds a route `02` §5.1 does not declare.

**Order.** Both permission checks run before the flag is read, so a caller without the
permission gets 403 whatever the flag, and learns nothing about it. On create, FastAPI's
body validation (422) still runs first, because the kind is in the body.

**Against `RL-1305`.** Under `RL-1305` D1 items 2 and 3, derive's
`requires(Permission.CUSTOM_OBJECTIVE_AUTHOR)` is a check site (a route dependency read off
the flattened routes) and create's `require_permission(…, permission=…)` call is one too
(the AST walk). Under its `STALE_OWNER` class (D1 item 4), the §4.1 Built row Task 3 writes
has an **empty** `Check owner` cell, because the checks land in the same commit. Task 3
writes the row in the shape `RL-1305` D4 applied to `06` §4.1 on main. This ruling decides
only where the checks sit; it does not touch the parity check or the table's shape.

**Sequencing dependency, not an open ruling.** Task 3's first red step runs the WK-1178
parity module, which `PL-1279` builds and which is not on main at `101e32dc`. Task 3 cannot
start until that slice has merged (PL 9789 activation need 3, Risk 1). If the merged
module does not recognise create's handler-level call, that is a defect in the module
against `RL-1305` D1 item 3, reported to the lead as a finding. It is not a reason to move
the check to a route of its own.

**Red first.** Two 403 tests for a caller with `model:fit` and without author, on create
(`kind: expression`) and derive. Both fail at the base **on `["code"]`**, receiving 409
`OBJECTIVE_KIND_NOT_ENABLED` where 403 is expected (PL 9789 Task 3). A third: a caller with
author and without `model:fit` gets 403 on both routes. On create, this passes at the base
by the existing route dependency and stays as the control. A regression test that template
create with `model:fit` alone is 201. And a test that no set in `BUILTIN_ROLES` contains the
member (FR-367 "not granted by any built-in role").

### DP-S3-3 — the new refusals: **(a) amended — grammar 422 with the position in `errors[]`, an underived certify is `VALIDATION_FAILED` 409, and a `draft` submit is `OBJECTIVE_NOT_CERTIFIED` 409 for both kinds**

**Ruled.** Three refusals:

1. **`OBJECTIVE_GRAMMAR_VIOLATION`, 422, with the position in one `FieldError`**:
   `field: "loss"`, `code: "OBJECTIVE_GRAMMAR_VIOLATION"`, and a `message` that begins
   `line <L>, column <C>:` from `ExpressionError.lineno` and `col_offset` (1-based column).
   **The plan's `position: {line, column}` problem extension is refused.** `ProblemDetail`
   is `extra="forbid"`, so an extension is a change to the platform-wide problem shape,
   its contract and every generated client, for one code. WF-702 B1.5 and the
   failure-modes row ask for a "position-accurate error", and the `errors[]` member that
   FR-403 put on the problem for this purpose gives one. If Slice 5's authoring view needs
   a structured line and column, its leaf plan raises that as a `07` problem-shape change.
2. **Certify of an `expression` objective whose `derived` is null: 409 `VALIDATION_FAILED`**,
   at the route, before a job is enqueued, with a `detail` naming
   `POST /api/v1/custom-objectives/{id}/derive`. **Not `OBJECTIVE_NOT_CERTIFIED`** as the
   plan recommends: the missing precondition is derivation, not certification, and a code
   that names the wrong missing step misleads the client that reads it. It is the module's
   existing lifecycle-precondition code, the one Task 4's `/derive` uses for a non-`draft`
   objective. A client already knows the state, because `derived: null` is on the
   `CustomObjective` it holds, so no new code is needed. (c), deriving first, is refused
   for the plan's reason (WF-702 B2.4).
3. **Submission of a `draft` objective: 409 `OBJECTIVE_NOT_CERTIFIED`, for both kinds**,
   replacing the `VALIDATION_FAILED` stand-in that `02` §5.1's note names
   (`02-modelling.md:2140-2142`). **The predicate is the status, `draft`**, because
   `record_certificate` sets `draft` on a failed certificate and `certified` on a passing
   one: `draft` is exactly "no passing certificate for this version". Every other invalid
   transition (`review`, `approved`, `deprecated` to `review`) keeps 409
   `VALIDATION_FAILED`. The status code does not change; only the code does, for templates
   too, and the slice's release note states it. (b) is refused for the plan's reason: two
   codes for one condition.

**Spec change, applied by the executor at Tasks 4, 5 and 7** (PL 9789's write set, `02`).
Remove the "(declared, Phase 2)" marker from `OBJECTIVE_GRAMMAR_VIOLATION` and
`OBJECTIVE_NOT_CERTIFIED` in the commit that registers each. Strike the stand-in sentence
"`submit_for_review` stands in with `VALIDATION_FAILED` today." with a dated note citing
this ruling and stating the `draft` predicate. Add a dated note to the §5.1 certify row:
an underived `expression` objective is refused with `VALIDATION_FAILED` naming `/derive`.

**Red first.** (1) The grammar test fails at the base with 409 `OBJECTIVE_KIND_NOT_ENABLED`
under the flag on; at green it asserts the status, `["code"]`, and
`["errors"][0]["field"] == "loss"` with the line and column in its message. (2) The
underived-certify test asserts 409, `VALIDATION_FAILED`, `/derive` in `detail`, and that no
job row was written. (3) `test_submission_without_a_certificate_is_refused` (`:429`), quoted
before and after, fails on `["code"]` (`VALIDATION_FAILED` where `OBJECTIVE_NOT_CERTIFIED`
is expected). A control test submits an `approved` objective and still gets
`VALIDATION_FAILED`, so the new code cannot be raised for every invalid transition.

### DP-S3-4 — the additional Approver: **(a), policy plus one, both kinds**

**Ruled (a), for both kinds.** When the version's latest certificate has a `convexity`
check with status `violated`, `submit_for_review` passes an increment of one to
`approvals.submit`. `approvals.submit` stores `approvers_required = policy + 1` on the
request row and records it in the submission's audit `after` (`approvals.py:309`). The
new keyword defaults to 0, so no other artifact type changes.

**Why.** FR-152's word is "an *additional* Approver": the requirement is relative to the
policy. FR-163's "two Approvers" is the same rule read at the default policy of one, and
it cites FR-152. `max(policy, 2)`, option (b), adds nobody when the policy is already two,
which breaks FR-152. **Both kinds, not `expression` only:** FR-152 is kind-agnostic, and the
re-verification above shows the quantile template **already** certifies `violated` and its
own code comment says it "needs … a second Approver". Today nothing enforces that. So
under (c) a live gap in template governance stays open. This is not a new burden on
templates: it enforces a rule that applies to them now.

**Spec change, applied by the executor at Task 7.** FR-163 gets a dated note: the
"`expression` objectives with `convexity: violated` need two Approvers" clause reads "any
objective whose certificate has `convexity: violated` needs the policy's Approvers plus one
(FR-152); at the default policy that is two". FR-152 needs no change.

**Red first.** At the base, count the template fixtures and seeded objectives whose
certificate is `violated` (PL 9789 Task 7) and record the count with its command. A
`violated` objective of each kind, under a policy of one: one non-author approval leaves
it in `review` (fails at the base, because it moves to `approved`), and a second approval
approves it. Under a policy of two, two approvals leave it in `review`. A `pass` objective
under a policy of one is approved by one approval (the control).

### DP-S3-5 — FR-207's two `custom_objective_ref` residuals: **(a), both re-noted to Phase 3, spec change first — the destination subject to the maintainer's line**

**Ruled (a) on the technical question.** The GLM arm's custom objective **is a separate
capability**. A `glum` fit is a GLM: a family and a link fitted by IRLS. A per-observation
loss `L(y, f, w)` in §4.6's grammar has no family, and `02` specifies no path from one to a
`glum` fit. So `GlmSpec.custom_objective_ref` cannot be made live in this slice without a
new, unspecified capability. Option (c) is refused for that reason. **`Model.custom_objective_ref`
cannot go live without it.** FR-207's 2026-08-25 amendment says the `Model` field "records
what the `GlmSpec` field declares", and a GBM names its objective through `spec.objective.ref`,
which R4 is enforced off. Option (b) would make the `Model` field a second record of the
GBM's ref: a second, lossy source of truth, the defect FR-207 struck
`transparency_artifact_id` for on 2026-08-22. The pair moves together, as FR-207's
amendment already says it must.

**The destination is a scope move, and the record says so.** Moving an owned id out of
WK-690 into Phase 3 is a scope consequence (`document-ids.md` §1.7: a *scope* question goes
to the maintainer). `PL-1268` Slice 3 already allows "re-noted" and asks for this decision
point if the GLM arm is a separate capability, and `RL-1265` DP-1 and DP-2 set the pattern
for moving WK-690 items to Phase 3. **Task 8 therefore applies only after a dated line
accepts the Phase 3 destination: the maintainer's, or the lead's under delegation.** The
deferral is in that pattern: Phase 3, spec change first, owner the maintainer, event the P2
phase closure record, which lists both for P3's first plan.

**Spec change, applied by the executor at Task 8.** FR-207 gets a dated amendment: both
`custom_objective_ref` residuals move from WK-690 to Phase 3 as above, citing this ruling.
The same commit corrects the owner clause wherever FR-207's 2026-08-25 sweep list found it
quoted: `model_schema/objectives.py` (around `:108`), `frontend/src/components/ObjectivePicker.vue`,
the `DECLARED_AND_UNBUILT` notes in `backend/tests/test_contracts.py` (`model` and
`model-spec`), and the staging descriptions on `model.custom_objective_ref` and
`model-spec`'s `GlmSpec` branch. Before writing, the executor greps for every quotation:
`git grep -n "custom_objective_ref" -- docs/specs docs/contracts packages backend frontend/src`.

**Red first.** No behaviour changes, so the red step is the drift check. Before Task 8,
`git grep -n -E "custom_objective_ref.*WK-690|WK-690.*custom_objective_ref" -- packages backend frontend/src docs/contracts docs/specs`
lists every quotation of the old owner. After Task 8 it prints only FR-207's own dated
history. `generate-contracts.py --check` passes. The contract keeps both properties with
their notes; neither is dropped.

## What it obliges

| Ruling | Applied at | Delta from PL 9789's recommendation |
|---|---|---|
| DP-S3-1 (a) | Task 6 | Compiles the stored `derived`, never re-derives. The status gate is unchanged (`certified`, `review`, `approved`). The link is read by the certify function |
| DP-S3-2 (b) | Task 3 | Derive keeps `model:fit` and adds author, where the plan dropped `model:fit`. `:617` is unchanged. Task 3 waits for `PL-1279`'s parity slice to merge |
| DP-S3-3 (a) amended | Tasks 4, 5, 7 | The position goes in `errors[0]`, not a problem extension. An underived certify is `VALIDATION_FAILED`, not `OBJECTIVE_NOT_CERTIFIED`. A submit is `OBJECTIVE_NOT_CERTIFIED` only from `draft` |
| DP-S3-4 (a), both kinds | Task 7 | None. The quantile template is a live instance today, which corrects `PL-1268`'s "first reachable by an `expression` objective" |
| DP-S3-5 (a) | Task 8 | Task 8 waits for a dated line accepting the Phase 3 destination |

The dispatch record carries these deltas against the frozen plan. PL 9789's Acceptance
items 6, 8 and 9 are read through them.

## Acceptance — the violation that must become detectable

Each line is a violation this ruling makes detectable, and the test that must fail first
on the base (`PL 9789` Acceptance items 6, 8 and 9, read through the deltas above).

1. **DP-S3-1.** A fit with an `expression` objective re-derives instead of compiling the
   stored, reviewed `derived` text: the stored-hessian test fails. `compile_objective`
   still refuses the kind: `-k compile_dispatch` fails with `OBJECTIVE_KIND_NOT_ENABLED`.
2. **DP-S3-2.** A caller with `model:fit` and without `custom_objective:author` creates
   (`kind: expression`) or derives: the two 403 tests fail on `["code"]` (409
   `OBJECTIVE_KIND_NOT_ENABLED` at the base). A caller with author and without `model:fit`
   derives: `test_deriving_without_model_fit_is_refused` fails. A built-in role grants the
   member: the `BUILTIN_ROLES` test fails.
3. **DP-S3-3.** A grammar error without its position: the `errors[0]` assertion fails. An
   underived expression enqueues a certify job: the no-job-row assertion fails. A `draft`
   submit answers `VALIDATION_FAILED`: the rewritten `:429` test fails on `["code"]`. An
   `approved` re-submit answers `OBJECTIVE_NOT_CERTIFIED`: the control fails.
4. **DP-S3-4.** A `violated` objective of either kind approved by the policy's count
   alone: the one-approval-stays-in-`review` test fails, at policy one and at policy two.
5. **DP-S3-5.** A quotation of WK-690 as the residuals' owner survives Task 8: the
   `git grep` above prints it.
