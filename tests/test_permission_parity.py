"""The permission-parity check: `06` §4.1 against `model_schema.Permission` (RL-1305).

The names are the enum's (ADR-704, CLAUDE.md §2). `06` §4.1 states what each one means. A new
permission lands in one commit: the `06` row, the enum member and the check. Each class
below is proved red on a synthetic input before the live tree is asserted clean (CLAUDE.md §13).
"""

from __future__ import annotations

import ast
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import pytest
from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute, APIRouter, iter_route_contexts

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "specs" / "06-governance.md"

BUILT_HEADER = "| Permission | Governs | Check owner |"
SPECIFIED_HEADER = "| Permission | Owner Work |"
ALIAS_HEADER = "| Name used before | Enum name |"

ENUM_WITHOUT_ROW = "enum member with no 06 §4.1 Built row"
ROW_WITHOUT_ENUM = "06 §4.1 Built row with no enum member"
SPECIFIED_IS_MEMBER = "Specified name is an enum member: move its row to Built in the same commit"
OWNER_UNRESOLVED = "owner is not a WK- heading in docs/roadmap.md"
ALIAS_TARGET_NOT_MEMBER = "alias target is not an enum member"
STRAY_TOKEN = "06 names a permission that is in no §4.1 table"
NO_CHECK_NO_OWNER = "Built name has no check site in backend/src and no owner"
STALE_OWNER = "Built name has a check site and still carries an owner: clear it in the same commit"
DUPLICATE_ROW = "name appears in more than one §4.1 table"

# RL-1236's whole-06 predicate, and its two exclusions.
_TOKEN = re.compile(r"\b[a-z][a-z_]*:(?:[a-z_]+\b|deploy_\*)")
_NOT_A_PERMISSION = re.compile(r":motor$|^type:name$")
_STRUCK = re.compile(r"~~.*?~~", re.DOTALL)
_ROW_NAME = re.compile(r"^`([a-z_]+:[a-z_*]+)`$")
_WORK = re.compile(r"\bWK-\d+\b")


def _section_4_1(text: str) -> str:
    start = text.index("\n### 4.1 ")
    return text[start : text.index("\n### 4.2 ", start)]


def _table(section: str, header: str) -> list[list[str]]:
    """Rows of the table whose header row is `header`, with any `> ` quote prefix removed."""
    lines = [line.removeprefix("> ").removeprefix(">").strip() for line in section.splitlines()]
    try:
        at = lines.index(header)
    except ValueError:
        return []
    rows: list[list[str]] = []
    for line in lines[at + 2 :]:  # skip the header and the |---| line
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def _name(cell: str) -> str:
    match = _ROW_NAME.match(cell)
    assert match, f"not a backticked permission name: {cell!r}"
    return match.group(1)


def _owner(cell: str) -> str | None:
    """The owning Work id in an owner cell ("WK-674 Slice 2" -> "WK-674"), else the raw text."""
    cell = cell.strip("`* ")
    match = _WORK.search(cell)
    return match.group(0) if match else (cell or None)


@dataclass(frozen=True)
class Catalogue:
    built: dict[str, str | None]
    specified: dict[str, str]
    aliases: dict[str, str]
    stray: frozenset[str]
    duplicates: frozenset[str]


def extract_catalogue(spec_text: str) -> Catalogue:
    section = _section_4_1(spec_text)
    built = {_name(r[0]): _owner(r[2]) for r in _table(section, BUILT_HEADER)}
    specified = {_name(r[0]): _owner(r[1]) or "" for r in _table(section, SPECIFIED_HEADER)}
    aliases = {_name(r[0]): _name(r[1]) for r in _table(section, ALIAS_HEADER)}
    tables = [set(built), set(specified), set(aliases)]
    every = set(built) | set(specified) | set(aliases)
    duplicates = frozenset(n for n in every if sum(n in t for t in tables) > 1)
    tokens = {
        t for t in _TOKEN.findall(_STRUCK.sub("", spec_text)) if not _NOT_A_PERMISSION.search(t)
    }
    # An alias target that is not a member is reported once, by its own class, not as stray.
    stray = frozenset(tokens - every - set(aliases.values()))
    return Catalogue(built, specified, aliases, stray, duplicates)


