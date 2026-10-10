---
id: FD-1586
family: finding
title: The 03 rating-engine attribute paragraph sat twice after 84ff9f0b merged Slice 4 from a branch stacked on Slice 3's pre-squash base, and both MERGE-ACKs missed it
status: active
created: 2026-10-10            # original date 2026-10-10, set at the mint; minted 2026-10-10 (no earlier draft)
owner: lead
tree: db0642c4b4f87e71dceff36d1ebd7c7ba4ef68f9
corrected_by: []
relates: [WK-673, SL-1387, SL-1388, FD-1585]
---

# FD-1586 — The `attribute` paragraph sat twice in 03

*Disclosure: this finding was drafted under working id 9944 and minted as FD-1586 on 2026-10-10, in the D6 batch mint PR. It has no earlier draft branch; the minter wrote it from the lead's entry "2026-10-10 07:09:25 BST — RULING: the duplicated 03 paragraph. FIX in D6 (remove :1190); record as an FD, not a backlog row, because the L3 VALVE applies (a wrong merge got through); ACK standard tightened" in `to-lead.md`, items 2 and 3.*

## Finding

`docs/specs/03-rating-engine.md` carried the Slice 3 paragraph that begins `*`attribute` (added 2026-10-08, WK-673 Slice 3).*` **twice**, at `:1188` and `:1190`, byte-identical (`md5` of the line with its newline: `a6ef61390741ad79376b41793172b99d`, 734 characters each, blank `:1189` between). The copy at `:1190` adds nothing: the spec said the same thing twice.

It entered main through `#1256` (WK-673 Slice 4, `SL-1388`), squash `84ff9f0b8d5369d08559d030cf235c60ad51abd0`, merged 2026-10-10 05:13:44 BST. Slice 4's branch was stacked on Slice 3's pre-squash base, and Slice 3 (`#1243`, `SL-1387`) had already landed that paragraph on main as `e40ab532278685cc3c59b3834d18310129218b55`. The merge of the stacked branch applied the paragraph a second time without a conflict. **Both MERGE-ACKs missed it:** the lead's request and the maintainer's entry "2026-10-10 05:13:20 BST — MERGE-ACK #1256 (WK-673 S4, SL-1388) @c9ad7b289964b834b63009ace002b4d1b1d97e0e …" in `to-lead.md`.
The defect is content-neutral (no requirement, number or shape changed), so it is **LOW**. It is a finding rather than a backlog row because RFC-1506 L3's valve applies: a wrong merge got through.

## Evidence

- **Two copies at the merge, one before it.** Counting lines that begin ``*`attribute` (added 2026-10-08, WK-673 Slice 3)`` in `docs/specs/03-rating-engine.md`: `git show e40ab532:docs/specs/03-rating-engine.md | grep -c '^\*`attribute` (added 2026-10-08, WK-673 Slice 3)'` prints `1`; the same command at `84ff9f0b` prints `2`; `e40ab532` is an ancestor of `db0642c4`.
- **The only duplicated long line.** `git show <rev>:docs/specs/03-rating-engine.md | awk 'length>120' | sort | uniq -c | awk '$1>1'` prints nothing at `e40ab532` and exactly this line, with count 2, at `84ff9f0b` and at `db0642c4` (the minter's run on the spec; the lead's own scan of every docs file `#1256` and `#1259` changed found no other, `docs/contracts/generated.json`'s repeated parameter descriptions being normal).
- **The two lines are identical.** At `db0642c4`, `sed -n 1188p` and `sed -n 1190p` of the file each pipe to `md5sum` as `a6ef61390741ad79376b41793172b99d`.
- **The fix is this batch.** D6 removes `:1190`; `git diff -U0 -- docs/specs/03-rating-engine.md` shows exactly one line removed and none added.

## Disposition

**Severity LOW (proposed by the minter from the lead's ruling; the lead decides). Owner: the lead's process.** The duplicate is fixed in this batch (the entry's item 1). What remains is the gap that let it through, closed by the ACK standard of the entry "2026-10-10 07:09:25 BST", item 3, which applies from then on to every PR whose branch was built on a pre-squash base or merged main more than once: the ACK request includes (a) `git merge-tree --write-tree <true base> main head` equal to the PR's tree, or the diff between them explained; and (b) a duplicate-long-line scan over every changed docs file (lines over 120 characters, `sort | uniq -d`), with the result. The lead runs (b) at each ACK.

**Decision: fix before close with an owner: the lead's process.** The fix is merged with this record; the standard is the disposition. Event that next confirms or discharges it: the first ACK request after 2026-10-10 07:09:25 BST that carries (a) and (b), or a duplicate-long-line scan over the docs suite at a later tree that prints nothing.
