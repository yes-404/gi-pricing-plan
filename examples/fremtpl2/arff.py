"""Minimal ARFF reader for the freMTPL2 files (`07` FR-439).

Fifty lines rather than a dependency: ARFF's full grammar has sparse rows, dates, relational
attributes and comment handling that these two files do not use, and a parser that supports
none of that is more honest than one that appears to.

**Nominal values arrive single-quoted** — `'D'`, `'B12'`, `'Regular'`. Left in place they
become part of the level, so a `VehBrand` of `'B12'` and `B12` would be two categories and
every one-way over it would be wrong. The quotes are stripped here, once.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path


def to_csv(path: Path) -> bytes:
    """Read an ARFF file and return it as CSV bytes the platform can ingest.

    CSV rather than a frame, because the platform's own entry point is a file: the seed
    should go in the way a user's data goes in, not through a side door that skips
    `read_tabular`, column normalisation and the reject partition.
    """
    header: list[str] = []
    rows: list[list[str]] = []
    in_data = False

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("%"):
                continue
            lowered = stripped.lower()
            if lowered.startswith("@attribute"):
                # `@attribute VehBrand {'B1','B10',…}` — the name is the second token, and
                # splitting on whitespace is safe because none of these names contain any.
                header.append(stripped.split()[1].strip("'\""))
            elif lowered.startswith("@data"):
                in_data = True
            elif in_data:
                rows.append([value.strip().strip("'\"") for value in stripped.split(",")])

    if not header:
        raise ValueError(f"{path.name} declares no @attribute lines")

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")
