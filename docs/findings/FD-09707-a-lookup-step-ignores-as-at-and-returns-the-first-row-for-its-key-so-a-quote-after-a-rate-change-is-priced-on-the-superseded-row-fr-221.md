---
id: FD-9707
family: finding
title: A lookup step ignores as_at and returns the first row for its key, so a quote after a rate change is priced on the superseded row (FR-221)
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
corrected_by: []
relates: [WK-1178, FR-221, FR-71, FD-1374]
---

# FD-9707 — `to_wire` translates a `lookup` step to an exact key match; `as_at` is never read

**Filed** by auditor-gaps on the lead's order of 2026-10-05, from the exit-demo draft's gap row B3. Working id 9707
(reserved in the lead's `eta.md`). `tree:` is `origin/main` at filing, and the reproduction ran at that tree.

## Finding

**Proposed severity HIGH; the deputy sets it at the mint. Proposed owner WK-1178 (provisional).** A lookup over
effective-dated rows returns the first row whose key matches, whatever the quote's `as_at`. When a key has more
than one row, a quote whose date falls in a later row's window is priced on an earlier row. That is a wrong rate
on a rated quote, not a missing feature.

FR-221 (`docs/specs/03-rating-engine.md:107`): "`lookup` steps evaluate reference data **as at a declared date** —
normally the policy effective date, never "now" (`01` FR-71). The date source is explicit in the step." It carries
no dated amendment. `RatingLookupStep.as_at` (`packages/model-schema/src/model_schema/rating.py:281`) is a required
field, so the date source is declared and then dropped.

The gap is known to the code and unknown to the register. `pricing_core/rating/runtime.py`'s module docstring
(lines 27-33) says: "A `lookup` step's `as_at` effective-dating window is translated as an **exact key match only**
… A lookup with more than one effective-dated row sharing a key returns whichever row's rule comes first, not the
one whose window contains the quote's `as_at` value." It adds "see the PR description for the recommended owner."
`docs/findings/register.md` has no row for it (`grep -n 'as_at\|FR-221' docs/findings/register.md` at this tree
finds only FD-1374's row, which names `as_at` as a sweep token).

## Evidence

### 1. The cause, read from the owning module

`_decision_table_node`, `lookup` branch (`runtime.py:246-253`), builds one decision-table rule per reference row,
with `i0` the row's `key` only, under `"hitPolicy": "first"`. `effective_from`, `effective_to` and the step's
`as_at` do not appear in it. `lookup_as_at` (`pricing_core/data/reference.py:27`) implements the correct half-open
rule `[effective_from, effective_to)`, and the rating runtime does not call it
(`grep -rln lookup_as_at packages/pricing-core/src backend/src` lists only `data/reference.py`, its own definition).

### 2. Reproduction, at `caa4e411a9c07a389cf47092a923c7761b2b92dc`, through pricing-core with no database

Two rows for key `SW1A`: `OLD` is in force until 2026-01-01 (exclusive), `NEW` from 2026-01-01. The step's `as_at`
is the declared input `effective_date`.

```python
import json, zen
from model_schema.rating import RatingAlgorithm
from pricing_core.rating.compile import to_jdm
from pricing_core.rating.runtime import to_wire
algo = RatingAlgorithm.model_validate({
 "slug":"lookup-only","version":1,
 "input_contract":[{"name":"postcode","type":"string","nullable":False},{"name":"effective_date","type":"string","nullable":False}],
 "outputs":[{"name":"rating_area","type":"string","required":True}],
 "steps":[
  {"step_id":"s_in","type":"input","label":"P","input_name":"postcode","on_missing":"error","produces":"postcode"},
  {"step_id":"s_area","type":"lookup","label":"A","reference_table_ref":"reference_table:ons@1","key_expr":["postcode"],"as_at":"effective_date","on_miss":"error","consumes":["postcode"],"produces":"area_code"},
  {"step_id":"s_out","type":"output","label":"O","output_name":"rating_area","rounding":{"mode":"half_even","dp":0},"consumes":["area_code"]}],
 "sub_graphs":[]})
rows=[{"key":"SW1A","payload":{"area_code":"OLD"},"effective_from":"2020-01-01","effective_to":"2026-01-01"},
      {"key":"SW1A","payload":{"area_code":"NEW"},"effective_from":"2026-01-01","effective_to":None}]
wire=to_wire(to_jdm(algo),{"reference_table:ons@1":{"rows":rows}})
d=zen.ZenEngine().create_decision(json.dumps(wire))
for dt in ("2025-06-01","2026-06-01"):
    print(dt, d.evaluate({"postcode":"SW1A","effective_date":dt})["result"]["area_code"])
```

Output (`uv run python`, 2026-10-05):

```
2025-06-01 OLD
2026-06-01 OLD
```

The first line is right. The second is wrong: `NEW` is in force on 2026-06-01. The same answer for both dates is the
defect. Not committed as a test; the scratch script is the record.

### 3. What this does not show

Whether a shipped Reference Table Version holds two rows for one key. The existing lookup test
(`test_rating_runtime.py::test_lookup_step_wire_translation_matches_by_key`) uses one row per key, so it passes.
Exposure in a local database was not measured. The platform's own reference-data rule (`ReferenceRow`, half-open
windows) allows such rows, so the case is the ordinary one for a rate change, not a corner.

## Disposition

Fix before close with an owner: the lookup translation selects by key and window, or the step type refuses a table
holding overlapping or successive rows for one key until it does. ZEN refuses `>` on strings (the docstring's
verified `vmError`), so the window test needs the date as a numeric ordinal or a pre-filter by `as_at` before the
decision is built. That is a design choice for `docs/open-questions.md`, not this record's. Red first: the
reproduction above as a test, with the control that a single-row key still resolves.

Open. Filed by the auditor, 2026-10-05; severity and owner are proposals, and the verdict is the lead's.
