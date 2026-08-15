#!/usr/bin/env python3
"""Measure the `01` throughput budgets — NFR-DATA-1, -2, -3 (and -4's read path).

Not a CI gate. A timing assertion on a shared runner fails for reasons that have nothing
to do with the code, and a check that fails randomly teaches everyone to re-run it. This
produces numbers for a workstream closure record instead, where a human reads them once
against the budget.

    uv run python scripts/bench-data.py --rows 2000000

`--rows` exists because the budgets are stated at 10M x 80 and this machine has 13 GB:
80 float64 columns at 10M rows is 6.4 GB resident before any operation runs. Measure at a
scale that fits, print the extrapolation to 10M, and say which it is. An extrapolation
labelled as a measurement is the more expensive mistake.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from uuid import uuid4

import numpy as np
import polars as pl

_PACKAGES = Path(__file__).resolve().parent.parent / "packages"
sys.path.insert(0, str(_PACKAGES / "pricing-core" / "src"))
sys.path.insert(0, str(_PACKAGES / "model-schema" / "src"))

from model_schema import (  # noqa: E402
    RuleSetEntry,
    Severity,
    ValidationLayer,
    ValidationRule,
    ValidationRuleSet,
)
from pricing_core.data.prepare import apply_recipe  # noqa: E402
from pricing_core.data.profile import profile_frame, profile_parquet  # noqa: E402
from pricing_core.data.validate import run_validation  # noqa: E402

TARGET_ROWS = 10_000_000
COLUMNS = 80

#: rows -> the budget the spec states, in seconds
BUDGETS = {
    "NFR-DATA-1 parquet ingest+prepare": 15 * 60,
    "NFR-DATA-1 csv ingest+prepare": 30 * 60,
    "NFR-DATA-2 validation, ~50 rules": 10 * 60,
    "NFR-DATA-2 structural layer alone": 2 * 60,
    "NFR-DATA-3 profiling": 5 * 60,
}

results: list[tuple[str, float, float]] = []

PAGE_MB = os.sysconf("SC_PAGE_SIZE") / 1e6


def _rss_mb() -> float:
    """Resident set in MB. `ru_maxrss` is a process high-water mark, so it cannot give a
    per-operation peak — statm sampled during the block can."""
    with open("/proc/self/statm") as handle:
        return int(handle.read().split()[1]) * PAGE_MB


@contextmanager
def timed(label: str) -> Iterator[None]:
    peak = _rss_mb()
    stop = threading.Event()

    def sample() -> None:
        nonlocal peak
        while not stop.wait(0.02):
            peak = max(peak, _rss_mb())

    sampler = threading.Thread(target=sample, daemon=True)
    sampler.start()
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        stop.set()
        sampler.join()
    peak = max(peak, _rss_mb())
    results.append((label, elapsed, peak))
    print(f"  {label:<40} {elapsed:8.1f} s   peak RSS {peak:7,.0f} MB")


def synthesise(rows: int) -> pl.DataFrame:
    """A frame shaped like a motor exposure file: keys, dates, the money and count columns
    the profiler needs, then filler numerics up to 80 columns."""
    index = pl.int_range(0, rows, eager=True)
    data: dict[str, pl.Series] = {
        "policy_id": ("P" + index.cast(pl.Utf8)).alias("policy_id"),
        "exposure_start": pl.Series(
            "exposure_start", [date(2024, 1, 1)] * rows, dtype=pl.Date
        ),
        "exposure_end": pl.Series("exposure_end", [date(2024, 12, 31)] * rows, dtype=pl.Date),
        "exposure_years": (index % 12 + 1).cast(pl.Float64) / 12,
        "claim_count": (index % 17 == 0).cast(pl.Int64),
        "claim_amount_minor": ((index % 17 == 0).cast(pl.Int64) * (index % 500_000)),
        "vehicle_group": ("G" + (index % 50).cast(pl.Utf8)).alias("vehicle_group"),
        "postcode_area": ("A" + (index % 120).cast(pl.Utf8)).alias("postcode_area"),
        "driver_age": (18 + index % 60).cast(pl.Int64),
    }
    # Deterministic but incompressible: a modulo pattern packs 80 columns into 0.2 MB,
    # and a parquet read over that measures the decompressor's best case, not this
    # platform's. `seed` keeps the run reproducible without Polars' global RNG state.
    for i in range(COLUMNS - len(data)):
        data[f"num_{i:02d}"] = pl.Series(
            f"num_{i:02d}", np.random.default_rng(i).normal(size=rows)
        )
    return pl.DataFrame(data)


def rule_set(rules: int, *, layers: set[ValidationLayer] | None = None) -> ValidationRuleSet:
    """`rules` rules spread across the layers, matching the spec's "~50 rules" shape.

    `layers` filters to one layer so NFR-DATA-2's separate structural budget is a separate
    measurement rather than the same number printed twice.
    """
    entries = []
    cycle = [
        ValidationLayer.STRUCTURAL,
        ValidationLayer.STRUCTURAL,
        ValidationLayer.ACTUARIAL_SANITY,
    ]
    numerics = [f"num_{i:02d}" for i in range(COLUMNS - 9)]
    for i in range(rules):
        column = numerics[i % len(numerics)]
        check, params = (
            ("column_presence", {"columns": [column]})
            if i % 3 == 0
            else ("not_null", {"columns": [column], "key_columns": ["policy_id"]})
            if i % 3 == 1
            else ("range", {"min": -1, "key_columns": ["policy_id"]})
        )
        entries.append(
            RuleSetEntry(
                rule=ValidationRule(
                    id=uuid4(), slug=f"r{i:03d}", version=1,
                    layer=cycle[i % len(cycle)],
                    check=check, severity=Severity.FAIL,
                    target={"table": "exposure", "column": column},
                    params=params,
                )
            )
        )
    if layers is not None:
        entries = [e for e in entries if e.rule.layer in layers]
    return ValidationRuleSet(id=uuid4(), slug="bench", version=1, entries=tuple(entries))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=2_000_000)
    parser.add_argument(
        "--generate-to",
        type=Path,
        help="Write the synthetic parquet here and exit, so a later --parquet run measures "
             "a process that has never held the data. glibc does not return freed arenas, "
             "so generating and profiling in one process inflates the profiler's peak by "
             "whatever the generator allocated.",
    )
    parser.add_argument("--parquet", type=Path, help="Profile this file instead of generating one")
    parser.add_argument("--rules", type=int, default=50)
    parser.add_argument(
        "--only",
        choices=("all", "profile-frame", "profile-parquet"),
        default="all",
        help="Run one phase in a fresh process. Peak RSS is a process high-water mark and "
             "the allocator does not return freed arenas, so a phase measured after "
             "another inherits its peak — NFR-DATA-3's memory clause needs isolation.",
    )
    args = parser.parse_args()

    if args.generate_to is not None:
        args.generate_to.parent.mkdir(parents=True, exist_ok=True)
        synthesise(args.rows).write_parquet(args.generate_to)
        print(f"wrote {args.generate_to} "
              f"({args.generate_to.stat().st_size / 1e6:,.0f} MB, {args.rows:,} rows)")
        return 0

    if args.parquet is not None:
        print(f"baseline RSS after imports: {_rss_mb():,.0f} MB")
        payload = args.parquet.stat().st_size / 1e6
        with timed("NFR-DATA-3 profiling (duckdb/parquet)"):
            profile_parquet([str(args.parquet)], dataset_version_id=uuid4(),
                            one_way_columns=["vehicle_group", "postcode_area", "driver_age"])
        print(f"\n  payload {payload:,.0f} MB, peak RSS {results[-1][2]:,.0f} MB")
        return 0

    scale = TARGET_ROWS / args.rows
    workdir = Path(tempfile.mkdtemp(prefix="gip-bench-"))
    print(f"baseline RSS after imports: {_rss_mb():,.0f} MB")
    print(f"{args.rows:,} rows x {COLUMNS} columns  ({scale:.1f}x below the 10M budget scale)")
    print(f"working in {workdir}\n")

    try:
        frame = synthesise(args.rows)
        parquet, csv = workdir / "exposure.parquet", workdir / "exposure.csv"
        frame.write_parquet(parquet)
        frame.write_csv(csv)
        payload_mb = parquet.stat().st_size / 1e6
        print(f"parquet {payload_mb:,.1f} MB · csv {csv.stat().st_size / 1e6:,.1f} MB\n")
        del frame

        recipe = [
            {"step": "cast", "table": "exposure",
             "params": {"columns": {"driver_age": "int32"}}},
            {"step": "derive_expression", "table": "exposure",
             "params": {"column": "burning_cost",
                        "expression": "claim_amount_minor / exposure_years"}},
            {"step": "filter_rows", "table": "exposure",
             "params": {"expression": "exposure_years > 0"}},
        ]

        if args.only == "profile-parquet":
            with timed("NFR-DATA-3 profiling (duckdb/parquet)"):
                profile_parquet([str(parquet)], dataset_version_id=uuid4(),
                                one_way_columns=["vehicle_group", "postcode_area",
                                                 "driver_age"])
            print(f"\n  parquet payload {payload_mb:,.0f} MB, "
                  f"peak RSS {results[-1][2]:,.0f} MB "
                  f"= {results[-1][2] / payload_mb:.1f}x the payload")
            return 0
        if args.only == "profile-frame":
            with timed("NFR-DATA-3 profiling (in-memory frame)"):
                profile_frame(pl.read_parquet(parquet), dataset_version_id=uuid4(),
                              one_way_columns=["vehicle_group", "postcode_area",
                                               "driver_age"])
            print(f"\n  parquet payload {payload_mb:,.0f} MB, "
                  f"peak RSS {results[-1][2]:,.0f} MB "
                  f"= {results[-1][2] / payload_mb:.1f}x the payload")
            return 0

        with timed("NFR-DATA-1 parquet ingest+prepare"):
            tables = {"exposure": pl.read_parquet(parquet)}
            prepared = apply_recipe(tables, recipe).tables
        with timed("NFR-DATA-1 csv ingest+prepare"):
            apply_recipe({"exposure": pl.read_csv(csv)}, recipe)

        full = rule_set(args.rules)
        structural = rule_set(args.rules, layers={ValidationLayer.STRUCTURAL})
        with timed("NFR-DATA-2 validation, ~50 rules"):
            report = run_validation(prepared, full, dataset_version_id=uuid4())
        with timed("NFR-DATA-2 structural layer alone"):
            run_validation(prepared, structural, dataset_version_id=uuid4())

        # A rule that raises is guarded into an `error` result and returns immediately.
        # Timing a set of those measures the guard, so refuse to report the number.
        tally: dict[str, int] = {}
        for result in report.results:
            tally[result.outcome.value] = tally.get(result.outcome.value, 0) + 1
        print(f"    {len(full.entries)} rules -> {tally}")
        if tally.get("error"):
            raise SystemExit(
                f"{tally['error']} of {len(full.entries)} rules errored — the validation "
                "timing measures the error guard, not the rules. Fix the rule set first."
            )

        one_ways = ["vehicle_group", "postcode_area", "driver_age"]
        with timed("NFR-DATA-3 profiling"):
            profile = profile_frame(
                prepared["exposure"], dataset_version_id=uuid4(), one_way_columns=one_ways
            )
        del prepared, tables
        with timed("NFR-DATA-3 profiling (duckdb/parquet)"):
            profile_parquet([str(parquet)], dataset_version_id=uuid4(),
                            one_way_columns=one_ways)

        blob = profile.model_dump_json()
        with timed("NFR-DATA-4 read a stored one-way"):
            from model_schema import Profile

            reloaded = Profile.model_validate_json(blob)
            assert reloaded.one_ways[0].rows

        print("\n  extrapolated to 10,000,000 rows (linear in rows):")
        worst = 0.0
        for label, elapsed, _peak in results:
            budget = BUDGETS.get(label)
            projected = elapsed * scale
            if budget is None:
                print(f"  {label:<40} {projected:8.1f} s   (no stated budget)")
                continue
            verdict = "within" if projected <= budget else "OVER"
            worst = max(worst, projected / budget)
            print(f"  {label:<40} {projected:8.1f} s / {budget:5.0f} s   {verdict}")
        print(f"\n  worst case: {worst:.0%} of its budget")
        print(f"  peak RSS across the run: {max(r[2] for r in results):,.0f} MB")
        return 0
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
