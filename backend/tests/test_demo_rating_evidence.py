"""The demo Rating Version is priced from the approved GLM, and its evidence is not circular
(PL-1525 Acceptance 1, 2, 3 and 6; WK-1178 exit-demo slice (a)).

`examples/fremtpl2/model.py` seeds one Rate Table per Factor of the approved GLM
(`seed_demo_rate_tables`), builds the algorithm over them, creates the Rating Version pinning
the algorithm, the model and every table, and gives it **executed** regression evidence whose
golden quotes are the GLM's own premiums. Models are inserted here rather than fitted: the
fit's coefficients are the test's own numbers, so the expected premiums below are computed in
this file, in Decimal, from those numbers, and never from the seeded tables or the scored bundle.
"""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import os
import sys
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from backend.tests.approved_rows import add_approved
from backend.tests.test_api_rate_tables import _ensure_factor, _glm_spec
from backend.tests.test_fremtpl2_algorithm import _BANDED, _DOMAINS, _FACTORS
from backend.tests.test_rating_versions import _principal
from backend.tests.test_score import admin_headers, client, scoring_headers  # noqa: F401
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.config import Settings
from app.db.models import (
    FactorRow,
    JobRow,
    ModelRow,
    RateTableRow,
    RateTableVersionRow,
    RegressionRunRow,
)
from app.db.session import Database
from app.platform import rating_versions as rating_service
from app.platform import transformations as transform_service
from model_schema import (
    ArtifactRef,
    Factor,
    FactorType,
    JobKind,
    JobStatus,
    ModelStatus,
    QuoteContext,
    RegressionRun,
    RegressionSuiteContent,
    new_uuid7,
)
from pricing_core.rating.properties import payable_minor
from pricing_core.rating.score import score_one

#: Overridable only so the 422 test can be run red against the parent's `string` algorithm.
_EXAMPLE = Path(
    os.environ.get("GIP_FREMTPL2_EXAMPLE_DIR")
    or Path(__file__).resolve().parents[2] / "examples" / "fremtpl2"
)
sys.path.insert(0, str(_EXAMPLE))  # `model.py` imports its sibling `algorithm`
_SPEC = importlib.util.spec_from_file_location("demo_model", _EXAMPLE / "model.py")
assert _SPEC is not None
assert _SPEC.loader is not None
demo_model = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = demo_model  # a dataclass in the module resolves its own module
_SPEC.loader.exec_module(demo_model)

_INTERCEPT = Decimal("-2.5")
_BASE_MINOR = 200_000
#: The fitted log-relativity of every non-base level; a base level is the first of its Factor.
_ESTIMATES: dict[str, dict[str, Decimal]] = {
    "driv_age_band": {"25-39": Decimal("-0.2"), "40+": Decimal("-0.1")},
    "veh_age_band": {"3-9": Decimal("0.1"), "10+": Decimal("0.25")},
    "veh_power_band": {"6-7": Decimal("0.05"), "8+": Decimal("0.3")},
    "veh_brand": {"B2": Decimal("0.15")},
    "veh_gas": {"Regular": Decimal("-0.07")},
    "area": {"B": Decimal("0.12")},
    "region": {"R24": Decimal("-0.05")},
}


def _levels(factor: str) -> list[str]:
    if factor in _BANDED:
        return list(_BANDED[factor].labels)
    return list(_DOMAINS[factor])


def _fit_result() -> dict[str, object]:
    """A `GlmFitResult` as JSON, from `_ESTIMATES`."""
    coefficients = [{
        "term": "intercept", "estimate": float(_INTERCEPT), "std_error": 0.01, "z": -250.0,
        "p_value": 0.0, "ci_95": [float(_INTERCEPT) - 0.02, float(_INTERCEPT) + 0.02],
        "relativity": float(_INTERCEPT.exp()),
    }]
    relativities: dict[str, list[dict[str, object]]] = {}
    for factor in _FACTORS:
        levels = _levels(factor)
        relativities[factor] = [
            {"level": levels[0], "relativity": 1.0, "estimate": 0.0, "is_base": True}
        ]
        for level in levels[1:]:
            estimate = _ESTIMATES[factor][level]
            relativity = float(estimate.exp())
            coefficients.append({
                "term": f"{factor}[{level}]", "estimate": float(estimate), "std_error": 0.01,
                "z": 5.0, "p_value": 0.01,
                "ci_95": [float(estimate) - 0.02, float(estimate) + 0.02],
                "relativity": relativity,
            })
            relativities[factor].append({
                "level": level, "relativity": relativity, "estimate": float(estimate),
                "is_base": False,
            })
    return {
        "model_type": "glm", "converged": True, "iterations": 8, "fit_seconds": 1.0,
        "coefficients": coefficients, "relativities": relativities,
    }


