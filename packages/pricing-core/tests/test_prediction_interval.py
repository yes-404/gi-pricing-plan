"""FR-MODEL-63's interval, and the covariance blob it is computed from.

The interval is a **confidence interval for `E[Y|x]`** and not a prediction interval for an
individual outcome — the module docstring on `model_schema.prediction` has the reasoning and
`02` FR-MODEL-63 the dated note. That distinction is what
`test_the_interval_covers_the_true_mean_about_as_often_as_it_claims` measures: coverage of
the *mean*, which is the thing `x'Vx` is the variance of.

Everything else here is a refusal, in the shape `02` R5 asks for: an interval that cannot be
trusted must fail to be produced rather than be produced and read.
"""

from __future__ import annotations

import json
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Factor,
    FactorType,
    GlmSpec,
    OffsetSpec,
)
from pricing_core.modelling import GlmFitError, decode_covariance, encode_covariance, fit_glm
from pricing_core.modelling.predict import predict_glm, predict_glm_interval


def _factor(slug: str, column: str) -> Factor:
    return Factor(
        id=uuid4(), slug=slug, dataset_id=uuid4(), version=1,
        type=FactorType.IDENTITY, source_columns=(column,),
    )


def _book(n: int = 8_000, seed: int = 20260818) -> pl.DataFrame:
    """log(mu) = log(exposure) - 2.0 + 0.5·[urban] + 0.03·(age - 40)."""
    rng = np.random.default_rng(seed)
    exposure = rng.uniform(0.25, 1.0, n)
    urban = rng.integers(0, 2, n)
    age = rng.integers(18, 80, n)
    eta = np.log(exposure) - 2.0 + 0.5 * urban + 0.03 * (age - 40)
    return pl.DataFrame(
        {
            "exposure_years": exposure,
            "area": ["urban" if u else "rural" for u in urban],
            "driv_age": age.astype(float),
            "claim_count": rng.poisson(np.exp(eta)).astype(float),
        }
    )


def _spec(**over: object) -> GlmSpec:
    base: dict[str, object] = {
        "model_family_slug": "motor-frequency",
        "dataset_version_id": uuid4(),
        "response_column": "claim_count",
        "offset": OffsetSpec(kind="log_column", column="exposure_years"),
        "family": "poisson",
        "link": "log",
    }
    base.update(over)
    return GlmSpec(**base)  # type: ignore[arg-type]


def _factors() -> list[Factor]:
    return [_factor("area", "area"), _factor("driv_age", "driv_age")]


@pytest.mark.req("FR-MODEL-63")
def test_the_fit_returns_a_covariance_blob_addressing_its_own_bytes() -> None:
    """The `BlobRef` is a pure function of the bytes beside it (ADR-0001, FR-MODEL-31).

    `pricing-core` cannot store a blob, so the contract with the caller is that the digest
    is already correct and the caller's only job is to write those bytes under it. A
    reference computed from anything else would resolve to nothing after a fit that
    reported success.
    """
    import hashlib

    fit = fit_glm(_book(), _spec(), _factors())

    assert fit.result.covariance_blob is not None
    ref = fit.result.covariance_blob
    assert ref.sha256 == hashlib.sha256(fit.covariance_bytes).hexdigest()
    assert ref.bytes_ == len(fit.covariance_bytes)
    assert ref.media_type == "application/json"


@pytest.mark.req("FR-MODEL-21")
def test_the_stored_diagonal_is_the_standard_errors_that_were_reported() -> None:
    """One matrix behind both numbers, which is what makes them comparable.

    The standard errors used to come from `glum.std_errors()` and the matrix did not exist;
    if the two were computed by separate paths, a coefficient's reported `std_error` and the
    width of a prediction interval through that coefficient could disagree, and nothing
    would say which was right.
    """
    fit = fit_glm(_book(), _spec(), _factors())
    assert fit.result.covariance_blob is not None

    terms = [c.term for c in fit.result.coefficients]
    matrix = decode_covariance(fit.covariance_bytes, terms)

    reported = np.array([c.std_error for c in fit.result.coefficients])
    assert np.allclose(np.sqrt(matrix.diagonal()), reported, rtol=1e-12)


