"""Every place a failure's text is stored or logged on a quote-input path goes through the
allow-list (NFR-499, RL-917), and a coverage guard keeps it that way.

`pricing_core.safe_error` / `app.platform.safe_exception` keep an exception's text only where it
is ours and input-free. That holds only while every **sink** uses them. This file enumerates the
sinks by AST, over the files a quote input can reach (the scoring route, the job runner, the
batch handler, the request middleware, the outbox, and `pricing_core.rating`), and fails when one
is added, moved or removed without a matching line in `_SINKS` saying what covers it.

A sink is: a logging call passed `exc_info`, a `.exception(` call, a `JobError(` construction, an
assignment to `last_error`, a use of an exception's text (`str(exc)`, `{exc}`, `repr(exc)`,
`{exc!r}`, `exc.args`), a bound exception passed bare as an argument of a logging call (the
logger formats it with `%s`), and a dict entry `error_message`.
"""

from __future__ import annotations

import ast
import logging
from collections import Counter
from pathlib import Path

import polars as pl
import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError, field_validator

from model_schema import BandingMethod, BandingProposal
from model_schema.input_free import InputFreeError
from pricing_core.data.expressions import ExpressionError
from pricing_core.modelling import BandingError, propose_banding
from pricing_core.safe_error import CodedError, safe_error_detail

_ROOT = Path(__file__).resolve().parents[2]
#: The scope is DERIVED by glob, so a new file is covered by default (maintainer, 2026-09-29,
#: Q889-a, widened by Q889-c to all of `app`): a list of files omitted four handlers and the
#: guard passed a leak added to one.
_GLOBS = (
    "backend/src/app/**/*.py",
    "packages/pricing-core/src/pricing_core/**/*.py",
)
#: Files the globs match and the census leaves out, each with why. A file not listed here is in.
#: Empty on purpose: every file under the two globbed trees is counted, and a sink in one that is
#: not a quote-input path is listed in `_SINKS` with why, so a new one is still seen.
_EXCLUDED: dict[str, str] = {}
#: Handlers a list once omitted; the census test asserts each is in the derived set.
_MUST_BE_IN_SCOPE = (
    "backend/src/app/worker/rating_handlers.py",
    "backend/src/app/worker/model_handlers.py",
    "backend/src/app/worker/data_handlers.py",
    "backend/src/app/worker/rate_table_handlers.py",
)

_SENTINEL = "SENTINEL-quote-input-d7e3c518"

