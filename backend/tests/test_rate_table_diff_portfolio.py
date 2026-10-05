"""FR-231's exposure weight through the platform (`RL-1361` items 5 to 8, `RL-1418`).

The pure join is `packages/pricing-core/tests/test_rate_table_weights.py`'s. This file owns what
only the platform can be wrong about: which portfolio a caller may name (scope, status, in what
order), how each key's pinned artifact is loaded, what the cache key covers, and that every
refusal precedes the cache read and any Job. Expected figures are hand-worked literals.

The fixture portfolio has four rows:

| quote | exposure | driver_age_band | age | region |
|---|---|---|---|---|
| q1 | 1.0 | 17-20 | 18 | N1 |
| q2 | 2.0 | 21-24 | 22 | N2 |
| q3 | 4.0 | 25-29 | 27 | S1 |
| q4 | 0.5 | 17-20 | 19 | S1 |

so by band `17-20` weighs 1.5, `21-24` weighs 2 and `25-29` weighs 4; by group NORTH weighs 3 and
SOUTH 4.5.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_data_jobs import _validate
from backend.tests.test_model_jobs import _actuary, _dataset
from backend.tests.test_rate_tables_service import (
    _fit_result,
    _glm_spec,
    _seed_approved_model,
    _set_threshold,
)
from fastapi.testclient import TestClient
from sqlalchemy import func, select, update

from app.config import Settings
from app.db.models import (
    BlobRow,
    JobRow,
    RateTableRow,
    RateTableVersionRow,
    RoleAssignmentRow,
    RoleRow,
    WorkspaceMemberRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import datasets as dataset_service
from app.platform import jobs as job_service
from app.platform import modelling as model_service
from app.platform import rate_tables as svc
from app.platform import transformations as transformation_service
from app.platform import validation as validation_service
from app.platform.blobs import BlobStore
from app.platform.diff_cache import DiffCache, definition_hash, version_content_hash
from app.worker.tasks import execute_job
from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorType,
    Grouping,
    GroupingMethod,
    JobKind,
    JobStatus,
    UnseenLevelBehaviour,
    new_uuid7,
)
from model_schema.rating import RateTable, RateTableDiff
from model_schema.refs import ArtifactRef

D = Decimal

PORTFOLIO = (
    b"policy_id,quote_id,exposure_years,driver_age_band,age,region\n"
    b"P1,q1,1.0,17-20,18,N1\n"
    b"P2,q2,2.0,21-24,22,N2\n"
    b"P3,q3,4.0,25-29,27,S1\n"
    b"P4,q4,0.5,17-20,19,S1\n"
)

_RECIPE = [
    {
        "step": "cast",
        "table": "policy_exposure",
        "params": {"columns": {"exposure_years": "float", "age": "int"}},
    }
]


@pytest.fixture(autouse=True)
def _handlers() -> None:
    from app.worker.rate_table_handlers import register_rate_table_handlers

    register_rate_table_handlers()


class _FakeClient:
    """A dict-backed Redis stand-in that records its reads and writes."""

    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}
        self.gets = 0
        self.sets = 0

    async def get(self, key: str) -> bytes | None:
        self.gets += 1
        return self.store.get(key)

    async def set(self, key: str, value: bytes) -> None:
        self.sets += 1
        self.store[key] = value


class _AnyKeyClient(_FakeClient):
    """Serves the same stored diff for every key: a request that reads the cache before it
    checks the portfolio is handed this entry, which is what a warm cache would do."""

    def __init__(self, stored: RateTableDiff) -> None:
        super().__init__()
        self._stored = stored.model_dump_json().encode()

    async def get(self, key: str) -> bytes | None:
        self.gets += 1
        return self._stored


async def ingest_portfolio(
    database: Database, blob_store: BlobStore, workspace_id: UUID, actor: Any,
    dataset_id: UUID, payload: bytes = PORTFOLIO,
) -> UUID:
    """Upload a portfolio and run its ingest Job; the version is `draft`."""
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, payload, "text/csv")
        job = await job_service.submit(
            session,
            JobKind.DATASET_INGEST,
            {
                "workspace_id": str(workspace_id),
                "actor": actor.model_dump(mode="json"),
                "dataset_id": str(dataset_id),
                "blob": ref.sha256,
                "filename": "portfolio.csv",
                "recipe": _RECIPE,
            },
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    from app.db.models import DatasetVersionRow

    async with database.session() as session:
        return (
            await session.execute(
                select(DatasetVersionRow.id)
                .where(DatasetVersionRow.dataset_id == dataset_id)
                .order_by(DatasetVersionRow.version.desc())
                .limit(1)
            )
        ).scalar_one()


async def validated_portfolio(
    database: Database, blob_store: BlobStore, workspace_id: UUID, actor: Any,
    payload: bytes = PORTFOLIO,
) -> UUID:
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await ingest_portfolio(
        database, blob_store, workspace_id, actor, dataset_id, payload
    )
    report_id = await _validate(database, blob_store, workspace_id, actor, version_id)
    async with database.unit_of_work() as session:
        await validation_service.promote_using_report(
            session, workspace_id=workspace_id, actor=actor,
            version_id=version_id, report_id=report_id,
        )
    return version_id


_AGE_LEVELS = [("17-20", 1.92), ("21-24", 1.41), ("25-29", 1.12)]
_REGION_LEVELS = [("NORTH", 1.5), ("SOUTH", 1.0)]


async def _seed_two_versions(
    database: Database, workspace_id: UUID, principal: Any, blob_store: BlobStore,
    *, factor: str, family: str, v2: bytes,
) -> str:
    """Seed one Factor of the family's model into a table, then import a changed v2."""
    slug = f"tbl-{uuid4().hex[:8]}"
    await svc.seed_from_model(
        database, workspace_id, principal.id, Settings(), blob_store, slug=slug,
        model_ref=ArtifactRef(type="model", slug=family, version=1),
        factor=factor, change_note="seed",
    )
    await svc.import_confirmed(
        database, workspace_id, principal.id, Settings(), blob_store, slug=slug,
        version=1, filename="v2.csv", content=v2,
    )
    return slug


