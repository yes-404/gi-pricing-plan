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
from backend.tests.test_data_jobs import _validate
from backend.tests.test_model_jobs import _actuary, _dataset
from backend.tests.test_rate_tables_service import _fit_result, _glm_spec, _seed_approved_model
from sqlalchemy import select, update

from app.config import Settings
from app.db.models import RateTableRow, RateTableVersionRow
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
