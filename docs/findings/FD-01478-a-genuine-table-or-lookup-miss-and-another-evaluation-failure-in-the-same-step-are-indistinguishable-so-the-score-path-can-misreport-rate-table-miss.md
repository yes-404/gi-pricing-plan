---
id: FD-1478
family: finding
title: A genuine table or lookup miss and another evaluation failure in the same step are indistinguishable, so the score path can misreport RATE_TABLE_MISS
status: active
created: 2026-10-08            # original date 2026-09-30, set at the draft; minted 2026-10-08
owner: auditor
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
corrected_by: []
relates: [WK-1178]
---

# FD-1478 — A genuine table or lookup miss and another evaluation failure in the same step are indistinguishable, so the score path can misreport RATE_TABLE_MISS

*Disclosure: drafted under working id 9888; minted as FD-1478 on 2026-10-08, in the T1 batch mint PR.*

## Finding

**Severity: low.** When `async_evaluate()` fails, `_reraise_engine_failure`
(`packages/pricing-core/src/pricing_core/rating/score.py:503`, found by symbol at `origin/main` `0ee8f414`) cannot tell **why**. The engine
reports a genuine `on_miss='error'` table or lookup miss and any other failure in the same step
(for example a null division) as the **same** `NodeError` shape, so the function infers the cause.
**This record is the residual only.** #968 (FD working id 9885) and #970 (RL working id 9982) are
fixing the broader case, in which the function names a table or lookup miss for a failure at a
step that consumes no such output whenever the algorithm has any `on_miss='error'` step: after
#970's DP-G4 fix the every-step scan is removed (RL-1313 DP-G4; landed as RL-1313 in mint batch #994, `fa9a73c2`; #968-#970 closed unmerged). What remains is the case where the
failing step **itself directly consumes an `on_miss='error'` output**: a genuine miss and another
evaluation failure in that step are indistinguishable, and the failure is **reported as a miss**
(`RATE_TABLE_MISS` or `REFERENCE_LOOKUP_MISS`). The docstring says so itself (the paragraph headed "The stated limit", `score.py:519-`): *"A failing step that itself directly consumes such an output, and fails for another reason,
still reports the miss code: the engine's error has the same shape in both cases."* The residual is pinned by
`test_the_stated_residual_still_reports_the_miss_code` (`packages/pricing-core/tests/test_rating_score.py:832`).

**Impact: a misdiagnosis, never a silent price.** Both paths raise a typed error and no quote is
returned. An operator sees a rate-table problem that did not happen.

## Evidence

Measured at `origin/main` `9f63d0feee524815e7e0c68c99a53ac3f80e6c37`, on the repository's own
score fixture (`packages/pricing-core/tests/test_rating_score.py`: `_algorithm_payload`,
`_FakeResolver`, `_version`, `_ctx`), repo `.venv`, `PYTHONPATH` at this tree. A spy wrapped
`_reraise_engine_failure` to print the engine failure it receives, then called the original.

| Case | Engine failure seen by `_reraise_engine_failure` | Raised by `score_one` |
|---|---|---|
| 1. Genuine table miss: `channel` `unseeded`, which the fixture refuses with `INPUT_CONTRACT_VIOLATION` as it stands; **this measurement widened the channel enum's domain** (as `test_a_rate_table_miss_is_refused_with_the_right_code` does) so the value reaches the table, which has no row for it | `RuntimeError :: {"type":"NodeError","source":"Failed to evaluate expression: \"risk_premium_minor * expense_factor\"","nodeId":"s_office"}` | `CodedError :: RATE_TABLE_MISS: the engine failed evaluating a downstream step, most likely because an on_miss='error' step found no matching row …` |
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

**Cause, by code reading (historical: the scan is gone at main).** The removed `:484-497` block set `has_table_miss` and `has_lookup_miss` by scanning
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

**Fix path:** the wire-level change named in the `_reraise_engine_failure` docstring (`score.py:504-525`), making the wire
translation itself fail gracefully so the failing step and its cause are known, not inferred.
Event that discharges it: that change merges, proven on this table: case 2 must not raise
`RATE_TABLE_MISS`, and case 1 must still raise it.

*Drafted under working id 9888.*

Amended 2026-10-05 before mint: line cites re-pointed by symbol to `origin/main` `47d770e8` (`_reraise_engine_failure` at `score.py:481`); the every-step scan the old `:469-498` / `:484-497` cites named was removed by RL-1313 DP-G4 (landed as RL-1313 in mint batch #994, `fa9a73c2`; #968-#970 closed unmerged), leaving only the residual above, which `test_the_stated_residual_still_reports_the_miss_code` pins. `PL-1314` cites this finding by working id (its lines 105, 336, 487) and is re-pointed at mint per its own line 487.

Re-anchored 2026-10-05 at main `caa4e411`: the residual still reproduces by code reading.
`_reraise_engine_failure` is at `score.py:481`, "The stated limit" paragraph at `:497`, and its
step lookup picks the miss code from `consumed & produces` only (`:504-525`), so a failing step
that directly consumes an `on_miss='error'` output and fails for another reason still reports
the miss code. `test_the_stated_residual_still_reports_the_miss_code` is at
`test_rating_score.py:832`. `score.py`'s last change on main is `1dd5e264` (#1045), after
`47d770e8`'s read of this tree, and does not touch that function. `RL-1313` DP-G4 is present at
main (`docs/rulings/RL-01313-…`, "DP-G4 — (a)+(i), with a stated limit"); `PL-1314` still cites
this finding by working id 9888 (its lines 105, 336, 487).

Re-anchored 2026-10-08 at main `0ee8f414`, at the mint: `score.py` last changed at `b6dd96fd` (SL-1427, #1219), which moved the function. By symbol, `_reraise_engine_failure` is at `score.py:503` (docstring `:504-525`, "The stated limit" paragraph at `:519`), and its step lookup picks the miss code from `consumed & produces` only (`:526-547`); the residual still reproduces by code reading, and `test_the_stated_residual_still_reports_the_miss_code` is still at `test_rating_score.py:832`. The lines 18, 27 and 79 above carry these re-pointed cites; the 2026-10-05 notes above keep the cites they were written with.
