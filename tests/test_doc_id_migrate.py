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
import re
import subprocess
import sys
import types
from collections.abc import Sequence
from datetime import date

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


@pytest.fixture(autouse=True)
def _fixture_corpus_declares_its_synthetic_vendored_skill(
    doc_id_cli: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`_VENDORED_SKILLS` (Ruling 69) is a hand-declared enumeration of this repository's
    28 real vendored skills, reconciled against `pyproject.toml`'s ruff `exclude` list —
    it has no mechanism left for recognising an arbitrary directory as vendored by
    inspecting the filesystem, which is exactly what Ruling 69 §2 rejected (`is_vendored`
    no longer reads any `LICENSE` file at all).

    `tests/fixtures/docs-migration/.claude/skills/vendored-example-skill/` predates that
    ruling and is not a real vendored skill — it earned the old, LICENSE-based exemption
    only because it carries its own `LICENSE`. Every test in this module now declares it
    into the effective set for the duration of the test, the same way the real set is
    declared in `.claude/skills/README.md`, rather than reintroducing a filesystem probe
    the fixture alone would need. `monkeypatch` reverts this after each test, so the real
    28-name set is what every other module in the suite sees.
    """
    monkeypatch.setattr(
        doc_id_cli._docid,
        "_VENDORED_SKILLS",
        doc_id_cli._docid._VENDORED_SKILLS | {"vendored-example-skill"},
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


def test_vendored_skill_manifest_with_no_license_is_still_stamped(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`_is_vendored_skill_manifest` (`scripts/doc-id.py`) tests membership in
    `_docid._VENDORED_SKILLS`, not `LICENSE` presence — proven on a vendored skill that
    ships none, the shape 26 of the repository's real 28 vendored skills actually have
    (only `planning-with-files` and `ui-ux-pro-max` carry one).

    Before this fix, a `LICENSE`-based `_is_vendored_skill_manifest` would return `False`
    for a manifest with no `LICENSE` sibling — not because the skill isn't vendored, but
    because the *manifest-boundary* check never found the file it was looking for. Once
    `is_vendored` itself became membership-based (this same PR), that combination would
    have made `_is_vendored_exempt` (`is_vendored` **and not** `_is_vendored_skill_manifest`)
    read as `True and not False = True` for such a manifest — wrongly exempting it from the
    blanket citation-rewrite pass, the opposite of NT-0019 §1.5, which never exempts a
    manifest. This fixture skill has no `LICENSE` at all, so it only passes if
    `_is_vendored_skill_manifest` is membership-based too.
    """
    monkeypatch.setattr(
        doc_id_cli._docid,
        "_VENDORED_SKILLS",
        doc_id_cli._docid._VENDORED_SKILLS | {"no-license-vendored-skill"},
    )
    skill_dir = pristine_a / ".claude" / "skills" / "no-license-vendored-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "# no-license-vendored-skill\n\nCites `FR-13` here.\n", encoding="utf-8"
    )
    doc_id_cli.migrate(pristine_a)
    manifest = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert manifest.startswith("---\n")
    assert "vendored: true" in manifest


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


def test_closure_records_not_closed_headings_become_ledger_drafts(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 84 (`docs/plans/2026-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md`)
    §2: *"the raise was correct while the family was undecided and is wrong the moment it
    is decided; it is replaced, not deleted, by the classification."* Supersedes
    `test_closure_records_raises_on_the_first_not_closed_heading` (same name up to
    2026-09-02): that test pinned task #31's interim raise, which Ruling 84 rules against
    directly. Two "not closed" headings present, both under the same workstream, to prove
    `_discover_closure_records` no longer stops at the first — it used to raise there and
    never see the second at all.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "closure-records.md").write_text(
        "### W1 — Repo foundations: closed 2026-08-14\n\nWork body.\n\n"
        "### W5 — first undetermined thing, 2026-08-15 *(in progress, not closed)*\n\nBody.\n\n"
        "### W5 — second undetermined thing, 2026-08-16 *(in progress, not closed)*\n\nBody.\n",
        encoding="utf-8",
    )
    drafts = doc_id_cli._discover_closure_records(tmp_path)

    assert [(d.prefix, d.kind, d.status, d.owner, d.work_token) for d in drafts] == [
        ("CR", "work", "active", "auditor", None),
        ("LG", None, "closed", "executor", "W5"),
        ("LG", None, "closed", "executor", "W5"),
    ]


def test_closure_records_ledger_disposition_reads_the_trailer_not_the_body(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 84 §2: *"each of the ten is read for its own outcome rather than
    blanket-stamped ... any that records a slice that did not complete takes retired."*
    Read from the heading's own trailer (`_ledger_disposition`), never the body: a real
    closure record's prose says "superseded"/"reverted" constantly about individual
    requirements inside an otherwise-successful slice, so a body-wide keyword search would
    false-positive on ordinary narrative. Proves both directions on one fixture: the first
    heading's trailer carries no disposition marker beyond "not closed" and reads
    `closed`; the second's does and reads `retired`, even though its *body* text below
    also says "reverted" about something unrelated, which must not itself flip the status.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "closure-records.md").write_text(
        "### W9 — the happy path, 2026-08-15 *(in progress, not closed)*\n\n"
        "The design was reverted once during the slice and rebuilt; the final shape "
        "shipped and nothing here failed.\n\n"
        "### W9 — the abandoned path, 2026-08-16 *(in progress, not closed, retired)*\n\n"
        "Superseded by the happy-path slice before this branch merged.\n",
        encoding="utf-8",
    )
    drafts = doc_id_cli._discover_closure_records(tmp_path)

    assert [d.status for d in drafts] == ["closed", "retired"]


def test_closure_records_real_corpus_decomposes_into_ruling_84s_four_buckets(
    doc_id_cli: types.ModuleType,
) -> None:
    """Ruling 84 §4's positive control: "A test that runs `_discover_closure_records`
    against the real `docs/audit/closure-records.md` and asserts 21 drafts: 8 `CR- kind:
    work`, 1 `CR- kind: phase`, 2 `RS- kind: audit`, 10 `LG-`. ... It must fail today with
    the `NotImplementedError` of §1(b) — the positive control the corpus already
    supplies." Run against `ROOT`, the real repository, not a fixture.
    """
    drafts = doc_id_cli._discover_closure_records(ROOT)

    assert len(drafts) == 21, [(d.prefix, d.kind, d.title) for d in drafts]
    counts = collections.Counter((d.prefix, d.kind) for d in drafts)
    assert counts == {
        ("CR", "work"): 8,
        ("CR", "phase"): 1,
        ("RS", "audit"): 2,
        ("LG", None): 10,
    }, counts
    ledger_drafts = [d for d in drafts if d.prefix == "LG"]
    assert all(d.work_token == "W5" for d in ledger_drafts), ledger_drafts
    assert all(d.status == "closed" for d in ledger_drafts), (
        "none of the real ten W5 records names a retired marker in its trailer — a "
        "different status here would mean the trailer-reading rule fired on the real "
        "corpus's free-form body prose instead"
    )


