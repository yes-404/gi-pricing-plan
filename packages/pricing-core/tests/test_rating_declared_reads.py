"""PL-1520 Task 1A (FR-246, FD-1374): a step reads only names it declares."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from pricing_core.rating.references import referenced_names
from test_rating_score import _algorithm_payload

from model_schema.rating import RatingAlgorithm, RatingVersion
from model_schema.refs import ArtifactRef
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle, validate_algorithm

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
            "expr": "a * b + round(a, 'half_even', 0)"}
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
    assert referenced_names(lookup) == {"postcode_outcode", "effective_date"}


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
    assert [(i.step_id, i.code) for i in issues] == [("s_clamp", UNDECLARED_READ_CODE)], issues
    assert "min_premium_minor" in issues[0].message


@pytest.mark.req("FR-246")
def test_an_expression_reading_an_undeclared_name_is_refused() -> None:
    payload = copy.deepcopy(_algorithm_payload())
    for step in payload["steps"]:
        if step["step_id"] == "s_office":
            step["expr"] = "risk_premium_minor * expense_factor * sanity_cap_minor"
    issues = _fr246(validate_algorithm(RatingAlgorithm.model_validate(payload)))
    assert [(i.step_id, i.code) for i in issues] == [("s_office", UNDECLARED_READ_CODE)], issues


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
        return ResolvedArtifact(status="approved", payload={"stub_for": str(ref)})


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


@pytest.mark.req("FR-246")
async def test_the_03_example_validates_in_full_and_compiles() -> None:
    """`RatingAlgorithm.model_validate` in full (FR-212, FR-214, every field), then
    `compile_bundle`, which runs `validate_algorithm` and so the declared-reads check."""
    example = _spec_example()
    RatingAlgorithm.model_validate(example)
    version = _example_version(example)
    assert version.algorithm_ref is not None
    bundle = await compile_bundle(version, _StubResolver(str(version.algorithm_ref), example))
    assert bundle.content_hash.startswith("sha256:")


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
