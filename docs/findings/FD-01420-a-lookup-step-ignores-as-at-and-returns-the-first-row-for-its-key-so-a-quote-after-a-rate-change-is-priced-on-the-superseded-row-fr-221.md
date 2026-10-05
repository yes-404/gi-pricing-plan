---
id: FD-1420
family: finding
title: A lookup step ignores as_at and returns the first row for its key, so a quote after a rate change is priced on the superseded row (FR-221)
status: active
created: 2026-10-05            # original date 2026-10-05, set at the draft; minted 2026-10-05
owner: auditor
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
corrected_by: []
relates: [WK-673, FR-221, FR-71, FD-1374]
---

# FD-1420 — `to_wire` translates a `lookup` step to an exact key match; `as_at` is never read

**Filed** by auditor-gaps on the lead's order of 2026-10-05, from the exit-demo draft's gap row B3. Minted as FD-1420
(reserved in the lead's `eta.md`). `tree:` is `origin/main` at filing, and the reproduction ran at that tree.

## Finding

**Severity HIGH (the maintainer's (by delegation), 2026-10-05 13:11:05 BST, final unless an upstream filter covers every scoring path; none found, see §3). Owner WK-673; deadline before the P2 exit demo.** A lookup over
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

### 3. No upstream filter on any scoring path (read, not run)

The out-of-force rows are not removed before the decision is built, on any of the three paths. All three evaluate
one decision built once per bundle by `load_bundle` (`runtime.py:666`: `to_wire(bundle.graph, bundle.resolved_payloads)`,
the only `to_wire` call in `backend/src` and `packages/*/src`), and a bundle is content-addressed, so it cannot
hold a per-quote date.

- The rows come from the resolver: `_Resolver.resolve`, `reference_table` branch (`backend/src/app/platform/rating_versions.py:515-523`),
  calls `reference_service.rows_as_at(..., as_at=None, limit=_ALL_REFERENCE_ROWS)`. With `as_at=None` that function
  does not filter (`reference.py:478-517`: the half-open window applies only `if as_at is not None`), so the bundle
  carries every row of every window.
- `POST /score`: `score_one` (`api/score.py:375`) → `bundle.decision.async_evaluate` (`score.py`, `score_one`).
  Not covered.
- `POST /score/compare`: two `score_one` calls (`api/score.py:447`). Not covered.
- `POST /score/batch`: `_score_one_ref` → `score_batch` (`worker/scoring_handlers.py:231`) →
  `_score_batch_row` → `bundle.decision.evaluate` (`score.py:1070`). Not covered.

Covered paths: none. Not covered: all three. The quote's `effective_date` reaches the engine as a context key
(`score.py:911`) and `as_at` names it, and nothing reads the pair.

### 4. Exposure in the seed and golden quotes

`grep -rn -i -E "effective_from|effective_to" examples/` prints nothing (rc 1). The freMTPL2 seed names one reference
table, `fr-region`, only as a column's `reference_table` annotation (`examples/fremtpl2/seed.py:195`, the sole file
naming it); it seeds no rows. Its rating version pins none: `examples/fremtpl2/model.py:323` has
`"reference_tables": []`. The golden-quote and ladder tests (`test_rating_ladder_control.py`, `baseline_ladder.py`,
`test_replay.py`, `test_rating_score.py`) hold zero `effective_from` (`grep -c`, 0 each). The only lookup rows in the
tests with an `effective_from` are one row per key (`test_rating_runtime.py`, `test_rating_pin_membership.py:74,276`).
So the seed and every golden quote are unaffected today. The defect is latent in the shipped examples and live for any
Reference Table Version holding successive rows for one key. Local-database exposure was not measured.

## Disposition

Fix before close with an owner: the lookup translation selects by key and window, or the step type refuses a table
holding overlapping or successive rows for one key until it does. ZEN refuses `>` on strings (the docstring's
verified `vmError`), so the window test needs the date as a numeric ordinal or a pre-filter by `as_at` before the
decision is built. That is a design choice for `docs/open-questions.md`, not this record's. Red first: the
reproduction above as a test, with the control that a single-row key still resolves.

Open. Filed by the auditor, 2026-10-05. Severity HIGH, owner WK-673 and the deadline (before the P2 exit demo) are the maintainer's (by delegation), 2026-10-05 13:11:05 BST (confirmed 13:20:26 BST); the fix is PL 9688 (working id).
