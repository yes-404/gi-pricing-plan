"""The Phase 1b rating version (OD1, W7-3) — draft, submit, approve, read.

`FR-440`: the demo seed creates and approves a minimal rating version that pins an
approved Model. The full `03` surface stays Phase 2. The lifecycle mirrors the model's:
`create_rating_version` (draft), `submit_for_review` (`draft → review`, creating the
approval request through the same governance `approvals.submit` the model uses), and the
approver's decision reaches the row through `apply_approval_decision`, the seam
`api/approvals.py::_carry_to_the_artifact` drives for every artifact type.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from decimal import Decimal
from typing import Any, Literal, cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalRequestRow,
    AuditEventRow,
    FactorRow,
    ModelRow,
    RatingAlgorithmRow,
    RatingVersionRow,
    RegressionSuiteRow,
    RegressionSuiteVersionRow,
)
from app.errors import PlatformError
from app.platform import approvals, audit, blobs, rbac
from app.platform import environments as environments_service
from app.platform import objectives as objectives_service
from app.platform import perils as perils_service
from app.platform import rate_tables as rate_tables_service
from app.platform import reference as reference_service
from app.platform import regression_runs as regression_runs_service
from app.platform import regression_suites as regression_suites_service
from app.platform import transparency as transparency_service
from app.platform.blobs import BlobStore
from app.platform.modelling import load_factors, to_factor, to_model
from model_schema import (
    ApprovalPolicy,
    ApprovalStatus,
    ArtifactRef,
    BundleMetadata,
    GbmFitResult,
    GoldenQuote,
    GoldenQuoteChange,
    GoldenQuoteChangeStep,
    GoldenQuoteCheck,
    GoldenQuoteDelta,
    GoldenQuoteNotChecked,
    JobSource,
    ModelReferenceMode,
    Permission,
    Pins,
    Principal,
    RatingAlgorithm,
    RatingModelCallStep,
    RatingVersion,
    RatingVersionEvidence,
    RatingVersionStatus,
    RegressionSuiteContent,
    check_model_reference_mode,
    context_hash,
    diff_algorithms,
)
from model_schema.approvals import (
    DEFAULT_APPROXIMATION_DEVIATION,
    DEFAULT_DISLOCATION_BASELINE_ENVIRONMENT,
)
from model_schema.dislocation import DislocationRun
from model_schema.rating import ApproximationCheck
from pricing_core.rating.compile import Bundle, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle
from pricing_core.rating.testing import evaluate_golden_quotes

#: `reference.rows_as_at`'s default `limit` (200) is a UI page size. A compiled Bundle
#: must be self-contained (FR-239) and embed a pinned reference table's rows in full —
#: a lookup key past the first page would silently miss inside a `CompiledBundle` that can
#: perform no I/O (Task 1.3/RL-873) — so this resolver asks for effectively all of them.
_ALL_REFERENCE_ROWS = 10_000_000

#: Loads a compiled bundle for a Rating Version ref. The route supplies one that refuses
#: rather than degrades when metadata storage is down (audit finding F5), which is why the
#: loading stays in the API layer and this module only calls it.
BundleLoader = Callable[[ArtifactRef], Awaitable[CompiledBundle]]

#: The statuses a version has once it has been approved; a baseline is one of these.
_APPROVED_OR_AFTER = (
    RatingVersionStatus.APPROVED.value,
    RatingVersionStatus.LIVE.value,
    RatingVersionStatus.RETIRED.value,
)

__all__ = [
    "BundleLoader",
    "WorkspaceResolver",
    "apply_approval_decision",
    "approximation_fidelity_statements",
    "compile_rating_version",
    "create_rating_version",
    "dislocation_run_verified",
    "golden_quote_delta_authors",
    "load_rating_version",
    "structural_diff_verified",
    "submit_for_review",
    "to_schema",
]


def to_schema(row: RatingVersionRow) -> RatingVersion:
    """The row as the `03` §4.3 RatingVersion — the Phase 1b subset plus the W9-3 fields.

    The §4.3 fields are nullable so Phase 1b rows (the demo seed) keep parsing; a W9-3
    version carries `algorithm_ref` and `pins` for compilation.
    """
    return RatingVersion(
        id=row.id,
        workspace_id=row.workspace_id,
        slug=row.slug,
        version=row.version,
        status=RatingVersionStatus(row.status),
        dataset_version_id=row.dataset_version_id,
        model_ref=ArtifactRef.model_validate(row.model_ref),
        created_at=row.created_at,
        created_by=row.created_by,
        updated_at=row.updated_at,
        algorithm_ref=(
            ArtifactRef.model_validate(row.algorithm_ref) if row.algorithm_ref else None
        ),
        pins=Pins.model_validate(row.pins) if row.pins else None,
        model_reference_mode=cast(
            Literal["exact", "approximation"], row.model_reference_mode or "exact"
        ),
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        bundle=BundleMetadata.model_validate(row.bundle) if row.bundle else None,
        change_summary=row.change_summary,
        evidence=RatingVersionEvidence.model_validate(row.evidence) if row.evidence else None,
        approval_request_id=row.approval_request_id,
    )


async def load_rating_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rating_version_id: UUID,
    for_update: bool = False,
) -> RatingVersionRow:
    """The row, scoped to the workspace so a cross-workspace id reads as 404.

    `for_update` takes the row lock (`with_for_update()`, as `apply_approval_decision` does),
    so `compile_rating_version` and `submit_for_review` of one version serialise (RL-1379).
    `populate_existing` makes a row already in the session's identity map reread under the lock.
    """
    row = await session.get(
        RatingVersionRow,
        rating_version_id,
        with_for_update=for_update,
        populate_existing=for_update,
    )
    if row is None or row.workspace_id != workspace_id:
        raise PlatformError(
            "NOT_FOUND", "Rating version not found", 404, f"No rating version {rating_version_id}."
        )
    return row


def require_compilable(row: RatingVersionRow) -> None:
    """Refuse a compile unless the version is `draft` (`03` FR-239, `00` FR-4; RL-1379).

    A version that has left `draft` gets a new compiled output only as a new version. Called
    by the compile route (a synchronous 409, no Job) and by `compile_rating_version` (the
    Job ends `failed` when the status changed after submission): one guard, two callers.
    """
    if RatingVersionStatus(row.status) is not RatingVersionStatus.DRAFT:
        raise PlatformError(
            "RATING_VERSION_IMMUTABLE",
            "Rating version is immutable",
            409,
            f"Rating version {row.slug}@{row.version} is {row.status}; only a draft rating "
            "version can be compiled (03 FR-239, 00 FR-4). Create a new version to compile again.",
        )


async def resolve_rating_version_ref(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    ref: ArtifactRef,
) -> RatingVersionRow:
    """The row a `rating_version:slug@version` reference names, scoped to the workspace.

    Scoring receives a reference rather than an id (RL-880), and until now the only
    ref-to-row resolution in this module was inline in `apply_approval_decision` — a write
    path, so it also took `FOR UPDATE`. This one deliberately does not: a read on the
    scoring path must not take row locks that contend with approvals.
    """
    row = (
        await session.execute(
            select(RatingVersionRow).where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == ref.slug,
                RatingVersionRow.version == ref.version,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        raise PlatformError(
            "NOT_FOUND", "Rating version not found", 404, f"No rating version {ref}."
        )
    return row


async def record_bundle_blob(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rating_version_id: UUID,
    blob_sha256: str,
) -> None:
    """Record the blob key the compiled bundle was stored under (RL-915).

    Kept here rather than in the Job handler because `row.bundle`'s shape is this module's
    to own — a handler assembling that dict itself would be the second place the shape is
    written down, which is what `CLAUDE.md` §2 forbids.

    Called *after* the `put`, inside the handler's existing `unit_of_work`: the key does not
    exist when `compile_rating_version` writes the row, so the row is completed rather than
    written twice. The alternative the ruling allows — moving the `put` inside
    `compile_rating_version` — would change that function's contract for every caller,
    including tests that compile without wanting a blob written.
    """
    row = await load_rating_version(
        session, workspace_id=workspace_id, rating_version_id=rating_version_id
    )
    if row.bundle is None:  # pragma: no cover - compile_rating_version always writes it
        raise PlatformError(
            "BUNDLE_COMPILE_FAILED",
            "Bundle metadata missing",
            500,
            "The compiled bundle's metadata was not written before its blob key.",
        )
    row.bundle = {**row.bundle, "blob_sha256": blob_sha256}


async def create_rating_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    slug: str,
    dataset_version_id: UUID,
    model_ref: ArtifactRef,
    algorithm_ref: ArtifactRef | None = None,
    pins: Pins | None = None,
    model_reference_mode: ModelReferenceMode = "exact",
) -> RatingVersionRow:
    """Create a draft rating version declaring its algorithm and pins (`FR-237`).

    The declaration is stored, not resolved: whether each ref exists, and at what
    maturity, is compile's (`FR-240`). An algorithm that does resolve is mode-checked
    here, because the version and the algorithm first meet at this write (`FR-223`).
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.RATING_WRITE,
    )
    algorithm_row = None
    if algorithm_ref is not None:
        algorithm_row = await session.scalar(
            select(RatingAlgorithmRow).where(
                RatingAlgorithmRow.workspace_id == workspace_id,
                RatingAlgorithmRow.slug == algorithm_ref.slug,
                RatingAlgorithmRow.version == algorithm_ref.version,
            )
        )
    next_version = 1 + (
        await session.execute(
            select(func.coalesce(func.max(RatingVersionRow.version), 0)).where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == slug,
            )
        )
    ).scalar_one()
    row = RatingVersionRow(
        workspace_id=workspace_id,
        slug=slug,
        version=next_version,
        status=RatingVersionStatus.DRAFT.value,
        dataset_version_id=dataset_version_id,
        model_ref=str(model_ref),
        algorithm_ref=str(algorithm_ref) if algorithm_ref is not None else None,
        pins=pins.model_dump(mode="json") if pins is not None else None,
        model_reference_mode=model_reference_mode,
        created_by=actor.id,
    )
    session.add(row)
    await session.flush()
    if algorithm_row is not None:
        try:
            check_model_reference_mode(
                to_schema(row), RatingAlgorithm.model_validate(algorithm_row.content)
            )
        except ValueError as exc:
            raise PlatformError(
                "MODEL_REFERENCE_MODE_INCONSISTENT",
                "Model reference mode inconsistent",
                422,
                str(exc),
            ) from exc
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action="rating_version.created",
        entity_ref=f"rating_version:{slug}@{next_version}",
        before={},
        after={
            "status": RatingVersionStatus.DRAFT.value,
            "model_ref": str(model_ref),
            "algorithm_ref": str(algorithm_ref) if algorithm_ref is not None else None,
            "pins": pins.model_dump(mode="json") if pins is not None else None,
            "model_reference_mode": model_reference_mode,
        },
    )
    return row


