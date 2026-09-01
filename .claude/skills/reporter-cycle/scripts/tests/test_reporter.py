"""Tests for reporter.py's get_eta staleness parsing and post_to_slack logging.

Defect (auditor-verified, 2026-08-31): get_eta's **Updated:** regex required a literal
`Z` suffix. eta.md is lead-owned and its own header says "All times are GB local (BST,
UTC+1)", so every real stamp written under that convention (e.g. "2026-08-30 10:00 BST")
failed to parse, `stale` came back `None`, and the caller printed "staleness unknown"
instead of ever evaluating the 2-hour STALE threshold. Measured over the reporter's whole
operating history (212 Slack messages, 2026-08-29..2026-08-31): the STALE branch fired
zero times; 166/190 ETA posts read "staleness unknown".

Second defect, found while the first fix was in flight: the returned headline includes its
own `**Headline:**` label — `get_eta`'s regex has to match on that label to locate the
paragraph, but it then returns `match.group(0)` (the whole match, label included) rather
than just the paragraph body. Every historical Slack post in this channel doubles the label
(`*ETA:* **Headline:** **...`), confirmed against Slack history, not merely the log. The
label cannot be dropped from `eta.md` (the regex needs it to find the paragraph), so the
strip belongs in `get_eta`.

Registered in `pyproject.toml`'s `testpaths` (since #530) so `uv run pytest -q` from the
repo root collects this file too, despite these scripts being stdlib-only utilities outside
the uv workspace — that registration is what makes CI's `pyproject.toml` path filter catch
a change here. Run scoped to just this file:

    uv run pytest .claude/skills/reporter-cycle/scripts/tests/test_reporter.py -q
"""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from reporter import _log_line, format_routine_post, get_eta, post_to_slack  # noqa: E402


def _write_eta(tmp_path: Path, updated_line: str) -> Path:
    eta_file = tmp_path / "eta.md"
    eta_file.write_text(
        "**Headline:** On track for the Friday demo.\n\n"
        f"{updated_line}\n"
    )
    return eta_file


def test_bst_stamp_parses_and_is_not_stale(tmp_path: Path) -> None:
    # 2026-08-30 is BST (UTC+1): 10:00 BST == 09:00 UTC.
    eta_file = _write_eta(tmp_path, "**Updated:** 2026-08-30 10:00 BST")
    now = datetime(2026, 8, 30, 9, 30, tzinfo=UTC)  # 30 min after the true UTC instant

    headline, stale = get_eta(eta_file, now)

    assert headline is not None
    assert stale is False


def test_gmt_stamp_uses_zero_offset_not_hardcoded_plus_one(tmp_path: Path) -> None:
    # 2026-01-15 is GMT (UTC+0): 10:00 GMT == 10:00 UTC, NOT 09:00 UTC.
    #
    # A fix that hardcoded "+1 for any letter suffix" instead of resolving BST/GMT via
    # zoneinfo would compute updated == 09:00 UTC here. With now=11:30 UTC that wrong
    # offset yields a 2h30m gap (stale=True) where the correct offset yields 1h30m
    # (stale=False) — this test fails under the hardcoded-+1 implementation.
    eta_file = _write_eta(tmp_path, "**Updated:** 2026-01-15 10:00 GMT")
    now = datetime(2026, 1, 15, 11, 30, tzinfo=UTC)

    headline, stale = get_eta(eta_file, now)

    assert headline is not None
    assert stale is False


def test_z_stamp_still_parses(tmp_path: Path) -> None:
    # The pre-existing form. Must not regress: one is live in eta.md right now.
    eta_file = _write_eta(tmp_path, "**Updated:** 2026-08-30 09:00Z")
    now = datetime(2026, 8, 30, 9, 30, tzinfo=UTC)

    headline, stale = get_eta(eta_file, now)

    assert headline is not None
    assert stale is False


def test_unparseable_timezone_returns_stale_none(tmp_path: Path) -> None:
    # A stamp bearing an unaccepted timezone abbreviation must not silently parse as if
    # it were BST/GMT/Z — staleness must come back unknown, not a guess.
    eta_file = _write_eta(tmp_path, "**Updated:** 2026-08-30 10:00 EST")
    now = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)

    headline, stale = get_eta(eta_file, now)

    assert headline is not None
    assert stale is None


def test_garbage_suffix_glued_to_letters_does_not_parse(tmp_path: Path) -> None:
    # Guards against a parse widened so far that "BSTX" or "GMT+1" would match a bare
    # "BST"/"GMT" alternation with no word boundary.
    eta_file = _write_eta(tmp_path, "**Updated:** 2026-08-30 10:00 BSTX")
    now = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)

    headline, stale = get_eta(eta_file, now)

    assert headline is not None
    assert stale is None


def test_stale_branch_fires_for_an_old_bst_stamp(tmp_path: Path) -> None:
    # This branch has never executed in production (STALE fired zero times in the
    # measured history) — prove it actually can, through a realistic GB-local stamp.
    eta_file = _write_eta(tmp_path, "**Updated:** 2026-08-30 08:00 BST")
    now = datetime(2026, 8, 30, 11, 0, tzinfo=UTC)  # true gap: 3h05m > 2h

    headline, stale = get_eta(eta_file, now)

    assert headline is not None
    assert stale is True

    post = format_routine_post(headline, stale, 0, [], "unknown", [], None)
    assert "STALE" in post


