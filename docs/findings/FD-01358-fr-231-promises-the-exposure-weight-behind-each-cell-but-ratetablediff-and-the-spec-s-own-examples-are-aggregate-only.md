---
id: FD-1358
family: finding
title: FR-231 promises the exposure weight behind each cell, but RateTableDiff and the spec's own examples are aggregate-only
status: active
created: 2026-10-01
owner: auditor
tree: 0e2c6a1d7d1539b0f97447c8be43c5931d80cf68
corrected_by: []
relates: [WK-673, FR-231, FR-232, PL-1267]
---

# FD-1358 — FR-231's per-cell weight against an aggregate-only RateTableDiff

**Filed** by auditor-rl9855, found while auditing the DP-5 ruling (working id 9855) (draft PR #941), which flagged it and
decided nothing. The `tree:` is the tree of `9b0fb97c`; the cited
spec, model-schema and code files are unchanged at `101e32dc`.

## Finding

**Severity: MEDIUM; owner WK-673.** FR-231 and the delivered diff shape disagree, and the spec disagrees with itself.
It **predates the DP-5 ruling (working id 9855)**; that ruling reported it.

- **The requirement.** `docs/specs/03-rating-engine.md:122`, FR-231: "Rate table edits are diffable cell-by-cell
  against any prior version, with the diff showing absolute and relative change and the exposure weight behind each cell
  (from the portfolio dataset), so an actuary sees which edits matter." `grep -n "FR-231" docs/specs/*.md` shows no dated
  amendment on the row that narrows it to an aggregate.
- **The shape.** `RateTableDiff` (`packages/model-schema/src/model_schema/rating.py:717-729`) has three fields:
  `changed_cells` (`:727`), `max_abs_change_pct` (`:728`) and `exposure_weighted_mean_change_pct` (`:729`). It carries no
  per-cell row, so neither a cell's absolute change, nor its relative change, nor its weight is returned.
- **The spec's own examples are aggregate.** `03` §4.2 shows `diff_vs_previous` and `diff_vs_seed` with `changed_cells`,
  `max_abs_change_pct` and `exposure_weighted_mean_change_pct` only (`:304-306`); §5.2's `diff_vs_previous` and
  `diff_vs_seed` return `RateTableDiff` (`:980-983`). So the spec is aggregate in §4.2 and §5.2 and per-cell in FR-231.
- **The route.** `GET /api/v1/rate-tables/{slug}@{version}/diff` is described as "Cell-level diff with exposure weights"
  (`:785`).

**Why MEDIUM.** The weighted mean is delivered, so nothing is wrong or silent in what the diff returns. What is missing
is the thing FR-231 gives as its purpose: "so an actuary sees which edits matter". Without per-cell change and weight, an
actuary sees that the weighted mean moved, not which cells moved it. It is not HIGH: no figure is wrong, and the aggregate
is a usable first slice. It is not LOW: the requirement as written is unmet, and the shape is a published contract
(`docs/contracts/`, FR-451) that a later per-cell addition changes.

## Evidence

Every citation above was read at the evidence tree: `03-rating-engine.md:122` (FR-231 as written, no dated amendment on the row),
`rating.py:717-729` (the three fields of `RateTableDiff`), `03:304-306` and `:980-983` (aggregate examples and signatures) and `:785`
(the route row). Predicate for "no amendment": `grep -n "FR-231" docs/specs/*.md` over `docs/specs` at `101e32dc`, which returns the
row at `03:122` and the unrelated mentions at `:123`, `:317`, `:782`, `:785`, `:1041` (the other specs name none). No test or run was needed: the
claim is that a field does not exist.

## Why it matters now

`PL-1267` Slice 7 implements FR-231's weights, and the DP-5 ruling (working id 9855) (DP-5) adds two **aggregate** coverage figures to
`RateTableDiff`. That deepens the aggregate shape. the DP-5 ruling's FR-231 dated clarification must not say the per-cell weight
is delivered. A per-cell result also interacts with FR-232: a parquet-stored table's diff is a Job returning "the same
artifact", so a per-cell artifact over millions of cells is a different size of result than three numbers.

## Disposition

Owner WK-673 (Slice 7 implements FR-231; it decides the shape with the spec change it writes first). Two ways to close,
both a spec change before code (`CLAUDE.md` §0), and the choice is the lead's or maintainer's:

- **Amend FR-231** with a dated clarification: the diff returns the aggregates; a per-cell view is a later requirement.
- **Add per-cell output** to `RateTableDiff` (or a paged cells resource) with its weight, through `model-schema` and the
  contract regeneration, with FR-232's Job path sized for it.

Evidence would be a test that the diff of a two-cell change returns each cell's absolute change, relative change and
weight (red on the current tree), or the amendment line. The lead gives the verdict.

Filed 2026-10-01 as working id 9785; minted 2026-10-01 as FD-1358.
