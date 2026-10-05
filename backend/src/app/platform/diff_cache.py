"""The DP3 diff cache (rulings 2026-08-28, option (b)): compute-on-read, cached.

The cache key is the diff's deterministic inputs, and nothing else:

- the content hashes of **both** versions, so an entry can never serve a diff the
  caller did not ask for,
- the hash of the current version's definition (its keys and value), because a key of
  another role, type or binding joins a portfolio differently, and
- the portfolio dataset version's identity and, with it, the workspace — a Dataset
  Version is immutable (`00` §2), so a changed portfolio snapshot is a different entry
  and a stale weighted diff can never be served.

**Never a wall-clock date**: a date key would silently serve yesterday's diff when
today's is wanted; with identity keys, invalidation is exact. No TTL either — an
entry for an immutable pair can never go stale, so eviction is memory policy, not
correctness.

Fail-open on purpose: Redis is an optimisation, not the correctness path. A cache
outage degrades to a plain compute-on-read, never to a 500.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

from redis.exceptions import RedisError

from model_schema.rating import RateTable, RateTableDiff

__all__ = ["DiffCache", "cells_key", "definition_hash", "version_content_hash"]

_log = logging.getLogger(__name__)


class _CacheClient(Protocol):
    """The slice of the Redis client the cache uses — a dict-backed fake satisfies
    it, so the key contract is testable without a broker."""

    async def get(self, key: str) -> Any: ...
    async def set(self, key: str, value: bytes) -> Any: ...


def version_content_hash(cells: Sequence[dict[str, str]]) -> str:
    """Content hash of a version's cells: canonical JSON, row order ignored.

    Canonical across storages: `sort_keys` normalises the key order a loader emits
    and the explicit row sort removes insertion order, so a rows-stored version and
    its parquet twin hash identically (FR-232's same-artifact guarantee).
    """
    canonical = sorted(cells, key=lambda cell: tuple(cell.values()))
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def definition_hash(table: RateTable) -> str:
    """Hash of what decides how a diff is weighted: the keys and the value declaration.

    Two versions with the same cells but a key of another role, type or binding
    (`banding_ref`, `factor_ref`) join a portfolio differently, so the definition is part
    of the cache key (`RL-1361` item 5).
    """
    canonical = {
        "keys": [key.model_dump(mode="json") for key in table.keys],
        "value": table.value.model_dump(mode="json"),
    }
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _entry_name(
    kind: str,
    current_hash: str,
    baseline_hash: str,
    definition_hash: str,
    portfolio_dataset_version_id: UUID | None,
    workspace_id: UUID | None,
) -> str:
    """The workspace joins the name only with a portfolio: an unweighted diff is a function of
    the two versions and the definition alone, and a weighted one of a portfolio that is scoped
    to a workspace (`RL-1361` item 5)."""
    if portfolio_dataset_version_id is None:
        portfolio = "none"
    else:
        portfolio = f"{portfolio_dataset_version_id}:{workspace_id}"
    return f"rate_table:{kind}:{current_hash}:{baseline_hash}:{definition_hash}:{portfolio}"


def cells_key(
    current_hash: str,
    baseline_hash: str,
    definition_hash: str,
    portfolio_dataset_version_id: UUID | None,
    workspace_id: UUID | None,
) -> str:
    """The name of one query's stored cell artifact (`RL-1418` T1), keyed like the diff."""
    return _entry_name(
        "diff_cells", current_hash, baseline_hash, definition_hash,
        portfolio_dataset_version_id, workspace_id,
    )


class DiffCache:
    """The DP3 read-path cache: `key` names the entry, `get`/`set` move the artifact.

    The value is the `RateTableDiff` itself, serialised as JSON — the same artifact
    the row-backed 200 returns, so a cache hit and a compute produce identical
    payloads by construction.
    """

    def __init__(self, client: _CacheClient) -> None:
        self._client = client

    @classmethod
    def from_url(cls, url: str) -> DiffCache:
        """A cache over the platform's Redis, built from a connection URL."""
        import redis.asyncio

        return cls(redis.asyncio.from_url(url))  # type: ignore[no-untyped-call]

    def key(
        self,
        current_hash: str,
        baseline_hash: str,
        definition_hash: str,
        portfolio_dataset_version_id: UUID | None,
        workspace_id: UUID | None,
    ) -> str:
        """The entry name (`_entry_name`)."""
        return _entry_name(
            "diff", current_hash, baseline_hash, definition_hash,
            portfolio_dataset_version_id, workspace_id,
        )

    async def get(self, key: str) -> RateTableDiff | None:
        try:
            raw = await self._client.get(key)
        except RedisError as exc:
            _log.warning(
                "diff cache read failed; computing without it",
                extra={"error_type": type(exc).__name__},
            )
            return None
        if raw is None:
            return None
        return RateTableDiff.model_validate_json(raw)

    async def set(self, key: str, diff: RateTableDiff) -> None:
        try:
            await self._client.set(key, diff.model_dump_json().encode())
        except RedisError as exc:
            _log.warning(
                "diff cache write failed; serving the computed diff",
                extra={"error_type": type(exc).__name__},
            )
