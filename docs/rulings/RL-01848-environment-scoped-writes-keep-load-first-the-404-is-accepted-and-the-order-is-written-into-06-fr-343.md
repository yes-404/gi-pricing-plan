---
id: RL-1848
family: ruling
title: "Environment-scoped writes keep load-first: the 404-before-403 existence answer is accepted within a deployment, and the order rule is written into 06 FR-343 (adopted by the maintainer 2026-10-22 17:21:38 BST, with one amendment)"
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

# RL-1848 — Environment-scoped writes keep load-first: the 404-before-403 existence answer is accepted within a deployment, and the order rule is written into 06 FR-343

Drafted 2026-10-22 under working id 8176 on branch `draft/rl-8176`. It is not minted here and
carries no INDEX hunk.

**Adopted by the maintainer, 2026-10-22 17:21:38 BST, with one amendment.** The authority is the
maintainer's entry "2026-10-22 17:21:38 BST — Maintainer: RL-1848 ADOPTED, option (A) with one
amendment; the RESOURCE_BACKED guard as a test; FD-1852 probe GO" in
`~/gi-pricing-plan.local/channel/to-lead.md` (local). Its item 1, copied by `sed`, unedited:

> 1. **RL-1848** (draft/rl-8176 @00c5b9fb, dm-8176) is **ADOPTED: (A), keep load-first** for Environment-scoped writes, with no code change. 06 FR-343 gets the dated order clause at the mint. **AMENDMENT:** the revisit triggers add "**any role, built-in or custom, that holds an Environment-scoped write permission without `settings:read`**". The built-in-only trigger misses custom roles, and that is exactly who the 404 would tell something new. FD-1851 = **LOW**; it closes as accepted, citing the minted RL. Its authority is this entry.

Its items 2–4 rule the guard, custom roles and the dataset observation. They are applied below
under "What it obliges" and "Acceptance". The draft was adopted at @00c5b9fb. The provenance
paragraph that follows was added after that, at 167c1ae1, and changes no ruled content. This
commit applies the adoption and the amendment.

**Provenance — the effort level.** The seat was spawned by lead 26 at effort `high`, as
`.claude/roles/decision-maker.md`'s "Model / effort" line provides for a decision-maker
ruling on the maintainer's raise. In the seat's own shell, `echo $CLAUDE_EFFORT` printed
`medium` (read 2026-10-22 17:14:17 BST). The seat reported the difference to the lead. The
lead said it would record it in `from-lead` and told the seat to work to the `high`
standard. Which effort the session actually ran at is not verified here.

**The question.** The maintainer's entry "2026-10-22 17:13:03 BST — Maintainer: the 404-vs-403
order on env-scoped writes goes to a DECISION-MAKER for an RL; FD-1851 is filed; SL-1260 is not
blocked" in `~/gi-pricing-plan.local/channel/to-lead.md` (local; copied by `sed`, unedited):

> - **Seat a decision-maker (opus)** to draft an RL: should Environment-scoped writes converge on permission-first (403 before 404), or is the existence oracle accepted within a workspace? Options, trade-offs (consistency, RL-1301 B.2's resource choice, test churn, what an attacker learns) and one recommendation. If it recommends convergence, it names the owner Work and a slice; it does not sit in SL-1260. I adopt or amend it.

and, from the same entry:

> - **FD-1851:** filed in the next docs batch. Its severity is **proposed by the decision-maker below**, not assumed MEDIUM; within an authenticated workspace, Environment slugs may not be sensitive.

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
"What it obliges", item 6, for a side observation on that route, now FD-1852.)

## Ruled

*Recommended as (A); adopted by the maintainer 2026-10-22 17:21:38 BST, with the amendment to the revisit trigger below.*

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
  does not list;
