"""The route-scope guard: a route gate must not contradict the scope its handler checks (FD 8177).

`PL-8181` Task 5; `06` FR-345's dated clause of 2026-10-22. Two predicates, one AST resolver, two
tables. Nothing here touches a database.

**Predicate 1** (the maintainer's "2026-10-22 17:27:15 BST" condition). A route is *gated without
scope* when one of its dependencies carries `PERMISSION_ATTRIBUTE` and not
`RESOURCE_CHECKED_IN_HANDLER_ATTRIBUTE` (`requires()` without `held_anywhere=True`): the gate
answers for the workspace only, so it refuses every scoped grant (`RL-1301` B.2 item 2). The
route fails if it also *reaches a scoped check* of that permission: a `require_permission` /
`has_permission` call whose `resource=` is not absent or `None`.

**Predicate 2** (the maintainer's "2026-10-22 17:36:24 BST" item 4, `PL-8181` DP-4 (a)). A check
with no resource where the spec names a scoped one cannot be seen by predicate 1: there is no
scoped check to pair. The difference between "workspace-wide by design" and "workspace-wide by
mistake" is in the spec, not the code, so every route holding a covered permission has a row in
`ROUTE_SCOPES` stating the scope it is meant to check, and the guard compares the code with it.

**Exclusions are owned and cannot go stale.** `KNOWN_SCOPE_GAPS` lists routes that fail today with
an owner and the slice that removes the row; a test asserts every row still fails, so the slice
that fixes a route is forced to delete it. A follow-on slice edits **only the two tables**.

**Limits, recorded.** The resolver follows calls by name through module-level functions of
`app.api.*` and `app.platform.*` to depth 3 (not methods, not callables passed as arguments). A
permission passed as a variable is treated as matching any gate. `MODEL_FAMILY` and
`RATING_ALGORITHM` scopes are declared but checked nowhere (`06` FR-345), so `model:*` and
`rating:*` routes are outside `COVERED_PERMISSIONS`; so are Environment-scoped `admin:*` routes,
of which none exists yet (no `admin:*` check names a resource). The spec cross-check reads only
cells that say "`dataset:…` on … Dataset"; a spec that names a scope in other words is caught by
table review alone.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import re
import subprocess
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import pytest
from backend.tests.test_management_429_declared import _calls, _flattened_operations
from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute

from app.api import authz, dislocation_runs
from app.api.authz import requires
from app.platform import datasets as dataset_service
from model_schema import Permission as Perm
from model_schema import ScopeType

REPO = Path(__file__).resolve().parents[2]

_CHECKERS = frozenset({"require_permission", "has_permission"})
_FOLLOW = ("app.api.", "app.platform.")
#: The checker itself, and the dependency factory (its `require_permission` call is the gate).
_NOT_FOLLOWED = frozenset({"app.platform.rbac", "app.api.authz"})
_DEPTH = 3

#: The permissions the tables classify. `DATASET_*` and `deployment:promote` are the ones whose
#: scope is checked anywhere in the code today (module docstring, "Limits").
COVERED_PERMISSIONS = frozenset(
    {
        "DATASET_READ",
        "DATASET_WRITE",
        "DATASET_VALIDATE",
        "DATASET_ACKNOWLEDGE_WARNING",
        "DEPLOYMENT_PROMOTE",
    }
)

Route = tuple[str, str]  # (METHOD, path)

# --------------------------------------------------------------------------------------------
# The tables. A follow-on slice changes only these.
# --------------------------------------------------------------------------------------------

#: Route -> the scope its handler is meant to check the permission on. Every route whose gate or
#: reached check holds a `COVERED_PERMISSIONS` member has a row (`test_every_covered_route_...`).
#: Spec lines: `01` §5.1 (datasets, versions, rules, reports), `03` §5.1 :1080/:1083 (dislocation
#: runs), `06` FR-345 (the clause of 2026-10-22), `07` (blobs, reference tables, deployments).
D, E, W = ScopeType.DATASET, ScopeType.ENVIRONMENT, ScopeType.WORKSPACE
ROUTE_SCOPES: dict[Route, ScopeType] = {
    # -- Fixed by this slice: held-anywhere gate, scoped check in the service (FR-345).
    ("PUT", "/api/v1/datasets/{slug}/dictionary"): D,
    ("PUT", "/api/v1/datasets/{slug}/rule-set"): D,
    ("POST", "/api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge"): D,
    # -- `deployment:promote` is checked on the Environment the path names (RL-1301 B.2).
    ("POST", "/api/v1/environments/{env}/deployments"): E,
    ("POST", "/api/v1/environments/{env}/deployment-requests"): E,
    ("POST", "/api/v1/environments/{env}/deployments/rollback"): E,
    # -- Acts on one named Dataset or Dataset Version: RL 8182's routes (`KNOWN_SCOPE_GAPS`).
    ("POST", "/api/v1/dataset-versions/{version_id}/validate"): D,
    ("GET", "/api/v1/dataset-versions/{version_id}/validation-reports"): D,
    ("POST", "/api/v1/dataset-versions/{version_id}/transition"): D,
    ("GET", "/api/v1/dataset-versions/{version_id}/profile"): D,
    ("GET", "/api/v1/dataset-versions/{version_id}/one-ways"): D,
    ("GET", "/api/v1/dataset-versions/{version_id}/compare"): D,
    ("POST", "/api/v1/dataset-versions/{version_id}/derive"): D,
    ("GET", "/api/v1/dataset-versions/{version_id}/lineage"): D,
    ("GET", "/api/v1/dataset-versions/{version_id}/rejected"): D,
    ("POST", "/api/v1/dataset-versions/{version_id}/splits"): D,
    ("GET", "/api/v1/dataset-versions/{version_id}/splits"): D,
    ("GET", "/api/v1/datasets/{slug}"): D,
    ("POST", "/api/v1/datasets/{slug}/versions"): D,
    ("GET", "/api/v1/datasets/{slug}/versions"): D,
    ("GET", "/api/v1/datasets/{slug}/versions/{version}"): D,
    ("GET", "/api/v1/dataset-versions/{version_id}"): D,
    ("PATCH", "/api/v1/datasets/{slug}/versions/{version}/schema"): D,
    ("GET", "/api/v1/validation-reports/{report_id}"): D,
    ("GET", "/api/v1/datasets/{slug}/rule-set"): D,
    ("GET", "/api/v1/blobs/{sha256}"): D,  # scoped through the owning Dataset Version
    # -- `03` §5.1 :1080/:1083 require `dataset:read` on the portfolio Dataset Version: FD 8184.
    ("POST", "/api/v1/dislocation-runs"): D,
    ("POST", "/api/v1/dislocation-runs/estimate"): D,
    ("GET", "/api/v1/dislocation-runs/{run_id}/movers"): D,
    ("GET", "/api/v1/rate-tables/{slug}@{version}/diff"): D,
    ("GET", "/api/v1/rate-tables/{slug}@{version}/diff/cells"): D,
    # -- Workspace-wide by design: they name no Dataset, or are outside FR-345's scopes.
    ("POST", "/api/v1/sources"): W,
    ("GET", "/api/v1/sources"): W,
    ("POST", "/api/v1/sources/{source_id}/preview"): W,
    ("POST", "/api/v1/datasets"): W,
    ("GET", "/api/v1/datasets"): W,
    ("PATCH", "/api/v1/datasets/{dataset_id}"): W,  # owner change: `admin:manage_roles` decides
    ("GET", "/api/v1/validation-rules"): W,
    ("POST", "/api/v1/validation-rules"): W,
    ("POST", "/api/v1/validation-rules/{rule_id}/dry-run"): W,
    ("POST", "/api/v1/validation-rules/{rule_id}/submit"): W,
    # Reference Tables are not a Dataset, have no ScopeType and sit outside FR-345 (RL 8182).
    ("GET", "/api/v1/reference-tables"): W,
    ("GET", "/api/v1/reference-tables/{slug}/lookup"): W,
    ("GET", "/api/v1/reference-tables/{slug}/versions"): W,
    ("GET", "/api/v1/reference-tables/{slug}/versions/{version}/rows"): W,
    # Upload is "held under any scope", the scope check at ingest (RL 8182).
    ("POST", "/api/v1/blobs/upload-url"): W,
    ("POST", "/api/v1/blobs/uploads/{upload_id}/complete"): W,
}

_RL_8182 = ("RL-8182", "the slice RL 8182 cuts")
_FD_8184 = ("FD-8184", "the slice RL 8182 cuts (FD 8184 joins it)")
_THIS = ("SL-8192", "SL-8192 (SL 8185 Task 4 follow-on), after SL-1736 merges")

#: The rule-set row is paired with four strict xfails in `test_dataset_scoped_writes.py`
#: (`_RULE_SET_OWED`): when SL 8192 fixes the route both XPASS and this row stops failing, so the
#: run goes red until the mark and the row are deleted together.
#: Route -> (owner record, the slice that removes the row). A row means: this route fails the
#: predicate today, the failure is owned, and that slice deletes the row. Working ids are written
#: in hyphen form until minted (`test_every_known_gap_names_an_owner_in_the_index`).
KNOWN_SCOPE_GAPS: dict[Route, tuple[str, str]] = {
    ("PUT", "/api/v1/datasets/{slug}/rule-set"): _THIS,
    **{
        route: _RL_8182
        for route in (
            ("POST", "/api/v1/dataset-versions/{version_id}/validate"),
            ("GET", "/api/v1/dataset-versions/{version_id}/validation-reports"),
            ("POST", "/api/v1/dataset-versions/{version_id}/transition"),
            ("GET", "/api/v1/dataset-versions/{version_id}/profile"),
            ("GET", "/api/v1/dataset-versions/{version_id}/one-ways"),
            ("GET", "/api/v1/dataset-versions/{version_id}/compare"),
            ("POST", "/api/v1/dataset-versions/{version_id}/derive"),
            ("GET", "/api/v1/dataset-versions/{version_id}/lineage"),
            ("GET", "/api/v1/dataset-versions/{version_id}/rejected"),
            ("POST", "/api/v1/dataset-versions/{version_id}/splits"),
            ("GET", "/api/v1/dataset-versions/{version_id}/splits"),
            ("GET", "/api/v1/datasets/{slug}"),
            ("POST", "/api/v1/datasets/{slug}/versions"),
            ("GET", "/api/v1/datasets/{slug}/versions"),
            ("GET", "/api/v1/datasets/{slug}/versions/{version}"),
            ("GET", "/api/v1/dataset-versions/{version_id}"),
            ("PATCH", "/api/v1/datasets/{slug}/versions/{version}/schema"),
            ("GET", "/api/v1/validation-reports/{report_id}"),
            ("GET", "/api/v1/datasets/{slug}/rule-set"),
            ("GET", "/api/v1/blobs/{sha256}"),
        )
    },
    **{
        route: _FD_8184
        for route in (
            ("POST", "/api/v1/dislocation-runs"),
            ("POST", "/api/v1/dislocation-runs/estimate"),
            ("GET", "/api/v1/dislocation-runs/{run_id}/movers"),
            ("GET", "/api/v1/rate-tables/{slug}@{version}/diff"),
            ("GET", "/api/v1/rate-tables/{slug}@{version}/diff/cells"),
        )
    },
}

# --------------------------------------------------------------------------------------------
# The AST resolver
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Check:
    """One `require_permission` / `has_permission` call a route reaches."""

    permission: str | None  # `Permission` member name; None when not written as an attribute
    scope: str | None  # None: no resource; "?": a resource of unknown kind; else a ScopeType name
    function: tuple[str, str]  # (module, function) enclosing the call
    where: str  # file:line


@cache
def _module_ast(modname: str) -> ast.Module:
    return ast.parse(inspect.getsource(importlib.import_module(modname)))


@cache
def _defs(modname: str) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        n.name: n
        for n in _module_ast(modname).body
        if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
    }


@cache
def _imports(modname: str) -> dict[str, tuple[str, ...]]:
    """Local name -> ("module", dotted) or ("func", dotted module, name)."""
    out: dict[str, tuple[str, ...]] = {}
    for n in ast.walk(_module_ast(modname)):
        if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            for a in n.names:
                local = a.asname or a.name
                try:
                    importlib.import_module(f"{n.module}.{a.name}")
                    out[local] = ("module", f"{n.module}.{a.name}")
                except ImportError:
                    out[local] = ("func", n.module, a.name)
        elif isinstance(n, ast.Import):
            for a in n.names:
                out[(a.asname or a.name).split(".")[0]] = (
                    "module",
                    a.name if a.asname else a.name.split(".")[0],
                )
    return out


def _name(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _target(modname: str, call: ast.Call) -> tuple[str, str] | None:
    """The module-level function a call names, through the calling module's imports."""
    f = call.func
    imports = _imports(modname)
    if isinstance(f, ast.Name):
        if f.id in _defs(modname):
            return modname, f.id
        found = imports.get(f.id)
        if found and found[0] == "func":
            return found[1], found[2]
    elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
        found = imports.get(f.value.id)
        if found and found[0] == "module":
            return found[1], f.attr
    return None


