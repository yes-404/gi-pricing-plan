#!/usr/bin/env python3
"""Detect a stale lead status line and signal (never send) a nudge.

This script only detects staleness and prints a signal string. Sending the actual nudge is
the reporter agent's own job, done with `SendMessage` per `.claude/roles/reporter.md`'s
"Mechanism" section — a plain script has no such tool, so it cannot send the nudge itself.

Configuration:
    REPORTER_HANDOVER_DIR   Required. Same directory reporter.py uses.
    REPORTER_STALE_SECONDS  Optional. Staleness threshold. Default: 1200 (20 minutes) —
                            see ../SKILL.md "Why 20 minutes" for the rationale.
"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_STALE_SECONDS = 20 * 60


def _handover_dir() -> Path:
    value = os.environ.get("REPORTER_HANDOVER_DIR")
    if not value:
        print("ERROR: REPORTER_HANDOVER_DIR is not set — see SKILL.md", file=sys.stderr)
        sys.exit(2)
    return Path(value)


def _stale_threshold_seconds() -> int:
    return int(os.environ.get("REPORTER_STALE_SECONDS", str(DEFAULT_STALE_SECONDS)))


def get_last_status_timestamp(status_ts_file: Path) -> float | None:
    """Read the marker file: a bare Unix timestamp, one line, no other format."""
    try:
        return float(status_ts_file.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def check_and_nudge(status_ts_file: Path, nudge_log: Path, threshold_seconds: int) -> bool:
    """Return True (and log) if the lead's last status is older than the threshold."""
    last_ts = get_last_status_timestamp(status_ts_file)
    if last_ts is None:
        return False  # No status seen yet this session — nothing to compare against.

    age = datetime.now(UTC).timestamp() - last_ts
    if age <= threshold_seconds:
        return False

    log_nudge(nudge_log, age, threshold_seconds)
    return True


def log_nudge(nudge_log: Path, age_seconds: float, threshold_seconds: int) -> None:
    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    age_min = age_seconds / 60
    threshold_min = threshold_seconds / 60
    line = (
        f"{now} - nudge sent - lead status {age_min:.1f} min old "
        f"(>{threshold_min} min threshold)\n"
    )
    with nudge_log.open("a") as handle:
        handle.write(line)


def update_status_timestamp(status_ts_file: Path) -> None:
    """Called by the reporter agent itself when a fresh lead status arrives."""
    status_ts_file.write_text(str(datetime.now(UTC).timestamp()))


def main() -> int:
    handover_dir = _handover_dir()
    status_ts_file = handover_dir / ".last_lead_status_ts"
    nudge_log = handover_dir / "nudge.log"
    if check_and_nudge(status_ts_file, nudge_log, _stale_threshold_seconds()):
        print("NUDGE_NEEDED")
    else:
        print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
