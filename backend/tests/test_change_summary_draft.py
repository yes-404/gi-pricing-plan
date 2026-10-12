"""The drafted change summary, pure (FR-242's drafting limb; WF-699 E1; PL-1502 Acceptance 1-9, 20).

`draft_change_summary` turns a baseline, a structural diff and the per-table diffs into the
deterministic `text` an actuary edits before submitting. It states *what* changed and leaves
*why* and the expected impact blank (DP-E1-3 (a)). No database: the diffs are built here.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.platform.change_summary import draft_change_summary
from model_schema import ArtifactRef
from model_schema.rating import (
    AlgorithmDiff,
    AlgorithmStepChange,
    AlgorithmTableRepoint,
    RateTableChange,
    RateTableDiff,
)

pytestmark = pytest.mark.req("FR-242")


def _rv(version: int) -> ArtifactRef:
    return ArtifactRef(type="rating_version", slug="motor", version=version)


def _table(slug: str, version: int) -> ArtifactRef:
    return ArtifactRef(type="rate_table", slug=slug, version=version)


def _changed(slug: str, before: int, after: int, **diff: object) -> RateTableChange:
    return RateTableChange(
        slug=slug,
        from_ref=_table(slug, before),
        to_ref=_table(slug, after),
        diff=RateTableDiff(**diff),  # type: ignore[arg-type]
    )


def test_each_structural_change_is_stated_by_step_id() -> None:
    structural = AlgorithmDiff(
        added_steps=["s_new"],
        removed_steps=["s_old"],
        changed_steps=[AlgorithmStepChange(step_id="s_expr", field="expr", before="a", after="b")],
        repointed_tables=[
            AlgorithmTableRepoint(
                step_id="s_age",
                field="rate_table_ref",
                before=_table("age", 1),
                after=_table("age", 2),
            )
        ],
    )
    draft = draft_change_summary(_rv(1), structural, [])
    for needle in ("s_new", "s_old", "s_expr", "s_age", "rate_table:age@1", "rate_table:age@2"):
        assert needle in draft.text
    assert draft.structural_diff == structural
    assert draft.baseline == _rv(1)


def test_each_rate_table_change_is_stated() -> None:
    entry = _changed("age", 3, 4, changed_cells=2, max_abs_change_pct=Decimal("12.5"))
    draft = draft_change_summary(_rv(1), AlgorithmDiff(), [entry])
    line = next(line for line in draft.text.splitlines() if "age" in line)
    for needle in ("age", "3", "4", "2", "12.5"):
        assert needle in line
    assert "unweighted" in draft.text
    assert draft.rate_tables == [entry]


def test_a_table_pinned_on_one_side_only_is_named() -> None:
    added = RateTableChange(slug="vehicle", from_ref=None, to_ref=_table("vehicle", 1))
    removed = RateTableChange(slug="zone", from_ref=_table("zone", 2), to_ref=None)
    draft = draft_change_summary(_rv(1), AlgorithmDiff(), [added, removed])
    vehicle = next(line for line in draft.text.splitlines() if "vehicle" in line)
    zone = next(line for line in draft.text.splitlines() if "zone" in line)
    assert "added" in vehicle
    assert "removed" in zone


def test_no_change_says_so() -> None:
    draft = draft_change_summary(_rv(1), AlgorithmDiff(), [])
    assert "No structural change. No rate-table change." in draft.text
    assert draft.rate_tables == []


def test_no_baseline_says_so() -> None:
    draft = draft_change_summary(None, None, [])
    assert draft.baseline is None
    assert draft.structural_diff is None
    assert "no approved earlier version" in draft.text.lower()


def test_a_baseline_without_an_algorithm_has_no_structural_diff() -> None:
    draft = draft_change_summary(_rv(1), None, [])
    assert draft.baseline == _rv(1)
    assert draft.structural_diff is None
    assert "has no algorithm" in draft.text
    assert "no approved earlier version" not in draft.text.lower()


def test_the_draft_is_deterministic() -> None:
    steps = ["s_c", "s_a", "s_b"]
    tables = [
        _changed("zone", 1, 2, changed_cells=1),
        _changed("age", 1, 2, changed_cells=3),
    ]
    one = draft_change_summary(_rv(1), AlgorithmDiff(added_steps=steps), tables)
    two = draft_change_summary(
        _rv(1), AlgorithmDiff(added_steps=list(reversed(steps))), list(reversed(tables))
    )
    assert one.text == two.text
    assert one.text.index("s_a") < one.text.index("s_b") < one.text.index("s_c")
    assert one.text.index("age") < one.text.index("zone")


def test_a_percentage_is_never_rendered_through_float() -> None:
    pct = Decimal("0.1000000000000000055511151231")
    draft = draft_change_summary(
        _rv(1), AlgorithmDiff(), [_changed("age", 1, 2, changed_cells=1, max_abs_change_pct=pct)]
    )
    assert str(pct) in draft.text
    assert f"change {pct}%" in draft.text  # the full digits, not a float's `0.1`


def test_why_and_impact_are_left_to_the_actuary() -> None:
    draft = draft_change_summary(_rv(1), AlgorithmDiff(added_steps=["s1"]), [])
    lines = draft.text.splitlines()
    assert lines[-2:] == ["Why:", "Expected impact:"]


def test_a_parquet_pair_is_named_pending_not_computed() -> None:
    entry = RateTableChange(
        slug="big", from_ref=_table("big", 1), to_ref=_table("big", 2), pending=True
    )
    draft = draft_change_summary(_rv(1), AlgorithmDiff(), [entry])
    assert draft.rate_tables[0].diff is None
    line = next(line for line in draft.text.splitlines() if "big" in line)
    assert "pending" in line
    assert "/api/v1/rate-tables/big@2/diff?against=1" in line
