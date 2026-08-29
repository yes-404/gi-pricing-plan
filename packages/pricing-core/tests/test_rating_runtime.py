"""`CompiledBundle`, `load_bundle`, and the JDM wire translation (W11 Task 1.3, FR-RATE-65).

Covers: the round trip from a real `compile_bundle()` output through `load_bundle` to a
live `zen.ZenDecision` that actually evaluates (Task 1.3 Step 1); the boundary that
`CompiledBundle` is never serialised (Step 5); Ruling 8's one-deserialisation property;
Ruling 10's two properties (`content_hash` exposure, cache purity); the `constraint` and
`interpolation="linear"` scope cuts this module's own docstring names; and a focused
`to_wire`-only test for a `lookup` step's decision-table translation.
"""

from __future__ import annotations

import dataclasses
import json
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
import xgboost as xgb
from pydantic import BaseModel

from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.modelling.gbm import load_gbm_booster
from pricing_core.rating.compile import ArtifactResolver, ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle, to_wire


def _train_tiny_booster() -> bytes:
    """A real, tiny, fitted XGBoost booster — one feature, `age_years` (W11 Task 1.3's own
    fixture; not `fit_gbm`'s output, since this test is about the runtime seam, not
    fitting)."""
    x = [[20.0], [30.0], [40.0], [50.0], [60.0]]
    y = [1000.0, 1200.0, 1500.0, 1800.0, 2000.0]
    dtrain = xgb.DMatrix(x, label=y, feature_names=["age_years"])
    params = {"objective": "reg:squarederror", "max_depth": 2}
    booster = xgb.train(params, dtrain, num_boost_round=3)
    return bytes(booster.save_raw(raw_format="json"))


def _gbm_model_payload(booster_bytes: bytes, *, model_type: str = "xgboost") -> dict[str, Any]:
    """A `model:...` resolved payload shaped like Task 1.2's `_Resolver` produces it:
    the `Model` dump's `fit_result`, plus `booster_content` — the booster's own JSON/text
    form carried *inside* the payload rather than as a blob reference (Ruling 7)."""
    return {
        "model_family_slug": "motor-freq",
        "version": 1,
        "status": "approved",
        "fit_result": {
            "model_type": model_type,
            "booster_blob": {
                "sha256": "a" * 64, "bytes": len(booster_bytes), "media_type": "application/json",
            },
            "booster_format": "xgboost_json",
            "feature_order": ["age_years"],
            "feature_dtypes": {},
            "categorical_maps": {},
            "monotone_constraints": [],
            "base_margin": {"kind": "none"},
            "best_iteration": 3,
            "inverse_link": None,
            "rows": 5,
            "fit_seconds": 0.01,
            "library_versions": {},
            "dropped_eval_metrics": [],
            "booster_content": booster_bytes.decode("utf-8"),
        },
    }


def _glm_model_payload() -> dict[str, Any]:
    """A GLM `model:...` payload — enough to reach the dispatch, not enough (deliberately;
    see `runtime.py`'s `_raise_model_call_failed`) to be scored."""
    return {
        "model_family_slug": "motor-freq-glm",
        "version": 1,
        "status": "approved",
        "fit_result": {"model_type": "glm", "converged": True, "iterations": 5, "fit_seconds": 0.01,
                       "coefficients": []},
    }


def _rate_table_payload() -> dict[str, Any]:
    return {
        "slug": "motor-expense", "version": 1, "rateable": True, "storage": "rows",
        "keys": [{"name": "channel", "type": "string", "banding_ref": None}],
        "value": {
            "name": "expense_factor", "type": "relativity", "unit": "factor",
            "min": None, "max": None,
        },
        "default_row": None,
        "rows": [
            {"channel": "direct", "expense_factor": "1.1"},
            {"channel": "broker", "expense_factor": "1.25"},
        ],
    }


