"""Artifact identity and references.

`00-overview.md` ID-1..ID-4. The canonical external reference to any artifact is
`{type}:{slug}@{version}` — the form that appears in traces, generated documentation and
the audit log, so it is parsed and rendered in exactly one place.
"""

from __future__ import annotations

import re
from typing import Annotated, Final, Self

from pydantic import BaseModel, Field

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
_REF_RE: Final[re.Pattern[str]] = re.compile(rf"^(?P<type>[a-z_]+):(?P<slug>{_SLUG})@(?P<version>\d+)$")

Slug = Annotated[str, Field(pattern=rf"^{_SLUG}$")]


class ArtifactRef(BaseModel, frozen=True):
    """A pinned reference to one immutable artifact version (ID-3).

    Frozen because FR-OVR-1 makes artifacts immutable; a reference that could be mutated
    in place would let a "pinned" dependency drift, which is the failure ID-3 exists to
    prevent.
    """

    type: str
    slug: str
    version: int = Field(ge=1)

    def __str__(self) -> str:
        return f"{self.type}:{self.slug}@{self.version}"

    @classmethod
    def parse(cls, raw: str) -> Self:
        """Parse the canonical string form, rejecting anything else.

        >>> str(ArtifactRef.parse("model:motor-ad-frequency@7"))
        'model:motor-ad-frequency@7'
        """
        match = _REF_RE.match(raw)
        if match is None:
            raise ValueError(f"{raw!r} is not a valid artifact reference ({{type}}:{{slug}}@{{version}})")
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
