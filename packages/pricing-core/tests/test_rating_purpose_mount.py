"""WK-1250 Slice 3 (SL-1341): FR-218's purpose mount and the real check (RL-1344, RL-1628).

Red first (`PL-1629` Tasks 3 and 4, acceptance 4 to 7). A purpose mount is a `sub_graphs`
entry with `purposes`; in that purpose's graph it RE-PRODUCES a parent name (DP-S3-1 (d)):
here the cancellation mount reads `expense_factor` and re-produces it halved, so the ladder
and the payable of a cancellation are the adjusted figures. Each purpose evaluates its own
graph and algorithm (DP-S3-2 (a) and condition 1).

The fixtures reuse `test_rating_score.py`'s (`_FakeResolver`, `_version`, `_ctx`), so a quote
here is priced by the same algorithm as the golden test there (payable 1507).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import polars as pl
import pytest
from test_rating_score import _ctx, _FakeResolver, _version
from test_rating_score_batch import _ctx_to_row

from model_schema.rating import RatingAlgorithm
from model_schema.refs import ArtifactRef
from model_schema.sub_graphs import SubGraph
from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.inline import inline_mounts
from pricing_core.rating.runtime import CompiledBundle, load_bundle
from pricing_core.rating.score import score_batch, score_one

_CANCEL_REF = "sub_graph:cancel-refund@1"
_NEW_BUSINESS_PAYABLE = 1_507  # the golden quote of `test_rating_score.py`


def _cancel_clamp_fragment_payload() -> dict[str, Any]:
    """A mount that only clamps the office premium it is handed (a re-producing clamp)."""
    return {
        "slug": "cancel-refund",
        "version": 1,
        "inputs": [{"name": "annual", "type": "money_minor"}],
        "outputs": [{"name": "refund", "type": "money_minor", "required": True}],
        "steps": [
            {
                "step_id": "s_clamp",
                "type": "constraint",
                "label": "Cancellation cap",
                "condition": "annual <= 1000",
                "on_violation": "clamp",
                "clamp_bounds": {"max": "1000"},
                "reason_code": "CANCEL_CLAMP",
                "consumes": ["annual"],
                "produces": "refund",
            }
        ],
        "change_note": "first cut",
    }


def _cancel_fragment_payload(*, decline: bool) -> dict[str, Any]:
    steps: list[dict[str, Any]] = [
        {
            "step_id": "s_prorata",
            "type": "expression",
            "label": "Pro-rata",
            "expr": "annual * 0.5",
            "result_type": "decimal",
            "consumes": ["annual"],
            "produces": "refund",
        },
    ]
    if decline:
        # Violated whenever it is evaluated (the condition is false for any positive refund).
        steps.append(
            {
                "step_id": "s_guard",
                "type": "constraint",
                "label": "Cancellation guard",
                "condition": "refund < 0",
                "on_violation": "decline",
                "reason_code": "CANCEL_GUARD",
                "consumes": ["refund"],
            }
        )
    return {
        "slug": "cancel-refund",
        "version": 1,
        "inputs": [{"name": "annual", "type": "decimal"}],
        "outputs": [{"name": "refund", "type": "decimal", "required": True}],
        "steps": steps,
        "change_note": "first cut",
    }


async def _compiled_with_a_mount(
    purposes: list[str] | None, *, decline: bool = False, clamp: bool = False
) -> CompiledBundle:
    return load_bundle(await _bundle_with_a_mount(purposes, decline=decline, clamp=clamp))


async def _bundle_with_a_mount(  # type: ignore[no-untyped-def]
    purposes: list[str] | None,
    *,
    decline: bool = False,
    clamp: bool = False,
    pinned: tuple[str, ...] = (_CANCEL_REF,),
):
    resolver = _FakeResolver()
    algorithm = resolver._payloads["rating_algorithm:score-fixture@1"]
    mount: dict[str, Any] = {
        "ref": _CANCEL_REF,
        "mount_point": "m_cancel",
        "inputs": {"annual": "office_premium_minor" if clamp else "expense_factor"},
        "outputs": {"refund": "office_premium_minor" if clamp else "expense_factor"},
    }
    if purposes is not None:
        mount["purposes"] = purposes
    algorithm["sub_graphs"] = [mount]
    if clamp:
        # Two re-producers of one name form a cycle (each depends on the other), so the mount's
        # clamp REPLACES the base minimum-premium clamp: the base graph has no clamp, the
        # cancellation graph has the mount's.
        algorithm["steps"] = [st for st in algorithm["steps"] if st["step_id"] != "s_clamp"]
    resolver._payloads[_CANCEL_REF] = (
        _cancel_clamp_fragment_payload() if clamp else _cancel_fragment_payload(decline=decline)
    )
    version = _version()
    pins = version.pins
    assert pins is not None
    version = version.model_copy(
        update={
            "pins": pins.model_copy(
                update={"sub_graphs": [ArtifactRef.parse(ref) for ref in pinned]}
            ),
        }
    )
    return await compile_bundle(version, resolver)


def _ladder_ids(result: Any) -> list[tuple[str, int]]:
    return [(r.rung, r.value_minor) for r in result.premium_ladder]


# --- fixture soundness: the same mount, unconditional, compiles and prices today ---------------


@pytest.mark.req("FR-217")
async def test_the_fixture_prices_new_business_with_an_unconditional_re_producing_mount() -> None:
    """Control: not red. The unconditional form of the fixture is valid today, so a red below
    is the purpose behaviour's absence, not a broken fixture."""
    compiled = await _compiled_with_a_mount(None)
    result = await score_one(compiled, _ctx(purpose="new_business"))
    assert result.outcome == "quoted"
    assert result.outputs["payable_premium_minor"] < _NEW_BUSINESS_PAYABLE  # halved factor


