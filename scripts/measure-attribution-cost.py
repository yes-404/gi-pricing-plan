#!/usr/bin/env python3
"""WK-673 Slice 3, Task 7: the attribution cost and replay harness on the freMTPL2 fixture.

    uv run python scripts/measure-attribution-cost.py fit
    uv run python scripts/measure-attribution-cost.py cost --policies 20000
    uv run python scripts/measure-attribution-cost.py sets --policies 20000
    uv run python scripts/measure-attribution-cost.py replay --policies 2000

`fit` writes `examples/fremtpl2/rating/` from two real `glum` Poisson fits (RL-1445 /
dispatch record, Ruling 1 (b'), condition (i)): the frequency model is per-factor relativity
tables, exp(beta), no `model_call`. Every other command reads those files and prints one JSON
line per run. The measurement is run alone in a held gate slot, never inside a gate.

The fixture is **measurement only**. The module-level helpers (`load_fixture`, `candidate_for`,
`replay_subset`, ...) are imported by `test_fremtpl2_rate_fixture.py` and
`test_rating_attribution.py` through `importlib` (the file name has a hyphen).
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import itertools
import json
import os
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "examples" / "fremtpl2" / "rating"
DATA = ROOT / "examples" / "fremtpl2" / "data" / "freMTPL2freq.arff"

#: Decimal places of every relativity table value and of the base frequency (ledgered).
TABLE_DP = 8
BASE_DP = 12

SEVERITY_V1, SEVERITY_V2 = 190_000, 197_600  # minor units; +4 %
LOAD_V1, LOAD_V2 = "1.25", "1.28"
FLOOR_V1, FLOOR_V2 = 15_000, 18_000
#: The transitional cap: min(premium, current premium * CAP). The baseline has the step with a
#: factor too large to bind (x1000): the engine allows one clamp per rung, so the cap is an
#: expression ahead of the minimum-premium clamp and a member edits its factor.
CAP_V1, CAP_V2 = "1000", "1.25"

#: Frequency factors: (input name, table slug stem, value column, in freq_v2 only).
#: freq_v1 is RS-1201's `prep` feature list (spike/run.py at 46ecb632): Area, power_band,
#: age_band, VehBrand, Region as categoricals; bm and log(Density) as numerics.
FACTORS_V1 = ("area", "veh_power", "age_band", "veh_brand", "region", "bonus_malus", "density")
FACTORS_V2_ONLY = ("veh_gas", "veh_age_band")
INT_FACTORS = {"veh_power", "bonus_malus", "density", "veh_age_band"}

#: The six catalogue members (RS-1201 `CORE`), by index, and the six F3 change sets.
MEMBERS = (
    "model: freq_v1 -> freq_v2 (adds VehGas, VehAge)",
    "rate_table: age relativity v1 -> v2",
    "severity 1900 -> 1976 (+4%)",
    "expense_load 0.25 -> 0.28",
    "min_premium 150 -> 180",
    "cap: increase capped at +25% of baseline",
)
SETS = ((0, 1, 2), (0, 1, 2, 3), (0, 1, 2, 3, 4), (0, 1, 2, 3, 4, 5), (0, 1, 4, 5), (1, 2, 4))
AGE_REL_V2 = {
    "18-20": "1.35", "21-25": "1.18", "26-30": "1.05", "31-40": "1.0",
    "41-50": "0.97", "51-60": "0.95", "61-70": "0.98", "71+": "1.10",
}  # fmt: skip
AGE_BANDS = tuple(AGE_REL_V2)


# ---------------------------------------------------------------------------
# Data and the fit.
# ---------------------------------------------------------------------------


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_portfolio(limit: int | None = None) -> Any:
    """The freMTPL2 frequency file as a frame with the fixture's input names, by `quote_id`."""
    import polars as pl

    sys.path.insert(0, str(ROOT / "examples" / "fremtpl2"))
    from arff import to_csv  # type: ignore[import-not-found]

    df = pl.read_csv(to_csv(DATA), infer_schema_length=None)
    age = pl.col("DrivAge")
    df = df.with_columns(
        pl.format("P{}", pl.col("IDpol").cast(pl.Int64).cast(pl.String).str.zfill(9)).alias(
            "quote_id"
        ),
        pl.col("Exposure").clip(upper_bound=1.0).alias("exposure_years"),
        pl.col("Area").alias("area"),
        pl.col("VehPower").clip(upper_bound=12).cast(pl.Int64).alias("veh_power"),
        pl.col("VehBrand").alias("veh_brand"),
        pl.col("Region").alias("region"),
        pl.col("BonusMalus").clip(upper_bound=150).cast(pl.Int64).alias("bonus_malus"),
        pl.col("Density").cast(pl.Int64).alias("density"),
        pl.col("VehGas").alias("veh_gas"),
        (pl.col("VehAge").clip(upper_bound=15).floordiv(3)).cast(pl.Int64).alias("veh_age_band"),
        pl.when(age < 21).then(pl.lit("18-20"))
        .when(age < 26).then(pl.lit("21-25"))
        .when(age < 31).then(pl.lit("26-30"))
        .when(age < 41).then(pl.lit("31-40"))
        .when(age < 51).then(pl.lit("41-50"))
        .when(age < 61).then(pl.lit("51-60"))
        .when(age < 71).then(pl.lit("61-70"))
        .otherwise(pl.lit("71+")).alias("age_band"),
    )  # fmt: skip
    df = df.sort("quote_id")
    return df.head(limit) if limit else df


