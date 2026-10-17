"""The scalar one-row GLM predict is bit-identical to the polars path (PL-8098, FD-8097).

`model_call` scores one quote through one GLM. The frame path builds a one-row polars frame and
runs a lazy `collect` per quote (`resolve_factors`); the scalar path (`predict_glm_row`) must
return **the same `float`** — compared here as `float.hex`, so not a tolerance and not even a
`-0.0` for a `0.0` — over the demo goldens, the seed portfolio rows and one synthetic case per
factor kind, link and offset kind. Both paths must also refuse the same inputs with the same code.

The reference is the production path today: `pl.DataFrame([row])` through `predict_glm`, the
one-row frame `_GlmScorer.predict` builds, not a batch over many rows (a batch `np.exp` may use
other SIMD lanes than a shape-(1,) one, so it is not the claim being preserved).
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    AboveRangePolicy,
    Banding,
    BandingMethod,
    BandingProposal,
    BelowRangePolicy,
    Coefficient,
    Factor,
    FactorType,
    GlmFitResult,
    GlmSpec,
    Grouping,
    GroupingMethod,
    OffsetSpec,
    UnseenLevelBehaviour,
)
from pricing_core.modelling import fit_glm
from pricing_core.modelling.bandings import propose_banding
from pricing_core.modelling.errors import FactorResolutionError
from pricing_core.modelling.predict import (
    PredictionError,
    linear_predictor,
    linear_predictor_row,
    predict_glm,
    predict_glm_row,
)

DATASET = uuid4()
_REPO = Path(__file__).resolve().parents[3]
_EXAMPLES = _REPO / "examples" / "fremtpl2"


# --- the reference: the one-row frame path, exactly as `_GlmScorer.predict` runs it ------------


@dataclass(frozen=True)
class World:
    fit: GlmFitResult
    spec: GlmSpec
    factors: tuple[Factor, ...]
    bandings: Mapping[Any, Banding]
    groupings: Mapping[Any, Grouping]

    def with_spec(self, **update: Any) -> World:
        return World(
            self.fit, self.spec.model_copy(update=update), self.factors, self.bandings,
            self.groupings,
        )

    def kwargs(self) -> dict[str, Any]:
        return {"bandings": self.bandings, "groupings": self.groupings}

    def frame_eta(self, row: Mapping[str, Any], model_offset: Any = None) -> Any:
        return linear_predictor(
            self.fit, pl.DataFrame([dict(row)]), self.factors, self.spec,
            model_offset=model_offset, **self.kwargs(),
        )

    def frame(self, row: Mapping[str, Any], model_offset: Any = None) -> float:
        return float(
            predict_glm(
                self.fit, pl.DataFrame([dict(row)]), self.factors, self.spec,
                model_offset=model_offset, **self.kwargs(),
            )[0]
        )

    def scalar_eta(self, row: Mapping[str, Any], model_offset: Any = None) -> Any:
        return linear_predictor_row(
            self.fit, row, self.factors, self.spec, model_offset=model_offset, **self.kwargs()
        )

    def scalar(self, row: Mapping[str, Any], model_offset: Any = None) -> float:
        return predict_glm_row(
            self.fit, row, self.factors, self.spec, model_offset=model_offset, **self.kwargs()
        )


def _same(a: float, b: float) -> bool:
    """Bit-for-bit: `float.hex` separates `0.0` from `-0.0` and equates two NaNs."""
    return float(a).hex() == float(b).hex()


def assert_identical(world: World, row: Mapping[str, Any], model_offset: Any = None) -> None:
    expected = world.frame(row, model_offset)
    got = world.scalar(row, model_offset)
    assert _same(got, expected), f"{got.hex()} != {expected.hex()} on {dict(row)}"
    assert isinstance(got, float)
    eta_expected = world.frame_eta(row, model_offset)
    eta_got = world.scalar_eta(row, model_offset)
    assert eta_got.shape == eta_expected.shape == (1,)
    assert _same(eta_got[0], eta_expected[0])


# --- the synthetic world: every supported factor kind -----------------------------------------


def _book(n: int = 3_000, seed: int = 20261017) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 78, n).astype(float)
    veh_age = rng.integers(0, 20, n).astype(float)
    region = rng.choice(["N1", "N2", "S1", "S2"], n)
    brand = rng.choice(["B1", "B2", "B3", "B4", "B5"], n)
    fuel = rng.choice(["petrol", "diesel"], n)
    value = rng.uniform(5_000.0, 50_000.0, n)
    exposure = rng.uniform(0.3, 1.0, n)
    rate = (
        0.08 * np.where(age < 30, 1.5, 1.0) * np.where(np.isin(region, ["S1", "S2"]), 1.3, 1.0)
        * np.where(fuel == "diesel", 0.9, 1.0) * (1 + value / 200_000.0)
    )
    return pl.DataFrame(
        {
            "driver_age": age, "veh_age": veh_age, "region": region, "brand": brand,
            "fuel": fuel, "vehicle_value": value, "exposure_years": exposure,
            "claim_count": rng.poisson(rate * exposure).astype(float),
        }
    )


def _factor(slug: str, column: str | None, **over: Any) -> Factor:
    base: dict[str, Any] = {
        "id": uuid4(), "slug": slug, "dataset_id": DATASET, "version": 1,
        "type": FactorType.IDENTITY, "source_columns": (column,) if column else (),
    }
    base.update(over)
    return Factor(**base)


def _synthetic_world() -> World:
    age_banding = Banding(
        id=uuid4(), slug="age-steps", dataset_id=DATASET, version=1, column="driver_age",
        method=BandingMethod.MANUAL, boundaries=(18.0, 30.0, 45.0, 60.0, 78.0),
        labels=("18-29", "30-44", "45-59", "60+"), below_range=BelowRangePolicy.NULL_LEVEL,
        above_range=AboveRangePolicy.CLAMP_TO_LAST, null_level="unknown",
    )
    veh_banding = Banding(
        id=uuid4(), slug="veh-steps", dataset_id=DATASET, version=1, column="veh_age",
        method=BandingMethod.MANUAL, boundaries=(0.0, 3.0, 10.0, 20.0),
        labels=("new", "mid", "old"),
    )
    region_grouping = Grouping(
        id=uuid4(), slug="region-ns", dataset_id=DATASET, version=1, column="region",
        method=GroupingMethod.MANUAL,
        mapping={"N1": "NORTH", "N2": "NORTH", "S1": "SOUTH", "S2": "SOUTH"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
    )
    brand_grouping = Grouping(
        id=uuid4(), slug="brand-groups", dataset_id=DATASET, version=1, column="brand",
        method=GroupingMethod.MANUAL,
        mapping={"B1": "G1", "B2": "G1", "B3": "G2", "B4": "G2", "B5": "G3"},
        unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT, default_target_level="G3",
    )
    value = _factor("vehicle_value", "vehicle_value")  # identity, continuous
    fuel = _factor("fuel", "fuel")  # identity, categorical
    age = _factor("age_band", "driver_age", type=FactorType.BANDING, banding_id=age_banding.id)
    region = _factor(
        "region_group", "region", type=FactorType.GROUPING, grouping_id=region_grouping.id
    )
    veh = _factor("veh_band", "veh_age", type=FactorType.BANDING, banding_id=veh_banding.id)
    brand = _factor(
        "brand_group", "brand", type=FactorType.GROUPING, grouping_id=brand_grouping.id
    )
    cross = _factor(
        "age_x_region", None, type=FactorType.INTERACTION,
        operand_factor_ids=(age.id, region.id),
    )
    factors = (value, fuel, veh, brand, age, region, cross)
    spec = GlmSpec(
        model_family_slug="scalar-parity", dataset_version_id=DATASET,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=tuple(f.id for f in factors), family="poisson", link="log",
    )
    bandings = {age_banding.id: age_banding, veh_banding.id: veh_banding}
    groupings = {region_grouping.id: region_grouping, brand_grouping.id: brand_grouping}
    fit = fit_glm(_book(), spec, list(factors), bandings=bandings, groupings=groupings)
    return World(fit.result, spec, factors, bandings, groupings)


@pytest.fixture(scope="module")
def world() -> World:
    return _synthetic_world()


QUOTES: tuple[dict[str, Any], ...] = (
    {"vehicle_value": 12_345.5, "fuel": "petrol", "veh_age": 1.0, "brand": "B1",
     "driver_age": 20.0, "region": "N1", "exposure_years": 1.0},
    {"vehicle_value": 30_000.0, "fuel": "diesel", "veh_age": 7.0, "brand": "B3",
     "driver_age": 44.5, "region": "S2", "exposure_years": 0.5},
    {"vehicle_value": 8_000.25, "fuel": "diesel", "veh_age": 19.0, "brand": "B5",
     "driver_age": 77.0, "region": "N2", "exposure_years": 0.37},
    # integer inputs, as a JSON quote carries them: the frame path casts, the scalar path must too
    {"vehicle_value": 20_000, "fuel": "petrol", "veh_age": 3, "brand": "B9",
     "driver_age": 60, "region": "S1", "exposure_years": 1},
    # outside the declared band range with a clamp policy; and a null on a nullable banding
    {"vehicle_value": 20_000.0, "fuel": "petrol", "veh_age": 3.0, "brand": "B2",
     "driver_age": 90.0, "region": "S1", "exposure_years": 0.9},
    {"vehicle_value": 20_000.0, "fuel": "petrol", "veh_age": 3.0, "brand": "B2",
     "driver_age": None, "region": "S1", "exposure_years": 0.9},
)


@pytest.mark.req("FR-193")
@pytest.mark.req("FR-222")
@pytest.mark.parametrize("quote", QUOTES, ids=range(len(QUOTES)))
def test_every_factor_kind_scores_bit_identically(world: World, quote: dict[str, Any]) -> None:
    kinds = {f.type for f in world.factors}
    assert kinds == {
        FactorType.IDENTITY, FactorType.BANDING, FactorType.GROUPING, FactorType.INTERACTION
    }
    assert_identical(world, quote)


@pytest.mark.req("FR-193")
@pytest.mark.parametrize("link", ["log", "identity", "logit", "inverse"])
@pytest.mark.parametrize("offset", ["none", "column", "log_column", "model"])
def test_every_link_and_offset_kind_scores_bit_identically(
    world: World, link: str, offset: str
) -> None:
    spec_offset = {
        "none": OffsetSpec(),
        "column": OffsetSpec(kind="column", column="exposure_years"),
        "log_column": OffsetSpec(kind="log_column", column="exposure_years"),
        "model": OffsetSpec(
            kind="model", offset_model_ref="model:source@1"  # type: ignore[arg-type]
        ),
    }[offset]
    variant = world.with_spec(link=link, offset=spec_offset)
    for quote in QUOTES[:4]:
        # the `model` offset is another model's linear predictor, a shape-(1,) array
        model_offset = world.frame_eta(quote) if offset == "model" else None
        with np.errstate(all="ignore"):
            assert_identical(variant, quote, model_offset)


# --- the same refusals, with the same code -----------------------------------------------------


def _code(call: Any) -> str:
    with pytest.raises(PredictionError) as caught:
        call()
    return caught.value.code


@pytest.mark.req("FR-193")
def test_an_unresolved_term_is_refused_with_the_same_code_on_both_paths(world: World) -> None:
    def term(name: str) -> Coefficient:
        return Coefficient(
            term=name, estimate=0.5, std_error=0.1, z=5.0, p_value=0.01, ci_95=(0.3, 0.7)
        )

    ghost, bare = term("ghost[x]"), term("phantom")
    for extra in (ghost, bare):
        broken = World(
            world.fit.model_copy(update={"coefficients": (*world.fit.coefficients, extra)}),
            world.spec, world.factors, world.bandings, world.groupings,
        )
        frame_code = _code(lambda b=broken: b.frame(QUOTES[0]))
        assert frame_code == _code(lambda b=broken: b.scalar(QUOTES[0]))
        assert frame_code == "MODEL_TERM_UNRESOLVED"


@pytest.mark.req("FR-116")
def test_an_offset_failure_is_refused_with_the_same_code_on_both_paths(world: World) -> None:
    no_exposure = {k: v for k, v in QUOTES[0].items() if k != "exposure_years"}
    non_positive = {**QUOTES[0], "exposure_years": 0.0}
    for quote in (no_exposure, non_positive):
        assert _code(lambda q=quote: world.frame(q)) == "MODEL_OFFSET_MISSING"
        assert _code(lambda q=quote: world.scalar(q)) == "MODEL_OFFSET_MISSING"
    model_world = world.with_spec(
        offset=OffsetSpec(kind="model", offset_model_ref="model:source@1")  # type: ignore[arg-type]
    )
    assert _code(lambda: model_world.frame(QUOTES[0])) == "MODEL_OFFSET_MISSING"
    assert _code(lambda: model_world.scalar(QUOTES[0])) == "MODEL_OFFSET_MISSING"


@pytest.mark.req("FR-193")
def test_an_unsupported_link_is_refused_with_the_same_code_on_both_paths(world: World) -> None:
    odd = world.with_spec(link="cloglog")
    assert _code(lambda: odd.frame(QUOTES[0])) == "MODEL_LINK_UNSUPPORTED"
    assert _code(lambda: odd.scalar(QUOTES[0])) == "MODEL_LINK_UNSUPPORTED"


@pytest.mark.req("FR-87")
def test_a_factor_resolution_refusal_is_the_same_on_both_paths(world: World) -> None:
    refusals = {
        "missing source column": {k: v for k, v in QUOTES[0].items() if k != "region"},
        "unseen level, grouping says error": {**QUOTES[0], "region": "ZZ"},
    }
    for label, quote in refusals.items():
        with pytest.raises(FactorResolutionError) as frame_error:
            world.frame(quote)
        with pytest.raises(FactorResolutionError) as scalar_error:
            world.scalar(quote)
        assert str(scalar_error.value) == str(frame_error.value), label


# --- the demo model: its goldens and every seed portfolio row ----------------------------------


def _demo_modules() -> tuple[Any, Any]:
    """`examples/fremtpl2`'s `model` and `seed`, imported where its own tests import them."""
    if not (_EXAMPLES / "data" / "freMTPL2freq.arff").exists():
        pytest.skip("examples/fremtpl2/data is not fetched (sha256-pinned, gitignored)")
    sys.path.insert(0, str(_EXAMPLES))
    try:
        import model as demo_model  # type: ignore[import-not-found]
        import seed as demo_seed  # type: ignore[import-not-found]
    finally:
        sys.path.remove(str(_EXAMPLES))
    return demo_model, demo_seed


