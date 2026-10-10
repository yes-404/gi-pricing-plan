"""The approval gate, part one: FR-257 limb (2), `structural_diff` and FR-224 (PL-1500).

`submit_for_review` refuses a version with no Dislocation Run against its baseline (limb (2)),
persists FR-219's structural diff as evidence, and gates an `approximation`-mode version on
FR-224's threshold. Written before the code, as `PL-1500` §"Tasks" orders; each section is one
task's. Every test needs Postgres.

The shared submit fixture (`test_rating_versions._Gate.submit`) records the limb (2) run by
default; these tests pass `dislocation=False` and record, or withhold, the run themselves.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import polars as pl
import pytest
from backend.tests.test_rating_version_compile import _minimal_algorithm
from backend.tests.test_rating_versions import (
    _algorithm,
    _approved_baseline,
    _Gate,
    _gate,
    _quote,
    _requests_for,
    _suite,
    record_dislocation_run,
)
from sqlalchemy import select

from app.db.models import (
    ApprovalPolicyRow,
    DeploymentRow,
    EnvironmentRow,
    ModelRow,
    RatingAlgorithmRow,
    RatingVersionRow,
    TransparencyArtifactRow,
)
from app.db.session import Database
from app.errors import PlatformError
from app.platform import rating_versions as rating_versions_service
from app.worker.dislocation_handlers import _ExactModeResolver, abs_change_pct_quantiles
from model_schema import (
    DEFAULT_POLICY,
    ApprovalPolicy,
    ArtifactRef,
    RatingAlgorithm,
    diff_algorithms,
    new_uuid7,
)
from pricing_core.rating.compile import ResolvedArtifact

_STALE_HASH = "sha256:" + "0" * 64


def _ref(slug: str, version: int) -> str:
    return f"rating_version:{slug}@{version}"


async def _candidate(gate: _Gate) -> tuple[UUID, str, str]:
    """A second version on an approved baseline: its id, its ref and its bundle hash."""
    rv_id = await gate.version()
    row = await gate.row(rv_id)
    return rv_id, _ref(row.slug, row.version), str(row.bundle["content_hash"])  # type: ignore[index]


async def _refused(gate: _Gate, rating_id: UUID) -> PlatformError:
    with pytest.raises(PlatformError) as refused:
        await gate.submit(rating_id, dislocation=False)
    return refused.value


def _assert_limb_2_refusal(error: PlatformError, reason: str) -> None:
    assert error.code == "EVIDENCE_INCOMPLETE"
    assert error.status_code == 422
    assert error.detail is not None
    assert "FR-257 limb (2)" in error.detail
    assert reason in error.detail


# ---- Task 3: FR-257 limb (2) -------------------------------------------------------


@pytest.mark.req("FR-257")
async def test_limb_2_refuses_with_no_dislocation_run(database: Database, workspace_id) -> None:
    """Limb (2) only: the baseline exists (an approved version), no run names the candidate."""
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    rv_id, _, _ = await _candidate(gate)
    before = await _requests_for(database, workspace_id)

    _assert_limb_2_refusal(await _refused(gate, rv_id), "no Dislocation Run names this version")
    assert (await gate.row(rv_id)).status == "draft"
    assert await _requests_for(database, workspace_id) == before


@pytest.mark.req("FR-257")
async def test_limb_2_refuses_a_run_on_a_stale_candidate_bundle_hash(
    database: Database, workspace_id
) -> None:
    """Limb (2) only: a run exists, but on an earlier bundle hash than the version's current."""
    gate = await _gate(database, workspace_id)
    rv_a = await _approved_baseline(gate, _suite(_quote()))
    rv_id, ref, _ = await _candidate(gate)
    baseline = _ref("minimal-rv", (await gate.row(rv_a)).version)
    await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=_STALE_HASH,
        baseline_ref=baseline, actor_id=gate.analyst.id,
    )
    before = await _requests_for(database, workspace_id)

    _assert_limb_2_refusal(await _refused(gate, rv_id), "(stale)")
    assert await _requests_for(database, workspace_id) == before


