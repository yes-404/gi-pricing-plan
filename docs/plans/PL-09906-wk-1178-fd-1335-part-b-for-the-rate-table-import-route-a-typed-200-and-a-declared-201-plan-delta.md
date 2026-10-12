---
id: PL-9906
family: plan
kind: map
title: WK-1178 — FD-1335 Part B for the rate-table import route, a typed 200 (ImportPreview) and a declared 201 (RateTableVersion): a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: 50bbdd96b2154cb4eb79ccf91658191e51ab8906
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1335, FD-1366, PL-1364, SL-1367, PL-1667, SL-1669, PL-1546, PL-1668, SL-1547, RL-1445]
---

# PL-9906 — WK-1178, FD-1335 Part B for the rate-table import route: a typed 200 and a declared 201

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1667`, this delta `relates:` the records it builds on:
> `FD-1335` (the finding whose Part B list holds this route), `PL-1364`/`SL-1367` (Part A, the
> guard) and `PL-1667`/`SL-1669` (the precedent this delta copies). It adds **one slice row**,
> working id 9911, under `### WK-1178` in [`../roadmap.md`](../roadmap.md).
> REQUIRED SUB-SKILL: subagent-driven-development (recommended) or executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds `test-driven-development`
> (every acceptance item is seen red **by its cause** before the code that turns it green),
> `python-test` (the `req` marker; negative tests), `fastapi-service` (Task 2), `contract-guard`
> (Task 3), `spec-change` (Task 1), `dev-commands` (`uv sync --all-packages`; both gate halves)
> and `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step. The executor is spawned from `.claude/roles/executor.md`.

Filed under **working id 9906**; its slice row is **working id 9911** (`draft`); the finding
filed beside it is **working id 9912**. All three were reserved by the lead, from-lead
"2026-10-12 07:29:15 BST" (`~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`). Written
2026-10-12 by the planner (seat planner-import). **Tree read:** `origin/main`
`50bbdd96b2154cb4eb79ccf91658191e51ab8906` (#1294); the branch was cut at
`3b2081b7333bded7e998104f042586d50e8bf3e3` (#1293, SL-1669) and fast-forwarded before any write.
Neither commit touches a file this plan cites by line except `docs/roadmap.md` and
`docs/findings/register.md`, whose lines below were read at `50bbdd96`. Every `file:line` below was
read there. **No test was run at planning time.**

## Context — the ruling this delta records

The maintainer's (by delegation) entry in `~/gi-pricing-plan.local/channel/to-lead.md`. A
repository reader cannot open that file (RFC-777), so the parts this delta rests on are quoted
verbatim.

1. **"2026-10-12 07:28:38 BST — S5 flags: (1) NEITHER (a) nor (c): type POST …/import's 200 FIRST
   in a tiny WK-1178 slice (d), with (a)+tripwire only as a named fallback; (3) the CONTRACT is
   wrong → FD MEDIUM, the class of non-JSON routes"**, flag (1):
   *"(d): a tiny WK-1178 slice (Part B continued) gives POST /rate-tables/{slug}@{version}/import a
   response_model built from the existing model-schema types (RateTableDiff + ImportVerdict, or the
   composed model DEFINED IN model-schema, not in TS). It removes the route from
   UNTYPED_2XX_PENDING_PART_B; contracts and the generated client are regenerated. S5 then uses
   the generated type with no cast."* And: *"Run it beside S5's parity-test work. S5's gate waits
   for it, which costs a few hours, not days."* And: *"FALLBACK, only if (d) hits a real blocker
   you send me: (a) with your tripwire test (it FAILS once the route is typed), a single site,
   disclosed."*
2. The flags as raised: the lead's from-lead entry **"2026-10-12 07:28:00 BST"**, flag (1):
   *"ImportPreview composed from generated RateTableDiff+ImportVerdict and asserted onto the
   still-untyped POST …/import 200 (UNTYPED_2XX_PENDING_PART_B, WK-1178's hold) at ONE call site"*.
3. The seat and the ids: the lead's from-lead entry **"2026-10-12 07:29:15 BST"**: *"Lead: PL 9906 +
   SL 9911 + FD 9912 reserved; SEATING planner-import"*.

Flag (3) of the same entry is **not this slice's**: it is the finding filed beside this plan
(working id 9912), whose remedy is a separate slice. This slice does not touch either export route.

**Which finding holds this route.** The import route's 200 is an entry of
`UNTYPED_2XX_PENDING_PART_B` (`backend/tests/test_contracts.py:3193`), whose reason is
`_PENDING_2XX = "pending FD-1335 part B: an object with no properties"` (`:3188`). So this is
**FD-1335 Part B**, not FD-1366. FD-1366 concerns JSON *request* bodies, and its Disposition
excludes this route's `multipart/form-data` request with a citation (`docs/findings/FD-01366-…md:74`).
The lead's brief named FD-1366's hold; the guard list it names, and the ruling's own words
("UNTYPED_2XX_PENDING_PART_B"), are FD-1335's.

## Goal

`POST /api/v1/rate-tables/{slug}@{version}/import` publishes a typed **200** and a declared
**201**, so that WK-675 S5 (`SL-1547`) uses the generated types and hand-writes neither
(`CLAUDE.md` §2, §3):

- the 200 (no `confirm`) is published as **`ImportPreview`**, the model that already exists in
  `model-schema` (`packages/model-schema/src/model_schema/rating.py:1363-1369`: `diff:
  RateTableDiff`, `created_by_import: ImportVerdict`) and that the service already returns
  (`backend/src/app/platform/rate_tables.py:893`). **No new model is needed and none is
  composed**: the ruling's "RateTableDiff + ImportVerdict" composition is this class;
- the 201 (`confirm: true`) is published as **`RateTableVersion`**, which the service already
  returns (`platform/rate_tables.py:923`) and which today is published nowhere (DP-1);
- the route leaves `UNTYPED_2XX_PENDING_PART_B` (`test_contracts.py:3193`);
- `docs/contracts/openapi/generated.json` and the frontend client are regenerated.

**Out of scope:** the two export routes and `/api/v1/audit/export` (the finding of working id
9912; its remedy is a separate slice); S5's frontend (S5 switches to the generated type after this
slice merges, per entry 1). `FD-1335` stays **active**: three entries remain in its Part B list.

## Status

The status is the `status:` field in the header, and nothing else. **No decision point is
open.** The scope is ruled (Context, entry 1). DP-1 and DP-2 are the planner's design choices
inside that scope, stated so the lead can overrule them. The plan stays `draft` until it is minted
or GO'd on its working ids.

## Activation needs, each with its state at `50bbdd96`

1. **The scope ruled.** **MET**: Context, entry 1 (07:28:38).
2. **DP-1 and DP-2 accepted or overruled by the lead.** **OPEN.**
3. **This delta minted or GO'd on its working ids**, as the lead dispatches. **OPEN.**
4. **No in-flight writer on the write set, or the dispatch record names the shared paths.** At
   `50bbdd96` one PR is open (`gh pr list --state open`, 2026-10-12 07:33:51 BST: #1295 only).
   `git diff --name-only origin/main...<ref>`, filtered to the write set, on the two refs that can
   reach it:
   - `origin/sl-1622-wk690-fix-row` (#1295) touches `docs/findings/register.md` (other rows);
   - `origin/sl-1547-wk675-s5` (`SL-1547`, no open PR, head `25ada217` at 07:33 BST) touches
     `backend/tests/test_contracts.py` (one test appended after `:3335`, away from `:3188-3217`),
     `docs/specs/03-rating-engine.md` (near `:79`, away from `:1046`) and
     `docs/contracts/openapi/generated.json` (regenerated from its own model changes).
   Neither touches `backend/src/app/api/rate_tables.py` or `backend/tests/test_api_rate_tables.py`.
   `generated.json` is regenerated by whichever PR merges second, never hand-merged. S5 merges
   after this slice (entry 1: "S5's gate waits for it"). **The census is not a full-ref sweep**: a
   gate slot was held when it ran, so the sweep-pause rule limited it to the open PR and S5's
   branch. **Re-check at the GO.**
5. **A build slot and the single gate** (`RL-1445` item 1). If another WK-1178 slice builds at
   the same time, `RL-1445` item 2's two conditions go in the dispatch record.
6. **The lead's GO.**

## Scope and requirements, each id individually

- `03` **FR-235** (export to and import from CSV/XLSX, a strict round-trip check, the import
  presented as a diff for confirmation before it creates a version): the route this slice types.
- `07` **FR-451** (the contract is generated, and CI fails on drift): the regenerated
  `docs/contracts/`.
- `FD-1335` Part B for this one route.

## Premises, read at `50bbdd96`

| # | Premise | Where | What the source says |
|---|---|---|---|
| a | The route publishes an open 200 and no 201 | `backend/src/app/api/rate_tables.py:266-326` | decorator `responses=problems(401, 403, 404, 413, 422)` (`:269`), no `response_model`; `-> dict[str, Any]` (`:281`); `return preview.model_dump(mode="json")` (`:312`); `response.status_code = status.HTTP_201_CREATED` (`:325`); `return created.model_dump(mode="json")` (`:326`) |
| b | The generated contract carries the open 200 | `docs/contracts/openapi/generated.json`, path `/api/v1/rate-tables/{slug}@{version}/import` `post` | `"200"` → `{"additionalProperties": true, "title": "Response Import Rate Table Api V1 Rate Tables  Slug   Version  Import Post", "type": "object"}`; **no `"201"` key**; 401, 403, 404, 413, 422 are `ProblemDetail` |
| c | The models exist in `model-schema` | `packages/model-schema/src/model_schema/rating.py:1128` (`RateTableDiff`), `:1345-1360` (`ImportVerdict`), `:1363-1369` (`ImportPreview`, `extra="forbid"`) | `ImportPreview`: `diff: RateTableDiff`, `created_by_import: ImportVerdict`; docstring *"The import preview (03 §5.2)"* |
| d | The service returns those models | `backend/src/app/platform/rate_tables.py:884-909`, `:912-923` | `import_preview(...) -> ImportPreview`; `import_confirmed(...) -> RateTableVersion` |
| e | The precedent for a preview/confirm pair | `rate_tables.py:138-178` (manual edit) | `response_model=None`; `responses={**problems(...), 200: {"model": RateTableDiff}, 201: {"model": RateTableVersion}}`; `-> RateTableDiff \| RateTableVersion`; returns the models; `response.status_code = status.HTTP_201_CREATED` on confirm. Published as `$ref` `RateTableDiff` (200) and `RateTableVersion` (201) |
| f | The guard and its stale check | `backend/tests/test_contracts.py:3188-3196`, `:3214-3217`, `:3268-3287` | `UNTYPED_2XX_PENDING_PART_B` holds four keys, the import 200 at `:3193`; `NON_JSON_REQUEST_BODIES` cites the import's request as `rate_tables.py:225-226` (stale at `50bbdd96`: `File()`/`Form()` are at `:279-280`); `test_every_untyped_body_exclusion_is_still_untyped` fails on a listed route that is no longer untyped (`stale_2xx`) |
| g | No standalone schema exists for the diff family | `scripts/generate-contracts.py:38` `GENERATED_SHAPES` (`"rate-table-version": "RateTableVersion"` at `:164`); `docs/contracts/schemas/generated/` | no `rate-table-diff`, `import-verdict` or `import-preview` slug; `RateTableDiff` is published only as a `generated.json` component (DP-2) |
| h | The model names the backend imports | `rate_tables.py:42-51` | `from model_schema.rating import (BulkOperationRequest, RateTable, RateTableCell, RateTableDiff, RateTableDiffCell, RateTableManualEdit, RateTableVersion, SeedFromModelRequest)`; `ImportPreview` is not imported. `Any` stays used (`:332`) |
| i | Existing API tests that pin behaviour | `backend/tests/test_api_rate_tables.py:760-777` (401/403), `:1002-1235` (`test_import_previews_a_modified_export`, `…_preview_creates_nothing`, `…_confirm_creates_the_version`, `…_confirm_cannot_override_the_verdict`, `…_confirm_on_a_parquet_baseline_spills`, `…_refuses_an_oversized_filename`, `…_refuses_a_wrong_header`, `…_diffs_against_a_parquet_baseline`); helper `_seeded_table` (`:943`) | **All stay green unchanged** |
| j | The precedent test for a published response | `test_api_rate_tables.py:881-891` (SL-1669) | `api_client.app.openapi()["paths"][…]["post"]`; `…["responses"]["201"]["content"]["application/json"]["schema"]["$ref"].endswith("/RateTableVersion")` |
| k | What S5 composed | `origin/sl-1547-wk675-s5` `25ada217`, `frontend/src/api/rateTables.ts:14-23`, `:93-106` | `interface ImportPreview { diff: RateTableDiff; created_by_import: ImportVerdict }`, asserted at `previewImport`; `confirmImport` asserts `Promise<RateTableVersion>` onto the undeclared 201. **Read to learn the shape; nothing is copied from it** |

## Decision points

| DP | Question | Options | Recommendation | Blocking | Who |
|---|---|---|---|---|---|
| DP-1 | How does one route publish a 200 and a 201 of different models? A bare `response_model=ImportPreview` validates the 201's `RateTableVersion` against `ImportPreview` and answers 500 | (i) the manual-edit precedent (premise e): `response_model=None`, `responses={…, 200: {"model": ImportPreview}, 201: {"model": RateTableVersion}}`, the handler returns the models; (ii) `response_model=ImportPreview`, and the 201 branch returns a `JSONResponse`, so the 201 stays unpublished; (iii) `response_model=ImportPreview \| RateTableVersion` | **(i).** It is the repository's own form for this exact preview/confirm pair (`rate_tables.py:138-178`). (ii) leaves S5's `confirmImport` asserting a type onto an undeclared 201, the same unchecked cast entry 1 refuses for the 200. (iii) publishes a union on the 200 that a client cannot narrow without a hand-written test. **This publishes the 201 as well as the 200**, one line wider than entry 1's words; it adds no model and no file | no | the planner (a design choice inside a ruled scope); stated here so the lead can overrule it |
| DP-2 | Does `ImportPreview` get a standalone generated schema (`docs/contracts/schemas/generated/import-preview.schema.json`)? | (i) no: the OpenAPI component in `generated.json` is its generated contract, as for `RateTableDiff` (premise g); (ii) yes: a `GENERATED_SHAPES` entry, a new file, a `ONE_SIDED_SLUGS` entry, and the non-markdown file count in `tests/test_audit_docs_ids.py` widened (SL-1669 needed that widening for its new file, `LG-1676`'s write-set note) | **(i).** Entry 1 asks for a contract that is generated, and `generated.json` is generated and drift-checked (FR-451). (ii) adds four edits for a shape no other artifact embeds | no | the planner; the lead can overrule it |

## Write set

| Path | What changes | Task |
|---|---|---|
| `docs/specs/03-rating-engine.md` §5.1 import row (`:1046`) | a dated clause: the 200 and the 201 | 1 |
| `backend/src/app/api/rate_tables.py` `:42-51`, `:266-326` | `ImportPreview` imported; the decorator, the return annotation and the two returns (DP-1 (i)) | 2 |
| `backend/tests/test_api_rate_tables.py` | two new tests (Task 2); the existing ones unchanged | 2 |
| `backend/tests/test_contracts.py` `:3193`, `:3215-3217` | the `UNTYPED_2XX_PENDING_PART_B` key removed; the `NON_JSON_REQUEST_BODIES` citation re-pointed to the handler's `File()`/`Form()` lines | 3 |
| `docs/contracts/openapi/generated.json` | regenerated, never hand-edited | 3 |
| `docs/findings/register.md` FD-1335 row | a dated line: the import route typed | 4 |
| `docs/roadmap.md` slice row (working id 9911); `docs/ledgers/LG-<working id>` | status lines and the slice ledger (L1 (a')) | 0, 4 |

**Not in the write set:** `packages/model-schema/` (DP-2 (i): no model changes);
`scripts/generate-contracts.py`; `frontend/src/api/generated` (regenerated and VCS-ignored). No
frontend source on `main` calls this route (`grep -rn '/import' frontend/src --include=*.ts
--include=*.vue | grep -v generated` → no output at `50bbdd96`).

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch, cut from
  `origin/main`. `uv sync --all-packages`.
- [ ] Re-read premises a–k at the slice base, and record each one in the `LG-`, with its locator.
- [ ] `gh pr list --state open`, and grep `to-lead.md` for entries since 2026-10-12 07:28:38 that
  rule on `import`, `FD-1335`, `ImportPreview` or `UNTYPED_2XX`. Name the SHA and the entry read.
- [ ] Quote entry 1 (Context) in the `LG-`.
- [ ] Commit the `LG-` scaffold and the slice row's `active` line (L1 (a')).

### Task 1: Spec — `03` §5.1's import row

- [ ] Append to the row's description cell (`03:1046`), keeping the row's cell count:
  `*(Amended <date>, <slice id>, FD-1335 Part B: **200** an ImportPreview (§5.2): diff, the RateTableDiff of the would-be version against the addressed one, and created_by_import, the ImportVerdict; nothing is created. **201** with confirm: true: the created RateTableVersion, carrying the same verdict as created_by_import.)*`
- [ ] `python3 scripts/audit-docs.py` exits 0 apart from check 31 on working ids (run once, under
  `flock -w 1800 /tmp/slots/gate-2`).
- [ ] Commit: `docs(specs): 03 §5.1 — the import route's 200 and 201 (FD-1335 Part B)`.

