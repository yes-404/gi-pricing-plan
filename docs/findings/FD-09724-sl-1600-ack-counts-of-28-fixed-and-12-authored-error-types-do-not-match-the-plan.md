---
id: FD-9724
family: finding
title: SL-1600's ACK states 28 fixed-text and 12 authored-text error types where PL-1599 states 30 and 10 with 74 changed, and records no delta
status: active
created: 2026-10-11
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
corrected_by: []
relates: [WK-1178, SL-1600, PL-1599, LG-1609, RS-9703, NFR-499]
---

# FD-9724 — unreconciled DP-5 type counts

Filed by the retro audit RS-9703. Reads are at the squash-merge `02f23b4a` (PR #1273).

## Evidence

- PL-1599 Acceptance 6: the ACK "lists every pydantic error type whose 422 rendering changes", re-derived by the stated predicate, "still **74**", with `_FIXED_TEXT_TYPES` meaning 30 types and 10 in `_AUTHORED_TEXT`; "It also states the ones a request body reaches today (Task 0 Step 4)."
- `packages/pricing-core/src/pricing_core/safe_error.py` at the merge sha: `_FIXED_TEXT_TYPES` has 28 members and `_AUTHORED_TEXT` has 12 (counted with `ast` over the two assignments).
- LG-1609's MERGE-ACK block states 28 and 12; it does not state 74, does not say why 30/10 became 28/12 (the only recorded delta is 69 to 68 rewritten messages), and has no "reached today" list.

## Finding

**Severity LOW-MEDIUM (proposed by the auditor):** which pydantic types keep their message and which are replaced decides what a 422 can leak (NFR-499); the count the maintainer acked cannot be traced to the plan's. Verdict candidate: delivered but untested (the derivation predicate was not re-run in the record).

## Disposition

**Owner: WK-1178.** Decision: `fix before close with an owner: WK-1178` — re-run the plan's predicate at the current tree, record the 74-type derivation and the reason for 28/12, and add the reached-today list. Event that next confirms or discharges it: that record. Filed by the auditor, 2026-10-11; the lead gives the verdict.
