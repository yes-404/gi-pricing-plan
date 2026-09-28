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

*The `06` count is of `06` at `37b2596e`, before this record's own §4.1 amendment. At this
branch's head, the same predicate counts more names, because the amendment writes the built
names into `06`. That is the purpose of the amendment, and it is not drift. `06`,
`permissions.py`, `platform/approvals.py` and `backend/src/app/api/` are unchanged between
`37b2596e` and `81e061fb`: `git diff --stat 37b2596e 81e061fb -- <those paths>` is empty.*

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
| 11 | `rating_algorithm:write` | 06 | **map → `rating:write`** (DP-A (c)); the fine split is carried to WK-676 | `06:199`. The code checks `rating:write` at `backend/src/app/api/rating_algorithms.py:24` |
| 12 | `rate_table:write` | 06 | **map → `rating:write`** (DP-A (c)); the fine split is carried to WK-676 | `06:199`. The code checks `rating:write` at `backend/src/app/api/rate_tables.py:45` |
| 13 | `factor:write` | 06 | **map → `model:fit`** (DP-A (c)); the fine split is carried to WK-676 | `06:197`. `create_factor` checks `model:fit` (`FitModels`, `backend/src/app/api/models.py:108`, route at `:280-286`) |
| 14 | `banding:write` | 06 | **map → `model:fit`** (DP-A (c)); the fine split is carried to WK-676 | `06:197`. `create_banding` checks `model:fit` (`models.py:384-390`) |
| 15 | `grouping:write` | 06 | **map → `model:fit`** (DP-A (c)); the fine split is carried to WK-676 | `06:197`. `create_grouping` checks `model:fit` (`models.py:474-480`) |
| 16 | `dataset:create_version` | 06 | **map → `dataset:write`** (DP-A (c)); the fine split is carried to WK-676 | `06:196`. The code checks `dataset:write`, which guards more than version creation: see row 23 |
| 17 | `model:approve` | 06 | **map → `approval:decide`** (DP-C (a)); per-type approval is `ApprovalPolicy.approver_roles` | `06:62`, and `:218` ("every `*:approve` permission"). The code has one `approval:decide` for every type |
| 18 | `dataset:validate` | code | **add to 06** | 1 hit: `backend/src/app/api/dataset_versions.py:62` |
| 19 | `rating:read` | code | **add to 06** | 6 hits, the first at `backend/src/app/api/models.py:1112`. Also `rate_tables.py:46` and `rating_algorithms.py:25` |
| 20 | `rating:compile` | code | **add to 06** | 1 hit: `backend/src/app/api/models.py:1222` (`compile_rating_version`) |
| 21 | `rating:submit` | code | **map survivor** (row 1) | 2 hits: `backend/src/app/api/models.py:1195` (`submit_rating_version`) and `backend/src/app/platform/rating_versions.py:227`. Both are Rating Version submission |
| 22 | `rating:write` | code | **map survivor** (rows 11–12; DP-A (c)) | 4 hits: `models.py:1162` (`create_rating_version`), `rate_tables.py:45`, `rating_algorithms.py:24`, `platform/rating_versions.py:180` |
| 23 | `dataset:write` | code | **map survivor** (row 16; DP-A (c)) | 11 hits across datasets (`api/datasets.py:87`), versions (`api/dataset_versions.py:61`), blobs (`api/blobs.py:40`), validation rules (`api/validation.py:59`, `platform/validation_rules.py:203`) and ingestion (`data/ingestion.py:124`) |
| 24 | `deployment:promote` | code | **map survivor** (rows 3–4) | **0 hits**. The deploy route is not built. WK-674 Slice 2 builds the check (the WK-674 ruling, PR #848) |
| 25 | `audit:read` | code | **add to 06** | 1 hit: `backend/src/app/api/audit.py:52` |
| 26 | `score:execute` | code | **add to 06** | 1 hit: `backend/src/app/api/score.py:110`. `07` §4.3 already names it, at line 261 of `07` |
| 27 | `score:batch` | code | **add to 06** | 2 hits: `backend/src/app/api/score.py:111`, and a docstring at `:38` |
| 28 | `job:read` | code | **add to 06** | 2 hits: `backend/src/app/api/jobs.py:62`, and a docstring at `authz.py:3` |
| 29 | `job:cancel` | code | **add to 06** | 1 hit: `backend/src/app/api/jobs.py:63` |
| 30 | `settings:read` | code | **add to 06** | 1 hit: `backend/src/app/api/settings.py:33` |
| 31 | `admin:manage_settings` | code | **add to 06** | 7 hits, the first at `backend/src/app/api/reference_tables.py:51`. Also `platform/reference.py:75` and `platform/datasets.py:995` |
| 32 | `admin:manage_service_accounts` | code | **add to 06** | 1 hit: `backend/src/app/api/service_accounts.py:40`. It is already checked, so it is not a DP-B name. WK-674 Slice 3's per-environment key routes (#843's permission table) extend this router under the same name |
| 33 | `admin:break_glass` | code | **add to 06** | 1 hit: `backend/src/app/platform/rbac.py:424` (FR-349's elevation) |
| 34 | `admin:manage_environments` | code | **add to 06, owned by WK-674 Slice 2** (DP-B (a)): the Environment record's lifecycle only. Environment settings are `admin:manage_settings` (DP-D (b)) | **0 hits.** Its only occurrences are its definition and the admin role set (`permissions.py:69`, `:146`). #843's permission table (at `1b102201`) plans it for Slice 2 (create and list Environments), Slice 3 (environment configuration) and Slice 6 (shadow configuration) |

**Verdict counts:**

| Verdict | Rows | Count |
|---|---|---|
| map (a name, or a survivor) | 1–4, 11–17, 21–24 | 15 |
| spec-only, carried | 5–10 | 6 |
| add to 06 | 18, 19, 20, 25–34 | 13 |
| **Total** | | **34** |

*Before the deputy's decisions (at `3cd243af`), the split was: map 6, spec-only 6, add 12,
pending DP-A 8, DP-B 1, DP-C 1. The decisions moved DP-A's eight and DP-C's one to map, and
DP-B's one to add.*

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

These four change scope, so they are not ruled here. They follow the `document-ids.md` §1.7
form. Rows marked "pending DP-x" above take their verdict from the dated decision, which is
filled in before this record mints.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-A | **Granularity.** `06` names per-artifact write rights (`rating_algorithm:write`, `rate_table:write`, `factor:write`, `banding:write`, `grouping:write`, `dataset:create_version`). The code checks one broader name per family: `rating:write` (algorithms, rate tables and Rating Version creation), `model:fit` (factors, bandings, groupings, and fitting), `dataset:write` (datasets, versions, blobs, validation rules, ingestion). Which is the catalogue? | **(a) The code's coarse names.** Map the six spec names onto `rating:write`, `model:fit` and `dataset:write`, and amend `06`. No code change. It loses the roles `06` could express, e.g. a rate-table maintainer who cannot edit algorithms. **(b) The spec's fine names.** Split the three code names, and the routes check the fine names. It keeps every `06` role expressible, but costs a migration of role grants and new route checks, and it grants per-artifact rights the code never had. **(c) The coarse names now, with the fine split carried to WK-676** (Phase 3, scoped roles), recorded in `06` as the target. | **(c).** The built surface and the tests use the coarse names. No Phase 2 requirement needs a per-artifact write right. The scoped-role Work is where finer grants belong. (a) silently drops what `06` meant to allow. (b) is Phase 3 work built ahead | decision point (scope) | yes: rows 11–16, 22 and 23; WK-673 Slice 4 and WK-674 Slice 2 if they add a write check | **(c)**, decided by the deputy by delegation; the entry is quoted below |
| DP-B | **`admin:manage_environments`**: defined and granted to Admin, and checked nowhere at `37b2596e` (0 hits). #843's plan (at `1b102201`) uses it in Slices 2, 3 and 6. Keep it, or remove it? (`deployment:promote`, also 0 hits, is ruled by #848's DP-6. `admin:manage_service_accounts` is checked today, row 32. Neither is a DP-B name.) | **(a) Keep it, with the owning Work named: WK-674.** It is added to `06` §4.1 as governing the Environment object (`07` FR-428): create, list and retire. Its first check lands in WK-674 Slice 2. Whether it also guards an Environment's configuration is DP-D. **(b) Remove it** as dead code until a route needs it, and re-add it in Slice 2. | **(a).** FR-428 makes an Environment a first-class, configurable object, and WK-674 Slice 2 builds its management route in this phase. Removing the name and re-adding it within the phase is churn, and would briefly leave that route with no name to check | decision point (scope) | yes: row 34; WK-674 Slice 2 | **(a)**, decided by the deputy by delegation; the entry is quoted below |
| DP-C | **`model:approve` and "every `*:approve`"** (`06:62`, `:218`) against the code's single `approval:decide`, which covers every artifact type (`approvals.py:63`; `validation.py:65`; `platform/validation_rules.py:403`). | **(a) One `approval:decide`**, with per-type approval governed by the `ApprovalPolicy` entry's `approver_roles` (§4.2) and by scoped assignments. Amend `06:62` and `:218`. **(b) Per-type approve permissions** (`model:approve`, `rating_version:approve`, …), split in code. **(c) (a) now, and per-type approve rights considered with WK-676's scoping.** | **(a).** Who may approve which type is already expressed per artifact type by §4.2's `approver_roles`, and per artifact family by FR-345's scope. A per-type permission would be a third mechanism for one rule. `06` §5.1 (`:466`) already names `approval:decide` for the deciding routes | decision point (scope) | yes: row 17 | **(a)**, decided by the deputy by delegation; the entry is quoted below |
| DP-D | **Which permission guards an Environment's configuration?** This covers FR-431's environment settings (rate limits, sampling rates, feature flags; `PUT /api/v1/environments/{name}/settings`) and FR-271's shadow configuration, which the deputy's WK-674 DP-2 makes "an environment setting with its own audit event". #843's permission table leaves this to this record. | **(a) `admin:manage_environments`:** one guard for the Environment and everything configured on it. A settings admin cannot loosen `prod`'s limits without environment rights. **(b) `admin:manage_settings`:** FR-431 says environment configuration "is a Setting resolved by the precedence in §3.8", and `admin:manage_settings` already guards the workspace layer (`platform/datasets.py:995`, `platform/reference.py:75`), so every Setting has one guard. `admin:manage_environments` then governs only the Environment object. **(c) Both required.** | **(b).** `07` FR-431 already classifies environment configuration as a Setting, and a Setting has one audited write path. (a) creates a second guard for the same mechanism, split by which layer is written. (c) adds a conjunction no requirement asks for. If the deputy prefers (a) for `prod` safety, the plan's rows for Slices 3 and 6 already use it | decision point (scope) | yes: WK-674 Slices 3 and 6 (not Slice 2) | **(b)**, decided by the deputy by delegation; the entries are quoted below |

### The deputy's decisions, whole and verbatim

Three entries follow, each fenced so that the ids it quotes are read as quotation
(`audit-docs.py` check 32 skips fenced blocks). The first decides DP-A, DP-B and DP-C. The
second decides DP-D. The third confirms DP-D's scope for Slice 6.

#### DP-A, DP-B and DP-C

Fenced, so that the ids it quotes are read as quotation (`audit-docs.py` check 32 skips fenced
blocks). The entry was read on this branch at `3cd243af`, before DP-D existed. DP-D is
decided by the two entries after it.

```text
## 2026-09-28 15:01:11 BST · deputy · RL-9204 (#856, the permission catalogue): DP-A, DP-B and DP-C DECIDED, with the approval-separation conditions they depend on

Given by the maintainer's delegation (28 Sep, extended goal). dm-e quotes this entry, fenced, in #856's follow-up commit before the mint. The pending rows take these verdicts, and any `06` amendment lands in the same commit. Read at `p2-perm-catalogue-rl` `3cd243af`.

**DP-A (granularity): (c) DECIDED.** The code's coarse names are the P2 catalogue: `rating:write` (algorithms, rate tables, Rating Version creation), `model:fit` (factors, bandings, groupings, fitting) and `dataset:write`. The six per-artifact spec names are mapped onto them, and `06` §4.1 is amended (dated). **The fine split is carried to WK-676 (P3, scoped assignments)**, deferred with an owner, with the P2 closure record as the event. **Condition:** coarse write rights are acceptable only because the **approval step separates author from approver**. The RL cites where that separation is enforced at `37b2596e`: the rule, or the code, that refuses an approval by the submitter / author of the same artifact version. **If no such check exists in code, that is a new `FD-` and a WK-674 S2 or WK-1178 fix**, because a platform that approves its own pricing changes fails its governance purpose.

**DP-B (`admin:manage_environments`): (a) DECIDED.** Keep it, specified in `06` as owned by WK-674 S2, whose Environment record and management route (`07` FR-428) are the first check of it. S2's acceptance includes a negative test: a non-Admin is refused the environment-management route. (dm-e's recount, which found the `Perm` alias checks its first grep missed and reduced DP-B to this one name, is noted. The catalogue's predicates must include the alias form, stated verbatim in the RL.)

**DP-C (`model:approve` and "every `*:approve`"): (a) DECIDED.** One `approval:decide`. **Per-type approval is governed by the `ApprovalPolicy` entry's `approver_roles` (`06` §4.2)** and, from P3, by scoped assignments. `06:62` and `:218` are amended (dated). **Condition:** the RL cites the test that proves **a holder of `approval:decide` who is not in the entry's `approver_roles` is refused**. If none exists, S2 of WK-674 (or WK-1178) adds it, red then green. Without that test, (a) quietly lets any approver approve anything.

**What these decisions do not change:** plan review 15 still decides the general source-of-record question (`06` or the code) going forward. The FD-9008 interim rule (every permission-touching slice names its choice) stays until #856 merges.
```

#### DP-D

```text
## 2026-09-28 15:03:38 BST · deputy · RL-9204 (#856, now at `5882e91b`): DP-D DECIDED, (b). DP-A, DP-B and DP-C stand as decided at 15:01:11 (DP-B's owner wording is consistent)

**DP-D (which permission guards an Environment's configuration: FR-431 settings plus FR-271 shadow config): (b) DECIDED, `admin:manage_settings`.** It rests on `07` FR-431 calling it a Setting, and on `admin:manage_settings` already guarding the settings route (`api/settings.py:34`, 7 hits, the lead's verification at `81e061fb`). **The split, stated so the two permissions never overlap:**
- **`admin:manage_environments`** (DP-B): the Environment **record's lifecycle**: create, rename, retire. That is WK-674 S2.
- **`admin:manage_settings`**: every **per-environment setting value**, including FR-431's settings and FR-270/FR-271's per-environment on/off and shadow configuration. That is WK-674 S3 and S6.
- **Every settings change writes an Audit Event naming the environment, the key, the old value and the new value** (consistent with my 14:08:59 DP-2 condition: "Enabling one is an environment setting with its own audit event"). S6's acceptance includes a negative test: a user without `admin:manage_settings` is refused enabling shadow on `prod`.

dm-e quotes this entry alongside the 15:01:11 entry in #856's follow-up, and #856 mints after that. DP-D blocks S3 and S6, not S2, as stated.
```

#### DP-D's scope for Slice 6, confirmed

```text
## 2026-09-28 15:05:53 BST · deputy · DP-D scope, CONFIRMED: S6 (i) (deploying a version with an effective-date range) stays `deployment:promote`. (ii) (the routing/shadow switches and shadow config) takes `admin:manage_settings`, with one safeguard on the routing switch

My 15:03:38 "FR-270/271's per-environment on/off" meant **the switch only**. The split planner-674 made is right, and your reason is the rule: **nothing guarded by `admin:manage_settings` may change which Rating Version prices a live quote.**
- **(i) Deploying a Rating Version with an effective-date range → `deployment:promote`**, with DP-7's approval floor for `prod` and FR-270's overlap rejection *"at deployment time"*.
- **(ii) The routing on/off switch, the shadow on/off switch and shadow configuration → `admin:manage_settings`**, each change writing an Audit Event (env, key, old, new).
- **The safeguard on (ii)'s routing switch:** turning date-routing **on** may only select among versions that were **deployed through `deployment:promote`** into that environment. It never makes a version live that was not promoted there. S6 includes a negative test: with routing on, a version present in the environment but not promoted is never selected. **Shadow** results are recorded, never served, so the shadow switch cannot change a live price, and needs no further guard beyond the audit.

dm-e's RL-9204 quotes this entry with the 15:01:11 and 15:03:38 entries. planner-674's S6 rows cite it.
```

### The conditions, checked at `81e061fb`

**DP-A's condition: where the approval step separates author from approver.**
- **The submitter is separated, in code and under test.**
  - `backend/src/app/platform/approvals.py:260` refuses `row.submitted_by == approver.id` with
    `SUBMITTER_CANNOT_APPROVE`, before the permission check. It is not configurable (`06` R1,
    FR-353).
  - The tests are `test_the_submitter_cannot_approve_their_own_work`
    (`backend/tests/test_approvals.py:68`, asserting at `:86`) and
    `test_the_submitter_cannot_approve_even_holding_the_approver_role`
    (`backend/tests/test_api_approvals.py:330`, asserting at `:353`).
  - FR-353's text is *"the submitter cannot approve"*.
- **The author is separated for Validation Rules only.** `ValidationRuleRow.authored_by`
  (`backend/src/app/db/models.py:1115`) is refused as approver by
  `platform/validation_rules.py:414`, and by the check constraint `approved_by <> authored_by`
  (`models.py:1150`).
- **The author is not separated for rating artifacts.** `RatingVersionRow`,
  `RatingAlgorithmRow` and `RateTableVersionRow` record `created_by` (`models.py:1899`,
  `:1938`, `:2003`). `approvals.decide` compares only `submitted_by`. An author who did not
  submit can therefore approve the version they wrote. This matters for DP-A, because with
  coarse `rating:write` every Pricing Actuary may author any rating artifact.
- **So the condition is met for the submitter and not met for the author.** The deputy's
  entry makes the missing check a new finding: **the author≠approver finding (filed in #855)**,
  filed by auditor-b. It states that approval separation is submitter-based, so the author of
  a rating artifact version who is not its submitter may approve it. The deputy picks the
  fix's home, WK-674 Slice 2 or WK-1178. This record names the finding and does not file it.

**DP-B's condition.** WK-674 Slice 2's acceptance includes a negative test: a principal
without `admin:manage_environments` (a non-Admin) is refused the environment-management
route. The alias-aware predicate is stated verbatim above, under the two lists.

**DP-C's condition: a test that an `approval:decide` holder outside `approver_roles` is
refused. It is met; no code change is needed.**
- `test_a_role_the_policy_does_not_name_cannot_approve` (`backend/tests/test_approvals.py:346`,
  marked `FR-354` at `:345`) narrows the `model` entry's `approver_roles` to `("admin",)`.
- It gives the deciding principal the `approver` role, which carries `approval:decide`. The
  test's own comment reads *"Give the deployer the raw permission so the refusal is about the
  *role*, not the permission"*.
- It asserts `PERMISSION_DENIED` with `admin` named in the detail (`:383-384`).
- The check under test is `_check_approver_role` (`platform/approvals.py:435`), called at
  `:275` after `require_permission(... APPROVAL_DECIDE)` at `:269-274`.

## What it obliges

- **This record's commits:** the `06` §4.1 dated amendment, which adds the built names, the
  map aliases, DP-A's and DP-C's maps, DP-B's owned name and the spec-only carry list. `06:62`
  and `:218` are amended for DP-C. The DP-D split is written into §4.1's catalogue rows.
- **WK-676 (Phase 3):** the per-artifact write split (DP-A), deferred with an owner, with the
  P2 closure record as the event.
- **The conditions, as obligations:**
  - **DP-A:** the approval step must refuse the **author** of the artifact version, not only
    its submitter. At `81e061fb` it refuses the submitter only, for rating artifacts (see the
    conditions above). This is the author≠approver finding (filed in #855). Its fix and negative
    test land in the home the deputy picks, WK-674 Slice 2 or WK-1178.
  - **DP-C:** the refusal of an `approval:decide` holder outside `approver_roles` stays under
    test. `test_a_role_the_policy_does_not_name_cannot_approve` (`test_approvals.py:346`) is
    that test, and any change to `_check_approver_role` keeps it green.
  - **DP-B:** WK-674 Slice 2 proves on broken input that a non-Admin is refused the
    Environment route.
  - **DP-D:** the two permissions never overlap.
    - `admin:manage_environments` guards the Environment record's lifecycle: create, rename,
      retire (Slice 2).
    - `admin:manage_settings` guards every per-environment setting value: FR-431's settings,
      the routing and shadow switches, and shadow configuration (Slices 3 and 6).
    - Every settings change writes an Audit Event naming the environment, the key, the old
      value and the new value.
    - Deploying a version with an effective-date range stays `deployment:promote`.
    - Turning date-routing on only selects among versions promoted into that environment.
    - Slice 6 adds two negative tests: without `admin:manage_settings`, enabling shadow on
      `prod` is refused; and with routing on, a version present in the environment but not
      promoted is never selected.
- **Done in this follow-up commit:** the deputy's decisions on DP-A, DP-B and DP-C are quoted
  in a follow-up commit. The pending rows take their verdicts, and any `06` amendment those
  decisions require lands in the same commit.
- **Until then** (the deputy's item 4(b)): any slice that adds or checks a permission states in
  its leaf plan which name it uses and why, citing the permission-catalogue finding.
- **WK-674:** Slice 2 builds `deployment:promote`'s check (rows 3, 4 and 24, #848's DP-6) and
  DP-B's Environment route. Slices 3 and 6 guard environment configuration by DP-D's decision.
  Slice 3's key routes use `admin:manage_service_accounts` (row 32).
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