#: (file, function, kind) -> (how many, what covers it).
_SINKS: dict[tuple[str, str, str], tuple[int, str]] = {
    ("backend/src/app/errors.py", "_handle_serialization_error", "str(exc)"): (
        1, "a substring classifier only: nothing stored, logged or echoed; "
        "test_decimal_write_bound.py:56 asserts the value is not in the response "
        "(maintainer's ruling, to-lead 2026-11-06 07:42:30 GMT, RED 1)"),
    ("backend/src/app/api/score.py", "_as_platform_error", "str(exc)"): (
        1, "reached only for a `CodedError` (by class, not text shape): the message has its value "
        "dropped at source: test_quote_input_raise_sites.py "
        "and test_score.py::test_a_422_for_a_bad_input_names_the_field_and_carries_no_value"),
    ("backend/src/app/api/score.py", "_maybe_sample_trace", "exc_info"): (
        1, "test_score.py::test_a_trace_sampling_failure_logs_no_quote_input"),
    ("backend/src/app/api/score.py", "_shadow_task", "exc_info"): (
        1, "test_shadow_log_sanitised.py::test_a_shadow_decision_failure_logs_no_quote_input"),
    ("backend/src/app/api/score.py", "_shadow_score", "exc_info"): (
        1, "test_shadow_log_sanitised.py::test_a_shadow_scoring_failure_logs_no_quote_input"),
    ("backend/src/app/platform/deployment_switch.py", "_listen", "exception"): (
        1, "`.exception(` writes the traceback to the log and echoes nothing into a response; "
        "the Redis SwitchMessage consumer, whose payload is deploy-time ids, not quote input "
        "(maintainer's ruling, 2026-10-19 02:45:42 BST, item 1 (a))"),
    ("backend/src/app/platform/deployment_switch.py", "handle", "exception"): (
        1, "`.exception(` writes the traceback to the log and echoes nothing into a response; "
        "PREPARE hydration of an approved deployment's artifacts (`hydrate_for_switch` reads "
        "only the Rating Version row, the blob row and the blob store), not request input "
        "(maintainer's ruling, 2026-10-19 02:45:42 BST, item 1 (b))"),
    ("backend/src/app/platform/deployment_switch.py", "_run", "exception"): (
        1, "logs the traceback of the reconcile loop, which runs on Redis deploy-time ids and "
        "never sees quote input; the _listen row's reasoning (2026-10-19 02:45:42 BST item 1 "
        "(a)/(b)) extended (maintainer's ruling, 2026-11-04 03:09:02 GMT (a))"),
    ("backend/src/app/platform/deployment_switch.py", "ensure", "exc_info"): (
        1, "logs the traceback of the listener restart, which runs on Redis deploy-time ids and "
        "never sees quote input; the _listen row's reasoning (2026-10-19 02:45:42 BST item 1 "
        "(a)/(b)) extended (maintainer's ruling, 2026-11-04 03:09:02 GMT (a))"),
    ("backend/src/app/platform/deployment_switch.py", "ensure", "exception"): (
        1, "not a log sink: asyncio Task.exception() on the listener task, counted by the "
        "census's name walker (maintainer's ruling, 2026-11-04 03:09:02 GMT (a); the walker "
        "fix is a process-backlog row, WK-1178 tooling after the freeze)"),
    ("backend/src/app/platform/deployments.py", "complete_switch", "exception"): (
        1, "`.exception(` writes the traceback to the log and echoes nothing into a response; "
        "the deploy route's COMMIT round, not a quote input "
        "(maintainer's ruling, 2026-10-19 02:45:42 BST, item 1 (c))"),
    ("backend/src/app/observability/middleware.py", "dispatch", "exc_info"): (
        1, "this file: test_an_unexpected_request_failure_logs_no_input"),
    ("backend/src/app/platform/outbox.py", "relay_once", "last_error"): (
        1, "test_outbox.py::test_a_publish_failure_stores_only_the_exception_type"),
    ("backend/src/app/worker/tasks.py", "execute_job", "JobError"): (
        4, "budget and named-refusal messages are our own text; the generic clause is "
        "test_job_error_sanitiser.py"),
    ("backend/src/app/worker/tasks.py", "execute_job", "exc_info"): (
        2, "test_job_error_sanitiser.py (the generic and the named-refusal clause)"),
    ("backend/src/app/worker/tasks.py", "execute_job", "str(exc)"): (
        1, "JobBudgetExceededError's own message: elapsed time and the budget, no input"),
    ("backend/src/app/auth/oidc.py", "verify", "{exc}"): (
        1, "PyJWT's `InvalidTokenError` text for a rejected bearer token; the token is a "
        "credential, not a quote input"),
    ("backend/src/app/data/ingestion.py", "correct_schema", "str(exc)"): (
        1, "`RecipeError`: names a column and a cast; upload path, Dataset Version data, not"
        " a quote"),
    ("backend/src/app/data/ingestion.py", "ingest_upload", "str(exc)"): (
        1, "`ColumnNameCollisionError`: names two column headers; upload path, not a quote"),
    ("backend/src/app/data/ingestion.py", "ingest_upload", "{exc}"): (
        1, "`RecipeError`: names a column and a cast; upload path, not a quote"),
    ("backend/src/app/platform/modelling.py", "resolve_offset_model", "str(exc)"): (
        1, "`FactorResolutionError`: names a factor and a dataset version; model path"),
    ("backend/src/app/platform/objectives.py", "derive_objective", "str(exc)"): (
        2, "`ExpressionError` on an author's own loss text, as the problem detail and its "
        "`loss` field error; a custom objective's declaration error (FR-145), no Quote Context"),
    ("backend/src/app/platform/prediction.py", "_unscoreable", "str(exc)"): (
        1, "`ModellingError`/`PredictionError`: named refusal of a model prediction; a "
        "Fitted Model scored on caller rows, synchronous, returned to the caller who sent"
        " them and not stored or logged"),
    ("backend/src/app/platform/rate_tables.py", "_map_operation_error", "str(exc)"): (
        1, "the coded branch only: splits `CODE: detail` off a pricing-core operation's refusal "
        "(a residual for a library `FOO_BAR: value` is recorded on #1712, row 3 Q1 (a)); the "
        "fallback goes through `safe_error_detail` "
        "(test_validation_error_sinks.py, FD-1589 rows 2 and 3, NFR-499)"),
    ("backend/src/app/platform/rate_tables.py", "_portfolio_weights", "str(exc)"): (
        1, "FEEDS the text of a `PortfolioFrameError`, `WeightJoinError` or "
        "`FactorResolutionError` to the failure of the `rate_table.diff_cells` Job (stored as the "
        "Job's error message; the weights are computed in the Job) and to the legacy `diff`'s "
        "422 body. The input is a portfolio Dataset Version, not a Quote Context. "
        "`WeightJoinError` names the key, the column or the ref and never a value "
        "(test_rate_table_weights.py::test_a_refusal_never_carries_a_portfolio_value; "
        "test_rate_table_diff_portfolio.py::"
        "test_a_portfolio_refusal_that_reads_the_content_is_the_jobs_validation_failed); a "
        "`FactorResolutionError`'s message is carried with its count and example value by "
        "RL-1361 item 3 and RL-1418 T5 "
        "(test_rate_table_diff_portfolio.py::"
        "test_a_resolution_error_reaches_the_failed_job_with_its_count_and_example)"),
    ("packages/pricing-core/src/pricing_core/rating/compile.py", "compile_bundle",
     "str(exc)"): (
        1, "FR-223 MODEL_REFERENCE_MODE_INCONSISTENT at compile: caught BY CLASS "
        "(`ModelReferenceModeError`), whose text is authored from the step id and the two "
        "declared modes; no quote is involved; any other `ValueError` falls through uncoded "
        "(test_rating_compile_bundle.py::"
        "test_a_foreign_value_error_is_not_given_the_mode_code)"),
    ("packages/pricing-core/src/pricing_core/rate_tables/weights.py", "_resolved_series",
     "str(exc)"): (
        1, "re-wraps a `FactorResolutionError` as a `WeightJoinError` with its message kept, as "
        "RL-1418 T5 and RL-1361 item 3 rule (the count and the example value); the input is a "
        "portfolio Dataset Version, not a Quote Context; the message reaches the Job's failure "
        "(test_rate_table_diff_portfolio.py::"
        "test_a_resolution_error_reaches_the_failed_job_with_its_count_and_example)"),
    ("backend/src/app/platform/rating_versions.py", "create_rating_version", "str(exc)"): (
        1, "create time: caught BY CLASS (`ModelReferenceModeError`), an artifact-level refusal "
        "(FR-223 MODEL_REFERENCE_MODE_INCONSISTENT) naming the step and the two declared modes; "
        "no quote is involved; any other `ValueError` goes through `safe_error_detail` "
        "(test_validation_error_sinks.py, FD-1589 row 7)"),
    ("backend/src/app/platform/regression_suites.py", "_validate_properties", "{exc}"): (
        1, "VERDICT (Q889-c): cannot carry a quote-input value. `UnsweepableProperty`'s text"
        " (`properties.py`, five raises) interpolates only `check.input`, "
        "`field.type.value`, `field.name`, and the `lower`/`upper` bounds, all declared "
        "by the suite's author or the input contract; the swept values are generated "
        "later, never in this text. Save-time, at declaration, before any quote-derived "
        "run"),
    ("backend/src/app/platform/settings.py", "coerce", "{exc}"): (
        1, "a workspace setting's type error; not a quote input"),
    ("backend/src/app/platform/transformations.py", "_refuse", "str(exc)"): (
        1, "a dataset transformation's named refusal; Dataset Version path"),
    ("backend/src/app/platform/validation_rules.py", "create_rule", "str(exc)"): (
        1, "a validation-rule catalogue lookup miss; Dataset Version path"),
    ("backend/src/app/api/demo.py", "get_guide", "{exc}"): (
        1, "the demo guide's own missing-source message: a path, no quote or dataset value"),
    ("backend/src/app/worker/data_handlers.py", "_materialise_split", "str(exc)"): (
        1, "`SplitError`, pricing-core's own message about a split definition; Dataset Version "
        "path, not a Quote Context"),
    ("backend/src/app/worker/model_handlers.py", "_compare", "str(exc)"): (
        1, "`ModellingError`: pricing-core's named modelling refusal; model path, not a quote"),
    ("backend/src/app/worker/model_handlers.py", "_fit", "str(exc)"): (
        2, "`EbmFitError`/`GbmFitError`/`GlmFitError`: named fit refusals; model path. And "
        "`NonFiniteDerivativeError`/`RoundBudgetExceededError` (FR-165): a fit job on a Dataset "
        "Version, never a quote input; the text names the round, the objective ref and a row "
        "count or timings, and the offending y/f range is kept out of it (FD-1219, "
        "DP-S2-4); pinned by pricing-core's test_objectives.py::"
        "test_nonfinite_aborts_an_expression_naming_the_round_and_no_value"),
    ("backend/src/app/worker/model_handlers.py", "_fit", "{exc}"): (
        1, "`FactorResolutionError`: names a factor and a dataset version; model path"),
    ("backend/src/app/worker/model_handlers.py", "_reconcile", "str(exc)"): (
        2, "`ModellingError`/`PredictionError`: named refusals of a peril reconciliation; model "
        "path, not a quote"),
    ("backend/src/app/worker/rating_handlers.py", "_rating_regression", "str(exc)"): (
        1, "`UnsweepableProperty`, a named refusal whose message names no quote input; every "
        "other exception propagates to `execute_job`'s one generic clause "
        "(test_regression_runs.py::test_a_validation_error_inside_a_run_never_puts_a_quote_input_in_the_job_error_or_the_logs)"),
    ("packages/pricing-core/src/pricing_core/data/validate.py", "_reject_unless_single_select",
     "{exc}"): (
        1, "a dataset validation rule's own SQL parse error; Dataset Version path, not a quote"),
    ("packages/pricing-core/src/pricing_core/data/validate.py", "_run_one", "{exc}"): (
        1, "a dataset validation rule's failure text; Dataset Version path, not a quote"),
    ("packages/pricing-core/src/pricing_core/data/validate.py", "_sql", "{exc}"): (
        1, "a dataset validation rule's DuckDB error; Dataset Version path, not a quote"),
    ("packages/pricing-core/src/pricing_core/modelling/ebm.py", "fit_ebm", "{exc}"): (
        1, "`interpret`'s refusal of a fit; model path, not a quote"),
    ("packages/pricing-core/src/pricing_core/modelling/glm.py", "decode_covariance", "{exc}"): (
        1, "a stored covariance blob's decode error; model path, not a quote"),
    ("packages/pricing-core/src/pricing_core/modelling/glm.py", "fit_glm", "{exc}"): (
        1, "`glum`'s refusal of a fit; model path, not a quote"),
    ("packages/pricing-core/src/pricing_core/safe_error.py", "safe_error_detail", "str(exc)"): (
        1, "the allow-list itself: reached only for a `CodedError`, whose text is input-free"),
    ("packages/pricing-core/src/pricing_core/safe_error.py", "_expression_detail", "str(exc)"): (
        1, "the allow-list itself: an `ExpressionError`'s text, raised where no frame is in scope "
        "(test_every_expression_error_is_raised_where_no_row_value_is_in_scope)"),
    ("packages/pricing-core/src/pricing_core/safe_error.py", "_expression_detail", "{exc}"): (
        1, "the allow-list itself: the same text with its position (as above)"),
    ("packages/pricing-core/src/pricing_core/rating/score.py", "_failing_node", "str(exc)"): (
        1, "reads only the engine error's JSON `nodeId`; the text is neither stored nor logged, "
        "and only a matched step's own id reaches the raised message: "
        "test_rating_score.py::test_an_engine_error_text_never_reaches_the_raised_message"),
    ("packages/pricing-core/src/pricing_core/rating/score.py", "_batch_error_row",
     "error_message key"): (
        1, "the one place a batch `\"error\"` row is written (FR-255), fed only by "
        "`_batch_error_code`'s safe text: it was `_score_batch_row`'s second sink until FD-1561's "
        "row escape (PL-1565 Task 1) wrote the row from two `except` clauses; "
        "test_rating_score_batch_outputs.py::test_an_error_row_from_serialisation_carries_no_value "
        "(SENTINEL-9513 not in error_message); widened by from-lead 2026-10-11 21:57:43 BST"),
    ("packages/pricing-core/src/pricing_core/rating/score.py", "_score_batch_row",
     "error_message key"): (
        1, "test_scoring_handlers.py and test_quote_input_raise_sites.py (the success row's "
        "None; the error row moved to `_batch_error_row`)"),
    # FD-1507: six sites that bind the exception to a name other than exc/e/err. Each verdict is
    # read from the raise sites of the exception it handles: none can hold a quote input.
    ("backend/src/app/platform/deployments.py", "_prepare", "{exc}"): (
        1, "a `SwitchIncompleteError`, raised only by `deployment_switch.prepare_round` with the "
        "process ids that did not acknowledge: no quote input reaches the switch"),
    ("backend/src/app/platform/rating_algorithms.py", "_accepted_feature_map_values",
     "str(exc)"): (
        1, "the `CodedError` of `refuse_control_in_features` over a stored model artifact (WK-2113 "
        "S3, B2): fixed texts naming a model ref, a feature, a Factor slug@version and an "
        "interaction, or a fit-result field; split at the code and returned in a 422 at save, "
        "where no quote exists (NFR-499)"),
    ("backend/src/app/platform/bundle_hydration.py", "_load_guard_refusal", "str(exc)"): (
        1, "the `CodedError` of `load_bundle` / `check_rateable_intent`, split at its code and "
        "kept only for a code in `LOAD_GUARD_CODES` (`CONTROL_FACTOR_IN_RATEABLE_PATH`, "
        "`MODEL_TERM_UNRESOLVED`): the text names a model ref, a feature, a Factor slug@version, "
        "an interaction and a term, all from stored artifacts, never a quote input; it reaches "
        "the 409 detail and the audit `after` (WK-2113 S3, #1741, NFR-499); "
        "test_bundle_hydration.py::test_every_load_guard_code_is_a_409_and_one_audit_event"),
    ("packages/pricing-core/src/pricing_core/rating/runtime.py", "_glm_scorer", "{exc}"): (
        1, "a `PredictionError` from `check_term_domains` at hydrate, re-raised as a `CodedError` "
        "naming the code, the Bundle ref and the term and Factor slug: read at load from the "
        "artifact, once per hydrate, no row exists (#1741, FR-193, FR-243); "
        "test_rating_glm_model_call.py::"
        "test_a_bundle_whose_glm_term_its_banding_cannot_produce_is_refused_at_load"),
    ("packages/pricing-core/src/pricing_core/modelling/gbm.py", "_compile_custom", "str(exc)"): (
        1, "an `ObjectiveError` from compiling a Custom Objective's declared source: the "
        "objective's own text, no quote exists at compile"),
    ("packages/pricing-core/src/pricing_core/modelling/objectives.py", "_smoke_fit_check",
     "{exc}"): (
        1, "a smoke fit over `_smoke_data`'s seeded synthetic rows: the detail names the "
        "exception type and text of a fit on generated data, never a dataset row"),
    ("packages/pricing-core/src/pricing_core/rating/compile.py", "_consumed_features", "{exc}"): (
        1, "a `ValueError` from `consumed_features` of a pinned model's fit result, at compile "
        "(same texts as rating_algorithms.py): no quote exists at compile"),
    ("packages/pricing-core/src/pricing_core/rating/runtime.py", "handler", "str(exc)"): (
        1, "a `_ModelCallRefusal`, raised only at `_predict_model`'s last line, with the step id "
        "(authored in the graph) and the model_type (from the artifact); read first, A6: the "
        "refusal text carries no feature value and no quote input (NFR-499)"),
}


