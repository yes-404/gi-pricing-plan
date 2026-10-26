"""FR-395: a Workspace is a named, addressable entity rather than a bare column."""

from __future__ import annotations

import pytest
from backend.tests.conftest_db import seed_as_owner
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import WorkspaceMemberRow, WorkspaceRow
from app.db.session import Database
from model_schema import new_uuid7


@pytest.mark.req("FR-395")
async def test_a_workspace_row_carries_a_name_and_a_slug(database: Database) -> None:
    """Every surface that would show a workspace shows a UUID until this row exists."""
    workspace_id = new_uuid7()
    slug = f"ws-{workspace_id.hex[-10:]}"

    async def seed(session: AsyncSession) -> None:
        session.add(WorkspaceRow(id=workspace_id, slug=slug, name="Motor Pricing"))

    await seed_as_owner(seed)

    async with database.session() as session:
        row = await session.get(WorkspaceRow, workspace_id)
    assert row is not None
    assert row.name == "Motor Pricing"
    assert row.slug == slug
    assert row.created_at is not None


@pytest.mark.req("FR-395")
async def test_a_membership_cannot_name_a_workspace_that_does_not_exist(
    database: Database,
) -> None:
    """**Negative**, and the reason the backfill covers every table rather than this one.

    The foreign key is what makes a workspace addressable rather than conventionally
    referenced. Without it a membership row can name an id nothing describes, which is the
    state the whole schema was in before this slice.
    """

    async def seed(session: AsyncSession) -> None:
        session.add(WorkspaceMemberRow(user_id=new_uuid7(), workspace_id=new_uuid7()))

    # Owner session on purpose: the subject is the FK constraint, not the role. On the app
    # role this would fail earlier with "permission denied" and test the wrong thing.
    with pytest.raises(IntegrityError):
        await seed_as_owner(seed)
