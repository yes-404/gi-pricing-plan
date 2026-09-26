---
family: reference
title: Fixture — a Reference file with an undeclared key
status: active
created: 2026-09-27
owner: lead
tree: fixture
corrected_by: []
relates: []
name: fixture-agent
description: "Fixture agent front matter, merged with the governed Reference header."
tools: Read, Grep
model: sonnet
colour: red
---

# Fixture — undeclared key still fails

`RL-1140` DP-8.1: the harness-key licence is narrow — `docs/_templates/REFERENCE.md` does
not declare `colour:`, so this header must still fail check 30 on it even though the four
harness keys are declared and pass. A licence that accepts anything has not been tested
(`CLAUDE.md` §13).

## Fixture

Fixture body — check 30 is this fixture's only target.
