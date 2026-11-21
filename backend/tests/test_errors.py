"""Every non-2xx response is one shape, with a code and a trace id (`00` §5.3)."""

from __future__ import annotations

import logging
import warnings

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator

from app.errors import (
    PLATFORM_ERROR_CODES,
    RATING_ERROR_CODES,
    PlatformError,
    build_location,
    install_error_handlers,
)
from app.main import create_app
from app.observability.middleware import TraceMiddleware
from app.observability.trace import TRACE_ID_PATTERN
from model_schema import GlmSpec, JobErrorLocation, new_uuid7
from model_schema.input_free import InputFreeError

PROBLEM = "application/problem+json"


class _Body(BaseModel):
    count: int


@pytest.fixture
def failing_client(settings) -> TestClient:
    """An app with routes that fail in each of the four ways the handlers cover."""
    app = create_app(settings)

    @app.post("/_test/validate")
    async def _validate(body: _Body) -> dict[str, int]:
        return {"count": body.count}

    @app.get("/_test/platform-error")
    async def _platform_error() -> None:
        raise PlatformError(
            "JOB_NOT_CANCELLABLE",
            "Job is not cancellable",
            409,
            "Job has already finished.",
        )

    @app.get("/_test/boom")
    async def _boom() -> None:
        raise RuntimeError("password=hunter2 leaked into the exception message")

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.req("FR-450")
def test_platform_error_renders_as_problem_json(failing_client: TestClient) -> None:
    response = failing_client.get("/_test/platform-error")
    assert response.status_code == 409
    assert response.headers["content-type"].startswith(PROBLEM)
    body = response.json()
    assert body["code"] == "JOB_NOT_CANCELLABLE"
    assert body["status"] == 409
    assert body["instance"] == "/_test/platform-error"
    assert body["type"].endswith("/job-not-cancellable")


@pytest.mark.req("FR-445")
def test_every_problem_carries_a_trace_id(failing_client: TestClient) -> None:
    """R4: a support conversation starts with an identifier, not a screenshot."""
    for path in ("/_test/platform-error", "/_test/boom", "/no-such-route"):
        body = failing_client.get(path).json()
        assert TRACE_ID_PATTERN.match(body["trace_id"]), path


@pytest.mark.req("FR-450")
def test_framework_404_is_a_problem_not_a_bare_detail(failing_client: TestClient) -> None:
    """Negative: Starlette's default `{"detail": ...}` would be a second error shape."""
    response = failing_client.get("/no-such-route")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith(PROBLEM)
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.req("FR-403")
def test_validation_failure_names_the_field(failing_client: TestClient) -> None:
    """A deterministic rejection must be renderable against the form that caused it."""
    response = failing_client.post("/_test/validate", json={"count": "not-an-int"})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_FAILED"
    assert body["errors"][0]["field"] == "count"
    assert body["errors"][0]["code"]


@pytest.mark.req("NFR-532")
def test_unexpected_error_does_not_leak_the_exception_message(
    failing_client: TestClient,
) -> None:
    """R3: an exception string can carry a credential. The trace id is the way in."""
    response = failing_client.get("/_test/boom")
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "INTERNAL_ERROR"
    assert "hunter2" not in response.text
    assert "password" not in response.text
    assert body["trace_id"]


@pytest.mark.req("FR-403")
def test_to_problem_leaves_a_refusals_location_out_of_the_problem_body() -> None:
    """#1917: `location` is for the Job worker only; a request's problem response is unchanged."""
    from model_schema.jobs import JobErrorLocation

    located = PlatformError(
        "VALIDATION_FAILED",
        "Nope",
        422,
        location=JobErrorLocation(step_id="s_rp", field="inputs.age"),
    )
    plain = PlatformError("VALIDATION_FAILED", "Nope", 422)
    body = located.to_problem().model_dump(mode="json")
    assert "location" not in body
    assert "s_rp" not in str(body)
    assert body == plain.to_problem().model_dump(mode="json")


