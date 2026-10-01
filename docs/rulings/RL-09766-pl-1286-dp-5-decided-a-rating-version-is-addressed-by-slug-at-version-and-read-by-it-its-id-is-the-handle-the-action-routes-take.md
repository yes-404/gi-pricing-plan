---
id: RL-9766
family: ruling
title: PL-1286 DP-5 decided — a Rating Version is addressed by slug@version and read by it; its id is the handle the action routes take
status: draft                  # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-01
owner: decision-maker
tree: 8bd782acbbdde8e3b4195b5a0acb89183b5a0253
phase: P2
work: WK-675
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1286, FR-237, FR-238, FR-24, FR-25, FR-440]
---

# RL-9766 — PL-1286 DP-5 decided: a Rating Version is addressed by `slug@version` and read by it; its `id` is the handle the action routes take

## How this was ruled

**Ruled 2026-10-01 10:12 BST at effort `medium`** by the decision-maker session
`dm-675dp56`. The process command line is `claude --effort medium --model opus --name
dm-675dp56`, and `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=medium`. The
session was commissioned by the lead on the maintainer's instruction (2026-10-01 ~10:09 BST,
as the lead relayed it: "Commission ONE decision-maker NOW (medium, opus, from
decision-maker.md) for DP-5 + DP-6"). This session did not read the channel entry itself.

**Working id 9766**, allocated by the lead. It is minted at its merge turn, and every
`RL-<this>` placeholder below is then this record's minted id. The sibling record for DP-6 is
RL 9767 (working id), on the same branch.

**Evidence tree.** Everything below was read at origin/main `1dd5e264` (tree `8bd782ac`),
fetched 2026-10-01 10:08 and re-fetched 10:12 BST, unchanged.

**Not touched.** DP-3 (`OQ-1223`) and DP-7 (`OQ-1285`) are held until Saturday's scope
freeze. This record does not rule them.

## The question

`PL-1286` DP-5 (`PL-1286`:244 at this tree): the `03` §5.3 view routes address a version as
`:slug/v/:version`, but the backend reads a Rating Version only by UUID. Which form wins, and
how do the two meet? It gates Slice 2's leaf plan going `active`. S4 and S10 reach the
answer through S2's routes.

## Evidence at `1dd5e264`

- **The view routes.** `03` §5.3 (`docs/specs/03-rating-engine.md:1093-1099`) gives six
  routes of the form `/rating/:slug/v/:version/…`. `00` §5.6 declares four of them as
  canonical (`docs/specs/00-overview.md:405-408`).
- **The model.** `03` §4.3 (`:345-414`): a Rating Version has its own `slug` and `version`
  (`"motor-gb"`, `27`) and an `algorithm_ref` with a different version
  (`rating_algorithm:motor-gb@14`). So `:version` in a view route is ambiguous unless a rule
  says whose version it is.
- **Uniqueness.** `UniqueConstraint("workspace_id", "slug", "version",
  name="uq_rating_versions_slug_version")` on `RatingVersionRow`
  (`backend/src/app/db/models.py`, the class at `:1945`, `__table_args__` at `:1985-1986`). The pair is a key.
- **The reads that exist.** `GET /rating-versions` (`backend/src/app/api/models.py:1112-1135`,
  the Phase 1b demo list) and `GET /rating-versions/{rating_version_id}`
  (`models.py:1138-1157`), both `rating:read`, both returning `RatingVersion`. Neither has a
  row in `03` §5.1 (`:777-801`). The by-id handler's 404 covers another workspace's id
  (`backend/src/app/platform/rating_versions.py:126-138`, `load_rating_version`).
- **The resolver that exists.** `resolve_rating_version_ref`
  (`backend/src/app/platform/rating_versions.py:141-171`) reads the row by
  `(workspace_id, slug, version)`, with no row lock, and answers 404 `NOT_FOUND`. The
  scoring path uses it already. **The new route needs no new query.**
- **The response type that exists.** `RatingVersion`
  (`packages/model-schema/src/model_schema/rating.py:137`), present in
  `docs/contracts/openapi/generated.json` `components.schemas` as `RatingVersion`.
- **The action routes.** `compile`, `submit` and the regression-run routes take `{id}`
  (`03` §5.1 `:793-800`; `models.py:1188`, `:1232`, `:1264`, `:1310`).
- **The `03` §5.1 convention.** Every other versioned read is `{slug}@{version}`:
  `rating-algorithms/{slug}@{version}/diff`, `sub-graphs/{slug}@{version}`,
  `rate-tables/{slug}@{version}/…`, `regression-suites/{slug}@{version}` (`:780-799`).
