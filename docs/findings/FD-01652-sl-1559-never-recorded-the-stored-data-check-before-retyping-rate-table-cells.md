---
id: FD-1652
family: finding
title: SL-1559 never recorded the stored-data check required before retyping rate-table rows and default_row
status: active
created: 2026-10-12
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
corrected_by: []
relates: [WK-675, SL-1559, PL-1558, LG-1635, RS-1649, FR-232]
---

# FD-1652 — the RL-1475 stored-data stop was not recorded

*(Minted 2026-10-12 as FD-1652 from working id 9714, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Filed by the retro audit RS-1649. Reads are at the squash-merge `372fa92a` (PR #1281).

## Evidence

- PL-1558 Acceptance 10: "The stored-data stop (RL-1475 *What it obliges*). Task 0 step 4's query output is pasted in the ledger. It shows no persisted non-`str` row or `default_row` value."
- LG-1635 at the merge sha: the Task 0 table says "step 4 OWED (no database on the box)"; the 2026-10-10 08:52 re-run says "Step 4 (the two `jsonb_typeof` counts) stays owed to the gate"; the gate-1 entry (25ede2d4) and the mint-turn entry do not mention it.
- The slice retyped `rows` and `default_row` to `RateTableCell` (`packages/model-schema/src/model_schema/rating.py`) and added the revision `d4e81b7a2c95`; CI on the PR head concluded `success` (pytest 5604 passed), which does not read any stored data.

## Finding

**Severity MEDIUM (proposed by the auditor):** the plan made this query a stop condition because a stored non-string value would fail validation after the retype. The merged record cannot show the stop was cleared. Verdict candidate: delivered but untested; exposure is likely nil (the dev database held no deployed rating), which the query would show.

## Disposition

**Owner: WK-675.** Decision: `fix before close with an owner: WK-675` — run the two read-only `jsonb_typeof` counts the plan names and record the output. Event that next confirms or discharges it: that output in a dated record. Filed by the auditor, 2026-10-11; the lead gives the verdict.

## Discharge path

Required by the maintainer's condition, `to-lead.md` "2026-10-11 20:17:38 BST" item 4: "each retro FD names its DISCHARGE PATH and date, not only an owner, so \"delivered-but-untested\" is closed by a TEST that runs, before the P2 close".

Measure on the dev database, read-only, `select count(*) … where jsonb_typeof(...) <> 'string'` over the stored `rows` and `default_row` values PL-1558 names, and record the count in this FD. If non-zero, it becomes a fix row under WK-675. Date, accepted by the lead: the first free window, no later than Fri 2026-10-23, and before the P2 exit demo, Thu 2026-11-12.
