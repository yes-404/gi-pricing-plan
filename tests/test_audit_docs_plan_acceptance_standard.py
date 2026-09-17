"""`scripts/audit-docs.py`'s check 28: a filed plan states an explicit acceptance standard.

RFC-895 §2's C1 mechanises `delivery-process.md` §5 step 4 / §6 step 1 — the lead's
replan-vs-proceed check that "an acceptance standard was actually defined, not just
implied." The note's own draft mechanism ("warn until the format lands, red thereafter")
was **rejected** by RL-906
(`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`): a time-of-run switch makes the same
file pass on Tuesday and fail on Wednesday, and a fresh clone cannot reproduce a verdict.

RL-906 ruled a durable discriminator instead: **the plan's own filename date against a
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

**W37-6 (2026-09-17): re-pointed from a whole-repo subprocess copy to
`check_plan_acceptance_standard()` called directly, hermetically.** NT-0019's migration
moved the discriminator `check_plan_acceptance_standard()` itself reads from the plan's
*filename* date to its front-matter `created:` field (the function's own `post_migration`
branch), which the previous fixture shape — a bare markdown file with no header at all,
matching the pre-migration convention — can no longer reach past: on a migrated tree every
plan needs a stamp header just to be classified, so the old fixtures tripped a *different*,
earlier gate ("no front-matter header") before check 28's own heading logic ever ran, and
none of the assertions on the specific "no \"Acceptance Standard\" heading" / "has no
content before the next heading" wording matched any more.

Adding a *stamped* header to the old fixtures does not repair the whole-repo-copy approach
either: the real corpus's ids are now a fully-packed, gapless, chronologically-ordered
sequence (check 31 — 365/365 distinct numbers, zero gaps, `created` non-decreasing with the
number), so any new document a fixture adds to that live copy needs a number past the
corpus's ceiling, which forces its own `created:` date to be at least as late as everything
already in the corpus — exactly backwards from what
`test_a_legacy_plan_before_the_cutoff_is_never_flagged` needs to backdate. Check 28's own
tests were never meant to depend on a global invariant a *different* check (31) owns; the
fix is the same hermetic shape `tests/test_audit_docs_ids.py`'s `audit` fixture already uses
for checks 30-39 generally — load a fresh copy of the module, point its `ROOT` at an
isolated one-plan `docs/` directory, and call `check_plan_acceptance_standard()` on its own,
so nothing outside the fixture's own plan file can fail.

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence for
a numbered platform requirement, the same reasoning `tests/test_scope_audit.py` gives for
`scope-audit.py` and `tests/test_audit_docs_finding_citations.py` gives for check 25.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"


def _load_by_path(name: str, path: pathlib.Path) -> types.ModuleType:
    """Load a hyphenated `scripts/` module by path — `audit-docs.py` cannot be
    `import`ed by name. Same idiom `tests/test_audit_docs_ids.py`, `tests/test_doc_id.py`
    and `tests/test_doc_index.py` already use for their own scripts.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def audit() -> types.ModuleType:
    """A fresh load of `audit-docs.py` per test — the same reasoning
    `tests/test_audit_docs_ids.py`'s `audit` fixture gives: cheap, and no test has to
    remember to reset state a previous test mutated (`ROOT` is reassigned by every test
    below).
    """
    return _load_by_path("_audit_docs_plan_acceptance_under_test", SCRIPT)


@pytest.fixture
def docs_root(tmp_path: pathlib.Path) -> pathlib.Path:
    """A minimal `docs/` directory `migrated_tree()` reads as migrated — it looks only for
    `INDEX.md` and `REDIRECTS.csv` (see that function's own docstring) — and nothing else,
    so `check_plan_acceptance_standard()`'s `post_migration` branch runs without pulling in
    any other governed document, real or fixture.
    """
    docs = tmp_path / "docs"
    (docs / "plans").mkdir(parents=True)
    (docs / "INDEX.md").write_text("# index\n", encoding="utf-8")
    (docs / "REDIRECTS.csv").write_text("old,new\n", encoding="utf-8")
    return docs


