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
from typing import Any

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
    rc, lines = _run([_row(bundle, "plain", 1)])

    assert rc == 1
    assert "PLAIN plain@1 status=approved" in lines
    assert any(line.startswith("NOTEXAMINED-CONTRACT 1 (PLAIN is an upper bound") for line in lines)


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