def _files() -> list[Path]:
    derived = {p for pattern in _GLOBS for p in _ROOT.glob(pattern) if "__pycache__" not in p.parts}
    return sorted(p for p in derived if p.relative_to(_ROOT).as_posix() not in _EXCLUDED)


#: The methods of a logger that format their arguments into a record. `exception` is counted
#: by its own kind above.
_LOGGING_METHODS = frozenset(
    {"debug", "info", "warning", "warn", "error", "critical", "fatal", "log"}
)


def _sinks(source: str, name: str) -> Counter[tuple[str, str, str]]:
    """Count the failure sinks of one file.

    An exception is recognised by what it is (FD-1507): a name bound by an enclosing
    `except ... as`, or a parameter named `exc`. Not by the spelling of a variable: `e` as a band
    edge is not one, and a handler that binds `problem` or `refusal` is.
    """
    found: Counter[tuple[str, str, str]] = Counter()

    def visit(node: ast.AST, function: str, excs: frozenset[str]) -> None:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            function = node.name
            parameters = (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
            if any(parameter.arg == "exc" for parameter in parameters):
                excs |= {"exc"}
        if isinstance(node, ast.ExceptHandler) and node.name:
            excs |= {node.name}
        if isinstance(node, ast.Call):
            callee = node.func
            called = (
                callee.attr if isinstance(callee, ast.Attribute)
                else callee.id if isinstance(callee, ast.Name) else ""
            )
            if called == "exception":
                found[(name, function, "exception")] += 1
            if any(keyword.arg == "exc_info" for keyword in node.keywords):
                found[(name, function, "exc_info")] += 1
            if called == "JobError":
                found[(name, function, "JobError")] += 1
            # FD-2029: a bound exception handed to a logging call as an argument is formatted
            # into the record, so its text is logged exactly as `str(exc)` would log it.
            if called in _LOGGING_METHODS and isinstance(callee, ast.Attribute):
                # `exc_info=` has its own kind above; any other keyword value counts here.
                keyword_values = (k.value for k in node.keywords if k.arg != "exc_info")
                for argument in (*node.args, *keyword_values):
                    if isinstance(argument, ast.Name) and argument.id in excs:
                        found[(name, function, "bare exc in logging call")] += 1
            if (
                called == "repr" and node.args and isinstance(node.args[0], ast.Name)
                and node.args[0].id in excs
            ):
                found[(name, function, "repr(exc)")] += 1
            if (
                called == "str" and node.args and isinstance(node.args[0], ast.Name)
                and node.args[0].id in excs
            ):
                found[(name, function, "str(exc)")] += 1
        if (
            isinstance(node, ast.FormattedValue) and isinstance(node.value, ast.Name)
            and node.value.id in excs
        ):
            found[(name, function, "{exc}")] += 1
            if node.conversion == ord("r"):  # `{exc!r}`: the repr carries the text too
                found[(name, function, "repr(exc)")] += 1
        if (
            isinstance(node, ast.Attribute) and node.attr == "args"
            and isinstance(node.value, ast.Name) and node.value.id in excs
        ):
            found[(name, function, "exc.args")] += 1
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and target.attr == "last_error":
                    found[(name, function, "last_error")] += 1
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and key.value == "error_message":
                    found[(name, function, "error_message key")] += 1
        for child in ast.iter_child_nodes(node):
            visit(child, function, excs)

    visit(ast.parse(source), "<module>", frozenset())
    return found


def _census() -> dict[tuple[str, str, str], int]:
    total: Counter[tuple[str, str, str]] = Counter()
    for path in _files():
        total += _sinks(path.read_text(encoding="utf-8"), path.relative_to(_ROOT).as_posix())
    return dict(total)


def _handler(body: str) -> str:
    return f"try:\n    f()\nexcept ValueError as problem:\n    {body}\n"


_PLANTED = {
    "bare exc in logging call": _handler("log.warning(problem)"),
    "repr(exc)": _handler("x = repr(problem)"),
    "repr(exc) f-string": _handler("x = f'{problem!r}'"),
    "exc.args": _handler("x = problem.args"),
}


@pytest.mark.parametrize(
    ("snippet", "kind"),
    [
        ("bare exc in logging call", "bare exc in logging call"),
        ("repr(exc)", "repr(exc)"),
        ("repr(exc) f-string", "repr(exc)"),
        ("exc.args", "exc.args"),
    ],
)
def test_the_census_finds_each_planted_sink_shape(snippet: str, kind: str) -> None:
    """FD-2029: red on deliberately broken input. Each shape, planted, is counted under its
    kind; the same shapes over a name that is no exception are not."""
    assert _sinks(_PLANTED[snippet], "planted.py")[("planted.py", "<module>", kind)] == 1
    control = _PLANTED[snippet].replace("except ValueError as problem", "except ValueError")
    assert not _sinks(control.replace("problem", "band"), "planted.py")


@pytest.mark.req("NFR-499")
def test_every_failure_sink_on_a_quote_input_path_is_accounted_for() -> None:
    assert _census() == {key: count for key, (count, _) in _SINKS.items()}, (
        "a sink that stores or logs an exception's text was added, moved or removed: bring it "
        "under app.platform.safe_exception / pricing_core.safe_error, give it a sentinel test, "
        "and list it in _SINKS"
    )


#: Every call, in the census's files, that fills a Job error's location (#1917, `07` §4.1): a call
#: with a `location=` keyword, or a `JobErrorLocation(` construction. (file, function) -> where the
#: values come from. The model bounds a location's free-text keys and refuses control characters,
#: but no rule can tell a submitted value from an identifier, so each raise site that fills one is
#: listed with the artifact field its values are read from, and a new one fails until it is.
_LOCATION_SITES: dict[tuple[str, str], str] = {
    ("backend/src/app/worker/tasks.py", "execute_job"): (
        "copies `exc.location`, the location `PlatformError` built from its own mapping and "
        "checked (`app.errors._build_location`): nothing is composed here"
    ),
}


def _composes_text(value: ast.AST) -> bool:
    """Whether an expression builds text from parts: an f-string, `+` or `%` on operands,
    `.format(` or `.join(`. A value filled from a name or an attribute is not composed."""
    for node in ast.walk(value):
        if isinstance(node, ast.JoinedStr):
            return True
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add | ast.Mod):
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"format", "join"}
        ):
            return True
    return False


