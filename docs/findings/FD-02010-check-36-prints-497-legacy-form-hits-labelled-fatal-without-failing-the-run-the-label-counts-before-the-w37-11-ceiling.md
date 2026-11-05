---
id: FD-2010
family: finding
title: Check 36 prints 497 legacy-form hits labelled fatal at 2f108b1e without failing the run: the label counts before the W37-11 residue ceiling, which discloses them
status: active
created: 2026-11-05   # drafted 2026-11-05 under working id 8367
owner: auditor
tree: 2f108b1eda22a4835279cee9b4c9e305babe3662   # origin/main when read
corrected_by: []
relates: [WK-1178]
---

# FD-2010 — Check 36 prints 497 legacy-form hits labelled fatal at 2f108b1e without failing the run: the label counts before the W37-11 residue ceiling, which discloses them

## Finding

**LOW, owner WK-1178.** Wording and authority: to-lead "2026-11-05 12:05:12 GMT" as staged for the next mint by lead 30 at 12:05:52 GMT: check 36 prints 497 lines labelled "fatal" at `2f108b1e` without failing the run; either the label is wrong or the check is unenforced.

**A reading of `scripts/audit-docs.py` (read at the tree in the front matter; not run here).** `check_redirects` calls `fail()` once per legacy-form hit that `_legacy_form_disclosure_reason` does not excuse, and its summary note counts those as "fatal" (`:3282-3315`). `main` then runs `_partition_by_w37_11_record()` last (`:4215-4220`) and moves every failure whose population is at or under its recorded W37-11 ceiling out of the counted failures into a "disclosed" block, which is printed by name and not counted (`:3619-3628`, `:4232-4244`); only `counted` makes the run return 1. So the check is enforced against the ceiling and not unenforced: the word "fatal" in the note is the pre-ceiling count, which the ceiling then discloses. The label is therefore misleading, and the question the ceiling leaves is whether any of the 497 sits OVER its ceiling and is hidden by the label rather than counted.

## Evidence

The line numbers above, read from `scripts/audit-docs.py` at the tree in the front matter. The 497 figure is the lead's relay and was not re-counted here. No check was run for this record: the audit-docs run is held (TESTS HOLD).

## Severity

**LOW.** No price or data is touched; a misleading label in a governance check's output.

## Disposition

Open, owner WK-1178, **fix before close with an owner** if a slice is free, else carried to P3 (the maintainer decides). Remedy, not made here: relabel the note ("counted before the W37-11 ceiling") and prove on PLANTED input that a hit over its ceiling fails the run, before any change is made to make it fail (a check that has never printed a failure has not been tested, CLAUDE.md §13). The event that next discharges it: that planted-input proof. Filed as working id 8367; minted FD-2010 in docs batch 11.
