# W9 Implementation Plan — Rating algorithm contract, validation, bundle compilation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first slice of the `03` rating engine: the `RatingAlgorithm` contract, its save-time validation, and the `RatingVersion` bundle compilation. This is the entry slice of the full `03` surface carried from Phase 1b (F8).

**Architecture:** Three slices on the existing Phase 1b seam. Slice W9-1 defines the `RatingAlgorithm` shape in `model-schema` (the seven step types, the input contract, the outputs, sub-graphs). Slice W9-2 validates it at save time and enforces the W8-confirmed boundary guards (FR-RATE-56/57/58/59). Slice W9-3 pins a `RatingVersion`, compiles it to a self-contained Bundle, and validates the bundle (FR-RATE-22..27). The `zen-engine` 0.53.0 installed and confirmed by W8 is the execution substrate (ADR-0004).

**Tech Stack:** GoRules ZEN (`zen-engine` 0.53.0, confirmed by W8), Pydantic v2 (`model-schema`), FastAPI + SQLAlchemy (backend), `pricing-core` (the `rating/` module), Polars.

**Spec:** [`03-rating-engine.md`](../specs/03-rating-engine.md) FR-RATE-1..13, FR-RATE-22..27, FR-RATE-56/57/58/59, NFR-RATE-13/14 · [`ADR-0004`](../adr/0004-zen-engine-for-rating-execution.md) · the W8 close record (`docs/audit/work/W8/README.md`).

**Highest ids:** No new requirement id is minted in this plan.

## Global Constraints

- The gate has two halves. Both must pass before a push (CLAUDE.md §11).
- Write prose in ASD-STE100. Code, identifiers and file paths stay unchanged.
- A filed plan stays frozen at its date. The plan file commits on the branch, never copied back.
- Requirement ids are permanent. Append, never renumber (CLAUDE.md §5).
- Every spec change runs `python3 scripts/audit-docs.py` before commit (CLAUDE.md §0).
- Nobody hand-writes a shape that already exists in `model-schema`.
- Money is integer minor units or Decimal in the rating path, never float (CLAUDE.md §7).
- `pricing-core` stays importable standalone with zero FastAPI/SQLAlchemy/Redis deps.
- The engine is confirmed by W8. W9 builds the contract and the compilation on it.
- The three slices run one at a time. Each slice is executed and audited with the work-item-close checklist before the next slice starts. No batching all slices and one audit at the end.
- A filed plan under `docs/plans/` stays frozen at its date.

---

## Scope and requirement coverage

| Requirement | Slice |
|---|---|
| FR-RATE-1 (DAG, cycles rejected) | W9-1, W9-2 |
| FR-RATE-2 (typed input contract) | W9-1 |
| FR-RATE-3 (typed outputs, premium ladder) | W9-1 |
| FR-RATE-4 (stable step_id) | W9-1 |
| FR-RATE-5 (topological, deterministic) | W9-2, W9-3 |
| FR-RATE-6 (sub-graphs) | W9-1 |
| FR-RATE-7 (structural diff) | W9-1 |
| FR-RATE-8 (`table` steps pin rate tables) | W9-1, W9-3 |
| FR-RATE-9 (`lookup` steps, as-at date) | W9-1 |
| FR-RATE-10 (`model_call` mode) | W9-1, W9-3 |
| FR-RATE-11 (`constraint` steps, reason codes) | W9-1 |
| FR-RATE-12 (`output` rounding) | W9-1 |
| FR-RATE-13 (result types checked at save) | W9-2 |
| FR-RATE-22 (nothing unpinned) | W9-3 |
| FR-RATE-23 (lifecycle) | W9-3 |
| FR-RATE-24 (self-contained Bundle, content hash) | W9-3 |
| FR-RATE-25 (bundle compilation validates) | W9-3 |
| FR-RATE-26 (effective dates) | W9-3 |
| FR-RATE-27 (change summary) | W9-3 |
| FR-RATE-56 (money crosses as integer minor units) | W9-2, W9-3 |
| FR-RATE-57 (division guarded) | W9-2, W9-3 |
| FR-RATE-58 (scale cap checked) | W9-2, W9-3 |
| FR-RATE-59 (vocabulary validated against engine) | W9-2, W9-3 |
| NFR-RATE-13 (validate inbound, never outbound) | W9-3, design constraint |
| NFR-RATE-14 (`nthread=1` per model_call) | W9-3, design constraint |

