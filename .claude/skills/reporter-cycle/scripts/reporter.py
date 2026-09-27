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

# RL-1059 (2026-09-04), rule 1: a routine post is at most this many words, counted over
# the whole rendered body. The ETA headline (and its staleness annotation) is exempt from
# truncation — see `_truncate_to_word_cap`.
MAX_ROUTINE_POST_WORDS = 100

# "(+42 words cut)" is always exactly 3 whitespace-separated tokens regardless of how many
# digits the count has — reserved out of the truncation budget so the marker itself never
# pushes the final post back over the cap.
_TRUNCATION_MARKER_WORD_COST = 3

# RL-1059 (2026-09-04), rule 2: the ETA headline must name a clock time in BST — a bare
# duration ("~2 hours", "soon") is rejected. Optionally followed by a `YYYY-MM-DD` date.
_BST_CLOCK_TIME_PATTERN = re.compile(r"\b\d{1,2}:\d{2}\s*BST\b(?:\s+\d{4}-\d{2}-\d{2})?")

# Sentinel messages `get_eta`/`check_main_staleness` return in place of the lead's actual
# headline text. `_is_eta_override_message` uses these to suppress the normal staleness
# annotation, which does not apply to a line that is not actually the ETA.
ETA_MALFORMED_MESSAGE = "ETA headline malformed — no clock time"
_ETA_STALE_MAIN_PREFIX = "ETA stale — main moved to `"


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