def _scope_of(resource: ast.AST | None) -> str | None:
    """None for an absent or literal-`None` resource; the `scope_type` of a `ResourceRef(...)`
    built anywhere in the expression; "?" for any other non-None expression."""
    if resource is None or (isinstance(resource, ast.Constant) and resource.value is None):
        return None
    for n in ast.walk(resource):
        if isinstance(n, ast.Call) and _name(n.func) == "ResourceRef":
            for kw in n.keywords:
                if kw.arg == "scope_type" and _name(kw.value):
                    return _name(kw.value)
    return "?"


def _check(call: ast.Call, modname: str, function: str) -> Check:
    kwargs = {k.arg: k.value for k in call.keywords}
    permission = kwargs.get("permission")
    if permission is None and len(call.args) >= 3:
        permission = call.args[2]
    return Check(
        permission=_name(permission) if isinstance(permission, ast.Attribute) else None,
        scope=_scope_of(kwargs.get("resource")),
        function=(modname, function),
        where=f"{modname.replace('.', '/')}.py:{call.lineno}",
    )


def reached_checks(
    modname: str, function: str, depth: int = _DEPTH, seen: set[tuple[str, str]] | None = None
) -> list[Check]:
    """Every permission check reachable from `modname.function` by following named calls."""
    seen = set() if seen is None else seen
    if (modname, function) in seen or modname in _NOT_FOLLOWED:
        return []
    seen.add((modname, function))
    node = _defs(modname).get(function)
    if node is None:
        return []
    found: list[Check] = []
    for n in ast.walk(node):
        if not isinstance(n, ast.Call):
            continue
        if _name(n.func) in _CHECKERS:
            found.append(_check(n, modname, function))
        elif depth > 0:
            target = _target(modname, n)
            if target and target[0].startswith(_FOLLOW):
                found.extend(reached_checks(target[0], target[1], depth - 1, seen))
    return found


