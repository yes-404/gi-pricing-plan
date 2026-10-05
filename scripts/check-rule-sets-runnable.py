#!/usr/bin/env python3
"""Check that every rule set in a workspace would run: the demo's pre-flight.

RL-1407 condition 2. A rule set runs only with every member present and `approved`
(`01` FR-50), so a workspace seeded before FD-1356's fix and then reset has rule sets the
platform refuses. `scripts/demo.py` runs this on every path, `--skip-seed` included, so the
refusal arrives before anything is served and not as a failed validation in the browser.

For each dataset in the workspace that has a rule set it calls
`rule_service.rule_set_to_run`, the run's own check, so this cannot disagree with the
platform. Read-only: it opens a session and never a unit of work.

Run: `uv run python scripts/check-rule-sets-runnable.py <workspace_id>`
(`GIP_DATABASE_URL` overrides the DSN, as in `scripts/revalidate-artifacts.py`).
Exit 1 prints the refusal's detail to stderr; exit 0 prints `rule sets runnable: <n>`.
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
from typing import Any, TextIO
from uuid import UUID

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend" / "src"))

#: The compose stack's DSN, used when `GIP_DATABASE_URL` is not set.
DEFAULT_DSN = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"


async def check(database: Any, workspace_id: UUID, *, out: TextIO, err: TextIO) -> int:
    """The exit status: 0 when every rule set runs, 1 on the first refusal or no rule set."""
    from sqlalchemy import select

    from app.db.models import DatasetRow, ValidationRuleSetRow
    from app.errors import PlatformError
    from app.platform import validation_rules as rule_service

    runnable = 0
    async with database.session() as session:
        datasets = (
            await session.execute(
                select(DatasetRow)
                .where(
                    DatasetRow.workspace_id == workspace_id,
                    DatasetRow.id.in_(
                        select(ValidationRuleSetRow.dataset_id).where(
                            ValidationRuleSetRow.workspace_id == workspace_id
                        )
                    ),
                )
                .order_by(DatasetRow.slug)
            )
        ).scalars()
        for dataset in datasets:
            try:
                await rule_service.rule_set_to_run(
                    session, workspace_id=workspace_id, dataset_id=dataset.id, slug=dataset.slug
                )
            except PlatformError as exc:
                print(exc.detail or exc.title, file=err)
                return 1
            runnable += 1
    if runnable == 0:
        print(
            f"Workspace {workspace_id} has no rule set: the seed did not finish. Re-run the seed.",
            file=err,
        )
        return 1
    print(f"rule sets runnable: {runnable}", file=out)
    return 0


def _settings() -> Any:
    from pydantic import SecretStr

    from app.config import Environment, Settings

    return Settings(
        environment=Environment.LOCAL,
        database_url=SecretStr(os.environ.get("GIP_DATABASE_URL", DEFAULT_DSN)),
    )


async def _main(workspace_id: UUID) -> int:
    from app.db.session import Database

    database = Database(_settings())
    try:
        return await check(database, workspace_id, out=sys.stdout, err=sys.stderr)
    finally:
        await database.dispose()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-rule-sets-runnable.py <workspace_id>")
    raise SystemExit(asyncio.run(_main(UUID(sys.argv[1]))))
