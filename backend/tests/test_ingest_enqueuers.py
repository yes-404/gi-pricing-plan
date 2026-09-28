"""The ingest route is the only place under `backend/src` that enqueues `dataset.ingest`.

The worker's ingest handler has no ownership check of its own, by design: `blobs` has no
workspace column, and whether a workspace may read a digest is decided once, at the ingest
route (`api/datasets.py::start_ingestion`, through `blob_readable_by`). That is sound only while
the route is the only enqueuer. A second one, a new internal caller or a second route, would
bypass the check without any test failing, so this test fails the moment one appears; the
worker-side check arrives with an owner record (the upload-completion finding in #869).

The scan is by AST. An **enqueue** is a call that is handed the `dataset.ingest` job kind,
either as `JobKind.DATASET_INGEST` or as the string `"dataset.ingest"`, in an argument or a
keyword (`submit(..., JobKind.DATASET_INGEST, ...)`, `JobRow(kind=JobKind.DATASET_INGEST)`).
Registering the handler and mapping the kind to its queue mention the kind but are not calls
handed it directly, so they are not enqueues.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
#: The one allowed enqueuer: (path under `backend/src`, enclosing function).
_ALLOWED = [("app/api/datasets.py", "start_ingestion")]


def _is_ingest_kind(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "DATASET_INGEST"
        and isinstance(node.value, ast.Name)
        and node.value.id == "JobKind"
    ) or (isinstance(node, ast.Constant) and node.value == "dataset.ingest")


def _enqueuers(source: str) -> list[str]:
    """The enclosing function of every call in `source` handed the ingest job kind."""
    found: list[str] = []

    def visit(node: ast.AST, function: str) -> None:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            function = node.name
        if isinstance(node, ast.Call):
            handed = [*node.args, *(keyword.value for keyword in node.keywords)]
            if any(_is_ingest_kind(argument) for argument in handed):
                found.append(function)
        for child in ast.iter_child_nodes(node):
            visit(child, function)

    visit(ast.parse(source), "<module>")
    return found


def _census(root: Path) -> list[tuple[str, str]]:
    return sorted(
        (path.relative_to(root).as_posix(), function)
        for path in root.rglob("*.py")
        for function in _enqueuers(path.read_text(encoding="utf-8"))
    )


@pytest.mark.req("FR-27")
def test_the_ingest_route_is_the_only_enqueuer_of_dataset_ingest_under_backend_src() -> None:
    assert _census(_SRC) == _ALLOWED, (
        "another module enqueues dataset.ingest; the ingest route's ownership check "
        "(blob_readable_by) does not cover it, and the worker has none by design"
    )


@pytest.mark.req("FR-27")
def test_the_census_sees_an_injected_second_enqueuer(tmp_path: Path) -> None:
    """Positive control: the shapes an enqueuer takes are each caught, and only those."""
    (tmp_path / "route.py").write_text(
        "async def start(session):\n"
        "    return await submit(session, JobKind.DATASET_INGEST, {}, None)\n",
        encoding="utf-8",
    )
    (tmp_path / "direct_row.py").write_text(
        "def add(session):\n    session.add(JobRow(kind=JobKind.DATASET_INGEST))\n",
        encoding="utf-8",
    )
    (tmp_path / "by_string.py").write_text(
        "def add(session):\n    submit(session, 'dataset.ingest', {})\n", encoding="utf-8"
    )
    (tmp_path / "registration.py").write_text(
        "def register():\n    for kind, handler in ((JobKind.DATASET_INGEST, _ingest),):\n"
        "        register_handler(kind, handler)\n",
        encoding="utf-8",
    )
    assert _census(tmp_path) == [
        ("by_string.py", "add"),
        ("direct_row.py", "add"),
        ("route.py", "start"),
    ]
