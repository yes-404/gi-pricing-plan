---
id: LG-2057
family: ledger
title: WK-1178 slice SL-2056 — DecimalStr serialises positionally (PL-2055, FD-1337)
status: closed                 # active → closed (§1.2a)
created: 2026-11-06   # original date 2026-11-05, working id 8341, minted 2026-11-06
owner: executor
tree: 9632320c797cabe58d5907700e83f091700d1a5d
phase: P2
work: WK-1178
slice: SL-2056
plans: [PL-2055]
corrected_by: []
relates: [FD-1337, FD-2058, PL-2055, RL-1329, RL-1343, FR-10, FR-21]
---

# LG-2057 — WK-1178 slice SL-2056: `DecimalStr` serialises positionally

*(Minted 2026-11-06 as LG-2057 from working id 8341, with the plan PL-2055 (working id 8339), the slice SL-2056 (working id 8340) and the finding FD-2058 (working id 8400), in the SL-2056 PR.)*

**GO:** to-lead "2026-11-05 15:55:35 GMT"; DP-L1 to DP-L3 ruled "2026-11-05 10:36:35 GMT"; brief `brief-exec-sl8340-2026-11-05.md` (sha256 prefix 0577549ad10b).
**MERGE-ACK:** (added at merge)

## Tasks

### R0 — premises and spec (`614a7c2a`)

Base `ddec34fe`, merged by sha: C `4abb3798`, R1 `662867bb` (INDEX.md: theirs, regenerated). Reach re-run at the merged tree: `git grep -n -E ':\s*(tuple\[|list\[)?(DecimalStr|Relativity)\b' HEAD -- packages/model-schema/src ':!packages/model-schema/src/model_schema/money.py'` = **29 lines** (the plan's figure, unchanged by C and R1). Hash sites read: `suite_content_hash` (`regression.py:220`, reached by `MonotoneInInput.lower/upper`); `bundle_hash` (`compile.py:676`, hashes `JdmGraph` + `Pins`, neither holds a `DecimalStr`); `spec_hash` (`modelling.py:161`, none); `version_content_hash`/`definition_hash` (`diff_cache.py`, cells and keys); `canonical_payload` (`audit.py:116`, hashes the JSON a writer passes: A5's audit-writer sweep is owed in the window). FR-21 gained a dated clause (`docs/specs/00-overview.md`).

### R2 — red first (`9632320c`)

`packages/model-schema/tests/test_money.py`, `uv run --directory "$WT" pytest -q packages/model-schema/tests/test_money.py` at `9632320c`: **9 failed, 25 passed**.
- T1 (8 cases: `DecimalStr` and `Relativity` x `1E-7`, `1.2E-28`, `1E+2` twice): `AssertionError: 1E-7` — `re.fullmatch('^-?[0-9]+(\.[0-9]+)?$', '1E-7')` is `None`.
- T2: `AssertionError` over three hashes for `10`, `1E+1`, `10.0` (`sha256:028228ef…`, `sha256:19a11329…`, `sha256:a50acf09…`).
- T3 control: green (`66000.440` kept).

### R2b — DP-L2 extended (to-lead "2026-11-05 16:14:34 GMT"), red first (`9a0a1ffe`)

