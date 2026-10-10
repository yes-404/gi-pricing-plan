"""The seed's pure parts, testable without the 36 MB (`07` FR-439).

The data is fetched, not committed, so CI cannot run the seed end to end. What it *can*
run is everything that decides whether the seed still works: the ARFF reader, the recipe
shape, and the rule set's conformance to FR-45.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from arff import to_csv
from seed import DICTIONARY, PORTFOLIO_ROWS, RENAMES, RULES, build_csv, recipe

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


@pytest.mark.req("FR-439")
def test_arff_strips_the_quotes_around_nominal_values(tmp_path: Path) -> None:
    """Left in place, `'B12'` and `B12` are two categories and every one-way over the
    column is wrong. ARFF quotes nominal values; CSV does not."""
    path = tmp_path / "sample.arff"
    path.write_text(SAMPLE, encoding="utf-8")

    lines = to_csv(path).decode().strip().split("\n")
    assert lines[0] == "IDpol,Exposure,Area,VehGas"
    assert lines[1] == "1,0.1,D,Regular"
    assert lines[2] == "3,0.77,B,Diesel"


@pytest.mark.req("FR-439")
def test_the_arff_reader_refuses_a_file_with_no_attributes(tmp_path: Path) -> None:
    path = tmp_path / "empty.arff"
    path.write_text("@relation nothing\n@data\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no @attribute"):
        to_csv(path)


@pytest.mark.req("FR-35")
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


@pytest.mark.req("FR-35")
def test_the_cleaned_recipe_adds_exactly_one_step() -> None:
    """The loop's whole point: one preparation step is the difference between a version
    that fails validation and one that reaches `validated`."""
    plain = recipe(drop_implausible_exposure=False)
    cleaned = recipe(drop_implausible_exposure=True)
    assert len(cleaned) == len(plain) + 1
    assert cleaned[-1]["step"] == "filter_rows"
    assert "exposure_years" in cleaned[-1]["params"]["expression"]


@pytest.mark.req("FR-45")
def test_the_rule_set_covers_all_four_layers() -> None:
    """FR-45: a Rule Set with an empty layer is a configuration warning. The seed is
    the platform's worked example, so it must not ship one."""
    assert {rule["layer"] for rule in RULES} == {
        "structural",
        "referential",
        "actuarial_sanity",
        "distributional",
    }


@pytest.mark.req("FR-50")
def test_every_seeded_rule_names_a_registered_check() -> None:
    """A rule citing an unregistered check becomes an `error`, never a pass — so a typo
    here would quietly weaken the example rule set rather than break it."""
    from pricing_core.data.validate import CHECKS

    unknown = sorted({rule["check"] for rule in RULES} - set(CHECKS))
    assert not unknown, f"unregistered checks in the seed: {unknown}"


@pytest.mark.req("FR-30")
def test_the_dictionary_covers_every_column_the_seed_produces() -> None:
    """FR-30 keeps the source name against the normalised one. A column with no
    dictionary entry is a column nobody has said the meaning of."""
    described = set(DICTIONARY)
    assert set(RENAMES.values()) <= described
    for column, entry in DICTIONARY.items():
        assert entry["description"], f"{column} has an empty description"


ARFF_DIR = Path(__file__).parent / "data"


