---
id: FD-1330
family: finding
title: The premium ladder attributes a clamp's effect to the office_premium rung, not to the constraints rung
status: active
created: 2026-09-30
owner: auditor
tree: 25ca36df89b0ac6e97a14cb08ca2b07f54fef085
corrected_by: []
relates: [WK-674]
---

# FD-1330 — The premium ladder attributes a clamp's effect to the office_premium rung, not to the constraints rung

## Finding

**Severity: medium**, a transparency mislabel on a governed artifact. When a `clamp` constraint
binds (a minimum premium above the office premium, say), the **Premium Ladder** shows the clamp's
whole effect on the **`office_premium` rung**, as a large `multiply` factor, and shows the
**`constraints` rung** as `operation.kind: "none"` with only the reason code listed in `applied`.
`FR-247` (`docs/specs/03-rating-engine.md:154`) puts *"± constraints (min premium, capping)"* on the
`constraints` rung, and the spec's worked ladder (`03:436-444`) shows that rung as
`{"kind": "none", "applied": []}` for **no clamp**, which implies a fired clamp is recorded there. The
ladder is the audit trail a reviewer reads, so a clamped quote's ladder says the office premium
was built by a factor of 3.8314 when the real factor is 1.1000 and the clamp did the rest.

It was surfaced by dm-eh-s3 while ruling DP-S3-5 (RL-1329, drafted as working id 9963; local head `48621365` in
the decision-maker's scratch tree, not in the repository), and routed by the maintainer's entry
`to-lead.md` "2026-09-30 16:16:06 BST — DP-S3-5 ruled (RL 9963, local 48621365): accepted in
substance pending auditor-plans; routing of the 4 observed items", item (3): *"the clamp's effect
attributed to the office_premium rung, not constraints: a new FD, MEDIUM (a transparency mislabel
on a governed artifact), owner WK-674 S3 (the same builder rewrite, fixed once)"*.

## Evidence

Reproduced at `origin/main` `25ca36df89b0ac6e97a14cb08ca2b07f54fef085` on the repository's own score
fixture (`packages/pricing-core/tests/test_rating_score.py`: `_compiled`, `_ctx`), repo `.venv`,
`PYTHONPATH=packages/pricing-core/src:packages/model-schema/src`, run as `python3 repro.py` from
the repository root. The fixture's clamp is `s_minprem` (`condition: office_premium_minor >=
min_premium_minor`, `on_violation: clamp`, `clamp_bounds: {"min": "min_premium_minor"}`,
`reason_code: MIN_PREMIUM_APPLIED`), so the input `min_premium_minor` decides whether it binds:

```python
import asyncio
import json
import sys

sys.path.insert(0, "packages/pricing-core/tests")
import test_rating_score as t


async def run(label, **inputs):
    compiled = await t._compiled()
    base = {"driver_age": 34, "channel": "direct", "min_premium_minor": 0,
            "sanity_cap_minor": 999_999_999, "sanity_floor_minor": 0}
    base.update(inputs)
    r = await t.score_one(compiled, t._ctx(inputs=base))
    d = r.model_dump(mode="json")
    print(f"== {label}: inputs {inputs}")
    for rung in d.get("ladder") or d.get("premium_ladder") or []:
        print("   rung", rung["rung"], "value_minor", rung["value_minor"],
              "operation", json.dumps(rung.get("operation")))


async def main():
    await run("no clamp binds", min_premium_minor=0)
    await run("clamp binds (floor 5000 > office 1436)", min_premium_minor=5000)


asyncio.run(main())
```

Output (operation fields trimmed to the ones set):

| Rung | No clamp (`min_premium_minor` 0) | **Clamp binds (`min_premium_minor` 5000)** |
|---|---|---|
| `risk_premium` | 1305 | 1305 |
| `office_premium` | 1436, `multiply` factor **1.1000** | **5000**, `multiply` factor **3.8314** |
| `constraints` | 1436, `none`, `applied: []` | **5000, `none`, `applied: ["MIN_PREMIUM_APPLIED"]`** |
| `instalment_loading` | 1507, `multiply` factor 1.0496 | 5250, `multiply` factor 1.0500 |
| `payable_premium` | 1507, `round` | 5250, `round` |

**Which rung's value changes:** with the clamp binding, the `office_premium` rung reads **5000**
(the clamped value) where the unclamped office premium is **1436**, and its recorded operation is
a `multiply` by **3.8314**, the ratio 5000/1305, not the loading's 1.1000. The `constraints` rung
carries **5000 forward** with **`kind: "none"`**: the step from 1436 to 5000 is recorded on no
rung of its own.

**Cause, by code reading.** `_build_ladder` (`packages/pricing-core/src/pricing_core/rating/score.py:551-`)
reads each rung's raw value from the evaluated result under the output step's `consumes` name
(`source_key`, `:589-592`), and the fixture's constraint step `produces` the **same name**
(`office_premium_minor`), so the engine's final value for that name is already the clamped one
(`runtime._constraint_node` overrides "in place", keyed to the same name so `passThrough`
overrides the pre-clamp value, `runtime.py:275-279`). The `office_premium` rung is then derived
from that overridden value. The `constraints` rung is **synthesised** (`score.py:562-572`): `value_minor=prev_minor`,
`operation=LadderOperation(kind="none", applied=list(clamp_reason_codes))`, so it can only carry the
previous rung's value forward. The module docstring says so (`score.py:84-88`): *"It carries forward
whatever the immediately preceding present rung settled on (a clamp already overrode that rung's
own value in place ...)"*. The behaviour is by design of the current builder; the design puts the
clamp on the wrong rung.

**Not measured:** a `max` clamp (a cap), two clamps at once, a fixture where the constraint step
does not follow the office rung, and any algorithm other than the score fixture. The reconciliation
of the ladder (each rung's value reproduces from the previous by its recorded operation) still
holds in the clamped case above; the defect is the attribution, not the arithmetic.

## Disposition

**Deferred with an owner: WK-674 Slice 3**, the same builder rewrite as DP-S3-5's (RL-1329, drafted as
working id 9963), fixed once, per the maintainer's entry cited above. Event that discharges it: Slice 3's merge.

**Acceptance, red first** (each written to fail on `origin/main` first): **a clamped quote's ladder
attributes the clamp to its constraint rung.** On the reproduction above: the `office_premium` rung
stays **1436** with `multiply` factor **1.1000** (as in the unclamped case), and the `constraints`
rung goes **1436 to 5000** with an operation that **records the clamp** (not `kind: "none"`), with
`MIN_PREMIUM_APPLIED` in `applied`; the downstream rungs and the payable stay as they are (5250).
The unclamped case is unchanged. Slice 3's own stop condition stands: it stops if any golden payable
moves.

*Disclosure: this record was drafted under working id 9967 and minted as FD-1330; the working id survives only in this line and in PR #1000's history.*
