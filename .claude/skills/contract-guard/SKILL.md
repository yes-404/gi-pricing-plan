---
name: contract-guard
description: Write or extend the schema-drift guard in backend/tests/test_contracts.py — the comparisons that hold a generated JSON Schema against its hand-authored contract. Use when adding a comparison or a walker, when one lands red, or when scoping a slug out of one. Covers what each walker reaches, why `if` is not followed, why `required` is compared in one direction only, the four defects that were in the guards rather than in the schemas, and why a comparison that counts paths cannot notice a walker that stopped descending.
---

# Extending the drift guard

`backend/tests/test_contracts.py` holds **the whole guard** — every walker, every comparison,
every scoped list. No other file holds any part of it. *Authoring* a contract is a different
job with a different reader: `.claude/skills/contract-schema`.

Two sides of one shape are compared:

- `docs/contracts/schemas/generated/<slug>.schema.json` — written by
  `scripts/generate-contracts.py` from `model-schema`. The code's account of the shape.
- `docs/contracts/schemas/<slug>.schema.json` — hand-authored since Phase 0. The
  **published** account, which external readers build against.

`COMPARED_SLUGS` is the twelve slugs that have both. A disagreement is a `CLAUDE.md` §0
question — say which side was wrong and why — never a quiet edit to whichever is easier.

## The walkers, and what each one is for

| Walker | Answers | Bound |
|---|---|---|
| `_deref` | follows `$ref`, local **and across files** (`common/money.schema.json#/$defs/MoneyMinor`), returning the node *and the document it now lives in* | `_MAX_REF_HOPS = 20` |
| `_variants` | the node plus every composed subschema beneath it — `anyOf`, `oneOf`, `allOf`, `then`, `else` — flattened to one list | `_MAX_COMPOSITION_DEPTH = 40` |
| `_scalar_types` | the JSON types a leaf admits, derived from `enum`/`const` members as well as `type`; `keep_null` decides whether nullability is part of the answer | via `_variants` |
| `_type_map` | the whole schema as `dotted.path -> admitted types`, descending `properties`, `items` **and `prefixItems`** | via `_variants` |

`_variants` deliberately does **not** follow `if`. `if` is the discriminator *test*, not a
description of the artifact: reading it folds `{"const": "glm"}` into `model_type`'s admitted
types as though the contract declared a second field there. `then`/`else` joined the three
combinators on 2026-08-22 — before that, every field in every conditional arm was invisible,
and `model-spec` produced its 12 flat properties and nothing from either arm: no `family`, no
`link`, no `objective`, no `early_stopping`.

New map walkers take `(document, node, base, path="")` and return a dict keyed by dotted path,
matching `_type_map` **exactly**, so a path in one map is a path in another and two maps can be
read against each other. Carry `*, _depth=0` only if the walker recurses through combinators
itself rather than delegating that to `_variants`.

## Adding a comparison — the order that works

1. **Measure first, in a throwaway script.** How many paths does the new axis reach, on how
   many slugs, and how many disagree? A guard specified without knowing how red it lands is a
   guard someone switches off. The three added on 2026-08-22 land on one or two slugs each —
   `required` on `model` alone, `additionalProperties` on `custom-objective` alone, scalar
   constraints on `grouping` and `objective-certificate` — and that is what made them
   switch-on-able.
2. **Write the walker and the test, with the measured expectation stated.** "Expect 11 passed,
   1 failed, naming `fit_result.terms.[]`" is checkable; "expect it to fail" is not.
3. **Intersect paths.** A path present on one side only is a difference of *intent*, arbitrated
   by `test_an_artifact_shape_carries_exactly_what_its_contract_declares`, not by a type or
   bound comparison.
4. **Resolve every disagreement it finds** before the slice ends. A red guard at the end of a
   slice is the same artifact as no guard.
5. **Prove it fails on deliberately broken input** (`CLAUDE.md` §13 rule 4) — break the
   *contract* with a one-line `python3 -c`, watch the named failure, `git checkout` the file.
   When the proof breaks the **walker** instead, `git stash` rather than `git checkout`, and do
   it last: `git checkout` on a file you are mid-edit in destroys more than the injected defect.
6. **Add its meta-guard** in the same commit (below).

## Never count what a walker reached — name a path

A comparison that intersects two maps is **green when both maps are empty**. That is the
guard's characteristic failure, and counting cannot catch it: the count of what the walker
produced shrinks along with the walker, so any threshold expressed as a fraction of its own
output moves out of the way of the defect it exists to catch.

