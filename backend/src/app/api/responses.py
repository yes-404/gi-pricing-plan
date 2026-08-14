"""Documenting the error model in the published contract (FR-PLAT-47, FR-PLAT-48).

`docs/contracts/openapi/generated.json` is what the frontend generates its types from
(`CLAUDE.md` §2). Until this module existed the document described only success shapes, so
a generated client was typed against FastAPI's default `HTTPValidationError` — a shape the
platform replaced and never emits — and had no type at all for the RFC 9457 problem it
does emit. The drift check could not catch it, because the contract faithfully described
the code; both were wrong together.

Routes declare which problems they can return. That is more work than a blanket default
and it is the point: a route that can return `409` says so, and one that cannot does not
advertise an error it will never produce.
"""

from __future__ import annotations

from typing import Any, Final

from model_schema import ProblemDetail

__all__ = ["PROBLEM_MEDIA_TYPE", "problems"]

PROBLEM_MEDIA_TYPE: Final = "application/problem+json"

#: One line per status the platform actually returns, with the codes `07` §5.1 enumerates.
_TITLES: Final[dict[int, str]] = {
    400: "Malformed request",
    401: "Authentication failed",
    403: "Not permitted",
    404: "Not found",
    409: "Conflict",
    422: "Request validation failed",
    429: "Rate limited",
    500: "Internal server error",
    503: "Not ready",
}


def problems(*statuses: int) -> dict[int | str, dict[str, Any]]:
    """Build the `responses=` mapping declaring RFC 9457 problems for these statuses.

    `422` is included by FastAPI automatically with *its* schema; passing it here replaces
    that with ours, which is what the platform returns.
    """
    return {
        status: {
            "model": ProblemDetail,
            "description": _TITLES.get(status, "Problem"),
            # A `$ref` to the component FastAPI emits from `model=`, not an inlined
            # schema. Inlining copies the model's `$defs` into each response, and those
            # refs then resolve nowhere in the assembled document — which the docs audit
            # catches and a client would hit at generation time.
            "content": {
                PROBLEM_MEDIA_TYPE: {
                    "schema": {"$ref": "#/components/schemas/ProblemDetail"}
                }
            },
        }
        for status in statuses
    }
