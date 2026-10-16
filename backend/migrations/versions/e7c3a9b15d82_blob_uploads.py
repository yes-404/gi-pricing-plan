"""blob uploads: the pending record of a presigned upload, and the blob.promote Job Kind

`07` §4.5, FR 8058, `RL-1724` (WK-1178, `SL-1722`). One row per Blob Upload, written when
`POST /api/v1/blobs/upload-url` issues the URLs: workspace, principal, staging key, the S3
multipart upload id (null for one part), the declared part count, the media type, the
completion deadline, the completing Job's id and the promoted digest (both null until set).
Also adds `blob.promote` to the `job_kind` enum, the `f3a7c1d9e2b4` pattern.

Revision ID: e7c3a9b15d82
Revises: d4e81b7a2c95
Create Date: 2026-10-16 09:00:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e7c3a9b15d82"
down_revision: str | None = "d4e81b7a2c95"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE job_kind ADD VALUE IF NOT EXISTS 'blob.promote' AFTER 'dataset.derive'")
    op.create_table(
        "blob_uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("s3_upload_id", sa.String(255), nullable=True),
        sa.Column("part_count", sa.Integer(), nullable=False),
        sa.Column("media_type", sa.String(255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("complete_by", sa.DateTime(timezone=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("digest", sa.String(64), nullable=True),
        sa.CheckConstraint(
            "part_count BETWEEN 1 AND 10000", name=op.f("ck_blob_uploads_part_count_in_range")
        ),
    )


def downgrade() -> None:
    # `job_kind` keeps `blob.promote`: PostgreSQL cannot drop an enum value, and a downgrade
    # that recreated the type would have to rewrite every `jobs` row to do it (FR-416).
    op.drop_table("blob_uploads")
