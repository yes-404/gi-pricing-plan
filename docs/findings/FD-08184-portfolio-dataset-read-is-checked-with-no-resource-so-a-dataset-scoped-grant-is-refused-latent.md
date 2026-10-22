---
id: FD-8184
family: finding
title: Portfolio dataset:read is checked with no resource, so a Dataset-scoped grant is refused (latent)
status: active
created: 2026-10-22
owner: auditor
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
corrected_by: []
relates: [WK-1178, WK-676, WK-673, FD-8177, RL-8182]
---

# FD-8184 — Portfolio dataset:read is checked with no resource, so a Dataset-scoped grant is refused (latent)

## Finding

**MEDIUM (latent): the FD-8177 class, correctly specified and unreachable by a P2 user, because no P2 path creates a
non-workspace grant.** Opened as a candidate on "2026-10-22 17:21:38 BST", rated HIGH on "2026-10-22 17:41:48 BST",
re-rated by the maintainer (by delegation) on "2026-10-22 17:46:43 BST" (`to-lead.md`), which supersedes the HIGH.
Owner WK-1178. Filed under working id 8184.

`03-rating-engine.md` :1080 (`POST /api/v1/dislocation-runs`) and :1083 (`GET …/dislocation-runs/{id}/movers`) require
`dataset:read` **on the portfolio Dataset Version**. The code checks `dataset:read` with no resource, which
`rbac.py` :209-212 refuses for any scoped assignment, so a Dataset-scoped `dataset:read` grant is refused 403.

## Evidence

At `origin/main` 71e481fa:

- `backend/src/app/api/rate_tables.py` :430-437 and :528-535 (the `portfolio is not None` branches of the diff
  routes, `rate_table_diff` :398 and `rate_table_diff_cells` :497): `rbac.require_permission(...,
  permission=Permission.DATASET_READ, credential_permissions=caller.permissions)`, no `resource=`.
- `backend/src/app/api/dislocation_runs.py` :50-59, `_require_dataset_read`, same call with no resource; its docstring
  says the portfolio "is named in the body or on the stored run, so the route-wide dependency cannot carry it
  (FR-345)"; called at :79, :105 and :167.

**Proof of the defect:** probe branch `probe/fd-8184-portfolio-dataset-read` @ee4e8596 (origin/main + one test file);
`~/gi-pricing-plan.local/scratch/fd-8184/result.md`: `1 failed, 1 passed`; `GET /api/v1/rate-tables/{slug}@2/diff?
against=previous&portfolio=<validated Dataset Version>` returns 403 `PERMISSION_DENIED` from the no-resource
`dataset:read` check (`rbac.py:292` region) for a caller with workspace-wide `rating:read` and `dataset:read` scoped
to the portfolio's Dataset only.

**Latent: no P2 grant path.** `git grep -n grant_role` at `71e481fa` over `backend/src` gives only `rbac.py:49`
(`__all__`), `:307` (the def) and `:398` (a docstring); no production caller. The seed writes WORKSPACE scope only
(`examples/fremtpl2/seed.py:404`). `06-governance.md:578` defers `POST /api/v1/role-assignments` to WK-676 (P3).

## Remedy (not made here)

It joins RL 8182's slice (`draft/rl-8182` @5e29e35a), not a new one: the dataset id resolved from the spec or the
stored run first, then the scoped check, each route red-first, the control asserting the scoped refusal rather than a
wrong-reason pass; the SL 8185 permanent guard's predicate extended to the shape "a permission check with no resource
where the spec names a scoped resource", or the reason it cannot be.

## Disposition

Open, owner WK-1178; **fix before close**, in RL 8182's slice. That slice is queued behind P2 row work and open P2
HIGHs and lands before P2 close if capacity allows; otherwise it is **carried to WK-676 with the condition "before
`POST /role-assignments` ships"**, never skipped silently. Filed under working id 8184.
