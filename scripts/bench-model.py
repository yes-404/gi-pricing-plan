#!/usr/bin/env python3
"""Measure the `02` budgets — NFR-MODEL-1, -2, -3, -4, -5, -10, -11 (and -12's saving).

`bench-data.py`'s sibling, and it inherits that script's rule verbatim:

    Not a CI gate. A timing assertion on a shared runner fails for reasons that have
    nothing to do with the code, and a check that fails randomly teaches everyone to
    re-run it. This produces numbers for a workstream closure record instead, where a
    human reads them once against the budget.

    uv run python scripts/bench-model.py --only curve --scales 100000,200000,400000,678013

`bench-data.py` knows only `01`'s budgets, which is why this exists rather than a flag on
it: the fixtures are different (a model needs factors, an offset and a holdout), the
budgets are different, and three of `02`'s are ratios and sizes rather than throughputs.

**Two of `02`'s budgets name a scale this machine cannot reach.** NFR-MODEL-1, -2 and -10
are stated at 5 M rows x 60 factors on a 16-core worker; a 5 M x 60 design matrix is
~7 GB dense before glum allocates anything. `--only curve` therefore measures at several
scales that do fit, fits `t = a·n^b` by least squares in log space, and prints both the
exponent and the extrapolation to 5 M — labelled as an extrapolation, because
`bench-data.py`'s docstring is right that an extrapolation reported as a measurement is
the more expensive mistake. The exponent is the part worth reading: it says whether the
path is linear in rows, and a super-linear one is the thing that would make the
extrapolation optimistic.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import threading
import time
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID, uuid4

import numpy as np
import polars as pl

_PACKAGES = Path(__file__).resolve().parent.parent / "packages"
sys.path.insert(0, str(_PACKAGES / "pricing-core" / "src"))
sys.path.insert(0, str(_PACKAGES / "model-schema" / "src"))

from model_schema import (  # noqa: E402
    TEMPLATE_APPLICABILITY,
    TEMPLATE_PARAMETERS,
    BandingMethod,
    BandingProposal,
    CustomObjective,
    Factor,
    FactorType,
    GbmFunctionRef,
    GbmSpec,
    GlmSpec,
    GroupingMethod,
    GroupingProposal,
    HessianStrategy,
    ObjectiveStatus,
    ObjectiveTemplate,
    OffsetSpec,
    ResponseKind,
    SamplingSpec,
    TemplateParameter,
    UnseenLevelBehaviour,
    new_uuid7,
)
from pricing_core.data.profile import one_way  # noqa: E402
from pricing_core.modelling.bandings import propose_banding  # noqa: E402
from pricing_core.modelling.diagnostics import (  # noqa: E402
    compute_diagnostics,
    compute_gbm_diagnostics,
)
from pricing_core.modelling.gbm import fit_gbm  # noqa: E402
from pricing_core.modelling.glm import fit_glm  # noqa: E402
from pricing_core.modelling.groupings import (  # noqa: E402
    grouping_evidence,
    propose_grouping,
)
from pricing_core.modelling.objectives import certify_objective  # noqa: E402

#: The scale the requirements are written at, and the one this machine cannot reach.
TARGET_ROWS = 5_000_000
TARGET_FACTORS = 60

#: label -> the budget the spec states, in seconds (or a ratio / bytes where named).
BUDGETS: dict[str, float] = {
    "NFR-MODEL-1 glm fit": 10 * 60,
    "NFR-MODEL-2 gbm fit, 500 trees": 20 * 60,
    "NFR-MODEL-3 propose_banding": 5.0,
    "NFR-MODEL-3 propose_grouping": 5.0,
    "NFR-MODEL-5 certify_objective": 3 * 60,
}

#: label -> (wall seconds, peak RSS in MB, CPU seconds)
results: list[tuple[str, float, float, float]] = []

PAGE_MB = os.sysconf("SC_PAGE_SIZE") / 1e6


def _rss_mb() -> float:
    """Resident set in MB — `bench-data.py`'s reader, for the same reason it gives.

    `ru_maxrss` is a process high-water mark and cannot give a per-operation peak; statm
    sampled during the block can.
    """
    with open("/proc/self/statm") as handle:
        return int(handle.read().split()[1]) * PAGE_MB


@contextmanager
def timed(label: str, *, quiet: bool = False) -> Iterator[list[float]]:
    """Time a block and sample its peak RSS. Yields a one-element list holding the seconds,
    so a caller inside the block can be told what it cost without a second timer."""
    slot = [0.0]
    peak = _rss_mb()
    stop = threading.Event()
    cpu_start = time.process_time()

    def sample() -> None:
        nonlocal peak
        while not stop.wait(0.02):
            peak = max(peak, _rss_mb())

    sampler = threading.Thread(target=sample, daemon=True)
    sampler.start()
    start = time.perf_counter()
    try:
        yield slot
    finally:
        elapsed = time.perf_counter() - start
        cpu = time.process_time() - cpu_start
        stop.set()
        sampler.join()
    slot[0] = elapsed
    peak = max(peak, _rss_mb())
    results.append((label, elapsed, peak, cpu))
    if not quiet:
        # CPU seconds beside wall-clock, because this machine is shared. Under contention
        # wall-clock inflates and CPU time does not, so a pair that has drifted apart says
        # the reading is contended rather than that the code got slower. (A parallel
        # backend such as XGBoost inverts this: CPU exceeds wall by the thread count.)
        print(
            f"  {label:<44} {elapsed:8.2f} s wall  {cpu:8.2f} s cpu   "
            f"peak RSS {peak:7,.0f} MB"
        )


def machine() -> str:
    cores = os.cpu_count() or 0
    with open("/proc/meminfo") as handle:
        total_kb = int(handle.readline().split()[1])
    model = "unknown"
    with open("/proc/cpuinfo") as handle:
        for line in handle:
            if line.startswith("model name"):
                model = line.split(":", 1)[1].strip()
                break
    with open("/proc/loadavg") as handle:
        load = handle.read().split()[0]
    # The load average is part of the measurement, not colour. This repository's
    # development machine is shared between concurrent sessions, and a wall-clock reading
    # taken at load 9 on 4 cores is a different number from the same code at load 0.5.
    return (
        f"{model}, {cores} cores, {total_kb / 1e6:.1f} GB RAM, "
        f"1-minute load average {load}"
    )


# -- fixtures ------------------------------------------------------------------------------


def synthesise(rows: int, factors: int, *, seed: int = 20260822) -> pl.DataFrame:
    """A motor book with `factors` rating variables, a third of them categorical.

    Deterministic per column but genuinely noisy: a modulo pattern would give the GLM a
    response it can reproduce exactly, and a fit with nothing left to explain converges in
    one iteration — which measures the setup, not the fit. The response is drawn from a
    Poisson whose rate depends on the first four factors, so the IRLS actually iterates.
    """
    rng = np.random.default_rng(seed)
    n_categorical = max(1, factors // 3)
    data: dict[str, pl.Series] = {
        "policy_id": pl.Series("policy_id", np.arange(rows), dtype=pl.Int64),
        "exposure_years": pl.Series(
            "exposure_years", rng.uniform(0.25, 1.0, rows), dtype=pl.Float64
        ),
    }
    log_rate = np.full(rows, -2.0)
    for i in range(n_categorical):
        levels = 8
        codes = rng.integers(0, levels, rows)
        data[f"cat_{i:02d}"] = pl.Series(f"cat_{i:02d}", [f"L{c}" for c in codes])
        if i < 2:
            log_rate += 0.15 * codes
    for i in range(factors - n_categorical):
        column = rng.normal(size=rows)
        data[f"num_{i:02d}"] = pl.Series(f"num_{i:02d}", column, dtype=pl.Float64)
        if i < 2:
            log_rate += 0.20 * column

    exposure = data["exposure_years"].to_numpy()
    counts = rng.poisson(np.exp(log_rate) * exposure)
    data["claim_count"] = pl.Series("claim_count", counts, dtype=pl.Int64)
    data["claim_amount_minor"] = pl.Series(
        "claim_amount_minor", counts * rng.integers(50_000, 400_000, rows), dtype=pl.Int64
    )
    return pl.DataFrame(data)


def factor_set(frame: pl.DataFrame, dataset_id: UUID) -> tuple[Factor, ...]:
    """One identity Factor per rating column — the widest design the spec's "60 factors"
    can mean, since a banded or grouped factor is narrower than its source."""
    return tuple(
        Factor(
            id=uuid4(), slug=column, dataset_id=dataset_id, version=1,
            type=FactorType.IDENTITY, source_columns=(column,),
        )
        for column in frame.columns
        if column.startswith(("cat_", "num_"))
    )


def glm_spec(version_id: UUID, factors: Sequence[Factor]) -> GlmSpec:
    return GlmSpec(
        model_family_slug=f"bench-{new_uuid7().hex[-6:]}",
        dataset_version_id=version_id,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=tuple(f.id for f in factors),
    )


def gbm_spec(version_id: UUID, factors: Sequence[Factor], *, rounds: int) -> GbmSpec:
    return GbmSpec(
        model_type="xgboost",
        model_family_slug=f"bench-{new_uuid7().hex[-6:]}",
        dataset_version_id=version_id,
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=tuple(f.id for f in factors),
        objective=GbmFunctionRef(kind="builtin", name="count:poisson"),
        categorical_handling="native",
        hyperparameters={"max_depth": 6, "eta": 0.1, "num_boost_round": rounds},
    )


def levelled_frame(rows: int, levels: int, *, seed: int = 20260822) -> pl.DataFrame:
    """A book whose one categorical column carries `levels` distinct values.

    NFR-MODEL-3's scale is stated in *levels*, not rows, so the row count is freMTPL2's and
    the level count is the variable. Rates vary smoothly across the levels so the clusterers
    have a real ordering to find rather than noise to partition arbitrarily.
    """
    rng = np.random.default_rng(seed)
    codes = rng.integers(0, levels, rows)
    exposure = rng.uniform(0.25, 1.0, rows)
    counts = rng.poisson(np.exp(-2.5 + 1.5 * codes / levels) * exposure)
    return pl.DataFrame(
        {
            "territory": pl.Series("territory", [f"T{c:05d}" for c in codes]),
            "exposure_years": pl.Series("exposure_years", exposure, dtype=pl.Float64),
            "claim_count": pl.Series("claim_count", counts, dtype=pl.Int64),
            "claim_amount_minor": pl.Series(
                "claim_amount_minor",
                counts * rng.integers(50_000, 400_000, rows),
                dtype=pl.Int64,
            ),
        }
    )


# -- phases --------------------------------------------------------------------------------


def bench_proposals(rows: int, levels: int, bands: int, groups: int) -> None:
    """NFR-MODEL-3, and NFR-MODEL-12's saving, broken down by where the time goes."""
    print(f"\nNFR-MODEL-3 — {rows:,} rows, {levels:,} distinct levels, budget 5 s")
    frame = levelled_frame(rows, levels)
    dataset_version_id = uuid4()

    for method in BandingMethod:
        if method is BandingMethod.MANUAL:
            continue
        proposal = BandingProposal(
            dataset_version_id=dataset_version_id, column="claim_amount_minor",
            method=method, n_bands=bands,
        )
        with timed(f"NFR-MODEL-3 propose_banding {method.value}"):
            propose_banding(frame, proposal, dataset_id=uuid4(), slug="amt")

    for method in (
        GroupingMethod.CREDIBILITY_WEIGHTED,
        GroupingMethod.HIERARCHICAL_CLUSTERING,
        GroupingMethod.TREE,
    ):
        proposal = GroupingProposal(
            dataset_version_id=dataset_version_id, column="territory",
            method=method, n_groups=groups,
            unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT,
        )
        with timed(f"NFR-MODEL-3 propose_grouping {method.value}"):
            propose_grouping(frame, proposal, dataset_id=uuid4(), slug="terr")


