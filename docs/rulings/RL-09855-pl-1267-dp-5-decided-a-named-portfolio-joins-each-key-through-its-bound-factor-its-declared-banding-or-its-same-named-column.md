---
id: RL-9855
family: ruling
title: PL-1267 DP-5 decided — a named portfolio joins each key through its bound Factor, its declared Banding or its same-named column, compared in the key's type; the cache key covers the definition
status: draft                  # RULED 2026-10-01, NOT MINTED — draft until the lead's mint turn (check 33 red by design)
created: 2026-10-01              # the ruling date; first prepared 2026-09-30 (see "How this was ruled")
owner: decision-maker
tree: 9b0fb97c9ed1cea743639897351191bc1a862041
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1267, FR-228, FR-230, FR-231, FR-232, RL-1264]
---

# RL-9855 — PL-1267 DP-5 decided — a named portfolio joins each key through its bound Factor, its declared Banding or its same-named column, compared in the key's type; the cache key covers the definition

## How this was ruled

**Ruled 2026-10-01 07:43 BST at effort `high`** by the decision-maker session `dm-dp5`. The
process command line is `claude --effort high --model opus --name dm-dp5`, and the session's
`echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`. The session was opened on
the maintainer's raise of 2026-10-01, as the lead relayed it: "Commission DP-5's ruling now: a
fresh --effort high DM per its role file".

**This record's history on PR #941.** It keeps working id 9855. The lead mints the id at the
merge turn.

1. **Prepared** at effort `medium` (`ca949339` to `490b7ef4`, 2026-09-30, "PREPARED, NOT
   RULED"), evidence tree `dd25db94`. The prepared recommendation was option (d).
2. **A first effort-high pass** by session `dm-effort-high` (`d8ec408d` to `ded14eb3`,
   2026-09-30 10:24–10:45 BST). It confirmed (d) and took in:
   - the maintainer's decisions on `736de32e` (the portfolio must be `validated`; the
     weighted key carries the workspace);
   - the maintainer's decision on auditor-plans' N2 (`dataset:read` only when a portfolio is
     given);
   - auditor-plans' findings F1–F3 and N1.

   That pass was never minted. It set `status: active` on an unminted record.
3. **This pass** re-verified every premise at origin/main `9b0fb97c`. It **replaces (d) with
   (e)**, for the reasons under "New at this pass". **The maintainer's decisions in item 2
   are kept as they were made.** They are inputs to this ruling, not this role's to reopen,
   and they appear in items 7 and 5 below. `status` goes back to `draft` until the mint.

## Locators — evidence tree `dd25db94` against origin/main `9b0fb97c`

`git diff --stat dd25db94 9b0fb97c` was run over every file cited below. Every code file is
unchanged **except** `packages/model-schema/src/model_schema/rating.py`. That file gained one
import line at `:27`, so every later line moves by +1. In `03`, hunks at `:459` (+4), `:740`
(+28) and `:778` (+4) move every later line. `02` moves by +48 before `:2045`. `01`, `06:64`
and PL-1267 are unchanged. The claim column was re-read at `9b0fb97c`, body and all.

