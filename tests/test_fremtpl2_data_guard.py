"""FD 8194: a test that reaches the freMTPL2 data carries a data-present guard.

`examples/fremtpl2/data` is fetched (sha256-pinned) and gitignored, so CI never has it. A test
that reads it unguarded passes on a developer's box and fails in CI: #1361's WF-701 journey did,
through a helper chain (`_run_in_process` -> `_full_level_world` -> `journey.portfolio_policies`
-> `seed.build_csv` -> `to_csv(DATA_DIR/...)`), with no path literal in the test at all.

The check is static and DB-free. Per test function it takes the **closure** of what that function
reaches inside its own file (called helpers, fixtures named in its parameters, the module level),
and asks two questions of the closure:

* **Reach.** Does it name a *data reader*, a path literal for the data, or a module-level alias
  of the data directory? The readers are **derived** from `examples/fremtpl2/*.py` (every
  function that touches `DATA_DIR` or `to_csv`, and, transitively, every function that calls
  one), so a new helper added to the example is covered without editing this file.
* **Guard.** Does it carry (a) an `if <...>.exists...: pytest.skip(...)`, the pattern
  `packages/pricing-core/tests/test_glm_scalar_predict.py` uses, (b) a `skipif` mark naming
  `.exists`, or (c) a redirect of `DATA_DIR` to synthetic files, which then reads no fetched data?

A name that merely *looks* like a guard (a comment, a string, an `.exists()` with no skip) is not
one: the guard is read from the AST, and the tests below feed it those shapes.
"""

from __future__ import annotations

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "fremtpl2"

#: Identifiers that are themselves the data directory or its reader, before derivation.
_SEED_READER_NAMES = frozenset({"DATA_DIR", "to_csv"})
_DATA_FILE_MARKERS = (".arff", "freMTPL2")


def _names(node: ast.AST) -> set[str]:
    """Every identifier and attribute name under `node` (a call `j.f()` yields `j` and `f`)."""
    found: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            found.add(sub.id)
        elif isinstance(sub, ast.Attribute):
            found.add(sub.attr)
        elif isinstance(sub, ast.arg):
            found.add(sub.arg)  # a fixture is reached by naming it as a parameter
    return found


def _loaded(node: ast.AST) -> set[str]:
    """The names `node` uses: a Load-context name or an attribute, not a binding or a parameter."""
    return {
        s.id if isinstance(s, ast.Name) else s.attr
        for s in ast.walk(node)
        if (isinstance(s, ast.Name) and isinstance(s.ctx, ast.Load)) or isinstance(s, ast.Attribute)
    }


def _strings(node: ast.AST) -> list[str]:
    return [
        s.value for s in ast.walk(node) if isinstance(s, ast.Constant) and isinstance(s.value, str)
    ]


def _functions(tree: ast.AST) -> dict[str, list[ast.AST]]:
    out: dict[str, list[ast.AST]] = {}
    for sub in ast.walk(tree):
        if isinstance(sub, ast.FunctionDef | ast.AsyncFunctionDef):
            out.setdefault(sub.name, []).append(sub)
    return out


def data_readers(sources: dict[str, str]) -> set[str]:
    """The names of the example's functions that read the data, directly or through a caller."""
    functions: dict[str, set[str]] = {}
    homes: dict[str, set[str]] = {}
    for module, source in sources.items():
        for name, nodes in _functions(ast.parse(source)).items():
            functions.setdefault(name, set()).update(*(_names(node) for node in nodes))
            homes.setdefault(name, set()).add(module)
    # A name defined in two example modules (`main`, `run`) cannot be told apart from a test's
    # own `main` by name alone, and one such name would drag every caller of it into the set.
    # `main` is the CLI entry point (a test reaches it through a subprocess, not by name).
    for name in [n for n, where in homes.items() if len(where) > 1 or n == "main"]:
        del functions[name]
    readers = {name for name, used in functions.items() if used & _SEED_READER_NAMES}
    while True:
        more = {name for name, used in functions.items() if used & readers} - readers
        if not more:
            return readers
        readers |= more


