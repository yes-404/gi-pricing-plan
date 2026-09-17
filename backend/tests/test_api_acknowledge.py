"""The acknowledge route over HTTP (FR-46, FR-47).

`01` §1.3's sharpest write, and it had **no HTTP test at all**: the service beneath it was
covered, the route wiring was not. Swapping its two path parameters — passing `rule_id`
where `report_id` belongs — left all 609 tests green.

The service tests prove the rules. These prove the rules are still reached when the route
is, which is a different claim and the one a wiring defect breaks.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from backend.tests.test_api_datasets import _headers
from fastapi.testclient import TestClient

from app.platform import datasets as dataset_service
from app.platform import validation
from model_schema import (
    RuleOutcome,
    RuleResult,
    Severity,
    ValidationLayer,
    ValidationReport,
    new_uuid7,
)


def _warn(rule_id: UUID | None = None) -> RuleResult:
    return RuleResult(
        rule_id=rule_id or uuid4(),
        rule_slug="severity-outlier",
        rule_version=1,
        layer=ValidationLayer.ACTUARIAL_SANITY,
        severity=Severity.WARN,
        outcome=RuleOutcome.WARN,
        detail="12 claims above the outlier threshold",
    )


async def _stored_report(database, workspace_id, actor, *results: RuleResult) -> UUID:
    async with database.unit_of_work() as session:
        dataset = await dataset_service.create_dataset(
            session, workspace_id=workspace_id, actor=actor, slug=f"ds-{new_uuid7().hex[-8:]}"
        )
        version = await dataset_service.new_version(
            session, workspace_id=workspace_id, actor=actor, dataset_id=dataset.id
        )
    started = datetime.now(UTC)
    report = ValidationReport(
        id=uuid4(),
        dataset_version_id=version.id,
        rule_set_id=uuid4(),
        rule_set_version=1,
        started_at=started,
        finished_at=started + timedelta(seconds=1),
        results=tuple(results),
    )
    async with database.unit_of_work() as session:
        await validation.store_report(
            session, workspace_id=workspace_id, actor=actor, report=report
        )
    return report.id


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    return _headers(principal.id, workspace_id)


@pytest.mark.req("FR-46")
def test_an_actuary_acknowledges_a_warning_through_the_route(
    api_client: TestClient, workspace_id, principal, actuary, database
) -> None:
    """And the acknowledgement lands against the rule that was named, not another one.

    The route takes two ids in its path. Swapping them is invisible to any test that
    checks only the status code, and produces an acknowledgement of nothing.
    """
    warn = _warn()
    report_id = asyncio.get_event_loop().run_until_complete(
        _stored_report(database, workspace_id, principal, warn)
    )

    created = api_client.post(
        f"/api/v1/validation-reports/{report_id}/results/{warn.rule_id}/acknowledge",
        json={"justification": "Large losses reviewed with the reserving team."},
        headers=actuary,
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["report_id"] == str(report_id)
    assert body["rule_id"] == str(warn.rule_id)
    assert body["user_id"] == str(principal.id)

    # The report now reads as acknowledged — the state promotion depends on.
    view = api_client.get(f"/api/v1/validation-reports/{report_id}", headers=actuary).json()
    assert view["results"][0]["acknowledgement"] is not None


@pytest.mark.req("FR-46")
def test_an_unknown_rule_on_a_real_report_is_refused(
    api_client: TestClient, workspace_id, principal, actuary, database
) -> None:
    """The pair is checked, not each id separately.

    This is what a swapped path parameter looks like from outside: both ids are real, the
    combination is not.
    """
    warn = _warn()
    report_id = asyncio.get_event_loop().run_until_complete(
        _stored_report(database, workspace_id, principal, warn)
    )
    refused = api_client.post(
        f"/api/v1/validation-reports/{report_id}/results/{new_uuid7()}/acknowledge",
        json={"justification": "for a rule this report does not carry"},
        headers=actuary,
    )
    assert refused.status_code == 404, refused.text

    # ...and the mirror image: the rule is real, the report is not.
    swapped = api_client.post(
        f"/api/v1/validation-reports/{warn.rule_id}/results/{report_id}/acknowledge",
        json={"justification": "the two path parameters, exchanged"},
        headers=actuary,
    )
    assert swapped.status_code == 404, swapped.text


@pytest.mark.req("FR-46")
def test_an_analyst_is_refused_by_the_route(
    api_client: TestClient, workspace_id, principal, grant, database
) -> None:
    """FR-46 puts this with an actuary. An analyst who could acknowledge could clear
    the way to `validated` alone, which is the whole control."""
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    warn = _warn()
    report_id = asyncio.get_event_loop().run_until_complete(
        _stored_report(database, workspace_id, principal, warn)
    )
    refused = api_client.post(
        f"/api/v1/validation-reports/{report_id}/results/{warn.rule_id}/acknowledge",
        json={"justification": "I am not an actuary"},
        headers=_headers(principal.id, workspace_id),
    )
    assert refused.status_code == 403, refused.text


@pytest.mark.req("FR-47")
def test_a_justification_is_mandatory_and_a_second_acknowledgement_is_refused(
    api_client: TestClient, workspace_id, principal, actuary, database
) -> None:
    """FR-47: one acknowledgement per `(report, rule)`, with a reason.

    A blank justification is the one a hurried user would send, so the route must refuse
    it rather than storing an empty string that reads as a recorded decision.
    """
    warn = _warn()
    report_id = asyncio.get_event_loop().run_until_complete(
        _stored_report(database, workspace_id, principal, warn)
    )
    url = f"/api/v1/validation-reports/{report_id}/results/{warn.rule_id}/acknowledge"

    blank = api_client.post(url, json={"justification": "   "}, headers=actuary)
    assert blank.status_code == 422, blank.text

    first = api_client.post(
        url, json={"justification": "Reviewed with reserving."}, headers=actuary
    )
    assert first.status_code == 201, first.text

    again = api_client.post(url, json={"justification": "Reviewed again."}, headers=actuary)
    assert again.status_code == 409, again.text
    assert again.json()["code"] == "ACKNOWLEDGEMENT_ALREADY_RECORDED"
