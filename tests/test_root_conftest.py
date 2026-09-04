"""Tests for the repository-root `conftest.py` — W37-6's thread-cap defaults and
gate-slot enforcement for a bare `uv run pytest -q` (`.claude/skills/dev-commands/
SKILL.md`'s gate block, found necessary after the wrapped form was typed wrong three
times in one day).

Fast, deterministic unit coverage of the actual decision logic
(`_is_bare_full_run`, the `pytest_configure`/`pytest_unconfigure` wiring, and the real
`flock` mechanics against a scratch slot directory) — never a full two-subprocess
concurrency race, which would make every future gate pay for a proof this module's own
logic already makes redundant. The concurrency proof itself (two bare sessions, the
second shown waiting; a spawned process carrying exactly 4 native-runtime threads; the
per-worktree-database refusal) was run live and is not repeated here as an automated
test — see the W37-6 PR description.

No `@pytest.mark.req` marker: this is test-infrastructure correctness, not evidence for
a numbered platform requirement.
"""

from __future__ import annotations

import contextlib
import fcntl
import importlib.util
import os
import sys
import threading
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONFTEST_PATH = ROOT / "conftest.py"

_THREAD_CAP_VARS = (
    "POLARS_MAX_THREADS",
    "RAYON_NUM_THREADS",
    "TOKIO_WORKER_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
)