| What | At `dd25db94` | At `9b0fb97c` | Claim at `9b0fb97c` |
|---|---|---|---|
| PL-1267 premise (k); DP table; DP-5; Slice 7 | `:319`; `:356`; `:362`; `:585-606` | unchanged | holds; DP-5 still "open (decision-maker)" |
| `Weights`, `KeyTuple` (`pricing_core/rate_tables/operations.py`) | `:85`, `:87-88` | unchanged | holds |
| `_index_rows` | `:322-328` | unchanged | keys are the cells' **stored strings**, exact-matched |
| `_compute_diff` | `:331-381` | unchanged | holds; and `total_weight` 0 divides by zero (`:370-372`), new below |
| `diff_vs_previous` / `diff_vs_seed` | `:383-392` / `:395-404` | unchanged | both call `_compute_diff` identically |
| `_value_matches_key_type` | `:702-717` | unchanged | `int("03")` passes, `bool` is case-folded: stored key strings are **not canonical**, new below |
| `seed_from_model` key construction | `:191-194` | unchanged | `RateTableKey(name=factor, type=STRING, banding_ref=None)` **always**, new below |
| `backend/src/app/platform/rate_tables.py` `diff` | `:237-300` | unchanged | `:253-254` "this slice passes none"; cache read `:285-292` before any portfolio use |
| `api/rate_tables.py` `RatingReadDep`; `rate_table_diff` | `:46`; `:314-364` | unchanged | `against` is the only query parameter; the 202 branch submits `JobKind.RATE_TABLE_DIFF` |
| `worker/rate_table_handlers.py` `_rate_table_diff` | `:24-54` | unchanged | calls `service.diff` with **no cache and no portfolio**, new below |
| `diff_cache.py` `version_content_hash`; `DiffCache.key` | `:46-56`; `:77-88` | unchanged | the hash is canonical JSON of the cell **dicts**, so it covers the column **names**; the key adds the portfolio id |
| `RatingLookupStep`; `RatingTableStep` (`model_schema/rating.py`) | `:275-280`; `:283-288` | `:276-281`; `:284-289` | +1; holds |
| `RateTableKeyType`; `RateTableKey` | `:632-638`; `:661-668` | `:633-639`; `:662-669` | +1; types `int`/`string`/`date`/`bool`; no Factor binding exists |
| `ArtifactRef` (`model_schema/refs.py`); `banding`, `factor` types | `:56-75`; `:24` | unchanged | pins `version: int`; frozen |
| `Banding` (`model_schema/modelling.py`) | `:339-380` | unchanged | "Versioned, never edited"; has `column`; no `status` |
| `Factor.banding_id` / `grouping_id` | `:122-161` | unchanged | a Factor pins its Banding or Grouping by id |
| `apply_banding` (`pricing_core/modelling/bandings.py`) | `:419-463` | unchanged | casts to `Float64` (`:427`); null refusal `:456`; range refusal `:480` in `_resolve_edge`, naming a count and **one** example value |
| `resolve_factors` (`pricing_core/modelling/factors.py`) | `:106` | unchanged | pure; refuses a missing source column and a missing artifact by name |
| `BandingRow`, `FactorRow` unique keys (`backend/src/app/db/models.py`) | — | `:1331`, `:1361` | unique on (`workspace_id`, `slug`, `version`) |
| `load_bandings` / `_refuse_missing` (`platform/transformations.py`) | — | `:390-411` | a missing artifact is `NOT_FOUND` 404, never an empty map |
| `fittable_or_refuse`; `load_version` (`platform/datasets.py`) | `:743-760`; `:763-781` | unchanged | holds |
| `ReadDatasets` (`api/dataset_versions.py`); `rbac._covers` | `:60`; `:205-217` | unchanged | holds |
| ADR-710's tenancy line (`api/deps.py`) | `:26-27` | unchanged | holds |
| `03` FR-228; FR-1186 | `:119`; — | `:119`; `:128` | holds |
| `03` §4.2 `RateTable` example | — | `:284-300` | a **seeded** table whose key declares `banding_ref` |
| `03` §4.8 (portfolio frame held for WK-673) | `:563`, `:575` | `:567`, `:579` | +4; still not designed: PL-1267 Slice 1 has not landed |
| `03` §5.1 bulk-operation row; diff row | `:748`; `:749` | `:784`; `:785` | +36; diff row names no portfolio parameter |
| `03` §5.1 owned error codes | `:771-782` | `:807-821` | +36; no portfolio code; `DATASET_NOT_VALIDATED` absent |
| `01` owns `DATASET_NOT_VALIDATED`; `02` re-raises it | `:929`; `:2045` | `:929`; `:2093` | `02` +48; holds |
| `06` Governed Artifact list | `:64` | `:64` | holds; Banding is not on it |

## New at this pass

