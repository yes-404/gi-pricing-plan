"""The freMTPL2 demo's rating algorithm builder (PL-1525, WK-1178 exit-demo slice (a)).

`examples/fremtpl2/algorithm.py` builds the algorithm the seed saves and slice (b)'s journey
reuses. These tests are pure: no database, no Job. The band expression is the one part of the
algorithm the engine does not already own (the engine has no banding step, `runtime.py`), so
it is checked against `apply_banding` itself on every edge.
"""

from __future__ import annotations

import importlib.util
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
import zen

from model_schema import (
    AboveRangePolicy,
    ArtifactRef,
    Banding,
    BandingMethod,
    BelowRangePolicy,
)
from model_schema.rating import RatingAlgorithm
from pricing_core.modelling.bandings import apply_banding

_SPEC = importlib.util.spec_from_file_location(
    "demo_algorithm",
    Path(__file__).resolve().parents[2] / "examples" / "fremtpl2" / "algorithm.py",
)
assert _SPEC is not None
assert _SPEC.loader is not None
demo_algorithm = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(demo_algorithm)

_DATASET = UUID("00000000-0000-0000-0000-0000000000d5")


def _banding(
    column: str,
    boundaries: tuple[float, ...],
    labels: tuple[str, ...],
    *,
    closed: str = "left",
    below: BelowRangePolicy = BelowRangePolicy.ERROR,
    above: AboveRangePolicy = AboveRangePolicy.ERROR,
    null_level: str | None = None,
) -> Banding:
    return Banding(
        id=UUID("00000000-0000-0000-0000-0000000000b1"),
        slug=f"{column}-banding",
        dataset_id=_DATASET,
        version=1,
        column=column,
        method=BandingMethod.MANUAL,
        boundaries=boundaries,
        closed=closed,  # type: ignore[arg-type]
        labels=labels,
        below_range=below,
        above_range=above,
        null_level=null_level,
    )


def _evaluate(expression: str, column: str, value: float) -> Any:
    return zen.evaluate_expression(expression, {column: value})


@pytest.mark.req("FR-97")
@pytest.mark.parametrize("closed", ["left", "right"])
def test_band_expression_maps_each_edge(closed: str) -> None:
    """Just below, at and just above every boundary, the generated ternary gives the label
    `apply_banding` gives. The engine has no banding step, so this is the proof that the
    algorithm's band step and the model's band assignment are one function."""
    import polars as pl

    banding = _banding(
        "driv_age", (18.0, 25.0, 40.0, 60.0, 99.0), ("18-24", "25-39", "40-59", "60+"),
        closed=closed,
    )
    expression = demo_algorithm.band_expression("driv_age", banding)
    values = [
        value
        for boundary in banding.boundaries
        for value in (boundary - 0.5, boundary, boundary + 0.5)
        if banding.boundaries[0] <= value <= banding.boundaries[-1]
    ]
    expected = apply_banding(pl.Series("driv_age", values), banding).to_list()
    got = [_evaluate(expression, "driv_age", value) for value in values]
    assert got == expected


@pytest.mark.req("FR-97")
def test_band_expression_follows_the_declared_out_of_range_policies() -> None:
    """Under `error` the algorithm's input contract refuses the value first, so the chain is
    never asked; `null_level` sends the value to the declared level, as `apply_banding` does."""
    banding = _banding(
        "veh_age", (0.0, 5.0, 10.0), ("new", "old"),
        below=BelowRangePolicy.NULL_LEVEL, above=AboveRangePolicy.NULL_LEVEL,
        null_level="other",
    )
    expression = demo_algorithm.band_expression("veh_age", banding)
    assert _evaluate(expression, "veh_age", -1) == "other"
    assert _evaluate(expression, "veh_age", 11) == "other"
    assert _evaluate(expression, "veh_age", 10) == "old"
    assert _evaluate(expression, "veh_age", 0) == "new"


@pytest.mark.req("FR-97")
def test_band_expression_refuses_a_label_it_cannot_quote() -> None:
    banding = _banding("veh_age", (0.0, 5.0, 10.0), ("it's", "old"))
    with pytest.raises(ValueError, match="label"):
        demo_algorithm.band_expression("veh_age", banding)


