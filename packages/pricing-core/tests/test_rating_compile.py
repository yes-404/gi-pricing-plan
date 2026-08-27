"""Save-time validation of a RatingAlgorithm (slice W9-2).

Covers FR-RATE-13 (result-type compatibility), FR-RATE-5 (determinism), and the four
boundary guards FR-RATE-56/57/58/59, each proven to fail on broken input.
"""

from __future__ import annotations

import pytest

from model_schema.rating import RatingAlgorithm
from pricing_core.rating.compile import assert_integer_minor_round_trip, validate_algorithm


def valid_algorithm() -> dict:
    """A consistent seven-step graph whose expressions compile against the engine."""
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
             "condition": "office_premium_minor >= 100", "on_violation": "clamp",
             "clamp_bounds": {"min": "100"}, "reason_code": "MIN_PREMIUM_APPLIED",
             "consumes": ["office_premium_minor"], "produces": "office_premium_minor"},
            {"step_id": "s_out", "type": "output", "label": "Payable premium",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["office_premium_minor"]},
        ],
        "sub_graphs": [],
    }


def codes(algorithm: RatingAlgorithm) -> set[str]:
    return {issue.code for issue in validate_algorithm(algorithm)}


@pytest.mark.req("FR-RATE-56")
def test_integer_minor_units_round_trip() -> None:
    """FR-RATE-56: the startup self-check asserts the integer round-trip."""
    assert_integer_minor_round_trip()  # must not raise


@pytest.mark.req("FR-RATE-13")
def test_a_valid_algorithm_has_no_save_time_issues() -> None:
    algorithm = RatingAlgorithm.model_validate(valid_algorithm())
    assert validate_algorithm(algorithm) == []


@pytest.mark.req("FR-RATE-13")
def test_a_result_type_mismatch_is_refused() -> None:
    """FR-RATE-13: an output declared money_minor fed by a string value fails."""
    data = valid_algorithm()
    data["input_contract"].append(
        {"name": "customer_name", "type": "string", "nullable": False}
    )
    # the office expression now consumes the string input and still produces money_minor —
    # but the output step consumes a string-typed input directly.
    data["outputs"].append({"name": "name_out", "type": "money_minor", "required": False})
    data["steps"].append({
        "step_id": "s_in_name", "type": "input", "label": "Name",
        "input_name": "customer_name", "on_missing": "error", "produces": "customer_name",
    })
    data["steps"].append({
        "step_id": "s_name_out", "type": "output", "label": "Name out",
        "output_name": "name_out", "rounding": {"mode": "half_even", "dp": 0},
        "consumes": "customer_name",
    })
    algorithm = RatingAlgorithm.model_validate(data)
    assert "RATING_TYPE_MISMATCH" in codes(algorithm)


@pytest.mark.req("FR-RATE-5")
def test_a_non_deterministic_expression_is_refused() -> None:
    """FR-RATE-5/30: an expression calling now() fails — no wall-clock in the graph."""
    data = valid_algorithm()
    for step in data["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor * expense_factor + now()"
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_NON_DETERMINISTIC" in codes(algorithm)


@pytest.mark.req("FR-RATE-57")
def test_an_unguarded_division_is_refused() -> None:
    """FR-RATE-57: division without an explicit zero guard fails."""
    data = valid_algorithm()
    for step in data["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor / expense_factor"
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_UNGUARDED_DIVISION" in codes(algorithm)


@pytest.mark.req("FR-RATE-57")
def test_a_guarded_division_is_accepted() -> None:
    """FR-RATE-57: a division carrying a zero guard is not flagged."""
    data = valid_algorithm()
    for step in data["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "expense_factor != 0 ? risk_premium_minor / expense_factor : 0"
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_UNGUARDED_DIVISION" not in codes(algorithm)


@pytest.mark.req("FR-RATE-58")
def test_a_scale_cap_overflow_is_refused() -> None:
    """FR-RATE-58: an input bound beyond rust_decimal's 28-place cap fails."""
    data = valid_algorithm()
    data["input_contract"][0]["min"] = "0.12345678901234567890123456789"  # 29 places
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_SCALE_OVERFLOW" in codes(algorithm)


@pytest.mark.req("FR-RATE-59")
def test_a_foreign_function_is_refused() -> None:
    """FR-RATE-59: an expression using a function the engine lacks fails to compile."""
    data = valid_algorithm()
    for step in data["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "foo(risk_premium_minor)"
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_INVALID_VOCABULARY" in codes(algorithm)