@pytest.mark.req("FR-257")
async def test_limb_2_refuses_a_run_whose_baseline_is_not_the_current_live_version(
    database: Database, workspace_id
) -> None:
    """Limb (2) only: a run at the current hash, against a baseline that is not the one."""
    gate = await _gate(database, workspace_id)
    await _approved_baseline(gate, _suite(_quote()))
    rv_id, ref, current_hash = await _candidate(gate)
    await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=current_hash,
        baseline_ref=_ref("some-other-version", 9), actor_id=gate.analyst.id,
    )
    before = await _requests_for(database, workspace_id)

    _assert_limb_2_refusal(await _refused(gate, rv_id), "as its baseline")
    assert await _requests_for(database, workspace_id) == before


@pytest.mark.req("FR-257")
async def test_limb_2_accepts_a_run_against_the_live_version_and_records_it(
    database: Database, workspace_id
) -> None:
    """Limb (2) only: the right run is accepted and its id is written to the evidence."""
    gate = await _gate(database, workspace_id)
    rv_a = await _approved_baseline(gate, _suite(_quote()))
    rv_id, ref, current_hash = await _candidate(gate)
    run_id = await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=current_hash,
        baseline_ref=_ref("minimal-rv", (await gate.row(rv_a)).version),
        actor_id=gate.analyst.id,
    )

    await gate.submit(rv_id, dislocation=False)

    row = await gate.row(rv_id)
    assert row.status == "review"
    assert row.evidence["dislocation_run_id"] == str(run_id)  # type: ignore[index]
    assert "no_baseline" not in row.evidence  # type: ignore[operator]


@pytest.mark.req("FR-257")
async def test_limb_2_with_nothing_live_or_approved_records_the_first_version(
    database: Database, workspace_id
) -> None:
    """DP-S5-1 (a), RL-1504 T3: a first version needs no run; the evidence records why."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()

    await gate.submit(rv_id, dislocation=False)

    row = await gate.row(rv_id)
    assert row.status == "review"
    assert row.evidence["no_baseline"] == "first_version"  # type: ignore[index]
    assert "dislocation_run_id" not in row.evidence  # type: ignore[operator]


@pytest.mark.req("FR-257")
async def test_limb_2_prefers_the_version_live_in_the_baseline_environment(
    database: Database, workspace_id
) -> None:
    """DP-S5-1 (a): the live version in `prod` is the baseline, ahead of the most recently
    approved one. A run against the approved version is refused; one against the live is not."""
    gate = await _gate(database, workspace_id)
    rv_a = await _approved_baseline(gate, _suite(_quote()))
    rv_b = await gate.version()
    await gate.approve((await gate.submit(rv_b)).id)
    live_ref = _ref("minimal-rv", (await gate.row(rv_a)).version)
    approved_ref = _ref("minimal-rv", (await gate.row(rv_b)).version)
    async with database.unit_of_work() as session:
        # Environments are deployment-wide (ADR-710) and the fixture re-seeds `prod`: reuse it.
        environment = await session.scalar(
            select(EnvironmentRow).where(EnvironmentRow.slug == "prod")
        )
        assert environment is not None
        session.add(
            DeploymentRow(
                workspace_id=workspace_id, environment_id=environment.id,
                rating_version_ref=live_ref,
                bundle_hash=str((await gate.row(rv_a)).bundle["content_hash"]),  # type: ignore[index]
                deployed_by=gate.analyst.id, reason="fixture",
            )
        )
    rv_c, ref, current_hash = await _candidate(gate)
    await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=current_hash,
        baseline_ref=approved_ref, actor_id=gate.analyst.id,
    )
    _assert_limb_2_refusal(await _refused(gate, rv_c), "as its baseline")

    run_id = await record_dislocation_run(
        database, workspace_id, candidate_ref=ref, candidate_hash=current_hash,
        baseline_ref=live_ref, actor_id=gate.analyst.id,
    )
    await gate.submit(rv_c, dislocation=False)
    assert (await gate.row(rv_c)).evidence["dislocation_run_id"] == str(run_id)  # type: ignore[index]


# ---- Task 2: structural_diff (FR-364 E4, FR-219) -----------------------------------


@pytest.mark.req("FR-219")
def test_a_first_versions_diff_is_taken_against_an_empty_algorithm() -> None:
    """DP-S5-1 (a): with no baseline the diff is against an empty algorithm, so every step is
    an addition. DB-free: the empty algorithm must itself validate as a `RatingAlgorithm`."""
    candidate = RatingAlgorithm.model_validate(_minimal_algorithm())
    empty = rating_versions_service._empty_algorithm(like=candidate)
    diff = diff_algorithms(empty, candidate)
    assert diff.added_steps == sorted(step.step_id for step in candidate.steps)
    assert diff.removed_steps == []
    assert diff.changed_steps == []


def _expected_diff(old: dict[str, Any] | None, new: dict[str, Any]) -> bytes:
    candidate = RatingAlgorithm.model_validate(new)
    previous = (
        RatingAlgorithm.model_validate(old)
        if old is not None
        else rating_versions_service._empty_algorithm(like=candidate)
    )
    return diff_algorithms(previous, candidate).model_dump_json().encode()


@pytest.mark.req("FR-364")
@pytest.mark.req("FR-219")
async def test_submission_persists_the_structural_diff_as_a_blob(
    database: Database, workspace_id
) -> None:
    """A first version: the diff is against an empty algorithm; the evidence names the blob,
    whose bytes are `AlgorithmDiff.model_dump_json()`, and the verifier accepts the row."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()
    assert not rating_versions_service.structural_diff_verified(await gate.row(rv_id))

    await gate.submit(rv_id)

    row = await gate.row(rv_id)
    digest = row.evidence["structural_diff_blob"]  # type: ignore[index]
    assert gate.blob_store.objects[digest] == _expected_diff(None, _algorithm(1))
    assert hashlib.sha256(gate.blob_store.objects[digest]).hexdigest() == digest
    assert rating_versions_service.structural_diff_verified(row)


