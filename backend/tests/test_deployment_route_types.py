"""The Environment and Deployment routes are typed both ways (`PL-1392` Acceptance 14 and 15).

`FD-1335`'s two forms of an untyped response are each refused **by name**: form 1, a schema
equal to `{}`; form 2, an `object` with no `properties`. A request body is a `model-schema`
class, found by walking the handler's own source rather than by trusting the OpenAPI, so a
body typed `dict[str, Any]` or a class the API module defines fails the AST half and the
OpenAPI half **separately**.

**Task 4 pinned rows 1 to 4 of the Route table** (the four Environment routes). **Task 5 widens
`ROWS` and `MODULES` to rows 5 to 7** (the deployment-request, deploy and history routes) **and
row 9** (`POST /api/v1/approval-requests`, body only: DP-S2-6 (c) leaves its 2xx an open object,
owned by FD 9752; the characterisation test below pins its key set instead). Nothing here is
hand-listed twice.
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
    #: The 2xx class name; for a list route, the item class. `None` for a route whose 2xx is
    #: deliberately left an open object (DP-S2-6 (c)): only its body is checked.
    response: str | None
    paged: bool = False


ROWS: tuple[Row, ...] = (
    Row("GET", "/api/v1/environments", None, "Environment", paged=True),
    Row("POST", "/api/v1/environments", "EnvironmentCreate", "Environment"),
    Row("PATCH", "/api/v1/environments/{slug}", "EnvironmentUpdate", "Environment"),
    Row("POST", "/api/v1/environments/{slug}/retire", None, "Environment"),
    Row(
        "POST",
        "/api/v1/environments/{env}/deployment-requests",
        "DeploymentRequestCreate",
        "DeploymentRequest",
    ),
    Row("POST", "/api/v1/environments/{env}/deployments", "DeploymentCreate", "Deployment"),
    Row("GET", "/api/v1/environments/{env}/deployments", None, "Deployment", paged=True),
    # Row 9: the body and (FD-1416, PL-1528) the 2xx are typed.
    Row("POST", "/api/v1/approval-requests", "ApprovalSubmission", "ApprovalRequest"),
    # Row 8 (Task 6): the withdraw body is `reason` only; the server derives liveness.
    Row(
        "POST",
        "/api/v1/approval-requests/{request_id}/withdraw",
        "ApprovalWithdrawal",
        "ApprovalRequest",
    ),
)

#: The module of each row's handler.
MODULES: tuple[Path, ...] = (
    API / "environments.py",
    API / "deployments.py",
    API / "approvals.py",
)

#: Rows that are Environment-prefixed routes: the set `test_the_route_set_is_pinned` holds equal.
ENVIRONMENT_ROWS: tuple[Row, ...] = tuple(
    row for row in ROWS if row.path.startswith("/api/v1/environments")
)


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

        if row.response is None:
            continue
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
        if row.response is None:
            continue
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


def _environment_operations(document: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (method.upper(), path)
        for path, operations in document["paths"].items()
        if path.startswith(f"{API_PREFIX}/environments")
        for method in operations
        if method in _METHODS
    }


@pytest.mark.req("FR-428")
def test_the_route_set_is_pinned(document: dict[str, Any]) -> None:
    """The operations under `/api/v1/environments` equal the Route table's seven rows, exactly.

    A route added or removed unchecked fails here naming it.
    """
    live = _environment_operations(document)
    expected = {(row.method, row.path) for row in ENVIRONMENT_ROWS}
    assert len(expected) == 7
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
    extra["paths"]["/api/v1/environments/{env}/deployments/rollback"] = {
        "post": {"responses": {}}
    }
    assert _environment_operations(extra) != {(row.method, row.path) for row in ENVIRONMENT_ROWS}


# --- the new routes, on broken input (Acceptance 14 and 15 over rows 5 to 7) -------------------


@pytest.mark.req("FR-267")
def test_a_deploy_body_retyped_dict_is_refused_by_both_halves(document: dict[str, Any]) -> None:
    original = _sources()["deployments.py"]
    source = original.replace("body: DeploymentCreate,", "body: dict[str, Any],", 1)
    assert source != original
    problems = ast_problems({"deployments.py": source})
    assert any(
        "POST /api/v1/environments/{env}/deployments:" in p and "dict[str, Any]" in p
        for p in problems
    )
    broken = copy.deepcopy(document)
    broken["paths"]["/api/v1/environments/{env}/deployments"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"] = {"type": "object", "additionalProperties": True}
    assert any(
        p.startswith("POST /api/v1/environments/{env}/deployments: request body is")
        for p in openapi_problems(broken)
    )


@pytest.mark.req("FR-267")
def test_a_request_body_class_defined_in_the_api_module_is_refused() -> None:
    original = _sources()["deployments.py"]
    text = original.replace("    DeploymentRequestCreate,\n", "", 1) + (
        "\n\nfrom pydantic import BaseModel\n\n\n"
        "class DeploymentRequestCreate(BaseModel):\n    x: int\n"
    )
    assert text != original
    problems = ast_problems({"deployments.py": text})
    assert any(
        "not imported from model_schema" in p and "DeploymentRequestCreate" in p for p in problems
    )


@pytest.mark.req("FR-267")
def test_each_untyped_2xx_of_the_deployment_routes_is_refused_by_name(
    document: dict[str, Any],
) -> None:
    form1 = copy.deepcopy(document)
    form1["paths"]["/api/v1/environments/{env}/deployments"]["post"]["responses"]["201"][
        "content"
    ]["application/json"]["schema"] = {}
    assert any("form 1" in p and "deployments" in p for p in openapi_problems(form1))

    form2 = copy.deepcopy(document)
    form2["paths"]["/api/v1/environments/{env}/deployment-requests"]["post"]["responses"][
        "201"
    ]["content"]["application/json"]["schema"] = {"type": "object", "additionalProperties": True}
    assert any("form 2" in p and "deployment-requests" in p for p in openapi_problems(form2))

    open_page = copy.deepcopy(document)
    open_page["components"]["schemas"]["Page_Deployment_"]["properties"]["items"]["items"] = {
        "type": "object",
        "additionalProperties": True,
    }
    assert any("Page_Deployment_" in p for p in openapi_problems(open_page))

    original = _sources()["deployments.py"]
    for broken, shown in (
        (original.replace(") -> Deployment:\n", "):\n", 1), "None"),
        (original.replace(") -> Deployment:\n", ") -> dict[str, Any]:\n", 1), "dict[str, Any]"),
    ):
        assert broken != original
        assert any(f"returns {shown}" in p for p in ast_problems({"deployments.py": broken}))


@pytest.mark.req("FR-267")
def test_the_approval_submission_body_is_a_model_schema_type_not_a_class_the_api_defines() -> None:
    """Acceptance 16: moved, not duplicated. `SubmitApproval` is gone from the backend, and the
    generic route's body is `ApprovalSubmission` from `model_schema`; reintroducing a local
    class of the old name fails the AST half."""
    import subprocess

    found = subprocess.run(
        ["git", "grep", "-n", "-E", r"^class (Withdraw|SubmitApproval)\b", "--", "backend/src"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout
    assert found == "", found  # neither `SubmitApproval` nor `Withdraw` is a backend class

    original = _sources()["approvals.py"]
    local = original.replace(
        "    ApprovalSubmission,\n", "", 1
    ) + "\n\nclass ApprovalSubmission(BaseModel):\n    artifact_ref: str\n"
    submission_row = next(r for r in ROWS if r.request == "ApprovalSubmission")
    problems = ast_problems({"approvals.py": local}, rows=(submission_row,))
    assert any("not imported from model_schema" in p for p in problems)


@pytest.mark.req("FR-357")
def test_the_withdrawal_body_is_a_model_schema_type_with_no_liveness_field() -> None:
    """Acceptance 16 for the withdraw route: the body is `ApprovalWithdrawal` from `model_schema`,
    and it carries `reason` only (`PL-1392` Task 6, C11) — liveness is the server's."""
    from model_schema import ApprovalWithdrawal

    assert set(ApprovalWithdrawal.model_fields) == {"reason"}
    assert ApprovalWithdrawal.model_config.get("extra") == "forbid"
    original = _sources()["approvals.py"]
    local = original.replace(
        "    ApprovalWithdrawal,\n", "", 1
    ) + "\n\nclass ApprovalWithdrawal(BaseModel):\n    reason: str\n"
    withdraw_row = next(r for r in ROWS if r.request == "ApprovalWithdrawal")
    problems = ast_problems({"approvals.py": local}, rows=(withdraw_row,))
    assert any("not imported from model_schema" in p for p in problems)


