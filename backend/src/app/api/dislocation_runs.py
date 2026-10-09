"""The Dislocation Run routes (`03` §5.1, FR-263, FR-265, FR-1399; `RL-1264`, `RL-1504`).

`POST /dislocation-runs` answers 202 with a `dislocation.run` Job; `POST …/estimate` answers
what such a run would cost, before launch, by the same code path; `GET …/{id}` is the
persisted artifact; `GET …/{id}/movers` is the one reader of the movers blob, which holds
`dislocation_frame`'s own columns only and is joined to the portfolio's columns here at read
(`RL-1504` item 5, NFR-499). The shapes are `model-schema`'s, never route-local.
"""

from __future__ import annotations

import io
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

import polars as pl
from fastapi import APIRouter, Depends, Request, Response, status

from app.api.authz import requires
from app.api.deps import Caller, DatabaseDep, job_identity
from app.api.responses import problems
from app.errors import PlatformError
from app.platform import dislocation_runs as service
from app.platform import jobs as job_service
from app.platform import rbac
from app.platform.blobs import BlobStore
from app.platform.datasets import read_version
from model_schema import JobKind, Permission
from model_schema.dislocation import DislocationEstimate, DislocationRun, DislocationSpec
from model_schema.jobs import Job
from pricing_core.rating.analysis import read_portfolio

router = APIRouter(tags=["rating"])

CompileDep = Annotated[Caller, Depends(requires(Permission.RATING_COMPILE))]
ReadDep = Annotated[Caller, Depends(requires(Permission.RATING_READ))]


def _blob_store(request: Request) -> BlobStore:
    store: BlobStore = request.app.state.blob_store
    return store


BlobStoreDep = Annotated[BlobStore, Depends(_blob_store)]


async def _require_dataset_read(database: DatabaseDep, caller: Caller) -> None:
    """`dataset:read` on the portfolio, checked in the handler as `rate_tables.py` does: the
    portfolio is named in the body or on the stored run, so the route-wide dependency cannot
    carry it (FR-345)."""
    async with database.session() as session:
        await rbac.require_permission(
            session,
            workspace_id=caller.workspace_id,
            principal=caller.principal,
            permission=Permission.DATASET_READ,
            credential_permissions=caller.permissions,
        )


@router.post(
    "/dislocation-runs/estimate",
    summary="The estimated cost of a Dislocation Run, before launch",
    responses=problems(401, 403, 404, 422),
)
async def estimate_dislocation_run(
    spec: DislocationSpec,
    caller: CompileDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
) -> DislocationEstimate:
    """**200** with the rating count and single-worker hours this spec's run would take
    (`RL-1264` item 3); **422** `VALIDATION_FAILED` for groups that do not partition the
    derived changes (FR-1399). Writes no Job and applies no size bound: the caller sees the
    estimate that the run's own bound is compared with."""
    await _require_dataset_read(database, caller)
    async with database.session() as session:
        return await service.estimate_for_spec(
            session, workspace_id=caller.workspace_id, spec=spec, blob_store=blob_store
        )


@router.post(
    "/dislocation-runs",
    summary="Start a Dislocation Run",
    status_code=status.HTTP_202_ACCEPTED,
    responses=problems(401, 403, 404, 422),
)
async def start_dislocation_run(
    spec: DislocationSpec,
    caller: CompileDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
    response: Response,
) -> Job:
    """**202** with a `dislocation.run` Job. **422** `VALIDATION_FAILED`, with no Job, when the
    change groups do not partition the derived changes (FR-1399, naming each change) or when
    the run is estimated above the single-Job bound (`RL-1504` item 1, naming K, the policy
    count and the estimate)."""
    await _require_dataset_read(database, caller)
    async with database.unit_of_work() as session:
        estimate = await service.estimate_for_spec(
            session, workspace_id=caller.workspace_id, spec=spec, blob_store=blob_store
        )
        service.refuse_over_single_job_bound(
            estimate, groups=None if spec.change_groups is None else len(spec.change_groups)
        )
        job = await job_service.submit(
            session,
            JobKind.DISLOCATION_RUN,
            {**job_identity(caller), "spec": spec.model_dump(mode="json")},
            caller.principal,
            workspace_id=caller.workspace_id,
        )
    response.headers["Location"] = f"/api/v1/jobs/{job.id}"
    return job


@router.get(
    "/dislocation-runs/{run_id}",
    summary="Read a Dislocation Run",
    responses=problems(401, 403, 404, 422),
)
async def get_dislocation_run(
    run_id: UUID, caller: ReadDep, database: DatabaseDep
) -> DislocationRun:
    """**200** with the persisted artifact (FR-265); **404** `NOT_FOUND` for an unknown id or
    another workspace's."""
    async with database.session() as session:
        row = await service.fetch_run(session, workspace_id=caller.workspace_id, run_id=run_id)
    return DislocationRun.model_validate(row.run)


def _json_value(value: Any) -> Any:
    """Exposure is a `Decimal` after `read_portfolio`; on the wire it is a string (FR-10)."""
    return str(value) if isinstance(value, Decimal) else value


@router.get(
    "/dislocation-runs/{run_id}/movers",
    summary="Read a Dislocation Run's movers, joined to the portfolio's columns",
    responses=problems(401, 403, 404, 422),
)
async def get_dislocation_run_movers(
    run_id: UUID,
    caller: ReadDep,
    database: DatabaseDep,
    blob_store: BlobStoreDep,
) -> list[dict[str, Any]]:
    """The run's movers in §4.6's mover order, each row joined at read on `quote_id` to the
    portfolio columns of the run's portfolio Dataset Version. Needs `rating:read` and
    `dataset:read`; the stored blob holds no portfolio column (`RL-1504` item 5, NFR-499), and
    this is its one reader (`GET /api/v1/blobs/{sha256}` refuses it)."""
    await _require_dataset_read(database, caller)
    async with database.session() as session:
        row = await service.fetch_run(session, workspace_id=caller.workspace_id, run_id=run_id)
        version = await read_version(
            session, workspace_id=caller.workspace_id, version_id=row.portfolio_dataset_version_id
        )
        movers = pl.read_parquet(
            io.BytesIO(
                await service.read_stored_blob(
                    session, blob_store, row.movers_blob_sha256, "The run's movers"
                )
            )
        )
        portfolio = pl.read_parquet(
            io.BytesIO(
                await service.read_stored_blob(
                    session,
                    blob_store,
                    service.portfolio_table(version)["blob"]["sha256"],
                    "The portfolio's table",
                )
            )
        )
    try:
        checked = read_portfolio(portfolio.lazy()).collect()
    except ValueError as exc:  # the portfolio no longer reads as §4.8's frame
        raise PlatformError(
            "VALIDATION_FAILED", "Portfolio does not read as a frame", 422, str(exc)
        ) from exc
    joined = movers.join(checked, on="quote_id", how="left", maintain_order="left")
    return [{k: _json_value(v) for k, v in r.items()} for r in joined.iter_rows(named=True)]
