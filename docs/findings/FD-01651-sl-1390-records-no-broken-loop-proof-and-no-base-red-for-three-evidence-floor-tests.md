---
id: FD-1651
family: finding
title: SL-1390 records no broken-loop proof and no base red for three evidence-floor tests
status: closed
created: 2026-10-12
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
corrected_by: []
relates: [WK-673, SL-1390, PL-1499, LG-1633, RS-1649, FR-364, SL-1997, LG-1998, PL-1984]
---

# FD-1651 — unrecorded red-first evidence on SL-1390

*(Minted 2026-10-12 as FD-1651 from working id 9712, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Filed by the retro audit RS-1649. Reads are at the squash-merge `3065770c` (PR #1279).

## Evidence

- PL-1499 Acceptance 4 requires `test_a_policy_naming_an_unverifiable_kind_is_refused_by_name` "shown red on a deliberately broken loop that skips unknown kinds (scratch-reverted)", and the preamble requires every test red before its code, quoted by cause.
- LG-1633 at the merge sha: the scratch-reverted broken-loop runs (skip unknown kinds; `rate_table_diffs` mapped as met) are "OWED" in the Task 2 entry and described as planned in the slot-script entry; the 2026-10-11 gate-1 classification entry covers Acceptance 1, 2 and 7 only. No quoted outcome exists for Acceptance 3, 4 or 10 against the base source, or for either broken-loop run.
- The tests exist (`backend/tests/test_rating_version_evidence_floor.py`: `test_a_policy_above_the_floor_adds_a_verifiable_kind`, `test_a_policy_naming_an_unverifiable_kind_is_refused_by_name`, `test_a_policy_naming_rate_table_diffs_is_refused_naming_the_kind`); CI on the PR head concluded `success` (pytest 5522 passed).

## Finding

**Severity MEDIUM (proposed by the auditor):** the fail-closed behaviour of the evidence floor is the point of the slice, and the record cannot show that its tests fail when the loop is broken. Verdict candidate: delivered but untested.

## Disposition

**Owner: WK-673.** Decision: `fix before close with an owner: WK-673` — run the three tests against the two scratch-broken loops and the base `rating_versions.py`, quote the failing lines in a dated record; SL 9965 touches the same verifier map and may carry it. Event that next confirms or discharges it: that record. Filed by the auditor, 2026-10-11; the lead gives the verdict.

## Discharge path

Required by the maintainer's condition, `to-lead.md` "2026-10-11 20:17:38 BST" item 4: "each retro FD names its DISCHARGE PATH and date, not only an owner, so \"delivered-but-untested\" is closed by a TEST that runs, before the P2 close".

Re-run on main the two broken-loop proofs (the loop skipping unknown kinds; `rate_table_diffs` mapped as met), each scratch-reverted, plus the three tests against the base `rating_versions.py`; quote the failing lines in this FD's resolution (LG-1633 is frozen). Date, accepted by the lead: the first free gate-2/small-test window, no later than Fri 2026-10-23, and in every case before the P2 exit demo, Thu 2026-11-12.

***Resolved 2026-11-04*** — closed in place 2026-11-04 by the executor, as the closing act of the mint of SL-1997 (WK-673, LG-1998, PL-1984; this PR, its number and squash written at the merge's date-of-record), on the lead's brief under the GO "2026-11-03 16:28:44 GMT" (`to-lead.md`, a local channel file), row 2 of PL-1984 (S-b). Discharge: the two broken-loop proofs, re-run on main, scratch-reverted, outputs quoted in LG-1998. With the baseline `test_rating_version_evidence_floor.py` at 10 passed: scratch A (`verify is None` becomes `continue`) fails `test_a_policy_naming_an_unverifiable_kind_is_refused_by_name` (`Failed: DID NOT RAISE PlatformError`, 1 failed 9 passed), and scratch B (the `rate_table_diffs` verifier returns `{}`) fails `test_a_policy_naming_rate_table_diffs_is_refused_naming_the_kind` (the same message, 1 failed 9 passed). No source change: the tests catch both broken loops. Gate evidence is in LG-1998: the SOLO gate at `07e62951` (pytest "13 failed, 7047 passed, 22 skipped, 5 xfailed" = the 13 item-31 docs-audit failures only; frontend all rc 0, vitest 919 of 919; demo designed stop 1587 s, dislocation #1 592 s), from-lead "2026-11-04 07:38:28 GMT", accepted under item 31 by to-lead "2026-11-04 07:39:25 GMT".