@pytest.mark.req("FR-MODEL-63")
def test_the_off_diagonal_terms_change_the_interval_materially() -> None:
    """The off-diagonal terms are why a `p x p` blob is stored rather than `p` numbers.

    `Var(sum b_j x_j)` equals the sum of the coefficient variances only when the estimates
    are independent, which a design sharing an intercept never gives. **The direction is not
    fixed** — a negative correlation between the intercept and a centred continuous term
    makes the correct interval *narrower* than the diagonal-only one, a positive one makes
    it wider — and that is precisely why the standard errors are not a substitute: a scorer
    using them alone is wrong by an amount whose sign it cannot know. The assertion is
    therefore on the size of the difference, not on which way it goes.
    """
    data = _book()
    spec, factors = _spec(), _factors()
    fit = fit_glm(data, spec, factors)
    assert fit.result.covariance_blob is not None

    terms = [c.term for c in fit.result.coefficients]
    full = decode_covariance(fit.covariance_bytes, terms)
    assert not np.allclose(full, np.diag(full.diagonal()))

    rows = data.head(50)
    _, lower, upper = predict_glm_interval(
        fit.result, rows, factors, spec, covariance_bytes=fit.covariance_bytes
    )
    diagonal_only = encode_covariance(terms, np.diag(full.diagonal()))
    _, naive_lower, naive_upper = predict_glm_interval(
        fit.result, rows, factors, spec, covariance_bytes=diagonal_only
    )
    ratio = (naive_upper - naive_lower) / (upper - lower)
    assert np.all(np.abs(ratio - 1.0) > 0.05)


@pytest.mark.req("FR-MODEL-63")
def test_the_interval_covers_the_true_mean_about_as_often_as_it_claims() -> None:
    """A nominal 95 % interval on `E[Y|x]` that covers 60 % of the time is not an interval.

    Coverage is measured against the mean the generator used, not against the simulated
    counts: `x'Vx` is the variance of the *estimated* linear predictor, so the quantity it
    brackets is `exp(eta)`, and a test that pointed it at `claim_count` would be measuring a
    prediction interval this deliberately is not.
    """
    data = _book(n=6_000, seed=7)
    spec, factors = _spec(), _factors()
    fit = fit_glm(data, spec, factors)
    assert fit.result.covariance_blob is not None

    truth = np.exp(
        np.log(data["exposure_years"].to_numpy())
        - 2.0
        + 0.5 * (data["area"].to_numpy() == "urban")
        + 0.03 * (data["driv_age"].to_numpy() - 40)
    )
    _, lower, upper = predict_glm_interval(
        fit.result, data, factors, spec, covariance_bytes=fit.covariance_bytes
    )
    coverage = float(np.mean((truth >= lower) & (truth <= upper)))
    assert 0.85 <= coverage <= 1.0


@pytest.mark.req("FR-MODEL-62")
def test_the_expectation_is_the_one_predict_glm_already_returned() -> None:
    """Two entry points, one number. The interval path builds the design as a matrix and the
    streaming path accumulates it column by column; a divergence between them would mean the
    interval was drawn around a centre no other caller sees."""
    data = _book()
    spec, factors = _spec(), _factors()
    fit = fit_glm(data, spec, factors)
    assert fit.result.covariance_blob is not None

    expected, _, _ = predict_glm_interval(
        fit.result, data, factors, spec, covariance_bytes=fit.covariance_bytes
    )
    assert np.allclose(expected, predict_glm(fit.result, data, factors, spec), rtol=1e-12)


@pytest.mark.req("FR-MODEL-63")
def test_the_offset_scales_the_interval_without_widening_it_relatively() -> None:
    """The offset is a known constant: it belongs in the centre, not in the width.

    Doubling exposure doubles the expectation and both bounds under a log link, leaving the
    interval's width *relative to* the expectation unchanged. A scorer that put the offset
    into the variance would report a wider relative interval for a longer policy term, which
    is not a thing the fit knows.
    """
    data = _book().head(100)
    spec, factors = _spec(), _factors()
    fit = fit_glm(_book(), spec, factors)
    assert fit.result.covariance_blob is not None

    def relative_width(frame: pl.DataFrame) -> np.ndarray:
        expected, lower, upper = predict_glm_interval(
            fit.result, frame, factors, spec, covariance_bytes=fit.covariance_bytes
        )
        return (upper - lower) / expected

    doubled = data.with_columns(pl.col("exposure_years") * 2.0)
    assert np.allclose(relative_width(data), relative_width(doubled), rtol=1e-10)


