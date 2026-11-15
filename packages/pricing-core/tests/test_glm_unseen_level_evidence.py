"""Evidence read on rows the fit has no relativity for (FR-2143).

A quote carrying such a level is refused. A diagnostics read, a comparison or a backtest must not
fail on it and must not score it as another level: the rows are excluded, counted with their
exposure, and a Factor declaring `map_to_base` scores them at the base level as a quote would.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Factor,
    FactorType,
    GlmSpec,
    OffsetSpec,
    PartitionDiagnostics,
    SplitRef,
    UnseenLevelBehaviour,
    new_uuid7,
)
from pricing_core.modelling import backtest_model, compute_diagnostics, fit_glm
from pricing_core.modelling.comparison import ComparisonCandidate, compare_models

TRUE = {"a": 1.0, "b": 2.0, "c": 3.0}
SPLIT = SplitRef(split_artifact_id=new_uuid7(), train_part="train", holdout_part="test")
UNSEEN_ROWS = 50


def _book(n: int = 3000, seed: int = 20261115) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    area = rng.choice(list(TRUE), size=n)
    exposure = rng.uniform(0.5, 1.5, size=n)
    lam = np.array([0.1 * TRUE[a] for a in area]) * exposure
    return pl.DataFrame(
        {
            "area": area, "exposure_years": exposure,
            "claim_count": rng.poisson(lam).astype(float),
        }
    )


def _holdout() -> pl.DataFrame:
    """Seen rows plus UNSEEN_ROWS rows on a level `d` the fit never saw, each of exposure 1.0."""
    extra = pl.DataFrame(
        {
            "area": ["d"] * UNSEEN_ROWS, "exposure_years": [1.0] * UNSEEN_ROWS,
            "claim_count": [0.0] * UNSEEN_ROWS,
        }
    )
    return pl.concat([_book(1000, seed=7), extra])


def _factor(**over: object) -> Factor:
    fields: dict[str, object] = {
        "id": uuid4(), "slug": "area", "dataset_id": uuid4(), "version": 1,
        "type": FactorType.IDENTITY, "source_columns": ("area",),
    }
    fields.update(over)
    return Factor(**fields)  # type: ignore[arg-type]


def _fitted(factor: Factor) -> tuple[object, GlmSpec]:
    spec = GlmSpec(
        model_family_slug="freq", dataset_version_id=uuid4(), response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=(factor.id,), family="poisson", split_ref=SPLIT,
    )
    return fit_glm(_book(), spec, [factor]).result, spec


def _declared(factor: Factor) -> Factor:
    return factor.model_copy(update={"unseen_level_behaviour": UnseenLevelBehaviour.MAP_TO_BASE})


def test_a_diagnostics_read_excludes_and_counts_holdout_rows_on_an_unseen_level() -> None:
    factor = _factor()
    fit, spec = _fitted(factor)
    result = compute_diagnostics(
        fit, spec, [factor], train=_book(), holdout=_holdout(), type_iii=False
    )
    holdout = result.universal.holdout
    assert holdout.rows == 1000  # the unseen rows are in no statistic
    assert holdout.rows_excluded_unseen_level == UNSEEN_ROWS
    assert holdout.exposure_excluded_unseen_level == Decimal(UNSEEN_ROWS)
    assert result.universal.train.rows_excluded_unseen_level == 0  # the rule ran, nothing excluded
    assert result.universal.train.exposure_excluded_unseen_level == Decimal(0)


def test_a_declared_map_to_base_scores_those_rows_as_a_quote_would() -> None:
    factor = _declared(_factor())
    fit, spec = _fitted(factor)
    result = compute_diagnostics(
        fit, spec, [factor], train=_book(), holdout=_holdout(), type_iii=False
    )
    holdout = result.universal.holdout
    assert holdout.rows == 1000 + UNSEEN_ROWS
    assert holdout.rows_excluded_unseen_level == 0


def test_a_backtest_excludes_and_counts_rows_on_an_unseen_level() -> None:
    factor = _factor()
    fit, spec = _fitted(factor)
    summary = backtest_model(
        fit, spec, [factor], _holdout(),
        model_ref="model:freq@1", dataset_version_ref="dataset_version:later@2",
        fitted_on_ref="dataset_version:fitted@1",
    )
    assert summary.partition.rows == 1000
    assert summary.partition.rows_excluded_unseen_level == UNSEEN_ROWS
    assert summary.partition.exposure_excluded_unseen_level == Decimal(UNSEEN_ROWS)


def test_a_comparison_excludes_one_shared_row_set_and_counts_it() -> None:
    first, second = _factor(), _factor(slug="area")
    fit_a, spec_a = _fitted(first)
    fit_b, spec_b = _fitted(second)
    candidates = [
        ComparisonCandidate(ref="model:a@1", fit=fit_a, spec=spec_a, factors=(first,)),
        ComparisonCandidate(ref="model:b@1", fit=fit_b, spec=spec_b, factors=(second,)),
    ]
    summary = compare_models(candidates, _holdout())
    assert summary.holdout_rows == 1000
    assert summary.rows_excluded_unseen_level == UNSEEN_ROWS
    assert summary.exposure_excluded_unseen_level == Decimal(UNSEEN_ROWS)


def test_a_comparison_with_every_row_unseen_is_refused_by_name() -> None:
    from pricing_core.modelling.errors import ModellingError

    first, second = _factor(), _factor()
    fit_a, spec_a = _fitted(first)
    fit_b, spec_b = _fitted(second)
    candidates = [
        ComparisonCandidate(ref="model:a@1", fit=fit_a, spec=spec_a, factors=(first,)),
        ComparisonCandidate(ref="model:b@1", fit=fit_b, spec=spec_b, factors=(second,)),
    ]
    only_unseen = _holdout().filter(pl.col("area") == "d")
    with pytest.raises(ModellingError) as raised:
        compare_models(candidates, only_unseen)
    assert raised.value.code == "MODELS_NOT_COMPARABLE"


def test_a_partition_stored_before_the_rule_reads_not_recorded_never_none() -> None:
    factor = _factor()
    fit, spec = _fitted(factor)
    partition = compute_diagnostics(
        fit, spec, [factor], train=_book(), holdout=_holdout(), type_iii=False
    ).universal.holdout
    stored = partition.model_dump(
        mode="json", exclude={"rows_excluded_unseen_level", "exposure_excluded_unseen_level"}
    )
    old = PartitionDiagnostics.model_validate(stored)
    assert old.rows_excluded_unseen_level is None  # "not recorded", not 0
    assert old.exposure_excluded_unseen_level is None
