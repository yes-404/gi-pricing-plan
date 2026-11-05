---
id: FD-1780
family: finding
title: A model_call's feature-collision check compares with `!=`, so two equal NaN values on one column raise the collision
status: closed
created: 2026-10-17
owner: auditor
tree: cf509df89dbebff329bb6b319bcc9bcd2a2c2352
corrected_by: []
relates: [WK-1178, SL-1761, FD-1753]
---

# FD-1780 — A model_call's feature-collision check compares with `!=`, so two equal NaN values on one column raise the collision

*(Minted 2026-10-17 as FD-1780 from working id 8086, in the D20 batch mint PR.)*

## Finding

**LOW; owner WK-1178; verdict proposed `deferred with an owner`** (the lead's brief, 2026-10-17 14:28:39 BST: SL-1761 audit A2 → a D20 FD). `predict` in `packages/pricing-core/src/pricing_core/rating/runtime.py` (at `origin/sl-8074-wk1178-fd8070-column-collision-2026-10-16`, head `2654a7445b0889e933d6556e53416d12d3576ecb`, SL-1761 / FD-1753) raises `MODEL_CALL_FEATURE_COLLISION` when `column in row and row[column] != value` (`:826-831`). Two `float('nan')` values compare unequal, so two inputs that map to one column and both carry NaN raise the collision although the values are equal. The refusal is loud and names the column (`terms=(column,)`, `:834`), so no wrong price results; the case is untested.

## Evidence

LG-1762's `## Audit` (same branch, `docs/ledgers/LG-01762-…-slice-ledger.md:72`), finding **A2 (LOW, observation)**: "`predict` compares `row[column] != value`; two equal `NaN` floats on one column compare unequal and would raise `MODEL_CALL_FEATURE_COLLISION`. Not constructed or …". Re-read by this author at the branch head: the comparison is at `runtime.py:826`, the raise at `:829-835`. Not run: reasoned from the code and the audit's observation. `main` (`cf509df89dbebff329bb6b319bcc9bcd2a2c2352`) does not hold this check; it lands with SL-1761.

## Disposition

Fix with an owner: WK-1178, a follow-up to SL-1761: compare NaN-aware (both values NaN counts as equal), with a test of two NaN inputs on one column that does not raise and a NaN against a number that does. The event that next discharges it: the merge of that fix.

***Resolved 2026-11-05*** — closed in place 2026-11-05 by the auditor, as the closing act of the mint of SL-2020 (WK-1178, LG-2021, PL-2019; ~~this PR, its number and squash written at the merge's date-of-record~~ #1436), on the lead's adoption of the SL-2020 audit and the maintainer's ruling "2026-11-05 10:41:08 GMT". Delivered remedy: `_same_value(a, b)` in `pricing_core/rating/runtime.py` (`bool(a == b or (a != a and b != b))`), used by `_GlmScorer.predict`'s collision check, so two NaN for one column are the ordinary shared-column case and a NaN against a number is still `MODEL_CALL_FEATURE_COLLISION`. Red first, by cause, at `68cb58df`: `assert 'MODEL_CALL_FEATURE_COLLISION' != 'MODEL_CALL_FEATURE_COLLISION'` (LG-2021; re-derived by the auditor with base source under the head's test); the two existing collision tests pass unedited (0 deleted lines in the test file). **Not closed by this: `Decimal('NaN')` through `predict`.** The slice asserts `_same_value` on `Decimal` NaN, not the scorer, because its fixture's banding raises `pyo3_runtime.PanicException` on a `Decimal('NaN')` (the executor's reading, not reproduced by the auditor): a separate score-time defect, carried to R2 or a new finding at the lead's choice. Gate evidence is in LG-2021.