def _algorithm_payload(*, model_ref: str = "model:motor-freq@1") -> dict[str, Any]:
    """Input -> table -> model_call -> expression -> output. Exercises every step type
    Task 1.3's `to_wire` translates (`constraint` deliberately excluded — see the module
    docstring's scope cut)."""
    return {
        "slug": "motor-runtime-test",
        "version": 1,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
            {"name": "channel", "type": "enum", "domain": ["direct", "broker"], "nullable": False},
        ],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in_age", "type": "input", "label": "Driver age",
             "input_name": "driver_age", "on_missing": "error", "produces": "driver_age"},
            {"step_id": "s_in_channel", "type": "input", "label": "Channel",
             "input_name": "channel", "on_missing": "error", "produces": "channel"},
            {"step_id": "s_expense", "type": "table", "label": "Expense factor",
             "rate_table_ref": "rate_table:motor-expense@1", "key_expr": ["channel"],
             "on_miss": "error", "interpolation": "none",
             "consumes": ["channel"], "produces": "expense_factor"},
            {"step_id": "s_risk", "type": "model_call", "label": "Risk premium",
             "model_ref": model_ref, "mode": "exact",
             "feature_map": {"driver_age": "age_years"},
             "consumes": ["driver_age"], "produces": ["risk_premium_minor"]},
            {"step_id": "s_office", "type": "expression", "label": "Office premium",
             "expr": "risk_premium_minor * expense_factor", "result_type": "money_minor",
             "consumes": ["risk_premium_minor", "expense_factor"],
             "produces": "office_premium_minor"},
            {"step_id": "s_out", "type": "output", "label": "Payable premium",
             "output_name": "payable_premium_minor",
             "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["office_premium_minor"]},
        ],
        "sub_graphs": [],
    }


def _algorithm_payload_with_constraint() -> dict[str, Any]:
    payload = _algorithm_payload()
    payload["steps"].append(
        {"step_id": "s_guard", "type": "constraint", "label": "Sanity cap",
         "condition": "office_premium_minor > 0", "on_violation": "decline",
         "reason_code": "SANITY_CAP", "consumes": ["office_premium_minor"]}
    )
    return payload


def _version(*, glm: bool = False) -> RatingVersion:
    return RatingVersion.model_validate({
        "id": str(uuid4()),
        "workspace_id": str(uuid4()),
        "slug": "motor-runtime-test",
        "version": 1,
        "status": "draft",
        "dataset_version_id": str(uuid4()),
        "model_ref": "model:motor-freq-glm@1" if glm else "model:motor-freq@1",
        "created_at": "2026-08-29T12:00:00Z",
        "created_by": str(uuid4()),
        "updated_at": "2026-08-29T12:00:00Z",
        "algorithm_ref": "rating_algorithm:motor-runtime-test@1",
        "pins": {
            "rate_tables": ["rate_table:motor-expense@1"],
            "models": ["model:motor-freq-glm@1"] if glm else ["model:motor-freq@1"],
            "reference_tables": [],
            "custom_objectives": [],
        },
        "model_reference_mode": "exact",
    })


class _FakeResolver:
    def __init__(self, *, glm: bool = False, with_constraint: bool = False) -> None:
        booster = _train_tiny_booster()
        model_ref = "model:motor-freq-glm@1" if glm else "model:motor-freq@1"
        algo = (
            _algorithm_payload_with_constraint()
            if with_constraint
            else _algorithm_payload(model_ref=model_ref)
        )
        self._payloads: dict[str, dict[str, Any]] = {
            "rating_algorithm:motor-runtime-test@1": algo,
            "rate_table:motor-expense@1": _rate_table_payload(),
            "model:motor-freq@1": _gbm_model_payload(booster),
            "model:motor-freq-glm@1": _glm_model_payload(),
        }

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=self._payloads[str(ref)])


async def _compiled(*, glm: bool = False, with_constraint: bool = False) -> CompiledBundle:
    resolver: ArtifactResolver = _FakeResolver(glm=glm, with_constraint=with_constraint)
    bundle = await compile_bundle(_version(glm=glm), resolver)
    return load_bundle(bundle)


# ---------------------------------------------------------------------------
# Step 1: the round trip through the real compile_bundle() path.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-65")
async def test_a_real_bundle_loads_and_evaluates() -> None:
    """The Bundle today's compile path produces evaluates through a real engine handle."""
    compiled = await _compiled()
    out = await compiled.decision.async_evaluate({"driver_age": 34, "channel": "direct"})
    assert out["result"], "the engine returned no outputs"


@pytest.mark.req("FR-RATE-65")
async def test_the_premium_ladder_reconciles_end_to_end() -> None:
    """NFR-RATE-8's shape, on this task's own scoring path: every rung the DAG computes
    (not only the terminal output) survives into the result, and applying the table
    factor to the model's prediction reproduces the declared output exactly."""
    compiled = await _compiled()
    out = await compiled.decision.async_evaluate({"driver_age": 34, "channel": "direct"})
    result = out["result"]
    assert "risk_premium_minor" in result, "the model_call's own output did not survive"
    assert "expense_factor" in result, "the table lookup's own output did not survive"
    # The engine's own arithmetic is plain float64 (FR-RATE-56) — nothing here rounds an
    # intermediate rung, that is Task 1.4's job when it builds the actual premium ladder.
    # `==` is not used: the engine's internal float64 multiplication and this same
    # multiplication redone in Python are not bit-identical (verified: they differ by
    # ~2e-13 on this fixture) — a cross-implementation float comparison, not a reconciliation
    # failure, which is exactly why NFR-RATE-8's real check (Task 1.4) is a tolerance.
    expected = result["risk_premium_minor"] * float(result["expense_factor"])
    assert result["office_premium_minor"] == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Step 5: CompiledBundle is provably not serialisable.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-65")
