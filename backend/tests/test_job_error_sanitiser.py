"""A failed Job's error and logs never carry a quote input (NFR-499, RL-917, R3).

An unexpected exception's text used to be stored verbatim in `JobError.message` and its traceback
logged. A Pydantic `ValidationError`'s `str()` prints every failing `input_value`, which for a
quote is a quote input; a SQLAlchemy `DBAPIError` prints `[parameters: ...]`, and the database's
own message can echo the failing row. Each test plants a **sentinel** as the input and looks for
it in every place the failure is recorded: `JobError.message`, the persisted Job logs, and the
captured log records including their tracebacks. Each also has a control showing that what an
operator needs to act on, the field path and error type, is still there.

`JobLogCapture` stores only a record's formatted message (`worker/logs.py`), never its traceback,
so the persisted-log assertion held before this change; it is kept so it keeps holding.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from app.db.models import JobLogRow, JobRow, ScoringTraceRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs
from app.platform.safe_exception import safe_job_error_text, safe_job_exc_info
from app.worker import handlers
from app.worker.tasks import execute_job
from model_schema import JobKind, JobResult, JobStatus
from pricing_core.progress import ProgressCallback

_SENTINEL = "SENTINEL-quote-input-7f3a91c2"


class _Quote(BaseModel):
    driver_age: int


@pytest.fixture(autouse=True)
def _isolate_handlers():
    """Handlers are process-global; a leak between tests is a confusing failure."""
    original = dict(handlers.HANDLERS)
    handlers.HANDLERS.clear()
    yield
    handlers.HANDLERS.clear()
    handlers.HANDLERS.update(original)


async def _run(database: Database, workspace_id, principal, handler) -> JobRow:
    handlers.register_handler(JobKind.MODEL_FIT, handler)
    async with database.unit_of_work() as session:
        job = await jobs.submit(
            session, JobKind.MODEL_FIT, {}, principal, workspace_id=workspace_id
        )
    assert await execute_job(database, job.id) is JobStatus.FAILED
    async with database.session() as session:
        row = await session.get(JobRow, job.id)
        assert row is not None
        return row


async def _persisted_logs(database: Database, job_id) -> str:
    async with database.session() as session:
        rows = await session.execute(select(JobLogRow).where(JobLogRow.job_id == job_id))
        return "\n".join(row.message for row in rows.scalars())


def _validation_failure() -> None:
    _Quote.model_validate({"driver_age": _SENTINEL})


@pytest.mark.req("NFR-499")
async def test_a_validation_error_in_a_handler_leaves_no_input_in_the_job_error_or_logs(
    database: Database, workspace_id, principal, caplog: pytest.LogCaptureFixture
) -> None:
    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        _validation_failure()
        raise AssertionError("unreachable")

    with caplog.at_level(logging.INFO):
        row = await _run(database, workspace_id, principal, handler)

    assert row.error is not None
    assert _SENTINEL not in row.error["message"], row.error["message"]
    assert _SENTINEL not in await _persisted_logs(database, row.id)
    assert "job handler failed" in caplog.text, "the log capture saw nothing"
    assert _SENTINEL not in caplog.text, "the sentinel reached the logged traceback"
    # The control: an operator still sees which field failed, and why.
    assert row.error["code"] == "JOB_HANDLER_FAILED"
    assert "driver_age" in row.error["message"]
    assert "int_parsing" in row.error["message"]


@pytest.mark.req("NFR-499")
async def test_a_named_refusal_chained_from_a_validation_error_leaks_nothing_into_the_log(
    database: Database, workspace_id, principal, caplog: pytest.LogCaptureFixture
) -> None:
    """`raise PlatformError(...) from exc` prints the chained `ValidationError` in the
    traceback, so the named-refusal clause has the same hole as the generic one."""

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        try:
            _validation_failure()
        except ValueError as exc:
            raise PlatformError(
                "VALIDATION_FAILED", "The quote is invalid", 422, "The quote is invalid."
            ) from exc
        raise AssertionError("unreachable")

    with caplog.at_level(logging.INFO):
        row = await _run(database, workspace_id, principal, handler)

    assert row.error is not None
    assert row.error["code"] == "VALIDATION_FAILED"
    assert row.error["message"] == "The quote is invalid."
    assert "job handler failed" in caplog.text
    assert _SENTINEL not in caplog.text, "the chained ValidationError reached the log"
    assert _SENTINEL not in await _persisted_logs(database, row.id)


@pytest.mark.req("NFR-499")
def test_safe_job_error_text_keeps_the_field_path_and_error_type_and_drops_the_value() -> None:
    with pytest.raises(ValidationError) as caught:
        _validation_failure()
    exc = caught.value
    assert _SENTINEL in str(exc), "control: the raw text does carry the input"
    message = safe_job_error_text(exc)
    assert _SENTINEL not in message
    assert "driver_age" in message
    assert "int_parsing" in message
    rendered = logging.Formatter().formatException(safe_job_exc_info(exc))
    assert _SENTINEL not in rendered
    assert "_validation_failure" in rendered, "the operator's traceback frames are kept"


@pytest.mark.req("NFR-499")
async def test_a_database_error_does_not_print_its_bound_parameters(database: Database) -> None:
    """The engine is built with `hide_parameters=True`. Red before: SQLAlchemy appended
    `[parameters: ('SENTINEL-...',)]` to the exception text."""
    with pytest.raises(DBAPIError) as caught:
        async with database.session() as session:
            await session.execute(
                text("INSERT INTO no_such_table_nfr499 (v) VALUES (:v)"), {"v": _SENTINEL}
            )
    assert _SENTINEL not in str(caught.value)
    assert "no_such_table_nfr499" in str(caught.value), "control: the error is still readable"


@pytest.mark.req("NFR-499")
async def test_safe_job_error_text_drops_a_value_the_database_itself_echoes(
    database: Database, workspace_id
) -> None:
    """A check violation's `DETAIL: Failing row contains (...)` repeats the rejected value, and
    it is in the driver's message, which `hide_parameters` does not touch.
    `safe_job_error_text` keeps the driver exception's type, its SQLSTATE and the constraint,
    and nothing else."""
    with pytest.raises(DBAPIError) as caught:
        async with database.unit_of_work() as session:
            session.add(
                ScoringTraceRow(
                    workspace_id=workspace_id,
                    rating_version_ref="rating_version:motor-gb@1",
                    bundle_hash="sha256:" + "0" * 64,
                    sample_reason="rate",
                    blob_sha256=_SENTINEL,
                )
            )
    assert _SENTINEL in str(caught.value.orig), "control: the driver's own text echoes the value"
    message = safe_job_error_text(caught.value)
    assert _SENTINEL not in message
    assert "23514" in message, message
    assert "blob_sha256_format" in message, message


@pytest.mark.req("NFR-499")
async def test_a_unique_violations_detail_does_not_reach_the_message_or_the_log(
    database: Database, workspace_id, principal, caplog: pytest.LogCaptureFixture
) -> None:
    """Postgres reports `DETAIL: Key (workspace_id, idempotency_key)=(..., SENTINEL) already
    exists`, echoing the value in the driver's own message. Through a handler, so JobError and
    the logged traceback are both covered."""
    from app.db.models import JobRow as _JobRow
    from model_schema import JobQueue, JobSource

    def _insert() -> Any:
        return _JobRow(
            workspace_id=workspace_id,
            kind=JobKind.RATE_TABLE_DIFF,
            status=JobStatus.SUCCEEDED,
            queue=JobQueue.DEFAULT,
            source=JobSource.API,
            submitted_by={"kind": "user", "id": str(principal.id)},
            idempotency_key=_SENTINEL,
            finished_at=datetime.now(UTC),
        )

    async with database.unit_of_work() as session:
        session.add(_insert())

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        progress.run_on_loop(_second_insert())
        raise AssertionError("unreachable")

    async def _second_insert() -> None:
        async with database.unit_of_work() as session:
            session.add(_insert())

    with caplog.at_level(logging.INFO):
        row = await _run(database, workspace_id, principal, handler)

    assert row.error is not None
    assert _SENTINEL not in row.error["message"], row.error["message"]
    assert "23505" in row.error["message"], row.error["message"]
    assert "job handler failed" in caplog.text
    assert _SENTINEL not in caplog.text, "the driver's DETAIL reached the logged traceback"
    assert _SENTINEL not in await _persisted_logs(database, row.id)

    # The control: the driver's own text does echo the value, so the assertions above bite.
    with pytest.raises(DBAPIError) as caught:
        await _second_insert()
    assert _SENTINEL in str(caught.value.orig)


@pytest.mark.req("NFR-499")
async def test_an_unexpected_exception_is_stored_as_its_type_only_and_keeps_the_ids_in_the_log(
    database: Database, workspace_id, principal, caplog: pytest.LogCaptureFixture
) -> None:
    """The allow-list: an exception that is not ours is its type name and nothing else, however
    it is worded. The operator keeps the type, the Job id and the trace id (on the log record)
    and the frames of the traceback."""
    from app.observability.logging import JsonFormatter
    from app.observability.trace import bind_trace_id, reset_trace_id

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        raise RuntimeError(f"the quote {_SENTINEL} could not be priced")

    trace_id = "ab" * 16
    token = bind_trace_id(trace_id)
    try:
        with caplog.at_level(logging.INFO):
            row = await _run(database, workspace_id, principal, handler)
        record = next(r for r in caplog.records if r.getMessage() == "job handler failed")
        rendered = JsonFormatter().format(record)
    finally:
        reset_trace_id(token)

    assert row.error is not None
    assert row.error["message"] == "RuntimeError"
    assert _SENTINEL not in caplog.text
    assert _SENTINEL not in await _persisted_logs(database, row.id)
    assert record.job_id == str(row.id)  # type: ignore[attr-defined]
    assert f'"trace_id":"{trace_id}"' in rendered
    assert f'"job_id":"{row.id}"' in rendered
    assert "RuntimeError" in rendered
    assert "handler" in rendered, "the traceback frames are kept"
    assert _SENTINEL not in rendered


@pytest.mark.req("NFR-499")
async def test_a_dataframe_library_error_is_stored_as_its_type_only(
    database: Database, workspace_id, principal, caplog: pytest.LogCaptureFixture
) -> None:
    """A polars `ComputeError` repeats the value it could not append; the next library will do
    the same, which is why the rule is an allow-list rather than a list of known offenders."""
    import polars as pl

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        pl.DataFrame([{"q": {"secret": _SENTINEL}}, {"q": _SENTINEL}])
        raise AssertionError("unreachable")

    with caplog.at_level(logging.INFO):
        row = await _run(database, workspace_id, principal, handler)

    assert row.error is not None
    assert row.error["message"] == "ComputeError"
    assert _SENTINEL not in caplog.text
    assert _SENTINEL not in await _persisted_logs(database, row.id)


@pytest.mark.req("NFR-499")
async def test_a_third_party_error_wearing_our_code_prefix_is_stored_type_only(
    database: Database, workspace_id, principal, caplog: pytest.LogCaptureFixture
) -> None:
    """Recognition is by class. A library's `ValueError("INPUT_CONTRACT_VIOLATION: <value>")`
    carries OUR real code prefix and a sentinel; through the Job store it is `ValueError`
    and nothing else, in `JobError.message`, the persisted logs and the captured log."""

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        raise ValueError(f"INPUT_CONTRACT_VIOLATION: {_SENTINEL}")

    with caplog.at_level(logging.INFO):
        row = await _run(database, workspace_id, principal, handler)

    assert row.error is not None
    assert row.error["message"] == "ValueError"
    assert _SENTINEL not in caplog.text
    assert _SENTINEL not in await _persisted_logs(database, row.id)


@pytest.mark.req("NFR-499")
async def test_a_genuine_coded_error_is_stored_as_it_was_before_minus_its_value(
    database: Database, workspace_id, principal
) -> None:
    """The positive control, and the byte-identity check for the Job path. `CodedError` is only
    the allow-list's marker; the stored form is what `origin/main` stored for the same
    `ValueError`: `worker/tasks.py:229-230` builds `code="JOB_HANDLER_FAILED"` and
    `message=f"{type(exc).__name__}: {exc}"`, i.e. `ValueError: <CODE: text>`, with no class name
    of ours in it. The one difference is the value: `origin/main`'s text for this site was
    `input 'driver_age'=987654321 is above the declared maximum 99`."""
    from pricing_core.safe_error import CodedError

    text = "INPUT_CONTRACT_VIOLATION: input 'driver_age' is above the declared maximum 99"

    def handler(params: dict[str, Any], progress: ProgressCallback) -> JobResult:
        raise CodedError(text)

    row = await _run(database, workspace_id, principal, handler)

    assert row.error is not None
    assert row.error["code"] == "JOB_HANDLER_FAILED"
    assert row.error["message"] == f"ValueError: {text}"
    assert "CodedError" not in row.error["message"]

