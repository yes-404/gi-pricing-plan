"""Capture `apply_grouping`'s behaviour from a given `groupings.py` as fixture expectations.

    BASE=c62f1ff67b45022fde947ff67cd01be5ffe89fc5
    SRC=packages/pricing-core/src/pricing_core/modelling/groupings.py
    DATA=packages/pricing-core/tests/data
    git show $BASE:$SRC > /tmp/groupings_old.py
    uv run python $DATA/make_apply_grouping_fixture.py /tmp/groupings_old.py \
        > $DATA/apply_grouping_c62f1ff6.json

Seed 20261017; 3 groupings x 600 draws of 0, 1, 2 or 5 values (strings, ints, floats, bool, null),
the draws that polars refuses to build as one Series skipped. Run once; the output is committed.
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
from uuid import uuid4

import polars as pl

from model_schema import Grouping, GroupingMethod, UnseenLevelBehaviour

MAPPING = {"a": "X", "b": "X", "c": "Y", "1": "Z", "1.0": "Z", "true": "Y"}
GROUPINGS = [
    {"behaviour": "error", "default": None},
    {"behaviour": "map_to_default", "default": "Y"},
    {"behaviour": "map_to_base", "default": None},
]
VALUES = ["a", "b", "c", "d", "e", None, 1, 1.0, True]


def build(spec: dict) -> Grouping:
    return Grouping(
        id=uuid4(), slug="g", dataset_id=uuid4(), version=1, column="c",
        method=GroupingMethod.MANUAL, mapping=MAPPING,
        unseen_level_behaviour=UnseenLevelBehaviour(spec["behaviour"]),
        default_target_level=spec["default"],
    )


def main(old_path: str) -> None:
    module_spec = importlib.util.spec_from_file_location("groupings_old", old_path)
    assert module_spec is not None
    assert module_spec.loader is not None
    old = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(old)
    rng = random.Random(20261017)
    cases = []
    for index, spec in enumerate(GROUPINGS):
        grouping = build(spec)
        for _ in range(600):
            values = [rng.choice(VALUES) for _ in range(rng.choice([0, 1, 1, 1, 2, 5]))]
            try:
                series = pl.Series("col", values, dtype=None if values else pl.String)
            except Exception:
                continue
            try:
                expected = {"levels": old.apply_grouping(series, grouping).to_list()}
            except Exception as error:
                expected = {"refusal": [type(error).__name__, str(error)]}
            cases.append({"grouping": index, "values": values, "expected": expected})
    json.dump({"mapping": MAPPING, "groupings": GROUPINGS, "cases": cases}, sys.stdout, indent=0)


if __name__ == "__main__":
    main(sys.argv[1])
