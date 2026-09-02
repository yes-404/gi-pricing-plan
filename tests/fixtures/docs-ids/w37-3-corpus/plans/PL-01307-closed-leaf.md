---
id: PL-1307
family: plan
kind: leaf
title: Closed leaf
status: active
created: 2026-01-04
owner: planner
phase: P9
work: WK-1200
slice: SL-1201
tree: fixture
plans: []
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: []
was: ~
---

Fixture plan — the "closed" execution case: its slice `SL-1201` is `closed` and `CR-1309`
cites `work: WK-1200`. Note `status:` stays `active` — `closed` is never a legal `status:`
value for the `plan` family (NT-0019 §1.2's status subset for PL is
`draft → active → superseded | retired`); "closed" is the *derived* `execution` value NT-0019
§1.7 defines, held nowhere on this file.
