---
id: RL-9855
family: ruling
title: PL-1267 DP-5 decided — a named portfolio joins by same-named or declared-banded key, the cache key covers the bandings, and the diff reports its coverage
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: eeda8f4ba20d247ac18d6a35d7f81589c8527ed2
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1267, FR-231, FR-228, FR-232]
---

# RL-9855 — PL-1267 DP-5 decided — a named portfolio joins by same-named or declared-banded key, the cache key covers the bandings, and the diff reports its coverage

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-effort-high`, launched with
`claude --effort high` on the maintainer's order of 2026-09-30 09:34:27 BST (`to-lead.md`,
entry headed "maintainer order: re-spawn the decision-maker at high effort"). The session's
own `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=high`.

The record was prepared at effort `medium` (PR #941, head `490b7ef4`, "PREPARED, NOT
RULED"). Its evidence, options and prepared recommendation are kept below as prepared.
**The decision is in "Ruled".** This pass confirmed option (d). It also found that one of
(d)'s stated premises is false at this tree: the cache key does **not** cover the table's
bandings. It adds the obligation that closes that gap. It keeps the working id 9855; the id
is minted at the lead's merge turn.

## Evidence, read at `dd25db94bad0b511042f536213a07e720677aad5` (origin/main)

*Refreshed 2026-09-30 at origin/main `0bc69b5b`: nothing changed.* *Re-verified 2026-09-30 at
`eeda8f4b` for this ruling:* `git diff --stat dd25db94 eeda8f4b --
packages/pricing-core/src/pricing_core/rate_tables backend/src/app/platform/rate_tables.py
backend/src/app/api/rate_tables.py backend/src/app/platform/diff_cache.py
packages/pricing-core/src/pricing_core/modelling/bandings.py packages/model-schema
docs/plans/PL-01267*` prints nothing, so the citations below hold at the ruling tree.
- PL-1267 and every code file cited below are unchanged since `dd25db94` (`git diff --stat`).
  That covers `operations.py`, `platform/rate_tables.py`, `api/rate_tables.py`,
  `diff_cache.py`, `bandings.py` and `model-schema`.
- `03` gained one line at `:1180`, after every `03` line cited here. `03:749` is still the diff
  route row.
- PL-1267's DP-5 is still "open (decision-maker)".
- None of this record's citations was a working id that has since minted.

**The row.** PL-1267 (`docs/plans/PL-01267-wk-673-dislocation-with-attribution-map-plan.md`)
has DP-5 at `:362`. It asks how FR-231's diff gets "the exposure weight behind each cell
(from the portfolio dataset)": which portfolio, and how a row maps to a cell.
- It blocks Slice 7 only (`:400`, `:604`).
- Slice 7's scope is at `:585-606`.

**Premise (k), plan `:319`, checked line by line.**

| Plan says | At this tree |
|---|---|
| `pricing_core/rate_tables/operations.py:336` takes `weights` | **CONFIRMED, with a caveat.** `:336` is the private `_compute_diff`'s `weights: Weights \| None` parameter. The public entry is `diff_vs_previous(..., weights: Weights \| None = None)` at `:383-392`. `Weights = Mapping[KeyTuple, Decimal \| int \| float]` is at `:87-88`. Weights are keyed by the cell's key tuple, so the join must produce key tuples in `RateTable.keys` order. |
| `backend/src/app/platform/rate_tables.py:237` passes none (`:253-254`) | **CONFIRMED.** `diff(..., portfolio_dataset_version_id: UUID \| None = None)` is at `:237-246`. `:253-254` is its docstring: "this slice passes none — the portfolio-dataset join is not yet built". The calls at `:294` and `:296` pass no `weights`. |
| The route `rate_table_diff` (`api/rate_tables.py:314`) has no portfolio parameter | **CONFIRMED.** `:314-323`: the only query parameter is `against`. |
| `03:748` has no portfolio parameter | **DIFFERS in line only.** `03:748` is the bulk-operation row. The diff route is `03:749`: `/api/v1/rate-tables/{slug}@{version}/diff?against=`, "Cell-level diff with exposure weights (FR-231)". It names no portfolio parameter. |
| The DP3 cache keys on portfolio identity (`diff_cache.py:81-88`) | **CONFIRMED.** The key is `rate_table:diff:{current_hash}:{baseline_hash}:{portfolio}`, with `"none"` when absent. |

**What the plan does not name.**
1. **A rate-table key already declares its own banding.**
   - `FR-228` (`03:119`): key columns are "each bound to a Factor or a banded input".
   - `RateTableKey` has `banding_ref: ArtifactRef | None`
     (`packages/model-schema/src/model_schema/rating.py:661-668`).
   - A `Banding` names its source `column` (`model_schema/modelling.py:339-360`).
   - `pricing_core.modelling.bandings.apply_banding(series, banding)` exists (`:419`).

   So the planner's motivating derived case, "a banded age", can be weighted **from the table's
   own declaration**, with no algorithm context: band the portfolio's `banding.column` with the
   pinned Banding version, then join.
2. **Option (b)'s mechanism is mislabelled.** A rate table is fed by a `table` step,
   `RatingTableStep`, whose `key_expr: list[str]` is at `rating.py:282-287`. A `lookup` step
   (`:274-279`) feeds a *reference* table. (b) would evaluate `key_expr` over portfolio rows,
   which means running expressions and so pulls in `pricing-core`'s expression evaluator and
   the algorithm's upstream steps. It is a partial re-rate, not a join.
3. **The portfolio frame's schema is not yet written.** `03` §4.8 is held for WK-673 to design
   (`03:575`), and PL-1267 Slice 1 writes it. The name of the exposure column that (a) sums
   therefore depends on Slice 1, and DP-5 should name it by reference to that schema, not by a
   literal.

## Options

| | Option | For | Against |
|---|---|---|---|
| (a) | A `portfolio` query parameter naming a Dataset Version. A row maps to the cell whose `RateTable.keys` equal its same-named columns. Weight = Σ exposure per cell. A missing key column is refused by name. | Matches the cache key (premise k). No algorithm context. The figure cites its portfolio. | Refuses every banded key, which is the common case for a continuous factor such as age or vehicle value |
| (b) | Through a Rating Algorithm Version: evaluate the `table` step's `key_expr` over portfolio rows | Honours any derivation | The diff depends on an algorithm. It needs the expression evaluator and every upstream step, which is a partial re-rate. The cache key would also have to carry the algorithm version, which it does not. |
| (c) | A workspace default portfolio, with (a)'s join | No parameter to pass | Hides which portfolio weighted the figures, which an actuary must be able to cite |
| (d) | **Not in the plan.** (a), plus: where a key declares `banding_ref`, band the portfolio's `banding.column` with that Banding version (`apply_banding`) before the join. A key that is neither same-named nor banded is refused by name. | Covers the banded case from the table's own FR-228 declaration. Stays a join, with no algorithm. The cache key is unchanged, because the table hash already fixes the `banding_ref`. | Loads a Banding artifact in the diff path. A key derived by an arbitrary expression is still refused. |

## Prepared recommendation (superseded by "Ruled"): (d). This departs from the planner's "(a) first, (b) where a key is derived".

- **(d) keeps what the planner valued in (a):** an explicit, citable portfolio, no algorithm
  dependency, and the existing cache key. It also removes (a)'s main gap using a declaration
  that FR-228 already makes.
- **(b) should not be the planned escape hatch.** It turns a table diff into a partial re-rate,
  and it would need a new cache-key component.
  - The case (b) alone covers is a key produced by an arbitrary expression, not by a Banding.
  - (d) refuses that case by name, and the refusal says so.
  - If practice shows such keys are common, that is a later spec change, not a Slice 7 build.
- **What (d) leaves to the ruling pass:**
  - A `banding_ref` pins a version. This is checked at this tree: `ArtifactRef` has
    `version: int` and renders as `{type}:{slug}@{version}`
    (`packages/model-schema/src/model_schema/refs.py:56-75`), and `banding` is an artifact
    type (`:24`). So the table hash fixes the banding, and the cache key stays sound. The high
    pass should re-confirm that the table hash covers `keys`.
  - Name the exposure column through Slice 1's `03` §4.8 schema.
  - State that a diff without `portfolio` answers unweighted and says so (plan `:595-596`
    already has this).
- **The error code for a refused key.** The plan says "refused by name". The ruling pass should
  pick an existing code, `VALIDATION_FAILED` 422 with the key named, over a new one, unless
  `03` §5.1 already owns a closer one. I did not check this at this tree.

## Ruled

### Presence and absence, as verified at `eeda8f4b`

| Claim | Verdict | How it was verified |
|---|---|---|
| The diff cache key covers the table definition (its `keys` and each `banding_ref`) | **false** | `diff` (`backend/src/app/platform/rate_tables.py:237`) builds the key from `version_content_hash(current_cells)` and `version_content_hash(baseline_cells)` plus the portfolio id (`:285-289`). `version_content_hash` (`backend/src/app/platform/diff_cache.py:46-56`) hashes the **cells** only: canonical JSON of the cell dicts, with row order ignored. The definition, `RateTable.model_validate(version_row.definition)` (`rate_tables.py:276`), is not in the key. Two versions with identical cells whose key declares a different `banding_ref` therefore share a key. *The prepared record's "the table hash already fixes the `banding_ref`" is corrected here.* |
| How weights enter the diff | **present** | `_compute_diff` (`packages/pricing-core/src/pricing_core/rate_tables/operations.py:331-381`) looks up `weights.get(key)` for each changed, comparable cell (`:361-364`). It returns only `exposure_weighted_mean_change_pct` from them, and `None` when no changed cell carries a weight (`:367-375`). A portfolio that matches no cell therefore yields `None`, the same value as "no weights given". |
| Banding a portfolio column drops nothing silently | **present** | `apply_banding` (`packages/pricing-core/src/pricing_core/modelling/bandings.py:419`): "Every value gets a level or an error; nothing is dropped. Out-of-range values and nulls follow the policies the artifact declares". |
| A key declares its own banding | **present** | `RateTableKey.banding_ref: ArtifactRef \| None` (`packages/model-schema/src/model_schema/rating.py:661-668`). `Banding.column` names its source (`modelling.py:339-360`). An `ArtifactRef` pins a version (`refs.py:56-75`). |
| A dedicated error code for a missing join column | **absent** | `03` §5.1's list of owned codes (`03-rating-engine.md:771-782`) was read. It has `RATE_TABLE_MISS`, `RATE_TABLE_INCOMPLETE` and `RATE_TABLE_KEY_DUPLICATE`, and none of them is about a portfolio column. |

### DP-5 — option (d)

1. **Which portfolio.** The caller names it: a `portfolio` query parameter on
   `GET /api/v1/rate-tables/{slug}@{version}/diff` (`03:749`), naming a portfolio Dataset
   Version. The frame is read through Slice 2's reader against `03` §4.8's portfolio-frame
   schema, which Slice 1 writes. The exposure column is **the one that schema names**, never
   a literal chosen here. There is no workspace default (option (c)), because the figure must
   cite its portfolio.
2. **How a row maps to a cell.** For each `RateTableKey` of the **current** version's
   definition (the one `diff` already uses for both sides, `rate_tables.py:276`):
   - **a key with no `banding_ref`** maps from the portfolio column of the same name;
   - **a key with a `banding_ref`** maps from the pinned Banding version's `column`, banded with
     `apply_banding`. Its out-of-range and null policies apply as the Banding declares them;
   - **any other key** — no same-named column, and no banding — is **refused, by name**.

   The per-cell weight is Σ exposure over the rows that map to that cell, aggregated in
   Polars, and passed as `weights` to `diff_vs_previous` or `diff_vs_seed`. A band label is
   matched against the cell's key in the cell's own string form. A test proves that the two
   agree.
3. **Refusals.** Each is `VALIDATION_FAILED` 422, naming the column. No new code is added:
   `03` §5.1 owns none for this (the table above), and the generic code with a named field is
   the platform's form. The cases:
   - a same-named key column absent from the frame;
   - a banded key's source column absent from the frame;
   - a key that is neither same-named nor banded;
   - **a portfolio whose rows match no cell of the table.** Without this refusal, the weighted
     mean reads `None`, indistinguishable from an unweighted diff (the table above).
4. **Coverage is reported.** When a portfolio is given, the diff carries two figures: the
   portfolio's total exposure, and the exposure that mapped to a cell of the current
   version. A reader then sees how much of the book the weights cover. They are fields of
   `RateTableDiff` (`model-schema`), regenerated into the contract (FR-451's drift check).
5. **The cache key covers the bandings — new at this pass.** When a portfolio is given, the
   DP3 key also carries each key's `banding_ref`, or a hash of the definition's `keys`. So two
   versions with identical cells but a different banding never share a weighted entry.
   Without a portfolio, the diff is unweighted and the cells alone determine it, so the key
   may stay as it is.
6. **No portfolio** → the diff answers unweighted and says so (PL-1267 Slice 7, `:596-597`).
7. **(b) is not planned.** A key derived by an arbitrary expression, rather than by a declared
   Banding, is refused by name (item 3). If practice shows such keys matter, that is a later
   spec change, not a Slice 7 build. (b) would turn a table diff into a partial re-rate that
   depends on an algorithm version, which the cache key does not carry.

**Why (d).** It keeps everything the planner valued in (a): an explicit, citable portfolio,
no algorithm dependency, and a join rather than an evaluation. It removes (a)'s main gap,
the banded key, which is the common case for a continuous factor, and it does so using a
declaration FR-228 already requires of every key (`03:119`).

## What it obliges

- **This commit:** this record only. The route row and FR-231's clarification are Slice 7's
  "spec first" (`PL-1267:588-589`). They depend on Slice 1's `03` §4.8 schema, which does not
  exist yet.
- **PL-1267 (the planner's file, not edited here):** DP-5's resolver cell cites this record
  once it is minted. Slice 7's scope gains items 3 (the zero-match refusal), 4 (the coverage
  fields and their contract regeneration) and 5 (the cache key's banding component). Its
  line "the DP3 cache key already carries the portfolio identity" is true but not
  sufficient.
- **WK-673 Slice 7:** items 1 to 6.

## Acceptance — the violation that must become detectable

The violation: **a weighted diff whose weights do not come from the named portfolio under
the table's own key declaration.** Each case is shown failing on deliberately broken input:
- A portfolio missing a same-named key column, or a banded key's source column, is refused
  with that column named. So is a key that is neither same-named nor banded.
- A portfolio whose rows match no cell is refused. With the refusal removed, the diff returns
  a `None` mean, and the test fails.
- A banded key's weights on a fixture equal a hand-computed Σ exposure per band. A label-format
  mismatch between the band labels and the cell keys makes this test fail.
- Two table versions with identical cells but different `banding_ref`s, diffed against one
  portfolio, produce two cache entries. With the banding component removed from the key, the
  second request is served the first one's weights, and the test fails.
- The coverage figures on a fixture equal the fixture's total and matched exposure.
- Two portfolios give two cache entries, as the plan already requires.
