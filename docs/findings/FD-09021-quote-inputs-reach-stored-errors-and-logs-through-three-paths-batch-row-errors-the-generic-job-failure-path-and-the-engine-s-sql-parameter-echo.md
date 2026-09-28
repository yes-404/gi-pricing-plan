---
id: FD-9021
family: finding
title: Quote inputs reach stored errors and logs through three paths: batch row errors, the generic Job failure path and the engine's SQL parameter echo
status: active
created: 2026-09-28
owner: auditor
tree: 9fa2b833e00281a36109183a12efc9d7152225e9
corrected_by: []
relates: [WK-1178]
---

# FD-9021 — Quote inputs reach stored errors and logs through three paths: batch row errors, the generic Job failure path and the engine's SQL parameter echo

**Severity: high.** The deputy ranked it high in his entry of 2026-09-28 22:24:08 BST ("Batch-scoring
stored leak: CONFIRMED in code, ranked HIGH now; the sanitiser must live in pricing-core"). His
bar was a production path shown with a concrete input, and the batch path is shown in the code.
The after-T7 stored-row demonstration below is this record's **evidence**, not a condition of the
rank. The auditor filed it on 2026-09-28, on the lead's instruction. executor-s2 found the generic
sink while fixing WK-672 Slice 3's regression handler (a sanitised re-raise, commit `45c0dcd8`, on
the Slice 3 branch), and auditor-a found the engine's parameter echo (F2). This is **one finding
with three entry points**, not three: the deputy ruled they share one fix.

## Finding

**Three entry points, one cause: text a library builds from its input is stored and logged.**

1. **Batch row errors (production, shown in the code).** `score_batch` catches a per-row
   `ValidationError` and stores `str(exc)`, `input_value` included, as the row's `error_message`
   in the batch output parquet and in the Job result's `error_samples`. The output parquet is a
   Job-result blob that the workspace can download through `/blobs` since #868.
