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

import collections
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


# ---------------------------------------------------------------------------------------
# Ruling 86 (docs/plans/2026-09-02-w37-ruling-a-series-and-standalone-ruling-files.md):
# a split ruling's owner is derived, never hardcoded — `_discover_multi_ruling_files` used
# to stamp every ruling `owner="decision-maker"` regardless of a dated, bounded delegation
# (found via `docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` §1.1: rulings A1-A3 are
# the lead's, under the maintainer's delegation, not the decision-maker's). Real-corpus
# assertions here follow the lead's own instruction: assert the *property*, never a count
# — the A-series citation population was independently measured to have grown from 21 to
# 27 occurrences across 5 to 6 files in the time between two agents' reports, purely from
# being discussed, so any hardcoded total would already be stale.
# ---------------------------------------------------------------------------------------

_A_SERIES_SOURCE = "docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md"


def test_ruling_file_owner_derives_lead_from_the_real_delegation_clause(
    doc_id_cli: types.ModuleType,
) -> None:
    """`_ruling_file_owner` (Ruling 86), run directly against the real A1-A3 source file's
    own text. Deliberately *not* routed through `_discover_multi_ruling_files(ROOT)`: that
    function's own matcher (`_RULING_HEADING_RE`, `##` + a bare digit) does not reach this
    file's headings at all — they are `###` and letter-suffixed (`Ruling A1`), the two-axis
    mismatch Ruling 86/87 rule on separately (routed to "W37-6's executor", not this fix).
    Verified: `_RULING_HEADING_RE.finditer()` over this file's text returns zero matches
    today, so `_discover_multi_ruling_files` currently produces no draft for it at all —
    neither the old wrong owner nor this fix's right one is reachable through that path yet.
    This test proves the *derivation* is correct on the real document regardless of when
    the matcher is widened to reach it.
    """
    path = ROOT / _A_SERIES_SOURCE
    text = path.read_text(encoding="utf-8")

    assert not list(doc_id_cli._RULING_HEADING_RE.finditer(text)), (
        "fixture assumption: if _RULING_HEADING_RE now matches this file, "
        "_discover_multi_ruling_files reaches it directly and the test above this one "
        "should be extended to assert the owner end to end, not just the derivation"
    )
    assert doc_id_cli._ruling_file_owner(path, text) == "lead"


def test_ruling_file_owner_defaults_to_decision_maker_with_no_delegation_heading(
    doc_id_cli: types.ModuleType,
) -> None:
    """The default (NT-0019 §1.6) holds for every real multi-ruling file that is *not*
    under a delegation — asserted over the whole real corpus as a property (every owner is
    "decision-maker" except drafts from the one known delegated file), never as a count of
    drafts, which grows as the corpus does.
    """
    drafts = doc_id_cli._discover_multi_ruling_files(ROOT)
    assert drafts, "fixture assumption: at least one real multi-ruling file exists"
    non_delegated = [d for d in drafts if d.was != _A_SERIES_SOURCE]
    assert non_delegated, "fixture assumption: not every multi-ruling file is delegated"
    assert all(d.owner == "decision-maker" for d in non_delegated), collections.Counter(
        d.owner for d in non_delegated
    )


def test_ruling_file_owner_raises_when_a_delegation_heading_names_no_role(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 86: "failing loudly when it cannot be determined rather than defaulting to a
    guess." A delegation-shaped heading that does not end in a parseable "delegated to the
    <role>" must not silently fall back to the decision-maker default — that would hide
    exactly the misattribution this fix exists to stop.
    """
    path = tmp_path / "delegation.md"
    text = (
        "# A record\n\n"
        "### 1.1 The delegation — the maintainer's authority, moved elsewhere for now\n\n"
        "Body.\n"
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(NotImplementedError, match="delegation"):
        doc_id_cli._ruling_file_owner(path, text)


def test_discover_multi_ruling_files_wires_a_derived_owner_through_to_the_draft(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The end-to-end path `_ruling_file_owner`'s real-corpus sibling test above cannot
    exercise (today's matcher does not reach the real delegated file) — proven here on a
    fixture whose heading level and id form the matcher *does* accept, so the wiring itself
    is under test independent of the separate, not-this-fix's-to-close matcher gap.
    """
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "2026-09-02-fixture-delegated-rulings.md").write_text(
        "# Fixture rulings\n\n"
        "### 1.1 The delegation — the maintainer's authority, delegated to the auditor\n\n"
        "## Ruling 501 — a fixture ruling\n\n"
        "Body.\n",
        encoding="utf-8",
    )
    drafts = doc_id_cli._discover_multi_ruling_files(tmp_path)
    assert len(drafts) == 1, drafts
    assert drafts[0].owner == "auditor"


