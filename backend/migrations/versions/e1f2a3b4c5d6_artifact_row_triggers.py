"""data: the row trigger six artifact tables were missing (`01` FR-DATA-47)

`a1b2c3d4e5f6` established that an artifact needs **two** layers. Layer 1 is
`GRANT SELECT, INSERT` / `REVOKE UPDATE, DELETE`, which stops the application role. Layer 2
is the trigger pair, which stops everything else — because revoking `UPDATE` from the
*owner* does nothing at all: ownership carries implicit privileges, and a migration, a
`psql` session or a restored dump all connect as the owner.

Six tables took layer 1 and part or none of layer 2. FR-DATA-47 was raised naming three of
them; measuring the same invariant across every table rather than re-reading the three found
three more:

| table | had | missing |
|---|---|---|
| `diagnostics` | grants | both triggers |
| `model_comparisons` | grants | both triggers |
| `transparency_artifacts` | grants | both triggers |
| `objective_certificates` | grants, `TRUNCATE` | the row trigger |
| `bandings` | grants, `TRUNCATE` | the row trigger |
| `groupings` | grants, `TRUNCATE` | the row trigger |

`bandings` and `groupings` are the sharpest of the six, because `c3d4e5f6a7b8` states the
protection in a comment — "so the rule survives a direct `UPDATE` from a psql session" — and
then creates only the `TRUNCATE` trigger. The claim has been in the tree since; nothing could
fail while it was untrue, which is what `backend/tests/test_artifact_immutability.py` now
fixes by deriving the table list from the grants instead of restating it.

`artifact_append_only()` already exists (`a1b2c3d4e5f6`); this migration only attaches it.
The grants are already correct on all six and are left alone — layer 1 was never the gap.

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-08-18 16:20:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: str | None = "d0e1f2a3b4c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Both triggers missing.
NO_TRIGGERS = ("diagnostics", "model_comparisons", "transparency_artifacts")
# `TRUNCATE` guarded, rows not.
TRUNCATE_ONLY = ("bandings", "groupings", "objective_certificates")


def upgrade() -> None:
    for table in NO_TRIGGERS + TRUNCATE_ONLY:
        op.execute(f"""
            CREATE TRIGGER {table}_no_modify
              BEFORE UPDATE OR DELETE ON {table}
              FOR EACH ROW EXECUTE FUNCTION artifact_append_only();
        """)
    # A row trigger does not fire on `TRUNCATE`, which is why the pair exists rather than
    # one trigger. The three above already carry this half.
    for table in NO_TRIGGERS:
        op.execute(f"""
            CREATE TRIGGER {table}_no_truncate
              BEFORE TRUNCATE ON {table}
              FOR EACH STATEMENT EXECUTE FUNCTION artifact_append_only();
        """)


def downgrade() -> None:
    for table in NO_TRIGGERS:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_truncate ON {table}")
    for table in NO_TRIGGERS + TRUNCATE_ONLY:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_modify ON {table}")
