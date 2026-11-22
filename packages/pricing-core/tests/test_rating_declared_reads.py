"""PL-1520 Task 1A (FR-246, FD-1374): a step reads only names it declares."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from test_rating_peril_scoring import _structure_payload
from test_rating_score import _algorithm_payload

from model_schema.rating import RatingAlgorithm, RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle, validate_algorithm
from pricing_core.rating.references import referenced_names
from pricing_core.safe_error import CodedError

#: DP-F35-1 (iii-a)'s ruled code (RL-1519).
UNDECLARED_READ_CODE = "RATING_STEP_UNDECLARED_READ"


@pytest.mark.req("FR-258")
def test_referenced_names_reads_every_field_a_step_evaluates() -> None:
    clamp = {
        "type": "constraint", "consumes": ["office_premium_minor"],
        "produces": ["office_premium_minor"],
        "condition": "office_premium_minor >= min_premium_minor",
        "clamp_bounds": {"min": "min_premium_minor"},
    }
    assert referenced_names(clamp) == {"office_premium_minor", "min_premium_minor"}
    expr = {"type": "expression", "consumes": ["a"], "produces": "c",
            "expr": "a * b + abs(a)"}
    assert referenced_names(expr) == {"a", "b"}
    table = {"type": "table", "consumes": ["channel"], "produces": "f", "key_expr": ["channel"]}
    assert referenced_names(table) == {"channel"}
    model = {"type": "model_call", "consumes": ["driver_age"], "produces": ["r"],
             "feature_map": {"driver_age": "age_years"}}
    assert referenced_names(model) == {"driver_age"}
    quoted = {"type": "expression", "consumes": [], "produces": "c",
              "expr": "channel == 'broker_fee'"}
    assert referenced_names(quoted) == {"channel"}
    lookup = {"type": "lookup", "consumes": ["postcode_outcode"], "produces": "area",
              "key_expr": ["postcode_outcode"], "as_at": "effective_date"}
    # `as_at: "effective_date"` is the stamped date, not a counted read (ruling 15:40:36 BST) ...
    assert referenced_names(lookup) == {"postcode_outcode"}
    # ... any other `as_at` is.
    assert referenced_names({**lookup, "as_at": "inception"}) == {"postcode_outcode", "inception"}


def _undeclared_clamp_payload() -> dict[str, Any]:
    """The named negative fixture: the scoring fixture with `s_clamp` as it was before FD-1374's
    fix, reading `min_premium_minor` without declaring it."""
    payload = copy.deepcopy(_algorithm_payload())
    for step in payload["steps"]:
        if step["step_id"] == "s_clamp":
            step["consumes"] = ["office_premium_minor"]
    return payload


def _fr246(issues: list[Any]) -> list[Any]:
    return [i for i in issues if "FR-246" in i.message]


@pytest.mark.req("FR-246")
def test_a_constraint_reading_an_undeclared_name_is_refused() -> None:
    issues = _fr246(validate_algorithm(RatingAlgorithm.model_validate(_undeclared_clamp_payload())))
    # #1712 S7c: one issue per READING LOCATION, in step order then field order, each field the
    # authored location (`authored_expression_fields`), never a name the author submitted.
    assert [(i.step_id, i.code, i.field) for i in issues] == [
        ("s_clamp", UNDECLARED_READ_CODE, "condition"),
        ("s_clamp", UNDECLARED_READ_CODE, "clamp_bounds.min"),
    ], issues
    # #1712 S7c: the text names no step and no name; the step is located by `step_id`/`field`.
    assert all("min_premium_minor" not in i.message for i in issues)
    assert all("s_clamp" not in i.message for i in issues)
    assert all("min_premium_minor" not in i.field for i in issues)


@pytest.mark.req("FR-246")
def test_an_expression_reading_an_undeclared_name_is_refused() -> None:
    payload = copy.deepcopy(_algorithm_payload())
    for step in payload["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor * expense_factor * sanity_cap_minor"
    issues = _fr246(validate_algorithm(RatingAlgorithm.model_validate(payload)))
    assert [(i.step_id, i.code, i.field) for i in issues] == [
        ("s_office", UNDECLARED_READ_CODE, "expr")
    ], issues


@pytest.mark.req("FR-246")
def test_the_location_is_the_position_of_the_read_and_the_order_is_fixed() -> None:
    """#1712 S7c: three steps each read a stray name at a NON-first location (a list position,
    a model_call feature_map position, an expression). Equality on (step_id, code, field), in
    step order; the submitted name is in no field."""
    payload = copy.deepcopy(_algorithm_payload())
    for step in payload["steps"]:
        if step["step_id"] == "s_expense":
            step["key_expr"] = ["channel", "stray_key"]
        elif step["step_id"] == "s_risk":
            step["feature_map"] = {"driver_age": "age_years", "stray_feature": "x"}
        elif step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor * expense_factor * stray_expr"
    expected = [
        ("s_expense", UNDECLARED_READ_CODE, "key_expr[1]"),
        ("s_risk", UNDECLARED_READ_CODE, "feature_map.stray_feature"),
        ("s_office", UNDECLARED_READ_CODE, "expr"),
    ]
    for _ in range(2):  # the same order on a second call
        issues = _fr246(validate_algorithm(RatingAlgorithm.model_validate(payload)))
        assert [(i.step_id, i.code, i.field) for i in issues] == expected, issues
    # the field of a list or an expression location holds no name; a keyed-map entry's holds the
    # key (it goes back to the caller), and no message holds any
    assert not any(n in i.message for i in issues
                   for n in ("stray_key", "stray_feature", "stray_expr"))
    assert not any(n in i.field for i in issues for n in ("stray_key", "stray_expr"))


@pytest.mark.req("FR-246")
def test_a_keyed_maps_entries_are_visited_in_sorted_key_order() -> None:
    """#1712 S7c second audit (S2): stored JSONB does not keep key order, so a save (request
    order) and a compile (stored order) must list a keyed map's entries the same way. The same
    algorithm with `feature_map` and `clamp_bounds` keys inserted in two orders gives the same
    issue list, in sorted key order."""

    def fields(reverse: bool) -> list[tuple[str, str, str]]:
        payload = copy.deepcopy(_algorithm_payload())
        for step in payload["steps"]:
            if step["step_id"] == "s_risk":
                items = [("driver_age", "age_years"), ("stray_a", "x"), ("stray_b", "y")]
                step["feature_map"] = dict(reversed(items) if reverse else items)
            elif step["step_id"] == "s_clamp":
                step["consumes"] = ["office_premium_minor"]
                items = [("max", "stray_c"), ("min", "stray_d")]
                step["clamp_bounds"] = dict(reversed(items) if reverse else items)
        issues = _fr246(validate_algorithm(RatingAlgorithm.model_validate(payload)))
        return [(i.step_id, i.code, i.field) for i in issues]

    forward, backward = fields(False), fields(True)
    assert forward == backward, (forward, backward)
    assert [f for s, _, f in forward if s == "s_risk"] == [
        "feature_map.stray_a",
        "feature_map.stray_b",
    ]
    assert [f for s, _, f in forward if s == "s_clamp"] == [
        "condition",
        "clamp_bounds.max",
        "clamp_bounds.min",
    ]


@pytest.mark.req("FR-246")
async def test_the_compile_refusal_for_an_undeclared_feature_map_key_carries_no_key() -> None:
    """#1712 S7c: what a Job stores is the `CodedError` text. It is the code and the literal
    message, no field and no key. (DB-free: the text is raised here, before any Job row.)"""
    example = _one_name_example()
    step = next(s for s in example["steps"] if s["type"] == "model_call")
    step["feature_map"] = {**step.get("feature_map", {}), "stray_feature": "x"}
    with pytest.raises(CodedError) as caught:
        await _compile(example)
    text = str(caught.value)
    assert text.startswith("RATING_STEP_UNDECLARED_READ:"), text
    assert "stray_feature" not in text, text


@pytest.mark.req("FR-246")
def test_the_fixed_fixture_declares_every_read() -> None:
    assert _fr246(validate_algorithm(RatingAlgorithm.model_validate(_algorithm_payload()))) == []


_SPEC_03 = Path(__file__).resolve().parents[3] / "docs" / "specs" / "03-rating-engine.md"


def _spec_example() -> dict[str, Any]:
    """`03` §4.1's example, verbatim: the first ```json block after the `### 4.1 ` heading."""
    lines = _SPEC_03.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("### 4.1 "))
    opening = next(i for i in range(start, len(lines)) if lines[i].startswith("```json"))
    closing = next(i for i in range(opening + 1, len(lines)) if lines[i].startswith("```"))
    payload: dict[str, Any] = json.loads("\n".join(lines[opening + 1 : closing]))
    return payload


