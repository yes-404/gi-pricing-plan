---
id: PL-9781
family: plan
kind: leaf
title: WK-1178 — The permission-parity check on RL-1305 (CR-1247 Proposal 1 (c)), superseding PL-1279: leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-01
owner: planner
tree: 101e32dc5baf8edeb986063b680ccec31e5ba724
phase: P2
work: WK-1178
supersedes: [PL-1279]
superseded_by: ~
corrected_by: []
relates: [RL-1305, CR-1247, RL-1236, RL-1263, PL-1268, PL-1237, PL-1348, ADR-704]
---

# WK-1178: the permission-parity check on RL-1305, leaf plan (supersedes PL-1279)

Filed 2026-10-01 under working id 9781, allocated by the lead. The lead mints it. At the mint,
`PL-1279` takes `status: superseded` and `superseded_by:` this plan's id. Those are the only
edits a frozen plan may take (`document-ids.md` §1.5). This plan does not edit `PL-1279`.

**Why a new plan and not an activation.** `RL-1305` changes `PL-1279`'s **acceptance**, not
only its method. The maintainer's rule is: "If any change alters a Task's ACCEPTANCE rather
than its method, file a superseding PL". The changes are:
- `PL-1279` Acceptance item 5 (the alias guard) is dropped;
- `PL-1279` Acceptance item 1's test count of 13 changes to 16 (re-derived below);
- `RL-1305` §Acceptance adds three cases that `PL-1279` lacks. They are a member that is
  referenced but never checked, a service-layer check that counts, and a route walk that
  does not flatten its routers;
- Task 3's predicate becomes a check site on live routes, plus an AST walk, with a
  flatten-and-reach proof. It replaces the text-regex scan.

Everything else in `PL-1279` that still holds is kept here and adapted, so an executor reads
this plan alone.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker and
> broken-input proofs), `test-driven-development` (every test is seen red before the code
> that turns it green), `dev-commands` (the two-half gate) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

## Goal

One test module that fails the gate in three cases:
- the permission names in [`06-governance.md`](../specs/06-governance.md) §4.1 and
  `model_schema.Permission` disagree;
- a Built name has no **check site** in `backend/src` and no owner;
- a Built name has a check site and still carries an owner.

This is the check that `CR-1247` Proposal 1 (c) requires before WK-690 Slice 3 adds
`custom_objective:author`. `RL-1305` decides it.

**Architecture:** a pytest invariant, not a production module. It does three things:
- it imports the enum directly and parses `06` §4.1's three catalogue tables;
- it reads check sites in two ways. One is the live app's routes, with included routers
  flattened and the walk's reach proved against the OpenAPI paths. The other is an AST walk
  of `require_permission(` calls in `backend/src`;
- it compares the results.

Every comparison is a pure function over text, sets or a synthetic app. So each violation
class is proved red on a synthetic broken input, and then the live tree is asserted clean. No
`backend/src` or `packages/*/src` file changes.

**Tech Stack:** Python 3.12, pytest, `re`, `ast`, `pathlib`, `fastapi.routing.iter_route_contexts`
(`fastapi` 0.141.1, `uv.lock`), `model_schema.Permission`.

**Spec and ruling:** [`06-governance.md`](../specs/06-governance.md) §3.1, §3.3 and §4.1.
`docs/rulings/RL-01305-cr-1247-proposal-1-c-decided-a-table-driven-permission-parity-test-with-a-route-leg-run-by-pytest-and-the-06-4-1-amendment.md`
§"Ruled", §"What it obliges" and §"Acceptance — the violation that must become detectable".
`docs/closures/CR-01247-plan-review-16-at-wk-672-s-close-the-permission-source-of-record-f35-s-owner-the-dedicated-host-and-p2-s-exit.md`
Proposal 1 (c).

## What RL-1305 decides, quoted verbatim

Quoted from `RL-1305` at `101e32dc`, §"Ruled", "D1 — option (C): table-driven, with a route
leg on a check-site predicate that reads checks, not references". Items 1–5:

> 1. **The catalogue legs, (B).** `06` §4.1 carries three machine-read tables, with PL-1279
>    Task 1's exact headers. The legs:
>    - **Built** (`| Permission | Governs | Check owner |`) equals the enum in both directions;
>    - **Specified** (`| Permission | Owner Work |`) is disjoint from the enum, and each owner
>      is a `WK-` heading in `docs/roadmap.md`;
>    - every **Alias** (`| Name used before | Enum name |`) targets a member;
>    - every other `name:name` token in `06`, outside struck text, is in one of the three
>      tables.
>
>    The exclusions are declared data, never layout.
> 2. **The route leg, (C), on a stricter predicate than PL-1279 Task 3's.** A Built name has a
>    **check site**, or else its `Check owner` cell names the Work that builds it. **A check
>    site is a check, not a reference:**
>    - a route dependency built by `requires(<member>)`, read off the live app's routes
>      through `PERMISSION_ATTRIBUTE`, **with the included routers flattened**. Iterating
>      `app.routes` at the top level, as `test_api_authorisation_sweep.py:184-199` does, sees
>      almost none of them (the table above), and a leg built that way would pass by seeing
>      nothing. The leg proves its own reach: the set of paths it walks must cover every path
>      in the app's OpenAPI schema (`app.openapi()["paths"]`), so a walk that sees too few
>      routes fails; or
>    - the `permission=` argument of a `require_permission(` call in `backend/src`, found by an
>      AST walk that resolves the enum's name through the module's imports.
>
>    A bare `Perm.X` or `Permission.X` reference elsewhere is **not** a check site. Examples are
>    a role list, an allow-list, or a comparison. PL-1279 Task 3's text-regex scan counts every
>    reference, a proxy that would pass a member that is named but never checked. Its alias
>    guard existed to patch the regex; under the AST walk the import resolution does that job.
>    Today the two predicates agree on every member (the table above). The difference is
>    latent, and it is exactly the case the leg exists for.
> 3. **A service-layer check counts.** `require_permission(` is the check, and `requires()` is
>    one caller of it (`authz.py:62-72`). So `admin:break_glass`, checked at `rbac.py:420-424`,
>    has a check site and needs no owner cell.
> 4. **`STALE_OWNER` is adopted, as the ninth class.** A Built row with a check site and a
>    non-empty `Check owner` fails. An owner cell cannot outlive the work it names (RFC-756).
>    **WK-674 Slice 2** clears the owner cells of `deployment:promote` and
>    `admin:manage_environments` **in the commit that adds their checks**. PL-1237 Task 2
>    builds both (`PL-1237:481-484`), and that commit touches `06` §4.1 for it. The lead tells
>    WK-674 Slice 2's leaf plan now, so the requirement is not first met as a red gate.
> 5. **The four prepared fixtures stand, and `STALE_OWNER` is the fifth.** Each is shown red on
>    a synthetic `06` and enum (the Acceptance below).

