---
id: RL-9906
family: ruling
title: WK-674 Slice 2 DP-S2-2 and DP-S2-3 decided — a deployment request owns its pinned evidence, and deployment:promote takes an Environment scope
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                    # set to the OQ-1234 ruling's minted id at this record's mint turn (item C)
relates: [PL-1237, CR-1212, RL-1232, FR-267, FR-429, FR-345, FR-356, FD-1200]
---

# RL-9906 — WK-674 Slice 2 DP-S2-2 and DP-S2-3 decided: a deployment request owns its pinned evidence, and `deployment:promote` takes an Environment scope

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). Its term was
extended through this record by the entry "2026-09-30 11:04:57 BST — WK-674 S2 DPs: routing
agreed; dm-effort-high extended; errors.py". That entry also set the conditions ruled in
item A.4 and item C.

The decision points are those of WK-674 Slice 2's leaf plan, which planner-924 is writing
(PL working id 9920, SL-1256). **At the time of writing its branch was not pushed**:
`git ls-remote origin` listed no `wk674-s2*` ref. So this record rules from the lead's relay
of the options, and from premises that this session verified at `9f63d0fe` (below). DP-S2-1,
a trace's link to its Deployment, is the medium-effort decision-maker's.

## Presence and absence, as verified at `9f63d0fe`

| Claim | Verdict | How it was verified |
|---|---|---|
| `deployment` as a reference type | **absent** | `ARTIFACT_TYPES` (`packages/model-schema/src/model_schema/refs.py:20-29`), read. It has no `"deployment"`. `ArtifactRef`'s validator refuses a type outside it (`:88-90`, `if match["type"] not in ARTIFACT_TYPES: raise`). `REF_PATTERN` is built from it (`:51-53`). **No `ArtifactRef` can name a deployment.** |
| The policy is keyed `deployment` | **present** | `EVIDENCE_FLOOR["deployment"] = ("rating_version_approval", "uat_deployment")` (`packages/model-schema/src/model_schema/approvals.py:107`). `approvals.submit` looks up `policy.entry_for(artifact_ref.type, environment)` (`backend/src/app/platform/approvals.py:225`). A `deployment` entry can therefore never be reached by a request whose ref must be one of `ARTIFACT_TYPES`. |
| An evidence column on the approval request | **absent** | `ApprovalRequestRow` (`backend/src/app/db/models.py:611-640`), read. Its columns are `id`, `workspace_id`, `artifact_ref`, `artifact_type`, `environment`, `submitted_by`, `submitted_at`, `change_summary`, `status`, `approvers_required`, `withdrawn_reason` and `decided_at`. None holds evidence. |
| Where evidence lives today | **present, on the owning module's row** | `rating_versions.submit_for_review` writes `row.evidence` on the Rating Version's own row, then calls `approvals.submit` (`backend/src/app/platform/rating_versions.py:294-300`). Generic `approvals.submit` (`platform/approvals.py:192-282`) checks the policy entry and the reference, and nothing else. |
| The single decision path | **present** | `api/approvals.py`'s decide and withdraw routes call `_carry_to_the_artifact` (`:260`, `:293`, defined `:488`). It drives each owning module's `apply_approval_decision`, for example `rating_versions.py:312`, whose mapping writes `APPROVED` at `:382`. The status itself comes from `_resolve_status` (`platform/approvals.py:547-554`). |
| Scope types | **present: four, no environment** | `ScopeType` (`packages/model-schema/src/model_schema/permissions.py:91-102`): `workspace`, `dataset`, `model_family`, `rating_algorithm`. `_covers` (`backend/src/app/platform/rbac.py:205-217`) lets a workspace-wide assignment cover everything. With no `resource`, it admits **only** a workspace-wide assignment. |
| CR-1212 item 4 | **present** | `docs/closures/CR-01212-…md:342-345`: "a `06`/`07` spec change that scopes `deployment:promote` to named environments, owned by WK-674 and landed with its environment record". `RL-1232` DP-6, as amended 2026-09-29 (`docs/rulings/RL-01232-…md:303-322`), leaves the mechanism to that item. |
| FR-345 | **present** | `06-governance.md:81`: "Role assignments are **scoped**: workspace-wide, or limited to named Datasets, Model Families, or Rating Algorithms". It names no Environment. |

## Ruled

### A. DP-S2-2 — option (a): a deployment request is its own artifact, owned by the deployment module, and its row pins its evidence

1. **The subject of a `deployment` approval request is a Deployment Request.** It is a row
   owned by the module that owns deployment (`03` FR-267, built in WK-674 Slice 2).
   - `"deployment"` joins `ARTIFACT_TYPES`, and `docs/contracts/schemas/common/artifact-ref.schema.json`
     is regenerated with it, since the list is a spec change (`refs.py:18-19`).
   - A request is referenced as `deployment:<slug>@<version>` (ID-3). The slug is immutable,
     and the version is monotone per slug (ID-2). **The leaf plan chooses the slug scheme,
     under one constraint:** the slug must not be a renamable name. An Environment can be
     renamed (`07` FR-428; `admin:manage_environments`), and a reference must never change
     its meaning.
   - The row pins the approved Rating Version it deploys, and the target Environment's
     **identity** (not its name).
