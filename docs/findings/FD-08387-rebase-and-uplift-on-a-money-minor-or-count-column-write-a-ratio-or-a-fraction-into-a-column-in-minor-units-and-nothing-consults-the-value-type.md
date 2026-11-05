---
id: FD-8387
family: finding
title: Rebase and uplift on a money_minor or count column write a ratio or a fraction into a column in minor units, and nothing consults the value type
status: active
created: 2026-11-05   # working id 8387, minted at the batch 12 mint
owner: WK-1178
tree: cded9f0e1953f2db6a6a1375892257a1a4822fc3   # origin/main; measurements ran on cda3c0dc of sl-8345-r2-cell-hard-error
corrected_by: []
relates: [WK-1178, FR-228, FR-233, OQ-8396, FD-8383]
---

# FD-8387 — refusal by value type: a bulk operation on a column whose type gives the result no meaning

## Finding

**MEDIUM, owner WK-1178.** Rated MEDIUM by to-lead "2026-11-05 17:20:30 GMT", raised to HIGH at "17:29:19 GMT", **re-rated MEDIUM at "2026-11-05 17:45:56 GMT" (supersedes the HIGH)**: a **latent defect behind an unbuilt path**. `rebase_to_level` on a `money_minor` or `count` column writes a RATIO into a column declared in minor units (a cell of 12807 becomes about 1); `uplift_table` and `uplift_by_filter` on a `count` column write non-integers. The value type is not consulted anywhere (`_value_issue` has no branch on type; the engine reads the value declaration only for its `name`: `compile.py:844`, `runtime.py:275`). FR-228 declares four value types, so a refusal must exist before any route creates a non-relativity table.

## Why MEDIUM and not HIGH

The only `RateTableRow(` is in the seed path (`platform/rate_tables.py:201`), where `operations.py` declares RELATIVITY; edit and import carry `base.value`; `03` §5.1 has **no create route**. So **no shipped route creates a non-relativity table**: the measured case below needs a row written directly. `_new_version` / `default_row` is unreachable and ignored (the seed sets None, edit and copy carry it, nothing sets it, no `rating/` code reads it). `floor_and_cap` on a `count` column can give a non-integral result under the same limit.

## Measured (M5, cda3c0dc, DB-free; `~/gi-pricing-plan.local/scratch/dm-fd8383/measure_types.py`)

A fee consumed at area F, a golden quote at C: F 18500 becomes 15001 with no automatic refusal, and the golden quote still passes (15000). **Kept as measured.** Limits: a constructed fee on a constructed algorithm; a user's own act; the submit, dislocation and approver steps are human stops and were **read, not run**; no real table is shown affected; seeded data is not affected. The error is of a type (orders of magnitude, unrefused), not a live incident. **Fractional money is contained:** a `money_minor` output is rounded once at the payable (`score.py:808-860`, dp 0); a cell 12807.9375 and a cell 12808 both give 14819.

## Proposed matrix (ACCEPTED by to-lead "2026-11-05 17:29:19 GMT")

Refused: `rebase` on `percentage`, `money_minor`, `count`; `uplift` and uplift by filter on `count`. Allowed: `rebase` on `relativity` only; `floor_and_cap` on all four types. Route: an FR-233 dated clause first (and a dated sentence that a rebase on relativity moves premiums unless the base rate offsets it), then the refusal at the operation, spec and code in one change, a coded refusal, red first on **every** matrix cell including the allowed ones, through the route.

## Not read

No deployed database was read for the value types actually stored. The seed-cell census gains a one-line read-only count of value types across the databases that exist (to-lead "17:45:56 GMT"); until it runs, there is no confirming read.

## Disposition

Open, owner WK-1178. Per DP-1 (b) of PL 8388, this record is filed by batch 12 because it landed before the fix slice (SL 8389); had SL 8389 landed first, its auditor would have filed it. Stacked on R2 if built in time; it may displace nothing in the chain. Filed as working id 8387.
