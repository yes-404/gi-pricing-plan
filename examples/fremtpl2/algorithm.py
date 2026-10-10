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

FREMTPL2_ALGORITHM_SLUG: Final = "fremtpl2-rate"

#: The eighth raw input: freMTPL2's `BonusMalus`. A rating-table input and not a model feature,
#: so no step of this algorithm consumes it (PL-1525 Pre-mint note 4); the journey's `ncd-ladder`
#: sub-graph keys on it. The range is freMTPL2's own (50 to 230).
BONUS_MALUS: Final = "bonus_malus"
BONUS_MALUS_RANGE: Final = (50, 230)

#: DP-a2's ruled label. It opens the base step's note and the algorithm's change note.
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


def build_fremtpl2_algorithm(
    *,
    tables: Mapping[str, ArtifactRef],
    bandings: Mapping[str, Banding],
    base_minor: int,
    domains: Mapping[str, Sequence[str]],
    version: int = 1,
) -> dict[str, Any]:
    """The algorithm payload, in the order of `tables` (one seeded table per Factor).

    `tables` maps each Factor slug to its seeded Rate Table ref. `bandings` maps each banded
    Factor slug to its Banding (its `column` is the raw input). `domains` maps each
    categorical Factor slug (which is also its column) to the levels the table holds.
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
            inputs.append({"name": column, "type": "string", "nullable": False,
                           "domain": list(domains[factor])})
        steps.append({"step_id": f"s_in_{column}", "type": "input", "label": column,
                      "input_name": column, "on_missing": "error", "produces": column})
    inputs.append({"name": BONUS_MALUS, "type": "int", "nullable": False,
                   "min": BONUS_MALUS_RANGE[0], "max": BONUS_MALUS_RANGE[1],
                   "description": "non-modelled: a rating-table input, not a model feature"})
    steps.append({"step_id": f"s_in_{BONUS_MALUS}", "type": "input", "label": BONUS_MALUS,
                  "input_name": BONUS_MALUS, "on_missing": "error", "produces": BONUS_MALUS})

    for factor, banding in bandings.items():
        steps.append({
            "step_id": f"s_band_{factor}", "type": "expression",
            "label": f"{banding.column} to its band",
            "expr": band_expression(banding.column, banding), "result_type": "string",
            "consumes": [banding.column], "produces": factor,
        })
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
