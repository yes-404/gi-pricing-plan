"""The DP3 diff cache (rulings 2026-08-28): compute-on-read, keyed by the diff's
deterministic inputs — both versions' content hashes and the portfolio dataset
version's identity (immutable, `00` §2) — never a wall-clock date.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest

from app.platform.diff_cache import DiffCache, version_content_hash
from model_schema.rating import RateTableDiff


class _FakeClient:
    """A dict-backed Redis stand-in — get/set on bytes, recording its calls."""

    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}
        self.gets = 0
        self.sets = 0

    async def get(self, key: str) -> bytes | None:
        self.gets += 1
        return self.store.get(key)

    async def set(self, key: str, value: bytes) -> None:
        self.sets += 1
        self.store[key] = value


def _diff() -> RateTableDiff:
    return RateTableDiff(
        changed_cells=1,
        max_abs_change_pct=Decimal("2.84"),
        exposure_weighted_mean_change_pct=Decimal("2.84"),
    )


async def test_the_key_hashes_both_versions_and_the_portfolio_identity() -> None:
    cache = DiffCache(_FakeClient())
    current = "a" * 64
    baseline = "b" * 64
    portfolio = uuid4()

    key = cache.key(current, baseline, portfolio)
    assert key == f"rate_table:diff:{current}:{baseline}:{portfolio}"

    # Deterministic — a wall-clock date in the key would make a second call differ.
    assert cache.key(current, baseline, portfolio) == key
    # Every input is load-bearing: a different current or baseline hash, a different
    # portfolio identity, or none at all, names a different entry.
    assert cache.key(baseline, current, portfolio) != key
    assert cache.key(current, "c" * 64, portfolio) != key
    assert cache.key(current, baseline, uuid4()) != key
    assert cache.key(current, baseline, None) == (
        f"rate_table:diff:{current}:{baseline}:none"
    )


async def test_the_cache_round_trips_a_diff() -> None:
    client = _FakeClient()
    cache = DiffCache(client)
    key = cache.key("a" * 64, "b" * 64, None)

    assert await cache.get(key) is None
    await cache.set(key, _diff())
    assert await cache.get(key) == _diff()


async def test_a_cache_failure_never_fails_the_diff() -> None:
    """Fail-open: Redis is an optimisation, not the correctness path — an outage
    degrades to a plain compute, never to a 500."""
    import redis

    class _BrokenClient:
        async def get(self, key: str) -> bytes | None:
            raise redis.RedisError("redis is down")

        async def set(self, key: str, value: bytes) -> None:
            raise redis.RedisError("redis is down")

    cache = DiffCache(_BrokenClient())
    key = cache.key("a" * 64, "b" * 64, None)

    assert await cache.get(key) is None
    await cache.set(key, _diff())  # must not raise


def test_version_content_hash_is_canonical_and_content_addressed() -> None:
    cells = [
        {"driver_age_band": "17-20", "relativity": "1.9200"},
        {"driver_age_band": "21-24", "relativity": "1.4500"},
        {"driver_age_band": "25-29", "relativity": "1.1200"},
    ]
    # Row order is not content: the same cells in another order hash identically.
    assert version_content_hash(list(reversed(cells))) == version_content_hash(cells)
    # Any change in any cell is a different hash.
    changed = [{"driver_age_band": "17-20", "relativity": "1.95"}, *cells[1:]]
    assert version_content_hash(changed) != version_content_hash(cells)


@pytest.mark.req("FR-RATE-17")
async def test_the_cache_round_trips_through_real_redis(settings) -> None:
    """The wire form is bytes of JSON — proven against the compose Redis; skipped
    when Redis is not reachable (the `test_celery_broker` convention)."""
    import redis.asyncio as aioredis

    client = aioredis.from_url(settings.redis_url.get_secret_value())
    try:
        await client.ping()
    except Exception as exc:
        pytest.skip(f"Redis not reachable: {type(exc).__name__}")

    cache = DiffCache(client)
    key = cache.key("a" * 64, "b" * 64, None)
    await client.delete(key)
    try:
        assert await cache.get(key) is None
        await cache.set(key, _diff())
        assert await cache.get(key) == _diff()
    finally:
        await client.delete(key)


@pytest.mark.req("FR-RATE-17")
async def test_diff_is_computed_on_miss_and_served_from_the_cache_on_hit(
    database, workspace_id, principal, blob_store
) -> None:
    """DP3 (b): compute-on-read — a miss computes and stores; a hit serves the stored
    artifact without recomputing (the recording client sees one set, then none)."""
    from uuid import uuid4

    from backend.tests.test_rate_tables_service import (
        _seed,
        _table_slug,
    )

    from app.config import Settings
    from app.platform import rate_tables as svc

    family = f"mf-{uuid4().hex[:8]}"
    slug = _table_slug()
    await _seed(database, workspace_id, principal, family, slug, blob_store)
    content = (
        b"driver_age_band,relativity\n"
        b"17-20,1.9200\n"
        b"21-24,1.4500\n"
        b"25-29,1.1200\n"
    )
    await svc.import_confirmed(
        database,
        workspace_id,
        principal.id,
        Settings(),
        blob_store,
        slug=slug,
        version=1,
        filename="import.csv",
        content=content,
    )

    client = _FakeClient()
    cache = DiffCache(client)
    first = await svc.diff(
        database,
        workspace_id,
        slug,
        2,
        "previous",
        blob_store=blob_store,
        cache=cache,
    )
    assert client.gets == 1
    assert client.sets == 1

    second = await svc.diff(
        database,
        workspace_id,
        slug,
        2,
        "previous",
        blob_store=blob_store,
        cache=cache,
    )
    assert second == first
    assert client.gets == 2
    assert client.sets == 1  # served from the cache — no recompute, no re-store

    portfolio = uuid4()
    await svc.diff(
        database,
        workspace_id,
        slug,
        2,
        "previous",
        blob_store=blob_store,
        cache=cache,
        portfolio_dataset_version_id=portfolio,
    )
    assert client.sets == 2  # a different portfolio identity is a different entry
