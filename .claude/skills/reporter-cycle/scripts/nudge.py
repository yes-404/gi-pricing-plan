#!/usr/bin/env python3
"""Detect a stale lead and signal (never send) a nudge.

This script only detects staleness and prints a signal string. Sending the actual nudge is
the reporter agent's own job, done with `SendMessage` per `.claude/roles/reporter.md`'s
"Mechanism" section — a plain script has no such tool, so it cannot send the nudge itself.

Multi-signal liveness (2026-09-01): a single-signal version of this check — the
`.last_lead_status_ts` marker alone — fired a false positive while the lead was, in the
same window, merging PRs, restarting executors and dispatching roles. The marker records
when the lead last *talked to the reporter*, which is not the same thing as whether the
lead is alive, and an alarm that fires hardest when the lead is busiest gets ignored — the
real failure, worse than any one false positive, is the credibility loss that follows.

This now checks THREE independent liveness signals and nudges only when every one of them
is stale:

    1. The marker file `.last_lead_status_ts` (original behaviour).
    2. `eta.md`'s `**Updated:**` stamp — lead-owned, parsed by `reporter.get_eta_updated`
       (reused, not reimplemented — see that function's docstring).
    3. `origin/main`'s newest local commit timestamp — the lead holds sole merge authority,
       so a recent merge is direct evidence of life. Read from the LOCAL ref
       (`git log -1 --format=%ct origin/main`), never fetched here: a monitor that blocks
       on the network is a monitor that can itself stop. Advancing that local ref is
       someone else's job (`reporter.py`'s own comments cover why `git fetch` is not run
       casually in this handover directory); this script only reads whatever is already
       there.

The 20-minute default threshold is unchanged — this fixes what counts as evidence of life,
never how long the alarm waits before acting on it. Widening the window would hide the same
defect behind a longer fuse instead of fixing it.

Configuration:
    REPORTER_HANDOVER_DIR   Required. Same directory reporter.py uses.
    REPORTER_REPO_DIR       Optional. Repo checkout to read `origin/main` from locally.
                            Default: cwd. Same variable and default as reporter.py's.
    REPORTER_STALE_SECONDS  Optional. Staleness threshold. Default: 1200 (20 minutes) —
                            see ../SKILL.md "Why 20 minutes" for the rationale.
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# reporter.py lives alongside this file; running `python3 nudge.py` puts this file's own
# directory at sys.path[0] automatically, so this import needs no path manipulation (unlike
# the test suite, which lives one directory down and inserts the path itself).
from reporter import get_eta_updated

DEFAULT_STALE_SECONDS = 20 * 60


def _handover_dir() -> Path:
    value = os.environ.get("REPORTER_HANDOVER_DIR")
    if not value:
        print("ERROR: REPORTER_HANDOVER_DIR is not set — see SKILL.md", file=sys.stderr)
        sys.exit(2)
    return Path(value)


def _repo_dir() -> Path:
    return Path(os.environ.get("REPORTER_REPO_DIR", str(Path.cwd())))


def _stale_threshold_seconds() -> int:
    return int(os.environ.get("REPORTER_STALE_SECONDS", str(DEFAULT_STALE_SECONDS)))


def get_last_status_timestamp(status_ts_file: Path) -> float | None:
    """Read the marker file: a bare Unix timestamp, one line, no other format."""
    try:
        return float(status_ts_file.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def marker_age_seconds(status_ts_file: Path, now: datetime) -> float | None:
    """Age of the `.last_lead_status_ts` marker, or `None` if it is missing/unparseable."""
    last_ts = get_last_status_timestamp(status_ts_file)
    if last_ts is None:
        return None
    return now.timestamp() - last_ts


def eta_age_seconds(eta_file: Path, now: datetime) -> float | None:
    """Age of eta.md's `**Updated:**` stamp, or `None` if missing/unreadable/unparseable.

    Uses `reporter.get_eta_updated` — the same parser `get_eta` itself calls — rather than
    a second regex against the same file. A shape (here, a stamp format) parsed twice
    diverges; CLAUDE.md §2 states this for API shapes and the same reasoning applies to a
    file format two scripts both need to read.
    """
    updated = get_eta_updated(eta_file)
    if updated is None:
        return None
    return (now - updated).total_seconds()


def main_commit_age_seconds(repo_dir: Path, now: datetime) -> float | None:
    """Age of `origin/main`'s newest commit, read from the LOCAL ref only.

    Deliberately `git log -1 --format=%ct origin/main`, never a fetch: constraint from the
    dispatch that introduced this check was explicit — a monitor that blocks on the network
    is a monitor that stops. This reads whatever `origin/main` already points at in this
    checkout; keeping that ref current is `reporter.py`'s concern (it fetches only after
    confirming, via `git ls-remote`, that the tip actually moved), not this script's.
    Returns `None` on any failure — no repo at `repo_dir`, no `origin/main` ref, a timeout,
    or unparseable output — rather than raising: a monitor script must never crash the loop
    that calls it.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "origin/main"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    try:
        commit_ts = float(result.stdout.strip())
    except ValueError:
        return None
    return now.timestamp() - commit_ts


