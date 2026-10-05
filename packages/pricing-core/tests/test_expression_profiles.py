"""02 §4.6's four profiles (RL-1184 E2; FR-144's 2026-09-28 amendment; FR-145; FR-36).

Each strict refusal has a positive control: the same string accepted by `recipe`. That
proves the refusal comes from the profile, and not from CPython's parser or a missing
translation.
"""

from __future__ import annotations

from uuid import uuid4

import polars as pl
import pytest

from model_schema import Severity, ValidationLayer, ValidationRule
from pricing_core.data import expressions as expr_module
from pricing_core.data.expressions import (
    ExpressionError,
    GrammarProfile,
    compile_expression,
    parse_expression,
)
from pricing_core.data.prepare import apply_recipe
from pricing_core.data.validate import CHECKS, ValidationContext

OBJECTIVE_SYMBOLS = frozenset({"y", "f", "w"})
FACTOR_SYMBOLS = frozenset({"y", "f", "w"})  # stands in for declared columns
FRAME = pl.DataFrame({"y": [0.5, 2.0, 5.0], "f": [0.0, 1.0, -1.0], "w": [1.0, 1.0, 2.0]})
STRICT = [
    (GrammarProfile.OBJECTIVE, OBJECTIVE_SYMBOLS),
    (GrammarProfile.FACTOR, FACTOR_SYMBOLS),
]


def _values(expression: str, profile: GrammarProfile = GrammarProfile.RECIPE) -> list[object]:
    return FRAME.select(compile_expression(expression, profile=profile)).to_series().to_list()


# -- where() and the four new functions, in recipe and check (they only add) ---------------


@pytest.mark.req("FR-36")
@pytest.mark.parametrize("profile", [GrammarProfile.RECIPE, GrammarProfile.CHECK])
def test_where_and_the_new_functions_compute(profile: GrammarProfile) -> None:
    assert _values("where(y > 1, 1, 0)", profile) == [0, 1, 1]
    assert _values("clip(y, 1, 3)", profile) == [1.0, 2.0, 3.0]
    assert _values("log1p(f)", profile)[0] == pytest.approx(0.0)
    assert _values("expm1(f)", profile)[0] == pytest.approx(0.0)


# -- the strict profiles' refusals, each with its recipe control ---------------------------


@pytest.mark.req("FR-144")
@pytest.mark.req("FR-145")
@pytest.mark.parametrize(("profile", "symbols"), STRICT)
@pytest.mark.parametrize(
    ("expression", "names"),
    [
        ("y > f", "comparison"),
        ("y % 2", "Mod"),
        ("y if f > 0 else w", "IfExp"),
        ("y > 0 and f > 0", "BoolOp"),
        ("not y", "Not"),
        ("+y", "UAdd"),
        ("floor(y)", "not an allowed function"),
        ("y + 'a'", "numeric"),
        ("where(y, f, w)", "one comparison"),
        ("where(y > 0 and f > 0, 1, 2)", "BoolOp"),
        ("where(y > f, 1)", "exactly 3"),
        ("y + z", "'z'"),
    ],
)
def test_a_strict_profile_refuses(
    profile: GrammarProfile, symbols: frozenset[str], expression: str, names: str
) -> None:
    with pytest.raises(ExpressionError, match=names) as excinfo:
        parse_expression(expression, profile, symbols=symbols)
    assert excinfo.value.lineno == 1  # NFR-483: every refusal carries a position


@pytest.mark.req("FR-36")
@pytest.mark.parametrize(
    "expression",
    ["y > f", "y % 2", "y if f > 0 else w", "y > 0 and f > 0", "not y", "+y", "floor(y)"],
)
def test_recipe_accepts_what_the_strict_profiles_refuse(expression: str) -> None:
    """The positive control. These are today's grammar, and `recipe` only adds."""
    parse_expression(expression, GrammarProfile.RECIPE)


@pytest.mark.req("NFR-483")
def test_an_unknown_symbol_is_refused_at_its_own_position() -> None:
    with pytest.raises(ExpressionError) as excinfo:
        parse_expression("y + z", GrammarProfile.OBJECTIVE, symbols=OBJECTIVE_SYMBOLS)
    assert (excinfo.value.col_offset, excinfo.value.end_col_offset) == (4, 5)


@pytest.mark.req("FR-145")
@pytest.mark.parametrize(("profile", "symbols"), STRICT)
def test_the_strict_grammar_accepts_the_spec_example(
    profile: GrammarProfile, symbols: frozenset[str]
) -> None:
    loss = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
    parse_expression(loss, profile, symbols=symbols | {"w_under", "w_over"})


def test_a_strict_profile_needs_its_symbols() -> None:
    with pytest.raises(ValueError, match="symbols"):
        parse_expression("y", GrammarProfile.OBJECTIVE)


def test_the_objective_profile_does_not_compile_to_polars() -> None:
    with pytest.raises(ValueError, match="to_sympy"):
        compile_expression("y", profile=GrammarProfile.OBJECTIVE, symbols=OBJECTIVE_SYMBOLS)


# -- exact arity, in every profile (RL-1292, DP-S1-2 (b)) --------------------------

LEGACY = ["abs", "round", "floor", "ceil", "log", "exp", "sqrt"]
STRICT_LEGACY = ["abs", "log", "exp", "sqrt"]  # the four the strict profiles admit
LENIENT = [GrammarProfile.RECIPE, GrammarProfile.CHECK]
EVERY = [(p, None) for p in LENIENT] + STRICT


def _admitted(profile: GrammarProfile) -> list[str]:
    return LEGACY if profile in LENIENT else STRICT_LEGACY


