---
id: PL-1710
family: plan
kind: map
title: Ruling 72 item 3 map
status: active
created: 2026-02-01
owner: planner
phase: P7
work: WK-1700
slice: ~
tree: fixture
plans: []
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: []
was: ~
---

Ruling 72 acceptance item 3 ("replanned then completed"): `WK-1700` has one slice,
`SL-1701`, whose leaf plan `PL-1711` was superseded by `PL-1712`, which then closed.
Must roll up to `closed` — the defect this fixture pins read `not started`, because the
superseded leaf's own derived value (`superseded → PL-1712`) matched no branch of the
old catch-all logic.
