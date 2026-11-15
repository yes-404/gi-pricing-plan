"""service_accounts.created_by, backfilled from the creation audit event (#1843, FR-348)

`grant_role` refuses a grant to a Service Account the granter owns, so the account must
record who created it. The column is nullable on purpose: **NULL means the owner is
unknown, and the guard refuses on it** (deny by default).

The backfill reads each account's `service_account.created` audit event (workspace and
`entity_ref = service_account:<slug>@1`) and takes the actor's id. An account with no such
event keeps NULL. The upgrade prints how many rows the backfill leaves NULL.

Reversibility (FR-416): reversible with loss. `downgrade()` drops the column, and the
owners it holds, backfilled or recorded at creation, are lost with it. Nothing else is
touched. The audit events are append-only and stay, so a later upgrade derives each owner
again from its `service_account.created` event; an account with no such event comes back
NULL. NULL is refused by `grant_role`, so a lost owner makes an account unassignable, never
over-permitted.

Revision ID: a1d9e47c3b52
Revises: c3a8e51f7d20
Create Date: 2026-11-15 12:00:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1d9e47c3b52"
down_revision: str | None = "c3a8e51f7d20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_BACKFILL = """
UPDATE service_accounts s
SET created_by = (e.actor ->> 'id')::uuid
FROM audit_events e
WHERE s.created_by IS NULL
  AND e.workspace_id = s.workspace_id
  AND e.action = 'service_account.created'
  AND e.entity_ref = 'service_account:' || s.slug || '@1'
"""


def upgrade() -> None:
    op.add_column(
        "service_accounts",
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    bind = op.get_bind()
    bind.execute(sa.text(_BACKFILL))
    unknown = bind.execute(
        sa.text("SELECT count(*) FROM service_accounts WHERE created_by IS NULL")
    ).scalar_one()
    print(f"service_accounts.created_by backfill: {unknown} row(s) left NULL (owner unknown)")


def downgrade() -> None:
    op.drop_column("service_accounts", "created_by")
