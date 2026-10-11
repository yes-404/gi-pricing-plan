"""Shape U / Shape T for PL-1364 Task 5 (RL-1365 DP-A2). Pure builders, no I/O."""
from decimal import Decimal

REF = "rating_version:minimal-rv@1"
RUNGS = ["risk_premium", "expense_loading", "commission", "profit_loading", "office_premium",
         "optimisation_adjustment", "constraints", "instalment_loading", "ipt_and_fees", "payable_premium"]


def shape_u_dict() -> dict:
    ladder = []
    for i, name in enumerate(RUNGS):
        ladder.append({
            "rung": name, "value_minor": 10_000 + i, "unrounded_minor": str(Decimal(10_000 + i) + Decimal("0.4")),
            "rounding": {"mode": "half_even", "dp": 0},
            "operation": {"kind": "multiply", "factor": "1.05", "applied": ["rule_a", "rule_b"]},
        })
    return {
        "outcome": "quoted", "rating_version_ref": REF, "bundle_hash": "sha256:" + "a" * 64,
        "premium_ladder": ladder, "outputs": {f"factor_{i:02d}": 1000 + i for i in range(60)},
        "decline_reasons": [], "trace": None, "timing_ms": {"total": 1.5, "compile": 0.2, "score": 1.1},
    }


def shape_t_dict() -> dict:
    d = shape_u_dict()
    steps = [{
        "step_id": f"s{i:02d}", "type": "expression", "label": f"Step {i}",
        "consumed": {"a": i, "b": i + 1, "c": i + 2}, "produced": {"x": i * 2, "y": i * 3, "z": i * 4},
        "elapsed_us": 40 + i,
    } for i in range(20)]
    d["trace"] = {"rating_version_ref": REF, "bundle_hash": d["bundle_hash"], "steps": steps,
                  "ladder_reconciled": True, "ladder_check_version": 1}
    return d
