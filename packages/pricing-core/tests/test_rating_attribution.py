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
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import load_bundle
from pricing_core.safe_error import CodedError, safe_error_text

_TESTS_DIR = str(Path(__file__).parent)
_BASE_ALG = "rating_algorithm:score-fixture@1"
_CAND_ALG = "rating_algorithm:score-fixture@2"
_TABLE_1 = "rate_table:motor-expense@1"
_TABLE_2 = "rate_table:motor-expense@2"
_NCD4 = "sub_graph:ncd-ladder@4"
_NCD5 = "sub_graph:ncd-ladder@5"


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


def _fragment(version: int, factor: int) -> dict[str, Any]:
    """A stored NCD ladder (WK-673 FD-1660): `@4` yields 1, `@5` yields 2, so a re-point moves
    every price."""
    return {
        "slug": "ncd-ladder",
        "version": version,
        "inputs": [{"name": "ncd_years", "type": "int"}],
        "outputs": [{"name": "ncd_factor", "type": "decimal", "required": True}],
        "steps": [
            {
                "step_id": "s_ladder",
                "type": "expression",
                "label": "Ladder",
                "expr": f"ncd_years * 0 + {factor}",
                "result_type": "decimal",
                "consumes": ["ncd_years"],
                "produces": "ncd_raw",
            },
            {
                "step_id": "s_cap",
                "type": "expression",
                "label": "Cap",
                "expr": "min([ncd_raw, 5])",
                "result_type": "decimal",
                "consumes": ["ncd_raw"],
                "produces": "ncd_factor",
            },
        ],
        "change_note": "ncd ladder",
    }


def _e_mounted(alg: dict[str, Any]) -> None:
    """Mount `m_ncd` (`@4`) on the score fixture: an `ncd_years` input, its input step, the mount
    and `s_office` consuming `ncd_factor` (the shape of `test_rating_score.py`'s
    `_compiled_with_a_mounted_sub_graph`). Do not follow it with `_e_office`: that rewrites
    `s_office`'s `expr` and drops `ncd_factor`."""
    alg["input_contract"].append(
        {"name": "ncd_years", "type": "int", "nullable": False, "min": 0, "max": 9}
    )
    alg["steps"].insert(
        0,
        {
            "step_id": "s_in_ncd",
            "type": "input",
            "label": "NCD years",
            "input_name": "ncd_years",
            "on_missing": "error",
            "produces": "ncd_years",
        },
    )
    office = _step(alg, "s_office")
    office["expr"] = "risk_premium_minor * expense_factor * ncd_factor"
    office["consumes"] = ["risk_premium_minor", "expense_factor", "ncd_factor"]
    alg["sub_graphs"] = [
        {
            "ref": _NCD4,
            "mount_point": "m_ncd",
            "inputs": {"ncd_years": "ncd_years"},
            "outputs": {"ncd_factor": "ncd_factor"},
        }
    ]


def _e_repoint(alg: dict[str, Any]) -> None:
    alg["sub_graphs"][0]["ref"] = _NCD5


def _mounted_base() -> dict[str, Any]:
    """The baseline that already mounts `m_ncd` at `@4` (version 1)."""
    alg = copy.deepcopy(_algorithm_payload())
    _e_mounted(alg)
    return alg


def _mounted_book() -> pl.LazyFrame:
    return _book(ncd_years=[i % 5 for i in range(12)])


