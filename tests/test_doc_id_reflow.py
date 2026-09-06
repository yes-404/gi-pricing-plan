"""`_reflow_long_lines`: the migration must not leave behind a line its own linter rejects.

`_rewrite_citations` substitutes a citation with a longer, id-based path and does not
reflow the line it just lengthened. At `cfbc0390` the tree lints clean; after a migration
run it did not — 190 diagnostics, every one of them a long line, across 56 files — so CI
stopped at the linter and no later stage ran at all.

The fix belongs in the tool, never in the tool's output: a hand-edited tree and the tool
that produced it would disagree, and the next run would reproduce the whole population.
That is what these tests pin, from both sides:

* a line the migration lengthens past the limit, where a newline is **provably**
  semantics-free (a whole-line `#` comment by `tokenize`, a docstring line by `ast`), is
  reflowed — and the program it belongs to is unchanged, which for the comment case is
  checkable exactly, since comments do not appear in the AST at all;
* a line where it is **not** provable — a string literal, whose value a newline would
  change — is refused, left byte-for-byte as it was, and carried out under a named refusal
  class for per-file disclosure into the governed W37-11 record. Never silently reflowed,
  never mangled, and never given a per-line lint suppression.

The second limb is the one worth having. A pass that reflowed everything would satisfy the
linter and corrupt a value on the way; a test that only checked "no long lines remain"
could not tell the two apart.
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

# `doc-id.py` does `import _docid` / `import _docverify`, its siblings in that directory.
# The identical two lines `tests/test_doc_id_migrate.py` carries, for the identical reason.
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))


def _load_doc_id() -> types.ModuleType:
    """The loader every other `doc-id.py` test module uses: a hyphenated filename is not
    an `import` target, and `sys.modules` registration must precede `exec_module` for the
    module's own dataclasses to resolve.
    """
    spec = importlib.util.spec_from_file_location("_doc_id_reflow_under_test", DOC_ID_SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def doc_id() -> types.ModuleType:
    return _load_doc_id()


#: A filename of the shape this migration actually writes. Long enough that the lines below
#: cross the limit once it is substituted in, and — deliberately — longer on its own than
#: the limit, which is the property that defeated a whitespace-only wrap: 86 of the 177
#: reflowable lines in the real corpus carried a token with no space in it at all.
LONG_PATH: Final = (
    "docs/rulings/RL-00922-the-remediation-is-ruled-into-the-reopen-and-the-verdict-is-"
    "ruled-with-it-and-the-owner-named.md"
)


def _tree(tmp_path: pathlib.Path, name: str, body: str) -> pathlib.Path:
    """A minimal tree carrying the project's own line limit and one Python file."""
    (tmp_path / "pyproject.toml").write_text(
        '[tool.ruff]\nline-length = 100\n', encoding="utf-8"
    )
    target = tmp_path / name
    target.write_text(body, encoding="utf-8")
    return target


def _limit(doc_id: types.ModuleType, tmp_path: pathlib.Path) -> int:
    return int(doc_id._python_lint_scope(tmp_path).limit)


