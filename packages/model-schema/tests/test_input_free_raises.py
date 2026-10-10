"""Every model-schema raise path renders authored text in a 422, and no authored text carries
an input value (NFR-499; FD-1589 row 8, remedy (c); PL-1599 acceptance (i) and (ii)).

`pricing_core.safe_error.safe_validation_message` keeps an `InputFreeError`'s text and nothing
else a validator raises, so (i) every `ValueError`-family raise here is an `InputFreeError`, and
(ii) every such raise passes a literal, or an f-string over upper-case module constants alone.
A value may enter a marker raise only as a DP-8 (b) keyword: `identifier(<expr>, PATTERN)`,
`PATTERN` an upper-case module constant.
"""

from __future__ import annotations

import ast
import builtins
import importlib
import re
from collections import Counter
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src" / "model_schema"
_CONST = re.compile(r"_?[A-Z][A-Z0-9_]*")

_Site = tuple[str, str, int]

#: Plain raises still to rewrite, by (file, "Class.function"): an EXACT count. A slice that
#: rewrites one decrements it; a new plain raise fails. Holds only sites no request body
#: reaches (PL-1599 Appendix A: B1 and B2, carried to P3). Emptied and deleted by the last slice.
_RESIDUAL: dict[tuple[str, str], int] = {
    ("approvals.py", "ApprovalRequest._recorded_matches_decisions"): 1,
    ("backtests.py", "BacktestSummary._a_backtest_is_not_run_on_the_data_it_learned_on"): 1,
    ("backtests.py", "BacktestSummary._the_period_is_ordered"): 1,
    ("comparison.py", "ComparisonMetric._an_unordered_metric_has_no_leader"): 1,
    ("comparison.py", "ComparisonMetric._the_leader_is_one_of_the_models_measured"): 1,
    ("comparison.py", "ComparisonSummary._every_reference_belongs_to_this_comparison"): 5,
    ("comparison.py", "DoubleLift._a_model_is_not_its_own_challenger"): 1,
    ("datasets.py", "DatasetSplit._a_split_has_at_least_two_parts"): 1,
    ("diagnostics.py", "AeCell._the_interval_is_ordered"): 1,
    ("diagnostics.py", "CrossValidationDiagnostics._every_fold_is_represented_at_the_selected_alpha"): 1,  # noqa: E501
    ("diagnostics.py", "CrossValidationDiagnostics._the_selected_alpha_is_a_point_on_the_path"): 1,
    ("diagnostics.py", "QuantileCrossing._the_two_numbers_describe_the_same_comparison"): 2,
    ("dislocation.py", "DislocationRun._quantile_keys_are_the_fixed_set"): 1,
    ("jobs.py", "JobResult._reference_required_unless_none"): 1,
    ("metrics.py", "CustomMetric._applicability_is_within_the_template"): 1,
    ("metrics.py", "CustomMetric._the_parameters_are_the_templates_own"): 2,
    ("modelling.py", "Coefficient._the_interval_contains_the_estimate"): 1,
    ("modelling.py", "EbmFitResult._every_term_names_existing_features"): 2,
    ("modelling.py", "EbmFitResult._the_base_slot_is_never_a_real_bin"): 1,
    ("modelling.py", "EbmFitResult._the_lookup_shapes_match_the_bins"): 5,
    ("modelling.py", "Factor._columns_match_the_type"): 2,
    ("modelling.py", "Factor._reasons_accompany_their_flags"): 2,
    ("modelling.py", "Factor._the_interaction_arm"): 4,
    ("modelling.py", "Factor._the_type_and_its_transformation_agree"): 2,
    ("modelling.py", "GbmFitResult._a_dropped_metric_is_named_once"): 1,
    ("modelling.py", "GbmFitResult._every_feature_declares_its_dtype"): 1,
    ("modelling.py", "Model._a_fitted_model_has_a_fit"): 1,
    ("modelling.py", "Model._a_fitted_model_has_its_diagnostics"): 1,
    ("modelling.py", "Model._the_fit_matches_the_specification"): 1,
    ("modelling.py", "SpecValidation._ok_means_no_problems"): 1,
    ("modelling.py", "TweediePowerFit._the_estimate_is_the_curves_argmax_and_the_interval_brackets_it"): 3,  # noqa: E501
    ("objectives.py", "CustomObjective._a_status_past_draft_rests_on_a_certificate"): 1,
    ("objectives.py", "CustomObjective._applicability_is_within_the_template"): 1,
    ("objectives.py", "CustomObjective._each_field_belongs_to_one_arm"): 6,
    ("objectives.py", "CustomObjective._the_parameters_are_the_templates_own"): 2,
    ("objectives.py", "TemplateParameter.check"): 4,
    ("perils.py", "PerilStructure._coherent"): 3,
    ("perils.py", "Reconciliation._coherent"): 1,
    ("prediction.py", "PredictedRow._the_bounds_are_a_pair_and_ordered"): 2,
    ("prediction.py", "Prediction._every_row_matches_the_declared_uncertainty"): 1,
    ("prediction.py", "Uncertainty._the_kind_and_its_evidence_agree"): 8,
    ("rating.py", "RatingAlgorithm._graph_invariants"): 5,
    ("regression.py", "RegressionSuiteContent._unique_names"): 1,
    ("sub_graphs.py", "SubGraphBody._graph_invariants"): 5,
    ("sub_graphs.py", "_topological_order"): 1,
    ("validation.py", "RuleSetEntry._an_override_may_only_raise"): 1,
    ("validation.py", "ValidationRule._catalogue_id_names_a_catalogue_entry"): 1,
}


