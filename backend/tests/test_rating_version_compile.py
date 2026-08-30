"""Rating Version compile endpoint (slice W9-3, FR-RATE-24/25; W11 Task 1.2).

A pinned version compiles to a self-contained Bundle with a reproducible hash; an
unpinned version and a broken guard are refused with named errors. Compilation is a
`rating.compile` Job since Task 1.2 (Ruling 2) — the route answers 202 rather than
computing synchronously — and every resolver branch (rate tables, reference tables,
custom objectives, models) must resolve real content, embedded inline per Ruling 7, for
the Job to succeed rather than fail with `NOT_FOUND` / `PIN_NOT_APPROVED`.
"""

from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

import pytest
from backend.tests.test_api_reference import _table as _seed_reference_table
from backend.tests.test_custom_objectives_api import _advance, _create
from backend.tests.test_model_jobs_gbm import _fitted_gbm
from backend.tests.test_rate_tables_service import _seed as _seed_rate_table
from backend.tests.test_rate_tables_service import _table_slug as _rate_table_slug
from sqlalchemy import select

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.db.models import (
    AuditEventRow,
    BlobRow,
    JobRow,
    ModelRow,
    RateTableVersionRow,
    RatingAlgorithmRow,
    RatingVersionRow,
)
from app.db.session import Database
from app.platform import rating_versions
from app.platform.blobs import BlobStore, to_ref
from app.platform.rating_versions import compile_rating_version
from app.worker.rating_handlers import register_rating_handlers
from app.worker.tasks import execute_job
from model_schema import JobSource, JobStatus, ModelStatus, ObjectiveStatus
from pricing_core.rating.compile import _APPROVED_OR_BETTER, Bundle


@pytest.fixture(autouse=True)
def _handlers() -> None:
    register_rating_handlers()


def _minimal_algorithm() -> dict:
    """A minimal graph with no external artifact refs — input, expression, output."""
    return {
        "slug": "minimal",
        "version": 1,
        "input_contract": [
            {"name": "premium_in", "type": "int", "nullable": False},
        ],
        "outputs": [
            {"name": "payable_premium_minor", "type": "money_minor", "required": True},
        ],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In",
             "input_name": "premium_in", "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_expr", "type": "expression", "label": "Apply",
             "expr": "premium_in * 2", "result_type": "money_minor",
             "consumes": ["premium_in"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }


def _headers(principal, workspace_id) -> dict[str, str]:
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }


def _empty_pins() -> dict:
    return {"rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": []}


async def _insert_version(
    database, workspace_id, created_by, algorithm_ref: str | None, pins: dict
) -> RatingVersionRow:
    row = RatingVersionRow(
        workspace_id=workspace_id,
        slug="minimal-rv",
        version=1,
        status="draft",
        dataset_version_id=uuid4(),
        model_ref="model:motor-ad-frequency@7",
        created_by=created_by,
        algorithm_ref=algorithm_ref,
        pins=pins,
    )
    async with database.unit_of_work() as session:
        session.add(row)
        await session.flush()
        return row


def _run_compile_job(
    api_client, headers: dict[str, str], database: Database, blob_store: BlobStore,
    rating_version_id: UUID,
) -> JobRow:
    """POST the compile route, drive the returned Job synchronously (no live worker in
    tests — the `test_worker_rate_tables` convention), and return the finished `JobRow`."""
    response = api_client.post(
        f"/api/v1/rating-versions/{rating_version_id}/compile", headers=headers
    )
    assert response.status_code == 202, response.text
    job_body = response.json()
    assert response.headers["Location"] == f"/api/v1/jobs/{job_body['id']}"
    job_id = UUID(job_body["id"])

    async def _run() -> JobRow:
        job_status = await execute_job(database, job_id, blob_store)
        async with database.session() as session:
            row = await session.get(JobRow, job_id)
        assert row is not None
        assert row.status is job_status
        return row

    return asyncio.get_event_loop().run_until_complete(_run())


