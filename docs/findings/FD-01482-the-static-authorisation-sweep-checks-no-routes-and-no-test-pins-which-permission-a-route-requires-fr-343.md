---
id: FD-1482
family: finding
title: The static authorisation sweep checks no routes, and no test pins which permission a route requires (FR-343)
status: active
created: 2026-10-08            # original date 2026-09-30, set at the draft; minted 2026-10-08
owner: auditor
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
corrected_by: []
relates: [WK-674, SL-1256, FR-343, FR-396, FR-397]
---

# FD-1482 — The static authorisation sweep checks no routes, and no test pins which permission a route requires

*Disclosure: drafted under working id 9988; minted as FD-1482 on 2026-10-08, in the T1 batch mint PR.*

## Amendment before mint (2026-10-05)

Amended 2026-10-05 before mint, re-measured at `47d770e8` (`origin/main`): **limbs 1 and 3 are fixed; limb 2 is the open claim.** **Limbs 1 and 3 — fixed by `dfddfad8` (#1104, SL-1256).** `_flattened_operations` descends `original_router` (`backend/tests/test_api_authorisation_sweep.py:108-128`), `test_every_operation_is_accounted_for_by_exactly_one_class` and `test_the_static_sweep_iterates_every_published_operation` (`:496`, `:538`) iterate every operation, and the behavioural no-roles sweep sends a valid body and accepts exactly 403 (`:388-392`), so a 422 is no longer counted as refused. **Limb 2 still holds.** `test_every_operation_declares_the_permission_it_enforces` (`:441`) asks only that a permission is declared (`_unguarded_operations`, `:140`), not which one; the new `tests/test_permission_parity.py` (SL-1360, #1049) compares `06` §4.1 with `model_schema.Permission` and the existence of a check site per permission name, not which route requires which; no §5.1 table has a `Permission` column (all seven `Method | Path | Purpose` tables, `01` to `07`) and `x-permission` appears in `docs/contracts/openapi/generated.json` 0 times. **Owner: the WK-1178 slice that carries RL-1483 (working id, unminted)**, which creates the declaration and pins each route against it, red first on the `AUDIT_READ` to `JOB_READ` swap. Event that discharges the open claim: that slice merges. **Mint after RL-1483**, so the event named exists. The cites in the sections below are to tree `9f63d0fe`; read them by symbol: `test_every_operation_declares_the_permission_it_enforces` (now `:441`), `_unguarded_operations` (now `:140`), `switch_workspace`'s membership check (`backend/src/app/api/me.py:248-251`, `WORKSPACE_SCOPE_DENIED`), `create_rule`'s permission checks (`backend/src/app/platform/validation_rules.py:204`, `:211`), and the audit routes' §5.1 table in `docs/specs/06-governance.md` (the `/api/v1/audit` rows are now `:578-579`). FR-343 is `docs/specs/06-governance.md:79`, unchanged.

## Finding

**Severity: medium, final.** The maintainer's entry of 2026-09-30 11:08:22 BST, "A1 = MEDIUM, conditional on the
behavioural switch_workspace confirmation", made it conditional (HIGH or CRITICAL if a non-member `POST /me/workspace`
were not refused with `WORKSPACE_SCOPE_DENIED`), and the entry of 2026-09-30 11:09:37 BST, "A1 MEDIUM confirmed
behaviourally; the condition is met" (`~/gi-pricing-plan.local/channel/to-lead.md`), closed the condition: the
non-member is refused switch, read and write, so the severity stays medium. The confirmation is auditor-close1255's, not
the author's (below). On
`origin/main` `9f63d0feee524815e7e0c68c99a53ac3f80e6c37`, **FR-343** (`docs/specs/06-governance.md:79`:
"Permissions are checked in the backend on every request against `(principal, permission, resource, scope)`")
has a test that appears to check it and does not.

