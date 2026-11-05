---
id: FD-8386
family: finding
title: Decompression expands before the size bound - XLSX workbooks and gzip uploads are held whole before a limit looks at them
status: active
created: 2026-11-05   # working id 8386, minted at the batch 12 mint
owner: WK-1178
tree: e75e0f1a   # read, not run; origin/main when drafted is cded9f0e1953f2db6a6a1375892257a1a4822fc3
corrected_by: []
relates: [FR-450, SL-8325, WK-1178]
---

# FD-8386 — decompression expands before the size bound (DP-A3)

## Finding

**LOW, owner WK-1178** (DP-A3 of the SL 8325 audit; draft `~/gi-pricing-plan.local/scratch/aud-sla/DP-A3-low-fd.md`, proposed LOW by the auditor, severity and owner to be ruled by the lead). FR-450's request-body limit (SL 8325) bounds the compressed bytes on the wire only. (1) `gzip.decompress` in `backend/src/app/data/formats.py:48-50` expands the whole payload before `_refuse_if_oversized` (`MAX_DECOMPRESSED_BYTES`, 2 GiB, `:42`, `:61-68`) compares it, so a .gz of at most 64 MiB can allocate its full expansion first. (2) An XLSX workbook is a zip; the core parser reads it whole and no expansion bound exists.

Both are reachable only through the two capped routes, by an authenticated caller holding `rating:*` or data permission (the 413 refusal runs before auth, the expansion after it).

## Not measured

Memory at any size; no reproduction was run. This was read at `e75e0f1a`, not run.

## Severity

**LOW.** Authenticated, and the 64 MiB cap shrinks the input; the harm is memory pressure on an api process with no `mem_limit` (`deploy/docker-compose.yml:124-155`), not wrong output or data loss.

## Disposition

Open, owner WK-1178 (the lead's verdict on the owner is not in the staged line: **the lead confirms**). Event that next discharges it: a merged change that bounds the expansion (streamed decompression with a running cap; a workbook entry-size check) with a red-first test of a small file that expands past the cap, or a dated ruling accepting the absence. Filed as working id 8386.