@pytest.mark.req("FR-364")
@pytest.mark.req("FR-219")
async def test_the_structural_diff_is_taken_against_the_baseline_algorithm(
    database: Database, workspace_id
) -> None:
    """A second version on `minimal@2` against the approved `minimal@1`: the diff names the
    changed step, not an all-additions diff against nothing."""
    gate = await _gate(database, workspace_id)
    # tolerance 1: `minimal@2` prices one minor unit above `minimal@1`, and the golden-quote
    # gate (FR-260) must pass for both.
    await _approved_baseline(gate, _suite(_quote(tolerance=1)))
    rv_id = await gate.version(algorithm="rating_algorithm:minimal@2")

    await gate.submit(rv_id)

    digest = (await gate.row(rv_id)).evidence["structural_diff_blob"]  # type: ignore[index]
    stored = gate.blob_store.objects[digest]
    assert stored == _expected_diff(_algorithm(1), _algorithm(2, plus=1))
    assert stored != _expected_diff(None, _algorithm(2, plus=1))


@pytest.mark.req("FR-364")
async def test_a_blob_store_is_required_to_submit(database: Database, workspace_id) -> None:
    """Fail closed: `submit_for_review` takes the store as a required keyword, so a caller that
    forgets it fails at once (`TypeError`), before anything is written."""
    gate = await _gate(database, workspace_id)
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()
    async with database.unit_of_work() as session:
        with pytest.raises(TypeError, match="blob_store"):
            await rating_versions_service.submit_for_review(  # type: ignore[call-arg]
                session, workspace_id=workspace_id, actor=gate.actuary,
                rating_version_id=rv_id, change_summary="no store",
            )


# ---- Task 4: the run's observed figure (RL-1504 T7; Acceptance 17 to 19, run half) --------

_KEYS = ("0.5", "0.9", "0.95", "0.99", "0.999", "1")


def _frame(*pairs: tuple[int, int]) -> pl.DataFrame:
    """A dislocation frame of policies quoted in both: `(baseline, candidate)` minor units."""
    return pl.DataFrame(
        {
            "quote_id": [f"q{i}" for i in range(len(pairs))],
            "baseline_outcome": ["quoted"] * len(pairs),
            "candidate_outcome": ["quoted"] * len(pairs),
            "baseline_minor": [b for b, _ in pairs],
            "candidate_minor": [c for _, c in pairs],
            "change_minor": [c - b for b, c in pairs],
        },
        schema_overrides={"change_minor": pl.Int64},
    )