- **any role, built-in or custom, that holds an Environment-scoped write permission without
  `settings:read`** *(added by the maintainer's amendment, 2026-10-22 17:21:38 BST, item 1: "The
  built-in-only trigger misses custom roles, and that is exactly who the 404 would tell something
  new.")*.

**If (C) is ever needed (convergence) — not adopted on 2026-10-22; kept as the trigger's answer: owner and slice.** The owner Work is **WK-674**,
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

*Option (A), as adopted 2026-10-22 17:21:38 BST with the maintainer's amendment.*

1. **The spec change, by the decision-maker, in the batch PR that mints this record (spec first,
   with the record in the same commit).** `06` FR-343 (`docs/specs/06-governance.md`:79) gains this
   dated clause, verbatim (it carries the maintainer's amended trigger):
   > *(Amended <date>, RL-<n>.)* **Order:** a route's permission check precedes any lookup of an id
   > its path names, so a caller without the permission is refused with 403 whether or not the id
   > exists. **One exception:** where the permission is checked with an **Environment** as the
   > resource (FR-345; `RL-1301` B.2), the Environment is loaded first, and an unknown slug is 404
   > `NOT_FOUND` for every caller. Environments are deployment-wide (`00` FR-16) and can be listed
   > under `settings:read` (`07` FR-428), so the 404 tells a caller nothing it cannot list. The
   > exception lapses if Environments become per-workspace, or if **any role, built-in or custom,
   > holds an Environment-scoped write permission without `settings:read`**.
2. **No code and no test changes.** SL-1260 is unaffected. Its two writes already follow the rule.
3. **FD-1851: severity LOW; it closes as accepted, citing this record once minted** (ruled, the
   maintainer's 17:21:38 entry, item 1). This record does not close it here (it is not minted,
   and FD-1851 is not on this branch).
4. **The `RESOURCE_BACKED` guard: ruled YES, as a test** (the maintainer's 17:21:38 entry, item 2).
   A test asserts that every `RESOURCE_BACKED` key in
   `backend/tests/test_api_authorisation_sweep.py` names an `/api/v1/environments/{env}/` path.
   It is shown **red first** on an injected non-Environment path.
   - **Owner:** FD-1851's close vehicle, a WK-1178 delta row, test-only and small. **Not SL-1260.**
     The working ids SL 8178 / LG 8179 are the lead's relay (lead 26, 2026-10-22). They are not in
     the maintainer's entry and are not verified here.
   - **Stop condition,** from the entry, verbatim: "If it fails on main today, STOP and report."
5. **Custom roles without `settings:read`:** covered by the amendment in item 1's clause (the
   maintainer's entry, item 3: "No further action now").
6. **The dataset dictionary route: raised here; tracked as FD-1852. Not ruled here.** The
   maintainer GO'd a red-first probe under FD-1852 (the 17:21:38 entry, item 4). The observation,
   as raised: `PUT /datasets/{slug}/dictionary` has a
   route-level `requires(Perm.DATASET_WRITE)` (`datasets.py`:88) and a dataset-scoped check in the
   handler (`platform/datasets.py`:282). Because `requires()` passes no resource and `_covers`
   returns False for a scoped assignment when the resource is `None` (`rbac.py`:209–212), a
   principal whose `dataset:write` grant is scoped to that one dataset appears to be refused at
   the route before the handler's scoped check runs. This is the failure RL-1301 B.2 item 2 names
   for Environments. I read it in the source only and did not test it.

**Not decided here:** the existence policy for a read route (none was in the survey), and FD-1852's
outcome.

## Acceptance — the violation that must become detectable

The violation: **a route that looks up an id from its path before its permission check, where that
id is not an Environment, so that a caller without the permission gets 404 instead of 403.** The
existing check is `test_every_operation_refuses_a_caller_holding_no_roles`
(`backend/tests/test_api_authorisation_sweep.py`:367 ff.). It fills every path parameter with an
unknown UUID (`_concrete`, `:174–186`) and asserts 403 with the role-check code. Such a route reds
it unless the route is listed in `RESOURCE_BACKED`.

- *Violation: a non-Environment route listed in `RESOURCE_BACKED` to make that test pass.* No check
  catches this at 71e481fa. **Ruled 2026-10-22 17:21:38 BST:** a guard test asserts that every
  `RESOURCE_BACKED` key's path starts with `/api/v1/environments/{env}/`. It is shown red first on
  an injected non-Environment path, and lands in FD-1851's close vehicle (a WK-1178 test-only delta;
  "What it obliges" item 4). This seat runs no tests, so the guard has not been shown red here.
- The sweep's own red on a load-first non-Environment route was not re-run here (this seat runs no
  tests). Its docstring (`:1–10`) records the class of injection it was built to catch.
