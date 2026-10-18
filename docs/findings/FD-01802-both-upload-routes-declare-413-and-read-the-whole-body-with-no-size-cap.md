---
id: FD-1802
family: finding
title: Both upload routes (rate-table import, source preview) declare 413 and read the whole body with no size cap
status: active
created: 2026-10-18   # filed 2026-10-17 under working id 8105; minted 2026-10-18 as FD-1802
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, FD-1803]
---

# FD-1802 — Both upload routes declare 413 and read the whole body with no size cap

## Finding

**MEDIUM; owner WK-1178; verdict deferred with an owner (no slice yet).** Authority: the lead's
verdict on SL-1547's audit (A2, `from-lead-2026-10-09.md`, "Lead VERDICT on SL-1547's audit"),
widened to both routes by the maintainer (by delegation), to-lead 2026-10-17 22:56:37 BST.
Pre-existing on `main`; not SL-1547's. Two upload routes list `413` among their documented
problems, and both buffer the entire request body in memory (`await file.read()`) before any size
check; the only cap in the repository bounds the *decompressed* size, after the raw body is already in memory.

## Evidence

All read at `origin/main` 9469721db3d26480824cc1d715da2ec4ca9044d0.

- **Rate-table import** (`POST /rate-tables/{slug}@{version}/import`). Declared:
  `backend/src/app/api/rate_tables.py:272`, `**problems(401, 403, 404, 413, 422)`. Uncapped read:
  `backend/src/app/api/rate_tables.py:307`, `content = await file.read()`. The only guard before
  it is the filename length (:297-305). `import_preview` (`backend/src/app/platform/rate_tables.py:884`)
  then hands the bytes to `import_from_csv` / `import_from_xlsx`; it does not use the datasets
  size guard. Nothing in this path can return the declared 413.
- **Source preview** (`POST /sources/{source_id}/preview`, router prefix not resolved here). Declared:
  `backend/src/app/api/datasets.py:209`, `responses=problems(401, 403, 404, 413, 422)` — **yes, the
  datasets route decorator declares 413**. Uncapped read: `backend/src/app/api/datasets.py:241`,
  `frame = read_tabular(await file.read(), ...)`. Its 413 is reachable only through the parser's
  decompressed-size refusal (next bullet), never for the raw body.
- **The only cap is on expansion.** `read_tabular` refuses a *decompressed* payload over
  `MAX_DECOMPRESSED_BYTES` (2 GiB, `backend/src/app/data/formats.py:42`; `_decompress` :44-57 and
  `_refuse_if_oversized` raise 413). That bounds a `.gz` / `.zst` bomb after the raw bytes were
  read; it does not bound the raw upload and does not apply to the rate-table route at all.
- **No request-size limit exists.** `git grep -n -i 'content-length\|max_request\|body_size\|client_max' origin/main -- backend/src`
  returned no hit (re-run 2026-10-17 at the same tree). A reverse-proxy limit, if any, is outside
  the repository and was not read.
- **Not measured:** memory use or latency at any upload size; whether an XLSX (a zip) expands
  beyond the raw size inside `import_from_xlsx`. This record asserts the missing cap, not a harm figure.

## Options (none picked)

- **Fix direction (the maintainer's, by delegation, 2026-10-17 22:56:37 BST):** a request-size limit
  *before* the read — middleware, or a per-route streamed cap — returning the declared `413` on both routes.
- Also bound XLSX expansion in the core parser.
- Specify the limit first: no spec in `docs/specs/03-rating-engine.md` states a rate-table import size.

## Disposition

Deferred with an owner: WK-1178; no slice yet. The event that next discharges it: a merged change
that returns 413 past a stated limit on both routes, or a dated ruling accepting the absence.
Filed under working id 8105.

Widened 2026-10-17 to both upload routes (the maintainer, to-lead 2026-10-17 22:56:37 BST).
