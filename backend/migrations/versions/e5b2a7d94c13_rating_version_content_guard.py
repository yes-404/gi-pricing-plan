"""the database holds a rating version's content once it has left draft (#1907, PR-1)

`01` FR-44, `06` FR-351 (clauses of 2026-11-16); ADR-2157. Four changes, one revision:

* `rating_versions_content_guard()`, a `BEFORE UPDATE ... FOR EACH ROW` trigger. A row whose
  status is `draft` is free unless an approved approval request exists for its reference
  (`rating_version:<slug>@<version>`, same workspace): then no column and no status of it
  changes. A row in `draft` never moves to `approved` or `live`. A row in `review` may change only along the two transitions the
  application's own writers make (`review` to `approved`, `review` to `draft`), which touch
  `status` and `updated_at` and nothing else. Every other change, in every other status
  (`approved`, `live`, `retired`, or one the platform does not define), is refused with
  SQLSTATE `42501`; an update that changes nothing is allowed. The comparison is over the
  whole row as JSON, so a column added later is held without this function naming it.
* `approval_guard()` takes an optional fourth trigger argument, a comma list of statuses held
  like `approved`; `rating_versions` names `live,retired`, so those statuses need the decided
  approval request too.
* A CHECK that `rating_versions.status` is one of the five statuses the platform defines. The
  upgrade counts the rows outside them first, raises and rewrites nothing.
* `approval_requests_decision_guard()`: `status`, `decided_at` and `withdrawn_reason` of a
  request change only along the state machine's edges (`VALID_APPROVAL_TRANSITIONS`): from
  `review` to `approved`, `rejected` or `changes_requested` with `decided_at` set and no
  `withdrawn_reason`; from `review` to `withdrawn` with `decided_at` set and a non-empty
  `withdrawn_reason`; and from `approved` to `withdrawn` with `decided_at` unchanged and a
  non-empty `withdrawn_reason`. Every other change, in every status, is held.

Existing rows are not touched (the triggers fire on UPDATE). Reversible: the downgrade drops
the three additions and restores the earlier `approval_guard()` body and trigger.

Revision ID: e5b2a7d94c13
Revises: c3a8e51f7d20
Create Date: 2026-11-16 12:00:00.000000+00:00
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e5b2a7d94c13"
down_revision: str | None = "c3a8e51f7d20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SQLSTATE = "GP001"
#: The statuses the platform defines for a rating version (`model_schema.RatingVersionStatus`).
STATUSES = ("draft", "review", "approved", "live", "retired")
CHECK_NAME = "rating_version_status_is_in_the_lifecycle"

CONTENT_GUARD_FUNCTION = """
CREATE OR REPLACE FUNCTION rating_versions_content_guard() RETURNS trigger AS $fn$
BEGIN
  IF OLD.status = 'draft' THEN
    IF NEW.status IN ('approved', 'live') THEN
      RAISE EXCEPTION
        'a rating version does not move from draft to approved or live (01 FR-44)'
        USING ERRCODE = '42501',
              DETAIL = 'table=rating_versions id=' || OLD.id || ' status=' || OLD.status;
    END IF;
    IF NOT EXISTS (
      SELECT 1 FROM approval_requests r
      WHERE r.workspace_id = OLD.workspace_id
        AND r.status = 'approved'
        AND r.artifact_ref = 'rating_version:' || OLD.slug || '@' || OLD.version
    ) OR to_jsonb(NEW) = to_jsonb(OLD) THEN
      RETURN NEW;
    END IF;
    RAISE EXCEPTION
      'a draft whose reference has an approved request is held: it does not change (01 FR-44)'
      USING ERRCODE = '42501',
            DETAIL = 'table=rating_versions id=' || OLD.id || ' status=' || OLD.status;
  END IF;
  IF OLD.status = 'review' AND NEW.status IN ('approved', 'draft')
     AND (to_jsonb(NEW) - 'status' - 'updated_at') = (to_jsonb(OLD) - 'status' - 'updated_at') THEN
    RETURN NEW;
  END IF;
  IF to_jsonb(NEW) = to_jsonb(OLD) THEN
    RETURN NEW;
  END IF;
  RAISE EXCEPTION
    'a rating version past draft is held: its content does not change (01 FR-44)'
    USING ERRCODE = '42501',
          DETAIL = 'table=rating_versions id=' || OLD.id || ' status=' || OLD.status;
