"""`POST /api/v1/score` — the real-time scoring endpoint (W11 Slice 2 Task 2B).

**Two groups, and the split is deliberate.** The refusal and RBAC cases exercise the real
stack end to end, because everything they test happens *before* a bundle is resolved. The
boundary cases below replace `_compiled_for` instead: what they test is what the route does
with what `score_one` hands back, and compiling a real bundle to reach that point would put
the engine, the blob store and the compile job inside the blast radius of a test about
error mapping. A failure there should name the boundary, not the fixture.

Version resolution itself — ref to row to blob key to bytes — is Ruling 37's, and is
covered by the happy-path and degraded-read tests, which do use a real compiled version.

The caller is a **Service Account**, not a user. `Permission.SCORE_EXECUTE` is granted by
no builtin role, deliberately (FR-GOV-6, asserted in `test_rbac.py`), so a `grant("analyst")`
principal reaches 403 at the permission dependency and never gets far enough to be refused
for the reason these tests are about.
"""

from __future__ import annotations

from typing import Any

import pytest
import pytest_asyncio
from backend.tests.test_bundle_slot import _compiled
from fastapi.testclient import TestClient

from app.api import score as score_module
from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Settings
from app.main import create_app
from model_schema import ArtifactRef, LadderRung, ScoringResult

SCORE_URL = "/api/v1/score"
SCORED_REF = "rating_version:fremtpl2-demo@1"


@pytest.fixture
def client(api_settings: Settings) -> Any:
    """`raise_server_exceptions=False` so a 500 is observable as a response.

    Task 2B step 5c asserts that a deliberately undesigned `NotImplementedError` reaches
    the caller as a 500 rather than being dressed as a typed per-quote error, and that is
    only assertable if the client does not re-raise.
    """
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def admin_headers(workspace_id: Any, principal: Any, grant: Any) -> dict[str, str]:
    """A user who may create Service Accounts — not one who may score."""
    await grant("admin")
    return {
        DEV_PRINCIPAL_HEADER: str(principal.id),
        "Workspace-Id": str(workspace_id),
    }


@pytest.fixture
def scoring_headers(
    client: TestClient, admin_headers: dict[str, str], workspace_id: Any
) -> dict[str, str]:
    """A `uat` Service Account holding `score:execute`, presented as an API key.

    `uat` rather than `prod` on purpose: FR-RATE-35's two restrictions — approved-only and
    a rewritten `what_if` purpose — sit inside its own `prod` clause, and Ruling 14 clause 3
    rules that W11 imposes neither. Scoring a `draft` version by explicit reference is the
    "what-if and testing" the requirement permits.
    """
    created = client.post(
        "/api/v1/service-accounts",
        json={
            "slug": "quote-engine-uat",
            "environments": ["uat"],
            "permissions": ["score:execute"],
        },
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    return {
        "X-API-Key": created.json()["key"],
        "Workspace-Id": str(workspace_id),
    }


def _quote(options: dict[str, Any] | None = None, *, omit_options: bool = False) -> dict[str, Any]:
    """A `QuoteContext` body. `options` is optional and nullable, and stays that way.

    Ruling 14 clause 1: a required `rating_version_ref` would put the code above its own
    specification — `03` §4.4's own example carries `"rating_version_ref": null`.
    """
    body: dict[str, Any] = {
        "purpose": "new_business",
        "quoted_at": "2026-08-30T09:00:00Z",
        "effective_date": "2026-09-01",
        "inputs": {"premium_in": 1000},
    }
    if not omit_options:
        body["options"] = options
    return body


@pytest.mark.req("FR-RATE-34")
def test_a_quote_naming_no_rating_version_is_refused(
    client: TestClient, scoring_headers: dict[str, str]
) -> None:
    """FR-RATE-34's **refusal limb only** — not the requirement.

    FR-RATE-34 has three limbs and this marker evidences one of them. The default path
    resolves *"the Rating Version currently live in the target environment"*, and `live` is
    a property of a Deployment (FR-RATE-23), which is W14's. Rather than guess a version,
    the platform refuses, and Ruling 14 makes that branch permanent rather than a stub:
    after W14 it is what an environment holding no Deployment answers.

    The delivered limb is evidenced by the happy-path test; the *"p99 < 50 ms server-side"*
    limb the requirement also carries is established by neither, and is Task 2D's.
    """
    response = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": None}), headers=scoring_headers
    )

    assert response.status_code == 409, response.text
    assert response.json()["code"] == "NO_LIVE_RATING_VERSION"