@pytest.mark.req("FR-224")
def test_quantiles_are_nearest_rank_not_interpolated() -> None:
    """Choice (1): changes -1, +2, -3, +4 % have absolute values 1, 2, 3, 4 (n = 4). Rank
    ceil(0.5 x 4) = 2 gives 2; linear interpolation gives 2.5 and Polars' default 3.0; a signed
    order gives -1. Rank ceil(0.9 x 4) = 4 gives 4 (interpolation 3.7)."""
    quantiles = abs_change_pct_quantiles(
        _frame((10000, 9900), (10000, 10200), (10000, 9700), (10000, 10400))
    )
    assert quantiles == {
        "0.5": "2.000000",
        "0.9": "4.000000",
        "0.95": "4.000000",
        "0.99": "4.000000",
        "0.999": "4.000000",
        "1": "4.000000",
    }


@pytest.mark.req("FR-224")
def test_quantiles_round_once_toward_positive_infinity() -> None:
    """Choice (2): +100/3 % is 33.333... exactly, so its 7th place is 3 and half-even rounds
    DOWN to 33.333333; toward +infinity gives 33.333334. An exact +10 % is not moved."""
    quantiles = abs_change_pct_quantiles(_frame((30000, 40000), (10000, 11000)))
    assert quantiles == {
        "0.5": "10.000000",
        "0.9": "33.333334",
        "0.95": "33.333334",
        "0.99": "33.333334",
        "0.999": "33.333334",
        "1": "33.333334",
    }


@pytest.mark.req("FR-224")
def test_an_empty_banded_set_has_null_quantiles() -> None:
    """Choice (3), run half: two policies quoted in both with a zero baseline are not banded
    (n = 0); the run holds all six keys, each null. FR-224's gate refuses it (Task 5)."""
    assert abs_change_pct_quantiles(_frame((0, 5000), (0, 5000))) == dict.fromkeys(_KEYS)


# ---- Task 4: the exact-mode twin and FR-136's pre-check -----------------------------------

_MODEL_REF = "model:fidelity-model@1"


def _approximation_algorithm() -> dict[str, Any]:
    """`premium_in` through one `model_call` in `approximation` mode, then an expression."""
    return {
        "slug": "approx-algo",
        "version": 1,
        "input_contract": [{"name": "premium_in", "type": "int", "nullable": False}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "In", "input_name": "premium_in",
             "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_mc", "type": "model_call", "label": "Risk premium",
             "model_ref": _MODEL_REF, "mode": "approximation",
             "feature_map": {"premium_in": "premium_in"}, "consumes": ["premium_in"],
             "produces": ["risk_premium_minor"]},
            {"step_id": "s_out", "type": "output", "label": "Out",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["risk_premium_minor"]},
        ],
        "sub_graphs": [],
    }


def _glm_payload(statement: str) -> dict[str, Any]:
    return {
        "glm_approximation": {
            "target": "gbm_prediction", "family": "gamma", "link": "log",
            "r_squared": 0.94, "deviance_explained": 0.9,
            "coefficients": [
                {"term": "intercept", "estimate": -2.4, "std_error": 0.01, "z": -199.8,
                 "p_value": 0.0, "ci_95": [-2.44, -2.39]},
            ],
            "relativities": {"region": [{"level": "north", "relativity": 1.0, "is_base": True}]},
            "worst_regions": [],
        },
        "shap_summary": None,
        "fidelity_statement": statement,
        "monotonicity_verified": None,
    }


