"""The demo command's refusals and its seed handshake (FR-408).

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


@pytest.mark.req("FR-408")
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


@pytest.mark.req("FR-408")
@pytest.mark.parametrize("environment", ["local", "dev", "", "  LOCAL  "])
def test_the_demo_runs_where_development_identity_does(environment: str) -> None:
    """The negative of the above: if it refused here it would refuse everywhere."""
    demo_script.check_environment({"GIP_ENVIRONMENT": environment})


@pytest.mark.req("FR-398")
def test_the_demo_env_points_the_browser_at_the_local_provider() -> None:
    """The one-command demo starts the auth profile and sets the OIDC variables.

    Without the issuer, audience and JWKS the API has nothing to verify against, and
    without the client id the browser login fails at the first redirect — the
    `deploy/README.md` gap, which resurfaced at Phase 1b UAT when the client id was
    omitted. The test pins all four so a removal is a deliberate act, not a silent
    regression.
    """
    env = demo_script.demo_env()
    assert env["GIP_OIDC_ISSUER"] == "http://localhost:8080/realms/gi-pricing"
    assert env["GIP_OIDC_CLIENT_ID"] == "gi-pricing-frontend"
    assert env["GIP_OIDC_AUDIENCE"] == "gi-pricing-api"
    assert env["GIP_OIDC_JWKS_URL"] == (
        "http://localhost:8080/realms/gi-pricing/protocol/openid-connect/certs"
    )


@pytest.mark.req("FR-408")
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


@pytest.mark.req("FR-408")
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


@pytest.mark.req("FR-408")
def test_waiting_for_a_server_accepts_any_answer_at_all() -> None:
    """A 401 proves the server is up as surely as a 200 does.

    The API's own readiness is checked against `/demo/guide`, which requires a credential —
    waiting for a 200 there would hang until the timeout on a perfectly healthy server.
    """
    with pytest.raises(demo_script.DemoRefusedError) as timed_out:
        # Port 1 is reserved and nothing listens on it.
        demo_script.wait_for("http://localhost:1/", step="nothing", timeout=1.0)
    assert "did not answer" in str(timed_out.value)


@pytest.mark.req("FR-408")
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


def _effective_demo_source() -> str:
    """`demo`'s source with `prepare_world`'s body in place of its call: the seed, the record and
    the two pre-flights moved there (SL-1711) so the compose run shares them, and the source-order
    tests below assert the order of the flow `demo` still runs."""
    import inspect

    call = "    record = prepare_world(rows=rows, skip_seed=skip_seed, env=env)\n"
    world = inspect.getsource(demo_script.prepare_world)
    body = world.split('"""', 2)[2].split("\n", 1)[1]
    body = body.replace("    return record\n", "")
    source = inspect.getsource(demo_script.demo)
    assert call in source
    return source.replace(call, body)


@pytest.mark.req("FR-50")
def test_the_rule_set_pre_flight_runs_after_the_seed_record_and_before_the_api_starts() -> None:
    """RL-1407 condition 2 (Acceptance 26): on every path, `--skip-seed` included.

    The orchestration is not run, as above; the source order is what is asserted. The
    pre-flight reads the database, so it cannot precede the migrations step, and it must
    precede the API command so a workspace with an unrunnable rule set is refused before
    anything is served.
    """
    source = _effective_demo_source()
    step = '"pre-flight: the demo workspace\'s rule sets are runnable"'
    assert "check-rule-sets-runnable.py" in source
    assert step in source
    record = source.index("record = read_seed_record()")
    pre_flight = source.index("check-rule-sets-runnable.py")
    api = source.index('"uvicorn"')
    assert record < pre_flight < api
    assert source.index('"migrations"') < pre_flight
    # Not inside the `if not skip_seed:` block: the seed is skipped on `--skip-seed`.
    assert source.index("if not skip_seed:") < record
    assert source[record:pre_flight].count("if not skip_seed") == 0


# -- SL-1527: the seed-record pre-flight, the refusal, and the journey (PL-1544 Tasks 5; DP-b1) --


def _load_script(name: str, filename: str):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).resolve().parents[2] / "scripts" / filename
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.req("FR-408")
async def test_the_seed_record_pre_flight_refuses_a_workspace_the_database_lost(database) -> None:  # type: ignore[no-untyped-def]
    """FD-1494 limb 1 (PL-1544 Acceptance 7 (i)): the record's workspace row is absent, so the
    check exits 1 naming the record and saying to re-run the seed without --skip-seed. Red first:
    the script did not exist, and on the base tree this path printed the rule-set script's
    "the seed did not finish" instead."""
    import io

    from model_schema import new_uuid7

    check = _load_script("gi_check_seed_record", "check-seed-record.py")
    out, err = io.StringIO(), io.StringIO()
    code = await check.check(database, new_uuid7(), new_uuid7(), out=out, err=err)
    assert code == 1
    assert "examples/fremtpl2/data/last-seed.json" in err.getvalue()
    assert "without --skip-seed" in err.getvalue()
    assert out.getvalue() == ""