A signed or exponent zero is the value 0: T4 `test_every_spelling_of_zero_gives_the_hash_of_zero`, `-0`, `-0.00`, `-0E+3`, `0E+3` each against `0`. Red on the committed tree without the draft: **4 failed**. The ruling also lets the window run two TEMP-table controls (`decexp_ctl.py`'s PG part, `regspell_ctl.py`) in a writable session on the `postgres` db, `CREATE TEMP TABLE` only, and extends the stored-instance predicate to negative-zero spellings; a stored `-0` changes its hash, and the STOP applies. PL-2055 is a filed plan, frozen at its date, so this record carries the dated line on its "no write" (G2/Needs) rather than an edit to it.

### R2c — no rounding to the ambient precision (to-lead "2026-11-05 16:18:17 GMT"), red first (`496723cf`)

T5 `test_a_hashed_bound_is_never_rounded_to_the_context_precision` (two 38-digit bounds ending `.10` and `.20` stay distinct; `.10` and `.100` hash alike) and `test_a_hashed_bound_does_not_depend_on_the_ambient_decimal_context` (one case under `localcontext()` with `prec=5`). Red measured twice: on the committed tree without the draft, the first fails (`.10` and `.100` hash apart; the second passes, because `str` ignores the context); on the draft with `v.normalize()`, **both fail** (the two 38-digit values collide to one hash, and `prec=5` changes the hash of `123456.7890`).

### R3 — green (committed after the window)

Patch `~/gi-pricing-plan.local/scratch/sl-8340-decimalstr-positional/code.patch` sha256 `10093e77719436a0e6d172cb4df0fa445d1dc2276d8b048daf134bdf690ed2f5`, 3 files (`money.py`, `regression.py`, `test_money.py` docstring). `CanonicalDecimalStr` serialises through `_canonical_decimal`: zero first (`0`), else `value.normalize(Context(prec=max(len(value.as_tuple().digits), 1), traps=[Inexact]))` then `format(…, "f")`, as ruled. *(Corrected 2026-11-05, audit N4: the final form is `traps=[Inexact, InvalidOperation]`, as R2d and the code say; `[Inexact]` alone is the form T6 was red on.)* `test_money.py` 40 passed; `ruff check packages/model-schema` clean; `mypy` on `money.py` clean.

**`.normalize(` sites** — predicate `git grep -n '\.normalize(' -- backend/src packages/*/src` at head `496723cf` plus the draft, 9 lines, one is `unicodedata.normalize` (not a Decimal). Read by "does the output reach a hash site (A5)":
- `money.py:152` — this slice's own, exact context; reaches `suite_content_hash` via `MonotoneInInput.lower/upper` only.
- `approvals.py:157` `quantile_key`: a dictionary key and a message text (`rating_versions.py:1161-1177`), no hash; ambient precision, but a quantile has few digits.
- `ladder.py:169,172,177,183`: inside `localcontext(_ctx())`, builds a `LadderOperation` (a scoring-trace shape), no hash site reads it.
- `analysis.py:339` `_edge_text`: display text of a band edge, no hash.
- `rate_tables/operations.py:697` `_format_value` (FD-1648, SL 8322's R1): writes the cell text of an operation result; the cells reach `version_content_hash` (`diff_cache.py:48`), the diff cache's key, not a governed hash, and the rounding at 28 digits is ambient there. Outside this slice's write set; for the lead.
- `ingest.py:95`: `unicodedata.normalize`, not a Decimal.

### R2d — sNaN (to-lead "2026-11-05 16:33:41 GMT"), red first (`e24299c0`)

Validation refuses `sNaN`, `NaN` and `Infinity` for `CanonicalDecimalStr` (pydantic's Decimal validation, `allow_inf_nan` off; run: all four `ValidationError`), but `Holder.model_construct(value=Decimal("sNaN")).model_dump(mode="json")` reaches the serialiser and, with `traps=[Inexact]` only, wrote `'NaN'`. T6 `test_a_signalling_nan_that_skips_validation_is_not_written_as_a_number` is red on that form (`DID NOT RAISE`); the form is now `Context(prec=max(len(value.as_tuple().digits), 1), traps=[Inexact, InvalidOperation])`, the same as R2's, and T6 is green (`test_money.py` 41 passed). Patch sha256 `10093e77719436a0e6d172cb4df0fa445d1dc2276d8b048daf134bdf690ed2f5`.

### Disclosure

While syntax-checking the window scripts I ran `regspell.py` once against the shared server, before the grant (about 16:2x UTC): SELECT only, READ ONLY transactions, `PGOPTIONS` read-only; it printed `databases 4 | with regression_suite_versions 2 | version rows 0`. That output is not the window result and is not used as one; the window runs it afresh.

## Re-measure (A3 to A5)

Window 2026-11-05 19:28:53 to 19:50:10 UTC, single-tenant, read-only (TEMP-table controls only, in a session on the `postgres` database), lead's grant and "No STOP" ruling to-lead "2026-11-05 19:50:54 GMT". Scripts and logs: `~/gi-pricing-plan.local/scratch/sl-8340-decimalstr-positional/` (`SHA256SUMS`, `out/`).

**no stored DecimalStr instance found on this stack; Postgres near-empty: 5 rows across 3 DBs, regression_suite_versions 0: a zero over a near-empty corpus: controls red (exponent 2 of 3, regspell 3 of 5); MinIO 7 444 of 35 544 read**

- **A3 tracked blobs** (`decexp.py`, `decexp2.py`, `decexp3.py` at head `bb4cf209`): 2814 files; 135 quoted exponent strings in 31 files, all prose, source or tests, none in a data file; the control (`decexp_ctl.py`) counted its planted values.
- **A3 PostgreSQL** (`decexp_pg.py`, `regspell.py`, `rowcount.py`): 3 databases, 64 tables, 5 rows (alembic_version 1, environments 3, tenant_marker 1); exponent-form rows 0; `regression_suite_versions` 1 database, 0 rows, 0 bound values, 0 non-canonical spellings including `-0` and `0E+3`. Controls (`decexp_ctl.py` PG part, `regspell_ctl.py`): exponent 2 of 3 planted rows, regspell 3 non-canonical of 5 bounds.
- **A3 MinIO** (`minio_scan.sh`, `minio_scan4.sh`; control `minio_ctl2.log`, 2 objects, 1 hit counted (`minio_ctl.log` counted 0: an earlier failed run)): 7 444 of 35 544 objects read (corrected 2026-11-05 by the audit: 578 + 19 + 6 847; 28 100 unread), in 6 buckets. The 28 100 unread are all in `gip-test-blobs`, test artifacts by name, out of this slice's scope. 19 objects with a quoted exponent-form string, all in `gip-blobs`, all under the key `relativity` (rate-table cell text, not a `DecimalStr`-typed field): they belong on FD-1648, origin unproven.
- **A4:** both counts are 0 for the shape this slice changes, over the corpus above; no version bump, no stop.
- **A5 hash sweep:** R0 above (`suite_content_hash` the only site a `DecimalStr` reaches); the `.normalize(` sweep in R3. Reading corrected 2026-11-05 (the audit): by the plan's predicate `git grep -n -E 'sha256|_canonical_sha256' 71158bdd -- backend/src packages/model-schema/src packages/pricing-core/src` the sweep is 40 files / 204 lines, not 5 sites. 11 audit writers pass `model_dump(mode="json")` payloads (`backtests.py:245`, `comparison.py:197`, `metrics.py:454`, `modelling.py:940`, `objectives.py:665`, `rating_versions.py:591,723,758,774,786`, `transparency.py:68`); `AuditEvent.recompute_hash` hashes the stored `payload` dict (`audit.py:96-118`), so no stored hash moves; a new event differs only in spelling, and only for an exponent-form value.
- **Guards:** template `alembic_version=1 environments=3 tenant_marker=1`, `redis-cli -n 0 dbsize` 56, `pg_database` 4 rows (md5 `0e557aec019c29ead221153636bd8d08`), `mc ls g/` 6 buckets: each the same before and after.


## N1 — the bound on writing (to-lead "2026-11-05 20:46:28 GMT", ruled (a))

**Reach (probe at head `955ea8ab` + the writer, `~/gi-pricing-plan.local/scratch/sl-8340b/probe_http.py`, TestClient over `create_app`, no DB):** the real `ReconcileRequest` (`api/peril_structures.py:85`, field `tolerance` at :120) *validates* `1E+999999999` (200 on an accept route); a route that *echoes* it answered **500 `INTERNAL_ERROR`** for `1E+400` and `1E-400` (red log `bound-red.log`), now **422 `DECIMAL_OUT_OF_RANGE`** (`bound-green.log`, 5 passed). `pydantic_core` does not chain the cause through FastAPI's serialiser (`__cause__` is None), so `errors.py` `_handle_serialization_error` reads the exception's type name in its message. The real reconcile route (`peril_structures.py:256`) does not echo the field: `reconcile_payload` (`platform/perils.py:238`) carries `str(tolerance)` and the route answers a Job (held by `test_the_reconcile_job_payload_does_not_write_the_tolerance_positionally`). **HTTP reach on a shipped path: none found; the 500 was reachable by any route that echoes a request `DecimalStr`, so the coded 422 is the backstop. No FD owed on this limb.**

**Fields of the three types (predicate, run at `955ea8ab`):** `git grep -n -E ':\s*(tuple\[|list\[)?(DecimalStr|Relativity|CanonicalDecimalStr)\b' HEAD -- packages/model-schema/src ':!packages/model-schema/src/model_schema/money.py'` = 29 lines, plus `backend/src/app/api/peril_structures.py:120` (the backend has one). By model name, request-bearing: `UpliftTableParameters.percentage`, `UpliftByFilterParameters.percentage`, `FloorAndCapParameters.floor/cap` (`rating.py:1389-1407`), the approval and dislocation thresholds (`approvals.py:152-153`, `rating.py:135-137`, `dislocation.py:52`), `modelling.py:344`, `ReconcileRequest.tolerance`; the rest (`exposure_years`, `profiles`, `diagnostics`, `Reconciliation.tolerance`, `imputed_share`, `CanonicalDecimalStr` `lower/upper`) are stored or derived. Not verified route by route; the writer and the handler do not depend on the split.

**R2 `_format_value`** (`sl-8345-r2-cell-hard-error@cda3c0dc`, `operations.py:692`; read only): reached with `old * (1 + percentage)` (:760, :789). The ambient context's Emax (999999) bounds the text to about 1 MB; `_validate_result` (:587) then runs `validate_rate_table` on the result rows, and `cell_parses` (:331) refuses it, coded, after the write. No change here.

**Closing lines (2026-11-05, exec-sl8340c, LAST-1, to-lead "2026-11-05 21:01:00 GMT"):** `DECIMAL_OUT_OF_RANGE` is owned by `00-overview.md` §5.3's "Error codes owned by this module" line (one owner; audit-docs check 10) and sits in `_GENERIC_ERROR_CODES` in `backend/src/app/errors.py`; FR-21's "no module's block lists it" amended to match. The handler carries a comment: the match is on pydantic's message text because pydantic_core does not chain `__cause__` through FastAPI's serialiser; fragile by that known cause; pinned by `test_decimal_write_bound.py`.

## LAST-1's two reds, ruled (to-lead "2026-11-06 07:42:30 GMT"; exec-sl8340f, 2026-11-06 08:14:56 UTC)

Edits made on `cb1b83af` after LAST-1's gate ENDED (08:12:25); **nothing has been run on them yet** (no test, probe or audit-docs: a demo runs). Their proof is the DB window the lead grants next; the lines below say what it must show.

1. **RED 1, `test_error_sinks.py`:** a `_SINKS` row for `("backend/src/app/errors.py", "_handle_serialization_error", "str(exc)")`: a substring classifier only, nothing stored, logged or echoed; `test_decimal_write_bound.py:56` asserts the value is not in the response. No new sentinel.
2. **RED 2, `test_api_rate_tables.py` (`test_bulk_operation_with_a_huge_percentage_is_a_coded_422_not_a_memory_fault`):** asserts `DECIMAL_OUT_OF_RANGE`, a small body, and no new version (`GET /rate-tables/{slug}@2` is 404). Docstring says which bound fires: the writer's, at `api/rate_tables.py:217` (`body.parameters.model_dump(mode="json")`), before the platform call, never reaching `_format_value`. `RATE_TABLE_CELL_UNPARSEABLE` (03 §4.2) is for a cell; a `percentage` is not one.
3. **ADDITION, the computed-cell limb through the route: a value exists, so the route test is added** (`test_bulk_operation_whose_computed_cell_passes_the_bound_is_a_cell_422`). Arithmetic: the writer bound and the cell bound are one constant, `MAX_POSITIONAL_EXPONENT = 308` (`money.py:132`; `_positional` admits `adjusted()` in [-308, 308]; `_format_value` the same, `operations.py:714`). `uplift_table` computes `old * (1 + percentage)` (`operations.py:792-794`). `percentage = 9E+308` has `adjusted() = 308`, so the writer admits it; the seeded cells are 1.92, 1.41, 1.12 (`_LEVELS`), and `1.92 * (1 + 9E+308) = 1.728E+309`, `adjusted() = 309`, so `_format_value` refuses the computed cell with `RATE_TABLE_CELL_UNPARSEABLE`. Any `percentage` with a computed adjusted exponent of 309 does it, so "route-unreachable" does not apply. Unit proof stays (`packages/pricing-core/tests/test_rate_table_bulk_ops.py:201`, `:251`); import route proof stays (`test_api_rate_tables.py` imports at the lines the ruling names). Whether the route maps the `ValueError` to a coded 422 is what the window shows; red there is a finding, not a test to weaken.
4. **WORDING, `errors.py`:** the `detail` is now "An exact decimal has an exponent beyond 308 in either direction and cannot be written."; the handler's docstring reads "cannot be written" in place of "no response can carry". Nothing else in `errors.py`. `test_decimal_write_bound.py` pins no detail text (the ruling's grep).
5. **GREEN set gains** `backend/tests/test_error_sinks.py` and `backend/tests/test_api_rate_tables.py` (common brief item 45).
6. **Commit order, the owed read (to-lead "2026-11-06 07:47:44 GMT", adopted):** By request-bearing field, every `DecimalStr` / `CanonicalDecimalStr` field persists through a `model_dump(mode="json")` inside the transaction before commit (bulk-operation `created_by_operation`, approval-policy row and audit, dislocation job spec, `POST /bandings` body, peril-structure perils, regression-suite hash then content), so the writer raises before the commit and the unit of work rolls back. Predicate: `git grep -n -E '\.model_dump\(' cb1b83af -- backend/src packages/*/src | grep -v 'mode="json"'` = 21 lines, none reaches a stored column with a writer-type field; no `Relativity` field exists outside `money.py`. The enumeration's regex missed three names, covered by this read: `band_edges_pct`, `abs_change_pct_quantiles`, and the `PositionalDecimalStr` sites (the alias of `DecimalStr`, `money.py`, so the same writer). One exception, NOT a poisoned row: `POST /peril-structures/{id}/reconcile` carries `tolerance` into the Job as `str(tolerance)` (`perils.py` `reconcile_payload`), so a tolerance past 308 commits a Job and answers 202; the writer fires in the worker's `store()`, the Job fails and nothing is written. Read, unprobed; the DB-free probe (item 7) follows the demos.

7. **Window and probe results (exec-sl8340f, 2026-11-06, head `ebc45f5f`, tree `67f15052`).** DB window `sl8340f` 08:39:34 to 08:44:09 UTC, no gate beside it; template guard `alembic_version=1 environments=3 tenant_marker=1` at both ends, `redis -n 0 dbsize` 56 at both ends, redis `-n 12` 0 at both ends, copy `gipricing_sl8340f` gone, bucket removed. Script `scratch/sl8340f-win.sh`, logs `scratch/sl8340f-*.log`. Runs, each rc 0: `test_error_sinks.py` 13 passed; `test_api_rate_tables.py` 99 passed, including the huge-percentage test (RED 2) and the `9E+308` computed-cell route test (a 422 `RATE_TABLE_CELL_UNPARSEABLE`, no `@2`; green, so item 3's route limb is proved at HTTP); `test_decimal_write_bound.py` 5 passed; `test_api_authorisation_sweep.py` 9 passed; `test_errors.py` 16 passed. `ruff check .` rc 0. Red-first for the no-new-version assert: a planted `bulk_operation` that commits a version before the raising call made the huge-percentage test FAIL (`GET …@2` answered 200); the plant was reverted and `git status` was clean.
   **Probe (DB-free, unit call; `scratch/sl8340f-probe/probe_tol.py`):** the reconcile store path with tolerance `1E+400`: payload `1E+400`; `Reconciliation` constructs; `model_dump(mode="json")` (the line `record_reconciliation` runs) raises `PydanticSerializationError`; the error text the worker stores via `safe_job_error_text` is `'PydanticSerializationError'`. Asserted: no `1E+400`, no digit run, no `400` in it. Control: the same script on `str(exc)` fails the digit-run assert. **Clean, NFR-499 not touched.** FD-2058 drafted at `scratch/aud-sl8340w/fd-8400.md`, LOW, WK-1178, carried to the P2 closure list; no fix in this slice.

## PRs

This PR; its number, squash commit and merge date are written at the merge's date-of-record.

## Audit

**Auditor:** aud-sl8340 (sonnet 5.5, medium). **Object:** detached worktree `aud-sl8340` at `71158bddb59cc92ea46788a1c106b651ae2aeae7`, tree `8e4ec35b0038f5c55dd84dc8c2f667a7af65f5d4`, audited 2026-11-05 20:40–20:45 UTC against `origin/main` `cded9f0e`. **Status: PROPOSAL — the lead adopts, amends or rejects.**
**Range:** `origin/main...HEAD` is 31 files because the branch merged C `4abb3798` and R1 `662867bb` **by sha**; neither is an ancestor of `origin/main` today (`git merge-base --is-ancestor`, both rc 1). The slice's own commits (`git diff --name-only 7df6d270 HEAD`) are 6 files, all in the Write set (`money.py`, `regression.py`, `test_money.py`, `00-overview.md`, LG 8341, INDEX). A PR cut before C and R1 merge carries their commits; after they merge the three-dot shrinks to the Write set.

| Item | Verdict | Evidence (tree `71158bdd`) |
|---|---|---|
| A1 write set | MET for the slice's own commits | the 6 files above; A1 read literally on `origin/main...HEAD` is not true until C and R1 merge |
| A2 spec first | MET | `614a7c2a` (00) precedes `9632320c` (first test) and `71158bdd` (code) |
| A3 re-measure | MET with two corrections | denominators and controls present; **LG says 7,448 read, 28,100 unread: 7,448 + 28,100 = 35,548, not 35,544.** `done_gtb.log` 6,847 + `done_1711.log` 19 + 578 (`gip-blobs` 564, `aud933` 1, `compiled-for` 2, `score-batch` 11) = **7,444**; 35,544 − 7,444 = 28,100. Write 7,444 (the 4 are the in-flight `xargs` workers if that was the source). The MinIO control is `minio_ctl2.log` (1 of 2 counted); `minio_ctl.log` counted 0 and is an earlier failed run, left in `out/`. Item-37 headers: `decexp_ctl.log` line 1 is `head=` followed by a date, not a sha; `decexp.log` ran at `bb4cf209`, not the audited head |
| A4 rule applied | MET on what was read | both counts 0; no bump; PG corpus is 3 databases / 64 tables / 5 rows (the 2026-09-30 run: 81 / 3,841), so the zero is over a near-empty corpus, as the LG says; 19 MinIO hits are the `relativity` cell text of compiled bundles (FD-1648), not a `DecimalStr` field; 28,100 `gip-test-blobs` objects unread, out of scope by the lead's ruling |
| A5 hash sweep | **NOT MET as written** | the LG names 5 sites; `git grep -n -E 'sha256\|_canonical_sha256' 71158bdd -- backend/src packages/model-schema/src packages/pricing-core/src` is 40 files / 204 lines, and the audit-writer sweep the R0 text calls "owed in the window" is not in the Re-measure section. Auditor's own read: 11 writers pass `model_dump(mode="json")` payloads (`backtests.py:245`, `comparison.py:197`, `metrics.py:454`, `modelling.py:940`, `objectives.py:665`, `rating_versions.py:591,723,758,774,786`, `transparency.py:68`); `PerilStructure` (`rating_versions.py:786`) and the approximation check carry `DecimalStr`. A stored event is not re-serialised: `AuditEvent.recompute_hash` hashes the stored `payload` dict (`audit.py:96-118`), so no stored hash moves; a new event differs only for an exponent-form value |
| A6 red first | MET (LG lines, not re-run) | T1 8 red + T2 red at `9632320c`; T4 4 red; T5 both red twice; T6 red on `traps=[Inexact]` |
| A7 schema holds | MET | `pytest packages/model-schema/tests/test_money.py` **41 passed** (`aud-sl8340/money.log`, rc 0); own probe: 15 spellings incl. `0`, `-0`, `-0.00`, `0E+3`, `1E+2`, `1.2E-28`, 40 digits, 60 digits all match the pattern and round-trip by value; `localcontext(prec=3)` leaves `123456.789`; canonical is idempotent |
| A8 spelling and hash | MET | T2/T3 in the 41 passed; `test_regression.py` 27 passed (rc 0) |
| A9 other hashes unchanged | MET for the slice; test_contracts OWED-TO-GATE | `git diff --stat 7df6d270 HEAD -- docs/contracts` empty (the one-line `generated.json` diff on `origin/main...HEAD` is C's `64525585`); `generate-contracts.py --check`: "58 generated contracts match the models", rc 0 |
| A10 ladder unchanged | MET | the only edit to an existing test is the `test_money.py:133` docstring |
| A11 no pandas/float | MET | `format(v, "f")` on `Decimal` only |
| A12 GREEN + gate | OWED-TO-GATE | the GREEN set is the suite (plan); SOLO full gate not yet run. Import-closure files that import the changed modules and are named, not looped: `backend/tests/test_contracts.py`, `test_rating_versions.py`, `test_regression_runs.py`, `frontend/.../RegressionSuiteView.test.ts`, `pricing-core/tests/test_rating_ordered_input.py`, `test_replay.py`, `test_testing.py`, `test_testing_determinism.py` |
| A13 FD closing act | drafted | `aud-sl8340/FD-1337-closing-act.md` |

**Findings against the slice**
1. **N1 — positional expansion is unbounded (new).** Validation still accepts `1E+999999999` (G3) and `DecimalStr`/`Relativity`/`PositionalDecimalStr` now write it positionally: `model_dump(mode="json")` returned a **1,000,000,000-character string in 2.4 s**, and `1E+9999999999999` raised `MemoryError` under a 3 GB address-space limit (`aud-sl8340/probe2.py`); `str()` was compact. `CanonicalDecimalStr` raises `Inexact` for exponents beyond the default `Emax` instead (fail-loud). Before this slice only the ladder's `PositionalDecimalStr` fields (engine outputs) had the shape; now all request-bearing fields do (e.g. `api/peril_structures.py:120`). HTTP reach was **not** probed (no app, DB-free). Proposed: an FD for the lead and the maintainer's severity and fix choice (a validation bound contradicts G3's "input unchanged"). Not a defect in the ruled behaviour; a consequence of it.
2. **N2 — the FR-21 clause lags the code.** `00-overview.md` says hashed bounds "drop trailing zeros"; it does not say every zero is `0` (T4) or that normalisation is exact, not context-rounded (T5). One dated sentence closes it.
3. **N3 — `NaN`/`Infinity` via `model_construct` are written as `NaN`/`Infinity`** by every type (`sNaN` alone raises on the canonical type); validation refuses all three. Unchanged from `str()`; T6 covers sNaN only. Note, no action.
4. **N4 — LG wording:** the R3 paragraph says `traps=[Inexact]`; the code and R2d say `[Inexact, InvalidOperation]`. The patch sha `10093e77…` is the final form (reverse-applies clean to the head).
5. **audit-docs** at the head (`aud-sl8340/audit-docs.log`, rc 1): FAILED (7), all check 31 (gaps 2006–8321, 8323–8327, 8329–8339, 8341–8345: working ids) and check 32 (`FD 1569` in `PL 8321`, which is R1's plan; `FD 1569` is in neither this tree nor `origin/main`'s INDEX) *[the two ids are written in space form at the mint: in the hyphen form the auditor wrote, neither resolves in this tree's INDEX, so check 32 reads the quotation as a citation]*. No failure on this slice's content.

**Requirement verdicts:** FR-21 (positional, one spelling per hashed value) delivered and tested; FR-10 unaffected. No requirement without evidence except the OWED-TO-GATE rows above.
**Verdict (proposed): STANDS, subject to** the A3 count correction, the A5 sweep recorded in the LG, N2's sentence, N1 ruled or filed, and the SOLO gate.
(The PR number and squash commit are written at the merge's date-of-record.)

### Adoption, gate and close (written at the mint, 2026-11-06, by exec-mintl1)

**Adoption.** The lead adopted aud-sl8340's FINAL (from-lead, 2026-11-05 20:46:10 GMT: "LAST-1 stands subject to: 7,444 correction, A5 sweep in the LG, N2 sentence, N1 ruling (positional output of an unbounded exponent), gate"). Each condition is met in this ledger: the 7,444 count, the A5 sweep and N2's sentence (above, 2026-11-05); N1 ruled (a) at "2026-11-05 20:46:28 GMT" (the N1 section); the gate (below). The owed reads were added by the lead's ruling of "2026-11-06 07:42:30 GMT" and adopted at "2026-11-06 07:47:44 GMT" (aud-sl8340w: no poisoned row; one LOW finding, FD-2058).

**Gate (the full gate of LAST-1, paired; lines read from `scratch/sl8340-gate/gate/gate.log` on 2026-11-06).** It ran on head `cb1b83afe7dca94a485bbe404c65480224edc089`, tree `10b078def719fae1888786d8473061a05a4eda99`, 06:10:22 to 08:12:25 UTC, paired with SL 8377's gate in the partner slot. The edits of the "two reds" section and the window of item 7 were made after it, on `ebc45f5f` and `457190a1`. The lines: ruff, mypy, import_linter, req_coverage and contracts rc 0. pytest rc 1: `15 failed, 7321 passed, 27 skipped, 5 xfailed, 154 warnings in 5248.41s (1:27:28)`; the 27 skipped equal the baseline. The 15 FAILED are item 31's 13 (the eight docs-audit files: `test_audit_docs_finding_citations` 1, `test_audit_docs_ids` 2, `test_audit_docs_process_core_digest` 2, `test_audit_docs_w37_11_ceiling` 1, `test_doc_index` 1, `test_register_lint` 3, `test_register_owed` 1, `test_repository_invariants` 2) plus the two ruled reds (`test_api_rate_tables.py::test_bulk_operation_with_a_huge_percentage_is_a_coded_422_not_a_memory_fault` and `test_error_sinks.py::test_every_failure_sink_on_a_quote_input_path_is_accounted_for`), both ruled at "2026-11-06 07:42:30 GMT" and proved green in the window of item 7. audit_docs rc 1 on check 31 only, naming the slice's own working ids. Frontend, all rc 0: install, generate:api, lint, type-check, test, build. Demo seeded (digests equal), `demo.py --journey wf-699` rc 0, 1522 s; dislocation 512 s. `D7 limbs vs baseline ... UNMOVED`: D7's total and both attribution limbs equal on the 19985-policy sample (rate table edits +485990825 == +485990825; NCD ladder and expense loading +3851186 == +3851186; sum +489842011 == +489842011). This says nothing about whether any price moved outside that sample.

**Item 42 (the `SL-` row).** The row for this slice did not exist on `origin/main` `9852f004b3c4`: it was added by the mint as `active`, and this audit commit sets it `closed`. Nothing else was found open.

**FD-1337** is closed by this PR (the closing act below, in `docs/findings/`). **FD-2058** is born open, LOW, owner WK-1178, carried to the P2 closure record's carry-forward list; no fix here. Its essay is `docs/findings/FD-02058-a-tolerance-past-the-write-bound-is-accepted-at-202-and-fails-the-job-after-the-compute.md`.
