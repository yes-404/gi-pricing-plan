"""Every routed Job kind has a handler in the production worker (PL-8022 E4.7; FR-405, FR-406).

The production entrypoint cannot be imported here (it reads settings, checks the tenant binding
and builds the Celery app at import), so this reads *which* `register_*_handlers` it calls from
its source, runs those registrars against an empty registry, and compares the result with the
routing table. A kind registered nowhere ends `failed` with `JOB_HANDLER_NOT_REGISTERED` on a
real worker: terminal, and the work never ran (FD 8021, working id).

No kind is named in the main assert. The only kinds named in this file are the allow-list's.
"""

from __future__ import annotations

import ast
import importlib
import pathlib
from typing import Any

import pytest

import app.worker.handlers as handlers
from app.platform.jobs import DEFAULT_QUEUE_FOR_KIND
from model_schema.jobs import JobKind

ENTRYPOINT = (
    pathlib.Path(__file__).resolve().parents[1] / "src" / "app" / "worker" / "entrypoint.py"
)

#: Kinds whose handler lands in a later phase: kind -> (phase, work, spec reference), each
#: verified against `docs/roadmap.md` (PL-8022 E4.7's table). A P1a, P1b or P2 kind may never be
#: listed. OBLIGATION (PL-8022 DP-Q4 (b)): the first later-phase slice that adds a route
#: submitting a listed kind makes `jobs.submit` refuse it (DP-Q4 (a)).
#: `BLOB_GC`: the dated roadmap line placing FR-420 under WK-1251 (DP-Q5 (a); the maintainer's
#: (by delegation) entry "2026-10-14 10:51:08 BST") is on main (`docs/roadmap.md`, WK-1251). No
#: handler may be registered for it: the stale-entry assert below fails if one is.
LATER_PHASE_KINDS: dict[JobKind, tuple[str, str, str]] = {
    JobKind.OPTIMISATION_RUN: ("P4", "WK-684", "04 FR-284"),
    JobKind.GIPP_CHECK: ("P4", "WK-685", "04 FR-294"),
    JobKind.MONITOR_RUN: ("P4", "WK-687", "05 FR-307"),
    JobKind.DOSSIER_GENERATE: ("P3", "WK-680", "06 FR-376"),
    JobKind.EXPORT_REGULATORY: ("P3", "WK-681", "06 FR-382"),
    JobKind.BLOB_GC: ("P3", "WK-1251", "07 FR-420"),
}

CURRENT_OR_EARLIER_PHASES = {"P1a", "P1b", "P2"}


def entrypoint_registrars() -> list[tuple[str, str]]:
    """`(module, function)` of each module-level `register_*_handlers()` call in the entrypoint."""
    tree = ast.parse(ENTRYPOINT.read_text(encoding="utf-8"))
    imported: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name.startswith("register_") and alias.name.endswith("_handlers"):
                    imported[alias.asname or alias.name] = node.module
    calls = []
    for node in tree.body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id in imported
        ):
            calls.append((imported[node.value.func.id], node.value.func.id))
    return calls


def kinds_registered_by(registrars: list[tuple[str, str]]) -> set[JobKind]:
    """Run the registrars against an empty registry, so other tests' registrations do not count.

    The registry is emptied and restored **in place**: several handler modules bind
    `HANDLERS` by name (`from app.worker.handlers import HANDLERS`), so a rebinding of
    `handlers.HANDLERS` would leave them reading, and skipping on, the original dict.
    """
    saved = dict(handlers.HANDLERS)
    handlers.HANDLERS.clear()
    try:
        for module, function in registrars:
            getattr(importlib.import_module(module), function)()
        return set(handlers.HANDLERS)
    finally:
        handlers.HANDLERS.clear()
        handlers.HANDLERS.update(saved)


def kinds_without_a_handler(registered: set[JobKind]) -> list[str]:
    return sorted(
        k.value
        for k in DEFAULT_QUEUE_FOR_KIND
        if k not in registered and k not in LATER_PHASE_KINDS
    )


def allow_list_problems(
    registered: set[JobKind], allow_list: dict[JobKind, tuple[str, str, str]]
) -> list[str]:
    problems = [
        f"{kind.value} is allow-listed for {phase}, which is not a later phase"
        for kind, (phase, _work, _spec) in allow_list.items()
        if phase in CURRENT_OR_EARLIER_PHASES
    ]
    problems += [
        f"{kind.value} is allow-listed and already has a handler (stale entry)"
        for kind in allow_list
        if kind in registered
    ]
    return problems


@pytest.mark.req("FR-405")
@pytest.mark.req("FR-406")
def test_every_routed_kind_has_a_handler_in_the_production_entrypoint() -> None:
    registered = kinds_registered_by(entrypoint_registrars())
    missing = kinds_without_a_handler(registered)
    assert missing == [], f"routed kinds with no handler in the production entrypoint: {missing}"


@pytest.mark.req("FR-405")
def test_the_allow_list_names_only_later_phase_kinds_without_a_handler() -> None:
    registered = kinds_registered_by(entrypoint_registrars())
    assert allow_list_problems(registered, LATER_PHASE_KINDS) == []


@pytest.mark.req("FR-405")
def test_the_guard_names_the_kinds_of_a_dropped_registrar() -> None:
    """Breaker: drop each registrar in turn; the guard names exactly the kinds it alone adds."""
    registrars = entrypoint_registrars()
    assert registrars, "the entrypoint calls no register_*_handlers"
    full = kinds_registered_by(registrars)
    for dropped in registrars:
        rest = [r for r in registrars if r != dropped]
        without = kinds_registered_by(rest)
        lost = {k.value for k in full - without if k in DEFAULT_QUEUE_FOR_KIND}
        assert lost <= set(kinds_without_a_handler(without)), dropped


@pytest.mark.req("FR-405")
def test_a_p2_entry_in_the_allow_list_is_refused() -> None:
    """Breaker: a kind allow-listed for P2 would hide a missing handler."""
    bad: dict[JobKind, Any] = {
        **LATER_PHASE_KINDS,
        JobKind.SCORE_TRACE_PRODUCE: ("P2", "WK-674", "07 FR-405"),
    }
    assert allow_list_problems(set(), bad)


@pytest.mark.req("FR-405")
def test_a_stale_allow_list_entry_is_refused() -> None:
    """Breaker: an entry whose handler has landed must leave the allow-list."""
    kind = next(iter(LATER_PHASE_KINDS))
    assert allow_list_problems({kind}, LATER_PHASE_KINDS)