def test_a_comment_line_over_the_limit_is_reflowed_and_the_program_is_unchanged(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Positive control, limb one: reflowed, under the limit, same program.

    A comment does not reach the AST, so `ast.dump` before and after is an exact equality
    — the strongest form this proof can take, and not one the docstring limb can offer.
    """
    body = f"# see {LONG_PATH} for why this line is over the limit after a rewrite\nX = 1\n"
    target = _tree(tmp_path, "mod.py", body)
    before = target.read_text(encoding="utf-8")
    assert any(len(line) > _limit(doc_id, tmp_path) for line in before.splitlines()), (
        "fixture is not over the limit, so it cannot control anything"
    )

    changed, refused = doc_id._reflow_long_lines(tmp_path)

    after = target.read_text(encoding="utf-8")
    assert changed == ["mod.py"]
    assert refused == []
    assert all(len(line) <= _limit(doc_id, tmp_path) for line in after.splitlines())
    assert ast.dump(ast.parse(after)) == ast.dump(ast.parse(before))
    # The citation survives the wrap as text, reassembled across the continuation the way
    # `_wrapped_path_patterns` reads one back: every break falls inside the path run.
    assert LONG_PATH in "".join(
        line.lstrip().removeprefix("# ").removeprefix("#") for line in after.splitlines()
    )


def test_a_docstring_line_over_the_limit_is_reflowed(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Positive control, limb one again, for the proof `ast` rather than `tokenize` gives.

    The docstring's *value* does change — the inserted newline and indentation become part
    of it — which is why this limb asserts the code around it is untouched and the words
    survive, rather than claiming an equality that would not be true.
    """
    body = f'"""Summary that cites {LONG_PATH} and therefore runs past the limit."""\n\nY = 2\n'
    target = _tree(tmp_path, "mod.py", body)

    changed, refused = doc_id._reflow_long_lines(tmp_path)

    after = target.read_text(encoding="utf-8")
    assert changed == ["mod.py"]
    assert refused == []
    assert all(len(line) <= _limit(doc_id, tmp_path) for line in after.splitlines())
    tree = ast.parse(after)
    assert ast.get_docstring(tree) is not None
    assert "Y = 2" in after


def test_a_string_literal_over_the_limit_is_refused_and_left_byte_for_byte(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Positive control, limb two — the limb that makes the first one mean something.

    A newline inside a string literal changes the value, so no proof covers it and the
    line is refused: unchanged on disk, and reported under a named class so it can be
    disclosed per file into the governed record. If this ever starts passing by the line
    being reflowed instead, the migration has begun rewriting values.
    """
    body = f'PATH = "{LONG_PATH}"  # a value, not prose\n'
    target = _tree(tmp_path, "mod.py", body)
    before = target.read_text(encoding="utf-8")

    changed, refused = doc_id._reflow_long_lines(tmp_path)

    assert changed == []
    assert target.read_text(encoding="utf-8") == before, "a refused line must not be touched"
    assert [(r.path, r.cls) for r in refused] == [
        ("mod.py", doc_id._REFUSAL_NOT_PROVABLY_SAFE)
    ]
    # The value is intact — the property a reflow here would have destroyed.
    module = ast.parse(target.read_text(encoding="utf-8"))
    assigned = module.body[0]
    assert isinstance(assigned, ast.Assign)
    assert isinstance(assigned.value, ast.Constant)
    assert assigned.value.value == LONG_PATH


def test_a_refusal_names_the_line_number_in_the_file_that_was_written(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A refusal is reported at its line in the file the run WRITES, not in the text read.

    Every reflow above a refusal inserts lines, so the two numbers diverge. The first
    reconciliation of this pass against the linter found exactly that — refusals citing a
    line eighteen short of the one the linter reported — and a disclosure row whose line
    number resolves to the wrong line is worse than no row at all.
    """
    body = (
        f"# a comment citing {LONG_PATH} that will be wrapped onto several lines\n"
        f'PATH = "{LONG_PATH}"  # refused: a value\n'
    )
    target = _tree(tmp_path, "mod.py", body)

    _, refused = doc_id._reflow_long_lines(tmp_path)

    assert len(refused) == 1
    written = target.read_text(encoding="utf-8").splitlines()
    assert written[refused[0].line - 1].startswith("PATH = ")
    assert refused[0].line > 2, "the comment above it wrapped, so the number must have moved"


def test_a_file_that_does_not_parse_has_every_long_line_refused(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """No proof is available for a file `tokenize`/`ast` cannot read, so nothing is
    reflowed in it — the one place a guess would be most confident and least safe.
    """
    body = f"# {LONG_PATH} is cited here and the next line is not Python at all\ndef (\n"
    target = _tree(tmp_path, "broken.py", body)
    before = target.read_text(encoding="utf-8")

    changed, refused = doc_id._reflow_long_lines(tmp_path)

    assert changed == []
    assert target.read_text(encoding="utf-8") == before
    assert [r.cls for r in refused] == [doc_id._REFUSAL_NOT_PROVABLY_SAFE]


def test_a_comment_carrying_a_tool_directive_is_refused_not_split(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A directive binds to the physical line it sits on. Splitting one would silently
    change which line is suppressed or checked, so such a comment is refused even though
    `tokenize` proves the newline itself harmless.
    """
    # The directive word sits in the comment's prose, not immediately after the `#`. A
    # comment that opens with a pragma is a different case entirely: the linter does not
    # report such a line at all, so this pass never reaches it — which is why the fixture
    # cannot be written that way and still be testing this branch.
    body = f"# {LONG_PATH} — and this line's prose also mentions a noqa directive\nZ = 3\n"
    target = _tree(tmp_path, "mod.py", body)
    before = target.read_text(encoding="utf-8")

    changed, refused = doc_id._reflow_long_lines(tmp_path)

    assert changed == []
    assert target.read_text(encoding="utf-8") == before
    assert [r.cls for r in refused] == [doc_id._REFUSAL_TOOL_DIRECTIVE]


def test_a_line_the_linter_would_not_report_is_neither_reflowed_nor_refused(
    doc_id: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Over-reporting is a defect too: refusing a line nothing will ever flag discloses a
    residue that does not exist.

    Two shapes the project's linter exempts and this pass must exempt with it — a line
    whose length is owed entirely to a trailing pragma, and a line with no whitespace to
    break at. Found by reconciling this pass's refusals against the linter's own output on
    the real corpus: seventeen such lines, none of them created by the migration.

    A no-op assertion cannot fail against a no-op implementation, so this test carries a
    positive limb in the same file: one comment line that MUST be reflowed. Without it the
    test passes against a `_reflow_long_lines` that does nothing at all — which is exactly
    what it did when the red-then-green control was run, and why the limb was added.
    """
    exempt = (
        "CALL = some_name(argument_one, argument_two)"
        + " " * 20
        + "  # type: ignore[no-untyped-call]\n"
        # A list element that is one long token and nothing else — no whitespace after the
        # indentation, so there is nowhere to break and the linter never reports it.
        f'VALUES = [\n    "{LONG_PATH}",\n]\n'
    )
    body = exempt + f"# a comment citing {LONG_PATH} which IS over the limit and must wrap\n"
    target = _tree(tmp_path, "mod.py", body)

    changed, refused = doc_id._reflow_long_lines(tmp_path)

    assert changed == ["mod.py"], "the positive limb must have been reflowed"
    assert refused == []
    after = target.read_text(encoding="utf-8")
    # Neither exempt line was touched: they are still present verbatim, still over-long.
    assert exempt in after
    assert all(
        len(line) <= _limit(doc_id, tmp_path)
        for line in after.splitlines()
        if line.lstrip().startswith("#")
    )