class _StubResolver:
    """The example's own algorithm, and an approved stub payload for every other pinned ref.

    `compile_bundle` resolves each pin for its status and stores the payload verbatim, and it
    never parses a pinned payload, so a stub is enough for it to run.
    """

    def __init__(self, algorithm_ref: str, algorithm: dict[str, Any]) -> None:
        self._algorithm_ref = algorithm_ref
        self._algorithm = algorithm

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        if str(ref) == self._algorithm_ref:
            return ResolvedArtifact(status="approved", payload=self._algorithm)
        if ref.type == "peril_structure":
            # A-3's compile parses the structure (RL-1459), so it needs a real one, not a stub.
            return ResolvedArtifact(status="approved", payload=_structure_payload())
        payload: dict[str, Any] = {"stub_for": str(ref)}
        if ref.type == "model":
            # FD-1495 (SL-1985): a pinned model carries the fields its consumed Factors are
            # derived from; the stub consumes exactly what the example's model_call steps map.
            mapped = {
                value
                for step in self._algorithm["steps"]
                if step["type"] == "model_call"
                for value in step["feature_map"].values()
            }
            payload["fit_result"] = {"model_type": "xgboost", "feature_order": sorted(mapped)}
        return ResolvedArtifact(status="approved", payload=payload)


def _example_version(example: dict[str, Any]) -> RatingVersion:
    """A draft Rating Version pinning exactly the refs the example's steps name, mirroring
    `test_rating_score._version()`."""
    steps = example["steps"]
    rate = [s["rate_table_ref"] for s in steps if s.get("rate_table_ref")]
    reference = [s["reference_table_ref"] for s in steps if s.get("reference_table_ref")]
    models = [
        s.get("model_ref") or s["peril_structure_ref"] for s in steps if s["type"] == "model_call"
    ]
    modes = {s["mode"] for s in steps if s["type"] == "model_call"}
    return RatingVersion.model_validate({
        "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": example["slug"],
        "version": example["version"], "status": "draft", "dataset_version_id": str(uuid4()),
        "model_ref": models[0] if models else None,
        "created_at": "2026-10-01T00:00:00Z", "created_by": str(uuid4()),
        "updated_at": "2026-10-01T00:00:00Z",
        "algorithm_ref": f"rating_algorithm:{example['slug']}@{example['version']}",
        "pins": {"rate_tables": rate, "models": models, "reference_tables": reference,
                 "custom_objectives": []},
        "model_reference_mode": modes.pop() if len(modes) == 1 else "exact",
    })