### Task 2: The route — a typed 200 and a declared 201

**Interfaces — Consumes:** `ImportPreview` and `RateTableVersion` from `model_schema.rating`, both
unchanged. The service calls keep their signatures (premise d).

- [ ] **Red 1 (the published contract).** A `@pytest.mark.req("FR-451")` test in
  `test_api_rate_tables.py`, mirroring premise j's test (do not reinvent its fixtures), reads
  `api_client.app.openapi()` for `/api/v1/rate-tables/{slug}@{version}/import` `post` and asserts,
  **in this order**:
  1. `responses["200"]["content"]["application/json"]["schema"]["$ref"]` ends with
     `/ImportPreview`;
  2. `responses["201"]["content"]["application/json"]["schema"]["$ref"]` ends with
     `/RateTableVersion`.

  Run it: **red by its cause**, `KeyError: '$ref'` on the first assertion (the 200 is premise b's
  open object). A `KeyError: '201'`, or any other failure first, is a plan defect: stop and report.
- [ ] **Red 2 (a real response round-trips through the published model; a guard).** A
  `@pytest.mark.req("FR-235")` test seeds a table with `_seeded_table`, exports it, changes one
  cell exactly as `test_import_previews_a_modified_export` does (`:1003-1028`), and posts it twice:
  - without `confirm`: 200; `ImportPreview.model_validate(body).model_dump(mode="json") == body`;
  - with `data={"confirm": "true"}`: 201;
    `RateTableVersion.model_validate(body).model_dump(mode="json") == body`.

  It is **green at the base**: the route already dumps these models. So it is a guard over the
  change, not a red, and is shown able to fail: in a scratch edit, make the preview branch
  return `{**preview.model_dump(mode="json"), "planted": 1}`; the test fails on `ImportPreview`'s
  `extra_forbidden`. Revert. Record both outputs in the `LG-`.
