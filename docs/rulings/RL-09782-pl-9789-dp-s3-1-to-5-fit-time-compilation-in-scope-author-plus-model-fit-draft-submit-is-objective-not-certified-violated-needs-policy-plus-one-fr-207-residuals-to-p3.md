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
#1037, branch `wk690-s3-leaf-plan`, head `2323b5447a420e2344c3c6339507795f980b33cb`
(cited below as `PL 9789:<line>` at that head). *(Text-fix pass, audit F4: the plan's file
path is not cited, because the file is not on main and check 32 cannot resolve it.)* The plan is frozen by family and is not
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

**DP-S3-4's §4.2 interaction** was ruled by the decision-maker session `dm-9782hi` at effort
`high`, on the maintainer's raise to the lead of 2026-10-01 08:14:25 BST; evidence re-read at
`101e32dc`, first clock read 08:24 BST.

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
could not have created, which is two rules for one act. **FR-367 is silent on the
conjunction:** it names the permission an `expression` objective needs, and says nothing
about whether `model:fit` is still needed with it. The ruling decides it on same-act
consistency: create and derive are one act, so a principal must not derive what they
cannot create. Create keeps `model:fit` (its route dependency is not in question), so
derive keeps it too, and the author permission is added to `model:fit`, never substituted
for it. **This reading is the ruling's, not the text's.** *(Corrected at the text-fix pass,
audit F2: this paragraph rested (b) on FR-366's "an *additional* control, never the only
one". That word is relative to FR-353's submitter-cannot-approve and `02` FR-163's
non-author Approver, the controls that stood in for a distinct permission. It is not
relative to `model:fit`, so it does not settle the conjunction.)* (b) also leaves
`test_deriving_without_model_fit_is_refused` (`backend/tests/test_custom_objectives.py:617`)
true and unchanged. (c) adds a route `02` §5.1 does not declare.

**Spec change, applied by the executor at Task 3.** *(New at the text-fix pass, audit F2.)*
FR-367 gets a one-line dated clarification: `custom_objective:author` is required in
addition to `model:fit`, never instead of it, on create and on derive, citing this ruling. The exact text and its placement are **S1** under *Spec changes — the exact texts*.

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
author and without `model:fit` gets 403 on both routes. This is a **new** test on create
and on derive. It passes at the base on both, because both routes carry `model:fit` as a
route dependency, and it stays as the control that guards the conjunction.
`test_deriving_without_model_fit_is_refused` (`:617`) grants only the auditor role, so it
cannot see this caller; it stays unchanged. *(Corrected at the text-fix pass, audit F3.)* A regression test that template
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
The exact texts and their placements are **S2** (Tasks 4 and 7), **S3** (Task 5) and **S4**
(Task 7) under *Spec changes — the exact texts*.

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
(FR-152); at the default policy that is two". FR-152 needs no change. The exact text and its
placement are **S5** under *Spec changes — the exact texts*.

**Red first.** At the base, count the template fixtures and seeded objectives whose
certificate is `violated` (PL 9789 Task 7) and record the count with its command. A
`violated` objective of each kind, under a policy of one: one non-author approval leaves
it in `review` (fails at the base, because it moves to `approved`), and a second approval
approves it. Under a policy of two, two approvals leave it in `review`. A `pass` objective
under a policy of one is approved by one approval (the control).

**§4.2 interaction ruled 2026-10-01 08:24 BST, by `dm-9782hi` at effort high: policy plus one is
a platform rule, not a policy key. §4.2's `escalation` key is struck and replaced by a stated
rule.** *(Raised by the text-fix pass, audit F1; escalated by the lead the same day.)* `06`
§4.2's default `ApprovalPolicy` gave `custom_objective` an absolute escalation:
`"escalation": {"when": "certificate.convexity == 'violated'", "approvers_required": 2}`
(`docs/specs/06-governance.md:349-351` at `101e32dc`). It is not combined with this ruling's
count: it is removed. The request's count is the matching entry's `approvers_required` plus one,
for both kinds, and no policy sets the increment. The §4.2 default instance is `1 + 1 = 2`, so the defaults' outcome
does not change.