---

## Findings (verified 2026-08-27 against origin/main `cdedef8`)

**F1. The `03` module is greenfield beyond the Phase 1b seam.** `backend/src/app/platform/rating_versions.py` carries the Phase 1b minimal `RatingVersion` (slug, version, status, a single pinned model, FR-PLAT-67). No `RatingAlgorithm` shape, no `rating/` module in `pricing-core`, no `rating-algorithms` route, and no FR-RATE marker exists. The Phase 1b `RatingVersion` in `model-schema` carries only the subset `03` §4.3 scopes.

**F2. W8 confirmed the engine and the guards.** The W8 close record (`docs/audit/work/W8/README.md`) records zen-engine 0.53.0 installed and pinned, the S1 suite re-run with 21 checks and 0 failed, the S2 latency re-run (NFR-RATE-14 p99 1.626 ms, 3.3 % of the 50 ms budget), the NFR-RATE-13 premise amended, and the ADR-0004 addendum confirming the decision at Phase 2 entry. W9 proceeds on that basis.

**F3. The boundary guards are specified and unbuilt.** FR-RATE-56/57/58/59 carry the spike evidence. None has a marker. W9's validation and bundle-compilation slices build them.

---

## The three slices

**Sequencing:** the slices run one at a time. The executor finishes W9-1, the auditor audits it against the work-item-close checklist, and only then does W9-2 start. The same holds between W9-2 and W9-3. The audit is per-slice, never one audit after all three.

### Slice W9-1 — the RatingAlgorithm contract

**T1. model-schema: the algorithm shape.**

- [ ] Add `RatingAlgorithm` to `packages/model-schema/src/model_schema/rating.py` or the module's rating section: `slug`, `version`, `input_contract`, `outputs`, `steps`, `sub_graphs` (the `03` §4.1 shape).
- [ ] Add the seven step types as a discriminated union: `input`, `lookup`, `table`, `expression`, `model_call`, `constraint`, `output`. Each declares its key fields from `03` §3.2.
- [ ] Add the `InputContract` entry shape: name, type (`int`, `decimal`, `string`, `date`, `bool`, `enum`), nullability, range or domain, description (FR-RATE-2).
- [ ] Add the `Output` shape: name, type, required flag, the money and ladder conventions (FR-RATE-3).
- [ ] Add the sub-graph shape: a versioned artifact reference and a mount point (FR-RATE-6).
- [ ] Add the money types: a monetary result is `decimal` or `money_minor` (FR-RATE-13, R2).
- [ ] Add model-schema tests: a valid algorithm parses. The seven step types accept their fields. A monetary result typed as float is refused.

**T2. The step invariants.**

- [ ] Enforce a stable `step_id` (FR-RATE-4): the id never changes on a label rename.
- [ ] Enforce every `consumes` name is produced by exactly one upstream step (FR-RATE-1).
- [ ] Enforce every declared output has an `output` step (FR-RATE-3).
- [ ] Enforce `model_call` declares a mode, exact or approximation (FR-RATE-10).
- [ ] Enforce `output` steps declare rounding explicitly (FR-RATE-12).
- [ ] Add negative tests: a cycle, an orphaned step, an undefined reference, a missing output step.

**T3. The structural diff.**

- [ ] Implement the structural diff between two algorithm versions: steps added, removed, or changed, and tables re-pointed (FR-RATE-7).
- [ ] Add tests that the diff names the change and attaches to the approval request.

**Slice gate:** the `RatingAlgorithm` shape parses, its invariants hold, and the diff names changes.