def _parse_updated_stamp(text: str) -> datetime | None:
    """Parse eta.md's `**Updated:**` stamp out of already-read file text.

    Factored out of `get_eta` (below) so there is exactly one place that understands the
    stamp format — a bare UTC `Z` suffix, or the GB-local `BST`/`GMT` forms `eta.md`'s own
    header documents, resolved via `zoneinfo.ZoneInfo("Europe/London")` rather than a
    hardcoded UTC+1. `get_eta_updated` (below) calls this too, for `nudge.py`'s
    multi-signal liveness check, so that caller reuses this parser instead of writing a
    second one that could drift from it (CLAUDE.md §2: "a shape defined twice will
    diverge"). Returns an aware UTC datetime, or `None` if no stamp matches or it fails to
    parse — never a naive datetime and never a guess.
    """
    updated_pattern = re.compile(
        r"^\*\*Updated:\*\*\s*(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})\s*(Z|BST|GMT)\b",
        re.MULTILINE,
    )
    updated_match = updated_pattern.search(text)
    if not updated_match:
        return None
    try:
        naive = datetime.strptime(
            f"{updated_match.group(1)} {updated_match.group(2)}", "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return None

    suffix = updated_match.group(3)
    updated = naive.replace(tzinfo=UTC) if suffix == "Z" else naive.replace(tzinfo=LONDON)
    return updated.astimezone(UTC)


def get_eta_updated(eta_file: Path) -> datetime | None:
    """Read eta.md and return its parsed `**Updated:**` stamp as an aware UTC datetime.

    `None` covers a missing file, an unreadable one, or one whose stamp does not parse —
    the same three cases `get_eta` already distinguishes for `stale=None`, collapsed here
    into a single "unknown" result because the caller (`nudge.py`) only needs an age, not a
    reason. See `_parse_updated_stamp` for why this exists as its own function rather than
    being inlined into `get_eta`.
    """
    try:
        text = eta_file.read_text()
    except OSError:
        return None
    return _parse_updated_stamp(text)


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

    RL-1059 (2026-09-04), rule 2: a headline naming no `HH:MM BST` clock time (optionally
    followed by `YYYY-MM-DD`) is never returned as given — a bare duration ("~2 hours",
    "soon") is rejected in favour of the fixed `ETA_MALFORMED_MESSAGE`, with `stale=None`
    (the staleness annotation describes the lead's actual ETA text, which this is not).
    This check runs before the `**Updated:**` staleness check below and short-circuits it.

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

    if not _BST_CLOCK_TIME_PATTERN.search(headline):
        return ETA_MALFORMED_MESSAGE, None

    updated = _parse_updated_stamp(text)
    if updated is None:
        return headline, None

    return headline, (now - updated) > timedelta(hours=2)


def get_eta_main_sha(eta_file: Path) -> str | None:
    """Read eta.md's `**main:**` field: the `origin/main` sha the lead derived the current
    ETA against (RL-1059, 2026-09-04, rule 3). Beside `**Updated:**`, e.g.
    ``**main:** `ad51906` `` — the backticks are optional, a bare short or full sha also
    parses. `None` covers a missing file, an unreadable one, or a file with no `main:`
    field — the same "unknown, never guessed" contract as `get_eta_updated`.
    """
    try:
        text = eta_file.read_text()
    except OSError:
        return None
    match = re.search(r"^\*\*main:\*\*\s*`?([0-9a-f]{4,40})`?", text, re.MULTILINE)
    if not match:
        return None
    return match.group(1)


def check_main_staleness(
    eta_main_sha: str | None, remote_sha: str | None, now: datetime
) -> str | None:
    """Return the stale-ETA line when eta.md's recorded `main:` sha disagrees with the live
    `origin/main` tip, or `None` when they agree or either side is unknown (never guessed).

    RL-1059 (2026-09-04), rule 3: the ETA is refreshed on every move of `origin/main`'s
    HEAD, and that refresh is the lead's own work, not the reporter's. This is the backstop
    that makes a missed refresh visible to a reader — not the mechanism itself. The
    comparison is prefix-based, since `eta_main_sha` is typically the 7-char short sha the
    lead writes by hand while `remote_sha` (from `get_remote_main_sha`, `git ls-remote`) is
    the full 40-char sha; a short sha that is a genuine prefix of the current tip is not
    misreported as stale.
    """
    if eta_main_sha is None or remote_sha is None:
        return None
    if remote_sha.startswith(eta_main_sha) or eta_main_sha.startswith(remote_sha):
        return None
    clock = now.astimezone(LONDON).strftime("%H:%M")
    sha = _short_sha(remote_sha)
    return f"{_ETA_STALE_MAIN_PREFIX}{sha}` at {clock} BST, ETA not yet re-derived"


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


def post_to_slack(token: str | None, text: str, channel: str) -> tuple[bool, str]:
    """Post one message to Slack. `token` is read once by the caller, never logged.

    Returns `(ok, detail)`. `detail` is a short, token-safe description of the outcome —
    the caller logs it so a failed post says *what* Slack rejected, not merely that it
    was rejected. It is built to never carry the token: the Slack response body itself
    never echoes the `Authorization` header, but `subprocess.TimeoutExpired`'s own
    `__str__` includes the full argv it was given — which contains
    `Authorization: Bearer <token>` — so that exception is caught separately and never
    stringified into `detail` or the log.
    """
    if not token:
        print("ERROR: No Slack token", file=sys.stderr)
        return False, "no token available"
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
    except subprocess.TimeoutExpired:
        # Deliberately not `{exc}`: TimeoutExpired.__str__ includes the full argv,
        # which carries the bearer token in the Authorization header.
        print("ERROR posting to Slack: curl timed out after 10s", file=sys.stderr)
        return False, "transport error: curl timed out after 10s"
    except OSError as exc:
        # A plain OSError (e.g. curl not found) does not echo argv the way
        # TimeoutExpired does, so this is safe to include verbatim.
        print(f"ERROR posting to Slack: {exc}", file=sys.stderr)
        return False, f"transport error: {exc}"
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"ERROR posting to Slack: {exc}", file=sys.stderr)
        detail = f"unparseable response (exit {result.returncode}): {result.stdout[:200]!r}"
        return False, detail
    ok = bool(response.get("ok", False))
    if not ok:
        error = str(response.get("error", "unknown"))
        print(f"Slack error: {error}", file=sys.stderr)
        return False, error
    return True, "ok"


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


def _word_count(text: str) -> int:
    return len(text.split())


def _is_eta_override_message(headline: str) -> bool:
    """True for a sentinel line (`get_eta`'s malformed message, or `check_main_staleness`'s
    stale-main line) standing in for the lead's actual headline text — those carry their
    own complete meaning, so the normal Updated-stamp staleness annotation below them would
    only confuse a reader.
    """
    return headline == ETA_MALFORMED_MESSAGE or headline.startswith(_ETA_STALE_MAIN_PREFIX)


def _build_eta_lines(eta_headline: str | None, eta_stale: bool | None) -> list[str]:
    if eta_headline is None:
        return ["*ETA:* eta.md missing or unparseable — nothing to report"]

    lines = [f"*ETA:* {eta_headline}"]
    if _is_eta_override_message(eta_headline):
        return lines
    if eta_stale is None:
        lines.append("_(Updated stamp missing or unparseable — staleness unknown)_")
    elif eta_stale:
        lines.append("_(STALE — Updated stamp is more than 2h old)_")
    return lines


def _build_pr_lines(pr_count: int, prs: list[dict[str, object]]) -> list[str]:
    if pr_count > 0:
        return [f"*OPEN PRs ({pr_count}):*", *(f"  • {_format_pr_line(pr)}" for pr in prs)]
    return ["*OPEN PRs:* none"]


def _build_merged_lines(
    merged_status: str, merged_subjects: list[str], remote_sha: str | None
) -> list[str]:
    if merged_status == "unknown":
        return ["*MERGED SINCE LAST POST:* could not reach origin (git ls-remote failed)"]
    if merged_status == "baseline":
        return [
            f"*MERGED SINCE LAST POST:* baseline set at `{_short_sha(remote_sha)}` — "
            "nothing to compare against yet"
        ]
    if merged_status == "unchanged":
        sha = _short_sha(remote_sha)
        return [f"*MERGED SINCE LAST POST:* none (main unchanged at `{sha}`)"]
    if merged_subjects:
        return ["*MERGED SINCE LAST POST:*", *(f"  • {s}" for s in merged_subjects)]
    return [
        f"*MERGED SINCE LAST POST:* main moved to `{_short_sha(remote_sha)}` but the "
        "commit log could not be read"
    ]


def _truncate_to_word_cap(headline_lines: list[str], body_lines: list[str]) -> str:
    """Truncate `body_lines` (the PR and merged-commit sections) to fit the whole post
    under `MAX_ROUTINE_POST_WORDS`, appending `(+N words cut)`.

    RL-1059 (2026-09-04), rule 1: the ETA headline (`headline_lines`) is never
    truncated — a half-cut ETA is worse than a full one with less context around it — so
    only the non-headline sections are candidates for the cut. `words_cut` counts every
    word actually dropped from the original body, computed as a difference so it stays
    correct regardless of how the cut point falls inside a line.
    """
    headline_text = "\n".join(headline_lines)
    headline_words = _word_count(headline_text)
    body_words_total = _word_count("\n".join(body_lines))

    budget = max(MAX_ROUTINE_POST_WORDS - headline_words - _TRUNCATION_MARKER_WORD_COST, 0)

    kept_lines: list[str] = []
    words_kept = 0
    for line in body_lines:
        words = line.split()
        if words_kept + len(words) <= budget:
            kept_lines.append(line)
            words_kept += len(words)
            continue
        remaining = budget - words_kept
        if remaining > 0:
            kept_lines.append(" ".join(words[:remaining]))
            words_kept += remaining
        break

    words_cut = body_words_total - words_kept
    kept_lines.append(f"(+{words_cut} words cut)")
    return "\n".join([*headline_lines, *kept_lines])


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

    RL-1059 (2026-09-04), rule 1: the whole rendered body is capped at
    `MAX_ROUTINE_POST_WORDS` words. Over the cap, the non-headline sections (PR list,
    merged-commit list) are truncated first — the ETA headline never is — and a
    `(+N words cut)` marker is appended. See `_truncate_to_word_cap`.
    """
    headline_lines = _build_eta_lines(eta_headline, eta_stale)
    body_lines = [
        *_build_pr_lines(pr_count, prs),
        *_build_merged_lines(merged_status, merged_subjects, remote_sha),
    ]

    full_text = "\n".join([*headline_lines, *body_lines])
    if _word_count(full_text) <= MAX_ROUTINE_POST_WORDS:
        return full_text

    return _truncate_to_word_cap(headline_lines, body_lines)


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
    eta_file = handover_dir / "eta.md"
    eta_headline, eta_stale = get_eta(eta_file, now)
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

    # RL-1059 (2026-09-04), rule 3: if eta.md's own `main:` field has fallen behind
    # `origin/main`'s live tip, the carried-forward headline is replaced with a stale-ETA
    # line rather than posted as if it were still current. The lead's own obligation is to
    # re-derive eta.md on every merge; this is only the backstop that makes a missed
    # refresh visible to a reader.
    stale_main_line = check_main_staleness(get_eta_main_sha(eta_file), remote_sha, now)
    if stale_main_line is not None:
        eta_headline, eta_stale = stale_main_line, None

    text = format_routine_post(
        eta_headline, eta_stale, pr_count, prs, merged_status, merged_subjects, remote_sha
    )
    ok, detail = post_to_slack(token, text, _channel())
    _log_line(log_path, f"routine post - ok={ok} - detail={detail}")
    _log_line(log_path, f"routine post body: {text!r}")
    if ok and remote_sha is not None:
        set_last_reported_sha(handover_dir, remote_sha)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
