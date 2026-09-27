"""The backtest artifact's invariants (`02` FR-187, §4.12).

No §4 subsection defined this artifact before the slice that built it, so every rule below
is a choice rather than a transcription, and each test is the record of one.

Two carry the meaning:

* **A backtest is not run on the data the model learned on.** `02` §2's glossary defines it
  that way, and the type refuses the parent case outright: a model measured on its own
  training rows reports how well it memorised, and that number renders identically to
  out-of-time performance. The platform refuses the split parts too — it is the only layer
  that knows them — and `backend/tests/test_backtests.py` is where that is proven.

* **One partition, and it is not called a holdout.** FR-183 makes a one-sided *fit*
  diagnostic a defect; a backtest population was never split, so there is no counterpart
  being withheld. `Diagnostics` accordingly no longer carries a `backtest` field, and the
  last test here is the one that would fail if it came back.
"""

from __future__ import annotations

import datetime as _datetime

import pydantic
import pytest

from model_schema import (
    Backtest,
    BacktestSummary,
    Diagnostics,
    PartitionDiagnostics,
    Weighting,
    new_uuid7,
)

MODEL = "model:motor-ad-frequency@7"
LATER = "dataset_version:motor-2025h2@4"
FITTED_ON = "dataset_version:motor-2024@1"


def _partition(rows: int = 40_000) -> PartitionDiagnostics:
    return PartitionDiagnostics(
        weighting=Weighting.EXPOSURE,
        rows=rows,
        ae_overall=1.07,
        gini=0.31,
        gini_normalised=0.62,
    )


def _summary(**overrides: object) -> BacktestSummary:
    fields: dict[str, object] = {
        "model_ref": MODEL,
        "dataset_version_ref": LATER,
        "fitted_on_ref": FITTED_ON,
        "period_from": _datetime.date(2025, 7, 1),
        "period_to": _datetime.date(2025, 12, 31),
        "partition": _partition(),
    }
    fields.update(overrides)
    return BacktestSummary.model_validate(fields)


@pytest.mark.req("FR-187")
def test_a_well_formed_backtest_round_trips() -> None:
    summary = _summary()
    assert BacktestSummary.model_validate(summary.model_dump(mode="json")) == summary


@pytest.mark.req("FR-187")
def test_a_backtest_refuses_the_version_it_was_fitted_on() -> None:
    """`02` §2's definition, made unrepresentable rather than merely documented."""
    with pytest.raises(pydantic.ValidationError, match="fitted on"):
        _summary(dataset_version_ref=FITTED_ON)


@pytest.mark.req("FR-187")
def test_a_backtest_period_runs_forwards() -> None:
    with pytest.raises(pydantic.ValidationError, match="backwards"):
        _summary(
            period_from=_datetime.date(2025, 12, 31),
            period_to=_datetime.date(2025, 7, 1),
        )


@pytest.mark.req("FR-187")
def test_a_backtest_may_declare_no_period() -> None:
    """A version that records no period is common and is not an error.

    Refusing one would make the artifact unbuildable for exactly the datasets a first
    backtest is run on — and FR-187 asks for the version it ran against, which is
    always known, rather than the dates, which are not.
    """
    summary = _summary(period_from=None, period_to=None)
    assert summary.period_from is None


@pytest.mark.req("FR-187")
def test_the_persisted_artifact_round_trips() -> None:
    backtest = Backtest(
        id=new_uuid7(),
        model_id=new_uuid7(),
        dataset_version_id=new_uuid7(),
        computed_at=_datetime.datetime(2026, 8, 18, 12, tzinfo=_datetime.UTC),
        job_id=new_uuid7(),
        summary=_summary(),
    )
    assert Backtest.model_validate(backtest.model_dump(mode="json")) == backtest


@pytest.mark.req("FR-187")
def test_diagnostics_no_longer_carries_a_backtest_field() -> None:
    """The field was declared from Phase 0 and typed `None`, and nothing could fill it.

    FR-170 computes diagnostics once at fit time; a backtest runs later, and again for
    every period after that. `extra="forbid"` makes this test the thing that fails if the
    field is reintroduced — the same guard the `double_lift` removal left behind.
    """
    assert "backtest" not in Diagnostics.model_fields
    assert "cross_validation" in Diagnostics.model_fields, (
        "FR-182's cross-validation is computed at fit time and does belong here; "
        "removing it with the backtest would be the opposite error."
    )
