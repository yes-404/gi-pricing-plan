"""The approval guard's static checks (WK-674 Slice 2a, PL-1303 Acceptance 5 and 7).

Three scans over `backend/src`, `backend/migrations` and `examples/`, each red first on a
planted violation, plus the allowance pinned as a literal. `backend/tests/` is exempt, and
nothing else. The scans take `{path: source}` so a test can plant a violation in a copy
without touching the tree.

A literal assembled at run time (concatenated, or in an f-string) evades the literal scan;
that residual is named in RL-1301 A.4.4 and PL-1303 Acceptance 11, not hidden.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SCANNED = ("backend/src", "backend/migrations", "examples")

DECISION_MODULE = "backend/src/app/platform/approvals.py"
GUARD_MIGRATION = "backend/migrations/versions/a9f3c6d21b87_approval_guard.py"

#: The two sanctioned sites of the decision path.
SANCTIONED_SITES = frozenset(
    {
        ("backend/src/app/platform/approvals.py", "decide"),
        ("backend/src/app/api/approvals.py", "_carry_to_the_artifact"),
    }
)

#: **The allowance, pinned as a literal and shrink-only** (RL-1301 A.4.5). A site enters
#: `approval_decision()` around a write of `approved` that is not a decision. Removing an
#: entry is a change; adding one is refused by the test below until a ruling adds it here.
ALLOWANCE_SITES = frozenset(
    {
        # Temporary: pending OQ 9987 (working id), per RL-1301 A.4.5.
        ("backend/src/app/platform/validation_rules.py", "replace_rule_set"),
        # Legitimate seed writers.
        ("backend/src/app/platform/validation_rules.py", "seed_builtin_rules"),
    }
)

FLAG = "app.approval_decision"


def _sources(root: Path = _ROOT) -> dict[str, str]:
    out: dict[str, str] = {}
    for top in _SCANNED:
        for path in sorted((root / top).rglob("*.py")):
            if "__pycache__" not in path.parts:
                out[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
    return out


def _is_decision_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return (isinstance(func, ast.Name) and func.id == "approval_decision") or (
        isinstance(func, ast.Attribute) and func.attr == "approval_decision"
    )


def _entries(sources: dict[str, str]) -> tuple[set[tuple[str, str]], list[str]]:
    """Every `async with …approval_decision(…)`, by (file, enclosing function); and every
    other use of the name as a call, which is refused outright."""
    entered: set[tuple[str, str]] = set()
    stray: list[str] = []
    for path, source in sources.items():
        tree = ast.parse(source)
        parents = {
            child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)
        }
        for node in ast.walk(tree):
            if not _is_decision_call(node):
                continue
            item = parents.get(node)
            if not (
                isinstance(item, ast.withitem) and isinstance(parents.get(item), ast.AsyncWith)
            ):
                stray.append(
                    f"{path}:{node.lineno}: approval_decision() called outside `async with`"
                )
                continue
            fn = parents.get(item)
            while fn is not None and not isinstance(fn, ast.AsyncFunctionDef | ast.FunctionDef):
                fn = parents.get(fn)
            entered.add((path, fn.name if fn is not None else "<module>"))
    return entered, stray


def _unsanctioned_entries(sources: dict[str, str]) -> list[str]:
    entered, stray = _entries(sources)
    allowed = SANCTIONED_SITES | ALLOWANCE_SITES
    return stray + [f"{p}::{fn}" for p, fn in sorted(entered - allowed)]


def _flag_literal_outside_its_owners(sources: dict[str, str]) -> list[str]:
    return [
        path
        for path, source in sources.items()
        if FLAG in source and path not in (DECISION_MODULE, GUARD_MIGRATION)
    ]


def _session_level_flag_sets(sources: dict[str, str]) -> list[str]:
    """A session-level `SET` (no `LOCAL`) or `set_config(…, false)` on the flag: it would
    leak across the pool. Checked in the two files that may name the flag at all."""
    bad = []
    for path, source in sources.items():
        if FLAG not in source:
            continue
        for match in re.finditer(r"\bSET\s+(?!LOCAL\b)" + re.escape(FLAG), source, re.IGNORECASE):
            bad.append(f"{path}: session-level SET at offset {match.start()}")
        for match in re.finditer(
            r"set_config\(\s*['\"]" + re.escape(FLAG) + r"['\"]\s*,[^)]*,\s*false\s*\)",
            source,
            re.IGNORECASE,
        ):
            bad.append(f"{path}: set_config(..., false) at offset {match.start()}")
    return bad


def _replication_role_sql(sources: dict[str, str]) -> list[str]:
    """`session_replication_role` in a string that is not a docstring: SQL that suspends
    every user trigger, the guard included."""
    bad = []
    for path, source in sources.items():
        tree = ast.parse(source)
        docstrings = {
            id(node.body[0].value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
        }
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and "session_replication_role" in node.value
                and id(node) not in docstrings
            ):
                bad.append(f"{path}:{node.lineno}")
    return bad


_ESCAPES = frozenset({"create_task", "gather", "run_in_executor", "to_thread"})


def _context_escapes(sources: dict[str, str]) -> list[str]:
    """A task, gather or executor call lexically inside an `approval_decision()` block runs
    outside the transaction the flag is local to."""
    bad = []
    for path, source in sources.items():
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.AsyncWith):
                continue
            if not any(_is_decision_call(item.context_expr) for item in node.items):
                continue
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    name = (
                        inner.func.attr
                        if isinstance(inner.func, ast.Attribute)
                        else getattr(inner.func, "id", "")
                    )
                    if name in _ESCAPES:
                        bad.append(f"{path}:{inner.lineno}: {name} inside approval_decision()")
    return bad


# -- the tree as it is ------------------------------------------------------------------


@pytest.mark.req("FR-351")
def test_approval_decision_is_entered_only_at_the_sanctioned_and_allowance_sites() -> None:
    assert _unsanctioned_entries(_sources()) == []


@pytest.mark.req("FR-351")
def test_every_pinned_site_really_enters_the_context() -> None:
    """The literal lists what exists: an entry whose site no longer enters is stale, and
    removing the last allowance of a table is a migration that drops its `flag` argument."""
    entered, _ = _entries(_sources())
    assert entered == SANCTIONED_SITES | ALLOWANCE_SITES


@pytest.mark.req("FR-351")
def test_the_flag_literal_lives_only_in_the_decision_module_and_the_guard_migration() -> None:
    assert _flag_literal_outside_its_owners(_sources()) == []


@pytest.mark.req("FR-351")
def test_no_session_level_set_of_the_flag_anywhere() -> None:
    assert _session_level_flag_sets(_sources()) == []


@pytest.mark.req("FR-351")
def test_no_sql_string_sets_session_replication_role() -> None:
    assert _replication_role_sql(_sources()) == []


@pytest.mark.req("FR-351")
def test_no_task_or_executor_is_started_inside_an_approval_decision_block() -> None:
    assert _context_escapes(_sources()) == []


# -- red on a planted violation ---------------------------------------------------------


def _plant(path: str, source: str) -> dict[str, str]:
    return {**_sources(), path: source}


_PLANT_ENTRY = (
    "async def rogue(session):\n    async with approval_decision(session):\n        pass\n"
)


@pytest.mark.req("FR-351")
def test_a_planted_new_entry_site_is_refused() -> None:
    planted = _plant("backend/src/app/platform/rogue.py", _PLANT_ENTRY)
    assert _unsanctioned_entries(planted) == ["backend/src/app/platform/rogue.py::rogue"]


@pytest.mark.req("FR-351")
def test_a_planted_bare_call_outside_async_with_is_refused() -> None:
    planted = _plant("backend/src/app/x.py", "def f(session):\n    approval_decision(session)\n")
    assert any("outside `async with`" in m for m in _unsanctioned_entries(planted))


@pytest.mark.req("FR-351")
def test_a_planted_second_function_in_an_allowed_file_is_refused() -> None:
    """The allowance is by site, not by file: a new writer in `validation_rules.py` is
    still refused."""
    planted = _plant(
        "backend/src/app/platform/validation_rules.py",
        _sources()["backend/src/app/platform/validation_rules.py"] + "\n\n" + _PLANT_ENTRY,
    )
    assert _unsanctioned_entries(planted) == ["backend/src/app/platform/validation_rules.py::rogue"]


@pytest.mark.req("FR-351")
def test_a_planted_flag_literal_is_refused() -> None:
    planted = _plant("backend/src/app/x.py", f"SQL = \"SELECT set_config('{FLAG}', 'on', true)\"\n")
    assert _flag_literal_outside_its_owners(planted) == ["backend/src/app/x.py"]


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    "sql",
    [f"SET {FLAG} = 'on'", f"SELECT set_config('{FLAG}', 'on', false)"],
    ids=["set", "set_config_false"],
)
def test_a_planted_session_level_set_is_refused(sql: str) -> None:
    planted = _plant(DECISION_MODULE, _sources()[DECISION_MODULE] + f'\nBAD = "{sql}"\n')
    assert _session_level_flag_sets(planted) != []


@pytest.mark.req("FR-351")
def test_the_transaction_local_form_is_not_mistaken_for_a_violation() -> None:
    assert _session_level_flag_sets({"x.py": f"A = \"SET LOCAL {FLAG} = 'on'\"\n"}) == []
    assert (
        _session_level_flag_sets({"x.py": f"A = \"SELECT set_config('{FLAG}', 'on', true)\"\n"})
        == []
    )


@pytest.mark.req("FR-351")
def test_a_planted_replication_role_statement_is_refused_and_a_docstring_is_not() -> None:
    planted = _plant("backend/src/app/x.py", 'Q = "SET session_replication_role = replica"\n')
    assert _replication_role_sql(planted) == ["backend/src/app/x.py:1"]
    prose = _plant(
        "backend/src/app/y.py", 'def f():\n    """Mentions session_replication_role in prose."""\n'
    )
    assert _replication_role_sql(prose) == []


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    "call", ["asyncio.create_task(g())", "asyncio.gather(g())", "loop.run_in_executor(None, g)"]
)
def test_a_planted_task_inside_the_block_is_refused(call: str) -> None:
    source = f"async def f(session):\n    async with approval_decision(session):\n        {call}\n"
    planted = _plant("backend/src/app/x.py", source)
    assert len(_context_escapes(planted)) == 1
