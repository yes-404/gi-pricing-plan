"""`scripts/req-coverage.py` and `scripts/scope-audit.py` read every form of the requirement
marker (FD-1725).

They read `@pytest.mark.req("FR-1")` only, by regex. Two other forms were never checked
against the specs: the multi-argument call `req("FR-272", "FR-273")` and the module-level
`pytestmark = pytest.mark.req(...)`, alone or in a list. A marker naming an id that does not
exist, in either form, passed the unknown-id check silently.

Each case builds its own tree under `tmp_path` and points the scripts' `ROOT` at it; nothing
writes into the real tree (the F89 lesson). No `@pytest.mark.req` marker on anything here: this
is the correctness of the two audit tools, not evidence for a numbered platform requirement.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(name: str, filename: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


req_coverage = _load("req_coverage_under_test", "req-coverage.py")
scope_audit = _load("scope_audit_under_test", "scope-audit.py")

DECORATOR = '@pytest.mark.req("FR-272")\ndef test_a() -> None: ...\n'
MULTI = '@pytest.mark.req("FR-272", "FR-273")\ndef test_b() -> None: ...\n'
MODULE_LEVEL = 'pytestmark = pytest.mark.req("NFR-5")\n'
MODULE_LIST = 'pytestmark = [pytest.mark.skip, pytest.mark.req("FR-272", "FR-273")]\n'
ATTRIBUTE_FORM = 'import pytest\n\n\n@pytest.mark.req("FR-273")\nclass TestX: ...\n'
NOT_A_MARKER = '"""Quotes @pytest.mark.req("FR-1") in prose."""\nx = req("FR-2")\n'


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (DECORATOR, ["FR-272"]),
        (MULTI, ["FR-272", "FR-273"]),
        (MODULE_LEVEL, ["NFR-5"]),
        (MODULE_LIST, ["FR-272", "FR-273"]),
        (ATTRIBUTE_FORM, ["FR-273"]),
        (NOT_A_MARKER, []),
    ],
)
def test_markers_in_reads_all_three_forms(source: str, expected: list[str]) -> None:
    assert req_coverage.markers_in(source) == expected


def _tree(tmp_path: pathlib.Path, **tests: str) -> pathlib.Path:
    """A fixture repository: three specified ids, `tests/` as the one test root."""
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "docs" / "specs" / "01.md").write_text(
        "| **FR-272** | a |\n| **FR-273** | b |\n| **NFR-5** | c |\n", encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n', encoding="utf-8"
    )
    (tmp_path / "tests").mkdir()
    for name, source in tests.items():
        (tmp_path / "tests" / f"test_{name}.py").write_text(source, encoding="utf-8")
    return tmp_path


def test_a_tree_of_known_ids_in_every_form_passes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _tree(tmp_path, a=DECORATOR, b=MULTI, c=MODULE_LEVEL)
    monkeypatch.setattr(req_coverage, "ROOT", root)
    assert req_coverage.main() == 0
    assert "requirements marked    : 3" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("source", "unknown"),
    [
        ('@pytest.mark.req("FR-272", "FR-999")\ndef test_a() -> None: ...\n', "FR-999"),
        ('pytestmark = pytest.mark.req("NFR-999")\n', "NFR-999"),
        ('pytestmark = [pytest.mark.req("FR-272", "FR-998")]\n', "FR-998"),
    ],
)
def test_an_unknown_id_in_the_multi_argument_or_module_level_form_fails(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    source: str,
    unknown: str,
) -> None:
    """The regex missed both: the unknown-id exit never fired for them."""
    root = _tree(tmp_path, planted=source)
    monkeypatch.setattr(req_coverage, "ROOT", root)
    assert req_coverage.main() == 1
    out = capsys.readouterr().out
    assert "tests claim requirements that do not exist" in out
    assert unknown in out


def test_scope_audit_evidence_reads_the_same_forms(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _tree(tmp_path, a=DECORATOR, b=MULTI, c=MODULE_LEVEL)
    monkeypatch.setattr(scope_audit, "ROOT", root)
    assert scope_audit.evidence() == {
        "FR-272": ["tests/test_a.py", "tests/test_b.py"],
        "FR-273": ["tests/test_b.py"],
        "NFR-5": ["tests/test_c.py"],
    }
