---
id: PL-2074
family: plan
kind: map
title: WK-1178 — the data and upload boundary, a stated request-body limit on both upload routes and a purge audit event with its before state (FD-1802, FD-1746), SL-2075 — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-07             # original date 2026-11-05, set at the draft under working id 8324; minted 2026-11-07
owner: planner
tree: dae9637ea6f6a56f6502e9db70392cdfb2f3983d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1802, FD-1746, SL-1736, SL-1547, FR-81, FR-235, FR-450, NFR-472]
---

# PL-2074 — WK-1178: the upload body limit and the purge audit's before state (SL-2075, a dated Work-plan delta)

*(Minted 2026-11-07 as PL-2074 from working id 8324, in the SL-2075 mint, with the mint tool of record `mint-repoint.py`; plan PL-2074, slice SL-2075 and ledger LG-2076 minted together, in that order.)*

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds one slice row, SL-2075, and edits no filed plan.
> The executor's skills are `superpowers:test-driven-development`, `.claude/skills/python-test`,
> `.claude/skills/fastapi-service`, `spec-change` and `git-hygiene`. PL-2074, SL-2075 and the ledger
> LG-2076 were minted 2026-11-07 from the working ids 8324, 8325 and 8326 the lead reserved.

## Authority

- **The user's decision and the order.** The maintainer's entry "2026-11-05 09:58:58 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`: "ALL 24 FIX-BEFORE-FREEZE rows AND FD-1337 (7 h) AND
  FD-1484 (8 h) are coded and merged before Thu 12"; "a red gate = fix-and-regate within the chain,
  and only a slice still red at Wed 12:00 goes to the exception list".
- **The rulings, closed, verbatim** (the entry "2026-11-05 09:51:53 GMT"): "(4) FD-1746, FD-1488,
  FD-1748 severities RULED MEDIUM as proposed."
- **FD-1802's direction.** "a request-size limit *before* the read — middleware, or a per-route
  streamed cap — returning the declared `413` on both routes" (the maintainer (by delegation), to-lead
  "2026-10-17 22:56:37 BST", as the essay quotes it), and "Specify the limit first". Its discharge:
  "a merged change that returns 413 past a stated limit on both routes".
- **FD-1746's direction.** The entry "2026-10-14 12:07:40 BST", DP-6, as the essay quotes it. Its
  discharge: "the WK-1178 slice that passes `before` on the purge event and adds a per-class
  assertion for acknowledgements, dictionary edits, rule-set changes and purges, each red on the
  pre-fix tree. The rule-set assertion is SL 1736's."
- **The rulings on this plan, closed, verbatim** (the entry "2026-11-05 10:20:55 GMT"): "DP-A1 → 64 MiB on both
  routes, but as a TYPED SETTING (the fastapi-service settings form) defaulting to 64 MiB, never a constant; the
  nginx `client_max_body_size` in deploy/lb.conf AND the new frontend conf = the same limit plus a small margin, so
  the proxy never answers first with its HTML 413 — the new fact (nginx default 1 MiB, FD-1802's essay never read the
  proxy) is a dated line on FD-1802; A MERGES AFTER D, accepted. DP-A2 → a dated clause on FR-450 + the new code
  PAYLOAD_TOO_LARGE as an RFC 9457 problem, no new id — accepted. DP-A3 → XLSX expansion and gzip expand-first OUT,
  named in the plan, and a LOW FD filed by the auditor — accepted. DP-A4 → purge's `before` = version ids and statuses
  only — accepted. The mechanism: ASGI middleware (a per-route cap is impossible, a global cap refused) — accepted, with
  the skill's middleware-ordering trap named in the brief (the cap sits before body consumption and does not break trace
  propagation; a test for both)."
- **The triage.** `~/gi-pricing-plan.local/handover/p2-code-owed-triage-2026-11-05.md`
  (`b28ba8e9454c`) §3, Slice A. The brief: FD-1802's limit value is "SPEC TEXT FIRST".

## Goal

Past a stated size, both upload routes answer the declared `413` before the body is held. A purge's
audit event carries the state before it, and NFR-472's coverage claim is true class by class.
FD-1802 and FD-1746 close.

## Evidence at `dae9637e`

