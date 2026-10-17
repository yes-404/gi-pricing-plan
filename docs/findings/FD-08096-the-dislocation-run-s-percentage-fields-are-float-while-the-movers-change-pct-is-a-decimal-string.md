---
id: FD-8096
family: finding
title: The dislocation run's percentage fields are float while the movers' change_pct is a decimal string
status: active
created: 2026-10-17
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, WK-675, PL-8095, FR-21]
---

# FD-8096 — The dislocation run's percentage fields are float while the movers' change_pct is a decimal string

## Finding

**LOW; owner WK-1178; verdict deferred with an owner** (the maintainer to the lead, about
19:42 BST on 2026-10-17: "The dislocation.py float pct fields → a LOW FD (WK-1178) in D21; do
not widen S8"). Four fields of the dislocation run are typed `float | None`, while the S8
delta (PL 8095, `origin/pl-1551-s8-delta-2026-10-17`) rules the new movers row's `change_pct`
as `PositionalDecimalStr`, rounded to 6 places toward +∞. One route family would then carry
two types for the same quantity, a percentage change.

## Evidence

At `origin/main` 9469721d, `packages/model-schema/src/model_schema/dislocation.py`:

- `:84` `DislocationTotals.change_pct: float | None`
- `:105` `DislocationBand.mean_change_pct: float | None`
- `:113` `SegmentSlice.mean_change_pct: float | None`
- `:163` `AttributionItem.mean_change_pct: float | None` (the class holding `shapley_minor`,
  `isolated_minor`; the same file also types `cumulative_change_pct` at `:164` and
  `RungContribution.contribution_pct` at `:120` as `float`; the brief named four fields, these
  two are the same predicate and are listed so the owner sees the whole set)

The hand-authored contract agrees with the code: `docs/contracts/schemas/dislocation-run.schema.json`
declares `change_pct` (`:23`) and `mean_change_pct` (`:49`, `:63`) as `{"type": ["number", "null"]}`,
and the generated schema emits `"type": "number"`. The `03-rating-engine.md` §4.6 example
(`:663-673`, `:683-687`) shows them as JSON numbers (`-14.2`, `1.94`).

PL 8095 item 5 records the contrast as an observation outside its scope and names the four
`dislocation.py` lines; it routes the question to the lead.

## The rule question

Is a percentage a quantity the exact-decimal rule covers? Two readings:

- **`CLAUDE.md` §7** ("Money is integer pence/cents, or Decimal in the rating path — never
  float") binds money. A percentage change is not money on its face, and the dislocation
  analysis runs in the analytics path, not the rating path. §7 does not bind these fields.
- **`FR-21`** (`docs/specs/00-overview.md:233`) says the *exact-decimal types* — `DecimalStr`
  and `Relativity` — refuse a `float`. It is a rule on those types, not a rule that a field
  must use them. A field typed `float` is outside it. FR-21 does not apply; it does give the
  reason the newer movers row uses a decimal string.

What the spec does fix: `03` §4.6 (`:705`) rounds `abs_change_pct_quantiles` "once to 6 places
toward +∞" so that rounding never brings a figure under FR-224's bound. I found no
requirement in `docs/specs/` that fixes the wire type of `change_pct`, `mean_change_pct`,
`cumulative_change_pct` or `contribution_pct`; their `:647` amendment calls two of them
"derived views" of integer minor units. Predicate: `grep -rn "mean_change_pct\|contribution_pct\|cumulative_change_pct" docs/specs`
at tree 9bd63545 (worktree docs-d21), read for a clause stating a type.

**Consequence.** After S8 lands, `/movers` rows carry `change_pct` as a decimal string, and
`totals.change_pct` on the same run carries a JSON number. A client formats and compares two
types for one quantity. The float values are also computed from integer minor units, so the
float form drops digits the decimal form keeps; for display this is harmless, for a
threshold comparison against `mover_threshold_pct` (a `DecimalStr`) it is not exact.

## Options (none picked)

1. **Leave as float.** Declare in `03` §4.6 that run-level percentages are display values and
   movers' `change_pct` is the exact one. Cheapest; keeps two types by rule.
2. **Retype all as `PositionalDecimalStr`**, 6 places, ROUND_UP as for the quantiles. Breaking
   change to the contract, the generated OpenAPI and the frontend types; one commit across spec,
   schema, code and tests.
3. **Retype only those a comparison reads** (`totals.change_pct`), leave means as float.
   Smaller, but leaves three of one family inconsistent.

## Disposition

Deferred with an owner: WK-1178. Decision on the option belongs to the lead or an RL; this
record picks none. The event that next discharges it: a merged spec-and-code change that
retypes the fields, or a dated ruling that keeps them `float` and says why. Out of scope here
and not opened: `exposure_share` (`_Share`) is also a float in the same file.
