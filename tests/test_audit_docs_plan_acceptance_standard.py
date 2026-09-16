"""`scripts/audit-docs.py`'s check 28: a filed plan states an explicit acceptance standard.

NT-0014 §2's C1 mechanises `delivery-process.md` §5 step 4 / §6 step 1 — the lead's
replan-vs-proceed check that "an acceptance standard was actually defined, not just
implied." The note's own draft mechanism ("warn until the format lands, red thereafter")
was **rejected** by Ruling 46
(`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`): a time-of-run switch makes the same
file pass on Tuesday and fail on Wednesday, and a fresh clone cannot reproduce a verdict.

Ruling 46 ruled a durable discriminator instead: **the plan's own filename date against a
constant cutoff** (`PLAN_ACCEPTANCE_STANDARD_CUTOFF` in the script) — no warn phase, because
C1 and the `writing-plans` acceptance-standard field land in the same commit. §3 of the
ruling requires three cases, "not one", because a check proven only to fire has not been
shown to discriminate:

- a synthetic plan **dated after the cutoff with no acceptance-standard field REDS**
  (`test_a_plan_after_the_cutoff_missing_the_field_is_refused`);
- a plan **dated before the cutoff PASSES** even with no field — the "never retro-red-gate"
  half (`test_a_legacy_plan_before_the_cutoff_is_never_flagged`);
- a **conforming plan dated after the cutoff PASSES** — the positive control, without which
  the check could go green by exempting everything
  (`test_a_conforming_plan_after_the_cutoff_is_not_flagged`).

Also checked: a bare "Acceptance Standard" heading with nothing under it before the next
heading is "implied", not "actually defined", and must still red
(`test_a_bare_heading_with_no_content_is_refused`).

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence for
a numbered platform requirement, the same reasoning `tests/test_scope_audit.py` gives for
`scope-audit.py` and `tests/test_audit_docs_finding_citations.py` gives for check 25.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Every one of these tests writes a scratch plan under `docs/plans/` and runs the real
#: `audit-docs.py` over it. `audit-docs.py` derives its own `REPO` from `__file__`
#: (`REPO = pathlib.Path(__file__).resolve().parent.parent`), never from an override or the
#: invoking process's `cwd` — so the only way to keep a scratch file out of the REAL
#: `docs/plans/` (a write no test should make into the actual repository under audit) is to
#: run a COPY of `audit-docs.py`, at a COPY of the repository, so its own `__file__`-derived
#: `REPO` resolves inside the tmpdir. A shallower copy (just `docs/`, or just `docs/plans/`)
#: would silently narrow every assertion below to "check 28 fires in isolation" rather than
#: "check 28 fires the way the real gate runs it" — the whole repo the real audit-docs.py
#: reads (`.claude/roles`, `.claude/skills`, `scripts/`, `CLAUDE.md`, `docs/`) is copied,
#: not trimmed, so nothing here is weaker than the fixture it replaces.
_COPY_IGNORE = shutil.ignore_patterns(
    ".git", "node_modules", ".venv", "__pycache__", "*.pyc", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "dist", "build",
)


def _init_throwaway_git_repo(dest: pathlib.Path) -> None:
    """`audit-docs.py`'s W37-11 partition (`_file_census.git_ls_files`) needs a real `git
    ls-files` to answer from — `REPO` in the copy has no `.git` at all (this worktree's own
    `.git` is a pointer file into the shared checkout elsewhere and is not something a
    disposable copy can use; see `.claude/skills/git-hygiene`'s worktree-corruption
    warning against `cp -r` of one). A fresh one-commit repo over the copy answers the same
    `git ls-files` question for every file this fixture actually wrote, which is all these
    tests exercise — this is throwaway scaffolding for the test, never a commit to the
    project, so `--no-verify` here does not skip anything that matters.
    """
    def run(*args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=dest, capture_output=True, text=True, check=True,
        )

    run("init", "-q")
    run("-c", "user.email=test@example.invalid", "-c", "user.name=test", "add", "-A")
    run(
        "-c", "user.email=test@example.invalid", "-c", "user.name=test",
        "commit", "-q", "--no-verify", "-m", "throwaway copy for check-28 tests",
    )


@pytest.fixture(scope="module")
def repo_copy(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """A disposable copy of the whole repository, module-scoped so the ~30 MB copy (no
    `.git`, no `node_modules` here) happens once for every test in this file rather than
    once per test. Pytest deletes `tmp_path_factory`'s base directory itself; nothing here
    needs its own cleanup, unlike the fixture this replaces which `unlink()`ed a file it had
    written into the real `docs/plans/`.
    """
    dest = tmp_path_factory.mktemp("audit_docs_plan_acceptance") / "repo"
    shutil.copytree(ROOT, dest, ignore=_COPY_IGNORE)
    _init_throwaway_git_repo(dest)
    return dest


@pytest.fixture
def plans_dir(repo_copy: pathlib.Path) -> pathlib.Path:
    """`<repo_copy>/docs/plans` — a fresh scratch file is written here per test and removed
    afterward so the shared `repo_copy` fixture stays clean across the four tests in this
    module, exactly as the original fixture cleaned up the real `docs/plans/` it wrote into.
    """
    return repo_copy / "docs" / "plans"


def _run(repo_copy: pathlib.Path) -> subprocess.CompletedProcess[str]:
    script = repo_copy / "scripts" / "audit-docs.py"
    return subprocess.run(
        ["python3", str(script)], capture_output=True, text=True, cwd=repo_copy / "docs",
    )


def test_a_plan_after_the_cutoff_missing_the_field_is_refused(
    plans_dir: pathlib.Path, repo_copy: pathlib.Path,
) -> None:
    """A plan filed on/after the cutoff with no "Acceptance Standard" heading must fail the
    audit and name the file. The title deliberately avoids the phrase "acceptance standard"
    itself, so the check's own red-path proof is not accidentally satisfied by the fixture's
    title matching the heading it is supposed to be missing.
    """
    scratch = plans_dir / "2026-08-31-zz-scratch-check28-missing-field.md"
    scratch.write_text(
        "# Scratch plan for check 28's red path\n\n"
        "**Goal:** exercise the missing-field case.\n\n"
        "## Global Constraints\n\nNone.\n",
        encoding="utf-8",
    )
    try:
        result = _run(repo_copy)
        assert result.returncode != 0, result.stdout + result.stderr
        assert scratch.name in result.stdout, result.stdout
        assert "no \"Acceptance Standard\" heading" in result.stdout, result.stdout
    finally:
        scratch.unlink()


def test_a_legacy_plan_before_the_cutoff_is_never_flagged(
    plans_dir: pathlib.Path, repo_copy: pathlib.Path,
) -> None:
    """A plan filed before the cutoff, with no acceptance-standard field either, must never
    red — Ruling 46's "never retro-red-gate a frozen plan". It is counted in the aggregate
    legacy note line, not flagged per-file.
    """
    scratch = plans_dir / "2026-08-20-zz-scratch-check28-legacy.md"
    scratch.write_text(
        "# Scratch plan for check 28's legacy exemption\n\n"
        "**Goal:** exercise the pre-cutoff case — dated before 2026-08-31.\n\n"
        "## Global Constraints\n\nNone.\n",
        encoding="utf-8",
    )
    try:
        result = _run(repo_copy)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "All checks passed" in result.stdout, result.stdout
        assert scratch.name not in result.stdout, result.stdout
    finally:
        scratch.unlink()


def test_a_conforming_plan_after_the_cutoff_is_not_flagged(
    plans_dir: pathlib.Path, repo_copy: pathlib.Path,
) -> None:
    """The positive control: a plan dated on/after the cutoff that *does* carry a populated
    "Acceptance Standard" heading must pass. Without this case the two tests above could
    both go green by a check that exempts everything, or reds every plan-kind file
    regardless of content.
    """
    scratch = plans_dir / "2026-08-31-zz-scratch-check28-conforming.md"
    scratch.write_text(
        "# Scratch plan for check 28's positive control\n\n"
        "**Goal:** exercise the conforming case.\n\n"
        "## Acceptance Standard\n\n"
        "This plan is accepted when:\n\n1. Check 28 passes on this file.\n",
        encoding="utf-8",
    )
    try:
        result = _run(repo_copy)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "All checks passed" in result.stdout, result.stdout
        assert scratch.name not in result.stdout, result.stdout
    finally:
        scratch.unlink()


def test_a_bare_heading_with_no_content_is_refused(
    plans_dir: pathlib.Path, repo_copy: pathlib.Path,
) -> None:
    """An "Acceptance Standard" heading immediately followed by another heading — nothing
    under it — is "implied", not "actually defined" (`delivery-process.md` §5 step 4), and
    must still red even though the heading text itself is present.
    """
    scratch = plans_dir / "2026-08-31-zz-scratch-check28-bare-heading.md"
    scratch.write_text(
        "# Scratch plan for check 28's bare-heading case\n\n"
        "## Acceptance Standard\n\n"
        "## Global Constraints\n\nNone.\n",
        encoding="utf-8",
    )
    try:
        result = _run(repo_copy)
        assert result.returncode != 0, result.stdout + result.stderr
        assert scratch.name in result.stdout, result.stdout
        assert "has no content before the next heading" in result.stdout, result.stdout
    finally:
        scratch.unlink()
