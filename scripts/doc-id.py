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
from collections.abc import Callable, Collection, Iterable, Iterator, Mapping, Sequence
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
    `_docid.is_vendored` tests membership in `_docid._VENDORED_SKILLS`, Ruling 69's
    declared constant) *before* attempting to parse either, so neither counts as a "skip":
    exclusion is not failure.

    A file whose front matter does not fit NT-0019 §1.5's closed grammar at all —
    `parse_header` raising `HeaderError` — is not fatal to the scan, but is recorded in
    `.skipped`, never silently dropped: a first-party file under `.claude/` carrying
    foreign front matter (a nested mapping, an unknown key — the shape a vendored skill's
    own upstream front matter takes, but outside `_VENDORED_SKILLS` so `is_vendored` does
    not exempt it) lands here rather than being silently absorbed as a skip that reads the
    same as "nothing to find". Whether a *governed* file's header is malformed enough to
    fail the gate is check 30's question (W37-4), not this scan's — this scan's job is
    finding every live id while making what it could not resolve legible to a reader of
    the CLI's output, since the scan itself cannot tell "malformed governed header" from
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


def _load_register_lint(repo_root: Path = REPO_ROOT) -> types.ModuleType:
    """`scripts/register-lint.py`, loaded by path, for `parse_register` — the register's
    own declared row grammar (its module docstring: the header row found by *position*,
    the `|`-led line immediately before the separator, never by column-name text; a data
    row splits on unescaped `|` into exactly 5 fields; every `|`-led line accounted for,
    `assert classified == seen`). W37-6 outstanding obligations row 34: this technique
    already exists for the register and "was never applied to migrate's discovery
    functions ... reuse it rather than inventing a second form" — so `_discover_register`
    below imports it exactly as `_load_doc_index`/`_load_audit_docs` import their own
    sibling scripts, rather than a second, driftable copy of the header-position and
    5-field rules. Always loaded from *this* repository's own `scripts/`, never from a
    `--repo-root` fixture target, for the identical reason `_load_doc_index` gives.
    """
    return _load_module("_register_lint_for_migrate", repo_root / "scripts" / "register-lint.py")


# ---------------------------------------------------------------------------------------
# Templates: the single source for what a stamped header contains, per family — read from
# *this* repository's `docs/_templates/`, never the migration target's (Ruling 70's
# reasoning applied a second place: "the permitted set for a family is the set of keys in
# that family's template front matter").
# ---------------------------------------------------------------------------------------

