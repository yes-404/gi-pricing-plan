"""Identity generation (`00` §ID-1).

> **ID-1** — Every entity has a `uuid` primary key (**UUIDv7**, time-ordered) plus a
> human-readable `slug` unique within its parent scope.

Time-ordering is not decoration. A random UUIDv4 primary key scatters inserts across the
whole B-tree, so every insert dirties a different page; a time-ordered key appends. On the
audit table — append-only, never updated, and the largest table in the system — that is the
difference between an index that stays in cache and one that does not.

`uuid7` is not in the standard library until 3.14, so it is implemented here rather than
taken as a dependency: it is thirty lines of bit-packing, and `model-schema` is the one
package whose dependency list is a contract (ADR-704).
"""

from __future__ import annotations

import os
import time
from uuid import UUID

__all__ = ["new_uuid7", "uuid7_timestamp_ms"]

_UNIX_TS_MS_BITS = 48
_VERSION = 7
_VARIANT_RFC4122 = 0b10


def new_uuid7(*, timestamp_ms: int | None = None) -> UUID:
    """Generate a UUIDv7: 48-bit millisecond timestamp, then 74 random bits.

    RFC 9562 §5.7 layout::

        unix_ts_ms (48) | ver (4) | rand_a (12) | var (2) | rand_b (62)

    Two ids generated in the same millisecond are ordered arbitrarily with respect to each
    other. That is acceptable everywhere it is used here: nothing derives ordering *within*
    a millisecond from the key. The audit chain establishes its own order through
    `prev_event_hash`, which is what makes it tamper-evident rather than merely sorted.
    """
    ts = int(time.time() * 1000) if timestamp_ms is None else timestamp_ms
    if not 0 <= ts < (1 << _UNIX_TS_MS_BITS):
        raise ValueError(f"timestamp_ms out of range for UUIDv7: {ts}")

    rand = int.from_bytes(os.urandom(10), "big")  # 80 bits, 74 of which are used
    rand_a = (rand >> 62) & 0xFFF
    rand_b = rand & ((1 << 62) - 1)

    value = ts << 80
    value |= _VERSION << 76
    value |= rand_a << 64
    value |= _VARIANT_RFC4122 << 62
    value |= rand_b
    return UUID(int=value)


def uuid7_timestamp_ms(value: UUID) -> int:
    """Recover the embedded millisecond timestamp from a UUIDv7.

    Useful for retention sweeps (FR-410 keeps job history ≥ 13 months): the age of a
    row is readable from its key without a column or an index.
    """
    if value.version != _VERSION:
        raise ValueError(f"not a UUIDv7 (version {value.version})")
    return value.int >> 80
