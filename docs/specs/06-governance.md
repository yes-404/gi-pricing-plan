# 06 — Governance

**Status:** draft · **Phase:** 0 (specification) · **Module code:** `GOV`
**Prerequisites:** [`00-overview.md`](00-overview.md) §1.4 (actors), §3 (FR-OVR-1/4/14).

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
> database transaction as the change (FR-OVR-4) — if the audit write fails, the change
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
| **Permission** | An atomic `(action, resource_type)` capability, e.g. `model:approve`, `dataset:acknowledge_warning`, `rating_version:deploy_prod`. |
| **Scope** | The subset of artifacts a role assignment applies to: workspace-wide, or restricted to named Datasets, Model Families, or Rating Algorithms (e.g. a motor actuary who cannot approve home pricing). |
| **Governed Artifact** | Any artifact with an approval-bearing lifecycle: Dataset Version, Validation Rule, Model, Custom Objective, Custom Metric, Peril Structure, Rate Table Version, Rating Version, Optimisation Run (when cited as evidence). |
| **Evidence Bundle** | The set of artifact references required for that artifact type (§3.3), resolved and pinned at submission time. |
| **Approval Policy** | The workspace configuration stating, per artifact type and environment, how many approvers are needed, which roles may approve, and what evidence is required. |
| **Approval Decision** | An approve / reject / request-changes act by an Approver, with a mandatory comment. |
| **Attestation** | A periodic, recorded confirmation by a named role that a live artifact remains fit for purpose (annual model review). |

---

## 3. Functional requirements

### 3.1 Identity, roles, permissions

| ID | Requirement |
|---|---|
| **FR-GOV-1** | Every API call resolves to a Principal. Anonymous access exists only for health checks and the OpenAPI document. |
| **FR-GOV-2** | Permissions are checked in the backend on every request against `(principal, permission, resource, scope)`. The frontend hides what a user cannot do; it never *enforces* it. |
| **FR-GOV-3** | The platform ships the roles from `00` §1.4 (Analyst, Pricing Actuary, Approver, Deployer, Auditor, Admin) with documented default permission sets, and supports custom roles composed from the same permission vocabulary. |
| **FR-GOV-4** | Role assignments are **scoped**: workspace-wide, or limited to named Datasets, Model Families, or Rating Algorithms — so a motor actuary cannot approve home pricing without an explicit assignment. |
| **FR-GOV-5** | The **Auditor** role is read-everything, write-nothing, including access to the audit log, superseded artifacts, and archived datasets. No role, including Admin, can hide an artifact from an Auditor. |
| **FR-GOV-6** | Service Accounts (for Consumer Systems) hold scoring permissions only, scoped to named environments, with credentials issued and rotated per `07-platform.md`. A Service Account can never hold an approval or deployment permission. |
| **FR-GOV-7** | Permission changes, role creation/edit, and role assignment are themselves audited and require the `admin:manage_roles` permission. A user cannot grant themselves a permission they do not hold. |
| **FR-GOV-8** | **Break-glass** access (emergency elevation) is supported as a time-boxed, reason-required, immediately-notified grant that expires automatically and is prominently flagged in the audit log. |
| **FR-GOV-41** | **Identity and role membership are the identity provider's; artifact *scope* is the platform's.** (OQ-GOV-2, decided 2026-08-18; **Phase 3**.) An IdP group maps to a platform Role by configuration (`07` FR-PLAT-4), so a leaver removed from the group loses platform access without anyone here remembering to act — which is the requirement large insurers actually impose, and the one a platform-authoritative model quietly fails. **Scope (FR-GOV-4's dataset, model-family and rating-algorithm restrictions) is assigned in-platform and never inferred from a group**, because scope names artifacts that exist here and nowhere else: an IdP administrator cannot express "motor-* but not household-*" against objects their directory has never heard of, and a mapping that pretended otherwise would silently widen access whenever a new model family was created. The two halves fail differently on purpose: a group that maps to no Role grants **nothing** (FR-PLAT-4), and a principal whose Role is granted but whose scope is unassigned holds the role's permissions over **no artifacts** rather than over all of them. Both defaults are closed, and the second is the one an implementation gets wrong. |

### 3.2 Approval workflow

| ID | Requirement |
|---|---|
| **FR-GOV-9** | The approval lifecycle is uniform across artifact types: `draft → review → (approved \| changes_requested \| rejected)`. Post-approval states (`live`, `superseded`, `retired`) belong to the owning module but are governed by the same audit rules. |
| **FR-GOV-10** | Submission requires: a complete Evidence Bundle (§3.3), a change summary, and a completed checklist for that artifact type. Missing items block submission with a field-level explanation (R4). |
| **FR-GOV-11** | **Separation of duties**: the submitter cannot approve, and where two approvals are required they must be distinct Principals (R1). Enforced in the backend. |
| **FR-GOV-12** | An **Approval Policy** per workspace defines, per artifact type (and per target environment for Rating Versions): required approver count, permitted approver roles, and required evidence. Defaults are specified in §4.2. |
| **FR-GOV-13** | `changes_requested` returns the artifact to **its pre-submission state** and requires a comment. The request and the subsequent resubmission are both audited, so a reviewer's concerns and their resolution are traceable. *(Amended 2026-08-17, W5. This said `draft`, and for a Model that is wrong: `02` uses `draft` for a specification reserved but not yet fitted, and `02` R2 makes a fitted model's coefficients immutable — so a model returned from review cannot un-fit, and `draft` would describe an artifact with numbers as one without. A Model returns to `fitted`; `rejected` and `withdrawn` return it there too. For artifact types whose pre-submission state **is** `draft`, nothing changes. **Extended 2026-08-18, W5: a Custom Objective returns to `certified`**, for the same reason and with a sharper edge — a certificate is pinned to the objective version (`02` FR-MODEL-42), the version did not change when an approver asked for one, and returning it to `draft` would discard evidence that is still valid and make re-certification the price of a comment.)* |
| **FR-GOV-14** | Approvals are **pinned**: the decision records the exact artifact version and evidence artifact ids. If any referenced artifact changes, the approval does not carry over — a new version needs a new approval (FR-OVR-1). |
| **FR-GOV-15** | An approval can be **withdrawn** before deployment by an Approver or an Admin with a reason; it cannot be withdrawn after the artifact is live (the correct action is then a rollback or a new version). |
| **FR-GOV-16** | The **Approvals inbox** shows each Approver their pending requests with the evidence inline — diffs, diagnostics, dislocation, GIPP — so review does not require assembling context by hand. |
| **FR-GOV-17** | Flags raised elsewhere propagate into the approval surface: `dataset_invalidated` (`01` FR-DATA-23), missing transparency artifact (`02` R3), unapproved custom objective (`02` R4), failing GIPP (`04` R4). A flagged artifact cannot be approved until the flag is cleared or explicitly overridden by an Admin with a recorded justification. |
| **FR-GOV-42** | **An Admin may override a flag, and the override is built to be expensive and permanent: `admin:manage_roles`-held Admin only, a mandatory written justification, **two** distinct Admins, a badge on the artifact that never expires, an entry in the exception log (FR-GOV-35), and its own line in the dossier's approval history (§4.4 §16).** (OQ-GOV-3, decided 2026-08-18; **Phase 3**.) Refusing overrides outright is the cleaner rule and the wrong one: flags come from other modules and can be *false* — a dataset invalidated and since re-validated, a transparency artifact whose generation job failed — and a governance system with no recourse gets bypassed outside itself, in a spreadsheet nobody audits. So the escape hatch exists **and leaves a scar**: the artifact carries `flag_overridden` for the rest of its life, not merely a line in a log that has to be searched for. **The permanence is the requirement, not the ceremony.** Two approvers and a justification make an override deliberate; only the permanent badge makes it *visible to the next reader*, who is the person an auditor will ask why this model was approved with a flag raised against it. An override is never a way to clear a flag: the underlying condition stays raised, and re-running the check is the only thing that lowers it. |
| **FR-GOV-18** | **Attestation**: governed artifacts that are live can carry a periodic review requirement (default annual). An overdue attestation is surfaced on the artifact, in the inbox, and in monitoring dashboards — it does not automatically retire anything. |
| **FR-GOV-45** | **TAS 200 (Insurance) v2.0 *does* apply to this platform's work, through its `Pricing frameworks` scope item — determined 2026-08-18 by reading the standard, not assumed.** (OQ-GOV-6, decided 2026-08-18; the obligations land in **Phase 3** with the dossier.) §1.2 of TAS 200 v2.0 lists *"Pricing frameworks — Technical actuarial work to support pricing frameworks"* among the work in scope, and its glossary defines a pricing framework as the product pricing principles **and the methodologies, assumptions and models implementing those principles** that support an insurer's premium rates or product charges. `insurer` is defined as any undertaking effecting or carrying out contracts of insurance or reinsurance, with no life/general split — so general insurance premium rating is not excluded, and the models, assumptions and rationale this platform produces are framework components by the standard's own definition. It applies to work completed on or after **1 January 2025** (§1.3), and TAS 200 work is also TAS 100 work (§1.4). **The unit of scope is the framework, not the quote:** a scoring call is not technical actuarial work, and nothing here implies otherwise. **There is no pricing-specific provisions section** — sections 2–6 cover valuation, capital, transformations, audit and with-profits — so what binds is §1, *Provisions for all work in scope*: P1.1 (consider and **document** material factors from customer-outcome obligations, which is where Consumer Duty enters), P1.2 (assumptions consistent with those used for other purposes — business planning, reserving, capital), P1.3 (a persistent gap between actual experience and assumed must be considered and documented), P1.4 (communications describe material inconsistencies). §4.4 gains sections **18** and **19** to carry P1.1 and P1.2/P1.4 respectively — appended, never inserted, because section numbers here are identifiers (`CLAUDE.md` §5). |

