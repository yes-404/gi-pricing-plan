"""Which names a rating step reads (PL-1520 Task 1A; FR-246; RL-1519 DP-F35-1 (ii)).

The save-time FR-246 check (`compile._check_declared_reads`) uses it, and later the trace's
`consumed` and the engine wiring may. The evaluated fields are `authored.EXPRESSION_FIELDS`'
names, so a field added there is read here too (FD-1317's one registry); a step's
`feature_map` keys name graph values the model reads and are added on top.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from pricing_core.rating.authored import EXPRESSION_FIELDS

#: A ZEN expression's string literals, removed before identifiers are read.
_STRING = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"")
#: An identifier not followed by `(` (a call) and not preceded by `.` or `$` (a member).
_NAME = re.compile(r"(?<![\w.$])([A-Za-z_][A-Za-z0-9_]*)\b(?!\s*\()")
_KEYWORDS = frozenset({"true", "false", "null", "and", "or", "not", "in"})
#: The date `score_one` and `score_batch` stamp into every engine context (`score.py`). A lookup's
#: `as_at` naming it is not a declared read (FR-221; FR-246's clarification, 2026-10-10).
STAMPED_DATE = "effective_date"
_EVALUATED = frozenset(name for _, name in EXPRESSION_FIELDS)


def _names_in(text: str) -> set[str]:
    return {m for m in _NAME.findall(_STRING.sub(" ", text)) if m not in _KEYWORDS}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    return [str(v) for v in (value if isinstance(value, list) else [value])]


def referenced_names(node: Mapping[str, Any]) -> frozenset[str]:
    """Declared `consumes` plus every name the node's evaluated fields read."""
    names = set(_as_list(node.get("consumes")))
    for field in _EVALUATED:
        value = node.get(field)
        if isinstance(value, Mapping):
            value = list(value.values())
        for text in [value] if isinstance(value, str) else value or []:
            if not isinstance(text, str):  # an absent clamp bound is None
                continue
            if field == "as_at" and text == STAMPED_DATE:
                continue  # the quote's stamped date: FR-221 declares no one (FR-246 clarified)
            names |= _names_in(text)
    names |= set((node.get("feature_map") or {}).keys())
    return frozenset(names)