def _expected_minor(levels: dict[str, str]) -> int:
    """The GLM's premium for a quote, computed here from `_ESTIMATES`: base x exp(sum of the
    fitted log-relativities of the non-base levels), half-even to a whole minor unit."""
    total = sum(
        (_ESTIMATES[factor].get(level, Decimal(0)) for factor, level in levels.items()),
        Decimal(0),
    )
    return int((Decimal(_BASE_MINOR) * total.exp()).quantize(Decimal(1), ROUND_HALF_EVEN))


#: Three quotes, as `{factor: level}`: every base level; a non-base level of every Factor; the
#: last level of every Factor. A banded Factor's raw value is the lower edge of its band.
_QUOTES: dict[str, dict[str, str]] = {
    "base-levels": {f: _levels(f)[0] for f in _FACTORS},
    "first-non-base-levels": {f: _levels(f)[1] for f in _FACTORS},
    "last-levels": {f: _levels(f)[-1] for f in _FACTORS},
}


def _raw_inputs(levels: dict[str, str]) -> dict[str, object]:
    inputs: dict[str, object] = {"bonus_malus": 100}
    for factor, level in levels.items():
        if factor in _BANDED:
            banding = _BANDED[factor]
            inputs[banding.column] = int(banding.boundaries[banding.labels.index(level)])
        else:
            inputs[factor] = level
    return inputs


async def _banded_factor(session, workspace_id, analyst, slug: str) -> object:  # type: ignore[no-untyped-def]
    """A BANDING Factor over its saved, pinned Banding, built the way the demo builds it
    (`examples/fremtpl2/model.py` `create_demo_bandings` + `_create_factor`, lines 175-188 and
    247-280 at the SL-1543 base): `create_banding` persists the Banding, and the Factor is
    `FactorType.BANDING` over the Banding's column with `banding_id` set. The hand-made fit
    below has `slug[label]` dummy terms over band labels, which only a banded Factor can
    produce; an IDENTITY Factor scores every one of them as 0 (the 20:56:36 BST ruling)."""
    # The demo's grammar-valid slug (`examples/fremtpl2/model.py:269`): the fixture's own
    # `<column>-banding` has an underscore, which `ArtifactRef` refuses for a `banding` at compile.
    banding = _BANDED[slug].model_copy(
        update={"slug": f"fremtpl2-{slug.replace('_', '-')}-banding"}
    )
    saved = await transform_service.create_banding(
        session, workspace_id=workspace_id, actor=analyst, banding=banding
    )
    factor = Factor(
        id=new_uuid7(), slug=slug, dataset_id=banding.dataset_id, version=1,
        type=FactorType.BANDING, source_columns=(banding.column,), banding_id=saved.id,
    )
    row = FactorRow(
        workspace_id=workspace_id, dataset_id=factor.dataset_id, slug=slug, version=1,
        body=factor.model_dump(mode="json", exclude={"id", "version", "dataset_id"}),
    )
    session.add(row)
    await session.flush()
    return row.id


async def _approved_model(database: Database, workspace_id) -> object:
    family = f"fremtpl2-glm-{uuid4().hex[:6]}"
    analyst = await _principal(database, workspace_id, "analyst")
    async with database.unit_of_work() as session:
        pinned = [
            await _banded_factor(session, workspace_id, analyst, slug)
            if slug in _BANDED
            else await _ensure_factor(session, workspace_id, slug, 1)
            for slug in _FACTORS
        ]
        spec = _glm_spec(family, new_uuid7())
        spec["factors"] = [str(factor_id) for factor_id in pinned]
        row = await add_approved(
            session,
            ModelRow(
                workspace_id=workspace_id, model_family_slug=family, version=1,
                status=ModelStatus.APPROVED.value, dataset_version_id=new_uuid7(), spec=spec,
                spec_hash=f"v3:sha256:{uuid4().hex}{uuid4().hex}", fit_result=_fit_result(),
                diagnostics_id=uuid4(),
            ),
        )
        return row.id


