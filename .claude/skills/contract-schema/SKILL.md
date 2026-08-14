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

## Verified

2026-08-14 — Confirmed by authoring 31 schemas. The duplicate-key trap is not
hypothetical: `custom-objective.schema.json` and `validation-rule.schema.json` were each
written with two `allOf` keys, parsed cleanly under `json.load`, and would have silently
dropped their `artifact-envelope` composition. A `object_pairs_hook` check caught both.
