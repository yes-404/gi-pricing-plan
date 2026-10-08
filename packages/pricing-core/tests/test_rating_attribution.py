"""Attribution: derived changes, exact Shapley, largest remainder (03 FR-266, FR-1397, FR-1398,
FR-1399; §4.6, §5.2). WK-673 Slice 3, PL-1452, with RL-1449 and RL-1451."""

from __future__ import annotations

import asyncio
import copy
import os
import subprocess
import sys
import textwrap
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from fractions import Fraction
from itertools import combinations
from math import factorial
from pathlib import Path
from typing import Any
from uuid import UUID

import polars as pl
import pytest
from test_rating_dislocation import _Spy, _with_secret_step
from test_rating_score import _algorithm_payload, _FakeResolver, _version

from model_schema.dislocation import ChangeGroup, DislocationSpec
from model_schema.rating import Pins
from model_schema.refs import ArtifactRef
from pricing_core.rating import analysis
from pricing_core.rating.analysis import (
    AttributionError,
    attribute,
    derive_changes,
    dislocation_frame,
    estimate_attribution_ratings,
)
from pricing_core.rating.compile import compile_bundle
from pricing_core.rating.runtime import load_bundle
from pricing_core.safe_error import CodedError

_TESTS_DIR = str(Path(__file__).parent)
_BASE_ALG = "rating_algorithm:score-fixture@1"
_CAND_ALG = "rating_algorithm:score-fixture@2"
_TABLE_1 = "rate_table:motor-expense@1"
_TABLE_2 = "rate_table:motor-expense@2"


def _ref(text: str) -> ArtifactRef:
    kind, rest = text.split(":")
    slug, version = rest.split("@")
    return ArtifactRef(type=kind, slug=slug, version=int(version))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Fixtures: the S2 score fixture, and a candidate built from named edits.
# ---------------------------------------------------------------------------


def _step(alg: dict[str, Any], step_id: str) -> dict[str, Any]:
    return next(s for s in alg["steps"] if s["step_id"] == step_id)


def _e_table(alg: dict[str, Any]) -> None:
    _step(alg, "s_expense")["rate_table_ref"] = _TABLE_2


def _e_instalment(alg: dict[str, Any]) -> None:
    _step(alg, "s_instalment")["expr"] = "office_premium_minor * 1.10"


def _e_office(alg: dict[str, Any]) -> None:
    _step(alg, "s_office")["expr"] = "risk_premium_minor * expense_factor + 500"


#: Sorted by `step_id`: c1 `s_expense` (table_repointed), c2 `s_instalment`, c3 `s_office`.
_THREE = (_e_table, _e_instalment, _e_office)


