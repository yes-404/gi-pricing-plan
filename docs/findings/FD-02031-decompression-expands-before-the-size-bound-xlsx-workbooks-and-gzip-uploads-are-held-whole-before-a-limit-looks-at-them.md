---
id: FD-2031
family: finding
title: Decompression expands before the size bound - XLSX workbooks and gzip uploads are held whole before a limit looks at them
status: active
created: 2026-11-06   # original date 2026-11-05, set at the draft; working id 8386, minted 2026-11-06
owner: lead
tree: e75e0f1a   # read, not run; origin/main when drafted is cded9f0e1953f2db6a6a1375892257a1a4822fc3
corrected_by: []
relates: [FR-450, WK-1178]
---

# FD-2031 — decompression expands before the size bound (DP-A3)

*(Minted 2026-11-06 as FD-2031 from working id 8386, in the docs batch 12 PR.)*

## Finding

**LOW, owner WK-1178** (DP-A3 of the SL 8325 audit; draft `~/gi-pricing-plan.local/scratch/aud-sla/DP-A3-low-fd.md`, proposed LOW by the auditor, severity and owner to be ruled by the lead). FR-450's request-body limit (SL 8325) bounds the compressed bytes on the wire only. (1) `gzip.decompress` in `backend/src/app/data/formats.py:48-50` expands the whole payload before `_refuse_if_oversized` (`MAX_DECOMPRESSED_BYTES`, 2 GiB, `:42`, `:61-68`) compares it, so a .gz of at most 64 MiB can allocate its full expansion first. (2) An XLSX workbook is a zip; the core parser reads it whole and no expansion bound exists.

Both are reachable only through the two capped routes, by an authenticated caller holding `rating:*` or data permission (the 413 refusal runs before auth, the expansion after it).

## Evidence

The lines named above, read at `e75e0f1a`, not run.

## Not measured

Memory at any size; no reproduction was run. This was read at `e75e0f1a`, not run.

## Severity

**LOW.** Authenticated, and the 64 MiB cap shrinks the input; the harm is memory pressure on an api process with no `mem_limit` (`deploy/docker-compose.yml:124-155`), not wrong output or data loss.

## Disposition

Open, owner WK-1178. Event that next discharges it: a merged change that bounds the expansion (streamed decompression with a running cap; a workbook entry-size check) with a red-first test of a small file that expands past the cap, or a dated ruling accepting the absence. Related, not yet minted (space form): SL 8325. Filed as working id 8386.

*(Dated line, 2026-11-07, docs batch 16, by the executor, on the lead's residue list for slice A (from-lead "2026-11-07 20:44:10 GMT"): the working id `SL 8325` cited at lines 19 and 37 above is now **SL-2075** (PL-2074, LG-2076), merged as #1456. Those lines are not edited.)*