@pytest.mark.req("FR-408")
async def test_the_seed_record_pre_flight_refuses_an_analyst_who_is_not_a_member(database) -> None:  # type: ignore[no-untyped-def]
    """Acceptance 7 (ii): the workspace is present and the analyst is not a member of it; and
    the negative, so the check cannot pass by always refusing: a member passes."""
    import io

    from backend.tests.conftest_db import seed_as_owner

    from app.platform import workspaces
    from model_schema import new_uuid7

    check = _load_script("gi_check_seed_record", "check-seed-record.py")
    workspace_id, member_id, stranger_id = new_uuid7(), new_uuid7(), new_uuid7()

    # `ensure_member` has no application caller: only the SEED runs as the owner. The
    # pre-flight under test (`check.check(database, ...)`) stays on the application session.
    async def seed(session) -> None:  # type: ignore[no-untyped-def]
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        await workspaces.ensure_member(
            session,
            workspace_id=workspace_id,
            user_id=member_id,
            issuer="http://localhost:8080/realms/gi-pricing",
            subject=f"sub-{member_id.hex[-12:]}",
        )

    await seed_as_owner(seed)
    out, err = io.StringIO(), io.StringIO()
    assert await check.check(database, workspace_id, stranger_id, out=out, err=err) == 1
    assert "not a member" in err.getvalue()
    assert "last-seed.json" in err.getvalue()
    out, err = io.StringIO(), io.StringIO()
    assert await check.check(database, workspace_id, member_id, out=out, err=err) == 0
    assert "seed record holds" in out.getvalue()


@pytest.mark.req("FR-408")
def test_the_seed_record_pre_flight_runs_before_the_rule_set_pre_flight() -> None:
    """Acceptance 7: it runs on every path (not inside `if not skip_seed`), right after the
    record is read and BEFORE `check-rule-sets-runnable.py`, which for an absent workspace takes
    its zero branch and prints the wrong message."""
    source = _effective_demo_source()
    record = source.index("record = read_seed_record()")
    seed_record = source.index("check-seed-record.py")
    rule_sets = source.index("check-rule-sets-runnable.py")
    assert record < seed_record < rule_sets
    assert source[record:seed_record].count("if not skip_seed") == 0


@pytest.mark.req("FR-408")
def test_postcondition_http_error_is_a_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    """FD-1494 limb 2 (Acceptance 11): the `/api/v1/models` call answers 403 and the check
    raises `DemoRefusedError` naming the status, the record's workspace id and the record's path,
    and `main()` returns 1. Red first: `urllib.error.HTTPError: HTTP Error 403` escaped, because
    `main` catches only `DemoRefusedError` and `KeyboardInterrupt`."""
    import io
    import sys
    import urllib.error
    import urllib.request

    def refuse(request, timeout=None):  # type: ignore[no-untyped-def]
        raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", {}, io.BytesIO(b""))  # type: ignore[arg-type]

    monkeypatch.setattr(urllib.request, "urlopen", refuse)
    record = {"workspace_id": "w-1", "analyst_id": "p-1"}
    with pytest.raises(demo_script.DemoRefusedError) as refusal:
        demo_script._verify_journey_postconditions(record, {})
    text = str(refusal.value)
    assert "403" in text
    assert "w-1" in text
    assert "last-seed.json" in text

    def demo_that_verifies(**_kwargs: object) -> int:
        demo_script._verify_journey_postconditions(record, {})
        return 0

    monkeypatch.setattr(demo_script, "demo", demo_that_verifies)
    monkeypatch.setattr(sys, "argv", ["demo.py"])
    assert demo_script.main() == 1


@pytest.mark.req("FR-408")
def test_the_journey_flag_names_one_journey_and_defaults_to_none() -> None:
    """DP-b1 (a): `--journey wf-699` is an option of the one command and is off by default
    (every Phase 1 demo would otherwise pay for the whole journey). SL-1711 adds `wf-701` and
    `--target`, whose default is the local API."""
    assert demo_script.JOURNEYS == ("wf-699", "wf-701")
    parser = demo_script.build_parser()
    assert parser.parse_args([]).journey is None
    assert parser.parse_args([]).target == "local"
    assert parser.parse_args(["--journey", "wf-699"]).journey == "wf-699"
    assert parser.parse_args(["--journey", "wf-701", "--target", "compose"]).target == "compose"
    with pytest.raises(SystemExit):
        parser.parse_args(["--journey", "wf-701", "--target", "elsewhere"])
    with pytest.raises(SystemExit):
        parser.parse_args(["--journey", "wf-700"])


