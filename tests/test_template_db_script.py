"""`deploy/setup-template-db.sh` (FD-1218): mode, fail-closed drop, and the emptiness
and revision check — exercised against stub `docker` and `uv` executables, so no
PostgreSQL is needed and each failure is provoked deliberately.
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "deploy" / "setup-template-db.sh"

_STUB_DOCKER = """#!/usr/bin/env bash
echo "$*" >> "$STUB_LOG"
[ -n "${STUB_FAIL_ON:-}" ] && [[ "$*" == *"$STUB_FAIL_ON"* ]] && exit 1
[[ "$*" == *query_to_xml* ]] && printf '%s' "${STUB_ROWS:-}"
[[ "$*" == *"FROM alembic_version"* ]] && echo "${STUB_REV:-}"
exit 0
"""
_STUB_UV = """#!/usr/bin/env bash
echo "uv $*" >> "$STUB_LOG"
[[ "$*" == *"alembic heads"* ]] && echo "${STUB_HEAD:-} (head)"
exit 0
"""


def _run(
    tmp_path: Path, *args: str, **env: str
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    for name, body in (("docker", _STUB_DOCKER), ("uv", _STUB_UV)):
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    log = tmp_path / "calls.log"
    log.write_text("")
    full_env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "STUB_LOG": str(log),
        **env,
    }
    done = subprocess.run(
        [str(SCRIPT), *args], env=full_env, capture_output=True, text=True, check=False
    )
    return done, log.read_text().splitlines()


def test_the_script_is_committed_executable() -> None:
    assert SCRIPT.stat().st_mode & stat.S_IXUSR
    tracked = subprocess.run(
        ["git", "ls-files", "-s", str(SCRIPT)],
        cwd=SCRIPT.parent,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    if tracked:  # a source tarball has no index to ask
        assert tracked.startswith("100755"), tracked


def test_a_failed_drop_stops_the_script_before_createdb(tmp_path: Path) -> None:
    done, calls = _run(tmp_path, STUB_FAIL_ON="dropdb")
    assert done.returncode != 0
    assert any("dropdb" in c for c in calls)
    assert not any("createdb" in c for c in calls)
    assert not any(c.startswith("uv ") for c in calls)


def test_no_command_in_the_script_swallows_its_failure() -> None:
    code = [ln for ln in SCRIPT.read_text().splitlines() if not ln.lstrip().startswith("#")]
    assert not [ln for ln in code if "|| true" in ln or "|| :" in ln]


def test_check_fails_on_a_template_that_holds_rows(tmp_path: Path) -> None:
    done, _ = _run(tmp_path, "--check", STUB_ROWS="users\n", STUB_REV="a1", STUB_HEAD="a1")
    assert done.returncode != 0
    assert "holds rows in: users" in done.stderr


def test_check_fails_on_a_template_behind_head(tmp_path: Path) -> None:
    done, _ = _run(tmp_path, "--check", STUB_ROWS="", STUB_REV="a1", STUB_HEAD="b2")
    assert done.returncode != 0
    assert "at a1" in done.stderr
    assert "head is b2" in done.stderr


def test_check_passes_on_an_empty_template_at_head(tmp_path: Path) -> None:
    done, _ = _run(tmp_path, "--check", STUB_ROWS="", STUB_REV="a1", STUB_HEAD="a1")
    assert done.returncode == 0, done.stderr
    assert "OK" in done.stdout


def test_check_fails_when_the_template_cannot_be_read(tmp_path: Path) -> None:
    done, _ = _run(tmp_path, "--check", STUB_FAIL_ON="query_to_xml")
    assert done.returncode != 0


@pytest.mark.parametrize("head", ["", "a1\nb2"])
def test_check_fails_without_exactly_one_head(tmp_path: Path, head: str) -> None:
    done, _ = _run(tmp_path, "--check", STUB_ROWS="", STUB_REV="a1", STUB_HEAD=head)
    assert done.returncode != 0
