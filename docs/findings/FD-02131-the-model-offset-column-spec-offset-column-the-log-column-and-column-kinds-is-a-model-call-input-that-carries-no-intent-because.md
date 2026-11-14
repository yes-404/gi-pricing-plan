---
id: FD-2131
family: finding
title: "The model offset column (`spec.offset.column`, the `log_column` and `column` kinds) is a `model_call` input that carries no intent, because an intent belongs to a Factor and a column is not one"
status: active
created: 2026-11-13
owner: auditor
tree: edad3ec0dacf
corrected_by: []
relates: [WK-2113, SL-2124, LG-2125, FD-1495, OQ-2128, FR-240]
---

# FD-2131 — The model offset column (`spec.offset.column`, the `log_column` and `column` kinds) is a `model_call` input that carries no intent, because an intent belongs to a Factor and a column is not one

*Working id 8444, allocated by lead 34; minted as FD-2131 (WK-2113 S1). This document files, as a finding file, the register row that carried the finding as a row only. Every statement below is the register row's, quoted; nothing is added to it.*

## Finding

Per the register row (`docs/findings/register.md`, the row ending "(FD 2131)"), severity and source: **Candidate LOW, UNPROBED**: raised as cell G6 of `scratch/aud-intent/sweep.md` (aud-intent, not in the repository), ruled "mention in G3's ruling" by the lead (R3, "2026-11-13 19:53:34 GMT" entry, `to-lead.md`). `compile.py` `_model_slugs` adds `spec.offset.column` to the accepted `feature_map` values, the save check in `rating_algorithms.py` does the same, and predict applies the column to the linear predictor. A price moves with it only if an author offsets by a year-of-account column; no probe has been run and none is claimed. Same family as OQ 2128's decision on intent over a column.

## Evidence

Locators are those the register row names, and `docs/ledgers/LG-02125-*` and `docs/open-questions.md` OQ-2128; read at origin/main `edad3ec0dacf`. Not run here: this file adds no measurement beyond the row's.

## Disposition

Register decision, per the row (WK-2113, phase 3): **deferred with an owner: WK-2113** (carried with a named owner, CLAUDE.md §14); the event that next discharges it: the decision on OQ 2128, which this row waits on.