def _snake(name: str) -> str:
    import re

    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


@pytest.fixture(scope="module")
def demo() -> tuple[World, list[dict[str, Any]], list[dict[str, Any]]]:
    """The demo GLM fitted in-process (no database) on the seed portfolio, its goldens' inputs,
    and every validated portfolio row as the quote a `model_call` receives."""
    import io

    demo_model, demo_seed = _demo_modules()
    raw = pl.read_csv(io.BytesIO(demo_seed.build_portfolio_csv()), infer_schema=False)
    raw = raw.rename({c: demo_seed.RENAMES.get(_snake(c), _snake(c)) for c in raw.columns})
    casts = {"float": pl.Float64, "int": pl.Int64}
    book = raw.with_columns(
        [pl.col(c).cast(casts[t]) for c, t in demo_seed.NUMERIC.items() if c in raw.columns]
    ).filter(pl.col("exposure_years") <= demo_seed.MAX_EXPOSURE)
    assert book.height == demo_seed.PORTFOLIO_VALIDATED_ROWS

    bandings: dict[str, Any] = {}
    banding_by_id: dict[Any, Banding] = {}
    factors: list[Factor] = []
    for slug, column in (*demo_model.CONTINUOUS_FACTORS, *demo_model.CATEGORICAL_FACTORS):
        if (slug, column) in demo_model.CONTINUOUS_FACTORS:
            banding = propose_banding(
                book,
                BandingProposal(
                    dataset_version_id=uuid4(), column=column,
                    method=demo_model.BANDING_METHOD, n_bands=demo_model.BAND_COUNT,
                ),
                dataset_id=DATASET, slug=f"fremtpl2-{column.replace('_', '-')}-banding",
            )
            banding_by_id[banding.id] = banding
            bandings[slug] = demo_model.DemoBanding(banding.id, banding)
            factors.append(
                _factor(slug, column, type=FactorType.BANDING, banding_id=banding.id)
            )
        else:
            factors.append(_factor(slug, column))
    spec = GlmSpec(
        model_family_slug="fremtpl2-glm-scalar", dataset_version_id=DATASET,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=tuple(f.id for f in factors), family="poisson", link="log",
        seed=demo_model.FIT_SEED,
    )
    fit = fit_glm(book, spec, factors, bandings=banding_by_id)
    goldens = [
        {**case.inputs, "exposure_years": 1.0}
        for case in demo_model.demo_golden_cases(fit.result, bandings, 10_000)
    ]
    columns = sorted({c for f in factors for c in f.source_columns} | {"exposure_years"})
    rows = book.select(columns).to_dicts()
    return World(fit.result, spec, tuple(factors), banding_by_id, {}), goldens, rows