# --------------------------------------------------------------------------------------------
# The predicates
# --------------------------------------------------------------------------------------------


def _gates(route: APIRoute) -> list[tuple[str, bool]]:
    """`(Permission name, resource checked in the handler)` for each `requires()` dependency."""
    out = []
    for call in _calls(route.dependant):
        permission = getattr(call, authz.PERMISSION_ATTRIBUTE, None)
        if permission is not None:
            out.append(
                (permission.name, bool(getattr(call, authz.RESOURCE_CHECKED_IN_HANDLER_ATTRIBUTE)))
            )
    return out


def _reached(route: APIRoute) -> list[Check]:
    return reached_checks(route.endpoint.__module__, route.endpoint.__name__)


def predicate_1(route: APIRoute) -> list[str]:
    """A scope-less route gate over a scoped check of the same permission."""
    reasons = []
    reached = _reached(route)
    for permission, handler_checked in _gates(route):
        if handler_checked:
            continue
        for check in reached:
            if check.scope is not None and check.permission in (permission, None):
                reasons.append(
                    f"gated by a scope-less requires({permission}) but {check.where} checks it "
                    f"on a {check.scope} resource"
                )
    return reasons


def _covered(route: APIRoute) -> bool:
    gate = any(p in COVERED_PERMISSIONS for p, _ in _gates(route))
    return gate or any(c.permission in COVERED_PERMISSIONS for c in _reached(route))


