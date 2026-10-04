"""The Dislocation Run (03 FR-263, FR-264; §4.8's portfolio frame). WK-673 Slice 2, PL-1403."""

from __future__ import annotations

import asyncio
import copy
from datetime import date
from decimal import Decimal
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
    dislocation_frame,
    read_portfolio,
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
