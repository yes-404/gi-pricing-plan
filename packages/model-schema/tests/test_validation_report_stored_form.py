"""The stored `ValidationReport` body keeps its bytes (FD 8379, SL 8381; `01` §4.6).

The stored body **is** the artifact (`ValidationReportRow`), so the outcome the response
carries (`overall`, `counts`) is never written into it. The fixture is a body captured
before the response-side shape existed; it must still read, and writing it back must give
exactly its text, key order included.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from model_schema.validation import ValidationReport

PRE_FIX = pathlib.Path(__file__).parent / "fixtures" / "validation-report-pre-fix.json"


@pytest.mark.req("FR-42", "NFR-469")
def test_a_pre_fix_body_reads_and_writes_back_byte_identical() -> None:
    """A bare `@computed_field` on `overall` would add two keys here, and then fail the
    re-read with `extra_forbidden`: the stored form must not carry the derived outcome."""
    stored = PRE_FIX.read_text()
    dumped = ValidationReport.model_validate(json.loads(stored)).model_dump(mode="json")

    assert sorted({"overall", "counts"} & dumped.keys()) == []
    assert json.dumps(dumped) == stored


@pytest.mark.req("FR-42")
def test_a_body_holding_only_the_required_fields_still_reads() -> None:
    body = {
        key: json.loads(PRE_FIX.read_text())[key]
        for key in (
            "id",
            "dataset_version_id",
            "rule_set_id",
            "rule_set_version",
            "started_at",
            "finished_at",
        )
    }
    report = ValidationReport.model_validate(body)
    assert report.results == ()
