---
family: ledger
title: Fixture — a ledger header carrying prs:
status: active
created: 2026-09-02
owner: executor
tree: fixture
plans: []
prs: [123]
corrected_by: []
relates: []
---

# Fixture — a ledger header carrying prs:

Ruling 70 §4 item 4: "A fixture ledger header carrying `prs:` must fail check 30" —
`docs/_templates/LG.md` records PRs in a `## PRs` body section, never a `prs:` header
field, so this must be rejected as an unknown field despite §1.5's parenthesis naming it.

## Tasks

Fixture body.

## PRs

Fixture body — the real place a ledger's PR list lives.
