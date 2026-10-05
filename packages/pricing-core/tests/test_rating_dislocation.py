"""The Dislocation Run (03 FR-263, FR-264; §4.8's portfolio frame). WK-673 Slice 2, PL-1403."""

from __future__ import annotations

import asyncio
import copy
import os
import pathlib
import subprocess
import sys
import textwrap
from datetime import date
from decimal import Decimal
from fractions import Fraction
from typing import Any
from uuid import uuid4

import polars as pl
import pytest
from test_rating_score import _algorithm_payload, _FakeResolver, _hand_compiled, _version

from model_schema.dislocation import DislocationSpec
from model_schema.refs import ArtifactRef
from model_schema.scoring import LadderRung
from pricing_core.rating import analysis
from pricing_core.rating.analysis import (
    PortfolioFrameError,
    dislocate,
    dislocation_frame,
    read_portfolio,
    select_movers,
    summarise_dislocation,
)
from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle


def _book(**columns: list[object]) -> pl.LazyFrame:
    base: dict[str, list[object]] = {
        "quote_id": ["Q1", "Q2", "Q3"],
        "exposure_years": [1.0, 0.5, 0.0],
        "driver_age": [34, 22, 70],
    }
    base.update(columns)
    return pl.DataFrame(base, strict=False).lazy()


def _refused(book: pl.LazyFrame, pattern: str, *, segments: tuple[str, ...] = ()) -> str:
    """The refusal is raised AT THE CALL (the frame is never collected here)."""
    with pytest.raises(PortfolioFrameError, match=pattern) as exc:
        read_portfolio(book, segments=segments)
    assert exc.value.code == "VALIDATION_FAILED"
    return str(exc.value)


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_purpose_column_by_name() -> None:
    """RL-1394: a portfolio column named `purpose` is refused, never silently overridden."""
    message = _refused(_book(purpose=["renewal", "renewal", "renewal"]), "purpose")
    assert "renewal" not in message


@pytest.mark.req("FR-263")
@pytest.mark.parametrize("name", ["effective_date", "rating_version_ref"])
def test_read_portfolio_refuses_each_other_stamped_column_by_name(name: str) -> None:
    _refused(_book(**{name: ["x", "x", "x"]}), name)


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_null_exposure_naming_the_column_and_count() -> None:
    """RL-1394 / RL-1361 §E: a null exposure is refused, never read as 0."""
    _refused(_book(exposure_years=[1.0, None, 0.5]), r"exposure_years.*\b1\b")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_nan_exposure() -> None:
    """RL-1402 DP-S2-7: a NaN is not null in Polars and passes `< 0`; refused with the nulls."""
    _refused(_book(exposure_years=[float("nan"), float("inf"), 0.5]), r"exposure_years.*\b2\b")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_negative_exposure() -> None:
    _refused(_book(exposure_years=[1.0, -0.5, -2.0]), r"exposure_years.*\b2\b")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_missing_exposure_column() -> None:
    book = pl.DataFrame({"quote_id": ["Q1"]}).lazy()
    _refused(book, "exposure_years")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_string_exposure_naming_its_dtype() -> None:
    _refused(_book(exposure_years=["1", "2", "3"]), r"exposure_years.*String")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_missing_quote_id_column() -> None:
    book = pl.DataFrame({"exposure_years": [1.0]}).lazy()
    _refused(book, "quote_id")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_null_quote_id() -> None:
    _refused(_book(quote_id=["Q1", None, "Q3"]), r"quote_id.*\b1\b")


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_duplicated_quote_id() -> None:
    message = _refused(_book(quote_id=["Q1", "Q1", "Q3"]), r"quote_id.*\b2\b")
    assert "Q1" not in message


@pytest.mark.req("FR-264")
def test_read_portfolio_refuses_a_float_segment_column_naming_its_dtype() -> None:
    """RL-1402 DP-S2-6: a float level has no stable string."""
    _refused(
        _book(vehicle_value=[1.5, 2.5, 3.5]), r"vehicle_value.*Float64", segments=("vehicle_value",)
    )


@pytest.mark.req("FR-264")
def test_read_portfolio_refuses_an_absent_segment_column() -> None:
    _refused(_book(), "region", segments=("region",))


@pytest.mark.req("FR-264")
def test_read_portfolio_admits_every_stated_segment_dtype() -> None:
    book = _book(
        s=["a", "b", None],
        c=pl.Series(["a", "b", "a"], dtype=pl.Categorical),
        e=pl.Series(["a", "b", "a"], dtype=pl.Enum(["a", "b"])),
        b=[True, False, None],
        d=[date(2026, 1, 1), date(2026, 1, 2), None],
    )
    read_portfolio(book, segments=("driver_age", "s", "c", "e", "b", "d"))


