"""The stored `ValidationReport` body keeps its bytes (FD-2090, SL-2088; `01` §4.6).

The stored body **is** the artifact (`ValidationReportRow`), so the outcome the response
carries (`overall`, `counts`) is never written into it. The fixture is a body captured
before the response-side shape existed; it must still read, and writing it back must give
exactly its text, key order included.
"""

from __future__ import annotations

import json
import pathlib

import pytest
from pydantic import ValidationError

from model_schema.validation import ValidationReport, ValidationReportView

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


def _report_with(*outcomes: str) -> ValidationReport:
    body = json.loads(PRE_FIX.read_text())
    template = body["results"][0]
    body["results"] = [
        {**template, "rule_id": f"00000000-0000-0000-0000-{i:012d}", "outcome": outcome}
        for i, outcome in enumerate(outcomes, start=1)
    ]
    return ValidationReport.model_validate(body)


@pytest.mark.req("FR-42")
@pytest.mark.parametrize(
    ("outcomes", "overall"),
    [
        (("pass", "skipped"), "pass"),
        (("pass", "warn"), "pass_with_warnings"),
        (("warn", "fail", "error"), "fail"),
        (("pass", "error", "warn"), "error"),
    ],
)
def test_the_view_agrees_with_the_report_for_each_verdict(
    outcomes: tuple[str, ...], overall: str
) -> None:
    report = _report_with(*outcomes)
    view = ValidationReportView.of(report)

    assert view.overall.value == overall == report.overall.value
    assert dict(view.counts) == report.counts


@pytest.mark.req("FR-42")
@pytest.mark.parametrize(
    "tampered",
    [{"overall": "pass"}, {"counts": {"pass": 0, "warn": 0, "fail": 0, "error": 0, "skipped": 0}}],
)
def test_a_view_whose_outcome_disagrees_with_its_results_is_refused(
    tampered: dict[str, object],
) -> None:
    """`overall` is derived, never assigned (`01` §4.6): a view cannot say otherwise."""
    dumped = ValidationReportView.of(_report_with("pass", "warn")).model_dump(mode="json")

    with pytest.raises(ValidationError, match="derived from results"):
        ValidationReportView.model_validate({**dumped, **tampered})


@pytest.mark.req("FR-42", "NFR-469")
def test_a_view_cannot_pose_as_a_stored_body() -> None:
    dumped = ValidationReportView.of(_report_with("pass", "warn")).model_dump(mode="json")

    with pytest.raises(ValidationError) as refused:
        ValidationReport.model_validate(dumped)
    assert {(e["type"], e["loc"]) for e in refused.value.errors()} >= {
        ("extra_forbidden", ("overall",)),
        ("extra_forbidden", ("counts",)),
    }
    assert ValidationReportView.model_validate(dumped).model_dump(mode="json") == dumped


@pytest.mark.req("FR-42", "NFR-469")
def test_the_view_has_the_reports_fields_in_the_reports_order_plus_the_outcome() -> None:
    """The ten stored fields keep their order, so the stored bytes cannot move."""
    assert list(ValidationReportView.model_fields) == [
        *ValidationReport.model_fields,
        "overall",
        "counts",
    ]
