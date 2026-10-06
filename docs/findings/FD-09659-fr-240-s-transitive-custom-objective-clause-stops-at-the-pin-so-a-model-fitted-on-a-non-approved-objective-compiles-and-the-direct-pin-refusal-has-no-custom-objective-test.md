---
id: FD-9659
family: finding
title: FR-240's transitive custom-objective clause stops at the pin, so a model fitted on a non-approved objective compiles, and the direct-pin refusal has no custom-objective test
status: active
created: 2026-10-05            # working id; the mint date will replace this (check 31)
owner: auditor
tree: caa4e411a9c07a389cf47092a923c7761b2b92dc
corrected_by: []
relates: [WK-1178, FR-240, FR-20, FR-163]
---

# FD-9659 — FR-240's custom-objective clause: the pin is checked, the model's own objective is not

**Filed** by auditor-batch1 on the lead's order of 2026-10-05, split out of FD 9697 (limbs 2 and 3 of that record as
first drafted by auditor-gaps, from the exit-demo draft's gap row C3). Working id 9659, reserved by the lead.
`tree:` is `origin/main` at filing; every reproduction below ran at that tree.

## Finding

**Severity HIGH; owner WK-673; deadline: before the P2 exit demo** (the maintainer's (by delegation) rule of 2026-10-05 13:38:03 BST, "Finding batch 1: FD 9697's owner = WK-673; FD 9659's limb-3 severity depends on one fact": approval does not refuse an unapproved objective, measured below, so a priced bundle can rest on an objective that never passed review). **By limb:** the test gap (item 1 below; the maintainer's (by delegation) "limb 2") is LOW, WK-673; the transitive clause (item 2 below; the maintainer's (by delegation) "limb 3") is HIGH, WK-673. **The record's severity is the higher limb's.** **Ruled** in the maintainer's (by delegation) entry "2026-10-05 14:12:13 BST — FD 9659: HIGH confirmed, owner WK-673, before the exit demo; first in batch 2; ONE fix plan for the FR-240 family" (`channel/to-lead.md`, local): **HIGH, owner WK-673, deadline before the P2 exit demo**; of the two caveats (the review status set by SQL; the service layer, not HTTP) it says they "belong in the record as written. They do not lower it, because the gap is the missing check, which no route supplies." The record mints first in batch 2, and one fix plan covers the FR-240 family (this record and FD 9697): (a) model approval refuses a model whose custom objective is not approved, (b) `compile_bundle` checks the transitive reach, red first on each.

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
   spec, and a GBM spec's `objective` may be `kind: custom` with a `ref` (`packages/model-schema/src/model_schema/modelling.py:1238-1272`,
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
`backend/src/app/platform/approvals.py` found no check of a model's objective on model approval (read; section 3 measured it).
The end-to-end path was run afterwards: section 3. Which artifact the spec means by "transitively" (the model's own objective, or
also a peril structure's) is for the spec, not this record. No database exposure was measured.

### 3. Measured: a Model is approved while its custom objective is not approved

Run at worktree `HEAD` `14e26c95e676648b38c5f745782a7f8ed82f5595` (this branch, `fd-9659`; its tree differs from the
`caa4e411` of section 1 only by docs), 2026-10-05 13:09:02 to 13:09:15 UTC (14:09 BST), on a per-worktree test database,
with SL-1409's gate finished (`gate-1` and `gate-2` free, no `pytest` running). One scratch test file, not committed
and deleted after the run; no full suite. It reused the fixtures of `backend/tests/test_expression_objective_fit.py`
(`_expression_objective(..., approve=False)`, `_fit`), `test_glm_approximation_model.py::_transparency_job` and
`test_model_lifecycle.py::_principal_with`:

1. an `expression` custom objective is created and certified through the real Job, then set to `review` by a direct
   `UPDATE custom_objectives SET status='review'` (the fixture leaves it `certified`; the test needs `review`), and its status is read back;
2. a GBM model is fitted on it through the real `model.fit` Job (`_fit`), then given its transparency artifact through
   the real `model.transparency` Job, because submission refuses a non-GLM model without one (first attempt, same sha:
   `SUBMIT REFUSED EVIDENCE_INCOMPLETE`, FR-211, which is that rule, not an objective rule);
3. `modelling.submit_for_review` as a `pricing_actuary`; then `approvals.decide(APPROVE)` and
   `modelling.apply_approval_decision` as a different principal with the `approver` role (service layer, not HTTP).

Output, verbatim (`uv run pytest -q -s`, the test's `print` lines):

```
OBJECTIVE_STATUS review
SUBMIT ok
APPROVAL ok
MODEL_STATUS approved
OBJECTIVE_STATUS_AFTER review
1 passed, 1 warning in 5.29s
```

**The fact: a Model CAN be approved while a custom objective it uses is NOT approved.** Submission was accepted and
approval was not refused; the model row reads `approved`. `OBJECTIVE_STATUS_AFTER` re-prints the status read in
step 1, not a second read, so the line shows nothing about the objective after the approval. What the run does show
is that no code on the submit or approve path refused with the objective in `review` at step 1. This agrees with the
read: `apply_approval_decision` (`backend/src/app/platform/modelling.py:1284`) refuses only `ARTIFACT_FLAGGED`
(FR-205), and `_require_evidence` checks policy evidence and the transparency artifact, with no objective status.
The comment at `objectives.py:175-178` says the resulting model "simply cannot be approved until the objective is";
the run shows nothing enforces that. A bypass needs no later status change.

## Disposition

Open. Filed by the auditor, 2026-10-05; severity and owner are the maintainer's (by delegation), ruled in the 2026-10-05 14:12:13 BST entry named above on the 13:38:03 BST rule and the measurement in section 3, and the verdict is the lead's.

Remedy for the lead's verdict: say in FR-240 what "transitively" reaches; have the resolver or compile read each pinned
model's objective ref and refuse one that is not approved or better; give the unapproved custom-objective pin its
negative test. Add to that: refuse at model approval too, or state in `02` that approval is not the gate. Red first for each: the reproduction above must end in a refusal, and the direct-pin test must fail if
`custom_objectives` leaves `all_refs`.
