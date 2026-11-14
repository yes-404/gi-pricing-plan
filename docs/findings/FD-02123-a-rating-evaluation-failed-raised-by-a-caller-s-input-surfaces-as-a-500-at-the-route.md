---
id: FD-2123
family: finding
title: "A `RATING_EVALUATION_FAILED` raised by a caller's input surfaces as a 500 at the route"
status: active
created: 2026-11-13
owner: auditor
tree: edad3ec0dacf
corrected_by: []
relates: [WK-2113, SL-2118, LG-2119, FD-2122, FR-273]
---

# FD-2123 — A `RATING_EVALUATION_FAILED` raised by a caller's input surfaces as a 500 at the route

*Filed late, 2026-11-14, by WK-2113 S1's mint (SL-2124): S2's mint (merge 112, #1490) recorded this finding as a register row only; this file adds no content beyond that row and S2's records.*

*Working id 8446, allocated by lead 34; minted as FD-2123 (WK-2113 S2). This document files, as a finding file, the register row that carried the finding as a row only. Every statement below is the register row's, quoted; nothing is added to it.*

## Finding

Per the register row (`docs/findings/register.md`, the row ending "(FD 2123)"), severity and source: **LOW-to-MEDIUM candidate**, from the maintainer's (by delegation) entry "2026-11-13 21:00:31 GMT" (S2 round 3): the measured case is a value the engine's decimal cannot hold (FD 2122, fixed in S2 for that class). Other engine failures a caller can trigger (a `number(x)` of a non-numeric string, a division by a caller-supplied zero) may surface the same way; the severity is set by a sweep of which engine failures a caller can trigger. **Named limb** (the maintainer's message after the 21:10 status, 2026-11-13): a float handed directly to pricing-core bypasses the precision guard and fails in the engine as `RATING_EVALUATION_FAILED`; no wrong number. The sweep answers it with the caller-triggered 500s. **Second named limb** (delta review rev4-sl8432 D2, 2026-11-13): whether the engine ever priced a `NaN`, `Infinity` or `-Infinity` in an undeclared key a step reads is unmeasured; SL 2118 now refuses such a body with a 422, so the sweep also measures what the engine did with those constants before.

## Evidence

Locators are those the register row names, and `docs/ledgers/LG-02119-*` and FR-273's dated clauses in `docs/specs/03-rating-engine.md`; read at origin/main `edad3ec0dacf`. Not run here: this file adds no measurement beyond the row's.

## Disposition

Register decision, per the row (WK-2113, phase 2): **deferred with an owner: WK-2113**, not fixed in S2. Filed under working id 2123.
