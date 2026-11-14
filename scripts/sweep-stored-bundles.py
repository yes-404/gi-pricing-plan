#!/usr/bin/env python3
"""Read-only sweep of stored Rating Version bundles for a `control`-intent operand (FD-1495 B1).

    uv run python scripts/sweep-stored-bundles.py [--dsn DSN] [--workspace UUID]

Run it BEFORE upgrading to the build that refuses such a bundle at load (`load_bundle`,
`CONTROL_FACTOR_IN_RATEABLE_PATH`): it names every stored version that build will refuse, so an
operator knows which versions need a NEW version (a compiled version is never mutated).

Each version with a stored bundle gets both halves of the check:

* **load**: the stored Bundle through `load_bundle`, the exact call that will refuse it;
* **keys / gbm**: the version's pins re-resolved through `check_rateable_intent`, for the rate
  table keys and the GBM features a Bundle does not carry.

Output, in this order (a zero over an empty corpus is vacuous, so the denominators come first):

    versions: N            every Rating Version read
    with a bundle: M       those whose row names a bundle (a content hash)
    checked: K             those whose bundle was read and checked (M minus unreadable)
    OFFENDER <ref> status=<s> hash=<h> half=<load|keys> <refusal text>   (one per offender)
    UNREADABLE <ref> status=<s> hash=<h> <why>                           (one per version)
    unreadable: U
    offenders: J

Exit code: 0 = every version with a bundle was checked and none offends; 1 = an offender; 2 = a
version whose bundle could not be read (fail closed: an unchecked version is not a clean one;
wins over 1); 64 = usage. One read-only transaction; nothing is written.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Callable
from typing import Any, TextIO

from pricing_core.rating.compile import Bundle
from pricing_core.rating.runtime import load_bundle
from pricing_core.safe_error import CodedError

CODE = "CONTROL_FACTOR_IN_RATEABLE_PATH"

#: `intent_check(version_dict)` -> the refusal text for the keys / GBM half, or `None` (clean).
IntentCheck = Callable[[dict[str, Any]], "str | None"]


def _refusal(exc: CodedError) -> str | None:
    code, separator, text = str(exc).partition(": ")
    return text if separator and code == CODE else None


def sweep(
    versions: list[dict[str, Any]], out: TextIO, intent_check: IntentCheck | None = None
) -> int:
    """Print the report for `versions` to `out` and return the exit code.

    A version dict is `{slug, version, status, bundle_hash, bundle}`; `bundle` is the parsed
    Bundle JSON, or `None` when the row has none to read (`bundle_hash` None: never compiled,
    not counted; `bundle_hash` set: a hash with no readable bundle, UNREADABLE).
    """
    with_bundle = [v for v in versions if v["bundle_hash"] is not None or v["bundle"] is not None]
    offenders: list[str] = []
    unreadable: list[str] = []
    for each in with_bundle:
        where = f"{each['slug']}@{each['version']} status={each['status']}"
        row_hash = each["bundle_hash"]
        if each["bundle"] is None:
            unreadable.append(
                f"UNREADABLE {where} hash={row_hash} the bundle cannot be re-validated"
            )
            continue
        try:
            bundle = Bundle.model_validate(each["bundle"])
        except ValueError as exc:
            unreadable.append(
                f"UNREADABLE {where} hash={row_hash} not a Bundle ({type(exc).__name__})"
            )
            continue
        hit = None
        try:
            load_bundle(bundle)
        except CodedError as exc:
            text = _refusal(exc)
            if text is None:
                unreadable.append(
                    f"UNREADABLE {where} hash={row_hash} {str(exc).partition(':')[0]}"
                )
                continue
            hit = ("load", text)
        if hit is None and intent_check is not None:
            try:
                text = intent_check(each)
            except Exception as exc:
                unreadable.append(
                    f"UNREADABLE {where} hash={row_hash} re-resolution failed "
                    f"({type(exc).__name__})"
                )
                continue
            if text is not None:
                hit = ("keys", text)
        if hit is not None:
            offenders.append(f"OFFENDER {where} hash={row_hash} half={hit[0]} {hit[1]}")
    print(f"versions: {len(versions)}", file=out)
    print(f"with a bundle: {len(with_bundle)}", file=out)
    print(f"checked: {len(with_bundle) - len(unreadable)}", file=out)
    for line in (*offenders, *unreadable):
        print(line, file=out)
    print(f"unreadable: {len(unreadable)}", file=out)
    print(f"offenders: {len(offenders)}", file=out)
    return 2 if unreadable else (1 if offenders else 0)


async def _read_versions(dsn: str | None, workspace: str | None) -> list[dict[str, Any]]:
    """Every Rating Version (one workspace if named), in ONE read-only transaction."""
    import json
    from uuid import UUID

    from sqlalchemy import select, text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.config import Settings
    from app.db.models import BlobRow, RatingVersionRow
    from app.platform import rating_versions as rv
    from app.platform.blobs import BlobStore, to_ref
    from pricing_core.rating.compile import check_rateable_intent

    settings = Settings()
    engine = create_async_engine(dsn or settings.database_url.get_secret_value())
    store = BlobStore(settings)
    out: list[dict[str, Any]] = []
    try:
        async with async_sessionmaker(engine)() as session, session.begin():
            await session.execute(text("SET TRANSACTION READ ONLY"))
            query = select(RatingVersionRow).order_by(
                RatingVersionRow.workspace_id, RatingVersionRow.slug, RatingVersionRow.version
            )
            if workspace is not None:
                query = query.where(RatingVersionRow.workspace_id == UUID(workspace))
            for row in (await session.execute(query)).scalars():
                meta = row.bundle or {}
                parsed: dict[str, Any] | None = None
                blob = (
                    await session.get(BlobRow, meta["blob_sha256"])
                    if meta.get("blob_sha256")
                    else None
                )
                if blob is not None:
                    try:
                        parsed = json.loads(await store.read(to_ref(blob)))
                    except Exception:
                        parsed = {"unreadable": True}
                out.append(
                    {
                        "slug": row.slug,
                        "version": row.version,
                        "status": row.status,
                        "bundle_hash": meta.get("content_hash"),
                        "bundle": parsed,
                        "_row": row,
                        "_workspace_id": row.workspace_id,
                    }
                )
            # The keys / GBM half re-resolves pins through the same session, so it runs here.
            for each in out:
                row = each["_row"]
                version = rv.to_schema(row)
                each["_refusal"] = None
                if each["bundle"] is None or version.pins is None or version.algorithm_ref is None:
                    continue
                resolver = rv.WorkspaceResolver(session, each["_workspace_id"], store)
                try:
                    await check_rateable_intent(version, resolver)
                except CodedError as exc:
                    each["_refusal"] = _refusal(exc)
                    if each["_refusal"] is None:
                        each["_error"] = str(exc).partition(":")[0]
                except Exception as exc:
                    each["_error"] = type(exc).__name__
    finally:
        await engine.dispose()
    return out


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
    parser.add_argument("--dsn", help="a READ-ONLY database URL (default: the app's settings)")
    parser.add_argument("--workspace", help="one workspace id (default: all)")
    args = parser.parse_args(argv)
    versions = asyncio.run(_read_versions(args.dsn, args.workspace))

    def intent_check(each: dict[str, Any]) -> str | None:
        if "_error" in each:
            raise RuntimeError(each["_error"])
        refusal: str | None = each["_refusal"]
        return refusal

    return sweep(versions, sys.stdout, intent_check)


if __name__ == "__main__":
    sys.exit(_main())