async def submit_for_review(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    rating_version_id: UUID,
    change_summary: str,
    blob_store: BlobStore,
    load_compiled: BundleLoader | None = None,
) -> tuple[RatingVersionRow, ApprovalRequestRow]:
    """`draft → review`, creating the approval request through governance.

    Before the request is created, the golden-quote gate runs (`03` FR-260 as amended
    2026-09-28): every golden quote of the algorithm's Regression Suite is re-scored
    against this version's compiled bundle, any mismatch refuses the submission, and the
    suite version checked — with its delta since the previous approved version of the
    same algorithm — is pinned into `evidence.golden_quotes`. `load_compiled` loads the
    bundle for a ref; the route supplies one that refuses rather than degrades when
    metadata storage is down (audit finding F5). It is needed only when a suite exists.

    `blob_store` is required, with no default: FR-219's structural diff is stored as a blob
    (`06` FR-364 E4), and a caller that forgets the store fails at once rather than submitting
    a version whose diff was never kept.
    """
    await rbac.require_permission(
        session,
        workspace_id=workspace_id,
        principal=actor,
        permission=Permission.RATING_SUBMIT,
    )
    row = await load_rating_version(
        session, workspace_id=workspace_id, rating_version_id=rating_version_id, for_update=True
    )
    if RatingVersionStatus(row.status) is not RatingVersionStatus.DRAFT:
        raise PlatformError(
            "VALIDATION_FAILED",
            "A rating version must be draft to submit",
            409,
            f"Rating version {row.slug}@{row.version} is {row.status}, not draft.",
        )
    ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)
    golden_quotes = await _golden_quote_gate(
        session, workspace_id=workspace_id, row=row, ref=ref, load_compiled=load_compiled
    )
    run_id = await _regression_run_gate(
        session, workspace_id=workspace_id, row=row, ref=ref, golden_quotes=golden_quotes
    )
    policy = await approvals.policy_for(session, workspace_id)
    baseline, baseline_reason = await _dislocation_baseline(
        session, workspace_id=workspace_id, row=row, policy=policy
    )
    dislocation_run_id = await _dislocation_gate(
        session, workspace_id=workspace_id, row=row, ref=ref, baseline=baseline
    )
    approximation_check = await _approximation_gate(
        session, workspace_id=workspace_id, row=row, ref=ref, policy=policy
    )
    structural_diff_blob = await _structural_diff_gate(
        session, workspace_id=workspace_id, row=row, ref=ref, baseline=baseline,
        blob_store=blob_store,
    )
    # Written once, here, and never edited after (`03` §4.3's invariant). The ids are the
    # only other keys these gates write; `golden_quotes` is exactly what the gate returned.
    row.evidence = {
        **(row.evidence or {}),
        "golden_quotes": golden_quotes,
        "regression_suite_run_id": str(run_id),
        "structural_diff_blob": structural_diff_blob,
        **(
            {"approximation_check": approximation_check.model_dump(mode="json")}
            if approximation_check is not None
            else {}
        ),
        **(
            {"dislocation_run_id": str(dislocation_run_id)}
            if dislocation_run_id is not None
            else {"no_baseline": baseline_reason}
        ),
    }
    # The version carries the summary it was submitted with (`03` FR-242; PL-1500 Task 7,
    # DP-E1-6 (a)); a resubmission overwrites it, as the evidence above is. A blank summary is
    # still `approvals.submit`'s refusal (FR-352), which rolls this assignment back.
    row.change_summary = change_summary
    request = await approvals.submit(
        session,
        workspace_id=workspace_id,
        submitter=actor,
        artifact_ref=ref,
        change_summary=change_summary,
    )
    row.status = RatingVersionStatus.REVIEW.value
    row.approval_request_id = request.id
    await session.flush()
    return row, request


