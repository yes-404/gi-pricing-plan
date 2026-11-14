---
id: FD-1802
family: finding
title: Both upload routes (rate-table import, source preview) declare 413 and read the whole body with no size cap
status: closed
created: 2026-10-18   # filed 2026-10-17 under working id 8105; minted 2026-10-18 as FD-1802
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, FD-1803, SL-2075, LG-2076, PL-2074, FD-2031]
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

*(Dated line, 2026-11-05, docs batch 11, by the auditor, on to-lead "2026-11-05 10:20:55 GMT" (plan A, DP-A1): a fact this record did not read: the proxy. `deploy/lb.conf` has no `client_max_body_size` (`grep -rn client_max_body_size deploy` at this tree: 0 hits), so nginx's default of 1 MiB applies and the proxy answers an over-size body with its own HTML 413 before the application's cap can. Ruled: the cap is a typed setting defaulting to 64 MiB on both routes, and the nginx limit in `deploy/lb.conf` and in the new frontend configuration is the same limit plus a small margin.)*

***Resolved 2026-11-07*** — closed in place 2026-11-07 as the closing act of the mint of SL-2075 (WK-1178, LG-2076, PL-2074; this PR; its number, squash commit and merge date are written at the merge's date-of-record), in the FD-1842 form. Delivered remedy: one request-body limit on both upload routes, the typed setting `max_upload_body_mib` (`GIP_MAX_UPLOAD_BODY_MIB`, default 64 MiB), enforced by `BodyLimitMiddleware` (`backend/src/app/api/body_limit.py`) before any body is read when the length is declared and on passing the limit when it is not, answering the declared 413 `PAYLOAD_TOO_LARGE` as an RFC 9457 problem with the request's `trace_id`; the proxy limit in `deploy/lb.conf` and `deploy/frontend.nginx.conf` is the same limit plus 1 MiB (`65m`), so the proxy never answers first. Red first, by cause, in LG-2076: `test_api_body_limit.py` red at `ebe2527a` (`3 failed, 2 passed`, `assert 200 == 413`), green at `d2490e18`; the proxy test red at `a029e461` (`deploy/lb.conf sets no client_max_body_size`), green at `0ecf4935`; A7's runtime limb passed at `8cf89fdc` (`1 passed in 132.19 s`: a 2 MiB body is not a 413, limit + 1 byte is the API's 413 `application/json`). What DP-A3 left out is not delivered here: XLSX decompression expansion and gzip's expand-first are bounded by neither limit, and are filed as FD-2031 (LOW, owner WK-1178). Gate evidence is in LG-2076: the SOLO gate at `28f15e11`, 14 pytest failures = item 31's 13 docs-audit failures plus the census entry in `test_worker_raise_sites.py` that the mint's first commit `14571939` adds.
