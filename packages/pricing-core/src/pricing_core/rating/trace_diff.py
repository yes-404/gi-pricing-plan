"""The Quote Sandbox step diff (FR-262, `03` §4.10): two executed Traces in, one `TraceDiff` out.

Pure and deterministic. Steps match by `step_id`; `elapsed_us` is recorded and never compared;
values compare as canonical JSON, so `1`, `1.0` and `True` are three different values. This is
not FR-219's structural `AlgorithmDiff`, which compares two algorithm definitions. That diff is
what `own_change` is read from (`RL-1261`): which steps are listed comes from the traces, whether a
listed step was itself edited comes from the two compiled algorithms.
"""

from __future__ import annotations

import json
from typing import Final

from model_schema.rating import RatingAlgorithm, diff_algorithms
from model_schema.scoring import StepChange, Trace, TraceDiff, TraceStep, TraceStepField

__all__ = ["diff_traces"]

_COMPARED: Final[tuple[TraceStepField, ...]] = (
    "type",
    "label",
    "consumed",
    "produced",
    "matched",
    "violation",
)


def _canonical(value: object) -> str:
    """Canonical JSON, so `1`, `1.0` and `True` are three different values."""
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))


def _by_id(trace: Trace) -> dict[str, TraceStep]:
    steps: dict[str, TraceStep] = {}
    for step in trace.steps:
        if step.step_id in steps:
            raise ValueError(f"duplicate step_id {step.step_id!r} in one trace")
        steps[step.step_id] = step
    return steps


def _edited_step_ids(base: RatingAlgorithm, comparison: RatingAlgorithm) -> set[str]:
    """Steps whose definition differs, as FR-219's `diff_algorithms` reports it. `note` is
    excluded here and only here (`RL-1261`): a documentation edit changes no behaviour."""
    return {c.step_id for c in diff_algorithms(base, comparison).changed_steps if c.field != "note"}


def diff_traces(
    base: Trace,
    comparison: Trace,
    base_algorithm: RatingAlgorithm,
    comparison_algorithm: RatingAlgorithm,
) -> TraceDiff:
    """Base steps in base order, then added steps in comparison order. `own_change` is true for
    an added or removed step and for a changed step whose definition differs between the two
    compiled algorithms (`RL-1261`); false means the step changed only through what it consumed.
    Each algorithm is the compiled (sub-graph-inlined) one, so a mounted step is compared by its
    namespaced `step_id`."""
    edited = _edited_step_ids(base_algorithm, comparison_algorithm)
    base_steps, other_steps = _by_id(base), _by_id(comparison)
    changes: list[StepChange] = []
    unchanged = 0
    for step_id, before in base_steps.items():
        after = other_steps.get(step_id)
        if after is None:
            changes.append(
                StepChange(step_id=step_id, change="removed", own_change=True, base=before)
            )
            continue
        fields = [
            f for f in _COMPARED if _canonical(getattr(before, f)) != _canonical(getattr(after, f))
        ]
        if not fields:
            unchanged += 1
            continue
        changes.append(
            StepChange(
                step_id=step_id,
                change="changed",
                changed_fields=fields,
                own_change=step_id in edited,
                base=before,
                comparison=after,
            )
        )
    changes.extend(
        StepChange(step_id=step_id, change="added", own_change=True, comparison=after)
        for step_id, after in other_steps.items()
        if step_id not in base_steps
    )
    return TraceDiff(steps=changes, unchanged=unchanged)
