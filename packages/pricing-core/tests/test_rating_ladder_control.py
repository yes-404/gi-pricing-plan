"""The false-positive control and the golden-rung stop predicate (`RL-1329` Acceptance 8, D1/D2).

For every quote of the corpus below the ruled builder is compared with `origin/main`'s builder
(`baseline_ladder.py`) on the same engine result. The stop predicate is evaluated in integers
and `Decimal`, never float:

- (a) a rung of the baseline ladder moved by more than its bound. On a baseline `multiply` rung
  `5e-5 * |base_{i-1}| + e_apply + e_ruled`; on an `add`, a `round`, the first rung and a rung
  that is `none` in the baseline `e_apply + e_ruled`; on a `constraints` rung where a clamp
  binds the new value must be exactly the bound. `e` is 0.5 for a `half_*` mode, 1 otherwise.
- (b) `5e-5 * |base_{i-1}| / |new_i|` above `2e-4` (report to the maintainer, never continue);
- (c) a payable that changed (stops the slice, report to the lead);
- a quote on which a clamp's comparison and disposition disagree, and any refusal at all.

The corpus is the golden-quote analogue of every committed scoring fixture and suite: the score
fixture over a grid of contexts (clamp binding and not), the demo suite's golden quote, and the
RL-1329 sweep configurations at every decade. The test prints its counts (run with `-s`) and
fails on any exceedance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from itertools import product
from typing import Any

import pytest
from baseline_ladder import _build_ladder as baseline_build_ladder
from test_rating_ladder_exact import (
    _CLAMP_INPUTS,
    _chain_algorithm,
    _compile_payload,
    _score_fixture,
)
from test_rating_ladder_sweep import _config, _quotes

from model_schema.scoring import LadderRung
from pricing_core.rating import score as score_module
from pricing_core.rating.ladder import LadderInputs, ladder_violations, round_once
from pricing_core.rating.runtime import CompiledBundle

_FIVE_E5 = Decimal("0.00005")
_REPORT_LINE = Decimal("0.0002")
_HALF = Decimal("0.5")


def _e(mode: str | None) -> Decimal:
    """A rounding's largest error: 0.5 for a `half_*` mode, 1 for `ceiling`, `floor`, `down`."""
    return _HALF if (mode or "half_even").startswith("half_") else Decimal(1)


@dataclass
class Report:
    quotes: int = 0
    rungs: int = 0
    exceedances: list[str] = field(default_factory=list)
    report_line_hits: list[str] = field(default_factory=list)
    payable_changes: list[str] = field(default_factory=list)
    disposition_disagreements: list[str] = field(default_factory=list)
    refusals: list[str] = field(default_factory=list)
    none_rungs: int = 0
    #: the rung before `constraints` on a quote where a clamp binds: FD-1330's correction
    #: (today it carries the post-clamp value, 5000; ruled, the pre-clamp 1436), which is not
    #: the 4 dp drift the exact bound derives from, so it is counted apart, never folded in.
    clamp_pre_rungs: int = 0
    directed_modes: dict[str, int] = field(default_factory=dict)
    modes_seen: set[str] = field(default_factory=set)
    max_tightness: dict[str, Decimal] = field(default_factory=dict)
    max_ratio: Decimal = Decimal(0)

    def summary(self) -> str:
        tight = {k: f"{v:.4f}" for k, v in sorted(self.max_tightness.items())}
        return (
            f"quotes={self.quotes} rungs={self.rungs} exceedances={len(self.exceedances)} "
            f"payable_changes={len(self.payable_changes)} "
            f"disposition_disagreements={len(self.disposition_disagreements)} "
            f"refusals={len(self.refusals)} baseline_none_rungs={self.none_rungs} "
            f"clamp_pre_rungs_excluded={self.clamp_pre_rungs} "
            f"report_line_hits={len(self.report_line_hits)} max_ratio={self.max_ratio:.3e} "
            f"max_tightness_by_kind={tight} directed_mode_rungs={self.directed_modes} "
            f"declared_and_applied_modes={sorted(self.modes_seen)}"
        )


