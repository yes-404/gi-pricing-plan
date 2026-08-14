"""Artifact identity and references.

`00-overview.md` ID-1..ID-4. The canonical external reference to any artifact is
`{type}:{slug}@{version}` — the form that appears in traces, generated documentation and
the audit log, so it is parsed and rendered in exactly one place.
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Final, Self

from pydantic import BaseModel, Field, GetJsonSchemaHandler, model_serializer, model_validator
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

__all__ = ["ARTIFACT_TYPES", "ArtifactRef", "BlobRef", "Slug"]

#: Every artifact type that may appear in a reference. Extending this is a spec change:
#: `docs/contracts/schemas/common/artifact-ref.schema.json` carries the same list.
ARTIFACT_TYPES: Final[frozenset[str]] = frozenset(
    {
        "dataset", "dataset_version", "validation_rule", "validation_rule_set",
        "reference_table", "factor", "banding", "grouping", "model", "custom_objective",
        "custom_metric", "peril_structure", "rating_algorithm", "sub_graph", "rate_table",
        "rating_version", "optimisation_run", "gipp_check", "monitor", "dossier",
    }
)

_SLUG = r"[a-z0-9][a-z0-9-]{1,62}"
# Versions start at 1 (ID-2), so `@0` is a malformed reference rather than a valid
# reference to an invalid version — rejecting it here keeps the error message consistent
# with every other malformed form.
_REF_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<type>[a-z_]+):(?P<slug>{_SLUG})@(?P<version>[1-9][0-9]*)$"
)

Slug = Annotated[str, Field(pattern=rf"^{_SLUG}$")]

#: The wire form of a reference, as a JSON Schema pattern. Built from the same pieces the
#: parser uses, so the schema and the parser cannot disagree — the contract previously
#: carried a hand-copied pattern that admitted `@0`, which the parser rejected.
REF_PATTERN: Final[str] = (
    rf"^({'|'.join(sorted(ARTIFACT_TYPES))}):{_SLUG}@[1-9][0-9]*$"
)


class ArtifactRef(BaseModel, frozen=True):
    """A pinned reference to one immutable artifact version (ID-3).

    Frozen because FR-OVR-1 makes artifacts immutable; a reference that could be mutated
    in place would let a "pinned" dependency drift, which is the failure ID-3 exists to
    prevent.

    **On the wire it is the string `{type}:{slug}@{version}`, not an object.** ID-3 makes
    that string the canonical external form — it is what appears in traces, documentation
    and the audit log, and what a person pastes into a support ticket. Structured in
    Python, flat in JSON: the validator parses the string and the serialiser renders it,
    so neither side of the boundary sees the other's representation.
    """

    type: str
    slug: str
    version: int = Field(ge=1)

    def __str__(self) -> str:
        return f"{self.type}:{self.slug}@{self.version}"

    @model_validator(mode="before")
    @classmethod
    def _accept_the_canonical_string(cls, value: Any) -> Any:
        """Parse `"model:motor-ad-frequency@7"`; leave a mapping alone."""
        if isinstance(value, str):
            match = _REF_RE.match(value)
            if match is None:
                raise ValueError(
                    f"{value!r} is not a valid artifact reference "
                    "({type}:{slug}@{version})"
                )
            if match["type"] not in ARTIFACT_TYPES:
                raise ValueError(
                    f"unknown artifact type {match['type']!r}; extending the set is a "
                    "spec change"
                )
            return {
                "type": match["type"],
                "slug": match["slug"],
                "version": int(match["version"]),
            }
        return value

    @model_serializer
    def _render_canonical(self) -> str:
        return str(self)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Emit the string form, so generated clients and the contract agree.

        Without this the schema describes the Python object — three properties — and a
        frontend generated from it would expect an object where every spec, trace and
        audit row carries a string.
        """
        return {
            "type": "string",
            "pattern": REF_PATTERN,
            "title": "ArtifactRef",
            "description": "Canonical artifact reference {type}:{slug}@{version} (ID-3).",
            "examples": ["model:motor-ad-frequency@7", "rating_version:motor-gb@27"],
        }

    @classmethod
    def parse(cls, raw: str) -> Self:
        """Parse the canonical string form, rejecting anything else.

        >>> str(ArtifactRef.parse("model:motor-ad-frequency@7"))
        'model:motor-ad-frequency@7'
        """
        match = _REF_RE.match(raw)
        if match is None:
            raise ValueError(
                f"{raw!r} is not a valid artifact reference "
                "({type}:{slug}@{version})"
            )
        kind = match["type"]
        if kind not in ARTIFACT_TYPES:
            raise ValueError(f"unknown artifact type {kind!r}; extending the set is a spec change")
        return cls(type=kind, slug=match["slug"], version=int(match["version"]))


class BlobRef(BaseModel, frozen=True):
    """A content-addressed object reference (ID-4)."""

    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    bytes_: int = Field(ge=0, alias="bytes")
    media_type: str
    part_count: int | None = Field(default=None, ge=1)

    model_config = {"populate_by_name": True}
