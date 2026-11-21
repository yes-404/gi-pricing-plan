"""The read-side `Provenance` shape and its ten read classes (FR-2159, FR-6; #1519, #1868).

Decided on #1506:

* #1519 (b): `Provenance` is a read-side class in `model-schema`, composed by the API on
  every read and **never persisted**;
* #1868 (a): it carries the shape's own identity (`entity_type`, a UUID `entity_id`) and
  `subject_refs`, its governed parents in the `refs` form (`{type}:{slug}@{version}`, ID-3);
* slice 1's accepted text: the object **omits `computed_at`**, because nothing composed on a
  read is an honest source for it;
* the accepted slice-2 approach: a read class per shape, each the persisted class plus a
  `provenance` field, with the persisted classes untouched.

These tests fail until `model_schema.Provenance` and the ten read classes exist. They read
the classes off the package (`model_schema.<name>`) so that each test fails on its own name
rather than the whole module failing to import.
"""

from __future__ import annotations

import datetime
import enum
import typing
from typing import Any
from uuid import UUID

import pydantic
import pytest

import model_schema
from model_schema import ArtifactRef, Profile, new_uuid7
from model_schema.refs import REF_PATTERN

#: The read class each route returns, and the class it extends. Nine extend the persisted
#: artifact; `ValidationReportRead` extends `ValidationReportView`, the report *as presented*
#: (`01` §4.6), because that is what `GET /validation-reports/{report_id}` returns today and
#: the persisted `ValidationReport` carries `overall` and `counts` only as properties.
READ_CLASSES: dict[str, str] = {
    "ValidationReportRead": "ValidationReportView",
    "ProfileRead": "Profile",
    "DiagnosticsRead": "Diagnostics",
    "ModelComparisonRead": "ModelComparison",
    "BacktestRead": "Backtest",
    "RegressionRunRead": "RegressionRun",
    "ObjectiveCertificateRead": "ObjectiveCertificate",
    "DislocationRunRead": "DislocationRun",
    "MetricCertificateRead": "MetricCertificate",
    "TransparencyArtifactRead": "TransparencyArtifact",
}

#: `entity_type` for each of the ten, the snake_case names the audit log already uses for
#: the ones it records (`validation_report:`, `profile:`, `model_comparison:`, `backtest:`).
ENTITY_TYPES: frozenset[str] = frozenset(
    {
        "validation_report",
        "profile",
        "diagnostics",
        "model_comparison",
        "backtest",
        "regression_run",
        "objective_certificate",
        "dislocation_run",
        "metric_certificate",
        "transparency_artifact",
    }
)


def _provenance_class() -> type[pydantic.BaseModel]:
    cls: type[pydantic.BaseModel] = model_schema.Provenance  # type: ignore[attr-defined]
    return cls


def _provenance(**over: Any) -> pydantic.BaseModel:
    base: dict[str, Any] = {
        "entity_type": "profile",
        "entity_id": new_uuid7(),
        "produced_by_job_id": new_uuid7(),
        "subject_refs": ("dataset_version:motor-gb@3",),
    }
    base.update(over)
    return _provenance_class().model_validate(base)


