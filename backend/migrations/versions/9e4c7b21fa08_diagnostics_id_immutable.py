"""a fitted Model's diagnostics pointer cannot be repointed (`02` R2, FR-OVR-1)

`b2c3d4e5f6a7` froze a fitted Model's `fit_result`, `spec`, `spec_hash` and
`dataset_version_id`. It did not freeze `diagnostics_id`, and that column is the one an
approval actually rests on: `02` §4.8 makes `status >= fitted` imply a `diagnostics_id`,
`06`'s approver reads the diagnostics that pointer reaches, and a raw
`UPDATE models SET diagnostics_id = ...` swapped the evidence under an *approved* model
with the trigger raising nothing. The numbers were immutable; the reason to believe them
was not. FR-OVR-1 makes an Artifact immutable once it leaves `draft` — a pointer to the
evidence is part of the artifact, not metadata beside it.

The whole function is replaced rather than altered: PostgreSQL has no "add a clause to a
trigger function", so `CREATE OR REPLACE` with the full body is the only edit there is, and
`downgrade()` restores `b2c3d4e5f6a7`'s body character for character.

## Which ordering case holds, and why the plain guard is safe

**One `UPDATE`.** `app.platform.modelling.record_fit` writes the diagnostics row first,
flushes it to get its id, then assigns `fit_result`, `diagnostics_id`, `status` and
`job_id` onto the *same* ORM object and flushes once
(`backend/src/app/platform/modelling.py:793-797`). SQLAlchemy emits a single
`UPDATE models SET fit_result = ..., diagnostics_id = ..., status = 'fitted', job_id = ...`,
so at that statement `OLD.fit_result IS NULL` and the outer `IF` does not fire at all. The
legitimate first write never reaches the new condition.

That is not incidental — it is the write order two invariants force, and
`backend/tests/test_model_lifecycle.py`'s `_next_version_of` already records it: the CHECK
`status IN ('draft','archived') OR diagnostics_id IS NOT NULL` refuses a `fitted` row with
no pointer, and the diagnostics row needs the model's id before it can name one. So the
model lands at `draft` with no numbers, its diagnostics are written, and the fit result,
the pointer and the status move together. Writing `fit_result` first and the pointer second
was *already* refused by `b2c3d4e5f6a7`'s guard, because by then `OLD.fit_result` is not
null.

The condition is therefore the plain
`NEW.diagnostics_id IS DISTINCT FROM OLD.diagnostics_id`, freezing the pointer **once
fitted** — the same gate the other four columns sit behind — rather than the weaker
`OLD.diagnostics_id IS NOT NULL AND ...`, which freezes it once *set*. The weaker form would
have admitted a `fitted` row whose pointer was somehow still null acquiring one later, a
state the CHECK constraint already forbids; there is nothing for it to protect and one more
way through for it to leave open.

`status`, `flags`, `approval_request_id` and the rest stay writable. A model still has a
lifecycle after it is fitted; what it may not have is a different reason for its numbers.

Revision ID: 9e4c7b21fa08
Revises: 2b2e2a481fb1
Create Date: 2026-08-22 10:00:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "9e4c7b21fa08"
down_revision: str | None = "2b2e2a481fb1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: `b2c3d4e5f6a7`'s body plus `diagnostics_id`. The trigger itself is unchanged and is not
#: recreated: `CREATE OR REPLACE FUNCTION` swaps the body under the existing
#: `models_fit_immutable` trigger, which already points at this name.
FIT_IMMUTABLE_WITH_DIAGNOSTICS = """
CREATE OR REPLACE FUNCTION models_fit_immutable() RETURNS trigger AS $fn$
BEGIN
  IF OLD.fit_result IS NOT NULL THEN
    IF NEW.fit_result IS DISTINCT FROM OLD.fit_result
       OR NEW.spec IS DISTINCT FROM OLD.spec
       OR NEW.spec_hash IS DISTINCT FROM OLD.spec_hash
       OR NEW.dataset_version_id IS DISTINCT FROM OLD.dataset_version_id
       OR NEW.diagnostics_id IS DISTINCT FROM OLD.diagnostics_id THEN
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

#: `b2c3d4e5f6a7`'s body verbatim, for `downgrade()`. Kept as its own literal rather than
#: imported from that module: a migration states the shape it restores, so reading this file
#: is enough to know what a downgrade leaves behind.
FIT_IMMUTABLE_WITHOUT_DIAGNOSTICS = """
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


def upgrade() -> None:
    op.execute(FIT_IMMUTABLE_WITH_DIAGNOSTICS)


def downgrade() -> None:
    op.execute(FIT_IMMUTABLE_WITHOUT_DIAGNOSTICS)
