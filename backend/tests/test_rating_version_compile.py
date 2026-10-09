"""Rating Version compile endpoint (slice W9-3, FR-239/240; WK-671 Task 1.2).

A pinned version compiles to a self-contained Bundle with a reproducible hash; an
unpinned version and a broken guard are refused with named errors. Compilation is a
`rating.compile` Job since Task 1.2 (RL-865) — the route answers 202 rather than
computing synchronously — and every resolver branch (rate tables, reference tables,
custom objectives, models) must resolve real content, embedded inline per RL-873, for
the Job to succeed rather than fail with `NOT_FOUND` / `PIN_NOT_APPROVED`.
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from backend.tests.approved_rows import mark_approved
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
    SubGraphVersionRow,
)
from app.db.session import Database
from app.platform import rating_versions
from app.platform.blobs import BlobStore, to_ref
from app.platform.rating_versions import compile_rating_version
from app.worker.rating_handlers import register_rating_handlers
from app.worker.tasks import execute_job
from model_schema import JobSource, JobStatus, ObjectiveStatus
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
    database,
    workspace_id,
    created_by,
    algorithm_ref: str | None,
    pins: dict,
    *,
    slug: str = "minimal-rv",
    version: int = 1,
) -> RatingVersionRow:
    row = RatingVersionRow(
        workspace_id=workspace_id,
        slug=slug,
        version=version,
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


@pytest.mark.req("FR-239")
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


@pytest.mark.req("FR-237")
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


@pytest.mark.req("FR-240")
def test_a_version_pinning_a_rate_table_compiles(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """A Rating Version pinning a real WK-670 rate table resolves and compiles.

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


@pytest.mark.req("FR-20")
def test_rate_table_version_row_has_no_status_column() -> None:
    """Self-invalidating guard for RL-856's `rate_table` maturity exemption.

    `docs/rulings/RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the-exemption-is-declared-and-self-invalidating.md`:
    the resolver above cannot report `rate_table`'s real maturity because
    `RateTableVersionRow` has none to
    read, so `pricing_core.rating.compile._MATURITY_CHECK_EXEMPT` exempts the type from
    the FR-20 floor rather than inventing `"approved"`. That exemption is only sound
    while the premise holds. This test is the tripwire: the day a migration adds a
    `status` column to `rate_table_versions`, it fails and names this record — the
    exemption (and `OQ-620`) must be revisited rather than carried forward silently.
    """
    assert "status" not in RateTableVersionRow.__table__.columns, (
        "RateTableVersionRow gained a status column — RL-856's rate_table maturity "
        "exemption (docs/rulings/RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the"
        "-exemption-is-declared-and-self-invalidating.md) and "
        "OQ-620 must be revisited: the resolver should report this real status "
        "instead of staying exempt from the FR-20 floor."
    )