@pytest.mark.req("FR-408")
def test_the_journey_runs_with_a_worker_after_the_postconditions_and_before_the_frontend() -> None:
    """G2's wiring (RL-1521; the lead's and maintainer's Option A for the worker): the journey
    starts a Celery worker and the outbox relay (`beat`) before its first call, because the API
    only writes an outbox row and with no worker the first 202 Job never completes. Order: the
    API's postconditions, then the worker and beat, then the journey, then the frontend, then
    the served-page check. Red first: none of these existed."""
    import inspect

    source = inspect.getsource(demo_script.demo)
    post = source.index("_verify_journey_postconditions(record, env)")
    worker = source.index("worker_command()")
    beat = source.index("beat_command()")
    journey = source.index("run_journey(")
    frontend = source.index("frontend_command,")
    served = source.index("check_served_page(")
    assert post < worker < journey
    assert post < beat < journey
    assert journey < frontend < served
    assert demo_script.worker_command()[:5] == [
        "uv",
        "run",
        "celery",
        "-A",
        "app.worker.entrypoint",
    ]
    assert "worker" in demo_script.worker_command()
    command = demo_script.worker_command()
    from app.platform.jobs import DEFAULT_QUEUE_FOR_KIND
    from app.worker.celery_app import RELAY_QUEUE

    expected = {q.value for q in DEFAULT_QUEUE_FOR_KIND.values()} | {RELAY_QUEUE.value}
    consumed = set(command[command.index("--queues") + 1].split(","))
    assert consumed >= expected, f"demo worker misses {sorted(expected - consumed)}"
    assert "beat" in demo_script.beat_command()