def _load_fresh(name: str) -> types.ModuleType:
    """A fresh exec of `conftest.py` under a throwaway module name.

    Required because the thread-cap defaults are top-level code that runs once at
    import — reusing pytest's own already-imported copy (`sys.modules["conftest"]`,
    already executed against this session's real environment before any test ran) would
    prove nothing about what a change to the caller's environment produces.
    """
    spec = importlib.util.spec_from_file_location(name, CONFTEST_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _FakeConfig:
    """The two `pytest.Config` surfaces this conftest reads — nothing else — so these
    tests exercise the real decision functions without needing a real `pytest.Config`
    (which `--collect-only`'s own scoped-per-file tests elsewhere in this suite avoid
    building for the identical reason).
    """

    def __init__(self, args: tuple[str, ...], *, collectonly: bool = False) -> None:
        self.invocation_params = types.SimpleNamespace(args=args)
        self._collectonly = collectonly

    def getoption(self, name: str) -> bool:
        if name == "collectonly":
            return self._collectonly
        raise AssertionError(f"unexpected getoption({name!r}) in this fake")


@pytest.fixture(scope="module")
def conftest_module() -> types.ModuleType:
    return _load_fresh("_root_conftest_under_test")


@pytest.fixture(autouse=True)
def _clear_gate_slot_announcement(monkeypatch: pytest.MonkeyPatch) -> None:
    """`GIP_GATE_SLOT` must not leak in from the real session running this suite (this
    session's own gate, if wrapped, would have it set) — every test below decides its own
    announcement state explicitly.
    """
    monkeypatch.delenv("GIP_GATE_SLOT", raising=False)


# ---------------------------------------------------------------------------------------
# 1. Thread caps
# ---------------------------------------------------------------------------------------


def test_thread_caps_default_to_four_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in _THREAD_CAP_VARS:
        monkeypatch.delenv(var, raising=False)
    _load_fresh("_root_conftest_probe_defaults")
    for var in _THREAD_CAP_VARS:
        assert os.environ[var] == "4"


def test_thread_caps_never_override_an_explicit_setting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POLARS_MAX_THREADS", "16")
    _load_fresh("_root_conftest_probe_override")
    assert os.environ["POLARS_MAX_THREADS"] == "16"


# ---------------------------------------------------------------------------------------
# 2. `_is_bare_full_run` — bare vs. targeted, the discriminant everything else hangs off
# ---------------------------------------------------------------------------------------


def test_no_args_at_all_is_bare(conftest_module: types.ModuleType) -> None:
    assert conftest_module._is_bare_full_run(_FakeConfig(())) is True


def test_bare_with_only_the_quiet_flag_is_bare(conftest_module: types.ModuleType) -> None:
    """The real gate command's own shape: `uv run pytest -q`."""
    assert conftest_module._is_bare_full_run(_FakeConfig(("-q",))) is True


def test_an_explicit_path_is_not_bare(conftest_module: types.ModuleType) -> None:
    assert (
        conftest_module._is_bare_full_run(_FakeConfig(("tests/test_doc_id.py",)))
        is False
    )


def test_a_node_id_is_not_bare(conftest_module: types.ModuleType) -> None:
    assert (
        conftest_module._is_bare_full_run(
            _FakeConfig(("tests/test_doc_id.py::test_pad_width_is_five",))
        )
        is False
    )


def test_a_keyword_filter_is_not_bare(conftest_module: types.ModuleType) -> None:
    assert (
        conftest_module._is_bare_full_run(_FakeConfig(("-k", "pad_width"))) is False
    )


def test_a_marker_filter_is_not_bare(conftest_module: types.ModuleType) -> None:
    assert conftest_module._is_bare_full_run(_FakeConfig(("-m", "req"))) is False


def test_an_attached_keyword_filter_form_is_not_bare(
    conftest_module: types.ModuleType,
) -> None:
    assert conftest_module._is_bare_full_run(_FakeConfig(("-kpad_width",))) is False


# ---------------------------------------------------------------------------------------
# 3. `pytest_configure`/`pytest_unconfigure` wiring — the decision, not the flock itself
# ---------------------------------------------------------------------------------------


def test_collect_only_never_acquires_a_slot(
    conftest_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: list[int] = []
    monkeypatch.setattr(
        conftest_module, "_acquire_pytest_gate_slot", lambda: called.append(1)
    )
    conftest_module.pytest_configure(_FakeConfig((), collectonly=True))
    assert called == []


def test_a_targeted_run_never_acquires_a_slot(
    conftest_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: list[int] = []
    monkeypatch.setattr(
        conftest_module, "_acquire_pytest_gate_slot", lambda: called.append(1)
    )
    conftest_module.pytest_configure(_FakeConfig(("tests/test_doc_id.py",)))
    assert called == []


def test_a_bare_run_acquires_exactly_one_slot(
    conftest_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: list[int] = []
    monkeypatch.setattr(
        conftest_module, "_acquire_pytest_gate_slot", lambda: called.append(1)
    )
    conftest_module.pytest_configure(_FakeConfig(("-q",)))
    assert called == [1]


def test_unconfigure_always_releases_regardless_of_configures_decision(
    conftest_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: list[int] = []
    monkeypatch.setattr(
        conftest_module, "_release_pytest_gate_slot", lambda: called.append(1)
    )
    conftest_module.pytest_unconfigure(_FakeConfig(()))
    assert called == [1]


def test_an_announced_slot_is_never_acquired_a_second_time(
    conftest_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The wrapper's own `export GIP_GATE_SLOT=/tmp/slots/gate-$i` (`dev-commands`'s gate
    block, set right after its own `flock` succeeds) must make this hook a no-op even for
    a bare-shaped run — the fix for the deputy's finding against an earlier, separate-
    namespace design: it let three wrapped gates and three unwrapped ones run at once,
    six total, defeating the three-slot budget both were meant to share.
    """
    monkeypatch.setenv("GIP_GATE_SLOT", "/tmp/slots/gate-1")
    called: list[int] = []
    monkeypatch.setattr(
        conftest_module, "_acquire_pytest_gate_slot", lambda: called.append(1)
    )
    conftest_module.pytest_configure(_FakeConfig(("-q",)))
    assert called == []


def test_an_unannounced_bare_run_still_acquires_normally(
    conftest_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The other half of the same proof: with no announcement, a bare run behaves exactly
    as it did before the announcement check existed.
    """
    monkeypatch.delenv("GIP_GATE_SLOT", raising=False)
    called: list[int] = []
    monkeypatch.setattr(
        conftest_module, "_acquire_pytest_gate_slot", lambda: called.append(1)
    )
    conftest_module.pytest_configure(_FakeConfig(("-q",)))
    assert called == [1]


# ---------------------------------------------------------------------------------------
# 4. The real `flock` mechanics — proof this is a genuine cross-process lock, not a
#    function that merely runs and returns.
# ---------------------------------------------------------------------------------------


def test_acquire_holds_a_real_exclusive_flock_and_release_frees_it(
    conftest_module: types.ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slot_dir = tmp_path / "slots"
    monkeypatch.setattr(conftest_module, "_SLOT_DIR", slot_dir)
    monkeypatch.setattr(conftest_module, "_SLOT_COUNT", 1)

    conftest_module._acquire_pytest_gate_slot()
    held_path = slot_dir / f"{conftest_module._SLOT_PREFIX}1"
    try:
        # A second, independent open() of the same file: `flock` locks are per open
        # file description, so this must conflict even though it is the same process.
        with open(held_path, "w") as second, pytest.raises(BlockingIOError):
            fcntl.flock(second.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    finally:
        conftest_module._release_pytest_gate_slot()

    with open(held_path, "w") as third:
        fcntl.flock(third.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  # must not raise
        fcntl.flock(third.fileno(), fcntl.LOCK_UN)


def test_a_full_slot_set_falls_through_to_the_blocking_wait_path(
    conftest_module: types.ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """With every non-blocking slot pre-held by someone else, `_acquire_pytest_gate_slot`
    must fall through to the blocking `flock` on slot 1 and print the wait message —
    proof (a)'s own mechanism, exercised without a second real process by holding every
    slot from this one first.
    """
    slot_dir = tmp_path / "slots"
    slot_dir.mkdir()
    monkeypatch.setattr(conftest_module, "_SLOT_DIR", slot_dir)
    monkeypatch.setattr(conftest_module, "_SLOT_COUNT", 2)

    with contextlib.ExitStack() as stack:
        holders = [
            stack.enter_context(
                open(slot_dir / f"{conftest_module._SLOT_PREFIX}{i}", "w")
            )
            for i in (1, 2)
        ]
        for handle in holders:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        def _release_holder_1_soon() -> None:
            fcntl.flock(holders[0].fileno(), fcntl.LOCK_UN)

        timer = threading.Timer(0.3, _release_holder_1_soon)
        timer.start()
        try:
            conftest_module._acquire_pytest_gate_slot()
        finally:
            timer.cancel()
        conftest_module._release_pytest_gate_slot()

        err = capsys.readouterr().err
        assert "all 2 gate slots are busy" in err
        assert "acquired after waiting" in err
