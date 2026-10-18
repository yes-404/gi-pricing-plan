---
id: PL-1708
family: plan
kind: map
title: WK-1178 — FD-1684's remedy, the four non-JSON routes declare their real media types in the published contract: a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: 36e2610ab8135bc3b3563464e7f5f719713b168b
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1684, FD-1335, PL-1682, SL-1683, PL-1667, SL-1669, PL-1364, SL-1367, SL-1547, RL-1445]
---

# PL-1708 — WK-1178, FD-1684's remedy: the four non-JSON routes declare their real media types

*(Minted 2026-10-14 as PL-1708 and SL-1709 from working ids 9997 and 9998, in the D15 batch mint PR.)*

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1667` and `PL-1682`, this delta `relates:` the records it
> builds on: `FD-1684` (the finding this slice discharges), `FD-1335`/`PL-1364`/`SL-1367` (Part A,
> the untyped-body guard whose `UNTYPED_2XX_PERMANENT` list holds the four routes) and
> `PL-1682`/`SL-1683` (the precedent this delta copies, and the slice it follows on shared files).
> It adds **one slice row**, `SL-1709`, under `### WK-1178` in [`../roadmap.md`](../roadmap.md).
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds `test-driven-development`
> (every acceptance item is seen red **by its cause** before the code that turns it green),
> `python-test` (the `req` marker; negative tests), `fastapi-service` (Task 2), `contract-guard`
> (Task 3), `spec-change` (Task 1), `dev-commands` (`uv sync --all-packages`; both gate halves)
> and `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step. The executor is spawned from `.claude/roles/executor.md`.

Filed under **working id 9997**; its slice row is **SL-1709** (`draft`, working id 9998). Both ids
were reserved by the lead, `~/gi-pricing-plan.local/handover/eta.md`, line "2026-10-14 09:29:43 BST
lead: RESERVED working ids PL 9997 (WK-1178 plan delta: FD-1684 remedy — declare the four non-JSON
media types, red first per route) and SL 9998 (its slice), seat planner-fd1684". Written 2026-10-14
by the planner (seat planner-fd1684). **Tree read:** `origin/main`
`36e2610ab8135bc3b3563464e7f5f719713b168b` (#1296). The branch is cut from #1297's branch
`origin/pl-9906-wk1178-import-200-typing` @`ae10fd43`, where `FD-1684`, `PL-1682` and `SL-1683` are
minted; it re-merges `origin/main` after #1297 merges. `FD-1684` cites its lines at `50bbdd96`;
`git diff --stat 50bbdd96 36e2610a` over `backend/src/app/api/{rate_tables,audit,jobs,responses}.py`,
`backend/tests/test_contracts.py` and `docs/contracts/openapi/generated.json` prints nothing, so
those citations hold at `36e2610a`. Every `file:line` below was read at `36e2610a`. **No test was
run at planning time.** One FastAPI spike was run (premise h), outside the repository.

## Context — the rulings this delta records

The maintainer's (by delegation) entries in `~/gi-pricing-plan.local/channel/to-lead.md`, and the
lead's in `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`. A repository reader cannot
open those files (RFC-777), so the parts this delta rests on are quoted verbatim.

1. **The maintainer (by delegation), "2026-10-12 07:28:38 BST — S5 flags: (1) NEITHER (a) nor (c):
   type POST …/import's 200 FIRST in a tiny WK-1178 slice (d), with (a)+tripwire only as a named
   fallback; (3) the CONTRACT is wrong → FD MEDIUM, the class of non-JSON routes"**, flag (3):
   *"The spec says "Export cells to CSV" (03 :1044, FR-235), and the wire sends text/csv, so the
   code's DECLARATION is wrong and the generated contract inherits it. The generated contract says
   application/json, empty schema, for /export/csv, /export/xlsx AND /api/v1/audit/export. It is the
   same class: a non-JSON route that never declares its media type."* And: *"Remedy: the routes
   declare their response media type, so the contract reads text/csv and the xlsx MIME type. S5
   stays unchanged: reading text is correct for the real wire."*
2. **The lead, from-lead "2026-10-12 07:29:15 BST"**, which relayed entry 1 and reserved FD 9912
   (now `FD-1684`): *"Flag (3): the CONTRACT is wrong (spec 03 :1044 FR-235 says CSV; wire
   text/csv) → FD MEDIUM over the CLASS (/export/csv, /export/xlsx, /api/v1/audit/export:
   application/json + empty schema); owner WK-1178 for the two rate-table routes; audit-export limb
   → the Work owning 06's audit export, cited, no default; remedy: routes declare their media types;
   S5 unchanged."* The owner split in this entry is **superseded by entry 3**.
3. **The maintainer (by delegation), "2026-10-12 07:46:06 BST — PL 9906/SL 9911/FD 9912: ACK + early
   mint as PL-1682/SL-1683/FD-1684 after #1295/#1296; DP-1 (type the 201 too) and DP-2 accepted; FD
   9912 owns ALL FOUR limbs under WK-1178, absorbing FD-1335's LOW sub-item"**, items 3 and 4:
   *"ONE owner for the whole class: WK-1178, all four limbs. That is /export/csv, /export/xlsx,
   /api/v1/jobs/{job_id}/events (07 :317 says "SSE stream", the wire is text/event-stream at
   jobs.py:310), and /api/v1/audit/export."* *"Why the audit export too, although WK-679 is P3:
   declaring the media type of a route that ALREADY EXISTS on main corrects the published contract
   of built code. It does not build a P3 capability, so §0's "do not build ahead" is not engaged."*
   *"WK-679 keeps the audit-export FEATURE."* And the remedy row: *"one small WK-1178 slice declares
   the four media types (response_class/responses), and generated.json then reads text/csv, the
   xlsx MIME, text/event-stream, and the audit export's real type. Red first: the contract test
   asserts each declared media type."*
4. **The lead, eta "2026-10-14 09:29:43 BST"** (above): the ids and the brief, *"declare the four
   non-JSON media types, red first per route"*.
5. **The maintainer (by delegation), "2026-10-14 09:45:05 BST" (A)**: DP-1 to DP-4 ruled (i) and DP-5 ruled
   (ii), each as recommended (the Decision points table's "Ruled" column). It also rules that Task 2's
   assert 1 is the evidence of record for DP-1, that DP-3's planted-route red is printed in the `LG-`,
   and that the SSE `data` finding is filed in the next batch, owner `WK-1178`, P2 backlog (the Hand-off).

**The four routes come from `FD-1684`, not from a brief.** `FD-1684` §Evidence's sweep lists four;
entries 1 and 2 name three; entry 3 adds `GET /api/v1/jobs/{job_id}/events`. The sweep, re-run on
`36e2610a` (the predicate is `FD-1684`'s, verbatim), prints the same four lines over the same 823
responses.

## Goal

The four routes publish their real response media types in `docs/contracts/openapi/generated.json`,
with no `application/json` entry on any of them and a non-empty schema on each, so that `FD-1684`'s
event holds: **its sweep predicate, run on `main`, prints no line.**

| # | Route | Declared 200 content (DP-1 (i), DP-2 (i)) |
|---|---|---|
| 1 | `GET /api/v1/rate-tables/{slug}@{version}/export/csv` | `text/csv`: `{"type": "string"}` |
| 2 | `GET /api/v1/rate-tables/{slug}@{version}/export/xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`: `{"type": "string", "format": "binary"}` |
| 3 | `GET /api/v1/audit/export` | `text/csv`: `{"type": "string"}`; `application/x-ndjson`: `{"type": "string"}` |
| 4 | `GET /api/v1/jobs/{job_id}/events` | `text/event-stream`: `{"type": "string"}` |

The wire does not change. Every handler body stays as it is. The four routes leave
`UNTYPED_2XX_PERMANENT` (DP-3). `generated.json` and the frontend client are regenerated.

**Out of scope:** the audit-export **feature** (`WK-679`, entry 3); S5's `exportCsv`
(`SL-1547`, entry 1: unchanged); the SSE event payload's shape (DP-4, and the Hand-off);
`FD-1335`'s Part B list (`SL-1683` and later slices).

## Status

The status is the `status:` field in the header, and nothing else. **The scope is ruled** (Context,
entries 1 and 3). **DP-1 to DP-5 are ruled** as recommended (the maintainer (by delegation), "2026-10-14 09:45:05 BST" (A); the Decision points table's "Ruled" column). The plan stays `draft` until the slice's activation commit sets it `active`. *(Activated 2026-10-17 13:11 BST by the executor's activation commit: the maintainer's GO of record "2026-10-17 13:09:07 BST" (SL-1709 GO CONFIRMED) and the lead's dispatch.)*

## Activation needs, each with its state at `36e2610a`

1. **The scope ruled.** **MET**: Context, entry 3 (07:46:06).
2. **DP-1 to DP-5 accepted or overruled.** **MET**: all five ruled as recommended, the maintainer (by delegation), "2026-10-14 09:45:05 BST" (A).
3. **This delta minted or GO'd on its working ids.** **NOT MET.**
4. **`FD-1684` on `main`.** **NOT MET**: it is minted on #1297's branch (`ae10fd43`), not yet
   merged. This branch re-merges `origin/main` after #1297 merges.
5. **`SL-1683` merged first, or the dispatch record names the shared paths.** `SL-1683` (`PL-1682`)
   writes the same three files near the same lines: `backend/src/app/api/rate_tables.py` (its
   `:266-326`, the import handler, directly after this slice's `:220-263`),
   `backend/tests/test_contracts.py` (its `:3193` and `:3215-3217`, after this slice's
   `:3169-3183`), and `docs/contracts/openapi/generated.json`. **Recommendation: dispatch this
   slice after `SL-1683` merges**, so it cuts from a `main` that has it. If the lead runs them at the
   same time, `RL-1445` item 2's two conditions go in the dispatch record, and the later PR
   regenerates `generated.json`, never hand-merges it.
6. **No other in-flight writer on the write set.** Census at 2026-10-14 09:3x BST, slots
   `gate-1` and `gate-2` both free when it ran: `gh pr list --state open` → #1297, #1298, #1299,
   #1300, #1301. `git diff --name-only origin/main...origin/<branch>`, filtered to the write set:
   - `sl-1549-wk675-s7b-compare-backend` (#1301, `e14e6d32`): `generated.json` (regenerated);
     `03-rating-engine.md` hunks at `:948-952`, away from `:1044-1045`;
   - `sl-1675-wk1178-zero-weight` (#1300, `52e7ec5f`): `generated.json`;
   - `docs-d14-2026-10-12` (#1298): `03` hunk at `:1504`;
   - `sl-1547-wk675-s5` (`SL-1547`, no PR, `25ada217`): `test_contracts.py` (appended after
     `:3337`), `generated.json`, `03` hunks at `:82`, `:182`, `:899`.
   None touches `backend/src/app/api/{rate_tables,audit,jobs}.py`,
   `backend/tests/test_api_{rate_tables,audit,jobs}.py`, `docs/specs/06-governance.md` or
   `.claude/skills/contract-guard/SKILL.md`. `generated.json` is regenerated by whichever PR merges
   later. **Re-check at the GO.**
7. **A build slot and the single gate** (`RL-1445` item 1).
8. **The lead's GO.**

## Scope and requirements, each id individually

- `03` **FR-235** (export to and import from CSV/XLSX): routes 1 and 2.
- `06` **FR-371** (the audit log … *"with cursor pagination and export to CSV/JSON"*, `06:157`):
  route 3, its declaration only (entry 3: WK-679 keeps the feature).
- `07` **FR-400** (Jobs report structured progress, `07:89`): route 4, the stream it reports
  through (`07:317`, *"SSE stream of progress updates"*); its existing test carries this marker
  (`backend/tests/test_api_jobs.py:319`).
- `07` **FR-451** (*"OpenAPI 3.1 is generated from the Pydantic models (ADR-704) and published at
  `/openapi.json`; the committed copy in `docs/contracts/openapi/` is regenerated in CI and a drift
  fails the build"*, `07:182`): the four declarations, the regenerated contract, the new tests'
  marker.
- `FD-1684`, all four limbs (Context, entry 3), and with it `FD-1335`'s LOW sub-item, absorbed
  into `FD-1684` (its §Evidence, entry "2026-10-12 07:46:06 BST", item 5).

## Premises, read at `36e2610a`

| # | Premise | Where | What the source says |
|---|---|---|---|
| a | Route 1 returns CSV, undeclared | `backend/src/app/api/rate_tables.py:220-238` | decorator `:220-224`: `summary`, `responses=problems(401, 403, 404)`, no `response_class`; `-> Response` (`:231`); `return Response(content=content, media_type="text/csv")` (`:238`) |
| b | Route 2 returns XLSX, undeclared | `rate_tables.py:241-263` | decorator `:241-245`, the same form; `media_type=("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")` (`:260-262`) |
| c | Route 3 streams one of two types, undeclared | `backend/src/app/api/audit.py:237-310` | decorator `:237-241`, `responses=problems(400, 401, 403, 422)`, no `response_class`; `format: … Query(pattern="^(csv\|json)$")] = "csv"` (`:245`); `StreamingResponse(json_lines(), media_type="application/x-ndjson", …)` (`:278-282`); `StreamingResponse(csv_rows(), media_type="text/csv", …)` (`:306-310`). `StreamingResponse` is imported from `fastapi.responses` (`:27`) |
| d | Route 4 streams SSE, undeclared | `backend/src/app/api/jobs.py:254-317` | decorator `:254-258`, `responses=problems(401, 403, 404, 422)`; `-> Response` (`:264`); `StreamingResponse(events(), media_type="text/event-stream", …)` (`:308-310`); each event is `event: progress\ndata: <json>\n\n` or `event: done\ndata: <json>\n\n`, the JSON a dict of `id`, `status`, `progress`, `trace_id` built in the handler (`:288-295`) |
| e | The published contract | `docs/contracts/openapi/generated.json` | each route's `"200"` is `{"content": {"application/json": {"schema": {}}}, "description": "Successful Response"}` (`FD-1684` §Evidence, lines `:31985-31992`, `:32088-32095`, `:19382-19389`, `:27869-27876` at `50bbdd96`; unchanged at `36e2610a`). The only non-JSON 2xx entry in the whole document is `GET /metrics` 200 `text/plain` `{"type": "string"}` |
| f | The repository's own declared-media-type precedent | `backend/src/app/api/health.py:139`, `:158` | `response_class=PlainTextResponse`; published as `text/plain` `{"type": "string"}` (premise e) |
| g | How FastAPI 0.142.2 (`uv.lock`) builds a 200's content | `fastapi/openapi/utils.py:330`, `:456-471`, `:472-516` (installed 0.142.2) | the default content key is the response class's `media_type`; a non-`JSONResponse` class gets `{"type": "string"}`; a `JSONResponse` with no response field gets `{}`; a `responses={200: {"content": …}}` map is **deep-merged** onto that default (`:515`). A class whose `media_type` is `None` (`Response`, `StreamingResponse`) adds no default key. `:421-455` hold FastAPI's native SSE and JSON Lines branches (`route.is_sse_stream`, `route.is_json_stream`), which emit `itemSchema` |
| h | The declaration forms, observed | spike, FastAPI 0.142.2 from the `sl-1547` worktree's venv, 2026-10-14, `/tmp/pl9997-spike/spike.py` (not in the repository) | handler returns `Response(b"a", media_type="text/csv")`; published 200 content: no declaration → `{"application/json": {"schema": {}}}`; **`responses` map only → `{"application/json": {"schema": {}}, "text/csv": {"schema": {"type": "string"}}}`** (the JSON entry survives); `response_class=Response` + `responses` map → `{"text/csv": {"schema": {"type": "string"}}}`; `response_class=<Response subclass with media_type = "text/csv">` → `{"text/csv": {"schema": {"type": "string"}}}`; `response_class=StreamingResponse` + a two-type map → exactly the two types |
| i | The guard and its lists | `backend/tests/test_contracts.py:3053-3089`, `:3098-3106`, `:3167-3183`, `:3224-3239`, `:3242-3287` | `_is_empty` is form 1 (`schema == {}`), `_is_open_object` form 2; `_walk_bodies` reads **every media type of every 2xx response**, a schema-less media type counting as `{}` (`:3068-3089`); `UNTYPED_2XX_PERMANENT` holds the four routes, *"2xx responses that are streams or files, so no JSON shape exists to publish. Permanent."* (`:3167-3168`), two reasons stale (`rate_tables.py:184`, `:206-207`); `_guard_remainder` and `test_every_untyped_body_exclusion_is_still_untyped` read it (`:3232`, `:3275`, `:3279`, `:3285-3286`); the stale check fails with `no longer untyped, remove from the 2xx lists: …` (`:3276`) |
| j | The skill describes the list | `.claude/skills/contract-guard/SKILL.md:292-296` | *"`UNTYPED_2XX_PERMANENT` (stream and file bodies, each reason names its file and line)"* among *"Four lists"* |
| k | Existing tests that pin the wire | `backend/tests/test_api_rate_tables.py:959-977` (`test_export_csv_returns_the_seeded_cells`, asserts `content-type` starts with `text/csv`), `:980-1000` (`test_export_xlsx_parses_to_the_seeded_cells`, no `content-type` assert); `backend/tests/test_api_audit.py:169-181` (`test_csv_export_carries_the_hashes`, `text/csv`), `:184-193` (`test_json_export_is_line_delimited`, no `content-type` assert); `backend/tests/test_api_jobs.py:319-337` (`test_the_event_stream_ends_when_the_job_is_terminal`, `text/event-stream`) | **All stay green unchanged**; two gain one line each (Task 2) |
| l | The precedent test for a published response | `test_api_rate_tables.py:878-889` (SL-1669) | `api_client.app.openapi()["paths"][…]["post"]["responses"]["201"]["content"]["application/json"]["schema"]` |
| m | The spec rows | `docs/specs/03-rating-engine.md:1044`, `:1045`; `docs/specs/06-governance.md:606`; `docs/specs/07-platform.md:317` | *"Export cells to CSV (FR-235)"*; *"Export cells to XLSX (FR-235)"*; *"Export CSV/JSON"*; *"SSE stream of progress updates"*. No row names `application/json`; only `06:606`'s *"JSON"* does not fix the wire format, which is JSON Lines (`audit.py:273`: *"JSON Lines, not one array"*) |
| n | No frontend source on `main` calls a route | `git grep -n "export/csv\|export/xlsx\|audit/export\|/events" 36e2610a -- frontend/src ':!frontend/src/api/generated'` | no output. `generate:api` is `openapi-typescript` 7 (`frontend/package.json:13`, `:43`) |
| o | The hand-authored design document | `docs/contracts/openapi/gi-pricing.yaml:473-479` | `/jobs/{id}/events` 200: `content: {text/event-stream: {}}`. Not regenerated, not in the write set |

## Decision points

| DP | Question | Options | Recommendation | Blocking | Who | Ruled |
|---|---|---|---|---|---|---|
| DP-1 | How does each route declare its media type? | (i) **`response_class=Response`** (routes 1, 2, 4) or **`response_class=StreamingResponse`** (route 3) — both have `media_type = None`, so FastAPI adds no default key — plus a 200 entry in the existing `responses=` map, `{**problems(…), 200: {"description": …, "content": {<media>: {"schema": …}}}}`; (ii) a `Response` subclass per media type (`CsvResponse`, `XlsxResponse`, `EventStreamResponse`) as `response_class`, the `PlainTextResponse` form of premise f; route 3 still needs (i), because one class carries one media type; (iii) the `responses` map alone, without `response_class` | **(i).** One form for all four, and the only form that covers route 3's two types (premise h). The handler bodies and their returns stay as they are. (ii) adds three classes, two forms, and puts the schema choice (DP-2) in FastAPI's default rather than in the declaration. (iii) is **wrong**: the spike shows it keeps `application/json {}` beside the real type (premise h), so `FD-1684`'s sweep still prints the route and the guard still reports it | yes | the maintainer (by delegation) | **Ruled (i)**, the maintainer (by delegation), "2026-10-14 09:45:05 BST" (A): `response_class=Response` (routes 1, 2, 4) / `StreamingResponse` (route 3) plus a 200 `content` entry in the existing `responses=` map; (iii) refused on the spike's evidence that it keeps `application/json {}`. Task 2's assert 1 (`set(content) == {…}`) is the evidence of record on the built routes, not the spike. |
| DP-2 | Which schema under each media type? | (i) `{"type": "string"}` for the three text types (`text/csv`, `application/x-ndjson`, `text/event-stream`), `{"type": "string", "format": "binary"}` for the XLSX; (ii) `{"type": "string"}` for all four, what FastAPI itself emits for a non-JSON class (premise g) and the `/metrics` precedent (premise e); (iii) `{"type": "string", "format": "binary"}` for all four; (iv) an empty or absent schema | **(i).** The XLSX is a zip archive, not text: a client generator that honours `format: binary` (most non-TypeScript generators) returns bytes rather than a decoded string, which would corrupt the file. The three text types are text. For `openapi-typescript` 7 all of (i)–(iii) type the body as `string`, so the frontend sees no difference. (iv) is refused: `_walk_bodies` counts a schema-less media type as `{}` (premise i), so the guard would report it, and `FD-1684`'s sweep would still print it | yes | the maintainer (by delegation) | **Ruled (i)**, the maintainer (by delegation), "2026-10-14 09:45:05 BST" (A): `{"type":"string"}` for text/csv, application/x-ndjson and text/event-stream; `{"type":"string","format":"binary"}` for xlsx. |
| DP-3 | What happens to `UNTYPED_2XX_PERMANENT` once its four entries leave? | (i) **remove the constant**, its two reads in `_guard_remainder` (`:3232`) and in the stale check (`:3275`, `:3279`, `:3285-3286`), and the skill's mention (premise j), with a dated line in the skill: a stream or file route now declares its media type, and then `test_no_json_body_is_untyped` reports it if it does not; (ii) keep the constant **empty**, its comment and reads unchanged | **(i).** The list's premise, *"no JSON shape exists to publish. Permanent."*, is what `FD-1684` shows false: every such route can publish its real type. An empty allow-list labelled "Permanent" invites the next stream route to be listed rather than declared. With the list gone, `test_no_json_body_is_untyped` is the standing guard for the whole class: a fifth undeclared stream publishes `{}` (form 1) and is reported. Task 3 shows that red on a planted route. (ii) is one edit smaller | yes | the maintainer (by delegation) | **Ruled (i)**, the maintainer (by delegation), "2026-10-14 09:45:05 BST" (A): remove `UNTYPED_2XX_PERMANENT` and its reads, with a dated line in the contract-guard SKILL. Task 3's planted-route red is the required broken-input proof and the `LG-` shows it printed. |
| DP-4 | Route 4: a plain declaration, or FastAPI's native SSE? | (i) the DP-1 (i) declaration: `text/event-stream` `{"type": "string"}`, the handler unchanged; (ii) FastAPI 0.142's native SSE (`route.is_sse_stream`, premise g): rewrite the handler to yield typed items, so the contract publishes an `itemSchema` with a typed `data` | **(i).** The finding is a misdeclared media type, and (i) fixes it without touching the wire. (ii) rewrites a working stream, and `itemSchema` is an OpenAPI 3.2 keyword inside a 3.1.0 document (`FR-451` says 3.1). The event's `data` is a dict built in the handler (premise d), which is a hand-written shape no `model-schema` model owns: the Hand-off reports it to the lead and does not decide it | yes | the maintainer (by delegation) | **Ruled (i)**, the maintainer (by delegation), "2026-10-14 09:45:05 BST" (A): a plain `text/event-stream` declaration, handler unchanged. Native SSE refused (`itemSchema` is a 3.2 keyword in a 3.1.0 document; it rewrites a working stream). |
| DP-5 | Does a spec row change? | (i) no spec edit: the rows already name the formats (premise m) and `FD-1684` says the spec agrees with the wire; (ii) one dated clause on **`06:606` only**, naming the two media types, because *"JSON"* there is the only row word that does not fix the wire format (JSON Lines, not one array); (iii) a dated clause on all four rows naming each media type | **(ii).** The contract will publish `application/x-ndjson`, and the spec should say JSON Lines where a reader would otherwise expect one JSON array. The other three rows already say CSV, XLSX and SSE. This edits a P3 module's spec for built code only, which entry 3 says does not engage `CLAUDE.md` §0's "do not build ahead". (iii) adds three clauses that restate their own row | no: with (i), Task 1 is dropped | the maintainer (by delegation) | **Ruled (ii)**, the maintainer (by delegation), "2026-10-14 09:45:05 BST" (A): one dated clause on `06` §5.1 `:606` only (JSON Lines). |

## Write set

| Path | What changes | Task |
|---|---|---|
| `docs/specs/06-governance.md` §5.1 audit-export row (`:606`) | a dated clause (DP-5 (ii)) | 1 |
| `backend/src/app/api/rate_tables.py` `:220-224`, `:241-245` | the two decorators (DP-1, DP-2) | 2 |
| `backend/src/app/api/audit.py` `:237-241` | the decorator | 2 |
| `backend/src/app/api/jobs.py` `:254-258` (and its `fastapi` import, if `Response` must be imported for `response_class`) | the decorator | 2 |
| `backend/tests/test_api_rate_tables.py`, `test_api_audit.py`, `test_api_jobs.py` | one new test per route (Reds 1–4); one added `content-type` line in each of the two tests premise k names without one | 2 |
| `backend/tests/test_contracts.py` `:3167-3183`, `:3232-3233`, `:3268-3287` | `UNTYPED_2XX_PERMANENT` and its reads removed (DP-3 (i)) | 3 |
| `.claude/skills/contract-guard/SKILL.md` `:292-296`, its `Verified` section (`.claude/skills/README.md` does not name the list at `36e2610a`) | the list's mention removed, a dated line (DP-3 (i)) | 3 |
| `docs/contracts/openapi/generated.json` | regenerated, never hand-edited | 3 |
| `docs/findings/register.md` FD-1684 row | a dated line: the four routes declared | 4 |
| `docs/roadmap.md` SL-1709 row; `docs/ledgers/LG-<working id>` | status lines and the slice ledger (L1 (a')) | 0, 4 |

**Not in the write set:** the handler bodies; `packages/model-schema/` (no model changes);
`scripts/generate-contracts.py`; `docs/contracts/openapi/gi-pricing.yaml` (premise o, hand-authored,
not regenerated); `frontend/src/api/generated` (regenerated and VCS-ignored); any frontend source
(premise n).

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch, cut from
  `origin/main` (after `SL-1683`, activation need 5). `uv sync --all-packages`.
- [ ] Re-read premises a–o at the slice base, and record each one in the `LG-`, with its locator.
  If `SL-1683` has merged, its lines in `rate_tables.py` and `test_contracts.py` will have moved:
  re-point this plan's line numbers in the `LG-`, never in this plan.
- [ ] Re-run `FD-1684`'s sweep predicate (its §Evidence, verbatim) at the slice base. It must print
  exactly the four lines. Record the output.
- [ ] `gh pr list --state open`, and grep `to-lead.md` for entries since 2026-10-12 07:46:06 that
  rule on `FD-1684`, `media type`, `UNTYPED_2XX_PERMANENT`, `export` or `events`. Name the SHA and
  the entry read.
- [ ] Quote Context entries 1 and 3 and the DP rulings in the `LG-`.
- [ ] Commit the `LG-` scaffold and the slice row's `active` line (L1 (a')).

### Task 1: Spec — `06` §5.1's audit-export row (DP-5 (ii); dropped under DP-5 (i))

- [ ] Append to the row's description cell (`06:606`), keeping the row's cell count:
  `*(Amended <date>, <slice id>, FD-1684: **200** `text/csv` for `format=csv` (the default), or JSON Lines, `application/x-ndjson`, one audit event per line, for `format=json`.)*`
- [ ] `python3 scripts/audit-docs.py` exits 0 apart from check 31 on working ids (run once, under
  `flock -w 1800 /tmp/slots/gate-2`).
- [ ] Commit: `docs(specs): 06 §5.1 — the audit export's two media types (FD-1684)`.

