---
id: RL-1835
family: ruling
title: SL-1554 (WK-675 S9) decided — a pinned sub-graph mount is its own node on the designer canvas, edited in the inspector, a purpose mount marked on the node; FR-218's mount declaration is the in-graph mount's `purposes` and is in scope, the Rating Version's pin is not; no list route is needed, the picker offers the Rating Version's sub-graph pins
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-21
owner: decision-maker
tree: 92c68396ab9fdeefab89bf228023a171dfa3ed7c
phase: P2
work: WK-675
slice: SL-1554
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1546, PL-1286, SL-1554, WK-675, WK-1250, FR-217, FR-218, FR-219, FR-212, FR-237, FR-1607, NFR-463, RL-1309, RL-1344, RL-1628, RL-1473]
---

# RL-1835 — SL-1554 (WK-675 S9): the three open points of sub-graph mounting in the designer

Disclosure: drafted as **working id RL 8143**; minted as RL-1835 on 2026-10-21, in the D29 batch mint PR. Drafted by
the decision-maker seat dm-8143. The maintainer adopts, amends or rejects this draft before
the mint; until then it binds nothing.

## Authority and scope

The maintainer's entry "2026-10-21 15:15:40 BST" in `~/gi-pricing-plan.local/channel/to-lead.md`,
item 2, verbatim (read at line 28312 on 2026-10-21):

> **2. SL-1554 (S9) — GO, but as a decision-maker RL (working id 8143), NOT a new leaf plan.**
> - Lean P2 (8 Oct) allows one plan per Work. PL-1546 is WK-675's plan, and its row 8 makes the PL-1286 S9 row this slice's scope. The open points are decisions, not planning: (i) the UI shape, (ii) whether FR-218's Rating-Version mount declaration is in scope, (iii) whether a list route is needed (if yes, spec first, CLAUDE.md §0).
> - The RL rules those three points. The executor writes its tasks, write set and acceptance into its LG, as every other slice does.

This record rules points (i)–(iii) and nothing else. It is not a plan: the tasks, write set and
acceptance are the executor's, in its `LG-`, built from the rulings below. The build order
(item D of the entry "2026-10-08 14:32:33 BST", S9 last) and the activation needs are not
ruled here.

## Verified first, at origin/main 11bddecb9bcafd315617c2d5d198598c6ecfad33 (tree 92c68396ab9fdeefab89bf228023a171dfa3ed7c)

- **Scope rows.** `docs/plans/PL-01546-*:153` (row 8): "SL-1554 — S9: Designer III: sub-graph
  mounting | `PL-1286` S9 row | `03` §3.1: FR-217 (the mount), FR-218 (authoring view)".
  `docs/plans/PL-01286-*:312`: "Mounting a pinned sub-graph in the designer (FR-217, FR-218's
  authoring view)". `docs/roadmap.md:1619-1635` is the SL-1554 block and adds no task-level scope.