@pytest.mark.req("FR-450")
def test_unknown_error_code_is_refused_at_construction() -> None:
    """Negative: an unenumerated code reaches a client as something it cannot branch on."""
    with pytest.raises(ValueError, match="unknown error code"):
        PlatformError("NOT_A_REAL_CODE", "Nope", 400)


@pytest.mark.req("FR-450")
def test_spec_error_codes_are_all_constructible() -> None:
    """The registry must match 07 §5.1 — a code in the spec but not here cannot be raised."""
    for code in PLATFORM_ERROR_CODES:
        assert PlatformError(code, "title", 400).code == code


@pytest.mark.req("FR-445")
def test_problem_response_survives_middleware_ordering() -> None:
    """Trace binding is outermost, so even a handler-less app problem carries the id."""
    app = FastAPI()
    app.add_middleware(TraceMiddleware)
    install_error_handlers(app)
    body = TestClient(app, raise_server_exceptions=False).get("/nope").json()
    assert TRACE_ID_PATTERN.match(body["trace_id"])


@pytest.mark.req("FR-450")
def test_no_live_rating_version_is_registered_at_409() -> None:
    """RL-880's refusal code, registered before the branch that raises it.

    `POST /api/v1/score` with no `options.rating_version_ref` answers *"this platform
    has no live Rating Version to score you against"* rather than guessing one, and
    `live` is a property of a Deployment (FR-238), which is WK-674's. 409 because this
    backend already answers "the artifact is not in a state that permits this" at 409
    (`platform/datasets.py`, `jobs.py`, `rating_versions.py`, `approvals.py`), and the
    caller's operator resolves it by deploying a version and retrying.

    `PlatformError.__init__` refuses an unenumerated code, so the route's branch cannot
    be written before this registration exists — the mechanism that stops RL-880
    being half-applied.
    """
    error = PlatformError(
        "NO_LIVE_RATING_VERSION",
        "No live Rating Version",
        409,
        "Supply options.rating_version_ref.",
    )
    assert error.code == "NO_LIVE_RATING_VERSION"
    assert error.status_code == 409


@pytest.mark.req("FR-260")
def test_golden_quote_mismatch_is_registered() -> None:
    """`03` §5.1 declares this code; Slice 2's promotion refusal raises it.

    Asserted by literal name, never by iterating `RATING_ERROR_CODES`: a test that iterates
    the collection it checks passes for every member by construction.
    """
    assert "GOLDEN_QUOTE_MISMATCH" in RATING_ERROR_CODES
    error = PlatformError("GOLDEN_QUOTE_MISMATCH", "Golden quote mismatch", 409)
    assert error.code == "GOLDEN_QUOTE_MISMATCH"


@pytest.mark.req("FR-227")
def test_monetary_float_refused_is_withdrawn() -> None:
    """`RL-1958` item 1 withdrew the code; `03` keeps it only as a tombstone.

    Asserted by literal name, never by iterating `RATING_ERROR_CODES`. A raise of the
    withdrawn code fails the same way as any other unknown code.
    """
    assert "MONETARY_FLOAT_REFUSED" not in RATING_ERROR_CODES
    with pytest.raises(ValueError, match="unknown error code"):
        PlatformError("MONETARY_FLOAT_REFUSED", "Monetary float refused", 422)


_SENTINEL = "SENTINEL-422-input-5e0c2b91"


class _Validated(BaseModel):
    family: str

    @field_validator("family")
    @classmethod
    def _refuse(cls, value: str) -> str:
        if value == "authored":
            raise InputFreeError("an authored, input-free message")
        raise ValueError(f"unacceptable value {value}")


@pytest.fixture
def validating_client(settings) -> TestClient:
    app = create_app(settings)

    @app.post("/_test/authored")
    async def _authored(body: _Validated) -> None:
        return None

    @app.post("/_test/glm")
    async def _glm(body: GlmSpec) -> None:
        return None

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.req("NFR-499")
def test_an_input_free_validator_message_reaches_the_422(validating_client: TestClient) -> None:
    response = validating_client.post("/_test/authored", json={"family": "authored"})
    assert response.status_code == 422
    (error,) = response.json()["errors"]
    assert error["code"] == "VALUE_ERROR"
    assert error["message"] == "Value error, an authored, input-free message"


