# Architecture Decision Records

One decision per file, numbered `NNNN-kebab-title.md`, never renumbered.

**Status values:** `proposed` → `accepted` → (`superseded by ADR-NNNN` | `deprecated`).
An accepted ADR is immutable; to change a decision, write a new ADR that supersedes it
and edit only the old one's status line.

**Write an ADR when** a choice constrains more than one module, is expensive to reverse,
or has already been made and needs recording. Otherwise use `docs/open-questions.md`.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-pricing-core-is-dependency-free.md) | pricing-core is dependency-free and owns all actuarial maths | accepted |
| [0002](0002-model-schema-single-source-of-truth.md) | model-schema is the single source of truth for shared shapes | accepted |
| [0003](0003-declarative-json-artifacts-no-pickles.md) | Model and rating definitions are declarative JSON artifacts | accepted |
| [0004](0004-zen-engine-for-rating-execution.md) | GoRules ZEN Engine executes rating DAGs | accepted |
| [0005](0005-polars-duckdb-over-pandas.md) | Polars + DuckDB as the data engine, not pandas | accepted |
