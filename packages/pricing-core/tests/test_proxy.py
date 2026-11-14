"""Proxy assessment against answers known independently (`02` FR-2138, FR-2139, FR-2141).

The measures are checked three ways: closed-form answers (an independent characteristic
carries no information, a perfect proxy carries all of it), equivalence (an integer exposure
is the same thing as replicated rows), and agreement with scikit-learn on the replicated
frame. scikit-learn is the oracle only; the module under test is pure Polars and NumPy.
"""

from __future__ import annotations

import dataclasses
import math

import numpy as np
import polars as pl
import pytest
from sklearn.metrics import roc_auc_score
from sklearn.metrics.cluster import mutual_info_score

from pricing_core.modelling.proxy import (
    FactorProxyResult,
    ProxyAssessmentError,
    ProxyAssessmentResult,
    assess_proxies,
)

CLASSES = ["x", "y", "z"]


def _subject_reference(keys: list[str], labels: list[str], classes: list[str]) -> pl.DataFrame:
    """An individual-level table: one class per key, as shares of 0 and 1."""
    return pl.DataFrame(
        {"k": keys, **{c: [1.0 if lab == c else 0.0 for lab in labels] for c in classes}}
    )


def _frame(keys: list[str], levels: list[str], exposure: list[float]) -> pl.DataFrame:
    return pl.DataFrame({"k": keys, "level": levels, "exposure_years": exposure})


def _assess(frame: pl.DataFrame, ref: pl.DataFrame, classes: list[str]) -> ProxyAssessmentResult:
    return assess_proxies(frame, ["level"], ref, key="k", reference_key="k", classes=classes)


@pytest.mark.req("FR-2139")
def test_an_independent_characteristic_gives_mi_zero_and_auc_one_half() -> None:
    keys = ["k1", "k2", "k3", "k4"]
    frame = _frame(keys, ["A", "A", "B", "B"], [1.0] * 4)
    ref = _subject_reference(keys, ["x", "y", "x", "y"], ["x", "y"])
    only = _assess(frame, ref, ["x", "y"]).factors[0]
    assert only.mutual_information_bits == 0.0
    assert only.normalised_mutual_information == 0.0
    assert only.auc_by_class == {"x": 0.5, "y": 0.5}


@pytest.mark.req("FR-2139")
def test_a_perfect_proxy_gives_mi_equal_to_the_class_entropy_and_auc_one() -> None:
    keys = ["k1", "k2", "k3", "k4"]
    frame = _frame(keys, ["A", "A", "B", "B"], [1.0] * 4)
    ref = _subject_reference(keys, ["x", "x", "y", "y"], ["x", "y"])
    only = _assess(frame, ref, ["x", "y"]).factors[0]
    assert only.mutual_information_bits == pytest.approx(1.0)  # H = 1 bit for a 50:50 class
    assert only.normalised_mutual_information == pytest.approx(1.0)
    assert only.auc_by_class == {"x": 1.0, "y": 1.0}


@pytest.mark.req("FR-2139")
def test_a_single_class_has_nothing_to_normalise_by() -> None:
    keys = ["k1", "k2"]
    frame = _frame(keys, ["A", "B"], [1.0, 1.0])
    ref = _subject_reference(keys, ["x", "x"], ["x", "y"])
    only = _assess(frame, ref, ["x", "y"]).factors[0]
    assert only.mutual_information_bits == 0.0
    assert only.normalised_mutual_information is None
    assert only.auc_by_class == {"x": None, "y": None}  # no negatives / no positives


def _random_subject_case(seed: int) -> tuple[pl.DataFrame, pl.DataFrame]:
    rng = np.random.default_rng(seed)
    n = 60
    keys = [f"k{i}" for i in range(n)]
    levels = [f"L{i}" for i in rng.integers(0, 5, n)]
    labels = [CLASSES[i] for i in rng.integers(0, 3, n)]
    exposure = [float(v) for v in rng.integers(1, 6, n)]
    return _frame(keys, levels, exposure), _subject_reference(keys, labels, CLASSES)


def _replicate(frame: pl.DataFrame) -> pl.DataFrame:
    """One row per unit of integer exposure, each of exposure 1."""
    rows = [
        row
        for row in frame.to_dicts()
        for _ in range(int(row["exposure_years"]))
    ]
    return pl.DataFrame(rows).with_columns(pl.lit(1.0).alias("exposure_years"))


@pytest.mark.req("FR-2139")
def test_integer_exposure_is_equivalent_to_replicated_rows() -> None:
    frame, ref = _random_subject_case(7)
    weighted = _assess(frame, ref, CLASSES).factors[0]
    replicated = _assess(_replicate(frame), ref, CLASSES).factors[0]
    assert weighted.mutual_information_bits == pytest.approx(
        replicated.mutual_information_bits, abs=1e-12
    )
    for c in CLASSES:
        assert weighted.auc_by_class[c] == pytest.approx(replicated.auc_by_class[c], abs=1e-12)


@pytest.mark.req("FR-2139")
@pytest.mark.parametrize("seed", [1, 2, 3])
def test_subject_results_agree_with_scikit_learn_on_the_replicated_frame(seed: int) -> None:
    frame, ref = _random_subject_case(seed)
    got = _assess(frame, ref, CLASSES).factors[0]

    rep = _replicate(frame).join(ref, on="k")
    level = rep["level"].to_numpy()
    label = np.array([CLASSES[i] for i in rep.select(CLASSES).to_numpy().argmax(axis=1)])

    assert got.mutual_information_bits == pytest.approx(
        mutual_info_score(level, label) / math.log(2), abs=1e-10
    )
    for c in CLASSES:
        y = label == c
        # The oracle's score is built independently: the class share of each replicated row's level.
        share = {lv: y[level == lv].mean() for lv in np.unique(level)}
        score = np.array([share[lv] for lv in level])
        assert got.auc_by_class[c] == pytest.approx(roc_auc_score(y, score), abs=1e-10)


