"""SL-1455 Task 0 Step 5 tabulation — SCRATCH. Reads a `t0_driver.py` output tree, prints
markdown for the ledger: per arm and rate (three runs pooled, runs also listed) p50/p99/max of
each phase; checkouts and statements; slot hits/misses; GC and loop-stall maxima; every
request of 100 ms or more with its dominant phase and the events overlapping it; the
slow-callback lines; py-spy's top frames by self time.

Usage: python3 -I t0_analyse.py <out dir>
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PHASES = ["total", "auth", "auth_scope", "rbac", "rbac_scope", "rate_limit", "serving_ref", "fetch_bundle",
          "compiled_for", "score_one", "sample_trace", "serialise"]
#: Disjoint phases a request's "dominant" label is chosen from (scopes overlap their inner calls).
LEAVES = ["auth_scope", "rbac_scope", "rate_limit", "serving_ref", "compiled_for", "score_one",
          "sample_trace", "serialise"]


def pct(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    return ordered[min(int(len(ordered) * p), len(ordered) - 1)]


def jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_pass(d: Path) -> dict[str, Any]:
    client = json.loads((d / "client.json").read_text())
    start = client["measure_from"]
    reqs = [r for r in jsonl(d / "requests.jsonl") if r["t"] >= start and r.get("status") == 200]
    events = [e for e in jsonl(d / "events.jsonl") if e["t"] >= start]
    log = (d / "server.log").read_text(errors="replace") if (d / "server.log").exists() else ""
    slow = [ln for ln in log.splitlines() if "took" in ln and "seconds" in ln]
    return {"dir": d, "client": client, "reqs": reqs, "events": events, "slow": slow}


def row(name: str, values: list[float]) -> str:
    return (f"| {name} | {pct(values, .5):.2f} | {pct(values, .99):.2f} | "
            f"{max(values) if values else float('nan'):.2f} |")


def overlap(req: dict[str, Any], events: list[dict[str, Any]]) -> list[str]:
    """Events inside the request's own wall-clock window (`t` is its start)."""
    end = req["t"] + req["phases"]["total"] / 1000
    out = []
    for e in events:
        if e["kind"] == "gc" and req["t"] - e["ms"] / 1000 <= e["t"] <= end:
            out.append(f"gc gen{e['generation']} {e['ms']:.0f} ms")
        elif e["kind"] == "loop_stall" and req["t"] <= e["t"] <= end + 0.05:
            out.append(f"loop_stall {e['late_ms']:.0f} ms")
        elif e["kind"] in ("slow_checkout", "new_connection") and req["t"] <= e["t"] <= end:
            out.append(e["kind"] + (f" {e['ms']:.0f} ms" if "ms" in e else ""))
    return out


def summarise_profile(path: Path, top: int = 12) -> list[str]:
    """`py-spy --format raw`: `frame;frame;frame count`. Self time = the last frame."""
    selfs: Counter[str] = Counter()
    total = 0
    for line in path.read_text().splitlines():
        stack, _, count = line.rpartition(" ")
        if not stack:
            continue
        n = int(count)
        total += n
        selfs[stack.split(";")[-1]] += n
    return [f"| {frame} | {n} | {100 * n / total:.1f}% |" for frame, n in selfs.most_common(top)]