def predicate_2(route: APIRoute, declared: ScopeType) -> list[str]:
    """The code against the scope the table declares for the route."""
    reached = [c for c in _reached(route) if c.permission in COVERED_PERMISSIONS]
    scoped = {c.scope for c in reached if c.scope is not None}
    reasons = []
    if declared is ScopeType.WORKSPACE:
        if scoped:
            reasons.append(f"declared WORKSPACE but reaches a scoped check ({sorted(scoped)})")
        return reasons
    for permission, handler_checked in _gates(route):
        if permission in COVERED_PERMISSIONS and not handler_checked:
            reasons.append(
                f"declared {declared.name} but gated by a scope-less requires({permission})"
            )
    if declared.name not in scoped:
        reasons.append(f"declared {declared.name} but no check names a {declared.name} resource")
    return reasons


def failures(route: APIRoute, declared: ScopeType | None) -> list[str]:
    reasons = predicate_1(route)
    if declared is not None:
        reasons += predicate_2(route, declared)
    return reasons


# --------------------------------------------------------------------------------------------
# The app
# --------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def routes() -> dict[Route, APIRoute]:
    from app.config import Environment, Settings
    from app.main import create_app

    app = create_app(Settings(environment=Environment.LOCAL, version="test"))
    found = {
        (method, path): route
        for method, path, route in _flattened_operations(app.routes)
        if path.startswith("/api/v1/")
    }
    assert len(found) > 100, "the route walk is vacuous"
    return found


