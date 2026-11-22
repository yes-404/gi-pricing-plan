#!/usr/bin/env python3
"""List the stored rule sets whose reference version belongs to another Dataset.

`01` FR-57 (clause of 2026-11-22): a rule set's reference version is checked when the rule set is
written, and again when a run uses it. Rule sets stored before the check may name a version of a
Dataset other than their own, in this workspace or another. This lists them for an administrator
and changes nothing: it opens a session and never a unit of work.

Each line gives the rule set's id, workspace, Dataset, slug and version, then the reference
version's id and the Dataset it belongs to. The last line is the count. A reference that names no
stored version is not another Dataset's version and is not listed.

Run: `uv run python scripts/list-cross-dataset-references.py [<workspace_id>]`
(all workspaces without the argument; `GIP_DATABASE_URL` overrides the DSN, as in
`scripts/check-rule-sets-runnable.py`). Exit 0 prints `cross-dataset references: <n>`.
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


async def list_references(
    database: Any, workspace_id: UUID | None, *, out: TextIO, err: TextIO
) -> int:
    """Print one line per matching rule-set row and the count; the exit status (0)."""
    from sqlalchemy import select

    from app.db.models import DatasetVersionRow, ValidationRuleSetRow

    query = (
        select(ValidationRuleSetRow, DatasetVersionRow.dataset_id)
        .join(
            DatasetVersionRow,
            DatasetVersionRow.id == ValidationRuleSetRow.reference_dataset_version_id,
        )
        .where(DatasetVersionRow.dataset_id != ValidationRuleSetRow.dataset_id)
        .order_by(
            ValidationRuleSetRow.workspace_id,
            ValidationRuleSetRow.slug,
            ValidationRuleSetRow.version,
        )
    )
    if workspace_id is not None:
        query = query.where(ValidationRuleSetRow.workspace_id == workspace_id)
    count = 0
    async with database.session() as session:
        for row, reference_dataset_id in (await session.execute(query)).all():
            print(
                f"rule_set={row.id} workspace={row.workspace_id} dataset={row.dataset_id} "
                f"slug={row.slug} version={row.version} "
                f"reference_version={row.reference_dataset_version_id} "
                f"reference_dataset={reference_dataset_id}",
                file=out,
            )
            count += 1
    print(f"cross-dataset references: {count}", file=out)
    return 0


def _settings() -> Any:
    from pydantic import SecretStr

    from app.config import Environment, Settings

    return Settings(
        environment=Environment.LOCAL,
        database_url=SecretStr(os.environ.get("GIP_DATABASE_URL", DEFAULT_DSN)),
    )


async def _main(workspace_id: UUID | None) -> int:
    from app.db.session import Database

    database = Database(_settings())
    try:
        return await list_references(database, workspace_id, out=sys.stdout, err=sys.stderr)
    finally:
        await database.dispose()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise SystemExit("usage: list-cross-dataset-references.py [<workspace_id>]")
    raise SystemExit(asyncio.run(_main(UUID(sys.argv[1]) if len(sys.argv) == 2 else None)))
