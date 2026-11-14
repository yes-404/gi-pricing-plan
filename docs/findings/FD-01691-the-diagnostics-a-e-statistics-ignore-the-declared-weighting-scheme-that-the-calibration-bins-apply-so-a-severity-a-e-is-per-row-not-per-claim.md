---
id: FD-1691
family: finding
title: The diagnostics' A/E statistics ignore the declared weighting scheme that the calibration bins apply, so a severity A/E is per row, not per claim
status: closed
created: 2026-10-12
owner: auditor
tree: 50bbdd96b2154cb4eb79ccf91658191e51ab8906
corrected_by: []
relates: [WK-1178, SL-1543, SL-1675, PL-1674, SL-2045, LG-2046, PL-2044, FR-171, FR-183, FR-184, FR-186, FR-111, OQ-1692]
---

# FD-1691 — a statistic inconsistent with its own declared scheme

*(Minted 2026-10-12 as FD-1691 from working id 9889, in the D14 batch mint PR, on the lead's from-lead entry "2026-10-12 07:57:35 BST" (`~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`). The question this finding raises is `OQ-1692`, minted in the same batch from working id 9891. The working ids remain only in quoted entries.)*

Filed from the maintainer's (by delegation) entry "2026-10-12 05:39:20 BST — SL-1543 severity block: (i) a small PRECEDING WK-1178 slice ACCEPTED; the diagnostics finding is RESTATED (your "actual weighted, expected not" does not match the code); S4 beat-as-fixture reading OK" (`~/gi-pricing-plan.local/channel/to-lead.md`, a local file cited by entry header). That entry restates a finding an earlier brief had worded differently. Every `file:line` below was read at `origin/main` `50bbdd96b2154cb4eb79ccf91658191e51ab8906` on 2026-10-12, in `packages/pricing-core/src/pricing_core/modelling/diagnostics.py`.

## Finding

**Severity MEDIUM, owner WK-1178** (the maintainer (by delegation): "File it MEDIUM (a statistic inconsistent with its own declared scheme; not shown wrong against a spec), owner WK-1178."). The maintainer's restatement, verbatim:

> *"THE FINDING, RESTATED. I read diagnostics.py at main:*
> *- _partition :358-363: y = the raw response, ae_overall = Σy / Σmu, BOTH UNWEIGHTED;*
> *- by-level A/E :373-374: both unweighted;*
> *- calibration :408: divides by bin_exposure (weighted, via _weights :131-138).*
> *So "actual weighted, expected unweighted" is NOT what the code does. The real defect is that the declared weighting scheme (_weighting :124-128, claim count for severity) is applied to SOME statistics (calibration) and not others (A/E overall and by level). For severity, A/E is per ROW, not per CLAIM, so a book where claim counts vary per row reads a different A/E than an actuary's Σw·y/Σw·μ. FR-183 is silent on weighting."*

## Evidence

- `diagnostics.py:118-129`, `_weighting`: the scheme is `EXPOSURE` when the offset is a column, `CLAIM_COUNT` when a weight column is declared (severity's convention, `CLAUDE.md` §7), else `COUNT`. It is recorded on the partition at `:444` (`weighting=scheme`).
- `diagnostics.py:132-139`, `_weights`: the per-row weight that scheme implies (the offset column, else the weight column, else ones). `_partition` binds it as `exposure` at `:358`.
- `diagnostics.py:357,361-363`: `y` is the raw response, `ae_overall = Σy / Σmu`, with no weight in either sum.
- `diagnostics.py:373-374`: the by-level A/E is `Σy[mask]` over `Σmu[mask]`, with no weight in either.
- `diagnostics.py:406,408`: the calibration bins divide `Σy[mask]` and `Σmu[mask]` by `bin_exposure = Σexposure[mask]`, the weighted sum. Calibration is the one statistic that applies the declared scheme.
- `docs/specs/02-modelling.md` FR-171 calls the A/E "exposure-weighted", and FR-184 requires each metric to be recorded "with their weighting scheme explicit". FR-183 (train and holdout side by side) says nothing about weighting. The code's A/E is the ratio of two unweighted sums, whatever the scheme recorded beside it says.

## Disposition

**Owner WK-1178.** The question of which A/E the platform defines (per row, or weighted by the declared scheme) is `OQ-1692`, with options and a recommendation; the spec text follows by ruling, not by this finding. The maintainer's instruction: "The (i) slice fixes ONLY the weight-0 exclusion. It does NOT change the A/E definition, so it does not pre-empt the OQ." So the weight-0 slice (`SL-1675`, planned in `PL-1674`; the FR-111 clause) leaves these statistics as they are. Event that next confirms or discharges it: a ruling on `OQ-1692` applied to FR-171/FR-183 and to `_partition`, with a test that a severity book whose claim counts vary per row reads the weighted A/E. Filed by the minter from the entry, 2026-10-12.

***Resolved 2026-11-05*** — closed in place 2026-11-06 by the executor, as the closing act of the mint of SL-2045 (WK-1178, LG-2046, PL-2044; ~~this PR; its number, squash commit and merge date are written at the merge's date-of-record~~ [this PR; its number, squash commit and merge date are written at the merge's date-of-record]; slice head gated `c27f1e48`, tree `1c6be07f`), on the lead's brief under the maintainer's (by delegation) entry "2026-11-05 11:55:25 GMT" (`to-lead.md`, a local channel file), OQ-1692 ruled (b) as corrected, and the GO for slice M. Delivered remedy: `ae_weights` (`pricing_core/modelling/diagnostics.py`), the model's declared weight column else 1, is the weight of the A/E, so A/E = Σw·y / Σw·μ overall and by level; the by-level interval under a weight column is `ratio·z/√Σw`; `comparison.py`'s `ae_overall` takes the same `ae_weights`, so one model prints one A/E on the Diagnostics page and in the comparison. `_weights` and `_weighting` are unchanged (calibration, lift, deviance and Gini do not move). A frequency model's A/E is unchanged by construction (w = 1; `mu` already carries exposure). Red first, by cause, in LG-2046: at `ffd7101a` T1 `0.9772727272727273` against `22400/22000 = 1.018181818181818`, T3 `1.0` against `0.7368421052631579`, T4 `3000.0` against `19000`, T5 `(0.964, 1.036)` against `(0.380, 1.620)`, `4 failed, 1 passed, 31 deselected`; T2, the frequency guard, green at base and head and red under the `_weights` mutation (`3 failed, 33 passed`); T6 (comparison) `0.9808003017095513` against `0.9810919563411584` at the base source, `12 passed` at the head. `02-modelling.md` FR-171, FR-183 and FR-184 carry dated lines and OQ-1692 is DECIDED in both mirrors, the same wording. Gate evidence is in LG-2046: the DB window of 2026-11-05 17:12:21 to 17:18:00 GMT (seven backend files, rc 0 each, no value moved) and the SOLO gate the paired gate on `c27f1e48` (`13 failed, 7205 passed, 27 skipped`, the 13 all in the item-31 set; frontend half rc 0) and the seeded demo re-run (PASS, 1563 s, dislocation #1 590 s; D7's total and both attribution limbs equal on the 19985-policy sample). Not closed by this slice: stored diagnostics are not rewritten (FR-170, G4); a rehearsal or demo figure for a severity A/E fitted before the merge is a different number from one fitted after it.
