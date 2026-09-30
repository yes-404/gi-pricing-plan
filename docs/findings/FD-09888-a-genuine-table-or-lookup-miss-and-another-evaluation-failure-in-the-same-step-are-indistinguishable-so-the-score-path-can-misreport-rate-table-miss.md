---
id: FD-9888
family: finding
title: A genuine table or lookup miss and another evaluation failure in the same step are indistinguishable, so the score path can misreport RATE_TABLE_MISS
status: active
created: 2026-09-30
owner: auditor
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
corrected_by: []
relates: [WK-1178]
---

# FD-9888 — A genuine table or lookup miss and another evaluation failure in the same step are indistinguishable, so the score path can misreport RATE_TABLE_MISS

## Finding

**Severity: low.** When `async_evaluate()` fails, `_reraise_engine_failure`
(`packages/pricing-core/src/pricing_core/rating/score.py:469-498`) cannot tell **why**. The engine
reports a genuine `on_miss='error'` table or lookup miss and any other failure in the same step
(for example a null division) as the **same** `NodeError` shape, so the function infers the cause.
It infers a table or lookup miss whenever the algorithm has *any* `on_miss='error'` table or lookup
step, and raises `RATE_TABLE_MISS` (or `REFERENCE_LOOKUP_MISS`). A failure that is not a miss is
therefore **reported as one**. The docstring says so itself (`:469-483`): *"it is honest about
being an inference: a correctness gap for a later slice to close by making the wire translation
itself fail gracefully"*.

**Impact: a misdiagnosis, never a silent price.** Both paths raise a typed error and no quote is
returned. An operator sees a rate-table problem that did not happen.

## Evidence

Measured at `origin/main` `9f63d0feee524815e7e0c68c99a53ac3f80e6c37`, on the repository's own
score fixture (`packages/pricing-core/tests/test_rating_score.py`: `_algorithm_payload`,
`_FakeResolver`, `_version`, `_ctx`), repo `.venv`, `PYTHONPATH` at this tree. A spy wrapped
`_reraise_engine_failure` to print the engine failure it receives, then called the original.

| Case | Engine failure seen by `_reraise_engine_failure` | Raised by `score_one` |
|---|---|---|
| 1. Genuine table miss: `channel` `unseeded` (accepted by the input contract, no row in the rate table) | `RuntimeError :: {"type":"NodeError","source":"Failed to evaluate expression: \"risk_premium_minor * expense_factor\"","nodeId":"s_office"}` | `CodedError :: RATE_TABLE_MISS: the engine failed evaluating a downstream step, most likely because an on_miss='error' step found no matching row …` |
| 2. Null division in the **same step** `s_office`: expr `expense_factor != 0 ? risk_premium_minor * expense_factor * (1 / (driver_age - driver_age)) : 0` | `RuntimeError :: {"type":"NodeError","source":"Failed to evaluate expression: \"expense_factor != 0 ? risk_premium_minor * expense_factor * (1 / (driver_age - driver_age)) : 0\"","nodeId":"s_office"}` | the same `RATE_TABLE_MISS` |

A third case, measured first, shows the broader form: with expr
`expense_factor != 0 ? risk_premium_minor * expense_factor / (driver_age - driver_age) : 0` the
null is produced in `s_office` and fails **downstream**, at the constraint step `s_clamp`
(`RuntimeError :: {"type":"NodeError","source":"Failed to evaluate expression:
\"!(office_premium_minor >= min_premium_minor)\"","nodeId":"s_clamp"}`), and `score_one` again
raises `RATE_TABLE_MISS`. That step consumes `office_premium_minor`, not an `on_miss='error'`
output, so this is the case #968's narrowed acceptance covers.

Cases 1 and 2 are each a `NodeError` at `nodeId` `s_office` whose `source` is *"Failed to evaluate
expression: …"*. The `source` differs only by the expression's own text, so nothing in the shape
says whether the cause was a missing row or a null. In case 2 the table step found its row; the
code names a rate-table miss regardless. The same shape was measured by #970's probe (RL working
id 9982), by the medium decision-maker, with a real `score_one` on the score fixture: a genuine
miss (table row removed) and a null-division failure in the same step give the same shape.

**Cause, by code reading.** `:484-497` set `has_table_miss` and `has_lookup_miss` by scanning
**every** step of the algorithm for `on_miss == "error"`, not by asking which step failed or what
it consumed. So the code is chosen from the algorithm's shape, not from the failure. This is
broader than the case the maintainer accepted below (a failing step that directly consumes an
`on_miss='error'` output): it also names a table miss for a failure at a step that consumes no such
output whenever any table step in the algorithm has `on_miss='error'`. #968's acceptance line is
about that broader case.

## Disposition

**Accepted as a residual and recorded here, owner WK-1178.** The maintainer's decision is
`to-lead.md` "2026-09-30 11:07:11 BST — DECISION: #970 DP-G4 residual → (a), recorded as a LOW FD;
#970 G1–G3 accepted": accept the residual because it is fail-closed either way (a wrong diagnosis,
never a silent price), and record it as a LOW FD with an owner, not a backlog note. #968's
"never RATE_TABLE_MISS" line is narrowed by a dated note to conditions and bounds whose step does
not directly consume an `on_miss='error'` output; this record is the residual that narrowing
leaves.

**Fix path:** the wire-level change named in `score.py:469-483`'s own docstring, making the wire
translation itself fail gracefully so the failing step and its cause are known, not inferred.
Event that discharges it: that change merges, proven on this table: case 2 must not raise
`RATE_TABLE_MISS`, and case 1 must still raise it.

*Drafted under working id 9888.*