@pytest.mark.req("FR-2138", "FR-2139")
def test_area_shares_agree_with_the_expanded_weighted_frame() -> None:
    rng = np.random.default_rng(11)
    n_rows, n_areas = 80, 6
    areas = [f"a{i}" for i in range(n_areas)]
    shares = rng.dirichlet([1.0, 1.0, 1.0], size=n_areas)
    ref = pl.DataFrame({"k": areas, **{c: shares[:, j] for j, c in enumerate(CLASSES)}})
    row_area = rng.integers(0, n_areas, n_rows)
    level = np.array([f"L{i}" for i in rng.integers(0, 4, n_rows)])
    exposure = rng.uniform(0.2, 3.0, n_rows)
    frame = _frame([areas[i] for i in row_area], level.tolist(), exposure.tolist())

    got = _assess(frame, ref, CLASSES).factors[0]

    p = shares[row_area]  # each row's expected class shares
    levels = np.unique(level)
    joint = np.array([[(exposure * p[:, j])[level == lv].sum() for j in range(3)] for lv in levels])
    assert got.mutual_information_bits == pytest.approx(
        mutual_info_score(None, None, contingency=joint) / math.log(2), abs=1e-10
    )
    level_total = joint.sum(axis=1)
    for j, c in enumerate(CLASSES):
        # Expand each row to a positive (weight w*p) and a negative (weight w*(1-p)), scored by
        # its level's share of the class: the AUC the module claims to compute.
        score_by_level = dict(zip(levels, joint[:, j] / level_total, strict=True))
        score = np.array([score_by_level[lv] for lv in level])
        y = np.concatenate([np.ones(n_rows), np.zeros(n_rows)])
        s = np.concatenate([score, score])
        w = np.concatenate([exposure * p[:, j], exposure * (1 - p[:, j])])
        assert got.auc_by_class[c] == pytest.approx(
            roc_auc_score(y, s, sample_weight=w), abs=1e-10
        )


@pytest.mark.req("FR-2138", "FR-2139")
def test_unmatched_rows_are_excluded_and_counted_in_the_coverage() -> None:
    frame = _frame(["k1", "k2", "k3", "ghost"], ["A", "A", "B", "B"], [1.0, 1.0, 2.0, 4.0])
    ref = _subject_reference(["k1", "k2", "k3"], ["x", "y", "x"], ["x", "y"])
    result = _assess(frame, ref, ["x", "y"])
    assert result.matched_rows == 3
    assert result.matched_exposure == 4.0
    assert result.total_exposure == 8.0
    assert result.coverage == 0.5


@pytest.mark.req("FR-2138")
@pytest.mark.parametrize(
    ("ref", "match"),
    [
        (pl.DataFrame({"k": ["k1", "k1"], "x": [1.0, 0.0], "y": [0.0, 1.0]}), "repeated"),
        (pl.DataFrame({"k": ["k1", "k2"], "x": [0.5, 1.0], "y": [0.4, 0.0]}), "sum to 1"),
        (pl.DataFrame({"k": ["k1", "k2"], "x": [1.5, 1.0], "y": [-0.5, 0.0]}), r"\[0, 1\]"),
        (pl.DataFrame({"k": ["k1", "k2"], "x": [1.0, 0.0]}), "no column"),
    ],
)
def test_a_reference_table_that_fits_neither_granularity_is_refused(
    ref: pl.DataFrame, match: str
) -> None:
    frame = _frame(["k1", "k2"], ["A", "B"], [1.0, 1.0])
    with pytest.raises(ProxyAssessmentError, match=match):
        _assess(frame, ref, ["x", "y"])


@pytest.mark.req("FR-2139")
def test_negative_exposure_is_refused() -> None:
    frame = _frame(["k1", "k2"], ["A", "B"], [1.0, -1.0])
    ref = _subject_reference(["k1", "k2"], ["x", "y"], ["x", "y"])
    with pytest.raises(ProxyAssessmentError, match="exposure"):
        _assess(frame, ref, ["x", "y"])


@pytest.mark.req("FR-2141")
def test_the_result_has_no_threshold_or_verdict_and_a_perfect_proxy_refuses_nothing() -> None:
    allowed = {
        "ProxyAssessmentResult": {
            "matched_rows", "matched_exposure", "total_exposure", "coverage", "factors",
        },
        "FactorProxyResult": {
            "factor", "mutual_information_bits", "normalised_mutual_information", "auc_by_class",
        },
    }
    assert {f.name for f in dataclasses.fields(ProxyAssessmentResult)} == allowed[
        "ProxyAssessmentResult"
    ]
    assert {f.name for f in dataclasses.fields(FactorProxyResult)} == allowed["FactorProxyResult"]

    keys = ["k1", "k2", "k3", "k4"]
    frame = _frame(keys, ["A", "A", "B", "B"], [1.0] * 4)
    ref = _subject_reference(keys, ["x", "x", "y", "y"], ["x", "y"])
    result = _assess(frame, ref, ["x", "y"])  # AUC 1.0: returns, raises nothing, flags nothing
    assert result.factors[0].auc_by_class == {"x": 1.0, "y": 1.0}
