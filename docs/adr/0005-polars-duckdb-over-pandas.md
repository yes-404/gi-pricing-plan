# ADR-0005 — Polars + DuckDB as the data engine, not pandas

- **Status:** accepted
- **Date:** 2026-08-14
- **Deciders:** maintainer
- **Related:** NFR-OVR-2, NFR-OVR-3, `01-data-management.md`

## Context

Pricing datasets are tens of millions of rows with wide factor sets. The platform needs
predictable memory, fast group-bys for one-ways and diagnostics, lazy execution for
larger-than-memory profiling, and strict typing so that a silently coerced column cannot
change a premium.

## Decision

- **Polars** is the in-memory dataframe library for `pricing-core`, workers, and
  pipelines. Its strict dtypes and lazy API are load-bearing, not a preference.
- **DuckDB** handles ad-hoc and larger-than-memory aggregation directly over the parquet
  files of a Dataset Version: profiling, one-way summaries, PSI, dislocation, A/E slices.
- **pandas** is permitted only at unavoidable library boundaries (e.g. a fitting library
  that accepts nothing else), converted immediately in and out, and never persisted or
  passed across a module boundary. New code must not introduce a pandas dependency.
- Dataset Versions are stored as **parquet** with an explicit, persisted Arrow schema.

## Consequences

**Positive** — meets the fitting/scoring performance NFRs; no silent dtype coercion;
SQL is available for actuaries who prefer it; parquet + DuckDB means profiling does not
require loading the dataset.

**Negative** — a smaller ecosystem of copy-paste actuarial recipes than pandas; some
libraries (statsmodels in particular) require conversion; contributors need to learn
Polars idioms — a `skills-map.md` entry.

**Neutral** — two data engines to reason about, mitigated by a clear split: Polars for
row-level transformation inside a fit, DuckDB for aggregation over stored parquet.
