"""The unseen-level sweep (`scripts/sweep-unseen-levels.py`, FR-2143), on a planted reachable
version and a clean one.

The sweep is READ-ONLY and prints version references and counts only. Its core, `sweep(versions,
out)`, takes the version dicts the stored-bundle sweep reads (`{slug, version, status, bundle_hash,
bundle}`), so no database is needed here. The fixtures are the committed stored bundles
(`fixtures/stored_bundles`): the clean one is a GLM over a FULL grid of two IDENTITY operands
(region x yoa), so no pairing of seen levels is missing. The planted ones are that bundle with one
cell's relativity removed (a pairing the fit saw separately and never together), and with an
undeclared IDENTITY factor given fitted relativities.
"""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import pathlib
from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "stored_bundles"

_spec = importlib.util.spec_from_file_location(
    "sweep_unseen_levels", ROOT / "scripts" / "sweep-unseen-levels.py"
)
assert _spec is not None
assert _spec.loader is not None
sweep_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sweep_module)

_MODEL = "model:motor-freq-glm@1"
_CROSS = "factor:region_x_yoa@1"
_HASH = "sha256:" + "d" * 64


def _clean() -> dict[str, Any]:
    bundle: dict[str, Any] = json.loads((FIXTURES / "clean.bundle.json").read_text())
    return bundle


def _row(bundle: dict[str, Any] | None, slug: str = "glm", version: int = 1) -> dict[str, Any]:
    return {
        "slug": slug, "version": version, "status": "approved",
        "bundle_hash": None if bundle is None else _HASH, "bundle": bundle,
    }


def _run(versions: list[dict[str, Any]]) -> tuple[int, list[str]]:
    out = io.StringIO()
    rc = sweep_module.sweep(versions, out)
    return rc, out.getvalue().splitlines()


def _without_a_cell() -> dict[str, Any]:
    """The clean bundle with one cell of the cross removed from the fit's relativities."""
    bundle = copy.deepcopy(_clean())
    cells = bundle["resolved_payloads"][_MODEL]["fit_result"]["relativities"]["region_x_yoa"]
    assert len(cells) == 4  # a full 2 x 2 grid, so removing one leaves a pairing never fitted
    bundle["resolved_payloads"][_MODEL]["fit_result"]["relativities"]["region_x_yoa"] = [
        c for c in cells if c["level"] != "A | 2011"
    ]
    return bundle


def _input(bundle: dict[str, Any], name: str) -> dict[str, Any]:
    contract: dict[str, Any] = next(
        c for c in bundle["graph"]["input_contract"] if c["name"] == name
    )
    return contract


@pytest.mark.req("FR-2143")
def test_a_clean_version_exits_zero_and_the_denominators_print_first() -> None:
    rc, lines = _run([_row(_clean())])

    assert rc == 0
    assert lines[:5] == [
        "versions: 1", "with a bundle: 1", "checked: 1", "unreadable: 0", "glm refs read: 1",
    ]
    findings = ("PLAIN ", "INTERACTION", "NULLLEVEL ", "GROUPING ")
    assert not any(line.startswith(findings) for line in lines)


@pytest.mark.req("FR-2143")
def test_a_reachable_version_is_listed_by_reference_and_exits_one() -> None:
    rc, lines = _run([_row(_without_a_cell(), "planted", 3), _row(_clean(), "clean", 2)])

    assert rc == 1
    assert "INTERACTION-LOWERBOUND planted@3 status=approved" in lines
    assert not any("clean@2" in line for line in lines)
    assert any(line.startswith("interaction-unfitted-lower-bound: 1 (a floor") for line in lines)
    # references and counts only: no level value, no hash
    text = "\n".join(lines)
    assert "2011" not in text
    assert "2010" not in text
    assert _HASH not in text


@pytest.mark.req("FR-2143")
def test_an_undeclared_identity_factor_with_relativities_is_listed_as_plain() -> None:
    bundle = copy.deepcopy(_clean())
    fit = bundle["resolved_payloads"][_MODEL]["fit_result"]
    fit["relativities"]["region"] = [
        {"level": "A", "is_base": True}, {"level": "B", "is_base": False},
    ]
    # the input is open: it admits a level the fit has no relativity for
    _input(bundle, "region")["domain"] = ["A", "B", "C"]
    rc, lines = _run([_row(bundle, "plain", 1)])

    assert rc == 1
    assert "PLAIN plain@1 status=approved" in lines
    assert any(line.startswith("NOTEXAMINED-CONTRACT 1 (") for line in lines)