END;
$fn$ LANGUAGE plpgsql
"""

DECISION_GUARD_FUNCTION = """
CREATE OR REPLACE FUNCTION approval_requests_decision_guard() RETURNS trigger AS $fn$
BEGIN
  IF OLD.status = 'review'
     AND NEW.status IN ('approved', 'rejected', 'changes_requested')
     AND NEW.decided_at IS NOT NULL
     AND NEW.withdrawn_reason IS NULL THEN
    RETURN NEW;
  END IF;
  IF OLD.status = 'review'
     AND NEW.status = 'withdrawn'
     AND NEW.decided_at IS NOT NULL
     AND btrim(coalesce(NEW.withdrawn_reason, '')) <> '' THEN
    RETURN NEW;
  END IF;
  IF OLD.status = 'approved'
     AND NEW.status = 'withdrawn'
     AND NEW.decided_at IS NOT DISTINCT FROM OLD.decided_at
     AND btrim(coalesce(NEW.withdrawn_reason, '')) <> '' THEN
    RETURN NEW;
  END IF;
  IF NEW.status IS NOT DISTINCT FROM OLD.status
     AND NEW.decided_at IS NOT DISTINCT FROM OLD.decided_at
     AND NEW.withdrawn_reason IS NOT DISTINCT FROM OLD.withdrawn_reason THEN
    RETURN NEW;
  END IF;
  RAISE EXCEPTION
    'a decided approval request is held: its decision does not change (06 FR-351)'
    USING ERRCODE = '42501',
          DETAIL = 'table=approval_requests id=' || OLD.id || ' status=' || OLD.status;
END;
$fn$ LANGUAGE plpgsql
"""

_APPROVAL_GUARD_BODY = """
CREATE OR REPLACE FUNCTION approval_guard() RETURNS trigger AS $fn$
DECLARE
  artifact_type text := TG_ARGV[0];
  slug_column   text := TG_ARGV[1];
  mode          text := TG_ARGV[2];
  held_statuses text := COALESCE(TG_ARGV[3], '');
  flag_is_off   boolean := current_setting('app.approval_decision', true) IS DISTINCT FROM 'on';
  ref           text;
BEGIN
  IF NEW.status IS DISTINCT FROM 'approved'
     AND NOT (NEW.status = ANY (string_to_array(held_statuses, ','))) THEN
    RETURN NEW;
  END IF;
  IF mode = 'flag_only' THEN
    IF NOT flag_is_off THEN
      RETURN NEW;
    END IF;
  ELSE
    IF mode = 'flag' AND NOT flag_is_off THEN
      RETURN NEW;
    END IF;
    ref := artifact_type || ':' || (to_jsonb(NEW) ->> slug_column) || '@' || NEW.version;
    IF EXISTS (
      SELECT 1 FROM approval_requests r
      WHERE r.workspace_id = NEW.workspace_id
        AND r.status = 'approved'
        AND r.artifact_ref = ref
    ) THEN
      RETURN NEW;
    END IF;
  END IF;
  RAISE EXCEPTION
    'only the approval decision path may write approved (06 FR-351): % on % rejected', TG_OP, TG_TABLE_NAME
    USING ERRCODE = '__SQLSTATE__',
          DETAIL = 'table=' || TG_TABLE_NAME || ' ref=' || COALESCE(ref, to_jsonb(NEW) ->> 'id'),
          HINT = 'Approve through POST /api/v1/approvals/{id}/decide. An approved row needs a decided '
                 'approval request for its ref, or (approval_requests, and the validation tables '
                 'while they hold an allowance) the decision flag set by approval_decision().';
END;
$fn$ LANGUAGE plpgsql
""".replace("__SQLSTATE__", SQLSTATE)

#: The function as `a9f3c6d21b87` created it (no fourth argument), for the downgrade.
_APPROVAL_GUARD_BEFORE = """
CREATE OR REPLACE FUNCTION approval_guard() RETURNS trigger AS $fn$
DECLARE
  artifact_type text := TG_ARGV[0];
  slug_column   text := TG_ARGV[1];
  mode          text := TG_ARGV[2];
  flag_is_off   boolean := current_setting('app.approval_decision', true) IS DISTINCT FROM 'on';
  ref           text;