def _app_failures(routes: dict[Route, APIRoute]) -> dict[Route, list[str]]:
    return {
        key: reasons
        for key, route in routes.items()
        if (reasons := failures(route, ROUTE_SCOPES.get(key)))
    }


@pytest.mark.req("FR-345")
def test_no_route_gate_contradicts_the_scope_its_handler_checks(
    routes: dict[Route, APIRoute],
) -> None:
    """The app-wide guard. Red at base: names exactly the three FD 8177 routes (dictionary,
    rule-set, acknowledge), which `KNOWN_SCOPE_GAPS` then carries only for rule-set."""
    bad = {k: v for k, v in _app_failures(routes).items() if k not in KNOWN_SCOPE_GAPS}
    assert not bad, "\n" + "\n".join(
        f"{m} {p}: {'; '.join(r)}" for (m, p), r in sorted(bad.items())
    )


@pytest.mark.req("FR-345")
def test_every_covered_route_has_a_row(routes: dict[Route, APIRoute]) -> None:
    """Completeness: a new route holding a covered permission cannot slip past the table."""
    missing = sorted(k for k, route in routes.items() if _covered(route) and k not in ROUTE_SCOPES)
    assert not missing, f"covered routes with no ROUTE_SCOPES row: {missing}"
    stale = sorted(set(ROUTE_SCOPES) - set(routes))
    assert not stale, f"ROUTE_SCOPES rows for routes that do not exist: {stale}"


@pytest.mark.req("FR-345")
def test_every_known_gap_still_fails(routes: dict[Route, APIRoute]) -> None:
    """An exclusion cannot go stale: the slice that fixes a route must delete its row."""
    fixed = sorted(k for k in KNOWN_SCOPE_GAPS if not failures(routes[k], ROUTE_SCOPES.get(k)))
    assert not fixed, f"these routes pass now; delete their KNOWN_SCOPE_GAPS rows: {fixed}"


@pytest.mark.req("FR-345")
def test_every_known_gap_names_an_owner_in_the_index() -> None:
    """The owner is a record that exists: in `docs/INDEX.md`, or a working id in hyphen form."""
    index = (REPO / "docs" / "INDEX.md").read_text()
    for route, (owner, removing) in KNOWN_SCOPE_GAPS.items():
        assert removing, f"{route} names no removing slice"
        assert re.fullmatch(r"(RL|FD|SL|PL)-\d+", owner), f"{route}: owner {owner!r} is not an id"
        assert owner in index or int(owner.split("-")[1]) >= 8000, f"{route}: {owner} is unknown"
    assert set(KNOWN_SCOPE_GAPS) <= set(ROUTE_SCOPES), "a gap row needs its ROUTE_SCOPES row"


@pytest.mark.req("FR-345")
def test_the_guard_does_not_flag_the_environment_or_workspace_wide_routes(
    routes: dict[Route, APIRoute],
) -> None:
    """Negative controls: the deployment routes (handler-guarded, ENVIRONMENT) and
    `GET /reference-tables` (WORKSPACE, RL 8182) are classified and clean."""
    for key in (
        ("POST", "/api/v1/environments/{env}/deployments"),
        ("GET", "/api/v1/reference-tables"),
    ):
        assert failures(routes[key], ROUTE_SCOPES[key]) == [], key


# ---- the guard is fed routes that must be flagged ------------------------------------------


def _router_with(endpoint: Any, gate: Any) -> APIRoute:
    router = APIRouter()
    router.add_api_route(
        "/synthetic/{slug}", endpoint, methods=["PUT"], dependencies=[Depends(gate)]
    )
    route = router.routes[0]
    assert isinstance(route, APIRoute)
    return route


async def _synthetic_dictionary_endpoint(slug: str) -> None:
    """Calls the scoped check of `update_dictionary` behind a scope-less gate."""
    await dataset_service.update_dictionary(
        None, workspace_id=None, actor=None, slug=slug, entries={}
    )  # type: ignore[arg-type]


async def _synthetic_portfolio_endpoint(slug: str) -> None:
    """Calls a scope-less `dataset:read` check, as `dislocation_runs` does."""
    await dislocation_runs._require_dataset_read(None, None)  # type: ignore[arg-type]


