---
id: PL-9820
family: plan
kind: leaf
title: WK-1250 Slice 1 — The sub-graph as a stored, versioned artifact (FR-217's artifact limb): leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-29
owner: planner
tree: 19c395acad594d1b193da197461bec85201d2248
phase: P2
work: WK-1250
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1254, FD-1241, RL-1242, PL-1239]
---

# WK-1250 Slice 1 — The sub-graph as a stored, versioned artifact (FR-217's artifact limb): leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` (Tasks 2–5), `python-test` (every task), `fastapi-service` (Task 5) and `dev-commands` (the gate), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make a sub-graph a **stored, versioned, immutable artifact** that a later slice can pin and
inline: a `model-schema` shape, a table, four routes, create-time validation, an Audit Event
on every write, and a resolver for `sub_graph:slug@version`. This slice does **not** pin,
inline, compile or score a sub-graph (Slice 2), and does not touch FR-218's purpose mount
(Slice 3).

**Architecture.** The closest precedent is the Rating Algorithm: one row per version, its
validated content stored as JSONB (`RatingAlgorithmRow`, `backend/src/app/db/models.py:1920-1948`),
a thin router (`backend/src/app/api/rating_algorithms.py`) over a service module
(`backend/src/app/platform/rating_algorithms.py`). The sub-graph follows it with three
differences: every write records an Audit Event in the same transaction (the precedent for
that is `backend/src/app/platform/objectives.py:238-250`, because `rating_algorithms.py` and
`rate_tables.py` record none — premise f); the fragment declares **ports** (map DP-3); and a
fragment carries no `sub_graphs` of its own (map DP-4).

**Tech Stack:** Pydantic v2 (`model-schema`), FastAPI, SQLAlchemy 2.x async, Alembic,
pytest. No new dependency.

**Spec:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3.1 — **FR-217** (`03:86`
  at the tree above); §4 (a new §4.11, Task 1); §5.1 (`03:741-768`, four new rows, Task 1).
- [`../specs/00-overview.md`](../specs/00-overview.md) §2 — the glossary, which gains
  **Sub-graph** (`CLAUDE.md` §7: "a new term goes there before first use"). `00` FR-4
  (`00:208`, immutability) and FR-16 (`00:220`, a workspace is not a tenant).
- [`../specs/06-governance.md`](../specs/06-governance.md) — FR-343 (`06:79`), FR-345
  (`06:81`), FR-368 (`06:154`); §3.3 (`06:111-121`), where map DP-1's outcome lands.
- [`../process/retrofit-impossible.md`](../process/retrofit-impossible.md) `:25`, `:26`,
  `:31` — audit in the caller's transaction, immutability, RBAC from the first endpoint.

