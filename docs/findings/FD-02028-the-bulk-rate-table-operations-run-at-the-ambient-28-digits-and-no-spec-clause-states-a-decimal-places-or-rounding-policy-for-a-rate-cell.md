---
id: FD-2028
family: finding
title: The bulk rate-table operations run at the ambient 28 digits and no spec clause states a decimal-places or rounding policy for a rate cell
status: closed
created: 2026-11-06   # original date 2026-11-05, set at the draft; working id 8383, minted 2026-11-06
owner: lead
tree: cded9f0e1953f2db6a6a1375892257a1a4822fc3   # origin/main when drafted; the measurements ran on cda3c0dc of sl-8345-r2-cell-hard-error
corrected_by: []
relates: [WK-1178, OQ-2035, FD-1783, OQ-1784, PL-2083, SL-2084, LG-2098, FR-2082]
---

# FD-2028 — the bulk rate-table operations run at the ambient 28 digits; no spec clause states a dp or rounding policy for a rate cell

*(Minted 2026-11-06 as FD-2028 from working id 8383, in the docs batch 12 PR.)*

## Finding

**MEDIUM, owner WK-1178. No fix in R2; no code before the decision (to-lead "2026-11-05 16:33:41 GMT" item 2).** `uplift_table`, `uplift_by_filter` and `rebase_to_level` (`packages/pricing-core/src/pricing_core/rate_tables/operations.py`) compute `old * factor` and `old / reference` in the **ambient** decimal context (28 significant digits, half-even; no `localcontext`, no `quantize`; production runs the default context and none is set in `rate_tables`). A result wider than 28 digits is rounded inside the arithmetic and the rounded text is stored. `floor_and_cap` does no arithmetic. `docs/specs/03-rating-engine.md` and `04-optimisation.md` state no dp or rounding policy for a rate cell at all: FR-233 gives the four operations and that each records its parameters, nothing more. That is a design choice the specs leave open, and an actuarial one (CLAUDE.md §0); it is raised as **OQ-2035**, not decided here.

**Today's behaviour, stated:** exact to the ambient precision, then a coded refusal (`RATE_TABLE_CELL_UNPARSEABLE`) when the rounded text has more than 28 decimal places or a mantissa the engine cannot read.

## Evidence

Measured by the data-modelling seat on `cda3c0dc`, DB-free, with the real operations and `cell_parses`: `~/gi-pricing-plan.local/scratch/sl8345f/measure_precision.py`, `measure_factor_digits.py`; `~/gi-pricing-plan.local/scratch/dm-fd8383/measure_rule.py` (output `measure_rule.out`).

- **Size of the rounding.** About 1e-28 relative (7.8e-29 to 3.9e-28 at the first rounded step). No money effect.
- **What is reached is the refusal.** **Step 1:** one rebase refuses an ordinary cell when the non-terminating quotient is below 0.1 (its 28 significant digits need 29 dp). Cells 0.05, 1, 1.5 on base 25–29 refuse `'0.03333333333333333333333333333'`. No compounding is needed. The direction is coded and visible, the safe one: no mispricing.
- **Seeded freMTPL2 tables: 0 of 56 (table, base) pairs refused.** The widest max/min ratio is 1.95. A table reaches the case when its max/min passes 10; `03` §4.2's own example bounds (0.2 to 5.0) allow 25.
- **Compounding, slower:** from four digits, a ×1.0375 uplift is first rounded at step 7 and ×1.05 at step 13; from 0.0123 the refusal is at step 7 for ×1.0375 and step 13 for ×1.05. A cell seeded from a GLM carries up to 17 digits and is first rounded sooner.
- **Stored text depends on the caller's ambient context:** inside `localcontext(prec=400)` the same operation stored the exact product.

## Judgement (marked, not measured)

**Whether a real table reaches these step counts or a max/min above 10 is JUDGEMENT, not a measurement.** A rate reviewed quarterly at 1.05 from four digits does not reach step 13 soon, and this record does not claim otherwise. No deployed store was read.

## Disposition

Open, owner WK-1178. **The decision is the user's** (it sets how rates are rounded): OQ-2035 carries the options and a recommendation to the §14 review of Mon 16 Nov 2026; if undecided, the P2 closure record carries it by name. Rulings: to-lead "2026-11-05 16:33:41 GMT" and "2026-11-05 17:20:30 GMT" (sizing corrected to step 1, MEDIUM stands). Related, not the same: FD-1783 / OQ-1784 ask for a declared precision at a fit's materialisation. Filed as working id 8383.

*(Decided 2026-11-08 by the plan's hand-off (PL-2083): decided D, `to-lead.md` 2026-11-07 23:22:37 GMT, corrected 23:29:34; fixed by SL-2084, or carried to Phase 3 by name.)*

***Resolved 2026-11-08*** — closed in place 2026-11-08 by the executor, as the closing act of the mint of SL-2084 (WK-1178, LG-2098, PL-2083; this PR's number, squash commit and merge date: <at merge>), on the lead's brief, from the audit of SL-2084 adopted by the lead (from-lead "2026-11-08 00:13:01 GMT"; the audit section is in LG-2098). The decision: option D, `to-lead.md` "2026-11-07 23:22:37 GMT", corrected "2026-11-07 23:29:34 GMT"; OQ-2035 is DECIDED in both mirrors. Delivered remedy: `uplift_table`, `uplift_by_filter` and `rebase_to_level` compute the exact result and round it once, half-even, in a context the operation states (precision 28, places 28), never the caller's; the bulk-operation record carries that context (FR-2082). Red first by cause in LG-2098 (R1 `4 failed, 120 passed`; the record red `6 failed, 122 passed`), conditions C1–C3 met, and the 28-digit refusal of a cell below 0.1 no longer arises. Gate evidence: LG-2098 (gate END `2026-11-08T05:27:14+00:00`, `rc=1`, standing under item 31 with one test-only fix, `f6fa7d18`; its green is the slice PR's python CI at the merged head).
