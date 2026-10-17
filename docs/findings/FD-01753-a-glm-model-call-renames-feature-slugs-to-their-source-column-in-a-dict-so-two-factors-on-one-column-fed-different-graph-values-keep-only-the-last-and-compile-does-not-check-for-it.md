---
id: FD-1753
family: finding
title: A GLM model_call renames feature slugs to their source column in a dict, so two Factors on one column that are fed different graph values keep only the last, and compile does not check for it
status: active
created: 2026-10-17 # original date 2026-10-16, set at the filing; minted 2026-10-17
owner: auditor
tree: a2f77b2dcad5aaec41a5f10aa664383caf421e8b
corrected_by: []
relates: [WK-1178]
---

# FD-1753 — `_GlmScorer.predict` collapses two feature slugs that name one source column, silently

*(Minted 2026-10-17 as FD-1753 from working id 8070, in the D18 batch mint PR.)*

*(Filed under working id 8070 (written "FD 8070" in prose), supplied by the lead. Authority: the
maintainer's entry "2026-10-16 10:47:33 BST", Observation B, in `channel/to-lead.md`, which sets
the owner (WK-1178), asks for the severity from a constructed case, and names the remedy. Every
read below was made at `origin/main` `a2f77b2dcad5aaec41a5f10aa664383caf421e8b`. **Amended
2026-10-16, before this finding merges:** the scratch test was written while SL-1455's ALONE gate
was in progress and run afterwards, in the small slot, 2026-10-16 11:08:14 to 11:09:20 BST
(reported in the lead's entry "2026-10-16 11:10:37 BST", `from-lead-2026-10-09.md`); its result
is quoted under Evidence 3 and the severity below is set by it.)*

## Finding

**Severity: HIGH by the 10:52:08 rule, on the run of 2026-10-16 11:08:14 to 11:09:20 BST.** The
maintainer's rule (entry "2026-10-16 10:52:08 BST", `to-lead.md`) was: a run that is red as
constructed, with no error, is HIGH. The run is red as constructed: `fd8070_collision_test.py`,
"2 passed in 11.14s" (the asserts state the defect), compile accepts the graph and the
`model_call` returns the adjusted value with no `MODEL_CALL_ERROR_KEY`. The maintainer's entry
"2026-10-16 11:11:03 BST", item 4, records the same: "FD 8070 HIGH (reproduced on main, silent)".
A rating graph that compile accepts today can
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

Scratch test (written, then run: 2 passed in 11.14s, below): `/home/puzhenhao1989/gi-pricing-plan.local/scratch/fd8070_collision_test.py`.
It asserts compile accepts the graph, that the three prices (intended, raw-only, adjusted-only)
are distinguishable, and that the `model_call` returns the adjusted-only price with no
`MODEL_CALL_ERROR_KEY`. It was run through `run-small.sh` (see the two runs below).

**The run (2026-10-16 11:08:14 to 11:09:20 BST, the small slot, through `run-small.sh`, as the
lead's entry "2026-10-16 11:10:37 BST" reports it):** "2 passed in 11.14s". The two tests assert
the defect, so a pass is the defect shown, not a green result for the product: compile accepts the
graph; the `model_call` returns `on_adj` (the adjusted-only price) with no `MODEL_CALL_ERROR_KEY`,
which is not the intended price; the three prices (intended, raw-only, adjusted-only) are
distinct. The severity no longer rests on the code reading alone.

**Re-run by the auditor, 2026-10-16 22:22:14 BST (Europe/London), against `origin/main`
`a2f77b2d`'s code (this worktree changes docs only), once through `run-small.sh`:** the scratch
test copied to `packages/pricing-core/tests/test_fd8070_collision.py` (the copy deleted after the
run, not committed): `2 passed in 3.16s`, rc 0. **It agrees with the relayed line** ("2 passed in
11.14s"): same count, same outcome; only the duration differs (load on the box). No raw log of the
11:08:14 run survived in `scratch/`, which is why the run was repeated.

### 4. A second route to the same loss: two graph names, one slug

`feature_map` is a `dict[str, str]`: the keys are unique, the values are not. Two graph names
mapped to **one** slug give `feature_row` one entry (`runtime.py:754-758`, the later wins), before
`predict` is reached. Compile's coverage check is then satisfied if every other slug is mapped.
This is a smaller exposure (the author names the slug twice on purpose) and the same guard covers
it. It was found by reading and is not in the scratch test.

### 5. The two arms not read first time (read at `origin/main` a2f77b2d; nothing run)

**(a) The GBM arm: no source-column rename, so no `:818` collision. Verdict: the same guard,
and only for the route Evidence 4 already names.** `_predict_model` (`runtime.py:594`) takes the
GBM branch at `:610-626`. The frame is `pl.DataFrame([dict(feature_row)])` (`:615`), so it is
keyed by the **feature slug** exactly as `feature_row` was built at `:754-758`; `_GlmScorer.columns`
and the `:818` comprehension are not on this path. `predict_gbm` is called with `factors=()`
(`:626`), and with no Factors it reads each `result.feature_order` slug straight off the frame
(`gbm.py:1240`, the `else` arm: `missing = [slug … if slug not in data.columns]`, then
`_encode` over `terms={slug: slug …}`). So two Factors on one raw column fed different graph
values stay two columns for a GBM, and each is read under its own slug; the GLM defect does not
exist here. The one loss left is upstream of the dispatch and shared by both arms: two graph
names mapped to **one** slug give `feature_row` one entry (`runtime.py:754-758`, the later
wins), which is Evidence 4 and is closed by the same compile check, not a new one. Side note,
not a finding here: a GBM whose spec carries Factors is scored with `factors=()`, so a banded
Factor's banding is not re-applied on this path; that is a modelling-equivalence question for the
slice that owns the GBM arm, and it was not pursued.

**(b) The offset-model merge `columns = {**source.columns, **columns}` (`runtime.py:879`).** The
keys are **slugs**, the values source columns, and in a dict merge the right operand wins: the
main model's entry beats the offset model's on a shared slug. The merged map is the one
`_GlmScorer.predict` applies at `:818` (`self.columns`, `:796-826`), and the offset source then
reads **the same renamed frame** (`offset_source.linear_predictor(frame)`, `:819-821`). Two
cases, with different verdicts:

1. **Different slugs, one column** (a main slug `m` and an offset-model slug `o`, both
   `source_columns=(C,)`). The merge keeps both keys; `:818` then collapses them to the one key
   `C`, later `feature_row` entry wins. This is the Evidence 3 mechanism exactly, with the second
   Factor in the offset model. **Verdict: the same guard** at predict (unequal values for one
   column refused). At compile the guard must group over the **offset model's** Factors too:
   `check_model_call_coverage` groups only the main pin's `factors`
   (`compile.py:969`, `required_model_inputs(pin.factors, …)`), while the save check admits the
   offset model's slugs into `feature_map` (`rating_algorithms.py:120-150`, the
   `offset.kind == "model"` branch), so a compile-time guard that reads only `pin.factors`
   would miss this route. That is a scope clause on the guard, not a new limb.
2. **One slug, two columns** (the offset model's Factor `s` reads `A`, the main model's Factor
   with the same slug `s` reads `B`). `:879` keeps `s -> B` and drops `s -> A` without a word.
   `feature_row[s]` becomes column `B`; the offset Factor still needs `A`
   (`factors.py:176-181`, `resolve_factors` reads `source_columns` off the frame). If no other
   slug supplies `A`, `resolve_factors` raises `FactorResolutionError` (a `ModellingError`,
   `errors.py:42`), which the handler turns into a coded `model_call` failure
   (`runtime.py:771-778`): **loud, not a mispricing.** If another slug also maps to `A`, the
   offset prices on that slug's value: silent and wrong, but it needs a slug shared across two
   models with different source columns **and** a third mapping onto `A`; this finding
   constructed neither the case nor a run. **Verdict: a separate limb** — a different
   mechanism (a static slug-to-column conflict, true of the bundle before any quote, independent
   of the quote's values), so the predict-time unequal-values guard does not see it (the values
   it would compare are keyed by column, after the merge has already chosen). Its fix is a
   bundle-load refusal at `:879`: a slug that maps to two columns across the main and offset
   models is a malformed bundle (`RATING_VERSION_UNPINNED`-style coded `ValueError`, as `:841-872`
   refuses the other malformed shapes). Severity is not ruled here; read as MEDIUM at most (a
   latent trap, loud in the plain case), pending a constructed case.

## Severity: the reasoning

HIGH, because the wrong value reaches a price and nothing says so. The two conditions are both
met at `a2f77b2d`: a graph that compile accepts feeds the slugs different values (Evidence 3), and
the result is a number, not an error (`predict` returns, `runtime.py:820-826`). It is not
CRITICAL on this reading because it needs two Factors on one column **and** two different graph
values for them; a graph that maps the one raw input to both slugs coincides and is priced
correctly. The scratch run of 2026-10-16 11:08:14 to 11:09:20 BST moved this from "read" to "shown".

## Disposition

**Fix with an owner: WK-1178**, in the next D batch (the maintainer's entry places it there).
**Amended 2026-10-16, on the run:** the predict-time guard is no longer SL-1274's. Per the
maintainer's entry "2026-10-16 10:52:08 BST" and the red run it names, it is **its own fast fix
slice, SL 8074 (owner WK-1178; being built off main)**, gated after SL-1543 by the readiness order
of the entry "2026-10-16 10:52:39 BST"; SL-1274 re-merges onto SL 8074 and drops its own copy of
the guard. Item 2 below is read with that change.

The requirement is a property of the fix, from the maintainer's ruling: **a guard that refuses
unequal values for one column; never a silent pick.**

1. **At compile, where the graph shows it.** For each `model_call`, group the `feature_map` values
   by their Factor's source column (the pins give `source_columns`; compile already resolves them,
   `check_model_call_coverage`'s `resolved_pins`). A column reached through two slugs is legal only
   when the two graph names are provably the same value (the same graph name, or names no step
   transforms differently). Otherwise refuse with a coded error that names the step, the two
   slugs and the column, never a quote value (NFR-499). A graph name mapped to two different
   slugs is the same graph value and passes.
2. **At predict: SL 8074 (the fast fix slice, see the amendment above), no longer S4.** The
   paragraph below is the text as filed, kept because it records the guard's form and where it
   was first placed. **At filing: discharged by S4 (SL-1274, branch `sl-1274-wk690-s4-factor-expression`), not by
   this finding's slice.** The maintainer's entry "2026-10-16 10:50:08 BST" (DP-1274-MULTI, (a'))
   moves the predict-time guard into S4: before the frame is built, two inputs that map to one
   column with **unequal** values are refused with a named error; equal values are allowed (the
   normal shared-column case). S4 makes the same collision reachable by a second route (an
   expression factor's source columns are carried as raw keys, a plain factor's slug is renamed to
   the raw column, so both land on one key), which is why the guard travels with S4. This finding
   **cites** that guard (SL-1274 `a820d7a3`, `_GlmScorer.predict`, `MODEL_CALL_FEATURE_COLLISION`; read, not run) for the predict-time limb and does not repeat it; its own slice keeps the
   compile-time guard (1 and 3), its severity (HIGH, main's constructed case above) and main's
   two-plain-factor case. The limb is closed when S4 merges with its red-first pair (unequal values
   give the error, equal values price normally); this finding then records it as discharged by
   SL-1274.
3. **Two graph names onto one slug** (Evidence 4, and the GBM arm's only route, Evidence 5(a)) is
   **this finding's compile-time limb alone, and the predict-time guard cannot catch it.** Read
   at SL-1274 `a820d7a3` (branch `sl-1274-wk690-s4-factor-expression`, verified by reading
   `packages/pricing-core/src/pricing_core/rating/runtime.py`): the handler still builds
   `feature_row = {feature_slug: context[graph_name] for … in step.feature_map.items()}` at
   `:754-758`, keyed by the `feature_map` **value**, so two graph names that map to one value
   collapse to one entry (last wins) before `_GlmScorer.predict` is called. The guard there
   (`MODEL_CALL_FEATURE_COLLISION`, `:826-835`) compares values per **column**, after the
   rename, over the entries it is handed; the dropped value never reaches it. The remedy is a
   compile refusal of a `feature_map` in which two keys map to one value (a coded error naming
   the step and the value, never a quote value, NFR-499); a `feature_map` that names each
   value once is unaffected. This holds for GLM and GBM alike.
4. **Scope of the guard, per verdict (Evidence 5).** The predict-time and compile-time guards
   cover: the GLM case (Evidence 3); the GBM arm's two-graph-names-one-slug route (Evidence 5(a),
   which is Evidence 4 and needs nothing new; the GBM arm has no rename to guard); and the
   offset-model different-slugs-one-column route (Evidence 5(b)1), for which the compile grouping
   must include the offset model's Factors, not only the main pin's. **Outside the guard, a
   separate limb:** one slug mapped to two columns across the main and offset models
   (Evidence 5(b)2), fixed by a bundle-load refusal at `runtime.py:879`; it stays in FD-1753's
   later limb with the compile-time guard and does not ride the fast fix slice unless a
   constructed case shows the silent variant.
5. **Severity is ruled after the scratch run, not on the reading** (the maintainer's entry
   "2026-10-16 10:52:08 BST"). The scratch run is the second small-slot run after END. **RED as
   constructed** (age 25 priced as 45, no error): **HIGH**, confirmed by run; the predict-time
   guard (unequal values for one column: a named refusal; equal values allowed) becomes its own
   small fix slice off main, owner WK-1178, gated right after SL-1543 and ahead of SL-1722 and
   SL-1341; SL-1274 then re-merges onto it and drops its own copy of the guard; the compile-time
   guard stays in this finding's later limb. **GREEN** (the values do not collide as
   constructed): the auditor states why the reading was wrong and severity drops to **MEDIUM**
   (a latent trap); the guard stays in SL-1274 as ruled at 10:50:08. **Outcome (the run of
   2026-10-16 11:08:14 to 11:09:20 BST): RED as constructed, so HIGH, and the guard is its own
   slice, SL 8074.** The Severity text above is set accordingly.

**Proof on a deliberately broken input (CLAUDE.md §13):** the scratch test, red-first. At
`a2f77b2d` it asserts the defect; after the compile-time guard the same graph must be refused at
compile. The predict-time refusal of a bundle that bypasses compile is S4's proof (SL-1274). A
coincident graph (both slugs fed the same value) must still price equal to `predict_glm`.

**The event that next discharges this finding:** the merge of that slice with the proof run
recorded in its ledger.

**Not in this finding.** Observation A (a multi-column expression factor missing from the `:877`
map), which the maintainer's entry places inside S4.

**Amended 2026-10-17, on the maintainer's entry "2026-10-17 11:15:37 BST" in `to-lead.md`**
(heading: "Maintainer: SL 8074 (FD 8070 HIGH) Q1 → (b) with a precision; Q2 → (b)"). Q1 → (b),
precised: the compile exemption holds only for two `input` steps with the same `input_name` AND
the same `on_missing` (and the same default value where `on_missing="default"`); any other pair
is refused. Q2 → (b): the collision check is per component model plus its offset model. The
entry supersedes the interim build and says this Disposition cites it.