@pytest.mark.req("FR-RATE-34")
def test_a_quote_with_no_options_at_all_is_refused(
    client: TestClient, scoring_headers: dict[str, str]
) -> None:
    """Same refusal through the other door: `options` absent, not merely null.

    `options` is itself optional, so a caller can omit it entirely. A route that reached
    for `ctx.options.rating_version_ref` without checking would raise `AttributeError` here
    and answer 500 — the same refusal must come out of both shapes.
    """
    response = client.post(SCORE_URL, json=_quote(omit_options=True), headers=scoring_headers)

    assert response.status_code == 409, response.text
    assert response.json()["code"] == "NO_LIVE_RATING_VERSION"


@pytest.mark.req("FR-RATE-34")
def test_the_refusal_is_the_routes_own_not_score_ones(
    client: TestClient, scoring_headers: dict[str, str]
) -> None:
    """The discriminator: **which** code comes back, not merely that it is a refusal.

    `score_one` also refuses a `None` ref — with `INPUT_CONTRACT_VIOLATION`, its own
    input-contract error. A route that simply forwarded to `score_one` and mapped whatever
    it raised would satisfy a status-only assertion while answering with the wrong code,
    and the caller's operator would be told their input was malformed when in fact the
    platform has no live version to score against. Ruling 14 puts the refusal in the route,
    before `score_one` is reached.
    """
    body = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": None}), headers=scoring_headers
    ).json()

    assert body["code"] == "NO_LIVE_RATING_VERSION"
    assert body["code"] != "INPUT_CONTRACT_VIOLATION"


# --------------------------------------------------------------------------------------
# NFR-RATE-11 — scoped credentials. Two of Ruling 18's three cases are refusals that land
# before the route, so they are testable now; the third (a permitted account scoring
# successfully) needs a resolved bundle and lands with the happy path.
# --------------------------------------------------------------------------------------


@pytest.fixture
def unpermissioned_headers(
    client: TestClient, admin_headers: dict[str, str], workspace_id: Any
) -> dict[str, str]:
    """A Service Account holding `score:batch` and **not** `score:execute`.

    An empty permission list is refused at creation (a Service Account must hold at least
    one), and the sibling permission is the sharper case regardless: it proves the route
    checks for *this* permission rather than merely for a permissioned caller. `score:batch`
    is Slice 3's and must not open Slice 2's endpoint.
    """
    created = client.post(
        "/api/v1/service-accounts",
        json={
            "slug": "batch-only-uat",
            "environments": ["uat"],
            "permissions": ["score:batch"],
        },
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    return {"X-API-Key": created.json()["key"], "Workspace-Id": str(workspace_id)}


@pytest.mark.req("NFR-RATE-11")
def test_an_account_without_score_execute_is_refused(
    client: TestClient, unpermissioned_headers: dict[str, str]
) -> None:
    """Ruling 18: Task 2B *checks* the permission and grants nothing.

    `SCORE_EXECUTE` is held by no builtin role (FR-GOV-6), so the only way to hold it is an
    explicit Service Account grant. An account without it must be refused at the permission
    dependency, before any scoring work.
    """
    response = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": None}), headers=unpermissioned_headers
    )

    assert response.status_code == 403, response.text