def test_missing_updated_stamp_returns_stale_none(tmp_path: Path) -> None:
    eta_file = tmp_path / "eta.md"
    eta_file.write_text("**Headline:** On track for the Friday demo.\n\nNo stamp here.\n")
    now = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)

    headline, stale = get_eta(eta_file, now)

    assert headline is not None
    assert stale is None


def test_missing_file_returns_none_none(tmp_path: Path) -> None:
    headline, stale = get_eta(tmp_path / "does-not-exist.md", datetime.now(UTC))

    assert headline is None
    assert stale is None


def test_headline_label_is_stripped_but_content_survives_verbatim(tmp_path: Path) -> None:
    # The label ("**Headline:**") must not appear in the returned text — it is a doubled
    # label at the call site (`*ETA:* **Headline:** ...`). Everything after the label,
    # including its own bold markers and an em dash, and a second physical line, must
    # come back byte-for-byte: the headline text is the lead's, relayed verbatim.
    eta_file = tmp_path / "eta.md"
    eta_file.write_text(
        "**Headline:** On track for the **Friday** demo — no blockers.\n"
        "Second line of the same paragraph.\n\n"
        "**Updated:** 2026-08-30 09:00Z\n"
    )
    now = datetime(2026, 8, 30, 9, 30, tzinfo=UTC)

    headline, _stale = get_eta(eta_file, now)

    assert headline == (
        "On track for the **Friday** demo — no blockers.\n"
        "Second line of the same paragraph."
    )
    assert "**Headline:**" not in headline


# ---------------------------------------------------------------------------
# post_to_slack / logging defect (auditor-found, 2026-08-31, fixed 2026-09-01):
# the log recorded only `ok=True`/`ok=False`, never the Slack response or the
# rendered post — an artifact consulted as evidence that could say *that*
# something happened but not *what*. Fixed by having post_to_slack return
# (ok, detail) and having main() log both the detail and the rendered body.
# ---------------------------------------------------------------------------


class _FakeCompleted:
    def __init__(self, stdout: str, returncode: int = 0) -> None:
        self.stdout = stdout
        self.returncode = returncode


def test_post_to_slack_failure_returns_the_slack_error_not_just_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(*_args: Any, **_kwargs: Any) -> _FakeCompleted:
        return _FakeCompleted('{"ok": false, "error": "invalid_auth"}')

    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, detail = post_to_slack("xoxb-fake-token", "hello", "C123")

    assert ok is False
    assert detail == "invalid_auth"


def test_post_to_slack_success_returns_ok_detail(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args: Any, **_kwargs: Any) -> _FakeCompleted:
        return _FakeCompleted('{"ok": true}')

    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, detail = post_to_slack("xoxb-fake-token", "hello", "C123")

    assert ok is True
    assert detail == "ok"


def test_post_to_slack_no_token_returns_false_without_a_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(*_args: Any, **_kwargs: Any) -> _FakeCompleted:
        raise AssertionError("post_to_slack must not call curl with no token")

    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, detail = post_to_slack(None, "hello", "C123")

    assert ok is False
    assert detail == "no token available"


def test_post_to_slack_timeout_never_leaks_the_token_via_str_exc(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # subprocess.TimeoutExpired's own __str__ includes the full argv it was given —
    # which, for this call, contains "Authorization: Bearer <token>". A fix that caught
    # (OSError, subprocess.TimeoutExpired) as one group and did f"{exc}" would put the
    # live token straight into the log. This is the failure this test guards against.
    token = "xoxb-should-never-appear-in-a-log"

    def fake_run(cmd: list[str], **_kwargs: Any) -> _FakeCompleted:
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=10)

    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, detail = post_to_slack(token, "hello", "C123")

    assert ok is False
    assert token not in detail
    assert "timed out" in detail


def test_failure_path_log_line_identifies_what_failed_not_merely_that_it_did(
    tmp_path: Path,
) -> None:
    # The defect this whole change fixes: the log used to say only `ok=False`. Prove the
    # log line written for a failed post now names the Slack error, and — separately —
    # that a token passed into post_to_slack never reaches the log file on disk.
    log_path = tmp_path / "slack-reporter.log"
    token = "xoxb-should-never-appear-in-a-log"

    # Mirrors what main() writes after a failed post_to_slack() call — deterministic
    # here rather than depending on a live Slack call, since what is under test is the
    # log line's content, not post_to_slack's HTTP behaviour (covered above).
    ok, detail = False, "channel_not_found"
    _log_line(log_path, f"routine post - ok={ok} - detail={detail}")
    _log_line(log_path, "routine post body: 'the rendered post body'")

    written = log_path.read_text()
    assert "ok=False" in written
    assert "channel_not_found" in written
    assert "the rendered post body" in written
    assert token not in written


def test_success_path_log_line_still_says_ok_and_carries_the_body(tmp_path: Path) -> None:
    log_path = tmp_path / "slack-reporter.log"

    ok, detail = True, "ok"
    _log_line(log_path, f"routine post - ok={ok} - detail={detail}")
    _log_line(log_path, "routine post body: 'the rendered post body'")

    written = log_path.read_text()
    assert "ok=True" in written
    assert "detail=ok" in written
    assert "the rendered post body" in written