### Task 2: The routes declare their media types — red first, per route

**Interfaces — Consumes:** `problems` from `app.api.responses` (unchanged); `Response` from
`fastapi` and `StreamingResponse` from `fastapi.responses`, already imported where they are used
(premises a–d). No model is added.

Each red is one new `@pytest.mark.req("FR-451")` test in the route's own test file, mirroring
premise l (do not reinvent its fixtures: `api_client` in `test_api_rate_tables.py`; the file's
`client: TestClient` fixture in `test_api_audit.py` and `test_api_jobs.py`, as at
`test_api_audit.py:171` and `test_api_jobs.py:321`). Each reads `<client>.app.openapi()["paths"][<path>]["get"]["responses"]["200"]["content"]`
and asserts, **in this order**:

1. `set(content) == {<the route's media types>}`;
2. each media type's `["schema"]` equals its DP-2 schema.

On `main` each fails on assertion 1, **by its cause**: premise e's content has one key,
`application/json`. A failure on assertion 2 first, a `KeyError`, or any other failure is a plan
defect: stop and report.

- [ ] **Red 1 (route 1).** `test_export_csv_publishes_text_csv` in `test_api_rate_tables.py`,
  path `/api/v1/rate-tables/{slug}@{version}/export/csv`, expected `{"text/csv"}`. Run it: red,
  pytest's first line `assert {'application/json'} == {'text/csv'}`.