**What this plan implements.** WK-1250's map plan, **PL-1254** (merged by #918 as
`4819ec88`; read at `19c395ac`), **Task 1 — "Slice 1: the sub-graph as a stored, versioned
artifact (FR-217's artifact limb)"** (`PL-1254:260-286`), whose Sequencing block reads
"Slice 1 the sub-graph artifact ─→ Slice 2 pin + inlining ─→ Slice 3 FR-218's purpose mount
+ the real check" (`PL-1254:227`).

## Status

**Draft**, filed 2026-09-29 against the tree above under **working id 9820**, which is
unused on `origin/main`, on every `origin/*` branch and on the head of every open PR at the
time of filing (swept with `git grep -o -E '\b98[12][0-9]\b'` over each ref; the only hit in
9810–9829 was 9829). It takes its real id from `python3 scripts/doc-id.py next --ref
origin/main` at its merge turn. (`next` read 1255 at `19c395ac`, but #924 holds
SL-1255 to SL-1259 unmerged, so the number is the lead's to reconcile at the turn.)

**Activation needs, in order:**
1. PL-1254 `active`. At the tree above it is `status: draft` (`PL-1254:6`), and WK-1250 is
   `status: draft` (`docs/roadmap.md`, `### WK-1250`).
2. The three `SL-` rows for WK-1250 minted. PL-1254 cuts them but does not mint them: "The
   three `SL-` rows are cut here and minted, `draft`, with ids the lead issues, when this
   plan is activated" (`PL-1254:221-222`). **This PR adds no `SL-` row.**
3. The map's **DP-1, DP-3 and DP-4** resolved by the decision-maker (`PL-1254:210`, `:212`, `:213`,
   Blocking "yes — Slice 1" on each), and this plan's **DP-S1-1 to DP-S1-4** below.
4. The lead's go, which must also settle the lane question in **Dependencies** below.

### Dependencies — what Slice 1 needs that is not built or not merged

- **Code: nothing.** PL-1254's Task 1 reads "**Depends on:** nothing in WK-1250. It is
  blocked on DP-1, DP-3 and DP-4. *(The WK-674 tenancy dependency is dropped, 2026-09-29,
  N1: workspace scoping is RBAC scope, not tenancy.)*" (`PL-1254:274`). Its Global
  Constraints give the reason: every row carries a `workspace_id` (`00` FR-16) and reads are
  scoped to the caller's workspace, "which exists today. A workspace is not a tenant and not
  an isolation boundary (`00` FR-16), so nothing here depends on WK-674's tenancy"
  (`PL-1254:125-131`). Checked against code at the tree above: the workspace filter this
  slice copies is `RatingAlgorithmRow.workspace_id == workspace_id` in
  `backend/src/app/platform/rating_algorithms.py` (`create_algorithm`, `get_algorithm`),
  fed by `caller.workspace_id` in `backend/src/app/api/rating_algorithms.py:48,68`. Nothing
  in PL-1239's tasks (the tenant marker, `platform_build`) is read or needed here.
- **Decisions: seven open.** DP-1, DP-3, DP-4 (map) and DP-S1-1 to DP-S1-4 (below). None is
  resolved on `origin/main` at `19c395ac`, and no open PR carries a ruling on any: the head of
  every open PR was diffed against `origin/main` for `sub-graph|sub_graph|FR-217|FR-218|PL-1254|WK-1250`;
  only #920 (WK-675's map plan, `1a2427f1`), #922 (`c310aea7`) and #909 (`259e8e16`) match,
  and none of those lines rules a DP.
- **Process: the parallel start is not recorded in the repository.** Three texts on
  `origin/main` put this slice after WK-674, not beside it:
  - `docs/process/delivery-process.md:156-157`: "Sequential processing of a layer's
    **children** (Project→Phase→Work→Slice: no two Slices run at once, at any layer)". The
    same section says "an exception argued on plan-independence argues past it (RL-871
    refused exactly that argument)".
  - `PL-1254:134-135` and `:230-231`: "One slice at a time (`delivery-process.md` §8), on the
    P2 lane **after WK-674** and before WK-675"; "after WK-674 closes".
  - `docs/roadmap.md:862`: "**Sequenced after WK-674 and before WK-675**".

  `git grep -i -E 'second lane|second code lane|two lanes|parallel start' origin/main -- docs`
  prints nothing. So running this slice while WK-674 Slice 1 runs needs a dated maintainer
  record that amends or excepts those three texts; until it lands, this plan inherits them.
  **The planner does not decide this** (`planner.md`, "Never": replan vs. proceed is the
  lead's).

### File contention with WK-674 Slice 1

WK-674 Slice 1's files are PL-1239's Tasks 1–5 at `origin/main` (and #924 at `f3d2cec6`, which
adds `backend/src/app/config.py:191`'s `require_startable()` and `backend/tests/test_config.py`
to the same files). Against this plan's file list (Tasks 1–5 below):

| File | WK-674 S1 (PL-1239) | This slice | Collision |
|---|---|---|---|
| `backend/migrations/versions/` | one new revision | one new revision | **Yes, certain.** The single head at `19c395ac` is `a71c3e95d204` (`backend/migrations/versions/a71c3e95d204_regression_runs.py`). Both revisions will name it as `down_revision`, so the second to merge makes two heads and fails FR-417's guard (`tests/test_repository_invariants.py`). The second must re-point its `down_revision` to the first's revision after a rebase |
| `docs/contracts/openapi/generated.json` | regenerated (the `Job` schema gains `platform_build`) | regenerated (four routes, the `SubGraph` schemas) | **Yes, likely a text conflict.** Resolve by regenerating on the rebased tree, never by hand (`CLAUDE.md` §2) |
| `backend/src/app/main.py` | the lifespan (`:75-94`) | one import beside `:34`, one `include_router` beside `:134-145` | Same file, different regions; git usually merges it cleanly |
| `backend/src/app/db/models.py` | `JobRow` (`:90`) gains a column | a new `SubGraphVersionRow` class | Same file. A conflict only if both append at the end of the file; add the new class after `RatingAlgorithmRow` (`:1948`), not at the end |
| `docs/INDEX.md` | regenerated | regenerated | Yes, every docs PR; regenerate at the turn |
| `backend/tests/conftest.py` | "if `api_settings` needs the new setting" (PL-1239 Task 4) | not touched (a fixture this slice needs goes in its own test module) | No |

Every other file below is disjoint from PL-1239's list (`07-platform.md`, `model_schema/jobs.py`,
`config.py`, `platform/jobs.py`, `worker/tasks.py`, `platform/blobs.py`,
`worker/celery_app.py`, `platform/tenancy.py`, and their tests).

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means
the failing run is quoted in the ledger with its failing assert line **and the cause the step
predicts**; a failure for any other cause is a plan defect, reported, not worked around.

