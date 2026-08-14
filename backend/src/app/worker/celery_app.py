"""The Celery application and its queue routing (FR-PLAT-13, FR-PLAT-22).

Four queues with independently sized pools, because they have nothing in common:

* ``compute`` — few, fat, long (a model fit).
* ``scoring`` — many, thin, latency-bound (`03` NFR-RATE-1 is 50 ms at p99).
* ``io`` — network-bound (ingestion, exports).
* ``default`` — everything else.

Putting a model fit on the scoring pool starves the quote path, which is the one with a
hard latency budget. Routing is derived from the Job kind rather than chosen at the call
site, so a caller cannot get it wrong.

Redis is the broker (OQ-PLAT-1, decided 2026-08-14). Nothing durable lives in it — every
task it carries is reconstructible from the `outbox` table (FR-PLAT-22, FR-PLAT-51).
"""

from __future__ import annotations

from celery import Celery

from app.config import Settings, load_settings

__all__ = ["TASK_RELAY_OUTBOX", "TASK_RUN_JOB", "build_celery"]

TASK_RUN_JOB = "app.worker.run_job"
TASK_RELAY_OUTBOX = "app.worker.relay_outbox"


def build_celery(settings: Settings | None = None) -> Celery:
    """Construct the Celery app. Takes settings so a test can point it elsewhere."""
    settings = settings or load_settings()
    app = Celery("gi-pricing", broker=settings.redis_url.get_secret_value())

    app.conf.update(
        # JSON only. Pickle would let a broker message execute arbitrary code in a worker,
        # and the broker is reachable by everything on the network the platform runs on.
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        # The outbox is the source of truth for "this job should run" (FR-PLAT-51), so a
        # task is acknowledged only after it completes. A worker killed mid-job leaves the
        # message for redelivery rather than losing the work silently.
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        # One task at a time per child process. A fit saturates a core; prefetching a
        # second means it waits behind the first while another worker sits idle.
        worker_prefetch_multiplier=1,
        broker_connection_retry_on_startup=True,
        task_default_queue="default",
    )
    return app
