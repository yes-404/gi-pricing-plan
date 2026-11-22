#!/usr/bin/env python3
"""Reconcile every workspace's approved-state artifacts against its verified audit chain.

`06` FR-2163 (rules R1 to R5 in `backend/src/app/platform/reconcile.py`). **Detective and
read-only**: it reports after the fact, prevents no write, and opens every workspace in a
`READ ONLY` transaction, so it writes nothing, not even an Audit Event.

Run: `uv run python scripts/reconcile-approvals.py` (the `gipricing` database;
`GIP_DATABASE_URL` overrides the DSN, as in `scripts/reset-unbacked-rule-approvals.py`). Use a
read-only login where one exists; the application login is acceptable because the run only
reads.

The workspaces are the union of the `workspaces` table, `audit_events.workspace_id` and the
`workspace_id` of every governed table. An id with no `workspaces` row is reconciled like any
other, printed on its own extra line `{"workspace_id", "workspace_row": false, "detail"}`,
counted in the summary as `workspaces_without_row`, and makes the exit code 1 at least.

Output: one JSON line per workspace, then one summary line.
`{"workspace_id", "chain": "intact"|"broken"|"unreadable", "events_verified", "artifacts_checked",
"requests_checked", "mismatches": [{"rule", "ref", "detail", "legacy"}]}`.
A mismatch with `"legacy": true` has chain evidence only before the workspace's first
decision event that carries its ids (by sequence, never by timestamp); it is reported and
counted like any other.

Exit codes: **0** every chain verifies and nothing mismatches; **1** at least one mismatch
(legacy ones included) or at least one workspace id with no `workspaces` row; **2** a chain is
broken or unreadable (a stored row the models refuse: that workspace prints
`"chain": "unreadable"` and the run still prints every other workspace), or the run could not
complete. A broken or unreadable chain outranks a mismatch, and such a workspace prints no rule
output.
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sys
from collections.abc import Collection, Iterable
from typing import Any
from uuid import UUID

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend" / "src"))

#: The compose stack's DSN, used when `GIP_DATABASE_URL` is not set.
DEFAULT_DSN = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"

EXIT_CLEAN, EXIT_MISMATCH, EXIT_BROKEN = 0, 1, 2


def render(reports: Iterable[Any], without_row: Collection[UUID] = ()) -> tuple[list[str], int]:
    """The output lines and the exit code for a run's per-workspace reports.

    `without_row` is the ids that have no `workspaces` row: each gets its own line after the
    reports and is counted in the summary."""
    lines: list[str] = []
    broken = unreadable = mismatched = 0
    total = 0
    for report in reports:
        total += 1
        if report.chain == "broken":
            broken += 1
        elif report.chain == "unreadable":
            unreadable += 1
        elif report.mismatches:
            mismatched += 1
        lines.append(
            json.dumps(
                {
                    "workspace_id": str(report.workspace_id),
                    "chain": report.chain,
                    "events_verified": report.events_verified,
                    "artifacts_checked": report.artifacts_checked,
                    "requests_checked": report.requests_checked,
                    "mismatches": [
                        {"rule": m.rule, "ref": m.ref, "detail": m.detail, "legacy": m.legacy}
                        for m in report.mismatches
                    ],
                    **({"chain_detail": report.chain_detail} if report.chain_detail else {}),
                },
                sort_keys=True,
            )
        )
    for workspace_id in sorted(without_row, key=str):
        lines.append(
            json.dumps(
                {
                    "workspace_id": str(workspace_id),
                    "workspace_row": False,
                    "detail": "governed rows or audit events name this workspace; "
                    "no workspaces row does",
                },
                sort_keys=True,
            )
        )
    lines.append(
        json.dumps(
            {
                "summary": True,
                "workspaces": total,
                "workspaces_without_row": len(without_row),
                "chain_broken": broken,
                "chain_unreadable": unreadable,
                "workspaces_with_mismatches": mismatched,
            },
            sort_keys=True,
        )
    )
    return (
        lines,
        EXIT_BROKEN
        if broken or unreadable
        else EXIT_MISMATCH
        if mismatched or without_row
        else EXIT_CLEAN,
    )


def _settings() -> Any:
    from pydantic import SecretStr

    from app.config import Environment, Settings

    return Settings(
        environment=Environment.LOCAL,
        database_url=SecretStr(os.environ.get("GIP_DATABASE_URL", DEFAULT_DSN)),
    )


async def _run() -> tuple[list[Any], frozenset[UUID]]:
    from sqlalchemy import text

    from app.db.session import Database
    from app.platform import reconcile

    database = Database(_settings())
    reports: list[Any] = []
    try:
        async with database.session() as session:
            await session.execute(text("SET TRANSACTION READ ONLY"))
            workspace_ids, without_row = await reconcile.workspace_ids(session)
        for workspace_id in workspace_ids:
            async with database.session() as session:
                await session.execute(text("SET TRANSACTION READ ONLY"))
                reports.append(await reconcile.reconcile(session, workspace_id))
    finally:
        await database.dispose()
    return reports, without_row


def main() -> int:
    try:
        reports, without_row = asyncio.run(_run())
    except Exception as exc:  # the run could not complete: exit 2, never 1
        print(json.dumps({"error": type(exc).__name__, "detail": str(exc)}), file=sys.stderr)
        return EXIT_BROKEN
    lines, code = render(reports, without_row)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