async def _approved_model(
    database: Database, workspace_id: UUID, family: str,
    pins: dict[str, UUID], relativities: dict[str, list[tuple[str, float]]],
) -> None:
    from backend.tests.approved_rows import add_approved

    from app.db.models import ModelRow
    from model_schema import ModelStatus

    async with database.unit_of_work() as session:
        spec = _glm_spec(family, new_uuid7())
        spec["factors"] = [str(factor_id) for factor_id in pins.values()]
        await add_approved(
            session,
            ModelRow(
                workspace_id=workspace_id, model_family_slug=family, version=1,
                status=ModelStatus.APPROVED.value, dataset_version_id=new_uuid7(),
                spec=spec, spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}",
                fit_result=_fit_result(relativities), diagnostics_id=uuid4(),
            ),
        )


async def _identity_table(
    database: Database, workspace_id: UUID, principal: Any, blob_store: BlobStore,
) -> str:
    """A seeded `driver_age_band` table: v1 relativities 1.92/1.41/1.12; v2 moves 17-20 by
    +10% (1.92 -> 2.112) and 21-24 by -10% (1.41 -> 1.269), leaving 25-29 alone."""
    family = f"mf-{uuid4().hex[:8]}"
    await _seed_approved_model(database, workspace_id, family, {"driver_age_band": _AGE_LEVELS})
    return await _seed_two_versions(
        database, workspace_id, principal, blob_store, factor="driver_age_band", family=family,
        v2=b"driver_age_band,relativity\n17-20,2.1120\n21-24,1.2690\n25-29,1.1200\n",
    )


async def _diff(database: Database, workspace_id: UUID, blob_store: BlobStore, slug: str,
                portfolio: UUID | None, cache: DiffCache | None = None,
                against: Any = "previous") -> RateTableDiff:
    return await svc.diff(
        database, workspace_id, slug, 2, against, blob_store=blob_store, cache=cache,
        portfolio_dataset_version_id=portfolio,
    )


