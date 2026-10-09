"""WK-1250 Slice 2 (SL-1340): the pure sub-graph inliner (FR-217; RL-1309 DP-3; RL 9586 DP-S2-2).

`inline_mounts` replaces each mount by the pinned fragment's steps, namespaced `<mount>__<name>`,
its ports renamed to the parent values they are mapped to, in a stable topological order (P5).
The input-port TYPE check and every pin check are `compile_bundle`'s
(`test_rating_compile_bundle.py`).
"""

from __future__ import annotations

from typing import Any

import pytest

from model_schema.rating import RatingAlgorithm
from model_schema.sub_graphs import SubGraph
from pricing_core.rating.inline import inline_mounts
from pricing_core.rating.vocabulary import rename_tokens
from pricing_core.safe_error import CodedError

REF = "sub_graph:ncd-ladder@4"


def _fragment(**overrides: Any) -> SubGraph:
    data: dict[str, Any] = {
        "slug": "ncd-ladder",
        "version": 4,
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "decimal", "required": True}],
        "steps": [
            {"step_id": "s_ladder", "type": "expression", "label": "Ladder",
             "expr": "ncd_years * 10", "result_type": "decimal",
             "consumes": ["ncd_years"], "produces": "ncd_raw"},
            {"step_id": "s_cap", "type": "expression", "label": "Cap",
             "expr": "min([ncd_raw, 50])", "result_type": "decimal",
             "consumes": ["ncd_raw"], "produces": "ncd_factor"},
        ],
        "change_note": "first cut",
    }
    data.update(overrides)
    return SubGraph.model_validate(data)


def _parent(
    *, mount: dict[str, Any] | None = None, extra_inputs: list[str] | None = None
) -> RatingAlgorithm:
    """Input steps for `years_clean` (and any extras), the mount, then an output step.

    The output step is listed BEFORE the mount's steps will be appended, so only a topological
    order puts the fragment's steps ahead of it.
    """
    names = ["years_clean", *(extra_inputs or [])]
    return RatingAlgorithm.model_validate({
        "slug": "motor-gb",
        "version": 1,
        "input_contract": [{"name": n, "type": "int", "nullable": False} for n in names],
        "outputs": [{"name": "premium", "type": "decimal", "required": True}],
        "steps": [
            *({"step_id": f"s_in_{n}", "type": "input", "label": n, "input_name": n,
               "on_missing": "error", "produces": n} for n in names),
            {"step_id": "s_out", "type": "output", "label": "Premium", "output_name": "premium",
             "rounding": {"mode": "half_even", "dp": 0}, "consumes": ["ncd_factor"]},
        ],
        "sub_graphs": [mount or {
            "ref": REF, "mount_point": "m_ncd",
            "inputs": {"ncd_years": "years_clean"}, "outputs": {"ncd_factor": "ncd_factor"},
        }],
    })


def _inline(parent: RatingAlgorithm, fragment: SubGraph | None = None) -> RatingAlgorithm:
    return inline_mounts(parent, {REF: fragment or _fragment()})


@pytest.mark.req("FR-217")
def test_an_algorithm_with_no_mounts_is_returned_equal_to_itself() -> None:
    data = _parent().model_dump(mode="json")
    data["sub_graphs"] = []
    data["steps"][-1]["consumes"] = ["years_clean"]
    plain = RatingAlgorithm.model_validate(data)
    assert inline_mounts(plain, {}) == plain


@pytest.mark.req("FR-217")
def test_every_fragment_step_and_internal_name_is_namespaced_and_ports_are_renamed() -> None:
    inlined = _inline(_parent())
    assert inlined.sub_graphs == []
    by_id = {s.step_id: s for s in inlined.steps}
    assert {"m_ncd__s_ladder", "m_ncd__s_cap"} <= set(by_id)
    ladder, cap = by_id["m_ncd__s_ladder"], by_id["m_ncd__s_cap"]
    # The input port is the parent value it is mapped to; the internal name is namespaced.
    assert ladder.expr == "years_clean * 10"
    assert ladder.consumes == ["years_clean"]
    assert ladder.produces == "m_ncd__ncd_raw"
    assert cap.expr == "min([m_ncd__ncd_raw, 50])"
    assert cap.consumes == ["m_ncd__ncd_raw"]
    # The mapped output port is the parent name it is mapped to.
    assert cap.produces == "ncd_factor"


