"""Governed-document paths split across source lines still name a file that exists.

RFC-937's migration gave governed documents `<PREFIX>-<nnnnn>-<slug>.md` filenames whose
slugs run to ~200 characters. Where such a path is the *value* of a string literal in a
Python source file, the literal cannot be wrapped as prose: any newline inserted into it
changes what the program does. The one transformation that does not is Python's implicit
concatenation of adjacent string literals, which the compiler folds into a single constant
before anything can observe the split.

This module holds the proof, in two parts:

* `test_implicit_concatenation_is_value_preserving` is the mechanism proof -- an
  `ast.literal_eval` round-trip of a single literal against the same text written as
  adjacent pieces, together with the two ways of splitting a literal that are *not*
  value-preserving, so the round-trip is shown to be capable of failing rather than merely
  observed to pass.
* `test_every_split_document_path_names_a_file_that_exists` is the corpus check -- every
  implicitly-concatenated literal in this repository's Python sources whose folded value is
  a governed-document path is resolved against the tree. A split that dropped, doubled or
  reordered a character produces a path that does not resolve, and this fails.

The predicate for "a governed-document path" is built from `_docid.FAMILY_PREFIXES` and
`_docid.PAD_WIDTH` by symbol rather than pasted, so it follows the standard's own width if
`doc-id.py widen` ever moves it (RFC-937 §1.8).

No `@pytest.mark.req` marker: this is correctness of the repository's own source text, not
evidence for a numbered platform requirement -- the same reasoning
`tests/test_notes_move_citations.py` and `tests/test_file_census.py` give.
"""

from __future__ import annotations