- [ ] **Red 2 (route 2).** `test_export_xlsx_publishes_the_spreadsheetml_type` in
  `test_api_rate_tables.py`, path `…/export/xlsx`, expected
  `{"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}`. Red:
  `assert {'application/json'} == {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}`.
- [ ] **Red 3 (route 3).** `test_export_publishes_csv_and_json_lines` in `test_api_audit.py`, path
  `/api/v1/audit/export`, expected `{"text/csv", "application/x-ndjson"}`. Red: the set comparison
  fails with `'application/json'` the only item on the left (pytest prints the right-hand set in
  its own order).
- [ ] **Red 4 (route 4).** `test_events_publish_text_event_stream` in `test_api_jobs.py`, path
  `/api/v1/jobs/{job_id}/events`, expected `{"text/event-stream"}`. Red:
  `assert {'application/json'} == {'text/event-stream'}`.
- [ ] Record the four red outputs in the `LG-`, each against the tree it ran on.
- [ ] **The wire, pinned where it is not (guards, green at the base).** Append one line to each
  test premise k names without a `content-type` assert:
  - `test_export_xlsx_parses_to_the_seeded_cells`: `assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"`;
  - `test_json_export_is_line_delimited`: `assert response.headers["content-type"].startswith("application/x-ndjson")`.

  Each is shown able to fail in a scratch edit (change the handler's `media_type` string; the
  line fails; revert). Record both outputs in the `LG-`. With premise k's three existing asserts,
  every declared media type is then pinned to the wire by a test.
