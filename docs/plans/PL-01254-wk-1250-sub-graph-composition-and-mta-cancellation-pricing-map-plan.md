---
id: PL-1254
family: plan
kind: map
title: WK-1250 — Sub-graph composition and MTA/cancellation pricing (FR-217's inlining and pin, FR-218's authoring half): map plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-29
owner: planner
tree: f0c3d197f5d89863efc647a2d7c1a6994b74dd63
phase: P2
work: WK-1250
supersedes: []
superseded_by: ~
corrected_by: []
relates: [CR-1247, CR-838, RL-1242, FD-1241, PL-1237, PL-1070]
---

# WK-1250 — Sub-graph composition and MTA/cancellation pricing: map plan

> **For agentic workers:** this is a **map plan**. It cuts WK-1250 into three slices and fixes their scope, order, dependencies and gates. It carries no code steps. Each slice gets its own leaf plan (`kind: leaf`) before it starts, and the executor works from that leaf plan. REQUIRED SUB-SKILL for each leaf plan's executor: subagent-driven-development (recommended) or executing-plans. Each executor also binds `spec-change` (every slice opens with a spec change), `contract-schema` and `contract-guard` (the new shapes), `python-package`, `python-test` (requirement markers, negative tests), `fastapi-service` (Slice 1's routes) and `dev-commands` (the gate), and reads `docs/plans/README.md`'s five unchecked conventions before its first step.

## Goal

Make FR-217 true and FR-218 authorable. A sub-graph becomes a stored, versioned artifact. A Rating
Version pins the exact version of each sub-graph its algorithm mounts. `compile_bundle` inlines the
pinned sub-graph at its mount point, so the compiled bundle, its hash and its trace carry it. A
Rating Version can then declare a sub-graph mounted only for `purpose ∈ {mid_term_adjustment,
cancellation}`. That lets an MTA or a cancellation be priced by the same risk price plus its
separately versioned refund and charge maths. The interim refusal of every such quote (#907,
`RL-1242`) is replaced by the real check, and `RL-1242`'s interim rule is retired in the same
commit.

The Work is done when FR-217 and FR-218 are evidenced by the limbs this Work adds (Acceptance
Standard below), FD-1241's three unbuilt limbs are built, and `RL-1242` is retired with a dated
strike.

