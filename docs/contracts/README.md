# Contracts

Draft machine-readable contracts for the specification suite.

| Path | Contents |
|---|---|
| `schemas/` | JSON Schema (draft 2020-12) for the persisted artifacts |
| `openapi/gi-pricing.yaml` | OpenAPI 3.1 stub for the `/api/v1` surface |

## Status and authority

These files are **drafts written by hand during Phase 0**. From Phase 1 they become
*generated output*: `packages/model-schema` holds the Pydantic v2 models and both the JSON
Schema and the OpenAPI document are generated from them, with CI failing on drift
([ADR-0002](../adr/0002-model-schema-single-source-of-truth.md), FR-OVR-6, FR-PLAT-48).

Until then, treat the module specs as authoritative where they disagree with a schema, and
fix the schema.

## Conventions

- `$id` is `https://contracts.gi-pricing.dev/<name>.schema.json`; cross-references use
  relative `$ref`.
- Every artifact composes `common/artifact-envelope.schema.json` (`00-overview.md` §4.3).
- Monetary values are **integer minor units** (field suffix `_minor`) or decimal **strings**
  — never JSON numbers with a fractional part (FR-OVR-7, `03` R2).
- Exposure and relativities are decimal strings for the same reason.
- Artifact cross-references use the canonical string form `{type}:{slug}@{version}`
  (`00-overview.md` ID-3), validated by `common/artifact-ref.schema.json`.
- Enum values match the status vocabularies in the specs exactly; a status not listed in a
  spec must not appear here.
- **`invariants`** is a non-standard annotation carrying the rules JSON Schema cannot
  express — cross-field conditions, state-machine constraints, and referential rules —
  each citing its requirement ID. Validators ignore it; reviewers and the Phase 1
  implementers should not. Where an invariant *can* be expressed in schema
  (`if`/`then`, `required`, `pattern`), it is, and it does not appear in `invariants`.

## Coverage

**31 schemas, covering every persisted artifact the specs define.**

| Area | Schemas |
|---|---|
| Common | artifact envelope, artifact ref, blob ref, money primitives, provenance |
| Data (01) | dataset version, validation rule, validation report, profile |
| Modelling (02) | banding, grouping, model spec, model, diagnostics, custom objective, objective certificate, transparency artifact, peril structure |
| Rating (03) | rating algorithm, rate table, rating version, scoring (quote context / result / ladder / trace), dislocation run, regression suite + run |
| Optimisation (04) | optimisation run + result, GIPP check |
| Monitoring (05) | monitor, monitoring result, alert |
| Governance (06) | approval request, audit event, dossier |
| Platform (07) | job |

Verify with `python3 scripts/audit-docs.py`, which parses every schema, rejects duplicate
keys, and resolves every local and cross-file `$ref`.
