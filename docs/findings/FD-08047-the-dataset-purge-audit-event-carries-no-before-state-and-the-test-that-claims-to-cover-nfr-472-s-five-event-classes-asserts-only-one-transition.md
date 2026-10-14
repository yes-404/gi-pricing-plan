---
id: FD-8047
family: finding
title: The dataset purge audit event carries no before state, and the test that claims to cover NFR-472's five event classes asserts only one transition
status: active
created: 2026-10-14
owner: auditor
tree: a3fc2e8dd384de6abf909f662f43011b8078fb4e
corrected_by: []
relates: [WK-1178, PL-8034, SL-8035, NFR-472, FR-7, FR-81, P2]
---

# FD-8047 — a purge audits no `before`, and the NFR-472 test is green by construction

*(Filed under working id 8047, reserved by the lead; a minter folds it into the docs batch.
Authority: the maintainer's (by delegation) entry "2026-10-14 12:07:40 BST" in
`channel/to-lead.md`, DP-6, verbatim: *"a finding: the purge audit lacks `before`
(datasets.py:1051-1055), and test_data_nfrs.py:147 claims coverage it does not assert (green by
construction, today's class). One FD, both limbs; NFR-472's red-first test covers the
replace_rule_set limb in SL 8035."* Every citation was read at `origin/main`
`a3fc2e8dd384de6abf909f662f43011b8078fb4e`.)*

## Finding

**Severity: MEDIUM, proposed by the auditor (to be ruled). Owner WK-1178.**

`docs/specs/01-data-management.md:1186`, NFR-472: *"Audit: dataset transitions,
acknowledgements, dictionary edits, rule-set changes, and purges each emit an Audit Event with
before/after state (FR-7)."* Two limbs.

### Limb 1 — the purge audit event has no `before`

`backend/src/app/platform/datasets.py:1046-1056` (`purge_subject`) calls `audit.record(...)` with
`action="dataset.subject_purged"`, `entity_ref=f"dataset:{dataset_id}@1"`,
`after={"subject_token": …, "versions_affected": len(versions)}` and `justification=reason`. It
passes no `before`. `backend/src/app/platform/audit.py:60` declares `before: dict[str, Any] | None
= None`, so the omission is silent: the event is written with `before` null and nothing fails. The
function already loads the affected versions (`:1027-1033`), so the pre-purge state is in hand at
the call. Other event classes do pass it: the status transition (`datasets.py:593`), the dictionary
edit (`:301`), the owner change (`:361`) and the warning acknowledgement
(`platform/validation.py:331`). Purge is the only class in NFR-472's list whose event is an erasure,
the case where a before state matters most. The `@1` in the `entity_ref` is a literal, not the
dataset's version; whether that is intended was not checked.

The adjacent limb of the same clause: `replace_rule_set` (`platform/validation_rules.py:894-909`)
also passes `after` only. NFR-472's red-first test in SL 8035 covers that limb; this finding does
not duplicate it, and a fix to one must not be reported as closing the other.

### Limb 2 — `test_data_nfrs.py:147` claims coverage it does not assert

`backend/tests/test_data_nfrs.py:147-180`: `@pytest.mark.req("NFR-472")` on
`test_every_dataset_transition_emits_an_audit_event_with_before_and_after`, whose docstring
(`:151`) says: *"NFR-472: transitions, acknowledgements, dictionary edits, rule-set changes and
purges each emit an Audit Event with before and after state."* The body creates a dataset and a
version, performs one transition (draft to validating), and asserts exactly this (`:178-180`):

```
assert len(events) == 1
assert events[0].before == {"status": "draft"}
assert events[0].after["status"] == "validating"
```

It exercises none of acknowledgements, dictionary edits, rule-set changes or purges. The marker
makes `scripts/req-coverage.py` count NFR-472 as covered, so the requirement reads as evidenced
while four of its five classes have no assertion. The test is green by construction for those
classes: it would stay green with Limb 1 present, as it does today.

## Why MEDIUM, proposed

- Against HIGH: the events are written, with `after`, `actor` and `justification`; what is missing
  is the prior state on one class, and the coverage claim on the rest. No wrong number or data loss.
- Against LOW: the missing `before` is on an erasure in an audit chain whose purpose is
  reconstruction, and the false coverage marker is the class (a passing check that cannot fail)
  that hid this limb.
- Re-rate trigger: HIGH if the SL 8035 red-first test finds a second event class with no `before`.

## Discharge

The event that next discharges it: the WK-1178 slice that passes `before` on the purge event and
adds a per-class assertion for acknowledgements, dictionary edits, rule-set changes and purges,
each red on the pre-fix tree. The rule-set assertion is SL 8035's.
