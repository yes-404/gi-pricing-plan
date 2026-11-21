"""The split and diagnostics surface over HTTP (`01` §5.1, `02` §5.1).

Written for the reason `test_api_transformations` gives, and one more specific to these:
`record_split` had a tested service function, a database table and **no route**, since WK-660.
The endpoint audit compares the spec's §5.1 table against the published contract, so an
endpoint missing from both is invisible to it — which is exactly how this one survived a
workstream closure. A test at the HTTP layer is what makes the absence detectable.
"""

from __future__ import annotations

import asyncio

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_contracts import OPENAPI, _load
from fastapi.testclient import TestClient

from model_schema import new_uuid7


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    return _headers(principal.id, workspace_id)


@pytest.mark.req("FR-76")
def test_the_split_endpoints_are_published() -> None:
    """The gap this slice closed: both routes must be in the **published contract** that
    external consumers read, not merely reachable in the running app. The endpoint audit
    reads this file, so this is the layer where the absence was invisible."""
    paths = _load(OPENAPI)["paths"]
    assert "/api/v1/dataset-versions/{version_id}/splits" in paths
    entry = paths["/api/v1/dataset-versions/{version_id}/splits"]
    assert "post" in entry
    assert "get" in entry


@pytest.mark.req("FR-170")
def test_the_diagnostics_endpoint_is_published() -> None:
    paths = _load(OPENAPI)["paths"]
    assert "/api/v1/models/{slug}/diagnostics" in paths


