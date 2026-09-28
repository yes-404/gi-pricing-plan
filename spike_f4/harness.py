"""Spike F4: seed and shrink determinism across processes, hypothesis vs numpy.

Usage: python harness.py <arm> <seed> <outfile>
Writes a canonical JSON log: every generated context in call order, then the
final (shrunk) counterexample. Byte-compare the outfiles across processes.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import tempfile
from decimal import Decimal

import numpy as np
from hypothesis import HealthCheck, Phase, given, seed, settings
from hypothesis import strategies as st
from hypothesis.database import DirectoryBasedExampleDatabase
from model_schema.rating import InputContractField, RatingInputType

# A rating input contract shaped like a motor quote (FR-213 fields).
CONTRACT = [
    InputContractField(name="driver_age", type=RatingInputType.INT, min=17, max=99),
    InputContractField(name="vehicle_value", type=RatingInputType.DECIMAL,
                       min=Decimal("500.00"), max=Decimal("150000.00")),
    InputContractField(name="region", type=RatingInputType.ENUM,
                       domain=["N", "S", "E", "W", "LDN"]),
    InputContractField(name="postcode", type=RatingInputType.STRING,
                       pattern=r"[A-Z]{1,2}[0-9]{1,2} [0-9][A-Z]{2}"),
    InputContractField(name="inception", type=RatingInputType.DATE),
    InputContractField(name="garaged", type=RatingInputType.BOOL),
    InputContractField(name="ncd_years", type=RatingInputType.INT, min=0, max=9,
                       nullable=True),
]
D0, D1 = dt.date(2026, 1, 1), dt.date(2027, 12, 31)


def premium(ctx: dict) -> Decimal:
    """Toy Decimal rating: a monotone-ish premium with a planted bound breach."""
    p = Decimal("250.00")
    p *= Decimal("2.5") if ctx["driver_age"] < 25 else Decimal("1.0")
    p += ctx["vehicle_value"] * Decimal("0.004")
    p *= Decimal("1.3") if ctx["region"] == "LDN" else Decimal("1.0")
    p *= Decimal("0.9") if ctx["garaged"] else Decimal("1.0")
    ncd = ctx["ncd_years"] or 0
    p *= Decimal("1") - Decimal("0.05") * ncd
    return p.quantize(Decimal("0.01"))


LIMIT = Decimal("900.00")  # planted: young or expensive+LDN breaches it


def canon(ctx: dict) -> dict:
    out = {}
    for k, v in ctx.items():
        out[k] = str(v) if isinstance(v, Decimal) else v.isoformat() if isinstance(v, dt.date) else v
    return out


# ---- (a) hypothesis: strategies derived from the contract ------------------
def field_strategy(f: InputContractField) -> st.SearchStrategy:
    t = f.type
    if t is RatingInputType.INT:
        s = st.integers(min_value=f.min, max_value=f.max)
    elif t is RatingInputType.DECIMAL:
        s = st.decimals(min_value=f.min, max_value=f.max, places=2,
                        allow_nan=False, allow_infinity=False)
    elif t is RatingInputType.ENUM:
        s = st.sampled_from(f.domain)
    elif t is RatingInputType.STRING:
        s = st.from_regex(f.pattern, fullmatch=True)
    elif t is RatingInputType.DATE:
        s = st.dates(min_value=D0, max_value=D1)
    else:
        s = st.booleans()
    return st.none() | s if f.nullable else s


CONTEXTS = st.fixed_dictionaries({f.name: field_strategy(f) for f in CONTRACT})


def run_hypothesis(arm: str, s: int, log: list) -> None:
    base = dict(max_examples=200, database=None, deadline=None,
                derandomize=False, report_multiple_bugs=False,
                suppress_health_check=[])
    if arm == "hyp_seed":                 # @seed(s), everything else pinned off
        kw, use_seed = base, True
    elif arm == "hyp_derand":             # derandomize=True, no @seed
        kw, use_seed = {**base, "derandomize": True}, False
    elif arm == "hyp_derand_seed":        # derandomize=True AND @seed(s): which wins?
        kw, use_seed = {**base, "derandomize": True}, True
    elif arm == "hyp_defaults":           # @seed(s) with hypothesis defaults
        kw, use_seed = dict(max_examples=200), True
    elif arm == "hyp_db_shared":          # @seed(s) + a DB dir shared across processes
        db = os.environ["F4_DB_DIR"]
        kw, use_seed = {**base, "database": DirectoryBasedExampleDatabase(db)}, True
    elif arm == "hyp_random":             # NEGATIVE CONTROL: no @seed, no derandomize
        kw, use_seed = base, False
    elif arm == "hyp_pass":               # a passing property: generation only, no shrink
        kw, use_seed = base, True
    else:
        raise SystemExit(arm)

    fails = arm != "hyp_pass"

    @settings(**kw)
    @given(CONTEXTS)
    def prop(ctx):
        log.append(canon(ctx))
        if fails:
            assert premium(ctx) <= LIMIT

    if use_seed:
        prop = seed(s)(prop)
    try:
        prop()
        log.append({"RESULT": "passed"})
    except AssertionError:
        log.append({"RESULT": "counterexample", "ctx": log[-1]})


# ---- (b) own seeded numpy generator ----------------------------------------
_PC_ALPHA = [chr(c) for c in range(65, 91)]


def np_field(f: InputContractField, rng: np.random.Generator):
    t = f.type
    if f.nullable and rng.random() < 0.1:
        return None
    if t is RatingInputType.INT:
        return int(rng.integers(int(f.min), int(f.max) + 1))
    if t is RatingInputType.DECIMAL:
        lo, hi = int(Decimal(f.min) * 100), int(Decimal(f.max) * 100)
        return Decimal(int(rng.integers(lo, hi + 1))) / 100
    if t is RatingInputType.ENUM:
        return f.domain[int(rng.integers(len(f.domain)))]
    if t is RatingInputType.STRING:  # generator for this one pattern only (spike)
        a = "".join(_PC_ALPHA[i] for i in rng.integers(26, size=int(rng.integers(1, 3))))
        n = str(int(rng.integers(0, 100 if rng.random() < .5 else 10)))
        return f"{a}{n} {int(rng.integers(10))}" + "".join(_PC_ALPHA[i] for i in rng.integers(26, size=2))
    if t is RatingInputType.DATE:
        return D0 + dt.timedelta(days=int(rng.integers((D1 - D0).days + 1)))
    return bool(rng.integers(2))


def np_simplest(f: InputContractField):
    t = f.type
    return {RatingInputType.INT: None if f.nullable else f.min,
            RatingInputType.DECIMAL: f.min, RatingInputType.ENUM: f.domain[0] if f.domain else None,
            RatingInputType.DATE: D0, RatingInputType.BOOL: False,
            RatingInputType.STRING: "A0 0AA"}[t]


def run_numpy(s: int, log: list) -> None:
    rng = np.random.default_rng(s)
    fail = None
    for _ in range(200):
        ctx = {f.name: np_field(f, rng) for f in CONTRACT}
        log.append(canon(ctx))
        if premium(ctx) > LIMIT:
            fail = ctx
            break
    if fail is None:
        log.append({"RESULT": "passed"})
        return
    # deterministic greedy shrink: per field in contract order, try the simplest value
    changed = True
    while changed:
        changed = False
        for f in CONTRACT:
            cand = {**fail, f.name: np_simplest(f)}
            if cand != fail and premium(cand) > LIMIT:
                fail, changed = cand, True
                log.append(canon(fail))
    log.append({"RESULT": "counterexample", "ctx": canon(fail)})


if __name__ == "__main__":
    arm, s, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    log: list = []
    if arm == "numpy":
        run_numpy(s, log)
    else:
        run_hypothesis(arm, s, log)
    with open(out, "w") as fh:
        json.dump(log, fh, sort_keys=True, separators=(",", ":"))