async def apply_approval_decision(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    actor: Principal,
    request: ApprovalRequestRow,
) -> RatingVersionRow | None:
    """Carry a governance decision into the artifact (W7-3, FR-440).

    Returns `None` when the request is about something other than a Rating Version, so the
    caller can drive every artifact type through one call per module. Called in the same
    transaction as the decision, exactly as the model's sibling.
    """
    if request.artifact_type != "rating_version":
        return None

    ref = ArtifactRef.model_validate(request.artifact_ref)
    row = (
        await session.execute(
            select(RatingVersionRow)
            .where(
                RatingVersionRow.workspace_id == workspace_id,
                RatingVersionRow.slug == ref.slug,
                RatingVersionRow.version == ref.version,
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if row is None:
        return None

    # What the decided request means for the version, as the model's, objective's and
    # metric's hooks read it. Until 2026-09-28 this hook set `approved` after **every**
    # decision — a rejection, a request for changes, and the first of the policy's two
    # approvals alike — and from any status (the approval status bypass).
    target = _target_status(ApprovalStatus(request.status))
    if target is None:
        return row  # still in review: one approval of two moves nothing
    if target is RatingVersionStatus.DRAFT and row.status == RatingVersionStatus.DRAFT.value:
        # A request opened on a version that never left `draft` (possible before this fix)
        # must stay closable: returning the version to where it already is moves nothing,
        # as the model's hook does when the row is already at its target. Refusing here
        # would leave the request open for ever and block the version's resubmission.
        return row
    # `06` FR-351: only a version in review moves, checked on the row this transaction
    # holds locked, so the route's refusal is not the only guard.
    approvals.require_in_review(ref, row.status)
    before = row.status
    row.status = target.value
    row.updated_at = func.now()
    await session.flush()
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=actor,
        source=JobSource.API,
        action=f"rating_version.{_ACTION[target]}",
        entity_ref=f"rating_version:{ref.slug}@{ref.version}",
        # The row's own prior state, never a literal: this line once recorded `review`
        # whatever the version had been.
        before={"status": before},
        after={"status": target.value},
    )
    return row


def _target_status(request_status: ApprovalStatus) -> RatingVersionStatus | None:
    """`approved` on an approved request; `draft` when the request comes back, as `06`
    FR-355 says for every artifact without a reason to differ; nothing while it is open."""
    return {
        ApprovalStatus.APPROVED: RatingVersionStatus.APPROVED,
        ApprovalStatus.CHANGES_REQUESTED: RatingVersionStatus.DRAFT,
        ApprovalStatus.REJECTED: RatingVersionStatus.DRAFT,
        ApprovalStatus.WITHDRAWN: RatingVersionStatus.DRAFT,
    }.get(request_status)


_ACTION = {
    RatingVersionStatus.APPROVED: "approved",
    RatingVersionStatus.DRAFT: "returned_to_draft",
}


class WorkspaceResolver:
    """The workspace's own `ArtifactResolver` (DP-S4-4): resolves an algorithm or a pin
    through the workspace's tables, embedding each artifact's real content (RL-873).

    Lifted unchanged from `compile_rating_version`, where it was nested, so that a worker
    resolves a pin exactly as a real compile does (`dislocation.run`, FR-1398).
    """

    def __init__(
        self, session: AsyncSession, workspace_id: UUID, blob_store: BlobStore
    ) -> None:
        self._session = session
        self._workspace_id = workspace_id
        self._blob_store = blob_store

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        session, workspace_id, blob_store = self._session, self._workspace_id, self._blob_store
        if ref.type == "rating_algorithm":
            algo = await session.scalar(
                select(RatingAlgorithmRow).where(
                    RatingAlgorithmRow.workspace_id == workspace_id,
                    RatingAlgorithmRow.slug == ref.slug,
                    RatingAlgorithmRow.version == ref.version,
                )
            )
            if algo is None:
                raise PlatformError("NOT_FOUND", "Rating algorithm not found", 404)
            # RL-859
            # (docs/rulings/RL-00859-the-remainder-splits-and-the-split-is-the-answer.md):
            # `RatingAlgorithmRow` has no `status` column, so `"approved"` was an invented
            # maturity rather than a read one. `"no_maturity_concept"` is the sentinel
            # `pricing_core.rating.compile._MATURITY_CHECK_EXEMPT` reads for a pin kind with
            # nothing to report.
            return ResolvedArtifact(status="no_maturity_concept", payload=algo.content)
        if ref.type == "model":
            model = await session.scalar(
                select(ModelRow).where(
                    ModelRow.workspace_id == workspace_id,
                    ModelRow.model_family_slug == ref.slug,
                    ModelRow.version == ref.version,
                )
            )
            if model is None:
                raise PlatformError("NOT_FOUND", "Model not found", 404)
            model_obj = to_model(model)
            payload = model_obj.model_dump(mode="json")
            if isinstance(model_obj.fit_result, GbmFitResult):
                # `gbm.py`'s `_fit_xgboost`/`fit_gbm` persist the booster as JSON
                # text wrapped in bytes (`bytes(booster.save_raw(raw_format="json"))`)
                # behind a content-addressed blob reference — the only place the
                # actual booster content exists. Compile time is when DB/blob access
                # is allowed (RL-874); dereference it now so the Bundle carries the
                # booster itself, never the reference (RL-873).
                booster_bytes = await blob_store.read(model_obj.fit_result.booster_blob)
                payload["fit_result"]["booster_content"] = booster_bytes.decode("utf-8")
            factors = await load_factors(
                session, workspace_id=workspace_id, factor_ids=list(model_obj.spec.factors)
            )
            return ResolvedArtifact(
                status=model.status, payload=payload, factors=tuple(factors)
            )
        if ref.type == "rate_table":
            # `rate_tables.py`'s own materialiser: a version's cells are either row-
            # or parquet-stored, and `_to_version` always returns them inline as
            # `rows` — reused rather than re-implemented (03 §3.3, FR-232).
            table_row = await rate_tables_service._load_table(
                session, workspace_id, ref.slug
            )
            version_row = await rate_tables_service._load_version(
                session, table_row.id, ref.version, ref.slug
            )
            materialised = await rate_tables_service._to_version(
                session, version_row, blob_store
            )
            # `RateTableVersionRow` carries no status column at all (rate tables are
            # immutable-on-write — seed, operation or import, never a draft phase),
            # so there is no real maturity value to read here. RL-856
            # (`docs/rulings/RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the-
            # exemption-is-declared-and-self-invalidating.md`)
            # refused inventing "approved" for it: that would put a constant where
            # `compile_bundle`'s gate reads a discriminator, and fail open the day
            # `RateTableVersionRow` gains a real status. `_MATURITY_CHECK_EXEMPT` is
            # what actually admits this pin past the FR-20 floor; the sentinel
            # below is deliberately not a member of `_APPROVED_OR_BETTER`, so a pin
            # still fails closed if the exemption is ever removed without this
            # branch being updated to match.
            return ResolvedArtifact(
                status="no_maturity_concept",
                payload=materialised.model_dump(mode="json"),
            )
        if ref.type == "reference_table":
            version = await reference_service.version_view(
                session, workspace_id=workspace_id, slug=ref.slug, version=ref.version
            )
            rows = await reference_service.rows_as_at(
                session,
                workspace_id=workspace_id,
                slug=ref.slug,
                version=ref.version,
                as_at=None,
                limit=_ALL_REFERENCE_ROWS,
            )
            # FR-70's own lifecycle is `draft`/`published`, not compile.py's
            # generic `approved`/`live`/`retired` vocabulary. "published" is that
            # lifecycle's FR-20 maturity gate (FR-70: "independently
            # approvable"); bridged here, deliberately and narrowly, rather than by
            # widening `compile_bundle`'s own `_APPROVED_OR_BETTER` (out of Task
            # 1.2's scope — see PR description). A real `draft` version still reports
            # its own, non-mature status, so an unpublished pin is still refused.
            status = "approved" if version.status == "published" else version.status
            return ResolvedArtifact(
                status=status,
                payload={
                    "definition": version.model_dump(mode="json"),
                    "rows": [row_.model_dump(mode="json") for row_ in rows],
                },
            )
        if ref.type == "custom_objective":
            objective = await objectives_service.resolve_ref(
                session, workspace_id=workspace_id, ref=str(ref)
            )
            return ResolvedArtifact(
                status=objective.status.value,
                payload=objective.model_dump(mode="json"),
            )
        if ref.type == "factor":
            factor = await session.scalar(
                select(FactorRow).where(
                    FactorRow.workspace_id == workspace_id,
                    FactorRow.slug == ref.slug,
                    FactorRow.version == ref.version,
                )
            )
            if factor is None:
                raise PlatformError("NOT_FOUND", "Factor not found", 404)
            # A Factor has no approval lifecycle (RL-856's sentinel); it is read to check
            # its intent (FR-88) and is never a pin, so no maturity floor reads it.
            return ResolvedArtifact(
                status="no_maturity_concept",
                payload=to_factor(factor).model_dump(mode="json"),
            )
        if ref.type == "peril_structure":
            structure_row = await perils_service.load_structure_by_ref(
                session, workspace_id=workspace_id, slug=ref.slug, version=ref.version
            )
            if structure_row is None:
                raise PlatformError("NOT_FOUND", "Peril Structure not found", 404, f"{ref}")
            # Its status is read as the row holds it, so `compile_bundle`'s maturity loop
            # (FR-20) refuses a structure that is not `approved` (FD-1456).
            return ResolvedArtifact(
                status=structure_row.status,
                payload=perils_service.to_structure(structure_row).model_dump(mode="json"),
            )
        raise PlatformError(
            "NOT_FOUND",
            "Pinned artifact cannot be resolved yet",
            404,
            f"{ref}: the compile resolver has no branch for artifact type {ref.type!r}; "
            "a compile cannot embed it.",
        )


async def compile_rating_version(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    rating_version_id: UUID,
    blob_store: BlobStore,
) -> Bundle:
    """Compile a pinned Rating Version to a self-contained Bundle (W9-3, WK-671 Task 1.2).

    Resolves the algorithm and every pin — rate tables, reference tables, custom
    objectives and models — through the workspace's own tables, embedding each pinned
    artifact's real content in `resolved_payloads` (RL-873: inline, never a blob
    reference, so `Bundle` stays self-contained and `load_bundle` needs no I/O). Returns
    the full `Bundle`; the caller (the `rating.compile` Job handler) persists it as a
    blob. `row.bundle` keeps carrying just the summary metadata it always has.
    """
    row = await load_rating_version(
        session, workspace_id=workspace_id, rating_version_id=rating_version_id, for_update=True
    )
    require_compilable(row)
    schema = to_schema(row)

    try:
        bundle = await compile_bundle(
            schema, WorkspaceResolver(session, workspace_id, blob_store)
        )
    except ValueError as exc:
        text = str(exc)
        code, _, detail = text.partition(": ")
        if not (code.isupper() and "_" in code):
            code, detail = "BUNDLE_COMPILE_FAILED", text
        raise PlatformError(
            code, code.replace("_", " ").title(), 422, detail
        ) from exc
    row.bundle = {
        "content_hash": bundle.content_hash,
        "bytes": len(bundle.model_dump_json().encode()),
        "compiled_at": bundle.compiled_at.isoformat(),
    }
    return bundle


# ---------------------------------------------------------------------------
# The golden-quote gate (`03` FR-260 as amended 2026-09-28; PL-1189 Task 5).
# ---------------------------------------------------------------------------


async def _golden_quote_gate(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    row: RatingVersionRow,
    ref: ArtifactRef,
    load_compiled: BundleLoader | None,
) -> dict[str, Any]:
    """Re-score the algorithm's golden quotes, refuse any mismatch, and return the
    evidence to pin: `GoldenQuoteCheck`, or the explicit `GoldenQuoteNotChecked`
    (DP-S2-4's interim rule — never an empty pass that reads as "0 mismatches")."""
    if row.algorithm_ref is None:
        return _not_checked("no_algorithm_ref")
    algorithm_slug = ArtifactRef.model_validate(row.algorithm_ref).slug
    found = await regression_suites_service.current_suite_for_algorithm(
        session, workspace_id=workspace_id, algorithm_slug=algorithm_slug
    )
    if found is None:
        return _not_checked("no_suite_for_algorithm")
    suite, current = found

    if row.bundle is None:
        raise PlatformError(
            "BUNDLE_COMPILE_FAILED",
            "Compile before submitting",
            409,
            f"{ref} has no compiled bundle, and algorithm {algorithm_slug!r} has a "
            "Regression Suite whose golden quotes must be re-scored against it (FR-260).",
        )
    if load_compiled is None:
        raise TypeError("submit_for_review with a Regression Suite requires load_compiled")
    bundle = await load_compiled(ref)
    if bundle.content_hash != row.bundle.get("content_hash"):
        raise PlatformError(
            "BUNDLE_COMPILE_FAILED",
            "The loaded bundle is not this version's bundle",
            409,
            f"{ref} records bundle {row.bundle.get('content_hash')!r}; the bundle loaded "
            f"is {bundle.content_hash!r}. Nothing was checked or written.",
        )

    content = RegressionSuiteContent.model_validate(current.content)
    results = evaluate_golden_quotes(bundle, content.golden_quotes, rating_version_ref=ref)
    failed = [result.name for result in results if result.status == "fail"]
    if failed:
        raise PlatformError(
            "GOLDEN_QUOTE_MISMATCH",
            "Golden quote mismatch",
            409,
            f"{ref} does not reproduce golden quote(s) {failed} of "
            f"{regression_suites_service.entity_ref(suite.slug, current.version)} within "
            "their declared tolerance (FR-260).",
        )

    delta = await _golden_quote_delta(
        session, workspace_id=workspace_id, algorithm_slug=algorithm_slug,
        suite=suite, current=current, exclude_id=row.id,
    )
    return GoldenQuoteCheck(
        status="checked",
        suite_ref=ArtifactRef(type="regression_suite", slug=suite.slug, version=current.version),
        suite_content_hash=current.content_hash,
        bundle_hash=bundle.content_hash,
        results=results,
        delta=delta,
    ).model_dump(mode="json")


async def _regression_run_gate(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    row: RatingVersionRow,
    ref: ArtifactRef,
    golden_quotes: dict[str, Any],
) -> UUID:
    """FR-257 limb (1), a passing Regression Suite (`PL-1205` Task 6): the run id to record.

    DP-S3-1: a passing suite has at least one golden quote, so no suite, or a suite with
    none, is refused. DP-S3-2 and audit A1: the **latest** run of this Rating Version for
    exactly this bundle and the suite version the golden-quote gate just pinned must itself
    be a pass — an earlier pass does not count once a later run on the same pair failed.
    """
    if golden_quotes.get("status") != "checked" or not golden_quotes.get("results"):
        raise _evidence_incomplete(
            ref, "a Regression Suite with at least one golden quote is required (FR-257)"
        )
    bundle_hash = (row.bundle or {}).get("content_hash")
    suite_hash = golden_quotes["suite_content_hash"]
    latest = await regression_runs_service.latest_run(
        session, workspace_id=workspace_id, rating_version_id=row.id,
        bundle_hash=str(bundle_hash), suite_content_hash=str(suite_hash),
    )
    if latest is None:
        raise _evidence_incomplete(
            ref,
            "no Regression Run exists for this version's current bundle and the suite "
            "version pinned at submission (FR-257)",
        )
    if latest.overall != "pass":
        raise _evidence_incomplete(
            ref,
            f"the latest Regression Run ({latest.id}) for this bundle and suite failed (FR-257)",
        )
    return latest.id


async def _dislocation_baseline(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    row: RatingVersionRow,
    policy: ApprovalPolicy,
) -> tuple[ArtifactRef | None, str]:
    """FR-257 limb (2)'s baseline and why (DP-S5-1 (a); `03` FR-257, 2026-10-10 clarification).

    The Rating Version live in the Environment the `rating_version` policy entry names (default
    `prod`); with nothing live there, the most recently approved other version of the same
    algorithm (`_baseline`, the golden-quote precedent); with neither, the version is the
    algorithm's first. The reason is `live:<environment>`, `approved` or `first_version`.
    """
    entry = policy.entry_for("rating_version")
    environment = (
        entry.dislocation_baseline_environment if entry is not None else None
    ) or DEFAULT_DISLOCATION_BASELINE_ENVIRONMENT
    live = await environments_service.live_rating_version_ref(
        session, workspace_id=workspace_id, environment_slug=environment
    )
    if live is not None:
        return ArtifactRef.parse(live), f"live:{environment}"
    if row.algorithm_ref is not None:
        found = await _baseline(
            session,
            workspace_id=workspace_id,
            algorithm_slug=ArtifactRef.model_validate(row.algorithm_ref).slug,
            exclude_id=row.id,
        )
        if found is not None:
            approved = found[0]
            return (
                ArtifactRef(type="rating_version", slug=approved.slug, version=approved.version),
                "approved",
            )
    return None, "first_version"


async def _dislocation_gate(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    row: RatingVersionRow,
    ref: ArtifactRef,
    baseline: ArtifactRef | None,
) -> UUID | None:
    """FR-257 limb (2), a Dislocation Run against the baseline: the run id to record.

    `None` only for a first version (no baseline, so no run is required; the caller records
    `no_baseline`). Otherwise the latest run naming this version at its **current** bundle hash
    as candidate and the baseline as baseline, else `EVIDENCE_INCOMPLETE` naming which of the
    three failed: no run at all, a run on an earlier bundle hash (stale), or a run against a
    different baseline.
    """
    if baseline is None:
        return None
    # Local, because `dislocation_runs` imports `WorkspaceResolver` and `to_schema` from this
    # module: a module-level import here is a cycle (PL-1500 Task 3).
    from app.platform import dislocation_runs as dislocation_runs_service

    bundle_hash = (row.bundle or {}).get("content_hash")
    if bundle_hash is None:
        raise _evidence_incomplete(
            ref, "FR-257 limb (2): the version has no compiled bundle for a Dislocation Run to name"
        )
    latest = await dislocation_runs_service.latest_run_for(
        session,
        workspace_id=workspace_id,
        candidate_ref=str(ref),
        candidate_bundle_hash=str(bundle_hash),
        baseline_ref=str(baseline),
    )
    if latest is not None:
        return latest.id
    keys = await dislocation_runs_service.candidate_run_keys(
        session, workspace_id=workspace_id, candidate_ref=str(ref)
    )
    if not keys:
        why = f"no Dislocation Run names this version as its candidate against {baseline}"
    elif not any(candidate_hash == str(bundle_hash) for candidate_hash, _ in keys):
        why = (
            f"every Dislocation Run of this version is on an earlier bundle hash than its "
            f"current {bundle_hash} (stale)"
        )
    else:
        why = (
            f"no Dislocation Run at this version's current bundle hash has {baseline}, the "
            "current live version, as its baseline"
        )
    raise _evidence_incomplete(ref, f"FR-257 limb (2): {why}")


async def approximation_fidelity_statements(
    session: AsyncSession, *, workspace_id: UUID, row: RatingVersionRow
) -> list[str]:
    """FR-136's pre-check for FR-224 (DP-S5-5 (a), `03` FR-224): the fidelity statements of the
    models a version references in `approximation` mode, or `EVIDENCE_INCOMPLETE` naming the
    first model whose transparency artifact has no GLM approximation (or none at all).

    A model with no approximation cannot be rated in `approximation` mode (`02` FR-133), so
    refusing it before a portfolio run is spent is the "plainly poor surrogate" case with no
    new threshold. Run at `POST /dislocation-runs` for an exact-mode baseline spec and again
    at submission; the statements are copied onto the evidence for the approver. A version
    that references no model in `approximation` mode yields none.
    """
    ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)
    algorithm = await _algorithm_of(session, workspace_id=workspace_id, rating_version=row)
    if algorithm is None:
        return []
    model_refs = sorted(
        {
            step.model_ref
            for step in algorithm.steps
            if isinstance(step, RatingModelCallStep)
            and step.mode == "approximation"
            and step.model_ref is not None
        },
        key=str,
    )
    statements: list[str] = []
    for model_ref in model_refs:
        model = await session.scalar(
            select(ModelRow).where(
                ModelRow.workspace_id == workspace_id,
                ModelRow.model_family_slug == model_ref.slug,
                ModelRow.version == model_ref.version,
            )
        )
        if model is None:
            raise _evidence_incomplete(ref, f"FR-136: {model_ref} is not a model of this workspace")
        try:
            artifact = await transparency_service.load_transparency(
                session, workspace_id=workspace_id, model_id=model.id
            )
        except PlatformError as exc:
            if exc.code != "NOT_FOUND":
                raise
            raise _evidence_incomplete(
                ref,
                f"FR-136: {model_ref} is referenced in approximation mode but has no "
                "transparency artifact",
            ) from exc
        if artifact.glm_approximation is None:
            raise _evidence_incomplete(
                ref,
                f"FR-136: {model_ref} is referenced in approximation mode but its transparency "
                "artifact has no GLM approximation",
            )
        statements.append(f"{model_ref}: {artifact.fidelity_statement}")
    return statements


async def _approximation_gate(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    row: RatingVersionRow,
    ref: ArtifactRef,
    policy: ApprovalPolicy,
) -> ApproximationCheck | None:
    """FR-224: an `approximation`-mode version is held to the policy's threshold (DP-S5-2).

    `None` for an `exact`-mode version, which the gate does not touch. Otherwise, in order:
    FR-136's pre-check (cheap, ahead of any figure), the latest Dislocation Run whose spec
    named this version at its current bundle hash as both baseline and candidate; then that
    run's observed `abs_change_pct_quantiles` at the declared quantile against the maximum. A run with no figure (an empty banded set, or
    one made before the field) is refused, never read as zero (RL-1504 T7 choice (3)).

    The threshold is read **only** from the `rating_version` policy entry, falling back to
    `DEFAULT_APPROXIMATION_DEVIATION` when the entry leaves it unset: no value switches the
    gate off, and nothing here reaches `Settings` or the environment (`RL-1264` DP-3 (b)).
    """
    if row.model_reference_mode != "approximation":
        return None
    from app.platform import dislocation_runs as dislocation_runs_service  # cycle, as limb (2)

    statements = await approximation_fidelity_statements(
        session, workspace_id=workspace_id, row=row
    )
    entry = policy.entry_for("rating_version")
    threshold = (
        entry.approximation_deviation
        if entry is not None and entry.approximation_deviation is not None
        else DEFAULT_APPROXIMATION_DEVIATION
    )
    bundle_hash = (row.bundle or {}).get("content_hash")
    latest = (
        None
        if bundle_hash is None
        else await dislocation_runs_service.latest_run_for(
            session,
            workspace_id=workspace_id,
            candidate_ref=str(ref),
            candidate_bundle_hash=str(bundle_hash),
            baseline_ref=str(ref),
        )
    )
    if latest is None:
        raise _evidence_incomplete(
            ref,
            "FR-224: an approximation-mode version needs a Dislocation Run against its own "
            "exact-mode twin at its current bundle hash, and there is none",
        )
    figures = DislocationRun.model_validate(latest.run).abs_change_pct_quantiles
    observed = None if figures is None else figures.get(threshold.quantile_key)
    if observed is None:
        raise _evidence_incomplete(
            ref,
            f"FR-224: the Dislocation Run {latest.id} has no figure at quantile "
            f"{threshold.quantile_key} (an empty banded set, or a run made before the field)",
        )
    if Decimal(observed) > threshold.max_abs_change_pct:
        raise _evidence_incomplete(
            ref,
            f"FR-224: the absolute percentage change at the {threshold.quantile_key} quantile "
            f"is {observed}%, above the policy's maximum of {threshold.max_abs_change_pct}% "
            f"(Dislocation Run {latest.id})",
        )
    return ApproximationCheck(
        dislocation_run_id=latest.id,
        quantile=Decimal(threshold.quantile_key),
        observed_abs_change_pct=Decimal(observed),
        max_abs_change_pct=threshold.max_abs_change_pct,
        fidelity_statements=tuple(statements),
    )


def _empty_algorithm(*, like: RatingAlgorithm) -> RatingAlgorithm:
    """The algorithm a first version is diffed against (DP-S5-1 (a)): the same slug, no inputs,
    no outputs, no steps, so every step of the first version is an addition."""
    return RatingAlgorithm(
        slug=like.slug, version=like.version, input_contract=[], outputs=[], steps=[]
    )


async def _algorithm_of(
    session: AsyncSession, *, workspace_id: UUID, rating_version: RatingVersionRow
) -> RatingAlgorithm | None:
    """The saved Rating Algorithm a version points at, or `None` for a version without one."""
    if rating_version.algorithm_ref is None:
        return None
    algorithm_ref = ArtifactRef.model_validate(rating_version.algorithm_ref)
    saved = await session.scalar(
        select(RatingAlgorithmRow).where(
            RatingAlgorithmRow.workspace_id == workspace_id,
            RatingAlgorithmRow.slug == algorithm_ref.slug,
            RatingAlgorithmRow.version == algorithm_ref.version,
        )
    )
    return None if saved is None else RatingAlgorithm.model_validate(saved.content)


async def _structural_diff_gate(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    row: RatingVersionRow,
    ref: ArtifactRef,
    baseline: ArtifactRef | None,
    blob_store: BlobStore,
) -> str:
    """FR-219's diff, computed at submission and stored: the blob's sha256 to record.

    The bytes are `AlgorithmDiff.model_dump_json()` of the baseline's algorithm (DP-S5-1:
    the same baseline limb (2) uses; an empty algorithm for a first version) against this
    version's. A version with no algorithm has nothing to diff and fails closed (R4).
    """
    candidate = await _algorithm_of(session, workspace_id=workspace_id, rating_version=row)
    if candidate is None:
        raise _evidence_incomplete(
            ref, "FR-219: a version with no saved Rating Algorithm has no structural diff"
        )
    previous = None
    if baseline is not None:
        baseline_row = await resolve_rating_version_ref(
            session, workspace_id=workspace_id, ref=baseline
        )
        previous = await _algorithm_of(
            session, workspace_id=workspace_id, rating_version=baseline_row
        )
    diff = diff_algorithms(
        previous if previous is not None else _empty_algorithm(like=candidate), candidate
    )
    stored = await blob_store.put(session, diff.model_dump_json().encode(), "application/json")
    # The row holds a reference to the blob for as long as the version exists, so FR-420's
    # collector (`ref_count == 0`) can never take it (the pattern `traces.write_trace` uses).
    await blobs.retain(session, stored.sha256)
    return stored.sha256


def structural_diff_verified(row: RatingVersionRow) -> bool:
    """Whether the evidence names a stored structural diff: Slice 6's `verifiable` entry for
    `structural_diff` (`06` FR-364's 2026-09-28 amendment, RL-1184 E4)."""
    return bool((row.evidence or {}).get("structural_diff_blob"))


def dislocation_run_verified(row: RatingVersionRow) -> bool:
    """Whether the evidence shows limb (2) satisfied: a run id, or the recorded first-version
    case. Slice 6's `verifiable` entry for `dislocation_run` (PL-1500 Hand-off)."""
    evidence = row.evidence or {}
    return evidence.get("dislocation_run_id") is not None or (
        evidence.get("no_baseline") == "first_version"
    )


def _evidence_incomplete(ref: ArtifactRef, why: str) -> PlatformError:
    return PlatformError(
        "EVIDENCE_INCOMPLETE", "Required evidence is missing", 422, f"{ref}: {why}."
    )


def _not_checked(
    reason: Literal["no_algorithm_ref", "no_suite_for_algorithm"],
) -> dict[str, Any]:
    return GoldenQuoteNotChecked(
        status="not_checked",
        regression_suite="none",
        message="no golden quotes were checked",
        reason=reason,
    ).model_dump(mode="json")


async def _baseline(
    session: AsyncSession, *, workspace_id: UUID, algorithm_slug: str, exclude_id: UUID
) -> tuple[RatingVersionRow, GoldenQuoteCheck | None] | None:
    """The most recently approved other version of the algorithm, by the `at` of its
    `rating_version.approved` Audit Event — the audit trail is the one source — with its
    pinned golden-quote check, if it was checked."""
    candidates = [
        candidate
        for candidate in (
            await session.execute(
                select(RatingVersionRow).where(
                    RatingVersionRow.workspace_id == workspace_id,
                    RatingVersionRow.status.in_(_APPROVED_OR_AFTER),
                    RatingVersionRow.algorithm_ref.is_not(None),
                    RatingVersionRow.id != exclude_id,
                )
            )
        ).scalars()
        if ArtifactRef.model_validate(candidate.algorithm_ref).slug == algorithm_slug
    ]
    if not candidates:
        return None
    by_ref = {f"rating_version:{c.slug}@{c.version}": c for c in candidates}
    approved_at = {
        entity_ref: at
        for entity_ref, at in (
            await session.execute(
                select(AuditEventRow.entity_ref, func.max(AuditEventRow.at))
                .where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == "rating_version.approved",
                    AuditEventRow.entity_ref.in_(list(by_ref)),
                )
                .group_by(AuditEventRow.entity_ref)
            )
        ).all()
    }
    if not approved_at:
        return None
    latest = max(approved_at, key=lambda entity_ref: approved_at[entity_ref])
    baseline = by_ref[latest]
    pinned = (baseline.evidence or {}).get("golden_quotes")
    check = (
        GoldenQuoteCheck.model_validate(pinned)
        if pinned is not None and pinned.get("status") == "checked"
        else None
    )
    return baseline, check


