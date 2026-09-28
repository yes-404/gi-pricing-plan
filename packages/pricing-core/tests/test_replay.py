"""`replay_cases` — re-score a persisted case log, never regenerate (PL-1205 Task 4, FR-261).

RS-1176 condition 4. The structural guarantee is the `replay-never-generates` import-linter
contract; this file is the behavioural half: `testing`'s bound `hypothesis` names and its
`generate_contexts` are made to raise, and a replay still completes.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from test_rating_score import _compiled
from test_testing import _golden, _now, _prop, _suite

from model_schema.refs import ArtifactRef
from model_schema.regression import CasesLog
from pricing_core.rating.replay import replay_cases
from pricing_core.rating.runtime import CompiledBundle
from pricing_core.rating.testing import run_regression

_REF = ArtifactRef.model_validate("rating_version:motor-gb@27")


@pytest.fixture(scope="module")
def bundle() -> CompiledBundle:
    return asyncio.run(_compiled())


def _boom(*_a: Any, **_k: Any) -> Any:
    raise AssertionError("replay reached the generator")


@pytest.mark.req("FR-261")
def test_a_replay_re_scores_the_persisted_cases_and_never_generates(
    bundle: CompiledBundle, monkeypatch: pytest.MonkeyPatch
) -> None:
    suite = _suite([
        _prop("tight", kind="premium_bounded", upper_minor=1),
        _prop("fine", kind="premium_positive"),
    ], golden=[_golden("known")])
    run, log = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)

    from pricing_core.rating import testing

    for name in ("generate_contexts", "_draw_contexts", "given", "hypothesis_seed",
                 "generation_settings", "run_regression"):
        monkeypatch.setattr(testing, name, _boom)
    # the log survives a JSON round trip exactly as the blob would
    restored = CasesLog.model_validate_json(log.model_dump_json())
    replayed = replay_cases(
        bundle, restored, suite, recorded=run, rating_version_ref=_REF, now=_now
    )

    assert replayed.overall == "fail"
    assert [(p.name, p.status) for p in replayed.property_results] == [
        (p.name, p.status) for p in run.property_results
    ]
    tight = replayed.property_results[0]
    assert tight.counterexample is not None
    assert tight.shrink == run.property_results[0].shrink == "completed"
    assert tight.counterexample_minimal is run.property_results[0].counterexample_minimal
    assert replayed.cases_blob == run.cases_blob
    assert replayed.generation == run.generation
    assert replayed.golden_results == run.golden_results


@pytest.mark.req("FR-261")
def test_a_replay_of_a_passing_run_passes(bundle: CompiledBundle) -> None:
    suite = _suite([_prop("fine", kind="premium_positive")], seed=3)
    run, log = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
    replayed = replay_cases(bundle, log, suite, recorded=run, rating_version_ref=_REF, now=_now)
    assert replayed.overall == "pass" == run.overall


@pytest.mark.req("FR-261")
def test_a_replay_does_not_claim_minimality_it_did_not_establish(
    bundle: CompiledBundle,
) -> None:
    """A property that fails on a case no shrink produced is reported unminimised. The
    recorded run is the one made under the same suite: only the case log's re-scoring
    differs, so this does not depend on the suite-hash refusal."""
    suite = _suite([_prop("tight", kind="premium_bounded", upper_minor=1)], seed=3)
    run, log = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
    log_without_counterexample = CasesLog(cases=log.cases, counterexamples={})
    replayed = replay_cases(
        bundle, log_without_counterexample, suite, recorded=run,
        rating_version_ref=_REF, now=_now,
    )
    (result,) = replayed.property_results
    assert result.status == "fail"
    assert result.shrink == "stopped_on_limit"
    assert result.counterexample_minimal is False


@pytest.mark.req("FR-261")
@pytest.mark.req("FR-257")
def test_a_replay_refuses_a_suite_that_is_not_the_recorded_one(
    bundle: CompiledBundle,
) -> None:
    """DP-S3-2: the suite hash is FR-257's pin, so a replay under another suite version is
    refused by name before anything is scored."""
    from pricing_core.rating.replay import SuiteMismatchError

    suite = _suite([_prop("fine", kind="premium_positive")], seed=3)
    run, log = run_regression(bundle, suite, rating_version_ref=_REF, now=_now)
    edited = _suite([_prop("fine", kind="premium_bounded", upper_minor=1)], seed=3)
    with pytest.raises(SuiteMismatchError) as caught:
        replay_cases(bundle, log, edited, recorded=run, rating_version_ref=_REF, now=_now)
    assert edited.content_hash in str(caught.value)
    assert suite.content_hash in str(caught.value)


@pytest.mark.req("FR-261")
def test_replay_module_does_not_import_hypothesis_or_testing() -> None:
    """The structural half, checked directly as well as by `lint-imports`."""
    import importlib
    import sys

    for name in [m for m in sys.modules if m.startswith("pricing_core.rating.replay")]:
        del sys.modules[name]
    replay = importlib.import_module("pricing_core.rating.replay")
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path(replay.__file__ or "").read_text())
    imported = {
        (n.module if isinstance(n, ast.ImportFrom) else a.name)
        for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
        for a in (n.names if isinstance(n, ast.Import) else [None])
    }
    assert not any(m and (m.startswith("hypothesis") or m.endswith("rating.testing"))
                   for m in imported)