@pytest.mark.req("FR-76")
def test_a_one_part_split_is_refused_over_the_api(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """Negative, at the edge. A one-part split is a filter, and recorded as a split it
    would let a model claim a holdout it never had — so the refusal must reach the caller
    as a 422 rather than as a 500 from inside the service."""
    refused = api_client.post(
        f"/api/v1/dataset-versions/{new_uuid7()}/splits",
        json={
            "name": "broken",
            "method": "random",
            "seed": 1,
            "parts": {"train": str(new_uuid7())},
        },
        headers=actuary,
    )
    assert refused.status_code == 422, refused.text


@pytest.mark.req("FR-170")
def test_diagnostics_for_an_unknown_model_are_a_404(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    missing = api_client.get(
        f"/api/v1/models/no-such-family-{new_uuid7().hex[-6:]}/diagnostics", headers=actuary
    )
    assert missing.status_code == 404, missing.text


# -- The finer level of a grouping chain (FR-109; #1506 slice 5, decision #1870 (b)) ---------

#: A book on a two-level chain whose two readings differ (decision #1908). `postcode` holds
#: the raw values; `area` (postcode to area) is `region`'s parent, applied first. The rating
#: Factor is on `region`, which reads the `area` column, so the fit resolves as it does today;
#: the finer levels are rebuilt from `postcode` alone. Reading each level from its own
#: grouping's column instead would give the area level the raw postcodes again (`AB1`, not
#: `AB`). Unit exposure; `AB1` carries two claims a row and `AB2` one, so the postcode level
#: shows a spread inside `NORTH` that the fitted level cannot.
_POSTCODES = ("AB1", "AB2", "CD1", "CD1")
_CLAIMS = {"AB1": 2, "AB2": 1, "CD1": 1}
CHAIN_BOOK = b"policy_id,exposure_years,postcode,area,claim_count,claim_amount_minor\n" + b"".join(
    (
        f"P{i},1.0,{_POSTCODES[i % 4]},{_POSTCODES[i % 4][:2]},{_CLAIMS[_POSTCODES[i % 4]]},"
        f"{100000 * _CLAIMS[_POSTCODES[i % 4]]}\n"
    ).encode()
    for i in range(1, 401)
)


async def _chain_fit(
    database, blob_store, workspace_id, *, chained: bool, gbm: bool = False,
    area_slug: str | None = None,
):
    """A GLM (or, with `gbm`, a GBM) fitted through the real Job on a GROUPING Factor: on
    `region` (chained under `area`) when `chained`, or on `area` (no parent) otherwise. Returns
    the actor, the model's family slug and the area grouping's slug. `area_slug` names the
    deepest grouping; `"postcode"` makes it equal to the column it reads."""
    from uuid import uuid4

    from backend.tests.test_model_jobs import (
        _actuary,
        _dataset,
        _spec,
        _split,
        _validated_version,
    )

    from app.platform import jobs as job_service
    from app.platform import modelling as model_service
    from app.platform import transformations as transform_service
    from app.worker.data_handlers import register_data_handlers
    from app.worker.model_handlers import register_model_handlers
    from app.worker.tasks import execute_job
    from model_schema import (
        Factor,
        FactorType,
        Grouping,
        GroupingMethod,
        JobKind,
        JobStatus,
        UnseenLevelBehaviour,
    )

    register_data_handlers()
    register_model_handlers()
    actor = await _actuary(database, workspace_id)
    dataset_id = await _dataset(database, blob_store, workspace_id, actor)
    version_id = await _validated_version(
        database, blob_store, workspace_id, actor, dataset_id, book=CHAIN_BOOK
    )
    split = await _split(database, blob_store, workspace_id, actor, version_id)
    suffix = uuid4().hex[-6:]
    area = Grouping(
        id=uuid4(), slug=area_slug or f"area-{suffix}", dataset_id=dataset_id, version=1,
        column="postcode", method=GroupingMethod.MANUAL,
        mapping={"AB1": "AB", "AB2": "AB", "CD1": "CD"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
    )
    async with database.unit_of_work() as session:
        area_id = (
            await transform_service.create_grouping(
                session, workspace_id=workspace_id, actor=actor, grouping=area
            )
        ).id
    region = Grouping(
        id=uuid4(), slug=f"region-{suffix}", dataset_id=dataset_id, version=1,
        column="area", method=GroupingMethod.MANUAL,
        mapping={"AB": "NORTH", "CD": "SOUTH"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR,
        parent_grouping_id=area_id,
    )
    async with database.unit_of_work() as session:
        region_id = (
            await transform_service.create_grouping(
                session, workspace_id=workspace_id, actor=actor, grouping=region
            )
        ).id
    grouping_id, column = (region_id, "area") if chained else (area_id, "postcode")
    async with database.unit_of_work() as session:
        factor_id = (
            await model_service.create_factor(
                session, workspace_id=workspace_id, actor=actor,
                factor=Factor(
                    id=uuid4(), slug="region", dataset_id=dataset_id, version=1,
                    type=FactorType.GROUPING, source_columns=(column,),
                    grouping_id=grouping_id,
                ),
            )
        ).id
    if gbm:
        from backend.tests.test_model_jobs_gbm import _gbm_spec

        spec = _gbm_spec(version_id, (factor_id,), split_ref=split)
    else:
        spec = _spec(version_id, (factor_id,), split_ref=split)
    async with database.unit_of_work() as session:
        row, _ = await model_service.reserve_model(
            session, workspace_id=workspace_id, actor=actor, spec=spec
        )
        job = await job_service.submit(
            session,
            JobKind.MODEL_FIT,
            {"workspace_id": str(workspace_id), "actor": actor.model_dump(mode="json"),
             "model_id": str(row.id)},
            actor,
            workspace_id=workspace_id,
        )
    assert await execute_job(database, job.id, blob_store) is JobStatus.SUCCEEDED
    return actor, spec.model_family_slug, area.slug


def _on_own_loop(make):
    """Drive async setup on a loop made for it: `TestClient` is blocking, so the async
    fixtures cannot be requested beside it (`test_api_model_lifecycle._fitted`'s reason)."""
    from backend.tests.conftest_db import test_blob_bucket, test_database_url

    from app.config import Settings
    from app.db.session import Database
    from app.platform.blobs import BlobStore

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        store = BlobStore(Settings(blob_bucket=test_blob_bucket()))
        try:
            loop.run_until_complete(store.ensure_bucket())
        except Exception as exc:  # pragma: no cover - infrastructure, not behaviour
            pytest.skip(f"MinIO not reachable: {type(exc).__name__}")
        try:
            return loop.run_until_complete(make(database, store))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()


def _cells(level: dict) -> dict[str, dict]:
    return {cell["level"]: cell for cell in level["cells"]}


@pytest.mark.req("FR-109")
@pytest.mark.req("FR-170")
@pytest.mark.req("FR-183")
def test_a_fit_on_a_chained_grouping_stores_the_finer_level_ae_and_the_read_returns_it(
    api_client: TestClient, workspace_id
) -> None:
    """Computed at fit time and stored on the `Diagnostics` as one top-level field, for train
    and holdout (FR-183); the read returns it as stored, and nothing is computed on read
    (FR-170)."""
    actor, slug, area_slug = _on_own_loop(
        lambda db, store: _chain_fit(db, store, workspace_id, chained=True)
    )
    read = api_client.get(
        f"/api/v1/models/{slug}/diagnostics", headers=_headers(actor.id, workspace_id)
    )
    assert read.status_code == 200, read.text
    body = read.json()
    assert body["finer_level_ae"] is not None, "no finer-level A/E on the read"
    # Not on the partitions: the field is the artifact's, and `PartitionDiagnostics` (which a
    # Backtest also reports) is unchanged (#1506, the maintainer's (B)).
    assert "finer_level_ae" not in body["universal"]["train"]

    for name in ("train", "holdout"):
        partition = body["universal"][name]
        finer = body["finer_level_ae"][name]
        assert [entry["factor"] for entry in finer] == ["region"]
        levels = finer[0]["levels"]
        # Finest first: the deepest column as it is, then the level `area` produces from it.
        assert [level["name"] for level in levels] == ["postcode", area_slug]
        postcode, area = levels
        # The readings differ (#1908): rebuilt, the area level is AB and CD, never raw codes.
        assert sorted(_cells(postcode)) == ["AB1", "AB2", "CD1"]
        assert sorted(_cells(area)) == ["AB", "CD"]
        fitted = {
            cell["level"]: cell
            for cell in partition["ae_by_factor"]
            if cell["factor"] == "region"
        }
        for level in levels:
            # Every row is rebuilt on this book, and the named "not available" row says so.
            assert level["unavailable_rows"] == 0
            assert float(level["unavailable_exposure"]) == 0.0
            # The level's totals equal the partition's: the same rows, the same fitted means.
            assert sum(c["actual"] for c in level["cells"]) + level[
                "unavailable_actual"
            ] == pytest.approx(sum(c["actual"] for c in fitted.values()))
            assert sum(c["expected"] for c in level["cells"]) + level[
                "unavailable_expected"
            ] == pytest.approx(sum(c["expected"] for c in fitted.values()))
            assert sum(float(c["exposure_years"]) for c in level["cells"]) == pytest.approx(
                partition["rows"]
            )
        # Area AB is all of region NORTH, so the two readings of it agree exactly ...
        assert _cells(area)["AB"]["ae"] == pytest.approx(fitted["NORTH"]["ae"])
        assert _cells(area)["CD"]["ae"] == pytest.approx(fitted["SOUTH"]["ae"])
        # ... and the postcode level shows the spread inside NORTH the fitted level cannot.
        assert _cells(postcode)["AB1"]["ae"] > 1.0 > _cells(postcode)["AB2"]["ae"]


@pytest.mark.req("FR-109")
@pytest.mark.parametrize(("chained", "named"), [(True, ["region"]), (False, [])])
def test_the_read_names_the_factors_that_have_a_finer_level(
    api_client: TestClient, workspace_id, chained: bool, named: list[str]
) -> None:
    """`chained_factors` (`02` §5.1, #1506 slice 5): the route composes it from the model's
    definition by the fit's own rule, so the view needs no rule of its own to tell "no finer
    level" from "fitted before the finer level was stored"."""
    actor, slug, _ = _on_own_loop(
        lambda db, store: _chain_fit(db, store, workspace_id, chained=chained)
    )
    read = api_client.get(
        f"/api/v1/models/{slug}/diagnostics", headers=_headers(actor.id, workspace_id)
    )
    assert read.status_code == 200, read.text
    assert read.json()["chained_factors"] == named
    # The fit's rule and the read's agree: the Factors named are those that got a finer level.
    assert [entry["factor"] for entry in read.json()["finer_level_ae"]["holdout"]] == named


@pytest.mark.req("FR-109")
def test_a_chain_parent_that_is_gone_is_skipped_never_a_404_that_fails_the_fit(
    workspace_id,
) -> None:
    """A stored Grouping can name a parent that no longer exists (the column has no foreign
    key). Loading the chain for the fit's diagnostics skips it, so `finer_levels` reports that
    level as "not available" and the fit is not failed by a `404` (FR-109's amendment of
    2026-11-17). Each parent is looked up on its own: a batch with one missing id is refused."""
    from uuid import uuid4

    from app.worker.model_handlers import _chain_parents
    from model_schema import Grouping, GroupingMethod, UnseenLevelBehaviour

    dangling = Grouping(
        id=uuid4(), slug="region-dangling", dataset_id=uuid4(), version=1,
        column="area", method=GroupingMethod.MANUAL, mapping={"AB": "NORTH"},
        unseen_level_behaviour=UnseenLevelBehaviour.ERROR, parent_grouping_id=uuid4(),
    )

    async def load(database, _store):
        async with database.session() as session:
            return await _chain_parents(
                session, workspace_id=workspace_id, groupings={dangling.id: dangling}
            )

    assert _on_own_loop(load) == {}


@pytest.mark.req("FR-109")
def test_a_fit_on_an_unchained_grouping_stores_no_finer_level(
    api_client: TestClient, workspace_id
) -> None:
    """A grouping with no parent has no finer level: the fit stores an empty set, which is
    "computed, and nothing to show", never `null` ("not available", a fit before the change)."""
    actor, slug, _ = _on_own_loop(
        lambda db, store: _chain_fit(db, store, workspace_id, chained=False)
    )
    read = api_client.get(
        f"/api/v1/models/{slug}/diagnostics", headers=_headers(actor.id, workspace_id)
    )
    assert read.status_code == 200, read.text
    assert read.json()["finer_level_ae"] == {"train": [], "holdout": []}


@pytest.mark.req("FR-109")
@pytest.mark.req("FR-170")
def test_a_level_query_returns_that_finer_level_only(
    api_client: TestClient, workspace_id
) -> None:
    """`?level=` selects one finer level of a chained grouping (`02` §5.1, #1506 slice 5): the
    rows of that level for each chained Factor that has it, read from what the fit stored, and
    the same rows as the unfiltered read carries for it."""
    actor, slug, area_slug = _on_own_loop(
        lambda db, store: _chain_fit(db, store, workspace_id, chained=True)
    )
    url = f"/api/v1/models/{slug}/diagnostics"
    headers = _headers(actor.id, workspace_id)
    everything = api_client.get(url, headers=headers)
    assert everything.status_code == 200, everything.text
    stored = everything.json()["finer_level_ae"]

    for level in ("postcode", area_slug):
        read = api_client.get(url, params={"level": level}, headers=headers)
        assert read.status_code == 200, read.text
        finer = read.json()["finer_level_ae"]
        for name in ("train", "holdout"):
            (entry,) = finer[name]
            assert entry["factor"] == "region"
            assert [lv["name"] for lv in entry["levels"]] == [level], (
                f"{name}: ?level={level} returned levels "
                f"{[lv['name'] for lv in entry['levels']]}"
            )
            (whole,) = [lv for lv in stored[name][0]["levels"] if lv["name"] == level]
            assert entry["levels"][0] == whole


@pytest.mark.req("FR-109")
def test_any_level_on_a_model_with_no_chain_is_refused_422(
    api_client: TestClient, workspace_id
) -> None:
    """A model fitted after the change on a grouping with no parent stored an empty finer level:
    it has no level to select, so any `level` is refused 422 (`02` §5.1)."""
    actor, slug, area_slug = _on_own_loop(
        lambda db, store: _chain_fit(db, store, workspace_id, chained=False)
    )
    read = api_client.get(
        f"/api/v1/models/{slug}/diagnostics",
        params={"level": area_slug},
        headers=_headers(actor.id, workspace_id),
    )
    assert read.status_code == 422, read.text
    assert read.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-109")
def test_a_slug_equal_to_its_column_fits_and_both_levels_are_selectable(
    api_client: TestClient, workspace_id
) -> None:
    """The deepest grouping is named `postcode` and reads the `postcode` column. The fit
    succeeds (`_chain_fit` asserts the Job SUCCEEDED), and the raw level is stored as "postcode
    (column)" beside the grouping's own level "postcode", each selectable by `?level=`."""
    actor, slug, _ = _on_own_loop(
        lambda db, store: _chain_fit(
            db, store, workspace_id, chained=True, area_slug="postcode"
        )
    )
    headers = _headers(actor.id, workspace_id)
    read = api_client.get(f"/api/v1/models/{slug}/diagnostics", headers=headers)
    assert read.status_code == 200, read.text
    levels = read.json()["finer_level_ae"]["holdout"][0]["levels"]
    assert [level["name"] for level in levels] == ["postcode (column)", "postcode"]
    for name in ("postcode (column)", "postcode"):
        one = api_client.get(
            f"/api/v1/models/{slug}/diagnostics", params={"level": name}, headers=headers
        )
        assert one.status_code == 200, one.text
        kept = one.json()["finer_level_ae"]["holdout"][0]["levels"]
        assert [level["name"] for level in kept] == [name]


@pytest.mark.req("FR-109")
def test_a_level_not_in_the_chain_is_refused_422(api_client: TestClient, workspace_id) -> None:
    """A `level` that is not a level of a chain on the model's groupings is a request that fails
    validation: `422 VALIDATION_FAILED`, never an empty table that looks like a real answer."""
    actor, slug, _ = _on_own_loop(
        lambda db, store: _chain_fit(db, store, workspace_id, chained=True)
    )
    read = api_client.get(
        f"/api/v1/models/{slug}/diagnostics",
        params={"level": "not-a-level-of-this-chain"},
        headers=_headers(actor.id, workspace_id),
    )
    assert read.status_code == 422, read.text
    body = read.json()
    assert body["code"] == "VALIDATION_FAILED"
    assert [error["field"] for error in body["errors"]] == ["level"]


@pytest.mark.req("FR-109")
@pytest.mark.req("FR-137")
@pytest.mark.req("FR-141")
def test_a_surrogate_of_a_model_on_a_chained_grouping_stores_the_finer_level(
    api_client: TestClient, workspace_id
) -> None:
    """The maintainer's (c) on #1506: a surrogate's diagnostics compute the finer level through
    the same call as any other GLM's, so a surrogate fitted after the change has it stored and
    "not available" keeps meaning only a model fitted before it. Its A/E is the surrogate
    against the source model's predictions (FR-137(iii)), which FR-141 says how to read."""

    async def surrogate_of_a_chained_gbm(database, store):
        from backend.tests.test_glm_approximation_model import _transparency_job

        from app.platform import modelling as model_service

        actor, slug, area_slug = await _chain_fit(
            database, store, workspace_id, chained=True, gbm=True
        )
        async with database.session() as session:
            source = await model_service.load_model(
                session, workspace_id=workspace_id, slug=slug
            )
        artifact = await _transparency_job(database, store, workspace_id, source.id, actor)
        assert artifact.glm_approximation is not None
        return actor, f"{slug}-approx", area_slug

    actor, surrogate_slug, area_slug = _on_own_loop(surrogate_of_a_chained_gbm)
    read = api_client.get(
        f"/api/v1/models/{surrogate_slug}/diagnostics", headers=_headers(actor.id, workspace_id)
    )
    assert read.status_code == 200, read.text
    finer = read.json()["finer_level_ae"]
    assert finer is not None, "the surrogate's diagnostics stored no finer level"
    for name in ("train", "holdout"):
        assert [entry["factor"] for entry in finer[name]] == ["region"]
        assert [lv["name"] for lv in finer[name][0]["levels"]] == ["postcode", area_slug]


#: A `Diagnostics` payload as a fit stored it before the finer level existed: no
#: `finer_level_ae` key.
_PARTITION_BEFORE = {
    "weighting": "exposure",
    "rows": 100,
    "ae_overall": 1.0,
    "ae_by_factor": [],
    "lift": [],
    "gini": 0.2,
    "gini_normalised": 0.3,
    "calibration": [],
    "residual_summary": None,
}
_PAYLOAD_BEFORE = {
    "universal": {"train": _PARTITION_BEFORE, "holdout": {**_PARTITION_BEFORE, "rows": 30}},
    "complexity": {"factor_count": 1, "parameter_count": 2},
    "glm": None,
    "gbm": None,
    "cross_validation": None,
}


@pytest.mark.req("FR-109")
@pytest.mark.req("FR-170")
def test_a_payload_stored_before_the_change_still_reads_and_is_not_available() -> None:
    """The stored row is never rewritten (FR-43), so the shape must read it as it is: the key
    absent, and the field `None`, which the view shows as "not available"."""
    from datetime import UTC, datetime

    from app.db.models import DiagnosticsRow
    from app.platform import diagnostics as diagnostics_service

    row = DiagnosticsRow(
        id=new_uuid7(), workspace_id=new_uuid7(), model_id=new_uuid7(),
        computed_at=datetime(2026, 11, 1, tzinfo=UTC), job_id=None,
        payload=_PAYLOAD_BEFORE,
    )
    assert "finer_level_ae" not in row.payload
    stored = diagnostics_service.to_diagnostics(row)
    assert stored.finer_level_ae is None


@pytest.mark.req("FR-109")
@pytest.mark.req("FR-170")
def test_a_model_fitted_before_the_change_reads_as_not_available(
    api_client: TestClient, workspace_id
) -> None:
    """Over HTTP: a model whose diagnostics were recorded without the finer level reads
    `finer_level_ae: null`, never empty lists, so the view can tell "not available" (refit to
    see it) from "no chained grouping"."""

    async def recorded_before(database, store):
        from backend.tests.test_model_jobs import (
            _actuary,
            _dataset,
            _factor,
            _spec,
            _split,
            _validated_version,
        )

        from app.platform import modelling as model_service
        from model_schema import Diagnostics, GlmFitResult

        actor = await _actuary(database, workspace_id)
        dataset_id = await _dataset(database, store, workspace_id, actor)
        version_id = await _validated_version(database, store, workspace_id, actor, dataset_id)
        area = await _factor(database, workspace_id, actor, dataset_id, "area", "area")
        split = await _split(database, store, workspace_id, actor, version_id)
        spec = _spec(version_id, (area,), split_ref=split)
        async with database.unit_of_work() as session:
            row, _ = await model_service.reserve_model(
                session, workspace_id=workspace_id, actor=actor, spec=spec
            )
            await model_service.record_fit(
                session, workspace_id=workspace_id, actor=actor, model_id=row.id,
                fit_result=GlmFitResult(
                    converged=True, iterations=3, fit_seconds=0.1, dispersion=1.0
                ),
                diagnostics=Diagnostics.model_validate(
                    {**_PAYLOAD_BEFORE, "id": str(new_uuid7()), "model_id": str(row.id),
                     "computed_at": "2026-11-01T00:00:00+00:00"}
                ),
            )
        return actor, spec.model_family_slug

    actor, slug = _on_own_loop(recorded_before)
    read = api_client.get(
        f"/api/v1/models/{slug}/diagnostics", headers=_headers(actor.id, workspace_id)
    )
    assert read.status_code == 200, read.text
    body = read.json()
    assert "finer_level_ae" in body, "the read does not carry the field"
    assert body["finer_level_ae"] is None
    # With `level`, the same "not available", never a 422: the chain may well have that level,
    # and it is the stored artifact that has nothing to select from.
    filtered = api_client.get(
        f"/api/v1/models/{slug}/diagnostics",
        params={"level": "postcode"},
        headers=_headers(actor.id, workspace_id),
    )
    assert filtered.status_code == 200, filtered.text
    assert filtered.json()["finer_level_ae"] is None

