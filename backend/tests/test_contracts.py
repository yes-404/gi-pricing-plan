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

    #: `01` FR-DATA-26's one-way row carries a **mean** severity and a **mean** burning
    #: cost. They are statistics, not amounts: `01` keeps them as floats deliberately,
    #: because rounding a mean to whole minor units would lose the precision the confidence
    #: interval beside it is expressing.
    #:
    #: The `_minor` suffix is what makes the scan flag them, and the suffix is the part that
    #: is wrong — FR-OVR-7 reserves it for integer minor units. Excluded here by name rather
    #: than by weakening the pattern, and **raised as OQ-OVR-7** rather than settled: the
    #: rename touches `01`'s published profile contract and every screen that reads it.
    #:
    #: Nothing else is excluded. These two surfaced only when `banding` and `grouping` began
    #: generating (they embed the one-way row); the scan had never reached them before.
    ratio_statistics = {"severity_minor", "burning_cost_minor"}

    #: `x_per_y` is a **ratio**, not a quantity of `x`. FR-MODEL-81's
    #: `exposure_per_parameter` is exposure divided by a count, and dividing a decimal
    #: exposure by an integer does not produce a decimal exposure — it produces a number
    #: whose precision carries no monetary meaning.
    #:
    #: A rule rather than two more names in `ratio_statistics`. OQ-OVR-7 objects to
    #: money-discipline exceptions maintained as a hand-written list precisely because such
    #: lists only grow; this one recognises a *shape* of name, so the next ratio needs no
    #: entry and no decision.
    #:
    #: Deliberately **not** a general `_per_\\w+$`: `premium_per_policy` is an average
    #: premium and is money, so a blanket ratio rule would open the hole this test exists to
    #: close. Only `_per_parameter` is dimensionless here — a model's parameter count is a
    #: property of the fit, not of the book.
    ratio_suffix = re.compile(r"_per_parameter$", re.I)

    #: Two `02` types every number on which is a **fitted estimate**, not a quantity:
    #: `Coefficient` and `RelativityLevel` carry `exp(β)` and the exposure it was measured
    #: over, each beside its own confidence interval. Rounding an estimate to a money grid
    #: would misstate the interval printed next to it, which is the same reason
    #: `ratio_statistics` above exists.
    #:
    #: Excluded by **owning type**, never by field name. `relativity` is also what a Rate
    #: Table entry is called (`03`), and that one *is* on the rating path, where
    #: `CLAUDE.md` §7 requires exact arithmetic. A bare `relativity` exclusion would open
    #: exactly the hole this test exists to close, and would open it in the module where
    #: it costs money. (Surfaced 2026-08-17, when `model` first generated — the scan had
    #: never reached these two types before.)
    estimate_types = {"Coefficient", "RelativityLevel"}
    owning_type = re.compile(r"\$defs\.([A-Za-z]+)\.properties$")

    def walk(node: object, path: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                owner = owning_type.search(path)
                if (
                    money_like.search(key)
                    and key not in ratio_statistics
                    and not ratio_suffix.search(key)
                    and not (owner and owner.group(1) in estimate_types)
                    and isinstance(value, dict)
                ):
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


#: Fields the `ArtifactEnvelope` contributes, which a hand-authored schema carries through
#: `allOf` rather than listing (`00` §4.3). They appear in the generated shape and not in
#: the authored one's `properties`, and that is not a divergence.
ENVELOPE_FIELDS = frozenset({"id", "slug", "version", "dataset_id"})


@pytest.mark.req("FR-OVR-6")
@pytest.mark.parametrize("slug", ["banding", "grouping"])
def test_an_artifact_shape_carries_exactly_what_its_contract_declares(slug: str) -> None:
    """Both directions, for the shapes with a hand-authored Phase-0 contract.

    `generate-contracts --check` compares the *generated* files against the models and is
    therefore silent about the twenty hand-written ones — so nothing compared the shape the
    code produces against the shape the contract promises. Four divergences accumulated in
    `Banding` and `Grouping` before anything noticed, and `main` moving is what surfaced
    them rather than any check:

    * a top-level `credibility_standard` the contract never had (it says
      `method_params.credibility_model`);
    * `band_stats` keyed by `label` in one schema and `level` in another, for the same
      statistics from the same requirement;
    * no `minimums` on the Banding, which the contract declares;
    * no `rationale` on the Grouping, which FR-MODEL-16 requires and the dossier prints
      verbatim.

    A missing field is a promise the platform breaks. An extra one is a shape defined twice,
    which `CLAUDE.md` §2 forbids because the two will diverge — and here a diverged shape is
    a mispricing.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    declared, produced = set(authored["properties"]), set(generated["properties"])
    assert not declared - produced, (
        f"the contract declares fields the model lacks: {sorted(declared - produced)}"
    )
    assert not produced - declared - ENVELOPE_FIELDS, (
        "the model produces fields the contract does not declare: "
        f"{sorted(produced - declared - ENVELOPE_FIELDS)}"
    )


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


# -- the error model in the published contract (found missing by audit, 2026-08-14) --------


@pytest.mark.req("FR-PLAT-48")
def test_the_contract_publishes_the_problem_shape() -> None:
    """The audit finding this guards against.

    The contract described only success shapes, so a client generated from it was typed
    against FastAPI's default `HTTPValidationError` — a shape the platform replaced and
    never emits — and had no type for the RFC 9457 problem it does. The drift check could
    not catch it: the contract faithfully described the code, and both were wrong.
    """
    schemas = _load(OPENAPI)["components"]["schemas"]
    assert "ProblemDetail" in schemas
    assert "FieldError" in schemas
    assert "HTTPValidationError" not in schemas
    assert "ValidationError" not in schemas


@pytest.mark.req("FR-PLAT-47")
def test_every_operation_documents_the_problems_it_returns() -> None:
    """A client cannot handle a status the contract does not mention."""
    paths = _load(OPENAPI)["paths"]
    # The unauthenticated operational surface. A scraper and a kubelet are infrastructure,
    # not principals, and are reachable only from inside the deployment — so these four
    # have no 401 to document. `/metrics` is here for that reason and not because it was
    # awkward: FR-PLAT-52 keeps identifiers out of its labels, so it discloses nothing.
    exempt = {"/healthz", "/readyz", "/version", "/metrics"}
    for path, operations in paths.items():
        if path in exempt:
            continue
        for method, operation in operations.items():
            documented = set(operation["responses"])
            assert "401" in documented, f"{method.upper()} {path}"
            assert documented - {"200", "201"}, f"{method.upper()} {path}"


@pytest.mark.req("FR-PLAT-47")
def test_problem_responses_advertise_the_rfc_9457_media_type() -> None:
    paths = _load(OPENAPI)["paths"]
    cancel = paths["/api/v1/jobs/{job_id}/cancel"]["post"]["responses"]["409"]
    assert "application/problem+json" in cancel["content"]
    assert (
        cancel["content"]["application/problem+json"]["schema"]["$ref"]
        == "#/components/schemas/ProblemDetail"
    )


@pytest.mark.req("FR-PLAT-47")
def test_the_settings_endpoints_are_published() -> None:
    assert "/api/v1/settings" in _load(OPENAPI)["paths"]