1. **Spec.** `03` gains §4.11 `SubGraph` (the shape, its invariants, an example) and four
   §5.1 rows (Task 1); `00` §2 gains **Sub-graph**; map DP-1's outcome is written where its
   ruling says. `03` FR-217 and FR-218 are **not** reworded here: FR-217 already says what
   this slice builds, and FR-218's interim rule is Slice 3's to strike (`RL-1242:83-85`). If
   the executor believes either needs a change, it stops and reports.
   `python3 scripts/audit-docs.py` exits 0.
2. **Contract.** `uv run python scripts/generate-contracts.py --check` exits 0 after the
   regeneration; `docs/contracts/schemas/generated/sub-graph.schema.json` exists and has the
   properties `slug`, `version`, `inputs`, `outputs`, `steps` and `change_note`, and no
   `sub_graphs`. The shape is declared once:
   `git grep -n -E '^class SubGraph(Body)?\(' -- packages backend/src` prints **exactly two**
   lines, both in `packages/model-schema/src/model_schema/sub_graphs.py`. Any other count fails.
3. **Migration (FR-417).** One new Alembic revision creates the table.
   `uv run alembic upgrade head`, `downgrade -1` and `upgrade head` again all exit 0 against a
   scratch database (the `dev-commands` DSN), and
   `uv run pytest tests/test_repository_invariants.py -q` passes. The unique constraint on
   `(workspace_id, slug, version)` is proven by a second insert of the same triple raising
   `IntegrityError` at the database, not by application code.
4. **Validation refusals (FR-217, FR-212), red first, one test per cause**, in
   `packages/model-schema/tests/test_sub_graph.py` (shape) and
   `backend/tests/test_sub_graphs_api.py` (the route), each `@pytest.mark.req("FR-217")`:
   - a step consumes a name that is neither a declared input nor produced by a step →
     refused, the message naming that name;
   - a declared output that no step produces → refused, naming it;
   - two steps with the same `step_id` → refused;
   - a cycle → refused;
   - a body carrying `sub_graphs` → refused by `extra="forbid"` (DP-4 (a)); the test asserts
     the error's `loc` is `("sub_graphs",)` and its type is `extra_forbidden`, not only that
     validation failed;
   - an `input` or `output` step inside the fragment → refused (the ports replace them,
     DP-3 (a));
   - an empty `change_note` → refused (DP-1 (b)).
   Through the route, each maps to the error code DP-S1-3 resolves, with a 422.
5. **Immutability (`00` FR-4).** There is no route that modifies a version: the
   authorisation sweep (`backend/tests/test_api_authorisation_sweep.py`) lists no `PUT`,
   `PATCH` or `DELETE` on `/sub-graphs`. A second create of an existing `slug@version` is
   refused with 409 and the stored content is byte-identical afterwards (asserted by reading
   it back).
6. **Audit (`06` FR-368, retrofit-impossible `:25`), red first.** Every successful write
   leaves exactly one Audit Event with `action == "sub_graph.created"` and
   `entity_ref == "sub_graph:<slug>@<version>"`, in the same transaction. **Broken-input
   proof:** with the `audit.record` call removed (a local edit, never committed), the test
   goes red on the event count being 0; the ledger quotes that red. A refused write leaves
   no event and no row.
7. **Permission (`06` FR-343), red first, per route.** A principal without the route's
   permission (DP-S1-1) gets 403; a principal whose only assignment is scoped to a named
   Rating Algorithm gets 403 too (`_covers` returns `False` for a scoped assignment when no
   resource is named, `backend/src/app/platform/rbac.py:205-216`). The authorisation sweep
   passes with the four new routes in it.
8. **Workspace scoping (`06` FR-345, `00` FR-16).** A sub-graph created in workspace A is
   **404, not 403**, to a caller in workspace B on `GET` of the version and absent from B's
   list. Mirror `backend/tests/test_api_jobs.py:172`
   (`test_a_job_in_another_workspace_is_404_not_403`); do not invent a fixture.
9. **Resolver.** `resolve_ref(session, workspace_id=…, ref=ArtifactRef)` (Task 4) returns
   exactly the addressed version's content for `sub_graph:slug@version`; an unknown slug, an
   unknown version, a ref of another type, and a ref to another workspace's sub-graph are
   each refused, by cause. It is **not** wired into the compile resolver in
   `backend/src/app/platform/rating_versions.py:417` — that is Slice 2's (see **Scope**).
10. **Coverage.** `uv run python scripts/req-coverage.py` lists the new test files against
    FR-217. The ledger records FR-217's verdict for this slice as **the artifact limb
    delivered; the pin and inlining limbs not started, owned by Slice 2** — never
    "FR-217 delivered".
11. **The gate.** The full two-half gate (`CLAUDE.md` §11) exits 0 on the committed tree, with
    every command's rc, the `N passed` line and `HEAD` quoted in the ledger, and `N passed`
    compared with `origin/main`'s (a total that did not move means the new tests were never
    collected). `backend/tests/test_demo_guide.py` passes with the new §5.1 rows present in
    the generated contract.