- **A routing trap, proved.** Starlette matches routes in registration order, and
  `{rating_version_id}` matches any one path segment, `motor-gb@27` included. A scratch app
  with the by-id route registered first answers `GET /rv/motor-gb@27` with **422** from the
  by-id handler. With the `{slug}@{version}` route registered first, the same request
  answers 200 from the new handler, and `GET /rv/<uuid>` still reaches the by-id handler
  (a UUID has no `@`). Run 2026-10-01 10:1x BST with the repository's `.venv` FastAPI. The
  script was the session's scratch `order.py`, and its output was:
  `id-first 422  {'h': 'id'}` / `ref-first 200 {'h': 'ref'} {'h': 'id'}`.
- **The interim path.** `RatingVersionView` is at `/rating-versions/:id`
  (`frontend/src/router/index.ts:235-238`).

## Options

| | Option | Assessment |
|---|---|---|
| (a) | Add `GET /rating-versions/{slug}@{version}`; keep the `{id}` routes for actions (the plan's (a)) | Matches every other versioned read in `03` §5.1, and keeps `00` §5.6's four canonical routes and `03` §5.3 unchanged. The resolver and the response type exist. One trap: route order (above). |
| (b) | Change the §5.3 and `00` §5.6 routes to `/rating-versions/:id/…` (the plan's (b)) | Edits seven routes in two specs. URLs become opaque: an actuary cannot read or type one, and a link in a review note names no version. |
| (c) | *(not in the plan)* The view lists `GET /rating-versions` and filters on the client | No spec change, but it reads the whole workspace to find one row, on a route that is unpaginated, documented as a demo route, and due to be specified by S10. A lookup by scan is a hand-built index. |
| (d) | *(not in the plan)* `GET /rating-versions?slug=&version=` | Returns a list for a key that is unique. The caller must handle zero, one or many. It is the same lookup as (a) in a weaker form. |

## Ruled

**(a).** A Rating Version is **addressed** by its `slug@version` and read by it.
`GET /api/v1/rating-versions/{slug}@{version}` returns the `RatingVersion`, whose `id` is the
handle the existing `{id}` action routes take. In `/rating/:slug/v/:version/…`, the slug and
version are the **Rating Version's own**, never its algorithm's. The existing by-id read is
declared in `03` §5.1 beside it, so the spec states how the two forms meet.

**Why.** (a) is the form `03` §5.1 already uses for every other versioned artifact. It keeps
human-readable URLs, which `00` §5.6 already declares. It is built on mechanisms that exist:
the unique key, `resolve_rating_version_ref` and `RatingVersion`. (b) costs two specs' routes
for opaque URLs. (c) and (d) put a lookup the server can answer in one indexed read onto the
client.

**The route this ruling creates, and its types.**

| Method, path | Request body | 2xx response | Permission |
|---|---|---|---|
| `GET /api/v1/rating-versions/{slug}@{version}` | none (path only: `slug: str`, `version: int`) | **200** `RatingVersion` (`packages/model-schema/src/model_schema/rating.py:137`) | `rating:read` |
| `GET /api/v1/rating-versions/{id}` *(exists; declared, not changed)* | none | **200** `RatingVersion` (same) | `rating:read` |

No `dict[str, Any]` appears in either signature. No new model-schema type is needed.

**Not decided here.**

- Whether `RatingVersionView` (`/rating-versions/:id`) stays after S10 is S10's leaf plan's
  question.
- The list route `GET /rating-versions` is S10's spec change (`PL-1286` S10).
- The algorithm-by-`{slug}@{version}` load route is DP-4's. The maintainer ruled it (a). Its
  FR and §5.1 row are still owed as a decision-maker spec text before S2's leaf plan goes
  `active`, and this record does not write them.

## Spec changes this ruling requires

These are applied by **Slice 2's spec-first step** under `.claude/skills/spec-change`, in the
same commit as the route's code and tests (`CLAUDE.md` §2). They are not applied in this
commit, and `PL-1286` is not edited. Placement was read at origin/main `1dd5e264`.

Placeholders: `RL-<this>` is this record's minted id. `FR-<new>` is the requirement id
minted for T1 when it is applied. `<date>` is the date of the applying commit. Nothing else
in a text is a placeholder.

**T1 — `03` §3.4, a new FR.** Placement: `docs/specs/03-rating-engine.md`, §3.4 *Rating
versions and bundles*. **Insert one new row immediately after the row that begins
`| **FR-243** |`** (`:140`), as the last row of that table. Nothing is struck.

```text
| **FR-<new>** | **A Rating Version is addressed by its `slug@version`; its `id` is a handle, not an address.** *(Added <date>, `RL-<this>`, `PL-1286` DP-5.)* The pair `(slug, version)` is unique within a workspace, and every §5.3 view route names a Rating Version by that pair: in `/rating/:slug/v/:version/…`, `:slug` and `:version` are the Rating Version's own `slug` and `version` (§4.3), never its algorithm's, whose version is read from `algorithm_ref`. `GET /api/v1/rating-versions/{slug}@{version}` reads the version by the pair. Its response carries the `id` that the §5.1 routes keyed by `{id}` take, so a view resolves the pair once and then acts by `id`. Both reads, by pair and by `id`, require `rating:read` and answer **404** `NOT_FOUND` for another workspace's version exactly as for one that does not exist. `00` §5.6's routes are unchanged. |
```

**T2 — `03` §5.1, two rows.** Placement: the §5.1 table. **Insert these two rows
immediately after the row that begins `| `POST` | `/api/v1/rating-versions` |`** (`:792`),
before the `compile` row. Nothing is struck.

```text
| `GET` | `/api/v1/rating-versions/{slug}@{version}` | Read one Rating Version by its `slug@version` (FR-<new>); requires `rating:read`. **200** with a `RatingVersion` (§4.3); 401; 403; **404** `NOT_FOUND` on an unknown version or another workspace's. Registered before the `{id}` read, which would otherwise take the request. **Added <date>** (`RL-<this>`) |
| `GET` | `/api/v1/rating-versions/{id}` | Read one Rating Version by `id`, the handle the `{id}` routes below take (FR-<new>); requires `rating:read`. **200** with a `RatingVersion` (§4.3); 401; 403; **404** `NOT_FOUND` on an unknown id or another workspace's. Built in Phase 1b (FR-440); declared here <date> (`RL-<this>`) |
```

The executor applies each text above byte-for-byte; authorship stays with the decision-maker (document-ids §1.6 FR row; CLAUDE.md §2 one-commit rule; the RL-1296 precedent). Any executor wording is a stop. If a text's anchor row is not found exactly once, that is a stop too, reported to the lead; the executor does not re-word it.

## What it obliges

- **This commit:** this record only.
- **`PL-1286`, the planner's file, is not edited here.** DP-5's *Resolved by* cell cites this
  record once it is minted.
- **Slice 2 (WK-675)**, in one commit with T1 and T2:
  - the handler sits in `backend/src/app/api/models.py` beside the by-id read, and is
    **registered before it**. It is typed `-> RatingVersion` and reads through
    `resolve_rating_version_ref` and `rating_versions_service.to_schema`, with no new query;
  - `docs/contracts/` is regenerated (`uv run python scripts/generate-contracts.py`), and
    the frontend reads the version through the generated client only;
  - every view at `/rating/:slug/v/:version/…` resolves the pair through this route and
    calls `{id}` routes with the returned `id`.
- **Slices 3–8, 10 and 11** use the same resolution. None of them adds a second lookup.
- **Contention** (`PL-1286` *Sequencing*): T1 is in `03` §3.4, where S10's FR also lands, and
  T2 is in `03` §5.1. Both serialise as that table says.

## Acceptance — the violation that must become detectable

The violation: **a view route that resolves to the wrong Rating Version, or to none.** Each
test carries `@pytest.mark.req("FR-<new>")` and is shown red on deliberately broken input.

1. **Order.** `GET /rating-versions/motor-gb@27` answers 200 from the new handler, and
   `GET /rating-versions/<that version's id>` still answers 200 by id. Broken input: register
   the by-id route first, and the first request answers 422.
2. **Whose version.** In a fixture where the version's `version` differs from its
   `algorithm_ref` version, the route answers by the Rating Version's own number, and asking
   by the algorithm's number answers 404. Broken input: resolve by the algorithm ref.
3. **Isolation.** Another workspace's `slug@version` answers 404 `NOT_FOUND`, the same body
   as an unknown pair.
4. **Permission.** A principal without `rating:read` gets 403.
5. **Contract.** The operation's 200 response in `generated.json` is a `$ref` to
   `RatingVersion`, and `uv run python scripts/generate-contracts.py --check` exits 0.
6. **Frontend (FR-25).** One view test (id `FR-<new>` in its name) mounts a
   `/rating/:slug/v/:version/…` route and asserts that the generated client was called with
   the slug and version from the URL.
