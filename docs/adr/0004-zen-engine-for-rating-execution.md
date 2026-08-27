# ADR-0004 — GoRules ZEN Engine executes rating DAGs

- **Status:** accepted · **confirmed by research 2026-08-14 and 2026-08-27** (see Addenda)
- **Date:** 2026-08-14
- **Deciders:** maintainer
- **Related:** NFR-OVR-1, ADR-0003, `03-rating-engine.md`

## Context

A rating algorithm is a DAG of lookups, expressions, table joins, model calls, and
constraints. It must (a) execute in single-digit milliseconds for a live quote, (b) be a
declarative artifact rather than generated code, (c) be renderable and editable as a
graph in the UI, and (d) produce a per-step trace.

Options considered: hand-rolled interpreter in `pricing-core`; generated Python;
generated SQL; a rules engine (GoRules ZEN, Drools-style); a spreadsheet-formula engine.

## Decision

Adopt the **GoRules ZEN Engine** (Rust core, Python bindings, JSON Decision Model
format) as the execution substrate for rating DAGs, wrapped by a `pricing-core` facade.

- The JDM graph is the persisted artifact; `pricing-core` owns translation between our
  `RatingAlgorithm` contract and JDM, so the engine never leaks into other modules.
- Custom node types we need beyond stock JDM (rate-table lookup with effective dating,
  `model_call`, decimal-safe arithmetic) are implemented as engine custom nodes /
  loader-provided functions, and specified in `03-rating-engine.md`.
- The Vue Flow designer edits our `RatingAlgorithm` contract, not raw JDM.

## Consequences

**Positive** — no bespoke interpreter to write, test, and optimise; Rust-speed execution
meets NFR-OVR-1; JSON graph format aligns with ADR-0003; built-in tracing supports the
`Trace` requirement; the same artifact runs in batch and real time.

**Negative** — a dependency on a third party's format and release cadence; JDM's
expression language must be constrained (no arbitrary code) and its numeric semantics
checked against our decimal-money rule (FR-OVR-7) — a genuine risk tracked as
OQ-RATE-1; debugging crosses a Python/Rust boundary.

**Neutral** — the `pricing-core` facade means a future swap of engines is a contained
change, at the cost of maintaining the translation layer.

---

## Addendum — 2026-08-14: decision confirmed by research

The "Negative" section above flagged that JDM's numeric semantics had to be checked against
FR-OVR-7, tracked as OQ-RATE-1 and identified as the highest-risk unknown in the suite.

**That check has now been done, and the decision holds.** `zen-types` represents
`Variable::Number` as `rust_decimal::Decimal` — a 96-bit-mantissa fixed-point decimal, not
`f64` — and all node inputs, outputs and expression results use that type system. Monetary
arithmetic inside JDM expressions is exact. The integer-minor-units workaround contemplated
in OQ-RATE-1's original recommendation is not required for correctness.

**This addendum does not change the decision** and does not supersede the ADR. It records
that a named risk was tested and did not materialise, and that the risk *moved* rather than
disappeared:

| Residual risk | Now specified as |
|---|---|
| `rust_decimal` serialises float-like by default; exact JSON needs the arbitrary-precision feature | `03` FR-RATE-56 |
| `maths-nopanic` (which `zen-engine` enables) returns `0` on invalid input instead of raising | `03` FR-RATE-57 |
| Decimal scale is capped at 28 | `03` FR-RATE-58 |

Evidence: [`docs/research/track-a-findings.md`](../research/track-a-findings.md) F1.

---

## Addendum — 2026-08-27: S1 and S2 confirmed at Phase 2 entry

The 2026-08-14 addendum confirmed the engine's decimal semantics. This addendum records
the Phase 2 entry re-verification (W8, `docs/plans/2026-08-27-w8-spike-resolution.md`):
the S1 suite re-ran against the installed `zen-engine` 0.53.0 and all four boundary
requirements hold — FR-RATE-56 (exact arithmetic), FR-RATE-57 (division guarded, unguarded
division rejected), FR-RATE-58 (decimal scale cap within the rounding discipline),
FR-RATE-59 (expression vocabulary validated against the engine). NFR-RATE-14 holds at
p99 1.626 ms with `nthread=1` (3.3 % of the 50 ms budget); NFR-RATE-13's design rule holds
and its ~1 ms premise is amended (see `03` NFR-RATE-13).

**This addendum does not change the decision** and does not supersede the ADR. The
residual risks remain specified as FR-RATE-56/57/58. **W9 proceeds** on this basis.

Evidence: [`docs/research/w8-spike-resolution.md`](../research/w8-spike-resolution.md).
