"""Tests for `scripts/doc-id.py migrate` (W37-5) — NT-0019 §4's seven-step migration,
proven against the fixture corpus at `tests/fixtures/docs-migration/` before anything in
the real tree moves (W37-6).

Every test copies the fixture corpus into a fresh `tmp_path` before running `migrate`
against it — the committed fixture itself is never mutated by a test run, the same
discipline `git status --porcelain docs/` at the end of this slice's own PR is the proof
of at the real-repo level.

No `@pytest.mark.req` marker: this is correctness of the migration tool itself, not
evidence for a numbered platform requirement — `tests/test_doc_id.py`'s own module
docstring gives the identical reasoning for `next`/`check`/`widen`.
"""

from __future__ import annotations

import csv
import importlib.util
import pathlib
import subprocess
import sys
import types
from collections.abc import Sequence

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC_ID_SCRIPT_PATH = ROOT / "scripts" / "doc-id.py"
FIXTURE_CORPUS = ROOT / "tests" / "fixtures" / "docs-migration"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load_by_path(name: str, path: pathlib.Path, *, missing_module_name: str) -> types.ModuleType:
    """The identical loader `tests/test_doc_id.py` uses, for the identical reason (a
    hyphenated filename is not `import`able, and `sys.modules` registration must precede
    `exec_module` for this module's own dataclasses to resolve)."""
    if not path.exists():
        raise ModuleNotFoundError(f"No module named {missing_module_name!r}: not found at {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def doc_id_cli() -> types.ModuleType:
    return _load_by_path(
        "_doc_id_migrate_under_test", DOC_ID_SCRIPT_PATH, missing_module_name="doc_id"
    )


def _run_git(args: Sequence[str], *, cwd: pathlib.Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _git_tracked_copy(src: pathlib.Path, dest: pathlib.Path) -> pathlib.Path:
    """A fresh, fully git-tracked copy of `src` at `dest` — one commit, so `migrate`'s
    `git log --diff-filter=A` date fallback (for the roadmap and the register, which carry
    no date of their own) has real history to read, the same as a real checkout, rather
    than silently taking the "not a git repository" fallback path every test would
    otherwise exercise instead of the code this slice actually needs proven.
    """
    import shutil

    shutil.copytree(src, dest)
    _run_git(["init", "--initial-branch=main", "--quiet"], cwd=dest)
    _run_git(["config", "user.email", "test@example.com"], cwd=dest)
    _run_git(["config", "user.name", "Test"], cwd=dest)
    _run_git(["add", "-A"], cwd=dest)
    _run_git(["commit", "-m", "seed: pristine fixture corpus", "--quiet"], cwd=dest)
    return dest


@pytest.fixture
def pristine_a(tmp_path: pathlib.Path) -> pathlib.Path:
    return _git_tracked_copy(FIXTURE_CORPUS, tmp_path / "a")


@pytest.fixture
def pristine_b(tmp_path: pathlib.Path) -> pathlib.Path:
    return _git_tracked_copy(FIXTURE_CORPUS, tmp_path / "b")


def _tree_files(root: pathlib.Path) -> dict[str, bytes]:
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".git" not in path.parts:
            out[path.relative_to(root).as_posix()] = path.read_bytes()
    return out


# ---------------------------------------------------------------------------------------
# The two properties the dispatch pins: deterministic, and idempotent. Distinct tests,
# distinct mechanisms — determinism runs `migrate` twice from independent fresh copies of
# the *same* starting input; idempotency runs it a second time on its *own* output.
# ---------------------------------------------------------------------------------------


def test_migrate_is_deterministic_across_independent_runs(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path, pristine_b: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    doc_id_cli.migrate(pristine_b)
    files_a, files_b = _tree_files(pristine_a), _tree_files(pristine_b)
    assert set(files_a) == set(files_b)
    mismatched = {rel for rel in files_a if files_a[rel] != files_b[rel]}
    assert mismatched == set(), f"non-deterministic output in: {sorted(mismatched)}"


def test_migrate_assigns_the_same_numbers_on_independent_runs(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path, pristine_b: pathlib.Path
) -> None:
    """The tree-level byte comparison above already implies this, but the assignment
    itself — the part DP-3's dispatch calls out by name ("including the number
    assignment") — is asserted directly too, against `MigrateResult.assigned` rather than
    inferred from file contents matching.
    """
    result_a = doc_id_cli.migrate(pristine_a)
    result_b = doc_id_cli.migrate(pristine_b)
    assert result_a.assigned == result_b.assigned
    assert result_a.assigned  # not vacuously true — something was actually assigned


def test_migrate_is_idempotent_on_its_own_output(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    before = _tree_files(pristine_a)
    second = doc_id_cli.migrate(pristine_a)
    after = _tree_files(pristine_a)
    assert before == after
    assert second.assigned == ()  # nothing left to discover — zero new ids


# ---------------------------------------------------------------------------------------
# Acceptance item (a): every fixture file classifies to exactly one family, "none" is 0 —
# proven on the *migrated* fixture, the same tree state NT-0019 §7 (a) itself describes
# ("at the migration PR's merge tree"). This is §10's last line's "classification script
# ... as a test helper, not a separate script": a thin function living in this module,
# reusing `doc_id_cli.classify_docs_files` for `docs/` and extending it to `.claude/`
# rather than a second, parallel classifier.
# ---------------------------------------------------------------------------------------


def classify_every_governance_file(
    doc_id_cli: types.ModuleType, root: pathlib.Path
) -> dict[str, int]:
    """§10's last line, generalised past `docs/`: every tracked file under `root` — not
    only `docs/` — classified to exactly one family, "none" reserved for a file this
    classifier cannot place at all. `docs/` itself is `classify_docs_files` unmodified
    (Acceptance Standard item 3's own function, reused rather than re-derived — a second
    classifier is exactly the drift NT-0003 and Ruling 67 both warn against); `.claude/`
    is this helper's own small addition, since a fixture corpus this slice's dispatch asks
    for spans both roots and (a) is stated over the *whole* corpus, not `docs/` alone.
    """
    counts = dict(doc_id_cli.classify_docs_files(root))
    for rel in doc_id_cli.git_ls_files(root, ".claude"):
        parts = pathlib.Path(rel).parts
        if len(parts) >= 4 and parts[1] == "skills" and parts[3] == "SKILL.md":
            family = "reference"
        elif len(parts) >= 4 and parts[1] == "skills":
            is_vendored = doc_id_cli._docid.is_vendored(root / rel, root)
            family = "vendored-exempt" if is_vendored else "none"
        else:
            family = "none"
        counts[family] = counts.get(family, 0) + 1
    return counts


def test_acceptance_item_a_zero_unmapped_after_migration(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    # `classify_docs_files` reads `git ls-files` (the index), by the same design choice
    # every other id-tool function in this module makes (`compute_next`, `check`) — git
    # state is the *caller's* to update, never mutated as a side effect of a read or a
    # filesystem write. A real migration commit stages before verifying; this test does
    # the same, rather than reading `migrate`'s own filesystem writes through a stale
    # index and mistaking that staleness for an unmapped file.
    _run_git(["add", "-A"], cwd=pristine_a)
    counts = classify_every_governance_file(doc_id_cli, pristine_a)
    assert counts.get("none", 0) == 0, counts
    assert sum(counts.values()) > 0  # not vacuously true over an empty corpus


# ---------------------------------------------------------------------------------------
# Acceptance item (g), DP-3's executable form: `migration_diff_violations` is empty on a
# clean fixture run, and — Ruling 68 §4's own acceptance items — is provably non-empty on
# two kinds of broken input: a mutated body line, and an unclassifiable hunk.
# ---------------------------------------------------------------------------------------


def test_acceptance_item_g_clean_migration_has_no_violations(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    old_root = _git_tracked_copy(FIXTURE_CORPUS, tmp_path / "old")
    new_root = _git_tracked_copy(FIXTURE_CORPUS, tmp_path / "new")
    doc_id_cli.migrate(new_root)
    violations = doc_id_cli.migration_diff_violations(old_root, new_root)
    assert violations == []


def test_acceptance_item_g_catches_a_mutated_body_line(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 68 §4 item 1: "A mutation fixture ... makes `migrate` alter one word of a
    body line that is neither a header nor a reference token. Violation: (g) is empty on
    the mutated run ... It must be non-empty *and* name that file."
    """
    old_root = _git_tracked_copy(FIXTURE_CORPUS, tmp_path / "old")
    new_root = _git_tracked_copy(FIXTURE_CORPUS, tmp_path / "new")
    doc_id_cli.migrate(new_root)
    target = new_root / "docs" / "adrs" / "ADR-00002-example-fixtures-stay-dependency-free.md"
    text = target.read_text(encoding="utf-8")
    mutated = text.replace(
        "Fixture ADRs carry no real decision", "Fixture ADRs carry a MUTATED decision"
    )
    assert mutated != text
    target.write_text(mutated, encoding="utf-8")

    violations = doc_id_cli.migration_diff_violations(old_root, new_root)
    assert violations != []
    assert any("adr" in v.lower() or "ADR-00002" in v for v in violations), violations


def test_acceptance_item_g_catches_an_unclassifiable_hunk(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 68 §4 item 2: "Feed it a hunk in none of the six classes — a body line
    reordered within a file. Violation: an unclassifiable hunk that produces no output."
    Realised here as a new file appearing with no `REDIRECTS.csv` row explaining it —
    exactly what a body-line-reorder-via-rewrite would look like to a checker that
    compares whole-file content against a redirects-recorded provenance, since this
    checker's granularity is the file, not the line (Ruling 68's own acceptance items are
    stated at file granularity too — "(g) is not testing the script ... must be non-empty
    *and* name that file").
    """
    old_root = _git_tracked_copy(FIXTURE_CORPUS, tmp_path / "old")
    new_root = _git_tracked_copy(FIXTURE_CORPUS, tmp_path / "new")
    doc_id_cli.migrate(new_root)
    rogue = new_root / "docs" / "plans" / "PL-99999-not-in-any-redirect-row.md"
    rogue.write_text("---\nid: PL-99999\n---\n\n# Rogue\n", encoding="utf-8")

    violations = doc_id_cli.migration_diff_violations(old_root, new_root)
    assert any("PL-99999" in v for v in violations), violations


def test_acceptance_item_g_frozen_branch_shares_check_34s_predicate(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 68 §4 item 3: "Mutate check 34's DP-7 allowance. Violation: (g)'s
    frozen-family branch does not change with it." Proven by identity, not behaviour: the
    predicate `migration_diff_violations` calls is the *exact same function object*
    `scripts/audit-docs.py`'s own `check_freeze` uses, loaded from the one file, so any
    edit to it is felt by both call sites with no second definition to fall out of sync
    (the module-load idiom itself is the load-bearing part of this proof).
    """
    audit_docs = doc_id_cli._load_audit_docs()
    assert audit_docs.frozen_file_matches_after_migration_stamp is not None
    # `migration_diff_violations` loads the identical path via the identical `_load_module`
    # helper `check_freeze`'s own module uses internally — verified by reading both
    # functions' bodies rather than asserted here as an untestable claim about source text.
    import inspect

    source = inspect.getsource(doc_id_cli.migration_diff_violations)
    assert "_load_audit_docs()" in source
    assert "frozen_file_matches_after_migration_stamp" in source


# ---------------------------------------------------------------------------------------
# Spot checks on individual §4 steps — narrower than the whole-corpus properties above,
# so a future regression in one step is diagnosed without re-reading a tree diff.
# ---------------------------------------------------------------------------------------


def test_vendored_skill_manifest_is_stamped_but_files_beneath_are_untouched(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    skill_dir = pristine_a / ".claude" / "skills" / "vendored-example-skill"
    manifest = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert manifest.startswith("---\n")
    assert "vendored: true" in manifest
    assert "FR-13" in manifest  # its own citation rewrites

    beneath = (skill_dir / "references" / "extra.md").read_text(encoding="utf-8")
    assert not beneath.startswith("---\n")
    assert "FR-EX-1" in beneath  # untouched — the legacy token survives, by design
    assert "FR-13" not in beneath

    license_text = (skill_dir / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in license_text  # byte-for-byte untouched


def test_a_citation_with_no_corresponding_record_is_left_unrewritten(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    note = next((pristine_a / "docs" / "rfcs").glob("RFC-*.md")).read_text(encoding="utf-8")
    assert "wf-01" in note  # this corpus carries no workflow fixture to resolve it against


def test_adr_bullet_header_becomes_front_matter_and_body_is_preserved(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    adr_path = pristine_a / "docs" / "adrs" / "ADR-00002-example-fixtures-stay-dependency-free.md"
    adr = adr_path.read_text(encoding="utf-8")
    assert adr.startswith("---\n")
    assert "id: ADR-2" in adr
    assert "- **Status:**" not in adr  # the legacy bullet header is gone
    assert "- **Date:**" not in adr
    assert "## Context" in adr
    assert "## Decision" in adr
    assert "## Consequences" in adr


def test_multi_ruling_file_splits_one_per_ruling(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    rulings = sorted((pristine_a / "docs" / "rulings").glob("RL-*.md"))
    assert len(rulings) == 2
    first = rulings[0].read_text(encoding="utf-8")
    assert "preamble" in first.lower() or "multi-ruling" in first.lower()


# ---------------------------------------------------------------------------------------
# Task #31: `_discover_closure_records` no longer delegates to `_discover_headed_split_file`
# -- the real `docs/audit/closure-records.md` has record-level semantic variation (a phase
# close, two bespoke-audit records, several records not yet closed at all) the shared,
# one-shape-fits-all splitter cannot express. These build a synthetic `closure-records.md`
# directly under `tmp_path` (no `pristine_a`/git needed -- the date comes from each
# heading's own capture, not `_module_first_commit_date`'s git-log fallback), rather than
# widening the committed fixture corpus: every new legacy shape added there buys a
# permanent `LEGACY_FORM_EXCLUDED_PATHS` entry (Ruling 67 §4 item 1), and none of these
# shapes need to be *discovery-defining* content of a fixture demonstrating something else
# -- they only need to exist long enough for one `_discover_closure_records` call.
# ---------------------------------------------------------------------------------------


def test_closure_records_classifies_phase_audit_and_work_headings(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "closure-records.md").write_text(
        "### Phase 1a — exit demo accepted 2026-08-15\n\nPhase body.\n\n"
        "### Independent audit — 2026-08-15, and what it changed\n\nAudit body.\n\n"
        "### W1 — Repo foundations: closed 2026-08-14\n\nWork body.\n",
        encoding="utf-8",
    )
    drafts = doc_id_cli._discover_closure_records(tmp_path)
    assert [(d.prefix, d.kind, d.status) for d in drafts] == [
        ("CR", "phase", "active"),
        ("RS", "audit", "closed"),
        ("CR", "work", "active"),
    ]


def test_closure_records_raises_on_the_first_not_closed_heading(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Task #31's own defect, reproduced directly: an "in progress, not closed" heading
    must raise rather than silently fold into whichever heading matches next. Two such
    headings present, to confirm the raise names the *first* one -- a deterministic
    result, not whichever the implementation happens to hit.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "closure-records.md").write_text(
        "### W1 — Repo foundations: closed 2026-08-14\n\nWork body.\n\n"
        "### W5 — first undetermined thing, 2026-08-15 *(in progress, not closed)*\n\nBody.\n\n"
        "### W5 — second undetermined thing, 2026-08-16 *(in progress, not closed)*\n\nBody.\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError, match="first undetermined thing"):
        doc_id_cli._discover_closure_records(tmp_path)


def test_closure_records_is_silent_on_a_missing_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    assert doc_id_cli._discover_closure_records(tmp_path) == []


# ---------------------------------------------------------------------------------------
# Task #35 (plan-reviews line): `_REVIEW_HEADING_RE` required a heading to END with its
# date -- the identical end-anchor defect `_CLOSURE_HEADING_RE` carried before #585. The
# real `docs/audit/plan-reviews.md`'s "Plan review 9" heading has decoration AFTER its
# date (`... 2026-08-30 — **FILED, with its drafting history intact**`), so it matched
# nothing at all, and because sections run from one matched heading to the next, its
# entire body -- and three other unmatched, undated headings ahead of it -- folded into
# whichever matched heading precedes it in the file. Fixed the identical way #585 fixed
# it: widen the trailing anchor from `\s*$` (nothing but whitespace) to a captured
# `(.*)$` (anything to end of line).
#
# Scope, deliberately narrow: only the end-anchor defect is fixed here. The file's three
# UNDATED headings ("Candidate A", "Candidate B", "Also carried, and not a new rule") stay
# out of scope -- whether they are their own records or sub-content nested inside a
# neighbouring review is an open design question for the decision-maker (task #35's own
# deferral), and admitting them here would mint three governed documents for things that
# may not be documents, the mirror image of the defect this fix corrects. They are not
# silently dropped by that omission, but they do still fold into whichever matched
# heading precedes them -- the second test below pins that consequence down explicitly
# (both before and after this fix) rather than leaving it an unstated side effect.
# ---------------------------------------------------------------------------------------


def test_plan_reviews_discovers_a_heading_with_trailing_text_after_its_date(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The real decorated shape, not a simplified stand-in: `Plan review 9`'s actual
    heading carries an em-dash and bold decoration after its date. Before the fix this
    heading matches nothing, so its own record disappears and its body (here, "Body
    nine") is swallowed by the preceding matched heading's section -- silently wrong
    (folded into a plausible-looking neighbour), not loudly missing.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "plan-reviews.md").write_text(
        "### Plan review 1 — at W6a's close, 2026-08-15\n\nBody one.\n\n"
        "### Plan review 9 — at W11's close, 2026-08-30 — "
        "**FILED, with its drafting history intact**\n\nBody nine.\n\n"
        "### Plan review 10 — at W11's second close, 2026-08-30\n\nBody ten.\n",
        encoding="utf-8",
    )
    drafts = doc_id_cli._discover_plan_reviews(tmp_path)
    assert [d.title for d in drafts] == [
        "Plan review 1 — at W6a's close",
        "Plan review 9 — at W11's close",
        "Plan review 10 — at W11's second close",
    ]
    assert [d.created.isoformat() for d in drafts] == ["2026-08-15", "2026-08-30", "2026-08-30"]
    review_9 = drafts[1]
    assert "Body nine" in review_9.body
    assert "Body ten" not in review_9.body  # correctly bounded by the NEXT matched heading
    review_1 = drafts[0]
    assert "Plan review 9" not in review_1.body  # no longer swallowed by its predecessor
    assert "Body nine" not in review_1.body


def test_plan_reviews_still_folds_an_undated_heading_into_the_preceding_review(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Out of scope for `_discover_plan_reviews` itself, made loud rather than left an
    unstated side effect: an undated heading between two dated ones is not its own
    record either before or after this fix -- Ruling 82's own ruling, not guessed at
    here -- so this pure splitter still folds it into whichever matched heading
    precedes it. Uses a plain (already-matching) `Plan review 9` heading, not the
    decorated shape the test above exercises, so this isolates and pins a behaviour the
    narrower fix leaves UNCHANGED -- green both before and after -- rather than
    re-proving the fix itself.

    `_discover_plan_reviews` alone stays silent about this fold (that is what the
    assertions below show); `migrate` no longer is -- the census tests further below
    (Ruling 83) independently re-scan the same source and refuse rather than let this
    fold complete unremarked.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "plan-reviews.md").write_text(
        "### Plan review 1 — at W6a's close, 2026-08-15\n\nBody one.\n\n"
        "### Undated sub-heading, not a review\n\nSub content.\n\n"
        "### Plan review 9 — at W11's close, 2026-08-30\n\nBody nine.\n",
        encoding="utf-8",
    )
    drafts = doc_id_cli._discover_plan_reviews(tmp_path)
    assert len(drafts) == 2  # the undated heading never becomes a third record
    review_1 = drafts[0]
    assert "Undated sub-heading, not a review" in review_1.body  # folded in, not dropped
    assert "Sub content." in review_1.body


# ---------------------------------------------------------------------------------------
# Ruling 83 (row 1 of the W37-5b obligations list, `docs/plans/2026-09-02-w37-6-
# outstanding-obligations.md`): a guard may not derive its denominator from the same
# matcher it is checking -- `_check_legacy_file_not_silently_unrecognised`'s
# `if drafts: return` cannot distinguish "found every review" from "found ten of eleven",
# because both give it a non-empty list. `_check_plan_reviews_heading_census` re-scans
# `plan-reviews.md` independently, at every heading level (`^#{1,6}`), and classifies
# each heading into one of three buckets:
#
#   1. a record       -- matched by `_REVIEW_HEADING_RE` (widened above for Plan
#                         review 9's trailing text);
#   2. derived body    -- the file's own first heading (folds into the preamble, the
#                         same convention `_discover_headed_split_file` already uses)
#                         or any heading deeper than the split level (`###`, i.e.
#                         `####`+ -- real content in the actual file, nested inside
#                         several individual reviews' own bodies);
#   3. a declared exception -- none exist for this file today.
#
# Anything left over is named by line number and `migrate` refuses (`NotImplementedError`)
# rather than silently completing -- Ruling 83 §3 item 4. Ruling 82 found the three
# undated headings ("Candidate A", "Candidate B", "Also carried, and not a new rule") and
# their `##` parent ("Pending proposals") sub-content, not records, but left their
# POSITIVE family and `kind:` an open planner derivation (Ruling 82 §3 item 3) -- as of
# this branch's own rebase tip (`cc17404`) a candidate ("RFC- kind: process", #597) has
# been proposed but not ruled -- so this function still may not guess a bucket-3 reason
# for them. They are named unclassified below instead: the row 1 obligation is exactly
# to make that failure loud, not to resolve it.
#
# Additive, not a replacement, alongside the existing `_check_legacy_file_not_silently_
# unrecognised` call at this site (Ruling 83 §1(f): the two guards catch different
# things -- true zero-discovery versus a non-zero undercount -- and neither alone is
# sufficient). Synthetic `tmp_path` content throughout, per the same preference already
# used for the closure-records tests above.
# ---------------------------------------------------------------------------------------


def test_plan_reviews_heading_census_raises_naming_unclassified_headings_by_line(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The positive control Ruling 83 §4 requires: a `##` container plus its undated
    `###` children, sitting between two properly dated (and matched) reviews. Neither
    is a record, neither is derivably body (same level as the split, not deeper; not
    the file's own title), and nothing has declared them an exception -- so the census
    must refuse, naming both the container and its child by line number, rather than
    let `_discover_plan_reviews`'s ten (of what should read as more) pass as complete.

    The container heading fails TWO independent axes at once, the same shape the
    planner's row-6 derivation found for `Ruling A1`/`A2`/`A3` (PR #595): wrong heading
    level (`##`, not the `###` `_REVIEW_HEADING_RE` requires) AND no comma-then-date at
    all (`"drafted 2026-08-29"`, a parenthetical-style date introduction, not
    `_REVIEW_HEADING_RE`'s `,\\s*(\\d{4}-\\d{2}-\\d{2})`) -- confirmed by direct regex
    check against this exact string, not asserted. A positive control failing only one
    axis would go green under a fix that widened just that axis while leaving the
    census with nothing to catch; this one does not have that escape, and it is not a
    contrived case -- the real `## Pending proposals ... (drafted 2026-08-29)` heading
    in `docs/audit/plan-reviews.md` has the identical two-axis shape (verified directly
    against the real file), so this synthetic heading is not a simplified stand-in for
    it either.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "plan-reviews.md").write_text(
        "# Plan reviews\n\n"  # line 1: the file's own title -- derived body
        "### Plan review 1 — at W6a's close, 2026-08-15\n\nBody one.\n\n"  # line 3
        "## Pending proposals — drafted 2026-08-29\n\n"  # line 7: unclassified, 2-axis
        "### Candidate A — a proposal\n\nProposal body.\n\n"  # line 9: unclassified
        "### Plan review 9 — at W11's close, 2026-08-30\n\nBody nine.\n",  # line 13
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError) as exc_info:
        doc_id_cli._check_plan_reviews_heading_census(tmp_path)
    message = str(exc_info.value)
    assert "line 7" in message
    assert "Pending proposals" in message
    assert "line 9" in message
    assert "Candidate A" in message
    # the records and the title are not misreported as unclassified
    assert "line 3" not in message
    assert "line 1" not in message
    assert "line 13" not in message


def test_plan_reviews_heading_census_is_silent_when_every_heading_is_a_record_or_the_title(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "plan-reviews.md").write_text(
        "# Plan reviews\n\n"
        "### Plan review 1 — at W6a's close, 2026-08-15\n\nBody one.\n\n"
        "### Plan review 9 — at W11's close, 2026-08-30\n\nBody nine.\n",
        encoding="utf-8",
    )
    doc_id_cli._check_plan_reviews_heading_census(tmp_path)  # must not raise


def test_plan_reviews_heading_census_treats_a_deeper_heading_as_derived_body(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A `####` heading nested inside a review's own body (real content in the actual
    file -- e.g. every review's own "Sources" subsection) is deeper than the split
    level and must not be reported as unclassified, with no exception needing to be
    declared for it.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "plan-reviews.md").write_text(
        "# Plan reviews\n\n"
        "### Plan review 1 — at W6a's close, 2026-08-15\n\n"
        "#### Sources\n\nBody one.\n",
        encoding="utf-8",
    )
    doc_id_cli._check_plan_reviews_heading_census(tmp_path)  # must not raise


def test_plan_reviews_heading_census_is_silent_on_a_missing_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    doc_id_cli._check_plan_reviews_heading_census(tmp_path)  # no docs/ dir at all


def test_migrate_raises_via_the_plan_reviews_census_on_a_real_shaped_tree(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    """End-to-end: overwrite the fixture's own (clean) `plan-reviews.md` with the real
    tree's shape -- a `##` container of undated sub-content between two dated,
    otherwise-matching reviews -- and confirm `migrate` raises through the new census
    rather than silently completing with the container's content folded away.
    """
    (pristine_a / "docs" / "audit" / "plan-reviews.md").write_text(
        "# Plan reviews\n\n"
        "### Plan review 1 — at W6a's close, 2026-08-15\n\nBody one.\n\n"
        "## Pending proposals — drafted 2026-08-29\n\n"
        "### Candidate A — a proposal\n\nProposal body.\n\n"
        "### Plan review 9 — at W11's close, 2026-08-30\n\nBody nine.\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError, match="Pending proposals"):
        doc_id_cli.migrate(pristine_a)


def test_roadmap_restructure_is_readable_by_doc_index(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    """The roadmap output is not just well-formed prose — `scripts/doc-index.py`'s own
    `build_corpus`/`scan_roadmap_rows`/`scan_phase_sections` must actually parse it, since
    `migrate`'s own step 7 depends on exactly that (this is also where a real discrepancy
    between NT-0019 §1.3's plain, unfenced phase-block illustration and
    `doc-index.py`'s actual fenced-block parser was found — flagged in the PR description).
    """
    doc_id_cli.migrate(pristine_a)
    doc_index = doc_id_cli._load_doc_index()
    corpus = doc_index.build_corpus(pristine_a / "docs")
    families = sorted(h.family for h in corpus.headers())
    assert families.count("work") == 1
    assert families.count("slice") == 2
    phases = doc_index.scan_phase_sections(pristine_a / "docs" / "roadmap.md")
    assert len(phases) == 1
    assert phases[0].phase == "P1a"
    assert phases[0].works == ("WK-17",)


_UNRECOGNISED_ROADMAP_TEXT = (
    "# Roadmap\n\n"
    "## 6. Phase 1 — split into 1a and 1b\n\n"
    "#### Phase 1a status\n\n"
    "| WS | Scope | Status |\n"
    "|---|---|---|\n"
    "| **W1** | Repo foundations | open |\n"
    "| ~~**W2**~~ ✔ | Platform core | closed |\n"
)


# ---------------------------------------------------------------------------------------
# Task #32: `_discover_roadmap` returning nothing is ambiguous by construction between
# "already migrated" (the file moved, or its tokens changed shape) and "this shape is not
# recognised". `docs/roadmap.md` never moves, so the ambiguity is real for it in a way it
# is not for a moved/renamed legacy file. `_check_roadmap_not_silently_unrecognised`
# resolves it using the one signal that *is* checkable without deciding anything about the
# real shape or how to convert it: whether `docs/roadmap.md` already carries a `WK-` row
# (step 3's own output). Unit-level tests target that function directly; one end-to-end
# test proves `migrate` actually wires it in.
# ---------------------------------------------------------------------------------------


def test_roadmap_guard_raises_on_a_non_empty_unrecognised_roadmap(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "roadmap.md").write_text(_UNRECOGNISED_ROADMAP_TEXT, encoding="utf-8")
    with pytest.raises(NotImplementedError, match="unrecognised shape"):
        doc_id_cli._check_roadmap_not_silently_unrecognised(tmp_path)


def test_roadmap_guard_is_silent_when_no_roadmap_file_exists(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    doc_id_cli._check_roadmap_not_silently_unrecognised(tmp_path)  # no docs/ dir at all


def test_roadmap_guard_is_silent_on_a_blank_roadmap(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "roadmap.md").write_text("   \n\n  \n", encoding="utf-8")
    doc_id_cli._check_roadmap_not_silently_unrecognised(tmp_path)  # genuinely nothing there


def test_roadmap_guard_is_silent_once_a_wk_row_is_already_present(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The same unrecognised-shaped prose as the raising test above, but with one `WK-`
    row heading already present — the signal `migrate`'s own step 3 leaves behind, so this
    reads as "already migrated", not "unrecognised". Proves the guard is not just "does
    the legacy pattern fail to match" in disguise.
    """
    (tmp_path / "docs").mkdir()
    text = _UNRECOGNISED_ROADMAP_TEXT + "\n### WK-1201 — Batch frame contract\n"
    (tmp_path / "docs" / "roadmap.md").write_text(text, encoding="utf-8")
    doc_id_cli._check_roadmap_not_silently_unrecognised(tmp_path)


def test_migrate_raises_via_the_roadmap_guard_on_a_real_shaped_tree(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    """End-to-end: overwrite the fixture's own (recognisable) roadmap with the
    unrecognised-shaped text and confirm `migrate` itself raises through the guard, rather
    than silently completing steps 1/2/4-7 and reporting success on step 3. Every other
    fixture file is untouched, so this isolates the roadmap change from the rest of the
    corpus this same file's other tests already prove correct.
    """
    (pristine_a / "docs" / "roadmap.md").write_text(_UNRECOGNISED_ROADMAP_TEXT, encoding="utf-8")
    with pytest.raises(NotImplementedError, match="unrecognised shape"):
        doc_id_cli.migrate(pristine_a)


def test_roadmap_restructure_is_unaffected_by_the_guard(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    """The guard lives in the `else` branch of `if roadmap_drafts:` — confirms directly
    (not just by the existing tests still passing) that a *recognised* roadmap never
    reaches `_check_roadmap_not_silently_unrecognised` at all: `migrate` succeeds and the
    restructured file carries no trace of the guard ever running.
    """
    result = doc_id_cli.migrate(pristine_a)
    assert result is not None
    restructured = (pristine_a / "docs" / "roadmap.md").read_text(encoding="utf-8")
    assert "WK-" in restructured


# ---------------------------------------------------------------------------------------
# Task #34: `_check_legacy_file_not_silently_unrecognised` — the same conflation class as
# the roadmap's, for the three legacy files that are migrated by *moving away* rather than
# rewritten in place (`closure-records.md`, `plan-reviews.md`, `register.md`). Simpler than
# the roadmap's guard: a file still present at its exact legacy path has no valid "already
# migrated" reading, so there is no second signal to check — "moved away" and "file does
# not exist" are the same fact.
# ---------------------------------------------------------------------------------------


def test_legacy_file_guard_raises_on_a_non_empty_unrecognised_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    f = tmp_path / "legacy.md"
    f.write_text("### Some Heading, not a date\n\nbody\n", encoding="utf-8")
    with pytest.raises(NotImplementedError, match="real shape"):
        doc_id_cli._check_legacy_file_not_silently_unrecognised(f, [], "test records")


def test_legacy_file_guard_is_silent_once_the_file_has_moved_away(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    doc_id_cli._check_legacy_file_not_silently_unrecognised(
        tmp_path / "nonexistent.md", [], "test records"
    )


def test_legacy_file_guard_is_silent_on_a_blank_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    f = tmp_path / "legacy.md"
    f.write_text("   \n\n", encoding="utf-8")
    doc_id_cli._check_legacy_file_not_silently_unrecognised(f, [], "test records")


def test_legacy_file_guard_is_silent_when_drafts_were_found(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    f = tmp_path / "legacy.md"
    f.write_text("### Some Heading, not a date\n\nbody\n", encoding="utf-8")
    doc_id_cli._check_legacy_file_not_silently_unrecognised(f, [object()], "test records")


@pytest.mark.parametrize(
    "rel_path",
    [
        "docs/audit/closure-records.md",
        "docs/audit/plan-reviews.md",
        "docs/audit/register.md",
    ],
)
def test_migrate_raises_via_the_legacy_file_guard_on_a_real_shaped_tree(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path, rel_path: str
) -> None:
    """End-to-end, one per wired call site: overwrite just that one fixture file with
    prose carrying no recognisable heading/cell shape, leaving the rest of the corpus
    untouched, and confirm `migrate` raises through the guard rather than silently
    completing with that file's records missing.
    """
    (pristine_a / rel_path).write_text(
        "Some unrelated prose with no recognisable legacy shape at all.\n", encoding="utf-8"
    )
    with pytest.raises(NotImplementedError, match="real shape"):
        doc_id_cli.migrate(pristine_a)


def test_migrate_writes_nothing_when_a_vendored_manifest_is_unparseable(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    """Task #34: `_discover_vendored_skill_manifests` is hoisted to run alongside every
    other discovery, before any write — so a malformed manifest aborts `migrate` cleanly
    rather than crashing mid-write with the tree already partially mutated. Proves the
    property that actually matters: nothing was written at all, not merely that `migrate`
    raised (which the un-hoisted call also does, just after two write phases had already
    run — the exact defect task #34 files).
    """
    bad_skill_dir = pristine_a / ".claude" / "skills" / "bad-vendored-skill"
    bad_skill_dir.mkdir(parents=True)
    (bad_skill_dir / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (bad_skill_dir / "SKILL.md").write_text(
        "---\nname: bad-vendored-skill\nuser-invocable: true\n---\n\nBody.\n",
        encoding="utf-8",
    )
    before = _tree_files(pristine_a)
    with pytest.raises(doc_id_cli._docid.HeaderError):
        doc_id_cli.migrate(pristine_a)
    after = _tree_files(pristine_a)
    assert after == before, "migrate wrote something before the vendored-manifest crash"


def test_index_md_is_byte_stable_against_a_fresh_regeneration(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    doc_index = doc_id_cli._load_doc_index()
    on_disk = (pristine_a / "docs" / "INDEX.md").read_text(encoding="utf-8")
    fresh = doc_index.render_index(doc_index.build_corpus(pristine_a / "docs"))
    assert on_disk == fresh


def test_redirects_csv_records_every_old_id_and_path(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    with (pristine_a / "docs" / "REDIRECTS.csv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    old_ids = {row["old_id"] for row in rows if row["old_id"]}
    expected = {
        "NT-0001", "ADR-0001", "Ruling 1", "Ruling 2", "F1", "F2", "W1", "W1-1", "W1-2",
    }
    assert expected <= old_ids
    # Every row that names an old_path also names a new_path (never a dangling redirect).
    assert all((not row["old_path"]) or row["new_path"] for row in rows)


def test_register_finding_ids_are_renumbered_and_file_moves(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    assert not (pristine_a / "docs" / "audit" / "register.md").exists()
    register = (pristine_a / "docs" / "findings" / "register.md").read_text(encoding="utf-8")
    assert "| F1 " not in register
    assert "| F2 " not in register
    assert "FD-" in register


def test_no_legacy_directory_survives_once_emptied(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    for legacy in ("docs/notes", "docs/adr", "docs/audit"):
        assert not (pristine_a / legacy).exists(), legacy


def test_requirement_bold_ids_renumber_in_spec_module_order(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    doc_id_cli.migrate(pristine_a)
    spec = (pristine_a / "docs" / "specs" / "00-overview.md").read_text(encoding="utf-8")
    numbers = [
        int(m.group(2))
        for m in doc_id_cli._docid.ID_RE.finditer(spec)
        if m.group(1) in ("FR", "NFR", "OQ")
    ]
    assert numbers == sorted(numbers)  # clause order preserved, ascending
    assert len(numbers) == 4
    assert "FR-EX-1" not in spec
    assert "FR-EX-2" not in spec


# ---------------------------------------------------------------------------------------
# Ordering: the family-rank tie-break (NT-0019 §4 step 1) is exercised for real by this
# corpus — `docs/findings/register.md` (family rank: finding, last in §1.2's table) and
# `docs/roadmap.md` (work/slice, ranks 4-5) tie on the same git first-commit date (both
# seeded in the fixture's one commit), so the *lower*-ranked family (work/slice) must sort
# — and therefore number — ahead of the finding rows.
# ---------------------------------------------------------------------------------------


def test_family_rank_tie_break_orders_work_before_finding(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    result = doc_id_cli.migrate(pristine_a)
    numbered = {new: old for old, new in result.assigned if old}
    wk_number = int(next(n for n in numbered if n.startswith("WK-")).split("-")[1])
    fd_numbers = [int(n.split("-")[1]) for n in numbered if n.startswith("FD-")]
    assert wk_number < min(fd_numbers)
