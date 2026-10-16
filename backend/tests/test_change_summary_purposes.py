"""SL-1341 pre-gate audit A-9 (LG 8056): the change summary words a `purposes`-only mount
change (`RL-1344` acceptance 5; PL-1629 acceptance 7). No DB: `_structural_lines` is pure."""

from __future__ import annotations

import pytest

from app.platform.change_summary import _structural_lines
from model_schema import ArtifactRef
from model_schema.rating import AlgorithmDiff, AlgorithmSubGraphChange

_NCD = ArtifactRef.parse("sub_graph:ncd-ladder@4")


def _lines(**change: object) -> list[str]:
    mount = AlgorithmSubGraphChange(mount_point="m_ncd", before=_NCD, after=_NCD, **change)  # type: ignore[arg-type]
    return _structural_lines(AlgorithmDiff(sub_graph_mounts=[mount]))


@pytest.mark.req("FR-218")
@pytest.mark.req("FR-242")
def test_a_purposes_only_mount_change_is_worded_as_such() -> None:
    (line,) = _lines(purposes_changed=True)
    assert line.startswith("Sub-graph mount m_ncd changed:")
    assert line.endswith("(purposes changed).")
    assert "(ports changed)" not in line


@pytest.mark.req("FR-218")
@pytest.mark.req("FR-242")
def test_a_mount_change_without_a_purposes_change_does_not_say_so() -> None:
    (line,) = _lines(ports_changed=True)
    assert "(ports changed)" in line
    assert "purposes" not in line
