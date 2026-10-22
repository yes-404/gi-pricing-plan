---
id: FD-8175
family: finding
title: Environment-scoped writes order 404 before 403 inconsistently; the existence oracle is accepted within a workspace
status: retired
created: 2026-10-22
owner: auditor
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
corrected_by: []
relates: [WK-1178, RL-8176, RL-1301, SL-1260, SL-8178]
---

# FD-8175 — Environment-scoped writes order 404 before 403 inconsistently; the existence oracle is accepted within a workspace

## Finding

**LOW; closed as accepted.** Filed on the maintainer's (by delegation) entry "2026-10-22 17:13:03 BST" (`to-lead.md`),
severity proposed by a decision-maker and set by the entry "2026-10-22 17:21:38 BST". Filed under working id 8175.

Environment-scoped write routes disagree on whether a missing Environment (404) or a missing permission (403) is
reported first. Where the 404 comes first, a caller without the permission learns whether an Environment slug exists.
Within an authenticated workspace, Environment slugs may not be sensitive; hence LOW.

## Evidence

At `origin/main` 71e481fa:

- **Load-first** (existence observable): `backend/src/app/platform/deployments.py` `_authorised_environment`,
  :130 `environments._load(...)` before :131 `rbac.require_permission(... DEPLOYMENT_PROMOTE ...)`; called at :274,
  :555 and :728 (submit_request, deploy, rollback). The maintainer's (by delegation) survey also lists the new routing
  write and a shadow write (`shadow.py :65→:67`); `backend/src/app/api/shadow.py` does not exist at 71e481fa, so that
  item is not verified here.
- **Permission-first:** `PUT /environments/{slug}/settings`, `backend/src/app/api/environment_settings.py` :51-83,
  route-level `ManageSettings` (:33, `requires(Perm.ADMIN_MANAGE_SETTINGS)`) before any load; and Environment update and
  retire, `backend/src/app/platform/environments.py` :258 and :362 (`_load` inside the handler), behind their route-level
  permission in `backend/src/app/api/environments.py`.

## Disposition

**Accepted** (`status: retired`). RL 8176 (`draft/rl-8176` @aab1b741), adopted by the maintainer (by delegation) on
"2026-10-22 17:21:38 BST", chooses option (A): keep load-first for Environment-scoped writes, with no code change;
`06` FR-343 gets a dated order clause at the mint. Its amendment adds a revisit trigger: any role, built-in or
custom, that holds an Environment-scoped write permission without `settings:read`.

The one action that remains is a guard, not a fix: "RESOURCE_BACKED may hold only /environments/{env}/ paths", as a
red-first test (injected non-env path), SL 8178 on `fix/fd-8175-resource-backed-guard` @db0502dd, a WK-1178 delta row,
not SL-1260. If it fails on main, STOP and report. Filed under working id 8175.