"D2 — option (ii): a pytest module under root `tests/`, run by `python.yml`":

> It is the only placement where a change on **any** side triggers the run: `packages/**` (the
> enum), `backend/**` (the checks), `docs/**` (`06`) and `tests/**` all trigger `python.yml`.
> `docs.yml` does not trigger on `packages/**` or `backend/**`, so an `audit-docs.py` check (i)
> would pass a `permissions.py`-only commit by not running (`CLAUDE.md` §2). The module imports
> `model_schema.Permission` rather than regex-reading the enum. It lives in root `tests/`, as
> PL-1279 plans (`testpaths`, the table above), and imports the app for the route leg, as
> `backend/tests` already does. It edits no shared script, so it serialises with nothing
> under `RL-1263`.

§"What it obliges":

> - **This commit:** this record, and the `06` §4.1 amendment (D4).
> - **WK-1178 (PL-1279, the planner's file, not edited here):**
>   - DP-1 to DP-3 are resolved by this record once it is minted: DP-1 (C) with `STALE_OWNER`,
>     DP-2 L2, and DP-3 (a), done here;
>   - **Task 3 changes:** the check-site predicate of D1 item 2 replaces the text-regex scan,
>     and the alias guard is no longer needed.
> - **WK-674 Slice 2:** D1 item 4. It clears the two owner cells in the commit that adds their
>   checks.
> - **WK-690 Slice 3:** moves `custom_objective:author` from Specified to Built in the commit
>   that adds the member and its `requires()` site.
> - **The lead:** tells WK-674 Slice 2's leaf plan about D1 item 4. The ADR-704 addendum is the
>   maintainer's to take up or not.

§"Acceptance — the violation that must become detectable":

> Each is shown red on broken input, as `CLAUDE.md` §13 requires, using a fixture spec and a fixture
> enum in WK-1178's slice, and the
> live tree passes:
> - an enum member with no Built row;
> - a Built row with no enum member;
> - a Specified name that is also an enum member;
> - a Built name with no check site and no owner cell;
> - a Built name with a check site **and** an owner cell (`STALE_OWNER`);
> - **a member referenced in `backend/src` but never checked**, for example listed in a role
>   set with no `requires(` and no `require_permission(` for it, still counts as having **no**
>   check site. With the text-regex predicate, it passes, and the test fails;
> - a member checked only by a service-layer `require_permission(..., permission=…)` counts as
>   checked;
> - a stray non-member token in `06` outside struck text, and outside the tables.
> - a route walk that does not flatten included routers fails the leg's own reach assertion
>   (its walked paths do not cover `app.openapi()["paths"]`).
>
> A commit touching only `packages/model-schema/src/model_schema/permissions.py` triggers
> `python.yml`, and so the test. This is shown by the workflow's `paths` (the table above) and
> observed on the slice's first such push.

## Status

`draft` until the lead mints it. It has **no open blocking decision point**: `RL-1305`
resolves `PL-1279`'s DP-1 to DP-3 (§"Decision points"), and its D4 amendment is on `main`
(Task 0 Step 2). Activation is the lead's dispatch with the maintainer's agreement, in a
separate PR. That PR carries the `SL-` row and this plan's status flip.

**SL.** WK-1178 is standing maintenance. The lead mints its slices at triage
([`document-ids.md`](../process/document-ids.md) §1.9). The proposed row text is in
§"Proposed SL row". This PR does not add it.

## Acceptance Standard

Each item can be checked by a command run from the repository root on the merge tree.

1. `uv run pytest -q tests/test_permission_parity.py` exits 0 and collects **16** tests:
   - Task 1: the clean control and nine broken-input cases (10);
   - Task 2: the live test (1);
   - Task 3: four check-site tests, which are the referenced-but-unchecked case, the
     service-layer case, the non-flattening walk and the flattened-walk control (4);
   - Task 4: the trigger test (1).
2. **Each of the nine violation classes is proved red on a broken input.** Every
   `test_broken_*` case of Task 1 asserts two things:
   - `parity_violations` returns exactly the messages that the case names;
   - each message begins with its class's own prefix constant.

   A case that returns the right count with another class's prefix fails. Seven cases name
   one class, and two cases name two (Task 1, Step 1).
3. **Every case in `RL-1305` §Acceptance has a named test.** The map:

   | `RL-1305` §Acceptance case | Test |
   |---|---|
   | an enum member with no Built row | `test_broken_enum_member_without_a_row` |
   | a Built row with no enum member | `test_broken_row_without_an_enum_member` |
   | a Specified name that is also an enum member | `test_broken_specified_name_that_is_already_a_member` |
   | a Built name with no check site and no owner cell | `test_broken_built_name_with_no_check_and_no_owner` |
   | a Built name with a check site and an owner cell (`STALE_OWNER`) | `test_broken_stale_owner_after_the_check_lands` |
   | a member referenced in `backend/src` but never checked has no check site | `test_broken_member_referenced_but_never_checked_has_no_check_site` |
   | a service-layer `require_permission(..., permission=…)` counts as checked | `test_service_layer_require_permission_counts_as_checked` |
   | a stray non-member token in `06` outside struck text and the tables | `test_broken_stray_token_in_prose` |
   | a route walk that does not flatten included routers fails the reach assertion | `test_broken_route_walk_without_flattening_fails_its_reach` |

   The referenced-but-unchecked test also asserts that `PL-1279`'s text-regex proxy counts the
   same member. So the test fails under the old predicate, as `RL-1305` requires ("With the
   text-regex predicate, it passes, and the test fails").
4. **The live tree is clean.** `test_live_tree_has_no_parity_violations` passes against the
   real `06`, the real `model_schema.Permission` and the real app. Inside it,
   `checked_permissions()` asserts that the route walk reaches every path in
   `app.openapi()["paths"]`.
5. **The live test is red on a real broken tree** (`CLAUDE.md` §13). Run two edits, one at a
   time, in the working tree. After each edit, run item 1. Record each printed failure line
   in the ledger:
   - (a) Delete the `dataset:read` row from `06` §4.1's Built table. The live test fails with
     one line, `enum member with no 06 §4.1 Built row: dataset:read`. Restore with
     `git checkout -- docs/specs/06-governance.md`.
   - (b) In `checked_permissions()`, pass `walk=_top_level_only` to `route_checks`. The live
     test fails, and each line begins `route walk did not reach a published path:`. There is
     one line per published path: 120 at `101e32dc`. Revert the edit.
6. **Every side of the comparison triggers the test in CI.**
   `test_python_workflow_triggers_on_every_parity_input` passes. For both `push` and
   `pull_request`, the `paths` of `.github/workflows/python.yml` include `packages/**`,
   `backend/**` and `docs/**`.
7. The full two-half gate of `CLAUDE.md` §11 exits 0 on the merge tree. Record each command's
   rc. The commands are `uv run ruff check .`, `uv run mypy`, `uv run lint-imports`,
   `uv run pytest -q`, `python3 scripts/audit-docs.py`,
   `uv run python scripts/req-coverage.py`,
   `uv run python scripts/generate-contracts.py --check`, and the five `pnpm --dir frontend`
   commands.
8. `git diff --stat origin/main...HEAD` names only these files:
   - `tests/test_permission_parity.py`;
   - the slice's ledger under `docs/ledgers/`;
   - `docs/INDEX.md`, regenerated for the ledger.

   It names no file under `backend/src/`, `packages/*/src/`, `frontend/` or `docs/specs/`.
   The check changes no behaviour and no spec, because `RL-1305` wrote the `06` amendment (D4).

## Global Constraints

- **No pandas** (`CLAUDE.md` §3). The test uses `re`, `ast` and `pathlib` only.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2). The
  test imports `model_schema.Permission` and never lists the 24 names.
- **A new permission lands in one commit: the `06` row, the enum member and the route check**
  (`CR-1247` Proposal 1 (c)). The check makes this a gate, and its messages say so.
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13). See Acceptance
  items 2, 3 and 5.
