---
id: FD-1852
family: finding
title: Three route-level scope-less requires() guards refuse a resource-scoped grant before the handler's scoped check (latent)
status: active
created: 2026-10-22
owner: auditor
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
corrected_by: []
relates: [WK-1178, WK-676, RL-1301]
---

# FD-1852 — Three route-level scope-less requires() guards refuse a resource-scoped grant before the handler's scoped check (latent)

## Finding

**MEDIUM (latent): correctly specified, unreachable by a P2 user, because no P2 path creates a non-workspace grant.**
Rated HIGH on "2026-10-22 17:27:15 BST" after the probe confirmed it, re-rated by the maintainer (by delegation)
on "2026-10-22 17:46:43 BST" (`to-lead.md`, ruling (ii)), which supersedes the HIGH. Owner WK-1178 (DP-0 of PL 8181;
WK-676 inherits the `06` FR-345 clause). Filed under working id 8177.

A route-level `requires(Perm.X)` is a scope-less check: `rbac.py` :209-212 returns False for a scoped assignment when
the question names no resource. A principal whose grant is scoped to one Dataset is therefore refused (403) before the
handler reaches its own correct, Dataset-scoped check. This is `RL-1301` B.2 item 2's failure, against `FR-345`.

## Evidence

At `origin/main` 71e481fa. The route-level guards are the aliases `WriteDatasets` (`backend/src/app/api/datasets.py:88`,
`backend/src/app/api/validation.py:68`) and `AcknowledgeWarnings` (`validation.py:69-71`); each pairs with a handler
that does the scoped check:

| Route | Route-level guard | Handler's scoped check |
|---|---|---|
| `PUT /datasets/{slug}/dictionary` (`datasets.py:494`, handler :500) | `WriteDatasets` :88 | `platform/datasets.py:282-288`, `DATASET_WRITE`, `ScopeType.DATASET` |
| `PUT /datasets/{slug}/rule-set` (`validation.py:435`) | `WriteDatasets` :68 | `platform/validation_rules.py:825-829`, `DATASET_WRITE`, `ScopeType.DATASET` |
| `POST …/acknowledge` (`validation.py:164`) | `AcknowledgeWarnings` :69-71 | `platform/validation.py:257-264`, `DATASET_ACKNOWLEDGE_WARNING`, `ScopeType.DATASET` |

**Proof of the defect:** probe branch `probe/fd-8177-dataset-scoped-write` @f4c0832f (origin/main + one test file);
`~/gi-pricing-plan.local/scratch/fd-8177/result.md`: `1 failed, 1 passed`; the failing test
`test_a_grant_scoped_to_one_dataset_may_replace_that_datasets_dictionary` asserts `403 == 200`, `PERMISSION_DENIED`,
for an `analyst` assignment with `scope_type=dataset` only. Scoped rows were created directly in the test database.

**Latent: no P2 grant path.** The maintainer's (by delegation) re-check, at `71e481fa`:
`git grep -n grant_role` over `backend/src`: only `rbac.py:49` (`__all__`), `:307` (the def) and `:398` (a docstring);
no production caller (the other hits are tests). The seed writes WORKSPACE scope only
(`examples/fremtpl2/seed.py:404`, `scope_type=ScopeType.WORKSPACE.value`). `06-governance.md:578` defers
`POST /api/v1/role-assignments` to WK-676 (P3), "none is built in Phase 2".

Not measured here: the sweep of every other route-level `requires(` whose handler does a scoped check was ordered on
"2026-10-22 17:21:38 BST"; the three rows above are the maintainer's (by delegation) set, with the `WriteDatasets`
alias also used by routes at `datasets.py:178,213,281,524,760` and `validation.py:319,355`, not individually
examined here.

## Remedy (not made here)

SL 8185 with LG 8186 under PL 8181 (`sl-8185-wk1178-fd8177-scoped-writes`; rule-set task only after SL-1736 merges):
the handler's scoped check made reachable, red-first per route, an AST-based permanent guard that names exactly
these three routes at base, and the `06` FR-345 dated clause: "declared, not yet enforced; enforcement ships with role
assignments (WK-676)" and that no P2 API creates a scoped grant. `MODEL_FAMILY` / `RATING_ALGORITHM` scoping is a P3
item for WK-676.

## Disposition

Open, owner WK-1178; **fix before close**: SL 8185 (LG 8186). Filed under working id 8177.
