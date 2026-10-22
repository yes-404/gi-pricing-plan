#!/usr/bin/env python3
"""WK-1178 / SL-1736 / PL-1735: the P2 NFR measurement sweep harness.

    uv run python scripts/measure-p2-nfr-sweep.py contention run --role A --out FILE
    uv run python scripts/measure-p2-nfr-sweep.py contention summarize FILE
    uv run python scripts/measure-p2-nfr-sweep.py --help

One committed instrument per NFR (PL-1735): `contention` (Task 0, the load factor of this box),
then `one-way` (NFR-468), `storage` (NFR-470), `cells-diff` (NFR-1443) and `profile`
(NFR-467). NFR-485's instrument is `bench-model.py --peak hwm`. Every reading is
DIAGNOSTIC on the shared VM and every latency figure is labelled LATENCY_LABEL (DP-2).

**The thresholds, bands and reading rules are module-level constants, committed before the
first run that uses them** (PL-1735 Global Constraints: pre-register before measuring). A
change is a new commit and a re-run, both recorded in the ledger. The decision logic is pure and
unit-tested by `tests/test_measure_p2_nfr_sweep.py`; the timed phases are run alone, in a held
gate slot, by a lead-granted window, never inside a gate.

Instrument rules (PL-1735): timers at request boundaries only; no profiler, no asyncio debug
mode, no sampler or poller thread during a timed phase; memory is the kernel's `VmHWM` read
after the phase, one phase per process.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

# =============================================================================================
# Pre-registered constants. P0 = the commit that first carries this block; the ledger cites it.
# =============================================================================================

#: DP-2: on every NFR-468 and NFR-1443 figure.
LATENCY_LABEL = "server-side, in-process, excludes network"

# --- Task 0: the contention factor (DP-1, "2026-10-14 12:25:22 BST", regime confirmed 12:31:22)
#: The fixed benchmark: `bench-model.py --only proposals` at its defaults (678 013 rows,
#: --levels 10000, --groups 20); only the line below is read. Its tree is the commit.
CONTENTION_ARGS = ("scripts/bench-model.py", "--only", "proposals")
CONTENTION_LABEL = "NFR-477 propose_grouping hierarchical_clustering"
#: ALONE run (A): load1 at start strictly below this.
ALONE_LOAD_BELOW = 1.0
#: Contended run (B): load1 at start in [lo, hi) ...
CONTENDED_LOAD_START = (1.0, 2.0)
#: ... and at end strictly below this. A run outside its regime is excluded and re-run.
CONTENDED_LOAD_END_BELOW = 2.0
MIN_PAIRS = 3
#: D4 (GO "2026-10-22 11:53:15 BST"): an ALONE start may settle this long, then STOP to the lead.
ALONE_SETTLE_MAX_S = 600
SETTLE_POLL_S = 15

# --- The sweep's thresholds and reading rules (DP-1, DP-3, the NFR sections of PL-1735)
#: Interim DP-1 band, accepted 12:25:22 (ii) as the conservative rounding of 1/2.3. Replaced by
#: `band_from_factor(max factor)` once Task 0's reading is in the ledger (commit P1).
NEAR_BOUND_FRACTION = 0.43
#: Budgets in ms (NFR-468: p95 < 300 ms; NFR-1443: page p95 <= 300 ms; NFR-467: 300 s).
THRESHOLDS_MS = {"NFR-468": 300.0, "NFR-1443": 300.0, "NFR-467": 300_000.0}
#: NFR-1443's p95(250 000) / p95(10 000) bands: <= 1.5 PASS, <= 2.0 NEAR-BOUND, above OVER.
RATIO_BANDS = (1.5, 2.0)
#: NFR-470 (DP-3 (b)): (payload + overhead) / payload <= 1.2, source upload excluded; dedup = 0
#: new parquet bytes for the identical table.
NFR_470_RULE = {"ratio_max": 1.2, "dedup_new_bytes": 0, "source_upload_excluded": True}
#: NFR-467 at 10 M (12:42:55 entry; r < 5.0 accepted 13:21:41 as DERIVED from "sub-linear").
NFR_467_RULE = {
    "sizes": [2_000_000, 10_000_000],
    "columns": 80,
    "time_budget_s": 300,
    "memory_ratio_below": 5.0,
    "mem_available_min_gb": 16,
    "disk_free_min_gb": 12,
}
#: NFR-485: peak VmHWM <= 32 GiB at 5 M x 60 (a projection is never read as a verdict).
NFR_485_CAP_BYTES = 32 * 2**30
#: NFR-468 / NFR-1443 request counts.
NFR_468_WARMUP, NFR_468_N = 20, 200
NFR_1443_N, NFR_1443_LIMIT, NFR_1443_SEEDED_JOBS = 100, 50, 10_000

# =============================================================================================
# Pure decision logic (unit-tested)
# =============================================================================================


def run_validity(role: str, load_start: float, load_end: float) -> tuple[bool, str]:
    """Is a contention run inside its regime? Returns (valid, reason); reason is "" if valid."""
    if role == "A":
        if load_start < ALONE_LOAD_BELOW:
            return True, ""
        return False, f"ALONE start load1 {load_start} >= {ALONE_LOAD_BELOW}"
    if role == "B":
        lo, hi = CONTENDED_LOAD_START
        if not lo <= load_start < hi:
            return False, f"contended start load1 {load_start} outside [{lo}, {hi})"
        if not load_end < CONTENDED_LOAD_END_BELOW:
            return False, f"contended end load1 {load_end} >= {CONTENDED_LOAD_END_BELOW}"
        return True, ""
    raise ValueError(f"role must be A or B, not {role!r}")


def band_from_factor(factor: float) -> float | None:
    """DP-1: the band is 1 / factor rounded DOWN to 2 decimals; a factor <= 1 gives none."""
    if factor <= 1.0:
        return None
    return math.floor(100 / factor) / 100


def contention_factor(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Pair interleaved A, B runs and return the factor (the MAX of the per-pair B/A wall ratios).

    An invalid run is excluded (never paired). Each valid A pairs with the next valid B; a valid
    A replaced by a later A before any B, and a valid B with no pending A, are reported as
    unpaired, never dropped silently.
    """
    excluded: list[dict[str, Any]] = []
    unpaired: list[dict[str, Any]] = []
    ratios: list[float] = []
    pending: dict[str, Any] | None = None
    for run in runs:
        ok, reason = run_validity(run["role"], run["load_start"], run["load_end"])
        if not ok:
            excluded.append({**run, "reason": reason})
            continue
        if run["role"] == "A":
            if pending is not None:
                unpaired.append(pending)
            pending = run
        else:
            if pending is None:
                unpaired.append(run)
                continue
            ratios.append(run["wall_s"] / pending["wall_s"])
            pending = None
    if pending is not None:
        unpaired.append(pending)
    result: dict[str, Any] = {
        "pairs": len(ratios),
        "ratios": ratios,
        "excluded": excluded,
        "unpaired": unpaired,
        "factor": None,
        "min": None,
        "spread": None,
        "band": None,
        "note": "",
    }
    if len(ratios) < MIN_PAIRS:
        result["note"] = f"fewer than {MIN_PAIRS} pairs: no factor"
        return result
    result["factor"] = max(ratios)
    result["min"] = min(ratios)
    result["spread"] = max(ratios) - min(ratios)
    result["band"] = band_from_factor(max(ratios))
    if result["band"] is None:
        result["note"] = "factor <= 1.0: band reported to the lead, not applied"
    return result