- **Shared files** (`RL-1263` option (c)). Two concurrent build slices may not both change the
  same existing function, class, spec section or policy table. `docs/INDEX.md` is a registry
  file, regenerated and never hand-merged.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What the check holds | Marker |
|---|---|---|---|
| `06` §3.1 | FR-343 | Permissions are checked in the backend. The route leg asserts that every Built name has a check site (a `requires()` route dependency or a service-layer `require_permission(` call) or an owner | `req("FR-343")` on the route-leg and check-site tests |
| `06` §3.1 | FR-344 | Custom roles compose from "the same permission vocabulary". The vocabulary is the enum, and `06` §4.1 states its meaning | `req("FR-344")` on the two-list tests |
| `06` §3.3 | FR-367 | `custom_objective:author`: "The enum member and its check land together in WK-690". The check turns that into a gate: the name moves from Specified to Built in the commit that adds the member | `req("FR-367")` on the Specified-is-member test |

FR-342, FR-345, FR-346, FR-347, FR-348, FR-349 and FR-350 (`06` §3.1) are **not** covered.
They govern identity, scope, the Auditor, Service Accounts, role administration, break-glass
and IdP mapping. None of them is about which names exist.

### Measurements at `101e32dc` (Task 0 Steps 1–3, re-run for this plan)

Each count was run from the repository root of a clean checkout at
`101e32dc5baf8edeb986063b680ccec31e5ba724` (origin/main, 2026-10-01). Each count names its
corpus and its predicate.

**M1. `RL-1305` is on `main`, and so is its D4 amendment.** The ruling file is
`docs/rulings/RL-01305-…` (`status: active`). Its decisions are D1 (C) with `STALE_OWNER`,
D2 (ii) and D3 (a), and D4 is written into `06`.

**M2. The three headers are on `main`, verbatim, inside a blockquote.** In `06` §4.1
(`### 4.1` at `06:188`, `### 4.2` at `06:342`):
- `> | Permission | Governs | Check owner |` is at `:269`;
- `> | Name used before | Enum name |` is at `:313`;
- `> | Permission | Owner Work |` is at `:333`.

Task 1's `_table` removes the `> ` prefix. These literals are now verified against the tree,
so they are no longer placeholders.