1. `test_every_operation_declares_the_permission_it_enforces` (`backend/tests/test_api_authorisation_sweep.py:175`)
   iterates `api_client.app.routes` (`:189`) filtered to `APIRoute`. On fastapi 0.141.1 the app's top-level
   routes are `_IncludedRouter` x22, `Route` x4 and `APIRoute` x2 (`/version`, `/api/v1/auth/config`, both
   `OPEN_BY_DESIGN` and skipped). **Zero routes are checked.** The 137 real operations sit under
   `_IncludedRouter.original_router.routes`.
2. **No test pins which permission a route requires.** Swapping `Permission.AUDIT_READ` for `Permission.JOB_READ`
   in `backend/src/app/api/audit.py` leaves all five tests in the sweep file green (below). A caller with the
   wrong role gets in and nothing fails.
3. The behavioural no-roles sweep counts **422 as "refused"** for POST/PUT/PATCH
   (`:135`, `refused = {403, 422} if method in {"POST", "PUT", "PATCH"} else {403}`), sends `json={}` (`:128`), and so
   cannot reach a guard that sits behind body validation: `POST /me/workspace` passes it on an empty body
   without its membership check running.

**No real route lacks a guard** (accounting below): 123 carry a route-level `requires()`, 5 are open by design,
7 are permission-free on purpose, 2 are guarded in the service layer. This is why the severity is medium: a
blind test, no hole found behind it. **Proposed by the auditor; the verdict is the lead's.**

## Evidence

### The behavioural condition, confirmed (auditor-close1255, not reproduced by the author)

Source: auditor-close1255, relayed by the lead: a scratch test on a per-worktree database at `9f63d0fe`. A non-member P (an analyst in
workspace A only) against workspace B: `POST /api/v1/me/workspace` {B} gave **403 `WORKSPACE_SCOPE_DENIED`**, with and
without the `Workspace-Id` header; `GET /datasets` and `GET /rating-versions` with `Workspace-Id: B` gave **403**;
`POST /datasets` with the header B gave **403**; **B's audit chain was unchanged**. The existing
`backend/tests/test_workspace_switch.py:187` (`test_a_switch_to_a_non_membership_is_denied`) already asserts the
non-member refusal. Route accounting 123 + 5 + 7 + 2 = 137 (below). The only `/me/workspace` gap is in the sweep: it is
not in the sweep's allow-list, so the static test would need to be told it is guarded by membership.


### Reproduced by the auditor at `9f63d0fe`

In a detached worktree at the same tree (`uv sync --all-packages`, `alembic upgrade head` on a scratch database
made with `createdb -T`), a temporary pytest over the `api_client` fixture printed:

```text
types {'Route': 4, '_IncludedRouter': 22, 'APIRoute': 2}
openapi operations 137
flattened APIRoutes 137 route-methods 137
flattened routes with a requires() dependency 123
flattened routes without one: 14  (5 open, 7 permission-free, POST /me/workspace, POST /validation-rules)
```

### Broken-input runs (`backend/tests/test_api_authorisation_sweep.py`, 5 tests, each run on the scratch DB)

| Run | Change to `backend/src/app/api/audit.py` | Result |
|---|---|---|
| baseline | none | 5 passed |
| M1 | `ReadAudit` uses `require_caller` instead of `requires(Permission.AUDIT_READ)` | **1 failed, 4 passed**: only the behavioural no-roles test fails (`GET /api/v1/audit`, `/audit/export`, `/audit/verify` all 200). The static test stays green. |
| M2 | `Permission.AUDIT_READ` replaced by `Permission.JOB_READ` | **5 passed** (the behavioural no-roles test passes too, since a role-less caller holds neither). |

The file was restored after each run (`git status --short` empty).

### A flattened static check flags two routes it cannot see a guard on

Flattening the included routers gives 137 `APIRoute`s, 123 with a `requires()` dependency. The 14 without one:

- 5 in `OPEN_BY_DESIGN` (`/healthz`, `/readyz`, `/version`, `/metrics`, `/api/v1/auth/config`);
- 7 in `NO_PERMISSION_REQUIRED` (`/api/v1/me`, `/me/workspaces`, `/demo/guide`, `/approval-requests` GET and POST,
  `/approval-requests/{request_id}`, `/approval-policy`);
