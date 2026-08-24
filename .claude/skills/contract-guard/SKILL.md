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

`COMPARED_SLUGS` is the fifteen slugs that have both. A disagreement is a `CLAUDE.md` §0
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

New map walkers take `(document, node, base, path="", *, arm=frozenset())` and return a dict
keyed by `(arm, dotted.path)`, matching `_type_map` **exactly**, so a key in one map is a key in
another and two maps can be read against each other. Carry `*, _depth=0` only if the walker
recurses through combinators itself rather than delegating that to `_variants`.

**The arm half of that key is not decoration.** Two maps are only comparable after both are
expanded onto one *complete* arm set — `_complete_arms` over the constraint sets **both walked
maps** carry, never `_arms` over a document root. A root reading misses any union nested below
the root, and `model`'s is nested under `spec` and `fit_result`: measured 2026-08-24, deriving
the arm set from the root takes the scalar-constraint comparison from 767 compared keys to 184
suite-wide, and `model` alone from 584 to 1 — **while still passing**. That is the silent-guard
failure this skill's "never count what a walker reached" section exists to catch, so a new
walker owes a reach control naming a path, not a count.

To read a map back as bare dotted paths — for a coverage question, or a pin that names a path
rather than an arm — go through `_paths` / `_flatten_constraints` rather than the raw keys. A
membership test against the arm-keyed map finds every bare path absent on both sides and reports
the reverse of what it was asked.

## Adding a comparison — the order that works

1. **Measure first, in a throwaway script.** How many paths does the new axis reach, on how
   many slugs, and how many disagree? A guard specified without knowing how red it lands is a
   guard someone switches off. The three added on 2026-08-22 land on one or two slugs each —
   `required` on `model` alone, `additionalProperties` on `custom-objective` alone, scalar
   constraints on `grouping` and `objective-certificate` — and that is what made them
   switch-on-able.
2. **Write the walker and the test, with the measured expectation stated.** "Expect 11 passed,
   1 failed, naming `fit_result.terms.[]`" is checkable; "expect it to fail" is not.
3. **Intersect keys, and know what the intersection drops.** A path present on one side only is
   outside the comparison by construction. **This step used to say that case is "arbitrated by
   `test_an_artifact_shape_carries_exactly_what_its_contract_declares`", and that was false** —
   corrected 2026-08-24 (W32-1b), in the same breath as the identical claim in the test's own
   docstring. That test compares field *names*; where a field exists on both sides and only one
   side bounds it, the names agree and it sees nothing. Measured 2026-08-24: 70 dotted paths
   carry a compared keyword on exactly one side, **18 of them at paths where the field exists on
   both sides**. Nothing reports those. `OQ-PLAT-10` owns the general question — every layer of
   the guard is scoped to the intersection of its two sides — so a new comparison should state
   which half of its axis it can and cannot see rather than inherit this sentence's old promise.
4. **Resolve every disagreement it finds** before the slice ends. A red guard at the end of a
   slice is the same artifact as no guard.
5. **Prove it fails on deliberately broken input** (`CLAUDE.md` §13 rule 4) — break the
   *contract* with a one-line `python3 -c`, watch the named failure, `git checkout` the file.
   When the proof breaks the **walker** instead, copy the file aside first (`cp f f.bak`),
   inject, watch it fail, then restore from that copy — and do it last: `git checkout` on a file
   you are mid-edit in destroys more than the injected defect. **Not `git stash`**, which this
   step recommended until 2026-08-24: the stash stack is shared across every worktree of the
   repository and concurrent sessions push and pop it, so a bare `stash`/`stash pop` here can
   restore someone else's work over yours or hand yours to them. A private backup file has
   neither failure mode.
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

**Every count in this section is a measurement of one tree at one moment.** Taken 2026-08-24
on the W32-11 branch, which is `946725f` plus that slice. Re-measure rather than trust it;
`scripts/generate-contracts.py` and `COMPARED_SLUGS` are the two sources.

**11 authored schemas have no generated counterpart** and are therefore compared against
nothing: `approval-request`, `dislocation-run`, `dossier`, `gipp-check`, `monitoring`,
`optimisation-run`, `rate-table`, `rating-algorithm`, `rating-version`, `regression-suite`,
`scoring`. **All eleven describe Phase 2+ artifacts that no model backs yet**, which is why
they are uncompared and not alarming — the residual is bounded by the phase rule rather than
by oversight.

