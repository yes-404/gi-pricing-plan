---
id: FD-2032
family: finding
title: Rebase and uplift on a money_minor or count column write a ratio or a fraction into a column in minor units, and nothing consults the value type
status: closed
created: 2026-11-06   # original date 2026-11-05, set at the draft; working id 8387, minted 2026-11-06
owner: lead
tree: cded9f0e1953f2db6a6a1375892257a1a4822fc3   # origin/main; measurements ran on cda3c0dc of sl-8345-r2-cell-hard-error
corrected_by: []
relates: [WK-1178, FR-228, FR-233, OQ-2035, FD-2028]
---

# FD-2032 — refusal by value type: a bulk operation on a column whose type gives the result no meaning

*(Minted 2026-11-06 as FD-2032 from working id 8387, in the docs batch 12 PR.)*

## Finding

**MEDIUM, owner WK-1178.** Rated MEDIUM by to-lead "2026-11-05 17:20:30 GMT", raised to HIGH at "17:29:19 GMT", **re-rated MEDIUM at "2026-11-05 17:45:56 GMT" (supersedes the HIGH)**: a **latent defect behind an unbuilt path**. `rebase_to_level` on a `money_minor` or `count` column writes a RATIO into a column declared in minor units (a cell of 12807 becomes about 1); `uplift_table` and `uplift_by_filter` on a `count` column write non-integers. The value type is not consulted anywhere (`_value_issue` has no branch on type; the engine reads the value declaration only for its `name`: `compile.py:844`, `runtime.py:275`). FR-228 declares four value types, so a refusal must exist before any route creates a non-relativity table.

## Why MEDIUM and not HIGH

The only `RateTableRow(` is in the seed path (`platform/rate_tables.py:201`), where `operations.py` declares RELATIVITY; edit and import carry `base.value`; `03` §5.1 has **no create route**. So **no shipped route creates a non-relativity table**: the measured case below needs a row written directly. `_new_version` / `default_row` is unreachable and ignored (the seed sets None, edit and copy carry it, nothing sets it, no `rating/` code reads it). `floor_and_cap` on a `count` column can give a non-integral result under the same limit.

## Evidence

Measured (M5, cda3c0dc, DB-free; `~/gi-pricing-plan.local/scratch/dm-fd8383/measure_types.py`)

A fee consumed at area F, a golden quote at C: F 18500 becomes 15001 with no automatic refusal, and the golden quote still passes (15000). **Kept as measured.** Limits: a constructed fee on a constructed algorithm; a user's own act; the submit, dislocation and approver steps are human stops and were **read, not run**; no real table is shown affected; seeded data is not affected. The error is of a type (orders of magnitude, unrefused), not a live incident. **Fractional money is contained:** a `money_minor` output is rounded once at the payable (`score.py:808-860`, dp 0); a cell 12807.9375 and a cell 12808 both give 14819.

## Proposed matrix (ACCEPTED by to-lead "2026-11-05 17:29:19 GMT")

Refused: `rebase` on `percentage`, `money_minor`, `count`; `uplift` and uplift by filter on `count`. Allowed: `rebase` on `relativity` only; `floor_and_cap` on all four types. Route: an FR-233 dated clause first (and a dated sentence that a rebase on relativity moves premiums unless the base rate offsets it), then the refusal at the operation, spec and code in one change, a coded refusal, red first on **every** matrix cell including the allowed ones, through the route.

## Not read

No deployed database was read for the value types actually stored. The seed-cell census gains a one-line read-only count of value types across the databases that exist (to-lead "17:45:56 GMT"); until it runs, there is no confirming read.

## Disposition

Open, owner WK-1178. Per DP-1 (b) of PL 8388, this record is filed by batch 12 because it landed before the fix slice (SL 8389); had SL 8389 landed first, its auditor would have filed it. Stacked on R2 if built in time; it may displace nothing in the chain. Filed as working id 8387.

***Resolved 2026-11-06*** — closed in place 2026-11-06 by the executor, on the lead's adoption of aud-sl8389 (`from-lead-2026-10-09.md` "2026-11-05 23:50:37 GMT"), as the closing act of the mint of SL-2041 (WK-1178, LG-2042, PL-2040; this PR; its number, squash commit and merge date are written at the merge's date-of-record), on the maintainer's entries "2026-11-05 17:20:30 GMT" and "2026-11-05 17:29:19 GMT" (`to-lead.md`, a local channel file; severity HIGH for the type of error, not a live incident). Delivered remedy: a bulk operation is refused where the column's declared value type gives its result no meaning. `pricing_core/rate_tables/operations.py` `_OPERATION_VALUE_TYPES` and `_check_value_type`, the first statement of each of the four operations: `rebase_to_level` runs only on `relativity`; `uplift_table` and `uplift_by_filter` are refused on `count`; `floor_and_cap` runs on all four (16 cells: 5 refused, 11 allowed). The refusal is 422 `BULK_OPERATION_NOT_APPLICABLE` (registered in `app/errors.py`, owned in `03` §5.1), naming the operation, the value type and `rate_table:<slug>@<version>`; no version is created; the refusal comes before the filter-key and the parquet checks. Spec and code are one change: `03` FR-233's dated clause, with "a rebase on a `relativity` column moves premiums unless the base rate offsets it" (no behaviour added) and the revisit trigger (a percentage rebase in real use lifts that one cell); `04` §4.4 points at it. A version stored before the clause keeps its cells (`00` FR-4); nothing replays a stored operation (`created_by_operation` is recorded, never re-run), so FR-239 is not in question; no rate set, nothing rounded, no price moved on a correct table. Reds in LG-2042: function level `5 failed, 103 passed` (`DID NOT RAISE ValueError`) at tests-only `0b718b91`; route level `5 failed, 11 passed`, each `assert 201 == 422`, in DB window `sl8389`; the 11 allowed cells shown red by plant P at both levels (`50 failed, 60 passed`; `11 failed, 5 passed`), P never committed; greens `170 passed` (function) and `16 passed` (route), whole `test_api_rate_tables.py` `98 passed`. Latent as filed: no route creates a column that is not `relativity` (`seed_from_model` is the only writer of a new table; import inherits the type), so the refusal was a guard on a path not yet built. The gate's decisive green and the merge are recorded at the merge (LG-2042 MERGE-ACK).