@pytest.mark.req("FR-263")
def test_read_portfolio_reads_a_float_exposure_rounded_to_six_places() -> None:
    """RL-1402 DP-S2-7: `_stored_exposure`'s rule (FR-62), the freMTPL2 dtype (Task 0 Step 5)."""
    out = read_portfolio(_book(exposure_years=[0.1234567, 0.5, 0.0])).collect()
    assert out["exposure_years"].dtype == pl.Decimal(None, 6)
    assert out["exposure_years"].to_list() == [Decimal("0.123457"), Decimal("0.5"), Decimal("0")]


@pytest.mark.req("FR-263")
def test_read_portfolio_reads_an_integer_exposure_exactly() -> None:
    out = read_portfolio(_book(exposure_years=[1, 2, 0])).collect()
    assert out["exposure_years"].to_list() == [Decimal(1), Decimal(2), Decimal(0)]


@pytest.mark.req("FR-263")
def test_read_portfolio_keeps_every_column_unchanged() -> None:
    """RL-1361 §E's frame premise: an undeclared column survives; the reader drops nothing."""
    book = _book(region=["N", "S", "N"])
    out = read_portfolio(book).collect()
    assert out.columns == ["quote_id", "exposure_years", "driver_age", "region"]
    assert out["region"].to_list() == ["N", "S", "N"]
    assert out["quote_id"].to_list() == ["Q1", "Q2", "Q3"]
    assert out["driver_age"].to_list() == [34, 22, 70]


# ---------------------------------------------------------------------------
# Task 4: the two passes and the per-policy frame (RL-1402 DP-S2-1, S2, DP-S2-5).
# ---------------------------------------------------------------------------

_BASE_REF = ArtifactRef(type="rating_version", slug="score-fixture", version=1)
_CAND_REF = ArtifactRef(type="rating_version", slug="score-fixture", version=2)


def _compiled_from(
    algorithm: dict[str, Any], *, expense_direct: str | None = None
) -> CompiledBundle:
    """A `draft` version compiled around `algorithm`, exactly as `_compiled` does (plan N7)."""
    resolver = _FakeResolver()
    resolver._payloads["rating_algorithm:score-fixture@1"] = algorithm
    if expense_direct is not None:
        resolver._payloads["rate_table:motor-expense@1"]["rows"][0]["expense_factor"] = (
            expense_direct
        )
    return load_bundle(asyncio.run(compile_bundle(_version(), resolver)))


def _spec() -> DislocationSpec:
    return DislocationSpec(
        baseline_ref=_BASE_REF,
        candidate_ref=_CAND_REF,
        portfolio_dataset_version_id=uuid4(),
        purpose="renewal",
        as_at=date(2026, 9, 1),
        band_edges_pct=["-5", "5"],
        mover_threshold_pct="10",
    )


def _policies(**columns: list[object]) -> pl.LazyFrame:
    base: dict[str, list[object]] = {
        "quote_id": ["Q1", "Q2", "Q3"],
        "exposure_years": [1.0, 0.5, 1.0],
        "driver_age": [34, 22, 70],
        "channel": ["direct", "broker", "direct"],
        "min_premium_minor": [0, 0, 0],
        "sanity_cap_minor": [999_999_999] * 3,
        "sanity_floor_minor": [0, 0, 0],
    }
    base.update(columns)
    return pl.DataFrame(base, strict=False).lazy()


class _Spy:
    """Records each `score_batch` input frame, then calls the real one."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.frames: list[pl.DataFrame] = []
        real = analysis.score_batch

        def spy(bundle: CompiledBundle, frame: pl.LazyFrame, **kw: Any) -> pl.LazyFrame:
            self.frames.append(frame.collect())
            return real(bundle, frame, **kw)

        monkeypatch.setattr(analysis, "score_batch", spy)


def _with_secret_step() -> dict[str, Any]:
    """The office premium also reads `secret_loading`, a name absent from `input_contract`."""
    alg = copy.deepcopy(_algorithm_payload())
    step = next(x for x in alg["steps"] if x["step_id"] == "s_office")
    step["expr"] = "risk_premium_minor * expense_factor + (secret_loading ?? 0)"
    return alg


@pytest.mark.req("FR-263")
def test_dislocation_undeclared_column_never_reaches_the_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RL-1394: an undeclared portfolio column is never given to the engine."""
    bundle = _hand_compiled(_with_secret_step())
    spy = _Spy(monkeypatch)
    with_col = dislocation_frame(bundle, bundle, _policies(secret_loading=[500, 900, 700]), _spec())
    without = dislocation_frame(bundle, bundle, _policies(), _spec())
    assert set(without["baseline_outcome"]) == {"quoted"}  # `?? 0`: absent reads as no loading
    cols = ["quote_id", "baseline_outcome", "baseline_minor", "baseline_error_code"]
    assert with_col.select(cols).equals(without.select(cols))
    for frame in spy.frames:
        assert "secret_loading" not in frame.columns


