"""`scripts/reconcile-approvals.py`: the output lines and the exit codes (`06` FR-2163).

The first half needs no database. The subprocess runs against a migrated database are named
at the foot and run in the slice's database window.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
from types import ModuleType
from uuid import uuid4

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "reconcile-approvals.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("reconcile_approvals_script", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _report(chain: str = "intact", mismatches: tuple[object, ...] = ()) -> object:
    from app.platform.reconcile import WorkspaceReport

    return WorkspaceReport(uuid4(), chain, 3, 1, 1, mismatches)  # type: ignore[arg-type]


def _mismatch(legacy: bool = False) -> object:
    from app.platform.reconcile import Mismatch

    return Mismatch("R1", "model:m@1", "no approved request", legacy)


@pytest.mark.req("FR-2163")
def test_a_clean_run_exits_zero_with_one_line_per_workspace_and_a_summary() -> None:
    script = _load()
    lines, code = script.render([_report(), _report()])
    assert code == 0
    assert len(lines) == 3
    assert json.loads(lines[-1]) == {
        "summary": True,
        "workspaces": 2,
        "chain_broken": 0,
        "workspaces_with_mismatches": 0,
    }


@pytest.mark.req("FR-2163")
def test_a_mismatch_exits_one_and_prints_its_rule_ref_and_detail() -> None:
    script = _load()
    lines, code = script.render([_report(mismatches=(_mismatch(),))])
    assert code == 1
    (entry,) = json.loads(lines[0])["mismatches"]
    assert entry == {
        "rule": "R1",
        "ref": "model:m@1",
        "detail": "no approved request",
        "legacy": False,
    }


@pytest.mark.req("FR-2163")
def test_a_legacy_mismatch_is_marked_and_the_exit_stays_one() -> None:
    script = _load()
    lines, code = script.render([_report(mismatches=(_mismatch(legacy=True),))])
    assert code == 1
    assert json.loads(lines[0])["mismatches"][0]["legacy"] is True


@pytest.mark.req("FR-2163")
def test_a_broken_chain_exits_two_and_outranks_a_mismatch_elsewhere() -> None:
    script = _load()
    broken = _report("broken")
    lines, code = script.render([_report(mismatches=(_mismatch(),)), broken])
    assert code == 2
    assert json.loads(lines[1])["mismatches"] == []
    assert json.loads(lines[-1])["chain_broken"] == 1


@pytest.mark.req("FR-2163")
def test_a_run_that_cannot_complete_exits_two(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    script = _load()

    async def _fails() -> list[object]:
        raise ConnectionRefusedError("no database")

    monkeypatch.setattr(script, "_run", _fails)
    assert script.main() == 2
    assert "ConnectionRefusedError" in capsys.readouterr().err


# -- DB-backed: run in the slice's database window ----------------------------------------------


def _test_database_url() -> str:
    """The application's DSN for the test database, from the suite's own helper (imported by
    name so the type checker does not follow it into the whole test fixture module)."""
    module = importlib.import_module("backend.tests.conftest_db")
    return str(module.test_database_url())


def _run_script_against_the_test_database() -> tuple[int, list[dict[str, object]], str]:
    import os
    import subprocess
    import sys

    env = {**os.environ, "GIP_DATABASE_URL": _test_database_url()}
    done = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    return done.returncode, [json.loads(line) for line in done.stdout.splitlines()], done.stderr


def _chain_heads() -> dict[str, tuple[int, str]]:
    """Per workspace: the chain head, read through the application's connection."""
    import asyncio

    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    async def _read() -> dict[str, tuple[int, str]]:
        engine = create_async_engine(_test_database_url())
        try:
            async with engine.connect() as conn:
                rows = await conn.execute(
                    text(
                        "SELECT DISTINCT ON (workspace_id) workspace_id, sequence, event_hash "
                        "FROM audit_events ORDER BY workspace_id, sequence DESC"
                    )
                )
                return {str(r[0]): (r[1], r[2]) for r in rows}
        finally:
            await engine.dispose()

    return asyncio.run(_read())


def test_script_db_a_migrated_demo_database_exits_zero_or_one_and_prints_json() -> None:
    code, lines, stderr = _run_script_against_the_test_database()
    assert code in (0, 1), stderr
    *workspaces, summary = lines
    assert summary["summary"] is True
    assert summary["workspaces"] == len(workspaces)
    for line in workspaces:
        assert line["chain"] == "intact"
        assert set(line) >= {"workspace_id", "events_verified", "mismatches"}
    expected = 1 if any(line["mismatches"] for line in workspaces) else 0
    assert code == expected


def test_script_db_writes_nothing_the_audit_chain_head_is_unchanged() -> None:
    before = _chain_heads()
    code, _lines, stderr = _run_script_against_the_test_database()
    assert code in (0, 1), stderr
    assert _chain_heads() == before