def _run_check_28(audit: types.ModuleType, docs_root: pathlib.Path) -> list[str]:
    """Point `audit.ROOT` at the hermetic fixture directory and run check 28 alone,
    returning the failures it produced. `failures`/`notes` are cleared first so a
    fixture's own prior use (there is none in practice, since `audit` is function-scoped)
    can never leak between calls — the same guard `tests/test_audit_docs_ids.py`'s
    `_run_all_ten` applies for the same reason.
    """
    audit.failures.clear()
    audit.notes.clear()
    # `setattr`, not `audit.ROOT = docs_root`: `types.ModuleType`'s stub declares
    # `__getattr__` (so any *read* on a dynamically-loaded module type-checks as `Any`),
    # but no `__setattr__` — mypy has no fallback for an assignment to a name it cannot
    # statically find. `tests/test_audit_docs_ids.py`'s `_run_all_ten` hits the same trap
    # for the same reason; same fix.
    setattr(audit, "ROOT", docs_root)  # noqa: B010 -- mypy needs setattr here
    audit.check_plan_acceptance_standard()
    return list(audit.failures)


def _write_plan(docs_root: pathlib.Path, name: str, created: str, body: str) -> None:
    """A minimal post-migration plan: only `kind:`/`created:` populated, because that is
    all `check_plan_acceptance_standard()` itself reads (`_docid.parse_header`'s grammar
    accepts a header with only some of RFC-937's closed field set present — required-ness
    of the rest is check 30's policy, not this parser's or this check's).
    """
    (docs_root / "plans" / name).write_text(
        f"---\nkind: leaf\ncreated: {created}\n---\n{body}", encoding="utf-8",
    )


def test_a_plan_after_the_cutoff_missing_the_field_is_refused(
    audit: types.ModuleType, docs_root: pathlib.Path,
) -> None:
    """A plan filed on/after the cutoff with no "Acceptance Standard" heading must fail the
    audit and name the file. The title deliberately avoids the phrase "acceptance standard"
    itself, so the check's own red-path proof is not accidentally satisfied by the fixture's
    title matching the heading it is supposed to be missing.
    """
    name = "PL-90001-zz-scratch-check28-missing-field.md"
    _write_plan(
        docs_root, name, "2026-09-01",
        "# Scratch plan for check 28's red path\n\n"
        "**Goal:** exercise the missing-field case.\n\n"
        "## Global Constraints\n\nNone.\n",
    )
    failures = _run_check_28(audit, docs_root)
    assert len(failures) == 1, failures
    assert name in failures[0], failures
    assert "no \"Acceptance Standard\" heading" in failures[0], failures


def test_a_legacy_plan_before_the_cutoff_is_never_flagged(
    audit: types.ModuleType, docs_root: pathlib.Path,
) -> None:
    """A plan filed before the cutoff, with no acceptance-standard field either, must never
    red — RL-906's "never retro-red-gate a frozen plan". It is counted in the aggregate
    legacy note line, not flagged per-file.
    """
    name = "PL-90002-zz-scratch-check28-legacy.md"
    _write_plan(
        docs_root, name, "2026-08-20",
        "# Scratch plan for check 28's legacy exemption\n\n"
        "**Goal:** exercise the pre-cutoff case — dated before 2026-08-31.\n\n"
        "## Global Constraints\n\nNone.\n",
    )
    failures = _run_check_28(audit, docs_root)
    assert failures == []
    assert any("1 legacy plan" in note for note in audit.notes), audit.notes


def test_a_conforming_plan_after_the_cutoff_is_not_flagged(
    audit: types.ModuleType, docs_root: pathlib.Path,
) -> None:
    """The positive control: a plan dated on/after the cutoff that *does* carry a populated
    "Acceptance Standard" heading must pass. Without this case the two tests above could
    both go green by a check that exempts everything, or reds every plan-kind file
    regardless of content.
    """
    name = "PL-90003-zz-scratch-check28-conforming.md"
    _write_plan(
        docs_root, name, "2026-09-01",
        "# Scratch plan for check 28's positive control\n\n"
        "**Goal:** exercise the conforming case.\n\n"
        "## Acceptance Standard\n\n"
        "This plan is accepted when:\n\n1. Check 28 passes on this file.\n",
    )
    failures = _run_check_28(audit, docs_root)
    assert failures == [], failures


def test_a_bare_heading_with_no_content_is_refused(
    audit: types.ModuleType, docs_root: pathlib.Path,
) -> None:
    """An "Acceptance Standard" heading immediately followed by another heading — nothing
    under it — is "implied", not "actually defined" (`delivery-process.md` §5 step 4), and
    must still red even though the heading text itself is present.
    """
    name = "PL-90004-zz-scratch-check28-bare-heading.md"
    _write_plan(
        docs_root, name, "2026-09-01",
        "# Scratch plan for check 28's bare-heading case\n\n"
        "## Acceptance Standard\n\n"
        "## Global Constraints\n\nNone.\n",
    )
    failures = _run_check_28(audit, docs_root)
    assert len(failures) == 1, failures
    assert name in failures[0], failures
    assert "has no content before the next heading" in failures[0], failures
