---
family: reference
title: Fixture — owner is not a role filename or maintainer
status: active
created: 2026-09-02
owner: some-random-person
tree: fixture
corrected_by: []
relates: []
---

# Fixture — bad owner

`owner: some-random-person` is neither a filename under `.claude/roles/` nor
`maintainer`. No `id:` (Reference carries none), so check 31 stays clean; `status:
active` is in Reference's own subset, so check 33 stays clean too.