@pytest.mark.req("NFR-499")
def test_an_interpolating_validator_message_does_not_reach_the_422(
    validating_client: TestClient,
) -> None:
    response = validating_client.post("/_test/authored", json={"family": _SENTINEL})
    assert response.status_code == 422
    assert _SENTINEL not in response.text
    (error,) = response.json()["errors"]
    assert error["field"] == "family"
    assert error["message"] == "The value is not valid (VALUE_ERROR)."


@pytest.mark.req("NFR-499")
def test_a_model_schema_authored_refusal_keeps_its_guidance(validating_client: TestClient) -> None:
    body = {
        "model_family_slug": "motor-ad-frequency",
        "dataset_version_id": str(new_uuid7()),
        "response_column": "claim_count",
    }  # family defaults to poisson and offset to kind "none"
    response = validating_client.post("/_test/glm", json=body)
    assert response.status_code == 422
    messages = [e["message"] for e in response.json()["errors"]]
    assert any("a Poisson model must declare an offset" in m for m in messages), messages


@pytest.mark.req("FR-403")
def test_a_fixed_text_type_keeps_its_message(failing_client: TestClient) -> None:
    response = failing_client.post("/_test/validate", json={"count": "not-an-int"})
    (error,) = response.json()["errors"]
    assert error["code"] == "INT_PARSING"
    assert error["message"] == (
        "Input should be a valid integer, unable to parse string as an integer"
    )


