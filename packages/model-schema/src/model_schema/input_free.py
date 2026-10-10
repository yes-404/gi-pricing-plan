"""A validator refusal whose message is authored text with no submitted value in it
(NFR-499; FD-1589 row 8, remedy (c)).

`pricing_core.safe_error` keeps this exception's message where it keeps no other `ValueError`'s:
a request-validation 422 and a stored `ValidationError` detail both show it. That is safe only
because every raise site passes a string literal (or an f-string over module constants alone),
which `tests/test_input_free_raises.py` holds by AST. A message names the field and the rule,
never the value it was given. Raised inside a pydantic validator, it is reported as
`type == "value_error"`, with the instance at `errors()[i]["ctx"]["error"]`, like
`graph_errors`'s signals.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Identifier:
    """A structural identifier of the submitted artifact (a step id, a node id), with the schema
    pattern its field declares (DP-8 (b), the lead's ruling of 2026-10-10 16:07:46 BST)."""

    value: str
    pattern: str


def identifier(value: str, pattern: str) -> Identifier:
    return Identifier(value, pattern)


class InputFreeError(ValueError):
    """A `ValueError` whose message is a literal: it names the field and the rule, never the value.

    It may name an identifier of the artifact's own structure, passed as a keyword built by
    `identifier(value, PATTERN)` with the field's own schema pattern. The constructor checks it:
    a value that does not match is refused, and a plain `ValueError` with a literal message is
    raised in its place, so the value is never echoed. Quote and policy values are never passed.
    """

    def __init__(self, message: str, /, **identifiers: Identifier) -> None:
        for named in identifiers.values():
            if not (isinstance(named.value, str) and re.fullmatch(named.pattern, named.value)):
                raise ValueError("an identifier in a validator message did not match its pattern")
        text = (
            message.format(**{k: repr(v.value) for k, v in identifiers.items()})
            if identifiers
            else message
        )
        super().__init__(text)
