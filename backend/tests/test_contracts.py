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
from typing import Any, Final

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GENERATED = ROOT / "docs" / "contracts" / "schemas" / "generated"
AUTHORED = ROOT / "docs" / "contracts" / "schemas"
OPENAPI = ROOT / "docs" / "contracts" / "openapi" / "generated.json"
GENERATOR = ROOT / "scripts" / "generate-contracts.py"

#: Schemas whose authored and generated sides are compared field-type by field-type. Written
#: out rather than globbed so that adding one is a visible act; `test_every_eligible_schema_
#: is_compared` is what stops the list going quietly stale, which is how `peril-structure`
#: sat outside it declaring three exact decimals as JSON numbers (`OQ-OVR-8`, 2026-08-19).
COMPARED_SLUGS: Final[tuple[str, ...]] = (
    "audit-event",
    "banding",
    "custom-objective",
    "diagnostics",
    "grouping",
    "job",
    "model",
    "model-spec",
    "objective-certificate",
    "peril-structure",
    "profile",
    "transparency-artifact",
)


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(document: dict, node: dict) -> dict:
    """Follow a local `$ref` one hop. Pydantic nests models through `$defs`."""
    ref = node.get("$ref")
    if ref is None:
        return node
    return document["$defs"][ref.rsplit("/", 1)[-1]]


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

    #: `x_per_y` is a **ratio**, not a quantity of `x`. FR-MODEL-81's
    #: `exposure_per_parameter` is exposure divided by a count, and dividing a decimal
    #: exposure by an integer does not produce a decimal exposure — it produces a number
    #: whose precision carries no monetary meaning.
    #:
    #: A rule rather than a hand-written list of names. OQ-OVR-7 objects to money-discipline
    #: exceptions maintained as a hand-written list precisely because such lists only grow;
    #: this one recognises a *shape* of name, so the next ratio needs no entry and no
    #: decision.
    #:
    #: Deliberately **not** a general `_per_\\w+$`: `premium_per_policy` is an average
    #: premium and is money, so a blanket ratio rule would open the hole this test exists to
    #: close. Only `_per_parameter` is dimensionless here — a model's parameter count is a
    #: property of the fit, not of the book.
    #: `_share` joins `_per_parameter` for the same reason and by the same rule rather than
    #: as another name: a share is a proportion of a total, dimensionless by construction
    #: and bounded to [0, 1] by the field itself. `exposure_share` is not a quantity of
    #: exposure any more than `exposure_per_parameter` is, and rounding either to minor
    #: units would be rounding a ratio. (Added 2026-08-17, when partial dependence and the
    #: transparency artifact both introduced one.)
    ratio_suffix = re.compile(r"(_per_parameter|_share)$", re.I)

    #: Two `02` types every number on which is a **fitted estimate**, not a quantity:
    #: `Coefficient` and `RelativityLevel` carry `exp(β)` and the exposure it was measured
    #: over, each beside its own confidence interval. Rounding an estimate to a money grid
    #: would misstate the interval printed next to it — the same reason `01`'s one-way row
    #: keeps its own mean fields as floats (FR-DATA-46).
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

#: `custom-objective` declares `template` and `params` inside an `if kind == template`
#: branch rather than in `properties` — the same carry-through as the envelope, for the
#: same reason: the field is declared, just not where a flat set-comparison looks.
CONDITIONAL_FIELDS: Final[dict[str, frozenset[str]]] = {
    "custom-objective": frozenset({"template", "params"}),
}


@pytest.mark.req("FR-OVR-6")
@pytest.mark.parametrize("slug", ["banding", "grouping", "custom-objective", "profile"])
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

    declared = set(authored["properties"]) | CONDITIONAL_FIELDS.get(slug, frozenset())
    produced = set(generated["properties"])
    assert not declared - produced, (
        f"the contract declares fields the model lacks: {sorted(declared - produced)}"
    )
    assert not produced - declared - ENVELOPE_FIELDS, (
        "the model produces fields the contract does not declare: "
        f"{sorted(produced - declared - ENVELOPE_FIELDS)}"
    )


