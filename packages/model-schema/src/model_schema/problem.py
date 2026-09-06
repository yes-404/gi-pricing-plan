"""The single error shape every module returns (`00` §5.3, FR-450).

RFC 9457 `application/problem+json`, extended with three fields the RFC leaves to the
application: a stable machine `code`, a `trace_id`, and a list of field-level errors.

It lives here rather than in the backend because every module returns it and the frontend
generates its type from it (ADR-704). A second definition anywhere would drift, and the
one thing a client must be able to rely on is that `code` means the same thing everywhere.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["FieldError", "ProblemDetail"]

_CODE_PATTERN = r"^[A-Z][A-Z0-9_]*$"


class FieldError(BaseModel):
    """One field-level failure inside a problem response.

    Present so that a rejected submission can be rendered against the form that produced
    it — FR-403 requires deterministic failures to name the offending field rather
    than only the operation.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    field: str = Field(description="Dotted path to the offending field, e.g. 'spec.family'.")
    code: str = Field(pattern=_CODE_PATTERN, description="Stable machine code for this field.")
    message: str = Field(description="Human-readable explanation.")


class ProblemDetail(BaseModel):
    """An RFC 9457 problem response.

    `code` is the contract, not `title` or `status`: titles are prose and several
    conditions share a status, so a client that branches on anything else is branching on
    something the platform is free to reword.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str = Field(
        default="about:blank",
        description="URI identifying the problem type; documentation lives at that URI.",
    )
    title: str = Field(description="Short human-readable summary, stable per type.")
    status: int = Field(ge=100, le=599, description="HTTP status code.")
    code: str = Field(
        pattern=_CODE_PATTERN,
        description="Stable machine-readable code, namespaced per module and enumerated "
        "in that module's spec. This is what clients branch on.",
    )
    detail: str | None = Field(
        default=None, description="Explanation specific to this occurrence."
    )
    instance: str | None = Field(default=None, description="Path of the failing request.")
    errors: tuple[FieldError, ...] = Field(
        default=(), description="Field-level errors, where the failure is field-attributable."
    )
    trace_id: str | None = Field(
        default=None,
        description="OpenTelemetry trace id for this request. Appears in every log line "
        "for the request, so a support conversation starts with an identifier (FR-445).",
    )
