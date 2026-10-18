---
id: FD-8118
family: finding
title: Existing rate tables may hold non-finite values saved before FR-234 refused them, and nothing has counted them
status: active
created: 2026-10-18   # filed 2026-10-18 under working id 8118
owner: auditor
tree: 79f1dede2d24d2c21871372fcc53515bd2c532a5
corrected_by: []
relates: [WK-1178, FD-1803, SL-1810, PL-1809]
---

# FD-8118 — Existing rate tables may hold non-finite values saved before FR-234 refused them

## Finding

**Severity MEDIUM, proposed by the auditor (the ruling gave none; the lead gives the verdict). Owner auditor (ruled); work item WK-1178.**
Source: the maintainer's entry "2026-10-18 12:18:08 BST" (`to-lead.md`), item 2: "The live-DB census of
existing rate tables for non-finite values: ONE FD, owner auditor, in D22. It needs a live database,
not a slice gate."

FD-1803 closed the write side: SL-1810 (#1341, merge commit `c1a9c430`) makes `_value_issue` refuse
NaN, sNaN and infinities as a named `OUT_OF_BOUNDS` issue. It does not touch rows already saved. Until
`c1a9c430` any non-finite value passed `validate_rate_table` (FD-1803), so a database that held rate
tables before that merge may hold a stored `NaN` or `Infinity` in a value column. A rate table's value
is a rating relativity; a stored non-finite value reaches the rating path. **No query has counted such
rows in any database.** This finding records that the count is owed; it does not claim any row exists.

## Evidence

At `c1a9c430` (tree `79f1dede`), read by the author:

- The refusal is write-side only: `packages/pricing-core/src/pricing_core/rate_tables/operations.py`
  `_value_issue` (new `is_finite()` branch) and `_index_rows`, which now raises a named
  `ValueError("OUT_OF_BOUNDS: …")` for a stored non-finite cell. The slice's test
  `test_a_diff_over_a_stored_non_finite_cell_is_named` shows the slice itself expects such rows.
- Cells are stored in two modes (`backend/src/app/platform/rate_tables.py`, `RateTableStorageMode`):
  `rows` (database) and `parquet` (a blob above the storage threshold). A census covers both.

## What the census must do

Count, per rate table version, value cells whose text does not parse to a finite `Decimal`
(`NaN`, `sNaN`, `Infinity`, `-Infinity`, in any case), over every database that has run a build from
before `c1a9c430` that still exists (a gate or demo database is dropped at its END, so those are
not reachable; which databases qualify is the census runner's to list and quote). Report table slug, version, storage mode and cell count; a
parquet version needs its blob read. It reads; it writes nothing. It needs a live database and is not a slice gate.

## Disposition

Deferred with an owner: auditor. The event that next discharges it: the census run against the live
database with its counts quoted (zero is a valid result), after which this row is set `closed`; a
non-zero count opens a remediation finding naming the tables. Filed under working id 8118.
