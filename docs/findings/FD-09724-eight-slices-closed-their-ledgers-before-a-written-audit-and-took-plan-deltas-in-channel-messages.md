---
id: FD-9724
family: finding
title: Eight slices closed their ledgers before a written audit, and several plan deltas exist only in ledgers and channel messages
status: active
created: 2026-10-11
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
corrected_by: []
relates: [RS-9703, SL-1257, SL-1541, SL-1529, SL-1631, SL-1390, SL-1559, SL-1600, SL-1557]
---

# FD-9724 — closing before audit; plan deltas without a durable plan record

Filed by the retro audit RS-9703 (limbs X1 and X3).

## Evidence

- X1. In each of LG-1634, LG-1608, LG-1623, LG-1632, LG-1633, LG-1635, LG-1609 and LG-1606 at its merge sha, `status:` is `closed` while `### Audit` reads "Not yet" or is empty (LG-1632 has no section) and `MERGE-ACK` reads "not yet given". `document-ids.md` §1.6 (SL and LG rows, amended 2026-10-04) makes the auditor's CLEAN verdict the authority for those closing acts when the brief orders the audit before the mint; here the audit followed the merge.
- X3. Plan deltas taken on channel rulings and recorded only in a ledger build log: SL-1529 delta D1 (4 exempt slugs, PL-1528 says 5); SL-1559 "04:19:42" and "04:23:36"; SL-1600 "23:03:19" and "23:53:00"; SL-1541 "23:46:57". PL files are frozen at first merge and the channel file is local.

## Finding

**Severity MEDIUM (proposed by the auditor):** the closed state of an `LG-`/`SL-` asserts an audit that did not exist at the time, and a reader of the plan alone gets acceptance numbers the code does not match. Nothing was found wrong in the code by RS-9703, which is why this is not higher.

## Disposition

**Owner: lead (process).** Decision: the lead chooses between (i) ledgers stay `active` until the audit is written and (ii) the audit is written before the merge; and whether a ledger quote of the ruling is enough durable record for a delta. Event that next confirms or discharges it: that rule stated in `delivery-process.md` or a ruling. Filed by the auditor, 2026-10-11; the lead gives the verdict.