1. **Model-seeded tables bind no key.** FR-230 seeding is the only path that builds a rate
   table automatically. It writes every key as `type: string, banding_ref: None`
   (`operations.py:191-194`). Under (d), a seeded table's banded key therefore takes the
   same-named branch: it looks for a portfolio column named after the factor. That column
   holds raw values, never band labels, so nothing matches, and the zero-match refusal is the
   only result. (d) cannot weight the case it was chosen for, on the tables most diffs will
   be about.
2. **A spec-vs-code disagreement, ruled here (`CLAUDE.md` §0).**
   - **The spec.** FR-228 says every key is "bound to a Factor or a banded input" (`03:119`).
     `03` §4.2's own example is a seeded table whose key declares `banding_ref`
     (`03:284-300`).
   - **The code.** `RateTableKey` has no field that can hold a Factor binding
     (`rating.py:662-669`), and seeding binds nothing.
   - **Ruling:** the code is wrong. FR-228 is normative, and the example shows the intended
     reading.
3. **(d) also refuses Grouping and interaction keys, and identity keys that are renamed.**
   - A Grouping key (vehicle group, postcode area) and an interaction key are derived, like a
     band. (d) has no branch for either.
   - An identity factor whose slug differs from its source column also misses, because the
     key is named after the factor.
   - `resolve_factors` (`factors.py:106`) already resolves every one of these from the Factor
     artifact, and it needs no database. It produced the levels that the model's relativities
     carry, and so the levels that seeded cells carry. Its `FactorMatrix` docstring states the
     purpose: "the relativity table weights them by exposure".
4. **Stored key strings are not canonical.**
   - `_index_rows` matches the cells' stored strings exactly.
   - An import accepts `"03"` for an `int` key and `"True"` for a `bool` key
     (`operations.py:702-717`).
   - A portfolio `Int64` value of 3, cast to a string, misses a cell stored as `"03"`, and
     nothing reports it.
5. **The earlier pass's "neither name is in the key" was half wrong.** `version_content_hash`
   hashes the cell **dicts** (`diff_cache.py:46-56`), so the column names are in the hash.
   What the hash does not hold:
   - which column is a key and which is the value;
   - each key's type;
   - each key's `banding_ref` (and, from this ruling, its `factor_ref`).

   The definition component in item 5 is still required. Its reason is corrected.
6. **All-zero weights crash.** If every weighted changed cell has Σ exposure 0, `_compute_diff`
   divides by a zero `total_weight` (`:370-372`). Decimal raises, and the route answers 500.
7. **The 202 path is not covered.** The parquet path runs `_rate_table_diff` in a worker
   (`rate_table_handlers.py:24-54`). The worker has no cache, and its parameters carry no
   portfolio. The earlier text ruled the check order only "before the cache is read", which
   leaves a Job path that has no checks at all.
8. **A binding can dangle.** Nothing at table creation checks that a `banding_ref` resolves.
   Bandings and Factors are unique per (`workspace_id`, `slug`, `version`) (`models.py:1331`,
   `:1361`). So a ref resolves only inside its own workspace.
9. **`apply_banding` on a non-numeric column** fails in a Polars cast (`:427`), not as a
   named refusal. The earlier text's "`bandings.py:456` names the offending values" was also
   wrong: `:456` is the null refusal, which gives a count. The range refusal is at `:480`,
   and it gives a count and **one** example value.

## Options, re-derived

| | Option | For | Against |
|---|---|---|---|
| (a) | A `portfolio` parameter. A row maps to a cell by same-named columns. | Explicit, citable, no algorithm | Refuses every derived key: band, group, interaction, renamed identity |
| (b) | Evaluate the algorithm's `table` step `key_expr` (the plan says "`lookup`", but a `lookup` step feeds reference tables, `rating.py:276-281`) | Honours any derivation | A partial re-rate. The diff depends on an algorithm version that the cache key does not carry. |
| (c) | A workspace default portfolio | No parameter | The weighting portfolio cannot be cited |
| (d) | (a), plus `apply_banding` where a key declares `banding_ref` | Covers a hand-authored banded key | Dead on seeded tables (new item 1). Refuses groupings, interactions and renamed identities (new item 3). |
| **(e)** | (d), plus a key bound to a **Factor** is resolved through that Factor with `resolve_factors` | FR-228's own binding. Covers every factor type a model can carry. Still a join, with no algorithm and no expression evaluator. The labels come from the function that made them. | One optional field on `RateTableKey`, and seeding must set it |