*Premises, re-verified at `101e32dc`.* `ApprovalPolicyEntry` is `extra="forbid"` and has no
`escalation` field, and `approvers_required` is `Field(ge=1, le=5)`
(`packages/model-schema/src/model_schema/approvals.py:114`, `:117`). `ApprovalRequest.approvers_required`
is `Field(ge=1)` with no upper bound (`:288`), and the table's only check is
`approvers_required >= 1` (`backend/src/app/db/models.py:687`). So policy 5 plus one stores 6
and no bound clips it. `git grep -n -i escalation origin/main -- backend packages frontend/src docs/contracts`
prints no approval escalation. The hits are FR-348's role escalation (`rbac.py`, `test_rbac.py`),
the contract-drift guard's own use of the word (`test_contracts.py:1766`, `:1904`), and one
docstring that names policy escalation as `06`'s (`backend/src/app/api/validation.py:370`, copied
into `docs/contracts/openapi/generated.json`). `FD-1281` measured the §4.2 document against the
model: it is refused, and `policies.1.escalation` is one of its three `extra_forbidden` errors.

| Option | Count at policy 1 / 2 / 5 | Verdict |
|---|---|---|
| (a) policy plus one, fixed by the platform | 2 / 3 / 6 | **Adopted.** FR-152 says "an *additional* Approver", and that is relative at every count. FR-163's "two" is the same rule read at the default of one |
| (a′) policy plus `n`, with `n` a policy key such as `approvers_added`, `n ≥ 1` | 1+`n` / 2+`n` / 5+`n` | Rejected. No requirement asks for an `n` other than one. It needs a model field, a regenerated contract and an evaluator for `when`. `when` is a second expression language that no section specifies. FR-354 names count, roles and evidence as the policy's content, not conditions on certificate contents. A workspace that wants more Approvers raises the entry's count |
| (b) `max(policy, 2)` | 2 / 2 / 5 | Rejected. It adds nobody at policy 2 or more, which breaks FR-152 |
| (c) the escalation's count replaces the policy's (§4.2 built as printed) | 2 / 2 / 2 | Rejected. It adds nobody at policy 2, and it lowers 5 to 2. A policy edit can also set it to 1 and remove FR-152's Approver. `06` R1 refuses that for separation of duties ("cannot be configured away"), and `ApprovalPolicy._separation_of_duties_is_not_configurable` gives the reason in code: "a rule that configuration can disable is not one" |
| (d) policy plus the escalation's count | 3 / 4 / 7 | Rejected. It gives 3 at the default, which contradicts FR-163's "two". It adds two, where FR-152 says one |
| (e) strike the key and state nothing in its place | 2 / 3 / 6 | Rejected. A reader of §4.2 would not see what a non-convex objective needs. FR-364's mechanism (i) restates its floor in §4.2 for that reason |

*Tested against the other rules.* **FR-353**: past one Approver, the Approvers must be distinct
Principals, and neither the submitter nor the Author decides. So policy `p` with a `violated`
certificate needs `p + 1` eligible Principals. A small workspace may be unable to approve. That is
the control working, not a defect. **FR-354**: unchanged. The entry still defines count, roles
and evidence, and the plus one is not an entry field. **FR-364**: an evidence floor, so it is not
amended. Its principle holds by analogy: a policy may add to what a requirement fixes and may not
remove it. (c) would let it remove FR-152's Approver, and (a) cannot. **FR-365** (Phase 3): the
base is the tier-matched entry's count. **FR-385** (unbuilt, `FD-1281`): an `expedited` request
needs its expedited count plus one. FR-385 permits the *policy* to reduce *its* count. FR-152 is
`02`'s requirement on the objective, and no policy count reaches it. `RL-1296` item 5 holds
`expedited` independent of the approver-count work, and this keeps it so. **`RL-1296`** leaves to
`FD-1281` whether the unmodelled §4.2 keys are modelled or struck. This ruling decides the
`escalation` limb only: struck. `expedited` and `separation_of_duties` stay `FD-1281`'s. The
row's `decision:` is the lead's. **The count is fixed at submission**: it is stored on the request
row from the latest certificate at `submit`. A later policy edit does not move an open request.
That is the behaviour of `approvals.submit` today (`backend/src/app/platform/approvals.py:286`). A
re-certification cannot happen under review: `certify` accepts only `draft` and `certified`
(`backend/src/app/platform/objectives.py:451`).

