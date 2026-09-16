"""The 13 refused string literals (deputy ruling, `to-lead.md` 2026-09-06 08:42 BST,
ACCEPTED): "ast-proven split for the 13 (no residue, no rows unless an actual refusal)".

`_reflow_long_lines` (W37-6 PR-C part 1) never touches a string literal — a newline
inside one changes its value, and no `tokenize`/`ast` proof covers that. This module is
the second, separate pass over exactly its own refusals (`_REFUSAL_NOT_PROVABLY_SAFE`
lines that are, specifically, a bare `NAME = "literal"` assignment on one physical
line): split the literal by implicit string-literal concatenation —

    NAME = (
        "first chunk "
        "second chunk"
    )

— which Python still evaluates to the identical single string, and accept the split only
when an `ast` round-trip proves it: every module-level constant's *value*, not just the
one being split, compared before and after the rewrite. Comparing constants means BEFORE
and AFTER — a candidate that merely parses is not proof that nothing changed.

Kept as a separate function from `_reflow_long_lines` rather than folded into it, so that
module's own pinned tests (the comment/docstring limbs and their refusal classes) are
untouched — this pass only ever revisits a line that pass already refused.
"""

from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys
import types
from typing import Final

import pytest

REPO: Final = pathlib.Path(__file__).resolve().parents[1]
DOC_ID_SCRIPT_PATH: Final = REPO / "scripts" / "doc-id.py"

if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))


def _load_doc_id() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "_doc_id_string_literal_under_test", DOC_ID_SCRIPT_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def doc_id() -> types.ModuleType:
    return _load_doc_id()


def _tree(tmp_path: pathlib.Path, name: str, body: str, *, limit: int = 100) -> pathlib.Path:
    (tmp_path / "pyproject.toml").write_text(
        f"[tool.ruff]\nline-length = {limit}\n", encoding="utf-8"
    )
    target = tmp_path / name
    target.write_text(body, encoding="utf-8")
    return target


def _limit(doc_id: types.ModuleType, tmp_path: pathlib.Path) -> int:
    return int(doc_id._python_lint_scope(tmp_path).limit)


#: A long path-shaped constant, exactly the corpus shape #770's own reconciliation named:
#: no whitespace at all, only path-run characters (`-`, `/`, `.`) -- the case a
#: whitespace-only wrap cannot help and `_token_break`'s rule exists for.
_LONG_PATH_CONST: Final = (
    "docs/rulings/RL-00922-the-remediation-is-ruled-into-the-reopen-and-the-verdict-is-"
    "ruled-with-it-and-the-owner-named.md"
)


