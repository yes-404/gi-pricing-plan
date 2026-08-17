"""What the `dataset.*` Jobs actually do (`01` §3.1 to §3.4).

The four 202 endpoints submit these. Until they existed the endpoints were honest about
returning a Job and the Job never ran, which is the shape of half a feature: everything
looks right and nothing happens.

**These are platform handlers, not `pricing-core` ones.** They read blobs, write rows and
emit audit events, so they need the data layer — which they take from the `JobProgress`
bridge rather than building their own engine, keeping one connection pool and one audit
path. The maths they call (`ingest`, `validate`, `profile`) knows nothing about any of it.

Each runs in a worker thread and marshals its async work back onto the loop with
`progress.run_on_loop`.
"""

from __future__ import annotations

import io
from typing import Any, Final
from uuid import UUID

import polars as pl

from app.data.ingestion import PARQUET_MEDIA_TYPE, ingest_upload
from app.db.models import BlobRow, DatasetVersionRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import datasets as dataset_service
from app.platform import profiles as profile_service
from app.platform import validation as validation_service
from app.platform import validation_rules as rule_service
from app.platform.blobs import BlobStore, to_ref
from app.worker.handlers import register_handler
from app.worker.progress import JobProgress
from model_schema import ActorKind, JobKind, JobResult, Principal
from pricing_core.data.profile import profile_frame
from pricing_core.data.validate import run_validation
from pricing_core.progress import ProgressCallback

__all__ = ["register_data_handlers"]

_log = get_logger("app.worker.data")

#: One-ways are chosen from the semantic types the profiler infers (FR-DATA-26), not from
#: a list of column names. The list this replaced was four English defaults and matched
#: exactly one of freMTPL2's five rating factors — `area`, `veh_power`, `veh_brand`,
#: `veh_gas` and `region` — so twelve of thirteen columns had no one-way and `02`'s factor
#: workbench would have had almost nothing to read.
_ONE_WAY_SELECTION: Final = "auto"


def _bridge(progress: ProgressCallback) -> JobProgress:
    """Narrow the shared callback to the platform one these handlers need.

    `JobHandler` passes a `ProgressCallback` because that is `pricing-core`'s contract and
    the great majority of handlers need nothing more (ADR-0001). These do — they read
    blobs and write rows — and the worker always passes a `JobProgress`. Checking rather
    than assuming turns a future harness change from an `AttributeError` deep inside a job
    into one sentence naming the cause.
    """
    if not isinstance(progress, JobProgress):
        raise TypeError(
            f"a dataset handler needs the platform progress bridge, got "
            f"{type(progress).__name__}. It reads blobs and writes rows, which the bare "
            "pricing-core ProgressCallback does not provide."
        )
    return progress


def _actor(parameters: dict[str, Any]) -> Principal:
    """The Principal that submitted the Job.

    Carried in the parameters rather than read from the Job row, because the handler
    receives only the parameters — and an action attributed to "the system" when a person
    asked for it is an audit trail that answers the wrong question.
    """
    submitted = parameters["actor"]
    return Principal(
        kind=ActorKind(submitted["kind"]),
        id=UUID(submitted["id"]),
        display=submitted.get("display", ""),
    )


def _workspace(parameters: dict[str, Any]) -> UUID:
    return UUID(parameters["workspace_id"])


async def _read_tables(
    session: Any, blob_store: BlobStore, version: DatasetVersionRow
) -> dict[str, pl.DataFrame]:
    """Load a version's parquet tables by name."""
    tables: dict[str, pl.DataFrame] = {}
    for entry in version.tables:
        row = await session.get(BlobRow, entry["blob"]["sha256"])
        if row is None:
            raise PlatformError(
                "NOT_FOUND",
                "A table's blob is missing",
                404,
                f"Version {version.id} names blob {entry['blob']['sha256']}, which is not "
                "in the store. The version is unreadable and cannot be validated.",
            )
        tables[entry["name"]] = pl.read_parquet(io.BytesIO(await blob_store.read(to_ref(row))))
    return tables