def test_base_premium_is_exp_intercept_times_mean_claim_cost_to_whole_minor_units() -> None:
    """DP-a2: `exp(intercept) x mean claim cost`, in Decimal, half-even to a whole minor unit."""
    got = demo_algorithm.base_premium_minor(Decimal("0"), Decimal("197600.5"))
    assert got == 197600  # 197600.5 -> half-even -> the even neighbour
    assert isinstance(got, int)
    assert demo_algorithm.base_premium_minor(Decimal("-3"), Decimal("200000")) == int(
        (Decimal("-3").exp() * Decimal(200000)).quantize(Decimal(1))
    )


def _fixture_algorithm() -> dict[str, Any]:
    bandings = {
        "driv_age_band": _banding(
            "driv_age", (18.0, 25.0, 99.0), ("18-24", "25+")
        ),
    }
    tables = {
        "driv_age_band": ArtifactRef(type="rate_table", slug="fremtpl2-driv-age-band", version=1),
        "veh_gas": ArtifactRef(type="rate_table", slug="fremtpl2-veh-gas", version=1),
    }
    return demo_algorithm.build_fremtpl2_algorithm(
        tables=tables,
        bandings=bandings,
        base_minor=25000,
        domains={"veh_gas": ["Diesel", "Regular"]},
    )


@pytest.mark.req("FR-213")
def test_the_built_algorithm_validates() -> None:
    """The builder returns a dict that `RatingAlgorithm` accepts, with one input per raw
    column (a banded factor's input is its source column, not the factor) plus `bonus_malus`,
    the base step and one output."""
    payload = _fixture_algorithm()
    algorithm = RatingAlgorithm.model_validate(payload)
    assert algorithm.slug == demo_algorithm.FREMTPL2_ALGORITHM_SLUG
    inputs = {field.name: field for field in algorithm.input_contract}
    # The eighth input, `bonus_malus`, is a rating-table input and no step consumes it.
    assert set(inputs) == {"driv_age", "veh_gas", "bonus_malus"}
    assert not any("bonus_malus" in str(step.consumes) for step in algorithm.steps)
    assert inputs["driv_age"].type == "int"
    assert (inputs["driv_age"].min, inputs["driv_age"].max) == (18, 99)
    assert inputs["veh_gas"].domain == ["Diesel", "Regular"]
    step_types = [step.type for step in algorithm.steps]
    assert step_types.count("output") == 1
    base = next(step for step in algorithm.steps if step.step_id == "s_base")
    assert base.note is not None
    assert "a simplification (frequency GLM × mean severity; no severity model)" in base.note


@pytest.mark.req("FR-226")
def test_the_demo_algorithm_declares_no_decimal_output() -> None:
    """`PL-1371` §7, `RL-1343` §4: until the RL-1343 fix merges every declared output is
    `money_minor`. Removed by the slice that merges that fix."""
    algorithm = RatingAlgorithm.model_validate(_fixture_algorithm())
    assert [output.type for output in algorithm.outputs] == ["money_minor"]
    assert [output.name for output in algorithm.outputs] == ["payable_premium_minor"]


# ---------------------------------------------------------------------------------------------
# FR-246's reads rule on the built algorithm (PL-1525 Acceptance 4 and 7; FD-1374's guard)
# ---------------------------------------------------------------------------------------------

_BANDED = {
    "driv_age_band": _banding("driv_age", (18.0, 25.0, 40.0, 99.0), ("18-24", "25-39", "40+")),
    "veh_age_band": _banding("veh_age", (0.0, 3.0, 10.0, 30.0), ("0-2", "3-9", "10+")),
    "veh_power_band": _banding("veh_power", (4.0, 6.0, 8.0, 15.0), ("4-5", "6-7", "8+")),
}
_DOMAINS = {
    "veh_brand": ["B1", "B2"],
    "veh_gas": ["Diesel", "Regular"],
    "area": ["A", "B"],
    "region": ["R11", "R24"],
}
_FACTORS = ("driv_age_band", "veh_age_band", "veh_power_band", "veh_brand", "veh_gas", "area",
            "region")


def _full_algorithm() -> dict[str, Any]:
    """The seven-Factor algorithm the seed builds, over fixed refs, bandings and domains."""
    tables = {
        factor: ArtifactRef(
            type="rate_table", slug=f"fremtpl2-{factor.replace('_', '-')}", version=1
        )
        for factor in _FACTORS
    }
    return demo_algorithm.build_fremtpl2_algorithm(
        tables=tables, bandings=_BANDED, base_minor=25000, domains=_DOMAINS
    )


