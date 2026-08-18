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
| **FR-GOV-18** | **Attestation**: governed artifacts that are live can carry a periodic review requirement (default annual). An overdue attestation is surfaced on the artifact, in the inbox, and in monitoring dashboards — it does not automatically retire anything. |

### 3.3 Required evidence by artifact type

| ID | Requirement |
|---|---|
| **FR-GOV-19** | Required evidence is defined per artifact type and enforced at submission (R4): |

| Artifact | Required evidence |
|---|---|
| **Dataset Version** → `validated` | Validation Report with no `fail`; every `warn` acknowledged with justification (`01` FR-DATA-17) |
| **Validation Rule** | Successful dry-run result against a real Dataset Version (`01` FR-DATA-21) |
| **Custom Objective** | Objective Certificate with `overall ≠ failed`; applicability declaration; usage impact if a new version of an in-use objective (`02` FR-MODEL-42/47) |
| **Model** | Diagnostics (train + holdout); transparency artifact where non-GLM; model comparison where a predecessor exists; factor/banding/grouping rationale; dataset lineage (`02` FR-MODEL-64) |
| **Peril Structure** | Per-peril model approvals; reconciliation result within tolerance (`02` FR-MODEL-60) |
| **Rate Table Version** | Change note; diff vs previous; diff vs technical seed where seeded (`03` FR-RATE-16/17) |
| **Rating Version** | Structural diff; rate table diffs; passing regression suite; dislocation run with attribution; GIPP check where enabled; change summary (`03` FR-RATE-40) |
| **Deployment to `prod`** | A complete Rating Version approval; a successful `uat` deployment; Deployer permission (`03` FR-RATE-50) |

