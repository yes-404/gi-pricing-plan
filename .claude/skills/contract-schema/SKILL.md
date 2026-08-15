---
name: contract-schema
description: Add or modify a JSON Schema artifact contract or the OpenAPI stub in docs/contracts/ of this GI pricing platform. Use when defining or changing the persisted shape of an artifact such as a dataset version, model, rating version, scoring result, or audit event. Covers the money and artifact-reference conventions, the invariants annotation, and the duplicate-key and $ref traps that JSON parsers hide.
---

# Editing a contract

`docs/contracts/schemas/` holds JSON Schema (draft 2020-12) for every persisted artifact.
These are **hand-drafted for Phase 0**; from Phase 1 they become generated output from
`packages/model-schema` (ADR-0002). Where a schema and a module spec disagree, **the spec
wins** — fix the schema.

## Conventions

- `$id` is `https://contracts.gi-pricing.dev/<name>.schema.json`; cross-file refs are
  relative (`common/money.schema.json#/$defs/MoneyMinor`).
- Every artifact composes `common/artifact-envelope.schema.json`.
- **Money is `MoneyMinor` (integer minor units) or `Decimal` (a string)** — never a JSON
  number with a fractional part (FR-OVR-7). Same for exposure and relativities.
- Artifact cross-references use `common/artifact-ref.schema.json` — the
  `{type}:{slug}@{version}` string form. Adding a new artifact type means extending that
  file's `pattern`.
- Express a rule in schema wherever schema can express it (`if`/`then`, `required`,
  `pattern`). Everything else goes in an **`invariants`** array of prose strings, each
  citing its requirement ID. `invariants` is a non-standard annotation: validators ignore
  it, reviewers must not.

## Two traps

**Duplicate keys.** `json.load` silently keeps the last one, so a second `allOf` block
silently discards the first — including a composed envelope. The audit catches this; do
not rely on the file merely "parsing".

**Phase 1 will change the shape.** Pydantic generates tagged unions as
`oneOf` + `discriminator`, not the `allOf` + `if`/`then` used in these drafts. Both are
valid and validate the same documents. Do not "fix" generated output back to the drafted
form.

## After

```bash
python3 scripts/audit-docs.py    # parses every schema, rejects duplicate keys, resolves every $ref
```

Then update the coverage tables in `docs/contracts/README.md` and
`docs/phase-0-status.md` §3 if you added a file.

## Generation (from W2, FR-PLAT-48)

`uv run python scripts/generate-contracts.py` writes the generated contracts;
`--check` fails on drift and runs in CI. Both directions are covered — a changed model with
a stale contract, and a hand-edited contract — and both were proven by injection.

**Generate validation-mode schemas, not serialization-mode.** Research F7's hazard is only
visible in validation mode: a bare `Decimal` renders as `anyOf: [number, string]` there and
as a plain string in serialization mode. A contract generated from the serialization schema
looks compliant while the *request* side still accepts the lossy JSON number FR-OVR-7
forbids. The request side is where the hazard lives.

**A Python-structured type may be a flat string on the wire.** `ArtifactRef` is three
fields in Python and `{type}:{slug}@{version}` in JSON (ID-3). That needs three pieces —
`model_validator(mode="before")` to parse, `model_serializer` to render, and
`__get_pydantic_json_schema__` to emit `{"type": "string", "pattern": ...}`. Miss the last
and the generated client expects an object where every spec, trace and audit row carries a
string.

**Do not overwrite a hand-authored design document with generated output.** The Phase 0
`openapi/gi-pricing.yaml` describes eight modules; `openapi/generated.json` describes the
routes that exist. They live side by side until the second reaches the first.

**Where a shape has both an authored and a generated schema, assert they agree** — field
names and enum values, in a test. That is what turns `CLAUDE.md` §0 ("when code and spec
disagree, stop and resolve it") into a mechanism. The first run found three real
divergences, one of them a wire-format error that would have reached the frontend.

**Serialise deterministically** — sorted keys, fixed indent, trailing newline. A document
that re-serialises differently each run reports drift that is not drift, and a check that
cries wolf gets turned off.

**That applies to generated schemas. Edit the hand-authored ones as text.** The Phase 0
schemas in `docs/contracts/schemas/` are hand-formatted — one-line leaf objects, wrapped
arrays — and `json.load` → `json.dumps` is not a round trip through that: adding two fields
to `grouping.schema.json` that way produced a 189-line diff for a 13-line change, burying
the edit in reflow and destroying the layout a reader relies on. Patch the text, then
`json.loads` the result to prove it still parses.

## Verified

2026-08-15 — Confirmed while applying OQ-MODEL-5's decision to `grouping.schema.json`
(`credibility_model` default, `credibility_pk`, `credibility_components`). The reformat trap
above cost a revert.

2026-08-14 — W2. Generation wired up and the drift check proven in both directions.
The generated/authored comparison found three real divergences on its first run.

2026-08-14 — Confirmed by authoring 31 schemas. The duplicate-key trap is not
hypothetical: `custom-objective.schema.json` and `validation-rule.schema.json` were each
written with two `allOf` keys, parsed cleanly under `json.load`, and would have silently
dropped their `artifact-envelope` composition. A `object_pairs_hook` check caught both.