import ast
import importlib.util
import io
import pathlib
import re
import subprocess
import sys
import token as _token
import tokenize
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCID_MODULE_PATH = ROOT / "scripts" / "_docid.py"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load_docid() -> types.ModuleType:
    """Load `scripts/_docid.py` by path -- `scripts/` is not a package."""
    if not DOCID_MODULE_PATH.exists():
        raise ModuleNotFoundError(f"No module named '_docid': not found at {DOCID_MODULE_PATH}")
    spec = importlib.util.spec_from_file_location("_docid_under_test", DOCID_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_docid = _load_docid()

#: Files whose concatenated document paths are *fixture data*, not citations: the path is
#: written to a synthetic tree built in `tmp_path` and names a pre-migration basename that
#: deliberately does not exist in this repository. Named file by file, with the reason, so
#: the exemption cannot widen into a directory the way a `tests/`-shaped rule would.
FIXTURE_PATH_SOURCES: dict[str, str] = {
    "tests/test_audit_docs_w37_11_ceiling.py": (
        "builds two synthetic `REDIRECTS.csv` allocations whose rows are the basenames the "
        "one-step test measured on `e6eb278`/`394a0d7`; those files are the migration's "
        "*inputs* and do not exist in the migrated tree, which is the point of the fixture"
    ),
}

#: `docs/<family-dir>/<PREFIX>-<padded>-<slug>.md`, with the prefix alternation and the
#: padding width read from `_docid` rather than written out here.
DOCUMENT_PATH_RE = re.compile(
    r"^docs/[a-z_]+/(?:"
    + "|".join(re.escape(p) for p in _docid.FAMILY_PREFIXES)
    + r")-\d{"
    + str(_docid.PAD_WIDTH)
    + r"}-[^\s]*\.md$"
)


# --- part 1: the mechanism ---------------------------------------------------------------

_WHOLE = (
    '"docs/rulings/RL-01060-check-36-is-one-rule-at-two-times-with-d-and-must-carry-'
    'd-s-disclosed-classes.md"'
)


def test_implicit_concatenation_is_value_preserving() -> None:
    """Adjacent literals fold to the byte-for-byte value the single literal carried."""
    split = (
        '"docs/rulings/RL-01060-check-36-is-one-rule-at-two-times-with-d-and-must-carry-"\n'
        '"d-s-disclosed-classes.md"'
    )
    assert ast.literal_eval(_WHOLE) == ast.literal_eval(f"({split})")


@pytest.mark.parametrize(
    ("name", "broken"),
    [
        # A newline written *into* the literal -- what wrapping the prose would do.
        (
            "newline inside the literal",
            '"docs/rulings/RL-01060-check-36-is-one-rule-at-two-times-with-d-and-must-carry-\\n"\n'
            '"d-s-disclosed-classes.md"',
        ),
        # A character lost at the seam -- what a hand-split gets wrong.
        (
            "character dropped at the seam",
            '"docs/rulings/RL-01060-check-36-is-one-rule-at-two-times-with-d-and-must-carry"\n'
            '"d-s-disclosed-classes.md"',
        ),
    ],
)
def test_a_split_that_is_not_value_preserving_fails_the_round_trip(name: str, broken: str) -> None:
    """The round-trip above can fail -- these two deliberately broken splits make it."""
    assert ast.literal_eval(_WHOLE) != ast.literal_eval(f"({broken})"), name


# --- part 2: the corpus -------------------------------------------------------------------


def _tracked_python_files() -> list[pathlib.Path]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z", "*.py"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [ROOT / rel for rel in out.split("\0") if rel]


def _concatenated_literals(source: str) -> list[tuple[int, str]]:
    """Every run of two or more adjacent STRING tokens, as (line, folded value)."""
    significant = [
        tok
        for tok in tokenize.generate_tokens(io.StringIO(source).readline)
        if tok.type
        not in (_token.NL, _token.NEWLINE, _token.COMMENT, _token.INDENT, _token.DEDENT)
    ]
    found: list[tuple[int, str]] = []
    run: list[tokenize.TokenInfo] = []
    for tok in [*significant, None]:
        if tok is not None and tok.type == _token.STRING:
            run.append(tok)
            continue
        if len(run) >= 2:
            pieces = " ".join(t.string for t in run)
            try:
                value = ast.literal_eval(f"({pieces})")
            except (ValueError, SyntaxError):
                run = []
                continue
            if isinstance(value, str):
                found.append((run[0].start[0], value))
        run = []
    return found


def test_every_split_document_path_names_a_file_that_exists() -> None:
    """A concatenated literal whose value is a document path must resolve in the tree."""
    files = _tracked_python_files()
    assert files, "git ls-files returned no Python sources -- the corpus is wrong"

    checked = 0
    missing: list[str] = []
    exempt_seen: set[str] = set()
    for path in files:
        rel = str(path.relative_to(ROOT))
        if rel in FIXTURE_PATH_SOURCES:
            exempt_seen.add(rel)
            continue
        try:
            source = path.read_text()
        except (OSError, UnicodeDecodeError):  # pragma: no cover -- no such file today
            continue
        try:
            literals = _concatenated_literals(source)
        except (tokenize.TokenError, SyntaxError):  # pragma: no cover -- no such file today
            continue
        for lineno, value in literals:
            if not DOCUMENT_PATH_RE.match(value):
                continue
            checked += 1
            if not (ROOT / value).exists():
                missing.append(f"{rel}:{lineno}: {value}")

    assert checked, (
        "no implicitly-concatenated governed-document path was found in any tracked "
        "Python source -- the predicate has stopped matching what it was written for, "
        "so a silent pass here would mean nothing"
    )
    assert not missing, (
        "an implicitly-concatenated document path does not resolve in the tree; the "
        "split lost or altered characters:\n  " + "\n  ".join(missing)
    )
    # A dead exemption is a statement that goes on reading true after it stopped being the
    # reason, so the set is held to the files that are actually still there.
    assert exempt_seen == set(FIXTURE_PATH_SOURCES), (
        "FIXTURE_PATH_SOURCES names a file that is no longer tracked: "
        f"{sorted(set(FIXTURE_PATH_SOURCES) - exempt_seen)}"
    )