- [ ] Implement (DP-1 (i), DP-2 (i)), the handler bodies unchanged:
  - route 1 (`rate_tables.py:220-224`): `response_class=Response`,
    `responses={**problems(401, 403, 404), 200: {"description": "The version's cells as CSV (FR-235)", "content": {"text/csv": {"schema": {"type": "string"}}}}}`;
  - route 2 (`:241-245`): the same, with the spreadsheetml type and `{"type": "string", "format": "binary"}`;
  - route 3 (`audit.py:237-241`): `response_class=StreamingResponse`, a 200 entry whose content
    holds `text/csv` and `application/x-ndjson`, each `{"type": "string"}`;
  - route 4 (`jobs.py:254-258`): `response_class=Response` (or `StreamingResponse`; both have
    `media_type = None`), a 200 entry with `text/event-stream` `{"type": "string"}`.

  If the four 200 entries repeat one shape, the executor may add one helper beside `problems` in
  `backend/src/app/api/responses.py`; that file then joins the write set, and the `LG-` says so.
- [ ] Reds 1–4 green. Every existing test of premise k passes **unchanged** (`uv run pytest -q
  backend/tests/test_api_rate_tables.py -k export`, `… test_api_audit.py -k export`, `…
  test_api_jobs.py -k "event or contract"`: one file and a `-k` selection at a time; check
  `pgrep -af 'pytest|vitest|flock'` and both slots first, per the executor charter).
