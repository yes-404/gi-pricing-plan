"""FR-420, #1855 (iv): every writer of a blob owner place takes a reference, and the test holds it.

The collector's safety rests on the reference count: a blob with `ref_count` > 0 is never collected.
That holds only if every function that writes an owner row (a place in `BLOB_OWNERS` that names a
digest) takes a reference to that digest in its own transaction, with `put`, `retain` or
`promote_upload`, so a writer that follows the rule waits on the row lock the collector holds and
never commits an owner row for a blob the collector is deleting.

`OWNER_WRITERS` (in `blobs.py`) names, for each owner place, the functions that write it and how
each takes its reference. This test is the census:

1. the registry covers exactly the owner places (a new `BlobOwner` with no writers fails here);
2. every registered function exists, and takes its reference as it says (the AST of its body calls
   `put`, `retain` or `promote_upload`, or the helper it names does);
3. every function under `backend/src`, `scripts` and `examples` that writes an owner column is
   registered. A writer nobody listed fails here, by name.

The search is the AST walk below: assignments to an owner column (`row.bundle = …`) and
constructor keywords (`ScoringTraceRow(blob_sha256=…)`). Pure AST, no database.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.platform.blobs import BLOB_OWNERS, OWNER_WRITERS

REPO = Path(__file__).resolve().parents[2]
ROOTS = (REPO / "backend" / "src", REPO / "scripts", REPO / "examples")

#: Attribute assignments that write an owner column, by attribute name.
ATTRIBUTES = frozenset(
    {"tables", "fit_result", "cells", "bundle", "evidence", "cases_blob_sha256",
     "movers_blob_sha256", "blob_sha256", "sha256"}
)
#: Attribute names that count only in one file (`result` is a column of `jobs` and a common word).
FILE_ATTRIBUTES = {"backend/src/app/platform/jobs.py": frozenset({"result"})}
#: Row constructors and the keyword that names a digest on each.
CONSTRUCTORS = {
    "DatasetVersionRow": frozenset({"tables"}),
    "ModelRow": frozenset({"fit_result"}),
    "RateTableVersionRow": frozenset({"cells"}),
    "RatingVersionRow": frozenset({"bundle", "evidence"}),
    "RegressionRunRow": frozenset({"cases_blob_sha256"}),
    "DislocationRunRow": frozenset({"movers_blob_sha256"}),
    "ScoringTraceRow": frozenset({"blob_sha256"}),
    "BlobUploadRow": frozenset({"sha256"}),
}
TAKES = frozenset({"put", "retain", "promote_upload"})
#: Functions that match the detector and are not writes of an owner place, each with its reason.
NOT_OWNER_WRITES: dict[str, str] = {}


def _py_files() -> list[Path]:
    return sorted(p for root in ROOTS if root.is_dir() for p in root.rglob("*.py"))


def _name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _functions(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [fn for _, fn in _qualified(tree)]


def _qualified(tree: ast.AST) -> list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    """Every function with its qualified name (`_derive.work` for a function nested in `_derive`,
    `BlobStore.put` for a method), so two nested functions both called `work` stay apart."""
    out: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                qualified = prefix + child.name
                out.append((qualified, child))
                visit(child, qualified + ".")
            elif isinstance(child, ast.ClassDef):
                visit(child, prefix + child.name + ".")
            else:
                visit(child, prefix)

    visit(tree, "")
    return out


def _own_nodes(fn: ast.AST) -> list[ast.AST]:
    """The nodes of `fn` that are not inside a nested function (those belong to that function)."""
    out: list[ast.AST] = []
    stack = list(ast.iter_child_nodes(fn))
    while stack:
        node = stack.pop()
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
            continue
        out.append(node)
        stack.extend(ast.iter_child_nodes(node))
    return out


def _calls(fn: ast.AST) -> set[str]:
    return {
        n
        for node in _own_nodes(fn)
        if isinstance(node, ast.Call) and (n := _name(node.func)) is not None
    }


def _writes_an_owner_column(fn: ast.AST, rel: str) -> bool:
    attrs = ATTRIBUTES | FILE_ATTRIBUTES.get(rel, frozenset())
    for node in _own_nodes(fn):
        if isinstance(node, ast.Assign | ast.AnnAssign | ast.AugAssign):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Attribute) and t.attr in attrs for t in targets):
                return True
        if isinstance(node, ast.Call):
            wanted = CONSTRUCTORS.get(_name(node.func) or "")
            if wanted and any(kw.arg in wanted for kw in node.keywords):
                return True
    return False


def _walk() -> dict[str, dict[str, ast.AST]]:
    """`{file relative to the repo: {function name: its node}}` for every source file."""
    found: dict[str, dict[str, ast.AST]] = {}
    for path in _py_files():
        rel = path.relative_to(REPO).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found[rel] = dict(_qualified(tree))
    return found


def _registered() -> dict[str, str]:
    """`{file::function: owner place}` over the whole registry."""
    return {
        f"{writer.file}::{writer.function}": owner
        for owner, writers in OWNER_WRITERS.items()
        for writer in writers
    }


@pytest.mark.req("FR-420")
def test_the_registry_covers_exactly_the_owner_places() -> None:
    assert set(OWNER_WRITERS) == {owner.name for owner in BLOB_OWNERS}
    # A place with no writer under this tree (an owner no code here writes) must say so.
    for owner, writers in OWNER_WRITERS.items():
        assert writers, f"{owner}: no writer listed; list its writers or say it has none"


@pytest.mark.req("FR-420")
def test_every_registered_writer_exists_and_takes_its_reference() -> None:
    tree = _walk()
    problems: list[str] = []
    for owner, writers in OWNER_WRITERS.items():
        for writer in writers:
            functions = tree.get(writer.file)
            if functions is None or writer.function not in functions:
                problems.append(f"{owner}: {writer.file}::{writer.function} does not exist")
                continue
            if writer.takes in TAKES:
                if writer.takes not in _calls(functions[writer.function]):
                    problems.append(
                        f"{owner}: {writer.file}::{writer.function} says it takes its reference "
                        f"with {writer.takes}() and its body never calls it"
                    )
            elif writer.via:
                # `via` is a function in the same file, or `file::function` in another.
                via_file, _, via_name = writer.via.rpartition("::")
                helper = (tree.get(via_file) if via_file else functions) or {}
                helper_fn = helper.get(via_name)
                if helper_fn is None or not (TAKES & _calls(helper_fn)):
                    problems.append(
                        f"{owner}: {writer.file}::{writer.function} names {writer.via} as the "
                        "function that takes the reference, and it takes none"
                    )
            elif not writer.reason:
                problems.append(f"{owner}: {writer.file}::{writer.function} gives no reason")
    assert problems == []


@pytest.mark.req("FR-420")
def test_every_function_that_writes_an_owner_column_is_registered() -> None:
    tree = _walk()
    registered = set(_registered()) | set(NOT_OWNER_WRITES)
    unlisted = sorted(
        f"{rel}::{name}"
        for rel, functions in tree.items()
        for name, fn in functions.items()
        if _writes_an_owner_column(fn, rel) and f"{rel}::{name}" not in registered
    )
    assert unlisted == [], (
        "a function writes an owner column and is not in OWNER_WRITERS: list it with how it takes "
        "its reference, or fix it to take one"
    )


@pytest.mark.req("FR-420")
def test_a_fit_result_naming_another_digest_than_the_one_stored_is_refused() -> None:
    """The gap the census found: `record_fit` stored the `BlobRef` `pricing-core` computed and
    nothing checked it against the bytes `put` stored. The check refuses a difference before the
    model row is written, and the fit handler makes it after each of its two puts."""
    from app.errors import PlatformError
    from app.worker.model_handlers import _assert_stored_the_named_digest

    _assert_stored_the_named_digest("a" * 64, "a" * 64)
    with pytest.raises(PlatformError) as raised:
        _assert_stored_the_named_digest("a" * 64, "b" * 64)
    assert raised.value.code == "BLOB_REFERENCE_INVARIANT_BREACHED"

    store = _walk()["backend/src/app/worker/model_handlers.py"]["_fit.store"]
    checks = [
        node
        for node in _own_nodes(store)
        if isinstance(node, ast.Call) and _name(node.func) == "_assert_stored_the_named_digest"
    ]
    assert len(checks) == 2  # the booster and the covariance


@pytest.mark.req("FR-420")
def test_the_census_sees_a_planted_writer_that_takes_no_reference() -> None:
    """Positive control: the detector flags a function that assigns an owner column, and the
    reference check flags it when its body never calls put, retain or promote_upload."""
    source = (
        "async def planted(session, row, digest):\n"
        "    row.blob_sha256 = digest\n"
    )
    fn = _functions(ast.parse(source))[0]
    assert _writes_an_owner_column(fn, "backend/src/app/planted.py")
    assert not (TAKES & _calls(fn))
