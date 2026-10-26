"""The start-up proof that the database's own immutability is intact (FR-44, FD-1729 part 2).

The artifact tables are append-only or guarded by **triggers**, and the triggers are only a
guard if the connecting role cannot take them away. Two things are therefore checked before
the process serves or consumes anything, on the connection it will run on:

1. **P-own.** The connecting role is not an owner of a table in `public`, not a superuser and
   not a role that bypasses row security -- directly or through any membership, `INHERIT FALSE`
   included. An owner can `DISABLE TRIGGER`; a superuser can `SET session_replication_role`.
2. **The triggers.** Every trigger the ORM declaration says a table carries (`_declared`, DP-8)
   exists, is enabled for every session (`tgenabled IN ('O', 'A')`), and runs a function whose body
   hashes to the pinned value. A trigger that was disabled, set to replica-only, dropped or
   given a `RETURN NEW` body is reported by table and trigger name.

Both are *detective* controls (`06` FR-372): the database cannot stop an owner tampering, it can
only make the tampering refuse the next start.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.base import Base

__all__ = [
    "PINNED_GUARD_FUNCTION_MD5",
    "P_OWN",
    "LeastPrivilegeError",
    "assert_least_privilege",
]


class LeastPrivilegeError(RuntimeError):
    """The database connection holds more power than the platform may run with."""


#: P-own: the roles `current_user` is a member of -- itself, directly or indirectly, `INHERIT
#: FALSE` memberships included (`'MEMBER'`, not `'USAGE'`, which an `INHERIT FALSE` membership
#: fails) -- that own a `public` table, are superusers, or bypass row security. One row per such
#: role; no rows is the only passing result. Defined once: tests import this constant.
P_OWN = text("""
    SELECT r.rolname
    FROM pg_roles r
    WHERE pg_has_role(current_user, r.oid, 'MEMBER')
      AND (
        r.rolsuper
        OR r.rolbypassrls
        OR EXISTS (
          SELECT 1 FROM pg_class c
          WHERE c.relowner = r.oid
            AND c.relnamespace = 'public'::regnamespace
            AND c.relkind IN ('r', 'p')
        )
      )
    ORDER BY r.rolname
""")

#: `md5(prosrc)` of every trigger function the migrations create, read from the head database
#: (never typed by hand; `test_the_pinned_guard_function_hashes_match_the_head`). A function the
#: declaration reaches that is absent here is refused as unpinned. The values are filled from a
#: throwaway migrated to head in S1b's DB window (LG-1947): an empty value never matches.
PINNED_GUARD_FUNCTION_MD5: dict[str, str] = {
    "approval_guard": "c4d56bfa76f12bfecba41b61975f1b65",
    "artifact_append_only": "c37e697febc245839b2672b90cf0b0ac",
    "audit_events_append_only": "1db7015bf61710795ac45ff15476fa06",
    "blobs_content_immutable": "73dbe02fec4b21b62649add0bea1e3d2",
    "custom_metrics_definition_immutable": "c6d3635fb58481053b519eba13b9e12c",
    "custom_metrics_undeletable": "2b0dd007c255ddcf2d0c4fea547d0140",
    "custom_objectives_definition_immutable": "d1632812ed74bd6752c02179f3aca414",
    "custom_objectives_undeletable": "ab2cbcacacd4f23e63344ac9e811176a",
    "dataset_versions_snapshot_guard": "3f3dd1ac44588b1f4c2e9d88154cb476",
    "models_fit_immutable": "1be27a4ea6ec706b7062b1dd1d1af3d5",
    "models_fitted_undeletable": "52df4a4825e7971dfdee640a6d1712fc",
    "peril_structures_composition_immutable": "53d6958a1db9583f458168c72da2e8f8",
    "peril_structures_reconciled_undeletable": "1e1dfaf61c4cb9240da81c7015b2c842",
    "rate_tables_pointer_only": "cd911971d3cf0d2e98a5e26397cb7843",
    "reference_table_versions_publish_only": "be3b2a9ff80fcc600e098725b7ff23c9",
}

#: `pg_trigger.tgenabled`: `O` (origin, the default) and `A` (`ENABLE ALWAYS`) both fire in a normal
#: session; `D` (disabled) and `R` (replica only) do not (PL-1769 Step 4.2).
_ENABLED_FOR_EVERY_SESSION = frozenset({"O", "A"})

_TRIGGERS = text("""
    SELECT c.relname AS tbl, t.tgname AS trigger, t.tgenabled::text AS enabled,
           p.proname AS function, md5(p.prosrc) AS body_md5
    FROM pg_trigger t
    JOIN pg_class c ON c.oid = t.tgrelid
    JOIN pg_proc p ON p.oid = t.tgfoid
    WHERE c.relnamespace = 'public'::regnamespace AND NOT t.tgisinternal
""")


def _declared(kind: str) -> tuple[str, ...]:
    """The tables whose ORM declaration says `kind` (DP-8): derived, never restated.

    Every mapped table declares `immutability` in `__table_args__` (`app/db/models.py`); a table
    that declares nothing fails `test_every_mapped_table_declares_its_immutability`. The set of
    tables Layer 1 locks is therefore read from where the table is written, and a new artifact
    table cannot be forgotten silently (FD-1728). It replaces the list that was written out in
    the tests, which had thirteen names and was why eleven artifact tables were missed.
    """
    # Imported here: `app.db.models` registers every table on `Base`, and this module must be
    # importable by `app.db.session` without that cost at import time.
    import app.db.models  # noqa: F401

    return tuple(
        sorted(t.name for t in Base.metadata.sorted_tables if t.info.get("immutability") == kind)
    )


def _expected_triggers() -> list[tuple[str, str]]:
    """`(table, trigger)` for every trigger the declaration says exists."""
    import app.db.models  # noqa: F401

    expected: list[tuple[str, str]] = []
    for table in Base.metadata.sorted_tables:
        kind = table.info.get("immutability")
        if kind == "append_only":
            expected += [(table.name, f"{table.name}_no_modify")]
        elif kind == "guarded":
            expected += [(table.name, guard) for guard in table.info["guards"]]
        else:
            continue
        expected.append((table.name, f"{table.name}_no_truncate"))
    return expected


async def assert_least_privilege(connection: AsyncConnection) -> None:
    """Raise `LeastPrivilegeError` unless `connection`'s role passes P-own and every declared
    trigger is present, enabled and unmodified. Reads only; changes nothing."""
    owners = [row[0] for row in (await connection.execute(P_OWN)).all()]
    if owners:
        raise LeastPrivilegeError(
            f"the database connection is, or is a member of, {owners}: a role that owns a table, "
            "is a superuser or bypasses row security can disable the immutability triggers. "
            "Connect as the application login role (scripts/provision-app-role.py)."
        )
    found = {(row.tbl, row.trigger): row for row in (await connection.execute(_TRIGGERS)).all()}
    for table, name in _expected_triggers():
        row = found.get((table, name))
        if row is None:
            raise LeastPrivilegeError(f"trigger {name} on {table} is missing (dropped?)")
        if row.enabled not in _ENABLED_FOR_EVERY_SESSION:
            raise LeastPrivilegeError(
                f"trigger {name} on {table} is not enabled for every session "
                f"(tgenabled={row.enabled!r})"
            )
        if PINNED_GUARD_FUNCTION_MD5.get(row.function) != row.body_md5:
            raise LeastPrivilegeError(
                f"trigger {name} on {table} runs {row.function}() whose body is not the pinned "
                "one (replaced, or not pinned)"
            )