@pytest.mark.req("FR-20")
def test_rating_algorithm_row_has_no_status_column() -> None:
    """Self-invalidating guard for RL-859's `rating_algorithm` maturity exemption.

    `docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`: the resolver above cannot
    report `rating_algorithm`'s real maturity because `RatingAlgorithmRow` has none to
    read, so `pricing_core.rating.compile._MATURITY_CHECK_EXEMPT` exempts the type from
    the FR-20 floor rather than inventing `"approved"`. That exemption is only sound
    while the premise holds. This test is the tripwire: the day a migration adds a
    `status` column to `rating_algorithms`, it fails and names this record — the
    exemption must be revisited rather than carried forward silently.
    """
    assert "status" not in RatingAlgorithmRow.__table__.columns, (
        "RatingAlgorithmRow gained a status column — RL-859's rating_algorithm "
        "maturity exemption (docs/plans/2026-08-29-w11-algorithm-pin-maturity.md) must "
        "be revisited: the resolver should report this real status instead of staying "
        "exempt from the FR-20 floor."
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


@pytest.mark.req("FR-20")
def test_the_resolver_reports_the_algorithm_sentinel_not_an_invented_approval(
    api_client, workspace_id, principal, grant, database, blob_store, monkeypatch
) -> None:
    """RL-859 part 1's tripwire: the `rating_algorithm` branch must keep failing closed.

    `docs/plans/2026-08-29-w11-algorithm-pin-maturity.md` replaced an invented
    `status="approved"` with the `"no_maturity_concept"` sentinel because the invented
    value put a constant where `compile_bundle`'s gate reads a discriminator: it is
    `_MATURITY_CHECK_EXEMPT` that admits this pin past the FR-20 floor, and the
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
        f"{statuses.get('rating_algorithm:minimal@1')!r}. RL-859 part 1 "
        "(docs/plans/2026-08-29-w11-algorithm-pin-maturity.md) forbids inventing a "
        "maturity `RatingAlgorithmRow` has no column to back. If this is deliberate, the "
        "row now has a real status to read and the `_MATURITY_CHECK_EXEMPT` membership "
        "must go with it."
    )
    assert "no_maturity_concept" not in _APPROVED_OR_BETTER, (
        "the sentinel joined `_APPROVED_OR_BETTER`, so an algorithm pin would now pass "
        "the FR-20 floor on the sentinel itself rather than on the exemption — the "
        "fail-closed property RL-859 part 1 was written for is gone."
    )


@pytest.mark.req("FR-20")
def test_the_resolver_reports_the_rate_table_sentinel_not_an_invented_approval(
    api_client, workspace_id, principal, grant, database, blob_store, monkeypatch
) -> None:
    """RL-856's list-mate of the tripwire above — the same hole, same shape.

    `docs/rulings/RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the-exemption-is-declared-and-self-invalidating.md`
    states the safety property in terms: *"the sentinel below is deliberately not a member of
    `_APPROVED_OR_BETTER`, so a pin still fails closed if the exemption is ever removed
    without this branch being updated to match."* That property had no test either
    (audit of PR #416, finding ③), and RL-856's exemption is the *provisional* one —
    OQ-620 may remove it — so it is the likelier of the two to be lifted.
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
        f"rate_table pin — it reported {statuses.get(ref_key)!r}. RL-856 "
        "(docs/rulings/RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the-exemption"
        "-is-declared-and-self-invalidating.md) refused inventing "
        "a maturity `RateTableVersionRow` has no column to back; see also OQ-620."
    )
    assert "no_maturity_concept" not in _APPROVED_OR_BETTER, (
        "the sentinel joined `_APPROVED_OR_BETTER`, so a rate_table pin would now pass "
        "the FR-20 floor on the sentinel itself rather than on the exemption — the "
        "fail-closed property RL-856 states in terms is gone."
    )


@pytest.mark.req("FR-240")
def test_a_version_pinning_a_published_reference_table_compiles(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """A Rating Version pinning a *published* reference table version resolves.

    FR-70's own lifecycle (`draft`/`published`) is not `compile_bundle`'s generic
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


@pytest.mark.req("FR-20")
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


@pytest.mark.req("FR-240")
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


@pytest.mark.req("FR-239")
def test_the_compiled_bundle_survives_persistence(
    workspace_id, principal, grant, database, blob_store, api_client
) -> None:
    """Compile, fetch the Bundle back from the blob store, and confirm nothing was
    dropped — including a GBM's booster, which must be the content itself (RL-873),
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
            await mark_approved(session, model_row)
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
    # The proof RL-873 asks for: real serialised booster content, not a blob sha256.
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


@pytest.mark.req("NFR-498")
def test_a_compile_emits_an_audit_event_carrying_before_and_after_bundle_hashes(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """NFR-498: compilations "emit Audit Events with before/after state".

    WK-671 Task 1.2 built the `rating.compile` Job with no audit event at all, so the one
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
        f"{len(events)}. NFR-498 requires compilations to emit Audit Events with "
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
        "content hash. `blob_sha256` was added to `BundleMetadata` by RL-915, so the "
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
        "the same pins must compile to the same hash (FR-239 reproducibility)"
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


# --- RL-1379: a Rating Version compiles only while `draft` (FR-239, 00 FR-4) -------------------


def _version_with_bundle(database: Database, workspace_id: UUID, created_by: UUID) -> UUID:
    """A compilable draft that has already been compiled once: `bundle` holds a hash and a key."""
    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database, workspace_id, created_by,
            algorithm_ref="rating_algorithm:minimal@1", pins=_empty_pins(),
            slug=f"rv-{uuid4().hex[:8]}",
        )
    )
    return row.id


def _set_status(database: Database, rating_version_id: UUID, status: str) -> None:
    async def _run() -> None:
        async with database.unit_of_work() as session:
            row = await session.get(RatingVersionRow, rating_version_id)
            assert row is not None
            if status == "approved":
                await mark_approved(session, row)
            else:
                row.status = status
                await session.flush()

    asyncio.get_event_loop().run_until_complete(_run())


def _row_bundle(database: Database, rating_version_id: UUID) -> dict | None:
    async def _run() -> dict | None:
        async with database.session() as session:
            row = await session.get(RatingVersionRow, rating_version_id)
        assert row is not None
        return None if row.bundle is None else dict(row.bundle)

    return asyncio.get_event_loop().run_until_complete(_run())


def _compile_jobs(database: Database, workspace_id: UUID, rating_version_id: UUID) -> list[JobRow]:
    async def _run() -> list[JobRow]:
        async with database.session() as session:
            rows = (
                await session.execute(
                    select(JobRow).where(
                        JobRow.workspace_id == workspace_id, JobRow.kind == "rating.compile"
                    )
                )
            ).scalars()
            return [
                r for r in rows if r.parameters.get("rating_version_id") == str(rating_version_id)
            ]

    return asyncio.get_event_loop().run_until_complete(_run())


@pytest.fixture
def compiled_version(api_client, workspace_id, principal, grant, database, blob_store):
    """A draft that has compiled once, so `row.bundle` holds `content_hash` and `blob_sha256`."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    created = api_client.post(
        "/api/v1/rating-algorithms", json=_minimal_algorithm(), headers=headers
    )
    assert created.status_code == 201, created.text
    rating_version_id = _version_with_bundle(database, workspace_id, principal.id)
    job = _run_compile_job(api_client, headers, database, blob_store, rating_version_id)
    assert job.status is JobStatus.SUCCEEDED, job.error
    bundle = _row_bundle(database, rating_version_id)
    assert bundle is not None
    assert bundle["content_hash"]
    assert bundle["blob_sha256"]
    return rating_version_id


_NON_DRAFT = ["review", "approved", "live", "retired", "approved+deployment"]


@pytest.mark.req("FR-239")
@pytest.mark.parametrize("status", _NON_DRAFT)
def test_c1_the_route_refuses_to_compile_a_version_that_has_left_draft(
    status, api_client, workspace_id, principal, grant, database, compiled_version
) -> None:
    """RL-1379 C1. Predicted red: 202 and a `rating.compile` Job, where 409 is ruled."""
    headers = _headers(principal, workspace_id)
    jobs_before = len(_compile_jobs(database, workspace_id, compiled_version))
    events_before = len(_compile_audit_events(database, workspace_id))
    _set_status(database, compiled_version, status.split("+")[0])
    if status == "approved+deployment":
        asyncio.get_event_loop().run_until_complete(grant("deployer"))
        slug = asyncio.get_event_loop().run_until_complete(_slug_of(database, compiled_version))
        deployed = api_client.post(
            "/api/v1/environments/dev/deployments",
            json={"rating_version_ref": f"rating_version:{slug}@1", "reason": "release"},
            headers=headers,
        )
        assert deployed.status_code == 201, deployed.text
    bundle_before = _row_bundle(database, compiled_version)

    response = api_client.post(
        f"/api/v1/rating-versions/{compiled_version}/compile", headers=headers
    )

    assert response.status_code == 409, response.text
    assert response.json()["code"] == "RATING_VERSION_IMMUTABLE"
    assert len(_compile_jobs(database, workspace_id, compiled_version)) == jobs_before
    assert _row_bundle(database, compiled_version) == bundle_before
    assert len(_compile_audit_events(database, workspace_id)) == events_before


async def _slug_of(database: Database, rating_version_id: UUID) -> str:
    async with database.session() as session:
        row = await session.get(RatingVersionRow, rating_version_id)
    assert row is not None
    return row.slug


@pytest.mark.req("FR-239")
def test_c2_the_service_refuses_a_status_that_changed_after_submission(
    api_client, workspace_id, principal, database, blob_store, compiled_version
) -> None:
    """RL-1379 C2. Predicted red: the Job succeeds and rewrites `bundle`."""
    headers = _headers(principal, workspace_id)
    bundle_before = _row_bundle(database, compiled_version)
    events_before = len(_compile_audit_events(database, workspace_id))
    submitted = api_client.post(
        f"/api/v1/rating-versions/{compiled_version}/compile", headers=headers
    )
    assert submitted.status_code == 202, submitted.text
    job_id = UUID(submitted.json()["id"])
    _set_status(database, compiled_version, "approved")

    async def _run() -> JobRow:
        await execute_job(database, job_id, blob_store)
        async with database.session() as session:
            row = await session.get(JobRow, job_id)
        assert row is not None
        return row

    job = asyncio.get_event_loop().run_until_complete(_run())

    assert job.status is JobStatus.FAILED
    assert job.error["code"] == "RATING_VERSION_IMMUTABLE"
    assert job.error["retryable"] is False
    assert _row_bundle(database, compiled_version) == bundle_before
    assert len(_compile_audit_events(database, workspace_id)) == events_before


@pytest.mark.req("FR-239")
def test_c3_control_a_draft_version_still_compiles_twice(
    api_client, workspace_id, principal, database, blob_store, compiled_version
) -> None:
    """RL-1379 C3: green before and after; the guard does not over-refuse a draft."""
    headers = _headers(principal, workspace_id)
    second = _run_compile_job(api_client, headers, database, blob_store, compiled_version)
    assert second.status is JobStatus.SUCCEEDED, second.error


@pytest.mark.req("FR-239")
def test_c4_control_a_version_returned_to_draft_compiles_again(
    api_client, workspace_id, principal, database, blob_store, compiled_version
) -> None:
    """RL-1379 C4: review → draft (what a `changes_requested` decision does, `_target_status`)
    → compile returns 202. Green after the change; shows the recourse in `03` FR-239's text."""
    headers = _headers(principal, workspace_id)
    _set_status(database, compiled_version, "review")
    assert (
        api_client.post(
            f"/api/v1/rating-versions/{compiled_version}/compile", headers=headers
        ).status_code
        == 409
    )
    _set_status(database, compiled_version, "draft")
    job = _run_compile_job(api_client, headers, database, blob_store, compiled_version)
    assert job.status is JobStatus.SUCCEEDED, job.error


# --- WK-1250 Slice 2 (SL-1340): the compile resolver reads a pinned Sub-graph Version -----------
# (FR-217; RL-1309 G1, G2, G4 (c))


@pytest.mark.req("FR-20")
@pytest.mark.req("FR-217")
def test_sub_graph_version_row_has_no_status_column() -> None:
    """G4 (c), the tripwire for `RL-1309` DP-1 item 5's `sub_graph` maturity exemption.

    A Sub-graph Version has no approval lifecycle, so `compile.py`'s `_MATURITY_CHECK_EXEMPT`
    admits the pin and the resolver reports the `"no_maturity_concept"` sentinel rather than an
    invented `"approved"`. That is sound only while the premise holds: the day a migration adds
    a `status` column to `sub_graph_versions`, this fails and names `RL-1309`, and the
    exemption must be revisited rather than carried forward silently.
    """
    assert "status" not in SubGraphVersionRow.__table__.columns, (
        "SubGraphVersionRow gained a status column: RL-1309 DP-1 item 5's sub_graph maturity "
        "exemption must be revisited; the resolver should report this real status instead of "
        "staying exempt from the FR-20 floor."
    )


#: Every place in `backend/src` that writes or forwards a Rating Version's `pins`, by the
#: predicate `RL-1309` G2 names (`git grep -nE '\.pins\s*=[^=]|pins=' -- backend/src`), counted
#: per file at the tree of SL-1340. `create_rating_version` is the only writer, and it inserts a
#: new `draft` row: there is no path that reaches an existing row, so none needs a refusal.
_PIN_WRITE_SITES = {
    "app/api/models.py": 1,  # the create route forwards `body.pins` to the service
    # `to_schema` reads `row.pins`; `create_rating_version` writes it (a new draft row)
    "app/platform/rating_versions.py": 2,
}


@pytest.mark.req("FR-237")
@pytest.mark.req("FR-217")
def test_g2_every_pin_write_path_is_enumerated() -> None:
    """RL-1309 G2: a pin write path that can reach an existing row must refuse a pin change
    unless the row is `draft`. At this tree there is exactly one writer and it creates a row. A
    new writer fails this test until it is enumerated here AND given the refusal."""
    src = Path(__file__).resolve().parents[1] / "src"
    pattern = re.compile(r"\.pins\s*=[^=]|pins=")
    found = {
        str(path.relative_to(src)): len(pattern.findall(path.read_text(encoding="utf-8")))
        for path in sorted(src.rglob("*.py"))
        if pattern.search(path.read_text(encoding="utf-8"))
    }
    assert found == _PIN_WRITE_SITES


def _ncd_sub_graph() -> dict:
    return {
        "slug": "ncd-ladder",
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_ladder", "type": "expression", "label": "Ladder",
             "expr": "ncd_years * 10", "result_type": "decimal",
             "consumes": ["ncd_years"], "produces": "ncd_factor"},
        ],
        "change_note": "first cut",
    }


