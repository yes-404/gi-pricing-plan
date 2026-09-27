"""modelling: bandings and groupings, and a versioned `spec_hash`

Three changes, one slice (`02` §3.2, §3.3).

* **`bandings` and `groupings`** — versioned artifacts with the same shape as `factors`,
  because FR-101 makes editing a banding a *new version* rather than an edit: a Model
  pins the version it was fitted with, and rewriting boundaries under a fitted model would
  change what it means without changing what it says. Both carry the artifact as JSONB;
  `model-schema` owns the shape (ADR-704).

* **`models.spec_hash` widens from 71 to 80.** The digest now carries the version of the
  algorithm that produced it — `v1:sha256:…` — so a stored digest from an older algorithm
  is findable rather than merely unmatchable (OQ-582's stated precondition). At 71 the
  first tagged digest would be silently truncated into a *different* valid-looking digest,
  which is the failure a length limit is least able to report.

* **Existing digests are left alone.** The version is inside the hashed payload as well as
  in front of it, so an old digest cannot be converted by prefixing it — `'v1:' || old` is
  not what the current code computes. Nothing here rewrites one. An untagged digest is not
  wrong, it is *unmatchable*: `spec_hash_is_current` says so, a resubmitted spec fits a new
  version rather than returning the old, and no row is silently mislabelled. A digest
  invented to look current would be the one failure this whole tag exists to prevent.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-15 22:15:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"


def upgrade() -> None:
    op.create_table(
        "bandings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("dataset_id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("column_name", sa.String(length=128), nullable=False),
        sa.Column("body", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "version >= 1", name=op.f("ck_bandings_banding_version_starts_at_one")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bandings")),
        sa.UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_bandings_slug_version"
        ),
    )
    op.create_index(
        "ix_bandings_dataset", "bandings", ["workspace_id", "dataset_id"], unique=False
    )

    op.create_table(
        "groupings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("dataset_id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("column_name", sa.String(length=128), nullable=False),
        sa.Column("parent_grouping_id", sa.UUID(), nullable=True),
        sa.Column("body", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "version >= 1", name=op.f("ck_groupings_grouping_version_starts_at_one")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groupings")),
        sa.UniqueConstraint(
            "workspace_id", "slug", "version", name="uq_groupings_slug_version"
        ),
    )
    op.create_index(
        "ix_groupings_dataset", "groupings", ["workspace_id", "dataset_id"], unique=False
    )

    op.alter_column(
        "models",
        "spec_hash",
        existing_type=sa.String(length=71),
        type_=sa.String(length=80),
        existing_nullable=False,
    )
    # `02` FR-101: a banding or grouping is versioned, never edited. Insert-only at the
    # privilege layer, so the rule survives a direct `UPDATE` from a psql session.
    op.execute(f"GRANT SELECT, INSERT ON bandings, groupings TO {APP_ROLE}")
    op.execute(f"REVOKE UPDATE, DELETE ON bandings, groupings FROM {APP_ROLE}")
    op.execute("REVOKE UPDATE, DELETE ON bandings, groupings FROM PUBLIC")
    for table in ("bandings", "groupings"):
        op.execute(f"""
            CREATE TRIGGER {table}_no_truncate
              BEFORE TRUNCATE ON {table}
              FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
        """)


def downgrade() -> None:
    for table in ("bandings", "groupings"):
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_truncate ON {table}")
    op.alter_column(
        "models",
        "spec_hash",
        existing_type=sa.String(length=80),
        type_=sa.String(length=71),
        existing_nullable=False,
    )
    op.drop_index("ix_groupings_dataset", table_name="groupings")
    op.drop_table("groupings")
    op.drop_index("ix_bandings_dataset", table_name="bandings")
    op.drop_table("bandings")
