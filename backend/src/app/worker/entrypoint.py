"""Module-level Celery app for the `celery` CLI.

    celery -A app.worker.entrypoint worker --queues compute --concurrency 2
    celery -A app.worker.entrypoint beat          # runs the outbox relay on a schedule

Kept apart from `tasks.py` because constructing the app reads settings and opens a broker
connection. Every test, every tooling script and the API process import worker code without
wanting either — so the side effect lives in the one module that is only imported when a
worker is actually being started.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta

from app.config import Settings, load_settings
from app.db.session import Database
from app.observability.logging import configure_logging
from app.platform.blobs import BlobStore
from app.platform.tenancy import require_tenant_binding
from app.worker.celery_app import TASK_RELAY_OUTBOX
from app.worker.tasks import create_worker

__all__ = ["app"]

_settings = load_settings()
configure_logging(_settings.log_level)


async def _require_tenant_binding(settings: Settings) -> None:
    database = Database(settings)
    try:
        await require_tenant_binding(settings, database, BlobStore(settings))
    finally:
        await database.dispose()


# FR-436: a worker bound to another tenant's stores must not consume a single task. This
# is a plain call at import, not a Celery signal handler: `Signal.send` catches what a
# receiver raises, so a handler that raised would let the worker carry on (proved in
# `backend/tests/test_tenant_binding.py`). An exception here stops `celery -A` before the
# worker exists.
asyncio.run(_require_tenant_binding(_settings))

app = create_worker(_settings)

# FR-406: the relay is what moves committed intent to the broker. It runs on a short
# schedule rather than being triggered by the writer, because the writer is inside the
# transaction and must not touch the broker at all.
#
# The interval is the floor on submit-to-running latency, which NFR-527 budgets at 5 s.
app.conf.beat_schedule = {
    "relay-outbox": {
        "task": TASK_RELAY_OUTBOX,
        "schedule": timedelta(seconds=1),
        "options": {"queue": "default", "expires": 10},
    }
}

# The `dataset.*`, `model.*`, `rate_table.*`, `rating.*` and `dislocation.*` handlers.
# Registered here rather than at import of the handler modules, so importing one for a type
# or a test does not mutate a process-global registry.
from app.worker.data_handlers import register_data_handlers  # noqa: E402
from app.worker.dislocation_handlers import register_dislocation_handlers  # noqa: E402
from app.worker.model_handlers import register_model_handlers  # noqa: E402
from app.worker.rate_table_handlers import register_rate_table_handlers  # noqa: E402
from app.worker.rating_handlers import register_rating_handlers  # noqa: E402
from app.worker.scoring_handlers import register_scoring_handlers  # noqa: E402

register_data_handlers()
register_model_handlers()
register_rate_table_handlers()
register_rating_handlers()
register_scoring_handlers()
register_dislocation_handlers()