def _fit(df: Any, factors: tuple[str, ...]) -> dict[str, Any]:
    """Poisson, log link, y = ClaimNb / Exposure weighted by Exposure (a log-exposure offset)."""
    import numpy as np
    import polars as pl
    from glum import GeneralizedLinearRegressor

    columns: list[Any] = []
    names: list[tuple[str, str]] = []  # (factor, level) per design column; ("bonus_malus","")
    for f in factors:
        if f == "bonus_malus":
            columns.append(df["bonus_malus"].cast(pl.Float64).to_numpy())
            names.append((f, ""))
        elif f == "density":
            columns.append(np.log(df["density"].cast(pl.Float64).to_numpy()))
            names.append((f, ""))
        else:
            levels = sorted(df[f].unique().to_list())
            for lvl in levels[1:]:  # first sorted level is the reference
                columns.append((df[f] == lvl).cast(pl.Float64).to_numpy())
                names.append((f, str(lvl)))
    x = np.column_stack(columns)
    y = (df["ClaimNb"] / df["exposure_years"]).to_numpy()
    model = GeneralizedLinearRegressor(family="poisson", alpha=0, fit_intercept=True)
    model.fit(x, y, sample_weight=df["exposure_years"].to_numpy())
    return {
        "intercept": float(model.intercept_),
        "coef": [
            {"factor": f, "level": lvl, "beta": float(b)}
            for (f, lvl), b in zip(names, model.coef_, strict=True)
        ],
    }


def _q(value: float, dp: int) -> str:
    return str(Decimal(repr(value)).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_EVEN))


def _tables(df: Any, fit: dict[str, Any], factors: tuple[str, ...]) -> dict[str, list[dict]]:
    """Per factor, the exact relativity of every level in the data: exp(beta) (categorical),
    exp(beta * x) (bonus_malus: every integer 50..150), exp(beta * log d) (density: every
    distinct integer d in the file, the key domain)."""
    import math

    beta = {(c["factor"], c["level"]): c["beta"] for c in fit["coef"]}
    out: dict[str, list[dict]] = {}
    for f in factors:
        col = f"rel_{f}"
        if f == "bonus_malus":
            keys = list(range(50, 151))
            vals = [math.exp(beta[(f, "")] * k) for k in keys]
        elif f == "density":
            keys = sorted(df["density"].unique().to_list())
            vals = [math.exp(beta[(f, "")] * math.log(k)) for k in keys]
        else:
            keys = sorted(df[f].unique().to_list())
            vals = [1.0 if i == 0 else math.exp(beta[(f, str(k))]) for i, k in enumerate(keys)]
        out[f] = [
            {f: k if f in INT_FACTORS else str(k), col: _q(v, TABLE_DP)}
            for k, v in zip(keys, vals, strict=True)
        ]
    return out


def _table_payload(slug: str, version: int, factor: str, rows: list[dict]) -> dict[str, Any]:
    key_type = "int" if factor in INT_FACTORS else "string"
    return {
        "slug": slug, "version": version, "rateable": True, "storage": "rows",
        "keys": [{"name": factor, "type": key_type, "banding_ref": None}],
        "value": {"name": f"rel_{factor}", "type": "relativity", "unit": "factor",
                  "min": None, "max": None},
        "default_row": None,
        "rows": [{k: str(v) for k, v in r.items()} for r in rows],
    }  # fmt: skip


def _slug(factor: str) -> str:
    return "fremtpl2-rel-" + factor.replace("_", "-")


