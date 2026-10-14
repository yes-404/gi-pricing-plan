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
import sys
from typing import Any

import pytest
import yaml

from app.platform.jobs import DEFAULT_QUEUE_FOR_KIND
from app.worker.celery_app import RELAY_QUEUE

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
    return any("alembic" in word for word in words)


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


def _celery_workers(compose: dict[str, Any]) -> dict[str, list[str]]:
    """Every service whose command runs `celery -A app.worker.entrypoint worker`."""
    found: dict[str, list[str]] = {}
    for name, svc in compose["services"].items():
        command = svc.get("command") or []
        words = command.split() if isinstance(command, str) else list(command)
        if "celery" in words and "worker" in words:
            found[name] = words
    return found


def _queues_of(words: list[str]) -> set[str] | None:
    """The comma-split argument after `--queues`, or None when the command has none."""
    if "--queues" not in words:
        return None
    return set(words[words.index("--queues") + 1].split(","))


def worker_has_a_memory_backstop(compose: dict[str, Any]) -> list[str]:
    """FR-415 (PL-8022 DP-Q1 (b)): at least one worker exists and EVERY worker has a limit."""
    workers = _celery_workers(compose)
    problems = [] if workers else ["no worker service runs celery"]
    problems += [
        f"{name} has no mem_limit"
        for name in sorted(workers)
        if not compose["services"][name].get("mem_limit")
    ]
    return problems


def routed_queues() -> set[str]:
    """Every pool the routing table names, read from the table at call time (PL-8022 E4.2)."""
    return {q.value for q in DEFAULT_QUEUE_FOR_KIND.values()}


def consumed_queues(compose: dict[str, Any]) -> set[str]:
    """The union of `--queues` over every celery worker service."""
    consumed: set[str] = set()
    for words in _celery_workers(compose).values():
        consumed |= _queues_of(words) or set()
    return consumed


def every_routed_queue_is_consumed(compose: dict[str, Any]) -> list[str]:
    """FR-415 / PL-8022 E4.2 + E4.4: consumed >= routed | {RELAY_QUEUE}; derived, not listed."""
    problems = [
        f"worker service {name} names no --queues"
        for name, words in sorted(_celery_workers(compose).items())
        if _queues_of(words) is None
    ]
    expected = routed_queues() | {RELAY_QUEUE.value}
    return problems + [
        f"queue {q} is routed to and never consumed"
        for q in sorted(expected - consumed_queues(compose))
    ]


def each_worker_consumes_one_pool(compose: dict[str, Any]) -> list[str]:
    """FR-405 (PL-8022 DP-Q1 (b)): one service per pool, so each pool is sized independently."""
    return [
        f"worker service {name} consumes {len(queues)} queues"
        for name, words in sorted(_celery_workers(compose).items())
        if len(queues := _queues_of(words) or set()) > 1
    ]


def one_image_three_roles(compose: dict[str, Any]) -> list[str]:
    services = compose["services"]
    images = {services[n].get("image") for n in ("api", "worker", "migrate")}
    return [] if len(images) == 1 else [f"api/worker/migrate use {len(images)} images"]


CHECKS = [
    api_needs_no_worker,
    migrations_are_their_own_step,
    worker_has_a_memory_backstop,
    every_routed_queue_is_consumed,
    each_worker_consumes_one_pool,
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


@pytest.mark.req("FR-415")
def test_every_routed_queue_is_consumed() -> None:
    assert consumed_queues(_load()) >= routed_queues() | {RELAY_QUEUE.value}, (
        every_routed_queue_is_consumed(_load())
    )


@pytest.mark.req("FR-405")
def test_each_worker_service_consumes_one_pool() -> None:
    assert each_worker_consumes_one_pool(_load()) == []


@pytest.mark.req("FR-415")
def test_the_consumed_set_is_derived_from_the_table_not_copied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hard-coded expected set cannot name a pool the table gained after it was written."""

    class _Phantom:
        value = "phantom"

    from app.platform.jobs import JobKind

    table: dict[Any, Any] = {**DEFAULT_QUEUE_FOR_KIND, JobKind.BLOB_GC: _Phantom()}
    monkeypatch.setattr(sys.modules[__name__], "DEFAULT_QUEUE_FOR_KIND", table)
    assert "queue phantom is routed to and never consumed" in every_routed_queue_is_consumed(
        _load()
    )


@pytest.mark.req("FR-415")
def test_the_relay_queue_is_asserted_even_when_no_kind_routes_to_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DP-Q2 (a): route every kind to `compute` and drop `default` from the workers.

    The routed-only form (b) passes on this input; the relay-aware form (a) names `default`.
    """
    from app.platform.jobs import JobQueue

    moved = dict.fromkeys(DEFAULT_QUEUE_FOR_KIND, JobQueue.COMPUTE)
    monkeypatch.setattr(sys.modules[__name__], "DEFAULT_QUEUE_FOR_KIND", moved)
    compose = copy.deepcopy(_load())
    _drop_queue_everywhere(compose, "default")
    assert routed_queues() <= consumed_queues(compose), "form (b) is meant to pass here"
    assert "queue default is routed to and never consumed" in every_routed_queue_is_consumed(
        compose
    )


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
    for name in _celery_workers(c):
        del c["services"][name]["mem_limit"]
        break


def _drop_queue_everywhere(c: dict[str, Any], queue: str) -> None:
    for name, words in _celery_workers(c).items():
        queues = (_queues_of(words) or set()) - {queue}
        words[words.index("--queues") + 1] = ",".join(sorted(queues))
        c["services"][name]["command"] = words


def _break_drop_io_consumer(c: dict[str, Any]) -> None:
    _drop_queue_everywhere(c, "io")


def _break_drop_scoring_consumer(c: dict[str, Any]) -> None:
    _drop_queue_everywhere(c, "scoring")


def _break_worker_consumes_two_pools(c: dict[str, Any]) -> None:
    name = next(iter(_celery_workers(c)))
    words = _celery_workers(c)[name]
    words[words.index("--queues") + 1] = "compute,scoring"
    c["services"][name]["command"] = words


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
        (_break_drop_io_consumer, every_routed_queue_is_consumed),
        (_break_drop_scoring_consumer, every_routed_queue_is_consumed),
        (_break_worker_consumes_two_pools, each_worker_consumes_one_pool),
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
