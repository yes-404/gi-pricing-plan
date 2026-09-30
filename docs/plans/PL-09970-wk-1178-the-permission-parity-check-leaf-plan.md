---
id: PL-9970
family: plan
kind: leaf
title: WK-1178 — The permission-parity check (CR-1247 Proposal 1 (c)): leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: dee49f781fd23f9df2e72161885c77fa17a6f1ab
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [CR-1247, RL-1236, RL-1263, PL-1268, PL-1237, ADR-704]
---

# PL-9970 (working id) — WK-1178: the permission-parity check, leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker and
> broken-input proofs), `test-driven-development` (every test is seen red before the code
> that turns it green), `dev-commands` (the two-half gate) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step.

## Goal

One test module that fails the gate when the permission names in
[`06-governance.md`](../specs/06-governance.md) §4.1 and `model_schema.Permission` disagree.
Under the ruling's option for a route leg, it also fails when an enum member has no check
site in `backend/src` and no owner. This is the check `CR-1247` Proposal 1 (c) requires before
WK-690 Slice 3 adds `custom_objective:author`.

**Architecture:** This is a pytest invariant, not a production module. It imports the enum
directly, parses `06` §4.1's catalogue tables, and compares the two lists. Every comparison is
a pure function over text and sets, so each violation class is proved red on a synthetic broken
input and the live tree is then asserted clean. No `backend/src` or `packages/*/src` file
changes.

**Tech Stack:** Python 3.12, pytest, `re`, `pathlib`, `model_schema.Permission`.

**Spec:** [`06-governance.md`](../specs/06-governance.md) §3.1 and §4.1;
`docs/closures/CR-01247-plan-review-16-at-wk-672-s-close-the-permission-source-of-record-f35-s-owner-the-dedicated-host-and-p2-s-exit.md`
Proposal 1 (c) (`:130-159`);
`docs/rulings/RL-01236-the-permission-catalogue-a-verdict-for-each-of-the-34-names-06-and-the-code-do-not-share.md`
§"Acceptance — the violation that must become detectable" (`:409-415`); and the P1 (c) ruling
prepared on PR #942 (working id 9856, head `4daa57cb`, **not ruled**). That ruling decides
DP-1 to DP-3 below.

## Status

`draft`. Blocking decision points DP-1, DP-2 and DP-3 are open (§"Decision points"). They are
resolved by the decision-maker's P1 (c) ruling, which is prepared on #942 and not ruled at
`dee49f78`. **This plan decides none of them.** Tasks 1 to 4 are written against #942's
provisional answers: D1 (C), D2 (ii) and the D4 table layout. Task 0 re-reads the ruling as
merged. Where it differs, the plan is revised before `active`, not patched by the executor.

**SL.** WK-1178 is standing maintenance. Its slices are minted by the lead at triage
([`document-ids.md`](../process/document-ids.md) §1.9, `:214`), not cut by a map plan. The
proposed row text is in §"Proposed SL row". It is not added by this PR.

## Acceptance Standard

Each item is checkable by a command run from the repository root on the merge tree.

1. `uv run pytest -q tests/test_permission_parity.py` exits 0. It collects 13 tests: Task 1's
   clean control and nine broken-input cases, Task 2's live test, Task 3's alias guard and
   Task 4's trigger test.
   - That count assumes the ruling adopts the stale-owner class. If 9856 omits it, it is 12.
   - Under DP-1 (B) there is no alias guard. The count is then 12 with stale-owner, or 11
     without it.
2. **Each violation class is proved red on a broken input.** There are nine classes, or eight
   if the ruling does not adopt stale-owner (Task 0 Step 1). Every
   `test_broken_*` case asserts two things:
   - `parity_violations` returns exactly the messages the case names;
   - each message begins with its class's own prefix constant (Task 1).

   A case that returns the right count with another class's prefix fails. Seven cases name
   one class and two cases name two (Task 1, Step 1). Without stale-owner, six cases name one
   class. The no-check and stale-owner classes are the route leg's and fire on the live tree
   only under DP-1 (C).
3. **The live tree is clean.** `test_live_tree_has_no_parity_violations` passes against the
   real `06` and the real `model_schema.Permission`. This happens only after the `06`
   amendment (DP-3) has merged.
4. **The live test is red on a real broken tree** (`CLAUDE.md` §13). Delete one row from
   `06` §4.1's Built table in the working tree and run item 1: the live test fails, naming that
   member with the enum-without-row prefix. Restore with `git checkout -- docs/specs/06-governance.md`.
   Record the printed failure line in the ledger.
5. **The alias guard holds.** `test_every_permission_import_alias_is_scanned` passes. With
   `from model_schema import Permission as P` added to any `backend/src` module in the working tree,
   it fails, naming that file. Record the failure and revert.
6. **Every side of the comparison triggers the test in CI.** `test_python_workflow_triggers_on_every_parity_input`
   passes: for both `push` and `pull_request`, `.github/workflows/python.yml`'s `paths` include
   `packages/**`, `backend/**` and `docs/**`.
7. The full two-half gate of `CLAUDE.md` §11 exits 0 on the merge tree, with each command's rc
   recorded. That is `uv run ruff check .`, `uv run mypy`, `uv run lint-imports`,
   `uv run pytest -q`, `python3 scripts/audit-docs.py`, `uv run python scripts/req-coverage.py`,
   `uv run python scripts/generate-contracts.py --check`, and the five `pnpm --dir frontend`
   commands.
8. `git diff --stat origin/main...HEAD` names no file under `backend/src/`, `packages/*/src/`,
   `frontend/` or `docs/specs/`. The check changes no behaviour and no spec. Exception: if the
   lead routes the `06` amendment into this slice (DP-3 (b)), `docs/specs/06-governance.md`
   is added, and only that file.

## Global Constraints

- **No pandas** (`CLAUDE.md` §3). The test uses `re` and `pathlib` only.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2). The
  test imports `model_schema.Permission` and never lists the 24 names.