BEGIN
  IF NEW.status IS DISTINCT FROM 'approved' THEN
    RETURN NEW;
  END IF;
  IF mode = 'flag_only' THEN
    IF NOT flag_is_off THEN
      RETURN NEW;
    END IF;
  ELSE
    IF mode = 'flag' AND NOT flag_is_off THEN
      RETURN NEW;
    END IF;
    ref := artifact_type || ':' || (to_jsonb(NEW) ->> slug_column) || '@' || NEW.version;
    IF EXISTS (
      SELECT 1 FROM approval_requests r
      WHERE r.workspace_id = NEW.workspace_id
        AND r.status = 'approved'
        AND r.artifact_ref = ref
    ) THEN
      RETURN NEW;
    END IF;
  END IF;
  RAISE EXCEPTION
    'only the approval decision path may write approved (06 FR-351): % on % rejected', TG_OP, TG_TABLE_NAME
    USING ERRCODE = '__SQLSTATE__',
          DETAIL = 'table=' || TG_TABLE_NAME || ' ref=' || COALESCE(ref, to_jsonb(NEW) ->> 'id'),
          HINT = 'Approve through POST /api/v1/approvals/{id}/decide. An approved row needs a decided '
                 'approval request for its ref, or (approval_requests, and the validation tables '
                 'while they hold an allowance) the decision flag set by approval_decision().';
END;
$fn$ LANGUAGE plpgsql
""".replace("__SQLSTATE__", SQLSTATE)

_RV_TRIGGER = (
    "CREATE TRIGGER approval_guard BEFORE INSERT OR UPDATE OF status, workspace_id, slug, version "
    "ON rating_versions FOR EACH ROW EXECUTE FUNCTION approval_guard('rating_version', 'slug'{extra})"
)


def upgrade() -> None:
    known = ", ".join(f"'{s}'" for s in STATUSES)
    outside = (
        op.get_bind()
        .execute(sa.text(f"SELECT count(*) FROM rating_versions WHERE status NOT IN ({known})"))
        .scalar_one()
    )
    held_drafts = (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT v.workspace_id, 'rating_version:' || v.slug || '@' || v.version "
                "FROM rating_versions v WHERE v.status = 'draft' AND EXISTS ("
                "SELECT 1 FROM approval_requests r WHERE r.workspace_id = v.workspace_id "
                "AND r.status = 'approved' "
                "AND r.artifact_ref = 'rating_version:' || v.slug || '@' || v.version) "
                "ORDER BY 1, 2"
            )
        )
        .all()
    )
    for workspace_id, reference in held_drafts:
        logging.getLogger("alembic.runtime.migration").warning(
            "held draft: workspace %s, %s is a draft with an approved request; "
            "it is held and the upgrade does not stop",
            workspace_id,
            reference,
        )
    if outside:
        raise RuntimeError(
            f"{outside} rating_versions row(s) hold a status outside the lifecycle; "
            "nothing was rewritten and the CHECK was not added"
        )
    op.execute(_APPROVAL_GUARD_BODY)
    op.execute("DROP TRIGGER approval_guard ON rating_versions")
    op.execute(_RV_TRIGGER.format(extra=", '', 'live,retired'"))
    op.execute(
        f"ALTER TABLE rating_versions ADD CONSTRAINT {CHECK_NAME} CHECK (status IN ({known}))"
    )
    op.execute(CONTENT_GUARD_FUNCTION)
    op.execute(
        "CREATE TRIGGER rating_versions_content_guard BEFORE UPDATE ON rating_versions "
        "FOR EACH ROW EXECUTE FUNCTION rating_versions_content_guard()"
    )
    op.execute(DECISION_GUARD_FUNCTION)
    op.execute(
        "CREATE TRIGGER approval_requests_decision_guard "
        "BEFORE UPDATE OF status, decided_at, withdrawn_reason ON approval_requests "
        "FOR EACH ROW EXECUTE FUNCTION approval_requests_decision_guard()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS approval_requests_decision_guard ON approval_requests")
    op.execute("DROP FUNCTION IF EXISTS approval_requests_decision_guard()")
    op.execute("DROP TRIGGER IF EXISTS rating_versions_content_guard ON rating_versions")
    op.execute("DROP FUNCTION IF EXISTS rating_versions_content_guard()")
    op.execute(f"ALTER TABLE rating_versions DROP CONSTRAINT IF EXISTS {CHECK_NAME}")
    op.execute("DROP TRIGGER approval_guard ON rating_versions")
    op.execute(_APPROVAL_GUARD_BEFORE)
    op.execute(_RV_TRIGGER.format(extra=""))
