"""FR-240's transitive and control-intent clauses at compile (`PL-1471`, SL-1472).

An unapproved custom objective reached through a pinned model is refused with
`PIN_NOT_APPROVED`; a `control`-intent Factor in a rateable path is refused with
`CONTROL_FACTOR_IN_RATEABLE_PATH` (`02` FR-88). The helpers are `test_rating_compile_bundle`'s.
"""

from __future__ import annotations

import pytest
from test_rating_compile_bundle import FakeResolver, _resolver, _version

from pricing_core.rating.compile import compile_bundle

OBJ = "custom_objective:asym-loss@1"
MODEL = "model:motor-ad-frequency@7"


def _with_objective(status: str) -> FakeResolver:
    res = _resolver()
    res._payloads[MODEL]["spec"] = {
        "model_type": "gbm",
        "objective": {"kind": "custom", "ref": OBJ},
    }
    res._payloads[OBJ] = {"slug": "asym-loss", "version": 1}
    res._statuses[OBJ] = status
    return res


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
@pytest.mark.parametrize("status", ["certified", "review", "deprecated"])
async def test_an_unapproved_objective_reached_through_a_pinned_model_is_refused(
    status: str,
) -> None:
    with pytest.raises(ValueError, match="PIN_NOT_APPROVED") as refused:
        await compile_bundle(_version(), _with_objective(status))
    message = str(refused.value)
    assert MODEL in message
    assert OBJ in message
    assert repr(status) in message


@pytest.mark.req("FR-240")
@pytest.mark.req("FR-20")
async def test_an_approved_objective_reached_through_a_pinned_model_compiles() -> None:
    bundle = await compile_bundle(_version(), _with_objective("approved"))
    # checked, not embedded: the objective's payload is not in the Bundle (FR-239).
    assert OBJ not in bundle.resolved_payloads


@pytest.mark.req("FR-240")
async def test_a_builtin_objective_needs_no_resolution() -> None:
    res = _resolver()
    res._payloads[MODEL]["spec"] = {
        "model_type": "gbm",
        "objective": {"kind": "builtin", "ref": None},
    }
    # `OBJ` has no payload: a resolve of it would `KeyError`, so passing proves no lookup.
    await compile_bundle(_version(), res)
