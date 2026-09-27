---
id: RFC-789
family: proposal
kind: process
title: "zero calls above 200k tokens" measures the compaction cap, not discipline
status: closed                  # draft → active → closed | retired | superseded (§1.2a)
created: 2026-08-25
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this RFC itself corrects a frozen record
relates: []                     # ids only
was: docs/notes/0007-context-bound-measures-cap-not-discipline.md
---

# "zero calls above 200k tokens" measures the compaction cap, not discipline

## The reading and what it actually measures

A session's token-per-call distribution is bounded **by construction**: calls are
compacted — summarised, truncated, split — before they can exceed the cap, so the
distribution cannot have a tail above the line unless the cap itself failed. "Zero calls
above 200k" therefore reports where the compaction threshold sits, not how light the
session's context usage was. A heavy session and a disciplined session produce the same
zero; the heavy one just spends its last re-read at 199k.

## Why it matters

CLAUDE.md §10's context-discipline rule rests on the measured share of spend carried by
large-context calls. If the boundary metric reads "zero" by construction, treating that
zero as improvement is reading a bound as behaviour — the same error class as treating
an enforced invariant as evidence the enforcement worked. A metric whose ceiling is the
cap cannot measure anything below the cap.

## The usable form

The honest readings are **trends at the boundary**, not absence above it:

- the share of calls sitting just under the cap (e.g. 150k–200k) — how often sessions run
  at the edge;
- the share of *spend* those near-cap calls carry — the thing §10's 73% figure measured.

Absence above the line proves nothing; presence above the line proves only that the cap
failed, not that usage was heavy.
