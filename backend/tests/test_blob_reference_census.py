"""FR-420's precondition, derived rather than listed: every blob row has one writer, and the
writer takes the reference.

`BlobStore.put` takes one reference for its caller (`07` FR-418's 2026-11-14 clause). That makes
"every blob owner holds a reference" a property of the one function that creates rows, and this
census holds the property in place: it walks the AST of every source file, so a second writer, a
manual `retain` after a `put`, or a direct write to `ref_count` outside `blobs.py` fails here
rather than leaking or double-counting a reference in production. No database is needed.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = (REPO / "backend" / "src", *sorted((REPO / "packages").glob("*/src")))
BLOBS_MODULE = REPO / "backend" / "src" / "app" / "platform" / "blobs.py"

# The only functions that may create a `blobs` row, both on `BlobStore`.
WRITERS = frozenset({"put", "promote_upload"})

# `{"<file relative to the repo>:<function>": "reason"}` for a `retain` that follows a `put` in
# one function body on purpose. Empty: `put` takes the reference, so none is expected.
ALLOWED: dict[str, str] = {}

_SQL_WRITE = re.compile(r"\b(update\s+blobs|insert\s+into\s+blobs|delete\s+from\s+blobs)\b", re.I)
# Receivers whose `.put(` is `BlobStore.put` (`blob_store`, `progress.blob_store`, ...).
_STORE_NAMES = frozenset({"blob_store", "store", "blobs", "blob"})
_WRITE_CALLS = frozenset({"insert", "pg_insert", "update", "delete", "BlobRow"})


def _name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _functions(tree: ast.Module) -> list[tuple[str, ast.AST]]:
    return [
        (node.name, node)
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    ]


def _rel(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def _writes_blobs_directly(node: ast.AST) -> bool:
    """A write to `blobs` that is not through `BlobStore`: a row call, `ref_count =`, or raw SQL."""
    if isinstance(node, ast.Call) and _name(node.func) in _WRITE_CALLS:
        return _name(node.func) == "BlobRow" or any(
            _name(a) == "BlobRow" for a in node.args if isinstance(a, ast.expr)
        )
    if isinstance(node, ast.Attribute):
        return node.attr == "ref_count" and isinstance(node.ctx, ast.Store)
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and _SQL_WRITE.search(node.value) is not None
    )


def scan(roots: tuple[Path, ...], repo: Path, blobs_module: Path) -> dict[str, list[str]]:
    """The violations of each of the three checks, over every `.py` file under `roots`."""
    found: dict[str, list[str]] = {"writer": [], "retain_after_put": [], "outside_blobs": []}
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            rel = _rel(path, repo)
            is_blobs = path == blobs_module

            # (a) a `blobs` row is created only inside `BlobStore.put` / `promote_upload`.
            for fname, fn in _functions(tree):
                for call in (n for n in ast.walk(fn) if isinstance(n, ast.Call)):
                    names = {_name(call.func)} | {
                        _name(a) for a in call.args if isinstance(a, ast.expr)
                    }
                    creates = (_name(call.func) == "BlobRow") or (
                        _name(call.func) in {"insert", "pg_insert"} and "BlobRow" in names
                    )
                    if creates and not (is_blobs and fname in WRITERS):
                        found["writer"].append(f"{rel}:{call.lineno} in {fname}")

                # (b) no `retain` after a `.put(` in one function body.
                puts = [
                    c.lineno
                    for c in ast.walk(fn)
                    if isinstance(c, ast.Call)
                    and isinstance(c.func, ast.Attribute)
                    and c.func.attr == "put"
                    and _name(c.func.value) in _STORE_NAMES
                ]
                retains = [
                    c.lineno
                    for c in ast.walk(fn)
                    if isinstance(c, ast.Call) and _name(c.func) == "retain"
                ]
                if puts and any(r > min(puts) for r in retains) and f"{rel}:{fname}" not in ALLOWED:
                    found["retain_after_put"].append(f"{rel}:{fname}")

            # (c) outside `blobs.py`, nothing writes `blobs` rows or `ref_count` directly.
            if not is_blobs:
                found["outside_blobs"] += [
                    f"{rel}:{node.lineno}"
                    for node in ast.walk(tree)
                    if _writes_blobs_directly(node)
                ]
    return {check: sorted(set(hits)) for check, hits in found.items()}


@pytest.mark.req("FR-420")
def test_the_source_tree_has_one_blob_writer_and_no_retain_after_a_put() -> None:
    found = scan(SOURCE_ROOTS, REPO, BLOBS_MODULE)
    assert found == {"writer": [], "retain_after_put": [], "outside_blobs": []}


@pytest.mark.req("FR-420")
def test_the_census_finds_the_two_writers_it_permits() -> None:
    """Positive control: the walker sees `put` and `promote_upload`, so an empty result above
    is not a walker that reaches nothing."""
    tree = ast.parse(BLOBS_MODULE.read_text(encoding="utf-8"))
    creators = {
        name
        for name, fn in _functions(tree)
        for call in ast.walk(fn)
        if isinstance(call, ast.Call)
        and (
            _name(call.func) == "BlobRow"
            or (
                _name(call.func) in {"insert", "pg_insert"}
                and any(_name(a) == "BlobRow" for a in call.args)
            )
        )
    }
    assert creators == WRITERS


def _plant(tmp_path: Path, body: str) -> dict[str, list[str]]:
    root = tmp_path / "src"
    root.mkdir()
    (root / "planted.py").write_text(body, encoding="utf-8")
    (root / "blobs.py").write_text("", encoding="utf-8")
    return scan((root,), tmp_path, root / "blobs.py")


@pytest.mark.req("FR-420")
def test_a_stray_blob_row_constructor_is_found(tmp_path: Path) -> None:
    found = _plant(tmp_path, "def f(session):\n    session.add(BlobRow(sha256='x'))\n")
    assert found["writer"]
    assert found["outside_blobs"]


@pytest.mark.req("FR-420")
def test_a_stray_insert_into_blobs_is_found(tmp_path: Path) -> None:
    found = _plant(
        tmp_path, "def f(session):\n    session.execute(pg_insert(BlobRow).values(a=1))\n"
    )
    assert found["writer"]
    assert found["outside_blobs"]


@pytest.mark.req("FR-420")
def test_a_retain_after_a_put_is_found(tmp_path: Path) -> None:
    body = (
        "async def f(session, blob_store):\n"
        "    ref = await blob_store.put(session, b'x', 'text/plain')\n"
        "    await blobs.retain(session, ref.sha256)\n"
    )
    assert _plant(tmp_path, body)["retain_after_put"] == ["src/planted.py:f"]


@pytest.mark.req("FR-420")
def test_a_direct_ref_count_write_is_found(tmp_path: Path) -> None:
    found = _plant(
        tmp_path,
        "def f(row):\n    row.ref_count = 0\n    q = 'UPDATE blobs SET ref_count = 0'\n",
    )
    assert len(found["outside_blobs"]) == 2