@pytest.mark.req("FR-263")
def test_dislocation_undeclared_billing_named_column_refuses_no_row() -> None:
    """P4: `instalment_count` is billing-named; undeclared, it is never read, so no row errors."""
    bundle = _compiled_from(_algorithm_payload())
    out = dislocation_frame(bundle, bundle, _policies(instalment_count=[3, 6, 12]), _spec())
    assert "error" not in out["baseline_outcome"].to_list()
    assert "error" not in out["candidate_outcome"].to_list()


@pytest.mark.req("FR-263")
def test_dislocation_stamps_purpose_date_and_each_passes_own_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _compiled_from(_algorithm_payload())
    spy = _Spy(monkeypatch)
    spec = _spec()
    dislocation_frame(bundle, bundle, _policies(), spec)
    assert len(spy.frames) == 2
    for frame, ref in zip(spy.frames, (spec.baseline_ref, spec.candidate_ref), strict=True):
        assert set(frame["purpose"]) == {spec.purpose}
        assert set(frame["effective_date"]) == {spec.as_at.isoformat()}
        assert set(frame["rating_version_ref"]) == {str(ref)}


@pytest.mark.req("FR-263")
def test_dislocation_each_pass_sees_only_its_own_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base = _compiled_from(_algorithm_payload())
    alg = copy.deepcopy(_algorithm_payload())
    alg["input_contract"].append({"name": "vehicle_group", "type": "int", "nullable": False})
    cand = _compiled_from(alg)
    spy = _Spy(monkeypatch)
    dislocation_frame(base, cand, _policies(vehicle_group=[1, 2, 3]), _spec())
    assert "vehicle_group" not in spy.frames[0].columns
    assert "vehicle_group" in spy.frames[1].columns


@pytest.mark.req("FR-263")
def test_dislocation_missing_declared_input_is_that_rows_error() -> None:
    """03 §4.8: a declared name absent from the portfolio is a row error, not a refusal."""
    bundle = _compiled_from(_algorithm_payload())
    out = dislocation_frame(bundle, bundle, _policies().drop("sanity_floor_minor"), _spec())
    assert set(out["baseline_outcome"]) == {"error"}
    assert set(out["baseline_error_code"]) == {"INPUT_CONTRACT_VIOLATION"}
    assert out["change_minor"].null_count() == 3


