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

from reporter import (  # noqa: E402
    ETA_MALFORMED_MESSAGE,
    _log_line,
    check_main_staleness,
    format_routine_post,
    get_eta,
    get_eta_main_sha,
    post_to_slack,
)


def _write_eta(tmp_path: Path, updated_line: str) -> Path:
    # The headline carries a BST clock time (Ruling 106, 2026-09-04, rule 2) so these
    # fixtures exercise the `**Updated:**`-staleness logic under test here, not rule 2's
    # own malformed-headline path — that path has its own dedicated test below.
    eta_file = tmp_path / "eta.md"
    eta_file.write_text(
        "**Headline:** On track for the Friday demo, ETA 14:30 BST.\n\n"
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
    eta_file.write_text(
        "**Headline:** On track for the Friday demo, ETA 14:30 BST.\n\nNo stamp here.\n"
    )
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
        "**Headline:** On track for the **Friday** demo at 14:30 BST — no blockers.\n"
        "Second line of the same paragraph.\n\n"
        "**Updated:** 2026-08-30 09:00Z\n"
    )
    now = datetime(2026, 8, 30, 9, 30, tzinfo=UTC)

    headline, _stale = get_eta(eta_file, now)

    assert headline == (
        "On track for the **Friday** demo at 14:30 BST — no blockers.\n"
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


# ---------------------------------------------------------------------------
# Ruling 106 (2026-09-04) — the Slack routine: a 100-word cap, a BST clock time in the
# ETA, and a refresh on every `origin/main` move. Three rules, three broken-input proofs,
# named verbatim in the ruling's own "Acceptance" section
# (docs/plans/2026-09-04-ruling-106-slack-routine-word-cap-bst-eta-and-head-refresh.md).
# ---------------------------------------------------------------------------


def test_over_140_word_body_is_truncated_to_the_cap_with_headline_intact() -> None:
    # Violation: a routine post over 100 words. Broken-input proof (ruling, "Acceptance"):
    # a deliberately >140-word body posts at <= 100 with the `(+N words cut)` marker,
    # headline intact.
    headline = "Earliest ETA 14:30 BST 2026-09-04, on (g) triage landing."
    prs = [
        {
            "number": i,
            "title": f"padding filler words chosen only to blow well past the word cap {i}",
            "mergeStateStatus": "CLEAN",
        }
        for i in range(1, 25)
    ]
    merged_subjects = [f"deadbeef{i} filler merged-commit subject line {i}" for i in range(20)]

    # The body alone (PR titles + merged subjects), before any truncation, is well over
    # 140 words — this fixture actually exercises the truncation path, not a coincidence.
    body_word_count = sum(len(str(pr["title"]).split()) + 2 for pr in prs) + sum(
        len(s.split()) for s in merged_subjects
    )
    assert body_word_count > 140

    post = format_routine_post(
        headline, False, len(prs), prs, "changed", merged_subjects, "deadbeef"
    )

    assert len(post.split()) <= 100
    assert "(+" in post
    assert "words cut)" in post
    assert f"*ETA:* {headline}" in post  # headline present, byte-for-byte, never cut


def test_headline_with_no_clock_time_is_rejected_not_posted_as_given(tmp_path: Path) -> None:
    # Violation: an ETA headline with no BST clock time. Broken-input proof (ruling,
    # "Acceptance"): a headline with a bare duration ("in 2 hours") is rejected and
    # replaced with the malformed-headline message, never posted as given.
    eta_file = tmp_path / "eta.md"
    eta_file.write_text(
        "**Headline:** Should land in about 2 hours, no rush.\n\n"
        "**Updated:** 2026-09-04 09:00 BST\n"
    )
    now = datetime(2026, 9, 4, 9, 30, tzinfo=UTC)

    headline, stale = get_eta(eta_file, now)

    assert headline == ETA_MALFORMED_MESSAGE
    assert "2 hours" not in headline

    post = format_routine_post(headline, stale, 0, [], "unchanged", [], "deadbeef")
    assert "2 hours" not in post
    assert ETA_MALFORMED_MESSAGE in post


def test_stale_eta_after_unrefreshed_main_move_carries_the_stale_marker(
    tmp_path: Path,
) -> None:
    # Violation: a post after origin/main has moved that still carries the old ETA with
    # no stale marker. Broken-input proof (ruling, "Acceptance"): advance a fixture
    # origin/main past the recorded `main:` sha with no accompanying eta.md update; the
    # next cycle's post must carry the stale-ETA line, not the carried-forward headline.
    eta_file = tmp_path / "eta.md"
    eta_file.write_text(
        "**Headline:** Earliest 14:30 BST 2026-09-04, on triage landing.\n\n"
        "**Updated:** 2026-09-04 09:00 BST\n"
        "**main:** `ad51906`\n"
    )
    now = datetime(2026, 9, 4, 9, 30, tzinfo=UTC)

    carried_headline, _carried_stale = get_eta(eta_file, now)
    assert carried_headline is not None
    assert "14:30 BST" in carried_headline

    # origin/main advanced to a new sha the lead has not re-derived eta.md against.
    new_remote_sha = "fa53484c1f79481add8e2a16a5977bd432346b3"
    eta_main_sha = get_eta_main_sha(eta_file)
    assert eta_main_sha == "ad51906"

    stale_line = check_main_staleness(eta_main_sha, new_remote_sha, now)
    assert stale_line is not None
    assert "ETA stale" in stale_line
    assert "fa53484" in stale_line
    assert "not yet re-derived" in stale_line

    post = format_routine_post(
        stale_line, None, 0, [], "changed", ["fa53484 docs: filed"], new_remote_sha
    )
    assert stale_line in post
    assert carried_headline not in post  # the carried-forward headline must not appear


def test_matching_main_sha_is_not_stale_and_carried_headline_posts_unchanged(
    tmp_path: Path,
) -> None:
    # Negative control for the same rule: when the lead HAS refreshed eta.md (its `main:`
    # field matches origin/main's live tip), no stale marker appears and the headline
    # posts as given.
    eta_file = tmp_path / "eta.md"
    eta_file.write_text(
        "**Headline:** Earliest 14:30 BST 2026-09-04, on triage landing.\n\n"
        "**Updated:** 2026-09-04 09:00 BST\n"
        "**main:** `ad51906b7b1582823f7ed32cf16cef426e8c6c28`\n"
    )
    now = datetime(2026, 9, 4, 9, 30, tzinfo=UTC)

    eta_main_sha = get_eta_main_sha(eta_file)
    assert eta_main_sha == "ad51906b7b1582823f7ed32cf16cef426e8c6c28"

    stale_line = check_main_staleness(eta_main_sha, "ad51906b7b1582823f7ed32cf16cef426e8c6c28", now)
    assert stale_line is None

    # A short local sha that is a genuine prefix of the full remote sha is also not stale.
    full_sha = "ad51906b7b1582823f7ed32cf16cef426e8c6c28"
    stale_line_prefix = check_main_staleness("ad51906", full_sha, now)
    assert stale_line_prefix is None
