#!/usr/bin/env python3
"""Time one `expression` objective certification end to end — NFR-480 (WK-690 Slice 3, Task 10).

`docs/specs/02-modelling.md` NFR-480: "Objective certification completes in < 3 min including
the synthetic smoke fit." This calls `certify_expression_objective` directly — no HTTP, no
database, no Job — on §4.6's example loss (`asymmetric-burning-cost`) over the grid
`app.platform.objectives.default_sampling` derives for a `burning_cost` / `claim_severity`
objective: `_DEFAULT_POINTS` 2 000, `DEFAULT_SEED`, `y_range` (0, 1e6), `f_range`
(-5, ceil(log 1e6) + 1), `_DEFAULT_WEIGHTS` (0.01, 10). Those four are mirrored here rather
than imported, because `default_sampling` takes a whole `CustomObjective`; a drift between the
two is visible in the printed grid; the grid constants are left mirrored because
`_DEFAULT_POINTS` and `_DEFAULT_WEIGHTS` are module-private and `y_range`/`f_range` are computed
inside `default_sampling`, so no single import supplies them. The timed span is the whole
call: compile, the nine checks and the smoke fit.

Not a CI gate and no verdict: it prints numbers, and a human reads them against 180 s.

    uv run python scripts/bench-expression-certify.py [--runs N]
"""

from __future__ import annotations

import argparse
import math
import statistics
import time

from model_schema import CertificateResult, HessianStrategy, SamplingSpec, YDomain
from pricing_core.modelling.expression_objective import certify_expression_objective

LOSS = "w * where(exp(f) < y, w_under, w_over) * (y - exp(f)) ** 2"
PARAMETERS = {"w_under": 2.0, "w_over": 1.0}
Y_HIGH = 1_000_000.0
SAMPLING = SamplingSpec(
    n_points=2_000,
    seed=20260818,
    y_range=(0.0, Y_HIGH),
    f_range=(-5.0, math.ceil(math.log(Y_HIGH)) + 1.0),
    w_range=(0.01, 10.0),
)


def certify_once() -> tuple[float, CertificateResult]:
    start = time.perf_counter()
    result = certify_expression_objective(
        ref="custom_objective:asymmetric-burning-cost@1",
        loss=LOSS,
        parameters=PARAMETERS,
        y_domain=YDomain(min_inclusive=0.0),
        hessian_strategy=HessianStrategy.CLIP_TO_MIN,
        hessian_min=1e-6,
        inverse_link="exp",
        sampling=SAMPLING,
    )
    return time.perf_counter() - start, result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=1, help="in-process repeats (default 1)")
    runs = parser.parse_args().runs
    print(f"grid: {SAMPLING.model_dump()}")
    times: list[float] = []
    for i in range(runs):
        seconds, result = certify_once()
        times.append(seconds)
        print(f"run {i + 1}: {seconds:.3f} s  overall={result.overall.value}")
        for check in result.checks:
            print(f"  {check.name}: {check.status.value}")
            if check.name == "smoke_fit":
                print(f"    detail: {check.detail}")
    if runs > 1:
        median = statistics.median(times)
        print(f"median {median:.3f} s  min {min(times):.3f}  max {max(times):.3f}")


if __name__ == "__main__":
    main()
