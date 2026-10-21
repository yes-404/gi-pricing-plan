"""Application factory (07 §3.9).

`create_app` takes its settings rather than reading them, so a test builds an app with a
different environment without mutating the process. It is also where the ordering that
matters is expressed: trace binding is the outermost middleware, because a request that
fails inside another middleware must still produce a problem response carrying a
`trace_id`.
"""

from __future__ import annotations

import gc
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI
from sqlalchemy import select

from app.api import (
    approvals,
    audit,
    auth_config,
    blobs,
    custom_metrics,
    custom_objectives,
    dataset_versions,
    datasets,
    demo,
    deployments,
    dislocation_runs,
    environment_settings,
    environments,
    health,
    jobs,
    me,
    models,
    peril_structures,
    rate_tables,
    rating_algorithms,
    reference_tables,
    regression_suites,
    score,
    service_accounts,
    sub_graphs,
    traces,
    validation,
)
from app.api import settings as settings_api
from app.api.responses import problems, without_fastapi_validation_error
from app.auth.oidc import OidcVerifier
from app.config import Settings, load_settings
from app.db.models import EnvironmentRow
from app.db.session import Database, database_probe
from app.errors import install_error_handlers
from app.observability.logging import configure_logging, get_logger
from app.observability.middleware import TraceMiddleware
from app.platform.blobs import BlobStore, blob_probe
from app.platform.bundle_slot import BundleSlot
from app.platform.deployment_switch import (
    LiveRefs,
    RedisSwitch,
    SwitchMember,
    SwitchMessage,
    SwitchSubscription,
    build_switch_client,
    process_id,
)
from app.platform.rate_limit import RateLimiter, build_redis_client
from app.platform.settings import validate_setting_overrides
from app.platform.tenancy import require_tenant_binding
from model_schema import OidcAuthConfig
from pricing_core.rating.compile import assert_integer_minor_round_trip

__all__ = ["create_app"]

_log = get_logger("app.main")