Cites were read at `origin/main` `dae9637ea6f6a56f6502e9db70392cdfb2f3983d`. Items marked FRAMEWORK
were read in tools-main's `.venv/lib/python3.12/site-packages`, the locked versions.

**FD-1802. The essay's cites have moved; its facts hold.**

- Rate-table import: `backend/src/app/api/rate_tables.py:291` `**problems(401, 403, 404, 413, 422)`,
  `:304` `file: Annotated[UploadFile, File()]`, `:326` `content = await file.read()`.
- Source preview: `backend/src/app/api/datasets.py:211` declares 413, `:217` the file, `:243`
  `read_tabular(await file.read(), …)`.
- **The class sweep:** `git grep -n -E 'UploadFile|File\(' origin/main -- backend/src` prints those two
  routes only. `git grep -n -E 'await request\.(body|json|form|stream)' origin/main -- backend/src`
  prints nothing. `problems(…413…)` appears only on these two: `git grep -n ', 413' origin/main --
  backend/src/app/api`.
- **A per-route cap cannot work (FRAMEWORK).** `fastapi/routing.py:443`: `body = await
  request.form()` runs in `get_request_handler` **before** the dependencies and the handler, so
  an `UploadFile` parameter means the whole multipart body has been consumed before any route code
  or auth check. The essay's "per-route streamed cap" option is closed by this. It must be below
  routing, in ASGI middleware.
- **An exception from `receive` needs the right class (FRAMEWORK).** The same function: `except
  HTTPException: raise` (`:480`), `except Exception` → `HTTPException(400, "There was an error
  parsing the body")` (`:483-485`). A `PlatformError` raised from a wrapped `receive` would be turned
  into a 400. So the streamed limb raises `fastapi.HTTPException(413)`, which `_handle_http_exception`
  (`backend/src/app/errors.py:558`) renders. That handler reads `_STATUS_CODES` (`:552-555`), which
  has no 413: it would fall to `INTERNAL_ERROR`.
- **The order.** `app.add_middleware(TraceMiddleware)` at `backend/src/app/main.py:217`, the only
  middleware, and "trace binding is the outermost middleware" (`main.py:5`). `add_middleware` puts
  the later call outside, so the new one is added **before** `:217`, keeping `trace_id` on its
  problem.
- **The essay did not read the proxy, and it has a limit.** `deploy/lb.conf` sets no
  `client_max_body_size`, and `git grep -n -i client_max_body_size origin/main -- deploy` prints
  nothing, so nginx's built-in default of 1 MiB applies (nginx's documented default; **not run
  here**). On the compose path, an upload over 1 MiB gets nginx's HTML 413 from `lb` today, not an RFC
  9457 problem and not the API. The authored `deploy/frontend.nginx.conf` of PL-2016 (cited as `PL 8319` at the draft; re-pointed 2026-11-07 by a dated note, PL-2016:26) has the same
  gap. A limit the proxy undercuts is not the stated limit.
- **The 413 that exists.** `formats.py:42` `MAX_DECOMPRESSED_BYTES` = 2 GiB; `_refuse_if_oversized`
  raises 413 `REJECT_RATE_EXCEEDED` (`:61-68`), and its text says "Ingest it from an object store
  rather than as an upload", so the platform's own stance is that large data takes the blob path
  (`07` FR-1776). `data/` holds the one bound; the rate-table route does not use it.
- **Sizes for the DP.** The full freMTPL2 frequency file is 36 288 567 bytes
  (`examples/fremtpl2/data/freMTPL2freq.arff`). `compose` sets no `mem_limit` on `api`
  (`deploy/docker-compose.yml:124-155`), and `WEB_CONCURRENCY` defaults to 1 (`:135`). **Memory
  use at any size is not measured** (the essay says so; nor is it here).
- **Spec state.** `git grep -n -i 'size limit\|Upload.*size' origin/main -- docs/specs` names no
  request limit. FR-450 (`07:182`) is "The API implements `00` §5 exactly". Error codes are registered
  by module in `errors.py` (`PLATFORM_ERROR_CODES` `:51`), and `07` §5 owns those.

**FD-1746.**

