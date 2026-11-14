---
id: FD-1659
family: finding
title: A reference-lookup miss in a step that also consumes a rate table is reported as RATE_TABLE_MISS, because _reraise_engine_failure checks tables first
status: closed
created: 2026-10-12
owner: auditor
tree: fc4401dcad789692f79f6c3ffc058c1c3921b7b9
corrected_by: []
relates: [WK-1178, SL-1527, FD-1648, FR-255]
---

# FD-1659 — the wrong miss code when a step consumes both a table and a lookup

*(Minted 2026-10-12 as FD-1659 from working id 9802, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Found by SL-1527 (LG-1647): the journey asserts the current behaviour with a comment naming this defect. Filed from the maintainer's (by delegation) entry "2026-10-12 02:20:32 BST — SL-1527: (a) D7 option (i) two-group split ACCEPTED; (b) RATE_TABLE_MISS exact + FD MEDIUM, WK-1178, separate from FD 9702 ACCEPTED; your refusal of the step-split workaround ENDORSED" (`to-lead.md`, local), item (b). Every line below was re-read at `origin/main` `fc4401dcad789692f79f6c3ffc058c1c3921b7b9` on 2026-10-12 (LG-1647 quoted `:550`, `:560` and `:562`; the function is now at `:525`).

## Evidence

`packages/pricing-core/src/pricing_core/rating/score.py`, `_reraise_engine_failure` (`:525`):

- `:557`, `consumes_output_of(steps)` is true when the failing step's `consumes` intersects the `produces` of any `on_miss="error"` step in the list it is given.
- `:560-561`: `if consumes_output_of(tables): code = "RATE_TABLE_MISS"`; only `:562` (`elif consumes_output_of(lookups)`) names `REFERENCE_LOOKUP_MISS`.
- So a step that consumes the output of **both** an `on_miss="error"` table and an `on_miss="error"` lookup is reported as `RATE_TABLE_MISS` whichever of the two actually missed. The docstring above (`:526` to `:545`) states a related limit, a step that fails for another reason, but not this one.
- WF-699's demo algorithm has such a step: `s_premium` consumes both the ladder and a lookup (the lead's entry gives this as the reason ladder and lookup are not separable for the D7 split).

## Finding

**Severity MEDIUM (the maintainer's (by delegation), entry "2026-10-12 02:20:32 BST", item (b)).** LOUD, never a misprice: the quote is refused either way. But a misattributed refusal sends an operator to the wrong artifact (a rate table that is fine, not the reference table that missed). Separate from FD-1648, which is a different cause (a ZEN literal the engine cannot parse, reported under the same code); the two share `_reraise_engine_failure` and no fix.

## Disposition

**Owner: WK-1178.** The workaround, moving the loading into its own step, was refused: it routes around the defect (entry above, ENDORSED). Fix before close: report by what actually missed, not by which list is checked first (for a step consuming both, name the step's failing input, or both candidates). Event that next confirms or discharges it: a merged slice with a red-first test whose step consumes a table and a lookup and whose lookup misses, red on `fc4401dc` by the code `RATE_TABLE_MISS`. Filed by the executor from the entry, 2026-10-12.

***Resolved 2026-11-06*** — closed in place 2026-11-06 by the executor, as the closing act of the mint of SL-2038 (WK-1178, LG-2039, PL-2019; this PR; its number, squash commit and merge date are written at the merge's date-of-record), on the lead's adoption of the SL-2038 audit and the maintainer's entries "2026-11-05 10:11:39 GMT" and "2026-11-05 10:41:08 GMT". Delivered remedy: `_reraise_engine_failure(evaluation, context, exc)` (`pricing_core/rating/score.py`) no longer lists the `on_miss="error"` tables and lookups a failing step consumes. It re-runs the failed quote through `PurposeEvaluation.diagnose`, a lazily built decision (`pricing_core/rating/runtime.py`) that carries a guard node after each table or lookup, and the guard's own node id says what failed: `RATE_TABLE_MISS` or `REFERENCE_LOOKUP_MISS` by the type of the step that missed, for that step. The live wire carries no guard (DP-R1), so a quote that scores pays nothing. Red first, by cause, at base `662867bb` with the tests of `1359a77d` fixed by `5db73f7e`: `test_a_step_consuming_a_table_and_a_lookup_reports_the_one_that_missed[the_lookup_missed]` raised `RATE_TABLE_MISS` where `REFERENCE_LOOKUP_MISS` is expected (LG-2039 Build log); green at the head (`test_rating_score.py` 53 passed, the auditor's re-run at `369c43c7`), `[the_table_missed]` the control. The spec clause is `03` FR-255 (appended, `930e7bd4`). The WF-699 journey asserted the old code (`examples/fremtpl2/journey.py`, step B3, and `test_wf699_journey.py`'s comment); both follow the fix in the same PR (LG-2039 Audit, N1).
