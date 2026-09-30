---
id: RL-9855
family: ruling
title: PREPARED, NOT RULED — PL-1267 DP-5, how a portfolio row maps to a rate-table cell for FR-231's exposure weight
status: draft                  # PREPARED, NOT RULED — kept draft by the maintainer's ruling (check-33 red is the fail-safe)
created: 2026-09-30
owner: decision-maker
tree: dd25db94bad0b511042f536213a07e720677aad5
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1267, FR-231, FR-228]
---

# RL-9855 (working id) — PREPARED, NOT RULED: PL-1267 DP-5, portfolio row → rate-table cell

> **Nothing in this record is ruled.** It was prepared at medium effort, under the
> maintainer's decision by delegation. It carries evidence, options and a **provisional**
> recommendation only. Do not rely on it. No slice may activate on it: Slice 7 stays blocked.
> The plan's DP-5 row is not resolved by it, and no spec is amended by it. It is never marked
> ready or minted before the effort-high pass.

## Evidence, read at `dd25db94bad0b511042f536213a07e720677aad5` (origin/main)

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

## Provisional recommendation: (d). This departs from the planner's "(a) first, (b) where a key is derived".

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

**Nothing.** This section is held for the high-effort pass.

## What it obliges

**Nothing yet.** Under (d), it would oblige the following in Slice 7:
- `03:749` gains the `portfolio` parameter and the refusal;
- FR-231 gains a dated clarification naming the same-name-or-banded join;
- a negative test for each refusal;
- a test that a banded key's weight equals the hand-computed Σ exposure per band.

## Acceptance — the violation that must become detectable

**Not set, because nothing is ruled.** Under (d):
- A portfolio missing a key column (or a banded key's source column) is refused with that
  column named.
- A banded key's weights, computed on a fixture, differ from an unbanded join's weights.
  A test asserts the banded figure against a hand computation.

Each must be shown failing on deliberately broken input.
