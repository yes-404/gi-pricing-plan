"""`replay_cases` — re-score a persisted case log, never regenerate it (FR-261, FR-9301).

RS-1176 condition 4: a Regression Run persists every generated case and every counterexample
as one content-addressed blob, and a replay re-scores exactly those. This module holds no
generator and no shrinker and **never imports `hypothesis` or `pricing_core.rating.testing`
— even indirectly** (the `replay-never-generates` contract in `.importlinter`). A
counterexample's `shrink` and `counterexample_minimal` are reported as the recorded run
carried them: replay cannot shrink, so it never claims a minimality it did not establish.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from model_schema.refs import ArtifactRef
from model_schema.regression import (
    CasesLog,
    PropertyResult,
    RegressionRun,
    RegressionSuite,
)
from pricing_core.rating.golden import evaluate_golden_quotes
from pricing_core.rating.properties import (
    PROPERTY_FAILED,
    build_run,
    case_holds,
    make_scorer,
)
from pricing_core.rating.runtime import CompiledBundle

__all__ = ["SuiteMismatchError", "replay_cases"]


class SuiteMismatchError(ValueError):
    """The suite passed to a replay is not the one the recorded run was made under.

    The suite's content hash is FR-257's pin (DP-S3-2), so a replay under another version
    would report a run of a suite nobody approved on."""


def replay_cases(
    bundle: CompiledBundle,
    cases: CasesLog,
    suite: RegressionSuite,
    *,
    recorded: RegressionRun,
    rating_version_ref: ArtifactRef,
    now: Callable[[], datetime],
) -> RegressionRun:
    """Re-score `cases` (and their counterexamples) and the suite's golden quotes.

    `recorded` is the run the case log came from: it supplies the generation record and
    each failing property's persisted `shrink`/`counterexample_minimal`. A property that
    now fails on a case the recorded run did not shrink is reported unminimised
    (`stopped_on_limit`, `counterexample_minimal=False`), since a replay cannot shrink.
    """
    if suite.content_hash != recorded.suite_content_hash:
        raise SuiteMismatchError(
            f"replay under suite {suite.content_hash}, but the recorded run is of suite "
            f"{recorded.suite_content_hash}"
        )
    started_at = now()
    contract = bundle.algorithm.input_contract
    score = make_scorer(bundle, rating_version_ref, contract)
    golden = evaluate_golden_quotes(
        bundle, suite.golden_quotes, rating_version_ref=rating_version_ref
    )
    prior = {p.name: p for p in recorded.property_results}

    results: list[PropertyResult] = []
    for prop in suite.properties:
        persisted = cases.counterexamples.get(prop.name)
        failing = next(
            (c for c in cases.cases if not case_holds(prop.check, c, score, contract)), None
        )
        persisted_still_fails = persisted is not None and not case_holds(
            prop.check, persisted, score, contract
        )
        if persisted_still_fails:
            assert persisted is not None
            was = prior.get(prop.name)
            results.append(PropertyResult(
                name=prop.name, status="fail", cases_run=len(cases.cases),
                counterexample=dict(persisted.inputs),
                counterexample_minimal=bool(was and was.counterexample_minimal),
                shrink=(was.shrink if was and was.shrink else "stopped_on_limit"),
                error_code=PROPERTY_FAILED,
            ))
        elif failing is not None:
            results.append(PropertyResult(
                name=prop.name, status="fail", cases_run=len(cases.cases),
                counterexample=dict(failing.inputs), counterexample_minimal=False,
                shrink="stopped_on_limit", error_code=PROPERTY_FAILED,
            ))
        else:
            results.append(PropertyResult(
                name=prop.name, status="pass", cases_run=len(cases.cases)
            ))

    return build_run(
        suite=suite, bundle_hash=bundle.content_hash, rating_version_ref=rating_version_ref,
        started_at=started_at, finished_at=now(), generation=recorded.generation,
        cases=cases, golden_results=golden, property_results=results,
    )
