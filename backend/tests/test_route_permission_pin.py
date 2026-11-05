"""The spec's `Permission` cell against what each live route checks (FR-343, RL-1483 item 3).

Every module spec's `§5.1` REST table declares, per route, the permission it requires. This
pin compares that declaration with the live app, **in both directions**:

* a live route with no row, or whose cell differs from what the route checks;
* a row whose route exists and which the live app does not check as declared.

The route side is the `PERMISSION_ATTRIBUTE` of its `requires()` dependency **and**, for a
handler-checked route, the `permission=` argument of `require_permission(` — in the handler
itself, or at the code site `HANDLER_GUARDED` names. `authenticated` matches a route with a
caller and no permission; `open` matches the sweep's `OPEN_BY_DESIGN` set. Unbuilt rows are
declarations only and are read when their route appears.

The declaration is never generated from `requires()` (RL-1483's rejected option (c)): it
would move with the code under test. Rows are read through `model_schema.table_rows`, and
paths are compared as `scripts/audit-docs.py`'s `_path_segments` compares them.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import inspect
import re
import sys
import textwrap
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import cast

import pytest
from backend.tests.test_api_authorisation_sweep import (
    HANDLER_GUARDED,
    OPEN_BY_DESIGN,
    _flattened_operations,
)
from fastapi import FastAPI

from model_schema import Permission
from model_schema.table_rows import endpoint_row, split_row

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "docs" / "specs"
APP_SRC = ROOT / "backend" / "src" / "app"

Key = tuple[str, tuple[str, ...]]

_NAME = re.compile(r"`([a-z_]+:[a-z_]+)`")
_PATH = re.compile(r"`([^`]+)`")
_MEMBERS = {member.name: member.value for member in Permission}

OPEN = "open"
AUTHENTICATED = "authenticated"


def _load_path_segments() -> Callable[[str], tuple[str, ...]]:
    """`audit-docs.py`'s `_path_segments`, loaded by path (the module is hyphenated)."""
    script = ROOT / "scripts" / "audit-docs.py"
    spec = importlib.util.spec_from_file_location("_pin_audit_docs", script)
    assert spec is not None
    assert spec.loader is not None
    module: ModuleType = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
        sys.modules.pop(spec.name, None)
    return cast("Callable[[str], tuple[str, ...]]", module._path_segments)


_segments = _load_path_segments()


def segments(path: str) -> tuple[str, ...]:
    return _segments(path)


# --- the declaration side ----------------------------------------------------------------


@dataclass(frozen=True)
class Declared:
    cell: str
    where: str


def declared_rows(spec_texts: Mapping[str, str]) -> tuple[dict[Key, Declared], list[str]]:
    """Every `§5.1` endpoint row, by `(METHOD, path segments)`, and the rows with no cell.

    A multi-method row (`GET`/`PUT`) is read once per method, though RL-1483 item 1 splits
    them; a row naming several backticked paths is read once per path.
    """
    rows: dict[Key, Declared] = {}
    problems: list[str] = []
    for name, text in spec_texts.items():
        in_section = False
        for number, line in enumerate(text.splitlines(), start=1):
            if line.startswith("### "):
                in_section = line.startswith("### 5.1")
            parsed = endpoint_row(line) if in_section else None
            if parsed is None:
                continue
            method_cell, path_cell = parsed
            cells = split_row(line)
            cell = cells[3] if len(cells) > 3 else ""
            where = f"{name}:{number}"
            if not cell.strip():
                problems.append(f"{where}: no Permission cell: {line[:80]}")
            paths = _PATH.findall(path_cell) or [path_cell]
            for method in re.split(r"`?/`?", method_cell):
                for path in paths:
                    rows[(method, segments(path))] = Declared(cell, where)
    return rows, problems


def claim(cell: str) -> tuple[str, frozenset[str]]:
    """What a cell claims: `open`, `authenticated`, or the permission names it backticks."""
    names = frozenset(_NAME.findall(cell))
    if names:
        return "permissions", names
    if f"`{OPEN}`" in cell:
        return OPEN, frozenset()
    if f"`{AUTHENTICATED}`" in cell:
        return AUTHENTICATED, frozenset()
    return "unreadable", frozenset()


# --- the code side -----------------------------------------------------------------------


@dataclass(frozen=True)
class Checked:
    path: str
    permissions: frozenset[str]
    open: bool


def _dependency_calls(dependant: object) -> Iterable[object]:
    for dependency in getattr(dependant, "dependencies", []):
        yield dependency.call
        yield from _dependency_calls(dependency)


def require_permission_arguments(source: str, lines: frozenset[int] | None = None) -> set[str]:
    """Values of `permission=Permission.X` in every `require_permission(` call of `source`.

    With `lines`, only the calls whose own first line is in the set (a `HANDLER_GUARDED`
    site, `(file, line, needle)`, names the line of the call).
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        callee = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
        if callee != "require_permission" or (lines is not None and node.lineno not in lines):
            continue
        for keyword in node.keywords:
            value = keyword.value
            if keyword.arg == "permission" and isinstance(value, ast.Attribute):
                found.add(_MEMBERS[value.attr])
    return found


def _handler_checks(method: str, path: str, endpoint: object) -> set[str]:
    """Permissions checked by the handler's own body, or at a `HANDLER_GUARDED` site."""
    found: set[str] = set()
    with contextlib.suppress(OSError, TypeError):
        found |= require_permission_arguments(textwrap.dedent(inspect.getsource(endpoint)))
    for file, line, _needle in HANDLER_GUARDED.get((method, path), ()):
        source = (APP_SRC / file).read_text(encoding="utf-8")
        found |= require_permission_arguments(source, frozenset({line, line - 1, line - 2}))
    return found