def _location_sites(source: str, name: str) -> tuple[set[tuple[str, str]], list[str]]:
    """The (file, function) of each call that fills a location, and `file:line` of each whose
    `location=` value composes text."""
    sites: set[tuple[str, str]] = set()
    composed: list[str] = []

    def visit(node: ast.AST, function: str) -> None:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            function = node.name
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "JobErrorLocation":
                sites.add((name, function))
            for keyword in node.keywords:
                if keyword.arg == "location":
                    sites.add((name, function))
                    if _composes_text(keyword.value):
                        composed.append(f"{name}:{node.lineno}")
        for child in ast.iter_child_nodes(node):
            visit(child, function)

    visit(ast.parse(source), "<module>")
    return sites, composed


def _location_problems(
    sites: set[tuple[str, str]], composed: list[str], registered: dict[tuple[str, str], str]
) -> list[str]:
    return [
        *(f"unregistered: {file} {function}" for file, function in sorted(sites - set(registered))),
        *(f"stale entry: {file} {function}" for file, function in sorted(set(registered) - sites)),
        *(f"composed text: {where}" for where in composed),
    ]


@pytest.mark.req("NFR-499")
def test_every_raise_site_that_fills_a_location_is_accounted_for() -> None:
    """A location holds identifiers of the caller's own artifact and never a submitted value. This
    cannot prove that: it makes every site that fills one visible and reasoned, as `_SINKS` does,
    and refuses a value built by composing text (which is where submitted text would get in)."""
    sites: set[tuple[str, str]] = set()
    composed: list[str] = []
    for path in _files():
        name = path.relative_to(_ROOT).as_posix()
        found, text = _location_sites(path.read_text(encoding="utf-8"), name)
        sites |= found
        composed += text
    assert _location_problems(sites, composed, _LOCATION_SITES) == [], (
        "a raise site fills a Job error's location without being listed in _LOCATION_SITES with "
        "where its values come from, or a listed site is gone, or a value is composed text"
    )


