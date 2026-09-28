---
id: FD-9008
family: finding
title: The permission names in 06 differ from the code's
status: active
created: 2026-09-28
owner: auditor
tree: 37b2596e4318092178c9b0c9fedb83610ee9fd28
corrected_by: []
relates: []
---

# FD-9008 — The permission names in 06 differ from the code's

The auditor filed this finding on 2026-09-28 in the register-and-records pass. It was routed
from dm-e's WK-674 ruling, PR #848, not merged at this writing, which amends only the deploy permission
(its DP-6) and leaves the rest *"for an auditor to file as a finding"*.

## Finding

The permission vocabulary in `docs/specs/06-governance.md` and the one the code ships in
`packages/model-schema/src/model_schema/permissions.py` differ. At `37b2596e` only 7 names
agree. **This record does not say which side is right**: no ruling covers the names beyond
DP-6's deploy permission, so both sides are recorded (`CLAUDE.md` §0).

## Evidence

The corpus and predicates, at `37b2596e`:

- **The 06 side.** `grep -oE "\b[a-z][a-z_]*:([a-z_]+\b|deploy_\*)"
  docs/specs/06-governance.md | grep -vE ":motor$|^type:name$" | sort -u` gives 24 names. The
  filter drops resource references of the form `rating_version:motor` (`06:353`, `:360`,
  `:364`, `:421`) and the `type:name` notation (`06:432`), which are not permissions. The names
  come from the glossary example (`06:62`), the built-in-role example (`06:196–201`), FR-366 and
  FR-367, and `06:219`.
- **The code side.** `grep -oE '= "[a-z_]+:[a-z_]+"'
  packages/model-schema/src/model_schema/permissions.py | tr -d '=" ' | sort -u` gives 24 names.
- **The comparison** is `comm` of the two sorted lists.

**In both (7):** `admin:manage_roles`, `approval:decide`, `dataset:acknowledge_warning`,
`dataset:read`, `model:fit`, `model:read`, `model:submit`.

**In `06` only (17):** `alert:acknowledge`, `alert:resolve`, `banding:write`,
`custom_objective:author`, `custom_objective:submit`, `dataset:create_version`, `factor:write`,
`grouping:write`, `model:approve`, `monitor:write`, `optimisation:materialise`,
`optimisation:run`, `rate_table:write`, `rating_algorithm:write`, `rating_version:deploy_*`,
`rating_version:deploy_prod`, `rating_version:submit`.

**In the code only (17):** `admin:break_glass`, `admin:manage_environments`,
`admin:manage_service_accounts`, `admin:manage_settings`, `audit:read`, `dataset:validate`,
`dataset:write`, `deployment:promote`, `job:cancel`, `job:read`, `rating:compile`, `rating:read`,
`rating:submit`, `rating:write`, `score:batch`, `score:execute`, `settings:read`.

**Pairs that name the same capability differently**, as dm-e observed them:

- `model:approve` (`06:62`) against `approval:decide` (code), though `06` also uses
  `approval:decide`;
- `rating_version:submit` (`06:199`) against `rating:submit`;
- `rating_version:deploy_prod` / `deploy_*` against `deployment:promote`, which #848's DP-6
  amends into `06`.

Some `06`-only names belong to later-phase modules, such as `optimisation:*`, `monitor:write`
and `alert:*`. `custom_objective:author` is FR-367's permission, which *"no built-in role"*
grants. So a name missing from the code is not by itself a defect. Which pairs are defects is
the owner's analysis.

## Disposition

**Deferred with an owner — the lead.** Event: the next slice that touches permissions, or
WK-1178 if none is scheduled. #848's DP-6 amendment of the deploy permission is outside this
finding.
