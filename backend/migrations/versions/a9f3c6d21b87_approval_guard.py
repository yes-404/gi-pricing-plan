"""approval guard: only the decision path writes `approved` (WK-674 Slice 2a, PL-1303)

`06` FR-351, FR-354; RL-1301 A.4. One PL/pgSQL function, `approval_guard()`, installed as a
`BEFORE INSERT OR UPDATE OF status, workspace_id, <slug column>, version … FOR EACH ROW`
trigger on each of the 8 approval-capable tables. It refuses an `approved` row without its
evidence, whatever write form produced it (ORM, Core, raw SQL, bulk, a non-literal value, a
column default), because a list of forbidden write forms can never be complete and a
trigger sees them all.

**What it requires, by trigger argument** (`TG_ARGV` = artifact type, slug column, mode):

* no mode: an `approval_requests` row with the same `workspace_id`, `status = 'approved'`
  and `artifact_ref` equal to this row's ref — committed, or written earlier in the same
  transaction (`decide` flushes it before the carry). The flag never satisfies it;
* `flag`: that evidence **or** the decision flag (`validation_rules`,
  `validation_rule_sets`, while their named allowance sites exist; shrink-only);
* `flag_only`: the decision flag (`approval_requests` itself — its transition is behind
  `decide`'s own guards).

The flag is `SET LOCAL app.approval_decision = 'on'`, set by
`app.platform.approvals.approval_decision()`. It is compared `IS DISTINCT FROM 'on'`, never
`= ''` or `IS NULL`: once a session has set it the setting reads `''`, not NULL, after the
transaction ends. The ref is composed in SQL as `type:slug@version`, the format
`model_schema.ArtifactRef` renders; a test pins the two together.

`SQLSTATE GP001` is the refusal. `app.errors` maps it to one named problem.

Revision ID: a9f3c6d21b87
Revises: d7e2a9b5c418
Create Date: 2026-09-30 14:30:00+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "a9f3c6d21b87"
down_revision: str | None = "d7e2a9b5c418"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: The refusal's SQLSTATE. `app.errors.APPROVAL_GUARD_SQLSTATE` holds the same literal and a
#: test pins the two.
SQLSTATE = "GP001"

APPROVAL_GUARD_FUNCTION = f"""
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
    USING ERRCODE = '{SQLSTATE}',
          DETAIL = 'table=' || TG_TABLE_NAME || ' ref=' || COALESCE(ref, to_jsonb(NEW) ->> 'id'),
          HINT = 'Approve through POST /api/v1/approvals/{{id}}/decide. An approved row needs a decided '
                 'approval request for its ref, or (approval_requests, and the validation tables '
                 'while they hold an allowance) the decision flag set by approval_decision().';
END;
$fn$ LANGUAGE plpgsql
"""

#: table -> (trigger arguments, columns whose update re-checks the row). `models` names its
#: family column `model_family_slug` (`platform/modelling.py`); every other artifact table
#: says `slug`. Order is the order of the 8 existing approval tables in RL-1301 A.4.2.
GUARDED_TABLES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "models": (("model", "model_family_slug"), ("model_family_slug",)),
    "custom_metrics": (("custom_metric", "slug"), ("slug",)),
    "custom_objectives": (("custom_objective", "slug"), ("slug",)),
    "peril_structures": (("peril_structure", "slug"), ("slug",)),
    "rating_versions": (("rating_version", "slug"), ("slug",)),
    "validation_rules": (("validation_rule", "slug", "flag"), ("slug",)),
    "validation_rule_sets": (("validation_rule_set", "slug", "flag"), ("slug",)),
    "approval_requests": (("", "", "flag_only"), ()),
}


def create_trigger_sql(table: str) -> str:
    args, slug_columns = GUARDED_TABLES[table]
    # `version` is on every artifact table and not on `approval_requests`.
    columns = ["status", "workspace_id", *slug_columns, *(["version"] if slug_columns else [])]
    arg_list = ", ".join(f"'{a}'" for a in args)
    return (
        f"CREATE TRIGGER approval_guard BEFORE INSERT OR UPDATE OF {', '.join(columns)} "
        f"ON {table} FOR EACH ROW EXECUTE FUNCTION approval_guard({arg_list})"
    )


def upgrade() -> None:
    op.execute(APPROVAL_GUARD_FUNCTION)
    for table in GUARDED_TABLES:
        op.execute(create_trigger_sql(table))


def downgrade() -> None:
    for table in GUARDED_TABLES:
        op.execute(f"DROP TRIGGER IF EXISTS approval_guard ON {table}")
    op.execute("DROP FUNCTION IF EXISTS approval_guard()")
