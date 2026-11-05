---
id: LG-8341
family: ledger
title: WK-1178 slice SL-8340 — DecimalStr serialises positionally (PL-8339, FD-1337)
status: active
created: 2026-11-05
owner: executor
tree: 9632320c797cabe58d5907700e83f091700d1a5d
phase: P2
work: WK-1178
slice: SL-8340
plans: [PL-8339]
corrected_by: []
relates: [FD-1337, PL-8339, RL-1329, RL-1343, FR-10, FR-21]
---

# LG-8341 — WK-1178 slice SL-8340: `DecimalStr` serialises positionally

**GO:** to-lead "2026-11-05 15:55:35 GMT"; DP-L1 to DP-L3 ruled "2026-11-05 10:36:35 GMT"; brief `brief-exec-sl8340-2026-11-05.md` (sha256 prefix 0577549ad10b).
**MERGE-ACK:** (added at merge)

## Tasks

### R0 — premises and spec (`614a7c2a`)

Base `ddec34fe`, merged by sha: C `4abb3798`, R1 `662867bb` (INDEX.md: theirs, regenerated). Reach re-run at the merged tree: `git grep -n -E ':\s*(tuple\[|list\[)?(DecimalStr|Relativity)\b' HEAD -- packages/model-schema/src ':!packages/model-schema/src/model_schema/money.py'` = **29 lines** (the plan's figure, unchanged by C and R1). Hash sites read: `suite_content_hash` (`regression.py:220`, reached by `MonotoneInInput.lower/upper`); `bundle_hash` (`compile.py:676`, hashes `JdmGraph` + `Pins`, neither holds a `DecimalStr`); `spec_hash` (`modelling.py:161`, none); `version_content_hash`/`definition_hash` (`diff_cache.py`, cells and keys); `canonical_payload` (`audit.py:116`, hashes the JSON a writer passes: A5's audit-writer sweep is owed in the window). FR-21 gained a dated clause (`docs/specs/00-overview.md`).

### R2 — red first (`9632320c`)

`packages/model-schema/tests/test_money.py`, `uv run --directory <wt> pytest -q packages/model-schema/tests/test_money.py` at `9632320c`: **9 failed, 25 passed**.
- T1 (8 cases: `DecimalStr` and `Relativity` x `1E-7`, `1.2E-28`, `1E+2` twice): `AssertionError: 1E-7` — `re.fullmatch('^-?[0-9]+(\.[0-9]+)?$', '1E-7')` is `None`.
- T2: `AssertionError` over three hashes for `10`, `1E+1`, `10.0` (`sha256:028228ef…`, `sha256:19a11329…`, `sha256:a50acf09…`).
- T3 control: green (`66000.440` kept).

### R2b — DP-L2 extended (to-lead "2026-11-05 16:14:34 GMT"), red first (`9a0a1ffe`)

A signed or exponent zero is the value 0: T4 `test_every_spelling_of_zero_gives_the_hash_of_zero`, `-0`, `-0.00`, `-0E+3`, `0E+3` each against `0`. Red on the committed tree without the draft: **4 failed**. The ruling also lets the window run two TEMP-table controls (`decexp_ctl.py`'s PG part, `regspell_ctl.py`) in a writable session on the `postgres` db, `CREATE TEMP TABLE` only, and extends the stored-instance predicate to negative-zero spellings; a stored `-0` changes its hash, and the STOP applies. PL-8339 is a filed plan, frozen at its date, so this record carries the dated line on its "no write" (G2/Needs) rather than an edit to it.

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

## PRs

(none yet — the push, PR and mint are not the executor's in this brief)
