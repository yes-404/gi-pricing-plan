---
id: RL-9204
family: ruling
title: The permission catalogue — a verdict for each of the 34 names that 06 and the code do not share
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-28
owner: decision-maker
tree: 37b2596e4318092178c9b0c9fedb83610ee9fd28
phase: P2
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [WK-674, WK-684, WK-686, WK-687, WK-688, WK-690, WK-676]
---

# RL-9204 — The permission catalogue: a verdict for each of the 34 names that 06 and the code do not share

## Verified first, at 37b2596e4318092178c9b0c9fedb83610ee9fd28

**The question.** The permission-catalogue finding (PR #855, not yet on `main`, so it is named
by PR) records a `CLAUDE.md` §0 disagreement at scale. `06-governance.md` names 24 permissions
and the code's `Permission` enum defines 24, and only 7 are shared. The deputy's entry of
2026-09-28 (14:52:49 BST, item 4) routes it here. It asks for one verdict per unshared name:
- **map**: the same capability under two names. Pick one; the other is an alias for one
  release.
- **spec-only**: specified, not built. It is carried to the Work that builds it.
- **code-only**: built, not specified. It is added to `06`, or removed if dead, proven by a
  caller grep.

A verdict that changes scope goes to the deputy as a maintainer decision point. This record
rules the rest and lists those.

This record was drafted in the decision-maker's worktree, on branch `p2-perm-catalogue-rl`, cut
from `origin/main` = `37b2596e` with a clean root. Clock at drafting: 2026-09-28 14:57:19 BST,
read by `TZ=Europe/London date`. **RL-9204 is a working id**, minted at its turn.

### The two lists, and their predicates

The predicates are run at `37b2596e`, from the repository root.
- **`06` side**, over the **whole of `06`**:
  `grep -oE "\b[a-z][a-z_]*:([a-z_]+\b|deploy_\*)" docs/specs/06-governance.md | grep -vE ":motor$|^type:name$" | sort -u`
  gives 24 names. It is the finding's own predicate. An independent extraction of backticked
  or quoted `name:name` tokens gives the identical set.
  - **The corpus is all of `06`, not §4.** Section 4 alone (lines 186–435) holds only 20 of
    the 24. The other four are `model:approve` and `rating_version:deploy_prod` (the §2
    glossary, `:62`), `admin:manage_roles` (FR-348 at `:84`, FR-360 at `:101`) and
    `approval:decide` (§5.1, `:466`).
- **Code side**:
  `grep -oE '= "[a-z_]+:[a-z_]+"' packages/model-schema/src/model_schema/permissions.py | tr -d '=" ' | sort -u`
  gives 24 names. No permission string outside that enum appears in `backend/src`,
  `packages/*/src` or `frontend/src`.
- **The counts:** 24 in `06`, 24 in code, 7 shared, 41 in the union, and **34 unshared**
  (17 each side). They agree with the finding.

**The caller predicate, for every verdict on a code name:**
`git grep -n -E "(Perm|Permission)\.<NAME>\b" 37b2596e -- backend/src | grep -v '#'`
The regex includes `Perm`, because twelve modules import the enum as `Perm`
(`git grep -l -E 'Permission as Perm' 37b2596e -- backend/src` lists 12; e.g.
`backend/src/app/api/jobs.py:53`).
**A first draft of this record's proposal matched `Permission\.` only.** It reported six
names as unchecked, and four of those are checked through the alias. The regex above is the
corrected one, and the row counts below come from it.

### The 7 shared names

| Name | `06` | A route that checks it (at `37b2596e`) |
|---|---|---|
| `admin:manage_roles` | FR-348 (`:84`) | `backend/src/app/api/approvals.py:64` |
| `approval:decide` | §5.1 (`:466`) | `backend/src/app/api/approvals.py:63` |
| `dataset:acknowledge_warning` | §2 (`:62`), §4.1 (`:196`) | `backend/src/app/api/validation.py:61` |
| `dataset:read` | §4.1 (`:196`) | `backend/src/app/api/datasets.py:86` |
| `model:fit` | FR-367 (`:148`), §4.1 (`:198`) | `backend/src/app/api/models.py:108` |
| `model:read` | §4.1 note (`:223`) | `backend/src/app/api/models.py:107` |
| `model:submit` | FR-367 (`:148`), §4.1 (`:198`) | `backend/src/app/api/models.py:109` |

