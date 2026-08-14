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

## Coverage

Drafted: envelope, artifact ref, money, dataset version, validation rule, validation
report, model spec, model, custom objective, objective certificate, rating algorithm, rate
table, rating version, quote context, scoring result, optimisation run, GIPP check,
monitor, monitoring result, audit event, job.

Not yet drafted (Phase 0 remaining): profile, banding, grouping, peril structure,
transparency artifact, diagnostics, dislocation run, regression suite, approval request,
dossier. Each is specified in prose in its module spec; the schema is mechanical from
there.
