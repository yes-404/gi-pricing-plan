"""the artifact tables append-only at the database (FD-1728, FD-1704; WK-1178 S-a, SL-1770)

`01` FR-43/FR-44 say an artifact cannot be rewritten and the database is what says so. Eleven
tables that hold artifacts something else cites as evidence had **neither layer**:
`factors` (it rode `models`' grant: `UPDATE` beside `models`, `b2c3d4e5f6a7:89`, and had no
trigger), and ten that `gip_app` holds nothing on and that carry no trigger at all
(`rate_tables`, `rate_table_versions`, `rate_table_cells`, `rating_algorithms`,
`sub_graph_versions`, `regression_suites`, `regression_suite_versions`, `reference_tables`,
`reference_table_versions`, `reference_rows`). A Model pins its Factors by row id, so an edited
`factors` row re-prices every pinned fitted Model with the pin unchanged.

What this adds (plan `PL-1769`, S-a, `DP-8` to `DP-13`, `DP-21`):

* **Nine tables are plain append-only** (`artifact_append_only()`, the pair form of
  `a1b2c3d4e5f6`): `factors`, `rate_table_cells`, `rate_table_versions`, `rating_algorithms`,
  `reference_rows`, `reference_tables`, `regression_suite_versions`, `regression_suites`,
  `sub_graph_versions`. Row trigger `<t>_no_modify`, statement trigger `<t>_no_truncate`.
* **Two are `guarded`** by a named column guard, each with the `TRUNCATE` trigger, because one
  legitimate in-place write exists (W1, W3): `rate_tables.current_version` moves forward (it is
  also the version allocator) and `reference_table_versions.status` goes `draft` to
  `published` (`01` FR-70's independent approval). Nothing else changes and no row goes.
* **Six tables that carry a row guard gain the `TRUNCATE` trigger they lacked** (plan review
  R2): `approval_requests`, `blobs`, `deployment_requests`, `rating_versions`,
  `validation_rule_sets`, `validation_rules`. A row trigger does not fire on `TRUNCATE`;
  `TRUNCATE rating_versions, <referencing tables>` emptied the approved price artifact.
* **`dataset_versions` is guarded** (DP-21, ruled by the maintainer (by delegation) "2026-10-14
  12:42:33 BST", refined "13:21:41", "13:27:39" and "2026-10-16 09:40:20"): "the immutable
  snapshot" of `CLAUDE.md` §7 has its data frozen from the first move into validation, for
  ever, FR-53's return to `draft` included. The new column `data_frozen_at` is that marker; the
  guard sets it, the application never does, and this migration back-fills it before the
  trigger exists.
* **Layer 1 for the ten** (DP-12): `SELECT, INSERT` for `gip_app`, column `UPDATE` on the two
  guarded tables, `UPDATE` and `DELETE` revoked from `PUBLIC` on all eleven and from `gip_app`
  on `factors`. **The grants are inert until SL-1771** (FD-1729): the application connects as
  the owner, which ownership lets past a privilege check, and the triggers are what refuse it.

**Reversibility (`07` FR-416 as amended by `OQ-1818`/D24).** Every statement here is a trigger,
a function, a grant or one nullable column. `downgrade()` drops them and restores the grants of
`b2c3d4e5f6a7` on `factors`; it never deletes, converts or rewrites a row. **Dropping the
triggers is data-safe and reversible**: no row of any table is touched in either direction.
This revision introduces no append-only artifact data of a *new kind* (it protects tables that
already exist), so it is not conditionally irreversible. `factors` may hold `expression`
Factors (`f2b6d90a4c17`, itself conditionally irreversible); dropping `factors_no_modify`
changes none of them. The only information dropped is `data_frozen_at`, which is derived: a
second `upgrade()` re-computes it from `status` and the audit chain by the same back-fill.

Revision ID: a4d1f08c3b97
Revises: f2b6d90a4c17
Create Date: 2026-10-18 23:10:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "a4d1f08c3b97"
down_revision: str | None = "f2b6d90a4c17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "gip_app"

#: No column changes, no row goes (`03` R1, FR-229; `01` FR-70; FD-1728, FD-1704).
APPEND_ONLY = (
    "factors",
    "rate_table_cells",
    "rate_table_versions",
    "rating_algorithms",
    "reference_rows",
    "reference_tables",
    "regression_suite_versions",
    "regression_suites",
    "sub_graph_versions",
)
#: Ten had no grant at all; `factors` had `UPDATE` beside `models` (`b2c3d4e5f6a7:89`).
NEWLY_GRANTED = (
    *(t for t in APPEND_ONLY if t != "factors"),
    "rate_tables",
    "reference_table_versions",
)
GUARDED = ("rate_tables", "reference_table_versions")
#: A row guard already, and no `TRUNCATE` half until now (plan review R2, 2026-10-14).
ROW_GUARDED = (
    "approval_requests",
    "blobs",
    "deployment_requests",
    "rating_versions",
    "validation_rule_sets",
    "validation_rules",
)

RATE_TABLES_GUARD = """
CREATE OR REPLACE FUNCTION rate_tables_pointer_only() RETURNS trigger AS $fn$
BEGIN
  IF TG_OP = 'DELETE'
     OR NEW.current_version <= OLD.current_version
     OR (to_jsonb(NEW) - 'current_version' - 'updated_at')
        IS DISTINCT FROM (to_jsonb(OLD) - 'current_version' - 'updated_at') THEN
    RAISE EXCEPTION
      'rate_tables: only current_version may change, and only forward: % rejected (03 FR-229)',
      TG_OP
      USING ERRCODE = 'insufficient_privilege',
            HINT = 'A rate table is edited by writing a new version, never by updating one.';
  END IF;
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""