def _bandings() -> dict[str, object]:
    return {slug: demo_model.DemoBanding(new_uuid7(), banding) for slug, banding in _BANDED.items()}


async def _seed(database: Database, workspace_id, blob_store):  # type: ignore[no-untyped-def]
    analyst = await _principal(database, workspace_id, "analyst")
    model_id = await _approved_model(database, workspace_id)
    tables = await demo_model.seed_demo_rate_tables(
        database, Settings(), blob_store, workspace_id, analyst, model_id
    )
    return analyst, model_id, tables


@pytest.mark.req("FR-230")
async def test_the_seed_seeds_one_table_per_rateable_factor(
    database: Database, workspace_id, blob_store
) -> None:
    """One Rate Table per Factor of the approved GLM, `fremtpl2-<factor slug, _ -> ->`, each
    `seeded_from` the approved model and each key bound to the model's Factor version."""
    _, model_id, tables = await _seed(database, workspace_id, blob_store)
    assert list(tables) == list(_FACTORS)
    async with database.session() as session:
        model_ref, _ = await demo_model.load_approved_glm(database, workspace_id, model_id)
        for factor, ref in tables.items():
            assert ref.slug == "fremtpl2-" + factor.replace("_", "-")
            row = (await session.execute(
                select(RateTableVersionRow)
                .join(RateTableRow, RateTableRow.id == RateTableVersionRow.rate_table_id)
                .where(RateTableRow.workspace_id == workspace_id, RateTableRow.slug == ref.slug,
                       RateTableVersionRow.version_number == ref.version)
            )).scalar_one()
            assert row.seeded_from is not None
            assert row.seeded_from["model_ref"] == str(model_ref)
            (key,) = row.definition["keys"]
            assert key["name"] == factor
            assert key["factor_ref"] == f"factor:{factor}@1"


@pytest.mark.req("FR-237")
async def test_the_demo_rating_version_pins_every_seeded_table(
    database: Database, workspace_id, blob_store
) -> None:
    """The Rating Version pins the algorithm, the approved GLM and exactly the seeded tables at
    their seeded versions, compiles through the `rating.compile` Job and is approved."""
    analyst, model_id, tables = await _seed(database, workspace_id, blob_store)
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    approver = await _principal(database, workspace_id, "approver")
    second = await _principal(database, workspace_id, "approver")
    rating_id = await demo_model.create_approved_rating_version(
        database, blob_store, workspace_id, analyst, actuary, approver, second,
        new_uuid7(), model_id, tables, _bandings(), _BASE_MINOR,
    )
    model_ref, _ = await demo_model.load_approved_glm(database, workspace_id, model_id)
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        compiles = (await session.execute(
            select(JobRow).where(JobRow.kind == JobKind.RATING_COMPILE)
        )).scalars().all()
    version = rating_service.to_schema(row)
    assert row.status == "approved"
    assert version.algorithm_ref == ArtifactRef(
        type="rating_algorithm", slug="fremtpl2-rate", version=1
    )
    assert version.pins is not None
    assert sorted(str(r) for r in version.pins.rate_tables) == sorted(
        str(r) for r in tables.values()
    )
    assert [str(r) for r in version.pins.models] == [str(model_ref)]
    assert any(job.status is JobStatus.SUCCEEDED for job in compiles)


