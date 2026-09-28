"""`generate_contexts` — the seed, the settings and the version (03 §5.2, FR-261; PL-1205 Task 3).

RS-1176's conditions 2, 3 and 6: the generation settings are fixed and asserted, a generator
built against another `hypothesis` version is refused by name, and two fresh interpreters
given the same persisted seed produce byte-identical case logs.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import textwrap
from typing import Any

import hypothesis
import pytest

from model_schema.rating import InputContractField
from model_schema.scoring import QuoteContext
from pricing_core.rating.testing import GeneratorVersionMismatch, generate_contexts

_CONTRACT = [
    InputContractField.model_validate(f)
    for f in (
        {"name": "driver_age", "type": "int", "min": 17, "max": 99},
        {"name": "channel", "type": "enum", "domain": ["direct", "broker"]},
        {"name": "ncd_years", "type": "int", "min": 0, "max": 9, "nullable": True},
        {"name": "vehicle_value", "type": "decimal", "min": 500, "max": 90000},
        {"name": "postcode", "type": "string", "pattern": "[A-Z]{1,2}[0-9]{1,2}"},
        {"name": "start", "type": "date"},
        {"name": "telematics", "type": "bool"},
    )
]


def _canonical(contexts: list[QuoteContext]) -> str:
    payload = [c.model_dump(mode="json") for c in contexts]
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


@pytest.mark.req("FR-261")
def test_the_same_seed_gives_the_same_cases_in_process() -> None:
    one = generate_contexts(_CONTRACT, 30, 11)
    two = generate_contexts(_CONTRACT, 30, 11)
    assert _canonical(one) == _canonical(two)
    assert len(one) == 30
    assert _canonical(generate_contexts(_CONTRACT, 30, 12)) != _canonical(one)


@pytest.mark.req("FR-261")
def test_every_case_satisfies_the_input_contract() -> None:
    for ctx in generate_contexts(_CONTRACT, 40, 3):
        i = ctx.inputs
        assert 17 <= i["driver_age"] <= 99  # type: ignore[operator]
        assert i["channel"] in {"direct", "broker"}
        assert i["ncd_years"] is None or 0 <= i["ncd_years"] <= 9  # type: ignore[operator]
        assert not isinstance(i["vehicle_value"], float)
        assert isinstance(i["telematics"], bool)


@pytest.mark.req("FR-261")
def test_the_generation_settings_are_the_declared_ones() -> None:
    """RS-1176 condition 2: what `run_regression` and `generate_contexts` both apply."""
    from pricing_core.rating.testing import generation_settings

    s = generation_settings(123)
    assert s.database is None
    assert s.deadline is None
    assert s.report_multiple_bugs is False
    assert s.derandomize is False
    assert s.max_examples == 123
    assert s.suppress_health_check == ()  # PL-1205:311's list, nothing added


@pytest.mark.req("FR-261")
def test_a_version_mismatch_is_refused_naming_both_versions() -> None:
    with pytest.raises(GeneratorVersionMismatch) as caught:
        generate_contexts(_CONTRACT, 5, 1, expect_version="0.0.1")
    assert "0.0.1" in str(caught.value)
    assert hypothesis.__version__ in str(caught.value)
    assert isinstance(caught.value, ValueError)
    assert len(generate_contexts(_CONTRACT, 5, 1, expect_version=hypothesis.__version__)) == 5


_TESTS_DIR = str(pathlib.Path(__file__).parent)

_CHILD = textwrap.dedent(
    """
    import asyncio, hashlib, json, sys
    sys.path.insert(0, sys.argv[2])
    from test_rating_score import _compiled
    from test_testing import _REF, _now, _prop, _suite

    from model_schema.regression import cases_log_bytes
    from pricing_core.rating import testing

    bundle = asyncio.run(_compiled())
    if sys.argv[1] == "none":
        # the negative control: the same generator with no persisted seed
        drawn = testing._draw_contexts(bundle.algorithm.input_contract, 30, None)
        blob = json.dumps([c.model_dump(mode="json") for c in drawn], sort_keys=True)
        print(hashlib.sha256(blob.encode()).hexdigest())
        print("{}")
        print("{}")
    else:
        suite = _suite(
            [_prop("tight", kind="premium_bounded", upper_minor=1),
             _prop("age-up", kind="monotone", input="driver_age", direction="increasing")],
            seed=int(sys.argv[1]),
        )
        run, log = testing.run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
        from model_schema.regression import MonotoneInInput
        from pricing_core.rating.properties import monotone_grid

        field = next(f for f in bundle.algorithm.input_contract if f.name == "driver_age")
        check = MonotoneInInput.model_validate(
            {"kind": "monotone", "input": "driver_age", "direction": "increasing"})
        print(hashlib.sha256(cases_log_bytes(log)).hexdigest())
        print(json.dumps(
            {k: v.model_dump(mode="json") for k, v in log.counterexamples.items()},
            sort_keys=True, separators=(",", ":"),
        ))
        # the SAMPLED grid and the verdicts of every property, from this interpreter
        print(json.dumps({
            "grid": monotone_grid(field, check, int(sys.argv[1])),
            "verdicts": [(p.name, p.status, p.grid) for p in run.property_results],
        }, sort_keys=True))
    """
)


def _child(seed: str, hashseed: str) -> tuple[str, str, str]:
    """(case-log sha256, canonical counterexamples) from a fresh interpreter running the
    PUBLIC `run_regression` (or the unseeded generator, for the negative control)."""
    out = subprocess.run(
        [sys.executable, "-c", _CHILD, seed, _TESTS_DIR],
        check=True, capture_output=True, text=True,
        env={**os.environ, "PYTHONHASHSEED": hashseed},
    )
    digest, counterexamples, grid = out.stdout.strip().splitlines()[-3:]
    return digest, counterexamples, grid


@pytest.mark.req("FR-261")
def test_the_same_seed_gives_the_same_run_across_fresh_interpreters() -> None:
    """RS-1176 condition 6, positive: different hash seeds, one persisted seed — the case
    log AND the shrunk counterexample are identical."""
    one = _child("424242", "1")
    two = _child("424242", "2")
    assert one == two
    assert one[1] != "{}"  # the counterexample is really there to compare
    assert '"grid": [' in one[2]  # and so is the sampled grid, with its verdicts


@pytest.mark.req("FR-261")
def test_the_comparator_can_fail_without_a_persisted_seed() -> None:
    """RS-1176 condition 6, negative control: no seed, and the logs differ."""
    assert _child("none", "1")[0] != _child("none", "1")[0]


@pytest.mark.req("FR-261")
@pytest.mark.parametrize("profile", ["default", "ci"])
def test_the_generation_settings_do_not_inherit_the_ambient_profile(profile: str) -> None:
    """RS-1176 condition 2, "fixed settings": Hypothesis auto-loads its built-in `ci` profile
    when `CI` is set, and that profile sets `derandomize=True`, `print_blob=True` and
    `suppress_health_check=[HealthCheck.too_slow]` among others. Every behaviour-affecting
    field is set explicitly, so the settings are the same under either profile."""
    from hypothesis import Phase, Verbosity
    from hypothesis import settings as hypothesis_settings

    from pricing_core.rating.testing import generation_settings

    previous = hypothesis_settings.get_current_profile_name()
    hypothesis_settings.load_profile(profile)
    try:
        s = generation_settings(123)
    finally:
        hypothesis_settings.load_profile(previous)
    assert s.database is None
    assert s.deadline is None
    assert s.report_multiple_bugs is False
    assert s.derandomize is False
    assert s.max_examples == 123
    assert s.suppress_health_check == ()
    assert s.print_blob is False
    assert s.verbosity == Verbosity.normal
    assert tuple(s.phases) == tuple(Phase)
    assert s.stateful_step_count == 50
    assert s.backend == "hypothesis"


@pytest.mark.req("FR-261")
def test_the_effective_settings_are_identical_under_ci_and_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The whole effective settings object, field by field, is the same when `CI` is exported
    (Hypothesis then loads its `ci` profile) as when it is unset."""
    from hypothesis import settings as hypothesis_settings

    from pricing_core.rating.testing import generation_settings

    fields = ("max_examples", "derandomize", "database", "verbosity", "phases",
              "stateful_step_count", "report_multiple_bugs", "suppress_health_check",
              "deadline", "print_blob", "backend")

    def effective(profile: str) -> dict[str, Any]:
        previous = hypothesis_settings.get_current_profile_name()
        hypothesis_settings.load_profile(profile)
        try:
            s = generation_settings(77)
        finally:
            hypothesis_settings.load_profile(previous)
        return {f: getattr(s, f) for f in fields}

    monkeypatch.setenv("CI", "1")
    under_ci = effective("ci")
    monkeypatch.delenv("CI")
    unset = effective("default")
    assert under_ci == unset