def checked_routes(app: FastAPI) -> dict[Key, Checked]:
    from app.api.authz import PERMISSION_ATTRIBUTE

    checked: dict[Key, Checked] = {}
    for method, path, route in _flattened_operations(app.routes):
        required = {
            str(getattr(call, PERMISSION_ATTRIBUTE).value)
            for call in _dependency_calls(route.dependant)
            if getattr(call, PERMISSION_ATTRIBUTE, None) is not None
        }
        required |= _handler_checks(method, path, route.endpoint)
        checked[(method, segments(path))] = Checked(
            path, frozenset(required), path in OPEN_BY_DESIGN
        )
    return checked


# --- the comparison ----------------------------------------------------------------------


def pin_violations(declared: Mapping[Key, Declared], checked: Mapping[Key, Checked]) -> list[str]:
    """Each live route against its row. A row with no live route is an unbuilt declaration."""
    violations: list[str] = []
    for key, code in sorted(checked.items()):
        method = key[0]
        row = declared.get(key)
        if row is None:
            violations.append(f"{method} {code.path}: live route with no §5.1 row")
            continue
        kind, names = claim(row.cell)
        if code.open:
            ok = kind == OPEN and not code.permissions
            seen = OPEN
        elif code.permissions:
            ok = kind == "permissions" and names == code.permissions
            seen = ", ".join(sorted(code.permissions))
        else:
            ok = kind == AUTHENTICATED
            seen = AUTHENTICATED
        if not ok:
            violations.append(
                f"{method} {code.path}: spec ({row.where}) says {row.cell!r}; code checks {seen}"
            )
    return violations


def _spec_texts() -> dict[str, str]:
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(SPECS.glob("0*.md"))}


# --- synthetic inputs (red first, CLAUDE.md §13) -----------------------------------------


def _synthetic(cell: str) -> dict[str, str]:
    return {
        "x.md": f"### 5.1 Rest\n\n| Method | Path | Purpose | Permission |\n|---|---|---|---|\n"
        f"| `GET` | `/api/v1/audit?a=b` | read | {cell} |\n"
        f"| `POST` | `/api/v1/things/{{id}}` | write | `dataset:write` |\n"
    }


_CODE = {
    ("GET", segments("/api/v1/audit")): Checked("/api/v1/audit", frozenset({"audit:read"}), False),
    ("POST", segments("/api/v1/things/{x}")): Checked(
        "/api/v1/things/{x}", frozenset({"dataset:write"}), False
    ),
}


def _violations(cell: str, code: Mapping[Key, Checked] = _CODE) -> list[str]:
    rows, _ = declared_rows(_synthetic(cell))
    return pin_violations(rows, code)


def test_control_a_matching_declaration_is_clean() -> None:
    assert _violations("`audit:read`") == []


def test_broken_a_cell_swapped_fails() -> None:
    assert [v for v in _violations("`job:read`") if "GET /api/v1/audit" in v]


def test_broken_a_route_whose_requires_is_swapped_fails() -> None:
    """RL-1483's own case: `ReadAudit` AUDIT_READ -> JOB_READ in the code, the cell unchanged."""
    swapped = {
        **_CODE,
        ("GET", segments("/api/v1/audit")): Checked(
            "/api/v1/audit", frozenset({"job:read"}), False
        ),
    }
    assert [v for v in _violations("`audit:read`", swapped) if "GET /api/v1/audit" in v]


def test_broken_a_live_route_with_no_row_fails() -> None:
    extra = {**_CODE, ("GET", segments("/api/v1/new")): Checked("/api/v1/new", frozenset(), False)}
    assert any("live route with no §5.1 row" in v for v in _violations("`audit:read`", extra))


def test_broken_authenticated_against_a_permissioned_route_fails() -> None:
    assert _violations("`authenticated`")


def test_broken_a_permission_on_a_permission_free_route_fails() -> None:
    free = {
        **_CODE,
        ("GET", segments("/api/v1/audit")): Checked("/api/v1/audit", frozenset(), False),
    }
    assert _violations("`audit:read`", free)
    assert _violations("`authenticated`", free) == []


def test_broken_open_against_a_guarded_route_fails() -> None:
    assert _violations("`open`")


def test_broken_an_empty_cell_is_reported() -> None:
    _, problems = declared_rows(_synthetic(""))
    assert problems


def test_a_handler_check_is_read_from_its_permission_argument() -> None:
    source = (
        "async def f():\n    await rbac.require_permission(s, permission=Permission.JOB_READ)\n"
    )
    assert require_permission_arguments(source) == {"job:read"}
    assert require_permission_arguments(source, frozenset({99})) == set()


# --- the live tree -----------------------------------------------------------------------


@pytest.mark.req("FR-343")
def test_every_row_has_a_permission_cell() -> None:
    _, problems = declared_rows(_spec_texts())
    assert not problems, "\n".join(problems)


@pytest.mark.req("FR-343")
def test_the_spec_declares_what_every_live_route_checks(app: FastAPI) -> None:
    declared, _ = declared_rows(_spec_texts())
    checked = checked_routes(app)
    assert len(checked) >= 50, f"only {len(checked)} live operations walked"
    assert len(declared) >= len(checked) - 5
    violations = pin_violations(declared, checked)
    assert not violations, "\n".join(violations)