def _input_field(name: str, tables: dict[str, list[dict]]) -> dict[str, Any]:
    domain = [r[name] for r in tables[name]] if name in tables else None
    if name in INT_FACTORS:
        keys = [r[name] for r in tables[name]]
        return {"name": name, "type": "int", "nullable": False, "min": min(keys), "max": max(keys)}
    return {"name": name, "type": "enum", "domain": domain, "nullable": False}


def _algorithm(
    v1_tables: dict[str, list[dict]],
    v2_tables: dict[str, list[dict]],
    base_v1: str,
    base_v2: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """The baseline algorithm and the full candidate (every member applied)."""

    def inputs(factors: list[str], tabs: dict[str, list[dict]]) -> list[dict[str, Any]]:
        return [_input_field(f, tabs) for f in factors]

    def in_step(f: str) -> dict[str, Any]:
        return {"step_id": f"s_in_{f}", "type": "input", "label": f, "input_name": f,
                "on_missing": "error", "produces": f}  # fmt: skip

    def table_step(f: str, version: int, step_id: str | None = None) -> dict[str, Any]:
        return {"step_id": step_id or f"s_t_{f}", "type": "table", "label": f"{f} relativity",
                "rate_table_ref": f"rate_table:{_slug(f)}@{version}", "key_expr": [f],
                "on_miss": "error", "consumes": [f], "produces": f"rel_{f}"}  # fmt: skip

    def freq_step(factors: list[str], base: str) -> dict[str, Any]:
        expr = " * ".join([base, *[f"rel_{f}" for f in factors]])
        return {"step_id": "s_freq", "type": "expression", "label": "Claim frequency",
                "expr": expr, "result_type": "decimal", "consumes": [f"rel_{f}" for f in factors],
                "produces": "freq"}  # fmt: skip

    def out_step(step_id: str, rung: str, source: str) -> dict[str, Any]:
        return {"step_id": step_id, "type": "output", "label": rung, "output_name": rung,
                "rounding": {"mode": "half_even", "dp": 0}, "consumes": [source]}  # fmt: skip

    age_in = {"name": "age_band", "type": "enum", "domain": list(AGE_BANDS), "nullable": False}

    def alg(
        version: int, freq_factors: list[str], tabs: dict[str, list[dict]], base: str,
        sev: int, load: str, floor: int, age_v: int, cap: str, freq_version: int,
    ) -> dict[str, Any]:  # fmt: skip
        steps: list[dict[str, Any]] = [in_step(f) for f in freq_factors]
        steps = [s for s in steps if s["input_name"] != "age_band"]
        steps += [in_step("age_band"), in_step("current_premium_minor")]
        steps += [table_step(f, freq_version) for f in freq_factors]
        steps += [
            freq_step(freq_factors, base),
            {"step_id": "s_risk", "type": "expression", "label": "Risk premium",
             "expr": f"freq * {sev}", "result_type": "money_minor",
             "consumes": ["freq"], "produces": "risk_minor"},
            out_step("s_out_risk", "risk_premium_minor", "risk_minor"),
            {"step_id": "s_load", "type": "expression", "label": "Expense loading",
             "expr": f"risk_minor * {load}", "result_type": "money_minor",
             "consumes": ["risk_minor"], "produces": "pre_cap_minor"},
            {"step_id": "s_cap", "type": "expression", "label": "Transitional cap",
             "expr": f"min([pre_cap_minor, current_premium_minor * {cap}])",
             "result_type": "money_minor",
             "consumes": ["pre_cap_minor", "current_premium_minor"], "produces": "loaded_minor"},
            out_step("s_out_load", "expense_loading_minor", "loaded_minor"),
            {"step_id": "s_age", "type": "table", "label": "Age relativity",
             "rate_table_ref": f"rate_table:fremtpl2-age-relativity@{age_v}",
             "key_expr": ["age_band"], "on_miss": "error", "consumes": ["age_band"],
             "produces": "rel_age_adj"},
            {"step_id": "s_adj", "type": "expression", "label": "Age adjustment",
             "expr": "loaded_minor * rel_age_adj", "result_type": "money_minor",
             "consumes": ["loaded_minor", "rel_age_adj"], "produces": "adjusted_minor"},
            out_step("s_out_adj", "profit_loading_minor", "adjusted_minor"),
            {"step_id": "s_floor", "type": "constraint", "label": "Minimum premium",
             "condition": f"adjusted_minor >= {floor}", "on_violation": "clamp",
             "clamp_bounds": {"min": str(floor)}, "reason_code": "MIN_PREMIUM_APPLIED",
             "consumes": ["adjusted_minor"], "produces": ["adjusted_minor"]},
        ]  # fmt: skip
        steps += [
            {"step_id": "s_pay", "type": "expression", "label": "Payable premium",
             "expr": "adjusted_minor", "result_type": "money_minor", "consumes": ["adjusted_minor"],
             "produces": "payable_minor"},
            out_step("s_out_payable", "payable_premium_minor", "payable_minor"),
        ]  # fmt: skip
        contract = [c for c in inputs(freq_factors, tabs) if c["name"] != "age_band"]
        contract += [
            age_in,
            {"name": "current_premium_minor", "type": "int", "nullable": False, "min": 0},
        ]
        return {
            "slug": "fremtpl2-rate", "version": version, "input_contract": contract,
            "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
            "steps": steps, "sub_graphs": [],
        }  # fmt: skip

    f_v1 = list(FACTORS_V1)
    f_v2 = [*FACTORS_V1, *FACTORS_V2_ONLY]
    base = alg(1, f_v1, v1_tables, base_v1, SEVERITY_V1, LOAD_V1, FLOOR_V1, 1, CAP_V1, 1)
    full = alg(2, f_v2, v2_tables, base_v2, SEVERITY_V2, LOAD_V2, FLOOR_V2, 2, CAP_V2, 2)
    # The two new factors have version-1 tables: `fremtpl2-rel-veh-gas@1`... are not v2 refits
    # of an existing table, so their steps point at version 1 (they are `step_added`, not
    # `table_repointed`).
    for s in full["steps"]:
        if s["step_id"] in ("s_t_veh_gas", "s_t_veh_age_band"):
            s["rate_table_ref"] = s["rate_table_ref"].rsplit("@", 1)[0] + "@1"
    return base, full


def cmd_fit(_args: argparse.Namespace) -> None:
    """Fit freq_v1 and freq_v2 and write the fixture. Prints one JSON line (the fit record)."""
    import glum
    import polars as pl

    df = load_portfolio()
    f_v1, f_v2 = FACTORS_V1, (*FACTORS_V1, *FACTORS_V2_ONLY)
    fit1, fit2 = _fit(df, f_v1), _fit(df, f_v2)
    t1, t2 = _tables(df, fit1, f_v1), _tables(df, fit2, f_v2)
    base1, base2 = (_q(__import__("math").exp(f["intercept"]), BASE_DP) for f in (fit1, fit2))
    FIXTURE.mkdir(parents=True, exist_ok=True)

    def put(name: str, payload: Any) -> None:
        (FIXTURE / name).write_text(json.dumps(payload, indent=1, sort_keys=False) + "\n")

    for f in f_v1:
        put(f"fremtpl2-rel-{f.replace('_', '-')}.rate-table.v1.json",
            _table_payload(_slug(f), 1, f, t1[f]))  # fmt: skip
        put(f"fremtpl2-rel-{f.replace('_', '-')}.rate-table.v2.json",
            _table_payload(_slug(f), 2, f, t2[f]))  # fmt: skip
    for f in FACTORS_V2_ONLY:
        put(f"fremtpl2-rel-{f.replace('_', '-')}.rate-table.v1.json",
            _table_payload(_slug(f), 1, f, t2[f]))  # fmt: skip
    age_rows_v1 = [{"age_band": b, "rel_age_adj": "1.0"} for b in AGE_BANDS]
    age_rows_v2 = [{"age_band": b, "rel_age_adj": v} for b, v in AGE_REL_V2.items()]
    for v, rows in ((1, age_rows_v1), (2, age_rows_v2)):
        payload = _table_payload("fremtpl2-age-relativity", v, "age_band", rows)
        payload["value"]["name"] = "rel_age_adj"
        put(f"fremtpl2-age-relativity.rate-table.v{v}.json", payload)
    base_alg, full_alg = _algorithm(t1, t2, base1, base2)
    put("fremtpl2-rate.rating-algorithm.v1.json", base_alg)
    put("fremtpl2-rate.rating-algorithm.v2.json", full_alg)
    put("fremtpl2-rate.changes.json", _changes())
    record = {
        "command": "uv run python scripts/measure-attribution-cost.py fit",
        "data": {"file": DATA.name, "sha256": _sha256(DATA), "rows": df.height,
                 "claims": int(df["ClaimNb"].sum())},
        "glum": glum.__version__, "polars": pl.__version__,
        "table_dp": TABLE_DP, "base_dp": BASE_DP,
        "freq_v1": {"base_frequency": base1, **fit1}, "freq_v2": {"base_frequency": base2, **fit2},
        "density_distinct_keys": len(t1["density"]),
    }  # fmt: skip
    put("fremtpl2-fit-record.json", record)
    print(json.dumps({k: record[k] for k in ("data", "glum", "polars", "density_distinct_keys")}
                     | {"base_v1": base1, "base_v2": base2}))  # fmt: skip


def _changes() -> dict[str, Any]:
    """The catalogue: per member, the step ids it takes from the full candidate."""
    freq_ids = [f"s_t_{f}" for f in FACTORS_V1]
    return {
        "members": [
            {"name": MEMBERS[0],
             "steps": [*freq_ids, "s_freq", "s_in_veh_gas", "s_in_veh_age_band", "s_t_veh_gas",
                       "s_t_veh_age_band"]},
            {"name": MEMBERS[1], "steps": ["s_age"]},
            {"name": MEMBERS[2], "steps": ["s_risk"]},
            {"name": MEMBERS[3], "steps": ["s_load"]},
            {"name": MEMBERS[4], "steps": ["s_floor"]},
            {"name": MEMBERS[5],
             "steps": ["s_cap"]},
        ],
        "sets": [list(s) for s in SETS],
    }  # fmt: skip


# ---------------------------------------------------------------------------
# The fixture, the candidates and the resolver.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Fixture:
    baseline: dict[str, Any]
    full: dict[str, Any]
    tables: dict[str, dict[str, Any]]  # "rate_table:<slug>@<v>" -> payload
    members: list[dict[str, Any]]
    sets: list[list[int]]


def load_fixture() -> Fixture:
    def read(name: str) -> Any:
        return json.loads((FIXTURE / name).read_text())

    tables = {}
    for path in sorted(FIXTURE.glob("*.rate-table.v*.json")):
        p = json.loads(path.read_text())
        tables[f"rate_table:{p['slug']}@{p['version']}"] = p
    changes = read("fremtpl2-rate.changes.json")
    return Fixture(
        read("fremtpl2-rate.rating-algorithm.v1.json"),
        read("fremtpl2-rate.rating-algorithm.v2.json"),
        tables, changes["members"], changes["sets"],
    )  # fmt: skip


def candidate_for(fx: Fixture, members: tuple[int, ...] | list[int]) -> dict[str, Any]:
    """The baseline with each chosen member's steps taken from the full candidate (a changed
    step replaces, a new step is appended), and the contract fields those steps read."""
    alg = copy.deepcopy(fx.baseline)
    alg["version"] = 2
    have = {s["step_id"]: i for i, s in enumerate(alg["steps"])}
    full = {s["step_id"]: s for s in fx.full["steps"]}
    fields = {c["name"]: c for c in alg["input_contract"]}
    full_fields = {c["name"]: c for c in fx.full["input_contract"]}
    for m in members:
        for sid in fx.members[m]["steps"]:
            step = copy.deepcopy(full[sid])
            if sid in have:
                alg["steps"][have[sid]] = step
            else:
                have[sid] = len(alg["steps"])
                alg["steps"].append(step)
            if step["type"] == "input":
                fields[step["input_name"]] = copy.deepcopy(full_fields[step["input_name"]])
    # Re-bound contract fields the repointed tables moved (a refit moves every key domain).
    alg["input_contract"] = [fields[n] for n in [*fields]]
    return alg


def table_refs(alg: dict[str, Any]) -> list[str]:
    return sorted({s["rate_table_ref"] for s in alg["steps"] if s["type"] == "table"})


class FixtureResolver:
    """Serves the algorithms and rate tables of a fixture; the algorithm payloads are set by the
    caller (`serve`)."""

    def __init__(self, fx: Fixture) -> None:
        self.payloads: dict[str, dict[str, Any]] = dict(fx.tables)

    def serve(self, ref: str, payload: dict[str, Any]) -> None:
        self.payloads[ref] = payload

    async def resolve(self, ref: Any) -> Any:
        from pricing_core.rating.compile import ResolvedArtifact

        return ResolvedArtifact(status="approved", payload=self.payloads[str(ref)])


def rating_version(alg_ref: str, tables: list[str], version: int) -> Any:
    from uuid import uuid4

    from model_schema.rating import RatingVersion

    return RatingVersion.model_validate(
        {
            "id": str(uuid4()), "workspace_id": str(uuid4()), "slug": "fremtpl2-rate",
            "version": version, "status": "draft", "dataset_version_id": str(uuid4()),
            "model_ref": "model:fremtpl2-unused@1",
            "created_at": "2026-10-08T12:00:00Z", "created_by": str(uuid4()),
            "updated_at": "2026-10-08T12:00:00Z", "algorithm_ref": alg_ref,
            "pins": {"rate_tables": tables, "models": [], "reference_tables": [],
                     "custom_objectives": []},
            "model_reference_mode": "exact",
        }
    )  # fmt: skip


def versions_for(fx: Fixture, members: tuple[int, ...] | list[int]) -> tuple[Any, Any, Any]:
    """(baseline RatingVersion, candidate RatingVersion, resolver) for a member set."""
    cand = candidate_for(fx, members)
    resolver = FixtureResolver(fx)
    resolver.serve("rating_algorithm:fremtpl2-rate@1", fx.baseline)
    resolver.serve("rating_algorithm:fremtpl2-rate@2", cand)
    base_v = rating_version("rating_algorithm:fremtpl2-rate@1", table_refs(fx.baseline), 1)
    cand_v = rating_version("rating_algorithm:fremtpl2-rate@2", table_refs(cand), 2)
    return base_v, cand_v, resolver


def portfolio_for(fx: Fixture, policies: int | None) -> Any:
    """The portfolio frame (lazy) with the fixture's inputs, and `current_premium_minor` set to
    the baseline's own payable premium (the cap is relative to it)."""
    import polars as pl

    from pricing_core.rating.analysis import dislocation_frame
    from pricing_core.rating.compile import compile_bundle
    from pricing_core.rating.runtime import load_bundle

    df = load_portfolio(policies)
    cols = ["quote_id", "exposure_years", *FACTORS_V1, *FACTORS_V2_ONLY]
    book = df.select(cols).lazy()
    base_v, _cand_v, resolver = versions_for(fx, [])
    bundle = load_bundle(asyncio.run(compile_bundle(base_v, resolver)))
    # The first pass needs the column: an inert placeholder (the baseline's cap is x1000 anyway).
    first = book.with_columns(pl.lit(10**9, dtype=pl.Int64).alias("current_premium_minor"))
    frame = dislocation_frame(bundle, bundle, first, _spec(base_v, base_v))
    current = frame.select("quote_id", pl.col("baseline_minor").alias("current_premium_minor"))
    return book.join(current.lazy(), on="quote_id", how="left")


def _spec(base_v: Any, cand_v: Any, groups: Any = None) -> Any:
    from model_schema.dislocation import DislocationSpec

    return DislocationSpec(
        baseline_ref=_art("rating_version:fremtpl2-rate@1"),
        candidate_ref=_art("rating_version:fremtpl2-rate@2"),
        portfolio_dataset_version_id=UUID(int=1), purpose="renewal", as_at=date(2026, 9, 1),
        band_edges_pct=["-5", "5"], mover_threshold_pct="10", change_groups=groups,
    )  # fmt: skip


def _art(text: str) -> Any:
    from model_schema.refs import ArtifactRef

    kind, rest = text.split(":")
    slug, version = rest.split("@")
    return ArtifactRef(type=kind, slug=slug, version=int(version))  # type: ignore[arg-type]


def groups_for(fx: Fixture, members: tuple[int, ...] | list[int], derived: Any) -> Any:
    """One `ChangeGroup` per member: the derived changes whose description starts with one of
    the member's step ids, or (a table or pin change) names a step the member holds. Members
    are named by their catalogue name."""
    from model_schema.dislocation import ChangeGroup

    out = []
    for m in members:
        steps = tuple(fx.members[m]["steps"])
        ids = [d.id for d in derived if any(d.description.startswith(s) for s in steps)]
        out.append(ChangeGroup(name=fx.members[m]["name"], changes=ids))
    return out


# ---------------------------------------------------------------------------
# Replay (DP-S3-3 (b)): measured here, never a production path.
# ---------------------------------------------------------------------------


#: The ladder rung each member's steps feed, by step-id prefix.
_STEP_RUNG = {
    "s_t_": "risk_premium", "s_freq": "risk_premium", "s_risk": "risk_premium",
    "s_in_veh": "risk_premium", "s_load": "expense_loading", "s_cap": "expense_loading",
    "s_age": "profit_loading", "s_floor": "constraints",
}  # fmt: skip


def member_rungs(fx: Fixture, member: int) -> set[str]:
    return {
        next(v for k, v in _STEP_RUNG.items() if sid.startswith(k))
        for sid in fx.members[member]["steps"]
    }


def step_aligned(fx: Fixture, members: tuple[int, ...] | list[int]) -> bool:
    """A set is step-aligned when no two of its members edit steps that feed the same ladder
    rung (so each rung's operation can be taken from baseline or candidate on its own)."""
    seen: set[str] = set()
    for m in members:
        rungs = member_rungs(fx, m)
        if rungs & seen:
            return False
        seen |= rungs
    return True


def replay_values(
    fx: Fixture,
    members: tuple[int, ...] | list[int],
    base: dict[str, dict[str, Any]],
    cand: dict[str, dict[str, Any]],
) -> dict[str, int]:
    """Replay of the candidate made of `members` from the baseline and full-candidate ladders:
    per policy, `replay_subset` with each rung taken from the candidate when a member owns it."""
    owned = set().union(*(member_rungs(fx, m) for m in members)) if members else set()
    out: dict[str, int] = {}
    for quote_id, b in base.items():
        c = cand[quote_id]
        if b["minor"] is None or c["minor"] is None:
            continue
        takes = {r.rung: r.rung in owned for r in b["ladder"]}
        out[quote_id] = replay_subset(b["ladder"], c["ladder"], takes)
    return out


def compare_replay(replayed: dict[str, int], rerated: dict[str, int]) -> list[tuple[str, int]]:
    """Every policy whose replayed premium differs from the true re-rate, as `(quote_id,
    replayed - rerated)` in minor units, sorted by quote_id."""
    return sorted((q, v - rerated[q]) for q, v in replayed.items() if v != rerated[q])


def replay_subset(
    base_ladder: list[Any], cand_ladder: list[Any], takes_cand: dict[str, bool]
) -> int:
    """v(S) by replay: the first rung's unrounded value from the side that owns it, then every
    later rung's recorded operation from the side `takes_cand` names, applied in exact decimal;
    the payable rung rounds once (half-even)."""
    base = {r.rung: r for r in base_ladder}
    cand = {r.rung: r for r in cand_ladder}
    names = [r.rung for r in base_ladder]
    value = Decimal(
        (cand if takes_cand[names[0]] else base)[names[0]].unrounded_minor  # type: ignore[arg-type]
    )
    for name in names[1:]:
        rung = (cand if takes_cand[name] else base)[name]
        op = rung.operation
        if op is None or op.kind == "none":
            continue
        if op.kind == "multiply":
            value *= Decimal(op.factor)
        elif op.kind == "divide":
            value /= Decimal(op.divisor)
        elif op.kind == "add":
            value += Decimal(op.amount_unrounded_minor)
        elif op.kind == "clamp":
            bound = Decimal(op.bound_unrounded_minor)
            value = max(value, bound) if op.bound == "min" else min(value, bound)
        else:  # round: the payable rung's own rounding
            pass
    return int(value.quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


# ---------------------------------------------------------------------------
# Measurement commands.
# ---------------------------------------------------------------------------


def _env() -> dict[str, Any]:
    tree = subprocess.run(
        ["/usr/bin/git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    return {"load1": round(os.getloadavg()[0], 2), "tree": tree,
            "stamp": datetime.now(UTC).isoformat(timespec="seconds")}  # fmt: skip


def _emit(**fields: Any) -> None:
    print(json.dumps({**fields, **_env()}), flush=True)


def _attribute(fx: Fixture, members: list[int], book: Any) -> Any:
    from pricing_core.rating.analysis import attribute, derive_changes

    base_v, cand_v, resolver = versions_for(fx, members)
    derived = asyncio.run(derive_changes(base_v, cand_v, resolver))
    spec = _spec(base_v, cand_v, groups_for(fx, members, derived))
    return asyncio.run(attribute(base_v, cand_v, book, spec, resolver))


def cmd_cost(args: argparse.Namespace) -> None:
    """score_batch N medians and the 2^K re-rates (K = 3..6) on the first `--policies` policies
    by quote_id, N runs each. Full-portfolio figures are DERIVED and labelled so."""
    from pricing_core.rating.compile import compile_bundle
    from pricing_core.rating.runtime import load_bundle
    from pricing_core.rating.score import score_batch

    fx = load_fixture()
    book = portfolio_for(fx, args.policies).collect().lazy()
    n = book.select(pl_len()).collect().item()
    base_v, _c, resolver = versions_for(fx, [])
    bundle = load_bundle(asyncio.run(compile_bundle(base_v, resolver)))
    inputs = [f["name"] for f in bundle.algorithm.input_contract]
    frame = book.select(["quote_id", *inputs]).with_columns(_stamp_columns())
    secs = []
    for _ in range(args.runs):
        t = time.perf_counter()
        score_batch(bundle, frame).collect()
        secs.append(time.perf_counter() - t)
    rate = n / statistics.median(secs)
    _emit(what="score_batch", k=0, policies=n, seconds=statistics.median(secs), runs=secs)
    for k, members in (
        (3, [0, 1, 2]),
        (4, [0, 1, 2, 3]),
        (5, [0, 1, 2, 3, 4]),
        (6, [0, 1, 2, 3, 4, 5]),
    ):
        runs = []
        for _ in range(args.runs):
            t = time.perf_counter()
            _attribute(fx, members, book)
            runs.append(time.perf_counter() - t)
        _emit(what="attribute", k=k, policies=n, seconds=statistics.median(runs), runs=runs)
        _emit(what="derived", k=k, formula="2^K * 678013 / rate",
              inputs={"K": k, "policies": 678013, "score_batch_policies_per_s": rate},
              seconds=(2**k) * 678013 / rate)  # fmt: skip


def pl_len() -> Any:
    import polars as pl

    return pl.len()


def _stamp_columns() -> list[Any]:
    import polars as pl

    return [
        pl.lit("renewal").alias("purpose"),
        pl.lit("2026-09-01").alias("effective_date"),
        pl.lit("rating_version:fremtpl2-rate@1").alias("rating_version_ref"),
    ]


def cmd_sets(args: argparse.Namespace) -> None:
    """The six F3 change sets on ZEN: S and R per set, beside RS-1201's table."""
    fx = load_fixture()
    book = portfolio_for(fx, args.policies).collect().lazy()
    for members in fx.sets:
        t = time.perf_counter()
        result = _attribute(fx, members, book)
        s = result.attribution_summary
        total = s.total_change_minor
        _emit(what="set", set=members, k=len(members), policies=args.policies,
              seconds=time.perf_counter() - t, total_change_minor=total,
              residual_minor=s.residual_minor, method=s.method,
              aligned=step_aligned(fx, members),
              shapley=[i.shapley_minor for i in result.attribution],
              isolated=[i.isolated_minor for i in result.attribution])  # fmt: skip


def _pass(fx: Fixture, members: tuple[int, ...] | list[int], book: Any, columns: list[str]) -> Any:
    """(baseline pass, candidate pass) of `_score_pass` for the baseline against `members`."""
    from pricing_core.rating.analysis import _score_pass
    from pricing_core.rating.compile import compile_bundle
    from pricing_core.rating.runtime import load_bundle

    base_v, cand_v, resolver = versions_for(fx, members)
    spec = _spec(base_v, cand_v)
    b = load_bundle(asyncio.run(compile_bundle(base_v, resolver)))
    c = load_bundle(asyncio.run(compile_bundle(cand_v, resolver)))
    return (
        _score_pass(b, book, columns, spec, spec.baseline_ref),
        _score_pass(c, book, columns, spec, spec.candidate_ref),
    )


def cmd_replay(args: argparse.Namespace) -> None:
    """Replay against true re-rates for the step-aligned sets: per set, the policies where a
    replayed subset premium differs from its true re-rate (count, largest minor-unit gap) and
    the wall times of both. A set that is not step-aligned is reported as such, not replayed."""
    fx = load_fixture()
    book = portfolio_for(fx, args.policies).collect().lazy()
    columns = book.collect_schema().names()
    for members in fx.sets:
        if not step_aligned(fx, members):
            _emit(what="replay", set=members, aligned=False)
            continue
        base, cand = _pass(fx, members, book, columns)
        t = time.perf_counter()
        replayed = {
            sub: replay_values(fx, sub, base, cand)
            for r in range(len(members) + 1)
            for sub in itertools.combinations(members, r)
        }
        replay_secs = time.perf_counter() - t
        t = time.perf_counter()
        mismatches = 0
        worst = 0
        for sub, values in replayed.items():
            _b, rerated = _pass(fx, sub, book, columns)
            truth = {q: v["minor"] for q, v in rerated.items() if v["minor"] is not None}
            diffs = compare_replay(values, truth)
            mismatches += len(diffs)
            worst = max([worst, *(abs(d) for _q, d in diffs)])
        _emit(
            what="replay", set=members, aligned=True, policies=len(base),
            subsets=len(replayed), replay_seconds=replay_secs,
            rerate_seconds=time.perf_counter() - t, mismatching_policy_subsets=mismatches,
            largest_gap_minor=worst,
        )  # fmt: skip


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fit").set_defaults(fn=cmd_fit)
    for name, fn in (("cost", cmd_cost), ("sets", cmd_sets), ("replay", cmd_replay)):
        p = sub.add_parser(name)
        p.add_argument("--policies", type=int, default=20_000)
        p.add_argument("--runs", type=int, default=5)
        p.set_defaults(fn=fn)
    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