def _mounting_algorithm() -> dict:
    return {
        "slug": "mounting",
        "version": 1,
        "input_contract": [
            {"name": "premium_in", "type": "int", "nullable": False},
            {"name": "ncd_years", "type": "int", "nullable": False},
        ],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": "premium_in",
             "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_in_ncd", "type": "input", "label": "NCD", "input_name": "ncd_years",
             "on_missing": "error", "produces": "ncd_years"},
            {"step_id": "s_expr", "type": "expression", "label": "Apply",
             "expr": "premium_in * ncd_factor", "result_type": "money_minor",
             "consumes": ["premium_in", "ncd_factor"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [{"ref": "sub_graph:ncd-ladder@1", "mount_point": "m_ncd",
                        "inputs": {"ncd_years": "ncd_years"},
                        "outputs": {"ncd_factor": "ncd_factor"}}],
    }


def _mount_a_stored_sub_graph(
    api_client, workspace_id, principal, grant, database, *, pinned: bool
) -> UUID:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    made = api_client.post("/api/v1/sub-graphs", json=_ncd_sub_graph(), headers=headers)
    assert made.status_code == 201, made.text
    algorithm = api_client.post(
        "/api/v1/rating-algorithms", json=_mounting_algorithm(), headers=headers
    )
    assert algorithm.status_code == 201, algorithm.text
    pins = _empty_pins() | ({"sub_graphs": ["sub_graph:ncd-ladder@1"]} if pinned else {})
    row = asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database, workspace_id, principal.id,
            algorithm_ref="rating_algorithm:mounting@1", pins=pins,
        )
    )
    return row.id


