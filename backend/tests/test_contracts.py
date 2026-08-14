"""FR-PLAT-48 / ADR-0002 — the committed contract follows the models, and is checked.

Two distinct claims are tested here, and conflating them is how a generated contract
becomes decorative:

1. **Freshness.** The committed files match what the models produce right now.
2. **Conformance.** Where a shape has both a hand-authored Phase 0 contract and a
   generated one, they agree. This is the mechanism `CLAUDE.md` §0 asks for — when code
   and spec disagree, the disagreement surfaces instead of being resolved by whichever was
   edited last.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GENERATED = ROOT / "docs" / "contracts" / "schemas" / "generated"
AUTHORED = ROOT / "docs" / "contracts" / "schemas"
OPENAPI = ROOT / "docs" / "contracts" / "openapi" / "generated.json"
GENERATOR = ROOT / "scripts" / "generate-contracts.py"


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.req("FR-PLAT-48")
def test_committed_contracts_match_the_models() -> None:
    """The check CI runs. A failure here means someone changed a model without regenerating."""
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.req("FR-PLAT-48")
def test_generated_document_is_openapi_31() -> None:
    """OpenAPI 3.1, because it is the version whose schema dialect is JSON Schema 2020-12 —
    the same dialect `docs/contracts/schemas/` is written in."""
    assert _load(OPENAPI)["openapi"].startswith("3.1")


@pytest.mark.req("FR-PLAT-41")
def test_health_endpoints_are_published() -> None:
    paths = _load(OPENAPI)["paths"]
    assert {"/healthz", "/readyz", "/version"} <= set(paths)


@pytest.mark.req("FR-OVR-7")
def test_decimal_money_is_pinned_to_the_string_form() -> None:
    """Research F7: a bare `Decimal` renders as `anyOf: [number, string]`, and the number
    branch is the lossy binary form FR-OVR-7 forbids — a payload could satisfy the contract
    while violating the spec.

    Asserted against `DecimalStr` itself rather than by scanning today's generated files.
    No shape currently carries a money field, so a scan would pass without checking
    anything and would keep passing on the day one is added wrongly.
    """
    from decimal import Decimal

    from pydantic import BaseModel

    from model_schema import DecimalStr

    class Pinned(BaseModel):
        premium_minor: DecimalStr

    class Bare(BaseModel):
        premium_minor: Decimal

    # Both modes: a contract is only safe if the request side is safe too.
    for mode in ("validation", "serialization"):
        pinned = Pinned.model_json_schema(mode=mode)["properties"]["premium_minor"]
        assert pinned["type"] == "string", mode
        assert "anyOf" not in pinned, mode

    # The control that makes the assertion above non-trivial — and it only shows up in
    # validation mode. In serialization mode a bare Decimal is already a string, so a
    # contract generated from the serialization schema would look compliant while the
    # request side still accepted a lossy JSON number. That is why the generator emits
    # validation-mode schemas.
    bare = Bare.model_json_schema(mode="validation")["properties"]["premium_minor"]
    assert "anyOf" in bare
    assert any(branch.get("type") == "number" for branch in bare["anyOf"])
    assert "anyOf" not in Bare.model_json_schema(mode="serialization")["properties"][
        "premium_minor"
    ]


@pytest.mark.req("FR-OVR-7")
def test_no_generated_money_field_admits_a_json_number() -> None:
    """The scan, kept as a guard for the shapes that arrive later.

    It is deliberately paired with the test above: on its own it would report success
    across a set of schemas that contains nothing to check.
    """
    money_like = re.compile(r"(_minor$|relativity|premium|exposure)", re.I)
    offenders: list[str] = []

    def walk(node: object, path: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if money_like.search(key) and isinstance(value, dict):
                    branches = value.get("anyOf", [value])
                    if any(b.get("type") == "number" for b in branches):
                        offenders.append(f"{path}.{key}")
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")

    for schema in GENERATED.glob("*.schema.json"):
        walk(_load(schema), schema.stem)
    assert offenders == []


@pytest.mark.req("FR-OVR-6")
def test_artifact_ref_is_a_string_on_the_wire() -> None:
    """ID-3 makes `{type}:{slug}@{version}` the canonical external form.

    The model is structured in Python and flat in JSON. Before this was wired up, the
    generated schema described the Python object — three properties — so a frontend
    generated from it would have expected an object where every spec, trace and audit row
    carries a string.
    """
    generated = _load(GENERATED / "artifact-ref.schema.json")
    assert generated["type"] == "string"
    assert "properties" not in generated


@pytest.mark.req("FR-OVR-6")
def test_artifact_ref_pattern_matches_the_authored_contract() -> None:
    """Conformance: the Phase 0 contract and the model must accept the same strings."""
    generated = _load(GENERATED / "artifact-ref.schema.json")
    authored = _load(AUTHORED / "common" / "artifact-ref.schema.json")
    assert generated["pattern"] == authored["pattern"]


@pytest.mark.req("FR-OVR-6")
@pytest.mark.parametrize(
    ("reference", "valid"),
    [
        ("model:motor-ad-frequency@7", True),
        ("rating_version:motor-gb@27", True),
        ("model:motor-gb@0", False),           # ID-2: versions start at 1
        ("model:motor-gb@2026-04", False),     # ID-2: the version is an integer
        ("nonsense:motor-gb@1", False),        # not an artifact type
        ("model:Motor-GB@1", False),           # slugs are lowercase
        ("model:motor-gb", False),             # no version
    ],
)
def test_authored_pattern_accepts_exactly_what_the_parser_accepts(
    reference: str, valid: bool
) -> None:
    """Negative: the contract previously admitted `@0`, which the parser has always
    rejected. A contract looser than the code lets a client build something the platform
    refuses at runtime."""
    from model_schema import ArtifactRef

    authored = re.compile(_load(AUTHORED / "common" / "artifact-ref.schema.json")["pattern"])
    assert bool(authored.match(reference)) is valid

    if valid:
        assert str(ArtifactRef.model_validate(reference)) == reference
    else:
        # Both rejection paths say "artifact": a malformed reference and an unknown type.
        with pytest.raises(ValueError, match="artifact"):
            ArtifactRef.model_validate(reference)


@pytest.mark.req("FR-OVR-6")
@pytest.mark.parametrize("slug", ["job", "audit-event"])
def test_generated_and_authored_agree_on_field_names(slug: str) -> None:
    """The two descriptions of one shape must not drift apart silently."""
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")
    assert set(generated["properties"]) == set(authored["properties"])


@pytest.mark.req("FR-OVR-6")
def test_job_status_and_kind_enums_agree_with_the_contract() -> None:
    """An enum in the code but not the contract routes work nowhere; the reverse is a
    value a client may legitimately send and the platform will reject."""
    generated = _load(GENERATED / "job.schema.json")
    authored = _load(AUTHORED / "job.schema.json")

    for field in ("status", "queue", "source"):
        authored_values = set(authored["properties"][field]["enum"])
        ref = generated["properties"][field]["$ref"].rsplit("/", 1)[-1]
        generated_values = set(generated["$defs"][ref]["enum"])
        assert generated_values == authored_values, field

    authored_kinds = set(authored["properties"]["kind"]["enum"])
    kind_ref = generated["properties"]["kind"]["$ref"].rsplit("/", 1)[-1]
    assert set(generated["$defs"][kind_ref]["enum"]) == authored_kinds


@pytest.mark.req("FR-PLAT-48")
def test_the_phase_zero_design_stub_is_not_overwritten() -> None:
    """`gi-pricing.yaml` describes the whole intended surface across eight modules.

    Replacing it with generated output covering the routes built so far would delete the
    specification to make the tooling tidy. It retires when the generated document reaches
    it, not before.
    """
    stub = ROOT / "docs" / "contracts" / "openapi" / "gi-pricing.yaml"
    assert stub.exists()
    assert stub.stat().st_size > 10_000
