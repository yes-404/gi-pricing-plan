"""`docs/specs/` JSON examples against `model-schema` (FD-1381). Correctness of the audit tool."""

import importlib.util
import json
import pathlib
import re
import sys
import types
from typing import Any

import pytest

import model_schema

ROOT = pathlib.Path(__file__).resolve().parents[1]
ILLUSTRATIVE_CEILING = 0  # S4 sets this to the count at the head; it may only fall.
_JSON_FENCE = re.compile(r"^\s*```json\b")


def _audit() -> types.ModuleType:
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location(
        "audit_docs_for_examples", ROOT / "scripts/audit-docs.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT: Any = _audit()
BLOCKS = [b for p in sorted((ROOT / "docs/specs").glob("*.md")) for b in AUDIT.spec_fences(p)]
MARKED = [b for b in BLOCKS if b.schema]


def _validate(schema: str, body: str) -> None:
    cls = getattr(model_schema, schema, None)
    assert cls is not None, f"{schema} is not in model_schema"
    cls.model_validate(json.loads(body))


@pytest.mark.parametrize("block", MARKED, ids=lambda b: f"{b.path.name}:{b.line}")
def test_a_class_marked_example_validates_in_full(block: Any) -> None:
    _validate(block.schema, block.body)


@pytest.mark.parametrize(
    ("info", "body", "expected"),
    [
        ("json", "{}", "no schema= or illustrative marker"),
        ("", "{}", "declares no language"),
        ("json schema=Dataset", "{", "does not parse"),
    ],
)
def test_check_40_refuses(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, info: str, body: str, expected: str
) -> None:
    spec = tmp_path / "99-planted.md"
    spec.write_text(f"```{info}\n{body}\n```\n", encoding="utf-8")
    failures: list[str] = []
    monkeypatch.setattr(AUDIT, "fail", failures.append)
    AUDIT.check_spec_examples([spec])
    assert [m for m in failures if m.startswith("check 40: ") and expected in m]


def test_an_unknown_class_is_refused() -> None:
    with pytest.raises(AssertionError, match="NoSuchClass"):
        _validate("NoSuchClass", "{}")


def test_the_example_the_finding_named_fails() -> None:
    body = (ROOT / "tests/fixtures/spec-examples/ra-c535b19d.json").read_text("utf-8")
    with pytest.raises(ValueError, match=r"premium_ladder.*FR-214"):
        _validate("RatingAlgorithm", body)


def test_the_census_is_a_second_reading_of_the_same_lines() -> None:
    lines = [
        ln for p in (ROOT / "docs/specs").glob("*.md") for ln in p.read_text("utf-8").splitlines()
    ]
    json_lines = sum(bool(_JSON_FENCE.match(ln)) for ln in lines)
    assert json_lines > 0
    assert json_lines == sum(b.language == "json" for b in BLOCKS)


def test_the_exemption_set_only_shrinks() -> None:
    assert sum(b.illustrative for b in BLOCKS) <= ILLUSTRATIVE_CEILING
