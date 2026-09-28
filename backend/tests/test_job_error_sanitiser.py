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
from typing import Any

import pytest
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from app.db.models import JobLogRow, JobRow, ScoringTraceRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs
from app.platform.safe_exception import safe_exc_info, safe_message
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
def test_safe_message_keeps_the_field_path_and_error_type_and_drops_the_value() -> None:
    with pytest.raises(ValueError) as caught:
        _validation_failure()
    exc = caught.value
    assert _SENTINEL in str(exc), "control: the raw text does carry the input"
    message = safe_message(exc)
    assert _SENTINEL not in message
    assert "driver_age" in message
    assert "int_parsing" in message
    rendered = logging.Formatter().formatException(safe_exc_info(exc))
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
async def test_safe_message_drops_a_value_the_database_itself_echoes(
    database: Database, workspace_id
) -> None:
    """A check violation's `DETAIL: Failing row contains (...)` repeats the rejected value, and
    it is in the driver's message, which `hide_parameters` does not touch. `safe_message` keeps
    the driver exception's type, its SQLSTATE and the constraint, and nothing else."""
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
    message = safe_message(caught.value)
    assert _SENTINEL not in message
    assert "23514" in message, message
    assert "blob_sha256_format" in message, message
