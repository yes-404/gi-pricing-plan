---
id: FD-1842
family: finding
title: The grammar refusal's structure walk raises RecursionError on a deeply nested loss, so the create path answers 500
status: closed
created: 2026-10-22
owner: auditor
tree: 96354f9cddf968aabbc817570c2b0b3f6ea55a5a
corrected_by: []
relates: [WK-690, SL-1994, LG-1995, PL-1996]
---

# FD-1842 — The grammar refusal's structure walk raises RecursionError on a deeply nested loss, so the create path answers 500

## Finding

**MEDIUM; owner WK-690; Lean P2 product-FD allowance** (a product defect, not a process one). Filed on the
maintainer's (by delegation) entry "2026-10-22 11:48:11 BST" (`to-lead.md`), (a), on the re-audit `RS-1845` N1
(`aud-1275b-2026-10-22` @51f1c261). Filed under working id 8153; to be minted as FD 1842 in its own docs PR after SL-1711 merges (the maintainer's entry "2026-10-22 13:17:52 BST", (a)), not on SL-1275's branch.
Not fixed in SL-1275 (the entry: "Do NOT widen SL-1275 to fix it").

`FR-145`'s grammar check recurses once per nesting level of the loss. A loss of 2000 characters
(the length `RS-1845` used; the stored `CustomObjective.loss` is capped at 2000, `model_schema/objectives.py` :619; the
create body `CreateCustomObjective.loss` at `app/api/custom_objectives.py` :107 carries no cap of its own) that is a unary chain, for example `"-" * 1999 + "f"`, nests about
2000 deep; the walk exceeds Python's recursion limit and raises `RecursionError`. `grammar_refusal` catches
`ExpressionError` and `SyntaxError` only, so the error leaves `_require_the_grammar` and `POST /custom-objectives`
answers 500 instead of 422 `OBJECTIVE_GRAMMAR_VIOLATION` (or the `FR-145` bound's 422 `VALIDATION_FAILED`).

## Evidence

At `sl-1275-wk690-s5-authoring-view` 96354f9c (tree 530c3e1d), read by this record's author:

- `backend/src/app/platform/objectives.py` :308, `grammar_refusal` calls
  `parse_expression(loss, GrammarProfile.OBJECTIVE, symbols=symbols)`; its handlers are `except ExpressionError`
  (:309) and `except SyntaxError` (:315). No `RecursionError` handler. `_require_the_grammar` (:321) calls it
  (:327), and `create_objective` calls `_require_the_grammar` at :240.
- `packages/pricing-core/src/pricing_core/data/expressions.py` :298-303, `parse_expression` runs `_check`
  (:299), then `_check_structure` (:300), and `_check_limits` last (:303). `_check_structure` (:213-261)
  calls itself on every child expression (:238, :253, :255, :259), so its depth is the loss's depth, and it
  runs **before** the node and depth limits are checked. `measure_expression` (:134), which counts iteratively,
  is not on that path.
- `RS-1845` N1 (the re-audit of the delta against RS-1844, unminted
  at `aud-1275b-2026-10-22` @51f1c261): in-process, `grammar_refusal` raised `RecursionError` on a 2000-character
  unary chain and on `"f+" * 999 + "f"`. That observation is the auditor's; this record's author read the code
  above and did **not** re-run it.
- The preview route no longer reaches it: `custom_objectives.py` :337 calls `objective_preview.refuse_over_bound`
  (defined at `platform/objective_preview.py` :57) before `preview`, and `refuse_over_bound` measures iteratively,
  so an over-bound loss is 422 before `grammar_refusal` runs. The same 2000-character unary chain is 2000 nodes,
  over `FR-145`'s limit.

**Established by reading, not reproduced.** Not measured here: the 500 on `POST /custom-objectives` is derived from the code and the auditor's in-process
raise; no HTTP test was run for this record.

## Disposition

`deferred with an owner: WK-690`. The remedy is not made here. Two shapes fit, and the choice is the fixing
slice's: (1) `create_objective` calls the same iterative bound check the preview route uses
(`refuse_over_bound`'s `measure_expression` test) before `_require_the_grammar`, so an over-bound loss is 422
`VALIDATION_FAILED` on both paths; or (2) `_check_structure` is made iterative. The fix **starts red-first**: a test that first reproduces the 500 (a create request with a
2000-character unary chain), then asserts 422. The register row names the event that next discharges it.

***Resolved 2026-11-04*** — closed in place 2026-11-04 by the executor, as the closing act of the mint of SL-1994 (WK-690, LG-1995, PL-1996; this PR, its number and squash written at the merge's date-of-record), on the lead's brief under the GO "2026-11-03 16:13:51 GMT" (`to-lead.md`, a local channel file), option (ii): SL-1994 is FD-1842 alone. Delivered remedy: a depth bound before the structure walk. `parse_expression` (`pricing_core/data/expressions.py`) now runs `_check_limits`, the iterative FR-145 bound (depth 20, 200 nodes), before the recursive `_check_structure`, so one change covers both callers: a deep or over-bound expression is a 422 and never a 500 `RecursionError` (create answers `OBJECTIVE_GRAMMAR_VIOLATION`; the factor caller answers `VALIDATION_FAILED` on `expression`); `modelling.py` is unchanged. Red first, by the 3 real reds in LG-1995: the create route answered 500 `INTERNAL_ERROR` on a 2000-character unary chain, and the objectives and factor callers each raised `RecursionError` on a deep loss, at base `84e9ad34`; `02-modelling.md` carries a dated clarification of FR-145 / §4.6. Gate evidence is in LG-1995: the SOLO gate at `8a913212` (pytest "13 failed, 7041 passed, 22 skipped" = the 13 item-31 docs-audit failures only; frontend all rc 0, vitest 905 of 905; demo designed stop 1718 s, dislocation #1 555 s), accepted under item 31 by "2026-11-04 05:13:46 GMT". FD-1751 is not closed by this slice: PL-1996 struck limb 1 ("FD-1751 is guarded at main"; the expression-Factor diagnostic itself carried to P3, owner WK-1178).
