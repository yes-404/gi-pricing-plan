---
id: FD-1166
family: finding
title: Rows owned by the §14 review decay through reviews without a register change
status: active
created: 2026-09-27
owner: auditor
tree: cddf9a6e32e6a780ac93ba769767bb602b054919
corrected_by: []
relates: [CR-932, CR-1050, CR-1064, FD-1165]
---

# FD-1166 — Rows owned by the §14 review decay through reviews without a register change

Filed by the auditor on 2026-09-27, in W37-11's closing-record PR, on the lead's instruction.
The evidence comes from the lead's plan review 14 (read-only, at `cddf9a6e`). The auditor
re-read the cited review text at `cddf9a6e` before filing.

## Finding

Eleven register rows name "the §14 review" as their owner or their decay target:
- FR-240 / F-W9-3, clauses 4–6;
- F27, clause (c);
- F29, F31, F33, F48, F58, F61, F63, F74 and F75.

Three plan reviews have passed over them since then, and none of the three left a register
change behind:

- **Review 11** discussed them
  (`CR-00932-plan-review-11-completing-the-review-sequence-at-wk-671-s-close-before-wk-672-opens.md:52-140`).
  Its acceptance (`:288-294`, dated 2026-09-01) says that *"the eleven register rows behind
  this review now pass to their named owners"*. But for most of them the review's text is a
  recommendation that is explicitly "not a pick". So the named owner that the rows pass to
  is, in their own cells, still the §14 review.
- **Review 12** (`CR-01050-plan-review-12-the-w37-6-w37-11-boundary-mid-window.md:70-72`)
  says *"Eleven rows predate WK-697 and are not re-derived here"*, under the skill's rule
  *"if a fresh audit has just covered this, say so and move on"*.
- **Review 13** (`CR-01064-plan-review-13-the-w37-6-close-the-w37-7-11-cut.md:139-144`) says
  that *"the eleven predating rows … take no new disposition here"*, and it cites review 11's
  acceptance as having passed them on.

Each review defers to the one before it, and the register cell is the one place that none of
them updates. A row owned by a recurring event decays through every occurrence of that event
unless the occurrence writes to the cell.

## Evidence

At `cddf9a6e`, `python3 scripts/register-owed.py review` exits 0 and still lists all eleven,
because each Decision cell still contains `§14` (FD-1165 limb 1 describes the predicate). The
lead's review-14 evidence reads that no cell changed across reviews 11–13. The auditor
verified the current state, that all eleven still match the §14 predicate at `cddf9a6e`. The
auditor did not replay the register's history across the migration, which rewrote its paths.

## Disposition

**Deferred with an owner — the lead** (the lead's instruction, 2026-09-27, at plan review
14). Event: the create-read-retire audit's first slice. This is related to F86, the RL-909
decay rule, whose limbs are not built (`CR-1164` §8). A decay rule that moves a row to "the
next review" needs the review to write its disposition into the row, or a check that fails
when a review passes a row on unchanged.
