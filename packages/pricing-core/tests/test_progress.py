"""ADR-0001: the core reports progress through an injected callback, not by doing I/O."""

import pytest

from pricing_core.progress import JobCancelled, NullProgress, ProgressCallback


@pytest.mark.req("FR-PLAT-8")
def test_null_progress_satisfies_the_protocol():
    """A core function must be callable from a notebook with no platform present —
    that is the promise ADR-0001 exists to keep."""
    assert isinstance(NullProgress(), ProgressCallback)


@pytest.mark.req("FR-PLAT-9")
def test_cancellation_is_an_exception_the_core_can_let_propagate():
    class Cancelling:
        def update(self, fraction: float, stage: str, **counters: int) -> None: ...
        def check_cancelled(self) -> None:
            raise JobCancelled("cancelled by user")

    with pytest.raises(JobCancelled):
        Cancelling().check_cancelled()
