#!/usr/bin/env python3
"""Check that the seed record names a workspace and an analyst the database still holds.

FD-1494 limb 1 (PL-1544 Acceptance 7). `examples/fremtpl2/data/last-seed.json` is written by
the seed and trusted by `scripts/demo.py`, but it is a file: a database that was reset or
recreated since leaves a record whose workspace row is gone, and the demo then fails later and
far from the cause (the rule-set pre-flight's "the seed did not finish", or a 403 from the API).
`scripts/demo.py` runs this on every path, `--skip-seed` included, **before** the rule-set
pre-flight, because for an absent workspace that script takes its zero branch and prints the
wrong message.

It checks the workspace row, and the analyst's membership of it (the dev-auth login resolves
through `workspace_members`). Read-only: it opens a session and never a unit of work.

Run: `uv run python scripts/check-seed-record.py <workspace_id> <analyst_id>`
(`GIP_DATABASE_URL` overrides the DSN, as in `scripts/check-rule-sets-runnable.py`).
Exit 1 prints the refusal to stderr; exit 0 prints `seed record holds`.
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
RECORD = "examples/fremtpl2/data/last-seed.json"


async def check(
    database: Any, workspace_id: UUID, analyst_id: UUID, *, out: TextIO, err: TextIO
) -> int:
    """The exit status: 0 when the workspace row and the analyst's membership are present."""
    from sqlalchemy import select

    from app.db.models import WorkspaceMemberRow, WorkspaceRow

    async with database.session() as session:
        workspace = await session.get(WorkspaceRow, workspace_id)
        member = (
            await session.execute(
                select(WorkspaceMemberRow.user_id).where(
                    WorkspaceMemberRow.workspace_id == workspace_id,
                    WorkspaceMemberRow.user_id == analyst_id,
                )
            )
        ).first()
    if workspace is None:
        print(
            f"The seed record ({RECORD}) names workspace {workspace_id}, which the database "
            "does not hold: it was reset or recreated since the seed ran. "
            "Re-run the seed without --skip-seed.",
            file=err,
        )
        return 1
    if member is None:
        print(
            f"The seed record ({RECORD}) names analyst {analyst_id}, who is not a member of "
            f"workspace {workspace_id}. Re-run the seed without --skip-seed.",
            file=err,
        )
        return 1
    print("seed record holds", file=out)
    return 0


def _settings() -> Any:
    from pydantic import SecretStr

    from app.config import Environment, Settings

    return Settings(
        environment=Environment.LOCAL,
        database_url=SecretStr(os.environ.get("GIP_DATABASE_URL", DEFAULT_DSN)),
    )


async def _main(workspace_id: UUID, analyst_id: UUID) -> int:
    from app.db.session import Database

    database = Database(_settings())
    try:
        return await check(database, workspace_id, analyst_id, out=sys.stdout, err=sys.stderr)
    finally:
        await database.dispose()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: check-seed-record.py <workspace_id> <analyst_id>")
    raise SystemExit(asyncio.run(_main(UUID(sys.argv[1]), UUID(sys.argv[2]))))
