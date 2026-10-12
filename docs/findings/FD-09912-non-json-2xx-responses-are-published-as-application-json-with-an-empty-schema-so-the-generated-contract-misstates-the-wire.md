---
id: FD-9912
family: finding
title: Non-JSON 2xx responses are published as application/json with an empty schema, so the generated contract misstates the wire
status: active
created: 2026-10-12
owner: auditor
tree: 50bbdd96b2154cb4eb79ccf91658191e51ab8906
corrected_by: []
relates: [FD-1335, PL-1364, SL-1367, WK-1178, WK-679, FR-235, FR-371, FR-451]
---

# FD-9912 — Non-JSON 2xx responses are published as `application/json` with an empty schema

*(Filed 2026-10-12 under working id 9912, reserved by the lead, from-lead "2026-10-12 07:29:15 BST"
(`~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`). Text drafted by the planner (seat
planner-import) on the lead's brief; the finding's owner field is the auditor's family default.)*

## Finding

**Severity: MEDIUM** (the maintainer's (by delegation) entry "2026-10-12 07:28:38 BST — S5 flags:
(1) NEITHER (a) nor (c): type POST …/import's 200 FIRST in a tiny WK-1178 slice (d), with
(a)+tripwire only as a named fallback; (3) the CONTRACT is wrong → FD MEDIUM, the class of non-JSON
routes", in `~/gi-pricing-plan.local/channel/to-lead.md`). Flag (3) of that entry, verbatim:

> The spec says "Export cells to CSV" (03 :1044, FR-235), and the wire sends text/csv, so the code's
> DECLARATION is wrong and the generated contract inherits it. The generated contract says
> application/json, empty schema, for /export/csv, /export/xlsx AND /api/v1/audit/export. It is the
> same class: a non-JSON route that never declares its media type.
> - FD MEDIUM: a published contract that misstates the wire breaks any generated client.
> - Owner WK-1178 for the two rate-table routes; the audit-export limb goes to the Work owning 06's
>   audit export (find it and cite the roadmap line; do not default).
> - Remedy: the routes declare their response media type, so the contract reads text/csv and the
>   xlsx MIME type. S5 stays unchanged: reading text is correct for the real wire.

The spec and the code agree on the wire; the **declaration** does not. Each route returns a
`Response` or `StreamingResponse` with an explicit `media_type`, but none declares it to FastAPI,
so the generated OpenAPI publishes FastAPI's default, `application/json` with `"schema": {}`. A
client generated from `docs/contracts/` (`CLAUDE.md` §2) then parses a CSV, a spreadsheet or a
stream as JSON. The frontend works today only because it bypasses the generated type: WK-675 S5
(`SL-1547`) reads the CSV export as text (`frontend/src/api/rateTables.ts` on `origin/sl-1547-wk675-s5`,
`exportCsv`, `responseType: "text"`), which is correct for the real wire and stays unchanged.

## Evidence

All at `origin/main` `50bbdd96b2154cb4eb79ccf91658191e51ab8906`.

### The class, swept over the whole contract

Every 2xx response in `docs/contracts/openapi/generated.json` whose media-type schema is exactly
`{}`, by this predicate, run from the repository root:

```bash
python3 -c "import json;d=json.load(open('docs/contracts/openapi/generated.json'));[print(m.upper(),p,k,media) for p,i in d['paths'].items() for m,op in i.items() if isinstance(op,dict) and 'responses' in op for k,v in op['responses'].items() if k.startswith('2') for media,s in v.get('content',{}).items() if s.get('schema')=={}]"
```

Output, verbatim (4 lines, over the contract's 823 responses):

```text
GET /api/v1/audit/export 200 application/json
GET /api/v1/jobs/{job_id}/events 200 application/json
GET /api/v1/rate-tables/{slug}@{version}/export/csv 200 application/json
GET /api/v1/rate-tables/{slug}@{version}/export/xlsx 200 application/json
```

**The ruling names three routes; the sweep finds four.** The fourth, the job-events SSE stream, is
the same class by the ruling's own definition ("a non-JSON route that never declares its media
type"). It is recorded here as limb 3, with no owner set (Disposition).

### The published contract, verbatim

`docs/contracts/openapi/generated.json`, each route's `"200"` block (the four blocks are identical):

| Route | Lines | Content |
|---|---|---|
| `GET /api/v1/rate-tables/{slug}@{version}/export/csv` | `:31985-31992` | `"200": { "content": { "application/json": { "schema": {} } }, "description": "Successful Response" }` |
| `GET /api/v1/rate-tables/{slug}@{version}/export/xlsx` | `:32088-32095` | the same |
| `GET /api/v1/audit/export` | `:19382-19389` | the same |
| `GET /api/v1/jobs/{job_id}/events` | `:27869-27876` | the same |

### What the code sends

| Route | Handler | Media type on the wire |
|---|---|---|
| `/export/csv` | `backend/src/app/api/rate_tables.py:220-238` (decorator `:220-224`: `summary`, `responses=problems(401, 403, 404)`, no `response_class`) | `return Response(content=content, media_type="text/csv")` (`:238`) |
| `/export/xlsx` | `rate_tables.py:241-263` (decorator `:241-245`, the same) | `media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"` (`:260-262`) |
| `/api/v1/audit/export` | `backend/src/app/api/audit.py:237-308` (decorator `:237-241`, no `response_class`; `format` query `csv`\|`json`, default `csv`) | `StreamingResponse(…, media_type="application/x-ndjson")` (`:278-280`) for `format=json`; `media_type="text/csv"` (`:306-308`) for `csv` |
| `/api/v1/jobs/{job_id}/events` | `backend/src/app/api/jobs.py:254-310` (decorator `:254-258`) | `StreamingResponse(…, media_type="text/event-stream")` (`:308-310`) |

### What the specs say

- `docs/specs/03-rating-engine.md:1044`: `` | `GET` | `/api/v1/rate-tables/{slug}@{version}/export/csv` | Export cells to CSV (FR-235) | ``;
  `:1045`: `… /export/xlsx` | `Export cells to XLSX (FR-235)`. **FR-235** (`03:128`): *"Rate tables can
  be exported to and imported from CSV/XLSX for offline work, with a strict round-trip check on
  import …"*.
- `docs/specs/06-governance.md:606`: `` | `GET` | `/api/v1/audit/export` | Export CSV/JSON | ``.
  **FR-371** (`06:157`): *"The audit log is queryable by actor, entity, action, time range, and free
  text over justifications, with cursor pagination and export to CSV/JSON."*
- `docs/specs/07-platform.md:317`: `` | `GET` | `/api/v1/jobs/{id}/events` | SSE stream of progress updates | ``.

No spec names `application/json` for any of the four.

### How the guard sees them today

`backend/tests/test_contracts.py:3169-3183`, `UNTYPED_2XX_PERMANENT` (FD-1335 Part A, `SL-1367`),
lists all four as *"2xx responses that are streams or files, so no JSON shape exists to publish.
Permanent."*, so the untyped-body guard passes them by citation. Two of its citations are stale at
`50bbdd96`: `rate_tables.py:184` for the CSV export (the `media_type` is at `:238`) and
`rate_tables.py:206-207` for the XLSX export (now `:260-262`). The guard's response side reads
every media type of every 2xx response (`_walk_bodies`, `:3068-3089`), so a route that declares its
media type but publishes it with an empty schema is still reported.

### The related item already on the register

FD-1335's register row carries a **LOW sub-item, same carrier, not blocking WK-675**: *"document
the four stream and file routes' media types as their code declares them."* That sub-item is this
finding's subject. The 07:28:38 entry sets the class at MEDIUM. Whether this finding absorbs the
sub-item, so that FD-1335's row is annotated to point here, is the lead's to decide; this record
does not edit FD-1335's row.

## Disposition

*Proposed; the lead gives the verdict.*

**MEDIUM, fix before close, one limb per owner:**

1. **Limb 1, the rate-table exports** (`/export/csv`, `/export/xlsx`): **owner WK-1178** (07:28:38).
2. **Limb 2, the audit export** (`/api/v1/audit/export`): **owner WK-679**, the Work that owns
   `06` FR-371's export. `docs/roadmap.md` at `50bbdd96`: `### WK-679 — Audit explorer, chain
   verification, export` (`:2591`), whose source row reads *"From “Workstreams” (line 470): Audit
   explorer, chain verification, export | FR-368, FR-369, FR-370, FR-371, FR-372, FR-374,
   FR-375"* (`:2603`). **WK-679 is `phase: P3`** (`:2600`). Under `CLAUDE.md` §0 and §14 ("A later
   phase's finding is a spec change only"), this limb is not built in P2 unless the maintainer
   reassigns it. The lead raises that consequence with the maintainer; this record does not decide
   it.
3. **Limb 3, the job-events stream** (`/api/v1/jobs/{job_id}/events`): **not named by the ruling;
   no owner set here.** The lead asks the maintainer whether it joins this finding and who owns it.

**Remedy (07:28:38):** each route declares its response media type, so the generated contract reads
`text/csv` and the spreadsheetml type for the two exports and `application/x-ndjson` and `text/csv`
for the audit export, with no `application/json` entry on any of them. The remedy also re-points or
removes the routes' `UNTYPED_2XX_PERMANENT` entries, as the declared schemas decide, and proves the
change red first on the stale-list test (`test_every_untyped_body_exclusion_is_still_untyped`). The
form (FastAPI `response_class` or a `responses` `content` map, and each media type's schema) is
the fixing slice's design. **S5 (`SL-1547`) is unchanged.**

**Event:** the finding closes when the sweep predicate above, run on `main`, prints no line for an
owned limb's route, and no limb remains open.