### 3.3 Required evidence by artifact type

| ID | Requirement |
|---|---|
| **FR-GOV-19** | Required evidence is defined per artifact type and enforced at submission (R4): |

| Artifact | Required evidence |
|---|---|
| **Dataset Version** → `validated` | Validation Report with no `fail`; every `warn` acknowledged with justification (`01` FR-DATA-17) |
| **Validation Rule** | Successful dry-run result against a real Dataset Version (`01` FR-DATA-21) |
| **Custom Objective** | Objective Certificate with `overall ≠ failed`; applicability declaration; usage impact if a new version of an in-use objective (`02` FR-MODEL-42/47) |
| **Custom Metric** | Metric Certificate with `overall ≠ failed` (`02` FR-MODEL-45/105/108) |
| **Model** | Diagnostics (train + holdout); transparency artifact where non-GLM; model comparison where a predecessor exists; factor/banding/grouping rationale; dataset lineage (`02` FR-MODEL-64) |
| **Peril Structure** | Per-peril model approvals; reconciliation result within tolerance (`02` FR-MODEL-60) |
| **Rate Table Version** | Change note; diff vs previous; diff vs technical seed where seeded (`03` FR-RATE-16/17) |
| **Rating Version** | Structural diff; rate table diffs; passing regression suite; dislocation run with attribution; GIPP check where enabled; change summary (`03` FR-RATE-40) |
| **Deployment to `prod`** | A complete Rating Version approval; a successful `uat` deployment; Deployer permission (`03` FR-RATE-50) |

> **`custom_metric` added 2026-08-22 (W5, the audit-remediation slice).** §4.2's
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
> projection of this row and leaves FR-GOV-37 no remainder to name.

