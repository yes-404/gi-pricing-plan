"""The ingest route is the only place under `backend/src` that enqueues `dataset.ingest`.

The worker's ingest handler has no ownership check of its own, by design: `blobs` has no
workspace column, and whether a workspace may read a digest is decided once, at the ingest
route (`api/datasets.py::start_ingestion`, through `blob_readable_by`). That is sound only while
the route is the only enqueuer. A second one, a new internal caller or a second route, would
bypass the check without any test failing, so this test fails the moment one appears; the
worker-side check arrives with an owner record (the upload-completion finding in #869).

The scan is by AST and **fails closed**: it flags every *reference* to the job kind, not only a
call handed it, so `kind = JobKind.DATASET_INGEST` followed by `submit(session, kind, ...)` and
an import alias (`JK.DATASET_INGEST`) are caught as readily as a direct call. A reference is an
attribute whose name is `DATASET_INGEST` (whatever it is read from), or the string
`"dataset.ingest"` or `"DATASET_INGEST"` used as a value. Three sites are allowed, each named
below with what it does: the route, the handler registration, and the kind-to-queue map.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
#: The allowed references: (path under `backend/src`, enclosing function).
_ALLOWED = [
    ("app/api/datasets.py", "start_ingestion"),  # the only enqueuer
    ("app/platform/jobs.py", "<module>"),  # the kind-to-queue map
    ("app/worker/data_handlers.py", "register_data_handlers"),  # registers the handler
]


def _is_reference(node: ast.AST) -> bool:
    if isinstance(node, ast.Attribute):
        return node.attr == "DATASET_INGEST"
    return isinstance(node, ast.Constant) and node.value in ("dataset.ingest", "DATASET_INGEST")


def _references(source: str) -> list[str]:
    """The enclosing function of every reference to the ingest job kind in `source`."""
    found: list[str] = []

    def visit(node: ast.AST, function: str) -> None:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            function = node.name
        if _is_reference(node):
            found.append(function)
        for child in ast.iter_child_nodes(node):
            visit(child, function)

    visit(ast.parse(source), "<module>")
    return found


def _census(root: Path) -> list[tuple[str, str]]:
    return sorted(
        (path.relative_to(root).as_posix(), function)
        for path in root.rglob("*.py")
        for function in _references(path.read_text(encoding="utf-8"))
    )


@pytest.mark.req("FR-27")
def test_the_ingest_route_is_the_only_enqueuer_of_dataset_ingest_under_backend_src() -> None:
    assert _census(_SRC) == sorted(_ALLOWED), (
        "another module refers to the dataset.ingest job kind; if it enqueues, the ingest "
        "route's ownership check (blob_readable_by) does not cover it, and the worker has "
        "none by design"
    )


@pytest.mark.req("FR-27")
def test_the_census_sees_an_injected_second_enqueuer(tmp_path: Path) -> None:
    """Positive control: each shape a reference takes is caught, including the aliased ones."""
    files = {
        "route.py": (
            "async def start(session):\n"
            "    return await submit(session, JobKind.DATASET_INGEST, {}, None)\n"
        ),
        "direct_row.py": (
            "def add(session):\n    session.add(JobRow(kind=JobKind.DATASET_INGEST))\n"
        ),
        "by_string.py": "def add(session):\n    submit(session, 'dataset.ingest', {})\n",
        "registration.py": (
            "def register():\n    for kind, handler in ((JobKind.DATASET_INGEST, _ingest),):\n"
            "        register_handler(kind, handler)\n"
        ),
        "alias_assign.py": (
            "async def start(session):\n    kind = JobKind.DATASET_INGEST\n"
            "    return await submit(session, kind, {})\n"
        ),
        "alias_import.py": (
            "from model_schema import JobKind as JK\n\n\n"
            "async def start(session):\n    return await submit(session, JK.DATASET_INGEST, {})\n"
        ),
        "by_member_name.py": "def add():\n    return getattr(JobKind, 'DATASET_INGEST')\n",
        "clean.py": "def add(session):\n    submit(session, JobKind.DATASET_VALIDATE, {})\n",
    }
    for name, text in files.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    assert _census(tmp_path) == [
        ("alias_assign.py", "start"),
        ("alias_import.py", "start"),
        ("by_member_name.py", "add"),
        ("by_string.py", "add"),
        ("direct_row.py", "add"),
        ("registration.py", "register"),
        ("route.py", "start"),
    ]
