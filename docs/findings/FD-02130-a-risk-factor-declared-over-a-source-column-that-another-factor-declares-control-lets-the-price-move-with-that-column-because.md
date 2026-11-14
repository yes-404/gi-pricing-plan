---
id: FD-2130
family: finding
title: "A `risk` Factor declared over a source column that another Factor declares `control` lets the price move with that column, because intent is a property of one Factor (FR-86, FR-88) and the guards read the Factor path only"
status: active
created: 2026-11-13
owner: auditor
tree: edad3ec0dacf
corrected_by: []
relates: [WK-2113, SL-2124, LG-2125, FD-1495, OQ-2128, FR-240, FR-86, FR-88]
---

# FD-2130 — A `risk` Factor declared over a source column that another Factor declares `control` lets the price move with that column, because intent is a property of one Factor (FR-86, FR-88) and the guards read the Factor path only

*Working id 8441, allocated by lead 34; minted as FD-2130 (WK-2113 S1). This document files, as a finding file, the register row that carried the finding as a row only. Every statement below is the register row's, quoted; nothing is added to it.*

## Finding

Per the register row (`docs/findings/register.md`, the row ending "(FD 2130)"), severity and source: **LOW**, set by the maintainer (by delegation), "2026-11-13 19:58:38 GMT" entry (`to-lead.md`): the price moves with a column another Factor calls control, and no act the spec prohibits as written is performed. Probe `scratch/exec-g3g4p/probe.md` at 2ba0d0d5, step 2: `driver_age` 20 / 45 / 70 gives 2578 / 2330 / 2141 minor units. **Spec gap, decision owed: OQ 2128** (options (a) to (d) in `docs/open-questions.md` and `02` §10). The SL 2124 guards do not cover it and its FR-240 dated clarification says so. Candidate row under working id 8441.

## Evidence

Locators are those the register row names, and `docs/ledgers/LG-02125-*` and `docs/open-questions.md` OQ-2128; read at origin/main `edad3ec0dacf`. Not run here: this file adds no measurement beyond the row's.

## Disposition

Register decision, per the row (WK-2113, phase 3): **deferred with an owner: WK-2113** (carried with a named owner, CLAUDE.md §14); the event that next discharges it: the decision on OQ 2128, then the slice that implements it.
