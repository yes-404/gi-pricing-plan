"""`scripts/bench-rating.py --http` serves the application the login DSN (FD-2001).

FD-1729 made `app.main` refuse to start as an owner or a superuser (FR-44), so the harness
must hand the server under test a least-privilege DSN (`--serve-dsn`) and keep `--dsn`, the
owner, for its own seeding and in-process fetch timing. These tests are DB-free: everything
`_run_http_sweep` calls before `_serve` is a recorder, and `_serve` raises a sentinel, so no
server starts.

The script is loaded from a copy under `tmp_path`: `_run_http_sweep` removes and recreates
`<script dir>/../.bench-logs`, which for the script in place is the worktree's own directory.
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import shutil
import sys
from types import ModuleType
from typing import Any

import pytest

pytestmark = pytest.mark.req("NFR-489")

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "bench-rating.py"
OWNER = "postgresql+asyncpg://owner-sentinel@localhost/db"
LOGIN = "postgresql+asyncpg://login-sentinel@localhost/db"
ENV_VAR = "GIP_TEST_APP_DATABASE_URL"


class _StopError(Exception):
    """Raised by a replaced function to end the run at a known point."""


@pytest.fixture
def bench(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> ModuleType:
    copy = tmp_path / "scripts" / "bench-rating.py"
    copy.parent.mkdir()
    shutil.copy(SCRIPT, copy)
    spec = importlib.util.spec_from_file_location("bench_rating_serve_dsn_under_test", copy)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # `@dataclass` under `from __future__ import annotations` looks the module up by name.
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_http_sweep_serves_the_login_dsn_and_seeds_with_the_owner_dsn(
    bench: ModuleType,
) -> None:
    seeded: list[str] = []
    fetched: list[str] = []
    served: list[str] = []

    async def _serialisable(**_kw: Any) -> object:
        return object()

    async def _seed(_bundle: object, *, dsn: str, **_kw: Any) -> tuple[str, str]:
        seeded.append(dsn)
        return "ws", "key"

    async def _measure_fetch(*, dsn: str, **_kw: Any) -> object:
        fetched.append(dsn)
        return object()

    def _serve(*, dsn: str, **_kw: Any) -> Any:
        served.append(dsn)
        raise _StopError

    bench._serialisable = _serialisable
    bench._seed = _seed
    bench._measure_fetch = _measure_fetch
    bench._report = lambda *_a, **_kw: None
    bench._serve = _serve

    args = argparse.Namespace(
        rates="25",
        rung_seconds=1,
        port=8099,
        dsn=OWNER,
        serve_dsn=LOGIN,
        bucket="b",
        workers=1,
        expr_steps=1,
        rounds=1,
        rows=1,
        speedup=2.1,
    )
    with pytest.raises(_StopError):
        bench._run_http_sweep(args)

    assert served == [LOGIN], served
    assert seeded == [OWNER], seeded
    assert fetched, "_measure_fetch was never called"
    assert set(fetched) == {OWNER}, fetched


def _parse(
    bench: ModuleType, monkeypatch: pytest.MonkeyPatch, argv: list[str]
) -> argparse.Namespace:
    """Run `main()` to the first statement after parsing, and return the namespace."""
    seen: list[argparse.Namespace] = []
    original = argparse.ArgumentParser.parse_args

    def _record(self: argparse.ArgumentParser, *a: Any, **kw: Any) -> argparse.Namespace:
        ns = original(self, *a, **kw)
        seen.append(ns)
        return ns

    def _stop() -> str:
        raise _StopError

    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", _record)
    monkeypatch.setattr(sys, "argv", ["bench-rating.py", *argv])
    bench.machine = _stop  # the first call `main` makes after parsing
    with pytest.raises(_StopError):
        bench.main()
    return seen[0]


def test_serve_dsn_option_parses(bench: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_VAR, raising=False)
    ns = _parse(bench, monkeypatch, ["--http", "--dsn", OWNER, "--serve-dsn", LOGIN])
    assert ns.serve_dsn == LOGIN
    assert ns.dsn == OWNER


def test_serve_dsn_defaults_to_the_suites_app_dsn_variable(
    bench: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(ENV_VAR, LOGIN)
    ns = _parse(bench, monkeypatch, ["--http", "--dsn", OWNER])
    assert ns.serve_dsn == LOGIN


def test_http_without_a_serve_dsn_is_refused_at_parse_time(
    bench: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv(ENV_VAR, raising=False)
    monkeypatch.setattr(sys, "argv", ["bench-rating.py", "--http", "--dsn", OWNER])
    bench.machine = lambda: (_ for _ in ()).throw(_StopError())

    with pytest.raises(SystemExit) as exit_info:
        bench.main()

    assert exit_info.value.code == 2
    err = capsys.readouterr().err
    assert "--serve-dsn" in err, err
    assert "FD-1729" in err, err


def test_a_run_without_http_needs_no_serve_dsn(
    bench: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_VAR, raising=False)
    ns = _parse(bench, monkeypatch, [])
    assert not ns.http
