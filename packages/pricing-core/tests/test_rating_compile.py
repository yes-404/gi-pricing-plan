"""Save-time validation of a RatingAlgorithm (slice W9-2).

Covers FR-227 (result-type compatibility), FR-216 (determinism), and the four
boundary guards FR-273/274/275/276, each proven to fail on broken input.
"""

from __future__ import annotations

import pytest

from model_schema.rating import RatingAlgorithm
from pricing_core.rating.compile import assert_integer_minor_round_trip, validate_algorithm
from pricing_core.rating.references import referenced_names

#: The pre-edit `valid_algorithm` body, verbatim (SL-1345, RL-1329 §2 step 5): its clamp is on the
#: source of the payable's rung, so the placement check refuses it with LADDER_CLAMP_UNPLACEABLE.
PRE_EDIT_VALID_ALGORITHM: dict = {
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


def valid_algorithm() -> dict:
    """A consistent twelve-step graph whose expressions compile against the engine."""
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
            # The clamped name is the source of the last rung before `constraints`
            # (`office_premium`), and the payable reads a later name: a placeable clamp.
            {"step_id": "s_out_office", "type": "output", "label": "Office premium",
             "output_name": "office_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["office_premium_minor"]},
            {"step_id": "s_payable", "type": "expression", "label": "Payable premium value",
             "expr": "office_premium_minor * 1", "result_type": "money_minor",
             "consumes": ["office_premium_minor"], "produces": "payable_value"},
            {"step_id": "s_out", "type": "output", "label": "Payable premium",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable_value"]},
        ],
        "sub_graphs": [],
    }


def codes(algorithm: RatingAlgorithm) -> set[str]:
    return {issue.code for issue in validate_algorithm(algorithm)}


@pytest.mark.req("FR-273")
def test_integer_minor_units_round_trip() -> None:
    """FR-273: the startup self-check asserts the integer round-trip."""
    assert_integer_minor_round_trip()  # must not raise


@pytest.mark.req("FR-227")
def test_a_valid_algorithm_has_no_save_time_issues() -> None:
    algorithm = RatingAlgorithm.model_validate(valid_algorithm())
    assert validate_algorithm(algorithm) == []


@pytest.mark.req("FR-227")
@pytest.mark.req("FR-240")
def test_a_result_type_mismatch_is_refused() -> None:
    """FR-227: an output declared money_minor fed by a string value fails.

    Also FR-240's own clause (3) ("all types compatible") — F-W9-3's cheap half
    (`docs/findings/register.md`), pointing the already-run mechanism at the umbrella
    requirement (`docs/plans/2026-08-29-w11-algorithm-pin-maturity.md`).
    """
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


@pytest.mark.req("FR-216")
def test_a_non_deterministic_expression_is_refused() -> None:
    """FR-216/246: an expression calling now() fails — no wall-clock in the graph."""
    data = valid_algorithm()
    for step in data["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor * expense_factor + now()"
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_NON_DETERMINISTIC" in codes(algorithm)


@pytest.mark.req("FR-274")
def test_an_unguarded_division_is_refused() -> None:
    """FR-274: division without an explicit zero guard fails."""
    data = valid_algorithm()
    for step in data["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor / expense_factor"
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_UNGUARDED_DIVISION" in codes(algorithm)


@pytest.mark.req("FR-274")
def test_a_guarded_division_is_accepted() -> None:
    """FR-274: a division carrying a zero guard is not flagged."""
    data = valid_algorithm()
    for step in data["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "expense_factor != 0 ? risk_premium_minor / expense_factor : 0"
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_UNGUARDED_DIVISION" not in codes(algorithm)


@pytest.mark.req("FR-275")
def test_a_scale_cap_overflow_is_refused() -> None:
    """FR-275: an input bound beyond rust_decimal's 28-place cap fails."""
    data = valid_algorithm()
    data["input_contract"][0]["min"] = "0.12345678901234567890123456789"  # 29 places
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_SCALE_OVERFLOW" in codes(algorithm)


@pytest.mark.req("FR-276")
def test_a_foreign_function_is_refused() -> None:
    """FR-276: an expression using a function the engine lacks fails to compile."""
    data = valid_algorithm()
    for step in data["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "foo(risk_premium_minor)"
    algorithm = RatingAlgorithm.model_validate(data)
    assert "EXPRESSION_INVALID_VOCABULARY" in codes(algorithm)


# ---------------------------------------------------------------------------
# WK-1178 code slice (PL-1314, RL-1312, RL-1313, FD-1317): FR-244's enforced allow-list, and
# every authored string (expr, condition, clamp_bounds, key_expr) through the same checks.
# ---------------------------------------------------------------------------


def _with(step_id: str, **fields: object) -> RatingAlgorithm:
    data = valid_algorithm()
    for step in data["steps"]:
        if step["step_id"] == step_id:
            step.update(fields)
            # FR-246 (FD-1374): a step declares what it reads, so an edited field's reads are
            # re-declared from the reference reader, not hand-picked.
            # The first consumed name stays first: FR-240's clamp placement reads it.
            first = list(step.get("consumes") or [])[:1]
            step["consumes"] = first + sorted(referenced_names(step) - set(first))
    return RatingAlgorithm.model_validate(data)


def _issues(algorithm: RatingAlgorithm, code: str) -> list:
    return [issue for issue in validate_algorithm(algorithm) if issue.code == code]


@pytest.mark.req("FR-244")
@pytest.mark.parametrize("expr", [
    "risk_premium_minor % 7",
    "risk_premium_minor in [1, 2]",
    "risk_premium_minor[0]",
    "risk_premium_minor.b",
    "len('x')",
    "sum([risk_premium_minor, 1])",
    "round(risk_premium_minor, 2)",
    "floor(risk_premium_minor)",
    "ceil(risk_premium_minor)",
])
def test_the_allow_list_refuses_a_construct_it_does_not_name(expr: str) -> None:
    """RL-1312 item 1: each is compiled by the engine today, and each is refused at save."""
    found = _issues(_with("s_office", expr=expr), "EXPRESSION_INVALID_VOCABULARY")
    assert [(i.step_id, i.field) for i in found] == [("s_office", "expr")]
    assert "FR-244" in found[0].message


@pytest.mark.req("FR-244")
@pytest.mark.parametrize("text", [
    "risk_premium_minor ?? 0",
    "expense_factor != 0 ? risk_premium_minor / expense_factor : 0",
    "min([max([risk_premium_minor, 0]), 1])",
    "abs(risk_premium_minor)",
])
def test_the_allow_list_accepts_the_ruled_constructs_in_an_expr(text: str) -> None:
    assert validate_algorithm(_with("s_office", expr=text)) == []


@pytest.mark.req("FR-244")
@pytest.mark.parametrize("text", [
    "(office_premium_minor ?? 0) >= 100",
    "(expense_factor != 0 ? office_premium_minor / expense_factor : 0) >= 100",
    "min([max([office_premium_minor, 0]), 1000]) >= 100",
    "abs(office_premium_minor) >= 100",
])
def test_the_allow_list_accepts_the_ruled_constructs_in_a_condition(text: str) -> None:
    assert validate_algorithm(_with("s_minprem", condition=text)) == []


#: FD-1317's evidence table (measured at 9f63d0fe): each of these returned `[]` before this slice.
_FD_1317_ROWS = [
    ("condition", "sum([office_premium_minor, 1]) >= 100", "EXPRESSION_INVALID_VOCABULARY"),
    ("condition", "office_premium_minor[0] >= 100", "EXPRESSION_INVALID_VOCABULARY"),
    ("condition", "office_premium_minor / expense_factor >= 100", "EXPRESSION_UNGUARDED_DIVISION"),
    ("condition", "office_premium_minor >=(((", "EXPRESSION_INVALID_VOCABULARY"),
    ("condition", "now() >= 100", "EXPRESSION_NON_DETERMINISTIC"),
    ("condition", "office_premium_minor >= 0." + "1" * 31, "EXPRESSION_SCALE_OVERFLOW"),
    ("clamp_bounds.min", "100 / expense_factor", "EXPRESSION_UNGUARDED_DIVISION"),
    ("clamp_bounds.min", "(((", "EXPRESSION_INVALID_VOCABULARY"),
    ("expr", "risk_premium_minor % 7", "EXPRESSION_INVALID_VOCABULARY"),
    ("key_expr[0]", "channel % 2", "EXPRESSION_INVALID_VOCABULARY"),
]


@pytest.mark.req("FR-274")
@pytest.mark.parametrize(("field", "text", "code"), _FD_1317_ROWS)
def test_every_authored_field_returns_its_issue(field: str, text: str, code: str) -> None:
    if field.startswith("clamp_bounds"):
        algorithm = _with("s_minprem", clamp_bounds={"min": text})
        step_id = "s_minprem"
    elif field == "condition":
        algorithm, step_id = _with("s_minprem", condition=text), "s_minprem"
    elif field.startswith("key_expr"):
        algorithm, step_id = _with("s_expense", key_expr=[text]), "s_expense"
    else:
        algorithm, step_id = _with("s_office", expr=text), "s_office"
    assert (step_id, field) in [(i.step_id, i.field) for i in _issues(algorithm, code)]


@pytest.mark.req("FR-274")
@pytest.mark.parametrize("unguarded", [
    "{} / expense_factor ?? 0",
    "({} / expense_factor) ?? 0",
    "{} / expense_factor != null ? {} / expense_factor : 0",
])
def test_a_null_coalescing_form_is_never_a_division_guard(unguarded: str) -> None:
    """RL-1312 item 2: `??` and `!= null` mask a division's null; they do not guard it."""
    code = "EXPRESSION_UNGUARDED_DIVISION"
    expr = unguarded.format("risk_premium_minor", "risk_premium_minor")
    cond = "(" + unguarded.format("office_premium_minor", "office_premium_minor") + ") >= 100"
    bound = unguarded.format("office_premium_minor", "office_premium_minor")
    assert _issues(_with("s_office", expr=expr), code)
    assert _issues(_with("s_minprem", condition=cond), code)
    assert _issues(_with("s_minprem", clamp_bounds={"min": bound}), code)


@pytest.mark.req("FR-274")
def test_the_guard_markers_hold_no_dead_or_masking_entry() -> None:
    from pricing_core.rating.compile import _GUARD_MARKERS

    for dead in ("?:", "coalesce(", "??", "!= null"):
        assert dead not in _GUARD_MARKERS


# --- WK-1250 Slice 1: FR-227 over steps and declared outputs, and the fragment entry point ---


@pytest.mark.req("FR-227")
def test_an_algorithm_type_mismatch_reports_the_output_step() -> None:
    """The refactor keeps the algorithm path's issue: the output step's id, `outputs`."""
    data = valid_algorithm()
    data["input_contract"].append({"name": "customer_name", "type": "string", "nullable": False})
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
    issues = _issues(RatingAlgorithm.model_validate(data), "RATING_TYPE_MISMATCH")
    assert [(i.step_id, i.field) for i in issues] == [("s_name_out", "outputs")]


def _fragment(output_type: str, result_type: str = "string") -> dict:
    return {
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": output_type, "required": True}],
        "steps": [
            {"step_id": "s_first", "type": "expression", "label": "first", "expr": "ncd_years",
             "result_type": "int", "consumes": "ncd_years", "produces": "mid"},
            {"step_id": "s_last", "type": "expression", "label": "last", "expr": "mid",
             "result_type": result_type, "consumes": "mid", "produces": "ncd_factor"},
        ],
        "change_note": "n",
    }


def _fragment_issues(payload: dict) -> list:
    from model_schema.sub_graphs import SubGraphBody
    from pricing_core.rating.compile import fragment_output_type_issues

    body = SubGraphBody.model_validate(payload)
    return fragment_output_type_issues(body.steps, body.inputs, body.outputs)


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-227")
def test_a_fragment_output_port_type_mismatch_names_the_producing_step() -> None:
    issues = _fragment_issues(_fragment("money_minor"))
    assert [(i.code, i.step_id, i.field) for i in issues] == [
        ("RATING_TYPE_MISMATCH", "s_last", "outputs")
    ]
    assert "'ncd_factor'" in issues[0].message


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-227")
def test_a_compatible_fragment_output_port_raises_no_issue() -> None:
    assert _fragment_issues(_fragment("string")) == []
    assert _fragment_issues(_fragment("money_minor", result_type="decimal")) == []


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-227")
def test_an_input_port_type_is_a_known_producer_type() -> None:
    payload = _fragment("money_minor")
    payload["inputs"] = [{"name": "ncd_factor", "type": "string"}]
    payload["steps"] = [
        {"step_id": "s_clamp", "type": "constraint", "label": "cap", "condition": "ncd_factor > 0",
         "on_violation": "clamp", "clamp_bounds": {"min": "0"}, "reason_code": "R",
         "consumes": "ncd_factor", "produces": "ncd_factor"}
    ]
    issues = _fragment_issues(payload)
    assert [(i.code, i.step_id) for i in issues] == [("RATING_TYPE_MISMATCH", "s_clamp")]


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-227")
def test_a_table_produced_output_port_is_not_checked_at_create() -> None:
    payload = _fragment("money_minor")
    payload["steps"] = [
        {"step_id": "s_tab", "type": "table", "label": "t", "rate_table_ref": "rate_table:ncd@2",
         "key_expr": ["ncd_years"], "consumes": "ncd_years", "produces": "ncd_factor"}
    ]
    assert _fragment_issues(payload) == []


@pytest.mark.req("FR-240")
def test_the_pre_edit_valid_algorithm_is_refused_by_validate_algorithm() -> None:
    """SL-1345: the old shape (a clamp on the payable's own source) stays refused."""
    issues = validate_algorithm(RatingAlgorithm.model_validate(PRE_EDIT_VALID_ALGORITHM))
    assert [i.code for i in issues] == ["LADDER_CLAMP_UNPLACEABLE"], issues
