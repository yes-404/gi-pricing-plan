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
from pydantic import BaseModel, ValidationError

_ROOT = Path(__file__).resolve().parents[2]
_SCOPE = [
    "backend/src/app/api/score.py",
    "backend/src/app/worker/tasks.py",
    "backend/src/app/worker/scoring_handlers.py",
    "backend/src/app/worker/trace_handlers.py",
    "backend/src/app/observability/middleware.py",
    "backend/src/app/platform/outbox.py",
    "backend/src/app/platform/traces.py",
    "packages/pricing-core/src/pricing_core/rating",
]

_SENTINEL = "SENTINEL-quote-input-d7e3c518"

#: (file, function, kind) -> (how many, what covers it).
_SINKS: dict[tuple[str, str, str], tuple[int, str]] = {
    ("backend/src/app/api/score.py", "_as_platform_error", "str(exc)"): (
        1, "the coded message with the value dropped at source: test_quote_input_raise_sites.py "
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
    ("packages/pricing-core/src/pricing_core/rating/compile.py", "_check_vocabulary", "{exc}"): (
        1, "compile time, artifact-level: no quote is involved"),
    ("packages/pricing-core/src/pricing_core/rating/score.py", "_score_batch_row",
     "error_message key"): (
        2, "test_scoring_handlers.py and test_quote_input_raise_sites.py (the error row and "
        "the success row's None)"),
}


def _files() -> list[Path]:
    files: list[Path] = []
    for entry in _SCOPE:
        path = _ROOT / entry
        files += sorted(path.glob("*.py")) if path.is_dir() else [path]
    return files


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
def test_the_census_sees_an_injected_sink() -> None:
    """Positive control: each shape of sink is found in a source that is not in the repository."""
    source = (
        "import logging\n_log = logging.getLogger('x')\n\n\n"
        "def leak_log(exc):\n    _log.exception('failed')\n\n\n"
        "def leak_text(exc):\n    return f'failed: {exc}'\n\n\n"
        "def leak_str(exc):\n    return str(exc)\n\n\n"
        "def leak_column(row, exc):\n    row.last_error = 'x'\n\n\n"
        "def leak_row():\n    return {'error_message': 'x'}\n"
    )
    assert dict(_sinks(source, "injected.py")) == {
        ("injected.py", "leak_log", "exception"): 1,
        ("injected.py", "leak_text", "{exc}"): 1,
        ("injected.py", "leak_str", "str(exc)"): 1,
        ("injected.py", "leak_column", "last_error"): 1,
        ("injected.py", "leak_row", "error_message key"): 1,
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
