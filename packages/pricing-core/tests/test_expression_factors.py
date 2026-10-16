"""An `expression` Factor resolves through the `factor` profile — or is refused by name.

`RL-1615` (WK-690 Slice 4, `SL-1274`), with `PL-1665` 4.3' for the list of limbs. Each test
is one limb of the ruling's Ruled table, seen failing first:

* **numeric and unbanded** -> `FactorResolutionError` naming FR-210 (`RL-1265` DP-4);
* **string and banded** -> refused (a category is not banded);
* **numeric and banded** -> `apply_banding` on the result;
* **string and unbanded** -> a categorical Factor;
* a **`source_expression` mismatch** -> refused at resolution, compared as a *normalised
  parse* (an AST dump), so white space is not a difference;
* **versioning** (FR-96) -> a Factor v2 with a changed expression that pins the v1 Banding.

Today every one of these fails at the same point, for the same cause: `Factor` has no
`expression` field (`extra="forbid"`). That is the cause the slice removes, so each test
asserts the field's existence **first** (`_require_the_new_fields`), at its own line, and
only then builds its input; the resolution limbs are red behind it by construction, which
is why each test asserts what it asserts about the *outcome* and not only that something
raised.
"""

from __future__ import annotations

from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    GlmSpec,
    OffsetSpec,
    SplitRef,
    new_uuid7,
)
from pricing_core.modelling import (
    FactorResolutionError,
    build_glm_approximation,
    fit_gbm,
    fit_glm,
    resolve_factors,
)

DATASET = uuid4()
EXPOSURE = OffsetSpec(kind="log_column", column="exposure_years")

#: `driver_age / 2` runs 9.0 to 38.5 over the book below. The three steps are cut on the
#: *result* of the expression, so a fit that banded the raw column, or did not band at all,
#: cannot recover them.
EXPRESSION = "driver_age / 2"
_STEP = {"9-18": 0.10, "19-28": 0.075, "29+": 0.05}


def _book(n: int = 20_000, seed: int = 20261014) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 78, n).astype(float)
    half = age / 2
    step = np.where(half < 19, 0.10, np.where(half < 29, 0.075, 0.05))
    exposure = rng.uniform(0.5, 1.0, n)
    counts = rng.poisson(step * exposure)
    return pl.DataFrame(
        {
            "driver_age": age,
            "region": rng.choice(["N1", "N2", "S1", "S2"], n),
            "alt_region": rng.choice(["E1", "E2"], n),
            "exposure_years": exposure,
            "claim_count": counts.astype(float),
            "claim_amount_minor": (counts * 200_000).astype(np.int64),
        }
    )


def _banding(source_expression: str = EXPRESSION, *, version: int = 1) -> Banding:
    return Banding(
        id=uuid4(), slug="half-age-steps", dataset_id=DATASET, version=version,
        source_expression=source_expression, method=BandingMethod.MANUAL,
        boundaries=(9.0, 19.0, 29.0, 39.0), labels=("9-18", "19-28", "29+"),
    )


def _factor(expression: str = EXPRESSION, *, columns: tuple[str, ...] = ("driver_age",),
            **over: object) -> Factor:
    base: dict[str, object] = {
        "id": uuid4(), "slug": "half_age", "dataset_id": DATASET, "version": 1,
        "type": FactorType.EXPRESSION, "source_columns": columns, "expression": expression,
    }
    base.update(over)
    return Factor(**base)  # type: ignore[arg-type]


def _require_the_new_fields() -> None:
    """The first assert of every test: the cause this slice removes, stated where it fails.

    `PL-1665` 4.1' / 4.3': `Factor.expression` and `Banding.source_expression` do not exist
    yet, so the helpers below cannot build the input. Asserting the fields first puts the
    red at the test's own assert, so a later partial fix cannot turn a test green (or move
    its red elsewhere) for a reason other than the behaviour it names.
    """
    assert "expression" in Factor.model_fields, (
        "PL-1665 4.1': Factor must carry `expression` (FR-95)"
    )
    assert "source_expression" in Banding.model_fields, (
        "PL-1665 4.1': Banding must carry `source_expression` (FR-97)"
    )


