"""The seed's pure parts, testable without the 36 MB (`07` FR-439).

The data is fetched, not committed, so CI cannot run the seed end to end. What it *can*
run is everything that decides whether the seed still works: the ARFF reader, the recipe
shape, and the rule set's conformance to FR-45.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from arff import to_csv
from seed import DICTIONARY, PORTFOLIO_ROWS, RENAMES, RULES, build_csv, recipe

#: None is the full book. Measured (LG-1641): every smaller sample has a level fitted below the
#: relativity floor; only the full book has none.
ROWS_FOR_A_HEALTHY_FIT: int | None = None

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


@pytest.fixture
def scratch_seed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """A scratch database of its own and a scratch data directory, never the demo's; yields
    the data directory with the fetched ARFF files linked into it.

    Needs the fetched ARFF files and the local Postgres/MinIO stack, so CI skips it."""
    import asyncio
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
        yield tmp_path
    finally:
        asyncio.run(admin_sql(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))


def test_the_seed_reruns_against_a_seeded_database(scratch_seed: Path) -> None:
    """FD 9717: the realm user's `(issuer, subject)` is unique, and the seed used to mint
    a fresh analyst id on every run, so a second seed died on `uq_users_issuer_subject`.
    The second run must reuse the first run's user, and `last-seed.json` must name it.

    Seeds ROWS_FOR_A_HEALTHY_FIT rows twice: every smaller sample fits a level the rating
    path cannot price, and the seed refuses it (the next test)."""
    import asyncio
    import json

    import seed

    assert asyncio.run(seed.run(ROWS_FOR_A_HEALTHY_FIT)) == 0
    first = json.loads((scratch_seed / "last-seed.json").read_text(encoding="utf-8"))
    assert asyncio.run(seed.run(ROWS_FOR_A_HEALTHY_FIT)) == 0
    second = json.loads((scratch_seed / "last-seed.json").read_text(encoding="utf-8"))

    assert second["workspace_id"] != first["workspace_id"]
    assert second["analyst_id"] == first["analyst_id"]


def test_a_small_seed_is_refused_for_its_degenerate_fit(scratch_seed: Path) -> None:
    """At 2 000 rows area[F] has no claims and fits to a relativity of 1.4e-07 (golden premium
    0 minor units; the engine cannot score it). The seed stops, naming the level, rather than
    failing later inside the regression Job as GOLDEN_QUOTE_MISMATCH."""
    import asyncio

    import seed
    from model import DegenerateFitError

    with pytest.raises(DegenerateFitError, match=r"area\[F\]"):
        asyncio.run(seed.run(2000))


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
    its rule is the sampler's evenly spaced integer indices over a pinned input, not because it
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
    # a request for at least as many rows as the book is the whole book, each row once
    assert pl.read_csv(io.BytesIO(build_csv(60_000)), infer_schema=False).height == 50_001

    ids = pl.read_csv(io.BytesIO(first), infer_schema=False)["IDpol"].to_list()
    assert len(ids) == PORTFOLIO_ROWS
    assert len(set(ids)) == PORTFOLIO_ROWS
    # Evenly spaced integer indices `i * N // n` (the maintainer's ruling, 2026-10-10 21:55:37):
    # the sample spans the whole file. The earlier `step = height // rows` stride took `rows` rows
    # at that step, so it ended at policy 39 999 of 50 001 and never saw the file's tail, which in
    # the real book is a distinct block (the last 18 013 rows, claim frequency 0.0613 against
    # 0.1007). Pure integer arithmetic keeps the sample bit-reproducible.
    expected = [str(i * 50_001 // PORTFOLIO_ROWS + 1) for i in range(PORTFOLIO_ROWS)]
    assert ids == expected
    assert ids[0] == "1"
    assert int(ids[-1]) > 49_990


@pytest.mark.req("FR-263")
def test_the_seeded_portfolio_satisfies_the_dislocation_frame(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """03 §4.8: a dislocation portfolio needs a unique, non-null string `quote_id` and a usable
    `exposure_years`, or `dislocation.run` ends `PortfolioFrameError` before any rating (found at
    SL-1526's stage d: the seeded portfolio had `policy_id` and no `quote_id`). The portfolio the
    seed ingests, taken through the seed's own recipe, passes `read_portfolio`; `quote_id` is the
    policy's identity, the same as `policy_id`."""
    import io

    import polars as pl
    import seed

    from pricing_core.data.prepare import apply_recipe
    from pricing_core.rating.analysis import read_portfolio

    _write_book(tmp_path, 2_000)
    monkeypatch.setattr(seed, "DATA_DIR", tmp_path)
    monkeypatch.setattr(seed, "PORTFOLIO_ROWS", 500)
    # the synthetic book has only IDpol and ClaimNb; the recipe also renames and casts the rest
    raw = pl.read_csv(io.BytesIO(seed.build_portfolio_csv()),
                      infer_schema=False)
    # ingestion snake-cases the headers before the recipe runs (`IDpol` -> `i_dpol`)
    raw = raw.rename({"IDpol": "i_dpol", "ClaimNb": "claim_nb"}).with_columns(
        pl.lit("0.5").alias("exposure")
    )
    stored = apply_recipe({"policy_exposure": raw}, [
        step if step["step"] != "cast" else {
            **step, "params": {"columns": {c: t for c, t in step["params"]["columns"].items()
                                           if c in {"exposure_years", "claim_count",
                                                    "claim_amount_minor"}}}}
        for step in recipe(drop_implausible_exposure=True)
    ]).tables["policy_exposure"]

    book = pl.read_csv(io.BytesIO(build_csv(500)), infer_schema=False)
    assert "quote_id" not in book.columns
    # the only change to the sample is the added column: every other column and row is the book's
    assert raw.drop("quote_id").height == book.height
    assert pl.read_csv(io.BytesIO(seed.build_portfolio_csv()), infer_schema=False).drop(
        "quote_id"
    ).equals(book)
    frame = read_portfolio(stored.lazy(), segments=()).collect()
    assert frame["quote_id"].null_count() == 0
    assert frame["quote_id"].n_unique() == frame.height
    assert frame["quote_id"].to_list() == frame["policy_id"].to_list()
    assert frame["quote_id"].dtype == pl.String


@pytest.mark.req("FR-439")
def test_a_degenerate_fit_is_refused_by_factor_and_level() -> None:
    """A level fitted below the relativity floor (no claims in the fitting rows) stops the
    seed, naming `factor[level]`. At 2 000 seeded rows area[F] fits to 1.4e-07: its golden
    premium is 0 minor units and the engine cannot score it. A healthy fit is untouched."""
    from model import DegenerateFitError, refuse_degenerate_fit

    from model_schema import RelativityLevel

    def level(name: str, relativity: float, base: bool = False) -> RelativityLevel:
        return RelativityLevel(level=name, relativity=relativity, is_base=base)

    healthy = {"area": [level("C", 1.0, True), level("F", 1.0354)]}
    refuse_degenerate_fit(healthy)

    degenerate = {
        "area": [level("C", 1.0, True), level("F", 1.3634832381413387e-07)],
        "region": [level("R24", 1.0, True), level("R43", 2.8e-08)],
    }
    with pytest.raises(DegenerateFitError) as raised:
        refuse_degenerate_fit(degenerate)
    assert "area[F]" in str(raised.value)
    assert "region[R43]" in str(raised.value)
    assert "area[C]" not in str(raised.value)


@pytest.mark.req("FR-345")
def test_the_demo_principals_use_existing_roles_and_cover_the_journey() -> None:
    """The WF-699 journey (SL-1527) acts as seven principals over HTTP, and no route grants a
    role or a membership, so the seed does. The set uses built-in role slugs only (no new role),
    and it must make the journey's separation-of-duties steps reachable: the submitter and the
    author hold an approver role, so SUBMITTER_CANNOT_APPROVE and AUTHOR_CANNOT_APPROVE fire past
    the role gate; the prod deployment is decided by one principal holding approver and deployer;
    the admin (service accounts) holds neither approver nor deployer."""
    from seed import DEMO_PRINCIPALS

    from model_schema.permissions import BUILTIN_ROLES

    assert set(DEMO_PRINCIPALS) == {
        "analyst", "actuary", "approver", "second_approver", "admin", "deployer", "prod_approver",
    }
    for roles in DEMO_PRINCIPALS.values():
        assert set(roles) <= set(BUILTIN_ROLES)
    assert "approver" in DEMO_PRINCIPALS["analyst"]
    assert "approver" in DEMO_PRINCIPALS["actuary"]
    assert {"approver", "deployer"} <= set(DEMO_PRINCIPALS["prod_approver"])
    assert not {"approver", "deployer"} & set(DEMO_PRINCIPALS["admin"])
