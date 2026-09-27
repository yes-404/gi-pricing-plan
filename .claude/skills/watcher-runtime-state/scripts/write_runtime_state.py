#!/usr/bin/env python3
"""Write and maintain the RFC-895 runtime state file (artifact B), per RL-907.

`docs/rulings/RL-00907-q4-artifacts-win-where-an-artifact-exists-and-nothing-that-blocks-an-action-may-be-counted-in-b-without-one.md`, RL-907, rejected the note's
original design (a state file the watcher writes and a mismatch detector compares
against artifact history) because that shape fails silently: if the writer dies or is
never wired up, the state file reads zero, the artifacts read zero, a mismatch detector
never fires, and every reader is told the process is healthy. So this script
**re-derives; it never compares two independently-kept tallies.**

Three things make the file it writes falsifiable rather than a second `roster-state.md`
(withdrawn as register finding F31 for publishing a fixed string with only its
timestamp updating):

1. **No file-level `updated_at`.** Each top-level section ("block") carries its own
   `written_by` / `written_at`, and a block whose derived content has not changed this
   cycle is left completely untouched -- not even its timestamp moves. This is what
   makes the acceptance test possible: a cycle in which nothing changed must produce a
   byte-identical file (see `tests/test_watcher_runtime_state.py`,
   `test_a_cycle_with_no_change_is_byte_identical`).
2. **No `retry_counters` block at all.** RL-907(c): a `0` from a counter nothing
   increments is indistinguishable from a true zero, and the hook that increments it
   (RFC-895 script C2) does not exist yet (adoption slice G). Absent, never zero.
3. **`in_flight_expensive_verifications` entries expire.** This block is genuinely
   underivable from any durable artifact -- it is ephemeral coordination state a role
   announces about itself (spec `docs/process/delivery-process.md` §8). Made
   falsifiable the other way: every entry carries `started_at` and a `ttl_seconds`, and
   an expired entry is pruned on the next cycle -- a reader never has to guess whether a
   stale entry means "still running" or "the announcer forgot to clear it".

`position.phase` / `.work` / `.slice` are **not auto-parsed from `docs/roadmap.md`**.
That file's "closed" convention (a struck-through `#` cell) is not applied consistently
across it -- WK-661, WK-664 and WK-671 are all closed in prose while their `#` cells are never
struck -- so a mechanical parser would confidently write a wrong answer some of the
time, which RL-907's own governing principle (a wrong derived value is worse than an
absent one) rules out. Instead the caller (the watcher cycle invocation) supplies the
value **and** the source it read it from; the field is written only when both are given,
and is otherwise left exactly as it was. `flow_step` is not supported at all -- Ruling
47(c): it has no source artifact, "carried only if slice E can name its source, and
dropped otherwise".

Usage:
    # Re-derive and write the state file (only touches blocks whose content changed):
    python3 write_runtime_state.py cycle \\
        [--phase VALUE --phase-source "docs/roadmap.md §7"] \\
        [--work VALUE --work-source "docs/roadmap.md §7"] \\
        [--slice VALUE --slice-source "docs/plans/2026-08-30-some-plan.md"]

    # A role announces an expensive verification it is about to start (spec §8):
    python3 write_runtime_state.py announce \\
        --what full_test_suite --by auditor --tree <sha> --ttl-seconds 1800

    # Show current state (for a role checking "is one already in flight" before
    # announcing its own, per spec §8):
    python3 write_runtime_state.py show

State file location: $RUNTIME_STATE_FILE, else ~/gi-pricing-plan.local/handover/
runtime-state.json. Outside the repository by design -- `docs/process/
delivery-process.md` §10 places runtime/ops state there, not under `docs/`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = "gi-pricing-plan-runtime-state"
SCHEMA_VERSION = 1
DEFAULT_STATE_FILE = Path.home() / "gi-pricing-plan.local" / "handover" / "runtime-state.json"
_TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _now() -> datetime:
    return datetime.now(UTC)


def _now_iso(now: datetime | None = None) -> str:
    return (now or _now()).strftime(_TS_FORMAT)


def _state_file_path(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    override = os.environ.get("RUNTIME_STATE_FILE")
    return Path(override) if override else DEFAULT_STATE_FILE


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        loaded: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError as exc:
        # Never silently discard evidence by overwriting a file we could not parse.
        raise SystemExit(
            f"runtime state file is not valid JSON, refusing to overwrite: {path} ({exc})"
        ) from exc
    return loaded


def _dump(doc: dict[str, Any]) -> str:
    return json.dumps(doc, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


def _prune_expired(entries: list[dict[str, Any]], now: datetime) -> list[dict[str, Any]]:
    kept = []
    for entry in entries:
        try:
            started = datetime.strptime(entry["started_at"], _TS_FORMAT).replace(
                tzinfo=UTC
            )
            ttl_seconds = int(entry["ttl_seconds"])
        except (KeyError, ValueError, TypeError):
            # An entry this script cannot read a TTL from cannot be trusted "in
            # flight" either -- drop it rather than carry forward something
            # unfalsifiable.
            continue
        if (now - started).total_seconds() <= ttl_seconds:
            kept.append(entry)
    return kept


def _position_block_content(
    existing_content: dict[str, Any],
    phase: str | None,
    phase_source: str | None,
    work: str | None,
    work_source: str | None,
    slice_: str | None,
    slice_source: str | None,
) -> dict[str, Any]:
    merged = dict(existing_content)
    if phase is not None:
        merged["phase"] = {"value": phase, "read_from": phase_source}
    if work is not None:
        merged["work"] = {"value": work, "read_from": work_source}
    if slice_ is not None:
        merged["slice"] = {"value": slice_, "read_from": slice_source}
    return merged


def _block_content(block: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in block.items() if k not in ("written_by", "written_at")}


def cycle(args: argparse.Namespace) -> int:
    path = _state_file_path(args.state_file)
    existing = _load(path)
    now = _now()
    now_iso = _now_iso(now)

    old_position_block = existing.get("position", {})
    new_position_content = _position_block_content(
        _block_content(old_position_block),
        args.phase,
        args.phase_source,
        args.work,
        args.work_source,
        args.slice,
        args.slice_source,
    )
    changed_blocks = []
    if "position" in existing and new_position_content == _block_content(old_position_block):
        new_position_block = old_position_block
    else:
        new_position_block = {
            "written_by": "watcher",
            "written_at": now_iso,
            **new_position_content,
        }
        changed_blocks.append("position")

    old_inflight_block = existing.get("in_flight_expensive_verifications", {})
    old_entries = old_inflight_block.get("entries", [])
    pruned_entries = _prune_expired(old_entries, now)
    if "in_flight_expensive_verifications" in existing and pruned_entries == old_entries:
        new_inflight_block = old_inflight_block
    else:
        new_inflight_block = {
            "written_by": "watcher",
            "written_at": now_iso,
            "entries": pruned_entries,
        }
        changed_blocks.append("in_flight_expensive_verifications")

    doc = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "project": "gi-pricing-plan",
        "position": new_position_block,
        "in_flight_expensive_verifications": new_inflight_block,
    }

    new_bytes = _dump(doc)
    old_bytes = path.read_text(encoding="utf-8") if path.exists() else None
    if new_bytes != old_bytes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_bytes, encoding="utf-8")
        print(f"runtime state written: {path} (blocks changed: {changed_blocks or ['none']})")
    else:
        print(f"runtime state unchanged: {path}")
    return 0


def announce(args: argparse.Namespace) -> int:
    path = _state_file_path(args.state_file)
    existing = _load(path)
    now = _now()
    now_iso = _now_iso(now)

    old_inflight_block = existing.get("in_flight_expensive_verifications", {})
    old_entries = old_inflight_block.get("entries", [])
    pruned = _prune_expired(old_entries, now)
    entry = {
        "what": args.what,
        "by": args.by,
        "tree": args.tree,
        "started_at": now_iso,
        "ttl_seconds": args.ttl_seconds,
    }
    new_inflight_block = {
        "written_by": "watcher",
        "written_at": now_iso,
        "entries": [*pruned, entry],
    }

    doc = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "project": "gi-pricing-plan",
        "position": existing.get("position", {}),
        "in_flight_expensive_verifications": new_inflight_block,
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_dump(doc), encoding="utf-8")
    print(f"announced: {json.dumps(entry)}")
    return 0


def show(args: argparse.Namespace) -> int:
    path = _state_file_path(args.state_file)
    existing = _load(path)
    if not existing:
        print(f"no runtime state file at {path}")
        return 0
    now = _now()
    live_entries = _prune_expired(
        existing.get("in_flight_expensive_verifications", {}).get("entries", []), now
    )
    print(_dump({**existing, "in_flight_expensive_verifications_live": live_entries}))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--state-file", default=None, help="Override RUNTIME_STATE_FILE / default path"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_cycle = sub.add_parser("cycle", help="Re-derive and write the state file")
    p_cycle.add_argument("--phase", default=None)
    p_cycle.add_argument("--phase-source", default=None)
    p_cycle.add_argument("--work", default=None)
    p_cycle.add_argument("--work-source", default=None)
    p_cycle.add_argument("--slice", default=None)
    p_cycle.add_argument("--slice-source", default=None)
    p_cycle.set_defaults(func=cycle)

    p_announce = sub.add_parser("announce", help="Announce an in-flight expensive verification")
    p_announce.add_argument("--what", required=True)
    p_announce.add_argument("--by", required=True)
    p_announce.add_argument("--tree", required=True)
    p_announce.add_argument("--ttl-seconds", required=True, type=int)
    p_announce.set_defaults(func=announce)

    p_show = sub.add_parser("show", help="Print current state, with expired entries pruned live")
    p_show.set_defaults(func=show)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