def _read_blob(database: Database, blob_store: BlobStore, sha256: str) -> bytes:
    async def _run() -> bytes:
        async with database.session() as session:
            row = await session.get(BlobRow, sha256)
        assert row is not None
        return await blob_store.read(to_ref(row))

    return asyncio.get_event_loop().run_until_complete(_run())


@pytest.mark.req("FR-RATE-24")
def test_a_pinned_version_compiles_over_http(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms",
        json=_minimal_algorithm(),
        headers=headers,
    )
    assert created.status_code == 201, created.text

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins=_empty_pins(),
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    assert job_row.result["kind"] == "blob"
    payload = _read_blob(database, blob_store, job_row.result["ref"])
    bundle = Bundle.model_validate_json(payload)
    assert bundle.content_hash.startswith("sha256:")
    assert bundle.graph.nodes


@pytest.mark.req("FR-RATE-22")
def test_an_unpinned_version_is_refused_over_http(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database, workspace_id, principal.id, algorithm_ref=None, pins=_empty_pins()
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "RATING_VERSION_UNPINNED"


@pytest.mark.req("FR-RATE-25")
def test_a_version_pinning_a_rate_table_compiles(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """A Rating Version pinning a real W10 rate table resolves and compiles.

    Before Task 1.2, `_Resolver`'s catch-all refuses every `rate_table` ref with
    `NOT_FOUND` and the detail `"has no backend table yet (Phase 2)"` — verified against
    unmodified `rating_versions.py` before this task's resolver branch was added.
    """
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    family = f"mf-{uuid4().hex[:8]}"
    slug = _rate_table_slug()
    seeded = asyncio.get_event_loop().run_until_complete(
        _seed_rate_table(database, workspace_id, principal, family, slug, blob_store)
    )

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [f"rate_table:{seeded.slug}@{seeded.version}"],
                "models": [],
                "reference_tables": [],
                "custom_objectives": [],
            },
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    payload = _read_blob(database, blob_store, job_row.result["ref"])
    bundle = Bundle.model_validate_json(payload)
    ref_key = f"rate_table:{seeded.slug}@{seeded.version}"
    assert ref_key in bundle.resolved_payloads
    assert bundle.resolved_payloads[ref_key]["rows"], "the rate table's rows were dropped"


@pytest.mark.req("FR-OVR-14")
def test_rate_table_version_row_has_no_status_column() -> None:
    """Self-invalidating guard for Ruling 22's `rate_table` maturity exemption.

    `docs/plans/2026-08-29-w11-1-2-rate-table-maturity-ruling.md`: the resolver above
    cannot report `rate_table`'s real maturity because `RateTableVersionRow` has none to
    read, so `pricing_core.rating.compile._MATURITY_CHECK_EXEMPT` exempts the type from
    the FR-OVR-14 floor rather than inventing `"approved"`. That exemption is only sound
    while the premise holds. This test is the tripwire: the day a migration adds a
    `status` column to `rate_table_versions`, it fails and names this record — the
    exemption (and `OQ-RATE-7`) must be revisited rather than carried forward silently.
    """
    assert "status" not in RateTableVersionRow.__table__.columns, (
        "RateTableVersionRow gained a status column — Ruling 22's rate_table maturity "
        "exemption (docs/plans/2026-08-29-w11-1-2-rate-table-maturity-ruling.md) and "
        "OQ-RATE-7 must be revisited: the resolver should report this real status "
        "instead of staying exempt from the FR-OVR-14 floor."
    )


@pytest.mark.req("FR-OVR-14")
def test_rating_algorithm_row_has_no_status_column() -> None:
    """Self-invalidating guard for Ruling 28's `rating_algorithm` maturity exemption.

    `docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`: the resolver above cannot
    report `rating_algorithm`'s real maturity because `RatingAlgorithmRow` has none to
    read, so `pricing_core.rating.compile._MATURITY_CHECK_EXEMPT` exempts the type from
    the FR-OVR-14 floor rather than inventing `"approved"`. That exemption is only sound
    while the premise holds. This test is the tripwire: the day a migration adds a
    `status` column to `rating_algorithms`, it fails and names this record — the
    exemption must be revisited rather than carried forward silently.
    """
    assert "status" not in RatingAlgorithmRow.__table__.columns, (
        "RatingAlgorithmRow gained a status column — Ruling 28's rating_algorithm "
        "maturity exemption (docs/plans/2026-08-29-w11-algorithm-pin-maturity.md) must "
        "be revisited: the resolver should report this real status instead of staying "
        "exempt from the FR-OVR-14 floor."
    )


def _statuses_the_backend_resolver_reported(
    database: Database,
    blob_store: BlobStore,
    workspace_id: UUID,
    monkeypatch: pytest.MonkeyPatch,
    rating_version_id: UUID,
) -> dict[str, str]:
    """Compile a Rating Version and return `{ref: status}` for every ref the **backend**
    resolver reported to `compile_bundle`.

    The two tripwires below need the value `rating_versions._Resolver` *produces*, not one
    a test supplies. The suite's only other uses of the sentinel are the two
    `_statuses[...] = "no_maturity_concept"` assignments in pricing-core's **fake** resolver
    (`packages/pricing-core/tests/test_rating_compile_bundle.py`), which *set* the value and
    so cannot notice the backend handing back something else. This wraps the real resolver
    on its way into `compile_bundle` and records what it returned.
    """
    captured: dict[str, str] = {}
    real_compile_bundle = rating_versions.compile_bundle

    async def _recording_compile_bundle(version, resolver):
        class _Recorder:
            async def resolve(self, ref):
                resolved = await resolver.resolve(ref)
                captured[str(ref)] = resolved.status
                return resolved

        return await real_compile_bundle(version, _Recorder())

    monkeypatch.setattr(rating_versions, "compile_bundle", _recording_compile_bundle)

    async def _run() -> None:
        async with database.unit_of_work() as session:
            await compile_rating_version(
                session,
                workspace_id=workspace_id,
                rating_version_id=rating_version_id,
                blob_store=blob_store,
            )

    asyncio.get_event_loop().run_until_complete(_run())
    return captured


@pytest.mark.req("FR-OVR-14")
def test_the_resolver_reports_the_algorithm_sentinel_not_an_invented_approval(
    api_client, workspace_id, principal, grant, database, blob_store, monkeypatch
) -> None:
    """Ruling 28 part 1's tripwire: the `rating_algorithm` branch must keep failing closed.

    `docs/plans/2026-08-29-w11-algorithm-pin-maturity.md` replaced an invented
    `status="approved"` with the `"no_maturity_concept"` sentinel because the invented
    value put a constant where `compile_bundle`'s gate reads a discriminator: it is
    `_MATURITY_CHECK_EXEMPT` that admits this pin past the FR-OVR-14 floor, and the
    sentinel is deliberately not a member of `_APPROVED_OR_BETTER`, so the pin still fails
    **closed** on the day the exemption is lifted. Reverting
    `rating_versions.py`'s `rating_algorithm` branch to `"approved"` left the whole backend
    suite green before this test existed (audit of PR #416, finding ③) — a regression that
    lands green, sits dormant, and then silently admits every algorithm as approved the
    moment someone removes the exemption expecting enforcement to start.

    Both halves are asserted: the sentinel is what the resolver produces, *and* it is
    outside `_APPROVED_OR_BETTER`. Asserting only the first would pass if
    `"no_maturity_concept"` were later added to the approved set.
    """
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins=_empty_pins(),
        )
    )

    statuses = _statuses_the_backend_resolver_reported(
        database, blob_store, workspace_id, monkeypatch, row.id
    )

    assert statuses.get("rating_algorithm:minimal@1") == "no_maturity_concept", (
        "the backend resolver no longer reports the `no_maturity_concept` sentinel for a "
        "rating_algorithm pin — it reported "
        f"{statuses.get('rating_algorithm:minimal@1')!r}. Ruling 28 part 1 "
        "(docs/plans/2026-08-29-w11-algorithm-pin-maturity.md) forbids inventing a "
        "maturity `RatingAlgorithmRow` has no column to back. If this is deliberate, the "
        "row now has a real status to read and the `_MATURITY_CHECK_EXEMPT` membership "
        "must go with it."
    )
    assert "no_maturity_concept" not in _APPROVED_OR_BETTER, (
        "the sentinel joined `_APPROVED_OR_BETTER`, so an algorithm pin would now pass "
        "the FR-OVR-14 floor on the sentinel itself rather than on the exemption — the "
        "fail-closed property Ruling 28 part 1 was written for is gone."
    )


