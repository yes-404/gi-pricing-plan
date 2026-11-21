"""blob GC definer function: the only DELETE path on `blobs`, owned by the owner role

WK-1251 slice 3b-1 (FR-420; #1504; #1550 option (c), the maintainer's amendment of 2026-11-15).
The application role holds no `DELETE` on `blobs` (OQ-1943) and gets none here. It gets `EXECUTE`
on `blob_gc_delete_unreferenced(p_cutoff)`, a `SECURITY DEFINER` function owned by the migrating
role (the owner of `blobs` and of every `BLOB_OWNERS` table). The re-checks are inside it, where no
caller can skip them. **Three statements in one body**, in this order:

1. lock the rows with `ref_count = 0` created before the cutoff, `SELECT … FOR UPDATE` (a concurrent
   `retain` is waited for and the count re-read);
2. a new `DELETE` of those rows that no owner place names, whose snapshot is taken after the locks;
3. a look, with a fresh snapshot and the locks still held, for an owner row that names a digest the
   `DELETE` just removed; if one exists the function raises `BLOB_GC_OWNER_APPEARED` and the whole
   run rolls back. This narrows, and does not close, the window for an owner writer that breaks the
   rule "every owner writer takes a reference" (#1855 (iv)).

The body is frozen here as a literal, not imported: a migration describes the schema as it was, and
one that imported the owner list would change its own body each time `BLOB_OWNERS` changes. A drift
test holds the function body equal to `app.platform.blobs.GC_FUNCTION_STATEMENTS`, so a later owner
added without a migration that `CREATE OR REPLACE`s this function fails the suite. A startup pin
holds the body's hash.

Hardening, each held by a test: `SET search_path = pg_catalog, public, pg_temp` (`pg_temp` last, so
a caller cannot shadow a table or operator with a temporary object); `REVOKE ALL ... FROM PUBLIC`
(PostgreSQL grants `EXECUTE` to `PUBLIC` on a new function by default); `EXECUTE` to `gip_app`
only, never to the login role directly (`b7e4c2a91d36`: "All grants go to `gip_app`"); no dynamic
SQL; and the **cutoff floor**: a cutoff younger than one day is refused, which is the
configuration's `blob_gc_grace_days >= 1` written where no caller can skip it.

Reversibility (FR-416): reversible. `downgrade()` drops the function. No data moves and no
privilege on any table changes; after a downgrade the collector has nothing to call and refuses
to run non-dry.

Revision ID: d5b9f20c8a14
Revises: c3a8e51f7d20
Create Date: 2026-11-16 10:00:00.000000+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d5b9f20c8a14"
down_revision: str | None = "c3a8e51f7d20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: One `SELECT` per owner place at this revision, one row per reference, in a column named
#: `sha256`. Frozen: the list `c3a8e51f7d20` froze, as `BLOB_OWNERS` stands at this slice.
_OWNERS: tuple[str, ...] = (
    "SELECT t->'blob'->>'sha256' AS sha256 FROM dataset_versions, jsonb_array_elements(tables) AS t",
    "SELECT result->>'ref' AS sha256 FROM jobs WHERE result->>'kind' = 'blob'",
    "SELECT sha256 FROM blob_uploads",
    "SELECT fit_result->'booster_blob'->>'sha256' AS sha256 FROM models",
    "SELECT fit_result->'covariance_blob'->>'sha256' AS sha256 FROM models",
    "SELECT cells->>'sha256' AS sha256 FROM rate_table_versions",
    "SELECT bundle->>'blob_sha256' AS sha256 FROM rating_versions",
    "SELECT evidence->>'structural_diff_blob' AS sha256 FROM rating_versions",
    "SELECT cases_blob_sha256 AS sha256 FROM regression_runs",
    "SELECT movers_blob_sha256 AS sha256 FROM dislocation_runs",
    "SELECT blob_sha256 AS sha256 FROM scoring_traces",
)

_OWNER_ROWS = " UNION ALL ".join(f"({owner})" for owner in _OWNERS)

#: The three statements, exactly `app.platform.blobs.GC_FUNCTION_STATEMENTS` at this revision.
_LOCK = (
    "SELECT coalesce(array_agg(l.sha256), ARRAY[]::text[]) INTO v_locked FROM "
    "(SELECT blobs.sha256::text AS sha256 FROM blobs "
    "WHERE blobs.ref_count = 0 AND blobs.created_at < p_cutoff FOR UPDATE) AS l"
)
_DELETE = (
    "WITH d AS (DELETE FROM blobs WHERE blobs.sha256 = ANY(v_locked) "
    "AND blobs.ref_count = 0 AND blobs.created_at < p_cutoff "
    f"AND NOT EXISTS (SELECT 1 FROM ({_OWNER_ROWS}) AS owned WHERE owned.sha256 = blobs.sha256) "
    "RETURNING blobs.sha256, blobs.bytes) "
    "SELECT coalesce(array_agg(d.sha256::text), ARRAY[]::text[]), "
    "coalesce(array_agg(d.bytes::bigint), ARRAY[]::bigint[]) INTO v_deleted, v_bytes FROM d"
)
_RECHECK = (
    f"SELECT EXISTS (SELECT 1 FROM ({_OWNER_ROWS}) AS owned WHERE owned.sha256 = ANY(v_deleted)) "
    "INTO v_appeared"
)

#: The function body, verbatim: PostgreSQL stores it as written, so `md5(prosrc)` of the migrated
#: function is `md5(_BODY)`, and the startup pin in `app.db.immutability` is that value.
_BODY = f"""
DECLARE
  v_locked text[];
  v_deleted text[];
  v_bytes bigint[];
  v_appeared boolean;
BEGIN
  IF p_cutoff IS NULL OR p_cutoff > now() - interval '1 day' THEN
    RAISE EXCEPTION 'BLOB_GC_CUTOFF_TOO_RECENT: cutoff % is inside the 1-day floor', p_cutoff
      USING ERRCODE = 'check_violation';
  END IF;
  {_LOCK};
  {_DELETE};
  {_RECHECK};
  IF v_appeared THEN
    RAISE EXCEPTION 'BLOB_GC_OWNER_APPEARED: an owner row names a digest this run deleted'
      USING ERRCODE = 'raise_exception';
  END IF;
  RETURN QUERY SELECT u.s, u.b FROM unnest(v_deleted, v_bytes) AS u(s, b);
END
"""

_SIGNATURE = "public.blob_gc_delete_unreferenced(timestamptz)"


def upgrade() -> None:
    # The OUT names differ from the column names (`sha256`, `bytes`), so PL/pgSQL never resolves a
    # column as a variable.
    op.execute(
        sa.text(
            "CREATE FUNCTION public.blob_gc_delete_unreferenced(p_cutoff timestamptz) "
            "RETURNS TABLE (deleted_sha256 text, deleted_bytes bigint) "
            "LANGUAGE plpgsql SECURITY DEFINER "
            "SET search_path = pg_catalog, public, pg_temp "
            f"AS $fn${_BODY}$fn$"
        )
    )
    op.execute(f"ALTER FUNCTION {_SIGNATURE} OWNER TO CURRENT_USER")
    op.execute(f"REVOKE ALL ON FUNCTION {_SIGNATURE} FROM PUBLIC")
    op.execute(f"GRANT EXECUTE ON FUNCTION {_SIGNATURE} TO gip_app")


def downgrade() -> None:
    op.execute(f"DROP FUNCTION {_SIGNATURE}")