So `test_each_new_walker_reaches_a_nested_path_it_is_supposed_to` and
`test_the_type_comparison_reaches_the_one_way_row` name one nested path per walker, each at
least two levels down and each chosen because a plausible refactor would lose it.

Anchor a `_closure_map` control at a real declaration, not at the root:
`model-spec.family_params`, never `<root>`. **No authored schema declares
`additionalProperties` in boolean form anywhere**, so a root anchor asserts a path that has
never existed on that side and is red from its first run. That mistake was made while drafting
the plan, which is why it is written down.

## `_variants` finds fields; it does not decide obligations

Flattening every combinator into one list is right for *"what fields exist anywhere in this
shape?"* and **wrong** for *"what must be present?"*:

- `allOf` is conjunction — union the branches' obligations.
- `oneOf` / `anyOf` is disjunction — a key is required only if **every** arm demands it, so
  **intersect**.
- `then` / `else` are conditional on an `if` this suite does not evaluate, and contribute
  nothing unconditionally.

Get this wrong and the guard **invents** requirements, which is the more expensive failure.
The naive union reported `model.fit_result.bins.[].cuts` **and** `.levels` as model-required;
`bins.[]` is a discriminated `oneOf` of `EbmNumericBins` and `EbmCategoricalBins`, the first
requires `cuts`, the second requires `levels`, and no single bin requires both. A contract
"corrected" to match would then have refused every valid categorical bin. **A guard that
manufactures the defect it reports is worse than no guard**, because someone will fix it.

`_required_at` is therefore written against the combinators directly and does not call
`_variants`. Finding children and deciding obligations are different questions.

## `required` is not symmetric, so compare one direction

The two sides answer different questions. Pydantic's `required` lists the fields with **no
default** — a fact about *construction*. A hand-authored contract's `required` lists what a
**reader may rely on**. A field carrying a default is still always serialised, so *the contract
requires more than the model* is safe, and it was 14 of the 18 differences measured on
2026-08-22. Asserting equality lands red on seven slugs for a reason that is mostly not a
defect.

The dangerous direction is the other one: **the contract must never mark optional what the
model requires.** That is a request a client builds from the published contract, sends, and has
refused — the refusal naming a field the contract said was not needed. It found
`model.fit_result.terms.[]`'s `bin_weights` and `standard_deviations`.

Say all of this in the test's docstring. The rule is not obvious, and a reader who does not
know it will "fix" the test the wrong way.

## `additionalProperties` has two meanings

- **Boolean.** `extra="forbid"` generates `"additionalProperties": false`. Every *generated*
  schema declares it at the root; **no authored schema declares it in boolean form anywhere**.
- **Schema.** `dict[str, float]` generates `"additionalProperties": {"type": "number"}` — a
  statement about the values an open map admits. This is the form the authored contracts use:
  `labels`, `mapping`, `params`, `progress.counters`, `glm.vif`, `fit_result.categorical_maps`,
  `spec.family_params` and eleven more.

A comparison written for the boolean form alone intersects an all-root generated map with an
empty authored one and **passes, having compared nothing**. `_closure_map` reads both into one
vocabulary — `CLOSED`/`OPEN` for the boolean form, the admitted JSON types for the schema form
— so a path where one side says `CLOSED` and the other says `number` is reported rather than
accidentally matched. Absence is not `OPEN`: JSON Schema's default is open, but a contract that
says nothing is silent rather than deliberate, and reporting every silence buries the one real
disagreement in the suite (`custom-objective.params`, where the contract refused the integer
the platform accepts).

## The four defects that were in the guards, not in the schemas

Each is a walker-writing trap rather than a schema trap. Every one of them reported success
while blind.

- **A clobbering `properties.update`.** The *last* variant to name a field replaced every
  earlier definition wholesale — and a conditional refinement is exactly that shape
  (`peril-structure` re-names `large_loss` inside a `then` only to add two required keys). So
  following `then` at all silently deleted the block's real definition and took the walker
  **from 36 paths to 28**. Collect the nodes per name and union their subtrees.
- **A `const` with no `type`.** A hand-authored `{"const": "derived_from_factors"}` carries no
  `"type"`, so a walker reading only `type` and `enum` called that branch typeless and reported
  the field as `object` against a model admitting `object | string`. Read `const` beside `enum`
  and derive the type from the member.
- **An `ENVELOPE_FIELDS` literal wrong in both directions.** It was the hand-written
  `{"id", "slug", "version", "dataset_id"}`: it **under-declared the envelope by eleven
  fields** and carried `dataset_id`, which the envelope has never had (it is a `Factor` /
  `Banding` / `Grouping` field, now named honestly in `MODEL_ONLY_UNRECONCILED`). A hand-copy
  of a published list is the shape-defined-twice `CLAUDE.md` §2 forbids — read the names from
  `common/artifact-envelope.schema.json`.
