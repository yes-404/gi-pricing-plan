---
id: RL-1657
family: ruling
title: FD-1624 corrected — the ledger it cites as "LG 9966" is LG-1641
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-12
owner: decision-maker
tree: 4af5997e14861bafda4685730180233db54dc243
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: FD-1624
relates: [FD-1624, LG-1641, SL-1526, WK-1178]
---

# RL-1657 — FD-1624 names a working id that was minted as LG-1641

*(Minted 2026-10-12 as RL-1657 from working id 9798, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

## Verified first, at 4af5997e14861bafda4685730180233db54dc243

FD-1624 (`docs/findings/FD-01624-…`, a frozen finding) says, in its Evidence section (line 24, the bullet on SL-1526): "SL-1526 (LG 9966; in-process run, `handover/sl1526-regate/inproc.out`, as the lead read it at 11:40:34)". "LG 9966" is a **working id**. `docs/ledgers/LG-01641-wk-1178-slice-sl-1526-exit-demo-a-the-real-fremtpl2-rating-algorithm-and-the-20000-policy-portfolio-pl-1525-pl-1577-slice-ledger.md` carries `id: LG-1641`, `slice: SL-1526`, `status: closed`, and was minted by SL-1526's merge, #1284, `4af5997e14861bafda4685730180233db54dc243`. `git grep -n "LG 9966" -- docs` at this tree finds FD-1624's line 24, the FD-1624 row of `docs/findings/register.md` and this record's own title in the generated `docs/INDEX.md`, and nothing else.

The authority is the lead's eta entries, in `handover/eta.md` (a local file, cited by entry header): "2026-10-11 19:59:29 BST" (LG 9966 reserved as LG-1641), "2026-10-11 20:21:10 BST" (FD-1624 line 24 cites working id "LG 9966" = LG-1641; needs a correcting record) and "2026-10-11 22:25:23 BST" (RL-1657 reserved for this record). This record decides nothing beyond the substitution; its `owner:` line is the lead's to confirm.

## Ruled

Wherever FD-1624 says "LG 9966", read **LG-1641**. No other word of FD-1624 is corrected: its finding, severity, owner and remedies stand. The correction is a new record and not an edit, because a frozen family's body is never edited (`document-ids.md` §1.11's check 34, and §1.5's header comment on `corrected_by:`); the option not taken, editing the body, would have been red on check 34 and would have destroyed the record of which id was believed. FD-1624 gains `corrected_by: [RL-<this record's minted id>]` at the mint and nothing else. The FD-1624 row of the register, which is not frozen, is annotated in place with a dated line naming this record.

## What it obliges

- The minter, at the mint of this record: append the minted id to FD-1624's `corrected_by:` (the only edit to that file), and rewrite this record's working id and the register annotation's working-id citation to the minted id.
- Nobody edits FD-1624's body. A reader of FD-1624 who meets "LG 9966" follows `corrected_by:` here.

## Acceptance — the violation that must become detectable

The violation: **a frozen finding's body edited to swap the id, or `corrected_by:` on FD-1624 naming a record whose `corrects:` does not name FD-1624.**

- *Violation: FD-1624's body edited.* Held by check 34 (the freeze), which reds when the diff against the merge-base touches more than `status:`, `superseded_by:` or an append to `corrected_by:`.
- *Violation: `corrected_by:` naming a record that does not correct FD-1624.* Held by the same check 34 clause: "every `corrected_by:` entry is a record whose `corrects:` names this file". This record's `corrects: FD-1624` is that link.
