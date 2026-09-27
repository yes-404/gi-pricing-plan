---
name: contract-schema
description: Add or modify a JSON Schema artifact contract or the OpenAPI stub in docs/contracts/ of this GI pricing platform. Use when defining or changing the persisted shape of an artifact such as a dataset version, model, rating version, scoring result, or audit event. Covers the money and artifact-reference conventions, the invariants annotation, and the duplicate-key and $ref traps that JSON parsers hide.
---

# Editing a contract

`docs/contracts/schemas/` holds JSON Schema (draft 2020-12) for every persisted artifact.
These are **hand-drafted for Phase 0**; from Phase 1 they become generated output from
`packages/model-schema` (ADR-704). Where a schema and a module spec disagree, **the spec
wins** — fix the schema.

## Conventions

- `$id` is `https://contracts.gi-pricing.dev/<name>.schema.json`; cross-file refs are
  relative (`common/money.schema.json#/$defs/MoneyMinor`).
- Every artifact composes `common/artifact-envelope.schema.json`.
- **Money is `MoneyMinor` (integer minor units) or `Decimal` (a string)** — never a JSON
  number with a fractional part (FR-10). Same for exposure and relativities.
- Artifact cross-references use `common/artifact-ref.schema.json` — the
  `{type}:{slug}@{version}` string form. Adding a new artifact type means extending that
  file's `pattern`.
- Express a rule in schema wherever schema can express it (`if`/`then`, `required`,
  `pattern`). Everything else goes in an **`invariants`** array of prose strings, each
  citing its requirement ID. `invariants` is a non-standard annotation: validators ignore
  it, reviewers must not.

## Four traps

**Duplicate keys.** `json.load` silently keeps the last one, so a second `allOf` block
silently discards the first — including a composed envelope. The audit catches this; do
not rely on the file merely "parsing".

**Phase 1 will change the shape.** Pydantic generates tagged unions as
`oneOf` + `discriminator`, not the `allOf` + `if`/`then` used in these drafts. Both are
valid and validate the same documents. Do not "fix" generated output back to the drafted
form.

**A fixed-length tuple is `prefixItems`, not `items`.** Pydantic emits
`tuple[float, float]` as `{"type": "array", "minItems": 2, "maxItems": 2, "prefixItems":
[{...}, {...}]}` — there is no `items` key at all. Anything that walks a schema looking for
array elements must read both, or it is silently blind to every tuple field in every
contract while reporting success. This cost `test_generated_and_authored_agree_on_scalar_types`
its teeth on the day it was written: `OneWayRow.severity_ci` was deliberately retyped from
number to integer and the comparison passed. Hand-authored schemas spell the same shape as
`"items"`, so the two sides of a comparison do **not** use the same keyword for it.

Related, when comparing a generated schema against a hand-authored one: the generated side
marks every `X | None` nullable through `anyOf` and the authored side often does not. The
advice here used to be "compare with `null` removed", and it was **measured false on
2026-08-22**: 70 of 417 authored paths are nullable, the comparison found 43 divergences
rather than the predicted noise, 20 were real and were fixed, and one was a bug this skill's
own advice had helped re-publish. Nullability is compared for the slugs in
`NULLABILITY_COMPARED_SLUGS` and the remainder is scoped, not excused. See
`.claude/skills/contract-guard`.

**A new authored schema is not compared until its slug is registered.**
`test_generated_and_authored_agree_on_scalar_types` in `backend/tests/test_contracts.py`
runs over `COMPARED_SLUGS`, a written-out list — not a glob, deliberately, so that adding a
schema to it is a visible act. Add the slug in the same change as the file. Forgetting is
not silent any more: `test_every_eligible_schema_is_compared` fails when a schema has both
an authored and a generated side and is neither compared nor pinned. It exists because
`peril-structure` sat outside the list from Phase 0 declaring `restoration_loading`, `ratio`
and `tolerance` as `{"type": "number"}` while all three are `DecimalStr` — the check that
would have caught it on the day it was written never looked at that file.

A schema may be excused only by a **pinned** divergence: a test asserting the disagreement is
exactly the known path and nothing else, so a new divergence in the same schema still fails
and the pin dies the day the question behind it is decided. `diagnostics` is the worked
example (`OQ-587`). An excused slug without that test is the exemption list this suite
refuses to grow.

## After

```bash
python3 scripts/audit-docs.py    # parses every schema, rejects duplicate keys, resolves every $ref
```

Then update the coverage tables in `docs/contracts/README.md` and
`docs/closures/CR-00709-phase-0-specification-status.md` §3 if you added a file.

## Generation (from WK-658, FR-451)

`uv run python scripts/generate-contracts.py` writes the generated contracts;
`--check` fails on drift and runs in CI. Both directions are covered — a changed model with
a stale contract, and a hand-edited contract — and both were proven by injection.

**Generate validation-mode schemas, not serialization-mode.** Research F7's hazard is only
visible in validation mode: a bare `Decimal` renders as `anyOf: [number, string]` there and
as a plain string in serialization mode. A contract generated from the serialization schema
looks compliant while the *request* side still accepts the lossy JSON number FR-10
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

2026-08-22 — W32-1, the contracts-and-drift-guard slice. The nullability paragraph above was
reversed: it advised stripping `null` before comparing, and the measurement that tested the
advice found 43 real divergences under it. The lesson is the one `CLAUDE.md` §0 states about
counts and this skill restated about a grep — an assertion about how noisy a check *would* be
is a prediction, and a prediction in a skill is read as a finding.

2026-08-19 — WK-661's `OQ-547` slice, applying the decision that `DecimalStr` refuses a float.
The fourth trap above was found by widening the comparison from 6 slugs to 11 while looking
for something else. Two lessons beyond the trap itself: an *input*-strictness change is what
makes a wrong `"type": "number"` reachable, since a string-serialising field's contract can
be wrong for months while every round-trip still passes; and a count written into prose
(`"26 DecimalStr fields across 7 modules"`) was a grep of mentions, not fields — there are
11. Recompute a number before repeating it, which is `CLAUDE.md` §0's rule about counts.

2026-08-19 — WK-661's profile-contract slice. The `prefixItems` trap above was paid for in
full. Also confirmed that comparing generated and hand-authored schemas on **field names**
is a much weaker check than it reads as: five scalar-type divergences (`mean_severity`,
`mean_burning_cost` and `severity_ci` declared integer against `float` in the model) sat
under matching names across two contracts, through a rename that touched both sides.

2026-08-15 — Confirmed while applying OQ-579's decision to `grouping.schema.json`
(`credibility_model` default, `credibility_pk`, `credibility_components`). The reformat trap
above cost a revert.

2026-08-14 — WK-658. Generation wired up and the drift check proven in both directions.
The generated/authored comparison found three real divergences on its first run.

2026-08-14 — Confirmed by authoring 31 schemas. The duplicate-key trap is not
hypothetical: `custom-objective.schema.json` and `validation-rule.schema.json` were each
written with two `allOf` keys, parsed cleanly under `json.load`, and would have silently
dropped their `artifact-envelope` composition. A `object_pairs_hook` check caught both.
