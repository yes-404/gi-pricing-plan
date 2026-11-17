"""The approval guard's static checks (WK-674 Slice 2a, PL-1303 Acceptance 5 and 7).

Three scans over `backend/src`, `backend/migrations` and `examples/`, each red first on a
planted violation, plus the allowance pinned as a literal. `backend/tests/` is exempt, and
nothing else. The scans take `{path: source}` so a test can plant a violation in a copy
without touching the tree.

A reader migration may only read the flag: its strings are joined and matched
case-insensitively, so a name assembled from literal pieces, an f-string's pieces or a
`%`-format's template are read too. What the scan still cannot see (a name that is not in any
literal) is listed in `_flag_beyond_a_read`'s docstring, and for the other files the literal
scan's residual is named in RL-1301 A.4.4 and PL-1303 Acceptance 11, not hidden.
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

#: **Reader migrations, pinned as a literal.** A file named here may carry the flag literal
#: only inside a `current_setting('<flag>', …)` read; any form that sets it is refused, as
#: it is for every other file. A read in a file not named here is refused like any other
#: mention of the flag. Adding a reader is a change to this list, by file name.
READER_MIGRATIONS = frozenset(
    {
        GUARD_MIGRATION,
        "backend/migrations/versions/e5b2a7d94c13_rating_version_content_guard.py",
    }
)

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


def _docstring_ids(tree: ast.AST) -> set[int]:
    return {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }


_FLAG_READ = re.compile(r"current_setting\(\s*'" + re.escape(FLAG) + r"'", re.IGNORECASE)
_FLAG_NAME = FLAG.partition(".")[2]
#: A message that names the Python context manager, `approval_decision()`, is not the setting.
_CONTEXT_MANAGER_NAME = re.compile(r"(?<!app\.)(?<!app\.\n)" + _FLAG_NAME + r"\(\)", re.IGNORECASE)
#: **A reader migration contains no data-changing statement and no session setting at all: it
#: only reads.** Refused, whatever the name or the spelling: `set_config`; a `SET` statement (the
#: word followed by `LOCAL`/`SESSION`, a parenthesis, a `ROLE`/`SCHEMA`/`TIME ZONE`-style keyword,
#: or a name and `=`/`TO`; so `UPDATE ... SET column = ...` is one, and prose such as "set by" is
#: not); `INSERT INTO`, `DELETE FROM`, `TRUNCATE`, `MERGE INTO`, `COPY ... FROM/TO`; and a
#: plpgsql or SQL `EXECUTE` of anything but `FUNCTION`/`PROCEDURE` (the trigger DDL's own).
_NO_WRITE_NO_SETTING = re.compile(
    r"\bset_config\b"
    r"|\bSET\s*\("
    r"|\bSET\s+(?:LOCAL|SESSION|ROLE|SCHEMA|TIME\s+ZONE|CONSTRAINTS|TRANSACTION|NAMES)\b"
    r"|\bSET\s+[^\s=;]+\s*(?:=|\bTO\b)"
    r"|\bINSERT\s+INTO\b|\bDELETE\s+FROM\b|\bTRUNCATE\b|\bMERGE\s+INTO\b"
    r"|\bCOPY\s+\S+\s+(?:FROM|TO)\b"
    r"|\bEXECUTE\b(?!\s+(?:FUNCTION|PROCEDURE)\b)",
    re.IGNORECASE,
)


def _flag_beyond_a_read(source: str) -> bool:
    """True when a reader migration breaks the rule: a reader migration contains no data-changing
    statement and no session setting at all: it only reads (`_NO_WRITE_NO_SETTING`), and it names
    the flag only in a `current_setting` read.

    The strings that are not docstrings (every `Constant`, so the pieces of an f-string and of a
    concatenation too, in source order) are joined, once with a newline between them and once with
    nothing, and read case-insensitively, as Postgres reads a setting name. Three refusals: a
    statement `_NO_WRITE_NO_SETTING` names; **any** occurrence of the flag's name once the plain
    `current_setting('<flag>', …)` reads and a message's `approval_decision()` (the context
    manager, never preceded by `app.`) are removed; and, together, that makes a split or escaped
    spelling of the name refused by the statement around it, whatever the name.

    **What this still cannot see** (it reads literals, not values; each is what review of the
    reader list, which is pinned by file name, exists for):

    1. a keyword or name assembled so that its pieces are not adjacent string literals (a
       `chr()` or `bytes` assembly, or pieces separated by another literal);
    2. a name or a statement read from a column, an environment variable or a function argument;
    3. a statement composed by a helper in another file;
    4. a comment (a comment is not executed);
    5. the flag name built at run time from a variable defined in another module (an imported
       constant or a value computed there), which no literal of the reader file contains;
    6. **`op.execute(...)` of a string built from parts in Python** (an f-string, `.format`, a
       helper's return value): the literals are read, the substituted values are not. Both real
       readers do this today, for DDL only: `a9f3c6d21b87_approval_guard.py`
       (`op.execute(create_trigger_sql(table))`, ``op.execute(f"DROP TRIGGER ... {table}")``) and
       `e5b2a7d94c13_rating_version_content_guard.py` (`_RV_TRIGGER.format(...)`, f-strings over
       `CHECK_NAME` and `known`), so the rule cannot refuse it. A plpgsql `EXECUTE` is refused.
    """
    tree = ast.parse(source)
    docstrings = _docstring_ids(tree)
    pieces = sorted(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstrings
        ),
        key=lambda node: (node.lineno, node.col_offset),
    )
    return any(
        _NO_WRITE_NO_SETTING.search(text) is not None
        or _FLAG_NAME in _CONTEXT_MANAGER_NAME.sub("", _FLAG_READ.sub("", text)).lower()
        for text in (
            "\n".join(str(node.value) for node in pieces),
            "".join(str(node.value) for node in pieces),
        )
    )


def _flag_literal_outside_its_owners(sources: dict[str, str]) -> list[str]:
    bad = []
    for path, source in sources.items():
        if path in READER_MIGRATIONS:
            if _flag_beyond_a_read(source):
                bad.append(path)
        elif FLAG in source.lower() and path != DECISION_MODULE:
            bad.append(path)
    return bad


def _session_level_flag_sets(sources: dict[str, str]) -> list[str]:
    """A session-level `SET` (no `LOCAL`) or `set_config(…, false)` on the flag: it would
    leak across the pool. Checked in the two files that may name the flag at all."""
    bad = []
    for path, source in sources.items():
        if FLAG not in source.lower():
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


_SETS_REPLICATION_ROLE = re.compile(
    r"\bSET\s+(LOCAL\s+|SESSION\s+)?session_replication_role\s*(=|\bTO\b)"
    r"|set_config\(\s*'session_replication_role'"
    r"|\bALTER\s+(ROLE|DATABASE|SYSTEM)\b[^;]*\bSET\s+session_replication_role\s*(=|\bTO\b)",
    re.IGNORECASE,
)


def _replication_role_sql(sources: dict[str, str]) -> list[str]:
    """SQL that suspends every user trigger, the guard included, in a string that is not a
    docstring. Three shapes write the parameter: `SET [LOCAL|SESSION] session_replication_role
    = | TO`, `set_config('session_replication_role', …)`, and the persistent `ALTER
    ROLE|DATABASE|SYSTEM … SET session_replication_role = | TO`. A read
    (`has_parameter_privilege`, `current_setting`, `pg_settings`) or a message that merely
    names the parameter is not refused."""
    bad = []
    for path, source in sources.items():
        tree = ast.parse(source)
        docstrings = _docstring_ids(tree)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and _SETS_REPLICATION_ROLE.search(node.value)
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
def test_the_flag_literal_lives_only_in_the_decision_module_and_the_reader_migrations() -> None:
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


_READER = "backend/migrations/versions/e5b2a7d94c13_rating_version_content_guard.py"


@pytest.mark.req("FR-351")
def test_the_reader_migrations_are_pinned_by_file_name() -> None:
    assert GUARD_MIGRATION in READER_MIGRATIONS
    assert _READER in READER_MIGRATIONS
    assert len(READER_MIGRATIONS) == 2
    assert _sources().keys() >= READER_MIGRATIONS


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    "sql",
    [
        f"SELECT set_config('{FLAG}', 'on', true)",
        f"SET LOCAL {FLAG} = 'on'",
        f"SET {FLAG} = 'on'",
    ],
    ids=["set_config_local", "set_local", "set"],
)
def test_a_planted_set_of_the_flag_in_a_reader_migration_is_refused(sql: str) -> None:
    planted = _plant(_READER, _sources()[_READER] + f'\nBAD = "{sql}"\n')
    assert _flag_literal_outside_its_owners(planted) == [_READER]


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    "statement",
    [
        "BAD = \"SET LOCAL APP.APPROVAL_DECISION = 'on'\"",
        "BAD = \"SELECT set_config('App.Approval_Decision', 'on', true)\"",
        'BAD = "SET LOCAL app." + "approval_decision" + " = \'on\'"',
        'BAD = "SET LOCAL app.approval_%s = \'on\'" % "decision"',
        'N = "approval_decision"\nBAD = f"SET LOCAL app.{N} = \'on\'"',
    ],
    ids=[
        "upper_case_set_local",
        "mixed_case_set_config",
        "split_literal",
        "percent_format",
        "fstring",
    ],
)
def test_a_reader_migration_that_sets_the_flag_by_any_spelling_is_refused(statement: str) -> None:
    planted = _plant(_READER, _sources()[_READER] + f"\n{statement}\n")
    assert _flag_literal_outside_its_owners(planted) == [_READER]


_SPLIT_FORMS = {
    "split_set_local": 'BAD = "SET LOCAL " + "app" + "." + "approval_" + "decision"',
    "split_inside_set_config": (
        'BAD = "SELECT set_config(\'" + "app" + "." + "approval_" + "decision" '
        "+ \"', 'on', true)\""
    ),
    "spaced_name": 'BAD = "SET LOCAL app . approval_ " + "decision"',
    "escaped_name": "BAD = " + repr("SELECT set_config(E'app.approval\\x5fdecision', 'on', true)"),
    "unicode_escaped_name": "BAD = "
    + repr('SET LOCAL U&"app".U&"approval\\005fdecision" = \'on\''),
}


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("statement", list(_SPLIT_FORMS.values()), ids=list(_SPLIT_FORMS))
def test_a_reader_migration_with_a_split_or_escaped_flag_name_is_refused(statement: str) -> None:
    """The rule is not a spelling of the flag: a reader contains no `SET` statement and no
    `set_config` at all, so a name split across literals or escaped in SQL is refused by the
    statement around it."""
    planted = _plant(_READER, _sources()[_READER] + f"\n{statement}\n")
    assert _flag_literal_outside_its_owners(planted) == [_READER]


_NOT_A_READER = {
    "update_set_column": "UPDATE rating_versions SET change_summary = 'x' WHERE false",
    "insert": "INSERT INTO rating_versions (id) VALUES (gen_random_uuid())",
    "delete": "DELETE FROM rating_versions WHERE false",
    "truncate": "TRUNCATE rating_versions",
    "set_config_other_name": "SELECT set_config('app.something_else', 'x', true)",
    "set_role": "SET LOCAL ROLE gip_owner",
    "plpgsql_execute": "DO $$ BEGIN EXECUTE format('SELECT %s', 1); END $$",
    "plpgsql_execute_literal": "DO $$ BEGIN EXECUTE 'SELECT 1'; END $$",
}


@pytest.mark.req("FR-351")
@pytest.mark.parametrize("sql", list(_NOT_A_READER.values()), ids=list(_NOT_A_READER))
def test_a_reader_migration_contains_no_data_changing_statement_and_no_session_setting(
    sql: str,
) -> None:
    """A reader migration contains no data-changing statement and no session setting at all: it
    only reads. `UPDATE ... SET column = ...` is refused in a reader too: a migration that
    writes is not a reader. Nor does a reader run a built string (`EXECUTE`)."""
    planted = _plant(_READER, _sources()[_READER] + f"\nBAD = {sql!r}\n")
    assert _flag_literal_outside_its_owners(planted) == [_READER]


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    "sql",
    [
        "CREATE TRIGGER t BEFORE INSERT OR UPDATE OF status ON x FOR EACH ROW "
        "EXECUTE FUNCTION f('a')",
        "RAISE EXCEPTION 'the decision flag set by approval_decision()'",
        "SELECT current_setting('app.approval_decision', true)",
    ],
    ids=["trigger_ddl", "prose_set_by", "plain_read"],
)
def test_what_a_reader_may_contain_is_not_refused(sql: str) -> None:
    assert _flag_literal_outside_its_owners({_READER: f"BAD = {sql!r}\n"}) == []


@pytest.mark.req("FR-351")
def test_an_upper_case_flag_in_a_file_that_is_not_a_reader_is_refused() -> None:
    other = "backend/src/app/x.py"
    sql = f"Q = \"SET LOCAL {FLAG.upper()} = 'on'\"\n"
    assert _flag_literal_outside_its_owners(_plant(other, sql)) == [other]
    assert _session_level_flag_sets({other: f"Q = \"SET {FLAG.upper()} = 'on'\"\n"}) != []


@pytest.mark.req("FR-351")
def test_a_planted_read_in_a_migration_not_on_the_list_is_refused() -> None:
    other = "backend/migrations/versions/zzzzzzzzzzzz_other.py"
    source = f"Q = \"SELECT current_setting('{FLAG}', true)\"\n"
    assert _flag_literal_outside_its_owners(_plant(other, source)) == [other]


@pytest.mark.req("FR-351")
def test_a_read_in_a_listed_reader_migration_is_not_refused() -> None:
    source = f"Q = \"SELECT current_setting('{FLAG}', true) IS DISTINCT FROM 'on'\"\n"
    assert _flag_literal_outside_its_owners({_READER: source}) == []


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
    "sql",
    [
        "SET session_replication_role = replica",
        "set local session_replication_role to replica",
        "SELECT set_config('session_replication_role', 'replica', false)",
        "ALTER ROLE gip_app_login SET session_replication_role = replica",
        "ALTER DATABASE gip SET session_replication_role = replica",
    ],
)
def test_every_statement_that_sets_the_replication_role_is_refused(sql: str) -> None:
    planted = {"backend/src/app/x.py": f"Q = {sql!r}\n"}
    assert _replication_role_sql(planted) == ["backend/src/app/x.py:1"]


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    "text",
    [
        "SELECT has_parameter_privilege(current_user, 'session_replication_role', 'SET')",
        "the connection may set session_replication_role, which switches the triggers off",
    ],
)
def test_a_read_or_a_message_naming_the_replication_role_is_not_refused(text: str) -> None:
    planted = {"backend/src/app/x.py": f"Q = {text!r}\n"}
    assert _replication_role_sql(planted) == []


@pytest.mark.req("FR-351")
@pytest.mark.parametrize(
    "call", ["asyncio.create_task(g())", "asyncio.gather(g())", "loop.run_in_executor(None, g)"]
)
def test_a_planted_task_inside_the_block_is_refused(call: str) -> None:
    source = f"async def f(session):\n    async with approval_decision(session):\n        {call}\n"
    planted = _plant("backend/src/app/x.py", source)
    assert len(_context_escapes(planted)) == 1
