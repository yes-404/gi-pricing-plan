---
id: PL-817
family: plan
kind: leaf
title: WK-668 Implementation Plan — Spike S1/S2 resolution and ADR-706 confirmation
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-27
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-27-w8-spike-resolution.md
---

# WK-668 Implementation Plan — Spike S1/S2 resolution and ADR-706 confirmation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the S1 and S2 spike findings and confirm ADR-706 as the Phase 2 entry decision. If the resolution confirms the ZEN engine and the specified requirements, WK-669 proceeds. If S1 fails, Phase 2 is re-planned.

**Architecture:** WK-668 is the Phase 2 entry gate. It installs the ZEN engine, re-runs the S1 and S2 verification suites against the installed engine, confirms the requirements the spikes produced (FR-273/274/275/276, NFR-502/501), and records a dated ADR-706 confirmation. The output is a decision record, not a build.

**Tech Stack:** GoRules ZEN (the `zen-engine` Python binding), the `library-spike` procedure for installing and verifying, `scripts/bench-model.py` for the latency measurement.

**Spec:** [`ADR-706`](../adrs/ADR-00706-gorules-zen-engine-executes-rating-dags.md) · `03-rating-engine.md` FR-273/274/275/276, NFR-502/501 · the S1 and S2 spike findings in [`docs/research/track-a-findings.md`](../research/track-a-findings.md) (F14 and F11).

**Highest ids:** No new requirement id is minted in this plan.

## Global Constraints

- The gate has two halves. Both must pass before a push (CLAUDE.md §11).
- Write prose in ASD-STE100. Code, identifiers and file paths stay unchanged.
- A filed plan stays frozen at its date. The plan file commits on the branch, never copied back.
- Requirement ids are permanent. Append, never renumber (CLAUDE.md §5).
- Every spec change runs `python3 scripts/audit-docs.py` before commit (CLAUDE.md §0).
- A later phase's capability is a spec change first (CLAUDE.md §0). WK-668 confirms. It does not build the rating engine.
- The verification follows the `library-spike` procedure. Fetch wheels without pip. Pin the version. Turn each result into a specification change.
- WK-668's closure follows the agreed closure-audit format: the work-item-close checklist and a `docs/findings/register.md` entry.

---

## What S1 tests

S1 (`docs/research/track-a-findings.md` F14, zen-engine 0.53.0) tested whether the ZEN engine preserves exact decimal money across the whole path. It found the engine exact and the binding inexact.

- **The engine is exact.** `0.1 + 0.2 == 0.3`, `1.005 * 100 == 100.5`, and `2.675 * 100 == 267.5` all hold. The engine's internal number type is `rust_decimal::Decimal`.
- **The Python binding has no decimal type.** `Decimal("1.005")` raises `TypeError`. `1/3` returns a Python float. `36120 + 7` returns `36127.0`, a float. Exactness cannot cross the boundary in either direction.
- **The consequence is FR-273.** Money crosses the boundary only as integer minor units, exactly representable in `float64` up to 2^53.
- **`log` and `sqrt` do not exist in the expression language.** They fail to parse. The real hazard is division: `1/0`, `0/0`, and `premium/0` all return `null` silently, and a null raises a `vmError` only at the point it is used. The consequence is FR-274.
- **The decimal scale is capped at 28.** `(1/3) * 3 == 1` evaluates `false`. The consequence is FR-275.
- **The expression vocabulary differs from the documentation.** `abs`, `round`, `floor`, `ceil` and `sum` are available. The two-argument `min(a, b)` and `max(a, b)` forms are rejected. The consequence is FR-276.

## What S2 tests

S2 (`docs/research/track-a-findings.md` F11 and the roadmap) tested the latency of exact-mode GBM scoring and the Pydantic baseline.

- **Exact-mode GBM latency is comfortably viable.** p99 is 1.09 ms, about 2 % of the 50 ms budget. Single-threading beats all-cores at the tail: 1.09 ms against 1.48 ms p99, 4.5 ms against 19.9 ms worst case. The consequence is NFR-501, `nthread=1` per request.
- **Pydantic validation costs about 1 ms per request.** The scoring endpoint must not apply `response_model` validation on the hot path. The consequence is NFR-502.

## The ADR-706 question

Does the GoRules ZEN engine remain the execution substrate for rating DAGs in Phase 2?

The decision was accepted and confirmed by research on 2026-08-14. The addendum records that `rust_decimal` makes engine arithmetic exact, so the decimal-semantics risk (OQ-614) did not materialise. The risk moved to the boundaries and is now specified as FR-273/274/275.

WK-668 confirms the decision at Phase 2 entry: it re-runs the S1 and S2 checks against the installed engine, verifies that the specified requirements match the engine's real behavior, and records a dated confirmation. The confirmation is the operating basis for WK-669.

