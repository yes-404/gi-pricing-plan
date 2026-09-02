"""`scripts/ruling-acceptance-item-census.py` — the ruling-form flag-day's own proofs.

The maintainer ruled the ruling-form flag-day 2026-09-02, at `#623`'s merge (`aab6327`):
every ruling filed after it must carry a W37-form acceptance item, so the census script's
`none` bucket stops being an unconditional pass and starts failing on a **post**-flag-day
ruling with none. `CLAUDE.md` §13: "a check that has never printed a failure has not been
tested" — this is that proof, against a synthetic git repository (mirroring `tests/
test_lineage_census_carveout.py`'s own synthetic-tree pattern), never against this
repository's own history, which must not be mutated to manufacture a bad commit.

Two things proven here, both required before the flag-day rule can be trusted:

  1. `flag_day_split` correctly separates a pre-flag-day `none` ruling (grandfathered)
     from a post-flag-day one (a violation) — using each heading's own introduction
     commit, not the file's, and not the ruling's number.
  2. `_NAMED_EXCEPTIONS` and `_PROSE_ONLY_RULINGS` are pinned to their flag-day contents.
     Frozen is untestable until something tries to grow it: proven by hand while writing
     this suite (added a fake `"999"` entry to each set, ran this test, watched both
     assertions fail naming the extra entry, removed it, watched both pass again) rather
     than left as an assertion nobody has seen fail.

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence
for a numbered platform requirement — the same reasoning `tests/test_register_lint.py`
and `tests/test_scope_audit.py` give for their own scripts.
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "ruling-acceptance-item-census.py"

_spec = importlib.util.spec_from_file_location("_ruling_acceptance_census_under_test", SCRIPT)
assert _spec is not None
assert _spec.loader is not None
census = importlib.util.module_from_spec(_spec)
# The module under test declares `@dataclass(frozen=True) class RulingHeading`, and the
# dataclass machinery looks its own module up in `sys.modules` while processing the class
# body -- registering here, before `exec_module`, is what makes that lookup succeed rather
# than raising on a module that exists but was never registered.
sys.modules[_spec.name] = census
_spec.loader.exec_module(census)


def _git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
    )


def _commit(root: pathlib.Path, message: str, date: str) -> str:
    """Commit with an explicit author/committer date, never the ambient system clock --
    two commits made back-to-back can land in the same wall-clock second (they did, the
    first time this test was written, and the "must differ" assertion below failed
    flakily against real time), so the dates that make pre/post-flag-day meaningful must
    be deterministic inputs, not a race against `git commit`'s default `now()`.
    """
    env = {**os.environ, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=root, check=True, env=env)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


@pytest.fixture
def synthetic_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A minimal git repository with one ruling filed at the (synthetic) flag-day commit
    and a second, unrelated ruling with no acceptance item filed afterward -- the exact
    shape `flag_day_split` exists to distinguish.
    """
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)

    plans = root / "docs" / "plans"
    plans.mkdir(parents=True)
    rulings = plans / "synthetic-rulings.md"
    rulings.write_text(
        "## Ruling 1 — pre-flag-day, no acceptance item\n\n"
        "Ordinary prose, no marker of any kind.\n",
        encoding="utf-8",
    )
    _commit(root, "seed: Ruling 1, pre-flag-day", date="2026-01-01T00:00:00+00:00")

    with rulings.open("a", encoding="utf-8") as f:
        f.write(
            "\n## Ruling 2 — post-flag-day, no acceptance item\n\n"
            "Ordinary prose, no marker of any kind -- filed after the flag-day.\n"
        )
    _commit(root, "add: Ruling 2, post-flag-day", date="2026-06-01T00:00:00+00:00")

    return root


def test_flag_day_split_separates_pre_and_post_flag_day_none_rulings(
    monkeypatch: pytest.MonkeyPatch, synthetic_repo: pathlib.Path,
) -> None:
    flag_day_sha = _git(synthetic_repo, "log", "--reverse", "--format=%H").stdout.splitlines()[0]
    monkeypatch.setattr(census, "_FLAG_DAY_COMMIT", flag_day_sha)

    buckets = census.classify(synthetic_repo)
    assert {h.number for h in buckets["none"]} == {"1", "2"}, (
        "both synthetic rulings must land in `none` -- neither carries any marker"
    )

    grandfathered, violations = census.flag_day_split(synthetic_repo, buckets["none"])

    assert {h.number for h in grandfathered} == {"1"}
    assert {h.number for h in violations} == {"2"}, (
        "Ruling 2 was introduced after the flag-day and has no acceptance item -- this "
        "is the violation the flag-day rule exists to catch"
    )


def test_flag_day_split_uses_the_headings_own_commit_not_the_files(
    monkeypatch: pytest.MonkeyPatch, synthetic_repo: pathlib.Path,
) -> None:
    """The trap named in the module docstring: a ruling appended to a file whose own
    first commit predates the flag-day must still be dated by its own heading's
    introduction commit. `synthetic_repo` already exercises exactly this shape -- both
    rulings live in one file whose first commit is the flag-day itself -- so this test
    pins the reason the other one passes, rather than repeating it.
    """
    flag_day_sha = _git(synthetic_repo, "log", "--reverse", "--format=%H").stdout.splitlines()[0]
    monkeypatch.setattr(census, "_FLAG_DAY_COMMIT", flag_day_sha)

    buckets = census.classify(synthetic_repo)
    ruling_2 = next(h for h in buckets["none"] if h.number == "2")

    introduced = census._heading_introduced_at(synthetic_repo, ruling_2)
    file_first_commit = _git(
        synthetic_repo, "log", "--reverse", "--format=%aI", "--", "docs/plans/synthetic-rulings.md",
    ).stdout.splitlines()[0]

    assert introduced != file_first_commit, (
        "Ruling 2's own introduction date must differ from the file's first-commit date "
        "-- if they were ever equal by construction this test would not be exercising "
        "the per-heading resolution at all"
    )


def test_named_exceptions_and_prose_only_rulings_are_frozen_at_the_flag_day() -> None:
    """Pinned membership, not a shape check -- growth after the flag-day is a violation
    per the maintainer's ruling, not a maintenance action. Proven to catch growth by
    hand (see module docstring): temporarily adding an entry to either set and re-running
    this test reds both assertions, naming the extra member; removing it passes again.
    """
    assert frozenset({"44"}) == census._NAMED_EXCEPTIONS
    assert frozenset(
        {"40", "42", "43", "45", "46", "47", "50", "51", "54", "60"}
    ) == census._PROSE_ONLY_RULINGS