# --- acceptance 4: the real check -------------------------------------------------------------


@pytest.mark.req("FR-218")
@pytest.mark.parametrize("purpose", ["mid_term_adjustment", "cancellation"])
async def test_a_version_with_only_an_unconditional_mount_is_refused_by_the_real_check(
    purpose: str,
) -> None:
    """RL-1344 section 3: refused unless the bundle inlines a mount for THIS purpose. The
    message says no mount for the purpose is inlined, and no longer says "interim"."""
    compiled = await _compiled_with_a_mount(None)
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION") as refused:
        await score_one(compiled, _ctx(purpose=purpose))
    message = str(refused.value)
    assert "interim" not in message
    assert purpose in message
    assert "no mount" in message
    assert "inlined" in message


@pytest.mark.req("FR-218")
async def test_a_cancellation_only_mount_refuses_a_mid_term_adjustment_quote() -> None:
    """Acceptance 4 / 5: not bypassable. The cancellation mount does not price the other
    purpose, and the refusal is the real check's."""
    compiled = await _compiled_with_a_mount(["cancellation"])
    with pytest.raises(ValueError, match="INPUT_CONTRACT_VIOLATION") as refused:
        await score_one(compiled, _ctx(purpose="mid_term_adjustment"))
    assert "interim" not in str(refused.value)
    assert "mid_term_adjustment" in str(refused.value)


@pytest.mark.req("FR-218")
async def test_a_cancellation_only_mount_prices_a_cancellation_with_the_mount() -> None:
    """Acceptance 4 and RL-1628 acceptance 1: the cancellation payable is the adjusted figure."""
    compiled = await _compiled_with_a_mount(["cancellation"])
    result = await score_one(compiled, _ctx(purpose="cancellation"), trace=True)
    assert result.outcome == "quoted"
    payable = result.outputs["payable_premium_minor"]
    assert 0 < payable < _NEW_BUSINESS_PAYABLE
    assert result.trace is not None
    assert result.trace.ladder_reconciled is True
    assert "m_cancel__s_prorata" in {s.step_id for s in result.trace.steps}


