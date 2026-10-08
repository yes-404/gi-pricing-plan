# 06 — Governance

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `GOV`
**Prerequisites:** [`00-overview.md`](00-overview.md) §1.4 (actors), §3 (FR-4/7/20).

---

## 1. Purpose & scope

### 1.1 In scope

The controls that make the platform's output defensible to an internal reviewer, an
auditor, or a regulator:

1. **Identity, roles, and permissions** — who can do what, to which artifacts.
2. **Approval workflow** — submission, evidence bundles, review, decision, and the
   separation-of-duties rules that apply to every governed artifact.
3. **Audit log** — the append-only record of every state change that affects a price.
4. **Generated documentation** — model and rating dossiers assembled from persisted
   artifacts, never hand-maintained.
5. **Change control across artifact types** — one consistent lifecycle model, so
   "approved" means the same thing for a Model, a Custom Objective, a Validation Rule, and
   a Rating Version.
6. **Regulatory response support** — reconstructing "what was live on date D, and why" and
   exporting the evidence.

### 1.2 Out of scope

| Not here | Where instead |
|---|---|
| Authentication mechanics (OIDC, sessions, tokens) | `07-platform.md` — this module consumes an authenticated principal |
| The *content* of what is approved | The owning module spec (`01`–`05`) |
| Corporate policy (who *should* be an Approver at a given insurer) | Configuration, not platform logic |
| Legal advice on regulatory obligations | Out of platform; we produce evidence, humans interpret it |

### 1.3 Hard rules

> **R1 — Separation of duties.** The submitter of an approval request can never be its
> approver. This is enforced in the backend, not the UI, and cannot be configured away.
>
> **R2 — The audit log is append-only and complete.** No API, role, or admin operation can
> update or delete an Audit Event. Every governed transition writes its event in the same
> database transaction as the change (FR-7) — if the audit write fails, the change
> fails.
>
> **R3 — Documentation is generated, never authored.** Every figure in a model dossier
> traces to a persisted artifact. Free-text commentary is a distinct, attributed,
> versioned field — never a place where numbers are retyped.
>
> **R4 — Approval requires evidence, and the required evidence is defined per artifact
> type.** An approval request missing its required evidence cannot be submitted, let alone
> approved.

---

## 2. Concepts & glossary

