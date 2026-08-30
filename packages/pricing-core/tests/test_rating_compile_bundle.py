"""Bundle compilation (slice W9-3) — a pinned version compiles to a self-contained
Bundle with a reproducible hash, and every validation failure is named.

Covers FR-RATE-22 (nothing unpinned), FR-RATE-24 (self-contained Bundle, content hash),
FR-RATE-25 (compilation validates), FR-RATE-60 (mode match), FR-OVR-14 (pins approved).
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from model_schema.rating import RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import (
    ArtifactResolver,
    ResolvedArtifact,
    bundle_hash,
    compile_bundle,
    to_jdm,
)


def valid_algorithm_payload() -> dict:
    """The saved algorithm content — matches the pricing-core save-time fixture."""
    return {
        "slug": "motor-gb",
        "version": 14,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
            {"name": "effective_date", "type": "date", "nullable": False},
            {"name": "channel", "type": "enum", "domain": ["direct", "broker"], "nullable": False},
        ],
        "outputs": [
            {"name": "payable_premium_minor", "type": "money_minor", "required": True},
        ],
        "steps": [
            {"step_id": "s_in_age", "type": "input", "label": "Driver age",
             "input_name": "driver_age", "on_missing": "error", "produces": "driver_age"},
            {"step_id": "s_in_eff", "type": "input", "label": "Effective date",
             "input_name": "effective_date", "on_missing": "error", "produces": "effective_date"},
            {"step_id": "s_in_channel", "type": "input", "label": "Channel",
             "input_name": "channel", "on_missing": "error", "produces": "channel"},
            {"step_id": "s_area", "type": "lookup", "label": "Area",
             "reference_table_ref": "reference_table:ons-postcode-directory@7",
             "key_expr": ["channel"], "as_at": "effective_date", "on_miss": "error",
             "consumes": ["channel", "effective_date"], "produces": "rating_area"},
            {"step_id": "s_rp", "type": "model_call", "label": "Risk premium",
             "model_ref": "model:motor-ad-frequency@7", "mode": "exact",
             "feature_map": {"driver_age": "driver_age", "rating_area": "rating_area"},
             "consumes": ["driver_age", "rating_area"],
             "produces": ["risk_premium_minor", "peril_risk_premium"]},
            {"step_id": "s_expense", "type": "table", "label": "Expense",
             "rate_table_ref": "rate_table:motor-expense@3", "key_expr": ["channel"],
             "on_miss": "default", "consumes": ["channel"], "produces": "expense_factor"},
            {"step_id": "s_office", "type": "expression", "label": "Office premium",
             "expr": "risk_premium_minor * expense_factor", "result_type": "money_minor",
             "consumes": ["risk_premium_minor", "expense_factor"],
             "produces": "office_premium_minor"},
            {"step_id": "s_out", "type": "output", "label": "Payable premium",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["office_premium_minor"]},
        ],
        "sub_graphs": [],
    }


def _version(status: str = "draft") -> RatingVersion:
    return RatingVersion.model_validate({
        "id": str(uuid4()),
        "workspace_id": str(uuid4()),
        "slug": "motor-gb",
        "version": 27,
        "status": status,
        "dataset_version_id": str(uuid4()),
        "model_ref": "model:motor-ad-frequency@7",
        "created_at": "2026-08-27T12:00:00Z",
        "created_by": str(uuid4()),
        "updated_at": "2026-08-27T12:00:00Z",
        "algorithm_ref": "rating_algorithm:motor-gb@14",
        "pins": {
            "rate_tables": ["rate_table:motor-expense@3"],
            "models": ["model:motor-ad-frequency@7"],
            "reference_tables": ["reference_table:ons-postcode-directory@7"],
            "custom_objectives": [],
        },
        "model_reference_mode": "exact",
    })


class FakeResolver:
    """A synchronous test resolver: every ref resolves to `approved` with its payload."""

    def __init__(self, payloads: dict[str, dict], statuses: dict[str, str] | None = None):
        self._payloads = payloads
        self._statuses = statuses or {}

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        key = str(ref)
        return ResolvedArtifact(
            status=self._statuses.get(key, "approved"),
            payload=self._payloads[key],
        )


def _resolver() -> ArtifactResolver:
    model_payload = {
        "model_type": "gbm",
        "status": "approved",
        "feature_map": {"driver_age": "driver_age", "rating_area": "rating_area"},
    }
    return FakeResolver(
        {
            "rating_algorithm:motor-gb@14": valid_algorithm_payload(),
            "rate_table:motor-expense@3": {"rateable": True, "rows": []},
            "model:motor-ad-frequency@7": model_payload,
            "reference_table:ons-postcode-directory@7": {"rows": []},
        }
    )


@pytest.mark.req("FR-RATE-24")
async def test_a_pinned_version_compiles_to_a_self_contained_bundle() -> None:
    """FR-RATE-24: the Bundle carries the graph and the resolved payloads."""
    bundle = await compile_bundle(_version(), _resolver())
    assert bundle.algorithm_ref == "rating_algorithm:motor-gb@14"
    assert bundle.graph.slug == "motor-gb"
    assert bundle.content_hash.startswith("sha256:")
    # self-contained: the resolved payloads are embedded, so scoring needs no DB.
    assert "model:motor-ad-frequency@7" in bundle.resolved_payloads
    assert bundle.resolved_payloads["model:motor-ad-frequency@7"]["status"] == "approved"


@pytest.mark.req("FR-RATE-24")
async def test_the_content_hash_is_reproducible() -> None:
    """FR-RATE-24: compiling the same pins and graph yields the same hash."""
    first = await compile_bundle(_version(), _resolver())
    second = await compile_bundle(_version(), _resolver())
    assert first.content_hash == second.content_hash
    # and bundle_hash is a pure function of the graph and pins
    assert bundle_hash(first.graph, first.pins) == first.content_hash


@pytest.mark.req("FR-RATE-22")
async def test_an_unpinned_version_is_refused() -> None:
    """FR-RATE-22: nothing unpinned — a version with no algorithm_ref fails."""
    version = _version().model_copy(update={"algorithm_ref": None})
    with pytest.raises(ValueError, match="RATING_VERSION_UNPINNED"):
        await compile_bundle(version, _resolver())


@pytest.mark.req("FR-OVR-14")
@pytest.mark.req("FR-RATE-25")
async def test_an_unapproved_pin_is_refused() -> None:
    """FR-OVR-14: a pin whose artifact is not approved fails, naming the pin.

    Targets the `model` pin rather than `rate_table`: Ruling 22
    (`docs/plans/2026-08-29-w11-1-2-rate-table-maturity-ruling.md`) exempts
    `rate_table` from this floor (`_MATURITY_CHECK_EXEMPT`), so it can no longer be the
    example that proves the gate fires.

    Also FR-RATE-25's own clause (2) ("references resolvable and at a sufficient
    maturity") — F-W9-3's cheap half (`docs/audit/register.md`), pointing the
    already-run mechanism at the umbrella requirement rather than writing a new test for
    it (`docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`).
    """
    resolver = _resolver()
    resolver._statuses["model:motor-ad-frequency@7"] = "draft"
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED"):
        await compile_bundle(_version(), resolver)


@pytest.mark.req("FR-OVR-14")
async def test_a_rate_table_pin_compiles_regardless_of_status() -> None:
    """Ruling 22: `rate_table` is exempt from the FR-OVR-14 floor, not a fourth member
    of `_APPROVED_OR_BETTER` — the gate is bypassed for the type, not satisfied by it.

    Proves the exemption is real rather than incidental: the resolver reports a status
    no member of `_APPROVED_OR_BETTER` would ever admit, and the pin still compiles.
    That the real `_Resolver.resolve` never invents an approved-sounding value for
    `rate_table` is a separate guarantee, held by that branch's own comment and by
    `test_rate_table_version_row_has_no_status_column`
    (`backend/tests/test_rating_version_compile.py`), not by this test.
    """
    resolver = _resolver()
    resolver._statuses["rate_table:motor-expense@3"] = "no_maturity_concept"
    bundle = await compile_bundle(_version(), resolver)
    assert "rate_table:motor-expense@3" in bundle.resolved_payloads


@pytest.mark.req("FR-RATE-25")
async def test_a_rating_algorithm_pin_compiles_regardless_of_status() -> None:
    """Ruling 28 (`docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`): `rating_algorithm`
    is exempt from the FR-OVR-14 floor for the same shape of reason Ruling 22 exempted
    `rate_table` — `RatingAlgorithmRow` has no status column to read a real maturity from
    (`test_rating_algorithm_row_has_no_status_column`,
    `backend/tests/test_rating_version_compile.py`), so the real resolver reports the
    `"no_maturity_concept"` sentinel rather than inventing `"approved"`. Proves the
    exemption is real rather than incidental, the same way
    `test_a_rate_table_pin_compiles_regardless_of_status` does for `rate_table`: the
    resolver reports a status no member of `_APPROVED_OR_BETTER` would ever admit, and the
    pin still compiles.
    """
    resolver = _resolver()
    resolver._statuses["rating_algorithm:motor-gb@14"] = "no_maturity_concept"
    bundle = await compile_bundle(_version(), resolver)
    assert bundle.algorithm_ref == "rating_algorithm:motor-gb@14"


@pytest.mark.req("FR-RATE-25")
async def test_the_algorithm_maturity_check_would_be_caught_if_removed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Proves Ruling 28's algorithm-maturity check is live code, not a declared-and-inert
    control (`06` FR-GOV-39's own language for exactly this defect — a member of an
    exemption set that nothing reads).

    Removing `rating_algorithm` from `_MATURITY_CHECK_EXEMPT` must turn an unapproved
    algorithm status into the same `PIN_NOT_APPROVED` refusal the loop below already
    raises for every other pin kind — proving the check, not merely a test that has never
    been seen to fail (`CLAUDE.md` §13).
    """
    import pricing_core.rating.compile as compile_module

    monkeypatch.setattr(compile_module, "_MATURITY_CHECK_EXEMPT", frozenset({"rate_table"}))
    resolver = _resolver()
    resolver._statuses["rating_algorithm:motor-gb@14"] = "draft"
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED"):
        await compile_bundle(_version(), resolver)


