"""FR-412's memory half, armed on the worker (FR-415; WK-674 Slice 4).

`resource_budget.memory_gb` was accepted by the shape and read by nothing: a budget that is
configured and never read is worse than none (FR-415). These tests need no database:
`JobProgress` reads its budgets from its constructor, and the budget check is the unit.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Iterator
from typing import Any

import pytest

from app.worker import progress as progress_module
from app.worker.progress import JobBudgetExceededError, JobProgress
from model_schema import new_uuid7

GIB = 1024**3


@pytest.fixture
def cancellation_loop(monkeypatch: pytest.MonkeyPatch) -> Iterator[asyncio.AbstractEventLoop]:
    """A running loop and a cancellation reader that reports "not requested".

    `check_cancelled()` goes on from the budget check to the cancellation poll, which
    schedules `_read_cancellation()` on the loop and waits for it. A loop that never runs
    would block that wait; the reader is stubbed so no database is needed, and the tests
    still drive `check_cancelled()` end to end.
    """

    async def not_requested(self: JobProgress) -> bool:
        return False

    monkeypatch.setattr(JobProgress, "_read_cancellation", not_requested)
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    try:
        yield loop
    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=5)
        loop.close()


def _progress(loop: asyncio.AbstractEventLoop | None = None, **budget: Any) -> JobProgress:
    # `database` is never touched by the budget check; the loop is only stored.
    return JobProgress(
        new_uuid7(),
        None,  # type: ignore[arg-type]
        loop or asyncio.new_event_loop(),
        **budget,
    )


@pytest.mark.req("FR-412")
def test_a_job_over_its_memory_budget_is_terminated_naming_the_budget(monkeypatch) -> None:
    """The oversized Job: resident memory 3 GiB against a 2 GiB budget."""
    monkeypatch.setattr(progress_module, "_resident_bytes", lambda: 3 * GIB)

    with pytest.raises(JobBudgetExceededError) as raised:
        _progress(memory_gb=2.0).check_cancelled()

    err = raised.value
    assert err.budget == "memory_gb"
    assert "memory budget of 2" in str(err)
    assert err.detail() == {"memory_gb": 2.0, "observed_gb": 3.0}


@pytest.mark.req("FR-412")
def test_a_job_within_its_memory_budget_is_not_stopped(
    monkeypatch, cancellation_loop: asyncio.AbstractEventLoop
) -> None:
    monkeypatch.setattr(progress_module, "_resident_bytes", lambda: 1 * GIB)
    _progress(cancellation_loop, memory_gb=2.0).check_cancelled()


@pytest.mark.req("FR-412")
def test_no_memory_budget_reads_no_memory(
    monkeypatch, cancellation_loop: asyncio.AbstractEventLoop
) -> None:
    """A Job without a memory budget must not pay for a /proc read at every checkpoint."""

    def boom() -> int:
        raise AssertionError("resident memory read with no memory budget")

    monkeypatch.setattr(progress_module, "_resident_bytes", boom)
    _progress(cancellation_loop).check_cancelled()


@pytest.mark.req("FR-412")
def test_the_resident_read_is_this_process_resident_set() -> None:
    """The real reader returns a plausible positive size, not a stub's number."""
    assert progress_module._resident_bytes() > 10 * 1024 * 1024