# --- Acceptance 18: S2 does not widen the untyped surface of the two changed routes -------------

#: `ApprovalRequest`'s 13 top-level keys (`model_schema/approvals.py`; `workspace_id` joined
#: the 12 `to_dict` emitted, FD-1416 DP-2 (a)).
APPROVAL_REQUEST_KEYS = frozenset(
    {
        "id",
        "workspace_id",
        "artifact_ref",
        "artifact_type",
        "environment",
        "submitted_by",
        "submitted_at",
        "change_summary",
        "status",
        "approvers_required",
        "approvers_recorded",
        "decisions",
        "withdrawn_reason",
    }
)


@pytest.fixture
def client():
    from backend.tests.conftest_db import test_blob_bucket, test_database_url
    from fastapi.testclient import TestClient
    from pydantic import SecretStr

    from app.config import Environment, Settings
    from app.main import create_app

    settings = Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
        blob_bucket=test_blob_bucket(),
    )
    with TestClient(create_app(settings), raise_server_exceptions=False) as c:
        yield c


def _keys(response: Any, status: int) -> set[str]:
    assert response.status_code == status, response.text
    body = response.json()
    assert body["decisions"] == []
    return set(body)


def _assert_exact(keys: set[str], route: str) -> None:
    """`==`, not a subset: an undeclared add, drop or rename fails naming the key."""
    assert keys == APPROVAL_REQUEST_KEYS, (
        f"{route}: added {sorted(keys - APPROVAL_REQUEST_KEYS)}, "
        f"dropped {sorted(APPROVAL_REQUEST_KEYS - keys)}"
    )


