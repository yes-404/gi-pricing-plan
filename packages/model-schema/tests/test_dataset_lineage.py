"""`01` §4.9's DatasetLineage — the wire form of FR-75, defined here first."""

import pytest
from pydantic import ValidationError

from model_schema.datasets import (
    DatasetLineage,
    LineageBuiltFrom,
    LineageDerivedVersion,
    LineageModel,
)

# The example JSON from `01` §4.9 (`:777-782`), verbatim apart from concrete ids.
EXAMPLE = {
    "version_id": "11111111-1111-4111-8111-111111111111",
    "built_from": {
        "parent_version_id": "22222222-2222-4222-8222-222222222222",
        "operation": "sample",
        "parameters": {},
    },
    "depends_on_this": {
        "derived_versions": [
            {"version_id": "33333333-3333-4333-8333-333333333333", "version": 3,
             "operation": "split"},
        ],
        "models": [
            {"model_id": "44444444-4444-4444-8444-444444444444",
             "slug": "motor-freq-2026", "status": "approved"},
        ],
        "rating_versions": [],
        "monitoring_baselines": [],
    },
}


def test_the_spec_example_round_trips() -> None:
    """§4.9's example is a claim about the wire: parse it, emit it, get it back."""
    parsed = DatasetLineage.model_validate(EXAMPLE)
    assert parsed.model_dump(mode="json") == EXAMPLE
    assert parsed.built_from == LineageBuiltFrom(
        parent_version_id="22222222-2222-4222-8222-222222222222",
        operation="sample",
        parameters={},
    )
    assert parsed.depends_on_this.derived_versions == [
        LineageDerivedVersion(
            version_id="33333333-3333-4333-8333-333333333333", version=3, operation="split"
        )
    ]
    assert parsed.depends_on_this.models == [
        LineageModel(
            model_id="44444444-4444-4444-8444-444444444444",
            slug="motor-freq-2026",
            status="approved",
        )
    ]


def test_built_from_is_nullable_for_a_root_version() -> None:
    """§4.9: `direction=down` returns `built_from: null` — and a version with no
    parent has no `built_from` in any direction."""
    root = {**EXAMPLE, "built_from": None}
    assert DatasetLineage.model_validate(root).built_from is None


def test_the_declared_empty_arms_are_present_and_empty() -> None:
    """§4.9: a key that appears and disappears is a second shape. Both arms are
    always on the wire, so a blast radius cannot silently read as one of one."""
    parsed = DatasetLineage.model_validate({**EXAMPLE, "depends_on_this": {
        "derived_versions": [],
        "models": [],
        "rating_versions": [],
        "monitoring_baselines": [],
    }})
    dumped = parsed.model_dump(mode="json")
    assert dumped["depends_on_this"]["rating_versions"] == []
    assert dumped["depends_on_this"]["monitoring_baselines"] == []


def test_the_shape_is_closed_and_frozen() -> None:
    """A shape defined twice diverges (CLAUDE.md §2): the wire refuses both a stray
    key and a missing one, and no caller can mutate a parsed response."""
    with pytest.raises(ValidationError):
        DatasetLineage.model_validate({**EXAMPLE, "surprise": 1})
    with pytest.raises(ValidationError):
        DatasetLineage.model_validate({**EXAMPLE, "built_from": {
            "parent_version_id": "22222222-2222-4222-8222-222222222222"}})
    parsed = DatasetLineage.model_validate(EXAMPLE)
    with pytest.raises(ValidationError):
        parsed.version_id = "55555555-5555-4555-8555-555555555555"
