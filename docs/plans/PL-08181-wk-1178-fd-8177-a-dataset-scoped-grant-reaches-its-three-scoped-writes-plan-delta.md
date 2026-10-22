---
id: PL-8181
family: plan
kind: map
title: WK-1178 — FD 8177, a dataset-scoped grant reaches the three writes whose handler checks the Dataset (dictionary, rule set, acknowledgement), and a permanent guard against the pattern — a dated Work-plan delta cutting one slice
status: draft                  # draft → active → superseded | retired (§1.2a) — draft: DP-0, DP-3 and DP-4 are blocking and open (DP-1 and DP-2 resolved by the maintainer's 2026-10-22 17:36:24 BST entry, RL 8182)
created: 2026-10-22
owner: planner
tree: 71e481fa5d240ed366cd80c1a8c6cf6cd1d918d5
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [RL-1301, RL-1687, FR-343, FR-345, FR-46, FR-51, FR-452, FR-263]
---

# PL-8181 — WK-1178: FD 8177, a dataset-scoped grant reaches its three scoped writes

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md`
> §1.6, PL row). It cuts **one fix slice** (its `SL-` id and its `LG-` id are not reserved
> yet; this draft calls the slice **"the slice"**). The executor is spawned from
> `.claude/roles/executor.md` and binds `test-driven-development`, `python-test`,
> `python-package`, `fastapi-service`, `spec-change`, `dev-commands` and `git-hygiene`. The
> ledger is filed by the executor at build; this plan names it and does not create it.
> Written by planner-8177 (Claude Opus 5.5), 2026-10-22, at tree `71e481fa` (origin/main).

## The ruling this plan carries out

The maintainer's entry "2026-10-22 17:27:15 BST — Maintainer: FD 8177 CONFIRMED HIGH; planner
GO for the fix slice; the FR-345 spec question goes to a decision-maker in parallel" in
`to-lead.md`, verbatim (the binding conditions):

> - **No objection to the route:** release exec-8177, then seat a planner (opus) to cut ONE fix slice covering the 3 swept routes (api/datasets.py:88; api/validation.py:68 and :70) and to name the owner Work. Conditions:
>   - **red-first for ALL THREE routes** (the 2 unprobed ones get their own failing tests at base);
>   - the control on dataset Y must assert **SCOPE_DENIED** from the handler, not the route's PERMISSION_DENIED (the caveat raised);
>   - **a regression guard:** a test that FAILS if any route pairs a scope-less route-level `requires()` with a handler-level scoped check (the sweep's predicate, made permanent), red-first via an injected route;
>   - **sequenced around SL-1736's Task 1** edits to validation_rules.py (no shared-file overlap in flight).

And from the entry "2026-10-22 17:21:38 BST" item 4: severity **HIGH**, "owner = the Work owning
datasets RBAC", "The fix is a slice cut by a planner". FD 8177 is a P2 HIGH, "resolved before
P2's close (§14)" (17:27:15).

**Revised 2026-10-22, before any merge, on RL 8182's adoption.** The maintainer's entry
"2026-10-22 17:36:24 BST — Maintainer: RL 8182 ADOPTED, option (C); the other single-Dataset
routes join its slice; the id-oracle residual ACCEPTED; FD 8184 probe GO" (RL 8182 draft
`draft/rl-8182` @`a0e4a6d7`), items quoted verbatim where they bind this plan:

> **Order: holds_anywhere → 403; load → 404; scoped → SCOPE_DENIED.** It applies to PL 8181's 3 routes too, and it is one more dated FR-343 sentence, minted with RL 8176's clause (one docs change, both sentences). **Owner:** WK-1178; **its own slice AFTER PL 8181's** (shared files are sequenced, not concurrent).

> 3. **The residual** (SCOPE_DENIED after load reveals that an id exists to a holder scoped to another Dataset): **ACCEPTED**, consistent with RL 8176 (A)'s reasoning (a workspace-internal oracle to an already-privileged holder).

> 4. [...] **Extend the 17:27:15 permanent guard's predicate** to catch this shape too (a permission check with no resource where the spec names a scoped resource), or say why it cannot.

This resolves DP-1 (the order is option (b)'s) and DP-2 (the residual is accepted, and the order
sentence is the decision-maker's, in RL 8176 / RL 8182's docs batch, not this slice's). It adds
DP-4 (the guard's second shape) and makes this slice's helper and guard the ones RL 8182's
follow-on slice reuses (*Reuse*, below).

## Verified first, at `71e481fa`

Each fact read in the source at the tree above (my own reads, not the relay):

1. **The route gate.** `backend/src/app/api/authz.py`:170 `def requires(permission, *,
   keep_session=False, management_counted=True)` calls `rbac.require_permission(...)` with **no
   `resource`**, then counts the request (`:205`–`:206`), and tags the dependency with
   `PERMISSION_ATTRIBUTE` and `MANAGEMENT_COUNTED_ATTRIBUTE` (`:211`–`:212`).
2. **Why a scoped grant fails it.** `backend/src/app/platform/rbac.py`:205 `_covers`: a
   non-workspace assignment with `resource is None` returns `False` (`:208`–`:211`).
3. **The three affected routes** (exec-8177's sweep, `scratch/fd-8177/result.md`, re-read here):
   - `PUT /api/v1/datasets/{slug}/dictionary` — `api/datasets.py`:88 `WriteDatasets =
     ...requires(Perm.DATASET_WRITE)`, route `:495`, handler `:499`; the scoped check is
     `platform/datasets.py`:282–288 (`update_dictionary`, def `:266`), load first (`:281`).
     **Probed, refused**: probe `f4c0832f`, `assert 403 == 200`, `PERMISSION_DENIED`.
   - `PUT /api/v1/datasets/{slug}/rule-set` — `api/validation.py`:68 `WriteDatasets`, route
     `:430`, handler `:434`, loads the dataset then calls `rule_service.replace_rule_set` at
     `:446`; the scoped check is `platform/validation_rules.py`:824–830 (def `:808`). Unprobed.
   - `POST /api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge` —
     `api/validation.py`:70 `AcknowledgeWarnings = ...requires(Perm.DATASET_ACKNOWLEDGE_WARNING)`,
     route `:155`, handler `:160`, calls `service.acknowledge` at `:169`; the scoped check is
     `platform/validation.py`:258–266 (`has_permission`, resource the version's dataset), def
     `:226`. Unprobed. **On refusal it raises `ACKNOWLEDGE_FORBIDDEN_ROLE`** (`:274`–`:280`),
     never `SCOPE_DENIED` — see DP-3.
4. **`rbac.holds_anywhere` exists** (`rbac.py`:219): "Does the principal hold this permission
   under any scope?" It reads role assignments only; it does not take `credential_permissions`.
5. **The handler-counted pattern exists.** `authz.py`:155 `management_counter` returns the count
   unrun; the service awaits it right after its own permission check, "so a `403` is never
   counted". Used by `platform/validation_rules.py`:200/`:230` (`count_management`) and
   `platform/deployments.py`:139. The rule is `07` FR-452 as amended by `RL-1687` (1a): "The
   count runs after authentication and after the route's own permission check ... so a `401`
   or a `403` is never counted, and before the route does any work."
6. **The sweep tests.** `backend/tests/test_api_authorisation_sweep.py`:
   `HANDLER_GUARDED` (`:83`), `RESOURCE_BACKED` (`:299`, Environment paths only), the no-role
   test `:367` (asserts 403 **and** `PERMISSION_DENIED` for every route outside
   `HANDLER_GUARDED`). `backend/tests/test_management_429_declared.py`:107 `_counts` treats a
   route as counted if any dependency carries `MANAGEMENT_COUNTED_ATTRIBUTE` or is
   `management_counter`.
7. **RL 8176 (adopted, not minted; `draft/rl-8176` @`aab1b741`)** writes into `06` FR-343:
   "a route's permission check precedes any lookup of an id its path names, so a caller without
   the permission is refused with 403 whether or not the id exists. **One exception:** ... an
   **Environment**". Its reason (A) item 1: the order rule "protects ids whose existence is
   itself access-controlled, such as datasets and models". The maintainer's 17:21:38 item 2
   rules a test: **`RESOURCE_BACKED` may hold only `/api/v1/environments/{env}/` paths.**
8. **The built-in roles.** `packages/model-schema/src/model_schema/permissions.py`:137–144:
   `dataset:acknowledge_warning` is held by `pricing_actuary`, not `analyst`.

## Owner Work — **WK-1178** recommended; DP-0 confirms

Two candidates, with evidence:

| Candidate | For | Against |
|---|---|---|
| **WK-676** "Full scoped RBAC, custom roles, break-glass" (`docs/roadmap.md`:3098) | Its row lists `06` FR-342 … FR-349, **FR-345 included** (`:3110`); it is the spec owner of scoped RBAC. | `phase: P3` (`:3107`). FD 8177 is a **P2** HIGH that must be resolved before P2's close; a P3 Work cannot carry a P2 close obligation, and `CLAUDE.md` §0 forbids building ahead of the phase. |
| **WK-1178** "P2 standing maintenance: hotfixes, dependency bumps and security findings" (`docs/roadmap.md`:1916) | `phase: P2`, `status: active`; scope "work that belongs to no other Work; each item names its `FD-`". The dataset routes and their scoped checks were delivered by **WK-659** (P1a, closed 2026-08-14, `:248`), so no open P2 Work owns them. RL 8176 (adopted) puts FD 8175's sibling fix in a WK-1178 delta row. | It is not the spec owner of FR-345; the slice changes no FR-345 *scope*, only the order and the gate, so this costs nothing. |

**Recommendation: WK-1178**, with WK-676 named in the FD as the spec owner of FR-345 for any
later scoped-RBAC work. Ambiguous enough that the maintainer confirms it (DP-0).

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-0 | Which Work owns the fix? | WK-1178 · WK-676 | **WK-1178** (table above) | scope | yes | |
| DP-1 | How does a route admit a scoped grant and still refuse a caller with no grant first? | (a) B.2 pattern · (b) "held anywhere" route gate + the existing scoped check · (c) other | **(b)** (below) | decision point | yes | the maintainer's entry 2026-10-22 17:36:24 BST item 1 (RL 8182): the order holds_anywhere → 403, load → 404, scoped → `SCOPE_DENIED` |
| DP-2 | `06` text: the order for a permission that can be held on a named Dataset | (i) held-anywhere counts as "holding it" for FR-343's order; a holder on another Dataset sees 404 for an unknown slug and `SCOPE_DENIED` for an existing one · (ii) a scoped holder gets 403 for an unknown slug too | **(i)** (below) | decision point | yes | the same entry, items 1 and 3: (i), residual ACCEPTED; the sentence goes into FR-343 in RL 8176 / RL 8182's docs batch |
| DP-3 | The acknowledge refusal for a holder whose grant is on another Dataset | `SCOPE_DENIED` (`06` §5.1) · keep `ACKNOWLEDGE_FORBIDDEN_ROLE` (`01` §5.1) | **`SCOPE_DENIED`** when held elsewhere; `ACKNOWLEDGE_FORBIDDEN_ROLE` kept when held nowhere | decision point | yes | |
| DP-4 | How does the permanent guard see "a permission check with no resource where the spec names a scoped one"? | (a) a declared route → expected scope table, checked against the code · (b) derived from each spec's §5.1 permission column · (c) other | **(a), with a spec cross-check as its completeness control** (below) | decision point | yes | |

### DP-1 — the design options

| | (a) RL-1301 B.2 pattern: drop the route `requires()`, guard in the handler with the resource | (b) a "held anywhere" route gate (`requires_held_anywhere`) + the handler's scoped check | (c) a route dependency that loads the Dataset by slug and checks with the resource |
|---|---|---|---|
| **Order** | load → 404 → scoped 403. A **no-grant** caller learns whether a dataset slug or a report id exists. | held anywhere? else 403 `PERMISSION_DENIED` → load → 404 → scoped 403 `SCOPE_DENIED` | as (b), but inside the dependency |
| **RL 8176 (adopted)** | **Breaks its FR-343 order rule**: the one exception is Environments, and its reason (A) item 1 names datasets as ids whose existence is access-controlled. | Kept: a caller with no grant is refused 403 whether or not the id exists. This is exactly RL 8176's option (C) form, applied where its reason says it belongs. | Kept |
| **Sweep lists** | All three routes need `HANDLER_GUARDED` entries **and** `RESOURCE_BACKED` entries (the no-role test fills an unknown id and would get 404). The second is **forbidden** by the guard the maintainer ruled on 17:21:38 item 2. | **No change.** The route still declares its permission (`_declares_a_permission`), and a no-role caller still gets `PERMISSION_DENIED` from the route. | No change |
| **FR-452 count** | Count via `management_counter`, awaited in the service after the check. | Same: the gate must **not** count (a `SCOPE_DENIED` would then be counted, against FR-452's "a 403 is never counted"); the handler takes `management_counter` and the service awaits it after its scoped check. | The dependency counts after its own scoped check; the service's check becomes a duplicate. |
| **Churn** | three services, two sweep lists (in a file SL-1260 and FD 8175's vehicle also edit), the order clause | `authz.py` (one keyword), three route aliases, three services gain `count_management`, one service's refusal code (DP-3) | a new resolver per route kind; the acknowledge route has no slug (report → version → dataset), so a second resolver; a double load and a double check |

**Recommendation: (b).** It is the only option that keeps RL 8176's order rule without a new
exception, it needs no change to either sweep list (so no overlap with SL-1260 or the FD 8175
vehicle), it reuses `rbac.holds_anywhere` and the established `count_management` pattern, and
the scoped check stays where it is. (a) is ruled out by the adopted RL 8176 and its guard; (c)
duplicates the check.

**Shape of (b), for the executor.** The builder is `requires_held_anywhere(permission)`, named
for RL 8182's reuse (*Reuse*, below); it shares `requires()`'s core and is not a keyword flag on
it. Its dependency (1) admits if `permission.value in caller.permissions` (credential grants, as
`authz.py`:203 passes them today) or `rbac.holds_anywhere(...)` is true; (2) otherwise raises
`PermissionDeniedError(permission, None, held_elsewhere=False)` (`PERMISSION_DENIED`);
(3) **never counts** (it takes no `management_counted` argument, so a counting variant cannot be
written); (4) sets `PERMISSION_ATTRIBUTE` and `RESOURCE_CHECKED_IN_HANDLER_ATTRIBUTE`, which the
guard reads.

### DP-2 — the order clause: resolved, and not this slice's spec change

Ruled by the maintainer's 17:36:24 entry, items 1 and 3: option (i). A principal holding the
permission on another Dataset sees 404 for an unknown slug and `SCOPE_DENIED` for an existing
one. That residual is **ACCEPTED**. The sentence is "one more dated FR-343 sentence, minted with
RL 8176's clause (one docs change, both sentences)". So it is the decision-maker's docs batch
that mints RL 8176 and RL 8182 (RL 8182 "What it obliges" item 1), and this slice adds **no spec
text**. The FR-345 clause this draft first proposed is withdrawn: RL 8182's batch writes FR-345's
"Where a dataset scope reaches" clause instead. The slice builds against that text once the batch
has merged (*Clashes and sequencing*).

### Reuse — the helper and the guard RL 8182's slice inherits

RL 8182 "What it obliges" item 2: its slice "reuses that slice's refusal helper and regression
guard". So both are named here, and both are built so the follow-on slice only **adds rows**:

- **The helper:** `requires_held_anywhere(permission)` in `backend/src/app/api/authz.py`, a named
  builder over `requires(...)`'s shared core, not a keyword flag (DP-1's shape, items 1–4). It
  returns the `Caller`, never counts, and tags the dependency with `PERMISSION_ATTRIBUTE` and
  `RESOURCE_CHECKED_IN_HANDLER_ATTRIBUTE`. Its handler takes `management_counter` and passes the
  count to the service, which awaits it after the scoped check. RL 8182's eleven
  `dataset_versions.py` routes and its `datasets.py` routes use the same builder. The helper
  carries no Dataset knowledge, so an Environment or Model Family route can use it later.
- **The guard:** `backend/tests/test_route_scope_guard.py`, with two module-level tables and two
  predicates (DP-4). A follow-on slice changes **only the tables**: it deletes its
  `KNOWN_SCOPE_GAPS` rows and, if a route is new, adds its `ROUTE_SCOPES` row. The predicates
  and the AST resolver are this slice's and are not edited by a follow-on.

### DP-4 — the guard's second shape: a permission check with no resource where the spec names one

**The shape** (RL 8182 "Also found"; the maintainer's 17:36:24 item 4): `03` §5.1
(`docs/specs/03-rating-engine.md`:1080, :1083) requires "`dataset:read` on the portfolio Dataset
Version". The code checks `dataset:read` with **no resource**: `api/dislocation_runs.py`:50–60
(`_require_dataset_read`), `api/rate_tables.py`:432–437 and :530–535. A dataset-scoped grant is
refused there.

**Why the first predicate cannot see it, and why no code-only predicate can.** The first predicate
(Task 5) looks for a scope-less route gate **paired with** a scoped check. Here there is no scoped
check anywhere, so the pair does not exist. A predicate over the code alone cannot tell "checked
workspace-wide by design" (`api/reference_tables.py`:50, which RL 8182 rules stays workspace-wide)
from "checked workspace-wide by mistake" (`dislocation_runs.py`), because the two are the same
code. The difference is in the spec. So the guard needs a stated expectation for each route.

| | (a) A declared table, route → expected scope | (b) Derived from each spec's §5.1 permission column | (c) A code-side annotation on each route (`requires_held_anywhere(..., scope=ScopeType.DATASET)`) |
|---|---|---|---|
| **What it catches** | Every route whose code disagrees with its row: a declared-`dataset` route with no `ScopeType.DATASET` check reached, or with a scope-less route gate; a declared-`workspace` route that gained a scoped check. | Only rows whose prose the parser reads. The cells are free text ("`dataset:read` on the portfolio Dataset Version", "on that Dataset Version", "requires `rating:read`"), so a parser is a proxy that misses other wordings. | The same as (a), but the expectation lives beside the code it checks, so one edit changes both. It is the code attesting to itself. |
| **Completeness** | The test fails on any route that holds a `dataset:*` or `deployment:promote` permission (at the route or reached from the handler) and has no row. A new route cannot slip past it. | Bounded by the parser. | None: an unannotated route is invisible. |
| **Churn** | One table, one row per such route (the executor enumerates them at build and quotes the count in the LG). | A spec parser and a path matcher. | Every affected route's code. |

**Recommendation: (a), with (b) as a cross-check, not the source.** The table is the guard's
source of truth. A second test reads each spec's §5.1 rows (`docs/specs/0[1-7]-*.md`) and finds
every cell that names a `dataset:*` permission followed within the cell by "on" and "Dataset"
(the exact pattern is the executor's, written in the test and quoted in the LG). Each matching
route must have the table row `dataset`. **Its limit, recorded:** a spec cell that names a scope
in other words is not matched, so it is caught only by table review. The cross-check makes the
common phrasing mechanical. It does not make the table correct.

**The tables:**

- `ROUTE_SCOPES: dict[tuple[str, str], ScopeType]`: `(METHOD, path)` → `DATASET`, `ENVIRONMENT`
  or `WORKSPACE`, for every published operation whose route gate or reached check holds a
  `dataset:*` permission, `deployment:promote` or an Environment-scoped `admin:*` permission.
  Every row cites its spec line in a comment.
- `KNOWN_SCOPE_GAPS: dict[tuple[str, str], tuple[str, str]]`: `(METHOD, path)` → `(owner record,
  removing slice)`. A row means "this route fails the predicate today, the failure is owned, and
  this slice removes the row".

**Predicate 2 (the second shape).** For a route declared `DATASET` (or `ENVIRONMENT`), the guard
fails unless (1) the route gate is held-anywhere or absent, **and** (2) the AST resolver reaches a
`require_permission` / `has_permission` call whose `resource=` builds a `ResourceRef` with
`scope_type=ScopeType.DATASET` (or `ENVIRONMENT`). For a route declared `WORKSPACE`, the guard
fails if it reaches a scoped check. The resolver follows calls into `app.api.*` module-level
functions as well as `app.platform.*`, so `_require_dataset_read` (`dislocation_runs.py`:50) is
reached.

**Start green on main, with owned exclusions.** At the slice head, `KNOWN_SCOPE_GAPS` holds
exactly the routes that still fail and are owned elsewhere:

- RL 8182's routes, owner RL 8182 (once minted), removed by RL 8182's slice: the eleven
  `api/dataset_versions.py` routes; `api/blobs.py`'s GET (scoped through the owning Dataset
  Version); `api/datasets.py` ingest :515, detail :433, versions :588 / :647 / :662, schema :751;
  `api/validation.py`:67's routes. Each row's path is the published path the executor enumerates
  at build; the file:line above is RL 8182's.
- FD 8184's routes, owner FD 8184, removed by RL 8182's slice if the probe confirms (the
  17:36:24 entry item 4: "the fix joins RL 8182's slice"): `POST /api/v1/dislocation-runs`
  (`dislocation_runs.py`:105), `POST /api/v1/dislocation-runs/estimate` (:79) and
  `GET /api/v1/dislocation-runs/{id}/movers` (:167), all three through `_require_dataset_read`;
  `GET /api/v1/rate-tables/{slug}@{version}/diff` (`rate_tables.py`:432–437) and
  `GET /api/v1/rate-tables/{slug}@{version}/diff/cells` (:530–535), each when a portfolio is
  given. If the probe does **not** confirm, those rows move
  to `ROUTE_SCOPES` as `WORKSPACE`, with the probe's record cited.

**An exclusion cannot go stale.** A third test asserts that **every `KNOWN_SCOPE_GAPS` row fails
the predicate today**. The slice that fixes a route therefore turns this test red until it deletes
the row. Removal is forced, not remembered. It also asserts that every row's owner id appears in
`docs/INDEX.md` or is a working id written in hyphen form, so an owner cannot be blank.

**What the guard does not cover (recorded limit).** `ScopeType` has `MODEL_FAMILY` and
`RATING_ALGORITHM` (`packages/model-schema/src/model_schema/permissions.py`:104–105), and FR-345
names both. Nothing in `backend/src` checks either: `grep -rn 'ScopeType\.\(MODEL\|RATING\)'
backend/src` at `71e481fa` returns 0 lines. So a Model-Family-scoped grant is refused on every
model route, and the guard's table does not cover `model:*` or `rating:*` routes. This is
reported to the lead as an observation, not decided or filed here. The table's completeness rule
extends to those permissions when a Work builds those scopes.

### DP-3 — the acknowledge refusal

`platform/validation.py`:274 raises `ACKNOWLEDGE_FORBIDDEN_ROLE` ("requires the Pricing Actuary
role") for any refusal. Under (b) the route already refuses a principal who holds the
permission nowhere (`PERMISSION_DENIED`, as today), so the service's refusal is reached by an
actuary whose grant is on another Dataset, and "requires the Pricing Actuary role" is false for
them. **Recommendation:** the service raises `SCOPE_DENIED` (via `require_permission` with the
resource, or `PermissionDeniedError(..., held_elsewhere=True)`) when `holds_anywhere` is true,
and keeps `ACKNOWLEDGE_FORBIDDEN_ROLE` when it is false. `test_validation_reports.py`:134
(an analyst calling the service directly, held nowhere) keeps asserting
`ACKNOWLEDGE_FORBIDDEN_ROLE` unchanged. No `01` text changes (`06` §5.1 owns `SCOPE_DENIED`;
`01` §5.1 keeps its code).

## Goal

A principal whose `dataset:write` or `dataset:acknowledge_warning` grant is scoped to Dataset X
can use the three routes on X. On Dataset Y the handler refuses it with `SCOPE_DENIED`. A
principal holding the permission nowhere is still refused 403 `PERMISSION_DENIED` by the route,
before any lookup. No `403` is counted. A permanent guard fails on either shape: a scope-less
route gate over a scoped check reached from its handler, or a route whose reached check does not
carry the scope its `ROUTE_SCOPES` row (the spec) names. It starts green on main, with every
known failure listed and owned.

## The slice (one row under WK-1178)

- **Title:** WK-1178 fix slice — FD 8177: a dataset-scoped grant reaches the dictionary, rule-set
  and acknowledge writes (`requires_held_anywhere`), and a permanent route-scope guard.
- **Requirements:** `06` FR-343 and FR-345 (as RL 8176 / RL 8182's batch amends them; no spec
  text in this slice); `01` FR-46, FR-51 (the routes' own FRs, unchanged for workspace-wide
  grants); `07` FR-452 (no 403 counted); `03` FR-263 (only through the guard's `KNOWN_SCOPE_GAPS`
  rows for FD 8184).
- **Dependencies:** **the docs batch that mints RL 8176 and RL 8182 merged to main before Task 3**
  (the order sentence the code implements, and FR-345's "Where a dataset scope reaches" clause
  that the guard's `ROUTE_SCOPES` rows cite). **SL-1736 merged to main before Task 4.** FD 8184's
  probe result before Task 5's `KNOWN_SCOPE_GAPS` is final (its rows' owner and their table).
- **Followed by:** RL 8182's slice (WK-1178, the 17:36:24 entry item 1: "its own slice AFTER PL
  8181's"). It reuses `requires_held_anywhere` and deletes its own `KNOWN_SCOPE_GAPS` rows.
- **Lane / order:** backend, one executor; any lane free of SL-1736's files. Severity HIGH:
  dispatch next after the GO.
- **Write set:** `backend/src/app/api/authz.py`; `backend/src/app/api/datasets.py`;
  `backend/src/app/api/validation.py`; `backend/src/app/platform/datasets.py`;
  `backend/src/app/platform/validation.py`; `backend/src/app/platform/validation_rules.py` (Task
  4 only: `replace_rule_set`'s signature and its count line); new
  `backend/tests/test_dataset_scoped_writes.py`; new `backend/tests/test_route_scope_guard.py`.
  **Not** in the write set: any `docs/specs/` file (the decision-maker's batch);
  `test_api_authorisation_sweep.py` (SL-1260 and the FD 8175 vehicle edit it); `rbac.py`'s
  `_covers` (unchanged); `docs/specs/01-data-management.md` (SL-1736 edits it).

## Tasks

Test-first: each red is shown at base before its fix, with the rc in the LG. DB-backed tests run
only through `run-small.sh` (≤3 files), in a DB window the lead grants.

1. **Base.** Re-merge main. Confirm the RL 8176 / RL 8182 batch is present: `git -C <wt> grep -n
   "Order, for a dataset-scoped check" docs/specs/06-governance.md` returns one line, quoted in
   the LG. If not, stop and report.
2. **Red tests for all three routes** — `backend/tests/test_dataset_scoped_writes.py`, built from
   probe `f4c0832f`'s `test_dataset_scoped_write_probe.py` (its `world` fixture). For each route
   R ∈ {dictionary, rule-set, acknowledge}, with Datasets X and Y in one workspace:
   - **R-in-scope:** a principal whose grant is scoped to X only (`analyst` for the two writes,
     `pricing_actuary` for acknowledge, on a report of X's version with a `warn` result) →
     2xx. **Red at base:** 403 `PERMISSION_DENIED`.
   - **R-out-of-scope (the control the maintainer required):** the same principal on Y →
     403 with `code == "SCOPE_DENIED"`. **Red at base:** `PERMISSION_DENIED` from the route.
     For acknowledge, it stays red until DP-3's change.
   - **R-workspace:** a workspace-wide holder on X → 2xx. Green at base; must stay green.
   - **R-no-grant-unknown-id:** a member with no role, unknown slug / report id → 403
     `PERMISSION_DENIED` (FR-343's order). Green at base; must stay green.
   - **R-scoped-unknown-id:** the X-scoped principal, unknown slug / report id → 404
     `NOT_FOUND` (the accepted residual's other half, RL 8182). Red at base (403).
   - **Count (dictionary only):** with a management limit set, an out-of-scope `SCOPE_DENIED`
     leaves the count unchanged (`07` FR-452). Green at base; it fails if the gate counts.
   Show the nine R-in-scope / R-out-of-scope / R-scoped-unknown-id tests red at base (rc 1, each
   `FAILED` line quoted), and the rest green.
3. **The helper.** `requires_held_anywhere(permission)` in `api/authz.py`, per DP-1's shape and
   *Reuse*. Switch `api/datasets.py` `put_dictionary` and `api/validation.py` `acknowledge` to it
   plus `management_counter`; `update_dictionary` and `acknowledge` take `count_management` and
   await it right after their scoped check. Make DP-3's refusal change in `acknowledge`. **Do
   not** change `WriteDatasets` for the other routes that use it (`datasets.py`:178, `:213`,
   `:281`, `:524`, `:760`): RL 8182's slice owns the single-Dataset ones, and the rest act on no
   named Dataset.
4. **The rule-set route — starts only after SL-1736 has merged to main and the slice has
   re-merged main.** Same switch for `put_rule_set` (`api/validation.py`:434);
   `replace_rule_set` takes `count_management` and awaits it after its check.
5. **The permanent guard** — `backend/tests/test_route_scope_guard.py`, with the tables and the
   predicates of *Reuse* and DP-4:
   - **The AST resolver.** From each route's endpoint, follow calls to module-level functions
     of `app.api.*` and `app.platform.*` modules (resolved through the calling module's imports),
     to depth 3, cycle-safe. Collect each reached `require_permission` / `has_permission` call
     with its permission and its `resource=` (absent, `None`, or a `ResourceRef` with its
     `scope_type`).
   - **Predicate 1 (the 17:27:15 shape).** A route is *gated without scope* when one of its
     dependencies (recursively) carries `PERMISSION_ATTRIBUTE` and not
     `RESOURCE_CHECKED_IN_HANDLER_ATTRIBUTE`. It fails if it also reaches a scoped check.
   - **Predicate 2 (the 17:36:24 shape, DP-4 (a)).** Each route in `ROUTE_SCOPES` is checked
     against its row, as DP-4 states. Any route that holds a covered permission and has no row
     fails as *unclassified*.
   - **Exclusions.** A route in `KNOWN_SCOPE_GAPS` is skipped by both predicates, and a separate
     test asserts that **each such row still fails one of them**, so a fixed route turns it red
     until its row is deleted.
   - **Spec cross-check (DP-4's (b) as a control).** Every §5.1 cell matching the test's quoted
     pattern maps to a route whose row is `DATASET`.
   - **Coverage control (it cannot go blind).** The scoped-check sites the resolver reaches,
     over all routes, equal the functions enclosing exec-8177's predicate 2 hits, run in the test
     verbatim: `grep -rn "ResourceRef(" backend/src/app --include=*.py`, excluding
     `platform/rbac.py`. At `71e481fa` those are `platform/validation.py`:264,
     `platform/deployments.py`:136, `platform/datasets.py`:287 and
     `platform/validation_rules.py`:829. The scope-less sites it reaches include
     `api/dislocation_runs.py`:55 (`_require_dataset_read`).
   - **Red first, three times.** (i) At base, before Task 3, with `KNOWN_SCOPE_GAPS` filled, the
     app-wide test fails naming exactly the three FD 8177 routes (quoted in the LG). (ii) A
     permanent test feeds predicate 1 a synthetic route: a test-local `APIRouter` whose endpoint
     carries a scope-less `requires(DATASET_WRITE)` and calls
     `platform.datasets.update_dictionary`. It asserts the route is flagged. (iii) A permanent
     test feeds predicate 2 a synthetic route declared `DATASET` whose endpoint calls
     `dislocation_runs._require_dataset_read`, and asserts it is flagged.
   - **Negative control.** The deployment routes (handler-guarded, `ENVIRONMENT`) and
     `GET /api/v1/reference-tables` (`WORKSPACE`, RL 8182) are not flagged. After Tasks 3–4 the
     guard is green on the whole app.
6. **Green.** Derive the GREEN set by import closure (common brief item 29): the changed modules
   from `git diff --name-only origin/main...HEAD -- backend/src`, their importers, one more level
   of importers, then every test file importing the closure. Run each through `run-small.sh`,
   including `test_api_authorisation_sweep.py`, `test_management_429_declared.py`,
   `test_rbac.py` and `test_validation_reports.py`. Then run the slice gate, on the lead's grant.

## Acceptance Standard

1. At base (`origin/main` + Task 2's file only), `run-small.sh` on
   `backend/tests/test_dataset_scoped_writes.py` exits 1 with exactly the nine R-in-scope /
   R-out-of-scope / R-scoped-unknown-id tests `FAILED`; at the slice head it exits 0.
2. At base + Task 5's file only, `test_route_scope_guard.py`'s app-wide test exits 1 and names
   exactly `PUT /api/v1/datasets/{slug}/dictionary`, `PUT /api/v1/datasets/{slug}/rule-set` and
   `POST /api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge`. At the slice head
   the whole file exits 0, including both synthetic-route tests and the stale-exclusion test.
3. At the slice head, every `KNOWN_SCOPE_GAPS` row names an owner (RL 8182 or FD 8184) and its
   removing slice, and the stale-exclusion test exits 0. The LG quotes the row count.
4. `test_api_authorisation_sweep.py` and `test_management_429_declared.py` exit 0 at the slice
   head **with no diff to either file**: `git diff --stat origin/main...HEAD --` on both paths
   is empty.
5. `git diff --stat origin/main...HEAD -- docs/specs` is empty.
6. The slice gate (both halves, `dev-commands`), on the lead's grant, is green at the slice head;
   the MERGE-ACK quotes its `passed` line.

## Clashes and sequencing

- **The RL 8176 / RL 8182 docs batch** amends `06` FR-343 and FR-345. This slice writes no spec
  text and starts its code (Task 3) after that batch merges.
- **SL-1736** (`sl-1736-wk1178-nfr-sweep` @`ef1d0efb`) edits `platform/validation_rules.py`
  hunks `@@ -805,6 +805,21 @@`, `@@ -852,14 +867,18 @@` and `@@ -905,15 +924,8 @@`, all inside
  `replace_rule_set`, and `docs/specs/01-data-management.md`. Only Task 4 touches
  `validation_rules.py`, and it starts after SL-1736 merges. The slice never touches `01`.
- **SL-1260** (`sl-1260-wk674-s6` @`c55410d6`) edits `test_api_authorisation_sweep.py`
  (`HANDLER_GUARDED`, `RESOURCE_BACKED`) and `api/score.py`; none of those are in this write set.
  SL-1260's two new Environment routes need `ROUTE_SCOPES` rows (`ENVIRONMENT`). If SL-1260
  merges first, Task 5 adds them. If it merges after, the guard's *unclassified* failure tells
  SL-1260's re-merge to add them. **The lead should tell SL-1260's executor**, because that
  branch would go red on re-merge.
- **FD 8175's close vehicle** (the `RESOURCE_BACKED` guard, a WK-1178 test-only delta row) edits
  `test_api_authorisation_sweep.py`, which is not in this write set. This slice's guard is a
  separate file for that reason.
- **RL 8182's slice** follows this one, and its shared files are sequenced, not concurrent (the
  17:36:24 entry). It deletes its `KNOWN_SCOPE_GAPS` rows, and FD 8184's if the probe confirms.

## Out of scope — a pointer

The rest of RL 8182 (the `dataset_versions.py`, `blobs.py` and other single-Dataset routes) is
RL 8182's own slice. The FD 8184 fix, if confirmed, joins that slice. Neither is built here. This
slice's guard only lists them, owned, in `KNOWN_SCOPE_GAPS`. Model Family and Rating Algorithm
scopes are not built anywhere (DP-4's recorded limit). That is an observation for the lead, not
in this plan.

## Self-review before freeze

- Every route, line and code above was re-read at `71e481fa` by this planner, not taken from the
  relay. exec-8177's `rbac.py`:209–212 cite is `_covers` at `:205`–`:216`. RL 8182's
  `dislocation_runs.py` and `rate_tables.py` sites were re-read here, and the three dislocation
  routes reaching `_require_dataset_read` (:79, :105, :167) are my reads.
- The three 17:27:15 conditions map to Task 2 (red for all three, the `SCOPE_DENIED` control),
  Task 5 (the guard, with injected reds) and Task 4's ordering (SL-1736). The 17:36:24 item 4
  extension maps to DP-4 and Task 5's predicate 2.
- DP-1 and DP-2 are resolved by the 17:36:24 entry. DP-0, DP-3 and DP-4 are blocking and open,
  so the status is `draft`. On the maintainer's ruling, the plan is minted with resolver ids in
  the table and set `active`.
