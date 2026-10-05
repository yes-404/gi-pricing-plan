---
id: RFC-9635
family: proposal
kind: process
title: Working ids and the meaning of created — the rules the 2026-10-05 id audit found practised but unwritten
status: draft                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-10-05            # drafted 2026-10-05; set to the mint date at mint (RL 9634 clause 2)
owner: maintainer
tree: 83ea509023d6d705d6f78fe74b7124fdf1375739
deliverable: RL-9634 applied — document-ids.md §1.5 and §1.7 amended with T1, T2a and T2b (the working_id field); the lint (T3, adopted by OP-C as ruled) cut into WK-1178's backlog
lands_in: docs/process/document-ids.md (and scripts/audit-docs.py only if T3 is adopted)
trigger: a working id is reserved, cited or minted; a governed record is minted
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RL-9634, WK-1178]
---

# RFC-9635 — Working ids and the meaning of `created:`

*Working id 9635; drafted 2026-10-05 by the decision-maker on the lead's instruction
(`document-ids.md` §1.6 RFC row: "any role drafts on instruction"). Its ruling is RL 9634. It
rests on two entries of the maintainer (by delegation) in `~/gi-pricing-plan.local/channel/to-lead.md` (a local file, not
in the repository): `2026-10-05 14:15:12 BST — ID AUDIT (the maintainer asked: "are recently
created ids consistent with the id requirement?"): the sequence is sound; 4 defects to fix, 3
rule gaps` (its "RULE GAPS" paragraph), and `2026-10-05 14:26:28 BST — ID AUDIT: consolidated
instruction and next steps (the maintainer: "instruct the lead and next steps about your
findings")` (its item 5). It mints after the freeze reconcile, #1147 (RFC 9653 + RL 9654, open
at `cd08475b`), in the mint queue like any record. The family is `process/`'s, so the
maintainer owns it (`document-ids.md` §1.6); the maintainer (by delegation) accepts it at its ACK.*

*The four open points (OP-A to OP-D) were ruled by the maintainer (by delegation) in the entry
`2026-10-05 14:33:33 BST — RFC 9635 + RL 9634 (#1153 @b14d674f, the working-id rules): OP-A..OP-D
RULED now, two narrowed`: OP-A (a) narrowed, OP-B (a), OP-C (a), OP-D (a), and clause (vii)
"OK". RL 9634 quotes the entry in full and carries each ruling into its clauses and T-texts.
Folded 2026-10-05 15:55 BST, with every cite re-verified at origin/main `cdaaa573`.*

## Problem

`document-ids.md` defines how a minted id is cited (§1.7: "Prose cites `<PREFIX>-<n>`") and
allocated (`doc-id.py next`, "The number is taken by the commit that adds it"). It says
nothing about the **working id**: the provisional number a record carries from its first
draft until it mints. The practice is uniform and the team relies on it every day, but it is
written only in channel entries and briefs. The maintainer's (by delegation) audit at origin/main `99afcde2`
found three gaps, all re-verified here at `83ea5090`:

