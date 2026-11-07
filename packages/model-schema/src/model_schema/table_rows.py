"""One markdown table row, split (FD-1484).

Stdlib only: `scripts/` load this file by path, under a bare `python3` with no project
packages (`.github/workflows/docs.yml`), so it imports nothing from `model_schema` or beyond.
The row-splitting logic lives here once; a second splitter would eventually disagree with
this one about where a cell ends.

An escaped pipe (`\\|`) is kept **as written** inside its cell, so a register comparison is a
byte comparison; a caller wanting display text unescapes it.
"""

from __future__ import annotations

import re
from typing import Final

__all__ = ["UNESCAPED_PIPE", "cell_count", "endpoint_row", "is_table_row", "split_row"]

#: A pipe that separates cells: not the `\|` markdown uses for a pipe inside one.
UNESCAPED_PIPE: Final = re.compile(r"(?<!\\)\|")

_PLACEHOLDER: Final = "\x00"

#: The method cell of a `§5.1` interface row: `GET`, or several (`GET`/`PUT`).
_METHOD_CELL: Final = re.compile(r"`?([A-Z]+(?:`?/`?[A-Z]+)*)`?")


def is_table_row(line: str) -> bool:
    """Whether the line opens with a pipe, as a table row does."""
    return line.lstrip().startswith("|")


def split_row(line: str) -> list[str]:
    """Cells of a table row, stripped, an escaped `\\|` kept as written."""
    hidden = line.replace("\\|", _PLACEHOLDER)
    cells = [cell.strip() for cell in hidden.strip().strip("|").split("|")]
    return [cell.replace(_PLACEHOLDER, "\\|") for cell in cells]


def cell_count(line: str) -> int:
    """The separators' count less one, as the cell-count check reads it."""
    return len(UNESCAPED_PIPE.findall(line)) - 1


def endpoint_row(line: str) -> tuple[str, str] | None:
    """The (method cell, path cell) of a `§5.1` REST row, or `None` for any other line.

    The method cell is returned without its outer backticks (``GET`/`PUT`` for a pair); the
    path cell is the whole cell, which may hold several backticked paths.
    """
    if not line.startswith("|"):
        return None
    cells = split_row(line)
    if len(cells) < 2 or not (len(cells) > 2 or line.rstrip().endswith("|")):
        return None
    method = _METHOD_CELL.fullmatch(cells[0])
    if method is None:
        return None
    return method.group(1), cells[1]
