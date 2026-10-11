---
id: FD-9724
family: finding
title: SL-1600's ACK states 28 fixed-text and 12 authored-text error types where PL-1599 states 30 and 10 with 74 changed; the delta is recorded in the ledger but the ACK omits the changed total and the reached-today list
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

- PL-1599 Acceptance 6: the ACK "lists every pydantic error type whose 422 rendering changes", re-derived by the stated predicate, "still **74**" (`value_error` plus 73 types), `_FIXED_TEXT_TYPES` meaning 30 types, 10 in `_AUTHORED_TEXT`, 63 on the DP-7 text; "It also states the ones a request body reaches today (Task 0 Step 4)."
- `packages/pricing-core/src/pricing_core/safe_error.py` at the merge sha `02f23b4a`: `_FIXED_TEXT_TYPES` has 28 members and `_AUTHORED_TEXT` has 12.
- LG-1609's MERGE-ACK block states 28 and 12; it does not state the changed-type total and has no "reached today" list.

## Reconciliation (run by the auditor, 2026-10-11, at `02f23b4a`)

Predicate: every member of `pydantic_core.core_schema.ErrorType` not in `_FIXED_TEXT_TYPES`, `_FIXED_TEXT_TYPES` and `_AUTHORED_TEXT` read by `ast` from the file at `02f23b4a` (`git show 02f23b4a:packages/pricing-core/src/pricing_core/safe_error.py`), run with the repository `.venv` Python (`-I`) through `run-small.sh`, script kept outside the repository. Printed: `pydantic_core 2.46.5 ErrorType 104 fixed 28 authored 12`; neither set names a type outside `ErrorType`; the sets do not overlap; 76 types are outside `_FIXED_TEXT_TYPES`, `value_error` among them, so 75 others; 12 of those 75 are authored and 63 take the DP-7 text.

| | PL-1599 | merged tree |
|---|---|---|
| `ErrorType` members | 104 | 104 |
| `_FIXED_TEXT_TYPES` (message kept) | 30 | 28 |
| types changed, plus `value_error` | 73 + 1 = 74 | 75 + 1 = 76 |
| authored text (`_AUTHORED_TEXT`) | 10 | 12 |
| DP-7 text | 63 | 63 |

The difference is two types, `date_from_datetime_parsing` and `datetime_from_date_parsing`, moved from fixed to authored. **LG-1609 records this** as a plan delta in its build log (the entry beginning "Plan delta (pydantic 2.13.5, probe by `TypeAdapter`/`create_model`)"): a FastAPI body is validated lax, so a bad date gives `date_from_datetime_parsing` and a bad date-time `datetime_from_date_parsing`, while `date_parsing` and `datetime_parsing` arise only from strict JSON; the lead ruled to keep the two strict types and add the two lax ones with their own authored text. The retro audit's first reading, "no recorded delta" (RS-9703 row and the first draft of this FD), was wrong and is corrected here.

## Finding

The 28/12 counts are reconciled to the plan: 30 − 2 = 28 fixed, 10 + 2 = 12 authored, 63 unchanged, total changed 74 + 2 = 76. What remains unrecorded is small: the ACK block does not state the changed-type total (76) and has no "reached today" list. The delta also lives in the ledger only (see FD-9784 limb iii).

**Severity LOW (proposed by the auditor).** Verdict candidate: accept, the reconciliation above being the resolution. No code change.

## Disposition

**Owner: WK-1178.** Decision: `accept` on the lead's verdict; this essay's Reconciliation is the test that ran. Discharge path (the maintainer's condition, `to-lead.md` "2026-10-11 20:17:38 BST" item 4): done in this record, 2026-10-11, by running the predicate at `02f23b4a`; the reached-today list, if wanted, is a one-line addition to SL-1601's plan. Filed by the auditor, 2026-10-11; the lead gives the verdict.
