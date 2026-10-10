"""DislocationSpec and DislocationRun (03 §4.6, §5.2; WK-673 Slice 2, PL-1403)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, get_args

import pytest
from pydantic import ValidationError

from model_schema.dislocation import (
    DeltaKind,
    DislocationOutcomes,
    DislocationRun,
    DislocationSpec,
)

_CONTRACT = (
    Path(__file__).resolve().parents[3] / "docs/contracts/schemas/dislocation-run.schema.json"
)
_SLICE_3_FIELDS: set[str] = set()  # every contract property is emitted since Slice 3 (SL-1387)
_NULLABLE = {
    ("totals", "change_pct"),
    ("distribution", "exposure_share"),
    ("distribution", "mean_change_pct"),
    ("by_segment", "level"),
    ("by_segment", "mean_change_pct"),
    ("by_segment", "exposure_share"),
    ("by_ladder_rung", "contribution_pct"),
    ("attribution", "shapley_minor"),
    ("attribution", "mean_change_pct"),
    ("attribution", "cumulative_change_pct"),
    ("attribution_summary", "order_sensitivity_lower_bound"),
    ("attribution_summary", "residual_share"),
    ("attribution_summary", "orders_sampled"),
}


def _spec(**overrides: object) -> DislocationSpec:
    body: dict[str, object] = {
        "baseline_ref": "rating_version:motor-gb@26",
        "candidate_ref": "rating_version:motor-gb@27",
        "portfolio_dataset_version_id": "00000000-0000-0000-0000-000000000001",
        "purpose": "new_business",
        "as_at": "2026-10-01",
        "segments": ["driver_age_band"],
        "band_edges_pct": ["-10", "-5", "0", "5", "10"],
        "mover_threshold_pct": "10",
    }
    body.update(overrides)
    return DislocationSpec.model_validate(body)


def _run_body(**overrides: object) -> dict[str, Any]:
    body: dict[str, Any] = {
        "baseline_ref": "rating_version:motor-gb@26",
        "candidate_ref": "rating_version:motor-gb@27",
        "portfolio_dataset_version_id": "00000000-0000-0000-0000-000000000001",
        "policy_count": 5,
        "exposure_years": "1.000000",
        "totals": {"baseline_premium_minor": 1, "candidate_premium_minor": 1, "change_pct": None},
        "outcomes": {
            "quoted_both": 3,
            "quoted_to_declined": 1,
            "declined_to_quoted": 0,
            "declined_both": 0,
            "error": 1,
            "zero_baseline": 1,
            "negative_baseline": 0,
        },
        "distribution": [
            {"band": "< 0%", "policies": 2, "exposure_share": None, "mean_change_pct": None}
        ],
        "errors": [{"code": "E", "count": 1}],
    }
    body.update(overrides)
    return body


@pytest.mark.req("FR-263")
def test_spec_refuses_a_purpose_the_frame_cannot_stamp() -> None:
    with pytest.raises(ValidationError, match="purpose"):
        _spec(purpose="mid_term_adjustment")


@pytest.mark.req("FR-263")
def test_spec_refuses_band_edges_that_do_not_increase() -> None:
    with pytest.raises(ValidationError, match="band_edges_pct"):
        _spec(band_edges_pct=["0", "-5"])


@pytest.mark.req("FR-263")
def test_spec_refuses_a_float_threshold() -> None:
    with pytest.raises(ValidationError, match="float"):
        _spec(mover_threshold_pct=10.0)


@pytest.mark.req("FR-264")
def test_spec_refuses_a_repeated_segment() -> None:
    with pytest.raises(ValidationError, match="segments"):
        _spec(segments=["driver_age_band", "driver_age_band"])


@pytest.mark.req("FR-263")
def test_run_accepts_a_consistent_body() -> None:
    DislocationRun.model_validate(_run_body())


@pytest.mark.req("FR-263")
def test_outcomes_must_sum_to_policy_count() -> None:
    outcomes = DislocationOutcomes(
        quoted_both=3,
        quoted_to_declined=1,
        declined_to_quoted=0,
        declined_both=0,
        error=1,
        zero_baseline=0,
        negative_baseline=0,
    )
    with pytest.raises(ValidationError, match="policy_count"):
        DislocationRun.model_validate(_run_body(policy_count=6, outcomes=outcomes.model_dump()))


@pytest.mark.req("FR-263")
def test_distribution_excludes_zero_and_negative_baselines() -> None:
    """RL-1402 N2: Σ distribution.policies = quoted_both - zero_baseline - negative_baseline."""
    body = _run_body(
        outcomes={
            "quoted_both": 3,
            "quoted_to_declined": 1,
            "declined_to_quoted": 0,
            "declined_both": 0,
            "error": 1,
            "zero_baseline": 0,
            "negative_baseline": 1,
        }
    )
    DislocationRun.model_validate(body)  # 2 = 3 - 0 - 1
    body["distribution"][0]["policies"] = 3
    with pytest.raises(ValidationError, match="negative_baseline"):
        DislocationRun.model_validate(body)


@pytest.mark.req("FR-263")
def test_error_counts_must_sum_to_outcomes_error() -> None:
    with pytest.raises(ValidationError, match=r"outcomes\.error"):
        DislocationRun.model_validate(_run_body(errors=[{"code": "E", "count": 2}]))


@pytest.mark.req("FR-263")
def test_run_refuses_an_unknown_field() -> None:
    with pytest.raises(ValidationError, match="extra"):
        DislocationRun.model_validate(_run_body(unknown_field=[]))


def _resolve(node: dict[str, Any], defs: dict[str, Any]) -> dict[str, Any]:
    """Follow a `$ref`, or an `anyOf` of one `$ref` and null, to the object schema."""
    if "$ref" in node:
        return _resolve(defs[node["$ref"].rsplit("/", 1)[-1]], defs)
    for branch in node.get("anyOf", []):
        if branch.get("type") != "null":
            return _resolve(branch, defs)
    return node


def _array_items(node: dict[str, Any]) -> dict[str, Any]:
    """The `items` of an array schema, or of the array arm of an `anyOf` with null."""
    if "items" in node:
        return node["items"]  # type: ignore[no-any-return]
    return next(b["items"] for b in node["anyOf"] if b.get("type") == "array")  # type: ignore[no-any-return]


def _admits_null(node: dict[str, Any]) -> bool:
    return any(b.get("type") == "null" for b in node.get("anyOf", []))


@pytest.mark.req("FR-263")
def test_dislocation_run_fields_match_the_hand_authored_contract() -> None:
    contract = json.loads(_CONTRACT.read_text())
    emitted = DislocationRun.model_json_schema(by_alias=True)
    defs = emitted["$defs"]
    assert set(emitted["properties"]) <= set(contract["properties"])
    assert set(contract["properties"]) - set(emitted["properties"]) == _SLICE_3_FIELDS
    assert set(emitted.get("required", [])) == set(contract["required"])

    objects: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for key in ("totals", "outcomes"):
        objects[key] = (contract["properties"][key], _resolve(emitted["properties"][key], defs))
    for key in ("distribution", "by_segment", "by_ladder_rung", "errors"):
        objects[key] = (
            contract["properties"][key]["items"],
            _resolve(emitted["properties"][key]["items"], defs),
        )
    for key in ("attribution", "derived_changes", "change_groups"):
        objects[key] = (
            contract["properties"][key]["items"],
            _resolve(_array_items(emitted["properties"][key]), defs),
        )
    objects["attribution_summary"] = (
        contract["properties"]["attribution_summary"],
        _resolve(emitted["properties"]["attribution_summary"], defs),
    )
    err_c = contract["properties"]["errors"]["items"]["properties"]["sample"]["items"]
    err_e = _resolve(
        _resolve(emitted["properties"]["errors"]["items"], defs)["properties"]["sample"], defs
    )
    objects["errors.sample"] = (err_c, _resolve(err_e["items"], defs))

    for name, (c, e) in objects.items():
        assert set(e["properties"]) == set(c["properties"]), name
        assert set(e.get("required", [])) == set(c.get("required", [])), name
        for prop in e["properties"]:
            if (name, prop) in _NULLABLE:
                assert _admits_null(e["properties"][prop]), (name, prop)


def _contract_admits_null(node: dict[str, Any]) -> bool:
    t = node.get("type")
    return (isinstance(t, list) and "null" in t) or any(
        b.get("type") == "null" for b in node.get("anyOf", [])
    )


@pytest.mark.req("FR-1397")
def test_attribution_ratio_with_zero_denominator_validates_against_the_contract() -> None:
    """DP-S3-1 (a): the authored contract admits the null a zero-denominator ratio gives."""
    contract = json.loads(_CONTRACT.read_text())["properties"]
    items = contract["attribution"]["items"]["properties"]
    for prop in ("mean_change_pct", "cumulative_change_pct", "shapley_minor"):
        assert _contract_admits_null(items[prop]), prop


@pytest.mark.req("FR-1399")
def test_delta_kinds_equal_the_contract_enum() -> None:
    contract = json.loads(_CONTRACT.read_text())["properties"]
    enum = contract["derived_changes"]["items"]["properties"]["kind"]["enum"]
    assert sorted(get_args(DeltaKind)) == sorted(enum)


@pytest.mark.req("FR-1399")
def test_dislocation_run_attribution_is_all_or_none() -> None:
    """The schema's `dependentRequired` (`:9`): the four attribution fields come together."""
    with pytest.raises(ValidationError, match="attribution"):
        DislocationRun.model_validate(_run_body(derived_changes=[]))
