#!/usr/bin/env python3
"""Post one routine team-status update to Slack.

Configuration is entirely by environment variable — this file is checked into the
repository and must not hardcode any one session's handover directory, token path, or
channel. See ../SKILL.md for the full mechanism and why each piece is shaped this way.

Required:
    REPORTER_HANDOVER_DIR   Absolute path to the current session's handover directory.

Optional (sensible defaults):
    REPORTER_TOKEN_PATH     Where the Slack token lives. Default: ~/.slack-token
    REPORTER_REPO_DIR       Repo checkout to run `gh pr list` and the `main`-tracking
                            git commands from. Default: cwd.
    REPORTER_SLACK_CHANNEL  Slack channel ID to post to. Default: C0BSYRQ6NGM
                            (#claude-code-update).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")

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
    """List open PRs via `gh`, run from the given repo checkout — with CI merge state."""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--json", "number,title,mergeStateStatus"],
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


def get_eta(eta_file: Path, now: datetime) -> tuple[str | None, bool | None]:
    """Read the lead-owned ETA file: the Headline paragraph, verbatim, and its staleness.

    The reporter never computes its own ETA — that judgement sits with the lead, and a
    number the reporter invented would be indistinguishable in Slack from one the lead
    stands behind. This only relays what `eta.md` already says. Maintainer instruction,
    2026-08-29.

    `now` is the current time in UTC, read once by the caller at the start of this cycle,
    so all staleness checks use the same moment. Drift between reading the clock and
    computing staleness is a source of false positives (stale flag set moments after a
    reading, wrong when reported minutes later). Maintainer instruction, 2026-08-30.

    Returns `(headline, stale)`. `headline` is `None` if the file is missing, unreadable,
    or has no parseable `**Headline:**` paragraph — the caller says so plainly rather than
    silently omitting the ETA section. `stale` is `True`/`False` once the `**Updated:**`
    stamp parses and is compared against `now`; it is `None` when a headline was found but
    the stamp was not, so the caller can say staleness is unknown instead of guessing.

    The stamp accepts two forms: a bare UTC `Z` suffix, or the GB-local form the lead's own
    `eta.md` header documents ("All times are GB local (BST, UTC+1)") and actually writes —
    `BST` or `GMT`. The GB-local forms are resolved via `zoneinfo.ZoneInfo("Europe/London")`
    rather than a hardcoded UTC+1, so a `GMT` (winter, UTC+0) stamp is not silently treated
    as if it were an hour ahead. Any other suffix — or no recognised suffix at all — is left
    unparsed (`stale=None`), never guessed.
    """
    try:
        text = eta_file.read_text()
    except OSError:
        return None, None

    # The label itself is not part of the content: it is only how this regex locates the
    # paragraph in eta.md (a label the lead's file always carries and that this file must
    # not ask the lead to drop). Capture the label separately so it can be excluded from
    # the returned text — the caller prefixes its own "*ETA:*" label, and returning this
    # one too doubled it in every historical post.
    headline_pattern = re.compile(
        r"^\*\*Headline:\*\*[ \t]*(.*?)(?=\n[ \t]*\n|\Z)", re.MULTILINE | re.DOTALL
    )
    headline_match = headline_pattern.search(text)
    if not headline_match:
        return None, None
    headline = headline_match.group(1).strip()

    updated_pattern = re.compile(
        r"^\*\*Updated:\*\*\s*(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})\s*(Z|BST|GMT)\b",
        re.MULTILINE,
    )
    updated_match = updated_pattern.search(text)
    if not updated_match:
        return headline, None
    try:
        naive = datetime.strptime(
            f"{updated_match.group(1)} {updated_match.group(2)}", "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return headline, None

    suffix = updated_match.group(3)
    updated = naive.replace(tzinfo=UTC) if suffix == "Z" else naive.replace(tzinfo=LONDON)

    return headline, (now - updated.astimezone(UTC)) > timedelta(hours=2)


def get_remote_main_sha(repo_dir: Path) -> str | None:
    """Ask the remote directly for main's current tip. Mutates no local ref.

    Deliberately `git ls-remote`, never `git log origin/main`: the latter reads this
    checkout's cached remote-tracking ref, which only advances when something in this
    checkout runs `git fetch`. A prior cycle read that cached ref and posted "git
    unchanged" a full 32 minutes after `origin/main` had actually moved — nothing was
    wrong with the comparison, the ref it compared against was just stale. `git ls-remote`
    asks the remote directly and moves nothing, which also matters because every worktree
    in this repository shares one `.git`, and a poller should not be moving refs other
    agents are reading. Maintainer instruction, 2026-08-29.
    """
    try:
        result = subprocess.run(
            ["git", "ls-remote", "origin", "refs/heads/main"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=repo_dir,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        return result.stdout.split()[0]
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: git ls-remote failed: {exc}", file=sys.stderr)
        return None


def get_merged_subjects(repo_dir: Path, last_sha: str, new_sha: str) -> list[str]:
    """List commits merged to main between two SHAs, as `git log --oneline` lines.

    Only called once `get_remote_main_sha` has already shown the tip moved: fetching
    mutates this checkout's remote-tracking ref, so it is deliberately not run every
    cycle — only here, once there is a known-good reason to move it.
    """
    try:
        subprocess.run(
            ["git", "fetch", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=20,
            cwd=repo_dir,
            check=False,
        )
        result = subprocess.run(
            ["git", "log", "--oneline", f"{last_sha}..{new_sha}"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=repo_dir,
            check=False,
        )
        if result.returncode != 0:
            return []
        return [line for line in result.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: git log failed: {exc}", file=sys.stderr)
        return []


def _last_sha_path(handover_dir: Path) -> Path:
    return handover_dir / ".last_reported_main_sha"


def get_last_reported_sha(handover_dir: Path) -> str | None:
    """Read the SHA of `main` as of the last successful routine post, if any."""
    try:
        value = _last_sha_path(handover_dir).read_text().strip()
    except FileNotFoundError:
        return None
    return value or None


def set_last_reported_sha(handover_dir: Path, sha: str) -> None:
    """Record the SHA just reported, so the next cycle diffs from here.

    Written only after a successful Slack post (see `main`) — if the post fails, the next
    cycle should see the same unreported commits again rather than silently losing them.
    """
    _last_sha_path(handover_dir).write_text(sha)


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


def _short_sha(sha: str | None) -> str:
    return sha[:7] if sha else "unknown"


def _shorten_title(title: str, limit: int = 60) -> str:
    return title if len(title) <= limit else title[: limit - 1].rstrip() + "…"


def _format_pr_line(pr: dict[str, object]) -> str:
    number = pr.get("number", "?")
    title = _shorten_title(str(pr.get("title", "")))
    state = str(pr.get("mergeStateStatus") or "UNKNOWN")
    note = " (checks running, not failing)" if state == "UNSTABLE" else ""
    return f"#{number} {title} — {state}{note}"


def format_routine_post(
    eta_headline: str | None,
    eta_stale: bool | None,
    pr_count: int,
    prs: list[dict[str, object]],
    merged_status: str,
    merged_subjects: list[str],
    remote_sha: str | None,
) -> str:
    """Format one routine status post. Content only — no token, no path, ever.

    No balance line: withdrawn by maintainer instruction, 2026-08-29. The DeepSeek poller
    and `balance-heartbeat.log` are unaffected — only this post's content lost the number.

    `merged_status` is one of `"unknown"` (the remote could not be reached), `"baseline"`
    (no prior post to diff against), `"unchanged"`, or `"changed"` — see `main`, which
    derives it from `get_remote_main_sha` and `get_last_reported_sha`.
    """
    lines = []

    if eta_headline is None:
        lines.append("*ETA:* eta.md missing or unparseable — nothing to report")
    else:
        lines.append(f"*ETA:* {eta_headline}")
        if eta_stale is None:
            lines.append("_(Updated stamp missing or unparseable — staleness unknown)_")
        elif eta_stale:
            lines.append("_(STALE — Updated stamp is more than 2h old)_")

    if pr_count > 0:
        lines.append(f"*OPEN PRs ({pr_count}):*")
        lines.extend(f"  • {_format_pr_line(pr)}" for pr in prs)
    else:
        lines.append("*OPEN PRs:* none")

    if merged_status == "unknown":
        lines.append("*MERGED SINCE LAST POST:* could not reach origin (git ls-remote failed)")
    elif merged_status == "baseline":
        lines.append(
            f"*MERGED SINCE LAST POST:* baseline set at `{_short_sha(remote_sha)}` — "
            "nothing to compare against yet"
        )
    elif merged_status == "unchanged":
        sha = _short_sha(remote_sha)
        lines.append(f"*MERGED SINCE LAST POST:* none (main unchanged at `{sha}`)")
    elif merged_subjects:
        lines.append("*MERGED SINCE LAST POST:*")
        lines.extend(f"  • {subject}" for subject in merged_subjects)
    else:
        lines.append(
            f"*MERGED SINCE LAST POST:* main moved to `{_short_sha(remote_sha)}` but the "
            "commit log could not be read"
        )

    return "\n".join(lines)


def main() -> int:
    """Run one reporter cycle. Exit 0 on a token outage — the cycle keeps running."""
    # Read the clock once at the start of this cycle, so all staleness checks use the
    # same moment. Drift between reading the clock and computing staleness is a source
    # of false positives (stale flag set moments after a reading, wrong when reported
    # minutes later). Maintainer instruction, 2026-08-30.
    now = datetime.now(UTC)

    handover_dir = _handover_dir()
    log_path = handover_dir / "slack-reporter.log"

    token = get_token(handover_dir, _token_path(), log_path)
    if not token:
        return 0

    repo_dir = _repo_dir()
    eta_headline, eta_stale = get_eta(handover_dir / "eta.md", now)
    pr_count, prs = get_prs(repo_dir)

    last_sha = get_last_reported_sha(handover_dir)
    remote_sha = get_remote_main_sha(repo_dir)
    merged_subjects: list[str] = []
    if remote_sha is None:
        merged_status = "unknown"
    elif last_sha is None:
        merged_status = "baseline"
    elif remote_sha == last_sha:
        merged_status = "unchanged"
    else:
        merged_status = "changed"
        merged_subjects = get_merged_subjects(repo_dir, last_sha, remote_sha)

    text = format_routine_post(
        eta_headline, eta_stale, pr_count, prs, merged_status, merged_subjects, remote_sha
    )
    ok = post_to_slack(token, text, _channel())
    _log_line(log_path, f"routine post - ok={ok}")
    if ok and remote_sha is not None:
        set_last_reported_sha(handover_dir, remote_sha)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
