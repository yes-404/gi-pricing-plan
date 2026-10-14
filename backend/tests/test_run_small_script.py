"""`scripts/run-small.sh`: the only sanctioned small targeted test run beside a held code gate.

RL-1626 (a)-(e), the maintainer's (by delegation) entry "2026-10-14 11:34:58 BST" in `to-lead.md`:
each refusal below is proven by running the script on bad input and asserting its exit code and
message. Nothing here takes the real `/tmp/slots/small-test` flock or a gate slot: `RUN_SMALL_SLOT`
points the flock at a file under `tmp_path`, `RUN_SMALL_LOADAVG` at a fake `/proc/loadavg`, and a
stub `uv` first on `PATH` stands in for the real pytest run. Those two variables exist for these
tests only; `RUN_SMALL_WAIT` bounds the held-flock test to one second.
"""

from __future__ import annotations

import fcntl
import os
import pathlib
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run-small.sh"

# Exit codes the script documents (flock's own -E code is 75, kept clear of pytest's 0-5).
USAGE, SLOT_SET, LOAD, ALEMBIC, TOO_MANY, NOT_A_TEST_FILE, BUSY = 64, 65, 66, 67, 68, 71, 75


class Env:
    def __init__(self, tmp: pathlib.Path) -> None:
        self.tmp = tmp
        self.wt = tmp / "wt"
        self.wt.mkdir()
        for name in ("test_a.py", "test_b.py", "test_c.py", "test_d.py"):
            (self.wt / name).write_text("def test_x():\n    pass\n")
        (self.wt / "tests").mkdir()
        self.slot = tmp / "small-test"
        self.loadavg = tmp / "loadavg"
        self.loadavg.write_text("0.50 0.50 0.50 1/100 1\n")
        self.record = tmp / "record"
        self.bin = tmp / "bin"
        self.bin.mkdir()
        uv = self.bin / "uv"
        uv.write_text(
            "#!/bin/bash\n"
            '{ echo "args: $*"; echo "slot: ${GIP_GATE_SLOT:-}";'
            ' echo "nice: $(cut -d" " -f19 /proc/self/stat)";'
            ' echo "io: $(ionice -p $$)"; } > "$RUN_SMALL_RECORD"\n'
            "exit ${STUB_RC:-0}\n"
        )
        uv.chmod(0o755)

    def run(self, *args: str, **extra: str) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if k != "GIP_GATE_SLOT"}
        env.update(
            PATH=f"{self.bin}:{env['PATH']}",
            RUN_SMALL_SLOT=str(self.slot),
            RUN_SMALL_LOADAVG=str(self.loadavg),
            RUN_SMALL_WAIT="1",
            RUN_SMALL_RECORD=str(self.record),
        )
        env.update(extra)
        return subprocess.run(
            ["bash", str(SCRIPT), *args], env=env, capture_output=True, text=True, timeout=60
        )


@pytest.fixture
def env(tmp_path: pathlib.Path) -> Env:
    return Env(tmp_path)


def _refused(env: Env, result: subprocess.CompletedProcess[str], rc: int, message: str) -> None:
    assert result.returncode == rc, result.stderr
    assert message in result.stderr
    assert not env.record.exists(), "a refused run must not reach the test command"


def test_no_args_is_refused(env: Env) -> None:
    _refused(env, env.run(), USAGE, "usage:")


def test_worktree_without_test_files_is_refused(env: Env) -> None:
    _refused(env, env.run(str(env.wt)), USAGE, "usage:")


def test_a_directory_is_refused(env: Env) -> None:
    _refused(env, env.run(str(env.wt), "tests"), NOT_A_TEST_FILE, "not a test file: tests")


def test_a_missing_file_is_refused(env: Env) -> None:
    _refused(
        env, env.run(str(env.wt), "test_nope.py"), NOT_A_TEST_FILE, "not a test file: test_nope.py"
    )


def test_a_pytest_option_is_refused(env: Env) -> None:
    _refused(env, env.run(str(env.wt), "-k", "x"), NOT_A_TEST_FILE, "not a test file: -k")


def test_four_files_are_refused(env: Env) -> None:
    result = env.run(str(env.wt), "test_a.py", "test_b.py", "test_c.py", "test_d.py")
    _refused(env, result, TOO_MANY, "at most 3 test files")


def test_three_files_are_accepted(env: Env) -> None:
    result = env.run(str(env.wt), "test_a.py", "test_b.py", "test_c.py")
    assert result.returncode == 0, result.stderr
    assert "pytest -q test_a.py test_b.py test_c.py" in env.record.read_text()


@pytest.mark.parametrize("arg", ["alembic", "Alembic.ini", "upgrade_alembic_head.py"])
def test_a_command_line_naming_alembic_is_refused(env: Env, arg: str) -> None:
    (env.wt / arg).write_text("")
    _refused(env, env.run(str(env.wt), arg), ALEMBIC, "alembic")


def test_alembic_in_the_worktree_path_is_refused(env: Env) -> None:
    wt = env.tmp / "alembic-wt"
    wt.mkdir()
    (wt / "test_a.py").write_text("")
    _refused(env, env.run(str(wt), "test_a.py"), ALEMBIC, "alembic")


def test_gate_slot_set_by_the_caller_is_refused(env: Env) -> None:
    _refused(
        env,
        env.run(str(env.wt), "test_a.py", GIP_GATE_SLOT="/tmp/slots/gate-1"),
        SLOT_SET,
        "GIP_GATE_SLOT is set",
    )


def test_load_at_or_above_six_is_refused_not_waited_on(env: Env) -> None:
    env.loadavg.write_text("6.00 1.00 1.00 1/100 1\n")
    _refused(env, env.run(str(env.wt), "test_a.py"), LOAD, "load1 6.00 is not below 6")


def test_load_just_below_six_runs(env: Env) -> None:
    env.loadavg.write_text("5.99 1.00 1.00 1/100 1\n")
    assert env.run(str(env.wt), "test_a.py").returncode == 0


@contextmanager
def _held(path: pathlib.Path) -> Iterator[None]:
    with path.open("w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def test_a_held_small_test_flock_is_refused_after_the_wait(env: Env) -> None:
    with _held(env.slot):
        result = env.run(str(env.wt), "test_a.py")
    _refused(env, result, BUSY, "")


@pytest.mark.parametrize("rc", [0, 1, 2, 5])
def test_exit_code_is_the_inner_pytests(env: Env, rc: int) -> None:
    assert env.run(str(env.wt), "test_a.py", STUB_RC=str(rc)).returncode == rc


def test_command_runs_niced_idle_io_and_inside_the_flock_with_its_slot(env: Env) -> None:
    assert env.run(str(env.wt), "test_a.py").returncode == 0
    record = env.record.read_text()
    assert f"args: run --directory {env.wt} pytest -q test_a.py" in record
    assert f"slot: {env.slot}" in record
    assert "nice: 19" in record
    assert "io: idle" in record


def test_source_has_no_handover_path_no_flock_double_dash_and_no_alembic_command() -> None:
    source = SCRIPT.read_text()
    assert "handover" not in source
    assert "flock --" not in source
    assert "alembic upgrade" not in source
