"""`scripts/scope-audit.py`'s `--extra` flag refuses a token matching no requirement.

`--extra` used to be a literal `args.extra.split(",")` with no shared-prefix inheritance,
so the natural-looking `--extra FR-RATE-40,41,42,NFR-RATE-1,13,14` silently resolved to six
tokens — `FR-257`, `"41"`, `"42"`, `NFR-489`, `"13"`, `"14"` — four of which match no
requirement anywhere. `main` folded every extra token into scope regardless of whether it
was real, and an unmatched one still printed a `NO EVIDENCE` row indistinguishable from a
genuine, untested requirement. Worse: one bogus token simply replaced the id it silently
dropped, so the in-scope *count* still came out looking right — the headline figure a
reviewer checks is exactly the one that could not move. This already reached a live
dispatch and a task description before an auditor caught it by hand; PR #395 documented the
trap in `.claude/skills/close-workstream/SKILL.md`, and this is the root-cause fix it
tracked separately.

No `@pytest.mark.req` marker on anything here: this is correctness of the `CLAUDE.md` §13
audit tool itself, not evidence for a numbered platform requirement. `scope-audit.py` is
*cited as a method* by other requirements' tests (see
`tests/test_repository_invariants.py`'s module docstring), but nothing in `docs/specs/`
specifies the tool's own `--extra` behaviour.

Every case runs the script as a real subprocess, exactly as
`tests/test_repository_invariants.py` runs `audit-docs.py`: a hyphenated filename is not
importable, and a subprocess is also the only way to observe the actual exit code, which is
what the fix changed. The six ids fixed throughout — `FR-257/258/259`,
`NFR-489/502/501` — are real `RATE` requirements confirmed against
`docs/specs/03-rating-engine.md`: FR-257, FR-258, FR-259 sit under §3.8 and NFR-489/502/501 under
its NFR table, both outside `--sections 3.7`, so they only reach scope through `--extra`
and exercise exactly the path the fix touched.
"""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "scope-audit.py"

_VALID_SIX = (
    "FR-257,FR-258,FR-259,NFR-489,NFR-502,NFR-501"
)


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
    )


def test_a_bogus_token_is_refused_with_a_non_zero_exit_naming_it() -> None:
    """A well-formed-looking id that names no real requirement must fail loudly.

    Before the fix this token would have been folded straight into scope and printed as a
    `NO EVIDENCE` row — a state indistinguishable from a real, untested requirement.
    """
    result = _run("RATE", "--sections", "3.7", "--extra", "ZZ-NOPE-999")
    assert result.returncode != 0, result.stdout + result.stderr
    assert "'ZZ-NOPE-999'" in result.stdout
    assert "no RATE requirement has this id" in result.stdout
    # It must not also have been silently accepted into the in-scope report.
    assert "IN SCOPE  ZZ-NOPE-999" not in result.stdout


def test_a_token_with_no_id_shape_at_all_is_refused_the_same_way() -> None:
    """The refusal does not depend on the token merely *looking* like a requirement id."""
    result = _run("RATE", "--sections", "3.7", "--extra", "banana")
    assert result.returncode != 0, result.stdout + result.stderr
    assert "'banana'" in result.stdout
    assert "no RATE requirement has this id" in result.stdout


def test_the_real_world_comma_split_shape_is_refused_not_half_accepted() -> None:
    """The exact string that caused the incident, verbatim: `FR-RATE-40,41,42,NFR-RATE-1,13,14`.

    Comma-splitting turns six intended ids into six literal tokens, four of which —
    `"41"`, `"42"`, `"13"`, `"14"` — match no requirement. Each must get a targeted hint
    naming the prefix a human reader assumes it inherited from the id before it, and the
    whole list must be refused together: accepting `FR-257` and `NFR-489` alone
    while rejecting the rest would be the same half-accepted shape as the original defect,
    one level down.
    """
    result = _run(
        "RATE", "--sections", "3.7", "--extra", "FR-RATE-40,41,42,NFR-RATE-1,13,14"
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert "--extra names 4 token(s) matching no requirement" in result.stdout
    for bad, guess in [
        ("41", "FR-258"),
        ("42", "FR-259"),
        ("13", "NFR-502"),
        ("14", "NFR-501"),
    ]:
        assert f"'{bad}'" in result.stdout, result.stdout
        assert f"did you mean '{guess}'?" in result.stdout, result.stdout
    # No token from this list — valid or not — may reach the in-scope report.
    assert "IN SCOPE" not in result.stdout, result.stdout


def test_a_leading_bare_number_with_no_prior_valid_id_gets_the_plain_refusal() -> None:
    """A bare number cannot be given a prefix hint when nothing valid came before it.

    `last_prefix` is only set by a token already confirmed to be a real requirement, so a
    list that opens on a bare number (or one following another bad token) falls back to the
    plain "matches no requirement" refusal rather than guessing.
    """
    result = _run("RATE", "--sections", "3.7", "--extra", "41,FR-257")
    assert result.returncode != 0, result.stdout + result.stderr
    assert "'41' — no RATE requirement has this id" in result.stdout, result.stdout
    assert "did you mean" not in result.stdout, result.stdout


def test_an_id_belonging_to_a_different_module_is_refused() -> None:
    """`--extra` is scoped to the module under audit, matching every real invocation on
    record (`.claude/skills/close-workstream/SKILL.md`'s own `--extra FR-450,FR-451`
    example, and the RATE incident this suite is named for) — none of them cross a module
    boundary. `FR-450` is a real requirement (`docs/specs/07-platform.md`), just not a
    `RATE` one, so auditing `RATE` must refuse it rather than silently accept an id that
    belongs to a different module's spec.
    """
    result = _run("RATE", "--sections", "3.7", "--extra", "FR-450")
    assert result.returncode != 0, result.stdout + result.stderr
    assert "'FR-450' — no RATE requirement has this id" in result.stdout, result.stdout


def test_a_fully_qualified_extra_list_still_passes_unchanged() -> None:
    """Every id spelled out in full must not be rejected — the fix only refuses bad input.

    Structurally pinned rather than diffed against git history: 7 requirements live under
    `--sections 3.7` alone (confirmed by the no-`--extra` case below), plus these 6 via
    `--extra`, is 13 — a fact independent of which of the 13 currently carry test evidence,
    so this does not rot as coverage changes elsewhere in the suite.
    """
    result = _run("RATE", "--sections", "3.7", "--extra", _VALID_SIX)
    assert "--extra names" not in result.stdout, "a fully valid list must not be refused"
    for rid in (
        "FR-257", "FR-258", "FR-259",
        "NFR-489", "NFR-502", "NFR-501",
    ):
        assert f"IN SCOPE  {rid:<34}" in result.stdout, result.stdout
    assert "  in scope        : 13" in result.stdout, result.stdout


def test_no_extra_flag_at_all_is_unaffected_by_the_new_validation() -> None:
    """The common case — no `--extra` — never touches the new validation path at all."""
    result = _run("RATE", "--sections", "3.7")
    assert "--extra names" not in result.stdout
    assert "IN SCOPE  FR-257" not in result.stdout, "40..42 are §3.8, not §3.7"
    assert "  in scope        : 7" in result.stdout, result.stdout
