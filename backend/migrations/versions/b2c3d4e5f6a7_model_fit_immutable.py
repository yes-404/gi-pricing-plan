"""a fitted model's numbers cannot be rewritten (`02` R2)

`02` §1.3 R2 makes a Model immutable once fitted, and the service refuses a second
`record_fit`. That is a rule about one process. An audit rewrote a stored coefficient from
0.6931 to 0.0 with a raw `UPDATE`, and deleted a fitted model outright — one migration
after `a1b2c3d4e5f6` gave `validation_reports`, `profiles` and `validation_acknowledgements`
exactly this protection, and one table over.

`models` cannot be append-only: `record_fit` legitimately updates the row once, to write
the fit onto the reservation. So the guard is conditional — the shape `blobs` uses. Once
`fit_result` is set, the numbers, the spec and the digest are frozen; `status`, `flags` and
the rest stay writable, because a model still has a lifecycle after it is fitted.

Revision ID: b2c3d4e5f6a7
Revises: 3ab4db71d0e8
Create Date: 2026-08-15 19:40:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "3ab4db71d0e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"

FIT_IMMUTABLE = """
CREATE OR REPLACE FUNCTION models_fit_immutable() RETURNS trigger AS $fn$
BEGIN
  IF OLD.fit_result IS NOT NULL THEN
    IF NEW.fit_result IS DISTINCT FROM OLD.fit_result
       OR NEW.spec IS DISTINCT FROM OLD.spec
       OR NEW.spec_hash IS DISTINCT FROM OLD.spec_hash
       OR NEW.dataset_version_id IS DISTINCT FROM OLD.dataset_version_id THEN
      RAISE EXCEPTION
        'a fitted Model is immutable (02 R2): % rejected', TG_OP
        USING ERRCODE = 'insufficient_privilege',
              HINT = 'Refitting produces a new version with parent_model_id set. '
                     'A Rating Version pins a model version; rewriting one changes '
                     'what every quote priced on it was priced with.';
    END IF;
  END IF;
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""

#: The delete guard is separate: a fitted model is evidence, and `01`'s artifact tables
#: refuse deletion outright. An unfitted reservation may still be removed.
FIT_UNDELETABLE = """
CREATE OR REPLACE FUNCTION models_fitted_undeletable() RETURNS trigger AS $fn$
BEGIN
  IF OLD.fit_result IS NOT NULL THEN
    RAISE EXCEPTION
      'a fitted Model cannot be deleted (02 R2)'
      USING ERRCODE = 'insufficient_privilege',
            HINT = 'Archive it. Models fitted on it, and rating versions citing them, '
                   'reference this row by id.';
  END IF;
  RETURN OLD;
END;
$fn$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.execute(FIT_IMMUTABLE)
    op.execute(FIT_UNDELETABLE)
    op.execute("""
        CREATE TRIGGER models_fit_immutable
          BEFORE UPDATE ON models
          FOR EACH ROW EXECUTE FUNCTION models_fit_immutable();
    """)
    op.execute("""
        CREATE TRIGGER models_fitted_undeletable
          BEFORE DELETE ON models
          FOR EACH ROW EXECUTE FUNCTION models_fitted_undeletable();
    """)
    op.execute("""
        CREATE TRIGGER models_no_truncate
          BEFORE TRUNCATE ON models
          FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
    """)
    op.execute(f"GRANT SELECT, INSERT, UPDATE ON models, factors TO {APP_ROLE}")
    op.execute(f"REVOKE DELETE ON models FROM {APP_ROLE}")
    op.execute("REVOKE DELETE ON models FROM PUBLIC")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS models_no_truncate ON models")
    op.execute("DROP TRIGGER IF EXISTS models_fitted_undeletable ON models")
    op.execute("DROP TRIGGER IF EXISTS models_fit_immutable ON models")
    op.execute("DROP FUNCTION IF EXISTS models_fitted_undeletable()")
    op.execute("DROP FUNCTION IF EXISTS models_fit_immutable()")
    op.execute(f"GRANT DELETE ON models TO {APP_ROLE}")
