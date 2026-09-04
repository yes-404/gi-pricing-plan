"""Tests for `scripts/_docid.py` and `scripts/doc-id.py` — NT-0019's shared header
parser, id grammar, and the `next` / `check` / `widen` subcommands (W37-2).

`doc-id.py migrate` is not part of this slice — it is W37-5's, built and proven against a
fixture corpus, nothing moved.

Every test that needs a governed-file tree builds one under `tmp_path`, never against this
repository's own `docs/` — the standard has not been migrated onto this repository yet
(W37-6), so there are no real ids to scan today, and a test pinned to today's tree would
start failing the moment migration lands, for a reason unrelated to the code under test.
`docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`'s W37-3 slice makes the identical
point about `doc-index.py`; the same reasoning applies here.

No `@pytest.mark.req` marker: this is correctness of the id-allocator tool itself, not
evidence for a numbered platform requirement — the same reasoning `tests/test_file_census.py`,
`tests/test_register_lint.py` and `tests/test_scope_audit.py` give for their own scripts.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import types
from collections.abc import Sequence
from datetime import date

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCID_MODULE_PATH = ROOT / "scripts" / "_docid.py"
DOC_ID_SCRIPT_PATH = ROOT / "scripts" / "doc-id.py"
FIXTURES = ROOT / "tests" / "fixtures" / "docs-ids"

# `scripts/` is not a package (no `__init__.py`) and is not on `sys.path` by default.
# `doc-id.py` does `import _docid` at its own top level, which needs `scripts/` on the
# path to resolve when the file is loaded by path (below) rather than run directly — a
# direct `python3 scripts/doc-id.py` gets this for free (Python puts a script's own
# directory on `sys.path[0]`), a `spec_from_file_location` load does not.
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load_by_path(name: str, path: pathlib.Path, *, missing_module_name: str) -> types.ModuleType:
    """Load a `scripts/` module by path rather than by name.

    Used for both `_docid.py` and `doc-id.py` — not only the hyphenated one — so mypy
    never has to resolve a static `import _docid` against a `scripts/` directory that is
    not on its own `mypy_path` (it isn't, and adding it there is a wider change than this
    test file's loading strategy should force). `types.ModuleType` permits arbitrary
    attribute access under `--strict`, so a dynamically-loaded module reads the same way
    to mypy either way.

    The explicit existence check makes the pre-implementation failure
    `ModuleNotFoundError` naming `missing_module_name`, not a `FileNotFoundError` from
    deep inside `importlib` (verified empirically against `tests/test_file_census.py`,
    which explains why: `spec_from_file_location` does not check existence at
    spec-creation time, only `exec_module`'s `get_data` does, at load time).
    """
    if not path.exists():
        raise ModuleNotFoundError(f"No module named {missing_module_name!r}: not found at {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registered in `sys.modules` *before* `exec_module`: both modules use `from
    # __future__ import annotations` (string annotations), and `doc-id.py`'s `@dataclass`
    # classes need `sys.modules[cls.__module__]` to resolve them at class-creation time —
    # without this line, building `CheckFailure` raises `AttributeError` deep inside
    # `dataclasses` ("'NoneType' object has no attribute '__dict__'"), which reads like a
    # broken dataclass rather than an unregistered dynamically-loaded module.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def docid() -> types.ModuleType:
    """`scripts/_docid.py`, loaded by path under the name `_docid` — the same name
    `doc-id.py`'s own `import _docid` resolves, so whichever of this fixture and
    `doc_id_cli` instantiates first leaves a single shared module in `sys.modules` for
    the other to reuse, rather than two separate instances of the same file (which would
    make `_docid.Header` from one fixture a different class object than `_docid.Header`
    from the other, and break `==` between them).
    """
    return _load_by_path("_docid", DOCID_MODULE_PATH, missing_module_name="_docid")


@pytest.fixture(scope="module")
def doc_id_cli() -> types.ModuleType:
    """`scripts/doc-id.py`, loaded by path — a hyphenated filename is not `import`able by
    name, the same reason `tests/test_file_census.py` loads `scripts/file-census.py` this
    way.
    """
    return _load_by_path(
        "_doc_id_under_test", DOC_ID_SCRIPT_PATH, missing_module_name="doc_id"
    )


# ---------------------------------------------------------------------------------------
# The id grammar: canonical/padded forms, the resolver regex, family lookup.
# ---------------------------------------------------------------------------------------


def test_status_words_are_the_five_word_vocabulary_in_order(docid: types.ModuleType) -> None:
    assert docid.STATUS_WORDS == ("draft", "active", "closed", "retired", "superseded")


def test_family_prefixes_names_all_fifteen_prefixes(docid: types.ModuleType) -> None:
    assert docid.FAMILY_PREFIXES == (
        "FR", "NFR", "DEP", "OQ", "WK", "SL", "WF",
        "ADR", "RFC", "PL", "LG", "RL", "RS", "CR", "FD",
    )


def test_pad_width_is_five(docid: types.ModuleType) -> None:
    assert docid.PAD_WIDTH == 5


def test_canonical_writes_the_bare_integer_never_padded(docid: types.ModuleType) -> None:
    assert docid.canonical("PL", 1240) == "PL-1240"


def test_padded_pads_to_the_default_width(docid: types.ModuleType) -> None:
    assert docid.padded("PL", 1240) == "PL-01240"


def test_padded_accepts_an_explicit_width(docid: types.ModuleType) -> None:
    assert docid.padded("PL", 1240, width=6) == "PL-001240"


def test_padded_does_not_truncate_a_number_wider_than_the_pad(docid: types.ModuleType) -> None:
    # A million-plus id must still round-trip; padding is cosmetic, never lossy.
    assert docid.padded("PL", 123456) == "PL-123456"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("See PL-1240 for detail.", [("PL", 1240)]),
        ("Padded PL-01240 also resolves.", [("PL", 1240)]),
        ("Double padded PL-001240 too.", [("PL", 1240)]),
        ("Two ids: FR-1187 and RL-1241.", [("FR", 1187), ("RL", 1241)]),
        ("No id here.", []),
        # A word boundary before the hyphen matters: this project has died on `\b` before
        # a hyphen before (memory: never-hardcode-a-fragment-of-an-identifier). `XPL-1240`
        # must not resolve as `PL-1240` with a stray `X` — `\b` before `PL` refuses it
        # because there is no boundary between `X` and `P`.
        ("XPL-1240 is not a match.", []),
        # A citation embedded in a larger token (e.g. a URL slug) must not spuriously match.
        ("something/PL-1240-slug.md", [("PL", 1240)]),
    ],
)
def test_id_re_resolves_prefix_and_integer(
    docid: types.ModuleType, text: str, expected: list[tuple[str, int]]
) -> None:
    found = [(m.group(1), int(m.group(2))) for m in docid.ID_RE.finditer(text)]
    assert found == expected


def test_family_of_maps_every_published_prefix(docid: types.ModuleType) -> None:
    # NT-0019 §1.2's own "Kind" column, lowercased — every prefix must resolve to
    # *something*, and a handful are pinned exactly so a typo'd mapping is caught.
    assert docid.family_of("PL") == "plan"
    assert docid.family_of("FR") == "requirement"
    assert docid.family_of("NFR") == "requirement"
    assert docid.family_of("DEP") == "requirement"
    assert docid.family_of("FD") == "finding"
    for prefix in docid.FAMILY_PREFIXES:
        assert docid.family_of(prefix), f"{prefix} has no family word"


def test_family_of_rejects_an_unknown_prefix(docid: types.ModuleType) -> None:
    with pytest.raises(ValueError, match="VR"):
        docid.family_of("VR")


# ---------------------------------------------------------------------------------------
# parse_header — NT-0019 §1.5's closed field set, hand-rolled over stdlib only (G4).
# ---------------------------------------------------------------------------------------

_FULL_HEADER = """\
---
id: PL-1240
family: plan
kind: leaf
title: Batch frame contract
status: active
created: 2026-09-02
owner: planner
phase: P2
work: WK-1201
slice: SL-1242
tree: 8f5d57d
plans: [PL-1240]
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [RFC-164, RL-65]
was: 2026-08-18-profile-contract.md
---

# Body starts here, and is never touched by the parser.
"""


def test_parse_header_returns_none_when_no_front_matter_block(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    path = tmp_path / "plain.md"
    path.write_text("# Just a heading\n\nNo front matter at all.\n", encoding="utf-8")
    assert docid.parse_header(path) is None


def test_parse_header_parses_every_known_scalar_and_list_field(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    path = tmp_path / "PL-01240-batch-frame-contract.md"
    path.write_text(_FULL_HEADER, encoding="utf-8")
    header = docid.parse_header(path)
    assert header == docid.Header(
        id="PL-1240",
        family="plan",
        kind="leaf",
        title="Batch frame contract",
        status="active",
        created=date(2026, 9, 2),
        owner="planner",
        phase="P2",
        work="WK-1201",
        slice_="SL-1242",
        tree="8f5d57d",
        plans=("PL-1240",),
        supersedes=(),
        superseded_by=None,
        corrected_by=(),
        corrects=None,
        relates=("RFC-164", "RL-65"),
        was="2026-08-18-profile-contract.md",
        vendored=False,
        origin=None,
        extra={},
    )


def test_parse_header_defaults_absent_fields(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    path = tmp_path / "minimal.md"
    path.write_text(
        "---\nfamily: ruling\nstatus: active\nowner: maintainer\ntitle: A minimal ruling\n---\n"
        "\nBody.\n",
        encoding="utf-8",
    )
    header = docid.parse_header(path)
    assert header is not None
    assert header.id is None
    assert header.phase is None
    assert header.work is None
    assert header.slice_ is None
    assert header.plans == ()
    assert header.relates == ()
    assert header.superseded_by is None
    assert header.vendored is False
    assert header.origin is None
    assert header.extra == {}


def test_parse_header_strips_a_trailing_inline_comment(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    path = tmp_path / "commented.md"
    path.write_text(
        "---\n"
        "family: plan\n"
        "status: active\n"
        "owner: planner\n"
        "title: Has a comment\n"
        "id: PL-1240                  # document and row families; integer form\n"
        "---\n",
        encoding="utf-8",
    )
    header = docid.parse_header(path)
    assert header is not None
    assert header.id == "PL-1240"


def test_parse_header_captures_an_unrecognised_field_in_extra(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # A skill's SKILL.md carries Claude Code's own `name:`/`description:` front matter
    # today, unrelated to NT-0019's field set — the parser must not choke on it, and must
    # not silently drop it either: a later, family-aware check (audit-docs check 30, not
    # this parser) is what decides whether an extra field is permitted for that family.
    path = tmp_path / "SKILL.md"
    path.write_text(
        "---\nname: some-skill\ndescription: does a thing\n---\n\n# some-skill\n",
        encoding="utf-8",
    )
    header = docid.parse_header(path)
    assert header is not None
    assert header.extra == {"name": "some-skill", "description": "does a thing"}
    assert header.family == ""
    assert header.title == ""


def test_parse_header_parses_vendored_true(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    path = tmp_path / "SKILL.md"
    path.write_text(
        "---\n"
        "family: reference\n"
        "status: active\n"
        "owner: maintainer\n"
        "title: A vendored skill\n"
        "vendored: true\n"
        "origin: https://github.com/example/upstream\n"
        "---\n",
        encoding="utf-8",
    )
    header = docid.parse_header(path)
    assert header is not None
    assert header.vendored is True
    assert header.origin == "https://github.com/example/upstream"


@pytest.mark.parametrize(
    "body",
    [
        # Duplicate key.
        "---\nfamily: plan\nfamily: ruling\nstatus: active\nowner: x\ntitle: t\n---\n",
        # A nested mapping — exactly what a closed, flat grammar must refuse (G4).
        "---\nfamily: plan\nnested:\n  child: 1\nstatus: active\nowner: x\ntitle: t\n---\n",
        # An unclosed list.
        "---\nfamily: plan\nrelates: [RFC-1\nstatus: active\nowner: x\ntitle: t\n---\n",
        # A malformed date.
        "---\nfamily: plan\ncreated: not-a-date\nstatus: active\nowner: x\ntitle: t\n---\n",
        # A line with no `key: value` shape at all.
        "---\nfamily: plan\njust some prose\nstatus: active\nowner: x\ntitle: t\n---\n",
        # An unclosed front-matter block (no closing delimiter).
        "---\nfamily: plan\nstatus: active\nowner: x\ntitle: t\n",
    ],
)
def test_parse_header_raises_header_error_on_malformed_input(
    docid: types.ModuleType, tmp_path: pathlib.Path, body: str
) -> None:
    path = tmp_path / "broken.md"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(docid.HeaderError):
        docid.parse_header(path)


def test_parse_header_error_names_path_and_line_number(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    path = tmp_path / "broken.md"
    path.write_text(
        "---\nfamily: plan\nfamily: ruling\nstatus: active\nowner: x\ntitle: t\n---\n",
        encoding="utf-8",
    )
    with pytest.raises(docid.HeaderError) as excinfo:
        docid.parse_header(path)
    message = str(excinfo.value)
    assert str(path) in message
    assert "3" in message  # the second `family:` line, 1-based, inside the fenced block


# ---------------------------------------------------------------------------------------
# is_vendored — Ruling 69: NT-0019 §1.5's detection-by-filesystem gloss is rejected.
# `is_vendored` now tests membership in `_VENDORED_SKILLS`, a declared constant reconciled
# against `pyproject.toml`'s ruff `exclude` list (Ruling 69 §2 part 2) — nothing in the
# function inspects a `LICENSE` file any more (Ruling 76's member 1 of 3; the other two are
# `docs/_templates/REFERENCE.md` and this file).
#
# The signature is unchanged (Ruling 69 §2 part 4), so these still build a synthetic repo
# tree under `tmp_path`; what changed is which directory *name* counts, so each test
# monkeypatches `_VENDORED_SKILLS` down to a small closed fixture set rather than relying
# on the real 28 — coupling these tests to the real list would make them fail the moment a
# skill is vendored or un-vendored, the exact coupling Ruling 69 rejected for the runtime
# predicate itself. The reconciliation against the real `pyproject.toml` is proven
# separately, below.
# ---------------------------------------------------------------------------------------


def test_is_vendored_true_for_a_directory_named_in_vendored_skills(
    docid: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(docid, "_VENDORED_SKILLS", frozenset({"some-vendored-skill"}))
    repo_root = tmp_path / "repo"
    skill_dir = repo_root / ".claude" / "skills" / "some-vendored-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")
    assert docid.is_vendored(skill_dir / "SKILL.md", repo_root) is True


def test_is_vendored_true_for_a_file_nested_below_a_vendored_skill_directory(
    docid: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(docid, "_VENDORED_SKILLS", frozenset({"some-vendored-skill"}))
    repo_root = tmp_path / "repo"
    skill_dir = repo_root / ".claude" / "skills" / "some-vendored-skill"
    nested = skill_dir / "references" / "deep.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("content\n", encoding="utf-8")
    assert docid.is_vendored(nested, repo_root) is True


def test_is_vendored_false_for_a_file_outside_claude_skills(
    docid: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(docid, "_VENDORED_SKILLS", frozenset({"some-vendored-skill"}))
    repo_root = tmp_path / "repo"
    docs = repo_root / "docs"
    docs.mkdir(parents=True)
    target = docs / "README.md"
    target.write_text("# docs\n", encoding="utf-8")
    # The rejected criterion walked upward looking for a `LICENSE` file, so it needed a
    # dedicated case ruling out the repository's own root file catching everything beneath
    # it. The membership test has no walk and no filesystem read at all — a path is only
    # ever vendored by being under `.claude/skills/<name>`, so this is the analogous
    # over-matching case: a real file elsewhere in the tree must never read as vendored no
    # matter what `_VENDORED_SKILLS` contains.
    assert docid.is_vendored(target, repo_root) is False


def test_is_vendored_false_for_a_directory_not_in_vendored_skills(
    docid: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(docid, "_VENDORED_SKILLS", frozenset({"some-vendored-skill"}))
    repo_root = tmp_path / "repo"
    skill_dir = repo_root / ".claude" / "skills" / "first-party-skill"
    skill_dir.mkdir(parents=True)
    target = skill_dir / "SKILL.md"
    target.write_text("---\nname: x\n---\n", encoding="utf-8")
    assert docid.is_vendored(target, repo_root) is False


def test_is_vendored_accepts_a_directory_path_as_well_as_a_file(
    docid: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(docid, "_VENDORED_SKILLS", frozenset({"some-vendored-skill"}))
    repo_root = tmp_path / "repo"
    skill_dir = repo_root / ".claude" / "skills" / "some-vendored-skill"
    skill_dir.mkdir(parents=True)
    assert docid.is_vendored(skill_dir, repo_root) is True


# ---------------------------------------------------------------------------------------
# vendored_skills_ruff_exclude_mismatch — Ruling 69 §2 part 2 and acceptance item 1. The
# first test is the one that matters at the real repository: it must be empty today, and
# it is the check that reds the moment `_VENDORED_SKILLS` and `pyproject.toml`'s ruff
# `exclude` list disagree, in either direction, naming which side moved. The rest are the
# broken-input proof on synthetic fixtures — fast, isolated, and independent of whatever
# the real lists happen to contain.
# ---------------------------------------------------------------------------------------


def test_vendored_skills_constant_is_reconciled_with_the_real_ruff_exclude_list(
    docid: types.ModuleType,
) -> None:
    only_in_constant, only_in_ruff = docid.vendored_skills_ruff_exclude_mismatch(ROOT)
    assert not only_in_constant, (
        f"_VENDORED_SKILLS names skills pyproject.toml's ruff exclude list does not: "
        f"{sorted(only_in_constant)}"
    )
    assert not only_in_ruff, (
        f"pyproject.toml's ruff exclude list names skills _VENDORED_SKILLS does not: "
        f"{sorted(only_in_ruff)}"
    )


def test_vendored_skills_ruff_exclude_mismatch_is_empty_when_the_two_lists_agree(
    docid: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(docid, "_VENDORED_SKILLS", frozenset({"alpha", "beta"}))
    (tmp_path / "pyproject.toml").write_text(
        '[tool.ruff]\nexclude = [".claude/skills/alpha", ".claude/skills/beta"]\n',
        encoding="utf-8",
    )
    assert docid.vendored_skills_ruff_exclude_mismatch(tmp_path) == (frozenset(), frozenset())


def test_vendored_skills_ruff_exclude_mismatch_catches_a_skill_only_ruff_excludes(
    docid: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ruling 69 acceptance item 1, one direction: a skill line added to `pyproject.toml`
    but not to `_VENDORED_SKILLS` must be named as having moved on the ruff side."""
    monkeypatch.setattr(docid, "_VENDORED_SKILLS", frozenset({"alpha", "beta"}))
    (tmp_path / "pyproject.toml").write_text(
        '[tool.ruff]\n'
        'exclude = [".claude/skills/alpha", ".claude/skills/beta", ".claude/skills/gamma"]\n',
        encoding="utf-8",
    )
    only_in_constant, only_in_ruff = docid.vendored_skills_ruff_exclude_mismatch(tmp_path)
    assert only_in_constant == frozenset()
    assert only_in_ruff == frozenset({"gamma"})


def test_vendored_skills_ruff_exclude_mismatch_catches_a_skill_only_the_constant_names(
    docid: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ruling 69 acceptance item 1, the other direction: an entry added to
    `_VENDORED_SKILLS` but not to `pyproject.toml` must be named as having moved on the
    constant side — the direction that matters most, since it is silent over-exemption
    otherwise (§5.4's "under-exempts 240 tracked files" failure mode, inverted)."""
    monkeypatch.setattr(docid, "_VENDORED_SKILLS", frozenset({"alpha", "beta", "delta"}))
    (tmp_path / "pyproject.toml").write_text(
        '[tool.ruff]\nexclude = [".claude/skills/alpha", ".claude/skills/beta"]\n',
        encoding="utf-8",
    )
    only_in_constant, only_in_ruff = docid.vendored_skills_ruff_exclude_mismatch(tmp_path)
    assert only_in_constant == frozenset({"delta"})
    assert only_in_ruff == frozenset()


# ---------------------------------------------------------------------------------------
# `doc-id.py next` — NT-0019 §1.7: "fetches origin/main, reads the maximum across every
# header, every spec bold-id, every roadmap row and INDEX.md, prints max + 1."
#
# Each of the four sources is tested alone against an otherwise-empty tree — the plan's own
# words: "A test that stubs three of the four and passes is the defect this bullet exists
# to prevent."
# ---------------------------------------------------------------------------------------


def _write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _header(id_: str, family: str = "plan") -> str:
    return f"---\nid: {id_}\nfamily: {family}\nstatus: active\nowner: maintainer\ntitle: T\n---\n"


def test_scan_header_ids_reads_the_id_field_of_a_governed_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    assert list(doc_id_cli.scan_header_ids(tmp_path)) == [("PL", 1240)]


def test_scan_header_ids_reads_a_charter_and_a_skill(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / ".claude" / "roles" / "executor.md", _header("RFC-9001", "proposal"))
    _write(
        tmp_path / ".claude" / "skills" / "some-skill" / "SKILL.md",
        _header("RFC-9002", "proposal"),
    )
    _write(
        tmp_path / ".claude" / "agents" / "gate-runner.md", _header("RFC-9003", "proposal")
    )
    found = set(doc_id_cli.scan_header_ids(tmp_path))
    assert found == {("RFC", 9001), ("RFC", 9002), ("RFC", 9003)}


def test_scan_header_ids_reads_a_readme_anywhere_in_the_tree(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "packages" / "README.md", _header("RFC-9010", "proposal"))
    assert list(doc_id_cli.scan_header_ids(tmp_path)) == [("RFC", 9010)]


def test_scan_header_ids_excludes_templates(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # `_templates/` carries example headers with placeholder ids, never real ones —
    # NT-0019 §1.4's own exemption for check 31, applied the same way here so a
    # placeholder cannot poison the allocator's max.
    _write(tmp_path / "docs" / "_templates" / "PL.md", _header("PL-99999"))
    assert list(doc_id_cli.scan_header_ids(tmp_path)) == []


def test_scan_header_ids_excludes_a_vendored_skills_content(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Ruling 69: vendored is membership in `_docid._VENDORED_SKILLS`, not a `LICENSE`
    # file — declare the fixture directory into the set rather than dropping a licence.
    monkeypatch.setattr(
        doc_id_cli._docid, "_VENDORED_SKILLS", frozenset({"some-vendored-skill"})
    )
    skill_dir = tmp_path / ".claude" / "skills" / "some-vendored-skill"
    _write(skill_dir / "SKILL.md", _header("RFC-9099", "proposal"))
    assert list(doc_id_cli.scan_header_ids(tmp_path)) == []


def test_scan_header_ids_skips_a_file_whose_front_matter_is_not_the_closed_grammar(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # Modelled on `.claude/skills/create-adaptable-composable/SKILL.md`, which carries a
    # `metadata:` mapping with an indented `author:`/`version:` underneath it — upstream
    # front matter, not an NT-0019 header. That real file is itself named in
    # `_VENDORED_SKILLS` (Ruling 69), so `is_vendored` excludes it before `parse_header`
    # ever runs on it; "some-skill" here is deliberately *not* in the set, so this fixture
    # still exercises the unparseable-but-not-vendored path `next` must survive: a file it
    # cannot parse contributes nothing, the same as a file with no front matter at all,
    # rather than crashing the whole command.
    _write(
        tmp_path / ".claude" / "skills" / "some-skill" / "SKILL.md",
        "---\nname: some-skill\nmetadata:\n  author: example\n  version: '1.0'\n---\n",
    )
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    assert list(doc_id_cli.scan_header_ids(tmp_path)) == [("PL", 1240)]


# ---------------------------------------------------------------------------------------
# scan_governed_headers — the skip must be reported, not silent. Raised in review of
# PR #567: a file with no NT-0019 header at all (every file in this repo, pre-migration)
# must stay silent, but a file whose front matter exists and fails to parse must be
# visible — a count and the paths at minimum — because the code cannot tell "malformed
# governed header" (what `check` exists to catch) from "legitimately foreign front
# matter" (the vendored-skill case). `tests/test_audit_docs_scan_roots.py` names the
# shape this guards against: a scan that silently stops covering something must not read
# the same as a scan that covered everything and found nothing.
# ---------------------------------------------------------------------------------------


def test_scan_governed_headers_reports_an_unparseable_file_in_skipped(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    bad_path = tmp_path / ".claude" / "skills" / "some-skill" / "SKILL.md"
    _write(
        bad_path,
        "---\nname: some-skill\nmetadata:\n  author: example\n  version: '1.0'\n---\n",
    )
    scan = doc_id_cli.scan_governed_headers(tmp_path)
    skipped_paths = [path for path, _reason in scan.skipped]
    assert skipped_paths == [bad_path]
    ((_path, reason),) = scan.skipped
    assert "metadata" in reason or "indented" in reason.lower()


def test_scan_governed_headers_does_not_report_a_file_with_no_header_at_all(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # Every file in this repository today, pre-migration — must not be noisy.
    _write(tmp_path / "docs" / "plans" / "plain.md", "# Just a heading\n\nNo header.\n")
    scan = doc_id_cli.scan_governed_headers(tmp_path)
    assert scan.skipped == ()


def test_scan_governed_headers_does_not_report_a_header_with_no_id_field(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(
        tmp_path / "docs" / "process" / "some-reference.md",
        "---\nfamily: reference\nstatus: active\nowner: maintainer\ntitle: T\n---\n",
    )
    scan = doc_id_cli.scan_governed_headers(tmp_path)
    assert scan.skipped == ()


def test_scan_governed_headers_does_not_report_a_template_or_vendored_exclusion(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Ruling 69: vendored is membership in `_docid._VENDORED_SKILLS`, not a `LICENSE`
    # file — declare the fixture directory into the set rather than dropping a licence.
    monkeypatch.setattr(
        doc_id_cli._docid, "_VENDORED_SKILLS", frozenset({"some-vendored-skill"})
    )
    # Excluded *before* parsing is attempted — neither is a parse failure, so neither
    # belongs in `.skipped` (which is specifically "front matter that failed to parse"),
    # and neither contributes a resolved id either — a valid header inside a vendored
    # skill's content would parse cleanly if it were ever reached, so `.ids` staying empty
    # is what proves the exclusion, not merely the absence from `.skipped`.
    _write(tmp_path / "docs" / "_templates" / "PL.md", _header("PL-99999"))
    skill_dir = tmp_path / ".claude" / "skills" / "some-vendored-skill"
    _write(skill_dir / "SKILL.md", _header("RFC-9099", "proposal"))
    scan = doc_id_cli.scan_governed_headers(tmp_path)
    assert scan.skipped == ()
    assert scan.ids == ()


def test_scan_governed_headers_ids_field_matches_scan_header_ids(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    scan = doc_id_cli.scan_governed_headers(tmp_path)
    assert [(prefix, number) for prefix, number, _path in scan.ids] == [("PL", 1240)]
    assert list(doc_id_cli.scan_header_ids(tmp_path)) == [("PL", 1240)]


def test_scan_governed_headers_candidates_scanned_counts_every_candidate(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    _write(tmp_path / "docs" / "plans" / "plain.md", "# No header\n")
    bad_path = tmp_path / ".claude" / "roles" / "broken.md"
    _write(bad_path, "---\nfamily: plan\nnested:\n  x: 1\n---\n")
    scan = doc_id_cli.scan_governed_headers(tmp_path)
    # One resolved id, one silent no-header file, one reported skip: three candidates.
    assert scan.candidates_scanned == 3
    assert len(scan.ids) == 1
    assert len(scan.skipped) == 1


def test_scan_header_ids_ignores_a_skills_non_skill_md_files(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # Only `.claude/skills/*/SKILL.md` carries a header (NT-0019 §1.5) — a reference file
    # underneath a skill is not itself a governed document.
    _write(
        tmp_path / ".claude" / "skills" / "some-skill" / "references" / "deep.md",
        _header("RFC-9020", "proposal"),
    )
    assert list(doc_id_cli.scan_header_ids(tmp_path)) == []


def test_scan_spec_bold_ids_reads_bold_requirement_ids(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(
        tmp_path / "docs" / "specs" / "02-modelling.md",
        "## 3. Functional requirements\n\n**FR-1187** The model must ...\n\n"
        "**NFR-1188** Latency must ...\n",
    )
    found = set(doc_id_cli.scan_spec_bold_ids(tmp_path))
    assert found == {("FR", 1187), ("NFR", 1188)}


def test_scan_spec_bold_ids_empty_when_no_specs_directory(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    assert list(doc_id_cli.scan_spec_bold_ids(tmp_path)) == []


def test_scan_roadmap_row_ids_reads_work_and_slice_row_headings(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(
        tmp_path / "docs" / "roadmap.md",
        "## P2 — Rating engine live\n\n"
        "### WK-1201 — Batch frame contract\nstatus: active\n\n"
        "#### SL-1242 — doc-id.py\nstatus: active\n",
    )
    found = set(doc_id_cli.scan_roadmap_row_ids(tmp_path))
    assert found == {("WK", 1201), ("SL", 1242)}


def test_scan_roadmap_row_ids_empty_when_no_roadmap(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    assert list(doc_id_cli.scan_roadmap_row_ids(tmp_path)) == []


def test_scan_index_ids_reads_every_id_index_lists(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(
        tmp_path / "docs" / "INDEX.md",
        "| id | family | title |\n|---|---|---|\n| PL-1240 | plan | Example |\n"
        "| RL-1241 | ruling | Example |\n",
    )
    found = set(doc_id_cli.scan_index_ids(tmp_path))
    assert found == {("PL", 1240), ("RL", 1241)}


def test_scan_index_ids_empty_when_no_index(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    assert list(doc_id_cli.scan_index_ids(tmp_path)) == []


def test_compute_next_is_one_when_every_source_is_empty(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    assert doc_id_cli.compute_next(tmp_path) == 1


@pytest.mark.parametrize(
    "populate",
    [
        # Header source alone drives the max.
        lambda root: _write(root / "docs" / "plans" / "PL-01240-x.md", _header("PL-1240")),
        # Spec bold-id source alone.
        lambda root: _write(
            root / "docs" / "specs" / "00-overview.md", "**FR-1240** ...\n"
        ),
        # Roadmap row source alone.
        lambda root: _write(
            root / "docs" / "roadmap.md", "### WK-1240 — Example\nstatus: active\n"
        ),
        # INDEX.md source alone.
        lambda root: _write(root / "docs" / "INDEX.md", "| PL-1240 | plan |\n"),
    ],
)
def test_compute_next_reads_each_source_independently(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path, populate: object
) -> None:
    # Each source alone, at 1240, must drive `next` to 1241 — a test that stubbed the
    # other three and still passed would not prove this source is actually read.
    populate(tmp_path)  # type: ignore[operator]
    assert doc_id_cli.compute_next(tmp_path) == 1241


def test_compute_next_takes_the_max_across_all_four_sources(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01100-x.md", _header("PL-1100"))
    _write(tmp_path / "docs" / "specs" / "00-overview.md", "**FR-1200** ...\n")
    _write(tmp_path / "docs" / "roadmap.md", "### WK-1300 — Example\nstatus: active\n")
    _write(tmp_path / "docs" / "INDEX.md", "| RL-1400 | ruling |\n")
    assert doc_id_cli.compute_next(tmp_path) == 1401


def test_compute_next_against_the_shared_fixture_corpus(
    doc_id_cli: types.ModuleType,
) -> None:
    # `tests/fixtures/docs-ids/next-basic/` — the shared fixture root NT-0019 §5.7 names
    # and W37-4 also uses, populated here with the same four-source scenario as the
    # tmp_path test above, so the directory this slice is asked to create carries real,
    # git-tracked content rather than staying empty (git does not track empty
    # directories). PL-1100 (header) and FR-1200 (spec bold) and WK-1300/SL-1301
    # (roadmap) are all below the INDEX.md maximum, RL-1400 — proving the max really is
    # taken across all four, not just the largest file's own source.
    assert doc_id_cli.compute_next(FIXTURES / "next-basic") == 1401


# ---------------------------------------------------------------------------------------
# Git-ref reading: `next` must read a ref's committed content, never the working tree and
# never an uncommitted local file (NT-0019 §1.7; DP-8's contiguity argument depends on
# this — see `docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`'s DP-8 disposition).
# ---------------------------------------------------------------------------------------


def _run_git(args: Sequence[str], *, cwd: pathlib.Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def tiny_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A minimal git repository, at `tmp_path / "repo"`, with one committed plan carrying
    id `PL-1000` on its `main` branch — small enough that every test using it starts from
    a known, stated state.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(["init", "--initial-branch=main", "--quiet"], cwd=repo)
    _run_git(["config", "user.email", "test@example.com"], cwd=repo)
    _run_git(["config", "user.name", "Test"], cwd=repo)
    _write(repo / "docs" / "plans" / "PL-01000-seed.md", _header("PL-1000"))
    _run_git(["add", "-A"], cwd=repo)
    _run_git(["commit", "-m", "seed", "--quiet"], cwd=repo)
    return repo


def test_ref_exists_true_for_a_real_branch(
    doc_id_cli: types.ModuleType, tiny_repo: pathlib.Path
) -> None:
    assert doc_id_cli.ref_exists("main", tiny_repo) is True


def test_ref_exists_false_for_an_unknown_ref(
    doc_id_cli: types.ModuleType, tiny_repo: pathlib.Path
) -> None:
    assert doc_id_cli.ref_exists("origin/main", tiny_repo) is False
    assert doc_id_cli.ref_exists("not-a-real-ref", tiny_repo) is False


def test_materialize_ref_extracts_the_committed_tree(
    doc_id_cli: types.ModuleType, tiny_repo: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    dest = tmp_path / "materialized"
    dest.mkdir()
    doc_id_cli.materialize_ref("main", dest, repo_root=tiny_repo)
    assert (dest / "docs" / "plans" / "PL-01000-seed.md").is_file()


def test_compute_next_at_ref_ignores_an_uncommitted_local_file(
    doc_id_cli: types.ModuleType, tiny_repo: pathlib.Path
) -> None:
    # An uncommitted draft claiming a much higher number must not be counted — an
    # unmerged number is reissued, never treated as taken (DP-8's "no hole" argument).
    _write(tiny_repo / "docs" / "plans" / "PL-09999-draft.md", _header("PL-9999"))
    assert doc_id_cli.compute_next_at_ref("main", repo_root=tiny_repo).number == 1001


def test_compute_next_at_ref_ignores_a_committed_but_unmerged_branch(
    doc_id_cli: types.ModuleType, tiny_repo: pathlib.Path
) -> None:
    # Committed on a side branch, never merged to `main` — still must not be counted:
    # `next` reads the named ref only, not "anything git knows about".
    _run_git(["checkout", "-b", "side", "--quiet"], cwd=tiny_repo)
    _write(tiny_repo / "docs" / "plans" / "PL-09999-side.md", _header("PL-9999"))
    _run_git(["add", "-A"], cwd=tiny_repo)
    _run_git(["commit", "-m", "side draft", "--quiet"], cwd=tiny_repo)
    assert doc_id_cli.compute_next_at_ref("main", repo_root=tiny_repo).number == 1001


def test_compute_next_at_ref_reports_a_skipped_file(
    doc_id_cli: types.ModuleType, tiny_repo: pathlib.Path
) -> None:
    bad_path = tiny_repo / ".claude" / "roles" / "broken.md"
    _write(bad_path, "---\nfamily: plan\nnested:\n  x: 1\n---\n")
    _run_git(["add", "-A"], cwd=tiny_repo)
    _run_git(["commit", "-m", "add a broken header", "--quiet"], cwd=tiny_repo)
    result = doc_id_cli.compute_next_at_ref("main", repo_root=tiny_repo)
    assert result.number == 1001
    skipped_names = [path.name for path, _reason in result.skipped]
    assert skipped_names == ["broken.md"]


def test_compute_next_at_ref_raises_a_clear_error_for_an_unresolvable_ref(
    doc_id_cli: types.ModuleType, tiny_repo: pathlib.Path
) -> None:
    with pytest.raises(doc_id_cli.GitArchiveError, match="origin/main"):
        doc_id_cli.compute_next_at_ref("origin/main", repo_root=tiny_repo)


# ---------------------------------------------------------------------------------------
# `doc-id.py check` — NT-0019 §1.7: "fails the gate on any duplicate or header/filename
# mismatch"; contiguity is "computed over INDEX.md, never over the working tree" (DP-8).
# ---------------------------------------------------------------------------------------


def test_check_passes_a_clean_tree(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    _write(tmp_path / "docs" / "INDEX.md", "| PL-1240 | plan |\n")
    assert doc_id_cli.check(tmp_path) == []


def test_check_finds_a_duplicate_number_across_two_files(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-first.md", _header("PL-1240"))
    _write(tmp_path / "docs" / "rulings" / "RL-01240-second.md", _header("RL-1240", "ruling"))
    failures = doc_id_cli.check(tmp_path)
    assert any(f.kind == "duplicate" for f in failures)


def test_check_finds_no_duplicate_when_every_number_is_unique(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-first.md", _header("PL-1240"))
    _write(tmp_path / "docs" / "rulings" / "RL-01241-second.md", _header("RL-1241", "ruling"))
    assert [f for f in doc_id_cli.check(tmp_path) if f.kind == "duplicate"] == []


def test_check_finds_a_header_filename_mismatch(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # Filename pads 1241; header claims 1240 — NT-0019 §1.1 rule 3's resolver treats them
    # as different ids by design, so a mismatch here is a real, catchable authoring error.
    _write(tmp_path / "docs" / "plans" / "PL-01241-example.md", _header("PL-1240"))
    failures = doc_id_cli.check(tmp_path)
    assert any(f.kind == "mismatch" for f in failures)


def test_check_finds_no_mismatch_when_header_and_filename_agree(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    assert [f for f in doc_id_cli.check(tmp_path) if f.kind == "mismatch"] == []


def test_check_ignores_a_file_whose_name_does_not_lead_with_a_padded_id(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # A charter or README carries a header but is never renamed to lead with a padded id —
    # nothing to compare, and that must not read as a mismatch.
    _write(tmp_path / ".claude" / "roles" / "executor.md", _header("RFC-9001", "proposal"))
    assert doc_id_cli.check(tmp_path) == []


def test_check_finds_a_gap_in_index_contiguity(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "INDEX.md", "| PL-1240 | plan |\n| PL-1242 | plan |\n")
    failures = doc_id_cli.check(tmp_path)
    assert any(f.kind == "noncontiguous" for f in failures)


def test_check_finds_no_gap_when_index_is_contiguous(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(
        tmp_path / "docs" / "INDEX.md",
        "| PL-1240 | plan |\n| RL-1241 | ruling |\n| RL-1242 | ruling |\n",
    )
    assert [f for f in doc_id_cli.check(tmp_path) if f.kind == "noncontiguous"] == []


def test_check_contiguity_does_not_start_at_one(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # D6: "five [width] because the sequence starts near 1 000" — contiguity must not
    # assume the run starts at 1; only internal gaps are a defect.
    _write(tmp_path / "docs" / "INDEX.md", "| PL-1000 | plan |\n| PL-1001 | plan |\n")
    assert [f for f in doc_id_cli.check(tmp_path) if f.kind == "noncontiguous"] == []


def test_check_ignores_a_local_file_numbered_above_the_merged_maximum(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # The plan's own words (DP-8): "A fixture carrying a local file numbered above the
    # merged maximum must pass" — contiguity reads INDEX.md only, so a fresh local draft
    # not yet reflected there must not manufacture a phantom gap.
    _write(tmp_path / "docs" / "INDEX.md", "| PL-1240 | plan |\n| PL-1241 | plan |\n")
    _write(tmp_path / "docs" / "plans" / "PL-09999-draft.md", _header("PL-9999"))
    failures = doc_id_cli.check(tmp_path)
    assert [f for f in failures if f.kind == "noncontiguous"] == []
    # Its own header/filename agreement is still checked — contiguity's exemption is not
    # a blanket exemption for the whole file.
    assert [f for f in failures if f.kind == "mismatch"] == []


def test_check_skips_a_file_whose_front_matter_is_not_the_closed_grammar(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # Same real-world case as `scan_header_ids`'s equivalent test: `check` must not crash
    # on a file whose front matter is not NT-0019's grammar at all.
    _write(
        tmp_path / ".claude" / "skills" / "some-skill" / "SKILL.md",
        "---\nname: some-skill\nmetadata:\n  author: example\n  version: '1.0'\n---\n",
    )
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    assert doc_id_cli.check(tmp_path) == []


def test_check_passes_when_index_is_absent(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # Pre-migration, `docs/INDEX.md` does not exist yet (W37-3/W37-6). Nothing to be
    # non-contiguous about is not a failure.
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    assert doc_id_cli.check(tmp_path) == []


# ---------------------------------------------------------------------------------------
# `check --classify` — Acceptance Standard item 3: "prints a per-family count table whose
# total equals `git ls-files docs/ | wc -l` and whose 'none' row is 0." The corpus is
# `git ls-files`, never a working-tree walk — the same reasoning `file-census.py` gives
# (`.venv/`, `graphify-out/`, anything untracked must not be counted).
#
# The "none" row reading 0 is a post-migration invariant (W37-6/W37-11), not provable
# today — `docs/` has not been reorganised into family directories yet. These tests pin
# the *mechanism* against a synthetic corpus, not today's real tree.
# ---------------------------------------------------------------------------------------


def _classify_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(["init", "--initial-branch=main", "--quiet"], cwd=repo)
    _run_git(["config", "user.email", "test@example.com"], cwd=repo)
    _run_git(["config", "user.name", "Test"], cwd=repo)
    return repo


def _commit_all(repo: pathlib.Path) -> None:
    _run_git(["add", "-A"], cwd=repo)
    _run_git(["commit", "-m", "seed", "--quiet"], cwd=repo)


def test_git_ls_files_lists_only_tracked_files_under_a_pathspec(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    repo = _classify_repo(tmp_path)
    _write(repo / "docs" / "plans" / "PL-01240-x.md", "x\n")
    _write(repo / "docs" / "untracked.md", "x\n")
    _run_git(["add", "docs/plans"], cwd=repo)
    _run_git(["commit", "-m", "seed", "--quiet"], cwd=repo)
    assert doc_id_cli.git_ls_files(repo, "docs") == ["docs/plans/PL-01240-x.md"]


def test_git_ls_files_raises_naming_the_cause_on_a_non_git_directory(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    with pytest.raises(doc_id_cli.GitLsFilesError):
        doc_id_cli.git_ls_files(tmp_path, "docs")


def test_classify_counts_every_document_family_directory(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    repo = _classify_repo(tmp_path)
    _write(repo / "docs" / "plans" / "PL-01240-x.md", "x\n")
    _write(repo / "docs" / "rulings" / "RL-01241-x.md", "x\n")
    _commit_all(repo)
    assert doc_id_cli.classify_docs_files(repo) == {"plan": 1, "ruling": 1}


def test_classify_reports_none_for_an_unclassified_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # Not `docs/roadmap.md`: W37-5 widened `classify_docs_files` to recognise it (and
    # `INDEX.md`, `REDIRECTS.csv`, `open-questions.md`, alongside `README.md`) as
    # `"reference"` — a top-level `docs/*.md` file with no recognised name at all is
    # still the genuinely unclassified case this test means to prove.
    repo = _classify_repo(tmp_path)
    _write(repo / "docs" / "some-unrecognised-file.md", "x\n")
    _commit_all(repo)
    assert doc_id_cli.classify_docs_files(repo) == {"none": 1}


def test_classify_readme_is_reference_not_none(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    repo = _classify_repo(tmp_path)
    _write(repo / "docs" / "README.md", "x\n")
    _commit_all(repo)
    assert doc_id_cli.classify_docs_files(repo) == {"reference": 1}


def test_classify_the_five_other_living_top_level_files_are_reference_not_none(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """W37-5's widening: `INDEX.md`, `REDIRECTS.csv`, `roadmap.md` and
    `open-questions.md` sit at `docs/`'s top level alongside `README.md` and are exactly
    as living and un-numbered — none of the four has a family directory of its own, and
    a fresh migrated tree without this widening reported all four as spurious `"none"`."""
    repo = _classify_repo(tmp_path)
    for name in ("INDEX.md", "REDIRECTS.csv", "roadmap.md", "open-questions.md"):
        _write(repo / "docs" / name, "x\n")
    _commit_all(repo)
    assert doc_id_cli.classify_docs_files(repo) == {"reference": 4}


def test_classify_templates_get_their_own_bucket(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    repo = _classify_repo(tmp_path)
    _write(repo / "docs" / "_templates" / "PL.md", "x\n")
    _commit_all(repo)
    assert doc_id_cli.classify_docs_files(repo) == {"template": 1}


def test_classify_total_equals_git_ls_files_count(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    repo = _classify_repo(tmp_path)
    _write(repo / "docs" / "plans" / "PL-01240-x.md", "x\n")
    _write(repo / "docs" / "roadmap.md", "x\n")
    _write(repo / "docs" / "specs" / "00-overview.md", "x\n")
    _commit_all(repo)
    counts = doc_id_cli.classify_docs_files(repo)
    assert sum(counts.values()) == len(doc_id_cli.git_ls_files(repo, "docs"))


# ---------------------------------------------------------------------------------------
# `doc-id.py widen --to WIDTH` — NT-0019 §1.8: "renames every padded file, rewrites every
# padded link target, appends to REDIRECTS.csv, updates the width in document-ids.md,
# regenerates INDEX.md; touches no citation, number, header or body line."
#
# Every test builds its own small tree under `tmp_path` — widen is fundamentally a
# post-migration operation (REDIRECTS.csv, a populated INDEX.md) and this repository has
# not been migrated yet, so there is no real corpus to widen today.
# ---------------------------------------------------------------------------------------


def test_widen_renames_a_padded_file(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", "# Example\n")
    doc_id_cli.widen(tmp_path, to=6)
    assert not (tmp_path / "docs" / "plans" / "PL-01240-example.md").exists()
    assert (tmp_path / "docs" / "plans" / "PL-001240-example.md").is_file()


def test_widen_rewrites_a_link_target_but_not_its_citation_text(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", "# Example\n")
    citing = tmp_path / "docs" / "rulings" / "RL-01241-example.md"
    _write(citing, "See [PL-1240](../plans/PL-01240-example.md) for detail.\n")
    doc_id_cli.widen(tmp_path, to=6)
    text = (tmp_path / "docs" / "rulings" / "RL-001241-example.md").read_text(
        encoding="utf-8"
    )
    assert "[PL-1240](../plans/PL-001240-example.md)" in text
    # The citation (link text) is unpadded and must never change — NT-0019 §1.1 rule 2.
    assert "[PL-001240]" not in text


def test_widen_does_not_touch_an_unpadded_citation_in_prose(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", "# Example\n")
    prose_file = tmp_path / "docs" / "rulings" / "RL-01241-example.md"
    _write(prose_file, "See PL-1240 for detail — no link here.\n")
    doc_id_cli.widen(tmp_path, to=6)
    text = (tmp_path / "docs" / "rulings" / "RL-001241-example.md").read_text(
        encoding="utf-8"
    )
    assert text == "See PL-1240 for detail — no link here.\n"


def test_widen_touches_no_citation_number_header_or_body_line(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # The plan's own prescribed proof: diff the tree with filenames and link targets
    # normalised away, and the result must be empty.
    target_before = "docs/plans/PL-01240-example.md"
    citing_before = "docs/rulings/RL-01241-example.md"
    _write(
        tmp_path / target_before,
        _header("PL-1240") + "\nBody text citing RL-1241 and PL-1240 in prose.\n",
    )
    _write(
        tmp_path / citing_before,
        _header("RL-1241", "ruling")
        + "\nSee [PL-1240](../plans/PL-01240-example.md) for detail.\n"
        "Prose also cites RL-1241 and PL-1240 without a link.\n",
    )
    before = {
        rel: (tmp_path / rel).read_text(encoding="utf-8")
        for rel in (target_before, citing_before)
    }

    doc_id_cli.widen(tmp_path, to=6)

    target_after = "docs/plans/PL-001240-example.md"
    citing_after = "docs/rulings/RL-001241-example.md"
    after = {
        rel: (tmp_path / rel).read_text(encoding="utf-8")
        for rel in (target_after, citing_after)
    }

    def _normalise(text: str) -> str:
        return text.replace("PL-01240", "PL-ID").replace("PL-001240", "PL-ID").replace(
            "RL-01241", "RL-ID"
        ).replace("RL-001241", "RL-ID")

    assert _normalise(before[target_before]) == _normalise(after[target_after])
    assert _normalise(before[citing_before]) == _normalise(after[citing_after])


def test_widen_appends_to_redirects_csv_creating_it_if_absent(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", "# Example\n")
    doc_id_cli.widen(tmp_path, to=6)
    redirects = (tmp_path / "docs" / "REDIRECTS.csv").read_text(encoding="utf-8")
    assert "docs/plans/PL-01240-example.md" in redirects
    assert "docs/plans/PL-001240-example.md" in redirects


def test_widen_appends_to_an_existing_redirects_csv_without_discarding_its_rows(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    existing = "old_id,new_id,old_path,new_path\nNT-0001,RFC-1,old.md,rfcs/RFC-00001-x.md\n"
    _write(tmp_path / "docs" / "REDIRECTS.csv", existing)
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", "# Example\n")
    doc_id_cli.widen(tmp_path, to=6)
    redirects = (tmp_path / "docs" / "REDIRECTS.csv").read_text(encoding="utf-8")
    assert "NT-0001,RFC-1,old.md,rfcs/RFC-00001-x.md" in redirects
    assert "docs/plans/PL-001240-example.md" in redirects


def test_widen_updates_the_document_ids_width_sentence(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(
        tmp_path / "docs" / "process" / "document-ids.md",
        "Filenames pad the integer to the standard's width, currently five: "
        "`PL-01240-<slug>.md`.\n",
    )
    result = doc_id_cli.widen(tmp_path, to=6)
    text = (tmp_path / "docs" / "process" / "document-ids.md").read_text(encoding="utf-8")
    assert "currently six" in text
    assert "currently five" not in text
    assert result.document_ids_updated is True


def test_widen_warns_but_does_not_fail_when_document_ids_md_is_absent(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", "# Example\n")
    result = doc_id_cli.widen(tmp_path, to=6)
    assert result.document_ids_updated is False
    assert any("document-ids.md" in w for w in result.warnings)


def test_widen_updates_the_pad_width_constant_in_docid_py(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    fake_docid = (
        "from __future__ import annotations\n\nfrom typing import Final\n\n"
        "PAD_WIDTH: Final = 5\n"
    )
    _write(tmp_path / "scripts" / "_docid.py", fake_docid)
    result = doc_id_cli.widen(tmp_path, to=6)
    updated = (tmp_path / "scripts" / "_docid.py").read_text(encoding="utf-8")
    assert "PAD_WIDTH: Final = 6" in updated
    assert result.pad_width_constant_updated is True


def test_widen_warns_when_docid_py_pad_width_constant_is_not_found(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    result = doc_id_cli.widen(tmp_path, to=6)
    assert result.pad_width_constant_updated is False
    assert any("PAD_WIDTH" in w for w in result.warnings)


def test_widen_regenerates_index_by_invoking_doc_index_py_when_present(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # A stand-in for W37-3's script — not real doc-index.py, just proof that widen shells
    # out to whatever lives at scripts/doc-index.py after making its own changes.
    _write(
        tmp_path / "scripts" / "doc-index.py",
        "from pathlib import Path\n"
        "Path('docs/INDEX.md').write_text('regenerated by the stand-in\\n')\n",
    )
    (tmp_path / "docs").mkdir(exist_ok=True)
    result = doc_id_cli.widen(tmp_path, to=6)
    assert result.index_regenerated is True
    assert (tmp_path / "docs" / "INDEX.md").read_text(encoding="utf-8") == (
        "regenerated by the stand-in\n"
    )


def test_widen_warns_when_doc_index_py_is_absent(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    result = doc_id_cli.widen(tmp_path, to=6)
    assert result.index_regenerated is False
    assert any("doc-index.py" in w for w in result.warnings)


# ---------------------------------------------------------------------------------------
# CLI wiring: `main()` dispatches `next` / `check` / `widen`, each accepting an explicit
# `--repo-root` so a test never touches this repository's own tree.
# ---------------------------------------------------------------------------------------


def test_main_next_prints_the_computed_number_and_exits_zero(
    doc_id_cli: types.ModuleType,
    tiny_repo: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_id_cli.main(["next", "--ref", "main", "--repo-root", str(tiny_repo)])
    assert exit_code == 0
    assert capsys.readouterr().out == "1001\n"


def test_main_next_reports_zero_skipped_on_stderr_when_clean(
    doc_id_cli: types.ModuleType,
    tiny_repo: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The claim "nothing was skipped" must be printed, not merely true by the absence of
    # a line — the same falsifiability argument `scripts/audit-docs.py`'s own residue
    # notes make (check 29): silence must not be the only evidence of a clean run.
    exit_code = doc_id_cli.main(["next", "--ref", "main", "--repo-root", str(tiny_repo)])
    assert exit_code == 0
    err = capsys.readouterr().err
    assert "0 skipped" in err or "0 file(s) skipped" in err


def test_main_next_reports_a_skipped_file_by_count_and_path_on_stderr(
    doc_id_cli: types.ModuleType,
    tiny_repo: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bad_path = tiny_repo / ".claude" / "roles" / "broken.md"
    _write(bad_path, "---\nfamily: plan\nnested:\n  x: 1\n---\n")
    _run_git(["add", "-A"], cwd=tiny_repo)
    _run_git(["commit", "-m", "add a broken header", "--quiet"], cwd=tiny_repo)
    exit_code = doc_id_cli.main(["next", "--ref", "main", "--repo-root", str(tiny_repo)])
    # Reporting a skip is not a failure pre-migration — the gate must stay green.
    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == "1001\n"  # stdout stays exactly the number — machine-consumable
    assert "1" in captured.err
    assert "skipped" in captured.err
    assert "broken.md" in captured.err


def test_main_next_exits_nonzero_naming_the_cause_for_an_unresolvable_ref(
    doc_id_cli: types.ModuleType,
    tiny_repo: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = doc_id_cli.main(
        ["next", "--ref", "origin/main", "--repo-root", str(tiny_repo)]
    )
    assert exit_code != 0
    assert "origin/main" in capsys.readouterr().err


def test_main_check_exits_zero_on_a_clean_tree(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    assert doc_id_cli.main(["check", "--repo-root", str(tmp_path)]) == 0


def test_main_check_exits_nonzero_and_reports_each_failure_on_a_broken_tree(
    doc_id_cli: types.ModuleType,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01241-example.md", _header("PL-1240"))
    exit_code = doc_id_cli.main(["check", "--repo-root", str(tmp_path)])
    assert exit_code == 1
    assert "mismatch" in capsys.readouterr().err


def test_main_check_reports_zero_skipped_on_stderr_when_clean(
    doc_id_cli: types.ModuleType,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    exit_code = doc_id_cli.main(["check", "--repo-root", str(tmp_path)])
    assert exit_code == 0
    err = capsys.readouterr().err
    assert "0 skipped" in err or "0 file(s) skipped" in err


def test_main_check_reports_a_skipped_file_by_count_and_path_without_failing_the_gate(
    doc_id_cli: types.ModuleType,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # A file `check` cannot parse is reported, not silent — but does not fail the gate
    # pre-migration: whether a *governed* file's header is malformed is check 30's
    # question (W37-4), which can tell this case apart from legitimately foreign
    # (vendored) front matter and this generic scan cannot.
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", _header("PL-1240"))
    bad_path = tmp_path / ".claude" / "roles" / "broken.md"
    _write(bad_path, "---\nfamily: plan\nnested:\n  x: 1\n---\n")
    exit_code = doc_id_cli.main(["check", "--repo-root", str(tmp_path)])
    assert exit_code == 0
    err = capsys.readouterr().err
    assert "1" in err
    assert "skipped" in err
    assert "broken.md" in err


def test_main_check_classify_prints_a_table_and_exits_zero(
    doc_id_cli: types.ModuleType,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _classify_repo(tmp_path)
    _write(repo / "docs" / "plans" / "PL-01240-x.md", "x\n")
    _commit_all(repo)
    exit_code = doc_id_cli.main(["check", "--classify", "--repo-root", str(repo)])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "plan" in out
    assert "1" in out


def test_main_widen_performs_the_rename_and_exits_zero(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    _write(tmp_path / "docs" / "plans" / "PL-01240-example.md", "# Example\n")
    exit_code = doc_id_cli.main(["widen", "--to", "6", "--repo-root", str(tmp_path)])
    assert exit_code == 0
    assert (tmp_path / "docs" / "plans" / "PL-001240-example.md").is_file()


def test_main_widen_requires_the_to_flag(doc_id_cli: types.ModuleType) -> None:
    with pytest.raises(SystemExit):
        doc_id_cli.main(["widen"])


def test_main_requires_a_subcommand(doc_id_cli: types.ModuleType) -> None:
    with pytest.raises(SystemExit):
        doc_id_cli.main([])


# ---------------------------------------------------------------------------------------
# `_docid.sweep_exclusion_reason` — the declared exclusion list W37-6 adds beside
# `LEGACY_FORM_PATTERNS`: three lockfiles (Ruling 67 Part 2), the two fixture-corpus roots
# (extending the 2026-09-02 RFC §3 declared-exception mechanism —
# `docs/plans/2026-09-02-w37-rfc-readme-row-and-stamp-set.md` §3 — from the id-stamp
# census to the migration sweep and the (d)/(e)/(g) verification corpus), and the
# instrument's own bytecode-cache exhaust. One shared predicate `doc-id.py`'s
# `_iter_tree_files` and `_docverify.py`'s `tracked_files` both read, so the two consumers
# can never disagree about what is excluded (Ruling 67 §2's "one shared constant").
# ---------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel", ["uv.lock", "pnpm-lock.yaml", "frontend/pnpm-lock.yaml"]
)
def test_sweep_exclusion_reason_excludes_every_declared_lockfile(
    docid: types.ModuleType, rel: str
) -> None:
    assert docid.sweep_exclusion_reason(rel) is not None


def test_sweep_exclusion_reason_leaves_a_lock_shaped_name_alone(
    docid: types.ModuleType,
) -> None:
    """The negative control the positive proof above needs: a name that merely *contains*
    "lock", or a lockfile at a path other than the three declared ones, must not be swept
    up by an accidental substring match — only the exact declared paths are excluded.
    """
    assert docid.sweep_exclusion_reason("docs/plans/2026-09-01-deadlock-notes.md") is None
    assert docid.sweep_exclusion_reason("backend/uv.lock") is None  # not the repo root's


@pytest.mark.parametrize(
    "rel",
    [
        "tests/fixtures/docs-ids/w37-4-checks/check35-readme-allowlist/README.md",
        "tests/fixtures/docs-migration/docs/notes/0001-example-note.md",
        "tests/fixtures/docs-migration",
    ],
)
def test_sweep_exclusion_reason_excludes_both_declared_fixture_corpus_roots(
    docid: types.ModuleType, rel: str
) -> None:
    assert docid.sweep_exclusion_reason(rel) is not None


def test_sweep_exclusion_reason_leaves_a_similarly_named_directory_alone(
    docid: types.ModuleType,
) -> None:
    """Proves a root match, not a bare substring test: a path that merely *starts with*
    the string "tests/fixtures" without being under either declared root is not excluded.
    """
    assert docid.sweep_exclusion_reason("tests/fixtures/other-tool/README.md") is None


@pytest.mark.parametrize(
    "rel",
    [
        "scripts/__pycache__/doc-index.cpython-312.pyc",
        "scripts/__pycache__/_docid.cpython-312.pyc",
        "packages/model-schema/tests/__pycache__/conftest.cpython-312.pyc",
        "scripts/foo.pyc",
    ],
)
def test_sweep_exclusion_reason_excludes_pycache_and_pyc_artifacts(
    docid: types.ModuleType, rel: str
) -> None:
    assert docid.sweep_exclusion_reason(rel) is not None


def test_sweep_exclusion_reason_leaves_a_real_python_source_file_alone(
    docid: types.ModuleType,
) -> None:
    assert docid.sweep_exclusion_reason("scripts/doc-id.py") is None
    assert docid.sweep_exclusion_reason("backend/src/app/main.py") is None


def test_sweep_exclusion_reason_gives_every_class_its_own_named_reason(
    docid: types.ModuleType,
) -> None:
    """"a DECLARED entry (a list with a reason per entry)" — the dispatch's own wording.
    Each class's reason string is non-empty and distinguishable from the other two, so a
    reader can tell *why* a given path was excluded, not merely that it was.
    """
    lockfile_reason = docid.sweep_exclusion_reason("uv.lock")
    fixture_reason = docid.sweep_exclusion_reason(
        "tests/fixtures/docs-migration/docs/README.md"
    )
    pycache_reason = docid.sweep_exclusion_reason("scripts/__pycache__/x.pyc")
    assert lockfile_reason
    assert fixture_reason
    assert pycache_reason
    assert len({lockfile_reason, fixture_reason, pycache_reason}) == 3


def test_load_module_does_not_write_bytecode_and_restores_global_state(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """`_load_module` is what `migrate()` uses to load a snapshot's own `scripts/*.py` by
    path (`_load_doc_index`/`_load_audit_docs`/`_load_register_lint`) — exec'ing a module
    this way writes a `.pyc` into its `__pycache__/` by default, which a non-git-aware
    whole-tree walk over the snapshot (`_iter_tree_files`) would then read back as new
    migration output. Proven directly at this helper, not only through the full `migrate()`
    proof in `tests/test_doc_id_migrate.py`. `sys.dont_write_bytecode` must also come back
    exactly as it was: the setting is process-global, so a concurrent import elsewhere must
    not have its own caching behaviour silently changed by this one call.
    """
    before = sys.dont_write_bytecode
    target = tmp_path / "probe_module.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")

    loaded = doc_id_cli._load_module("probe_module_under_test", target)

    assert loaded.VALUE == 1  # the load itself still succeeded
    assert not (tmp_path / "__pycache__").exists()
    assert sys.dont_write_bytecode == before


def test_iter_tree_files_applies_the_shared_exclusion_and_still_yields_real_files(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """`doc-id.py`'s own migration-sweep walk, `_iter_tree_files` — the population
    `migrate()`'s citation rewrite, vendored-skip loop and Ruling 68 row (g) classifier
    (`_read_tree_text`) all iterate. Proof at the walk itself, not only at the shared
    predicate it calls: a wiring mistake (calling the predicate on the wrong string, or
    not at all) would pass the predicate-only tests above and still leak here.
    """
    root = tmp_path / "tree"
    excluded = [
        "uv.lock",
        "pnpm-lock.yaml",
        "frontend/pnpm-lock.yaml",
        "tests/fixtures/docs-ids/w37-4-checks/check35-readme-allowlist/README.md",
        "tests/fixtures/docs-migration/docs/notes/0001-example-note.md",
        "scripts/__pycache__/doc-index.cpython-312.pyc",
    ]
    included = ["docs/notes/0002-real.md", "scripts/doc-id.py", "README.md"]
    for rel in [*excluded, *included]:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("NT-0001 lives here\n", encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    seen = {p.relative_to(root).as_posix() for p in doc_id_cli._iter_tree_files(root)}

    for rel in excluded:
        assert rel not in seen, f"{rel} should have been excluded from the sweep"
    for rel in included:
        assert rel in seen, f"{rel} should still be part of the sweep"
    assert ".git/HEAD" not in seen
