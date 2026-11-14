---
id: FD-2117
family: finding
title: No test plants a fractional `_minor` value, so audit-docs check 12 has never been seen red on the money rule; delivered but untested
status: active
created: 2026-11-13
owner: auditor
tree: 2ba0d0d53142
corrected_by: []
relates: [CR-2110, WK-2114]
---

# FD-2117 — Check 12 of `audit-docs.py` has never printed a failure on a planted fraction

*Working id 8435, allocated by lead 34 (`from-lead` 2026-11-13); minted as FD-2117 in this batch. Raised by the maintainer's condition (2), `to-lead` "2026-11-13 19:56:23 GMT", when closing the register row of `FR-23` (F14).*

## Finding

The register row `FR-23` (F14) asked for "a test naming FR-23". It is closed as fixed: `tests/test_repository_invariants.py:139-155` (`@pytest.mark.req("FR-23")`, `test_money_discipline_is_enforced_by_the_docs_audit`) asserts `"_minor"` and `"FR-23"` appear in `scripts/audit-docs.py` and that the audit passes (rc 0). The check itself is `scripts/audit-docs.py:4055-4063`, a regex of the form `"(\w*_minor)"\s*:\s*(-?\d+\.\d+)`.

**The limit.** No test plants a fractional `_minor` value and sees check 12 fail (`git grep -n -i '_minor.*fraction' -- tests` at `2ba0d0d53142` finds only a docstring). The regex also sees only the quoted-key JSON form with a decimal point. A money-discipline check that has never printed a failure on a planted fraction has not been tested (`CLAUDE.md` §13: enforcement is proven on deliberately broken input). This is the verdict **delivered but untested** for that limb of `FR-23`, not a note on a closed row.

**Severity: LOW** (the maintainer's condition (2)). The value rule is held by the types (`MoneyMinor`, `DecimalStr`), per the test's own docstring; this check is a second line.

## Evidence

`tests/test_repository_invariants.py:139-155` and `scripts/audit-docs.py:4055-4063`, read at tree `2ba0d0d53142`; `git grep -n -i '_minor.*fraction' -- tests` prints a docstring only. Not run: no test, per the batch's docs-only scope.

## Disposition

Register decision: **delivered but untested: WK-2114** (P3-D). Owed: a red-first test that plants a fractional value in a `_minor` field in a scratch spec and a contract and sees check 12 report it, and a second planted shape for any form the regex cannot see.