@pytest.mark.req("FR-218")
async def test_a_cancellation_only_mount_leaves_new_business_exactly_as_without_it() -> None:
    """Acceptance 4, third bullet: the same payable, the same ladder, the same trace step ids,
    and none of the cancellation mount's steps (acceptance 5: absent from another purpose)."""
    from test_rating_score import _compiled

    with_mount = await score_one(
        await _compiled_with_a_mount(["cancellation"]), _ctx(purpose="new_business"), trace=True
    )
    without = await score_one(await _compiled(), _ctx(purpose="new_business"), trace=True)
    assert with_mount.outputs["payable_premium_minor"] == _NEW_BUSINESS_PAYABLE
    assert with_mount.outputs == without.outputs
    assert _ladder_ids(with_mount) == _ladder_ids(without)
    assert with_mount.trace is not None
    assert without.trace is not None
    with_ids = [s.step_id for s in with_mount.trace.steps]
    assert with_ids == [s.step_id for s in without.trace.steps]


@pytest.mark.req("FR-218")
async def test_a_constraint_inside_a_cancellation_mount_is_evaluated_for_it() -> None:
    """RL-1628 condition 1: the purpose's own algorithm is what is read. A decline constraint
    inside the mount is in no base-algorithm read, so only a selector that returns the
    cancellation algorithm lets the quote be declined with its reason."""
    compiled = await _compiled_with_a_mount(["cancellation"], decline=True)
    cancelled = await score_one(compiled, _ctx(purpose="cancellation"))
    assert cancelled.outcome == "declined"
    assert cancelled.decline_reasons == ["CANCEL_GUARD"]
    new_business = await score_one(compiled, _ctx(purpose="new_business"))
    assert new_business.outcome == "quoted"


@pytest.mark.req("FR-218")
async def test_a_clamp_inside_a_cancellation_mount_appears_in_the_cancellation_ladder() -> None:
    """RL-1628 DP-S3-2 condition 1, red first as the maintainer ruled it (to-lead 2026-10-17
    13:58:04 BST, F5 (b)): a cancellation mount containing a clamping `constraint` step, whose
    clamp appears in the cancellation quote's ladder. The clamp is in no base-algorithm read,
    so a selector that returned the base algorithm would price the cancellation with no clamp
    in its ladder."""
    compiled = await _compiled_with_a_mount(["cancellation"], clamp=True)
    cancelled = await score_one(compiled, _ctx(purpose="cancellation"), trace=True)
    assert cancelled.outcome == "quoted"
    constraints = next(r for r in cancelled.premium_ladder if r.rung == "constraints")
    assert constraints.operation is not None
    assert constraints.operation.kind == "clamp"
    assert constraints.operation.applied == ["CANCEL_CLAMP"]
    assert cancelled.trace is not None
    assert cancelled.trace.ladder_reconciled is True
    new_business = await score_one(compiled, _ctx(purpose="new_business"), trace=True)
    assert new_business.outcome == "quoted"
    assert new_business.outputs["payable_premium_minor"] == _NEW_BUSINESS_PAYABLE
    assert "CANCEL_CLAMP" not in str(new_business.premium_ladder)


@pytest.mark.req("FR-218")
async def test_removing_the_real_check_would_be_caught(monkeypatch: pytest.MonkeyPatch) -> None:
    """Acceptance 5: with the check neutralised the MTA quote is priced silently, so the
    refusal test above is the only thing standing between the quote and a mispricing."""
    import pricing_core.rating.score as score_module

    monkeypatch.setattr(score_module, "_check_purpose_mount", lambda *args, **kwargs: None)
    compiled = await _compiled_with_a_mount(["cancellation"])
    result = await score_one(compiled, _ctx(purpose="mid_term_adjustment"))
    assert result.outcome == "quoted"


# --- Task 3: the bundle per purpose -----------------------------------------------------------


@pytest.mark.req("FR-218")
@pytest.mark.req("FR-239")
async def test_compile_bundle_emits_a_graph_for_exactly_the_selected_purposes() -> None:
    bundle = await _bundle_with_a_mount(["cancellation"])
    assert set(bundle.purpose_graphs) == {"cancellation"}
    assert set(bundle.purpose_graphs["cancellation"].nodes) != set(bundle.graph.nodes)
    both = await _bundle_with_a_mount(["mid_term_adjustment", "cancellation"])
    assert set(both.purpose_graphs) == {"mid_term_adjustment", "cancellation"}
    unconditional = await _bundle_with_a_mount(None)
    assert unconditional.purpose_graphs == {}