def bench_breakdown(rows: int, levels: int, groups: int) -> None:
    """Where NFR-MODEL-3's wall-clock goes, in a **fresh process**.

    Its own phase rather than a tail on `bench_proposals`, and the reason is a measurement
    this script produced before it was split: the same `one_way` call timed 15.8 s after
    eight proposals had run and 4.6 s on its own. Peak RSS is a process high-water mark and
    glibc does not return freed arenas — the same isolation `bench-data.py --only` exists
    for, reached here by the same route.

    NFR-MODEL-12 removed the *second* source summary. This asks what the first one still
    costs, because that is exactly what a Profile-fed proposal (`01` FR-DATA-26) would not
    have to pay.
    """
    print(f"\nNFR-MODEL-3 breakdown — {rows:,} rows, {levels:,} levels")
    frame = levelled_frame(rows, levels)
    with timed("  one_way over the source levels"):
        summary = one_way(
            frame, column="territory", exposure_column="exposure_years",
            claim_count_column="claim_count", claim_amount_column="claim_amount_minor",
        )
    source = tuple(summary.rows)

    from pricing_core.modelling.groupings import _hierarchical

    proposal = GroupingProposal(
        dataset_version_id=uuid4(), column="territory",
        method=GroupingMethod.HIERARCHICAL_CLUSTERING, n_groups=groups,
        unseen_level_behaviour=UnseenLevelBehaviour.MAP_TO_DEFAULT,
    )
    with timed("  ward linkage + fcluster alone"):
        clusters = _hierarchical(source, proposal)
    mapping = {
        row.level: f"G{index:03d}"
        for index, cluster in enumerate(clusters)
        for row in cluster
    }
    with timed("  grouping_evidence, source supplied"):
        grouping_evidence(
            frame, mapping, column="territory", exposure_column="exposure_years",
            claim_count_column="claim_count", claim_amount_column="claim_amount_minor",
            source=source,
        )