## Success and failure criteria

- **S1 succeeds** when the verified engine behavior supports the specified requirements. Integer minor units cross the binding exactly. Division is guarded and compilation rejects an unguarded division. The scale cap stays within the ladder's rounding discipline. The expression vocabulary is validated against the engine. The exact-mode latency holds the budget. Then ADR-706 is confirmed and WK-669 proceeds.
- **S1 fails** when a verified behavior contradicts a requirement and no workaround exists inside the engine. Examples: an integer minor unit does not round-trip exactly, a required rateable operation cannot be expressed, or the latency budget cannot be met. Then ADR-706 is re-opened and Phase 2 is re-planned.
- **The failure decision is recorded with its evidence.** A re-plan names the contradiction, the requirement it breaks, and the alternatives to the ZEN engine.

## The Phase 1b carry-forwards

The Phase 1b close carried four items into Phase 2. None blocks WK-668. WK-668's confirmation precedes them.

- **Bandings and groupings.** The `WF-698` §4 surfaces the demo does not seed. They belong to the modelling work Phase 2 takes up.
- **The full `03` rating surface.** Compile, score, rate tables, and deployment. WK-669 to WK-674 build it.
- **FR-59 (`unrun_layers`).** The Phase 2 validation-report successor owns it.
- **FR-67.** The trigger-based deferral stays unowned until a consumer asks for exposure-ordered levels.

---

## Tasks

### T1. Add the ZEN engine and pin the version.

- [ ] Fetch the `zen-engine` wheel and its dependencies without pip, per the `library-spike` procedure.
- [ ] Pin the version. The S1 spike ran against 0.53.0. If the pinned version differs, record the delta.
- [ ] Verify the import works in the environment.

### T2. Re-run the S1 verification suite.

- [ ] Run the exactness tests: `0.1 + 0.2 == 0.3`, `1.005 * 100 == 100.5`, `2.675 * 100 == 267.5`.
- [ ] Run the binding tests: `Decimal("1.005")` raises, `1/3` returns a float, `36120 + 7` returns a float.
- [ ] Run the division tests: `1/0`, `0/0`, and `premium/0` return `null`. A used null raises `vmError`.
- [ ] Run the vocabulary tests: `log` and `sqrt` fail to parse. The two-argument `min` and `max` are rejected. `abs`, `round`, `floor`, `ceil` and `sum` are accepted.
- [ ] Record each result beside the requirement it concerns (FR-273/274/275/276).

### T3. Confirm the requirements match the engine.

- [ ] Compare each S1 result with its requirement. If the requirement disagrees with the engine, amend the requirement with a dated note.
- [ ] Run `python3 scripts/audit-docs.py` after any spec change.

### T4. Re-run the S2 latency verification.

- [ ] Measure the exact-mode GBM scoring latency at the tail.
- [ ] Verify `nthread=1` per request against the all-cores case (NFR-501).
- [ ] Verify the scoring path does not apply `response_model` validation (NFR-502).
- [ ] Record the measured numbers beside the budgets.

### T5. Confirm ADR-706.

- [ ] Add a dated confirmation note to `docs/adrs/ADR-00706-gorules-zen-engine-executes-rating-dags.md`: the S1 and S2 resolutions hold at Phase 2 entry, and the decision is the operating basis for WK-669.
- [ ] Confirm the residual risks remain specified as FR-273/274/275.

### T6. Record the success or failure decision.

- [ ] If the verification confirms the requirements, record the decision: WK-669 proceeds.
- [ ] If the verification contradicts a requirement with no workaround, record the failure: Phase 2 is re-planned. Name the contradiction and the alternatives.

### T7. Close WK-668 in the closure-audit format.

- [ ] Run the work-item-close checklist: scope, checklist, evidence, findings, sign-off.
- [ ] File the WK-668 record under `docs/audit/work/`.
- [ ] Write any open finding into `docs/findings/register.md`.
- [ ] Run both gate halves.

---

## Verification

- Both gate halves pass locally before a push:
  - `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
  - `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
- The S1 and S2 checks are recorded beside their requirements.
- ADR-706 carries the dated Phase 2 entry confirmation.
- The success or failure decision is recorded with its evidence.
- The WK-668 closure record and the register entry exist.

---

## Sources

- `docs/adrs/ADR-00706-gorules-zen-engine-executes-rating-dags.md`: the decision and its addendum.
- `docs/research/track-a-findings.md`: F14 (S1) and F11 (S2).
- `docs/specs/03-rating-engine.md`: FR-273/274/275/276, NFR-502/501.
- `docs/roadmap.md` §7: the WK-668 row and the Phase 2 top risks.
- `docs/closures/INDEX.md#closure-recordsmd`: the Phase 1b close and its carry-forwards.