def parity_violations(
    spec_text: str,
    enum_values: frozenset[str],
    checked: frozenset[str],
    works: frozenset[str],
) -> list[str]:
    cat = extract_catalogue(spec_text)
    out: list[str] = []
    out += [f"{ENUM_WITHOUT_ROW}: {n}" for n in sorted(enum_values - set(cat.built))]
    out += [f"{ROW_WITHOUT_ENUM}: {n}" for n in sorted(set(cat.built) - enum_values)]
    out += [f"{SPECIFIED_IS_MEMBER}: {n}" for n in sorted(set(cat.specified) & enum_values)]
    owners = {n: o for n, o in cat.built.items() if o} | cat.specified
    out += [
        f"{OWNER_UNRESOLVED}: {n} -> {o!r}" for n, o in sorted(owners.items()) if o not in works
    ]
    out += [
        f"{ALIAS_TARGET_NOT_MEMBER}: {a} -> {t}"
        for a, t in sorted(cat.aliases.items())
        if t not in enum_values
    ]
    out += [f"{STRAY_TOKEN}: {n}" for n in sorted(cat.stray)]
    out += [f"{DUPLICATE_ROW}: {n}" for n in sorted(cat.duplicates)]
    for name, owner in sorted(cat.built.items()):
        if name not in enum_values:
            continue
        if name not in checked and owner is None:
            out.append(f"{NO_CHECK_NO_OWNER}: {name}")
        if name in checked and owner is not None:
            out.append(f"{STALE_OWNER}: {name} ({owner})")
    return out


# --- synthetic inputs -------------------------------------------------------------------

_WORKS = frozenset({"WK-674", "WK-690"})


def _spec(built: str, specified: str = "", aliases: str = "", prose: str = "") -> str:
    return (
        "# 06\n\n" + prose + "\n\n### 4.1 `Permission`\n\n"
        f"{BUILT_HEADER}\n|---|---|---|\n{built}\n\n"
        f"{SPECIFIED_HEADER}\n|---|---|\n{specified}\n\n"
        f"{ALIAS_HEADER}\n|---|---|\n{aliases}\n\n"
        "### 4.2 `ApprovalPolicy`\n"
    )


_CLEAN = _spec(
    built="| `a:read` | Reading A |  |\n| `a:deploy` | Deploying A | WK-674 |",
    specified="| `a:author` | WK-690 |",
    aliases="| `a:ship` | `a:deploy` |",
    prose="Reading needs `a:read`; the old ~~`a:legacy`~~ name is struck.",
)
_ENUM = frozenset({"a:read", "a:deploy"})
_CHECKED = frozenset({"a:read"})


def _only(violations: list[str], *prefixes: str) -> None:
    """Exactly one message per named class, and no other: a right count with a wrong class fails."""
    assert len(violations) == len(prefixes), violations
    for prefix in prefixes:
        assert sum(v.startswith(prefix + ": ") for v in violations) == 1, (prefix, violations)


@pytest.mark.req("FR-344")
def test_clean_control_has_no_violations() -> None:
    assert parity_violations(_CLEAN, _ENUM, _CHECKED, _WORKS) == []


@pytest.mark.req("FR-344")
def test_broken_enum_member_without_a_row() -> None:
    _only(parity_violations(_CLEAN, _ENUM | {"a:write"}, _CHECKED, _WORKS), ENUM_WITHOUT_ROW)


@pytest.mark.req("FR-344")
def test_broken_row_without_an_enum_member() -> None:
    extra = "| `a:read` | Reading A |  |\n| `a:gone` | Gone | WK-674 |"
    spec = _CLEAN.replace("| `a:read` | Reading A |  |", extra)
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), ROW_WITHOUT_ENUM)


@pytest.mark.req("FR-367")
def test_broken_specified_name_that_is_already_a_member() -> None:
    # An enum member that is still Specified also has no Built row: both messages are right.
    violations = parity_violations(_CLEAN, _ENUM | {"a:author"}, _CHECKED, _WORKS)
    _only(violations, SPECIFIED_IS_MEMBER, ENUM_WITHOUT_ROW)


@pytest.mark.req("FR-344")
def test_broken_owner_that_is_not_a_work() -> None:
    spec = _CLEAN.replace("| `a:author` | WK-690 |", "| `a:author` | WK-9 |")
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), OWNER_UNRESOLVED)


@pytest.mark.req("FR-344")
def test_broken_alias_to_a_non_member() -> None:
    spec = _CLEAN.replace("| `a:ship` | `a:deploy` |", "| `a:ship` | `a:send` |")
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), ALIAS_TARGET_NOT_MEMBER)


@pytest.mark.req("FR-344")
def test_broken_stray_token_in_prose() -> None:
    spec = _CLEAN.replace("Reading needs `a:read`;", "Reading needs `a:read` or `a:peek`;")
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), STRAY_TOKEN)


