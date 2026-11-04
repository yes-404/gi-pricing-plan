"""The two shadow-scoring log sinks keep the quote input out of the log (NFR-499).

`_shadow_task` (the decision, before the response) and `_shadow_score` (the scoring, after it)
each log a failure and never raise it. The failing call carries the quote context, so an
exception's own text can hold quote input; the log line must keep the frames and the type and
drop the text (`safe_job_exc_info`). Both tests are DB-free: the failing call is replaced, and the
objects the sinks pass on are never reached.
"""

from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from app.api import score as score_module

_SENTINEL = "SENTINEL-quote-input-5c91d2e7"


def _boom(*_args: Any, **_kwargs: Any) -> Any:
    raise ValueError(f"cannot read {_SENTINEL}")


@pytest.mark.req("NFR-499", "FR-271")
def test_a_shadow_decision_failure_logs_no_quote_input(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """The flag read raises with the sentinel in its text: the quote is not affected (the task
    is `None`), the line keeps the type and drops the text."""

    async def boom(*args: Any, **kwargs: Any) -> Any:
        _boom()

    monkeypatch.setattr(score_module.settings_service, "resolve", boom)
    caller = SimpleNamespace(environment="uat", workspace_id=uuid4())
    with caplog.at_level(logging.DEBUG):
        task = asyncio.run(
            score_module._shadow_task(  # type: ignore[arg-type]
                None,
                None,
                caller,
                None,
                None,
                None,
                None,
                None,
                None,  # type: ignore[arg-type]
            )
        )
    assert task is None
    assert "shadow scoring decision failed" in caplog.text
    assert "ValueError" in caplog.text
    assert _SENTINEL not in caplog.text


@pytest.mark.req("NFR-499", "FR-271")
def test_a_shadow_scoring_failure_logs_no_quote_input(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """The candidate bundle load raises with the sentinel in its text: nothing propagates, the
    line keeps the type and drops the text."""

    async def boom(*args: Any, **kwargs: Any) -> Any:
        _boom()

    monkeypatch.setattr(score_module, "_compiled_for", boom)
    with caplog.at_level(logging.DEBUG):
        asyncio.run(
            score_module._shadow_score(  # type: ignore[arg-type]
                None,
                None,
                None,
                uuid4(),
                "uat",
                None,
                None,
                None,
                "rating_version:x@1",  # type: ignore[arg-type]
            )
        )
    assert "shadow scoring failed; the response was already sent" in caplog.text
    assert "ValueError" in caplog.text
    assert _SENTINEL not in caplog.text
