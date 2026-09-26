---
family: reference
title: Fixture — a Reference file with the merged Claude Code harness header
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
---

# Fixture — merged harness header, all declared

`RL-1140` DP-8.1: the four Claude Code harness keys (`name:`, `description:`, `tools:`,
`model:`) are declared in `docs/_templates/REFERENCE.md`'s top-level `---` block and are
permitted for the reference family. This header carries all four alongside the governed
keys and must pass check 30 cleanly — the positive control for the harness-key licence.

## Fixture

Fixture body — check 30 is this fixture's only target.
