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

import copy
import json
import pathlib
import re
import subprocess
import sys
from collections.abc import Iterable
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
    "dataset-version",
    "diagnostics",
    "grouping",
    "job",
    "model",
    "model-spec",
    "objective-certificate",
    "peril-structure",
    "profile",
    "transparency-artifact",
    "validation-report",
    "validation-rule",
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
    #: `_fraction` joins them on 2026-08-24 (W32-11), when `validation-report` first
    #: generated and `RuleResult.affected_exposure_fraction` reached this scan. It is the
    #: `_share` case under another word: `01` §4.6 declares it
    #: `{"type": ["number", "null"], "minimum": 0, "maximum": 1}` — a proportion of the
    #: affected exposure, dimensionless and bounded by the field itself, which a rule's
    #: `tolerance` is compared against. Both sides already agree it is a JSON number, so
    #: this is the heuristic's word list catching up with its own stated rule and not a
    #: money-discipline exception. FR-OVR-7 is untouched: no quantity of money is named
    #: `_fraction`, and a fraction rounded to minor units would be a rounded ratio.
    ratio_suffix = re.compile(r"(_per_parameter|_share|_fraction)$", re.I)

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


#: The schema a hand-authored contract composes to inherit `00` §4.3's envelope.
_ENVELOPE_SCHEMA: Final = "common/artifact-envelope.schema.json"

#: The envelope's field names, **read from the envelope contract** rather than listed here.
#:
#: It used to be the literal `{"id", "slug", "version", "dataset_id"}` — four names, of
#: which the envelope actually declares three and `dataset_id` is not one of them at all.
#: A hand-written copy of a published list is the shape-defined-twice `CLAUDE.md` §2
#: forbids, and this copy was wrong in both directions: it under-declared the envelope by
#: eleven fields, and it carried a `banding`/`grouping` field under a heading that had
#: nothing to do with it (see `MODEL_ONLY_UNRECONCILED`).
ENVELOPE_FIELDS: Final[frozenset[str]] = frozenset(
    _load(AUTHORED / "common" / "artifact-envelope.schema.json")["properties"]
)


def _composes_the_envelope(authored: dict[str, Any]) -> bool:
    """Whether this authored contract inherits `00` §4.3's envelope through `allOf`.

    The carve-out below is applied **only** to schemas that actually compose it. The flat
    exemption applied to every slug, which is why `TransparencyArtifact.id` and
    `Diagnostics.id` — required fields on artifacts that carry no envelope at all — were
    exempted from a check they should always have failed.
    """
    return any(
        entry.get("$ref") == _ENVELOPE_SCHEMA for entry in authored.get("allOf", [])
    )


#: **A recorded divergence the guard is told not to litigate** (W5 audit, 2026-08-22).
#:
#: Twelve authored contracts `allOf` the envelope and thereby promise fourteen fields.
#: `ArtifactEnvelope` is defined at `model_schema/envelope.py:16` and exported at
#: `model_schema/__init__.py:83` — and **no model in the package inherits from it**. `Model`
#: carries `id`, `version`, `status`; `PerilStructure` adds `slug` and `created_at`; the
#: other nine fields (`workspace_id`, `created_by`, `updated_at`, `archived_at`,
#: `parent_id`, `currency`, `labels`, `description`, `schema_version`) exist on no artifact.
#:
#: Composing the envelope is a data-model change across the whole suite, not a contract fix,
#: so it is **not** made here: the finding is recorded, the owner is the maintainer, and
#: this test stays silent about it rather than going red on nine fields nobody is fixing
#: today. `test_the_envelope_gap_is_still_the_shape_the_carve_out_assumes` below is what
#: stops the silence outliving the reason for it.
ENVELOPE_GAP_IS_RECORDED_NOT_FIXED: Final = True

#: Model-side fields no authored contract declares, **outside this slice's scope**.
#:
#: `dataset_id` is on `Factor`, `Banding` and `Grouping` (`modelling.py:133`, `:355`,
#: `:497`) and is declared by neither `banding.schema.json` nor `grouping.schema.json`,
#: which name `derived_on_dataset_version_id` instead. It sat inside `ENVELOPE_FIELDS`
#: labelled an envelope field, which it has never been. Named honestly here, for `01`/`02`'s
#: banding-and-grouping owner; W5 owns the six `02` artifact slugs and not these two.
MODEL_ONLY_UNRECONCILED: Final[dict[str, frozenset[str]]] = {
    "banding": frozenset({"dataset_id"}),
    "grouping": frozenset({"dataset_id"}),
}

#: Contract fields **declared and unbuilt on purpose**, each with a requirement and an owner.
#:
#: FR-MODEL-87 is the rule: *"§4 is a staged contract: a field is shown live only once a
#: slice populates it, and anything else is named in place with a dated note saying it is
#: declared-and-unbuilt and which workstream owns it"* (OQ-MODEL-8, decided 2026-08-17).
#: Deleting these from the published contract to make a test green would destroy exactly the
#: staging record that requirement exists to keep, and `CLAUDE.md` §0 forbids building them
#: to match: a later phase's capability is a spec change, not code.
#:
#: Each entry carries its note in the schema's own `description` beside the field, so a
#: reader of the contract meets the same fact as a reader of this list:
#:
#: * `model.custom_objective_ref` / `model-spec`'s `custom_objective_ref` — FR-MODEL-87,
#:   *"absent entirely … owned by Phase 1b"*. `ObjectiveBackend.glm` exists so an author can
#:   narrow applicability to a backend nothing reaches yet (`objectives.py:101-114`).
#: * `model-spec.filter` — FR-MODEL-87, same verdict, same owner.
#: * `model.transparency_artifact_id` — FR-MODEL-87, *"declared and unbuilt, as §4.8 already
#:   says of them … owned by W5"*. **Open question for the maintainer:** FR-MODEL-96 was
#:   built on 2026-08-19 and made the reference run the other way — `TransparencyArtifact`
#:   carries `model_id`, and R3 is enforced by query at
#:   `backend/src/app/platform/modelling.py:1147`, not by a column on `Model`. Whether the
#:   back-pointer is still wanted is a `CLAUDE.md` §0 question, not a test's to settle.
#: * `custom-objective`'s `if kind == "expression"` branch — `loss`, `derived`,
#:   `bound_symbols`, `parameters`. `ObjectiveKind.EXPRESSION` is Phase 2 behind
#:   `expression_objectives_enabled` (`objectives.py:75-81`) and `CustomObjective` **refuses
#:   to be constructed with it** (`objectives.py:8-12`), so the shape is not merely absent —
#:   it is refused by name (OQ-MODEL-1).
#:
#: The `if kind == "template"` branch is *not* here: `template` and `params` are built, and
#: the flattening above now sees them where the retired `CONDITIONAL_FIELDS` exemption used
#: to assert them by hand.
DECLARED_AND_UNBUILT: Final[dict[str, frozenset[str]]] = {
    "custom-objective": frozenset({"loss", "derived", "bound_symbols", "parameters"}),
    "model": frozenset({"custom_objective_ref", "transparency_artifact_id"}),
    "model-spec": frozenset({"custom_objective_ref", "filter"}),
}


def _declared_fields(
    document: dict[str, Any], node: dict[str, Any], base: pathlib.Path
) -> set[str]:
    """Every field name this schema declares, wherever it declares it.

    `set(schema["properties"])` was the whole of this, and it is blind to all three ways a
    contract in this suite names a field somewhere else:

    * **`allOf` composition.** `model` and `peril-structure` inherit `00` §4.3's envelope by
      reference, so fourteen of their fields live in another file. Reading only
      `properties` reported `PerilStructure.created_at` and `.status` as fields "the
      contract does not declare" when the contract declares both.
    * **`if`/`then` refinement.** `model-spec`'s two arms hold every GLM and GBM field it
      has; `custom-objective`'s hold the template and expression blocks.
    * **A discriminated union on the generated side.** `model-spec.schema.json` generates as
      `oneOf: [GlmSpec, GbmSpec, EbmSpec]` with **no top-level `properties` at all**, so the
      comparison did not merely miss fields — it raised `KeyError: 'properties'` and the
      slug could not be checked in either direction.

    `_variants` already resolves all three, so this is that walker asked for names instead
    of types.
    """
    names: set[str] = set()
    for _owner, variant, _arm in _variants(document, node, base):
        names.update(variant.get("properties", {}))
    return names