- **The spec.** `docs/specs/03-rating-engine.md:86` (FR-217); `:87` (FR-218, with `RL-1344`'s
  amendment of 2026-09-30: *"'Declared on the Rating Version' means declared by the algorithm
  version the Rating Version pins (`algorithm_ref`), as an ordinary sub-graph mount (FR-217) in
  the algorithm's `sub_graphs`, with an optional `purposes` selector. Its exact sub-graph version
  is pinned in the Rating Version's `pins` like every other mount; there is no second declaration
  site and no purpose-specific pin."*); `:352` (`RL-1309` DP-3: *"a mount is a node"*); `:354`
  (`RL-1628`: FR-212 per purpose; a purpose mount re-produces a parent name); `:1433` (§5.3, the
  designer cell names "sub-graph mounting"); `:1051-1054` (the four sub-graph routes).
- **The shapes** (`packages/model-schema/src/model_schema/rating.py`): `SubGraphRef` (`:466-508`)
  is `ref` (an exact `sub_graph:slug@version`), `mount_point`, `inputs`, `outputs`, `purposes`
  (absent = every purpose; else a non-empty, duplicate-free subset of `mid_term_adjustment`,
  `cancellation`). `Pins.sub_graphs` (`:85`). `_MountNode` (`:511-519`) carries the mount's
  `mount_point` as its `step_id`, so a graph-invariant issue on a mount is located by its
  `mount_point`. `AlgorithmDiff.sub_graph_mounts` (`:973`) lists each mount added, removed,
  re-pointed or re-mapped, by `mount_point` (`AlgorithmSubGraphChange`, `:916-932`).
- **The routes** (`docs/contracts/openapi/generated.json`): `POST /api/v1/sub-graphs`,
  `GET|POST /api/v1/sub-graphs/{slug}/versions`, `GET /api/v1/sub-graphs/{slug}@{version}`
  (200 = `SubGraph`: `slug`, `version`, `inputs`, `outputs`, `steps`, `change_note`). There is
  **no** `GET /api/v1/sub-graphs` (all slugs), and no route that edits an existing Rating
  Version's `pins` (`/api/v1/rating-versions` has `GET`, `POST`; `/{id}` only `GET`).
- **The designer today.** `frontend/src/views/RatingDesignView.vue` loads the Rating Version and
  the algorithm it pins, and saves a new algorithm version; a version with no algorithm shows
  *"pinning it to the version is not part of this view"* (`:143`). It passes
  `rating.pins?.rate_tables` to the designer (`:208`), and `StepInspector.vue:359-380` offers a
  `table` step's rate table from those pins only (*"Only the tables this Rating Version pins."*).
  No designer file reads or writes `sub_graphs` (a grep for `sub_graph|subGraph|SubGraph|mount_point|purposes`
  under `frontend/src`, excluding `generated/`, hits only `sub_graphs: []` at
  `RatingDesignView.vue:54` and two test fixtures).
- **The validate route.** `backend/src/app/platform/rating_algorithms.py:381-391`
  `validate_draft` runs `graph_invariant_issues` (mounts as nodes, per purpose) then
  `validate_algorithm`. It does **not** read the fragment: a port map checked against the pinned
  fragment's ports, and a purpose mount reaching `risk_premium_minor`, are compile's (`03:985`,
  `:963`; `RL-1628`).

## Ruled

### (i) The UI shape — a mount is its own node on the canvas, edited in the inspector

1. **A mount is a node, never a side panel.** Each `SubGraphRef` in the draft's `sub_graphs` is
   one node on the Vue Flow canvas, of a node type distinct from a step's, with node id = its
   `mount_point`. Reason: the spec and the code already treat it as one — `03:352` (*"a mount is a
   node"*), `_MountNode`, FR-1399's *"A mount (FR-217) is a node of the parent's graph"* — so the
   validate route's issues (located by `step_id` = `mount_point`) and the diff (by `mount_point`)
   land on it with no translation. A panel would show a graph element off the graph, and its
   edges — which values it consumes and produces — would not be visible at all.
2. **The node is collapsed.** It shows the `mount_point`, the mounted `slug@version`, and its
   purpose marking (item 4). The fragment's own steps are not drawn and are not editable in this
   view: authoring a fragment is `POST /api/v1/sub-graphs[/{slug}/versions]`, not S9's
   (`PL-1286:312` is "mounting"), and mounts are one level deep (`RL-1309`).
3. **Edges.** A mount consumes the parent values its `inputs` map to and produces the parent names
   its `outputs` map to, and the canvas draws its edges by the same producer → consumer rule as a
   step's (`graph.ts` `edgesOf`), the mount counted as a node.
4. **Purpose-conditional mounts.** A mount with `purposes` carries, on the node, a visible text
   badge naming its purposes (e.g. "MTA only", "Cancellation only", "MTA + cancellation") and a
   dashed border, and the edges into and out of it are dashed. A mount without `purposes` carries
   neither. The text badge is the non-colour channel (NFR-463); the dashing is an addition, not
   the only signal. Reason: a purpose mount re-produces a parent name (`RL-1628`), so its node
   sits on an edge the base graph also has; the reader must see that the detour runs only for an
   MTA or cancellation quote. No per-purpose canvas filter is ruled: the validate route already
   reports each purpose graph's issues on the node (FR-212 per purpose, `03:354`).
5. **The inspector edits the mount**, as it edits a step: the sub-graph version (a select, item
   (iii)); the `mount_point`; one row per input port of the pinned fragment, each mapped to a
   parent name (every input port is required, `03:352`); one row per output port, mapping
   optional (a non-empty subset, `03:352`); and `purposes` as exactly two checkboxes,
   `mid_term_adjustment` and `cancellation`, none checked meaning "every purpose" (the field is
   then omitted, never `[]` — `SubGraphRef` refuses an empty list). The port names and types come
   from `GET /api/v1/sub-graphs/{slug}@{version}`, read through a function in a new
   `frontend/src/api/` module over the generated `SubGraph` type; no port shape is hand-written
   (`CLAUDE.md` §2, §3).
6. **Adding and removing** a mount are reachable from the same controls that add and remove a
   step, and **the keyboard path covers mounts**: `NodeNavigator.vue` lists each mount as an
   option (NFR-463; RS-1269 F2 condition 2, quoted in that file's header).
7. **The diff overlay marks a mount** added, removed or changed from
   `AlgorithmDiff.sub_graph_mounts`, as it marks a step from `added_steps`, `removed_steps` and
   `changed_steps`. Reason: the mount is now a node the canvas shows, and an overlay silent about
   it would report "no change" on a version whose refund maths moved.

**Testable as:** a draft with one unconditional and one `purposes: ["cancellation"]` mount
renders two mount nodes with their `mount_point`s, the second with the cancellation badge and a
dashed border and the first with neither; an edge is drawn from the producer of each mapped input
and to each consumer of each mapped output; a validate-route issue whose `step_id` is a
`mount_point` is shown on that node; the inspector's input-port rows are exactly the fragment's
input ports; unchecking both purposes saves a body with no `purposes` key; `NodeNavigator` lists
both mounts; a diff with one `sub_graph_mounts` entry marks that node and no other.

### (ii) FR-218's Rating-Version mount declaration — in S9's scope as the in-graph mount; the pin is not

1. **In scope.** Under FR-218 as amended by `RL-1344` (quoted above), the "declaration on the
   Rating Version" **is** the in-graph mount with its `purposes` selector, in the algorithm the
   Rating Version pins; there is no second declaration site. Authoring `purposes` on a mount
   (item (i)5) is therefore FR-218's authoring view, and S9 delivers it. There is nothing
   separate to declare.
2. **Out of scope: writing the Rating Version's `pins`.** The exact sub-graph version is pinned in
   `pins.sub_graphs`, which is set only when a Rating Version is created (`POST
   /api/v1/rating-versions`, `RatingVersionCreate`); no route edits an existing version's pins,
   and the designer already states that pinning *"is not part of this view"*
   (`RatingDesignView.vue:143`). S9 adds no pin-writing control and no route. This is the same
   boundary the rate-table step has today.
3. **Shown, not enforced, in the view: a mount whose version this Rating Version does not pin.**
   A loaded algorithm can name a sub-graph version absent from `rating.pins.sub_graphs`; compile
   refuses it with `RATING_VERSION_UNPINNED` (`03:963`). The node shows that as a warning in text
   ("not pinned by this Rating Version"). It does not block saving the algorithm, because the
   algorithm is a valid artifact and the pin is the Rating Version's act.
4. **Not shown in this view: the compile-time mount checks** — a port map against the fragment's
   declared ports, an incompatible port type, a purpose mount reaching `risk_premium_minor`.
   `validate_draft` does not read the fragment, so the designer cannot report them before save;
   the compile route reports them. S9 does not move them into the validate route (that is a
   backend change to FR-1607's route, outside `PL-1286:312`). The inspector's port rows (item
   (i)5), built from the fragment's own ports, prevent the unmapped and undeclared cases at
   authoring time.

**Testable as:** with a Rating Version whose `pins.sub_graphs` omits the mounted version, the
node shows the not-pinned warning and the save control stays enabled; no request in the slice's
tests is a write to `/api/v1/rating-versions`.

### (iii) A list route — not needed; no spec change precedes S9

1. **The picker offers the Rating Version's sub-graph pins.** The inspector's sub-graph select
   lists exactly `rating.pins.sub_graphs`, as the rate-table select lists exactly
   `rating.pins.rate_tables` (`StepInspector.vue:363`). Reason: a mount the Rating Version does
   not pin cannot compile (FR-237, *nothing is unpinned*; `RATING_VERSION_UNPINNED`), so offering
   any other version would offer a mount that cannot price. The ref is an exact version
   (`SubGraphRef.ref`), so no "latest" lookup is needed either.
2. **The port read uses an existing route**, `GET /api/v1/sub-graphs/{slug}@{version}`.
   `GET /api/v1/sub-graphs/{slug}/versions` exists but S9 needs it for nothing.
3. **Therefore no new route, no new FR and no §5.1 row are required, and `CLAUDE.md` §0's
   spec-first step does not arise.** S9 changes no `model-schema` shape and no
   `docs/contracts/` file. A workspace-wide sub-graph catalogue (`GET /api/v1/sub-graphs`) is a
   capability for whoever builds sub-graph authoring or a pin-setting view; it is not ruled here.
4. **An empty pin list.** Where `rating.pins.sub_graphs` is empty, the add-mount control is
   disabled with a text reason ("this Rating Version pins no sub-graph"), not hidden.

**Testable as:** the select's options equal the Rating Version's `pins.sub_graphs` in a test with
two pinned versions; with none pinned, the add-mount control is disabled and the reason is shown;
the slice's diff touches nothing under `packages/model-schema/`, `backend/` or `docs/contracts/`.

## What it obliges

- SL-1554's executor writes its `LG-` tasks, write set and acceptance from (i) items 1–7,
  (ii) items 1–4 and (iii) items 1–4, and cites this record by id at each.
- The write set stays under `frontend/` (the designer components, `RatingDesignView`, a new
  `frontend/src/api/` module for the sub-graph read, and their tests). A change under
  `packages/model-schema/`, `backend/`, `docs/contracts/` or `docs/specs/` is outside this
  ruling and is a stop to the lead.
- `PL-1546` and `PL-1286` are not edited; this record stands beside them.

## Acceptance — the violation that must become detectable

Each violation below is caught by a frontend test that fails on the broken input, shown red
once, per `CLAUDE.md` §13:

- *a mount drawn off the canvas, or not drawn:* a draft with two mounts renders two mount nodes
  whose ids are their `mount_point`s;
- *a purpose mount indistinguishable from an unconditional one:* the cancellation-only mount
  carries the badge text and the unconditional one does not;
- *a mount issue lost:* a validate-route issue with `step_id` = a `mount_point` is shown on that
  node;
- *an incomplete port map authored:* the inspector's input-port rows equal the fragment's input
  ports, read through the generated `SubGraph` type;
- *an empty `purposes` saved:* unchecking both purposes saves a body with no `purposes` key;
- *an unpinned version offered:* the sub-graph select's options equal `pins.sub_graphs`;
- *an unpinned mount hidden:* a mount whose version is not in `pins.sub_graphs` shows the
  not-pinned warning;
- *a mount change silent in the diff:* one `sub_graph_mounts` entry marks that node and no
  other;
- *a mount unreachable by keyboard:* `NodeNavigator` lists each mount.

The write-set limit in "What it obliges" is checked by reading the slice's diff at the audit.

## Not ruled here

- Whether S9 may start ahead of S8, S10 and S11 against item D's reverse ladder order: the
  census (`handover/census-planner-lanec-2026-10-21.md` §1, FLAG) leaves it to the maintainer.
- The tasks, write set and acceptance list: the executor's `LG-`, from this record.
