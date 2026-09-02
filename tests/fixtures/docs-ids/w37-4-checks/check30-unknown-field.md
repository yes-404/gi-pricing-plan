---
family: finding
title: Fixture — decision on the wrong carrier
status: active
created: 2026-09-02
owner: auditor
tree: fixture
decision: fix before close
corrected_by: []
relates: []
---

# Fixture — decision on the wrong carrier

`decision:` is a register-row field (Ruling 70), not this essay's — `docs/_templates/FD.md`
does not declare it, so `_docid.parse_header` puts it in `.extra` and check 30 must reject
it as an unknown field. Ruling 70 §4 item 1: "A fixture `FD-` essay whose front matter
carries `decision:` must fail check 30."

## Finding

Fixture body — check 37 is not this fixture's target, so every `FD.md`-required section
(`## Finding`, `## Evidence`, `## Disposition`) is present regardless.

## Evidence

Fixture body.

## Disposition

Fixture body.
