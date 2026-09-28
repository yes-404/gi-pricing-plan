---
id: FD-1174
family: finding
title: register-lint.py never built RFC-896 P3's owner-existence and id-uniqueness rules
status: active
created: 2026-09-28
owner: auditor
tree: df8e5811a151a99c7317690faf9278a6dc3400be
corrected_by: []
relates: [RFC-896, CR-1173]
---

# FD-1174 — register-lint.py never built RFC-896 P3's owner-existence and id-uniqueness rules

Filed by the auditor on 2026-09-28 in WK-694's closure record (`CR-1173`), on the lead's
ruling of that day. Read at `df8e5811`.

## Finding

RFC-896 §2 P3 specifies five checks for `scripts/register-lint.py`:

1. every Decision parses to a P1 shape;
2. every unowned row names its decay event (P2);
3. every *resolved* annotation carries a date and a PR or SHA;
4. every named owner is a roadmap row that exists, a dated ruling record, or a named event;
5. every finding id is unique.

RFC-896 §8 acceptance item (b) requires the linter to be red on three deliberately broken
inputs: *"an unparseable decision, a dateless resolution, and a nonexistent owner"*.

Checks 1 to 3 were built. **Checks 4 and 5 were not**, and there is no fixture for the
third broken input of item (b). No ruling, register row or closure record says the scope
was narrowed. The linter's own docstring states "Three rules" as if the set were complete.

## Evidence

- `scripts/register-lint.py` module docstring, at `df8e5811`: *"Three rules, each an
  obligation the register's own header … states in prose"*. The three rules are the
  Decision-cell grammar, the resolution-annotation format and the unowned-row decay. No
  rule reads `docs/roadmap.md` or compares finding ids.
- `grep -n -i 'owner\|roadmap\|unique\|duplicate' scripts/register-lint.py` at `df8e5811`
  finds only the verdict string `deferred with an owner`, docstring prose and residue-class
  labels. It finds no owner lookup and no uniqueness test.
- `tests/test_register_lint.py` has red fixtures for the first two broken inputs:
  `test_a_decision_outside_the_grammar_is_refused` and
  `test_a_resolution_marker_with_no_date_or_reference_is_refused`. It has none for a
  nonexistent owner. `uv run pytest -q tests/test_register_lint.py tests/test_register_owed.py`
  at `df8e5811` gives 45 passed. The suite is green because it does not test the missing rules.
- The narrowing is recorded nowhere. I searched the five rulings on RFC-896's questions
  (`RL-909` to `RL-913`), the reconciliation `PL-900`, plan review 11 (`CR-932`) and
  `docs/findings/register.md` for an owner-existence or uniqueness disposition, and found none.

## Disposition

**Not started; deferred with an owner — the lead.** Event: the first slice of the
create-read-retire audit Work (WK-1170). This is the lead's ruling of 2026-09-28. WK-694's
close carries RFC-896 acceptance item (b) as this deferral. The slice either builds the two
rules and the third broken-input fixture, or records a dated decision not to.
