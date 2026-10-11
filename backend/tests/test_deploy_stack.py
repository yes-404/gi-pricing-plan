"""The compose deployment path's shape (WK-674 Slice 4; FR-434, FR-435, FR-415, FD-1211).

These tests read `deploy/docker-compose.yml` and need no Docker. They hold the *shape* the
runtime tests rely on: `api` does not need `worker`, migrations are their own one-shot step,
and the worker has a memory backstop. The runtime proofs (NFR-534 serving with no worker,
NFR-531 rolling N-1 to N) are in `test_deploy_stack_runtime.py`.

`yaml` is imported directly: PyYAML is a runtime dependency of `uvicorn[standard]`, which
`backend/pyproject.toml` declares, so it is present wherever this suite runs.
"""

from __future__ import annotations

import copy
import pathlib
from typing import Any

import pytest
import yaml

COMPOSE = pathlib.Path(__file__).resolve().parents[2] / "deploy" / "docker-compose.yml"


def _load() -> dict[str, Any]:
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))


def _needs(services: dict[str, Any], name: str) -> set[str]:
    """Every service `name` transitively starts, through `depends_on`."""
    seen: set[str] = set()
    todo = [name]
    while todo:
        deps = services[todo.pop()].get("depends_on") or {}
        for dep in deps:
            if dep not in seen:
                seen.add(dep)
                todo.append(dep)
    return seen


def _runs_alembic(service: dict[str, Any]) -> bool:
    command = service.get("command") or []
    words = command.split() if isinstance(command, str) else command
    return "alembic" in words


def api_needs_no_worker(compose: dict[str, Any]) -> list[str]:
    """FR-434 / NFR-534: `api` starts, and keeps serving, with `worker` absent."""
    services = compose["services"]
    return [
        f"api needs {name}"
        for name in sorted(_needs(services, "api") & {"worker"})
    ]


def migrations_are_their_own_step(compose: dict[str, Any]) -> list[str]:
    """FR-435: one one-shot service migrates; `api` waits for it; nothing else migrates."""
    services = compose["services"]
    problems = []
    migrate = services.get("migrate", {})
    if not _runs_alembic(migrate):
        problems.append("migrate does not run alembic")
    if migrate.get("restart") != "no":
        problems.append("migrate is not one-shot (restart must be 'no')")
    gate = (services["api"].get("depends_on") or {}).get("migrate", {})
    if gate.get("condition") != "service_completed_successfully":
        problems.append("api does not wait for migrate to complete successfully")
    problems += [
        f"{name} runs alembic" for name, svc in services.items()
        if name != "migrate" and _runs_alembic(svc)
    ]
    return problems


def worker_has_a_memory_backstop(compose: dict[str, Any]) -> list[str]:
    """FR-415: the worker service exists and a memory limit is applied to it."""
    worker = compose["services"].get("worker", {})
    command = worker.get("command") or []
    problems = []
    if "celery" not in command:
        problems.append("worker does not run celery")
    if not worker.get("mem_limit"):
        problems.append("worker has no mem_limit")
    return problems


def one_image_three_roles(compose: dict[str, Any]) -> list[str]:
    services = compose["services"]
    images = {services[n].get("image") for n in ("api", "worker", "migrate")}
    return [] if len(images) == 1 else [f"api/worker/migrate use {len(images)} images"]


CHECKS = [
    api_needs_no_worker,
    migrations_are_their_own_step,
    worker_has_a_memory_backstop,
    one_image_three_roles,
]


@pytest.mark.req("FR-434")
@pytest.mark.req("NFR-534")
def test_api_does_not_depend_on_the_worker() -> None:
    assert api_needs_no_worker(_load()) == []


@pytest.mark.req("FR-435")
@pytest.mark.req("NFR-531")
def test_migrations_are_a_separate_one_shot_step_that_api_waits_for() -> None:
    assert migrations_are_their_own_step(_load()) == []


@pytest.mark.req("FR-415")
@pytest.mark.req("FR-412")
def test_the_worker_service_carries_a_memory_limit() -> None:
    assert worker_has_a_memory_backstop(_load()) == []


@pytest.mark.req("FR-434")
def test_api_worker_and_migrate_are_one_image() -> None:
    assert one_image_three_roles(_load()) == []


@pytest.mark.req("FR-434")
@pytest.mark.req("FR-435")
def test_the_default_up_is_still_only_the_backing_services() -> None:
    """The path is behind the `app` profile: the default `up` claims nothing it cannot run."""
    services = _load()["services"]
    default = {n for n, s in services.items() if not s.get("profiles")}
    assert default == {"postgres", "redis", "minio"}


# -- broken-input proofs: each check names the break it exists to catch --------------------


def _break_api_imports_worker(c: dict[str, Any]) -> None:
    c["services"]["api"]["depends_on"]["worker"] = {"condition": "service_started"}


def _break_api_migrates_at_start(c: dict[str, Any]) -> None:
    c["services"]["api"]["command"] = ["sh", "-c", "alembic upgrade head && uvicorn app.main:app"]


def _break_migrate_not_awaited(c: dict[str, Any]) -> None:
    del c["services"]["api"]["depends_on"]["migrate"]


def _break_no_memory_limit(c: dict[str, Any]) -> None:
    del c["services"]["worker"]["mem_limit"]


@pytest.mark.req("FR-434")
@pytest.mark.req("FR-435")
@pytest.mark.req("FR-415")
@pytest.mark.parametrize(
    ("breaker", "check"),
    [
        (_break_api_imports_worker, api_needs_no_worker),
        (_break_api_migrates_at_start, migrations_are_their_own_step),
        (_break_migrate_not_awaited, migrations_are_their_own_step),
        (_break_no_memory_limit, worker_has_a_memory_backstop),
    ],
)
def test_each_check_goes_red_on_the_break_it_exists_for(breaker: Any, check: Any) -> None:
    broken = copy.deepcopy(_load())
    breaker(broken)
    assert check(broken), f"{check.__name__} stayed green on {breaker.__name__}"


@pytest.mark.req("FR-437")
def test_the_reference_keycloak_is_marked_as_the_deployers_to_operate() -> None:
    """FR-437: documented, in production mode, no default credential, accountability stated."""
    folder = COMPOSE.parent / "keycloak"
    readme = (folder / "README.md").read_text(encoding="utf-8")
    assert "operate it, you" in readme
    assert "accountable" in readme
    reference = yaml.safe_load((folder / "docker-compose.yml").read_text(encoding="utf-8"))
    service = reference["services"]["keycloak"]
    assert service["command"] == ["start"], "the reference runs production mode, not start-dev"
    assert "ports" not in service, "the reference publishes no port; the proxy fronts it"
    for key in ("KC_DB_PASSWORD", "KC_BOOTSTRAP_ADMIN_PASSWORD"):
        assert ":?" in service["environment"][key], f"{key} must be required, not defaulted"