@pytest.mark.req("FR-2143")
def test_a_declared_map_to_base_is_not_a_finding() -> None:
    bundle = _without_a_cell()
    bundle["resolved_payloads"][_CROSS]["unseen_level_behaviour"] = "map_to_base"
    rc, lines = _run([_row(bundle)])

    assert rc == 0
    assert not any(line.startswith("INTERACTION") for line in lines)


@pytest.mark.req("FR-2143")
def test_an_unreadable_bundle_exits_two_and_wins_over_a_reachable_one() -> None:
    rc, lines = _run(
        [_row({"not": "a bundle"}, "broken", 1), _row(_without_a_cell(), "planted", 3)]
    )

    assert rc == 2
    assert "UNREADABLE broken@1 status=approved (bundle-unparseable)" in lines
    assert "checked: 1" in lines  # M minus unreadable


@pytest.mark.req("FR-2143")
def test_a_numeric_looking_label_on_an_identity_factor_is_counted_as_not_examined() -> None:
    bundle = copy.deepcopy(_clean())
    fit = bundle["resolved_payloads"][_MODEL]["fit_result"]
    fit["coefficients"].append(
        {"term": "yoa[9z]", "estimate": 0.3, "std_error": 0.1, "z": 3.0, "p_value": 0.01,
         "ci_95": [0.1, 0.5]}
    )
    _, lines = _run([_row(bundle, "numeric", 1), _row(_clean(), "clean", 2)])

    # (the planted term has no relativities entry, so this version is also NORELATIVITIES: the
    # not-examined class is listed beside it, never instead of it and never omitted)
    assert "NOTEXAMINED-NUMERIC-TERMS numeric@1 status=approved" in lines
    assert not any("clean@2" in line for line in lines)
    assert any(line.startswith("NOTEXAMINED-NUMERIC-TERMS 1 (versions with") for line in lines)
    assert "9z" not in "\n".join(lines)  # references and counts only: never the label


@pytest.mark.req("FR-2143")
@pytest.mark.parametrize(
    "label", ["3", "3.0", "007", "1.50", "-.5", "+.5", "nan", "inf", "-inf", " 1 ", "3+", "25-39"]
)
def test_every_identity_label_that_parses_as_a_number_is_counted_as_not_examined(
    label: str,
) -> None:
    """A label that parses as a number is listed as well: whether a numeric input can produce it
    depends on the input's type (`3` from an int, `3.0` from a float), which the sweep does not
    classify. The count is a floor on what was examined, never the label itself, never an exit."""
    bundle = copy.deepcopy(_clean())
    bundle["resolved_payloads"][_MODEL]["fit_result"]["coefficients"].append(
        {"term": f"yoa[{label}]", "estimate": 0.3, "std_error": 0.1, "z": 3.0, "p_value": 0.01,
         "ci_95": [0.1, 0.5]}
    )
    rc, lines = _run([_row(bundle, "numeric", 1), _row(_clean(), "clean", 2)])

    assert "NOTEXAMINED-NUMERIC-TERMS numeric@1 status=approved" in lines
    assert not any("clean@2" in line for line in lines)
    assert any(line.startswith("NOTEXAMINED-NUMERIC-TERMS 1 (versions with") for line in lines)
    assert any("a FLOOR on what the sweep examined, not a count of faults" in ln for ln in lines)
    assert f"[{label}]" not in "\n".join(lines)  # references and counts only: never the label
    # the NOTEXAMINED line never decides the exit code: this version is reachable only through
    # the classes the planted term also triggers (no relativities entry), never through it
    assert rc == 1
    only_not_examined = [ln for ln in lines if ln.startswith("NOTEXAMINED-NUMERIC-TERMS numeric")]
    assert only_not_examined == ["NOTEXAMINED-NUMERIC-TERMS numeric@1 status=approved"]


