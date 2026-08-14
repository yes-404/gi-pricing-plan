"""Reading the formats FR-DATA-3 accepts.

> CSV, TSV, parquet, and Excel (`.xlsx`, first sheet or a named sheet) for
> `upload`/`object_store` sources, and any query result for `sql`. Compressed variants
> (`.gz`, `.zst`) are transparently handled.

Every reader takes **bytes** rather than a path. Uploads arrive over HTTP and object-store
reads arrive as streams; neither is a file on this machine, and a signature that takes a
path invites a temporary file whose lifetime somebody has to own.

Parsing is deliberately permissive: dates that do not match are read as strings and become
nulls, which `pricing_core.data.ingest.partition_rejects` then quarantines with a reason.
Failing the whole file because one row has a bad date would discard 4.8 million good rows
to punish seventeen.
"""

from __future__ import annotations

import gzip
import io
from typing import Final

import polars as pl
import zstandard

from app.errors import PlatformError

__all__ = ["SUPPORTED_SUFFIXES", "read_tabular"]

SUPPORTED_SUFFIXES: Final[tuple[str, ...]] = (
    ".csv",
    ".tsv",
    ".txt",
    ".parquet",
    ".pqt",
    ".xlsx",
)

#: A compressed upload that expands beyond this is refused rather than decompressed. A
#: 100 kB file that becomes 40 GB in memory is a decompression bomb, and an ingestion
#: endpoint that accepts uploads is exactly where one arrives.
MAX_DECOMPRESSED_BYTES: Final = 2 * 1024**3


def _decompress(data: bytes, name: str) -> tuple[bytes, str]:
    """Transparently handle `.gz` and `.zst`, returning the inner name (FR-DATA-3)."""
    lowered = name.lower()
    if lowered.endswith(".gz"):
        expanded = gzip.decompress(data)
        _refuse_if_oversized(len(expanded))
        return expanded, name[: -len(".gz")]
    if lowered.endswith(".zst"):
        decompressor = zstandard.ZstdDecompressor()
        expanded = decompressor.decompress(data, max_output_size=MAX_DECOMPRESSED_BYTES)
        _refuse_if_oversized(len(expanded))
        return expanded, name[: -len(".zst")]
    return data, name


def _refuse_if_oversized(size: int) -> None:
    if size > MAX_DECOMPRESSED_BYTES:
        raise PlatformError(
            "REJECT_RATE_EXCEEDED",
            "Decompressed upload is too large",
            413,
            f"The archive expands to {size} bytes, beyond the {MAX_DECOMPRESSED_BYTES} "
            "limit. Ingest it from an object store rather than as an upload.",
        )


def read_tabular(data: bytes, filename: str, *, sheet: str | None = None) -> pl.DataFrame:
    """Read an uploaded file into a frame, choosing the reader by suffix (FR-DATA-3)."""
    payload, name = _decompress(data, filename)
    lowered = name.lower()

    try:
        if lowered.endswith((".parquet", ".pqt")):
            return pl.read_parquet(io.BytesIO(payload))
        if lowered.endswith(".xlsx"):
            # `sheet_name=None` reads the first sheet, which is FR-DATA-3's default.
            return pl.read_excel(
                io.BytesIO(payload), sheet_name=sheet, infer_schema_length=0
            )
        if lowered.endswith((".tsv", ".txt")):
            return _read_delimited(payload, separator="\t")
        if lowered.endswith(".csv"):
            return _read_delimited(payload, separator=",")
    except PlatformError:
        raise
    except Exception as exc:
        raise PlatformError(
            "SCHEMA_INFERENCE_CONFLICT",
            "The file could not be read",
            422,
            f"{type(exc).__name__} while reading {filename!r}. The file may be corrupt, "
            "or its extension may not match its contents.",
        ) from exc

    raise PlatformError(
        "SCHEMA_INFERENCE_CONFLICT",
        "Unsupported file type",
        422,
        f"{filename!r} is not one of {list(SUPPORTED_SUFFIXES)} (FR-DATA-3).",
    )


def _read_delimited(payload: bytes, *, separator: str) -> pl.DataFrame:
    """Read delimited text with **everything as a string**.

    Type inference happens later, from the confirmed schema (FR-DATA-4). Letting the CSV
    reader guess means a policy id of `007` becomes `7`, and a column that is numeric in
    this extract and alphanumeric in the next changes type between versions of the same
    dataset — which is a schema change nobody made.
    """
    return pl.read_csv(
        io.BytesIO(payload),
        separator=separator,
        infer_schema=False,
        try_parse_dates=False,
        null_values=["", "NA", "N/A", "NULL", "null"],
        truncate_ragged_lines=False,
    )