| ID | Requirement |
|---|---|
| **FR-GOV-37** | **The table above is a floor. §4.2's `ApprovalPolicy` may add to it and may never remove from it.** (OQ-GOV-7, decided 2026-08-18.) The two tables have disagreed since Phase 0 and the code could only enforce one of them, because a check has to read a list and there were two. The deciding case is `02` §4.8 R3: a transparency artifact for a non-GLM model is an invariant of the artifact, not a workspace preference, and a policy edit that removes it is a mispricing waiting for an audit. Three mechanisms, so that neither table can be read alone: (i) the floor is restated in §4.2's own text, so a reader of the defaults sees what the defaults may not drop below — the objection to a floor was always that a submission refused for evidence the policy does not mention is an error nobody can act on; (ii) `PUT /api/v1/approval-policy` refuses an entry whose `evidence` omits a floor kind for that artifact type with `POLICY_BELOW_EVIDENCE_FLOOR`, naming the artifact type and the kinds, because a policy document that says less than it enforces misleads its reader; (iii) submission checks the **union** of the floor and the matching policy entry, so a policy stored before this requirement cannot dodge the floor by being old. **The enforced floor is the checkable projection of §3.3, and the remainder is named with an owner rather than asserted**: for `model` it is `diagnostics` and `transparency_artifact_if_non_glm`; `model_comparison_if_predecessor` stays out until a comparison names its models in a queryable column rather than inside `payload` (owner: the slice that adds it), and §3.3's factor/banding/grouping rationale is unmodelled (owner: Phase 1b). Submission continues to **fail closed** on any evidence kind it cannot verify (R4), so a tightened policy can never silently do nothing. An artifact type with **no §3.3 row has an empty floor** — `peril_structure` is that case — and a floor that says nothing permits anything, which is the right default for an artifact §3.3 predates rather than a gap to be filled by inference. **Amended 2026-08-22 (W5, the audit-remediation slice), on both halves.** `custom_metric` joins the floor with `metric_certificate`, §3.3 having gained the row that entry projects — the spec row first, because the entry alone would have put the code above its own specification. And the `peril_structure` sentence above rested on a false premise: §3.3 has carried a Peril Structure row since 2026-08-14, four days *before* this requirement was written, so "no §3.3 row" was never true of it. The empty floor survives the correction, for a reason the original did not give — the row's **reconciliation** half is enforced structurally, since `review` is reachable only from `reconciled` and a `fail` verdict is refused at submission, so a floor entry would restate a lifecycle edge rather than add a control. Its other half, **per-peril model approvals**, sits in `peril_structures.perils` as JSONB and cannot be queried, which is `model_comparison_if_predecessor`'s case exactly: naming it in the floor would fail every peril-structure submission closed on evidence nothing can verify. **Owner: W17**, which owns FR-GOV-9..19 and evidence enforcement, and is where a queryable per-peril approval projection belongs — an owner that is a workstream rather than "the slice that touches it next", which is a phrase. |
| **FR-GOV-43** | **A Model Family and a Rating Algorithm each carry a `risk_tier` (`1 \| 2 \| 3`, 1 the most material), and `ApprovalPolicy` entries may key on it — approver count, evidence, and attestation cadence (FR-GOV-18).** (OQ-GOV-4, decided 2026-08-18; **Phase 3**, and previously deferred there.) Tiering is how UK insurer model governance already works, and per-artifact-type policy cannot express it: `artifact_type: model` treats a headline motor frequency model and a windscreen burning-cost model as the same risk, so a workspace wanting two approvers on the first has to impose them on both and then watch the requirement be resented into irrelevance. **The tier sits on the *family* and the *algorithm*, never on the version**, so it is a standing statement about a line of business rather than a per-fit judgement someone could set to 3 on the day they need a quicker approval; changing it is itself audited (FR-GOV-20). It **extends** the policy shape rather than replacing it — an entry with no `risk_tier` applies to every tier, so FR-GOV-37's floor and the §4.2 defaults keep working unchanged and a workspace that never tiers anything sees no difference. |
| **FR-GOV-38** | **`model:fit` governs Custom Objectives for as long as the catalogue is the only kind, and whether an `expression` objective needs an authoring permission of its own is answered *before* `expression_objectives_enabled` may be lifted — not after.** (OQ-GOV-8, **deferred to Phase 2** 2026-08-18, with this requirement as its trigger.) For a §4.5 template objective the two acts are one: choosing `capped_gamma` with a cap is choosing how a model is fitted, by the person who fits it, and a permission no role would grant separately is vocabulary without a decision behind it (§4.1's superseding note). An `expression` objective is different in kind — author-written maths a reviewer must read, whose blast radius spans every model using it (`02` FR-MODEL-47) — and the answer turns on how much of that review an Objective Certificate can carry (FR-MODEL-42), which nobody knows until a user-authored loss has been through one. **Deferring is therefore the decision, and this is what stops it decaying into an omission:** the flag is the trigger, **W30 is the owner**, and the enum stays closed with nothing unchecked in it meanwhile (§3.1). The separation a distinct permission would buy is not absent in the interim — it is bought by FR-GOV-11's submitter-cannot-approve and `02` FR-MODEL-46's non-author Approver — so what is deferred is an *additional* control, never the only one. **Amended 2026-08-18: the trigger is discharged.** OQ-GOV-8 was decided the same day rather than at the flag, as `FR-GOV-39`, so what this requirement now carries is its first half — `model:fit` governs template objectives — plus the record that the precondition was met before W30 rather than by W30. The deferral was answerable sooner than it looked: it rested on how much review a certificate can carry, and that is the wrong dependency, because certification analyses the artifact and never authorises the author. |
| **FR-GOV-39** | **Authoring, editing or versioning an `expression` Custom Objective requires `custom_objective:author`, a permission distinct from `model:fit` and **not** granted by any built-in role's default set. Selecting a §4.5 *template* objective remains `model:fit`, and submitting either for approval remains `model:submit`.** (OQ-GOV-8, decided 2026-08-18, discharging FR-GOV-38's trigger.) The test is §4.1's own, the one that superseded these strings in the first place: *would a role plausibly grant one and withhold the other?* For a template it would not — choosing `capped_gamma` with a cap is choosing how one's own model is fitted. For an expression it plainly would: "every pricing actuary may fit models" and "a nominated few may write the loss function everyone's models are fitted with" are two statements an insurer makes separately, and an objective is **reusable across models** (§7) whose blast radius spans every model using it (`02` FR-MODEL-47). Authoring one is a platform-level act wearing the clothes of a per-model one. **Certification and the non-author Approver do not substitute for it**, which is the argument that decided this rather than the cost comparison: `02` FR-MODEL-42 analyses the artifact — convexity, domain, sampling — and FR-MODEL-46 gates *approval*, so both act after authoring and neither says anything about whether this principal should be writing loss functions at all. An objective that is merely `draft` can already fit models whose numbers reach a pack. The controls are complementary; the authorisation one was missing. **Not default-granted** is the operative half — a permission every fitter holds is the vocabulary-without-a-decision that §4.1 removed — so it is granted explicitly by an Admin (`admin:manage_roles`) and appears in no built-in role. **The enum member and its check land together in W30**, with the `expression` kind: adding a member now that nothing checks would recreate the exact defect §4.1 records. |

