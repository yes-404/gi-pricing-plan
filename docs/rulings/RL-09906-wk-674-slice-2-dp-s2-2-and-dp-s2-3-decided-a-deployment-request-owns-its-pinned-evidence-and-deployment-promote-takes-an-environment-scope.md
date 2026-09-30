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
| The policy is keyed `deployment` | **present** | `EVIDENCE_FLOOR["deployment"] = ("rating_version_approval", "uat_deployment")` (`packages/model-schema/src/model_schema/approvals.py:107`). `approvals.submit` looks up `policy.entry_for(artifact_ref.type, environment)` (`backend/src/app/platform/approvals.py:226`). A `deployment` entry can therefore never be reached by a request whose ref must be one of `ARTIFACT_TYPES`. |
| An evidence column on the approval request | **absent** | `ApprovalRequestRow` (`backend/src/app/db/models.py:611-640`), read. Its columns are `id`, `workspace_id`, `artifact_ref`, `artifact_type`, `environment`, `submitted_by`, `submitted_at`, `change_summary`, `status`, `approvers_required`, `withdrawn_reason` and `decided_at`. None holds evidence. |
| Where evidence lives today | **present, on the owning module's row** | `rating_versions.submit_for_review` writes `row.evidence` on the Rating Version's own row, then calls `approvals.submit` (`backend/src/app/platform/rating_versions.py:294-300`). Generic `approvals.submit` (`platform/approvals.py:192-282`) checks the policy entry and the reference, and nothing else. |
| The single decision path | **present** | `api/approvals.py`'s decide and withdraw routes call `_carry_to_the_artifact` (`:260`, `:293`, defined `:488`). It drives each owning module's `apply_approval_decision`, for example `rating_versions.py:312`, which writes the row's status at `:360` (`row.status = target.value`) from the mapping whose `APPROVED` entry is `:382`. The status itself comes from `_resolve_status` (`platform/approvals.py:547-554`). |
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
   - **Only the single decision path writes `approved`: on every approval-capable table,
     derived, attributed exactly, and failing closed.** *(Restated 2026-09-30, and superseding
     the versions at `fa49e06c` and `324ea165`. The maintainer's entries "11:21:51 BST — …
     three rulings" (derive from approval-status enums) and "11:22:45 BST — A.4 residual
     (record_certificate conditionals): steer WIDEN, not baseline" decide the population and
     the widening. auditor-close1255 implemented the earlier text and ran it at
     `9f63d0fe`, finding 5 red sites outside the baseline: `datasets.py:581`,
     `jobs.py:226`, `traces.py:252`, `metrics.py:459` and `objectives.py:532`. Each is
     closed below.)*
     1. **The population is derived from approval-status enums.** Every mapped class under
        `app.db.models.Base` with a `status` column **declares that column's vocabulary**:
        the `StrEnum` its values come from, as column metadata (for example
        `info={"status_vocabulary": RatingVersionStatus}`). A status column with no declared
        vocabulary fails the check, so no table escapes by omission. **The population is
        every class whose declared vocabulary has an `APPROVED` member.** At `9f63d0fe`,
        the enums with one are `ApprovalStatus` (`model_schema/approvals.py:41`),
        `MetricStatus` (`metrics.py:48`), `ModelStatus` (`modelling.py:1975`),
        `ObjectiveStatus` (`objectives.py:137`), `PerilStructureStatus` (`perils.py:94`) and
        `RatingVersionStatus` (`rating.py:31`).
        - The validation tables hold their vocabulary as string constants
          (`platform/validation_rules.py:65`, `DRAFT, REVIEW, APPROVED = "draft", "review",
          "approved"`), not an enum. So Slice 2 declares a `StrEnum` of those same values
          for `validation_rules` and `validation_rule_sets`, which brings both into the
          population.
        - `jobs` (`JobStatus`), `dataset_versions` (`DatasetStatus`) and `scoring_traces`
          have no `APPROVED` member, so the writes at `jobs.py:226`, `datasets.py:581` and
          `traces.py:252` fall outside the population by construction.
        - The Deployment Request table declares its vocabulary and joins by having
          `APPROVED`.
     2. **Attribution: every write is tied to its table, or it fails.** A status write
        found by the AST walk over `backend/src` is attributed to a mapped class by:
        - a constructor `XRow(..., status=…)`;
        - a `<name>.status = …` where `<name>` is annotated with a mapped class, or was
          bound in the same function from `session.get(XRow, …)` or a `select(XRow)`
          result.

        A write attributable to no class **fails closed**, and the author adds the
        annotation. A column `default=` or `server_default=` of `"approved"` is a write
        on its own class, for example `models.py:1195`.
     3. **Which writes can produce `approved`.** Each write's possible values are evaluated
        statically:
        - a string literal;
        - an enum member, or its `.value`;
        - a module-level name bound to a literal (as `validation_rules.py:65` binds
          `APPROVED`);
        - a conditional, which is the union of its branches;
        - a name annotated with an enum type, which is all that enum's members;
        - a lookup in a module-level dict literal, which is its values.

        **A write is ignored if and only if every value it can produce is a non-approved
        member of its table's vocabulary.** This covers `record_certificate`'s
        `(X.DRAFT if failed else X.CERTIFIED).value` at `metrics.py:459` and
        `objectives.py:532` (the WIDEN steer, rather than baseline entries). Any other
        write is "possibly approved", an unknown value included, which fails closed.
     4. **The rule:** on a population table, every possibly-approved write sits in that
        table's `apply_approval_decision` reached from `_carry_to_the_artifact`
        (`api/approvals.py:488`, carrying at `:499-517`). For `approval_requests`, it sits
        in `platform/approvals.py`'s decision path (`_resolve_status`, `:547-554`).
     5. **Red first:**
        - a planted second writer of `approved` on the deployment-request table;
        - a planted conditional with an `APPROVED` branch, for example
          `(X.APPROVED if ok else X.DRAFT).value`, which is caught;
        - a planted unattributable status write;
        - a planted `default="approved"`;
        - a status column planted with no declared vocabulary.

        Each fails the check.
     6. **Zero writers passes, and is reported as a note.** "At most one path writes
        `approved`" is satisfied by a table nothing approves. `peril_structures` is one:
        auditor-close1255 found only `review` (`perils.py:338`) and `reconciled`
        (`:256`) written. Whether its `approved` state is reachable is not ruled here, and
        is offered to the lead.
     7. **The baseline: exactly the three validation writers, named, dated 2026-09-30,
        temporary and shrink-only**, pinned as a literal citing the finding filed under the
        maintainer's 11:14:48 BST DEFECT entry (in prose until minted). Any
        possibly-approved writer not in the literal fails:
        - `approve_rule` (`platform/validation_rules.py:395`), writing at `:423`, reached
          by `api/validation.py:359`;
        - `seed_builtin_rules` (`:89`), constructing at `:132` with `status=APPROVED` at
          `:154`;
        - `replace_rule_set` (`:538`), constructing `ValidationRuleSetRow` at `:621` with
          `status=APPROVED` at `:643`. The column default `models.py:1195` on the same
          class belongs to this entry.

        **The WK-1178 fix slice removes each entry red first.** `replace_rule_set`'s entry
        waits on that finding's triage. If the triage finds rule sets legitimately
        ungoverned (they are absent from `06:64`), it becomes a permanent exemption carrying
        that spec citation, and otherwise it is removed like the others. The Deployment
        Request table has no entry.