_MIGRATE_TEMPLATE_FILENAME: Final[Mapping[str, str]] = {
    "ADR": "ADR.md", "RFC": "RFC.md", "PL": "PL.md", "RL": "RL.md", "CR": "CR.md",
    "REFERENCE": "REFERENCE.md", "LG": "LG.md",
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
    phase: str | None = None,
    work: str | None = None,
) -> str:
    """Render one document family's front-matter block by substituting the template's own
    placeholder tokens — never a hand-built YAML string, so a field this family's template
    does not declare can never silently appear here (the same guarantee Ruling 70 states
    for check 30's read of the same files, now applied to the writer as well as the
    checker). `number=None` is the Reference family (`prefix="REFERENCE"`): no prefix, no
    number, no `id:` line at all (§1.2), so the template simply carries none to substitute.

    `phase`/`work` are optional (default `None`, dropped exactly as before Ruling 84 —
    every caller but `_write_document_drafts`'s `LG-` path leaves them unset) — Ruling 84
    §3: an `LG-` record carries `work:` resolved to W5's post-migration `WK-` id and,
    derived from that same resolution, `phase:`; no other family populates either yet, for
    the same "no data source" reason the module docstring above already gives.
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
        elif key == "phase":
            if phase is None:
                continue
            line = re.sub(r"phase:\s*\S+", f"phase: {phase}", line)
        elif key == "work":
            if work is None:
                continue
            line = re.sub(r"work:\s*\S+", f"work: {work}", line)
        elif key in ("slice", "deliverable", "lands_in", "trigger"):
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
    # Ruling 94's substituted Ruling 84 §4 item 2, and item 3 alongside it: what the
    # ledger-axis check *looked at*, carried out so `_cmd_migrate` can print it whether or
    # not it found anything. A passing zero that says which zero it counted, never the
    # absence of a line — the same reason `_report_skipped` prints its own zero.
    ledger_records_checked: int = 0
    ledger_slice_values_checked: int = 0
    ledger_work_values_checked: int = 0


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

#: NT-0019 §1.6's own default for a ruling: "ruling (RL) — decision-maker; the maintainer
#: may author one on scope or process." The row already contemplates a ruling authored by
#: someone other than the decision-maker — naming the highest such case — and leaves the
#: owner unchanged: the column is "Owner — creates & amends", not "author" (Ruling 88 §2).
#: Ruling 86 §3 item 2 read the row the other way and made this default depart to the
#: drafting role for a dated, bounded delegation (`docs/plans/2026-08-30-nt-0012-0013-0014-
#: adoption.md` §1.1, the one match in the corpus, PR #603). Ruling 95 (`docs/plans/2026-09-
#: 02-w37-gap-1-ruling-86-owner-ruling.md`) struck that clause as a self-correction against
#: Ruling 88's own later, more general reading of the identical column applied to this same
#: row: an exception *author* is not an exception *owner*. Every `RL-` takes this constant
#: now, with no per-document exception — authorship is preserved where Ruling 88 already put
#: it, in the record's own body and in `was:`, never in `owner:`.
_RULING_DEFAULT_OWNER: Final = "decision-maker"


def _ruling_file_owner(path: Path, text: str) -> str:
    """A split ruling's owner — always `_RULING_DEFAULT_OWNER` (Ruling 95). `path` and
    `text` are accepted but no longer inspected, kept only so the call site below and the
    real-corpus regression tests documenting this correction need no restructuring.

    Until Ruling 95, this derived a departure from a "The delegation — ... delegated to the
    <role>" heading via a pair of regexes (Ruling 86 §3 item 2, PR #603) — removed along
    with this function's body rather than left as a dead branch (Ruling 95 §3 item 3: a
    branch that once encoded a reversed ruling is worse than no branch). Struck because
    NT-0019 §1.6's `RL` row was already answering the question the departure re-opened, and
    answering it the other way; see the constant's own comment above for the citations.
    """
    return _RULING_DEFAULT_OWNER

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


#: NT-0019 §1.6's own "Owner — creates & amends" column for the `PL` family, split by
#: `kind:` — "plan (PL map/leaf) — planner, via writing-plans"; "plan (PL review) —
#: auditor"; "plan (PL handover) — executor". `doc-index.py`'s `_OWNERSHIP_TABLE` already
#: transcribes the same column once, licensed by NT-0019 §1.6 rather than derived from a
#: file (that module's own comment: "Not byte-identical prose ... kept close enough that
#: every role name appearing in the note's own column also appears here"); this is the same
#: transcription, narrowed to the one family this function writes, kept local rather than
#: reached across a dynamic `importlib` load for four rows that change only when §1.6 does.
#: Ruling 86: hardcoding a single owner ("planner") for every kind was the same false-
#: attribution defect as `_discover_multi_ruling_files`'s "decision-maker" hardcode, in the
#: opposite direction — a plan review is the auditor's and a handover the executor's, not
#: the planner's, and `_plan_kind_for_slug` already computes which is which.
_PLAN_KIND_OWNER: Final[Mapping[str, str]] = {
    "map": "planner", "leaf": "planner", "review": "auditor", "handover": "executor",
}


def _plan_title(text: str) -> str | None:
    """The file's own `# Title` line, joined with every following non-blank line up to the
    next blank line or heading — never just the first physical line. A title that reads as
    one continuous sentence in the source can be hard-wrapped across two (or more) physical
    lines with no other marker (`docs/plans/2026-09-01-ruling-60-census-provenance-
    checkout-depth.md` and two siblings, found migrating them as `PL-`: the same wrapped-
    heading defect class already fixed in `FD.md`/`REFERENCE.md`/`RFC.md`/`WK.md`'s
    templates, here in a real document rather than a template). Verified against every
    plan-shaped file in the real corpus: joining changes the extracted title for exactly
    those three files and nothing else, each into one coherent sentence.
    """
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        heading_match = re.match(r"^#\s+(.+)$", line)
        if heading_match is None:
            continue
        parts = [heading_match.group(1).rstrip()]
        for cont in lines[idx + 1 :]:
            if not cont.strip() or cont.lstrip().startswith("#"):
                break
            parts.append(cont.strip())
        return " ".join(parts)
    return None


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
        owner = _ruling_file_owner(path, text)
        for i, heading in enumerate(headings):
            number_word, title = heading.group(1), (heading.group(2) or "").strip()
            start = heading.start() if i > 0 else 0  # preamble folds into the first ruling
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            section_text = text[start:end].rstrip("\n") + "\n"
            drafts.append(
                _Draft(
                    materialize="document", prefix="RL", kind=None,
                    title=title or f"Ruling {number_word}",
                    status="active", created=created, owner=owner,
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
    r"^###\s+(.+?),?\s*(?:accepted\s+)?(\d{4}-\d{2}-\d{2})(.*)$", re.MULTILINE
)
# Task #35 (plan-reviews line): widened the identical way #585 widened
# `_CLOSURE_HEADING_RE` -- a heading no longer has to END with its date. The real
# `docs/audit/plan-reviews.md`'s "Plan review 9" heading carries decoration after its
# date (`... 2026-08-30 — **FILED, with its drafting history intact**`); the old
# `\s*$` anchor required nothing-but-whitespace after the date, so that heading matched
# nothing and its body folded into whichever matched heading preceded it. The trailing
# group is captured (group 3) only for symmetry with `_CLOSURE_HEADING_RE` and is not
# read by `_discover_headed_split_file` below, which still only uses groups 1-2 --
# plan-reviews has no closure-style "not closed"/bespoke-audit classification need.
_REVIEW_HEADING_RE: Final = re.compile(r"^###\s+(.+?),\s*(\d{4}-\d{2}-\d{2})(.*)$", re.MULTILINE)

# Task #31: two `closure-records.md` headings are a bespoke audit, never a plan or a
# closure -- CLAUDE.md §5.4's bespoke-audit rule, its worked precedent
# (`docs/audit/phases/1b/w11-process-conformance-audit.md`), and Ruling 77 (#579). Matched
# by a distinctive title prefix, not the full reconstructed heading text (the exact
# whitespace/punctuation the regex captures around the date is a capture-group detail, not
# a stable string worth hardcoding) and not by position, so a future reordering of the
# file does not silently misfile a different row onto this disposition.
_CLOSURE_AUDIT_TITLE_PREFIXES: Final = (
    "Independent audit",
    "W4 mid-workstream scope findings",
)


#: A "not closed" record's own heading names the workstream it is one slice of — `"W5 —
#: the GLM spine, ..."` — derived per record rather than assumed, so a future workstream's
#: own not-yet-closed records resolve to *their* work, not a hardcoded `"W5"` (Ruling 84 is
#: about the ten real `W5 —` records; the mechanism it obliges is general).
_CLOSURE_WORK_TOKEN_RE: Final = re.compile(r"^(W\d+[a-z]?)\s+—")

#: Ruling 84 §2: "each of the ten is read for its own outcome rather than blanket-stamped
#: ... any that records a slice that did not complete takes retired". Read from the
#: heading's own trailer — the same structured annotation `"not closed"` itself comes
#: from — never the record's free-form body: a closure record's prose uses "superseded"/
#: "reverted"/"retired" constantly for individual requirements and decisions inside an
#: otherwise-successful slice (verified against the real ten: none of these words appears
#: in a body in a way that means the *slice* failed), so keying off the body would
#: false-positive on ordinary engineering narrative. A trailer that also names one of
#: these markers is the deliberate, structured way a future record states that *this*
#: slice itself did not complete.
_LEDGER_RETIRED_MARKERS: Final = ("retired", "abandoned", "withdrawn")


def _ledger_disposition(trailer: str) -> str:
    lowered = trailer.lower()
    if any(marker in lowered for marker in _LEDGER_RETIRED_MARKERS):
        return "retired"
    return "closed"


def _discover_closure_records(root: Path) -> list[_Draft]:
    """`docs/audit/closure-records.md`: one `###` heading per record. Unlike
    `_discover_plan_reviews` below, this does not delegate to `_discover_headed_split_file`
    -- task #31 found the real file's headings carry real, record-level semantic
    variation `_discover_headed_split_file`'s one-shape-fits-all output cannot express:

    - Most headings end with their closing date and become a plain `CR-`, `kind: work`
      record (`_discover_headed_split_file`'s original behaviour, unchanged here).
    - The file's own first heading is a *phase* close, not a workstream's -- `kind:
      phase` rather than the workstream default.
    - Two headings (`_CLOSURE_AUDIT_TITLE_PREFIXES`) are a bespoke audit record: `RS-`,
      `kind: audit`, `status: closed` rather than `CR-`/`work`/`active`.
    - A heading carrying an "in progress, not closed" qualifier after its date is a
      per-slice delivery record, not a closure — Ruling 84
      (`docs/plans/2026-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md`):
      `family: ledger`, `work:` resolved to the workstream's post-migration `WK-` id (by
      `_write_document_drafts`, once `roadmap_drafts` names it — until then `work:` is
      simply omitted, the same as any other unresolved optional field) and no `slice:`.
      This used to raise `NotImplementedError` and stop migrate on the first of the ten;
      Ruling 84 §1(b) is explicit that the raise was correct *while the family was
      undecided* and is wrong now that it is decided.
    """
    path = root / "docs" / "audit" / "closure-records.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    headings = list(_CLOSURE_HEADING_RE.finditer(text))
    drafts: list[_Draft] = []
    for i, heading in enumerate(headings):
        title, date_str, trailer = heading.group(1).strip(), heading.group(2), heading.group(3)
        start = heading.start() if i > 0 else 0  # preamble folds into the first record
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        section_text = text[start:end].rstrip("\n") + "\n"
        work_token: str | None = None
        if "not closed" in trailer.lower():
            prefix, kind, owner = "LG", None, "executor"
            status = _ledger_disposition(trailer)
            work_match = _CLOSURE_WORK_TOKEN_RE.match(title)
            work_token = work_match.group(1) if work_match else None
        elif title.startswith(_CLOSURE_AUDIT_TITLE_PREFIXES):
            prefix, kind, status, owner = "RS", "audit", "closed", "auditor"
        elif title.startswith("Phase "):
            prefix, kind, status, owner = "CR", "phase", "active", "auditor"
        else:
            prefix, kind, status, owner = "CR", "work", "active", "auditor"
        drafts.append(
            _Draft(
                materialize="document", prefix=prefix, kind=kind, title=title, status=status,
                created=date.fromisoformat(date_str), owner=owner,
                tie_break=("docs/audit/closure-records.md", i), old_token=None,
                was="docs/audit/closure-records.md", body=section_text,
                work_token=work_token,
            )
        )
    return drafts


def _discover_plan_reviews(root: Path) -> list[_Draft]:
    """`docs/audit/plan-reviews.md`, via the shared `_discover_headed_split_file` --
    unlike `_discover_closure_records` above, this file's headings carry no per-record
    semantic variation that splitter cannot express (no phase/audit distinction, nothing
    left mid-flight), so it still delegates rather than growing its own loop.

    Ruling 82: three of the file's `###` headings carry no date at all ("Candidate A",
    "Candidate B", "Also carried, and not a new rule") and so never match
    `_REVIEW_HEADING_RE` regardless of the trailing-anchor fix below -- they are ruled
    sub-content of a `##` container, not independent records, but the container's own
    positive family and `kind:` is a separate, still open, planner derivation (Ruling
    82 §3 item 3). Left unclassified, they fold into whichever matched heading precedes
    them in the file (sections run heading-to-heading), the same way an unmatched
    heading always has -- `_discover_headed_split_file` itself has no accounting step
    that would notice a heading count short of the file's own `###` total, unlike
    `_discover_closure_records`'s bespoke loop. That is no longer silent at the
    `migrate` level, though: `_check_plan_reviews_heading_census` below independently
    re-scans this same file and refuses rather than let the fold complete unremarked
    (Ruling 83, row 1 of the W37-5b obligations list).
    """
    drafts = _discover_headed_split_file(
        root, "docs/audit/plan-reviews.md", _REVIEW_HEADING_RE, "CR", "lead"
    )
    for d in drafts:
        d.kind = "review"
    return drafts


_ANY_HEADING_RE: Final = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.MULTILINE)

_PLAN_REVIEWS_SPLIT_LEVEL: Final = 3  # `_REVIEW_HEADING_RE` records are `###` headings


def _check_plan_reviews_heading_census(root: Path) -> None:
    """Ruling 83 (row 1, `docs/plans/2026-09-02-w37-6-outstanding-obligations.md`): a
    guard may not derive its denominator from the same matcher it is checking --
    `_check_legacy_file_not_silently_unrecognised`'s `if drafts: return` cannot tell
    "found every review" from "found ten of eleven", since both give it a non-empty
    list (measured: `_discover_plan_reviews` returns ten drafts for eleven real
    reviews, and the guard is satisfied). This re-scans `plan-reviews.md` independently
    of `_REVIEW_HEADING_RE`'s own match count, at every heading level (`^#{1,6}`), and
    classifies each heading into exactly one of Ruling 83's three buckets:

    1. **a record** -- matched by `_REVIEW_HEADING_RE` (already widened above for
       Plan review 9's trailing text);
    2. **derived body**, computed rather than listed -- the file's own first heading
       (folds into the preamble, the same convention `_discover_headed_split_file`
       already applies to every legacy split file) or any heading deeper than
       `_PLAN_REVIEWS_SPLIT_LEVEL` (`####`+ -- real content today, nested inside
       several individual reviews' own "Sources"/"Proposals, consolidated" subsections);
    3. **a declared exception** -- none implemented for this file yet. Ruling 82 found
       the three undated headings ("Candidate A", "Candidate B", "Also carried, and not
       a new rule") and their `##` parent ("Pending proposals") sub-content, not
       records. Ruling 88 has since ruled the container's family (`RFC-`,
       `kind: process`, `status: closed`, `owner:` the maintainer) -- but a ruling is a
       decision, not a code change: nothing in this module yet builds an `RFC-` draft
       for it (that is separate follow-up work, not this function's), so it still has
       no bucket-3 entry here and this function still has no authority to invent one.

    Anything left over is named, by line number and heading text -- never a bare count
    (Ruling 83 §3 item 4) -- and `migrate` refuses. That is today's correct outcome for
    this file, not a defect in this function: the leftover headings are exactly Ruling
    82/88's `##` container and its three children, ruled but not yet implemented.

    Additive alongside the existing `_check_legacy_file_not_silently_unrecognised` call
    for this same file, not a replacement of it (Ruling 83 §1(f)): that guard still
    catches true zero-discovery (a census over zero headings has nothing to name), this
    one catches an undercount even when discovery's own output is non-empty. Neither
    alone is sufficient.
    """
    path = root / "docs" / "audit" / "plan-reviews.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    record_starts = {m.start() for m in _REVIEW_HEADING_RE.finditer(text)}
    headings = list(_ANY_HEADING_RE.finditer(text))
    unaccounted = [
        (text.count("\n", 0, m.start()) + 1, m.group(0).strip())
        for idx, m in enumerate(headings)
        if m.start() not in record_starts
        and idx != 0  # the file's own title -- derived body, folds into the preamble
        and len(m.group(1)) <= _PLAN_REVIEWS_SPLIT_LEVEL  # deeper is derived body too
    ]
    if unaccounted:
        named = "; ".join(f"line {n} ({h!r})" for n, h in unaccounted)
        raise NotImplementedError(
            f"migrate: {path} carries heading(s) the census cannot classify as a "
            f"record or as derived body: {named}. Ruling 88 ruled their disposition "
            f"(RFC-, kind: process) but this module has no code yet that builds that "
            f"draft -- implement that discovery before migrating this file."
        )


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
        title = _plan_title(text) or slug
        drafts.append(
            _Draft(
                materialize="document", prefix="PL", kind=kind, title=title,
                status="active", created=created, owner=_PLAN_KIND_OWNER[kind],
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



# ---------------------------------------------------------------------------------------
# Task #32 (W37-6 outstanding obligations row 2), what the transform produces ruled at
# Rulings 90-92 (`docs/plans/2026-09-02-w37-roadmap-transform-rulings.md`): the shape
# below (`##`/`###` `Phase <id> — <title>` heading, `### <work-key> — <title>` + a
# `status:` line, `- **<slice-key>**` bullets) was this module's own guess at "the legacy
# roadmap shape". Ruling 79/80's Correction section proved it wrong by running the three
# patterns against the real `docs/roadmap.md`: all three matched zero times,
# `_restructure_roadmap` was therefore never reached, and `migrate` reported success on a
# roadmap it never touched.
#
# The real shape, verified directly against `docs/roadmap.md`: a Work is a markdown table
# row whose leading cell is `**W<n>[<letter>]**` — wrapped in `~~...~~` with a trailing
# `✔` once closed, undecorated otherwise, with **neither form reliable as a status
# oracle** (Ruling 83 §1(g): `W5` is undecorated with its own Status cell reading
# "closed"; `W7` is struck three rows below it in the same table; Ruling 90: "`status:`
# comes from the Status cell, never from the decoration") — gathered under a
# `## <n>. Phase <label> — <title>` or `### Phase <label> — <title>` heading. Several
# such tables exist per phase, so a work id can head more than one leading row (56
# leading rows, 41 distinct ids, measured at `59bba94`) — **Ruling 91: these merge into
# one `WK-` row, they do not become several.** No slice ever exists as a row or a bullet,
# in any shape, anywhere in the corpus (Ruling 80's Correction section), so this rewrite
# discovers work rows only.
#
# **All 41 ids convert (Rulings 90-92) — nothing is withheld.** A closed work converts
# with `status: closed` (Ruling 90); a multi-row work's rows merge into one, its body
# carrying every source row's own text labelled by the table it came from (Ruling 91);
# `W6` — whose only row sits under `### Workstreams`, a *sibling* of the self-described
# archival heading `### Original scope, for reference`, not a child of it (Ruling 92
# corrected this rewrite's own first premise on that point) — converts with
# `status: retired`, its body naming `W6a`/`W6b` as the works its scope was re-cut into.
# The one thing `migrate` still refuses on is Ruling 91 obligation 1: if a work's several
# rows disagree on status, that is a data defect in the roadmap and a human's to resolve,
# never a silent pick of the first, the last, or the richest cell.
# ---------------------------------------------------------------------------------------

_ROADMAP_WORK_ROW_RE: Final = re.compile(
    r"^\|\s*(~~)?\*\*(W\d+[a-z]?)\*\*(~~)?\s*(?:✔)?\s*\|(.*)$"
)
_ROADMAP_PHASE_LABEL_RE: Final = re.compile(r"^#{2,4}\s+(?:\d+\.\s+)?Phase\s+(\S+)\b")
_ROADMAP_PHASE_TITLE_RE: Final = re.compile(
    r"^#{2,4}\s+(?:\d+\.\s+)?Phase\s+(\S+)\s+—\s+(.+?)\s*$", re.MULTILINE
)
_ROADMAP_ANY_HEADING_RE: Final = re.compile(r"^(#+)\s+(.+?)\s*$")

# Ruling 90: the status word lives in the row's own prose, never in the `~~...~~`/`✔`
# decoration. §1.2's `WK` subset is `draft → active → closed | retired`; a row's remaining
# cells are searched for one of the four case-insensitively, and separately for a nearby
# `YYYY-MM-DD` date, because the real cells are free prose ("✔ **closed 2026-08-14**",
# "**Closed 2026-08-22** — 110 built ...") rather than a fixed field.
#
# Anchored on a *bolded* occurrence of the word (`\*\*\s*` immediately before it), not a
# bare one — found live, at `W7`'s third row (line 337, "the original scope" table):
# "The data half closed early as W7a" contains the bare word "closed" describing a
# *different* work's history in passing prose, not this row's own status. Every genuine
# status declaration in the real corpus is bolded (`**Closed ...**`, `✔ **closed ...**`);
# no bare, unbolded occurrence of any of the four words is a real declaration anywhere in
# `docs/roadmap.md` today, verified by running this pattern and its bare-word predecessor
# side by side over the whole file.
_ROADMAP_STATUS_WORD_RE: Final = re.compile(
    r"\*\*\s*(closed|active|draft|retired)\b", re.IGNORECASE
)
_ROADMAP_STATUS_DATE_RE: Final = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

# Ruling 92: `W6`'s scope was re-cut into `W6a` and `W6b`, both closed, both with their
# own rows; `W6` itself never completed *under that name*, so `closed` ("completed its
# purpose") is false of it and `retired` ("ended without completing ... the reason is in
# the body") is the available word — `superseded` is exact and not in the `WK` subset
# (surfaced for the maintainer's `RFC-` route in the ruling, not fixed here). A named,
# declared exception (Ruling 83's bucket 3 shape: "acceptable only for what cannot be
# derived, and only with a reason per entry") rather than a general rule, because the
# derivation is specific to this one id — a dependency reference in another row (`W7`'s
# `Depends on` cell names `W6`), not anything mechanically visible in `W6`'s own row.
_ROADMAP_RETIRED_WORK_IDS: Final[Mapping[str, str]] = {
    "W6": (
        "Retired rather than closed (Ruling 92): this work's own row carries no closed "
        "signal, and its scope was re-cut into WK-successors before it completed under "
        "this name — see the successors named below."
    ),
}
# Which id(s) each retired id's scope was re-cut into, for the body note above — derived
# from the roadmap's own dependency reference (`W7`'s `Depends on` cell names `W4, W5,
# W6`) and prose ("The pre-split frontend work... re-cut into W6a and W6b"), not
# mechanically derivable from `W6`'s own row.
_ROADMAP_RETIRED_SUCCESSORS: Final[Mapping[str, tuple[str, ...]]] = {"W6": ("W6a", "W6b")}

# Ruling 92 found that `docs/roadmap.md`'s heading nesting is unreliable — `### Original
# scope, for reference` (317) and its sibling `### Workstreams` (327, which actually
# carries `W6`'s row at 336) are both children of the single unnumbered `## Historical
# record` (269), and this rewrite's simple "last `Phase <label>` heading wins" tracker
# has no way to tell that the whole span from 269 to the next `##` is pre-split content
# describing what *became* phase 1a and 1b, not phase-1b content itself. Measured live:
# the tracker attributes every row in that span to "1b" (the last real phase heading
# before it, `### Phase 1b — Modelling Workbench` at 273) — right for `W7` (whose real,
# non-span occurrences are also 1b) and wrong for `W1`-`W4` (whose real occurrences are
# all 1a), producing a false "spans two phases" refusal for exactly the ids this heading
# span was never meant to relabel. A occurrence inside this span is marked uncertain
# rather than excluded — Ruling 92's point was that the *row still counts*, only its
# *phase attribution by proximity* does not — and the merge below prefers a work's
# non-uncertain occurrences when any exist, falling back to the uncertain one only when
# it is all a work has (`W6`'s own case).
_ROADMAP_HISTORICAL_RECORD_HEADING_RE: Final = re.compile(r"^##\s+Historical record\s*$")


@dataclass(frozen=True)
class _RoadmapRowOccurrence:
    """One real leading work-id row, exactly as `_ROADMAP_WORK_ROW_RE` found it — the
    unit `_discover_roadmap`'s census below classifies, never the id alone (an id heads
    anywhere from one to three of these on the real tree, Ruling 83 §1(g))."""

    work_id: str
    line_no: int  # 1-based, so a human can find it without re-running the regex
    struck: bool
    title: str  # the row's own second cell, trimmed — this occurrence's own title only
    rest: str  # every cell after the id, verbatim — Ruling 91's "every row's Notes"
    phase_label: str | None  # the nearest `Phase <label>` heading above it, or None
    section_heading: str | None  # nearest heading of any level, for labelling the body
    phase_uncertain: bool  # inside "## Historical record" — see the constant's comment


def _scan_roadmap_rows(text: str) -> list[_RoadmapRowOccurrence]:
    """Every real leading work-id row in `text`, in document order — the census
    `_discover_roadmap` needs before it can decide anything (Ruling 83): **the unit is the
    row**, found by a pattern that does not encode which rows the caller wants, not a
    per-id count that a duplicate would already have folded away.
    """
    occurrences: list[_RoadmapRowOccurrence] = []
    phase_label: str | None = None
    section_heading: str | None = None
    phase_uncertain = False
    historical_record_level = 0
    for i, line in enumerate(text.splitlines()):
        heading_match = _ROADMAP_ANY_HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            if phase_uncertain and level <= historical_record_level:
                phase_uncertain = False
            section_heading = heading_match.group(2)
            label_match = _ROADMAP_PHASE_LABEL_RE.match(line)
            if label_match:
                phase_label = label_match.group(1)
            if _ROADMAP_HISTORICAL_RECORD_HEADING_RE.match(line):
                phase_uncertain = True
                historical_record_level = level
        row_match = _ROADMAP_WORK_ROW_RE.match(line)
        if row_match is None:
            continue
        struck = bool(row_match.group(1) and row_match.group(3))
        rest = row_match.group(4).strip().strip("|").strip()
        title = row_match.group(4).split("|", 1)[0].strip()
        occurrences.append(
            _RoadmapRowOccurrence(
                work_id=row_match.group(2), line_no=i + 1, struck=struck,
                title=title, rest=rest, phase_label=phase_label,
                section_heading=section_heading, phase_uncertain=phase_uncertain,
            )
        )
    return occurrences


def _row_status_signal(rest: str) -> tuple[str, str | None] | None:
    """`(status word, date)` read from a row's own remaining cells, or `None` when the
    row states no explicit status at all (an open work's row typically does not, e.g.
    `W8`'s "Must complete before W9. If S1 fails, this phase is re-planned"). The word is
    lower-cased to the `WK` vocabulary's own spelling; the date is `None` when the row
    carries a status word but no nearby date (also real: `W6b`'s dependency column reads
    "OQ-PLAT-6 ✔" — a decided-question checkmark unrelated to this row's own status).
    """
    word_match = _ROADMAP_STATUS_WORD_RE.search(rest)
    if word_match is None:
        return None
    date_match = _ROADMAP_STATUS_DATE_RE.search(rest)
    return (word_match.group(1).lower(), date_match.group(1) if date_match else None)


def _work_id_sort_key(work_id: str) -> tuple[int, str]:
    m = re.match(r"W(\d+)([a-z]?)", work_id)
    assert m is not None
    return int(m.group(1)), m.group(2)


@dataclass
class _MergedWork:
    work_id: str
    phase_label: str | None
    title: str
    status: str
    body: str
    line_nos: list[int]  # every source occurrence's line, for the surgical rewrite


def _merge_roadmap_work(work_id: str, occurrences: list[_RoadmapRowOccurrence]) -> _MergedWork:
    """Ruling 91: one `WK-` row per work id, its several source rows merged rather than
    turned into several rows and none chosen over the others. Obligation 1 (status cells
    must agree, or refuse), obligation 2 (every source row's Notes survive the merge,
    labelled by the table each came from) and Ruling 92's `W6` exception all live here.
    """
    ordered = sorted(occurrences, key=lambda o: o.line_no)
    # A work's *certain* occurrences settle its phase whenever any exist -- the "## 6.
    # Historical record" span mislabels some ids by proximity alone (the constant's own
    # comment: `W1`-`W4`'s occurrence there is tagged "1b", the last real phase heading
    # before it, though their real occurrences are all "1a"). Falling back to the
    # uncertain occurrences only when a work has *no* certain one at all is `W6`'s exact
    # case: its single occurrence sits inside that span, and Ruling 92 does not name a
    # phase for it, so this rewrite reports the one fact the tracker actually has (the
    # nearest preceding real phase heading, "1b") rather than inventing a rule for it.
    certain = [o for o in ordered if not o.phase_uncertain]
    candidates = certain or ordered
    phase_labels = {o.phase_label for o in candidates}
    phase_label = next(iter(phase_labels)) if len(phase_labels) == 1 else None
    # A genuine cross-phase split among a work's *certain* occurrences is not something
    # Ruling 91's routing table anticipated a rule for ("if any work was executed across
    # two phases the rule needs a tie-break, and I did not measure whether one exists") --
    # measured here as absent among every work's certain occurrences on the real tree
    # today; `phase_label` is `None` above if it is ever not, and `_discover_roadmap`
    # refuses on it explicitly below rather than picking either phase silently.

    body_fragments = [
        f"From “{o.section_heading}” (line {o.line_no}): {o.rest}" for o in ordered
    ]

    if work_id in _ROADMAP_RETIRED_WORK_IDS:
        successors = ", ".join(_ROADMAP_RETIRED_SUCCESSORS[work_id])
        body_fragments.append(f"{_ROADMAP_RETIRED_WORK_IDS[work_id]} Successors: {successors}.")
        return _MergedWork(
            work_id=work_id, phase_label=phase_label, title=ordered[-1].title,
            status="retired", body="\n\n".join(body_fragments),
            line_nos=[o.line_no for o in ordered],
        )

    signals = [_row_status_signal(o.rest) for o in ordered]
    known_signals = {s for s in signals if s is not None}
    if len(known_signals) > 1:
        detail = "; ".join(
            f"line {o.line_no}: {s!r}" for o, s in zip(ordered, signals, strict=True)
        )
        raise NotImplementedError(
            f"migrate: {work_id}'s {len(ordered)} rows disagree on status (Ruling 91 "
            f"obligation 1) -- {detail}. migrate does not pick the first, the last, or "
            "the richest row; this is a data defect in docs/roadmap.md for a human to "
            "resolve, naming the work rather than a count."
        )
    if known_signals:
        status = next(iter(known_signals))[0]
    else:
        # No occurrence states an explicit status word at all (real: `W32`, single row,
        # struck, 6000+ characters of prose and none of the four words) -- Ruling 90's
        # "never the decoration" rule is about the cell overriding decoration when they
        # *disagree*; with no cell text to consult, decoration is the only fact left, so
        # it is used here rather than defaulting every silent row to "active" regardless
        # of what it looks like. Still checked for internal agreement, not trusted blind:
        # a work whose several undeclared rows are struck inconsistently is the same
        # species of data defect as a declared disagreement.
        struck_states = {o.struck for o in ordered}
        if len(struck_states) > 1:
            detail = "; ".join(f"line {o.line_no}: struck={o.struck}" for o in ordered)
            raise NotImplementedError(
                f"migrate: {work_id}'s {len(ordered)} rows state no status word at all "
                f"and disagree on strikethrough decoration -- {detail}. Neither the cells "
                "nor the decoration settle this work's status; migrate refuses rather "
                "than picking one."
            )
        status = "closed" if next(iter(struck_states)) else "active"
    # `ordered[-1]` (document order, so typically the most-recently-written table's own
    # phrasing) rather than the first -- an arbitrary but deterministic and *disclosed*
    # choice for the merged row's title; every occurrence's own title text still survives
    # verbatim inside `rest`, which is folded into the body fragment above.
    return _MergedWork(
        work_id=work_id, phase_label=phase_label, title=ordered[-1].title,
        status=status, body="\n\n".join(body_fragments), line_nos=[o.line_no for o in ordered],
    )


def _discover_roadmap(
    root: Path,
) -> tuple[list[_Draft], dict[str, str], list[_RoadmapRowOccurrence]]:
    """The real `docs/roadmap.md` shape (module note above, Rulings 90-92): every leading
    work-id row across the whole file, grouped by id and merged into one `_Draft` per id
    (Ruling 91) — never a per-id count a duplicate would already have folded away.

    Returns `(drafts, phase_titles, occurrences)`. `phase_titles` maps every phase label
    actually used by a draft to that phase's own title text (a `## <n>. Phase <label> —
    <title>` or `### Phase <label> — <title>` heading), because Ruling 91 puts each work
    "under the milestone of the phase the work was executed in" and the real corpus has
    several such milestones, not the one this function used to assume. `occurrences` is
    the full census (every real leading row, before merging) — `_restructure_roadmap`
    needs the original line numbers to remove exactly the rows that were merged away,
    never anything else in the document.

    The one thing this still refuses on: a work whose several rows disagree on status
    (Ruling 91 obligation 1), or a work whose occurrences span more than one phase
    section (measured absent on the real tree today; a genuine tie-break this function
    does not invent one for). Everything else converts.
    """
    roadmap_path = root / "docs" / "roadmap.md"
    if not roadmap_path.is_file():
        return [], {}, []
    text = roadmap_path.read_text(encoding="utf-8")
    occurrences = _scan_roadmap_rows(text)
    if not occurrences:
        return [], {}, []

    by_id: dict[str, list[_RoadmapRowOccurrence]] = {}
    for occ in occurrences:
        by_id.setdefault(occ.work_id, []).append(occ)

    merged = [_merge_roadmap_work(work_id, occs) for work_id, occs in by_id.items()]

    unresolved_phase = [m.work_id for m in merged if m.phase_label is None]
    if unresolved_phase:
        raise NotImplementedError(
            "migrate: work(s) "
            f"{', '.join(sorted(unresolved_phase, key=_work_id_sort_key))} have leading "
            "rows in more than one phase section, with no rule to pick which milestone "
            "the merged WK- row belongs under (Ruling 91's routing table left this "
            "unmeasured beyond today's real tree, where it does not occur) -- migrate "
            "refuses rather than choosing a phase silently."
        )

    phase_titles = {
        m.group(1): m.group(2) for m in _ROADMAP_PHASE_TITLE_RE.finditer(text)
    }
    created = _module_first_commit_date(roadmap_path, root)
    drafts: list[_Draft] = []
    for order, work in enumerate(sorted(merged, key=lambda m: _work_id_sort_key(m.work_id))):
        assert work.phase_label is not None  # narrowed by the check above
        drafts.append(
            _Draft(
                materialize="roadmap_row", prefix="WK", kind=None, title=work.title,
                status=work.status, created=created, owner="maintainer",
                tie_break=("docs/roadmap.md", order), old_token=work.work_id,
                phase=f"P{work.phase_label}", body=work.body,
            )
        )
    return drafts, phase_titles, occurrences


# ---------------------------------------------------------------------------------------
# Task #32's sibling defect (W37-6 outstanding obligations row 3): `\bF(\d+)\b` under
# `.fullmatch` demands the *whole* Finding-id cell be a bare `F<n>` — true of no real row.
# Every one of the register's 73 data rows is compound, `<description> (<id>)`, and the
# parenthesised id itself takes one of two forms verified against every real cell: a bare
# `F<n>` (`F6` .. `F76`), or a workstream-scoped id, `F-W<n>[<letter>]` followed by one or
# more `-<n>` groups (`F-W9-1` .. `F-W10-2-2`) — never the whole-cell form the old pattern
# required. Anchored on the trailing parenthesis (`\)\s*$`) rather than the whole cell, so
# a cell whose description text happens to contain an unrelated `F<n>`-shaped substring
# earlier on cannot be mistaken for the id.
# ---------------------------------------------------------------------------------------

_REGISTER_FINDING_RE: Final = re.compile(r"\((F(?:\d+|-W\d+[a-z]?(?:-\d+)+))\)\s*$")


def _discover_register(root: Path) -> list[_Draft]:
    """The register's declared row grammar (module note above; `scripts/register-lint.py`
    `parse_register`, reused rather than reimplemented — W37-6 outstanding obligations row
    34): a data row is a `|`-led line inside the one table, the header found by
    *position* (immediately before the `|---|...` separator, never by column-name text —
    the F64 defect `parse_register`'s own comment records), split on unescaped `|` into
    exactly 5 fields (Finding id, Concerns, Work item, Phase, Decision). Every candidate
    `|`-led line is accounted for by `parse_register` itself (`assert classified ==
    seen`), so a row missing its leading `|` or splitting into the wrong field count is
    loud there rather than silently absent here.

    Matched only at the legacy path (NT-0019 §5.2: "Finding-id cells → `FD-n` with
    `was:`") — a second run (moved to `docs/findings/register.md`) finds nothing there.
    """
    drafts: list[_Draft] = []
    path = root / "docs" / "audit" / "register.md"
    if not path.is_file():
        return drafts
    register_lint = _load_register_lint()
    rows, _problems = register_lint.parse_register(path)
    created = _module_first_commit_date(path, root)
    order = 0
    for row in rows:
        cell = row.fields[0]
        m = _REGISTER_FINDING_RE.search(cell)
        if m is None:
            continue
        token = m.group(1)
        title = cell[: m.start()].strip() or f"Finding {token}"
        drafts.append(
            _Draft(
                materialize="register_row", prefix="FD", kind=None, title=title,
                status="active", created=created, owner="auditor",
                tie_break=("docs/audit/register.md", order), old_token=token,
                source_path=path,
            )
        )
        order += 1
    return drafts


def _is_vendored_skill_manifest(path: Path) -> bool:
    """True only for the `SKILL.md` that *defines* a vendored skill's boundary — its
    parent directory is named in `_docid._VENDORED_SKILLS` — never a file beneath it.
    `_docid.is_vendored` cannot make this distinction by itself: called on
    `skill_dir/SKILL.md`, it is `True` for the manifest exactly as it is for anything
    beneath it (NT-0019 §1.5: the manifest is stamped, only the files *beneath* it are
    exempt).

    Ruling 69 (reassigned to this slice by Ruling 76): the criterion is membership in
    `_VENDORED_SKILLS`, the same declared constant `_docid.is_vendored` tests, not a
    `LICENSE`-file probe. The two functions' criteria could silently disagree otherwise:
    only 2 of the 28 real vendored skills carry a `LICENSE` (`planning-with-files`,
    `ui-ux-pro-max`), so an unfixed, still-LICENSE-based version of this function would
    read every one of the other 26 skills' own `SKILL.md` (`writing-plans` and
    `subagent-driven-development` among them) as *not* the manifest — making
    `_is_vendored_exempt` below treat each as exempt from the blanket citation-rewrite
    pass, when NT-0019 §1.5 requires every manifest to be stamped and rewritten like any
    other file.
    """
    return path.name == "SKILL.md" and path.parent.name in _docid._VENDORED_SKILLS


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
    "LG": "ledgers",
}


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "untitled"


def _write_document_drafts(
    root: Path, drafts: list[_Draft], roadmap_drafts: Sequence[_Draft] = ()
) -> tuple[list[str], list[str]]:
    """Every `materialize="document"` draft: stamp its header, write it under its family
    directory, and delete its `was` source once every draft sharing that source has been
    written. Returns `(files_written, files_deleted)`, both repo-relative posix paths.

    `roadmap_drafts` resolves a draft's `work_token` (Ruling 84 §2: an `LG-` record's
    `work:`) the same way `_restructure_roadmap` already resolves an `SL-` row's `work:` —
    by `old_token`, against drafts that already carry their assigned `.number` (Phase B's
    `_assign_numbers` runs over the combined draft list, `roadmap_drafts` included, before
    this function is called). `phase:` is derived from the same lookup — the resolved
    work's own `.phase` — rather than set directly on the `LG-` draft, since a closure
    record has no independent way to know its workstream's phase. Neither field is set
    when `work_token` does not resolve (the real corpus's `roadmap_drafts` is empty until a
    separate, unassigned defect — "`_discover_roadmap` converts 0 of 41 works" — is fixed;
    `work:`/`phase:` are simply omitted then, exactly as for any other unresolved optional
    field, never a raise).
    """
    written: list[str] = []
    was_sources: set[str] = set()
    roadmap_by_token = {
        d.old_token: d for d in roadmap_drafts if d.old_token is not None
    }
    for d in drafts:
        if d.materialize != "document":
            continue
        target_dir = root / "docs" / _DOCUMENT_FAMILY_DIR[d.prefix]
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{_docid.padded(d.prefix, d.number)}-{_slug(d.title)}.md"
        new_path = target_dir / filename
        d.new_path = new_path
        work_value: str | None = None
        phase_value = d.phase
        if d.work_token is not None:
            work_draft = roadmap_by_token.get(d.work_token)
            if work_draft is not None:
                work_value = _docid.canonical(work_draft.prefix, work_draft.number)
                if phase_value is None:
                    phase_value = work_draft.phase
        header = _stamp_header(
            d.prefix, d.number, kind=d.kind, title=d.title, status=d.status,
            created=d.created, owner=d.owner, was=d.was,
            phase=phase_value, work=work_value,
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


# Plain `key: value` lines directly beneath the heading, no fence and no blank line
# before the first field — `docs/_templates/PHASE.md`'s own form, matching NT-0019 §1.3's
# unfenced illustration and `document-ids.md` §1.3 byte-for-byte apart from heading depth.
# Ruling 80 (`docs/plans/2026-09-02-w37-template-parser-conflicts-rulings.md`) settled
# this the other way from how it was first built here: `scripts/doc-index.py`'s
# `scan_phase_sections` used to require a fence too, so the two agreed with each other
# while disagreeing with the standard, `PHASE.md` and `audit-docs.py` check 30's
# `_EXPECTED_NO_BLOCK_TEMPLATES` all at once. Both sides are fixed together in the same
# commit that fixes this constant.
_PHASE_TEMPLATE: Final = (
    "## {phase} — {title}\n"
    "status: active\n"
    "opened: {opened}\n"
    "target: ~\n"
    "gates: ~\n"
    "exit criteria: ~\n"
    "works: {works}\n"
)


# ---------------------------------------------------------------------------------------
# Ruling 83 -- the independent census. A `_discover_*` function's own denominator is its
# own matcher, so "found nothing" and "found everything" look identical to it (`#585`'s
# fix for `_discover_closure_records` is exhaustive over its OWN matches and still cannot
# see a match the matcher never made -- Ruling 83 §1(b)). Every guard below instead counts
# with a pattern that does not encode the splitter's own expectations, classifies each
# independently-found unit into exactly one of three buckets -- record, derived body, or a
# declared exception carrying a reason -- and refuses by NAMING the units left over, never
# by comparing two counts (a count can agree by coincidence; a named unit cannot).
# Generalises `_check_roadmap_not_silently_unrecognised`'s own principle (a post-migration
# marker, not the legacy matcher, decides "nothing to do") from a yes/no into an
# arithmetic that closes, and reuses `register-lint.py`'s `classified == seen` accounting
# discipline: walk every independently-found candidate exactly once, into exactly one
# bucket, so a bug in the reconciliation itself is a loud, immediate error rather than a
# silent skip.
# ---------------------------------------------------------------------------------------


@dataclass(frozen=True)
class _CensusUnit:
    """One candidate unit an independent, splitter-pattern-agnostic count found -- a
    heading line, a bold requirement marker, or a file. `key` is the identity a caller
    checks against a record set or an exception mapping; `locator` and `text` are what a
    refusal message prints, kept separate from `key` so the message never has to be parsed
    back into an identity.
    """

    key: str
    locator: str
    text: str
    level: int = 0  # heading level (1-6); 0 when the unit is not heading-shaped


def _reconcile_census(
    *,
    scope: str,
    units: Sequence[_CensusUnit],
    records: Collection[str],
    is_body: Callable[[_CensusUnit], bool] = lambda _unit: False,
    exceptions: Mapping[str, str] | None = None,
) -> None:
    """Ruling 83 §2: classify every independently-counted unit into record / derived body
    / declared exception, and refuse -- naming the unaccounted units, never a count (§3
    item 4) -- when any unit is none of the three. `exceptions` must carry a non-empty
    reason for every key present: an entry with a blank reason is refused outright rather
    than silently read as "still a valid exception" (§4's second mutation).
    """
    exceptions = exceptions or {}
    blank = sorted(key for key, reason in exceptions.items() if not reason.strip())
    if blank:
        raise ValueError(
            f"{scope}: declared exception(s) with no reason: {blank} -- a bucket-3 entry "
            "must carry a reason string (Ruling 83 §3 item 3); one with none is a defect "
            "in the fix, not a legitimate exception"
        )
    unaccounted = [
        unit
        for unit in units
        if unit.key not in records and unit.key not in exceptions and not is_body(unit)
    ]
    if not unaccounted:
        return
    named = "\n".join(f"  - {u.locator}: {u.text}" for u in unaccounted)
    raise NotImplementedError(
        f"migrate: {scope} -- {len(unaccounted)} unit(s) an independent census found are "
        "neither a produced record, a derived body line, nor a declared exception "
        f"(Ruling 83):\n{named}\nmigrate refuses to guess and silently report success "
        "instead."
    )


# Named distinctly from #602's own module-level `_ANY_HEADING_RE` (used by
# `_check_plan_reviews_heading_census` above) to avoid a silent duplicate-definition
# collision -- the two landed independently and are not byte-identical.
_CENSUS_ANY_HEADING_RE: Final = re.compile(r"^(#{1,6})[ \t]+(\S.*?)\s*$", re.MULTILINE)


def _heading_census_units(text: str, locator_prefix: str) -> list[tuple[int, _CensusUnit]]:
    """Every markdown heading in `text`, matched only on `^#{1,6}` -- a level-independent
    pattern that encodes no one splitter's expectations (Ruling 83 §2's own words: "for a
    heading-split file, every heading at any level"). Returns `(start_offset, unit)` pairs
    in document order.
    """
    out: list[tuple[int, _CensusUnit]] = []
    for m in _CENSUS_ANY_HEADING_RE.finditer(text):
        line_no = text.count("\n", 0, m.start()) + 1
        unit = _CensusUnit(
            key=str(m.start()), locator=f"{locator_prefix}:{line_no}", text=m.group(0).strip(),
            level=len(m.group(1)),
        )
        out.append((m.start(), unit))
    return out


def _record_spans(record_starts: Collection[int], text_len: int) -> list[tuple[int, int]]:
    """`[start, end)` for every record, the same "up to the next one, or EOF" shape every
    `_discover_*` heading-splitter already uses to slice a record's own body.
    """
    ordered = sorted(record_starts)
    return [
        (start, ordered[i + 1] if i + 1 < len(ordered) else text_len)
        for i, start in enumerate(ordered)
    ]


def _is_body_heading(
    unit: _CensusUnit,
    record_level: int,
    spans: Sequence[tuple[int, int]],
    first_record_start: int | None,
) -> bool:
    """Bucket 2 for a heading-split file: nested inside an established record's own body,
    or preamble before the first record -- both fold into a record's body by construction,
    per every `_discover_*` heading-splitter's own docstring ("preamble ... is prepended
    to the first split record's body").

    Nesting requires BOTH position and level, and neither alone is enough:

    - **Level alone is wrong** when no enclosing record exists at all -- `_discover_multi_
      ruling_files`'s `Ruling A1`/`A2` sit at `###` while `_RULING_HEADING_RE` targets
      `##`, but there is no *actual* `## Ruling N` record in that file for them to be
      "below": `record_level` there is a property of the *pattern*, not a structural fact
      about the whole file the way it is for a dedicated single-shape file. Treating
      "deeper than the pattern's own level" as sufficient would silently exempt exactly
      the units Ruling 83 requires this guard to name.
    - **Position alone is wrong** for the opposite reason (an earlier version of this
      function's mistake): a record's span runs to the *next* record's start, or EOF when
      there is none, so a same-level "impostor" heading sitting after the last real record
      falls inside that record's span with nothing to end it early, and would be silently
      absorbed as "nested" -- `_discover_closure_records`'s pre-`#585` defect (eleven
      unmatched headings folding into one neighbouring record's body) one level further
      down.

    Combined, a unit is nested only when it is both inside a specific record's span AND
    strictly deeper than that record's own level -- a same-level heading occurring
    anywhere in a record's span is never nested, and a deeper heading with no enclosing
    record is never nested either.
    """
    start = int(unit.key)
    if unit.level > record_level and any(s <= start < e for s, e in spans):
        return True
    return first_record_start is not None and start < first_record_start


def _check_heading_split_not_silently_unrecognised(
    locator_prefix: str, text: str, heading_re: re.Pattern[str], split_level: int, *, scope: str
) -> None:
    """Ruling 83's census for one dedicated heading-split file (`_discover_headed_split_
    file`'s shape: the file's *entire* structure is either a record, that record's own
    nested content, or the file's leading preamble -- nothing else is going on in it, so
    the fully generic `^#{1,6}` census from `_heading_census_units` is safe here without
    the word-anchoring `_check_multi_ruling_files_not_silently_unrecognised` needs for a
    directory of otherwise-unrelated documents). `split_level` is the heading depth
    `heading_re` itself targets (3, for both `closure-records.md` and `plan-reviews.md`'s
    `###` shape) -- passed explicitly rather than inferred from the pattern text, since a
    record's own matched level is the one fact `_is_body_heading` must not get wrong.
    """
    headings = _heading_census_units(text, locator_prefix)
    record_starts = {m.start() for m in heading_re.finditer(text)}
    spans = _record_spans(record_starts, len(text))
    first_record_start = min(record_starts) if record_starts else None
    units = [unit for _start, unit in headings]
    _reconcile_census(
        scope=scope,
        units=units,
        records={str(s) for s in record_starts},
        is_body=lambda u: _is_body_heading(u, split_level, spans, first_record_start),
    )


def _check_headed_split_file_not_silently_unrecognised(
    root: Path, rel_path: str, heading_re: re.Pattern[str], split_level: int, description: str
) -> None:
    """Task #30/#31 (Ruling 83's census), for `_discover_headed_split_file`'s shape
    (`plan-reviews.md` today; `closure-records.md` has its own discovery function and its
    own disposition logic -- Ruling 84 territory, not this one). Mirrors `_check_legacy_
    file_not_silently_unrecognised`'s early returns: a moved-away or genuinely blank file
    has nothing to reconcile. Runs *alongside*, not instead of, that existing "zero total"
    guard -- this one closes the arithmetic; that one still catches a file moved to an
    unexpected new location returning zero drafts outright.
    """
    path = root / rel_path
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return
    _check_heading_split_not_silently_unrecognised(
        rel_path, text, heading_re, split_level, scope=f"{rel_path} ({description})"
    )


def _check_closure_records_not_silently_unrecognised(root: Path) -> None:
    """Ruling 83's census for `_discover_closure_records`, deliberately excluded from
    `_check_headed_split_file_not_silently_unrecognised` above by that function's own
    docstring: "closure-records.md has its own discovery function and its own disposition
    logic -- Ruling 84 territory, not this one." `_discover_closure_records` classifies
    every `_CLOSURE_HEADING_RE` match into one of four buckets (`CR- kind: work`, `CR-
    kind: phase`, `RS- kind: audit`, `LG-`), but the census does not care which bucket a
    record lands in -- it only verifies every `###`-level unit in the file is one of the
    four, never silently folded into a neighbour's body.

    Ruling 84 §3 item 6: landing Ruling 83's census before this ruling's raise removal was
    ordering *for* this guard, not merely so the mechanism existed somewhere in the
    codebase -- removing the raise on the "not closed" branch is what exposes `_check_
    legacy_file_not_silently_unrecognised`'s weaker `if drafts: return` guard as the only
    thing standing between an undercount and a silent migration. Without this function,
    that stays true after this ruling lands too.

    Reuses `_check_heading_split_not_silently_unrecognised` — closure-records.md's real
    shape (a `###` record, its own nested `####`+ body, and one leading `#` preamble,
    nothing else) is exactly what that function already generalises over, verified against
    the real file directly (every `####`+ heading found sits inside an enclosing `###`
    record's span) rather than assumed from the plan-reviews.md precedent alone.
    """
    path = root / "docs" / "audit" / "closure-records.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return
    _check_heading_split_not_silently_unrecognised(
        "docs/audit/closure-records.md", text, _CLOSURE_HEADING_RE, 3,
        scope="docs/audit/closure-records.md (closure records)",
    )


_CENSUS_ANY_RULING_HEADING_RE: Final = re.compile(
    r"^#{1,6}[ \t]+Ruling[ \t]+\S.*$", re.MULTILINE
)


def _check_multi_ruling_files_not_silently_unrecognised(root: Path) -> None:
    """Task #31 (Ruling 83's census) for `_discover_multi_ruling_files`.
    `_RULING_HEADING_RE` assumes every ruling heading is written `## Ruling <digits>`; the
    real corpus carries some that are not (Ruling 83 §1(c)): a handful of files title
    themselves `# Ruling <n>` at h1 depth, and one file carries `### Ruling A1`/`A2`/`A3`
    sub-headings, whose letter suffixes `_RULING_HEADING_RE`'s `(\\d+)` cannot match.

    The independent unit-finder is anchored on the literal word "Ruling" (any heading
    level, any suffix) rather than the fully generic `^#{1,6}`
    `_check_heading_split_not_silently_unrecognised` uses for a *dedicated* single-purpose
    file: unlike `plan-reviews.md`, `docs/plans/` holds many files with their own,
    unrelated section structure (`## 1. The maintainer's instructions`, ...), which a fully
    generic heading census would wrongly sweep in as unaccounted.

    **Both open questions this docstring originally deferred are now ruled** (`docs/plans/
    2026-09-02-w37-ruling-a-series-and-standalone-ruling-files.md`), and this paragraph is
    corrected rather than left to read as still-current -- the *reasoning* below is what
    changed; the guard's behaviour today does not, because neither ruling is implemented
    in code yet:

    - **Ruling 87: a standalone ruling file (the h1 case) is `RL-`, not `PL- kind: leaf`.**
      Its §3 item 1 leaves open *which* function converts them ("a widened ruling
      splitter, or a prior classification pass") -- so a file whose only "Ruling"-anchored
      heading is also the file's own first heading stays exempt from *this* function's
      census, not because it is settled that `_discover_multi_ruling_files` will never be
      the mechanism, but because today it demonstrably is not one (zero `_RULING_HEADING_
      RE` matches, confirmed by running it) and no widening has landed. Once Ruling 87 is
      implemented, whichever function claims these files owns making them a `_reconcile_
      census` record; this guard does not anticipate that interface.
    - **Ruling 86: `Ruling A1`/`A2`/`A3` become three `RL-` records**, via `_RULING_
      HEADING_RE` widening on two axes (heading level and token shape, §3 item 1). That
      widening has not landed, so they are correctly still named as unaccounted below --
      this is `_reconcile_census` doing exactly its job (Ruling 83's own "the census
      cannot be cleared while three units are unclassified" is now "while the ruled
      widening is unimplemented", not a change to what this function does).

    **The coupling this leaves, stated rather than anticipated:** the "record" bucket
    below is keyed off `_RULING_HEADING_RE`'s own matches. If Ruling 86's widening lands
    inside that same pattern, this guard needs no change. If it lands as a *different*
    mechanism (a separate classification pass, per Ruling 87 §3 item 1's other option),
    this guard's `record_starts` must be re-pointed to recognise that mechanism's output
    too, or it will re-flag units a different, correct code path has already claimed. Not
    fixed pre-emptively -- the interface does not exist yet to fix it against.
    """
    plans_dir = root / "docs" / "plans"
    if not plans_dir.is_dir():
        return
    for path in sorted(plans_dir.glob("*.md")):
        if _PLAN_FILENAME_RE.match(path.name) is None:
            continue
        text = path.read_text(encoding="utf-8")
        loose = list(_CENSUS_ANY_RULING_HEADING_RE.finditer(text))
        if not loose:
            continue  # not remotely ruling-shaped -- `_discover_plain_plans`'s concern
        first_heading = _CENSUS_ANY_HEADING_RE.search(text)
        if (
            len(loose) == 1
            and first_heading is not None
            and first_heading.start() == loose[0].start()
        ):
            continue  # one ruling, titling its own file -- settled, not a defect (above)
        rel = path.relative_to(root).as_posix()
        record_starts = {m.start() for m in _RULING_HEADING_RE.finditer(text)}
        spans = _record_spans(record_starts, len(text))
        first_record_start = min(record_starts) if record_starts else None
        units = [
            _CensusUnit(
                key=str(m.start()),
                locator=f"{rel}:{text.count(chr(10), 0, m.start()) + 1}",
                text=m.group(0).strip(),
                level=len(m.group(0)) - len(m.group(0).lstrip("#")),
            )
            for m in loose
        ]

        def is_body(
            unit: _CensusUnit,
            spans: list[tuple[int, int]] = spans,
            first_record_start: int | None = first_record_start,
        ) -> bool:
            return _is_body_heading(unit, 2, spans, first_record_start)  # `## Ruling N`

        _reconcile_census(
            scope=f"{rel} (multi-ruling headings)",
            units=units,
            records={str(s) for s in record_starts},
            is_body=is_body,
        )


_CENSUS_DEP_BARE_RE: Final = re.compile(r"\*\*DEP-([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\*\*")


def _check_requirements_not_silently_unrecognised(root: Path) -> None:
    """Task #30 (Ruling 83's census) for `_discover_requirements`, the only discovery
    function that shipped with no guard at all. `_LEGACY_SPEC_BOLD_RE` assumes every
    legacy requirement id carries a module code between the prefix and the number
    (`**FR-DATA-12**`); `docs/specs/00-overview.md`'s `DEP-1`, `DEP-1a`, `DEP-2`, `DEP-3`
    are real, module-spec-defined dependency rules that never carry one -- confirmed
    empirically (zero `DEP` occurrences anywhere in `docs/specs/*.md` carry a module code),
    and invisible to every count built on that assumption, `docs/notes/0019-one-id-per-
    document.md`'s own acceptance-criteria greps included.

    The census here is deliberately narrower than "every bold span starting with a
    prefix": it drops only the module-code assumption (via `_CENSUS_DEP_BARE_RE`, `DEP`
    only -- see below for why not the other three), keeping the one genuinely structural
    signal a definition marker has and a reference does not -- the bold span closes right
    after the id, nothing else inside it. That is why a dated-amendment sentence like
    `**FR-OVR-20 says so twelve rows above this one**` (real corpus text) is never a
    census candidate at all -- the bold span does not close after the id -- while
    `**DEP-1a**` is.

    Scoped to `DEP` only, not all four prefixes: measured directly, broadening `FR`/`NFR`/
    `OQ` the same module-optional way finds zero additional real units in this corpus, and
    the post-migration form for those three is module-less (`**FR-<n>**`) -- broadening
    them would make this guard fire on `migrate`'s own second-run output and break
    idempotency. `DEP` carries no such collision: it is not recognised by `_discover_
    requirements` at all today, so it has no post-migration, module-less form to collide
    with yet.
    """
    specs_dir = root / "docs" / "specs"
    if not specs_dir.is_dir():
        return
    for path in sorted(specs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        records = {str(m.start()) for m in _LEGACY_SPEC_BOLD_RE.finditer(text)}
        units = []
        for m in itertools.chain(
            _LEGACY_SPEC_BOLD_RE.finditer(text), _CENSUS_DEP_BARE_RE.finditer(text)
        ):
            line_no = text.count("\n", 0, m.start()) + 1
            units.append(
                _CensusUnit(key=str(m.start()), locator=f"{rel}:{line_no}", text=m.group(0))
            )
        _reconcile_census(scope=f"{rel} (requirement ids)", units=units, records=records)


def _check_plain_plans_not_silently_unrecognised(root: Path) -> None:
    """Task #31 (Ruling 83's census) for `_discover_plain_plans`'s file-population shape:
    every file directly under `docs/plans/` -- not gated by `_PLAN_FILENAME_RE`'s own
    dated-filename assumption -- must become a plain-plan record, be derived as a multi-
    ruling file (`_discover_multi_ruling_files`'s own concern, computed the same way that
    function itself decides it), already carry a canonical post-migration filename (an
    idempotency/second-run reading, checked positively via `_docid.ID_RE` rather than "the
    legacy pattern found nothing" -- the fixture-corpus assumption Ruling 83 rejects), or
    be a declared exception. `docs/plans/README.md` is the one file this corpus carries
    that is none of the first three.
    """
    plans_dir = root / "docs" / "plans"
    if not plans_dir.is_dir():
        return
    units = []
    records: set[str] = set()
    derived: set[str] = set()  # bucket 2: a different function's own record, not listed
    for path in sorted(p for p in plans_dir.iterdir() if p.is_file()):
        key = path.name
        units.append(_CensusUnit(key=key, locator=f"docs/plans/{key}", text=key))
        if _PLAN_FILENAME_RE.match(path.name) is None:
            continue
        file_text = path.read_text(encoding="utf-8")
        if _RULING_HEADING_RE.search(file_text):
            derived.add(key)  # a multi-ruling file -- `_discover_multi_ruling_files`'s own
            continue
        records.add(key)

    def is_body(unit: _CensusUnit) -> bool:
        # Bucket 2: derived as a multi-ruling file (computed above, the same test
        # `_discover_plain_plans` itself uses to delegate), or already in a canonical
        # post-migration filename shape -- an idempotency/second-run reading, checked
        # positively via `_docid.ID_RE` rather than "the legacy pattern found nothing"
        # (the fixture-corpus assumption Ruling 83 rejects).
        return unit.key in derived or _docid.ID_RE.match(unit.key) is not None

    _reconcile_census(
        scope="docs/plans/ (plain plans)",
        units=units,
        records=records,
        is_body=is_body,
        exceptions={"README.md": "the directory's own README, not a dated record"},
    )


def _check_flat_document_directory_not_silently_unrecognised(
    root: Path, rel_dir: str, title_re: re.Pattern[str], description: str,
    exceptions: Mapping[str, str],
) -> None:
    """Task #31 (Ruling 83's census) for `_discover_notes`/`_discover_adrs`'s shared
    skip-path: "found nothing" there is read as "already migrated" purely because the
    legacy title regex found no match -- the exact fixture-corpus assumption Ruling 83
    rejects for `_discover_closure_records`, applied here to a directory instead of a
    heading. Every file directly under `rel_dir` must carry the legacy title, already be
    in a canonical post-migration filename shape (checked positively, the same idempotency
    reading `_check_plain_plans_not_silently_unrecognised` uses), or be a declared
    exception -- `<rel_dir>/README.md` in both `docs/notes/` and `docs/adr/` today.
    """
    directory = root / rel_dir
    if not directory.is_dir():
        return
    units = []
    records: set[str] = set()
    for path in sorted(p for p in directory.iterdir() if p.is_file()):
        key = path.name
        units.append(_CensusUnit(key=key, locator=f"{rel_dir}/{key}", text=key))
        if path.suffix == ".md" and title_re.search(path.read_text(encoding="utf-8")):
            records.add(key)

    def is_already_canonical(unit: _CensusUnit) -> bool:
        return _docid.ID_RE.match(unit.key) is not None

    _reconcile_census(
        scope=f"{rel_dir}/ ({description})",
        units=units, records=records, is_body=is_already_canonical, exceptions=exceptions,
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


def _find_table_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """Every maximal run of contiguous `|`-led lines in `lines` — a candidate markdown
    table, header and separator included, `(start, end)` with `end` exclusive.
    """
    blocks: list[tuple[int, int]] = []
    i, n = 0, len(lines)
    while i < n:
        if lines[i].startswith("|"):
            start = i
            while i < n and lines[i].startswith("|"):
                i += 1
            blocks.append((start, i))
        else:
            i += 1
    return blocks


def _roadmap_row_block(templates_dir: Path, d: _Draft, all_drafts: list[_Draft]) -> str:
    """One `WK-`/`SL-` fenced row block, keyed off `d.prefix` rather than assuming `WK`
    — restored from the pre-Ruling-90 version of `_restructure_roadmap`, which handled
    both row families this way. `_discover_roadmap` above only ever produces `WK` drafts
    today (Ruling 80/83: no slice exists in the real corpus in any shape), but this
    function's own contract — and Ruling 81's round-trip test, which feeds it a hand-built
    `SL` draft directly — is not limited to that one caller.
    """
    canon = _docid.canonical(d.prefix, d.number)
    family = "work" if d.prefix == "WK" else "slice"
    heading_level = "###" if d.prefix == "WK" else "####"
    fields = {
        "id": canon, "family": family, "title": d.title, "status": d.status,
        "created": d.created.isoformat(), "owner": d.owner, "phase": d.phase,
    }
    if d.prefix == "SL" and d.work_token is not None:
        fields["work"] = _docid.canonical(
            "WK", next(x.number for x in all_drafts if x.old_token == d.work_token)
        )
    permitted = _docid.row_template_fields(templates_dir, family)
    unknown = sorted(set(fields) - permitted)
    if unknown:
        raise ValueError(
            f"_restructure_roadmap: would emit field(s) {unknown} for a {family} row "
            f"({canon}) not declared by docs/_templates/{_docid.ROW_TEMPLATE_FILES[family]} "
            "— the writer must not disagree with the template (Ruling 79 §3 item 4)"
        )
    field_text = "\n".join(f"{k}: {v}" for k, v in fields.items())
    body = d.body.strip()
    return f"\n{heading_level} {canon} — {d.title}\n\n```yaml\n{field_text}\n```\n\n{body}\n"


def _restructure_roadmap(
    root: Path,
    roadmap_drafts: list[_Draft],
    phase_titles: Mapping[str, str],
    occurrences: list[_RoadmapRowOccurrence],
) -> None:
    """NT-0019 §4 step 3, as Rulings 90-92 settled what it produces: a **surgical, in-place
    edit** of `docs/roadmap.md`, never the full-file overwrite this function used to be.

    That distinction is not cosmetic. Every previous version of this function replaced the
    entire file with a stub built only from `roadmap_drafts` — safe only because
    `_discover_roadmap` had been returning zero drafts since W37-5 shipped (all three of
    its legacy patterns matched the real file zero times), so this call was never reached.
    The moment discovery recognises the real shape, the old body destroys the other ~700
    lines of this file — decision gates, sizing, every phase's narrative — the first time
    `migrate` runs against the real tree. Fixing discovery and leaving this function alone
    would have turned a silent no-op into a silent, irreversible loss inside the one commit
    that cannot be re-run (NT-0019 §4: "one scripted PR, once"). This rewrite is therefore
    the other half of task #32, not a follow-on: removing exactly the leading work-id row
    lines Ruling 91 merges away, inserting the new `WK-` blocks, and leaving every other
    line — headings, prose, the other ten `##` sections — byte-identical.

    A table left with no data rows once its work rows are gone is removed in full (header,
    separator, and — where a heading's only content was that table — the heading too),
    never left as a header-only husk; the removal itself is the diff hunk that accounts for
    it (Ruling 91 obligation 3). A table that mixes work rows with others (the "status"
    tables' Exit demo / Exit gate / phase-label rows) keeps everything but the converted
    rows. Whether to keep, fold or replace a source table is this function's call (Ruling
    91's routing table: "an editorial choice ... not a standard question"); folding narrow
    line ranges in place, rather than rebuilding sections from scratch, is the version of
    that choice least likely to lose something nobody asked it to touch.

    Each phase's own `## <n>. Phase <label> — <title>` / `### Phase <label> — <title>`
    heading becomes its `## P<label> — <title>` milestone form with a plain fields block
    (Ruling 80), and every work assigned to that phase is inserted as a `### WK-NNNNN`
    block immediately after it — `_discover_roadmap` already refused if any work's
    occurrences disagreed on which phase it belongs to, so every phase named in
    `phase_titles` here has exactly one declaring heading.

    The row block's field set is validated against `_docid.row_template_fields` rather
    than hardcoded (Ruling 79 §3 item 4), the same reasoning the previous version of this
    docstring already gave and which still holds: only `id, family, title, status,
    created, owner, phase` are emitted, a `_Draft`'s natural fields, and not
    `tree:`/`corrected_by:`/`relates:`, which the template also permits but for which a
    freshly-converted row has no value to invent.
    """
    templates_dir = root / "docs" / "_templates"
    roadmap_path = root / "docs" / "roadmap.md"
    text = roadmap_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    removed: set[int] = {occ.line_no - 1 for occ in occurrences}
    for start, end in _find_table_blocks(lines):
        if end - start <= 2:
            continue
        if all(i in removed for i in range(start + 2, end)):
            removed.update((start, start + 1))
            j = start - 1
            while j >= 0 and lines[j].strip() == "":
                j -= 1
            if j >= 0 and j not in removed and _ROADMAP_ANY_HEADING_RE.match(lines[j]):
                removed.add(j)

    drafts_by_phase: dict[str, list[_Draft]] = {}
    for d in roadmap_drafts:
        assert d.phase is not None  # every roadmap_row draft carries one (see caller)
        drafts_by_phase.setdefault(d.phase, []).append(d)

    phase_heading_idx: dict[str, int] = {}
    for i, line in enumerate(lines):
        m = _ROADMAP_PHASE_TITLE_RE.match(line)
        if m is None:
            continue
        label = f"P{m.group(1)}"
        if label in drafts_by_phase and label not in phase_heading_idx:
            phase_heading_idx[label] = i

    missing = set(drafts_by_phase) - set(phase_heading_idx)
    if missing:
        raise AssertionError(
            f"_restructure_roadmap: no declaring 'Phase <label> — <title>' heading found "
            f"for {sorted(missing)}, which _discover_roadmap assigned work(s) to"
        )

    inserted: dict[int, str] = {}
    for phase, idx in phase_heading_idx.items():
        phase_drafts = drafts_by_phase[phase]
        works = sorted(
            (d for d in phase_drafts if d.prefix == "WK"),
            key=lambda d: _work_id_sort_key(d.old_token or ""),
        )
        title = phase_titles.get(phase[1:])
        if title is None:
            raise AssertionError(f"_restructure_roadmap: no title recorded for phase {phase!r}")
        works_canon = [_docid.canonical("WK", d.number) for d in works]
        block = [
            _PHASE_TEMPLATE.format(
                phase=phase, title=title,
                opened=min(d.created for d in phase_drafts).isoformat(),
                works=", ".join(works_canon),
            ).rstrip("\n")
        ]
        for work in works:
            block.append(_roadmap_row_block(templates_dir, work, roadmap_drafts))
            slices = sorted(
                (d for d in phase_drafts if d.prefix == "SL" and d.work_token == work.old_token),
                key=lambda d: d.tie_break,
            )
            for sl in slices:
                block.append(_roadmap_row_block(templates_dir, sl, roadmap_drafts))
        inserted[idx] = "\n".join(block)

    out: list[str] = []
    for i, line in enumerate(lines):
        if i in inserted:
            out.append(inserted[i])
            continue
        if i in removed:
            continue
        out.append(line)
    new_text = "\n".join(out)
    if not new_text.endswith("\n"):
        new_text += "\n"
    roadmap_path.write_text(new_text, encoding="utf-8")


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
# Ruling 84 §4's second acceptance item, as Ruling 94 substituted it
# (`docs/plans/2026-09-02-w37-vacuous-acceptance-item-ruling.md` §2 — register finding
# F77). The struck form asked for a check reddening "on a deliberately broken fixture
# carrying `slice: SL-99999`", which no fixture can produce: `_stamp_header` skips `slice`
# for every caller, so the writer refuses to emit the key a fixture would have to carry.
# Nothing was ever wrong because nothing was ever written.
#
# The substituted form *counts* rather than forbids, and Ruling 94 §2 gives the reason:
# forbidding `slice:` outright "encodes this migration's 'no data source' state as the
# rule, so it would red correctly today and wrongly the first time a ledger legitimately
# carries a slice" (Ruling 84 §3 item 5 keeps the field permitted for every other ledger).
# Its broken input is "a one-line mutation of `_stamp_header` — remove `slice` from the
# skip tuple so the template's `slice: SL-NNNNN` placeholder is emitted", the
# mutate-the-writer shape Ruling 70 item 2 established and Rulings 79/80 already use.
#
# Ruling 84 §4's *third* item shares this pass, because Ruling 94 §4 obliges it — "an
# emitted `LG-` with `work=None` must red. *Violation: assuming an item is satisfied
# because its sibling was found vacuous*" — and because Ruling 84 §1(e) makes the two one
# property: "the ten are permitted to omit `slice:` because `work:` is present, not
# because both may be absent."
#
# Read from the files on disk, never from `migrate`'s own draft bookkeeping, for the
# reason `migration_diff_violations` gives above: a bug in what `migrate` *reports* must
# not be able to hide from what it *did*. `slice:` in particular exists only as a
# template placeholder that survives `_stamp_header` — no `_Draft` field carries it — so a
# draft-level check could not see the mutation at all.
# ---------------------------------------------------------------------------------------


@dataclass(frozen=True)
class _LedgerAxes:
    """What the ledger-axis check looked at, not only what it found. The three counts are
    reported unconditionally (including zero) by `_cmd_migrate`, per Ruling 94's "the
    passing state today is a count of **zero**, and the check must **say so** rather than
    pass silently" and [`NT-0007`](../docs/notes/0007-context-bound-measures-cap-not-discipline.md):
    a boundary metric that reads zero by construction reports where the boundary sits, not
    that anything was verified.
    """

    records: int
    slice_values: int
    work_values: int
    slice_violations: tuple[str, ...]
    work_violations: tuple[str, ...]


def _emitted_ledger_headers(root: Path) -> list[tuple[str, _docid.Header]]:
    """Every `LG-` document present under the ledger family directory of `root`, as
    `(repo-relative path, parsed header)`. Filtered on the header's own `id:` rather than
    on the filename, so a file that landed in the directory without an id — or with
    another family's — is not counted as a ledger this migration emitted.
    """
    ledgers_dir = root / "docs" / _DOCUMENT_FAMILY_DIR["LG"]
    if not ledgers_dir.is_dir():
        return []
    found: list[tuple[str, _docid.Header]] = []
    for path in sorted(ledgers_dir.rglob("*.md")):
        header = _docid.parse_header(path)
        if header is None or header.id is None:
            continue
        id_match = _docid.ID_RE.fullmatch(header.id)
        if id_match is None or id_match.group(1) != "LG":
            continue
        found.append((path.relative_to(root).as_posix(), header))
    return found


def _resolves_to_row(value: str, prefix: str, rows: Collection[tuple[str, int]]) -> bool:
    """Whether `value` is a well-formed `prefix`-family id naming a row in `rows`.

    Parsed with `_docid.ID_RE` rather than compared as a string, so the padded filename
    form and the unpadded citation form of one id resolve alike (NT-0019 §1.1 rules 2-3) —
    and so a value that is not an id at all, the template's own `SL-NNNNN` placeholder
    included, resolves to nothing rather than raising.
    """
    match = _docid.ID_RE.fullmatch(value.strip())
    if match is None or match.group(1) != prefix:
        return False
    return (prefix, int(match.group(2))) in rows


def _check_emitted_ledger_axes(root: Path) -> _LedgerAxes:
    """Ruling 84 §4's second and third acceptance items, over the ledgers `root` actually
    carries, resolved against `root`'s own (post-restructure) `docs/roadmap.md`.

    Both row families come from `scan_roadmap_row_ids`, the module's existing reader of
    `WK-`/`SL-` row headings — never a second pattern, which is how two definitions of
    "a row" drift apart (Ruling 67 §2).
    """
    emitted = _emitted_ledger_headers(root)
    row_ids = list(scan_roadmap_row_ids(root))
    slice_rows = {pair for pair in row_ids if pair[0] == "SL"}
    work_rows = {pair for pair in row_ids if pair[0] == "WK"}

    slice_values = work_values = 0
    slice_violations: list[str] = []
    work_violations: list[str] = []
    for rel, header in emitted:
        if header.slice_ is not None:
            slice_values += 1
            if not _resolves_to_row(header.slice_, "SL", slice_rows):
                slice_violations.append(
                    f"{rel}: slice: {header.slice_} resolves to no SL- row in "
                    "docs/roadmap.md (Ruling 84 §4 item 2, as substituted by Ruling 94)"
                )
        if header.work is not None:
            work_values += 1
            if not _resolves_to_row(header.work, "WK", work_rows):
                work_violations.append(
                    f"{rel}: work: {header.work} resolves to no WK- row in "
                    "docs/roadmap.md (Ruling 84 §4 item 3)"
                )
        elif header.slice_ is None:
            work_violations.append(
                f"{rel}: carries neither work: nor slice: (Ruling 84 §4 item 3 — a "
                "ledger omits slice: because work: is present, not because both may be "
                "absent, §1(e))"
            )
    return _LedgerAxes(
        records=len(emitted),
        slice_values=slice_values,
        work_values=work_values,
        slice_violations=tuple(slice_violations),
        work_violations=tuple(work_violations),
    )


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
    notes_drafts = _discover_notes(root)
    _check_flat_document_directory_not_silently_unrecognised(
        root, "docs/notes", _NOTE_TITLE_RE, "notes",
        {"README.md": "the directory's own README, not a governed note"},
    )
    drafts += notes_drafts
    adr_drafts = _discover_adrs(root)
    _check_flat_document_directory_not_silently_unrecognised(
        root, "docs/adr", _ADR_TITLE_RE, "ADRs",
        {"README.md": "the directory's own README, not a governed ADR"},
    )
    drafts += adr_drafts
    multi_ruling_drafts = _discover_multi_ruling_files(root)
    _check_multi_ruling_files_not_silently_unrecognised(root)
    drafts += multi_ruling_drafts
    closure_drafts = _discover_closure_records(root)
    _check_legacy_file_not_silently_unrecognised(
        root / "docs" / "audit" / "closure-records.md", closure_drafts, "closure records"
    )
    _check_closure_records_not_silently_unrecognised(root)
    drafts += closure_drafts
    review_drafts = _discover_plan_reviews(root)
    _check_legacy_file_not_silently_unrecognised(
        root / "docs" / "audit" / "plan-reviews.md", review_drafts, "plan reviews"
    )
    # Both guards kept, deliberately: #602's own bespoke, file-specific census
    # (_check_plan_reviews_heading_census) and this slice's shared, reusable mechanism
    # cover the same file with overlapping but independently-derived logic. Reported to
    # the lead as a collision rather than silently reconciled -- see the PR body.
    _check_plan_reviews_heading_census(root)
    _check_headed_split_file_not_silently_unrecognised(
        root, "docs/audit/plan-reviews.md", _REVIEW_HEADING_RE, 3, "plan reviews"
    )
    drafts += review_drafts
    plain_plan_drafts = _discover_plain_plans(root)
    _check_plain_plans_not_silently_unrecognised(root)
    drafts += plain_plan_drafts
    requirement_drafts = _discover_requirements(root)
    _check_requirements_not_silently_unrecognised(root)
    roadmap_drafts, phase_titles, roadmap_occurrences = _discover_roadmap(root)
    register_drafts = _discover_register(root)
    _check_legacy_file_not_silently_unrecognised(
        root / "docs" / "audit" / "register.md", register_drafts, "register finding rows"
    )
    drafts += requirement_drafts + roadmap_drafts + register_drafts
    # Hoisted here to run alongside every other discovery, before any write below: a
    # malformed vendored manifest's HeaderError must abort migrate cleanly, not after
    # Phase C's document/roadmap/register writes have already landed on disk (task #34).
    # `_is_vendored_skill_manifest`'s detection rule was LICENSE-based until Ruling 69's
    # membership-test fix landed here (reassigned to this slice by Ruling 76); this hoist
    # was never about which files the check reaches, only about when a malformed one
    # aborts the run.
    vendored_skill_manifests = _discover_vendored_skill_manifests(root)

    start = compute_next(root)
    _assign_numbers(drafts, start)

    files_written, files_deleted = _write_document_drafts(root, drafts, roadmap_drafts)

    if roadmap_drafts:
        _restructure_roadmap(root, roadmap_drafts, phase_titles, roadmap_occurrences)
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

    # Last, because it reads what was written rather than what was planned, and the
    # roadmap it resolves against is only final after `_restructure_roadmap` above.
    #
    # The two limbs are treated differently, deliberately, and each for a stated reason.
    # `slice_violations` raises: Ruling 94 says "requires every one to resolve", and the
    # count is zero by construction today (`_stamp_header` skips the key), so this can
    # fire only after a deliberate change to the writer — it adds no new way for a real
    # run to stop. `work_violations` warns: Ruling 84 §4 item 3 scopes itself to "once
    # W37-6 has created the `WK-` rows", a state nothing can execute end to end while the
    # three unconditional guards (F80-F82) abort a real run before it, so making it abort
    # would add an unmeasured stop to an irreversible migration. It is a hard assertion in
    # the tests instead. Flagged as an interpretation rather than made silently, in
    # `docs/audit/findings/F77.md`'s 2026-09-02 update and this row's register entry.
    ledger_axes = _check_emitted_ledger_axes(root)
    warnings.extend(ledger_axes.work_violations)
    if ledger_axes.slice_violations:
        raise ValueError(
            "migrate: emitted LG- record(s) carry a slice: naming no SL- row -- "
            + "; ".join(ledger_axes.slice_violations)
        )

    return MigrateResult(
        assigned=tuple(assigned),
        redirect_rows=tuple(redirect_rows),
        files_written=tuple(dict.fromkeys([*files_written, *rewritten])),
        files_deleted=tuple(files_deleted),
        skipped_vendored=tuple(skipped_vendored),
        warnings=tuple(warnings),
        ledger_records_checked=ledger_axes.records,
        ledger_slice_values_checked=ledger_axes.slice_values,
        ledger_work_values_checked=ledger_axes.work_values,
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
    # Unconditionally, including the zeros — Ruling 94: "the passing state today is a
    # count of zero, and the check must say so rather than pass silently."
    print(
        f"doc-id.py migrate: ledger axes checked on {result.ledger_records_checked} "
        f"emitted LG- record(s): {result.ledger_slice_values_checked} slice: value(s) "
        f"and {result.ledger_work_values_checked} work: value(s) resolved against "
        "docs/roadmap.md",
        file=sys.stderr,
    )
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