def _reads(step: dict[str, Any]) -> frozenset[str]:
    """What a step reads: `referenced_names` (the shipped extractor, `PL-1520` Task 1A) on the
    step with its declaration removed. It returns `consumes` plus the reads, so the
    declaration is dropped first to leave the reads alone."""
    from pricing_core.rating.references import referenced_names

    return referenced_names({key: value for key, value in step.items() if key != "consumes"})


def _undeclared_reads(algorithm: dict[str, Any]) -> dict[str, frozenset[str]]:
    found: dict[str, frozenset[str]] = {}
    for step in algorithm["steps"]:
        extra = _reads(step) - set(
            [step["consumes"]] if isinstance(step.get("consumes"), str)
            else step.get("consumes", [])
        )
        if extra:
            found[step["step_id"]] = extra
    return found


def _edges(algorithm: dict[str, Any], *, by: str) -> set[tuple[str, str]]:
    """(producing step, reading step) pairs, with the names read taken from `consumes` or from
    the step's read set."""
    produced_by = {
        name: step["step_id"]
        for step in algorithm["steps"]
        for name in ([step["produces"]] if isinstance(step.get("produces"), str)
                     else step.get("produces", []))
    }
    edges = set()
    for step in algorithm["steps"]:
        names = _reads(step) if by == "reads" else set(step.get("consumes", []))
        edges |= {(produced_by[name], step["step_id"]) for name in names}
    return edges


@pytest.mark.req("FR-246")
def test_the_demo_algorithm_reads_only_what_it_declares() -> None:
    """Every step's reads are inside its declared `consumes` (0 undeclared reads), and so the
    graph built from the reads has no edge the graph built from `consumes` lacks
    (0 added edges, hence 0 added cycles once the algorithm compiles as a DAG)."""
    algorithm = _full_algorithm()
    RatingAlgorithm.model_validate(algorithm)
    for step in algorithm["steps"]:
        print(step["step_id"], sorted(_reads(step)))
    assert _undeclared_reads(algorithm) == {}
    # An `output` step reads nothing the engine evaluates and only declares its `consumes`, so
    # the claim is "no edge the reads add", not equality.
    assert _edges(algorithm, by="reads") - _edges(algorithm, by="consumes") == set()


@pytest.mark.req("FR-246")
def test_a_predicate_that_agrees_with_itself_is_not_the_oracle() -> None:
    """The independence condition: three steps' reads are written out by hand here, so a wrong
    extractor cannot pass by agreeing with itself."""
    steps = {step["step_id"]: step for step in _full_algorithm()["steps"]}
    assert _reads(steps["s_premium"]) == {
        "base_premium_minor", "rel_driv_age_band", "rel_veh_age_band", "rel_veh_power_band",
        "rel_veh_brand", "rel_veh_gas", "rel_area", "rel_region",
    }
    assert _reads(steps["s_band_driv_age_band"]) == {"driv_age"}
    assert _reads(steps["s_t_veh_gas"]) == {"veh_gas"}
    assert _reads(steps["s_base"]) == frozenset()


@pytest.mark.req("FR-246")
def test_the_reads_check_refuses_an_undeclared_read() -> None:
    """Broken input: one name dropped from one step's `consumes` is exactly one undeclared read,
    naming that step and that name."""
    algorithm = _full_algorithm()
    premium = next(step for step in algorithm["steps"] if step["step_id"] == "s_premium")
    premium["consumes"] = [name for name in premium["consumes"] if name != "rel_veh_gas"]
    assert _undeclared_reads(algorithm) == {"s_premium": frozenset({"rel_veh_gas"})}


# -- the extractor against the engine (PL-1520 Spike S1 step 1; the ruling's condition) ---------

_RAW = (
    {"driv_age": 20, "veh_age": 1, "veh_power": 5, "veh_brand": "B1", "veh_gas": "Diesel",
     "area": "A", "region": "R11", "bonus_malus": 50},
    {"driv_age": 30, "veh_age": 5, "veh_power": 7, "veh_brand": "B2", "veh_gas": "Regular",
     "area": "B", "region": "R24", "bonus_malus": 100},
    {"driv_age": 60, "veh_age": 12, "veh_power": 10, "veh_brand": "B1", "veh_gas": "Regular",
     "area": "A", "region": "R24", "bonus_malus": 230},
)