@pytest.mark.req("NFR-RATE-11")
def test_a_key_relabelled_to_another_environment_is_refused_at_authentication(
    client: TestClient, admin_headers: dict[str, str], workspace_id: Any
) -> None:
    """FR-PLAT-30: the environment in a key is a label, not an authorisation.

    A key is `gip_{environment}_{prefix}_{secret}` and only the *secret* is hashed, so the
    environment segment is caller-supplied text that can be rewritten while the credential
    still verifies. This relabels a `uat` key to `prod`, keeping prefix and secret intact —
    the account is found and the secret matches, and the request must still be refused
    because `prod` is not among the environments the account was granted.

    **"Refused at authentication, before the route" means before the route *handler*, not
    before *routing*.** Authentication runs as a dependency of a matched route, so until
    `/api/v1/score` is registered this request 404s and `authenticate_api_key` is never
    reached — the check cannot fire on a path that does not exist. Worth stating because the
    distinction is invisible until you run it: the refusal genuinely does precede the
    permission check and the handler, but it does not precede routing.

    The inversion below is what stops this passing for the wrong reason — the same key,
    unmodified, must *not* be refused at authentication.
    """
    created = client.post(
        "/api/v1/service-accounts",
        json={
            "slug": "quote-engine-uat-scoped",
            "environments": ["uat"],
            "permissions": ["score:execute"],
        },
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    key = created.json()["key"]
    namespace, environment, prefix, secret = key.split("_", 3)
    assert environment == "uat", key

    relabelled = "_".join([namespace, "prod", prefix, secret])
    refused = client.post(
        SCORE_URL,
        json=_quote({"rating_version_ref": None}),
        headers={"X-API-Key": relabelled, "Workspace-Id": str(workspace_id)},
    )

    assert refused.status_code == 401, refused.text
    assert refused.json()["code"] == "ENVIRONMENT_SCOPE_DENIED"

    # Inversion: the untampered key is *not* refused at authentication. It fails later and
    # for another reason — 404 until the route exists, and the 409 refusal after — but it
    # must never be 401, or the assertion above would be passing on the credential rather
    # than on the environment label.
    intact = client.post(
        SCORE_URL,
        json=_quote({"rating_version_ref": None}),
        headers={"X-API-Key": key, "Workspace-Id": str(workspace_id)},
    )
    assert intact.status_code != 401, intact.text


# --------------------------------------------------------------------------------------
# The error boundary and the response shape. These isolate the route from version
# resolution on purpose: what is under test is what the route does with what `score_one`
# hands back, so `_compiled_for` is replaced with a bundle rather than one being compiled.
# --------------------------------------------------------------------------------------


@pytest.fixture
def served(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Resolution replaced by a held bundle, so only the boundary is under test."""

    async def _compiled_for(*_args: Any, **_kwargs: Any) -> Any:
        return _compiled("hash-scored")

    monkeypatch.setattr(score_module, "_compiled_for", _compiled_for)


def _scored(**overrides: Any) -> ScoringResult:
    body: dict[str, Any] = {
        "outcome": "quoted",
        "rating_version_ref": ArtifactRef.model_validate(SCORED_REF),
        "bundle_hash": "sha256:" + "a" * 64,
        "premium_ladder": [
            LadderRung(rung="risk_premium", value_minor=10_000),
            LadderRung(rung="payable_premium", value_minor=12_000),
        ],
        "outputs": {"payable_premium_minor": 12_000},
        "decline_reasons": [],
        "trace": None,
        "timing_ms": {"total": 1.5},
    }
    body.update(overrides)
    return ScoringResult(**body)


@pytest.mark.req("NFR-RATE-13")
def test_the_result_is_returned_without_outbound_validation(
    client: TestClient,
    scoring_headers: dict[str, str],
    served: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ruling 17's acceptance test, and the one that discriminates the implementations.

    A `ScoringResult` built with `model_construct` holds values that violate its own
    declared types — no validation ran to stop them. The route must emit those bytes
    verbatim with a 200. **A route carrying a Pydantic return annotation or a
    `response_model=` answers 500 here**, because FastAPI would validate on the way out,
    which is exactly what NFR-RATE-13 forbids: validate inbound, never outbound.
    """
    malformed = ScoringResult.model_construct(
        outcome="quoted",
        rating_version_ref=ArtifactRef.model_validate(SCORED_REF),
        bundle_hash=12345,  # declared `str`
        premium_ladder="not-a-list",  # declared `list[LadderRung]`
        outputs={"payable_premium_minor": 12_000},
        decline_reasons=[],
        trace=None,
        timing_ms={"total": "not-a-float"},  # declared `dict[str, float]`
    )

    async def _score_one(*_args: Any, **_kwargs: Any) -> ScoringResult:
        return malformed

    monkeypatch.setattr(score_module, "score_one", _score_one)
    response = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": SCORED_REF}), headers=scoring_headers
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["bundle_hash"] == 12345
    assert body["premium_ladder"] == "not-a-list"
    assert body["timing_ms"] == {"total": "not-a-float"}


@pytest.mark.req("FR-RATE-38")
@pytest.mark.parametrize(
    "code",
    [
        "INPUT_CONTRACT_VIOLATION",
        "RATE_TABLE_MISS",
        "REFERENCE_LOOKUP_MISS",
        "MODEL_CALL_FAILED",
    ],
)
def test_each_per_quote_code_maps_to_its_own_problem(
    client: TestClient,
    scoring_headers: dict[str, str],
    served: Any,
    monkeypatch: pytest.MonkeyPatch,
    code: str,
) -> None:
    """FR-RATE-38: each per-quote failure comes back as its own typed problem.

    `pricing-core` cannot import `PlatformError` (ADR-0001), so it raises a code-named bare
    `ValueError` and the mapping is the boundary's. The message half is prose that will
    change, so the route parses the code off the front — this test asserts the code that
    comes back, never the message.
    """

    async def _score_one(*_args: Any, **_kwargs: Any) -> ScoringResult:
        raise ValueError(f"{code}: something specific and prose-like happened")

    monkeypatch.setattr(score_module, "score_one", _score_one)
    response = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": SCORED_REF}), headers=scoring_headers
    )

    assert response.status_code == 422, response.text
    assert response.json()["code"] == code


@pytest.mark.req("FR-RATE-39")
def test_a_decline_is_a_two_hundred_with_a_populated_ladder(
    client: TestClient,
    scoring_headers: dict[str, str],
    served: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FR-RATE-39: a decline is an answer, not a failure.

    **This is the test that stops the mapping above being written too widely.** A boundary
    that caught every `ValueError` and problem-ified it would pass all four cases above and
    fail here — a declined quote is a priced, reasoned refusal with a populated ladder, and
    turning it into an HTTP error would tell a broker their request was malformed when the
    platform simply will not quote them.
    """
    declined = _scored(outcome="declined", decline_reasons=["driver_age below minimum"])

    async def _score_one(*_args: Any, **_kwargs: Any) -> ScoringResult:
        return declined

    monkeypatch.setattr(score_module, "score_one", _score_one)
    response = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": SCORED_REF}), headers=scoring_headers
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["outcome"] == "declined"
    assert body["decline_reasons"] == ["driver_age below minimum"]
    assert len(body["premium_ladder"]) == 2


@pytest.mark.req("FR-RATE-38")
def test_an_undesigned_failure_stays_a_five_hundred(
    client: TestClient,
    scoring_headers: dict[str, str],
    served: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The one thing the mapping must **not** do.

    A firing `on_violation="error"` constraint raises a plain `NotImplementedError` —
    deliberately undesigned in Task 1.4, and not a platform error code. Dressing it as a
    typed per-quote problem would hide an unfinished design behind a 422 that looks
    considered, so it must surface as a 500 and stay visible to whoever finishes it.

    A bare `ValueError` whose prefix is not a registered code takes the same path, which is
    why the route returns `None` from its mapper rather than guessing the nearest code.
    """

    async def _score_one(*_args: Any, **_kwargs: Any) -> ScoringResult:
        raise NotImplementedError("on_violation='error' is undesigned")

    monkeypatch.setattr(score_module, "score_one", _score_one)
    response = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": SCORED_REF}), headers=scoring_headers
    )

    assert response.status_code == 500, response.text


@pytest.mark.req("FR-RATE-38")
def test_an_unregistered_code_is_not_invented_into_a_problem(
    client: TestClient,
    scoring_headers: dict[str, str],
    served: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative for the parser: a code-shaped prefix that is not a registered per-quote
    code must not be mapped. Otherwise the boundary would mint error codes from whatever
    `pricing-core` happened to put before the first colon."""

    async def _score_one(*_args: Any, **_kwargs: Any) -> ScoringResult:
        raise ValueError("SOMETHING_ELSE: not one of the four")

    monkeypatch.setattr(score_module, "score_one", _score_one)
    response = client.post(
        SCORE_URL, json=_quote({"rating_version_ref": SCORED_REF}), headers=scoring_headers
    )

    assert response.status_code == 500, response.text