@pytest.mark.req("FR-193")
def test_the_demo_goldens_score_bit_identically(
    demo: tuple[World, list[dict[str, Any]], list[dict[str, Any]]],
) -> None:
    world, goldens, _ = demo
    assert len(goldens) == 3
    for golden in goldens:
        assert_identical(world, golden)


@pytest.mark.req("FR-193")
@pytest.mark.req("FR-222")
def test_every_seed_portfolio_row_scores_bit_identically(
    demo: tuple[World, list[dict[str, Any]], list[dict[str, Any]]],
) -> None:
    world, _, rows = demo
    assert len(rows) > 19_000
    mismatches = [
        row for row in rows if not _same(world.scalar(row), world.frame(row))
    ]
    assert not mismatches, f"{len(mismatches)} rows differ, first {mismatches[0]}"


# --- the refusals of a factor kind the resolver does not resolve ------------------------------


@pytest.mark.req("FR-208")
@pytest.mark.parametrize(
    "kind",
    [FactorType.SPLINE, FactorType.POLYNOMIAL, FactorType.OFFSET, FactorType.EXPRESSION],
)
def test_a_factor_kind_the_resolver_refuses_is_refused_identically_on_both_paths(
    world: World, kind: FactorType
) -> None:
    """The scalar path has no factor logic of its own: it reads `resolve_factor_columns`, so
    every kind is covered or refused exactly as the frame path does, with no per-scorer choice
    to make at bundle load (PL-8098 constraint 5, met by construction)."""
    try:
        odd = _factor("odd", "vehicle_value", type=kind)
    except ValueError:
        pytest.skip(f"the Factor shape refuses a bare {kind.value!r} before any resolver sees it")
    variant = World(
        world.fit, world.spec, (odd,), world.bandings, world.groupings
    )
    with pytest.raises(FactorResolutionError) as frame_error:
        variant.frame(QUOTES[0])
    with pytest.raises(FactorResolutionError) as scalar_error:
        variant.scalar(QUOTES[0])
    assert str(scalar_error.value) == str(frame_error.value)