_PLANTED_LOCATIONS = {
    "a new raise site": (
        "def refuse(step):\n"
        "    raise PlatformError('X_Y', 't', 422, location={'step_id': step.id})\n",
        "unregistered: planted.py refuse",
    ),
    "a JobErrorLocation built": (
        "def refuse(step):\n    return JobErrorLocation(step_id=step.id)\n",
        "unregistered: planted.py refuse",
    ),
    "an f-string value": (
        "def refuse(name):\n"
        "    raise PlatformError('X_Y', 't', 422, location={'field': f'inputs.{name}'})\n",
        "composed text: planted.py:2",
    ),
    "a concatenated value": (
        "def refuse(name):\n"
        "    raise PlatformError('X_Y', 't', 422, location={'field': 'inputs.' + name})\n",
        "composed text: planted.py:2",
    ),
    "a formatted value": (
        "def refuse(name):\n"
        "    raise PlatformError('X_Y', 't', 422, location={'field': 'inputs.{}'.format(name)})\n",
        "composed text: planted.py:2",
    ),
}


@pytest.mark.parametrize("shape", sorted(_PLANTED_LOCATIONS))
def test_the_location_census_finds_each_planted_shape(shape: str) -> None:
    """Red on deliberately broken input: each shape, planted, is reported under its own reason."""
    source, expected = _PLANTED_LOCATIONS[shape]
    sites, composed = _location_sites(source, "planted.py")
    registered = {("planted.py", "refuse"): "a registered site"} if "composed" in expected else {}
    assert expected in _location_problems(sites, composed, registered)


