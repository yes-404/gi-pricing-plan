"""The drafted change summary (03 FR-242's drafting limb; WF-699 E1; `RL-1498` DP-E1-4).

Pure prose over diffs the platform already computes: the structural diff (FR-219) and the
rate-table diffs (FR-231). The text states *what* changed and leaves *why* and the expected
impact to the actuary (DP-E1-3 (a)). Output is deterministic: steps, tables and fields are
sorted, and a percentage is rendered by `str(Decimal)`, never through `float`.
"""

from __future__ import annotations

from collections.abc import Sequence

from model_schema import ArtifactRef
from model_schema.rating import (
    AlgorithmDiff,
    ChangeSummaryDraft,
    RateTableChange,
    RatingAlgorithm,
    RatingTableStep,
)

__all__ = ["draft_change_summary", "pair_rate_tables"]


def draft_change_summary(
    baseline: ArtifactRef | None,
    structural_diff: AlgorithmDiff | None,
    rate_tables: Sequence[RateTableChange],
) -> ChangeSummaryDraft:
    """The draft for a version against `baseline`.

    `baseline` `None` means no approved earlier version; `baseline` set with `structural_diff`
    `None` means the baseline has no algorithm (DP-E1-5). The rate-table entries are those
    `pair_rate_tables` names: through the `table` step that names a pin, then by slug for a pin
    no step entry names (`RL-1707`).
    """
    tables = sorted(rate_tables, key=_entry_order)
    lines: list[str] = []
    if baseline is None:
        lines.append("No approved earlier version of this algorithm: nothing to compare against.")
    else:
        lines.append(f"Drafted against {baseline}.")
        if structural_diff is None:
            lines.append("The baseline has no algorithm, so there is no structural diff.")
    structural = _structural_lines(structural_diff) if structural_diff is not None else []
    if structural_diff is not None and not structural and not tables:
        lines.append("No structural change. No rate-table change.")
    else:
        if structural_diff is not None:
            lines.extend(structural or ["No structural change."])
        if baseline is not None and not tables:
            lines.append("No rate-table change.")
    if tables:
        lines.append("Rate tables (unweighted, no portfolio joined):")
        lines.extend(_table_line(entry) for entry in tables)
    lines.extend(["Why:", "Expected impact:"])
    return ChangeSummaryDraft(
        baseline=baseline,
        structural_diff=structural_diff,
        rate_tables=tables,
        text="\n".join(lines),
    )


def pair_rate_tables(
    previous: RatingAlgorithm | None,
    candidate: RatingAlgorithm,
    before: Sequence[ArtifactRef],
    after: Sequence[ArtifactRef],
) -> list[RateTableChange]:
    """RL-1707's two passes over the baseline's and the version's rate-table pins.

    Pass 1 pairs each `table` step by `step_id`, as FR-219 does; pass 2 pairs a pin
    difference no step entry names by slug only where it is the one such ref on each side.
    Without the baseline's algorithm there is no step entry. No entry carries a diff.
    """
    entries: list[RateTableChange] = []
    named: set[ArtifactRef] = set()
    if previous is not None:
        old_steps, new_steps = _table_refs(previous), _table_refs(candidate)
        for step_id in sorted(old_steps.keys() | new_steps.keys()):
            old, new = old_steps.get(step_id), new_steps.get(step_id)
            if old == new:
                continue
            if old is not None and new is not None and old.slug == new.slug:
                entries.append(
                    RateTableChange(slug=old.slug, step_id=step_id, from_ref=old, to_ref=new)
                )
            else:
                if old is not None:
                    entries.append(RateTableChange(slug=old.slug, step_id=step_id, from_ref=old))
                if new is not None:
                    entries.append(RateTableChange(slug=new.slug, step_id=step_id, to_ref=new))
            named.update(ref for ref in (old, new) if ref is not None)
    # DP-5 (a): each side's pins are a set, so a ref listed twice is one pin.
    removed = (set(before) - set(after)) - named
    added = (set(after) - set(before)) - named
    for slug in sorted({ref.slug for ref in removed | added}):
        gone = [ref for ref in removed if ref.slug == slug]
        came = [ref for ref in added if ref.slug == slug]
        if len(gone) == 1 and len(came) == 1:
            entries.append(RateTableChange(slug=slug, from_ref=gone[0], to_ref=came[0]))
        else:
            entries += [RateTableChange(slug=slug, from_ref=ref) for ref in gone]
            entries += [RateTableChange(slug=slug, to_ref=ref) for ref in came]
    return entries


def _table_refs(algorithm: RatingAlgorithm) -> dict[str, ArtifactRef]:
    """Each top-level `table` step's rate-table ref by `step_id`; the draft never inlines."""
    return {
        step.step_id: step.rate_table_ref
        for step in algorithm.steps
        if isinstance(step, RatingTableStep)
    }


def _entry_order(entry: RateTableChange) -> tuple[str, int, str, str, str]:
    """RL-1707 rule 4: slug, step entries before pin entries, step_id, from_ref, to_ref;
    a null ref sorts as the empty string (DP-4 (a))."""
    return (
        entry.slug,
        0 if entry.step_id is not None else 1,
        entry.step_id or "",
        "" if entry.from_ref is None else str(entry.from_ref),
        "" if entry.to_ref is None else str(entry.to_ref),
    )


def _structural_lines(diff: AlgorithmDiff) -> list[str]:
    lines = [f"Step added: {step_id}." for step_id in sorted(diff.added_steps)]
    lines += [f"Step removed: {step_id}." for step_id in sorted(diff.removed_steps)]
    lines += [
        f"Step {change.step_id} field {change.field} changed: "
        f"{change.before!r} -> {change.after!r}."
        for change in sorted(diff.changed_steps, key=lambda c: (c.step_id, c.field))
    ]
    lines += [
        f"Step {repoint.step_id} re-pointed from {repoint.before} to {repoint.after}."
        for repoint in sorted(diff.repointed_tables, key=lambda r: (r.step_id, r.field))
    ]
    lines += [
        f"Sub-graph mount {mount.mount_point} changed: {mount.before} -> {mount.after}"
        f"{' (ports changed)' if mount.ports_changed else ''}."
        for mount in sorted(diff.sub_graph_mounts, key=lambda m: m.mount_point)
    ]
    lines += [
        f"Input {delta.name} {delta.change}."
        for delta in sorted(diff.input_contract_deltas, key=lambda d: d.name)
    ]
    lines += [
        f"Output {delta.name} {delta.change}."
        for delta in sorted(diff.output_deltas, key=lambda d: d.name)
    ]
    return lines


def _table_line(entry: RateTableChange) -> str:
    slug = entry.slug
    label = slug if entry.step_id is None else f"{slug} (step {entry.step_id})"
    if entry.from_ref is None and entry.to_ref is not None:
        return f"- {label}: added, pinned at version {entry.to_ref.version}."
    if entry.to_ref is None and entry.from_ref is not None:
        return f"- {label}: removed, was pinned at version {entry.from_ref.version}."
    assert entry.from_ref is not None
    assert entry.to_ref is not None
    moved = f"- {label}: version {entry.from_ref.version} -> {entry.to_ref.version}"
    if entry.pending or entry.diff is None:
        return (
            f"{moved}, diff pending (a parquet table is not computed here); run "
            f"GET /api/v1/rate-tables/{slug}@{entry.to_ref.version}/diff"
            f"?against={entry.from_ref.version}."
        )
    line = f"{moved}, {entry.diff.changed_cells} cell(s) changed"
    if entry.diff.max_abs_change_pct is not None:
        line += f", largest absolute change {entry.diff.max_abs_change_pct}%"
    return line + "."