@pytest.mark.req("FR-OVR-14")
def test_the_resolver_reports_the_rate_table_sentinel_not_an_invented_approval(
    api_client, workspace_id, principal, grant, database, blob_store, monkeypatch
) -> None:
    """Ruling 22's list-mate of the tripwire above — the same hole, same shape.

    `docs/plans/2026-08-29-w11-1-2-rate-table-maturity-ruling.md` states the safety
    property in terms: *"the sentinel below is deliberately not a member of
    `_APPROVED_OR_BETTER`, so a pin still fails closed if the exemption is ever removed
    without this branch being updated to match."* That property had no test either
    (audit of PR #416, finding ③), and Ruling 22's exemption is the *provisional* one —
    OQ-RATE-7 may remove it — so it is the likelier of the two to be lifted.
    """
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    family = f"mf-{uuid4().hex[:8]}"
    slug = _rate_table_slug()
    seeded = asyncio.get_event_loop().run_until_complete(
        _seed_rate_table(database, workspace_id, principal, family, slug, blob_store)
    )
    ref_key = f"rate_table:{seeded.slug}@{seeded.version}"

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [ref_key],
                "models": [],
                "reference_tables": [],
                "custom_objectives": [],
            },
        )
    )

    statuses = _statuses_the_backend_resolver_reported(
        database, blob_store, workspace_id, monkeypatch, row.id
    )

    assert statuses.get(ref_key) == "no_maturity_concept", (
        "the backend resolver no longer reports the `no_maturity_concept` sentinel for a "
        f"rate_table pin — it reported {statuses.get(ref_key)!r}. Ruling 22 "
        "(docs/plans/2026-08-29-w11-1-2-rate-table-maturity-ruling.md) refused inventing "
        "a maturity `RateTableVersionRow` has no column to back; see also OQ-RATE-7."
    )
    assert "no_maturity_concept" not in _APPROVED_OR_BETTER, (
        "the sentinel joined `_APPROVED_OR_BETTER`, so a rate_table pin would now pass "
        "the FR-OVR-14 floor on the sentinel itself rather than on the exemption — the "
        "fail-closed property Ruling 22 states in terms is gone."
    )


