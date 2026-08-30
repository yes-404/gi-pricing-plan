"""Rating Algorithm contract (W9-1, 03 §4.1) — shape, invariants, structural diff.

Covers FR-RATE-1 (DAG invariants), FR-RATE-2 (input contract), FR-RATE-3 (outputs),
FR-RATE-4 (stable step_id), FR-RATE-6 (sub-graphs), FR-RATE-7 (structural diff),
FR-RATE-10 (model_call mode), FR-RATE-12 (output rounding), FR-RATE-13 (money types).
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
            {"step_id": "s_minprem", "type": "constraint", "label": "Min premium",
             "condition": "office_premium_minor >= min_premium_minor",
             "on_violation": "clamp", "clamp_bounds": {"min": "min_premium_minor"},
             "reason_code": "MIN_PREMIUM_APPLIED",
             "consumes": ["office_premium_minor"], "produces": "office_premium_minor"},
            {"step_id": "s_out", "type": "output", "label": "Payable premium",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["office_premium_minor"]},
        ],
        "sub_graphs": [{"ref": "sub_graph:ncd-ladder@4", "mount_point": "s_ncd"}],
    }


@pytest.mark.req("FR-RATE-1")
@pytest.mark.req("FR-RATE-2")
@pytest.mark.req("FR-RATE-4")
@pytest.mark.req("FR-RATE-6")
def test_a_valid_algorithm_parses() -> None:
    """T1: the §4.1 shape accepts a consistent graph with all seven step types.

    Covers FR-RATE-1 (the shape is a DAG of steps that passes its invariants),
    FR-RATE-2 (the typed input contract), FR-RATE-4 (step_id is a stable identifier,
    distinct from the label), FR-RATE-6 (the sub-graph references and mount points).
    """
    algorithm = RatingAlgorithm.model_validate(valid_algorithm())
    assert algorithm.slug == "motor-gb"
    assert algorithm.version == 14
    assert len(algorithm.steps) == 9
    assert algorithm.sub_graphs[0].ref.type == "sub_graph"
    assert algorithm.sub_graphs[0].mount_point == "s_ncd"
    types = {type(step).__name__ for step in algorithm.steps}
    assert {
        "RatingInputStep", "RatingLookupStep", "RatingTableStep",
        "RatingExpressionStep", "RatingModelCallStep", "RatingConstraintStep",
        "RatingOutputStep",
    } <= types
    # FR-RATE-2: each input carries a name, a type, nullability, and a range or domain.
    age = algorithm.input_contract[0]
    assert age.name == "driver_age"
    assert age.type.value == "int"
    assert age.nullable is False
    assert age.min == 17
    assert age.max == 99
    channel = algorithm.input_contract[2]
    assert channel.domain == ["direct", "broker"]
    # FR-RATE-4: a step's id is a separate, stable identifier, never derived from its
    # human label — renaming the label cannot change the id.
    for step in algorithm.steps:
        assert step.step_id != step.label


@pytest.mark.req("FR-RATE-8")
@pytest.mark.req("FR-RATE-9")
@pytest.mark.req("FR-RATE-10")
@pytest.mark.req("FR-RATE-11")
@pytest.mark.req("FR-RATE-12")
def test_the_seven_step_types_accept_their_key_fields() -> None:
    """T1: each step type carries the key fields from 03 §3.2.

    Covers FR-RATE-8 (table steps pin a rate table), FR-RATE-9 (lookup steps evaluate
    as at a declared date), FR-RATE-10 (model_call declares a mode), FR-RATE-11
    (constraint steps carry a reason code), FR-RATE-12 (output steps declare rounding).
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


@pytest.mark.req("FR-RATE-13")
def test_a_monetary_result_typed_as_float_is_refused() -> None:
    """T1: FR-RATE-13 — money is `decimal` or `money_minor`, never float."""
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


@pytest.mark.req("FR-RATE-10")
def test_a_model_call_declares_exactly_one_reference() -> None:
    """T1: FR-RATE-10 — a model_call pins a model or a peril structure, not both."""
    data = valid_algorithm()
    data["steps"][4] = {
        **data["steps"][4],
        "model_ref": "model:motor-ad-frequency@7",
        "peril_structure_ref": "peril_structure:motor-gb-2026h2@2",
    }
    with pytest.raises(ValidationError, match="exactly one of model_ref or peril_structure_ref"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-RATE-1")
@pytest.mark.req("FR-RATE-25")
def test_a_cycle_is_refused() -> None:
    """T2: FR-RATE-1 — a cyclic graph fails.

    Also FR-RATE-25's own clause (1) ("the DAG is acyclic") — F-W9-3's cheap half
    (`docs/audit/register.md`). `compile_bundle` calls `RatingAlgorithm.model_validate`
    on the resolved payload before anything else, so this shape-level check is already
    the mechanism FR-RATE-25 relies on for the acyclic half of clause (1), and this test
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


@pytest.mark.req("FR-RATE-1")
def test_an_undefined_reference_is_refused() -> None:
    """T2: FR-RATE-1 — a consumed name no step produces fails."""
    data = valid_algorithm()
    data["steps"][6] = {
        **data["steps"][6],
        "consumes": ["no_such_value"], "produces": "office_premium_minor",
    }
    with pytest.raises(ValidationError, match="undefined value"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-RATE-3")
def test_a_missing_output_step_is_refused() -> None:
    """T2: FR-RATE-3 — every declared output has an output step."""
    data = valid_algorithm()
    data["outputs"].append({"name": "extra_output", "type": "money_minor", "required": False})
    with pytest.raises(ValidationError, match="has no output step"):
        RatingAlgorithm.model_validate(data)


@pytest.mark.req("FR-RATE-1")
@pytest.mark.req("FR-RATE-25")
def test_an_orphaned_step_is_refused() -> None:
    """T2: FR-RATE-1 — a step neither reachable from an input nor feeding an output.

    Also FR-RATE-25's own clause (1) ("the DAG is ... fully connected") — F-W9-3's cheap
    half (`docs/audit/register.md`), pointing the already-run mechanism at the umbrella
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


@pytest.mark.req("FR-RATE-7")
def test_the_diff_names_added_removed_and_changed_steps() -> None:
    """T3: FR-RATE-7 — the structural diff names each change."""
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


@pytest.mark.req("FR-RATE-7")
def test_the_diff_names_a_repointed_table() -> None:
    """T3: FR-RATE-7 — a table step whose rate table changed is named as re-pointed."""
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