- **A new permission lands in one commit: the `06` row, the enum member and the route check**
  (`CR-1247` `:143-144`). The check makes this a gate, and its messages say so.
- **NFRs are measured, not asserted; enforcement is proven on deliberately broken input**
  (`CLAUDE.md` §13). See Acceptance items 2, 4 and 5.
- **Shared files** (`RL-1263`, option (c), `docs/rulings/RL-01263-parallel-start-preparation-in-parallel-at-most-two-build-slices-from-different-works-a-measurement-runs-alone.md:85-100`).
  Two concurrent build slices may not both change the same existing function, class, spec
  section or policy table. `docs/INDEX.md` is a registry file, regenerated and never
  hand-merged.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What the check holds | Marker |
|---|---|---|---|
| `06` §3.1 | FR-343 | Permissions are checked in the backend. The route leg (DP-1 (C)) asserts that every Built name has a check site or an owner | `req("FR-343")` on the route-leg tests |
| `06` §3.1 | FR-344 | Custom roles compose from "the same permission vocabulary". The vocabulary is the enum, and `06` §4.1 states its meaning | `req("FR-344")` on the two-list tests |
| `06` §3.3 | FR-367 | `custom_objective:author`: "the enum member and its check land together in WK-690". The check turns that into a gate: the name moves from Specified to Built in the commit that adds the member | `req("FR-367")` on the Specified-is-member test |

FR-342, FR-345, FR-346, FR-347, FR-348, FR-349 and FR-350 (`06` §3.1) are **not** covered. They
govern identity, scope, the Auditor, Service Accounts, role administration, break-glass and IdP
mapping, and none of them is about which names exist.

### Today's mismatches — the check's first findings, measured at `dee49f78`

Every count names its corpus and its predicate. Each was run from the repository root of a
checkout at `dee49f781fd23f9df2e72161885c77fa17a6f1ab`.

**E1. The enum has 24 members.**
`grep -oE '= "[a-z_]+:[a-z_]+"' packages/model-schema/src/model_schema/permissions.py | tr -d '=" ' | sort -u`
gives 24. This is `RL-1236`'s code-side predicate.

**E2. The whole of `06` names 41 distinct tokens. All 24 enum members are among them, and 17 are not members.**
`grep -oE "\b[a-z][a-z_]*:([a-z_]+\b|deploy_\*)" docs/specs/06-governance.md | grep -vE ":motor$|^type:name$" | sort -u`
gives 41. This is `RL-1236`'s `06`-side predicate. `comm -23` against E1 gives these 17:
`alert:acknowledge`, `alert:resolve`, `banding:write`, `custom_objective:author`,
`custom_objective:submit`, `dataset:create_version`, `factor:write`, `grouping:write`,
`model:approve`, `monitor:write`, `optimisation:materialise`, `optimisation:run`,
`rate_table:write`, `rating_algorithm:write`, `rating_version:deploy_*`,
`rating_version:deploy_prod` and `rating_version:submit`. `comm -13` is empty.

**E3. `06` → enum, after `CR-1247`'s exclusions: 7 today, and 0 once the role block goes.**
The exclusions are read as follows: drop `~~…~~` spans; drop the `>`-quoted lines of §4.1
(`:188-304`, the superseded note and the alias notes); drop `RL-1236` rows 5–10. Then:
- With the Pricing Actuary JSON role block (`06:190-205`) still present, 7 tokens remain:
  `banding:write`, `dataset:create_version`, `factor:write`, `grouping:write`,
  `rate_table:write`, `rating_algorithm:write` and `rating_version:submit`. These are
  `RL-1236`'s DP-A and row-1 maps, which survive only inside the example.
- With that JSON block also dropped, 0 remain. `CR-1247`'s verdict (`:158`) replaces the block
  with a reference to `BUILTIN_ROLES`.
- Predicate (I1):
  `awk 'NR<188||NR>304||!/^>/' docs/specs/06-governance.md | sed -E 's/~~[^~]*~~//g' | grep -oE "\b[a-z][a-z_]*:([a-z_]+\b|deploy_\*)" | grep -vE ":motor$|^type:name$" | sort -u`,
  then `comm -23` against E1 and against the six row 5–10 names.

**E4. Enum → `06` §4.1: 11 today under the table reading, and 1 under the any-mention reading.**
- **Table reading:** 11 enum members have no row in `06` §4.1's catalogue table. They are
  `admin:manage_roles`, `approval:decide`, `dataset:acknowledge_warning`, `dataset:read`,
  `dataset:write`, `deployment:promote`, `model:fit`, `model:read`, `model:submit`,
  `rating:submit` and `rating:write`.
  - Predicate: `sed -n '188,304p' docs/specs/06-governance.md | grep -oE '^> \| `[a-z_]+:[a-z_]+`' | grep -oE '[a-z_]+:[a-z_]+' | sort -u`
    gives 13 table rows. `comm -23` of E1 against it gives the 11.
- **Any-mention reading:** 1 member is not mentioned anywhere in §4.1: `admin:manage_roles`.
  It is named only by FR-348 (`:84`) and FR-360.
- Two more members, `dataset:read` and `dataset:acknowledge_warning`, appear in §4.1 **only**
  inside the JSON role block. So the any-mention count becomes 3 once the block is replaced.
- **So `CR-1247`'s "an enum member has no `06` §4.1 row" is red at this tree** under either
  reading. The check cannot merge green until `06` §4.1 gains those rows (DP-3).

**E5. Route side: 2 enum members have no check site, or 3 if only `requires()` routes count.**
- **Alias-aware caller predicate** (`RL-1236` `:79-87`, run once per member NAME):
  `git grep -n -E "(Perm|Permission)\.<NAME>\b" -- backend/src | grep -v '#'`.
  - It gives 0 sites for `deployment:promote` and `admin:manage_environments`. Both are owned
    by WK-674 Slice 2 (`RL-1236` rows 24 and 34).
  - It gives at least 1 site for each of the other 22.
