---
id: RL-9856
family: ruling
title: PREPARED, NOT RULED — CR-1247 Proposal 1 (c), the permission-parity check and the `06` §4.1 amendment
status: draft                  # PREPARED, NOT RULED — kept draft by the maintainer's ruling (check-33 red is the fail-safe)
created: 2026-09-30
owner: decision-maker
tree: dee49f781fd23f9df2e72161885c77fa17a6f1ab
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [CR-1247, RL-1236, PL-1268, ADR-704, FR-367]
---

# RL-9856 (working id) — PREPARED, NOT RULED: CR-1247 Proposal 1 (c), the permission-parity check

> **Nothing in this record is ruled.** It was prepared at medium effort, under the
> maintainer's decision by delegation. It carries evidence, options and **provisional**
> recommendations only. Do not rely on it.
> - No slice may activate on it: WK-690 Slice 3 stays blocked on the parity check and its RL.
> - WK-1178 builds nothing on it.
> - `06` is not amended by it.
>
> It is never marked ready or minted before the effort-high pass.

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
  `custom_objective:author` (`RL-1236` row 5; PL-1268 Slice 3 "Depends on", `:498-499` and
  `:574-575`).
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

**Provisional: (C).**
- (B) is the part that makes the check trustworthy.
- The route leg is what makes "the enum member and its check land together" (FR-367;
  PL-1268 Slice 3) a gate rather than a review item. That is the case this check is being
  built for.
- The route leg's owner cell keeps the two current gaps honest instead of red.
- **Fallback:** (B), with the route leg left to each slice's own negative test (as PL-1268
  acceptance item 8 already does for `custom_objective:author`), if the high pass judges the
  regex route leg too fragile.

## D2: where the check runs

| | Option | For | Against |
|---|---|---|---|
| (i) | An `audit-docs.py` numbered check only | Beside the other docs checks | **Does not run on a `packages/**`-only commit** (evidence 6) |
| (ii) | A pytest test under `tests/` or `packages/model-schema/tests/`, run by `python.yml` | `python.yml` triggers on `packages/**`, `backend/**` and `docs/**`, so every side of the comparison triggers it. It can import `model_schema.Permission` directly instead of regex-scanning the enum. | Not in `audit-docs`' numbered list |
| (iii) | (i), with `packages/model-schema/src/model_schema/permissions.py` added to `docs.yml`'s paths | Keeps it an audit check | Widens a path filter by hand. `backend/src/**` route checks (D1 (C)) would need adding too, and each addition is a place for the filter to drift. |

**Provisional: (ii).**
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

**Provisional: (a).** The constraint on every future permission comes from ADR-704 and
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

## Ruled

**Nothing.** This section is held for the high-effort pass.

## What it obliges

**Nothing yet.** Under the provisional answers:
- **WK-1178** builds the pytest parity check (D2 (ii)) with red-on-broken proofs.
- **The decision-maker** writes the D4 amendment in the same PR as the ruling, or in the one
  before the check.
- **WK-690 Slice 3's commit** moves `custom_objective:author` from Specified to Built, adds
  the enum member and adds its `requires()` site.
- `RL-1236`'s interim rule retires when the check merges.

## Acceptance — the violation that must become detectable

**Not set, because nothing is ruled.** Under D1 (C) and D2 (ii), four broken fixtures must
each fail the test:
- an enum member with no Built row;
- a Built row with no enum member;
- a Specified name that is also an enum member;
- a Built name with no check site and no owner cell.

A commit touching only `permissions.py` must trigger the job that runs it.