# -- The shape ------------------------------------------------------------------------------


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_provenance_carries_the_identity_the_job_and_the_subject_refs_and_nothing_else() -> None:
    """#1868 (a): the shape's own identity, the producing Job, and the governed parents.

    No `version`: the ten shapes are addressed by UUID and carry no version of their own
    (the version a reader needs is inside each subject ref). No `computed_at`: slice 1's
    accepted text.

    Plus `unnamed_subjects` (#1506's proposal of 2026-11-19, pending the maintainer's answer):
    the count of governed parents the `refs` form cannot name, null when there are none. It is
    optional, so a provenance that names every parent is exactly #1868's.
    """
    cls = _provenance_class()
    assert set(cls.model_fields) == {
        "entity_type",
        "entity_id",
        "produced_by_job_id",
        "subject_refs",
        "unnamed_subjects",
    }
    assert not cls.model_fields["unnamed_subjects"].is_required()


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_provenance_omits_computed_at_and_refuses_it() -> None:
    """Omitted, not optional: a caller cannot attach a time the composition has no source for.

    `extra="forbid"` is what makes the omission hold on the way in as well as on the way out.
    """
    cls = _provenance_class()
    assert "computed_at" not in cls.model_fields
    assert "computed_at" not in cls.model_json_schema(mode="validation")["properties"]
    with pytest.raises(pydantic.ValidationError):
        _provenance(computed_at=datetime.datetime.now(datetime.UTC).isoformat())


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_provenance_is_frozen() -> None:
    """A composed object a view reads must not be edited between composition and response."""
    provenance = _provenance()
    with pytest.raises(pydantic.ValidationError):
        provenance.entity_type = "backtest"  # type: ignore[attr-defined]


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_the_entity_id_is_a_uuid() -> None:
    """The ten shapes are addressed by UUID (#1868); a slug or a ref is not an entity id."""
    entity_id = new_uuid7()
    assert _provenance(entity_id=str(entity_id)).entity_id == entity_id  # type: ignore[attr-defined]
    with pytest.raises(pydantic.ValidationError):
        _provenance(entity_id="profile:motor-gb@3")
    schema = _provenance_class().model_json_schema(mode="validation")
    assert schema["properties"]["entity_id"]["format"] == "uuid"


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
@pytest.mark.parametrize("entity_type", sorted(ENTITY_TYPES))
def test_each_of_the_ten_entity_types_is_admitted(entity_type: str) -> None:
    assert _provenance(entity_type=entity_type).entity_type == entity_type  # type: ignore[attr-defined]


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_entity_type_is_declared_as_a_closed_set_of_exactly_the_ten_names() -> None:
    """The coordinator's constraint for slice 2: `entity_type` is a `Literal` or a `StrEnum`
    of exactly the ten shape names, declared in `model-schema`, never a free `str`.

    Checked twice: on the Python annotation, and on the generated schema, because the
    generated contract is the binding surface for field names and types (FR-24) and a
    `str` with a validator would pass the first reading while publishing an open string.
    """
    annotation = _provenance_class().model_fields["entity_type"].annotation
    if isinstance(annotation, type) and issubclass(annotation, enum.StrEnum):
        declared = {member.value for member in annotation}
        assert len(annotation) == len(ENTITY_TYPES)
    else:
        assert typing.get_origin(annotation) is typing.Literal, (
            f"entity_type is {annotation!r}; it must be a Literal or a StrEnum"
        )
        declared = set(typing.get_args(annotation))
        assert len(typing.get_args(annotation)) == len(ENTITY_TYPES)
    assert declared == ENTITY_TYPES

    schema = _provenance_class().model_json_schema(mode="validation")
    node = schema["properties"]["entity_type"]
    if "$ref" in node:
        node = schema["$defs"][node["$ref"].rsplit("/", 1)[-1]]
    assert node["type"] == "string"
    assert sorted(node["enum"]) == sorted(ENTITY_TYPES)


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
@pytest.mark.parametrize(
    "outside",
    [
        # A real artifact type, and still refused: a subject, never the entity a `Provenance`
        # describes, until a requirement brings it in (FR-6's amendment).
        "dataset_version",
        "model",
        # The class names, and near misses of the snake_case names.
        "Profile",
        "ValidationReport",
        "validation-report",
        "transparency",
        "regression_suite",
        "",
    ],
)
def test_an_entity_type_outside_the_ten_is_refused(outside: str) -> None:
    """A closed set: a typo in a composer is a 422/500 in a test, not a badge naming nothing."""
    with pytest.raises(pydantic.ValidationError):
        _provenance(entity_type=outside)


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_a_job_id_that_was_never_recorded_is_null_and_still_present() -> None:
    """`produced_by_job_id` is `UUID | None` and always serialised.

    Null is "not recorded" (slice 3's badge text), and the key must be there for the badge to
    say so; an absent key would read as a different shape. It is required, with no default,
    so a composer that forgets it fails rather than silently stating "not recorded".
    """
    provenance = _provenance(produced_by_job_id=None)
    dumped = provenance.model_dump(mode="json")
    assert "produced_by_job_id" in dumped
    assert dumped["produced_by_job_id"] is None
    assert _provenance_class().model_fields["produced_by_job_id"].is_required()


# -- The refs form --------------------------------------------------------------------------


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_subject_refs_are_artifact_refs_and_travel_as_canonical_strings() -> None:
    """#1810 B / #1868 (a): the refs form, `{type}:{slug}@{version}` on the wire (ID-3)."""
    refs = ("rating_version:motor-gb@26", "rating_version:motor-gb@27")
    provenance = _provenance(entity_type="dislocation_run", subject_refs=refs)
    assert all(isinstance(ref, ArtifactRef) for ref in provenance.subject_refs)  # type: ignore[attr-defined]
    assert provenance.model_dump(mode="json")["subject_refs"] == list(refs)
    # Round trip: a client reading the JSON back gets the same object.
    again = _provenance_class().model_validate_json(provenance.model_dump_json())
    assert again == provenance


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_subject_refs_keep_the_order_they_were_given_in() -> None:
    """Order is meaningful (ModelComparison, DislocationRun, RegressionRun), so the field is
    a sequence, never a set: the composer's order is the order the reader sees."""
    refs = ("model:motor-b@2", "model:motor-a@1", "model:motor-c@4")
    provenance = _provenance(entity_type="model_comparison", subject_refs=refs)
    assert [str(ref) for ref in provenance.subject_refs] == list(refs)  # type: ignore[attr-defined]


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
@pytest.mark.parametrize(
    "bad",
    [
        "model:motor-freq",  # no version
        "model:motor-freq@0",  # versions start at 1 (ID-2)
        "validation_report:motor@1",  # not an artifact-ref type
        "1f0b6a52-0000-7000-8000-000000000000",  # a bare UUID is an entity id, not a ref
    ],
)
def test_a_subject_ref_outside_the_refs_grammar_is_refused(bad: str) -> None:
    with pytest.raises(pydantic.ValidationError):
        _provenance(subject_refs=(bad,))


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_the_schema_declares_subject_refs_as_the_artifact_ref_string() -> None:
    """The generated contract carries the string pattern, not ArtifactRef's three Python
    fields, so the frontend's generated type is `string[]` (contract-schema's ArtifactRef
    note)."""
    schema = _provenance_class().model_json_schema(mode="validation")
    items = schema["properties"]["subject_refs"]["items"]
    if "$ref" in items:
        items = schema["$defs"][items["$ref"].rsplit("/", 1)[-1]]
    assert items["type"] == "string"
    assert items["pattern"] == REF_PATTERN
    assert set(schema["required"]) == {
        "entity_type",
        "entity_id",
        "produced_by_job_id",
        "subject_refs",
    }