@pytest.mark.req("FR-267")
@pytest.mark.asyncio
async def test_the_two_changed_approval_routes_return_exactly_the_declared_keys(
    client, database, workspace_id, grant
) -> None:
    """Condition 2 of the maintainer's DP-S2-6 (c) entry. The test **characterises today's
    output**: it was green at `14c7e805` for the `rating_version` and withdraw cases before
    Task 5 touched either route, and stays green, unchanged, after. The deployment branch is
    exercised through a Deployment Request put back in `review` by a fixture after its
    approval request was withdrawn (a row in `review` otherwise always holds its open request,
    which is why the generic route refuses it)."""
    from uuid import uuid4

    from backend.tests.test_deployments import (
        Seat,
        _approval_id,
        _request_for_prod,
    )
    from sqlalchemy import text

    from app.db.models import RatingVersionRow
    from model_schema import new_uuid7

    async def seat(*roles: str) -> Seat:
        made = Seat(workspace_id)
        for role in roles:
            await grant(role, principal_id=made.id)
        return made

    # rating_version: a version in `review`, submitted through the generic route.
    slug = f"rv-{uuid4().hex[:8]}"
    async with database.unit_of_work() as session:
        session.add(
            RatingVersionRow(
                workspace_id=workspace_id, slug=slug, version=1, status="review",
                dataset_version_id=uuid4(), model_ref="model:motor-ad-frequency@7",
                created_by=new_uuid7(),
            )
        )
    analyst = await seat("analyst")
    created = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": f"rating_version:{slug}@1", "change_summary": "go"},
        headers=analyst.headers,
    )
    _assert_exact(_keys(created, 201), "POST /api/v1/approval-requests (rating_version)")

    # withdraw
    approver = await seat("approver")
    withdrawn = client.post(
        f"/api/v1/approval-requests/{created.json()['id']}/withdraw",
        json={"reason": "not ready"},
        headers=approver.headers,
    )
    _assert_exact(_keys(withdrawn, 200), "POST /api/v1/approval-requests/{id}/withdraw")

    # deployment branch
    submitter, _, request = await _request_for_prod(client, database, workspace_id, seat)
    first = _approval_id(client, submitter, request["ref"])
    assert client.post(
        f"/api/v1/approval-requests/{first}/withdraw",
        json={"reason": "redo"},
        headers=approver.headers,
    ).status_code == 200
    async with database.unit_of_work() as session:
        await session.execute(
            text("UPDATE deployment_requests SET status = 'review' WHERE workspace_id = :w"),
            {"w": workspace_id},
        )
    again = client.post(
        "/api/v1/approval-requests",
        json={"artifact_ref": request["ref"], "change_summary": "again", "environment": "prod"},
        headers=submitter.headers,
    )
    _assert_exact(_keys(again, 201), "POST /api/v1/approval-requests (deployment)")


@pytest.mark.req("FR-267")
def test_the_key_set_check_names_an_added_dropped_or_renamed_key() -> None:
    """Broken input for `_assert_exact`: each of the three departures fails, naming the key."""
    added = set(APPROVAL_REQUEST_KEYS) | {"extra"}
    dropped = set(APPROVAL_REQUEST_KEYS) - {"withdrawn_reason"}
    renamed = (set(APPROVAL_REQUEST_KEYS) - {"environment"}) | {"env"}
    for broken, needle in ((added, "extra"), (dropped, "withdrawn_reason"), (renamed, "env")):
        with pytest.raises(AssertionError) as raised:
            _assert_exact(broken, "route")
        assert needle in str(raised.value)
