"""FR-244's enforced allow-list for authored rating strings (RL-1312 item 1, RL-1313 DP-G3).

ZEN's expression language is far larger than anything a rating algorithm should use: indexing,
member access, object literals, string and date functions, `in`, `%` and `^` all compile today.
This module is a small tokenizer that refuses everything outside the ruled lists. It runs
before FR-276's engine compile, which still runs, because a construct can be on the list and
still not compile.

The three tuples below are the code's copy of FR-244's amended text in
`docs/specs/03-rating-engine.md`; `test_rating_vocabulary.py` compares them item for item.
Parentheses, and the brackets and comma of `min([...])` / `max([...])`, are structure, not
listed operators. `pricing_core.data.expressions` never parses this grammar (RL-1312).
"""

from __future__ import annotations

import re
from collections.abc import Mapping

#: FR-244's **Operators:** clause. `?` and `:` are the two halves of the ternary `c ? a : b`.
OPERATORS: tuple[str, ...] = (
    "+", "-", "*", "/",
    "==", "!=", "<", "<=", ">", ">=",
    "and", "or", "not",
    "?", ":", "??",
)
#: FR-244's **Literals:** clause, beside numbers and single-quoted strings.
LITERAL_WORDS: tuple[str, ...] = ("true", "false", "null")
#: FR-244's **Functions:** clause. `min` and `max` take one array literal, `number` takes one
#: argument (RL-1322, correcting RL-1312: a lookup's output is a string); there is no rounding
#: function (RL-1312, OQ-1316).
FUNCTIONS: tuple[str, ...] = ("min", "max", "abs", "number")

_ARRAY_FUNCTIONS = frozenset({"min", "max"})
_WORD_OPERATORS = frozenset(op for op in OPERATORS if op.isalpha())
_SYMBOL_OPERATORS = tuple(
    sorted((op for op in OPERATORS if not op.isalpha()), key=len, reverse=True)
)

_NUMBER = re.compile(r"\d+(?:\.\d+)?")
_STRING = re.compile(r"'[^'\n]*'")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_STRUCTURE = frozenset("()[],")


def _refused(construct: str) -> str:
    return f"`{construct}` is not on FR-244's allow-list"


def _scan(text: str) -> tuple[list[tuple[str, int, int]], str | None]:
    """The tokens of `text` with their `[start, end)` spans, and the first refused construct."""
    tokens: list[tuple[str, int, int]] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char.isspace():
            i += 1
        elif (match := _NUMBER.match(text, i)) or (match := _STRING.match(text, i)):
            tokens.append((match.group(0), i, match.end()))
            i = match.end()
        elif char == "'":
            return tokens, _refused("'") + " (an unterminated string)"
        elif match := _NAME.match(text, i):
            word = match.group(0)
            start = i
            i = match.end()
            if word == "in":
                return tokens, _refused("in")
            called = text[i:].lstrip().startswith("(")
            if called and word not in FUNCTIONS and word not in _WORD_OPERATORS:
                return tokens, _refused(word)
            tokens.append((word, start, i))
        elif symbol := next((op for op in _SYMBOL_OPERATORS if text.startswith(op, i)), None):
            tokens.append((symbol, i, i + len(symbol)))
            i += len(symbol)
        elif char in _STRUCTURE:
            tokens.append((char, i, i + 1))
            i += 1
        else:
            return tokens, _refused(char)
    return tokens, None


def _tokenize(text: str) -> tuple[list[str], str | None]:
    """The tokens of `text`, and the first refused construct found while scanning, if any."""
    spans, refused = _scan(text)
    return [token for token, _, _ in spans], refused


def rename_tokens(text: str, mapping: Mapping[str, str]) -> str:
    """`text` with each FR-244 name TOKEN that is a key of `mapping` replaced by its value.

    Renaming is by token, never by substring (RL 9586 DP-S2-2): `ncd` is renamed and `ncd_years`
    is not. A function, a word operator and a literal word (`min`, `and`, `true`) are never
    renamed, and a string literal is one token that is not a name. Everything between tokens,
    whitespace included, is kept as written. Raises `ValueError` on a construct the allow-list
    refuses, since there is no token boundary to rename at.
    """
    spans, refused = _scan(text)
    if refused is not None:
        raise ValueError(refused)
    keep = set(FUNCTIONS) | set(LITERAL_WORDS) | _WORD_OPERATORS
    out: list[str] = []
    cursor = 0
    for token, start, end in spans:
        if token in mapping and token not in keep and _NAME.fullmatch(token):
            out.append(text[cursor:start])
            out.append(mapping[token])
            cursor = end
    out.append(text[cursor:])
    return "".join(out)


def _array_argument(tokens: list[str], start: int) -> tuple[set[int], str | None]:
    """The positions of the brackets and commas that belong to the `min([...])` / `max([...])`
    whose name is at `start`; or the refused construct. A nested call registers its own."""
    name = tokens[start]
    only_array = _refused(name) + f" (only the array form `{name}([...])` is ruled)"
    if tokens[start + 1 : start + 3] != ["(", "["]:
        return set(), only_array
    owned = {start + 2}
    brackets, parens = 1, 0
    for j in range(start + 3, len(tokens)):
        token = tokens[j]
        if token == "[":
            brackets += 1
        elif token == "(":
            parens += 1
        elif token == ")":
            parens -= 1
        elif token == "," and brackets == 1 and parens == 0:
            owned.add(j)
        elif token == "]":
            brackets -= 1
            if brackets == 0:
                if tokens[j + 1 : j + 2] != [")"]:
                    return set(), only_array
                return owned | {j}, None
    return set(), _refused("[") + " (unclosed)"


def check_allow_list(text: str) -> str | None:
    """The first construct in `text` FR-244 does not name, or `None` if all are on the list."""
    tokens, refused = _tokenize(text)
    if refused is not None:
        return refused
    structural: set[int] = set()
    for index, token in enumerate(tokens):
        if token in _ARRAY_FUNCTIONS and tokens[index + 1 : index + 2] == ["("]:
            allowed, refused = _array_argument(tokens, index)
            if refused is not None:
                return refused
            structural |= allowed
        elif token in _ARRAY_FUNCTIONS:
            return _refused(token) + " (only the array form `" + token + "([...])` is ruled)"
        elif token == "number" and tokens[index + 1 : index + 3] == ["(", ")"]:
            return _refused(token) + " (it takes exactly one argument)"
    for index, token in enumerate(tokens):
        if token in {"[", "]", ","} and index not in structural:
            return _refused(token)
    return None
