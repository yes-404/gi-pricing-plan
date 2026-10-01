"""Typed signals for a graph refusal (03 FR-212), so a caller maps a refusal to its code
by class, never by matching the message text.

Both are `ValueError` subclasses: raised inside a `model_validator`, pydantic reports
them as `type == "value_error"` with the instance at `errors()[i]["ctx"]["error"]`.
"""

from __future__ import annotations


class GraphCycleError(ValueError):
    """The steps form a cycle (FR-212)."""


class GraphUnresolvedRefError(ValueError):
    """A step consumes, or a declared output names, a value nothing produces (FR-212)."""