- 2 guarded elsewhere: `POST /api/v1/validation-rules` (the service layer, `platform/validation_rules.py:192` and
  `:199`, `rbac.require_permission` with `ADMIN_MANAGE_SETTINGS` or the analyst permission) and `POST /api/v1/me/workspace`
  (the membership check, `backend/src/app/api/me.py:249` (the check) and `:251` (the raise), `WORKSPACE_SCOPE_DENIED`; FR-396 and FR-397).

### Route accounting, 137 operations at `9f63d0fe`

Method, published path (openapi), and what guards it. Predicate: the flattened route list of the scratch app; a
route's permission is the `PERMISSION_ATTRIBUTE` of a dependency in `route.dependant.dependencies`.

| Method | Path | Guard |
|---|---|---|
| GET | `/api/v1/approval-policy` | authenticated, permission-free on purpose (`NO_PERMISSION_REQUIRED`) |
| PUT | `/api/v1/approval-policy` | `admin:manage_roles` (route-level `requires()`) |
| GET | `/api/v1/approval-requests` | authenticated, permission-free on purpose (`NO_PERMISSION_REQUIRED`) |
| POST | `/api/v1/approval-requests` | authenticated, permission-free on purpose (`NO_PERMISSION_REQUIRED`) |
| GET | `/api/v1/approval-requests/{request_id}` | authenticated, permission-free on purpose (`NO_PERMISSION_REQUIRED`) |
| POST | `/api/v1/approval-requests/{request_id}/decide` | `approval:decide` (route-level `requires()`) |
| POST | `/api/v1/approval-requests/{request_id}/withdraw` | `approval:decide` (route-level `requires()`) |
| GET | `/api/v1/audit` | `audit:read` (route-level `requires()`) |
| GET | `/api/v1/audit/export` | `audit:read` (route-level `requires()`) |
| GET | `/api/v1/audit/verify` | `audit:read` (route-level `requires()`) |
| GET | `/api/v1/auth/config` | open by design (`OPEN_BY_DESIGN`, sweep `:28`) |
| GET | `/api/v1/bandings` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/bandings` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/bandings/evaluate` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/bandings/propose` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/blobs/upload-url` | `dataset:write` (route-level `requires()`) |
| GET | `/api/v1/blobs/{sha256}` | `dataset:read` (route-level `requires()`) |
| GET | `/api/v1/custom-metrics` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/custom-metrics` | `model:fit` (route-level `requires()`) |
| GET | `/api/v1/custom-metrics/{metric_id}` | `model:read` (route-level `requires()`) |
| GET | `/api/v1/custom-metrics/{metric_id}/certificate` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/custom-metrics/{metric_id}/certify` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/custom-metrics/{metric_id}/submit` | `model:submit` (route-level `requires()`) |
| GET | `/api/v1/custom-metrics/{metric_id}/usage` | `model:read` (route-level `requires()`) |
| GET | `/api/v1/custom-objectives` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/custom-objectives` | `model:fit` (route-level `requires()`) |
| GET | `/api/v1/custom-objectives/{objective_id}` | `model:read` (route-level `requires()`) |
| GET | `/api/v1/custom-objectives/{objective_id}/certificate` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/custom-objectives/{objective_id}/certify` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/custom-objectives/{objective_id}/derive` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/custom-objectives/{objective_id}/submit` | `model:submit` (route-level `requires()`) |
| GET | `/api/v1/custom-objectives/{objective_id}/usage` | `model:read` (route-level `requires()`) |
| GET | `/api/v1/dataset-versions/{version_id}` | `dataset:read` (route-level `requires()`) |
| GET | `/api/v1/dataset-versions/{version_id}/compare` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/dataset-versions/{version_id}/derive` | `dataset:write` (route-level `requires()`) |
| GET | `/api/v1/dataset-versions/{version_id}/lineage` | `dataset:read` (route-level `requires()`) |
| GET | `/api/v1/dataset-versions/{version_id}/one-ways` | `dataset:read` (route-level `requires()`) |
| GET | `/api/v1/dataset-versions/{version_id}/profile` | `dataset:read` (route-level `requires()`) |
| GET | `/api/v1/dataset-versions/{version_id}/rejected` | `dataset:read` (route-level `requires()`) |
| GET | `/api/v1/dataset-versions/{version_id}/splits` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/dataset-versions/{version_id}/splits` | `dataset:write` (route-level `requires()`) |
| POST | `/api/v1/dataset-versions/{version_id}/transition` | `dataset:validate` (route-level `requires()`) |
| POST | `/api/v1/dataset-versions/{version_id}/validate` | `dataset:validate` (route-level `requires()`) |
| GET | `/api/v1/dataset-versions/{version_id}/validation-reports` | `dataset:read` (route-level `requires()`) |
| GET | `/api/v1/datasets` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/datasets` | `dataset:write` (route-level `requires()`) |
| PATCH | `/api/v1/datasets/{dataset_id}` | `dataset:read` (route-level `requires()`) |
| GET | `/api/v1/datasets/{slug}` | `dataset:read` (route-level `requires()`) |
| PUT | `/api/v1/datasets/{slug}/dictionary` | `dataset:write` (route-level `requires()`) |
| GET | `/api/v1/datasets/{slug}/rule-set` | `dataset:read` (route-level `requires()`) |
| PUT | `/api/v1/datasets/{slug}/rule-set` | `dataset:write` (route-level `requires()`) |
| GET | `/api/v1/datasets/{slug}/versions` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/datasets/{slug}/versions` | `dataset:write` (route-level `requires()`) |
| GET | `/api/v1/datasets/{slug}/versions/{version}` | `dataset:read` (route-level `requires()`) |
| PATCH | `/api/v1/datasets/{slug}/versions/{version}/schema` | `dataset:write` (route-level `requires()`) |
| GET | `/api/v1/demo/guide` | authenticated, permission-free on purpose (`NO_PERMISSION_REQUIRED`) |
| GET | `/api/v1/factors` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/factors` | `model:fit` (route-level `requires()`) |
| GET | `/api/v1/groupings` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/groupings` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/groupings/evaluate` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/groupings/propose` | `model:fit` (route-level `requires()`) |
| GET | `/api/v1/jobs` | `job:read` (route-level `requires()`) |
| GET | `/api/v1/jobs/{job_id}` | `job:read` (route-level `requires()`) |
| POST | `/api/v1/jobs/{job_id}/cancel` | `job:cancel` (route-level `requires()`) |
| GET | `/api/v1/jobs/{job_id}/events` | `job:read` (route-level `requires()`) |
| GET | `/api/v1/jobs/{job_id}/logs` | `job:read` (route-level `requires()`) |
| GET | `/api/v1/me` | authenticated, permission-free on purpose (`NO_PERMISSION_REQUIRED`) |
| POST | `/api/v1/me/workspace` | **guarded elsewhere**: membership check, `api/me.py:249` and `:251` (`WORKSPACE_SCOPE_DENIED`) |
| GET | `/api/v1/me/workspaces` | authenticated, permission-free on purpose (`NO_PERMISSION_REQUIRED`) |
| POST | `/api/v1/model-specs/validate` | `model:fit` (route-level `requires()`) |
| GET | `/api/v1/models` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/models` | `model:fit` (route-level `requires()`) |
| GET | `/api/v1/models/backtests/{backtest_id}` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/models/compare` | `model:fit` (route-level `requires()`) |
| GET | `/api/v1/models/comparisons/{comparison_id}` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/models/{model_id}/archive` | `model:submit` (route-level `requires()`) |
| POST | `/api/v1/models/{model_id}/backtest` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/models/{model_id}/predict` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/models/{model_id}/submit` | `model:submit` (route-level `requires()`) |
| GET | `/api/v1/models/{model_id}/transparency` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/models/{model_id}/transparency` | `model:fit` (route-level `requires()`) |
| GET | `/api/v1/models/{slug}` | `model:read` (route-level `requires()`) |
| GET | `/api/v1/models/{slug}/diagnostics` | `model:read` (route-level `requires()`) |
| GET | `/api/v1/peril-structures` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/peril-structures` | `model:fit` (route-level `requires()`) |
| GET | `/api/v1/peril-structures/{structure_id}` | `model:read` (route-level `requires()`) |
| POST | `/api/v1/peril-structures/{structure_id}/reconcile` | `model:fit` (route-level `requires()`) |
| POST | `/api/v1/peril-structures/{structure_id}/submit` | `model:submit` (route-level `requires()`) |
| POST | `/api/v1/rate-tables/{slug}/seed-from-model` | `rating:write` (route-level `requires()`) |
| POST | `/api/v1/rate-tables/{slug}@{version}/bulk-operation` | `rating:write` (route-level `requires()`) |
| GET | `/api/v1/rate-tables/{slug}@{version}/diff` | `rating:read` (route-level `requires()`) |
| GET | `/api/v1/rate-tables/{slug}@{version}/export/csv` | `rating:read` (route-level `requires()`) |
| GET | `/api/v1/rate-tables/{slug}@{version}/export/xlsx` | `rating:read` (route-level `requires()`) |
| POST | `/api/v1/rate-tables/{slug}@{version}/import` | `rating:write` (route-level `requires()`) |
| POST | `/api/v1/rating-algorithms` | `rating:write` (route-level `requires()`) |
| GET | `/api/v1/rating-algorithms/{slug}@{version}/diff` | `rating:read` (route-level `requires()`) |
| GET | `/api/v1/rating-versions` | `rating:read` (route-level `requires()`) |
| POST | `/api/v1/rating-versions` | `rating:write` (route-level `requires()`) |
| GET | `/api/v1/rating-versions/{rating_version_id}` | `rating:read` (route-level `requires()`) |
| POST | `/api/v1/rating-versions/{rating_version_id}/compile` | `rating:compile` (route-level `requires()`) |
| POST | `/api/v1/rating-versions/{rating_version_id}/regression-runs` | `rating:compile` (route-level `requires()`) |
| GET | `/api/v1/rating-versions/{rating_version_id}/regression-runs/{run_id}` | `rating:read` (route-level `requires()`) |
| GET | `/api/v1/rating-versions/{rating_version_id}/regression-runs/{run_id}/cases` | `rating:read` (route-level `requires()`) |
| POST | `/api/v1/rating-versions/{rating_version_id}/submit` | `rating:submit` (route-level `requires()`) |
| GET | `/api/v1/reference-tables` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/reference-tables` | `admin:manage_settings` (route-level `requires()`) |
| GET | `/api/v1/reference-tables/{slug}/lookup` | `dataset:read` (route-level `requires()`) |
| GET | `/api/v1/reference-tables/{slug}/versions` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/reference-tables/{slug}/versions` | `admin:manage_settings` (route-level `requires()`) |
| POST | `/api/v1/reference-tables/{slug}/versions/{version}/publish` | `admin:manage_settings` (route-level `requires()`) |
| GET | `/api/v1/reference-tables/{slug}/versions/{version}/rows` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/regression-suites/{slug}/versions` | `rating:write` (route-level `requires()`) |
| GET | `/api/v1/regression-suites/{slug}@{version}` | `rating:read` (route-level `requires()`) |
| POST | `/api/v1/score` | `score:execute` (route-level `requires()`) |
| POST | `/api/v1/score/batch` | `score:batch` (route-level `requires()`) |
| POST | `/api/v1/score/compare` | `rating:read` (route-level `requires()`) |
| POST | `/api/v1/service-accounts` | `admin:manage_service_accounts` (route-level `requires()`) |
| DELETE | `/api/v1/service-accounts/{account_id}/keys/{prefix}` | `admin:manage_service_accounts` (route-level `requires()`) |
| POST | `/api/v1/service-accounts/{account_id}/rotate` | `admin:manage_service_accounts` (route-level `requires()`) |
| GET | `/api/v1/settings` | `settings:read` (route-level `requires()`) |
| PUT | `/api/v1/settings` | `admin:manage_settings` (route-level `requires()`) |
| GET | `/api/v1/sources` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/sources` | `dataset:write` (route-level `requires()`) |
| POST | `/api/v1/sources/{source_id}/preview` | `dataset:write` (route-level `requires()`) |
| GET | `/api/v1/traces` | `rating:read` (route-level `requires()`) |
| GET | `/api/v1/validation-reports/{report_id}` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge` | `dataset:acknowledge_warning` (route-level `requires()`) |
| GET | `/api/v1/validation-rules` | `dataset:read` (route-level `requires()`) |
| POST | `/api/v1/validation-rules` | **guarded elsewhere**: service layer, `platform/validation_rules.py:192` and `:199` |
| POST | `/api/v1/validation-rules/{rule_id}/approve` | `approval:decide` (route-level `requires()`) |
| POST | `/api/v1/validation-rules/{rule_id}/dry-run` | `dataset:write` (route-level `requires()`) |
| POST | `/api/v1/validation-rules/{rule_id}/submit` | `dataset:write` (route-level `requires()`) |
| GET | `/healthz` | open by design (`OPEN_BY_DESIGN`, sweep `:28`) |
| GET | `/metrics` | open by design (`OPEN_BY_DESIGN`, sweep `:28`) |
| GET | `/readyz` | open by design (`OPEN_BY_DESIGN`, sweep `:28`) |
| GET | `/version` | open by design (`OPEN_BY_DESIGN`, sweep `:28`) |

### Other sweeps

`git grep -n "\.routes" -- backend/tests backend/src` at `9f63d0fe` finds one use, at
`backend/tests/test_api_authorisation_sweep.py:189`; the other two sweeps in that file enumerate from
`app.openapi()` and are not affected by the router nesting. So there is no sibling that iterates `app.routes`
the same way today, and the fix task still names them so a future one is covered.

### What the spec declares, and does not

No spec declares route permissions. Every §5.1 route table in `01` to `07` has the header
`| Method | Path | Purpose |` (`06-governance.md:534-536`, the audit routes, is one), and `docs/contracts/openapi/generated.json`
has no `x-permission` (also `grep -rn "x-permission\|x-required-permission" backend/src docs/contracts`, 0 hits).
*(Corrected 2026-09-30 by the auditor: the first draft of this section, and the maintainer's earlier A1 entries,
named "the §5.1 permission column, or the contract" as the source to pin against. The maintainer's entry of
2026-09-30 11:17:35 BST, "DATED CORRECTION to my A1 entries", supersedes that parenthetical: the mechanism does not
exist.)* The principle stands, pin against a declaration and never a test-local map (CLAUDE.md §2), but the
declaration is not there yet. **DP-S2-4** decides it, with dm-effort-high: (a) a §5.1 Permission column, or (b) a
routes cell on `06` §4.1's Built rows; the entry rejects (c) as circular.

## Disposition

**Proposed disposition: carry forward with an owner.** Owner: **WK-674 Slice 2** (`SL-1256`), as its **first
task, before any new route**, per the maintainer's entries of 2026-09-30 11:01:50 BST ("DECISION: candidate A1
(vacuous authorisation sweep): evidence, severity rule, owner WK-674 S2"), 11:06:50 BST ("A1 reproduced: decisions
pending switch_workspace; the fix's shape") and 11:08:22 BST ("A1 = MEDIUM, conditional on the behavioural
switch_workspace confirmation"). Slice 2 adds deploy and environment routes whose guards this sweep would
"verify". The task is test-only (`backend/tests`), so the maintainer's entry finds no `RL-1263` overlap with
WK-690 Slice 1. Its acceptance, as decided:

- flatten the included routers in the static sweep;
- assert the iterated count equals the openapi operation count, so it cannot shrink silently again;
- ~~pin each route's specific permission against the spec's declared permission (the `06`/`03` §5.1 permission
  column, or the contract), never a hand-written map in the test; red first on the `AUDIT_READ` to `JOB_READ` swap
  (M2 above);~~ *(Struck 2026-09-30 on the maintainer's entry of 11:17:35 BST: that column or contract field does not
  exist. This comparison step **moves out of Slice 2** into the slice DP-S2-4's ruling names, which pins each route's
  permission against the declaration the ruling creates, never a hand-written map, red first on the `AUDIT_READ` to
  `JOB_READ` swap (M2 above). Slice 2's new deploy routes are declared by whichever of the two lands second.)*
- account for all 137 routes; triage `POST /validation-rules` and `POST /me/workspace` and record each
  service-layer guard in a **named allow-list with file:line**, so the static sweep knows them rather than
  skipping silently;
- make the no-roles behavioural sweep send a **valid body per route** and assert **401 or 403 specifically**, never
  any refusal status (a 422 is not a refusal), red first on `/me/workspace`, which passes today on a 422;
- remove `requires()` from one real guarded route and show the test red (M1 is the shape);
- fix the sibling tests that iterate `app.routes` the same way in the same task.

Slice 2 keeps everything above except the struck comparison step.

The maintainer's entry of 11:08:22 BST also rules that **no permission is needed on `/me/workspace`**: membership
(FR-396, FR-397) is the right control for choosing among one's own workspaces, and no spec change follows from it.

**Event that next confirms or discharges it:** (a) WK-674 Slice 2's first task merges with the acceptance above
(flattening, count equality, the 137-route accounting, the named allow-list, valid body with 401 or 403, the M1 shape
and the sibling tests); and (b) the slice DP-S2-4's ruling names merges the permission-pinning comparison (M2 red first).
The behavioural condition is already met; see the evidence section.

Ownership shape: event

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it. The maintainer's
three entries above have already set the severity rule, the owner and the acceptance.

*Disclosure: drafted under working id 9988; minted at the merge, when the id is re-read against `origin/main`.*

Re-anchored 2026-10-05 at main `caa4e411`: the open claim, limb 2, still holds, and limbs 1
and 3 stay fixed. `backend/tests/test_api_authorisation_sweep.py` is unchanged since `dfddfad8`:
`_flattened_operations` (`:108`, descends `original_router`), `_declares_a_permission` and
`_unguarded_operations` (`:131`, `:140`) test only that *a* permission is declared, and
`test_every_operation_declares_the_permission_it_enforces` (`:441`) asserts only that no
operation is unguarded, so swapping `Permission.AUDIT_READ` for `Permission.JOB_READ` is still
not pinned. `tests/test_permission_parity.py` (`#1049`, `d8537220`) compares `06` §4.1 with
`model_schema.Permission` and not which route requires which; no §5.1 table has a `Permission`
column (the seven `| Method | Path | Purpose |` headers, `01` to `07`), and `x-permission` appears
0 times in `docs/contracts/openapi/generated.json`. Moved since `47d770e8`: the `/api/v1/audit`
rows of `06` §5.1 are now `docs/specs/06-governance.md:589-592` (four rows, the query, verify,
anchor and export routes; read `:578-579` as the first two). Unchanged: FR-343 at
`docs/specs/06-governance.md:79`; `switch_workspace`'s `WORKSPACE_SCOPE_DENIED` membership check
(`backend/src/app/api/me.py:248-251`); `create_rule`'s permission checks
(`backend/src/app/platform/validation_rules.py:204`, `:211`). `RL-1483` is minted in the same batch (T1) as this record; `PL-1408` (line 510) cites this finding by its working id 9988
(a filed plan, frozen, not edited here).