@pytest.mark.req("FR-398")
def test_the_seed_reruns_against_a_seeded_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FD 9717: the realm user's `(issuer, subject)` is unique, and the seed used to mint
    a fresh analyst id on every run, so a second seed died on `uq_users_issuer_subject`.
    The second run must reuse the first run's user, and `last-seed.json` must name it.

    Needs the fetched ARFF files and the local Postgres/MinIO stack, so CI skips it. Runs
    on a scratch database of its own and a scratch data directory, never the demo's."""
    import asyncio
    import json
    import os
    import subprocess
    from uuid import uuid4

    import seed
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    if not (ARFF_DIR / "freMTPL2freq.arff").exists():
        pytest.skip("run examples/fremtpl2/fetch.py first")

    name = f"scratch_sl1409c_{uuid4().hex[:8]}"
    admin = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/postgres"

    async def admin_sql(statement: str) -> None:
        engine = create_async_engine(admin, isolation_level="AUTOCOMMIT")
        try:
            async with engine.connect() as connection:
                await connection.execute(text(statement))
        finally:
            await engine.dispose()

    asyncio.run(admin_sql(f'CREATE DATABASE "{name}"'))
    try:
        url = f"postgresql+asyncpg://gipricing:gipricing@localhost:5432/{name}"
        monkeypatch.setenv("GIP_DATABASE_URL", url)
        subprocess.run(
            ["uv", "run", "alembic", "upgrade", "head"],
            cwd=Path(__file__).resolve().parents[2],
            env=dict(os.environ),
            check=True,
            capture_output=True,
        )
        for arff in ARFF_DIR.glob("*.arff"):
            (tmp_path / arff.name).symlink_to(arff.resolve())
        monkeypatch.setattr(seed, "DATA_DIR", tmp_path)

        assert asyncio.run(seed.run(2000)) == 0
        first = json.loads((tmp_path / "last-seed.json").read_text(encoding="utf-8"))
        assert asyncio.run(seed.run(2000)) == 0
        second = json.loads((tmp_path / "last-seed.json").read_text(encoding="utf-8"))

        assert second["workspace_id"] != first["workspace_id"]
        assert second["analyst_id"] == first["analyst_id"]
    finally:
        asyncio.run(admin_sql(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))


def _write_book(directory: Path, policies: int) -> None:
    """A synthetic freMTPL2 pair ordered by claim count, as the real file is."""
    freq = ["@relation freMTPL2freq", "@attribute IDpol numeric", "@attribute ClaimNb numeric",
            "@data"]
    sev = ["@relation freMTPL2sev", "@attribute IDpol numeric", "@attribute ClaimAmount numeric",
           "@data"]
    claiming = policies // 20
    for index in range(policies):
        claims = 1 if index >= policies - claiming else 0
        freq.append(f"{index + 1},{claims}")
        if claims:
            sev.append(f"{index + 1},{1000 + index}.50")
    (directory / "freMTPL2freq.arff").write_text("\n".join(freq) + "\n", encoding="utf-8")
    (directory / "freMTPL2sev.arff").write_text("\n".join(sev) + "\n", encoding="utf-8")


@pytest.mark.req("FR-439")
def test_the_portfolio_sample_is_the_same_policies_every_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PL-1577 DP-2/DP-3: the 20,000-policy sample is reproducible because its size is fixed and
    its rule is the sampler's deterministic every-nth-row over a pinned input, not because it
    has a random seed. The same input gives the same `IDpol` set on two calls, of exactly
    `PORTFOLIO_ROWS` policies, spread over the ordered file (not its head)."""
    import io

    import polars as pl
    import seed

    assert PORTFOLIO_ROWS == 20_000
    _write_book(tmp_path, 50_001)
    monkeypatch.setattr(seed, "DATA_DIR", tmp_path)

    first = build_csv(PORTFOLIO_ROWS)
    second = build_csv(PORTFOLIO_ROWS)
    assert first == second

    ids = pl.read_csv(io.BytesIO(first), infer_schema=False)["IDpol"].to_list()
    assert len(ids) == PORTFOLIO_ROWS
    assert len(set(ids)) == PORTFOLIO_ROWS
    # `step = height // rows` = 2 here: policies 1, 3, 5, ... The rule takes `rows` rows at that
    # step, so it ends at policy 39 999 and never reaches the last 10 002 rows of the file. That is
    # the sampler's own property and it is asserted, not hidden (the real book: step 33, so the
    # sample ends at row 660 000 of 678 013; LG-9966 records the comparison).
    assert ids[:3] == ["1", "3", "5"]
    assert ids[-1] == "39999"
