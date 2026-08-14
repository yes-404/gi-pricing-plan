"""What a Job kind actually does.

The dispatcher exists before the work does: W2 builds the platform, and the handlers for
`dataset.*` and `model.*` arrive with W4 and W5. Registering them here keeps the worker
free of knowledge about any particular module — it moves a Job through its lifecycle and
calls one function.

A handler is **synchronous** and takes a `ProgressCallback`. That is the `pricing-core`
contract (ADR-0001): the maths is pure, blocking, and reports through the injected
callback. The worker runs it in a thread so the event loop stays free to service the
progress writes the callback makes.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from model_schema import JobKind, JobResult
from pricing_core.progress import ProgressCallback

__all__ = ["HANDLERS", "JobHandler", "handler_for", "register_handler"]

#: `(parameters, progress) -> JobResult`. Blocking by design.
JobHandler = Callable[[dict[str, Any], ProgressCallback], JobResult]

HANDLERS: dict[JobKind, JobHandler] = {}


def register_handler(kind: JobKind, handler: JobHandler) -> None:
    """Register the implementation for a Job kind.

    Refuses to replace an existing registration: two handlers for one kind means the
    behaviour depends on import order, and the symptom is a job that does the wrong thing
    only in production, where the import graph differs.
    """
    if kind in HANDLERS:
        raise ValueError(f"a handler for {kind.value!r} is already registered")
    HANDLERS[kind] = handler


def handler_for(kind: JobKind) -> JobHandler | None:
    """The handler for a kind, or `None` when the deployment has none."""
    return HANDLERS.get(kind)
