---
id: FD-2129
family: finding
title: "A `control`-intent column reaches a price through a rate-table key that has no `factor_ref` (a bare `name`, or a `banding_ref` only), because FR-240 binds intent \"by `factor_ref`\" and a key with no Factor carries none"
status: active
created: 2026-11-13
owner: auditor
tree: edad3ec0dacf
corrected_by: []
relates: [WK-2113, SL-2124, LG-2125, FD-1495, OQ-2127, FR-240, FR-86, FR-88]
---

# FD-2129 — A `control`-intent column reaches a price through a rate-table key that has no `factor_ref` (a bare `name`, or a `banding_ref` only), because FR-240 binds intent "by `factor_ref`" and a key with no Factor carries none

*Working id 8440, allocated by lead 34; minted as FD-2129 (WK-2113 S1). This document files, as a finding file, the register row that carried the finding as a row only. Every statement below is the register row's, quoted; nothing is added to it.*

## Finding

Per the register row (`docs/findings/register.md`, the row ending "(FD 2129)"), severity and source: **MEDIUM**, set by the maintainer (by delegation), "2026-11-13 19:58:38 GMT" entry (`to-lead.md`): a control column reaches the price by a bare-name key. Probe `scratch/exec-g3g4p/probe.md` at 2ba0d0d5, step 2: `score_one` with `channel` direct against broker gives 1507 against 1713 minor units. **Spec gap, decision owed: OQ 2127** (options (a) to (d) in `docs/open-questions.md` and `03` §10); not a guard bug, since FR-240 and FR-86/FR-88 are silent on a key with no Factor. The SL 2124 guards do not cover it and its FR-240 dated clarification says so. Candidate row under working id 8440.

## Evidence

Locators are those the register row names, and `docs/ledgers/LG-02125-*` and `docs/open-questions.md` OQ-2127; read at origin/main `edad3ec0dacf`. Not run here: this file adds no measurement beyond the row's.

## Disposition

Register decision, per the row (WK-2113, phase 3): **deferred with an owner: WK-2113** (carried with a named owner, CLAUDE.md §14); the event that next discharges it: the decision on OQ 2127, then the slice that implements it.
