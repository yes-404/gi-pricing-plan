"""The demo command's refusals and its seed handshake (FR-PLAT-53).

The orchestration itself — compose, uvicorn, vite — is not unit-testable and is not worth
faking; it is proven by running it. What *is* worth testing is everything that decides
whether it runs at all, because those are the parts that would otherwise be discovered in
the one environment they must never run in.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "demo_script", Path(__file__).resolve().parents[2] / "scripts" / "demo.py"
)
assert _SPEC is not None
assert _SPEC.loader is not None
demo_script = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(demo_script)


@pytest.mark.req("FR-PLAT-53")
@pytest.mark.parametrize("environment", ["prod", "staging", "PROD", "production"])
def test_the_demo_refuses_outside_local_and_dev(environment: str) -> None:
    """Before anything is started, not after.

    A stack brought up and then rejected is a worse message than one never brought up —
    and the whole path hangs off the one refusal that already exists rather than a second
    flag that can be left on.
    """
    with pytest.raises(demo_script.DemoRefusedError) as refusal:
        demo_script.check_environment({"GIP_ENVIRONMENT": environment})
    assert "development identity" in str(refusal.value)


@pytest.mark.req("FR-PLAT-53")
@pytest.mark.parametrize("environment", ["local", "dev", "", "  LOCAL  "])
def test_the_demo_runs_where_development_identity_does(environment: str) -> None:
    """The negative of the above: if it refused here it would refuse everywhere."""
    demo_script.check_environment({"GIP_ENVIRONMENT": environment})


@pytest.mark.req("FR-PLAT-58")
def test_the_demo_env_points_the_browser_at_the_local_provider() -> None:
    """The one-command demo starts the auth profile and sets the OIDC variables.

    Without these three the API has no issuer to verify against and the browser login
    fails at the first redirect — the gap `deploy/README.md` recorded until W6b. The test
    pins the values so a removal is a deliberate act, not a silent regression.
    """
    env = demo_script.demo_env()
    assert env["GIP_OIDC_ISSUER"] == "http://localhost:8080/realms/gi-pricing"
    assert env["GIP_OIDC_AUDIENCE"] == "gi-pricing-api"
    assert env["GIP_OIDC_JWKS_URL"] == (
        "http://localhost:8080/realms/gi-pricing/protocol/openid-connect/certs"
    )


@pytest.mark.req("FR-PLAT-53")
def test_the_seed_record_is_read_rather_than_scraped_from_output(tmp_path: Path) -> None:
    """The seed writes ids to a file; the demo reads that file.

    Parsing them out of the seed's printed lines would make its print format a contract
    between two programs — the least visible kind there is, and the first thing a tidy-up
    of the output would break.
    """
    record = tmp_path / "last-seed.json"
    record.write_text(
        json.dumps({"workspace_id": "w-1", "analyst_id": "p-1", "actuary_id": "p-2"}),
        encoding="utf-8",
    )
    assert demo_script.read_seed_record(record)["analyst_id"] == "p-1"


@pytest.mark.req("FR-PLAT-53")
def test_a_missing_or_partial_seed_record_says_which_command_writes_it(
    tmp_path: Path,
) -> None:
    with pytest.raises(demo_script.DemoRefusedError) as missing:
        demo_script.read_seed_record(tmp_path / "absent.json")
    assert "seed.py" in str(missing.value)

    partial = tmp_path / "partial.json"
    partial.write_text(json.dumps({"actuary_id": "p-2"}), encoding="utf-8")
    with pytest.raises(demo_script.DemoRefusedError) as incomplete:
        demo_script.read_seed_record(partial)
    assert "workspace_id" in str(incomplete.value)
    assert "analyst_id" in str(incomplete.value)


@pytest.mark.req("FR-PLAT-53")
def test_waiting_for_a_server_accepts_any_answer_at_all() -> None:
    """A 401 proves the server is up as surely as a 200 does.

    The API's own readiness is checked against `/demo/guide`, which requires a credential —
    waiting for a 200 there would hang until the timeout on a perfectly healthy server.
    """
    with pytest.raises(demo_script.DemoRefusedError) as timed_out:
        # Port 1 is reserved and nothing listens on it.
        demo_script.wait_for("http://localhost:1/", step="nothing", timeout=1.0)
    assert "did not answer" in str(timed_out.value)


@pytest.mark.req("FR-PLAT-53")
def test_a_held_port_is_refused_before_anything_starts() -> None:
    """The command reports only servers it started.

    `wait_for` returns on any answer, so with a stale server on the port it printed
    "Open http://localhost:5173/demo" while its own children were dead of
    `[Errno 98] address already in use` — sending the reader to a different server with a
    different identity. Checked before starting rather than after, because polling the
    child races its own death: `pnpm` outlives the `vite` it spawned by a moment.
    """
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as holder:
        holder.bind(("127.0.0.1", 0))
        holder.listen(1)
        port = holder.getsockname()[1]

        with pytest.raises(demo_script.DemoRefusedError) as refusal:
            demo_script.require_free(port, step="the API")
        assert "already in use" in str(refusal.value)
        assert "did not start" in str(refusal.value)

    # ...and the negative: the same port, once released, is not refused.
    demo_script.require_free(port, step="the API")
