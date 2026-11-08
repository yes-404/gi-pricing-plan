"""`scripts/measure-p2-nfr-sweep.py`'s storage arm (FD-2094, PL-2095): its per-version queries run.

The arm's `audit_events_rows` query bound a `UUID` against `cast(:v as text)`, which asyncpg
refuses (`expected str, got UUID`). No test reached the database arms, so the defect met its first
run in a measurement window. Each query runs here on the login role against the per-worktree
database, with a version id that has no rows: every sum is then `0`.

`dataset_versions_row` is excluded: it is a `scalar_one` over a row the empty database lacks, so it
raises `NoResultFound` for any id, which says nothing about its bind. Its bind is the plain
`id = :v` comparison the other queries share.

No `@pytest.mark.req` marker: the correctness of a measurement tool, not requirement evidence.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

from app.db.session import Database
from model_schema import new_uuid7

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "measure-p2-nfr-sweep.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("measure_p2_nfr_sweep_storage", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = _load()

EXCLUDED = {"dataset_versions_row"}
COALESCE_SHAPED = sorted(set(m.STORAGE_VERSION_QUERIES) - EXCLUDED)


def test_the_excluded_query_is_a_query_the_arm_has() -> None:
    assert set(m.STORAGE_VERSION_QUERIES) >= EXCLUDED
    assert COALESCE_SHAPED  # the parametrisation below is not vacuous


@pytest.mark.parametrize("name", COALESCE_SHAPED)
async def test_a_storage_query_binds_a_uuid_version_id(name: str, database: Database) -> None:
    async with database.session() as session:
        value = await m._version_scalar(session, m.STORAGE_VERSION_QUERIES[name], new_uuid7())
    assert value == 0