@pytest.mark.req("FR-217")
def test_the_steps_are_in_a_stable_topological_order_not_parent_then_mounts() -> None:
    """RL 9586 P5: `s_out` consumes the mount's output, so it comes after the fragment's steps."""
    order = [s.step_id for s in _inline(_parent()).steps]
    assert order.index("m_ncd__s_ladder") < order.index("m_ncd__s_cap") < order.index("s_out")
    assert order[:1] == ["s_in_years_clean"]


@pytest.mark.req("FR-217")
def test_a_fragment_name_equal_to_a_parent_name_is_namespaced_not_merged() -> None:
    """The deliberate clash: the parent has its own `ncd_raw`; the fragment's stays its own."""
    inlined = _inline(_parent(extra_inputs=["ncd_raw"]))
    produced_by_parent = [s for s in inlined.steps if s.produces == "ncd_raw"]
    assert [s.step_id for s in produced_by_parent] == ["s_in_ncd_raw"]
    assert any(s.produces == "m_ncd__ncd_raw" for s in inlined.steps)


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-244")
def test_an_internal_name_inside_an_expression_is_renamed_and_the_expression_still_passes() -> None:
    from pricing_core.rating.vocabulary import check_allow_list

    cap = next(s for s in _inline(_parent()).steps if s.step_id == "m_ncd__s_cap")
    assert check_allow_list(cap.expr) is None
    assert "/" not in cap.expr
    assert "__" in cap.expr


@pytest.mark.req("FR-217")
@pytest.mark.req("FR-244")
def test_only_the_exact_token_is_renamed_never_a_substring() -> None:
    """`ncd` beside `ncd_years`: the port `ncd_years` maps to a parent value, `ncd` is internal."""
    fragment = _fragment(
        steps=[
            {"step_id": "s_one", "type": "expression", "label": "one", "expr": "ncd_years + 1",
             "result_type": "decimal", "consumes": ["ncd_years"], "produces": "ncd"},
            {"step_id": "s_two", "type": "expression", "label": "two", "expr": "ncd + ncd_years",
             "result_type": "decimal", "consumes": ["ncd", "ncd_years"], "produces": "ncd_factor"},
        ],
    )
    two = next(s for s in _inline(_parent(), fragment).steps if s.step_id == "m_ncd__s_two")
    assert two.expr == "m_ncd__ncd + years_clean"


@pytest.mark.req("FR-217")
@pytest.mark.parametrize(("step", "attr", "expected"), [
    ({"type": "constraint", "condition": "ncd_raw >= 0", "on_violation": "decline",
      "reason_code": "X", "consumes": ["ncd_raw"]}, "condition", "m_ncd__ncd_raw >= 0"),
    ({"type": "constraint", "condition": "ncd_raw >= 0", "on_violation": "clamp",
      "clamp_bounds": {"min": "ncd_raw"}, "reason_code": "X", "consumes": ["ncd_raw"],
      "produces": "ncd_raw"}, "clamp_bounds", {"min": "m_ncd__ncd_raw"}),
    ({"type": "model_call", "model_ref": "model:motor-ad@1", "mode": "exact",
      "feature_map": {"f": "ncd_raw"}, "consumes": ["ncd_raw"], "produces": "m_out"},
     "feature_map", {"f": "m_ncd__ncd_raw"}),
    ({"type": "table", "rate_table_ref": "rate_table:expense@1", "key_expr": ["ncd_raw"],
      "consumes": ["ncd_raw"], "produces": "t_out"}, "key_expr", ["m_ncd__ncd_raw"]),
    ({"type": "lookup", "reference_table_ref": "reference_table:area@1", "key_expr": ["ncd_raw"],
      "as_at": "ncd_raw", "on_miss": "error", "consumes": ["ncd_raw"], "produces": "l_out"},
     "as_at", "m_ncd__ncd_raw"),
])
def test_every_name_bearing_field_is_renamed(
    step: dict[str, Any], attr: str, expected: Any
) -> None:
    extra = {"step_id": "s_x", "label": "x", **step}
    base = _fragment().model_dump(mode="json")["steps"]
    fragment = _fragment(steps=[*base, extra])
    renamed = next(s for s in _inline(_parent(), fragment).steps if s.step_id == "m_ncd__s_x")
    assert getattr(renamed, attr) == expected
    assert renamed.consumes == ["m_ncd__ncd_raw"]