- [ ] Implement at `rate_tables.py:266-326`, as premise e does:
  - `response_model=None` and `responses={**problems(401, 403, 404, 413, 422), 200: {"model": ImportPreview}, 201: {"model": RateTableVersion}}`;
  - `-> ImportPreview | RateTableVersion`;
  - `return preview` (`:312`) and `return created` (`:326`);
  - add `ImportPreview` to the `model_schema.rating` import (`:42-51`).

  Keep the docstring. `Any` stays (premise h).
- [ ] Reds 1–2 green. Every existing import test (premise i) passes **unchanged**:
  `uv run pytest -q backend/tests/test_api_rate_tables.py -k import` (one file, `-k` selection;
  check `pgrep -af 'pytest|vitest|flock'` and both slots first, per the executor charter).
- [ ] Commit: `feat(rating): publish POST import's 200 as ImportPreview and its 201 as RateTableVersion (FD-1335 Part B)`.

### Task 3: Contracts and the guard list

- [ ] `uv run python scripts/generate-contracts.py` (writes). Then `git diff --stat docs/contracts`
  must name **only** `openapi/generated.json`. Any other file is a stop. In the `LG-`, show that
  the import path's hunk is the 200's `$ref`, the new 201 and nothing else of that path, and
  name every other hunk (the new `ImportPreview` component is expected).
