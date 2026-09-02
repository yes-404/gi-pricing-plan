---
id: PL-1320
family: plan
kind: map
title: Alpha map
status: active
created: 2026-01-01
owner: planner
phase: P9
work: WK-1200
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

Fixture map plan for the roll-up rule NT-0019 §1.7 states: "any `in progress` gives
`in progress`." Its slices' leaf plans are every `kind: leaf` plan sharing `work: WK-1200` —
`PL-1300` (not started), `PL-1302` (in progress), `PL-1305` (executed), `PL-1307` (closed),
`PL-1310` (superseded), `PL-1311` (not started), `PL-1314` is `kind: review` and so is not a
leaf child of this map. `PL-1302`'s "in progress" must win over every other child's state.
