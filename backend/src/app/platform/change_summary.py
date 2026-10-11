"""The drafted change summary (03 FR-242's drafting limb; WF-699 E1; `RL-1498` DP-E1-4).

Pure prose over diffs the platform already computes: the structural diff (FR-219) and the
rate-table diffs (FR-231). The text states *what* changed and leaves *why* and the expected
impact to the actuary (DP-E1-3 (a)). Output is deterministic: steps, tables and fields are
sorted, and a percentage is rendered by `str(Decimal)`, never through `float`.
"""

from __future__ import annotations

from collections.abc import Sequence

from model_schema import ArtifactRef
from model_schema.rating import AlgorithmDiff, ChangeSummaryDraft, RateTableChange

__all__ = ["draft_change_summary"]


def draft_change_summary(
    baseline: ArtifactRef | None,
    structural_diff: AlgorithmDiff | None,
    rate_tables: Sequence[RateTableChange],
) -> ChangeSummaryDraft:
    """The draft for a version against `baseline`.

    `baseline` `None` means no approved earlier version; `baseline` set with `structural_diff`
    `None` means the baseline has no algorithm (DP-E1-5). The rate-table entries are those
    whose pinned version differs, one side only included.
    """
    tables = sorted(rate_tables, key=lambda entry: entry.slug)
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
    if entry.from_ref is None and entry.to_ref is not None:
        return f"- {slug}: added, pinned at version {entry.to_ref.version}."
    if entry.to_ref is None and entry.from_ref is not None:
        return f"- {slug}: removed, was pinned at version {entry.from_ref.version}."
    assert entry.from_ref is not None
    assert entry.to_ref is not None
    moved = f"- {slug}: version {entry.from_ref.version} -> {entry.to_ref.version}"
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
