---
id: PL-1910
family: plan
kind: map
title: Rollup-raise fixture map plan
status: active
created: 2026-01-02
owner: planner
phase: P6
work: WK-1900
tree: fixture
plans: []
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: []
was: ~
---

Fixture map plan for `scripts/audit-docs.py` check 33 — its one slice, `SL-1901`, carries
two live leaf plans at once (`PL-1911` and `PL-1912`, both `status: active`), which
`_slice_child_state` (`scripts/doc-index.py`) refuses to resolve silently (Ruling 72:
"a check 33 disagreement, not a case to resolve silently").