def _compared(quote: GoldenQuote) -> dict[str, Any]:
    """The three fields the delta compares; `note` is deliberately not one of them."""
    return {
        "expected": quote.expected,
        "tolerance": quote.tolerance,
        "context": context_hash(quote.context),
    }


def _quotes(version: RegressionSuiteVersionRow | None) -> dict[str, GoldenQuote]:
    if version is None:
        return {}
    content = RegressionSuiteContent.model_validate(version.content)
    return {quote.name: quote for quote in content.golden_quotes}


def _step_fields(before: GoldenQuote | None, after: GoldenQuote | None) -> list[str]:
    if before is None and after is None:
        return []
    if before is None:
        return ["added"]
    if after is None:
        return ["removed"]
    old, new = _compared(before), _compared(after)
    return [field for field in ("expected", "tolerance", "context") if old[field] != new[field]]


async def _author_of_suite_version(
    session: AsyncSession, *, workspace_id: UUID, suite_slug: str, version: int
) -> UUID:
    """The actor of the version's `regression_suite.created` Audit Event (`06` FR-368,
    #861's definition) — never the row's `created_by`. Missing: refused, fail-closed."""
    entity_ref = regression_suites_service.entity_ref(suite_slug, version)
    actor = (
        await session.execute(
            select(AuditEventRow.actor).where(
                AuditEventRow.workspace_id == workspace_id,
                AuditEventRow.action == regression_suites_service.CREATED_ACTION,
                AuditEventRow.entity_ref == entity_ref,
            )
        )
    ).scalars().first()
    if actor is None or actor.get("id") is None:
        raise PlatformError(
            "APPROVAL_AUTHOR_UNRESOLVED",
            "The author of a golden-quote change cannot be established",
            403,
            f"{entity_ref} has no creation Audit Event, so who changed its golden quotes "
            "cannot be shown to the approver. `03` FR-260 and `06` FR-353: refused, never "
            "submitted unchecked.",
        )
    return UUID(str(actor["id"]))


