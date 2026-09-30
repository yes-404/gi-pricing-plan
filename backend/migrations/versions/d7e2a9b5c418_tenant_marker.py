"""tenant marker: the single-row binding of this database to one tenant (WK-674 Slice 1, PL-1239 Task 4)

`07` FR-436, ADR-710. One row, written here from `GIP_TENANT_ID`, refused a second by the
database (`smallint` key, `CHECK (id = 1)`). The application reads it at startup and
refuses to start when it disagrees with its configuration; it never writes it.

**This stamp trusts configuration.** Before this revision no database records its tenant,
so nothing exists to check the migrating process's `GIP_TENANT_ID` against. The id stamped
is printed so the operator sees it in the migration output; it is written once, so any later
drift is caught.

Revision ID: d7e2a9b5c418
Revises: c4d1e8a7b302
Create Date: 2026-09-29 23:50:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.config import load_settings

revision: str = "d7e2a9b5c418"
down_revision: str | None = "c4d1e8a7b302"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    tenant_id = load_settings().tenant_id
    op.create_table(
        "tenant_marker",
        sa.Column("id", sa.SmallInteger(), autoincrement=False, nullable=False),
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.CheckConstraint("id = 1", name=op.f("ck_tenant_marker_single_row")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tenant_marker")),
    )
    op.execute(
        sa.text("INSERT INTO tenant_marker (id, tenant_id) VALUES (1, :tenant_id)").bindparams(
            tenant_id=tenant_id
        )
    )
    print(f"tenant_marker: stamped tenant_id={tenant_id!r} (from GIP_TENANT_ID)")


def downgrade() -> None:
    op.drop_table("tenant_marker")
