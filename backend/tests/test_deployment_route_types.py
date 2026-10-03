"""The Environment and Deployment routes are typed both ways (`PL-1392` Acceptance 14 and 15).

`FD-1335`'s two forms of an untyped response are each refused **by name**: form 1, a schema
equal to `{}`; form 2, an `object` with no `properties`. A request body is a `model-schema`
class, found by walking the handler's own source rather than by trusting the OpenAPI, so a
body typed `dict[str, Any]` or a class the API module defines fails the AST half and the
OpenAPI half **separately**.

**Task 4 pins rows 1 to 4 of the Route table** (the four Environment routes). Task 5 widens
`ROWS`, `MODULES` and `PINNED_PREFIX_FILTER` to all seven; nothing here is hand-listed twice.
"""

from __future__ import annotations

import ast
import copy
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "backend" / "src" / "app" / "api"
GENERATED_SCHEMAS = ROOT / "docs" / "contracts" / "schemas" / "generated"
API_PREFIX = "/api/v1"
_METHODS = ("get", "post", "put", "patch", "delete")


@dataclass(frozen=True)
class Row:
    """One row of `PL-1392`'s Route table."""

    method: str
    path: str
    request: str | None  # a model-schema class name, or None for "no body"
    response: str  # the 2xx class name; for a list route, the item class
    paged: bool = False


ROWS: tuple[Row, ...] = (
    Row("GET", "/api/v1/environments", None, "Environment", paged=True),
    Row("POST", "/api/v1/environments", "EnvironmentCreate", "Environment"),
    Row("PATCH", "/api/v1/environments/{slug}", "EnvironmentUpdate", "Environment"),
    Row("POST", "/api/v1/environments/{slug}/retire", None, "Environment"),
)

#: The module of each row's handler. Task 5 adds `deployments.py`.
MODULES: tuple[Path, ...] = (API / "environments.py",)


def _published_names() -> set[str]:
    """The class names `scripts/generate-contracts.py` publishes (its `GENERATED_SHAPES`)."""
    spec = importlib.util.spec_from_file_location(
        "generate_contracts", ROOT / "scripts" / "generate-contracts.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    shapes: dict[str, str] = module.GENERATED_SHAPES
    return set(shapes.values())


def _ref(name: str) -> dict[str, str]:
    return {"$ref": f"#/components/schemas/{name}"}


def _untyped_form(schema: dict[str, Any]) -> str | None:
    """FD-1335's form 1 (`{}`) or form 2 (an object with no properties); else `None`."""
    if schema == {}:
        return "form 1 (a schema equal to {})"
    if schema.get("type") == "object" and "properties" not in schema and "$ref" not in schema:
        return "form 2 (an object with no properties)"
    return None


# --- OpenAPI half --------------------------------------------------------------------------


def openapi_problems(document: dict[str, Any], rows: tuple[Row, ...] = ROWS) -> list[str]:
    """Every way the document's typing of `rows` departs from the Route table."""
    problems: list[str] = []
    published = _published_names()
    components: dict[str, Any] = document["components"]["schemas"]
    for row in rows:
        where = f"{row.method} {row.path}"
        operation = document["paths"].get(row.path, {}).get(row.method.lower())
        if operation is None:
            problems.append(f"{where}: not in the OpenAPI document")
            continue

        body = operation.get("requestBody")
        if row.request is None:
            if body is not None:
                problems.append(f"{where}: declares a requestBody; the table says no body")
        else:
            schema = (body or {}).get("content", {}).get("application/json", {}).get("schema")
            if schema != _ref(row.request):
                problems.append(f"{where}: request body is {schema}, not {_ref(row.request)}")
            if row.request not in published:
                problems.append(f"{where}: request type {row.request} is not a published shape")

        twoxx = {c: r for c, r in operation["responses"].items() if c.startswith("2")}
        if not twoxx:
            problems.append(f"{where}: no 2xx response")
        for code, response in twoxx.items():
            schema = response.get("content", {}).get("application/json", {}).get("schema")
            if schema is None:
                problems.append(f"{where}: {code} has no JSON schema (form 1)")
                continue
            form = _untyped_form(schema)
            if form is not None:
                problems.append(f"{where}: {code} is {form}")
                continue
            if row.paged:
                page = f"Page_{row.response}_"
                if schema != _ref(page):
                    problems.append(f"{where}: {code} is {schema}, not {_ref(page)}")
                    continue
                items = components.get(page, {}).get("properties", {}).get("items", {})
                if items.get("items") != _ref(row.response):
                    problems.append(
                        f"{where}: {page}.items.items is {items.get('items')}, "
                        f"not {_ref(row.response)}"
                    )
                elif _untyped_form(items["items"]) is not None:
                    problems.append(f"{where}: {page} items are untyped")
            elif schema != _ref(row.response):
                problems.append(f"{where}: {code} is {schema}, not {_ref(row.response)}")
            if row.response not in published:
                problems.append(f"{where}: response type {row.response} is not a published shape")
            if not (GENERATED_SCHEMAS / f"{_kebab(row.response)}.schema.json").is_file():
                problems.append(f"{where}: no generated schema file for {row.response}")
    return problems


def _kebab(name: str) -> str:
    out = ""
    for i, ch in enumerate(name):
        if ch.isupper() and i:
            out += "-"
        out += ch.lower()
    return out


# --- AST half ------------------------------------------------------------------------------


def _router_prefix(tree: ast.Module) -> str:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "APIRouter"
        ):
            for keyword in node.keywords:
                if keyword.arg == "prefix" and isinstance(keyword.value, ast.Constant):
                    return str(keyword.value.value)
    return ""


