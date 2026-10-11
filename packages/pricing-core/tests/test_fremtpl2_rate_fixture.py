"""The measurement-only freMTPL2 rating fixture under `examples/fremtpl2/rating/` (WK-673 Slice 3,
PL-1452 Task 7; dispatch record Ruling 1 (b')). No data is needed: every file loads through its
`model-schema` model and the baseline and each F3 change set's candidate compile."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

from model_schema.rating import RateTable, RatingAlgorithm
from pricing_core.rating.analysis import derive_changes
from pricing_core.rating.compile import compile_bundle

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "measure-attribution-cost.py"


def _harness() -> Any:
    spec = importlib.util.spec_from_file_location("measure_attribution_cost", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


H = _harness()


@pytest.mark.req("FR-266")
def test_every_fixture_file_loads_and_compiles() -> None:
    fx = H.load_fixture()
    RatingAlgorithm.model_validate(fx.baseline)
    RatingAlgorithm.model_validate(fx.full)
    assert fx.tables, "no rate table file loaded"
    for ref, payload in fx.tables.items():
        RateTable.model_validate({k: payload[k] for k in RateTable.model_fields})
        assert payload["rows"]
        assert ref == f"rate_table:{payload['slug']}@{payload['version']}"
    # No model_call and no model pin: Ruling 1 (b').
    for alg in (fx.baseline, fx.full):
        assert all(s["type"] != "model_call" for s in alg["steps"])
    base_v, _cand_v, resolver = H.versions_for(fx, [])
    asyncio.run(compile_bundle(base_v, resolver))
    for members in [*fx.sets, list(range(6))]:
        _b, cand_v, resolver = H.versions_for(fx, members)
        asyncio.run(compile_bundle(cand_v, resolver))


@pytest.mark.req("FR-1399")
def test_member_zero_is_one_group_and_the_catalogue_partitions_the_derived_changes() -> None:
    fx = H.load_fixture()
    base_v, cand_v, resolver = H.versions_for(fx, list(range(6)))
    derived = asyncio.run(derive_changes(base_v, cand_v, resolver))
    groups = H.groups_for(fx, list(range(6)), derived)
    assert len(groups) == 6
    flat = [c for g in groups for c in g.changes]
    assert sorted(flat) == sorted(d.id for d in derived)  # every change in exactly one group
    # Member 0 (the model swap) holds the seven table repoints, the frequency product, the two
    # new input steps and the two new tables: one group (condition (iii)).
    assert len(groups[0].changes) >= 12
    kinds = {d.id: d.kind for d in derived}
    assert sum(kinds[c] == "table_repointed" for c in groups[0].changes) == 7
