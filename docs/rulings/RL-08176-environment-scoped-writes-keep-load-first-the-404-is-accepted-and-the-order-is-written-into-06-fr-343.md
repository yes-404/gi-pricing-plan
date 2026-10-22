---
id: RL-8176
family: ruling
title: "Environment-scoped writes keep load-first: the 404-before-403 existence answer is accepted within a deployment, and the order rule is written into 06 FR-343 (draft for the maintainer to adopt or amend)"
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-10-22   # drafted 2026-10-22 under working id 8176; not minted
owner: decision-maker
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1301, RL-1834, RL-1401, RL-1687, SL-1260]
---

# RL-8176 — Environment-scoped writes keep load-first: the 404-before-403 existence answer is accepted within a deployment, and the order rule is written into 06 FR-343

Drafted 2026-10-22 under working id 8176 on branch `draft/rl-8176`. **This is a draft for the
maintainer to adopt, amend or reject.** It rules nothing until the maintainer adopts it with a
dated line. It is not minted here and carries no INDEX hunk.

**The question.** The maintainer's entry "2026-10-22 17:13:03 BST — Maintainer: the 404-vs-403
order on env-scoped writes goes to a DECISION-MAKER for an RL; FD 8175 is filed; SL-1260 is not
blocked" in `~/gi-pricing-plan.local/channel/to-lead.md` (local; copied by `sed`, unedited):