@pytest.mark.req("FR-OVR-6")
def test_the_column_profile_shape_matches_its_contract() -> None:
    """The profile's divergences live one level down, where the flat tests do not look.

    `test_an_artifact_shape_carries_exactly_what_its_contract_declares` compares top-level
    properties. `ColumnProfile` is nested inside `columns.items`, which is where the
    histogram was missing for three days and where `min`/`minimum` still disagreed — so a
    flat comparison would have reported this contract as conforming throughout.

    `top_levels` is nested a level deeper still, and until FR-DATA-49 that second hop was
    where a *structural* disagreement hid: the model carried an unnamed `(str, int)` pair
    and the contract declared `{level, count, exposure_years}`, but `top_levels` itself
    existed on both sides, so comparing only this function's first-level property-name set
    reported the contract as conforming. Descending into the item and comparing *its*
    property names is what makes that class of defect visible instead of merely matching
    the container's name.
    """
    generated = _load(GENERATED / "profile.schema.json")
    authored = _load(AUTHORED / "profile.schema.json")

    produced_column = _resolve(generated, generated["properties"]["columns"]["items"])
    declared_column = authored["properties"]["columns"]["items"]["properties"]

    produced = set(produced_column["properties"])
    declared = set(declared_column)

    assert not declared - produced, (
        f"the contract declares column fields the model lacks: {sorted(declared - produced)}"
    )
    assert not produced - declared, (
        "the model produces column fields the contract does not declare: "
        f"{sorted(produced - declared)}"
    )

    produced_top_level = _resolve(generated, produced_column["properties"]["top_levels"]["items"])
    declared_top_level = _resolve(authored, declared_column["top_levels"]["items"])

    produced_top_level_fields = set(produced_top_level["properties"])
    declared_top_level_fields = set(declared_top_level["properties"])

    assert not declared_top_level_fields - produced_top_level_fields, (
        "the contract declares top_levels fields the model lacks: "
        f"{sorted(declared_top_level_fields - produced_top_level_fields)}"
    )
    assert not produced_top_level_fields - declared_top_level_fields, (
        "the model produces top_levels fields the contract does not declare: "
        f"{sorted(produced_top_level_fields - declared_top_level_fields)}"
    )


#: How many `$ref` hops to follow before concluding the document is cyclic. A contract that
#: needs more than this is malformed, and looping forever in a test reads as a hung suite.
_MAX_REF_HOPS: Final = 20

#: JSON type names for the Python values an `enum` list holds. A hand-authored enum is
#: written `{"enum": [...]}` with no `"type"`; the generated one carries `"type": "string"`
#: beside the same members. Deriving the type from the members makes the two comparable
#: instead of reporting every enum in the suite as a divergence.
_JSON_TYPE_OF: Final[dict[type, str]] = {
    bool: "boolean",
    int: "integer",
    float: "number",
    str: "string",
}

def _deref(document: dict[str, Any], node: dict[str, Any], base: pathlib.Path) -> tuple[
    dict[str, Any], dict[str, Any]
]:
    """Follow `$ref`, local or into a sibling file, returning the node and its document.

    `_resolve` follows one local hop, which is all the flat comparisons need. The authored
    contracts reach across files — `common/money.schema.json#/$defs/MoneyMinor` — and the
    whole point of comparing types is to see what is on the far end of that reference.
    """
    for _ in range(_MAX_REF_HOPS):
        ref = node.get("$ref")
        if ref is None:
            return node, document
        filename, _, fragment = ref.partition("#")
        if filename:
            document = _load(base / filename)
        cursor: Any = document
        for part in fragment.lstrip("/").split("/"):
            if part:
                cursor = cursor[part]
        node = cursor
    raise AssertionError(f"more than {_MAX_REF_HOPS} $ref hops — the document is cyclic")