REFERENCE_VERSIONS_GUARD = """
CREATE OR REPLACE FUNCTION reference_table_versions_publish_only() RETURNS trigger AS $fn$
BEGIN
  IF TG_OP = 'DELETE'
     OR NOT (OLD.status = 'draft' AND NEW.status = 'published')
     OR (to_jsonb(NEW) - 'status') IS DISTINCT FROM (to_jsonb(OLD) - 'status') THEN
    RAISE EXCEPTION
      'reference_table_versions: only draft -> published: % rejected (01 FR-70)', TG_OP
      USING ERRCODE = 'insufficient_privilege',
            HINT = 'A published reference table version is pinned by rating versions; add a new one.';
  END IF;
  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""

# -- dataset_versions (DP-21) ---------------------------------------------------------

#: `model_schema.datasets.VALID_DATASET_TRANSITIONS`, transcribed. A migration is a frozen
#: record of one revision and cannot import a table that may change; the pin test holds this
#: constant to the source exactly (`test_the_snapshot_guard_pins_the_transition_table`).
TRANSITIONS: dict[str, tuple[str, ...]] = {
    "draft": ("validating", "archived"),
    "validating": ("validated", "failed", "draft"),
    "validated": ("validating", "archived"),
    "failed": ("validating", "archived"),
    "archived": (),
}

#: The data the first validation freezes (the ruling: `tables`, schema, content-hash, row-count
#: and identity, plus the planner's provenance additions, ACKed "2026-10-14 15:14:52 BST" (A)).
FROZEN_DATA_COLUMNS = (
    "tables",
    "source_fingerprint",
    "totals",
    "derived_from",
    "library_versions",
    "ingestion_run_id",
)
#: Columns the application moves in place (census: 11) plus the freeze marker. Every OTHER
#: column is identity, compared as `to_jsonb(NEW) - ...` so a column added later is guarded by
#: default (DP-9's form).
MOVING_COLUMNS = (
    *FROZEN_DATA_COLUMNS,
    "status",
    "validation_report_id",
    "archived_at",
    "profile_id",
    "updated_at",
    "data_frozen_at",
)

#: Back-fill of `data_frozen_at`, run BEFORE the trigger exists. A row that is not `draft`
#: has been through validation; a `draft` row whose audit chain records a move to `validating`
#: is FR-53's return (`validating -> draft`). `datasets._transition` records
#: `dataset_version.<status>` against `dataset_version:<dataset slug>@<version>`.
BACK_FILL_SQL = """
UPDATE dataset_versions dv
   SET data_frozen_at = COALESCE(dv.updated_at, dv.created_at)
 WHERE dv.data_frozen_at IS NULL
   AND (dv.status <> 'draft'
        OR EXISTS (SELECT 1 FROM audit_events a
                    WHERE a.workspace_id = dv.workspace_id
                      AND a.action = 'dataset_version.validating'
                      AND a.entity_ref = 'dataset_version:' || dv.slug || '@' || dv.version))
