# ADR-0004 — GoRules ZEN Engine executes rating DAGs

- **Status:** accepted
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