- [ ] Run `uv run pytest -q backend/tests/test_contracts.py -k untyped`: **red by its cause**.
  `test_every_untyped_body_exclusion_is_still_untyped` fails with `no longer untyped, remove from
  the 2xx lists:` naming `('POST', '/api/v1/rate-tables/{slug}@{version}/import', '200')`
  (`LG-1676`'s record of the same red for bulk-operation is the precedent). This red cannot be seen
  on `main`: the test is green there by design and turns red only once the route is typed. Record
  the output.
- [ ] Remove that key from `UNTYPED_2XX_PENDING_PART_B` (`:3193`); the other three stay. Re-point
  the `NON_JSON_REQUEST_BODIES` reason (`:3215-3217`) to the handler's `File()`/`Form()` lines
  after Task 2. Re-run: green.
- [ ] `uv run python scripts/generate-contracts.py --check` exits 0;
  `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api && pnpm --dir frontend type-check` exits 0.
- [ ] Commit: `chore(contracts): regenerate for the typed import route; the 2xx pending list shrinks (FD-1335 Part B)`.

### Task 4: The gate, the register line, the ledger

- [ ] `docs/findings/register.md`, FD-1335's row (the row whose first cell ends `(FD-1335)`):
  append `*(<date>: POST /rate-tables/{slug}@{version}/import's 200 typed as ImportPreview, and its 201 published as RateTableVersion, by <slice id> (<plan id>). Remaining in Part B's list: GET /dataset-versions/{version_id}/rejected, POST /sources/{source_id}/preview, POST /validation-reports/{report_id}/results/{rule_id}/acknowledge.)*`
  The finding stays `active`. Run `python3 scripts/register-lint.py`.
- [ ] The full gate, both halves (`CLAUDE.md` §11), in the single gate slot, on
  `origin/main...<branch>`; the rc table goes in the `LG-`.
- [ ] Closing acts in the slice PR's last commit (L1 (a')): the slice row's `closed` line; the
  `LG-`'s Audit section after the auditor's verdict.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root.

