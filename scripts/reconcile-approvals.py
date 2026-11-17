#!/usr/bin/env python3
"""Reconcile every workspace's approved-state artifacts against its verified audit chain.

`06` FR-2163 (rules R1 to R5 in `backend/src/app/platform/reconcile.py`). **Detective and
read-only**: it reports after the fact, prevents no write, and opens every workspace in a
`READ ONLY` transaction, so it writes nothing, not even an Audit Event.

Run: `uv run python scripts/reconcile-approvals.py` (the `gipricing` database;
`GIP_DATABASE_URL` overrides the DSN, as in `scripts/reset-unbacked-rule-approvals.py`). Use a
read-only login where one exists; the application login is acceptable because the run only
reads.

Output: one JSON line per workspace, then one summary line.
`{"workspace_id", "chain": "intact"|"broken", "events_verified", "artifacts_checked",
"requests_checked", "mismatches": [{"rule", "ref", "detail", "legacy"}]}`.
A mismatch with `"legacy": true` has chain evidence only before the workspace's first
decision event that carries its ids (by sequence, never by timestamp); it is reported and
counted like any other.

Exit codes: **0** every chain verifies and nothing mismatches; **1** at least one mismatch
(legacy ones included); **2** a chain is broken, or the run could not complete. A broken
chain outranks a mismatch, and a broken workspace prints no rule output.
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sys
from collections.abc import Iterable
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend" / "src"))

#: The compose stack's DSN, used when `GIP_DATABASE_URL` is not set.
DEFAULT_DSN = "postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"

EXIT_CLEAN, EXIT_MISMATCH, EXIT_BROKEN = 0, 1, 2


def render(reports: Iterable[Any]) -> tuple[list[str], int]:
    """The output lines and the exit code for a run's per-workspace reports."""
    lines: list[str] = []
    broken = mismatched = 0
    total = 0
    for report in reports:
        total += 1
        if report.chain == "broken":
            broken += 1
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
    lines.append(
        json.dumps(
            {
                "summary": True,
                "workspaces": total,
                "chain_broken": broken,
                "workspaces_with_mismatches": mismatched,
            },
            sort_keys=True,
        )
    )
    return lines, EXIT_BROKEN if broken else EXIT_MISMATCH if mismatched else EXIT_CLEAN


def _settings() -> Any:
    from pydantic import SecretStr

    from app.config import Environment, Settings

    return Settings(
        environment=Environment.LOCAL,
        database_url=SecretStr(os.environ.get("GIP_DATABASE_URL", DEFAULT_DSN)),
    )


async def _run() -> list[Any]:
    from sqlalchemy import select, text

    from app.db.models import WorkspaceRow
    from app.db.session import Database
    from app.platform import reconcile

    database = Database(_settings())
    reports: list[Any] = []
    try:
        async with database.session() as session:
            await session.execute(text("SET TRANSACTION READ ONLY"))
            workspace_ids = list((await session.execute(select(WorkspaceRow.id))).scalars())
        for workspace_id in workspace_ids:
            async with database.session() as session:
                await session.execute(text("SET TRANSACTION READ ONLY"))
                reports.append(await reconcile.reconcile(session, workspace_id))
    finally:
        await database.dispose()
    return reports


def main() -> int:
    try:
        reports = asyncio.run(_run())
    except Exception as exc:  # the run could not complete: exit 2, never 1
        print(json.dumps({"error": type(exc).__name__, "detail": str(exc)}), file=sys.stderr)
        return EXIT_BROKEN
    lines, code = render(reports)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
