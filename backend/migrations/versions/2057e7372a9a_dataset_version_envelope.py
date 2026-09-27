"""dataset_version_envelope

`DatasetVersion` catches up to its published contract (OQ-568, decided (c)): the
row gains the envelope's nine flat fields — `slug`, `description`, `created_by`,
`updated_at`, `archived_at`, `parent_id`, `labels`, `schema_version`, `currency` — so a
version serialises to a document that names its own provenance instead of borrowing it
from the dataset it belongs to.

The backfill answers four questions no other table can:

* **`slug`** — a version's slug is its dataset's slug (a version is addressed as
  `dataset-slug@version`), so it is copied from `datasets.slug` by `dataset_id`.
* **`created_by`** — the only record of who created an existing version is the audit
  chain, so it is read back out with the exact `entity_ref`
  (`dataset_version:{slug}@{version}`) and `action = 'dataset_version.created'`,
  ordered by the chain sequence so the earliest event wins. A version whose event is
  missing falls back to the workspace's earliest member. Rows that still have no creator
  after both stop the migration: `alter_column(nullable=False)` raises, and inventing a
  creator for a governed field is worse than a migration that refuses and says so — the
  same decision `82edffbe1dce` records for `datasets.owner_id`.
* **`parent_id`** — the previous version id within the same dataset, null on version 1
  (the `Model.parent_model_id` precedent).
* **`updated_at`** — a version is created and updated in the same moment (OQ-553,
  resolved (a)), so the honest backfill is `created_at`, not `now()`.
* **`source_fingerprint.extracted_at`** — OQ-568 (c) made the object form carry the
  extraction moment, and the moment a stored fingerprint was extracted is the moment its
  version was created. The backfill only touches fingerprints that lack the field, and the
  new ingestion code writes it from then on.

Revision ID: 2057e7372a9a
Revises: 57547846f0a3
Create Date: 2026-08-26 23:00:16.586237+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2057e7372a9a"
down_revision: str | None = "57547846f0a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


#: The backfills, each a single statement so the shadow-table tests can run the
#: migration's own SQL verbatim, one at a time (a multi-statement string cannot).
_BACKFILL_SLUG = """
UPDATE dataset_versions v SET slug = d.slug
  FROM datasets d
 WHERE d.id = v.dataset_id
   AND v.slug IS NULL
"""

_BACKFILL_PARENT_ID = """
UPDATE dataset_versions v SET parent_id = (
    SELECT p.id
      FROM dataset_versions p
     WHERE p.dataset_id = v.dataset_id
       AND p.version = v.version - 1
     LIMIT 1
)
"""

#: A version's creator, read back out of the audit chain. The `entity_ref` is matched
#: exactly — `new_version` writes `dataset_version:{slug}@{version}` — and the earliest
#: event wins, so a re-validation that records nothing does not displace the creator.
_BACKFILL_CREATED_BY = """
UPDATE dataset_versions v SET created_by = (
    SELECT (a.actor ->> 'id')::uuid
      FROM audit_events a
     WHERE a.workspace_id = v.workspace_id
       AND a.action = 'dataset_version.created'
       AND a.entity_ref = 'dataset_version:' || d.slug || '@' || v.version
       AND a.actor ->> 'id' IS NOT NULL
     ORDER BY a.sequence ASC
     LIMIT 1
)
FROM datasets d
WHERE d.id = v.dataset_id
  AND v.created_by IS NULL
"""

#: The fallback: the workspace's earliest member. Not every version's creation event
#: survived (the audit table predates the chain), and a version with no creator cannot be
#: serialised — the envelope requires the field.
_BACKFILL_CREATED_BY_FALLBACK = """
UPDATE dataset_versions v SET created_by = (
    SELECT m.user_id
      FROM workspace_members m
     WHERE m.workspace_id = v.workspace_id
     ORDER BY m.created_at ASC, m.id ASC
     LIMIT 1
)
WHERE v.created_by IS NULL
"""

_BACKFILL_UPDATED_AT = "UPDATE dataset_versions SET updated_at = created_at"

#: The extraction moment of a stored fingerprint is its version's creation moment; the
#: `?` guard leaves already-complete fingerprints alone.
_BACKFILL_SOURCE_FINGERPRINT = """
UPDATE dataset_versions SET source_fingerprint =
    source_fingerprint || jsonb_build_object('extracted_at', to_jsonb(created_at))
WHERE source_fingerprint IS NOT NULL
  AND NOT (source_fingerprint ? 'extracted_at')
"""

_BACKFILL_CURRENCY = """
UPDATE dataset_versions v SET currency = COALESCE(d.currency, 'GBP')
  FROM datasets d
 WHERE d.id = v.dataset_id
"""

_BACKFILL_LABELS = "UPDATE dataset_versions SET labels = '{}'::jsonb"

_BACKFILL_SCHEMA_VERSION = "UPDATE dataset_versions SET schema_version = 1"

#: In execution order. `_BACKFILL_PARENT_ID` must run before the non-null constraints are
#: set; the creator pair must run in this order (event first, member fallback second).
_BACKFILLS: tuple[str, ...] = (
    _BACKFILL_SLUG,
    _BACKFILL_PARENT_ID,
    _BACKFILL_CREATED_BY,
    _BACKFILL_CREATED_BY_FALLBACK,
    _BACKFILL_UPDATED_AT,
    _BACKFILL_SOURCE_FINGERPRINT,
    _BACKFILL_CURRENCY,
    _BACKFILL_LABELS,
    _BACKFILL_SCHEMA_VERSION,
)


def upgrade() -> None:
    op.add_column("dataset_versions", sa.Column("slug", sa.String(64), nullable=True))
    op.add_column("dataset_versions", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "dataset_versions",
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "dataset_versions",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "dataset_versions",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "dataset_versions",
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("dataset_versions", sa.Column("labels", postgresql.JSONB(), nullable=True))
    op.add_column("dataset_versions", sa.Column("schema_version", sa.Integer(), nullable=True))
    op.add_column("dataset_versions", sa.Column("currency", sa.String(3), nullable=True))

    for statement in _BACKFILLS:
        op.execute(statement)

    # The constraint, not the backfill, is the refusal: a row that still has no slug or
    # no creator stops here with PostgreSQL's own error naming the table.
    op.alter_column("dataset_versions", "slug", nullable=False)
    op.alter_column("dataset_versions", "created_by", nullable=False)
    op.alter_column(
        "dataset_versions",
        "updated_at",
        nullable=False,
        server_default=sa.text("now()"),
    )
    op.alter_column("dataset_versions", "labels", nullable=False)
    op.alter_column("dataset_versions", "schema_version", nullable=False)
    op.alter_column("dataset_versions", "currency", nullable=False)


def downgrade() -> None:
    op.drop_column("dataset_versions", "currency")
    op.drop_column("dataset_versions", "schema_version")
    op.drop_column("dataset_versions", "labels")
    op.drop_column("dataset_versions", "parent_id")
    op.drop_column("dataset_versions", "archived_at")
    op.drop_column("dataset_versions", "updated_at")
    op.drop_column("dataset_versions", "created_by")
    op.drop_column("dataset_versions", "description")
    op.drop_column("dataset_versions", "slug")
