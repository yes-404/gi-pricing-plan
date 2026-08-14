"""Structured JSON logging with the request's identity attached (FR-PLAT-38).

Every line carries `trace_id`, and — once those exist — `workspace_id`, `principal_id`,
`job_id` and the entity reference. They are pulled from the context rather than passed,
so a log call in a service module cannot omit them by accident.

FR-PLAT-10 and R3 also apply here: **logs never contain secrets**. Nothing in this module
serialises arbitrary objects; a caller passes explicit fields, and `SecretValue` (§3.4)
has no representation that survives `str()`.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from app.observability.trace import current_trace_id

__all__ = ["JsonFormatter", "configure_logging", "get_logger"]

# Attributes present on every LogRecord; anything else a caller attached is a custom field
# worth emitting. Enumerated rather than filtered by prefix so a future stdlib addition
# shows up as an unexpected key in a test rather than silently polluting every line.
_RESERVED = frozenset(
    {
        "args", "asctime", "created", "exc_info", "exc_text", "filename", "funcName",
        "levelname", "levelno", "lineno", "module", "msecs", "message", "msg", "name",
        "pathname", "process", "processName", "relativeCreated", "stack_info",
        "taskName", "thread", "threadName",
    }
)


class JsonFormatter(logging.Formatter):
    """Render a record as one JSON object per line.

    JSON rather than a text template because these lines are queried, not read: "show me
    every line for this trace id" is the first question asked when a job fails, and it is
    a filter over a field rather than a regex over prose.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%03dZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        trace_id = current_trace_id()
        if trace_id is not None:
            payload["trace_id"] = trace_id

        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # default=str keeps a UUID or datetime from turning a log call into an exception —
        # losing a log line is worse than rendering a value approximately.
        return json.dumps(payload, default=str, separators=(",", ":"))


def configure_logging(level: str = "INFO") -> None:
    """Install the JSON formatter as the only handler on the root logger.

    Existing handlers are removed rather than added to: uvicorn installs its own, and the
    result would be every line emitted twice, once structured and once not.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(level)

    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True


def get_logger(name: str) -> logging.Logger:
    """A logger that emits through the configured JSON handler."""
    return logging.getLogger(name)
