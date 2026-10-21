"""Slice 4's harness record (PL-9921 D4.2): a run short of its conditions is void.

The record logic is pure, so it is tested without Docker or load. The harness reuses
`scripts/bench-rating.py`'s open-loop generator and adds only this record.
"""

from __future__ import annotations

import importlib.util
import pathlib
from types import SimpleNamespace

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "bench-deploy-path.py"


def _harness():
    spec = importlib.util.spec_from_file_location("bench_deploy_path", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rung(*, offered=200, achieved=200.0, errors=0):
    return SimpleNamespace(
        offered_rps=offered, achieved_rps=achieved, errors=errors, load_start=1.0, load_end=1.5
    )


def _record(harness, rung, *, replicas=4, running=4):
    return harness.record(rung=rung, replicas=replicas, running=running, workers=1, tree="t")


@pytest.mark.req("NFR-489")
def test_a_clean_run_is_a_reading_and_states_its_topology() -> None:
    harness = _harness()
    out = _record(harness, _rung())
    assert out["void"] is False
    assert out["replicas"] == 4
    assert out["workers_per_replica"] == 1
    assert "round-robin" in out["topology"]
    assert {"nproc", "free_g", "machine_type"} <= set(out["host"])


@pytest.mark.req("NFR-489")
@pytest.mark.parametrize(
    ("rung", "running", "why"),
    [
        (_rung(achieved=150.0), 4, "short of offered"),
        (_rung(errors=3), 4, "3 errors"),
        (_rung(), 3, "compose runs 3 api replicas"),
    ],
)
def test_a_run_short_of_its_conditions_is_void(rung, running, why) -> None:
    out = _record(_harness(), rung, running=running)
    assert out["void"] is True
    assert any(why in reason for reason in out["void_reasons"])


@pytest.mark.req("NFR-489")
def test_a_run_whose_observed_worker_count_differs_from_the_declared_one_is_void() -> None:
    """PL-1766 D5.13 (DP-S5-Q2 (a)): the bench observes N per container and voids a mismatch."""
    harness = _harness()
    observed = harness.observed_workers({"a1:10:1": "committed", "a1:11:1": "committed"})
    assert observed == {"a1": 2}
    out = harness.record(
        rung=_rung(), replicas=1, running=1, workers=1, tree="t", reading="exit", observed=observed
    )
    assert out["void"] is True
    assert any("observed workers" in reason for reason in out["void_reasons"])
    agreed = harness.record(
        rung=_rung(), replicas=1, running=1, workers=2, tree="t", reading="exit", observed=observed
    )
    assert agreed["void"] is False
    assert agreed["reading"] == "exit"
    assert _record(harness, _rung())["reading"] == "diagnostic", "an explicit ref is never the exit"
