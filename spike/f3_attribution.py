"""Spike F3 (2026-09-28): the WK-673 attribution method, measured on freMTPL2.

Scratch only; never merged. It mirrors a motor rating algorithm in Polars (NOT the ZEN
engine) and compares three attribution methods over the full 678 013-row portfolio:

  (a) isolated + cumulative in a declared step order, with an interaction-residual line;
  (b) exact Shapley over steps (2**K portfolio re-ratings);
  (c) cumulative only (which is (a)'s cumulative column).

Money is integer cents after the final rounding; every total is an exact integer sum.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
import polars as pl
from glum import GeneralizedLinearRegressor

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "examples" / "fremtpl2" / "data" / "freMTPL2freq.arff"
sys.path.insert(0, str(HERE.parent / "examples" / "fremtpl2"))
from arff import to_csv  # noqa: E402


# --------------------------------------------------------------------------- data
def load() -> pl.DataFrame:
    df = pl.read_csv(to_csv(DATA), infer_schema_length=None)
    return df.with_columns(
        pl.col("Exposure").clip(upper_bound=1.0),
        pl.when(pl.col("DrivAge") < 21).then(pl.lit("18-20"))
        .when(pl.col("DrivAge") < 26).then(pl.lit("21-25"))
        .when(pl.col("DrivAge") < 31).then(pl.lit("26-30"))
        .when(pl.col("DrivAge") < 41).then(pl.lit("31-40"))
        .when(pl.col("DrivAge") < 51).then(pl.lit("41-50"))
        .when(pl.col("DrivAge") < 61).then(pl.lit("51-60"))
        .when(pl.col("DrivAge") < 71).then(pl.lit("61-70"))
        .otherwise(pl.lit("71+")).alias("age_band"),
        pl.col("VehPower").clip(upper_bound=12).cast(pl.Utf8).alias("power_band"),
        pl.col("VehAge").clip(upper_bound=15).floordiv(3).cast(pl.Utf8).alias("vehage_band"),
        pl.col("BonusMalus").clip(upper_bound=150).alias("bm"),
        pl.col("Density").log().alias("log_density"),
        pl.col("BonusMalus").clip(upper_bound=150).floordiv(10).cast(pl.Utf8).alias("bm_band"),
    )


def design(df: pl.DataFrame, cats: list[str], nums: list[str]) -> np.ndarray:
    parts = [df.select(nums).to_numpy().astype(float)] if nums else []
    for c in cats:
        d = df.select(pl.col(c)).to_dummies(drop_first=True)
        parts.append(d.to_numpy().astype(float))
    return np.hstack(parts)


def fit_predict(df: pl.DataFrame, cats: list[str], nums: list[str]) -> np.ndarray:
    """Poisson GLM, log link, exposure as weight on the rate (= log-exposure offset)."""
    x = design(df, cats, nums)
    y = (df["ClaimNb"] / df["Exposure"]).to_numpy()
    w = df["Exposure"].to_numpy()
    m = GeneralizedLinearRegressor(family="poisson", alpha=0, fit_intercept=True)
    m.fit(x, y, sample_weight=w)
    return m.predict(x)  # annual claim frequency


# --------------------------------------------------------------------------- algorithm
@dataclass(frozen=True)
class Config:
    freq_col: str = "freq_v1"          # which model's prediction
    severity: float = 1900.0           # € per claim
    age_rel: dict[str, float] = field(default_factory=dict)   # rate-table relativity
    extra_rel: tuple[tuple[str, tuple[tuple[str, float], ...]], ...] = ()
    expense_load: float = 0.25
    min_premium: float = 150.0
    cap_up: float | None = None        # transitional cap on increase vs baseline premium


AGE_REL_V1 = {"18-20": 1.00, "21-25": 1.00, "26-30": 1.00, "31-40": 1.00,
              "41-50": 1.00, "51-60": 1.00, "61-70": 1.00, "71+": 1.00}


def rate(df: pl.DataFrame, cfg: Config, baseline_cents: pl.Series | None) -> pl.Series:
    rel = pl.col("age_band").replace_strict(cfg.age_rel or AGE_REL_V1, default=1.0)
    p = pl.col(cfg.freq_col) * cfg.severity * rel
    for factor, table in cfg.extra_rel:
        p = p * pl.col(factor).replace_strict(dict(table), default=1.0)
    p = p * (1.0 + cfg.expense_load)
    p = pl.max_horizontal(p, pl.lit(cfg.min_premium))
    out = df.select((p * 100).round(0).cast(pl.Int64).alias("c"))["c"]
    if cfg.cap_up is not None and baseline_cents is not None:
        capped = (baseline_cents.cast(pl.Float64) * (1 + cfg.cap_up)).round(0).cast(pl.Int64)
        out = pl.select(pl.min_horizontal(out, capped)).to_series()
    return out


# --------------------------------------------------------------------------- deltas
Delta = tuple[str, Callable[[Config], Config]]

CORE: list[Delta] = [
    ("model: freq_v1 -> freq_v2 (adds VehGas, VehAge)", lambda c: replace(c, freq_col="freq_v2")),
    ("rate_table: age relativity v1 -> v2",
     lambda c: replace(c, age_rel={"18-20": 1.35, "21-25": 1.18, "26-30": 1.05, "31-40": 1.0,
                                   "41-50": 0.97, "51-60": 0.95, "61-70": 0.98, "71+": 1.10})),
    ("severity 1900 -> 1976 (+4%)", lambda c: replace(c, severity=1976.0)),
    ("expense_load 0.25 -> 0.28", lambda c: replace(c, expense_load=0.28)),
    ("min_premium 150 -> 180", lambda c: replace(c, min_premium=180.0)),
    ("cap: increase capped at +25% of baseline", lambda c: replace(c, cap_up=0.25)),
]

# Extra relativity edits used only to grow K for the Shapley cost curve.
_EXTRA_FACTORS = [("Area", "ABCDEF"), ("power_band", [str(i) for i in range(4, 13)]),
                  ("vehage_band", "012345"), ("VehBrand", [f"B{i}" for i in range(1, 15)]),
                  ("bm_band", [str(i) for i in range(5, 16)]),
                  ("Region", ["R11", "R24", "R82", "R93", "R53", "R52", "R72"]),
                  ("VehGas", ["Regular", "Diesel"]), ("Area", "ABC"), ("power_band", "4567"),
                  ("VehBrand", ["B12", "B1", "B2"]), ("bm_band", ["5", "6", "7"]),
                  ("Region", ["R11", "R82"]), ("vehage_band", "01"), ("Area", "EF")]


def extra_delta(i: int) -> Delta:
    factor, levels = _EXTRA_FACTORS[i]
    rng = np.random.default_rng(1000 + i)
    table = tuple((lvl, float(round(rng.uniform(0.9, 1.12), 3))) for lvl in levels)
    return (f"extra rel #{i} on {factor}",
            lambda c: replace(c, extra_rel=c.extra_rel + ((factor, table),)))


# --------------------------------------------------------------------------- methods
class Rater:
    def __init__(self, df: pl.DataFrame, deltas: list[Delta], base: Config) -> None:
        self.df, self.deltas, self.base = df, deltas, base
        self.baseline = rate(df, base, None)
        self.cache: dict[frozenset[int], pl.Series] = {frozenset(): self.baseline}
        self.ratings = 0

    def premiums(self, subset: frozenset[int]) -> pl.Series:
        if subset not in self.cache:
            cfg = self.base
            for k in sorted(subset):  # config composition is order-free by construction
                cfg = self.deltas[k][1](cfg)
            self.cache[subset] = rate(self.df, cfg, self.baseline)
            self.ratings += 1
        return self.cache[subset]

    def total(self, subset: frozenset[int]) -> int:
        return int(self.premiums(subset).sum())


def method_a(r: Rater, order: list[int]) -> dict:
    k_all = frozenset(range(len(r.deltas)))
    t0, t1 = r.total(frozenset()), r.total(k_all)
    iso = {k: r.total(frozenset({k})) - t0 for k in order}
    cum, applied, prev = {}, set(), t0
    for k in order:
        applied.add(k)
        cur = r.total(frozenset(applied))
        cum[k] = cur - prev
        prev = cur
    return {"total": t1 - t0, "isolated": iso, "cumulative": cum,
            "residual": (t1 - t0) - sum(iso.values())}


def shapley_totals(r: Rater) -> dict[int, float]:
    n = len(r.deltas)
    phi = dict.fromkeys(range(n), 0.0)
    for size in range(n):
        wgt = math.factorial(size) * math.factorial(n - size - 1) / math.factorial(n)
        for s in itertools.combinations(range(n), size):
            fs = frozenset(s)
            base = r.total(fs)
            for k in range(n):
                if k not in fs:
                    phi[k] += wgt * (r.total(fs | {k}) - base)
    return phi


def shapley_per_policy(df_len: int, r: Rater) -> np.ndarray:
    """Per-policy Shapley (cents), streaming over subsets: memory O(n·K)."""
    n = len(r.deltas)
    phi = np.zeros((df_len, n))
    for size in range(n):
        wgt = math.factorial(size) * math.factorial(n - size - 1) / math.factorial(n)
        for s in itertools.combinations(range(n), size):
            fs = frozenset(s)
            b = r.premiums(fs).to_numpy()
            for k in range(n):
                if k not in fs:
                    phi[:, k] += wgt * (r.premiums(fs | {k}).to_numpy() - b)
    return phi