@pytest.mark.req("NFR-499")
def test_a_malformed_json_body_renders_the_authored_text_and_no_input(
    validating_client: TestClient,
) -> None:
    """DP-5's extension: FastAPI reports a malformed body as `json_invalid`, whose own text is
    the parser's detail; the authored text replaces it and the submitted bytes never appear."""
    response = validating_client.post(
        "/_test/authored",
        content=b'{"family": "' + _SENTINEL.encode(),
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 422
    assert _SENTINEL not in response.text
    (error,) = response.json()["errors"]
    assert error["code"] == "JSON_INVALID"
    assert error["message"] == "The request body is not valid JSON."


@pytest.mark.req("FR-403")
@pytest.mark.parametrize(
    "value",
    [
        {"step_id": "base premium"},
        {"step_id": "s" * 129},
        {"interaction": "VehAge & DrivAge"},
        {"feature": "Veh Age"},
        {"key": "Driver Age"},
        {"objective": "reg:tweedie"},
        {"factor": "vehicle_group_rated"},
    ],
)
def test_a_refusal_built_from_a_mapping_keeps_a_location_that_fits_its_source_field(
    value: dict[str, str],
) -> None:
    """Review of #1930, point 3: each is a valid value of its source field."""
    from model_schema.jobs import JobErrorLocation

    refusal = PlatformError("VALIDATION_FAILED", "Nope", 422, location=value)
    assert refusal.location == JobErrorLocation(**value)


@pytest.mark.req("FR-403")
@pytest.mark.parametrize(
    "bad",
    [{}, {"nope": "x"}, {"step_id": 42}, {"ref": "not-a-reference"}, {"peril": "has a space"}],
)
def test_a_location_that_cannot_be_built_never_costs_the_refusal_its_code(
    bad: dict[str, object],
) -> None:
    """A location is an aid: when it cannot be built the refusal is raised without one, under
    its own code, never as a `ValidationError` from the raise site."""
    refusal = PlatformError("VALIDATION_FAILED", "Nope", 422, "Nope.", location=bad)  # type: ignore[arg-type]
    assert (refusal.code, refusal.status_code, refusal.location) == ("VALIDATION_FAILED", 422, None)


_LOCATION_SENTINEL = "SENTINEL-submitted-value-3c9e"


@pytest.mark.req("FR-403")
@pytest.mark.parametrize(
    ("bad", "key"),
    [
        ({"ref": _LOCATION_SENTINEL}, "ref"),
        ({"peril": _LOCATION_SENTINEL}, "peril"),
        ({"step_id": "s_rp", "structure": _LOCATION_SENTINEL}, "structure"),
        ({"undeclared": _LOCATION_SENTINEL}, "undeclared:1"),
        ({_LOCATION_SENTINEL: "x", "step_id": "s_rp"}, "undeclared:1"),
        (
            {_LOCATION_SENTINEL: "x", _LOCATION_SENTINEL + "2": "y", "ref": "bad"},
            "ref,undeclared:2",
        ),
        ({}, "(none)"),
    ],
)
def test_a_dropped_location_is_logged_with_the_code_and_the_key_and_never_the_value(
    bad: dict[str, str], key: str, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.WARNING, logger="app.errors"):
        refusal = PlatformError("VALIDATION_FAILED", "Nope", 422, location=bad)

    assert refusal.location is None
    lines = [r.getMessage() for r in caplog.records if r.name == "app.errors"]
    assert len(lines) == 1, lines
    assert "VALIDATION_FAILED" in lines[0]
    assert f"keys={key}" in lines[0]
    assert _LOCATION_SENTINEL not in caplog.text


@pytest.mark.req("FR-403")
def test_a_location_that_builds_is_not_logged(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="app.errors"):
        PlatformError("VALIDATION_FAILED", "Nope", 422, location={"step_id": "base premium"})
    assert [r for r in caplog.records if r.name == "app.errors"] == []


#: Instances that were never validated: `model_construct` skips every validator, and
#: `model_copy(update=...)` does not re-run them, so each can hold what the model refuses.
_UNVALIDATED_INSTANCES = {
    "model_construct, 300 characters": lambda: JobErrorLocation.model_construct(
        step_id=_LOCATION_SENTINEL + "x" * 300
    ),
    "model_construct, a control character": lambda: JobErrorLocation.model_construct(
        step_id=_LOCATION_SENTINEL + "\nx"
    ),
    "model_copy(update=), 300 characters": lambda: JobErrorLocation(step_id="s").model_copy(
        update={"step_id": _LOCATION_SENTINEL + "x" * 300}
    ),
}


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize("shape", sorted(_UNVALIDATED_INSTANCES))
def test_build_location_checks_an_instance_like_a_mapping(
    shape: str, caplog: pytest.LogCaptureFixture
) -> None:
    """An instance that was never validated is held to the same bound and rule: it is dropped
    with the one warning naming the key and never the value, and the caller gets None."""
    instance = _UNVALIDATED_INSTANCES[shape]()
    with caplog.at_level(logging.WARNING, logger="app.errors"):
        built = build_location("VALIDATION_FAILED", instance)

    assert built is None
    lines = [r.getMessage() for r in caplog.records if r.name == "app.errors"]
    assert len(lines) == 1, lines
    assert "VALIDATION_FAILED" in lines[0]
    assert "keys=step_id" in lines[0]
    assert _LOCATION_SENTINEL not in caplog.text


@pytest.mark.req("NFR-499")
def test_build_location_never_raises_on_an_instance_with_a_badly_typed_field(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The sink must never raise: dumping an unvalidated instance whose field has the wrong type
    makes pydantic warn, and under warnings-as-errors that warning would be exactly the escape
    this check exists to close. The instance is dropped with the one warning, and None returned."""
    instance = JobErrorLocation.model_construct(step_id=42)
    with (
        caplog.at_level(logging.WARNING, logger="app.errors"),
        warnings.catch_warnings(),  # scoped to the call: a fixture's own warnings stay warnings
    ):
        warnings.simplefilter("error")
        built = build_location("VALIDATION_FAILED", instance)

    assert built is None
    lines = [r.getMessage() for r in caplog.records if r.name == "app.errors"]
    assert len(lines) == 1, lines
    assert "keys=step_id" in lines[0]


@pytest.mark.req("NFR-499")
def test_build_location_keeps_a_valid_instance_even_when_it_was_never_validated(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="app.errors"):
        built = build_location(
            "VALIDATION_FAILED", JobErrorLocation.model_construct(step_id="base premium")
        )
    assert built == JobErrorLocation(step_id="base premium")
    assert [r for r in caplog.records if r.name == "app.errors"] == []
