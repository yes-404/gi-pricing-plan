"""Declarative base and the naming convention Alembic depends on.

Without an explicit convention, PostgreSQL names constraints for you and Alembic then
generates migrations that cannot drop them by name — `op.drop_constraint(None, ...)`. The
convention has to be set before the first migration, because renaming constraints later is
itself a migration on every table.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

__all__ = ["NAMING_CONVENTION", "Base"]

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
