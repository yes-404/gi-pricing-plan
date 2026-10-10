"""Rating Algorithm contract (W9-1, 03 §4.1) — shape, invariants, structural diff.

Covers FR-212 (DAG invariants), FR-213 (input contract), FR-214 (outputs),
FR-215 (stable step_id), FR-217 (sub-graphs), FR-219 (structural diff),
FR-222 (model_call mode), FR-226 (output rounding), FR-227 (money types).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from model_schema.rating import (
    RatingAlgorithm,
    RatingConstraintStep,
    RatingExpressionStep,
    RatingInputStep,
    RatingLookupStep,
    RatingModelCallStep,
    RatingOutputStep,
    RatingTableStep,
    diff_algorithms,
)


def valid_algorithm() -> dict:
    """A consistent seven-step graph: inputs -> lookup -> model_call/table -> expr
    -> constraint (clamp chain) -> output. Every consumed name is produced by an
    upstream step; the constraint re-produces `office_premium_minor` in place.
    """
    return {
        "slug": "motor-gb",
        "version": 14,
        "input_contract": [
            {"name": "driver_age", "type": "int", "nullable": False, "min": 17, "max": 99},
            {"name": "effective_date", "type": "date", "nullable": False},
            {"name": "channel", "type": "enum", "domain": ["direct", "broker"], "nullable": False},
            {"name": "min_premium_minor", "type": "int", "nullable": False},
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
            {"step_id": "s_in_min_premium", "type": "input", "label": "Minimum premium",
             "input_name": "min_premium_minor", "on_missing": "error",
             "produces": "min_premium_minor"},
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
            {"step_id": "s_minprem", "type": "constraint", "label": "Min premium",
             "condition": "office_premium_minor >= min_premium_minor",
             "on_violation": "clamp", "clamp_bounds": {"min": "min_premium_minor"},
             "reason_code": "MIN_PREMIUM_APPLIED",
             "consumes": ["office_premium_minor", "min_premium_minor"],
             "produces": "office_premium_minor"},
            {"step_id": "s_out", "type": "output", "label": "Payable premium",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["office_premium_minor"]},
        ],
        "sub_graphs": [{"ref": "sub_graph:ncd-ladder@4", "mount_point": "s_ncd"}],
    }


@pytest.mark.req("FR-212")
@pytest.mark.req("FR-213")
@pytest.mark.req("FR-215")
@pytest.mark.req("FR-217")
def test_a_valid_algorithm_parses() -> None:
    """T1: the §4.1 shape accepts a consistent graph with all seven step types.

    Covers FR-212 (the shape is a DAG of steps that passes its invariants),
    FR-213 (the typed input contract), FR-215 (step_id is a stable identifier,
    distinct from the label), FR-217 (the sub-graph references and mount points).
    """
    algorithm = RatingAlgorithm.model_validate(valid_algorithm())
    assert algorithm.slug == "motor-gb"
    assert algorithm.version == 14
    assert len(algorithm.steps) == 10
    assert algorithm.sub_graphs[0].ref.type == "sub_graph"
    assert algorithm.sub_graphs[0].mount_point == "s_ncd"
    types = {type(step).__name__ for step in algorithm.steps}
    assert {
        "RatingInputStep", "RatingLookupStep", "RatingTableStep",
        "RatingExpressionStep", "RatingModelCallStep", "RatingConstraintStep",
        "RatingOutputStep",
    } <= types
    # FR-213: each input carries a name, a type, nullability, and a range or domain.
    age = algorithm.input_contract[0]
    assert age.name == "driver_age"
    assert age.type.value == "int"
    assert age.nullable is False
    assert age.min == 17
    assert age.max == 99
    channel = algorithm.input_contract[2]
    assert channel.domain == ["direct", "broker"]
    # FR-215: a step's id is a separate, stable identifier, never derived from its
    # human label — renaming the label cannot change the id.
    for step in algorithm.steps:
        assert step.step_id != step.label


@pytest.mark.req("FR-220")
@pytest.mark.req("FR-221")
@pytest.mark.req("FR-222")
@pytest.mark.req("FR-225")
@pytest.mark.req("FR-226")
def test_the_seven_step_types_accept_their_key_fields() -> None:
    """T1: each step type carries the key fields from 03 §3.2.

    Covers FR-220 (table steps pin a rate table), FR-221 (lookup steps evaluate
    as at a declared date), FR-222 (model_call declares a mode), FR-225
    (constraint steps carry a reason code), FR-226 (output steps declare rounding).
    """
    algorithm = RatingAlgorithm.model_validate(valid_algorithm())
    by_id = {s.step_id: s for s in algorithm.steps}

    assert isinstance(by_id["s_in_age"], RatingInputStep)
    assert by_id["s_in_age"].on_missing == "error"

    assert isinstance(by_id["s_area"], RatingLookupStep)
    assert by_id["s_area"].as_at == "effective_date"
    assert by_id["s_area"].on_miss == "error"

    assert isinstance(by_id["s_rp"], RatingModelCallStep)
    assert by_id["s_rp"].mode == "exact"
    assert by_id["s_rp"].feature_map == {"driver_age": "driver_age", "rating_area": "rating_area"}

    assert isinstance(by_id["s_expense"], RatingTableStep)
    assert by_id["s_expense"].interpolation == "none"

    assert isinstance(by_id["s_office"], RatingExpressionStep)
    assert by_id["s_office"].result_type == "money_minor"

    assert isinstance(by_id["s_minprem"], RatingConstraintStep)
    assert by_id["s_minprem"].on_violation == "clamp"
    assert by_id["s_minprem"].reason_code == "MIN_PREMIUM_APPLIED"

    assert isinstance(by_id["s_out"], RatingOutputStep)
    assert by_id["s_out"].rounding.mode == "half_even"
    assert by_id["s_out"].rounding.dp == 0


@pytest.mark.req("FR-227")
def test_a_monetary_result_typed_as_float_is_refused() -> None:
    """T1: FR-227 — money is `decimal` or `money_minor`, never float."""
    data = valid_algorithm()
    data["outputs"] = [{"name": "premium", "type": "float", "required": True}]
    with pytest.raises(ValidationError, match="never float"):
        RatingAlgorithm.model_validate(data)

    data = valid_algorithm()
    data["steps"][6] = {
        **data["steps"][6], "result_type": "float",
    }
    with pytest.raises(ValidationError, match="never float"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-222")
def test_a_model_call_declares_exactly_one_reference() -> None:
    """T1: FR-222 — a model_call pins a model or a peril structure, not both."""
    data = valid_algorithm()
    data["steps"][4] = {
        **data["steps"][4],
        "model_ref": "model:motor-ad-frequency@7",
        "peril_structure_ref": "peril_structure:motor-gb-2026h2@2",
    }
    with pytest.raises(ValidationError, match="exactly one of model_ref or peril_structure_ref"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-212")
@pytest.mark.req("FR-240")
def test_a_cycle_is_refused() -> None:
    """T2: FR-212 — a cyclic graph fails.

    Also FR-240's own clause (1) ("the DAG is acyclic") — F-W9-3's cheap half
    (`docs/findings/register.md`). `compile_bundle` calls `RatingAlgorithm.model_validate`
    on the resolved payload before anything else, so this shape-level check is already
    the mechanism FR-240 relies on for the acyclic half of clause (1), and this test
    is pointed at the umbrella requirement rather than a new one being written
    (`docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`).
    """
    data = valid_algorithm()
    # s_office consumes cycle_val (produced by the constraint) while the constraint
    # consumes office_premium_minor (produced by s_office): a genuine two-step cycle
    # that still leaves the declared output reachable.
    data["steps"][6] = {
        **data["steps"][6],
        "consumes": ["risk_premium_minor", "expense_factor", "cycle_val"],
        "produces": "office_premium_minor",
    }
    data["steps"][7] = {
        **data["steps"][7],
        "consumes": ["office_premium_minor"],
        "produces": "cycle_val",
    }
    with pytest.raises(ValidationError, match="cycle"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-212")
def test_an_undefined_reference_is_refused() -> None:
    """T2: FR-212 — a consumed name no step produces fails."""
    data = valid_algorithm()
    data["steps"][6] = {
        **data["steps"][6],
        "consumes": ["no_such_value"], "produces": "office_premium_minor",
    }
    with pytest.raises(ValidationError, match="undefined value"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-214")
def test_a_missing_output_step_is_refused() -> None:
    """T2: FR-214 — every declared output has an output step."""
    data = valid_algorithm()
    data["outputs"].append({"name": "extra_output", "type": "money_minor", "required": False})
    with pytest.raises(ValidationError, match="has no output step"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-212")
@pytest.mark.req("FR-240")
def test_an_orphaned_step_is_refused() -> None:
    """T2: FR-212 — a step neither reachable from an input nor feeding an output.

    Also FR-240's own clause (1) ("the DAG is ... fully connected") — F-W9-3's cheap
    half (`docs/findings/register.md`), pointing the already-run mechanism at the umbrella
    requirement (`docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`).
    """
    data = valid_algorithm()
    data["steps"].append({
        "step_id": "s_orphan", "type": "expression", "label": "Orphan",
        "expr": "1", "result_type": "decimal",
        "consumes": [], "produces": "orphan_value",
    })
    with pytest.raises(ValidationError, match="unreachable from any input"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-219")
def test_the_diff_names_added_removed_and_changed_steps() -> None:
    """T3: FR-219 — the structural diff names each change."""
    old = RatingAlgorithm.model_validate(valid_algorithm())
    new_data = valid_algorithm()
    # remove the constraint, change the expression's label and expr, add a step.
    new_data["steps"] = [s for s in new_data["steps"] if s["step_id"] != "s_minprem"]
    for step in new_data["steps"]:
        if step["step_id"] == "s_office":
            step["label"] = "Office premium (revised)"
            step["expr"] = "risk_premium_minor * expense_factor * 1.1"
    new_data["steps"].append({
        "step_id": "s_extra", "type": "expression", "label": "Extra",
        "expr": "office_premium_minor", "result_type": "money_minor",
        "consumes": ["office_premium_minor"], "produces": "extra_minor",
    })
    new = RatingAlgorithm.model_validate(new_data)

    diff = diff_algorithms(old, new)
    assert "s_extra" in diff.added_steps
    assert "s_minprem" in diff.removed_steps
    changed = {c.step_id for c in diff.changed_steps}
    assert "s_office" in changed
    fields = {c.field for c in diff.changed_steps if c.step_id == "s_office"}
    assert {"label", "expr"} <= fields
    assert "no structural change" not in diff.summary


@pytest.mark.req("FR-219")
def test_the_diff_names_a_repointed_table() -> None:
    """T3: FR-219 — a table step whose rate table changed is named as re-pointed."""
    old = RatingAlgorithm.model_validate(valid_algorithm())
    new_data = valid_algorithm()
    for step in new_data["steps"]:
        if step["step_id"] == "s_expense":
            step["rate_table_ref"] = "rate_table:motor-expense@4"
    new = RatingAlgorithm.model_validate(new_data)

    diff = diff_algorithms(old, new)
    assert len(diff.repointed_tables) == 1
    repoint = diff.repointed_tables[0]
    assert repoint.step_id == "s_expense"
    assert repoint.field == "rate_table_ref"
    assert str(repoint.before) == "rate_table:motor-expense@3"
    assert str(repoint.after) == "rate_table:motor-expense@4"


@pytest.mark.req("FR-1399")
def test_diff_algorithms_reports_contract_and_output_deltas() -> None:
    """DP-S3-2 (a): added, removed and changed contract fields and outputs, by name."""
    old = RatingAlgorithm.model_validate(valid_algorithm())
    new_data = valid_algorithm()
    contract = [f for f in new_data["input_contract"] if f["name"] != "channel"]
    for f in contract:
        if f["name"] == "driver_age":
            f["max"] = 90
    contract.append({"name": "ncd", "type": "int", "nullable": False})
    new_data["input_contract"] = contract
    new_data["outputs"] = [
        {**o, "required": False} if o["name"] == "payable_premium_minor" else o
        for o in new_data["outputs"]
    ]
    new = RatingAlgorithm.model_validate(new_data)

    diff = diff_algorithms(old, new)
    assert [(d.name, d.change) for d in diff.input_contract_deltas] == [
        ("channel", "removed"),
        ("driver_age", "changed"),
        ("ncd", "added"),
    ]
    assert [(d.name, d.change) for d in diff.output_deltas] == [
        ("payable_premium_minor", "changed")
    ]
    assert diff.input_contract_changed is True
    assert diff.outputs_changed is True


@pytest.mark.req("FR-227")
def test_a_stored_model_call_without_result_type_loads_as_the_legacy_default() -> None:
    """A payload written before the field validates and keeps its legacy meaning: `None`, a GBM
    prediction rounded at the step as before (PL-1464 item 16; the 2026-10-10 00:40:31 BST
    ruling). It does not become `decimal`, which is the opt-in."""
    data = valid_algorithm()
    assert "result_type" not in data["steps"][4]
    algorithm = RatingAlgorithm.model_validate(data)
    assert algorithm.steps[4].result_type is None  # type: ignore[union-attr]


@pytest.mark.req("FR-227")
@pytest.mark.parametrize("declared", ["decimal", "money_minor"])
def test_a_model_call_accepts_decimal_or_money_minor(declared: str) -> None:
    data = valid_algorithm()
    data["steps"][4] = {**data["steps"][4], "result_type": declared}
    assert RatingAlgorithm.model_validate(data).steps[4].result_type == declared  # type: ignore[union-attr]


@pytest.mark.req("FR-227")
@pytest.mark.parametrize("declared", ["relativity", "float", "string"])
def test_a_model_call_refuses_any_other_result_type(declared: str) -> None:
    data = valid_algorithm()
    data["steps"][4] = {**data["steps"][4], "result_type": declared}
    with pytest.raises(ValidationError, match=r"decimal or money_minor.*FR-227"):
        RatingAlgorithm.model_validate(data)


# --- WK-1250 Slice 2 (SL-1340): a sub-graph mount is a node of the parent's graph ---------------
# (RL-1309 DP-3 items 2 to 4; RL 9586 (working id) DP-S2-2: the port map, `mount_point` pattern)

from model_schema.graph_errors import GraphUnresolvedRefError  # noqa: E402
from model_schema.rating import Pins  # noqa: E402


def _mounted(*, consumer: str = "ncd_factor", outputs: dict | None = None) -> dict:
    """`valid_algorithm()` with the mount mapped, and a new step consuming `consumer`."""
    data = valid_algorithm()
    data["input_contract"].append(
        {"name": "ncd_years", "type": "int", "nullable": False, "min": 0, "max": 9}
    )
    data["steps"].insert(
        0,
        {"step_id": "s_in_ncd", "type": "input", "label": "NCD years",
         "input_name": "ncd_years", "on_missing": "error", "produces": "ncd_years"},
    )
    data["sub_graphs"] = [
        {"ref": "sub_graph:ncd-ladder@4", "mount_point": "s_ncd",
         "inputs": {"ncd_years": "ncd_years"},
         "outputs": {"ncd_factor": "ncd_factor"} if outputs is None else outputs}
    ]
    for step in data["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = f"risk_premium_minor * expense_factor * {consumer}"
            step["consumes"] = ["risk_premium_minor", "expense_factor", consumer]
    return data


@pytest.mark.req("FR-212")
@pytest.mark.req("FR-217")
def test_a_consumer_of_a_mapped_mount_output_is_accepted() -> None:
    algorithm = RatingAlgorithm.model_validate(_mounted())
    assert algorithm.sub_graphs[0].outputs == {"ncd_factor": "ncd_factor"}
    assert algorithm.sub_graphs[0].inputs == {"ncd_years": "ncd_years"}


@pytest.mark.req("FR-212")
@pytest.mark.req("FR-217")
def test_a_consumer_of_an_unmapped_port_is_refused_as_unresolved() -> None:
    """The name only an UNMAPPED output port would produce is produced by nothing."""
    with pytest.raises(ValidationError) as raised:
        RatingAlgorithm.model_validate(_mounted(outputs={"other_port": "other_value"}))
    errors = [e["ctx"]["error"] for e in raised.value.errors() if "ctx" in e]
    assert any(isinstance(e, GraphUnresolvedRefError) for e in errors)


@pytest.mark.req("FR-212")
@pytest.mark.req("FR-217")
def test_a_mount_that_consumes_a_value_no_step_produces_is_refused_as_unresolved() -> None:
    data = _mounted()
    data["sub_graphs"][0]["inputs"] = {"ncd_years": "never_produced"}
    with pytest.raises(ValidationError) as raised:
        RatingAlgorithm.model_validate(data)
    errors = [e["ctx"]["error"] for e in raised.value.errors() if "ctx" in e]
    assert any(isinstance(e, GraphUnresolvedRefError) for e in errors)


@pytest.mark.req("FR-212")
@pytest.mark.req("FR-217")
def test_a_mount_point_equal_to_a_step_id_is_refused() -> None:
    data = _mounted()
    data["sub_graphs"][0]["mount_point"] = "s_office"
    with pytest.raises(ValidationError, match="mount_point"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-212")
@pytest.mark.req("FR-217")
def test_two_mounts_may_not_share_a_mount_point() -> None:
    data = _mounted()
    data["sub_graphs"].append(
        {"ref": "sub_graph:other@1", "mount_point": "s_ncd", "inputs": {}, "outputs": {"o": "o"}}
    )
    with pytest.raises(ValidationError, match="mount_point"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-217")
@pytest.mark.parametrize("bad", ["a__b", "9x", "has space", "", "x-y"])
def test_a_mount_point_that_breaks_the_pattern_is_refused(bad: str) -> None:
    data = _mounted()
    data["sub_graphs"][0]["mount_point"] = bad
    with pytest.raises(ValidationError, match="mount_point"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-217")
def test_pins_default_has_no_sub_graphs_and_a_stored_four_list_dict_validates() -> None:
    assert Pins().sub_graphs == []
    stored = {"rate_tables": [], "models": [], "reference_tables": [], "custom_objectives": []}
    assert Pins.model_validate(stored).sub_graphs == []
    pinned = Pins.model_validate({"sub_graphs": ["sub_graph:ncd-ladder@4"]})
    assert str(pinned.sub_graphs[0]) == "sub_graph:ncd-ladder@4"


# --- the diff limb (RL-1309 DP-1 item 3; FR-219) -------------------------------------------------


def _ladder(version: int, expr: str):
    from model_schema.sub_graphs import SubGraph

    return SubGraph.model_validate({
        "slug": "ncd-ladder", "version": version,
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_ncd", "type": "expression", "label": "NCD", "expr": expr,
             "result_type": "decimal", "consumes": ["ncd_years"], "produces": "ncd_factor"},
        ],
        "change_note": f"v{version}",
    })


def _repointed(version: int) -> RatingAlgorithm:
    data = _mounted()
    data["sub_graphs"][0]["ref"] = f"sub_graph:ncd-ladder@{version}"
    return RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-219")
def test_the_diff_names_a_repointed_sub_graph_and_its_inner_step_changes() -> None:
    """Two algorithms that differ ONLY in a mount's version: the re-point and the inner change."""
    old, new = _repointed(4), _repointed(5)
    fragments = {
        "sub_graph:ncd-ladder@4": _ladder(4, "ncd_years * 10"),
        "sub_graph:ncd-ladder@5": _ladder(5, "ncd_years * 12"),
    }
    diff = diff_algorithms(old, new, fragments=fragments)
    assert diff.added_steps == diff.removed_steps == []
    assert len(diff.sub_graph_mounts) == 1
    change = diff.sub_graph_mounts[0]
    assert change.mount_point == "s_ncd"
    assert str(change.before) == "sub_graph:ncd-ladder@4"
    assert str(change.after) == "sub_graph:ncd-ladder@5"
    assert change.steps is not None
    inner = {(c.step_id, c.field): (c.before, c.after) for c in change.steps.changed_steps}
    assert inner[("s_ncd", "expr")] == ("ncd_years * 10", "ncd_years * 12")
    assert "sub-graph" in diff.summary


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-219")
def test_the_diff_names_the_repoint_without_fragments_and_nothing_when_unchanged() -> None:
    diff = diff_algorithms(_repointed(4), _repointed(5))
    assert [str(c.after) for c in diff.sub_graph_mounts] == ["sub_graph:ncd-ladder@5"]
    assert diff.sub_graph_mounts[0].steps is None
    same = diff_algorithms(_repointed(4), _repointed(4))
    assert same.sub_graph_mounts == []
    assert same.summary == "no structural change"


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-219")
def test_the_diff_names_an_added_or_removed_mount_and_a_changed_port_map() -> None:
    bare = valid_algorithm()
    bare["sub_graphs"] = []
    added = diff_algorithms(RatingAlgorithm.model_validate(bare), _repointed(4))
    assert [(c.before, str(c.after)) for c in added.sub_graph_mounts] == [
        (None, "sub_graph:ncd-ladder@4")
    ]
    data = _mounted()
    data["sub_graphs"][0]["inputs"] = {"ncd_years": "driver_age"}
    remapped = diff_algorithms(_repointed(4), RatingAlgorithm.model_validate(data))
    assert [c.ports_changed for c in remapped.sub_graph_mounts] == [True]