def test_the_location_census_is_quiet_on_a_copy_and_reports_a_stale_entry() -> None:
    copy = "def run(exc):\n    return JobError(code=exc.code, location=exc.location)\n"
    sites, composed = _location_sites(copy, "planted.py")
    assert sites == {("planted.py", "run")}
    assert _location_problems(sites, composed, {("planted.py", "run"): "a copy"}) == []
    assert _location_problems(set(), [], {("planted.py", "run"): "a copy"}) == [
        "stale entry: planted.py run"
    ]


@pytest.mark.req("NFR-499")
def test_a_banding_refusal_in_a_fit_keeps_its_text_and_no_row_value() -> None:
    """The `BandingError` arm of `model_handlers._fit` persists `safe_error_detail(exc)`."""
    from uuid import uuid4

    frame = pl.DataFrame({"age": [None, None], "note": [_SENTINEL, _SENTINEL]})
    proposal = BandingProposal(
        dataset_version_id=uuid4(), column="age", method=BandingMethod.EQUAL_WIDTH
    )
    with pytest.raises(BandingError) as refused:
        propose_banding(frame, proposal, dataset_id=uuid4(), slug="age")
    detail = safe_error_detail(refused.value)
    assert isinstance(refused.value, CodedError)
    assert "'age'" in detail, "control: the allow-list keeps the refusal's own text"
    assert _SENTINEL not in detail


_REFUSED_FORMULA = "__import__('os')"


@pytest.mark.req("NFR-499", "FR-95")
def test_an_expression_refusal_over_a_dataset_keeps_its_text_and_no_row_value() -> None:
    """The six wrapped sites of an `expression` Factor or Banding (`bandings._cut_values` x2,
    `bandings.source_columns_of`, `factors._expression_series` x2; the sixth is the creation
    sink below): each keeps the grammar text and the engine's dtype prose, and a sentinel in
    the dataset's rows is in none, because the text goes through `safe_error_text`."""
    from uuid import uuid4

    from model_schema import Factor, FactorType
    from pricing_core.modelling import FactorResolutionError, resolve_factors, source_columns_of

    frame = pl.DataFrame({"region": [_SENTINEL] * 3, "age": [30.0, 40.0, 50.0]})
    dataset = uuid4()

    def factor(expression: str) -> Factor:
        return Factor(
            id=uuid4(), slug="expr-factor", dataset_id=dataset, version=1,
            type=FactorType.EXPRESSION, source_columns=("region",), expression=expression,
            banding_id=uuid4(),
        )

    def proposal(expression: str) -> BandingProposal:
        return BandingProposal(
            dataset_version_id=dataset, source_expression=expression,
            method=BandingMethod.EQUAL_WIDTH,
        )

    refusals: list[FactorResolutionError] = []
    for expression in (_REFUSED_FORMULA, "region * 2"):  # grammar arm, then the engine's dtype arm
        for attempt in (
            lambda e=expression: resolve_factors(frame, [factor(e)]),
            lambda e=expression: propose_banding(frame, proposal(e), dataset_id=dataset, slug="s"),
        ):
            with pytest.raises(FactorResolutionError) as refused:
                attempt()
            refusals.append(refused.value)
    with pytest.raises(FactorResolutionError) as refused:
        source_columns_of(proposal(_REFUSED_FORMULA), frame.columns)
    refusals.append(refused.value)
    assert len(refusals) == 5
    for refusal in refusals:
        assert _SENTINEL not in str(refusal)
    assert "'__import__' is not an allowed function" in str(refusals[0]), (
        "control: the grammar arm keeps the author's own text"
    )
    assert "dtypes" in str(refusals[2]), "control: the dtype arm keeps the engine's own text"


