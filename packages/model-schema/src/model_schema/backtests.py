"""A model measured on a Dataset Version it was not fitted on (`02` FR-MODEL-57, §4.12).

The glossary defines a backtest as *evaluation of a Model on a Dataset Version other than
the one it was fitted on — typically a later period*, and FR-MODEL-57 asks for "the same
diagnostic shapes, marked with the version it ran against". Three shape decisions follow,
each made here because no §4 subsection defined this artifact before the slice that built
it.

* **A backtest is its own artifact, not a field on `Diagnostics`.** `Diagnostics.backtest`
  was declared from Phase 0 and typed `None`, and nothing could ever have populated it:
  FR-MODEL-49 makes diagnostics computed once at fit time and read thereafter, while a
  backtest runs later — and runs again for every subsequent period, which one field on one
  immutable artifact has no room for. That field is removed with this slice, for the reason
  `PartitionDiagnostics.double_lift` was removed before it: a field that is structurally
  always null reads as a measurement that came out empty.

* **One `PartitionDiagnostics`, not a `UniversalDiagnostics`.** FR-MODEL-54's "train and
  holdout, side by side" is a statement about a *fit*. A backtest population was never
  split, and calling its single partition a holdout would claim a split nobody made. The
  fit-time counterpart is not copied in either: it lives on the model's own diagnostics,
  which `model_id` reaches, and a second immutable copy of an immutable number buys nothing
  but a second thing to keep true.

* **The version it was fitted on is stored, not merely differed from.** `fitted_on_ref` is
  derivable — model → spec → `dataset_version_id` — and it is stored for the reason
  `ComparisonSummary` stores the `split_ref` it verified: the artifact's defining claim is
  *this is not the data it learned on*, and an approval that cites a backtest should be able
  to check that claim without re-deriving it. Storing both makes the claim an invariant this
  type enforces rather than a rule the platform is trusted to have applied.
"""

from __future__ import annotations

import datetime as _datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from model_schema.diagnostics import PartitionDiagnostics

__all__ = ["Backtest", "BacktestSummary"]


class BacktestSummary(BaseModel):
    """What a backtest found, before the platform gives it an identity.

    The `DiagnosticsResult` and `ComparisonSummary` split, for the same reason:
    `pricing-core` computes, and does not allocate ids, know about rows in a database, or
    read a clock (ADR-0001).

    The weighting scheme is inside `partition` and is not restated: it is a function of the
    model's spec (FR-MODEL-55), and a backtest scores its own model's spec, so it cannot
    differ from the fit-time scheme the reader will compare against.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: `model:{family}@{version}` — the model measured, pinned by version.
    model_ref: str
    #: `dataset_version:{slug}@{version}` — FR-MODEL-57's "marked with the version it ran
    #: against", in the reference form `00` ID-3 makes canonical.
    dataset_version_ref: str
    #: The version the model was fitted on. Stored so "other than" is checkable from the
    #: artifact alone, and enforced below.
    fitted_on_ref: str
    #: The period the backtested version covers, where it declares one. FR-MODEL-57 calls a
    #: backtest the evidence bridge into `05-monitoring.md`, and a deterioration nobody can
    #: date is not evidence of drift.
    period_from: _datetime.date | None = None
    period_to: _datetime.date | None = None
    partition: PartitionDiagnostics

    @model_validator(mode="after")
    def _a_backtest_is_not_run_on_the_data_it_learned_on(self) -> Self:
        if self.dataset_version_ref == self.fitted_on_ref:
            raise ValueError(
                f"{self.model_ref} was fitted on {self.fitted_on_ref} and this backtest "
                "names the same version. A model measured on its own training data reports "
                "how well it memorised, and the number renders identically to out-of-time "
                "performance."
            )
        return self

    @model_validator(mode="after")
    def _the_period_is_ordered(self) -> Self:
        if (
            self.period_from is not None
            and self.period_to is not None
            and self.period_from > self.period_to
        ):
            raise ValueError(
                f"backtest period {self.period_from} → {self.period_to} runs backwards."
            )
        return self


class Backtest(BaseModel):
    """The persisted artifact (`02` §4.12, FR-MODEL-57).

    Immutable, and enforced at the privilege layer as well as here (FR-DATA-42): a backtest
    is what a monitoring review and a re-approval argue from, and evidence that can change
    after the decision is not evidence.

    No slug and no version of its own, for the reason `Diagnostics` and `ModelComparison`
    have none — it is always reached by id, from the Job that produced it or the record that
    cites it. Unlike `Diagnostics` it is **not** one-per-model: a model backtested against
    four quarters has four, which is the point.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: UUID
    model_id: UUID
    dataset_version_id: UUID
    computed_at: _datetime.datetime
    job_id: UUID | None = None
    summary: BacktestSummary
