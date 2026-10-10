"""Every place a failure's text is stored or logged on a quote-input path goes through the
allow-list (NFR-499, RL-917), and a coverage guard keeps it that way.

`pricing_core.safe_error` / `app.platform.safe_exception` keep an exception's text only where it
is ours and input-free. That holds only while every **sink** uses them. This file enumerates the
sinks by AST, over the files a quote input can reach (the scoring route, the job runner, the
batch handler, the request middleware, the outbox, and `pricing_core.rating`), and fails when one
is added, moved or removed without a matching line in `_SINKS` saying what covers it.

A sink is: a logging call passed `exc_info`, a `.exception(` call, a `JobError(` construction, an
assignment to `last_error`, a use of an exception's text (`str(exc)`, `{exc}`), and a dict entry
`error_message`.
"""

from __future__ import annotations

import ast
import logging
from collections import Counter
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError, field_validator

from model_schema.input_free import InputFreeError
from pricing_core.safe_error import CodedError

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
    ("backend/src/app/api/score.py", "_as_platform_error", "str(exc)"): (
        1, "reached only for a `CodedError` (by class, not text shape): the message has its value "
        "dropped at source: test_quote_input_raise_sites.py "
        "and test_score.py::test_a_422_for_a_bad_input_names_the_field_and_carries_no_value"),
    ("backend/src/app/api/score.py", "_maybe_sample_trace", "exc_info"): (
        1, "test_score.py::test_a_trace_sampling_failure_logs_no_quote_input"),
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
    ("backend/src/app/platform/metrics.py", "_validated", "{exc}"): (
        1, "a custom metric's own declaration error (RL-917's artifact path); no Quote Context"),
    ("backend/src/app/platform/modelling.py", "resolve_offset_model", "str(exc)"): (
        1, "`FactorResolutionError`: names a factor and a dataset version; model path"),
    ("backend/src/app/platform/objectives.py", "_validated", "{exc}"): (
        1, "a custom objective's own declaration error; no Quote Context"),
    ("backend/src/app/platform/objectives.py", "_require_the_grammar", "str(exc)"): (
        1, "`ExpressionError`: the grammar refusal of an author's own loss text, positioned by "
        "line and column; a custom objective's declaration error (FR-145), no Quote Context"),
    ("backend/src/app/platform/objectives.py", "derive_objective", "str(exc)"): (
        2, "`ExpressionError` on an author's own loss text, as the problem detail and its "
        "`loss` field error; a custom objective's declaration error (FR-145), no Quote Context"),
    ("backend/src/app/platform/prediction.py", "_unscoreable", "str(exc)"): (
        1, "`ModellingError`/`PredictionError`: named refusal of a model prediction; a "
        "Fitted Model scored on caller rows, synchronous, returned to the caller who sent"
        " them and not stored or logged"),
    ("backend/src/app/platform/prediction.py", "predict_rows", "{exc}"): (
        1, "polars' text for a ragged body, returned to the caller who sent it in a 422; "
        "synchronous model-prediction path, not stored or logged, not a Quote Context"),
    ("backend/src/app/platform/rate_tables.py", "_map_operation_error", "str(exc)"): (
        2, "a bulk operation's named refusal over a rate table; a rate table is not a quote input"),
    ("backend/src/app/platform/rate_tables.py", "bulk_operation", "str(exc)"): (
        1, "a rate-table bulk operation's parameter validation, echoed to the caller who sent it"),
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
    ("packages/pricing-core/src/pricing_core/rate_tables/weights.py", "_resolved_series",
     "str(exc)"): (
        1, "re-wraps a `FactorResolutionError` as a `WeightJoinError` with its message kept, as "
        "RL-1418 T5 and RL-1361 item 3 rule (the count and the example value); the input is a "
        "portfolio Dataset Version, not a Quote Context; the message reaches the Job's failure "
        "(test_rate_table_diff_portfolio.py::"
        "test_a_resolution_error_reaches_the_failed_job_with_its_count_and_example)"),
    ("backend/src/app/platform/rating_algorithms.py", "graph_validation_error", "str(exc)"): (
        1, "RETURNS Pydantic's text of the submitter's own algorithm or sub-graph JSON to the "
        "submitter in the 422 body; not stored, not logged; an artifact definition, not a Quote "
        "Context. The code is chosen by the typed error class, never by this text (FD-1326)"),
    ("backend/src/app/platform/rating_versions.py", "create_rating_version", "str(exc)"): (
        1, "create time: an artifact-level refusal (FR-223 MODEL_REFERENCE_MODE_INCONSISTENT) "
        "naming the step and the two declared modes; no quote is involved"),
    ("backend/src/app/platform/regression_suites.py", "_validate_properties", "{exc}"): (
        1, "VERDICT (Q889-c): cannot carry a quote-input value. `UnsweepableProperty`'s text"
        " (`properties.py`, five raises) interpolates only `check.input`, "
        "`field.type.value`, `field.name`, and the `lower`/`upper` bounds, all declared "
        "by the suite's author or the input contract; the swept values are generated "
        "later, never in this text. Save-time, at declaration, before any quote-derived "
        "run"),
    ("backend/src/app/platform/settings.py", "_parse_env", "{exc}"): (
        1, "a workspace setting or environment override, an operator value; not a quote input"),
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
    ("packages/pricing-core/src/pricing_core/rating/compile.py", "_check_vocabulary", "{exc}"): (
        1, "compile time, artifact-level: no quote is involved"),
    ("packages/pricing-core/src/pricing_core/rating/score.py", "_failing_node", "str(exc)"): (
        1, "reads only the engine error's JSON `nodeId`; the text is neither stored nor logged, "
        "and only a matched step's own id reaches the raised message: "
        "test_rating_score.py::test_an_engine_error_text_never_reaches_the_raised_message"),
    ("packages/pricing-core/src/pricing_core/rating/score.py", "_score_batch_row",
     "error_message key"): (
        2, "test_scoring_handlers.py and test_quote_input_raise_sites.py (the error row and "
        "the success row's None)"),
}


