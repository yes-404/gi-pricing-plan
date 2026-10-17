---
id: FD-8105
family: finding
title: The rate-table import route declares 413 and reads the whole upload with no size cap
status: active
created: 2026-10-17
owner: auditor
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
corrected_by: []
relates: [WK-1178, FD-8106]
---

# FD-8105 — The rate-table import route declares 413 and reads the whole upload with no size cap

## Finding

**MEDIUM; owner WK-1178; verdict deferred with an owner (no slice yet).** Authority: the lead's
verdict on SL-1547's audit (A2, `from-lead-2026-10-09.md`, "Lead VERDICT on SL-1547's audit").
Pre-existing on `main`; not SL-1547's. `POST /api/v1/rate-tables/{slug}@{version}/import` lists
`413` among its documented problems but nothing in the path can return it: the handler buffers the
entire upload in memory, then parses it.

## Evidence

All read at `origin/main` 9469721db3d26480824cc1d715da2ec4ca9044d0.

- **Declared:** `backend/src/app/api/rate_tables.py:272`, `**problems(401, 403, 404, 413, 422)`.
- **Uncapped read:** `backend/src/app/api/rate_tables.py:307`, `content = await file.read()`. The
  only guard before it is the filename length (:297-305). `import_preview`
  (`backend/src/app/platform/rate_tables.py:884`) then hands the bytes to `import_from_csv` /
  `import_from_xlsx`; `grep -n -E 'read_tabular|_decompress' ` over `backend/src/app/api/rate_tables.py`
  and `backend/src/app/platform/rate_tables.py` finds no use of the datasets size guard.
- **The comparison the lead named, corrected:** the datasets upload reads the same way
  (`backend/src/app/api/datasets.py:241`, `await file.read()`), but its parser, `read_tabular`,
  refuses a *decompressed* payload over `MAX_DECOMPRESSED_BYTES` (2 GiB, `backend/src/app/data/formats.py:42`;
  `_refuse_if_oversized` :60-69 raises a 413). That is a cap on expansion, not on the raw upload, and
  it does not apply to the rate-table route at all. No request-size middleware was found:
  `git grep -n -i 'content-length\|max_request\|body_size\|client_max' origin/main -- backend/src`
  returned no hit. A reverse proxy limit, if any, is outside the repository and was not read.
- **Not measured:** memory use or latency at any upload size; whether an XLSX (a zip) expands
  beyond the raw size inside `import_from_xlsx`. This record asserts the missing cap, not a harm figure.

## Options (none picked)

- Cap the raw read in the route (stream with a limit, or check `Content-Length` and the bytes read) and
  return the declared `413`.
- Also bound XLSX expansion in the core parser.
- Specify the limit first: no spec in `docs/specs/03-rating-engine.md` states a rate-table import size.

## Disposition

Deferred with an owner: WK-1178; no slice yet. The event that next discharges it: a merged change
that returns 413 past a stated limit, or a dated ruling accepting the absence. Filed under working id 8105.