1. **The route publishes a typed 200 and 201:** Red 1's test passes, and
   `python3 -c "import json;d=json.load(open('docs/contracts/openapi/generated.json'));r=d['paths']['/api/v1/rate-tables/{slug}@{version}/import']['post']['responses'];print(r['200']['content']['application/json']['schema'], r['201']['content']['application/json']['schema'])"`
   prints an `ImportPreview` `$ref` and a `RateTableVersion` `$ref`.
2. **The guard entry is gone, the other three stay:** `grep -n 'import", "200"' backend/tests/test_contracts.py`
   prints nothing; `grep -c '"/api/v1/sources/{source_id}/preview", "200"\|"/api/v1/dataset-versions/{version_id}/rejected", "200"\|/acknowledge", "201"' backend/tests/test_contracts.py`
   prints `3`.
3. **A real response round-trips through the published models:** Red 2 passes, and its
   planted-extra red is in the `LG-`.
4. **The contract red was seen by its cause:** Red 1's `KeyError: '$ref'` and Task 3's stale-list
   failure are quoted in the `LG-`, each run against the tree it names.
5. **Existing behaviour holds:** premise i's tests pass unchanged (`git diff origin/main --
   backend/tests/test_api_rate_tables.py` adds lines only).
6. **No hand-written shape; no drift:** `git diff origin/main --stat -- packages/model-schema` prints
   nothing; `uv run python scripts/generate-contracts.py --check` exits 0; `pnpm --dir frontend
   generate:api` leaves `git status --short` clean of tracked files.
7. **Only `generated.json` moves under `docs/contracts/`:** `git diff origin/main --name-only -- docs/contracts`
   prints exactly `docs/contracts/openapi/generated.json`.
8. **The gate is green on the merge tree:** the `CLAUDE.md` §11 commands, both halves, each exit 0
   against `origin/main...<slice branch>`.

## Global Constraints

- `CLAUDE.md` §2: no shape written twice; `docs/contracts/` generated, never hand-edited;
  `frontend/src/api/generated` VCS-ignored.
- `CLAUDE.md` §3: never hand-write an API type in the frontend.
- One PR per slice (L1 (a')): code, tests, spec clause, slice status line, one `LG-`.
- `RL-1445` item 1: one full gate at a time; targeted single-file runs only outside it.

## Hand-off (not this plan's writes)

- **The WK-1178 roadmap row** lists this delta as a Work-plan delta. The planner's charter limits
  its roadmap writes to the `SL-` rows it cuts. The line is the lead's or the minter's.
- **S5's switch** to the generated `ImportPreview` and to the generated 201, removing its composed
  interface and both assertions (premise k), is `SL-1547`'s, after this slice merges (entry 1).
- **The fallback** (entry 1: "(a) with your tripwire test … only if (d) hits a real blocker you
  send me") is the lead's to raise with the maintainer. This plan names no blocker.

## Self-review

- **Spec coverage.** FR-235's route is typed in both statuses; FR-451's drift check covers the
  regenerated file. The `03` §5.1 row names its response shapes for the first time (Task 1).
- **Placeholders.** `<date>`, `<slice id>`, `<plan id>` and the `LG-` working id are filled at
  execution. None else.
- **Type consistency.** `ImportPreview`, `ImportVerdict`, `RateTableDiff` and `RateTableVersion`
  are named the same in every task and match `rating.py` (premise c).
- **Literals.** Every `file:line` was read at `50bbdd96`. The route path, the guard-list key and
  the failure message text of Task 3 were read from `test_contracts.py:3188-3196`, `:3268-3276`.
  The `KeyError: '$ref'` cause is predicted from premise b's published schema, which has no `$ref`
  key; Red 1 is the arbiter.
- **Convention 4.** `gh pr list --state open` at 2026-10-12 07:33:51 BST returned only #1295
  (SL-1622), which does not rule on this subject. The to-lead entries were read up to "2026-10-12
  07:33:30 BST" (#1294's merge ACK), none ruling on this subject after 07:28:38.