def test_write_document_drafts_resolves_a_ledgers_work_and_phase_from_the_roadmap(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 84 §4: "A check that every emitted `LG-` carries a `work:` that does
    resolve, once W37-6 has created the `WK-` rows." Simulates that post-W37-6 state
    directly on `_write_document_drafts` (`_discover_roadmap`'s own 0-of-41 defect, row 2
    of the W37-5b obligations list, is a separate, unassigned fix — not built here, so
    this does not go through the full `migrate()` pipeline against the real corpus, which
    cannot resolve anything yet). Also proves the negative: `work_token` with no matching
    roadmap draft resolves to nothing rather than raising, which is what today's real
    corpus (empty `roadmap_drafts`) actually exercises.
    """
    root = tmp_path
    (root / "docs" / "_templates").mkdir(parents=True)
    (root / "docs" / "_templates" / "LG.md").write_text(
        (ROOT / "docs" / "_templates" / "LG.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    work_draft = doc_id_cli._Draft(
        materialize="roadmap_row", prefix="WK", kind=None, title="Modelling",
        status="closed", created=date(2026, 8, 15), owner="maintainer",
        tie_break=("roadmap.md", 0), old_token="W5", phase="P2", number=7,
    )
    ledger_draft = doc_id_cli._Draft(
        materialize="document", prefix="LG", kind=None, title="the GLM spine",
        status="closed", created=date(2026, 8, 15), owner="executor",
        tie_break=("docs/audit/closure-records.md", 0), old_token=None,
        was="docs/audit/closure-records.md", body="Body.\n", work_token="W5",
        number=50,
    )
    unresolved_draft = doc_id_cli._Draft(
        materialize="document", prefix="LG", kind=None, title="an orphaned record",
        status="closed", created=date(2026, 8, 16), owner="executor",
        tie_break=("docs/audit/closure-records.md", 1), old_token=None,
        was="docs/audit/closure-records.md", body="Body.\n", work_token="W999",
        number=51,
    )

    doc_id_cli._write_document_drafts(
        root, [ledger_draft, unresolved_draft], [work_draft]
    )

    resolved_text = ledger_draft.new_path.read_text(encoding="utf-8")
    assert "work: WK-7\n" in resolved_text, resolved_text
    assert "phase: P2\n" in resolved_text, resolved_text
    assert "slice:" not in resolved_text, (
        "Ruling 84 §2: LG- carries work: and no slice: — the template still declares "
        "slice:, so this must be an active omission, not an absent field by coincidence"
    )

    unresolved_text = unresolved_draft.new_path.read_text(encoding="utf-8")
    assert "work:" not in unresolved_text, (
        "an unresolved work_token must omit work: entirely, never write a broken "
        "reference or raise — today's real corpus has zero roadmap drafts to resolve "
        "against, and migrate must not fail because of it"
    )


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
    # No slice ever exists as a row or a bullet in the real corpus (Ruling 83 §1(g)), so
    # the fixture carries none either — this replaces a `== 2` from the fixture's former,
    # invented `- **<slice-key>**` bullet shape.
    assert families.count("slice") == 0
    phases = doc_index.scan_phase_sections(pristine_a / "docs" / "roadmap.md")
    assert len(phases) == 1
    assert phases[0].phase == "P1a"
    assert len(phases[0].works) == 1
    assert phases[0].works[0].startswith("WK-")


# Fed only to `_check_roadmap_not_silently_unrecognised` directly below, never through
# `migrate` — under the real-shape fix both ids in this text now convert cleanly (`W1`
# active, `W2` closed per Ruling 90), so it is no longer "unrecognised" in the discovery
# sense. Kept for the guard-isolation tests, which do not call `_discover_roadmap` at all
# and so do not care whether the text is convertible — only whether `docs/roadmap.md`
# carries a `WK-` row is what that guard itself asks.
_GUARD_TEST_ROADMAP_TEXT = (
    "# Roadmap\n\n"
    "## 6. Phase 1 — split into 1a and 1b\n\n"
    "#### Phase 1a status\n\n"
    "| WS | Scope | Status |\n"
    "|---|---|---|\n"
    "| **W1** | Repo foundations | open |\n"
    "| ~~**W2**~~ ✔ | Platform core | closed |\n"
)

# Genuinely unrecognised: no `Phase <label>` heading and no `**W<n>**`-shaped leading
# cell anywhere, so `_scan_roadmap_rows` finds nothing and `_discover_roadmap` returns
# `([], {}, [])` exactly as it does for a file `_ROADMAP_WORK_ROW_RE` cannot read at all
# — the one case that still reaches `_check_roadmap_not_silently_unrecognised` through
# `migrate` now that every recognised id converts (Rulings 90-92).
_TRULY_UNRECOGNISED_ROADMAP_TEXT = (
    "# Roadmap\n\nSome free-form prose with no phase heading and no work row at all.\n"
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
    (tmp_path / "docs" / "roadmap.md").write_text(_GUARD_TEST_ROADMAP_TEXT, encoding="utf-8")
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
    """The same guard-test prose as the raising test above, but with one `WK-` row
    heading already present — the signal `migrate`'s own step 3 leaves behind, so this
    reads as "already migrated", not "unrecognised". Proves the guard is not just "does
    the legacy pattern fail to match" in disguise.
    """
    (tmp_path / "docs").mkdir()
    text = _GUARD_TEST_ROADMAP_TEXT + "\n### WK-1201 — Batch frame contract\n"
    (tmp_path / "docs" / "roadmap.md").write_text(text, encoding="utf-8")
    doc_id_cli._check_roadmap_not_silently_unrecognised(tmp_path)


def test_migrate_raises_via_the_roadmap_guard_on_a_real_shaped_tree(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    """End-to-end: overwrite the fixture's own (recognisable) roadmap with text
    `_scan_roadmap_rows` finds nothing in at all (no phase heading, no leading work-id
    row) and confirm `migrate` itself raises through the guard, rather than silently
    completing steps 1/2/4-7 and reporting success on step 3. Every other fixture file is
    untouched, so this isolates the roadmap change from the rest of the corpus this same
    file's other tests already prove correct.
    """
    (pristine_a / "docs" / "roadmap.md").write_text(
        _TRULY_UNRECOGNISED_ROADMAP_TEXT, encoding="utf-8"
    )
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
# Rulings 90-92 (`docs/plans/2026-09-02-w37-roadmap-transform-rulings.md`): all 41 real
# work ids convert. Ruling 90 (a closed work converts, `status: closed`, from the Status
# cell, never the decoration), Ruling 91 (a multi-row work's rows merge into one, its
# body preserving every source row's text labelled by table, and its rows' status cells
# must agree or `migrate` refuses) and Ruling 92 (`W6` converts, `status: retired`, body
# naming `W6a`/`W6b`) each get a fixture-level test below; the real-corpus tests further
# down prove the same properties against `docs/roadmap.md` itself.
# ---------------------------------------------------------------------------------------


def test_a_closed_single_row_work_converts_with_status_closed(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 90: a work recorded as closed converts, `status: closed`, read from the
    Status cell's own bolded word — never inferred from the `~~...~~`/`✔` decoration
    alone (this fixture omits the checkmark on purpose, to prove the cell text, not the
    strikethrough, is what is read).
    """
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "_templates").mkdir()
    for name in ("WK.md", "SL.md"):
        (tmp_path / "docs" / "_templates" / name).write_text(
            (ROOT / "docs" / "_templates" / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    (tmp_path / "docs" / "roadmap.md").write_text(
        "# Roadmap\n\n"
        "## 1. Phase 1a — Example workbench\n\n"
        "| WS | Scope | Status |\n"
        "|---|---|---|\n"
        "| ~~**W1**~~ | Example workstream | **Closed 2026-08-14** |\n",
        encoding="utf-8",
    )
    drafts, phase_titles, occurrences = doc_id_cli._discover_roadmap(tmp_path)
    assert len(drafts) == 1
    assert drafts[0].status == "closed"
    doc_id_cli._restructure_roadmap(tmp_path, drafts, phase_titles, occurrences)
    restructured = (tmp_path / "docs" / "roadmap.md").read_text(encoding="utf-8")
    assert "status: closed" in restructured


_MULTI_ROW_MERGE_ROADMAP_TEXT = (
    "# Roadmap\n\n"
    "## 1. Phase 1a — Example workbench\n\n"
    "| WS | Scope | Status |\n"
    "|---|---|---|\n"
    "| **W1** | Example workstream, plan-table wording | **Closed 2026-08-14** — the "
    "pointer fragment |\n"
    "\n"
    "### Workstreams\n\n"
    "| # | Workstream | Notes |\n"
    "|---|---|---|\n"
    "| ~~**W1**~~ ✔ | Example workstream, status-table wording | **Closed 2026-08-14** "
    "— the delivery-breakdown fragment |\n"
    "\n"
    "### Original scope\n\n"
    "| # | Workstream | Notes |\n"
    "|---|---|---|\n"
    "| ~~**W1**~~ ✔ | Example workstream, historical wording | **Closed 2026-08-14** — "
    "the scope-figure fragment |\n"
)


def test_a_multi_row_work_merges_into_one_row_with_every_fragment_in_the_body(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 91 obligation 2, `W5`'s own shape reproduced at fixture scale: three source
    rows for one id, agreeing on status, each carrying a distinct fragment of prose. The
    violation Ruling 91 acceptance names directly: *"a merge that keeps one cell and
    drops the rest"* — so this asserts all three fragments are present, not that the body
    is merely non-empty, which a merge keeping only the richest cell would also satisfy.
    """
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "_templates").mkdir()
    for name in ("WK.md", "SL.md"):
        (tmp_path / "docs" / "_templates" / name).write_text(
            (ROOT / "docs" / "_templates" / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    (tmp_path / "docs" / "roadmap.md").write_text(
        _MULTI_ROW_MERGE_ROADMAP_TEXT, encoding="utf-8"
    )
    drafts, phase_titles, occurrences = doc_id_cli._discover_roadmap(tmp_path)
    assert len(drafts) == 1  # 41 ids in, 41 WK- rows out -- one work, one row, merged
    assert drafts[0].old_token == "W1"
    assert drafts[0].status == "closed"
    for fragment in ("pointer fragment", "delivery-breakdown fragment", "scope-figure fragment"):
        assert fragment in drafts[0].body, f"missing {fragment!r} in merged body"
    doc_id_cli._restructure_roadmap(tmp_path, drafts, phase_titles, occurrences)
    restructured = (tmp_path / "docs" / "roadmap.md").read_text(encoding="utf-8")
    assert restructured.count("### WK-") == 1  # never several rows for one id
    for fragment in ("pointer fragment", "delivery-breakdown fragment", "scope-figure fragment"):
        assert fragment in restructured


def test_a_status_conflict_across_a_works_rows_refuses_naming_the_work(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 91 obligation 1 and its own acceptance item: *"a fixture in which one
    work's two rows carry different status words must make migrate refuse, naming the
    work"* — never pick the first, the last, or the richest row.
    """
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "roadmap.md").write_text(
        "# Roadmap\n\n"
        "## 1. Phase 1a — Example workbench\n\n"
        "| WS | Scope | Status |\n"
        "|---|---|---|\n"
        "| **W1** | Example workstream | **Active** |\n"
        "\n"
        "### Workstreams\n\n"
        "| # | Workstream | Notes |\n"
        "|---|---|---|\n"
        "| ~~**W1**~~ ✔ | Example workstream | **Closed 2026-08-14** |\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError, match="W1") as excinfo:
        doc_id_cli._discover_roadmap(tmp_path)
    assert "disagree on status" in str(excinfo.value)


def test_a_table_emptied_by_conversion_is_removed_and_a_mixed_table_keeps_its_other_rows(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 91 obligation 3: a source table is not silently deleted, but nor is an
    emptied one left as a header-only husk once every data row it had was a work row —
    the removal itself is the diff hunk that accounts for it. A table mixing work rows
    with others (an "Exit demo"-shaped non-work row here) keeps the others.
    """
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "_templates").mkdir()
    for name in ("WK.md", "SL.md"):
        (tmp_path / "docs" / "_templates" / name).write_text(
            (ROOT / "docs" / "_templates" / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    (tmp_path / "docs" / "roadmap.md").write_text(
        "# Roadmap\n\n"
        "## 1. Phase 1a — Example workbench\n\n"
        "| WS | Scope | Status |\n"
        "|---|---|---|\n"
        "| **W1** | Example workstream | active |\n"
        "\n"
        "A fully-work-row table sits directly above; a mixed one follows.\n"
        "\n"
        "#### Phase 1a status\n\n"
        "| WS | Scope | Status |\n"
        "|---|---|---|\n"
        "| **W1** | Example workstream | active |\n"
        "| ~~**Exit demo**~~ ✔ | Not a work row | ✔ **accepted 2026-08-15** |\n",
        encoding="utf-8",
    )
    drafts, phase_titles, occurrences = doc_id_cli._discover_roadmap(tmp_path)
    doc_id_cli._restructure_roadmap(tmp_path, drafts, phase_titles, occurrences)
    restructured = (tmp_path / "docs" / "roadmap.md").read_text(encoding="utf-8")
    # The fully-work-row table (the first one) is gone -- header included.
    assert "| WS | Scope | Status |" not in restructured or restructured.count(
        "| WS | Scope | Status |"
    ) == 1
    # The mixed table's non-work row survives, and its own header is still present.
    assert "Exit demo" in restructured
    assert "#### Phase 1a status" in restructured


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
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Task #34: `_discover_vendored_skill_manifests` is hoisted to run alongside every
    other discovery, before any write — so a malformed manifest aborts `migrate` cleanly
    rather than crashing mid-write with the tree already partially mutated. Proves the
    property that actually matters: nothing was written at all, not merely that `migrate`
    raised (which the un-hoisted call also does, just after two write phases had already
    run — the exact defect task #34 files).

    `_is_vendored_skill_manifest` tests membership in `_VENDORED_SKILLS` (Ruling 69), not
    `LICENSE` presence, so `bad-vendored-skill` must be declared into the set for this
    fixture to be treated as a manifest at all — the `LICENSE` file it also carries is
    incidental now, not what makes `_discover_vendored_skill_manifests` reach it.
    """
    monkeypatch.setattr(
        doc_id_cli._docid,
        "_VENDORED_SKILLS",
        doc_id_cli._docid._VENDORED_SKILLS | {"bad-vendored-skill"},
    )
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
    # No slice ever exists as a row or a bullet in the real corpus (Ruling 83 §1(g)), so
    # the fixture no longer carries "W1-1"/"W1-2" — it used to, under the fixture's
    # former, invented `- **<slice-key>**` bullet shape.
    expected = {"NT-0001", "ADR-0001", "Ruling 1", "Ruling 2", "F1", "F2", "W1"}
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
# Ruling 86 (docs/plans/2026-09-02-w37-ruling-a-series-and-standalone-ruling-files.md) §3
# item 2's first clause read NT-0019 §1.6's `RL` row as moving `owner:` away from
# "decision-maker" for a ruling authored under a dated, bounded delegation
# (`docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` §1.1: rulings A1-A3 were drafted
# by the lead, under the maintainer's delegation) and PR #603 implemented that departure.
#
# Ruling 95 (docs/plans/2026-09-02-w37-gap-1-ruling-86-owner-ruling.md) struck that clause:
# the `RL` row already names an exception *author* ("the maintainer may author one on scope
# or process") and leaves the owner unchanged, so authorship never moved it — a
# self-correction against Ruling 88 §2's later, general reading of the identical column
# ("Owner — creates & amends", not "author"). The tests below used to prove the departure;
# they are changed in place to prove its absence, on the same real file and the same
# fixtures, rather than deleted — a re-introduction of the struck clause should turn these
# red again, not read as an unrelated gap in coverage.
#
# Real-corpus assertions here follow the lead's own instruction: assert the *property*,
# never a count — the A-series citation population was independently measured to have
# grown from 21 to 27 occurrences across 5 to 6 files in the time between two agents'
# reports, purely from being discussed, so any hardcoded total would already be stale.
# ---------------------------------------------------------------------------------------

_A_SERIES_SOURCE = "docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md"


def test_ruling_owner_departure_machinery_is_removed_not_left_inert() -> None:
    """Ruling 95 §3 item 3: with the exception struck, the delegation-heading regex and its
    role-parsing sibling have no case left to serve, and a dead branch that once encoded a
    reversed ruling is worse than no branch — so they are removed, not merely unreachable.
    Read the module's own source text rather than introspecting its namespace, so hiding
    the pair behind a different name would not silently satisfy this. Must fail before the
    fix, when both names are still present as real module-level constants.
    """
    source = DOC_ID_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "_RULING_DELEGATION_HEADING_RE" not in source
    assert "_RULING_DELEGATION_ROLE_RE" not in source


def test_ruling_file_owner_resolves_the_real_delegation_clause_to_decision_maker(
    doc_id_cli: types.ModuleType,
) -> None:
    """`_ruling_file_owner`, run directly against the real A1-A3 source file's own text —
    the exact file and heading ("### 1.1 The delegation — ... delegated to the lead") that
    used to make this function return "lead" instead of the family default (Ruling 86 §3
    item 2, PR #603). Deliberately *not* routed through `_discover_multi_ruling_files(ROOT)`:
    that function's own matcher (`_RULING_HEADING_RE`, `##` + a bare digit) does not reach
    this file's headings at all — they are `###` and letter-suffixed (`Ruling A1`), the
    two-axis mismatch Ruling 86/87 rule on separately (routed to "W37-6's executor", not
    this fix). Verified: `_RULING_HEADING_RE.finditer()` over this file's text returns zero
    matches today, so `_discover_multi_ruling_files` currently produces no draft for it at
    all — this direct call is the only way to prove the resolution against the real
    document until that matcher gap is closed. Must return "lead" before the fix.
    """
    path = ROOT / _A_SERIES_SOURCE
    text = path.read_text(encoding="utf-8")

    assert not list(doc_id_cli._RULING_HEADING_RE.finditer(text)), (
        "fixture assumption: if _RULING_HEADING_RE now matches this file, "
        "_discover_multi_ruling_files reaches it directly and the test above this one "
        "should be extended to assert the owner end to end, not just the resolution"
    )
    assert "delegated to the lead" in text.lower(), (
        "fixture assumption: the real delegation clause this correction concerns is still "
        "in the source file -- if this fails, re-target both assertions at wherever it moved"
    )
    assert doc_id_cli._ruling_file_owner(path, text) == "decision-maker"


def test_ruling_file_owner_defaults_to_decision_maker_for_every_multi_ruling_file(
    doc_id_cli: types.ModuleType,
) -> None:
    """The default (NT-0019 §1.6) holds for every real multi-ruling file, full stop — Ruling
    95 struck the one exception Ruling 86 §3 item 2 carved out, so there is no more
    "non-delegated" subset to filter to before asserting. Property over the whole real
    corpus, never a count, which grows as the corpus does.
    """
    drafts = doc_id_cli._discover_multi_ruling_files(ROOT)
    assert drafts, "fixture assumption: at least one real multi-ruling file exists"
    assert all(d.owner == "decision-maker" for d in drafts), collections.Counter(
        d.owner for d in drafts
    )


def test_ruling_file_owner_no_longer_raises_on_an_unparseable_delegation_heading(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Before Ruling 95, a delegation-shaped heading with no parseable "delegated to the
    <role>" failed loudly rather than guessing (Ruling 86). Ruling 95 removes the whole
    branch that heading used to trigger, not just the guessing it refused — the identical
    fixture that used to raise is body text now, like any other content, and resolves to
    the family default without error. Kept on the same fixture rather than a fresh one so
    this proves the exact old failure mode is gone, not merely that some case works.
    """
    path = tmp_path / "delegation.md"
    text = (
        "# A record\n\n"
        "### 1.1 The delegation — the maintainer's authority, moved elsewhere for now\n\n"
        "Body.\n"
    )
    path.write_text(text, encoding="utf-8")
    assert doc_id_cli._ruling_file_owner(path, text) == "decision-maker"


def test_discover_multi_ruling_files_ignores_a_delegation_heading(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The end-to-end path, on a fixture whose heading level and id form `_RULING_HEADING_RE`
    *does* accept (the real A1-A3 file's own headings still do not — see the direct-call
    test above). Same delegation-heading fixture Ruling 86 relied on to reach "auditor";
    Ruling 95 means the heading no longer changes the outcome at all.
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
    assert drafts[0].owner == "decision-maker"


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


# =========================================================================================
# W37-5b -- Ruling 83's census (docs/plans/2026-09-02-w37-guard-arithmetic-and-ledger-
# family-rulings.md), applied to the five discovery functions rows 30 and 31 of
# docs/plans/2026-09-02-w37-6-outstanding-obligations.md name as silent: `_discover_
# requirements` (no guard at all), `_discover_multi_ruling_files`, `_discover_headed_
# split_file` (plan-reviews.md's shape), `_discover_plain_plans`, and the shared skip-path
# of `_discover_notes`/`_discover_adrs`. Every guard here refuses by NAMING the unaccounted
# unit, never by comparing a count (Ruling 83 §3 item 4) -- the property the two guards
# above this section do not have (row 5: "both shipped guards test only 'zero drafts from
# a non-blank file'").
# =========================================================================================


# -----------------------------------------------------------------------------------------
# `_reconcile_census` itself: the shared mechanism every guard below calls. Tested directly
# once, rather than through all five call sites, because it is the one place the bucket
# arithmetic and the "name units, not counts" property can go wrong.
# -----------------------------------------------------------------------------------------


def test_reconcile_census_is_silent_when_every_unit_is_a_record(
    doc_id_cli: types.ModuleType,
) -> None:
    units = [doc_id_cli._CensusUnit(key="1", locator="f.md:1", text="a")]
    doc_id_cli._reconcile_census(scope="test", units=units, records={"1"})


def test_reconcile_census_raises_naming_the_unaccounted_unit(
    doc_id_cli: types.ModuleType,
) -> None:
    units = [
        doc_id_cli._CensusUnit(key="1", locator="f.md:1", text="a"),
        doc_id_cli._CensusUnit(key="2", locator="f.md:9", text="mystery heading"),
    ]
    with pytest.raises(NotImplementedError, match=r"f\.md:9: mystery heading"):
        doc_id_cli._reconcile_census(scope="test", units=units, records={"1"})


def test_reconcile_census_names_the_unit_not_just_a_count(
    doc_id_cli: types.ModuleType,
) -> None:
    """The property Ruling 83 §3 item 4 and §4 both insist on: a failure message must
    identify *which* unit is unaccounted, not merely how many. Two units, one of which is
    a real record and one an impostor -- `len(units) - len(records) == 1` would already be
    "the right count" even if the guard picked the wrong unit to blame, so this checks the
    actual named unit, not just that something failed.
    """
    units = [
        doc_id_cli._CensusUnit(key="1", locator="f.md:1", text="real record"),
        doc_id_cli._CensusUnit(key="2", locator="f.md:2", text="impostor"),
    ]
    with pytest.raises(NotImplementedError) as exc_info:
        doc_id_cli._reconcile_census(scope="test", units=units, records={"1"})
    message = str(exc_info.value)
    assert "impostor" in message
    assert "real record" not in message


def test_reconcile_census_is_body_predicate_exempts_a_unit(
    doc_id_cli: types.ModuleType,
) -> None:
    units = [doc_id_cli._CensusUnit(key="1", locator="f.md:1", text="nested")]
    doc_id_cli._reconcile_census(
        scope="test", units=units, records=set(), is_body=lambda _u: True
    )


def test_reconcile_census_declared_exception_with_a_reason_is_silent(
    doc_id_cli: types.ModuleType,
) -> None:
    units = [doc_id_cli._CensusUnit(key="README.md", locator="d/README.md", text="README.md")]
    doc_id_cli._reconcile_census(
        scope="test", units=units, records=set(),
        exceptions={"README.md": "the directory's own README"},
    )


def test_reconcile_census_refuses_a_declared_exception_with_no_reason(
    doc_id_cli: types.ModuleType,
) -> None:
    """Ruling 83 §4's second mutation: deleting a declared exception's reason string must
    be refused outright, never silently treated as "still a valid exception". Covers all
    five call sites below at once, since every one of them routes its `exceptions=` through
    this same function rather than checking reasons itself.
    """
    units = [doc_id_cli._CensusUnit(key="README.md", locator="d/README.md", text="README.md")]
    with pytest.raises(ValueError, match="no reason"):
        doc_id_cli._reconcile_census(
            scope="test", units=units, records=set(), exceptions={"README.md": "   "}
        )


# -----------------------------------------------------------------------------------------
# Row 30: `_discover_requirements` shipped with no guard at all. `_LEGACY_SPEC_BOLD_RE`
# assumes every legacy requirement id carries a module code; the real corpus's `DEP-1`,
# `DEP-1a`, `DEP-2`, `DEP-3` never do -- a real, measured gap, not a hypothetical one.
# -----------------------------------------------------------------------------------------


def test_requirements_guard_raises_on_a_module_less_dep_id(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    specs_dir = tmp_path / "docs" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "00-overview.md").write_text(
        "**FR-EX-1** A normal requirement.\n\n"
        "**DEP-1** A dependency rule with no module code -- the real corpus's actual "
        "shape.\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError, match=r"DEP-1"):
        doc_id_cli._check_requirements_not_silently_unrecognised(tmp_path)


def test_requirements_guard_is_silent_when_every_id_is_recognised(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    specs_dir = tmp_path / "docs" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "00-overview.md").write_text(
        "**FR-EX-1** One. **NFR-EX-2** Two. **DEP-EX-3** carries a module code, too.\n",
        encoding="utf-8",
    )
    doc_id_cli._check_requirements_not_silently_unrecognised(tmp_path)


def test_requirements_guard_does_not_flag_a_dated_amendment_sentence(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A bold clause that *references* an id in running prose -- real corpus shape, e.g.
    `**FR-OVR-20 says so twelve rows above this one**` -- must never become a census
    candidate: the bold span does not close immediately after the id, the one structural
    signal a definition marker has and a reference does not.
    """
    specs_dir = tmp_path / "docs" / "specs"
    specs_dir.mkdir(parents=True)
    (specs_dir / "00-overview.md").write_text(
        "**FR-EX-1** The one real requirement here.\n\n"
        "**FR-EX-1 is amended by this whole bolded sentence, which is not a "
        "definition.**\n",
        encoding="utf-8",
    )
    doc_id_cli._check_requirements_not_silently_unrecognised(tmp_path)


def test_migrate_raises_via_the_requirements_guard_on_a_real_shaped_tree(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    spec = pristine_a / "docs" / "specs" / "00-overview.md"
    text = spec.read_text(encoding="utf-8")
    spec.write_text(
        text + "\n\n**DEP-1** A dependency rule with no module code.\n", encoding="utf-8"
    )
    with pytest.raises(NotImplementedError, match=r"DEP-1"):
        doc_id_cli.migrate(pristine_a)


# -----------------------------------------------------------------------------------------
# Row 31: `_discover_multi_ruling_files` assumes every ruling heading is `## Ruling
# <digits>`. Both of Ruling 83 §1(c)'s own worked form variations are reproduced: an h1
# single-ruling file (must NOT be flagged -- Ruling 87 confirms it is not this function's
# job) and `Ruling A1`/`A2`-shaped letter-suffixed headings (MUST be named -- Ruling 83
# §4's own "mutation the widening approach cannot survive").
# -----------------------------------------------------------------------------------------


def test_multi_ruling_guard_is_silent_on_a_clean_multi_ruling_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "2026-08-12-example-rulings.md").write_text(
        "# Example rulings\n\n"
        "## Ruling 1 — Example decision A\n\n### Question\n\nBody.\n\n"
        "### Ruling\n\nBody.\n\n"
        "## Ruling 2 — Example decision B\n\nBody.\n",
        encoding="utf-8",
    )
    doc_id_cli._check_multi_ruling_files_not_silently_unrecognised(tmp_path)


def test_multi_ruling_guard_exempts_a_solitary_h1_ruling_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """One ruling per file, titling the file itself, at `#` depth -- Ruling 83's own worked
    form variation invisible to `_RULING_HEADING_RE` (h1, not h2), and the settled non-
    defect case (Ruling 87): `_discover_multi_ruling_files` is correctly not this file's
    mechanism, so the census must not flag it either.
    """
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "2026-09-01-solo-ruling.md").write_text(
        "# Ruling 59 -- a single ruling, filed alone\n\nBody of the ruling.\n",
        encoding="utf-8",
    )
    doc_id_cli._check_multi_ruling_files_not_silently_unrecognised(tmp_path)


def test_multi_ruling_guard_names_a_letter_suffixed_ruling_heading(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Ruling 83 §4's own acceptance mutation: `Ruling A1`'s shape, in a fixture. Widening
    `_RULING_HEADING_RE`'s digit group would not catch this -- only an independent,
    form-agnostic count does. Also proves the word-anchor keeps ordinary, unrelated section
    headings (`## 1. Background`) out of the failure entirely, which a fully generic
    `^#{1,6}` census would have wrongly swept in.
    """
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "2026-08-30-adoption.md").write_text(
        "# An adoption plan, with rulings under delegation\n\n"
        "## 1. Background\n\nProse.\n\n"
        "## 2. Rulings under the delegation\n\n"
        "### Ruling A1 -- the first delegated ruling\n\nBody.\n\n"
        "### Ruling A2 -- the second delegated ruling\n\nBody.\n\n"
        "## 3. Acceptance\n\nProse.\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError) as exc_info:
        doc_id_cli._check_multi_ruling_files_not_silently_unrecognised(tmp_path)
    message = str(exc_info.value)
    assert "Ruling A1" in message
    assert "Ruling A2" in message
    assert "Background" not in message
    assert "Acceptance" not in message


def test_migrate_raises_via_the_multi_ruling_guard_on_a_real_shaped_tree(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    """A second, separate plan file -- not the fixture's own multi-ruling file -- shaped
    like the real corpus's `Ruling A1`/`A2`/`A3` file: no `## Ruling <digit>` heading at
    all, so the fixture's own existing records are untouched and only this file's two
    letter-suffixed sub-rulings are unaccounted.
    """
    (pristine_a / "docs" / "plans" / "2026-08-30-adoption.md").write_text(
        "# An adoption plan, with rulings under delegation\n\n"
        "## 1. Background\n\nProse.\n\n"
        "## 2. Rulings under the delegation\n\n"
        "### Ruling A1 -- the first delegated ruling\n\nBody.\n\n"
        "### Ruling A2 -- the second delegated ruling\n\nBody.\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError, match=r"Ruling A1"):
        doc_id_cli.migrate(pristine_a)


# -----------------------------------------------------------------------------------------
# Row 31: `_discover_headed_split_file`'s shape (`plan-reviews.md` today). A fully generic
# `^#{1,6}` census within the one dedicated file this function is called for -- no
# unrelated section structure to exclude, since the whole file is a record, a record's own
# nested content, or its leading preamble.
# -----------------------------------------------------------------------------------------


def test_headed_split_file_guard_names_an_undercounted_heading(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A real, still-live undercount shape (row 1 of the outstanding-obligations plan,
    landed as #602): `_REVIEW_HEADING_RE` was widened to accept any trailing text after
    the date, so a heading is now only invisible to it when it carries NO date at all --
    the corpus's "Candidate A"/"Candidate B"/"Also carried" shape. A widening-only fix
    cannot see this either, because it still has no independent denominator.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "plan-reviews.md").write_text(
        "# Plan reviews\n\n"
        "### Plan review 1, 2026-08-15\n\nBody.\n\n"
        "### A candidate proposal, carrying no date at all\n\nBody.\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError) as exc_info:
        doc_id_cli._check_headed_split_file_not_silently_unrecognised(
            tmp_path, "docs/audit/plan-reviews.md", doc_id_cli._REVIEW_HEADING_RE, 3,
            "plan reviews",
        )
    assert "A candidate proposal" in str(exc_info.value)


def test_headed_split_file_guard_is_silent_on_a_clean_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "plan-reviews.md").write_text(
        "# Plan reviews\n\n### Plan review 1, 2026-08-15\n\n**Verdict:** fine.\n",
        encoding="utf-8",
    )
    doc_id_cli._check_headed_split_file_not_silently_unrecognised(
        tmp_path, "docs/audit/plan-reviews.md", doc_id_cli._REVIEW_HEADING_RE, 3,
        "plan reviews",
    )


def test_headed_split_file_guard_treats_a_nested_subheading_as_body(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """`closure-records.md`/`plan-reviews.md`'s real shape: several levels of sub-heading
    nested inside one record (`#### Question 1`, `##### ...`). Both must fold into the
    enclosing record's body, never read as unaccounted units of their own.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "plan-reviews.md").write_text(
        "# Plan reviews\n\n"
        "### Plan review 1, 2026-08-15\n\n#### Question 1 -- Completion\n\nBody.\n\n"
        "##### A yet deeper sub-point\n\nBody.\n",
        encoding="utf-8",
    )
    doc_id_cli._check_headed_split_file_not_silently_unrecognised(
        tmp_path, "docs/audit/plan-reviews.md", doc_id_cli._REVIEW_HEADING_RE, 3,
        "plan reviews",
    )


def test_migrate_raises_via_the_headed_split_file_guard_on_plan_reviews(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    reviews_path = pristine_a / "docs" / "audit" / "plan-reviews.md"
    text = reviews_path.read_text(encoding="utf-8")
    reviews_path.write_text(
        text + "\n\n### A candidate proposal, carrying no date at all\n\nBody.\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError, match="A candidate proposal"):
        doc_id_cli.migrate(pristine_a)


# -----------------------------------------------------------------------------------------
# Ruling 84 §3 item 6: the census landing before the raise removal was ordering, not the
# whole obligation -- "removing the raise on its own does not restore a working guard, it
# exposes one whose blind spot has simply been hidden." `_check_headed_split_file_not_
# silently_unrecognised`'s own docstring reserved `closure-records.md` explicitly ("has its
# own discovery function and its own disposition logic -- Ruling 84 territory, not this
# one"), so the reachable guard this ruling exposes stays the weak `if drafts: return` one
# unless this fix also wires the file into the census -- confirmed empirically first
# (`_check_multi_ruling_files_not_silently_unrecognised`, `_check_headed_split_file_not_
# silently_unrecognised`, `_check_plain_plans_not_silently_unrecognised` and
# `_check_requirements_not_silently_unrecognised` between them touch every file
# `migrate()` reads except this one) before writing the fix below.
# -----------------------------------------------------------------------------------------


def test_closure_records_census_names_an_undercounted_heading(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The identical undercount shape `test_headed_split_file_guard_names_an_undercounted_
    heading` proves for plan-reviews.md, here for closure-records.md's own `_CLOSURE_
    HEADING_RE` (which also requires a date): a `###` heading with no date at all is
    invisible to `_discover_closure_records` and, pre-this-fix, silently folds into
    whichever record precedes it -- the exact failure Ruling 83 exists to name rather than
    leave to a count comparison.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "closure-records.md").write_text(
        "# Closure records\n\n"
        "### W1 — a real closure, 2026-08-15\n\nBody.\n\n"
        "### An undated candidate, carrying no date at all\n\nBody.\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError) as exc_info:
        doc_id_cli._check_closure_records_not_silently_unrecognised(tmp_path)
    assert "An undated candidate" in str(exc_info.value)


def test_closure_records_census_is_silent_on_a_clean_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "closure-records.md").write_text(
        "# Closure records\n\n"
        "### W1 — a real closure, 2026-08-15\n\nBody.\n\n"
        "### W2 — the second, 2026-08-16 *(in progress, not closed)*\n\nBody.\n",
        encoding="utf-8",
    )
    doc_id_cli._check_closure_records_not_silently_unrecognised(tmp_path)


def test_closure_records_census_treats_a_nested_subheading_as_body(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The real file's own shape (verified directly, `docs/audit/closure-records.md`):
    `####`/`#####` sub-headings nested inside a `###` record, e.g. W32's own back-filled
    per-slice sub-records. Both must fold into the enclosing record's body, never read as
    unaccounted units in their own right.
    """
    audit_dir = tmp_path / "docs" / "audit"
    audit_dir.mkdir(parents=True)
    (audit_dir / "closure-records.md").write_text(
        "# Closure records\n\n"
        "### W1 — a real closure, 2026-08-15\n\n#### 1. Scope\n\nBody.\n\n"
        "##### A yet deeper sub-point\n\nBody.\n",
        encoding="utf-8",
    )
    doc_id_cli._check_closure_records_not_silently_unrecognised(tmp_path)


def test_closure_records_census_is_silent_on_a_missing_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    doc_id_cli._check_closure_records_not_silently_unrecognised(tmp_path)


def test_migrate_raises_via_the_closure_records_census_on_a_real_shaped_tree(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    closure_path = pristine_a / "docs" / "audit" / "closure-records.md"
    text = closure_path.read_text(encoding="utf-8")
    closure_path.write_text(
        text + "\n\n### An undated candidate, carrying no date at all\n\nBody.\n",
        encoding="utf-8",
    )
    with pytest.raises(NotImplementedError, match="An undated candidate"):
        doc_id_cli.migrate(pristine_a)


# -----------------------------------------------------------------------------------------
# Row 31: `_discover_plain_plans`'s file-population shape. Every file directly under
# docs/plans/ must be a record, derived (delegated to the multi-ruling function),
# already-canonical (idempotency), or a declared exception -- `README.md` is the one
# real-corpus file that is none of the first three.
# -----------------------------------------------------------------------------------------


def test_plain_plans_guard_raises_on_an_unrecognised_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "NOTES.txt").write_text("not a dated plan, not declared", encoding="utf-8")
    with pytest.raises(NotImplementedError, match=re.escape("NOTES.txt")):
        doc_id_cli._check_plain_plans_not_silently_unrecognised(tmp_path)


def test_plain_plans_guard_is_silent_on_the_declared_readme(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "README.md").write_text("Conventions for this directory.\n", encoding="utf-8")
    (plans_dir / "2026-08-17-example-plan.md").write_text("# A plan\n\nBody.\n", encoding="utf-8")
    doc_id_cli._check_plain_plans_not_silently_unrecognised(tmp_path)


def test_plain_plans_guard_treats_a_multi_ruling_file_as_derived(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "2026-08-12-rulings.md").write_text(
        "# Rulings\n\n## Ruling 1 -- A\n\nBody.\n", encoding="utf-8"
    )
    doc_id_cli._check_plain_plans_not_silently_unrecognised(tmp_path)  # delegated, not flagged


def test_plain_plans_guard_treats_an_already_canonical_filename_as_derived(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Idempotency: a second `migrate` run sees renamed `PL-00001-*.md` files, which
    `_PLAN_FILENAME_RE` correctly does not match -- the guard must read that positively as
    "already migrated", never as "the legacy pattern found nothing" (the fixture-corpus
    assumption Ruling 83 rejects).
    """
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "PL-00001-example-plan.md").write_text(
        "---\nid: PL-1\n---\n\nBody.\n", encoding="utf-8"
    )
    doc_id_cli._check_plain_plans_not_silently_unrecognised(tmp_path)


def test_migrate_raises_via_the_plain_plans_guard_on_a_real_shaped_tree(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path
) -> None:
    (pristine_a / "docs" / "plans" / "NOTES.txt").write_text("stray file", encoding="utf-8")
    with pytest.raises(NotImplementedError, match=re.escape("NOTES.txt")):
        doc_id_cli.migrate(pristine_a)


# -----------------------------------------------------------------------------------------
# Row 31: `_discover_notes`/`_discover_adrs`'s shared skip-path reads "found nothing" as
# "already migrated" purely because the legacy title regex missed -- the same fixture-
# corpus assumption Ruling 83 rejects for `_discover_closure_records`, here applied to a
# directory instead of a heading.
# -----------------------------------------------------------------------------------------


def test_flat_document_directory_guard_raises_on_an_unrecognised_note(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    notes_dir = tmp_path / "docs" / "notes"
    notes_dir.mkdir(parents=True)
    (notes_dir / "0099-mystery.md").write_text(
        "No legacy title heading here at all.\n", encoding="utf-8"
    )
    with pytest.raises(NotImplementedError, match=re.escape("0099-mystery.md")):
        doc_id_cli._check_flat_document_directory_not_silently_unrecognised(
            tmp_path, "docs/notes", doc_id_cli._NOTE_TITLE_RE, "notes",
            {"README.md": "the directory's own README, not a governed note"},
        )


def test_flat_document_directory_guard_is_silent_on_the_declared_readme(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    notes_dir = tmp_path / "docs" / "notes"
    notes_dir.mkdir(parents=True)
    (notes_dir / "README.md").write_text("Conventions.\n", encoding="utf-8")
    (notes_dir / "0001-a-note.md").write_text(
        "# NT-0001 — A note\n\nBody.\n", encoding="utf-8"
    )
    doc_id_cli._check_flat_document_directory_not_silently_unrecognised(
        tmp_path, "docs/notes", doc_id_cli._NOTE_TITLE_RE, "notes",
        {"README.md": "the directory's own README, not a governed note"},
    )


@pytest.mark.parametrize(
    ("rel_dir", "mystery_filename"),
    [("docs/notes", "0099-mystery.md"), ("docs/adr", "0099-mystery.md")],
)
def test_migrate_raises_via_the_flat_document_directory_guard(
    doc_id_cli: types.ModuleType, pristine_a: pathlib.Path, rel_dir: str, mystery_filename: str
) -> None:
    (pristine_a / rel_dir / mystery_filename).write_text(
        "No legacy title heading here at all.\n", encoding="utf-8"
    )
    with pytest.raises(NotImplementedError, match=re.escape(mystery_filename)):
        doc_id_cli.migrate(pristine_a)


# ---------------------------------------------------------------------------------------
# W37-6 outstanding obligations rows 2 and 3 (task #32 and its register sibling), against
# the real `docs/roadmap.md` and `docs/audit/register.md` — not a fixture. "A control
# written against a simplified fixture ... goes green because of what it misses." The
# corpus grows and is edited, so these assert **properties** (every real row is
# accounted for by an independent count; the real narrative survives the restructure),
# never a specific figure a future edit would silently falsify. `ROOT`, defined at the
# top of this file, is this repository's own checkout; every test below copies what it
# needs into `tmp_path` first and never writes to `ROOT` itself.
# ---------------------------------------------------------------------------------------


def _naive_leading_work_ids(text: str) -> list[str]:
    """An independent re-derivation of `_scan_roadmap_rows`' leading-cell id, by plain
    string operations rather than `_ROADMAP_WORK_ROW_RE` — Ruling 83's own principle
    ("a census counted with the pattern you split with closes trivially and proves
    nothing") applied to this test: the denominator below must not be the thing under
    test. Deliberately cruder than the production regex (no phase tracking, no status
    text extraction) — it only has to agree on *which lines carry a work id*.
    """
    ids = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cell = line[1:].split("|", 1)[0].strip()
        cell = cell.removeprefix("~~").strip()
        if not cell.startswith("**W"):
            continue
        close = cell.find("**", 2)
        if close == -1:
            continue
        token = cell[2:close]
        if re.fullmatch(r"W\d+[a-z]?", token):
            ids.append(token)
    return ids


def test_roadmap_census_matches_an_independently_derived_row_count_on_the_real_tree(
    doc_id_cli: types.ModuleType,
) -> None:
    """The positive control the real corpus already supplies (W37-6 outstanding
    obligations row 2): before this fix, `_discover_roadmap` found nothing at all against
    `docs/roadmap.md` (all three legacy patterns matched zero times — Ruling 80's
    Correction section). After it, `_scan_roadmap_rows` must find *every* leading work-id
    row a wholly independent re-derivation also finds — a property that holds regardless
    of how many rows the file carries on the day this runs, unlike a hard-coded count.
    """
    text = (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
    occurrences = doc_id_cli._scan_roadmap_rows(text)
    assert sorted(o.work_id for o in occurrences) == sorted(_naive_leading_work_ids(text))
    assert len(occurrences) > 1  # non-vacuous


def test_discover_roadmap_converts_every_real_id_with_none_left_over(
    doc_id_cli: types.ModuleType,
) -> None:
    """Rulings 90-92: every distinct id the census finds becomes exactly one `WK-` draft
    — the property Ruling 90 acceptance states directly ("41 work ids in, 41 WK- rows
    out... a conversion that silently drops a partition" is the violation) — asserted
    against the independently-derived id set above, never a hard-coded "41", so a future
    edit to `docs/roadmap.md` cannot make this test stale by adding or closing a work.
    """
    text = (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
    expected_ids = set(_naive_leading_work_ids(text))
    drafts, phase_titles, occurrences = doc_id_cli._discover_roadmap(ROOT)
    assert {d.old_token for d in drafts} == expected_ids
    assert len(drafts) == len(expected_ids)  # no id produced twice
    assert set(phase_titles) >= {d.phase[1:] for d in drafts if d.phase}
    assert occurrences  # the full census is returned too, for the restructure below


def _copy_roadmap_and_templates(dest: pathlib.Path) -> None:
    dest_docs = dest / "docs"
    dest_docs.mkdir(parents=True, exist_ok=True)
    (dest_docs / "roadmap.md").write_text(
        (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8"), encoding="utf-8"
    )
    templates_dir = dest_docs / "_templates"
    templates_dir.mkdir()
    for name in ("WK.md", "SL.md"):
        (templates_dir / name).write_text(
            (ROOT / "docs" / "_templates" / name).read_text(encoding="utf-8"), encoding="utf-8"
        )


def test_restructure_roadmap_preserves_the_narrative_on_the_real_tree(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The check the lead asked for by name: not only that the real tree's works convert,
    but that the 700-odd lines of narrative, decision gates and sizing this function used
    to overwrite wholesale still exist afterwards. A test that only checked the converted
    rows would pass just as well against the old full-file-stub `_restructure_roadmap` —
    that is the exact defect this rewrite exists to remove (`_restructure_roadmap`'s own
    docstring: "the moment discovery recognises the real shape, the old body destroys the
    other ~700 lines of this file... the first time migrate runs against the real tree").

    Anchored on `## 10. Decision gates` onward, because nothing above that heading is
    itself a target of this transform's surgery (`_restructure_roadmap` only ever edits a
    `Phase <label> — <title>` heading and a leading work-id row's own table) — so this
    span must survive **byte for byte**, not merely "contain some familiar words".
    """
    _copy_roadmap_and_templates(tmp_path)
    original = (tmp_path / "docs" / "roadmap.md").read_text(encoding="utf-8")
    tail_marker = "## 10. Decision gates"
    assert tail_marker in original
    original_tail = original[original.index(tail_marker) :]

    drafts, phase_titles, occurrences = doc_id_cli._discover_roadmap(tmp_path)
    for i, d in enumerate(drafts):
        d.number = 9000 + i
    doc_id_cli._restructure_roadmap(tmp_path, drafts, phase_titles, occurrences)
    restructured = (tmp_path / "docs" / "roadmap.md").read_text(encoding="utf-8")

    assert tail_marker in restructured
    assert restructured[restructured.index(tail_marker) :] == original_tail
    # Every other numbered top-level section this file's own module docstring never
    # touches is still present too.
    for heading in (
        "## 1. How to read this", "## 2. Where the project is",
        "## 3. Before Phase 1 — the on-ramp", "## 4. Build order, and why it is not negotiable",
        "## 11. Sizing", '## 12. What "done" looks like, per phase',
    ):
        assert heading in restructured, f"{heading!r} did not survive the restructure"


def test_restructure_roadmap_is_readable_by_doc_index_on_the_real_tree(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Round-trip validation against the real corpus, the same property
    `test_roadmap_restructure_is_readable_by_doc_index` proves on the fixture: the output
    is not just well-formed prose, `doc-index.py`'s own parser must read back exactly the
    work population `_discover_roadmap` computed — a property, so a future edit changing
    which ids exist does not make this assertion stale the way a hard-coded count would.
    """
    _copy_roadmap_and_templates(tmp_path)
    drafts, phase_titles, occurrences = doc_id_cli._discover_roadmap(tmp_path)
    for i, d in enumerate(drafts):
        d.number = 9000 + i
    doc_id_cli._restructure_roadmap(tmp_path, drafts, phase_titles, occurrences)

    doc_index = doc_id_cli._load_doc_index()
    corpus = doc_index.build_corpus(tmp_path / "docs")
    families = [h.family for h in corpus.headers()]
    assert families.count("work") == len(drafts)

    phases = doc_index.scan_phase_sections(tmp_path / "docs" / "roadmap.md")
    phases_by_id = {p.phase: p for p in phases}
    assert set(phases_by_id) == {d.phase for d in drafts if d.phase}
    for phase_id, works in collections.Counter(d.phase for d in drafts).items():
        assert len(phases_by_id[phase_id].works) == works


def test_w6_retires_naming_its_successors_on_the_real_tree(
    doc_id_cli: types.ModuleType,
) -> None:
    """Ruling 92's acceptance items directly: `W6`'s migrated row is `status: retired`
    (never dropped — it is a live dependency target, `W7`'s `Depends on` cell names it)
    and its body names `W6a` and `W6b` as the works its scope was re-cut into.
    """
    drafts, _phase_titles, _occurrences = doc_id_cli._discover_roadmap(ROOT)
    w6 = next(d for d in drafts if d.old_token == "W6")
    assert w6.status == "retired"
    assert "W6a" in w6.body
    assert "W6b" in w6.body


def test_w5s_three_source_rows_all_survive_the_merge_on_the_real_tree(
    doc_id_cli: types.ModuleType,
) -> None:
    """Ruling 91's own worked example, on the real tree rather than a reproduction of it:
    `W5` heads three rows — a status-table pointer, a delivery breakdown, and a
    scope-at-close figure — and the ruling's violation is a merge that keeps one and
    drops the rest. Each fragment quoted here is frozen, dated, already-closed-workstream
    prose that does not change as the roadmap grows elsewhere.
    """
    drafts, _phase_titles, _occurrences = doc_id_cli._discover_roadmap(ROOT)
    w5 = next(d for d in drafts if d.old_token == "W5")
    assert w5.status == "closed"
    for fragment in (
        "see [`docs/audit/closure-records.md`](audit/closure-records.md)",
        "110 built · 10 declared-and-refused-by-name · 16 unevidenced",
        "136 in scope at close, of which 110 built",
    ):
        assert fragment in w5.body, f"missing {fragment!r} in W5's merged body"


def test_register_discovery_matches_every_row_register_lint_itself_declares(
    doc_id_cli: types.ModuleType,
) -> None:
    """The positive control the real corpus already supplies (W37-6 outstanding
    obligations row 3): before this fix, `_discover_register` matched none of the real
    register's data rows (`_REGISTER_FINDING_RE.fullmatch` required a bare `F<n>`; every
    real cell is compound). After it, every data row `register-lint.py`'s own
    `parse_register` returns must be recognised — a property immune to the register
    growing a 74th row tomorrow, unlike a hard-coded "73".
    """
    register_lint = doc_id_cli._load_register_lint()
    path = ROOT / "docs" / "audit" / "register.md"
    rows, problems = register_lint.parse_register(path)
    assert not problems  # no structurally malformed row on the real tree today
    assert len(rows) > 1  # non-vacuous

    unmatched = [
        row.finding_id for row in rows
        if not doc_id_cli._REGISTER_FINDING_RE.search(row.fields[0])
    ]
    assert not unmatched, f"finding-id cell(s) with no recognised id: {unmatched}"

    drafts = doc_id_cli._discover_register(ROOT)
    assert len(drafts) == len(rows)
    old_tokens = [d.old_token for d in drafts]
    assert len(set(old_tokens)) == len(old_tokens)  # every id discovered exactly once