5. **The deploy route executes only an approved request.** For a target whose deployments are
   approval-gated, `POST /api/v1/environments/{env}/deployments` names an **approved**
   Deployment Request and re-evaluates FR-429's one predicate from the request's **pinned**
   evidence. It never re-reads a changeable source. A target with no `deployment` policy
   entry needs no request. For it, the predicate reads the predecessor's successful
   Deployment directly, and no skip is possible (the OQ-1234 ruling, item 1).

6. **A3 — the approval policy must not resolve through a renamable name** (auditor-close1255's
   advisory, ruled on the maintainer's 11:14:48 BST steer).
   - **The hazard:** `ApprovalPolicyEntry.environment` is a string
     (`packages/model-schema/src/model_schema/approvals.py:119-121`), `entry_for` matches on
     it, and `ApprovalRequestRow.environment` is `String(32)` (`models.py:627`). `06` §4.1
     gives `admin:manage_environments` the Environment's "create, rename, retire". A rename
     would make the `prod` entry resolve to nothing, and under item 5 a target with no
     `deployment` entry needs no request. **A rename would ungate `prod` silently.**
   - **Ruled: policy resolution keys on an identity that a rename cannot change.** Every
     Environment has an **immutable `slug`** and a mutable display `name`. **The split, and the
     slug's immutability, are this ruling's own decision**, carried into `07` §4 by Slice 2's
     spec-first commit. `00` ID-1 (`00-overview.md:279`) gives only that a slug is "unique
     within its parent scope", and `07` FR-428 gives an Environment a name but no slug.
     *(Recast on auditor-close1255's nit, which found that this item first cited ID-1 for
     the immutability.)* The
     approval policy's `environment`, `ApprovalRequestRow.environment`, the deploy route's
     `{env}` and every Environment reference name the **slug**. `07` FR-428's rename changes
     the `name` only. **A change of slug is refused**, because it would change which policy
     entry resolves. This is the maintainer's steer, keying by identity and refusing a
     resolution-changing rename, met by one mechanism. The slug is also what the item 1
     reference and the OQ-1234 ruling's "environment-qualified" entry mean.
   - **The policy may not name an Environment that does not exist.** `set_policy` refuses an
     entry whose `environment` is not an existing Environment's slug. Otherwise a typo
     (`prd`) would ungate the real target as silently as a rename. **Environments are
     deployment-wide, not per workspace.** `07` §4.2's Environment has no workspace field;
     a Service Account's key lists environment names with no workspace
     (`models.py:397-398`); and ADR-710 makes the deployment the tenant boundary
     (`backend/src/app/api/deps.py:26-27`). *(Worded on the leaf plan's rev 4 question. This
     item first said "the workspace's Environments", which was loose wording and not a
     design difference.)*
   - **Two leaf-plan choices, both consistent with this ruling** (rev 4, `4bde1cfb`):
     - the Deployment Request's slug is its target Environment's immutable slug
       (`deployment:prod@3`). That meets item A.1's constraint, because that slug cannot
       be renamed;
     - retiring an Environment that a policy entry names is refused with 409. Item A.6
       left retirement to the plan, and this is a sound answer.
   - **This item disposes of the leaf plan's DP-S2-5** (A3: Environment rename versus the
     policy key), which planner-924 opened for this ruling. The planner may close it citing
     this item.
   - **Red first:** rename `prod`'s display name, and a deploy to it still requires its
     approved Deployment Request. A request to change `prod`'s slug is refused. A policy
     naming `prd` is refused by `set_policy`. With resolution keyed on the display name,
     the first test fails.

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
  and the one-writer check of item A.4, red on each plant of its sub-item 5, and green on the
  live tree only through its pinned three-writer baseline;
- item A.5: a deploy to an approval-gated target naming no approved Deployment Request is
  refused. A request whose pinned predecessor item no longer satisfies FR-429's predicate is
  refused at the route;
- item A.6's three cases: a display rename keeps `prod` gated; a slug change is refused; a
  policy naming a non-existent environment is refused;
- item B.5's four cases.
