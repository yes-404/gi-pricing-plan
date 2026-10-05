---
id: FD-1422
family: finding
title: compile_bundle accepts a rate table seeded from a control-intent factor, so FR-240's "no control-intent factor in a rateable path" has no implementation
status: active
created: 2026-10-05            # original date 2026-10-05, set at the draft; minted 2026-10-05
owner: auditor
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
corrected_by: []
relates: [WK-1178, FR-240, FR-88, FR-230, FR-20]
---

# FD-1422 — FR-240's "no `control`-intent factor in a rateable path" has no implementation

**Filed** by auditor-gaps on the lead's order of 2026-10-05, from the exit-demo draft's gap row C3. Minted as FD-1422
(reserved in the lead's `eta.md`). `tree:` is `origin/main` at filing, and the reproduction ran at that tree.

## Finding

**Severity HIGH (the maintainer's (by delegation), 2026-10-05 13:20:26 BST, decisions 22–27; final at the mint). Owner WK-673 (the maintainer's (by delegation) ruling, 2026-10-05 13:38:03 BST, "Finding batch 1: FD-1422's owner = WK-673; FD 9659's limb-3 severity depends on one fact": the fix is in `compile_bundle` against FR-240, which WK-673 owns); deadline: none set for this finding alone; the maintainer's (by delegation) 2026-10-05 14:12:13 BST ruling puts it in ONE fix plan for the FR-240 family (with FD 9659), owner WK-673, red first, "a HIGH G2 blocker" (PL 9649, working id).** FR-240 requires that bundle compilation validates "no `control`-intent
factor in a rateable path (`02` FR-88)", and `compile_bundle` does not. A rate table built from a `control` factor is
accepted and compiles, so a price can depend on a factor the platform declared must not price. That is a mispricing
class, not a test gap (the maintainer's (by delegation) reasoning, 13:20:26 BST).

FR-240 (`docs/specs/03-rating-engine.md:137`): bundle compilation validates "… no `control`-intent factor in a
rateable path (`02` FR-88), no unapproved custom objective transitively reachable." FR-88 (`02`): "Rating Versions
may only use `risk` factors; a `control` factor reaching a rate table is a validation error in `03`."

**Split, 2026-10-05.** This record first also held the untested unapproved-custom-objective limb and the "transitively
reachable" limb of the same FR-240 sentence. Neither is the control-intent defect: the direct-pin refusal works
(`PIN_NOT_APPROVED` fires), so what is missing there is a negative test and a ruling on "transitively". They moved, on
the maintainer's (by delegation) instruction of 2026-10-05 13:20:26 BST, to FD 9659 (LOW).

**`control` intent: no check anywhere on the path.** `compile_bundle`
(`packages/pricing-core/src/pricing_core/rating/compile.py:573-640`) resolves the algorithm and the rate-table,
model, reference-table and custom-objective pin and reads each one's status. It never resolves a Factor, and
`grep -n -i 'control\|intent' packages/pricing-core/src/pricing_core/rating/compile.py` finds nothing. The seed
path does not check it either: `seed_from_model` (`pricing_core/rate_tables/operations.py`, the Factor lookup
after `check_model_approved`) takes the bound Factor and never reads `intent`
(`grep -n intent packages/pricing-core/src/pricing_core/rate_tables/operations.py` finds nothing). So a table
built from a `control` factor is created `rateable=True` and compiles.

## Evidence

### 1. Reproduction, at `caa4e411a9c07a389cf47092a923c7761b2b92dc`, through pricing-core with no database

A scratch test, not committed, in `packages/pricing-core/tests/`. It makes a Factor with `intent=control`, seeds a rate
table from it, puts that table's payload behind the rate-table pin of the existing `test_rating_compile_bundle.py`
fixture (`_version`, `_resolver`), and compiles.

```python
import asyncio
from datetime import UTC, datetime
from model_schema.modelling import FactorIntent, ModelStatus
from pricing_core.rate_tables.operations import seed_from_model
from pricing_core.rating.compile import compile_bundle
import test_rate_table_operations as T
import test_rating_compile_bundle as C

ctl = T._factor("driver_age_band").model_copy(update={"intent": FactorIntent.CONTROL})
seeded = seed_from_model(T._glm_model(ModelStatus.APPROVED), factor="driver_age_band",
    factors=[ctl], table_slug="motor-expense", change_note="seed",
    seeded_at=datetime(2026, 10, 5, tzinfo=UTC))
print("SEED ACCEPTED: key factor_ref =", seeded.table.keys[0].factor_ref, "rateable =", seeded.table.rateable)
res = C._resolver()
res._payloads["rate_table:motor-expense@3"] = seeded.table.model_dump(mode="json")
bundle = asyncio.run(compile_bundle(C._version(), res))
print("COMPILE ACCEPTED:", bundle.content_hash)
```

Output (`uv run pytest`, the test ended in a deliberate `assert 0` so the prints show; 2026-10-05):

```
SEED ACCEPTED: key factor_ref = factor:driver_age_band@1 rateable = True
COMPILE ACCEPTED: sha256:a41bf21924281a0da969e7f17ec9bad5b1e4a8d218e7c4f3f456243c0f9bb66a
```

Where FR-240 says the compile "must" refuse, it returns a bundle.

### 2. What this does not show

The table is a unit-test construction. The compile fixture's algorithm reads the table through the
`rate_table:motor-expense@3` pin, so the path is the real one, but a Factor's intent is reachable from the table only
through `RateTableKey.factor_ref`, which `compile_bundle` never resolves. That is also why the fix is not a one-line
check: the resolver has to resolve the key's `factor_ref` and the compile has to read its `intent`. Whether
`POST /api/v1/factors` can create a `control` Factor today was not re-checked here. No database exposure was measured.

## Disposition

Open. Filed by the auditor, 2026-10-05. Severity HIGH (13:20:26 BST) and owner WK-673 (13:38:03 BST) are the maintainer's (by delegation); the fix is the FR-240 family plan, PL 9649 (working id).

Remedy for the lead's verdict: refuse a `control` factor at seed (it cannot be rated on, FR-88) or at compile, or both.
Red first: the reproduction above must end in a refusal. The custom-objective clauses are FD 9659's.