async def _golden_quote_delta(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    algorithm_slug: str,
    suite: RegressionSuiteRow,
    current: RegressionSuiteVersionRow,
    exclude_id: UUID,
) -> GoldenQuoteDelta:
    """Every golden quote added, removed, or whose expected output, tolerance or context
    changed since the suite pinned by the previous approved version of the algorithm,
    each with every substantive step and its author (the deputy's DP-S2-1 condition)."""
    versions = await regression_suites_service.suite_versions(session, suite=suite)
    by_number = {version.version: version for version in versions}

    found = await _baseline(
        session, workspace_id=workspace_id, algorithm_slug=algorithm_slug,
        exclude_id=exclude_id,
    )
    baseline_rv, baseline_check = found if found is not None else (None, None)
    baseline_version = 0
    if (
        baseline_check is not None
        and baseline_check.suite_ref.slug == suite.slug
        and baseline_check.suite_ref.version in by_number
    ):
        baseline_version = baseline_check.suite_ref.version

    steps: dict[str, list[GoldenQuoteChangeStep]] = {}
    previous = _quotes(by_number.get(baseline_version))
    for number in range(baseline_version + 1, current.version + 1):
        quotes = _quotes(by_number.get(number))
        touched = {
            name: fields
            for name in sorted(set(previous) | set(quotes))
            if (fields := _step_fields(previous.get(name), quotes.get(name)))
        }
        if touched:
            author = await _author_of_suite_version(
                session, workspace_id=workspace_id, suite_slug=suite.slug, version=number
            )
            for name, fields in touched.items():
                steps.setdefault(name, []).append(
                    GoldenQuoteChangeStep.model_validate(
                        {"version": number, "changed_fields": fields, "author": author}
                    )
                )
        previous = quotes

    before_quotes = _quotes(by_number.get(baseline_version))
    after_quotes = _quotes(current)
    changes: list[GoldenQuoteChange] = []
    for name in sorted(set(before_quotes) | set(after_quotes)):
        before, after = before_quotes.get(name), after_quotes.get(name)
        net = _step_fields(before, after)
        if not net:
            continue
        change = "added" if before is None else "removed" if after is None else "changed"
        changes.append(
            GoldenQuoteChange.model_validate(
                {
                    "name": name,
                    "change": change,
                    "changed_fields": net if change == "changed" else [],
                    "before": before.expected if before else None,
                    "after": after.expected if after else None,
                    "before_tolerance": before.tolerance if before else None,
                    "after_tolerance": after.tolerance if after else None,
                    "before_context_hash": context_hash(before.context) if before else None,
                    "after_context_hash": context_hash(after.context) if after else None,
                    "steps": steps.get(name, []),
                }
            )
        )

    return GoldenQuoteDelta(
        baseline_rating_version_ref=(
            ArtifactRef(type="rating_version", slug=baseline_rv.slug, version=baseline_rv.version)
            if baseline_rv is not None and baseline_check is not None
            else None
        ),
        baseline_suite_ref=baseline_check.suite_ref if baseline_check is not None else None,
        baseline_suite_content_hash=(
            baseline_check.suite_content_hash if baseline_check is not None else None
        ),
        changes=changes,
    )


async def golden_quote_delta_authors(
    session: AsyncSession, *, workspace_id: UUID, artifact_ref: ArtifactRef
) -> set[UUID]:
    """Every author of every step of every change in the version's golden-quote delta.

    Empty when the version was not checked, and when `evidence.golden_quotes` is absent
    (a version already in review when the gate shipped was never gated, so there is no
    suite change to judge). A load failure or an unparsable evidence blob propagates, so
    a decision is refused rather than made without this check (re-audit N2).
    """
    row = await resolve_rating_version_ref(session, workspace_id=workspace_id, ref=artifact_ref)
    pinned = (row.evidence or {}).get("golden_quotes")
    if pinned is None or pinned.get("status") != "checked":
        return set()
    check = GoldenQuoteCheck.model_validate(pinned)
    return {step.author for change in check.delta.changes for step in change.steps}