@pytest.mark.req("FR-345")
def test_predicate_1_flags_a_scope_less_gate_over_a_scoped_check() -> None:
    """Red-first, the injection: a route gated by a scope-less `requires(DATASET_WRITE)` whose
    endpoint reaches `update_dictionary`'s scoped check is flagged; the same route behind
    `held_anywhere=True` is not."""
    flagged = _router_with(_synthetic_dictionary_endpoint, requires(Perm.DATASET_WRITE))
    assert predicate_1(flagged), "the injected scope-less gate was not flagged"
    clean = _router_with(
        _synthetic_dictionary_endpoint, requires(Perm.DATASET_WRITE, held_anywhere=True)
    )
    assert predicate_1(clean) == []


@pytest.mark.req("FR-345")
def test_predicate_2_flags_a_route_declared_dataset_that_checks_no_resource() -> None:
    """Red-first, the injection: a route declared DATASET whose endpoint calls the scope-less
    `_require_dataset_read` is flagged, and passes when declared WORKSPACE."""
    route = _router_with(_synthetic_portfolio_endpoint, requires(Perm.RATING_READ))
    assert predicate_2(route, ScopeType.DATASET), "the injected unscoped check was not flagged"
    assert predicate_2(route, ScopeType.WORKSPACE) == []


# ---- the guard cannot go blind -------------------------------------------------------------


@pytest.mark.req("FR-345")
def test_the_resolver_finds_exactly_the_functions_that_build_a_resource(
    routes: dict[Route, APIRoute],
) -> None:
    """Coverage control. The functions enclosing a reached scoped check equal the functions
    enclosing the hits of `grep -rn "ResourceRef(" backend/src/app --include=*.py`, excluding
    `platform/rbac.py`: a call shape the resolver cannot follow shows up as a missing function."""
    out = subprocess.run(
        ["grep", "-rn", "ResourceRef(", "backend/src/app", "--include=*.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    expected: set[tuple[str, str]] = set()
    for line in out.splitlines():
        file, lineno, _ = line.split(":", 2)
        if file.endswith("platform/rbac.py"):
            continue
        modname = file.removeprefix("backend/src/").removesuffix(".py").replace("/", ".")
        enclosing = [
            n.name
            for n in _defs(modname).values()
            if n.lineno <= int(lineno) <= (n.end_lineno or n.lineno)
        ]
        expected.add((modname, enclosing[0] if enclosing else f"<module:{lineno}>"))
    found = {
        c.function for route in routes.values() for c in _reached(route) if c.scope is not None
    }
    assert found == expected, f"resolver found {sorted(found)}, grep found {sorted(expected)}"


@pytest.mark.req("FR-345")
def test_the_spec_names_a_dataset_scope_only_for_routes_declared_dataset() -> None:
    """DP-4's (b) as a control: every §5.1 row whose cell says "`dataset:…` on … Dataset" maps to
    a route whose `ROUTE_SCOPES` row is DATASET. Limit: a spec that names the scope in other words
    is not matched here."""
    pattern = re.compile(r"`dataset:[a-z_]+`\s+on\s+(?:that|the|each|a)\b[^|;.]*?Dataset")
    row = re.compile(r"^\|\s*`([A-Z]+)`\s*\|\s*`([^`]+)`\s*\|(.*)$")
    matched = []
    for spec in sorted((REPO / "docs" / "specs").glob("0[1-7]-*.md")):
        for text in spec.read_text().splitlines():
            m = row.match(text)
            if m and pattern.search(m.group(3)):
                matched.append((m.group(1), re.sub(r"\{[^}]*\}", "{}", m.group(2))))
    assert matched, "the cross-check matched no spec row: its pattern is stale"
    declared = {
        (method, re.sub(r"\{[^}]*\}", "{}", path)): scope
        for (method, path), scope in ROUTE_SCOPES.items()
    }
    wrong = [r for r in matched if declared.get(r) is not ScopeType.DATASET]
    assert not wrong, f"spec says a Dataset scope; ROUTE_SCOPES does not (or has no row): {wrong}"


@pytest.mark.req("FR-345")
def test_held_anywhere_with_a_counted_gate_is_a_type_error() -> None:
    """`held_anywhere=True` never counts: asking it to is refused at construction (PL-8181 DP-1)."""
    with pytest.raises(TypeError):
        requires(Perm.DATASET_WRITE, held_anywhere=True, management_counted=True)