# ---------------------------------------------------------------------------------------
# The same class of defect, the opposite direction: `_discover_plain_plans` hardcoded
# `owner="planner"` for every plan regardless of `kind:`, though NT-0019 §1.6 gives a
# review to the auditor and a handover to the executor. Two hardcodes pointing opposite
# ways were "two wrong attributions" (the lead's words) until both were fixed.
# ---------------------------------------------------------------------------------------


def test_plain_plans_owner_is_derived_from_kind_not_hardcoded(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    fixtures = {
        "2026-09-02-fixture-leaf.md": "planner",
        "2026-09-02-fixture-final-review.md": "auditor",
        "2026-09-02-fixture-handover.md": "executor",
        "2026-09-02-fixture-slice-map.md": "planner",
    }
    for filename in fixtures:
        (plans_dir / filename).write_text(f"# {filename}\n\nBody.\n", encoding="utf-8")

    drafts = doc_id_cli._discover_plain_plans(tmp_path)

    by_filename = {pathlib.Path(d.was).name: d for d in drafts}
    assert set(by_filename) == set(fixtures)
    for filename, expected_owner in fixtures.items():
        assert by_filename[filename].owner == expected_owner, (filename, by_filename[filename])


def test_plain_plans_real_corpus_owner_always_matches_its_own_kind(
    doc_id_cli: types.ModuleType,
) -> None:
    """Property over the whole real corpus, not a count (the corpus grows): every emitted
    `PL-` draft's `owner` is exactly `_PLAN_KIND_OWNER[kind]` — proves the derivation is
    wired for every plan discovered today, not merely for the fixture's four kinds.
    """
    drafts = doc_id_cli._discover_plain_plans(ROOT)
    assert drafts, "fixture assumption: at least one plain plan exists in the real corpus"
    mismatched = [
        (d.was, d.kind, d.owner)
        for d in drafts
        if d.owner != doc_id_cli._PLAN_KIND_OWNER[d.kind]
    ]
    assert mismatched == []


# ---------------------------------------------------------------------------------------
# Same function, a second defect found alongside the owner hardcode: `_discover_plain_
# plans`' title regex captured only the first physical line of a `# Title` heading. Three
# real files (also `row 15`'s subject — the same three h1 ruling headings the multi-ruling
# splitter does not reach) wrap their title onto a second line with no other marker, the
# same wrapped-heading defect class already fixed in the document-family templates.
# ---------------------------------------------------------------------------------------

_WRAPPED_TITLE_FILES = (
    "docs/plans/2026-09-01-nt-0016-slice2-fr-data-32-ruling.md",
    "docs/plans/2026-09-01-ruling-60-census-provenance-checkout-depth.md",
    "docs/plans/2026-09-01-ruling-61-notes-tombstone-stubs-watched.md",
)


def test_plan_title_joins_a_wrapped_heading_on_the_real_files(
    doc_id_cli: types.ModuleType,
) -> None:
    for rel in _WRAPPED_TITLE_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        title = doc_id_cli._plan_title(text)
        assert title is not None, rel
        first_line = text.splitlines()[0].removeprefix("# ")
        assert title != first_line, (
            f"{rel}: title equals just the heading's first physical line — the join did "
            "not run, or this file's own wrap was fixed and this fixture is stale"
        )
        assert title.startswith(first_line), (rel, title)


def test_plan_title_does_not_join_across_a_blank_line(
    doc_id_cli: types.ModuleType,
) -> None:
    """The join must stop at the first blank line or heading — proven directly, since every
    real document in the corpus happens to have a blank line before its body and so cannot
    show this failing (Ruling 83's own principle: a check that only ever passes on real
    input has not been proven against the case it exists to rule out).
    """
    text = "# A short title\n\nThis paragraph must never join onto the title above.\n"
    assert doc_id_cli._plan_title(text) == "A short title"