# -- The ten read classes -------------------------------------------------------------------


#: Read-side fields beyond `provenance`, by read class. Only one, and it is named here so that a
#: second one cannot be added without this test saying so (#1506 slice 5).
_READ_SIDE_EXTRAS: dict[str, set[str]] = {"DiagnosticsRead": {"chained_factors"}}


def _read_and_base(read_name: str) -> tuple[type[pydantic.BaseModel], type[pydantic.BaseModel]]:
    read: type[pydantic.BaseModel] = getattr(model_schema, read_name)
    base: type[pydantic.BaseModel] = getattr(model_schema, READ_CLASSES[read_name])
    return read, base


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
@pytest.mark.parametrize("read_name", sorted(READ_CLASSES))
def test_each_read_class_is_its_shape_plus_provenance(read_name: str) -> None:
    """The accepted approach: a subclass, the shape's fields unchanged, plus one field.

    One named exception, `DiagnosticsRead`, also carries `chained_factors`, which the route
    composes from the model's definition by the fit's rule and which is never persisted (`02`
    §5.1, #1506 slice 5). It is optional, so the persisted shape still validates as the read."""
    read, base = _read_and_base(read_name)
    assert issubclass(read, base)
    extra = {"provenance"} | (_READ_SIDE_EXTRAS.get(read_name, set()))
    assert set(read.model_fields) == set(base.model_fields) | extra
    for name in _READ_SIDE_EXTRAS.get(read_name, set()):
        assert not read.model_fields[name].is_required(), name
    for name, field in base.model_fields.items():
        assert read.model_fields[name].annotation == field.annotation, name
        assert read.model_fields[name].is_required() == field.is_required(), name
    provenance = read.model_fields["provenance"]
    assert provenance.annotation is model_schema.Provenance  # type: ignore[attr-defined]
    assert provenance.is_required()


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
@pytest.mark.parametrize("read_name", sorted(READ_CLASSES))
def test_each_read_class_keeps_its_shapes_frozen_and_forbidding_config(read_name: str) -> None:
    read, base = _read_and_base(read_name)
    assert read.model_config.get("frozen") is True
    assert read.model_config.get("extra") == "forbid"
    assert base.model_config.get("extra") == "forbid"


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
@pytest.mark.parametrize("base_name", sorted(READ_CLASSES.values()))
def test_the_persisted_shape_is_untouched(base_name: str) -> None:
    """#1519: never persisted. The stored class has no `provenance` field, so the bytes a
    row holds, and any hash over them, cannot move because of this slice.

    A guard, green before the slice and after it: it reads the base classes alone."""
    base: type[pydantic.BaseModel] = getattr(model_schema, base_name)
    assert "provenance" not in base.model_fields
    assert "provenance" not in base.model_json_schema(mode="validation").get("properties", {})


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_each_read_class_is_exported() -> None:
    exported = set(model_schema.__all__)
    assert {"Provenance", *READ_CLASSES} <= exported


@pytest.mark.req("FR-2159")
@pytest.mark.req("FR-6")
def test_a_read_dumps_as_the_stored_shape_plus_provenance_and_cannot_be_stored_back() -> None:
    """Worked on `Profile`: the read's JSON minus `provenance` is the stored JSON byte for
    byte, and the stored class refuses the read's JSON (`extra="forbid"`), so a read can never
    be written back as the artifact."""
    stored = Profile(
        id=new_uuid7(),
        dataset_version_id=new_uuid7(),
        computed_at=datetime.datetime(2026, 11, 17, 9, 0, tzinfo=datetime.UTC),
        job_id=new_uuid7(),
        row_count=3,
    )
    provenance = _provenance(entity_id=stored.id, produced_by_job_id=stored.job_id)
    read_cls = model_schema.ProfileRead  # type: ignore[attr-defined]
    read = read_cls.model_validate({**stored.model_dump(mode="json"), "provenance": provenance})

    dumped = read.model_dump(mode="json")
    assert dumped.pop("provenance") == provenance.model_dump(mode="json")
    assert dumped == stored.model_dump(mode="json")

    with pytest.raises(pydantic.ValidationError):
        Profile.model_validate(read.model_dump(mode="json"))
    assert isinstance(read.provenance.entity_id, UUID)
