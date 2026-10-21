---
id: FD-1803
family: finding
title: Rate tables accept non-finite decimals - NaN, sNaN and Infinity pass validate_rate_table
status: closed
created: 2026-10-18   # filed 2026-10-17 under working id 8106; minted 2026-10-18 as FD-1803
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, FD-1802]
---

# FD-1803 — Rate tables accept non-finite decimals

## Finding

**HIGH; owner WK-1178; verdict deferred with an owner. The fix is its own P2 slice, SL 8108 / PL 8107
(planned; GO 22:51:59), gated after SL 8099 → SL-1543.** Authority: the maintainer's entry
"2026-10-17 22:51:59 BST" (`to-lead.md`: FD-1803 → HIGH, verified) and the lead's
"2026-10-17 22:51:15 BST" entry in `from-lead-2026-10-09.md` (A3). A rate table's value is a rating
relativity; a stored `NaN` or `Infinity` reaches the rating path.

## Evidence

All read at `origin/main` 9469721db3d26480824cc1d715da2ec4ca9044d0.

- **The parse:** `packages/pricing-core/src/pricing_core/rate_tables/operations.py:307`,
  `decimal_value = Decimal(raw)`, inside a `try` that catches only `InvalidOperation` (:306-313).
- **What `Decimal` accepts:** `python3 -I -c` over `Decimal(s)` printed
  `NaN Decimal('NaN') False`, `sNaN Decimal('sNaN') False`, `Infinity Decimal('Infinity') False`,
  `-Infinity Decimal('-Infinity') False` (the last column is `is_finite()`). None raises, so none is
  reported as "not a decimal number".
- **Bounds unset:** `class RateTableValue` (`packages/model-schema/src/model_schema/rating.py:1076`)
  declares `min` and `max` as `SchemaDecimal | int | None = None` (:1084-1085). With no bounds the
  :314 and :322 comparisons are skipped, so all four values pass `validate_rate_table`. (The lead's
  brief cited :1104-1105; those lines are not the declaration at this tree.)
- **Bounds set:** `decimal_value < value.min` (:314) or `> value.max` (:322) with a NaN operand raises
  `decimal.InvalidOperation` *outside* the `try`: an unhandled exception (an HTTP 500), not a named
  `OUT_OF_BOUNDS` issue. (Inferred from the stdlib comparison semantics and the code shape; the route
  was not run — no tests in this audit.)
- **Bulk operations reach the same validator:** `_validate_result` (:554-565) calls
  `validate_rate_table`; :393 (`_index_rows`) parses again with `Decimal(row[value_name])`.
- **Every `Decimal(` parse under `rate_tables/`** (`git grep -n 'Decimal(' origin/main -- packages/pricing-core/src/pricing_core/rate_tables`):
  `operations.py` :166, :307, :393, :428, :479, :481, :673, :712, :734, :740, :812, :819;
  `weights.py` :219, :220. Those on stored cell strings (:307, :393, :673, :740, :812, :819) take whatever
  was saved; :166 and :428 go through `str()` of a number.

## FR-234

`docs/specs/03-rating-engine.md:127`: "Rate tables validate on save: complete coverage of the declared
key domain (or an explicit default row), no null values, values within declared bounds, and no key
duplication." It names null, bounds, coverage and duplicates and says nothing of finiteness, so a
non-finite value is neither forbidden nor required to be refused. The fix slice must state the
rule in the spec first (CLAUDE.md §0).

## Disposition

Deferred with an owner: WK-1178; fix SL 8108 / PL 8107 (planned). The event that next discharges it: the
merged SL 8108 with a test that a non-finite value is refused as a named issue, with and without bounds.
Filed under working id 8106.
