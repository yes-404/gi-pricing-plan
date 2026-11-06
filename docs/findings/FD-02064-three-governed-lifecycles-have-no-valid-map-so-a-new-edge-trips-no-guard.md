---
id: FD-2064
family: finding
title: three governed lifecycles have no VALID_ map, so a new edge trips no guard
status: active
created: 2026-11-06   # original date 2026-11-06, set at the draft; working id 8399, minted 2026-11-06
owner: auditor
tree: 8f3553e224b6bd393a40cd27088a0c28677c99f9   # the slice branch before the merge of origin/main
corrected_by: []
relates: [WK-1178, SL-2060, LG-2061, FD-2034, FR-7]
---

# FD-2064 — three governed lifecycles have no VALID_ map, so a new edge trips no guard

*(Minted 2026-11-06 as FD-2064 from working id 8399, born open, in the PR of SL-2060. Severity LOW; ruled an FD, not a process row, to-lead "2026-11-06 02:44:00 GMT".)*

## Finding

Raised by aud-sl8377, 2026-11-06; ruled an FD, not a process row, to-lead "2026-11-06 02:44:00 GMT": it can let a wrong merge through (CLAUDE.md §13).

## Evidence

`backend/tests/test_audit_transitions.py`'s guard reads the eight `VALID_*TRANSITIONS` maps (predicate: `git grep '^VALID_[A-Z_]*TRANSITIONS\b'`) and fails if a map edge has no row. No such map exists for Validation Rule, Reference Table Version or Deployment Request edges; their rows are hand-listed. A new edge in one of those three lifecycles therefore trips no guard, and its missing Audit Event (FR-7, FR-368) would pass the suite.

Nothing wrong is live: the hand-listed rows cover every edge those lifecycles have today, by aud-sl8377's read at 684efcc0.

## Disposition

no fix before freeze. Carried to the P2 closure record's list with FD-2034's C1 to C6, unless a map lands by itself. Filed at SL-2060's mint.
