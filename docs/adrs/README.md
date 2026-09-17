---
family: reference
title: Architecture Decision Records
status: active                  # active → retired (§1.2a)
created: 2026-08-14
owner: lead
corrected_by: []
relates: []                      # ids only
was: docs/adr/README.md
---

# Architecture Decision Records

One decision per file, named `ADR-nnnnn-<slug>.md` — the padded id leads the filename, and the
id itself is permanent: never renumbered, never reused
([`../process/document-ids.md`](../process/document-ids.md)).

**Status values** are the front matter's `status:` field: `draft` → `active` →
(`superseded` | `retired`). An `active` ADR is immutable; to change a decision, write a new
ADR that supersedes it and edit only the old one's `status:` and `superseded_by:`.

**Write an ADR when** a choice constrains more than one module, is expensive to reverse, or
has already been made and needs recording. Otherwise use
[`../open-questions.md`](../open-questions.md).

**This table is generated.** [`../INDEX.md`](../INDEX.md) is the complete index across every
family and is the one that cannot go stale; this table is a convenience view of one family,
rewritten by `scripts/doc-id.py` rather than maintained by hand.

| ADR | Title | Status |
|---|---|---|
| [ADR-703](ADR-00703-pricing-core-is-dependency-free-and-owns-all-actuarial-maths.md) | pricing-core is dependency-free and owns all actuarial maths | active |
| [ADR-704](ADR-00704-model-schema-is-the-single-source-of-truth-for-shared-shapes.md) | model-schema is the single source of truth for shared shapes | active |
| [ADR-705](ADR-00705-model-and-rating-definitions-are-declarative-json-artifacts.md) | Model and rating definitions are declarative JSON artifacts | active |
| [ADR-706](ADR-00706-gorules-zen-engine-executes-rating-dags.md) | GoRules ZEN Engine executes rating DAGs | active |
| [ADR-707](ADR-00707-polars-duckdb-as-the-data-engine-not-pandas.md) | Polars + DuckDB as the data engine, not pandas | active |
| [ADR-710](ADR-00710-tenant-isolation-is-a-deployment-boundary.md) | Tenant isolation is a deployment boundary | active |