2. **The generic Job failure path.** Described in the next paragraph.
3. **The engine's SQL parameter echo.** `create_async_engine` is built without
   `hide_parameters=True`, so any `DBAPIError` carries `[parameters: …]`. **Setting it is not
   enough (executor-s1's correction).** The Postgres driver's own text also echoes values:
   `DETAIL: Failing row contains (…)`, and asyncpg's *"invalid input for query argument $1:
   'value'"*. The fix therefore reduces a `DBAPIError` to its type, SQLSTATE and constraint, and
   sets `hide_parameters` as well. **Measured below:** the asyncpg argument text and the
   `DETAIL:` line of a foreign-key violation both carried values.

For the second entry point, for every Job handler, an unexpected exception is stored in the Job's
error (`JobError.message`, in the database) and logged with its traceback to the process log.
NFR-499 says quote inputs are never logged in full outside sampled traces. A Pydantic
`ValidationError` raised inside a handler that validates a quote input prints the failing value as
`input_value=…`, so that value reaches the stored Job error and the process log.

**Premise correction (executor-s1, read from the code and verified by the auditor):** the
*persisted* Job logs do **not** carry the traceback. `JobLogCapture.emit` (`worker/logs.py:45`)
stores only `record.getMessage()` (`:47`), never `exc_info`, and its docstring says *"Only the
formatted message is stored"* (`:8`). The generic path's sinks are therefore **`JobError.message`**
and the **process log**, where the JSON formatter puts `exception = self.formatException(...)`
(`observability/logging.py:60`–`:61`). There is also a **chained-exception hole**: a handler that
re-raises `raise PlatformError(...) from validation_error` prints the `ValidationError` text in
that traceback, even though the stored `JobError` then carries only the `PlatformError`'s detail.

## Evidence

At `origin/main` `9fa2b833`, `backend/src/app/worker/tasks.py`:

- `:224` `_log.exception("job handler failed", extra={"job_id": str(job_id)})` logs the
  traceback to the process log, which prints `str(exc)`.
- `:230` `message=f"{type(exc).__name__}: {exc}"` builds the `JobError` that `_fail` (`:252`)
  writes to the Job row, so it is readable through the Jobs API.
- `:246` `await capture.flush_to_database()` writes the run's captured log records to the database.
  **That does not store the traceback** (see the premise correction above): `JobLogCapture.emit`
  keeps `record.getMessage()` only, and `_log.exception("job handler failed", …)`'s message is that
  fixed string.
- The comment above (`:213`–`:218`) says *"a handler that puts a credential in an exception string
  is a bug in the handler"*. That covers a handler that formats its own message. It does not
  cover a library exception whose own `str()` contains input.

Measured, at the same tree in a detached checkout after `uv sync --all-packages`:
`QuoteContext.model_validate({'purpose': 'new_business', 'quoted_at': '2026-01-01T00:00:00',
'effective_date': 'not-a-date', 'inputs': {...}})` raises `ValidationError` whose text includes
`effective_date … [type=date_from_datetime_parsing, input_value='not-a-date', input_type=str]`.

**Handlers that validate a quote input at `origin/main`:** `backend/src/app/worker/trace_handlers.py:79`,
`ctx = QuoteContext.model_validate(row.pending_quote_context)`, in the `score.trace_produce` handler.
The other registered handlers (`data_handlers`, `model_handlers`, `rate_table_handlers`,
`rating_handlers`, `scoring_handlers`) take dataset or artifact references. `scoring_handlers.py:310`
validates `ArtifactRef` values only. WK-672 Slice 3's `rating.regression` handler is not on
`main`; per the lead it was the first to take generated quote inputs.

## Root cause found by auditor-a (F2): the engine echoes SQL parameters

`backend/src/app/db/session.py:40` builds the engine as
`create_async_engine(settings.database_url.get_secret_value(), pool_pre_ping=True, future=True)`.
It does not set `hide_parameters=True`; `git grep -n hide_parameters origin/main -- backend`
prints nothing. SQLAlchemy's `DBAPIError` text carries `[parameters: …]`, the bound values of the
failed statement. So any database error raised in a handler carries the row values it was writing
or reading, and the generic clause above stores that text in the Job's error and logs it. The values include persisted
quote inputs: `ScoringTraceRow.pending_quote_context` (`db/models.py:2164`, a whole
`QuoteContext` in JSONB), and, once Slice 3 lands, its run row's counterexample and case blob. A
database error while updating such a row (an integrity error, a serialization failure, a dropped
connection mid-statement) would print them. **Measured:** see *Demonstrated* below: a failing statement through a handler stored the parameter echo and the driver text in `JobError.message`. The lead relayed the finding from auditor-a.

## Demonstrated (measured 2026-09-28 at `origin/main` `7f5b4ea7`)

`tasks.py`, `db/session.py`, `worker/logs.py` and `rating/score.py` are byte-identical between `9fa2b833` and `7f5b4ea7`
(`git diff 9fa2b833 7f5b4ea7 --stat` over those four paths prints nothing). A throw-away test, run with `uv run pytest -q
-p no:randomly -s` at `nice -n 10` against a per-tree database, registered a handler for `JobKind.MODEL_FIT` and ran it
through `execute_job`, with the sentinel `ZZ99-SENTINEL-9ZZ` as the offending value. Three failures, each read back from
the stored Job row:

| Failure raised inside the handler | Sentinel in stored `JobError.message` | in persisted `job_logs` | in the process log |
|---|---|---|---|
| a `ForeignKeyViolationError` inserting a `workspace_settings` row whose `key` is the sentinel | **yes** | no | yes |
| an `asyncpg` `DataError`: the sentinel as an integer column's argument | **yes** | no | yes |
| a `ValidationError` from `QuoteContext`, the sentinel as `effective_date` | **yes** | no | yes |

- **The stored text carries SQLAlchemy's parameter echo.** The FK case's stored message contains
  `[parameters: (UUID('…'), UUID('8402da62-…'), 'ZZ99-SENTINEL-9ZZ', '{"v": 1}')]`, and
  `DETAIL:  Key (workspace_id)=(…) is not present in table "workspaces".` So `hide_parameters` matters.
- **The driver's own text carries the value even without it.** The bad-argument case's stored message contains
  `invalid input for query argument $2: 'ZZ99-SENTINEL-9ZZ' ('str' object cannot be interpreted as an integer)`,
  and the same `[parameters: …]` line. This confirms executor-s1's correction that `hide_parameters=True` alone is not
  enough: the asyncpg message is not one of SQLAlchemy's parameters. I did not run a case with `hide_parameters=True`
  set, so which lines survive it is read from the message text, not measured.
- **The persisted Job logs did not carry the sentinel in any case**, confirming the premise correction
  (`JobLogCapture.emit` stores `record.getMessage()` only).
- **The batch row.** `score_batch` on a two-row frame, the second row's `effective_date` the sentinel, against the real
  bundle of `packages/pricing-core/tests/test_rating_score.py`, returned an output row `error_code = 'ValueError'`,
  `error_message = "Invalid isoformat string: 'ZZ99-SENTINEL-9ZZ'"`. The value is in the string that becomes the output
  parquet's `error_message`. The failing input there is a plain `ValueError` from `date.fromisoformat`, before Pydantic is
  reached. The first row also errored, on an `ArtifactRef` (`rating_version:x@1` is not a valid reference), with
  `input_value='rating_version:x@1'` in its message.
- **Not run:** the stored Job-result `error_samples` for a full batch Job, the parquet written to the blob store and
  downloaded through `/blobs`, and the integer-`quote_id` frame-build path (the entry-point-1 sub-case above). The output
  frame is what the handler writes to the parquet, so the row content is the stored content, but the blob round trip was
  not observed.

The script is kept outside the repository, as `trees/auditor-b-883.demo-fd9021.py`.

## What is not shown

- **The stored parquet and `error_samples` observed.** The batch output row is demonstrated above at the frame level;
  the blob-store round trip is not.
- **The generic path's reach at `main`.** `trace_handlers.py:79` validates a context that the
  `/score` route already accepted, so a `ValidationError` there is expected only after a schema
  change. No failing case was constructed for the generic clause.
- **What survives `hide_parameters=True`.** The `[parameters: …]` echo, the asyncpg argument text and the
  `DETAIL:` line are all observed above. No run set `hide_parameters=True`, so what remains after it is read from
  the message text. `DETAIL: Failing row contains (…)` (a not-null or check violation) was not triggered.
- **Whether the persisted Job logs ever carry input.** They store the log message only, so they carry
  input only if a handler formats input into a message string. This record did not sweep the handlers
  for that.
- **What a leaked field is worth.** A validation error names one failing field's value, not the
  whole context. NFR-499's wording is *"in full"*. The deputy's ranking stands on the batch path,
  where the stored text is downloadable by the workspace.

## Entry point 1 in detail: the batch route, and the paths outside per-row isolation (read at `9fa2b833`)

The deputy verified this path in the code (`score.py:955`, `:961`, `:881`–`:890`, `:963`–`:973`):
`_row_to_ctx(row)` builds the Pydantic `QuoteContext` inside the `try`, `except (ValueError,
RuntimeError)` catches its `ValidationError`, `_batch_error_code` falls back to
`(type(exc).__name__, str(exc))`, and the message is stored in the output row. Any batch upload
with one malformed input field reaches it on the production batch route. This record ran it at the frame level (see *Demonstrated* below).

- **Inside the isolation, by design, and not the generic clause.** `pricing_core/rating/score.py:942`
  (`_score_batch_row`) catches `(ValueError, RuntimeError)` per row (`:961`). `_batch_error_code`
  (`:881`, its fallback at `:891`) returns `str(exc)` as the row's `error_message` for any exception that does not follow the
  `CODE: message` convention, so a `ValidationError` from `QuoteContext(...)` (for example an
  integer `quote_id`, which the model types as `str | None`) writes its full text, `input_value`
  included, into the output parquet row and into the Job result's `error_samples`
  (`scoring_handlers.py`, `error_samples`). This is a stored row, not a leak through
  `JOB_HANDLER_FAILED`, and the row's blob is workspace data. It is named here because it is the
  same kind of text.
- **Outside the isolation: `KeyError`.** `_score_batch_row` does not catch `KeyError`, which is
  neither `ValueError` nor `RuntimeError`. A missing `purpose` column (`_row_to_ctx`,
  `:906`, `row["purpose"]`) reaches the generic clause, but a `KeyError` prints the key name, not a
  value.
- **Outside the isolation: the frame build.** `_score_batch_chunk` (`:988`) builds
  `pl.DataFrame(rows, schema=_BATCH_OUTPUT_SCHEMA)` (`:990`) from the rows. An error row copies the raw
  `row.get("quote_id")` into the row (`:964`), unvalidated. If the dataset's `quote_id` column is an
  integer, `_row_to_ctx` fails validation, the error row carries that integer, and the frame build
  meets a value that does not fit the schema. **Whether polars then raises, and whether its message
  includes the value, is not read but to be measured.** If it does, the text reaches `job.error`
  and the process log through the generic clause, and the input is a policy identifier from a client
  dataset.
- **The `PlatformError` detail clause** (`tasks.py:182`) stores `exc.detail or exc.title`. Three
  handlers put a library exception's text into a `PlatformError` detail:
  `model_handlers.py:398` (`str(exc)` of a fit error) and `:405` (`f"{exc} FR-87: …"`). Whether a
  modelling exception's text carries data values (training data, not a quote input) has not been
  read for each raise site. Every other `PlatformError` in `backend/src/app/worker` interpolates ids,
  slugs, counts or a dataset column name, from the grep of `raise PlatformError(` with an f-string.
- **The database.** Any `DBAPIError` in any handler prints `[parameters: …]` (the root cause
  above). The demonstration is a failing insert carrying a sentinel value through `execute_job`.

**Not yet demonstrated:** `score_batch` on a frame with an integer `quote_id` (the polars frame-build message), and the same
batch handler through `execute_job` end to end.

## Proposed fix

**One sanitiser, per the deputy's entry of 22:24:08 BST, plus one engine setting.**

1. **The sanitiser lives in `pricing-core`** (for example `pricing_core/errors.py`, or next to
   `_raise_named`), because pricing-core must stay importable standalone (`CLAUDE.md` §2) and
   cannot import from `app`. The worker imports it, so there is one rule and never two copies.
   `_batch_error_code` uses it: for a `ValidationError`, `errors(include_input=False,
   include_url=False)` rendered as field locations and messages, never `str(exc)`. The same
   sanitiser serves the generic Job path.
2. **`hide_parameters=True` on the engine** at `db/session.py:40`, which removes SQLAlchemy's
   parameter echo, **and** a reduction of any `DBAPIError` to its type, SQLSTATE and constraint,
   because the driver's own `DETAIL` and argument text echo values too (executor-s1's correction).
   Setting `hide_parameters` alone does not close entry point 3.
