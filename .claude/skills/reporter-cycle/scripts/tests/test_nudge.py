"""Tests for nudge.py's multi-signal lead-staleness predicate.

Defect (2026-09-01): the lead-staleness nudge fired off a SINGLE signal —
`.last_lead_status_ts`, a marker written by the reporter that in practice records when the
lead last *talked to the reporter*, not whether the lead is alive. It produced a false
positive at 10:45Z: the marker read 25.4 minutes "stale" while the lead had, in that same
window, merged six PRs, restarted two executors and dispatched two roles. An alarm that
fires hardest when the lead is busiest gets ignored, and the failure that matters is not
the one false positive but the credibility loss that follows it — the alarm being useless
on the day the lead really has stopped.

Fix: `nudge.py` now checks THREE independent liveness signals — the marker, `eta.md`'s
`**Updated:**` stamp (via `reporter.get_eta_updated`, reused rather than re-parsed), and
`origin/main`'s newest LOCAL commit timestamp — and nudges only when ALL THREE are stale
(`lead_is_stale`, a pure conjunction). The 20-minute default threshold is unchanged; only
what counts as evidence of life changed, per the dispatch that requested this fix.

The three source timestamps cannot be retroactively aged on disk, so every test here drives
the pure decision functions with an injected `now` far enough past a source's real
timestamp to cross the threshold — nothing sleeps, and nothing needs a stale fixture file
to already exist on disk.

Registered in `pyproject.toml`'s `testpaths` alongside `test_reporter.py`, so
`uv run pytest -q` from the repo root collects this file too. Run scoped to just this file:

    uv run pytest .claude/skills/reporter-cycle/scripts/tests/test_nudge.py -q
"""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from nudge import (  # noqa: E402
    check_and_nudge,
    eta_age_seconds,
    lead_is_stale,
    main_commit_age_seconds,
    marker_age_seconds,
)

THRESHOLD = 1200  # 20 minutes — the production default, held fixed per the dispatch.


