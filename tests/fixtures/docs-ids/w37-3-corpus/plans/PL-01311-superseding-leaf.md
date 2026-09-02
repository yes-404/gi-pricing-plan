---
id: PL-1311
family: plan
kind: leaf
title: Superseding leaf
status: active
created: 2026-01-06
owner: planner
phase: P9
work: WK-1200
slice: ~
tree: fixture
plans: []
supersedes: [PL-1310]
superseded_by: ~
corrected_by: []
corrects: ~
relates: []
was: ~
---

Fixture plan — the target of `PL-1310`'s `superseded_by:`. Carries no slice, so its own
execution resolves through the ordinary leaf ladder to "not started" (no `LG-` cites it and
it has no `SL-`); it exists only to give `PL-1310`'s derived value somewhere real to point
at, matching D1's "a bare number resolves anywhere" for a `superseded_by:` target.
