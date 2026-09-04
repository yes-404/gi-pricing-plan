"""Repository-root `conftest.py` — loaded by pytest unconditionally, before any
`testpaths` entry, regardless of which of them a given invocation collects (confirmed
directly: a probe placed here fires for every one of `backend/tests`,
`packages/*/tests`, `tests`, `examples/fremtpl2`; a probe placed in `tests/conftest.py`
does not, since `tests/` is a sibling of the other roots rather than their parent).

Two things belong here because a bare `uv run pytest -q` — not only the wrapped gate
command `.claude/skills/dev-commands/SKILL.md` documents — must be budgeted, after that
wrapper form was typed wrong three times in one day (W37-6 channel):

1. The six thread-cap environment variables, defaulted (never overridden) before any
   test module can import Polars/DuckDB and size a runtime thread pool from them.
2. A gate-slot lock acquired for a bare, untargeted, executing run — never for a
   targeted iteration run (`pytest <file> -k <symbol>`, which `dev-commands` explicitly
   keeps "uncapped and unslotted" during iteration), never for `--collect-only`
   (`.claude/skills/python-test/SKILL.md`: "`--collect-only` needs no window"), and never
   a *second* time when the wrapper already holds one (below).

**One shared lock namespace with the wrapper, announced rather than duplicated.** This
hook locks the identical `/tmp/slots/gate-{1,2,3}` files the wrapped gate command in
`dev-commands` uses — a *separate* namespace was tried first and rejected (the deputy's
ruling): it let three wrapped gates and three bare ones run at once, six total, defeating
the budget the files exist to enforce. One namespace means a correctly-wrapped run and a
bare one draw from the same three slots either way.

That raises the deadlock risk a shared namespace implies: the wrapper's outer shell holds
its lock via its own open file description and then execs `uv run pytest` as a *child* —
if this hook's `flock()` ran unconditionally inside that child, it would be a fresh
`open()` unrelated to the parent's held lock, and it would block forever waiting for a
lock its own ancestor already holds and never releases until this process exits. The
wrapper's own `export GIP_GATE_SLOT=/tmp/slots/gate-$i` (set immediately after its own
`flock` succeeds, before the `&&`-chain runs) is the fix: this hook checks the variable
first and does nothing when it is already set, trusting the announcement rather than
re-acquiring. A bare invocation carries no such announcement, so it locks for real.
"""

from __future__ import annotations

import fcntl
import os
import sys
from pathlib import Path
from typing import IO, Any

import pytest

# --- 1. Thread caps -----------------------------------------------------------------
#
# `setdefault`, not assignment: an explicit override in the calling environment (the
# wrapped gate command already exports all six at `4`) must still win. Measured
# 2026-09-04 (`dev-commands`): an uncapped gate process carried 152 threads — 16
# `tokio-rt-worker` + 16 `async-executor-` (Polars/DuckDB, each sized to `nproc` by
# default) beyond the suite's own ~98 Python pool threads — with none of these six set.
for _var in (
    "POLARS_MAX_THREADS",
    "RAYON_NUM_THREADS",
    "TOKIO_WORKER_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
):
    os.environ.setdefault(_var, "4")
del _var

# --- 2. Gate-slot enforcement for a bare, untargeted, executing run -------------------

#: The wrapper's own files (`.claude/skills/dev-commands/SKILL.md`'s gate block) —
#: deliberately the same namespace, not a private one; see the module docstring.
_SLOT_DIR: Any = Path("/tmp/slots")
_SLOT_COUNT = 3  # matches dev-commands' current gate concurrency budget
_SLOT_PREFIX = "gate-"
#: Set by the wrapper immediately after its own `flock` succeeds — its presence means a
#: slot is already held on this process's behalf, so this hook must not acquire a second.
_ANNOUNCEMENT_VAR = "GIP_GATE_SLOT"

_held_slot_file: IO[Any] | None = None


def _is_bare_full_run(config: pytest.Config) -> bool:
    """True only for the shape `testpaths` fills in with no explicit path, node id,
    `-k` or `-m` filter — the actual "someone typed `uv run pytest -q`" case, never a
    targeted iteration run. `config.invocation_params.args` carries the RAW tokens the
    invocation was given, before pytest's own `testpaths` fallback populates
    `config.args` — confirmed directly: for `pytest -q` alone it is `('-q',)`; for
    `pytest tests/x.py -k foo` it is `('tests/x.py', '-k', 'foo')`; for no args at all
    (ini fallback) it is `()`.

    A token that does not start with `-` and is not itself the value of `-k`/`-m` reads
    as an explicit path or node id and disqualifies the run. This is deliberately
    conservative in one direction only: an unrelated flag taking a bare-word value it
    cannot special-case (`-p no:cacheprovider`'s `no:cacheprovider`) would also
    disqualify a run that is genuinely bare — under-throttling, never the reverse, which
    is the safe failure mode for a lock that must never over-fire and block iteration.
    """
    args = config.invocation_params.args
    for arg in args:
        if arg in ("-k", "-m"):
            return False
        if arg.startswith(("-k", "-m")) and arg not in ("-k", "-m"):
            return False  # "-kpad_width" / "-mreq" form, no space
        if not arg.startswith("-"):
            return False  # an explicit path or node id was given
    return True


def _acquire_pytest_gate_slot() -> None:
    global _held_slot_file
    _SLOT_DIR.mkdir(parents=True, exist_ok=True)
    # Try every slot non-blocking first, so a free slot is taken immediately rather than
    # waiting behind a slot this process could have skipped entirely.
    for i in range(1, _SLOT_COUNT + 1):
        path = _SLOT_DIR / f"{_SLOT_PREFIX}{i}"
        handle = open(path, "w")  # noqa: SIM115 -- held for the whole session, closed in pytest_unconfigure
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            continue
        _held_slot_file = handle
        print(f"[conftest] gate slot {path} acquired, proceeding", file=sys.stderr)
        return
    # All slots busy: block on the first one, printing which slot so a concurrent
    # session's own output names it (dev-commands' proof requirement).
    path = _SLOT_DIR / f"{_SLOT_PREFIX}1"
    print(
        f"\n[conftest] all {_SLOT_COUNT} gate slots are busy — waiting for {path} to "
        "free (.claude/skills/dev-commands/SKILL.md's gate concurrency budget)",
        file=sys.stderr,
    )
    handle = open(path, "w")  # noqa: SIM115
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)  # blocks until a holder releases
    print(f"[conftest] gate slot {path} acquired after waiting, proceeding", file=sys.stderr)
    _held_slot_file = handle


def _release_pytest_gate_slot() -> None:
    global _held_slot_file
    if _held_slot_file is not None:
        fcntl.flock(_held_slot_file.fileno(), fcntl.LOCK_UN)
        _held_slot_file.close()
        _held_slot_file = None


def pytest_configure(config: pytest.Config) -> None:
    if config.getoption("collectonly"):
        return
    if os.environ.get(_ANNOUNCEMENT_VAR):
        # The wrapper already holds a slot on this process's behalf -- trust it rather
        # than acquiring a second one, which would deadlock (module docstring).
        return
    if not _is_bare_full_run(config):
        return
    _acquire_pytest_gate_slot()


def pytest_unconfigure(config: pytest.Config) -> None:
    del config  # unused: the hook signature is pytest's, not this function's to shrink
    _release_pytest_gate_slot()