@pytest.mark.req("FR-343")
def test_broken_built_name_with_no_check_and_no_owner() -> None:
    old, new = "| `a:deploy` | Deploying A | WK-674 |", "| `a:deploy` | Deploying A |  |"
    spec = _CLEAN.replace(old, new)
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), NO_CHECK_NO_OWNER)


@pytest.mark.req("FR-343")
def test_broken_stale_owner_after_the_check_lands() -> None:
    _only(parity_violations(_CLEAN, _ENUM, _CHECKED | {"a:deploy"}, _WORKS), STALE_OWNER)


@pytest.mark.req("FR-344")
def test_broken_name_in_two_tables() -> None:
    extra = "| `a:author` | WK-690 |\n| `a:read` | WK-690 |"
    spec = _CLEAN.replace("| `a:author` | WK-690 |", extra)
    # `a:read` is Built and Specified, so it is also a Specified enum member: both are right.
    _only(parity_violations(spec, _ENUM, _CHECKED, _WORKS), DUPLICATE_ROW, SPECIFIED_IS_MEMBER)


def _roadmap_works() -> frozenset[str]:
    text = (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
    return frozenset(re.findall(r"^### (WK-\d+)\b", text, re.MULTILINE))


@pytest.mark.req("FR-344")
def test_live_tree_has_no_parity_violations() -> None:
    from model_schema import Permission

    violations = parity_violations(
        SPEC.read_text(encoding="utf-8"),
        frozenset(p.value for p in Permission),
        checked_permissions(),
        _roadmap_works(),
    )
    assert not violations, "permission parity (CR-1247 P1 (c)):\n" + "\n".join(violations)


BACKEND_SRC = ROOT / "backend" / "src"
#: The one service-layer check function (`backend/src/app/platform/rbac.py`); `requires()`
#: is one of its callers (`backend/src/app/api/authz.py`). RL-1305 D1 item 3.
CHECK_FUNCTION = "require_permission"
REACH_SHORTFALL = "route walk did not reach a published path"


def service_layer_checks(sources: Iterable[str], members: Mapping[str, str]) -> frozenset[str]:
    """Members passed as `permission=` to a `require_permission(` call (RL-1305 D1 item 2).

    `members` maps an enum attribute name to its value. The enum's local name is resolved
    through each module's own `from model_schema import Permission [as X]`, so an alias is
    followed and a bare reference elsewhere (a role set, an allow-list, a comparison) is not
    a check site.
    """
    found: set[str] = set()
    for source in sources:
        tree = ast.parse(source)
        local = {
            alias.asname or alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module == "model_schema"
            for alias in node.names
            if alias.name == "Permission"
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            callee = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            if callee != CHECK_FUNCTION:
                continue
            for kw in node.keywords:
                value = kw.value
                if (
                    kw.arg == "permission"
                    and isinstance(value, ast.Attribute)
                    and isinstance(value.value, ast.Name)
                    and value.value.id in local
                    and value.attr in members
                ):
                    found.add(members[value.attr])
    return frozenset(found)


def walk_api_routes(app: FastAPI) -> list[tuple[str, APIRoute]]:
    """Every API route with its full path, included routers flattened (RL-1305 D1 item 2)."""
    return [
        (str(context.path), context.original_route)
        for context in iter_route_contexts(app.routes)
        if isinstance(context.original_route, APIRoute)
    ]


def route_checks(
    app: FastAPI,
    attribute: str,
    walk: Callable[[FastAPI], list[tuple[str, APIRoute]]] = walk_api_routes,
) -> tuple[frozenset[str], list[str]]:
    """Members declared by `requires()` on the walked routes, and the leg's reach shortfall."""

    def calls(dependant: object) -> Iterable[object]:
        for dependency in getattr(dependant, "dependencies", []):
            yield dependency.call
            yield from calls(dependency)

    walked = walk(app)
    members = frozenset(
        str(getattr(call, attribute).value)
        for _, route in walked
        for call in calls(route.dependant)
        if getattr(call, attribute, None) is not None
    )
    reached = {path for path, _ in walked}
    shortfall = [f"{REACH_SHORTFALL}: {p}" for p in sorted(set(app.openapi()["paths"]) - reached)]
    return members, shortfall


def checked_permissions() -> frozenset[str]:
    """The live check sites: routes (flattened, reach proved) and service-layer calls."""
    from app.api.authz import PERMISSION_ATTRIBUTE
    from app.config import Environment, Settings
    from app.main import create_app
    from model_schema import Permission

    app = create_app(Settings(environment=Environment.LOCAL, version="parity", log_level="ERROR"))
    routed, shortfall = route_checks(app, PERMISSION_ATTRIBUTE)
    assert not shortfall, "\n".join(shortfall)
    sources = (p.read_text(encoding="utf-8") for p in sorted(BACKEND_SRC.rglob("*.py")))
    return routed | service_layer_checks(sources, {m.name: m.value for m in Permission})


# --- synthetic check sites --------------------------------------------------------------

_MEMBERS = {"A_READ": "a:read", "A_DEPLOY": "a:deploy"}
_ROLE_SET_ONLY = """
from model_schema import Permission as P

READERS = frozenset({P.A_READ, P.A_DEPLOY})

async def promote(session, actor):
    if P.A_DEPLOY in READERS:
        return actor
"""
_SERVICE_CHECK = """
from model_schema import Permission as P
from app.platform import rbac

async def promote(session, actor):
    await rbac.require_permission(session, principal=actor, permission=P.A_DEPLOY)
"""
_TEXT_REGEX = re.compile(r"\b(?:Perm|Permission|P)\.([A-Z_]+)\b")  # PL-1279 Task 3's proxy


@pytest.mark.req("FR-343")
def test_broken_member_referenced_but_never_checked_has_no_check_site() -> None:
    # The text-regex proxy counts both members; the AST predicate counts neither.
    assert {_MEMBERS[n] for n in _TEXT_REGEX.findall(_ROLE_SET_ONLY)} == {"a:read", "a:deploy"}
    assert service_layer_checks([_ROLE_SET_ONLY], _MEMBERS) == frozenset()
    checked = service_layer_checks([_ROLE_SET_ONLY], _MEMBERS) | {"a:read"}
    old, new = "| `a:deploy` | Deploying A | WK-674 |", "| `a:deploy` | Deploying A |  |"
    _only(parity_violations(_CLEAN.replace(old, new), _ENUM, checked, _WORKS), NO_CHECK_NO_OWNER)


@pytest.mark.req("FR-343")
def test_service_layer_require_permission_counts_as_checked() -> None:
    assert service_layer_checks([_SERVICE_CHECK], _MEMBERS) == frozenset({"a:deploy"})
    old, new = "| `a:deploy` | Deploying A | WK-674 |", "| `a:deploy` | Deploying A |  |"
    checked = service_layer_checks([_SERVICE_CHECK], _MEMBERS) | {"a:read"}
    assert parity_violations(_CLEAN.replace(old, new), _ENUM, checked, _WORKS) == []


class _P(StrEnum):
    A_READ = "a:read"


_ATTRIBUTE = "__parity_probe__"


def _nested_app() -> FastAPI:
    async def dependency() -> None:
        return None

    setattr(dependency, _ATTRIBUTE, _P.A_READ)
    inner = APIRouter(prefix="/inner")

    @inner.get("/thing", dependencies=[Depends(dependency)])
    async def thing() -> dict[str, str]:
        return {}

    outer = APIRouter(prefix="/outer")
    outer.include_router(inner)
    app = FastAPI()
    app.include_router(outer, prefix="/api")
    return app


def _top_level_only(app: FastAPI) -> list[tuple[str, APIRoute]]:
    """The walk `backend/tests/test_api_authorisation_sweep.py` uses: no flattening."""
    return [(str(r.path), r) for r in app.routes if isinstance(r, APIRoute)]


@pytest.mark.req("FR-343")
def test_broken_route_walk_without_flattening_fails_its_reach() -> None:
    members, shortfall = route_checks(_nested_app(), _ATTRIBUTE, walk=_top_level_only)
    assert members == frozenset()
    assert shortfall == [f"{REACH_SHORTFALL}: /api/outer/inner/thing"]


@pytest.mark.req("FR-343")
def test_flattened_route_walk_reaches_nested_routers() -> None:
    assert route_checks(_nested_app(), _ATTRIBUTE) == (frozenset({"a:read"}), [])


def test_python_workflow_triggers_on_every_parity_input() -> None:
    """docs.yml does not run on packages/** or backend/**; this module must run on all three."""
    workflow = (ROOT / ".github" / "workflows" / "python.yml").read_text(encoding="utf-8")
    push, _, pull_request = workflow.partition("\n  pull_request:")
    for block in (push, pull_request):
        for path in ("'packages/**'", "'backend/**'", "'docs/**'"):
            assert f"- {path}" in block, f"python.yml no longer triggers on {path}"