def _fit_glm_once(frame: pl.DataFrame, *, label: str) -> tuple[object, object, float]:
    dataset_id = uuid4()
    factors = factor_set(frame, dataset_id)
    spec = glm_spec(uuid4(), factors)
    with timed(label) as slot:
        fit = fit_glm(frame, spec, factors, seed=0)
    return fit, (spec, factors), slot[0]


def bench_glm(rows: int, factors: int) -> float:
    print(f"\nNFR-MODEL-1 — {rows:,} rows x {factors} factors, budget 600 s at 5 M x 60")
    frame = synthesise(rows, factors)
    _, _, elapsed = _fit_glm_once(frame, label="NFR-MODEL-1 glm fit")
    return elapsed


def bench_gbm(rows: int, factors: int, rounds: int) -> float:
    """NFR-MODEL-2's fit, and NFR-MODEL-11's artifact on the path the 50 MB budget names.

    The GLM arm's diagnostics artifact is small because a GLM has no SHAP dependence and no
    partial dependence. NFR-MODEL-11 names exactly those, so measuring only the GLM arm
    would report the budget as met on the path that was never the risk.
    """
    print(
        f"\nNFR-MODEL-2 — {rows:,} rows x {factors} factors x {rounds} trees, "
        "budget 1200 s at 5 M x 60 x 500"
    )
    frame = synthesise(rows, factors)
    split = int(rows * 0.75)
    train, holdout = frame.head(split), frame.tail(rows - split)
    dataset_id = uuid4()
    factor_objects = factor_set(frame, dataset_id)
    spec = gbm_spec(uuid4(), factor_objects, rounds=rounds)
    with timed("NFR-MODEL-2 gbm fit, 500 trees") as slot:
        fit = fit_gbm(train, spec, factor_objects)
    with timed("NFR-MODEL-11 gbm diagnostics"):
        computed = compute_gbm_diagnostics(
            fit.result, fit.booster_bytes or b"", spec, factor_objects,
            train=train, holdout=holdout, eval_curve=fit.eval_curve,
        )
    _artifact_size(computed, fit)
    return slot[0]