def _input_free(arg: ast.expr) -> bool:
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return True
    if isinstance(arg, ast.JoinedStr):
        names = {
            n.id
            for v in arg.values
            if isinstance(v, ast.FormattedValue)
            for n in ast.walk(v.value)
            if isinstance(n, ast.Name)
        }
        return all(_CONST.fullmatch(name) for name in names)
    return False


def _identifier_keyword(value: ast.expr) -> bool:
    """A DP-8 (b) keyword: `identifier(<expr>, PATTERN)`, the pattern an upper-case constant."""
    return (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id == "identifier"
        and len(value.args) == 2
        and isinstance(value.args[1], ast.Name)
        and bool(_CONST.fullmatch(value.args[1].id))
    )


def _census(
    source: str, namespace: dict[str, object], filename: str
) -> tuple[list[_Site], list[_Site]]:
    """(plain, interpolating): the raises that would render generic text, and the marker raises
    that pass something other than a literal."""
    from model_schema.input_free import InputFreeError

    plain: list[_Site] = []
    interpolating: list[_Site] = []

    def resolve(name: str) -> object:
        return namespace.get(name, getattr(builtins, name, None))

    def visit(node: ast.AST, scope: list[str]) -> None:
        for child in ast.iter_child_nodes(node):
            inner = (
                [*scope, child.name]
                if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                else scope
            )
            where = (filename, ".".join(inner[-2:]) or "<module>", getattr(child, "lineno", 0))
            if isinstance(child, ast.Assert):
                plain.append(where)
            if (
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id == "PydanticCustomError"
            ):
                plain.append(where)
            if isinstance(child, ast.Raise) and child.exc is not None:
                exc = child.exc
                call = exc if isinstance(exc, ast.Call) else None
                target = call.func if call is not None else exc
                if isinstance(target, ast.Name):
                    cls = resolve(target.id)
                    if isinstance(cls, type) and issubclass(cls, ValueError):
                        if not issubclass(cls, InputFreeError):
                            plain.append(where)
                        elif call is None or not (
                            len(call.args) == 1
                            and _input_free(call.args[0])
                            and all(_identifier_keyword(k.value) for k in call.keywords)
                        ):
                            interpolating.append(where)
            visit(child, inner)

    visit(ast.parse(source), [])
    return plain, interpolating


def _all() -> tuple[list[_Site], list[_Site]]:
    plain: list[_Site] = []
    interpolating: list[_Site] = []
    for path in sorted(_SRC.glob("*.py")):
        if path.name == "input_free.py":
            continue  # the marker's own refusal is a plain, literal ValueError by design
        name = "model_schema" if path.stem == "__init__" else f"model_schema.{path.stem}"
        module = importlib.import_module(name)
        p, i = _census(path.read_text(), vars(module), path.name)
        plain += p
        interpolating += i
    return plain, interpolating


@pytest.mark.req("NFR-499")
def test_no_marker_raise_interpolates_a_value() -> None:  # acceptance (ii)
    _, interpolating = _all()
    assert not interpolating, (
        "an InputFreeError takes a literal message (or identifier(value, PATTERN)): "
        f"{interpolating}"
    )


@pytest.mark.req("NFR-499")
def test_every_raise_path_renders_authored_text_in_a_422() -> None:  # acceptance (i)
    plain, _ = _all()
    counts = Counter((f, where) for f, where, _ in plain)
    residual = Counter(_RESIDUAL)
    assert counts == residual, (
        "raise InputFreeError with input-free text (a plain ValueError, an assert or a "
        "PydanticCustomError renders generic text in a 422); rewritten sites leave _RESIDUAL: "
        f"{sorted((counts - residual).items())} new, {sorted((residual - counts).items())} stale"
    )


@pytest.mark.req("NFR-499")
def test_the_census_reports_planted_violations() -> None:
    from model_schema.input_free import InputFreeError, identifier

    planted = (
        "def f(value):\n"
        "    raise ValueError('a literal message')\n"
        "    raise InputFreeError(f'bad {value}')\n"
        "    raise InputFreeError(f'ok {_LIMIT}')\n"
        "    assert value\n"
        "    raise InputFreeError('step {step}', step=identifier(value, _STEP_ID))\n"
        "    raise InputFreeError('step {step}', step=identifier(value, '^x$'))\n"
        "    raise InputFreeError('step {step}', step=value)\n"
        "    raise ValueError\n"
    )
    plain, interpolating = _census(
        planted, {"InputFreeError": InputFreeError, "identifier": identifier}, "planted.py"
    )
    assert [line for *_, line in plain] == [2, 5, 9]
    assert [line for *_, line in interpolating] == [3, 7, 8]