@pytest.mark.req("FR-263")
def test_dislocation_frame_refuses_a_colliding_portfolio_column(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _compiled_from(_algorithm_payload())
    spy = _Spy(monkeypatch)
    with pytest.raises(PortfolioFrameError, match="origin_rung") as exc:
        dislocation_frame(bundle, bundle, _policies(origin_rung=["a", "b", "c"]), _spec())
    assert exc.value.code == "VALIDATION_FAILED"
    assert spy.frames == []


@pytest.mark.req("FR-263")
def test_dislocation_frame_is_sorted_by_quote_id_with_change_minor() -> None:
    base = _compiled_from(_algorithm_payload())
    cand = _compiled_from(_algorithm_payload(), expense_direct="1.2")
    book = _policies(quote_id=["Q3", "Q1", "Q2"], region=["N", "S", "N"])
    out = dislocation_frame(base, cand, book, _spec())
    assert out.columns == [
        "quote_id",
        "baseline_outcome",
        "candidate_outcome",
        "baseline_minor",
        "candidate_minor",
        "change_minor",
        "baseline_error_code",
        "candidate_error_code",
        "origin_rung",
        "exposure_years",
        "driver_age",
        "channel",
        "min_premium_minor",
        "sanity_cap_minor",
        "sanity_floor_minor",
        "region",
    ]
    assert out["quote_id"].to_list() == ["Q1", "Q2", "Q3"]
    assert out["region"].to_list() == ["S", "N", "N"]  # the pass-through follows its policy
    assert out.schema["change_minor"] == pl.Int64
    assert out.schema["baseline_minor"] == pl.Int64
    for row in out.iter_rows(named=True):
        assert row["baseline_outcome"] == "quoted" == row["candidate_outcome"]
        assert row["change_minor"] == row["candidate_minor"] - row["baseline_minor"]


@pytest.mark.req("FR-263")
def test_dislocation_frame_change_is_null_unless_both_quoted() -> None:
    base = _compiled_from(_algorithm_payload())
    cand = _compiled_from(_algorithm_payload())
    book = _policies(sanity_cap_minor=[999_999_999, 1, 999_999_999])  # Q2 declines in both
    out = dislocation_frame(base, cand, book, _spec())
    q2 = out.filter(pl.col("quote_id") == "Q2").row(0, named=True)
    assert q2["baseline_outcome"] == "declined"
    assert q2["baseline_minor"] is None
    assert q2["change_minor"] is None
    assert q2["origin_rung"] is None


def _rung(name: str, value: int, unrounded: str) -> LadderRung:
    return LadderRung.model_validate(
        {"rung": name, "value_minor": value, "unrounded_minor": unrounded}
    )


@pytest.mark.req("FR-264")
def test_dislocation_frame_origin_rung_is_the_first_differing_rung() -> None:
    base = _compiled_from(_algorithm_payload())
    # A relativity moves the premium; the first rung it reaches is the origin.
    relativity = _compiled_from(_algorithm_payload(), expense_direct="1.2")
    out = dislocation_frame(base, relativity, _policies(), _spec())
    direct = out.filter(pl.col("channel") == "direct")
    assert set(direct["origin_rung"]) == {"office_premium"}
    broker = out.filter(pl.col("channel") == "broker")
    assert broker["origin_rung"].to_list() == [None]  # nothing changed for broker
    assert broker["change_minor"].to_list() == [0]

    # Rounding only: a rung's value_minor moves, its unrounded_minor does not.
    # office premiums 1435.5, 1631.25, 1864.5: `ceiling` moves Q2 and Q3 only.
    alg = copy.deepcopy(_algorithm_payload())
    step = next(x for x in alg["steps"] if x["step_id"] == "s_out_office")
    step["rounding"] = {"mode": "ceiling", "dp": 0}
    rounding = dislocation_frame(base, _compiled_from(alg), _policies(), _spec())
    assert rounding["origin_rung"].to_list() == [None, "office_premium", "office_premium"]


@pytest.mark.req("FR-264")
def test_origin_rung_compares_unrounded_as_decimals_not_strings() -> None:
    a = [_rung("risk_premium", 100, "100"), _rung("payable_premium", 100, "100")]
    b = [_rung("risk_premium", 100, "100.0"), _rung("payable_premium", 100, "100.0")]
    assert analysis._origin_rung(a, b) is None
    c = [_rung("risk_premium", 100, "100"), _rung("payable_premium", 101, "101")]
    assert analysis._origin_rung(a, c) == "payable_premium"
    d = [_rung("risk_premium", 100, "100")]
    assert analysis._origin_rung(a, d) == "payable_premium"  # present in one ladder only


# ---------------------------------------------------------------------------
# Task 5: the summary (RL-1402 S1, S3, S4, S5; Amendment N2; DP-S2-1..6).
# ---------------------------------------------------------------------------

_FRAME_SCHEMA: dict[str, Any] = {
    "quote_id": pl.String,
    "baseline_outcome": pl.String,
    "candidate_outcome": pl.String,
    "baseline_minor": pl.Int64,
    "candidate_minor": pl.Int64,
    "change_minor": pl.Int64,
    "baseline_error_code": pl.String,
    "candidate_error_code": pl.String,
    "origin_rung": pl.String,
    "exposure_years": pl.Decimal(None, 6),
    "region": pl.String,
}


def _frame(rows: list[dict[str, object]]) -> pl.DataFrame:
    """Rows as `dislocation_frame` gives them; an absent key is null, so a test states only
    what it needs. `change_minor` is derived when both premiums are given."""
    full: list[dict[str, object]] = []
    for row in rows:
        r = dict(row)
        r.setdefault("exposure_years", Decimal(1))
        if "change_minor" not in r and None not in (
            r.get("baseline_minor"),
            r.get("candidate_minor"),
        ):
            r["change_minor"] = r["candidate_minor"] - r["baseline_minor"]  # type: ignore[operator]
        full.append({k: r.get(k) for k in _FRAME_SCHEMA})
    return pl.DataFrame(full, schema=_FRAME_SCHEMA)


def _q(
    quote_id: str,
    baseline: int,
    candidate: int,
    exposure: str = "1",
    region: str | None = None,
    origin: str | None = None,
) -> dict[str, object]:
    return {
        "quote_id": quote_id,
        "baseline_outcome": "quoted",
        "candidate_outcome": "quoted",
        "baseline_minor": baseline,
        "candidate_minor": candidate,
        "exposure_years": Decimal(exposure),
        "region": region,
        "origin_rung": origin,
    }


def _other(
    quote_id: str,
    baseline_outcome: str,
    candidate_outcome: str,
    *,
    baseline_minor: int | None = None,
    candidate_minor: int | None = None,
    baseline_code: str | None = None,
    candidate_code: str | None = None,
    exposure: str = "1",
) -> dict[str, object]:
    return {
        "quote_id": quote_id,
        "baseline_outcome": baseline_outcome,
        "candidate_outcome": candidate_outcome,
        "baseline_minor": baseline_minor,
        "candidate_minor": candidate_minor,
        "baseline_error_code": baseline_code,
        "candidate_error_code": candidate_code,
        "exposure_years": Decimal(exposure),
    }


def _dspec(
    *,
    segments: list[str] | None = None,
    edges: list[str] | None = None,
    threshold: str = "10",
) -> DislocationSpec:
    return DislocationSpec(
        baseline_ref=_BASE_REF,
        candidate_ref=_CAND_REF,
        portfolio_dataset_version_id=uuid4(),
        purpose="renewal",
        as_at=date(2026, 9, 1),
        segments=segments or [],
        band_edges_pct=edges or ["-10", "-5", "0", "5", "10"],
        mover_threshold_pct=threshold,
    )


def _book16() -> pl.DataFrame:
    """Sixteen policies. P01..P09 baseline 1000, exposure as stated, region N/S/null; P10 a zero
    baseline, P11 a negative baseline; P12 quoted_to_declined; P13 declined_both; P14 an error
    in both passes; P15 an error in the candidate pass only; P16 declined_to_quoted."""
    return _frame(
        [
            _q("P01", 1000, 850, "1", "N", "risk_premium"),
            _q("P02", 1000, 920, "0.5", "N", "risk_premium"),
            _q("P03", 1000, 960, "0.5", "S", "office_premium"),
            _q("P04", 1000, 1000, "1", "S", None),
            _q("P05", 1000, 1030, "1", "N", "office_premium"),
            _q("P06", 1000, 1050, "0.25", None, "office_premium"),
            _q("P07", 1000, 1070, "0.75", "S", "payable_premium"),
            _q("P08", 1000, 1100, "1", "N", "payable_premium"),
            _q("P09", 1000, 1200, "1", None, "risk_premium"),
            _q("P10", 0, 500, "1", "N", "risk_premium"),
            _q("P11", -200, -100, "1", "S", "risk_premium"),
            _other("P12", "quoted", "declined", baseline_minor=1000, exposure="2"),
            _other("P13", "declined", "declined"),
            _other(
                "P14",
                "error",
                "error",
                baseline_code="RATING_EVALUATION_FAILED",
                candidate_code="INPUT_CONTRACT_VIOLATION",
            ),
            _other("P15", "declined", "error", candidate_code="INPUT_CONTRACT_VIOLATION"),
            _other("P16", "declined", "quoted", candidate_minor=700),
        ]
    )


@pytest.mark.req("NFR-496")
def test_dislocation_totals_are_sums_of_per_policy_minor_units() -> None:
    """Compared set P01..P11. Σ baseline = 9x1000 + 0 - 200 = 8800; Σ candidate =
    850+920+960+1000+1030+1050+1070+1100+1200 (= 9180) + 500 - 100 = 9580.
    Mutation: sum `baseline_minor` over every quoted baseline row (adds P12's 1000 → 9800)."""
    run = summarise_dislocation(_book16(), _dspec())
    assert type(run.totals.baseline_premium_minor) is int
    assert type(run.totals.candidate_premium_minor) is int
    assert run.totals.baseline_premium_minor == 8800
    assert run.totals.candidate_premium_minor == 9580


@pytest.mark.req("FR-263")
def test_dislocation_change_pct_is_the_ruled_ratio() -> None:
    """Σ change = 9580 - 8800 = 780; 780 / 8800 x 100 = 8.8636… → 8.86 (round once, half-even).
    Mutation: the unweighted mean of per-policy percentages over the banded set
    (-15 -8 -4 0 3 5 7 10 20 → 18/9 = 2.0)."""
    run = summarise_dislocation(_book16(), _dspec())
    expected = float(
        Decimal(round(Fraction(780, 8800) * 100, 2).numerator)
        / Decimal(round(Fraction(780, 8800) * 100, 2).denominator)
    )
    assert run.totals.change_pct == expected == 8.86


@pytest.mark.req("FR-263")
def test_dislocation_rounds_each_ratio_once() -> None:
    """Two policies, baselines 5 000 000 each, changes 6 749 and 6 750: Σchange 13 499 over
    Σbaseline 10 000 000 is 0.13499 %. One rounding of the exact fraction gives 0.13.
    The two-step form — `Decimal(n) / Decimal(d)` at prec=4 (0.001350), x 100, quantize
    half-even — gives 0.14. Mutation: that two-step conversion."""
    frame = _frame([_q("A", 5_000_000, 5_006_749), _q("B", 5_000_000, 5_006_750)])
    run = summarise_dislocation(frame, _dspec())
    assert run.totals.change_pct == 0.13


@pytest.mark.req("FR-263")
def test_dislocation_bands_count_policies_and_exposure_shares() -> None:
    """Edges -10 -5 0 5 10. Exact change %: P01 -15 | P02 -8 | P03 -4 | P04 0, P05 +3 |
    P06 +5, P07 +7 | P08 +10, P09 +20 — an edge is in the UPPER band. Counts 1,1,1,2,2,2 = 9
    = quoted_both 11 - zero_baseline 1 - negative_baseline 1. The banded Σ exposure is
    1+.5+.5+1+1+.25+.75+1+1 = 7: shares 1/7=.142857, .071429, .071429, 2/7=.285714,
    1/7=.142857, 2/7=.285714 (the compared set's 9 would give 1/9 for the first).
    Mean %: -15, -8, -4, (0+30)/2000=1.5, (50+70)/2000=6.0, (100+200)/2000=15.0.
    Mutations: the edge test `> lo` for `>= lo`; a denominator over the compared set."""
    run = summarise_dislocation(_book16(), _dspec())
    assert [b.band for b in run.distribution] == [
        "< -10%",
        "-10% to -5%",
        "-5% to 0%",
        "0% to +5%",
        "+5% to +10%",
        "≥ +10%",
    ]
    assert [b.policies for b in run.distribution] == [1, 1, 1, 2, 2, 2]
    assert [b.exposure_share for b in run.distribution] == [
        0.142857,
        0.071429,
        0.071429,
        0.285714,
        0.142857,
        0.285714,
    ]
    assert [b.mean_change_pct for b in run.distribution] == [-15.0, -8.0, -4.0, 1.5, 6.0, 15.0]
    o = run.outcomes
    assert sum(b.policies for b in run.distribution) == 9
    assert sum(b.policies for b in run.distribution) == (
        o.quoted_both - o.zero_baseline - o.negative_baseline
    )


@pytest.mark.req("FR-263")
def test_dislocation_empty_band_mean_is_none() -> None:
    """One banded policy (-15 %); every other band has `policies == 0`, a null mean and an
    `exposure_share` of 0.0 (a zero numerator over a banded Σ of 1). A book with no banded
    policy at all has every share null, and a null `change_pct` when Σ baseline is 0.
    Mutation: return `0.0` for a zero denominator."""
    run = summarise_dislocation(_frame([_q("A", 1000, 850)]), _dspec())
    empties = [b for b in run.distribution if b.policies == 0]
    assert len(empties) == 5
    assert all(b.mean_change_pct is None and b.exposure_share == 0.0 for b in empties)

    only_zero = summarise_dislocation(_frame([_q("A", 0, 100)]), _dspec())
    assert all(
        b.exposure_share is None and b.mean_change_pct is None for b in only_zero.distribution
    )
    assert only_zero.totals.change_pct is None
    assert only_zero.totals.candidate_premium_minor == 100


@pytest.mark.req("FR-264")
def test_dislocation_by_segment_reports_each_level() -> None:
    """Compared set P01..P11 by `region`; compared Σ exposure 9.
    N: P01 P02 P05 P08 P10 → 5 policies, Σbase 4000, Σchg -150-80+30+100+500 = 400 → 10.0;
    exposure 4.5/9 = 0.5.  S: P03 P04 P07 P11 → 4, Σbase 2800, Σchg -40+0+70+100 = 130 →
    4.642857 → 4.64; 3.25/9 = 0.361111.  null: P06 P09 → 2, Σbase 2000, Σchg 250 → 12.5;
    1.25/9 = 0.138889. The null level is last. Mutation: filter nulls out of `by_segment`."""
    run = summarise_dislocation(_book16(), _dspec(segments=["region"]))
    got = [
        (s.factor, s.level, s.policies, s.mean_change_pct, s.exposure_share) for s in run.by_segment
    ]
    assert got == [
        ("region", "N", 5, 10.0, 0.5),
        ("region", "S", 4, 4.64, 0.361111),
        ("region", None, 2, 12.5, 0.138889),
    ]


@pytest.mark.req("FR-264")
def test_dislocation_by_ladder_rung_parts_sum_to_the_total() -> None:
    """From `_book16`: change by originating rung — risk_premium -150-80+200+500+100 = 570,
    office_premium -40+30+50 = 40, payable_premium 70+100 = 170; P04 originates nothing.
    570+40+170 = 780 = 9580 - 8800. Contributions over Σbase 8800: 6.48, 0.45, 1.93, in
    ladder order, one row per originating rung. Mutation: an origin comparing
    `unrounded_minor` alone is Task 4's `_origin_rung`; here, drop the `origin_rung` filter."""
    frame = _book16()
    run = summarise_dislocation(frame, _dspec())
    assert [(r.rung, r.contribution_pct) for r in run.by_ladder_rung] == [
        ("risk_premium", 6.48),
        ("office_premium", 0.45),
        ("payable_premium", 1.93),
    ]
    by_rung = (
        frame.filter(
            (pl.col("baseline_outcome") == "quoted") & (pl.col("candidate_outcome") == "quoted")
        )
        .group_by("origin_rung")
        .agg(pl.col("change_minor").sum())
    )
    parts = {r["origin_rung"]: r["change_minor"] for r in by_rung.iter_rows(named=True)}
    assert sum(parts.values()) == 9580 - 8800
    assert sum(Fraction(v, 8800) * 100 for v in parts.values()) == Fraction(780, 8800) * 100


@pytest.mark.req("FR-264")
def test_dislocate_is_the_summary_of_the_frame_on_a_real_book() -> None:
    """A relativity candidate moves only `direct` policies, at `office_premium` (Task 4)."""
    base = _compiled_from(_algorithm_payload())
    cand = _compiled_from(_algorithm_payload(), expense_direct="1.2")
    spec = _dspec(segments=["channel"])
    run = dislocate(base, cand, _policies(), spec)
    frame = dislocation_frame(base, cand, _policies(), spec)
    assert run == summarise_dislocation(frame, spec)
    assert [r.rung for r in run.by_ladder_rung] == ["office_premium"]
    total = run.totals.candidate_premium_minor - run.totals.baseline_premium_minor
    assert total == frame["change_minor"].sum() > 0
    assert run.policy_count == 3


@pytest.mark.req("FR-263")
def test_dislocation_outcomes_and_errors_are_counted() -> None:
    """`_book16`: quoted_both 11, quoted_to_declined 1, declined_to_quoted 1, declined_both 1,
    error 2 (P14, P15) — the first five sum to 16; zero_baseline 1 (P10), negative_baseline 1
    (P11). P14 errored in both passes and is counted once, under the baseline's code
    RATING_EVALUATION_FAILED; P15 under the candidate's INPUT_CONTRACT_VIOLATION; codes in
    order. 12 more erroring policies give a `sample` of the first 10 by `quote_id`.
    `exposure_years` = Σ over all 16 = 9 + 2 + 1+1+1+1+1 = 15.
    Mutation: count a both-pass error under both codes."""
    run = summarise_dislocation(_book16(), _dspec())
    o = run.outcomes
    assert (
        o.quoted_both,
        o.quoted_to_declined,
        o.declined_to_quoted,
        o.declined_both,
        o.error,
        o.zero_baseline,
        o.negative_baseline,
    ) == (11, 1, 1, 1, 2, 1, 1)
    assert (
        run.policy_count
        == 16
        == (o.quoted_both + o.quoted_to_declined + o.declined_to_quoted + o.declined_both + o.error)
    )
    assert [(e.code, e.count) for e in run.errors] == [
        ("INPUT_CONTRACT_VIOLATION", 1),
        ("RATING_EVALUATION_FAILED", 1),
    ]
    assert run.errors[0].sample is not None
    assert [x.model_dump() for x in run.errors[0].sample] == [{"quote_id": "P15"}]
    assert run.exposure_years == Decimal("15.000000")

    many = _frame([_other(f"E{i:02d}", "error", "quoted", baseline_code="BOOM") for i in range(12)])
    tally = summarise_dislocation(many, _dspec()).errors[0]
    assert tally.count == 12
    assert tally.sample is not None
    assert [x.quote_id for x in tally.sample] == [f"E{i:02d}" for i in range(10)]


@pytest.mark.req("FR-263")
def test_dislocation_movers_are_kept_for_drill_down() -> None:
    """Threshold 10. In: X +20 %, then A -12 % and B +12 % (same |pct|, same |change| 120, so
    by `quote_id`: A, B), then E at exactly +10 %. Out: F one minor unit below +10 % (1099),
    Z (zero baseline), N (negative baseline: -100 ≥ 10 % x -200 would admit it unguarded),
    D (quoted_to_declined). The frame lists B before A. Expected `["X","A","B","E"]`.
    Mutations: sort by signed change; drop the `quote_id` tie-break."""
    frame = _frame(
        [
            _q("F", 1000, 1099),
            _q("E", 1000, 1100),
            _q("B", 1000, 1120),
            _q("Z", 0, 200),
            _q("N", -200, -100),
            _q("A", 1000, 880),
            _other("D", "quoted", "declined", baseline_minor=1000),
            _q("X", 1000, 1200),
        ]
    )
    movers = select_movers(frame, _dspec(threshold="10"))
    assert movers["quote_id"].to_list() == ["X", "A", "B", "E"]
    assert movers.columns == frame.columns


@pytest.mark.req("FR-263")
def test_select_movers_breaks_a_pct_tie_by_absolute_minor_change() -> None:
    """Audit-9734 N1: M1 (1000 → 1150) and M2 (2000 → 2300) are both +15 %; the larger
    |change| (300) goes first. Mutation: remove sort step 2, which gives ["M1", "M2"]."""
    frame = _frame([_q("M1", 1000, 1150), _q("M2", 2000, 2300)])
    assert select_movers(frame, _dspec())["quote_id"].to_list() == ["M2", "M1"]


# ---------------------------------------------------------------------------
# Task 6: NFR-495 — byte-identical across processes (mirrors test_testing_determinism.py).
# ---------------------------------------------------------------------------


_TESTS_DIR = str(pathlib.Path(__file__).parent)

_CHILD = textwrap.dedent(
    """
    import sys
    from datetime import date
    from uuid import UUID

    sys.path.insert(0, sys.argv[1])
    from test_rating_dislocation import _BASE_REF, _CAND_REF, _compiled_from, _policies
    from test_rating_score import _algorithm_payload

    from model_schema.dislocation import DislocationSpec
    from pricing_core.rating.analysis import dislocate

    base = _compiled_from(_algorithm_payload())
    cand = _compiled_from(_algorithm_payload(), expense_direct="1.2")
    spec = DislocationSpec(
        baseline_ref=_BASE_REF,
        candidate_ref=_CAND_REF,
        portfolio_dataset_version_id=UUID(int=1),  # fixed: a uuid4 would differ per process
        purpose="renewal",
        as_at=date(2026, 9, 1),
        segments=["channel"],
        band_edges_pct=["-10", "-5", "0", "5", "10"],
        mover_threshold_pct="10",
    )
    exposure = [1.0, 0.5, 1.0]
    if len(sys.argv) > 2 and sys.argv[2] == "mutate":
        exposure[0] = 2.0  # the first policy's exposure changes: the run must differ
    book = _policies(exposure_years=exposure)
    print(dislocate(base, cand, book, spec).model_dump_json())
    """
)


def _child(hashseed: str, *, mutate_first_row: bool = False) -> str:
    """`run.model_dump_json()` from a fresh interpreter under `PYTHONHASHSEED=hashseed`."""
    argv = [sys.executable, "-c", _CHILD, _TESTS_DIR]
    if mutate_first_row:
        argv.append("mutate")
    out = subprocess.run(
        argv,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHASHSEED": hashseed},
    )
    return out.stdout.strip().splitlines()[-1]


@pytest.mark.req("NFR-495")
def test_dislocation_is_byte_identical_across_fresh_interpreters() -> None:
    assert _child("1") == _child("2")
    assert '"totals"' in _child("1")  # the run is really there to compare


@pytest.mark.req("NFR-495")
def test_the_comparator_can_fail_when_the_portfolio_changes() -> None:
    assert _child("1") != _child("1", mutate_first_row=True)