- **`prefixItems` blindness.** Pydantic emits `tuple[float, float]` as `prefixItems` with no
  `items` key at all, and the authored side spells the same shape as `items`. Reading only
  `items` made every tuple field in every contract invisible: `OneWayRow.severity_ci` was
  deliberately retyped from number to integer and the comparison passed.

  **It was written again on 2026-08-22, in this file, hours after the line above was drafted.**
  A new comparison collected `path.rsplit(".", 1)[-1]` and rebuilt `f"{block}.{name}"` — valid
  only where every leaf sits one level below the block. `OneWayRow`'s two tuple fields arrive
  as `…frequency_ci.[]` and `…severity_ci.[]`, whose last segment is `[]`, so the reassembly
  asserted `…source_level_stats.[].[]`: a path neither side can produce. The test failed
  unconditionally while saying nothing about the contract, and because it was red for a
  plausible-looking reason it nearly read as a real finding.

  **Never rebuild a path from a segment. Compare whole paths, as sets.** A dotted path is the
  walker's output; splitting and rejoining it re-implements the walker, badly. That the same
  trap caught the same file twice in one day is the argument for the rule rather than for
  remembering the trap.

## A hand-copy of a shared shape is where divergence starts

`OneWayRow` is computed once and shared by `01`'s profile and `02`'s factor workbench precisely
so both see the same numbers — and it was hand-copied into **three** contracts (`profile`,
`banding`, `grouping`). Two copies require `claim_count`, which the model defaults to 0; the
`grouping` copy invented a `relativity` the model never had and omitted six fields it does
have. The type comparison intersects paths, so a field on one side only is skipped rather than
reported: a copy can be wrong for a year without a single red test.

Where a contract block describes a shared model, `$ref` one `$defs` entry from both places, and
add a test that both blocks resolve to the same property set.

## Every scoped list needs the thing that notices it went stale

A curated list is only as good as the check that reads it. The pattern is `COMPARED_SLUGS` /
`test_every_eligible_schema_is_compared`: the list is written out rather than globbed, so adding
a slug is a visible act — and the meta-guard fails when a schema has both sides and is in
neither the list nor a pin. Widening that list found a `peril-structure` contract that had been
wrong since Phase 0 precisely because nothing enforced this.

The same bargain holds `NULLABILITY_COMPARED_SLUGS` (six slugs, held there by
`test_every_model_owned_slug_compares_nullability`), `ENVELOPE_GAP_IS_RECORDED_NOT_FIXED`
(`test_the_envelope_gap_is_still_the_shape_the_carve_out_assumes`) and the three walkers W32-1
added. A slug may be excused only by a **pinned** divergence — a test asserting the
disagreement is exactly the known path and nothing else, so a *new* divergence in the same
schema still fails and the pin dies the day its question is decided. An excused slug without
that test is the exemption list this suite refuses to grow.

## What the guard does not reach

**14 authored schemas have no generated counterpart** and are therefore compared against
nothing: `approval-request`, `dataset-version`, `dislocation-run`, `dossier`, `gipp-check`,
`monitoring`, `optimisation-run`, `rate-table`, `rating-algorithm`, `rating-version`,
`regression-suite`, `scoring`, `validation-report`, `validation-rule`. Most describe Phase 2+
artifacts that no model backs yet, which is why they are uncompared and not alarming — but
**`dataset-version`, `validation-report` and `validation-rule` describe artifacts Phase 1a
built**. Those three are a genuine gap in the guard's reach, named here so the next reader does
not rediscover it.

**Arm-level attribution is not built** (`W32-1b`, owned by W32). `_type_map` unions every arm's
contribution onto one dotted path, so a GLM-only field declared on the GBM arm still passes.
Fixing it means threading arm identity through `_variants`' return type and every caller, which
is its own slice rather than a widening of an existing one.

## Verified

2026-08-22 — W32-1, the contracts-and-drift-guard slice, which added the `required`,
`additionalProperties` and scalar-constraint comparisons and the meta-guards that control them.
Confirmed by the failure that motivated the slice: `GroupingEvidence.source_level_stats` was
declared in `docs/contracts/schemas/grouping.schema.json` from Phase 0 and **absent from the
Python model throughout**, with every check green the whole time — the field is nested under
`evidence`, and the field-name comparison reads top-level names only. Six further real defects
fell out of the three new comparisons on their first run. The lesson to carry: a guard's reach
is a claim like any other, and the only evidence for it is a named path it is asserted to
reach.