**The Phase-1a gap is closed.** `validation-rule` gained a generated side in W32-2 and
`dataset-version` and `validation-report` in W32-11, so no shape describing an artifact
Phase 1a built is now a hand-authored promise nothing checks. The sentence this section used
to carry — that those three were a genuine gap — is retired rather than reworded, because the
set it named is empty.

**What replaced it is a harder finding, and it is a design question rather than a gap
(`OQ-PLAT-10`).** Every layer of this guard is scoped to the **intersection** of its two
sides: `test_generated_and_authored_agree_on_scalar_types` intersects paths,
`test_generated_and_authored_agree_on_scalar_constraints` intersects paths and then keywords,
and `test_every_eligible_schema_is_compared` — the completeness check — defines an eligible
schema as one with both sides, so it is defined over the complement of the problem. Nothing is
wrong today. What is missing is any way to keep knowing that: **the guard is silent in exactly
the same way whether a shape is one-sided on purpose or by accident.** Ten slugs are
generated-only and five of those say why in a comment beside their entry in
`generate-contracts.py` — but nothing checks those comments, and `peril-structure`'s went
stale for six days, still denying an authored side #133 had added. A deleted authored side
would present identically to a deliberate first written form.

Two figures follow from this and **a written count must say which it means**, because both are
true of the same tree: the guard compares 15 of 15 shapes it defines as in scope, with none
unaccounted for; and 21 of the 36 distinct shapes in the corpus are out of scope by
construction (11 authored-only, 10 generated-only).

**Arm-level attribution is built** (`W32-1b`, 2026-08-24) — the paragraph here previously said it
was not. All three walkers key on `(arm, path)` and all three comparisons expand onto a complete
arm set before intersecting, so a bound or a type declared inside one conditional arm is compared
against that arm alone. What that closed, measured on the repository's own `model-spec`: moving
`max_bins` — the ebm arm's `16 ≤ n ≤ 32768` — into the glm arm left the old walker returning maps
that compared **equal**, 21 keys each, zero disagreements reported either way. The same move is
now drift. `test_two_arms_declaring_different_bounds_are_both_kept`,
`test_a_bound_moved_between_arms_is_drift` and `test_a_closed_map_moved_between_arms_is_drift`
hold the cases.

**What arm attribution did *not* close is arm-level *existence*.** W32-1b delivers type and bound
disagreement on paths shared by both sides *within an arm*; a field that leaves the shared set
entirely — moved between arms so that no arm holds it on both sides — is still reported by
nothing, because every layer intersects. That is `OQ-PLAT-10`, which names the boundary
explicitly, and it is open.

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

2026-08-24 — W32-11, which gave `dataset-version` and `validation-report` their generated
sides and so closed the Phase-1a gap the section above used to name. Two things were learned
by measuring rather than by reading. **First, publishing a shape is what finds its defects:**
`validation-report` had been a hand-authored contract since Phase 0 declaring no `id` at all,
while the model has always required one, and it was invisible until the day a generated side
existed to compare against — the same shape of failure as `source_level_stats` above, found the
same way. **Second, the guard's reach is narrower than "what it does not reach" made it sound.**
Every layer intersects its two sides, so one-sidedness is not something the guard is quiet about
by omission; it is outside the guard's scope by construction, and no test can distinguish a
deliberate one-sided shape from an accidental one. That is `OQ-PLAT-10`. The lesson to carry is
the same one this file already learned, applied one level up: a guard's *scope* is a claim like
any other, and "every eligible schema is compared" is only as strong as the definition of
eligible — which here is the intersection, so the completeness check cannot see the gap it
would need to report.

2026-08-24 — W32-1b, which keyed all three walkers on `(arm, path)` and taught all three
comparisons to expand onto a complete arm set before intersecting. Two corrections to this file
came out of it, both of the same kind: **a sentence here asserted a coverage this repository did
not have.** Step 3 of "Adding a comparison" said the field-name test arbitrates a one-sided
bound — it does not, and 18 of the 70 one-sided bounds in the suite sit at paths where the field
exists on both sides and nothing reports them. "What the guard does not reach" said arm
attribution was unbuilt on the day it was being built. Neither was caught by a test, because
neither is the sort of claim a test is pointed at; both were caught by measuring the thing the
sentence asserted. The lesson to carry: **this file's prose is unversioned evidence, and the
reach controls only guard the numbers that live in code.** A slice that changes what the guard
reaches owes this file a re-read, not just an appended entry — and the corpus figures quoted in
`test_contracts.py` docstrings move whenever `COMPARED_SLUGS` does, as all nine of them did when
W32-11 took it from thirteen slugs to fifteen.