- [ ] Commit: `fix(api): the four non-JSON routes declare their real media types (FD-1684)`.

### Task 3: Contracts and the guard list

- [ ] `uv run python scripts/generate-contracts.py` (writes). Then `git diff --stat docs/contracts`
  must name **only** `openapi/generated.json`. Any other file is a stop. In the `LG-`, show that
  each of the four paths' hunks is its `200` block and nothing else, and name every other hunk
  (none is expected).
- [ ] `FD-1684`'s sweep predicate, verbatim, on the regenerated file: **no output**.
- [ ] Run `uv run pytest -q backend/tests/test_contracts.py -k untyped`: **red by its cause**.
  `test_every_untyped_body_exclusion_is_still_untyped` fails with `no longer untyped, remove from
  the 2xx lists:` naming exactly the four keys, `('GET', '/api/v1/audit/export', '200')`,
  `('GET', '/api/v1/jobs/{job_id}/events', '200')`,
  `('GET', '/api/v1/rate-tables/{slug}@{version}/export/csv', '200')`,
  `('GET', '/api/v1/rate-tables/{slug}@{version}/export/xlsx', '200')`. This red cannot be seen on
  `main`: the test is green there by design and turns red only once the routes are declared
  (`LG-1676`'s record of the same red is the precedent). Record the output.
- [ ] DP-3 (i): remove `UNTYPED_2XX_PERMANENT` (`:3167-3183`) and its reads (`:3232`, `:3275`,
  `:3279`, `:3285-3286`); `UNTYPED_2XX_PENDING_PART_B` and the other lists stay. Under DP-3 (ii),
  remove the four entries and keep the constant empty. Re-run: green.
- [ ] **The standing guard, shown able to fail.** In a scratch edit, remove `response_class` and
  the 200 entry from route 1, regenerate, and run `uv run pytest -q backend/tests/test_contracts.py
  -k test_no_json_body_is_untyped`: `[response]` fails naming
  `('response', 'GET', '/api/v1/rate-tables/{slug}@{version}/export/csv', '200')`. Revert both
  edits and regenerate; `git diff` is clean of the scratch. Record the output.
- [ ] `.claude/skills/contract-guard/SKILL.md`: the list's mention removed from `:292-296` ("Four
  lists" becomes three), one line saying a stream or file route declares its media type
  (`FD-1684`, `<slice id>`), and the `Verified` section dated. `.claude/skills/README.md` does
  not name the list (`git grep UNTYPED_2XX_PERMANENT 36e2610a -- .claude`: `SKILL.md:294` only).
- [ ] `uv run python scripts/generate-contracts.py --check` exits 0;
  `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && pnpm --dir frontend type-check` exits 0.
  The generated `schema.d.ts` types each route's 200 as `string` under its media type (premise n:
  no source caller, so nothing else moves). Record the four generated lines in the `LG-`.
