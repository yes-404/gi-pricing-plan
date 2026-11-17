"""One cleaned git environment for every script under `scripts/` that runs git (#1913).

An exported GIT_DIR / GIT_WORK_TREE (as inside a git hook) overrides `git -C`, so a script that
finds its checkout through `__file__` would read, or write, another repository. Each script's git
calls pass `env=clean_env()` from `scripts/_gitenv.py`; these tests plant the variables and hold
the whole of `scripts/` to that, by a census over the AST (T9-T11).
"""

from __future__ import annotations

import ast
import importlib.util
import os
import pathlib
import subprocess
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
# `scripts/` is not a package; a by-path load of a script that does `from _gitenv import ...`
# needs it on `sys.path` (a direct run gets it as `sys.path[0]`; tests/test_doc_id.py says so too).
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load(name: str, path: pathlib.Path | None = None) -> types.ModuleType:
    path = path or SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_t1913_{name.replace('-', '_')}", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_gitenv = _load("_gitenv")  # by path, so mypy needs no `scripts/` on its own path


def _git(repo: pathlib.Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, env=env
    ).stdout.strip()


def _make_repo(path: pathlib.Path, text: str, commits: int) -> pathlib.Path:
    path.mkdir()
    _git(path, "init", "-q", "-b", "main")
    _git(path, "config", "user.email", "t@example.com")
    _git(path, "config", "user.name", "t")
    for i in range(commits):
        (path / "f.txt").write_text(f"{text} {i}\n")
        _git(path, "add", "-A")
        _git(path, "commit", "-q", "-m", f"{text} {i}")
    return path


@pytest.fixture
def two_repos(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[pathlib.Path, pathlib.Path]:
    """`own` (2 commits) and `other` (3), then GIT_DIR / GIT_WORK_TREE planted at `other`."""
    for k in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(k)
    own = _make_repo(tmp_path / "own", "own", 2)
    other = _make_repo(tmp_path / "other", "other", 3)
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(other))
    return own, other


def test_clean_env_drops_every_redirect_and_keeps_the_rest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in _gitenv.REDIRECTS:
        monkeypatch.setenv(name, "x")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "keep")
    env = _gitenv.clean_env()
    assert not set(_gitenv.REDIRECTS) & set(env)
    assert env["GIT_AUTHOR_NAME"] == "keep"
    assert env["PATH"] == os.environ["PATH"]


def test_redirects_cover_gits_own_local_env_vars() -> None:
    out = subprocess.run(
        ["git", "rev-parse", "--local-env-vars"], capture_output=True, text=True, check=True
    ).stdout.split()
    assert set(out) <= set(_gitenv.REDIRECTS), set(out) - set(_gitenv.REDIRECTS)


