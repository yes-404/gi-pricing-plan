"""`scripts/audit-docs.py` check 1 ignores links written inside code (F66).

Check 1 scanned raw lines, so `[x](y)` quoted in back-ticks or in a fenced block was resolved as
a path and reported as a broken link. It now masks fenced blocks and inline code spans first.
A broken link in prose must still fail, on the same line as a code span and after a fence.

No `@pytest.mark.req` marker: this is the correctness of the docs audit tool, not evidence for a
numbered platform requirement. Each case writes its fixture under `tmp_path`.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"


def _load_audit() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("_audit_docs_link_code_spans", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


audit = _load_audit()


def _broken(tmp_path: pathlib.Path, body: str) -> list[str]:
    doc = tmp_path / "doc.md"
    doc.write_text(body, encoding="utf-8")
    (tmp_path / "real.md").write_text("x\n", encoding="utf-8")
    return list(audit.broken_relative_links(doc))


@pytest.mark.parametrize(
    "body",
    [
        "A link is written `[x](missing.md)` in markdown.\n",
        "Double ticks ``[x](missing.md)`` too.\n",
        "```\n[x](missing.md)\n```\n",
        "```md\nsee [x](missing.md)\n```\nafter the fence\n",
    ],
)
def test_a_link_inside_code_is_not_a_link(tmp_path: pathlib.Path, body: str) -> None:
    assert _broken(tmp_path, body) == []


@pytest.mark.parametrize(
    ("body", "targets"),
    [
        ("A broken [link](missing.md) in prose.\n", ["missing.md"]),
        ("`[x](ignored.md)` then [bad](missing.md).\n", ["missing.md"]),
        ("```\n[x](ignored.md)\n```\n[bad](missing.md)\n", ["missing.md"]),
        ("A unclosed ` tick then [bad](missing.md).\n", ["missing.md"]),
        ("A good [link](real.md) and [web](https://example.org/x).\n", []),
    ],
)
def test_a_broken_link_outside_code_still_fails(
    tmp_path: pathlib.Path, body: str, targets: list[str]
) -> None:
    assert _broken(tmp_path, body) == targets