def compare_quote(
    report: Report,
    where: str,
    base: list[LadderRung],
    new: list[LadderRung],
    exact: tuple[LadderInputs, dict[str, Any]] | None = None,
) -> None:
    """Evaluate the stop predicate for one quote (`base` is the baseline ladder)."""
    report.quotes += 1
    if base[-1].value_minor != new[-1].value_minor:
        report.payable_changes.append(f"{where}: {base[-1].value_minor} -> {new[-1].value_minor}")
    by_new = {r.rung: r for r in new}
    clamp_pre: str | None = None
    for position, rung in enumerate(new):
        if rung.operation is not None and rung.operation.kind == "clamp" and position > 0:
            clamp_pre = new[position - 1].rung
    for index, b in enumerate(base):
        n = by_new.get(b.rung)
        if n is None:
            report.exceedances.append(f"{where}: rung {b.rung} missing from the ruled ladder")
            continue
        report.rungs += 1
        if b.operation is not None and b.operation.kind == "none":
            report.none_rungs += 1
        if b.rung == clamp_pre:
            # Dispatch Delta 2 (1): by design the rung before `constraints` carries the
            # pre-clamp value, so it is outside the drift predicate and checked exactly.
            report.clamp_pre_rungs += 1
            if exact is not None:
                inputs, outputs = exact
                pre = inputs.exact[b.rung]
                # (a) the exact pre-clamp value, rounded once
                if n.unrounded_minor != pre or n.value_minor != round_once(pre, n.rounding):  # type: ignore[arg-type]
                    report.exceedances.append(f"{where}: clamp pre-rung {b.rung} (a)")
                # (c) the served declared output is still the post-clamp bound (C2)
                served = outputs.get(f"{b.rung}_minor")
                if served is not None and served != by_new["constraints"].value_minor:
                    report.exceedances.append(f"{where}: clamp pre-rung {b.rung} output (c)")
            continue
        if b.rung == "constraints" and not (n.operation and n.operation.kind == "clamp"):
            # Dispatch Delta 2 (2): an inheriting rung is checked by exact inheritance.
            before_new = new[[r.rung for r in new].index("constraints") - 1]
            if base[index].value_minor != base[index - 1].value_minor or not (
                n.value_minor == before_new.value_minor
                and n.unrounded_minor == before_new.unrounded_minor
            ):
                report.exceedances.append(f"{where}: constraints does not inherit exactly")
            continue
        source = index
        kind = "first" if source == 0 else (base[source].operation or b.operation).kind  # type: ignore[union-attr]
        diff = abs(Decimal(b.value_minor) - Decimal(n.value_minor))
        applied_mode = b.operation.mode if b.operation and b.operation.mode else None
        ruled_mode = n.rounding.mode if n.rounding else None
        for mode in (applied_mode, ruled_mode):
            if mode is not None:
                report.modes_seen.add(mode)
                if not mode.startswith("half_"):
                    report.directed_modes[mode] = report.directed_modes.get(mode, 0) + 1
        slack = _e(applied_mode or ruled_mode) + _e(ruled_mode)
        if n.operation is not None and n.operation.kind == "clamp":
            # (b) `constraints` is exactly the bound, with the clamp kind and the bound's value
            if (
                n.unrounded_minor != n.operation.bound_unrounded_minor
                or n.operation.bound not in ("min", "max")
            ):
                report.exceedances.append(f"{where}: clamp rung {b.rung} is not exactly the bound")
            continue
        if kind == "multiply" and source > 0:
            prev = abs(Decimal(base[source - 1].value_minor))
            bound = _FIVE_E5 * prev + slack
            if diff > bound:
                report.exceedances.append(f"{where}: {b.rung} diff {diff} > {bound}")
            if prev:
                tight = (diff - slack) / (_FIVE_E5 * prev)
                if tight > report.max_tightness.get("multiply", Decimal("-Infinity")):
                    report.max_tightness["multiply"] = tight
                if n.value_minor:
                    ratio = _FIVE_E5 * prev / abs(Decimal(n.value_minor))
                    report.max_ratio = max(report.max_ratio, ratio)
                    if ratio > _REPORT_LINE:
                        report.report_line_hits.append(f"{where}: {b.rung} ratio {ratio}")
        elif diff > slack:
            report.exceedances.append(f"{where}: {b.rung} ({kind}) diff {diff} > {slack}")