def bench_diagnostics(rows: int, factors: int, *, type_iii: bool) -> None:
    """NFR-MODEL-4: diagnostics must add no more than 30 % to fit wall-clock.

    A ratio needs no data scale, which is why this one is measurable today. Both halves are
    timed here; the platform emits the same pair per fit as `diagnostics_seconds` /
    `diagnostics_over_fit` on `app.worker.model`'s "diagnostics complete" line.

    **Measured with and without FR-MODEL-51's type-III tests**, because those drop each
    factor and *refit*: the cost is one extra GLM fit per factor, so the ratio the budget is
    stated against is a function of the factor count and not of the data. Separating the two
    arms is what turns "diagnostics is slow" into a number that names its cause.
    """
    print(f"\nNFR-MODEL-4 — {rows:,} rows x {factors} factors, budget 30 % of fit")
    frame = synthesise(rows, factors)
    split = int(rows * 0.75)
    train, holdout = frame.head(split), frame.tail(rows - split)

    dataset_id = uuid4()
    factor_objects = factor_set(train, dataset_id)
    spec = glm_spec(uuid4(), factor_objects)
    with timed("NFR-MODEL-4 glm fit (denominator)") as fit_slot:
        fit = fit_glm(train, spec, factor_objects, seed=0)

    with timed("NFR-MODEL-4 diagnostics, no type-III") as base_slot:
        computed = compute_diagnostics(
            fit.result, spec, factor_objects, train=train, holdout=holdout, type_iii=False
        )
    _ratios("without FR-MODEL-51's type-III refits", base_slot[0], fit_slot[0], fit)

    if type_iii:
        with timed(f"NFR-MODEL-4 diagnostics, type-III ({factors} refits)") as full_slot:
            computed = compute_diagnostics(
                fit.result, spec, factor_objects, train=train, holdout=holdout, type_iii=True
            )
        _ratios("with type-III (what the platform runs)", full_slot[0], fit_slot[0], fit)

    _artifact_size(computed, fit)


