#!/usr/bin/env python3
"""doc-id.py — NT-0019's id allocator, checker and widener.

Subcommands: `next`, `check`, `widen`. `migrate` is **not** part of this script yet — it
is W37-5's, built and proven against a fixture corpus before anything real moves
(`docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`, slice W37-2 vs W37-5).

`docs/notes/0019-one-id-per-document.md` §1.7 (`next`, `check`), §1.8 (`widen`).

**Standard library only** (G4/DP-5) — see `scripts/_docid.py`'s module docstring for why.
`subprocess` calls to `git` are git plumbing, not a package import, and are explicitly
authorised by the plan's Tech Stack line.

Usage:
    python3 scripts/doc-id.py next
    python3 scripts/doc-id.py check [--classify]
    python3 scripts/doc-id.py widen --to WIDTH
"""

from __future__ import annotations

import argparse
import csv
import itertools
import re
import subprocess
import sys
import tempfile
import zipfile
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
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


def _governed_header_ids(tree_root: Path) -> Iterator[tuple[str, int, Path]]:
    """Every governed file under the header-bearing locations that has a parseable
    header naming a resolvable id — the shared scan behind `next`'s header source and
    `check`'s duplicate/mismatch detection alike.

    Excludes `_templates/` (example headers with placeholder ids — the same exemption
    check 31 gets by path, NT-0019 §1.4) and vendored skill content (§1.5: a vendored
    skill's files are exempt from stamping, so they are never a real source of a live id —
    see `_docid.is_vendored`'s own docstring for the known detection gap).

    A file whose front matter does not fit NT-0019 §1.5's closed grammar at all —
    `parse_header` raising `HeaderError` — is skipped, not fatal: verified against this
    repository's own real tree, `.claude/skills/create-adaptable-composable/SKILL.md`
    carries upstream front matter with a nested `metadata:` mapping, and `is_vendored`
    does not catch it (the reported LICENSE-detection gap). Whether a *governed* file's
    header is malformed is check 30's question (W37-4), not this scan's; this scan's job
    is finding every live id, and a file it cannot parse contributes none, the same as a
    file with no front matter at all.
    """
    for path in _candidate_header_paths(tree_root):
        if "_templates" in path.relative_to(tree_root).parts:
            continue
        if _docid.is_vendored(path, tree_root):
            continue
        try:
            header = _docid.parse_header(path)
        except _docid.HeaderError:
            continue
        if header is None or header.id is None:
            continue
        match = _docid.ID_RE.fullmatch(header.id)
        if match is None:
            continue
        yield match.group(1), int(match.group(2)), path


def scan_header_ids(tree_root: Path) -> Iterator[tuple[str, int]]:
    """Source 1 of 4 (NT-0019 §1.7): every header `id:` field under the governed
    locations — see `_governed_header_ids` for exactly what counts and why.
    """
    for prefix, number, _path in _governed_header_ids(tree_root):
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
    for prefix, number, path in _governed_header_ids(tree_root):
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
    for prefix, number, path in _governed_header_ids(tree_root):
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
    """
    counts: dict[str, int] = {}
    for rel in git_ls_files(repo_root, "docs"):
        parts = Path(rel).parts  # ("docs", ...) always, since the pathspec was "docs"
        if len(parts) < 2:
            continue  # defensive: git ls-files -- "docs" cannot itself return "docs"
        if len(parts) == 2:
            family = "reference" if parts[1] == "README.md" else "none"
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


def compute_next_at_ref(ref: str, *, repo_root: Path = REPO_ROOT) -> int:
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
        return compute_next(tree)


# ---------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------


def _cmd_next(args: argparse.Namespace) -> int:
    try:
        number = compute_next_at_ref(args.ref, repo_root=args.repo_root)
    except GitArchiveError as exc:
        print(f"doc-id.py next: {exc}", file=sys.stderr)
        return 1
    print(number)
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
    return 1 if failures else 0


def _cmd_widen(args: argparse.Namespace) -> int:
    result = widen(args.repo_root, to=args.to)
    for old_rel, new_rel in result.renamed:
        print(f"renamed {old_rel} -> {new_rel}")
    for warning in result.warnings:
        print(f"doc-id.py widen: warning: {warning}", file=sys.stderr)
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

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