def _init_repo_with_commit(repo_dir: Path) -> None:
    """A minimal real git repo with a HEAD commit and an `origin/main` ref pointing at it.

    `refs/remotes/origin/main` is created directly with `update-ref` rather than by adding
    a real remote and fetching — this is exactly the local ref `main_commit_age_seconds`
    reads, and building it this way keeps the test off the network entirely, matching the
    constraint the function itself is under.
    """
    subprocess.run(["git", "init", "-q"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_dir, check=True)
    (repo_dir / "f.txt").write_text("x")
    subprocess.run(["git", "add", "f.txt"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo_dir, check=True)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_dir, capture_output=True, text=True, check=True
    ).stdout.strip()
    subprocess.run(["git", "update-ref", "refs/remotes/origin/main", sha], cwd=repo_dir, check=True)


# ---- individual signal readers -------------------------------------------------------


def test_marker_age_seconds_missing_file_returns_none(tmp_path: Path) -> None:
    age = marker_age_seconds(tmp_path / "does-not-exist", datetime.now(UTC))
    assert age is None


def test_marker_age_seconds_fresh(tmp_path: Path) -> None:
    marker = tmp_path / ".last_lead_status_ts"
    now = datetime.now(UTC)
    marker.write_text(str(now.timestamp()))
    age = marker_age_seconds(marker, now)
    assert age is not None
    assert age < 1.0


def test_eta_age_seconds_missing_file_returns_none(tmp_path: Path) -> None:
    age = eta_age_seconds(tmp_path / "eta.md", datetime.now(UTC))
    assert age is None


def test_eta_age_seconds_parses_via_shared_get_eta_updated(tmp_path: Path) -> None:
    now = datetime.now(UTC)
    stamp = now.strftime("%Y-%m-%d %H:%M")
    eta_file = tmp_path / "eta.md"
    eta_file.write_text(f"**Headline:** things are fine\n\n**Updated:** {stamp} Z\n")
    age = eta_age_seconds(eta_file, now)
    assert age is not None
    assert age < 60.0  # same minute, allowing for the seconds truncated by the stamp


def test_main_commit_age_seconds_real_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo_with_commit(repo)
    age = main_commit_age_seconds(repo, datetime.now(UTC))
    assert age is not None
    assert age < 60.0


def test_main_commit_age_seconds_non_repo_returns_none(tmp_path: Path) -> None:
    not_a_repo = tmp_path / "empty"
    not_a_repo.mkdir()
    age = main_commit_age_seconds(not_a_repo, datetime.now(UTC))
    assert age is None


# ---- lead_is_stale: the pure decision function ----------------------------------------


def test_lead_is_stale_all_fresh_no_nudge() -> None:
    assert lead_is_stale(60.0, 60.0, 60.0, THRESHOLD) is False


@pytest.mark.parametrize(
    ("marker_age", "eta_age", "main_age"),
    [
        (60.0, THRESHOLD + 100, THRESHOLD + 100),  # only the marker is fresh
        (THRESHOLD + 100, 60.0, THRESHOLD + 100),  # only eta.md is fresh
        (THRESHOLD + 100, THRESHOLD + 100, 60.0),  # only origin/main is fresh
    ],
)
def test_lead_is_stale_any_one_fresh_signal_blocks_the_nudge(
    marker_age: float, eta_age: float, main_age: float
) -> None:
    """Negative case, all three permutations: one fresh signal is enough to call the lead
    alive, regardless of how stale the other two are — this is exactly what stopped
    today's false positive (a stale marker, everything else fresh)."""
    assert lead_is_stale(marker_age, eta_age, main_age, THRESHOLD) is False


def test_lead_is_stale_all_three_stale_fires() -> None:
    """Positive case: every signal past the threshold — the nudge DOES fire.

    A check that has never printed a failure has not been tested (CLAUDE.md §13). This
    is the assertion that would have caught the previous defect in the other direction
    too: a predicate that silently never fires again (e.g. by treating a missing source
    as automatically fresh) is strictly worse than the over-firing single-signal version
    it replaces, because it fails silently.
    """
    assert lead_is_stale(THRESHOLD + 1, THRESHOLD + 1, THRESHOLD + 1, THRESHOLD) is True


def test_lead_is_stale_missing_sources_count_as_stale_not_fresh() -> None:
    """A missing/unparseable source (`None`) must not silently vote for liveness.

    All three signals unavailable, with none of them explicitly "stale" by an age
    comparison, still fires — because `None` is treated as stale, never as fresh (see
    `nudge._is_stale`'s docstring for the reasoning). If a missing source instead defaulted
    to "fresh", this predicate would go permanently silent the moment one file vanished.
    """
    assert lead_is_stale(None, None, None, THRESHOLD) is True


def test_lead_is_stale_missing_source_does_not_alone_force_a_nudge() -> None:
    """One missing source, but a genuinely fresh other signal, still blocks the nudge —
    a missing source only fails to BLOCK a nudge the other signals already justify; it
    cannot manufacture one on its own against real evidence of life."""
    assert lead_is_stale(None, 60.0, None, THRESHOLD) is False


# ---- check_and_nudge: end-to-end against real files and a real repo -------------------


def test_check_and_nudge_positive_case_fires_and_logs(tmp_path: Path) -> None:
    """The nudge DOES fire end-to-end, with real output — the case CLAUDE.md §13 asks for
    explicitly: a check that has never printed a failure has not been tested.

    All three real sources are written/committed at (approximately) the real current time;
    staleness is produced by injecting a `now` far enough in the future that every age
    exceeds the threshold, rather than by sleeping or backdating files on disk (the sources
    "cannot be retroactively aged", per the dispatch that requested this test).
    """
    handover_dir = tmp_path / "handover"
    handover_dir.mkdir()
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    _init_repo_with_commit(repo_dir)

    real_now = datetime.now(UTC)
    marker = handover_dir / ".last_lead_status_ts"
    marker.write_text(str(real_now.timestamp()))
    eta_file = handover_dir / "eta.md"
    stamp = real_now.strftime("%Y-%m-%d %H:%M")
    eta_file.write_text(f"**Headline:** all clear\n\n**Updated:** {stamp} Z\n")

    nudge_log = handover_dir / "nudge.log"
    injected_now = real_now + timedelta(seconds=THRESHOLD + 300)

    fired = check_and_nudge(handover_dir, repo_dir, nudge_log, THRESHOLD, now=injected_now)

    assert fired is True
    assert nudge_log.exists()
    log_content = nudge_log.read_text()
    assert "nudge sent" in log_content
    assert "marker" in log_content
    assert "eta" in log_content
    assert "main" in log_content
    print(f"REAL OUTPUT — nudge.log content:\n{log_content}", file=sys.stderr)


def test_check_and_nudge_negative_case_no_log_written(tmp_path: Path) -> None:
    """One fresh signal (the marker) blocks the nudge and nothing is logged."""
    handover_dir = tmp_path / "handover"
    handover_dir.mkdir()
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    _init_repo_with_commit(repo_dir)

    real_now = datetime.now(UTC)
    marker = handover_dir / ".last_lead_status_ts"
    marker.write_text(str(real_now.timestamp()))  # fresh at the injected "now" below
    # No eta.md, and the git commit will read as stale under the injected `now` — both
    # missing/stale, but the marker alone must still block the nudge.

    nudge_log = handover_dir / "nudge.log"
    injected_now = real_now + timedelta(seconds=30)  # marker still fresh at this point

    fired = check_and_nudge(handover_dir, repo_dir, nudge_log, THRESHOLD, now=injected_now)

    assert fired is False
    assert not nudge_log.exists()
