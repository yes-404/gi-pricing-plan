"""Application factory (07 §3.9).

`create_app` takes its settings rather than reading them, so a test builds an app with a
different environment without mutating the process. It is also where the ordering that
matters is expressed: trace binding is the outermost middleware, because a request that
fails inside another middleware must still produce a problem response carrying a
`trace_id`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import (
    approvals,
    audit,
    blobs,
    dataset_versions,
    datasets,
    demo,
    health,
    jobs,
    me,
    reference_tables,
    service_accounts,
    validation,
)
from app.api import settings as settings_api
from app.auth.oidc import OidcVerifier
from app.config import Settings, load_settings
from app.db.session import Database, database_probe
from app.errors import install_error_handlers
from app.observability.logging import configure_logging, get_logger
from app.observability.middleware import TraceMiddleware
from app.platform.blobs import BlobStore, blob_probe

__all__ = ["create_app"]

_log = get_logger("app.main")

API_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the API application. Fails loudly on invalid configuration (FR-PLAT-44)."""
    settings = settings or load_settings()
    configure_logging(settings.log_level)

    database = Database(settings)
    blob_store = BlobStore(settings)
    # One verifier per app: it caches the provider's key set, and a per-request client
    # would fetch the JWKS on every call and make the platform's own traffic the reason
    # logins start failing.
    oidc_verifier = OidcVerifier(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        # Probes are registered here rather than at import time so that building an app
        # has no global side effect — two apps in one test session must not share a probe
        # registry pointing at each other's engine.
        health.register_probe("database", database_probe(database))
        health.register_probe("blobs", blob_probe(blob_store))
        # Idempotent, and it is the one piece of setup that must happen before the first
        # upload rather than as a deploy step: a missing bucket fails every write, and the
        # failure reads as a credentials problem.
        await blob_store.ensure_bucket()
        yield
        health.clear_probes()
        await database.dispose()

    app = FastAPI(
        lifespan=lifespan,
        title="GI Pricing Platform API",
        version=settings.version,
        # OpenAPI 3.1 generated from the Pydantic models, published here and committed to
        # docs/contracts/ where CI checks it for drift (FR-PLAT-48).
        openapi_url="/openapi.json",
        docs_url="/docs",
    )

    app.add_middleware(TraceMiddleware)
    install_error_handlers(app)

    app.include_router(health.router)
    app.include_router(jobs.router, prefix=API_PREFIX)
    app.include_router(service_accounts.router, prefix=API_PREFIX)
    app.include_router(settings_api.router, prefix=API_PREFIX)
    app.include_router(me.router, prefix=API_PREFIX)
    app.include_router(audit.router, prefix=API_PREFIX)
    app.include_router(approvals.router, prefix=API_PREFIX)
    # `01` — Data. Order matters only for readability; FastAPI matches on the full path.
    app.include_router(blobs.router, prefix=API_PREFIX)
    app.include_router(demo.router, prefix=API_PREFIX)
    app.include_router(datasets.router, prefix=API_PREFIX)
    app.include_router(dataset_versions.router, prefix=API_PREFIX)
    app.include_router(validation.router, prefix=API_PREFIX)
    app.include_router(reference_tables.router, prefix=API_PREFIX)
    app.add_api_route(
        "/version",
        health.version_route(settings),
        methods=["GET"],
        tags=["platform"],
        summary="Service name, version and environment",
        response_model=health.VersionInfo,
    )

    # FR-PLAT-35: migrations are an explicit pre-deploy step. Nothing here runs them.
    app.state.settings = settings
    app.state.oidc_verifier = oidc_verifier
    app.state.database = database
    app.state.blob_store = blob_store

    _log.info(
        "application configured",
        extra={"environment": settings.environment.value, "version": settings.version},
    )
    return app