@pytest.mark.req("FR-95")
def test_a_numeric_unbanded_expression_is_refused_naming_fr_210() -> None:
    """`RL-1265` DP-4 (b): the refusal's message names FR-210, and the refusal is by dtype."""
    _require_the_new_fields()
    factor = _factor()
    with pytest.raises(FactorResolutionError, match="FR-210") as excinfo:
        resolve_factors(_book(200), [factor])
    assert "half_age" in str(excinfo.value)


@pytest.mark.req("FR-95")
def test_a_string_banded_expression_is_refused() -> None:
    """A category is not banded: the Banding would receive text it cannot cut."""
    _require_the_new_fields()
    banding = _banding("where(driver_age > 40, region, alt_region)")
    factor = _factor(
        "where(driver_age > 40, region, alt_region)",
        columns=("driver_age", "region", "alt_region"),
        banding_id=banding.id,
    )
    with pytest.raises(FactorResolutionError, match="half_age"):
        resolve_factors(_book(200), [factor], bandings={banding.id: banding})


@pytest.mark.req("FR-95")
def test_a_numeric_banded_expression_resolves_through_apply_banding() -> None:
    _require_the_new_fields()
    banding = _banding()
    factor = _factor(banding_id=banding.id)
    frame = _book(500)
    matrix = resolve_factors(frame, [factor], bandings={banding.id: banding})

    column = matrix.terms["half_age"]
    assert column in matrix.categorical
    assert set(matrix.frame[column].unique().to_list()) <= set(banding.labels)
    # The bands are cut on the expression's *result*: a 30-year-old is `15`, band `9-18`.
    youngest = matrix.frame.filter(pl.col("driver_age") == 30.0)[column].unique().to_list()
    assert youngest == ["9-18"]


@pytest.mark.req("FR-95")
def test_a_string_unbanded_expression_is_a_categorical_factor() -> None:
    _require_the_new_fields()
    expression = "where(driver_age > 40, region, alt_region)"
    factor = _factor(expression, columns=("driver_age", "region", "alt_region"))
    matrix = resolve_factors(_book(500), [factor])

    column = matrix.terms["half_age"]
    assert column in matrix.categorical
    older = matrix.frame.filter(pl.col("driver_age") > 40)
    assert set(older[column].to_list()) <= {"N1", "N2", "S1", "S2"}
    younger = matrix.frame.filter(pl.col("driver_age") <= 40)
    assert set(younger[column].to_list()) <= {"E1", "E2"}


@pytest.mark.req("FR-97")
def test_a_banding_cut_over_another_expression_is_refused_at_resolution() -> None:
    """`RL-1615` DP-S4-1 (a2): the pin is on the *expression*, not the slug."""
    _require_the_new_fields()
    banding = _banding("driver_age / 3")
    factor = _factor(banding_id=banding.id)
    with pytest.raises(FactorResolutionError, match="source_expression"):
        resolve_factors(_book(100), [factor], bandings={banding.id: banding})


@pytest.mark.req("FR-97")
def test_the_expression_match_is_a_normalised_parse_not_a_raw_string() -> None:
    """Two spellings that differ only in white space are one expression."""
    _require_the_new_fields()
    banding = _banding("driver_age/2")
    factor = _factor("driver_age   /   2", banding_id=banding.id)
    matrix = resolve_factors(_book(100), [factor], bandings={banding.id: banding})
    assert matrix.terms["half_age"] in matrix.frame.columns


@pytest.mark.req("FR-96")
def test_a_new_factor_version_with_a_changed_expression_cannot_pin_the_old_banding() -> None:
    """The mismatch refusal is what makes FR-101's "a Banding version per edit" enforced."""
    _require_the_new_fields()
    v1_banding = _banding(version=1)
    v2 = _factor("driver_age / 4", version=2, banding_id=v1_banding.id)
    with pytest.raises(FactorResolutionError, match="source_expression"):
        resolve_factors(_book(100), [v2], bandings={v1_banding.id: v1_banding})


