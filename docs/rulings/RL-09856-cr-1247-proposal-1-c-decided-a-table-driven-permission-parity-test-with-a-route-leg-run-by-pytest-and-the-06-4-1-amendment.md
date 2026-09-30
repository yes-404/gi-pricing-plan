---
id: RL-9856
family: ruling
title: CR-1247 Proposal 1 (c) decided — a table-driven permission-parity test with a route leg, run by pytest, and the 06 §4.1 amendment
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 48792023e09cd79c771c2184d6808e378732b76b
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [CR-1247, RL-1236, PL-1268, PL-1279, PL-1237, ADR-704, FR-367]
---

# RL-9856 — CR-1247 Proposal 1 (c) decided — a table-driven permission-parity test with a route leg, run by pytest, and the 06 §4.1 amendment

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). The session's
own `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`.

The record was prepared at effort `medium` (PR #942, head `2f26abb1`, "PREPARED, NOT
RULED"). Its evidence, options and prepared recommendations are kept below as prepared.
**The decisions are in "Ruled"**, and **the `06` §4.1 amendment (D4) is in this commit.** It
keeps the working id 9856; the id is minted at the lead's merge turn.

*Re-verified 2026-09-30 at `48792023`:* `git diff --stat dee49f78 48792023 --
packages/model-schema/src/model_schema/permissions.py docs/specs/06-governance.md
.github/workflows docs/adrs/ADR-00704*` prints nothing, and the counts reproduce: 24 members;
13 §4.1 rows; the same 11 members without a row; and 0 check sites for `deployment:promote`
and `admin:manage_environments`.

*Refreshed 2026-09-30 at origin/main `0bc69b5b`: the deciding evidence is unchanged.*
- `permissions.py`, `06`, `backend/src`, `.github/workflows` and ADR-704 are unchanged since
  `dee49f78` (`git diff --stat` is empty).
- So these still hold: 24 enum members; 13 §4.1 rows, with the same 11 members missing;
  0 caller-predicate sites for `deployment:promote` and `admin:manage_environments`; and
  `docs.yml` not triggering on `packages/**`.
- CR-1247 and RL-1236 are unchanged.
- PL-1268 changed (37 insertions, 8 deletions), but its Slice 3 still requires the parity
  check and its RL first. It is now cited by heading.
- The working id 9970 is now cited as PL-1279.

## What is already decided, and so is not prepared here

**`CR-1247` Proposal 1** (`docs/closures/CR-01247-…-p2-s-exit.md:81-159`) was decided as (c):
- **Lead verdict:** "ADOPTED, (c)", 2026-09-29 (`:158`).
- **Maintainer acceptance:** "Accepted: (c), one permission source of record plus a gate
  check", 2026-09-29, by delegation (`:159`).

(c) splits the two jobs:
- `model_schema.Permission` and `BUILTIN_ROLES` are the one definition of the **names** and
  of the built-in role sets.
- `06` is the source of record for their **meaning**.
- A check fails the gate when `06` and the enum disagree.
- A new permission lands in one commit: the `06` row, the enum member and the route check.
- **The decision-maker** writes the `RL-` and the `06` amendment, which replaces the role
  block's names with a reference to `BUILTIN_ROLES`.
- **WK-1178** builds the check before the first slice that adds a name: WK-690's
  `custom_objective:author` (`RL-1236` row 5; PL-1268 §Tasks, "Slice 3 — The `expression`
  kind through the platform, behind the flag", its "Depends on", and §Activation's Slice 3
  line).
- Until then, `RL-1236`'s interim rule stands (`RL-1236` Acceptance, `:409-417`).

This record prepares only what (c) leaves open: **what the check asserts, where it runs, the
record's form, and the `06` amendment's content.**

## Evidence, measured at `dee49f781fd23f9df2e72161885c77fa17a6f1ab` (origin/main)

Each count below gives its predicate.

1. **The enum has 24 members.** Predicate: the regex
   `^\s+[A-Z_]+\s*=\s*"([a-z_]+:[a-z_]+)"`, multiline, over
   `packages/model-schema/src/model_schema/permissions.py` (`class Permission` at `:28`).
   `BUILTIN_ROLES` is at `:131`. `custom_objective:author` is not a member.
2. **The `06` §4.1 permission table has 13 rows.** The section runs from `docs/specs/06-governance.md:188`
   (`### 4.1`) to the line before `### 4.2`, and the table header `| Permission | Governs |` is
   at `:262`. Predicate: each line matching `^>?\s*\|\s*`([a-z_]+:[a-z_*]+)`` within that
   span.
   - All 13 rows are enum members.
   - **11 enum members have no §4.1 row:** `admin:manage_roles`, `approval:decide`,
     `dataset:acknowledge_warning`, `dataset:read`, `dataset:write`, `deployment:promote`,
     `model:fit`, `model:read`, `model:submit`, `rating:submit` and `rating:write`. They are
     described only in prose elsewhere in `06`.
   - **So the check as `CR-1247` words it ("an enum member has no `06` §4.1 row") is red at
     this tree.** The `06` amendment must add those 11 rows in the commit that lands the
     check, or before it.
3. **The whole of `06` holds 41 distinct `name:name` tokens.** Predicate: `RL-1236`'s
   whole-`06` predicate, `\b[a-z][a-z_]*:([a-z_]+\b|deploy_\*)` less `:motor$` and
   `^type:name$`.
   - Every enum member appears somewhere in `06`.
   - **17 tokens are not enum members:** `RL-1236`'s maps and aliases (for example
     `rating_version:submit`, `model:approve`, `rating_algorithm:write`), its spec-only rows
     5–10, `custom_objective:submit` (named at `06:224` as not existing), and a `rating_version:deploy_`
     fragment the regex cuts from `deploy_*`.
   - These are the tokens `CR-1247`'s exclusions ("struck text, the §4.1 alias notes, and
     `RL-1236` rows 5–10") have to remove. **Today they are identified only by their
     position in prose.**