## Ruled

### The 34 unshared names, one row each

The **side** column is where the name appears: `06` only, or code only. The **evidence**
column holds the `06` line, the caller-predicate count and first route hit, or both.

| # | Name | Side | Verdict | Evidence |
|---|---|---|---|---|
| 1 | `rating_version:submit` | 06 | **map → `rating:submit`** | `06:199` (§4.1 Pricing Actuary). Its partner is row 21 |
| 2 | `custom_objective:submit` | 06 | **map → `model:submit`**, already ruled | `06:222-247`: the 2026-08-18 note says it "does **not** return", and submitting stays `model:submit` (FR-367, `:148`) |
| 3 | `rating_version:deploy_prod` | 06 | **map → `deployment:promote`**, ruled in the WK-674 ruling (PR #848, DP-6) and cited, not re-ruled | `06:62` |
| 4 | `rating_version:deploy_*` | 06 | **map → `deployment:promote`**, as row 3 | `06:219` |
| 5 | `custom_objective:author` | 06 | **spec-only → WK-690** (FR-367; its Slice 3 or 5 builds the check) | `06:148`, `:239-242` |
| 6 | `monitor:write` | 06 | **spec-only → WK-687** | `06:201` |
| 7 | `alert:acknowledge` | 06 | **spec-only → WK-688** | `06:201` |
| 8 | `alert:resolve` | 06 | **spec-only → WK-688** | `06:201` |
| 9 | `optimisation:run` | 06 | **spec-only → WK-684** | `06:200` |
| 10 | `optimisation:materialise` | 06 | **spec-only → WK-686** | `06:200` |
| 11 | `rating_algorithm:write` | 06 | **pending DP-A** | `06:199`. The code checks `rating:write` at `backend/src/app/api/rating_algorithms.py:24` |
| 12 | `rate_table:write` | 06 | **pending DP-A** | `06:199`. The code checks `rating:write` at `backend/src/app/api/rate_tables.py:45` |
| 13 | `factor:write` | 06 | **pending DP-A** | `06:197`. `create_factor` checks `model:fit` (`FitModels`, `backend/src/app/api/models.py:108`, route at `:280-286`) |
| 14 | `banding:write` | 06 | **pending DP-A** | `06:197`. `create_banding` checks `model:fit` (`models.py:384-390`) |
| 15 | `grouping:write` | 06 | **pending DP-A** | `06:197`. `create_grouping` checks `model:fit` (`models.py:474-480`) |
| 16 | `dataset:create_version` | 06 | **pending DP-A** | `06:196`. The code checks `dataset:write`, which guards more than version creation: see row 23 |
| 17 | `model:approve` | 06 | **pending DP-C** | `06:62`, and `:218` ("every `*:approve` permission"). The code has one `approval:decide` for every type |
| 18 | `dataset:validate` | code | **add to 06** | 1 hit: `backend/src/app/api/dataset_versions.py:62` |
| 19 | `rating:read` | code | **add to 06** | 6 hits, the first at `backend/src/app/api/models.py:1112`. Also `rate_tables.py:46` and `rating_algorithms.py:25` |
| 20 | `rating:compile` | code | **add to 06** | 1 hit: `backend/src/app/api/models.py:1222` (`compile_rating_version`) |
| 21 | `rating:submit` | code | **map survivor** (row 1) | 2 hits: `backend/src/app/api/models.py:1195` (`submit_rating_version`) and `backend/src/app/platform/rating_versions.py:227`. Both are Rating Version submission |
| 22 | `rating:write` | code | **pending DP-A** | 4 hits: `models.py:1162` (`create_rating_version`), `rate_tables.py:45`, `rating_algorithms.py:24`, `platform/rating_versions.py:180` |
| 23 | `dataset:write` | code | **pending DP-A** | 11 hits across datasets (`api/datasets.py:87`), versions (`api/dataset_versions.py:61`), blobs (`api/blobs.py:40`), validation rules (`api/validation.py:59`, `platform/validation_rules.py:203`) and ingestion (`data/ingestion.py:124`) |
| 24 | `deployment:promote` | code | **map survivor** (rows 3–4) | **0 hits**. The deploy route is not built. WK-674 Slice 2 builds the check (the WK-674 ruling, PR #848) |
| 25 | `audit:read` | code | **add to 06** | 1 hit: `backend/src/app/api/audit.py:52` |
| 26 | `score:execute` | code | **add to 06** | 1 hit: `backend/src/app/api/score.py:110` |
| 27 | `score:batch` | code | **add to 06** | 2 hits: `backend/src/app/api/score.py:111`, and a docstring at `:38` |
| 28 | `job:read` | code | **add to 06** | 2 hits: `backend/src/app/api/jobs.py:62`, and a docstring at `authz.py:3` |
| 29 | `job:cancel` | code | **add to 06** | 1 hit: `backend/src/app/api/jobs.py:63` |
| 30 | `settings:read` | code | **add to 06** | 1 hit: `backend/src/app/api/settings.py:33` |
| 31 | `admin:manage_settings` | code | **add to 06** | 7 hits, the first at `backend/src/app/api/reference_tables.py:51`. Also `platform/reference.py:75` and `platform/datasets.py:995` |
| 32 | `admin:manage_service_accounts` | code | **add to 06** | 1 hit: `backend/src/app/api/service_accounts.py:40` |
| 33 | `admin:break_glass` | code | **add to 06** | 1 hit: `backend/src/app/platform/rbac.py:424` (FR-349's elevation) |
| 34 | `admin:manage_environments` | code | **pending DP-B** | **0 hits.** Its only occurrences are its definition and the admin role set (`permissions.py:69`, `:146`) |

**Verdict counts:**

| Verdict | Rows | Count |
|---|---|---|
| map | 1, 2, 3, 4, 21, 24 | 6 |
| spec-only, carried | 5–10 | 6 |
| add to 06 | 18, 19, 20, 25–33 | 12 |
| pending DP-A | 11–16, 22, 23 | 8 |
| pending DP-B | 34 | 1 |
| pending DP-C | 17 | 1 |
| **Total** | | **34** |

### Why each map is the same capability, and where the alias lives

- **`rating_version:submit` → `rating:submit`.**
  - The spec name is the Pricing Actuary's right to submit a Rating Version (`06:199`). The
    code name is checked at exactly two places, and both submit a Rating Version for approval
    (`models.py:1195`, `rating_versions.py:227`). Nothing else checks it.
  - One act, one capability, no broader reach. **The code name survives**, because it is
    built and tested and it follows the code's `rating:*` family.
  - The alias lives in the spec text, in the `06` §4.1 note this commit adds, for one
    release. No code ever carried `rating_version:submit`, so there is no code alias to keep.
- **`custom_objective:submit` → `model:submit`.** `06`'s own 2026-08-18 note ruled this, and
  FR-367 restates it: submitting either kind of objective "remains `model:submit`". This row
  records the existing ruling and changes nothing.
- **`rating_version:deploy_prod` and `rating_version:deploy_*` → `deployment:promote`.** Ruled in
  the WK-674 ruling (PR #848, DP-6), which amends `06:62` and `:219` itself. It is cited here so
  the catalogue has one row per name. It is not re-ruled.

### The "add to 06" verdicts are not scope changes

Each of the twelve names is **already checked** by the route cited in its row, so each already
grants exactly what it will be specified to grant. Writing it into `06` records built behaviour
and grants nothing new. Row 33's `admin:break_glass` is FR-349's elevation, which `06` specifies
without naming the permission. This commit adds the twelve to `06` §4.1 as a dated amendment:
a catalogue table placed after §4.1's existing notes. No new section number is created, since
§4.1 already exists and already covers `Permission`.

### The spec-only verdicts

Each is carried to the Work its capability belongs to: WK-690 for `custom_objective:author`
(FR-367 names that Work), WK-687 for monitors, WK-688 for alerts, WK-684 for optimisation runs
and WK-686 for materialisation. None is built now (`CLAUDE.md` §0: no later phase built ahead).
The Work that builds the capability adds the check and its negative test.

## Decision points for the maintainer (by delegation, the deputy)

These three change scope, so they are not ruled here. They follow the `document-ids.md` §1.7
form. Rows marked "pending DP-x" above take their verdict from the dated decision, which is
filled in before this record mints.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-A | **Granularity.** `06` names per-artifact write rights (`rating_algorithm:write`, `rate_table:write`, `factor:write`, `banding:write`, `grouping:write`, `dataset:create_version`). The code checks one broader name per family: `rating:write` (algorithms, rate tables and Rating Version creation), `model:fit` (factors, bandings, groupings, and fitting), `dataset:write` (datasets, versions, blobs, validation rules, ingestion). Which is the catalogue? | **(a) The code's coarse names.** Map the six spec names onto `rating:write`, `model:fit` and `dataset:write`, and amend `06`. No code change. It loses the roles `06` could express, e.g. a rate-table maintainer who cannot edit algorithms. **(b) The spec's fine names.** Split the three code names, and the routes check the fine names. It keeps every `06` role expressible, but costs a migration of role grants and new route checks, and it grants per-artifact rights the code never had. **(c) The coarse names now, with the fine split carried to WK-676** (Phase 3, scoped roles), recorded in `06` as the target. | **(c).** The built surface and the tests use the coarse names. No Phase 2 requirement needs a per-artifact write right. The scoped-role Work is where finer grants belong. (a) silently drops what `06` meant to allow. (b) is Phase 3 work built ahead | decision point (scope) | yes: rows 11–16, 22 and 23; WK-673 Slice 4 and WK-674 Slice 2 if they add a write check | |
| DP-B | **`admin:manage_environments`**: defined and granted to Admin, and checked nowhere (0 hits). Keep it, or remove it? | **(a) Keep it, specified in `06` as owned by WK-674**, whose Slice 2 builds the Environment record (`07` FR-428) and its management route. **(b) Remove it** as dead code until a route needs it. | **(a).** FR-428 makes an Environment a first-class, configurable object. Something must govern who manages it, and WK-674 Slice 2 is that route. Removing it and re-adding it in the same phase is churn | decision point (scope) | yes: row 34; WK-674 Slice 2 | |
| DP-C | **`model:approve` and "every `*:approve`"** (`06:62`, `:218`) against the code's single `approval:decide`, which covers every artifact type (`approvals.py:63`; `validation.py:65`; `platform/validation_rules.py:403`). | **(a) One `approval:decide`**, with per-type approval governed by the `ApprovalPolicy` entry's `approver_roles` (§4.2) and by scoped assignments. Amend `06:62` and `:218`. **(b) Per-type approve permissions** (`model:approve`, `rating_version:approve`, …), split in code. **(c) (a) now, and per-type approve rights considered with WK-676's scoping.** | **(a).** Who may approve which type is already expressed per artifact type by §4.2's `approver_roles`, and per artifact family by FR-345's scope. A per-type permission would be a third mechanism for one rule. `06` §5.1 (`:466`) already names `approval:decide` for the deciding routes | decision point (scope) | yes: row 17 | |

## What it obliges

- **This commit:** the `06` §4.1 dated amendment, which adds the twelve built names, the two
  map aliases and the spec-only carry list. The pending rows are **not** written into `06`
  until their DPs are decided.
- **Before this record mints:** the deputy's dated decisions on DP-A, DP-B and DP-C are quoted
  in a follow-up commit. The pending rows take their verdicts, and any `06` amendment those
  decisions require lands in the same commit.
- **Until then** (the deputy's item 4(b)): any slice that adds or checks a permission states in
  its leaf plan which name it uses and why, citing the permission-catalogue finding.
- **WK-674 Slice 2:** `deployment:promote`'s check (rows 3, 4 and 24), and DP-B's route if (a)
  is decided.
- **WK-690:** `custom_objective:author` (row 5). **WK-687, WK-688, WK-684, WK-686:** rows 6–10.
- **Plan review 15:** the general question stays with it: whether `06` or the code is the
  source of record for the catalogue from now on. This record is the per-name working
  resolution and does not answer that.

## Acceptance — the violation that must become detectable

The violation: **a permission name used by the code that `06` does not name, or named by `06`
with no owner, after this record's verdicts are applied.** This record builds nothing, so it
proves nothing red itself. The check it asks for is a two-list comparison: the two predicates
above, and a `comm -3` of their outputs against this table's rows. It is proposed to plan
review 15 as a docs check. Until one exists, the table is re-derived at each Work close that
touches permissions.