> - **Seat a decision-maker (opus)** to draft an RL: should Environment-scoped writes converge on permission-first (403 before 404), or is the existence oracle accepted within a workspace? Options, trade-offs (consistency, RL-1301 B.2's resource choice, test churn, what an attacker learns) and one recommendation. If it recommends convergence, it names the owner Work and a slice; it does not sit in SL-1260. I adopt or amend it.

and, from the same entry:

> - **FD 8175:** filed in the next docs batch. Its severity is **proposed by the decision-maker below**, not assumed MEDIUM; within an authenticated workspace, Environment slugs may not be sensitive.

## Verified first, at 71e481fa (main) and 6aa350c7 (`origin/sl-1260-wk674-s6`)

Every line below was read at the tree named. Paths are repository-relative.

**1. The load-first sites (unknown slug → 404 before any permission check).**

- `backend/src/app/platform/deployments.py`:130–131 at 71e481fa, in `_authorised_environment`:
  `:130` "env = await environments._load(session, slug, lock=lock)", then `:131` "await
  rbac.require_permission(" with `permission=Permission.DEPLOYMENT_PROMOTE` and
  `resource=rbac.ResourceRef(scope_type=ScopeType.ENVIRONMENT, scope_id=env.id)`. Its callers are
  `:274` (submit a Deployment Request), `:555` (deploy) and `:728` (rollback). `_load`
  (`backend/src/app/platform/environments.py`:142–149) selects by slug only and raises
  `_not_found(slug)` when no row matches.
- On SL-1260's branch at 6aa350c7: `backend/src/app/platform/routing.py`:77 "env = await
  _authorised_environment(" (the routing write uses the same helper), and
  `backend/src/app/platform/shadow.py`:66 "env = await environments._load(session, environment)"
  then `:67` "await rbac.require_permission(" with `Permission.ADMIN_MANAGE_SETTINGS` and the
  Environment as the resource. The shadow docstring lists the refusals in this order: "unknown
  Environment 404; no `admin:manage_settings` on it 403; retired 409".
- None of these routes has a route-level `requires(...)`. The sweep test lists them as
  handler-checked: `backend/tests/test_api_authorisation_sweep.py`:93–108 at 71e481fa (the three
  deployment routes, each pointing at `platform/deployments.py`, 131); at 6aa350c7, `:107–113`
  adds `PUT …/{env}/routing` and `PUT …/{env}/shadow` (`platform/shadow.py`, 67).

**2. The permission-first sites (403 before 404).**

- `backend/src/app/api/environment_settings.py`:33 "ManageSettings = Annotated[Caller,
  Depends(requires(Perm.ADMIN_MANAGE_SETTINGS))]", used by `PUT /{slug}/settings` at `:60`. The
  dependency runs before the handler reads the slug.
- `backend/src/app/api/environments.py`:33–34 "ManageEnvironmentsDep = Annotated[ Caller,
  Depends(requires(Permission.ADMIN_MANAGE_ENVIRONMENTS))". The services it gates then call
  `_load` at `backend/src/app/platform/environments.py`:258 (update) and `:362` (retire).
- Why the two families differ: `requires()` (`backend/src/app/api/authz.py`:170–210) calls
  `rbac.require_permission` with **no resource**. `_covers` (`backend/src/app/platform/rbac.py`:205–215)
  returns True for a workspace-wide assignment and False for any scoped assignment when the
  resource is `None`. So a route dependency can only check a workspace-wide grant. These routes'
  permissions (`admin:manage_settings` for settings, `admin:manage_environments`) are not checked
  against an Environment, so nothing needs to be loaded first.

**3. Why the deployment routes load first: RL-1301 B.2.**
`docs/rulings/RL-01301-…-deployment-promote-takes-an-environment-scope.md`:515–520, B.2: "**The
deploy route checks in the handler, with the target Environment as the resource.** … It **must
not** rely on a bare `requires(Permission.DEPLOYMENT_PROMOTE)` dependency. With no resource,
`_covers` admits only a workspace-wide grant …, so a `uat`-only Deployer would be refused in
`uat` too." To build that `ResourceRef`, the check needs the Environment's id. Today the id comes
from the loaded row. RL-1834 D2 item 3 (`docs/rulings/RL-01834-…`:219–221) gives the shadow route
the same form: "`admin:manage_settings`, Environment as resource … Refusals …: unknown
Environment 404 `NOT_FOUND`". Neither ruling states the order between the 404 and the 403.

**4. What the existence answer discloses.**

- Environments are deployment-wide: `backend/src/app/db/models.py`:2824 "**Deployment-wide, not
  per workspace** (ADR-710): there is no `workspace_id`." `docs/specs/00-overview.md`:229, FR-16:
  "**One tenant, one deployment — permanently**". `:2829`: "The migration seeds `dev`, `uat` and
  `prod`."
- Environments can be listed under `settings:read`: `backend/src/app/api/environments.py`:36
  "ReadEnvironmentsDep = Annotated[Caller, Depends(requires(Permission.SETTINGS_READ))]", and
  `:5` "List, retired ones included". `docs/specs/06-governance.md`:292 defines `settings:read`
  as "Reading workspace settings, and listing and reading Environments".
- Every built-in role holds `settings:read`: `packages/model-schema/src/model_schema/permissions.py`:82–91
  (`READ_PERMISSIONS` includes `Permission.SETTINGS_READ`). `:111–126` (`_analyst`, which
  `pricing_actuary` extends) lists it. `:145–148`: approver, deployer, auditor and admin are each
  `frozenset(READ_PERMISSIONS) | …`.
- The 403 already names the Environment. `backend/src/app/platform/rbac.py`:90 "where = f\" on
  {resource.scope_type.value}:{resource.scope_id}\" if resource else \"\"", and `:96` places it in
  the `SCOPE_DENIED` detail ("You hold {permission.value} but not{where}."). A principal who holds
  the permission on another Environment therefore learns both that the slug exists and its id.
  *I read this in the source only. I did not issue a request to confirm the detail reaches the
  RFC 9457 body (this seat runs no tests).*

**5. What the platform's own check says, and the exception it already makes.**
`backend/tests/test_api_authorisation_sweep.py`:177–178 at 71e481fa, `_concrete`'s docstring:
"The refusal must precede the lookup: a 404 for a caller who should have been refused would tell
them the id does not exist, which is itself an answer they had no right to." `:372–373`: "`403`,
not `404` and not `422`: the permission check must resolve before the handler touches an id or a
body, or the refusal leaks whether the id exists." The Environment routes are excepted by
`RESOURCE_BACKED` (`:299–312`), which fills `{env}` with the real slug `"dev"`, so the role-less
sweep still proves that each route refuses with 403. The exception is in the test with its reason
(`:297`: "the Environment is the resource of `deployment:promote`, `RL-1301` B.2"). No spec
states it.

**6. No spec states the 404/403 order.** Predicate, run over `docs/specs/*.md` at 71e481fa:
`grep -rn -i "404 before 403\|403 before 404\|before the permission\|after the permission\|existence oracle\|enumerat\|reveal.*exist\|leak.*exist" docs/specs/*.md`.
Each hit was read, and none states an order between a 404 and a 403. The nearest is `03` §4.12
(`docs/specs/03-rating-engine.md`:1024): "The refusal [retired, 409] comes after the permission
check and before the Rating Version is read. An unknown slug is 404 `NOT_FOUND`." It orders the
409, not the 404. `06` FR-343 (`docs/specs/06-governance.md`:79) says only that "Permissions are
checked in the backend on every request against `(principal, permission, resource, scope)`."

**7. The other resource-scoped writes are permission-first.** For example, `PUT
/datasets/{slug}/dictionary`: `backend/src/app/api/datasets.py`:88 "WriteDatasets =
Annotated[Caller, Depends(requires(Perm.DATASET_WRITE))]" runs before
`backend/src/app/platform/datasets.py`:281 `load_dataset` and the scoped check at `:282`. (See
"What it obliges", item 4, for a side observation on that route.)

## Ruled

*Recommended; the maintainer adopts or amends.*

**Option (A) is recommended: the existence answer is accepted for Environment-scoped writes, and
the rule is written into the spec.** An Environment-scoped write loads the Environment and then
checks the permission with that Environment as the resource. An unknown slug is 404 `NOT_FOUND`
for every caller, including one who holds no grant. This is the current behaviour at every site
in "Verified first" items 1–2, so no code changes.

**The options considered.**

| | (A) Accept the oracle, write the rule | (B) Bare route dependency | (C) "Held anywhere" pre-check, then load | (D) 404 for both unknown and out-of-scope |
|---|---|---|---|---|
| **Order** | load → 404; check → 403 | 403 → load → 404 | `holds_anywhere` → 403 `PERMISSION_DENIED`; load → 404; scoped check → 403 `SCOPE_DENIED` | load; any refusal → 404 |
| **RL-1301 B.2** | kept | **breaks it**: B.2 item 2 forbids a bare `requires(DEPLOYMENT_PROMOTE)`, and a `uat`-only Deployer is refused in `uat` | kept: the scoped check is unchanged; the pre-check uses `rbac.holds_anywhere` (`rbac.py`:219), which already exists | kept, but it removes `SCOPE_DENIED`'s actionable distinction (`rbac.py`:76–81; `06` §5.1) |
| **Consistency** | the platform rule becomes "permission first, except where the resource is an Environment"; stated in `06` FR-343 and already in the sweep's `RESOURCE_BACKED` | uniform | uniform for a caller with no grant; a principal holding the permission on another Environment still sees 404 vs 403 | departs from every other route |
| **Test churn** | none; the sweep comment may later cite FR-343 | rewrites RL-1301's acceptance tests | one helper (`_authorised_environment`) and its twin in `shadow.py`; the five `RESOURCE_BACKED` Environment entries can be removed so the sweep runs those routes with unknown slugs; new red-first tests for the pre-check | wide: every 403 assertion on these routes |
| **What a caller learns** | whether a slug exists. Every built-in role can already list all Environments, retired included (item 4) | nothing | a no-grant caller learns nothing; a caller holding the permission elsewhere learns existence and the id (item 4, `rbac.py`:90) | nothing |

**Why (A).**

1. **The answer discloses nothing new.** Environments are deployment-wide (FR-16, ADR-710), and
   `dev`, `uat` and `prod` are seeded. `GET /api/v1/environments` already returns every
   Environment, retired ones included, to any caller holding `settings:read` workspace-wide. Every
   built-in role holds it (item 4). The rule the sweep protects is that an id must not be
   confirmed "to a caller who should have been refused". It protects ids whose existence is
   itself access-controlled, such as datasets and models. An Environment slug is not one of them.
2. **The order follows from RL-1301 B.2.** The scoped check needs the Environment's id, and the
   `SCOPE_DENIED` detail names it. Option (C) closes the existence answer only for a caller with no
   grant. That caller can list the same Environments under `settings:read`, so (C) adds a check
   to every Environment-scoped write and protects nothing.
3. **(A) costs nothing now and does not touch SL-1260.** (C) would need a new WK-674 slice inside
   Phase 2's freeze band.
4. **(A)'s real cost is that the exception lives only in a test.** That is fixed by writing it into
   `06` FR-343 (below). The exception then stops being a silent carve-out and becomes a cited
   rule with a revisit trigger.

**Why not (B) or (D).** (B) undoes RL-1301 B.2's decision, which is not reopened here. (D) hides
existence but deletes the `PERMISSION_DENIED` / `SCOPE_DENIED` distinction. `06` §5.1 owns both
codes, and the sweep asserts the code, not only the status (`test_api_authorisation_sweep.py`:378, "The code is asserted, not just the status").

**The revisit trigger.** (A) holds only while an Environment is deployment-wide and every caller
who can reach an Environment-scoped write can also list Environments. Any one of these reopens the
question, and the answer is then (C):

- an Environment gains a `workspace_id`, or FR-16 or ADR-710 changes;
- a built-in role loses `settings:read`;
- an Environment-scoped route is added whose 404 would reveal something `GET /api/v1/environments`
  does not list.

**If the maintainer amends to (C) (convergence): owner and slice.** The owner Work is **WK-674**,
which owns `_authorised_environment` and SL-1260's routing and shadow writes. The fix goes in **a
new WK-674 slice** that the planner cuts as an SL row. It is not SL-1260. It is dispatched after
SL-1260 merges, because it changes SL-1260's `shadow.py`:66–67 and its routing call, and before
SL-1711 (the WK-674 demo slice), so the scripted WF-701 journey runs on the final order. Its
content:

1. In `_authorised_environment` and `shadow.py`'s check, `rbac.holds_anywhere(permission)` runs
   before `_load`. If it is false, the route refuses with 403 `PERMISSION_DENIED`. `RL-1687` (1a)
   still holds, because a 403 is never counted.
2. The five Environment entries leave `RESOURCE_BACKED`.
3. Red first: a role-less caller gets 403 for an unknown slug. The test fails with the pre-check
   removed.
4. `03` §4.12:1024 gains the order.

## What it obliges

*On adoption of option (A).*

1. **The spec change, by the decision-maker, in the batch PR that mints this record (spec first,
   with the record in the same commit).** `06` FR-343 (`docs/specs/06-governance.md`:79) gains this
   dated clause, verbatim unless the maintainer amends it:
   > *(Amended <date>, RL-<n>.)* **Order:** a route's permission check precedes any lookup of an id
   > its path names, so a caller without the permission is refused with 403 whether or not the id
   > exists. **One exception:** where the permission is checked with an **Environment** as the
   > resource (FR-345; `RL-1301` B.2), the Environment is loaded first, and an unknown slug is 404
   > `NOT_FOUND` for every caller. Environments are deployment-wide (`00` FR-16) and can be listed
   > under `settings:read` (`07` FR-428), so the 404 tells a caller nothing it cannot list. If
   > Environments become per-workspace, or a role that can reach such a route cannot list them,
   > the exception lapses.
2. **No code and no test changes.** SL-1260 is unaffected. Its two writes already follow the rule.
3. **FD 8175's disposition: accepted by this ruling.** It is closed citing RL-<n> when both records
   are minted. This record does not close it here (it is not minted, and FD 8175 is not on this
   branch).
4. **A side observation, not ruled here, for the lead.** `PUT /datasets/{slug}/dictionary` has a
   route-level `requires(Perm.DATASET_WRITE)` (`datasets.py`:88) and a dataset-scoped check in the
   handler (`platform/datasets.py`:282). Because `requires()` passes no resource and `_covers`
   returns False for a scoped assignment when the resource is `None` (`rbac.py`:209–212), a
   principal whose `dataset:write` grant is scoped to that one dataset appears to be refused at
   the route before the handler's scoped check runs. This is the failure RL-1301 B.2 item 2 names
   for Environments. I read it in the source only and did not test it. It may be a product defect
   in FR-345's dataset scope. Whether it needs an `FD-` is the lead's call.

**Not decided here:** the existence policy for a read route (none was in the survey). Whether a
custom role without `settings:read` should be guarded is also left open: the revisit trigger
covers built-in roles only. A custom-role check is left to the maintainer (see Acceptance).

## Acceptance — the violation that must become detectable

The violation: **a route that looks up an id from its path before its permission check, where that
id is not an Environment, so that a caller without the permission gets 404 instead of 403.** The
existing check is `test_every_operation_refuses_a_caller_holding_no_roles`
(`backend/tests/test_api_authorisation_sweep.py`:367 ff.). It fills every path parameter with an
unknown UUID (`_concrete`, `:174–186`) and asserts 403 with the role-check code. Such a route reds
it unless the route is listed in `RESOURCE_BACKED`.

- *Violation: a non-Environment route listed in `RESOURCE_BACKED` to make that test pass.* No check
  catches this today. A one-line guard (every `RESOURCE_BACKED` key's path starts with
  `/api/v1/environments/{env}/`) would. Whether to add it, and in which WK-674 slice, is **left to
  the maintainer**. This seat runs no tests, so the guard has not been shown red. Under (C) the
  guard is not needed, because `RESOURCE_BACKED` loses its Environment entries.
- The sweep's own red on a load-first non-Environment route was not re-run here (this seat runs no
  tests). Its docstring (`:1–10`) records the class of injection it was built to catch.