"""


def _array(names: tuple[str, ...]) -> str:
    return "ARRAY[" + ", ".join(f"'{n}'" for n in names) + "]"


def _transition_values() -> str:
    return ", ".join(
        f"('{source}', '{target}')" for source, targets in TRANSITIONS.items() for target in targets
    )


def snapshot_guard_function() -> str:
    return f"""
CREATE OR REPLACE FUNCTION dataset_versions_snapshot_guard() RETURNS trigger AS $fn$
DECLARE
  col text;
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION
      'dataset_versions is an immutable snapshot: DELETE rejected (00 §2)'
      USING ERRCODE = 'insufficient_privilege',
            HINT = 'A Dataset Version is archived, never deleted; Models were fitted on it.';
  END IF;

  IF OLD.status = 'archived' THEN
    RAISE EXCEPTION
      'dataset_versions: an archived version takes no UPDATE (terminal state): UPDATE rejected (00 §2)'
      USING ERRCODE = 'insufficient_privilege';
  END IF;

  IF (to_jsonb(NEW) - {_array(MOVING_COLUMNS)}::text[])
     IS DISTINCT FROM (to_jsonb(OLD) - {_array(MOVING_COLUMNS)}::text[]) THEN
    RAISE EXCEPTION
      'dataset_versions: identity columns never change (state %): UPDATE rejected (00 §2)',
      OLD.status
      USING ERRCODE = 'insufficient_privilege';
  END IF;

  IF NEW.data_frozen_at IS DISTINCT FROM OLD.data_frozen_at AND OLD.data_frozen_at IS NOT NULL THEN
    RAISE EXCEPTION
      'dataset_versions: data_frozen_at is set once by this guard and never changed: UPDATE rejected (00 §2)'
      USING ERRCODE = 'insufficient_privilege';
  END IF;

  -- An UPDATE that leaves status unchanged is not a transition; the rules below still bind it.
  IF NEW.status IS DISTINCT FROM OLD.status AND NOT EXISTS (
       SELECT 1 FROM (VALUES {_transition_values()}) AS t(source, target)
        WHERE t.source = OLD.status AND t.target = NEW.status) THEN
    RAISE EXCEPTION
      'dataset_versions: status % -> % is not a valid transition (01 §4.2, 00 §2): UPDATE rejected',
      OLD.status, NEW.status
      USING ERRCODE = 'insufficient_privilege';
  END IF;

  -- The marker: set the first time the version leaves `draft` for validation, never again.
  IF OLD.data_frozen_at IS NULL AND NEW.status NOT IN ('draft', 'archived') THEN
    NEW.data_frozen_at := now();
  END IF;

  IF OLD.data_frozen_at IS NOT NULL THEN
    FOREACH col IN ARRAY {_array(FROZEN_DATA_COLUMNS)} LOOP
      IF to_jsonb(NEW) -> col IS DISTINCT FROM to_jsonb(OLD) -> col THEN
        RAISE EXCEPTION
          'dataset_versions: data-frozen since the first validation: % cannot change in state % (00 §2): UPDATE rejected',
          col, OLD.status
          USING ERRCODE = 'insufficient_privilege',
                HINT = 'Models were fitted on this data. Derive a new Dataset Version instead.';
      END IF;
    END LOOP;
  END IF;

  IF NEW.validation_report_id IS DISTINCT FROM OLD.validation_report_id
     AND NOT (OLD.status = 'validating' AND NEW.status <> 'validating') THEN
    RAISE EXCEPTION
      'dataset_versions: validation_report_id moves only out of validating, not in state % -> %: UPDATE rejected (00 §2)',
      OLD.status, NEW.status
      USING ERRCODE = 'insufficient_privilege';
  END IF;

  IF OLD.data_frozen_at IS NOT NULL AND OLD.profile_id IS NOT NULL
     AND NEW.profile_id IS DISTINCT FROM OLD.profile_id THEN
    RAISE EXCEPTION
      'dataset_versions: the profile of a data-frozen version is set once and never re-pointed (01 FR-60): UPDATE rejected'
      USING ERRCODE = 'insufficient_privilege';
  END IF;

  IF NEW.archived_at IS DISTINCT FROM OLD.archived_at
     AND NOT (OLD.archived_at IS NULL AND NEW.archived_at IS NOT NULL
              AND NEW.status = 'archived') THEN
    RAISE EXCEPTION
      'dataset_versions: archived_at is set only by the move to archived: UPDATE rejected (00 §2)'
      USING ERRCODE = 'insufficient_privilege';
  END IF;

  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    for table in APPEND_ONLY:
        op.execute(f"""
            CREATE TRIGGER {table}_no_modify
              BEFORE UPDATE OR DELETE ON {table}
              FOR EACH ROW EXECUTE FUNCTION artifact_append_only();
        """)
    op.execute(RATE_TABLES_GUARD)
    op.execute(REFERENCE_VERSIONS_GUARD)
    op.execute("""
        CREATE TRIGGER rate_tables_pointer_only
          BEFORE UPDATE OR DELETE ON rate_tables
          FOR EACH ROW EXECUTE FUNCTION rate_tables_pointer_only();
    """)
    op.execute("""
        CREATE TRIGGER reference_table_versions_publish_only
          BEFORE UPDATE OR DELETE ON reference_table_versions
          FOR EACH ROW EXECUTE FUNCTION reference_table_versions_publish_only();
    """)

    # dataset_versions: the marker column and its back-fill, then the guard (the guard's own
    # UPDATE rules would otherwise see the back-fill as a change to a frozen row).
    op.execute("ALTER TABLE dataset_versions ADD COLUMN data_frozen_at timestamptz NULL")
    op.execute(BACK_FILL_SQL)
    op.execute(snapshot_guard_function())
    op.execute("""
        CREATE TRIGGER dataset_versions_snapshot_guard
          BEFORE UPDATE OR DELETE ON dataset_versions
          FOR EACH ROW EXECUTE FUNCTION dataset_versions_snapshot_guard();
    """)

    # A row trigger does not fire on `TRUNCATE`, which is why every table also gets this.
    for table in (*APPEND_ONLY, *GUARDED, *ROW_GUARDED, "dataset_versions"):
        op.execute(f"""
            CREATE TRIGGER {table}_no_truncate
              BEFORE TRUNCATE ON {table}
              FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
        """)

    # Layer 1 (DP-12). Inert until SL-1771: the application connects as the owner (FD-1729).
    op.execute(f"REVOKE UPDATE, DELETE ON factors FROM {APP_ROLE}")
    for table in NEWLY_GRANTED:
        op.execute(f"GRANT SELECT, INSERT ON {table} TO {APP_ROLE}")
    op.execute(f"GRANT UPDATE (current_version, updated_at) ON rate_tables TO {APP_ROLE}")
    op.execute(f"GRANT UPDATE (status) ON reference_table_versions TO {APP_ROLE}")
    for table in (*APPEND_ONLY, *GUARDED):
        op.execute(f"REVOKE UPDATE, DELETE ON {table} FROM PUBLIC")


