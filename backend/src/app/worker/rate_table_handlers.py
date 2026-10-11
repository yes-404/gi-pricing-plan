"""What the `rate_table.diff` Job actually does (03 §5.1, FR-232).

The 202 endpoint submits these. The Job exists only because one or both versions is
`storage: parquet` — the row-backed read path stays synchronous. The handler does not
re-decide anything: it computes the same diff the 200 path computes (same service
call, same parquet materialisation), then persists the artifact to the blob store and
returns `JobResult(kind="blob")` with the sha256 as the ref — the first blob-kind
result in the codebase, and the reason `GET /blobs/{sha256}` exists.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.platform import rate_tables as service
from app.worker.data_handlers import _bridge, _workspace
from app.worker.handlers import HANDLERS, register_handler
from model_schema import JobKind, JobResult
from pricing_core.progress import ProgressCallback

__all__ = ["register_rate_table_handlers"]


def _rate_table_diff(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`rate_table.diff` — the parquet-eligible diff, computed and stored as a blob.

    `against` arrives verbatim from the endpoint — `previous`, `seed`, or a version
    number as a string — and is re-parsed here, deterministically on immutable
    versions. The `job_id` the runner injects is not needed: the diff is a pure read
    and stamps no artifact.

    A `portfolio` parameter names the weighting Dataset Version. The service re-runs its
    checks under the Job's workspace, because the portfolio can lose its standing (be
    archived) between submit and run (`RL-1361` item 8): the Job then fails with the same
    code the 409 would have been.
    """
    progress = _bridge(callback)
    workspace_id = _workspace(parameters)
    raw_against: str = parameters["against"]
    against: str | int = int(raw_against) if raw_against.isdigit() else raw_against
    raw_portfolio = parameters.get("portfolio")
    portfolio = UUID(raw_portfolio) if raw_portfolio is not None else None
    progress.update(0.05, "materialising cells")

    async def work() -> str:
        diff = await service.diff(
            progress.database,
            workspace_id,
            parameters["slug"],
            int(parameters["version"]),
            against,
            blob_store=progress.blob_store,
            portfolio_dataset_version_id=portfolio,
        )
        payload = diff.model_dump_json().encode()
        async with progress.database.unit_of_work() as session:
            ref = await progress.blob_store.put(session, payload, "application/json")
            return ref.sha256

    sha256 = progress.run_on_loop(work())
    progress.update(1.0, "done")
    return JobResult(kind="blob", ref=sha256)


def _rate_table_diff_cells(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`rate_table.diff_cells` — every changed cell, in order, stored as chunk blobs and a manifest.

    The manifest's sha256 is the Job's `result.ref`, and the routes find it again by the `key`
    the Job's parameters carry. It serves the cells route and the diff route alike. The
    portfolio's checks run again under the Job's workspace (`RL-1361` item 8), so an archived
    portfolio fails the Job with `DATASET_NOT_VALIDATED`.
    """
    progress = _bridge(callback)
    workspace_id = _workspace(parameters)
    raw_against: str = parameters["against"]
    against: str | int = int(raw_against) if raw_against.isdigit() else raw_against
    raw_portfolio = parameters.get("portfolio")
    portfolio = UUID(raw_portfolio) if raw_portfolio is not None else None
    progress.update(0.05, "materialising cells")

    async def work() -> str:
        return await service.build_cells_artifact(
            progress.database,
            workspace_id,
            parameters["slug"],
            int(parameters["version"]),
            against,
            blob_store=progress.blob_store,
            portfolio_dataset_version_id=portfolio,
        )

    sha256 = progress.run_on_loop(work())
    progress.update(1.0, "done")
    return JobResult(kind="blob", ref=sha256)


def register_rate_table_handlers() -> None:
    """Register the `rate_table.*` handlers.

    A function rather than import-time side effects: `register_handler` refuses a
    duplicate (rightly), and a module that registers on import cannot be imported
    twice — which a test importing this module for a type would do. The `dataset.*`
    and `model.*` handlers set the same precedent.
    """
    for kind, handler in (
        (JobKind.RATE_TABLE_DIFF, _rate_table_diff),
        (JobKind.RATE_TABLE_DIFF_CELLS, _rate_table_diff_cells),
    ):
        if kind not in HANDLERS:
            register_handler(kind, handler)
