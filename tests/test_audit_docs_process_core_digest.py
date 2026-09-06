"""`scripts/audit-docs.py`'s check 27: the process core extract's digest against the spec.

Check 26 is, by its own docstring, "the cheap half of a drift check": it resolves every
block's `source` § citation but compares no content. RL-905
(`docs/rulings/INDEX.md#2026-08-30-nt-0014-q1-q3-q4-rulingsmd`) verified the gap was not theoretical —
`delivery-process.md` took two commits past the extract's only commit, one of them adding
two normative rules to the section a guard block cites, and check 26 stayed green
throughout.

Check 27 is the other half: `meta.derived_from_digest` records a `sha256:` digest of the
exact bytes of `meta.derived_from` (`delivery-process.md`), paired with the commit that
digest was taken at (`meta.verified_against_tree`). §3's broken-input proof: "one byte
changed in `delivery-process.md` reds it, with a negative control changing a different file
that must stay green."

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence for
a numbered platform requirement — the same reasoning `tests/test_scope_audit.py` gives for
`scope-audit.py` and `tests/test_audit_docs_plan_acceptance_standard.py` gives for check 28.
"""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"
SPEC = ROOT / "docs" / "process" / "delivery-process.md"
CORE = ROOT / "docs" / "process" / "delivery-process.core.json"
ROADMAP = ROOT / "docs" / "roadmap.md"


def _run() -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", str(SCRIPT)], capture_output=True, text=True, cwd=ROOT)


def test_a_byte_changed_in_the_spec_reds_the_digest_check() -> None:
    """RL-905 §3's broken-input proof, first half: one byte changed in
    `delivery-process.md`, with the extract untouched, must red — the digest recorded on
    the extract no longer matches the spec's current bytes.
    """
    original = SPEC.read_text(encoding="utf-8")
    try:
        SPEC.write_text(original + "\n", encoding="utf-8")
        result = _run()
        assert result.returncode != 0, result.stdout + result.stderr
        assert "derived_from_digest" in result.stdout, result.stdout
        assert "does not match the current bytes" in result.stdout, result.stdout
    finally:
        SPEC.write_text(original, encoding="utf-8")


def test_a_missing_digest_field_reds() -> None:
    """`meta.derived_from_digest` absent entirely — not merely stale — must also red. A
    digest field nothing writes is indistinguishable from a true match unless its absence
    is itself a failure (`RFC-789`'s boundary-metric trap in another dress: a check silent
    on a missing field would let the mechanism be disarmed by deleting the field).
    """
    original = CORE.read_text(encoding="utf-8")
    try:
        assert '"derived_from_digest"' in original, "fixture assumption: field must exist first"
        lines = original.splitlines(keepends=False)
        line_removed = "\n".join(line for line in lines if '"derived_from_digest"' not in line)
        # Dropping the whole line leaves the JSON one key short but still valid — no other
        # line needs a trailing-comma fix, since derived_from_digest is not the last key
        # in meta and the preceding line keeps its own comma.
        CORE.write_text(line_removed + "\n", encoding="utf-8")
        result = _run()
        assert result.returncode != 0, result.stdout + result.stderr
        assert "`meta.derived_from_digest` is missing" in result.stdout, result.stdout
    finally:
        CORE.write_text(original, encoding="utf-8")


def test_an_unrelated_file_edit_is_the_negative_control_and_stays_green() -> None:
    """RL-905 §3's broken-input proof, second half: a negative control changing a
    *different* file must stay green — proof the check is reading `delivery-process.md`
    specifically, not failing on any repository change whatsoever.
    """
    original = ROADMAP.read_text(encoding="utf-8")
    try:
        ROADMAP.write_text(original + "\n", encoding="utf-8")
        result = _run()
        assert result.returncode == 0, result.stdout + result.stderr
        assert "check 27: process core digest matches" in result.stdout, result.stdout
    finally:
        ROADMAP.write_text(original, encoding="utf-8")


def test_the_committed_digest_currently_matches_the_committed_spec() -> None:
    """Positive control, unmodified: today's committed digest must match today's committed
    spec bytes — without this, the two red-path tests above could pass for the wrong
    reason (a check that reds unconditionally reds on a byte change too).
    """
    result = _run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "check 27: process core digest matches" in result.stdout, result.stdout