### 3.4 Audit log

| ID | Requirement |
|---|---|
| **FR-GOV-20** | Every governed state change, permission change, acknowledgement, approval decision, deployment, rollback, suppression, and data purge emits an Audit Event, written in the same transaction as the change (R2). |
| **FR-GOV-21** | An Audit Event records: actor (Principal), timestamp (UTC), action, entity reference (`{type}:{slug}@{version}`), before state, after state, justification where the action requires one, `trace_id`, and source (`ui` / `api` / `job` / `system`). |
| **FR-GOV-22** | The audit table is append-only enforced at the **database privilege level** — the application role holds `INSERT` and `SELECT` only, with `UPDATE`/`DELETE` revoked (NFR-OVR-5). |
| **FR-GOV-23** | The audit log is queryable by actor, entity, action, time range, and free text over justifications, with cursor pagination and export to CSV/JSON. |
| **FR-GOV-24** | Audit events are chained with a hash of the previous event per workspace, so tampering at the storage layer (below the application) is detectable. The chain head is checkpointed and exportable. |
| **FR-GOV-40** | **The audit chain is per workspace, self-held, and described as tamper-*evident* rather than tamper-proof — and the platform ships an explicit `POST /api/v1/audit/anchor` that exports a signed chain head for the customer to store somewhere the operator does not control.** (OQ-GOV-1, decided 2026-08-18; **Phase 3**.) Per workspace is already FR-GOV-24's shape and this confirms it rather than changing it: a global chain serialises writes across workspaces for no detection benefit, since tampering is detected within the chain that covers the altered event. **What the decision adds is honesty about the threat model, in the product rather than in a footnote.** A self-held chain detects storage-layer tampering — someone editing rows underneath the application — and does **not** detect a determined platform operator, who can recompute every subsequent hash. The UI and the dossier must therefore say *tamper-evident against modification below the application*, and must not say tamper-proof; a claim an auditor can falsify in one question is worse than no claim. The anchor operation closes the operator gap **only to the extent the customer automates it**, so it is offered, documented and never described as enabled by default: it is the customer's ritual, on the customer's schedule, into the customer's store. |
| **FR-GOV-25** | Automated (`job` / `system`) actions are audited identically to human ones, with the triggering job id and, where applicable, the schedule or event that caused them. |
| **FR-GOV-26** | Sensitive values never enter the audit log verbatim: secrets, credentials, and full quote inputs are recorded as references or hashes, not values (NFR-RATE-11). |

### 3.5 Generated documentation

| ID | Requirement |
|---|---|
| **FR-GOV-27** | The platform generates a **Model Dossier** for any Model, Peril Structure, or Rating Version, assembled entirely from persisted artifacts (R3). Sections are specified in §4.4, and the dossier states the platform build that produced the figures (`00` FR-OVR-16) — under ADR-0006 each tenant runs its own deployment, so the build is not inferable from the date. |
| **FR-GOV-28** | Human commentary is supported as named, versioned, attributed **Commentary Blocks** slotted into defined positions in the dossier. Commentary is clearly distinguished from generated content in the rendered output. |
| **FR-GOV-44** | **Exactly two Commentary Blocks are mandatory before an approval may be submitted — §4.4 §1 *Purpose, scope and intended use* and §15 *Limitations and known issues* — each with a minimum length and **no pre-filled default text to accept**. Every other block stays optional.** (OQ-GOV-5, decided 2026-08-18; **Phase 3**.) Requiring commentary in ten slots reliably produces ten paragraphs of boilerplate, which is worse than silence because it *looks* like documentation and an approver stops reading it. Two is the number a person can be made to actually write, and these two are the ones a reviewer asks for first: what is this for, and where does it break. **The absence of default text is load-bearing** — a template with placeholder prose is a boilerplate generator with extra steps, and the platform ships no starter sentence for either block. A minimum length is a blunt instrument and is used anyway, because it costs a determined author nothing and stops "N/A" from being a purpose statement. |
| **FR-GOV-29** | Dossiers render to HTML and PDF, and are exportable as a self-contained bundle (document plus the referenced artifact JSON) so an external reviewer can verify a figure without platform access. |
| **FR-GOV-30** | A dossier is generated **as at a point in time** and can be regenerated for any historical state — "produce the model documentation as it stood when version 27 went live" is a supported operation, not an archaeology exercise. |
| **FR-GOV-31** | Dossiers are versioned artifacts themselves; the version submitted with an approval request is retained exactly as reviewed. |
| **FR-GOV-32** | A **regulatory response export** assembles, for a stated date or date range: what was live in each environment, the artifacts it pinned, the approvals behind them, the validation and GIPP evidence, the monitoring results, and the audit trail — as one signed, self-contained archive. |