def _variants(
    document: dict[str, Any], node: dict[str, Any], base: pathlib.Path
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """The node itself plus every `anyOf`/`oneOf`/`allOf` branch beneath it, dereferenced.

    An optional field is `anyOf: [{...}, {"type": "null"}]` when generated and a bare type
    when authored. Flattening both to the set of branches lets one comparison read them the
    same way, which is what makes `severity_ci` — an optional *array* — comparable at all.
    """
    node, document = _deref(document, node, base)
    found = [(document, node)]
    for keyword in ("anyOf", "oneOf", "allOf"):
        for branch in node.get(keyword, []):
            found.extend(_variants(document, branch, base))
    return found


def _scalar_types(
    document: dict[str, Any], node: dict[str, Any], base: pathlib.Path
) -> set[str]:
    """The JSON types this node admits, ignoring `null`.

    `null` is dropped deliberately. The generated contracts mark every `X | None` nullable
    and the authored ones mark almost none, so comparing nullability would report a
    divergence on nearly every optional field — a uniform difference of idiom, not the
    integer-for-a-float this test exists to find. Nullability is worth reconciling, but as
    its own change against the whole authored suite, not smuggled in here.
    """
    admitted: set[str] = set()
    for owner, variant in _variants(document, node, base):
        declared = variant.get("type")
        if isinstance(declared, str):
            admitted.add(declared)
        elif isinstance(declared, list):
            admitted.update(declared)
        for member in variant.get("enum", ()):
            named = _JSON_TYPE_OF.get(type(member))
            if named is not None:
                admitted.add(named)
        del owner
    return admitted - {"null"}


def _type_map(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    path: str = "",
) -> dict[str, frozenset[str]]:
    """Flatten a schema to `dotted.path -> admitted JSON types`, descending into arrays.

    Both array spellings are followed. A variable-length array declares `items`; a
    **fixed-length tuple declares `prefixItems`**, one entry per position, and Pydantic
    emits `tuple[float, float]` that way. Reading only `items` makes this walker silently
    blind to every tuple field — which is exactly what it was, until `severity_ci` failed
    to fail. Element positions collapse onto one `.[]` path: a contract that types position
    0 differently from position 1 is a separate defect, and a comparison that reported it
    as a type mismatch would be describing the wrong problem.
    """
    found: dict[str, frozenset[str]] = {}
    properties: dict[str, Any] = {}
    elements: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for owner, variant in _variants(document, node, base):
        properties.update(variant.get("properties", {}))
        if "items" in variant:
            elements.append((owner, variant["items"]))
        elements.extend((owner, entry) for entry in variant.get("prefixItems", ()))

    if properties:
        for name, child in sorted(properties.items()):
            found.update(_type_map(document, child, base, f"{path}.{name}".lstrip(".")))
        return found
    if elements:
        for owner, child in elements:
            for key, types in _type_map(owner, child, base, f"{path}.[]".lstrip(".")).items():
                found[key] = found.get(key, frozenset()) | types
        return found

    types = _scalar_types(document, node, base)
    if types:
        found[path] = frozenset(types)
    return found


@pytest.mark.req("FR-OVR-6")
@pytest.mark.req("FR-DATA-46")
@pytest.mark.parametrize("slug", COMPARED_SLUGS)
def test_generated_and_authored_agree_on_scalar_types(slug: str) -> None:
    """The same field must not be a float in the model and an integer in the contract.

    Every conformance test above this one compares field *names*. Names agreeing is a
    weaker claim than it looks: `OneWayRow.mean_severity` and `mean_burning_cost` were
    declared `float | None` by the model and `MoneyMinor` — `{"type": "integer"}` — by the
    hand-authored contract in both `banding` and `profile`, and `profile`'s `severity_ci`
    typed its interval bounds as integers while `banding`'s copy of the identical shape
    typed them as numbers. A mean severity of 45812.42 fails all four. Nothing failed,
    because the names matched, and the rename in FR-DATA-46 carried the names across
    without ever looking at the type beneath them.

    That is the divergence FR-DATA-46 exists to prevent, stated in the contract itself: a
    mean is a statistic, not an amount, and rounding it to minor units discards the
    precision the confidence interval beside it is expressing.

    Only paths present on **both** sides are compared, so a difference of *structure* is
    skipped rather than reported. `ColumnProfile.top_levels` used to be the live example:
    the model produced an array of `[level, count]` pairs against a contract declaring an
    array of objects, the two sides shared no path, and this test said nothing about it.
    **Corrected 2026-08-19 (FR-DATA-49):** the model now carries `LevelCount` —
    `{level, count, exposure_years}` — matching the contract's shape, so
    `columns.[].top_levels.[].level/.count/.exposure_years` are paths on both sides and
    this test does compare them; it currently finds no disagreement, `exposure_years`
    included, which is `DecimalStr` versus the contract's `Decimal` `$ref` — both strings.
    The scope line is still deliberate: a conformance test that grows an exemption list is
    one nobody reads, and this one is precise about types exactly because it does not try
    to arbitrate structure — `test_the_column_profile_shape_matches_its_contract` does
    that, one level into `top_levels`' item.

    **Widened 2026-08-19 (`OQ-OVR-8`).** The list covered six slugs while twelve schemas
    have both an authored and a generated side, and the six it omitted were not chosen —
    they were simply never added. `peril-structure` was one of them, and it declared
    `restoration_loading`, `ratio` and `tolerance` as `{"type": "number"}` while all three
    are exact decimals the model has always serialised as strings. A client following the
    published contract would have posted a JSON number; before `OQ-OVR-8` that was silently
    coerced, after it the request is refused. The check that existed would have caught it on
    the day it was written, and did not, because the schema was outside its parametrize
    list — which is the argument for deriving the list rather than curating it. It is still
    written out here rather than globbed, because a slug appearing without anyone noticing is
    how the *other* direction of this failure starts; `test_every_eligible_schema_is_compared`
    below is what keeps the written list honest.

    Every eligible slug is now compared. The last excused one, `diagnostics`, was corrected
    on 2026-08-21 (`OQ-MODEL-15` decided — FR-MODEL-109): `aliasing` is an array of the
    strings the model always produced, and the pin that excused it is deleted rather than
    relaxed.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    produced = _type_map(generated, generated, GENERATED)
    declared = _type_map(authored, authored, AUTHORED)

    compared = set(produced) & set(declared)
    disagreed = {
        path: (sorted(produced[path]), sorted(declared[path]))
        for path in sorted(compared)
        if produced[path] != declared[path]
    }
    assert not disagreed, (
        "the model and the contract disagree on the type of "
        + ", ".join(f"{p} (model {g}, contract {a})" for p, (g, a) in disagreed.items())
    )


@pytest.mark.req("FR-OVR-6")
def test_every_eligible_schema_is_compared() -> None:
    """A curated list is only as good as the thing that notices it went stale.

    The parametrize list above is written out rather than globbed, so that adding a schema
    is a visible act. This is the other half of that bargain: every slug with both an
    authored and a generated side must be compared. The one excused slug, `diagnostics`,
    was corrected on 2026-08-21 (FR-MODEL-109) and the pin that excused it retired with it,
    which is why no exemption mechanism remains. Widening the list on 2026-08-19 found a
    contract that had been wrong since Phase 0 precisely because nothing enforced this.
    """
    eligible = {
        path.name.split(".")[0]
        for path in GENERATED.glob("*.schema.json")
        if (AUTHORED / path.name).exists()
    }
    unaccounted = eligible - set(COMPARED_SLUGS)
    assert not unaccounted, (
        "these schemas have both an authored and a generated side and are not compared: "
        f"{sorted(unaccounted)}"
    )


@pytest.mark.req("FR-DATA-46")
@pytest.mark.parametrize(
    ("slug", "row"), [("banding", "band_stats.[]"), ("profile", "one_ways.[].rows.[]")]
)
def test_the_type_comparison_reaches_the_one_way_row(slug: str, row: str) -> None:
    """The control for the test above, which compares only paths present on both sides.

    That scope rule is what keeps the comparison quiet about idiom, and it is also how the
    comparison could go silent altogether: a walker that stops descending aligns nothing,
    finds no disagreement, and passes. Counting aligned paths does not catch it — the count
    of what the walker produced shrinks along with the walker, so any threshold expressed
    as a fraction of its own output moves out of the way of the defect it is meant to catch.

    So this names the paths instead. All three are fields FR-DATA-46 governs, and
    `severity_ci` is the one that matters most: it is a `tuple[float, float]`, which Pydantic
    emits as `prefixItems` rather than `items`, and the first version of the walker read only
    `items`. Every tuple field in every contract was invisible to it, and nothing said so —
    the comparison passed with the interval bounds deliberately typed as integers.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")
    compared = set(_type_map(generated, generated, GENERATED)) & set(
        _type_map(authored, authored, AUTHORED)
    )

    wanted = {f"{row}.mean_severity", f"{row}.mean_burning_cost", f"{row}.severity_ci.[]"}
    assert wanted <= compared, (
        f"the type comparison no longer reaches {sorted(wanted - compared)} in {slug} — "
        "it is passing because it stopped looking, not because the contracts agree"
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