def downgrade() -> None:
    """Data-safe and reversible: triggers, functions, grants and one derived column."""
    for table in (*APPEND_ONLY, *GUARDED, *ROW_GUARDED, "dataset_versions"):
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_truncate ON {table}")
    op.execute("DROP TRIGGER IF EXISTS dataset_versions_snapshot_guard ON dataset_versions")
    op.execute("DROP FUNCTION IF EXISTS dataset_versions_snapshot_guard()")
    op.execute("ALTER TABLE dataset_versions DROP COLUMN IF EXISTS data_frozen_at")
    op.execute(
        "DROP TRIGGER IF EXISTS reference_table_versions_publish_only ON reference_table_versions"
    )
    op.execute("DROP TRIGGER IF EXISTS rate_tables_pointer_only ON rate_tables")
    for table in APPEND_ONLY:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_modify ON {table}")
    op.execute("DROP FUNCTION IF EXISTS reference_table_versions_publish_only()")
    op.execute("DROP FUNCTION IF EXISTS rate_tables_pointer_only()")
    op.execute(f"REVOKE UPDATE (status) ON reference_table_versions FROM {APP_ROLE}")
    op.execute(f"REVOKE UPDATE (current_version, updated_at) ON rate_tables FROM {APP_ROLE}")
    for table in NEWLY_GRANTED:
        op.execute(f"REVOKE SELECT, INSERT ON {table} FROM {APP_ROLE}")
    # Exactly `b2c3d4e5f6a7`'s state on `factors`: `UPDATE` granted, `DELETE` never was.
    op.execute(f"GRANT UPDATE ON factors TO {APP_ROLE}")
