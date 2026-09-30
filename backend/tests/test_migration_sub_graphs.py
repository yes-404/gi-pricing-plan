"""The `sub_graph_versions` table (WK-1250 Slice 1, FR-217, FR-417): the database itself
refuses a second version with the same address, and the table carries no mutable columns.
"""

from __future__ import annotations

from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db.models import SubGraphVersionRow
from app.db.session import Database
from model_schema import new_uuid7

pytestmark = pytest.mark.req("FR-217")


def _row(workspace_id: UUID, slug: str, version: int) -> SubGraphVersionRow:
    return SubGraphVersionRow(
        workspace_id=workspace_id,
        slug=slug,
        version=version,
        content={"steps": []},
        change_note="note",
        created_by=new_uuid7(),
    )


async def test_a_second_insert_of_the_same_address_is_refused_by_the_database(
    database: Database,
) -> None:
    workspace_id = new_uuid7()
    async with database.session() as session:
        session.add(_row(workspace_id, "ncd-ladder", 1))
        await session.flush()
        session.add(_row(workspace_id, "ncd-ladder", 1))
        with pytest.raises(IntegrityError, match="uq_sub_graph_versions_slug_version"):
            await session.flush()
        await session.rollback()


async def test_the_table_has_no_update_or_parent_column(database: Database) -> None:
    async with database.session() as session:
        columns = (
            await session.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'sub_graph_versions'"
                )
            )
        ).scalars().all()
    assert set(columns) == {
        "id", "workspace_id", "slug", "version", "content", "change_note",
        "created_at", "created_by",
    }
