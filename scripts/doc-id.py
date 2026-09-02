#!/usr/bin/env python3
"""doc-id.py — NT-0019's id allocator, checker, widener and migrator.

Subcommands: `next`, `check`, `widen`, `migrate`. `migrate` (W37-5) implements
`docs/notes/0019-one-id-per-document.md` §4 steps 1-7, built and proven against the
fixture corpus at `tests/fixtures/docs-migration/` — nothing in the real tree moves
until W37-6 points `--repo-root` at it, under its own preconditions.

`docs/notes/0019-one-id-per-document.md` §1.7 (`next`, `check`), §1.8 (`widen`), §4
(`migrate`).

**Standard library only** (G4/DP-5) — see `scripts/_docid.py`'s module docstring for why.
`subprocess` calls to `git` are git plumbing, not a package import, and are explicitly
authorised by the plan's Tech Stack line. `migrate` loads `scripts/doc-index.py` and
`scripts/audit-docs.py` by path (the same `importlib.util.spec_from_file_location` idiom
`audit-docs.py` already uses for its own checks 30-39) rather than reimplementing INDEX.md
rendering or the DP-7 freeze predicate a second time — NT-0003's lesson, applied to code
instead of prose: two definitions of "reference tokens only" is how they drift apart
(Ruling 68 §2, "One definition ... implementing it twice is how the two drift apart").

Usage:
    python3 scripts/doc-id.py next
    python3 scripts/doc-id.py check [--classify]
    python3 scripts/doc-id.py widen --to WIDTH
    python3 scripts/doc-id.py migrate [--repo-root PATH]
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import itertools
import re
import subprocess
import sys
import tempfile
import types
import zipfile
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Final

import _docid

REPO_ROOT: Final = Path(__file__).resolve().parent.parent

# English number words for widths this standard is ever likely to reach — PAD_WIDTH starts
# at 5 and widens only when INDEX.md passes 90 000 (NT-0019 §1.8), so a handful of small
# integers is the whole practical range.
_NUMBER_WORDS: Final = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
    "eighteen", "nineteen", "twenty",
)


def _number_word(n: int) -> str:
    try:
        return _NUMBER_WORDS[n]
    except IndexError:
        raise ValueError(f"no English word on file for {n}; extend _NUMBER_WORDS") from None


# ---------------------------------------------------------------------------------------
# Git plumbing: reading a ref's committed content without touching the working tree.
# ---------------------------------------------------------------------------------------


class GitArchiveError(RuntimeError):
    """`git archive` (or the `rev-parse` that checks a ref resolves) failed, naming why."""


def ref_exists(ref: str, repo_root: Path) -> bool:
    """True when `ref` resolves to a commit `repo_root`'s local git already knows about.

    Deliberately does **not** run `git fetch` — `.github/workflows/docs.yml`'s
    `fetch-depth: 0` is what makes `origin/main` resolvable in CI (NT-0019 §5.8), and a
    local caller is expected to have fetched. `next`/`check` mutating the local
    `refs/remotes/origin/main` pointer as a side effect of an allocation command would be
    a surprise; failing with a clear, actionable message is not.
    """
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0


def materialize_ref(ref: str, dest: Path, *, repo_root: Path) -> None:
    """Extract the full tree at git ref `ref` into directory `dest`.

    `next` must read `origin/main`'s committed content, never the working tree and never
    an uncommitted local file — NT-0019 §1.7 says so, and DP-8's contiguity argument in
    `docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md` depends on it: an unmerged
    number must not be counted, or `next` would hand it out again instead of reissuing it.
    Materialising to a throwaway directory and scanning it with the same `pathlib`-based
    functions used everywhere else avoids a second "read file content from a git blob"
    code path existing only for this one caller.
    """
    zip_path = dest / "_docid_ref_archive.zip"
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "archive", "--format=zip", "-o", str(zip_path), ref],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise GitArchiveError(
            f"`git archive {ref}` exited {proc.returncode}: {stderr or '(no stderr)'}"
        )
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    zip_path.unlink()


# ---------------------------------------------------------------------------------------
# `next` — the four sources NT-0019 §1.7 names, each a pure function over a tree on disk
# (a real checkout, a fixture directory, or a materialized git ref — all the same to these).
# ---------------------------------------------------------------------------------------

# Document-family directories that hold one governed file per number, flat (NT-0019 §1.4).
_DOC_FAMILY_DIRS: Final = (
    "workflows", "adrs", "rfcs", "plans", "ledgers",
    "rulings", "research", "closures", "findings",
)


def _candidate_header_paths(tree_root: Path) -> Iterator[Path]:
    """Every path NT-0019 §1.5 says carries a header: the document-family directories,
    `docs/process/`, every `README.md` anywhere in the tree, `.claude/roles/`,
    `.claude/skills/*/SKILL.md`, and `.claude/agents/`. `_templates/` is excluded by the
    caller, not here — see `scan_header_ids`.
    """
    seen: set[Path] = set()

    def _emit(paths: Iterable[Path]) -> Iterator[Path]:
        for path in paths:
            if path not in seen:
                seen.add(path)
                yield path

    for name in _DOC_FAMILY_DIRS:
        root = tree_root / "docs" / name
        if root.is_dir():
            yield from _emit(sorted(root.glob("*.md")))

    process_root = tree_root / "docs" / "process"
    if process_root.is_dir():
        yield from _emit(sorted(process_root.rglob("*.md")))

    yield from _emit(sorted(tree_root.rglob("README.md")))

    roles_root = tree_root / ".claude" / "roles"
    if roles_root.is_dir():
        yield from _emit(sorted(roles_root.glob("*.md")))

    skills_root = tree_root / ".claude" / "skills"
    if skills_root.is_dir():
        yield from _emit(sorted(skills_root.glob("*/SKILL.md")))

    agents_root = tree_root / ".claude" / "agents"
    if agents_root.is_dir():
        yield from _emit(sorted(agents_root.glob("*.md")))


@dataclass(frozen=True)
class HeaderScan:
    """The result of scanning every header-bearing location once.

    `skipped` exists so a file this scan cannot cover is *visible*, not silently dropped
    — raised in review of PR #567 against `tests/test_audit_docs_scan_roots.py`'s own
    lesson: a scan that quietly stops covering something must not read the same as a scan
    that covered everything and found nothing. A file with **no front matter at all**, or
    a header with no `id:` field, is not in `skipped` — that is the overwhelming majority
    of this repository today, pre-migration, and reporting *that* as a skip would be the
    noise the note itself warns against. Only a file whose front matter exists and fails
    to parse — `parse_header` raising `HeaderError` — lands in `skipped`, alongside the
    message naming why.
    """

    ids: tuple[tuple[str, int, Path], ...]
    skipped: tuple[tuple[Path, str], ...]
    candidates_scanned: int


def scan_governed_headers(tree_root: Path) -> HeaderScan:
    """Every governed file under the header-bearing locations, resolved into either a
    live id or a reported skip — the shared scan behind `next`'s header source and
    `check`'s duplicate/mismatch detection alike.

    Excludes `_templates/` (example headers with placeholder ids — the same exemption
    check 31 gets by path, NT-0019 §1.4) and vendored skill content (§1.5: a vendored
    skill's files are exempt from stamping, so they are never a real source of a live id —
    see `_docid.is_vendored`'s own docstring for the known detection gap) *before*
    attempting to parse either, so neither counts as a "skip": exclusion is not failure.

    A file whose front matter does not fit NT-0019 §1.5's closed grammar at all —
    `parse_header` raising `HeaderError` — is not fatal to the scan, but is recorded in
    `.skipped`, never silently dropped: verified against this repository's own real tree,
    `.claude/skills/create-adaptable-composable/SKILL.md` carries upstream front matter
    with a nested `metadata:` mapping, and `is_vendored` does not catch it (the reported
    LICENSE-detection gap). Whether a *governed* file's header is malformed enough to fail
    the gate is check 30's question (W37-4), not this scan's — this scan's job is finding
    every live id while making what it could not resolve legible to a reader of the CLI's
    output, since the scan itself cannot tell "malformed governed header" from
    "legitimately foreign, e.g. vendored, front matter".
    """
    ids: list[tuple[str, int, Path]] = []
    skipped: list[tuple[Path, str]] = []
    candidates_scanned = 0
    for path in _candidate_header_paths(tree_root):
        if "_templates" in path.relative_to(tree_root).parts:
            continue
        if _docid.is_vendored(path, tree_root):
            continue
        candidates_scanned += 1
        try:
            header = _docid.parse_header(path)
        except _docid.HeaderError as exc:
            skipped.append((path, str(exc)))
            continue
        if header is None or header.id is None:
            continue
        match = _docid.ID_RE.fullmatch(header.id)
        if match is None:
            continue
        ids.append((match.group(1), int(match.group(2)), path))
    return HeaderScan(
        ids=tuple(ids), skipped=tuple(skipped), candidates_scanned=candidates_scanned
    )


def scan_header_ids(tree_root: Path) -> Iterator[tuple[str, int]]:
    """Source 1 of 4 (NT-0019 §1.7): every header `id:` field under the governed
    locations — see `scan_governed_headers` for exactly what counts and why. Drops the
    `.skipped` report: a caller that needs it calls `scan_governed_headers` directly, as
    the CLI does for its own reporting.
    """
    for prefix, number, _path in scan_governed_headers(tree_root).ids:
        yield prefix, number


_SPEC_BOLD_RE: Final = re.compile(r"\*\*(FR|NFR|DEP|OQ)-0*(\d+)\*\*")


def scan_spec_bold_ids(tree_root: Path) -> Iterator[tuple[str, int]]:
    """Source 2 of 4: every bold requirement/open-question id inside `docs/specs/*.md`
    (NT-0019 §1.2: "requirement rows are bold ids in tables")."""
    specs_root = tree_root / "docs" / "specs"
    if not specs_root.is_dir():
        return
    for path in sorted(specs_root.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in _SPEC_BOLD_RE.finditer(text):
            yield match.group(1), int(match.group(2))


# A WK-/SL- row's own id is cited in its heading (NT-0019 §1.9's GitHub-alignment table
# titles a slice issue `SL-1242: <title>`, and §1.5 calls the row's own line "the row's
# heading"). Matches `### WK-1201 — Batch frame contract` and the same for `SL-`.
_ROADMAP_ROW_RE: Final = re.compile(r"^#{1,6}[ \t]+.*?\b(WK|SL)-0*(\d+)\b", re.MULTILINE)


def scan_roadmap_row_ids(tree_root: Path) -> Iterator[tuple[str, int]]:
    """Source 3 of 4: every WK-/SL- row heading inside `docs/roadmap.md`.

    The exact heading shape is inferred (W37-1's restructured `docs/roadmap.md` has not
    landed at the time this was written) rather than pinned by a worked example in
    NT-0019 or the map plan — flagged to the lead as a coordination point, not a blocker:
    if the real format differs, this is a one-function fix once real content exists.
    """
    roadmap = tree_root / "docs" / "roadmap.md"
    if not roadmap.is_file():
        return
    text = roadmap.read_text(encoding="utf-8", errors="replace")
    for match in _ROADMAP_ROW_RE.finditer(text):
        yield match.group(1), int(match.group(2))


def scan_index_ids(tree_root: Path) -> Iterator[tuple[str, int]]:
    """Source 4 of 4: every id `docs/INDEX.md` lists — the generated safety net. Read
    generically via `_docid.ID_RE` rather than any assumed column layout: `doc-index.py`
    (W37-3) owns `INDEX.md`'s exact shape, and this must keep working whatever it is,
    since NT-0019 only fixes "one row per id", not a column schema.
    """
    index_path = tree_root / "docs" / "INDEX.md"
    if not index_path.is_file():
        return
    text = index_path.read_text(encoding="utf-8", errors="replace")
    for match in _docid.ID_RE.finditer(text):
        yield match.group(1), int(match.group(2))


def compute_next(tree_root: Path) -> int:
    """`max` across all four NT-0019 §1.7 sources, plus one. No id anywhere -> 1."""
    numbers = [
        n
        for _, n in (
            *scan_header_ids(tree_root),
            *scan_spec_bold_ids(tree_root),
            *scan_roadmap_row_ids(tree_root),
            *scan_index_ids(tree_root),
        )
    ]
    return max(numbers, default=0) + 1


# ---------------------------------------------------------------------------------------
# `check` — NT-0019 §1.7: "fails the gate on any duplicate or header/filename mismatch."
# Contiguity is computed over `docs/INDEX.md`, never the working tree (DP-8): a local,
# not-yet-merged draft numbered above the merged maximum must not manufacture a phantom
# gap. Duplicate and mismatch detection, by contrast, must see the working tree — they are
# about one file's own header agreeing with itself and with its siblings, which is exactly
# what a pre-merge CI run on a PR branch needs to catch before the number ever reaches
# `origin/main`.
# ---------------------------------------------------------------------------------------

@dataclass(frozen=True)
class CheckFailure:
    """One `check` failure. `kind` is `"duplicate"`, `"mismatch"` or `"noncontiguous"`."""

    kind: str
    message: str


# Built from `_docid.FAMILY_PREFIXES` rather than restated anywhere in this file, so
# every filename-leading pattern below can never drift from the id grammar's own list.
_PREFIX_ALTERNATION: Final = "|".join(_docid.FAMILY_PREFIXES)

# A filename leads with one of `ID_RE`'s own prefixes, followed by a mandatory `-` before
# the padded digits (`PL-01240-slug.md`, never bare `PL01240`).
_FILENAME_ID_RE: Final = re.compile(rf"^({_PREFIX_ALTERNATION})-(\d+)-")


def find_duplicate_ids(tree_root: Path) -> list[CheckFailure]:
    """Every number claimed by more than one governed file's header.

    Keyed on the bare number, never `(prefix, number)`: NT-0019 §1.1 rule 1 is one global
    sequence shared by every family — `PL-1240` and `RL-1240` are as much a collision as
    two files both claiming `PL-1240`, because the number, not the prefix, is what "no
    number is used twice" protects.
    """
    seen: dict[int, tuple[str, Path]] = {}
    failures: list[CheckFailure] = []
    for prefix, number, path in scan_governed_headers(tree_root).ids:
        earlier = seen.get(number)
        if earlier is not None:
            earlier_prefix, earlier_path = earlier
            failures.append(
                CheckFailure(
                    "duplicate",
                    f"{number} is claimed by both {_docid.canonical(earlier_prefix, number)} "
                    f"({earlier_path}) and {_docid.canonical(prefix, number)} ({path})",
                )
            )
        else:
            seen[number] = (prefix, path)
    return failures


def find_header_filename_mismatches(tree_root: Path) -> list[CheckFailure]:
    """Every governed file whose header `id` disagrees with its own filename's padded
    integer. A file not led by a padded id at all (a charter, a README) has nothing to
    compare and is silently skipped, not flagged.
    """
    failures: list[CheckFailure] = []
    for prefix, number, path in scan_governed_headers(tree_root).ids:
        filename_match = _FILENAME_ID_RE.match(path.name)
        if filename_match is None:
            continue
        filename_prefix = filename_match.group(1)
        filename_number = int(filename_match.group(2))
        if (prefix, number) != (filename_prefix, filename_number):
            failures.append(
                CheckFailure(
                    "mismatch",
                    f"{path}: header id {_docid.canonical(prefix, number)} but filename "
                    f"pads {_docid.canonical(filename_prefix, filename_number)}",
                )
            )
    return failures


def find_noncontiguous_gaps(tree_root: Path) -> list[CheckFailure]:
    """Every gap in the numbers `docs/INDEX.md` lists — never the working tree (DP-8), so
    an unmerged local draft cannot manufacture a phantom gap. No `docs/INDEX.md` at all
    (pre-migration) is nothing to be non-contiguous about, not a failure.
    """
    numbers = sorted({n for _, n in scan_index_ids(tree_root)})
    failures: list[CheckFailure] = []
    for lower, upper in itertools.pairwise(numbers):
        if upper != lower + 1:
            failures.append(
                CheckFailure(
                    "noncontiguous",
                    f"docs/INDEX.md has a gap between {lower} and {upper}",
                )
            )
    return failures


def check(tree_root: Path) -> list[CheckFailure]:
    """Every `doc-id.py check` failure at `tree_root`: duplicates, header/filename
    mismatches, and `docs/INDEX.md` contiguity gaps.
    """
    return [
        *find_duplicate_ids(tree_root),
        *find_header_filename_mismatches(tree_root),
        *find_noncontiguous_gaps(tree_root),
    ]


# ---------------------------------------------------------------------------------------
# `check --classify` — Acceptance Standard item 3: a per-family count over every
# git-tracked file under `docs/`, whose total equals `git ls-files docs/ | wc -l` and
# whose `none` row is 0 once migration lands. The corpus is `git ls-files`, never a
# working-tree walk — `scripts/file-census.py` measured why: a walk picks up `.venv/`,
# `graphify-out/` and anything else untracked, which differs between two checkouts of the
# same commit.
# ---------------------------------------------------------------------------------------


class GitLsFilesError(RuntimeError):
    """`git ls-files` could not enumerate the tracked corpus, naming why."""


def git_ls_files(repo_root: Path, pathspec: str) -> list[str]:
    """Tracked files under `pathspec`, NUL-delimited via `git -C <repo_root> ls-files -z`.

    Raises `GitLsFilesError` naming the cause rather than returning an empty list when
    `repo_root` is not a git repository or `git` cannot be invoked at all — the same
    contract `scripts/file-census.py`'s `git_ls_files` gives, for the same reason: an
    empty census is indistinguishable from a clean repository.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z", "--", pathspec],
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise GitLsFilesError(f"could not invoke git: {exc}") from exc
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise GitLsFilesError(
            f"`git -C {repo_root} ls-files -- {pathspec}` exited {result.returncode}: "
            f"{stderr or '(no stderr)'}"
        )
    decoded = result.stdout.decode("utf-8", errors="replace")
    return [p for p in decoded.split("\x00") if p]


# Document-family directory name -> family word (NT-0019 §1.2's "Kind" column), for the
# nine directories that hold exactly one family each (§1.4). Built independently of
# `_docid.family_of` (which maps a *prefix*, not a directory name) rather than reused,
# because the two vocabularies coincide by construction, not by a shared table.
_CLASSIFY_FAMILY_BY_DIR: Final[dict[str, str]] = {
    "workflows": "workflow",
    "adrs": "decision",
    "rfcs": "proposal",
    "plans": "plan",
    "ledgers": "ledger",
    "rulings": "ruling",
    "research": "research",
    "closures": "closure",
    "findings": "finding",
}


def classify_docs_files(repo_root: Path) -> dict[str, int]:
    """Per-family count of every git-tracked file under `docs/` — Acceptance Standard
    item 3.

    `_templates/` gets its own `"template"` bucket (example headers with placeholder ids,
    never real ones — the same exemption check 31 gets by path, NT-0019 §1.4) rather than
    counting as `"none"`, which is reserved for a file this classifier cannot place at
    all — exactly the files a fresh, pre-migration `docs/` tree is full of today.

    `docs/specs/*.md` is classified `"requirement"`: it is a *container* for the FR-/NFR-/
    DEP-/OQ- row families (NT-0019 §1.2), not a document family in its own right, and
    "requirement" is the dominant content. This mapping — and the plain `docs/*.md` ->
    `"reference"`/`"none"` split below — is this script's own reasonable reading, not a
    table NT-0019 states outright; flagged as a coordination point for W37-1's templates
    and W37-4's checks 30-39 rather than asserted as settled.

    Widened by W37-5 (`migrate`'s own fixture-corpus proof of Acceptance Standard item 3
    needed it to be correct, not just documented as open): the five other living,
    top-level `docs/*.md` files NT-0019 §1.4's own tree names — `INDEX.md`,
    `REDIRECTS.csv`, `roadmap.md`, `open-questions.md`, alongside `README.md` — are
    `"reference"` too, not `"none"`. Before this widening, a post-migration tree carrying
    only those five plus `README.md` at the top level still reported four spurious
    `"none"` files, which is exactly the false failure this slice's own acceptance item
    (a) would otherwise have produced.
    """
    top_level_reference_files = frozenset(
        {"README.md", "INDEX.md", "REDIRECTS.csv", "roadmap.md", "open-questions.md"}
    )
    counts: dict[str, int] = {}
    for rel in git_ls_files(repo_root, "docs"):
        parts = Path(rel).parts  # ("docs", ...) always, since the pathspec was "docs"
        if len(parts) < 2:
            continue  # defensive: git ls-files -- "docs" cannot itself return "docs"
        if len(parts) == 2:
            family = "reference" if parts[1] in top_level_reference_files else "none"
        else:
            subdir = parts[1]
            if subdir == "_templates":
                family = "template"
            elif subdir == "specs":
                family = "requirement"
            elif subdir == "process":
                family = "reference"
            else:
                family = _CLASSIFY_FAMILY_BY_DIR.get(subdir, "none")
        counts[family] = counts.get(family, 0) + 1
    return counts


# ---------------------------------------------------------------------------------------
# `widen` — NT-0019 §1.8: "renames every padded file, rewrites every padded link target,
# appends to REDIRECTS.csv, updates the width in document-ids.md, regenerates INDEX.md;
# touches no citation, number, header or body line." Trigger: `INDEX.md` passes 90 000.
# ---------------------------------------------------------------------------------------


@dataclass(frozen=True)
class WidenResult:
    """What one `widen` run did, for the CLI to report and tests to assert on."""

    renamed: tuple[tuple[str, str], ...]  # (old relpath, new relpath), posix-separated
    document_ids_updated: bool
    pad_width_constant_updated: bool
    index_regenerated: bool
    warnings: tuple[str, ...]


def _find_padded_files(repo_root: Path, old_width: int) -> list[Path]:
    """Every file whose basename leads with `<PREFIX>-<digits>-`, at exactly `old_width`
    digits — the padded filename form (NT-0019 §1.1 rule 3). Excludes `_templates/`
    (example headers with placeholder ids, not real files to rename).
    """
    pattern = re.compile(rf"^({_PREFIX_ALTERNATION})-(\d{{{old_width}}})-")
    found = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if "_templates" in path.relative_to(repo_root).parts:
            continue
        if pattern.match(path.name):
            found.append(path)
    return sorted(found)


def _rename_padded_files(
    repo_root: Path, old_width: int, new_width: int
) -> list[tuple[str, str]]:
    """Rename every padded file found by `_find_padded_files` to `new_width`, returning
    `(old_relpath, new_relpath)` pairs, posix-separated, in the order renamed.
    """
    filename_re = re.compile(rf"^({_PREFIX_ALTERNATION})-(\d+)-(.*)$")
    renames: list[tuple[str, str]] = []
    for path in _find_padded_files(repo_root, old_width):
        match = filename_re.match(path.name)
        assert match is not None  # guaranteed by _find_padded_files's own pattern
        prefix, digits, rest = match.group(1), match.group(2), match.group(3)
        new_name = f"{_docid.padded(prefix, int(digits), width=new_width)}-{rest}"
        new_path = path.with_name(new_name)
        old_rel = path.relative_to(repo_root).as_posix()
        new_rel = new_path.relative_to(repo_root).as_posix()
        path.rename(new_path)
        renames.append((old_rel, new_rel))
    return renames


# A markdown link's target: `[text](target)`, captured so only `target` is rewritten and
# `text` — the citation, always unpadded per NT-0019 §1.1 rule 2 — is never touched.
_MARKDOWN_LINK_RE: Final = re.compile(r"(\]\()([^)\s]+)(\))")


def _rewrite_link_targets(repo_root: Path, renames: Iterable[tuple[str, str]]) -> None:
    """Rewrite every markdown link target whose final path segment (basename) matches a
    renamed file's old basename to the new basename, leaving the rest of the target (its
    directory prefix, however many `../` it carries) and the link's citation text alone.
    Matching on the basename, not the full relative path, sidesteps having to resolve a
    target's `../` segments against the linking file's own location.
    """
    basename_map = {
        old.rsplit("/", 1)[-1]: new.rsplit("/", 1)[-1] for old, new in renames
    }
    if not basename_map:
        return

    def _replace(match: re.Match[str]) -> str:
        target = match.group(2)
        head, _, basename = target.rpartition("/")
        new_basename = basename_map.get(basename)
        if new_basename is None:
            return match.group(0)
        new_target = f"{head}/{new_basename}" if head else new_basename
        return f"{match.group(1)}{new_target}{match.group(3)}"

    for path in repo_root.rglob("*.md"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        new_text = _MARKDOWN_LINK_RE.sub(_replace, text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")


_REDIRECTS_FIELDS: Final = ("old_id", "new_id", "old_path", "new_path")


def _append_redirects(repo_root: Path, renames: Iterable[tuple[str, str]]) -> None:
    """Append one row per rename to `docs/REDIRECTS.csv`, creating it with a header if it
    does not exist yet, preserving every existing row otherwise.

    Column schema (`old_id,new_id,old_path,new_path`) is this script's own choice: NT-0019
    fixes only that the file records "every old path and old id -> new id -> new path"
    (§1.4), not a column layout — `doc-id.py migrate` (W37-5) is what actually creates
    `REDIRECTS.csv` for the first time, and has not landed. Flagged as a coordination
    point rather than assumed settled.
    """
    renames = list(renames)
    if not renames:
        return  # nothing to record; do not create an empty REDIRECTS.csv out of nowhere
    redirects_path = repo_root / "docs" / "REDIRECTS.csv"
    redirects_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = redirects_path.is_file()
    with redirects_path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_REDIRECTS_FIELDS)
        if not file_exists:
            writer.writeheader()
        for old_rel, new_rel in renames:
            match = _FILENAME_ID_RE.match(old_rel.rsplit("/", 1)[-1])
            assert match is not None
            canonical_id = _docid.canonical(match.group(1), int(match.group(2)))
            writer.writerow(
                {
                    "old_id": canonical_id,
                    "new_id": canonical_id,
                    "old_path": old_rel,
                    "new_path": new_rel,
                }
            )


def _update_document_ids_width(repo_root: Path, old_width: int, new_width: int) -> bool:
    """Update the width sentence in `docs/process/document-ids.md` — NT-0019 §1.1 rule 3:
    "Filenames pad the integer to the standard's width, currently five." Returns whether
    an update was made; a missing file or an unrecognised sentence is not fatal (see
    `widen`'s docstring for why), just unreported to the caller as a success.
    """
    path = repo_root / "docs" / "process" / "document-ids.md"
    if not path.is_file():
        return False
    old_word, new_word = _number_word(old_width), _number_word(new_width)
    text = path.read_text(encoding="utf-8")
    needle = f"the standard's width, currently {old_word}"
    if needle not in text:
        return False
    path.write_text(
        text.replace(needle, f"the standard's width, currently {new_word}"),
        encoding="utf-8",
    )
    return True


def _update_pad_width_constant(repo_root: Path, new_width: int) -> bool:
    """Update `scripts/_docid.py`'s own `PAD_WIDTH` constant. Not one of NT-0019 §1.8's
    five enumerated widen actions, but required for `widen`'s own internal consistency:
    every `padded()` call — including the renames this very function just performed —
    reads `PAD_WIDTH`, so leaving it stale would make the tool contradict the width it
    just wrote into `document-ids.md`. It is the script's own constant, not a governed
    document's citation, number, header or body line, so updating it does not violate
    §1.8's "touches no citation..." constraint.
    """
    path = repo_root / "scripts" / "_docid.py"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^PAD_WIDTH: Final = (\d+)$", text, re.MULTILINE)
    if match is None:
        return False
    new_text = text[: match.start(1)] + str(new_width) + text[match.end(1) :]
    path.write_text(new_text, encoding="utf-8")
    return True


def _regenerate_index(repo_root: Path) -> bool:
    """Invoke `scripts/doc-index.py` (W37-3) to regenerate `docs/INDEX.md` after a widen.
    Returns `False`, without failing, when that script does not exist yet — true during
    this slice's own development, before W37-3 merges; `widen`'s CLI reports it as a
    warning rather than a silent no-op.
    """
    doc_index_script = repo_root / "scripts" / "doc-index.py"
    if not doc_index_script.is_file():
        return False
    subprocess.run(
        [sys.executable, str(doc_index_script)], cwd=repo_root, check=True
    )
    return True


def widen(repo_root: Path, *, to: int) -> WidenResult:
    """Widen the padded-id filename width from `_docid.PAD_WIDTH` to `to`.

    NT-0019 §1.8's five actions, plus updating `scripts/_docid.py`'s own `PAD_WIDTH`
    constant (see `_update_pad_width_constant`'s docstring for why that is in scope).
    Renames and link-target rewrites are exact and total for what this function can see;
    `_append_redirects`'s column schema and `_update_document_ids_width`'s exact sentence
    match are this script's own reasonable readings of an underspecified point, flagged in
    this slice's PR rather than silently assumed.
    """
    old_width = _docid.PAD_WIDTH
    warnings: list[str] = []

    renames = _rename_padded_files(repo_root, old_width, to)
    _rewrite_link_targets(repo_root, renames)
    _append_redirects(repo_root, renames)

    document_ids_updated = _update_document_ids_width(repo_root, old_width, to)
    if not document_ids_updated:
        warnings.append(
            "docs/process/document-ids.md was not updated — either it does not exist "
            "yet, or its width sentence did not match the expected wording"
        )

    pad_width_constant_updated = _update_pad_width_constant(repo_root, to)
    if not pad_width_constant_updated:
        warnings.append("scripts/_docid.py's PAD_WIDTH constant was not found to update")

    index_regenerated = _regenerate_index(repo_root)
    if not index_regenerated:
        warnings.append(
            "docs/INDEX.md was not regenerated — scripts/doc-index.py does not exist yet"
        )

    return WidenResult(
        renamed=tuple(renames),
        document_ids_updated=document_ids_updated,
        pad_width_constant_updated=pad_width_constant_updated,
        index_regenerated=index_regenerated,
        warnings=tuple(warnings),
    )


@dataclass(frozen=True)
class NextResult:
    """`next`'s answer, plus what it could not resolve — reported, not silent (same
    reasoning as `HeaderScan`, and over the same materialised tree, so `next`'s report and
    its number are always about the identical snapshot)."""

    number: int
    skipped: tuple[tuple[Path, str], ...]


def compute_next_at_ref(ref: str, *, repo_root: Path = REPO_ROOT) -> NextResult:
    """`compute_next`, but reading `ref`'s committed content rather than any local
    directory — the entry point `next`'s CLI uses.
    """
    if not ref_exists(ref, repo_root):
        raise GitArchiveError(
            f"{ref!r} does not resolve to a commit in {repo_root} — fetch it first "
            f"(e.g. `git fetch origin main`)"
        )
    with tempfile.TemporaryDirectory(prefix="doc-id-next-") as tmp:
        tree = Path(tmp)
        materialize_ref(ref, tree, repo_root=repo_root)
        number = compute_next(tree)
        skipped = scan_governed_headers(tree).skipped
        return NextResult(number=number, skipped=skipped)


# ---------------------------------------------------------------------------------------
# `migrate` — NT-0019 §4's seven steps (assign, split, restructure the roadmap, move,
# stamp, rewrite citations, regenerate), run once against a tree on disk. Built and proven
# against `tests/fixtures/docs-migration/` (W37-5); nothing in the real tree moves until
# W37-6 points `--repo-root` at it, under that slice's own preconditions.
#
# Two properties the tests pin (dispatch, `docs/plans/2026-09-01-nt-0019-id-standard-map-
# plan.md` Slice W37-5): **deterministic** (two independent runs from the same starting
# input produce byte-identical output, including the number assignment) and **idempotent**
# (running `migrate` again on already-migrated output is a no-op, zero diff). Idempotency
# falls out of each discovery function's own shape: every `_discover_*` function below
# looks for a *legacy* shape only (a bullet-list ADR header, a `YYYY-MM-DD-` plan filename,
# a bare `F<n>` finding cell, a bold `**FR-EX-1**`-style spec id with an alphabetic module
# segment) — once a file is migrated it no longer has that shape (it moved, or its tokens
# changed to the numeric-only post-migration form), so a second run's discovery passes find
# nothing there and touch nothing. The one file that does *not* move or change shape
# detectably by absence is a vendored skill's own `SKILL.md` (NT-0019 §1.5): it is stamped
# in place, so its discovery function checks `_docid.parse_header` directly rather than
# relying on "the old thing is gone".
# ---------------------------------------------------------------------------------------


def _load_module(name: str, path: Path) -> types.ModuleType:
    """Load a `scripts/` module by path — required for every hyphenated filename here
    (`doc-index.py`, `audit-docs.py` are not legal `import` targets). The exact idiom
    `scripts/audit-docs.py`'s own `_load_module` already uses for `_docid.py` and
    `doc-index.py`, copied rather than imported from there: `audit-docs.py` is a sibling
    script, not a package this module can import from, and loading *it* by path (to reuse
    its DP-7 freeze predicate, below) needs the identical helper on this side too.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_doc_index(repo_root: Path = REPO_ROOT) -> types.ModuleType:
    """`scripts/doc-index.py`, loaded by path. Always loaded from *this* repository's own
    `scripts/`, never from a `--repo-root` fixture target — a fixture corpus carries no
    copy of the tooling, only the governed documents the tooling operates on, the same
    reason `docs/_templates/` (below) is always read from this repository regardless of
    which tree `migrate` is pointed at.
    """
    return _load_module("_doc_index_for_migrate", repo_root / "scripts" / "doc-index.py")


def _load_audit_docs(repo_root: Path = REPO_ROOT) -> types.ModuleType:
    """`scripts/audit-docs.py`, loaded by path, for its DP-7 freeze predicate
    (`frozen_file_matches_after_migration_stamp`) — Ruling 68 §3: "The frozen-family
    branch of the filter calls check 34's DP-7 predicate rather than reimplementing it."
    Loading the whole module executes its own top-level `_docid`/`doc-index.py` loads and
    constant definitions, but never `main()` (guarded by `if __name__ == "__main__":`), so
    this is cheap and side-effect-free against the filesystem.
    """
    return _load_module("_audit_docs_for_migrate", repo_root / "scripts" / "audit-docs.py")


# ---------------------------------------------------------------------------------------
# Templates: the single source for what a stamped header contains, per family — read from
# *this* repository's `docs/_templates/`, never the migration target's (Ruling 70's
# reasoning applied a second place: "the permitted set for a family is the set of keys in
# that family's template front matter").
# ---------------------------------------------------------------------------------------

_MIGRATE_TEMPLATE_FILENAME: Final[Mapping[str, str]] = {
    "ADR": "ADR.md", "RFC": "RFC.md", "PL": "PL.md", "RL": "RL.md", "CR": "CR.md",
    "REFERENCE": "REFERENCE.md",
}

_LEADING_COMMENT_RE: Final = re.compile(r"\A<!--.*?-->\n?\n?", re.DOTALL)


def _template_header_lines(prefix: str) -> list[str]:
    """The raw `key: value` lines of `prefix`'s template header block, after stripping the
    template's own leading `<!-- ... -->` instructional comment — the same reading
    `scripts/audit-docs.py`'s `_template_front_matter_lines` gives the identical files, for
    the identical reason (a template's placeholder values are policy data, never a document
    instance to parse as one).
    """
    path = REPO_ROOT / "docs" / "_templates" / _MIGRATE_TEMPLATE_FILENAME[prefix]
    text = _LEADING_COMMENT_RE.sub("", path.read_text(encoding="utf-8"), count=1)
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: expected a leading `---` block")
    closing = lines.index("---", 1)
    return lines[1:closing]


def _stamp_header(
    prefix: str,
    number: int | None,
    *,
    kind: str | None,
    title: str,
    status: str,
    created: date,
    owner: str,
    was: str | None,
    extra: Mapping[str, str] = types.MappingProxyType({}),
) -> str:
    """Render one document family's front-matter block by substituting the template's own
    placeholder tokens — never a hand-built YAML string, so a field this family's template
    does not declare can never silently appear here (the same guarantee Ruling 70 states
    for check 30's read of the same files, now applied to the writer as well as the
    checker). `number=None` is the Reference family (`prefix="REFERENCE"`): no prefix, no
    number, no `id:` line at all (§1.2), so the template simply carries none to substitute.
    """
    canon = _docid.canonical(prefix, number) if number is not None else None
    lines = list(_template_header_lines(prefix))
    rendered: list[str] = []
    for line in lines:
        key_match = re.match(r"^([A-Za-z_]+):", line)
        key = key_match.group(1) if key_match else None
        if key == "id":
            assert canon is not None
            line = re.sub(r"id:\s*\S+", f"id: {canon}", line)
        elif key == "kind":
            if kind is None:
                continue
            line = re.sub(r"kind:\s*\S+(\s*#.*)?$", f"kind: {kind}", line)
        elif key == "title":
            line = f"title: {title}"
        elif key == "status":
            line = re.sub(r"status:\s*\S+", f"status: {status}", line)
        elif key == "created":
            line = f"created: {created.isoformat()}"
        elif key == "owner":
            line = re.sub(r"owner:\s*\S+(\s*#.*)?$", f"owner: {owner}", line)
        elif key == "tree":
            continue  # this fixture-corpus migration carries no real commit sha to stamp
        elif key in ("phase", "work", "slice", "deliverable", "lands_in", "trigger"):
            continue  # not populated by this slice's migration — no data source for them
        elif key in ("supersedes", "superseded_by", "corrected_by", "corrects", "relates"):
            pass  # keep the template's own empty default ([] / ~)
        rendered.append(line)
    if was is not None:
        rendered.append(f"was: {was}")
    for extra_key, extra_value in extra.items():
        rendered.append(f"{extra_key}: {extra_value}")
    return "---\n" + "\n".join(rendered) + "\n---\n"


def _strip_front_matter(text: str) -> str:
    """`text` with a leading `---`-delimited block removed, unchanged if there is none —
    the same reading `frozen_file_matches_after_migration_stamp` gives, factored out so
    the split-concatenation check (class 4) can use it without going through that
    function's redirects-inversion, which does not apply mid-split.
    """
    lines = text.splitlines()
    if lines and lines[0] == "---":
        try:
            closing = lines.index("---", 1)
            return "\n".join(lines[closing + 1 :])
        except ValueError:
            return text
    return text


# ---------------------------------------------------------------------------------------
# The pending-assignment record: one shape covers every family this slice's fixture corpus
# carries. `materialize` dispatches phase C (below) to the family-specific writer.
# ---------------------------------------------------------------------------------------


@dataclass
class _Draft:
    materialize: str  # "document" | "requirement" | "roadmap_row" | "register_row" | "phase"
    prefix: str
    kind: str | None
    title: str
    status: str
    created: date
    owner: str
    tie_break: tuple[str, int]  # (source file, in-file order) — beneath (created, family rank)
    old_token: str | None  # a bare legacy citation form this becomes, for the rewrite map
    was: str | None = None  # `was:` value for a "document" draft
    body: str = ""  # a "document" draft's final body (post header-conversion / split)
    new_path: Path | None = None  # filled once the target directory + slug are known
    phase: str | None = None
    work_token: str | None = None  # this draft's own family+number, for an SL's `work:`
    number: int = 0  # filled in during assignment (phase B)
    # requirement/register-row fields:
    source_path: Path | None = None
    match_span: tuple[int, int] | None = None  # char offsets of the old token, for in-place rewrite


@dataclass
class MigrateResult:
    """What one `migrate` run did — enough for a caller (the CLI, or a test) to report it
    and for the redirects/citation-rewrite passes to work from.
    """

    assigned: tuple[tuple[str, str], ...]  # (old_token_or_empty, new_canonical_id)
    redirect_rows: tuple[dict[str, str], ...]  # old_id, new_id, old_path, new_path
    files_written: tuple[str, ...]
    files_deleted: tuple[str, ...]
    skipped_vendored: tuple[str, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------------------
# Phase A — discovery. Each function returns `_Draft`s for exactly one legacy shape, never
# touching disk beyond reading it.
# ---------------------------------------------------------------------------------------

_FAMILY_RANK: Final[Mapping[str, int]] = {
    prefix: rank for rank, prefix in enumerate(_docid.FAMILY_PREFIXES)
}

_NOTE_TITLE_RE: Final = re.compile(r"^#\s+NT-(\d{4})\s+—\s+(.+)$", re.MULTILINE)
_NOTE_RAISED_RE: Final = re.compile(
    r"^\|\s*\*\*Raised\*\*\s*\|\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE
)
_NOTE_STATUS_RE: Final = re.compile(r"^\|\s*\*\*Status\*\*\s*\|\s*`?(\w+)`?", re.MULTILINE)
_NOTE_STATUS_MAP: Final[Mapping[str, str]] = {
    "open": "draft", "accepted": "active", "landed": "closed",
    "dropped": "retired", "superseded": "superseded",
}


def _discover_notes(root: Path) -> list[_Draft]:
    """A note's legacy prose-table header (NT-0019 §5.2: "prose header → front matter,
    statuses mapped") — matched only on the `# NT-<4 digits> — <title>` heading, so an
    already-migrated `RFC-<n>-*.md` (no such heading) is invisible to a second run.
    """
    drafts: list[_Draft] = []
    notes_dir = root / "docs" / "notes"
    if not notes_dir.is_dir():
        return drafts
    for path in sorted(notes_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title_match = _NOTE_TITLE_RE.search(text)
        if title_match is None:
            continue
        old_number, title = title_match.group(1), title_match.group(2)
        raised_match = _NOTE_RAISED_RE.search(text)
        if raised_match is None:
            raise ValueError(f"{path}: no **Raised** date found in the legacy note header")
        created = date.fromisoformat(raised_match.group(1))
        status_match = _NOTE_STATUS_RE.search(text)
        legacy_status = status_match.group(1) if status_match else "open"
        status = _NOTE_STATUS_MAP.get(legacy_status, "active")
        # Body: replace the H1 + prose table with just the title line (RFC- form), keeping
        # everything from the first `---` separator's *content* onward untouched.
        body_start = text.find("\n---\n")
        rest = text[body_start + len("\n---\n") :] if body_start != -1 else ""
        body = f"# {title}\n\n{rest.lstrip(chr(10))}".rstrip("\n") + "\n"
        drafts.append(
            _Draft(
                materialize="document", prefix="RFC", kind="process", title=title,
                status=status, created=created, owner="maintainer",
                tie_break=(path.relative_to(root).as_posix(), 0),
                old_token=f"NT-{old_number}", was=path.relative_to(root).as_posix(),
                body=body,
            )
        )
    return drafts


_ADR_TITLE_RE: Final = re.compile(r"^#\s+ADR-(\d{4})\s+—\s+(.+)$", re.MULTILINE)
_ADR_STATUS_RE: Final = re.compile(r"^-\s+\*\*Status:\*\*\s*(\w+)", re.MULTILINE)
_ADR_DATE_RE: Final = re.compile(r"^-\s+\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)
_ADR_STATUS_MAP: Final[Mapping[str, str]] = {
    "accepted": "active", "proposed": "draft", "deprecated": "retired",
    "superseded": "superseded",
}


def _discover_adrs(root: Path) -> list[_Draft]:
    """An ADR's legacy bullet header (NT-0019 §5.2: "bullet header → front matter"),
    matched on `# ADR-<4 digits> — <title>` — invisible to a second run once the file has
    moved to `docs/adrs/ADR-<n>-*.md` with no such heading.
    """
    drafts: list[_Draft] = []
    adr_dir = root / "docs" / "adr"
    if not adr_dir.is_dir():
        return drafts
    for path in sorted(adr_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title_match = _ADR_TITLE_RE.search(text)
        if title_match is None:
            continue
        old_number, title = title_match.group(1), title_match.group(2)
        date_match = _ADR_DATE_RE.search(text)
        if date_match is None:
            raise ValueError(f"{path}: no **Date:** bullet found in the legacy ADR header")
        created = date.fromisoformat(date_match.group(1))
        status_match = _ADR_STATUS_RE.search(text)
        legacy_status = status_match.group(1) if status_match else "accepted"
        status = _ADR_STATUS_MAP.get(legacy_status, "active")
        # Body: drop the bullet metadata block (every leading `- **Key:** ...` line right
        # after the title), keep the title heading and everything from the first `##`
        # section onward untouched.
        lines = text.splitlines()
        first_section = next(i for i, ln in enumerate(lines) if ln.startswith("## "))
        body = f"# {title}\n\n" + "\n".join(lines[first_section:]).rstrip("\n") + "\n"
        drafts.append(
            _Draft(
                materialize="document", prefix="ADR", kind=None, title=title,
                status=status, created=created, owner="decision-maker",
                tie_break=(path.relative_to(root).as_posix(), 0),
                old_token=f"ADR-{old_number}", was=path.relative_to(root).as_posix(),
                body=body,
            )
        )
    return drafts


_PLAN_FILENAME_RE: Final = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
_RULING_HEADING_RE: Final = re.compile(r"^##\s+Ruling\s+(\d+)\s*(?:—\s*(.+))?$", re.MULTILINE)

# NT-0019 §5.2's suffix -> kind mapping, longest/most-specific suffix first so
# `-slice-map` is not shadowed by a hypothetical shorter alternative.
_PLAN_SUFFIX_KIND: Final[tuple[tuple[str, str], ...]] = (
    ("-final-review", "review"), ("-verified", "review"),
    ("-handover", "handover"),
    ("-slice-map", "map"), ("-map-plan", "map"),
)


def _plan_kind_for_slug(slug: str) -> str:
    for suffix, kind in _PLAN_SUFFIX_KIND:
        if slug.endswith(suffix):
            return kind
    return "leaf"


def _discover_multi_ruling_files(root: Path) -> list[_Draft]:
    """A legacy multi-ruling file (NT-0019 §4 step 2: "Multi-ruling files → one per
    `## Ruling N`"), split one ruling per `## Ruling N` heading. Matched only on a
    `YYYY-MM-DD-`-prefixed filename under `docs/plans/` that contains at least one
    `## Ruling N` heading — a post-migration `RL-<n>-*.md` has neither shape.

    Date source: this corpus's own reasonable extension of "filename date for plans"
    (NT-0019 §4 step 1) to a file that is *found* under `docs/plans/` with that naming
    convention even though it does not *stay* a plan after the split — flagged in the PR
    description as a coordination point, the same way `doc-id.py`'s roadmap-row regex was
    flagged by W37-2 before real roadmap content existed to check it against.

    Preamble (any text before the first `## Ruling` heading — here, just the file's own
    title line) is prepended to the *first* split ruling's body, so the concatenation of
    every split output reproduces this file's body lines in order (Ruling 68 class 4) —
    this corpus's own necessary refinement of step 1's tie-break for "several records
    split from one source file": ties are broken by the record's own position in the file.
    """
    drafts: list[_Draft] = []
    plans_dir = root / "docs" / "plans"
    if not plans_dir.is_dir():
        return drafts
    for path in sorted(plans_dir.glob("*.md")):
        m = _PLAN_FILENAME_RE.match(path.name)
        if m is None:
            continue
        text = path.read_text(encoding="utf-8")
        headings = list(_RULING_HEADING_RE.finditer(text))
        if not headings:
            continue
        created = date.fromisoformat(m.group(1))
        rel = path.relative_to(root).as_posix()
        for i, heading in enumerate(headings):
            number_word, title = heading.group(1), (heading.group(2) or "").strip()
            start = heading.start() if i > 0 else 0  # preamble folds into the first ruling
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            section_text = text[start:end].rstrip("\n") + "\n"
            drafts.append(
                _Draft(
                    materialize="document", prefix="RL", kind=None,
                    title=title or f"Ruling {number_word}",
                    status="active", created=created, owner="decision-maker",
                    tie_break=(rel, i),
                    old_token=f"Ruling {number_word}", was=rel, body=section_text,
                )
            )
    return drafts


def _discover_headed_split_file(
    root: Path, rel_path: str, heading_re: re.Pattern[str], prefix: str, owner: str
) -> list[_Draft]:
    """`closure-records.md`/`plan-reviews.md`'s shared shape: one `###` heading per
    record, each ending in the date it closed/ran — matched only at the exact legacy path,
    so a second run (the file already moved to `docs/closures/`) finds nothing.

    Preamble (the file's own `# Title` and introductory blockquote, before the first
    `###` heading) folds into the first record's body, the identical rule
    `_discover_multi_ruling_files` uses and for the identical reason: the concatenation
    of every split output must reproduce this file's body lines in order (Ruling 68
    class 4), so no line may belong to no output.
    """
    drafts: list[_Draft] = []
    path = root / rel_path
    if not path.is_file():
        return drafts
    text = path.read_text(encoding="utf-8")
    headings = list(heading_re.finditer(text))
    for i, heading in enumerate(headings):
        title, created_str = heading.group(1).strip(), heading.group(2)
        start = heading.start() if i > 0 else 0
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        section_text = text[start:end].rstrip("\n") + "\n"
        drafts.append(
            _Draft(
                materialize="document", prefix=prefix, kind="work",
                title=title, status="active", created=date.fromisoformat(created_str),
                owner=owner, tie_break=(rel_path, i), old_token=None, was=rel_path,
                body=section_text,
            )
        )
    return drafts


_CLOSURE_HEADING_RE: Final = re.compile(
    r"^###\s+(.+?),?\s*(?:accepted\s+)?(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE
)
_REVIEW_HEADING_RE: Final = re.compile(r"^###\s+(.+?),\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def _discover_closure_records(root: Path) -> list[_Draft]:
    return _discover_headed_split_file(
        root, "docs/audit/closure-records.md", _CLOSURE_HEADING_RE, "CR", "auditor"
    )


def _discover_plan_reviews(root: Path) -> list[_Draft]:
    drafts = _discover_headed_split_file(
        root, "docs/audit/plan-reviews.md", _REVIEW_HEADING_RE, "CR", "lead"
    )
    for d in drafts:
        d.kind = "review"
    return drafts


def _discover_plain_plans(root: Path) -> list[_Draft]:
    """Every remaining `YYYY-MM-DD-*.md` file directly under `docs/plans/` that is *not*
    a multi-ruling file (those are `_discover_multi_ruling_files`'s) — `kind:` from its
    filename suffix (NT-0019 §5.2). Matched on the date-prefixed legacy filename only, so
    an already-migrated `PL-<n>-*.md` (no date prefix) is invisible to a second run.
    """
    drafts: list[_Draft] = []
    plans_dir = root / "docs" / "plans"
    if not plans_dir.is_dir():
        return drafts
    for path in sorted(plans_dir.glob("*.md")):
        m = _PLAN_FILENAME_RE.match(path.name)
        if m is None:
            continue
        text = path.read_text(encoding="utf-8")
        if _RULING_HEADING_RE.search(text):
            continue  # a multi-ruling file — the other discovery function's
        created_str, slug = m.group(1), m.group(2)
        created = date.fromisoformat(created_str)
        kind = _plan_kind_for_slug(slug)
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1) if title_match else slug
        drafts.append(
            _Draft(
                materialize="document", prefix="PL", kind=kind, title=title,
                status="active", created=created, owner="planner",
                tie_break=(path.relative_to(root).as_posix(), 0),
                old_token=None, was=path.relative_to(root).as_posix(),
                body=text.rstrip("\n") + "\n",
            )
        )
    return drafts


_LEGACY_SPEC_BOLD_RE: Final = re.compile(r"\*\*(FR|NFR|DEP|OQ)-([A-Z]+)-(\d+)\*\*")


def _discover_requirements(root: Path) -> list[_Draft]:
    """Every legacy `**FR-<MODULE>-<n>**`-shaped bold id in `docs/specs/*.md` (NT-0019 §4
    step 1: "spec module order then clause order for requirements, using the module's
    first-commit date"). Matched only on the *module-coded* legacy form (an alphabetic
    segment between the prefix and the number) — the post-migration form `**FR-<n>**` has
    none, so a second run finds nothing.

    Date source: `_module_first_commit_date` below — real git history when `root` is a
    git checkout (a real repository, or a test's own `tiny_repo`-style fixture), today's
    date as a graceful fallback when it is not (a plain-directory `tmp_path` fixture in a
    unit test with no git history at all). Every clause in one spec file shares that one
    module-level date; ordering *within* the file is the tie-break (`i`, this loop's own
    enumeration order — spec module order is the outer loop's `sorted(specs_dir.glob(...))`
    over filenames).
    """
    drafts: list[_Draft] = []
    specs_dir = root / "docs" / "specs"
    if not specs_dir.is_dir():
        return drafts
    for path in sorted(specs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        module_date = _module_first_commit_date(path, root)
        for i, m in enumerate(_LEGACY_SPEC_BOLD_RE.finditer(text)):
            prefix, module, number = m.group(1), m.group(2), m.group(3)
            title = f"{prefix}-{module}-{number}"
            drafts.append(
                _Draft(
                    materialize="requirement", prefix=prefix, kind=None, title=title,
                    status="active", created=module_date, owner="decision-maker",
                    tie_break=(path.relative_to(root).as_posix(), i),
                    old_token=f"{prefix}-{module}-{number}",
                    source_path=path, match_span=m.span(),
                )
            )
    return drafts


def _module_first_commit_date(path: Path, root: Path) -> date:
    """The spec module's git first-commit date, when `root` is inside a git checkout;
    falls back to today's date when it is not (a plain-directory `tmp_path` fixture in a
    unit test that does not need real date values, only relative order).
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "log", "--diff-filter=A", "--follow",
             "--format=%aI", "--", str(path.relative_to(root))],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return date.today()
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if proc.returncode != 0 or not lines:
        return date.today()
    return date.fromisoformat(lines[-1][:10])


_ROADMAP_LEGACY_PHASE_RE: Final = re.compile(
    r"^##\s+Phase\s+(\S+)\s+—\s+(.+)$", re.MULTILINE
)
_ROADMAP_LEGACY_WORK_RE: Final = re.compile(
    r"^###\s+(W\d+[a-z]?)\s+—\s+(.+)$\nstatus:\s*(\w+)$", re.MULTILINE
)
_ROADMAP_LEGACY_SLICE_RE: Final = re.compile(
    r"^-\s+\*\*(W\d+[a-z]?-\d+)\*\*\s+(.+?)\s+—\s+status:\s*(\w+)\s*$", re.MULTILINE
)


def _discover_roadmap(root: Path) -> tuple[list[_Draft], str | None, str | None]:
    """The legacy roadmap shape this corpus defines (module docstring above): a `##
    Phase <id> — <title>` heading, `### <work-key> — <title>` + `status:` for each work,
    and `- **<slice-key>** <title> — status: <status>` bullets under it (NT-0019 §4 step
    3). Returns `(drafts, phase_id, phase_title)` — `phase_id`/`phase_title` are `None`
    when no legacy phase section is found (a second run: the file is already restructured
    into the `## P<n> — ...` fenced form, which this regex does not match).
    """
    roadmap_path = root / "docs" / "roadmap.md"
    if not roadmap_path.is_file():
        return [], None, None
    text = roadmap_path.read_text(encoding="utf-8")
    phase_match = _ROADMAP_LEGACY_PHASE_RE.search(text)
    if phase_match is None:
        return [], None, None
    phase_id_raw, phase_title = phase_match.group(1), phase_match.group(2)
    phase_id = f"P{phase_id_raw}"
    created = _module_first_commit_date(roadmap_path, root)
    drafts: list[_Draft] = []
    order = 0
    for work_match in _ROADMAP_LEGACY_WORK_RE.finditer(text):
        work_key, work_title, work_status = work_match.groups()
        drafts.append(
            _Draft(
                materialize="roadmap_row", prefix="WK", kind=None, title=work_title,
                status=work_status, created=created, owner="maintainer",
                tie_break=("docs/roadmap.md", order), old_token=work_key, phase=phase_id,
            )
        )
        order += 1
        work_end = work_match.end()
        next_work = _ROADMAP_LEGACY_WORK_RE.search(text, work_end)
        section_end = next_work.start() if next_work else len(text)
        for slice_match in _ROADMAP_LEGACY_SLICE_RE.finditer(text, work_end, section_end):
            slice_key, slice_title, slice_status = slice_match.groups()
            drafts.append(
                _Draft(
                    materialize="roadmap_row", prefix="SL", kind=None, title=slice_title,
                    status=slice_status, created=created, owner="planner",
                    tie_break=("docs/roadmap.md", order), old_token=slice_key,
                    phase=phase_id, work_token=work_key,
                )
            )
            order += 1
    return drafts, phase_id, phase_title


_REGISTER_FINDING_RE: Final = re.compile(r"\bF(\d+)\b")


def _discover_register(root: Path) -> list[_Draft]:
    """Bare `F<n>` Finding-id cells in the legacy `docs/audit/register.md` (NT-0019 §5.2:
    "Finding-id cells → `FD-n` with `was:`"). Matched only at the legacy path — a second
    run (moved to `docs/findings/register.md`) finds nothing there.
    """
    drafts: list[_Draft] = []
    path = root / "docs" / "audit" / "register.md"
    if not path.is_file():
        return drafts
    text = path.read_text(encoding="utf-8")
    created = _module_first_commit_date(path, root)
    order = 0
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cell = line.split("|")[1].strip()
        m = _REGISTER_FINDING_RE.fullmatch(cell)
        if m is None:
            continue
        drafts.append(
            _Draft(
                materialize="register_row", prefix="FD", kind=None, title=f"Finding {m.group(1)}",
                status="active", created=created, owner="auditor",
                tie_break=("docs/audit/register.md", order), old_token=f"F{m.group(1)}",
                source_path=path,
            )
        )
        order += 1
    return drafts


def _is_vendored_skill_manifest(path: Path) -> bool:
    """True only for the `SKILL.md` that *defines* a vendored skill's boundary (its own
    directory ships the `LICENSE`) — never a file beneath it. `_docid.is_vendored` cannot
    make this distinction by itself: called on `skill_dir/SKILL.md`, it walks up from
    `skill_dir` (a file's own directory), finds `skill_dir/LICENSE` immediately, and
    returns `True` for the manifest exactly as it does for anything beneath it (NT-0019
    §1.5: the manifest is stamped, only the files *beneath* it are exempt).
    """
    return path.name == "SKILL.md" and (path.parent / "LICENSE").is_file()


def _discover_vendored_skill_manifests(root: Path) -> list[Path]:
    """Every vendored skill's own `SKILL.md` that has not yet been stamped — the one
    discovery function in this module that cannot infer "already migrated" from a legacy
    shape being absent, because stamping does not move or rename this file (NT-0019 §1.5).
    """
    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return []
    out = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        if not _is_vendored_skill_manifest(skill_md):
            continue
        if _docid.parse_header(skill_md) is not None:
            continue  # already stamped
        out.append(skill_md)
    return out


def _iter_tree_files(root: Path) -> Iterator[Path]:
    """Every real file under `root`, sorted, excluding `.git/` — every whole-tree walk
    `migrate` and `migration_diff_violations` run needs this exclusion once a test (or a
    real checkout) makes `root` an actual git repository: `.git/index` and packed objects
    are binary, but `.git/HEAD`, `.git/config` and the ref files under `.git/refs/` decode
    as UTF-8 text perfectly well, so relying on `UnicodeDecodeError` alone to keep this
    module from ever reading — and, worse, rewriting — git's own plumbing is not a
    guarantee, only a coincidence of what today's token set happens not to match.
    """
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if ".git" in path.relative_to(root).parts:
            continue
        yield path


def _is_vendored_exempt(path: Path, root: Path) -> bool:
    """True for a file beneath a vendored skill's boundary that is *not* the manifest
    itself — exempt from stamping, citation rewrite and every migration action (NT-0019
    §1.5). The manifest (`_is_vendored_skill_manifest`) is never exempt: it is stamped
    and its own citations rewrite like any other file.
    """
    return _docid.is_vendored(path, root) and not _is_vendored_skill_manifest(path)


# ---------------------------------------------------------------------------------------
# Phase B — order and number. One combined sequence over every draft from every discovery
# function (NT-0019 D1: one global sequence), starting at `compute_next(root)` so a
# from-scratch corpus starts at 1 and an already-partly-migrated one (a second `migrate`
# run that somehow still found something new) continues after the current maximum.
# ---------------------------------------------------------------------------------------


def _sort_key(d: _Draft) -> tuple[date, int, str, int]:
    source, order = d.tie_break
    return (d.created, _FAMILY_RANK[d.prefix], source, order)


def _assign_numbers(drafts: list[_Draft], start: int) -> None:
    for offset, d in enumerate(sorted(drafts, key=_sort_key)):
        d.number = start + offset


# ---------------------------------------------------------------------------------------
# Phase C — materialize. Only two `materialize` kinds write anything themselves: a
# "document" draft becomes a new stamped file; "roadmap_row" drafts are consumed together
# by the roadmap restructure. A "requirement" or "register_row" draft writes nothing here
# — it contributes only an `(old_token, canonical_id)` pair to Phase D's global rewrite,
# because the spec file and the (moved) register file are rewritten by that same pass like
# every other citing file in the tree; a second rewrite mechanism here would be the
# duplicate-definition risk Ruling 67 §2 names ("one shared constant ... two definitions
# of 'a legacy form' will drift").
# ---------------------------------------------------------------------------------------

_DOCUMENT_FAMILY_DIR: Final[Mapping[str, str]] = {
    "ADR": "adrs", "RFC": "rfcs", "PL": "plans", "RL": "rulings", "CR": "closures",
}


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "untitled"


def _write_document_drafts(root: Path, drafts: list[_Draft]) -> tuple[list[str], list[str]]:
    """Every `materialize="document"` draft: stamp its header, write it under its family
    directory, and delete its `was` source once every draft sharing that source has been
    written. Returns `(files_written, files_deleted)`, both repo-relative posix paths.
    """
    written: list[str] = []
    was_sources: set[str] = set()
    for d in drafts:
        if d.materialize != "document":
            continue
        target_dir = root / "docs" / _DOCUMENT_FAMILY_DIR[d.prefix]
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{_docid.padded(d.prefix, d.number)}-{_slug(d.title)}.md"
        new_path = target_dir / filename
        d.new_path = new_path
        header = _stamp_header(
            d.prefix, d.number, kind=d.kind, title=d.title, status=d.status,
            created=d.created, owner=d.owner, was=d.was,
        )
        new_path.write_text(header + "\n" + d.body, encoding="utf-8")
        written.append(new_path.relative_to(root).as_posix())
        if d.was is not None:
            was_sources.add(d.was)

    deleted: list[str] = []
    for was in sorted(was_sources):
        source = root / was
        if source.is_file():
            source.unlink()
            deleted.append(was)
    return written, deleted


def _remove_if_empty(path: Path) -> None:
    if path.is_dir() and not any(path.iterdir()):
        path.rmdir()


_PHASE_TEMPLATE: Final = (
    "## {phase} — {title}\n"
    "\n"
    "```yaml\n"
    "status: active\n"
    "opened: {opened}\n"
    "target: ~\n"
    "gates: ~\n"
    "exit criteria: ~\n"
    "works: {works}\n"
    "```\n"
)


def _check_roadmap_not_silently_unrecognised(root: Path) -> None:
    """Task #32: `_discover_roadmap` returning nothing is ambiguous by construction —
    every `_discover_*` function's idempotency argument (module docstring above) reads
    "found nothing" as "already migrated", which is only true when something already
    moved or changed shape. `docs/roadmap.md` never moves and is rewritten in place, so
    that reading does not hold for it: a roadmap that still has works described in a shape
    `_discover_roadmap`'s legacy patterns do not recognise looks identical, to this
    script, to a roadmap with nothing left to convert.

    The one thing that *is* checkable without deciding anything about what the real shape
    is or how to convert it: post-migration, `docs/roadmap.md` carries `WK-` row headings
    `scan_roadmap_row_ids` (`_ROADMAP_ROW_RE`, line ~265) can see. So a roadmap file that
    exists, is non-blank, and has neither a legacy phase section (`_discover_roadmap`
    returned nothing) nor any `WK-` row already in it (nothing to show step 3 already ran)
    is not "nothing to do" — it is a shape this script does not recognise, and `migrate`
    must say so rather than silently report success. Called only from `migrate`'s
    `roadmap_drafts` branch, so it never runs, and never raises, when discovery succeeded.

    Deliberately does not try to tell "no works exist in the roadmap at all" apart from
    "works exist but not in a shape this script matches" — doing that from inside this
    check would mean guessing at the real shape, which is exactly what task #32 says not
    to do here. A roadmap that is genuinely work-free tripping this is an accepted,
    fail-safe false positive: a human confirms and moves on, rather than `migrate`
    silently reporting a conversion that never happened.
    """
    roadmap_path = root / "docs" / "roadmap.md"
    if not roadmap_path.is_file():
        return
    if not roadmap_path.read_text(encoding="utf-8").strip():
        return
    if any(prefix == "WK" for prefix, _ in scan_roadmap_row_ids(root)):
        return  # already migrated: WK- rows are step 3's own output, already present
    raise NotImplementedError(
        "migrate: docs/roadmap.md exists and is non-blank, but _discover_roadmap found no "
        "legacy '## Phase <id> — <title>' section, and docs/roadmap.md carries no WK- row "
        "either. That is not 'nothing to convert' -- it is an unrecognised shape (task "
        "#32): NT-0019 §4 step 3 requires each existing slice to become an SL- row and "
        "each existing work a WK- row, and the real roadmap's works do not match the "
        "legacy shape this script's patterns were built against. Resolving what the real "
        "shape is and how to convert it is open (task #32); migrate refuses to guess and "
        "silently report success instead."
    )


def _check_legacy_file_not_silently_unrecognised(
    path: Path, drafts: list[_Draft], description: str
) -> None:
    """The same class of defect `_check_roadmap_not_silently_unrecognised` guards against,
    for the three legacy files (`closure-records.md`, `plan-reviews.md`, `register.md`)
    whose own `_discover_*` docstrings already state the property that makes this check
    *simpler* than the roadmap's: each is "matched only at the exact legacy path", i.e.
    migrated by moving away from `path` entirely, never rewritten in place. So unlike the
    roadmap, there is no second signal to check for "already migrated" — `path` no longer
    existing already *is* that signal, and is handled by the first `return` below. A
    `path` that still exists and is non-blank therefore has no valid "already migrated"
    reading at all: zero discovered records from it is unrecognised shape, full stop
    (confirmed live for `register.md`: `_discover_register` requires a table cell to
    `fullmatch` bare `F<n>`, and the real file's cells are compound, e.g. `FR-DATA-57
    (F6)`) — the third instance of the pattern `_check_roadmap_not_silently_unrecognised`'s
    docstring names.
    """
    if not path.is_file():
        return  # moved away already: correctly read as "already migrated"
    if not path.read_text(encoding="utf-8").strip():
        return  # genuinely nothing in it
    if drafts:
        return  # discovery found something; nothing ambiguous to flag
    raise NotImplementedError(
        f"migrate: {path} exists and is non-blank, but no {description} were recognised "
        f"in it. That is not 'nothing to convert' -- this script's legacy pattern does not "
        f"match this file's real shape. Resolving the real shape is open; migrate refuses "
        f"to guess and silently report success instead."
    )


def _restructure_roadmap(
    root: Path, roadmap_drafts: list[_Draft], phase_id: str, phase_title: str
) -> None:
    """NT-0019 §4 step 3: the legacy `## Phase <id> — <title>` / `### <work-key>` /
    `- **<slice-key>**` shape becomes a `## P<n> — <title>` milestone section with a fenced
    field block, each `WK-`/`SL-` a heading carrying its own fenced row block (§1.5) — the
    exact shape `scripts/doc-index.py`'s `scan_phase_sections`/`scan_roadmap_rows` read at
    the time this was written (verified by reading that module directly, not inferred from
    NT-0019 §1.3's own plain, unfenced illustration).

    **Ruling 80 has since settled that discrepancy the other way**: the spec's unfenced
    illustration is right, `scan_phase_sections`'s fence requirement is the defect, and
    `PHASE.md` — enforced unfenced by `audit-docs.py`'s `_EXPECTED_NO_BLOCK_TEMPLATES`
    already — settles the real form. So the fenced phase heading this function emits is a
    known, ruled latent bug (not corrected here): it only runs on discovery finding a
    legacy phase section (the fixture's), the real roadmap's transform stays deferred
    (task #32) until `doc-index.py`'s parsers are fixed to match the ruling, and rewriting
    this function's *output shape* now would mean rebuilding it twice.

    The row block's field set (`id, family, title, status, created, owner, phase, [work]`)
    is narrower than NT-0019 §1.5's full closed set by construction, not as a workaround:
    it happens to satisfy `doc-index.py`'s current `_ROW_FIELDS` (Ruling 79: wrong in both
    directions — rejects `tree:`/`corrected_by:`/`relates:`, wrongly admits `kind:`/
    `slice:` on a `WK-` row), but that is this function never needing those fields for a
    freshly-converted row, not a deliberate accommodation of the wrong parser. Widening it
    once real `WK-`/`SL-` rows need `tree:`/`corrected_by:`/`relates:` will need the parser
    fix first, same as the fence.
    """
    work_ids = sorted(
        {d.old_token for d in roadmap_drafts if d.prefix == "WK"},
        key=lambda tok: next(
            d.number for d in roadmap_drafts if d.prefix == "WK" and d.old_token == tok
        ),
    )
    works_canon = [
        _docid.canonical("WK", next(d.number for d in roadmap_drafts if d.old_token == wid))
        for wid in work_ids
    ]
    lines = [
        _PHASE_TEMPLATE.format(
            phase=phase_id, title=phase_title,
            opened=min(d.created for d in roadmap_drafts).isoformat(),
            works=", ".join(works_canon),
        ).rstrip("\n")
    ]
    for d in sorted(roadmap_drafts, key=_sort_key):
        canon = _docid.canonical(d.prefix, d.number)
        family = "work" if d.prefix == "WK" else "slice"
        heading_level = "###" if d.prefix == "WK" else "####"
        block = [f"id: {canon}", f"family: {family}", f"title: {d.title}",
                  f"status: {d.status}", f"created: {d.created.isoformat()}",
                  f"owner: {d.owner}", f"phase: {d.phase}"]
        if d.prefix == "SL" and d.work_token is not None:
            work_canon = _docid.canonical(
                "WK", next(x.number for x in roadmap_drafts if x.old_token == d.work_token)
            )
            block.append(f"work: {work_canon}")
        block_text = "\n".join(block)
        lines.append(f"\n{heading_level} {canon} — {d.title}\n\n```yaml\n{block_text}\n```\n")
    (root / "docs" / "roadmap.md").write_text(
        "# Roadmap (fixture)\n\n" + "".join(lines), encoding="utf-8"
    )


# ---------------------------------------------------------------------------------------
# Phase D — rewrite every citation across the whole tree (NT-0019 §4 step 6). Longest
# tokens first, so a shorter token's word boundary cannot accidentally consume part of a
# longer one already handled (`W37` vs `W37-5`) — sequential whole-file passes, one token
# fully applied before the next, rather than one combined alternation, so this remains
# provably correct at fixture scale; a real corpus's performance is out of this slice's
# scope (nothing in DP-3's acceptance items is a performance NFR).
# ---------------------------------------------------------------------------------------


def _rewrite_citations(root: Path, token_map: Mapping[str, str]) -> list[str]:
    changed: list[str] = []
    ordered_tokens = sorted(token_map, key=len, reverse=True)
    patterns = [(tok, re.compile(rf"\b{re.escape(tok)}\b")) for tok in ordered_tokens]
    for path in _iter_tree_files(root):
        if _is_vendored_exempt(path, root):
            continue
        if path.name in ("REDIRECTS.csv",):
            continue  # generated below, from the same map — never itself rewritten
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        original = text
        for tok, pattern in patterns:
            if tok in text:
                text = pattern.sub(token_map[tok], text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(path.relative_to(root).as_posix())
    return changed


# ---------------------------------------------------------------------------------------
# Phase E — regenerate. `docs/REDIRECTS.csv` (append-only across runs, the same convention
# `widen`'s `_append_redirects` already uses for the identical file) and `docs/INDEX.md`
# (rendered fresh every run via `doc-index.py`'s own `build_corpus`/`render_index` — a pure
# function of the corpus, so a run that found nothing new reproduces byte-identical output,
# which is exactly what idempotency needs).
# ---------------------------------------------------------------------------------------


def _write_redirects(root: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    redirects_path = root / "docs" / "REDIRECTS.csv"
    redirects_path.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, str]] = []
    if redirects_path.is_file():
        with redirects_path.open(newline="", encoding="utf-8") as fh:
            existing = list(csv.DictReader(fh))
    with redirects_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_REDIRECTS_FIELDS)
        writer.writeheader()
        for row in existing:
            writer.writerow(row)
        for row in rows:
            writer.writerow(row)


def _regenerate_index_for_migrate(root: Path) -> None:
    doc_index = _load_doc_index()
    corpus = doc_index.build_corpus(root / "docs")
    fresh = doc_index.render_index(corpus)
    (root / "docs" / "INDEX.md").write_text(fresh, encoding="utf-8")


# ---------------------------------------------------------------------------------------
# `migrate` itself.
# ---------------------------------------------------------------------------------------


def migrate(root: Path) -> MigrateResult:
    """NT-0019 §4 steps 1-7 against `root` (a repository root, real or a fixture). Nothing
    outside `root` is read or written — no `--repo-root` argument reaches beyond the tree
    it names, which is also what keeps this safe to run repeatedly against the same
    fixture in a test suite.
    """
    warnings: list[str] = []

    drafts: list[_Draft] = []
    drafts += _discover_notes(root)
    drafts += _discover_adrs(root)
    drafts += _discover_multi_ruling_files(root)
    closure_drafts = _discover_closure_records(root)
    _check_legacy_file_not_silently_unrecognised(
        root / "docs" / "audit" / "closure-records.md", closure_drafts, "closure records"
    )
    drafts += closure_drafts
    review_drafts = _discover_plan_reviews(root)
    _check_legacy_file_not_silently_unrecognised(
        root / "docs" / "audit" / "plan-reviews.md", review_drafts, "plan reviews"
    )
    drafts += review_drafts
    drafts += _discover_plain_plans(root)
    requirement_drafts = _discover_requirements(root)
    roadmap_drafts, phase_id, phase_title = _discover_roadmap(root)
    register_drafts = _discover_register(root)
    _check_legacy_file_not_silently_unrecognised(
        root / "docs" / "audit" / "register.md", register_drafts, "register finding rows"
    )
    drafts += requirement_drafts + roadmap_drafts + register_drafts
    # Hoisted here to run alongside every other discovery, before any write below: a
    # malformed vendored manifest's HeaderError must abort migrate cleanly, not after
    # Phase C's document/roadmap/register writes have already landed on disk (task #34).
    # `_is_vendored_skill_manifest`'s LICENSE-based detection is still wrong (Ruling 69,
    # reassigned to W37-6 by Ruling 76) -- this hoist fixes only when the crash happens,
    # not whether it should have fired at all.
    vendored_skill_manifests = _discover_vendored_skill_manifests(root)

    start = compute_next(root)
    _assign_numbers(drafts, start)

    files_written, files_deleted = _write_document_drafts(root, drafts)

    if roadmap_drafts:
        if phase_id is None or phase_title is None:
            raise AssertionError("roadmap drafts found but no phase id/title discovered")
        _restructure_roadmap(root, roadmap_drafts, phase_id, phase_title)
    else:
        _check_roadmap_not_silently_unrecognised(root)

    register_moved_to: str | None = None
    if register_drafts:
        old_register = root / "docs" / "audit" / "register.md"
        new_register = root / "docs" / "findings" / "register.md"
        if old_register.is_file():
            new_register.parent.mkdir(parents=True, exist_ok=True)
            new_register.write_text(old_register.read_text(encoding="utf-8"), encoding="utf-8")
            old_register.unlink()
            files_written = [*files_written, "docs/findings/register.md"]
            files_deleted = [*files_deleted, "docs/audit/register.md"]
            register_moved_to = "docs/findings/register.md"

    for legacy_dir in ("docs/notes", "docs/adr", "docs/audit"):
        _remove_if_empty(root / legacy_dir)

    token_map: dict[str, str] = {}
    redirect_rows: list[dict[str, str]] = []
    assigned: list[tuple[str, str]] = []
    for d in drafts:
        canon = _docid.canonical(d.prefix, d.number)
        assigned.append((d.old_token or "", canon))
        if d.old_token is not None:
            token_map[d.old_token] = canon
        old_path = d.was or ""
        new_path = d.new_path.relative_to(root).as_posix() if d.new_path is not None else ""
        if d.materialize == "register_row":
            old_path, new_path = "docs/audit/register.md", (register_moved_to or "")
        elif d.materialize == "requirement" and d.source_path is not None:
            # Stays at the same path — a row family embedded in a shared file, not moved.
            old_path = new_path = d.source_path.relative_to(root).as_posix()
        elif d.materialize == "roadmap_row":
            old_path = new_path = "docs/roadmap.md"
        redirect_rows.append(
            {
                "old_id": d.old_token or "",
                "new_id": canon,
                "old_path": old_path,
                "new_path": new_path,
            }
        )

    rewritten = _rewrite_citations(root, token_map)

    skipped_vendored: list[str] = []
    for skill_md in vendored_skill_manifests:
        header = _stamp_header(
            "REFERENCE", None, kind=None, title=skill_md.parent.name, status="active",
            created=date.today(), owner="maintainer", was=None,
            extra={"vendored": "true", "origin": "vendored fixture, upstream unknown"},
        )
        body = skill_md.read_text(encoding="utf-8")
        skill_md.write_text(header + "\n" + body, encoding="utf-8")
        files_written = [*files_written, skill_md.relative_to(root).as_posix()]
    for path in _iter_tree_files(root):
        if _is_vendored_exempt(path, root):
            skipped_vendored.append(path.relative_to(root).as_posix())

    _write_redirects(root, redirect_rows)
    _regenerate_index_for_migrate(root)

    return MigrateResult(
        assigned=tuple(assigned),
        redirect_rows=tuple(redirect_rows),
        files_written=tuple(dict.fromkeys([*files_written, *rewritten])),
        files_deleted=tuple(files_deleted),
        skipped_vendored=tuple(skipped_vendored),
        warnings=tuple(warnings),
    )


# ---------------------------------------------------------------------------------------
# Acceptance item (g), DP-3's executable form (Ruling 68): the migration diff, filtered to
# hunks in the six-class closed enumeration, is empty. Independent of `migrate`'s own
# bookkeeping — computed from two trees on disk plus the `REDIRECTS.csv` `migrate` wrote,
# never from anything `migrate` claims about itself while running — so a bug in what
# `migrate` *reports* cannot also hide from what it *did*.
# ---------------------------------------------------------------------------------------

_MIGRATION_DIFF_GENERATED: Final = frozenset({"docs/INDEX.md", "docs/REDIRECTS.csv"})
_MIGRATION_DIFF_ROADMAP: Final = frozenset({"docs/roadmap.md", "docs/open-questions.md"})


def _read_tree_text(root: Path) -> dict[str, str | None]:
    """Every file under `root`, keyed by repo-relative posix path. `None` for a file that
    does not decode as UTF-8 (a binary asset this checker has nothing to say about — it
    reports a violation on it below rather than silently skipping, since a hunk this
    filter cannot classify must never pass through unexamined, DP-3's own rule for its own
    filter).
    """
    out: dict[str, str | None] = {}
    for path in _iter_tree_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            out[rel] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            out[rel] = None
    return out


def _read_redirect_rows(new_root: Path) -> list[dict[str, str]]:
    path = new_root / "docs" / "REDIRECTS.csv"
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def migration_diff_violations(old_root: Path, new_root: Path) -> list[str]:
    """Every hunk `migrate`'s own output at `new_root` (compared against the pre-migration
    snapshot at `old_root`) does not fit Ruling 68's six-class closed enumeration — empty
    means DP-3's executable form of NT-0019 §7 (g) holds.

    1. a front-matter block added (+ the legacy header it replaces removed) — and
    2. a reference token substituted — are one combined predicate here, because in this
       migration they are never separated: every stamped file also has its own citations
       rewritten in the same pass. `frozen_file_matches_after_migration_stamp` (loaded from
       `scripts/audit-docs.py`, Ruling 68 §3 — never reimplemented here) is that combined
       predicate, applied to *every* single-source file this diff finds, not only a
       DP-7-frozen family's: its own body-equality-after-stripping-and-inversion check is
       exactly as correct a predicate for a non-frozen single-file transform, and a second,
       parallel definition is exactly the drift Ruling 67 §2 warns against.
    3. a file moved with no content change beyond 1+2 — folded into the same predicate:
       an old/new path difference is not itself inspected, only content.
    4. a split — the concatenation of every target's stripped-and-inverted body
       reproduces the source's own body, in order.
    5. the roadmap (and `open-questions.md`, the same kind of living, un-numbered
       container) — unconditionally permitted; excluded from comparison entirely.
    6. a generated artifact (`INDEX.md`, `REDIRECTS.csv`) — unconditionally permitted;
       excluded from comparison entirely.

    A hunk fitting none of these — an old file vanished with no `REDIRECTS.csv` row
    naming where it went, a new file appeared with no row naming where it came from, a
    split target missing, or content that survives stripping-and-inversion changed
    anyway — is a violation, named with the file(s) involved.
    """
    audit_docs = _load_audit_docs()
    rows = _read_redirect_rows(new_root)
    redirects_inverse = {
        row["new_id"]: row["old_id"] for row in rows if row.get("old_id") and row.get("new_id")
    }
    moves: dict[str, list[str]] = {}
    for row in rows:
        old_path, new_path = row.get("old_path") or "", row.get("new_path") or ""
        if old_path and new_path and old_path != new_path:
            existing = moves.setdefault(old_path, [])
            if new_path not in existing:  # a register-row-style rewrite cites its one
                existing.append(new_path)  # target file once per row; not a split

    # Ruling 68 class 1's *combined* allowance for the two families whose legacy header is
    # itself removed (ADR's bullet block, a note's prose table) — re-derived from
    # `old_root` by the same discovery functions `migrate` itself uses, never from
    # `migrate`'s own runtime bookkeeping, so this stays an independent check of what
    # discovery *should* produce against what the written file actually contains.
    header_converted_bodies: dict[str, str] = {
        d.was: d.body
        for d in (*_discover_notes(old_root), *_discover_adrs(old_root))
        if d.was is not None
    }

    old_files = _read_tree_text(old_root)
    new_files = _read_tree_text(new_root)
    violations: list[str] = []
    consumed_new: set[str] = set()

    def _lines_no_blank(text: str) -> list[str]:
        return [ln for ln in text.splitlines() if ln.strip()]

    for old_rel, old_text in old_files.items():
        if old_rel in _MIGRATION_DIFF_ROADMAP or old_rel in _MIGRATION_DIFF_GENERATED:
            continue
        if old_text is None:
            violations.append(f"{old_rel}: not UTF-8 text — this filter cannot classify it")
            continue
        compare_against = header_converted_bodies.get(old_rel, old_text)
        targets = moves.get(old_rel)
        if not targets:
            new_text = new_files.get(old_rel)
            if new_text is None:
                violations.append(
                    f"{old_rel}: vanished with no REDIRECTS.csv row accounting for it"
                )
                continue
            consumed_new.add(old_rel)
            if new_text == compare_against:
                continue
            if not audit_docs.frozen_file_matches_after_migration_stamp(
                compare_against, new_text, redirects_inverse
            ):
                violations.append(
                    f"{old_rel}: content changed beyond header stamp + token rewrite, "
                    "with no REDIRECTS.csv move recorded"
                )
            continue

        if len(targets) == 1:
            new_rel = targets[0]
            new_text = new_files.get(new_rel)
            if new_text is None:
                violations.append(
                    f"{old_rel} -> {new_rel}: REDIRECTS.csv names this target, but it "
                    "does not exist"
                )
                continue
            consumed_new.add(new_rel)
            if not audit_docs.frozen_file_matches_after_migration_stamp(
                compare_against, new_text, redirects_inverse
            ):
                violations.append(
                    f"{old_rel} -> {new_rel}: content changed beyond header stamp + "
                    "token rewrite"
                )
            continue

        # A genuine split: several *distinct* target files share one `old_path` row. The
        # concatenation of every target's own body (front matter stripped, tokens
        # inverted back), compared line-by-line ignoring blank-line-count (formatting,
        # not content — `migrate`'s own slicing normalises each piece's trailing blank
        # lines to one `\n`, which a byte-exact join cannot generally undo without
        # reproducing that same normalisation a second time), must reproduce
        # `old_text`'s own non-blank lines in order (Ruling 68 class 4).
        pieces: list[str] = []
        ok = True
        for new_rel in targets:
            new_text = new_files.get(new_rel)
            if new_text is None:
                violations.append(f"{old_rel}: split target {new_rel} does not exist")
                ok = False
                continue
            consumed_new.add(new_rel)
            stripped = _strip_front_matter(new_text)
            for new_token in sorted(redirects_inverse, key=len, reverse=True):
                stripped = re.sub(
                    rf"\b{re.escape(new_token)}\b", redirects_inverse[new_token], stripped
                )
            pieces.append(stripped)
        if ok:
            joined_lines = [ln for piece in pieces for ln in _lines_no_blank(piece)]
            if joined_lines != _lines_no_blank(old_text):
                violations.append(
                    f"{old_rel}: split targets {targets} do not reproduce this file's "
                    "body lines in order"
                )

    for new_rel, _new_text in new_files.items():
        if new_rel in consumed_new:
            continue
        if new_rel in _MIGRATION_DIFF_ROADMAP or new_rel in _MIGRATION_DIFF_GENERATED:
            continue
        if new_rel in old_files:
            continue  # untouched, same path — already handled by the old_files loop above
        violations.append(
            f"{new_rel}: appeared with no REDIRECTS.csv row naming where it came from"
        )

    return violations


# ---------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------


def _report_skipped(command: str, skipped: Sequence[tuple[Path, str]]) -> None:
    """Print the skip count unconditionally — including zero — so "nothing was skipped"
    is a printed, falsifiable claim rather than the absence of a line. Raised in review of
    PR #567: `tests/test_audit_docs_scan_roots.py` exists because a vanished scan root
    used to make checks quietly stop running while the gate printed "All checks passed";
    the fix there, and here, is that a scan reports what it covered, not just what it found.
    """
    print(
        f"doc-id.py {command}: {len(skipped)} file(s) skipped "
        "(front matter present but did not parse as NT-0019's header):",
        file=sys.stderr,
    )
    for _path, reason in skipped:
        # `reason` is a `HeaderError` message, which already leads with `{path}:{line}:`
        # (`_docid.py`'s own convention) — printing `path` again here would repeat it.
        print(f"  {reason}", file=sys.stderr)


def _cmd_next(args: argparse.Namespace) -> int:
    try:
        result = compute_next_at_ref(args.ref, repo_root=args.repo_root)
    except GitArchiveError as exc:
        print(f"doc-id.py next: {exc}", file=sys.stderr)
        return 1
    _report_skipped("next", result.skipped)
    print(result.number)
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    if args.classify:
        counts = classify_docs_files(args.repo_root)
        width = max((len(family) for family in counts), default=len("total"))
        for family in sorted(counts):
            print(f"{family:<{width}}  {counts[family]}")
        print(f"{'total':<{width}}  {sum(counts.values())}")
        return 0

    failures = check(args.repo_root)
    for failure in failures:
        print(f"doc-id.py check: [{failure.kind}] {failure.message}", file=sys.stderr)
    _report_skipped("check", scan_governed_headers(args.repo_root).skipped)
    return 1 if failures else 0


def _cmd_widen(args: argparse.Namespace) -> int:
    result = widen(args.repo_root, to=args.to)
    for old_rel, new_rel in result.renamed:
        print(f"renamed {old_rel} -> {new_rel}")
    for warning in result.warnings:
        print(f"doc-id.py widen: warning: {warning}", file=sys.stderr)
    return 0


def _cmd_migrate(args: argparse.Namespace) -> int:
    result = migrate(args.repo_root)
    for path in result.files_written:
        print(f"wrote {path}")
    for path in result.files_deleted:
        print(f"deleted {path}")
    for path in result.skipped_vendored:
        print(f"skipped (vendored) {path}")
    for warning in result.warnings:
        print(f"doc-id.py migrate: warning: {warning}", file=sys.stderr)
    print(f"doc-id.py migrate: {len(result.assigned)} id(s) assigned")
    return 0


def _add_repo_root_argument(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to operate against (default: this repository).",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    next_parser = subparsers.add_parser(
        "next", help="Print the next free id number (max across every source, plus one)."
    )
    next_parser.add_argument(
        "--ref", default="origin/main", help="Git ref to read (default: origin/main)."
    )
    _add_repo_root_argument(next_parser)
    next_parser.set_defaults(func=_cmd_next)

    check_parser = subparsers.add_parser(
        "check", help="Check duplicate numbers, header/filename agreement, and contiguity."
    )
    check_parser.add_argument(
        "--classify",
        action="store_true",
        help="Print a per-family file count instead of checking.",
    )
    _add_repo_root_argument(check_parser)
    check_parser.set_defaults(func=_cmd_check)

    widen_parser = subparsers.add_parser(
        "widen", help="Widen the padded-id filename width."
    )
    widen_parser.add_argument("--to", type=int, required=True, help="The new width.")
    _add_repo_root_argument(widen_parser)
    widen_parser.set_defaults(func=_cmd_widen)

    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Run NT-0019 §4's migration (assign, split, restructure, move, stamp, "
        "rewrite citations, regenerate) against --repo-root.",
    )
    _add_repo_root_argument(migrate_parser)
    migrate_parser.set_defaults(func=_cmd_migrate)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