@pytest.mark.req("FR-RATE-25")
def test_a_version_pinning_a_published_reference_table_compiles(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """A Rating Version pinning a *published* reference table version resolves.

    FR-DATA-30's own lifecycle (`draft`/`published`) is not `compile_bundle`'s generic
    `approved`/`live`/`retired` maturity vocabulary; the resolver bridges "published" to
    "approved" so a real, published reference table can compile at all.
    """
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("admin"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    slug = _seed_reference_table(api_client, headers, publish=True)

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [],
                "models": [],
                "reference_tables": [f"reference_table:{slug}@1"],
                "custom_objectives": [],
            },
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    payload = _read_blob(database, blob_store, job_row.result["ref"])
    bundle = Bundle.model_validate_json(payload)
    ref_key = f"reference_table:{slug}@1"
    assert ref_key in bundle.resolved_payloads
    assert bundle.resolved_payloads[ref_key]["rows"], "the reference table's rows were dropped"


@pytest.mark.req("FR-OVR-14")
def test_a_version_pinning_an_unpublished_reference_table_is_refused(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """A `draft` reference table version is still refused — the bridge must not fake
    maturity for a version that was never published."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("admin"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    slug = _seed_reference_table(api_client, headers, publish=False)

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [],
                "models": [],
                "reference_tables": [f"reference_table:{slug}@1"],
                "custom_objectives": [],
            },
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "PIN_NOT_APPROVED"


@pytest.mark.req("FR-RATE-25")
def test_a_version_pinning_an_approved_custom_objective_compiles(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    objective = _create(api_client, headers)
    _advance(UUID(objective["id"]), status=ObjectiveStatus.APPROVED)

    objective_ref = f"custom_objective:{objective['slug']}@{objective['version']}"
    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [],
                "models": [],
                "reference_tables": [],
                "custom_objectives": [objective_ref],
            },
        )
    )

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    payload = _read_blob(database, blob_store, job_row.result["ref"])
    bundle = Bundle.model_validate_json(payload)
    assert objective_ref in bundle.resolved_payloads


@pytest.mark.req("FR-RATE-24")
def test_the_compiled_bundle_survives_persistence(
    workspace_id, principal, grant, database, blob_store, api_client
) -> None:
    """Compile, fetch the Bundle back from the blob store, and confirm nothing was
    dropped — including a GBM's booster, which must be the content itself (Ruling 7),
    never a blob reference `load_bundle` (Task 1.3) could not fetch without I/O."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    async def _seed_gbm() -> str:
        model_id, fit_status = await _fitted_gbm(database, blob_store, workspace_id)
        assert fit_status is JobStatus.SUCCEEDED
        async with database.unit_of_work() as session:
            model_row = await session.get(ModelRow, model_id)
            assert model_row is not None
            model_row.status = ModelStatus.APPROVED.value
            slug, version = model_row.model_family_slug, model_row.version
        return f"model:{slug}@{version}"

    model_ref = asyncio.get_event_loop().run_until_complete(_seed_gbm())

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins={
                "rate_tables": [],
                "models": [model_ref],
                "reference_tables": [],
                "custom_objectives": [],
            },
        )
    )

    async def _in_process_bundle() -> Bundle:
        async with database.unit_of_work() as session:
            return await compile_rating_version(
                session, workspace_id=workspace_id, rating_version_id=row.id,
                blob_store=blob_store,
            )

    in_process_bundle = asyncio.get_event_loop().run_until_complete(_in_process_bundle())

    job_row = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    assert job_row.result["kind"] == "blob"

    payload = _read_blob(database, blob_store, job_row.result["ref"])
    restored = Bundle.model_validate_json(payload)
    assert restored.graph.nodes, "the persisted Bundle has an empty graph"
    assert restored.resolved_payloads, "the persisted Bundle has no resolved payloads"
    assert restored.content_hash == in_process_bundle.content_hash

    fit_result = restored.resolved_payloads[model_ref]["fit_result"]
    assert fit_result["model_type"] in ("xgboost", "lightgbm")
    assert "booster_content" in fit_result, "the booster is missing from the payload"
    # The proof Ruling 7 asks for: real serialised booster content, not a blob sha256.
    assert len(fit_result["booster_content"]) > 100
    assert fit_result["booster_content"] != fit_result["booster_blob"]["sha256"]


