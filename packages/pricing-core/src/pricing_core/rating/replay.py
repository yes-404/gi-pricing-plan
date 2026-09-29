"""`replay_cases` — re-score a persisted case log, never regenerate it (FR-261, FR-1221).

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
from typing import Literal

from model_schema.refs import ArtifactRef
from model_schema.regression import (
    CasesLog,
    PropertyResult,
    RegressionRun,
    RegressionSuite,
)
from pricing_core.rating.golden import evaluate_golden_quotes
from pricing_core.rating.properties import (
    NO_COMPARABLE_PAIRS,
    PROPERTY_FAILED,
    build_run,
    case_holds,
    counterexample_points,
    make_scorer,
    monotone_has_comparable_pair,
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

    seed = suite.generation.seed
    outputs = [o.name for o in bundle.algorithm.outputs]
    results: list[PropertyResult] = []
    for prop in suite.properties:
        check = prop.check
        grid: Literal["uniform+sampled"] | None = (
            "uniform+sampled" if check.kind == "monotone" else None
        )
        persisted = cases.counterexamples.get(prop.name)
        failing = next(
            (
                c for c in cases.cases
                if not case_holds(check, c, score, contract, seed=seed, outputs=outputs)
            ),
            None,
        )
        persisted_still_fails = persisted is not None and not case_holds(
            check, persisted, score, contract, seed=seed, outputs=outputs
        )
        if persisted_still_fails or failing is not None:
            shown = persisted if persisted_still_fails else failing
            assert shown is not None
            was = prior.get(prop.name)
            kept = persisted_still_fails and was is not None
            results.append(PropertyResult(
                name=prop.name, status="fail", cases_run=len(cases.cases),
                counterexample=dict(shown.inputs),
                counterexample_minimal=bool(kept and was and was.counterexample_minimal),
                shrink=(was.shrink if kept and was and was.shrink else "stopped_on_limit"),
                error_code=PROPERTY_FAILED, grid=grid,
                counterexample_points=counterexample_points(check, contract, shown, score, seed),
            ))
        elif check.kind == "monotone" and not monotone_has_comparable_pair(
            check, contract, cases.cases, score, seed
        ):
            results.append(PropertyResult(
                name=prop.name, status="fail", cases_run=len(cases.cases), shrink="completed",
                error_code=NO_COMPARABLE_PAIRS, grid=grid,
            ))
        else:
            results.append(PropertyResult(
                name=prop.name, status="pass", cases_run=len(cases.cases), grid=grid
            ))

    return build_run(
        suite=suite, bundle_hash=bundle.content_hash, rating_version_ref=rating_version_ref,
        started_at=started_at, finished_at=now(), generation=recorded.generation,
        cases=cases, golden_results=golden, property_results=results,
    )
