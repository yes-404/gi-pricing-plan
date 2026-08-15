"""The seed's pure parts, testable without the 36 MB (`07` FR-PLAT-37).

The data is fetched, not committed, so CI cannot run the seed end to end. What it *can*
run is everything that decides whether the seed still works: the ARFF reader, the recipe
shape, and the rule set's conformance to FR-DATA-16.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from arff import to_csv
from seed import DICTIONARY, RENAMES, RULES, recipe

SAMPLE = """% a comment, ignored
@relation freMTPL2freq

@attribute IDpol numeric
@attribute Exposure numeric
@attribute Area {'A','B'}
@attribute VehGas string

@data
1,0.1,'D',Regular
3,0.77,'B','Diesel'
"""


@pytest.mark.req("FR-PLAT-37")
def test_arff_strips_the_quotes_around_nominal_values(tmp_path: Path) -> None:
    """Left in place, `'B12'` and `B12` are two categories and every one-way over the
    column is wrong. ARFF quotes nominal values; CSV does not."""
    path = tmp_path / "sample.arff"
    path.write_text(SAMPLE, encoding="utf-8")

    lines = to_csv(path).decode().strip().split("\n")
    assert lines[0] == "IDpol,Exposure,Area,VehGas"
    assert lines[1] == "1,0.1,D,Regular"
    assert lines[2] == "3,0.77,B,Diesel"


@pytest.mark.req("FR-PLAT-37")
def test_the_arff_reader_refuses_a_file_with_no_attributes(tmp_path: Path) -> None:
    path = tmp_path / "empty.arff"
    path.write_text("@relation nothing\n@data\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no @attribute"):
        to_csv(path)


@pytest.mark.req("FR-DATA-9")
def test_the_recipe_renames_before_it_casts() -> None:
    """Order is the recipe's meaning. `cast` names `exposure_years`, which does not exist
    until `rename` has run — reversing the two makes the cast silently target nothing."""
    steps = recipe(drop_implausible_exposure=False)
    kinds = [step["step"] for step in steps]
    assert kinds == ["rename", "cast"]

    renamed = set(steps[0]["params"]["columns"].values())
    cast = set(steps[1]["params"]["columns"])
    assert {"exposure_years", "claim_count"} <= renamed
    assert cast & renamed, "the cast targets no renamed column — check the order"


@pytest.mark.req("FR-DATA-9")
def test_the_cleaned_recipe_adds_exactly_one_step() -> None:
    """The loop's whole point: one preparation step is the difference between a version
    that fails validation and one that reaches `validated`."""
    plain = recipe(drop_implausible_exposure=False)
    cleaned = recipe(drop_implausible_exposure=True)
    assert len(cleaned) == len(plain) + 1
    assert cleaned[-1]["step"] == "filter_rows"
    assert "exposure_years" in cleaned[-1]["params"]["expression"]


@pytest.mark.req("FR-DATA-16")
def test_the_rule_set_covers_all_four_layers() -> None:
    """FR-DATA-16: a Rule Set with an empty layer is a configuration warning. The seed is
    the platform's worked example, so it must not ship one."""
    assert {rule["layer"] for rule in RULES} == {
        "structural",
        "referential",
        "actuarial_sanity",
        "distributional",
    }


@pytest.mark.req("FR-DATA-21")
def test_every_seeded_rule_names_a_registered_check() -> None:
    """A rule citing an unregistered check becomes an `error`, never a pass — so a typo
    here would quietly weaken the example rule set rather than break it."""
    from pricing_core.data.validate import CHECKS

    unknown = sorted({rule["check"] for rule in RULES} - set(CHECKS))
    assert not unknown, f"unregistered checks in the seed: {unknown}"


@pytest.mark.req("FR-DATA-5")
def test_the_dictionary_covers_every_column_the_seed_produces() -> None:
    """FR-DATA-5 keeps the source name against the normalised one. A column with no
    dictionary entry is a column nobody has said the meaning of."""
    described = set(DICTIONARY)
    assert set(RENAMES.values()) <= described
    for column, entry in DICTIONARY.items():
        assert entry["description"], f"{column} has an empty description"