2. **The evidence lives on that row, written once at submission, before `approvals.submit`
   is called**, as `rating_versions.submit_for_review` does today. This is the established
   pattern, so no evidence column is added to `ApprovalRequestRow` (option (c)), and
   governance keeps importing nothing from the owning module. The two floor items
   (`approvals.py:107`):
   - **`rating_version_approval`**: the decided approval request of the pinned Rating
     Version;
   - **`uat_deployment`**, the predecessor item: **either** the id of the successful
     predecessor Deployment of that Rating Version, **or** a skip record, naming the skipped
     environment and a non-empty reason. A skip record is valid only where the target's
     environment-qualified `deployment` policy entry permits the skip (the OQ-1234 ruling, item
     1).

   The owning module checks the floor and FR-429's one predicate before it writes. A
   request missing either item is refused with `EVIDENCE_INCOMPLETE`.
3. **Why not (b) or (c).**
   - (b) names the Rating Version with a policy-key override. The Rating Version has its own
     `rating_version` approval, so one ref would carry two kinds of request. Evidence would
     still have no home: (b) moves the key, not the evidence.
   - (c) adds a second place where evidence lives: generic, beside the owning modules' own.
     That is wider than Slice 2 and breaks the pattern every other approvable type follows.
4. **The FD-1200 class — required, each red first** (the 11:04:57 BST entry's conditions):
   - **No approval without its pinned evidence.** A deployment request whose row lacks either
     floor item, or is deliberately stripped of it by a test fixture, cannot reach `approved`.
     The submission is refused, and a decision on such a row is refused too. With the check
     removed, the fixture is approved, and the test fails.
   - **The evidence is immutable after submission** (FR-356, `00` FR-4). No code path
     updates the row's evidence or pins once the request exists. An attempted update through
     the module's functions is refused, and a test proves it. A migration adds no
     `ON UPDATE` path, and if the leaf plan chooses a database trigger, its test is also red
     first.
   - **Only the single decision path writes `approved`: for every table, derived from the
     models, not listed by hand.** *(Widened 2026-09-30 on the maintainer's must-check
     relayed after #971's first push. It first covered the deployment-request row only.)*
     - **The population:** every mapped class under `app.db.models.Base` that has a `status`
       column, enumerated from the SQLAlchemy mapper registry at test time. A new table,
       including the Deployment Request row, joins the population by existing, with no edit
       to the test. The status columns are plain strings (`models.py:635`, `:788`, …,
       `:1898`), so the population is keyed on the column, not on its type.
     - **The writers:** an AST walk over `backend/src` finds every place that can set such a
       row's `status`: an attribute assignment `<row>.status = …`, a constructor's
       `status=…`, and the model's own `default=`/`server_default=`. A write whose value is
       provably not `approved` (another literal, or another enum member) is ignored. Every
       other write, including a non-literal one, must sit in that table's
       `apply_approval_decision` reached from `_carry_to_the_artifact`
       (`api/approvals.py:488`, carrying at `:499-517`), or, for `approval_requests` itself,
       in `platform/approvals.py`'s decision (`_resolve_status`, `:547-554`).
     - **Red first:** a planted second writer of `approved` on the deployment-request table
       fails the check. So does a planted non-literal status write on any table, and a
       planted `default="approved"`.
     - **It does not hold today, and the check says so honestly.** At `9f63d0fe`, two
       existing writers sit outside that path:
       1. **validation rules** are approved through their own route,
          `api/validation.py:359` → `validation_rules.approve_rule`
          (`platform/validation_rules.py:395`), which writes `row.status = APPROVED` at
          `:423`. `_carry_to_the_artifact` carries modelling, objectives, metrics and rating
          versions only (`api/approvals.py:499-517`);
       2. **validation rule sets** are approved by construction: the column's
          `default="approved"` (`models.py:1195`), taken by `ValidationRuleSetRow(...)`
          without a `status` (`validation_rules.py:621`). A rule set is not in `06` §2's
          Governed Artifact list (`06-governance.md:64`).

       The check lands with a **pinned baseline** of exactly these two, as a literal in the
       test, citing this record. Any writer not in the literal fails, and the baseline can
       only shrink, as `#940`'s exemption rule does. **Whether either is a defect is not ruled
       here.** Both are offered to the lead as candidate findings of the FD-1200 class: a
       second decision path for a Governed Artifact, and an `approved` status set with no
       approval. The Deployment Request table has no baseline entry.
5. **The deploy route executes only an approved request.** For a target whose deployments are
   approval-gated, `POST /api/v1/environments/{env}/deployments` names an **approved**
   Deployment Request and re-evaluates FR-429's one predicate from the request's **pinned**
   evidence. It never re-reads a changeable source. A target with no `deployment` policy
   entry needs no request. For it, the predicate reads the predecessor's successful
   Deployment directly, and no skip is possible (the OQ-1234 ruling, item 1).

### B. DP-S2-3 — option (a): `ScopeType.ENVIRONMENT`, checked with the Environment as the resource

1. **`ScopeType` gains `ENVIRONMENT`**, with `scope_id` the Environment's id. A workspace-wide
   Deployer still covers every environment, which is `_covers`' uniform rule for every scope
   (`rbac.py:207-208`). A workspace-wide assignment remains "a deliberate choice"
   (`ScopeType`'s docstring). This meets `CR-1212` item 4 and the planned case: a Deployer
   whose grant names only `uat` is refused on `prod`.
2. **The deploy route checks in the handler, with the target Environment as the resource.**
   It calls `rbac.require_permission(..., permission=Permission.DEPLOYMENT_PROMOTE,
   resource=ResourceRef(ScopeType.ENVIRONMENT, <environment id>))`. It **must not** rely on a
   bare `requires(Permission.DEPLOYMENT_PROMOTE)` dependency. With no resource, `_covers`
   admits only a workspace-wide grant (the table above), so a `uat`-only Deployer would be
   refused in `uat` too. (This handler check is a `permission=` site, so the permission-parity
   check's AST leg counts it, per #942's ruling.)
3. **Why not (b) or (c).**
   - (b) would honour `deployment:promote` only through an environment-scoped grant. That
     makes one permission an exception to `_covers`' rule for every other scope, and strands
     every existing workspace-wide Deployer. `CR-1212` item 4 asks that the permission *can*
     be scoped to named environments, not that it *must* be.
   - (c) puts a list of environments on one assignment. The assignment's shape is one
     `scope_type` and one `scope_id`, and several assignments already express several
     environments.
4. **The spec change, in Slice 2's spec-first commit:** `06` FR-345's list of scopes gains
   "or Environments", dated, citing this record and `CR-1212` item 4. `06` §4.1's assignment
   example may show an `environments` scope. `ScopeType` is a `model-schema` enum, so the
   contract is regenerated.
5. **Acceptance, red first:**
   - a Deployer assigned only to `uat` deploys in `uat` and is refused on `prod`;
   - a workspace-wide Deployer deploys to both;
   - with the handler's resource argument removed, the `uat`-only Deployer is refused in
     `uat` as well, and the test fails;
   - a Service Account is still refused (FR-347).

### C. A dated amendment to the OQ-1234 ruling (#935, working id 9901, minted on its branch as the next ruling id)

**This record amends it; it does not reinterpret it** (the 11:04:57 BST entry's condition).
That ruling's item 3 says the reason for a skip "is the **predecessor-deployment evidence
item** (for `prod`, the `uat_deployment` item) … **pinned at submission**, as every evidence
item is (FR-352, FR-356)". It also says "the `03` Deployment record references the approval
that carries it". It assumed an evidence item held **on the approval request**. **No such
home exists:** `ApprovalRequestRow` has no evidence column, and no `ArtifactRef` can name a
deployment (the table above).

**Amended 2026-09-30:** the predecessor-deployment evidence item, including a skip record
and its reason, is pinned on the **Deployment Request** row of item A. That row is the
subject of the `deployment` approval request. The rest of that ruling stands unchanged: where
the permission lives, the one predicate reading only its arguments, and the reason always
required.

**The form, as the entry asked "say which": an item in this record**, with `corrects:`
naming the OQ-1234 ruling. That ruling is not yet on `main` at this record's tree, so its id
would not resolve here. **At this record's mint turn, the lead sets `corrects:` to that
ruling's minted id**, and appends this record's id to that ruling's `corrected_by:`. Check 34
permits appending there on a written-once record, and requires the pair to point at each
other.

## What it obliges

- **This commit:** this record only. The spec and contract changes are Slice 2's spec-first
  step (A.1, B.4).
- **WK-674 Slice 2 (the leaf plan, PL working id 9920):**
  - the Deployment Request row and its reference type (A.1);
  - the pinned evidence and its checks (A.2);
  - the FD-1200-class acceptance (A.4) and the deploy route's use of the request (A.5);
  - `ScopeType.ENVIRONMENT` and the handler's resource check (B), with the `06` FR-345
    amendment and the contract regeneration.
- **The lead:** at the mint turn, the `corrects:`/`corrected_by:` pair of item C. And
  planner-924 re-reads its draft against items A and B.

## Acceptance — the violation that must become detectable

The violations: **a deployment approved without its pinned evidence, evidence changed after
submission, a second writer of `approved`, or a Deployer acting outside the Environments its
grant names.** In WK-674 Slice 2, each is shown failing on deliberately broken input
(`CLAUDE.md` §13):
- item A.4's cases: approval without pinned evidence; an evidence update after submission;
  and the model-derived one-writer check, red on a planted second writer on the
  deployment-request table, a planted non-literal status write and a planted
  `default="approved"`, green on the live tree only through its pinned two-entry baseline;
- item A.5: a deploy to an approval-gated target naming no approved Deployment Request is
  refused. A request whose pinned predecessor item no longer satisfies FR-429's predicate is
  refused at the route;
- item B.5's four cases.