@pytest.mark.req("FR-217")
def test_rename_tokens_never_touches_a_function_a_literal_word_or_a_substring() -> None:
    assert rename_tokens("min([a, ab]) + abs(a) + true", {"a": "z", "min": "q", "true": "t"}) == (
        "min([z, ab]) + abs(z) + true"
    )


@pytest.mark.req("FR-217")
@pytest.mark.parametrize(("mount_edit", "code"), [
    ({"inputs": {}}, "RATING_GRAPH_UNRESOLVED_REF"),  # an unmapped input port
    ({"inputs": {"ncd_years": "years_clean", "ghost": "years_clean"}},
     "RATING_GRAPH_UNRESOLVED_REF"),  # an undeclared input port
    ({"outputs": {"ghost": "ncd_factor"}}, "RATING_GRAPH_UNRESOLVED_REF"),  # an undeclared output
])
def test_a_port_map_that_does_not_fit_the_fragment_is_refused_by_cause(
    mount_edit: dict[str, Any], code: str
) -> None:
    mount = {"ref": REF, "mount_point": "m_ncd", "inputs": {"ncd_years": "years_clean"},
             "outputs": {"ncd_factor": "ncd_factor"}, **mount_edit}
    with pytest.raises(CodedError, match=rf"^{code}"):
        _inline(_parent(mount=mount))


@pytest.mark.req("FR-217")
def test_a_mount_that_maps_no_output_port_is_refused() -> None:
    parent = _parent()
    bare = parent.model_copy(update={
        "sub_graphs": [parent.sub_graphs[0].model_copy(update={"outputs": {}})],
    })
    with pytest.raises(CodedError, match=r"^RATING_GRAPH_UNRESOLVED_REF"):
        _inline(bare)


@pytest.mark.req("FR-217")
@pytest.mark.parametrize("parent_name", [
    "m_ncd__ncd_raw",              # a namespaced value name
    "m_ncd__s_ladder",             # a namespaced step id
    "m_ncd__s_ladder__violated",   # a key to_wire derives from a namespaced step id
    "m_ncd__s_cap__max",
])
def test_a_namespaced_name_equal_to_a_parent_name_is_refused_never_merged(parent_name: str) -> None:
    with pytest.raises(CodedError, match=r"^VALIDATION_FAILED"):
        _inline(_parent(extra_inputs=[parent_name]))


@pytest.mark.req("FR-217")
def test_a_fragment_that_re_produces_its_input_port_is_refused() -> None:
    """It would overwrite the parent's value the port maps to (unruled: refused, not picked)."""
    fragment = _fragment(
        steps=[
            {"step_id": "s_clamp", "type": "expression", "label": "c",
             "expr": "min([ncd_years, 5])", "result_type": "int",
             "consumes": ["ncd_years"], "produces": "ncd_years"},
            {"step_id": "s_cap", "type": "expression", "label": "Cap", "expr": "ncd_years * 2",
             "result_type": "decimal", "consumes": ["ncd_years"], "produces": "ncd_factor"},
        ],
    )
    with pytest.raises(CodedError, match=r"^VALIDATION_FAILED"):
        _inline(_parent(), fragment)


@pytest.mark.req("FR-217")
def test_a_mount_with_no_fragment_is_refused_as_unpinned() -> None:
    with pytest.raises(CodedError, match=r"^RATING_VERSION_UNPINNED"):
        inline_mounts(_parent(), {})
