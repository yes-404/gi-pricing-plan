"""Bundle compilation (slice W9-3) — a pinned version compiles to a self-contained
Bundle with a reproducible hash, and every validation failure is named.

Covers FR-237 (nothing unpinned), FR-239 (self-contained Bundle, content hash),
FR-240 (compilation validates), FR-223 (mode match), FR-20 (pins approved).
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


@pytest.mark.req("FR-239")
async def test_a_pinned_version_compiles_to_a_self_contained_bundle() -> None:
    """FR-239: the Bundle carries the graph and the resolved payloads."""
    bundle = await compile_bundle(_version(), _resolver())
    assert bundle.algorithm_ref == "rating_algorithm:motor-gb@14"
    assert bundle.graph.slug == "motor-gb"
    assert bundle.content_hash.startswith("sha256:")
    # self-contained: the resolved payloads are embedded, so scoring needs no DB.
    assert "model:motor-ad-frequency@7" in bundle.resolved_payloads
    assert bundle.resolved_payloads["model:motor-ad-frequency@7"]["status"] == "approved"


@pytest.mark.req("FR-239")
async def test_the_content_hash_is_reproducible() -> None:
    """FR-239: compiling the same pins and graph yields the same hash."""
    first = await compile_bundle(_version(), _resolver())
    second = await compile_bundle(_version(), _resolver())
    assert first.content_hash == second.content_hash
    # and bundle_hash is a pure function of the graph and pins
    assert bundle_hash(first.graph, first.pins) == first.content_hash


@pytest.mark.req("FR-237")
async def test_an_unpinned_version_is_refused() -> None:
    """FR-237: nothing unpinned — a version with no algorithm_ref fails."""
    version = _version().model_copy(update={"algorithm_ref": None})
    with pytest.raises(ValueError, match="RATING_VERSION_UNPINNED"):
        await compile_bundle(version, _resolver())


@pytest.mark.req("FR-20")
@pytest.mark.req("FR-240")
async def test_an_unapproved_pin_is_refused() -> None:
    """FR-20: a pin whose artifact is not approved fails, naming the pin.

    Targets the `model` pin rather than `rate_table`: RL-856
    (`docs/rulings/RL-00856-the-resolver-reports-no-maturity-for-a-rate-table-and-the-exemption-is-declared-and-self-invalidating.md`)
    exempts `rate_table` from this floor (`_MATURITY_CHECK_EXEMPT`), so it can no longer be the
    example that proves the gate fires.

    Also FR-240's own clause (2) ("references resolvable and at a sufficient
    maturity") — F-W9-3's cheap half (`docs/findings/register.md`), pointing the
    already-run mechanism at the umbrella requirement rather than writing a new test for
    it (`docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`).
    """
    resolver = _resolver()
    resolver._statuses["model:motor-ad-frequency@7"] = "draft"
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED"):
        await compile_bundle(_version(), resolver)


@pytest.mark.req("FR-20")
async def test_a_rate_table_pin_compiles_regardless_of_status() -> None:
    """RL-856: `rate_table` is exempt from the FR-20 floor, not a fourth member
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