12. **Item 11.** Before the lead merges, the maintainer's **MERGE-ACK**, naming the PR's full
    head SHA, is recorded in the lead's channel file (`~/gi-pricing-plan.local/channel/to-lead.md`),
    given by the maintainer or on the maintainer's behalf. **It is never posted on the PR.**
    The slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and
    the lead's merge — no maintainer acceptance line is required for a slice, and none is to
    be waited on.

## Global Constraints

- **Spec first** (`CLAUDE.md` §0): Task 1 lands before any code.
- **No hand-written shape `model-schema` owns** (`CLAUDE.md` §2): `SubGraph` and
  `SubGraphBody` are declared once, in `model-schema`; the backend imports them.
- **`pricing-core` gains no import and no code** in this slice (DP-S1-4's recommendation;
  `.importlinter` keeps it standalone either way).
- **Every write emits its Audit Event in the caller's transaction** (`06` FR-368;
  `backend/src/app/platform/audit.py:52-75` raises if there is no open transaction).
- **RBAC in the backend on every request** (`06` FR-343), from a `Permission` in
  `packages/model-schema/src/model_schema/permissions.py`.
- **A version is immutable** (`00` FR-4): no update route, no update code path.
- **Every row carries a `workspace_id`; a workspace is not a tenant** (`00` FR-16).
- **The migration chain has exactly one head** (`07` FR-417).
- **Do not build ahead of the phase** (`CLAUDE.md` §0): no frontend view (WK-675's), no pin,
  no inlining.

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.1 | FR-217 | **The artifact limb only**: "versioned artifacts referenced by the parent". The pin and "inlined at bundle time" are Slice 2's |

Supporting requirements this slice must honour but does not own: `00` FR-4, `00` FR-16,
`03` FR-212 (the graph invariants, applied to the fragment), `06` FR-343, `06` FR-345,
`06` FR-368, `07` FR-417.

**Not in this slice**, each with where it goes (PL-1254's coverage table, `PL-1254:141-147`):
- `Pins.sub_graphs`, the compile resolver's `sub_graph` branch, inlining, `bundle_hash`, and
  FR-258's inlined steps → **Slice 2**. The resolver branch in
  `backend/src/app/platform/rating_versions.py:417` stays with Slice 2 because nothing calls
  it until `compile_bundle` reads `sub_graphs`; a branch with no caller is behaviour nobody
  tests. This slice's `resolve_ref` is the function that branch will call.
- FR-218's purpose mount, and `RL-1242`'s retirement → **Slice 3**.
- The designer's sub-graph view → **WK-675** (#920's S9, unmerged).
- A mount-point check against a parent's steps → **Slice 2** (a fragment does not know its
  parent).

### Premises re-derived at the tree above

| # | Premise | Evidence |
|---|---|---|
| a | No sub-graph table, route or service exists | `git grep -n -i 'sub_graph\|subgraph' -- backend/src packages/*/src` prints 7 lines: `model_schema/__init__.py:282,669`, `model_schema/rating.py:340,343,390`, `model_schema/refs.py:25`, and `pricing_core/rating/score.py:399,401` (docstrings). None under `backend/src` |
| b | `SubGraphRef` is `ref: ArtifactRef` + `mount_point: str`, frozen, `extra="forbid"`; `RatingAlgorithm.sub_graphs` defaults to `[]` | `packages/model-schema/src/model_schema/rating.py:340-351`, `:390` |
| c | `"sub_graph"` is a legal `ArtifactRef` type | `packages/model-schema/src/model_schema/refs.py:25` |
| d | Intermediate Derived Values carry no declared type: only `InputContractField` (`:205-211`) and `AlgorithmOutput` (`:238-244`) have a `type` | `grep -n 'type:' packages/model-schema/src/model_schema/rating.py` — so a port is a name, not a typed field (DP-3 (a) as recommended here) |
| e | The graph-invariant helpers are module functions over a step list | `_produced_by`, `_consumed_by` (`rating.py:357-370`), used by `RatingAlgorithm._graph_invariants` (`:392`) |
| f | Neither the rating-algorithm nor the rate-table write path records an Audit Event; custom objectives do | `grep -n 'audit\.' backend/src/app/platform/rating_algorithms.py backend/src/app/platform/rate_tables.py` prints nothing; `backend/src/app/platform/objectives.py:238` calls `audit.record(…, action="custom_objective.created", entity_ref=f"custom_objective:{row.slug}@{row.version}", …)` |
| g | `requires(permission)` passes no resource, so only a workspace-wide assignment satisfies it | `backend/src/app/api/authz.py:54-77`; `backend/src/app/platform/rbac.py:205-216` (`_covers`: "A scoped assignment cannot satisfy a question about no particular resource") |
| h | `rating:read` and `rating:write` exist; the Analyst role holds both | `packages/model-schema/src/model_schema/permissions.py:47-48`, `:113-114` |
| i | The migration chain's single head is `a71c3e95d204` | a scan of every `revision`/`down_revision` under `backend/migrations/versions/` (46 files) |
| j | The generated-contract registry is a slug → symbol map | `scripts/generate-contracts.py:39-101` (e.g. `"custom-objective": "CustomObjective"`) |
| k | `03` §4's last subsection is §4.10 `ScoreComparison`, and §5.1 has no sub-graph row | `grep -n '^### 4\.' docs/specs/03-rating-engine.md`; `03:741-768` |
| l | `00` §2 has no "Sub-graph" term | `grep -n -i 'sub-graph\|sub_graph' docs/specs/00-overview.md` prints nothing |

