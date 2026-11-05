# Draft finding (for the auditor, not filed): the bulk rate-table operations round to the ambient 28 digits, and no spec clause says so

Written by exec-sl8345f on branch sl-8345-r2-cell-hard-error (e6d141ba + this slice's commits). Draft only: no id, no register row. Severity proposed: **LOW by policy (no stated rule), but reachable by a real table, so the lead decides.**

## Claim
`uplift_table`, `uplift_by_filter` and `rebase_to_level` (packages/pricing-core/src/pricing_core/rate_tables/operations.py) compute `old * factor` / `old / reference` in the **ambient** decimal context (28 significant digits; no `localcontext`, no `quantize`, no caller sets one). A result wider than 28 digits is rounded half-even **inside the arithmetic**, and the rounded text is stored as the cell. `_format_value` is not the cause (it now writes exactly; at ambient 28 old and new give identical rows). `floor_and_cap` does no arithmetic.

## Policy
`grep -n -i -E "(decimal places|\bdp\b|round|quantis|quantiz|precision|significant digits)" docs/specs/03-rating-engine.md | grep -i -E "uplift|floor_and_cap|floor/cap|rebase|bulk"`, and the same over 04-optimisation.md: no line. FR-233 (03-rating-engine.md line 126) states the four operations and that each records its parameters; nothing on dp or rounding. This is a missing rule, so none is proposed here (CLAUDE.md section 0: a design choice the specs leave open goes to open-questions.md with options).

## Evidence (scratch/sl8345f/measure_precision.py, ambient 28)
- Cell `1234567890123456789012345.6789` x 1.5 through `uplift_table` and `uplift_by_filter`: stored `1851851835185185183518518.518`, exact `1851851835185185183518518.51835`.
- Repeated x 1.0375 through the real `uplift_table`: the exact product gains 4 digits per step. From 0.1234, step 7 is the first at which the mantissa reaches 28 digits and the first at which stored != exact: stored `0.1596731515941606426239013672`, exact `0.15967315159416064262390136718750`. From 1.0: stored `1.293947743874883651733398438`, exact `1.29394774387488365173339843750`.
- From 0.0123, step 7 is refused: `RATE_TABLE_CELL_UNPARSEABLE: value '0.01591555724966106891632080078'` (29 decimal places; `cell_parses`, rating/compile.py:820, accepts up to 29 digits and 28 dp, measured).
- The result depends on the caller's ambient context: inside `localcontext(prec=400)` the same op stored the exact product.

## Reachability
Yes: a realistic cell uplifted by 3.75% seven times is rounded silently (the engine then prices the rounded text), and a cell below 0.1 is refused at the same step. One bulk operation on a cell already at 25+ digits does it in one step. Whether real tables carry such cells (fitted relativities with many digits, repeated annual uplifts) is the lead's to judge.

## Options (to price, not chosen)
A. State a rule (for example quantise each op result to N dp, half-even) in FR-233 first, then code it. B. State "exact or refuse": compute in a context sized to the operands and refuse an inexact result with a named code. C. Record the 28-digit ambient behaviour as the stated policy. Recommendation: A or B via open-questions.md; either changes stored bytes, so FR-239 hashing is touched for any table an op has already produced.
