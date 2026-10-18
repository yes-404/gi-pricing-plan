"""FR-190, SL-1543 DP-4 (a): the reconcile Job finds the claim-count column for imputation.

Pure -- the helper reads only the structure's severity references and their specs, so no
database is needed. The end-to-end persistence of the imputation counts is
`test_demo_peril_structure.py` (DB window).
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from app.worker.model_handlers import _claim_count_column


def _structure(*severity_refs: str | None) -> Any:
    return SimpleNamespace(
        perils=[SimpleNamespace(severity_model=ref) for ref in severity_refs]
    )


def _candidates(**weights: tuple[str, str | None]) -> dict[str, Any]:
    return {
        ref: SimpleNamespace(spec=SimpleNamespace(weight=SimpleNamespace(kind=k, column=c)))
        for ref, (k, c) in weights.items()
    }


@pytest.mark.req("FR-190")
def test_the_severity_models_weight_column_is_the_claim_count_column() -> None:
    structure = _structure("model:ad-sev@1", None)
    candidates = _candidates(**{"model:ad-sev@1": ("column", "claim_count")})
    assert _claim_count_column(structure, candidates) == "claim_count"


@pytest.mark.req("FR-190")
def test_two_severity_models_on_one_weight_column_agree() -> None:
    structure = _structure("model:a@1", "model:b@1")
    candidates = _candidates(
        **{"model:a@1": ("column", "claim_count"), "model:b@1": ("column", "claim_count")}
    )
    assert _claim_count_column(structure, candidates) == "claim_count"


@pytest.mark.req("FR-190")
@pytest.mark.parametrize(
    ("structure", "candidates"),
    [
        (_structure(None), {}),  # no severity model at all (burning-cost method)
        (_structure("model:a@1"), _candidates(**{"model:a@1": ("none", None)})),
        (  # two different weight columns: not guessed
            _structure("model:a@1", "model:b@1"),
            _candidates(**{"model:a@1": ("column", "n1"), "model:b@1": ("column", "n2")}),
        ),
    ],
    ids=["no-severity", "unweighted", "disagreeing"],
)
def test_no_unambiguous_claim_count_column_is_none_never_a_guess(
    structure: Any, candidates: dict[str, Any]
) -> None:
    assert _claim_count_column(structure, candidates) is None