3. **Red-first tests:** (a) a batch with one row carrying a sentinel in a malformed field, asserting
   the sentinel is absent from the output parquet's `error_message`, from `error_samples`, from the
   `JobError` and from the logs, with a positive control that the field location is still present.
   (b) A failing statement (an FK or check violation, and a bad-typed argument) carrying a sentinel
   through `execute_job`, asserting the sentinel is absent from `str(exc)`, the stored `JobError` and
   the process log, including `DETAIL: Failing row contains (…)` and asyncpg's argument text.

Earlier form of the generic-path change, kept for the record: when the exception is a
`pydantic.ValidationError`, build the stored message and the logged text from
`exc.errors(include_input=False, include_url=False)` (location, type and message only), and log
with the sanitised exception in place of the original text. That covers every current and future
handler and removes the need for each handler to re-raise. A test that raises a `ValidationError`
carrying a sentinel input through `execute_job` and asserts the sentinel is absent from `job.error`
and every captured log record, driven through the worker path and not the handler function.

## Disposition

**Fix before close — fix in progress, owner the lead**, under WK-1178. Event: executor-s1's sanitiser
PR (the pricing-core sanitiser, `hide_parameters=True` with the `DBAPIError` reduction, and the
red-first sentinel tests). The
finding is ranked high by the deputy.