@pytest.mark.req("NFR-499", "FR-95")
def test_every_expression_error_is_raised_where_no_row_value_is_in_scope() -> None:
    """Why `safe_error` may keep an `ExpressionError`'s text: every function in
    `pricing_core/data/expressions.py` that constructs one takes an expression and column
    names, never a polars frame or series, so no row value can reach its message."""
    path = _ROOT / "packages/pricing-core/src/pricing_core/data/expressions.py"
    assert _expression_error_scopes_with_data(path.read_text(encoding="utf-8")) == []
    # Positive control: the predicate sees a function that takes a frame and raises one.
    leaky = (
        "import polars as pl\n"
        "def evaluate(frame: pl.DataFrame):\n"
        "    raise ExpressionError(f'bad {frame}')\n"
    )
    assert _expression_error_scopes_with_data(leaky) == ["evaluate"]


def _expression_error_scopes_with_data(source: str) -> list[str]:
    """Names of functions that construct an `ExpressionError` and take a polars frame, series
    or lazy frame (any parameter annotated `pl.DataFrame`, `pl.Series` or `pl.LazyFrame`)."""
    tree = ast.parse(source)
    leaking: list[str] = []
    for function in ast.walk(tree):
        if not isinstance(function, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        raises = any(
            isinstance(node, ast.Call)
            and (getattr(node.func, "id", None) or getattr(node.func, "attr", None))
            == "ExpressionError"
            for node in ast.walk(function)
        )
        takes_data = any(
            any(
                isinstance(part, ast.Attribute)
                and part.attr in ("DataFrame", "Series", "LazyFrame")
                for part in ast.walk(argument.annotation)
            )
            for argument in (*function.args.args, *function.args.kwonlyargs)
            if argument.annotation is not None
        )
        if raises and takes_data:
            leaking.append(function.name)
    return leaking


@pytest.mark.req("NFR-499", "FR-95")
def test_an_expression_factor_refusal_at_creation_carries_the_formula_and_no_row() -> None:
    """`_require_a_creatable_expression` reads no dataset: it answers the formula's own
    grammar refusal, positioned (RL-1700 (b))."""
    import asyncio
    from uuid import uuid4

    from app.errors import PlatformError
    from app.platform.modelling import _require_a_creatable_expression
    from model_schema import Factor, FactorType

    factor = Factor(
        id=uuid4(), slug="expr-factor", dataset_id=uuid4(), version=1,
        type=FactorType.EXPRESSION, source_columns=("region",), expression=_REFUSED_FORMULA,
    )
    with pytest.raises(PlatformError) as refused:
        asyncio.run(
            _require_a_creatable_expression(None, workspace_id=uuid4(), factor=factor)  # type: ignore[arg-type]
        )
    (error,) = refused.value.errors
    assert error.field == "expression"
    assert error.message.startswith("line 1, column ")
    assert _SENTINEL not in error.message


@pytest.mark.req("NFR-499")
def test_the_derived_scope_holds_every_worker_handler() -> None:
    """The scope is a glob, not a list: the four handlers a list once omitted are in it, and a
    file added under a globbed directory is in it by default."""
    in_scope = {p.relative_to(_ROOT).as_posix() for p in _files()}
    assert set(_MUST_BE_IN_SCOPE) <= in_scope
    on_disk = {p.name for p in (_ROOT / "backend/src/app/worker").glob("*.py")}
    assert on_disk <= {Path(f).name for f in in_scope}


@pytest.mark.req("NFR-499")
def test_the_census_sees_an_injected_sink() -> None:
    """Positive control: each shape of sink is found in a source that is not in the repository."""
    source = (
        "import logging\n_log = logging.getLogger('x')\n\n\n"
        "def leak_log(exc):\n    _log.exception('failed')\n\n\n"
        "def leak_text(exc):\n    return f'failed: {exc}'\n\n\n"
        "def leak_str(exc):\n    return str(exc)\n\n\n"
        "def leak_column(row, exc):\n    row.last_error = 'x'\n\n\n"
        "def leak_row():\n    return {'error_message': 'x'}\n\n\n"
        "def leak_info(exc):\n    _log.error('x', exc_info=exc)\n\n\n"
        "def leak_job(exc):\n    return JobError(code='X', message='y')\n"
    )
    assert dict(_sinks(source, "injected.py")) == {
        ("injected.py", "leak_log", "exception"): 1,
        ("injected.py", "leak_text", "{exc}"): 1,
        ("injected.py", "leak_str", "str(exc)"): 1,
        ("injected.py", "leak_column", "last_error"): 1,
        ("injected.py", "leak_row", "error_message key"): 1,
        ("injected.py", "leak_info", "exc_info"): 1,
        ("injected.py", "leak_job", "JobError"): 1,
    }
    # FD-1507: an exception is recognised by what it is -- bound by an enclosing `except ... as`
    # (whatever the name), or a parameter named `exc` -- never by the spelling of a variable.
    renamed = (
        "def handler_str():\n    try:\n        pass\n    except ValueError as problem:\n"
        "        return str(problem)\n\n\n"
        "def handler_text():\n    try:\n        pass\n    except ValueError as failure:\n"
        "        return f'failed: {failure}'\n"
    )
    assert dict(_sinks(renamed, "renamed.py")) == {
        ("renamed.py", "handler_str", "str(exc)"): 1,
        ("renamed.py", "handler_text", "{exc}"): 1,
    }
    not_an_exception = "def band(low):\n    e = 1\n    return str(e) + f'{e}'\n"
    assert dict(_sinks(not_an_exception, "edge.py")) == {}


class _Quote(BaseModel):
    driver_age: int


@pytest.mark.req("NFR-499")
def test_an_unexpected_request_failure_logs_no_input(
    api_client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    """The middleware's own catch: a `ValidationError` escaping a route carries the request's
    input in its text. The log line keeps the frames, the type and the trace id."""

    async def boom() -> None:
        _Quote.model_validate({"driver_age": _SENTINEL})

    api_client.app.add_api_route("/__boom_nfr499", boom)  # type: ignore[attr-defined]
    with caplog.at_level(logging.DEBUG):
        response = api_client.get("/__boom_nfr499")

    assert response.status_code == 500
    assert _SENTINEL not in response.text
    assert "request failed" in caplog.text
    assert _SENTINEL not in caplog.text
    record = next(r for r in caplog.records if r.getMessage() == "request failed")
    assert record.exc_info is not None
    assert ValidationError.__name__ in str(record.exc_info[1])


_AUTHORED = "authored-trigger"
_CODED = "coded-trigger"


class _SentinelBody(BaseModel):
    driver_age: int

    @field_validator("driver_age", mode="before")
    @classmethod
    def _refuse_with_the_value(cls, value: object) -> object:
        if value == _SENTINEL:
            # A custom validator that interpolates what it was given: the shape of every
            # `value_error` and `assertion_error` a request model can raise.
            raise ValueError(f"unacceptable value {value}")
        if value == _AUTHORED:
            raise InputFreeError("an authored, input-free message")
        if value == _CODED:
            raise CodedError("AUTHORED_CODE: an authored, input-free message")
        return value


def _post(api_client: TestClient, path: str, value: str) -> dict[str, object]:
    async def intake(body: _SentinelBody) -> None:
        return None

    api_client.app.add_api_route(path, intake, methods=["POST"])  # type: ignore[attr-defined]
    response = api_client.post(path, json={"driver_age": value})
    assert response.status_code == 422
    assert _SENTINEL not in response.text
    return response.json()  # type: ignore[no-any-return]


@pytest.mark.req("NFR-499")
def test_a_request_validation_422_carries_no_submitted_value(api_client: TestClient) -> None:
    """FD-1589 row 8: `_handle_validation_error` copied pydantic's `msg` into the 422's
    `FieldError.message`, and a custom validator's `msg` carries the submitted value."""
    body = _post(api_client, "/__nfr499_422", _SENTINEL)
    assert body["errors"][0]["code"] == "VALUE_ERROR"  # type: ignore[index]


@pytest.mark.req("NFR-499")
def test_an_input_free_validator_message_survives_the_422_sink(api_client: TestClient) -> None:
    """An `InputFreeError` is input-free by construction, so its authored message is kept,
    byte for byte as on `main` (DP-4 (a): the "Value error, " prefix stays)."""
    body = _post(api_client, "/__nfr499_authored", _AUTHORED)
    assert body["errors"][0]["message"] == "Value error, an authored, input-free message"  # type: ignore[index]


@pytest.mark.req("NFR-499")
def test_a_coded_validator_message_gets_the_fixed_text(api_client: TestClient) -> None:
    """A `CodedError` is not on the 422 allow-list (DP-3 (a) with DP-5 (b)): the parked form of
    this test asserted its text survived; PL-1599 Task 5 changes that on purpose."""
    body = _post(api_client, "/__nfr499_coded", _CODED)
    assert body["errors"][0]["message"] == "The value is not valid (VALUE_ERROR)."  # type: ignore[index]


def _positioned_refusal() -> ExpressionError:
    refusal = ExpressionError("refused", node=ast.parse("a + b", mode="eval").body)
    refusal.__cause__ = ValueError(_SENTINEL)
    return refusal


@pytest.mark.req("NFR-499")
def test_the_objective_grammar_refusal_is_the_allow_lists_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`objectives.grammar_refusal` (create and preview share it) reads `safe_error_detail`."""
    from app.platform import objectives

    def refuse(*_: object, **__: object) -> None:
        raise _positioned_refusal()

    monkeypatch.setattr(objectives, "parse_expression", refuse)
    refusal = objectives.grammar_refusal("a + b", symbols=frozenset({"a", "b"}))
    assert refusal == (1, 1, "line 1, column 1: refused"), "control: the author's own text"
    assert _SENTINEL not in str(refusal)


@pytest.mark.req("NFR-499")
def test_the_objective_preview_derive_refusal_is_the_allow_lists_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`objective_preview._run`'s `derive` arm answers `safe_error_detail`, not `str(exc)`."""
    from app.platform import objective_preview
    from model_schema import ObjectivePreviewRequest

    def refuse(*_: object, **__: object) -> None:
        raise _positioned_refusal()

    monkeypatch.setattr(objective_preview, "derive", refuse)
    request = ObjectivePreviewRequest.model_validate(
        {
            "loss": "w * (y - f) ** 2",
            "parameters": [],
            "grid": {"y": 1.0, "w": 1.0, "f_range": [0.0, 1.0], "n_points": 3},
        }
    )
    answer = objective_preview._run(request)
    assert answer.error is not None
    assert answer.error.message == "line 1, column 1: refused", "control: the author's own text"
    assert _SENTINEL not in answer.error.message