async def _both(
    bundle: CompiledBundle, context: dict[str, Any]
) -> tuple[list[LadderRung], list[LadderRung], list[str], tuple[LadderInputs, dict[str, Any]]]:
    """`(baseline ladder, ruled ladder, violations, (inputs, served outputs))` for one result."""
    result = bundle.decision.evaluate(context)["result"]
    _, codes = score_module._apply_constraints(bundle.algorithm, result)
    base, _ = baseline_build_ladder(bundle.algorithm, result, codes)
    inputs = score_module._ladder_inputs(bundle.algorithm, result, codes)
    new = score_module._build_ladder(inputs, codes)
    outputs = score_module._build_outputs(bundle.algorithm, result)
    return base, new, ladder_violations(new, inputs), (inputs, outputs)


def _file(report: Report, where: str, violations: list[str]) -> None:
    if violations:
        report.refusals.append(f"{where}: {violations}")
        if any("disagree" in v for v in violations):
            report.disposition_disagreements.append(where)


def _context(**inputs: Any) -> dict[str, Any]:
    return {"effective_date": "2026-09-01", "purpose": "new_business", **inputs}


async def _corpus() -> Report:
    report = Report()

    # 1. the score fixture over a grid of contexts: the clamp binds on some, not on others
    bundle = await _compile_payload(_score_fixture(outputs=("office_premium_minor",)))
    for age, channel, minimum in product(range(17, 100, 6), ("direct", "broker"), (0, 5000, 10**6)):
        inputs = {**_CLAMP_INPUTS, "driver_age": age, "channel": channel,
                  "min_premium_minor": minimum}
        where = f"score-fixture age={age} channel={channel} min={minimum}"
        base, new, violations, exact = await _both(bundle, _context(**inputs))
        _file(report, where, violations)
        compare_quote(report, where, base, new, exact)

    # 2. the demo suite's golden quote (`examples/fremtpl2/model.py`): a payable-only ladder
    demo = {
        "slug": "score-fixture", "version": 1,
        "input_contract": [{"name": "premium_in", "type": "int", "nullable": False,
                            "min": 0, "max": 1_000_000}],
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": [
            {"step_id": "s_in", "type": "input", "label": "in", "input_name": "premium_in",
             "on_missing": "error", "produces": "premium_in"},
            {"step_id": "s_expr", "type": "expression", "label": "x2", "expr": "premium_in * 2",
             "result_type": "money_minor", "consumes": ["premium_in"], "produces": "payable"},
            {"step_id": "s_out", "type": "output", "label": "payable",
             "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
             "consumes": ["payable"]},
        ],
        "sub_graphs": [],
    }
    demo_bundle = await _compile_payload(demo)
    for premium_in in (0, 1, 1234, 999_999):
        where = f"demo-suite premium_in={premium_in}"
        base, new, violations, exact = await _both(demo_bundle, _context(premium_in=premium_in))
        _file(report, where, violations)
        compare_quote(report, where, base, new, exact)

    # 3. the RL-1329 sweep configurations, at every decade, two seeds
    configs = (*(("plain", k) for k in range(7)), ("grossup", 3), ("add", 3), ("mixed", 4))
    for kind, count in configs:
        factors, _ = _config(kind, count)
        sweep_bundle = await _compile_payload(_chain_algorithm(factors=factors))
        for seed, decade in product((20260930, 7), (3, 4, 5, 6, 7)):
            for risk in _quotes(seed, decade, 12):
                where = f"sweep {kind}/{count} seed={seed} decade={decade} risk={risk!r}"
                context = _context(risk_premium_minor=risk)
                base, new, violations, exact = await _both(sweep_bundle, context)
                _file(report, where, violations)
                compare_quote(report, where, base, new, exact)
    return report


