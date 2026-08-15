"""Module-level Celery app for the `celery` CLI.

    celery -A app.worker.entrypoint worker --queues compute --concurrency 2
    celery -A app.worker.entrypoint beat          # runs the outbox relay on a schedule

Kept apart from `tasks.py` because constructing the app reads settings and opens a broker
connection. Every test, every tooling script and the API process import worker code without
wanting either — so the side effect lives in the one module that is only imported when a
worker is actually being started.
"""

from __future__ import annotations

from datetime import timedelta

from app.config import load_settings
from app.observability.logging import configure_logging
from app.worker.celery_app import TASK_RELAY_OUTBOX
from app.worker.tasks import create_worker

__all__ = ["app"]

_settings = load_settings()
configure_logging(_settings.log_level)

app = create_worker(_settings)

# FR-PLAT-51: the relay is what moves committed intent to the broker. It runs on a short
# schedule rather than being triggered by the writer, because the writer is inside the
# transaction and must not touch the broker at all.
#
# The interval is the floor on submit-to-running latency, which NFR-PLAT-2 budgets at 5 s.
app.conf.beat_schedule = {
    "relay-outbox": {
        "task": TASK_RELAY_OUTBOX,
        "schedule": timedelta(seconds=1),
        "options": {"queue": "default", "expires": 10},
    }
}

# The `dataset.*` and `model.*` handlers. Registered here rather than at import of the
# handler modules, so importing one for a type or a test does not mutate a process-global
# registry.
from app.worker.data_handlers import register_data_handlers  # noqa: E402
from app.worker.model_handlers import register_model_handlers  # noqa: E402

register_data_handlers()
register_model_handlers()