def _example_with_s_rp_producing(names: list[str]) -> dict[str, Any]:
    """The example with its Peril Structure step `s_rp` set to exactly `names`, whatever 03 §4.1
    declares for it at run time (the text is known-wrong, FD 9953 (working id), and a correction
    must not change this test). The per-peril output step and output go, as nothing produces
    their name in the one-name form."""
    example = copy.deepcopy(_spec_example())
    for step in example["steps"]:
        if step["step_id"] == "s_rp":
            step["produces"] = names
    example["steps"] = [s for s in example["steps"] if s["step_id"] != "s_out_peril"]
    example["outputs"] = [o for o in example["outputs"] if o["name"] != "peril_risk_premium"]
    return example


def _one_name_example() -> dict[str, Any]:
    return _example_with_s_rp_producing(["risk_premium_minor"])


async def _compile(example: dict[str, Any]) -> Any:
    version = _example_version(example)
    assert version.algorithm_ref is not None
    return await compile_bundle(version, _StubResolver(str(version.algorithm_ref), example))


@pytest.mark.req("FR-246")
async def test_the_03_example_validates_in_full() -> None:
    """`RatingAlgorithm.model_validate` in full (FR-212, FR-214, every field)."""
    RatingAlgorithm.model_validate(_spec_example())


@pytest.mark.req("FR-246")
async def test_the_one_name_form_of_the_03_example_compiles_with_its_reads_declared() -> None:
    """`compile_bundle` runs `validate_algorithm`, so the declared-reads check, over the example
    with `s_rp` producing one name (RL-1459 DP-A3-1 (c))."""
    bundle = await _compile(_one_name_example())
    assert bundle.content_hash.startswith("sha256:")