@pytest.mark.req("FR-257")
async def test_the_demo_premium_is_the_glm_premium_and_the_golden_quotes_are_not_circular(
    database: Database, workspace_id, blob_store
) -> None:
    """Acceptance 3 and 6. For three quotes (every base level; a non-base level of every Factor;
    the last level of every Factor, banded ones on a band edge) the scored premium equals the
    premium computed here from the fit's coefficients. The Regression Suite holds the same three
    as golden quotes with those expected values, and its fixed properties pass
    in a run produced by the `rating.regression` Job."""
    analyst, model_id, tables = await _seed(database, workspace_id, blob_store)
    actuary = await _principal(database, workspace_id, "pricing_actuary")
    approver = await _principal(database, workspace_id, "approver")
    second = await _principal(database, workspace_id, "approver")
    rating_id = await demo_model.create_approved_rating_version(
        database, blob_store, workspace_id, analyst, actuary, approver, second,
        new_uuid7(), model_id, tables, _bandings(), _BASE_MINOR,
    )
    bundle = await demo_model._load_compiled(database, blob_store, workspace_id, rating_id)
    async with database.session() as session:
        row = await rating_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=rating_id
        )
        run_row = (await session.execute(
            select(RegressionRunRow).where(RegressionRunRow.rating_version_id == rating_id)
        )).scalar_one()
    ref = ArtifactRef(type="rating_version", slug=row.slug, version=row.version)
    run = RegressionRun.model_validate(run_row.run)
    assert run.overall == "pass"
    assert run.job_id is not None
    expected_by_name = {}
    for name, levels in _QUOTES.items():
        context = QuoteContext.model_validate({
            "purpose": "new_business", "quoted_at": "2026-09-28T09:00:00",
            "effective_date": "2026-10-01", "inputs": _raw_inputs(levels),
            "options": {"rating_version_ref": str(ref)},
        })
        scored = payable_minor(await score_one(bundle, context))
        expected = _expected_minor(levels)
        assert scored == expected, name
        expected_by_name[f"fremtpl2-rate-{name}"] = expected
    assert len(set(expected_by_name.values())) == 3  # three different premiums, not one
    assert [g.status for g in run.golden_results] == ["pass"] * 3
    assert {g.name: g.expected_minor for g in run.golden_results} == expected_by_name
    kinds = {p.name: p.status for p in run.property_results}
    assert kinds["no-null-output"] == "pass"
    assert kinds["premium-bounded"] == "pass"


@pytest.mark.req("FR-213")
def test_a_categorical_outside_its_declared_domain_is_a_422_through_the_api(
    client: TestClient, scoring_headers: dict[str, str],  # noqa: F811
    database: Database, blob_store, workspace_id,
) -> None:
    """SL-1526 condition (c), the HTTP status. The demo's categorical inputs are declared
    `enum`, so a `veh_brand` outside the seeded levels is refused at the input contract
    (`INPUT_CONTRACT_VIOLATION`, 422) rather than reaching the rate-table lookup, where it
    was a `RATE_TABLE_MISS`. The in-domain quote scores first, so the 422 is the value's."""
    loop = asyncio.get_event_loop()

    async def _build() -> ArtifactRef:
        analyst, model_id, tables = await _seed(database, workspace_id, blob_store)
        actuary = await _principal(database, workspace_id, "pricing_actuary")
        approver = await _principal(database, workspace_id, "approver")
        second = await _principal(database, workspace_id, "approver")
        rating_id = await demo_model.create_approved_rating_version(
            database, blob_store, workspace_id, analyst, actuary, approver, second,
            new_uuid7(), model_id, tables, _bandings(), _BASE_MINOR,
        )
        async with database.session() as session:
            row = await rating_service.load_rating_version(
                session, workspace_id=workspace_id, rating_version_id=rating_id
            )
        return ArtifactRef(type="rating_version", slug=row.slug, version=row.version)

    ref = loop.run_until_complete(_build())

    def _post(inputs: dict[str, object]):  # type: ignore[no-untyped-def]
        return client.post("/api/v1/score", headers=scoring_headers, json={
            "purpose": "new_business", "quoted_at": "2026-09-28T09:00:00Z",
            "effective_date": "2026-10-01", "inputs": inputs,
            "options": {"rating_version_ref": str(ref)},
        })

    base = _raw_inputs(_QUOTES["base-levels"])
    assert _post(base).status_code == 200
    response = _post({**base, "veh_brand": "ZZZ"})
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "INPUT_CONTRACT_VIOLATION"
    assert "veh_brand" in response.json()["detail"]


@pytest.mark.req("FR-261")
def test_the_declared_properties_are_fixed_and_read_no_fit() -> None:
    """A property is a declaration of intent, not a reading of the fit it then checks: the
    declaration takes no fit, is valid suite content, and claims no monotonicity (the fitted
    `veh_age_band` relativities are not monotone)."""
    assert not inspect.signature(demo_model.declared_properties).parameters
    properties = demo_model.declared_properties()
    assert [p["check"]["kind"] for p in properties] == ["no_null_output", "premium_bounded"]
    RegressionSuiteContent.model_validate({
        "algorithm_slug": "fremtpl2-rating", "golden_quotes": [], "properties": properties,
        "generation": {"cases": 25, "seed": 1, "strategy": "input_contract_sampling"},
    })