### 3.6 Change control across the platform

| ID | Requirement |
|---|---|
| **FR-GOV-33** | Every governed artifact exposes a uniform **history view**: versions, transitions, actors, timestamps, justifications, and diffs, in one place with one shape regardless of type. |
| **FR-GOV-34** | **Blast-radius queries** are available for any artifact: "what depends on this?" spanning datasets → models → peril structures → rating versions → deployments, and "what does this depend on?" in the other direction (`01` FR-DATA-35, `02` FR-MODEL-47). |
| **FR-GOV-35** | Emergency changes follow the same path with an `expedited` marker: the same evidence is required, but the Approval Policy may permit a reduced approver count for `expedited` requests, and every expedited approval is reported in a standing exception log reviewed at the next committee. |
| **FR-GOV-36** | **Submission resolves the artifact it pins.** `POST /approval-requests` must refuse a reference naming an artifact version that does not exist, with `NOT_FOUND`. *(Appended 2026-08-17, W5, from building the model lifecycle — where the spec is right and the code is not, the spec gains the obligation rather than being edited down to what was built.* `CLAUDE.md` *§14.)* FR-GOV-14 makes an approval **pinned** to an exact artifact version; a request pinned to a version that was never created is pinned to nothing, and it can be submitted today because the endpoint validates only the `{type}:{slug}@{version}` grammar. The consequence is worse than a bad row: the owning module cannot move an artifact that does not exist, so the request decides without effect and there is nothing for a reader to reconcile the decision against. **Not fixable from the owning module** — resolution needs a lookup per artifact type and DEP-1 forbids `GOV` importing `DATA`–`MON`, so this is a resolver registered *with* governance by each owning module, or a check in each module's own submit path. **Owner: W5's peril-structure slice**, which is the first to add a second artifact type to this path and therefore the first where a per-type resolver pays for itself. Until then, a `model:` reference produced by any route in this platform resolves by construction (`02` FR-MODEL-64's submission holds the row it names), and a decision on a request naming a model that does not exist moves nothing rather than failing — a request nobody can close being the worse of the two. *(Amended 2026-08-22, W5's audit-remediation slice.* **Built — and in neither of the two shapes this requirement names.** The fan-out lives in the **route**. `api/approvals.py` already fans out per artifact type for the *decide* direction — `_carry_to_the_artifact`, one call per type, each module's function returning `None` for a request that is not its own — and the route sits above both governance and the owning modules, so DEP-1 is satisfied with no registry and no per-module submit check. `_resolve_the_artifact` mirrors it for the *submit* direction, and `approvals.submit` gained an optional `resolve` callback so governance keeps the **order**: the policy check answers first, because "no approval policy for this artifact type" is the actionable half of the two correct refusals an unpolicied reference earns. This requirement's two options were not wrong so much as incomplete — a resolver registry would have been a second mechanism for a seam that already had one, and the one registry precedent in the codebase, `worker/handlers.register_handler`, is registered from the worker entrypoint and never runs on the API path.* **Six of the twenty artifact types resolve**: `model`, `custom_objective`, `custom_metric`, `peril_structure`, `validation_rule`, `dataset_version`. **A type no module in this build can resolve fails closed**, with the `06`-owned `ARTIFACT_TYPE_NOT_RESOLVABLE` (422). `rating_version` has a policy entry and no module because `03` is unbuilt; thirteen more types have neither. `07`'s `JOB_HANDLER_NOT_REGISTERED` settles what is owed — a platform deployable before every kind has an implementation must **say the capability is absent** rather than accept work it cannot move, and accepting the submission would recreate this very defect one level up. The code is deliberately not `VALIDATION_FAILED`, which the malformed-reference branch still uses correctly: there the caller's input is bad, here it is not. **One divergence stands and is deliberate**: `metrics.resolve_ref` raises `METRIC_REF_UNRESOLVED` where this requirement names `NOT_FOUND`, because `02` §4.13's fit-path caller must tell a stale reference from a missing artifact; the route translates it at the boundary rather than changing the fit path's answer. **Owner for the durable fix: W17** — a sibling `resolve_artifact_ref` on `platform.metrics` raising `NOT_FOUND`, alongside moving the three route adapters into their own modules and making `resolve` a required parameter, which is the shape that would be fail-closed by construction rather than by every caller remembering. |

---

## 4. Data contracts

### 4.1 `Role`, `RoleAssignment`, `Permission`

```json
{
  "role": {
    "slug": "pricing-actuary",
    "name": "Pricing Actuary",
    "permissions": [
      "dataset:read", "dataset:create_version", "dataset:acknowledge_warning",
      "factor:write", "banding:write", "grouping:write",
      "model:fit", "model:submit",
      "rating_algorithm:write", "rate_table:write", "rating_version:submit",
      "optimisation:run", "optimisation:materialise",
      "monitor:write", "alert:acknowledge", "alert:resolve"
    ],
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

Notably absent from Pricing Actuary: every `*:approve` permission and
`rating_version:deploy_*` (R1, FR-GOV-6).

> **Superseded 2026-08-18 (W5, the custom-objectives slice).** The role above lists
> `custom_objective:author` and `custom_objective:submit`. **Neither exists**, and the built
> surface checks `model:read`, `model:fit` and `model:submit` instead — the same three
> permissions that govern the fits those objectives are for.
>
> The spec was the wrong side. Phase 1's objectives are the §4.5 template catalogue
> (FR-MODEL-75): choosing `capped_gamma` with a cap is choosing how a model is fitted, by
> the person who fits it, and a permission no role would ever grant separately is vocabulary
> without a decision behind it. The `Permission` enum is closed by design (`06` §3.1) so
> that a screen can enumerate what a role grants; two strings in it that nothing checks are
> exactly what a closed enum exists to prevent.
>
> **The separation this would have bought is intact and is bought elsewhere**: FR-GOV-11
> keeps the submitter out of the approval, and `02` FR-MODEL-46 requires an Approver who is
> not the author. What is *not* settled is Phase 2, where an `expression` objective is
> author-written maths rather than a parameter on a shipped loss — a case for a distinct
> authoring permission that the template catalogue does not make. Recorded as **OQ-GOV-8**
> rather than decided here — and **decided later the same day as FR-GOV-39**: an
> `expression` objective *does* need `custom_objective:author`, distinct from `model:fit`
> and granted by no built-in role's default set.
>
> **`custom_objective:author` therefore returns to the vocabulary, and the name is reused
> deliberately.** It was removed because nothing checked it and the template catalogue made
> no case for it; it comes back with a case and with its check, which land together in W30.
> `custom_objective:submit` does **not** return — the same test fails for it, since
> FR-GOV-11 already keeps a submitter out of their own approval. The Pricing Actuary set
> above no longer lists either, which is the point of the decision rather than an omission:
> a permission every fitter holds by default would be the vocabulary-without-a-decision this
> note was written about.

### 4.2 `ApprovalPolicy` (workspace defaults)

```json
{
  "policies": [
    {"artifact_type": "validation_rule", "approvers_required": 1,
     "approver_roles": ["approver", "admin"], "evidence": ["dry_run_result"]},
    {"artifact_type": "custom_objective", "approvers_required": 1,
     "approver_roles": ["approver"], "evidence": ["objective_certificate"],
     "escalation": {"when": "certificate.convexity == 'violated'", "approvers_required": 2}},
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
     "evidence": ["rating_version_approval", "uat_deployment"]}
  ],
  "expedited": {"enabled": true, "approvers_required": 1,
                "requires_reason": true, "reported_in_exception_log": true},
  "separation_of_duties": {"submitter_may_approve": false, "configurable": false}
}
```

`separation_of_duties.configurable: false` is deliberate and is not a placeholder (R1).

> **`risk_tier` joins the entry shape in Phase 3 with FR-GOV-43** (OQ-GOV-4, decided
> 2026-08-18): an entry may carry `"risk_tier": 1`, and an entry **without** one applies to
> every tier. That default is what keeps this document true as written — the defaults above
> gain nothing and lose nothing, and a workspace that never tiers a Model Family sees no
> change at all. Tier is read from the artifact's Model Family or Rating Algorithm, never
> from the version under approval.

> **These defaults sit on top of §3.3's floor, and may only add to it (FR-GOV-37, OQ-GOV-7 decided
> 2026-08-18).** An entry whose `evidence` omits a floor kind for its artifact type is refused when
> the policy is saved: the floor for `model` is `diagnostics` and `transparency_artifact_if_non_glm`,
> for `validation_rule` `dry_run_result`, for `custom_objective` `objective_certificate`, and
> `peril_structure` has no §3.3 row and therefore an empty floor. Submission checks the union of the
> floor and the entry, so an older stored policy cannot sit below it either.
>
> **Which is also where this document was ahead of the build, recorded rather than quietly aligned
> (`CLAUDE.md` §0).** The `model` entry above lists `transparency_artifact_if_non_glm` and
> `model_comparison_if_predecessor`; `DEFAULT_POLICY` in `model-schema` shipped `diagnostics` alone,
> and the `rating_version` entry above lists six kinds against the three it ships. The **defaults in
> code were right for the day they were written** — an uncheckable kind fails closed (R4), so a
> default naming `model_comparison_if_predecessor` would have refused every model submission — and
> the page was right about the destination. FR-GOV-37 is what reconciles them: the checkable kinds
> become the enforced floor and move into `DEFAULT_POLICY`, the rest keep their place here with an
> owner. `transparency_artifact_if_non_glm` is the kind's name on both sides from 2026-08-18; the
> submission check had been answering a kind it called `transparency_artifact`, so a workspace that
> copied the name off this page got a fail-closed refusal for evidence it had.

> **`peril_structure` added 2026-08-18 (W5, the peril-structure slice).** `02` FR-MODEL-61
> has made a Peril Structure approvable since Phase 0, and `peril_structure` has been in
> `ARTIFACT_TYPES` for as long — but with no entry here, `submit` refuses it with "no
> approval policy for this artifact type". That is a *correct* refusal, which is what made
> it invisible: the machine was working exactly as FR-GOV-12 specifies, on an artifact
> nobody could ever approve.
>
> Its evidence is the **reconciliation**, because `02` FR-MODEL-60 makes that the coherence
> check an approver is being asked to accept. It is enforced structurally as well as by
> policy: `reconciled` is the only state with an edge into `review`, and a reconciliation
> whose status is `fail` is refused at submission — the tolerance is the submitter's own
> declaration, so missing it is failing a test they set themselves.
>
> This is an **addition** to §3.3's evidence floor and removes nothing, so it sits inside
> OQ-GOV-7's recommendation rather than pre-empting it.

> **`custom_metric` added 2026-08-20 (W5, the custom-metrics slice).** `02` FR-MODEL-45
> gives a Custom Metric the same lifecycle and grammar as a Custom Objective, and
> `platform.metrics._require_evidence` has expected this entry since the slice that added
> `submit` — but with no entry here, `certified -> review` refused with 409 in every
> workspace, on "no approval policy for this artifact type", before `_require_evidence` was
> ever reached. The approval lifecycle was unreachable without it, the same defect class as
> `peril_structure` above.
>
> Its evidence is the **metric certificate**, mirroring `custom_objective`'s
> `objective_certificate`, because `02` FR-MODEL-105 makes certification the check an
> approver is being asked to accept.
>
> This is an **addition** to §3.3's evidence floor and removes nothing, so it sits inside
> OQ-GOV-7's recommendation rather than pre-empting it.

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
| 18 | Regulatory considerations — material factors arising from customer-outcome obligations, and what was allowed for | Commentary Block (attributed), FR-GOV-45 |
| 19 | Assumption consistency — material assumptions against those used for business planning, reserving and capital, and any material inconsistency | Commentary Block (attributed), FR-GOV-45 |

> **18 and 19 added 2026-08-18 with FR-GOV-45** (OQ-GOV-6), appended rather than slotted in beside §13's compliance material because the numbers are cited from other documents and behave like every other identifier here (`CLAUDE.md` §5). They carry TAS 200 v2.0's P1.1 and P1.2/P1.4 respectively.
>
> **They are not part of FR-GOV-44's mandatory two**, and the distinction is deliberate rather than an oversight. FR-GOV-44 governs what an *approver* must be given before a submission is accepted, and the answer stays exactly two blocks. These two serve a different reader — someone assessing the work against TAS 200 — so they are required for a dossier to be **complete for that purpose**, and a workspace outside the standard's geographic or membership scope may leave them empty without blocking an approval. Making them mandatory at submission would have quietly turned "exactly two" into four, which is the boilerplate slope OQ-GOV-5 was decided to avoid.

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

---

## 5. Interfaces

### 5.1 REST API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/me` | Current principal, roles, effective permissions |
| `GET` | `/api/v1/me/workspaces` | The principal's own memberships, unscoped — the list first selection chooses from (FR-PLAT-63) |
| `POST` | `/api/v1/me/workspace` | Audits a switch into both chains; an absent `Workspace-Id` is `left=None`, the first selection (FR-PLAT-63) |
| `GET`/`POST` | `/api/v1/roles` | List / create roles (FR-GOV-3) |
| `POST` | `/api/v1/role-assignments` | Assign a scoped role (FR-GOV-4) |
| `POST` | `/api/v1/break-glass` | Time-boxed elevation with reason (FR-GOV-8) |
| `GET`/`PUT` | `/api/v1/approval-policy` | Read / update the workspace policy (FR-GOV-12) |
| `POST` | `/api/v1/approval-requests` | Submit an artifact; validates evidence and checklist (FR-GOV-10) |
| `GET` | `/api/v1/approval-requests?assigned_to=me&status=review` | Approvals inbox (FR-GOV-16) |
| `GET` | `/api/v1/approval-requests/{id}` | Request with resolved evidence inline |
| `POST` | `/api/v1/approval-requests/{id}/decide` | `approve` / `reject` / `request_changes` + comment (FR-GOV-11/13) |
| `POST` | `/api/v1/approval-requests/{id}/withdraw` | Withdraw before deployment (FR-GOV-15) |

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
> from putting it forward. Reading the queue and the policy follow from FR-GOV-16's purpose:
> an approvals inbox that only approvers could see would hide from a submitter what is
> waiting on whom, and the policy is the rule everyone is being held to.
>
> All four remain **workspace-scoped** — a caller sees their own workspace and no other —
> and none of them decides anything. The deciding routes carry `approval:decide`, and
> FR-GOV-11's separation of duties is enforced in three independent layers, database
> constraint included.
| `POST` | `/api/v1/attestations` | Record a periodic review (FR-GOV-18) |
| `GET` | `/api/v1/audit?actor=&entity=&action=&from=&to=&q=` | Query the audit log (FR-GOV-23) |
| `GET` | `/api/v1/audit/verify?from=&to=` | Verify the hash chain (FR-GOV-24) |
| `POST` | `/api/v1/audit/anchor` | Export a signed chain head for external anchoring (FR-GOV-40) |
| `GET` | `/api/v1/audit/export` | Export CSV/JSON |
| `POST` | `/api/v1/dossiers` | **202** Generate a dossier for an artifact (FR-GOV-27) |
| `GET` | `/api/v1/dossiers/{id}?format=html\|pdf\|bundle` | Render / export (FR-GOV-29) |
| `POST` | `/api/v1/dossiers/{id}/commentary` | Add/update an attributed Commentary Block (FR-GOV-28) |
| `POST` | `/api/v1/regulatory-exports` | **202** Point-in-time evidence archive (FR-GOV-32) |
| `GET` | `/api/v1/artifacts/{ref}/history` | Uniform history view (FR-GOV-33) |
| `GET` | `/api/v1/artifacts/{ref}/dependencies?direction=up\|down` | Blast radius (FR-GOV-34) |

