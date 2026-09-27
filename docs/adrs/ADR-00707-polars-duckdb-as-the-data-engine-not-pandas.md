---
id: ADR-707
family: decision
title: Polars + DuckDB as the data engine, not pandas
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-08-14
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                    # ids only — the FR-/NFR-/ADR- this decision touches
was: docs/adr/0005-polars-duckdb-over-pandas.md
---

# Polars + DuckDB as the data engine, not pandas

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

---

## Addendum — 2026-08-14: the split is load-bearing for a reason we did not anticipate

This ADR assigns *row-level transformation* to Polars and *aggregation* to DuckDB, argued
at the time on ergonomics and on not loading a dataset to profile it.

Research found a second, stronger justification. Polars' new streaming engine carries an
**open, unresolved memory regression** ([pola-rs/polars#25607](https://github.com/pola-rs/polars/issues/25607)):
a simple group-by over Parquet consumes more than 6 GB of RAM on 1.35.2 where the previous
streaming engine did not.

Because profiling, one-way summaries, PSI and dislocation — every heavy group-by in the
platform — are assigned to DuckDB by this ADR, **none of them touches the affected path**.
A design chosen for clarity turns out to also route around a live upstream defect.

The practical consequence is a rule worth stating explicitly: *a new heavy aggregation
belongs in DuckDB by default*, and moving one into Polars requires checking the state of
that issue first.

Evidence: [`docs/research/track-a-findings.md`](../research/track-a-findings.md) F10.