def _imported_from_model_schema(tree: ast.Module) -> set[str]:
    return {
        alias.asname or alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.module is not None
        and (node.module == "model_schema" or node.module.startswith("model_schema."))
        for alias in node.names
    }


def _handlers(tree: ast.Module) -> dict[tuple[str, str], ast.AsyncFunctionDef]:
    """`(METHOD, full path)` of every `@router.<method>(...)` handler in the module."""
    prefix = API_PREFIX + _router_prefix(tree)
    found: dict[tuple[str, str], ast.AsyncFunctionDef] = {}
    for node in tree.body:
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and isinstance(decorator.func.value, ast.Name)
                and decorator.func.value.id == "router"
                and decorator.func.attr in _METHODS
                and decorator.args
                and isinstance(decorator.args[0], ast.Constant)
            ):
                path = prefix + str(decorator.args[0].value)
                found[(decorator.func.attr.upper(), path)] = node
    return found


def ast_problems(sources: dict[str, str], rows: tuple[Row, ...] = ROWS) -> list[str]:
    """Every way a handler's own source departs from the Route table.

    `sources` maps a module name to its text, so a test can hand in a broken copy.
    """
    handlers: dict[tuple[str, str], tuple[str, ast.AsyncFunctionDef, set[str]]] = {}
    for name, text in sources.items():
        tree = ast.parse(text)
        imported = _imported_from_model_schema(tree)
        for key, node in _handlers(tree).items():
            handlers[key] = (name, node, imported)

    problems: list[str] = []
    for row in rows:
        where = f"{row.method} {row.path}"
        if (row.method, row.path) not in handlers:
            problems.append(f"{where}: no handler found in the checked modules")
            continue
        module, node, imported = handlers[(row.method, row.path)]
        params = {a.arg: a for a in node.args.args + node.args.kwonlyargs}
        if row.request is None:
            if "body" in params:
                problems.append(f"{where}: {module} takes a `body` parameter; the table says none")
        else:
            annotation = params["body"].annotation if "body" in params else None
            if not isinstance(annotation, ast.Name):
                shown = ast.unparse(annotation) if annotation is not None else "no `body`"
                problems.append(
                    f"{where}: {module} body is {shown}, not the bare name {row.request}"
                )
            elif annotation.id != row.request:
                problems.append(f"{where}: {module} body is {annotation.id}, not {row.request}")
            elif annotation.id not in imported:
                problems.append(
                    f"{where}: {module} body {annotation.id} is not imported from model_schema "
                    "(a class the API module defines is a second copy of a shape)"
                )
        expected = f"Page[{row.response}]" if row.paged else row.response
        returns = ast.unparse(node.returns) if node.returns is not None else None
        if returns != expected:
            problems.append(f"{where}: {module} returns {returns}, not {expected}")
    return problems


def _sources() -> dict[str, str]:
    return {path.name: path.read_text() for path in MODULES}


# --- the tests -----------------------------------------------------------------------------


@pytest.fixture(scope="module")
def document() -> dict[str, Any]:
    from app.config import Environment, Settings
    from app.main import create_app

    app = create_app(Settings(environment=Environment.LOCAL, version="test"))
    return app.openapi()


@pytest.mark.req("FR-428")
def test_the_route_set_is_pinned(document: dict[str, Any]) -> None:
    """The operations of the Environment routes equal the Route table's rows, exactly.

    A route added or removed unchecked fails here naming it. Task 5 widens the filter to the
    deployment routes under the same prefix.
    """
    live = {
        (method.upper(), path)
        for path, operations in document["paths"].items()
        if path.startswith(f"{API_PREFIX}/environments") and "/deployment" not in path
        for method in operations
        if method in _METHODS
    }
    expected = {(row.method, row.path) for row in ROWS}
    assert live == expected, (
        f"extra: {sorted(live - expected)}; missing: {sorted(expected - live)}"
    )


@pytest.mark.req("FR-428")
def test_every_request_body_is_a_model_schema_type_in_the_source() -> None:
    assert ast_problems(_sources()) == []


@pytest.mark.req("FR-428")
def test_every_request_body_is_a_ref_to_a_published_shape(document: dict[str, Any]) -> None:
    problems = [p for p in openapi_problems(document) if "request" in p or "requestBody" in p]
    assert problems == []