@pytest.mark.req("FR-218")
@pytest.mark.req("FR-239")
async def test_a_change_to_purposes_alone_changes_the_content_hash() -> None:
    """RL-1344 acceptance 5, hash half."""
    one = await _bundle_with_a_mount(["cancellation"])
    other = await _bundle_with_a_mount(["mid_term_adjustment"])
    assert one.content_hash != other.content_hash


@pytest.mark.req("FR-239")
async def test_a_version_with_no_purpose_mount_keeps_the_hash_it_had() -> None:
    """DP-S3-2 (a): `purpose_graphs` is hashed only when non-empty. An unconditional mount's
    bundle hash is the hash of its graph and pins alone, as at Slice 2."""
    from pricing_core.rating.compile import bundle_hash

    bundle = await _bundle_with_a_mount(None)
    assert bundle.content_hash == bundle_hash(bundle.graph, bundle.pins)


# --- SL-1341 pre-gate audit A-1 / A-4 (LG 8056): the batch path and the serialised bytes -------


@pytest.mark.req("FR-218")
async def test_a_batch_row_under_a_purpose_mount_is_priced_by_the_purposes_graph() -> None:
    """A-1, acceptance 4's batch path (`score_batch` -> `_score_context_sync`/`_score_batch_row`):
    a cancellation row is priced by the cancellation graph (the payable `score_one` gives, below
    new business), a new-business row by the base graph (1507), and a mid-term adjustment row,
    which no mount serves, is that row's error row naming the purpose, never the base price."""
    compiled = await _compiled_with_a_mount(["cancellation"])
    contexts = [
        _ctx(quote_id="C1", purpose="cancellation"),
        _ctx(quote_id="N1", purpose="new_business"),
        _ctx(quote_id="M1", purpose="mid_term_adjustment"),
    ]
    frame = pl.DataFrame([_ctx_to_row(c) for c in contexts]).lazy()
    rows = {r["quote_id"]: r for r in score_batch(compiled, frame).collect().to_dicts()}

    single = await score_one(compiled, _ctx(quote_id="C1", purpose="cancellation"))
    cancelled = json.loads(rows["C1"]["outputs_json"])["payable_premium_minor"]
    assert rows["C1"]["outcome"] == "quoted"
    assert 0 < cancelled < _NEW_BUSINESS_PAYABLE
    assert cancelled == single.outputs["payable_premium_minor"]
    assert json.loads(rows["N1"]["outputs_json"])["payable_premium_minor"] == _NEW_BUSINESS_PAYABLE
    assert rows["M1"]["outcome"] == "error"
    assert rows["M1"]["outputs_json"] is None
    assert "mid_term_adjustment" in (rows["M1"]["error_message"] or "")


@pytest.mark.req("FR-218")
async def test_a_batch_row_reads_the_purposes_algorithm_for_its_decision() -> None:
    """A-1: the decline constraint lives only inside the cancellation mount, so a batch
    cancellation row is declined with its reason only if the batch path reads the purpose's
    algorithm (`bundle.evaluation_for(ctx.purpose)`), and a new-business row is not."""
    compiled = await _compiled_with_a_mount(["cancellation"], decline=True)
    frame = pl.DataFrame(
        [
            _ctx_to_row(_ctx(quote_id="C1", purpose="cancellation")),
            _ctx_to_row(_ctx(quote_id="N1", purpose="new_business")),
        ]
    ).lazy()
    rows = {r["quote_id"]: r for r in score_batch(compiled, frame).collect().to_dicts()}
    assert rows["C1"]["outcome"] == "declined"
    assert rows["N1"]["outcome"] == "quoted"