The executor re-reads each at its own tree and stops on any that no longer holds
([`README.md`](README.md) convention 4).

### Decision points

The map's **DP-1** (is a sub-graph version a Governed Artifact), **DP-3** (the port contract
at the mount) and **DP-4** (may a sub-graph mount sub-graphs) each block this slice
(`PL-1254:210`, `:212`, `:213`). They are **not restated or re-decided here**; this plan is written on the
map's recommendations — DP-1 (b), DP-3 (a), DP-4 (a) — and names below every step that
changes if a ruling differs. The four below are this slice's own; each is the
decision-maker's (`delivery-process.md` §3). The planner rules none of them.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S1-1 | Which permission do the four routes check, and may a principal scoped to a named Rating Algorithm (`06` FR-345) author a sub-graph? | (a) `rating:write` for the two writes and `rating:read` for the two reads, through `requires()`, which admits only a workspace-wide assignment (premise g). No new permission, no new scope type; (b) new `sub_graph:read` / `sub_graph:write` permissions, added to `06`'s catalogue, `permissions.py` and the built-in roles, still workspace-wide; (c) as (a), plus a new `ScopeType.SUB_GRAPH` so an assignment can name one sub-graph | **(a).** A sub-graph is rating maths authored by whoever authors algorithms, and §5.1's Regression Suite rows set the precedent of reusing `rating:write`/`rating:read` for a rating artifact (`03:755-756`). A sub-graph can be mounted by any algorithm in the workspace, so authoring one is a workspace-wide act, which is exactly what `requires()` enforces today. (b) adds catalogue entries (`RL-1236` governs that catalogue) for no separation anyone has asked for. (c) builds a scope nobody needs before a designer exists | decision point | yes — Tasks 1 and 5 | |
| DP-S1-2 | How are versions stored and numbered, and what are the routes? | (a) One table `sub_graph_versions`, one row per version, content as JSONB, unique `(workspace_id, slug, version)` — the `RatingAlgorithmRow` layout. `POST /api/v1/sub-graphs` creates version 1 of a new slug (409 if the slug exists); `POST /api/v1/sub-graphs/{slug}/versions` creates the next version, numbered by the server as the current maximum plus one, with the unique constraint turning a race into a 409 (the `objectives.py:229-236` form); `GET /api/v1/sub-graphs/{slug}@{version}`; `GET /api/v1/sub-graphs/{slug}/versions`, cursor-paginated with `app.api.pagination`; (b) two tables, `sub_graphs` + `sub_graph_versions`, the rate-table layout (`models.py:1951`, `:1978`); (c) as (a) but the client supplies `version` in the body and one `POST` does both, the rating-algorithm form (`api/rating_algorithms.py:28-50`) | **(a).** A server-numbered version has no gaps, so `@4` always means the fourth change; one table is enough because a sub-graph has no container-level state (no status under DP-1 (b), no owner beyond the workspace). (b) is a second table with nothing in it. (c) lets two authors pick `@5` and lets a pin name a version that was never the latest. **`00` FR-4's `parent_id`:** the only table carrying one is at `models.py:818`; neither rating artifact has one. Under (a) the previous version is `version - 1`, so no column is added — the decision-maker may rule otherwise | decision point | yes — Tasks 1, 3 and 5 | |
| DP-S1-3 | Which error codes does a refused sub-graph carry? | (a) Reuse `03` §5.1's codes: a cycle → `RATING_GRAPH_CYCLIC`; a consumed name nobody produces or an unproduced output → `RATING_GRAPH_UNRESOLVED_REF`; any other shape refusal (duplicate `step_id`, `sub_graphs` present, an `input`/`output` step, an empty change note) → `VALIDATION_FAILED`; unknown `slug@version` → `NOT_FOUND`; an existing version → 409 `VALIDATION_FAILED`, as `create_algorithm` does; (b) new `SUB_GRAPH_*` codes owned by `03` §5.1 | **(a).** The defects are the same defects the algorithm's own validator names, and a client that already handles them handles these. (b) adds codes that differ only in which artifact carried the defect, which the `instance` path already says | decision point | yes — Tasks 1 and 5 | |
| DP-S1-4 | How deep is create-time validation? `pricing-core`'s `validate_algorithm` (`packages/pricing-core/src/pricing_core/rating/compile.py:261-275`) runs five checks — result types, determinism, division guards, scale cap, vocabulary — each taking a whole `RatingAlgorithm` | (a) The shape invariants only (acceptance 4), in `model-schema`. The five expression checks run on the **inlined** algorithm at compile, in Slice 2, where the parent's input contract and outputs exist; (b) generalise the five helpers to take a step list and run the context-free ones at create, leaving result types to compile; (c) wrap the fragment in a synthetic `RatingAlgorithm` and run `validate_algorithm` unchanged | **(a).** It keeps `pricing-core` out of this slice (and out of any file Slice 2 edits), and every check still runs before a bundle can score. The cost is that a fragment with a non-deterministic expression is saved and refused only when an algorithm that mounts it is compiled; Slice 2's gate must then prove that refusal. (b) is the stricter FR-212 reading ("rejected at save") and touches `compile.py`, which Slice 2 also rewrites. (c) invents an input contract the fragment does not have, so result-type checks would pass or fail on fiction | decision point | yes — Tasks 2 and 5 | |