@pytest.mark.req("FR-217")
def test_a_version_mounting_a_stored_sub_graph_compiles_over_http(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    """Acceptance 11: 202, and the `rating.compile` Job succeeds with the fragment inlined."""
    version_id = _mount_a_stored_sub_graph(
        api_client, workspace_id, principal, grant, database, pinned=True
    )
    headers = _headers(principal, workspace_id)
    job_row = _run_compile_job(api_client, headers, database, blob_store, version_id)
    assert job_row.status is JobStatus.SUCCEEDED, job_row.error
    bundle = Bundle.model_validate_json(_read_blob(database, blob_store, job_row.result["ref"]))
    assert "m_ncd__s_ladder" in bundle.graph.nodes
    assert "sub_graph:ncd-ladder@1" in bundle.resolved_payloads


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-237")
def test_a_mount_whose_sub_graph_is_not_pinned_fails_the_compile_job(
    api_client, workspace_id, principal, grant, database, blob_store
) -> None:
    version_id = _mount_a_stored_sub_graph(
        api_client, workspace_id, principal, grant, database, pinned=False
    )
    headers = _headers(principal, workspace_id)
    job_row = _run_compile_job(api_client, headers, database, blob_store, version_id)
    assert job_row.status is JobStatus.FAILED
    assert job_row.error["code"] == "RATING_VERSION_UNPINNED"