@pytest.mark.req("FR-249")
async def test_a_peril_structure_model_call_producing_two_names_is_refused_at_compile() -> None:
    """The RULE (RL-1459 DP-A3-1 (c); the lead's ruling of 2026-10-10 14:43:15 BST): a Peril
    Structure `model_call` produces one name; two are refused with BUNDLE_COMPILE_FAILED naming
    the step. `03` §4.1's example (03:295-299, `s_rp`, as RL-1519 ruled it) declares two and is
    KNOWN-WRONG text pending a correcting RL (FD 9953 (working id)): do not read it as valid.
    The two-name step is built here, not read from 03, so a correction of the text leaves this
    test green. Red before the rework: the old test compiled that example and failed with this
    very code."""
    two = _example_with_s_rp_producing(["risk_premium_minor", "peril_risk_premium"])
    with pytest.raises(CodedError, match=r"BUNDLE_COMPILE_FAILED: step 's_rp'.*2 produced names"):
        await _compile(two)
    assert (await _compile(_one_name_example())).content_hash.startswith("sha256:")


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    return [str(v) for v in (value if isinstance(value, list) else [value])]


@pytest.mark.req("FR-246")
def test_the_03_example_declares_every_read() -> None:
    """The declared-reads check stated on its own, over the raw step dicts, so its red is
    visible even while the example fails validation."""
    undeclared = {
        step["step_id"]: sorted(referenced_names(step) - set(_as_list(step.get("consumes"))))
        for step in _spec_example()["steps"]
        if step["type"] not in ("input", "output")
    }
    undeclared = {sid: names for sid, names in undeclared.items() if names}
    assert undeclared == {}, f"03 §4.1 steps read undeclared names: {undeclared}"


@pytest.mark.req("FR-246")
def test_a_mounted_fragment_passes_the_declared_reads_check_once_inlined() -> None:
    """The planner's semantic risk (PL-1535): SL-1340's inliner renames the fields a step
    evaluates with `rename_tokens`, and the check reads them with `references._names_in`. Two
    tokenizers over one set of fields must agree: the inlined fragment's renamed `expr`, its
    renamed `consumes` and the mapped ports leave no read undeclared. A guard, not a red-first:
    it passed on first run, so no defect was exposed."""
    from test_rating_inline import _fragment, _parent

    from pricing_core.rating.inline import inline_mounts

    ref = "sub_graph:ncd-ladder@4"
    inlined = inline_mounts(_parent(), {ref: _fragment()})
    assert any(s.step_id.startswith("m_ncd__") for s in inlined.steps)
    issues = [i for i in validate_algorithm(inlined) if i.code == UNDECLARED_READ_CODE]
    assert issues == []

    # Control: the same path flags a fragment step that reads a name it does not declare, so the
    # empty list above is the check running, not the check failing to see the fragment.
    broken = _fragment(steps=[
        {"step_id": "s_ladder", "type": "expression", "label": "Ladder",
         "expr": "ncd_years * stray", "result_type": "decimal",
         "consumes": ["ncd_years"], "produces": "ncd_factor"},
    ])
    flagged = [i for i in validate_algorithm(inline_mounts(_parent(), {ref: broken}))
               if i.code == UNDECLARED_READ_CODE]
    assert [i.step_id for i in flagged] == ["m_ncd__s_ladder"]


def _undeclared_issue_steps(as_at: str) -> list[str]:
    from test_rating_lookup_as_at import _algo

    algorithm = RatingAlgorithm.model_validate(_algo(as_at=as_at))
    return [i.step_id for i in validate_algorithm(algorithm) if i.code == UNDECLARED_READ_CODE]


@pytest.mark.req("FR-246")
def test_a_lookup_as_at_the_stamped_date_declares_nothing() -> None:
    """Ruling 2026-10-10 15:40:36 BST: `as_at: "effective_date"` is the quote's stamped date
    (FR-221, RL-1446), not a read FR-246 counts. Red before the exemption (s_area flagged)."""
    assert _undeclared_issue_steps("effective_date") == []


@pytest.mark.req("FR-246")
def test_a_lookup_as_at_any_other_undeclared_name_is_still_refused() -> None:
    """The guard on the exemption's width: any other `as_at` is a read and must be declared.
    Green before and after the exemption."""
    assert _undeclared_issue_steps("inception") == ["s_area"]


@pytest.mark.req("FR-246")
def test_an_expression_reading_the_stamped_date_as_a_value_still_declares_it() -> None:
    """The narrowing: only the lookup's `as_at` is exempt; an expression reading
    `effective_date` as a value is a read."""
    expr = {"type": "expression", "consumes": [], "produces": "c", "expr": "effective_date"}
    assert referenced_names(expr) == {"effective_date"}
