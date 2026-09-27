"""Documenting the error model in the published contract (FR-450, FR-451).

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

__all__ = ["PROBLEM_MEDIA_TYPE", "problems", "without_fastapi_validation_error"]

PROBLEM_MEDIA_TYPE: Final = "application/problem+json"

#: One line per status the platform actually returns, with the codes `07` §5.1 enumerates.
_TITLES: Final[dict[int, str]] = {
    400: "Malformed request",
    401: "Authentication failed",
    403: "Not permitted",
    404: "Not found",
    409: "Conflict",
    413: "Payload too large",
    422: "Request validation failed",
    429: "Rate limited",
    500: "Internal server error",
    501: "Not implemented",
    503: "Not ready",
}


def problems(*statuses: int) -> dict[int | str, dict[str, Any]]:
    """Build the `responses=` mapping declaring RFC 9457 problems for these statuses.

    `422` is included by FastAPI automatically with *its* schema; passing it here replaces
    that with ours, which is what the platform returns. **Any route taking a path or query
    parameter can return 422**, because a non-UUID id fails to parse before the handler
    runs — seven routes omitted it and published FastAPI's `HTTPValidationError` instead,
    which is a second error shape a client would have to branch on.

    An unlisted status is refused rather than given a generic title. The same reasoning as
    the error-code registry: a typo that silently produces "Problem" is a documentation
    defect nobody notices, and the set of statuses this platform returns is small and
    known.
    """
    unknown = sorted(set(statuses) - set(_TITLES))
    if unknown:
        raise ValueError(
            f"no problem title for status {unknown}. Add it to `_TITLES` — and check the "
            "owning spec declares the status before the route claims it."
        )
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


#: The methods an OpenAPI path item may carry. A path item also holds keys that are not
#: operations (`parameters`, `summary`), so the values cannot simply be iterated.
_METHODS: Final = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})


def _is_injected_validation_error(response: dict[str, Any]) -> bool:
    """FastAPI's own `422`, told apart from ours by its media type and its schema."""
    schema = response.get("content", {}).get("application/json", {}).get("schema", {})
    ref = schema.get("$ref", "") if isinstance(schema, dict) else ""
    return bool(ref.endswith("/HTTPValidationError"))


def without_fastapi_validation_error(document: dict[str, Any]) -> dict[str, Any]:
    """Delete the `422` FastAPI injects on its own, and the two schemas it drags in.

    FastAPI adds a `422` — typed as its `HTTPValidationError` — to every operation that has
    any parameter and does not already declare one. This platform replaced that shape:
    `errors.install_error_handlers` answers a `RequestValidationError` with an RFC 9457
    problem, so the injected response documents a body the API never sends, and a client
    generated from the document carries a second error type to branch on. That is the
    FR-451 finding this module was written for, arriving by a route the module did not
    anticipate.

    Until W32-7 the per-route convention was enough, because an operation with no
    parameters got no injected `422` and so never needed to opt out. Declaring
    `Workspace-Id` on `require_caller` gave 112 operations a parameter in one edit, and
    five that had never had one began publishing `HTTPValidationError`. A convention every
    route author must remember cannot catch a change made in a dependency, which is why
    this runs over the assembled document instead.

    A route that can genuinely fail validation declares `problems(422)` and is untouched:
    ours is `application/problem+json` and refs `ProblemDetail`, so it never matches. The
    five are not given `problems(422)` instead, because they cannot return one — the
    header is optional and unparsed by FastAPI, and `api.deps` answers a malformed
    `Workspace-Id` with `403 WORKSPACE_SCOPE_DENIED`. Declaring it would advertise an
    error they never produce, which is the thing `problems` exists to stop.
    """
    for path_item in document.get("paths", {}).values():
        for method, operation in path_item.items():
            if method not in _METHODS:
                continue
            responses = operation.get("responses", {})
            response = responses.get("422")
            if response is not None and _is_injected_validation_error(response):
                del responses["422"]

    # Unreferenced once the injected responses are gone. Dropped by name rather than by
    # reachability: the platform emits neither shape from anywhere, so their presence in
    # the published contract is a defect however they arrived.
    schemas = document.get("components", {}).get("schemas", {})
    for name in ("HTTPValidationError", "ValidationError"):
        schemas.pop(name, None)
    return document