- **Route-only predicate:** `git grep -n -E "requires\((Perm|Permission)\.<NAME>\b" -- backend/src/app/api`.
  - It gives 0 sites for those two and also for `admin:break_glass`. That member is checked
    only in the service layer (`backend/src/app/platform/rbac.py:420`, FR-349).
- **So a route leg built by introspecting routes misses service-level checks.**
  - `git grep -n -E '(require|has)_permission\(' -- backend/src | grep -v 'def '` lists 50 lines.
    One is `requires()` itself (`backend/src/app/api/authz.py:63`); the other 49 are
    service-level call lines, 3 of them inside `rbac.py`.
  - Task 3 therefore scans source, not routes.
- **Other literals.** `git grep -n 'requires(' -- backend/src/app/api | wc -l` prints **54**.
  - 52 of those lines are call sites, `requires(Perm.…)` or `requires(Permission.…)`
    (`git grep -n -E 'requires\((Perm|Permission)\.' -- backend/src/app/api | wc -l`).
  - The other 2 lines are not checks: a comment at `authz.py:33` and the definition
    `def requires(` at `authz.py:54`.
  - *(Corrected 2026-09-30 on auditor-plans2's F1: this bullet first said "53", a total that
    had silently excluded the definition line.)*
  - `requires` takes a `Permission` (`authz.py:54`), so mypy already stops a route from
    naming a non-member.
  - The only permission-string literal outside the enum is
    `backend/src/app/api/service_accounts.py:44` (`ALLOWED_PERMISSIONS`). Both of its strings
    are members.

**E6. CI triggers.**
- `.github/workflows/python.yml` lists `packages/**`, `backend/**` and `docs/**` under both
  `push` and `pull_request`. The `docs/**` entry and its reason are at `:23-31`.
- `.github/workflows/docs.yml:16,18` lists `docs/**` and the doc scripts. It does **not** list
  `packages/**` or `backend/**`.
- **Correction, disclosed:** a first read of this plan's own sweep took only `python.yml:6-20`,
  and on that read it concluded that `python.yml` does not trigger on `docs/**`. That was
  false. #942's evidence 6 is right.

### Decision points

**The gating ruling is working id 9856**: the decision-maker's P1 (c) record, prepared on #942
at head `4daa57cb` and **not ruled**. Its D1, D2 and D4 are this plan's DP-1, DP-2 and DP-3.
This plan does not restate 9856's analysis. Its option letters (A), (B) and (C) and its
D2 (i)–(iii) are used by reference. E1–E6 above are this plan's own re-measurement at the
same tree:
- They agree with 9856's evidence items 1, 2, 5 and 6.
- They add two things. One is E5's route-only count of 3, which shows why the route leg must
  scan source rather than routes. The other is E3's split of the 17 non-member tokens by the
  exclusion that removes each one.


| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | **What the check asserts.** | (A) `CR-1247`'s wording, with exclusions found by position in prose (E3's I1 reading). (B) Table-driven: §4.1 carries Built, Specified-not-built and Aliases tables, each machine-read, and any other `06` token outside struck text is a violation. (C) (B), plus a route leg: every Built name has a check site in `backend/src` or an owner cell (E5) | **(C)**, agreeing with 9856's provisional answer. Only (C) makes FR-367's "the enum member and its check land together" a gate rather than a review item, and E5 shows its route leg is red today only on two members that already have an owner. **The ruling decides it**, and Tasks 1–4 are written to (C). A proposal for the ruling, not part of 9856's four fixtures: a ninth class, stale-owner, for a Built row with both a check site and an owner. Under it, WK-674 Slice 2 clears the owner cells of `deployment:promote` and `admin:manage_environments` in the commit that adds their checks. It is conditional on the ruling adopting it (Task 0 Step 1) | decision point (scope) | yes: Tasks 1–3 | working id 9856 (#942), its D1 |
| DP-2 | **Where the check lives.** | (L1) A numbered `scripts/audit-docs.py` check. It regex-reads `permissions.py` and runs under `docs.yml`. (L2) A root `tests/` pytest module that imports the enum and runs under `python.yml`. (L3) Both: the `audit-docs` check for the `06`-internal legs, and the pytest for every leg touching code. (L4) L1, with `packages/model-schema/src/model_schema/permissions.py` and `backend/src/**` added to `docs.yml`'s paths | **L2.** It is the only placement where a change on any side triggers the run (E6). L1 does not run on a `packages/**`-only commit, which is the very drift the check exists for. L4 keeps a hand-widened path filter that drifts. L3 runs the same comparison twice, and one copy can go stale. L1, L3 and L4 also edit `scripts/audit-docs.py`, which WK-1170 Slices 3 and 6 edit (the WK-1170 map plan on open PR #930, working id 9811, `:271-296`). That is a shared file under `RL-1263` (c), so they serialise, and the next free check number becomes a merge race. L2 edits no shared file | decision point (placement) | yes: every task's **Files** | working id 9856 (#942), its D2 |
| DP-3 | **Who writes the `06` §4.1 amendment, and when** (the 11 rows of E4, the Specified and Aliases tables, and the role block replaced by a reference to `BUILTIN_ROLES`)? | (a) The decision-maker, in the ruling's PR or one before it. This slice then only reads `06`. (b) This slice, in its first commit, from the ruling's text. (c) The ruling's PR carries the tables, and this slice carries only the role-block replacement | **(a)**, this plan's recommendation. `CR-1247` `:149-151` names the decision-maker as owner of only one part: the `06` amendment that replaces the role block with a reference to `BUILTIN_ROLES`. The 11 rows reach the decision-maker only through 9856's unruled D4 item 1. Under (a) this slice edits no spec section, so it shares nothing with WK-674 Slices 2/3 or WK-690 Slice 3 (all of which touch `06` §4.1). Under (b) it takes `06` §4.1 and serialises with all three | decision point (ownership, sequencing) | yes: Task 2's live test is red until it lands (E4) | working id 9856 (#942), its D4, and the lead's dispatch |

`CR-1247` `:150` also leaves **RL or ADR** open (working id 9856, D3). It does not block this plan unless
the answer is an ADR: an ADR goes `draft → active` only on the maintainer's acceptance, and
Task 0 then waits for that acceptance too.

### The slice under 9856 D1 (C), and under its fallback (B)

| | Under D1 (C), 9856's provisional | Under D1 (B), 9856's named fallback |
|---|---|---|
| Violation classes live on the real tree | nine, or eight if the ruling omits stale-owner | seven, or six without stale-owner. `NO_CHECK_NO_OWNER` and `STALE_OWNER` keep their synthetic red proofs but are dormant on the live tree, because `checked` is the whole enum |
| Task 3 (source scan, alias guard) | built | dropped. Task 2 passes `frozenset(p.value for p in Permission)` as `checked` |
| `06` §4.1 Built table | needs a `Check owner` column: `WK-674` on `deployment:promote` and `admin:manage_environments` (E5) | two columns, name and governs. Task 1 reads the owner column only when it is present (`len(r) > 2`), so a two-column table gives every Built name owner `None`. `STALE_OWNER`, if adopted, cannot fire, and `NO_CHECK_NO_OWNER` cannot fire because `checked` is the whole enum. `BUILT_HEADER` takes the two-column header at Task 0 Step 2, which is a header-literal change only |
| Tests collected (Acceptance item 1) | 13, or 12 without stale-owner | 12, or 11 without stale-owner |
| Where FR-367's "the member and its check land together" is enforced | this gate (the route leg) | each slice's own negative test (`PL-1268` Acceptance item 8), not this gate |
| Binds WK-674 S2 | only if the ruling adopts stale-owner: it then clears two owner cells in the commit that adds its checks | no |
| Size | about 250 lines | about 190 lines |

Any other D1 answer, including (A), is a replan before `active`. (A) identifies its exclusions
by their position in prose, and Task 1's parser has no such mode.

### Where the 11 missing rows land (E4)

- **Under DP-3 (a), which is recommended:** in the `06` amendment that 9856 carries (its D4
  item 1), merged before this slice is dispatched. The slice reads `06` and edits no spec
  section.
- **Under DP-3 (b):** as this slice's first commit, written from 9856's D4 text. The slice
  then takes `06` §4.1 and serialises with WK-674 S2/S3 and WK-690 S3 (the contention table
  below).
- **In both cases** the rows cannot land with the check alone. The live test is red until all
  24 members have a Built row, and a red test does not merge.
- **This plan's recommendation**, not an existing assignment: DP-3 (a) keeps the governing
  text for the 11 names with the record that rules on it. A slice that writes meaning into
  `06` §4.1 would be deciding that meaning.
  - `CR-1247` `:149-151` names the decision-maker as owner of the role-block replacement
    only (`BUILTIN_ROLES`).
  - The 11 rows are proposed for the decision-maker by 9856's D4 item 1, which is not ruled.
  - *(Reworded 2026-09-30 on auditor-plans2's citation finding. The first wording cited
    `CR-1247` as if it assigned the whole amendment.)*

### File contention (for the lead's serialisation under `RL-1263` option (c))

| Path | This slice | Other slices that edit it | Consequence |
|---|---|---|---|
| `tests/test_permission_parity.py` (new) | creates | none | none |
| `docs/specs/06-governance.md` §4.1 | reads only under DP-3 (a); edits under (b) | the decision-maker's amendment (DP-3); **WK-674 Slice 2** (`admin:manage_environments` and `deployment:promote` get their first check sites, `PL-1237` `:481-484`); **WK-674 Slice 3** (`admin:manage_service_accounts`, `score:execute` and `admin:manage_settings` rows, `PL-1237` `:485-487`); **WK-690 Slice 3** (`custom_objective:author`, `PL-1268` `:82-85`, `:479-486`) | Under (a): no file overlap, but an **order**. Once this lands, each of those three slices must satisfy it: WK-690 S3 moves the name from Specified to Built in the same commit as the enum member and route, and WK-674 S2 clears two owner cells. Under (b): serialise with all three |
| `packages/model-schema/src/model_schema/permissions.py` | reads (imports) | **WK-690 Slice 3** adds `CUSTOM_OBJECTIVE_AUTHOR`. WK-674 S2/S3 add no member (`PL-1237` table: every name they use is at `permissions.py:53-70`) | none. WK-690 S3 must come after this slice (`PL-1268` Slice 3, Depends on) |
| `scripts/audit-docs.py` | not touched under L2 | **WK-1170 Slices 3 and 6** (the WK-1170 map plan, PR #930, `:271-296`) | Under L1, L3 or L4: serialise with both, and re-take the next free check number at merge |
| `.github/workflows/docs.yml` | not touched under L2 | none planned | Under L4: a path-filter edit |
| `docs/INDEX.md` | regenerated if this PR adds a governed record | every PR | registry file: regenerate, never hand-merge |

**Behavioural dependency, not file contention:** WK-674 Slice 2 checks `deployment:promote`
(`PL-1237` table, Slice 2 rows). If it merges **before** this slice, the owner cells DP-3
writes must already reflect its check sites. Otherwise Task 3's stale-owner class, if the ruling
adopts it, goes red on the first run. Task 0 re-measures E5 for exactly this.

### Proposed SL row (the lead mints it; not added here)

````markdown
#### SL-<n> — WK-1178: the permission-parity check (CR-1247 Proposal 1 (c))

```yaml
id: SL-<n>
family: slice
title: "WK-1178: the permission-parity check (CR-1247 Proposal 1 (c))"
status: draft
created: <mint date>
owner: lead                      # standing maintenance: minted at triage (document-ids.md §1.9)
tree: <mint tree>
phase: P2
work: WK-1178
corrected_by: []
relates: [CR-1247, RL-1236, PL-<this plan's minted id>, RL-<the P1 (c) ruling>]
```

A pytest invariant fails the gate when `06` §4.1's permission tables and `model_schema.Permission`
disagree, or when a Built name has neither a check site nor an owner. It must merge before
WK-690 Slice 3's commit that adds `custom_objective:author` (`PL-1268` Slice 3, Depends on).
Leaf plan `PL-<id>`; decision points ruled by `RL-<id>`. It retires `RL-1236`'s interim
re-derive-at-each-close rule when it merges.
````

### Size

Small. One new test module of about 250 lines and no production code. There are four tasks
after preconditions. The work is about half a day for an executor, plus one full two-half gate
run (a gate slot under `RL-1263`). It takes no NFR measurement, so it need not run exclusive.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm the P1 (c) ruling has merged: `git grep -l "CR-1247" origin/main -- docs/rulings`
  names a record besides `RL-1252`. Read its D1, D2 and D3 answers. If D1 is not (C) or D2 is
  not L2, **stop**: the plan is revised before `active`. **Stale-owner:** if the ruling does
  not adopt it (it is not among 9856's four acceptance fixtures at `4daa57cb`), remove all of
  the following in the first commit:
  - `STALE_OWNER`;
  - its branch in `parity_violations`;
  - `test_broken_stale_owner_after_the_check_lands`.

  The counts are then 8 classes, and 12 tests under (C) (Acceptance items 1 and 2).
- [ ] **Step 2:** Confirm the `06` amendment has merged (DP-3 (a)). Copy the exact header rows
  of §4.1's Built, Specified and Aliases tables into Task 1's `BUILT_HEADER`, `SPECIFIED_HEADER`
  and `ALIAS_HEADER`. These are the only literals the amendment is allowed to change. The Built
  table may have two columns under D1 (B) or three under (C). The code reads the owner column
  only if it is present, so either shape is a header-literal change. Anything else, such as a
  different table set or a different column order, is a replan.
- [ ] **Step 3:** Re-run E1, E4 (table reading, against the new Built table) and E5 at the new
  tree. Record each count with its tree in the ledger. E4 must print nothing. E5's zero-site
  members must equal the Built rows that carry an owner.
- [ ] **Step 4:** `gh pr list --state open` for anything touching `06` §4.1 or `permissions.py`
  (WK-674 S2/S3, WK-690 S3). Name each one's head SHA in the ledger.

### Task 1: The pure comparison, and each violation class proved red

**Files:**
- Create: `tests/test_permission_parity.py`

**Interfaces:**
- Produces:
  - `parity_violations(spec_text: str, enum_values: frozenset[str], checked: frozenset[str], works: frozenset[str]) -> list[str]`.
  - The nine message-prefix constants below.
  - `extract_catalogue(spec_text: str) -> Catalogue`, where `Catalogue` is a frozen dataclass
    with these fields:
    - `built: dict[str, str | None]`: name → owner Work or `None`;
    - `specified: dict[str, str]`: name → owner Work;
    - `aliases: dict[str, str]`: `06`-era name → enum name;
    - `stray: frozenset[str]`: other tokens.

- [ ] **Step 1: Write the failing tests.** The header literals are #942 D4's layout. Task 0
  Step 2 replaces them with the merged amendment's.

```python
"""The permission-parity check: `06` §4.1 against `model_schema.Permission` (CR-1247 P1 (c)).

The names are the enum's (ADR-704, CLAUDE.md §2). `06` §4.1 states what each one means. A new
permission lands in one commit: the `06` row, the enum member and the check. Each class
below is proved red on a synthetic input before the live tree is asserted clean (CLAUDE.md §13).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "specs" / "06-governance.md"

BUILT_HEADER = "| Permission | Governs | Check owner |"
SPECIFIED_HEADER = "| Permission | Owner Work |"
ALIAS_HEADER = "| Name used before | Enum name |"

ENUM_WITHOUT_ROW = "enum member with no 06 §4.1 Built row"
ROW_WITHOUT_ENUM = "06 §4.1 Built row with no enum member"
SPECIFIED_IS_MEMBER = "Specified name is an enum member: move its row to Built in the same commit"
OWNER_UNRESOLVED = "owner is not a WK- heading in docs/roadmap.md"
ALIAS_TARGET_NOT_MEMBER = "alias target is not an enum member"
STRAY_TOKEN = "06 names a permission that is in no §4.1 table"
NO_CHECK_NO_OWNER = "Built name has no check site in backend/src and no owner"
STALE_OWNER = "Built name has a check site and still carries an owner: clear it in the same commit"
DUPLICATE_ROW = "name appears in more than one §4.1 table"

# RL-1236's whole-06 predicate, and its two exclusions.
_TOKEN = re.compile(r"\b[a-z][a-z_]*:(?:[a-z_]+\b|deploy_\*)")
_NOT_A_PERMISSION = re.compile(r":motor$|^type:name$")
_STRUCK = re.compile(r"~~.*?~~", re.DOTALL)
_ROW_NAME = re.compile(r"^`([a-z_]+:[a-z_*]+)`$")
_WORK = re.compile(r"\bWK-\d+\b")


def _section_4_1(text: str) -> str:
    start = text.index("\n### 4.1 ")
    return text[start : text.index("\n### 4.2 ", start)]


def _table(section: str, header: str) -> list[list[str]]:
    """Rows of the table whose header row is `header`, with any `> ` quote prefix removed."""
    lines = [line.removeprefix("> ").removeprefix(">").strip() for line in section.splitlines()]
    try:
        at = lines.index(header)
    except ValueError:
        return []
    rows: list[list[str]] = []
    for line in lines[at + 2 :]:  # skip the header and the |---| line
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def _name(cell: str) -> str:
    match = _ROW_NAME.match(cell)
    assert match, f"not a backticked permission name: {cell!r}"
    return match.group(1)


def _owner(cell: str) -> str | None:
    """The owning Work id in an owner cell ("WK-674 Slice 2" -> "WK-674"), else the raw text."""
    cell = cell.strip("`* ")
    match = _WORK.search(cell)
    return match.group(0) if match else (cell or None)


@dataclass(frozen=True)
class Catalogue:
    built: dict[str, str | None]
    specified: dict[str, str]
    aliases: dict[str, str]
    stray: frozenset[str]
    duplicates: frozenset[str]


def extract_catalogue(spec_text: str) -> Catalogue:
    section = _section_4_1(spec_text)
    # The owner column is optional: under 9856 D1 (B) the Built table has two columns.
    rows = _table(section, BUILT_HEADER)
    built = {_name(r[0]): _owner(r[2]) if len(r) > 2 else None for r in rows}
    specified = {_name(r[0]): _owner(r[1]) or "" for r in _table(section, SPECIFIED_HEADER)}
    aliases = {_name(r[0]): _name(r[1]) for r in _table(section, ALIAS_HEADER)}
    tables = [set(built), set(specified), set(aliases)]
    every = set(built) | set(specified) | set(aliases)
    duplicates = frozenset(n for n in every if sum(n in t for t in tables) > 1)
    tokens = {
        t for t in _TOKEN.findall(_STRUCK.sub("", spec_text)) if not _NOT_A_PERMISSION.search(t)
    }
    # An alias target that is not a member is reported once, by its own class, not as stray.
    stray = frozenset(tokens - every - set(aliases.values()))
    return Catalogue(built, specified, aliases, stray, duplicates)


def parity_violations(
    spec_text: str,
    enum_values: frozenset[str],
    checked: frozenset[str],
    works: frozenset[str],
) -> list[str]:
    cat = extract_catalogue(spec_text)
    out: list[str] = []
    out += [f"{ENUM_WITHOUT_ROW}: {n}" for n in sorted(enum_values - set(cat.built))]
    out += [f"{ROW_WITHOUT_ENUM}: {n}" for n in sorted(set(cat.built) - enum_values)]
    out += [f"{SPECIFIED_IS_MEMBER}: {n}" for n in sorted(set(cat.specified) & enum_values)]
    owners = {n: o for n, o in cat.built.items() if o} | cat.specified
    out += [
        f"{OWNER_UNRESOLVED}: {n} -> {o!r}" for n, o in sorted(owners.items()) if o not in works
    ]
    out += [
        f"{ALIAS_TARGET_NOT_MEMBER}: {a} -> {t}"
        for a, t in sorted(cat.aliases.items())
        if t not in enum_values
    ]
    out += [f"{STRAY_TOKEN}: {n}" for n in sorted(cat.stray)]
    out += [f"{DUPLICATE_ROW}: {n}" for n in sorted(cat.duplicates)]
    for name, owner in sorted(cat.built.items()):
        if name not in enum_values:
            continue
        if name not in checked and owner is None:
            out.append(f"{NO_CHECK_NO_OWNER}: {name}")
        if name in checked and owner is not None:
            out.append(f"{STALE_OWNER}: {name} ({owner})")
    return out


# --- synthetic inputs -------------------------------------------------------------------

_WORKS = frozenset({"WK-674", "WK-690"})


def _spec(built: str, specified: str = "", aliases: str = "", prose: str = "") -> str:
    return (
        "# 06\n\n" + prose + "\n\n### 4.1 `Permission`\n\n"
        f"{BUILT_HEADER}\n|---|---|---|\n{built}\n\n"
        f"{SPECIFIED_HEADER}\n|---|---|\n{specified}\n\n"
        f"{ALIAS_HEADER}\n|---|---|\n{aliases}\n\n"
        "### 4.2 `ApprovalPolicy`\n"
    )


_CLEAN = _spec(
    built="| `a:read` | Reading A |  |\n| `a:deploy` | Deploying A | WK-674 |",
    specified="| `a:author` | WK-690 |",
    aliases="| `a:ship` | `a:deploy` |",
    prose="Reading needs `a:read`; the old ~~`a:legacy`~~ name is struck.",
)
_ENUM = frozenset({"a:read", "a:deploy"})
_CHECKED = frozenset({"a:read"})


def _only(violations: list[str], *prefixes: str) -> None:
    """Exactly one message per named class, and no other: a right count with a wrong class fails."""
    assert len(violations) == len(prefixes), violations
    for prefix in prefixes:
        assert sum(v.startswith(prefix + ": ") for v in violations) == 1, (prefix, violations)


@pytest.mark.req("FR-344")
def test_clean_control_has_no_violations() -> None:
    assert parity_violations(_CLEAN, _ENUM, _CHECKED, _WORKS) == []


@pytest.mark.req("FR-344")
def test_broken_enum_member_without_a_row() -> None:
    _only(parity_violations(_CLEAN, _ENUM | {"a:write"}, _CHECKED, _WORKS), ENUM_WITHOUT_ROW)


@pytest.mark.req("FR-344")
def test_broken_row_without_an_enum_member() -> None:
    extra = "| `a:read` | Reading A |  |\n| `a:gone` | Gone | WK-674 |"
    spec = _CLEAN.replace("| `a:read` | Reading A |  |", extra)
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), ROW_WITHOUT_ENUM)


@pytest.mark.req("FR-367")
def test_broken_specified_name_that_is_already_a_member() -> None:
    # An enum member that is still Specified also has no Built row: both messages are right.
    violations = parity_violations(_CLEAN, _ENUM | {"a:author"}, _CHECKED, _WORKS)
    _only(violations, SPECIFIED_IS_MEMBER, ENUM_WITHOUT_ROW)


@pytest.mark.req("FR-344")
def test_broken_owner_that_is_not_a_work() -> None:
    spec = _CLEAN.replace("| `a:author` | WK-690 |", "| `a:author` | WK-9 |")
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), OWNER_UNRESOLVED)