## Ruled

**Option (e).**

1. **Which portfolio.**
   - The caller names a portfolio Dataset Version in a `portfolio` query parameter on
     `GET /api/v1/rate-tables/{slug}@{version}/diff` (`03:785`).
   - The frame is read through PL-1267 Slice 2's reader, against `03` §4.8's portfolio-frame
     schema, which Slice 1 writes.
   - The exposure column is **the one that schema names**. This ruling chooses no literal.
   - There is no workspace default.
2. **How a row maps to a cell.** This applies to each `RateTableKey` of the **current**
   version's definition. That is the definition `diff` uses for both sides
   (`rate_tables.py:276`). Exactly one branch applies:
   - **`factor_ref` set (new field, below).** Resolve the pinned Factor version over the frame
     with `resolve_factors`. Pass the Banding or Grouping the Factor pins, and an
     interaction's operand Factors. The key's value is the resolved level.
   - **`banding_ref` set.** Band the pinned Banding version's `column` with `apply_banding`.
     The Banding's out-of-range and null policies apply as declared.
   - **Neither set.** Use the portfolio column of the key's own name.
   - **Comparison is in the key's declared type, never by raw string.**
     - The key's value from the frame and each cell's stored key string are both read as the
       key's `type`: `int` as an integer, `bool` case-folded, `date` as a date, `string`
       exactly.
     - They match when the two typed values are equal.
     - The weight is then keyed by the cell's **stored** key tuple, which is the tuple
       `_compute_diff` looks up.
   - **The weight.** A cell's weight is Σ exposure over the rows that map to it, computed in
     Polars. It is passed as `weights` to `diff_vs_previous` or `diff_vs_seed`.
     - A cell whose Σ is 0 is given **no** weight, so the division in new item 6 cannot
       happen.
     - A negative exposure value is refused (item 3).
   - **Artifacts are resolved as pinned, under the caller's workspace, with no approval
     check.** A Banding has no lifecycle (`06:64`). A rate table has none either (FR-1186).
     The diff reports what the table declares. Reading them needs no permission beyond item 7,
     because the diff returns only aggregates.
3. **Refusals.** Each one names the key, the column or the ref.
   - **`VALIDATION_FAILED` 422** is the code for each of these:
     - a same-named column is absent;
     - a Banding's or Factor's source column is absent (`resolve_factors` already refuses
       this by name);
     - a banded source column is not numeric. This is checked before `apply_banding` casts.
     - a resolution error: `FactorResolutionError` from a Banding or Grouping policy. The
       response carries its message, which gives the count and the example value;
     - a negative exposure value;
     - **a portfolio whose rows match no cell of the table.**
   - **`NOT_FOUND` 404** for a `factor_ref` or `banding_ref` that does not resolve in the
     caller's workspace. The detail names the key and the ref. This is the form of
     `_refuse_missing` (`transformations.py`). A missing artifact is never an empty map.
   - **The `None` mean.** It has three causes: no portfolio; weights on no changed, comparable
     cell; or only zero-weight cells. Only a zero match is refused. **Item 4's coverage
     figures tell the other cases apart.**
4. **Coverage is reported.** With a portfolio, `RateTableDiff` (`model-schema`) carries two
   figures: total exposure, and the exposure that mapped to a cell of the current version.
   Both are regenerated into the contract (FR-451's drift check).
5. **The cache key** carries everything the answer depends on:
   - the two versions' cell hashes (already there);
   - the portfolio Dataset Version id (already there, `diff_cache.py:77-88`);
   - **always**, a hash of the canonical JSON of the current definition's `keys` and `value`.
     This covers each key's name, type, `banding_ref` and `factor_ref`, and the value's name
     and type (new item 5);
   - **the caller's workspace id when a portfolio is given** (the maintainer's decision on
     `736de32e`).

   **Why this is sound under banding versions.** A ref pins an immutable version (FR-4; a
   Banding is "Versioned, never edited"). A Factor pins its Banding or Grouping by an
   immutable id. Refs are unique per workspace (new item 8). So the workspace plus the
   definition hash fixes every artifact that shaped the weights.