async def _approximation_version(
    database: Database, workspace_id: UUID, actor_id: UUID, *, transparency: dict[str, Any] | None
) -> RatingVersionRow:
    """A draft `approximation`-mode version over `_approximation_algorithm`, its model with the
    given transparency payload (`None`: the model has no transparency artifact)."""
    async with database.unit_of_work() as session:
        model = ModelRow(
            workspace_id=workspace_id, model_family_slug="fidelity-model", version=1,
            status="draft", dataset_version_id=new_uuid7(),
            spec={"model_family_slug": "fidelity-model"}, spec_hash="v3:sha256:" + "e" * 64,
        )
        session.add(model)
        session.add(
            RatingAlgorithmRow(
                workspace_id=workspace_id, slug="approx-algo", version=1,
                content=_approximation_algorithm(), created_by=actor_id,
            )
        )
        await session.flush()
        if transparency is not None:
            session.add(
                TransparencyArtifactRow(
                    id=new_uuid7(), workspace_id=workspace_id, model_id=model.id,
                    created_at=datetime.now(UTC), job_id=None, payload=transparency,
                )
            )
        version = RatingVersionRow(
            workspace_id=workspace_id, slug="approx-rv", version=1, status="draft",
            dataset_version_id=new_uuid7(), model_ref=_MODEL_REF, created_by=actor_id,
            algorithm_ref="rating_algorithm:approx-algo@1", model_reference_mode="approximation",
        )
        session.add(version)
        await session.flush()
        return version


@pytest.mark.req("FR-224")
@pytest.mark.req("FR-136")
async def test_fr136_precheck_refuses_before_any_run(database: Database, workspace_id) -> None:
    """DP-S5-5 (a): a model referenced in `approximation` mode with no GLM approximation is
    refused `EVIDENCE_INCOMPLETE` naming the model, ahead of any portfolio run."""
    row = await _approximation_version(database, workspace_id, new_uuid7(), transparency=None)
    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await rating_versions_service.approximation_fidelity_statements(
                session, workspace_id=workspace_id, row=row
            )
    assert refused.value.code == "EVIDENCE_INCOMPLETE"
    assert refused.value.status_code == 422
    assert refused.value.detail is not None
    assert _MODEL_REF in refused.value.detail
    assert "FR-136" in refused.value.detail


@pytest.mark.req("FR-136")
async def test_fr136_precheck_returns_the_statements_of_approximated_models(
    database: Database, workspace_id
) -> None:
    row = await _approximation_version(
        database, workspace_id, new_uuid7(), transparency=_glm_payload("94% of deviance.")
    )
    async with database.session() as session:
        statements = await rating_versions_service.approximation_fidelity_statements(
            session, workspace_id=workspace_id, row=row
        )
    assert statements == [f"{_MODEL_REF}: 94% of deviance."]


@pytest.mark.req("FR-224")
async def test_the_exact_twin_resolver_flips_only_model_call_modes() -> None:
    """DP-S5-3 (a): the ephemeral exact-mode twin is the same algorithm with every
    `model_call` in `exact` mode; every other step and every other artifact is untouched."""
    algorithm_ref = ArtifactRef.parse("rating_algorithm:approx-algo@1")
    other_ref = ArtifactRef.parse("model:fidelity-model@1")
    payload = _approximation_algorithm()
    artifacts = {
        algorithm_ref: ResolvedArtifact(status="approved", payload=payload),
        other_ref: ResolvedArtifact(status="approved", payload={"unchanged": True}),
    }

    class _Inner:
        async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
            return artifacts[ref]

    resolver = _ExactModeResolver(_Inner(), algorithm_ref)
    flipped = await resolver.resolve(algorithm_ref)
    modes = {s["step_id"]: s.get("mode") for s in flipped.payload["steps"]}
    assert modes == {"s_in": None, "s_mc": "exact", "s_out": None}
    assert [s for s in flipped.payload["steps"] if s["type"] != "model_call"] == [
        s for s in payload["steps"] if s["type"] != "model_call"
    ]
    assert payload["steps"][1]["mode"] == "approximation"  # the source payload is not mutated
    assert (await resolver.resolve(other_ref)).payload == {"unchanged": True}


# ---- Task 5: FR-224's gate and the threshold (DP-S5-2, RL-1504 item 7) ----------------------

_TWIN_HASH = "sha256:" + "1" * 64


def _figure(value: str | None) -> dict[str, str | None]:
    """A run's quantile map with one figure at every key."""
    return dict.fromkeys(_KEYS, value)