@pytest.mark.req("FR-95")
def test_a_glm_on_a_banded_expression_recovers_the_steps_and_marks_a_base() -> None:
    _require_the_new_fields()
    banding = _banding()
    factor = _factor(banding_id=banding.id)
    spec = GlmSpec(
        model_family_slug="half-age",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=EXPOSURE,
        factors=(factor.id,),
    )
    result = fit_glm(_book(), spec, [factor], bandings={banding.id: banding}).result

    table = {row.level: row for row in result.relativities["half_age"]}
    assert set(table) == set(_STEP)
    base = next(level for level, row in table.items() if row.is_base)
    assert sum(row.is_base for row in table.values()) == 1
    for level, step in _STEP.items():
        assert table[level].relativity == pytest.approx(step / _STEP[base], rel=0.15)


@pytest.mark.req("FR-95")
def test_a_glm_on_a_string_expression_yields_its_relativity_table() -> None:
    _require_the_new_fields()
    expression = "where(driver_age > 40, region, alt_region)"
    factor = _factor(expression, columns=("driver_age", "region", "alt_region"))
    spec = GlmSpec(
        model_family_slug="where-region",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=EXPOSURE,
        factors=(factor.id,),
    )
    result = fit_glm(_book(), spec, [factor]).result
    table = result.relativities["half_age"]
    assert {row.level for row in table} == {"N1", "N2", "S1", "S2", "E1", "E2"}
    assert sum(row.is_base for row in table) == 1


@pytest.mark.req("FR-95")
@pytest.mark.parametrize("backend", ["xgboost", "lightgbm"])
def test_a_gbm_on_a_banded_expression_yields_its_relativity_table(backend: str) -> None:
    """FR-113's table for a GBM is its GLM approximation's (FR-133, FR-137)."""
    _require_the_new_fields()
    banding = _banding()
    factor = _factor(banding_id=banding.id)
    spec = GbmSpec(
        model_type=backend,
        model_family_slug="half-age-gbm",
        dataset_version_id=uuid4(),
        split_ref=SplitRef(split_artifact_id=uuid4()),
        response_column="claim_count",
        offset=EXPOSURE,
        objective=GbmFunctionRef(kind="builtin", name="count:poisson"),
        categorical_handling="native",
        hyperparameters={"max_depth": 3, "eta": 0.1, "num_boost_round": 40},
        early_stopping=None,
        factors=(factor.id,),
    )
    data = _book(6_000)
    bandings = {banding.id: banding}
    fit = fit_gbm(data, spec, [factor], bandings=bandings)
    assert set(fit.result.categorical_maps["half_age"]) == set(banding.labels)

    approximation = build_glm_approximation(
        fit.result, fit.booster_bytes, spec, [factor], data,
        holdout=data, source_model_id=new_uuid7(),
        source_model_slug=spec.model_family_slug, source_model_version=1,
        bandings=bandings,
    )
    table = approximation.result.relativities["half_age"]
    assert {row.level for row in table} == set(banding.labels)
    assert sum(row.is_base for row in table) == 1


@pytest.mark.req("FR-95")
def test_referenced_columns_default_is_unchanged_and_the_symbols_call_resolves() -> None:
    """`RL-1700` (a): `referenced_columns` gains an optional `symbols`; the default is as it was."""
    from pricing_core.data.expressions import GrammarProfile, referenced_columns

    assert referenced_columns("a + b * 2") == frozenset({"a", "b"})  # recipe profile
    with pytest.raises(ValueError, match="bound symbols"):
        referenced_columns("a + b", profile=GrammarProfile.FACTOR)
    assert referenced_columns(
        "where(a > 1, b, c)",
        profile=GrammarProfile.FACTOR,
        symbols=frozenset({"a", "b", "c", "d"}),
    ) == frozenset({"a", "b", "c"})