def main(root: Path) -> None:
    for arm_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        passes = {}
        profile = None
        for d in sorted(arm_dir.iterdir()):
            if not (d / "client.json").exists():
                continue
            if d.name.endswith("profile"):
                profile = d
                continue
            rate = int(d.name.split("-")[0][1:])
            passes.setdefault(rate, []).append(load_pass(d))
        print(f"\n## Arm `{arm_dir.name}`")
        probe = arm_dir / "probe-main-handler" / "probe.json"
        if probe.exists():
            print(f"\nProbe, `main`'s handler unchanged, no ref in the body: `{probe.read_text()}`")
        for rate, runs in sorted(passes.items()):
            reqs = [r for p in runs for r in p["reqs"]]
            events = [e for p in runs for e in p["events"]]
            print(f"\n### {rate} rps offered — {len(runs)} runs, {len(reqs)} requests pooled\n")
            print("Per run: " + "; ".join(
                f"run{p['client']['run']} {p['client']['start_utc']}→{p['client']['end_utc']} "
                f"load {p['client']['load_start']:.2f}→{p['client']['load_end']:.2f} "
                f"errors {p['client']['errors']} achieved {p['client']['achieved_rps']:.1f} rps "
                f"client p99 {pct(p['client']['samples_ms'], .99):.1f} ms" for p in runs) + "\n")
            print("| phase (ms) | p50 | p99 | max |\n|---|---|---|---|")
            for ph in PHASES:
                print(row(ph, [r["phases"][ph] for r in reqs if ph in r["phases"]]))
            print(f"\nCheckouts/request p50 {pct([r.get('checkouts', 0) for r in reqs], .5):.0f}, "
                  f"checkout ms p99 {pct([r.get('checkout_ms', 0.0) for r in reqs], .99):.2f}, "
                  f"longest single {max([r.get('checkout_max_ms', 0.0) for r in reqs] or [0]):.2f}; "
                  f"statements/request p50 {pct([r.get('statements', 0) for r in reqs], .5):.0f}; "
                  f"commits/request p50 {pct([r.get('commits', 0) for r in reqs], .5):.0f}.")
            print(f"Requests whose ref the instrument filled (default-live scratch fix): "
                  f"{sum(bool(r.get('ref_filled')) for r in reqs)} of {len(reqs)}.")
            print(f"Slot hits {sum(r.get('slot_hit', 0) for r in reqs)}, "
                  f"misses {sum(r.get('slot_miss', 0) for r in reqs)} (measured window; expect 0 — "
                  "the one miss per process is in the discarded warm-up).")
            for gen in (0, 1, 2):
                ms = [e["ms"] for e in events if e["kind"] == "gc" and e["generation"] == gen]
                print(f"GC gen{gen}: {len(ms)} collections, longest {max(ms or [0]):.2f} ms.")
            stalls = [e["late_ms"] for e in events if e["kind"] == "loop_stall"]
            print(f"Loop stalls ≥ 50 ms (10 ms ticker): {len(stalls)}, longest {max(stalls or [0]):.0f} ms. "
                  f"New connections in window: {sum(e['kind'] == 'new_connection' for e in events)}.")
            slow = [ln for p in runs for ln in p["slow"]]
            print(f"asyncio slow-callback lines: {len(slow)}" + ("" if not slow else "\n```\n" + "\n".join(
                s[:300] for s in slow[:20]) + "\n```"))
            big = [r for r in reqs if r["phases"]["total"] >= 100]
            print(f"\nRequests ≥ 100 ms: {len(big)}.")
            for r in sorted(big, key=lambda r: -r["phases"]["total"])[:25]:
                dom = max(LEAVES, key=lambda k: r["phases"].get(k, 0.0))
                inner = sum(r["phases"].get(k, 0.0) for k in LEAVES)
                print(f"- total {r['phases']['total']:.0f} ms; dominant {dom} "
                      f"{r['phases'].get(dom, 0.0):.0f} ms; unaccounted "
                      f"{r['phases']['total'] - inner:.0f} ms; checkouts {r.get('checkouts', 0)} "
                      f"({r.get('checkout_ms', 0.0):.0f} ms); overlapping events: "
                      f"{', '.join(overlap(r, events)) or 'none seen'}")
        if profile is not None and (profile / "profile.txt").exists():
            print("\n### py-spy, 25 rps, top frames by self time\n\n| frame | samples | share |\n|---|---|---|")
            print("\n".join(summarise_profile(profile / "profile.txt")))
        elif profile is not None:
            print(f"\n### py-spy: no profile.txt in {profile.name}; see its server.log")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