@pytest.mark.req("FR-36")
@pytest.mark.req("FR-145")
@pytest.mark.parametrize(("profile", "symbols"), EVERY)
def test_a_legacy_function_given_two_arguments_is_refused(
    profile: GrammarProfile, symbols: frozenset[str] | None
) -> None:
    """Red first: at fb90d381 every one of these compiles and silently drops the second
    argument (premise c). RL-1292 makes each an ExpressionError with a position."""
    for name in _admitted(profile):
        with pytest.raises(ExpressionError, match=rf"{name}\(\) takes exactly 1 argument") as e:
            parse_expression(f"{name}(y, f)", profile, symbols=symbols)
        assert (e.value.lineno, e.value.col_offset) == (1, 0)


@pytest.mark.req("FR-36")
@pytest.mark.parametrize("expression", ["abs(y, f)", "round(y, 2)", "log(y, 10)"])
def test_the_ruling_s_named_cases_are_refused_in_recipe(expression: str) -> None:
    """The three expressions RL-1292's proof names. At fb90d381, `round(y, 2)`
    rounds to 0 decimals and `log(y, 10)` is the natural log."""
    with pytest.raises(ExpressionError, match="takes exactly 1 argument"):
        compile_expression(expression)


@pytest.mark.req("FR-36")
@pytest.mark.parametrize(("profile", "symbols"), EVERY)
def test_a_legacy_function_with_one_argument_is_still_accepted(
    profile: GrammarProfile, symbols: frozenset[str] | None
) -> None:
    """The positive control: the refusal is of the extra argument, not of the function.
    `min`, `max` and `coalesce` keep "at least one", so several arguments stay valid."""
    for name in _admitted(profile):
        parse_expression(f"{name}(y)", profile, symbols=symbols)
    parse_expression("min(y, f, w) + max(y, f)", profile, symbols=symbols)
    if profile in LENIENT:
        parse_expression("coalesce(y, f, w)", profile, symbols=symbols)


# -- FD-1294: the refusal reaches all three callers (Acceptance 12) -------


def _round_check(expr: str) -> ValidationRule:
    return ValidationRule(
        id=uuid4(), slug="rounded", version=1, layer=ValidationLayer.ACTUARIAL_SANITY,
        check="expression", severity=Severity.FAIL, target={"table": "t"},
        params={"expr": expr},
    )


@pytest.mark.req("FR-36")
def test_round_with_two_arguments_is_refused_through_the_callers_derive_expression() -> None:
    """Red first: at fb90d381 this step succeeds and rounds to 0 decimals."""
    with pytest.raises(ExpressionError, match=r"round\(\) takes exactly 1 argument") as e:
        apply_recipe(
            {"t": FRAME},
            [{"step": "derive_expression", "params": {"column": "z", "expression": "round(y, 2)"}}],
        )
    assert (e.value.lineno, e.value.col_offset) == (1, 0)


@pytest.mark.req("FR-36")
def test_round_with_two_arguments_is_refused_through_the_callers_filter_rows() -> None:
    """Red first: at fb90d381 this filter succeeds on the silently rounded value."""
    with pytest.raises(ExpressionError, match=r"round\(\) takes exactly 1 argument") as e:
        apply_recipe(
            {"t": FRAME}, [{"step": "filter_rows", "params": {"expression": "round(y, 2) > 1"}}]
        )
    assert (e.value.lineno, e.value.col_offset) == (1, 0)


@pytest.mark.req("FR-50")
def test_round_with_two_arguments_is_refused_through_the_callers_expression_check() -> None:
    """Red first: at fb90d381 the check runs and reports on the silently rounded value."""
    with pytest.raises(ExpressionError, match=r"round\(\) takes exactly 1 argument") as e:
        CHECKS["expression"](
            _round_check("round(y, 2) > 1"),
            {"t": FRAME},
            ValidationContext(reference_tables={}, reference_frames={}),
        )
    assert (e.value.lineno, e.value.col_offset) == (1, 0)


# -- the call sites pass their profiles (Acceptance 7) --------------------------------------


def _spy(monkeypatch: pytest.MonkeyPatch, target: object) -> list[GrammarProfile]:
    seen: list[GrammarProfile] = []
    real = expr_module.compile_expression

    def spy(expression: str, **kwargs: object) -> pl.Expr:
        seen.append(kwargs["profile"])  # type: ignore[arg-type]
        return real(expression, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(target, "compile_expression", spy)
    return seen


@pytest.mark.req("FR-36")
def test_call_site_derive_expression_and_filter_rows_pass_recipe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import pricing_core.data.prepare as prepare

    seen = _spy(monkeypatch, prepare)
    apply_recipe(
        {"t": FRAME},
        [
            {"step": "derive_expression", "params": {"column": "z", "expression": "y * 2"}},
            {"step": "filter_rows", "params": {"expression": "y > 1"}},
        ],
    )
    assert seen == [GrammarProfile.RECIPE, GrammarProfile.RECIPE]


@pytest.mark.req("FR-50")
def test_call_site_expression_check_passes_check(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = _spy(monkeypatch, expr_module)  # validate imports it lazily, at call time
    rule = ValidationRule(
        id=uuid4(), slug="y-positive", version=1, layer=ValidationLayer.ACTUARIAL_SANITY,
        check="expression", severity=Severity.FAIL, target={"table": "t"},
        params={"expr": "where(y > 1, 1, 0) == 1"},
    )
    outcome = CHECKS["expression"](rule, {"t": FRAME}, ValidationContext(
        reference_tables={}, reference_frames={}))
    assert seen == [GrammarProfile.CHECK]
    assert outcome.violating_rows == 1  # y = 0.5 is the one row the predicate rejects
