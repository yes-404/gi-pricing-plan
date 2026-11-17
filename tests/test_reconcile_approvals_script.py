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


# DB-backed (run in the database window; named, not run here):
#   test_script_db_a_migrated_demo_database_exits_zero_or_one_and_prints_json
#   test_script_db_writes_nothing_the_audit_chain_head_is_unchanged
