"""FD-1211's event: a process that loads FD-1199's extensions exits cleanly (WK-674 Slice 4).

FD-1199's abort (`PyGILState_Release: thread state ... must be current`) fires at interpreter
**finalization**, once the work is done, in a process that has loaded native extensions with
their own threads. `deploy/docker-compose.yml` states the design: `api` and `worker` finalize
normally on SIGTERM and the container is then replaced. This test is the proof FD-1211 asks
for, at the process level: a fresh interpreter loads the extension list the finding names (the
lazy imports of the worker's fit handlers) and exits through the normal path.

The abort is intermittent (one occurrence in the last 40 CI runs of FD-1199), so one clean exit
proves nothing. `RUNS` is the stated count; the broken-input proof shows the helper reports a
child that aborts at exit, which is the signature being hunted.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

#: Stated repetition count (PL-1237 Task 4 gate: "repeated enough times to meet an
#: intermittent abort, with the count stated").
RUNS = 25

# The extension list of FD-1211's evidence, plus the app's eager reach.
LOAD_EXTENSIONS = (
    "import numpy, scipy, polars, sklearn, pandas, pyarrow, numexpr, glum, xgboost, lightgbm;"
    "import app.worker.model_handlers;"
)


def _exit_codes(program: str, runs: int) -> list[int]:
    return [
        subprocess.run([sys.executable, "-c", program], capture_output=True, timeout=120).returncode
        for _ in range(runs)
    ]


@pytest.mark.req("FR-415")
def test_a_process_that_loads_the_extensions_exits_cleanly_every_time() -> None:
    codes = _exit_codes(LOAD_EXTENSIONS, RUNS)
    assert codes == [0] * RUNS, f"non-zero exits (rc -6 is the FD-1199 abort): {codes}"


@pytest.mark.req("FR-415")
def test_the_check_reports_an_abort_at_exit() -> None:
    """Broken-input proof: a child that aborts after loading the extensions is not a 0."""
    aborting = LOAD_EXTENSIONS + "import os; os.abort()"
    assert _exit_codes(aborting, 2) == [-6, -6]