- [ ] Commit: `chore(contracts): regenerate for the four declared media types; UNTYPED_2XX_PERMANENT removed (FD-1684)`.

### Task 4: The gate, the register line, the ledger

- [ ] `docs/findings/register.md`, FD-1684's row (the row whose first cell ends `(FD-1684)`):
  append `*(<date>: the four routes declare their media types, by <slice id> (<plan id>): text/csv; the spreadsheetml type; text/csv and application/x-ndjson; text/event-stream. The sweep predicate prints no line on <sha>.)*`
  The auditor sets the finding `closed` (`document-ids.md` §1.6, FD row). Run
  `python3 scripts/register-lint.py`.
- [ ] The full gate, both halves (`CLAUDE.md` §11), in the single gate slot, on
  `origin/main...<branch>`; the rc table goes in the `LG-`.
- [ ] Closing acts in the slice PR's last commit (L1 (a')): the slice row's `closed` line; the
  `LG-`'s Audit section after the auditor's verdict.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root.

1. **`FD-1684`'s event:** its sweep predicate (`FD-1684` §Evidence, verbatim) prints no line on the
   slice branch.
2. **Each route publishes exactly its real media types:**
   `python3 -c "import json;d=json.load(open('docs/contracts/openapi/generated.json'))['paths'];[print(p, d[p]['get']['responses']['200']['content']) for p in ('/api/v1/rate-tables/{slug}@{version}/export/csv','/api/v1/rate-tables/{slug}@{version}/export/xlsx','/api/v1/audit/export','/api/v1/jobs/{job_id}/events')]"`
   prints the Goal table's content for each, and no `application/json` key.
