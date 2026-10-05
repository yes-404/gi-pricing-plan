---
id: FD-9699
family: finding
title: MONETARY_FLOAT_REFUSED is registered and published and raised nowhere, so a float result type is refused as VALIDATION_FAILED (FR-227, FR-245)
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
corrected_by: []
relates: [WK-1178, FR-227, FR-245, FR-212]
---

# FD-9699 — the code `03` §5.1 publishes for a float is never produced

**Filed** by auditor-gaps on the lead's order of 2026-10-05, from the exit-demo draft's gap row B9. Working id 9699
(reserved in the lead's `eta.md`). `tree:` is `origin/main` at filing, and the reproduction ran at that tree.

## Finding

**Severity LOW, ruled by the maintainer (by delegation) in the entry headed *"2026-10-05 13:20:26 BST — DECISIONS 22–27; severity signals for the four gap findings"* (`to-lead.md`, a local channel file, so cited by its header): "as proposed". Owner: proposed: WK-1178 (provisional); ruled by the maintainer (by delegation) at the ACK.** The refusal
happens, which is why the severity is low: a float result type never reaches a rating version. What is wrong is the
code. `MONETARY_FLOAT_REFUSED` is in `RATING_ERROR_CODES` (`backend/src/app/errors.py:310`) and is listed among
`03`'s error codes (`docs/specs/03-rating-engine.md:929`), and nothing raises it. A client that handles the
published code never sees it.

FR-227 (`03:113`): "A monetary result must be `decimal` or `money_minor` (R2)." FR-245 (`03:147`): "Mixing a
monetary value and a float-typed value in one expression is a compile-time error." Neither dated amendment names the
code, and `03:929` is the only place that ties the code to a requirement.

**A second gap sits beside it and is not the same one.** FR-245's *expression* clause is a different refusal from
FR-227's *declared type* clause. The only float check found is the type check below, on a declared result type.
`grep -n -i float packages/pricing-core/src/pricing_core/rating/*.py` finds nothing in expression validation
(the hits are `compile.py:82-91`, an integer round-trip assert, `golden.py`, and `analysis.py`'s exposure column).
No test or reproduction here shows a money-times-float expression being accepted, so that clause is recorded as not
found, not as reproduced.

## Evidence

### 1. No raiser

`grep -rn MONETARY_FLOAT_REFUSED backend/src packages/*/src` at this tree prints one line, the registration at
`backend/src/app/errors.py:310`. The only other files naming it are `docs/specs/03-rating-engine.md` and
`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`. The float refusal that does exist is
`_reject_float_type` (`packages/model-schema/src/model_schema/rating.py:222-233`), which raises a plain `ValueError`.
`RATING_TYPE_MISMATCH`, registered on the line above, is raised (`pricing_core/rating/compile.py:146`); this one is
not.

### 2. Reproduction, at `caa4e411a9c07a389cf47092a923c7761b2b92dc`, at the route's own mapping seam, no database

`_parse_algorithm` calls `graph_validation_error` (`backend/src/app/platform/rating_algorithms.py:32`) on any
`ValidationError`; it maps `GraphCycleError` and `GraphUnresolvedRefError` to named codes and everything else to
`VALIDATION_FAILED`.

```python
from pydantic import ValidationError
from model_schema.rating import RatingAlgorithm
from app.platform.rating_algorithms import graph_validation_error
payload = {"slug":"float-out","version":1,
 "input_contract":[{"name":"x","type":"int","nullable":False}],
 "outputs":[{"name":"payable_premium_minor","type":"float","required":True}],
 "steps":[{"step_id":"s_in","type":"input","label":"X","input_name":"x","on_missing":"error","produces":"x"},
  {"step_id":"s_out","type":"output","label":"O","output_name":"payable_premium_minor","rounding":{"mode":"half_even","dp":0},"consumes":["x"]}],
 "sub_graphs":[]}
try:
    RatingAlgorithm.model_validate(payload)
except ValidationError as exc:
    e = graph_validation_error(exc, artifact="rating algorithm")
    print(vars(e))
```

Output (`uv run python`, 2026-10-05, `detail` cut at 300 characters):

```
{'code': 'VALIDATION_FAILED', 'title': 'Rating algorithm is invalid', 'status_code': 422, 'detail': "1 validation error for RatingAlgorithm\noutputs.0.type\n  Value error, a rating result type is never float (FR-227); a monetary result is decimal or money_minor (got 'float') [type=value_error, input_value='float', input_type=str]\n ...
```

The HTTP route was not run: the per-worktree test database does not exist here. The same mapping carries
`test_another_shape_refusal_is_validation_failed` (`backend/tests/test_rating_algorithms.py:251`), which pins
`VALIDATION_FAILED` for another shape refusal.

## Disposition

Open. Filed by the auditor, 2026-10-05; severity and owner are proposals, and the verdict is the lead's.

Two ways to close it, and choosing one is the spec's: raise the code (a typed signal like `GraphCycleError`, mapped in
`graph_validation_error`, with a red-first test), or remove it from `RATING_ERROR_CODES` and `03:929` and say
`VALIDATION_FAILED` is the answer. Doing neither leaves a published code no client can receive. The FR-245
expression clause needs its own check: a reproduction of a money-times-float expression is the first step.
