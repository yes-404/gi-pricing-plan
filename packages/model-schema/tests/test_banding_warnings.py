"""FR-100 (SL-8031, red first): a thin-band warning is a typed record on the fit results.

`BandingWarning` and `BandingMeasure` are imported inside each test so that, on a tree
without them, each test fails at its own import rather than the file failing to collect.
"""

from __future__ import annotations

import json
from decimal import Decimal

import pytest
from pydantic import ValidationError

from model_schema.modelling import (
    EbmFitResult,
    GbmFitResult,
    GlmFitResult,
    OffsetSpec,
)
from model_schema.refs import BlobRef


def _gbm(**over: object) -> GbmFitResult:
    base: dict[str, object] = {
        "model_type": "xgboost",
        "booster_blob": BlobRef(sha256="a" * 64, bytes=2048, media_type="application/json"),
        "booster_format": "xgboost_json",
        "feature_order": ("a",),
        "feature_dtypes": {"a": "i32"},
        "monotone_constraints": (0,),
        "base_margin": OffsetSpec(kind="log_column", column="exposure_years"),
        "best_iteration": 1,
        "rows": 10,
        "fit_seconds": 1.0,
        "library_versions": {"xgboost": "3.4.1"},
    }
    base.update(over)
    return GbmFitResult(**base)  # type: ignore[arg-type]


def _exposure(**over: object) -> dict[str, object]:
    base: dict[str, object] = {
        "banding": "banding:age@1",
        "band_label": "17-29",
        "band_index": 0,
        "measure": "exposure",
        "observed": Decimal("1.5"),
        "minimum": Decimal("10"),
    }
    base.update(over)
    return base


def _claims(**over: object) -> dict[str, object]:
    base = _exposure(measure="claim_count", observed=3, minimum=10)
    base.update(over)
    return base


@pytest.mark.req("FR-100")
def test_the_three_fit_results_default_banding_warnings_to_empty() -> None:
    assert _gbm().banding_warnings == ()  # type: ignore[attr-defined]
    for model in (GlmFitResult, EbmFitResult):
        assert "banding_warnings" in model.model_fields


@pytest.mark.req("FR-100")
def test_a_stored_fit_result_without_the_key_still_validates() -> None:
    stored = json.loads(_gbm().model_dump_json())
    stored.pop("banding_warnings", None)
    assert GbmFitResult.model_validate(stored).banding_warnings == ()  # type: ignore[attr-defined]


@pytest.mark.req("FR-100")
def test_a_warning_round_trips_with_a_decimal_exposure_and_an_int_count() -> None:
    from model_schema.modelling import BandingMeasure, BandingWarning  # noqa: F401

    result = _gbm(banding_warnings=(_exposure(), _claims()))
    wire = json.loads(result.model_dump_json())["banding_warnings"]
    assert (wire[0]["observed"], wire[0]["minimum"]) == ("1.5", "10")
    assert (wire[1]["observed"], wire[1]["minimum"]) == (3, 10)
    again = GbmFitResult.model_validate_json(result.model_dump_json())
    assert again.banding_warnings[0].observed == Decimal("1.5")  # type: ignore[attr-defined]
    assert type(again.banding_warnings[1].observed) is int  # type: ignore[attr-defined]


@pytest.mark.req("FR-100")
@pytest.mark.parametrize(
    "bad",
    [
        _exposure(observed=1.5),  # float exposure
        _claims(observed=3.5),  # float count
        _claims(observed=Decimal("3")),  # Decimal count
        _exposure(measure="premium"),  # outside the enum
        _exposure(banding="dataset:age@1"),  # not a banding ref
        _exposure(band_index=-1),
    ],
)
def test_a_malformed_warning_is_refused(bad: dict[str, object]) -> None:
    from model_schema.modelling import BandingWarning  # noqa: F401

    with pytest.raises(ValidationError):
        _gbm(banding_warnings=(bad,))


@pytest.mark.req("FR-100")
def test_a_free_text_warning_is_refused() -> None:
    from model_schema.modelling import BandingWarning  # noqa: F401

    with pytest.raises(ValidationError):
        _gbm(banding_warnings=("band 17-29 is below the minimum",))
