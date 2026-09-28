"""Spike F3 driver. Usage: run.py prep | core | cost KMAX NRUNS"""

from __future__ import annotations

import itertools
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f3_attribution as f3  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)
PQ = OUT / "portfolio.parquet"
BASE = f3.Config()


def env() -> dict:
    return {"cpus": os.cpu_count(), "load": os.getloadavg(),
            "stamp": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "polars": pl.__version__}


def prep() -> None:
    t = time.perf_counter()
    df = f3.load()
    base_cats = ["Area", "power_band", "age_band", "VehBrand", "Region"]
    df = df.with_columns(
        pl.Series("freq_v1", f3.fit_predict(df, base_cats, ["bm", "log_density"])),
        pl.Series("freq_v2", f3.fit_predict(df, base_cats + ["VehGas", "vehage_band"],
                                            ["bm", "log_density"])),
    )
    df.write_parquet(PQ)
    print(json.dumps({"rows": df.height, "claims": int(df["ClaimNb"].sum()),
                      "mean_freq_v1": float(df["freq_v1"].mean()),
                      "mean_freq_v2": float(df["freq_v2"].mean()),
                      "secs": round(time.perf_counter() - t, 1), **env()}))


def pct(x: float, t0: int) -> float:
    return round(100 * x / t0, 4)


def pctl(x: np.ndarray) -> dict:
    return {"p50": round(float(np.percentile(x, 50)), 4), "p95": round(float(np.percentile(x, 95)), 4),
            "max": round(float(x.max()), 4)}