# --- the wiring: `_GlmScorer.predict` is the scalar path ---------------------------------------


def _scorer(world: World, offset_source: Any = None) -> Any:
    from pricing_core.rating.runtime import _GlmScorer

    columns = {f.slug: f.source_columns[0] for f in world.factors if len(f.source_columns) == 1}
    return _GlmScorer(
        world.fit, world.spec, world.factors, world.bandings, world.groupings, columns,
        offset_source,
    )


def _no_frame_resolution(*_: Any, **__: Any) -> Any:
    raise AssertionError("resolve_factors was called: the frame path ran")


@pytest.mark.req("FR-222")
@pytest.mark.req("FR-193")
def test_a_model_call_scores_without_the_frame_resolution(
    world: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With `resolve_factors` patched to raise, the scorer still scores — and the frame path,
    run beside it, is the one that trips the patch."""
    from pricing_core.modelling import predict as predict_module

    scorer = _scorer(world)
    expected = [world.frame(quote) for quote in QUOTES]
    monkeypatch.setattr(predict_module, "resolve_factors", _no_frame_resolution)

    assert [scorer.predict(quote) for quote in QUOTES] == expected
    with pytest.raises(AssertionError, match="frame path ran"):
        world.frame(QUOTES[0])


@pytest.mark.req("FR-116")
def test_a_model_offset_scorer_scores_without_the_frame_resolution(
    world: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pricing_core.modelling import predict as predict_module

    residual = world.with_spec(
        offset=OffsetSpec(kind="model", offset_model_ref="model:source@1")  # type: ignore[arg-type]
    )
    scorer = _scorer(residual, offset_source=_scorer(world))
    expected = [residual.frame(quote, world.frame_eta(quote)) for quote in QUOTES[:4]]
    monkeypatch.setattr(predict_module, "resolve_factors", _no_frame_resolution)

    assert [scorer.predict(quote) for quote in QUOTES[:4]] == expected


@pytest.mark.req("FR-222")
def test_the_scorer_keeps_its_renames_and_its_collision_refusal(world: World) -> None:
    """`feature_map` names (a Factor slug) reach the source column; two names for one column
    with different values are still `MODEL_CALL_FEATURE_COLLISION`."""
    scorer = _scorer(world)
    by_slug = {
        "age_band": QUOTES[1]["driver_age"], "region_group": QUOTES[1]["region"],
        "veh_band": QUOTES[1]["veh_age"], "brand_group": QUOTES[1]["brand"],
        "vehicle_value": QUOTES[1]["vehicle_value"], "fuel": QUOTES[1]["fuel"],
        "exposure_years": QUOTES[1]["exposure_years"],
    }
    assert _same(scorer.predict(by_slug), world.frame(QUOTES[1]))
    clash = {**by_slug, "driver_age": QUOTES[1]["driver_age"] + 1.0}
    assert _code(lambda: scorer.predict(clash)) == "MODEL_CALL_FEATURE_COLLISION"


# --- diagnostic: ms/quote on both paths (asserts nothing about time) ---------------------------


def print_timing(world: World, rows: list[dict[str, Any]], label: str) -> None:
    """Print ms/quote for the frame path and the scalar path over `rows`, with the tree and
    the box. A figure to read, never an assertion: this box is shared and a time assert on it
    is a flake (FD-8097's 16.9 ms was a loaded-box sample, 2.0 ms on main)."""
    import os
    import subprocess
    import time

    def per_quote(call: Any) -> float:
        start = time.perf_counter()
        for row in rows:
            call(row)
        return (time.perf_counter() - start) / len(rows) * 1e3

    tree = subprocess.run(
        ["git", "-C", str(_REPO), "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    frame_ms = per_quote(world.frame)
    scalar_ms = per_quote(world.scalar)
    print(
        f"\nGLM_PREDICT_TIMING {label}: head={tree} nproc={os.cpu_count()} "
        f"load1={os.getloadavg()[0]:.2f} polars_max_threads={os.environ.get('POLARS_MAX_THREADS')}"
        f" quotes={len(rows)} frame_ms_per_quote={frame_ms:.4f} "
        f"scalar_ms_per_quote={scalar_ms:.4f} ratio={frame_ms / scalar_ms:.1f}x"
    )


@pytest.mark.req("NFR-489")
def test_print_the_per_quote_cost_of_both_paths(
    world: World,
    demo: tuple[World, list[dict[str, Any]], list[dict[str, Any]]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    with capsys.disabled():
        print_timing(world, list(QUOTES[:4]) * 250, "synthetic")
        print_timing(demo[0], demo[2], "seed-portfolio")


@pytest.mark.req("FR-104")
def test_a_grouping_maps_one_value_exactly_as_it_maps_a_column(world: World) -> None:
    """`apply_grouping` reads a single value without a lazy `collect` (FD-8097) and a column
    through `unique` + `replace_strict`; both come from `_targets`, and this holds them equal —
    the mapped level, the fallback for an unseen level, and the refusal text."""
    from pricing_core.modelling.groupings import apply_grouping

    def outcome(series: pl.Series, grouping: Grouping) -> tuple[str, Any]:
        try:
            return "level", apply_grouping(series, grouping)[0]
        except FactorResolutionError as error:
            return "refusal", str(error)

    for grouping in world.groupings.values():
        for value in ("N1", "S2", "B1", "B5", "B9", "ZZ", "1", "1.5"):
            single, column = pl.Series("v", [value]), pl.Series("v", [value, value])
            assert outcome(single, grouping) == outcome(column, grouping)


@pytest.mark.req("FR-104")
def test_apply_grouping_reproduces_every_recorded_expectation_of_c62f1ff6() -> None:
    """The batch path is unchanged by the single-value branch: 1 443 inputs (seed 20261017, three
    unseen-level behaviours, 0/1/2/5 values of strings, ints, floats, bool and null) with the
    outputs and refusal texts `groupings.py` gave at `c62f1ff6` (the base of SL-8099), stored as
    data, not as a copied module. Captured once with
    `packages/pricing-core/tests/data/make_apply_grouping_fixture.py` (its docstring has the
    command)."""
    import json

    from pricing_core.modelling.groupings import apply_grouping

    fixture = json.loads(
        (Path(__file__).parent / "data" / "apply_grouping_c62f1ff6.json").read_text()
    )
    groupings = [
        Grouping(
            id=uuid4(), slug="g", dataset_id=DATASET, version=1, column="c",
            method=GroupingMethod.MANUAL, mapping=fixture["mapping"],
            unseen_level_behaviour=UnseenLevelBehaviour(spec["behaviour"]),
            default_target_level=spec["default"],
        )
        for spec in fixture["groupings"]
    ]
    assert len(fixture["cases"]) == 1_443
    for case in fixture["cases"]:
        series = pl.Series("col", case["values"], dtype=None if case["values"] else pl.String)
        try:
            got: dict[str, Any] = {
                "levels": apply_grouping(series, groupings[case["grouping"]]).to_list()
            }
        except FactorResolutionError as error:
            got = {"refusal": [type(error).__name__, str(error)]}
        assert got == case["expected"], case
