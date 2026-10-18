---
id: FD-1783
family: finding
title: The stored rate-table artifact is not byte-reproducible across identical seeds, so recompute-audit cannot match its bytes or content hash
status: active
created: 2026-10-17
owner: auditor
tree: cb5aa3228777ec86d272b2cd524e8071d6d275e7
corrected_by: []
relates: [WK-1178, SL-1543, FR-11, NFR-481]
---

# FD-1783 — The stored rate-table artifact is not byte-reproducible across identical seeds, so recompute-audit cannot match its bytes or content hash

*(Minted 2026-10-17 as FD-1783 from working id 8092, in the D20 batch mint PR.)*

## Finding

**MEDIUM; owner WK-1178; verdict proposed `deferred with an owner`** (the lead decides). The maintainer's ruling, relayed by the lead's brief of 18:30:08 BST on 2026-10-17: "NFR-481 is FR-11's measurable form for fits (coefficients identical to 1e-10), and Δ ~1e-16 is well inside it, so FR-11 is MET. What fails is the STORED ARTIFACT's byte-reproducibility: the same inputs give different rate-table bytes and content hash, which defeats recompute-audit."

Two full seeds of the same tree produce rate-table cell values that differ in the last one or two binary digits, so the persisted rate-table bytes, and the bundle `content_hash` that covers them, differ between runs of identical inputs. **FR-11 is met**: `00-overview.md` FR-11 asks for "identical outputs" given identical inputs and pinned versions, and `02-modelling.md` NFR-481 (read with its 2026-08-22 amendment, which names the GLM bound as `abs(Δestimate) <= 1e-10` per coefficient) is its measurable form for fits. A Δ of about 1e-16 sits six orders inside it. What fails is a different property: **a stored artifact that an auditor can recompute and compare byte for byte**. A recompute-audit that re-fits from the pinned inputs and compares hashes cannot match, so it must fall back to a tolerance compare, which is not what the stored hash promises.

**Whether any quote's rounded pence changes is UNMEASURED.** The cells differ at about 1e-16 relative; no rating run was compared across the two seeds.

## Evidence

**1. Two seeds, same tree** (`~/gi-pricing-plan.local/scratch/sl1543-hashdiff/`, `B.rows.json` and `C.rows.json`: ids-normalised dumps by `dump.py`, run by `window.sh`; B and C are two full seeds of the same tree, SL-1543's fix branch at `5e20ac65`). Re-derived by this auditor at worktree `docs-d20` HEAD `cb5aa3228777ec86d272b2cd524e8071d6d275e7` with `python3 -I ~/gi-pricing-plan.local/scratch/sl1543-hashdiff/rederive_d20c.py ~/gi-pricing-plan.local/scratch/sl1543-hashdiff`, which joins each `rate_table_cells` row to its `rate_table_versions` row and `rate_tables.slug`, and compares by `(slug, key)` using `Decimal`:

- `rate_table_cells`: 56 cells in B and in C; the `(slug, key)` sets are identical.
- Values differ in **40 of 56**; **max |Δ| = 4E-16**; **max relative Δ = 3.076162450620079547265415962E-16**.
- `fremtpl2-veh-age-band` `('0-1',)`: `1.9532561296454942` against `1.9532561296454938`.
- `fremtpl2-area` `('A',)`: `0.8891410278771941` against `0.889141027877194`.
- `fremtpl2-driv-age-band` `('18-31',)`: `1.3582053935989764` against `1.3582053935989762`.
- `bandings` rows are identical between B and C.

**2. Same diff, wider** (executor-jitter's `diff.py`, in the lead's session scratchpad, not re-run here; the script was no longer on disk at this audit and these figures are relayed, not re-derived): GLM coefficients differ by at most 1.8e-15; the bundle `content_hash` and blob bytes differ; the decile diagnostics differ (holdout gini by 3.6e-7, calibration actual by at most 1.1e-5), through rows changing decile bin at near-ties.

**3. Two-process probe** (lead's scratchpad `fitdet/`, run on `main` `9469721d`, threads unset, `nproc` 8, OpenBLAS 8 threads; `cmp.py` re-run by this auditor over the saved outputs): four GLM fits of one spec; max |Δcoef| against fit 1: `3.552713678800501e-15` (glm2), `6.661338147750939e-16` (glm3), `3.3306690738754696e-15` (glm4), 9 terms each, the intercept carrying the max in each; the XGBoost booster sha256 of two fits is **identical** (`gbm identical: True`). So the jitter is in the GLM solve (a thread-count-dependent BLAS reduction order is the natural suspect; this is a hypothesis, no probe varied the thread count), not in the boosters.

**4. Precision FR search** (`grep -rniE` over `docs/specs/` for relativity, rate-table or materialisation precision, decimal places, quantise, significant digits at `cb5aa322`): **no FR sets a precision for a materialised relativity or rate-table cell value.** FR-245 (`03-rating-engine.md`) fixes the Decimal context for monetary arithmetic (28 significant digits, `ROUND_HALF_EVEN`), which governs evaluation, not what a fit writes into a cell; FR-21 (`00-overview.md`) refuses a float at the exact-decimal types. The stored cell value is a string of a float's shortest repr (see the values above). A quantisation precision is therefore a design choice the specs leave open and goes to a P3 open question, **OQ-1784**.

## Notes: decile tie-breaking

The decile diagnostics (item 2) move by the same mechanism and are not a second defect: rows whose predictions are equal to within the 1e-15 jitter fall on either side of a decile edge depending on the run, so a bin assignment, and every aggregate over it, changes by a few rows. Whatever remedy is chosen for the cells, the decile assignment needs a deterministic tie-break (an explicit secondary sort key such as row id) or its inputs need the same quantisation; otherwise the diagnostics stay unreproducible even when the cells are not. The size observed (3.6e-7 and at most 1.1e-5) shows the effect is small and bounded by the bin sizes.

## Disposition

**Deferred with an owner: WK-1178**, Phase 3 timing as WK-1178 sets it. Remedy options, **not picked**:

- **(a)** Quantise relativities at materialisation to a declared precision, so that last-digit jitter cannot reach the stored bytes. The precision is OQ-1784, a P3 open question (no FR sets one; item 4). Risk to weigh: a quantisation edge can still split two near-equal values onto different sides, and the quantised value differs from the fit by up to the precision, which NFR-481 and FR-245 consumers must accept.
- **(b)** Make thread counts deterministic (pin BLAS and library threads for fits), so the reduction order is fixed. Cheaper to state, but it binds to library versions and CPU behaviour (an identical thread count on a different CPU or BLAS build need not give identical bits) and costs fit speed.

The event that next discharges it: a ruling or fix slice that picks a remedy, with a test that seeds twice and compares the stored rate-table bytes and content hash for equality (and, if tolerance is chosen instead, a spec change that says the artifact is reproducible to a tolerance and not byte for byte). The pence-impact measurement (a rating run over both seeds) is part of that slice's evidence.