@pytest.mark.req("FR-239")
async def test_the_serialised_bytes_of_a_bundle_with_no_purpose_mount_omit_the_key() -> None:
    """A-4 (LG 8056): `bundle_hash`'s default is not the proof (see the test above); the stored
    bytes are. An empty `purpose_graphs` is absent from the JSON and from the python dump, the
    bundle still round-trips, and a bundle that does select a purpose carries the key."""
    from pricing_core.rating.compile import Bundle

    bundle = await _bundle_with_a_mount(None)
    assert bundle.purpose_graphs == {}
    assert "purpose_graphs" not in json.loads(bundle.model_dump_json())
    assert "purpose_graphs" not in bundle.model_dump()
    assert Bundle.model_validate_json(bundle.model_dump_json()) == bundle
    selected = await _bundle_with_a_mount(["cancellation"])
    assert set(json.loads(selected.model_dump_json())["purpose_graphs"]) == {"cancellation"}
    # The hash of an unconditional-mount bundle is the sha256 of the pre-slice canonical form
    # (graph and pins only), computed here from the serialised bytes, not by `bundle_hash`.
    bundle = await _bundle_with_a_mount(None)
    pins = bundle.pins.model_dump()
    if not pins["sub_graphs"]:
        pins.pop("sub_graphs")
    canonical = json.dumps(
        {"graph": bundle.graph.model_dump(), "pins": pins}, sort_keys=True, separators=(",", ":")
    )
    assert bundle.content_hash == "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


@pytest.mark.req("FR-218")
@pytest.mark.req("FR-243")
async def test_load_bundle_refuses_a_purpose_graph_that_disagrees_with_its_algorithm() -> None:
    """RL-1628 condition 2 (C1 per purpose graph): `BUNDLE_COMPILE_FAILED`."""
    bundle = await _bundle_with_a_mount(["cancellation"])
    graph = bundle.purpose_graphs["cancellation"]
    nodes = dict(graph.nodes)
    nodes["m_cancel__renamed"] = nodes.pop("m_cancel__s_prorata")
    tampered = bundle.model_copy(
        update={
            "purpose_graphs": {"cancellation": graph.model_copy(update={"nodes": nodes})},
        }
    )
    with pytest.raises(ValueError, match="BUNDLE_COMPILE_FAILED") as raised:
        load_bundle(tampered)
    assert "m_cancel__" in str(raised.value)


# --- Task 3: the inliner's `purpose` argument -------------------------------------------------


def _purpose_parent() -> RatingAlgorithm:
    """`factor` has one producer; the cancellation mount reads it and re-produces it."""
    return RatingAlgorithm.model_validate(
        {
            "slug": "motor-gb",
            "version": 1,
            "input_contract": [{"name": "years_clean", "type": "int", "nullable": False}],
            "outputs": [{"name": "premium", "type": "decimal", "required": True}],
            "steps": [
                {
                    "step_id": "s_in_years",
                    "type": "input",
                    "label": "Years",
                    "input_name": "years_clean",
                    "on_missing": "error",
                    "produces": "years_clean",
                },
                {
                    "step_id": "s_factor",
                    "type": "expression",
                    "label": "Factor",
                    "expr": "years_clean * 10",
                    "result_type": "decimal",
                    "consumes": ["years_clean"],
                    "produces": "factor",
                },
                {
                    "step_id": "s_out",
                    "type": "output",
                    "label": "Premium",
                    "output_name": "premium",
                    "rounding": {"mode": "half_even", "dp": 0},
                    "consumes": ["factor"],
                },
            ],
            "sub_graphs": [
                {
                    "ref": _CANCEL_REF,
                    "mount_point": "m_cancel",
                    "purposes": ["cancellation"],
                    "inputs": {"annual": "factor"},
                    "outputs": {"refund": "factor"},
                }
            ],
        }
    )


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-218")
def test_inline_mounts_inlines_a_purpose_mount_for_its_purpose_only() -> None:
    """`purpose=None` inlines unconditional mounts only (Slice 2's behaviour, the default)."""
    fragments: dict[str, SubGraph] = {
        _CANCEL_REF: SubGraph.model_validate(_cancel_fragment_payload(decline=False))
    }
    parent = _purpose_parent()
    base = inline_mounts(parent, fragments, purpose=None)
    cancellation = inline_mounts(parent, fragments, purpose="cancellation")
    other = inline_mounts(parent, fragments, purpose="mid_term_adjustment")
    assert not any(s.step_id.startswith("m_cancel__") for s in base.steps)
    assert not any(s.step_id.startswith("m_cancel__") for s in other.steps)
    ids = [s.step_id for s in cancellation.steps]
    # The re-producing step reads the parent's `factor` and re-produces it before the output.
    assert "m_cancel__s_prorata" in ids
    assert ids.index("s_factor") < ids.index("m_cancel__s_prorata") < ids.index("s_out")
