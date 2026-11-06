---
id: FD-1781
family: finding
title: A TypeError raised in score escapes the property runner's except clause and reaches SanitisedError, which drops its message
status: closed
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

***Resolved 2026-11-05*** — closed in place 2026-11-05 by the auditor, as the closing act of the mint of SL-2020 (WK-1178, LG-2021, PL-2019; ~~this PR, its number and squash written at the merge's date-of-record~~ #1436, squash `5e5c83f7d4a4`, merged 2026-11-05), on the lead's adoption of the SL-2020 audit and the maintainer's ruling "2026-11-05 10:41:08 GMT" (DP-R4 (a): status only). Delivered remedy: `make_scorer` in `pricing_core/rating/properties.py` catches `(ValueError, RuntimeError, TypeError)`; the docstring names the `TypeError` and cites the ruling; `NotImplementedError` still propagates. A `TypeError` from the evaluation makes the property `fail` and the run `overall="fail"` instead of an exception out of the Job. Red first at `68cb58df` (`TypeError: x` propagates, case property and monotone sweep; `scratch/sl-8322-r1/red-t10-t11.log`); green by `test_a_type_error_from_the_evaluation_is_a_failed_property_not_a_crash` (`test_testing.py`, `req("FR-261")`, both properties). The message is not carried (DP-R4 (b) declined): the finding's "no cause" half stays as ruled. Gate evidence is in LG-2021.
