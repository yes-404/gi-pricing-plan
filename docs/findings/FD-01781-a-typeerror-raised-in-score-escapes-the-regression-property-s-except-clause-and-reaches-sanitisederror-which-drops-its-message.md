---
id: FD-1781
family: finding
title: A TypeError raised in score escapes the property runner's except clause and reaches SanitisedError, which drops its message
status: active
created: 2026-10-17
owner: auditor
tree: cf509df89dbebff329bb6b319bcc9bcd2a2c2352
corrected_by: []
relates: [WK-1178, SL-1543, WK-673]
---

# FD-1781 — A TypeError raised in score escapes the property runner's except clause and reaches SanitisedError, which drops its message

*(Minted 2026-10-17 as FD-1781 from working id 8087, in the D20 batch mint PR.)*

## Finding

**LOW; owner WK-1178; verdict proposed `deferred with an owner`** (the maintainer ruled it a LOW FD: "SL-1543 reds", `to-lead.md` about 14:31 BST on 2026-10-17, relayed by the lead's brief of 14:28:39 BST). `score` in `packages/pricing-core/src/pricing_core/rating/properties.py` (`:104-117` at `origin/main` `cf509df89dbebff329bb6b319bcc9bcd2a2c2352`) catches `NotImplementedError` (re-raised) and `(ValueError, RuntimeError)` (`:116`, cached as `None`). A `TypeError` from `_score_context_sync` is neither, so it propagates to the caller, and `SanitisedError` (`packages/pricing-core/src/pricing_core/safe_error.py:73`) carries no message, so the failure reads as a bare typed error with no cause.

## Evidence

`~/gi-pricing-plan.local/scratch/sl1543-diag.md`, "Red 1" (executor-1543diag, 2026-10-17 14:25 BST, SL-1543 head `9fe9a253`): a seeded rating algorithm with a first `decimal` input; `coerce_inputs` turns property-case strings into `Decimal`; the ZEN engine then fails with `TypeError: argument 'ctx': unsupported type Decimal` (pure repro, `ZenEngine().create_decision(...).evaluate({'x': Decimal('1.00')})`). The diagnosis cites the catch as `properties.py:112`; at `origin/main` `cf509df89dbebff329bb6b319bcc9bcd2a2c2352` the `except (ValueError, RuntimeError)` is at `:116`. The Decimal-to-engine conversion is a separate defect owned by SL-1543; this record covers only the uncaught `TypeError` and the lost message. Latent on `main`: no seeded algorithm has a `decimal` input there (the diagnosis's claim, not re-verified here). Read, not run.

## Disposition

Fix with an owner: WK-1178: decide, in a ruling or the fix slice's plan, what a `TypeError` in `score` means for the property runner (caught and reported as a property failure naming the exception type and message, or kept loud with the message preserved by `SanitisedError`); a test that raises `TypeError` from the engine and asserts the outcome. The event that next discharges it: the merge of that fix.
