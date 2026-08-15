"""The bridge between a long-running computation and the platform that scheduled it.

ADR-0001 forbids `pricing-core` from doing I/O — no logging to a database, no writing job
rows. But FR-PLAT-8 requires structured progress and FR-PLAT-9 requires cooperative
cancellation. Both are satisfied by an *injected callback* defined here and implemented by
the backend, so the dependency points inward and the core stays pure.

Defining the protocol here rather than in the backend is the whole point: `pricing-core`
owns the contract, the backend conforms to it, and the core never imports the backend.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["JobCancelled", "ProgressCallback", "ScaledProgress"]


class JobCancelled(Exception):
    """Raised by `check_cancelled` when the caller has requested cancellation.

    Cancellation is cooperative (FR-PLAT-9): the core checks at points where stopping
    leaves no half-written artifact, rather than being killed at an arbitrary instruction.
    """


@runtime_checkable
class ProgressCallback(Protocol):
    """What the backend supplies so the core can report progress without doing I/O."""

    def update(self, fraction: float, stage: str, **counters: int) -> None:
        """Report progress. `fraction` in [0, 1]; `stage` is human-readable."""
        ...

    def check_cancelled(self) -> None:
        """Raise `JobCancelled` if cancellation has been requested."""
        ...


class ScaledProgress:
    """A window onto a caller's range, so a nested computation can report its own `0..1`.

    Without it a handler that reports `0.35` before calling a core function which reports
    `0.05` leaves the bar going *backwards* — and a caller who avoids that by not reporting
    at all leaves it frozen, which is the failure FR-PLAT-8 exists to prevent. The core
    should not have to know it is a middle stage of something; this is how it does not.
    """

    def __init__(self, inner: ProgressCallback, *, start: float, end: float) -> None:
        if not 0.0 <= start <= end <= 1.0:
            raise ValueError(
                f"a progress window must satisfy 0 <= start <= end <= 1, got "
                f"[{start}, {end}]."
            )
        self._inner = inner
        self._start = start
        self._end = end

    def update(self, fraction: float, stage: str, **counters: int) -> None:
        bounded = min(max(fraction, 0.0), 1.0)
        self._inner.update(self._start + (self._end - self._start) * bounded, stage, **counters)

    def check_cancelled(self) -> None:
        self._inner.check_cancelled()


class NullProgress:
    """A no-op callback, so a core function is callable from a notebook or a test.

    ADR-0001's promise is that the maths runs outside the platform. That promise is only
    real if progress reporting is optional at the call site.
    """

    def update(self, fraction: float, stage: str, **counters: int) -> None:
        return None

    def check_cancelled(self) -> None:
        return None
