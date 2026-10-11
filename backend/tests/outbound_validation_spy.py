"""A spy on FastAPI's outbound (response) validation, for NFR-502's property test.

NFR-502 is "validate inbound, never outbound". A 500 on a malformed body observes a *side
effect* of outbound validation, and is blind to a route that validates and passes (returning an
instance of the declared class). This counts the call itself (PL-1364 Acceptance 8b).

The point is `fastapi._compat.v2.ModelField.validate`, counted only when `loc` starts with
`"response"`: every response validation passes through it (the plain-return path via
`serialize_response`, and the JSONL/SSE stream path directly), a raw `Response` return skips it,
and request bodies go through the same method with `loc=("body", ...)`, which the `loc` filter
separates. Measured under fastapi 0.141.1; a control route that *does* validate must count at
least one, in the same process, so a FastAPI change that moves the point fails the control and
not the property.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi._compat import v2


class OutboundValidationSpy:
    """Counts response-validation calls; `reset()` zeroes the count."""

    def __init__(self) -> None:
        self._calls = 0

    @property
    def calls(self) -> int:
        return self._calls

    def reset(self) -> None:
        self._calls = 0

    def _count(self) -> None:
        self._calls += 1


def install_outbound_validation_spy(monkeypatch: pytest.MonkeyPatch) -> OutboundValidationSpy:
    spy = OutboundValidationSpy()
    original = v2.ModelField.validate

    def validate(self: Any, value: Any, values: Any = None, *args: Any, **kwargs: Any) -> Any:
        if tuple(kwargs.get("loc", ()))[:1] == ("response",):
            spy._count()
        if values is None:
            return original(self, value, **kwargs)
        return original(self, value, values, *args, **kwargs)

    monkeypatch.setattr(v2.ModelField, "validate", validate)
    return spy