- **Limb 1.** `purge_subject` (`backend/src/app/platform/datasets.py:1004`), `audit.record` at
  `:1059-1068`, `action="dataset.subject_purged"`, `after={"subject_token": …, "versions_affected":
  len(versions)}`, and no `before`. `versions` is loaded at `:1040-1047`. The essay's `:1046-1056`
  has moved by 13 lines.
- **The route.** `purge_subject` has no API route (`backend/tests/test_lineage.py:507`), so the call
  is the service function, as that test does (`:511`, `:553`).
- **Limb 2 has mostly been paid.** NFR-472 (`docs/specs/01-data-management.md:1194`) names five classes.
  Read at this tree, each with its test and its assert on `before`:

| Class | Test | `before` asserted |
|---|---|---|
| transition | `test_data_nfrs.py:150` | yes |
| acknowledgement | `test_validation_reports.py:262` | yes (`:292`) |
| dictionary edit | `test_api_datasets.py:144` | yes (`:187`) |
| rule-set change | `test_api_datasets.py:191` (SL-1736) | read by the executor at R0 |
| **purge** | **none**: `test_lineage.py:543` asserts the action only | **no** |

  So the essay's "four of five have no assertion" reads the one test, and the marker's over-claim is
  now in a **docstring** (`test_data_nfrs.py:153-154`). What is owed: the purge assertion, the
  docstring, and the proof that the two older assertions can fail, since no red for them was ever
  recorded. The rule-set one is SL-1736's and is not re-proved here.
- **The trap in "`before`".** An erasure's prior state must not put back what it erased. The event
  already carries `subject_token`, the pseudonym, in `after`, so no new identity is added by naming the
  versions. FR-81: "Admin-only, audited". Rows are not read here: `before` carries version ids and
  statuses only.
- `@1` in `entity_ref` (`:1065`): the essay "was not checked". Left unchanged: it is the entity
  form the migration test reads (`test_migration_dataset_owner.py:267-279`).

**NFR-472 is DB-backed.** All these tests take the `database` fixture, so they are not small runs
(common seat brief, item 32).

## Decision points

**None open.** DP-A1 to DP-A4 are ruled by the entry "2026-11-05 10:20:55 GMT", quoted under Authority: (a) on all four,
with the limit a typed setting rather than the constant this plan first proposed. The options are recorded in the plan's
first filing, `d7af4f25`.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's
merge tree. Items 1 and 2 apply to this plan; A1 to A12 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no
   failing line except check 31 / check 32 lines naming this delta's own working ids (PL-2074, SL-2075, LG-2076 before the 2026-11-07 mint). After the
   mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints
   no line that stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only the Write set below.
  Nothing under `frontend/`, `packages/`, `docs/contracts/` (the two routes already declare 413;
  `generate-contracts.py --check` rc 0 proves it) or `scripts/`.
- **A2. Spec text first.** The spec commit precedes the first code commit, and states 64 MiB as the default of a
  setting. `git grep -n -E '67108864|64 MiB|65m' -- docs/specs backend/src deploy` shows the spec, the setting, and
  the two nginx files, each citing the spec.
- **A3. Red first, by cause.** LG-2076 quotes the red lines of T1 to T5, from the slice's named base.
- **A4. The limit, declared length.** T1: a request declaring a `Content-Length` over the limit on
  each route answers 413, code `PAYLOAD_TOO_LARGE`, with `trace_id`, and the handler is not entered.
  **The two ruled ordering proofs:** the sentinel `receive` shows no body read before the refusal (the cap sits before
  body consumption), and the response's `x-trace-id` header equals the problem's `trace_id` for a supplied `traceparent`
  (trace propagation is not broken).
- **A5. The limit, undeclared length.** T2: a chunked body with no `Content-Length` passing the limit
  answers the same 413. At the limit exactly, and below it, it passes (T3, both sides of the
  boundary).
- **A6. Exactly the routes that declare it.** T4: the set of routes whose OpenAPI operation declares
  `413` equals the set the middleware caps. A route that gains the declaration without the cap, or the
  reverse, goes red; shown by a break.
