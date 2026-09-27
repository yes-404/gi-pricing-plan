---
id: ADR-705
family: decision
title: Model and rating definitions are declarative JSON artifacts
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-08-14
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                    # ids only — the FR-/NFR-/ADR- this decision touches
was: docs/adr/0003-declarative-json-artifacts-no-pickles.md
---

# Model and rating definitions are declarative JSON artifacts

## Context

A price quoted to a customer may need to be reproduced and explained years later, after
library upgrades and staff turnover. Python pickles fail this outright: they are
version-fragile, unreadable, undiffable, and are an arbitrary-code-execution vector when
loaded. A regulator or internal reviewer must be able to read what the model *is*.

## Decision

Every model and rating definition is persisted as declarative JSON conforming to a
`model-schema` contract. Specifically:

- **GLM** — family, link, offset, weights, factor list with their bandings/groupings,
  base levels, coefficient table with standard errors, and fitting metadata. A GLM is
  fully re-scorable from its JSON with no library state.
- **GBM (XGBoost/LightGBM)** — the booster is exported in the library's own **JSON/text**
  model format (`Booster.save_model('*.json')`), stored content-addressed (ID-4), and
  referenced by hash alongside a JSON record of hyperparameters, feature order,
  `base_margin` construction, monotone constraints, and the objective reference. Never
  `pickle`, `joblib`, or a language-specific serialisation.
- **Custom objective** — declarative parameters or a restricted expression string; never
  a pickled callable (see `02-modelling.md`).
- **Rating algorithm** — a JSON DAG (ADR-706) plus JSON/parquet rate tables.
- **Bandings and groupings** — explicit boundary and mapping tables, not fitted objects.

Loading an artifact must never execute code contained in that artifact.

## Consequences

**Positive** — artifacts are diffable in review, portable between instances (FR-5),
inspectable by an auditor without our runtime, and safe to load from untrusted storage.

**Negative** — artifacts are larger than pickles; every new model type needs an explicit
serialisation contract and a re-scoring path; some library-specific state (e.g. exact
internal float layout of a booster) is only preserved via the library's own JSON format,
so we pin library versions per artifact and record them.

**Neutral** — forces us to keep a scoring implementation in `pricing-core` that reads the
declarative form, which is exactly what real-time scoring wants anyway.