**M3 (E1). The enum has 24 members.**
`grep -oE '= "[a-z_]+:[a-z_]+"' packages/model-schema/src/model_schema/permissions.py | tr -d '=" ' | sort -u | wc -l`
prints 24.

**M4 (E4, table reading). The Built table has 24 rows, and it equals the enum in both
directions.**
`sed -n '188,341p' docs/specs/06-governance.md | awk '/^> \| Permission \| Governs \| Check owner \|/{f=1;next} f&&/^> \|---/{next} f&&/^> \|/{print;next} f{exit}' | grep -oE '^> \| `[a-z_]+:[a-z_]+`' | grep -oE '[a-z_]+:[a-z_]+' | sort -u`
prints 24 names. `comm -23` and `comm -13` against M3 are both empty. The only rows with a
non-empty `Check owner` are `deployment:promote` → `WK-674` and
`admin:manage_environments` → `WK-674`.

**M5 (E5). Check sites under `RL-1305`'s predicate: 22 members are checked, and the 2 that
are not are exactly the 2 owner rows.**
- **Route leg.** The live app comes from `create_app(Settings(environment=Environment.LOCAL,
  version=…, log_level="ERROR"))`, the construction that `scripts/generate-contracts.py`
  uses, with no database and no lifespan. The leg walks
  `fastapi.routing.iter_route_contexts(app.routes)` and keeps `APIRoute` originals.
  - It walks 141 route contexts over 120 distinct paths. `app.openapi()["paths"]` has 120.
    Both set differences are empty, so the reach is complete.
  - Reading `PERMISSION_ATTRIBUTE` off each route's dependency tree gives **21** members.
- **The top-level walk is blind**, as `RL-1305` says. Iterating `app.routes` directly gives
  29 entries: 2 `APIRoute`s, and the rest are `Route` or `_IncludedRouter`. The 2 routes
  declare 0 members, and 118 of the 120 OpenAPI paths are unreached.
- **AST leg.** It looks for calls whose callee name is `require_permission` and whose
  `permission=` keyword is `<local name of model_schema.Permission>.<MEMBER>`, over
  `backend/src/**/*.py`. There are **46** such calls, and they name **11** members.
  - 2 further `permission=<Permission>.X` keywords are `has_permission(` calls. They are not
    check sites under `RL-1305` D1 item 2. Their members are route-checked anyway.
  - `admin:break_glass` is the only member found by the AST leg alone
    (`backend/src/app/platform/rbac.py:424`).
- **Union: 22 members.** The members with no check site are `deployment:promote` and
  `admin:manage_environments`, and M4 gives each of them an owner. So the live tree is clean.
- **`PL-1279`'s text-regex predicate** (`(Perm|Permission)\.<NAME>\b` outside comments) gives
  the same 22. The two predicates agree today, as `RL-1305` D1 item 2 says, and the
  difference is latent.
- **Cross-check by grep:**
  - `grep -rnE --include='*.py' 'requires\((Perm|Permission)\.' backend/src/app/api | wc -l`
    prints 54 call lines. `grep -rn --include='*.py' 'requires(' backend/src/app/api | wc -l`
    prints 56. At `dee49f78` the figures were 52 and 54.
  - `grep -rnE --include='*.py' 'permission=(Perm|Permission)\.' backend/src` prints 48 lines:
    the 46 `require_permission` calls and the 2 `has_permission` calls.

**M6 (E6). CI triggers are unchanged.** `.github/workflows/python.yml` lists `packages/**`,
`backend/**` and `docs/**` under both `push` and `pull_request`. `docs.yml` lists neither
`packages/**` nor `backend/**`.

### File contention (for the lead's serialisation under `RL-1263` option (c))

