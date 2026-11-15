"""When EVERY holdout (or backtest) row is on a level the fit has no relativity for, on a Factor
that does not declare `map_to_base`, the read is refused, coded, with the count and the next step
(FR-2143): never a zero-row partition. The text is built from a partition name and a count only.
"""

from __future__ import annotations

import polars as pl
import pytest
from test_glm_unseen_level_evidence import _book, _declared, _factor, _fitted

from pricing_core.modelling import backtest_model, compute_diagnostics
from pricing_core.modelling.predict import AllRowsUnseenError

ROWS = 30


def _all_unseen() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "area": ["d"] * ROWS, "exposure_years": [1.0] * ROWS, "claim_count": [0.0] * ROWS,
        }
    )


@pytest.mark.req("FR-2143")
def test_a_diagnostics_read_with_every_holdout_row_unseen_is_refused_with_the_count() -> None:
    factor = _factor()
    fit, spec = _fitted(factor)
    with pytest.raises(AllRowsUnseenError) as raised:
        compute_diagnostics(
            fit, spec, [factor], train=_book(), holdout=_all_unseen(), type_iii=False
        )
    assert raised.value.code == "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"
    assert f"every one of the {ROWS} holdout rows" in str(raised.value)
    assert "Declare “map to base” on that factor, or re-split the data." in str(raised.value)
    assert "'d'" not in str(raised.value)  # a count, never a level


@pytest.mark.req("FR-2143")
def test_a_backtest_with_every_row_unseen_is_refused_with_the_count() -> None:
    factor = _factor()
    fit, spec = _fitted(factor)
    with pytest.raises(AllRowsUnseenError) as raised:
        backtest_model(
            fit, spec, [factor], _all_unseen(),
            model_ref="model:freq@1", dataset_version_ref="dataset_version:later@2",
            fitted_on_ref="dataset_version:fitted@1",
        )
    assert raised.value.code == "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED"
    assert f"every one of the {ROWS} backtest rows" in str(raised.value)


@pytest.mark.req("FR-2143")
def test_a_declared_map_to_base_is_not_refused_and_scores_every_row() -> None:
    factor = _declared(_factor())
    fit, spec = _fitted(factor)
    result = compute_diagnostics(
        fit, spec, [factor], train=_book(), holdout=_all_unseen(), type_iii=False
    )
    assert result.universal.holdout.rows == ROWS
    assert result.universal.holdout.rows_excluded_unseen_level == 0
