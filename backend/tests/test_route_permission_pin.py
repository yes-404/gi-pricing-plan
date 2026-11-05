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
import importlib.util
import inspect
import re
import sys
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


def _checks_in(node: ast.AST, lines: frozenset[int] | None = None) -> set[str]:
    """Values of `permission=Permission.X` in every `require_permission(` call under `node`.

    With `lines`, only the calls whose own first line is in the set (a `HANDLER_GUARDED`
    site, `(file, line, needle)`, names the line of the call).
    """
    found: set[str] = set()
    for call in ast.walk(node):
        if not isinstance(call, ast.Call):
            continue
        func = call.func
        callee = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
        if callee != "require_permission" or (lines is not None and call.lineno not in lines):
            continue
        for keyword in call.keywords:
            value = keyword.value
            if keyword.arg == "permission" and isinstance(value, ast.Attribute):
                found.add(_MEMBERS[value.attr])
    return found


def require_permission_arguments(source: str, lines: frozenset[int] | None = None) -> set[str]:
    return _checks_in(ast.parse(source), lines)


def _module_functions(tree: ast.Module) -> dict[str, ast.AST]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    }


def handler_checks(module_source: str, handler: str) -> set[str]:
    """What a handler checks: in its own body, and in the functions it calls that are
    **defined in the same module** (ONE level: the helper's own callees are not followed, and
    a function of another module is not read; lead's ruling, 2026-11-05 16:11:02 GMT).
    A callee is followed by what the call reaches, never by its name.
    """
    functions = _module_functions(ast.parse(module_source))
    body = functions.get(handler)
    if body is None:  # a handler built inside a factory: nothing at module level to read
        return set()
    found = _checks_in(body)
    for call in ast.walk(body):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
            callee = functions.get(call.func.id)
            if callee is not None and call.func.id != handler:
                found |= _checks_in(callee)
    return found


#: Routes whose cell names a resource condition beyond a permission, each with the service
#: function that holds it. ONE entry (the lead's ruling, 2026-11-05 16:11:02 GMT, FR-82):
#: `PATCH /datasets/{dataset_id}` is gated on `dataset:read` by `requires()`, and
#: `set_owner` applies "Admin, or the current owner". A new entry is a visible diff:
#: `test_the_named_list_is_exactly_one_entry` asserts the whole mapping.
NAMED_CONDITIONS: dict[tuple[str, str], tuple[str, str]] = {
    ("PATCH", "/api/v1/datasets/{dataset_id}"): ("platform/datasets.py", "set_owner"),
}


def named_condition_checks(source: str, function: str) -> set[str]:
    """`{admin:manage_roles}` if `function` holds BOTH limbs of FR-82 and raises, else empty.

    Both limbs (`is_owner` and `ADMIN_MANAGE_ROLES`) must sit in the test of one `if` whose body
    raises; a function that lost either, or no longer raises, proves nothing and the row stays red.
    """
    body = _module_functions(ast.parse(source)).get(function)
    if body is None:
        return set()
    assigned = any(
        isinstance(n, ast.Name) and n.id == "is_owner" and isinstance(n.ctx, ast.Store)
        for n in ast.walk(body)
    )
    for branch in ast.walk(body):
        if not assigned or not isinstance(branch, ast.If):
            continue
        test = list(ast.walk(branch.test))
        owner = any(isinstance(n, ast.Name) and n.id == "is_owner" for n in test)
        admin = any(isinstance(n, ast.Attribute) and n.attr == "ADMIN_MANAGE_ROLES" for n in test)
        raises = any(isinstance(n, ast.Raise) for stmt in branch.body for n in ast.walk(stmt))
        if owner and admin and raises:
            return {Permission.ADMIN_MANAGE_ROLES.value}
    return set()


def _handler_checks(method: str, path: str, endpoint: Callable[..., object]) -> set[str]:
    """Permissions checked in the handler, one level below it, at a `HANDLER_GUARDED` site, or
    by a `NAMED_CONDITIONS` service function."""
    found: set[str] = set()
    file = inspect.getsourcefile(endpoint)
    if file is not None:
        found |= handler_checks(Path(file).read_text(encoding="utf-8"), endpoint.__name__)
    for site, line, _needle in HANDLER_GUARDED.get((method, path), ()):
        source = (APP_SRC / site).read_text(encoding="utf-8")
        found |= require_permission_arguments(source, frozenset({line, line - 1, line - 2}))
    if (method, path) in NAMED_CONDITIONS:
        site, function = NAMED_CONDITIONS[(method, path)]
        found |= named_condition_checks((APP_SRC / site).read_text(encoding="utf-8"), function)
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


_HELPER = """
async def _guard(c):
    await rbac.require_permission(s, permission=Permission.DATASET_READ)

async def _deeper(c):
    await _guard(c)

async def handler(c):
    await {call}(c)
"""


def test_the_walk_follows_a_same_module_helper_one_level() -> None:
    assert handler_checks(_HELPER.format(call="_guard"), "handler") == {"dataset:read"}


def test_broken_the_helper_without_the_check_proves_nothing() -> None:
    source = _HELPER.format(call="_guard").replace("require_permission", "log")
    assert handler_checks(source, "handler") == set()


def test_broken_the_walk_stops_at_one_level() -> None:
    assert handler_checks(_HELPER.format(call="_deeper"), "handler") == set()


def test_broken_the_walk_does_not_read_another_module() -> None:
    source = "async def handler(c):\n    await other.guard(c)\n    await imported_guard(c)\n"
    assert handler_checks(source, "handler") == set()


_SET_OWNER = """
async def set_owner(actor, row):
    is_owner = actor.id == row.owner_id
    if not is_owner and not await has_permission(permission=Permission.ADMIN_MANAGE_ROLES):
        raise PlatformError("PERMISSION_DENIED")
"""


def test_the_named_condition_holds_with_both_limbs_and_a_raise() -> None:
    assert named_condition_checks(_SET_OWNER, "set_owner") == {"admin:manage_roles"}


@pytest.mark.parametrize(
    "removed",
    [
        ("is_owner = actor.id == row.owner_id", "is_o = actor.id == row.owner_id"),
        ("not is_owner and ", ""),
        ("ADMIN_MANAGE_ROLES", "DATASET_READ"),
        ('raise PlatformError("PERMISSION_DENIED")', "pass"),
    ],
)
def test_broken_a_named_condition_that_lost_a_limb_proves_nothing(removed: tuple[str, str]) -> None:
    broken = _SET_OWNER.replace(*removed)
    assert broken != _SET_OWNER
    assert named_condition_checks(broken, "set_owner") == set()


def test_the_named_list_is_exactly_one_entry() -> None:
    assert NAMED_CONDITIONS == {
        ("PATCH", "/api/v1/datasets/{dataset_id}"): ("platform/datasets.py", "set_owner")
    }


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