def _candidate_payload(*edits: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    alg = copy.deepcopy(_algorithm_payload())
    alg["version"] = 2
    for edit in edits:
        edit(alg)
    return alg


class _MountAwareResolver(_FakeResolver):
    """The score fixture's resolver, answering a sub-graph ref with the status a stored fragment
    carries (`no_maturity_concept`, as `test_rating_compile_bundle.py` resolves one)."""

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        resolved = await super().resolve(ref)
        if ref.type == "sub_graph":
            return ResolvedArtifact(status="no_maturity_concept", payload=resolved.payload)
        return resolved


def _resolver(
    cand: dict[str, Any] | None = None, *, base: dict[str, Any] | None = None
) -> _FakeResolver:
    resolver = _MountAwareResolver()
    resolver._payloads[_NCD4] = _fragment(4, 1)
    resolver._payloads[_NCD5] = _fragment(5, 2)
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


def _mounted_version(*sub_graphs: str) -> Any:
    """The baseline version, pinning the given sub-graph refs."""
    base = _version()
    assert base.pins is not None
    pins = base.pins.model_copy(update={"sub_graphs": [_ref(r) for r in sub_graphs]})
    return base.model_copy(update={"pins": pins})


def _candidate_version(
    *, table: bool = False, extra_pins: tuple[str, ...] = (), sub_graphs: tuple[str, ...] = ()
) -> Any:
    base = _version()
    assert base.pins is not None
    tables = [_ref(_TABLE_2 if table else _TABLE_1), *(_ref(t) for t in extra_pins)]
    pins = Pins(
        rate_tables=tables,
        models=base.pins.models,
        reference_tables=base.pins.reference_tables,
        custom_objectives=base.pins.custom_objectives,
        sub_graphs=[_ref(r) for r in sub_graphs],
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
    base_sub_graphs: tuple[str, ...] = (),
    sub_graphs: tuple[str, ...] = (),
    base: dict[str, Any] | None = None,
) -> Any:
    resolver = resolver or _resolver(cand, base=base)
    return asyncio.run(
        attribute(
            _mounted_version(*base_sub_graphs),
            _candidate_version(table=table, extra_pins=extra_pins, sub_graphs=sub_graphs),
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
    # Two layers: compile now refuses a step that reads an undeclared name (FR-246, tested in
    # test_rating_declared_reads.py). This test proves the RUNTIME guard on its own, so the
    # declared-reads check alone is switched off here, test-only (the analogue of the
    # dislocation sibling's `_hand_compiled`); no production path gains a way around compile.
    from pricing_core.rating import compile as compile_module

    monkeypatch.setattr(
        compile_module,
        "ALGORITHM_CHECKS",
        tuple(
            c for c in compile_module.ALGORITHM_CHECKS if c.__name__ != "_check_declared_reads"
        ),
    )
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


def _harness() -> Any:
    """The measurement harness (`scripts/measure-attribution-cost.py`), loaded by path."""
    import importlib.util

    path = Path(__file__).resolve().parents[3] / "scripts" / "measure-attribution-cost.py"
    spec = importlib.util.spec_from_file_location("measure_attribution_cost", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.req("FR-1398")
def test_replay_that_differs_from_a_true_rerate_is_detected_and_recorded() -> None:
    """DP-S3-3 (b), Acceptance 18: replay is measured in the harness, never a production path.
    On a step-aligned set the replay equals every true re-rate; a replay with one operand off
    is reported as a mismatch naming the policy and the minor-unit difference."""
    h = _harness()
    fx = h.load_fixture()
    members = (1, 2, 4)  # age relativity, severity, minimum premium: three rungs
    assert h.step_aligned(fx, members)
    assert not h.step_aligned(fx, (0, 2))  # the model swap and severity feed one rung
    keys = {
        f: [
            int(r[f]) if f in h.INT_FACTORS else r[f]
            for r in fx.tables[f"rate_table:fremtpl2-rel-{f.replace('_', '-')}@1"]["rows"]
        ]
        for f in h.FACTORS_V1
    }
    rows = [
        {"quote_id": f"Q{i:03d}", "exposure_years": 1.0, "current_premium_minor": 10_000 + 3_000 * i}  # noqa: E501
        | {f: ks[(i * 7) % len(ks)] for f, ks in keys.items()}
        | {"veh_gas": "Regular", "veh_age_band": i % 6}
        for i in range(30)
    ]  # fmt: skip
    book = pl.DataFrame(rows, strict=False).lazy()
    columns = book.collect_schema().names()
    base, cand = h._pass(fx, members, book, columns)
    assert sum(v["minor"] is not None for v in base.values()) == 30  # every policy is quoted
    truth = {}
    for sub in ((), (1,), (2,), (4,), (1, 2), (1, 4), (2, 4), (1, 2, 4)):
        _b, rerated = h._pass(fx, sub, book, columns)
        truth[sub] = {q: v["minor"] for q, v in rerated.items()}
    # Linear subsets (no clamp member) and the whole set replay exactly.
    for sub in ((), (1,), (2,), (1, 2), (1, 2, 4)):
        assert h.compare_replay(h.replay_values(fx, sub, base, cand), truth[sub]) == []
    # A clamp whose binding depends on the mixed value is not replayed: the candidate ladder
    # records no clamp for a policy the full set lifts above the floor. The harness names the
    # policy and the minor-unit difference; this is the measured finding, not a failure of the run.
    diffs = h.compare_replay(h.replay_values(fx, (4,), base, cand), truth[(4,)])
    assert diffs, "the fixture book must include a policy the floor binds on in a mixed subset"
    assert all(q.startswith("Q") and d != 0 for q, d in diffs)
    quote, diff = diffs[0]
    assert truth[(4,)][quote] + diff == h.replay_values(fx, (4,), base, cand)[quote]
    # One operand off by one minor unit on one policy: named, with its difference.
    off = dict(h.replay_values(fx, (1, 2, 4), base, cand))
    off["Q007"] += 1
    assert h.compare_replay(off, truth[(1, 2, 4)]) == [("Q007", 1)]


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


# ---------------------------------------------------------------------------
# FD-1660 (WK-673, PL-1694 Stage A): attribution does not see sub-graph mounts, so it refuses.
# ---------------------------------------------------------------------------


class _MountSpy:
    """Records every subset compile `attribute` attempts: the sub-graph refs a compiled bundle
    resolved, and the text of a compile that failed."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.compiled: list[tuple[str, list[str]]] = []
        self.failed: list[tuple[str, str]] = []
        real = analysis.compile_bundle

        async def spy(version: Any, resolver: Any) -> Any:
            slug = version.algorithm_ref.slug
            try:
                bundle = await real(version, resolver)
            except ValueError as exc:
                self.failed.append((slug, safe_error_text(exc)))
                raise
            resolved = sorted(k for k in bundle.resolved_payloads if k.startswith("sub_graph:"))
            self.compiled.append((slug, resolved))
            return bundle

        monkeypatch.setattr(analysis, "compile_bundle", spy)

    @property
    def attempts(self) -> int:
        return len(self.compiled) + len(self.failed)


def _g1_run() -> Any:
    """The baseline mounts `m_ncd` at `@4`; the candidate re-points it to `@5` and edits the rate
    table. No groups."""
    cand = _candidate_payload(_e_mounted, _e_repoint, _e_table)
    return _run(
        cand,
        table=True,
        book=_mounted_book(),
        base=_mounted_base(),
        base_sub_graphs=(_NCD4,),
        sub_graphs=(_NCD5,),
    )


def _independent_total(version: Any, payload: dict[str, Any], slug: str) -> int:
    """The book's summed payable premium for one algorithm, scored without attribution."""
    book = _mounted_book()
    resolver = _resolver()
    ref = _ref(f"rating_algorithm:{slug}@1")
    resolver._payloads[str(ref)] = payload
    bundle = load_bundle(
        asyncio.run(compile_bundle(version.model_copy(update={"algorithm_ref": ref}), resolver))
    )
    rated = analysis._score_pass(bundle, book, book.collect_schema().names(), _spec(), ref)
    assert all(r["minor"] is not None for r in rated.values())
    return sum(int(r["minor"]) for r in rated.values())


def _g1_independent_effects() -> tuple[int, int, int, int]:
    """(total, ladder-only effect, table-only effect, interaction), each from its own bundle."""
    base = _independent_total(_mounted_version(_NCD4), _mounted_base(), "g1-base")
    repoint = copy.deepcopy(_mounted_base())
    _e_repoint(repoint)
    ladder = _independent_total(_mounted_version(_NCD5), repoint, "g1-ladder") - base
    table_only = copy.deepcopy(_mounted_base())
    _e_table(table_only)
    table_version = _candidate_version(table=True, sub_graphs=(_NCD4,))
    table = _independent_total(table_version, table_only, "g1-tbl") - base
    full = _candidate_payload(_e_mounted, _e_repoint, _e_table)
    full_version = _candidate_version(table=True, sub_graphs=(_NCD5,))
    total = _independent_total(full_version, full, "g1-full") - base
    return total, ladder, table, total - ladder - table


def _assert_refused(exc: AttributionError, *mount_points: str) -> None:
    """The guard's refusal: `VALIDATION_FAILED`, naming the finding, the slice that lifts it and
    each mount point (Acceptance 1)."""
    assert exc.code == "VALIDATION_FAILED"
    text = str(exc)
    for needle in ("sub-graph mount", "FD-1660", "SL-1696", *mount_points):
        assert needle in text, (needle, text)


@pytest.mark.req("FR-1399")
def test_guard_mount_difference_refuses_a_re_pointed_mount(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FD-1660 limb 3, after the guard: the re-point plus one table edit is refused naming `m_ncd`,
    before any subset compiles, instead of crediting the table edit with the ladder's effect."""
    spy = _MountSpy(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _g1_run()
    _assert_refused(exc.value, "m_ncd")
    assert "a mount differs" in str(exc.value)
    assert spy.attempts == 0


@pytest.mark.req("FR-1399")
def test_guard_fixture_has_a_non_zero_ladder_effect_that_attribution_would_misattribute() -> None:
    """The refusal in `_g1_run` is not for a vacuous fixture: scored without attribution, the
    re-point alone moves the book, and total = ladder + table + interaction (SL-1696 reads it)."""
    _total, ladder, table, _interaction = _g1_independent_effects()
    assert ladder != 0
    assert table != 0


def _g2_run() -> Any:
    """Baseline and candidate both mount `m_ncd` at `@4`; the candidate adds the rate-table and
    instalment edits (K = 2, no groups): no mount differs, but the baseline mounts."""
    cand = _candidate_payload(_e_mounted, _e_table, _e_instalment)
    return _run(
        cand,
        table=True,
        book=_mounted_book(),
        base=_mounted_base(),
        base_sub_graphs=(_NCD4,),
        sub_graphs=(_NCD4,),
    )


def _demo_shape_run(split: Callable[[list[Any]], list[tuple[str, list[str]]]]) -> Any:
    """The demo's shape: the baseline has no mount; the candidate mounts `m_ncd` with its consumer
    edited (`s_in_ncd` added, `s_office` consuming `ncd_factor`) and also edits `s_instalment`.
    `split` turns the derived changes into the declared groups."""
    cand = _candidate_payload(_e_mounted, _e_instalment)
    sub_graphs = (_NCD4,)
    changes = asyncio.run(
        derive_changes(_version(), _candidate_version(sub_graphs=sub_graphs), _resolver(cand))
    )
    return _run(cand, book=_mounted_book(), sub_graphs=sub_graphs, groups=split(changes))


def _one_group(changes: list[Any]) -> list[tuple[str, list[str]]]:
    return [("all", [c.id for c in changes])]


def _structure_and_instalment(changes: list[Any]) -> list[tuple[str, list[str]]]:
    instalment = [c.id for c in changes if "s_instalment" in c.description]
    return [
        ("structure", [c.id for c in changes if c.id not in instalment]),
        ("instalment", instalment),
    ]


@pytest.mark.req("FR-1399")
def test_guard_baseline_mount_k2_refuses_when_either_side_mounts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FD-1660 limb 2, after the guard: no mount differs, but the baseline mounts and K = 2, so the
    run is refused naming `m_ncd` before any compile (not as `BUNDLE_COMPILE_FAILED`)."""
    spy = _MountSpy(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _g2_run()
    _assert_refused(exc.value, "m_ncd")
    assert "a sub-graph is mounted and two or more groups are declared" in str(exc.value)
    assert spy.attempts == 0


@pytest.mark.req("FR-1399")
def test_guard_does_not_refuse_a_mounted_k1_run_with_an_unchanged_mount(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GUARD (green by design): baseline and candidate both mount `m_ncd` at `@4`, one edit, so
    K = 1 and no mount differs. The FD-1660 guard must not refuse it; it attributes normally."""
    spy = _MountSpy(monkeypatch)
    cand = _candidate_payload(_e_mounted, _e_instalment)
    result = _run(
        cand,
        book=_mounted_book(),
        base=_mounted_base(),
        base_sub_graphs=(_NCD4,),
        sub_graphs=(_NCD4,),
    )
    assert result is not None
    assert spy.attempts > 0


@pytest.mark.req("FR-1399")
def test_guard_one_group_refused_even_when_one_group_holds_every_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DP-G (exemption (i) refused): the demo-shaped candidate with one group holding every
    derived change is refused, not returned as one item equal to the total."""
    spy = _MountSpy(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _demo_shape_run(_one_group)
    _assert_refused(exc.value, "m_ncd")
    assert spy.attempts == 0


@pytest.mark.req("FR-1399")
def test_guard_mount_added_two_groups_refuses_before_any_compile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FD-1660 limb 1, after the guard: a mount added with two groups is refused naming `m_ncd`
    instead of failing as `BUNDLE_COMPILE_FAILED` in the `structure` subset."""
    spy = _MountSpy(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _demo_shape_run(_structure_and_instalment)
    _assert_refused(exc.value, "m_ncd")
    assert spy.attempts == 0


@pytest.mark.req("FR-1399")
@pytest.mark.req("NFR-499")
def test_guard_text_survives_safe_error_text() -> None:
    """Condition (a) (the 07:44:13 entry): the Job keeps `safe_error_text(exc)` of an
    `AttributionError`, so the guard's error is also a `CodedError` and its text reaches the Job."""
    with pytest.raises(AttributionError) as exc:
        _g1_run()
    kept = safe_error_text(exc.value)
    for needle in ("VALIDATION_FAILED", "FD-1660", "SL-1696", "m_ncd"):
        assert needle in kept, (needle, kept)
    assert isinstance(exc.value, CodedError)


# ---------------------------------------------------------------------------
# FD-1660 (WK-673, PL-1694 Stage B, SL-1696): a mount is derived like a step, a subset carries its
# mount changes and their pins, and a mount is a node for dependence (RL-1686 DP-1 to DP-3, T1, T2).
# Written red-first. The two derive tests (`test_mount_repoint_is_one_step_changed_change_naming_
# the_mount` and `test_mount_added_and_removed_are_step_added_and_step_removed`) are red by their
# own cause even on Stage A's head: `_derive` never reads a mount, and the guard is not on their
# path. The others are red at the guard (`VALIDATION_FAILED`, FD-1660); the bug's own cause is
# shown by running them against the base without the guard. Stage B flips the Stage A
# `test_guard_*` cases into these, so a `test_guard_*` case is removed only by that flip.
# ---------------------------------------------------------------------------

_M_NCD_REPOINT = f"m_ncd: mount {_NCD4} → {_NCD5}"


def _mount_changes(changes: list[Any]) -> list[Any]:
    return [c for c in changes if c.description.startswith("m_ncd:")]


def _by_description(changes: list[Any], needle: str) -> Any:
    (found,) = [c for c in changes if needle in c.description]
    return found


def _g1_changes() -> list[Any]:
    cand = _candidate_payload(_e_mounted, _e_repoint, _e_table)
    return asyncio.run(
        derive_changes(
            _mounted_version(_NCD4),
            _candidate_version(table=True, sub_graphs=(_NCD5,)),
            _resolver(cand, base=_mounted_base()),
        )
    )


class _BundleSpy:
    """Records, per subset `attribute` compiles, the compiled graph node ids and the
    `(rate_tables, sub_graphs)` pins the subset's version carries (DP-2)."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.nodes: list[set[str]] = []
        self.pins: list[tuple[list[str], list[str]]] = []
        real = analysis.compile_bundle

        async def spy(version: Any, resolver: Any) -> Any:
            bundle = await real(version, resolver)
            self.nodes.append(set(bundle.graph.nodes))
            assert version.pins is not None
            self.pins.append(
                (
                    [str(r) for r in version.pins.rate_tables],
                    [str(r) for r in version.pins.sub_graphs],
                )
            )
            return bundle

        monkeypatch.setattr(analysis, "compile_bundle", spy)


@pytest.mark.req("FR-1399")
def test_mount_repoint_is_one_step_changed_change_naming_the_mount() -> None:
    """R3 (T1), the derivation half: the re-point is exactly one `step_changed` change, described
    from its `mount_point` with both versions, and its sub-graph pin difference is part of it, not
    a separate `pin` change. (Red by its cause under the guard too: `_derive` skips mounts.)"""
    changes = _g1_changes()
    (mount,) = _mount_changes(changes)
    assert mount.kind == "step_changed"
    assert mount.description == _M_NCD_REPOINT
    assert [c for c in changes if c.kind == "pin"] == []
    # `m_ncd` sorts before `s_expense`, so the mount change is the first one.
    assert [c.kind for c in changes] == ["step_changed", "table_repointed"]
    assert changes[0] is mount


@pytest.mark.req("FR-1399")
def test_mount_added_and_removed_are_step_added_and_step_removed() -> None:
    """T1 / DP-1: added is `step_added` (`<mount_point>: mount added (<ref>)`), removed is
    `step_removed` (`<mount_point>: mount removed (<ref>)`); neither is `table_repointed`."""
    cand = _candidate_payload(_e_mounted)
    added = asyncio.run(
        derive_changes(
            _version(), _candidate_version(sub_graphs=(_NCD4,)), _resolver(cand, base=None)
        )
    )
    (m_added,) = _mount_changes(added)
    assert (m_added.kind, m_added.description) == ("step_added", f"m_ncd: mount added ({_NCD4})")
    removed = asyncio.run(
        derive_changes(
            _mounted_version(_NCD4),
            _candidate_version(),
            _resolver(_candidate_payload(), base=_mounted_base()),
        )
    )
    (m_removed,) = _mount_changes(removed)
    assert (m_removed.kind, m_removed.description) == (
        "step_removed",
        f"m_ncd: mount removed ({_NCD4})",
    )
    assert [c for c in added + removed if c.kind == "pin"] == []


@pytest.mark.req("FR-1399")
@pytest.mark.req("FR-266")
def test_mount_repoint_plus_table_edit_attributes_each_effect_to_its_own_change() -> None:
    """R3 (T1, T2), the numbers: the mount change's isolated part equals the independently computed
    ladder-only effect, the table change's the table-only effect, and the two Shapley parts split
    the interaction and sum to the total (FR-266)."""
    total, ladder, table, interaction = _g1_independent_effects()
    assert ladder != 0
    result = _g1_run()
    mount = _mount_changes(result.derived_changes)[0]
    other = _by_description(result.derived_changes, "s_expense")
    items = {i.group: i for i in result.attribution}
    assert items[mount.id].isolated_minor == ladder
    assert items[other.id].isolated_minor == table
    summary = result.attribution_summary
    assert summary.total_change_minor == total
    assert sum(i.shapley_minor for i in result.attribution) == total
    assert interaction != 0
    assert table != 0
    # A part is the sum over the book's policies of a largest-remainder allocation of each policy's
    # own split, so it is within half a minor unit of the exact value per policy (two parts: the
    # unit goes to the larger remainder), never within one unit overall.
    n_policies = _mounted_book().collect().height
    bound = Fraction(n_policies, 2)
    for change, isolated in ((mount, ladder), (other, table)):
        exact = Fraction(isolated) + Fraction(interaction, 2)
        part = items[change.id].shapley_minor
        assert abs(Fraction(part) - exact) <= bound, (part, exact, bound)


@pytest.mark.req("FR-1399")
@pytest.mark.req("FR-266")
def test_mount_added_two_groups_returns_and_reconciles() -> None:
    """R1 (T2): a mount added with its consumer in `structure` and an unrelated edit in
    `instalment` runs, by Shapley, and reconciles to the total."""
    result = _demo_shape_run(_structure_and_instalment)
    summary = result.attribution_summary
    assert summary.method == "shapley"
    items = {i.group: i for i in result.attribution}
    assert set(items) == {"structure", "instalment"}
    assert sum(i.shapley_minor for i in result.attribution) == summary.total_change_minor
    assert summary.residual_minor == summary.total_change_minor - sum(
        i.isolated_minor for i in result.attribution
    )
    structure = next(g for g in result.change_groups if g.name == "structure")
    assert _mount_changes([c for c in result.derived_changes if c.id in structure.changes])


@pytest.mark.req("FR-1398")
@pytest.mark.req("FR-266")
def test_baseline_mount_k2_every_subset_inlines_the_baselines_mount(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R2 (T2): both versions mount `@4`, the candidate adds two edits (K = 2). The run returns and
    reconciles, and each subset bundle inlines the baseline's mount (the node ids of
    `test_rating_compile_bundle.py`'s `m_ncd__s_ladder`) and resolved only `@4`."""
    spy = _MountSpy(monkeypatch)
    nodes = _BundleSpy(monkeypatch)
    result = _g2_run()
    assert spy.failed == []
    assert len(spy.compiled) == 4
    assert all(resolved == [_NCD4] for _, resolved in spy.compiled)
    assert all("m_ncd__s_ladder" in n for n in nodes.nodes)
    summary = result.attribution_summary
    assert sum(i.shapley_minor for i in result.attribution) == summary.total_change_minor


@pytest.mark.req("FR-1399")
def test_mount_and_its_consumer_ungrouped_is_refused_naming_the_pair(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R4 (DP-3): the mount change and the step that consumes its output in different groups is
    refused as a dependent pair before any compile, with the dependence text, not the guard's."""
    cand = _candidate_payload(_e_mounted, _e_instalment)
    sub_graphs = (_NCD4,)
    changes = asyncio.run(
        derive_changes(_version(), _candidate_version(sub_graphs=sub_graphs), _resolver(cand))
    )
    mount = _mount_changes(changes)[0]
    producer = _by_description(changes, "s_in_ncd")
    consumer = _by_description(changes, "s_office")
    instalment = _by_description(changes, "s_instalment")
    groups = [("mount", [mount.id, producer.id]), ("rest", [consumer.id, instalment.id])]
    spy = _MountSpy(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _run(cand, book=_mounted_book(), sub_graphs=sub_graphs, groups=groups)
    text = str(exc.value)
    assert exc.value.code == "VALIDATION_FAILED"
    assert "dependent changes must share a group" in text
    assert f"({consumer.id}, {mount.id})" in text
    assert "FD-1660" not in text
    assert spy.attempts == 0


@pytest.mark.req("FR-1399")
def test_one_group_holding_every_change_returns_one_item_equal_to_the_total() -> None:
    """Acceptance 15 (G3 flipped): the one-group run returns one item equal to the total, and the
    group's members include the mount change (the label is right)."""
    result = _demo_shape_run(_one_group)
    (item,) = result.attribution
    assert item.shapley_minor == result.attribution_summary.total_change_minor
    (group,) = result.change_groups
    assert _mount_changes([c for c in result.derived_changes if c.id in group.changes])


@pytest.mark.req("FR-1398")
def test_mounted_empty_and_full_subsets_hash_equal_baseline_and_candidate() -> None:
    """Acceptance 17: with a mounted candidate the subset of no changes hashes to the baseline's
    bundle and the subset of every change to the candidate's."""
    cand = _candidate_payload(_e_mounted, _e_instalment)
    result = _demo_shape_run(_structure_and_instalment)
    resolver = _resolver(cand)
    base_hash = asyncio.run(compile_bundle(_version(), resolver)).content_hash
    cand_hash = asyncio.run(
        compile_bundle(_candidate_version(sub_graphs=(_NCD4,)), resolver)
    ).content_hash
    hashes = result.attribution_summary.subset_bundle_hashes
    assert base_hash in hashes
    assert cand_hash in hashes
    assert base_hash != cand_hash
    assert len(set(hashes)) == 4


@pytest.mark.req("FR-1399")
def test_mount_ports_re_mapped_forms() -> None:
    """DP-1 (T1): a re-map alone is `<mount_point>: mount ports re-mapped (<ref>)`; a re-point with
    a re-map is the re-point form plus `; ports re-mapped`. Both are one `step_changed`."""

    def remap(alg: dict[str, Any]) -> None:
        alg["sub_graphs"][0]["outputs"] = {"ncd_factor": "ncd_f2"}
        office = _step(alg, "s_office")
        office["expr"] = "risk_premium_minor * expense_factor * ncd_f2"
        office["consumes"] = ["risk_premium_minor", "expense_factor", "ncd_f2"]

    def derived(*edits: Callable[[dict[str, Any]], None], sub_graphs: tuple[str, ...]) -> Any:
        cand = _candidate_payload(_e_mounted, *edits)
        changes = asyncio.run(
            derive_changes(
                _mounted_version(_NCD4),
                _candidate_version(sub_graphs=sub_graphs),
                _resolver(cand, base=_mounted_base()),
            )
        )
        (mount,) = _mount_changes(changes)
        return mount

    ports_only = derived(remap, sub_graphs=(_NCD4,))
    assert ports_only.kind == "step_changed"
    assert ports_only.description == f"m_ncd: mount ports re-mapped ({_NCD4})"
    both = derived(_e_repoint, remap, sub_graphs=(_NCD5,))
    assert both.kind == "step_changed"
    assert both.description == f"{_M_NCD_REPOINT}; ports re-mapped"


@pytest.mark.req("FR-1398")
def test_each_subset_pins_only_the_sub_graphs_of_the_mounts_it_holds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DP-2: the mount-only subset pins `@5` only, the table-only subset `@4` only (neither carries
    the other's version), and the empty and full subsets are the baseline's and the candidate's."""
    nodes = _BundleSpy(monkeypatch)
    _g1_run()
    assert sorted(nodes.pins) == sorted(
        [
            ([_TABLE_1], [_NCD4]),  # empty subset: the baseline
            ([_TABLE_1], [_NCD5]),  # the mount change alone
            ([_TABLE_2], [_NCD4]),  # the table change alone
            ([_TABLE_2], [_NCD5]),  # every change: the candidate
        ]
    )


@pytest.mark.req("FR-1399")
def test_mount_alone_in_a_group_without_its_input_step_is_refused_naming_the_pair(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DP-3, the reverse direction: the mount alone in one group while `s_in_ncd`, which produces
    the parent value the mount's `inputs` map, sits in another is refused as a dependent pair
    (the mount first: it depends on `s_in_ncd`), before any compile."""
    cand = _candidate_payload(_e_mounted, _e_instalment)
    sub_graphs = (_NCD4,)
    changes = asyncio.run(
        derive_changes(_version(), _candidate_version(sub_graphs=sub_graphs), _resolver(cand))
    )
    mount = _mount_changes(changes)[0]
    producer = _by_description(changes, "s_in_ncd")
    groups = [
        ("mount", [mount.id]),
        ("rest", [c.id for c in changes if c.id != mount.id]),
    ]
    spy = _MountSpy(monkeypatch)
    with pytest.raises(AttributionError) as exc:
        _run(cand, book=_mounted_book(), sub_graphs=sub_graphs, groups=groups)
    text = str(exc.value)
    assert exc.value.code == "VALIDATION_FAILED"
    assert "dependent changes must share a group" in text
    assert f"({mount.id}, {producer.id})" in text
    assert "FD-1660" not in text
    assert spy.attempts == 0


@pytest.mark.req("FR-1398")
@pytest.mark.req("FR-266")
def test_mount_removed_two_groups_returns_and_reconciles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`_merged`'s removal path: the baseline mounts `@5`, the candidate drops the mount (with its
    input step and consumer edit, in `structure`) and edits `s_instalment` (K = 2). The run
    reconciles to the independently scored total, the removal carries a non-zero effect, and a
    subset pins `@5` exactly while its mount is not removed."""
    base_payload = copy.deepcopy(_mounted_base())
    _e_repoint(base_payload)
    cand = _candidate_payload(_e_instalment)
    changes = asyncio.run(
        derive_changes(
            _mounted_version(_NCD5), _candidate_version(), _resolver(cand, base=base_payload)
        )
    )
    (removed,) = _mount_changes(changes)
    assert removed.kind == "step_removed"
    instalment = [c.id for c in changes if "s_instalment" in c.description]
    groups = [
        ("structure", [c.id for c in changes if c.id not in instalment]),
        ("instalment", instalment),
    ]
    nodes = _BundleSpy(monkeypatch)
    result = _run(
        cand,
        book=_mounted_book(),
        base=base_payload,
        base_sub_graphs=(_NCD5,),
        groups=groups,
    )
    summary = result.attribution_summary
    base = _independent_total(_mounted_version(_NCD5), base_payload, "rm-base")
    full = _independent_total(_candidate_version(), cand, "rm-full")
    assert summary.method == "shapley"
    assert summary.total_change_minor == full - base != 0
    assert {i.group for i in result.attribution} == {"structure", "instalment"}
    assert sum(i.shapley_minor for i in result.attribution) == summary.total_change_minor
    structure = next(g for g in result.change_groups if g.name == "structure")
    assert removed.id in structure.changes
    items = {i.group: i for i in result.attribution}
    assert items["structure"].isolated_minor != 0
    pins = sorted(p[1] for p in nodes.pins)
    assert pins == sorted([[_NCD5], [_NCD5], [], []])


@pytest.mark.req("FR-1399")
def test_guard_three_edit_change_list_is_unchanged_without_a_mount() -> None:
    """GUARD (item 16, green on Stage A's head and after Stage B): a candidate with no mount on
    either side derives exactly the lists below, so the mount work does not move a no-mount run."""
    changes = _derive(_candidate_payload(*_THREE), table=True)
    table = "rate_table_ref rate_table:motor-expense@1 → rate_table:motor-expense@2"
    instalment = "expr office_premium_minor * 1.05 → office_premium_minor * 1.10"
    office = "expr risk_premium_minor * expense_factor → risk_premium_minor * expense_factor + 500"
    assert [(c.id, c.kind, c.description) for c in changes] == [
        ("c1", "table_repointed", f"s_expense: {table}"),
        ("c2", "step_changed", f"s_instalment: {instalment}"),
        ("c3", "step_changed", f"s_office: {office}"),
    ]