*Every §4.2 entry, checked at `101e32dc` (`docs/specs/06-governance.md:344-372`).* One entry
changes. The others do not change.

| §4.2 item | Lines | Before | After |
|---|---|---|---|
| `validation_rule` | 347-348 | as printed | unchanged |
| `custom_objective` | 349-351 | `{"artifact_type": "custom_objective", "approvers_required": 1,` / `"approver_roles": ["approver"], "evidence": ["objective_certificate"],` / `"escalation": {"when": "certificate.convexity == 'violated'", "approvers_required": 2}},` | `{"artifact_type": "custom_objective", "approvers_required": 1,` / `"approver_roles": ["approver"], "evidence": ["objective_certificate"]},` |
| `custom_metric` | 352-353 | as printed | unchanged. FR-157: a metric certificate has no convexity check ("absent, not `not_applicable`"), so the rule cannot apply |
| `model` | 354-356 | as printed | unchanged |
| `peril_structure` | 357-358 | as printed | unchanged |
| `rating_version` | 359-361 | as printed | unchanged |
| `deployment` (`prod`) | 362-364 | as printed | unchanged. `RL-1296`'s field is not affected |
| `expedited` (top level) | 366-367 | as printed | unchanged text. The new note gives the plus one on top of it once FR-385 is built |
| `separation_of_duties` (top level) | 368 | as printed | unchanged |
| prose after the block | after 372 | none | the note below, added |

**The spec change, recorded and not applied.** It is applied at **WK-690 S3 Task 7**, in the one
commit that adds the `submit` increment (`CLAUDE.md` §2: spec, code and tests in one commit). It
does not take its own path. Only one entry changes, and the code that enforces the rule is Task 7's.
An earlier, separate change would print a rule that nothing enforces, which is the gap `FD-1281`
records. `RL-1296` item 5 orders its §4.2 field the same way. The executor applies the text below
verbatim under `.claude/skills/spec-change`. The design step is this record. A wording change is a
new ruling, not a judgement at Task 7. The dispatch record carries it as a further DP-S3-4 delta at
Task 7.

1. `06` §4.2 `custom_objective` entry: before and after as in the table above.
2. `06` §4.2, a new note after the paragraph `` `separation_of_duties.configurable: false` is deliberate ``:
   > **A non-convex Custom Objective needs the policy's count plus one, and that is not a policy
   > key** (`02` FR-152; added <Task 7 date>, `RL-<minted id>` DP-S3-4). When the latest
   > certificate of a submitted `custom_objective` version has a `convexity` check with status
   > `violated`, the request's `approvers_required` is the matching entry's `approvers_required`
   > plus one. That is two under the defaults above and three under a policy of two. It applies to
   > both objective kinds. When FR-385 is built, it applies to the expedited count too. It is
   > stored on the request row (§4.3) at submission, and no policy can configure it, for R1's
   > reason: a rule that a policy edit can remove is not a rule. It replaces the entry's former
   > `"escalation": {"when": "certificate.convexity == 'violated'", "approvers_required": 2}`. That
   > was an absolute count, which added nobody under a policy of two, and the model never accepted
   > it (`FD-1281`).
3. `02` FR-163: text **S5** under *Spec changes — the exact texts*.
4. `02` §7.1, the `06-governance` row (`docs/specs/02-modelling.md:2859`): "two approvers for
   non-convex objectives" becomes "an additional Approver for a non-convex objective (FR-152):
   two under the default policy".
5. **`WF-702` step B4.2** (`docs/workflows/WF-00702-custom-objective-lifecycle.md:121`):
   "Escalates: convexity `violated` triggers the two-approver rule from the Approval Policy"
   becomes "Escalates: convexity `violated` adds one Approver to the Approval Policy's count,
   two under the default policy". The citation `` `02` FR-152, `06` §4.2 `` is unchanged. **Not
   Task 7's executor:** `document-ids.md` §1.6's WF row gives the journey to the decision-maker
   via `spec-change`, and the executor "never amends the journey itself". A decision-maker
   applies it in its own PR after Task 7 merges.

Checked and unchanged: FR-152 (relative already); FR-353, FR-354, FR-364, FR-365 and FR-385
(above); `06` §4.3, whose `approvers_required` is already the request's own count; and
`02-modelling.md:1067` ("a second Approver (FR-152)"), which is the default instance.