async def test_a_compiled_bundle_cannot_be_serialised() -> None:
    """FR-RATE-65: never itself serialised. Assert the boundary rather than assume it."""
    compiled = await _compiled()
    with pytest.raises(TypeError):
        json.dumps(dataclasses.asdict(compiled))
    assert not isinstance(compiled, BaseModel)


# ---------------------------------------------------------------------------
# Ruling 10: content_hash exposure and cache purity.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-65")
async def test_compiled_bundle_exposes_its_source_content_hash() -> None:
    """Ruling 10 clause (i): without this, FR-RATE-51's "never a mix" is unverifiable."""
    resolver: ArtifactResolver = _FakeResolver()
    bundle = await compile_bundle(_version(), resolver)
    compiled = load_bundle(bundle)
    assert compiled.content_hash == bundle.content_hash


@pytest.mark.req("FR-RATE-65")
async def test_load_bundle_is_pure_with_respect_to_any_cache() -> None:
    """Ruling 10 clause (ii), and Ruling 16's own acceptance test for it: called twice on
    the same Bundle, load_bundle returns two distinct objects. Identical objects would
    mean a cache had been put inside pricing_core, which .importlinter's
    core-has-no-infrastructure contract already forbids at the import level — this is the
    behavioural half, expressible the moment load_bundle exists, not only once Slice 2
    builds a holding tier above it.
    """
    resolver: ArtifactResolver = _FakeResolver()
    bundle = await compile_bundle(_version(), resolver)
    first = load_bundle(bundle)
    second = load_bundle(bundle)
    assert first is not second
    assert first.decision is not second.decision
    assert first.boosters["model:motor-freq@1"] is not second.boosters["model:motor-freq@1"]