| ID | Requirement |
|---|---|
| **FR-GOV-37** | **The table above is a floor. §4.2's `ApprovalPolicy` may add to it and may never remove from it.** (OQ-GOV-7, decided 2026-08-18.) The two tables have disagreed since Phase 0 and the code could only enforce one of them, because a check has to read a list and there were two. The deciding case is `02` §4.8 R3: a transparency artifact for a non-GLM model is an invariant of the artifact, not a workspace preference, and a policy edit that removes it is a mispricing waiting for an audit. Three mechanisms, so that neither table can be read alone: (i) the floor is restated in §4.2's own text, so a reader of the defaults sees what the defaults may not drop below — the objection to a floor was always that a submission refused for evidence the policy does not mention is an error nobody can act on; (ii) `PUT /api/v1/approval-policy` refuses an entry whose `evidence` omits a floor kind for that artifact type with `POLICY_BELOW_EVIDENCE_FLOOR`, naming the artifact type and the kinds, because a policy document that says less than it enforces misleads its reader; (iii) submission checks the **union** of the floor and the matching policy entry, so a policy stored before this requirement cannot dodge the floor by being old. **The enforced floor is the checkable projection of §3.3, and the remainder is named with an owner rather than asserted**: for `model` it is `diagnostics` and `transparency_artifact_if_non_glm`; `model_comparison_if_predecessor` stays out until a comparison names its models in a queryable column rather than inside `payload` (owner: the slice that adds it), and §3.3's factor/banding/grouping rationale is unmodelled (owner: Phase 1b). Submission continues to **fail closed** on any evidence kind it cannot verify (R4), so a tightened policy can never silently do nothing. An artifact type with **no §3.3 row has an empty floor** — `peril_structure` is that case — and a floor that says nothing permits anything, which is the right default for an artifact §3.3 predates rather than a gap to be filled by inference. |
| **FR-GOV-38** | **`model:fit` governs Custom Objectives for as long as the catalogue is the only kind, and whether an `expression` objective needs an authoring permission of its own is answered *before* `expression_objectives_enabled` may be lifted — not after.** (OQ-GOV-8, **deferred to Phase 2** 2026-08-18, with this requirement as its trigger.) For a §4.5 template objective the two acts are one: choosing `capped_gamma` with a cap is choosing how a model is fitted, by the person who fits it, and a permission no role would grant separately is vocabulary without a decision behind it (§4.1's superseding note). An `expression` objective is different in kind — author-written maths a reviewer must read, whose blast radius spans every model using it (`02` FR-MODEL-47) — and the answer turns on how much of that review an Objective Certificate can carry (FR-MODEL-42), which nobody knows until a user-authored loss has been through one. **Deferring is therefore the decision, and this is what stops it decaying into an omission:** the flag is the trigger, **W30 is the owner**, and the enum stays closed with nothing unchecked in it meanwhile (§3.1). The separation a distinct permission would buy is not absent in the interim — it is bought by FR-GOV-11's submitter-cannot-approve and `02` FR-MODEL-46's non-author Approver — so what is deferred is an *additional* control, never the only one. |

### 3.4 Audit log

| ID | Requirement |
|---|---|
| **FR-GOV-20** | Every governed state change, permission change, acknowledgement, approval decision, deployment, rollback, suppression, and data purge emits an Audit Event, written in the same transaction as the change (R2). |
| **FR-GOV-21** | An Audit Event records: actor (Principal), timestamp (UTC), action, entity reference (`{type}:{slug}@{version}`), before state, after state, justification where the action requires one, `trace_id`, and source (`ui` / `api` / `job` / `system`). |
| **FR-GOV-22** | The audit table is append-only enforced at the **database privilege level** — the application role holds `INSERT` and `SELECT` only, with `UPDATE`/`DELETE` revoked (NFR-OVR-5). |
| **FR-GOV-23** | The audit log is queryable by actor, entity, action, time range, and free text over justifications, with cursor pagination and export to CSV/JSON. |
| **FR-GOV-24** | Audit events are chained with a hash of the previous event per workspace, so tampering at the storage layer (below the application) is detectable. The chain head is checkpointed and exportable. |
| **FR-GOV-25** | Automated (`job` / `system`) actions are audited identically to human ones, with the triggering job id and, where applicable, the schedule or event that caused them. |
| **FR-GOV-26** | Sensitive values never enter the audit log verbatim: secrets, credentials, and full quote inputs are recorded as references or hashes, not values (NFR-RATE-11). |

### 3.5 Generated documentation

| ID | Requirement |
|---|---|
| **FR-GOV-27** | The platform generates a **Model Dossier** for any Model, Peril Structure, or Rating Version, assembled entirely from persisted artifacts (R3). Sections are specified in §4.4, and the dossier states the platform build that produced the figures (`00` FR-OVR-16) — under ADR-0006 each tenant runs its own deployment, so the build is not inferable from the date. |
| **FR-GOV-28** | Human commentary is supported as named, versioned, attributed **Commentary Blocks** slotted into defined positions in the dossier. Commentary is clearly distinguished from generated content in the rendered output. |
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
| **FR-GOV-36** | **Submission resolves the artifact it pins.** `POST /approval-requests` must refuse a reference naming an artifact version that does not exist, with `NOT_FOUND`. *(Appended 2026-08-17, W5, from building the model lifecycle — where the spec is right and the code is not, the spec gains the obligation rather than being edited down to what was built.* `CLAUDE.md` *§14.)* FR-GOV-14 makes an approval **pinned** to an exact artifact version; a request pinned to a version that was never created is pinned to nothing, and it can be submitted today because the endpoint validates only the `{type}:{slug}@{version}` grammar. The consequence is worse than a bad row: the owning module cannot move an artifact that does not exist, so the request decides without effect and there is nothing for a reader to reconcile the decision against. **Not fixable from the owning module** — resolution needs a lookup per artifact type and DEP-1 forbids `GOV` importing `DATA`–`MON`, so this is a resolver registered *with* governance by each owning module, or a check in each module's own submit path. **Owner: W5's peril-structure slice**, which is the first to add a second artifact type to this path and therefore the first where a per-type resolver pays for itself. Until then, a `model:` reference produced by any route in this platform resolves by construction (`02` FR-MODEL-64's submission holds the row it names), and a decision on a request naming a model that does not exist moves nothing rather than failing — a request nobody can close being the worse of the two. |

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
      "model:fit", "model:submit", "custom_objective:author", "custom_objective:submit",
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
> rather than decided here — and **deferred to Phase 2 on 2026-08-18 with a trigger rather than
> a hope**: FR-GOV-38 makes answering it a precondition of lifting
> `expression_objectives_enabled` (`07` FR-PLAT-46), owned by W30.

### 4.2 `ApprovalPolicy` (workspace defaults)

```json
{
  "policies": [
    {"artifact_type": "validation_rule", "approvers_required": 1,
     "approver_roles": ["approver", "admin"], "evidence": ["dry_run_result"]},
    {"artifact_type": "custom_objective", "approvers_required": 1,
     "approver_roles": ["approver"], "evidence": ["objective_certificate"],
     "escalation": {"when": "certificate.convexity == 'violated'", "approvers_required": 2}},
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
`BREAK_GLASS_REASON_REQUIRED`, `AUDIT_CHAIN_BROKEN`, `ATTESTATION_OVERDUE`.

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
| `07-platform` | Authenticated principals, user directory/OIDC claims, notification channels, job identity for `system` audit events |

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
| **OQ-GOV-1** | Should the audit hash chain be per workspace or global — **"global" now means "per deployment", since ADR-0006 gives every tenant its own** — and is a chain sufficient without external anchoring (e.g. periodically publishing the chain head somewhere the platform operator cannot alter)? A chain an operator controls end-to-end detects storage tampering but not a determined operator. |
| **OQ-GOV-2** | Are platform roles authoritative, or should group membership from the identity provider be? IdP-authoritative is better for large insurers' joiner/leaver processes; platform-authoritative is far clearer for scoped, artifact-level permissions. |
| **OQ-GOV-3** | Should Admin be able to override a flag (FR-GOV-17) at all? Allowing it creates a bypass of every gate in the platform; disallowing it means a genuine false-positive flag blocks a legitimate change with no recourse. |
| **OQ-GOV-4** | Do we need a formal "model risk tiering" concept (tier 1 models needing more approvers, more frequent attestation), or is per-artifact-type policy plus scoped roles sufficient? Tiering is standard in UK insurer model governance. |
| **OQ-GOV-5** | How much commentary is *required* in a dossier before an approval can be submitted? Requiring it improves documentation quality and invites boilerplate; not requiring it produces dossiers that are all numbers and no reasoning. |
| **OQ-GOV-6** | Does **TAS 200 (Insurance)** cover pricing and premium rating, or only reserving, capital and Solvency II actuarial-function work? TAS 100 applies to this platform's output regardless. If TAS 200 also applies, its assumption-setting requirements (strengthened in v2.0, effective 2025-01-01) bear directly on `02`'s factor/banding/grouping rationale and `01`'s validation evidence, and §4.4's dossier sections must satisfy them. The scope statement is in the standard text, not in the FRC's public summaries. |
| **OQ-GOV-7** | ~~Does `06` §3.3's per-artifact evidence table or `06` §4.2's `ApprovalPolicy` defaults decide what a submission actually requires?~~ **DECIDED 2026-08-18: §3.3 is a floor per artifact type and §4.2 may only add to it — FR-GOV-37**, with the floor restated in §4.2 so a reader of the defaults sees it, refused at policy save, and applied as a union at submission. The enforced floor is §3.3's checkable projection; the uncheckable remainder is named with an owner. |
| **OQ-GOV-8** | Does an `expression` Custom Objective (Phase 2, `02` FR-MODEL-75) need an authoring permission distinct from `model:fit`? Raised 2026-08-18 by superseding `custom_objective:author`/`custom_objective:submit` in §4.1: for a template objective the two are the same act, and for author-written maths they may not be. **Deferred to Phase 2 on 2026-08-18 — the deferral is the decision, and FR-GOV-38 is its trigger**: the question is answered before `expression_objectives_enabled` may be lifted, owned by W30. The answer turns on how much of the review a certificate can carry, which is unknown until a user-authored loss has been through one. |
