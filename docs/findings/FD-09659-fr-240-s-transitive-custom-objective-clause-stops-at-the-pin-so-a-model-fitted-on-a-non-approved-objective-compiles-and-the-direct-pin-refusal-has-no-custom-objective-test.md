---
id: FD-9659
family: finding
title: FR-240's transitive custom-objective clause stops at the pin, so a model fitted on a non-approved objective compiles, and the direct-pin refusal has no custom-objective test
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
corrected_by: []
relates: [WK-1178, FR-240, FR-20, FR-163, FD-9697]
---

# FD-9659 — FR-240's custom-objective clause: the pin is checked, the model's own objective is not

**Filed** by auditor-batch1 on the lead's order of 2026-10-05, split out of FD 9697 (limbs 2 and 3 of that record as
first drafted by auditor-gaps, from the exit-demo draft's gap row C3). Working id 9659, reserved by the lead.
`tree:` is `origin/main` at filing; every reproduction below ran at that tree.

## Finding

**Proposed severity MEDIUM (limb 3 sets it; limb 2 alone would be LOW); the deputy rules at the mint. Proposed owner WK-1178 (provisional).**

FR-240 (`docs/specs/03-rating-engine.md:137`): bundle compilation validates "… no `control`-intent factor in a
rateable path (`02` FR-88), no unapproved custom objective transitively reachable." This record is the second half.
The first half is FD 9697.

1. **Direct pin: implemented, untested for a custom objective.** `compile_bundle`'s `all_refs` loop
   (`packages/pricing-core/src/pricing_core/rating/compile.py:618-631`) includes `version.pins.custom_objectives` and
   raises `PIN_NOT_APPROVED` for one that is not approved or better. `custom_objective` is not in
   `_MATURITY_CHECK_EXEMPT` (`compile.py:431`: `rate_table`, `rating_algorithm`), so the refusal fires; the control
   run in the reproduction below shows it. The only custom-objective compile test is
   `test_a_version_pinning_an_approved_custom_objective_compiles`
   (`backend/tests/test_rating_version_compile.py:536`, the approved case;
   `grep -n 'def test.*custom_objective' backend/tests/test_rating_version_compile.py` lists that one). The same loop is
   tested for a model pin (`packages/pricing-core/tests/test_rating_compile_bundle.py:170`) and an unapproved
   model in the backend (`test_rating_version_compile.py:532`), so the mechanism has coverage and the custom-objective
   arm has none. Deleting `*version.pins.custom_objectives` from `all_refs` would pass the suite. This limb is a test gap.
2. **"Transitively reachable": not implemented.** Only the pins are read. A model pin's payload carries its own fit
   spec, and a GBM spec's `objective` may be `kind: custom` with a `ref` (`packages/model-schema/src/model_schema/modelling.py:1239-1271`,
   `GbmFunctionRef`; `:1361` `objective: GbmFunctionRef`). Nothing in `compile_bundle` follows that ref. A fit may use
   an objective that is `certified`, `review` or `approved` (`FITTABLE_OBJECTIVE_STATUSES`,
   `packages/model-schema/src/model_schema/objectives.py:179`; enforced at `backend/src/app/platform/model_specs.py:361`),
   so a model fitted on a not-yet-approved objective can exist, and a version pinning it compiles. This limb is a
   functional gap: the word "transitively" is the spec's, and the code stops at the pin.

## Evidence

### 1. Reproduction of limb 2, at `caa4e411a9c07a389cf47092a923c7761b2b92dc`, through pricing-core with no database

A scratch script, not committed, run from the repository root with the `packages/pricing-core/tests` fixtures
(`_version`, `_resolver`). The pinned model's payload names a custom objective by ref; the objective's status is
`review`; it is **not** in `pins.custom_objectives`. The control pins the same objective directly.

```python
import asyncio
import sys

sys.path.insert(0, "packages/pricing-core/tests")
import test_rating_compile_bundle as C
from pricing_core.rating.compile import compile_bundle

OBJ = "custom_objective:asym-loss@1"
res = C._resolver()
res._payloads["model:motor-ad-frequency@7"]["spec"] = {
    "model_type": "gbm", "objective": {"kind": "custom", "ref": OBJ}}
res._payloads[OBJ] = {"slug": "asym-loss", "version": 1}
res._statuses[OBJ] = "review"          # not approved

b = asyncio.run(compile_bundle(C._version(), res))
print("TRANSITIVE, unapproved, not pinned -> COMPILE ACCEPTED:", b.content_hash)

d = C._version().model_dump(mode="json")
d["pins"]["custom_objectives"] = [OBJ]
v = type(C._version()).model_validate(d)
try:
    asyncio.run(compile_bundle(v, res))
except ValueError as e:
    print("CONTROL, same objective pinned directly -> refused:", e)
```

Output (`.venv/bin/python`, 2026-10-05):

```
TRANSITIVE, unapproved, not pinned -> COMPILE ACCEPTED: sha256:a41bf21924281a0da969e7f17ec9bad5b1e4a8d218e7c4f3f456243c0f9bb66a
CONTROL, same objective pinned directly -> refused: PIN_NOT_APPROVED: custom_objective:asym-loss@1 is 'review', not approved or better (FR-20)
```

The same objective is refused when pinned and accepted when reached through the model: the transitive path is open.

### 2. What this does not show

The payload is a unit-test construction: the `spec` block is placed by hand in the fixture's model payload, and the
objective is never resolved because `compile_bundle` never looks. It does not show a real model reaching `approved`
with a `review` objective: `fit_gbm` and the validator allow the fit (see above), and a read of
`backend/src/app/platform/approvals.py` found no check of a model's objective on model approval (read, not run).
That end-to-end path was not run. Which artifact the spec means by "transitively" (the model's own objective, or
also a peril structure's) is for the spec, not this record. No database exposure was measured.

## Disposition

Open. Filed by the auditor, 2026-10-05; severity and owner are proposals, and the verdict is the lead's.

Remedy for the lead's verdict: say in FR-240 what "transitively" reaches; have the resolver or compile read each pinned
model's objective ref and refuse one that is not approved or better; give the unapproved custom-objective pin its
negative test. Red first for each: the reproduction above must end in a refusal, and the direct-pin test must fail if
`custom_objectives` leaves `all_refs`.