**Architecture.** A map plan, per `docs/process/delivery-process.md` §5 step 2, in the form of
`PL-1237` (WK-674's map plan). The design direction is `CR-1247` Proposal 10, option (a), as
accepted in the maintainer's entry `2026-09-29 17:27:28 BST · maintainer (acting on the
maintainer's behalf) · ACCEPTANCES: the WK-672 Work close (#906) and plan review 16 (#905), per
proposal`, §2 row 10, and WK-1250's roadmap section (`docs/roadmap.md:850-862`).

**Tech Stack.** Pydantic v2 in `model-schema`, the new shapes (ADR-704); `pricing-core`'s
`compile_bundle` and scorer; FastAPI and SQLAlchemy 2.x async plus Alembic for the stored
artifact; GoRules ZEN, the JDM the inliner writes into. **No new dependency is planned.**

**Spec.** The executors read these with their leaf plans:
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md): §3.1, FR-217 (`03:86`) and
  FR-218 (`03:87`, with `RL-1242`'s dated interim rule); §2's `purpose` (`03:63`); §4.1's
  `RatingAlgorithm.sub_graphs` example (`03:276`); §4.3's `RatingVersion.pins` (`03:353-358`,
  four keys and no sub-graph slot) and its reproducibility invariant (`03:401`); §4.4's
  `QuoteContext.purpose` (`03:419`); §5.1 (`03:741-768`, no sub-graph route); §5.2's
  `compile_bundle` (`03:859`), `bundle_hash` (`03:861`) and `score_one` (`03:870-871`); FR-258,
  the trace (`03:175`); §10's decided OQ-617 (`03:1170`).
- [`../specs/06-governance.md`](../specs/06-governance.md): §3.3's evidence table (`06:111-121`,
  no sub-graph row), with the struck Rate Table Version row (`06:119`) as the precedent that
  DP-1 weighs; §4.2's `DEFAULT_POLICY` (`06:307-332`, no `sub_graph`).
- [`../workflows/WF-00699-approved-models-to-approved-rating-version.md`](../workflows/WF-00699-approved-models-to-approved-rating-version.md)
  step B7 (`:62`), where the Pricing Actuary "mounts the reusable `sub_graph:ncd-ladder@4`".

## Acceptance Standard

These conditions are for the Work as a whole. Each leaf plan states its own conditions for its
slice. Every command runs in the executor's own worktree, over `origin/main...HEAD`.

1. **FR-217 and FR-218 have verdicts from the limbs this Work adds.** Run `python3
   scripts/scope-audit.py RATE --sections 3.1 --extra FR-258` (§3.1 already holds FR-217 and
   FR-218; at `f0c3d197` it prints "in scope: 9", rc 0). FR-217 and FR-218 must be evidenced by
   a test this Work adds, read in the test body. **A pre-existing marker is not delivery**:
   - FR-217's only marker today is a parse of the shape
     (`packages/model-schema/tests/test_rating_algorithm.py:81`);
   - FR-218's markers test the interim refusal (`packages/pricing-core/tests/test_rating_score.py:415-476`).
2. **FD-1241's three limbs are built** (its title: "CR-838 marks FR-217 delivered, but its
   versioned-artifact, pin and bundle-time inlining limbs are not built"):
   - (a) a sub-graph is a stored, versioned artifact with routes;
   - (b) `Pins` carries sub-graphs, and `bundle_hash` changes when a pinned sub-graph's version
     changes;
   - (c) `compile_bundle` inlines each pinned sub-graph at its mount point.

   Each is proven red first on deliberately broken input. For example: a bundle whose pinned
   sub-graph version changes but whose hash does not; a mount point that names no node; a
   reference to a sub-graph that does not exist, refused **at compile**, not at score.
3. **FR-218 prices, and still refuses what it must.** On one Rating Version whose algorithm
   mounts a purpose sub-graph:
   - an MTA and a cancellation quote are priced through the sub-graph, with a payable that
     differs from the `new_business` quote by the sub-graph's own charge or refund;
   - `new_business`, `renewal` and `what_if` are unchanged;
   - a version that mounts no purpose sub-graph still refuses an MTA or cancellation quote with
     `INPUT_CONTRACT_VIOLATION`.

   Proven through `pricing-core` and through the platform routes (`/api/v1/score` and
   `/api/v1/score/compare`). The platform route is the one FD-1241's end-to-end run used.
4. **`RL-1242` is retired**, in the commit that replaces the interim guard, as `RL-1242` itself
   obliges (`RL-1242:83-85`): a dated strike on FR-218's interim-rule text in `03:87`, and a
   dated note on `RL-1242`. The interim guard's docstring in `score.py` (`:394-411`) is
   rewritten to describe the real check.
5. **The trace shows the inlined steps** (FR-258: "every step's id, label, consumed values,
   produced value"). An inlined step's id is attributable to its sub-graph and mount point.
6. **Every Decision point has its resolver before the slice it blocks starts** (`document-ids.md`
   §1.7).
7. **Every slice closes on its own clean audit** and its own item 11 (see **Tasks**).
8. **The full gate passes, both halves, on the merged tree of the last slice** (`CLAUDE.md` §11).

## Global Constraints

- **Spec first** (`CLAUDE.md` §0). `03` declares no sub-graph artifact contract, no sub-graph
  pin and no sub-graph route. Each slice opens with its spec change, through `spec-change`,
  before its code.
- **No hand-written shape `model-schema` owns** (`CLAUDE.md` §2). The sub-graph artifact, the pin
  and the purpose selector are `model-schema` shapes, and `docs/contracts/` is regenerated.
- **`pricing-core` stays standalone** (`.importlinter`). Resolution of a sub-graph goes through
  the existing `ArtifactResolver` that `compile_bundle` already takes (`03:859`).
- **The bundle hash stays reproducible from the pins** (`03:401`). Adding a pin slot must keep
  that true, and a test proves it.
- **Money** is integer minor units, or `Decimal` in the rating path. The refund and charge maths
  in a sub-graph is rating maths and follows the same rule.
- **The write path's retrofit-impossible invariants**
  ([`../process/retrofit-impossible.md`](../process/retrofit-impossible.md)):
  - every sub-graph create or version write emits its Audit Event **in the caller's
    transaction** (`:25`; `06` FR-368);
  - every route checks a permission in the backend on every request (`:31`; `06` FR-343), named
    from the permission catalogue (`RL-1236`) or added to it by the slice's spec change;
  - a created version is immutable (`:26`, artifact immutability and versioning).

  Not on that list, but binding the same way: every row carries a `workspace_id` (`00` FR-16),
  and reads are scoped to the caller's workspace as RBAC scope (`06` FR-345: role assignments
  are "workspace-wide, or limited to named Datasets, Model Families, or Rating Algorithms"),
  which exists today. A workspace is not a tenant and not an isolation boundary (`00` FR-16),
  so nothing here depends on WK-674's tenancy. Slice 1's gate proves each.
  *(Corrected 2026-09-29 on the #918 re-check, N1: the first wording tied workspace scoping to
  WK-674 Slice 1's tenant marker, which is a different thing.)*
- **Do not build ahead of the phase** (`CLAUDE.md` §0). The DAG designer's sub-graph **view** is
  WK-675's (roadmap `:862`). This Work builds the backend a designer authors against, not the view.
- **One slice at a time** (`delivery-process.md` §8), on the P2 lane **after WK-674 and before
  WK-675** (roadmap `:862`).

---

## Scope

### Requirement coverage, each id individually

| Section | Id | What it demands (short) | Slice |
|---|---|---|---|
| `03` §3.1 | FR-217 | Sub-graphs are versioned artifacts, referenced by the parent, inlined at bundle time. **Limbs:** the stored artifact (1), the pin (2), the inlining (2) | 1, 2 |
| `03` §3.1 | FR-218 | MTA/cancellation priced by the same algorithm for the risk price, with the policy-administration maths in a sub-graph mounted only for those purposes, declared on the Rating Version and version-pinned; a version mounting none refuses. **This Work's half:** the purpose mount, its pin, and the real check replacing the interim refusal | 3 |
| `03` §3.1 | FR-258 | The trace returns every step. **This Work's limb only:** inlined steps are traced and attributable. Precondition: the decision-maker's `TraceStep` ruling (`CR-1247` Proposal 3), because FD-1246 ("A scoring trace omits the algorithm's input and output steps, where 03 FR-258 says every step"; owner WK-1178) shows `_build_trace` (`score.py:669`) skipping the input/output wire nodes, which DP-3 (a)'s ports would add | 2 |

**Scope, stated so the activation accepts it knowingly.** This Work takes **all three** of
FR-217's limbs (the stored artifact, the pin, the inlining), which is wider than WK-1250's
roadmap charter, "FR-217's inlining limb" (`docs/roadmap.md:862`). The reasons:
- the charter's own words, "inlines the **pinned** sub-graph", need a pin, and a pin needs a
  stored, versioned artifact to point at;
- FD-1241's disposition routes all three unbuilt limbs to "the Work that takes FR-218's
  authoring half", which is this one.

The lead aligns the roadmap's scope line in a later roadmap PR.

### Carried obligations

- **`RL-1242`** (FR-218's interim rule, #911). It obliges "the Work that builds [FR-217's
  inlining] replaces the interim refusal with a check that the sub-graph this purpose needs is
  inlined in the bundle. It retires the interim rule in the same commit, with a dated strike"
  (`RL-1242:83-85`). → **Slice 3.**
- **#907** (`a78fe98f`, under WK-1178), the interim guard: `_check_purpose_mount` refuses every
  MTA and cancellation quote (`packages/pricing-core/src/pricing_core/rating/score.py:393-420`,
  called at `:782` and `:943`), with tests at `test_rating_score.py:415-476` and a raise-site
  count at `test_quote_input_raise_sites.py:63`. Slice 3 replaces the body. It keeps the
  refusal for a version that mounts no purpose sub-graph, and updates the raise-site count if it
  changes.
- **FD-1246** ("A scoring trace omits the algorithm's input and output steps, where 03 FR-258
  says every step"; the lead's decision: deferred with an owner, WK-1178, after the
  decision-maker's `TraceStep` ruling, `CR-1247` Proposal 3). `_build_trace`
  (`packages/pricing-core/src/pricing_core/rating/score.py:669`) skips an entry with no
  algorithm step: "the synthetic input/output wire nodes, not an algorithm step". DP-3 (a)'s
  ports make inlined input and output nodes likely. → **Slice 2's trace limb starts only after
  that ruling**, and follows it.
- **FD-1241** (severity high; the auditor's). Its three unbuilt limbs are Slices 1 and 2. **The
  finding's closure is the auditor's**, at Slice 2's close for the FR-217 limbs.
- **`CR-838`'s dated correction** (`docs/closures/CR-00838-…:46`) records "guard delivered;
  `sub_graphs` inlining NOT delivered". This Work's close record cites it. It is not edited
  here.
- **The maintainer's decision that WK-669 is not reopened** (CR-1247 P10, the entry of 16:25:49
  BST, item 4). This Work owns the remedy.

### Premises, read at `f0c3d197`

| # | Premise | Evidence | Status |
|---|---|---|---|
| a | A sub-graph is a stored artifact | `grep -rn 'sub_graph\|SubGraph' backend/src` prints nothing. There is no table; `sub_graphs` lives inside `rating_algorithms.content` JSONB (FD-1241:98). `"sub_graph"` exists only as an artifact kind (`packages/model-schema/src/model_schema/refs.py:25`) | **greenfield** → Slice 1 |
| b | A Rating Version pins sub-graphs | `Pins` (`model_schema/rating.py:63-76`): `rate_tables`, `models`, `reference_tables`, `custom_objectives`; frozen, `extra="forbid"`. `03` §4.3 lists the same four keys (`03:353-358`) | **does not reproduce** → Slice 2 |
| c | `compile_bundle` reads `sub_graphs` | `compile.py:425-492`: it resolves the four pin lists (`:467-481`), calls `to_jdm(algorithm)` (`:483`) and never reads `sub_graphs`. There is no TODO in `compile.py` | **does not reproduce** → Slice 2 |
| d | The reference shape exists | `SubGraphRef` (`rating.py:340-350`: `ref: ArtifactRef`, `mount_point: str`) and `RatingAlgorithm.sub_graphs` (`:390`); contract `docs/contracts/schemas/rating-algorithm.schema.json:89-96` | reproduces |
| e | `purpose` has the two values FR-218 needs | `QuotePurpose` (`model_schema/scoring.py:44`) includes `mid_term_adjustment` and `cancellation`; `QuoteContext.purpose` (`:101`) | reproduces |
| f | The interim guard refuses every MTA and cancellation quote | `score.py:412-420`; tests `test_rating_score.py:415-476` including the bogus-reference test (`:438-440`) | reproduces (#907) |
| g | 06 governs sub-graphs | `06` §3.3 has no sub-graph row and §4.2 no `sub_graph` policy (`06:111-121`, `:307-332`). The struck Rate Table Version row (`06:119`) is the precedent for an ungoverned artifact whose change is approved inside the Rating Version | **open** → DP-1 |
| h | A workflow uses sub-graphs | WF-699 step B7 (line 62 of its file) mounts `sub_graph:ncd-ladder@4` (FR-217). No workflow prices an MTA or cancellation | noted; the exit demo is new business |

---

## Decision points

Every row is a technical question, so each is **the decision-maker's, by `RL-`**
(`document-ids.md` §1.6; STRUCTURE §1). **None is the maintainer's**, and none is left without
a named resolver. The cells stay empty until the ruling mints, as the §1.7 form requires. The
planner rules none of them.

| # | Question | Options | Recommendation (the planner's input) | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | Is a sub-graph version a Governed Artifact with its own approval, evidence row (`06` §3.3) and `DEFAULT_POLICY` entry (§4.2)? Or does its change reach approval inside the Rating Version that pins it? | (a) Its own approval: a `06` §3.3 row, a §4.2 `sub_graph` policy, and maturity checked at compile; (b) not governed on its own: like a Rate Table Version (`06:119`, `03` FR-1186, OQ-620), its diff reaches approval inside the Rating Version row's evidence, and its version carries a change note. **Consequence:** `03` §4.3's invariant says every pin resolves to `approved` or better (FR-20, `03:399-401`), and a `rate_table` pin is exempt today (`_MATURITY_CHECK_EXEMPT`, `compile.py:314`; the `PIN_NOT_APPROVED` refusal at `:469-481`). Under (b) a `sub_graph` pin must be exempted the same way, and the FR-20 invariant in `03:401` must be clarified in the same spec change; (c) governed only when it is a purpose (MTA/cancellation) sub-graph | **(b).** A sub-graph is a fragment of an algorithm. It prices nothing until a Rating Version pins it, and that is the act `06` already approves. (a) adds an approval path and a maturity gate for an artifact that is never live on its own. (c) splits one artifact kind by its use | decision point | yes — Slice 1 | *(decision-maker, by `RL-`)* |
| DP-2 | Where is FR-218's purpose mount declared, given FR-218's "declared on the Rating Version and version-pinned like any other sub-graph"? | (a) On the algorithm: `SubGraphRef` gains an optional `purposes` selector, and the Rating Version's `pins` pin the exact sub-graph version, as it pins rate tables; (b) on the Rating Version: a separate `purpose_mounts` field outside the algorithm; (c) both, with (b) overriding (a) | **(a).** "Like any other sub-graph" puts the reference where the other sub-graph references are (the algorithm), and the pin where every other pin is (the version). The version still declares which sub-graph version prices a cancellation. (b) gives one kind of sub-graph a second declaration site. (c) is two places for one fact | decision point | yes — Slice 2 (its pin and shape land in Slice 2's spec change) and Slice 3 | *(decision-maker, by `RL-`)* |
| DP-3 | How does a sub-graph connect at its mount point? | (a) An explicit port contract: a sub-graph declares named inputs and outputs, the mount maps parent values to them, and inlined node ids are namespaced by the mount point; (b) a splice: node ids are copied into the parent graph and wired by name; (c) the sub-graph runs as a separate ZEN evaluation called from a node | **(a).** A declared interface is what lets the compiler refuse a mismatched mount at compile time. Namespaced ids keep FR-258's trace attributable. (b) makes a name clash a silent rewire. (c) is not inlining, which FR-217 names, and puts a second evaluation on the scoring path | decision point | yes — Slice 1 (the contract) and Slice 2 (the inliner) | *(decision-maker, by `RL-`)* |
| DP-4 | May a sub-graph mount sub-graphs? | (a) No, depth 1, refused at validation; (b) yes, to a fixed depth, with cycle detection; (c) yes, unbounded, with cycle detection | **(a) for this Work.** No P2 requirement or workflow needs nesting, and depth 1 keeps the pin set and the trace flat. If a need appears, it is a spec change | decision point | yes — Slice 1 (its create-time validation) and Slice 2 | *(decision-maker, by `RL-`)* |

**Slice design, decided here and not a DP.** The three FD-1241 limbs are split so that the
inliner (Slice 2) has something real to inline and pin. The stored artifact (Slice 1) comes
first, because a reference that resolves to nothing is the failure FD-1241 demonstrated. FR-218's
half (Slice 3) comes last, because its real check is "the sub-graph this purpose needs is
inlined in the bundle" (`RL-1242:83-85`), which needs Slice 2.

**Slice ids.** No `SL-` row exists for WK-1250. The three `SL-` rows are cut here and minted,
`draft`, with ids the lead issues, when this plan is activated (§1.6's SL row).

## Sequencing

```
Slice 1  the sub-graph artifact ─→ Slice 2  pin + inlining ─→ Slice 3  FR-218's purpose mount + the real check
```

Strictly one slice at a time (`delivery-process.md` §8), on the P2 lane after WK-674 closes and
before WK-675 starts (roadmap `:862`). The plan itself is drafted off the lane. Each slice depends
on the one before it:
- **Slice 2 needs Slice 1**, because it pins and inlines a stored artifact.
- **Slice 3 needs Slice 2**, because its check is that the purpose sub-graph is inlined in the
  bundle.

**Sizing, like for like with the P2 sizing table** (its rates: 0.5 / 0.75 / 1.5 days per slice;
rulings acceptance 0 / 0.25 / 0.5; the close 0.25 / 0.5 / 1). Three slices give:
- best 3 × 0.5 + 0 + 0.25 = **1.75**;
- likely 3 × 0.75 + 0.25 + 0.5 = **3.0**;
- worst 3 × 1.5 + 0.5 + 1 = **6.0** working days.

That is inside the table's band for this Work (1.25 / 3 / 7.5, assumed at 2–4 slices). *(Corrected
2026-09-29 on the audit of #918: the first draft read 1.75 / 2.75 / 5.5, which left out the
rulings overhead.)*

---

## Tasks

At this level each slice is one task: its scope, its dependency, and an outline of its gate. The
steps are written in its leaf plan. **Item 11 of every slice** is the close condition:

> **The maintainer's MERGE-ACK, naming the PR's full head SHA, is recorded in the lead's channel
> file (`~/gi-pricing-plan.local/channel/to-lead.md`), given by the maintainer or on the
> maintainer's behalf, before the lead merges. It is never posted on the PR.** And the slice's
> clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and the lead's
> merge — no maintainer acceptance line is required for a slice, and none is to be waited on.

### Task 1 — Slice 1: the sub-graph as a stored, versioned artifact (FR-217's artifact limb)

- **Scope.**
  - **The spec change first:**
    - `03` §4 gains a sub-graph data contract: the JDM fragment, its port contract per DP-3,
      its version and change note;
    - `03` §5.1 gains its routes (create a sub-graph, add a version, get one, list versions);
    - `03` §2 gains the term "Sub-graph", and `00` §2 if it is a platform entity;
    - DP-1's outcome is written into `06` where it lands.
  - The `model-schema` shape and the regenerated contracts.
  - The stored artifact: an Alembic migration (one head, `07` FR-417), the rows, the routes,
    each version immutable once created, and the resolver for `sub_graph:slug@version`.
  - Validation at create time: the fragment validates as JDM, its ports are declared per DP-3,
    and it mounts nothing per DP-4.
- **Depends on:** nothing in WK-1250. It is blocked on DP-1, DP-3 and DP-4. *(The WK-674 tenancy dependency is dropped, 2026-09-29, N1: workspace scoping is RBAC scope, not tenancy.)*
- **Gate outline.**
  - Each refusal is tested by its cause: an invalid fragment; an undeclared port; an edit to an
    existing version.
  - A resolver test: `sub_graph:slug@version` resolves to exactly that version, and an unknown
    one is refused.
  - A 403 test per route: a principal without the route's permission is refused (FR-343).
  - An audit-event test: a create or version write whose transaction commits with no Audit
    Event is shown red on deliberately broken input (FR-368).
  - An RBAC-scope test (`06` FR-345): a principal whose role assignment covers another
    workspace only cannot read or write a sub-graph in this one.
  - `generate-contracts.py --check` passes.
  - The full gate. Item 11.

### Task 2 — Slice 2: the pin and the inlining (FR-217's pin and inlining limbs; FR-258's inlined steps)

- **Scope.**
  - **The spec change first:** `03` §4.3 gains a `sub_graphs` pin slot. The reproducibility
    invariant (`03:401`) is restated to cover it. `03` §5.2's `compile_bundle` contract says it
    inlines each pinned sub-graph.
  - `Pins.sub_graphs` in `model-schema`, and the regenerated contracts.
  - `compile_bundle` resolves each `SubGraphRef` against the pinned version, refuses a reference
    that is not pinned, does not exist or has the wrong port contract, and inlines the fragment
    at its `mount_point`, with node ids namespaced per DP-3.
  - `bundle_hash` covers the pinned sub-graph through the pins.
  - The trace carries the inlined steps, attributable to their mount point (FR-258).
  - A version that pins no sub-graph compiles and scores exactly as today.
- **Depends on:** Slice 1. It is blocked on DP-2, DP-3 and DP-4. Its trace limb also waits on the decision-maker's `TraceStep` ruling (FD-1246).
- **Gate outline.**
  - Red-first proofs, each by its cause:
    - a bogus reference refused at compile, not at score (FD-1241's end-to-end case);
    - a mount point naming no node;
    - a port mismatch;
    - a nested mount (DP-4).
  - The hash test: change only a pinned sub-graph's version, and the hash changes; recompile
    the same pins, and the hash is identical.
  - A trace test on an inlined step.
  - The existing scoring and bundle suites are unchanged on versions with no sub-graph.
  - The full gate. Item 11. **FD-1241's FR-217 limbs are the auditor's to close here.**

### Task 3 — Slice 3: FR-218's purpose mount and the real check (retires `RL-1242`)

- **Scope.**
  - **The spec change first:** FR-218's mount declaration, in DP-2's shape. **`RL-1242`'s
    interim rule is struck, dated, in `03:87`**, and `RL-1242` gets a dated retirement note, in
    this slice's final commit, per `RL-1242:83-85`.
  - The purpose mount in `model-schema` (per DP-2) and its pin.
  - The scorer: an MTA or cancellation quote is priced with the purpose sub-graph inlined. Any
    other purpose is priced without it, so the risk price is the same algorithm (FR-218's "one
    risk price").
  - `_check_purpose_mount` (`score.py:393-420`) is rewritten from the interim refusal to the
    real check: refuse with `INPUT_CONTRACT_VIOLATION` when the bundle does not inline the
    sub-graph this purpose needs. Its docstring says so. The raise-site count at
    `test_quote_input_raise_sites.py:63` is updated if it changes.
  - The interim tests (`test_rating_score.py:415-476`) are rewritten to the new rule. The
    bogus-reference test moves to Slice 2's compile refusal. "No purpose sub-graph → refused"
    and "other purposes unaffected" stay.
- **Depends on:** Slice 2. It is blocked on DP-2.
- **Gate outline.**
  - Acceptance Standard item 3, through `pricing-core` and through `/api/v1/score` and
    `/api/v1/score/compare`, each red first.
  - A broken-input proof that the check is not bypassable: a version that inlines a sub-graph
    for one purpose does not price the other.
  - The full gate. Item 11.

---

## Activation

When the maintainer (or the session acting on the maintainer's behalf) accepts this plan and
activates WK-1250 (the maintainer's instruction, relayed by the lead on 2026-09-29: "I activate
WK-1250 on that map plan"), the activation commit:
1. Sets this plan `status: active`. This is permitted only when every blocking Decision point
   row has a resolver id (`document-ids.md` §1.7). Otherwise the plan stays `draft`, and the
   open rows are named in the acceptance line.
2. The lead adds the three `SL-` rows under `### WK-1250`, each `draft`, with ids the lead
   issues, and sets WK-1250 `active` on the maintainer's line.
3. `docs/INDEX.md` is regenerated in the final commit only.

## Status

- **Acceptance line:** _pending — the maintainer's dated line, or one given on the maintainer's
  behalf_.
- **Minted as `PL-1254`** at #918's merge turn, 2026-09-29, with `python3 scripts/doc-id.py next --ref origin/main` at `0d5b0765` (working id 9680 before the mint).
- **Open:** DP-1 to DP-4, all the decision-maker's.

## Self-review

1. **Spec coverage.** FR-217 (three limbs), FR-218 (this Work's half) and FR-258's inlined-step
   limb are each in the coverage table with a slice. `RL-1242`'s obligation, #907's guard,
   FD-1241 and CR-838's correction are carried with a slice or an owner.
2. **Scope boundaries.** The designer's sub-graph view is WK-675's, not built here. Nesting is
   excluded unless DP-4 rules otherwise. G2's exit demo is new business and needs none of this.
3. **Literals.** Every file:line, id and function name in the premises was read at `f0c3d197`,
   by a read-only sweep; the leaf plans re-read them at their own trees.
4. **Placeholders.** None. The empty `Resolved by` cells are the §1.7 form for open rows, and
   each names its resolver. There are no code steps; this is a map plan.
5. **Consistency.** The slice numbers in the coverage table, the carried obligations, the DP
   `Blocking` cells, the Sequencing and the Tasks agree (grep "Slice N" across the file).

---

*(Delta, row 4 (FD-1768's fix), added 2026-11-03 by the planner (seat plan-fd1768, lead 30),
on the maintainer's entry "2026-11-03 15:36:59 GMT" item (5) in
`~/gi-pricing-plan.local/channel/to-lead.md` (the G1 close schedule: "WK-1250 Wed 4 Nov"), on
the entry "2026-11-03 15:46:13 GMT" ("earlier is never blocked"), and on the calendar of the
entry "2026-11-03 15:38:58 GMT" (code freeze Tue 10 Nov 2026, docs freeze Wed 11 Nov 2026, P2
exit demo Wed 18 Nov 2026). The owed fix is the register row `docs/findings/register.md:392`
(FD-1768, MEDIUM, owner WK-1250, "**fix before close with an owner: WK-1250**, a follow-up slice
after SL-1341 merges"). SL-1341 is `closed` (`docs/roadmap.md`, its row). This plan cut
Slices 1 to 3 as Tasks 1 to 3. This row is the Work's fourth slice, in the Lean P2 form
(`.claude/roles/planner.md` "Lean P2"): one dated row in the Work's one plan. Tasks 1 to 3, the
Decision points and the rest of the plan body are unchanged.)*

**A new row 4: SL 8296 — FD-1768's fix: a sub-graph mount whose `purposes` alone changed is
worded "mount ports re-mapped" in the declared changes.** Ledger **LG 8297**. Both are working
ids, in space form until the mint. Work **WK-1250**. Order 4. It depends on SL-1341 (closed)
and on DP-5 to DP-7 below being ruled. Size 1: one `sonnet` executor. It merges by **Fri 6 Nov
2026** at the latest, and on **Wed 4 Nov 2026** if it can, so that WK-1250's close audit sees
FD-1768 discharged. The hard stop is **Mon 9 Nov 2026**, before the code freeze on Tue 10 Nov
2026 (weekdays read from `date -d <d> +%A`).

*(Added by row 4's dated line, 2026-11-03.)* Every `file:line` below is at `origin/main`
`a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe` and was read, not run.

- **R0 — the base, read.**
  - **The diff is correct.** `packages/model-schema/src/model_schema/rating.py:1093-1095`
    (`_diff_mounts`) keeps a mount whose `ref` is the same on both sides when `ports_changed` or
    `purposes_changed` is true. So a `purposes`-only change is one `AlgorithmSubGraphChange` with
    `before == after`, `ports_changed=False` and `purposes_changed=True` (the model, `:950-965`).
    This is `RL-1344` acceptance 5 ("A change to a mount's `purposes` alone appears in FR-219's
    structural diff", `RL-1344` :197-198). **`model-schema` is not changed by this slice.**
  - **The wording is wrong.** `packages/pricing-core/src/pricing_core/rating/analysis.py:662-664`
    reads `elif mount.before == mount.after:` and then
    `text = f"{point}: mount ports re-mapped ({mount.after})"`, without reading `ports_changed`
    or `purposes_changed`. A `purposes`-only change thus gets a description that names ports.
    The re-point branch (`:665-669`) adds `; ports re-mapped` when `ports_changed` is true, but
    says nothing when `purposes_changed` is true (DP-6).
  - **The strings are ruled.** `RL-1686` "Descriptions" (`:261-267`) fixes the exact forms:
    added, removed, the re-point `<mount_point>: mount <before> → <after>`, the re-map suffix
    `; ports re-mapped`, and `<mount_point>: mount ports re-mapped (<ref>)` alone. It gives no
    form for a `purposes` change, so a new form needs a ruling (DP-5).
    `packages/pricing-core/tests/test_rating_attribution.py:1356-1384`
    (`test_mount_ports_re_mapped_forms`, `req("FR-1399")`) asserts the two ported forms. No test
    changes `purposes`. The backend's change summary already words both flags
    (`backend/src/app/platform/change_summary.py:144-145`: `(ports changed)`, `(purposes
    changed)`).
  - **FR-1399 lists the mount changes** (`docs/specs/03-rating-engine.md:198`, the clause
    *(Amended 2026-10-14, WK-673, RL-1686, `FD-1660`.)*): "Each mount the structural diff
    (FR-219) reports as added, removed, re-pointed or re-mapped is exactly one derived change".
    A `purposes`-only change is none of those four words (DP-7).
- **R1 — red first, on main, DB-free.** Add `test_mount_purposes_changed_forms`, marked
  `req("FR-1399")`, to `packages/pricing-core/tests/test_rating_attribution.py`. It uses the
  file's own helpers (`_e_mounted`, `_mounted_base`, `_mounted_version`, `_candidate_version`,
  `_resolver`, `_mount_changes`). The candidate changes only the `m_ncd` mount's `purposes`
  (for example, from absent to `["mid_term_adjustment"]`; `MountPurpose`,
  `packages/model-schema/src/model_schema/scoring.py:57`). The test asserts exactly one derived
  mount change, of kind `step_changed`, whose description is DP-5's ruled form. If DP-6 is
  ruled in, a second case changes `ref` and `purposes` together and asserts the re-point form
  with DP-5's suffix. Neither the test nor its helpers need a database (no DB fixture, no
  `conftest_db`, no `DATABASE_URL` in the file or in `test_rating_dislocation.py` /
  `test_rating_score.py`, which it imports). Run it through `run-small.sh` as one file with
  `-k test_mount_purposes_changed_forms`. **Red by its cause:** an `AssertionError` on the
  description, which reads `m_ncd: mount ports re-mapped (sub_graph:ncd-ladder@4)`. A fixture or
  compile error is not the red. The `LG-` quotes the failing assert line and the actual string.
- **R2 — green.** In `analysis.py`'s mount loop, the `before == after` branch words each changed
  flag in DP-5's ruled form. Ports alone keeps today's string exactly. If DP-6 is ruled in, the
  re-point branch adds the purposes suffix after `; ports re-mapped`. Nothing else in
  `analysis.py` changes, and `test_mount_ports_re_mapped_forms` passes unedited. If DP-7 rules
  (a), FR-1399's mount sentence gets a dated amendment in the same commit as the code
  (`.claude/skills/spec-change`). No requirement id is added.
- **G — the gate.** The diff leaves `docs/` (`packages/pricing-core/**`), so the full code gate
  runs with both halves (`CLAUDE.md` §11; the common seat brief item 30). The slice runs it in a
  gate slot. The CI that fires, from the path filters: `python.yml` (`packages/**`), `docs.yml`
  (`docs/**`, the `LG-`) and `history-policy.yml`. `frontend.yml` does not fire: its filters are
  `frontend/**`, `docs/contracts/openapi/**` and `packages/pricing-core/src/pricing_core/
  modelling/**`, and `analysis.py` is under `pricing_core/rating/`. **No contract
  regeneration:** `model-schema` is not edited, so `docs/contracts/` does not move.
  `generate-contracts.py --check` is rc 0 in the gate, and any change under
  `packages/model-schema/` or `docs/contracts/` stops the slice. **When it runs:** after the
  rulings, on Tue 3 Nov 2026 overnight or Wed 4 Nov 2026. It does not run during nfr-bench-1
  (Thu 5 – Fri 6 Nov 2026): no gate and no DB window beside it. If Wed 4 is missed, the gate
  runs after the bench ends and before Mon 9 Nov 2026. The merge is not a gate, so it can go
  on any day up to the hard stop.
- **Acceptance (row 4, items A1 to A8).** Each is checkable on the slice's merge tree.
  1. A1. `git diff --name-only origin/main...HEAD` lists only
     `packages/pricing-core/src/pricing_core/rating/analysis.py`,
     `packages/pricing-core/tests/test_rating_attribution.py`, the `LG-`, `docs/INDEX.md`,
     `docs/roadmap.md` (the SL row), and `docs/specs/03-rating-engine.md` if DP-7 is (a).
     Nothing under `packages/model-schema/`, `docs/contracts/`, `backend/` or `frontend/`.
  2. A2. The `LG-` holds R1's red line, run at the base, with the failing assert and the actual
     `mount ports re-mapped` string.
  3. A3. `test_mount_purposes_changed_forms` passes at the head, and its description assert is
     DP-5's ruled string, character for character.
  4. A4. `test_mount_ports_re_mapped_forms` passes unedited:
     `git diff origin/main...HEAD -- packages/pricing-core/tests/test_rating_attribution.py`
     shows only added lines.
  5. A5. `git grep -n "mount ports re-mapped" -- packages` shows the one f-string in
     `analysis.py`, reached only when `ports_changed` is true, and the existing test lines.
  6. A6. The GREEN set is found by import closure (the common seat brief item 29), and the
     commands and the list are quoted in the `LG-`.
  7. A7. The full code gate, both halves, is green at the re-merged head. Every rc is quoted,
     and `generate-contracts.py --check` is rc 0. If DP-7 is (a), `req-coverage.py` is rc 0.
  8. A8. **FD-1768's closing act.** The auditor sets FD-1768 `status: closed` and the register
     row :392 resolved, citing the PR number and the merge commit by sha. This is the event the
     register row names ("the merge of that slice"). The act rides with the slice's mint and
     closing acts, and `docs/INDEX.md` is regenerated after it (the common seat brief item 17).
- **Decision points (the decision-maker's; each is resolved by a ruling before activation).**

  | DP | Question | Options | Recommendation |
  |---|---|---|---|
  | DP-5 | The exact description of a mount change whose `ref` did not move | (a) Keep `RL-1686`'s forms and add the same suffix form for purposes. Ports alone: `<mp>: mount ports re-mapped (<ref>)`, unchanged. Purposes alone: `<mp>: mount purposes changed (<ref>)`. Both: `<mp>: mount ports re-mapped (<ref>); purposes changed`. (b) Name the selectors: `<mp>: mount purposes <old> → <new> (<ref>)`, with a word for an absent selector (all purposes). (c) One neutral form, `<mp>: mount changed (<ref>)`, plus the suffixes. | **(a).** Every ruled string and test stays as it is. It uses the backend change summary's vocabulary ("purposes changed", `change_summary.py:145`). It needs no rendering rule for an absent selector. (b) gives more detail but needs its own rule for `None`. (c) changes the ruled ports-only string that `test_mount_ports_re_mapped_forms` asserts. |
  | DP-6 | Is the re-point branch in scope? `ref` moves and `purposes` changes too, and the description says nothing about purposes (`analysis.py:665-669`). FD-1768's disposition names only the `before == after` branch. | (a) In scope: add `; purposes changed` after `; ports re-mapped`, with one test case. (b) Out of scope: file it as a separate finding. | **(a).** It is the same loop and the same test. The description leaves out a change but does not misstate one. (b) adds a record for about 2 lines of code. |
  | DP-7 | FR-1399's mount sentence lists "added, removed, re-pointed or re-mapped" (`03`:198). A `purposes`-only change is a derived change in the code but is not named there. | (a) A dated amendment to FR-1399 in this slice, in the same commit as the code: "… re-pointed, re-mapped, or with its `purposes` selector changed …". (b) No spec edit: `RL-1344` acceptance 5 already rules that the diff carries it. | **(a).** The spec is the contract the code is written against (`CLAUDE.md` §2). Without (a), FR-1399 is silent on a change that the code derives and that A3 asserts. The cost is one sentence and a `req-coverage` run. |

- **Write set.** `packages/pricing-core/src/pricing_core/rating/analysis.py` (the mount loop,
  `:650-676`, only); `packages/pricing-core/tests/test_rating_attribution.py` (one added test);
  LG 8297 under `docs/ledgers/`; `docs/specs/03-rating-engine.md` FR-1399 (only if DP-7 is
  (a)); at the mint, the SL 8296 row under `### WK-1250` in `docs/roadmap.md`, `docs/INDEX.md`
  and the FD-1768 closing act (A8).
- **Hand-off (not this row's writes).** The rulings on DP-5 to DP-7 are the decision-maker's.
  The maintainer's GO on this row comes before the executor is briefed. The SL 8296 roadmap row
  and the mint are the lead's. The `LG-` is the executor's. FD-1768's closing act is the
  auditor's.
- **Self-review (row 4).** (1) Every cite above was read at `a8ef6f19`. (2) Every requirement
  is named by id: FR-1399, and no range is used. (3) There are no placeholders except DP-5's
  ruled string, which A3 reads from the ruling. (4) Rows 1 to 3 (Tasks 1 to 3) and the
  plan body are unchanged. This row only appends.