| Term | Definition |
|---|---|
| **Principal** | An authenticated identity acting on the platform: a User or a Service Account (a Consumer System calling the scoring API). |
| **Role** | A named bundle of Permissions. The platform ships the roles of `00` §1.4 and allows custom roles. |
| **Permission** | An atomic `(action, resource_type)` capability, e.g. ~~`model:approve`~~ `approval:decide` *(amended 2026-09-28, `RL-1236` DP-C)*, `dataset:acknowledge_warning`, ~~`rating_version:deploy_prod`~~ `deployment:promote`. *(Amended 2026-09-28, `RL-1232` DP-6: there is one deploy permission, `deployment:promote`, and no per-environment family. Environments are configurable (`07` FR-428), so a per-environment name would make the permission vocabulary that FR-344's custom roles compose from open-ended.)* |
| **Scope** | The subset of artifacts a role assignment applies to: workspace-wide, or restricted to named Datasets, Model Families, or Rating Algorithms (e.g. a motor actuary who cannot approve home pricing). |
| **Governed Artifact** | Any artifact with an approval-bearing lifecycle: Dataset Version, Validation Rule, Model, Custom Objective, Custom Metric, Peril Structure, ~~Rate Table Version~~, Rating Version, Optimisation Run (when cited as evidence). *(Rate Table Version struck 2026-09-28: it has no approval lifecycle and is governed through the Rating Version that pins it. See `03` FR-1186 and OQ-620.)* |
| **Evidence Bundle** | The set of artifact references required for that artifact type (§3.3), resolved and pinned at submission time. |
| **Approval Policy** | The workspace configuration stating, per artifact type and environment, how many approvers are needed, which roles may approve, and what evidence is required. |
| **Approval Decision** | An approve / reject / request-changes act by an Approver, with a mandatory comment. |
| **Attestation** | A periodic, recorded confirmation by a named role that a live artifact remains fit for purpose (annual model review). |

---

## 3. Functional requirements

### 3.1 Identity, roles, permissions

| ID | Requirement |
|---|---|
| **FR-342** | Every API call resolves to a Principal. Anonymous access exists only for health checks and the OpenAPI document. |
| **FR-343** | Permissions are checked in the backend on every request against `(principal, permission, resource, scope)`. The frontend hides what a user cannot do; it never *enforces* it. |
| **FR-344** | The platform ships the roles from `00` §1.4 (Analyst, Pricing Actuary, Approver, Deployer, Auditor, Admin) with documented default permission sets, and supports custom roles composed from the same permission vocabulary. |
| **FR-345** | Role assignments are **scoped**: workspace-wide, or limited to named Datasets, Model Families, or Rating Algorithms — so a motor actuary cannot approve home pricing without an explicit assignment. *(Amended 2026-10-03, WK-674 Slice 2, `RL-1301` B and `CR-1212` item 4: the list of scopes gains **Environments**, so that a Deployer can be limited to named environments. The scope kind is the `ScopeType` value `environment`, and `scope_id` is the Environment's id. A workspace-wide Deployer still covers every environment. `deployment:promote` is checked with the target Environment as the resource, so a Deployer whose assignment names only `uat` is refused on `prod`.)* |
| **FR-346** | The **Auditor** role is read-everything, write-nothing, including access to the audit log, superseded artifacts, and archived datasets. No role, including Admin, can hide an artifact from an Auditor. |
| **FR-347** | Service Accounts (for Consumer Systems) hold scoring permissions only, scoped to named environments, with credentials issued and rotated per `07-platform.md`. A Service Account can never hold an approval or deployment permission. |
| **FR-348** | Permission changes, role creation/edit, and role assignment are themselves audited and require the `admin:manage_roles` permission. A user cannot grant themselves a permission they do not hold. |
| **FR-349** | **Break-glass** access (emergency elevation) is supported as a time-boxed, reason-required, immediately-notified grant that expires automatically and is prominently flagged in the audit log. |
| **FR-350** | **Identity and role membership are the identity provider's; artifact *scope* is the platform's.** (OQ-634, decided 2026-08-18; **Phase 3**.) An IdP group maps to a platform Role by configuration (`07` FR-390), so a leaver removed from the group loses platform access without anyone here remembering to act — which is the requirement large insurers actually impose, and the one a platform-authoritative model quietly fails. **Scope (FR-345's dataset, model-family and rating-algorithm restrictions) is assigned in-platform and never inferred from a group**, because scope names artifacts that exist here and nowhere else: an IdP administrator cannot express "motor-* but not household-*" against objects their directory has never heard of, and a mapping that pretended otherwise would silently widen access whenever a new model family was created. The two halves fail differently on purpose: a group that maps to no Role grants **nothing** (FR-390), and a principal whose Role is granted but whose scope is unassigned holds the role's permissions over **no artifacts** rather than over all of them. Both defaults are closed, and the second is the one an implementation gets wrong. |

### 3.2 Approval workflow

| ID | Requirement |
|---|---|
| **FR-351** | The approval lifecycle is uniform across artifact types: `draft → review → (approved \| changes_requested \| rejected)`. Post-approval states (`live`, `superseded`, `retired`) belong to the owning module but are governed by the same audit rules. **Clause added 2026-09-28 (WK-1178), on the deputy's decisions by delegation of that day (the approval status bypass, recorded in #855's approval-bypass finding): only a version in its type's reviewable state can be put to a decision.** The reviewable state is `review` for `model`, `custom_objective`, `custom_metric`, `peril_structure`, `validation_rule` and `rating_version`, and `validated` for `dataset_version`, whose lifecycle has no `review` state. `POST /approval-requests` refuses any other state with `APPROVAL_SUBJECT_NOT_IN_REVIEW` (409), naming it, because a version reaches its reviewable state only through its owning module's own path, where that module's gates run; and the decision hooks refuse it again on the row they hold locked. A hook moves the version only once the request is decided, as FR-355 says: nothing while it is still in review, the approved state on approval, and the returned state on a rejection, a request for changes or a withdrawal; its Audit Event's `before` is the row's real prior state. `peril_structure`, `validation_rule` and `dataset_version` have no decision hook: approving one records the governance decision and does not move the version's row. **Amended 2026-10-05, `RL-1407` DP-1 (WK-1178, the `FD-1356` fix):** `validation_rule` now has a decision hook. A decision on a validation rule's request moves the rule as FR-355 says: `approved` on approval, and `draft` on a rejection, a request for changes or a withdrawal. Before it writes `approved`, the hook refuses a rule whose attached dry-run report cannot be read in the workspace, or records an `error` outcome, with `EVIDENCE_INCOMPLETE` (FR-363). The sentence of this requirement that names the types with no decision hook now holds for `peril_structure` and `dataset_version` only. `01`'s `POST /validation-rules/{id}/approve` records its decision through this path and moves nothing itself. |
| **FR-352** | Submission requires: a complete Evidence Bundle (§3.3), a change summary, and a completed checklist for that artifact type. Missing items block submission with a field-level explanation (R4). |
| **FR-353** | **Separation of duties**: the submitter cannot approve, and where two approvals are required they must be distinct Principals (R1). Enforced in the backend. **Amended 2026-09-28 (WK-1178), on #856's DP-A and the deputy's decisions by delegation of that day, the second refining the first: neither the submitter nor the Author of an artifact version may decide on it — approve, reject or request changes — exactly as R1 bars the submitter.** The **Author** is the actor of the version's **creation Audit Event** (`00` §2.5), one definition for all seven approvable types — `model` (`model.reserved`), `custom_objective`, `custom_metric`, `peril_structure`, `validation_rule`, `dataset_version` and `rating_version` (`<type>.created`). For a `model` the creation event is `model.reserved`, not `model.fitted`: the Author is **whoever reserved the version**, and the fit that follows is not authorship. The audit trail is the governance record of who did what, so it is the one source: four of the seven carry no author column, and where one exists (`created_by` on `rating_version` and `dataset_version`, `authored_by` on `validation_rule`) it is a copy that a test holds equal to the event's actor, never a second source the check reads. The check refuses any decision by the Author with `AUTHOR_CANNOT_APPROVE`, after R1 and before the permission for R1's own reason; and it **fails closed** — a version with no creation Audit Event is refused with `APPROVAL_AUTHOR_UNRESOLVED`, never approved unchecked. A built-in validation rule is seeded `approved` with no creation event and so cannot be put through an approval request, which is correct: it was reviewed in the specification. The reason for the widening: the coarse write rights of #856's DP-A let one person author a version that someone else submits, and the submitter-only rule then let that person approve it. **Scope limit: the Authors of the components a version pins** — a rate table version's or a model version's creator, reaching approval inside a Rating Version — **are not covered here.** That is the harder maker-checker question and is carried to **WK-677**, this requirement's owner, as a named carry with #855's approver ≠ author finding; it sits beside `03` FR-1186, that a Rate Table Version has no approval lifecycle of its own, which is the path by which a component Author's work reaches approval unchecked. *(Added 2026-09-28, `PL-1189`, the deputy's decision on audit finding F4.) For a Rating Version, an approver who authored any golden-quote change listed in the submission's delta (`03` FR-260) is refused with `APPROVAL_BY_EVIDENCE_AUTHOR` (403). This is not the general component-author rule, which WK-677 owns.* *(Noted 2026-09-29: "#856's DP-A" above is `RL-1236` DP-A, the record #856 minted. Its adoption by the decision-maker is in that record's section of this date.)* *(Amended 2026-10-03, `RL-1401` (WK-674 Slice 2): an eighth approvable type, `deployment`, whose subject is a Deployment Request (`03` §4.12; `RL-1301` A.1). Its creation Audit Event is `deployment_request.created`, recorded by the deployment module in the transaction that writes the request and submits it, with `entity_ref` exactly the request's reference `deployment:<environment slug>@<n>` and the submitting Principal as actor. The Author of a Deployment Request is therefore its submitter, whom R1 refuses first; the fail-closed half is unchanged, so a Deployment Request with no `deployment_request.created` event is refused with `APPROVAL_AUTHOR_UNRESOLVED`. A deployment approval request is on the Deployment Request, not on the Rating Version it pins: the Author of that Rating Version is the Author of a component the request pins, and is within the scope limit above, carried to WK-677 beside the rate-table and model-version Authors, not barred by this clause.)* |
| **FR-354** | An **Approval Policy** per workspace defines, per artifact type (and per target environment for Rating Versions): required approver count, permitted approver roles, and required evidence. Defaults are specified in §4.2. |
| **FR-355** | `changes_requested` returns the artifact to **its pre-submission state** and requires a comment. The request and the subsequent resubmission are both audited, so a reviewer's concerns and their resolution are traceable. *(Amended 2026-08-17, WK-661. This said `draft`, and for a Model that is wrong: `02` uses `draft` for a specification reserved but not yet fitted, and `02` R2 makes a fitted model's coefficients immutable — so a model returned from review cannot un-fit, and `draft` would describe an artifact with numbers as one without. A Model returns to `fitted`; `rejected` and `withdrawn` return it there too. For artifact types whose pre-submission state **is** `draft`, nothing changes. **Extended 2026-08-18, WK-661: a Custom Objective returns to `certified`**, for the same reason and with a sharper edge — a certificate is pinned to the objective version (`02` FR-146), the version did not change when an approver asked for one, and returning it to `draft` would discard evidence that is still valid and make re-certification the price of a comment.)* *(Amended 2026-10-04, `RL-1404` (WK-674 Slice 2): **a subject created by its own submission has no pre-submission state, and a request for changes ends it `rejected`.** A Deployment Request (`03` §4.12; `RL-1301` A.1) is written in `review` by the transaction that submits it, and its evidence is pinned once (FR-356), so there is no state to return it to and nothing a resubmission could change. A request for changes on a `deployment` approval request therefore ends the Deployment Request `rejected`, as a rejection does, and the way forward is a new Deployment Request, which pins its evidence afresh. The comment is still required. The reviewer's concern stays traceable through the decision's Audit Event; its resolution is the new request for the same Rating Version and Environment. Every other approvable type's subject exists before its submission (FR-351, FR-386) and is unaffected. An approvable type added later whose subject is created by its own submission states its `changes_requested` outcome in the commit that adds it.)* |
| **FR-356** | Approvals are **pinned**: the decision records the exact artifact version and evidence artifact ids. If any referenced artifact changes, the approval does not carry over — a new version needs a new approval (FR-4). |
| **FR-357** | An approval can be **withdrawn** before deployment by an Approver or an Admin with a reason; it cannot be withdrawn after the artifact is live (the correct action is then a rollback or a new version). |
| **FR-358** | The **Approvals inbox** shows each Approver their pending requests with the evidence inline — diffs, diagnostics, dislocation, GIPP — so review does not require assembling context by hand. |
| **FR-359** | Flags raised elsewhere propagate into the approval surface: `dataset_invalidated` (`01` FR-53), missing transparency artifact (`02` R3), unapproved custom objective (`02` R4), failing GIPP (`04` R4). A flagged artifact cannot be approved until the flag is cleared or explicitly overridden by an Admin with a recorded justification. |
| **FR-360** | **An Admin may override a flag, and the override is built to be expensive and permanent: `admin:manage_roles`-held Admin only, a mandatory written justification, **two** distinct Admins, a badge on the artifact that never expires, an entry in the exception log (FR-385), and its own line in the dossier's approval history (§4.4 §16).** (OQ-635, decided 2026-08-18; **Phase 3**.) Refusing overrides outright is the cleaner rule and the wrong one: flags come from other modules and can be *false* — a dataset invalidated and since re-validated, a transparency artifact whose generation job failed — and a governance system with no recourse gets bypassed outside itself, in a spreadsheet nobody audits. So the escape hatch exists **and leaves a scar**: the artifact carries `flag_overridden` for the rest of its life, not merely a line in a log that has to be searched for. **The permanence is the requirement, not the ceremony.** Two approvers and a justification make an override deliberate; only the permanent badge makes it *visible to the next reader*, who is the person an auditor will ask why this model was approved with a flag raised against it. An override is never a way to clear a flag: the underlying condition stays raised, and re-running the check is the only thing that lowers it. |
| **FR-361** | **Attestation**: governed artifacts that are live can carry a periodic review requirement (default annual). An overdue attestation is surfaced on the artifact, in the inbox, and in monitoring dashboards — it does not automatically retire anything. |
| **FR-362** | **TAS 200 (Insurance) v2.0 *does* apply to this platform's work, through its `Pricing frameworks` scope item — determined 2026-08-18 by reading the standard, not assumed.** (OQ-638, decided 2026-08-18; the obligations land in **Phase 3** with the dossier.) §1.2 of TAS 200 v2.0 lists *"Pricing frameworks — Technical actuarial work to support pricing frameworks"* among the work in scope, and its glossary defines a pricing framework as the product pricing principles **and the methodologies, assumptions and models implementing those principles** that support an insurer's premium rates or product charges. `insurer` is defined as any undertaking effecting or carrying out contracts of insurance or reinsurance, with no life/general split — so general insurance premium rating is not excluded, and the models, assumptions and rationale this platform produces are framework components by the standard's own definition. It applies to work completed on or after **1 January 2025** (§1.3), and TAS 200 work is also TAS 100 work (§1.4). **The unit of scope is the framework, not the quote:** a scoring call is not technical actuarial work, and nothing here implies otherwise. **There is no pricing-specific provisions section** — sections 2–6 cover valuation, capital, transformations, audit and with-profits — so what binds is §1, *Provisions for all work in scope*: P1.1 (consider and **document** material factors from customer-outcome obligations, which is where Consumer Duty enters), P1.2 (assumptions consistent with those used for other purposes — business planning, reserving, capital), P1.3 (a persistent gap between actual experience and assumed must be considered and documented), P1.4 (communications describe material inconsistencies). §4.4 gains sections **18** and **19** to carry P1.1 and P1.2/P1.4 respectively — appended, never inserted, because section numbers here are identifiers (`CLAUDE.md` §5). |

### 3.3 Required evidence by artifact type

| ID | Requirement |
|---|---|
| **FR-363** | Required evidence is defined per artifact type and enforced at submission (R4): |

| Artifact | Required evidence |
|---|---|
| **Dataset Version** → `validated` | Validation Report with no `fail`; every `warn` acknowledged with justification (`01` FR-46) |
| **Validation Rule** | Successful dry-run result against a real Dataset Version (`01` FR-50) *(Clarified 2026-10-05, `RL-1407` DP-3, on the maintainer's reading of `01` §4.5 step 2 of 2026-09-30: "successful" means the dry run executed. Its report can be read in the workspace and records no `error` outcome. A `fail` outcome is a run that executed and caught rows, and is accepted. A refusal is `EVIDENCE_INCOMPLETE`.)* |
| **Custom Objective** | Objective Certificate with `overall ≠ failed`; applicability declaration; usage impact if a new version of an in-use objective (`02` FR-146/164) |
| **Custom Metric** | Metric Certificate with `overall ≠ failed` (`02` FR-154/157/162) |
| **Model** | Diagnostics (train + holdout); transparency artifact where non-GLM; model comparison where a predecessor exists; factor/banding/grouping rationale; dataset lineage (`02` FR-202) |
| **Peril Structure** | Per-peril model approvals; reconciliation result within tolerance (`02` FR-190) |
| ~~**Rate Table Version**~~ | ~~Change note; diff vs previous; diff vs technical seed where seeded (`03` FR-230/231)~~ **Struck 2026-09-28** (`03` FR-1186, OQ-620): not a Governed Artifact. Its diffs reach approval inside the Rating Version row's rate table diffs, and `03` FR-229 requires its change note on every version. |
| **Rating Version** | Structural diff; rate table diffs; passing regression suite; dislocation run with attribution; GIPP check where enabled; change summary (`03` FR-257) |
| **Deployment to `prod`** | A complete Rating Version approval; a successful `uat` deployment; Deployer permission (`03` FR-267) |

> **`custom_metric` added 2026-08-22 (WK-661, the audit-remediation slice).** §4.2's
> `DEFAULT_POLICY` has named `metric_certificate` for `custom_metric` since 2026-08-20 and
> this table had no row for it — so `EVIDENCE_FLOOR` had no key for the type,
> `below_floor()` returned nothing, and a workspace could edit `metric_certificate` out of
> its own policy entry and be accepted. **§3.3 is the side that was wrong**: the evidence
> was decided when §4.2 gained the entry, and the floor that entry sits on was never
> written down.
>
> **It was not exploitable, and this record must not imply it was.** What protects a metric
> is the lifecycle rather than the policy: submission requires status `certified`, only
> `record_certificate` sets that status, it sets it alongside a `certificate_id`, and the
> `certified_metric_has_a_certificate` CHECK refuses the pair coming apart at a layer a
> direct `UPDATE` cannot walk past — so an uncertified metric cannot be submitted even
> under an emptied policy. The real defect is the one `POLICY_BELOW_EVIDENCE_FLOOR` was
> added to prevent: **the policy reader was told a floor existed where none did.**
>
> The row is deliberately **exactly what is checkable**, and no more. `record_certificate`
> sets `certified` only when `overall` is not `failed`, so the enforced floor is a complete
> projection of this row and leaves FR-364 no remainder to name.

| ID | Requirement |
|---|---|
| **FR-364** | **The table above is a floor. §4.2's `ApprovalPolicy` may add to it and may never remove from it.** (OQ-639, decided 2026-08-18.) The two tables have disagreed since Phase 0 and the code could only enforce one of them, because a check has to read a list and there were two. The deciding case is `02` §4.8 R3: a transparency artifact for a non-GLM model is an invariant of the artifact, not a workspace preference, and a policy edit that removes it is a mispricing waiting for an audit. Three mechanisms, so that neither table can be read alone: (i) the floor is restated in §4.2's own text, so a reader of the defaults sees what the defaults may not drop below — the objection to a floor was always that a submission refused for evidence the policy does not mention is an error nobody can act on; (ii) `PUT /api/v1/approval-policy` refuses an entry whose `evidence` omits a floor kind for that artifact type with `POLICY_BELOW_EVIDENCE_FLOOR`, naming the artifact type and the kinds, because a policy document that says less than it enforces misleads its reader; (iii) submission checks the **union** of the floor and the matching policy entry, so a policy stored before this requirement cannot dodge the floor by being old. **The enforced floor is the checkable projection of §3.3, and the remainder is named with an owner rather than asserted**: for `model` it is `diagnostics` and `transparency_artifact_if_non_glm`; `model_comparison_if_predecessor` stays out until a comparison names its models in a queryable column rather than inside `payload` (owner: the slice that adds it), and §3.3's factor/banding/grouping rationale is unmodelled (owner: Phase 1b). Submission continues to **fail closed** on any evidence kind it cannot verify (R4), so a tightened policy can never silently do nothing. An artifact type with **no §3.3 row has an empty floor** — `peril_structure` is that case — and a floor that says nothing permits anything, which is the right default for an artifact §3.3 predates rather than a gap to be filled by inference. **Amended 2026-08-22 (WK-661, the audit-remediation slice), on both halves.** `custom_metric` joins the floor with `metric_certificate`, §3.3 having gained the row that entry projects — the spec row first, because the entry alone would have put the code above its own specification. And the `peril_structure` sentence above rested on a false premise: §3.3 has carried a Peril Structure row since 2026-08-14, four days *before* this requirement was written, so "no §3.3 row" was never true of it. The empty floor survives the correction, for a reason the original did not give — the row's **reconciliation** half is enforced structurally, since `review` is reachable only from `reconciled` and a `fail` verdict is refused at submission, so a floor entry would restate a lifecycle edge rather than add a control. Its other half, **per-peril model approvals**, sits in `peril_structures.perils` as JSONB and cannot be queried, which is `model_comparison_if_predecessor`'s case exactly: naming it in the floor would fail every peril-structure submission closed on evidence nothing can verify. **Owner: WK-677**, which owns FR-351, FR-352, FR-353, FR-354, FR-355, FR-356, FR-357, FR-358, FR-359, FR-361, FR-363 and evidence enforcement, and is where a queryable per-peril approval projection belongs — an owner that is a workstream rather than "the slice that touches it next", which is a phrase. **Amended 2026-08-29 (WK-671 Slice 2), naming the `rating_version` remainder this requirement had left unnamed since it was written.** The enforced floor for `rating_version` is `structural_diff`, `regression_run` and `dislocation_run`; its §3.3 row also carries rate table diffs, a GIPP check where enabled, and the change summary, which is enforced separately at submission (FR-352). `regression_run` becomes verifiable in **WK-672** (`03` FR-261) and `dislocation_run` in **WK-673** (`03` FR-263). `structural_diff` carries a **trigger rather than an owner** *(superseded by the 2026-09-28 amendment at the end of this row)* — no workstream row names a persisted structural-diff artifact, and `03` FR-219's diff is computed on demand, so the trigger is the first artifact that stores one; naming a workstream that does not own it would be the phrase this requirement already rejects. **And the invariant that was implicit until now, because the three kinds above look like a contradiction of the checkable-projection rule without it: a floor entry that no submission path can yet verify is permitted only while no submission path consults it, and the path that will consult it carries the owner.** That is what distinguishes `rating_version`'s entry, which nothing reads (`effective_evidence("rating_version")` has no caller), from `model_comparison_if_predecessor`, which a live submission check would have refused every model on. Wiring the rating-version check is WK-673's, the last of the two enablers. Ruled in `docs/rulings/RL-00885-finding-1-the-rating-version-evidence-floor-stands-the-specification-is-the-side-that-moves.md` RL-885, with `docs/rulings/RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md` RL-881 for the wiring. **Amended 2026-09-28 (`RL-1184` E4): `structural_diff` has an owner, WK-673.** At submission, WK-673 persists `03` FR-219's structural diff as a content-addressed blob and registers a verifier for the `structural_diff` kind. It does this before it wires `03` FR-257's gate (RL-881). Until then no submission path consults the kind, which this requirement's 2026-08-29 invariant permits. |
| **FR-365** | **A Model Family and a Rating Algorithm each carry a `risk_tier` (`1 \| 2 \| 3`, 1 the most material), and `ApprovalPolicy` entries may key on it — approver count, evidence, and attestation cadence (FR-361).** (OQ-636, decided 2026-08-18; **Phase 3**, and previously deferred there.) Tiering is how UK insurer model governance already works, and per-artifact-type policy cannot express it: `artifact_type: model` treats a headline motor frequency model and a windscreen burning-cost model as the same risk, so a workspace wanting two approvers on the first has to impose them on both and then watch the requirement be resented into irrelevance. **The tier sits on the *family* and the *algorithm*, never on the version**, so it is a standing statement about a line of business rather than a per-fit judgement someone could set to 3 on the day they need a quicker approval; changing it is itself audited (FR-368). It **extends** the policy shape rather than replacing it — an entry with no `risk_tier` applies to every tier, so FR-364's floor and the §4.2 defaults keep working unchanged and a workspace that never tiers anything sees no difference. |
| **FR-366** | **`model:fit` governs Custom Objectives for as long as the catalogue is the only kind, and whether an `expression` objective needs an authoring permission of its own is answered *before* `expression_objectives_enabled` may be lifted — not after.** (OQ-632, **deferred to Phase 2** 2026-08-18, with this requirement as its trigger.) For a §4.5 template objective the two acts are one: choosing `capped_gamma` with a cap is choosing how a model is fitted, by the person who fits it, and a permission no role would grant separately is vocabulary without a decision behind it (§4.1's superseding note). An `expression` objective is different in kind — author-written maths a reviewer must read, whose blast radius spans every model using it (`02` FR-164) — and the answer turns on how much of that review an Objective Certificate can carry (FR-146), which nobody knows until a user-authored loss has been through one. **Deferring is therefore the decision, and this is what stops it decaying into an omission:** the flag is the trigger, **WK-690 is the owner**, and the enum stays closed with nothing unchecked in it meanwhile (§3.1). The separation a distinct permission would buy is not absent in the interim — it is bought by FR-353's submitter-cannot-approve and `02` FR-163's non-author Approver — so what is deferred is an *additional* control, never the only one. **Amended 2026-08-18: the trigger is discharged.** OQ-632 was decided the same day rather than at the flag, as `FR-367`, so what this requirement now carries is its first half — `model:fit` governs template objectives — plus the record that the precondition was met before WK-690 rather than by WK-690. The deferral was answerable sooner than it looked: it rested on how much review a certificate can carry, and that is the wrong dependency, because certification analyses the artifact and never authorises the author. **Noted 2026-10-05 (WK-690 Slice 3, `PL-1382` Task 3):** the discharge `FR-367` names has landed — `custom_objective:author` is built and checked on `expression` create and derive, in addition to `model:fit` (`RL-1362` DP-S3-2). A note, not a change of rule. |
| **FR-367** | **Authoring, editing or versioning an `expression` Custom Objective requires `custom_objective:author`, a permission distinct from `model:fit` and **not** granted by any built-in role's default set. Selecting a §4.5 *template* objective remains `model:fit`, and submitting either for approval remains `model:submit`.** (OQ-632, decided 2026-08-18, discharging FR-366's trigger.) The test is §4.1's own, the one that superseded these strings in the first place: *would a role plausibly grant one and withhold the other?* For a template it would not — choosing `capped_gamma` with a cap is choosing how one's own model is fitted. For an expression it plainly would: "every pricing actuary may fit models" and "a nominated few may write the loss function everyone's models are fitted with" are two statements an insurer makes separately, and an objective is **reusable across models** (§7) whose blast radius spans every model using it (`02` FR-164). Authoring one is a platform-level act wearing the clothes of a per-model one. **Certification and the non-author Approver do not substitute for it**, which is the argument that decided this rather than the cost comparison: `02` FR-146 analyses the artifact — convexity, domain, sampling — and FR-163 gates *approval*, so both act after authoring and neither says anything about whether this principal should be writing loss functions at all. An objective that is merely `draft` can already fit models whose numbers reach a pack. The controls are complementary; the authorisation one was missing. **Not default-granted** is the operative half — a permission every fitter holds is the vocabulary-without-a-decision that §4.1 removed — so it is granted explicitly by an Admin (`admin:manage_roles`) and appears in no built-in role. **The enum member and its check land together in WK-690**, with the `expression` kind: adding a member now that nothing checks would recreate the exact defect §4.1 records. **Clarified 2026-10-04 (`RL-1362` DP-S3-2): `custom_objective:author` is required in addition to `model:fit`, never instead of it, on create and on derive.** Create and derive are one act, so a principal must not derive an objective that it cannot create. Both routes keep their `model:fit` dependency, and an `expression` objective adds the author check to it. Template create and certify remain `model:fit`, and submit remains `model:submit`. This row is silent on the conjunction; the clarification is the ruling's reading, not a reading of the text above. |

### 3.4 Audit log

| ID | Requirement |
|---|---|
| **FR-368** | Every governed state change, permission change, acknowledgement, approval decision, deployment, rollback, suppression, and data purge emits an Audit Event, written in the same transaction as the change (R2). |
| **FR-369** | An Audit Event records: actor (Principal), timestamp (UTC), action, entity reference (`{type}:{slug}@{version}`), before state, after state, justification where the action requires one, `trace_id`, and source (`ui` / `api` / `job` / `system`). |
| **FR-370** | The audit table is append-only enforced at the **database privilege level** — the application role holds `INSERT` and `SELECT` only, with `UPDATE`/`DELETE` revoked (NFR-458). |
| **FR-371** | The audit log is queryable by actor, entity, action, time range, and free text over justifications, with cursor pagination and export to CSV/JSON. |
| **FR-372** | Audit events are chained with a hash of the previous event per workspace, so tampering at the storage layer (below the application) is detectable. The chain head is checkpointed and exportable. |
| **FR-373** | **The audit chain is per workspace, self-held, and described as tamper-*evident* rather than tamper-proof — and the platform ships an explicit `POST /api/v1/audit/anchor` that exports a signed chain head for the customer to store somewhere the operator does not control.** (OQ-633, decided 2026-08-18; **Phase 3**.) Per workspace is already FR-372's shape and this confirms it rather than changing it: a global chain serialises writes across workspaces for no detection benefit, since tampering is detected within the chain that covers the altered event. **What the decision adds is honesty about the threat model, in the product rather than in a footnote.** A self-held chain detects storage-layer tampering — someone editing rows underneath the application — and does **not** detect a determined platform operator, who can recompute every subsequent hash. The UI and the dossier must therefore say *tamper-evident against modification below the application*, and must not say tamper-proof; a claim an auditor can falsify in one question is worse than no claim. The anchor operation closes the operator gap **only to the extent the customer automates it**, so it is offered, documented and never described as enabled by default: it is the customer's ritual, on the customer's schedule, into the customer's store. |
| **FR-374** | Automated (`job` / `system`) actions are audited identically to human ones, with the triggering job id and, where applicable, the schedule or event that caused them. |
| **FR-375** | Sensitive values never enter the audit log verbatim: secrets, credentials, and full quote inputs are recorded as references or hashes, not values (NFR-499). |

### 3.5 Generated documentation

| ID | Requirement |
|---|---|
| **FR-376** | The platform generates a **Model Dossier** for any Model, Peril Structure, or Rating Version, assembled entirely from persisted artifacts (R3). Sections are specified in §4.4, and the dossier states the platform build that produced the figures (`00` FR-18) — under ADR-710 each tenant runs its own deployment, so the build is not inferable from the date. |
| **FR-377** | Human commentary is supported as named, versioned, attributed **Commentary Blocks** slotted into defined positions in the dossier. Commentary is clearly distinguished from generated content in the rendered output. |
| **FR-378** | **Exactly two Commentary Blocks are mandatory before an approval may be submitted — §4.4 §1 *Purpose, scope and intended use* and §15 *Limitations and known issues* — each with a minimum length and **no pre-filled default text to accept**. Every other block stays optional.** (OQ-637, decided 2026-08-18; **Phase 3**.) Requiring commentary in ten slots reliably produces ten paragraphs of boilerplate, which is worse than silence because it *looks* like documentation and an approver stops reading it. Two is the number a person can be made to actually write, and these two are the ones a reviewer asks for first: what is this for, and where does it break. **The absence of default text is load-bearing** — a template with placeholder prose is a boilerplate generator with extra steps, and the platform ships no starter sentence for either block. A minimum length is a blunt instrument and is used anyway, because it costs a determined author nothing and stops "N/A" from being a purpose statement. |
| **FR-379** | Dossiers render to HTML and PDF, and are exportable as a self-contained bundle (document plus the referenced artifact JSON) so an external reviewer can verify a figure without platform access. |
| **FR-380** | A dossier is generated **as at a point in time** and can be regenerated for any historical state — "produce the model documentation as it stood when version 27 went live" is a supported operation, not an archaeology exercise. |
| **FR-381** | Dossiers are versioned artifacts themselves; the version submitted with an approval request is retained exactly as reviewed. |
| **FR-382** | A **regulatory response export** assembles, for a stated date or date range: what was live in each environment, the artifacts it pinned, the approvals behind them, the validation and GIPP evidence, the monitoring results, and the audit trail — as one signed, self-contained archive. |

### 3.6 Change control across the platform

| ID | Requirement |
|---|---|
| **FR-383** | Every governed artifact exposes a uniform **history view**: versions, transitions, actors, timestamps, justifications, and diffs, in one place with one shape regardless of type. |
| **FR-384** | **Blast-radius queries** are available for any artifact: "what depends on this?" spanning datasets → models → peril structures → rating versions → deployments, and "what does this depend on?" in the other direction (`01` FR-75, `02` FR-164). |
| **FR-385** | Emergency changes follow the same path with an `expedited` marker: the same evidence is required, but the Approval Policy may permit a reduced approver count for `expedited` requests, and every expedited approval is reported in a standing exception log reviewed at the next committee. |
| **FR-386** | **Submission resolves the artifact it pins.** `POST /approval-requests` must refuse a reference naming an artifact version that does not exist, with `NOT_FOUND`. *(Appended 2026-08-17, WK-661, from building the model lifecycle — where the spec is right and the code is not, the spec gains the obligation rather than being edited down to what was built.* `CLAUDE.md` *§14.)* FR-356 makes an approval **pinned** to an exact artifact version; a request pinned to a version that was never created is pinned to nothing, and it can be submitted today because the endpoint validates only the `{type}:{slug}@{version}` grammar. The consequence is worse than a bad row: the owning module cannot move an artifact that does not exist, so the request decides without effect and there is nothing for a reader to reconcile the decision against. **Not fixable from the owning module** — resolution needs a lookup per artifact type and DEP-1 forbids `GOV` importing `DATA`–`MON`, so this is a resolver registered *with* governance by each owning module, or a check in each module's own submit path. **Owner: WK-661's peril-structure slice**, which is the first to add a second artifact type to this path and therefore the first where a per-type resolver pays for itself. Until then, a `model:` reference produced by any route in this platform resolves by construction (`02` FR-202's submission holds the row it names), and a decision on a request naming a model that does not exist moves nothing rather than failing — a request nobody can close being the worse of the two. *(Amended 2026-08-22, WK-661's audit-remediation slice.* **Built — and in neither of the two shapes this requirement names.** The fan-out lives in the **route**. `api/approvals.py` already fans out per artifact type for the *decide* direction — `_carry_to_the_artifact`, one call per type, each module's function returning `None` for a request that is not its own — and the route sits above both governance and the owning modules, so DEP-1 is satisfied with no registry and no per-module submit check. `_resolve_the_artifact` mirrors it for the *submit* direction, and `approvals.submit` gained an optional `resolve` callback so governance keeps the **order**: the policy check answers first, because "no approval policy for this artifact type" is the actionable half of the two correct refusals an unpolicied reference earns. This requirement's two options were not wrong so much as incomplete — a resolver registry would have been a second mechanism for a seam that already had one, and the one registry precedent in the codebase, `worker/handlers.register_handler`, is registered from the worker entrypoint and never runs on the API path.* **Six of the twenty artifact types resolve**: `model`, `custom_objective`, `custom_metric`, `peril_structure`, `validation_rule`, `dataset_version`. **A type no module in this build can resolve fails closed**, with the `06`-owned `ARTIFACT_TYPE_NOT_RESOLVABLE` (422). `rating_version` has a policy entry and no module because `03` is unbuilt; thirteen more types have neither. `07`'s `JOB_HANDLER_NOT_REGISTERED` settles what is owed — a platform deployable before every kind has an implementation must **say the capability is absent** rather than accept work it cannot move, and accepting the submission would recreate this very defect one level up. The code is deliberately not `VALIDATION_FAILED`, which the malformed-reference branch still uses correctly: there the caller's input is bad, here it is not. **One divergence stands and is deliberate**: `metrics.resolve_ref` raises `METRIC_REF_UNRESOLVED` where this requirement names `NOT_FOUND`, because `02` §4.13's fit-path caller must tell a stale reference from a missing artifact; the route translates it at the boundary rather than changing the fit path's answer. **Owner for the durable fix: WK-677** — a sibling `resolve_artifact_ref` on `platform.metrics` raising `NOT_FOUND`, alongside moving the three route adapters into their own modules and making `resolve` a required parameter, which is the shape that would be fail-closed by construction rather than by every caller remembering. |

---

## 4. Data contracts

### 4.1 `Role`, `RoleAssignment`, `Permission`

```json
{
  "role": {
    "slug": "pricing-actuary",
    "name": "Pricing Actuary",
    "permissions": "BUILTIN_ROLES[\"pricing_actuary\"] — see below",
    "builtin": true
  },
  "assignment": {
    "principal_id": "uuid",
    "role_slug": "pricing-actuary",
    "scope": {"kind": "restricted",
              "datasets": ["motor-gb-quote-bind"],
              "model_families": ["motor-*"],
              "rating_algorithms": ["motor-gb"]},
    "granted_by": "uuid", "granted_at": "2026-01-05T09:00:00Z",
    "expires_at": null
  }
}
```

*(Amended 2026-09-30, `RL-1305` item D4, on `CR-1247` Proposal 1 (c): the
example's permission list is replaced by a reference.)* A built-in role's permission set is
**`BUILTIN_ROLES`** in `packages/model-schema/src/model_schema/permissions.py`, the one
definition of the names and of the built-in role sets (ADR-704). This page states what each
name governs (the tables below) and never restates a role's set. The list this example
carried named sixteen permissions, twelve of which the platform never defined. Their
successors are in the tables below.

Notably absent from Pricing Actuary: ~~every `*:approve` permission~~ `approval:decide`
*(amended 2026-09-28, `RL-1236` DP-C: one approval permission)* and
~~`rating_version:deploy_*`~~ `deployment:promote` (R1, FR-347). *(Amended 2026-09-28,
`RL-1232` DP-6.)*

> **An `environments` scope, dated 2026-10-03 (WK-674 Slice 2; `RL-1301` B.4, amending the scope example of `RL-1232` DP-6).** An assignment may be scoped to Environments, as it may be to Datasets: a Deployer limited to `uat` carries `"scope": {"kind": "restricted", "environments": ["uat"]}` in the example's form, and is stored as `scope_type` `environment` with `scope_id` the Environment's id (FR-345). The example above is not rewritten.

> **Superseded 2026-08-18 (WK-661, the custom-objectives slice).** The role above lists
> `custom_objective:author` and `custom_objective:submit`. **Neither exists**, and the built
> surface checks `model:read`, `model:fit` and `model:submit` instead — the same three
> permissions that govern the fits those objectives are for.
>
> The spec was the wrong side. Phase 1's objectives are the §4.5 template catalogue
> (FR-150): choosing `capped_gamma` with a cap is choosing how a model is fitted, by
> the person who fits it, and a permission no role would ever grant separately is vocabulary
> without a decision behind it. The `Permission` enum is closed by design (`06` §3.1) so
> that a screen can enumerate what a role grants; two strings in it that nothing checks are
> exactly what a closed enum exists to prevent.
>
> **The separation this would have bought is intact and is bought elsewhere**: FR-353
> keeps the submitter out of the approval, and `02` FR-163 requires an Approver who is
> not the author. What is *not* settled is Phase 2, where an `expression` objective is
> author-written maths rather than a parameter on a shipped loss — a case for a distinct
> authoring permission that the template catalogue does not make. Recorded as **OQ-632**
> rather than decided here — and **decided later the same day as FR-367**: an
> `expression` objective *does* need `custom_objective:author`, distinct from `model:fit`
> and granted by no built-in role's default set.
>
> **`custom_objective:author` therefore returns to the vocabulary, and the name is reused
> deliberately.** It was removed because nothing checked it and the template catalogue made
> no case for it; it comes back with a case and with its check, which land together in WK-690.
> `custom_objective:submit` does **not** return — the same test fails for it, since
> FR-353 already keeps a submitter out of their own approval. The Pricing Actuary set
> above no longer lists either, which is the point of the decision rather than an omission:
> a permission every fitter holds by default would be the vocabulary-without-a-decision this
> note was written about.

> **Permission catalogue, amended 2026-09-28 (`RL-1236`).** The permission names this spec
> uses and the names the code's closed `Permission` enum defines had drifted: 24 on each side,
> 7 shared. The names below are ruled~~; names whose verdict changes scope wait on a
> maintainer decision and are not listed here~~. *(Corrected 2026-09-29: all four of
> `RL-1236`'s decision points are decided, and every ruled name is listed.)*
>
> **Built and now specified.** Each is checked by the route or service named in `RL-1236`, and
> is part of the closed vocabulary §3.1 describes. *(Amended 2026-09-30, `RL-1305`
> item D4.)* **This table has exactly one row per member of `model_schema.Permission`.** The
> names are the enum's, and this table states their meaning. A gate check holds the two equal
> in both directions (`RL-1305` D1 and D2). A new permission lands in one commit: its row
> here, its enum member, and its check (FR-367). **Check owner** names the Work that builds a
> member's first check, and is empty once a check exists. The eleven members this table
> lacked until 2026-09-30 are added, each with its governing text and that text's source:
>
> | Permission | Governs | Check owner |
> |---|---|---|
> | `dataset:read` | Reading Datasets, Dataset Versions and their validation reports and profiles (the dataset read routes; before 2026-09-30 no `06` text described it, and it was named only in the role example's list, now replaced) |  |
> | `dataset:write` | Creating Datasets and Dataset Versions, and writing blobs, validation rules and ingestion (`RL-1236` DP-A, which folds `dataset:create_version` into it) |  |
> | `dataset:validate` | Running validation on a Dataset Version |  |
> | `dataset:acknowledge_warning` | Acknowledging a validation `warn` with a justification (§3.3's Dataset Version row, `01` FR-46; §2's Permission term) |  |
> | `model:read` | Reading Models, Model Specs and their diagnostics (the superseded note above: "the built surface checks `model:read`, `model:fit` and `model:submit`") |  |
> | `model:fit` | Fitting a Model, and writing Factors, Bandings and Groupings (`RL-1236` DP-A). It governs catalogue Custom Objectives (FR-366) |  |
> | `model:submit` | Submitting a Model, or a catalogue Custom Objective, for approval (the notes above; FR-367) |  |
> | `custom_objective:author` | Authoring, editing or versioning an `expression` Custom Objective (FR-367) |  |
> | `rating:read` | Reading Rating Algorithms, Sub-graphs, Regression Suites, Rate Tables, Rating Versions and scoring traces, and an Environment's Deployment history (`03` §4.12; `GET /api/v1/environments/{env}/deployments`, WK-674 Slice 2). *(Amended 2026-10-04, `RL-1404`: a Deployment is a rating record; the Environment's own record is `settings:read`'s.)* |  |
> | `rating:write` | Writing Rating Algorithms and Rate Tables, and creating a Rating Version (`RL-1236` DP-A) |  |
> | `rating:submit` | Submitting a Rating Version for approval (the mapped note below) |  |
> | `rating:compile` | Compiling a Rating Version to its Bundle |  |
> | `approval:decide` | Deciding an approval request. Which roles may decide which artifact type is §4.2's `approver_roles` (`RL-1236` DP-C, the note below) |  |
> | `deployment:promote` | Deploying an approved Rating Version to an Environment (`03` FR-267; R1, FR-347; `RL-1232` DP-6) |  |
> | `audit:read` | Reading the audit log |  |
> | `score:execute` | Real-time scoring (a Service Account may hold it, FR-347) |  |
> | `score:batch` | Batch scoring (a Service Account may hold it, FR-347) |  |
> | `job:read` | Reading Jobs |  |
> | `job:cancel` | Cancelling a Job |  |
> | `settings:read` | Reading workspace settings, and listing and reading Environments (`07` FR-428, FR-431; `GET /api/v1/environments`, WK-674 Slice 2). *(Amended 2026-10-03, WK-674 Slice 2, on the maintainer's dated decision.)* |  |
> | `admin:manage_roles` | Changing permissions, roles and role assignments (FR-348), and the workspace Approval Policy (`PUT /approval-policy` requires it, as this spec's route permission table states) |  |
> | `admin:manage_settings` | Changing workspace settings and reference data, and every per-environment setting value: `07` FR-431's settings, and FR-270/FR-271's routing and shadow switches and shadow configuration (DP-D). Each change writes an Audit Event naming the environment, the key, the old value and the new value. Nothing it guards can change which Rating Version prices a live quote |  |
> | `admin:manage_service_accounts` | Creating, rotating and revoking Service Accounts |  |
> | `admin:break_glass` | Break-glass elevation (FR-349). Checked in the service layer, not by a route (`RL-1305` D1) |  |
> | `admin:manage_environments` | The Environment record's lifecycle: create, rename, retire (`07` FR-428). Not its settings, which are `admin:manage_settings`. Its route, WK-674 Slice 2's, is its first check |  |
>
> **Mapped: the same capability under two names; the code's name survives.**
> `rating_version:submit` (the Pricing Actuary set above) is `rating:submit`.
> `custom_objective:submit` was already superseded by `model:submit` (the note above, and
> FR-367). The deploy permission is ruled separately, in ~~the WK-674 ruling~~ `RL-1232` DP-6
> *(2026-09-29)*: it is `deployment:promote`. The spec name is
> kept in this note as the alias for one release: no code ever carried it, so there is no
> code alias to keep.
>
> **Coarse write rights are the Phase 2 catalogue (decided 2026-09-28, `RL-1236` DP-A):**
> `rating_algorithm:write` and `rate_table:write` are `rating:write`, which also covers creating
> a Rating Version, and writing Sub-graphs and Regression Suites (`RL-1309` DP-S1-1). `factor:write`, `banding:write` and `grouping:write` are `model:fit`, which
> also covers fitting. `dataset:create_version` is `dataset:write`, which also covers
> datasets, blobs, validation rules and ingestion. The per-artifact split in the role example
> above is carried to WK-676 (Phase 3, scoped assignments).
>
> **Names used before, and the enum name each maps to** *(added 2026-09-30, `RL-1305` item D4: the aliases of the notes above, as a table the gate check reads)*:
>
> | Name used before | Enum name |
> |---|---|
> | `rating_version:submit` | `rating:submit` |
> | `custom_objective:submit` | `model:submit` |
> | `rating_algorithm:write` | `rating:write` |
> | `rate_table:write` | `rating:write` |
> | `factor:write` | `model:fit` |
> | `banding:write` | `model:fit` |
> | `grouping:write` | `model:fit` |
> | `dataset:create_version` | `dataset:write` |
>
> **One approval permission (decided 2026-09-28, `RL-1236` DP-C):** `approval:decide`. Which
> roles may approve an artifact type is the `ApprovalPolicy` entry's `approver_roles` (§4.2),
> and from Phase 3 also the scope of the assignment. There are no per-type `*:approve`
> permissions.
>
> **Specified and not yet built, carried to the Work that builds it.** A name here is **not**
> an enum member. Its row moves to the table above in the commit that adds the member and its
> check *(table form 2026-09-30, `RL-1305` item D4)*:
>
> | Permission | Owner Work |
> |---|---|
> | `monitor:write` | WK-687 |
> | `alert:acknowledge` | WK-688 |
> | `alert:resolve` | WK-688 |
> | `optimisation:run` | WK-684 |
> | `optimisation:materialise` | WK-686 |

### 4.2 `ApprovalPolicy` (workspace defaults)

```json
{
  "policies": [
    {"artifact_type": "validation_rule", "approvers_required": 1,
     "approver_roles": ["approver", "admin"], "evidence": ["dry_run_result"]},
    {"artifact_type": "custom_objective", "approvers_required": 1,
     "approver_roles": ["approver"], "evidence": ["objective_certificate"]},
    {"artifact_type": "custom_metric", "approvers_required": 1,
     "approver_roles": ["approver"], "evidence": ["metric_certificate"]},
    {"artifact_type": "model", "approvers_required": 1,
     "approver_roles": ["approver"],
     "evidence": ["diagnostics", "transparency_artifact_if_non_glm", "model_comparison_if_predecessor"]},
    {"artifact_type": "peril_structure", "approvers_required": 1,
     "approver_roles": ["approver"], "evidence": ["reconciliation"]},
    {"artifact_type": "rating_version", "approvers_required": 2,
     "approver_roles": ["approver"],
     "evidence": ["structural_diff", "rate_table_diffs", "regression_run", "dislocation_run", "gipp_check_if_enabled", "change_summary"]},
    {"artifact_type": "deployment", "environment": "prod", "approvers_required": 1,
     "approver_roles": ["deployer"],
     "evidence": ["rating_version_approval", "uat_deployment"],
     "skippable_predecessors": []}
  ],
  "expedited": {"enabled": true, "approvers_required": 1,
                "requires_reason": true, "reported_in_exception_log": true},
  "separation_of_duties": {"submitter_may_approve": false, "configurable": false}
}
```

`separation_of_duties.configurable: false` is deliberate and is not a placeholder (R1).

> **A non-convex Custom Objective needs the policy's count plus one, and that is not a policy
> key** (`02` FR-152; added 2026-10-04, `RL-1362` DP-S3-4). When the latest
> certificate of a submitted `custom_objective` version has a `convexity` check with status
> `violated`, the request's `approvers_required` is the matching entry's `approvers_required`
> plus one. That is two under the defaults above and three under a policy of two. It applies to
> both objective kinds. When FR-385 is built, it applies to the expedited count too. It is
> stored on the request row (§4.3) at submission, and no policy can configure it, for R1's
> reason: a rule that a policy edit can remove is not a rule. It replaces the entry's former
> `"escalation": {"when": "certificate.convexity == 'violated'", "approvers_required": 2}`. That
> was an absolute count, which added nobody under a policy of two, and the model never accepted
> it (`FD-1281`).

> **The `deployment` entry in `DEFAULT_POLICY`, dated 2026-10-03 (WK-674 Slice 2; `RL-886`).** The `deployment` entry above, for `prod`, is added to `DEFAULT_POLICY` in `model-schema` by this slice. `RL-886` ruled that the spec was right and the code was one entry short: §3.3's floor already names `deployment` (FR-364), and `submit` refused a Deployment Request with "no approval policy for this artifact type" for want of the entry. Its `environment` is an Environment's slug (`07` §4.2).

> **`skippable_predecessors`, dated 2026-10-03 (WK-674 Slice 2; `RL-1296`).** The `prod` entry above carries the field that `OQ-1234` decided (`03` FR-429; `07` FR-429's amendment of 2026-09-30). It names the predecessor Environment slugs a deployment into the entry's environment may skip, and is empty by default, so no skip is permitted until a workspace lists one. `ApprovalPolicyEntry` refuses a non-empty value unless the entry's `artifact_type` is `deployment` and it names an `environment`: an unqualified entry applies to every environment, and a skip listed there would grant one to all of them. The reason for a skip is always required and is not configurable; it is the `uat_deployment` evidence item's `PromotionSkip.reason` (`03` §4.12).

> **`risk_tier` joins the entry shape in Phase 3 with FR-365** (OQ-636, decided
> 2026-08-18): an entry may carry `"risk_tier": 1`, and an entry **without** one applies to
> every tier. That default is what keeps this document true as written — the defaults above
> gain nothing and lose nothing, and a workspace that never tiers a Model Family sees no
> change at all. Tier is read from the artifact's Model Family or Rating Algorithm, never
> from the version under approval.

> **These defaults sit on top of §3.3's floor, and may only add to it (FR-364, OQ-639 decided
> 2026-08-18).** An entry whose `evidence` omits a floor kind for its artifact type is refused when
> the policy is saved. The enforced floor is: `validation_rule` — `dry_run_result`;
> `custom_objective` — `objective_certificate`; `custom_metric` — `metric_certificate`; `model` —
> `diagnostics` and `transparency_artifact_if_non_glm`; `rating_version` — `structural_diff`,
> `regression_run` and `dislocation_run`; `deployment` — `rating_version_approval` and
> `uat_deployment`. `peril_structure` has an **empty** floor — not for want of a §3.3 row, which it
> has had since 2026-08-14, but because its reconciliation half is enforced structurally and its
> per-peril approvals half is unqueryable. Submission checks the union of the floor and the entry,
> so an older stored policy cannot sit below it either.
>
> *(Corrected 2026-08-29, WK-671 Slice 2. This restatement named four artifact types while the
> enforced floor held six, so mechanism (i) — the reader of the defaults sees what they may not
> drop below — was two thirds true; and it still carried the "`peril_structure` has no §3.3 row"
> premise that FR-364's own 2026-08-22 amendment had already withdrawn. Ruled in `docs/rulings/RL-00885-finding-1-the-rating-version-evidence-floor-stands-the-specification-is-the-side-that-moves.md` RL-885.)*
>
> **Which is also where this document was ahead of the build, recorded rather than quietly aligned
> (`CLAUDE.md` §0).** The `model` entry above lists `transparency_artifact_if_non_glm` and
> `model_comparison_if_predecessor`; `DEFAULT_POLICY` in `model-schema` shipped `diagnostics` alone,
> and the `rating_version` entry above lists six kinds against the three it ships. The **defaults in
> code were right for the day they were written** — an uncheckable kind fails closed (R4), so a
> default naming `model_comparison_if_predecessor` would have refused every model submission — and
> the page was right about the destination. FR-364 is what reconciles them: the checkable kinds
> become the enforced floor and move into `DEFAULT_POLICY`, the rest keep their place here with an
> owner. `transparency_artifact_if_non_glm` is the kind's name on both sides from 2026-08-18; the
> submission check had been answering a kind it called `transparency_artifact`, so a workspace that
> copied the name off this page got a fail-closed refusal for evidence it had.

> **`peril_structure` added 2026-08-18 (WK-661, the peril-structure slice).** `02` FR-191
> has made a Peril Structure approvable since Phase 0, and `peril_structure` has been in
> `ARTIFACT_TYPES` for as long — but with no entry here, `submit` refuses it with "no
> approval policy for this artifact type". That is a *correct* refusal, which is what made
> it invisible: the machine was working exactly as FR-354 specifies, on an artifact
> nobody could ever approve.
>
> Its evidence is the **reconciliation**, because `02` FR-190 makes that the coherence
> check an approver is being asked to accept. It is enforced structurally as well as by
> policy: `reconciled` is the only state with an edge into `review`, and a reconciliation
> whose status is `fail` is refused at submission — the tolerance is the submitter's own
> declaration, so missing it is failing a test they set themselves.
>
> This is an **addition** to §3.3's evidence floor and removes nothing, so it sits inside
> OQ-639's recommendation rather than pre-empting it.

> **`custom_metric` added 2026-08-20 (WK-661, the custom-metrics slice).** `02` FR-154
> gives a Custom Metric the same lifecycle and grammar as a Custom Objective, and
> `platform.metrics._require_evidence` has expected this entry since the slice that added
> `submit` — but with no entry here, `certified -> review` refused with 409 in every
> workspace, on "no approval policy for this artifact type", before `_require_evidence` was
> ever reached. The approval lifecycle was unreachable without it, the same defect class as
> `peril_structure` above.
>
> Its evidence is the **metric certificate**, mirroring `custom_objective`'s
> `objective_certificate`, because `02` FR-157 makes certification the check an
> approver is being asked to accept.
>
> This is an **addition** to §3.3's evidence floor and removes nothing, so it sits inside
> OQ-639's recommendation rather than pre-empting it.

### 4.3 `ApprovalRequest` and `ApprovalDecision`

```json
{
  "artifact_ref": "rating_version:motor-gb@27",
  "artifact_type": "rating_version",
  "submitted_by": "uuid", "submitted_at": "2026-09-12T14:02:00Z",
  "change_summary": "AD frequency model refit on 2026H1 data; driver-age relativities softened at young ages; minimum premium raised to £280.",
  "expedited": false,
  "evidence_bundle": {
    "structural_diff": "blob:sha256:…",
    "rate_table_diffs": ["rate_table:motor-driver-age-relativity@5→@6"],
    "regression_run": "uuid",
    "dislocation_run": "uuid",
    "gipp_check": "uuid",
    "model_dossier": "dossier:motor-gb@27-v1"
  },
  "checklist": [
    {"item": "Dislocation reviewed with the pricing committee", "checked": true, "by": "uuid"},
    {"item": "GIPP check passing", "checked": true, "by": "uuid", "auto_verified": true},
    {"item": "Reinsurance impact considered", "checked": true, "by": "uuid"}
  ],
  "flags": [],
  "status": "review",
  "decisions": [
    {"approver_id": "uuid", "decision": "approved", "at": "2026-09-13T10:11:00Z",
     "comment": "Dislocation is within the agreed envelope; young-driver softening is supported by the refit and the GIPP evidence is clean."}
  ],
  "approvers_required": 2, "approvers_recorded": 1
}
```

### 4.4 `Dossier` structure

Generated sections, in order (R3). Each cites the artifacts it drew from.

| § | Section | Source |
|---|---|---|
| 1 | Purpose, scope, and intended use | Commentary Block (attributed) |
| 2 | Data — dataset versions, lineage, period, volumes | `01` Dataset Version, lineage |
| 3 | Data quality — validation report summary, acknowledged warnings and their justifications | `01` Validation Report |
| 4 | Factors — definitions, intents, bandings and groupings with methods and rationale | `02` Factor / Banding / Grouping |
| 5 | Model specification — type, family, link, offset, weights, objective (incl. custom objective and its certificate) | `02` Model Spec, Objective Certificate |
| 6 | Results — coefficients/relativities with standard errors, or booster summary | `02` Fit Result |
| 7 | Diagnostics — train vs holdout, A/E, lift, calibration, CV | `02` Diagnostics |
| 8 | Transparency — GLM approximation, SHAP summary, fidelity statement | `02` Transparency Artifact |
| 9 | Peril structure and reconciliation | `02` Peril Structure |
| 10 | Rating structure — DAG summary, rate tables, constraints, premium ladder | `03` Rating Algorithm, Rate Tables |
| 11 | Impact — dislocation, attribution, regression results | `03` Dislocation, Regression |
| 12 | Commercial — optimisation run, constraints, elasticities | `04` Optimisation Run |
| 13 | Compliance — GIPP evidence, price walking, fairness constraints and rationales | `04` GIPP Check |
| 14 | Monitoring plan and live performance to date | `05` Monitors, Results |
| 15 | Limitations and known issues | Commentary Block (attributed) |
| 16 | Approval history and attestations | This module |
| 17 | Appendix — artifact references with content hashes | All |
| 18 | Regulatory considerations — material factors arising from customer-outcome obligations, and what was allowed for | Commentary Block (attributed), FR-362 |
| 19 | Assumption consistency — material assumptions against those used for business planning, reserving and capital, and any material inconsistency | Commentary Block (attributed), FR-362 |

> **18 and 19 added 2026-08-18 with FR-362** (OQ-638), appended rather than slotted in beside §13's compliance material because the numbers are cited from other documents and behave like every other identifier here (`CLAUDE.md` §5). They carry TAS 200 v2.0's P1.1 and P1.2/P1.4 respectively.
>
> **They are not part of FR-378's mandatory two**, and the distinction is deliberate rather than an oversight. FR-378 governs what an *approver* must be given before a submission is accepted, and the answer stays exactly two blocks. These two serve a different reader — someone assessing the work against TAS 200 — so they are required for a dossier to be **complete for that purpose**, and a workspace outside the standard's geographic or membership scope may leave them empty without blocking an approval. Making them mandatory at submission would have quietly turned "exactly two" into four, which is the boilerplate slope OQ-637 was decided to avoid.

### 4.5 `AuditEvent`

```json
{
  "id": "01J…",
  "workspace_id": "uuid",
  "at": "2026-09-13T10:11:00.482Z",
  "actor": {"kind": "user", "id": "uuid", "display": "a.actuary@insurer.example"},
  "source": "ui",
  "action": "rating_version.approved",
  "entity_ref": "rating_version:motor-gb@27",
  "before": {"status": "review", "approvers_recorded": 1},
  "after": {"status": "approved", "approvers_recorded": 2},
  "justification": "Dislocation within the agreed envelope; GIPP clean.",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "job_id": null,
  "prev_event_hash": "sha256:…",
  "event_hash": "sha256:…"
}
```

*`entity_ref` names the subject of the event: an `ArtifactRef` when the subject is an artifact, a scoped `type:name` otherwise. *(Recorded 2026-08-26, OQ-653.)*

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/me` | Current principal, roles, effective permissions |
| `GET` | `/api/v1/me/workspaces` | The principal's own memberships, unscoped — the list first selection chooses from (FR-396) |
| `POST` | `/api/v1/me/workspace` | Audits a switch into both chains; an absent `Workspace-Id` is `left=None`, the first selection (FR-396) |
| `GET`/`POST` | `/api/v1/roles` | List / create roles (FR-344) |
| `POST` | `/api/v1/role-assignments` | Assign a scoped role (FR-345) |
| `POST` | `/api/v1/break-glass` | Time-boxed elevation with reason (FR-349) |
| `GET`/`PUT` | `/api/v1/approval-policy` | Read / update the workspace policy (FR-354) |
| `POST` | `/api/v1/approval-requests` | Submit an artifact; validates evidence and checklist (FR-352) |
| `GET` | `/api/v1/approval-requests?assigned_to=me&status=review` | Approvals inbox (FR-358) |
| `GET` | `/api/v1/approval-requests/{id}` | Request with resolved evidence inline |
| `POST` | `/api/v1/approval-requests/{id}/decide` | `approve` / `reject` / `request_changes` + comment (FR-353/355) |
| `POST` | `/api/v1/approval-requests/{id}/withdraw` | Withdraw before deployment (FR-357) |

> **Permissions on this table, stated 2026-08-15 after an independent audit.** Four of
> these six require **authentication only**, and nothing said so — a route sweep found them
> answering a principal holding no roles at all, which read as a hole until the handlers
> were read.
>
> | Route | Requires |
> |---|---|
> | `POST /approval-requests` | authenticated |
> | `GET /approval-requests` | authenticated |
> | `GET /approval-requests/{id}` | authenticated |
> | `GET /approval-policy` | authenticated |
> | `POST …/decide`, `POST …/withdraw` | `approval:decide` |
> | `PUT /approval-policy` | `admin:manage_roles` |
>
> **Submitting is asking.** The module owning the artifact has already decided whether this
> principal could create it; gating the ask as well would stop an analyst who built a model
> from putting it forward. Reading the queue and the policy follow from FR-358's purpose:
> an approvals inbox that only approvers could see would hide from a submitter what is
> waiting on whom, and the policy is the rule everyone is being held to.
>
> All four remain **workspace-scoped** — a caller sees their own workspace and no other —
> and none of them decides anything. The deciding routes carry `approval:decide`, and
> FR-353's separation of duties is enforced in three independent layers, database
> constraint included.
| `POST` | `/api/v1/attestations` | Record a periodic review (FR-361) |
| `GET` | `/api/v1/audit?actor=&entity=&action=&from=&to=&q=` | Query the audit log (FR-371) |
| `GET` | `/api/v1/audit/verify?from=&to=` | Verify the hash chain (FR-372) |
| `POST` | `/api/v1/audit/anchor` | Export a signed chain head for external anchoring (FR-373) |
| `GET` | `/api/v1/audit/export` | Export CSV/JSON |
| `POST` | `/api/v1/dossiers` | **202** Generate a dossier for an artifact (FR-376) |
| `GET` | `/api/v1/dossiers/{id}?format=html\|pdf\|bundle` | Render / export (FR-379) |
| `POST` | `/api/v1/dossiers/{id}/commentary` | Add/update an attributed Commentary Block (FR-377) |
| `POST` | `/api/v1/regulatory-exports` | **202** Point-in-time evidence archive (FR-382) |
| `GET` | `/api/v1/artifacts/{ref}/history` | Uniform history view (FR-383) |
| `GET` | `/api/v1/artifacts/{ref}/dependencies?direction=up\|down` | Blast radius (FR-384) |

**Error codes owned by this module:** `PERMISSION_DENIED`, `SCOPE_DENIED`,
`SUBMITTER_CANNOT_APPROVE`, `AUTHOR_CANNOT_APPROVE`, `APPROVAL_AUTHOR_UNRESOLVED`,
`APPROVAL_SUBJECT_NOT_IN_REVIEW`, `APPROVAL_BY_EVIDENCE_AUTHOR`,
`DUPLICATE_APPROVER`, `EVIDENCE_INCOMPLETE`,
`POLICY_BELOW_EVIDENCE_FLOOR`, `CHECKLIST_INCOMPLETE`, `ARTIFACT_FLAGGED`,
`APPROVAL_PINNED_ARTIFACT_CHANGED`, `APPROVAL_ALREADY_DECIDED`,
`WITHDRAW_AFTER_DEPLOY_FORBIDDEN`,
`BREAK_GLASS_REASON_REQUIRED`, `AUDIT_CHAIN_BROKEN`, `ATTESTATION_OVERDUE`,
`ARTIFACT_TYPE_NOT_RESOLVABLE`, `APPROVAL_OUTSIDE_DECISION_PATH`. *(`APPROVAL_BY_EVIDENCE_AUTHOR` added 2026-09-28, `PL-1189`,
the deputy's decision on audit finding F4: 403, FR-353's golden-quote delta rule. `APPROVAL_OUTSIDE_DECISION_PATH` added 2026-09-30, `PL-1303` (WK-674 Slice 2a), `RL-1301` A.4.2: **500**, the database's refusal of an `approved` write that did not come through the decision path: a backstop no client request can reach, so reaching it is a defect in the platform's own code and is logged at ERROR with the table and ref, not a permission problem as a 403 would say.)*

### 5.2 Backend service interfaces

Governance is backend-side; it has no `pricing-core` surface (it contains no actuarial
maths — ADR-703).

```python
# backend/app/governance/authz.py
def require(principal: Principal, permission: str, resource: ArtifactRef) -> None
def effective_permissions(principal: Principal) -> set[str]

# backend/app/governance/approvals.py
async def submit(artifact: ArtifactRef, submitter: Principal,
                 change_summary: str, checklist: Checklist) -> ApprovalRequest
async def decide(request_id: UUID, approver: Principal,
                 decision: Decision, comment: str) -> ApprovalRequest

# backend/app/governance/audit.py
async def emit(session: AsyncSession, event: AuditEventDraft) -> AuditEvent
   # MUST be called inside the caller's transaction (R2)

# backend/app/governance/dossier.py
async def generate(artifact: ArtifactRef, as_at: datetime | None) -> Dossier
```

### 5.3 Frontend views

| View | Route | Contents |
|---|---|---|
| Approvals inbox | `/approvals` | Pending requests with artifact type, submitter, age, flags; evidence rendered inline (diffs, dislocation charts, diagnostics) so no context-gathering is needed |
| Approval detail | `/approvals/:id` | Evidence bundle, checklist, flags, decision panel with mandatory comment, prior decisions and change requests |
| Audit explorer | `/audit` | Filterable timeline, entity-centric view, justification search, chain verification status, export |
| Artifact history | `/artifacts/:ref/history` | Uniform version/transition timeline with diffs and actors |
| Dependencies | `/artifacts/:ref/dependencies` | Blast-radius graph in both directions |
| Dossier | `/dossiers/:id` | Rendered document with generated content and clearly-marked commentary; regenerate-as-at control; export buttons |
| Roles & access | `/admin/access` | Roles, permission matrix, scoped assignments, break-glass grants and their expiry |
| Attestations | `/attestations` | Live artifacts with review status and overdue flags |

**Interaction requirement:** the approval detail view is where the platform earns its
keep. An Approver must be able to make a defensible decision without opening another
module — that means dislocation charts, diagnostics, and diffs rendered in place, not
linked away.

---

## 6. Workflows

| Step | Actor | Action |
|---|---|---|
| 1 | Analyst / Pricing Actuary | Completes work on a governed artifact |
| 2 | Frontend → Backend | `POST /approval-requests` — evidence and checklist validated (FR-352) |
| 3 | Backend | Resolves and pins the evidence bundle; emits an Audit Event; notifies eligible Approvers |
| 4 | Approver | Opens the inbox, reviews inline evidence |
| 5a | Approver | `request_changes` with a comment → artifact returns to its pre-submission state (FR-355) — `draft` for most types, `fitted` for a Model; a Deployment Request, which has no pre-submission state, ends `rejected` (FR-355, amended 2026-10-04). |
| 5b | Approver | `approve` with a comment → decision recorded, separation of duties enforced (R1) |
| 6 | Backend | On the final required approval, transitions the artifact and emits Audit Events |
| 7 | Deployer | For a Rating Version, deploys (`03` FR-267) — itself an audited, permissioned act |
| 8 | Backend | Periodically flags overdue attestations on live artifacts (FR-361) |

Governance appears in every workflow document; the custom-objective path is the most
governance-heavy: [`WF-702-custom-objective-lifecycle.md`](../workflows/WF-00702-custom-objective-lifecycle.md).

---

## 7. Cross-module dependencies

### 7.1 Consumes

| From | What |
|---|---|
| `07-platform` | Authenticated principals **and their workspace memberships** (FR-395, FR-396 — the identity endpoint carries the list a selector renders), user directory/OIDC claims, notification channels, job identity for `system` audit events |

**Not a dependency:** the artifact states, evidence artifacts and flags that gate approval
(FR-359) are **pushed to** this module by `01`–`05` — they appear in those modules'
§7.2. Governance does not read their tables, which is what keeps DEP-1 intact.

### 7.2 Provides

| To | What |
|---|---|
| `01`–`05` | Permission checks, the approval workflow, the audit sink, and the flag surface |
| External reviewers / regulators | Dossiers and point-in-time evidence exports (FR-379/382) |

### 7.3 Contract note

Every module calls `governance.audit.emit` **inside its own transaction**. There is no
asynchronous audit path, no buffered audit queue, and no best-effort audit write (R2) —
this is the single most important integration rule in the platform.

---

## 8. Tech dependencies

| Component | Used for | Notes for `skills-map.md` |
|---|---|---|
| **PostgreSQL 16** | Audit log (append-only via privileges), approval state machines, role/permission tables | Revoking `UPDATE`/`DELETE` from the application role; `BEFORE UPDATE` triggers as belt-and-braces; partitioning the audit table by month; hash chaining in a trigger vs in application code |
| **SQLAlchemy 2.x (async)** | Transactional audit writes alongside domain changes | Ensuring the audit insert shares the caller's session and transaction (R2); avoiding autocommit surprises |
| **FastAPI dependencies** | Permission enforcement as a dependency on every route | Dependency injection for the principal; failing closed by default; making an unprotected route impossible to write by accident |
| **OIDC claims (via `07`)** | Mapping external groups to platform roles | Claim-to-role mapping configuration, group sync, and why platform roles remain the authority |
| **WeasyPrint / Typst (PDF)** | Dossier rendering to PDF | Deterministic rendering, embedded fonts, chart images from the same data as the UI, reproducible output for the same artifact set |
| **Jinja2 or a typed template layer** | Dossier HTML assembly | Keeping generated content and commentary structurally distinct (R3) |
| **Content hashing** | Audit chain, artifact references, export integrity | Canonical JSON serialisation so a hash is stable across processes and versions |

New skills this spec adds to `skills-map.md`: append-only tables via PostgreSQL
privileges and triggers; hash-chained audit logs; deterministic PDF generation;
separation-of-duties enforcement patterns in a web API.

---

## 9. Non-functional requirements

| ID | Requirement |
|---|---|
| **NFR-518** | Permission checks add < 5 ms to a request, using a cached effective-permission set invalidated on assignment change. |
| **NFR-519** | Audit writes never fail silently: an audit write failure rolls back the domain change (R2). |
| **NFR-520** | Audit queries over 100 M events return a filtered page in < 2 s, supported by partitioning and indexes on `(workspace_id, at)`, `(entity_ref)`, `(actor_id)`. |
| **NFR-521** | Audit retention ≥ 7 years (NFR-459); the hash chain is verifiable over the whole retained range. |
| **NFR-522** | Dossier generation for a full Rating Version completes in < 2 min and is byte-reproducible for the same artifact set and template version. |
| **NFR-523** | A regulatory export for a one-year range assembles in < 30 min and is self-contained (verifiable without platform access). |
| **NFR-524** | The approvals inbox loads in < 1 s with evidence summaries; full evidence renders progressively. |
| **NFR-525** | Separation of duties, append-only audit, and permission enforcement are covered by explicit negative tests in CI — the test suite must prove that a submitter *cannot* approve, not merely that an approver can. |

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-633** | ~~Audit hash chain: per workspace or global, and is a self-held chain enough?~~ **DECIDED 2026-08-18: per workspace, self-held, described as tamper-evident rather than tamper-proof, with an explicit chain-head anchor operation the customer automates into a store the operator does not control — FR-373.** |
| **OQ-634** | ~~Are platform roles authoritative, or is IdP group membership?~~ **DECIDED 2026-08-18: hybrid — the IdP owns identity and role membership so a leaver loses access automatically; the platform owns artifact scope, which names objects no directory has heard of — FR-350.** |
| **OQ-635** | ~~Can an Admin override a flag (FR-359)?~~ **DECIDED 2026-08-18: yes, and it leaves a scar — two Admins, a written justification, a badge on the artifact that never expires, the exception log, and its own line in the approval history — FR-360.** An override never clears the underlying flag. |
| **OQ-636** | ~~Do we need formal model risk tiering?~~ **DECIDED 2026-08-18: yes — `risk_tier` on Model Family and Rating Algorithm, which `ApprovalPolicy` entries may key on — FR-365.** On the family and the algorithm rather than the version, so it cannot be lowered on the day a quicker approval is wanted. |
| **OQ-637** | ~~How much commentary is required before an approval can be submitted?~~ **DECIDED 2026-08-18: exactly two Commentary Blocks — §4.4 §1 and §15 — with a minimum length and no default text to accept — FR-378.** Ten mandatory slots produce ten paragraphs of boilerplate; two produce two paragraphs somebody wrote. |
| **OQ-638** | ~~Does TAS 200 (Insurance) cover pricing and premium rating, or only reserving, capital and Solvency II actuarial-function work?~~ **DETERMINED 2026-08-18 by reading TAS 200 v2.0: it applies, through the `Pricing frameworks` scope item, whose glossary definition names the methodologies, assumptions and models behind an insurer's premium rates — FR-362.** No pricing-specific provisions section exists, so §1's P1.1–P1.4 bind, plus TAS 100. |
| **OQ-639** | ~~Does `06` §3.3's per-artifact evidence table or `06` §4.2's `ApprovalPolicy` defaults decide what a submission actually requires?~~ **DECIDED 2026-08-18: §3.3 is a floor per artifact type and §4.2 may only add to it — FR-364**, with the floor restated in §4.2 so a reader of the defaults sees it, refused at policy save, and applied as a union at submission. The enforced floor is §3.3's checkable projection; the uncheckable remainder is named with an owner. |
| **OQ-632** | ~~Does an `expression` Custom Objective (Phase 2, `02` FR-150) need an authoring permission distinct from `model:fit`?~~ **DECIDED 2026-08-18: yes — `custom_objective:author`, granted by no built-in role's default set — FR-367**, discharging FR-366's trigger before WK-690 rather than at it. Template selection stays `model:fit`; submission stays `model:submit`. |
| **OQ-1486** | **OPEN** — **Is a Validation Rule Set a Governed Artifact?** §2 (`:64`) lists Validation Rule, but not Rule Set. `replace_rule_set` publishes each set version `approved` with no review, so a new version can drop member rules or re-point the Reference Dataset Version unreviewed. Raised 2026-09-30 by the decision-maker (`RL-1485`). Mirrored in `docs/open-questions.md`. *Amended 2026-10-05 before mint (currency only, at `47d770e8`): the cites above are at `65b33479`; at `47d770e8` they are `validation_rules.py:549` (`replace_rule_set`), `:654` (`status=APPROVED`), `models.py:1247` and `validation.py:400-432`. `RL-1407` (#1109) has since ruled that a rule set runs only approved, existing members (FD-1414; delivered by `SL-1409`, not yet in the code); that does not review a change of composition, and the options are not re-weighed here (`RL-1485` J2).* Status: **open** (owner WK-1178). |