4. **The Pricing Actuary role block** (`06:190-205`, a JSON example) names 16 permissions,
   and 12 of them are not enum members. `CR-1247` measured this at `1c8762d9`, and the lines
   are unchanged at this tree. In code, `BUILTIN_ROLES["pricing_actuary"]` is `_analyst()`
   plus additions (`permissions.py:131-152`).
5. **Route checks.** The caller predicate is `RL-1236`'s,
   `git grep -n -E "(Perm|Permission)\.<NAME>\b" -- backend/src | grep -v '#'`, run once per
   member. **Two enum members have 0 check sites:**
   - `admin:manage_environments`, owned by WK-674 Slice 2 (`RL-1236` DP-B);
   - `deployment:promote`, whose deploy route is unbuilt (`RL-1236` row 24).

   `requires()` is at `backend/src/app/api/authz.py:54`. A route leg that demands a check site
   for every member is therefore red today unless it declares these two.
6. **CI path filters.** `.github/workflows/docs.yml:16,18` triggers on `docs/**`, the doc
   scripts, `CLAUDE.md`, `.claude/**` and the workflow itself. **It does not trigger on
   `packages/**`.** `.github/workflows/python.yml:6-31` triggers on `packages/**`,
   `backend/**` **and** `docs/**`.
   - A parity check placed only in `audit-docs.py` does not run on a commit that adds an enum
     member and leaves `docs/` untouched. That is exactly the drift it exists to catch, and
     the failure CLAUDE.md §2 names: path filtering lets a check "pass by not running".
7. **ADR-704** (`docs/adrs/ADR-00704-model-schema-is-the-single-source-of-truth-for-shared-shapes.md:24-44`)
   already decides that `model-schema` holds every shared shape and that everything else is
   generated from it. `permissions.py`'s docstring (`:1-20`) places the vocabulary there "because both sides need it and
   neither may invent it". `06` restating the names is the second definition that CLAUDE.md
   §2 and ADR-704 forbid, and (c) applies ADR-704 to it.

## D1: what the check asserts

