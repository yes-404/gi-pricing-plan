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
   - **Only the single decision path writes `approved`: a runtime guard on every
     approval-capable table.** *(Restated a third time, and superseding the static
     AST-attribution versions at `fa49e06c`, `324ea165` and `327e1179`, on the maintainer's
     entry "11:32:49 BST — three rulings: …; #971 A.4 method; …", item 2. auditor-close1255
     implemented the static version and ran it. Attribution failed closed on 16 of 23
     assignments, including the sanctioned `platform/approvals.py:416`. A runtime guard
     removes the attribution problem, because the ORM knows each row's class and its actual
     value.)*
     1. **The population is derived from approval-status enums** (the 11:21:51 BST entry).
        - Every approval-capable table declares its status column's vocabulary, the
          `StrEnum` its values come from, as column metadata (for example
          `info={"status_vocabulary": RatingVersionStatus}`).
        - The population is every mapped class whose declared vocabulary has an `APPROVED`
          member. At `9f63d0fe`: `ApprovalStatus` (`model_schema/approvals.py:41`),
          `MetricStatus` (`metrics.py:48`), `ModelStatus` (`modelling.py:1975`),
          `ObjectiveStatus` (`objectives.py:137`), `PerilStructureStatus` (`perils.py:94`)
          and `RatingVersionStatus` (`rating.py:31`), and the tables they govern.
        - Slice 2 also declares the vocabulary of `validation_rules` and
          `validation_rule_sets`, through a `StrEnum` of their string constants
          (`validation_rules.py:65`), since they have no enum. And it declares the Deployment
          Request table's.
        - **F-A resolves this way:** a declaration is required only of approval-capable
          tables, and a test asserts it. Every table whose module has an
          `apply_approval_decision` that `_carry_to_the_artifact` drives, and
          `approval_requests`, must declare one with `APPROVED`. `scoring_traces`,
          `ingestion_runs`, `reference_table_versions`, `jobs` and `dataset_versions` need
          none, and the guard does not touch them.
     2. **The guard.** A `before_flush` listener on the ORM `Session` inspects every object in
        `session.new` and `session.dirty` whose class is in the population:
        - **an insert** is refused if its `status` is the `APPROVED` member's value. That
          covers an explicit constructor value, and an unset `status` whose column
          `default=` or `server_default=` is that value (`models.py:1195` is one);
        - **an update** is refused if its attribute history shows `status` changed to that
          value;
        - either is allowed **only while the decision-path context variable is set**.

        A `do_orm_execute` listener refuses an ORM-enabled `update()`/`insert()` statement
        on a population table whose values set `status` to that value outside the context.
        The refusal is a named error raised before the flush writes, so the transaction rolls
        back.
     3. **The decision-path context.** One context manager, `approval_decision()`, in
        `platform/approvals.py`, sets a `ContextVar`. It is entered in exactly two places:
        - `platform/approvals.decide`, around its own write of the request's status at
          `:416`;
        - `api/approvals._carry_to_the_artifact` (`:488`), around the owning module's
          `apply_approval_decision`, which the decide route runs in the same unit of work
          right after `decide` (`api/approvals.py:250-260`).

        A static test asserts that `approval_decision()` is entered nowhere else in
        `backend/src`. This check is by name, which is reliable where the old attribution
        was not.
     4. **What the guard cannot see, and what covers it.**
        - Core `connection.execute` and raw `text()` SQL bypass the ORM events. At
          `9f63d0fe`, no Core or bulk statement targets a population table: the only two,
          `platform/blobs.py:455` and `worker/progress.py:200`, update `BlobRow` and `JobRow`.
          A static test fails any `update(X)`/`insert(X)` over a population class, and any
          `text()` naming a population table's `status`, outside the two sanctioned sites.
        - **A database trigger is not required now.** It becomes the escalation if a Core
          writer to a population table is ever needed.
        - Alembic data migrations run outside the application session and are not covered.
          A migration that writes `approved` rows is a review item for the slice's auditor.
     5. **The exemption: temporary, per table, citing the finding filed under the
        maintainer's 11:14:48 BST DEFECT entry** (in prose until minted). The guard is
        per table, so the exemption is too:
        - **`validation_rules`**, whose writers are `approve_rule` (`:395`, writing at
          `:423`), `seed_builtin_rules` (`:89`, with `status=APPROVED` at `:154`), and the
          demo seed's direct row (`examples/fremtpl2/seed.py:441`);
        - **`validation_rule_sets`**, whose writer is `replace_rule_set` (`:538`,
          `status=APPROVED` at `:643`), plus its column default (`models.py:1195`).

        Both entries are dated 2026-09-30, pinned as a literal, and shrink-only. **The
        WK-1178 fix slice removes them red first.** The rule-set entry waits on the
        finding's triage, and becomes a permanent exemption with its spec citation only if
        rule sets are legitimately ungoverned (`06:64`).
     6. **Test fixtures.** 17 backend test files match
        `git grep -l -E 'status\s*=\s*"approved"|Status\.APPROVED|status=APPROVED' 9f63d0fe --
        backend/tests`. That is an upper bound on the files that write `approved` rows
        directly, since some matches only read or compare. Under the guard they refuse. **Declared Slice 2
        work:** each goes through the decision path, or through a helper that enters
        `approval_decision()` and is defined under `backend/tests/` only. The static test of
        item 3 exempts `backend/tests/` and nothing else.
     7. **Red first:**
        - for **every** population table, derived as in item 1: a direct write of `approved`
          outside the context, on insert and on update, is refused. With the listener
          removed, each write succeeds and the test fails;
        - the deployment-request plant is refused;
        - an insert relying on a `default="approved"` is refused;
        - an ORM bulk `update()` setting `approved` is refused;
        - `approval_decision()` entered at a third site in `backend/src` fails the static
          test;
        - a population table without a declared vocabulary fails the declaration test;
        - **positive control:** the sanctioned decide-and-carry path approves a request and
          its artifact.
     8. **Zero writers.** A population table nothing approves, `peril_structures` today,
        needs no guard and gets a note. Its reachability is the lead's to route (the
        tripwire of the perils finding covers it, per the lead).
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
   - **A credential names only existing Environments.** A Service Account's `environments`
     is a free `list[str]` (`backend/src/app/api/service_accounts.py:63`), and a key is minted
     from `environments[0]` (`:180` at creation, `:246` at rotation). Nothing checks either
     against an Environment, because at this tree there are none to check against. Once
     Slice 2 creates Environment records, the rule is:
     - each name in `environments` must be an existing Environment's slug at creation and at
       rotation, or the request is refused with `VALIDATION_FAILED` 422 naming it;
     - retiring an Environment that an unrevoked Service Account key names is refused with
       409, like one a policy entry names, until the key is revoked or its environments are
       narrowed.

     **Carried by Slice 2**, which creates the Environment records and their retire route.
     `Caller.environment` then always names a real, unrenamable Environment. **Red first:**
     issuing a key for `prd` is refused, and retiring `uat` while a live key names it is
     refused.
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
  and item A.4's runtime guard, red on each case of its sub-item 7, and green on the live
  tree only through its two temporary table exemptions;
- item A.5: a deploy to an approval-gated target naming no approved Deployment Request is
  refused. A request whose pinned predecessor item no longer satisfies FR-429's predicate is
  refused at the route;
- item A.6's three cases: a display rename keeps `prod` gated; a slug change is refused; a
  policy naming a non-existent environment is refused; a Service Account key for `prd` is
  refused; retiring an Environment a live key names is refused;
- item B.5's four cases.