@pytest.mark.req("FR-RATE-60")
async def test_a_mode_mismatch_is_refused_at_compile() -> None:
    """FR-RATE-60: a model_call mode disagreeing with the version fails compilation."""
    version = _version().model_copy(update={"model_reference_mode": "approximation"})
    with pytest.raises(ValueError, match="FR-RATE-60"):
        await compile_bundle(version, _resolver())


@pytest.mark.req("FR-RATE-25")
async def test_a_broken_guard_fails_compilation_with_a_named_error() -> None:
    """FR-RATE-25: a boundary-guard violation re-checked at compile is named."""
    payload = valid_algorithm_payload()
    for step in payload["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor / expense_factor"  # unguarded division
    resolver = FakeResolver(
        {
            "rating_algorithm:motor-gb@14": payload,
            "rate_table:motor-expense@3": {"rateable": True, "rows": []},
            "model:motor-ad-frequency@7": {"status": "approved"},
            "reference_table:ons-postcode-directory@7": {"rows": []},
        }
    )
    with pytest.raises(ValueError, match="EXPRESSION_UNGUARDED_DIVISION"):
        await compile_bundle(_version(), resolver)


@pytest.mark.req("FR-RATE-24")
def test_to_jdm_translates_the_steps() -> None:
    """to_jdm names the nodes and edges of the DAG."""
    from model_schema.rating import RatingAlgorithm

    algo = RatingAlgorithm.model_validate(valid_algorithm_payload())
    graph = to_jdm(algo)
    assert graph.slug == "motor-gb"
    assert len(graph.nodes) == 8
    assert graph.nodes["s_office"]["type"] == "expression"
    assert graph.nodes["s_office"]["consumes"] == ["risk_premium_minor", "expense_factor"]