6. **No portfolio.** The diff answers unweighted and says so (PL-1267 Slice 7).
7. **Portfolio permission, scope and status, before the cache read and before any Job.**
   These are the maintainer's decisions, kept unchanged.
   - **Permission.** The route stays `RatingReadDep`, so an unweighted diff stays open to a
     rating-only reader. When `portfolio` is given, the handler also requires
     `Perm.DATASET_READ`, workspace-wide. It is checked without loading the version, so the
     403 is the same for any id.
   - **Scope.** Use `load_version`'s predicate. The answer is one `NOT_FOUND` 404 body for a
     missing version and for another workspace's version. A read may drop the row lock.
   - **Status.** `validated` only, using `fittable_or_refuse`'s predicate. `draft` and
     `archived` are refused with **`DATASET_NOT_VALIDATED` 409**, re-raised from `01`, and the
     detail names the diff. A weighted figure is reproduced from its persisted evidence item,
     never by re-running against an archived portfolio.
   - **Order.** These checks run before the cache is read, and the test runs on a warm cache.
8. **The 202 path (new).**
   - The route runs item 7's checks **before** it submits `JobKind.RATE_TABLE_DIFF`. A refused
     portfolio never becomes a Job.
   - The Job's parameters carry `portfolio`.
   - The worker calls the same service path. That path re-runs the scope and status checks
     under the Job's workspace. A portfolio archived between submit and run fails the Job with
     `DATASET_NOT_VALIDATED`.
   - The worker computes the same weights as the 200 path. It has no cache, and this ruling
     adds none.
9. **The binding.**
   - **The new field.** `RateTableKey` gains `factor_ref: ArtifactRef | None = None`, of type
     `factor`. **A key carries at most one of `factor_ref` and `banding_ref`**, and the
     `model-schema` validator enforces this. `banding_ref` stays for "a banded input" with no
     Factor.
   - **Seeding.** FR-230 seeding sets `factor_ref` on every key to the Factor version that the
     model pins for that relativity entry. A relativity entry with no pinned Factor is
     refused by name at seeding.
   - **Existing versions** are immutable (FR-4), so they stay unbound. Their derived keys are
     refused under item 3 until the table is re-seeded. No migration rewrites them.
10. **(b) is not planned.** A key derived by an arbitrary expression is refused by name. If
    such keys turn out to matter, that is a later spec change.

**Why (e).**
- It keeps everything the planner valued in (a): a citable portfolio, no algorithm, and a
  join.
- It weights the keys FR-228 says every key is: bound to a Factor or a banded input.
- It uses the function that produced the levels, so the band and group labels agree by
  construction, not by convention.
- (d) is the special case of (e) for a hand-authored banded key. On its own, (d) leaves the
  FR-230 path, the main origin of rate tables, unweightable.

## Spec changes this ruling requires

These are recorded here and **applied by Slice 7's spec-first step** under
`.claude/skills/spec-change` (PL-1267 Slice 7, "Spec first"). They are not applied in this
commit, and PL-1267 is not edited.

- **FR-228, dated clarification.** "Bound to a Factor" is `factor_ref`. "A banded input" is
  `banding_ref`. A key has at most one of them. A key with neither is joined by its name.
- **FR-230, dated clarification.** Seeding binds each key to the Factor version the model
  pins.
- **FR-231, dated clarification.** The weight is Σ portfolio exposure per cell, under item 2's
  mapping, from a named `validated` portfolio Dataset Version. Coverage is reported. A
  portfolio that matches no cell is refused.
