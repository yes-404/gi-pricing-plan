"""The Model lifecycle as data (`02` FR-MODEL-64).

The table is the requirement, so the tests are about what it **refuses**. A transition
table that only ever gets asked about legal moves is a lookup, not an invariant.

`01`'s `VALID_DATASET_TRANSITIONS` set the pattern and the reason: the lifecycle written as
data rather than as conditionals scattered through a service, so a reader can see the whole
machine at once and a test can assert the edges that must not exist.
"""

from __future__ import annotations

import pytest

from model_schema import (
    TERMINAL_MODEL_STATUSES,
    VALID_MODEL_TRANSITIONS,
    ModelFlag,
    ModelStatus,
)


@pytest.mark.req("FR-MODEL-64")
def test_every_status_appears_in_the_table() -> None:
    """A status missing from the table is a state nothing can leave, silently."""
    assert set(VALID_MODEL_TRANSITIONS) == set(ModelStatus)


@pytest.mark.req("FR-MODEL-64")
def test_the_lifecycle_order_is_the_one_the_requirement_states() -> None:
    assert VALID_MODEL_TRANSITIONS[ModelStatus.DRAFT] == frozenset(
        {ModelStatus.FITTED, ModelStatus.ARCHIVED}
    )
    assert VALID_MODEL_TRANSITIONS[ModelStatus.FITTED] == frozenset(
        {ModelStatus.REVIEW, ModelStatus.ARCHIVED}
    )
    assert VALID_MODEL_TRANSITIONS[ModelStatus.REVIEW] == frozenset(
        {ModelStatus.APPROVED, ModelStatus.FITTED}
    )
    assert VALID_MODEL_TRANSITIONS[ModelStatus.APPROVED] == frozenset(
        {ModelStatus.SUPERSEDED}
    )


@pytest.mark.req("FR-MODEL-64")
def test_a_model_cannot_reach_review_without_being_fitted() -> None:
    """`draft → review` would put an approval request in front of an approver with no
    coefficients and no diagnostics behind it."""
    assert ModelStatus.REVIEW not in VALID_MODEL_TRANSITIONS[ModelStatus.DRAFT]


@pytest.mark.req("FR-MODEL-64")
def test_review_returns_to_fitted_and_never_to_draft() -> None:
    """`06` FR-GOV-13 returns a rejected artifact to its pre-submission state. For a Model
    that is `fitted`, not `draft`: R2 makes the numbers immutable, so a model cannot un-fit,
    and `draft` in `02` means *reserved, not yet fitted*."""
    assert ModelStatus.FITTED in VALID_MODEL_TRANSITIONS[ModelStatus.REVIEW]
    assert ModelStatus.DRAFT not in VALID_MODEL_TRANSITIONS[ModelStatus.REVIEW]


@pytest.mark.req("FR-MODEL-64")
def test_an_approved_model_supersedes_rather_than_archiving_directly() -> None:
    """Archiving an approved model would remove a Rating Version's referent without
    anything taking its place. Supersession names the replacement; archiving does not."""
    assert VALID_MODEL_TRANSITIONS[ModelStatus.APPROVED] == frozenset(
        {ModelStatus.SUPERSEDED}
    )
    assert ModelStatus.ARCHIVED not in VALID_MODEL_TRANSITIONS[ModelStatus.APPROVED]


@pytest.mark.req("FR-MODEL-64")
def test_archived_is_the_only_end_state() -> None:
    assert frozenset({ModelStatus.ARCHIVED}) == TERMINAL_MODEL_STATUSES
    assert VALID_MODEL_TRANSITIONS[ModelStatus.ARCHIVED] == frozenset()


@pytest.mark.req("FR-MODEL-64")
def test_no_transition_names_a_status_that_does_not_exist() -> None:
    for current, targets in VALID_MODEL_TRANSITIONS.items():
        assert all(isinstance(t, ModelStatus) for t in targets), current


@pytest.mark.req("FR-MODEL-67")
def test_the_flag_a_dataset_invalidation_raises_is_named_not_freeform() -> None:
    """FR-MODEL-67's flag is branched on by the approval path and by `06` FR-GOV-17's
    surface. A free string is a flag two callers spell differently."""
    assert ModelFlag.DATASET_INVALIDATED.value == "dataset_invalidated"