### Slice W9-2 — save-time validation

**T1. The algorithm validator.**

- [ ] Implement `validate_algorithm` in `packages/pricing-core/src/pricing_core/rating/compile.py` per `03` §5.2.
- [ ] Check the DAG is acyclic and fully connected (FR-RATE-1).
- [ ] Check every result type is compatible at save time (FR-RATE-13).
- [ ] Check evaluation is deterministic: no wall-clock reads, no randomness, no external calls beyond pinned model invocations (FR-RATE-5).
- [ ] Add tests: a cyclic graph fails, a type mismatch fails, a non-deterministic step fails.

**T2. The boundary guards.**

- [ ] Enforce FR-RATE-56: money crosses the engine boundary only as integer minor units. A startup self-check asserts the round-trip.
- [ ] Enforce FR-RATE-57: every division in a rateable path carries an explicit zero guard. Bundle compilation rejects an unguarded division.
- [ ] Enforce FR-RATE-58: no rate table value, constant, or intermediate requires a decimal scale beyond 28.
- [ ] Enforce FR-RATE-59: the expression step's function vocabulary is validated against the engine's real vocabulary.
- [ ] Add tests per guard, each proven to fail on broken input.

**T3. The endpoint.**

- [ ] Add `POST /api/v1/rating-algorithms` and the version/diff routes from `03` §5.1.
- [ ] Save-time validation runs before the algorithm persists.
- [ ] Add backend tests: an invalid algorithm is refused with the named error. A valid one saves.

**Slice gate:** an invalid graph is refused at save time, and the four boundary guards fail on deliberately broken input.

### Slice W9-3 — bundle compilation

**T1. The full RatingVersion shape.**

- [ ] Widen the Phase 1b `RatingVersion` in `model-schema` to the `03` §4.3 contract: `algorithm_ref`, `pins`, `model_reference_mode`, `effective_from` and `effective_to`, `bundle`, `change_summary`, `evidence`, `approval_request_id`.
- [ ] Keep the Phase 1b fields working. The `03` §4.3 scoping note records the Phase 1b subset. This slice widens it.
- [ ] Enforce the invariants: every pin resolves to an artifact at `approved` or better (FR-OVR-14). Every `model_call` mode equals `model_reference_mode` (FR-RATE-60).
- [ ] Add model-schema tests: a version with an unpinned reference fails. A mode mismatch fails.

**T2. The lifecycle.**

- [ ] Implement the `draft → review → approved → live → retired` transitions (FR-RATE-23).
- [ ] Only `approved` versions can deploy. `live` is a property of a Deployment, not the version.
- [ ] Add the effective-date fields (FR-RATE-26): effective dates are metadata, not a runtime selector.
- [ ] Add the change summary (FR-RATE-27): a required field, drafted from the diffs and edited by the actuary.
- [ ] Add tests for the transitions and the invariants.

**T3. The compiler.**

- [ ] Implement `compile_bundle`, `to_jdm`, and `bundle_hash` in `packages/pricing-core/src/pricing_core/rating/compile.py` per `03` §5.2.
- [ ] The Bundle is self-contained: sufficient to score with no database access (FR-RATE-24, NFR-RATE-3).
- [ ] The Bundle carries a reproducible content hash from the pins.
- [ ] Compilation validates the whole structure: DAG, references, types, constraints, no `control`-intent factor in a rateable path, no unapproved custom objective transitively reachable (FR-RATE-25).
- [ ] Compilation re-checks the boundary guards: division, scale cap, vocabulary (FR-RATE-57/58/59).
- [ ] Add the scoring-path discipline as a design constraint: the compiled form respects NFR-RATE-13 (no outbound validation) and NFR-RATE-14 (`nthread=1`).
- [ ] Add tests: a valid bundle compiles and hashes. Each validation failure is named.

**T4. The compile endpoint.**