_BENCH_LINE = re.compile(
    re.escape(CONTENTION_LABEL) + r"\s+([\d.]+) s wall\s+([\d.]+) s cpu"
)


def parse_bench_line(output: str) -> tuple[float, float]:
    """(wall seconds, cpu seconds) of the named benchmark line in `bench-model.py`'s output."""
    found = _BENCH_LINE.search(output)
    if found is None:
        raise ValueError(f"no {CONTENTION_LABEL!r} line in the benchmark output")
    return float(found.group(1)), float(found.group(2))


def classify_latency(value: float, *, budget: float, fraction: float) -> str:
    """DP-1: <= fraction x budget PASS; above it and <= budget NEAR-BOUND; above budget OVER."""
    if value <= fraction * budget:
        return "DIAGNOSTIC-PASS"
    if value <= budget:
        return "NEAR-BOUND"
    return "DIAGNOSTIC-OVER"


def classify_ratio(ratio: float) -> str:
    """NFR-1443's 2x property: its own bands, since contention can move it either way."""
    lo, hi = RATIO_BANDS
    if ratio <= lo:
        return "DIAGNOSTIC-PASS"
    if ratio <= hi:
        return "NEAR-BOUND"
    return "DIAGNOSTIC-OVER"


def nearest_rank(values: list[float], percentile: float) -> float:
    """Nearest-rank percentile: the value at rank ceil(p/100 x n) of the sorted sample."""
    if not values:
        raise ValueError("nearest_rank of an empty sample")
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile / 100 * len(ordered)))
    return ordered[rank - 1]


def classify_storage(payload: int, overhead: int, dedup_new_bytes: int) -> str:
    """NFR-470 (DP-3 (b)): (payload + overhead) / payload <= 1.2 and dedup adds 0 new bytes."""
    if payload <= 0:
        raise ValueError("NFR-470 needs a positive parquet payload")
    ok = (payload + overhead) * 10 <= payload * 12 and (
        dedup_new_bytes == NFR_470_RULE["dedup_new_bytes"]
    )
    return "DIAGNOSTIC-PASS" if ok else "DIAGNOSTIC-OVER"