**If a map DP is ruled differently.** DP-1 (a) adds a status lifecycle, an approval path, an
evidence row and a `DEFAULT_POLICY` entry, and would roughly double this slice; the plan is
then **replanned, not patched** (a new `PL-` with `supersedes:`). DP-3 (b) or (c) removes the
`inputs`/`outputs` fields and acceptance 4's port bullets. DP-4 (b) or (c) replaces the
`extra="forbid"` refusal with a depth or cycle check. Each is named at its step below.

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch.
- [ ] `uv sync --all-packages` (a fresh worktree without it reports hundreds of phantom mypy
  errors — `dev-commands`).
- [ ] Re-derive premises a–l; record the tree and each result in the ledger.
- [ ] `gh pr list --state open`, and read anything that rules on FR-217, sub-graphs, the
  permission catalogue or `03` §4–§5.1 ([`README.md`](README.md) convention 4). Name the SHA
  read. **Check the migration head again** (premise i): if WK-674 Slice 1 has merged, its
  revision is the new head and this slice's `down_revision` names it.
- [ ] Confirm the resolutions of DP-1, DP-3, DP-4 and DP-S1-1 to DP-S1-4, by record id, in
  the ledger. Any that differs from the recommendation this plan is written on: apply it at
  every step named in **If a map DP is ruled differently**, or stop and report if it is
  DP-1 (a).

### Task 1: Spec — `03` §4.11 and §5.1, `00` §2, and DP-1's outcome

