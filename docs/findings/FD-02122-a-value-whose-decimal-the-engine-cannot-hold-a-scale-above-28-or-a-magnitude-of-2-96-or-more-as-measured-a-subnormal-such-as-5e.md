---
id: FD-2122
family: finding
title: "A value whose decimal the engine cannot hold (a scale above 28, or a magnitude of 2^96 or more, as measured: a subnormal such as `5e-324`, the smallest normal double, `1e-29`, `1e29`) passed FR-273's guard and failed in the engine as `RATING_EVALUATION_FAILED`, a 500 `INTERNAL_ERROR` at the route, an internal error for a caller's input"
status: active
created: 2026-11-13
owner: auditor
tree: edad3ec0dacf
corrected_by: []
relates: [WK-2113, SL-2118, LG-2119, FR-273, FD-1671]
---

# FD-2122 — A value whose decimal the engine cannot hold (a scale above 28, or a magnitude of 2^96 or more, as measured: a subnormal such as `5e-324`, the smallest normal double, `1e-29`, `1e29`) passed FR-273's guard and failed in the engine as `RATING_EVALUATION_FAILED`, a 500 `INTERNAL_ERROR` at the route, an internal error for a caller's input

*Filed late, 2026-11-14, by WK-2113 S1's mint (SL-2124): S2's mint (merge 112, #1490) recorded this finding as a register row only; this file adds no content beyond that row and S2's records.*

*Working id 8445, allocated by lead 34; minted as FD-2122 (WK-2113 S2). This document files, as a finding file, the register row that carried the finding as a row only. Every statement below is the register row's, quoted; nothing is added to it.*

## Finding

Per the register row (`docs/findings/register.md`, the row ending "(FD 2122)"), severity and source: **LOW**, from the maintainer's (by delegation) entries "2026-11-13 20:56:28 GMT" and "2026-11-13 21:00:31 GMT" (S2 round 3): found by the S2 seat's red run at `ccdafcc8`; the engine's decimal (`ScaleExceedsMaximumPrecision`; a bare error on the large side) fails every float outside scale <= 28 and magnitude < 2^96, which includes the subnormals the 20:56:28 ruling named and the smallest normal double it said would price. No value that priced is affected. `backend/tests/test_score_decimal_input_http.py`, `packages/pricing-core/tests/test_rating_score_engine_decimal_limits.py`.

## Evidence

Locators are those the register row names, and `docs/ledgers/LG-02119-*` and FR-273's dated clauses in `docs/specs/03-rating-engine.md`; read at origin/main `edad3ec0dacf`. Not run here: this file adds no measurement beyond the row's.

## Disposition

Register decision, per the row (WK-2113, phase 2): ***Resolved 2026-11-13*** — filed and closed in the same PR: fixed by SL 2118 round 3 (the guard refuses the engine's own predicate with `INPUT_CONTRACT_VIOLATION`, 422, naming the key path; the two limits are pinned to the engine by a both-direction property test; FR-273's dated line in `docs/specs/03-rating-engine.md`, and `docs/ledgers/LG-02119-wk-2113-slice-sl-2118-fd-1671-the-score-routes-refuse-what-core-refuses-slice-ledger.md`). The lead fills the merge sha at the PR's read-back. Filed under working id 2122.
