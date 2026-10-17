---
id: FD-8086
family: finding
title: A model_call's feature-collision check compares with `!=`, so two equal NaN values on one column raise the collision
status: active
created: 2026-10-17
owner: auditor
tree: cf509df89dbebff329bb6b319bcc9bcd2a2c2352
corrected_by: []
relates: [WK-1178, SL-1761, FD-1753]
---

# FD-8086 — A model_call's feature-collision check compares with `!=`, so two equal NaN values on one column raise the collision

## Finding

**LOW; owner WK-1178; verdict proposed `deferred with an owner`** (the lead's brief, 2026-10-17 14:28:39 BST: SL-1761 audit A2 → a D20 FD). `predict` in `packages/pricing-core/src/pricing_core/rating/runtime.py` (at `origin/sl-8074-wk1178-fd8070-column-collision-2026-10-16`, head `2654a7445b0889e933d6556e53416d12d3576ecb`, SL-1761 / FD-1753) raises `MODEL_CALL_FEATURE_COLLISION` when `column in row and row[column] != value` (`:826-831`). Two `float('nan')` values compare unequal, so two inputs that map to one column and both carry NaN raise the collision although the values are equal. The refusal is loud and names the column (`terms=(column,)`, `:834`), so no wrong price results; the case is untested.

## Evidence

LG-1762's `## Audit` (same branch, `docs/ledgers/LG-01762-…-slice-ledger.md:72`), finding **A2 (LOW, observation)**: "`predict` compares `row[column] != value`; two equal `NaN` floats on one column compare unequal and would raise `MODEL_CALL_FEATURE_COLLISION`. Not constructed or …". Re-read by this author at the branch head: the comparison is at `runtime.py:826`, the raise at `:829-835`. Not run: reasoned from the code and the audit's observation. `main` (`cf509df89dbebff329bb6b319bcc9bcd2a2c2352`) does not hold this check; it lands with SL-1761.

## Disposition

Fix with an owner: WK-1178, a follow-up to SL-1761: compare NaN-aware (both values NaN counts as equal), with a test of two NaN inputs on one column that does not raise and a NaN against a number that does. The event that next discharges it: the merge of that fix.