def _is_stale(age_seconds: float | None, threshold_seconds: int) -> bool:
    """One signal's staleness. A missing/unparseable source (`None`) counts as stale.

    This is the deliberate direction required by constraint 2 of the dispatch that added
    the multi-signal check: a source that could not be read is not evidence the lead is
    alive, so it must never vote "fresh". If it did, the alarm would go silent the moment
    that one file (or, for the git signal, that one subprocess call) failed — an alarm
    failing into silence is the exact class of defect this repository keeps producing
    (see CLAUDE.md's constraint 2, dispatched 2026-09-01). Because the overall predicate
    (below) is a conjunction of ALL THREE signals, a missing source alone can never cause a
    nudge by itself — it can only fail to block one that the other two signals already
    justify.
    """
    return age_seconds is None or age_seconds > threshold_seconds


def lead_is_stale(
    marker_age: float | None,
    eta_age: float | None,
    main_age: float | None,
    threshold_seconds: int,
) -> bool:
    """Pure decision function: nudge only if EVERY liveness signal is stale.

    Equivalently: the freshest of the three signals is older than `threshold_seconds`. Any
    one signal at or under the threshold means the lead is alive by that evidence, so no
    nudge — this is what stopped today's false positive (a stale marker, 25.4 minutes old,
    while `origin/main` had six merges inside the same window).

    Takes ages rather than file paths so it can be unit-tested directly, without aging any
    real file or repository on disk — the timestamps themselves cannot be retroactively
    aged, which is the reason this function exists as a separate, seam-tested unit rather
    than being inlined into `check_and_nudge`.
    """
    return all(
        _is_stale(age, threshold_seconds) for age in (marker_age, eta_age, main_age)
    )


def log_nudge(
    nudge_log: Path,
    marker_age: float | None,
    eta_age: float | None,
    main_age: float | None,
    threshold_seconds: int,
) -> None:
    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    threshold_min = threshold_seconds / 60

    def _fmt(age: float | None) -> str:
        return "missing" if age is None else f"{age / 60:.1f} min"

    line = (
        f"{now} - nudge sent - marker {_fmt(marker_age)}, eta {_fmt(eta_age)}, "
        f"main {_fmt(main_age)} (all >{threshold_min} min threshold)\n"
    )
    with nudge_log.open("a") as handle:
        handle.write(line)


def check_and_nudge(
    handover_dir: Path,
    repo_dir: Path,
    nudge_log: Path,
    threshold_seconds: int,
    now: datetime | None = None,
) -> bool:
    """Compute all three signals against real sources and return True (and log) iff stale.

    `now` is injectable for tests; production callers (`main`, below) leave it `None` and
    get the real clock, read once so all three ages are measured against the same moment.
    """
    if now is None:
        now = datetime.now(UTC)

    marker_age = marker_age_seconds(handover_dir / ".last_lead_status_ts", now)
    eta_age = eta_age_seconds(handover_dir / "eta.md", now)
    main_age = main_commit_age_seconds(repo_dir, now)

    if not lead_is_stale(marker_age, eta_age, main_age, threshold_seconds):
        return False

    log_nudge(nudge_log, marker_age, eta_age, main_age, threshold_seconds)
    return True


def update_status_timestamp(status_ts_file: Path) -> None:
    """Called by the reporter agent itself when a fresh lead status arrives."""
    status_ts_file.write_text(str(datetime.now(UTC).timestamp()))


def main() -> int:
    handover_dir = _handover_dir()
    repo_dir = _repo_dir()
    nudge_log = handover_dir / "nudge.log"
    if check_and_nudge(handover_dir, repo_dir, nudge_log, _stale_threshold_seconds()):
        print("NUDGE_NEEDED")
    else:
        print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