3. **Reds 1–4 pass, and each was seen red by its cause:** the four tests pass, and their red
   outputs (assertion 1, `{'application/json'}` on the left) are quoted in the `LG-`, each against
   the tree it names.
4. **The wire matches the declaration:** premise k's three `content-type` asserts and Task 2's two
   new lines pass; the two new lines' planted reds are in the `LG-`.
5. **The guard list is gone and the standing guard bites:** `grep -n UNTYPED_2XX_PERMANENT
   backend/tests/test_contracts.py .claude/skills/contract-guard/SKILL.md` prints nothing (DP-3
   (i)); Task 3's stale-list red and its planted `test_no_json_body_is_untyped` red (a planted
   route that declares no media type, DP-3's required broken-input proof, 09:45:05 (A)) are quoted
   in the `LG-`, printed.
6. **Existing behaviour holds:** premise k's tests pass; `git diff origin/main --
   backend/tests/test_api_rate_tables.py backend/tests/test_api_audit.py backend/tests/test_api_jobs.py`
   adds lines only; `git diff origin/main -- backend/src/app/api` changes decorator lines (and
   imports) only, no handler body line.
7. **No hand-written shape; no drift:** `git diff origin/main --stat -- packages/model-schema`
   prints nothing; `uv run python scripts/generate-contracts.py --check` exits 0; `pnpm --dir
   frontend generate:api` leaves `git status --short` clean of tracked files.
8. **Only `generated.json` moves under `docs/contracts/`:** `git diff origin/main --name-only --
   docs/contracts` prints exactly `docs/contracts/openapi/generated.json`.
9. **The gate is green on the merge tree:** the `CLAUDE.md` §11 commands, both halves, each exit 0
   against `origin/main...<slice branch>`.

## Global Constraints

- `CLAUDE.md` §2: no shape written twice; `docs/contracts/` generated, never hand-edited;
  `frontend/src/api/generated` VCS-ignored.
- `CLAUDE.md` §3: never hand-write an API type in the frontend.
- `CLAUDE.md` §0: do not build ahead of the phase. Entry 3 rules that declaring an existing route's
  media type is not a P3 build; nothing else of `WK-679` is touched.
- One PR per slice (L1 (a')): code, tests, spec clause, skill edit, slice status line, one `LG-`.
- `RL-1445` item 1: one full gate at a time; targeted single-file runs only outside it.

## Hand-off (not this plan's writes)

- **The WK-1178 roadmap row** lists this delta as a Work-plan delta. The planner's charter limits
  its roadmap writes to the `SL-` rows it cuts. The line is the lead's or the minter's.
- **The SSE event payload.** Route 4's `data` is a dict built in the handler (`jobs.py:288-295`:
  `id`, `status`, `progress`, `trace_id`), a shape no `model-schema` model owns. Declaring
  `text/event-stream` (DP-4 (i)) does not type it. Whether that is a finding was the lead's to judge;
  the maintainer (by delegation), "2026-10-14 09:45:05 BST" (A), ruled it a LOW finding, owner `WK-1178`,
  filed in the next batch as working id 8006 (the same batch as this plan).
- **S5** (`SL-1547`) keeps `exportCsv` reading text (entry 1). Nothing in this slice asks it to
  change.

## Self-review

- **Spec coverage.** FR-235's two exports, FR-371's export and FR-400's stream are each declared;
  FR-451's drift check covers the regenerated file. `06:606` names its wire formats (Task 1,
  DP-5 (ii)).
- **Every limb is in a task.** Routes 1–4 each have a red (Task 2), a declaration (Task 2), a
  regenerated block (Task 3) and a register mention (Task 4).
- **Placeholders.** `<date>`, `<slice id>`, `<plan id>`, `<sha>` and the `LG-` working id are
  filled at execution. None else.
- **Literals.** Every `file:line` was read at `36e2610a`. The four paths and the stale-check
  message were read from `test_contracts.py:3169-3183`, `:3276`. The red text of assertion 1 is
  predicted from premise e (one `application/json` key); the tests are the arbiter. The declaration
  forms' output is premise h's spike, not a prediction.
- **Decision points.** Five, each with options and a recommendation; none is picked silently.
  Task 1 and DP-3's edits each carry their alternative.
- **Convention 4.** `gh pr list --state open` at 2026-10-14 09:3x BST returned #1297–#1301, none
  ruling on this subject. The to-lead entries were searched for `1684`, `9912`, `media`,
  `export/csv` and `event-stream` among entries dated 2026-10-12 to 2026-10-14; the only hit is
  07:46:06 (Context, entry 3).