def _compile_audit_events(database: Database, workspace_id: UUID) -> list[AuditEventRow]:
    """Every `rating_version.compiled` event for the workspace, oldest first.

    Ordered by `id` rather than `at`: `id` is a uuid7 and so monotonic, while `at` defaults
    to `func.now()` — transaction time — and two compiles in one test can tie on it.
    """

    async def _run() -> list[AuditEventRow]:
        async with database.session() as session:
            rows = (
                await session.execute(
                    select(AuditEventRow)
                    .where(
                        AuditEventRow.workspace_id == workspace_id,
                        AuditEventRow.action == "rating_version.compiled",
                    )
                    .order_by(AuditEventRow.id)
                )
            ).scalars()
            return list(rows)

    return asyncio.get_event_loop().run_until_complete(_run())


@pytest.mark.req("NFR-RATE-10")
def test_a_compile_emits_an_audit_event_carrying_before_and_after_bundle_hashes(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """NFR-RATE-10: compilations "emit Audit Events with before/after state".

    W11 Task 1.2 built the `rating.compile` Job with no audit event at all, so the one
    governed operation this workstream added left no trace in the chain `06` §4.5 exists
    to keep. The requirement names *before/after state*, not merely that something was
    recorded — so this compiles **twice** and asserts the second event's `before` carries
    the first compile's hash. A single compile can only ever show `before: None`, which
    would satisfy a weaker test while leaving the before/after half unevidenced.
    """
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)

    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text

    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins=_empty_pins(),
        )
    )

    first_job = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert first_job.status is JobStatus.SUCCEEDED, first_job.error
    first_bundle = Bundle.model_validate_json(
        _read_blob(database, blob_store, first_job.result["ref"])
    )

    events = _compile_audit_events(database, workspace_id)
    assert len(events) == 1, (
        "a successful compile emitted no `rating_version.compiled` audit event — found "
        f"{len(events)}. NFR-RATE-10 requires compilations to emit Audit Events with "
        "before/after state."
    )
    first = events[0]
    assert first.entity_ref == "rating_version:minimal-rv@1"
    assert first.source is JobSource.API, (
        "`JobSource` records the request's origin, not its executor — its members are UI, "
        "API, SCHEDULE and SYSTEM, and there is no WORKER. A compile submitted through "
        "the 202 route is `API` even though the worker runs it, matching "
        "`dataset_version.ingested`, which is emitted from inside a worker handler."
    )
    assert first.job_id == first_job.id, "the event must name the Job that produced it"
    assert first.before == {"bundle_hash": None}, (
        f"a first compile has no prior bundle, so `before` must say so: {first.before!r}"
    )
    assert first.after["bundle_hash"] == first_bundle.content_hash
    assert first.after["blob_sha256"] == first_job.result["ref"], (
        "the after-state must name the blob this compile actually wrote, not just the "
        "content hash. `blob_sha256` was added to `BundleMetadata` by Ruling 37, so the "
        "event describing the compile has to report it or the trail cannot answer 'which "
        "stored artifact did this produce' — and these are two different hashes: "
        f"{first.after!r} vs job result {first_job.result!r}"
    )

    # Compile again: only a second compile can evidence the *before* half of the
    # requirement, because the first has nothing to be "before".
    second_job = _run_compile_job(api_client, headers, database, blob_store, row.id)
    assert second_job.status is JobStatus.SUCCEEDED, second_job.error

    events = _compile_audit_events(database, workspace_id)
    assert len(events) == 2, "the second compile emitted no event"
    second = events[1]
    assert second.before == {"bundle_hash": first_bundle.content_hash}, (
        "the second compile's `before` must carry the hash the first one left, not None — "
        f"got {second.before!r}. Without it the chain cannot show what changed."
    )
    assert second.after["bundle_hash"] == first_bundle.content_hash, (
        "the same pins must compile to the same hash (FR-RATE-24 reproducibility)"
    )
    assert second.after["blob_sha256"] != first.after["blob_sha256"], (
        "the two compiles wrote the same blob, which they must not: `content_hash` is "
        "computed over the graph and pins alone — `bundle_hash`'s docstring excludes "
        "`compiled_at` because hashing a timestamp would break reproducibility — while the "
        "*stored payload* is `bundle.model_dump_json()`, which carries `compiled_at`. So "
        "identical pins give an identical `content_hash` and a different `blob_sha256`, and "
        "equal keys mean `compiled_at` did not vary. That would make the reproducibility "
        "assertion above far weaker than it reads: it would be comparing a bundle with "
        "itself rather than with an independently recompiled one. Two hashes of two "
        "different things — a hash certifies what it was computed over, and nothing else."
    )
    assert second.job_id == second_job.id