- **A7. The proxy does not undercut it.** T5: `client_max_body_size` in `deploy/lb.conf`, and in
  `deploy/frontend.nginx.conf`, is the setting's default plus 1 MiB (`65m`). A deployer who raises the setting raises
  both: `deploy/README.md` says so. **In a build
  window,** a 2 MiB and a limit + 1 byte upload through `lb` on project `gip-s4-runtime`: the first
  reaches the API, the second is the API's RFC 9457 `413` and not nginx's HTML.
- **A8. FD-1746 limb 1.** T6: the purge's event has `before == {"versions": [...]}` as DP-A4 rules,
  ordered, id and status, and `after` is unchanged.
- **A9. FD-1746 limb 2.** `test_data_nfrs.py:153`'s docstring claims the transition only and points at
  the other four tests. **A planted-break proof** for the two classes with no recorded red: with
  `before=` removed at `datasets.py` `update_dictionary` (`:314`) and at
  `platform/validation.py:354`, in the DB window, uncommitted, each test goes red by its own assert;
  the LG quotes both, then `git diff --quiet` on those files, rc 0.
- **A10. The GREEN set and the gate.** The GREEN set by import closure (common seat brief, item 29),
  commands and list in the LG. **The full code gate, both halves, SOLO**, green at the re-merged head,
  every rc quoted. If `deploy/lb.conf` is in the diff, the gate is compose-changing in spirit: **not
  pairable**, and the shared stack is restored only from tools-main. `req-coverage.py` rc 0.
- **A11. FD closing acts, in the FD-1842 form, in the slice's own PR, by the slice's auditor**, for
  FD-1802 and FD-1746: the essay's `status: closed`, `relates:` gaining the slice's ids, a
  `***Resolved <date>***` paragraph naming the delivered remedy, its red and its LG, the same on the
  register row, and the PR number and squash at the merge's date of record. FD-1802's paragraph names
  what DP-A3 left out, its essay gains the dated line on nginx's 1 MiB default, and the auditor files the LOW FD for
  XLSX expansion and gzip's expand-first. FD-1746's register cell records the MEDIUM ruling of 09:51:53 by a dated line.
- **A12. The LG Audit section**, with the lead's adoption, lands in the audit's own commit, and
  `docs/INDEX.md` is regenerated after the closing acts (common seat brief, item 17).

## Global Constraints

- **G1. The cap is at the two routes that declare 413 and no wider.** A global cap would make every
  write route able to return an undeclared status. The rule is RL-1687's for 429: an operation declares
  a status iff it can return it.
- **G2. `TraceMiddleware` stays outermost** (`main.py:5`). A 413 carries `trace_id` (FR-445).
- **G3. The limit counts the request body as sent**, multipart framing included. It is not the file's
  size, and the spec text says so.
- **G4. The limit is a typed setting,** `Settings.max_request_body_bytes`, default `64 * 1024 * 1024`, in the
  `fastapi-service` settings form (`backend/src/app/config.py`), never a constant (ruled). `create_app` passes it to the
  middleware. The tests construct the middleware with a small `max_bytes`.
- **G5. `REJECT_RATE_EXCEEDED` and `MAX_DECOMPRESSED_BYTES` are unchanged.**
- **G6. Audit events already written are immutable.** Old purges keep `before` null. No backfill, no
  migration. `audit.py:60`'s default is unchanged.
- **G7. Red first, by cause. No test is removed or weakened** (common seat brief, item 13).

## Needs