| | Option | For | Against |
|---|---|---|---|
| (A) | `CR-1247`'s wording, literally. Every enum member has a §4.1 row. Every `06` token is an enum member, except struck text, the alias notes and `RL-1236` rows 5–10, identified by parsing their position in prose. | Closest to the accepted text | The exclusions are heuristics over prose, such as `~~` spans and blockquote alias notes. A check that decides what to ignore by layout is the weak kind (a new note in a new place is silently excluded or wrongly flagged). It is red at this tree until 11 rows are added. |
| (B) | **Table-driven.** `06` §4.1 carries three machine-read tables. **Built** (name, governs) must equal the enum set in both directions. **Specified, not built** (name, owner Work) must be disjoint from the enum, and each owner must resolve to a roadmap row. **Aliases** (`06`-era name → enum name): the right side must be a member. Any other `name:name` token in `06` outside struck text must appear in one of the three tables. | The exclusions become declared data, not layout. A new permission moves from "Specified" to "Built" in the same commit as its enum member, which **is** (c)'s one-commit rule made visible. `RL-1236` rows 5–10 become rows with owners. | A larger `06` amendment: 11 rows added, rows 5–10 and the alias notes turned into tables |
| (C) | (B), plus a **route leg**: every Built name has at least one caller-predicate hit in `backend/src`, or its row names the Work that builds the check | Covers the third element of the one-commit rule (the route check) | Two rows need a check owner now (`admin:manage_environments`, `deployment:promote`). The caller predicate is a regex over code, which the aliasing trap (`Perm.` versus `Permission.`, `RL-1236` `:79-87`) has already fooled once. |

**Prepared recommendation (superseded by "Ruled"): (C).**
- (B) is the part that makes the check trustworthy.
- The route leg is what makes "the enum member and its check land together" (FR-367;
  PL-1268 Slice 3) a gate rather than a review item. That is the case this check is being
  built for.
- The route leg's owner cell keeps the two current gaps honest instead of red.
- **Fallback:** (B), with the route leg left to each slice's own negative test (as PL-1268
  acceptance item 8 already does for `custom_objective:author`), if the high pass judges the
  regex route leg too fragile.

