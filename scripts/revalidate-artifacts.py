#!/usr/bin/env python3
"""Revalidate every stored artifact against today's models (OQ-650, decided (c)).

A stored payload is validated on write against whatever the model said that day, then
parsed again on read against whatever it says now. A tightening that is correct going
forward can therefore make an existing row unreadable, and the failure surfaces at read
time to a user who did nothing, far from the commit that caused it. This script runs the
read path over every stored artifact and reports what no longer reads — on the committer's
clock instead of the user's, and it turns "is anything unreadable?" into a question with
an answer.

It reuses each table's read-path converter (the same function the API calls), so it cannot
disagree with the platform about whether a row reads. It is read-only: it parses and
reports, never mutates. The covered tables are the ones whose read paths exist today; a
stored artifact whose read path is not yet written is out of scope.

Run: `uv run python scripts/revalidate-artifacts.py`
Exit status is non-zero when any stored artifact fails to parse.
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
from collections.abc import Callable
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend" / "src"))

#: The compose stack's DSN, used when `GIP_DATABASE_URL` is not set — the same default the
#: one-command demo uses (`scripts/demo.py`).
DEFAULT_DSN = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"


def _excerpt(exc: Exception) -> str:
    """First 300 chars of the validation error, on one line."""
    return str(exc).replace("\n", " ")[:300]


def _guard(parse: Callable[[Any], None]) -> Callable[[Any], str | None]:
    def checked(row: Any) -> str | None:
        try:
            parse(row)
        except Exception as exc:
            return _excerpt(exc)
        return None

    return checked


async def _all_rows(database: Any, model: type[Any]) -> list[Any]:
    from sqlalchemy import select

    async with database.session() as session:
        return list((await session.execute(select(model))).scalars())


async def _report(
    database: Any,
    label: str,
    rows: list[Any],
    parse: Callable[[Any], None],
) -> bool:
    checked = _guard(parse)
    failed = [(row, exc) for row in rows if (exc := checked(row)) is not None]
    if not failed:
        print(f"  {label}: {len(rows)} row(s) read, all parse")
        return True
    print(f"  {label}: {len(rows)} row(s) read, {len(failed)} do not parse")
    for row, exc in failed[:5]:
        print(f"    - {row.id}: {exc}")
    if len(failed) > 5:
        print(f"    - ... and {len(failed) - 5} more")
    return False


async def _sweep(database: Any) -> int:
    from app.db.models import (
        BandingRow,
        DiagnosticsRow,
        GroupingRow,
        ModelRow,
        PerilStructureRow,
        ProfileRow,
        TransparencyArtifactRow,
        ValidationReportRow,
    )
    from app.platform import diagnostics as diagnostics_service
    from app.platform import perils as perils_service
    from app.platform import transparency as transparency_service
    from app.platform.transformations import to_banding, to_grouping
    from model_schema import FIT_RESULT_ADAPTER, MODEL_SPEC_ADAPTER, Profile, ValidationReport

    clean = True

    rows = await _all_rows(database, ValidationReportRow)
    clean = await _report(
        database, "validation_reports", rows,
        lambda r: ValidationReport.model_validate(r.body),
    ) and clean

    rows = await _all_rows(database, ProfileRow)
    clean = await _report(
        database, "profiles", rows,
        lambda r: Profile.model_validate(r.body),
    ) and clean

    rows = await _all_rows(database, BandingRow)
    clean = await _report(database, "bandings", rows, to_banding) and clean

    rows = await _all_rows(database, GroupingRow)
    clean = await _report(database, "groupings", rows, to_grouping) and clean

    rows = await _all_rows(database, TransparencyArtifactRow)
    clean = await _report(
        database, "transparency_artifacts", rows, transparency_service.to_artifact
    ) and clean

    rows = await _all_rows(database, DiagnosticsRow)
    clean = await _report(
        database, "diagnostics", rows, diagnostics_service.to_diagnostics
    ) and clean

    rows = await _all_rows(database, PerilStructureRow)
    clean = await _report(
        database, "peril_structures", rows, perils_service.to_structure
    ) and clean

    # `models` parses two body columns through two adapters, so it does not fit the
    # single-parse `_report` shape.
    from sqlalchemy import select

    async with database.session() as session:
        model_rows = (
            await session.execute(select(ModelRow.id, ModelRow.spec, ModelRow.fit_result))
        ).all()
    model_failures: list[str] = []
    for model_id, spec, fit_result in model_rows:
        try:
            MODEL_SPEC_ADAPTER.validate_python(spec)
        except Exception as exc:
            model_failures.append(f"models {model_id} spec: {_excerpt(exc)}")
        if fit_result is not None:
            try:
                FIT_RESULT_ADAPTER.validate_python(fit_result)
            except Exception as exc:
                model_failures.append(f"models {model_id} fit_result: {_excerpt(exc)}")
    if not model_failures:
        print(f"  models: {len(model_rows)} row(s) read, all parse")
    else:
        print(f"  models: {len(model_rows)} row(s) read, {len(model_failures)} do not parse")
        for detail in model_failures[:5]:
            print(f"    - {detail}")
        if len(model_failures) > 5:
            print(f"    - ... and {len(model_failures) - 5} more")
        clean = False

    return 0 if clean else 1


def _settings() -> Any:
    from pydantic import SecretStr

    from app.config import Environment, Settings

    return Settings(
        environment=Environment.LOCAL,
        database_url=SecretStr(os.environ.get("GIP_DATABASE_URL", DEFAULT_DSN)),
    )


async def _main() -> int:
    from app.db.session import Database

    database = Database(_settings())
    try:
        return await _sweep(database)
    finally:
        await database.dispose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