@pytest.mark.req("FR-428")
def test_every_2xx_is_a_ref_to_a_published_shape(document: dict[str, Any]) -> None:
    assert openapi_problems(document) == []


@pytest.mark.req("FR-428")
def test_the_committed_contract_types_the_routes_the_same_way() -> None:
    """`docs/contracts/openapi/generated.json` is the published spec artifact (FR-451)."""
    committed = json.loads(
        (ROOT / "docs" / "contracts" / "openapi" / "generated.json").read_text()
    )
    assert openapi_problems(committed) == []


# --- broken input: each check fails, naming the route, on a deliberately broken copy -----------


@pytest.mark.req("FR-428")
def test_a_body_retyped_dict_is_refused_by_the_ast_and_the_openapi_halves(
    document: dict[str, Any],
) -> None:
    source = _sources()["environments.py"].replace(
        "body: EnvironmentCreate,", "body: dict[str, Any],", 1
    )
    assert source != _sources()["environments.py"]
    problems = ast_problems({"environments.py": source})
    assert any("POST /api/v1/environments:" in p and "dict[str, Any]" in p for p in problems)

    broken = copy.deepcopy(document)
    broken["paths"]["/api/v1/environments"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"] = {"type": "object", "additionalProperties": True}
    problems = openapi_problems(broken)
    assert any(p.startswith("POST /api/v1/environments: request body is") for p in problems)


@pytest.mark.req("FR-428")
def test_a_body_class_defined_in_the_api_module_is_refused() -> None:
    text = _sources()["environments.py"].replace(
        "from model_schema import Environment, EnvironmentCreate, EnvironmentUpdate, Permission",
        "from pydantic import BaseModel\n"
        "from model_schema import Environment, EnvironmentUpdate, Permission\n\n\n"
        "class EnvironmentCreate(BaseModel):\n    slug: str\n",
        1,
    )
    problems = ast_problems({"environments.py": text})
    assert any("not imported from model_schema" in p and "EnvironmentCreate" in p for p in problems)


@pytest.mark.req("FR-428")
def test_a_body_on_a_no_body_route_is_refused() -> None:
    text = _sources()["environments.py"].replace(
        "slug: str, caller: ManageEnvironmentsDep, database: DatabaseDep\n) -> Environment:\n"
        '    """**200** with `retired_at` set.',
        "slug: str, body: dict[str, Any], caller: ManageEnvironmentsDep, database: DatabaseDep\n"
        ") -> Environment:\n"
        '    """**200** with `retired_at` set.',
        1,
    )
    assert text != _sources()["environments.py"]
    problems = ast_problems({"environments.py": text})
    assert any("retire" in p and "takes a `body` parameter" in p for p in problems)


@pytest.mark.req("FR-428")
def test_each_untyped_response_form_is_refused_by_name(document: dict[str, Any]) -> None:
    form1 = copy.deepcopy(document)
    form1["paths"]["/api/v1/environments"]["post"]["responses"]["201"]["content"][
        "application/json"
    ]["schema"] = {}
    assert any(
        "POST /api/v1/environments" in p and "form 1" in p for p in openapi_problems(form1)
    )

    form2 = copy.deepcopy(document)
    form2["paths"]["/api/v1/environments/{slug}"]["patch"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"] = {"type": "object", "additionalProperties": True}
    assert any(
        "PATCH /api/v1/environments/{slug}" in p and "form 2" in p
        for p in openapi_problems(form2)
    )

    open_page = copy.deepcopy(document)
    open_page["components"]["schemas"]["Page_Environment_"]["properties"]["items"]["items"] = {
        "type": "object",
        "additionalProperties": True,
    }
    assert any("Page_Environment_" in p for p in openapi_problems(open_page))


@pytest.mark.req("FR-428")
def test_a_missing_or_open_return_annotation_is_refused() -> None:
    original = _sources()["environments.py"]
    for broken, shown in (
        (original.replace("-> Environment:\n", ":\n", 1), "None"),
        (original.replace("-> Environment:\n", "-> dict[str, Any]:\n", 1), "dict[str, Any]"),
    ):
        assert broken != original
        problems = ast_problems({"environments.py": broken})
        assert any(f"returns {shown}" in p for p in problems), problems


@pytest.mark.req("FR-428")
def test_a_route_added_unchecked_fails_the_pin(document: dict[str, Any]) -> None:
    extra = copy.deepcopy(document)
    extra["paths"]["/api/v1/environments/{slug}/wipe"] = {"delete": {"responses": {}}}
    live = {
        (method.upper(), path)
        for path, operations in extra["paths"].items()
        if path.startswith(f"{API_PREFIX}/environments") and "/deployment" not in path
        for method in operations
        if method in _METHODS
    }
    assert live != {(row.method, row.path) for row in ROWS}
