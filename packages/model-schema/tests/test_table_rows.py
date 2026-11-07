"""`table_rows.py` -- the one markdown table-row splitter (FD-1484).

It is stdlib-only because `scripts/` load it by path under a bare `python3` with no project
packages (`.github/workflows/docs.yml`), so the import guard and the bare-load test are the
two halves of the same constraint.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

from model_schema import table_rows

_MODULE_PATH = Path(table_rows.__file__)


@pytest.mark.parametrize(
    ("line", "cells"),
    [
        ("| a | b | c |", ["a", "b", "c"]),
        ("| a\\|x | b | c |", ["a\\|x", "b", "c"]),
        ("| a | b\\|y | c |", ["a", "b\\|y", "c"]),
        ("| a | b | c\\|z |", ["a", "b", "c\\|z"]),
        ("| a | b | d\\| |", ["a", "b", "d\\|"]),
        ("| `GET` | `/x\\|y` | z |", ["`GET`", "`/x\\|y`", "z"]),
        ("| a |  | c |", ["a", "", "c"]),
        ("| a | b | c", ["a", "b", "c"]),
    ],
)
def test_split_row_keeps_an_escaped_pipe_inside_its_cell(line: str, cells: list[str]) -> None:
    assert table_rows.split_row(line) == cells


def test_cell_count_ignores_an_escaped_pipe() -> None:
    assert table_rows.cell_count("| a | b\\|c | d |") == 3


def test_endpoint_row_reads_the_whole_path_cell_across_an_escaped_pipe() -> None:
    row = "| `GET`/`PUT` | `/api/v1/x?a=1\\|2`, `/api/v1/y` | notes |"
    assert table_rows.endpoint_row(row) == ("GET`/`PUT", "`/api/v1/x?a=1\\|2`, `/api/v1/y`")
    assert table_rows.endpoint_row("| Method | Path | Notes |") is None
    assert table_rows.endpoint_row("| --- | --- | --- |") is None
    assert table_rows.endpoint_row("prose | GET | `/x` |") is None


def test_table_rows_imports_only_the_stdlib() -> None:
    tree = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "a relative import reaches model_schema"
            imported.add((node.module or "").split(".")[0])
    assert imported <= set(sys.stdlib_module_names), imported - set(sys.stdlib_module_names)


def test_a_script_loads_it_by_path_with_no_project_packages() -> None:
    program = (
        "import importlib.util, sys\n"
        "spec = importlib.util.spec_from_file_location('table_rows', sys.argv[1])\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(m)\n"
        "print(m.split_row('| a\\\\|b | c |'))\n"
    )
    done = subprocess.run(
        [sys.executable, "-I", "-S", "-c", program, str(_MODULE_PATH)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "['a\\\\|b', 'c']"
