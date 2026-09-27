---
family: ruling
title: Fixture — a non-Reference file carrying a harness key
status: active
created: 2026-09-27
owner: decision-maker
tree: fixture
phase: P2
work: WK-00697
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: []
tools: Bash
---

# Fixture — the licence is per family

`RL-1140` DP-8.1: the harness-key licence is per family, not global. `docs/_templates/
RL.md` does not declare `tools:`, so a ruling carrying it must still fail check 30 —
proving the four names were not added to `scripts/_docid.py`'s `_KNOWN_KEYS`, which would
license them for every family through a hand-written constant (the second copy `RL-981`
§2 item 1 refuses). No `id:` is given, so check 31 (which only fires on a present id) and
check 37's section requirement are both satisfied below, keeping this fixture's only
failure on check 30.

## Ruled

Fixture body.

## What it obliges

Fixture body.

## Acceptance — the violation that must become detectable

Fixture body.
