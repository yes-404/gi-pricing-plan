---
id: FD-1815
family: finding
title: Existing rate tables may hold non-finite values saved before FR-234 refused them, and nothing has counted them
status: active
created: 2026-10-18   # filed 2026-10-18 under working id 8118; minted 2026-10-18
owner: auditor
tree: 79f1dede2d24d2c21871372fcc53515bd2c532a5
corrected_by: []
relates: [WK-1178, FD-1803, SL-1810, PL-1809]
---

# FD-1815 — Existing rate tables may hold non-finite values saved before FR-234 refused them

## Finding

**Severity MEDIUM, owner auditor, work item WK-1178, due before the P2 code freeze (Wed 4 Nov 2026)** (the maintainer, to-lead "2026-10-18 15:22:32 BST", Q1). MEDIUM and not HIGH because in P2 the only stores are dev/demo databases and #1341 stops new writes.
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

## Escalation (ruled, 15:22:32 BST Q1)

- If the census finds ANY stored non-finite rate-table value, this finding becomes **HIGH** (a NaN premium is a silent mispricing), and a remedy (refuse at load, or a data migration with a dated note) is owed before the P2 close.
- If it finds none, the finding closes with the census query, its count and the databases it ran on quoted.

## Disposition

Deferred with an owner: auditor (WK-1178), due before the code freeze. The event that next discharges it: the census run against a live database with its query, count and databases quoted, then the Escalation above. Filed under working id 8118.