def _names_the_data_path(node: ast.AST) -> bool:
    """A `fremtpl2/data` literal, or one expression that joins `"data"` to a freMTPL2 file name.

    `".arff"` alone is not enough: a test that writes its own `sample.arff` under `tmp_path`
    names the extension and reads no fetched data."""
    asserted = {id(c) for a in ast.walk(node) if isinstance(a, ast.Assert) for c in ast.walk(a)}
    for sub in ast.walk(node):
        if id(sub) in asserted:
            continue  # a path quoted in an assertion (an expected message) is not a read of it
        if (
            isinstance(sub, ast.Constant)
            and isinstance(sub.value, str)
            and "fremtpl2/data" in sub.value
        ):
            return True
        if isinstance(sub, ast.BinOp):
            parts = _strings(sub)
            if "data" in parts and any(m in p for p in parts for m in _DATA_FILE_MARKERS):
                return True
    return False


def _module_level(tree: ast.Module) -> list[ast.stmt]:
    return [
        s
        for s in tree.body
        if not isinstance(s, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
    ]


def _data_aliases(statements: list[ast.stmt], *, sibling_data: bool) -> set[str]:
    """Module-level names bound to a path into the data directory (`ARFF_DIR = ... / "data"`).

    `__file__ / "data"` is the freMTPL2 data only for a file beside it (`sibling_data`); any
    other test's own `data/` directory is its own."""
    aliases: set[str] = set()
    for statement in statements:
        if not (isinstance(statement, ast.Assign) and "data" in _strings(statement.value)):
            continue
        named = "fremtpl2" in _strings(statement.value)
        beside = sibling_data and "__file__" in _names(statement.value)
        if named or beside:
            aliases |= {t.id for t in statement.targets if isinstance(t, ast.Name)}
    return aliases


def _is_guard(node: ast.AST) -> bool:
    """`if ….exists…: pytest.skip(…)`, a `skipif` naming `.exists`, or a `DATA_DIR` redirect."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.If) and "exists" in _names(sub.test):
            skips = [c for stmt in sub.body for c in ast.walk(stmt) if isinstance(c, ast.Call)]
            if any("skip" in _names(c.func) for c in skips):
                return True
        skipif = isinstance(sub, ast.Call) and "skipif" in _names(sub.func)
        if skipif and any("exists" in _names(arg) for arg in sub.args):  # type: ignore[attr-defined]
            return True
        redirect = isinstance(sub, ast.Call) and "setattr" in _names(sub.func)
        if redirect and "DATA_DIR" in _strings(sub):
            return True
    return False


def unguarded_tests(source: str, readers: set[str], *, sibling_data: bool = False) -> list[str]:
    """The `test_*` functions of `source` whose closure reaches the data and holds no guard."""
    tree = ast.parse(source)
    functions = _functions(tree)
    module_level = _module_level(tree)
    aliases = _data_aliases(module_level, sibling_data=sibling_data)
    module_nodes: list[ast.AST] = list(module_level)

    def closure(start: str) -> list[ast.AST]:
        seen = {start}
        nodes: list[ast.AST] = []
        queue = [start]
        while queue:
            for node in functions.get(queue.pop(), []):
                nodes.append(node)
                for name in _names(node):
                    if name in functions and name not in seen:
                        seen.add(name)
                        queue.append(name)
        return nodes

    def reaches(nodes: list[ast.AST]) -> bool:
        used = set().union(*(_loaded(n) for n in nodes)) if nodes else set()
        literal = any(_names_the_data_path(n) for n in nodes)
        return bool(used & (readers | aliases | {"DATA_DIR"})) or literal

    unguarded: list[str] = []
    for name in functions:
        if not name.startswith("test_"):
            continue
        nodes = closure(name) + module_nodes
        if reaches(nodes) and not any(_is_guard(n) for n in nodes):
            unguarded.append(name)
    return sorted(set(unguarded))


def _example_sources() -> dict[str, str]:
    return {
        p.name: p.read_text(encoding="utf-8")
        for p in sorted(EXAMPLE.glob("*.py"))
        # `fetch.py` is the downloader that *writes* the data directory, not a reader of it.
        if not p.name.startswith("test_") and p.name != "fetch.py"
    }


def _test_files() -> list[pathlib.Path]:
    roots = [
        ROOT / "backend" / "tests",
        *sorted((ROOT / "packages").glob("*/tests")),
        ROOT / "tests",
        EXAMPLE,
    ]
    return sorted(
        p
        for root in roots
        for p in root.glob("test_*.py")
        if p.resolve() != pathlib.Path(__file__).resolve()
    )


def test_every_test_that_reaches_the_fremtpl2_data_carries_the_guard() -> None:
    """The invariant, over the real tree. A failure names `file::test`."""
    readers = data_readers(_example_sources())
    assert {
        "build_csv",
        "build_portfolio_csv",
    } <= readers  # the derivation found the seed's readers
    offenders = [
        f"{path.relative_to(ROOT)}::{name}"
        for path in _test_files()
        for name in unguarded_tests(
            path.read_text(encoding="utf-8"), readers, sibling_data=path.parent == EXAMPLE
        )
    ]
    assert not offenders, (
        "reads examples/fremtpl2/data without a data-present guard (CI never fetches it): "
        + ", ".join(offenders)
    )


# --- the checker on fixtures: it must fail on the shapes that bit, and pass on the guarded ones ---

_EXAMPLE_FIXTURE = {
    "seed.py": (
        "DATA_DIR = 1\ndef build_csv(rows):\n    return to_csv(DATA_DIR / 'freMTPL2freq.arff')\n"
    ),
    "journey.py": (
        "def portfolio_policies():\n    return seed.build_csv(5)\ndef unrelated():\n    return 1\n"
    ),
}
_READERS = data_readers(_EXAMPLE_FIXTURE)

# #1361's shape: the test names no path and no reader; the read is three calls away.
_HELPER_CHAIN = """
import pytest

def _world():
    return j.portfolio_policies()

def _run_in_process():
    return _world()

def test_the_journey():
    _run_in_process()
"""


def test_the_readers_are_derived_through_callers() -> None:
    assert {"build_csv", "portfolio_policies"} == _READERS


def test_a_read_through_a_helper_chain_without_a_guard_is_caught() -> None:
    assert unguarded_tests(_HELPER_CHAIN, _READERS) == ["test_the_journey"]


def test_a_direct_unguarded_reference_is_caught() -> None:
    literal = "def test_a():\n    open('examples/fremtpl2/data/freMTPL2freq.arff')\n"
    alias = "D = Path(__file__).parent / 'data'\ndef test_b():\n    D.glob('*')\n"
    assert unguarded_tests(literal, _READERS) == ["test_a"]
    assert unguarded_tests(alias, _READERS, sibling_data=True) == ["test_b"]
    assert unguarded_tests(alias, _READERS) == []  # another test's own data/ directory


def test_a_skip_guard_anywhere_in_the_closure_passes() -> None:
    guarded = _HELPER_CHAIN.replace(
        "def _world():",
        "def _world():\n    if not DATA.exists():\n        pytest.skip('not fetched')",
    )
    assert unguarded_tests(guarded, _READERS) == []
    via_fixture = (
        "import pytest\n@pytest.fixture\ndef scratch():\n    if not D.exists():\n"
        "        pytest.skip('x')\n    return 1\n"
        "def test_a(scratch):\n    seed.build_csv(1)\n"
    )
    assert unguarded_tests(via_fixture, _READERS) == []


def test_a_redirect_to_synthetic_data_passes() -> None:
    redirected = (
        "def test_a(monkeypatch, tmp_path):\n"
        "    monkeypatch.setattr(seed, 'DATA_DIR', tmp_path)\n    seed.build_csv(1)\n"
    )
    assert unguarded_tests(redirected, _READERS) == []


def test_things_that_only_look_like_a_guard_are_not_one() -> None:
    comment = "def test_a():\n    # pytest.skip if .exists()\n    seed.build_csv(1)\n"
    no_skip = "def test_a():\n    if D.exists():\n        pass\n    seed.build_csv(1)\n"
    wrong_skip = "def test_a():\n    if flag:\n        pytest.skip('x')\n    seed.build_csv(1)\n"
    for source in (comment, no_skip, wrong_skip):
        assert unguarded_tests(source, _READERS) == ["test_a"], source


def test_a_test_that_reaches_nothing_is_not_flagged() -> None:
    assert unguarded_tests("def test_a():\n    assert unrelated() == 1\n", _READERS) == []