**Against lane A, `SL-1345` (`PL-1348`'s write set, §"Write set, and its contention"):
no overlap.** This slice creates `tests/test_permission_parity.py` and its ledger, and it
regenerates `docs/INDEX.md`, which is a registry file. Not one of these paths is in
`PL-1348`'s write set:
- `03`;
- `docs/open-questions.md`;
- `model_schema/money.py` and `scoring.py`;
- `scoring.schema.json`;
- `pricing_core/money.py`, `__init__.py`, and the `rating/` files `ladder.py`, `score.py`,
  `runtime.py`, `properties.py` and `compile.py`;
- `backend/src/app/errors.py`, `api/score.py` and `observability/metrics.py`;
- the test files that the table names.

The two slices only meet through reads. This slice's live test imports `app.main.create_app`,
which imports `backend/src/app/api/score.py`. `SL-1345` edits that file's responses and its
error mapping, not its `requires()` dependencies, and it adds no permission. So the parity
result does not depend on which slice merges first. Each slice re-gates on the other's merge
as usual.

| Path | This slice | Other slices that edit it | Consequence |
|---|---|---|---|
| `tests/test_permission_parity.py` (new) | creates | none | none |
| `docs/specs/06-governance.md` §4.1 | reads only (`RL-1305` D4 wrote it) | **WK-674 Slice 2**, which clears the two owner cells in the commit that adds the checks for `deployment:promote` and `admin:manage_environments` (`RL-1305` D1 item 4; `PL-1237` Task 2). **WK-690 Slice 3**, which moves `custom_objective:author` from Specified to Built (`RL-1305` §"What it obliges"; `PL-1268` Slice 3) | No file overlap, but an **order**. Once this lands, each of those slices must satisfy the check in its own commit |
| `packages/model-schema/src/model_schema/permissions.py` | reads (imports) | **WK-690 Slice 3** adds `CUSTOM_OBJECTIVE_AUTHOR` | none. WK-690 S3 comes after this slice (`PL-1268` Slice 3, Depends on) |
| `backend/src/**` | reads (the AST walk; the app import) | **SL-1345** (above); WK-674 S2/S3, WK-690 S3, WK-1250 later slices | none. Each one adds or keeps check sites, and the parity check reads them unchanged |
| `scripts/audit-docs.py`, `.github/workflows/*` | not touched (D2 (ii)) | WK-1170 and WK-1169 slices (`audit-docs.py`) | none |
| `docs/INDEX.md` | regenerated for the ledger | every PR | registry file: regenerate, never hand-merge |

**Behavioural dependency, not file contention.** WK-674 Slice 2 might merge **before** this
slice. In that case its commit has already cleared the two owner cells, as `RL-1305` D1
item 4 obliges, and Task 0 Step 3 re-measures M4 and M5 to confirm it. If the cells were not
cleared, `STALE_OWNER` fires on the first run. That is a finding against WK-674 S2, not
something to fix in this slice.

### Proposed SL row (the lead mints it; not added here)

````markdown
#### SL-<n> — WK-1178 slice — the permission-parity check (PL-<this plan>, RL-1305)

```yaml
id: SL-<n>
family: slice
title: WK-1178 slice — the permission-parity check (PL-<this plan>, RL-1305)
status: draft                   # draft → active → closed | retired (§1.2a)
created: <mint date>
owner: planner                   # cut by the planner (draft); lead dispatches (active)
tree: <mint tree>
phase: P2
work: WK-1178
corrected_by: []
relates: [PL-<this plan>, RL-1305, CR-1247, RL-1236, PL-1268]
```

A pytest invariant fails the gate in three cases: `06` §4.1's permission tables and
`model_schema.Permission` disagree; a Built name has no check site (a flattened, reach-proved
`requires()` route dependency, or an AST-found `require_permission(` call) and no owner; or a
Built name has a check site and still carries an owner (`CR-1247` Proposal 1 (c), decided by
`RL-1305`). It must merge before WK-690 Slice 3's commit that adds `custom_objective:author`
(`PL-1268` Slice 3). It retires `RL-1236`'s interim re-derive-at-each-close rule when it merges.
Leaf plan `PL-<this plan>`, which supersedes `PL-1279`.
````

### Size

Small. One new test module of about 430 lines, and no production code. There are four tasks
after the preconditions. The work is about half a day for an executor, plus one full two-half
gate run (a gate slot under `RL-1263`). It takes no NFR measurement, so it need not run
exclusive.

## Decision points

None is open. `RL-1305` resolves every one that `PL-1279` carried:

| `PL-1279` DP | Question | Resolved by | Answer |
|---|---|---|---|
| DP-1 | What the check asserts | `RL-1305` D1 | (C): table-driven, plus a route leg on a check-site predicate that "reads checks, not references". `STALE_OWNER` is adopted as the ninth class (D1 item 4) |
| DP-2 | Where the check lives | `RL-1305` D2 | (ii) = `PL-1279`'s L2: a root `tests/` pytest module run by `python.yml` |
| DP-3 | Who writes the `06` §4.1 amendment | `RL-1305` D4 | (a): the decision-maker, in the ruling's own commit. It is on `main` (M2, M4) |
| — | RL or ADR (`CR-1247` Proposal 1) | `RL-1305` D3 | (a): the ruling. A dated ADR-704 addendum is proposed to the maintainer and does not gate this slice |

`PL-1279`'s branches for "if 9856 omits stale-owner", "under DP-1 (B)" and "under DP-3 (b)"
are removed, because `RL-1305` decided each of them. The (B)-shape fallback in
`extract_catalogue` (the optional owner column) is removed too. The Built table has three
columns (M2).

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** Confirm that `RL-1305` is on `main` and is still `status: active`, with no
  `superseded_by`:
  `git grep -n '^status:\|^superseded_by:' origin/main -- 'docs/rulings/RL-01305-*'`.
  If it has been superseded, **stop**. The plan is revised before `active`.
- [ ] **Step 2:** Confirm the three header rows of M2 at the dispatch tree. `BUILT_HEADER`,
  `SPECIFIED_HEADER` and `ALIAS_HEADER` must equal them character for character, without the
  `> ` prefix. A changed header, table set or column order is a replan.
- [ ] **Step 3:** Re-run M3, M4 and M5 at the dispatch tree, using the predicates exactly as
  written above. Record each count with its tree in the ledger. M4's two `comm` runs must
  print nothing. M5's zero-site members must equal the Built rows that carry an owner, and the
  route walk's reach must be complete.
- [ ] **Step 4:** Run `gh pr list --state open` to find anything that touches `06` §4.1,
  `permissions.py` or a `requires(`/`require_permission(` site (WK-674 S2/S3, WK-690 S3,
  WK-1250). Name each one's head SHA in the ledger.

### Task 1: The pure comparison, and each violation class proved red

**Files:**
- Create: `tests/test_permission_parity.py`

**Interfaces:**
- Produces:
  - `parity_violations(spec_text: str, enum_values: frozenset[str], checked: frozenset[str], works: frozenset[str]) -> list[str]`;
  - the nine message-prefix constants below;
  - `extract_catalogue(spec_text: str) -> Catalogue`. `Catalogue` is a frozen dataclass with
    these fields: `built` (name → owner Work or `None`), `specified` (name → owner Work),
    `aliases` (`06`-era name → enum name), `stray` (other tokens) and `duplicates`.

- [ ] **Step 1: Write the failing tests.** The header literals are M2's, verified at
  `101e32dc`.

```python
"""The permission-parity check: `06` §4.1 against `model_schema.Permission` (RL-1305).

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
    built = {_name(r[0]): _owner(r[2]) for r in _table(section, BUILT_HEADER)}
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
  has no Built row either. A name in two tables is also a Specified name that is a member.
  The other seven `test_broken_*` cases each expect exactly one message, of a single class.

- [ ] **Step 2: Run them before the implementation exists.** Stub `parity_violations` to
  `return []`, then run `uv run pytest -q tests/test_permission_parity.py`.
  - Expected: every `test_broken_*` case fails on `_only`'s length assertion, with `[]`
    printed. The clean control passes.
  - A broken case that fails for any other reason is a defect in the sample. Fix it before
    Step 3.
- [ ] **Step 3:** Restore the implementation above and run the same command. Expected: 10
  passed.
- [ ] **Step 4: Commit.**

```bash
git add tests/test_permission_parity.py
git commit -m "test(governance): permission-parity comparison, each class proved red (WK-1178)"
```

### Task 2: The live tree

**Files:**
- Modify: `tests/test_permission_parity.py` (append)

**Interfaces:**
- Consumes: `parity_violations` from Task 1 and `checked_permissions()` from Task 3. Write
  Task 2's code, then Task 3's, and run neither until Task 3 Step 3. Task 2's red proof
  (Step 2) runs after Task 3 Step 4. Commit the two tasks together.
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

- [ ] **Step 2 (after Task 3 Step 4): Prove the live test red on the real tree**
  (Acceptance item 5 (a)). In the working tree, delete the `dataset:read` row from `06`
  §4.1's Built table, then run the module.
  - Expected: only the live test fails, with one line:
    `enum member with no 06 §4.1 Built row: dataset:read`.
  - Any other line means that the live tree was not clean before the edit. Record that as a
    finding in the ledger. Do not fix it in this slice.
  - Restore with `git checkout -- docs/specs/06-governance.md`.

### Task 3: The check-site predicate, which reads checks, not references (`RL-1305` D1 items 2 and 3)

**This replaces `PL-1279` Task 3 in full.** That task scanned the text for every
`Perm.X`/`Permission.X` reference and had an alias guard. Both are gone: the AST walk resolves
the import alias, and a reference that is not a check does not count.

**Files:**
- Modify: `tests/test_permission_parity.py` (append; the imports go at the module top)

**Interfaces:**
- Produces:
  - `service_layer_checks(sources: Iterable[str], members: Mapping[str, str]) -> frozenset[str]`.
    It returns the members passed as `permission=<local Permission name>.<MEMBER>` to a call
    whose callee name is `require_permission`. The local name is resolved from each module's
    `from model_schema import Permission [as X]`;
  - `walk_api_routes(app) -> list[tuple[str, APIRoute]]`. It returns every API route with its
    full path, with included routers flattened through `fastapi.routing.iter_route_contexts`;
  - `route_checks(app, attribute, walk=walk_api_routes) -> tuple[frozenset[str], list[str]]`.
    It returns the members that the walked routes' dependency trees declare through
    `attribute`, and the reach shortfall against `app.openapi()["paths"]`;
  - `checked_permissions() -> frozenset[str]`. It is the live union of the two legs, and it
    asserts that the shortfall is empty.

- [ ] **Step 1: Add the imports to the module top.**

```python
import ast
from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum

from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute, APIRouter, iter_route_contexts
```

- [ ] **Step 2: Write the predicate and its four tests.** The tests use synthetic modules
  and a synthetic app with an included router inside another included router.

```python
BACKEND_SRC = ROOT / "backend" / "src"
#: The one service-layer check function (`backend/src/app/platform/rbac.py`); `requires()`
#: is one of its callers (`backend/src/app/api/authz.py`). RL-1305 D1 item 3.
CHECK_FUNCTION = "require_permission"
REACH_SHORTFALL = "route walk did not reach a published path"


def service_layer_checks(sources: Iterable[str], members: Mapping[str, str]) -> frozenset[str]:
    """Members passed as `permission=` to a `require_permission(` call (RL-1305 D1 item 2).

    `members` maps an enum attribute name to its value. The enum's local name is resolved
    through each module's own `from model_schema import Permission [as X]`, so an alias is
    followed and a bare reference elsewhere (a role set, an allow-list, a comparison) is not
    a check site.
    """
    found: set[str] = set()
    for source in sources:
        tree = ast.parse(source)
        local = {
            alias.asname or alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module == "model_schema"
            for alias in node.names
            if alias.name == "Permission"
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            callee = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            if callee != CHECK_FUNCTION:
                continue
            for kw in node.keywords:
                value = kw.value
                if (
                    kw.arg == "permission"
                    and isinstance(value, ast.Attribute)
                    and isinstance(value.value, ast.Name)
                    and value.value.id in local
                    and value.attr in members
                ):
                    found.add(members[value.attr])
    return frozenset(found)


def walk_api_routes(app: FastAPI) -> list[tuple[str, APIRoute]]:
    """Every API route with its full path, included routers flattened (RL-1305 D1 item 2)."""
    return [
        (str(context.path), context.original_route)
        for context in iter_route_contexts(app.routes)
        if isinstance(context.original_route, APIRoute)
    ]


def route_checks(
    app: FastAPI,
    attribute: str,
    walk: Callable[[FastAPI], list[tuple[str, APIRoute]]] = walk_api_routes,
) -> tuple[frozenset[str], list[str]]:
    """Members declared by `requires()` on the walked routes, and the leg's reach shortfall."""

    def calls(dependant: object) -> Iterable[object]:
        for dependency in getattr(dependant, "dependencies", []):
            yield dependency.call
            yield from calls(dependency)

    walked = walk(app)
    members = frozenset(
        str(getattr(call, attribute).value)
        for _, route in walked
        for call in calls(route.dependant)
        if getattr(call, attribute, None) is not None
    )
    reached = {path for path, _ in walked}
    shortfall = [f"{REACH_SHORTFALL}: {p}" for p in sorted(set(app.openapi()["paths"]) - reached)]
    return members, shortfall


def checked_permissions() -> frozenset[str]:
    """The live check sites: routes (flattened, reach proved) and service-layer calls."""
    from app.api.authz import PERMISSION_ATTRIBUTE
    from app.config import Environment, Settings
    from app.main import create_app
    from model_schema import Permission

    app = create_app(Settings(environment=Environment.LOCAL, version="parity", log_level="ERROR"))
    routed, shortfall = route_checks(app, PERMISSION_ATTRIBUTE)
    assert not shortfall, "\n".join(shortfall)
    sources = (p.read_text(encoding="utf-8") for p in sorted(BACKEND_SRC.rglob("*.py")))
    return routed | service_layer_checks(sources, {m.name: m.value for m in Permission})


# --- synthetic check sites --------------------------------------------------------------

_MEMBERS = {"A_READ": "a:read", "A_DEPLOY": "a:deploy"}
_ROLE_SET_ONLY = """
from model_schema import Permission as P

READERS = frozenset({P.A_READ, P.A_DEPLOY})

async def promote(session, actor):
    if P.A_DEPLOY in READERS:
        return actor
"""
_SERVICE_CHECK = """
from model_schema import Permission as P
from app.platform import rbac

async def promote(session, actor):
    await rbac.require_permission(session, principal=actor, permission=P.A_DEPLOY)
"""
_TEXT_REGEX = re.compile(r"\b(?:Perm|Permission|P)\.([A-Z_]+)\b")  # PL-1279 Task 3's proxy


@pytest.mark.req("FR-343")
def test_broken_member_referenced_but_never_checked_has_no_check_site() -> None:
    # The text-regex proxy counts both members; the AST predicate counts neither.
    assert {_MEMBERS[n] for n in _TEXT_REGEX.findall(_ROLE_SET_ONLY)} == {"a:read", "a:deploy"}
    assert service_layer_checks([_ROLE_SET_ONLY], _MEMBERS) == frozenset()
    checked = service_layer_checks([_ROLE_SET_ONLY], _MEMBERS) | {"a:read"}
    old, new = "| `a:deploy` | Deploying A | WK-674 |", "| `a:deploy` | Deploying A |  |"
    _only(parity_violations(_CLEAN.replace(old, new), _ENUM, checked, _WORKS), NO_CHECK_NO_OWNER)


@pytest.mark.req("FR-343")
def test_service_layer_require_permission_counts_as_checked() -> None:
    assert service_layer_checks([_SERVICE_CHECK], _MEMBERS) == frozenset({"a:deploy"})
    old, new = "| `a:deploy` | Deploying A | WK-674 |", "| `a:deploy` | Deploying A |  |"
    checked = service_layer_checks([_SERVICE_CHECK], _MEMBERS) | {"a:read"}
    assert parity_violations(_CLEAN.replace(old, new), _ENUM, checked, _WORKS) == []


class _P(StrEnum):
    A_READ = "a:read"


_ATTRIBUTE = "__parity_probe__"


def _nested_app() -> FastAPI:
    async def dependency() -> None:
        return None

    setattr(dependency, _ATTRIBUTE, _P.A_READ)
    inner = APIRouter(prefix="/inner")

    @inner.get("/thing", dependencies=[Depends(dependency)])
    async def thing() -> dict[str, str]:
        return {}

    outer = APIRouter(prefix="/outer")
    outer.include_router(inner)
    app = FastAPI()
    app.include_router(outer, prefix="/api")
    return app


def _top_level_only(app: FastAPI) -> list[tuple[str, APIRoute]]:
    """The walk `backend/tests/test_api_authorisation_sweep.py` uses: no flattening."""
    return [(str(r.path), r) for r in app.routes if isinstance(r, APIRoute)]


@pytest.mark.req("FR-343")
def test_broken_route_walk_without_flattening_fails_its_reach() -> None:
    members, shortfall = route_checks(_nested_app(), _ATTRIBUTE, walk=_top_level_only)
    assert members == frozenset()
    assert shortfall == [f"{REACH_SHORTFALL}: /api/outer/inner/thing"]


@pytest.mark.req("FR-343")
def test_flattened_route_walk_reaches_nested_routers() -> None:
    assert route_checks(_nested_app(), _ATTRIBUTE) == (frozenset({"a:read"}), [])
```

- [ ] **Step 3: Red first, against the two proxies that `RL-1305` rejects.** Before the
  bodies are final, make two temporary changes:
  - make the first line of `service_layer_checks`
    `return frozenset(members[n] for src in sources for n in _TEXT_REGEX.findall(src) if n in members)`,
    which is `PL-1279`'s text-regex predicate;
  - give `route_checks` the default `walk=_top_level_only`.

  Then run `uv run pytest -q tests/test_permission_parity.py -k 'check_site or service_layer or flatten'`.
  - Expected: 2 failed and 2 passed.
  - `test_broken_member_referenced_but_never_checked_has_no_check_site` fails, because the
    proxy counts the role-set references.
  - `test_flattened_route_walk_reaches_nested_routers` fails, because the top-level walk
    reaches nothing.
  - The service-layer test passes. The two predicates agree on that case, as `RL-1305`
    D1 item 2 says.
  - The non-flattening test passes, because it names its walk explicitly.

  Remove both changes and run the whole module. Expected: 15 passed (Tasks 1–3).
- [ ] **Step 4: Red proof on the real app** (Acceptance item 5 (b)). In
  `checked_permissions()`, pass `walk=_top_level_only` to `route_checks`, then run the module.
  - Expected: only the live test fails. Every line begins
    `route walk did not reach a published path:`. At `101e32dc` there are 120 lines.
  - Revert the edit. Record the count and the first line.
- [ ] **Step 5: Commit Tasks 2 and 3 together.**

```bash
git add tests/test_permission_parity.py
git commit -m "test(governance): live permission parity and the check-site route leg (WK-1178)"
```

**Known limit, fail-closed.** A `requires()` dependency attached at router level
(`APIRouter(dependencies=[…])` or `include_router(…, dependencies=[…])`) is not in a route's
own `dependant` tree. At `101e32dc` the only router-level dependency is `demo_enabled`
(`backend/src/app/api/demo.py:51`), which is not a permission. A future router-level
permission would read as **no** check site. The result is a red gate, never a false green, and
the fix is to read the include context then.

### Task 4: The trigger proof, the gate and the ledger

**Files:**
- Modify: `tests/test_permission_parity.py` (append)

- [ ] **Step 1: Write the trigger test** (Acceptance item 6). It is a plain text read, so it
  needs no YAML dependency.

```python
def test_python_workflow_triggers_on_every_parity_input() -> None:
    """docs.yml does not run on packages/** or backend/**; this module must run on all three."""
    workflow = (ROOT / ".github" / "workflows" / "python.yml").read_text(encoding="utf-8")
    push, _, pull_request = workflow.partition("\n  pull_request:")
    for block in (push, pull_request):
        for path in ("'packages/**'", "'backend/**'", "'docs/**'"):
            assert f"- {path}" in block, f"python.yml no longer triggers on {path}"
```

- [ ] **Step 2:** Break the test: in the working tree, delete `- 'docs/**'` from the
  `pull_request` block. Expected: the test fails and names `'docs/**'`. Revert the edit.
- [ ] **Step 3:** Run the full two-half gate (Acceptance item 7) through the gate-runner, which
  holds a gate slot under `RL-1263`. Record each command's rc and the tree it ran on.
- [ ] **Step 4:** Commit and push. In the slice's `LG-` ledger, record each red proof of
  Acceptance items 2, 3, 5 and 6, with the failure line as printed. Paraphrase a line where it
  names an undefined id, per [`README.md`](README.md) rule 2.

```bash
git add tests/test_permission_parity.py
git commit -m "test(governance): python.yml must trigger the parity check on every input (WK-1178)"
```

## Hand-off

- The lead mints this plan's id and the `SL-`, and dispatches the slice. It must merge
  **before** WK-690 Slice 3's commit that adds `custom_objective:author` (`PL-1268` Slice 3,
  Depends on).
- When this slice merges, `RL-1236`'s interim rule (re-derive the table at each Work close that
  touches permissions) retires, as `RL-1305` D4's closing line says. This plan does not edit
  `RL-1236`.
- The lead tells WK-674 Slice 2's leaf plan about `RL-1305` D1 item 4 (`RL-1305`
  §"What it obliges"). This plan only records the order.

## Self-review

1. **Coverage of the ruling.** The nine cases of `RL-1305` §Acceptance each have one named
   test (Acceptance item 3). The trigger sentence is Task 4. D1 item 1 is Task 1. D1 items 2
   and 3 are Task 3. D1 item 4 is `STALE_OWNER` in Task 1. D2 is the module's placement. D4 is
   read, not written.
2. **What changed from `PL-1279`, and why it is acceptance and not method.**
   - Acceptance item 1 changes from 13 tests to 16. The alias guard (−1) is gone, and Task 3
     adds four tests (+4).
   - `PL-1279` item 5 (the alias guard) is gone.
   - Item 3 (the `RL-1305` map) is new.
   - Item 5 gains (b), the reach red proof.
   - Item 8 loses the DP-3 (b) exception.
   - The removed conditionals are listed in §"Decision points".
3. **Placeholder scan.** The header literals are now verified at `101e32dc` (M2). The SL row
   text holds `<n>`, `<this plan>`, `<mint date>` and `<mint tree>`, which the lead fills in
   at minting.
4. **Type consistency.**
   - `parity_violations` has the same signature in Tasks 1 and 2.
   - `checked_permissions()` is defined in Task 3 and consumed in Task 2, and the two tasks
     are committed together.
   - `route_checks`' `walk` parameter is the seam that both the non-flattening test and
     Acceptance item 5 (b) use.
5. **Repository literals checked at `101e32dc`:**
   - `PERMISSION_ATTRIBUTE` and `requires()` (`backend/src/app/api/authz.py`);
   - `require_permission` and `has_permission` (`backend/src/app/platform/rbac.py:274`,
     `:256`);
   - `create_app` and `Settings`/`Environment` (`backend/src/app/main.py:64`,
     `backend/src/app/config.py:32`), and the construction without a database in
     `scripts/generate-contracts.py`;
   - `fastapi.routing.iter_route_contexts` on `fastapi` 0.141.1;
   - `### 4.1 ` at `06:188` and `### 4.2 ` at `06:342`;
   - `python.yml`'s `  pull_request:` key;
   - `mypy`'s `files` includes `tests` (`pyproject.toml`).
6. **The samples were executed, not only read.** Every `python` block of this plan was
   assembled in order into a scratch `tests/test_permission_parity.py` at `101e32dc`, with
   Task 3's imports at the top:
   - `uv run ruff check` and `ruff format --check`: clean;
   - `uv run mypy` (strict): no issues;
   - `uv run pytest -q tests/test_permission_parity.py`: **16 passed**;
   - Acceptance item 5 (a): 1 failed, with the single line
     `enum member with no 06 §4.1 Built row: dataset:read`;
   - Acceptance item 5 (b): 1 failed, with 120 reach-shortfall lines, the first being
     `route walk did not reach a published path: /api/v1/approval-policy`;
   - Task 3 Step 3's proxy stubs: 2 failed and 2 passed, exactly as that step states.

   The scratch file was deleted, and this PR adds no test.
