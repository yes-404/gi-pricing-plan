---
id: RL-877
family: ruling
title: `MODEL_CALL_FAILED`
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slice1-rulings.md
---

## RL-877 — `MODEL_CALL_FAILED`

**The decision.** `FR-255` (`../specs/03-rating-engine.md:166`) names five per-quote
error categories: *"contract violation, reference miss, table miss, constraint decline,
model failure."* §5.1's owned-code block (`:527-540`) covers three
(`INPUT_CONTRACT_VIOLATION`, `REFERENCE_LOOKUP_MISS`, `RATE_TABLE_MISS`); constraint decline
is `FR-256`'s successful-response path and correctly has no code; **model failure has
none.** Recovery item 4 recommends declaring `MODEL_CALL_FAILED`, matching the existing
`_FAILED` suffix family, and says the decision-maker will *"rule this formally (as a spec
change appending to §5.1's owned-code list) once the plan reaches the slice."* The slice has
been reached.

**Ruled: confirmed. `MODEL_CALL_FAILED`,** appended to `03`'s owned-code block in this
commit, dated in the same style as the block's two existing `*(added …)*` annotations.
Re-verified at `7b8473a`: `git grep -n MODEL_CALL_FAILED` returns five hits, all in
`docs/plans/`, none in `docs/specs/` or `backend/` — so the code is unowned and check 10 of
`../../scripts/audit-docs.py` (cross-spec ownership exclusivity, `:574-598`) cannot
conflict on it. The alternative, reusing `BUNDLE_COMPILE_FAILED`, is refused for the reason
recovery item 4 gives: it names a compile-time failure and would blur the audit trail
between a bundle that would not build and a booster that would not answer.

**No `FR-` is appended.** `FR-255` already states the obligation ("model failure" is one
of its five categories); this names the code that discharges it. Error codes are a separate
namespace, and `../../backend/src/app/errors.py`'s own `PlatformError.__init__` names the
spec as the authority — *"Codes are enumerated in the owning spec's Interfaces section; add
it there before raising it"* (`errors.py:344-348`). Spec first is therefore the enforced
order, and this commit is that first half.

**For the executor, verified and not assumed.** Adding the code to the spec does not make it
raisable. `PlatformError` refuses any code outside `_KNOWN_CODES` (`errors.py:314-321`,
`:335-349`), and `RATING_ERROR_CODES` (`:275-307`) does not currently contain
`MODEL_CALL_FAILED` — nor, checked at the same tree, `INPUT_CONTRACT_VIOLATION`,
`REFERENCE_LOOKUP_MISS` or `LADDER_RECONCILIATION_FAILED`, all three of which §5.1 already
lists as owned and all three of which Task 1.4's error-typing work names. **Four codes, not
one**, must reach `RATING_ERROR_CODES` before anything raises them as a `PlatformError`.
Their absence today is a not-yet-built path rather than a defect — none has a caller — but
an executor reading Task 1.4 and expecting three of the four to already exist will find they
do not. Separately: inside `pricing-core`, which cannot import `app`, the established
convention is a code-named `ValueError` — `compile.py`'s `_raise_named` produces
`ValueError(f"{code}: {message}")` — so `score_one`'s own refusals follow that, and the
mapping to `PlatformError` happens at the backend boundary in Slice 2.

---

---
