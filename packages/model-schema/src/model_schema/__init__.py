"""Single source of truth for every shape crossing a module boundary (ADR-0002).

Depends on Pydantic and nothing else. No SQLAlchemy, no FastAPI, no Polars — the
`.importlinter` contract enforces it, because a convenience import here would quietly make
this package un-generatable and un-shareable.
"""

from model_schema.envelope import ArtifactEnvelope
from model_schema.money import Currency, DecimalStr, MoneyMinor, Relativity, apply_factor, to_minor
from model_schema.problem import FieldError, ProblemDetail
from model_schema.refs import ARTIFACT_TYPES, ArtifactRef, BlobRef, Slug

__all__ = [
    "ARTIFACT_TYPES",
    "ArtifactEnvelope",
    "ArtifactRef",
    "BlobRef",
    "Currency",
    "DecimalStr",
    "FieldError",
    "MoneyMinor",
    "ProblemDetail",
    "Relativity",
    "Slug",
    "apply_factor",
    "to_minor",
]
