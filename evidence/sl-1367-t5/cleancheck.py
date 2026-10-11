"""SL-1367 Task 5, run D: the pre-registered validity check and the information-only paired deltas.

Criterion: to-lead "2026-10-11 15:26:41 BST" item 2 (i). The run is CLEAN only if every limb-2
invocation's duration lies within +-15% of the median of all six limb-2 durations, AND every
invocation's steal is <= 5% of ALL its CPU ticks (idle and iowait included).
Amended by Q3 (b), to-lead "2026-10-11 15:32:42 BST", before any run-D data: the
denominator of the verdict's steal test is all ticks, not busy ticks; both ratios are printed,
the verdict uses steal_all.

Usage: cleancheck.py clean  <stamps.tsv>
       cleancheck.py paired <out.jsonl>
stamps.tsv columns: label, limb, tree, iter, start, end, dur_s, steal_ticks, busy_ticks, all_ticks
(busy = user+nice+system+irq+softirq+steal; all = busy + idle + iowait; /proc/stat "cpu " line).
"""

import json
import statistics
import sys

DUR_TOL_PCT = 15.0
STEAL_MAX_PCT = 5.0
LIMB2_COUNT = 6


def _read_stamps(path: str) -> list[dict[str, str]]:
    keys = ("label", "limb", "tree", "iter", "start", "end", "dur_s", "steal", "busy", "all")
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    return [dict(zip(keys, ln.split("\t"), strict=True)) for ln in lines]


def clean(path: str) -> bool:
    rows = _read_stamps(path)
    limb2 = [r for r in rows if r["limb"] == "2"]
    bad: list[str] = []
    if len(limb2) != LIMB2_COUNT:
        bad.append(f"limb 2 has {len(limb2)} invocations, want {LIMB2_COUNT}")
        median = float("nan")
    else:
        median = statistics.median(float(r["dur_s"]) for r in limb2)
    print(
        f"CLEAN CHECK (15:26:41 item 2 (i)): limb-2 median duration {median:.1f} s; "
        f"tolerance +-{DUR_TOL_PCT:g}%, steal_all <= {STEAL_MAX_PCT:g}% of all ticks (verdict); "
        "steal_busy printed"
    )
    for r in rows:
        dur, steal = float(r["dur_s"]), int(r["steal"])
        busy, tot = int(r["busy"]), int(r["all"])
        busy_pct = 100.0 * steal / busy if busy > 0 else float("inf")
        steal_pct = 100.0 * steal / tot if tot > 0 else float("inf")
        notes = []
        if r["limb"] == "2":
            pct = 100.0 * (dur - median) / median if median == median else float("nan")
            shown = f"{pct:+.1f}% from median"
            if not abs(pct) <= DUR_TOL_PCT:
                notes.append("duration")
        else:
            shown = "n/a (limb 1+3: not in the median)"
        if not steal_pct <= STEAL_MAX_PCT:
            notes.append("steal_all")
        if notes:
            bad.append(f"{r['label']} (limb {r['limb']}, {r['tree']}): {'+'.join(notes)}")
        print(
            f"  {r['label']:<16} limb {r['limb']} {r['tree']:<4} {r['start']} -> {r['end']}  "
            f"{dur:7.1f} s  {shown}; steal {r['steal']} ticks: steal_busy {busy_pct:.2f}% "
            f"steal_all {steal_pct:.2f}%  "
            f"{'OK' if not notes else 'FAIL ' + '+'.join(notes)}"
        )
    print("CLEAN" if not bad else "UNCLEAN (" + "; ".join(bad) + ")")
    return not bad


def paired(path: str) -> None:
    with open(path) as fh:
        rows = [json.loads(ln) for ln in fh if ln.strip()]
    print(
        "PAIRED per-iteration p99 deltas, HEAD - base (INFORMATION ONLY (15:26:41 item 3); "
        "the verdict is the plan's median statistic)"
    )
    for route in ("/score", "/score/compare"):
        limb2 = [r for r in rows if r.get("limb") == 2 and r["route"] == route]
        b = [r["p99_ms"] for r in limb2 if r["tree"] == "base"]
        h = [r["p99_ms"] for r in limb2 if r["tree"] == "HEAD"]
        for i, (bv, hv) in enumerate(zip(b, h, strict=False), start=1):
            print(
                f"  {route:<15} iteration {i}: base {bv:8.3f}  HEAD {hv:8.3f}  "
                f"delta {hv - bv:+8.3f} ms"
            )
        if len(b) != 3 or len(h) != 3:
            print(f"  {route}: INCOMPLETE ({len(b)} base, {len(h)} HEAD)")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "clean":
        clean(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "paired":
        paired(sys.argv[2])
    else:
        sys.exit(__doc__)
