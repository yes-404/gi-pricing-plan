"""ADR-0001: the core reports progress through an injected callback, not by doing I/O."""

import pytest

from pricing_core.progress import (
    JobCancelled,
    NullProgress,
    ProgressCallback,
    ScaledProgress,
)


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


@pytest.mark.req("FR-PLAT-8")
def test_a_scaled_window_keeps_a_nested_computation_inside_its_share():
    """A core function reports `0..1`; the handler decides where that lands on the bar.

    Without this, a handler that reported 0.35 before calling `fit_glm` — which reports its
    own 0.05 — sent the bar *backwards*, and a handler that avoided that by reporting
    nothing left it frozen for the whole fit. Both were real: the fit sat at 0.35 for its
    entire duration, which is the state FR-PLAT-8 exists to prevent.
    """
    seen: list[tuple[float, str]] = []

    class Recording:
        def update(self, fraction: float, stage: str, **counters: int) -> None:
            seen.append((fraction, stage))

        def check_cancelled(self) -> None: ...

    window = ScaledProgress(Recording(), start=0.10, end=0.85)
    window.update(0.0, "start")
    window.update(0.5, "half")
    window.update(1.0, "end")

    assert seen == [(0.10, "start"), (0.475, "half"), (0.85, "end")]
    assert [f for f, _ in seen] == sorted(f for f, _ in seen), "never backwards"


@pytest.mark.req("FR-PLAT-8")
def test_a_scaled_window_clamps_a_fraction_outside_zero_to_one():
    """A core function that miscounts its stages must not push the bar past the window."""
    seen: list[float] = []

    class Recording:
        def update(self, fraction: float, stage: str, **counters: int) -> None:
            seen.append(fraction)

        def check_cancelled(self) -> None: ...

    window = ScaledProgress(Recording(), start=0.2, end=0.6)
    window.update(-1.0, "under")
    window.update(9.0, "over")
    assert seen == [0.2, 0.6]


@pytest.mark.req("FR-PLAT-8")
def test_an_inverted_window_is_refused():
    with pytest.raises(ValueError, match="0 <= start <= end <= 1"):
        ScaledProgress(NullProgress(), start=0.9, end=0.1)


@pytest.mark.req("FR-PLAT-9")
def test_a_scaled_window_passes_cancellation_straight_through():
    """Cancellation is not a fraction, so scaling has nothing to do with it."""

    class Cancelling:
        def update(self, fraction: float, stage: str, **counters: int) -> None: ...
        def check_cancelled(self) -> None:
            raise JobCancelled("cancelled by user")

    with pytest.raises(JobCancelled):
        ScaledProgress(Cancelling(), start=0.0, end=1.0).check_cancelled()