- [ ] Add `POST /api/v1/rating-versions/{id}/compile` per `03` §5.1.
- [ ] Compilation runs as a Job or synchronously, matching the `07` FR-PLAT-13/15 model.
- [ ] Add backend tests: compile succeeds on a valid version and fails with named errors on an invalid one.

**Slice gate:** a pinned version compiles to a self-contained Bundle with a reproducible hash, and every validation failure is named.

---

## The folded-in deferred items

- **F8 — the full `03` rating surface.** W9 is the entry slice. Compile, score, rate tables, and deployment stay in W9 to W14. W9 builds the contract, the validation, and the bundle.
- **F9's `03` parts — Peril Structure and reconciliation.** The `model_call` step type pins a Peril Structure (`03` §4.1, FR-RATE-10). A Rating Version pins an approved Peril Structure whose reconciliation (FR-MODEL-60) is on file (FR-OVR-14). W9's contract supports the `peril_structure_ref`. The Peril Structure artifacts themselves stay 02-owned.

---

## Decision points

**DP1 — the compiled Bundle's concrete format.** The spec gives the function signatures and the "self-contained" property but not the bundle's internal shape. **Recommendation:** the Bundle is the JDM graph plus the pinned artifacts' resolved payloads, wrapped by the `pricing-core` facade (ADR-0004). The content hash covers the graph and the pinned artifact hashes.

**DP2 — sub-graph support in the first pass.** FR-RATE-6 allows composing from versioned sub-graphs. Options: build the sub-graph reference and inlining in W9-1, or declare the reference and defer the inlining. **Recommendation:** build the reference and the inlining in W9-1. The mount point is already in the `03` §4.1 example.

**DP3 — the lifecycle ceiling.** FR-RATE-23 names `draft → review → approved → live → retired`. Deployment is W14. Options: W9 builds through `approved` and declares `live`/`retired` transitions for the deployment slice, or W9 builds the full transition set. **Recommendation:** build through `approved` now. The `live` and `retired` transitions belong with the deployment slice.

**Ruled 2026-08-27 (decision-maker) — all three confirmed.**

- **DP1 confirmed.** The Bundle is the JDM graph plus the pinned artifacts' resolved
  payloads, wrapped by the `pricing-core` facade (ADR-0004). The content hash covers the
  graph and the pinned artifact hashes. This matches FR-RATE-24's self-contained bundle
  and the spec's Bundle and Compiled Bundle definitions.
- **DP2 confirmed.** Build the sub-graph reference and the inlining in W9-1. FR-RATE-6
  requires sub-graphs to be "inlined at bundle time"; deferring the inlining would
  contradict the requirement. The mount point is already in the `03` §4.1 example.
- **DP3 confirmed.** Build through `approved`; declare `live`/`retired` for the
  deployment slice W14. FR-RATE-23 makes `live` a property of a Deployment, so the
  transition belongs with W14.

---

## Verification

- Both gate halves pass locally before a push:
  - `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
  - `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
  - `uv run python scripts/generate-contracts.py --check`
- Every in-scope FR-RATE carries a marker. The boundary guards fail on deliberately broken input.
- A pinned version compiles to a self-contained Bundle with a reproducible hash.
- The `RatingAlgorithm` shape matches `03` §4.1, and the `RatingVersion` shape matches §4.3.

---

## Sources

- `docs/specs/03-rating-engine.md`: FR-RATE-1..13, FR-RATE-22..27, FR-RATE-56/57/58/59, NFR-RATE-13/14, §4.1, §4.3, §5.1, §5.2.
- `docs/adr/0004-zen-engine-for-rating-execution.md`: the decision and the 2026-08-27 addendum.
- `docs/audit/work/W8/README.md`: the W8 close record and the confirmation evidence.
- `docs/plans/2026-08-27-w8-spike-resolution.md`: the W8 plan.
- `docs/roadmap.md` §7: the W9 row and the Phase 2 workstreams.
- `backend/src/app/platform/rating_versions.py`: the Phase 1b seam this plan widens.