def _files() -> list[Path]:
    derived = {p for pattern in _GLOBS for p in _ROOT.glob(pattern) if "__pycache__" not in p.parts}
    return sorted(p for p in derived if p.relative_to(_ROOT).as_posix() not in _EXCLUDED)


def _sinks(source: str, name: str) -> Counter[tuple[str, str, str]]:
    found: Counter[tuple[str, str, str]] = Counter()

    def visit(node: ast.AST, function: str) -> None:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            function = node.name
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
            if (
                called == "str" and node.args and isinstance(node.args[0], ast.Name)
                and node.args[0].id in ("exc", "e", "err")
            ):
                found[(name, function, "str(exc)")] += 1
        if (
            isinstance(node, ast.FormattedValue) and isinstance(node.value, ast.Name)
            and node.value.id in ("exc", "e", "err")
        ):
            found[(name, function, "{exc}")] += 1
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and target.attr == "last_error":
                    found[(name, function, "last_error")] += 1
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and key.value == "error_message":
                    found[(name, function, "error_message key")] += 1
        for child in ast.iter_child_nodes(node):
            visit(child, function)

    visit(ast.parse(source), "<module>")
    return found


def _census() -> dict[tuple[str, str, str], int]:
    total: Counter[tuple[str, str, str]] = Counter()
    for path in _files():
        total += _sinks(path.read_text(encoding="utf-8"), path.relative_to(_ROOT).as_posix())
    return dict(total)


@pytest.mark.req("NFR-499")
def test_every_failure_sink_on_a_quote_input_path_is_accounted_for() -> None:
    assert _census() == {key: count for key, (count, _) in _SINKS.items()}, (
        "a sink that stores or logs an exception's text was added, moved or removed: bring it "
        "under app.platform.safe_exception / pricing_core.safe_error, give it a sentinel test, "
        "and list it in _SINKS"
    )


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
