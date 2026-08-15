"""Prometheus metrics (`07` §5.1, FR-PLAT-40).

Four families, and the one design decision that matters is what may become a **label**.

`/api/v1/jobs/019a4c...` as a label value creates a new time series per job, and a
Prometheus instance that has seen a million jobs is holding a million series for one
counter. Every label here is drawn from a bounded set: the *route template* rather than the
path, the method, the status class, the Job kind. There is no label anywhere carrying a
UUID, and there must not be.

FR-PLAT-40 also names scoring latency by environment and rating version, and cache hit
rate. Neither is emitted: the scoring path arrives with W11 and there is no cache yet. They
are recorded as not delivered rather than exposed as a metric that is always zero — a
dashboard panel that reads zero because nothing reports is indistinguishable from one
reading zero because nothing is wrong.
"""

from __future__ import annotations

from typing import Final

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST

__all__ = [
    "CONTENT_TYPE_LATEST",
    "REGISTRY",
    "blob_bytes",
    "blob_objects",
    "job_duration_seconds",
    "job_queue_depth",
    "observe_request",
    "render",
]

#: A registry of our own rather than the process-global default. Two apps in one test
#: session would otherwise share counters and each see the other's traffic — the same
#: reason `create_app` takes its settings instead of reading globals.
REGISTRY: Final = CollectorRegistry()

#: Buckets chosen around the budgets the platform is actually held to: NFR-GOV-1's 5 ms
#: permission check, NFR-DATA-4's 300 ms one-way read, NFR-DATA-7's 500 ms report summary,
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