@pytest.mark.req("FR-2143")
def test_an_internal_failure_exits_seventy_with_the_type_only(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An uncaught exception would exit 1, the code for "a version is reachable". It exits 70, and
    prints the exception's TYPE only: its text may carry a value."""

    def planted(*args: object, **kwargs: object) -> list[dict[str, Any]]:
        raise RuntimeError("SENTINEL-sweep-9d1e")

    monkeypatch.setattr(sweep_module, "_read_versions", planted)

    assert sweep_module._main(["--dsn", "unused"]) == 70
    captured = capsys.readouterr()
    assert captured.err.strip() == "internal error: RuntimeError"
    assert "SENTINEL-sweep-9d1e" not in captured.out + captured.err


@pytest.mark.req("FR-2143")
def test_a_usage_error_exits_sixty_four_not_argparses_two() -> None:
    assert sweep_module._main(["--no-such-option"]) == 64


def _with_a_gbm(bundle: dict[str, Any]) -> dict[str, Any]:
    """`bundle` also pinning a GBM, stored as a compile stores it: the `Model` dump's `fit_result`
    plus `booster_content`, the booster's own text carried inside the payload."""
    from model_schema import GbmFitResult

    fit_result: dict[str, Any] = {
        "model_type": "xgboost",
        "booster_blob": {"sha256": "a" * 64, "bytes": 2, "media_type": "application/json"},
        "booster_format": "xgboost_json",
        "feature_order": ["age_years"],
        "feature_dtypes": {},
        "categorical_maps": {},
        "monotone_constraints": [],
        "base_margin": {"kind": "none"},
        "best_iteration": 3,
        "inverse_link": None,
        "rows": 5,
        "fit_seconds": 0.01,
        "library_versions": {},
        "dropped_eval_metrics": [],
    }
    GbmFitResult.model_validate(fit_result)  # the stored shape is model-schema's own
    with_gbm = copy.deepcopy(bundle)
    with_gbm["resolved_payloads"]["model:gbm-challenger@1"] = {
        "fit_result": {**fit_result, "booster_content": "{}"}
    }
    return with_gbm


@pytest.mark.req("FR-2143")
def test_a_bundle_that_also_pins_a_gbm_is_examined_on_its_glm_not_unreadable() -> None:
    """A GBM payload carries a bundle-only field (`booster_content`) that its fit-result schema
    forbids. A version pinning one is examined on its GLM; the GBM is not validated as a GLM."""
    rc, lines = _run([_row(_with_a_gbm(_clean()), "wf699", 1), _row(_clean(), "clean", 2)])

    assert not any(line.startswith("UNREADABLE") for line in lines)
    assert "checked: 2" in lines
    assert "unreadable: 0" in lines
    assert "glm refs read: 2" in lines
    assert rc != 2


@pytest.mark.req("FR-2143")
def test_a_version_pinning_another_family_is_counted_with_the_family_named() -> None:
    rc, lines = _run([_row(_with_a_gbm(_clean()), "wf699", 1), _row(_clean(), "clean", 2)])

    other = [ln for ln in lines if ln.startswith("not-examined-other-family:")]
    assert len(other) == 1
    assert other[0].startswith("not-examined-other-family: 1 (families: xgboost;")
    assert not any("wf699@1" in ln and not ln.startswith("not-examined") for ln in lines)
    assert rc == 0  # a non-GLM model is never a finding


@pytest.mark.req("FR-2143")
@pytest.mark.parametrize(
    ("reason", "plant"),
    [
        ("no-model-type", lambda fit: fit.pop("model_type")),
        ("unknown-model-type", lambda fit: fit.update(model_type="SENTINEL-family-3b7c")),
    ],
)
def test_a_model_payload_with_no_or_an_unknown_model_type_is_unreadable_by_reason(
    reason: str, plant: Any
) -> None:
    bundle = copy.deepcopy(_clean())
    plant(bundle["resolved_payloads"][_MODEL]["fit_result"])

    rc, lines = _run([_row(bundle, "glm", 1)])

    assert f"UNREADABLE glm@1 status=approved ({reason})" in lines
    assert rc == 2
    assert "SENTINEL-family-3b7c" not in "\n".join(lines)  # a reason word, never a value


@pytest.mark.req("FR-2143")
def test_a_model_payload_with_no_fit_result_is_unreadable_by_reason() -> None:
    """A pinned model with no `fit_result` cannot be classified: its version is UNREADABLE, never
    read as having no GLM."""
    bundle = copy.deepcopy(_clean())
    bundle["resolved_payloads"][_MODEL].pop("fit_result")

    rc, lines = _run([_row(bundle, "nofit", 1)])

    assert "UNREADABLE nofit@1 status=approved (no-fit-result)" in lines
    assert "checked: 0" in lines
    assert rc == 2


@pytest.mark.req("FR-2143")
def test_a_glm_payload_that_does_not_validate_is_unreadable_by_its_exception_type_only() -> None:
    bundle = copy.deepcopy(_clean())
    bundle["resolved_payloads"][_MODEL]["fit_result"]["coefficients"][0]["estimate"] = (
        "SENTINEL-sweep-4f2a"
    )

    rc, lines = _run([_row(bundle, "glm", 1)])

    assert "UNREADABLE glm@1 status=approved (ValidationError)" in lines
    assert rc == 2
    assert "SENTINEL-sweep-4f2a" not in "\n".join(lines)  # the type, never the exception's text


@pytest.mark.req("FR-2143")
def test_an_empty_corpus_exits_three_never_zero() -> None:
    rc_none, lines_none = _run([])
    rc_uncompiled, _ = _run([_row(None, "draft", 1)])

    assert rc_none == rc_uncompiled == 3
    assert lines_none[:3] == ["versions: 0", "with a bundle: 0", "checked: 0"]


# --- FR-2143: an undeclared identity Factor no quote can bring an unseen level to -------------

_SECOND = "model:motor-sev-glm@1"


def _region_fitted(bundle: dict[str, Any], model: str, levels: list[str]) -> None:
    fit = bundle["resolved_payloads"][model]["fit_result"]
    fit["relativities"]["region"] = [
        {"level": level, "is_base": i == 0, "relativity": 1.0, "estimate": 0.0, "exposure": 1.0}
        for i, level in enumerate(levels)
    ]


def _algorithm(bundle: dict[str, Any]) -> dict[str, Any]:
    stored: dict[str, Any] = bundle["resolved_payloads"][bundle["algorithm_ref"]]
    return stored


def _set_input(bundle: dict[str, Any], name: str, **changes: Any) -> None:
    """Change one input-contract entry in the graph and in the stored algorithm, which the real
    scorer reads: the two stay one statement."""
    for contract in (bundle["graph"]["input_contract"], _algorithm(bundle)["input_contract"]):
        next(entry for entry in contract if entry["name"] == name).update(changes)


def _main_effects() -> dict[str, Any]:
    """The clean bundle refitted as one main effect, region on A, B, with no cross and no yoa term:
    a bundle the real scorer scores, and one whose region is closed-input."""
    bundle = copy.deepcopy(_clean())
    fit = bundle["resolved_payloads"][_MODEL]["fit_result"]
    template = fit["coefficients"][1]
    fit["coefficients"] = [fit["coefficients"][0], {**template, "term": "region[B]"}]
    del fit["relativities"]["region_x_yoa"]
    _region_fitted(bundle, _MODEL, ["A", "B"])
    spec = bundle["resolved_payloads"][_MODEL]["spec"]
    region = bundle["resolved_payloads"]["factor:region@1"]["id"]
    spec["factors"] = [region]
    return bundle


def _closed() -> dict[str, Any]:
    """Region undeclared and fitted on A, B, the input's own domain, as a main effect."""
    return _main_effects()


def _with_second_model(bundle: dict[str, Any], levels: list[str]) -> None:
    """A second GLM payload, a copy of the first fitted on levels, and a second model_call."""
    payloads = bundle["resolved_payloads"]
    payloads[_SECOND] = copy.deepcopy(payloads[_MODEL])
    _region_fitted(bundle, _SECOND, levels)
    nodes = bundle["graph"]["nodes"]
    nodes["s_risk2"] = {**nodes["s_risk"], "model_ref": _SECOND, "produces": ["risk2"]}


@pytest.mark.req("FR-2143")
def test_a_factor_fed_only_by_a_closed_enum_over_its_levels_is_not_reachable() -> None:
    rc, lines = _run([_row(_closed(), "closed", 1)])

    assert rc == 0
    assert "NOTREACHABLE closed@1 status=approved (closed-input)" in lines
    assert "not-reachable: 1" in lines
    assert "plain: 0" in lines
    assert any(line.startswith("NOTEXAMINED-CONTRACT 0 (") for line in lines)
    assert not any(line.startswith("PLAIN ") for line in lines)


@pytest.mark.req("FR-2143")
def test_an_open_input_keeps_the_factor_plain() -> None:
    bundle = _closed()
    _input(bundle, "region")["domain"] = ["A", "B", "C"]
    rc, lines = _run([_row(bundle, "open", 1)])

    assert rc == 1
    assert "PLAIN open@1 status=approved" in lines
    assert "not-reachable: 0" in lines


@pytest.mark.req("FR-2143")
def test_the_closed_check_is_made_per_glm_a_second_fit_lacking_a_level_stays_plain() -> None:
    bundle = _closed()
    _with_second_model(bundle, ["A"])  # the second fit never saw B, which the input admits
    rc, lines = _run([_row(bundle, "severity", 1)])

    assert rc == 1
    assert "PLAIN severity@1 status=approved" in lines
    assert "not-reachable: 0" in lines


@pytest.mark.req("FR-2143")
def test_two_fits_each_over_the_whole_domain_are_not_reachable() -> None:
    bundle = _closed()
    _with_second_model(bundle, ["A", "B"])
    rc, lines = _run([_row(bundle, "both", 1)])

    assert rc == 0
    assert "NOTREACHABLE both@1 status=approved (closed-input)" in lines


def _structured(second_levels: list[str]) -> dict[str, Any]:
    """The closed bundle whose one model_call scores through a Peril Structure of two GLMs."""
    from model_schema import (
        ArtifactRef,
        LargeLossKind,
        LargeLossTreatment,
        PerilComponent,
        PerilMethod,
        PerilStructure,
    )

    bundle = _closed()
    _with_second_model(bundle, second_levels)
    nodes = bundle["graph"]["nodes"]
    del nodes["s_risk2"]
    structure = PerilStructure(
        id=UUID("11111111-1111-4111-8111-111111111111"),
        slug="motor-perils",
        version=1,
        perils=(
            PerilComponent(
                peril="AD",
                method=PerilMethod.FREQUENCY_SEVERITY,
                frequency_model=ArtifactRef.model_validate(_MODEL),
                severity_model=ArtifactRef.model_validate(_SECOND),
                large_loss=LargeLossTreatment(kind=LargeLossKind.NONE),
            ),
        ),
        created_at=datetime(2026, 10, 1, tzinfo=UTC),
    )
    bundle["resolved_payloads"]["peril_structure:motor-perils@1"] = structure.model_dump(
        mode="json"
    )
    nodes["s_risk"]["model_ref"] = None
    nodes["s_risk"]["peril_structure_ref"] = "peril_structure:motor-perils@1"
    return bundle


@pytest.mark.req("FR-2143")
def test_a_factor_scored_through_a_peril_structure_is_judged_on_every_component() -> None:
    rc, lines = _run([_row(_structured(["A", "B"]), "perils", 1)])
    assert rc == 0
    assert "NOTREACHABLE perils@1 status=approved (closed-input)" in lines

    rc, lines = _run([_row(_structured(["A"]), "perils", 2)])
    assert rc == 1
    assert "PLAIN perils@2 status=approved" in lines


@pytest.mark.req("FR-2143")
def test_a_value_from_a_step_a_nullable_input_or_an_approximation_stays_plain() -> None:
    from_a_step = _closed()
    nodes = from_a_step["graph"]["nodes"]
    nodes["s_derived"] = {**nodes["s_region"], "type": "expression", "produces": ["derived"]}
    nodes["s_risk"]["feature_map"]["derived"] = "region"
    del nodes["s_risk"]["feature_map"]["region"]

    nullable = _closed()
    _input(nullable, "region")["nullable"] = True

    approximate = _closed()
    approximate["graph"]["nodes"]["s_risk"]["mode"] = "approximation"

    for index, bundle in enumerate((from_a_step, nullable, approximate)):
        rc, lines = _run([_row(bundle, "case", index)])
        assert rc == 1, index
        assert f"PLAIN case@{index} status=approved" in lines


@pytest.mark.req("FR-2143")
def test_a_version_with_one_closed_and_one_open_factor_stays_plain() -> None:
    bundle = _closed()
    fit = bundle["resolved_payloads"][_MODEL]["fit_result"]
    fit["relativities"]["yoa"] = [{"level": "2010", "is_base": True}]  # the input admits 2011 too
    yoa = bundle["resolved_payloads"]["factor:yoa@1"]["id"]
    bundle["resolved_payloads"][_MODEL]["spec"]["factors"].append(yoa)
    rc, lines = _run([_row(bundle, "mixed", 1)])

    assert rc == 1
    assert "PLAIN mixed@1 status=approved" in lines
    assert "not-reachable: 0" in lines


@pytest.mark.req("FR-2143")
def test_a_glm_no_model_call_scores_is_not_reachable_whatever_the_input_admits() -> None:
    bundle = _closed()
    _input(bundle, "region")["domain"] = ["A", "B", "C"]  # open, yet nothing scores the first fit
    _with_second_model(bundle, ["A", "B", "C"])
    nodes = bundle["graph"]["nodes"]
    nodes["s_risk"]["model_ref"] = _SECOND  # the only model_call now scores the second GLM
    del nodes["s_risk2"]
    rc, lines = _run([_row(bundle, "unscored", 1)])

    assert rc == 0
    assert "NOTREACHABLE unscored@1 status=approved (closed-input,not-scored)" in lines


@pytest.mark.req("FR-2143")
def test_an_input_read_with_a_default_or_a_second_producer_stays_plain() -> None:
    with_a_default = _closed()
    with_a_default["graph"]["nodes"]["s_region"]["on_missing"] = "default"

    with_a_second_producer = _closed()
    nodes = with_a_second_producer["graph"]["nodes"]
    nodes["s_region_again"] = {**nodes["s_region"], "type": "expression", "produces": ["region"]}

    for index, bundle in enumerate((with_a_default, with_a_second_producer)):
        rc, lines = _run([_row(bundle, "case", index)])
        assert rc == 1, index
        assert f"PLAIN case@{index} status=approved" in lines


@pytest.mark.req("FR-2143")
def test_a_second_model_call_scoring_the_glm_from_an_open_input_keeps_it_plain() -> None:
    """Every model_call that scores the GLM must feed the Factor from a closed input (FR-2143): a
    second call to the same GLM, fed from an open input, makes the Factor reachable."""
    bundle = _closed()
    graph = bundle["graph"]
    graph["input_contract"].append(
        {**_input(bundle, "region"), "name": "region2", "domain": ["A", "B", "C"]}
    )
    nodes = graph["nodes"]
    nodes["s_region2"] = {
        **nodes["s_region"], "input_name": "region2", "label": "region2", "produces": ["region2"],
    }
    nodes["s_risk_again"] = {
        **nodes["s_risk"],
        "consumes": ["region2"],
        "feature_map": {**nodes["s_risk"]["feature_map"], "region": "region2"},
        "produces": ["risk_again"],
    }
    rc, lines = _run([_row(bundle, "two-calls", 1)])

    assert rc == 1
    assert "PLAIN two-calls@1 status=approved" in lines, lines
    assert "not-reachable: 0" in lines


@pytest.mark.req("FR-2143")
def test_a_model_call_in_a_purpose_graph_is_judged_with_the_base_graphs() -> None:
    """The base graph's call reads a closed input; a purpose graph's call to the same GLM reads an
    open one (its input contract admits C, which the fit never saw): the version stays PLAIN."""
    bundle = _closed()
    purpose = copy.deepcopy(bundle["graph"])
    next(c for c in purpose["input_contract"] if c["name"] == "region")["domain"] = ["A", "B", "C"]
    bundle["purpose_graphs"] = {"cancellation": purpose}
    rc, lines = _run([_row(bundle, "purposed", 1)])

    assert rc == 1
    assert "PLAIN purposed@1 status=approved" in lines, lines

    closed_everywhere = _closed()
    closed_everywhere["purpose_graphs"] = {
        "cancellation": copy.deepcopy(closed_everywhere["graph"])
    }
    rc, lines = _run([_row(closed_everywhere, "purposed", 2)])

    assert rc == 0
    assert "NOTREACHABLE purposed@2 status=approved (closed-input)" in lines, lines


# --- #1906: the two bundles a review found listed NOTREACHABLE while a quote was refused --------


def _her_offset(offset_levels: list[str]) -> dict[str, Any]:
    """Region fitted A, B, C with the input's domain A, B, C, as a main effect, and a second GLM
    fitted on offset_levels as the first's offset model (spec.offset)."""
    bundle = _main_effects()
    _region_fitted(bundle, _MODEL, ["A", "B", "C"])
    _set_input(bundle, "region", domain=["A", "B", "C"])
    payloads = bundle["resolved_payloads"]
    payloads[_SECOND] = copy.deepcopy(payloads[_MODEL])
    _region_fitted(bundle, _SECOND, offset_levels)
    payloads[_MODEL]["spec"]["offset"] = {
        "kind": "model", "column": None, "offset_model_ref": _SECOND,
    }
    return bundle


def _her_interaction() -> dict[str, Any]:
    """The clean bundle, cross included: region fitted A, B, C with the input's domain A, B, C,
    and the cross left with its four cells, none for C."""
    bundle = copy.deepcopy(_clean())
    _region_fitted(bundle, _MODEL, ["A", "B", "C"])
    _set_input(bundle, "region", domain=["A", "B", "C"])
    return bundle


@pytest.mark.req("FR-2143")
def test_an_offset_glm_fitted_on_fewer_levels_keeps_the_version_plain() -> None:
    rc, lines = _run([_row(_her_offset(["A", "B"]), "offset", 1)])

    assert "PLAIN offset@1 status=approved" in lines, lines
    assert not any(line.startswith("NOTREACHABLE ") for line in lines)
    assert rc == 1


@pytest.mark.req("FR-2143")
def test_an_offset_glm_over_the_whole_domain_is_scored_not_unscored() -> None:
    rc, lines = _run([_row(_her_offset(["A", "B", "C"]), "offset", 1)])

    assert "NOTREACHABLE offset@1 status=approved (closed-input)" in lines, lines
    assert rc == 0


@pytest.mark.req("FR-2143")
def test_an_offset_of_an_offset_is_followed_to_its_end() -> None:
    bundle = _her_offset(["A", "B", "C"])
    payloads = bundle["resolved_payloads"]
    third = "model:motor-third-glm@1"
    payloads[third] = copy.deepcopy(payloads[_SECOND])
    _region_fitted(bundle, third, ["A", "B"])
    payloads[_SECOND]["spec"]["offset"] = {
        "kind": "model", "column": None, "offset_model_ref": third,
    }
    rc, lines = _run([_row(bundle, "chain", 1)])

    assert "PLAIN chain@1 status=approved" in lines, lines
    assert rc == 1


@pytest.mark.req("FR-2143")
def test_a_factor_an_interaction_takes_as_an_operand_is_never_closed_input() -> None:
    rc, lines = _run([_row(_her_interaction(), "ix", 1)])

    assert "PLAIN ix@1 status=approved" in lines, lines
    assert not any(line.startswith("NOTREACHABLE ") for line in lines)
    assert rc == 1


@pytest.mark.req("FR-2143")
def test_an_interaction_outside_the_glms_factors_leaves_the_operand_closed() -> None:
    bundle = _main_effects()  # the cross Factor is carried, and is not one of this GLM's factors
    cross = bundle["resolved_payloads"]["factor:region_x_yoa@1"]["id"]
    assert cross not in bundle["resolved_payloads"][_MODEL]["spec"]["factors"]
    rc, lines = _run([_row(bundle, "ix", 2)])

    assert "NOTREACHABLE ix@2 status=approved (closed-input)" in lines, lines
    assert rc == 0


@pytest.mark.req("FR-2143")
def test_a_version_with_a_reachable_class_is_not_also_listed_notreachable() -> None:
    bundle = _closed()  # region is closed; a ghost level indicator has no relativities entry
    fit = bundle["resolved_payloads"][_MODEL]["fit_result"]
    fit["coefficients"].append({**fit["coefficients"][1], "term": "ghost[x]"})
    rc, lines = _run([_row(bundle, "both", 1)])

    assert "NORELATIVITIES both@1 status=approved" in lines, lines
    assert not any(line.startswith("NOTREACHABLE ") for line in lines)
    assert "not-reachable: 0" in lines
    assert rc == 1


@pytest.mark.req("FR-2143")
def test_a_version_carrying_a_not_examined_line_is_not_listed_notreachable() -> None:
    bundle = _closed()
    fit = bundle["resolved_payloads"][_MODEL]["fit_result"]
    fit["coefficients"].append({**fit["coefficients"][1], "term": "region[3.0]"})
    rc, lines = _run([_row(bundle, "numeric", 1)])

    assert any(line.startswith("NOTEXAMINED-NUMERIC-TERMS numeric@1") for line in lines), lines
    assert not any(line.startswith("NOTREACHABLE ") for line in lines)
    assert rc == 0


@pytest.mark.req("FR-2143")
def test_an_unbanded_expression_factor_with_relativities_is_plain() -> None:
    bundle = _closed()
    factor = bundle["resolved_payloads"]["factor:region@1"]
    factor["type"] = "expression"
    factor["expression"] = "region"
    rc, lines = _run([_row(bundle, "expr", 1)])

    assert "PLAIN expr@1 status=approved" in lines, lines
    assert rc == 1


# --- the second, differently built check: the real scorer, never the classifier ---------------


def _quote_combinations(bundle: dict[str, Any]) -> list[dict[str, object]]:
    """Every combination of the declared domains of the bundle's enum inputs (the contract's own,
    all of them, not only the ones the classifier called closed); another input is held at a
    valid value. Never a sample."""
    contract = bundle["graph"]["input_contract"]
    fixed: dict[str, object] = {
        entry["name"]: 1 for entry in contract if entry["type"] not in ("enum",)
    }
    enums = [(entry["name"], entry["domain"]) for entry in contract if entry["type"] == "enum"]
    combos: list[dict[str, object]] = [dict(fixed)]
    for name, domain in enums:
        combos = [{**combo, name: level} for combo in combos for level in domain]
    return combos


def _refusals(bundle: dict[str, Any]) -> list[str]:
    """Score every combination through the runtime's own loader and entry; the refusals' codes."""
    import asyncio

    from model_schema import ArtifactRef
    from model_schema.scoring import QuoteContext, QuoteContextOptions
    from pricing_core.rating.compile import Bundle
    from pricing_core.rating.runtime import load_bundle
    from pricing_core.rating.score import score_one

    compiled = load_bundle(Bundle.model_validate(bundle))
    reference = ArtifactRef(type="rating_version", slug="probe-rv", version=1)

    async def score_all() -> list[str]:
        refused: list[str] = []
        for combo in _quote_combinations(bundle):
            context = QuoteContext(
                purpose="new_business",
                quoted_at=datetime(2026, 11, 1, tzinfo=UTC),
                effective_date=date(2026, 11, 1),
                inputs=combo,
                options=QuoteContextOptions(rating_version_ref=reference),
            )
            try:
                await score_one(compiled, context)
            except Exception as exc:
                refused.append(f"{sorted(combo.items())}: {type(exc).__name__}: {str(exc)[:90]}")
        return refused

    return asyncio.run(score_all())


def _closed_with_a_purpose_graph() -> dict[str, Any]:
    bundle = _closed()
    bundle["purpose_graphs"] = {"cancellation": copy.deepcopy(bundle["graph"])}
    return bundle


def _mirror_the_second_call(bundle: dict[str, Any], model: str) -> None:
    """The real loader re-inlines the stored algorithm and compares it with the graph: the second
    model_call `_with_second_model` put in the graph goes into the algorithm too."""
    steps = _algorithm(bundle)["steps"]
    first = next(step for step in steps if step["type"] == "model_call")
    steps.append({**first, "step_id": "s_risk2", "model_ref": model, "produces": ["risk2"]})
    bundle["pins"]["models"].append(model)


def _two_fits_over_the_whole_domain() -> dict[str, Any]:
    bundle = _closed()
    _with_second_model(bundle, ["A", "B"])
    _mirror_the_second_call(bundle, _SECOND)
    return bundle


def _unscored_glm() -> dict[str, Any]:
    """The test above's bundle: an open input, and the first GLM scored by no model_call."""
    bundle = _closed()
    _set_input(bundle, "region", domain=["A", "B", "C"])
    _with_second_model(bundle, ["A", "B", "C"])
    nodes = bundle["graph"]["nodes"]
    nodes["s_risk"]["model_ref"] = _SECOND
    del nodes["s_risk2"]
    next(s for s in _algorithm(bundle)["steps"] if s["type"] == "model_call")["model_ref"] = _SECOND
    bundle["pins"]["models"].append(_SECOND)
    return bundle


def _closed_fixtures() -> dict[str, dict[str, Any]]:
    """Every fixture above the sweep lists NOTREACHABLE (closed-input), each scored for real."""
    return {
        "main-effects": _main_effects(),
        "offset-over-the-whole-domain": _her_offset(["A", "B", "C"]),
        "two-fits-over-the-whole-domain": _two_fits_over_the_whole_domain(),
        "peril-structure-over-the-whole-domain": _structured(["A", "B"]),
        "a-glm-no-model-call-scores": _unscored_glm(),
        "a-closed-version-with-a-purpose-graph": _closed_with_a_purpose_graph(),
    }


@pytest.mark.req("FR-2143")
@pytest.mark.parametrize("name", sorted(_closed_fixtures()))
def test_every_version_listed_notreachable_scores_every_combination_of_its_inputs(
    name: str,
) -> None:
    bundle = _closed_fixtures()[name]
    _rc, lines = _run([_row(bundle, "fixture", 1)])

    assert any(
        line.startswith("NOTREACHABLE fixture@1 ") and "closed-input" in line for line in lines
    ), lines
    assert _refusals(bundle) == []


@pytest.mark.req("FR-2143")
@pytest.mark.parametrize(
    "name", ["offset-fitted-on-fewer-levels", "interaction-cell-absent"]
)
def test_the_two_bundles_a_review_found_are_refused_by_the_real_scorer_and_read_plain(
    name: str,
) -> None:
    bundle = (
        _her_offset(["A", "B"]) if name == "offset-fitted-on-fewer-levels" else _her_interaction()
    )
    rc, lines = _run([_row(bundle, "refused", 1)])
    refusals = _refusals(bundle)

    assert refusals, "the real scorer scored every combination"
    assert all("UNSEEN_LEVEL_BEHAVIOUR_REQUIRED" in line for line in refusals), refusals
    assert "PLAIN refused@1 status=approved" in lines, lines
    assert rc == 1


@pytest.mark.req("FR-2143")
def test_a_version_the_runtime_cannot_load_is_unreadable_by_the_exception_type() -> None:
    """The sweep takes what is scored from the runtime's own loader, so a Bundle the runtime cannot
    load (here a GLM whose Factor the Bundle does not carry) is UNREADABLE with the exception's
    type, never a class: such a version cannot quote at all."""
    bundle = _closed()
    del bundle["resolved_payloads"]["factor:region@1"]
    rc, lines = _run([_row(bundle, "unloadable", 1)])

    assert "UNREADABLE unloadable@1 status=approved (ValueError)" in lines, lines
    assert rc == 2