@pytest.mark.req("FR-408")
def test_a_journey_failure_exits_non_zero_with_the_step_line(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Acceptance 6: a journey failure reaches `main` as a refusal carrying `<step>: <code>`, and
    the command exits 1 with that line on stderr."""
    import sys

    class FailedError(RuntimeError):
        step, code, status = "C1", "VALIDATION_FAILED", 422

    def failing_journey(_record: dict[str, str]) -> None:
        raise demo_script.DemoRefusedError(demo_script.journey_failure_line(FailedError()))

    def demo_that_runs_the_journey(**_kwargs: object) -> int:
        failing_journey({})
        return 0

    monkeypatch.setattr(demo_script, "demo", demo_that_runs_the_journey)
    monkeypatch.setattr(sys, "argv", ["demo.py", "--journey", "wf-699"])
    assert demo_script.main() == 1
    assert (
        demo_script.journey_failure_line(FailedError())
        == "the WF-699 journey failed at C1: VALIDATION_FAILED (HTTP 422)"
    )


@pytest.mark.req("FR-408")
def test_the_journey_refuses_to_run_without_the_frontend(monkeypatch: pytest.MonkeyPatch) -> None:
    """RL-1521: the command ends with the frontend serving a 200 page. `--journey` with
    `--no-frontend` would run the journey, wait for Ctrl-C and exit 0 with no 200 check, so it is
    refused, before anything is started, with a nonzero exit and a message saying why. Red first:
    on the unfixed command it started the infrastructure instead of refusing."""
    import sys

    with pytest.raises(demo_script.DemoRefusedError) as refusal:
        demo_script.demo(rows=None, skip_seed=True, frontend=False, journey="wf-699")
    assert "--no-frontend" in str(refusal.value)

    monkeypatch.setattr(sys, "argv", ["demo.py", "--journey", "wf-699", "--no-frontend"])
    assert demo_script.main() == 1


@pytest.mark.req("FR-408")
def test_the_journey_refuses_when_pnpm_is_absent() -> None:
    """The same end-state rule when the frontend cannot start: `demo` must not fall back to an
    API-only run for a journey (it would end with no served page). The refusal sits at the place
    the fallback was."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(demo_script.shutil, "which", lambda _name: None)
        with pytest.raises(demo_script.DemoRefusedError) as refusal:
            demo_script.demo(rows=None, skip_seed=True, frontend=True, journey="wf-699")
        assert "pnpm" in str(refusal.value)
        patch.setattr(demo_script.sys, "argv", ["demo.py", "--journey", "wf-699"])
        assert demo_script.main() == 1


@pytest.mark.req("FR-408")
def test_a_wf701_failure_names_its_journey_and_the_step(monkeypatch: pytest.MonkeyPatch) -> None:
    """R8 (PL-1710): with A1's body refused the command exits non-zero with the one line, in the
    form of the WF-699 line, naming WF-701 and the step `A1`. `run_journey` maps the journey
    module's own failure type, so a failure that names another journey cannot slip through."""
    import sys
    import types

    class A1FailedError(RuntimeError):
        step, code, status = "A1", "VALIDATION_FAILED", 422

    def refused(*_args: object, **_kwargs: object) -> None:
        raise A1FailedError

    walker = types.SimpleNamespace(
        JourneyStepFailed=A1FailedError,
        run_wf699_journey=lambda *a, **k: None,
        run_wf701_after=refused,
    )
    monkeypatch.setattr(demo_script, "_load_journey", lambda _name: walker)
    with pytest.raises(demo_script.DemoRefusedError) as refusal:
        demo_script.run_journey({}, "wf-701")
    assert str(refusal.value) == "the WF-701 journey failed at A1: VALIDATION_FAILED (HTTP 422)"

    def demo_that_runs_the_journey(**_kwargs: object) -> int:
        demo_script.run_journey({}, "wf-701")
        return 0

    monkeypatch.setattr(demo_script, "demo", demo_that_runs_the_journey)
    monkeypatch.setattr(sys, "argv", ["demo.py", "--journey", "wf-701"])
    assert demo_script.main() == 1


@pytest.mark.req("FR-408")
def test_the_compose_target_refuses_naming_the_services_that_are_down() -> None:
    """R9 (PL-1710): with the stack down the command refuses before it seeds anything, and the
    message names each missing service. The workers are derived from the routing table, so a
    pool added to it is required here without an edit to this script."""
    from app.platform.jobs import DEFAULT_QUEUE_FOR_KIND

    needed = demo_script.compose_services()
    assert {f"worker-{q.value}" for q in DEFAULT_QUEUE_FOR_KIND.values()} <= needed
    assert {"postgres", "redis", "minio", "lb", "api"} <= needed
    with pytest.raises(demo_script.DemoRefusedError) as refusal:
        demo_script.check_compose_up({})
    message = str(refusal.value)
    for service in sorted(needed - {"api"}):
        assert service in message
    assert "api (x2; 0 running)" in message
    # `api` once is still one replica short: A2 and C4 show a COMMIT set of two.
    one = {name: 1 for name in needed}
    with pytest.raises(demo_script.DemoRefusedError) as short:
        demo_script.check_compose_up(one)
    assert "api (x2; 1 running)" in str(short.value)
    demo_script.check_compose_up({**one, "api": 2})


@pytest.mark.req("FR-408")
def test_the_compose_target_runs_only_the_wf701_journey_and_refuses_before_seeding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(demo_script, "compose_running", dict)
    seeded: list[str] = []
    monkeypatch.setattr(demo_script, "prepare_world", lambda **_k: seeded.append("seed"))
    with pytest.raises(demo_script.DemoRefusedError, match="only `--journey wf-701`"):
        demo_script.demo(
            rows=None, skip_seed=True, frontend=False, journey="wf-699", target="compose"
        )
    with pytest.raises(demo_script.DemoRefusedError, match="Missing"):
        demo_script.demo(
            rows=None, skip_seed=True, frontend=False, journey="wf-701", target="compose"
        )
    assert seeded == []


@pytest.mark.req("FR-408")
def test_compose_command_names_the_shipped_file_when_compose_file_is_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unset `COMPOSE_FILE`: the command passes the shipped file and the `app` profile."""
    monkeypatch.delenv("COMPOSE_FILE", raising=False)
    monkeypatch.delenv("GIP_COMPOSE_PROJECT", raising=False)
    assert demo_script.compose_command("ps") == [
        "docker",
        "compose",
        "-f",
        "deploy/docker-compose.yml",
        "--profile",
        "app",
        "ps",
    ]
    monkeypatch.setenv("GIP_COMPOSE_PROJECT", "other")
    assert demo_script.compose_command("ps")[:4] == ["docker", "compose", "-p", "other"]


@pytest.mark.req("FR-408")
def test_compose_command_leaves_the_file_list_to_compose_when_compose_file_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Set `COMPOSE_FILE` (a ':'-separated list): no `-f`, so every compose call the demo makes,
    the outbox relay's `run` included, reads the same merged files the operator named. A fixed
    `-f` would drop an override file for that one call."""
    monkeypatch.setenv("COMPOSE_FILE", "/stack/docker-compose.yml:/stack/override.yml")
    monkeypatch.delenv("GIP_COMPOSE_PROJECT", raising=False)
    command = demo_script.compose_command("run", "--rm", "-d", "worker-default")
    assert "-f" not in command
    assert command == [
        "docker",
        "compose",
        "--profile",
        "app",
        "run",
        "--rm",
        "-d",
        "worker-default",
    ]


@pytest.mark.req("FR-408")
def test_the_demo_env_keeps_compose_file_for_its_compose_subprocesses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The compose calls run with `demo_env()`; `COMPOSE_FILE` must reach them."""
    monkeypatch.setenv("COMPOSE_FILE", "/stack/docker-compose.yml:/stack/override.yml")
    assert demo_script.demo_env()["COMPOSE_FILE"] == "/stack/docker-compose.yml:/stack/override.yml"