**Open item under D1 for the ruling: a ninth violation class, `STALE_OWNER`** *(added
2026-09-30, at the lead's request; not ruled).*
- **The proposal.** WK-1178's leaf plan, **PL-1279**, proposes it in §Tasks, Task 1 ("The pure
  comparison, and each violation class proved red"): "Built name has a check site and still
  carries an owner: clear it in the same commit". Task 1 also holds its synthetic red proof.
  - The plan is PL-1279 (#944; read before minting on `origin/wk1178-parity-leaf` at
    `e56809ed` and `42b9774d`, and re-read on main at `0bc69b5b` on 2026-09-30, where it is
    still `draft` and its DP-1 to DP-3 await this record's D1, D2 and D4).
  - *(Citations changed 2026-09-30 from line numbers to section headings, at the lead's
    request, because the line numbers moved between those two heads.)*
- **It is not among this record's four acceptance fixtures.** Those cover a missing Built row,
  a Built row with no member, a Specified name that is a member, and a Built name with no check
  site and no owner. `STALE_OWNER` is the converse of the fourth.
- **What adopting it means.** WK-674 Slice 2 must clear the owner cells on `deployment:promote`
  and `admin:manage_environments` **in the commit that adds their check sites**. Their rows are
  in the permission table of PL-1237 (`docs/plans/PL-01237-wk-674-deployment-environments-switchover-tenancy-map-plan.md:481-484`),
  where Slice 2 builds both checks. If Slice 2's commit does not also touch `06` §4.1, the gate
  goes red on it.

| | Option | For | Against |
|---|---|---|---|
| (adopt) | `STALE_OWNER` is a fifth fixture and a live violation class | An owner cell cannot outlive the work it names. Without it, a cleared gap still reads as open in `06`, which is RFC-756's stale-status failure in a new place. It completes the route leg in both directions. | It couples a code slice (WK-674 S2) to a `06` edit in the same commit. That is the one-commit rule (c) already imposes for a *new* name, now applied to closing an existing gap. |
| (omit) | Only `NO_CHECK_NO_OWNER`; a stale owner cell is tidied at the next Work close | Looser coupling for WK-674 S2 | The owner cell becomes a claim nothing re-checks, the kind of cell the route leg exists to keep honest |

**Prepared recommendation (superseded by "Ruled"): adopt.**
- It is the same one-commit discipline (c) already requires. The cost falls on one known
  commit: WK-674 S2's, whose plan already names both check sites.
- The ruling should also tell WK-674 S2's leaf plan about it, so the requirement is not first
  discovered as a red gate.
- Under D1 (B), the fallback, the class is dormant on the live tree because `checked` is the
  whole enum (PL-1279, §Scope, "The slice under 9856 D1 (C), and under its fallback
  (B)"). It is therefore free to keep either way.
- The leaf plan's E5 (PL-1279 §Scope, "Today's mismatches", E5) also records a third unchecked
  member "if only `requires()` routes count". ~~That is the `service_accounts.py` literal
  `RL-1236` corrected.~~
  - *Corrected 2026-09-30, after the lead relayed planner-parity's objection. I re-verified all
    three points myself at origin/main `2f24fcba`. The earlier sentence was wrong.*
  - The third member is **`admin:break_glass`**. It has no `requires()` route. It is checked
    only in the service layer, by `await require_permission(` at
    `backend/src/app/platform/rbac.py:420`, with `permission=Permission.ADMIN_BREAK_GLASS` at
    `:424`.
  - The `service_accounts.py:44` literal is
    `ALLOWED_PERMISSIONS = frozenset({"score:execute", "score:batch"})`. Both of those names
    have `requires()` sites: `backend/src/app/api/score.py:124` (`SCORE_EXECUTE`) and `:125`
    (`SCORE_BATCH`). So the literal leaves no member unchecked.
  - The ruling should say whether a service-layer `require_permission(` site counts as a check
    site. If it does not, `admin:break_glass` needs an owner cell.
  - This record's evidence item 5 ("2 enum members have 0 check sites") used `RL-1236`'s
    `Perm`/`Permission` caller predicate. That predicate matches `rbac.py:424`, so the item
    stands as measured. The difference between 2 and 3 is exactly this counting question.

## D2: where the check runs

| | Option | For | Against |
|---|---|---|---|
| (i) | An `audit-docs.py` numbered check only | Beside the other docs checks | **Does not run on a `packages/**`-only commit** (evidence 6) |
| (ii) | A pytest test under `tests/` or `packages/model-schema/tests/`, run by `python.yml` | `python.yml` triggers on `packages/**`, `backend/**` and `docs/**`, so every side of the comparison triggers it. It can import `model_schema.Permission` directly instead of regex-scanning the enum. | Not in `audit-docs`' numbered list |
| (iii) | (i), with `packages/model-schema/src/model_schema/permissions.py` added to `docs.yml`'s paths | Keeps it an audit check | Widens a path filter by hand. `backend/src/**` route checks (D1 (C)) would need adding too, and each addition is a place for the filter to drift. |

**Prepared recommendation (superseded by "Ruled"): (ii).**
- It is the only placement where every changed side of the comparison triggers the run.
- Importing the enum removes one of the three regexes.
- It must be proved red on a broken input: a fixture enum member with no Built row, and a
  Built row with no member (CLAUDE.md §13).

## D3: RL or ADR

| | Option | For | Against |
|---|---|---|---|
| (a) | An `RL-` (this record, ruled) | The architectural decision is already ADR-704's, and CLAUDE.md §2 already states it. What is new is a check and a `06` layout: cheap to reverse, the kind a ruling holds. The decision-maker's to rule (`CR-1247` `:150-151`, "`RL-`, or an ADR if the lead judges it cross-module"). | It constrains every future permission, which is `adr-write`'s "constrains more than one module" |
| (b) | A new ADR | Matches `adr-write`'s first criterion literally | An ADR goes `draft → active` only on the maintainer's acceptance (`document-ids.md:156`). That is a further gate before WK-1178 can build, and WK-690 Slice 3 waits on it. It would also restate ADR-704. |
| (c) | (a), plus a dated annotation on ADR-704 naming the permission vocabulary as a covered shape | The ADR record shows the application, and the ruling carries the mechanics | An addendum on an accepted ADR is the maintainer's to accept (`adr-write`, "When research confirms or complicates an accepted ADR") |

**Prepared recommendation (superseded by "Ruled"): (a).** The constraint on every future permission comes from ADR-704 and
CLAUDE.md §2, which already bind every module. The ruling records how that constraint is
checked for one shape. (c)'s annotation is worth proposing, but it should not gate WK-1178.
The lead's judgement under `CR-1247` `:150-151` decides between (a) and (b).

## D4: the `06` amendment's content (under D1 (C))

In one commit, with the check, or in the commit before it:
1. **§4.1 Built table**, containing:
   - the 13 existing rows;
   - the 11 missing members (evidence 2), each with its "governs" text taken from the prose
     that describes it today, and that prose's citation;
   - a lead sentence that the names are `model_schema.Permission`'s, and that this table
     states their meaning.
2. **§4.1 Specified, not built**: `RL-1236` rows 5–10, each with its owner Work (WK-690,
   WK-687, WK-688, WK-684, WK-686, per `RL-1236` `:404`).
   - `custom_objective:author` sits here until WK-690 Slice 3's commit moves it to Built.
3. **§4.1 Aliases**: `RL-1236`'s map rows (rows 1 and 11–17), `06`-era name → enum name,
   replacing the blockquote alias notes.
4. **Role block** (`06:190-205`): the JSON example's `permissions` list is replaced by a
   reference to `BUILTIN_ROLES` (the lead's verdict, `CR-1247` `:158`).
   - The example keeps its shape, with a placeholder, or with a subset that is valid by
     construction.
   - The 12 non-member names leave the page.
5. **FR-367** (`06:148`) is unchanged. It already requires the one-commit landing.

*Context, not a decision (added 2026-09-30):* PL-1268's acceptance places the `06` §4.1 row for
`custom_objective:author` in WK-690 Slice 3's own commit
(PL-1268 §Tasks, "Slice 3 — The `expression` kind through the platform, behind the flag": "the `06` §4.1
row for `custom_objective:author`, the enum member … and the route check land in **one
commit**"). That is consistent with item 2's "moves to Built in Slice 3's commit".

## Ruled

### Presence and absence, as verified at `48792023`

| Claim | Verdict | How it was verified |
|---|---|---|
| The enum | **present, 24 members** | `class Permission` (`packages/model-schema/src/model_schema/permissions.py:28`), read, with the members grouped by spec (`:35-71`). `BUILTIN_ROLES` is at `:131`. The regex of evidence 1 reproduces 24. |
| `06` §4.1's rows | **13, and 11 members without one** | `06-governance.md:188-303`, read in full. The predicate of evidence 2 reproduces 13 rows, all of them members. The 11 members without a row are `admin:manage_roles`, `approval:decide`, `dataset:acknowledge_warning`, `dataset:read`, `dataset:write`, `deployment:promote`, `model:fit`, `model:read`, `model:submit`, `rating:submit` and `rating:write`. |
| Non-member tokens in `06`, outside struck text | **14** | This is PL-1279 Task 1's own predicate (`_TOKEN` less `_NOT_A_PERMISSION`, over `06` with `~~…~~` removed): `alert:acknowledge`, `alert:resolve`, `banding:write`, `custom_objective:author`, `custom_objective:submit`, `dataset:create_version`, `factor:write`, `grouping:write`, `monitor:write`, `optimisation:materialise`, `optimisation:run`, `rate_table:write`, `rating_algorithm:write` and `rating_version:submit`. Evidence 3's "17" used `RL-1236`'s whole-`06` predicate, which also counts struck text. |
| Check sites | **2 members have none; 1 is checked only in the service layer** | Per member, the lines of `git grep -n -E "(Perm\|Permission)\.<NAME>\b" 48792023 -- backend/src` that are not comments, split into `requires(` sites and `permission=` sites. `deployment:promote` and `admin:manage_environments` have neither. `admin:break_glass` has one `permission=` site, `backend/src/app/platform/rbac.py:424`, inside `await require_permission(` (`:420`), and no `requires(` site. Every other member has a `requires(` site. |
| A live enumeration of route permissions | **present** | `requires()` tags each dependency with `PERMISSION_ATTRIBUTE` (`backend/src/app/api/authz.py:41`, `:76`). `backend/tests/test_api_authorisation_sweep.py:186-197` already reads it off the app's routes. |
| The CI triggers | **present** | `python.yml`'s `paths` include `packages/**`, `backend/**`, `docs/**` and `tests/**` (`:6-34`). `pyproject.toml`'s `testpaths` include `tests` (`:161-169`). `docs.yml`'s `paths` exclude `packages/**` and `backend/**` (`:14-17`). |
| PL-1279's parser | **present** | `PL-1279` (on `main`, `status: draft`) §Tasks, Task 1: the headers `\| Permission \| Governs \| Check owner \|`, `\| Permission \| Owner Work \|` and `\| Name used before \| Enum name \|`; the whole-`06` stray scan; and Task 3's check-site scan, which counts **any** `Perm.X` or `Permission.X` reference in `backend/src`. |

### D1 — option (C): table-driven, with a route leg on a check-site predicate that reads checks, not references

1. **The catalogue legs, (B).** `06` §4.1 carries three machine-read tables, with PL-1279
   Task 1's exact headers. The legs:
   - **Built** (`| Permission | Governs | Check owner |`) equals the enum in both directions;
   - **Specified** (`| Permission | Owner Work |`) is disjoint from the enum, and each owner
     is a `WK-` heading in `docs/roadmap.md`;
   - every **Alias** (`| Name used before | Enum name |`) targets a member;
   - every other `name:name` token in `06`, outside struck text, is in one of the three
     tables.

   The exclusions are declared data, never layout.
2. **The route leg, (C), on a stricter predicate than PL-1279 Task 3's.** A Built name has a
   **check site**, or else its `Check owner` cell names the Work that builds it. **A check
   site is a check, not a reference:**
   - a route dependency built by `requires(<member>)`, read off the live app's routes
     through `PERMISSION_ATTRIBUTE`, as `test_api_authorisation_sweep.py:186-197` already
     does; or
   - the `permission=` argument of a `require_permission(` call in `backend/src`, found by an
     AST walk that resolves the enum's name through the module's imports.

   A bare `Perm.X` or `Permission.X` reference elsewhere is **not** a check site. Examples are
   a role list, an allow-list, or a comparison. PL-1279 Task 3's text-regex scan counts every
   reference, a proxy that would pass a member that is named but never checked. Its alias
   guard existed to patch the regex; under the AST walk the import resolution does that job.
   Today the two predicates agree on every member (the table above). The difference is
   latent, and it is exactly the case the leg exists for.
3. **A service-layer check counts.** `require_permission(` is the check, and `requires()` is
   one caller of it (`authz.py:62-72`). So `admin:break_glass`, checked at `rbac.py:420-424`,
   has a check site and needs no owner cell.
4. **`STALE_OWNER` is adopted, as the ninth class.** A Built row with a check site and a
   non-empty `Check owner` fails. An owner cell cannot outlive the work it names (RFC-756).
   **WK-674 Slice 2** clears the owner cells of `deployment:promote` and
   `admin:manage_environments` **in the commit that adds their checks**. PL-1237 Task 2
   builds both (`PL-1237:481-484`), and that commit touches `06` §4.1 for it. The lead tells
   WK-674 Slice 2's leaf plan now, so the requirement is not first met as a red gate.
5. **The four prepared fixtures stand, and `STALE_OWNER` is the fifth.** Each is shown red on
   a synthetic `06` and enum (the Acceptance below).

### D2 — option (ii): a pytest module under root `tests/`, run by `python.yml`

It is the only placement where a change on **any** side triggers the run: `packages/**` (the
enum), `backend/**` (the checks), `docs/**` (`06`) and `tests/**` all trigger `python.yml`.
`docs.yml` does not trigger on `packages/**` or `backend/**`, so an `audit-docs.py` check (i)
would pass a `permissions.py`-only commit by not running (`CLAUDE.md` §2). The module imports
`model_schema.Permission` rather than regex-reading the enum. It lives in root `tests/`, as
PL-1279 plans (`testpaths`, the table above), and imports the app for the route leg, as
`backend/tests` already does. It edits no shared script, so it serialises with nothing
under `RL-1263`.

### D3 — option (a): this ruling, not a new ADR

The architectural decision is ADR-704's: `model-schema` holds every shared shape. `CLAUDE.md`
§2 already binds it to every module. This record decides only how that is checked for one
shape, and how `06` is laid out for the check. Both are cheap to reverse, which is a
ruling's kind. A new ADR would restate ADR-704, and it would gate WK-1178 on a further
maintainer acceptance (`document-ids.md` §1.6, the ADR row). **Proposed, not gating:** a dated
addendum on ADR-704 naming the permission vocabulary as a covered shape, for the maintainer
to accept or decline (`adr-write`). `CR-1247` `:150-151` left RL or ADR to the lead's
judgement. This ruling takes the RL form, and the lead may still ask for the ADR.

### D4 — the `06` §4.1 amendment, written in this commit

In one commit with this ruling, so WK-1178's slice only reads `06`, as PL-1279 DP-3 (a)
recommends:
1. **The role block's list is replaced by a reference to `BUILTIN_ROLES`** (`CR-1247` `:158`).
   A dated note says why. The twelve names the platform never defined leave the example, and
   their successors are in the tables.
2. **Built:** 24 rows, one per member.
   - The 13 existing rows are kept.
   - The 11 missing rows are added, each with its governing text and that text's source in
     `06`: §2's Permission term, §3.3, FR-348, FR-366 and FR-367, `RL-1232` DP-6, and the
     `RL-1236` notes.
   - `dataset:read` had no `06` text at all. Its row says so, and states what its read routes
     check.
   - **Check owner:** `WK-674` on `deployment:promote` and `admin:manage_environments`. It
     is empty elsewhere, including on `admin:break_glass` (D1 item 3).
3. **Specified:** `RL-1236` rows 5 to 10, as a table with owner Works: `custom_objective:author`
   WK-690, `monitor:write` WK-687, `alert:acknowledge` and `alert:resolve` WK-688,
   `optimisation:run` WK-684, `optimisation:materialise` WK-686.
   `custom_objective:author` moves to Built in WK-690 Slice 3's commit (PL-1268 §Tasks,
   Slice 3).
4. **Aliases:** the eight names used before: `rating_version:submit` → `rating:submit`;
   `custom_objective:submit` → `model:submit`; `rating_algorithm:write` and `rate_table:write`
   → `rating:write`; `factor:write`, `banding:write` and `grouping:write` → `model:fit`;
   `dataset:create_version` → `dataset:write`. The prose notes stay as the dated record of
   the decisions. The table is what the check reads.
5. **FR-367 is unchanged.** It already requires the one-commit landing.

**Proved against the planned parser.** PL-1279 Task 1's `extract_catalogue`, as the plan
writes it, was run over this commit's `06`:
- Built has 24 rows, equal to the enum's 24 in both directions;
- Specified ∩ enum is empty;
- every alias target is a member;
- stray tokens: none;
- duplicates: none;
- owners: `WK-674` twice, and WK-690, WK-687, WK-688 (twice), WK-684 and WK-686, each a
  `WK-` heading in `docs/roadmap.md`.

`RL-1236`'s interim rule (`RL-1236` Acceptance, `:409-417`) retires when WK-1178's check
merges.

## What it obliges

- **This commit:** this record, and the `06` §4.1 amendment (D4).
- **WK-1178 (PL-1279, the planner's file, not edited here):**
  - DP-1 to DP-3 are resolved by this record once it is minted: DP-1 (C) with `STALE_OWNER`,
    DP-2 L2, and DP-3 (a), done here;
  - **Task 3 changes:** the check-site predicate of D1 item 2 replaces the text-regex scan,
    and the alias guard is no longer needed.
- **WK-674 Slice 2:** D1 item 4. It clears the two owner cells in the commit that adds their
  checks.
- **WK-690 Slice 3:** moves `custom_objective:author` from Specified to Built in the commit
  that adds the member and its `requires()` site.
- **The lead:** tells WK-674 Slice 2's leaf plan about D1 item 4. The ADR-704 addendum is the
  maintainer's to take up or not.

## Acceptance — the violation that must become detectable

Each is shown red on broken input, as `CLAUDE.md` §13 requires, using a fixture spec and a fixture
enum in WK-1178's slice, and the
live tree passes:
- an enum member with no Built row;
- a Built row with no enum member;
- a Specified name that is also an enum member;
- a Built name with no check site and no owner cell;
- a Built name with a check site **and** an owner cell (`STALE_OWNER`);
- **a member referenced in `backend/src` but never checked**, for example listed in a role
  set with no `requires(` and no `require_permission(` for it, still counts as having **no**
  check site. With the text-regex predicate, it passes, and the test fails;
- a member checked only by a service-layer `require_permission(..., permission=…)` counts as
  checked;
- a stray non-member token in `06` outside struck text, and outside the tables.

A commit touching only `packages/model-schema/src/model_schema/permissions.py` triggers
`python.yml`, and so the test. This is shown by the workflow's `paths` (the table above) and
observed on the slice's first such push.
