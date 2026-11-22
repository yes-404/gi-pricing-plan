"""Prometheus metrics (`07` §5.1, FR-443).

Five families, and the one design decision that matters is what may become a **label**.

`/api/v1/jobs/019a4c...` as a label value creates a new time series per job, and a
Prometheus instance that has seen a million jobs is holding a million series for one
counter. Every label here is drawn from a bounded set: the *route template* rather than the
path, the method, the status class, the Job kind. There is no label anywhere carrying a
UUID, and there must not be.

FR-443 also names scoring latency by environment and rating version. It is not emitted: the
scoring path arrives with WK-671, and the family belongs to #1509 and #1813. It is recorded as
not delivered rather than exposed as a metric that is always zero — a dashboard panel that
reads zero because nothing reports is indistinguishable from one reading zero because nothing
is wrong.

The cache hit rate is the fifth family (`07` §5.1, #1505): `gip_cache_lookups_total`, one
counter with two bounded labels, `cache` and `result`. The unit is a lookup, not a request.
The same rule holds for it: a label set has no sample until its first use, so a cache nobody
has read is absent, not zero. The OIDC key-set cache is not reported.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterable
from typing import Final

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from prometheus_client.core import CounterMetricFamily, Metric
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST
from prometheus_client.registry import Collector

__all__ = [
    "CONTENT_TYPE_LATEST",
    "REGISTRY",
    "auth_failures",
    "blob_bytes",
    "blob_objects",
    "job_duration_seconds",
    "job_queue_depth",
    "ladder_reconciliation_failed",
    "observe_cache_lookup",
    "observe_request",
    "rate_limit_unenforced",
    "render",
    "reset_cache_lookups",
    "track_cache",
]

#: A registry of our own rather than the process-global default. Two apps in one test
#: session would otherwise share counters and each see the other's traffic — the same
#: reason `create_app` takes its settings instead of reading globals.
REGISTRY: Final = CollectorRegistry()

#: Buckets chosen around the budgets the platform is actually held to: NFR-518's 5 ms
#: permission check, NFR-468's 300 ms one-way read, NFR-471's 500 ms report summary,
#: and `03`'s 50 ms p99 quote. Default buckets would put 300 ms and 500 ms in one bin and
#: make two different budgets indistinguishable on a graph.
_LATENCY_BUCKETS: Final = (
    0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.3, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0,
)

_requests = Counter(
    "gip_http_requests_total",
    "HTTP requests by route template, method and status class.",
    ("route", "method", "status"),
    registry=REGISTRY,
)

_request_seconds = Histogram(
    "gip_http_request_duration_seconds",
    "HTTP request duration by route template and method.",
    ("route", "method"),
    buckets=_LATENCY_BUCKETS,
    registry=REGISTRY,
)

auth_failures = Counter(
    "gip_auth_failures_total",
    "Failed authentications by reason (07 FR-392). `reason` is the closed set of "
    "`app.auth.service.AuthFailureReason`, never the presented credential.",
    ("reason",),
    registry=REGISTRY,
)

rate_limit_unenforced = Counter(
    "gip_rate_limit_unenforced_total",
    "Requests admitted without a rate-limit decision because the counter was unavailable "
    "(FR-452, RL-1347 rule 5), by the caller's Environment ('' for a caller with none).",
    ("environment",),
    registry=REGISTRY,
)

ladder_reconciliation_failed = Counter(
    "gip_ladder_reconciliation_failed_total",
    "Quotes refused on POST /score because their Premium Ladder did not reconcile "
    "(RL-1346, FR-248), by the caller's Environment ('' for a caller with none).",
    ("environment",),
    registry=REGISTRY,
)

job_queue_depth = Gauge(
    "gip_job_queue_depth",
    "Jobs not yet in a terminal state, by kind and status.",
    ("kind", "status"),
    registry=REGISTRY,
)

job_duration_seconds = Histogram(
    "gip_job_duration_seconds",
    "Completed job wall-clock duration by kind.",
    ("kind",),
    buckets=(1, 5, 15, 60, 300, 900, 1800, 3600, 7200),
    registry=REGISTRY,
)

blob_objects = Gauge(
    "gip_blob_objects",
    "Distinct content-addressed objects in the blob store.",
    registry=REGISTRY,
)

blob_bytes = Gauge(
    "gip_blob_bytes",
    "Total bytes stored, counting each distinct object once.",
    registry=REGISTRY,
)


#: The caches that report, and the results a lookup can end in. Closed sets: a label value
#: outside them is refused rather than exposed, so the family cannot grow a series per caller
#: input. The OIDC key-set cache is deliberately not here (`07` §5.1). `error` is the
#: Redis-backed cache's alone, so an outage is not read as misses; the in-process slot
#: accepts `hit` and `miss` only.
_RESULTS_BY_CACHE: Final = {
    "bundle_slot": frozenset({"hit", "miss"}),
    "diff_cache": frozenset({"hit", "miss", "error"}),
}
_CACHES: Final = frozenset(_RESULTS_BY_CACHE)
_SLOT_RESULTS: Final = ("hit", "miss")


class _CacheLookups(Collector):
    """`gip_cache_lookups_total`, from two sources under one family name.

    A cache that calls `observe_cache_lookup` (the Redis-backed `DiffCache`) is counted here
    as it happens. A cache that keeps integer tallies of its own and is registered with
    `track_cache` (the per-process `BundleSlot`) is read when the scrape runs. A family has
    one name in a registry, so one collector emits both. A label set with a count of zero
    has no sample: it gets its first on first use (`07` §5.1).
    """

    _name = "gip_cache_lookups"
    _doc = "Cache lookups by cache and result (hit, miss, or error for the Redis-backed cache)."
    _labels = ("cache", "result")

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counted: dict[tuple[str, str], int] = {}
        self._tallies: dict[str, Callable[[], tuple[int, int]]] = {}

    def observe(self, cache: str, result: str) -> None:
        if result not in _RESULTS_BY_CACHE.get(cache, frozenset()):
            # A literal message: the arguments are programmer-supplied constants, and none
            # of them is echoed (NFR-499's habit).
            raise ValueError("cache lookup label outside the closed set")
        with self._lock:
            self._counted[(cache, result)] = self._counted.get((cache, result), 0) + 1

    def track(self, cache: str, tally: Callable[[], tuple[int, int]]) -> None:
        if cache not in _CACHES:
            raise ValueError("cache lookup label outside the closed set")
        with self._lock:
            self._tallies[cache] = tally

    def reset(self) -> None:
        with self._lock:
            self._counted.clear()
            self._tallies.clear()

    def describe(self) -> Iterable[Metric]:
        return [CounterMetricFamily(self._name, self._doc, labels=self._labels)]

    def collect(self) -> Iterable[Metric]:
        with self._lock:
            counts = dict(self._counted)
            tallies = dict(self._tallies)
        for cache, tally in tallies.items():
            for result, count in zip(_SLOT_RESULTS, tally(), strict=True):
                counts[(cache, result)] = counts.get((cache, result), 0) + count
        family = CounterMetricFamily(self._name, self._doc, labels=self._labels)
        for (cache, result), count in sorted(counts.items()):
            if count > 0:
                family.add_metric([cache, result], count)
        # A family with no sample is not emitted at all: absent, not zero.
        return [family] if family.samples else []


_cache_lookups = _CacheLookups()
REGISTRY.register(_cache_lookups)


def observe_cache_lookup(cache: str, result: str) -> None:
    """Count one lookup of `cache` ending in `result` (`hit`, `miss` or `error`).

    The unit is a lookup, not a request (`07` §4.6). `cache` is `bundle_slot` (`hit`,
    `miss`) or `diff_cache` (also `error`); anything else raises `ValueError`.
    """
    _cache_lookups.observe(cache, result)


def track_cache(cache: str, tally: Callable[[], tuple[int, int]]) -> None:
    """Report a cache that keeps its own `(hits, misses)` integers, read at scrape time.

    Registering a second tally under the same name replaces the first: there is one
    `bundle_slot` per API process. A tally of `(0, 0)` gives the cache no sample.
    """
    _cache_lookups.track(cache, tally)


def reset_cache_lookups() -> None:
    """Forget every counted lookup and every tracked tally. For tests: the registry is
    process-wide, and a cache's first-use state is part of what they assert."""
    _cache_lookups.reset()


def observe_request(route: str, method: str, status_code: int, seconds: float) -> None:
    """Record one request.

    `route` must be the **template** (`/api/v1/jobs/{job_id}`), never the resolved path.
    The caller is responsible for that because only the router knows which it matched, and
    getting it wrong is a slow leak rather than an error: the counter keeps working and the
    Prometheus instance keeps growing.
    """
    # `2xx`/`4xx`/`5xx` rather than the code: the alert anyone writes is "the error rate
    # rose", and 47 distinct status labels per route make that a sum over a guess about
    # which codes count.
    _requests.labels(route=route, method=method, status=f"{status_code // 100}xx").inc()
    _request_seconds.labels(route=route, method=method).observe(seconds)


def render() -> bytes:
    """The exposition text for a scrape."""
    return generate_latest(REGISTRY)