**Error codes owned by this module:** `PERMISSION_DENIED`, `SCOPE_DENIED`,
`SUBMITTER_CANNOT_APPROVE`, `DUPLICATE_APPROVER`, `EVIDENCE_INCOMPLETE`,
`POLICY_BELOW_EVIDENCE_FLOOR`, `CHECKLIST_INCOMPLETE`, `ARTIFACT_FLAGGED`,
`APPROVAL_PINNED_ARTIFACT_CHANGED`, `APPROVAL_ALREADY_DECIDED`,
`WITHDRAW_AFTER_DEPLOY_FORBIDDEN`,
`BREAK_GLASS_REASON_REQUIRED`, `AUDIT_CHAIN_BROKEN`, `ATTESTATION_OVERDUE`,
`ARTIFACT_TYPE_NOT_RESOLVABLE`.

### 5.2 Backend service interfaces

Governance is backend-side; it has no `pricing-core` surface (it contains no actuarial
maths — ADR-0001).

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
| 2 | Frontend → Backend | `POST /approval-requests` — evidence and checklist validated (FR-GOV-10) |
| 3 | Backend | Resolves and pins the evidence bundle; emits an Audit Event; notifies eligible Approvers |
| 4 | Approver | Opens the inbox, reviews inline evidence |
| 5a | Approver | `request_changes` with a comment → artifact returns to its pre-submission state (FR-GOV-13) — `draft` for most types, `fitted` for a Model |
| 5b | Approver | `approve` with a comment → decision recorded, separation of duties enforced (R1) |
| 6 | Backend | On the final required approval, transitions the artifact and emits Audit Events |
| 7 | Deployer | For a Rating Version, deploys (`03` FR-RATE-50) — itself an audited, permissioned act |
| 8 | Backend | Periodically flags overdue attestations on live artifacts (FR-GOV-18) |