@pytest.mark.req("FR-344")
def test_broken_alias_to_a_non_member() -> None:
    spec = _CLEAN.replace("| `a:ship` | `a:deploy` |", "| `a:ship` | `a:send` |")
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), ALIAS_TARGET_NOT_MEMBER)


@pytest.mark.req("FR-344")
def test_broken_stray_token_in_prose() -> None:
    spec = _CLEAN.replace("Reading needs `a:read`;", "Reading needs `a:read` or `a:peek`;")
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), STRAY_TOKEN)


@pytest.mark.req("FR-343")
def test_broken_built_name_with_no_check_and_no_owner() -> None:
    old, new = "| `a:deploy` | Deploying A | WK-674 |", "| `a:deploy` | Deploying A |  |"
    spec = _CLEAN.replace(old, new)
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), NO_CHECK_NO_OWNER)


@pytest.mark.req("FR-343")
def test_broken_stale_owner_after_the_check_lands() -> None:
    _only(parity_violations(_CLEAN, _ENUM, _CHECKED | {"a:deploy"}, _WORKS), STALE_OWNER)


@pytest.mark.req("FR-344")
def test_broken_name_in_two_tables() -> None:
    extra = "| `a:author` | WK-690 |\n| `a:read` | WK-690 |"
    spec = _CLEAN.replace("| `a:author` | WK-690 |", extra)
    # `a:read` is Built and Specified, so it is also a Specified enum member: both are right.
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), DUPLICATE_ROW, SPECIFIED_IS_MEMBER)
```

  Two cases expect two messages, and both are named. A Specified name that is an enum member
  has no Built row either, and a name in two tables is also Specified-and-member. The other
  seven `test_broken_*` cases each expect exactly one message, of a single class.

- [ ] **Step 2: Run them before the implementation exists.** Stub `parity_violations` to
  `return []`. Run `uv run pytest -q tests/test_permission_parity.py`.
  - Expected: every `test_broken_*` case fails, each on `_only`'s length assertion with `[]`
    printed. The clean control passes.
  - A broken case that fails for any other reason is a defect in the sample and is fixed
    before Step 3. An `IndexError` from `_table`, for example, means the synthetic spec does
    not match the headers.
- [ ] **Step 3:** Restore the implementation above. Run the same command: 10 passed.
- [ ] **Step 4: Commit.**

```bash
git add tests/test_permission_parity.py
git commit -m "test(governance): permission-parity comparison, each class proved red (WK-1178)"
```

### Task 2: The live tree

**Files:**
- Modify: `tests/test_permission_parity.py` (append)

**Interfaces:**
- Consumes: `parity_violations` from Task 1, and `checked_permissions()` from Task 3. Write
  Task 2's code, then Task 3's, and run neither until Task 3 Step 2. Task 2's red proof
  (Step 2) runs after Task 3 Step 4. The two are committed together.
- Produces: `test_live_tree_has_no_parity_violations`.

- [ ] **Step 1: Write the live test.**

```python
def _roadmap_works() -> frozenset[str]:
    text = (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
    return frozenset(re.findall(r"^### (WK-\d+)\b", text, re.MULTILINE))


@pytest.mark.req("FR-344")
def test_live_tree_has_no_parity_violations() -> None:
    from model_schema import Permission

    violations = parity_violations(
        SPEC.read_text(encoding="utf-8"),
        frozenset(p.value for p in Permission),
        checked_permissions(),
        _roadmap_works(),
    )
    assert not violations, "permission parity (CR-1247 P1 (c)):\n" + "\n".join(violations)
```

- [ ] **Step 2 (after Task 3 Step 4): Prove the live test red on the real tree** (Acceptance item 4). Delete the
  `dataset:read` row from `06` §4.1's Built table in the working tree, then run the module.
  - Expected: exactly the live test fails, with one line beginning with `ENUM_WITHOUT_ROW`'s
    text and ending `dataset:read`.
  - Any other line means the live tree was not clean before the edit. That is a finding for
    the ledger, not something to fix in this slice.
  - Restore with `git checkout -- docs/specs/06-governance.md`.

### Task 3: The route leg's source scan and the alias guard (DP-1 (C) only)

**Files:**
- Modify: `tests/test_permission_parity.py` (append)

**Interfaces:**
- Produces: `checked_permissions() -> frozenset[str]` (values of every member referenced as
  `Perm.X` or `Permission.X` in `backend/src/**/*.py`, outside comments), and
  `test_every_permission_import_alias_is_scanned`.

- [ ] **Step 1: Write the alias guard first, and see it pass on the real tree.** Then see it
  red with the Acceptance item 5 edit.

```python
BACKEND_SRC = ROOT / "backend" / "src"
SCANNED_ALIASES = ("Perm", "Permission")
_ALIAS = re.compile(r"\bPermission as (\w+)")
_REFERENCE = re.compile(r"\b(?:" + "|".join(SCANNED_ALIASES) + r")\.([A-Z_]+)\b")


def _code_lines(path: Path) -> list[str]:
    return [line.split("#", 1)[0] for line in path.read_text(encoding="utf-8").splitlines()]


def checked_permissions() -> frozenset[str]:
    """RL-1236's caller predicate (`:79-87`) as code: routes and service-level checks (E5)."""
    from model_schema import Permission

    names = {
        match
        for path in BACKEND_SRC.rglob("*.py")
        for line in _code_lines(path)
        for match in _REFERENCE.findall(line)
    }
    return frozenset(Permission[n].value for n in names if n in Permission.__members__)


@pytest.mark.req("FR-343")
def test_every_permission_import_alias_is_scanned() -> None:
    """A new alias would hide its module's checks from `checked_permissions` (RL-1236 `:84-87`)."""
    unscanned = sorted(
        f"{path.relative_to(ROOT)}: {alias}"
        for path in BACKEND_SRC.rglob("*.py")
        for line in _code_lines(path)
        for alias in _ALIAS.findall(line)
        if alias not in SCANNED_ALIASES
    )
    assert not unscanned, "Permission imported under an unscanned name:\n" + "\n".join(unscanned)
```

- [ ] **Step 2:** Run `uv run pytest -q tests/test_permission_parity.py -k alias`. Expected:
  passes at the Task 0 tree. The 12 `Permission as Perm` imports that `RL-1236` counted all
  use `Perm`.
- [ ] **Step 3: Red proof** (Acceptance item 5). Add `from model_schema import Permission as P`
  to `backend/src/app/api/jobs.py` in the working tree and re-run.
  - Expected: it fails, naming `backend/src/app/api/jobs.py: P`.
  - Revert with `git checkout -- backend/src/app/api/jobs.py`. Record the line.
- [ ] **Step 4:** Run the whole module. Expected: all pass, and the live test is green only if
  E5's zero-site members (Task 0 Step 3) are exactly the Built rows with an owner.
- [ ] **Step 5: Commit Tasks 2 and 3 together.**

```bash
git add tests/test_permission_parity.py
git commit -m "test(governance): live permission parity and the route leg's source scan (WK-1178)"
```

  **Under DP-1 (B)** (no route leg): drop Task 3 and pass `frozenset(p.value for p in Permission)`
  as `checked` in Task 2. Then `NO_CHECK_NO_OWNER` never fires on the live tree. Its synthetic
  proof stays, and the plan is revised to say the class is dormant rather than silently
  keeping it.

### Task 4: The trigger proof, the gate and the ledger

**Files:**
- Modify: `tests/test_permission_parity.py` (append)

- [ ] **Step 1: Write the trigger test** (Acceptance item 6). It is a plain text read, so it
  needs no YAML dependency.

```python
def test_python_workflow_triggers_on_every_parity_input() -> None:
    """E6: docs.yml does not run on packages/** or backend/**; this module must run on all three."""
    workflow = (ROOT / ".github" / "workflows" / "python.yml").read_text(encoding="utf-8")
    push, _, pull_request = workflow.partition("\n  pull_request:")
    for block in (push, pull_request):
        for path in ("'packages/**'", "'backend/**'", "'docs/**'"):
            assert f"- {path}" in block, f"python.yml no longer triggers on {path}"
```

- [ ] **Step 2:** Break it: delete `- 'docs/**'` from the `pull_request` block in the working
  tree. Expected: it fails naming `'docs/**'`. Revert.
- [ ] **Step 3:** Run the full two-half gate (Acceptance item 7) through the gate-runner, which
  holds a gate slot under `RL-1263`. Record each command's rc and the tree it ran on.
- [ ] **Step 4:** Commit. Push. Record the red proofs of Acceptance items 2, 4, 5 and 6 in the
  slice's `LG-` ledger, each with the failure line as printed (paraphrased where it names an
  undefined id, per [`README.md`](README.md) rule 2).

```bash
git add tests/test_permission_parity.py
git commit -m "test(governance): python.yml must trigger the parity check on every input (WK-1178)"
```

## Hand-off

- The lead mints the `SL-` and dispatches this slice after the P1 (c) ruling and its `06`
  amendment merge. It must merge **before** WK-690 Slice 3's commit that adds
  `custom_objective:author` (`PL-1268` Slice 3, Depends on).
- Once it merges, `RL-1236`'s interim rule (re-derive the table at each Work close that
  touches permissions) is retired. The ruling's "What it obliges" says so; this plan does not
  edit `RL-1236`.

## Self-review

1. **Spec coverage.**
   - `CR-1247` (c)'s two assertions are covered by Task 1's enum-without-row and
     row-without-enum classes, plus the stray-token class under the table reading.
   - "Proved red on a broken input" is Acceptance items 2, 4, 5 and 6.
   - The one-commit rule is the Specified-is-member and stale-owner classes.
   - The route check is Task 3.
   - `RL-1236`'s Acceptance (the two-list comparison) is Task 2.
   - Gap left open, by design: whether the check also compares the `BUILTIN_ROLES` role sets
     with `06`. `CR-1247` replaces `06`'s role block with a reference, so there is nothing to
     compare. If the ruling keeps an example with a subset, the stray-token class already
     covers it.
2. **Placeholder scan.** The three header literals are marked as re-read at Task 0 Step 2.
   They are the only values that are not verified against the tree, because the tables do not
   exist at `dee49f78` (E4).
3. **Type consistency.**
   - `parity_violations(spec_text, enum_values, checked, works)` has the same signature in
     Tasks 1 and 2.
   - `checked_permissions()` is defined in Task 3 and consumed in Task 2, which is committed
     with Task 3.
   - `Catalogue`'s fields are used only inside `parity_violations`.
4. **Repository literals checked at `dee49f78`:**
   - `model_schema.Permission` (imported the same way at `backend/src/app/api/authz.py:28`);
   - `Permission.__members__` and member values (`permissions.py:28-78`);
   - `### 4.1 ` at `06:188` and `### 4.2 ` at `06:305`;
   - `req` marker usage (`backend/tests/test_api_authorisation_sweep.py:174`);
   - `python.yml`'s `  pull_request:` key and its `docs/**` entries;
   - `backend/src/app/api/jobs.py` exists and imports `Permission as Perm` (`:53`).
5. **The samples were executed, not only read.** Every `python` block of this plan was
   concatenated in order into a scratch `tests/test_permission_parity.py` at `dee49f78`.
   The results were:
   - `uv run ruff check`: rc 0.
   - `uv run mypy` (strict): no issues.
   - `uv run pytest -q`: 12 passed and 1 failed. The one failure is the live test, as E4
     predicts: `06` has no table under `BUILT_HEADER` yet.
   - The live failure lists 24 enum-without-row lines (every member, because the Built
     header is absent) and 38 stray-token lines. That is E2's 41 tokens less the 3 that
     appear only in struck text.
   - The first run also exposed one defect in the sample, fixed before filing: an alias
     target that is not a member was reported both as an alias violation and as a stray
     token.

   - Re-run 2026-09-30 after auditor-plans2's F4. The results were unchanged: ruff rc 0,
     mypy clean, 12 passed and 1 failed (the live test).
   - A (B)-shape probe fed `parity_violations` a two-column Built table, with that header,
     `checked` equal to the enum, and every member in a row. It returned `[]` and raised no
     `IndexError`.

   The scratch file was deleted, and this PR adds no test.
