"""The revalidation sweep's parse path fails on deliberately broken input (OQ-650 (c)).

The sweep (`scripts/revalidate-artifacts.py`) parses every stored artifact against today's
models and reports what no longer reads. The mechanism is the parse path — the same
`model_validate` the API's read routes run — so the unit under test is that parse path,
proven on deliberately broken input per `CLAUDE.md` §13: a check that has never printed a
failure has not been tested.
"""

from __future__ import annotations

import importlib.util
import pathlib
from uuid import uuid4

from model_schema import ValidationReport

ROOT = pathlib.Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "revalidate_artifacts", ROOT / "scripts" / "revalidate-artifacts.py"
)
sweep = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(sweep)


def _valid_report() -> dict:
    return {
        "id": str(uuid4()),
        "dataset_version_id": str(uuid4()),
        "rule_set_id": str(uuid4()),
        "rule_set_version": 1,
        "started_at": "2026-08-15T09:00:00Z",
        "finished_at": "2026-08-15T09:05:00Z",
        "results": [],
        "empty_layers": [],
    }


def test_the_sweep_reports_a_stored_artifact_that_no_longer_reads() -> None:
    """A body written under a looser model — a required field absent — must be reported.

    This is the OQ-650 failure mode: a stored payload parsed on write against whatever
    the model said that day, then parsed on read against whatever it says now. The sweep
    must surface the row the read path would refuse, not stay silent.
    """
    broken = {"rule_set_version": 1}  # missing the six required envelope fields
    checked = sweep._guard(lambda r: ValidationReport.model_validate(r["body"]))
    error = checked({"id": "row-1", "body": broken})
    assert error is not None
    assert "id" in error


def test_the_sweep_passes_a_stored_artifact_that_still_reads() -> None:
    """Positive control: a body that parses today stays silent."""
    checked = sweep._guard(lambda r: ValidationReport.model_validate(r["body"]))
    assert checked({"id": "row-2", "body": _valid_report()}) is None