def _candidate_payload(*edits: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    alg = copy.deepcopy(_algorithm_payload())
    alg["version"] = 2
    for edit in edits:
        edit(alg)
    return alg


def _resolver(
    cand: dict[str, Any] | None = None, *, base: dict[str, Any] | None = None
) -> _FakeResolver:
    resolver = _FakeResolver()
    if base is not None:
        resolver._payloads[_BASE_ALG] = base
    if cand is not None:
        resolver._payloads[_CAND_ALG] = cand
    table_2 = copy.deepcopy(resolver._payloads[_TABLE_1])
    table_2["version"] = 2
    table_2["rows"] = [
        {"channel": "direct", "expense_factor": "1.2"},
        {"channel": "broker", "expense_factor": "1.4"},
    ]
    resolver._payloads[_TABLE_2] = table_2
    return resolver


def _candidate_version(*, table: bool = False, extra_pins: tuple[str, ...] = ()) -> Any:
    base = _version()
    assert base.pins is not None
    tables = [_ref(_TABLE_2 if table else _TABLE_1), *(_ref(t) for t in extra_pins)]
    pins = Pins(
        rate_tables=tables,
        models=base.pins.models,
        reference_tables=base.pins.reference_tables,
        custom_objectives=base.pins.custom_objectives,
    )
    return base.model_copy(update={"algorithm_ref": _ref(_CAND_ALG), "pins": pins})


def _book(n: int = 12, **columns: list[object]) -> pl.LazyFrame:
    data: dict[str, list[object]] = {
        "quote_id": [f"Q{i:03d}" for i in range(n)],
        "exposure_years": [1.0] * n,
        "driver_age": [18 + (i * 7) % 60 for i in range(n)],
        "channel": ["direct" if i % 2 == 0 else "broker" for i in range(n)],
        "min_premium_minor": [0] * n,
        "sanity_cap_minor": [999_999_999] * n,
        "sanity_floor_minor": [0] * n,
    }
    data.update(columns)
    return pl.DataFrame(data, strict=False).lazy()


def _spec(groups: list[tuple[str, list[str]]] | None = None) -> DislocationSpec:
    return DislocationSpec(
        baseline_ref=_ref("rating_version:score-fixture@1"),
        candidate_ref=_ref("rating_version:score-fixture@2"),
        portfolio_dataset_version_id=UUID(int=1),
        purpose="renewal",
        as_at=date(2026, 9, 1),
        band_edges_pct=["-5", "5"],
        mover_threshold_pct="10",
        change_groups=(
            None if groups is None else [ChangeGroup(name=n, changes=c) for n, c in groups]
        ),
    )


def _run(
    cand: dict[str, Any],
    *,
    table: bool = False,
    book: pl.LazyFrame | None = None,
    groups: list[tuple[str, list[str]]] | None = None,
    resolver: Any = None,
    extra_pins: tuple[str, ...] = (),
) -> Any:
    resolver = resolver or _resolver(cand)
    return asyncio.run(
        attribute(
            _version(),
            _candidate_version(table=table, extra_pins=extra_pins),
            book if book is not None else _book(),
            _spec(groups),
            resolver,
        )
    )


class _CompileSpy:
    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.slugs: list[str] = []
        real = analysis.compile_bundle

        async def spy(version: Any, resolver: Any) -> Any:
            self.slugs.append(version.algorithm_ref.slug)
            return await real(version, resolver)

        monkeypatch.setattr(analysis, "compile_bundle", spy)


# ---------------------------------------------------------------------------
# Task 3: derive_changes (FR-1399).
# ---------------------------------------------------------------------------


def _derive(cand: dict[str, Any], **kw: Any) -> list[Any]:
    return asyncio.run(derive_changes(_version(), _candidate_version(**kw), _resolver(cand)))


@pytest.mark.req("FR-1399")
def test_derive_changes_one_change_per_step_id_sorted() -> None:
    def edit(alg: dict[str, Any]) -> None:
        alg["steps"] = [s for s in alg["steps"] if s["step_id"] != "s_decl_floor"]
        alg["steps"].append(
            {
                "step_id": "s_a_extra",
                "type": "constraint",
                "label": "Extra decline",
                "condition": "office_premium_minor >= 0",
                "on_violation": "decline",
                "reason_code": "EXTRA",
                "consumes": ["office_premium_minor"],
            }
        )
        step = _step(alg, "s_instalment")
        step["expr"] = "office_premium_minor * 1.10"
        step["label"] = "Instalment loading (revised)"

    changes = _derive(_candidate_payload(edit))
    assert [(c.id, c.kind) for c in changes] == [
        ("c1", "step_added"),
        ("c2", "step_removed"),
        ("c3", "step_changed"),
    ]
    assert [c.description.split(":")[0] for c in changes] == [
        "s_a_extra",
        "s_decl_floor",
        "s_instalment",
    ]
    assert "expr" in changes[2].description
    assert "label" in changes[2].description


@pytest.mark.req("FR-1399")
def test_derive_changes_table_repoint_is_one_change() -> None:
    """RL-1394 Acceptance: only one step's table ref `@1 -> @2`, its pin carried, no pin change."""
    changes = _derive(_candidate_payload(_e_table), table=True)
    assert [(c.id, c.kind) for c in changes] == [("c1", "table_repointed")]


@pytest.mark.req("FR-1399")
def test_derive_changes_unaccounted_pin_is_its_own_change_after_the_steps() -> None:
    changes = _derive(_candidate_payload(_e_table), table=True, extra_pins=("rate_table:unused@1",))
    assert [(c.id, c.kind) for c in changes] == [("c1", "table_repointed"), ("c2", "pin")]
    assert "rate_table:unused@1" in changes[1].description


@pytest.mark.req("FR-1399")
def test_derive_changes_refuses_a_model_reference_mode_difference() -> None:
    cand_version = _candidate_version().model_copy(update={"model_reference_mode": "approximation"})
    with pytest.raises(AttributionError, match="model_reference_mode") as exc:
        asyncio.run(
            derive_changes(_version(), cand_version, _resolver(_candidate_payload(_e_office)))
        )
    assert exc.value.code == "VALIDATION_FAILED"


@pytest.mark.req("FR-1399")
def test_contract_change_with_no_reader_is_one_input_field_change() -> None:
    """RL-1449 violation 3 (DP-3 (beta), case 2): only `driver_age`'s `max` 99 -> 90."""
    cand = _candidate_payload()
    next(f for f in cand["input_contract"] if f["name"] == "driver_age")["max"] = 90
    changes = _derive(cand)
    assert [(c.id, c.kind) for c in changes] == [("c1", "input_field")]
    assert "driver_age" in changes[0].description


def _vehicle_age_base() -> dict[str, Any]:
    """The score fixture plus `vehicle_age`, read by two input steps that feed a decline."""
    alg = copy.deepcopy(_algorithm_payload())
    alg["input_contract"].append({"name": "vehicle_age", "type": "int", "nullable": False})
    alg["steps"] += [
        {
            "step_id": "in_vage",
            "type": "input",
            "label": "Vehicle age",
            "input_name": "vehicle_age",
            "on_missing": "error",
            "produces": "vage",
        },
        {
            "step_id": "in_vage_band",
            "type": "input",
            "label": "Vehicle age (band)",
            "input_name": "vehicle_age",
            "on_missing": "error",
            "produces": "vage_band",
        },
        {
            "step_id": "s_vage_x",
            "type": "expression",
            "label": "Vehicle age mix",
            "expr": "vage + vage_band",
            "result_type": "money_minor",
            "consumes": ["vage", "vage_band"],
            "produces": "vage_x",
        },
        {
            "step_id": "s_vage_c",
            "type": "constraint",
            "label": "Vehicle age bound",
            "condition": "vage_x >= 0",
            "on_violation": "decline",
            "reason_code": "VAGE",
            "consumes": ["vage_x"],
        },
    ]
    return alg


def _vehicle_age_cand() -> dict[str, Any]:
    cand = copy.deepcopy(_vehicle_age_base())
    cand["version"] = 2
    next(f for f in cand["input_contract"] if f["name"] == "vehicle_age")["type"] = "decimal"
    _step(cand, "in_vage")["label"] = "Vehicle age (revised)"
    _step(cand, "in_vage_band")["label"] = "Vehicle age band (revised)"
    return cand


@pytest.mark.req("FR-1399")
def test_delta_with_two_readers_is_its_own_change_and_refused_ungrouped() -> None:
    """RL-1449 violation 5 (DP-3 case 3): three changes, the third `input_field`; c1 without c3
    is refused naming (c1, c3)."""
    cand = _vehicle_age_cand()
    resolver = _resolver(cand, base=_vehicle_age_base())
    changes = asyncio.run(derive_changes(_version(), _candidate_version(), resolver))
    assert [(c.id, c.kind) for c in changes] == [
        ("c1", "step_changed"),
        ("c2", "step_changed"),
        ("c3", "input_field"),
    ]
    assert [c.description.split(":")[0] for c in changes[:2]] == ["in_vage", "in_vage_band"]
    with pytest.raises(AttributionError) as exc:
        asyncio.run(
            attribute(
                _version(),
                _candidate_version(),
                _book(),
                _spec([("a", ["c1", "c2"]), ("b", ["c3"])]),
                resolver,
            )
        )
    assert exc.value.code == "VALIDATION_FAILED"
    assert "c1" in str(exc.value)
    assert "c3" in str(exc.value)


# ---------------------------------------------------------------------------
# Task 4: groups, dependence, subset construction (FR-1398, FR-1399 T1, T3).
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-1399")
@pytest.mark.parametrize(
    ("groups", "named"),
    [
        ([("a", ["c1", "c2"])], "c3"),  # c3 left out
        ([("a", ["c1", "c2"]), ("b", ["c2", "c3"])], "c2"),  # c2 in two groups
    ],
)
def test_attribute_refuses_groups_that_do_not_partition_the_derived_changes(
    monkeypatch: pytest.MonkeyPatch, groups: list[tuple[str, list[str]]], named: str
) -> None:
    spy = _CompileSpy(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _run(_candidate_payload(*_THREE), table=True, groups=groups)
    assert exc.value.code == "VALIDATION_FAILED"
    assert named in str(exc.value)
    assert spy.slugs == []  # refused before any compile


@pytest.mark.req("FR-1398")
def test_attribute_fails_the_run_naming_a_subset_that_does_not_compile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LG-1400 Task 7 row: a subset that does not compile fails the run, never skipped."""
    real = analysis.compile_bundle

    async def failing(version: Any, resolver: Any) -> Any:
        if version.algorithm_ref.slug.endswith("-subset-010"):
            raise CodedError("PIN_NOT_APPROVED: the subset's table is not approved")
        return await real(version, resolver)

    monkeypatch.setattr(analysis, "compile_bundle", failing)
    spy = _Spy(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _run(_candidate_payload(*_THREE), table=True)
    assert exc.value.code == "BUNDLE_COMPILE_FAILED"
    assert "c2" in str(exc.value)
    assert spy.frames == []  # every subset compiles before the first rating: nothing was rated


def _ncd_candidate() -> dict[str, Any]:
    """`ncd` added with its input step `s_in_ncd`; `s_office` edited to consume it."""
    cand = _candidate_payload()
    cand["input_contract"].append({"name": "ncd", "type": "int", "nullable": False})
    cand["steps"].append(
        {
            "step_id": "s_in_ncd",
            "type": "input",
            "label": "No claims discount",
            "input_name": "ncd",
            "on_missing": "error",
            "produces": "ncd",
        }
    )
    office = _step(cand, "s_office")
    office["expr"] = "risk_premium_minor * expense_factor + ncd"
    office["consumes"] = ["risk_premium_minor", "expense_factor", "ncd"]
    return cand


@pytest.mark.req("FR-1398")
def test_subset_contract_carries_the_field_its_own_change_adds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RL-1449 violation 1 (DP-1 (c)): the subset holding the group declares `ncd`."""
    cand = _ncd_candidate()
    _e_instalment(cand)  # a third change, outside the group: the subsets are not all-or-nothing
    spy = _Spy(monkeypatch)
    result = _run(
        cand,
        book=_book(ncd=[100 + i for i in range(12)]),
        groups=[("ncd", ["c1", "c3"]), ("instalment", ["c2"])],
    )
    assert [c.kind for c in result.derived_changes] == [
        "step_added",
        "step_changed",
        "step_changed",
    ]
    assert result.derived_changes[0].description.startswith("s_in_ncd")
    # four subsets: {} and {instalment} lack `ncd`; {ncd group} and the full one declare it
    assert sum("ncd" in f.columns for f in spy.frames) == 2
    assert sum("ncd" not in f.columns for f in spy.frames) == 2


@pytest.mark.req("FR-1399")
def test_dependent_changes_ungrouped_are_refused_before_any_compile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RL-1449 violation 4 (DP-2 (i)): the consumer (c2) and its producer (c1), ungrouped."""
    spy = _CompileSpy(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _run(_ncd_candidate(), book=_book(ncd=[100] * 12))
    assert exc.value.code == "VALIDATION_FAILED"
    assert "c2" in str(exc.value)
    assert "c1" in str(exc.value)
    assert spy.slugs == []


@pytest.mark.req("FR-1398")
def test_empty_and_full_subsets_hash_equal_baseline_and_candidate() -> None:
    """RL-1449 violation 2: the subset of no changes is the baseline, of every change the
    candidate, by content hash."""
    result = _run(_candidate_payload(*_THREE), table=True)
    resolver = _resolver(_candidate_payload(*_THREE))
    base_hash = asyncio.run(compile_bundle(_version(), resolver)).content_hash
    cand_hash = asyncio.run(compile_bundle(_candidate_version(table=True), resolver)).content_hash
    hashes = result.attribution_summary.subset_bundle_hashes
    assert base_hash in hashes
    assert cand_hash in hashes
    assert base_hash != cand_hash
    assert result.attribution_summary.subset_bundle_count == len(hashes) == 8


# ---------------------------------------------------------------------------
# Task 5: Shapley, allocation, reconciliation (FR-266, FR-1397).
# ---------------------------------------------------------------------------

_V3 = {
    0b000: 1000,
    0b001: 1100,
    0b010: 1050,
    0b100: 1000,
    0b011: 1180,
    0b101: 1130,
    0b110: 1070,
    0b111: 1200,
}


def _shapley_by_formula(v: dict[int, int], k: int) -> list[int]:
    out = []
    for i in range(k):
        others = [j for j in range(k) if j != i]
        total = 0
        for size in range(k):
            for subset in combinations(others, size):
                mask = sum(1 << j for j in subset)
                total += factorial(size) * factorial(k - size - 1) * (v[mask | 1 << i] - v[mask])
        out.append(total)
    return out


@pytest.mark.req("FR-266")
def test_shapley_is_exact_over_k_factorial() -> None:
    numerators = analysis._shapley_numerators(_V3, 3)
    assert numerators == _shapley_by_formula(_V3, 3)
    assert numerators == [720, 390, 90]  # hand-computed
    assert sum(numerators) == factorial(3) * (_V3[0b111] - _V3[0])  # efficiency: 6 * 200


@pytest.mark.req("FR-266")
def test_largest_remainder_ties_go_in_declared_order() -> None:
    # K! = 6; three equal remainders, one leftover unit: it goes to the first.
    assert analysis._allocate([2, 2, 2], 3) == [1, 0, 0]
    assert analysis._allocate([6, 6, 6], 3) == [1, 1, 1]


@pytest.mark.req("FR-266")
def test_largest_remainder_handles_negative_parts() -> None:
    """Floors toward -infinity, remainders in [0, K!); the two largest remainders (5, 5) win."""
    parts = analysis._allocate([-1, -1, 8], 3)
    assert parts == [0, 0, 1]
    assert sum(parts) == 1


def _break_plain_rounding(monkeypatch: pytest.MonkeyPatch) -> None:
    def plain(numerators: list[int], k: int) -> list[int]:
        return [round(Fraction(p, factorial(k))) for p in numerators]

    monkeypatch.setattr(analysis, "_allocate", plain)


@pytest.mark.req("FR-1397")
def test_reconciliation_refuses_plain_rounding_allocation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The allocator is plain rounding on a policy where plain rounding does not sum."""
    _break_plain_rounding(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _run(_candidate_payload(*_THREE), table=True)
    assert exc.value.code == "ATTRIBUTION_RECONCILIATION_FAILED"
    assert "Q0" in str(exc.value)


@pytest.mark.req("FR-1397")
def test_reconciliation_refuses_a_shapley_value_perturbed_by_one_minor_unit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = analysis._allocate

    def perturbed(numerators: list[int], k: int) -> list[int]:
        parts = real(numerators, k)
        return [parts[0] + 1, *parts[1:]]

    monkeypatch.setattr(analysis, "_allocate", perturbed)
    with pytest.raises(AttributionError) as exc:
        _run(_candidate_payload(*_THREE), table=True)
    assert exc.value.code == "ATTRIBUTION_RECONCILIATION_FAILED"
    assert "Q000" in str(exc.value)


@pytest.mark.req("FR-1397")
def test_reconciliation_refuses_isolated_plus_residual_off_by_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = analysis._residual

    monkeypatch.setattr(analysis, "_residual", lambda total, isolated: real(total, isolated) + 1)
    with pytest.raises(AttributionError) as exc:
        _run(_candidate_payload(*_THREE), table=True)
    assert exc.value.code == "ATTRIBUTION_RECONCILIATION_FAILED"
    assert "Q000" in str(exc.value)


# ---------------------------------------------------------------------------
# Task 6: attribute end to end.
# ---------------------------------------------------------------------------


def _hand_values(mask: int, book: pl.LazyFrame) -> dict[str, int]:
    """v(S) by hand: the baseline with the edits of the changes in `mask` applied, rated by S2's
    `dislocation_frame` (independent of `attribute`'s subset construction)."""
    alg = copy.deepcopy(_algorithm_payload())
    chosen = [e for i, e in enumerate(_THREE) if mask >> i & 1]
    for edit in chosen:
        edit(alg)
    table = _e_table in chosen
    resolver = _resolver(base=alg)
    version = _version().model_copy(update={"pins": _candidate_version(table=table).pins})
    bundle = load_bundle(asyncio.run(compile_bundle(version, resolver)))
    frame = dislocation_frame(bundle, bundle, book, _spec())
    return dict(zip(frame["quote_id"], frame["baseline_minor"], strict=True))


@pytest.mark.req("FR-266")
def test_isolated_and_cumulative_views_and_residual_line() -> None:
    book = _book()
    result = _run(_candidate_payload(*_THREE), table=True, book=book)
    v = {mask: _hand_values(mask, book) for mask in range(8)}
    quotes = sorted(v[0])
    total = sum(v[7][q] - v[0][q] for q in quotes)
    items = {i.group: i for i in result.attribution}
    assert list(items) == ["c1", "c2", "c3"]
    assert result.change_groups == []  # FR-1399 (clarified): the analyst's groups only; none given
    assert [c.id for c in result.derived_changes] == ["c1", "c2", "c3"]
    for g in range(3):
        item = items[f"c{g + 1}"]
        assert item.isolated_minor == sum(v[1 << g][q] - v[0][q] for q in quotes)
        prefix, before = (1 << (g + 1)) - 1, (1 << g) - 1
        assert item.cumulative_minor == sum(v[prefix][q] - v[before][q] for q in quotes)
        parts = [
            analysis._allocate(analysis._shapley_numerators({m: v[m][q] for m in v}, 3), 3)[g]
            for q in quotes
        ]
        assert item.shapley_minor == sum(parts)
    summary = result.attribution_summary
    assert summary.method == "shapley"
    assert summary.total_change_minor == total
    assert sum(i.shapley_minor for i in result.attribution) == total
    assert sum(i.cumulative_minor for i in result.attribution) == total
    assert summary.residual_minor == total - sum(i.isolated_minor for i in result.attribution)
    assert summary.orders_sampled is None
    assert summary.order_sensitivity_lower_bound is None
    assert summary.residual_share is None


@pytest.mark.req("NFR-496")
def test_attribution_portfolio_figures_are_sums_of_policy_parts() -> None:
    """NFR-496 applied: run on one policy at a time, the portfolio's figures are the sums."""
    book = _book(6)
    whole = _run(_candidate_payload(*_THREE), table=True, book=book)
    singles = [
        _run(
            _candidate_payload(*_THREE),
            table=True,
            book=_book(6).filter(pl.col("quote_id") == f"Q{i:03d}"),
        )
        for i in range(6)
    ]
    for g in range(3):
        one = [s.attribution[g] for s in singles]
        assert whole.attribution[g].shapley_minor == sum(i.shapley_minor for i in one)
        assert whole.attribution[g].isolated_minor == sum(i.isolated_minor for i in one)
    assert whole.attribution_summary.total_change_minor == sum(
        s.attribution_summary.total_change_minor for s in singles
    )


def _seven_chain(constant: str) -> dict[str, Any]:
    """Seven chained expression steps scaling `expense_factor`, between the table and the office
    premium (a step after the instalment would break the ladder: the payable rung is the last)."""
    alg = copy.deepcopy(_algorithm_payload())
    prev = "expense_factor"
    steps = []
    for i in range(1, 8):
        steps.append(
            {
                "step_id": f"s_x{i}",
                "type": "expression",
                "label": f"x{i}",
                "expr": f"{prev} * {constant}",
                "result_type": "decimal",
                "consumes": [prev],
                "produces": f"x{i}",
            }
        )
        prev = f"x{i}"
    office = _step(alg, "s_office")
    office["expr"] = f"risk_premium_minor * {prev}"
    office["consumes"] = ["risk_premium_minor", prev]
    alg["steps"] += steps
    return alg


def _seven_run(groups: list[tuple[str, list[str]]] | None = None) -> Any:
    base = _seven_chain("1.00")
    cand = _seven_chain("1.03")
    cand["version"] = 2
    return asyncio.run(
        attribute(
            _version(),
            _candidate_version(),
            _book(6),
            _spec(groups),
            _resolver(cand, base=base),
        )
    )


@pytest.mark.req("FR-266")
def test_above_six_ungrouped_is_order_dependent_with_r_and_s_bound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spy = _CompileSpy(monkeypatch)
    result = _seven_run()
    summary = result.attribution_summary
    assert [c.kind for c in result.derived_changes] == ["step_changed"] * 7
    assert result.change_groups == []  # not one group per change: the bound is 6
    assert [i.group for i in result.attribution] == [c.id for c in result.derived_changes]
    assert summary.method == "order_dependent"
    assert summary.orders_sampled == 2
    assert all(i.shapley_minor is None for i in result.attribution)
    assert summary.subset_valuation == "rerate"
    assert summary.replay_fell_back is False
    assert len(spy.slugs) == summary.subset_bundle_count == 3 * 7 - 2  # never 2**7
    iso = [i.isolated_minor for i in result.attribution]
    d = sum(abs(x) for x in iso)
    assert d > 0
    residual = summary.residual_minor
    expected = (Decimal(abs(residual)) / Decimal(d)).quantize(Decimal("0.000001"))
    assert summary.residual_share == expected
    assert summary.order_sensitivity_lower_bound is not None
    assert summary.order_sensitivity_lower_bound >= 0
    assert residual == summary.total_change_minor - sum(iso)
    assert sum(i.cumulative_minor for i in result.attribution) == summary.total_change_minor


@pytest.mark.req("FR-266")
def test_above_six_grouped_runs_shapley_over_groups() -> None:
    ids = [f"c{i}" for i in range(1, 8)]
    groups = [("g1", ids[:3]), ("g2", ids[3:5]), ("g3", ids[5:])]
    result = _seven_run(groups)
    summary = result.attribution_summary
    assert summary.method == "shapley"
    assert summary.subset_bundle_count == 8
    assert [i.group for i in result.attribution] == ["g1", "g2", "g3"]
    assert sum(i.shapley_minor for i in result.attribution) == summary.total_change_minor


@pytest.mark.req("FR-266")
def test_estimate_attribution_ratings_counts() -> None:
    assert estimate_attribution_ratings(3, 10, grouped=False) == 80
    assert estimate_attribution_ratings(6, 10, grouped=True) == 640
    assert estimate_attribution_ratings(7, 10, grouped=False) == 190  # 3 * 7 - 2
    with pytest.raises(ValueError, match="at most 6"):
        estimate_attribution_ratings(7, 10, grouped=True)


@pytest.mark.req("FR-1398")
def test_attribute_undeclared_column_never_reaches_the_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RL-1394 Acceptance, Slice 3's half: every subset's premium ignores the secret column."""
    base = _with_secret_step()
    cand = copy.deepcopy(base)
    cand["version"] = 2
    _e_instalment(cand)
    spy = _Spy(monkeypatch)
    resolver = _resolver(cand, base=base)

    def go(book: pl.LazyFrame) -> Any:
        return asyncio.run(attribute(_version(), _candidate_version(), book, _spec(), resolver))

    with_col = go(_book(secret_loading=[500 + 10 * i for i in range(12)]))
    without = go(_book())
    assert with_col.model_dump_json() == without.model_dump_json()
    assert spy.frames
    assert all("secret_loading" not in f.columns for f in spy.frames)


@pytest.mark.req("FR-1398")
def test_attribute_fails_naming_a_policy_not_quoted_in_some_subset() -> None:
    """DP-S3-7 (a): quoted at the empty and the full subset, declined in one mixed subset."""

    def edit_cap(alg: dict[str, Any]) -> None:  # c1: lowers the decline threshold by 1000
        _step(alg, "s_decl_cap")["condition"] = "office_premium_minor <= sanity_cap_minor - 1000"

    def edit_office(alg: dict[str, Any]) -> None:  # c2: lowers the office premium by 600
        _step(alg, "s_office")["expr"] = "risk_premium_minor * expense_factor - 600"

    cand = _candidate_payload(edit_cap, edit_office)
    book = _book(4)
    # The office premium is about payable / 1.05; a cap 500 above it is quoted at the baseline
    # and at the candidate (premium - 600 <= cap - 1000), and declined under `c1` alone.
    payable = _hand_values(0, book)
    caps = [round(payable[q] / 1.05) + 500 for q in sorted(payable)]
    book = _book(4, sanity_cap_minor=caps)
    with pytest.raises(AttributionError) as exc:
        _run(cand, book=book)
    assert exc.value.code == "ATTRIBUTION_RECONCILIATION_FAILED"
    assert "Q000" in str(exc.value)
    assert "c1" in str(exc.value)


@pytest.mark.req("FR-1398")
def test_attribute_records_rerate_and_no_fallback() -> None:
    summary = _run(_candidate_payload(*_THREE), table=True).attribution_summary
    assert summary.subset_valuation == "rerate"
    assert summary.replay_fell_back is False


_CHILD = textwrap.dedent(
    """
    import sys
    sys.path.insert(0, sys.argv[1])
    from test_rating_attribution import _scenario_json
    print(_scenario_json())
    """
)


def _scenario_json() -> str:
    return _run(_candidate_payload(*_THREE), table=True).model_dump_json()


def _child(hashseed: str) -> str:
    out = subprocess.run(
        [sys.executable, "-c", _CHILD, _TESTS_DIR],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHASHSEED": hashseed},
    )
    return out.stdout.strip().splitlines()[-1]


@pytest.mark.req("NFR-495")
def test_attribute_is_byte_identical_across_processes() -> None:
    first, second = _child("1"), _child("2")
    assert first == second
    assert '"attribution_summary"' in first
