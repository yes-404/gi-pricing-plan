---
id: FD-2010
family: finding
title: audit-docs prints ceiling-counted disclosures with the word 'fatal'; a reader takes them for failures; the ceiling test is the enforcement
status: active
created: 2026-11-05   # drafted 2026-11-05 under working id 8367
owner: auditor
tree: 2f108b1eda22a4835279cee9b4c9e305babe3662   # origin/main when read
corrected_by: []
relates: [WK-1178]
---

# FD-2010 — audit-docs prints ceiling-counted disclosures with the word 'fatal'; a reader takes them for failures; the ceiling test is the enforcement

## Finding

**LOW, owner WK-1178.** First filed from to-lead "2026-11-05 12:05:12 GMT" (staged by lead 30 at 12:05:52 GMT) as "check 36 prints 497 lines labelled 'fatal' without failing the run: either the label is wrong or the check is unenforced". **Re-ruled on the arithmetic by the maintainer, to-lead "2026-11-05 14:07:26 GMT":** the check 36 lines ARE enforced, by the W37-11 residue ceiling, and fail only past it; the finding is the LABEL. `check_redirects` (`scripts/audit-docs.py:3282-3315`) counts every unexcused legacy-form hit as "fatal" in its summary note before the ceiling is applied; `main` then moves every failure whose `(path, cls)` population is at or under its recorded ceiling into a "DISCLOSED" block that is not counted (`:4215-4244`). A reader meets "497 fatal" beside "All checks passed" and takes the first for a failure.

**The enforcement and its threshold.** `tests/test_audit_docs_w37_11_ceiling.py` pins the rule: a `(path, cls)` key **at or under** its recorded ceiling is disclosed (`test_a_key_at_its_ceiling_is_disclosed`, `test_a_key_under_its_ceiling_is_disclosed`); a key **over** its ceiling is not disclosed at all and fails in full (`test_a_key_over_its_ceiling_is_not_disclosed_at_all`, with the broken-input proof the file's docstring names, a file pushed over its ceiling). The threshold per key is the `limit` recorded in `docs/process/residue-ceiling-record.md`, read through `_docid` (the same reader `_h1_residue_by_file` uses).

**The arithmetic.** audit-docs prints "DISCLOSED (849, at or under the W37-11 residue ceiling)" and no counted failure. The 849 by check, by the predicate `awk '/^DISCLOSED/{f=1;next} /^(FAILED|All checks)/{f=0} f && /^  - /' <output> | sed -E 's/^  - (check [0-9]+).*/\1/' | sort | uniq -c` over the output of `run-heavy.sh --light -- python3 scripts/audit-docs.py` (rc 0, "All checks passed.") at head `ec00b553050ec6aa6d651f5a943968b4cb3817d2` (this batch's branch, whose added files introduce none of these keys): check 2: 5; check 5: 5; check 30: 71; check 32: 244; check 35: 27; check 36: 497. 5 + 5 + 71 + 244 + 27 + 497 = 849. The maintainer verified the same sum at `2f108b1e` (14:07:26).

## Evidence

The line numbers and tests above, read at the tree in the front matter; the counts are the output named above, run at the head named above (not at the front-matter tree).

## Severity

**LOW.** No price or data is touched; a label in a governance check's output. No planted proof "that the run can be made to fail" is owed: the ceiling test is that proof and already exists.

## Disposition

Open, owner WK-1178, **fix before close with an owner** if a slice is free, else carried to P3 (the maintainer decides). Remedy, not made here: relabel the note so the pre-ceiling count reads "counted before the W37-11 ceiling" (or print the disclosed count only). The event that next discharges it: that relabel merging. Filed as working id 8367; minted FD-2010 in docs batch 11.

***Dated line, 2026-11-09*** (docs batch 29, by the auditor). `to-lead` "2026-11-09 10:12:52 GMT" (3): the auditor's proposed owner accepted as a proposal: **P3-D**. The row's own terms are fix before close if a slice is free, else carry; no code after the freeze (P19 (a)), so the carry applies; a note relabel. P19 (a); `CR-2103` P25 makes P3-C and P3-D WK-1178's successors, and neither has a `### WK-` row yet, so this record is their owner until the rows exist.