def _produced(index: int) -> dict[str, Any]:
    """One fixed non-null value, of the declared type, for every produced name."""
    out: dict[str, Any] = {factor: _BANDED[factor].labels[index % 3] for factor in _BANDED}
    out.update({f"rel_{factor}": 1.0 + (i + 1) / 10 + index / 100
                for i, factor in enumerate(_FACTORS)})
    out.update({"base_premium_minor": 25000, "premium_unrounded": 31234.5})
    return out


def _contexts() -> list[dict[str, Any]]:
    """The three raw contexts with the produced names, and one context per band of every banded
    step (a value inside that band), so every ternary branch is evaluated."""
    contexts = [{**raw, **_produced(i), "zz_unused": 7} for i, raw in enumerate(_RAW)]
    for banding in _BANDED.values():
        for low, high in zip(banding.boundaries, banding.boundaries[1:], strict=False):
            contexts.append({**_RAW[0], **_produced(0), "zz_unused": 7,
                             banding.column: int((low + high) // 2)})
    return contexts


def _engine_reads(text: str, context: dict[str, Any]) -> set[str]:
    """The names the engine reads in `text` under `context`: removing one raises or changes the
    result. (A missing name can evaluate to `null` without an error, so "no error" alone is not
    "not read".)"""
    full = zen.evaluate_expression(text, context)
    read = set()
    for name in context:
        cut = {key: value for key, value in context.items() if key != name}
        try:
            changed = zen.evaluate_expression(text, cut) != full
        except RuntimeError:
            changed = True
        if changed:
            read.add(name)
    return read


def _extractor_vs_engine(
    text: str, reference_set: frozenset[str], contexts: list[dict[str, Any]]
) -> list[tuple[str, str, str]]:
    """Failures as (string, name, kind). `outside`: the engine reads a name the extractor does
    not report. `unread`: the extractor reports a name the engine reads under no context."""
    engine: set[str] = set()
    failures = []
    for context in contexts:
        read = _engine_reads(text, context)
        engine |= read
        failures += [(text, name, "engine reads outside the set")
                     for name in sorted(read - reference_set)]
    failures += [(text, name, "extractor claims a read the engine does not make")
                 for name in sorted(reference_set - engine)]
    return list(dict.fromkeys(failures))


def _extractor_set(field: str, text: str) -> frozenset[str]:
    from pricing_core.rating.references import referenced_names

    base = field.split("[")[0].split(".")[0]
    node: dict[str, Any] = {"key_expr": [text]} if base == "key_expr" else {base: text}
    return referenced_names(node)


@pytest.mark.req("FR-246")
def test_the_reads_extractor_agrees_with_the_engine() -> None:
    """For every string `authored_expression_fields` returns, the shipped extractor's reference
    set equals what `zen.evaluate_expression` reads (both computed, then compared)."""
    from pricing_core.rating.authored import authored_expression_fields

    algorithm = RatingAlgorithm.model_validate(_full_algorithm())
    contexts = _contexts()
    strings = authored_expression_fields(algorithm)
    assert strings
    for authored in strings:
        reference = _extractor_set(authored.field, authored.text)
        failures = _extractor_vs_engine(authored.text, reference, contexts)
        print(authored.step_id, authored.field, sorted(reference), failures)
        assert failures == []


@pytest.mark.req("FR-246")
def test_the_cross_check_refuses_a_planted_mismatch() -> None:
    """Red on a planted mismatch, in both directions, on one real string of the algorithm."""
    from pricing_core.rating.authored import authored_expression_fields

    algorithm = RatingAlgorithm.model_validate(_full_algorithm())
    text = next(a.text for a in authored_expression_fields(algorithm) if a.step_id == "s_premium")
    truth = _extractor_set("expr", text)
    contexts = _contexts()
    under = _extractor_vs_engine(text, truth - {"rel_area"}, contexts)
    assert under == [(text, "rel_area", "engine reads outside the set")]
    over = _extractor_vs_engine(text, truth | {"zz_unused"}, contexts)
    assert over == [(text, "zz_unused", "extractor claims a read the engine does not make")]
