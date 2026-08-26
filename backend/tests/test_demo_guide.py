"""The demo entrance's guide (FR-PLAT-53, FR-PLAT-54).

The guide's purpose is telling a person what to trust, so the property under test is not
"it renders" but **"it cannot claim more than the repository has"**. Every assertion below
is about that: a view is implemented because the router routes it, a workstream is closed
because the roadmap says so, and the whole surface is absent where development identity is.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Environment, Settings
from app.demo.guide import GuideSourceMissingError, build_guide, repository_root
from app.main import create_app


def _fixture_repo(root: Path, *, routes: tuple[str, ...] = ("/data",)) -> Path:
    """A miniature checkout: one spec, one router, one contract, one roadmap."""
    specs = root / "docs" / "specs"
    specs.mkdir(parents=True)
    (specs / "01-data-management.md").write_text(
        "### 5.3 Frontend views\n\n"
        "| View | Route | Contents |\n"
        "|---|---|---|\n"
        "| Dataset list | `/data` | Datasets with status |\n"
        "| **Validation report** | `/data/:slug/validation` | The banner |\n"
        "\n## 6. Workflows\n",
        encoding="utf-8",
    )
    (specs / "03-rating-engine.md").write_text(
        "### 5.3 Frontend views\n\n"
        "| View | Route | Contents |\n"
        "|---|---|---|\n"
        "| Rating version list | `/rating` | Versions by status |\n"
        "\n## 6. Workflows\n",
        encoding="utf-8",
    )
    router = root / "frontend" / "src" / "router"
    router.mkdir(parents=True)
    (router / "index.ts").write_text(
        "const routes = [\n"
        + "".join(f'  {{ path: "{route}" }},\n' for route in routes)
        + "];\n",
        encoding="utf-8",
    )
    contract = root / "docs" / "contracts" / "openapi"
    contract.mkdir(parents=True)
    (contract / "generated.json").write_text(
        json.dumps(
            {
                "paths": {
                    "/api/v1/datasets": {
                        "get": {"tags": ["datasets"]},
                        "post": {"tags": ["datasets"]},
                        "parameters": [],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    (root / "docs" / "roadmap.md").write_text(
        "#### Phase 1a status\n\n"
        "| WS | Scope | Status |\n"
        "|---|---|---|\n"
        "| ~~**W4**~~ ✔ | Data | ✔ **closed 2026-08-15** |\n"
        "| **W6a** | Frontend | **next** |\n"
        "\n### Something else\n\n"
        "| WS | Scope | Status |\n"
        "|---|---|---|\n"
        "| **W99** | Not a status table | should not appear |\n",
        encoding="utf-8",
    )
    return root


@pytest.mark.req("FR-PLAT-54")
def test_a_view_is_implemented_because_the_router_routes_it(tmp_path: Path) -> None:
    """Not because anyone said so. The claim is one file agreeing with another."""
    guide = build_guide(_fixture_repo(tmp_path))
    by_route = {view.route: view for view in guide.views}
    assert by_route["/data"].implemented is True
    assert by_route["/data/:slug/validation"].implemented is False
    assert by_route["/rating"].implemented is False
    # The bolded name in the spec table is the view's name, not part of it.
    assert by_route["/data/:slug/validation"].name == "Validation report"
    assert by_route["/rating"].module == "RATE"


@pytest.mark.req("FR-PLAT-54")
def test_the_guide_names_what_is_not_functional(tmp_path: Path) -> None:
    """The valuable half.

    A demo showing only what works invites the reader to assume everything else does too —
    which is the failure `CLAUDE.md` §13 exists to prevent, in the one place a person reads.
    """
    guide = build_guide(_fixture_repo(tmp_path))
    assert {view.route for view in guide.not_functional} == {
        "/data/:slug/validation",
        "/rating",
    }
    assert {view.route for view in guide.implemented_views} == {"/data"}


@pytest.mark.req("FR-PLAT-54")
def test_workstream_state_is_the_roadmaps_word_not_a_second_judgement(
    tmp_path: Path,
) -> None:
    """A guide that decided for itself would be a second status table, and they would
    disagree. Only tables under a `#### Phase … status` heading are read."""
    guide = build_guide(_fixture_repo(tmp_path))
    assert [(w.workstream, w.closed) for w in guide.workstreams] == [
        ("W4", True),
        ("W6a", False),
    ]
    assert all(w.phase == "Phase 1a" for w in guide.workstreams)


@pytest.mark.req("FR-PLAT-54")
def test_a_missing_source_is_refused_rather_than_half_answered(tmp_path: Path) -> None:
    """A partial guide looks like a platform missing a capability."""
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    with pytest.raises(GuideSourceMissingError):
        build_guide(tmp_path)


@pytest.mark.req("FR-PLAT-54")
def test_the_real_repository_derives_a_guide() -> None:
    """The fixture proves the parser; this proves it against the repository it describes."""
    guide = build_guide(repository_root())
    routes = {view.route for view in guide.implemented_views}
    assert "/data" in routes
    assert "/reference" in routes
    assert any(view.module == "MODEL" for view in guide.not_functional)
    assert any(group.tag == "datasets" for group in guide.api)


@pytest.mark.req("FR-PLAT-53")
def test_the_entrance_is_absent_where_development_identity_is(tmp_path: Path) -> None:
    """FR-PLAT-53: one switch, and it is the refusal that already exists.

    `dev_auth_enabled` is `False` by default and refuses to start in a deployed
    environment. A page listing every route beside a pre-authenticated session is a genuine
    hole if it ever ships, and a second flag is one more thing that can be left on.
    """
    settings = Settings(environment=Environment.LOCAL, version="test", dev_auth_enabled=False)
    with TestClient(create_app(settings), raise_server_exceptions=False) as client:
        refused = client.get("/api/v1/demo/guide")
        # 404, not 401: the surface does not exist here, and 401 would say "authenticate
        # and try again" — the opposite of what is true. This is why the flag is a
        # router-level dependency, solved before the caller is.
        assert refused.status_code == 404, refused.text
        assert refused.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-PLAT-53")
async def test_the_guide_is_served_where_the_demo_runs(
    tmp_path: Path, principal, workspace_id, membership
) -> None:
    from backend.tests.conftest_db import test_database_url
    from pydantic import SecretStr

    from app.api.deps import DEV_PRINCIPAL_HEADER

    # The dev caller resolves through the memberships the database holds (W6b-11), so
    # this client needs the test database, not the default DSN.
    settings = Settings(
        environment=Environment.LOCAL,
        version="test",
        dev_auth_enabled=True,
        database_url=SecretStr(test_database_url()),
    )
    await membership()
    with TestClient(create_app(settings), raise_server_exceptions=False) as client:
        response = client.get(
            "/api/v1/demo/guide",
            headers={
                DEV_PRINCIPAL_HEADER: str(principal.id),
                "Workspace-Id": str(workspace_id),
            },
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["generated_from"], "the guide names the files it was derived from"
    assert any(view["route"] == "/data" and view["implemented"] for view in body["views"])


@pytest.mark.req("FR-PLAT-54")
def test_every_spec_that_declares_views_contributes_them() -> None:
    """The guide cannot go stale; it *could* silently go empty.

    `_spec_views` matches `### 5.3 Frontend views` exactly and returns nothing when the
    heading moves — no error, docs audit green, suite green. Renaming `07`'s heading
    dropped six views and the earlier test did not notice, because it asserted only that
    `/data` and `/reference` exist: `01` and `02` were protected by accident and `03` to `07`
    by nothing.

    Derived from the files rather than from a list, so a *new* spec is covered too.
    """
    from app.demo.guide import _MODULES

    root = repository_root()
    declaring = {
        spec.stem
        for spec in sorted((root / "docs" / "specs").glob("*.md"))
        if "### 5.3 Frontend views" in spec.read_text(encoding="utf-8")
    }
    assert declaring, "no spec declares a view table — the heading itself must have moved"

    guide = build_guide(root)
    contributing = {view.spec for view in guide.views}
    assert declaring == contributing, (
        f"specs declaring views but contributing none: {sorted(declaring - contributing)}"
    )
    # And the map that gates which specs are looked at must not silently drop one.
    assert declaring <= set(_MODULES), f"not in _MODULES: {sorted(declaring - set(_MODULES))}"


@pytest.mark.req("FR-PLAT-54")
def test_the_roadmap_yields_workstreams_and_names_the_phases_it_omits() -> None:
    """`_workstreams` matches `#### Phase … status` exactly and returns () when it moves.

    Nothing asserted the real roadmap produced any workstream at all, so the section could
    empty itself with every check green — and an empty section reads as a platform with no
    workstreams rather than as a broken parser.
    """
    guide = build_guide(repository_root())
    assert guide.workstreams, "the roadmap's status table produced nothing"
    assert all(w.phase.startswith("Phase ") for w in guide.workstreams)
    # The scoping fact the page renders: which phases have no status table yet. If this
    # were empty, "N workstreams closed" would read as covering the whole project.
    assert guide.phases_without_status


@pytest.mark.req("FR-PLAT-54")
def test_a_commented_out_route_is_not_built(tmp_path: Path) -> None:
    """"Built" is a fact about the router, so it must not be a fact about its comments.

    A `// TODO { path: "/rating" }` rendered a green badge for a view nobody had started,
    on the page whose only job is saying what is worth clicking.
    """
    root = _fixture_repo(tmp_path)
    (root / "frontend" / "src" / "router" / "index.ts").write_text(
        'const routes = [\n'
        '  { path: "/data" },\n'
        '  // TODO one day: { path: "/rating" },\n'
        '  /* { path: "/data/:slug/validation" } */\n'
        "];\n",
        encoding="utf-8",
    )
    by_route = {view.route: view for view in build_guide(root).views}
    assert by_route["/data"].implemented is True
    assert by_route["/rating"].implemented is False
    assert by_route["/data/:slug/validation"].implemented is False


@pytest.mark.req("FR-PLAT-54")
def test_the_guide_names_the_endpoints_a_spec_declares_and_the_contract_lacks() -> None:
    """FR-PLAT-54's "not yet functional", applied to the API.

    The page reported "63 endpoints published" and nothing else — true, and silent about
    the declared routes that do not exist, which is the half the question asks about.

    `modules` names the modules that still have at least one endpoint declared but not
    published. That set is expected to shrink as modules close their endpoint axis — MODEL
    dropped out on 2026-08-20 when the custom-metrics slice's Task 1 and Task 5 published
    the last of its 40 declared endpoints — so a future failure here most likely means a
    module finished, not that something broke.
    """
    guide = build_guide(repository_root())
    assert guide.unpublished_endpoints, "no module declares an unbuilt endpoint?"
    modules = {endpoint.module for endpoint in guide.unpublished_endpoints}
    assert {"RATE"} <= modules, modules


@pytest.mark.req("FR-PLAT-54")
def test_a_route_carrying_a_query_is_matched_on_its_path(tmp_path: Path) -> None:
    """The query is the view's input, not part of where the view lives.

    `02` §5.3 writes `/models/:slug/diagnostics?version=` because `?version=` is what that
    view reads, and a router path never carries a query. Compared raw the two can never
    match, so the guide rendered a red "built" badge for two views that are built and
    routed — the commented-out-route defect below, in the other direction, on the one page
    whose whole job is saying what is worth clicking.
    """
    root = _fixture_repo(tmp_path, routes=("/data", "/data/:slug/validation"))
    (root / "docs" / "specs" / "01-data-management.md").write_text(
        "### 5.3 Frontend views\n\n"
        "| View | Route | Contents |\n"
        "|---|---|---|\n"
        "| Validation report | `/data/:slug/validation?tab=` | The banner |\n"
        "| Profile | `/data/:slug/profile?column=` | One column |\n"
        "\n## 6. Workflows\n",
        encoding="utf-8",
    )
    by_route = {view.route: view for view in build_guide(root).views}
    assert by_route["/data/:slug/validation?tab="].implemented is True
    # Both directions, because stripping a suffix is exactly the change that could turn
    # every badge green: a query on a route nobody declared stays not built.
    assert by_route["/data/:slug/profile?column="].implemented is False