def memory_ratio(delta_large: float, delta_small: float) -> float:
    """NFR-467: r = delta-peak(10 M) / delta-peak(2 M)."""
    if delta_small <= 0:
        raise ValueError("the 2 M delta-peak must be positive")
    return delta_large / delta_small


def classify_nfr467_memory(ratio: float) -> str:
    """r < 5.0 is sub-linear (the row's amendment); r >= 5.0 is OVER."""
    return "PASS" if ratio < NFR_467_RULE["memory_ratio_below"] else "OVER"


def classify_nfr485(vmhwm_bytes: int) -> str:
    return "PASS" if vmhwm_bytes <= NFR_485_CAP_BYTES else "OVER"


def parse_status_kb(text: str, key: str) -> int:
    """A `/proc/<pid>/status` field in bytes (the file reports kB)."""
    for line in text.splitlines():
        if line.startswith(key + ":"):
            return int(line.split()[1]) * 1024
    raise ValueError(f"{key} not in the status text")


# =============================================================================================
# Host readings
# =============================================================================================


def read_load1() -> float:
    with open("/proc/loadavg") as handle:
        return float(handle.read().split()[0])


def read_status_bytes(key: str) -> int:
    with open("/proc/self/status") as handle:
        return parse_status_kb(handle.read(), key)


def mem_available_gb() -> float:
    with open("/proc/meminfo") as handle:
        for line in handle:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 2**20
    raise ValueError("MemAvailable not in /proc/meminfo")


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()


def session_header() -> dict[str, Any]:
    """PL-1735 Task 0 Step 5: what every session records at its start and end."""
    def run(*cmd: str) -> str:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

    return {
        "head": git_head(),
        "tree": run("git", "-C", str(ROOT), "rev-parse", "HEAD^{tree}"),
        "nproc": os.cpu_count(),
        "loadavg": open("/proc/loadavg").read().strip(),
        "meminfo_available_gb": round(mem_available_gb(), 2),
        "pgrep": run("pgrep", "-af", "[p]ytest|[v]itest|[f]lock"),
        "at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }


# =============================================================================================
# Task 0: the contention subcommand
# =============================================================================================


def _contention_run(role: str, out: Path) -> int:
    if role == "A":
        waited = 0
        while read_load1() >= ALONE_LOAD_BELOW and waited < ALONE_SETTLE_MAX_S:
            time.sleep(SETTLE_POLL_S)
            waited += SETTLE_POLL_S
        if read_load1() >= ALONE_LOAD_BELOW:
            print(
                f"STOP: load1 {read_load1()} >= {ALONE_LOAD_BELOW} after {waited} s of settling "
                "(D4: record the reading and report to the lead; no run taken)"
            )
            return 3
    head = git_head()
    load_start = read_load1()
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    proc = subprocess.run(
        [sys.executable, *CONTENTION_ARGS], cwd=ROOT, capture_output=True, text=True
    )
    load_end = read_load1()
    if proc.returncode != 0:
        print(proc.stdout, proc.stderr, sep="\n")
        return proc.returncode
    wall, cpu = parse_bench_line(proc.stdout)
    valid, reason = run_validity(role, load_start, load_end)
    record = {
        "role": role, "tree": head, "started": started, "load_start": load_start,
        "load_end": load_end, "wall_s": wall, "cpu_s": cpu, "valid": valid, "reason": reason,
    }
    with open(out, "a") as handle:
        handle.write(json.dumps(record) + "\n")
    print(json.dumps(record))
    return 0


def _contention_summarize(path: Path) -> int:
    runs = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    trees = {r["tree"] for r in runs}
    if len(trees) > 1:
        print(f"ERROR: the factor runs span {len(trees)} trees: {sorted(trees)}")
        return 2
    result = contention_factor(runs)
    print(json.dumps(result, indent=2))
    if result["factor"] is None:
        print(f"no factor: {result['note']}")
        return 1
    print(
        f"factor (max of {result['pairs']} ratios) {result['factor']:.3f}; "
        f"min {result['min']:.3f}; spread {result['spread']:.3f}; band {result['band']}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    cont = sub.add_parser("contention", help="Task 0: re-measure the contention factor")
    cont_sub = cont.add_subparsers(dest="action", required=True)
    run = cont_sub.add_parser("run", help="one A or B run of the fixed benchmark")
    run.add_argument("--role", choices=("A", "B"), required=True)
    run.add_argument("--out", type=Path, required=True, help="JSON-lines file, appended")
    summ = cont_sub.add_parser("summarize", help="pair the runs and print the factor and band")
    summ.add_argument("file", type=Path)
    args = parser.parse_args()
    if args.command == "contention":
        if args.action == "run":
            return _contention_run(args.role, args.out)
        return _contention_summarize(args.file)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