- **A DB window, lead-granted in writing**, single-tenant, about 20 min, no gate or timed stage beside
  it: `createdb -T` a copy under the slice's own name, **never the template**; `GIP_REDIS_URL` on `-n
  11`, `12` or `13`, never db 0 (live). Runs T6 red and green, and A9's two planted breaks. It ends
  with the two quoted zeros (common seat brief, items 22 and 23).
- **A build window**, for A7 only, about 30 min, serial with D's and after D's merge, on `gip-s4-runtime`,
  images by `docker build` and `up --no-build`. Needs `df -h /` read first (the 5 GB floor of PL-2016, cited as `PL 8319` at the draft; re-pointed 2026-11-07).
  **If no window is free by Tue 10,** A7's runtime limb is reported to the lead rather than dropped.
- **NFR VM:** nothing.

## Tasks

### SL-2075 — the upload body limit and the purge before state

**The row.** Fourth in the 09:58:58 order after D, R, C and T. WK-1178 fix slice. One `sonnet`
executor (the charter's model line governs).

- **Scope (what LG-2076 quotes):** R0 to R3 and G below.
- **Requirements:** `07` FR-450, FR-445 (read); `03` FR-235; `01` NFR-472, FR-81 (read).
- **Register:** FD-1802 and FD-1746 (both MEDIUM), closing at the merge (A11).
- **Depends on:** the maintainer's GO; the windows and the gate slot; **D merged**, since this slice merges after D
  and edits its `deploy/frontend.nginx.conf` (ruled).
- **Size:** 6.5 h (triage 7 h): FD-1802 5 h, FD-1746 1 h (the classes are mostly covered), windows 0.5 h.
  SOLO gate about 2.5 h, not counted. **Split point:** R3 (FD-1746) is independent.
- **Calendar:** merged before Thu 12 Nov 2026; still red at Wed 11 Nov 12:00 → the exception list.

**R0 — spec text first.** Re-read every Evidence cite at the base; a changed fact stops the slice.
Read `test_api_datasets.py:191`'s asserts for the table's open cell. Then, under `spec-change`, dated,
citing this plan and the 10:20:55 entry: the clause on FR-450, 64 MiB the setting's default, (`docs/specs/07-platform.md`),
`PAYLOAD_TOO_LARGE` in `07` §5's code list, the pointer clause on FR-235 and on the preview row
(`01:856`), and a line in `07` §7 or wherever the deploy path is described only if `audit-docs.py`
asks. Commit alone (A2).

**R1 — the limit, red first.** New `backend/tests/test_api_body_limit.py`, `req("FR-450")`, DB-free
for T1 to T4, built on a tiny `FastAPI()` with `install_error_handlers`, one `File()` route and a
sentinel that records entry, and for T4 the real route table:

- **T1** `test_a_declared_length_over_the_limit_is_refused_before_the_handler`. **Red:** 200, the
  sentinel entered.
- **T2** `test_a_chunked_body_over_the_limit_is_refused`, an async generator as the `httpx` body.
  **Red:** 200.
- **T3** `test_a_body_at_the_limit_passes`, and limit + 1 refused, parametrised. **Red:** the second
  arm.
- **T4** `test_the_capped_routes_are_the_routes_that_declare_413`: walk `app.openapi()["paths"]`
  for operations with `"413"`, and match each to `CAPPED_ROUTES`, both directions. **Red:** `NameError`
  is not a red, so T4 is added after R1's green, with its proof by break: a monkeypatched
  `CAPPED_ROUTES` missing one entry fails it.

**Green.** New `backend/src/app/api/body_limit.py`, pure ASGI:

```python
CAPPED_ROUTES: Final = (
    re.compile(r"^/api/v1/rate-tables/[^/]+/import$"),
    re.compile(r"^/api/v1/sources/[^/]+/preview$"),
)


class BodyLimitMiddleware:
    def __init__(self, app: ASGIApp, max_bytes: int) -> None: ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not any(r.match(scope["path"]) for r in CAPPED_ROUTES):
            return await self.app(scope, receive, send)
        declared = Headers(scope=scope).get("content-length")
        if declared is not None and declared.isdigit() and int(declared) > self.max_bytes:
            return await _too_large(scope)(scope, receive, send)
        seen = 0

        async def counted() -> Message:
            nonlocal seen
            message = await receive()
            seen += len(message.get("body", b""))
            if seen > self.max_bytes:
                raise HTTPException(413, _detail(self.max_bytes))
            return message

        await self.app(scope, counted, send)