def _ratios(name: str, diagnostics: float, wall: float, fit: object) -> None:
    """Two denominators, because the requirement says "fit wall-clock" and the code offers
    two readings of it. `fit_seconds` is the artifact's own number and excludes factor
    resolution and design-matrix construction; the timed block is what a caller waits for.
    Both are reported: which one NFR-MODEL-4 means is a question for `02` §9, and picking
    one silently would answer it by arithmetic."""
    print(f"\n  {name}: {diagnostics:.2f} s of diagnostics")
    for label, denominator in (
        ("fit wall-clock (resolve + design + solve)", wall),
        ("fit_seconds, as the artifact records it", fit.result.fit_seconds),
    ):
        ratio = diagnostics / denominator if denominator else float("nan")
        print(
            f"    / {label:<44} = {ratio:8.1%}   "
            f"({'within' if ratio <= 0.30 else 'OVER'})   [{denominator:.2f} s]"
        )


def _artifact_size(computed: object, fit: object) -> None:
    """NFR-MODEL-11: the diagnostics artifact stays under 50 MB.

    Measured as the JSON the platform stores — `DiagnosticsRow.payload` is one JSONB
    document, so the serialised length *is* the size, not a proxy for it.
    """
    payload: dict[str, object] = {}
    for name in ("universal", "complexity", "glm", "gbm"):
        part = getattr(computed, name, None)
        if part is not None:
            payload[name] = part.model_dump(mode="json")
    encoded = json.dumps(payload).encode()
    print(
        f"\nNFR-MODEL-11 — diagnostics artifact {len(encoded) / 1e6:.2f} MB "
        f"of a 50 MB budget ({len(encoded) / 50e6:.1%})"
    )
    for name, part in payload.items():
        print(f"    {name:<12} {len(json.dumps(part).encode()) / 1e6:8.3f} MB")


def bench_certify() -> None:
    """NFR-MODEL-5: certification, including the synthetic smoke fit, under 3 minutes.

    Every template at the **default** grid the platform would use — 2 000 points, and the
    `y`/`f` ranges `app.platform.objectives.default_sampling` derives from the template's
    own applicability. Replicated here rather than imported so this script stays a
    `pricing-core` client (ADR-0001's boundary, and `bench-data.py`'s shape); the suite's
    300- and 1 000-point grids exist to keep tests fast and would understate this budget by
    the factor the density was reduced by.
    """
    print("\nNFR-MODEL-5 — every template, 2 000-point grid, budget 180 s")
    for template in ObjectiveTemplate:
        applicability = TEMPLATE_APPLICABILITY[template]
        params = {
            parameter.name: parameter.default
            for parameter in TEMPLATE_PARAMETERS[template]
            if parameter.default is not None
        }
        for parameter in TEMPLATE_PARAMETERS[template]:
            if parameter.default is None:
                # §4.5 gives no default for a cap or a threshold, "because there is no
                # amount that is right by default". Take the middle of the declared range
                # rather than skip the template: the budget is about the grid and the smoke
                # fit, and both run whatever the parameter is.
                params[parameter.name] = _mid(parameter)
        try:
            objective = CustomObjective(
                id=new_uuid7(), slug=f"bench-{template.value.replace('_', '-')}", version=1,
                template=template, params=params, applicability=applicability,
                hessian_strategy=HessianStrategy.CLIP_TO_MIN, hessian_min=1e-6,
                status=ObjectiveStatus.DRAFT,
            )
            with timed(f"NFR-MODEL-5 certify {template.value}"):
                certify_objective(objective, sampling=_default_sampling(applicability.responses))
        except Exception as exc:
            # A template this fixture cannot build is a finding about the fixture, not
            # about the budget. Say which, and carry on.
            print(f"  {template.value:<44} skipped: {type(exc).__name__}: {exc}")


