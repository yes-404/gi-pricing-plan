"""A test that takes `caplog` must not build the app in its own body (#1894).

`create_app` calls `configure_logging` (`app/main.py`), which removes every root handler
(`app/observability/logging.py`), `caplog`'s handler included, so a negative assertion on
`caplog.text` or `caplog.records` afterwards passes over a log that was never captured. Importing
`app.worker.entrypoint` does the same at import time. The app belongs in a fixture the test takes
(`client`), built before `caplog` attaches, or the test reads `capsys`.

The scan is by AST over `backend/tests`. It flags a `test_*` taking `caplog` whose body reaches
`create_app` or `configure_logging`, directly or through module-local helpers that are not
fixtures (transitively), or imports `app.worker.entrypoint` inside the body or such a helper.
A name imported `as` another name is still the builder (`from app.main import create_app as
mk`); `usefixtures("caplog")` on the test counts as taking `caplog`.

**The scan's limits** (shapes it does not see; none is in the tree today):

- `importlib.import_module("app.worker.entrypoint")` or `importlib.reload(...)` of the entrypoint
- a helper defined in another module is not followed
- a helper passed as a callback (`run(_h)`) is not a call the scan sees
- `getattr(m, "create_app")(s)`: the builder is named by a string
- a positional-only `caplog` parameter (`def test_a(caplog, /)`)
- `usefixtures("caplog")` on a class or in a module `pytestmark`
- two classes in one module with a same-named helper share one entry (the scan keys by bare name)
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_TESTS = Path(__file__).resolve().parent
_BUILDERS = {"create_app", "configure_logging"}
_ENTRYPOINT = "app.worker.entrypoint"
_Func = ast.FunctionDef | ast.AsyncFunctionDef


def _takes_caplog(fn: _Func) -> bool:
    """`caplog` in the argument list, or named by a `usefixtures(...)` marker on the test."""
    if "caplog" in [a.arg for a in fn.args.args + fn.args.kwonlyargs]:
        return True
    return any(
        isinstance(d, ast.Call)
        and ast.unparse(d.func).endswith("usefixtures")
        and any(isinstance(a, ast.Constant) and a.value == "caplog" for a in d.args)
        for d in fn.decorator_list
    )


def _called(fn: _Func) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                names.add(f.id)
            elif isinstance(f, ast.Attribute):
                names.add(f.attr)
    return names


def _imports_entrypoint(fn: _Func) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.Import) and any(a.name == _ENTRYPOINT for a in node.names):
            return True
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod == _ENTRYPOINT or (
                mod == "app.worker" and any(a.name == "entrypoint" for a in node.names)
            ):
                return True
    return False


def _census(root: Path) -> tuple[int, list[str]]:
    """(caplog tests examined, offenders as `path:line::name`) over every `*.py` under `root`."""
    examined = 0
    offenders: list[str] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        funcs = {
            n.name: n
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
        }

        # `from m import create_app as mk`: the local name `mk` is the builder
        aliases = {
            a.asname
            for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom)
            for a in n.names
            if a.asname and a.name in _BUILDERS
        }

        def builds(
            name: str,
            seen: tuple[str, ...] = (),
            funcs: dict[str, _Func] = funcs,
            aliases: set[str] = aliases,
        ) -> bool:
            if name in _BUILDERS or name in aliases:
                return True
            fn = funcs.get(name)
            if fn is None or name in seen:
                return False
            return _imports_entrypoint(fn) or any(builds(c, (*seen, name)) for c in _called(fn))

        for fn in funcs.values():
            if not (fn.name.startswith("test_") and _takes_caplog(fn)):
                continue
            examined += 1
            if _imports_entrypoint(fn) or any(builds(c) for c in _called(fn)):
                offenders.append(f"{path.relative_to(root).as_posix()}:{fn.lineno}::{fn.name}")
    return examined, offenders


def test_every_caplog_test_is_accounted_for() -> None:
    examined, offenders = _census(_TESTS)
    print(f"caplog tests examined: {examined}")
    assert examined > 0, "the scan examined no caplog test; an empty corpus proves nothing"
    assert offenders == [], (
        "a test that takes caplog builds the app (create_app / configure_logging) or imports "
        "app.worker.entrypoint in its body; that removes caplog's handler, so a negative "
        "assertion on the log passes vacuously. Build the app in a fixture, or read capsys."
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("def test_a(caplog):\n    create_app(s)\n    assert 'x' not in caplog.text\n", True),
        ("def test_a(caplog):\n    app.main.configure_logging()\n", True),
        (
            "def _h():\n    return create_app(s)\n\n\ndef test_a(caplog):\n    _h()\n",
            True,
        ),
        (
            "def _h2():\n    return create_app(s)\n\n\ndef _h():\n    return _h2()\n\n\n"
            "def test_a(caplog):\n    _h()\n",
            True,
        ),
        ("def test_a(caplog):\n    import app.worker.entrypoint\n", True),
        ("def test_a(caplog):\n    from app.worker import entrypoint\n", True),
        # an aliased import and an aliased module are still the builder
        ("from app.main import create_app as mk\n\n\ndef test_a(caplog):\n    mk(s)\n", True),
        ("import app.main as m\n\n\ndef test_a(caplog):\n    m.create_app(s)\n", True),
        ("import app.worker.entrypoint as e\n\n\ndef test_a(caplog):\n    e.run()\n", False),
        # caplog taken through usefixtures, not the argument list
        (
            "@pytest.mark.usefixtures('caplog')\ndef test_a():\n    create_app(s)\n",
            True,
        ),
        # a factory fixture CALLED in the body builds the app after caplog attaches
        (
            "@pytest.fixture\ndef make_app():\n    return lambda: create_app(s)\n\n\n"
            "def test_a(caplog, make_app):\n    make_app()\n",
            True,
        ),
        # a fixture builds the app before caplog attaches: not an offender
        (
            "@pytest.fixture\ndef client():\n    return create_app(s)\n\n\n"
            "def test_a(caplog, client):\n    client.get('/')\n",
            False,
        ),
        ("def test_a(client):\n    create_app(s)\n", False),  # no caplog: out of scope
    ],
)
def test_the_census_sees_a_planted_caplog_app_build(
    tmp_path: Path, source: str, expected: bool
) -> None:
    """Positive control: each shape is caught; a fixture-built app and a no-caplog test are not."""
    (tmp_path / "test_planted.py").write_text(source, encoding="utf-8")
    examined, offenders = _census(tmp_path)
    assert examined == (1 if "caplog" in source else 0)
    assert bool(offenders) is expected
