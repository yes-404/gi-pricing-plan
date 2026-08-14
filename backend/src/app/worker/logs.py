"""Capturing a Job's log lines so they can be read with the Job (FR-PLAT-10).

A `logging.Handler` attached for the duration of one Job, buffering records and flushing
them to `job_logs`. Buffered rather than written per line: a fitting loop can emit
thousands of lines, and a synchronous insert per line would make logging the slowest part
of the job.

**Only the formatted message is stored** (R3, FR-GOV-26). A `LogRecord` carries arbitrary
attributes, and sweeping those into the database is how a credential someone attached to a
log call ends up in a table the UI renders. What is not captured cannot leak.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Final
from uuid import UUID

from app.db.models import JobLogRow
from app.db.session import Database
from app.observability.trace import current_trace_id

__all__ = ["JobLogCapture"]

#: A runaway handler must not exhaust the worker's memory. The oldest lines are dropped
#: first because the tail is what explains a failure.
MAX_BUFFERED: Final = 5_000

TRUNCATION_NOTICE: Final = (
    "[log truncated: earlier lines dropped after %d buffered records]"
)


class JobLogCapture(logging.Handler):
    """Buffers records for one Job; `flush_to_database` persists them."""

    def __init__(self, job_id: UUID, database: Database, level: int = logging.INFO) -> None:
        super().__init__(level)
        self._job_id = job_id
        self._database = database
        self._buffer: deque[tuple[str, str, str, str | None]] = deque(maxlen=MAX_BUFFERED)
        self._dropped = 0

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = record.getMessage()
        except Exception:  # a broken format string must not fail the job
            message = f"<unformattable log record from {record.name}>"
        if len(self._buffer) == MAX_BUFFERED:
            self._dropped += 1
        self._buffer.append(
            (record.levelname, record.name, message[:8000], current_trace_id())
        )

    async def flush_to_database(self) -> int:
        """Write buffered lines and clear the buffer. Returns how many were written."""
        if not self._buffer:
            return 0

        rows = [
            JobLogRow(
                job_id=self._job_id,
                level=level,
                logger=logger,
                message=message,
                trace_id=trace_id,
            )
            for level, logger, message, trace_id in self._buffer
        ]
        if self._dropped:
            rows.insert(
                0,
                JobLogRow(
                    job_id=self._job_id,
                    level="WARNING",
                    logger="app.worker.logs",
                    message=TRUNCATION_NOTICE % MAX_BUFFERED,
                    trace_id=current_trace_id(),
                ),
            )
        self._buffer.clear()
        self._dropped = 0

        async with self._database.unit_of_work() as session:
            session.add_all(rows)
        return len(rows)