def _mid(parameter: TemplateParameter) -> float | int:
    """A value inside a required parameter's declared range."""
    low = parameter.minimum if parameter.minimum is not None else 0.0
    high = parameter.maximum if parameter.maximum is not None else low + 1_000_000.0
    value = (low + high) / 2.0
    return int(value) if parameter.kind == "money_minor" else value


def _default_sampling(responses: frozenset[ResponseKind]) -> SamplingSpec:
    """`app.platform.objectives.default_sampling`, replicated. Keep the two in step."""
    probability = frozenset({ResponseKind.CONVERSION, ResponseKind.RETENTION})
    if responses <= probability:
        return SamplingSpec(
            n_points=2_000, seed=20260818, y_range=(0.0, 1.0), f_range=(-6.0, 6.0),
            w_range=(0.01, 10.0),
        )
    y_high = 20.0 if responses <= frozenset({ResponseKind.CLAIM_COUNT}) else 1_000_000.0
    return SamplingSpec(
        n_points=2_000, seed=20260818, y_range=(0.0, y_high),
        f_range=(-5.0, math.ceil(math.log(y_high)) + 1.0), w_range=(0.01, 10.0),
    )


def bench_curve(scales: list[int], factors: int, rounds: int, *, gbm: bool) -> None:
    """NFR-MODEL-1/-2/-10 at scales that fit, with the growth exponent stated.

    `t = a·n^b` fitted by least squares on `(log n, log t)`. `b` is what makes the
    extrapolation defensible or not: at `b ≈ 1` the path is linear in rows and projecting
    is arithmetic; at `b > 1` the projection is a lower bound and the honest verdict is
    that the budget is unmeasured at its stated scale.
    """
    print(f"\nNFR-MODEL-1/2/10 growth curve — {factors} factors, {len(scales)} scales")
    glm_points: list[tuple[int, float, float, float]] = []
    gbm_points: list[tuple[int, float, float, float]] = []
    for rows in scales:
        frame = synthesise(rows, factors)
        dataset_id = uuid4()
        factor_objects = factor_set(frame, dataset_id)

        spec = glm_spec(uuid4(), factor_objects)
        with timed(f"  glm  {rows:>9,} rows") as slot:
            fit_glm(frame, spec, factor_objects, seed=0)
        glm_points.append((rows, slot[0], results[-1][2], results[-1][3]))

        if gbm:
            gspec = gbm_spec(uuid4(), factor_objects, rounds=rounds)
            with timed(f"  gbm  {rows:>9,} rows") as slot:
                fit_gbm(frame, gspec, factor_objects)
            gbm_points.append((rows, slot[0], results[-1][2], results[-1][3]))
        del frame, factor_objects

    _report_curve("NFR-MODEL-1 GLM", glm_points, BUDGETS["NFR-MODEL-1 glm fit"])
    if gbm:
        _report_curve(
            f"NFR-MODEL-2 GBM ({rounds} trees)",
            gbm_points,
            BUDGETS["NFR-MODEL-2 gbm fit, 500 trees"],
        )


