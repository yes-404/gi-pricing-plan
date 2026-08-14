"""Setting resolution (`07` §4.4, FR-PLAT-43..46).

> Settings resolve by precedence: **environment variable → workspace setting → platform
> default**. The effective value and its source are inspectable by an Admin.

The resolution carries its **candidates**, not only the winner. "Why is this setting what
it is?" is a support question with three layers behind it, and answering it from the
effective value alone means reading deployment manifests. Showing what each layer offered
turns that into one screen.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SettingCandidate",
    "SettingResolution",
    "SettingSource",
    "SettingType",
]


class SettingSource(enum.StrEnum):
    """Which layer supplied a value. Ordered by precedence, highest first."""

    ENV = "env"
    WORKSPACE = "workspace"
    DEFAULT = "default"


class SettingType(enum.StrEnum):
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STRING = "string"


class SettingCandidate(BaseModel):
    """What one layer offered, `None` when that layer says nothing."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: SettingSource
    value: Any = None


class SettingResolution(BaseModel):
    """One setting's effective value and how it was arrived at (`07` §4.4)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str
    effective_value: Any
    resolved_from: SettingSource
    candidates: tuple[SettingCandidate, ...]
    type: SettingType
    constraints: dict[str, Any] = Field(default_factory=dict)
    feature_flag: bool = Field(
        default=False,
        description="Feature flags gate optional or risk-bearing capabilities and default "
        "to the safe value (FR-PLAT-46).",
    )
    description: str = ""
