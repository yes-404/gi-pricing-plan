"""artifacts are immutable in the database, not by convention (FR-43)

`01` FR-42 says a Validation Report is immutable and re-validation creates a new one.
Until this migration that was `frozen=True` on a Pydantic model — a rule about one process.
An independent audit rewrote **190 stored reports** from `fail` to `pass` in a single
statement, which is the whole gate `01` §1.3 describes, undone by one `UPDATE`.

Three tables become append-only on the pattern `audit_events` already uses (FR-370): a
row trigger for `UPDATE`/`DELETE`, a **statement** trigger for `TRUNCATE` because row
triggers do not fire on it, and privileges narrowed to `SELECT, INSERT` for the application
role.

`blobs` is deliberately **not** among them, and the requirement was corrected when this was
built rather than the table quietly dropped: `ref_count` changes on every reference and
release, and reference-counted GC deletes unreferenced rows. A blob's content is immutable
for a better reason than a trigger — the row is keyed by the sha256 of its own bytes — so
what it gets here is a guard that the content columns can never be updated, leaving the
lifecycle columns free.

Revision ID: a1b2c3d4e5f6
Revises: 55b2bea92837
Create Date: 2026-08-15 17:10:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "55b2bea92837"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"

#: The tables `01` FR-43 names. Each holds an artifact something else cites as
#: evidence: a report a version's `validated` status depends on, a profile a factor
#: workbench reads, an acknowledgement that let a warning through.
APPEND_ONLY = ("validation_reports", "profiles", "validation_acknowledgements")

APPEND_ONLY_FUNCTION = """
CREATE OR REPLACE FUNCTION artifact_append_only() RETURNS trigger AS $fn$
BEGIN
  RAISE EXCEPTION
    '% is append-only: % rejected (01 FR-42, FR-43)', TG_TABLE_NAME, TG_OP
    USING ERRCODE = 'insufficient_privilege',
          HINT = 'Artifacts are never rewritten. Produce a new one; the old one is evidence.';
END;
$fn$ LANGUAGE plpgsql;
"""

#: Content is what the digest addresses; `ref_count` and the timestamps are lifecycle.
BLOB_CONTENT_FUNCTION = """
CREATE OR REPLACE FUNCTION blobs_content_immutable() RETURNS trigger AS $fn$
BEGIN
  IF NEW.sha256 IS DISTINCT FROM OLD.sha256
     OR NEW.bytes IS DISTINCT FROM OLD.bytes
     OR NEW.media_type IS DISTINCT FROM OLD.media_type THEN
    RAISE EXCEPTION
      'a blob is addressed by the digest of its bytes: % cannot change', TG_OP
      USING ERRCODE = 'insufficient_privilege',
            HINT = 'Store new bytes as a new blob. ref_count may change; content may not.';
  END IF;
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.execute(APPEND_ONLY_FUNCTION)
    op.execute(BLOB_CONTENT_FUNCTION)

    for table in APPEND_ONLY:
        op.execute(f"""
            CREATE TRIGGER {table}_no_modify
              BEFORE UPDATE OR DELETE ON {table}
              FOR EACH ROW EXECUTE FUNCTION artifact_append_only();
        """)
        op.execute(f"""
            CREATE TRIGGER {table}_no_truncate
              BEFORE TRUNCATE ON {table}
              FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
        """)
        # Layer 1, as FR-370 does it: the application cannot even attempt the write.
        # Revoking from the *owner* does not work — ownership carries implicit privileges,
        # which is why the triggers above exist as well.
        op.execute(f"GRANT SELECT, INSERT ON {table} TO {APP_ROLE}")
        op.execute(f"REVOKE UPDATE, DELETE ON {table} FROM {APP_ROLE}")
        op.execute(f"REVOKE UPDATE, DELETE ON {table} FROM PUBLIC")

    op.execute("""
        CREATE TRIGGER blobs_content_immutable
          BEFORE UPDATE ON blobs
          FOR EACH ROW EXECUTE FUNCTION blobs_content_immutable();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS blobs_content_immutable ON blobs")
    for table in APPEND_ONLY:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_truncate ON {table}")
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_modify ON {table}")
        op.execute(f"GRANT UPDATE, DELETE ON {table} TO {APP_ROLE}")
    op.execute("DROP FUNCTION IF EXISTS blobs_content_immutable()")
    op.execute("DROP FUNCTION IF EXISTS artifact_append_only()")
