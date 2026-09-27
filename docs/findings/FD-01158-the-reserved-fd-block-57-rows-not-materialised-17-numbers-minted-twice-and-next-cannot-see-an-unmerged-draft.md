---
id: FD-1158
family: finding
title: The reserved FD block — 57 legacy register rows not materialised, 17 of its numbers borne by other documents, and next cannot see an unmerged draft
status: active
created: 2026-09-27
owner: auditor
tree: 3749db65eb29fbe95dd46e6b787960fa8386af0b
corrected_by: []
relates: [PL-1144, RL-1078, LG-1137, OQ-1146]
---

# FD-1158 — The reserved FD block — 57 legacy register rows not materialised, 17 of its numbers borne by other documents, and next cannot see an unmerged draft

Filed by the auditor at 2026-09-27 15:04:42 BST, under the lead's adoption of 2026-09-27 14:58:11 BST
(C14 → a finding filed before the closure record, with face 19 of `PL-1144` Scope B as a
face of it). This is `PL-1144` Scope A item C14. It is filed in one commit with FD-1154 to
FD-1162, before the W37 closure record cites any of them (condition 1). At `3749db65` the
register had no row for the block or for its collisions.

## Finding

`docs/REDIRECTS.csv` allocates a block of `FD-` numbers to legacy findings-register **rows**.
They never become files. `RL-1078` §1 rules them *"allocated within the meaning of RFC-937 §1.1
rule 1 — reserved for named governed rows by a maintainer ruling — and their application is
W37-11's"*. Three things about the block are open:

1. **57 of the rows are reserved but not materialised.** `docs/INDEX.md` lists them as
   *"reserved (not yet materialised)"*.
2. **Numbers in the block are borne by other governed documents.** Before `W37-7` Task 16
   taught the allocator the reservation, `doc-id.py next` handed out numbers inside the block.
   So a legacy citation that resolves through the redirect row can land on an unrelated
   document. `RL-1078` §(vi) leaves the minted ids *"not this slice's to heal"*: they are
   permanent under `CLAUDE.md` §5, and after Task 16 they are *"a closed set that cannot
   grow"*.
3. **`next` cannot see an unmerged draft** (face 19, `PL-1144` F-19; the deputy, 11:28:23 and
   11:37:34 BST). `doc-id.py next` defaults to `--ref origin/main`, so an id held on an
   unmerged branch is invisible to it. `OQ-1146` was derived as next + 2 for this reason. The
   same mechanism produced this Work's own id collisions.

## Evidence

At `3749db65`, on a detached copy:

- **The block**: `grep ',docs/findings/register.md,' docs/REDIRECTS.csv | grep -oE 'FD-[0-9]{4}' | sort -u -V`
  gives **74** numbers, 1063 to 1136 (written bare here: the first seventeen do not resolve as findings, which is the defect). This is `RL-1078` §1's predicate, with `[0-9]{4}` in place of its `1[0-9]{3}`; both read 74.
- **Reserved, not materialised**: `grep -c 'reserved (not yet materialised)' docs/INDEX.md`
  gives **57**, first `FD-1080`, last `FD-1136`.
- **Borne by another document.** Each of the 74 numbers was tested for an `INDEX.md` row that
  is not a reservation. **17** have one: `CR-1063`, `CR-1064`, `CR-1065`, `FD-1066`–`FD-1069`,
  `PL-1070`–`PL-1073`, `FD-1074`, `RL-1075`–`RL-1078` and `FD-1079`. Nothing above 1079
  collides, so the closed-set property holds at this tree.
- **"15" against "17".** The records name **15** collisions (the deputy's count of 2026-09-19,
  carried by `PL-1144` C14 and the D5 line). `LG-1137:141` reads *"17 pre-fix"*. The measured
  set here is 17, and `RL-1078` and `FD-1079` are among its members. The two figures come
  from different dates and are both reported, with the predicate above. Neither is picked.
- **`LG-1137:141`, routed to W37-11:** *"Predicate (i) stops measuring the harm after Task 16.
  It read 17 pre-fix and reads 74 post-fix, because the population changed"*. The ledger
  proposes redefining it as *"reserved numbers carrying a record that is not their own
  reservation — which reads 17 on both sides"*. The test above uses that redefinition.
- **Face 19.** On 2026-09-27 `next` printed 1144 while unmerged drafts held 1144 and 1145, and
  `OQ-1146` took next + 2. The same day, W37-11's closure-record id was reported as 1154
  before nine findings were minted ahead of it. The block was renumbered to keep the sequence
  contiguous, so the record became 1163.

## Disposition

**The lead's verdict** (`RL-1078:278-280`: *"a verdict, not a decision point"*), adopted
2026-09-27 14:58:11 BST: **deferred with an owner — the lead**. Event: the create-read-retire
audit's first slice. The minted ids stay as minted. The D5 line (the deputy, 2026-09-26
17:06:12 BST, by delegation) is cited as the rule for any future reservation: *"the clause
governs every family"*. Fixing face 19 is the owner's choice: default `next` to `--ref HEAD`,
or print the ref it read.