@pytest.mark.req("NFR-496")
async def test_the_false_positive_control_and_the_golden_rung_stop_predicate() -> None:
    report = await _corpus()
    print("\nLADDER CONTROL:", report.summary())
    assert report.quotes > 0
    assert report.refusals == [], report.refusals[:3]
    assert report.disposition_disagreements == []
    assert report.payable_changes == [], report.payable_changes[:3]
    assert report.report_line_hits == [], report.report_line_hits[:3]
    assert report.exceedances == [], report.exceedances[:3]


@pytest.mark.req("NFR-496")
async def test_the_control_fails_when_one_baseline_rung_is_shifted_to_its_bound_plus_one() -> None:
    """Red on broken input: the shifted rung is named, and the count is non-zero."""
    bundle = await _compile_payload(_chain_algorithm(factors=[
        ("expense_loading", "{prev} * 1.15", "half_even"),
        ("office_premium", "{prev} * 1.131", "half_even"),
    ]))
    base, new, _, _exact = await _both(bundle, _context(risk_premium_minor=61234.5))
    clean = Report()
    compare_quote(clean, "q", base, new)
    assert clean.exceedances == []

    prev = abs(Decimal(base[0].value_minor))
    bound = _FIVE_E5 * prev + Decimal(1)  # multiply rung: half and half
    shifted = [r.model_copy() for r in base]
    # one unit past the bound, from the ruled value (an integer shift never lands on the bound)
    shifted[1] = shifted[1].model_copy(
        update={"value_minor": new[1].value_minor + int(bound) + 1}
    )
    broken = Report()
    compare_quote(broken, "q", shifted, new)
    assert len(broken.exceedances) == 1
    assert "expense_loading" in broken.exceedances[0]


@pytest.mark.req("NFR-496")
async def test_the_exact_clamp_and_inheritance_checks_fail_on_broken_input() -> None:
    """Dispatch Delta 2: each exact check is red when its own object is broken."""
    bundle = await _compile_payload(_score_fixture(outputs=("office_premium_minor",)))
    inputs = {**_CLAMP_INPUTS, "min_premium_minor": 5000}
    base, new, _, exact = await _both(bundle, _context(**inputs))
    clean = Report()
    compare_quote(clean, "q", base, new, exact)
    assert clean.exceedances == []
    assert clean.clamp_pre_rungs == 1

    names = [r.rung for r in new]
    pre, con = names.index("office_premium"), names.index("constraints")
    # (a) the pre-clamp rung carries the clamped value instead of the exact pre-clamp one
    broken_pre = list(new)
    broken_pre[pre] = new[pre].model_copy(update={"value_minor": new[con].value_minor})
    report = Report()
    compare_quote(report, "q", base, broken_pre, exact)
    assert any("(a)" in e for e in report.exceedances)
    # (b) `constraints` is not the bound
    broken_con = list(new)
    broken_con[con] = new[con].model_copy(update={"unrounded_minor": Decimal("4999.5")})
    report = Report()
    compare_quote(report, "q", base, broken_con, exact)
    assert any("not exactly the bound" in e for e in report.exceedances)
    # (c) the served output is the pre-clamp value
    served = (exact[0], {**exact[1], "office_premium_minor": new[pre].value_minor})
    report = Report()
    compare_quote(report, "q", base, new, served)
    assert any("(c)" in e for e in report.exceedances)

    # inheritance: an unclamped quote whose `constraints` rung is one unit off its predecessor
    free_base, free_new, _, free_exact = await _both(
        bundle, _context(**{**_CLAMP_INPUTS, "min_premium_minor": 0})
    )
    c = [r.rung for r in free_new].index("constraints")
    off = list(free_new)
    off[c] = free_new[c].model_copy(update={"value_minor": free_new[c].value_minor + 1})
    report = Report()
    compare_quote(report, "q", free_base, off, free_exact)
    assert any("inherit" in e for e in report.exceedances)