@pytest.mark.req("FR-231")
async def test_an_unweighted_diff_says_so(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    diff = await _diff(database, workspace_id, blob_store, slug, None)
    assert diff.changed_cells == 2
    assert diff.exposure_weighted_mean_change_pct is None
    assert diff.portfolio_exposure is None
    assert diff.matched_exposure is None


@pytest.mark.req("FR-231")
async def test_a_weighted_diff_matches_the_hand_computed_figures(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """17-20 (+10%, weight 1.5) and 21-24 (-10%, weight 2): (1.5*10 + 2*-10) / 3.5."""
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    diff = await _diff(database, workspace_id, blob_store, slug, portfolio)
    assert diff.changed_cells == 2
    assert diff.max_abs_change_pct == D("10")
    assert diff.exposure_weighted_mean_change_pct is not None
    assert diff.exposure_weighted_mean_change_pct.quantize(D("0.000001")) == D("-1.428571")
    assert diff.portfolio_exposure == D("7.5")
    assert diff.matched_exposure == D("7.5")


async def _banding_factor(database, workspace_id, actor) -> tuple[UUID, UUID]:
    dataset_id = new_uuid7()
    banding = Banding(
        id=uuid4(), slug=f"age-{uuid4().hex[:6]}", dataset_id=dataset_id, version=1,
        column="age", method=BandingMethod.MANUAL,
        boundaries=(17.0, 21.0, 25.0, 30.0), labels=("17-20", "21-24", "25-29"),
    )
    async with database.unit_of_work() as session:
        await transformation_service.create_banding(
            session, workspace_id=workspace_id, actor=actor, banding=banding
        )
        stored = (await transformation_service.list_bandings(
            session, workspace_id=workspace_id, dataset_id=dataset_id))[0]
        factor = await model_service.create_factor(
            session, workspace_id=workspace_id, actor=actor,
            factor=Factor(
                id=uuid4(), slug="age_banded", dataset_id=dataset_id, version=1,
                type=FactorType.BANDING, source_columns=("age",), banding_id=stored.id,
            ),
        )
        return factor.id, stored.id


async def _grouping_factor(database, workspace_id, actor) -> UUID:
    dataset_id = new_uuid7()
    grouping = Grouping(
        id=uuid4(), slug=f"region-{uuid4().hex[:6]}", dataset_id=dataset_id, version=1,
        column="region", method=GroupingMethod.MANUAL,
        mapping={"N1": "NORTH", "N2": "NORTH", "S1": "SOUTH"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
    )
    async with database.unit_of_work() as session:
        await transformation_service.create_grouping(
            session, workspace_id=workspace_id, actor=actor, grouping=grouping
        )
        stored = (await transformation_service.list_groupings(
            session, workspace_id=workspace_id, dataset_id=dataset_id))[0]
        factor = await model_service.create_factor(
            session, workspace_id=workspace_id, actor=actor,
            factor=Factor(
                id=uuid4(), slug="region_grp", dataset_id=dataset_id, version=1,
                type=FactorType.GROUPING, source_columns=("region",), grouping_id=stored.id,
            ),
        )
        return factor.id


@pytest.mark.req("FR-231")
async def test_seeded_banding_and_grouping_tables_are_weighted(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    age_factor, _ = await _banding_factor(database, workspace_id, actor)
    region_factor = await _grouping_factor(database, workspace_id, actor)
    family = f"mf-{uuid4().hex[:8]}"
    await _approved_model(
        database, workspace_id, family,
        {"age_banded": age_factor, "region_grp": region_factor},
        {"age_banded": _AGE_LEVELS, "region_grp": _REGION_LEVELS},
    )
    age_table = await _seed_two_versions(
        database, workspace_id, principal, blob_store, factor="age_banded", family=family,
        v2=b"age_banded,relativity\n17-20,2.1120\n21-24,1.2690\n25-29,1.1200\n",
    )
    region_table = await _seed_two_versions(
        database, workspace_id, principal, blob_store, factor="region_grp", family=family,
        v2=b"region_grp,relativity\nNORTH,1.6500\nSOUTH,0.9000\n",
    )

    banded = await _diff(database, workspace_id, blob_store, age_table, portfolio)
    assert banded.exposure_weighted_mean_change_pct is not None
    assert banded.exposure_weighted_mean_change_pct.quantize(D("0.000001")) == D("-1.428571")
    assert banded.matched_exposure == D("7.5")

    grouped = await _diff(database, workspace_id, blob_store, region_table, portfolio)
    # NORTH +10% weight 3, SOUTH -10% weight 4.5: (30 - 45) / 7.5.
    assert grouped.exposure_weighted_mean_change_pct == D("-2")
    assert grouped.matched_exposure == D("7.5")

    # Strip `factor_ref` from the stored definitions: the key is then joined by its own name,
    # `age_banded`, which the portfolio has no column of.
    async with database.unit_of_work() as session:
        row = await session.scalar(
            select(RateTableRow).where(
                RateTableRow.workspace_id == workspace_id, RateTableRow.slug == age_table
            )
        )
        assert row is not None
        for version in (
            await session.execute(
                select(RateTableVersionRow).where(RateTableVersionRow.rate_table_id == row.id)
            )
        ).scalars():
            definition = json.loads(json.dumps(version.definition))
            for key in definition["keys"]:
                key.pop("factor_ref", None)
            await session.execute(
                update(RateTableVersionRow)
                .where(RateTableVersionRow.id == version.id)
                .values(definition=definition)
            )
    with pytest.raises(PlatformError) as refused:
        await _diff(database, workspace_id, blob_store, age_table, portfolio)
    assert refused.value.status_code == 422
    assert refused.value.code == "VALIDATION_FAILED"
    assert "age_banded" in (refused.value.detail or "")


@pytest.mark.req("FR-231")
async def test_the_frame_passes_through_undeclared_columns(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """`age` and `region` are in no schema §4.8 declares, and a Factor still resolves them."""
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    age_factor, _ = await _banding_factor(database, workspace_id, actor)
    family = f"mf-{uuid4().hex[:8]}"
    await _approved_model(
        database, workspace_id, family, {"age_banded": age_factor}, {"age_banded": _AGE_LEVELS}
    )
    table = await _seed_two_versions(
        database, workspace_id, principal, blob_store, factor="age_banded", family=family,
        v2=b"age_banded,relativity\n17-20,2.1120\n21-24,1.2690\n25-29,1.1200\n",
    )
    diff = await _diff(database, workspace_id, blob_store, table, portfolio)
    assert diff.matched_exposure == D("7.5")


@pytest.mark.req("FR-231")
async def test_a_portfolio_must_be_validated(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    actor = await _actuary(database, workspace_id)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    draft_dataset = await _dataset(database, blob_store, workspace_id, actor)
    draft = await ingest_portfolio(database, blob_store, workspace_id, actor, draft_dataset)
    with pytest.raises(PlatformError) as refused:
        await _diff(database, workspace_id, blob_store, slug, draft)
    assert (refused.value.code, refused.value.status_code) == ("DATASET_NOT_VALIDATED", 409)
    assert "diff" in (refused.value.detail or "")

    archived = await validated_portfolio(database, blob_store, workspace_id, actor)
    async with database.unit_of_work() as session:
        await dataset_service.archive_version(
            session, workspace_id=workspace_id, actor=actor, version_id=archived,
            reason="superseded",
        )
    with pytest.raises(PlatformError) as refused:
        await _diff(database, workspace_id, blob_store, slug, archived)
    assert (refused.value.code, refused.value.status_code) == ("DATASET_NOT_VALIDATED", 409)

    validated = await validated_portfolio(database, blob_store, workspace_id, actor)
    assert (await _diff(database, workspace_id, blob_store, slug, validated)).changed_cells == 2


@pytest.mark.req("FR-231")
async def test_a_foreign_portfolio_is_404_on_a_warm_cache(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """Another workspace's portfolio answers as a nonexistent id does, and the checks run
    before the cache read: a cache that would serve any key is never asked."""
    other = uuid4()
    other_actor = await _actuary(database, other)
    foreign = await validated_portfolio(database, blob_store, other, other_actor)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    warm = _AnyKeyClient(
        RateTableDiff(changed_cells=2, portfolio_exposure=D("1"), matched_exposure=D("1"))
    )
    cache = DiffCache(warm)
    missing = uuid4()
    bodies = []
    for ref in (foreign, missing):
        with pytest.raises(PlatformError) as refused:
            await _diff(database, workspace_id, blob_store, slug, ref, cache=cache)
        assert (refused.value.code, refused.value.status_code) == ("NOT_FOUND", 404)
        bodies.append((refused.value.title, (refused.value.detail or "").replace(str(ref), "<id>")))
    assert bodies[0] == bodies[1]
    assert warm.gets == 0


@pytest.mark.req("FR-231")
@pytest.mark.parametrize("kind", ["factor_ref", "banding_ref"])
async def test_a_dangling_ref_is_404_naming_key_and_ref(
    database: Database, workspace_id, principal, blob_store: BlobStore, kind: str
) -> None:
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    dangling = "factor:nowhere@7" if kind == "factor_ref" else "banding:nowhere@7"
    async with database.unit_of_work() as session:
        row = await session.scalar(
            select(RateTableRow).where(
                RateTableRow.workspace_id == workspace_id, RateTableRow.slug == slug
            )
        )
        assert row is not None
        for version in (
            await session.execute(
                select(RateTableVersionRow).where(RateTableVersionRow.rate_table_id == row.id)
            )
        ).scalars():
            definition = json.loads(json.dumps(version.definition))
            for key in definition["keys"]:
                key.pop("factor_ref", None)
                key[kind] = dangling
            await session.execute(
                update(RateTableVersionRow)
                .where(RateTableVersionRow.id == version.id)
                .values(definition=definition)
            )
    with pytest.raises(PlatformError) as refused:
        await _diff(database, workspace_id, blob_store, slug, portfolio)
    assert (refused.value.code, refused.value.status_code) == ("NOT_FOUND", 404)
    assert "driver_age_band" in (refused.value.detail or "")
    assert dangling in (refused.value.detail or "")


@pytest.mark.req("FR-231")
async def test_null_and_negative_exposure_are_422_naming_the_column(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """`read_portfolio` refuses them (P3); the test pins that they reach the caller as a 422."""
    actor = await _actuary(database, workspace_id)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    negative = PORTFOLIO.replace(b"P2,q2,2.0,", b"P2,q2,-2.0,")
    # The exposure rule refuses a non-positive row at validation, so the version is made
    # valid first and then replaced under the same id would be a different test; here the
    # version is ingested and its status forced, which is all `check_portfolio` reads.
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await ingest_portfolio(
        database, blob_store, workspace_id, actor, dataset_id, negative
    )
    from app.db.models import DatasetVersionRow

    async with database.unit_of_work() as session:
        await session.execute(
            update(DatasetVersionRow)
            .where(DatasetVersionRow.id == version_id)
            .values(status="validated", validation_report_id=uuid4())
        )
    with pytest.raises(PlatformError) as refused:
        await _diff(database, workspace_id, blob_store, slug, version_id)
    assert (refused.value.code, refused.value.status_code) == ("VALIDATION_FAILED", 422)
    assert "exposure_years" in (refused.value.detail or "")
    assert "negative" in (refused.value.detail or "")


# --- the cache key (Acceptance 16) --------------------------------------------------------


@pytest.mark.req("FR-231")
def test_two_portfolios_are_two_entries() -> None:
    cache = DiffCache(_FakeClient())
    ws = uuid4()
    assert cache.key("c", "b", "d", uuid4(), ws) != cache.key("c", "b", "d", uuid4(), ws)


@pytest.mark.req("FR-231")
def test_two_workspaces_are_two_entries_with_a_portfolio() -> None:
    cache = DiffCache(_FakeClient())
    portfolio = uuid4()
    first, second = uuid4(), uuid4()
    assert cache.key("c", "b", "d", portfolio, first) != cache.key("c", "b", "d", portfolio, second)
    # Without a portfolio the figure is workspace-independent, and the key says so.
    assert cache.key("c", "b", "d", None, uuid4()) == cache.key("c", "b", "d", None, uuid4())


def _table(**key_over: Any) -> RateTable:
    key = {"name": "band", "type": "string", **key_over}
    return RateTable.model_validate(
        {
            "slug": "tbl-x", "version": 1, "rateable": True, "storage": "rows", "keys": [key],
            "value": {"name": "relativity", "type": "relativity", "unit": "x"},
        }
    )


@pytest.mark.req("FR-231")
@pytest.mark.parametrize(
    "change",
    [{"name": "other"}, {"type": "int"}, {"banding_ref": "banding:bb@1"},
     {"factor_ref": "factor:ff@1"}],
    ids=["key-role", "key-type", "banding_ref", "factor_ref"],
)
@pytest.mark.parametrize("with_portfolio", [False, True])
def test_a_definition_change_is_a_new_entry(change: dict[str, str], with_portfolio: bool) -> None:
    cache = DiffCache(_FakeClient())
    portfolio = uuid4() if with_portfolio else None
    ws = uuid4()
    before = cache.key("c", "b", definition_hash(_table()), portfolio, ws)
    after = cache.key("c", "b", definition_hash(_table(**change)), portfolio, ws)
    assert before != after
    assert version_content_hash([{"band": "a", "relativity": "1"}])  # the key's other half


@pytest.mark.req("FR-231")
async def test_two_portfolios_are_two_cached_figures(
    database: Database, workspace_id, principal, blob_store: BlobStore
) -> None:
    """The second portfolio is not served the first one's figure."""
    actor = await _actuary(database, workspace_id)
    full = await validated_portfolio(database, blob_store, workspace_id, actor)
    half = await validated_portfolio(
        database, blob_store, workspace_id, actor,
        PORTFOLIO.replace(b"P2,q2,2.0,", b"P2,q2,0.5,"),
    )
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    client = _FakeClient()
    cache = DiffCache(client)
    first = await _diff(database, workspace_id, blob_store, slug, full, cache=cache)
    second = await _diff(database, workspace_id, blob_store, slug, half, cache=cache)
    assert client.sets == 2
    assert first.portfolio_exposure == D("7.5")
    assert second.portfolio_exposure == D("6.0")
    assert second.exposure_weighted_mean_change_pct != first.exposure_weighted_mean_change_pct


# --- the route, the Job and the worker (Acceptance 10 and 17) -------------------------------


async def _rating_only_caller(database: Database, workspace_id: UUID) -> dict[str, str]:
    """A caller with `rating:read` and nothing else: no built-in role is that narrow, so a
    custom role is stored for it."""
    from model_schema import ScopeType

    caller = uuid4()
    async with database.unit_of_work() as session:
        role = RoleRow(
            workspace_id=workspace_id, slug=f"rating-only-{uuid4().hex[:6]}",
            description="rating:read only", permissions=["rating:read"], builtin=False,
        )
        session.add(role)
        await session.flush()
        session.add(
            RoleAssignmentRow(
                workspace_id=workspace_id, principal_kind="user", principal_id=caller,
                role_id=role.id, scope_type=ScopeType.WORKSPACE.value,
            )
        )
        session.add(WorkspaceMemberRow(user_id=caller, workspace_id=workspace_id))
    return _headers(caller, workspace_id)


async def _job_count(database: Database) -> int:
    async with database.session() as session:
        return (await session.execute(select(func.count()).select_from(JobRow))).scalar_one()


@pytest.mark.req("FR-231")
async def test_portfolio_needs_dataset_read_and_hides_existence(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    rating_only = await _rating_only_caller(database, workspace_id)
    url = f"/api/v1/rate-tables/{slug}@2/diff"

    # Without `portfolio` the narrow caller succeeds: `dataset:read` is not route-wide.
    plain = api_client.get(url, params={"against": "previous"}, headers=rating_only)
    assert plain.status_code == 200, plain.text
    assert plain.json()["portfolio_exposure"] is None

    # With `portfolio`, an existing id and a nonexistent one are refused identically.
    refused = [
        api_client.get(
            url, params={"against": "previous", "portfolio": str(ref)}, headers=rating_only
        )
        for ref in (portfolio, uuid4())
    ]
    assert [r.status_code for r in refused] == [403, 403]
    assert refused[0].json()["code"] == refused[1].json()["code"]
    assert refused[0].json()["detail"] == refused[1].json()["detail"]

    # A caller who holds `dataset:read` is served the weighted figure.
    analyst = _headers(principal.id, workspace_id)
    weighted = api_client.get(
        url, params={"against": "previous", "portfolio": str(portfolio)}, headers=analyst
    )
    assert weighted.status_code == 200, weighted.text
    body = weighted.json()
    assert body["changed_cells"] == 2
    assert Decimal(body["matched_exposure"]) == D("7.5")
    mean = Decimal(body["exposure_weighted_mean_change_pct"])
    assert mean.quantize(D("0.000001")) == D("-1.428571")


async def _parquet_table(
    database: Database, workspace_id: UUID, principal: Any, blob_store: BlobStore
) -> str:
    """The identity table with both versions stored as parquet (threshold 1 cell)."""
    await _set_threshold(database, workspace_id, 1)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    await _set_threshold(database, workspace_id, 250_000)
    return slug


async def _job_row(database: Database, job_id: Any) -> JobRow:
    async with database.session() as session:
        row = await session.get(JobRow, job_id)
    assert row is not None
    return row


@pytest.mark.req("FR-231")
@pytest.mark.req("FR-232")
async def test_a_refused_portfolio_creates_no_job(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    slug = await _parquet_table(database, workspace_id, principal, blob_store)
    draft_dataset = await _dataset(database, blob_store, workspace_id, actor)
    draft = await ingest_portfolio(database, blob_store, workspace_id, actor, draft_dataset)
    rating_only = await _rating_only_caller(database, workspace_id)
    analyst = _headers(principal.id, workspace_id)
    url = f"/api/v1/rate-tables/{slug}@2/diff"

    before = await _job_count(database)
    cases = [
        (rating_only, uuid4(), 403),
        (analyst, uuid4(), 404),
        (analyst, draft, 409),
    ]
    for headers, ref, status_code in cases:
        response = api_client.get(
            url, params={"against": "previous", "portfolio": str(ref)}, headers=headers
        )
        assert response.status_code == status_code, response.text
    assert await _job_count(database) == before

    # A rating-only caller without `portfolio` is accepted, and the Job exists.
    plain = api_client.get(url, params={"against": "previous"}, headers=rating_only)
    assert plain.status_code == 202, plain.text
    assert await _job_count(database) == before + 1


@pytest.mark.req("FR-231")
@pytest.mark.req("FR-232")
async def test_the_job_result_equals_the_200_figure(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    parquet = await _parquet_table(database, workspace_id, principal, blob_store)
    rows = await _identity_table(database, workspace_id, principal, blob_store)
    analyst = _headers(principal.id, workspace_id)

    accepted = api_client.get(
        f"/api/v1/rate-tables/{parquet}@2/diff",
        params={"against": "previous", "portfolio": str(portfolio)}, headers=analyst,
    )
    assert accepted.status_code == 202, accepted.text
    job = accepted.json()
    assert accepted.headers["Location"] == f"/api/v1/jobs/{job['id']}"
    assert await execute_job(database, UUID(job["id"]), blob_store) is JobStatus.SUCCEEDED
    finished = await _job_row(database, UUID(job["id"]))
    assert finished.result is not None
    from app.db.models import BlobRow
    from app.platform.blobs import to_ref

    async with database.session() as session:
        blob = await session.get(BlobRow, finished.result["ref"])
    assert blob is not None
    stored = await blob_store.read(to_ref(blob))
    from_job = RateTableDiff.model_validate_json(stored)

    twin = api_client.get(
        f"/api/v1/rate-tables/{rows}@2/diff",
        params={"against": "previous", "portfolio": str(portfolio)}, headers=analyst,
    )
    assert twin.status_code == 200, twin.text
    assert from_job == RateTableDiff.model_validate(twin.json())
    assert from_job.matched_exposure == D("7.5")


@pytest.mark.req("FR-232")
async def test_a_portfolio_archived_before_the_worker_runs_fails_the_job(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    slug = await _parquet_table(database, workspace_id, principal, blob_store)
    accepted = api_client.get(
        f"/api/v1/rate-tables/{slug}@2/diff",
        params={"against": "previous", "portfolio": str(portfolio)},
        headers=_headers(principal.id, workspace_id),
    )
    assert accepted.status_code == 202, accepted.text
    async with database.unit_of_work() as session:
        await dataset_service.archive_version(
            session, workspace_id=workspace_id, actor=actor, version_id=portfolio,
            reason="superseded",
        )
    job_id = UUID(accepted.json()["id"])
    assert await execute_job(database, job_id, blob_store) is JobStatus.FAILED
    row = await _job_row(database, job_id)
    assert row.error is not None
    assert row.error["code"] == "DATASET_NOT_VALIDATED"


@pytest.mark.req("FR-232")
async def test_a_dangling_ref_fails_the_job_with_not_found(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    slug = await _parquet_table(database, workspace_id, principal, blob_store)
    async with database.unit_of_work() as session:
        row = await session.scalar(
            select(RateTableRow).where(
                RateTableRow.workspace_id == workspace_id, RateTableRow.slug == slug
            )
        )
        assert row is not None
        for version in (
            await session.execute(
                select(RateTableVersionRow).where(RateTableVersionRow.rate_table_id == row.id)
            )
        ).scalars():
            definition = json.loads(json.dumps(version.definition))
            for key in definition["keys"]:
                key["factor_ref"] = "factor:nowhere@7"
            await session.execute(
                update(RateTableVersionRow)
                .where(RateTableVersionRow.id == version.id)
                .values(definition=definition)
            )
    accepted = api_client.get(
        f"/api/v1/rate-tables/{slug}@2/diff",
        params={"against": "previous", "portfolio": str(portfolio)},
        headers=_headers(principal.id, workspace_id),
    )
    assert accepted.status_code == 202, accepted.text
    job_id = UUID(accepted.json()["id"])
    assert await execute_job(database, job_id, blob_store) is JobStatus.FAILED
    row_job = await _job_row(database, job_id)
    assert row_job.error is not None
    assert row_job.error["code"] == "NOT_FOUND"
    assert "driver_age_band" in row_job.error["message"]


# --- the paged cells route (RL-1418 T1, T2; Acceptance 18) -----------------------------------


def _cells_url(slug: str, version: int = 2) -> str:
    return f"/api/v1/rate-tables/{slug}@{version}/diff/cells"


async def _uplifted_table(
    database: Database, workspace_id: UUID, principal: Any, blob_store: BlobStore,
    levels: list[str],
) -> str:
    """A seeded `driver_age_band` table of these levels (relativity 1.0 each), then a v2 that
    uplifts every cell by 10%: every cell is a changed cell, the commonest bulk operation."""
    family = f"mf-{uuid4().hex[:8]}"
    await _seed_approved_model(
        database, workspace_id, family, {"driver_age_band": [(lv, 1.0) for lv in levels]}
    )
    slug = f"tbl-{uuid4().hex[:8]}"
    await svc.seed_from_model(
        database, workspace_id, principal.id, Settings(), blob_store, slug=slug,
        model_ref=ArtifactRef(type="model", slug=family, version=1),
        factor="driver_age_band", change_note="seed",
    )
    await svc.bulk_operation(
        database, workspace_id, principal.id, Settings(), blob_store, slug=slug, version=1,
        kind="uplift_table", parameters={"percentage": "10"},
    )
    return slug


def _all_pages(
    api_client: TestClient, url: str, headers: dict[str, str], **params: str
) -> list[Any]:
    """Every item across pages at the default limit."""
    items: list[Any] = []
    cursor: str | None = None
    while True:
        query = dict(params)
        if cursor is not None:
            query["cursor"] = cursor
        response = api_client.get(url, params=query, headers=headers)
        assert response.status_code == 200, response.text
        body = response.json()
        items.extend(body["items"])
        cursor = body["next_cursor"]
        if cursor is None:
            return items


@pytest.mark.req("FR-231")
async def test_diff_cells_gives_each_cells_change_and_weight_through_the_route(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    analyst = _headers(principal.id, workspace_id)

    response = api_client.get(
        _cells_url(slug), params={"against": "previous", "portfolio": str(portfolio)},
        headers=analyst,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["next_cursor"] is None
    assert body["total_estimate"] == 2
    first, second = body["items"]
    assert first["key"] == {"driver_age_band": "17-20"}
    assert first["change"] == "changed"
    assert Decimal(first["baseline_value"]) == D("1.92")
    assert Decimal(first["current_value"]) == D("2.112")
    assert Decimal(first["abs_change"]) == D("0.192")
    assert Decimal(first["rel_change_pct"]) == D("10")
    assert Decimal(first["weight"]) == D("1.5")
    assert second["key"] == {"driver_age_band": "21-24"}
    assert Decimal(second["abs_change"]) == D("-0.141")
    assert Decimal(second["rel_change_pct"]) == D("-10")
    assert Decimal(second["weight"]) == D("2")

    # No portfolio: every weight is null.
    plain = api_client.get(_cells_url(slug), params={"against": "previous"}, headers=analyst)
    assert [item["weight"] for item in plain.json()["items"]] == [None, None]


@pytest.mark.req("FR-231")
async def test_an_uplift_of_every_cell_is_served_in_full(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    """More than `MAX_LIMIT` changed cells: the items number `changed_cells`, no key repeats."""
    from app.api.pagination import MAX_LIMIT

    await grant("analyst")
    levels = [f"L{i:03d}" for i in range(MAX_LIMIT + 50)]
    slug = await _uplifted_table(database, workspace_id, principal, blob_store, levels)
    analyst = _headers(principal.id, workspace_id)

    summary = api_client.get(
        f"/api/v1/rate-tables/{slug}@2/diff", params={"against": "previous"}, headers=analyst
    ).json()
    assert summary["changed_cells"] == MAX_LIMIT + 50
    items = _all_pages(
        api_client, _cells_url(slug), analyst, against="previous", limit=str(MAX_LIMIT)
    )
    keys = [item["key"]["driver_age_band"] for item in items]
    assert len(items) == summary["changed_cells"]
    assert len(set(keys)) == len(keys)
    assert keys == sorted(levels)


@pytest.mark.req("FR-231")
async def test_the_pages_concatenate_in_key_order(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    """Pages at `limit=1` concatenate to the full list; `"10"` sorts before `"9"`; a repeat of
    a page is the same bytes."""
    await grant("analyst")
    slug = await _uplifted_table(database, workspace_id, principal, blob_store, ["9", "10", "2"])
    analyst = _headers(principal.id, workspace_id)
    pages = _all_pages(api_client, _cells_url(slug), analyst, against="previous", limit="1")
    assert [item["key"]["driver_age_band"] for item in pages] == ["10", "2", "9"]

    first = api_client.get(
        _cells_url(slug), params={"against": "previous", "limit": "1"}, headers=analyst
    )
    cursor = first.json()["next_cursor"]
    assert cursor is not None
    again = [
        api_client.get(
            _cells_url(slug), params={"against": "previous", "limit": "1", "cursor": cursor},
            headers=analyst,
        ).content
        for _ in range(2)
    ]
    assert again[0] == again[1]


@pytest.mark.req("FR-231")
async def test_one_weights_map_feeds_summary_and_cells(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    """The summary's mean and maximum, recomputed from the cells route's items, equal the
    diff route's: both come from one weights map."""
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    analyst = _headers(principal.id, workspace_id)
    params = {"against": "previous", "portfolio": str(portfolio)}
    summary = api_client.get(
        f"/api/v1/rate-tables/{slug}@2/diff", params=params, headers=analyst
    ).json()
    items = _all_pages(api_client, _cells_url(slug), analyst, **params)

    pairs = [
        (Decimal(i["weight"]), Decimal(i["rel_change_pct"]))
        for i in items
        if i["weight"] is not None and Decimal(i["weight"]) != 0 and i["rel_change_pct"] is not None
    ]
    mean = sum((w * p for w, p in pairs), D(0)) / sum((w for w, _ in pairs), D(0))
    assert Decimal(summary["exposure_weighted_mean_change_pct"]) == mean
    assert Decimal(summary["max_abs_change_pct"]) == max(
        abs(Decimal(i["rel_change_pct"])) for i in items if i["rel_change_pct"] is not None
    )


@pytest.mark.req("FR-231")
async def test_a_resolution_error_reaches_the_422_with_its_count_and_example(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    # age 5 is below the banding's first boundary (17) and the policy is `error`.
    out_of_range = PORTFOLIO.replace(b"P1,q1,1.0,17-20,18,N1", b"P1,q1,1.0,17-20,5,N1")
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor, out_of_range)
    age_factor, _ = await _banding_factor(database, workspace_id, actor)
    family = f"mf-{uuid4().hex[:8]}"
    await _approved_model(
        database, workspace_id, family, {"age_banded": age_factor}, {"age_banded": _AGE_LEVELS}
    )
    table = await _seed_two_versions(
        database, workspace_id, principal, blob_store, factor="age_banded", family=family,
        v2=b"age_banded,relativity\n17-20,2.1120\n21-24,1.2690\n25-29,1.1200\n",
    )
    response = api_client.get(
        _cells_url(table), params={"against": "previous", "portfolio": str(portfolio)},
        headers=_headers(principal.id, workspace_id),
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"
    detail = response.json()["detail"]
    assert "1" in detail
    assert "5" in detail


@pytest.mark.req("FR-231")
async def test_a_bad_cursor_is_400_and_a_bad_limit_is_422(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    from app.api.pagination import MAX_LIMIT, encode_cursor

    await grant("analyst")
    slug = await _identity_table(database, workspace_id, principal, blob_store)
    analyst = _headers(principal.id, workspace_id)
    for cursor in ("not-a-cursor!", encode_cursor(2), encode_cursor(10_000), encode_cursor(0)):
        response = api_client.get(
            _cells_url(slug), params={"against": "previous", "cursor": cursor}, headers=analyst
        )
        assert response.status_code == 400, (cursor, response.text)
        assert response.json()["code"] == "VALIDATION_FAILED"
    too_big = api_client.get(
        _cells_url(slug), params={"against": "previous", "limit": str(MAX_LIMIT + 1)},
        headers=analyst,
    )
    assert too_big.status_code == 422
    assert too_big.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-231")
@pytest.mark.req("FR-232")
@pytest.mark.parametrize("storage", ["rows", "parquet"])
async def test_the_cells_route_refuses_before_anything_else(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient, storage: str,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    slug = (
        await _parquet_table(database, workspace_id, principal, blob_store)
        if storage == "parquet"
        else await _identity_table(database, workspace_id, principal, blob_store)
    )
    draft_dataset = await _dataset(database, blob_store, workspace_id, actor)
    draft = await ingest_portfolio(database, blob_store, workspace_id, actor, draft_dataset)
    rating_only = await _rating_only_caller(database, workspace_id)
    analyst = _headers(principal.id, workspace_id)

    before = await _job_count(database)
    for headers, params, status_code in (
        (rating_only, {"portfolio": str(uuid4())}, 403),
        (analyst, {"portfolio": str(uuid4())}, 404),
        (analyst, {"portfolio": str(draft)}, 409),
        (analyst, {"against": "9"}, 404),
    ):
        query = {"against": "previous", **params}
        response = api_client.get(_cells_url(slug), params=query, headers=headers)
        assert response.status_code == status_code, (params, response.text)
    assert await _job_count(database) == before

    plain = api_client.get(
        _cells_url(slug), params={"against": "previous"}, headers=rating_only
    )
    assert plain.status_code == (202 if storage == "parquet" else 200), plain.text


@pytest.mark.req("FR-231")
@pytest.mark.req("FR-232")
async def test_a_parquet_cells_request_runs_one_job_then_pages(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    full = await validated_portfolio(database, blob_store, workspace_id, actor)
    other = await validated_portfolio(
        database, blob_store, workspace_id, actor, PORTFOLIO.replace(b"P2,q2,2.0,", b"P2,q2,0.5,")
    )
    parquet = await _parquet_table(database, workspace_id, principal, blob_store)
    rows = await _identity_table(database, workspace_id, principal, blob_store)
    analyst = _headers(principal.id, workspace_id)
    params = {"against": "previous", "portfolio": str(full)}

    accepted = api_client.get(_cells_url(parquet), params=params, headers=analyst)
    assert accepted.status_code == 202, accepted.text
    job = accepted.json()
    assert job["kind"] == "rate_table.diff_cells"
    assert accepted.headers["Location"] == f"/api/v1/jobs/{job['id']}"
    assert await execute_job(database, UUID(job["id"]), blob_store) is JobStatus.SUCCEEDED

    paged = api_client.get(_cells_url(parquet), params=params, headers=analyst)
    assert paged.status_code == 200, paged.text
    twin = api_client.get(_cells_url(rows), params=params, headers=analyst)
    assert paged.json() == twin.json()
    assert len(paged.json()["items"]) == 2

    # Another query is never served this query's artifact: a different portfolio is a 202.
    elsewhere = api_client.get(
        _cells_url(parquet), params={**params, "portfolio": str(other)}, headers=analyst
    )
    assert elsewhere.status_code == 202, elsewhere.text

    # With the stored artifact removed the request is a 202 again, never another page.
    finished = await _job_row(database, UUID(job["id"]))
    assert finished.result is not None
    from sqlalchemy import delete

    async with database.unit_of_work() as session:
        await session.execute(delete(BlobRow).where(BlobRow.sha256 == finished.result["ref"]))
    again = api_client.get(_cells_url(parquet), params=params, headers=analyst)
    assert again.status_code == 202, again.text


@pytest.mark.req("FR-232")
async def test_a_cells_job_for_an_archived_portfolio_fails(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    await grant("analyst")
    actor = await _actuary(database, workspace_id)
    portfolio = await validated_portfolio(database, blob_store, workspace_id, actor)
    parquet = await _parquet_table(database, workspace_id, principal, blob_store)
    accepted = api_client.get(
        _cells_url(parquet), params={"against": "previous", "portfolio": str(portfolio)},
        headers=_headers(principal.id, workspace_id),
    )
    assert accepted.status_code == 202, accepted.text
    async with database.unit_of_work() as session:
        await dataset_service.archive_version(
            session, workspace_id=workspace_id, actor=actor, version_id=portfolio,
            reason="superseded",
        )
    job_id = UUID(accepted.json()["id"])
    assert await execute_job(database, job_id, blob_store) is JobStatus.FAILED
    row = await _job_row(database, job_id)
    assert row.error is not None
    assert row.error["code"] == "DATASET_NOT_VALIDATED"


@pytest.mark.req("FR-232")
async def test_a_rows_version_and_its_parquet_twin_find_the_same_cells_artifact(
    database: Database, workspace_id, principal, blob_store: BlobStore, grant,
    api_client: TestClient,
) -> None:
    """FR-232: storage never changes what a diff contains, so the cells artifact is keyed by
    the cells (`version_content_hash`), not by how a version happens to be stored. Two tables
    with the same cells and definition, one pair (rows, parquet) and one (parquet, parquet),
    share one stored artifact: the second request is a 200, not a second Job."""
    await grant("analyst")
    analyst = _headers(principal.id, workspace_id)

    async def table(v1_parquet: bool) -> str:
        await _set_threshold(database, workspace_id, 1 if v1_parquet else 250_000)
        family = f"mf-{uuid4().hex[:8]}"
        await _seed_approved_model(
            database, workspace_id, family, {"driver_age_band": _AGE_LEVELS}
        )
        slug = f"tbl-{uuid4().hex[:8]}"
        await svc.seed_from_model(
            database, workspace_id, principal.id, Settings(), blob_store, slug=slug,
            model_ref=ArtifactRef(type="model", slug=family, version=1),
            factor="driver_age_band", change_note="seed",
        )
        await _set_threshold(database, workspace_id, 1)
        await svc.import_confirmed(
            database, workspace_id, principal.id, Settings(), blob_store, slug=slug,
            version=1, filename="v2.csv",
            content=b"driver_age_band,relativity\n17-20,2.1120\n21-24,1.2690\n25-29,1.1200\n",
        )
        await _set_threshold(database, workspace_id, 250_000)
        return slug

    mixed = await table(v1_parquet=False)
    both = await table(v1_parquet=True)
    params = {"against": "previous"}

    first = api_client.get(_cells_url(mixed), params=params, headers=analyst)
    assert first.status_code == 202, first.text
    assert await execute_job(database, UUID(first.json()["id"]), blob_store) is JobStatus.SUCCEEDED
    before = await _job_count(database)
    twin = api_client.get(_cells_url(both), params=params, headers=analyst)
    assert twin.status_code == 200, twin.text
    assert await _job_count(database) == before
    assert twin.json() == api_client.get(_cells_url(mixed), params=params, headers=analyst).json()
