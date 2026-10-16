---
id: FD-8070
family: finding
title: A GLM model_call renames feature slugs to their source column in a dict, so two Factors on one column that are fed different graph values keep only the last, and compile does not check for it
status: active
created: 2026-10-16
owner: auditor
tree: a2f77b2dcad5aaec41a5f10aa664383caf421e8b
corrected_by: []
relates: [WK-1178]
---

# FD-8070 — `_GlmScorer.predict` collapses two feature slugs that name one source column, silently

*(Filed under working id 8070 (written "FD 8070" in prose), supplied by the lead. Authority: the
maintainer's entry "2026-10-16 10:47:33 BST", Observation B, in `channel/to-lead.md`, which sets
the owner (WK-1178), asks for the severity from a constructed case, and names the remedy. Every
read below was made at `origin/main` `a2f77b2dcad5aaec41a5f10aa664383caf421e8b`. Nothing was run:
SL-1455's ALONE gate was in progress, so the scratch test is written and not executed.)*

## Finding

**Severity: HIGH (proposed; the lead's verdict).** A rating graph that compile accepts today can
feed two Factors that share one raw column two different values for one quote, and the GLM then
prices the quote on one of them for both Factors, with no error and no trace entry. The case is
constructed in Evidence 3; it needs no unusual input, only a Factor pair the platform already
treats as legitimate (`02-modelling.md` FR-177 records `shared_source_columns` for exactly this
shape) and an expression step upstream of the `model_call`.

**The mechanism.** A `model_call` step maps *graph names* to *feature slugs* (`feature_map`,
`packages/model-schema/src/model_schema/rating.py:387`). The handler builds
`feature_row = {feature_slug: context[graph_name] …}` (`runtime.py:754-758`), which is keyed by
slug, so two slugs stay two entries. `_GlmScorer.predict` then renames each slug to its Factor's
source column: `{self.columns.get(k, k): v for k, v in feature_row.items()}` (`runtime.py:818`),
with `columns = {f.slug: f.source_columns[0] …}` (`:877`). When two slugs map to the same column
the comprehension assigns the same key twice and **the later entry overwrites the earlier one**.
`predict_glm` then reads one value of that column, and `resolve_factors` applies each Factor's
banding or grouping to that one value. The earlier graph value is dropped without a log line.

## Evidence

### 1. Nothing before `predict` looks at the collision

| Layer | Where | What it checks | Collision seen? |
|---|---|---|---|
| Save | `backend/src/app/platform/rating_algorithms.py:184-221` | each `feature_map` **value** is a Factor slug or the offset column of the pinned model (membership) | no |
| Compile | `packages/pricing-core/src/pricing_core/rating/compile.py:933-975` | `required_model_inputs` (the Factors' slugs) is a subset of `set(step.feature_map.values())` (completeness) | no |
| Bundle load | `runtime.py:841-880` `_glm_scorer` | the bundle carries each Factor, Banding and Grouping; builds `columns` | no |
| Predict | `runtime.py:817-818` | none | collapses silently |

Membership and completeness are both satisfied by a map that names every slug once. Neither looks
at which source column a slug resolves to, and the source columns are only read at `runtime.py:877`,
after both checks.

### 2. Two Factors on one column is a supported shape

`Factor.source_columns` is a free tuple (`modelling.py:143`); no validator refuses a second Factor
over a column another Factor in the same spec reads. The diagnostics code names the case:
`PermutationImportance.shared_source_columns` (`diagnostics.py:981`, `:1106`, FR-177). The
existing test world is a banding of `driver_age` (`test_rating_glm_model_call.py:glm_world`), so a
second Factor over `driver_age` (an identity, or a second banding at other cut points) is the
obvious next Factor an actuary adds.

### 3. The constructed case, and whether compile accepts it

Model: a gamma GLM, Factors `age_fine` (banding of `driver_age`, cut at 38) and `age_coarse`
(banding of `driver_age`, cut at 30), both `source_columns=("driver_age",)`.

Graph:

```
input driver_age (int)                       -> driver_age
expression driver_age + 20 (int)             -> driver_age_adj
model_call feature_map
   {"driver_age": "age_fine", "driver_age_adj": "age_coarse"}
```

Compile: `check_model_call_coverage` finds `{age_fine, age_coarse} ⊆ {age_fine, age_coarse}` and
passes (`compile.py:949`, `:969`); the save check finds both values are Factor slugs. **Compile
accepts it by reading both checks; the scratch test pins the claim by running it.** The
`driver_age_adj` name is an upstream expression step's output, which the handler reads from
`context` (`runtime.py:750`, `:757`), so the two graph names carry genuinely different values.

The quote `driver_age = 25` has `driver_age_adj = 45`. Its intended cell is
`age_fine` from 25 (below 38) and `age_coarse` from 45 (30 or over). Real rows aged 30 to 37
occupy that cell, so the intended price is the model's price for `driver_age = 33`. Instead
`feature_row` is `{age_fine: 25, age_coarse: 45}` (map order), `predict` builds
`{driver_age: 45}`, and the quote is priced as a 45-year-old on **both** Factors. If the map is
written in the other order the quote is priced as a 25-year-old on both. Which value wins is a
property of dict order in the authored JSON, and nothing in the product shows the author that one
value was discarded.

Scratch test (written, not run): `/home/puzhenhao1989/gi-pricing-plan.local/scratch/fd8070_collision_test.py`.
It asserts compile accepts the graph, that the three prices (intended, raw-only, adjusted-only)
are distinguishable, and that the `model_call` returns the adjusted-only price with no
`MODEL_CALL_ERROR_KEY`. Run it, once the gate has ended, as its header says, through
`run-small.sh`. Until it has read rc 0 this severity rests on the code reading above.

### 4. A second route to the same loss: two graph names, one slug

`feature_map` is a `dict[str, str]`: the keys are unique, the values are not. Two graph names
mapped to **one** slug give `feature_row` one entry (`runtime.py:754-758`, the later wins), before
`predict` is reached. Compile's coverage check is then satisfied if every other slug is mapped.
This is a smaller exposure (the author names the slug twice on purpose) and the same guard covers
it. It was found by reading and is not in the scratch test.

### 5. What was not read

The GBM arm (`_predict_model`) was not read for this finding: it feeds a booster by feature name,
and no source-column rename is on that path at `a2f77b2d`, but that is a reading from the
`_GlmScorer` docstring, not a verified absence. The offset model's `columns` merge
(`runtime.py:879`, `{**source.columns, **columns}`) can map a main-model slug and an offset-model
slug to one column in the same way; it was not constructed. The slice should treat both as part of
its scope check.

## Severity: the reasoning

HIGH, because the wrong value reaches a price and nothing says so. The two conditions are both
met at `a2f77b2d`: a graph that compile accepts feeds the slugs different values (Evidence 3), and
the result is a number, not an error (`predict` returns, `runtime.py:820-826`). It is not
CRITICAL on this reading because it needs two Factors on one column **and** two different graph
values for them; a graph that maps the one raw input to both slugs coincides and is priced
correctly. The scratch test, once run, moves this from "read" to "shown".

## Disposition

**Fix with an owner: WK-1178**, in the next D batch (the maintainer's entry places it there).

The requirement is a property of the fix, from the maintainer's ruling: **a guard that refuses
unequal values for one column; never a silent pick.**

1. **At compile, where the graph shows it.** For each `model_call`, group the `feature_map` values
   by their Factor's source column (the pins give `source_columns`; compile already resolves them,
   `check_model_call_coverage`'s `resolved_pins`). A column reached through two slugs is legal only
   when the two graph names are provably the same value (the same graph name, or names no step
   transforms differently). Otherwise refuse with a coded error that names the step, the two
   slugs and the column, never a quote value (NFR-499). A graph name mapped to two different
   slugs is the same graph value and passes.
2. **At predict: discharged by S4 (SL-1274, branch `sl-1274-wk690-s4-factor-expression`), not by
   this finding's slice.** The maintainer's entry "2026-10-16 10:50:08 BST" (DP-1274-MULTI, (a'))
   moves the predict-time guard into S4: before the frame is built, two inputs that map to one
   column with **unequal** values are refused with a named error; equal values are allowed (the
   normal shared-column case). S4 makes the same collision reachable by a second route (an
   expression factor's source columns are carried as raw keys, a plain factor's slug is renamed to
   the raw column, so both land on one key), which is why the guard travels with S4. This finding
   **cites** that guard for the predict-time limb and does not repeat it; its own slice keeps the
   compile-time guard (1 and 3), its severity (HIGH, main's constructed case above) and main's
   two-plain-factor case. The limb is closed when S4 merges with its red-first pair (unequal values
   give the error, equal values price normally); this finding then records it as discharged by
   SL-1274.
3. **Two graph names onto one slug** (Evidence 4) is refused at compile by the same check.

**Proof on a deliberately broken input (CLAUDE.md §13):** the scratch test, red-first. At
`a2f77b2d` it asserts the defect; after the compile-time guard the same graph must be refused at
compile. The predict-time refusal of a bundle that bypasses compile is S4's proof (SL-1274). A
coincident graph (both slugs fed the same value) must still price equal to `predict_glm`.

**The event that next discharges this finding:** the merge of that slice with the proof run
recorded in its ledger.

**Not in this finding.** Observation A (a multi-column expression factor missing from the `:877`
map), which the maintainer's entry places inside S4.
