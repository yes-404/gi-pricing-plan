"""scoring traces: index blob_sha256 for the blob route's quote-input refusal (#868)

`GET /api/v1/blobs/{sha256}` refuses any digest a quote-input store references (`07` §5.1,
amended 2026-09-28), so every download asks whether some scoring trace names the digest.
Without an index that is a sequential scan of the whole trace table, which grows by one row
per sampled quote. Measured on 100,000 rows: a seq scan of about 18 ms per download. This
index makes it an index probe (the deputy's ruling of 2026-09-28 18:55:39 BST, H2 (a)).

**Built `CONCURRENTLY`, outside the migration's transaction.** A plain `CREATE INDEX`
takes a lock that blocks writes to `scoring_traces` for the length of the build, and this
is a table the serving path writes on every sampled quote. `CREATE INDEX CONCURRENTLY`
cannot run inside a transaction block, so it runs in Alembic's `autocommit_block()`; the
downgrade drops it the same way. `if_not_exists` / `if_exists` make a re-run after an
interrupted concurrent build (which leaves an INVALID index behind) safe to repeat once the
invalid index is dropped by hand — PostgreSQL's documented recovery.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "02d24f580752"
down_revision: str | None = "fb705749c5d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_scoring_traces_blob_sha256",
            "scoring_traces",
            ["blob_sha256"],
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_scoring_traces_blob_sha256",
            table_name="scoring_traces",
            postgresql_concurrently=True,
            if_exists=True,
        )