@pytest.mark.req("FR-OVR-6")
@pytest.mark.parametrize(
    "slug",
    [
        "banding",
        "grouping",
        "custom-objective",
        "profile",
        "model",
        "model-spec",
        "diagnostics",
        "transparency-artifact",
        "objective-certificate",
        "peril-structure",
    ],
)
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

    declared = _declared_fields(authored, authored, AUTHORED)
    produced = _declared_fields(generated, generated, GENERATED)

    exempt = DECLARED_AND_UNBUILT.get(slug, frozenset()) | MODEL_ONLY_UNRECONCILED.get(
        slug, frozenset()
    )
    if _composes_the_envelope(authored):
        exempt |= ENVELOPE_FIELDS

    assert not declared - produced - exempt, (
        f"the contract declares fields the model lacks: {sorted(declared - produced - exempt)}"
    )
    assert not produced - declared - exempt, (
        "the model produces fields the contract does not declare: "
        f"{sorted(produced - declared - exempt)}"
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


#: How deep to follow composition keywords before concluding the document is malformed.
#: `_deref` bounds `$ref` chains; this bounds `allOf`-inside-`then`-inside-`oneOf` nesting,
#: which no `$ref` hop has to appear in.
_MAX_COMPOSITION_DEPTH: Final = 40


#: The discriminator constraints in force at a node: `(dotted path of the discriminator
#: property, the values that reach here)`. The empty set is the unconditional arm — the node
#: is reached whatever the discriminator says — and it is what every union-free document
#: produces, so those documents keep behaving exactly as they did.
Arm = frozenset[tuple[str, frozenset[str]]]


def _discriminated_branches(node: dict[str, Any]) -> dict[str, frozenset[str]]:
    """`$ref` -> the discriminator values that select it, from an OpenAPI discriminator.

    The generated side's spelling. `discriminator.mapping` is value -> `$ref`, and this
    inverts it, which is what collapses `xgboost` and `lightgbm` onto the single `GbmSpec`
    branch they share.
    """
    discriminator = node.get("discriminator")
    if not isinstance(discriminator, dict):
        return {}
    inverted: dict[str, set[str]] = {}
    for value, ref in discriminator.get("mapping", {}).items():
        inverted.setdefault(ref, set()).add(value)
    return {ref: frozenset(values) for ref, values in inverted.items()}


def _condition_values(test: dict[str, Any]) -> tuple[str, frozenset[str]] | None:
    """The authored side's spelling: `{"if": {"properties": {"<name>": {"const"|"enum"}}}}`.

    Returns the constraint the sibling `then` is guarded by, or `None` when the `if` tests
    something this walker cannot express as a discriminator — a `required` test, or two
    properties at once. Returning `None` degrades that branch to unconditional, which is
    what the walker did for **every** branch before this change: strictly no worse.
    """
    properties = test.get("properties", {})
    if len(properties) != 1:
        return None
    ((name, constraint),) = properties.items()
    if "const" in constraint:
        return name, frozenset({constraint["const"]})
    if "enum" in constraint:
        return name, frozenset(constraint["enum"])
    return None


def _variants(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    *,
    path: str = "",
    arm: Arm = frozenset(),
    _depth: int = 0,
) -> list[tuple[dict[str, Any], dict[str, Any], Arm]]:
    """The node itself plus every composed subschema beneath it, dereferenced.

    An optional field is `anyOf: [{...}, {"type": "null"}]` when generated and a bare type
    when authored. Flattening both to the set of branches lets one comparison read them the
    same way, which is what makes `severity_ci` — an optional *array* — comparable at all.

    **`then`/`else` joined `anyOf`/`oneOf`/`allOf` on 2026-08-22 (W5).** A hand-authored
    contract refines a tagged union with `allOf: [{"if": …, "then": {"properties": …}}]`,
    and a walker reading only the three combinators sees a branch node carrying neither
    `properties` nor `type` and moves on. Every field in every conditional arm of the suite
    was therefore invisible: `model-spec` produced exactly its 12 flat properties and
    **nothing** from either arm — no `family`, no `link`, no `objective`, no
    `early_stopping` — and `model.spec` `$ref`s it, so a Model's whole specification went
    uncompared too. `CONDITIONAL_FIELDS` was the hand-maintained patch over one slug's
    corner of this, and it is deleted with this change rather than extended.

    `if` is deliberately **not** followed. It is the discriminator test, not a description
    of the artifact: reading it would fold `{"const": "glm"}` into `model_type`'s admitted
    types as though the contract declared a second field there.

    **The sibling `if` is now read for the arm *tag*, and still not for the description.**
    Each variant carries the discriminator constraints in force where it was found, so a
    caller can key on `(arm, path)` and stop a field moving between arms from reading as no
    change at all. What comes back as a *description* of the node is exactly what it was:
    the `if` contributes a tag, never a type, a closure or a constraint.
    """
    if _depth > _MAX_COMPOSITION_DEPTH:
        raise AssertionError(
            f"more than {_MAX_COMPOSITION_DEPTH} composition levels — the document nests "
            "without bottoming out"
        )
    node, document = _deref(document, node, base)
    found = [(document, node, arm)]
    branch_tags = _discriminated_branches(node)
    for keyword in ("anyOf", "oneOf", "allOf"):
        for branch in node.get(keyword, []):
            values = branch_tags.get(branch.get("$ref", ""))
            child = (
                arm | {(f"{path}.{node['discriminator']['propertyName']}".lstrip("."), values)}
                if values
                else arm
            )
            found.extend(
                _variants(document, branch, base, path=path, arm=child, _depth=_depth + 1)
            )
    # `else` stays unconditional. Its true constraint is the complement of the `if`, which a
    # set of admitted values cannot express, and inventing one would be worse than the honest
    # under-constraint: an `else` field lands in every arm, so a comparison can produce a
    # false pass there but never a false failure. Considered, not overlooked.
    condition = node.get("if")
    guard = _condition_values(condition) if isinstance(condition, dict) else None
    for keyword in ("then", "else"):
        branch = node.get(keyword)
        if not isinstance(branch, dict):
            continue
        child = arm
        if guard is not None and keyword == "then":
            name, guard_values = guard
            child = arm | {(f"{path}.{name}".lstrip("."), guard_values)}
        found.extend(
            _variants(document, branch, base, path=path, arm=child, _depth=_depth + 1)
        )
    return found


def _arms(document: dict[str, Any], node: dict[str, Any], base: pathlib.Path) -> frozenset[Arm]:
    """Every **complete, single-valued** arm this document declares.

    A variant's own tag may name several values at once — the shared `GbmSpec` branch is
    tagged `{xgboost, lightgbm}` — so the tags are not themselves the arms. Splitting them
    to one value each gives the coordinate system both sides are expanded onto, and it is
    the same set however each side spells it. `model-spec` is the worked example: the
    generated side declares four `discriminator.mapping` entries, the authored side three
    `if`s (`glm`, `{xgboost, lightgbm}`, `ebm`). Different branch counts, one arm set — which
    is the whole reason arms are the coordinate system and branches are not.

    A document with no union yields `{frozenset()}`: one unconditional arm, which is what
    keeps the union-free majority of `COMPARED_SLUGS` comparing exactly as before.

    The cartesian product across independent discriminators is deliberate and worth
    watching: two unions of four values each give sixteen arms. Three unions at Phase 1b's
    sizes is fine; if a fourth appears and the suite slows, the fix is to key on the
    constraint set rather than expand, not to drop arm attribution.
    """
    return _complete_arms(arm for _, _, arm in _variants(document, node, base))


def _complete_arms(tags: Iterable[Arm]) -> frozenset[Arm]:
    """Split a collection of discriminator tags into the complete single-valued arms.

    Factored out of `_arms` so that a caller holding tags rather than a document can build
    the same coordinate system. `_type_map`'s consumers need exactly that: `_arms` reads a
    document *root*, and it is the root that says nothing about the union nested under
    `model.spec` — measured 2026-08-24, `model.schema.json` has no root union at all
    (`_arms` returns the single unconditional arm) while its walked generated map carries
    nine distinct constraint sets, eight of them conditional, across `spec.model_type`,
    `fit_result.model_type` and `fit_result.bins.[].kind`.
    """
    by_property: dict[str, set[str]] = {}
    for arm in tags:
        for name, values in arm:
            by_property.setdefault(name, set()).update(values)
    if not by_property:
        return frozenset({frozenset()})
    combinations: list[Arm] = [frozenset()]
    for name in sorted(by_property):
        combinations = [
            existing | {(name, frozenset({value}))}
            for existing in combinations
            for value in sorted(by_property[name])
        ]
    return frozenset(combinations)


#: Slugs whose nullability is compared as well as their types (`keep_null` below).
#:
#: Scoped rather than universal **because the reconciliation is scoped, not because the
#: rest are believed to agree.** The measurement on 2026-08-22 found 43 nullability
#: divergences across the twelve compared slugs; the 20 in these six were fixed with this
#: change, and the remainder belongs to their owners. Re-measured after the fix, with the
#: `if`/`then` flattening in place, **24 remain** — one more than the original count, because
#: `custom-objective.template` sits inside a conditional branch nothing used to read:
#:
#: * `audit-event` — `actor.display`
#: * `banding` — `band_stats.[].frequency`, `.mean_burning_cost`, `.mean_severity`,
#:   `derived_on_dataset_version_id`
#: * `custom-objective` — `applicability.y_domain.max_inclusive`, `.min_inclusive`,
#:   `template`
#: * `grouping` — `derived_on_dataset_version_id`, `evidence.chi2_p_value`,
#:   `evidence.deviance_after`, `.deviance_before`, `rationale`
#: * `job` — `error.trace_id`, `resource_budget.memory_gb`, `.wall_clock_s`, `result.ref`,
#:   `trace_id`
#: * `profile` — `columns.[].top_levels.[].exposure_years`, `one_ways.[].banding`†,
#:   `one_ways.[].rows.[].frequency`, `.level`†, `.mean_burning_cost`, `.mean_severity`
#:
#: † runs *contract*-nullable — the contract admits a `null` the model refuses, which is the
#: direction a client can actually be broken by. Removing a slug from this set is how the
#: check would go quiet, so it is written out and `test_every_model_owned_slug_compares_
#: nullability` holds it to the six.
NULLABILITY_COMPARED_SLUGS: Final[frozenset[str]] = frozenset(
    {
        "model",
        "model-spec",
        "diagnostics",
        "transparency-artifact",
        "objective-certificate",
        "peril-structure",
    }
)


def _scalar_types(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    *,
    keep_null: bool = False,
) -> set[str]:
    """The JSON types this node admits — including `null` where `keep_null` is set.

    **Corrected 2026-08-22 (W5).** This function dropped `null` unconditionally, and said
    why: *"the generated contracts mark every `X | None` nullable and the authored ones mark
    almost none, so comparing nullability would report a divergence on nearly every optional
    field — a uniform difference of idiom, not the integer-for-a-float this test exists to
    find."* Both halves of that were measured and are false.

    * **The authored suite is not silent on nullability.** 70 of its 417 dotted paths across
      the twelve compared slugs are marked nullable — 17 %, not "almost none". `model`
      alone spells `{"type": ["string", "null"]}` eleven times.
    * **It is not uniform.** 40 of the 43 hidden divergences run model-nullable, and **3 run
      the other way** — `model.fit_result.iterations`, `profile.one_ways.[].banding`,
      `profile.one_ways.[].rows.[].level`. A difference of idiom has no exceptions; this has
      three, and they are the dangerous direction: the contract promises a `null` the
      platform refuses.

    And the conclusion did not hold either. `model.fit_result.coefficients.[].relativity` is
    `float | None` in the code and `{"type": "number"}` in the contract — and `02` §4.8's
    dated amendment records that nullability as the **fix** to a real defect: *"Reporting
    `exp(β)` as 1.0 for a `logit` model said 'no effect' for a factor spanning eighteen
    log-odds."* The contract still published the pre-fix shape, and this line is the reason
    nothing said so. Not a difference of idiom — a resolved bug, re-published.

    The docstring's own closing sentence named the right remedy — *"as its own change
    against the whole authored suite"* — and `NULLABILITY_COMPARED_SLUGS` is that change,
    landed for the six `02`-owned slugs and scoped in the open for the rest.

    `const` is read alongside `enum`, and for the same reason the enum handling exists: a
    hand-authored `{"const": "derived_from_factors"}` carries no `"type"`, so a walker
    reading only `type` and `enum` called that branch typeless and reported the field as
    `object` against a model admitting `object | string`.
    """
    admitted: set[str] = set()
    for owner, variant, _arm in _variants(document, node, base):
        declared = variant.get("type")
        if isinstance(declared, str):
            admitted.add(declared)
        elif isinstance(declared, list):
            admitted.update(declared)
        members = list(variant.get("enum", ()))
        if "const" in variant:
            members.append(variant["const"])
        for member in members:
            if member is None:
                admitted.add("null")
                continue
            named = _JSON_TYPE_OF.get(type(member))
            if named is not None:
                admitted.add(named)
        del owner
    return admitted if keep_null else admitted - {"null"}


def _ordered(arm: Arm) -> list[tuple[str, list[str]]]:
    """A total order over arms, for deterministic iteration.

    Sorting arms directly would compare `frozenset`s, and `<` on a set is the *subset*
    relation — a partial order. `sorted` accepts it without complaint and produces an order
    that depends on input sequence, which is how a walker starts returning different output
    for the same document.
    """
    return sorted((name, sorted(values)) for name, values in arm)


def _type_map(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    path: str = "",
    *,
    keep_null: bool = False,
    arm: Arm = frozenset(),
) -> dict[tuple[Arm, str], frozenset[str]]:
    """Flatten a schema to `(arm, dotted.path) -> admitted types`, descending into arrays.

    Both array spellings are followed. A variable-length array declares `items`; a
    **fixed-length tuple declares `prefixItems`**, one entry per position, and Pydantic
    emits `tuple[float, float]` that way. Reading only `items` makes this walker silently
    blind to every tuple field — which is exactly what it was, until `severity_ci` failed
    to fail. Element positions collapse onto one `.[]` path: a contract that types position
    0 differently from position 1 is a separate defect, and a comparison that reported it
    as a type mismatch would be describing the wrong problem.

    **A property declared by more than one variant is unioned, not overwritten (2026-08-22,
    W5).** This read `properties.update(...)`, so the *last* variant to name a field
    replaced every earlier definition of it wholesale. A conditional refinement is exactly
    that shape — `peril-structure`'s `{"if": large_loss.kind == "capped", "then":
    {"properties": {"large_loss": {"required": [...]}}}}` names `large_loss` again only to
    add two required keys — so following `then` at all silently deleted the block's real
    definition and took the walker from 36 paths to 28. Collecting the nodes per name and
    unioning their subtrees is what makes the extra reach an addition rather than a trade.

    **Keyed by `(arm, path)` since arm attribution (W32-1b).** That union stays and is still
    load-bearing, but it now unions *within* an arm rather than across arms. Merging across
    them was the defect this slice fixes: moving `family` from the glm arm to the gbm arm in
    the authored `model-spec` left this map equal dict-for-dict — 64 paths before and after,
    and no disagreement against the generated side either way — so the guard reported a
    contract it had not checked. It also meant `spec.monotone_constraints` carried
    `{null, object, string}`, the merge of `GbmSpec`'s `string` and `EbmSpec`'s
    `object | null`, a shape no single arm admits.

    `arm` is what the recursion carries down, so a nested variant's tag composes with its
    parent's, and `path` is handed to `_variants` so a nested discriminator is named by its
    full dotted path instead of colliding with a same-named one higher up.
    """
    found: dict[tuple[Arm, str], frozenset[str]] = {}
    properties: dict[tuple[Arm, str], list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    elements: dict[Arm, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    for owner, variant, found_in in _variants(document, node, base, path=path, arm=arm):
        for name, child in variant.get("properties", {}).items():
            properties.setdefault((found_in, name), []).append((owner, child))
        if "items" in variant:
            elements.setdefault(found_in, []).append((owner, variant["items"]))
        for entry in variant.get("prefixItems", ()):
            elements.setdefault(found_in, []).append((owner, entry))

    if properties:
        for found_in, name in sorted(properties, key=lambda key: (key[1], _ordered(key[0]))):
            for owner, child in properties[(found_in, name)]:
                subtree = _type_map(
                    owner,
                    child,
                    base,
                    f"{path}.{name}".lstrip("."),
                    keep_null=keep_null,
                    arm=found_in,
                )
                for key, types in subtree.items():
                    found[key] = found.get(key, frozenset()) | types
        return found
    if elements:
        for found_in in sorted(elements, key=_ordered):
            for owner, child in elements[found_in]:
                subtree = _type_map(
                    owner,
                    child,
                    base,
                    f"{path}.[]".lstrip("."),
                    keep_null=keep_null,
                    arm=found_in,
                )
                for key, types in subtree.items():
                    found[key] = found.get(key, frozenset()) | types
        return found

    types = _scalar_types(document, node, base, keep_null=keep_null)
    if types:
        found[(arm, path)] = frozenset(types)
    return found


#: Type disagreements escalated to the maintainer instead of fixed here. Keyed slug → paths.
#: An entry is a live question, never a permission, and it is spelled out rather than
#: curated: `test_the_escalated_type_disagreements_are_still_unresolved` deletes the excuse
#: the moment it stops earning its place. This is the shape the pin for `diagnostics`'
#: `aliasing` had before `OQ-MODEL-15` was decided and it was removed rather than relaxed.
#:
#: `OQ-DATA-12` (opened 2026-08-24, W32-11). `validation-report`'s offending sample is an
#: array of `string` on the model and of `object` in the contract, found the day this slug
#: first gained a generated side. **Neither side is obviously right, which is why this is a
#: question and not a fix.** The model's string is what `_sample` in
#: `pricing_core.data.validate` actually emits — composite key values pipe-joined with no
#: escaping, `None` rendered as `""` and so indistinguishable from an empty string, column
#: names dropped — an encoding no specification defines. The contract's `{"type": "object"}`
#: is bare: it names no properties, so it constrains nothing a validator could check. `01`'s
#: glossary and FR-DATA-20 both say "primary keys of rows" without choosing an encoding, and
#: §4.6's only example prints `"offending_sample": []`, which is evidence for neither.
#: Deciding it means changing `pricing-core`'s validation engine, 13 assertions across three
#: test modules — `test_validate.py`, `test_catalogue.py` and `test_api_datasets.py`, measured
#: 2026-08-24 — the published contract, the generated frontend type and §4.6's example: a
#: data-model change across the suite rather than a
#: contract fix, and out of scope for a slice about certificate floors and two generated
#: sides. So it is recorded with an owner and this comparison stays silent on that one path,
#: on the `ENVELOPE_GAP_IS_RECORDED_NOT_FIXED` precedent above.
UNRESOLVED_TYPE_DISAGREEMENTS: Final[dict[str, frozenset[str]]] = {
    "validation-report": frozenset({"results.[].offending_sample.[]"}),
}
def _admits(constraints: Arm, arm: Arm) -> bool:
    """Does a complete `arm` satisfy every constraint in `constraints`?

    A constraint names the values that reach a node; the arm names one value per
    discriminator. The arm satisfies a constraint when its value is among them — and a
    discriminator the arm does not mention cannot satisfy a constraint on it.

    Written as an explicit predicate rather than a `constraints <= arm` subset test,
    deliberately: the subset relation between two constraint sets is the kind of expression
    that reads as correct while being backwards, and it would be backwards here.
    """
    chosen = dict(arm)
    return all(name in chosen and chosen[name] <= values for name, values in constraints)


def _expand(
    by_arm: dict[tuple[Arm, str], frozenset[str]], arms: frozenset[Arm]
) -> dict[tuple[Arm, str], frozenset[str]]:
    """Re-key each entry onto every complete arm its constraints admit.

    The two sides declare the same field in different places: the authored `model-spec` is
    flat-plus-`if`/`then` by design (its `$comment` says so), so `model_family_slug` is
    unconditional, while the generated side declares it inside each arm's `$ref`ed
    subschema. Comparing raw keys would call every shared field drift. Expanding both onto
    the complete arm set puts them on one coordinate system, after which equality means
    what it says.

    An entry constrained by a discriminator no complete arm mentions is **dropped**, not
    spread over all of them. That happens only for a union `arms` was not derived over, and
    dropping is the honest outcome: spreading would restore exactly the cross-arm merge
    this keying exists to stop. It is also why the caller passes an arm set derived from
    the same documents it is comparing rather than a hand-written one.
    """
    expanded: dict[tuple[Arm, str], frozenset[str]] = {}
    for (constraints, path), value in by_arm.items():
        for arm in arms:
            if _admits(constraints, arm):
                key = (arm, path)
                expanded[key] = expanded.get(key, frozenset()) | value
    return expanded


def _paths(by_arm: dict[tuple[Arm, str], frozenset[str]]) -> dict[str, frozenset[str]]:
    """The arm-flattened view: exactly what `_type_map` returned before arm attribution.

    The reach tests ask "does the walker get to this dotted path at all", which is a
    question about coverage and not about arms. Flattening here keeps that question
    answerable in one line rather than re-keying `REACHED_NESTED_PATHS`'s literals, which
    would make a coverage assertion depend on a union's shape.
    """
    flat: dict[str, frozenset[str]] = {}
    for (_, path), types in by_arm.items():
        flat[path] = flat.get(path, frozenset()) | types
    return flat


def _arm_name(arm: Arm) -> str:
    """`model_type=glm:` — the arm a disagreement was found in, for a failure message.

    A bare dict diff over two hundred keys is not actionable; the arm is the first thing a
    reader needs, because a type mismatch in one arm and the same mismatch in all of them
    are different defects.
    """
    if not arm:
        return "<every arm>"
    return ",".join(
        f"{name}={'|'.join(sorted(values))}" for name, values in sorted(arm)
    ) + ":"


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

    **A pin is live again as of 2026-08-24 (W32-11):** `validation-report`'s
    `results.[].offending_sample.[]`, escalated as `OQ-DATA-12`. The refusal above is of a
    *curated* exemption list — one that accumulates entries nobody can date or justify — not
    of a single path held open against a written question with an owner, which is what
    `diagnostics` was. `UNRESOLVED_TYPE_DISAGREEMENTS` carries the reasoning and
    `test_the_escalated_type_disagreements_are_still_unresolved` is what stops it outliving
    the question, on the same terms `aliasing` was held and then released.
    **Compared arm by arm since 2026-08-24 (W32-1b).** The two sides put the same field in
    different places — the authored `model-spec` declares `model_family_slug`
    unconditionally while the generated side declares it inside each arm — so both maps are
    expanded onto one complete arm set before the intersection, and only then does equality
    mean what it says.

    That arm set is built from the constraints **both walked maps** carry, not from
    `_arms` over a document root, and the difference is not cosmetic. `_arms` reads
    composition at the root only, and `model.schema.json` has no root union at all: its
    walked map carries nine constraint sets across `spec.model_type`,
    `fit_result.model_type` and `fit_result.bins.[].kind`, none of which a root reading
    sees. Measured 2026-08-24 — expanding onto the root arm set took this slug from 125
    compared paths to 11 while still passing, which is the silent-guard failure the reach
    controls below exist to catch. Built from the maps, the count is unchanged at 556
    across the thirteen slugs.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    keep_null = slug in NULLABILITY_COMPARED_SLUGS
    produced = _type_map(generated, generated, GENERATED, keep_null=keep_null)
    declared = _type_map(authored, authored, AUTHORED, keep_null=keep_null)

    arms = _complete_arms(constraints for constraints, _ in set(produced) | set(declared))
    produced = _expand(produced, arms)
    declared = _expand(declared, arms)

    # The pin is matched on the bare path. `UNRESOLVED_TYPE_DISAGREEMENTS` predates arm
    # attribution and names a path, not an arm, so the arm is stripped before the test —
    # the same way the constraint carve-out below is matched on `(path, keyword)`. A pin
    # naming an arm would stop matching the day its schema grew one.
    unresolved = UNRESOLVED_TYPE_DISAGREEMENTS.get(slug, frozenset())
    compared = {key for key in set(produced) & set(declared) if key[1] not in unresolved}
    disagreed = {
        key: (sorted(produced[key]), sorted(declared[key]))
        for key in sorted(compared, key=lambda k: (k[1], _arm_name(k[0])))
        if produced[key] != declared[key]
    }
    assert not disagreed, (
        "the model and the contract disagree on the type of "
        + ", ".join(
            f"{_arm_name(arm)} {path} (model {g}, contract {a})"
            for (arm, path), (g, a) in disagreed.items()
        )
    )


@pytest.mark.req("FR-PLAT-48")
@pytest.mark.parametrize("slug", sorted(UNRESOLVED_TYPE_DISAGREEMENTS))
def test_the_escalated_type_disagreements_are_still_unresolved(slug: str) -> None:
    """The pin above must not outlive the question it was taken for.

    `CLAUDE.md` §12's rule for a curated list: whatever notices it went stale ships with it.
    A path excused while `OQ-DATA-12` is open is a hole in the type comparison the moment the
    question is answered, and nothing else in this file would say so — the comparison just
    keeps skipping a path that now agrees.

    **Two ways an entry stops earning its place, and this checks both.** The obvious one is
    that the sides now agree. The other is that the path stopped being compared at all —
    renamed, restructured, or dropped from one side — after which the pin is skipping
    something that no longer exists and would go on doing so silently. Its sibling
    `test_the_escalated_constraint_disagreements_are_still_unresolved` tests only the first:
    it reads both sides through `.get(...)`, so a keyword present on one side alone compares
    a real value against `None`, which is unequal, which reads as *still disagreeing*. That
    is the failure mode this pair is supposed to prevent, so it is not repeated here — the
    membership test comes before the value test, and absence is reported as absence.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    keep_null = slug in NULLABILITY_COMPARED_SLUGS
    # Read through `_paths`: the pin names a dotted path, not an arm, and this asks whether
    # that path is still compared at all — a coverage question, not an arm question. Against
    # the arm-keyed map every bare path is absent from both sides, so the membership test
    # would report every live pin as stale, which is the reverse of what it is for.
    produced = _paths(_type_map(generated, generated, GENERATED, keep_null=keep_null))
    declared = _paths(_type_map(authored, authored, AUTHORED, keep_null=keep_null))

    stale: list[str] = []
    for path in sorted(UNRESOLVED_TYPE_DISAGREEMENTS[slug]):
        if path not in produced or path not in declared:
            sides = "model" if path in produced else "contract" if path in declared else "neither"
            stale.append(f"{path} (no longer compared on both sides; present on {sides})")
        elif produced[path] == declared[path]:
            stale.append(f"{path} (now agrees: {sorted(produced[path])})")

    assert not stale, (
        f"{slug} no longer needs its type pin at "
        + ", ".join(stale)
        + " — delete the entry from UNRESOLVED_TYPE_DISAGREEMENTS rather than leaving the "
        "comparison blind there, and close OQ-DATA-12 if that is what settled it"
    )


_ROOT_PATH: Final = "<root>"


def _required_at(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    *,
    _depth: int = 0,
) -> frozenset[str]:
    """The keys required **at this node**, respecting what each combinator means.

    `_variants` deliberately flattens every combinator into one list, which is right for
    asking "what fields exist anywhere in this shape?" and wrong for asking "what must be
    present?". So this does not use it. `allOf` is conjunction — every branch's obligations
    hold, so union them. `oneOf`/`anyOf` is disjunction — a key is required only if
    **every** arm demands it, so intersect. `then`/`else` are conditional on an `if` this
    suite does not evaluate, and contribute nothing unconditionally.

    Getting this wrong **invents** requirements rather than missing them, which is the more
    expensive failure. `model.fit_result.bins.[]` is
    `oneOf: [EbmNumericBins, EbmCategoricalBins]` with a discriminator: the first requires
    `cuts`, the second requires `levels`, and no single bin requires both. A union reports
    both as model-required, and a contract "corrected" to match would then refuse every
    valid categorical bin — a guard that manufactures the defect it reports.
    """
    if _depth > _MAX_COMPOSITION_DEPTH:
        raise AssertionError(
            f"more than {_MAX_COMPOSITION_DEPTH} composition levels — the document nests "
            "without bottoming out"
        )
    node, document = _deref(document, node, base)
    here = set(node.get("required", ()))
    for branch in node.get("allOf", []):
        here |= _required_at(document, branch, base, _depth=_depth + 1)
    for keyword in ("oneOf", "anyOf"):
        arms = [b for b in node.get(keyword, []) if b.get("type") != "null"]
        if not arms:
            continue
        common = _required_at(document, arms[0], base, _depth=_depth + 1)
        for arm in arms[1:]:
            common &= _required_at(document, arm, base, _depth=_depth + 1)
        here |= common
    return frozenset(here)


def _required_map(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    path: str = "",
) -> dict[str, frozenset[str]]:
    """Flatten a schema to `dotted.path -> the keys required at that path`.

    Descends the way `_type_map` does — `_variants` to find children, the same `.[]`
    collapse for arrays — so a path here is a path there and the two maps can be read
    against each other. What is required *at* each node comes from `_required_at` instead,
    because **finding children and deciding obligations are different questions** and only
    the first one wants a flattened view.
    """
    found: dict[str, frozenset[str]] = {}
    required = _required_at(document, node, base)
    if required:
        found[path or _ROOT_PATH] = required

    for owner, variant, _arm in _variants(document, node, base):
        for name, child in variant.get("properties", {}).items():
            subtree = _required_map(owner, child, base, f"{path}.{name}".lstrip("."))
            for key, keys in subtree.items():
                found[key] = found.get(key, frozenset()) | keys
        elements = list(variant.get("prefixItems", ()))
        if "items" in variant:
            elements.append(variant["items"])
        for child in elements:
            subtree = _required_map(owner, child, base, f"{path}.[]".lstrip("."))
            for key, keys in subtree.items():
                found[key] = found.get(key, frozenset()) | keys
    return found


@pytest.mark.req("FR-PLAT-48")
@pytest.mark.req("FR-OVR-6")
@pytest.mark.parametrize("slug", COMPARED_SLUGS)
def test_the_contract_never_marks_optional_what_the_model_requires(slug: str) -> None:
    """One direction, deliberately, and the direction is the whole design.

    The two sides answer different questions. Pydantic's `required` lists the fields with
    no default — a fact about *construction*. A hand-authored contract's `required` lists
    what a reader may rely on. A field carrying a default is still always serialised, so
    "the contract requires more than the model" is safe, and on 2026-08-22 it accounted for
    fourteen of the eighteen differences across the twelve compared slugs. Asserting
    equality would land red on seven schemas for a reason that is mostly not a defect, and
    a guard that lands like that is one somebody switches off.

    The other direction is a live bug. A field the model demands and the contract calls
    optional is a request a client will build from the published contract, send, and have
    refused — and the refusal names a field the contract said was not needed.

    The two this found on the day it was written are `model.fit_result.terms.[]`'s
    `bin_weights` and `standard_deviations`, which `EbmTerm` requires and the contract
    marks optional.

    It found them only because `_required_at` respects combinators. The naive union also
    reported `bins.[].cuts` and `bins.[].levels`, which are **not** defects: `bins.[]` is a
    discriminated `oneOf` and no single arm requires both.

    `dataset_id` on `banding` and `grouping` is not among them because it is already a
    recorded divergence with a named owner (`MODEL_ONLY_UNRECONCILED`) — the same field,
    the same finding, and re-reporting it here would be a second account of one fact.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    produced = _required_map(generated, generated, GENERATED)
    declared = _required_map(authored, authored, AUTHORED)

    exempt = MODEL_ONLY_UNRECONCILED.get(slug, frozenset())
    if _composes_the_envelope(authored):
        exempt |= ENVELOPE_FIELDS

    optional_but_demanded = {
        path: sorted(produced[path] - declared.get(path, frozenset()) - exempt)
        for path in sorted(set(produced) & set(declared))
        if produced[path] - declared.get(path, frozenset()) - exempt
    }
    assert not optional_but_demanded, (
        "the model requires fields the contract marks optional, so a client following the "
        "published contract builds a request the platform refuses: "
        + ", ".join(f"{p} ({', '.join(n)})" for p, n in optional_but_demanded.items())
    )


def _closure_map(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    path: str = "",
) -> dict[str, frozenset[str]]:
    """Flatten a schema to `dotted.path -> what `additionalProperties` says there`.

    Both spellings land in one vocabulary so they cannot be silently compared against each
    other: the boolean form becomes `{"CLOSED"}` or `{"OPEN"}`, the schema form becomes the
    JSON types its value schema admits. A path where one side says `CLOSED` and the other
    says `number` is then a reported disagreement rather than an accidental match.

    Only nodes that *state* `additionalProperties` are recorded. Absence is not `OPEN`:
    JSON Schema's default is open, but a hand-authored contract that says nothing is silent
    rather than deliberate, and reporting every silence would bury the real disagreements —
    which measured **one** across the whole compared suite.
    """
    found: dict[str, frozenset[str]] = {}
    for owner, variant, _arm in _variants(document, node, base):
        extra = variant.get("additionalProperties")
        if extra is not None:
            key = path or _ROOT_PATH
            if isinstance(extra, bool):
                says = frozenset({"OPEN" if extra else "CLOSED"})
            else:
                says = frozenset(_scalar_types(owner, extra, base)) or frozenset({"ANY"})
            found[key] = found.get(key, frozenset()) | says
        for name, child in variant.get("properties", {}).items():
            for key, says in _closure_map(
                owner, child, base, f"{path}.{name}".lstrip(".")
            ).items():
                found[key] = found.get(key, frozenset()) | says
        elements = list(variant.get("prefixItems", ()))
        if "items" in variant:
            elements.append(variant["items"])
        for child in elements:
            for key, says in _closure_map(
                owner, child, base, f"{path}.[]".lstrip(".")
            ).items():
                found[key] = found.get(key, frozenset()) | says
    return found


@pytest.mark.req("FR-PLAT-48")
@pytest.mark.parametrize("slug", COMPARED_SLUGS)
def test_generated_and_authored_agree_on_what_an_open_map_admits(slug: str) -> None:
    """An open map's value type is published, and a client validates against it.

    Seventeen paths declare `additionalProperties` on both sides and nothing has ever read
    one. The measured disagreement is `custom-objective.params`: the model admits
    `integer | number` and the contract admits `number` alone, so an objective parameterised
    with a whole number — a period, a count, a cap in whole units — is a document the
    published contract rejects and the platform accepts. That is the direction that wastes
    an author's afternoon, because the thing refusing them is their own validator.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    produced = _closure_map(generated, generated, GENERATED)
    declared = _closure_map(authored, authored, AUTHORED)

    disagreed = {
        path: (sorted(produced[path]), sorted(declared[path]))
        for path in sorted(set(produced) & set(declared))
        if produced[path] != declared[path]
    }
    assert not disagreed, (
        "the model and the contract disagree on what extra properties are admitted at "
        + ", ".join(f"{p} (model {g}, contract {a})" for p, (g, a) in disagreed.items())
    )


#: The constraint keywords compared. Written out rather than "every keyword that is not a
#: structural one", because the structural set grows with the spec and a negative list would
#: quietly start comparing things this guard has no opinion about.
_COMPARED_CONSTRAINTS: Final[frozenset[str]] = frozenset(
    {
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
        "pattern",
        "minItems",
        "maxItems",
    }
)


def _constraint_map(
    document: dict[str, Any],
    node: dict[str, Any],
    base: pathlib.Path,
    path: str = "",
    *,
    _depth: int = 0,
) -> dict[str, dict[str, Any]]:
    """Flatten a schema to `dotted.path -> the constraint keywords declared there`.

    Only keywords in `_COMPARED_CONSTRAINTS`, and only where a side declares one: a path
    constrained on neither side is not a disagreement, and a path constrained on one side
    only is reported by the comparison rather than by this walker.
    """
    if _depth > _MAX_COMPOSITION_DEPTH:
        raise AssertionError(
            f"more than {_MAX_COMPOSITION_DEPTH} composition levels — the document nests "
            "without bottoming out"
        )
    found: dict[str, dict[str, Any]] = {}
    properties: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    elements: list[tuple[dict[str, Any], dict[str, Any]]] = []

    for owner, variant, _arm in _variants(document, node, base):
        declared = {k: v for k, v in variant.items() if k in _COMPARED_CONSTRAINTS}
        if declared:
            found.setdefault(path or _ROOT_PATH, {}).update(declared)
        for name, child in variant.get("properties", {}).items():
            properties.setdefault(name, []).append((owner, child))
        if "items" in variant:
            elements.append((owner, variant["items"]))
        elements.extend((owner, entry) for entry in variant.get("prefixItems", ()))

    for name in sorted(properties):
        for owner, child in properties[name]:
            for key, declared in _constraint_map(
                owner, child, base, f"{path}.{name}".lstrip("."), _depth=_depth + 1
            ).items():
                found.setdefault(key, {}).update(declared)
    for owner, child in elements:
        for key, declared in _constraint_map(
            owner, child, base, f"{path}.[]".lstrip("."), _depth=_depth + 1
        ).items():
            found.setdefault(key, {}).update(declared)
    return found


#: Constraint disagreements this slice found and deliberately did **not** resolve, keyed by
#: slug and holding `(dotted path, keyword)` pairs. Scoped out in the open rather than
#: exempted silently, and `test_the_escalated_constraint_disagreements_are_still_unresolved`
#: is what notices when a decision lands and this entry should go.
#:
#: **Empty since 2026-08-24 (W32-11).** Its one entry —
#: `objective-certificate` / `result.checks` / `minItems`, model 1 against contract 8 — was
#: OQ-MODEL-30, decided as FR-MODEL-126: the shared `CertificateResult` stays unbounded and
#: each certificate type enforces its own battery, so the carve-out died with the question,
#: in the same commit. The dict is kept rather than deleted: it is the mechanism for the next
#: escalation, and its companion test collects zero cases while it is empty.
#:
#: **Corrected 2026-08-24 (W32-11): the pair stopped being _comparable_, not disagreeing.**
#: Unbinding the shared type removed `minItems` from the generated side entirely, and a
#: keyword present on one side alone is outside what this comparison speaks about. The
#: distinction is not pedantic — the slice plan predicted that leaving the entry in place
#: would turn the companion below red, and it did not. That companion reads both sides
#: through `.get(...)`, so it compared the model's absent `None` against the contract's `9`,
#: found them unequal, and reported the pair as still disagreeing. An entry could therefore
#: have outlived its question here indefinitely without anything saying so. The defect is
#: left standing rather than fixed mid-slice, and `UNRESOLVED_TYPE_DISAGREEMENTS`' companion
#: is written the other way round — membership before value — so the newer pin cannot
#: inherit it.
UNRESOLVED_CONSTRAINT_DISAGREEMENTS: Final[dict[str, frozenset[tuple[str, str]]]] = {}


@pytest.mark.req("FR-PLAT-48")
@pytest.mark.parametrize("slug", COMPARED_SLUGS)
def test_generated_and_authored_agree_on_scalar_constraints(slug: str) -> None:
    """A bound is part of the published contract, and a wrong one is refused input.

    The type comparison above answers "may this be a string?" and stops. It says nothing
    about a `minLength: 1` the model enforces and the contract omits — under which a client
    posts the empty string the contract permitted and meets a 422 naming a rule it was
    never told. Only keywords declared on **both** sides are compared, for the same reason
    the type comparison intersects paths: a constraint on one side alone is a difference of
    intent, and `test_an_artifact_shape_carries_exactly_what_its_contract_declares` is
    where intent is arbitrated.

    A pair may be scoped out through `UNRESOLVED_CONSTRAINT_DISAGREEMENTS` when the
    disagreement is a question for the maintainer rather than a fix. **That dict is empty**
    — its one entry was OQ-MODEL-30, settled 2026-08-24 — so nothing is skipped here today,
    and `test_the_escalated_constraint_disagreements_are_still_unresolved` is what notices
    if a future entry outlives its question.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    produced = _constraint_map(generated, generated, GENERATED)
    declared = _constraint_map(authored, authored, AUTHORED)
    unresolved = UNRESOLVED_CONSTRAINT_DISAGREEMENTS.get(slug, frozenset())

    disagreed: dict[str, dict[str, tuple[Any, Any]]] = {}
    for path in sorted(set(produced) & set(declared)):
        for keyword in sorted(set(produced[path]) & set(declared[path])):
            if (path, keyword) in unresolved:
                continue
            if produced[path][keyword] != declared[path][keyword]:
                disagreed.setdefault(path, {})[keyword] = (
                    produced[path][keyword],
                    declared[path][keyword],
                )
    assert not disagreed, (
        "the model and the contract disagree on a bound at "
        + "; ".join(
            f"{p}: " + ", ".join(f"{k} model={g} contract={a}" for k, (g, a) in d.items())
            for p, d in disagreed.items()
        )
    )


@pytest.mark.req("FR-PLAT-48")
@pytest.mark.parametrize("slug", sorted(UNRESOLVED_CONSTRAINT_DISAGREEMENTS))
def test_the_escalated_constraint_disagreements_are_still_unresolved(slug: str) -> None:
    """The carve-out above must not outlive the question it was taken for.

    `CLAUDE.md` §12's rule for a curated list: whatever notices it went stale ships with it.
    An exemption written for a live disagreement is a hole in the guard the moment the
    disagreement is settled, and nothing else in this file would say so — the comparison
    just keeps skipping a pair that now agrees. So this asserts the exemption is still
    earning its place, and goes red with instructions when it stops.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")

    produced = _constraint_map(generated, generated, GENERATED)
    declared = _constraint_map(authored, authored, AUTHORED)

    settled = [
        (path, keyword)
        for path, keyword in sorted(UNRESOLVED_CONSTRAINT_DISAGREEMENTS[slug])
        if produced.get(path, {}).get(keyword) == declared.get(path, {}).get(keyword)
    ]
    assert not settled, (
        f"{slug} no longer disagrees at "
        + ", ".join(f"{p}.{k}" for p, k in settled)
        + " — the question was answered, so delete the entry from "
        "UNRESOLVED_CONSTRAINT_DISAGREEMENTS rather than leaving the guard blind there"
    )


@pytest.mark.req("FR-PLAT-48")
@pytest.mark.parametrize(
    ("walker", "slug", "path"),
    [
        (_required_map, "grouping", "evidence.source_level_stats.[]"),
        (_required_map, "model", "fit_result.bins.[]"),
        (_closure_map, "model-spec", "family_params"),
        (_constraint_map, "grouping", "evidence.source_level_stats.[].claim_count"),
    ],
)
def test_each_new_walker_reaches_a_nested_path_it_is_supposed_to(
    walker: Any, slug: str, path: str
) -> None:
    """The control for the three comparisons above, at the depth where they go quiet.

    A comparison that intersects two maps is green when both maps are empty. Counting what
    a walker produced does not catch a walker that stopped descending — the count shrinks
    with it, so any threshold expressed as a fraction of its own output moves out of the
    way of the defect it exists to catch. So this names one path per walker instead, each
    one nested at least two levels down and each chosen because a plausible refactor of the
    walker would lose it.
    """
    authored = _load(AUTHORED / f"{slug}.schema.json")
    reached = walker(authored, authored, AUTHORED)
    assert path in reached, (
        f"{walker.__name__} no longer reaches {path} in {slug} — the comparison built on "
        "it is now silent about everything beneath that point"
    )


@pytest.mark.req("FR-PLAT-48")
def test_a_generated_union_branch_is_tagged_with_its_discriminator_values() -> None:
    """The generated side spells an arm as a `$ref` and a `discriminator.mapping` entry.

    `xgboost` and `lightgbm` share one `GbmSpec`, so **four discriminator values map onto
    three branches** and a tag must be a set of values rather than one value. That asymmetry
    is the reason this is not a dictionary lookup.
    """
    document = _load(GENERATED / "model-spec.schema.json")
    tags = {arm for _, _, arm in _variants(document, document, GENERATED) if arm}
    values = {v for arm in tags for _, v in arm}
    assert frozenset({"xgboost", "lightgbm"}) in values
    assert frozenset({"glm"}) in values


@pytest.mark.req("FR-PLAT-48")
def test_an_authored_conditional_arm_is_tagged_from_its_sibling_if() -> None:
    """The authored side spells the same arm as `{"if": ..., "then": ...}`.

    `if` is read for the **tag** and never for the types — folding `{"const": "glm"}` into
    `model_type`'s admitted types would invent a field declaration, which is what
    `_variants` has always refused and still refuses.
    """
    document = _load(AUTHORED / "model-spec.schema.json")
    values = {
        v
        for _, _, arm in _variants(document, document, AUTHORED)
        for _, v in arm
    }
    assert frozenset({"glm"}) in values


@pytest.mark.req("FR-PLAT-48")
def test_both_sides_declare_the_same_complete_arms() -> None:
    """The comparison is only meaningful if the two arm sets are the same set.

    If they differ, the drift is in the union's shape itself and every later per-arm
    comparison would be comparing arms that do not correspond — a failure worth its own
    message rather than forty confusing ones.
    """
    generated = _load(GENERATED / "model-spec.schema.json")
    authored = _load(AUTHORED / "model-spec.schema.json")
    assert _arms(generated, generated, GENERATED) == _arms(authored, authored, AUTHORED)


@pytest.mark.req("FR-PLAT-48")
def test_a_document_with_no_union_has_one_unconditional_arm() -> None:
    """Most of the thirteen compared slugs have no union at all.

    They must keep behaving exactly as they did, which per-arm keying achieves by making
    their single arm the empty constraint set rather than by special-casing them.
    """
    document = _load(AUTHORED / "audit-event.schema.json")
    assert _arms(document, document, AUTHORED) == frozenset({frozenset()})


def _move_property_between_arms(
    document: dict[str, Any], name: str, *, source: str, target: str
) -> dict[str, Any]:
    """A deep copy of an authored document with one property moved between two `if` arms.

    Pure on purpose. The mutated document is never written back, so a test that fails
    part-way through cannot leave `docs/contracts/` modified — a guard whose own failure
    mode is corrupting the artifact it guards is worse than no guard.

    The arms are located by their sibling `if`, read through `_condition_values` rather
    than by re-parsing the `const`/`enum` spelling here, so a schema that respells its
    discriminator moves this helper with it instead of silently matching nothing.
    """
    moved = copy.deepcopy(document)
    arms: dict[str, dict[str, Any]] = {}
    for block in moved.get("allOf", []):
        condition = block.get("if")
        guard = _condition_values(condition) if isinstance(condition, dict) else None
        if guard is None:
            continue
        for value in guard[1]:
            arms[value] = block.setdefault("then", {}).setdefault("properties", {})
    missing = {value for value in (source, target) if value not in arms}
    assert not missing, (
        f"no conditional arm for {sorted(missing)} — this document does not have the shape "
        f"the test is built on, and it declares {sorted(arms)}"
    )
    assert name in arms[source], f"{name!r} is not declared by the {source!r} arm"
    arms[target][name] = arms[source].pop(name)
    return moved


@pytest.mark.req("FR-PLAT-48")
def test_a_field_moved_between_arms_is_drift() -> None:
    """**The defect, on the case it was measured on.**

    `family` belongs to the glm arm. Moving it to the gbm arm is drift of the worst kind —
    the field set is unchanged, so a walker that merges the arms into one namespace sees
    nothing at all, and the guard reports a contract it has not checked. Measured on
    2026-08-23: the two `_type_map` outputs were equal dict-for-dict with the property
    moved, and every other test in this module went on passing with the schema in that
    state.
    """
    authored = _load(AUTHORED / "model-spec.schema.json")
    moved = _move_property_between_arms(authored, "family", source="glm", target="xgboost")

    generated = _load(GENERATED / "model-spec.schema.json")
    arms = _arms(generated, generated, GENERATED)
    before = _expand(_type_map(authored, authored, AUTHORED), arms)
    after = _expand(_type_map(moved, moved, AUTHORED), arms)
    assert before != after, (
        "moving a property between arms produced an identical map — the walker is still "
        "merging arms into one namespace"
    )


@pytest.mark.req("FR-PLAT-48")
def test_an_arm_specific_type_is_not_unioned_across_arms() -> None:
    """`monotone_constraints` reports a union no single arm admits.

    Before arm attribution one dotted path carried `{null, object, string}` — the merge of
    **two** arms: `GbmSpec`'s `Literal["derived_from_factors", "none"]`
    (`model_schema/modelling.py:1327`, `string`) and `EbmSpec`'s `dict[str, int] | None`
    (`:1441`, `object` + `null`). `GlmSpec` has no such field. No arm admits all three
    types, so the guard was comparing a shape that does not exist and would have accepted a
    contract declaring any one of them in either arm.

    `GbmFitResult.monotone_constraints` (`:1640`) is **not** part of this union — measured,
    not assumed: it lands at `fit_result.monotone_constraints.[]` in `model.schema.json` and
    reports `{integer}`. Recorded because the three-way reading is the intuitive one and it
    is wrong.

    `keep_null=True` is required, not decoration: `model-spec` is in
    `NULLABILITY_COMPARED_SLUGS`, so the comparison test walks it that way, and without it
    `null` is stripped and this assertion can never fail — it would pass before the fix and
    after it, testing nothing.
    """
    generated = _load(GENERATED / "model-spec.schema.json")
    by_arm = _type_map(generated, generated, GENERATED, keep_null=True)
    for (arm, path), types in by_arm.items():
        if path.endswith("monotone_constraints"):
            assert types != frozenset({"null", "object", "string"}), (
                f"{sorted(arm)} still carries the cross-arm union"
            )


#: Nested fields this slice added to the `02`-owned contracts, named so their removal is
#: noticed. Each must be a path the comparison reaches **on both sides**.
#:
#: `test_an_artifact_shape_carries_exactly_what_its_contract_declares` compares **top-level**
#: field names only, and `test_generated_and_authored_agree_on_scalar_types` compares only
#: paths present on both sides — so a *nested* field deleted from a contract appears in
#: neither: it stops being a shared path and the type comparison simply says less. That is
#: exactly how `gbm.quantile_crossing` (FR-MODEL-78) and `gbm.tree_count` came to be absent
#: from `diagnostics.schema.json` for months with every check green, and it was rediscovered
#: on 2026-08-22 by trying to break the improved guard and finding it did not notice
#: (`CLAUDE.md` §13.4).
#:
#: A general nested-existence comparison would light up every legitimately unshared path in
#: the suite, so this is the same instrument
#: `test_the_type_comparison_reaches_the_one_way_row` uses: name the paths that matter.
REACHED_NESTED_PATHS: Final[dict[str, frozenset[str]]] = {
    "model": frozenset(
        {
            "fit_result.booster_format",
            "fit_result.best_iteration",
            "fit_result.base_margin.kind",
            "fit_result.feature_dtypes",
            "fit_result.categorical_maps",
            "fit_result.dropped_eval_metrics.[].reason",
            "fit_result.coefficients.[].relativity",
            "fit_result.covariance_blob.sha256",
            "fit_result.tweedie.estimated_power",
            "fit_result.intercept",
        }
    ),
    "model-spec": frozenset(
        {"alpha", "select_by", "tweedie.p_grid.[]", "interval_for.alpha", "max_bins",
         "loss_treatment.kind", "approximates_model_id", "offset_acknowledgement"}
    ),
    "diagnostics": frozenset(
        {
            "gbm.quantile_crossing.rows_crossing",
            "gbm.tree_count",
            "gbm.max_depth",
            "gbm.mean_depth",
            "gbm.importances.[].feature",
            "gbm.permutation_importances.[].degradation",
            "gbm.partial_dependence.[].points.[].exposure_share",
            "gbm.monotonicity.[].holds",
            "gbm.eval_curve.[].metric",
            "cross_validation.path.[].alpha",
            "cross_validation.fold_metrics.[].fold",
            "cross_validation.selected_alpha",
            "universal.train.rows",
            "universal.holdout.residual_summary.p99",
        }
    ),
    "transparency-artifact": frozenset(
        {
            "glm_approximation.relativity_table_blob.sha256",
            "glm_approximation.coefficients.[].estimate",
            "glm_approximation.family",
            "shap_summary.dependence_blob.sha256",
            "shap_summary.interactions_available",
        }
    ),
    "peril-structure": frozenset(
        {
            "reconciliation.perils.[].peril",
            "reconciliation.perils.[].modelled_burning_cost_minor",
            "reconciliation.computed_at",
            "perils.[].large_loss.evidence_blob.sha256",
        }
    ),
    #: Added 2026-08-22 (W32-1). `grouping` had no entry, which is why
    #: `evidence.source_level_stats` could be declared in the contract since Phase 0 and
    #: absent from `GroupingEvidence` throughout with every check green: the field-name
    #: comparison reads top-level names only, and the type comparison reads only paths
    #: present on both sides — an undeclared nested field is on neither list.
    "grouping": frozenset(
        {
            "evidence.source_level_stats.[].level",
            "evidence.source_level_stats.[].exposure_years",
            "evidence.source_level_stats.[].claim_count",
            "evidence.target_level_stats.[].level",
            "evidence.target_level_stats.[].exposure_years",
            "evidence.target_level_stats.[].claim_count",
        }
    ),
}


@pytest.mark.req("FR-OVR-6")
@pytest.mark.parametrize("slug", sorted(REACHED_NESTED_PATHS))
def test_the_comparison_reaches_the_nested_fields_this_slice_added(slug: str) -> None:
    """The control for the two comparisons above, at the depth where they go quiet.

    Neither of them fails when a *nested* contract field is deleted — the top-level name set
    does not contain it, and the type comparison only narrows. So these paths are named, and
    they must be present on **both** sides: the contract declares them, and the walker
    still reaches them.
    """
    generated = _load(GENERATED / f"{slug}.schema.json")
    authored = _load(AUTHORED / f"{slug}.schema.json")
    keep_null = slug in NULLABILITY_COMPARED_SLUGS
    compared = set(
        _paths(_type_map(generated, generated, GENERATED, keep_null=keep_null))
    ) & set(_paths(_type_map(authored, authored, AUTHORED, keep_null=keep_null)))

    wanted = REACHED_NESTED_PATHS[slug]
    assert wanted <= compared, (
        f"the comparison no longer reaches {sorted(wanted - compared)} in {slug} — either "
        "the contract stopped declaring them or the walker stopped descending, and both "
        "read as a passing test"
    )


@pytest.mark.req("FR-OVR-6")
def test_every_model_owned_slug_compares_nullability() -> None:
    """The nullability comparison is scoped; this is what stops the scope shrinking.

    `NULLABILITY_COMPARED_SLUGS` is the only thing standing between `keep_null` and a check
    that silently stops running, and a set literal is edited as easily as it is read. The
    six `02`-owned slugs were reconciled on 2026-08-22 and none of them may leave without
    this failing — which is the same bargain `test_every_eligible_schema_is_compared` makes
    for the outer list.

    It does **not** demand the other six join: those 23 divergences belong to `01`, `06` and
    `07`, are enumerated by name beside the set, and widening the scope here would be this
    slice fixing another's contracts.
    """
    owned = {
        "model",
        "model-spec",
        "diagnostics",
        "transparency-artifact",
        "objective-certificate",
        "peril-structure",
    }
    assert owned <= NULLABILITY_COMPARED_SLUGS, (
        "these `02`-owned slugs were reconciled for nullability and have been dropped from "
        f"the comparison: {sorted(owned - NULLABILITY_COMPARED_SLUGS)}"
    )
    assert set(COMPARED_SLUGS) >= NULLABILITY_COMPARED_SLUGS, (
        "a slug is marked for nullability comparison but is not compared at all: "
        f"{sorted(NULLABILITY_COMPARED_SLUGS - set(COMPARED_SLUGS))}"
    )


@pytest.mark.req("FR-OVR-6")
def test_the_envelope_gap_is_still_the_shape_the_carve_out_assumes() -> None:
    """The recorded-not-fixed envelope divergence, held to its recorded shape.

    `ENVELOPE_FIELDS` buys the existence test's silence about `00` §4.3's envelope, and an
    exemption nobody re-reads is how a real divergence acquires tenure. So the exemption
    states what it is covering for, and fails if that stops being true:

    * the envelope contract still declares exactly the fourteen fields being exempted, and
    * no `model_schema` model has quietly started composing `ArtifactEnvelope` — because on
      the day one does, the carve-out is hiding a *narrower* gap than it claims and should
      shrink with it.

    The verdict and the owner for the gap itself are the maintainer's; this only guarantees
    the description stays accurate while it is open.
    """
    envelope = _load(AUTHORED / "common" / "artifact-envelope.schema.json")
    assert set(envelope["properties"]) == set(ENVELOPE_FIELDS)
    assert len(ENVELOPE_FIELDS) == 14, sorted(ENVELOPE_FIELDS)

    import model_schema

    composing = sorted(
        name
        for name in model_schema.__all__
        if isinstance(getattr(model_schema, name, None), type)
        and issubclass(getattr(model_schema, name), model_schema.ArtifactEnvelope)
        and getattr(model_schema, name) is not model_schema.ArtifactEnvelope
    )
    assert composing == [], (
        f"{composing} now compose(s) ArtifactEnvelope. The carve-out above is written for a "
        "suite where nothing does; narrow it to the artifacts still outside."
    )


@pytest.mark.req("FR-MODEL-109")
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
    compared = set(_paths(_type_map(generated, generated, GENERATED))) & set(
        _paths(_type_map(authored, authored, AUTHORED))
    )

    wanted = {f"{row}.mean_severity", f"{row}.mean_burning_cost", f"{row}.severity_ci.[]"}
    assert wanted <= compared, (
        f"the type comparison no longer reaches {sorted(wanted - compared)} in {slug} — "
        "it is passing because it stopped looking, not because the contracts agree"
    )


@pytest.mark.req("FR-MODEL-15")
@pytest.mark.parametrize(
    "block", ["evidence.source_level_stats.[]", "evidence.target_level_stats.[]"]
)
def test_the_grouping_evidence_rows_are_the_shared_one_way_row(block: str) -> None:
    """Both halves of the evidence describe `OneWayRow`, and describe it the same way.

    The authored contract hand-copied a four-field subset of `OneWayRow` into
    `target_level_stats` and gave it a `relativity` the shared model has never had, while
    `source_level_stats` was `{"items": {"type": "object"}}` — untyped, describing nothing.
    Neither was visible: the type comparison reads only paths present on both sides, so a
    field on one side alone is skipped rather than reported, and a wholly untyped item has
    no leaves to compare at all.

    **Compare whole paths, never a path rebuilt from its last segment.** The first version
    of this test collected `path.rsplit(".", 1)[-1]` and reassembled `f"{block}.{name}"`,
    which is only valid where every leaf is one level down. `OneWayRow` carries two
    `tuple[float, float]` fields, and Pydantic emits a tuple as `prefixItems`, so
    `frequency_ci` and `severity_ci` reach this walker as `…frequency_ci.[]`. Their last
    segment is `[]`, and the reassembly then asserted `…source_level_stats.[].[]` — a path
    neither side can ever produce, so the test failed unconditionally and said nothing
    about the contract. `prefixItems` is the same blindness recorded against `_type_map`
    itself; it is worth noticing that knowing the trap did not prevent writing it again.
    """
    generated = _load(GENERATED / "grouping.schema.json")
    authored = _load(AUTHORED / "grouping.schema.json")

    produced = {
        path
        for path in _paths(_type_map(generated, generated, GENERATED))
        if path.startswith(f"{block}.")
    }
    declared = {
        path
        for path in _paths(_type_map(authored, authored, AUTHORED))
        if path.startswith(f"{block}.")
    }

    assert produced, f"the model produces no leaves under {block}"
    assert not produced - declared, (
        f"the contract does not declare: {sorted(produced - declared)}"
    )
    assert not declared - produced, (
        f"the contract declares fields the model lacks: {sorted(declared - produced)}"
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