@pytest.mark.req("FR-MODEL-63")
def test_a_covariance_blob_written_for_other_terms_is_refused() -> None:
    """A covariance matrix is positional, and the wrong one produces a plausible number.

    Paired with a design built in a different order, `x'Vx` is the variance of a linear
    combination nobody estimated — positive, finite, and wrong. Nothing downstream can
    detect that, which is why the term order travels inside the blob and is checked here.
    """
    data = _book()
    spec, factors = _spec(), _factors()
    fit = fit_glm(data, spec, factors)
    assert fit.result.covariance_blob is not None

    terms = [c.term for c in fit.result.coefficients]
    matrix = decode_covariance(fit.covariance_bytes, terms)
    shuffled = encode_covariance([terms[0], *reversed(terms[1:])], matrix)

    with pytest.raises(GlmFitError) as raised:
        predict_glm_interval(
            fit.result, data.head(5), factors, spec, covariance_bytes=shuffled
        )
    assert raised.value.code == "GLM_RANK_DEFICIENT"
    assert "different set of terms" in str(raised.value)


@pytest.mark.req("FR-MODEL-63")
def test_a_covariance_blob_that_is_not_one_is_refused_rather_than_guessed_at() -> None:
    """Neither a truncated blob nor a matrix of the wrong size yields an interval."""
    with pytest.raises(GlmFitError):
        decode_covariance(b"not json", ["intercept"])
    with pytest.raises(GlmFitError):
        decode_covariance(json.dumps({"terms": ["intercept"]}).encode(), ["intercept"])
    with pytest.raises(GlmFitError):
        decode_covariance(
            json.dumps({"terms": ["intercept"], "matrix": [[1.0, 0.0]]}).encode(),
            ["intercept"],
        )


@pytest.mark.req("FR-MODEL-63")
def test_the_bounds_come_back_ordered_under_a_decreasing_inverse_link() -> None:
    """`g⁻¹` for `inverse` is decreasing, so the transformed endpoints arrive swapped.

    This is the only link in `02`'s set where the naive `(g⁻¹(η-h), g⁻¹(η+h))` is reversed,
    and `PredictedRow` refuses a reversed pair — so without the re-ordering here the
    endpoint would 500 on a model the platform is happy to fit.
    """
    rng = np.random.default_rng(11)
    n = 4_000
    age = rng.integers(18, 80, n).astype(float)
    eta = 0.5 + 0.004 * (age - 40)
    data = pl.DataFrame({"driv_age": age, "cost": rng.gamma(20.0, 1.0 / (20.0 * eta), n)})
    spec = GlmSpec(
        model_family_slug="motor-severity",
        dataset_version_id=uuid4(),
        response_column="cost",
        offset=OffsetSpec(kind="none"),
        family="gamma",
        link="inverse",
    )
    factors = [_factor("driv_age", "driv_age")]
    fit = fit_glm(data, spec, factors)
    assert fit.result.covariance_blob is not None

    expected, lower, upper = predict_glm_interval(
        fit.result, data.head(200), factors, spec, covariance_bytes=fit.covariance_bytes
    )
    assert np.all(lower <= upper)
    assert np.all(lower <= expected)
    assert np.all(expected <= upper)


@pytest.mark.req("FR-MODEL-63")
def test_a_confidence_level_that_is_not_a_probability_is_refused() -> None:
    """`level=1.0` is an infinitely wide interval and `level=0` a point; neither is one."""
    from pricing_core.modelling.predict import PredictionError

    data = _book().head(20)
    spec, factors = _spec(), _factors()
    fit = fit_glm(_book(), spec, factors)

    for level in (0.0, 1.0, -0.5, 2.0):
        with pytest.raises(PredictionError):
            predict_glm_interval(
                fit.result, data, factors, spec,
                covariance_bytes=fit.covariance_bytes, level=level,
            )
