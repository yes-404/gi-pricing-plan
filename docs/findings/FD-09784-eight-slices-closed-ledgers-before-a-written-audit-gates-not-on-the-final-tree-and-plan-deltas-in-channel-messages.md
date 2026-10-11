---
id: FD-9784
family: finding
title: Eight slices closed ledgers before a written audit, several gates ran on an older tree or left no ledger record, and plan deltas were taken in channel messages
status: active
created: 2026-10-11
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
corrected_by: []
relates: [RS-9703, SL-1257, SL-1541, SL-1529, SL-1631, SL-1390, SL-1559, SL-1600, SL-1557]
---

# FD-9784 — closing before audit, gates off the final tree, deltas without a plan record

Filed by the retro audit RS-9703. Three limbs, one process cause.

## Evidence

- **(i) Closed before audit, 8/8.** In LG-1634, LG-1608, LG-1623, LG-1632, LG-1633, LG-1635, LG-1609 and LG-1606 at their merge shas, `status:` is `closed` while `### Audit` reads "Not yet" or is empty (LG-1632 has no section) and `MERGE-ACK` reads "not yet given". `document-ids.md` §1.6 (SL and LG rows, amended 2026-10-04) makes the auditor's CLEAN verdict the authority for those closing acts when the brief orders the audit before the mint; here the audit followed the merge.
- **(ii) Gate not on the final tree, or no ledger record.** SL-1541 A12 (ruff E501 fixed after the gate); SL-1529 A10 (five ruff errors fixed, "not re-gated"); SL-1390 (LG-1633 `### Gate` empty); SL-1559 (`### Gate` "Not run." above a real record; frontend fix `58864465` not re-gated); SL-1600 (gate at 8f674476, main `99f22479` merged after, conflicts in `rating.py`); SL-1557 (`### Gate` "Not run."; frontend half of the run not recorded). What does exist is CI at each merged PR head, read by the lead with `gh run list --commit <head>` (from-lead 2026-10-11 20:14:10 BST), all workflows green: #1271 26b78e49, #1272 559ed54a, #1273 71d578ae, #1276 eea1adac, #1278 4726e440, #1279 64fe7eda, #1280 418f78e6, #1281 024208de. The audit also read the `python` logs: 5562, 5469, 5497, 5507, 5512, 5522, 5604 passed for seven PRs, #1271's log empty.
- **(iii) Plan deltas in channel messages.** SL-1529 delta D1 (4 exempt slugs, PL-1528 says 5); SL-1559 "04:19:42" and "04:23:36"; SL-1600 "23:03:19" and "23:53:00"; SL-1541 "23:46:57". They sit in ledger build logs; PL files are frozen at first merge and the channel file is local.

## Finding

**Severity MEDIUM (proposed by the auditor):** a closed status asserted an audit that did not exist, ledgers do not show what was gated, and a reader of a plan alone gets numbers the code does not match. CI green at the PR heads limits the harm; no code defect was found.

## Disposition

**Owner: process backlog (Lean P2 item 5).** Decision: the lead chooses whether ledgers stay `active` until the audit is written, and whether a ledger quote of the ruling is enough durable record for a plan delta. Event that next confirms or discharges it: that rule stated in `delivery-process.md` or a ruling. Filed by the auditor, 2026-10-11; the lead gives the verdict.
