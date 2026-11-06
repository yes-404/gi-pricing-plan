---
id: FD-8402
family: finding
title: scripts/doc-index.py derives a leaf plan's execution as closed from a work CR's existence, not its verdict
status: active
created: 2026-11-06   # working id 8402, drafted 2026-11-06 (aud-wk674b), filed by exec-cr8315
owner: auditor
tree: 9b18810ae6af807d6c1c4f3bae5556b4ab02c96d
corrected_by: []
relates: [WK-1178, CR-8315, CR-1952]
---

# FD-8402 — doc-index derives a plan's `execution: closed` from a closure record's existence

*(Filed 2026-11-06 from working id 8402, in the PR of CR 8315, as ruled by to-lead "2026-11-05 12:02:53 GMT" and `to-lead` "2026-11-06 09:58:14 GMT" (5): owner WK-1178.)*

## Finding

`_derive_leaf_execution`, `scripts/doc-index.py:798`, returns `closed` when `_closure_covers(header, corpus)` holds and the slice is `closed`. It does not read whether the Work closed. Filing a close **audit** therefore moves five WK-674 leaf plans from `executed` to `closed` in `docs/INDEX.md` while the Work is `active`: a wrong status in a generated index.

## Evidence

`git diff 2f108b1e 7d65135d -- docs/INDEX.md`: PL-1239, PL-1303, PL-1348, PL-1392, PL-1583. The same defect at WK-675: process-backlog row 2026-10-26 10:58 GMT.

## Severity

LOW, ruled. The INDEX line is accepted as generated output, never hand-edited.

## Disposition

**Deferred with an owner: WK-1178.** Derive `execution` from the closure record's verdict, red first, or a ruling. The Work stays `active`.
