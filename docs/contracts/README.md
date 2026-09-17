---
family: reference
title: Contracts
status: active                  # active → retired (§1.2a)
created: 2026-08-14
owner: lead
corrected_by: []
relates: []                      # ids only
---

# Contracts

Draft machine-readable contracts for the specification suite.

| Path | Contents | Authored or generated |
|---|---|---|
| `schemas/` | JSON Schema (draft 2020-12) for the persisted artifacts | **hand-authored, Phase 0** |
| `schemas/generated/` | The shapes `packages/model-schema` now owns | **generated** — do not edit |
| `openapi/generated.json` | The API as it is today | **generated** — do not edit |
| `openapi/gi-pricing.yaml` | Phase 0 design stub for the whole `/api/v1` surface | **hand-authored** |

Regenerate with `uv run python scripts/generate-contracts.py`; CI runs it with `--check`
and fails on drift (FR-451).

### Why the design stub is not overwritten

`gi-pricing.yaml` describes the whole intended surface across eight modules.
`generated.json` describes the routes that exist. Replacing the first with the second
would delete a specification to make the tooling tidy. The generated document grows toward
the stub as routes land, and the stub retires when it is reached — not before.

### Why the generated schemas are validation-mode

Research F7 below is only visible in validation mode: a bare `Decimal` renders as
`anyOf: [number, string]` there, and as a plain string in serialization mode. A contract
generated from the serialization schema would look compliant while the *request* side still
accepted the lossy JSON number FR-10 forbids. The request side is where the hazard
lives, so that is the schema that is committed.

## Status and authority

Generation began in **WK-658 (2026-08-14)** and is partial by design: `schemas/generated/` and
`openapi/generated.json` are produced from the code, and the rest remain the Phase 0
hand-authored drafts until the shapes they describe exist in `packages/model-schema`
([ADR-704](../adrs/ADR-00704-model-schema-is-the-single-source-of-truth-for-shared-shapes.md), FR-9, FR-451).

For a shape with **both** an authored and a generated schema, the generated one is
authoritative — the model is the source of truth — and `backend/tests/test_contracts.py`
asserts the two agree on field names and enum values, so a divergence fails the build
rather than being resolved by whichever file was edited last (`CLAUDE.md` §0).

For a shape with only an authored schema, the module spec remains authoritative; where they
disagree, fix the schema.

*The first run of that comparison found three real divergences — see the changelog below.*

## Changelog

**2026-08-14 (WK-658).** Generation wired up. The comparison immediately found:

1. `ArtifactRef` serialised as a **JSON object**, while ID-3 makes
   `{type}:{slug}@{version}` the canonical external string. A frontend generated from the
   model would have expected an object where every spec, trace and audit row carries a
   string. Fixed in the model.
2. `common/artifact-ref.schema.json` admitted `@0`, which the parser has always rejected
   (ID-2 starts versions at 1). The contract was looser than the code, so a client could
   have built something the platform refuses. The pattern is now generated from
   `model_schema.refs.REF_PATTERN`.
3. ID-3's own example `rating_version:motor-gb@2026-04` contradicted ID-2's `version: int`
   and the reference pattern. Corrected in `00-overview.md`.

## Conventions

- `$id` is `https://contracts.gi-pricing.dev/<name>.schema.json`; cross-references use
  relative `$ref`.
- Every artifact composes `common/artifact-envelope.schema.json` (`00-overview.md` §4.3).
- Monetary values are **integer minor units** (field suffix `_minor`) or decimal **strings**
  — never JSON numbers with a fractional part (FR-10, `03` R2).
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

## Two findings that affect generation (research 2026-08-14)

**1 — The generated shape differs from these drafts.** Pydantic emits tagged unions as
`oneOf` + `discriminator` (`{"propertyName": ..., "mapping": {...}}`), verified against
Pydantic 2.13.4. These hand-drafted schemas express variants as `allOf` + `if`/`then`.
Both are valid JSON Schema and both validate the same documents, but **the drafted form is
not the target** — when generation replaces these files in Phase 1, expect the shape to
change and do not "fix" it back. A `Literal` covering two tags maps both onto one branch,
which is exactly what `model-spec.schema.json` needs for `xgboost`/`lightgbm`.

**2 — `Decimal` generates a permissive union, and that breaks FR-10.** Pydantic renders
a `Decimal` field as `anyOf: [{"type": "number"}, {"type": "string", "pattern": ...}]`.
Serialisation is safe — `model_dump_json()` emits an exact string — but the *schema* also
admits `{"type": "number"}`, the lossy binary-float form the specification forbids. A
payload could therefore satisfy the contract while violating the spec.

**Monetary and relativity fields must be constrained to the string form in the generated
schema**, not left as `anyOf`. This is a generation requirement, not a style preference.
See [`research/track-a-findings.md`](../research/track-a-findings.md) F6–F7.

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