async def _approximation_candidate(gate: _Gate, *, mode: str = "approximation") -> UUID:
    """A compiled first version declared in `mode`; its limb (2) needs no run (no baseline)."""
    await gate.suite(gate.analyst, _suite(_quote()))
    rv_id = await gate.version()
    async with gate.database.unit_of_work() as session:
        row = await rating_versions_service.load_rating_version(
            session, workspace_id=gate.workspace_id, rating_version_id=rv_id
        )
        row.model_reference_mode = mode
    return rv_id


async def _twin_run(gate: _Gate, rv_id: UUID, quantiles: dict[str, str | None] | None) -> UUID:
    """A Dislocation Run naming the version as both baseline and candidate, its baseline bundle
    a different hash from the candidate's (the exact-mode twin)."""
    row = await gate.row(rv_id)
    ref = _ref(row.slug, row.version)
    return await record_dislocation_run(
        gate.database, gate.workspace_id, candidate_ref=ref,
        candidate_hash=str(row.bundle["content_hash"]),  # type: ignore[index]
        baseline_ref=ref, baseline_hash=_TWIN_HASH, actor_id=gate.analyst.id,
        quantiles=quantiles,
    )


def _assert_fr224_refusal(error: PlatformError, *reasons: str) -> None:
    assert error.code == "EVIDENCE_INCOMPLETE"
    assert error.status_code == 422
    assert error.detail is not None
    assert "FR-224" in error.detail
    for reason in reasons:
        assert reason in error.detail, (reason, error.detail)


@pytest.mark.req("FR-224")
async def test_fr224_refuses_an_approximation_version_above_the_threshold(
    database: Database, workspace_id
) -> None:
    """The default threshold is {0.99, 10}: a 0.99-quantile deviation of 10.500000 % is above
    it. The refusal names the quantile and the observed figure; no request is opened."""
    gate = await _gate(database, workspace_id)
    rv_id = await _approximation_candidate(gate)
    await _twin_run(gate, rv_id, _figure("10.500000"))
    before = await _requests_for(database, workspace_id)

    _assert_fr224_refusal(await _refused(gate, rv_id), "0.99 quantile", "10.500000", "10%")
    assert (await gate.row(rv_id)).status == "draft"
    assert await _requests_for(database, workspace_id) == before