def _ingest(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`dataset.ingest` — bytes to a Dataset Version, then a Profile (FR-DATA-2, -25).

    Profiling happens here rather than as a second Job because FR-DATA-25 says it runs
    *after successful ingestion*, and a separate Job could be cancelled, leaving a version
    with no profile and no record of why.
    """
    progress = _bridge(callback)
    blob_store = progress.blob_store
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    progress.update(0.05, "reading the upload")

    async def work() -> UUID:
        async with progress.database.session() as session:
            row = await session.get(BlobRow, parameters["blob"])
            if row is None:
                raise PlatformError(
                    "NOT_FOUND",
                    "The uploaded file is not in the blob store",
                    404,
                    f"No blob {parameters['blob']}. Upload it before starting an "
                    "ingestion run.",
                )
            payload = await blob_store.read(to_ref(row))

        async with progress.database.unit_of_work() as session:
            outcome = await ingest_upload(
                session,
                blob_store,
                workspace_id=workspace_id,
                actor=actor,
                dataset_id=UUID(parameters["dataset_id"]),
                data=payload,
                filename=parameters.get("filename", "upload.csv"),
                recipe=parameters.get("recipe") or [],
            )
            return UUID(str(outcome.version.id))

    version_id = progress.run_on_loop(work())
    progress.update(0.6, "profiling")
    _profile_version(progress, workspace_id=workspace_id, actor=actor, version_id=version_id)
    progress.update(1.0, "done")
    return JobResult(kind="artifact", ref=f"dataset_version:{version_id}")


def _profile_version(
    progress: JobProgress, *, workspace_id: UUID, actor: Principal, version_id: UUID
) -> UUID:
    blob_store = progress.blob_store

    async def work() -> UUID:
        async with progress.database.session() as session:
            version = await session.get(DatasetVersionRow, version_id)
            if version is None:
                raise PlatformError(
                    "NOT_FOUND", "Dataset version not found", 404, f"No version {version_id}."
                )
            tables = await _read_tables(session, blob_store, version)

        first = next(iter(tables.values())) if tables else pl.DataFrame()
        profile = profile_frame(
            first, dataset_version_id=version_id, one_way_columns=_ONE_WAY_SELECTION
        )
        async with progress.database.unit_of_work() as session:
            stored = await profile_service.store_profile(
                session, workspace_id=workspace_id, actor=actor, profile=profile
            )
            return UUID(str(stored.id))

    return progress.run_on_loop(work())


def _profile(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`dataset.profile` — re-profile an existing version (FR-DATA-25)."""
    progress = _bridge(callback)
    profile_id = _profile_version(
        progress,
        workspace_id=_workspace(parameters),
        actor=_actor(parameters),
        version_id=UUID(parameters["dataset_version_id"]),
    )
    return JobResult(kind="artifact", ref=f"profile:{profile_id}")


def _validate(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`dataset.validate` — run the rule set and persist the report (FR-DATA-15).

    Does **not** promote the version. Promotion is a decision an actuary makes after
    reading the report and acknowledging what it warns about (`01` §1.3, FR-DATA-17); a
    job that promoted on a pass would make the gate automatic, which is the one thing it
    must not be.
    """
    progress = _bridge(callback)
    blob_store = progress.blob_store
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    version_id = UUID(parameters["dataset_version_id"])
    dry_run_rule_id = parameters.get("dry_run_rule_id")
    progress.update(0.05, "loading the version")

    async def load() -> tuple[dict[str, pl.DataFrame], Any, Any]:
        async with progress.database.session() as session:
            version = await session.get(DatasetVersionRow, version_id)
            if version is None or version.workspace_id != workspace_id:
                raise PlatformError(
                    "NOT_FOUND", "Dataset version not found", 404, f"No version {version_id}."
                )
            tables = await _read_tables(session, blob_store, version)

            if dry_run_rule_id is not None:
                # A dry run validates against the single rule under review, not the
                # dataset's set: the approver is asking what *this rule* does.
                from model_schema import RuleSetEntry, ValidationRuleSet

                rule = await rule_service.load_rule(
                    session, workspace_id=workspace_id, rule_id=UUID(dry_run_rule_id)
                )
                rule_set = ValidationRuleSet(
                    id=rule.id,
                    slug=f"dry-run-{rule.slug}",
                    version=rule.version,
                    entries=(RuleSetEntry(rule=rule_service.to_schema(rule)),),
                )
            else:
                rule_set = await rule_service.rule_set_for(
                    session,
                    workspace_id=workspace_id,
                    dataset_id=version.dataset_id,
                    slug=str(version.dataset_id),
                )

            reference_profile = None
            reference_id = rule_set.reference_dataset_version_id
            if reference_id is not None:
                try:
                    reference_profile = await profile_service.latest_profile(
                        session, workspace_id=workspace_id, version_id=reference_id
                    )
                except PlatformError:
                    # FR-DATA-24 prefers the profile; a reference version without one is a
                    # reason to skip the distributional rules, not to fail the run.
                    reference_profile = None
            return tables, rule_set, reference_profile

    tables, rule_set, reference_profile = progress.run_on_loop(load())
    progress.update(0.3, "running rules")

    report = run_validation(
        tables,
        rule_set,
        dataset_version_id=version_id,
        reference_profile=reference_profile,
        progress=progress,
    )

    async def store() -> UUID:
        async with progress.database.unit_of_work() as session:
            if dry_run_rule_id is None:
                # The run opens the state it later closes. A dry run validates a *rule*
                # against a version and must not touch the version's status at all.
                await dataset_service.begin_validation(
                    session,
                    workspace_id=workspace_id,
                    actor=actor,
                    version_id=UUID(str(report.dataset_version_id)),
                )
            row = await validation_service.store_report(
                session, workspace_id=workspace_id, actor=actor, report=report
            )
            if dry_run_rule_id is not None:
                await rule_service.attach_dry_run(
                    session,
                    workspace_id=workspace_id,
                    rule_id=UUID(dry_run_rule_id),
                    report_id=row.id,
                )
            # FR-DATA-43. The job still does **not** promote — that is an actuary's act
            # after reading the report (`01` §1.3) — but a version whose report failed will
            # never be promoted, and leaving it in `validating` reads as "still running" on
            # every screen. A dry run concludes nothing: it validates a rule, not a version.
            elif not report.permits_validation:
                await dataset_service.conclude_failed_validation(
                    session,
                    workspace_id=workspace_id,
                    actor=actor,
                    version_id=UUID(str(report.dataset_version_id)),
                )
            return UUID(str(row.id))

    report_id = progress.run_on_loop(store())
    progress.update(1.0, "done")
    _log.info(
        "validation complete",
        extra={"report_id": str(report_id), "overall": validation_service.overall_outcome(
            report
        ).value},
    )
    return JobResult(kind="artifact", ref=f"validation_report:{report_id}")


def _derive(parameters: dict[str, Any], callback: ProgressCallback) -> JobResult:
    """`dataset.derive` — a declared operation over a parent version (FR-DATA-33).

    **`split` is materialised; every other operation is refused.** A derived version used
    to inherit its parent's `tables` wholesale, which made a "1 % sample" a version
    containing 100 % of the rows and a train/test split two versions each containing
    everything. FR-DATA-34 says a derived version inherits schema, dictionary and rule set
    — the code was inheriting the *data*, and the two had been conflated.

    Fixed here for `split`, because the diagnostics slice needs an honest holdout and a
    holdout containing every training row is worse than none: it produces excellent numbers
    that mean nothing. The rest now fail the Job with `DERIVATION_NOT_MATERIALISED` in
    `derive_version` (FR-DATA-45, OQ-DATA-8 decided 2026-08-17) rather than succeeding with
    the parent's rows — the same failure, made loud.
    """
    progress = _bridge(callback)
    blob_store = progress.blob_store
    actor, workspace_id = _actor(parameters), _workspace(parameters)
    operation = parameters["operation"]
    params = parameters.get("params") or {}

    async def work() -> UUID:
        async with progress.database.unit_of_work() as session:
            row = await dataset_service.derive_version(
                session,
                workspace_id=workspace_id,
                actor=actor,
                parent_version_id=UUID(parameters["parent_version_id"]),
                operation=operation,
                params=params,
            )
            if operation == "split":
                row.tables = await _materialise_split(
                    session, blob_store, tables=list(row.tables), params=params
                )
            return UUID(str(row.id))

    version_id = progress.run_on_loop(work())
    return JobResult(kind="artifact", ref=f"dataset_version:{version_id}")


async def _materialise_split(
    session: Any,
    blob_store: BlobStore,
    *,
    tables: list[dict[str, Any]],
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    """Write the requested part's rows as their own blob (FR-DATA-33, FR-DATA-36).

    The partition is `pricing_core.data.splits`', which computes it as a pure function of
    method, seed and fractions — so the `train` Job and the `test` Job, running minutes
    apart in different processes, agree on every row without coordinating.
    """
    from pricing_core.data.splits import SplitError, partition

    part = params.get("part")
    if not part:
        raise PlatformError(
            "VALIDATION_FAILED",
            "A split must say which part this version is",
            422,
            "`params.part` names the part being derived (e.g. 'train'). Without it there "
            "is nothing to select and the version would silently be the whole parent.",
        )

    written: list[dict[str, Any]] = []
    for entry in tables:
        blob_row = await session.get(BlobRow, entry["blob"]["sha256"])
        if blob_row is None:
            raise PlatformError(
                "NOT_FOUND", "A table's blob is missing", 404,
                f"The parent names blob {entry['blob']['sha256']}, which is not in the store.",
            )
        frame = pl.read_parquet(io.BytesIO(await blob_store.read(to_ref(blob_row))))
        try:
            parts = partition(
                frame,
                method=params.get("method", "random"),
                seed=int(params.get("seed", 0)),
                fractions=params.get("fractions"),
                key_column=params.get("key_column"),
                time_column=params.get("time_column"),
                cutoff=params.get("cutoff"),
            )
        except SplitError as exc:
            raise PlatformError(
                "VALIDATION_FAILED", "The split cannot be computed as described", 422, str(exc)
            ) from exc

        if part not in parts:
            raise PlatformError(
                "VALIDATION_FAILED",
                "The split has no such part",
                422,
                f"Part {part!r} is not one of {sorted(parts)}. A version derived for a part "
                "the split does not define would carry no rows and claim to be a holdout.",
            )

        selected = parts[part]
        buffer = io.BytesIO()
        selected.write_parquet(buffer, compression="zstd")
        ref = await blob_store.put(session, buffer.getvalue(), PARQUET_MEDIA_TYPE)
        written.append(
            {
                **entry,
                "row_count": selected.height,
                "blob": ref.model_dump(mode="json", by_alias=True),
            }
        )
    return written


def register_data_handlers() -> None:
    """Register the `dataset.*` handlers.

    A function rather than import-time side effects: `register_handler` refuses a duplicate
    (rightly), and a module that registers on import cannot be imported twice — which a
    test session does routinely.
    """
    for kind, handler in (
        (JobKind.DATASET_INGEST, _ingest),
        (JobKind.DATASET_VALIDATE, _validate),
        (JobKind.DATASET_PROFILE, _profile),
        (JobKind.DATASET_DERIVE, _derive),
    ):
        if kind not in __import__("app.worker.handlers", fromlist=["HANDLERS"]).HANDLERS:
            register_handler(kind, handler)