Governance appears in every workflow document; the custom-objective path is the most
governance-heavy: [`wf-05-custom-objective-lifecycle.md`](../workflows/wf-05-custom-objective-lifecycle.md).

---

## 7. Cross-module dependencies

### 7.1 Consumes

| From | What |
|---|---|
| `07-platform` | Authenticated principals **and their workspace memberships** (FR-PLAT-62, FR-PLAT-63 — the identity endpoint carries the list a selector renders), user directory/OIDC claims, notification channels, job identity for `system` audit events |

**Not a dependency:** the artifact states, evidence artifacts and flags that gate approval
(FR-GOV-17) are **pushed to** this module by `01`–`05` — they appear in those modules'
§7.2. Governance does not read their tables, which is what keeps DEP-1 intact.

### 7.2 Provides

| To | What |
|---|---|
| `01`–`05` | Permission checks, the approval workflow, the audit sink, and the flag surface |
| External reviewers / regulators | Dossiers and point-in-time evidence exports (FR-GOV-29/32) |

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
| **NFR-GOV-1** | Permission checks add < 5 ms to a request, using a cached effective-permission set invalidated on assignment change. |
| **NFR-GOV-2** | Audit writes never fail silently: an audit write failure rolls back the domain change (R2). |
| **NFR-GOV-3** | Audit queries over 100 M events return a filtered page in < 2 s, supported by partitioning and indexes on `(workspace_id, at)`, `(entity_ref)`, `(actor_id)`. |
| **NFR-GOV-4** | Audit retention ≥ 7 years (NFR-OVR-6); the hash chain is verifiable over the whole retained range. |
| **NFR-GOV-5** | Dossier generation for a full Rating Version completes in < 2 min and is byte-reproducible for the same artifact set and template version. |
| **NFR-GOV-6** | A regulatory export for a one-year range assembles in < 30 min and is self-contained (verifiable without platform access). |
| **NFR-GOV-7** | The approvals inbox loads in < 1 s with evidence summaries; full evidence renders progressively. |
| **NFR-GOV-8** | Separation of duties, append-only audit, and permission enforcement are covered by explicit negative tests in CI — the test suite must prove that a submitter *cannot* approve, not merely that an approver can. |

