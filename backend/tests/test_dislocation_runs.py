"""The Dislocation Run as a backend artifact (03 §5.1, FR-263, FR-265, FR-266; PL-1501).

The `dislocation.run` Job handler, its persisted row (`dislocation_runs`, one writer,
`persist_run`), the routes and the generated contract. Tests are written before their code
(PL-1501 §"Tasks"); each section below is one task's.
"""

from __future__ import annotations

import pytest

from app.errors import RATING_ERROR_CODES

# ---- Task 1: the error code --------------------------------------------------------


@pytest.mark.req("FR-1397")
def test_the_reconciliation_failure_code_is_registered() -> None:
    assert "ATTRIBUTION_RECONCILIATION_FAILED" in RATING_ERROR_CODES