@pytest.mark.req("FR-240")
async def test_a_rating_algorithm_pin_compiles_regardless_of_status() -> None:
    """RL-859 (`docs/rulings/RL-00859-the-remainder-splits-and-the-split-is-the-answer.md`):
    `rating_algorithm`
    is exempt from the FR-20 floor for the same shape of reason RL-856 exempted
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


@pytest.mark.req("FR-240")
async def test_the_algorithm_maturity_check_would_be_caught_if_removed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Proves RL-859's algorithm-maturity check is live code, not a declared-and-inert
    control (`06` FR-367's own language for exactly this defect — a member of an
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


@pytest.mark.req("FR-223")
async def test_a_mode_mismatch_is_refused_at_compile() -> None:
    """FR-223: a model_call mode disagreeing with the version fails compilation."""
    version = _version().model_copy(update={"model_reference_mode": "approximation"})
    with pytest.raises(ValueError, match="FR-223"):
        await compile_bundle(version, _resolver())


@pytest.mark.req("FR-240")
async def test_a_broken_guard_fails_compilation_with_a_named_error() -> None:
    """FR-240: a boundary-guard violation re-checked at compile is named."""
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


@pytest.mark.req("FR-239")
def test_to_jdm_translates_the_steps() -> None:
    """to_jdm names the nodes and edges of the DAG."""
    from model_schema.rating import RatingAlgorithm

    algo = RatingAlgorithm.model_validate(valid_algorithm_payload())
    graph = to_jdm(algo)
    assert graph.slug == "motor-gb"
    assert len(graph.nodes) == 8
    assert graph.nodes["s_office"]["type"] == "expression"
    assert graph.nodes["s_office"]["consumes"] == ["risk_premium_minor", "expense_factor"]


# --- WK-1250 Slice 2 (SL-1340): a pinned sub-graph is resolved, checked and inlined -------------
# (FR-217; RL-1309 G1, G4, DP-3 item 5, DP-4, DP-S1-4 item 6; RL 9586 DP-S2-2)

import copy  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
from typing import Any  # noqa: E402

from pricing_core.rating import compile as compile_module  # noqa: E402

NCD = "sub_graph:ncd-ladder@4"
NCD5 = "sub_graph:ncd-ladder@5"


def _fragment_payload(version: int = 4, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "slug": "ncd-ladder", "version": version,
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_ladder", "type": "expression", "label": "Ladder",
             "expr": "ncd_years * 10", "result_type": "decimal",
             "consumes": ["ncd_years"], "produces": "ncd_factor"},
        ],
        "change_note": "first cut",
    }
    payload.update(overrides)
    return payload


def _mounted_payload(**mount_edit: Any) -> dict[str, Any]:
    """`valid_algorithm_payload()` with an NCD input, the mount, and `s_office` consuming it."""
    payload = copy.deepcopy(valid_algorithm_payload())
    payload["input_contract"].append(
        {"name": "ncd_years", "type": "int", "nullable": False, "min": 0, "max": 9}
    )
    payload["steps"].insert(
        0,
        {"step_id": "s_in_ncd", "type": "input", "label": "NCD years",
         "input_name": "ncd_years", "on_missing": "error", "produces": "ncd_years"},
    )
    for step in payload["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor * expense_factor * ncd_factor"
            step["consumes"] = ["risk_premium_minor", "expense_factor", "ncd_factor"]
    payload["sub_graphs"] = [{
        "ref": NCD, "mount_point": "m_ncd",
        "inputs": {"ncd_years": "ncd_years"}, "outputs": {"ncd_factor": "ncd_factor"},
        **mount_edit,
    }]
    return payload


def _mounted_version(pinned: tuple[str, ...] = (NCD,)) -> RatingVersion:
    version = _version()
    pins = version.pins
    assert pins is not None
    return version.model_copy(update={
        "pins": pins.model_copy(update={"sub_graphs": [ArtifactRef.parse(r) for r in pinned]}),
    })


def _mounted_resolver(
    algorithm: dict[str, Any] | None = None,
    fragments: dict[str, dict[str, Any]] | None = None,
) -> FakeResolver:
    base = _resolver()
    assert isinstance(base, FakeResolver)
    payloads = dict(base._payloads)
    payloads["rating_algorithm:motor-gb@14"] = algorithm or _mounted_payload()
    for ref, payload in (fragments or {NCD: _fragment_payload()}).items():
        payloads[ref] = payload
    return FakeResolver(payloads, {ref: "no_maturity_concept" for ref in (NCD, NCD5)})


@pytest.mark.req("FR-217")
async def test_a_pinned_mount_is_inlined_namespaced_and_carried_in_the_bundle() -> None:
    bundle = await compile_bundle(_mounted_version(), _mounted_resolver())
    assert "m_ncd__s_ladder" in bundle.graph.nodes
    assert bundle.graph.nodes["m_ncd__s_ladder"]["produces"] == ["ncd_factor"]
    assert bundle.resolved_payloads[NCD]["slug"] == "ncd-ladder"
    # The stored algorithm artifact is the un-inlined payload the ref names (RL-873).
    assert bundle.resolved_payloads["rating_algorithm:motor-gb@14"]["sub_graphs"]
    assert bundle.pins.sub_graphs == [ArtifactRef.parse(NCD)]


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-237")
async def test_g1_a_mount_whose_version_is_not_pinned_is_refused_with_no_steps() -> None:
    with pytest.raises(ValueError, match="RATING_VERSION_UNPINNED") as raised:
        await compile_bundle(_mounted_version(pinned=()), _mounted_resolver())
    assert "m_ncd" in str(raised.value)


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-237")
async def test_g1_a_mount_pinned_at_another_version_is_refused() -> None:
    with pytest.raises(ValueError, match="RATING_VERSION_UNPINNED"):
        await compile_bundle(
            _mounted_version(pinned=(NCD5,)),
            _mounted_resolver(fragments={NCD: _fragment_payload(), NCD5: _fragment_payload(5)}),
        )


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-237")
@pytest.mark.parametrize("step", [
    {"step_id": "s_tab", "type": "table", "label": "t", "rate_table_ref": "rate_table:other@1",
     "key_expr": ["ncd_years"], "consumes": ["ncd_years"], "produces": "ncd_factor"},
    {"step_id": "s_tab", "type": "lookup", "label": "l",
     "reference_table_ref": "reference_table:other@1", "key_expr": ["ncd_years"],
     "as_at": "effective_date", "on_miss": "error", "consumes": ["ncd_years"],
     "produces": "ncd_factor"},
    {"step_id": "s_tab", "type": "model_call", "label": "m", "model_ref": "model:other@1",
     "mode": "exact", "feature_map": {}, "consumes": ["ncd_years"], "produces": "ncd_factor"},
])
async def test_g1_a_fragment_reference_the_version_does_not_pin_is_refused(
    step: dict[str, Any],
) -> None:
    fragment = _fragment_payload(steps=[step])
    with pytest.raises(ValueError, match="RATING_VERSION_UNPINNED") as raised:
        await compile_bundle(_mounted_version(), _mounted_resolver(fragments={NCD: fragment}))
    assert "m_ncd__s_tab" in str(raised.value)


@pytest.mark.req("FR-217")
@pytest.mark.parametrize(("mount_edit", "code"), [
    ({"inputs": {}}, "RATING_GRAPH_UNRESOLVED_REF"),
    ({"inputs": {"ncd_years": "ncd_years", "ghost": "ncd_years"}}, "RATING_GRAPH_UNRESOLVED_REF"),
    ({"outputs": {"ghost": "ncd_factor"}}, "RATING_GRAPH_UNRESOLVED_REF"),
    ({"inputs": {"ncd_years": "channel"}}, "RATING_TYPE_MISMATCH"),
])
async def test_the_port_map_is_checked_against_the_pinned_versions_ports(
    mount_edit: dict[str, Any], code: str
) -> None:
    payload = _mounted_payload(**mount_edit)
    with pytest.raises(ValueError, match=code):
        await compile_bundle(_mounted_version(), _mounted_resolver(algorithm=payload))


@pytest.mark.req("FR-217")
async def test_dp4_a_pinned_payload_that_mounts_another_is_refused_by_cause() -> None:
    nested = _fragment_payload(sub_graphs=[{"ref": NCD5, "mount_point": "m_inner"}])
    with pytest.raises(ValueError, match="VALIDATION_FAILED"):
        await compile_bundle(_mounted_version(), _mounted_resolver(fragments={NCD: nested}))


@pytest.mark.req("FR-216")
@pytest.mark.req("FR-274")
@pytest.mark.req("FR-275")
@pytest.mark.req("FR-276")
@pytest.mark.parametrize(("expr", "code"), [
    ("ncd_years * 10 + now()", "EXPRESSION_NON_DETERMINISTIC"),
    ("ncd_years / 2", "EXPRESSION_UNGUARDED_DIVISION"),
    ("ncd_years * 0.12345678901234567890123456789", "EXPRESSION_SCALE_OVERFLOW"),
    ("ncd_years % 2", "EXPRESSION_INVALID_VOCABULARY"),
])
async def test_the_save_time_checks_run_over_the_inlined_algorithm(expr: str, code: str) -> None:
    """DP-S1-4 item 6: a fragment saved at create is refused when a mounting algorithm compiles."""
    step = {"step_id": "s_ladder", "type": "expression", "label": "Ladder", "expr": expr,
            "result_type": "decimal", "consumes": ["ncd_years"], "produces": "ncd_factor"}
    fragment = _fragment_payload(steps=[step])
    with pytest.raises(ValueError, match=code):
        await compile_bundle(_mounted_version(), _mounted_resolver(fragments={NCD: fragment}))


@pytest.mark.req("FR-217")
async def test_a_namespacing_collision_is_refused_never_merged() -> None:
    payload = _mounted_payload()
    payload["input_contract"].append({"name": "m_ncd__s_ladder", "type": "int", "nullable": False})
    payload["steps"].insert(
        0,
        {"step_id": "s_in_clash", "type": "input", "label": "x", "input_name": "m_ncd__s_ladder",
         "on_missing": "error", "produces": "m_ncd__s_ladder"},
    )
    with pytest.raises(ValueError, match="VALIDATION_FAILED"):
        await compile_bundle(_mounted_version(), _mounted_resolver(algorithm=payload))


@pytest.mark.req("FR-239")
@pytest.mark.req("FR-217")
async def test_the_hash_covers_the_pinned_fragment() -> None:
    """Move only the pinned sub-graph version (the mount's ref and the pin together)."""
    fragments = {NCD: _fragment_payload(), NCD5: _fragment_payload(5)}
    first = await compile_bundle(_mounted_version(), _mounted_resolver(fragments=fragments))
    again = await compile_bundle(_mounted_version(), _mounted_resolver(fragments=fragments))
    moved = await compile_bundle(
        _mounted_version(pinned=(NCD5,)),
        _mounted_resolver(algorithm=_mounted_payload(ref=NCD5), fragments=fragments),
    )
    assert first.content_hash == again.content_hash
    assert moved.content_hash != first.content_hash


@pytest.mark.req("FR-239")
async def test_a_version_that_pins_no_sub_graph_hashes_exactly_as_before() -> None:
    """The pre-Slice-2 formula: `Pins` had four lists, so `sub_graphs` is not in the hash when
    empty and every existing bundle's `content_hash` stays reproducible from its pins."""
    bundle = await compile_bundle(_version(), _resolver())
    pins = bundle.pins.model_dump()
    assert pins.pop("sub_graphs") == []
    canonical = json.dumps(
        {"graph": bundle.graph.model_dump(), "pins": pins},
        sort_keys=True, separators=(",", ":"),
    )
    assert bundle.content_hash == "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


@pytest.mark.req("FR-20")
@pytest.mark.req("FR-240")
async def test_g4_a_sub_graph_pin_compiles_regardless_of_status_and_the_exemption_is_declared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RL-1309 DP-1 item 5: a Sub-graph Version has no approval lifecycle, so `sub_graph` joins
    `_MATURITY_CHECK_EXEMPT`; remove it and the same pin is refused with `PIN_NOT_APPROVED`."""
    resolver = _mounted_resolver()
    bundle = await compile_bundle(_mounted_version(), resolver)
    assert NCD in bundle.resolved_payloads
    assert "sub_graph" in compile_module._MATURITY_CHECK_EXEMPT
    monkeypatch.setattr(
        compile_module, "_MATURITY_CHECK_EXEMPT", frozenset({"rate_table", "rating_algorithm"})
    )
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED"):
        await compile_bundle(_mounted_version(), resolver)
