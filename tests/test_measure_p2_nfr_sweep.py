"""`scripts/measure-p2-nfr-sweep.py` (WK-1178, SL-1736, PL-1735): the pure decision logic.

The harness's timed phases need a database, a quiet box and a granted window, so they are
not run here. What decides a reading is pure and is tested here: the contention factor and its
band (PL-1735 Task 0), the DP-1 latency bands, the NFR-1443 ratio bands, NFR-470's rule, NFR-467's
memory rule and NFR-485's cap. A band that is wrong silently turns an OVER into a PASS, so each
boundary has a case on both sides of it.

No `@pytest.mark.req` marker: this is the correctness of a measurement tool, not evidence for
a numbered requirement (the readings are the evidence, in LG-8155).

The file name has a hyphen, so the module is loaded through `importlib`, as
`test_rating_attribution.py` loads `measure-attribution-cost.py`.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "measure-p2-nfr-sweep.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("measure_p2_nfr_sweep", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = _load()


def _run(role: str, start: float, end: float, wall: float, cpu: float = 1.0) -> dict[str, Any]:
    return {"role": role, "load_start": start, "load_end": end, "wall_s": wall, "cpu_s": cpu}


# --- the contention factor (Task 0) ---------------------------------------------------------


@pytest.mark.parametrize(
    ("role", "start", "end", "valid"),
    [
        ("A", 0.99, 5.0, True),  # an ALONE run's end load is not constrained
        ("A", 1.0, 0.1, False),  # ALONE needs load1 < 1.0 at start
        ("B", 1.0, 1.99, True),
        ("B", 0.99, 1.5, False),  # below the contended regime
        ("B", 1.5, 2.0, False),  # end must be < 2.0
        ("B", 2.0, 1.5, False),  # start must be < 2.0
    ],
)
def test_run_validity_follows_the_ruled_regime(
    role: str, start: float, end: float, valid: bool
) -> None:
    ok, reason = m.run_validity(role, start, end)
    assert ok is valid
    assert (reason == "") is valid


def test_the_factor_is_the_maximum_pair_ratio_and_the_spread_is_printed() -> None:
    runs = [
        _run("A", 0.5, 0.6, 10.0),
        _run("B", 1.5, 1.6, 25.0),  # 2.5
        _run("A", 0.4, 0.5, 10.0),
        _run("B", 1.2, 1.9, 21.0),  # 2.1
        _run("A", 0.3, 0.4, 10.0),
        _run("B", 1.1, 1.3, 23.0),  # 2.3
    ]
    result = m.contention_factor(runs)
    assert result["ratios"] == pytest.approx([2.5, 2.1, 2.3])
    assert result["factor"] == pytest.approx(2.5)
    assert result["min"] == pytest.approx(2.1)
    assert result["spread"] == pytest.approx(0.4)
    assert result["pairs"] == 3
    assert result["band"] == 0.4  # floor(100 / 2.5) / 100


def test_an_invalid_run_is_excluded_and_never_paired() -> None:
    runs = [
        _run("A", 0.5, 0.6, 10.0),
        _run("B", 2.5, 2.6, 99.0),  # contended outside the regime: excluded
        _run("B", 1.5, 1.6, 20.0),  # the next valid B pairs with the A
    ]
    result = m.contention_factor(runs)
    assert result["ratios"] == pytest.approx([2.0])
    assert [e["role"] for e in result["excluded"]] == ["B"]
    assert result["excluded"][0]["wall_s"] == 99.0


def test_an_unpaired_valid_run_is_reported_not_dropped_silently() -> None:
    runs = [
        _run("A", 0.5, 0.6, 10.0),
        _run("A", 0.5, 0.6, 10.0),  # a second A with no B between: the first is unpaired
        _run("B", 1.5, 1.6, 20.0),
        _run("B", 1.5, 1.6, 20.0),  # a B with no pending A
    ]
    result = m.contention_factor(runs)
    assert result["pairs"] == 1
    assert len(result["unpaired"]) == 2


def test_fewer_than_three_pairs_is_not_a_factor() -> None:
    runs = [_run("A", 0.5, 0.6, 10.0), _run("B", 1.5, 1.6, 20.0)]
    result = m.contention_factor(runs)
    assert result["pairs"] == 1
    assert result["factor"] is None
    assert result["band"] is None
    assert "fewer than 3 pairs" in result["note"]


@pytest.mark.parametrize(
    ("factor", "band"),
    [(2.33, 0.42), (2.3, 0.43), (2.0, 0.5), (3.0, 0.33), (1.0001, 0.99)],
)
def test_the_band_is_one_over_factor_rounded_down_to_two_decimals(
    factor: float, band: float
) -> None:
    assert m.band_from_factor(factor) == band


def test_a_factor_at_or_below_one_gives_no_band() -> None:
    assert m.band_from_factor(1.0) is None
    assert m.band_from_factor(0.8) is None


def test_the_band_uses_floor_not_round() -> None:
    # 1 / 2.35 = 0.4255...: round() would give 0.43, floor gives 0.42.
    assert m.band_from_factor(2.35) == 0.42
    assert math.isclose(1 / 2.35, 0.4255, abs_tol=1e-4)


def test_the_benchmark_line_is_parsed_from_bench_model_output() -> None:
    out = (
        "machine: ...\n"
        "  NFR-477 propose_banding equal_width      0.01 s wall   0.01 s cpu   peak RSS 1 MB\n"
        "  NFR-477 propose_grouping hierarchical_clustering     8.58 s wall"
        "     9.12 s cpu   peak RSS   950 MB\n"
    )
    assert m.parse_bench_line(out) == (8.58, 9.12)


def test_a_missing_benchmark_line_is_an_error_not_a_zero() -> None:
    with pytest.raises(ValueError, match="hierarchical_clustering"):
        m.parse_bench_line("nothing here\n")


# --- the reading bands -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("ms", "band"),
    [
        (0.0, "DIAGNOSTIC-PASS"),
        (129.0, "DIAGNOSTIC-PASS"),  # exactly 0.43 x 300
        (129.0001, "NEAR-BOUND"),
        (300.0, "NEAR-BOUND"),
        (300.0001, "DIAGNOSTIC-OVER"),
    ],
)
def test_latency_bands_at_the_interim_fraction(ms: float, band: str) -> None:
    assert m.classify_latency(ms, budget=300.0, fraction=0.43) == band


def test_the_latency_fraction_moves_with_the_measured_band() -> None:
    assert m.classify_latency(140.0, budget=300.0, fraction=0.50) == "DIAGNOSTIC-PASS"
    assert m.classify_latency(140.0, budget=300.0, fraction=0.43) == "NEAR-BOUND"


@pytest.mark.parametrize(
    ("ratio", "band"),
    [
        (1.5, "DIAGNOSTIC-PASS"),
        (1.5001, "NEAR-BOUND"),
        (2.0, "NEAR-BOUND"),
        (2.0001, "DIAGNOSTIC-OVER"),
    ],
)
def test_ratio_bands(ratio: float, band: str) -> None:
    assert m.classify_ratio(ratio) == band


def test_nearest_rank_percentile() -> None:
    values = list(range(1, 101))  # 1..100
    assert m.nearest_rank(values, 95) == 95
    assert m.nearest_rank(values, 50) == 50
    assert m.nearest_rank(values, 99) == 99
    assert m.nearest_rank(values, 100) == 100
    assert m.nearest_rank([5, 1, 3], 95) == 5  # unsorted input, rank ceil(0.95 * 3) = 3
    with pytest.raises(ValueError, match="empty sample"):
        m.nearest_rank([], 95)


@pytest.mark.parametrize(
    ("payload", "overhead", "new_bytes", "verdict"),
    [
        (1000, 200, 0, "DIAGNOSTIC-PASS"),  # exactly 1.2
        (1000, 201, 0, "DIAGNOSTIC-OVER"),
        (1000, 100, 1, "DIAGNOSTIC-OVER"),  # any new bytes for the identical table
    ],
)
def test_nfr_470_rule(payload: int, overhead: int, new_bytes: int, verdict: str) -> None:
    assert m.classify_storage(payload, overhead, new_bytes) == verdict


def test_nfr_470_a_zero_payload_is_an_error() -> None:
    with pytest.raises(ValueError, match="positive parquet payload"):
        m.classify_storage(0, 10, 0)


@pytest.mark.parametrize(("r", "verdict"), [(4.99, "PASS"), (5.0, "OVER"), (9.0, "OVER")])
def test_nfr_467_memory_ratio_is_strictly_below_five(r: float, verdict: str) -> None:
    assert m.classify_nfr467_memory(r) == verdict


def test_nfr_467_memory_ratio_needs_a_positive_small_run() -> None:
    assert m.memory_ratio(236.0, 113.0) == pytest.approx(236.0 / 113.0)
    with pytest.raises(ValueError, match="must be positive"):
        m.memory_ratio(100.0, 0.0)


@pytest.mark.parametrize(
    ("hwm_bytes", "verdict"),
    [(32 * 2**30, "PASS"), (32 * 2**30 + 1, "OVER")],
)
def test_nfr_485_cap_is_32_gib(hwm_bytes: int, verdict: str) -> None:
    assert m.classify_nfr485(hwm_bytes) == verdict


def test_vmhwm_is_read_from_proc_status_text() -> None:
    text = "Name:\tpython\nVmPeak:\t  999 kB\nVmHWM:\t  123456 kB\nVmRSS:\t   100 kB\n"
    assert m.parse_status_kb(text, "VmHWM") == 123456 * 1024
    with pytest.raises(ValueError, match="VmHWM"):
        m.parse_status_kb("Name:\tx\n", "VmHWM")


# --- pre-registration ------------------------------------------------------------------------


def test_the_pre_registered_constants_are_the_ruled_ones() -> None:
    assert m.ALONE_LOAD_BELOW == 1.0
    assert m.CONTENDED_LOAD_START == (1.0, 2.0)
    assert m.CONTENDED_LOAD_END_BELOW == 2.0
    assert m.MIN_PAIRS == 3
    assert m.CONTENTION_LABEL == "NFR-477 propose_grouping hierarchical_clustering"


# --- the settle before a timed phase (PL-1735 Tasks 2 and 5: "load settled below 2.0") --------


def test_settle_returns_at_once_when_the_load_is_already_below_the_limit() -> None:
    slept: list[float] = []
    ok, waited = m.settle_load(2.0, 600, 15, read=lambda: 1.2, sleep=slept.append)
    assert ok is True
    assert waited == 0
    assert slept == []


def test_settle_waits_until_the_load_falls_below_the_limit() -> None:
    readings = iter([3.0, 2.5, 1.9])
    slept: list[float] = []
    ok, waited = m.settle_load(2.0, 600, 15, read=lambda: next(readings), sleep=slept.append)
    assert ok is True
    assert waited == 30
    assert slept == [15, 15]


def test_settle_gives_up_after_the_maximum_wait_and_says_so() -> None:
    slept: list[float] = []
    ok, waited = m.settle_load(2.0, 45, 15, read=lambda: 5.0, sleep=slept.append)
    assert ok is False
    assert waited == 45
    assert len(slept) == 3


def test_a_load_exactly_at_the_limit_has_not_settled() -> None:
    ok, _ = m.settle_load(2.0, 0, 15, read=lambda: 2.0, sleep=lambda _s: None)
    assert ok is False


# --- the NFR-467 profile: size selection, summary and guards (Task 5a; ruling 22:52:52) ---

TWO_M, TEN_M = 2_000_000, 10_000_000


def _reading(wall: float, delta: int) -> dict[str, Any]:
    return {"wall_s": wall, "delta_peak_bytes": delta, "vmhwm_bytes": delta + 100}


def test_the_default_profile_runs_both_sizes_of_the_pre_registered_rule() -> None:
    assert m.select_profile_sizes(None) == [TWO_M, TEN_M]
    assert m.select_profile_sizes(None) == m.NFR_467_RULE["sizes"]


def test_a_two_million_only_run_selects_only_that_size() -> None:
    assert m.select_profile_sizes([TWO_M]) == [TWO_M]


def test_selected_sizes_come_back_in_the_rule_order_without_duplicates() -> None:
    assert m.select_profile_sizes([TEN_M, TWO_M, TWO_M]) == [TWO_M, TEN_M]


@pytest.mark.parametrize("bad", [[], [5_000_000], [TWO_M, 1]])
def test_a_size_outside_the_rule_or_no_size_is_refused(bad: list[int]) -> None:
    with pytest.raises(ValueError, match="sizes"):
        m.select_profile_sizes(bad)


def test_the_full_summary_reads_the_ratio_and_the_ten_million_time() -> None:
    summary = m.profile_summary({TWO_M: _reading(9.0, 100), TEN_M: _reading(60.0, 300)})
    assert summary["partial"] is False
    assert summary["memory_ratio"] == pytest.approx(3.0)
    assert summary["memory_verdict"] == "PASS"
    assert summary["time_s"] == 60.0
    assert summary["time_band"] == "DIAGNOSTIC-PASS"  # 60 s <= 0.43 x 300 s


def test_the_full_summary_marks_a_linear_memory_ratio_over() -> None:
    summary = m.profile_summary({TWO_M: _reading(9.0, 100), TEN_M: _reading(60.0, 500)})
    assert summary["memory_ratio"] == pytest.approx(5.0)
    assert summary["memory_verdict"] == "OVER"


def test_a_two_million_only_summary_reads_no_ratio_and_no_ten_million_band() -> None:
    summary = m.profile_summary({TWO_M: _reading(9.0, 100)})
    assert summary["partial"] is True
    assert "memory_ratio" not in summary
    assert "memory_verdict" not in summary
    assert "time_band" not in summary
    assert summary["sizes"] == [TWO_M]
    assert summary["by_size"][TWO_M] == {"wall_s": 9.0, "delta_peak_bytes": 100}
    assert "carried to nfr-bench-1" in summary["note"]


def test_a_ten_million_only_summary_has_its_time_band_but_no_ratio() -> None:
    summary = m.profile_summary({TEN_M: _reading(200.0, 300)})
    assert summary["partial"] is True
    assert "memory_ratio" not in summary
    assert summary["time_band"] == "NEAR-BOUND"  # 129 s < 200 s <= 300 s


@pytest.mark.parametrize(
    ("mode", "mem_gb", "disk_gb", "refused"),
    [
        ("generate-and-profile", 20.0, 20.0, False),
        ("generate-and-profile", 20.0, 11.9, True),  # the disk guard applies to generation
        ("generate-only", 20.0, 11.9, True),
        ("pregenerated", 20.0, 1.0, False),  # a pregenerated file already holds its disk
        ("pregenerated", 15.9, 50.0, True),  # the memory guard applies to every mode
        ("generate-only", 15.9, 50.0, True),
    ],
)
def test_the_profile_guards_by_mode(
    mode: str, mem_gb: float, disk_gb: float, refused: bool
) -> None:
    failure = m.profile_guard_failure(mode, mem_gb, disk_gb)
    assert (failure is not None) is refused


def test_the_profile_command_line_defaults_to_every_size_and_parses_a_subset() -> None:
    parser = m.build_parser()
    default = parser.parse_args(["profile", "--tmpdir", "/x"])
    assert default.sizes is None
    assert default.mode == "generate-and-profile"
    subset = parser.parse_args(["profile", "--tmpdir", "/x", "--sizes", "2000000"])
    assert subset.sizes == [TWO_M]
