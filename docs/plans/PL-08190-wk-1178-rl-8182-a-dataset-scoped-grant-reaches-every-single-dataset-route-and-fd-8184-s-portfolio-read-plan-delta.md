---
id: PL-8190
family: plan
kind: map
title: WK-1178 — RL 8182, a dataset-scoped grant reaches every route that acts on one Dataset (Dataset Version routes, single-Dataset dataset and validation reads, blob download through its owning version, blob staging held anywhere) and FD 8184's portfolio `dataset:read` — a dated Work-plan delta cutting one slice
status: draft                  # draft → active → superseded | retired (§1.2a) — draft while DP-1..DP-4 are open; working id, not minted
created: 2026-10-22
owner: planner
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-8181, SL-8185, RL-8182, FD-8184, RL-8176, FR-345, FR-343, FR-350, FR-452, FR-263, FR-63, FR-76]
---

# PL-8190 — WK-1178: RL 8182's slice — a dataset-scoped grant reaches every single-Dataset route, and FD 8184's fix

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md`
> §1.6, PL row). It cuts **one fix slice** under WK-1178. Its `SL-` and `LG-` ids are the
> lead's to allocate at the GO; this plan calls them "the slice" and "its ledger" until then.
> The executor is spawned from `.claude/roles/executor.md` and binds `test-driven-development`,
> `python-test`, `python-package`, `fastapi-service`, `spec-change`, `dev-commands` and
> `git-hygiene`. The ledger is filed by the executor at build; this plan names it and does not
> create it. Written by planner-8182 (Claude Opus 5.5), 2026-10-22, at tree `71e481fa`
> (origin/main), with SL 8185's guard read at `sl-8185-wk1178-fd8177-scoped-writes` @`40de35f5`.

## Goal

A principal whose `dataset:*` grant is scoped to Dataset X uses every route that acts
on X or one of X's Dataset Versions, and is refused on Dataset Y with `SCOPE_DENIED` (a blob:
the same 404 as an unknown one). The 25 owned rows that RL 8182 and FD 8184 hold in SL 8185's
`KNOWN_SCOPE_GAPS` are deleted, each after a red-first test.

## Architecture

SL 8185's `requires(perm, held_anywhere=True)` route gate, then the handler
loads (404) and checks the permission on the Dataset (403 `SCOPE_DENIED`) through three small
literal-permission helpers, then counts (FR-452). The guard file changes in its tables only.

**Tech Stack:** FastAPI, SQLAlchemy async, pytest (DB-backed, through `run-small.sh`).

**Spec:** `docs/specs/06-governance.md` FR-345 (SL 8185's dated clause of 2026-10-22, and RL
8182's clause, DP-1), FR-343, FR-350; `docs/specs/03-rating-engine.md`:1060, :1061, :1080,
:1083 (§5.1, the portfolio `dataset:read`); `docs/specs/07-platform.md` FR-452.

## The rulings this plan carries out

All four are entries in `/home/puzhenhao1989/gi-pricing-plan.local/channel/to-lead.md`, read
there by this planner.

- **"2026-10-22 17:36:24 BST — Maintainer: RL 8182 ADOPTED, option (C); the other single-Dataset
  routes join its slice; the id-oracle residual ACCEPTED; FD 8184 probe GO"**, items 1 and 2,
  verbatim:
  > 1. **ADOPTED: (C), per route by what it acts on:**
  >    - dataset_versions.py :60–62 (11 routes) HONOUR the scope;
  >    - blobs.py:52 upload-url/complete is "held under any scope", with the scope check at ingest;
  >    - blobs.py:50 GET is scoped through the owning Dataset Version (job-only blobs workspace-wide; a refusal is the same 404);
  >    - reference_tables.py:50 stays WORKSPACE-wide and **the spec records it** (not a Dataset, no ScopeType, outside FR-345; FR-350 never infers scope).
  >
  >    **Order: holds_anywhere → 403; load → 404; scoped → SCOPE_DENIED.** [...] **Owner:** WK-1178; **its own slice AFTER PL 8181's** (shared files are sequenced, not concurrent). The authority is this entry.
  > 2. **datasets.py's other single-Dataset routes** (ingest :515, detail :433, versions :588/:647/:662, schema :751) **and validation.py:67 JOIN RL 8182's slice.** It is the same class, so one sweep and one test pattern. Each route gets its own red-first test with a scoped principal, and the permanent guard from 17:27:15 covers them.
- **"2026-10-22 17:38:11 BST — Maintainer: PL 8181 (FD 8177 fix) DP-0..DP-3 RULED; [...]"**: the
  helper is `requires(perm, held_anywhere=True)`; "the route gate does not count, and services
  count after their scoped check"; the order sentence is a dated **FR-345** clause; the guard's
  `KNOWN_SCOPE_GAPS` rows are "removed by the slice that fixes it (RL 8182's slice, FD 8184)".
- **"2026-10-22 17:41:48 BST — [...] FD 8184 = HIGH [...]"**, item 2: the fix "JOINS RL 8182's
  slice, covering rate_tables.py :432–437/:528–535 and dislocation_runs.py
  `_require_dataset_read` (:79/:105/:167), with the dataset_id resolved from the spec or the
  stored run FIRST. Each route red-first. The control must assert the scoped refusal, not the
  wrong-reason pass."
- **"2026-10-22 17:46:43 BST — Maintainer: FD 8177 and FD 8184 RE-RATED MEDIUM (LATENT); [...]"**,
  item 2, verbatim: "**RL 8182's slice** (FD 8184 plus the joining routes) is **queued BEHIND P2
  row work and open P2 HIGHs**. It lands before P2 close if capacity allows; otherwise it is
  CARRIED to WK-676 with owner and condition: "before POST /role-assignments ships". It must not
  be skipped silently." See *The carry rule*, below.

RL 8182 itself is `docs/rulings/RL-08182-*.md` on `docs/batch-fd1842-oq-gaterows` @`39c4ae25`
(minting as RL 1849); FD 8184 is on the same branch (FD 1853 at mint). Its "What it obliges"
items 2–5 are the scope below.

## Verified first, at `71e481fa`

My own reads, not the relay. Routes and handlers by an AST walk of the router decorators in
`backend/src/app/api/{dataset_versions,blobs,validation,datasets,reference_tables}.py`; the guard
by reading `backend/tests/test_route_scope_guard.py` at `40de35f5`.

1. **SL 8185's guard tables** (`test_route_scope_guard.py` at `40de35f5`): `ROUTE_SCOPES` (`:87`),
   `KNOWN_SCOPE_GAPS` (`:151`) with **26 rows**: 1 owned `SL-8185` (`PUT
   /api/v1/datasets/{slug}/rule-set`, its Task 4), **20 owned `RL-8182`**, **5 owned `FD-8184`**.
   This slice deletes exactly the 25 RL-8182 and FD-8184 rows. The SL-8185 row is not this
   slice's.
2. **Reference tables stay workspace-wide, and the guard already says so.** `ROUTE_SCOPES` holds
   `GET /api/v1/reference-tables`, `/{slug}/lookup`, `/{slug}/versions` and
   `/{slug}/versions/{version}/rows` as `WORKSPACE` (`:135`–`:138`); none is in
   `KNOWN_SCOPE_GAPS`. `api/reference_tables.py`:50 `ReadDatasets = requires(DATASET_READ)` is
   unchanged by this slice. The guard's negative control
   (`test_the_guard_does_not_flag_the_environment_or_workspace_wide_routes`) covers `GET
   /api/v1/reference-tables`.
3. **Blob staging is `WORKSPACE` in the guard, not a gap.** `POST /api/v1/blobs/upload-url` and
   `POST /api/v1/blobs/uploads/{upload_id}/complete` are `ROUTE_SCOPES` `WORKSPACE` rows (`:140`–`:141`),
   gated by `api/blobs.py`:52 `WriteDatasets = requires(DATASET_WRITE)` with no resource. RL 8182
   rules them "held under any scope". The guard cannot see this gap (DP-4).
4. **The guard's predicate 2 drops a check whose permission is a variable.** `_check`
   (`:279`) sets `permission=None` unless the `permission=` argument is an attribute
   (`Permission.DATASET_READ`), and `predicate_2` (`:358`) keeps only checks with
   `c.permission in COVERED_PERMISSIONS`. A shared helper written as
   `require_permission(..., permission=permission, resource=ResourceRef(...))` is therefore
   invisible to predicate 2, and every route using it stays red with "no check names a DATASET
   resource". `_NOT_FOLLOWED` (`:61`) excludes `app.platform.rbac` and `app.api.authz`, so a
   helper there is invisible too (DP-2).
5. **The coverage control is dynamic.** `test_the_resolver_finds_exactly_the_functions_that_build_a_resource`
   (`:515`) compares the functions enclosing `grep -rn "ResourceRef(" backend/src/app
   --include=*.py` (minus `platform/rbac.py`) with the functions the resolver reaches from any
   route. Each new helper that builds a `ResourceRef` must be reached by at least one route, or
   that test goes red.
6. **`_scoped`** (`api/dataset_versions.py`:73) loads a version in the caller's workspace or raises
   404 `NOT_FOUND`. Every Dataset Version handler already calls it; `compare` calls it for
   `version_id` and `against` (`:313`–`:314`).
7. **FD 8184's sites.** `api/dislocation_runs.py`:50 `_require_dataset_read(database, caller)`
   calls `rbac.require_permission(..., permission=Permission.DATASET_READ,
   credential_permissions=caller.permissions)` with **no resource**; called at `:79`
   (`estimate_dislocation_run`), `:105` (`start_dislocation_run`) and `:167`
   (`get_dislocation_run_movers`). The portfolio id is
   `DislocationSpec.portfolio_dataset_version_id` (`packages/model-schema/src/model_schema/dislocation.py`:47)
   on estimate and start, and `row.portfolio_dataset_version_id` on the stored run (movers,
   `:168`–`:171`). `api/rate_tables.py`:430–437 (diff) and :528–535 (diff cells) do the same
   when `portfolio` is given.
8. **`03` §5.1 already states the order for the diff routes.** `03-rating-engine.md`:1060–1061:
   "**403** without `dataset:read`, the same for any id, **404** `NOT_FOUND` for a portfolio that
   is missing or in another workspace, **409** `DATASET_NOT_VALIDATED` [...]". Held-anywhere
   first, then load, then the scoped check fits it with no `03` text change.
9. **The routes' current gates and handlers** (route decorator line → handler def):

   | # | Route | File:line → def | Gate today | Loads |
   |---|---|---|---|---|
   | 1 | `POST /api/v1/dataset-versions/{version_id}/validate` | `dataset_versions.py`:130 → :136 | `ValidateDatasets` (:62) | `_scoped` |
   | 2 | `GET /api/v1/dataset-versions/{version_id}/validation-reports` | :168 → :173 | `ReadDatasets` (:60) | `_scoped` |
   | 3 | `POST /api/v1/dataset-versions/{version_id}/transition` | :203 → :208 | `ValidateDatasets` | `_scoped` |
   | 4 | `GET /api/v1/dataset-versions/{version_id}/profile` | :263 → :266 | `ReadDatasets` | `_scoped` |
   | 5 | `GET /api/v1/dataset-versions/{version_id}/one-ways` | :277 → :282 | `ReadDatasets` | `_scoped` |
   | 6 | `GET /api/v1/dataset-versions/{version_id}/compare` | :296 → :301 | `ReadDatasets` | `_scoped` ×2 (`against`) |
   | 7 | `POST /api/v1/dataset-versions/{version_id}/derive` | :332 → :338 | `WriteDatasets` (:61) | `_scoped` |
   | 8 | `GET /api/v1/dataset-versions/{version_id}/lineage` | :372 → :375 | `ReadDatasets` | `_scoped` |
   | 9 | `GET /api/v1/dataset-versions/{version_id}/rejected` | :413 → :418 | `ReadDatasets` | `_scoped` |
   | 10 | `POST /api/v1/dataset-versions/{version_id}/splits` | :467 → :473 | `WriteDatasets` | `_scoped` + each of `SplitRequest.parts` |
   | 11 | `GET /api/v1/dataset-versions/{version_id}/splits` | :505 → :510 | `ReadDatasets` | `_scoped` |
   | 12 | `GET /api/v1/datasets/{slug}` | `datasets.py`:433 → :436 | `ReadDatasets` (:87) | by slug |
   | 13 | `POST /api/v1/datasets/{slug}/versions` (ingest) | :515 → :521 | `WriteDatasets` (:88) | by slug |
   | 14 | `GET /api/v1/datasets/{slug}/versions` | :588 → :593 | `ReadDatasets` | by slug |
   | 15 | `GET /api/v1/datasets/{slug}/versions/{version}` | :647 → :652 | `ReadDatasets` | by slug |
   | 16 | `GET /api/v1/dataset-versions/{version_id}` | :662 → :667 | `ReadDatasets` | by id |
   | 17 | `PATCH /api/v1/datasets/{slug}/versions/{version}/schema` | :751 → :756 | `WriteDatasets` | by slug |
   | 18 | `GET /api/v1/validation-reports/{report_id}` | `validation.py`:138 → :143 | `ReadDatasets` (:67) | report → version |
   | 19 | `GET /api/v1/datasets/{slug}/rule-set` | :412 → :417 | `ReadDatasets` (:67) | `load_dataset` (:424) |
   | 20 | `GET /api/v1/blobs/{sha256}` | `blobs.py`:156 → :163 | `ReadDatasets` (:50) | `BlobRow`, owners |
   | 21 | `POST /api/v1/dislocation-runs/estimate` | `dislocation_runs.py`:64 → :69 | `CompileDep` + `_require_dataset_read` :79 | spec's portfolio |
   | 22 | `POST /api/v1/dislocation-runs` | :86 → :92 | `CompileDep` + :105 | spec's portfolio |
   | 23 | `GET /api/v1/dislocation-runs/{run_id}/movers` | :152 → :157 | `ReadDep` + :167 | stored run's portfolio |
   | 24 | `GET /api/v1/rate-tables/{slug}@{version}/diff` | `rate_tables.py`:430–437 (in-handler) | rating gate + no-resource `dataset:read` | `portfolio` query |
   | 25 | `GET /api/v1/rate-tables/{slug}@{version}/diff/cells` | :528–535 (in-handler) | rating gate + no-resource `dataset:read` | `portfolio` query |
   | 26 | `POST /api/v1/blobs/upload-url` | `blobs.py`:69 → :74 | `WriteDatasets` (:52) | none |
   | 27 | `POST /api/v1/blobs/uploads/{upload_id}/complete` | :110 → :116 | `WriteDatasets` | none |

   Rows 1–20 are the 20 `RL-8182` gap rows, rows 21–25 the 5 `FD-8184` gap rows; rows 26–27 are
   RL 8182's "held under any scope" routes, which hold no gap row. **27 routes in all.**
   `validation.py`:67's alias also guards `GET /api/v1/validation-rules` (:212), which names no
   Dataset and stays `WORKSPACE` (RL 8182 item 4: "The list routes [...] stay workspace-wide").

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | RL 8182 "What it obliges" item 1's spec text — the FR-345 "**Where a dataset scope reaches**" clause and the `06` §3 `dataset:read` row's "and Reference Tables, workspace-wide only (FR-345)" — is on **no branch** (below). Who writes it, and when? | (a) the docs batch that mints RL 8182, as RL 8182 says · (b) this slice, Task 1, spec first · (c) leave it out | **(a)**, with this slice's Task 1 as a precondition check | decision point | yes (spec first) | — |
| DP-2 | The shape of the scoped check for 25 routes | (a) inline in each handler or service · (b) three literal-permission helpers in one followed module · (c) one generic `permission=` helper | **(b)** (below) | design | yes | — |
| DP-3 | Is a load 404 counted (FR-452)? | (a) no: count after the scoped check, as ruled for SL 8185 · (b) yes: count the 404 too; only the scoped 403 is uncounted · (c) split by grant kind | **(b)** (below) | decision point (spec vs code) | yes | — |
| DP-4 | The guard cannot see rows 26–27 (blob staging) | (a) red-first tests only; the guard's tables unchanged · (b) a new guard category for "held anywhere, no handler check" | **(a)** (below) | design | no | — |

### DP-1 — RL 8182's own spec text is not on any branch

Measured by this seat on 2026-10-22, between 18:10:59 and 18:15:43 BST, predicate `grep -c 'Where a dataset scope reaches'` over
`git show <ref>:docs/specs/06-governance.md`: **0** on `origin/main` (`71e481fa`), **0** on
`origin/docs/batch-fd1842-oq-gaterows` (`39c4ae25`), **0** on
`origin/sl-8185-wk1178-fd8177-scoped-writes` (`40de35f5`). The batch's `06` diff touches only
FR-343 (RL 8176's clause). `06`:273's `dataset:read` row on `origin/main` has no Reference Table
text. SL 8185 writes the **order** clause in FR-345 and the FR-343 pointer (its commits
`40015b55`, `9b6c21bd`, `f1454fc1`), which RL 8182 item 1's second bullet and the 17:38:11 DP-2
cover. RL 8182 item 1's **first** bullet ("Where a dataset scope reaches") and fourth bullet
(the §3 row) are written by nobody yet. So the brief's "RL 8182 obliges none of its own beyond
what SL 8185 writes" is **not confirmed**.

- **(a)** The batch writes both, in the commit that mints RL 8182 (RL 8182 item 1: "by the
  decision-maker, in the batch PR that mints this record (spec first, with the record in the
  same commit)"). It keeps the record and its spec text together, and it lands before any code.
- **(b)** This slice writes both as Task 1. It works, but the record and its spec text land in
  different PRs, against RL 8182's own wording.
- **(c)** Code without its spec: refused by `CLAUDE.md` §0 ("Spec change first").

**Recommendation: (a).** This slice's Task 1 then only verifies the text is on `origin/main`
(the grep above returns 1) and STOPs if not. If the batch has already merged without it when
the slice is dispatched, the lead decides between a batch follow-up and (b).

### DP-2 — the scoped-check helpers

The guard decides the shape (*Verified* items 4–5). A generic helper with
`permission=permission` is invisible to predicate 2, and a helper in `rbac.py` or `authz.py` is
not followed.

- **(a) Inline**, as SL 8185 did in `update_dictionary`: 25 copies of the same five lines.
- **(b) Three helpers** in a new module `backend/src/app/platform/dataset_scope.py` (followed:
  `app.platform.*`), each with its own literal call:

  ```python
  async def require_dataset_read_on(
      session: AsyncSession, caller: Caller, dataset_id: UUID,
      count_management: Callable[[], Awaitable[None]] | None = None,
  ) -> None:
      """`dataset:read` on this Dataset (FR-345's order: the route gate already checked it is
      held anywhere; the caller loaded the Dataset). 403 `SCOPE_DENIED` otherwise. Counts after
      the check, so a 403 is never counted (FR-452)."""
      await rbac.require_permission(
          session,
          workspace_id=caller.workspace_id,
          principal=caller.principal,
          permission=Permission.DATASET_READ,
          resource=rbac.ResourceRef(scope_type=ScopeType.DATASET, scope_id=dataset_id),
          credential_permissions=caller.permissions,
      )
      if count_management is not None:
          await count_management()
  ```

  and `require_dataset_write_on` / `require_dataset_validate_on`, identical but for the
  literal permission. `Caller` is `app.api.deps.Caller`; if import-linter refuses
  `app.platform` → `app.api`, the helpers take `workspace_id`, `principal` and
  `credential_permissions` instead (the executor quotes `lint-imports`' rc). Each helper is
  reached by at least one route, so the coverage control stays green.
- **(c) One generic helper:** fails predicate 2 on every route (*Verified* item 4); changing the
  predicate breaks PL 8181's rule that a follow-on slice "changes **only the tables**".

**Recommendation: (b).** One place for the check and the count, and the guard sees every
call. `credential_permissions=caller.permissions` is passed as `dislocation_runs.py`:58 does
today; it changes nothing for a dataset permission (`rbac.py`:196–201: a credential holds only
`score:*`).

### DP-3 — a 404 from the load: counted or not (FR-452)

`07` FR-452 (`07-platform.md`:184, RL-1687): "The count runs after authentication and after the
route's own permission check [...] so a `401` or a `403` is never counted, and before the route
does any work." Only a 401 or a 403 is uncounted. Under the 17:38:11 ruling ("services count
after their scoped check") a load 404 comes **before** the count, so it is not counted. That is
already true of SL 8185's three routes (`update_dictionary`: `load_dataset` raises before
`count_management`). For this slice's 25 routes it means that an unknown-id probe by a
permission holder is never rate-limited. That is a spec-vs-code disagreement, which the planner
does not rule (`delivery-process.md` §3).

- **(a)** Keep the ruled pattern and record it: a dated FR-452 sentence ("a `404` from the
  lookup a scoped check needs is not counted"). Spec change only.
- **(b)** Count the 404 too: the handler awaits the count before it raises a load `NOT_FOUND`,
  and after the scoped check passes. Only the scoped 403 is uncounted, which is FR-452's letter.
  A blob refused as 404 is counted like an unknown blob, so the two stay indistinguishable.
- **(c)** Count right after the gate for a workspace-wide holder, after the scoped check for a
  scoped one. Two paths; the count timing then tells the two kinds of holder apart.

**Recommendation: (b)**, applied to this slice's 25 routes. If ruled, SL 8185's three routes
need the same change (one `except`/count line each); the lead decides whether that is SL 8185's
follow-up or this slice's (its write set already holds `platform/datasets.py` and
`platform/validation.py`). Under (a) the R-scoped-unknown-id tests assert "not counted"; under
(b), "counted".

### DP-4 — blob staging is invisible to the guard

Rows 26–27 move to `requires(DATASET_WRITE, held_anywhere=True)`. RL 8182 rules that they check
no Dataset; the Dataset is checked at ingest (row 13). Their `ROUTE_SCOPES` rows are
`WORKSPACE`, and predicate 2 fails a `WORKSPACE` row only if it reaches a scoped check. So the
guard is green whether or not the gate is held-anywhere.

- **(a)** Red-first HTTP tests pin it (the scoped principal gets 200/201 on both). No table
  change.
- **(b)** A new guard category. It edits the predicates, which PL 8181 reserves to SL 8185.

**Recommendation: (a).** The tests are the guard for these two routes. The row comment at
`:139` ("Upload is "held under any scope" [...]") already records the reason.

## The slice (one row under WK-1178; SL / LG ids from the lead at the GO)

- **Title:** WK-1178 fix slice — RL 8182 + FD 8184: a dataset-scoped grant reaches every route
  that acts on one Dataset (FR-345), the portfolio `dataset:read` is checked on the portfolio,
  and the 25 owned `KNOWN_SCOPE_GAPS` rows are deleted.
- **Requirements:** `06` FR-345 (both dated clauses: SL 8185's order clause and RL 8182's
  "Where a dataset scope reaches", DP-1), FR-343 (the order, unchanged), FR-350 (closed default:
  list routes stay workspace-wide); `03` FR-263 and §5.1 :1060, :1061, :1080, :1083 (the
  portfolio check); `01` FR-63 (`compare`, both versions checked) and FR-76 (`splits`, every
  part checked); `07` FR-452 (DP-3).
- **Dependencies, all before Task 2:** (1) **SL 8185 merged to main** (the helper
  `requires(..., held_anywhere=True)`, `RESOURCE_CHECKED_IN_HANDLER_ATTRIBUTE` and
  `test_route_scope_guard.py` exist only on its branch at `40de35f5`); (2) **the docs batch that
  mints RL 8182 (RL 1849) and FD 8184 (FD 1853) merged**, carrying DP-1's text if ruled (a);
  (3) DP-1..DP-3 ruled.
- **Queue:** behind P2 row work and open P2 HIGHs (17:46:43 item 2). See *The carry rule*.
- **Lane / order:** backend, one executor. Shares `api/datasets.py`, `api/validation.py`,
  `platform/datasets.py`, `platform/validation.py` and `test_route_scope_guard.py` with SL 8185,
  so it starts only after SL 8185 merges ("shared files are sequenced, not concurrent").
- **Write set:** `backend/src/app/platform/dataset_scope.py` (new, DP-2);
  `backend/src/app/api/dataset_versions.py`; `backend/src/app/api/datasets.py`;
  `backend/src/app/api/validation.py` (the `get_report` and `get_rule_set` handlers and the
  `ReadDatasets` alias's users; not `put_rule_set`, which is SL 8185's Task 4);
  `backend/src/app/api/blobs.py`; `backend/src/app/platform/blobs.py` (the scope-aware owner
  check); `backend/src/app/platform/validation.py` (only if `get_report` needs the version's
  Dataset id from `load_report_view`); `backend/src/app/api/dislocation_runs.py`;
  `backend/src/app/api/rate_tables.py`; `backend/tests/test_route_scope_guard.py`
  (**`KNOWN_SCOPE_GAPS` rows only**); three new test files (Task 2). DP-3 (b), if ruled and
  assigned here: `platform/datasets.py` and `platform/validation.py`'s count lines. DP-1 (b),
  if ruled: `docs/specs/06-governance.md`, FR-345's row and `:273` only.
  **Not** in the write set: `platform/validation_rules.py` (SL-1736); `platform/rbac.py`;
  `api/authz.py`; `api/reference_tables.py`; `test_api_authorisation_sweep.py`;
  `test_management_429_declared.py`; any `docs/specs/` text other than DP-1 (b).

## Tasks

Test-first: each red is shown at base before its fix, with the rc and every `FAILED` line in the
ledger. DB-backed tests run only through `run-small.sh` (≤3 files), in DB windows the lead
grants. "Base" below is `origin/main` after the dependencies have merged, plus the task's test
file only.

1. **Spec precondition** (`spec-change`). Re-merge main. Run
   `git -C <wt> show origin/main:docs/specs/06-governance.md | grep -c 'Where a dataset scope reaches'`
   and `grep -c 'Order, for a dataset-scoped check'` on the same file. Both must print `1`.
   Otherwise STOP and report (DP-1). Quote both outputs in the ledger.
2. **Red tests**, in three new files built on SL 8185's `world` fixture
   (`backend/tests/test_dataset_scoped_writes.py`:81, Datasets X and Y in one workspace) and its
   `limited_client` / `limit_two` count fixtures (:270, :278):
   - `backend/tests/test_dataset_version_scope.py`: rows 1–11 and 20, 26, 27;
   - `backend/tests/test_dataset_read_scope.py`: rows 12–19;
   - `backend/tests/test_portfolio_dataset_scope.py`: rows 21–25.

   For **each of rows 1–25**, a principal whose grant is scoped to X only (`analyst` for read
   and write; a role holding `dataset:validate` for rows 1 and 3):
   - **R-in-scope:** on X → the route's success code (200 / 201 / 202; row 20: 307). Red at
     base: 403 `PERMISSION_DENIED`.
   - **R-out-of-scope:** on Y → 403 with `code == "SCOPE_DENIED"` (row 20: 404 `NOT_FOUND`, the
     same body as an unknown blob). Red at base: `PERMISSION_DENIED`. For rows 21–25 this is the
     control the 17:41:48 entry requires: it asserts the code, not only the status.
   - **R-scoped-unknown-id:** an unknown id or slug (rows 21–22: an unknown
     `portfolio_dataset_version_id`; row 23: an unknown `run_id`; rows 24–25: an unknown
     `portfolio`) → 404 `NOT_FOUND`, and the count as DP-3 rules. Red at base: 403.
   - **R-count-scoped:** with `limit_two`, the refusal on Y twice, then a third request: the
     refusals carry the R-out-of-scope code and are not counted (FR-452). Red at base on the
     code.
   - **R-workspace:** a workspace-wide holder on X → success. Green at base; stays green.
   - **R-no-grant:** a member holding the permission nowhere, unknown id → 403
     `PERMISSION_DENIED` (FR-343's order; rows 21–25: a principal with the rating permission but
     no `dataset:read`). Green at base; stays green.

   **Extra cases:**
   - **compare-against-Y** (row 6): `version_id` in X, `against` in Y → 403 `SCOPE_DENIED`. Red.
   - **split-part-in-Y** (row 10): parent in X, one of `parts` in Y → 403 `SCOPE_DENIED`. Red.
   - **upload-url-scoped** (row 26) and **complete-scoped** (row 27): the X-scoped `dataset:write`
     principal → success. Red. Row 13's R-in-scope uses this principal's own upload, so the
     staged-then-ingested flow of RL 8182 item 3 is covered end to end.
   - **job-blob-scoped** (row 20): a blob owned only by a Job's result → 404 for the scoped
     principal. Red at base (403). **job-blob-workspace:** 307 for a workspace-wide holder. Green.
   - **upload-no-grant** (rows 26, 27): 403 `PERMISSION_DENIED`. Green, two tests.
   - **reference-tables-pinned:** the X-scoped `dataset:read` principal on `GET
     /api/v1/reference-tables` → 403 `PERMISSION_DENIED` (RL 8182 item 3's last case). Green.

   **The red set is 105 tests:** 4 × 25 (R-in-scope, R-out-of-scope, R-scoped-unknown-id,
   R-count-scoped) + compare-against-Y + split-part-in-Y + upload-url-scoped + complete-scoped +
   job-blob-scoped. **The green-at-base set is 54:** 2 × 25 (R-workspace, R-no-grant) +
   job-blob-workspace + 2 upload-no-grant + reference-tables-pinned. Show the 105 red (rc 1, each
   `FAILED` line quoted; the per-file `N failed, M passed` lines must sum to 105 failed and 54
   passed) and the 54 green. If a test cannot be red at base, the ledger says which and why, and
   the count is corrected there, never silently.
3. **The helpers** (DP-2): `backend/src/app/platform/dataset_scope.py` with
   `require_dataset_read_on`, `require_dataset_write_on`, `require_dataset_validate_on`.
4. **Dataset Version routes (rows 1–11).** In `api/dataset_versions.py`, replace the three
   aliases at :60–62 with `requires(..., held_anywhere=True)` versions. Each handler takes
   `count: Annotated[CountAfterCheck, Depends(management_counter)]`, calls `_scoped`, then the
   matching helper with `row.dataset_id` and `count`, before any work. `compare` checks
   `against`'s Dataset too; `record_split` checks every `parts` value's Dataset. Count once per
   request (the helper's `count_management` only on the last check).
5. **Single-Dataset dataset and validation routes (rows 12–19).** In `api/datasets.py`, a
   held-anywhere `ReadNamedDataset` alias and SL 8185's `WriteNamedDataset` (it exists after SL
   8185); `ReadDatasets` and `WriteDatasets` stay for the list and create routes (`:171`,
   `:206`, `:258`, `:274`, `:300`, `:454`). In `api/validation.py`, a held-anywhere alias for
   `get_report` and `get_rule_set`; `list_rules` keeps `ReadDatasets`.
6. **Blobs (rows 20, 26, 27).** Rows 26–27: `requires(DATASET_WRITE, held_anywhere=True)` plus
   `management_counter`, counted at the start of the handler (no scoped check; RL 8182).
   Row 20: a held-anywhere `dataset:read` gate; in `platform/blobs.py`, a scope-aware owner
   check beside `blob_readable_by` (`:703`): a workspace-wide `dataset:read` keeps today's answer;
   otherwise the blob is readable only if some owning Dataset Version's Dataset passes
   `rbac.has_permission(..., permission=Permission.DATASET_READ, resource=ResourceRef(DATASET,
   dataset_id))` (a literal permission, so the guard sees it). A refusal raises
   `blob_not_found(sha256)` (`:697`), the same 404.
7. **Portfolio routes (rows 21–25), FD 8184.** In `api/dislocation_runs.py`,
   `_require_dataset_read(database, caller, portfolio_dataset_version_id, count)`: held anywhere
   (`rbac.holds_anywhere`, else 403 `PERMISSION_DENIED`), then load the version (404), then
   `require_dataset_read_on(..., version.dataset_id)`. Estimate and start pass
   `spec.portfolio_dataset_version_id`; movers first fetches the run (404 for an unknown
   `run_id`), then passes `row.portfolio_dataset_version_id`. In `api/rate_tables.py`, the same
   three steps at :430–437 and :528–535 on the `portfolio` query parameter. **The count moves
   too.** Today the rating gates (`dislocation_runs.py`:38 `CompileDep`, :39 `ReadDep`;
   `rate_tables.py`:59 `RatingReadDep`) count at the gate, so a `SCOPE_DENIED` from the dataset
   check would be counted, against FR-452. Rows 21–25 therefore use
   `requires(<rating perm>, management_counted=False)` aliases of their own plus
   `management_counter`, and count after the dataset check (DP-3 applies as on the other rows);
   the rate-table diff routes called **without** `portfolio` count right after the gate, as
   today. The shared aliases stay unchanged for every other route that uses them.
8. **Delete the 25 gap rows.** After each route group is green, delete its `KNOWN_SCOPE_GAPS`
   rows from `test_route_scope_guard.py` (`test_every_known_gap_still_fails` forces it: it goes
   red for a fixed route until the row is gone). At the slice head `KNOWN_SCOPE_GAPS` holds only
   SL 8185's rule-set row, if SL 8185's Task 4 has not landed, and no `RL-8182` or `FD-8184`
   row. Quote `grep -c -E '"(RL|FD)-81(82|84)"' backend/tests/test_route_scope_guard.py`
   (expected `0`) and the remaining row count.
9. **GREEN by import closure** (common brief item 29): changed modules from `git diff
   --name-only origin/main...HEAD -- backend/src`, their importers, one more level of importers,
   then every test file importing the closure. It must include `test_route_scope_guard.py`,
   `test_api_authorisation_sweep.py`, `test_management_429_declared.py`, `test_rbac.py`,
   `test_dataset_scoped_writes.py` and the three new files. Run each through `run-small.sh`,
   quote the commands and the list in the ledger. Then the full code gate on the lead's grant.

## Acceptance Standard

1. At base, the three new test files exit 1 through `run-small.sh`, and their `N failed, M
   passed` summary lines sum to **105 failed, 54 passed** (or the ledger's corrected count,
   with the reason per test). At the slice head all three exit 0.
2. At the slice head, `grep -c -E '"(RL|FD)-81(82|84)"' backend/tests/test_route_scope_guard.py`
   prints `0`, and `test_route_scope_guard.py` exits 0, including
   `test_every_known_gap_still_fails` and
   `test_the_resolver_finds_exactly_the_functions_that_build_a_resource`.
3. `git diff origin/main...HEAD -- backend/tests/test_route_scope_guard.py` changes only lines
   inside `KNOWN_SCOPE_GAPS` (`:151`–`:188` at `40de35f5`).
4. `git diff --stat origin/main...HEAD -- backend/tests/test_api_authorisation_sweep.py
   backend/tests/test_management_429_declared.py backend/src/app/api/reference_tables.py
   backend/src/app/platform/validation_rules.py` is empty, and the first two exit 0 at the
   slice head.
5. `uv run lint-imports` exits 0 (DP-2's module boundary).
6. The full code gate (both halves, `dev-commands`), on the lead's grant, is green at the slice
   head; the MERGE-ACK quotes its `passed` line and its frontend `Test Files N passed` line.

## The carry rule (17:46:43 item 2)

The slice lands before P2's close if capacity allows. Otherwise it is **carried to WK-676**, owner
WK-676, condition **"before POST /role-assignments ships"**, by a dated line on WK-1178's and
WK-676's roadmap rows. It is never dropped silently. The line, for the lead or the maintainer to
fill and date:

> *(Dated line, 2026-__-__, the maintainer: PL-8190's slice is CARRIED from WK-1178 to WK-676,
> owner WK-676, condition "before POST /role-assignments ships" (the maintainer's entry
> "2026-10-22 17:46:43 BST" item 2). Reason: P2 closes on __ with the slice not started/not
> merged. FD-8184 (FD 1853) and RL-8182 (RL 1849) move with it; their `KNOWN_SCOPE_GAPS` rows
> are re-owned to WK-676's slice in the same change.)*

**Trigger for the lead:** when P2's exit demo is scheduled and this slice has no GO yet, the
lead raises carry-or-land with the maintainer, before the phase review (`CLAUDE.md` §14). The
guard rows stay owned either way, so `test_every_known_gap_names_an_owner_in_the_index` keeps
them visible.

## Clashes and sequencing

- **SL 8185** (`sl-8185-wk1178-fd8177-scoped-writes` @`40de35f5`): shares `api/datasets.py`,
  `api/validation.py`, `platform/datasets.py`, `platform/validation.py` and
  `test_route_scope_guard.py`. Sequenced: this slice starts after SL 8185 merges.
- **SL-1736** (`sl-1736-wk1178-nfr-sweep` @`d235c8a6`): `git diff --name-only origin/main...` names
  `backend/src/app/platform/validation_rules.py`, which is not in this write set (row 19 checks
  in `api/validation.py`, beside `load_dataset`).
- **SL-1260** (`sl-1260-wk674-s6` @`eaf045d2`): its diff names `docs/specs/03-rating-engine.md`
  among this plan's files of interest. This slice writes no `03` text, so no overlap.
- **Other in-flight branches:** not swept at this commit. The all-branch sweep was paused because
  gate slots were held (gate-1b and gate-2 at 18:15:43 BST; the sweep-pause rule). It is owed
  before the GO: `git diff --name-only origin/main...<b>` for every `git ls-remote --heads
  origin` branch, filtered to this write set.

## Out of scope

- SL 8185's rule-set route (`PUT /api/v1/datasets/{slug}/rule-set`, its Task 4) and its
  `KNOWN_SCOPE_GAPS` row.
- Reference Tables (unchanged, RL 8182).
- `MODEL_FAMILY` and `RATING_ALGORITHM` scopes (`06` FR-345, WK-676, the 17:46:43 item 3).
- Any change to the guard's predicates or resolver (PL 8181: a follow-on edits only the tables).

## Self-review before freeze

- Every route, line and code above was re-read at `71e481fa` or `40de35f5` by this planner.
  The 26-row `KNOWN_SCOPE_GAPS` split (1 / 20 / 5) and the four `WORKSPACE` reference-table rows
  were read in the guard file itself.
- Each 17:36:24, 17:41:48 and 17:46:43 obligation maps to a task: items 1–2 → Tasks 4–6; FD 8184
  → Task 7; the guard rows → Task 8; the carry → *The carry rule*.
- RL 8182 "What it obliges" item 3's four acceptance cases map to Task 2: the profile route's
  R-in-scope / R-out-of-scope / R-no-grant, the upload-then-ingest flow, the blob 307/404, and
  reference-tables-pinned.
- DP-1..DP-3 are open, so the status is `draft`. The ids 8190, 8182, 8184 and 8185 are working
  ids, so `audit-docs.py` check 32 reports this file's rows until the mint.