def core(idx: list[int]) -> dict:
    """The deputy's criterion (11:39:35): D, S, R and the exact-reconciliation gate.

    All arithmetic after rounding is int64 cents. The ratios S and R are scale-free, so
    computing them on total premium cents equals computing them on §4.6's total-premium
    mean_change_pct (a common divisor, baseline total premium, cancels).
    """
    df = pl.read_parquet(PQ)
    deltas = [f3.CORE[i] for i in idx]
    k = len(deltas)
    r = f3.Rater(df, deltas, BASE)
    everything = frozenset(range(k))
    P = {s: r.premiums(frozenset(s)).to_numpy().astype(np.int64)
         for n in range(k + 1) for s in itertools.combinations(range(k), n)}
    P = {frozenset(s): v for s, v in P.items()}
    base_v, cand_v = P[frozenset()], P[everything]
    t_i = cand_v - base_v
    iso = np.stack([P[frozenset({j})] - base_v for j in range(k)], axis=1)
    res_i = t_i - iso.sum(axis=1)
    decl = np.stack([P[frozenset(range(j + 1))] - P[frozenset(range(j))] for j in range(k)], axis=1)

    # --- gate: exact reconciliation, integer cents, per policy and portfolio
    gate_a_iso = bool(np.array_equal(iso.sum(axis=1) + res_i, t_i))
    gate_a_cum = bool(np.array_equal(decl.sum(axis=1), t_i))
    # Shapley scaled by K! is an integer: phi_k * K! = sum_S |S|!(K-|S|-1)! * marginal
    kf = math.factorial(k)
    phi_s = np.zeros((len(t_i), k), dtype=np.int64)
    for s, v in P.items():
        for j in range(k):
            if j not in s:
                phi_s[:, j] += math.factorial(len(s)) * math.factorial(k - len(s) - 1) * (P[s | {j}] - v)
    gate_b_exact = bool(np.array_equal(phi_s.sum(axis=1), kf * t_i))
    # Shapley shown in cents needs rounding: count policies where rounded parts miss the total
    phi_round = np.rint(phi_s / kf).astype(np.int64)
    b_round_miss = int((phi_round.sum(axis=1) != t_i).sum())
    # largest-remainder allocation (ties -> declared order): an explicit, declared rule
    fl = np.floor_divide(phi_s, kf)
    rem = phi_s - fl * kf
    short = t_i - fl.sum(axis=1)  # 0 <= short <= K-1
    rank = np.argsort(-rem, axis=1, kind="stable")
    alloc = fl.copy()
    for pos in range(k):
        give = short > pos
        alloc[np.arange(len(t_i))[give], rank[give, pos]] += 1
    b_lr_exact = bool(np.array_equal(alloc.sum(axis=1), t_i))
    b_lr_max_dev_cents = int(np.abs(alloc * kf - phi_s).max())  # in cents x K!

    # --- portfolio S, R over D (any predecessor set is reachable by some order)
    T = int(t_i.sum()); ISO = iso.sum(axis=0); DECL = decl.sum(axis=0)
    D = int(np.abs(ISO).sum())
    marg = {j: [int((P[s | {j}] - P[s]).sum()) for s in P if j not in s] for j in range(k)}
    s_port = max(abs(m - int(DECL[j])) for j in range(k) for m in marg[j]) / D
    # cross-check against explicit permutations
    s_perm = 0
    for o in itertools.permutations(range(k)):
        seen: frozenset[int] = frozenset()
        for j in o:
            s_perm = max(s_perm, abs(int((P[seen | {j}] - P[seen]).sum()) - int(DECL[j])))
            seen = seen | {j}
    assert s_perm / D == s_port
    r_port = abs(T - int(ISO.sum())) / D

    # --- per policy evidence (D_i > 0 only)
    D_i = np.abs(iso).sum(axis=1)
    ok = D_i > 0
    s_i = np.zeros(len(t_i))
    for j in range(k):
        for s in P:
            if j not in s:
                s_i = np.maximum(s_i, np.abs((P[s | {j}] - P[s]) - decl[:, j]))
    t0 = int(base_v.sum())
    rows = [{"step": deltas[j][0],
             "isolated_pct": pct(ISO[j], t0), "cum_declared_pct": pct(DECL[j], t0),
             "cum_min_pct": pct(min(marg[j]), t0), "cum_max_pct": pct(max(marg[j]), t0),
             "shapley_pct": pct(int(phi_s[:, j].sum()) / kf, t0)} for j in range(k)]
    return {
        "set": idx, "K": k, "changes": [d[0] for d in deltas],
        "baseline_total_eur": t0 / 100, "total_change_pct": pct(T, t0),
        "D_pct": pct(D, t0), "residual_pct": pct(T - int(ISO.sum()), t0),
        "S": round(s_port, 4), "R": round(r_port, 4),
        "a_passes_set": s_port <= 0.10 and r_port <= 0.10,
        "gate": {"a_isolated_plus_residual_exact": gate_a_iso, "a_cumulative_exact": gate_a_cum,
                 "b_shapley_exact_as_rational_xKfact": gate_b_exact,
                 "b_policies_where_cent_rounded_shapley_misses_total": b_round_miss,
                 "b_largest_remainder_exact": b_lr_exact,
                 "b_lr_max_dev_cents": b_lr_max_dev_cents / kf,
                 "policies": len(t_i)},
        "per_policy": {"n_Di_gt_0": int(ok.sum()), "R_i": pctl(np.abs(res_i[ok]) / D_i[ok]),
                       "S_i": pctl(s_i[ok] / D_i[ok])},
        "steps": rows, "ratings": r.ratings + 1, **env(),
    }


def cost(kmax: int, nruns: int) -> None:
    df = pl.read_parquet(PQ)
    for k in range(3, kmax + 1):
        deltas = (f3.CORE + [f3.extra_delta(i) for i in range(len(f3._EXTRA_FACTORS))])[:k]
        times_s, times_a = [], []
        for _ in range(nruns):
            t = time.perf_counter()
            r = f3.Rater(df, deltas, BASE)
            f3.method_a(r, list(range(k)))
            times_a.append(time.perf_counter() - t)
            t = time.perf_counter()
            r = f3.Rater(df, deltas, BASE)
            f3.shapley_totals(r)
            times_s.append(time.perf_counter() - t)
            ratings = r.ratings + 1
            if times_s[-1] > 600:
                break
        print(json.dumps({"k": k, "shapley_ratings": ratings, "a_ratings": 2 * k,
                          "a_secs": [round(x, 2) for x in times_a],
                          "shapley_secs": [round(x, 2) for x in times_s], **env()}), flush=True)
        if max(times_s) > 600:
            print(json.dumps({"ceiling_k": k}), flush=True)
            return


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prep":
        prep()
    elif cmd == "core":
        print(json.dumps(core([int(x) for x in sys.argv[2].split(",")]), indent=1, default=str))
    elif cmd == "cost":
        cost(int(sys.argv[2]), int(sys.argv[3]))
