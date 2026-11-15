"""FR-420 — `BlobStore.collect_garbage` has no caller yet (#1504 slice 3a, #1855 condition (iii)).

The collector deletes stored artifacts. Slice 3a makes its form safe (rows deleted by one
re-checking statement, objects deleted after the commit, under the digest lock) and gives it no
caller, schedule, endpoint or enabling setting. Slice 3b wires it, after #1550 decides the role
that may delete from `blobs`. **3b changes this guard on purpose, in the same commit that adds
the wiring**; until then any caller that appears fails here.

Pure text and AST: nothing here imports the application (`entrypoint` connects at import). The
scanners take `(path, source)` so each kind of caller is proven red on a planted source below,
and the scan over the real tree is proven green by the last test.

A "caller" is any of:

1. a Python call of `collect_garbage` (attribute or bare name) under `backend/src`,
   `backend/scripts`, `scripts` or `packages/*/src` (tests are not callers);
2. a reference to `JobKind.BLOB_GC` under `backend/src` beyond the one routing-map entry in
   `platform/jobs.py`, or the literal `"blob.gc"` there (a handler registration, a submit);
3. a beat-schedule entry whose task names a blob or garbage-collection task;
4. an HTTP route whose path names `gc` or `garbage`;
5. any mention of `collect_garbage`, `blob.gc` or `BLOB_GC` in `deploy/`, `.github/workflows/`,
   `Makefile` or `justfile`.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_PY_ROOTS = ("backend/src", "backend/scripts", "scripts")
_NON_PY = ("deploy", ".github/workflows", "Makefile", "justfile")
_JOBS_MODULE = "backend/src/app/platform/jobs.py"
_TEXT_NAMES = re.compile(r"collect_garbage|blob\.gc|BLOB_GC")
_ROUTE_NAMES = re.compile(r"(^|[/_.-])(gc|garbage)($|[/_.-])", re.IGNORECASE)
_ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "route", "api_route"}


def _rel(path: Path) -> str:
    return path.relative_to(_REPO).as_posix()


def python_call_sites(rel: str, source: str) -> list[str]:
    """Kind 1: calls of `collect_garbage`."""
    hits = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            if name == "collect_garbage":
                hits.append(f"{rel}:{node.lineno} calls collect_garbage")
    return hits


def blob_gc_job_references(rel: str, source: str) -> list[str]:
    """Kind 2: `JobKind.BLOB_GC` (beyond the single routing entry) and the `"blob.gc"` literal."""
    hits = []
    uses = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Attribute)
        and node.attr == "BLOB_GC"
        and isinstance(node.value, ast.Name)
        and node.value.id == "JobKind"
    ]
    allowed = 1 if rel == _JOBS_MODULE else 0
    hits += [f"{rel}:{n.lineno} references JobKind.BLOB_GC" for n in uses[allowed:]]
    if rel != _JOBS_MODULE:
        hits += [
            f"{rel}:{n.lineno} names the job kind 'blob.gc'"
            for n in ast.walk(ast.parse(source))
            if isinstance(n, ast.Constant) and n.value == "blob.gc"
        ]
    return hits


def beat_entries(rel: str, source: str) -> list[str]:
    """Kind 3: in a module that declares a beat schedule, any `"task": <str>` naming blob or GC."""
    if "beat_schedule" not in source:
        return []
    hits = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values, strict=True):
                if (
                    isinstance(key, ast.Constant)
                    and key.value == "task"
                    and isinstance(value, ast.Constant)
                    and isinstance(value.value, str)
                    and re.search(r"blob|gc|garbage", value.value, re.IGNORECASE)
                ):
                    hits.append(f"{rel}:{node.lineno} beat task {value.value!r}")
    return hits


def route_paths(rel: str, source: str) -> list[str]:
    """Kind 4: a route decorator whose path names `gc` or `garbage`."""
    hits = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            for deco in node.decorator_list:
                if (
                    isinstance(deco, ast.Call)
                    and isinstance(deco.func, ast.Attribute)
                    and deco.func.attr in _ROUTE_METHODS
                    and deco.args
                    and isinstance(deco.args[0], ast.Constant)
                    and isinstance(deco.args[0].value, str)
                    and _ROUTE_NAMES.search(deco.args[0].value)
                ):
                    hits.append(f"{rel}:{node.lineno} route {deco.args[0].value!r}")
    return hits


def outside_python(rel: str, text: str) -> list[str]:
    """Kind 5: any mention in deployment files."""
    return [
        f"{rel}:{i} mentions {m.group(0)}"
        for i, line in enumerate(text.splitlines(), 1)
        if (m := _TEXT_NAMES.search(line))
    ]


def _python_files() -> list[Path]:
    roots = [_REPO / r for r in _PY_ROOTS] + sorted(_REPO.glob("packages/*/src"))
    return sorted(p for root in roots if root.is_dir() for p in root.rglob("*.py"))


def _non_python_files() -> list[Path]:
    files: list[Path] = []
    for name in _NON_PY:
        path = _REPO / name
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files += sorted(p for p in path.rglob("*") if p.is_file())
    return files


def scan_tree() -> dict[str, list[str]]:
    """Every caller on disk, by kind. The definition in `blobs.py` is not a call."""
    found: dict[str, list[str]] = {"call": [], "job": [], "beat": [], "route": [], "outside": []}
    for path in _python_files():
        rel, source = _rel(path), path.read_text(encoding="utf-8")
        found["call"] += python_call_sites(rel, source)
        if rel.startswith("backend/src/"):
            found["job"] += blob_gc_job_references(rel, source)
            found["beat"] += beat_entries(rel, source)
        if rel.startswith("backend/src/app/api/"):
            found["route"] += route_paths(rel, source)
    for path in _non_python_files():
        try:
            found["outside"] += outside_python(_rel(path), path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
    return found


@pytest.mark.req("FR-420")
def test_collect_garbage_has_no_caller_schedule_endpoint_or_job_handler() -> None:
    found = scan_tree()
    assert not any(found.values()), (
        "BlobStore.collect_garbage must have no caller until slice 3b wires it (#1550, #1855): "
        f"{found}"
    )


@pytest.mark.req("FR-420")
def test_the_scan_sees_the_tree_it_claims_to_scan() -> None:
    """A guard that scans nothing is green for ever: the roots must hold real files, and the
    definition itself must be where the scan looks."""
    files = {_rel(p) for p in _python_files()}
    assert "backend/src/app/platform/blobs.py" in files
    assert _JOBS_MODULE in files
    assert len(files) > 50
    assert "def collect_garbage" in (_REPO / "backend/src/app/platform/blobs.py").read_text()


# -- Each kind of caller, planted: the scanner must report it ----------------------------------


@pytest.mark.req("FR-420")
@pytest.mark.parametrize(
    ("scanner", "source"),
    [
        (python_call_sites, "async def f(s):\n    await store.collect_garbage(s)\n"),
        (python_call_sites, "def f():\n    collect_garbage()\n"),
        (blob_gc_job_references, "register_handler(JobKind.BLOB_GC, handler)\n"),
        (blob_gc_job_references, "kind = 'blob.gc'\n"),
        (
            beat_entries,
            "app.conf.beat_schedule = {'gc': {'task': 'app.worker.blob_gc', 'schedule': 1}}\n",
        ),
        (route_paths, "@router.post('/blobs/gc')\nasync def run():\n    ...\n"),
        (route_paths, "@router.post('/maintenance/garbage-collect')\nasync def run():\n    ...\n"),
    ],
)
def test_each_kind_of_python_caller_is_detected(scanner, source: str) -> None:
    assert scanner("backend/src/app/x.py", source)


@pytest.mark.req("FR-420")
def test_a_second_job_kind_reference_in_the_jobs_module_is_detected() -> None:
    one = "ROUTING = {JobKind.BLOB_GC: 'io'}\n"
    assert blob_gc_job_references(_JOBS_MODULE, one) == []
    assert blob_gc_job_references(_JOBS_MODULE, one + "submit(JobKind.BLOB_GC)\n")


@pytest.mark.req("FR-420")
@pytest.mark.parametrize(
    "line",
    ["  command: python -c 'collect_garbage()'", "BLOB_GC=1", "run: curl -d kind=blob.gc"],
)
def test_a_deployment_mention_is_detected(line: str) -> None:
    assert outside_python("deploy/compose.yaml", line + "\n")


@pytest.mark.req("FR-420")
def test_the_relay_beat_entry_and_ordinary_routes_are_not_flagged() -> None:
    assert not beat_entries(
        "backend/src/app/worker/entrypoint.py",
        "app.conf.beat_schedule = {'relay': {'task': 'app.worker.relay_outbox'}}\n",
    )
    assert not route_paths(
        "backend/src/app/api/x.py", "@router.get('/blobs/{sha}')\nasync def f(): ...\n"
    )