- **`03` §4.2.** The `RateTable` shape gains `factor_ref`. `RateTableDiff` gains the two
  coverage figures. Both go through `model-schema` and the contract regeneration.
- **`03` §5.1, the diff row (`:785`).** Add the `portfolio` parameter, the 403, 404, 409 and
  422 refusals, and the 202 path's carriage of the parameter.
- **`03` §5.1, the owned codes (`:807-821`).** Add `DATASET_NOT_VALIDATED`, marked "(re-raised from
  `01`)" so that check 10 (one owner per code) holds.

## What it obliges

- **This commit:** this record only.
- **PL-1267, which is the planner's file and is not edited here:**
  - DP-5's resolver cell cites this record once it is minted.
  - Slice 7's scope gains items 3–5, 8 and 9.
  - **The seeding limb of item 9 may be cut as its own process-slice before Slice 7.** Slice
    design is the planner's.
- **Not decided here. Reported to the lead.**
  - FR-231 says the diff shows "the exposure weight behind each **cell**".
  - `RateTableDiff` is aggregate only (`rating.py`, `class RateTableDiff`): it has no
    per-cell rows. Per-cell output is a question about how FR-231 is delivered, not about
    how a row maps to a cell.

## Acceptance — the violation that must become detectable

The violation: **a weighted diff whose weights do not come from the named portfolio under
the table's own key declaration.** Each case is shown failing on deliberately broken input.

**The join**
- **Seeded and banded, red-first.** A table seeded from a fixture GLM with a banded Factor
  is weighted. Σ exposure per band equals a hand-computed figure. With seeding's `factor_ref`
  removed, the request is refused with zero match, and the test fails.
- **One test per Factor type** that `resolve_factors` implements: identity with a slug that
  differs from its column, banding, grouping, and interaction. Each is weighted equal to a
  hand-computed figure.
- **A hand-authored `banding_ref` key** is weighted through `apply_banding`. A table carrying
  both `factor_ref` and `banding_ref` is refused by `model-schema`.
- **Typed comparison.** Cells stored as `"03"` and `"True"` receive the weight of portfolio
  values `3` and `true`. With a raw string join, the test fails.

**Refusals**
- A missing same-named column, a missing source column, a non-numeric banded column, a
  negative exposure, and a portfolio that matches nothing: each gives 422 and names the
  column. With the zero-match refusal removed, a `None` mean comes back and the test fails.
- A Banding with `error` policy that meets an out-of-range value gives 422 and names the
  column.
- A dangling `factor_ref` or `banding_ref` gives 404 and names the key and the ref. A ref
  that exists only in another workspace gives the same 404.
- Only zero-weight changed cells: a `None` mean, no 500, and non-zero coverage figures.
- A matched portfolio with no changed cell: a `None` mean, non-zero matched exposure, not
  refused.
- The coverage figures equal the fixture's total and matched exposure.

**The cache key**
- Two portfolios give two entries.
- The same content and portfolio in two workspaces give two entries.
- Two versions with identical cells whose definitions differ only in a key's role, a key's
  type, a `banding_ref` or a `factor_ref` give two entries, with and without a portfolio.
- Each test is red-first: with that component removed from the key, the second request is
  served the first one's figure, and the test fails.

**Permission, scope and status**
- A rating-only caller succeeds on an unweighted diff.
- With a `portfolio`, a rating-only caller gets 403, the same for an existing id and a
  nonexistent one. With `dataset:read` made route-wide, the unweighted case fails. With the
  handler check removed, the weighted case is served.
- Another workspace's portfolio gives the same 404 as a nonexistent id. This is also tested
  on a warm cache, with the foreign entry placed first. With the checks moved after the cache
  read, the test fails.
- A `draft` portfolio and an `archived` one each give `DATASET_NOT_VALIDATED` 409. A
  `validated` one is accepted.

**The 202 path**
- A refused portfolio on a parquet version gives the refusal and **no Job row**.
- An accepted one gives a Job whose result equals the 200 path's weighted figure on the
  rows-stored twin.
