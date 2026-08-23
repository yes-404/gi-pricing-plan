"""dataset owner

A Dataset gains an explicit, non-null `owner_id` (`01` FR-DATA-51). Ownership is a fact
about the container rather than a projection of its versions, so it is a column — unlike
FR-DATA-50's status and last-validated date, which are derived per request and stored
nowhere.

Revision ID: 82edffbe1dce
Revises: 9e4c7b21fa08
Create Date: 2026-08-23 11:28:43.137862+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "82edffbe1dce"
down_revision: str | None = "9e4c7b21fa08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


#: The only record of who created a pre-existing Dataset is the audit chain. `actor` is a
#: JSONB `Principal`, so the id comes out of it with `->>`, and the chain is ordered by
#: `sequence` — `at` has no defined order within a millisecond (`AuditEventRow`:198-201).
#:
#: **`@%` and not `@1`, deliberately.** `dataset.created` writes
#: `dataset:<slug>@1` in `platform/datasets.py:191`, but `:868` writes a *UUID* where the
#: rest write the slug and `dataset.dictionary_updated` (`:271`) omits `@version`
#: altogether. Those are pre-existing inconsistencies this migration must survive rather
#: than depend on; narrowing the pattern to `@1` would silently stop resolving rows the
#: day one of them is fixed. Recorded here so the next reader does not "tidy" it.
_BACKFILL = """
UPDATE datasets d SET owner_id = (
    SELECT (a.actor ->> 'id')::uuid
      FROM audit_events a
     WHERE a.workspace_id = d.workspace_id
       AND a.action = 'dataset.created'
       AND a.entity_ref LIKE 'dataset:' || d.slug || '@%'
       AND a.actor ->> 'id' IS NOT NULL
     ORDER BY a.sequence ASC
     LIMIT 1
)
WHERE d.owner_id IS NULL
"""


def upgrade() -> None:
    op.add_column(
        "datasets",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(_BACKFILL)
    # A row the backfill could not resolve stops here, and PostgreSQL's own error names
    # the table. That is deliberate: inventing an owner for a governed field is worse than
    # a migration that refuses and says so.
    op.alter_column("datasets", "owner_id", nullable=False)


def downgrade() -> None:
    op.drop_column("datasets", "owner_id")