def _report_curve(
    label: str, points: list[tuple[int, float, float, float]], budget: float
) -> None:
    """`t = a·n^b` by least squares on `(log n, log t)`, fitted on **both** clocks.

    The exponent is what makes the extrapolation defensible or not: at `b ~ 1` the path is
    linear in rows and projecting is arithmetic; at `b > 1` the projection is a lower bound
    and the honest verdict is that the budget is unmeasured at its stated scale.

    Fitted on CPU seconds as well as wall-clock because this machine is shared. Contention
    inflates wall-clock by a factor that varies run to run; if it is roughly constant across
    the scales it cancels out of the *exponent* and shifts only the intercept — so two
    exponents that agree say the shape is trustworthy even where the level is not.
    """
    if len(points) < 2:
        return
    xs = np.log(np.array([p[0] for p in points], dtype=float))

    def fit(values: list[float]) -> tuple[float, float, float]:
        ys = np.log(np.array(values, dtype=float))
        slope, intercept = np.polyfit(xs, ys, 1)
        residual = ys - (slope * xs + intercept)
        r2 = 1.0 - float(np.sum(residual**2)) / float(np.sum((ys - ys.mean()) ** 2) or 1.0)
        return float(slope), float(intercept), r2

    wall_b, wall_a, wall_r2 = fit([p[1] for p in points])
    cpu_b, cpu_a, cpu_r2 = fit([p[3] for p in points])
    mem_b, mem_a, mem_r2 = fit([p[2] for p in points])

    projected = math.exp(wall_a) * TARGET_ROWS**wall_b
    projected_cpu = math.exp(cpu_a) * TARGET_ROWS**cpu_b
    projected_mb = math.exp(mem_a) * TARGET_ROWS**mem_b

    print(f"\n  {label}")
    print(f"    wall:  t = {math.exp(wall_a):.3g} * n^{wall_b:.3f}   (R^2 = {wall_r2:.4f})")
    print(f"    cpu:   t = {math.exp(cpu_a):.3g} * n^{cpu_b:.3f}   (R^2 = {cpu_r2:.4f})")
    print(f"    RSS:   m = {math.exp(mem_a):.3g} * n^{mem_b:.3f}   (R^2 = {mem_r2:.4f})")
    for rows, elapsed, peak, cpu in points:
        print(
            f"      {rows:>9,} rows  {elapsed:8.2f} s wall  {cpu:8.2f} s cpu   "
            f"peak RSS {peak:7,.0f} MB"
        )
    verdict = "within" if projected <= budget else "OVER"
    print(
        f"    EXTRAPOLATED to {TARGET_ROWS:,}: {projected:,.0f} s wall "
        f"({projected_cpu:,.0f} s cpu) / {budget:,.0f} s budget - {verdict}"
    )
    print(
        f"    EXTRAPOLATED peak RSS: {projected_mb / 1000:,.1f} GB / 32 GB "
        f"(NFR-MODEL-10) - {'within' if projected_mb / 1000 <= 32 else 'OVER'}"
    )
    if wall_b > 1.15 or cpu_b > 1.15:
        print(
            f"    NOTE: n^{max(wall_b, cpu_b):.2f} is super-linear; the projection above "
            "is a LOWER bound and the budget is unmeasured at its stated scale."
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        choices=(
            "all", "proposals", "breakdown", "glm", "gbm", "diagnostics", "certify",
            "curve",
        ),
        default="all",
        help="Run one phase in a fresh process. Peak RSS is a process high-water mark and "
             "glibc does not return freed arenas, so a phase measured after another "
             "inherits its peak — NFR-MODEL-10 needs the isolation.",
    )
    parser.add_argument("--rows", type=int, default=678_013, help="freMTPL2's row count")
    parser.add_argument("--factors", type=int, default=TARGET_FACTORS)
    parser.add_argument("--levels", type=int, default=10_000, help="NFR-MODEL-3's scale")
    parser.add_argument("--bands", type=int, default=20)
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--rounds", type=int, default=500, help="NFR-MODEL-2's tree count")
    parser.add_argument(
        "--scales",
        default="100000,200000,400000,678013",
        help="Comma-separated row counts for --only curve",
    )
    parser.add_argument("--no-gbm", action="store_true", help="curve: GLM only")
    parser.add_argument(
        "--skip-type-iii",
        action="store_true",
        help="diagnostics: omit FR-MODEL-51's per-factor refits, which are one extra "
             "GLM fit each and dominate the wall-clock at any real factor count.",
    )
    args = parser.parse_args()

    print(f"machine: {machine()}")
    print(f"baseline RSS after imports: {_rss_mb():,.0f} MB")

    if args.only in ("all", "proposals"):
        bench_proposals(args.rows, args.levels, args.bands, args.groups)
    if args.only == "breakdown":
        bench_breakdown(args.rows, args.levels, args.groups)
    if args.only in ("all", "glm"):
        bench_glm(args.rows, args.factors)
    if args.only in ("all", "gbm"):
        bench_gbm(args.rows, args.factors, args.rounds)
    if args.only in ("all", "diagnostics"):
        bench_diagnostics(args.rows, args.factors, type_iii=not args.skip_type_iii)
    if args.only in ("all", "certify"):
        bench_certify()
    if args.only == "curve":
        bench_curve(
            [int(s) for s in args.scales.split(",")],
            args.factors,
            args.rounds,
            gbm=not args.no_gbm,
        )

    if results:
        print("\n  against the budgets stated at this scale:")
        for label, elapsed, _peak, _cpu in results:
            budget = BUDGETS.get(label)
            if budget is None:
                continue
            print(
                f"  {label:<44} {elapsed:8.2f} s / {budget:7.1f} s   "
                f"{'within' if elapsed <= budget else 'OVER'}"
            )
        print(f"  peak RSS across the run: {max(r[2] for r in results):,.0f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