API_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the API application. Fails loudly on invalid configuration (FR-447)."""
    settings = settings or load_settings()
    configure_logging(settings.log_level)

    database = Database(settings)
    blob_store = BlobStore(settings)
    # One verifier per app: it caches the provider's key set, and a per-request client
    # would fetch the JWKS on every call and make the platform's own traffic the reason
    # logins start failing.
    oidc_verifier = OidcVerifier(settings)

    @asynccontextmanager
    async def lifespan(running: FastAPI) -> AsyncIterator[None]:
        # FR-273: "A startup self-check asserts the round-trip; failing it prevents
        # the service starting." First, before any I/O — it is pure computation, and a
        # machine that fails it must never reach the probes or the blob bucket below.
        # `assert_integer_minor_round_trip` raises a bare `AssertionError` on failure,
        # which this lifespan does not catch, so it propagates and the app never starts
        # (WK-671 Task 1.4, F-W11-1-3 — the function has existed since W9-2 with no
        # production caller; this is the first one).
        assert_integer_minor_round_trip()
        # FR-447 (FD-1320): a `GIP_SETTING_*` variable the registry cannot honour — unknown,
        # ill-typed, out of range, or for an Environment-only key (`RL-1311` item 3a) —
        # stops the process here, with the variable named, rather than failing at first use.
        validate_setting_overrides(settings)
        # FR-436: every store must be bound to this deployment's tenant, or the process
        # does not start. Before the probes and before any write to a store, and the check
        # itself orders the stores so that the read-only database check comes first. It also
        # ensures the bucket, which the marker needs.
        await require_tenant_binding(settings, database, blob_store)
        # Probes are registered here rather than at import time so that building an app
        # has no global side effect — two apps in one test session must not share a probe
        # registry pointing at each other's engine.
        health.register_probe("database", database_probe(database))
        health.register_probe("blobs", blob_probe(blob_store))
        # FR-452 (RL-1347 rule 5): one Redis client per process for the scoring rate limit,
        # built here and closed below — never per request. Building it opens no connection,
        # so an unavailable Redis does not stop startup; the limiter fails open.
        redis_client = build_redis_client(settings.redis_url.get_secret_value())
        running.state.rate_limiter = RateLimiter(redis_client)
        # FR-268 (PL-1766 D5.8, the maintainer's 2026-10-18 23:03:15 BST ruling (A)): this
        # process answers the deployment switch and holds its own `live` reference. Subscribe
        # first, then load: the DB is ahead of or equal to any COMMIT (DB first), so loading
        # last can only catch up, never lose a deployment that committed in between. A fresh
        # process therefore serves the latest committed Deployment of every Environment.
        # Unlike the rate limiter this does not fail open: a process that cannot subscribe
        # would silently miss every switch, so it does not start.
        switch_client = build_switch_client(settings.redis_url.get_secret_value())
        switch = RedisSwitch(switch_client, f"{settings.environment.value}:{settings.tenant_id}")
        # One channel per platform Environment (`dev`, `uat`, `prod`, ...). An Environment
        # created after this process started is not subscribed until it restarts: a deploy into
        # it names no such process. That gap is part of FD-1823 (MEDIUM, WK-674).
        async with database.session() as session:
            environments = list(
                (
                    await session.execute(
                        select(EnvironmentRow.slug).where(EnvironmentRow.retired_at.is_(None))
                    )
                ).scalars()
            )

        async def hydrate(message: SwitchMessage) -> None:
            await score.hydrate_for_switch(database, blob_store, running.state.bundle_slot, message)

        subscription = SwitchSubscription(
            switch,
            switch_client,
            SwitchMember(process_id(), running.state.live_refs, hydrate),
            environments,
        )
        await subscription.start()
        async with database.session() as session:
            await running.state.live_refs.load_latest(session)
        running.state.switch = switch
        # RL-1685 (PL-1454 DP-4): everything built above lives for the process. Moving it
        # into the permanent generation takes it out of every later gen2 collection, whose
        # pause (about 200 to 300 ms on the Task 0 record) was the request-path stall.
        # Last, so the freeze covers the whole start-up and nothing built after it escapes it.
        gc.freeze()
        yield
        health.clear_probes()
        await subscription.stop()
        await switch_client.aclose()
        await redis_client.aclose()
        await database.dispose()

    app = FastAPI(
        lifespan=lifespan,
        title="GI Pricing Platform API",
        version=settings.version,
        # OpenAPI 3.1 generated from the Pydantic models, published here and committed to
        # docs/contracts/ where CI checks it for drift (FR-451).
        openapi_url="/openapi.json",
        docs_url="/docs",
    )

    # The document FastAPI assembles, minus the `422` it injects into any operation that
    # has a parameter — a shape this API replaced and never emits (FR-451). Applied
    # here rather than in `scripts/generate-contracts.py` so the served document and the
    # committed contract are the same bytes; the script reads this same method.
    _assemble = app.openapi

    def _openapi() -> dict[str, Any]:
        if app.openapi_schema is None:
            app.openapi_schema = without_fastapi_validation_error(_assemble())
        return app.openapi_schema

    app.openapi = _openapi  # type: ignore[method-assign]

    app.add_middleware(TraceMiddleware)
    install_error_handlers(app)

    # FR-452 / RL-1687: an operation declares `429 RATE_LIMITED` iff it can return one (the
    # lead's ruling "2026-10-16 10:30:18 BST" as amended). Every router the management limiter
    # counts is included through this one function and declares it once, here, not per route.
    # `score.router` is the one exception: it mixes the scoring limit (`POST /score`), the
    # management limit (`POST /score/compare`) and no limit (`POST /score/batch`), so it
    # declares per route.
    def counted(router: APIRouter) -> None:
        app.include_router(router, prefix=API_PREFIX, responses=problems(429))

    app.include_router(health.router)
    counted(jobs.router)
    counted(service_accounts.router)
    counted(environments.router)
    counted(environment_settings.router)
    counted(deployments.router)
    counted(settings_api.router)
    counted(me.router)
    counted(audit.router)
    counted(approvals.router)
    # `01` — Data. Order matters only for readability; FastAPI matches on the full path.
    counted(blobs.router)
    counted(demo.router)
    counted(models.router)
    counted(rating_algorithms.router)
    counted(sub_graphs.router)
    counted(rate_tables.router)
    counted(regression_suites.router)
    counted(dislocation_runs.router)
    counted(peril_structures.router)
    counted(custom_objectives.router)
    counted(custom_metrics.router)
    counted(datasets.router)
    counted(dataset_versions.router)
    counted(validation.router)
    counted(reference_tables.router)
    app.include_router(score.router, prefix=API_PREFIX)
    counted(traces.router)
    app.add_api_route(
        "/version",
        health.version_route(settings),
        methods=["GET"],
        tags=["platform"],
        summary="Service name, version and environment",
        response_model=health.VersionInfo,
    )
    # FR-394: the browser login cannot start behind an auth gate, so this publishes
    # unauthenticated — the issuer and the client_id are public by design, and the route
    # is mounted with the prefix because the requirement names the full path.
    app.add_api_route(
        f"{API_PREFIX}/auth/config",
        auth_config.auth_config_route(settings),
        methods=["GET"],
        tags=["platform"],
        summary="The OIDC values the browser login needs",
        response_model=OidcAuthConfig,
    )

    # FR-435: migrations are an explicit pre-deploy step. Nothing here runs them.
    app.state.settings = settings
    app.state.oidc_verifier = oidc_verifier
    app.state.database = database
    app.state.blob_store = blob_store
    # One slot per worker process, built once at startup and read per request — the same
    # lifetime `blob_store` has. Deliberately *not* per request: a slot rebuilt per call
    # holds nothing, which is the state option (a) was rejected for (RL-882).
    app.state.bundle_slot = BundleSlot(capacity=settings.bundle_slot_capacity)
    # This process's `live` reference (FR-268). Empty until the lifespan loads the latest
    # committed Deployments; written afterwards only by a COMMIT this process acknowledged.
    app.state.live_refs = LiveRefs()

    _log.info(
        "application configured",
        extra={"environment": settings.environment.value, "version": settings.version},
    )
    return app
