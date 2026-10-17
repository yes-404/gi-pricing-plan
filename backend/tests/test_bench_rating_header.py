"""`scripts/bench-rating.py` prints N, the worker count of the replica, in its header.

RL-1685 (PL-1454 DP-3 (b)): a replica is N `uvicorn` worker processes, N is stated with every
NFR-489 or NFR-454 reading, and *"every bench output prints N in its header, so a reading
without N cannot exist"*. The header is what these tests read; they run `main()` up to the
first thing after it (`_ctx`, replaced by a sentinel that stops the run) so no bundle is
compiled, no database touched and no server started.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import sys
from types import ModuleType
from typing import Any

import pytest

pytestmark = pytest.mark.req("NFR-489")

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "bench-rating.py"


class _HeaderPrintedError(Exception):
    """Raised by the replaced `_ctx`, the first call `main` makes after printing its header."""


@pytest.fixture
def bench(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    spec = importlib.util.spec_from_file_location("bench_rating_under_test", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # `@dataclass` under `from __future__ import annotations` looks the module up by name.
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)

    def _stop() -> Any:
        raise _HeaderPrintedError

    module._ctx = _stop
    return module


def _header(
    bench: ModuleType,
    argv: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> str:
    monkeypatch.setattr(sys, "argv", ["bench-rating.py", *argv])
    with pytest.raises(_HeaderPrintedError):
        bench.main()
    return capsys.readouterr().out


def test_the_header_prints_the_n_it_was_started_with(
    bench: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    header = _header(bench, ["--workers", "4"], monkeypatch, capsys)
    assert re.search(r"\bN = 4\b", header), header


def test_a_run_with_no_workers_flag_prints_n_as_one(
    bench: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    header = _header(bench, [], monkeypatch, capsys)
    assert re.search(r"\bN = 1\b", header), header


def test_the_server_is_started_with_the_n_the_header_prints(
    bench: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    import subprocess

    argv: list[list[str]] = []
    monkeypatch.setattr(subprocess, "Popen", lambda cmd, **_kw: argv.append(cmd))

    bench._serve(dsn="x", bucket="y", log_path=tmp_path / "s.log", port=1, workers=4)
    bench._serve(dsn="x", bucket="y", log_path=tmp_path / "s.log", port=1, workers=1)

    assert argv[0][argv[0].index("--workers") + 1] == "4", argv[0]
    assert "--workers" not in argv[1], argv[1]