**Files:** Modify `docs/specs/03-rating-engine.md` (§2, a new §4.11 after §4.10, §5.1);
`docs/specs/00-overview.md` (§2); `docs/specs/06-governance.md` (where DP-1's ruling says).

- [ ] `00` §2: add **Sub-graph** — "A reusable, versioned fragment of a Rating Algorithm
  (`03` FR-217), with declared input and output ports, mounted by a parent algorithm and
  inlined into the parent's Bundle. It holds no premium on its own." Add it in the table's
  existing order; read the neighbouring rows first (`00:161` is **Rating Algorithm**).
- [ ] `03` §2: a one-line **Sub-graph** row pointing at `00` §2, in the form the other `03`
  rows that restate a `00` term use (read them; do not invent a form).
- [ ] `03` §4.11 `SubGraph`: the example below, the invariants of acceptance 4 as prose, and a
  dated note citing FR-217 and this slice.

  ```json
  {
    "slug": "ncd-ladder",
    "version": 4,
    "inputs": ["ncd_years"],
    "outputs": ["ncd_factor"],
    "steps": [
      {"step_id": "s_ncd", "type": "table", "label": "NCD ladder",
       "rate_table_ref": "rate_table:ncd@2", "key_expr": ["ncd_years"],
       "consumes": "ncd_years", "produces": "ncd_factor"}
    ],
    "change_note": "Step-back after one claim is two years, not three."
  }
  ```

  The step's fields are `RatingTableStep`'s (`rating.py:283-288`) and follow the §4.1
  example's table step (`03:262-264`); re-verify them at the executor's tree before they
  enter the spec ([`README.md`](README.md) convention 1). The slug `ncd-ladder` and `@4` are
  `WF-699` B7's (`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:62`),
  so the journey and the spec name the same artifact.
- [ ] `03` §5.1: four rows, in DP-S1-2's form and DP-S1-1's permissions, each with its status
  code and FR-217. Add the routes' error codes under §5.1's "Error codes owned by this
  module" only if DP-S1-3 is ruled (b).
- [ ] DP-1's outcome where its ruling says. Under (b), the likely site is `06` §3.3, beside
  the struck Rate Table Version row (`06:119`), and the `03` FR-20 clarification PL-1254's
  DP-1 names (`03:399-401`) — but the ruling's own text decides both.
- [ ] `python3 scripts/audit-docs.py`; quote the rc. Commit:
  `docs(specs): 03 §4.11 SubGraph and §5.1 routes, 00 §2 Sub-graph (FR-217, WK-1250 S1)`.

### Task 2: `model-schema` — `SubGraph`, `SubGraphBody` and the contract

**Files:** Create `packages/model-schema/src/model_schema/sub_graphs.py`,
`packages/model-schema/tests/test_sub_graph.py`; modify
`packages/model-schema/src/model_schema/__init__.py` (export both, beside `SubGraphRef` at
`:282` and `:669`), `scripts/generate-contracts.py` (register `"sub-graph": "SubGraph"` in the
map at `:39-101`); regenerate `docs/contracts/`.

**Interfaces:**
- Produces: `SubGraphBody` (the request body: `inputs: list[str]`, `outputs: list[str]`,
  `steps: list[RatingStep]`, `change_note: str`) and `SubGraph(SubGraphBody)` (adds
  `slug: Slug`, `version: int`). Both `frozen=True, extra="forbid"`.

- [ ] **Red first:** the model-level tests of acceptance 4, plus one positive test that the
  Task 1 example parses. Predicted red: `ImportError` on `model_schema.sub_graphs` for every
  test, the same cause for each; any other failure is a plan defect.
- [ ] Implement. The invariant check reuses `_produced_by` and `_consumed_by` from
  `rating.py` (premise e) — import them, do not copy them. The cycle check reuses whatever
  `RatingAlgorithm._graph_invariants` uses (`rating.py:392` onward; read it, do not rewrite
  it). If reuse needs a helper promoted from `_graph_invariants` into a module function,
  promote it in `rating.py` and keep `RatingAlgorithm`'s behaviour identical: the existing
  `packages/model-schema/tests/test_rating_algorithm.py` must pass unchanged. The checks read
  `consumes` and `produces` only, as `_graph_invariants` does; a name referenced only inside
  `key_expr` or `expr` is not seen by either, and this slice does not widen that.
  - DP-3 (b)/(c): drop `inputs`/`outputs` and the port checks.
  - DP-4 (b)/(c): replace the reliance on `extra="forbid"` with an explicit
    `sub_graphs: list[SubGraphRef]` and the ruled depth or cycle check.
- [ ] Green. Regenerate: `uv run python scripts/generate-contracts.py`, then `--check` exits 0.
  Run the contract guard (`contract-guard`) and quote its result. Acceptance 2's count.
- [ ] Commit.

### Task 3: The table and its migration

**Files:** Modify `backend/src/app/db/models.py` (a `SubGraphVersionRow` class **after
`RatingAlgorithmRow`, `:1948`** — see **File contention**); create one Alembic revision under
`backend/migrations/versions/`; create `backend/tests/test_migration_sub_graphs.py`.

- [ ] **Red first:** acceptance 3's constraint test. Predicted red: the table does not exist
  (`UndefinedTable`); any other cause is a plan defect.
- [ ] The row, per DP-S1-2 (a): `id` (uuid7, as `RatingAlgorithmRow:1930`), `workspace_id`,
  `slug` (`String(64)`), `version` (`Integer`), `content` (`JSONB`), `change_note` (`Text`,
  not null), `created_at`, `created_by`; `UniqueConstraint("workspace_id", "slug", "version",
  name="uq_sub_graph_versions_slug_version")` and an index on `(workspace_id, slug)`. **No
  `updated_at`**: the precedent carries one (`:1939-1941`), but nothing may update this row
  (`00` FR-4), and a column that says otherwise invites the code path.
- [ ] The revision: `down_revision` is the head Task 0 found. `upgrade` creates the table;
  `downgrade` drops it. Round-trip per acceptance 3.
- [ ] Green; commit.

### Task 4: The service and the resolver

**Files:** Create `backend/src/app/platform/sub_graphs.py`,
`backend/tests/test_sub_graphs_service.py`.

**Interfaces:**
- Consumes: `SubGraph`, `SubGraphBody` (Task 2); `SubGraphVersionRow` (Task 3);
  `audit.record` (`backend/src/app/platform/audit.py:52`).
- Produces, each taking `(database_or_session, workspace_id, …)` in the form of the
  neighbouring service module:
  - `create_sub_graph(database, workspace_id, actor, slug, body) -> SubGraph` — version 1;
  - `create_version(database, workspace_id, actor, slug, body) -> SubGraph` — max + 1;
  - `get_version(database, workspace_id, slug, version) -> SubGraph`;
  - `list_versions(database, workspace_id, slug, cursor, limit)` — the page type
    `app.api.pagination` already defines (read it; do not define a new one);
  - `resolve_ref(session, *, workspace_id, ref: ArtifactRef) -> SubGraph`, in the signature
    form of `objectives.resolve_ref` (`backend/src/app/platform/objectives.py:400`).

- [ ] **Red first:** acceptance 6 (audit), 5 (the 409 and unchanged content) and 9 (the
  resolver, each refusal by cause). Predicted red: `ImportError` on `app.platform.sub_graphs`.
- [ ] Implement, mirroring `objectives.py:225-250` for the write-plus-audit shape (flush, catch
  `IntegrityError` as 409, then `audit.record(..., source=JobSource.API,
  action="sub_graph.created", entity_ref=f"sub_graph:{slug}@{version}", after={...})`, all
  inside `database.unit_of_work()`). The `after` payload carries `change_note`, `inputs` and
  `outputs`, not the whole step list.
- [ ] The acceptance 6 broken-input proof: remove the `audit.record` call locally, run, quote
  the red in the ledger, restore. Never commit the broken state.
- [ ] Green; commit.

### Task 5: The routes

**Files:** Create `backend/src/app/api/sub_graphs.py`, `backend/tests/test_sub_graphs_api.py`;
modify `backend/src/app/main.py` (the import beside `:34`, `include_router` beside
`:134-145`); regenerate `docs/contracts/openapi/generated.json`.

- [ ] **Red first:** acceptance 4 through the route (each refusal's code per DP-S1-3), 7
  (403 per route, unscoped and scoped) and 8 (404 across workspaces). Predicted red: 404 on
  every route, because no route is mounted. A 404 on the cross-workspace test **after**
  Task 5 is green is the pass, so write that test to first assert the same `GET` returns 200
  in workspace A.
- [ ] Implement in `rating_algorithms.py`'s form (`RatingWriteDep`/`RatingReadDep` via
  `requires(Permission.…)` per DP-S1-1; `problems(...)` for the documented codes). The body
  is `SubGraphBody`, typed, not `dict[str, Any]`, so the OpenAPI document carries the shape.
- [ ] Regenerate contracts; `--check` exits 0; run `backend/tests/test_api_authorisation_sweep.py`
  and `backend/tests/test_demo_guide.py`.
- [ ] Green; commit.

### Task 6: The gate and the ledger

- [ ] `tests/test_repository_invariants.py`, the migration round trip, then the full two-half
  gate on the committed tree. Quote every rc, the `N passed` line and `HEAD`, against
  `origin/main`'s `N passed`.
- [ ] The ledger records: the tree; premises a–l; the red-first quotes; the DP resolutions by
  record id; FR-217's partial verdict (acceptance 10); and, if WK-674 Slice 1 merged first,
  the re-pointed `down_revision`.
- [ ] Item 11 (acceptance 12).

## Hand-off

Slice 2 (the pin and the inlining) starts after this slice closes. It consumes `resolve_ref`
and `SubGraph` from here. Under DP-S1-4 (a) its gate must also prove that a sub-graph whose
step fails one of `validate_algorithm`'s five checks is refused **at compile** of a parent
that mounts it.

## Self-review

- **Scope against the map and the spec.** FR-217's artifact limb is the only requirement
  delivered, listed individually; its other two limbs are named as Slice 2's in the coverage
  table and in acceptance 10. The map's Task 1 gate items — refusal per cause, a resolver
  test, a 403 per route, an audit test red on broken input, a workspace-scope test,
  `generate-contracts.py --check`, the full gate, item 11 (`PL-1254:275-285`) — are
  acceptance 4, 9, 7, 6, 8, 2, 11 and 12. The map's scope bullet "the resolver for
  `sub_graph:slug@version`" is `resolve_ref` (Task 4); wiring it into compile is left to
  Slice 2, stated in **Scope** with the reason.
- **FR-217 read to its clauses** (`03:86`): "reusable fragments" → the stored artifact;
  "versioned artifacts" → DP-S1-2 and acceptance 5; "referenced by the parent" → the
  resolver; "inlined at bundle time" → Slice 2. It carries no dated amendment (`FD-1241`'s
  own sweep).
- **Literals** in this plan were read at the tree above (premises). Names the executor adds
  (`SubGraph`, `SubGraphBody`, `SubGraphVersionRow`, `sub_graph_versions`,
  `sub_graph.created`, the function names) are proposals, named once each and used
  consistently in Tasks 2–5.
- **Open:** map DP-1, DP-3, DP-4 and DP-S1-1 to DP-S1-4, all the decision-maker's; the
  parallel-start record, the lead's and the maintainer's.
