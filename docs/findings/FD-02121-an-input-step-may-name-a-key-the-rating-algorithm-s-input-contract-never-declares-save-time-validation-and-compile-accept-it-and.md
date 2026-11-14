---
id: FD-2121
family: finding
title: "An `input` step may name a key the Rating Algorithm's input contract never declares: save-time validation and compile accept it and the algorithm prices on it"
status: active
created: 2026-11-13
owner: auditor
tree: edad3ec0dacf
corrected_by: []
relates: [WK-2113, SL-2118, LG-2119, OQ-2120, FR-213, FR-212, FR-273]
---

# FD-2121 — An `input` step may name a key the Rating Algorithm's input contract never declares: save-time validation and compile accept it and the algorithm prices on it

*Filed late, 2026-11-14, by WK-2113 S1's mint (SL-2124): S2's mint (merge 112, #1490) recorded this finding as a register row only; this file adds no content beyond that row and S2's records.*

*Working id 8442, allocated by lead 34; minted as FD-2121 (WK-2113 S2). This document files, as a finding file, the register row that carried the finding as a row only. Every statement below is the register row's, quoted; nothing is added to it.*

## Finding

Per the register row (`docs/findings/register.md`, the row ending "(FD 2121)"), severity and source: **MEDIUM candidate**, from the maintainer's (by delegation) entry "2026-11-13 20:34:11 GMT" (S2 question (a)): after SL 2118 no precision loss remains through it (FR-273 now guards every numeric key), but an algorithm can price on an input the contract does not declare, which FR-213's typed-input promise does not expect. `authored.py:60` says the key must be declared in a comment only; FR-212's producer check is satisfied by the input step itself. `packages/pricing-core/tests/test_rating_score_undeclared_input_precision.py::test_save_time_validation_lets_an_input_step_name_an_undeclared_key` pins the path.

## Evidence

Locators are those the register row names, and `docs/ledgers/LG-02119-*` and `docs/open-questions.md` OQ-2120; read at origin/main `edad3ec0dacf`. Not run here: this file adds no measurement beyond the row's.

## Disposition

Register decision, per the row (WK-2113, phase 2): **deferred with an owner: WK-2113**, not fixed in S2; the decision is `OQ-2120` (the maintainer's recommendation: REFUSE AT SAVE AND COMPILE). Filed under working id 2121.
