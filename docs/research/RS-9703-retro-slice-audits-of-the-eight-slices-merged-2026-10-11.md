---
id: RS-9703
family: research
kind: audit
title: Retro slice audits of the eight slices merged on 2026-10-11 without a written audit
status: draft
created: 2026-10-11
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1257, SL-1541, SL-1529, SL-1631, SL-1390, SL-1559, SL-1600, SL-1557, PL-1583, PL-1540, PL-1528, PL-1630, PL-1499, PL-1558, PL-1599, PL-1556, LG-1634, LG-1608, LG-1623, LG-1632, LG-1633, LG-1635, LG-1609, LG-1606]
---

# RS-9703 — Retro slice audits of the eight slices merged on 2026-10-11

## Question

Eight slices merged on 2026-10-11 with their `LG-` and `SL-` rows already `closed` and the
`### Audit` section of each ledger reading "Not yet" or empty. Does each merge tree satisfy
its plan's Acceptance Standard, and what does each ledger fail to evidence?

Authority: `to-lead.md` entry "2026-10-11 19:57:42 BST", item 3 (one auditor seat, G2/exit
slices first, each slice against its own plan at its own merge sha, one record, one row per
slice, every finding an `FD-` with an owner, a missing requirement reopens through an `FD-`
and never by editing a closed row). The family is `RS` `audit` (`document-ids.md` §1.6:
"auditor — a bespoke audit's method, evidence and verdicts; files every finding as `FD-`").

## Method

