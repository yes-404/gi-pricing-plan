"""The freMTPL2 demo's rating algorithm, priced from the approved GLM (PL-1525, FR-230, FR-237).

One builder defines the algorithm: the seed saves what it returns and exit-demo slice (b)'s
journey imports it, so the demo never carries two freMTPL2 algorithms that disagree
(`CLAUDE.md` §2: a shape defined twice diverges, and in a pricing platform that is a mispricing).

The algorithm multiplies a base premium by one seeded relativity per Factor and rounds once to
the penny (FR-226). **The base premium is a simplification (frequency GLM x mean severity; no
severity model)** (DP-a2): `exp(intercept)` of the frequency GLM times the mean claim cost of
freMTPL2sev. Nobody should read it as a modelled pure premium.

The engine has no banding step and matches table keys exactly (`pricing_core.rating.runtime`),
so each banded Factor's raw value becomes its band label through one `expression` step, a chain
of ZEN ternaries generated here from the Banding's own boundaries and labels. That is the only
logic in this module; `test_fremtpl2_algorithm.py` holds it against `apply_banding` on every edge.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Any, Final

from model_schema import (
    AboveRangePolicy,
    ArtifactRef,
    Banding,
    BelowRangePolicy,
    Coefficient,
    RelativityLevel,
)

#: VR-ACT-2's bound. An annual motor policy cannot be on risk for two years.
MAX_EXPOSURE: Final = 1.05

#: The smallest exposure the cleaned training sample keeps (1/366 of a year: one day), the lower
#: end of the model's training domain (SL-1543 (A)). A string, so the declared bound is exact
#: rather than a float's repr. **Measured, not derived**, 2026-10-17:
#: `build_csv(PORTFOLIO_ROWS)` over the sha256-pinned book, then the minimum of `Exposure`
#: among the rows with `Exposure <= MAX_EXPOSURE` (19 985 rows) = 0.00273224043715847.
MIN_EXPOSURE: Final = "0.00273224043715847"

FREMTPL2_ALGORITHM_SLUG: Final = "fremtpl2-rate"

#: The eighth raw input: freMTPL2's `BonusMalus`. A rating-table input and not a model feature,
#: so no step of this algorithm consumes it (PL-1525 Pre-mint note 4); the journey's `ncd-ladder`
#: sub-graph keys on it. The range is freMTPL2's own (50 to 230).
BONUS_MALUS: Final = "bonus_malus"
BONUS_MALUS_RANGE: Final = (50, 230)

#: DP-a2's ruled label. It opens the base step's note and the algorithm's change note.
#: B4's input and second output (PL-1542 Task 3): the frequency GLM's offset column, and the raw
#: Peril Structure value beside the payable premium (FR-214, FR-249).
EXPOSURE: Final = "exposure_years"
STRUCTURE_PREMIUM: Final = "peril_structure_premium"

BASE_LABEL: Final = "a simplification (frequency GLM \u00d7 mean severity; no severity model)"


def _number(value: float) -> str:
    """A boundary as ZEN source: an integer when it is one, else the shortest exact float."""
    return str(int(value)) if float(value).is_integer() else repr(float(value))


def _quote(label: str) -> str:
    if "'" in label or "\\" in label:
        raise ValueError(
            f"band label {label!r} holds a quote or a backslash; a label is a ZEN string "
            "literal here and cannot be escaped"
        )
    return f"'{label}'"


def band_expression(column: str, banding: Banding) -> str:
    """The ZEN ternary chain mapping `column`'s raw value to the Banding's band label.

    Honours `closed` (`left`: a value on a boundary joins the band above it; `right`: the band
    below it) and the label order. Out of range, it follows the Banding's own policies
    (`apply_banding`): `null_level` sends the value to that level, `clamp_*` to the end band,
    and under `error` the algorithm's input contract refuses the value before this runs.
    """
    interior = banding.boundaries[1:-1]
    op = "<" if banding.closed == "left" else "<="
    chain = _quote(banding.labels[-1])
    for upper, label in reversed(list(zip(interior, banding.labels[:-1], strict=True))):
        chain = f"{column} {op} {_number(upper)} ? {_quote(label)} : ({chain})"
    first, last = banding.boundaries[0], banding.boundaries[-1]
    if banding.above_range is AboveRangePolicy.NULL_LEVEL:
        chain = f"{column} > {_number(last)} ? {_null_level(banding)} : ({chain})"
    if banding.below_range is BelowRangePolicy.NULL_LEVEL:
        chain = f"{column} < {_number(first)} ? {_null_level(banding)} : ({chain})"
    return chain


def _null_level(banding: Banding) -> str:
    if banding.null_level is None:
        raise ValueError(
            f"banding {banding.slug!r} sends out-of-range values to its null level and "
            "declares none"
        )
    return _quote(banding.null_level)


def mean_claim_cost_minor(amounts: Sequence[int | None], claim_counts: Sequence[int]) -> Decimal:
    """Σ amount ÷ Σ claim_count over the policies whose amount is KNOWN (FR-111, SL-1543).

    A `None` amount is a claimant with no severity record: unknown, not nil. Its claims are
    left out of the denominator as its amount is out of the numerator, so an unknown amount
    cannot pull the mean down.
    """
    known = [(a, n) for a, n in zip(amounts, claim_counts, strict=True) if a is not None]
    return Decimal(sum(a for a, _ in known)) / Decimal(sum(n for _, n in known))


def base_premium_minor(intercept: Decimal, mean_claim_minor: Decimal) -> int:
    """`exp(intercept) x mean claim cost`, in Decimal, half-even to whole minor units (DP-a2)."""
    return int((intercept.exp() * mean_claim_minor).quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


def glm_premium_minor(
    coefficients: Sequence[Coefficient],
    relativities: Mapping[str, Sequence[RelativityLevel]],
    base_minor: int,
    levels: Mapping[str, str],
) -> int:
    """The premium the fitted GLM gives a quote, independent of the seeded tables and of the
    scored bundle (PL-1525 Acceptance 3): `base x Π exp(β_level)`, in Decimal from the
    coefficients, half-even to a whole minor unit. A Factor at its base level contributes 1.

    Refuses a level that is neither the base nor a fitted coefficient, so a mistyped level cannot
    quietly price as the base.
    """
    estimates = {c.term: Decimal(str(c.estimate)) for c in coefficients}
    total = Decimal(0)
    for factor, level in levels.items():
        entry = next((r for r in relativities[factor] if r.level == level), None)
        if entry is None:
            raise ValueError(f"factor {factor!r} has no level {level!r} in the fit")
        if not entry.is_base:
            total += estimates[f"{factor}[{level}]"]
    return int((Decimal(base_minor) * total.exp()).quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


def _glm_mean(
    coefficients: Sequence[Coefficient],
    relativities: Mapping[str, Sequence[RelativityLevel]],
    levels: Mapping[str, str],
) -> Decimal:
    """`exp(intercept + Σ β)` for a quote on `levels`, in Decimal. A base level adds nothing."""
    estimates = {c.term: Decimal(str(c.estimate)) for c in coefficients}
    total = estimates["intercept"]
    for factor, level in levels.items():
        entry = next((r for r in relativities[factor] if r.level == level), None)
        if entry is None:
            raise ValueError(f"factor {factor!r} has no level {level!r} in the fit")
        if not entry.is_base:
            total += estimates[f"{factor}[{level}]"]
    return total.exp()


def structure_premium_minor(
    frequency: tuple[Sequence[Coefficient], Mapping[str, Sequence[RelativityLevel]]],
    severity: tuple[Sequence[Coefficient], Mapping[str, Sequence[RelativityLevel]]],
    levels: Mapping[str, str],
    exposure: Decimal = Decimal(1),
) -> int:
    """The AD Peril Structure's premium for a quote (B4, PL-1542 Task 4): frequency x severity,
    from each fit's own coefficients and never from the scored bundle (PL-1525 Acceptance 3).

    The frequency is an expected count for `exposure` years (its offset is `log(exposure)`),
    the severity is minor units per claim, and the DP-A4-3 large-loss treatment is `none`, so
    nothing is restored. Half-even to a whole minor unit, once.
    """
    cost = (
        _glm_mean(*frequency, levels) * exposure * _glm_mean(*severity, levels)
    )
    return int(cost.quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


def build_fremtpl2_algorithm(
    *,
    tables: Mapping[str, ArtifactRef],
    bandings: Mapping[str, Banding],
    base_minor: int,
    domains: Mapping[str, Sequence[str]],
    version: int = 1,
    peril_structure_ref: ArtifactRef | None = None,
    origin_tables: Mapping[str, ArtifactRef] | None = None,
) -> dict[str, Any]:
    """The algorithm payload, in the order of `tables` (one seeded table per Factor).

    `tables` maps each Factor slug to its seeded Rate Table ref. `bandings` maps each banded
    Factor slug to its Banding (its `column` is the raw input). `domains` maps each
    categorical Factor slug (which is also its column) to the levels the table holds.

    With `peril_structure_ref` the price is B4's (`WF-699`, PL-1542 DP-A4-1 (B), mechanism B1,
    `RL-1538`): the Peril Structure's risk premium for the quote, times Π(pinned cell ÷
    seed-origin cell) over the Factors. `origin_tables` maps each Factor slug to its table's
    seed-origin version (03 §4.2: the lowest-numbered version whose `seeded_from` equals the
    pinned version's); it defaults to `tables`, an unedited seed, whose ratio is exactly 1.
    `base_minor` is not read then: the structure replaces the base premium.
    """
    inputs: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []
    for factor in tables:
        banding = bandings.get(factor)
        column = banding.column if banding is not None else factor
        if banding is not None:
            low, high = math.ceil(banding.boundaries[0]), math.floor(banding.boundaries[-1])
            inputs.append({"name": column, "type": "int", "nullable": False,
                           "min": low, "max": high})
        else:
            inputs.append({"name": column, "type": "enum", "nullable": False,
                           "domain": list(domains[factor])})
        steps.append({"step_id": f"s_in_{column}", "type": "input", "label": column,
                      "input_name": column, "on_missing": "error", "produces": column})
    inputs.append({"name": BONUS_MALUS, "type": "int", "nullable": False,
                   "min": BONUS_MALUS_RANGE[0], "max": BONUS_MALUS_RANGE[1],
                   "description": "non-modelled: a rating-table input, not a model feature"})
    steps.append({"step_id": f"s_in_{BONUS_MALUS}", "type": "input", "label": BONUS_MALUS,
                  "input_name": BONUS_MALUS, "on_missing": "error", "produces": BONUS_MALUS})
    if peril_structure_ref is not None:
        inputs.append({"name": EXPOSURE, "type": "decimal", "nullable": False,
                       "min": MIN_EXPOSURE, "max": str(MAX_EXPOSURE),
                       "description": "the quote's exposure in years: the frequency offset; "
                                      "bounded by the model's training domain"})
        steps.append({"step_id": f"s_in_{EXPOSURE}", "type": "input", "label": EXPOSURE,
                      "input_name": EXPOSURE, "on_missing": "error", "produces": EXPOSURE})

    for factor, banding in bandings.items():
        steps.append({
            "step_id": f"s_band_{factor}", "type": "expression",
            "label": f"{banding.column} to its band",
            "expr": band_expression(banding.column, banding), "result_type": "string",
            "consumes": [banding.column], "produces": factor,
        })
    if peril_structure_ref is not None:
        return _with_peril_structure(
            inputs, steps, tables, bandings, peril_structure_ref,
            origin_tables if origin_tables is not None else tables, version,
        )
    steps.append({
        "step_id": "s_base", "type": "expression", "label": "Base premium",
        "note": (
            f"{BASE_LABEL}: exp(intercept) of the frequency GLM x the mean freMTPL2sev claim "
            "cost, in whole minor units"
        ),
        "expr": str(base_minor), "result_type": "money_minor",
        "consumes": [], "produces": "base_premium_minor",
    })
    relativities = []
    for factor, ref in tables.items():
        steps.append({
            "step_id": f"s_t_{factor}", "type": "table", "label": f"{factor} relativity",
            "rate_table_ref": str(ref), "key_expr": [factor], "on_miss": "error",
            "consumes": [factor], "produces": f"rel_{factor}",
        })
        relativities.append(f"rel_{factor}")
    steps.append({
        "step_id": "s_premium", "type": "expression", "label": "Premium before rounding",
        "expr": " * ".join(["base_premium_minor", *relativities]), "result_type": "decimal",
        "consumes": ["base_premium_minor", *relativities], "produces": "premium_unrounded",
    })
    steps.append({
        "step_id": "s_out", "type": "output", "label": "Payable premium",
        "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
        "consumes": ["premium_unrounded"],
    })
    return {
        "slug": FREMTPL2_ALGORITHM_SLUG,
        "version": version,
        "input_contract": inputs,
        "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
        "steps": steps,
        "sub_graphs": [],
    }


def _with_peril_structure(
    inputs: list[dict[str, Any]],
    steps: list[dict[str, Any]],
    tables: Mapping[str, ArtifactRef],
    bandings: Mapping[str, Banding],
    structure: ArtifactRef,
    origin_tables: Mapping[str, ArtifactRef],
    version: int,
) -> dict[str, Any]:
    """B1: `model_call` x Π(pinned ÷ origin), rounded once at the output (FR-226, FR-249).

    The feature map's keys are graph names and its values are the models' Factor slugs
    (FR-222): a banded Factor's key is its RAW column, because scoring applies the Banding
    itself, and the exposure maps to the frequency model's offset column.
    """
    feature_map = {
        (bandings[factor].column if factor in bandings else factor): factor for factor in tables
    }
    feature_map[EXPOSURE] = EXPOSURE
    steps.append({
        "step_id": "s_model", "type": "model_call", "label": "Peril Structure risk premium",
        "peril_structure_ref": str(structure), "mode": "exact", "feature_map": feature_map,
        "result_type": "decimal", "consumes": list(feature_map), "produces": "model_premium",
    })
    pinned, origin = [], []
    for factor, ref in tables.items():
        steps.append({
            "step_id": f"s_t_{factor}", "type": "table", "label": f"{factor} relativity",
            "rate_table_ref": str(ref), "key_expr": [factor], "on_miss": "error",
            "consumes": [factor], "produces": f"rel_{factor}",
        })
        steps.append({
            "step_id": f"s_o_{factor}", "type": "table",
            "label": f"{factor} seed-origin relativity",
            "rate_table_ref": str(origin_tables[factor]), "key_expr": [factor],
            "on_miss": "error", "consumes": [factor], "produces": f"origin_{factor}",
        })
        pinned.append(f"rel_{factor}")
        origin.append(f"origin_{factor}")
    ratios = " * ".join(f"({p} / {o})" for p, o in zip(pinned, origin, strict=True))
    guard = " and ".join(f"{o} != 0" for o in origin)
    steps.append({
        "step_id": "s_premium", "type": "expression", "label": "Premium before rounding",
        # Parenthesised whole: the journey appends `* ncd_factor` and `* expense_loading`.
        "expr": f"(({guard}) ? model_premium * {ratios} : 0)", "result_type": "decimal",
        "consumes": ["model_premium", *pinned, *origin], "produces": "premium_unrounded",
    })
    steps.append({
        "step_id": "s_out", "type": "output", "label": "Payable premium",
        "output_name": "payable_premium_minor", "rounding": {"mode": "half_even", "dp": 0},
        "consumes": ["premium_unrounded"],
    })
    steps.append({
        "step_id": "s_out_model", "type": "output", "label": "Peril Structure premium",
        "output_name": STRUCTURE_PREMIUM, "rounding": {"mode": "half_even", "dp": 9},
        "consumes": ["model_premium"],
    })
    return {
        "slug": FREMTPL2_ALGORITHM_SLUG,
        "version": version,
        "input_contract": inputs,
        "outputs": [
            {"name": "payable_premium_minor", "type": "money_minor", "required": True},
            {"name": STRUCTURE_PREMIUM, "type": "decimal", "required": True},
        ],
        "steps": steps,
        "sub_graphs": [],
    }