def test_audit_docs_reads_its_own_base_text(
    two_repos: tuple[pathlib.Path, pathlib.Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    own, _other = two_repos
    module = _load("audit-docs")
    monkeypatch.setattr(module, "REPO", own)
    monkeypatch.setattr(module, "_BASE_REF", "main")
    assert module._merge_base() == _git(own, "rev-parse", "HEAD")
    assert module._text_at_base("f.txt") == "own 1\n"


def test_doc_id_reads_its_own_repository(
    two_repos: tuple[pathlib.Path, pathlib.Path],
) -> None:
    own, _other = two_repos
    module = _load("doc-id")
    assert module.ref_exists("HEAD", own)
    assert module.history_commit_count(own) == 2
    assert module.is_shallow_repository(own) is False
    assert module.git_ls_files(own, "f.txt") == ["f.txt"]


def test_doc_id_materialises_without_touching_another_repository(
    two_repos: tuple[pathlib.Path, pathlib.Path], tmp_path: pathlib.Path
) -> None:
    own, other = two_repos
    module = _load("doc-id")
    other_head = _git(other, "rev-parse", "HEAD")
    archived = tmp_path / "archived"
    archived.mkdir()
    module.materialize_ref("HEAD", archived, repo_root=own)
    assert (archived / "f.txt").read_text() == "own 1\n"
    assert _git(other, "rev-parse", "HEAD") == other_head


def test_doc_id_clone_does_not_move_another_repository(
    two_repos: tuple[pathlib.Path, pathlib.Path], tmp_path: pathlib.Path
) -> None:
    own, other = two_repos
    module = _load("doc-id")
    other_head = _git(other, "rev-parse", "HEAD")
    cloned = tmp_path / "cloned"
    module.materialize_ref_with_history("HEAD", cloned, repo_root=own)
    assert (cloned / "f.txt").read_text() == "own 1\n"
    assert _git(cloned, "rev-list", "--count", "HEAD") == "2"
    # the planted GIT_DIR names `other`: its HEAD and working tree must be untouched
    assert _git(other, "rev-parse", "HEAD") == other_head
    assert _git(other, "status", "--porcelain") == ""
    assert (other / "f.txt").read_text() == "other 2\n"


def test_doc_id_clone_does_not_write_into_a_sibling_clone(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one redirect that WRITES (#1913): `other` is a clone of `own` (same history, an
    `origin`, a branch) and `GIT_DIR` names it. Unfixed, `remote remove origin` and
    `checkout --detach` run against `other`: its `origin` is gone and its HEAD detached."""
    for k in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(k)
    own = _make_repo(tmp_path / "own", "own", 2)
    other = tmp_path / "other"
    _git(tmp_path, "clone", "-q", str(own), str(other))
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    module = _load("doc-id")
    module.materialize_ref_with_history("HEAD", tmp_path / "cloned", repo_root=own)
    assert _git(other, "remote") == "origin"
    assert _git(other, "symbolic-ref", "HEAD") == "refs/heads/main"
    assert _git(other, "status", "--porcelain") == ""
    assert (tmp_path / "cloned" / "f.txt").read_text() == "own 1\n"


def test_double_stamp_scan_sees_its_own_changes(
    two_repos: tuple[pathlib.Path, pathlib.Path],
) -> None:
    own, other = two_repos
    (own / "g.txt").write_text("new\n")
    (other / "h.txt").write_text("new\n")
    module = _load("double-stamp-scan")
    assert module._changed_since(own, "HEAD") == {"g.txt"}


@pytest.mark.parametrize(
    "name", ["bench-deploy-path", "measure-p2-nfr-sweep", "measure-attribution-cost"]
)
def test_bench_and_measure_scripts_head_is_their_own(
    name: str, two_repos: tuple[pathlib.Path, pathlib.Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load(name)
    own_head = _git(ROOT, "rev-parse", "HEAD")
    own_tree = _git(ROOT, "rev-parse", "HEAD^{tree}")
    if name == "bench-deploy-path":
        assert module.tree_of() == own_head
    elif name == "measure-p2-nfr-sweep":
        assert module.git_head() == own_head
        header = module.session_header()
        assert header["head"] == own_head
        assert header["tree"] == own_tree
    else:
        assert module._env()["tree"] == own_head


# --- every importer of _gitenv loads by path from anywhere (#1913) ---------------------------

_IMPORTERS = sorted(
    p.name
    for p in SCRIPTS.glob("*.py")
    if any(line.startswith("from _gitenv import") for line in p.read_text().splitlines())
)

_LOADER = (
    "import importlib.util, sys\n"
    "spec = importlib.util.spec_from_file_location('_t1913_loaded', sys.argv[1])\n"
    "module = importlib.util.module_from_spec(spec)\n"
    "sys.modules[spec.name] = module\n"
    "spec.loader.exec_module(module)\n"
)


@pytest.mark.parametrize("script", _IMPORTERS)
def test_every_gitenv_importer_loads_by_path_from_outside_the_repo(
    script: str, tmp_path: pathlib.Path
) -> None:
    """`python -I` drops the script directory from `sys.path`; the cwd is outside the repo."""
    result = subprocess.run(
        [sys.executable, "-I", "-c", _LOADER, str(SCRIPTS / script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


# --- the census (T9-T11) ---------------------------------------------------------------------

_SUBPROCESS_FUNCS = {"run", "Popen", "check_output", "check_call", "call"}


def _is_git_argv(node: ast.expr | None) -> bool:
    if not isinstance(node, ast.List | ast.Tuple) or not node.elts:
        return False
    first = node.elts[0]
    return (
        isinstance(first, ast.Constant)
        and isinstance(first.value, str)
        and pathlib.PurePosixPath(first.value).name == "git"
    )


def _subprocess_names(nodes: list[ast.AST]) -> tuple[set[str], set[str]]:
    """The names a file binds to the `subprocess` module and to one of its run functions
    (`import subprocess as sp`, `from subprocess import run as r`)."""
    modules, funcs = {"subprocess"}, set()
    for n in nodes:
        if isinstance(n, ast.Import):
            modules |= {a.asname or a.name for a in n.names if a.name == "subprocess"}
        elif isinstance(n, ast.ImportFrom) and n.module == "subprocess":
            funcs |= {a.asname or a.name for a in n.names if a.name in _SUBPROCESS_FUNCS}
    return modules, funcs


def _is_subprocess_call(node: ast.AST, modules: set[str], funcs: set[str]) -> bool:
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    if isinstance(f, ast.Name):
        return f.id in funcs
    return (
        isinstance(f, ast.Attribute)
        and isinstance(f.value, ast.Name)
        and f.value.id in modules
        and f.attr in _SUBPROCESS_FUNCS
    )


def _has_clean_env(call: ast.Call) -> bool:
    for kw in call.keywords:
        if kw.arg == "env" and isinstance(kw.value, ast.Call):
            func = kw.value.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if name == "clean_env":
                return True
    return False


def census(scripts: pathlib.Path) -> tuple[list[str], int]:
    """(offenders, count of covered subprocess calls) over `scripts/**/*.py` but `_gitenv.py`.

    Each call to `subprocess` (through `import subprocess as sp` or `from subprocess import run`
    too) whose argv is a literal git list, or is not a literal, must carry `env=clean_env()`:
    per call, so a `clean_env()` elsewhere in the file hides nothing. Its limits, silent by
    design: a git name held in a variable (`CMD = "git"`); a helper in another module that runs
    git; `os.system`; `shell=True` or `shlex.split` command strings; a `.sh` file; `gh`, which
    runs git itself; and, found by the #1913 audit, `from subprocess import *`; a subprocess
    function bound to a name and called later (`r = subprocess.run`, then `r([...])`);
    `importlib.import_module("subprocess")`; `subprocess.getoutput` and `getstatusoutput`; the
    `os.spawn*`, `os.exec*` and `os.popen` families.
    """
    offenders: list[str] = []
    covered = 0
    for path in sorted(scripts.rglob("*.py")):
        if path.name == "_gitenv.py":
            continue
        tree = ast.parse(path.read_text())
        nodes = list(ast.walk(tree))
        git_file = any(_is_git_argv(n) for n in nodes if isinstance(n, ast.List | ast.Tuple))
        if not git_file:
            continue
        rel = path.relative_to(scripts).as_posix()
        if not any(
            isinstance(n, ast.Call)
            and (n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", ""))
            == "clean_env"
            for n in nodes
        ):
            offenders.append(f"{rel}: git argv and no clean_env call")
        modules, funcs = _subprocess_names(nodes)
        for n in nodes:
            if not _is_subprocess_call(n, modules, funcs):
                continue
            assert isinstance(n, ast.Call)
            first = n.args[0] if n.args else None
            literal = isinstance(first, ast.List | ast.Tuple)
            if literal and not _is_git_argv(first):
                continue
            if _has_clean_env(n):
                covered += 1
            else:
                offenders.append(f"{rel}:{n.lineno}")
    return offenders, covered


def redirect_holders(scripts: pathlib.Path) -> list[str]:
    """The files under `scripts/` holding the string constant "GIT_WORK_TREE" (a tuple copy)."""
    return [
        path.name
        for path in sorted(scripts.rglob("*.py"))
        if any(
            isinstance(n, ast.Constant) and n.value == "GIT_WORK_TREE"
            for n in ast.walk(ast.parse(path.read_text()))
        )
    ]


def test_every_git_call_under_scripts_is_covered_by_clean_env() -> None:
    offenders, covered = census(SCRIPTS)
    assert offenders == []
    assert covered >= 22, covered


def test_the_census_sees_a_planted_uncovered_git_call(tmp_path: pathlib.Path) -> None:
    (tmp_path / "a.py").write_text("import subprocess\nsubprocess.run(['git', 'status'])\n")
    (tmp_path / "b.py").write_text(
        "import subprocess\n"
        "def x(*cmd):\n    return subprocess.run(cmd)\n"
        "x('git', 'status')\nsubprocess.run(['git', 'log'], env=None)\n"
    )
    (tmp_path / "c.py").write_text("import subprocess\nsubprocess.run(['/usr/bin/git', 'log'])\n")
    (tmp_path / "d.py").write_text(
        "T = ('GIT_WORK_TREE',)\nimport subprocess\nsubprocess.run(['git'])\n"
    )
    offenders, covered = census(tmp_path)
    assert covered == 0
    assert redirect_holders(tmp_path) == ["d.py"]
    for name in ("a.py", "b.py", "c.py", "d.py"):
        assert any(o.startswith(name) for o in offenders), (name, offenders)


def test_the_census_sees_an_aliased_git_call_beside_a_covered_one(tmp_path: pathlib.Path) -> None:
    """A `clean_env()` call elsewhere in the file must not hide an aliased call (#1913)."""
    (tmp_path / "e.py").write_text(
        "import subprocess as sp\nfrom _gitenv import clean_env\n"
        "sp.run(['git', 'status'], env=clean_env())\nsp.run(['git', 'log'])\n"
    )
    (tmp_path / "f.py").write_text(
        "from subprocess import run as r\nfrom _gitenv import clean_env\n"
        "r(['git', 'status'], env=clean_env())\nr(['git', 'log'])\n"
    )
    offenders, covered = census(tmp_path)
    assert covered == 2
    assert offenders == ["e.py:4", "f.py:4"], offenders


def test_redirect_name_census_finds_one_definition() -> None:
    assert redirect_holders(SCRIPTS) == ["_gitenv.py"]