@pytest.mark.req("FR-224")
async def test_fr224_refuses_an_approximation_version_with_no_exact_baseline_run(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    rv_id = await _approximation_candidate(gate)
    before = await _requests_for(database, workspace_id)

    _assert_fr224_refusal(await _refused(gate, rv_id), "exact-mode twin")
    assert await _requests_for(database, workspace_id) == before


@pytest.mark.req("FR-224")
async def test_fr224_accepts_inside_the_threshold_and_records_the_figures(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    rv_id = await _approximation_candidate(gate)
    run_id = await _twin_run(gate, rv_id, _figure("10.000000"))  # at the maximum: inside

    await gate.submit(rv_id, dislocation=False)

    row = await gate.row(rv_id)
    assert row.status == "review"
    check = row.evidence["approximation_check"]  # type: ignore[index]
    assert check["dislocation_run_id"] == str(run_id)
    assert Decimal(check["quantile"]) == Decimal("0.99")
    assert Decimal(check["observed_abs_change_pct"]) == Decimal("10")
    assert Decimal(check["max_abs_change_pct"]) == Decimal(10)


@pytest.mark.req("FR-224")
async def test_fr224_does_not_apply_to_an_exact_mode_version(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    rv_id = await _approximation_candidate(gate, mode="exact")

    await gate.submit(rv_id, dislocation=False)

    row = await gate.row(rv_id)
    assert row.status == "review"
    assert "approximation_check" not in row.evidence  # type: ignore[operator]


@pytest.mark.req("FR-224")
async def test_fr224_threshold_ignores_environment_variables(
    database: Database, workspace_id, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`RL-1264` DP-3 (b): the threshold is never read from Settings. With every `GIP_` variable
    a Settings field could map to set permissively, a version above the policy's threshold is
    still refused. Shown red on a gate that reads `load_settings()` (OWED: scratch-reverted)."""
    for name in (
        "GIP_APPROVAL_DEVIATION_THRESHOLD", "GIP_APPROXIMATION_DEVIATION",
        "GIP_APPROXIMATION_MAX_ABS_CHANGE_PCT", "GIP_MAX_ABS_CHANGE_PCT",
        "GIP_DEVIATION_THRESHOLD", "GIP_APPROXIMATION_DEVIATION_QUANTILE",
    ):
        monkeypatch.setenv(name, "1000")
    gate = await _gate(database, workspace_id)
    rv_id = await _approximation_candidate(gate)
    await _twin_run(gate, rv_id, _figure("10.500000"))

    _assert_fr224_refusal(await _refused(gate, rv_id), "10.500000")


async def _set_deviation(
    database: Database, workspace_id: UUID, deviation: dict[str, str] | None
) -> None:
    """Replace the workspace's `rating_version` entry with one carrying `deviation` (`None`:
    the field unset)."""
    entries = [
        entry.model_copy(update={"approximation_deviation": None})
        if entry.artifact_type == "rating_version"
        else entry
        for entry in DEFAULT_POLICY.policies
    ]
    document = ApprovalPolicy(policies=tuple(entries)).model_dump(mode="json")
    for entry in document["policies"]:
        if entry["artifact_type"] == "rating_version" and deviation is not None:
            entry["approximation_deviation"] = deviation
    async with database.unit_of_work() as session:
        session.add(ApprovalPolicyRow(workspace_id=workspace_id, policy=document))


@pytest.mark.req("FR-224")
async def test_fr224_an_unset_threshold_is_governed_by_the_default(
    database: Database, workspace_id
) -> None:
    """RL-1504 item 7: an entry that leaves `approximation_deviation` unset is governed by
    {0.99, 10}, not refused and not ungated: 10.5 % is refused, 9.9 % accepted; a workspace
    entry of {0.99, 5} refuses 9.9 % too. Shown red on a gate reading an unset entry as 'no
    gate' (OWED: scratch-reverted)."""
    gate = await _gate(database, workspace_id)
    await _set_deviation(database, workspace_id, None)
    refused_id = await _approximation_candidate(gate)
    await _twin_run(gate, refused_id, _figure("10.500000"))
    _assert_fr224_refusal(await _refused(gate, refused_id), "10.500000", "10%")

    accepted_id = await gate.version()
    async with gate.database.unit_of_work() as session:
        accepted = await rating_versions_service.load_rating_version(
            session, workspace_id=workspace_id, rating_version_id=accepted_id
        )
        accepted.model_reference_mode = "approximation"
    await _twin_run(gate, accepted_id, _figure("9.900000"))
    await gate.submit(accepted_id, dislocation=False)
    assert (await gate.row(accepted_id)).status == "review"


@pytest.mark.req("FR-224")
async def test_fr224_a_workspace_threshold_replaces_the_default(
    database: Database, workspace_id
) -> None:
    gate = await _gate(database, workspace_id)
    await _set_deviation(database, workspace_id, {"quantile": "0.99", "max_abs_change_pct": "5"})
    rv_id = await _approximation_candidate(gate)
    await _twin_run(gate, rv_id, _figure("9.900000"))  # inside the default, above 5

    _assert_fr224_refusal(await _refused(gate, rv_id), "9.900000", "5%")


@pytest.mark.req("FR-224")
async def test_an_empty_banded_set_has_null_quantiles_and_fr224_refuses(
    database: Database, workspace_id
) -> None:
    """Choice (3), gate half: a twin run whose banded set was empty carries six nulls; the gate
    refuses it, naming the quantile and that the run has no figure, and opens no request. Shown
    red on a gate that reads null as 0 (OWED: scratch-reverted)."""
    gate = await _gate(database, workspace_id)
    rv_id = await _approximation_candidate(gate)
    await _twin_run(gate, rv_id, _figure(None))
    before = await _requests_for(database, workspace_id)

    _assert_fr224_refusal(await _refused(gate, rv_id), "no figure at quantile 0.99")
    assert await _requests_for(database, workspace_id) == before