**Red first, at the base.** The tests use a `violated` objective of each kind unless they say
otherwise.

1. Policy 1: the request row's `approvers_required` is 2, and the submission's audit `after`
   gives 2. One non-author approval leaves the objective in `review`. A second, distinct
   approval approves it. This fails at the base, where the row holds 1 and one approval approves.
2. Policy 2: the row holds 3. Two approvals leave the objective in `review`, and a third
   approves it. This fails at the base and **also under (b)**, which stores 2.
3. The §4.2 default instance: under `DEFAULT_POLICY` the row holds 2. That is the outcome the
   struck key printed, and the test fails at the base, where the row holds 1.
4. Policy 5: the row holds 6, and `ApprovalRequest` validates it. This shows that the policy's
   `le=5` does not clip the request.
5. Controls, green at the base and after: a `pass` certificate under policy 1 stores 1, and one
   approval approves it. A policy document whose `custom_objective` entry carries an
   `escalation` key is refused `extra_forbidden`, so no workspace can configure the rule.
6. Measured, by `FD-1281`'s method: the `policies` array parsed out of §4.2 and validated as
   `ApprovalPolicyEntry` values is refused on `policies.1.escalation` at the base and validates
   after Task 7's commit. The whole document stays refused on `expedited` and
   `separation_of_duties` (`FD-1281`'s other limbs). Record the command and both outputs in the
   ledger.

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

**The dated line exists.** *(Added at the text-fix pass.)* The maintainer's acceptance, in
the lead's channel entry headed *"2026-10-01 08:07:02 BST — ACCEPTANCE: RL 9782 DP-S3-5's Phase 3 destination; FILE the quantile-convexity gap as an FD now"*, verbatim:

> *"2026-10-01 — the maintainer (by delegation) accepts Phase 3 as the destination of
> FR-207's two `custom_objective_ref` residuals (`GlmSpec.custom_objective_ref` and
> `Model.custom_objective_ref`), as RL 9782 DP-S3-5 (a) rules: the GLM arm's custom
> objective is a separate, unspecified capability (a `glum` IRLS fit has no path from a
> per-observation loss in `02` §4.6's grammar), and the `Model` field moves with it to avoid
> a second, lossy source of truth. It follows the RL-1265 pattern, and PL-1268 Slice 3
> anticipated it ('re-noted'). Conditions: spec change first (FR-207 gets a dated amendment
> citing RL 9782, with every owner quotation swept); owner the maintainer; listed in the P2
> phase closure record for P3's first plan. This is a scope move made before the 3 Oct scope
> freeze."*

**Spec change, applied by the executor at Task 8.** FR-207 gets a dated amendment: both
`custom_objective_ref` residuals move from WK-690 to Phase 3 as above, citing this ruling.
The same commit corrects the owner clause wherever FR-207's 2026-08-25 sweep list found it
quoted: `model_schema/objectives.py` (around `:108`), `frontend/src/components/ObjectivePicker.vue`,
the `DECLARED_AND_UNBUILT` notes in `backend/tests/test_contracts.py` (`model` and
`model-spec`), and the staging descriptions on `model.custom_objective_ref` and
`model-spec`'s `GlmSpec` branch. Before writing, the executor greps for every quotation:
`git grep -n "custom_objective_ref" -- docs/specs docs/contracts packages backend frontend/src`.
The exact texts and their placements are **S6** (FR-207) and **S7** (the sweep) under
*Spec changes — the exact texts*.

**Red first.** No behaviour changes, so the red step is the drift check. Before Task 8,
`git grep -n -E "custom_objective_ref.*WK-690|WK-690.*custom_objective_ref" -- packages backend frontend/src docs/contracts docs/specs`
lists every quotation of the old owner. After Task 8 it prints only FR-207's own dated
history. `generate-contracts.py --check` passes. The contract keeps both properties with
their notes; neither is dropped.

## Spec changes — the exact texts

*(Added at the final pre-mint text pass, 2026-10-01, on the maintainer's exact-text rule.)*
Each item below
gives the file, the place, and the exact bytes to find and to write. `<Task N date>` is the
date of the commit that applies the item. `RL-<minted id>` is this ruling's minted id. Nothing
else in a text is a placeholder. Placement was read at `origin/main` `65fc6129`.

**S1 — `06` FR-367, Task 3 (DP-S3-2).** Placement: `docs/specs/06-governance.md`, the FR-367
row (`:148`). The text is **appended** to the end of the row's second cell, after
`` with the `expression` kind: adding a member now that nothing checks would recreate the exact defect §4.1 records. `` and one space, before the closing ` |`. Nothing is struck.

```text
**Clarified <Task 3 date> (`RL-<minted id>` DP-S3-2): `custom_objective:author` is required in addition to `model:fit`, never instead of it, on create and on derive.** Create and derive are one act, so a principal must not derive an objective that it cannot create. Both routes keep their `model:fit` dependency, and an `expression` objective adds the author check to it. Template create and certify remain `model:fit`, and submit remains `model:submit`. This row is silent on the conjunction; the clarification is the ruling's reading, not a reading of the text above.
```

**S2 — `02` §5.1 owned codes, Task 4 and Task 7 (DP-S3-3).** Placement:
`docs/specs/02-modelling.md`, the §5.1 owned-codes list (`:2102`, `:2104`). Each marker is
**removed** in place, in the commit that registers its code. Task 4 replaces the line

```text
`OBJECTIVE_GRAMMAR_VIOLATION` (declared, Phase 2),
```

with

```text
`OBJECTIVE_GRAMMAR_VIOLATION`,
```

Task 7 replaces the line

```text
`OBJECTIVE_NOT_CERTIFIED` (declared, Phase 2),
```

with

```text
`OBJECTIVE_NOT_CERTIFIED`,
```

The other two `(declared, Phase 2)` markers (`OBJECTIVE_NONFINITE_DERIVATIVE`,
`OBJECTIVE_ROUND_BUDGET_EXCEEDED`) are not this ruling's and are unchanged.

**S3 — `02` §5.1 certify row, Task 5 (DP-S3-3).** Placement: `docs/specs/02-modelling.md`,
the §5.1 endpoint row for `POST /api/v1/custom-objectives/{id}/certify` (`:1837`). The third
cell is **appended to**. Task 5 replaces the row

```text
| `POST` | `/api/v1/custom-objectives/{id}/certify` | **202** Run the certificate checks (FR-146) |
```

with

```text
| `POST` | `/api/v1/custom-objectives/{id}/certify` | **202** Run the certificate checks (FR-146). An `expression` objective whose `derived` is null is refused 409 `VALIDATION_FAILED` before a job is enqueued, with a `detail` naming `POST /api/v1/custom-objectives/{id}/derive` (**added <Task 5 date>, `RL-<minted id>` DP-S3-3**) |
```

**S4 — `02` §5.1 stand-in sentence, Task 7 (DP-S3-3).** Placement:
`docs/specs/02-modelling.md`, the third bullet of the blockquote that begins
`` `OBJECTIVE_NOT_CERTIFIED`, `OBJECTIVE_GRAMMAR_VIOLATION` and `` (`:2140-2142`). The sentence
is **struck and replaced**, with the dated note after it. Task 7 replaces the line

```text
>   raises them is scheduled. `submit_for_review` stands in with `VALIDATION_FAILED` today.
```

with

```text
>   raises them is scheduled. ~~`submit_for_review` stands in with `VALIDATION_FAILED` today.~~
>   **Amended <Task 7 date> (`RL-<minted id>` DP-S3-3): the stand-in is replaced.** A
>   submission of a `draft` objective, of either kind, is refused 409
>   `OBJECTIVE_NOT_CERTIFIED`. The predicate is the status `draft`: `record_certificate` sets
>   `draft` on a failed certificate and `certified` on a passing one, so `draft` is exactly
>   "no passing certificate for this version". Every other invalid transition to `review`
>   keeps 409 `VALIDATION_FAILED`.
```

**S5 — `02` FR-163, Task 7 (DP-S3-4).** Placement: `docs/specs/02-modelling.md`, the FR-163
row (`:227`). One clause is **struck and replaced**, and a dated note is **appended** to the
end of the second cell. Task 7 replaces

```text
Approval is by an Approver who is not the author; `expression` objectives with `convexity: violated` need two Approvers (FR-152). Editing an `approved` objective creates a new version requiring fresh certification and approval. |
```

with

```text
Approval is by an Approver who is not the author; ~~`expression` objectives with `convexity: violated` need two Approvers (FR-152)~~ any objective whose certificate has `convexity: violated` needs the policy's Approvers plus one (FR-152); at the default policy that is two. Editing an `approved` objective creates a new version requiring fresh certification and approval. **Amended <Task 7 date> (`RL-<minted id>` DP-S3-4): the non-convex rule is relative and applies to both kinds.** FR-152's Approver is *additional* to the policy's count, so an absolute two adds nobody under a policy of two. The quantile template already certifies `convexity: violated`, so the rule is not the `expression` kind's alone. The count is fixed on the request at submission, and no policy key sets the increment (`06` §4.2). |
```

**S6 — `02` FR-207, Task 8 (DP-S3-5).** Placement: `docs/specs/02-modelling.md`, the FR-207
row (`:370`). The text is **appended** to the end of the row's second cell, after
`` so it goes stale silently. `` and one space, before the closing ` |`. Nothing is struck: the
earlier amendments are dated history.

```text
**Amended <Task 8 date> (`RL-<minted id>` DP-S3-5; the Phase 3 destination accepted by the maintainer, by delegation, 2026-10-01): both `custom_objective_ref` residuals move from WK-690 to Phase 3, together, owned by the maintainer.** The GLM arm's custom objective is a separate capability that this spec does not specify: a `glum` fit is a family and a link fitted by IRLS, and a per-observation loss in §4.6's grammar has no family and no path to such a fit. So `GlmSpec.custom_objective_ref` cannot go live in WK-690. `Model.custom_objective_ref` moves with it, because the 2026-08-25 amendment above holds that the `Model` field records what the `GlmSpec` field declares. Made live for a GBM, it would be a second, lossy record of `spec.objective.ref`, the defect `transparency_artifact_id` was struck for. The verdicts do not change: the `GlmSpec` field is absent entirely and the `Model` field is declared and unbuilt, and the contract keeps both properties with their notes. The P2 phase closure record lists both for P3's first plan. The owner clause is corrected in the same commit everywhere it was quoted: `model_schema/objectives.py` (`ObjectiveBackend`), `frontend/src/components/ObjectivePicker.vue`, `backend/tests/test_contracts.py`'s `DECLARED_AND_UNBUILT` note, and the staging descriptions on `model.custom_objective_ref` and `model-spec`'s `GlmSpec` branch.
```

**S7 — the owner-quotation sweep, Task 8 (DP-S3-5), in the same commit as S6.** Each item
replaces the exact bytes shown, and nothing else. No replacement names WK-690, so that the
DP-S3-5 drift `git grep` prints only FR-207's own dated history after Task 8. The generated
schemas (`docs/contracts/schemas/generated/custom-objective.schema.json` and
`custom-metric.schema.json`, `ObjectiveBackend`'s description) are regenerated by
`uv run python scripts/generate-contracts.py`, never hand-edited.

S7.1 — `packages/model-schema/src/model_schema/objectives.py`, the `ObjectiveBackend`
docstring (`:107-110`). Replace

```text
    needs `GlmSpec.custom_objective_ref`, which FR-207 records as absent entirely
    and owned by WK-690 — Phase 2, not this one. The owner was reassigned on 2026-08-22 and
    confirmed on 2026-08-25 to cover this field as well as its `Model` twin, which
    records what it declares. The member exists because FR-153 names it and an author
```

with

```text
    needs `GlmSpec.custom_objective_ref`, which FR-207 records as absent entirely
    and owned by Phase 3: a separate, unspecified capability, moved there on <Task 8 date>
    (RL-<minted id> DP-S3-5) together with its `Model` twin, which records what it
    declares. The member exists because FR-153 names it and an author
```

S7.2 — `frontend/src/components/ObjectivePicker.vue`, the header comment (`:11`). Replace

```text
 * entirely" with **WK-690** as owner — Phase 2, reassigned 2026-08-22 — and
```

with

```text
 * entirely" with **Phase 3** as owner — moved there on <Task 8 date>, RL-<minted id> — and
```

S7.3 — `backend/tests/test_contracts.py`, the `DECLARED_AND_UNBUILT` note (`:532-534`).
Replace

```text
#:   and the `Model` one *"declared and unbuilt"*. **Both are owned by WK-690** — Phase 2,
#:   reassigned 2026-08-22 and confirmed 2026-08-25 to reach the pair rather than the
#:   `Model` half alone. They cannot be split: `Model.custom_objective_ref` would record
```

with

```text
#:   and the `Model` one *"declared and unbuilt"*. **Both are owned by Phase 3**, a
#:   separate, unspecified capability, moved there together on <Task 8 date>
#:   (RL-<minted id> DP-S3-5). They cannot be split: `Model.custom_objective_ref` would record
```

S7.4 — `docs/contracts/schemas/model.schema.json`, the `custom_objective_ref` description
(`:168`). Replace

```text
DECLARED AND UNBUILT (FR-207, owner WK-690 — Phase 2, reassigned 2026-08-22 and confirmed 2026-08-25 to reach this field and its `GlmSpec` twin, not the `Model` one alone).
```

with

```text
DECLARED AND UNBUILT (FR-207, owner Phase 3, moved there on <Task 8 date> with its `GlmSpec` twin, RL-<minted id> DP-S3-5: the GLM arm's custom objective is a separate, unspecified capability).
```

S7.5 — `docs/contracts/schemas/model-spec.schema.json`, the `GlmSpec` branch's
`custom_objective_ref` description (`:83`). Replace

```text
DECLARED AND UNBUILT (FR-207, owner WK-690 — Phase 2, reassigned 2026-08-22 and confirmed 2026-08-25 to reach this field and its `Model` twin).
```

with

```text
DECLARED AND UNBUILT (FR-207, owner Phase 3, moved there on <Task 8 date> with its `Model` twin, RL-<minted id> DP-S3-5: the GLM arm's custom objective is a separate, unspecified capability).
```

Checked and unchanged by S7: `02-modelling.md:643-658` (dated 2026-08-17 and 2026-08-21
notes, history) and `:1314` (names no owner). If the executor's `git grep` finds a quotation
that S7 does not list, that is a stop, reported to the lead; the executor does not word it.

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop. This covers every text S1 to S7 above and the §4.2 texts under DP-S3-4.

## What it obliges

| Ruling | Applied at | Delta from PL 9789's recommendation |
|---|---|---|
| DP-S3-1 (a) | Task 6 | Compiles the stored `derived`, never re-derives. The status gate is unchanged (`certified`, `review`, `approved`). The link is read by the certify function |
| DP-S3-2 (b) | Task 3 | Derive keeps `model:fit` and adds author, where the plan dropped `model:fit`. `:617` is unchanged; a new author-without-`model:fit` test guards both routes. FR-367 gets a dated clarification. Task 3 waits for `PL-1279`'s parity slice to merge |
| DP-S3-3 (a) amended | Tasks 4, 5, 7 | The position goes in `errors[0]`, not a problem extension. An underived certify is `VALIDATION_FAILED`, not `OBJECTIVE_NOT_CERTIFIED`. A submit is `OBJECTIVE_NOT_CERTIFIED` only from `draft` |
| DP-S3-4 (a), both kinds | Task 7 | None. The quantile template is a live instance today, which corrects `PL-1268`'s "first reachable by an `expression` objective" |
| DP-S3-5 (a) | Task 8 | The dated line accepting the Phase 3 destination exists (quoted under DP-S3-5); Task 8 quotes it |

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
   creates or derives: the new author-without-`model:fit` test is green at the base (a control) and fails if the route's `model:fit` dependency is removed. `test_deriving_without_model_fit_is_refused`
   (`:617`) grants only the auditor role and is unchanged. *(Corrected at the text-fix
   pass, audit F3: this item said `:617` fails for that caller, which it cannot see.)* A built-in role grants the
   member: the `BUILTIN_ROLES` test fails.
3. **DP-S3-3.** A grammar error without its position: the `errors[0]` assertion fails. An
   underived expression enqueues a certify job: the no-job-row assertion fails. A `draft`
   submit answers `VALIDATION_FAILED`: the rewritten `:429` test fails on `["code"]`. An
   `approved` re-submit answers `OBJECTIVE_NOT_CERTIFIED`: the control fails.
4. **DP-S3-4.** A `violated` objective of either kind approved by the policy's count
   alone: the one-approval-stays-in-`review` test fails, at policy one and at policy two.
5. **DP-S3-5.** A quotation of WK-690 as the residuals' owner survives Task 8: the
   `git grep` above prints it.