1. **Working ids.** Practice: four digits from 9000 up, the space form ("FD 9707"),
   reserved by the lead in `~/gi-pricing-plan.local/handover/eta.md`'s reservation table.
   Nothing written forbids a working id in a title or slug, or says when it is re-pointed.
   The defects that followed:
   - `RL-1362`'s title reads *"PL 9789 DP-S3-1 to DP-S3-5 decided — …"* and its filename
     slug begins `rl-01362-pl-9789-…`. PL 9789 minted as `PL-1382` (`PL-1382`'s body: "filed
     under working id 9789"). Added by `c535b19d`, 2026-10-01.
   - `RL-1379`'s title reads *"PL 9765 DP-S2-7 decided — …"* and its slug begins
     `rl-01379-pl-9765-…`. PL 9765 minted as `PL-1392` (`PL-1392`'s body: "filed under
     working id 9765"). Added by `95bcf1a9`, 2026-10-03.
   - `docs/specs/03-rating-engine.md:136` reads *"(Amended 2026-10-04, RL-1379, on FD 9754:
     …"*; FD 9754 had minted as `FD-1393` (its body: "**Working id 9754**"). This is the
     audit's D1.
   - `docs/roadmap.md:1434` names "FD 9747" and "FD 9748", which minted as `FD-1415` and
     `FD-1414` (their bodies: "id 9747" and "FD 9748's remedy"). This is the audit's D2.
     #1150 (open, head `72f2acb5`) re-points D1 and D2; at `83ea5090` both still read as
     quoted. #1150 has since merged as `bc92bb7e`: at `cdaaa573` the two lines read "on
     FD-1393" and "FD-1415", "FD-1414".
   - Seven open PR titles carried working ids in the hyphen form — the form a real id takes
     — so a squash merge would have put a non-existent id into main's history. This is
     the audit's D4. The maintainer's (by delegation) 14:26:28 entry records it fixed ("7 PR titles in space
     form, verified 0 left"); this RFC does not re-measure open PR titles.

   #1147 records `RL-1362`'s and `RL-1379`'s titles and slugs as known historical defects,
   standing as merged, with no correcting record (the maintainer's (by delegation) `2026-10-05 14:19:21 BST —
   CORRECTION to my 14:15:12 order 3: RL-1362 and RL-1379 are NOT under the cut; #1147's
   recording accepted`). This RFC does not record them again. It writes the rule whose
   absence let them merge.

2. **`created:`.** §1.5 lists `created:` and check 31 requires it "non-decreasing with the
   number", but nothing says which date it is. Three readings are in use at `83ea5090`:
   - **The mint date, with the filing date in a YAML comment.** `RL-1379`:
     `created: 2026-10-03              # the mint date (check 31); ruled 2026-10-01`, added by
     `95bcf1a9` (`%cI` 2026-10-03T18:31:02+01:00). `FD-1413`:
     `created: 2026-10-05            # the mint date (check 31); filed 2026-10-01`, added by
     `072c56e1` (2026-10-05T12:10:45+01:00). `RL-1379` is the earlier of the two.
   - **A date before the mint, with no comment.** `RL-1346` and `RL-1347` read
     `created: 2026-09-30`. Their bodies say "**Minted 2026-10-01 as RL-1346**" (`RL-1346`:31)
     and "**Minted 2026-10-01 as RL-1347**" (`RL-1347`:30). Both were added by `d2ac260d` at
     2026-10-01T00:57:18+01:00. **That instant is 2026-09-30 23:57:18 UTC.** So the
     `created:` value equals the merge's **UTC** date and differs from its **UK** date. The
     files do not say whether 2026-09-30 was meant as the filing date or was a UTC reading.
     Either way, the header and the body disagree.
   - `LG-1412` reads `created: 2026-10-04`. Its body :21 reads "reserved by the lead
     2026-10-04 17:15:20 BST (dispatch Delta 1); it was minted as `LG-1412` on 2026-10-05".
     It was added by `36a9f483` at 2026-10-05T11:45:05+01:00, which is 10-05 in UTC as well.
     So this value is the reservation date. It is not a clock artefact.

   Check 31 passes all three because each value is still non-decreasing with the number.
   A rule that does not name its clock leaves the `RL-1346` case undecidable.

3. **Check 32 cannot see the space form.** Its resolver (`check_citations` in
   `scripts/audit-docs.py`, via `_docid.ID_RE`; §1.7's pattern
   `\b(FR|NFR|DEP|OQ|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0*(\d+)\b`) needs a hyphen. A
   working id that stays in a living file after it mints is therefore invisible to the
   gate. D1 and D2 are two such cases.

### Noted for this RFC's audit: two pre-existing hits of a name with no role

The maintainer (by delegation), entry `2026-10-05 15:11:49 BST — #1157 (SL-1409): OPTION (b),
one docs fix commit; a 9th session allowed for it`, last line: the two pre-existing hits of
the name that #1157's wording commit replaced in its narrative by "the maintainer (by
delegation)" (the FR-351 row and INDEX) are not #1157's, and
are listed for this RFC's audit. They are listed here, at `cdaaa573`:

- `docs/specs/06-governance.md:92`, the **FR-351** row (its 2026-09-28 WK-1178 amendment).
- `docs/INDEX.md:369`, FR-351's generated INDEX row, which mirrors the spec row. It is
  regenerated by `doc-index.py` when the spec row changes, never edited by hand.

Scope: the predicate `git grep -c -i 'd[e]puty' cdaaa573 -- <path>`, counts more lines
in living files at that tree: `docs/specs` 17 (in total), `docs/roadmap.md` 15,
`docs/open-questions.md` 5, `docs/findings/register.md` 58 and `docs/INDEX.md` 16. This RFC
does not classify them (narrative or quotation) and proposes no edit. That is not part of the
working-id rules, and the entry asks only for the two hits to be listed.

## Proposal

Write the practice down as three T-texts in `docs/process/document-ids.md`. RL 9634 states
them in full: **T1** (a new paragraph at the end of §1.7, "Working ids"), **T2a** (a sentence
after §1.5's field block, defining `created:`), **T2b** (the `working_id:` field, added to
§1.5's closed field set by OP-C as ruled) and **T3** (the lint, adopted by OP-C as ruled; not
built here). The spec-change skill states no id rules (read at `83ea5090`: it covers requirement
ids, sections and open questions, and says nothing about working ids or `created:`), so it
does not change. Nothing is applied in this PR beyond the two record files.

**Measured against practice: what a lint would see today.** Predicate, run at `83ea5090`:

```
git grep -n -o -E '.{0,50}\b(FD|RL|PL|SL|LG|RFC|OQ|RS|CR|WK) 9[0-9]{3}\b.{0,30}' 83ea509023d6d705d6f78fe74b7124fdf1375739 -- docs/specs docs/roadmap.md docs/open-questions.md
```

It printed 13 hits on 11 lines. Each one, classified:

| Hit | Class |
|---|---|
| `03-rating-engine.md:136` "on FD 9754" | **stale**: minted as `FD-1393` (D1) |
| `roadmap.md:1434` "FD 9747", "FD 9748" | **stale**: minted as `FD-1415`, `FD-1414` (D2) |
| `roadmap.md:603`, `:736`, `:1019`, `:1377` | **quotation**: each is inside a quoted channel-entry header ("entry \"2026-10-01 08:01:45 BST — FD 9786 …\"", etc.) |
| `open-questions.md:141` (twice), `03-rating-engine.md:1369` "`PL 9776` (working id)" | **live**: PL 9776 is not minted; labelled "(working id)" |
| `00-overview.md:346`, `07-platform.md:181`, `roadmap.md:774` "RFC 9457" | **not an id**: IETF RFC 9457 (HTTP problem details) |

So 3 of the 13 hits are true positives. A lint that fired on all 13 would be noise. T3 says
how to exclude the other three classes. The `RFC 9457` class is the one nobody named: the
`RFC` prefix in the space form collides with IETF numbering. This RFC's own working id, 9635,
is also an IETF RFC number.

## Deliverable

RL 9634 applied: T1, T2a and T2b land in `document-ids.md` in one docs PR, with
`audit-docs.py` clean apart from the known check 31 and 34 rows. T3 was adopted by OP-C as
ruled. It becomes a WK-1178 backlog item (owner the lead), warn-only until the date that
RL 9634 states at its mint, then fatal. WK-1178, the standing maintenance Work, cuts it. No
new Work is needed.
