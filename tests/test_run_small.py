"""`scripts/run-small.sh` takes a pytest node id, and a run that ran no test is an error (#1924).

Each case runs a COPY of the script (its slot, load source and wait substituted, as in
`backend/tests/test_run_small_script.py`) against a tiny temp worktree. A stub `uv` first on
`PATH` stands in for `uv run --directory <wt> pytest ...` and runs the REAL pytest there, so
the node ids, the brackets and pytest's own exit codes are exercised, not assumed. No database,
no service, no real slot. `RUN_SMALL_UNDER_TEST` points the run at another copy of the script
(used to show a case red against the previous script).
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = pathlib.Path(os.environ.get("RUN_SMALL_UNDER_TEST", ROOT / "scripts" / "run-small.sh"))

NOT_A_TEST_FILE, TOO_MANY, OUTSIDE_WORKTREE, NOT_TEST_NAMED = 71, 68, 72, 73
PYTEST_NOT_FOUND, PYTEST_NOTHING_COLLECTED = 4, 5

TEST_SOURCE = """\
import pytest


def test_one():
    pass


def test_two():
    pass


@pytest.mark.parametrize("v", ["a", "b"])
def test_param(v):
    pass


class TestBox:
    def test_inside(self):
        pass
"""


class Env:
    def __init__(self, tmp: pathlib.Path) -> None:
        self.tmp = tmp
        self.wt = tmp / "wt"
        self.wt.mkdir()
        (self.wt / "test_sample.py").write_text(TEST_SOURCE)
        (self.wt / "test_other.py").write_text("def test_o():\n    pass\n")
        (self.wt / "helper.py").write_text("")
        (self.wt / "sub").mkdir()
        (tmp / "slot").write_text("")
        (tmp / "loadavg").write_text("0.50 0.50 0.50 1/100 1\n")
        script = tmp / "run-small.sh"
        patched = SCRIPT.read_text()
        for name, value in (("slot", tmp / "slot"), ("loadavg", tmp / "loadavg"), ("wait_s", 5)):
            patched, n = re.subn(rf"^{name}=.*$", f"{name}={value}", patched, flags=re.M)
            assert n == 1, name
        script.write_text(patched)
        self.script = script
        self.bin = tmp / "bin"
        self.bin.mkdir()
        uv = self.bin / "uv"
        # uv run --directory <wt> pytest <args>  ->  the real pytest, run inside <wt>.
        uv.write_text(
            "#!/bin/bash\n"
            'wt=$3; shift 4; cd "$wt" || exit 99\n'
            f'exec {sys.executable} -m pytest -p no:cacheprovider --rootdir "$wt" "$@"\n'
        )
        uv.chmod(0o755)

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if k != "GIP_GATE_SLOT"}
        env["PATH"] = f"{self.bin}:{env['PATH']}"
        return subprocess.run(
            ["bash", str(self.script), str(self.wt), *args],
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )


@pytest.fixture
def env(tmp_path: pathlib.Path) -> Env:
    return Env(tmp_path)


def test_a_whole_file_runs_every_test_in_it(env: Env) -> None:
    result = env.run("test_sample.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "5 passed" in result.stdout


@pytest.mark.parametrize(
    "node_id",
    [
        "test_sample.py::test_one",
        "test_sample.py::test_param[a]",
        "test_sample.py::TestBox::test_inside",
    ],
)
def test_a_node_id_runs_that_test_only(env: Env, node_id: str) -> None:
    result = env.run(node_id)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 passed" in result.stdout


def test_a_node_id_that_selects_nothing_is_an_error(env: Env) -> None:
    result = env.run("test_sample.py::test_not_there")
    assert result.returncode != 0, "a run of nothing must not be a green"
    assert "NO TEST RAN" in result.stderr
    assert "passed" not in result.stdout


def test_a_bracketed_id_that_selects_nothing_is_an_error(env: Env) -> None:
    result = env.run("test_sample.py::test_param[zzz]")
    assert result.returncode != 0
    assert "NO TEST RAN" in result.stderr


def test_a_file_that_collects_no_test_is_an_error(env: Env) -> None:
    (env.wt / "test_empty.py").write_text("x = 1\n")
    result = env.run("test_empty.py")
    assert result.returncode == PYTEST_NOTHING_COLLECTED
    assert "NO TEST RAN" in result.stderr


def test_the_exit_code_of_a_missing_node_id_is_pytests_own(env: Env) -> None:
    assert env.run("test_sample.py::test_not_there").returncode == PYTEST_NOT_FOUND


def test_a_failing_test_keeps_its_own_exit_code_and_no_no_test_line(env: Env) -> None:
    (env.wt / "test_bad.py").write_text("def test_bad():\n    assert 1 == 2\n")
    result = env.run("test_bad.py::test_bad")
    assert result.returncode == 1
    assert "NO TEST RAN" not in result.stderr


def test_up_to_three_node_ids_run_together(env: Env) -> None:
    result = env.run("test_sample.py::test_one", "test_sample.py::test_two", "test_other.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "3 passed" in result.stdout


def test_four_node_ids_are_refused(env: Env) -> None:
    ids = [f"test_sample.py::test_{n}" for n in ("one", "two", "one", "two")]
    result = env.run(*ids)
    assert result.returncode == TOO_MANY
    assert "passed" not in result.stdout


def test_a_node_id_whose_file_is_missing_is_refused(env: Env) -> None:
    result = env.run("test_nope.py::test_one")
    assert result.returncode == NOT_A_TEST_FILE
    assert "not a test file" in result.stderr


@pytest.mark.parametrize("arg", ["sub", "sub::test_one", "test_sample.py::", "::test_one"])
def test_a_directory_or_an_empty_part_is_refused(env: Env, arg: str) -> None:
    assert env.run(arg).returncode == NOT_A_TEST_FILE


@pytest.mark.parametrize("args", [("-k", "one"), ("-x", "test_sample.py"), ("-k=one",)])
def test_an_option_is_refused(env: Env, args: tuple[str, ...]) -> None:
    result = env.run(*args)
    assert result.returncode == NOT_A_TEST_FILE
    assert "passed" not in result.stdout


def test_a_node_id_of_a_non_test_file_is_refused(env: Env) -> None:
    result = env.run("helper.py::test_one")
    assert result.returncode == NOT_TEST_NAMED


def test_a_node_id_outside_the_worktree_is_refused(env: Env) -> None:
    outside = env.tmp / "test_outside.py"
    outside.write_text("def test_o():\n    pass\n")
    result = env.run(f"{outside}::test_o")
    assert result.returncode == OUTSIDE_WORKTREE
    assert "passed" not in result.stdout
