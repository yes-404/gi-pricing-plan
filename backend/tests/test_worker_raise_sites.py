"""A coded refusal on a quote-input path names no quote input (NFR-499, RL-917).

`pricing_core`'s raise sites are held by
`packages/pricing-core/tests/test_quote_input_raise_sites.py`.
This file holds the backend half: every `PlatformError(` / `_raise_named(` / `CodedError(` under
`backend/src/app/**` whose code is a quote-input code, or is
not a literal (so could be one), is enumerated by AST and pinned to **the expressions it
interpolates**. A site whose message gains an expression (`f"{stats}"`) fails here until the new
expression is reviewed as input-free and listed. The file set is derived by glob, so a new file is
covered by default (maintainer, 2026-09-29, Q889-a, widened by Q889-c to all of `app`). The code
may be positional or the `code=` keyword, and keyword arguments (`detail=`) are read too.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_GLOBS = ("backend/src/app/**/*.py",)
#: Files the globs match and the census leaves out, each with why. Empty: none needs leaving out.
_EXCLUDED: dict[str, str] = {}
_MUST_BE_IN_SCOPE = (
    "backend/src/app/worker/rating_handlers.py",
    "backend/src/app/worker/model_handlers.py",
    "backend/src/app/worker/data_handlers.py",
    "backend/src/app/worker/rate_table_handlers.py",
    "backend/src/app/worker/scoring_handlers.py",
    "backend/src/app/worker/trace_handlers.py",
)
_CALLEES = ("PlatformError", "_raise_named", "CodedError")
#: The codes a quote input can reach: `pricing-core`'s four per-quote codes, the ladder check,
#: and the batch run's two (their message states a failure rate from a batch of quotes).
_QUOTE_INPUT_CODES = frozenset({
    "INPUT_CONTRACT_VIOLATION", "RATE_TABLE_MISS", "REFERENCE_LOOKUP_MISS", "MODEL_CALL_FAILED",
    "LADDER_RECONCILIATION_FAILED", "BATCH_ABORTED", "BATCH_ABORT_THRESHOLD_ABOVE_SETTING",
})
_DYNAMIC = "<dynamic>"

_Key = tuple[str, str, str]


def _files() -> list[Path]:
    found = {p for pattern in _GLOBS for p in _ROOT.glob(pattern) if "__pycache__" not in p.parts}
    return sorted(p for p in found if p.relative_to(_ROOT).as_posix() not in _EXCLUDED)


def _interpolated(node: ast.expr) -> set[str]:
    """The non-literal expressions an argument is built from."""
    if isinstance(node, ast.Constant):
        return set()
    if isinstance(node, ast.JoinedStr):
        found: set[str] = set()
        for part in node.values:
            if isinstance(part, ast.FormattedValue):
                found.add(ast.unparse(part.value))
        return found
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _interpolated(node.left) | _interpolated(node.right)
    if isinstance(node, ast.IfExp):
        return _interpolated(node.body) | _interpolated(node.orelse)
    return {ast.unparse(node)}


def _sites(source: str, name: str) -> dict[_Key, set[str]]:
    found: dict[_Key, set[str]] = {}

    def visit(node: ast.AST, function: str) -> None:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            function = node.name
        if (
            isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in _CALLEES
        ):
            keyword_code = next((k.value for k in node.keywords if k.arg == "code"), None)
            first = node.args[0] if node.args else keyword_code
            if first is None:
                code = ""  # not a coded raise: nothing to pin (an exception's own `code` attribute)
            elif isinstance(first, ast.Constant) and isinstance(first.value, str):
                code = first.value if first.value in _QUOTE_INPUT_CODES else ""
            else:
                code = _DYNAMIC
            if code:
                exprs: set[str] = set()
                rest = node.args[1:] if node.args else []
                for argument in [*rest, *(k.value for k in node.keywords if k.arg != "code")]:
                    exprs |= _interpolated(argument)
                found.setdefault((name, function, code), set()).update(exprs)
        for child in ast.iter_child_nodes(node):
            visit(child, function)

    visit(ast.parse(source), "<module>")
    return found


def _census() -> dict[_Key, frozenset[str]]:
    total: dict[_Key, set[str]] = {}
    for path in _files():
        name = path.relative_to(_ROOT).as_posix()
        for key, exprs in _sites(path.read_text(encoding="utf-8"), name).items():
            total.setdefault(key, set()).update(exprs)
    return {key: frozenset(exprs) for key, exprs in total.items()}


#: (file, function, code) -> (the expressions its message and arguments interpolate, why each is
#: input-free). A quote-input code's message states a count, a threshold or a ref, never a value.
_SITES: dict[_Key, tuple[frozenset[str], str]] = {
    ("backend/src/app/api/score.py", "_as_platform_error", _DYNAMIC): (
        frozenset({
            "_PER_QUOTE_STATUS", "code.replace('_', ' ').title()", "detail or None",
            "_LADDER_REFUSAL_STATUS", "detail", "_LADDER_REFUSAL_NOTE",
        }),
        "reached only for a `CodedError` (by class): its detail is the input-free coded message, "
        "and the title is the code. The `LADDER_RECONCILIATION_FAILED` branch (RL-1346) adds a "
        "fixed status and a fixed sentence to `build_scoring_result`'s clause, rung names and "
        "minor-unit differences",
    ),
    ("backend/src/app/api/score.py", "_naming_side", _DYNAMIC): (
        frozenset({"detail", "problem.status_code", "problem.title"}),
        "re-wraps a `PlatformError` `_as_platform_error` built, prefixing `base` or `comparison`",
    ),
    ("backend/src/app/auth/service.py", "_unauthenticated", _DYNAMIC): (
        frozenset(),
        "a fixed 401 detail chosen by the caller of the helper; no interpolation",
    ),
    ("backend/src/app/platform/jobs.py", "transition", _DYNAMIC): (
        frozenset({"row.status.value", "to_status.value"}),
        "two Job status names",
    ),
    ("backend/src/app/platform/prediction.py", "_unscoreable", _DYNAMIC): (
        frozenset({"str(exc)"}),
        "`ModellingError`/`PredictionError` on the synchronous model-prediction path"
        " (test_error_sinks.py `_SINKS`)",
    ),
    ("backend/src/app/platform/rate_tables.py", "_edit_failure", _DYNAMIC): (
        frozenset({"errors", "len(errors)"}),
        "a manual edit's refusal: `errors` are the field errors, whose value issues name the table "
        "key and the submitted value (pricing configuration, the caller's own edit, not a quote "
        "input under NFR-499; ruled in the maintainer's 2026-10-10 22:16:18 BST entry in "
        "`to-lead.md`); `len(errors)` is a count",
    ),
    ("backend/src/app/platform/rate_tables.py", "_load_table", "RATE_TABLE_MISS"): (
        frozenset({"slug"}),
        "an artifact slug the caller named in the path; a rate-table lookup, not a per-quote miss",
    ),
    ("backend/src/app/platform/rate_tables.py", "_load_version", "RATE_TABLE_MISS"): (
        frozenset({"slug", "version_number"}),
        "an artifact slug and version number; not a per-quote miss",
    ),
    ("backend/src/app/platform/rate_tables.py", "_map_operation_error", _DYNAMIC): (
        frozenset({"code.replace('_', ' ').title()", "detail"}),
        "a rate-table bulk operation's own named refusal (test_error_sinks.py `_SINKS`)",
    ),
    ("backend/src/app/platform/rate_tables.py", "_resolve_baseline", "RATE_TABLE_MISS"): (
        frozenset({"version"}),
        "a baseline version number; not a per-quote miss",
    ),
    ("backend/src/app/platform/rate_tables.py", "bulk_operation", "RATE_TABLE_MISS"): (
        frozenset({"slug"}),
        "an artifact slug; not a per-quote miss",
    ),
    ("backend/src/app/platform/rating_algorithms.py", "raise_first_issue", _DYNAMIC): (
        frozenset({"issue.code.replace('_', ' ').title()", "issue.message"}),
        "save-time graph-validation issues about an algorithm's own nodes; no quote is involved",
    ),
    ("backend/src/app/platform/rating_versions.py", "compile_rating_version", _DYNAMIC): (
        frozenset({"code.replace('_', ' ').title()", "detail"}),
        "compile time: an artifact-level error from `compile_bundle`"
        " (test_error_sinks.py `_SINKS`)",
    ),
    ("backend/src/app/platform/transformations.py", "_refuse", _DYNAMIC): (
        frozenset({"str(exc)", "title"}),
        "a dataset transformation's named refusal (test_error_sinks.py `_SINKS`);"
        " Dataset Version path",
    ),
    ("backend/src/app/worker/model_handlers.py", "_compare", _DYNAMIC): (
        frozenset({"str(exc)"}),
        "`ModellingError` on the model path (test_error_sinks.py `_SINKS`); no Quote Context",
    ),
    ("backend/src/app/worker/model_handlers.py", "_fit", _DYNAMIC): (
        frozenset({"spec.model_type", "str(exc)"}),
        "a named fit refusal on the model path (test_error_sinks.py `_SINKS`); no Quote Context",
    ),
    ("backend/src/app/worker/model_handlers.py", "_reconcile", _DYNAMIC): (
        frozenset({"str(exc)"}),
        "`ModellingError` on the peril-reconciliation path (test_error_sinks.py `_SINKS`)",
    ),
    ("backend/src/app/worker/rating_handlers.py", "_rating_regression", _DYNAMIC): (
        frozenset({"failed_golden", "failed_props", "ref", "run.suite_ref", "saved.id"}),
        "golden-quote and property NAMES the suite's author wrote, a version ref and two ids",
    ),
    ("backend/src/app/worker/scoring_handlers.py", "_effective_threshold",
     "BATCH_ABORT_THRESHOLD_ABOVE_SETTING"): (
        frozenset({"requested", "workspace_threshold"}),
        "two failure-rate thresholds, both numbers the caller and the workspace set",
    ),
    ("backend/src/app/worker/scoring_handlers.py", "_score_one_ref", "BATCH_ABORTED"): (
        frozenset({"effective_threshold", "ref", "stats.failure_rate"}),
        "an observed failure rate, the threshold and the version ref; never a row's value",
    ),
    ("backend/src/app/platform/dislocation_runs.py", "estimate_for_spec", _DYNAMIC): (
        frozenset({"exc.code.replace('_', ' ').title()", "safe_error_text(exc)"}),
        "an `AttributionError` from `derive_changes` (WK-673 Slice 4, 03 §5.1): the title is its "
        "code, one of three fixed names, and the detail is `safe_error_text(exc)`, built at "
        "dislocation_runs.py:253, which keeps the type name and no message text for a non-coded "
        "error (NFR-499)",
    ),
    ("backend/src/app/worker/dislocation_handlers.py", "_dislocation_run", _DYNAMIC): (
        frozenset({"exc.code.replace('_', ' ').title()", "safe_error_text(exc)"}),
        "an `AttributionError` from `attribute` (WK-673 Slice 4, 03 §5.1): the title is its code, "
        "one of three fixed names, and the detail is `safe_error_text(exc)`, built at "
        "dislocation_handlers.py:236; `attribute`'s own message can name a quote id "
        "(analysis.py `no premium under the subset bundle`), which is why the raw text is not kept "
        "(NFR-499)",
    ),
}


@pytest.mark.req("NFR-499")
def test_the_derived_scope_holds_every_worker_handler() -> None:
    in_scope = {p.relative_to(_ROOT).as_posix() for p in _files()}
    assert set(_MUST_BE_IN_SCOPE) <= in_scope
    worker = _ROOT / "backend/src/app/worker"
    on_disk = {p.relative_to(_ROOT).as_posix() for p in worker.glob("*.py")}
    assert on_disk <= in_scope


@pytest.mark.req("NFR-499")
def test_every_quote_input_coded_raise_site_in_the_backend_is_accounted_for() -> None:
    assert _census() == {key: exprs for key, (exprs, _) in _SITES.items()}, (
        "a quote-input `PlatformError`/`_raise_named` site was added, moved, or now interpolates "
        "a new expression: review that it names no quote input, then list it in _SITES"
    )


@pytest.mark.req("NFR-499")
def test_the_backend_guard_sees_an_injected_leak_and_an_injected_site() -> None:
    """Positive control on a source that is not in the repository."""
    clean = (
        "def f(stats):\n"
        "    raise PlatformError('BATCH_ABORTED', 't', 422, f'rate {stats.failure_rate}')\n"
    )
    leaky = clean.replace("{stats.failure_rate}", "{stats.failure_rate} {stats}")
    assert _sites(clean, "x.py") == {("x.py", "f", "BATCH_ABORTED"): {"stats.failure_rate"}}
    assert _sites(leaky, "x.py") == {
        ("x.py", "f", "BATCH_ABORTED"): {"stats.failure_rate", "stats"}
    }
    dynamic = "def g(exc):\n    raise PlatformError(exc.code, 't', 409, str(exc))\n"
    assert _sites(dynamic, "x.py") == {("x.py", "g", _DYNAMIC): {"str(exc)"}}
    keyword = (
        "def k(s):\n"
        "    raise PlatformError(code='BATCH_ABORTED', title='t', status_code=422, detail=f'{s}')\n"
    )
    assert _sites(keyword, "x.py") == {("x.py", "k", "BATCH_ABORTED"): {"s"}}
    other = "def h():\n    raise PlatformError('NOT_FOUND', 't', 404, 'x')\n"
    assert _sites(other, "x.py") == {}