```

- `_too_large` is a `problem_response(ProblemDetail(...))`, the same text as the handler's.
- `errors.py`: `_STATUS_CODES` gains `status.HTTP_413_...: ("PAYLOAD_TOO_LARGE", "Request body too
  large")`, and `PLATFORM_ERROR_CODES` the code.
- `main.py`: `app.add_middleware(BodyLimitMiddleware, max_bytes=settings.max_request_body_bytes)` immediately **before** `:217`, with a
  one-line comment on why the order. `HTTPException` is `fastapi.HTTPException` (Evidence).
- The message names the limit and the blob path, never the filename (NFR-499).

**R2 — the proxy.** **T5**, in `test_deploy_stack.py`, `req("FR-450")`: the two confs' directive,
parsed, against `Settings.model_fields["max_request_body_bytes"].default` + 1 MiB. **Red:** no directive in `lb.conf`. **Green:**
`client_max_body_size` in `deploy/lb.conf`'s `server` block, and in `deploy/frontend.nginx.conf`, both `65m`.
Then A7's window.

**R3 — FD-1746.** In `backend/tests/test_data_nfrs.py`, `req("NFR-472")`:

- **T6** `test_a_purge_is_audited_with_the_versions_before_it`, on a dataset with two versions, by
  the service call as `test_lineage.py:511` does (Admin actor). It reads `AuditEventRow` for
  `dataset.subject_purged` and asserts A8. **Red:** `before` is `None`. DB window.
- **Green.** `datasets.py`, the `audit.record` call at `:1059`:

  ```python
  before={"versions": [{"id": str(v.id), "status": v.status} for v in versions]},
  ```

  in the loaded order (make it `order_by` the version number if the query has none, so the event is
  deterministic), the status serialised as the transition event does it (`:606`).
- `test_data_nfrs.py:153-154`, the docstring: "NFR-472, the transition class. Acknowledgements:
  `test_validation_reports.py`. Dictionary edits and rule-set changes: `test_api_datasets.py`. Purges:
  `test_a_purge_is_audited_with_the_versions_before_it`." The marker stays. `test_every_dataset_transition_…`'s
  body is unchanged.
- A9's planted breaks, same window.

**G — the gate.** Full code gate, both halves, SOLO, after a re-merge of `origin/main` and the GREEN
set. **Shared-fixture risk:** none in `conftest`; `main.py`'s middleware stack is under every API test,
which the gate covers. No migration, no contract regeneration. CI set from the three-dot diff:
`python`, `docs`, `history-policy`.

### Write set

- `backend/src/app/api/body_limit.py` (new), `backend/src/app/main.py`, `backend/src/app/config.py`,
  `backend/src/app/errors.py`,
  `backend/src/app/platform/datasets.py`.
- `backend/tests/test_api_body_limit.py` (new), `backend/tests/test_data_nfrs.py`,
  `backend/tests/test_deploy_stack.py`.
- `deploy/lb.conf`, `deploy/frontend.nginx.conf`, `deploy/README.md`.
- `docs/specs/07-platform.md`, `docs/specs/03-rating-engine.md`, `docs/specs/01-data-management.md`.
- LG-2076 under `docs/ledgers/`.
- At the mint: the SL-2075 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, the two
  essays and `docs/findings/register.md` (A11).

### Files shared with other groups

**D:** `deploy/frontend.nginx.conf`, `backend/tests/test_deploy_stack.py`, `docs/specs/07-platform.md`
(§8 there, §5 here). Code can be built in parallel with D; **merge after D.** **H:** FD-1488
changes `conftest_db`, under T6's fixture: a textual no-conflict, and a re-merge. **R:** `03`, different
rows. **Safe in parallel:** R, C, T, H, F for building; D for building, serial for the window.

## Hand-off (not this plan's writes)

- The GO: the maintainer. The windows and the gate slot: the lead.
- The SL-2075 row and mint: the lead. The LG: the executor. A11: the slice's auditor.
- Anything in `examples/` or the demo that posts a preview over the ruled limit: none is known, and
  `scripts/demo.py` is not in the write set. If the gate's demo stage hits it, that is a stop and a
  report, not a raised limit.

## Self-review

1. **Every cite was read** at `dae9637e`; the two framework facts at the locked versions. nginx's 1 MiB
   default is the documented default and is the one line not run; A7 runs it.
2. **Requirements by id**, no range.
3. **Placeholders:** `...` in `__init__` and `_detail` are named by the prose beside them.
4. **Each finding has a red by cause:** T1 to T3 for FD-1802, T6 for FD-1746, and a planted break where
   a class had no recorded red.
5. **The triage and essays are corrected:** a per-route cap is impossible, the proxy's limit was unread,
   and FD-1746's limb 2 is smaller than its essay.
6. **The rulings are carried verbatim.**
7. **Calendar:** Thu 12 Nov and Wed 11 Nov 2026, weekdays read with `date -d`.
