#!/usr/bin/env python3
"""Post one routine team-status update to Slack.

Configuration is entirely by environment variable — this file is checked into the
repository and must not hardcode any one session's handover directory, token path, or
channel. See ../SKILL.md for the full mechanism and why each piece is shaped this way.

Required:
    REPORTER_HANDOVER_DIR   Absolute path to the current session's handover directory.

Optional (sensible defaults):
    REPORTER_TOKEN_PATH     Where the Slack token lives. Default: ~/.slack-token
    REPORTER_REPO_DIR       Repo checkout to run `gh pr list` from. Default: cwd.
    REPORTER_SLACK_CHANNEL  Slack channel ID to post to. Default: C0BSYRQ6NGM
                            (#claude-code-update).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_CHANNEL = "C0BSYRQ6NGM"  # #claude-code-update


def _handover_dir() -> Path:
    """Return the current session's handover directory, or exit loudly if unset.

    Unlike a missing token (below), a missing handover directory is a misconfiguration,
    not an expected transient outage — it means this script was invoked without being
    told where to read and write its own state, so failing loudly here is correct.
    """
    value = os.environ.get("REPORTER_HANDOVER_DIR")
    if not value:
        print("ERROR: REPORTER_HANDOVER_DIR is not set — see SKILL.md", file=sys.stderr)
        sys.exit(2)
    return Path(value)


def _token_path() -> Path:
    default = Path.home() / ".slack-token"
    return Path(os.environ.get("REPORTER_TOKEN_PATH", str(default)))


def _repo_dir() -> Path:
    return Path(os.environ.get("REPORTER_REPO_DIR", str(Path.cwd())))


def _channel() -> str:
    return os.environ.get("REPORTER_SLACK_CHANNEL", DEFAULT_CHANNEL)


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def get_token(handover_dir: Path, token_path: Path, log_path: Path) -> str | None:
    """Read the Slack token from its durable path.

    Exits silently (returns `None`) if the token is unavailable — a token outage is an
    expected, recoverable condition (rotation, a durable path not yet provisioned for a
    fresh session), not a bug, so the cycle must keep running rather than error out. The
    outage is logged exactly once via a flag file, never on every 15-minute retry, so a
    multi-hour outage does not fill the log with an identical line every cycle.
    """
    flag = handover_dir / ".token_outage_logged"
    try:
        return token_path.read_text().strip()
    except FileNotFoundError:
        if not flag.exists():
            _log_line(log_path, f"TOKEN OUTAGE START - path {token_path} not found")
            flag.touch()
        return None
    except OSError as exc:
        if not flag.exists():
            _log_line(log_path, f"TOKEN ERROR - {exc}")
            flag.touch()
        return None


def _log_line(log_path: Path, message: str) -> None:
    with log_path.open("a") as handle:
        handle.write(f"{_utc_now_iso()} - {message}\n")


def get_balance(balance_log: Path) -> tuple[str | None, str | None]:
    """Extract the most recent balance reading from the balance-heartbeat log."""
    try:
        lines = balance_log.read_text().splitlines()
    except FileNotFoundError:
        return None, None
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z).*?(\d+\.\d{2})\s*CNY")
    for line in reversed(lines):
        if "BALANCE HEARTBEAT:" not in line:
            continue
        match = pattern.search(line)
        if match:
            ts, balance = match.groups()
            return balance, ts
    return None, None


def get_roster(roster_file: Path) -> str | None:
    """Read the watcher's roster-state file, if one exists."""
    try:
        return roster_file.read_text()
    except FileNotFoundError:
        return None


def get_prs(repo_dir: Path) -> tuple[int, list[dict[str, object]]]:
    """List open PRs via `gh`, run from the given repo checkout."""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--json", "number,title"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=repo_dir,
            check=False,
        )
        if result.returncode != 0:
            return 0, []
        prs: list[dict[str, object]] = json.loads(result.stdout)
        return len(prs), prs
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"ERROR: gh pr list failed: {exc}", file=sys.stderr)
        return 0, []


def post_to_slack(token: str | None, text: str, channel: str) -> bool:
    """Post one message to Slack. `token` is read once by the caller, never logged."""
    if not token:
        print("ERROR: No Slack token", file=sys.stderr)
        return False
    payload = {"channel": channel, "text": text, "mrkdwn": True}
    try:
        result = subprocess.run(
            [
                "curl", "-s", "-X", "POST", "https://slack.com/api/chat.postMessage",
                "-H", f"Authorization: Bearer {token}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(payload),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        response = json.loads(result.stdout)
        ok = bool(response.get("ok", False))
        if not ok:
            print(f"Slack error: {response.get('error', 'unknown')}", file=sys.stderr)
        return ok
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"ERROR posting to Slack: {exc}", file=sys.stderr)
        return False


def format_routine_post(
    balance: str | None,
    balance_ts: str | None,
    pr_count: int,
    prs: list[dict[str, object]],
) -> str:
    """Format one routine status post. Content only — no token, no path, ever."""
    lines = []
    lines.append(f"*BALANCE:* {balance} CNY @ {balance_ts}" if balance else "*BALANCE:* unreported")
    if pr_count > 0:
        shown = ", ".join(f"#{pr['number']}" for pr in prs[:5])
        if pr_count > 5:
            shown += f" (+{pr_count - 5})"
        lines.append(f"*OPEN PRs:* {shown}")
    else:
        lines.append("*OPEN PRs:* none")
    return "\n".join(lines)


def main() -> int:
    """Run one reporter cycle. Exit 0 on a token outage — the cycle keeps running."""
    handover_dir = _handover_dir()
    log_path = handover_dir / "slack-reporter.log"

    token = get_token(handover_dir, _token_path(), log_path)
    if not token:
        return 0

    balance, balance_ts = get_balance(handover_dir / "balance-heartbeat.log")
    pr_count, prs = get_prs(_repo_dir())
    text = format_routine_post(balance, balance_ts, pr_count, prs)
    ok = post_to_slack(token, text, _channel())
    _log_line(log_path, f"routine post - ok={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