def test_a_whitespace_splittable_constant_is_split_by_implicit_concatenation(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Positive control: a long string constant with break points is split into an
    implicit concatenation, still parses, and its value is byte-identical to before —
    the exact property the ast round-trip proof exists to establish.
    """
    body = (
        'SUMMARY = "this is a long piece of prose that will not fit on one line at '
        'all once it is assigned to a module constant like this one"\n'
        "OTHER = 1\n"
    )
    target = _tree(tmp_path, "mod.py", body)
    before_value = (
        "this is a long piece of prose that will not fit on one line at all once it "
        "is assigned to a module constant like this one"
    )

    _changed, refused = doc_id._reflow_long_lines(tmp_path)
    limit = _limit(doc_id, tmp_path)
    resplit, still_refused = doc_id._split_long_string_literals(tmp_path, limit, refused)

    after = target.read_text(encoding="utf-8")
    assert resplit == ["mod.py"]
    assert still_refused == []
    assert all(len(line) <= limit for line in after.splitlines())
    ast.parse(after)  # must still parse
    module_constants = doc_id._module_constants(after)
    assert module_constants is not None
    assert module_constants["SUMMARY"] == before_value
    assert module_constants["OTHER"] == 1
    assert "(" in after
    assert ")" in after  # implicit concatenation, not one wide literal


def test_a_no_whitespace_path_constant_is_split_at_a_path_character(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The shape the real 13 actually are: a citation with no whitespace at all. Split
    at a `_TOKEN_BREAK_CHARS` character inside the path run — the identical rule
    `_token_break` already applies for the comment/docstring limb, reused here — never a
    second definition of the same break rule.
    """
    body = f'PATH = "{_LONG_PATH_CONST}"  # a value, not prose\n'
    target = _tree(tmp_path, "mod.py", body)

    _changed, refused = doc_id._reflow_long_lines(tmp_path)
    limit = _limit(doc_id, tmp_path)
    resplit, still_refused = doc_id._split_long_string_literals(tmp_path, limit, refused)

    after = target.read_text(encoding="utf-8")
    assert resplit == ["mod.py"]
    assert still_refused == []
    assert all(len(line) <= limit for line in after.splitlines())
    module_constants = doc_id._module_constants(after)
    assert module_constants is not None
    assert module_constants["PATH"] == _LONG_PATH_CONST


def test_a_backslash_bearing_literal_is_refused_not_split(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A body carrying a backslash is refused outright, never attempted: a cut could
    land inside an escape sequence, and refusing rather than reasoning about escapes is
    the same "no proof, no touch" discipline the comment/docstring limbs already apply.
    """
    long_word = "a" * 90
    body = f'PATTERN = "{long_word}\\\\n more text after the escape to push it over"\n'
    target = _tree(tmp_path, "mod.py", body)
    before = target.read_text(encoding="utf-8")

    _changed, refused = doc_id._reflow_long_lines(tmp_path)
    limit = _limit(doc_id, tmp_path)
    resplit, still_refused = doc_id._split_long_string_literals(tmp_path, limit, refused)

    assert resplit == []
    assert target.read_text(encoding="utf-8") == before
    assert [(r.path, r.cls) for r in still_refused] == [
        ("mod.py", doc_id._REFUSAL_NOT_PROVABLY_SAFE)
    ]


def test_a_single_unbreakable_token_with_no_break_character_stays_refused(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """No whitespace and no `_TOKEN_BREAK_CHARS` character at all — truly nowhere safe
    to cut — is refused and left byte-for-byte, exactly like before this pass existed.
    """
    long_word = "a" * 140
    body = f'PATTERN = "{long_word}"\n'
    target = _tree(tmp_path, "mod.py", body)
    before = target.read_text(encoding="utf-8")

    _changed, refused = doc_id._reflow_long_lines(tmp_path)
    limit = _limit(doc_id, tmp_path)
    resplit, still_refused = doc_id._split_long_string_literals(tmp_path, limit, refused)

    assert resplit == []
    assert target.read_text(encoding="utf-8") == before
    assert [(r.path, r.cls) for r in still_refused] == [
        ("mod.py", doc_id._REFUSAL_NOT_PROVABLY_SAFE)
    ]


def test_the_proof_compares_every_module_constant_not_only_the_one_split(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A file with several module-level constants: splitting one must not perturb any
    other's value. `_module_constants` is compared whole, before and after — a proof
    scoped to the one name being split cannot see a break that corrupted another.
    """
    body = (
        'A = "unrelated short value"\n'
        'SUMMARY = "this is a long piece of prose that will not fit on one line at '
        'all once it is assigned to a module constant like this one"\n'
        "B = 42\n"
        'C = "another short one"\n'
    )
    target = _tree(tmp_path, "mod.py", body)

    _changed, refused = doc_id._reflow_long_lines(tmp_path)
    limit = _limit(doc_id, tmp_path)
    resplit, still_refused = doc_id._split_long_string_literals(tmp_path, limit, refused)

    after = target.read_text(encoding="utf-8")
    assert resplit == ["mod.py"]
    assert still_refused == []
    module_constants = doc_id._module_constants(after)
    assert module_constants == {
        "A": "unrelated short value", "SUMMARY": (
            "this is a long piece of prose that will not fit on one line at all once "
            "it is assigned to a module constant like this one"
        ),
        "B": 42, "C": "another short one",
    }