# ---------------------------------------------------------------------------
# Ruling 8: exactly one booster deserialisation across N scorings.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-65")
async def test_scoring_n_quotes_deserialises_the_booster_once_not_n(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ruling 8's acceptance test, stated as the violation: written to fail against a
    handler that re-loads the booster from bytes on every call (the pre-Task-1.3
    behaviour) and to pass against one that scores through `CompiledBundle.boosters`'s
    already-loaded object. Verified by making the failure happen first: temporarily
    calling `load_gbm_booster` inside the per-quote path (simulated below by counting
    calls across N evaluations of one already-loaded CompiledBundle) must stay at the
    hydration count, not grow with N.
    """
    calls = 0
    real = load_gbm_booster

    def counting(*args: Any, **kwargs: Any) -> object:
        nonlocal calls
        calls += 1
        return real(*args, **kwargs)

    # Two call sites, not one: `_load_boosters` (runtime.py) holds its own imported name
    # bound at import time, and `predict_gbm` (gbm.py) looks the name up fresh in its own
    # module's namespace on every call — patching only the former would leave a per-call
    # fallback through the latter invisible to this counter (verified: an earlier version
    # of this test patched runtime.py alone and stayed green even when the handler was
    # made to pass raw bytes to `predict_gbm` on every call, because `predict_gbm`'s own
    # `load_gbm_booster` reference was untouched).
    monkeypatch.setattr("pricing_core.rating.runtime.load_gbm_booster", counting)
    monkeypatch.setattr("pricing_core.modelling.gbm.load_gbm_booster", counting)

    compiled = await _compiled()
    assert calls == 1, "load_bundle itself must deserialise the booster exactly once"

    for _ in range(5):
        out = await compiled.decision.async_evaluate({"driver_age": 40, "channel": "broker"})
        assert out["result"]["risk_premium_minor"]

    assert calls == 1, (
        "scoring 5 quotes against one CompiledBundle deserialised the booster "
        f"{calls} times, not once — Ruling 8's seam was bypassed"
    )


# ---------------------------------------------------------------------------
# Scope cuts this module's own docstring names, each proven rather than assumed.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-RATE-65")
def test_to_wire_refuses_a_constraint_step() -> None:
    """A `constraint` step's decline/clamp semantics are Ruling 9's / Task 1.4's to
    design; to_wire raises rather than guessing at untested business logic."""
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.compile import to_jdm

    algo = RatingAlgorithm.model_validate(_algorithm_payload_with_constraint())
    graph = to_jdm(algo)
    with pytest.raises(NotImplementedError, match="constraint"):
        to_wire(graph)


@pytest.mark.req("FR-RATE-65")
async def test_a_glm_model_call_is_refused_with_a_named_code() -> None:
    """`predict_glm` needs real Factor objects the Bundle does not carry (see
    `runtime.py`'s `_raise_model_call_failed` docstring) — refused loudly, not silently
    mis-scored. Through `async_evaluate()` this surfaces as `zen`'s own generic node-error
    wrapper, not the handler's `MODEL_CALL_FAILED` message — a verified finding, not an
    oversight (see `_raise_model_call_failed`'s docstring): the binding discards whatever a
    `customHandler` raises. The handler itself, called directly, still raises the named
    `ValueError` intact — asserted second, so this test would fail if a future change
    stopped raising it internally even though `evaluate()` cannot show that from outside.
    """
    resolver = _FakeResolver(glm=True)
    bundle = await compile_bundle(_version(glm=True), resolver)
    compiled = load_bundle(bundle)

    with pytest.raises(RuntimeError, match="Failed to run custom node handler"):
        await compiled.decision.async_evaluate({"driver_age": 34, "channel": "direct"})

    from pricing_core.rating.runtime import _model_call_handler

    handler = _model_call_handler(compiled.algorithm, bundle.resolved_payloads, compiled.boosters)
    fake_request = SimpleNamespace(node={"id": "s_risk"}, input={"driver_age": 34, "$nodes": {}})

    with pytest.raises(ValueError, match="MODEL_CALL_FAILED"):
        handler(fake_request)


@pytest.mark.req("FR-RATE-65")
def test_to_wire_refuses_table_interpolation() -> None:
    """Exact-match rows only — see the module docstring's `interpolation` gap."""
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.compile import to_jdm

    payload = _algorithm_payload()
    for step in payload["steps"]:
        if step["step_id"] == "s_expense":
            step["interpolation"] = "linear"
    algo = RatingAlgorithm.model_validate(payload)
    graph = to_jdm(algo)
    with pytest.raises(NotImplementedError, match="interpolation"):
        to_wire(graph, {"rate_table:motor-expense@1": _rate_table_payload()})


# ---------------------------------------------------------------------------
# A focused, to_wire-only test for the `lookup` (reference table) translation — not
# routed through compile_bundle, since a reference table's resolver shape is Task 1.2's
# and this is purely about to_wire's own decisionTableNode construction (exact key match,
# no as_at windowing — see the module docstring).
# ---------------------------------------------------------------------------


def test_lookup_step_wire_translation_matches_by_key() -> None:
    algo_payload = {
        "slug": "lookup-only", "version": 1,
        "input_contract": [{"name": "postcode", "type": "string", "nullable": False}],
        "outputs": [{"name": "rating_area", "type": "string", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "Postcode",
             "input_name": "postcode", "on_missing": "error", "produces": "postcode"},
            {"step_id": "s_area", "type": "lookup", "label": "Area",
             "reference_table_ref": "reference_table:ons@1", "key_expr": ["postcode"],
             "as_at": "postcode", "on_miss": "error",
             "consumes": ["postcode"], "produces": "area_code"},
            {"step_id": "s_out", "type": "output", "label": "Area out",
             "output_name": "rating_area", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["area_code"]},
        ],
        "sub_graphs": [],
    }
    from model_schema.rating import RatingAlgorithm
    from pricing_core.rating.compile import to_jdm

    algo = RatingAlgorithm.model_validate(algo_payload)
    graph = to_jdm(algo)
    payloads = {
        "reference_table:ons@1": {
            "rows": [
                {"key": "SW1A", "payload": {"area_code": "LDN"},
                 "effective_from": "2020-01-01", "effective_to": None},
                {"key": "M1", "payload": {"area_code": "MAN"},
                 "effective_from": "2020-01-01", "effective_to": None},
            ]
        }
    }
    wire = to_wire(graph, payloads)

    import zen

    decision = zen.ZenEngine().create_decision(json.dumps(wire))
    decision.validate()
    assert decision.evaluate({"postcode": "SW1A"})["result"]["area_code"] == "LDN"
    assert decision.evaluate({"postcode": "M1"})["result"]["area_code"] == "MAN"
