"""Deterministic train/test partitioning (`01` FR-DATA-33, FR-DATA-36).

**The property this module exists for:** two independent calls, one asking for `train` and
one asking for `test`, must produce complementary row sets — every row in exactly one part,
no row in both. They are separate Jobs, minutes apart, in different processes; the only
thing they share is the split artifact's `method`, `seed` and `fractions`.

So the assignment is a **pure function of those three and the frame's row order**, computed
identically by every caller, rather than a shuffle whose result is stored. That is what
makes FR-DATA-36's "provably identical holdout rows" a fact about the arithmetic instead of
a promise about bookkeeping.

The three methods `01` FR-DATA-33 names:

* `random` — a seeded uniform draw per row.
* `temporal` — before the cutoff trains, on or after it tests. Seedless by nature: a date
  is not random, and a temporal split that moved with a seed would not be a temporal split.
* `grouped_by_key` — every row sharing a key lands in the same part, so a policy with
  twelve monthly rows cannot appear in both. Assigning those rows independently is the
  standard leakage bug, and it flatters the holdout.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping

import numpy as np
import polars as pl

__all__ = ["SplitError", "assign_parts", "partition"]

#: `01` FR-DATA-33's declared split methods.
METHODS = ("random", "temporal", "grouped_by_key")


class SplitError(ValueError):
    """A split that cannot be computed as described."""


def _cumulative(fractions: Mapping[str, float]) -> list[tuple[str, float]]:
    """Part boundaries on `[0, 1)`, in a fixed order.

    Sorted by name rather than left in mapping order: two callers passing the same
    fractions in a different order must get the same partition, and a dict's order is the
    caller's business rather than the split's.
    """
    total = sum(fractions.values())
    if total <= 0:
        raise SplitError("split fractions sum to zero")
    if any(v < 0 for v in fractions.values()):
        raise SplitError("a split fraction is negative")
    if not 0.999 <= total <= 1.001:
        raise SplitError(
            f"split fractions sum to {total:g}, not 1. A split whose parts do not cover "
            "the data drops rows silently, which is the one outcome a holdout cannot have."
        )

    edges: list[tuple[str, float]] = []
    running = 0.0
    for name in sorted(fractions):
        running += fractions[name] / total
        edges.append((name, running))
    return edges


def _uniform_from_seed(n: int, seed: int) -> np.ndarray:
    """`n` draws that depend only on `seed` and `n`.

    `default_rng(seed)` is reproducible across processes and platforms for a given numpy
    generation, which is exactly the guarantee two separate Jobs need.
    """
    return np.asarray(np.random.default_rng(seed).random(n), dtype=np.float64)


def _hash_unit(values: list[object], seed: int) -> np.ndarray:
    """Map each key to `[0, 1)` by hashing it with the seed.

    Hashed rather than drawn, because the same key must land in the same place regardless
    of how many rows carry it or where they sit — which a positional draw cannot promise.
    `blake2b` rather than `hash()`: Python's is salted per process, so a grouped split
    would land differently in the worker than in the test that verified it.
    """
    out = np.empty(len(values), dtype=np.float64)
    prefix = str(seed).encode()
    for i, value in enumerate(values):
        digest = hashlib.blake2b(prefix + b":" + str(value).encode(), digest_size=8).digest()
        out[i] = int.from_bytes(digest, "big") / float(1 << 64)
    return out


def assign_parts(
    frame: pl.DataFrame,
    *,
    method: str,
    seed: int,
    fractions: Mapping[str, float] | None = None,
    key_column: str | None = None,
    time_column: str | None = None,
    cutoff: str | None = None,
    parts: tuple[str, str] = ("train", "test"),
) -> pl.Series:
    """The part name for every row, as a string series aligned to `frame`."""
    if method not in METHODS:
        raise SplitError(f"unknown split method {method!r}; expected one of {METHODS}")

    if method == "temporal":
        if not time_column or cutoff is None:
            raise SplitError(
                "a temporal split needs `time_column` and `cutoff`. Without them there is "
                "no time to split on, and falling back to a random split would record a "
                "method the data was not partitioned by."
            )
        if time_column not in frame.columns:
            raise SplitError(f"temporal split names {time_column!r}, which is not a column")
        before, after = parts
        column = frame[time_column]
        boundary = pl.Series([cutoff]).cast(column.dtype, strict=False)[0]
        if boundary is None:
            raise SplitError(
                f"cutoff {cutoff!r} cannot be read as {column.dtype}; a cutoff that does "
                "not compare against the column would put every row on one side."
            )
        return pl.Series(
            "part", [before if v is not None and v < boundary else after for v in column]
        )

    shares = dict(fractions or {parts[0]: 0.8, parts[1]: 0.2})
    edges = _cumulative(shares)

    if method == "grouped_by_key":
        if not key_column:
            raise SplitError("a grouped_by_key split needs `key_column`")
        if key_column not in frame.columns:
            raise SplitError(f"grouped split names {key_column!r}, which is not a column")
        u = _hash_unit(frame[key_column].to_list(), seed)
    else:
        u = _uniform_from_seed(frame.height, seed)

    names = np.empty(frame.height, dtype=object)
    lower = 0.0
    for name, upper in edges:
        names[(u >= lower) & (u < upper)] = name
        lower = upper
    # A draw of exactly 1.0 is impossible from `random()`, but float accumulation can leave
    # the last edge a hair below it. Unassigned rows belong to the final part rather than
    # to none — a row in no part is a row silently dropped.
    names[names == None] = edges[-1][0]  # noqa: E711
    return pl.Series("part", names.tolist(), dtype=pl.String)


def partition(
    frame: pl.DataFrame,
    *,
    method: str,
    seed: int,
    fractions: Mapping[str, float] | None = None,
    key_column: str | None = None,
    time_column: str | None = None,
    cutoff: str | None = None,
    parts: tuple[str, str] = ("train", "test"),
) -> dict[str, pl.DataFrame]:
    """Every part of the split, keyed by name.

    Returns all parts rather than the one asked for, so a caller materialising one part can
    still assert the partition is complete — `sum(heights) == frame.height` is the check
    that a split has not quietly lost rows, and it needs every part to make.
    """
    assignment = assign_parts(
        frame,
        method=method,
        seed=seed,
        fractions=fractions,
        key_column=key_column,
        time_column=time_column,
        cutoff=cutoff,
        parts=parts,
    )
    tagged = frame.with_columns(assignment.alias("__part__"))
    return {
        name: tagged.filter(pl.col("__part__") == name).drop("__part__")
        for name in sorted(set(assignment.to_list()))
    }