Scope was derived from each slice's plan first (its Acceptance Standard, write set and
closing acts), then evidenced at the slice's squash-merge commit on `origin/main`
(`git show <sha>:<path>`, `git diff <sha>^1 <sha>`, `git grep <pat> <sha> -- <path>`).
Evidence is read, not run: **no test, gate or build was run by this audit**; "MET" means
the named test or text exists at the merge sha and its assert was read where the row says
so, and a result quoted from an `LG-` is marked CARRIED-by-LG. **CI on each PR head was
read** with `gh pr view <n> --json statusCheckRollup` and `gh run view <id> --log`: the
`python` workflow concluded `success` on all eight PR heads, with a pytest summary of
`N passed` and no `failed` line for seven (#1280 5562, #1272 5469, #1276 5507, #1278 5512,
#1279 5522, #1281 5604, #1273 5497); the log of #1271's run (26b78e49, run 38090771465)
returned no text, so for it only the `success` conclusion is evidenced. CI ran on each PR
head, not on the squash-merge tree.
Verdicts below are proposals; the lead adopts, amends or rejects them (`CLAUDE.md` §13).

| Slice | PR | Merge sha (parent) | Plan | Ledger |
|---|---|---|---|---|
| SL-1257 | #1280 | fe80aec6 (3065770c) | PL-1583 | LG-1634 |
| SL-1541 | #1272 | d699a561 (99f22479) | PL-1540 | LG-1608 |
| SL-1529 | #1276 | e3a98c97 (b1cdefb5) | PL-1528 | LG-1623 |
| SL-1631 | #1278 | fbde0f70 (ff0edc39) | PL-1630 | LG-1632 |
| SL-1390 | #1279 | 3065770c (fbde0f70) | PL-1499 | LG-1633 |
| SL-1559 | #1281 | 372fa92a (fe80aec6) | PL-1558 | LG-1635 |
| SL-1600 | #1273 | 02f23b4a (d699a561) | PL-1599 | LG-1609 |
| SL-1557 | #1271 | 99f22479 (14fa6fb3) | PL-1556 | LG-1606 |

## Findings

One row per slice. "A<n>" is the plan's Acceptance item n.

| Slice | Acceptance items | Gaps (proposed verdict) | Closing acts at the merge sha |
|---|---|---|---|
| SL-1257 | A1, A2, A4–A8 MET; A3 PARTIAL; A9 CARRIED-by-LG only; A10 see closing | A3: no committed migration round-trip test and no "existing `api_keys` rows unchanged" test; the round trip is a slot-script result in the ledger (delivered but untested, `FD-9704`) | `LG-1634` and `SL-1257` `closed`; Audit "Not yet run"; MERGE-ACK "not yet given"; PRs "None yet" |
| SL-1541 | A1–A7, A9, A13 MET; A8 MET; A11 CARRIED-by-LG; A12 PARTIAL | A12: no local gate on the final tree (ruff E501 fixed after the gate); CI on the PR head `success`, 5469 passed. Write-set additions all carried by quoted rulings; `FD-1610` filed for the inliner defect | `LG-1608` `closed`; Audit "Not yet given"; MERGE-ACK "not yet given" |
| SL-1529 | A1–A9, A11–A13 MET; A10 PARTIAL | A10: ruff fixes after the local gate, "not re-gated"; CI on the PR head `success`, 5507 passed. Plan delta D1 (4 exempt slugs, not 5) lives in the ledger and a channel message only (X3, `FD-9724`) | `LG-1623` `closed`; its Gate table still "(not yet run)" above a later gate record; Audit empty |
| SL-1631 | (a)–(e) MET, (d) a GUARD not a red; LG line 1, 4, 5 MET/CARRIED | LG lines 2 and 3 (no money change; NFR-499) not written (not filed; proposed accept) | `LG-1632` `closed`; no Audit section |
| SL-1390 | A1–A3, A5–A7, A10 MET; A4 UNEVIDENCED; A8 CARRIED-by-CI | A4: the broken-loop proofs and the base-red outcomes of A3/A4/A10 are not recorded (delivered but untested, `FD-9712`); A8: `LG-1633` `### Gate` is empty, CI on the PR head `success`, 5522 passed | `LG-1633` `closed`; Audit "(Written by the auditor at slice close.)" |
| SL-1559 | A1–A9, A11–A17 MET by presence; A10 GAP; A18 PARTIAL | A10: the stored-data stop query (RL-1475) was never recorded; the slice retyped `rows`/`default_row` and shipped a migration (`FD-9714`) | `LG-1635` `closed`; Gate "Not run." above a real gate record; GO line stale |
| SL-1600 | A1–A5, A7, A8, A11, A12 MET; A6 GAP; A9 PARTIAL | A6: the ACK states 28/12 type counts where the plan states 30/10 and 74 changed types, with no recorded delta and no "reached today" list ((unfiled, id needed)). B1/B2 raise sites render the generic text in a 422 until P3 ((unfiled, id needed), conditional on P3 being a live row) | `LG-1609` `closed`; "Written by the auditor." |
| SL-1557 | A1–A23 MET by presence; A24 CARRIED-by-CI (conclusion only) | A24: ledger gate section empty and the frontend half of the local gate run not recorded (CI on the PR head `success`, run log empty); A16/A19 mismatch HTTP tests are GUARDS, not reds. Executor's finding candidate: no owned code for a malformed stored payload ((unfiled, id needed)) | `LG-1606` `closed`; Audit "Not yet." |

Cross-slice (X1–X3), filed once:

- **X1.** All eight ledgers and slice rows were set `closed` in the slice PR while the
  ledger's own `### Audit` read "Not yet" or was empty and `MERGE-ACK` read "not yet given".
  The `document-ids.md` §1.6 SL row lets the auditor's CLEAN verdict authorise the closing
  acts when the brief orders the audit before the mint; here the audit followed the merge.
- **X2.** Seven of eight ledger gate records end non-zero with failures classed "mint
  artefact" (13 `tests/` audit-on-tree modules and `audit-docs` checks 31/32/39). The
  claim that the mint-turn rerun is green is not in any ledger, but CI on each PR head is
  green (see Method), which discharges it for the PR heads; no finding is filed for X2.
- **X3.** Plan deltas accepted in channel messages (SL-1529 D1; SL-1559 "04:19:42" and
  "04:23:36"; SL-1600 "23:03:19" and "23:53:00"; SL-1541 "23:46:57") are recorded in the
  ledger build logs and the local channel file, not in the frozen plan.

## Result

Eight slices audited; no slice has a code defect found by reading. Proposed findings, each
to be filed as an `FD-` with the owner shown: `FD-9704` SL-1257 A3 (WK-674, MEDIUM);
`FD-9712` SL-1390 A4 and the unrecorded base reds of A3/A10 (WK-673, MEDIUM); `FD-9714` SL-1559 A10 (WK-675, MEDIUM);
(unfiled, id needed) SL-1600 A6 (WK-1178, LOW); (unfiled, id needed) SL-1600 B1/B2 generic text, conditional
(WK-1178, MEDIUM); (unfiled, id needed) malformed stored pinned payload has no owned code (WK-1178,
LOW); `FD-9724` X1 and X3: closing before audit, channel-only plan deltas (process, MEDIUM); (not filed; proposed accept) SL-1631 LG lines 2 and 3 (WK-1178, LOW, proposed accept).
Ids for the three unfiled rows are the lead's to give; the SL-1631 row is proposed accept and needs none.