---

## 10. Open questions

Mirrored into [`open-questions.md`](../open-questions.md).

| ID | Question |
|---|---|
| **OQ-GOV-1** | ~~Audit hash chain: per workspace or global, and is a self-held chain enough?~~ **DECIDED 2026-08-18: per workspace, self-held, described as tamper-evident rather than tamper-proof, with an explicit chain-head anchor operation the customer automates into a store the operator does not control — FR-GOV-40.** |
| **OQ-GOV-2** | ~~Are platform roles authoritative, or is IdP group membership?~~ **DECIDED 2026-08-18: hybrid — the IdP owns identity and role membership so a leaver loses access automatically; the platform owns artifact scope, which names objects no directory has heard of — FR-GOV-41.** |
| **OQ-GOV-3** | ~~Can an Admin override a flag (FR-GOV-17)?~~ **DECIDED 2026-08-18: yes, and it leaves a scar — two Admins, a written justification, a badge on the artifact that never expires, the exception log, and its own line in the approval history — FR-GOV-42.** An override never clears the underlying flag. |
| **OQ-GOV-4** | ~~Do we need formal model risk tiering?~~ **DECIDED 2026-08-18: yes — `risk_tier` on Model Family and Rating Algorithm, which `ApprovalPolicy` entries may key on — FR-GOV-43.** On the family and the algorithm rather than the version, so it cannot be lowered on the day a quicker approval is wanted. |
| **OQ-GOV-5** | ~~How much commentary is required before an approval can be submitted?~~ **DECIDED 2026-08-18: exactly two Commentary Blocks — §4.4 §1 and §15 — with a minimum length and no default text to accept — FR-GOV-44.** Ten mandatory slots produce ten paragraphs of boilerplate; two produce two paragraphs somebody wrote. |
| **OQ-GOV-6** | ~~Does TAS 200 (Insurance) cover pricing and premium rating, or only reserving, capital and Solvency II actuarial-function work?~~ **DETERMINED 2026-08-18 by reading TAS 200 v2.0: it applies, through the `Pricing frameworks` scope item, whose glossary definition names the methodologies, assumptions and models behind an insurer's premium rates — FR-GOV-45.** No pricing-specific provisions section exists, so §1's P1.1–P1.4 bind, plus TAS 100. |
| **OQ-GOV-7** | ~~Does `06` §3.3's per-artifact evidence table or `06` §4.2's `ApprovalPolicy` defaults decide what a submission actually requires?~~ **DECIDED 2026-08-18: §3.3 is a floor per artifact type and §4.2 may only add to it — FR-GOV-37**, with the floor restated in §4.2 so a reader of the defaults sees it, refused at policy save, and applied as a union at submission. The enforced floor is §3.3's checkable projection; the uncheckable remainder is named with an owner. |
| **OQ-GOV-8** | ~~Does an `expression` Custom Objective (Phase 2, `02` FR-MODEL-75) need an authoring permission distinct from `model:fit`?~~ **DECIDED 2026-08-18: yes — `custom_objective:author`, granted by no built-in role's default set — FR-GOV-39**, discharging FR-GOV-38's trigger before W30 rather than at it. Template selection stays `model:fit`; submission stays `model:submit`. |
