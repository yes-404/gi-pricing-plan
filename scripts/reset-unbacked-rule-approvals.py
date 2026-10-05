#!/usr/bin/env python3
"""Return every approval that no approved approval request backs to `review`, audited.

FD-1356 follow-on 2, RL-1407 DP-6 (b). Before the fix a validation rule could reach
`approved` without a decided request. The population is FD-1356's follow-on predicate:
`validation_rules` rows with `status = 'approved'` and `builtin IS NOT TRUE` and no
`approval_requests` row with the same workspace, `artifact_type = 'validation_rule'`,
`artifact_ref = 'validation_rule:' || slug || '@' || version` and `status = 'approved'`.
Built-ins are `01` FR-68's exemption and are never touched.

Each row goes to `status = 'review'` with `approved_by` cleared, and one
`validation_rule.approval_reset` Audit Event is written through `audit.record`, so the
withdrawal carries the chain's own lock, sequence and hash. One unit of work covers the
database: a failure rolls it back and the script exits non-zero. Then
`audit.verify_chain` runs for every workspace written to, inside that unit of work, so a
broken chain rolls the resets back too.

Run: `uv run python scripts/reset-unbacked-rule-approvals.py` (the `gipricing` database;
`GIP_DATABASE_URL` overrides the DSN, as in `scripts/revalidate-artifacts.py`). No flags:
the read-only count is FD-1356's own script.
Output, one line: `<database> reset=<n> workspaces=<m> chain_verified=<m>`.
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
from typing import Any
from uuid import UUID

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend" / "src"))

#: The compose stack's DSN, used when `GIP_DATABASE_URL` is not set.
DEFAULT_DSN = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"

JUSTIFICATION = (
    "FD-1356 follow-on 2: approved outside the approval workflow; no approved approval "
    "request backs this approval (RL-1407 DP-6)."
)


async def reset(database: Any) -> dict[UUID, int]:
    """Reset the population and return the rows reset per workspace, chains verified."""
    from sqlalchemy import String, exists, select

    from app.db.models import ApprovalRequestRow, ValidationRuleRow
    from app.platform import audit
    from model_schema import ActorKind, JobSource, Principal

    actor = Principal(kind=ActorKind.SYSTEM, display="fd-1356-reset")
    reset_by_workspace: dict[UUID, int] = {}
    async with database.unit_of_work() as session:
        rows = (
            (
                await session.execute(
                    select(ValidationRuleRow)
                    .where(
                        ValidationRuleRow.status == "approved",
                        ValidationRuleRow.builtin.is_not(True),
                        ~exists().where(
                            ApprovalRequestRow.workspace_id == ValidationRuleRow.workspace_id,
                            ApprovalRequestRow.artifact_type == "validation_rule",
                            ApprovalRequestRow.artifact_ref
                            == "validation_rule:"
                            + ValidationRuleRow.slug
                            + "@"
                            + ValidationRuleRow.version.cast(String),
                            ApprovalRequestRow.status == "approved",
                        ),
                    )
                    .order_by(
                        ValidationRuleRow.workspace_id,
                        ValidationRuleRow.slug,
                        ValidationRuleRow.version,
                    )
                    .with_for_update(of=ValidationRuleRow)
                )
            )
            .scalars()
            .all()
        )
        for row in rows:
            approved_by = row.approved_by
            row.status = "review"
            row.approved_by = None
            await session.flush()
            await audit.record(
                session,
                workspace_id=row.workspace_id,
                actor=actor,
                source=JobSource.SYSTEM,
                action="validation_rule.approval_reset",
                entity_ref=f"validation_rule:{row.slug}@{row.version}",
                before={"status": "approved", "approved_by": str(approved_by)},
                after={"status": "review", "approved_by": None},
                justification=JUSTIFICATION,
            )
            reset_by_workspace[row.workspace_id] = reset_by_workspace.get(row.workspace_id, 0) + 1
        for workspace_id in reset_by_workspace:
            await audit.verify_chain(session, workspace_id)
    return reset_by_workspace


def _settings() -> Any:
    from pydantic import SecretStr

    from app.config import Environment, Settings

    return Settings(
        environment=Environment.LOCAL,
        database_url=SecretStr(os.environ.get("GIP_DATABASE_URL", DEFAULT_DSN)),
    )


async def _main() -> int:
    from sqlalchemy.engine import make_url

    from app.db.session import Database

    settings = _settings()
    database = Database(settings)
    try:
        by_workspace = await reset(database)
    finally:
        await database.dispose()
    name = make_url(settings.database_url.get_secret_value()).database
    workspaces = len(by_workspace)
    print(
        f"{name} reset={sum(by_workspace.values())} workspaces={workspaces} "
        f"chain_verified={workspaces}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
