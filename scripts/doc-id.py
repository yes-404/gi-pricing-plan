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
    python3 scripts/doc-id.py migrate --verify [SNAPSHOT] [--ref REF]

`migrate --verify` is Ruling 102 §1's instrument
(`docs/plans/2026-09-03-w37-6-ruling-102-verify-instrument.md`): it runs the migration on a
disposable snapshot — never a real checkout — computes all nine NT-0019 §7 (a)-(i)
acceptance rows with the predicate each counted with, and exits 1 on any fail. The rows
themselves live in `scripts/_docverify.py`; this file only owns the CLI seam, so that the
predicates stay in one module rather than being re-derived beside the code they measure.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import types
import zipfile
from collections.abc import Callable, Collection, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Final

import _docid
import _docverify

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


# A row's OWN id, in the leading cell `doc-index.py`'s `render_index` always writes it in
# (`"| " + id + " | " + family + " | " + ...`) -- never a bare `_docid.ID_RE` sweep of the
# whole file. A generated row's *body* column routinely cites other ids in prose (a large
# requirement's description names half a dozen more), and nothing distinguishes such a
# citation from a row's own definition once the scan is not anchored to the id column: it
# manufactures a false "present" for a number no row ever defines
# (`docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`'s own illustrative `PL-01240`,
# quoted verbatim inside another row's body, is exactly this) without correcting the
# opposite failure -- the id `scan_bold_id_rows` never turned into a row at all, which is
# what `doc-id.py check`'s NT-0019 §7(b) noncontiguous-id failures actually are.
_INDEX_ROW_ID_RE: Final = re.compile(
    r"^\|\s*(FR|NFR|DEP|OQ|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0*(\d+)\s*\|"
)


def scan_index_ids(tree_root: Path) -> Iterator[tuple[str, int]]:
    """Source 4 of 4: every id `docs/INDEX.md` lists in a row's own leading id column — the
    generated safety net. Anchored to `doc-index.py`'s own `render_index` row shape
    (`_INDEX_ROW_ID_RE`) rather than a whole-text sweep — see that constant's comment.
    """
    index_path = tree_root / "docs" / "INDEX.md"
    if not index_path.is_file():
        return
    text = index_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        match = _INDEX_ROW_ID_RE.match(line)
        if match is None:
            continue
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

    Widened again W37-6, two census defects NT-0019 §1.2's own Reference row names and
    this function did not implement:

    - **`docs/contracts/`** — the row's second named path (*"`process/`, `contracts/`,
      every `README.md` anywhere in the tree, ..."*) — was absent from the `subdir`
      branch below, so every file under it fell to `_CLASSIFY_FAMILY_BY_DIR.get(subdir,
      "none")` and counted `"none"`: 61 files at the tree this docstring was last verified
      against (`git ls-files docs/contracts | wc -l`). Mapped to `"reference"` alongside
      `process/`, the identical reading the row already gives both paths.
    - **Every `README.md` anywhere in the tree**, not the five whitelisted top-level
      names — the row's third clause, unqualified by location. Checked *before* the
      `len(parts) == 2` / `subdir` branches below, so a `README.md` nested under a family
      directory (`docs/workflows/README.md`, `docs/findings/README.md`, ...) is
      `"reference"` too, never that directory's own family bucket — Reference is what NT-
      0019 §1.2 names for it, not a second definition of what "workflow"/"finding"/etc.
      contains.
    - **Every `INDEX.md` anywhere in the tree**, on the same clause and for the same
      reason as the `README.md` widening above it. Ruling 101 clause 1 puts a generated
      split-source index inside a family directory (`docs/rulings/INDEX.md`, ...), and
      without this it would be counted as a *member* of the family it indexes -- one
      spurious `"ruling"`/`"closure"`/`"plan"` per index file. An index of a family is
      Reference, exactly as that family's README is; NT-0019 §1.2's Reference row already
      names `INDEX.md` (as the top-level one), and nesting does not change what it is.
      This does **not** move the `"none"` count: an `INDEX.md` under a family directory
      already matched `_CLASSIFY_FAMILY_BY_DIR`, so the widening corrects which bucket it
      lands in, never whether it lands in one.
    """
    top_level_reference_files = frozenset(
        {
            "README.md", "INDEX.md", "REDIRECTS.csv", "roadmap.md", "open-questions.md",
            # `skills-map.md` — NT-0019 §5.2 `:315`: *"`skills-map.md` | citations rewrite
            # | `M`"* — it is swept for citation rewrites in place, never moved into a
            # family directory, the same "stays at its own top-level path" shape the five
            # names above already have. A W37-6 census widening, not a §1.2 family: this
            # file names no document family at all.
            "skills-map.md",
        }
    )
    counts: dict[str, int] = {}
    for rel in git_ls_files(repo_root, "docs"):
        parts = Path(rel).parts  # ("docs", ...) always, since the pathspec was "docs"
        if len(parts) < 2:
            continue  # defensive: git ls-files -- "docs" cannot itself return "docs"
        if parts[-1] in ("README.md", "INDEX.md"):
            family = "reference"
        elif len(parts) == 2:
            family = "reference" if parts[1] in top_level_reference_files else "none"
        else:
            subdir = parts[1]
            if subdir == "_templates":
                family = "template"
            elif subdir == "specs":
                family = "requirement"
            elif subdir in ("process", "contracts"):
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


#: `citing_dir` (task 4 item 4, the 27/34 class-4 link hunks): blank for every row that
#: predates it and for every tree-wide id/path row -- those are correct from any citing
#: file, by definition. Set only for a bare-basename relative-link repoint
#: (`_bare_basename_rewrite`'s own token form), where `old_id`/`new_id` are not global ids
#: at all but the *relative link text* as written from files in that one directory --
#: `../audit/register.md` from `docs/rulings/` is a different string from the same target
#: cited by relative path from a directory at a different depth, so a row without a scope
#: would be silently wrong for every other citing directory it happened to also match.
#: `(g)`'s inverse and the class-4 split-body check both read this column to build a
#: per-file merged inverse rather than the single flat one every other row still uses.
_REDIRECTS_FIELDS: Final = ("old_id", "new_id", "old_path", "new_path", "citing_dir")


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

    Bytecode caching suppressed for the duration of this one `exec_module` call: this
    helper is what `migrate()` uses (via `_load_doc_index`/`_load_audit_docs`/
    `_load_register_lint`) to load `root/scripts/*.py` **while `root` is one of `verify`'s
    snapshot trees**, and the default loader writes a `.pyc` into `root/scripts/
    __pycache__/` as a side effect of exec'ing it. That directory then exists only because
    this process ran, appears only in the migrated tree (the control is never `migrate()`d
    and the loads here never touch it), and — before `_iter_tree_files`'s own
    `sweep_exclusion_reason` filter, above — was read by `_read_tree_text`/
    `classify_migration_diff` as a genuinely new file the migration produced: the
    instrument measuring its own exhaust as row (g) residue. `sys.dont_write_bytecode` is
    process-global, not per-loader, so it is saved and restored rather than left set —
    a concurrent import elsewhere in the same interpreter must not have its own caching
    behaviour silently changed by this helper running.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode
    return module


def _load_doc_index(repo_root: Path = REPO_ROOT) -> types.ModuleType:
    """`scripts/doc-index.py`, loaded by path.

    Loaded from `repo_root`'s own `scripts/` when it has one, and only then falls back to
    *this* repository's own copy — the reverse of the rule every other `_load_*` helper in
    this file states and keeps (`_load_audit_docs`, `_load_register_lint`): those exist to
    reuse stable *parsing logic* against a target that may carry no tooling of its own (a
    bare `tests/fixtures/docs-migration/`-style fixture), so pinning them to this
    repository's own `scripts/` is correct. This call is different: `migrate()`'s own
    `_regenerate_index_for_migrate` uses this module to *write* `docs/INDEX.md`'s content
    into `root`, and NT-0019 §7(c)'s instrument later re-derives that same content by
    running `root/scripts/doc-index.py --check` as an independent process against `root`
    (Ruling 102 §1's own predicate: "the tree's OWN copy"). When `root` carries its own
    `scripts/` — a real repository snapshot, exactly what `--verify`'s git-archive tree is —
    `_rewrite_citations` has, by the time this runs, already swept `root/scripts/
    doc-index.py` itself (an `NT-0019`/`Ruling NN` docstring or literal is rewritten to its
    post-migration citation form, and `render_index`'s own written header line, `"...see
    NT-0019 §1.4."`, is exactly such a literal). Writing `docs/INDEX.md` with *this* repository's
    still-unrewritten copy while `--check` reads the target's already-rewritten one makes
    the two disagree by that one line — no `OK (byte-stable)`, NT-0019 §7(c)'s own failure.
    Loading `root`'s own copy first, when it exists, makes both sides run the identical
    source. A bare fixture with no `scripts/` at all still falls back to this repository's
    copy exactly as before.
    """
    candidate = repo_root / "scripts" / "doc-index.py"
    if not candidate.is_file():
        candidate = REPO_ROOT / "scripts" / "doc-index.py"
    return _load_module("_doc_index_for_migrate", candidate)


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

#: Every prefix `_stamp_header` can render, mapped to its template. **`REFERENCE` is here
#: and deliberately absent from `_DOCUMENT_FAMILY_DIR`**: the Reference family is stamped
#: in place by `_stamp_reference_targets` and the vendored-manifest writer, never moved
#: into a family directory, and it carries no `id:` (§1.2) so it has no padded filename
#: either. That is the only legitimate difference between the two tables, and
#: `_check_every_document_draft_is_placeable` treats it as the only one.
_MIGRATE_TEMPLATE_FILENAME: Final[Mapping[str, str]] = {
    "ADR": "ADR.md", "RFC": "RFC.md", "PL": "PL.md", "RL": "RL.md", "CR": "CR.md",
    "REFERENCE": "REFERENCE.md", "LG": "LG.md", "RS": "RS.md", "FD": "FD.md", "WF": "WF.md",
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
    # Ruling 89's re-derivation, and the maintainer's extension of it to the path-only
    # case: the 1-based, inclusive line range this draft's body occupied **in its source
    # file**, and the number of lines the written file puts in front of that body (its
    # stamped header). Together they map a source line number onto the destination
    # record's own numbering, which is what lets a `path:1994` citation into a split file
    # be re-derived rather than repointed blind. Set only where a source can produce more
    # than one draft — the splitters and `_discover_plain_plans` (whose whole-file draft
    # can coexist with `_discover_lettered_rulings`' nested ones). `None` means "this
    # draft cannot say where it came from", and a split source with any such target
    # refuses line resolution outright rather than guessing.
    source_line_span: tuple[int, int] | None = None
    body_line_offset: int = 0
    # requirement/register-row fields:
    source_path: Path | None = None
    match_span: tuple[int, int] | None = None  # char offsets of the old token, for in-place rewrite
    # Task 4's wf-0n ruling (team-lead, 2026-09-04, citing the deputy): a legacy workflow
    # is cited two ways in the real corpus -- the filename's own lowercase form (`wf-01`,
    # `old_token`'s primary key, since that is the identifier itself under §7(d)'s own
    # `wf-0[0-9]` alternative) and the in-file heading's uppercase form (`WF-01`). Both
    # must resolve to the same new id or the uppercase form -- what nearly every real
    # citation of a workflow actually uses -- goes unswept forever (case-sensitive
    # substitution never bridges the two). `extra_old_tokens` carries every alias beyond
    # `old_token` that a citation of this draft may use; empty for every other family.
    extra_old_tokens: tuple[str, ...] = ()


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
    # W37-5c item 2: `(path, reason)` for every file **in** NT-0019 §4 step 5's Reference
    # stamp set that this run did not stamp — the 53 carrying the harness's own front
    # matter, the two §5.2/§5.3 delete, and the check-35 fixture. Carried out and printed
    # by name rather than left absent, for the reason the ledger-axis zeros above are:
    # a population nothing reports is a population nothing can check. F83's condition 1
    # ("every exempt entry cites its reason") applied to a deferral rather than to an
    # exemption — these are waiting on W37-6's Task 1, not permanently out.
    deferred_reference_stamps: tuple[tuple[str, str], ...] = ()
    # Bucket (iv): every citation of a split source that named no single target. Carried
    # out by name — citing file, line, source path and the competing destinations —
    # because the ruling's disposition is per citation, and a count is not something a
    # reader can disposition. Under Ruling 101 clause 1 each of these **is** rewritten, to
    # its family index's section for the source; the population is still carried by name
    # because the reader who follows one of those links is the person who has to choose.
    index_resolved_split_citations: tuple[_UnresolvedCitation, ...] = ()
    # The citations of a split source left exactly as they were. **0 by construction**
    # (Ruling 101 clause 1: the family-index fallback is always available), and reported
    # anyway, because "0 by construction" is a claim about the code and this is the
    # measurement of it — the two have come apart here before.
    unresolved_split_citations: tuple[_UnresolvedCitation, ...] = ()
    # Ruling 101 clause 3: every `INDEX.md#<anchor>` a citation was resolved to whose
    # section does not exist or lists fewer than two documents, named with the citing file
    # and the anchor. A link to an empty index section resolves at the file level, so the
    # dangling-link scanner cannot see it; this is the check that can.
    split_index_violations: tuple[str, ...] = ()
    # Ruling 105 D3/#18: every path this run generated in full (a class-6 artifact per
    # Ruling 104 §2, a property this constant records rather than lets each reader
    # re-derive) — `docs/INDEX.md`, `docs/REDIRECTS.csv`, every family README
    # `_regenerate_family_readmes` wrote, and every split-source index. Read by (f)'s
    # exclusion (`_docverify.row_f`) so a product identifier merely echoed into a
    # generated artifact is not counted as having moved, AND (W37-6 channel `:394-417`)
    # by `classify_migration_diff`'s `_try_class6`, which used to key class 6 on second-run
    # reproducibility alone — every deterministic write is reproducible, including a
    # deterministic defect — and now requires membership in this same recorded set first,
    # keeping the second-run content equality only as a second condition within it. One
    # recorded set, read by both consumers, rather than each re-deriving its own
    # (`docs/notes/0003-duplicated-status-goes-stale.md` — the copy is what goes stale).
    generated_paths: tuple[str, ...] = ()


# ---------------------------------------------------------------------------------------
# Phase A — discovery. Each function returns `_Draft`s for exactly one legacy shape, never
# touching disk beyond reading it.
# ---------------------------------------------------------------------------------------

_FAMILY_RANK: Final[Mapping[str, int]] = {
    prefix: rank for rank, prefix in enumerate(_docid.FAMILY_PREFIXES)
}


def _line_span(text: str, start: int, end: int) -> tuple[int, int]:
    """The 1-based, inclusive line range `text[start:end]` occupies in `text`.

    `end` is the *exclusive* character offset the splitters already compute (the next
    record's heading start, or `len(text)`), and it almost always sits at the beginning of
    a line — the first line of the *next* record. The last line of this record is
    therefore the line containing `end - 1`, which is what this returns; a zero-length
    slice degenerates to `(line, line - 1)`, an empty range, rather than silently claiming
    the next record's first line.
    """
    first = text.count("\n", 0, start) + 1
    last = text.count("\n", 0, max(start, end - 1)) + 1 if end > start else first - 1
    return (first, last)

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
                    source_line_span=_line_span(text, start, end),
                )
            )
    return drafts


#: Ruling 86 (`docs/plans/2026-09-02-w37-ruling-a-series-and-standalone-ruling-files.md`,
#: PR #598): `### Ruling A1`, `A2` and `A3` in `docs/plans/2026-08-30-nt-0012-0013-0014-
#: adoption.md` are three `RL-` records. `_RULING_HEADING_RE` misses them on **two
#: independent axes** — its `^##` cannot see a `###` heading and its `(\d+)` cannot see the
#: `A1` token — and Ruling 86 §3 item 1 names that pair explicitly: *"A fix to either alone
#: reds nothing and looks green."* This pattern is level-independent and letter-led, so
#: neither axis is left half-fixed.
#:
#: **`[A-Za-z]+\d+`, not `\S+`.** Ruling 86 §2 reads the `A` as a delegation marker in
#: front of a real number (*"marking authorship under delegation rather than absence of a
#: number, evidenced by the numbered sequence running to 48 and 53 the same day"*), so the
#: token this splits on is a letter prefix followed by a number, and nothing else. That
#: matters in the other direction too: a `Ruling`-anchored heading in some third shape —
#: say a bare `### Ruling B` — is deliberately **not** matched here, so
#: `_check_multi_ruling_files_not_silently_unrecognised` names it as unaccounted instead of
#: this function guessing at a record for it. A widened `\S+` would silently swallow it,
#: which is the exact class of defect Ruling 83's census exists to prevent.
#:
#: **The token is the constraint; the punctuation after it is not.** `_RULING_HEADING_RE`
#: makes its title trailer an optional `—`-introduced group, so a heading written with `--`
#: instead of an em dash matches *nothing* there and falls out of the record set silently.
#: Here everything after the token is captured and the separator stripped afterwards, so a
#: record cannot stop being a record because someone typed a different dash — the same
#: lesson Ruling 93 records for heading levels, applied to punctuation.
_LETTERED_RULING_HEADING_RE: Final = re.compile(
    r"^(#{1,6})[ \t]+Ruling[ \t]+([A-Za-z]+\d+)[ \t]*(.*)$", re.MULTILINE
)


def _discover_lettered_rulings(root: Path) -> list[_Draft]:
    """Ruling 86's A-series: one `RL-` per letter-suffixed `Ruling <letter><n>` heading in
    a dated `docs/plans/` file. `status: active`, `created:` the filename date, `was:` the
    source file's path and `old_token:` the heading's own `Ruling A<n>` — every field as
    Ruling 86 §2 fixes it, `owner:` from `_RULING_DEFAULT_OWNER` per Ruling 95.

    **Why this is a sibling of `_discover_multi_ruling_files` rather than a widening of
    it.** Widening `_RULING_HEADING_RE` on the two axes would also make
    `_discover_plain_plans` skip the adoption file (it delegates any file that pattern
    matches), and the whole file would migrate as three `RL-` records with no plan left
    behind. Ruling 86 §3 item 5 forbids that outcome by requiring the opposite: *"The
    residual `PL-` is checked for sense: after §3's subsections leave, its §3 heading has
    nothing under it."* A residual `PL-` is only possible if the file stays a plain plan,
    so the records are **extracted from** a document that survives, not **split out of** one
    that does not. That is the one structural difference from
    `_discover_multi_ruling_files`, and it is why no preamble folds into the first record
    here: the preamble belongs to the surviving plan.

    **The section close.** A record ends at the next heading of its own level or shallower
    — `### Ruling A3` ends at `## 4. Acceptance …`, not at end of file. Unlike
    `plan-reviews.md` (Ruling 88 §3 item 1, Ruling 93), where records are top-level
    siblings and a level-derived close swallows the records after it, these records are
    *nested inside* a section of a larger document that has real headings above and below
    them. There is no "next record" to close A3, and the enclosing structure is the only
    thing that says where §3 ends. The distinction is between using a heading level as an
    identifier (which Ruling 93 rejects, and which this function does not do — the record
    is identified by its `Ruling A<n>` token at any depth) and reading the document's own
    nesting to find where a nested section stops.

    **Not done here, and deliberately** — Ruling 86 §3 items 3 and 5, both of which are
    about `migrate`'s *output* rather than about discovering the records: the range-form
    citation (`Rulings A1` through `A3`, written with an en dash in the corpus) is not a
    token substitution -- one citation becomes three ids -- and needs the executor's choice
    between allocating them contiguously and emitting a range, or expanding the citation;
    and the residual plan's now-empty §3 heading and its §4 table's own range citation are
    a body edit to a document this function does not write. `_rewrite_citations`' own
    `\\b`-anchored substitution leaves both untouched, so neither is silently half-done.
    Both are named in W37-5c's report rather than improvised.
    """
    drafts: list[_Draft] = []
    plans_dir = root / "docs" / "plans"
    if not plans_dir.is_dir():
        return drafts
    for path in sorted(plans_dir.glob("*.md")):
        m = _PLAN_FILENAME_RE.match(path.name)
        if m is None:
            continue  # a post-migration `PL-<n>-*.md` has no date prefix: second run finds none
        text = path.read_text(encoding="utf-8")
        headings = [
            (hm.start(), len(hm.group(1))) for hm in _CENSUS_ANY_HEADING_RE.finditer(text)
        ]
        created = date.fromisoformat(m.group(1))
        rel = path.relative_to(root).as_posix()
        for i, heading in enumerate(_LETTERED_RULING_HEADING_RE.finditer(text)):
            level = len(heading.group(1))
            token = heading.group(2)
            title = heading.group(3).lstrip(" \t—-").strip()
            end = next(
                (s for s, lv in headings if s > heading.start() and lv <= level), len(text)
            )
            drafts.append(
                _Draft(
                    materialize="document", prefix="RL", kind=None,
                    title=title or f"Ruling {token}",
                    status="active", created=created, owner=_RULING_DEFAULT_OWNER,
                    tie_break=(rel, i),
                    old_token=f"Ruling {token}", was=rel,
                    body=text[heading.start() : end].rstrip("\n") + "\n",
                    source_line_span=_line_span(text, heading.start(), end),
                )
            )
    return drafts


def _discover_headed_split_file(
    root: Path, rel_path: str, heading_re: re.Pattern[str], prefix: str, owner: str,
    *, foreign_records: Collection[int] = (),
) -> list[_Draft]:
    """`closure-records.md`/`plan-reviews.md`'s shared shape: one `###` heading per
    record, each ending in the date it closed/ran — matched only at the exact legacy path,
    so a second run (the file already moved to `docs/closures/`) finds nothing.

    Preamble (the file's own `# Title` and introductory blockquote, before the first
    `###` heading) folds into the first record's body, the identical rule
    `_discover_multi_ruling_files` uses and for the identical reason: the concatenation
    of every split output must reproduce this file's body lines in order (Ruling 68
    class 4), so no line may belong to no output.

    `foreign_records` is the set of character offsets in this same file at which *another*
    discovery function produces a record — `_discover_proposal_containers`' `RFC-`
    container in `plan-reviews.md` today. Each such offset does two things here, and both
    are Ruling 88 §3 item 1's ("the section closes at the next *record* heading, never at
    the next same-level heading"): it **ends** the preceding record's body, so the
    container's lines belong to the container rather than folding into the review above
    it, and it is **never emitted** as a record by this function even when `heading_re`
    also matches there. The second half is Ruling 93 §2's added acceptance item read from
    the other side — the container is claimed by the function that identifies it
    positively, so a container heading that came to match `_REVIEW_HEADING_RE` (three
    edits away, Ruling 93 §1(d)) still does not become a `CR- kind: review` here.
    """
    drafts: list[_Draft] = []
    path = root / rel_path
    if not path.is_file():
        return drafts
    text = path.read_text(encoding="utf-8")
    foreign = set(foreign_records)
    headings = [m for m in heading_re.finditer(text) if m.start() not in foreign]
    boundaries = sorted({*(m.start() for m in headings), *foreign, len(text)})
    for i, heading in enumerate(headings):
        title, created_str = heading.group(1).strip(), heading.group(2)
        start = heading.start() if i > 0 else 0
        end = next(b for b in boundaries if b > heading.start())
        section_text = text[start:end].rstrip("\n") + "\n"
        drafts.append(
            _Draft(
                materialize="document", prefix=prefix, kind="work",
                title=title, status="active", created=date.fromisoformat(created_str),
                owner=owner, tie_break=(rel_path, i), old_token=None, was=rel_path,
                body=section_text, source_line_span=_line_span(text, start, end),
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
                work_token=work_token, source_line_span=_line_span(text, start, end),
            )
        )
    return drafts


# ---------------------------------------------------------------------------------------
# F84 (`docs/audit/findings/F84.md`): the 17 closure records the migration cannot see.
#
# `_discover_closure_records` above reads `docs/audit/closure-records.md` and nothing
# else -- its own docstring says so ("one `###` heading per record"). The per-work and
# per-phase records living one-to-a-file under `docs/audit/work/` and
# `docs/audit/phases/` are a second location it never visits, and before this block
# `scripts/doc-id.py` carried no reference to either path at all.
#
# **Why this was worse than F80, F81 and F82 despite being smaller.** Those three abort:
# a guard refuses to migrate a governed thing it has no discovery code for, so a real
# `migrate()` run stops and names it. This one was silent -- no census covered the path,
# so the 17 were not "discovered zero and flagged", they were outside the question. The
# run completed, reported success, and left them to whatever generic rule reaches a
# `README.md`. A guard that aborts is a gap that announces itself; a population no census
# covers is a gap that does not (the asymmetry `NT-0007` records for boundary metrics).
# ---------------------------------------------------------------------------------------

#: NT-0019 §5.2's own routing, read from the row `"audit/work/*/README.md (15),
#: audit/phases/1b/README.md, audit/exit-demo-uat.md"` -> `"closures/CR-0nnnn-*.md,
#: kind: work / phase"`. The **directory decides the `kind:`**, which is what makes this
#: a routing rule rather than a filename rule -- the discriminator
#: `docs/plans/2026-09-02-w37-rfc-readme-row-and-stamp-set.md` §1 states for the README
#: row: *"A `README.md` takes the family §5.2 routes it to"*, never its filename.
#:
#: §5.2's row says 15 work READMEs where 16 now exist (16 at `544b90c`); the rule is used
#: here, not the count, which is why this survives that drift.
#:
#: **`docs/audit/exit-demo-uat.md` is in that same §5.2 row and has the same defect, and
#: is deliberately not folded in here**: it is under neither directory, and F84's
#: falsifiable section is written over 17 files. It is reported as a residual instead --
#: widening a finding's discharge past what the finding states is how a discharge stops
#: being checkable against its own text.
_AUDIT_CLOSURE_README_DIRS: Final[Mapping[str, str]] = {
    "docs/audit/work": "work",
    "docs/audit/phases": "phase",
}

#: The record heading these files actually carry, verified against all 17 at `544b90c`
#: with `grep -h '^# ' docs/audit/work/*/README.md docs/audit/phases/1b/README.md`:
#: **14** read `# Work-item record — <id> (<title>)`, **two** read `# Audit record —
#: <slug> (<clause>)` (`nt-0010-0011-adoption`, `nt-0012-0013-0014-adoption`) and **one**
#: reads `# Phase record — 1b (Modelling Workbench)`. F84's own prose says their headings
#: read *"`# Work-item record — W11`, `# Phase record — 1b`"*; that is true of 15 of the
#: 17, and the two `# Audit record —` files are the exception the finding does not name.
#: Matching the three forms rather than the one is what keeps all 17 discovered.
#:
#: **Matched, never assumed from the path.** A file under these directories whose H1 is
#: none of the three forms is deliberately *not* claimed: `title:` would have to be
#: invented, and the census below naming it is better than this function guessing -- the
#: identical reading `_proposal_containers` gives a container heading with no date.
_AUDIT_CLOSURE_TITLE_RE: Final = re.compile(
    r"^#[ \t]+((?:Work-item|Audit|Phase)[ \t]+record[ \t]+—[ \t]+\S.*?)[ \t]*$", re.MULTILINE
)


def _discover_audit_closure_readmes(root: Path) -> list[_Draft]:
    """The per-record closure documents NT-0019 §5.2 routes to `closures/CR-0nnnn-*.md`,
    `kind: work` / `kind: phase` -- `docs/audit/work/<work>/README.md` (16 at `544b90c`)
    and `docs/audit/phases/<phase>/README.md` (1). F84's first limb.

    `owner: auditor` is §1.6's `CR` row read from the cell
    (`docs/notes/0019-one-id-per-document.md:152`, mirrored at
    `docs/process/document-ids.md:157`): *"auditor (`work`, `phase`); lead (`review`)"*.
    Neither of the two kinds this function produces is `review`, so the value is uniform
    and is not derived from what a role ought to own.

    `status: active` is §1.2's `CR` row -- write-once, `active` its only value for the
    family's whole life -- the same value `_discover_closure_records` assigns its own
    `CR-` drafts.

    `created:` is the file's git first-commit date: NT-0019 §4 step 1's own rule for a
    document carrying no date of its own (*"git first-commit date otherwise"*), through
    the same `_module_first_commit_date` call `_discover_register` already makes for the
    register, which likewise has no date in its text.

    Idempotent for the reason every other document discovery here is: the file moves to
    `docs/closures/` and its source is deleted by `_write_document_drafts`, so a second
    run's `*/README.md` glob finds nothing to claim.
    """
    drafts: list[_Draft] = []
    for rel_dir, kind in _AUDIT_CLOSURE_README_DIRS.items():
        directory = root / rel_dir
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*/README.md")):
            text = path.read_text(encoding="utf-8")
            title_match = _AUDIT_CLOSURE_TITLE_RE.search(text)
            if title_match is None:
                continue  # left for the census below to NAME, never guessed at
            rel_path = path.relative_to(root).as_posix()
            drafts.append(
                _Draft(
                    materialize="document", prefix="CR", kind=kind,
                    title=title_match.group(1), status="active",
                    created=_module_first_commit_date(path, root), owner="auditor",
                    tie_break=(rel_path, 0), old_token=None, was=rel_path,
                    body=text,
                )
            )
    return drafts


_PLAN_REVIEWS_REL_PATH: Final = "docs/audit/plan-reviews.md"

#: Ruling 88 (`docs/plans/2026-09-02-w37-container-family-and-line-citations-rulings.md`,
#: PR #601): `docs/audit/plan-reviews.md`'s "Pending proposals" section is a record in its
#: own right -- `RFC-`, `kind: process`, `status: closed`, `owner: maintainer` -- not
#: preamble to the review that follows it. Ruling 89 §1 held that *stamping* it happens
#: during W37-6; F82's sibling finding F80 is that no code built the draft at all, so
#: `_check_plan_reviews_heading_census` correctly aborted `migrate` on it. This is that
#: code.
#:
#: **The container is identified positively, never by `_REVIEW_HEADING_RE` failing to
#: match it** — Ruling 93 §2's added acceptance item, in its own words: *"A negative test
#: says 'this `###` is not a review', which is true today by three edits (§1(d)) and would
#: silently reclassify the container into a `CR- kind: review` if any of them were ever
#: made."* What is matched here is the section's own content: its name, and the
#: `(drafted <date>)` trailer that carries the `created:` Ruling 88 §2 fixes at
#: `2026-08-29`. The date is read from the heading rather than written in as a constant so
#: the field is a property of the document, not of this line.
#:
#: **Level-independent by construction** (`#{1,6}`, not `###`). PR #609 demoted this exact
#: heading from `##` to `###` and in doing so invalidated a heading-level fixture — the
#: whole subject of Ruling 93. A pattern pinned to a level would have to be re-cut by the
#: next such restructure and would read as correct until someone ran it; this one does not
#: change under any demotion or promotion of the heading.
#:
#: **Punctuation-independent too, and that is Ruling 93's acceptance item rather than
#: tidiness.** The item's fixture is *"the container's heading edited to match the review
#: pattern, and the classifier must still produce an `RFC-`"* — the three edits Ruling 93
#: §1(d) measured are adding a comma, removing the parenthesis and removing the word
#: "drafted". A pattern that required the literal `(drafted <date>)` would stop claiming
#: the heading under exactly that fixture and hand it to `_REVIEW_HEADING_RE`, which is the
#: reclassification the item exists to forbid. So the section is claimed on its **name**,
#: and the date is read from wherever in the heading it sits.
#:
#: A heading that names the container but carries no date at all is deliberately **not**
#: claimed: `created:` would have to be invented, and Ruling 83's census naming it is
#: better than this function guessing.
#:
#: Precedent for matching a distinctive title rather than a position or a level:
#: `_CLOSURE_AUDIT_TITLE_PREFIXES` above, and for the identical stated reason.
_PROPOSAL_CONTAINER_RE: Final = re.compile(r"^#{1,6}[ \t]+(Pending proposals\b.*)$", re.MULTILINE)

#: The trailing date the heading carries, in either the corpus's own `(drafted <date>)`
#: form or the `, <date>` form Ruling 93's acceptance fixture edits it into. Stripped from
#: the record's `title:` so the same section produces the same title under both.
_PROPOSAL_CONTAINER_DATE_RE: Final = re.compile(
    r"[ \t]*[(,]?[ \t]*(?:drafted[ \t]+)?(\d{4}-\d{2}-\d{2})\)?[ \t]*$"
)


def _proposal_containers(text: str) -> list[tuple[re.Match[str], str, date]]:
    """`(heading match, title, created)` for every "Pending proposals" container in `text`.
    One definition, shared by the discovery function below, by `_discover_plan_reviews`'
    boundary set and by both censuses over this file, so "which offsets are the
    container's" is never computed twice and cannot drift (Ruling 67 §2).
    """
    out: list[tuple[re.Match[str], str, date]] = []
    for m in _PROPOSAL_CONTAINER_RE.finditer(text):
        dated = _PROPOSAL_CONTAINER_DATE_RE.search(m.group(1))
        if dated is None:
            continue  # no `created:` to read -- left for the census to name, not guessed
        title = m.group(1)[: dated.start()].rstrip(" \t,—-")
        out.append((m, title, date.fromisoformat(dated.group(1))))
    return out


def _proposal_container_starts(text: str) -> set[int]:
    """The character offsets `_proposal_containers` claims in `text`."""
    return {m.start() for m, _title, _created in _proposal_containers(text)}


def _discover_proposal_containers(root: Path) -> list[_Draft]:
    """Ruling 88's `RFC-` container in `docs/audit/plan-reviews.md`, one draft per
    `_PROPOSAL_CONTAINER_RE` match.

    The section **closes at the next record heading, never at the next same-level
    heading** — Ruling 88 §3 item 1, which states the trap explicitly: *"The file has
    exactly one level-2 heading, so 'from the `##` to the next `##`' yields 1155 to end of
    file — swallowing Plan reviews 9, 10 and 11."* After PR #609's demotion the trap is
    strictly worse, not better (Ruling 93 §2: with zero level-2 headings a *"to the next
    `##`"* rule runs to end of file from **any** starting point), which is why the
    boundary below is computed from the other discovery function's record offsets rather
    than from any heading depth.

    Ruling 88 §3 item 5: the three `####` candidates stay body inside this record — they
    are inside the span this function slices, and no separate draft is minted for them.
    """
    path = root / _PLAN_REVIEWS_REL_PATH
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    container_starts = _proposal_container_starts(text)
    record_starts = sorted(
        {
            *container_starts,
            *(m.start() for m in _REVIEW_HEADING_RE.finditer(text)),
            len(text),
        }
    )
    drafts: list[_Draft] = []
    for i, (m, title, created) in enumerate(_proposal_containers(text)):
        end = next(b for b in record_starts if b > m.start())
        drafts.append(
            _Draft(
                materialize="document", prefix="RFC", kind="process",
                title=title, status="closed",
                created=created, owner="maintainer",
                tie_break=(_PLAN_REVIEWS_REL_PATH, i), old_token=None,
                was=_PLAN_REVIEWS_REL_PATH,
                body=text[m.start() : end].rstrip("\n") + "\n",
                source_line_span=_line_span(text, m.start(), end),
            )
        )
    return drafts


def _discover_plan_reviews(root: Path) -> list[_Draft]:
    """`docs/audit/plan-reviews.md`, via the shared `_discover_headed_split_file` --
    unlike `_discover_closure_records` above, this file's *review* headings carry no
    per-record semantic variation that splitter cannot express (no phase/audit
    distinction, nothing left mid-flight), so it still delegates rather than growing its
    own loop. The one record in the file that is not a review is not squeezed into that
    delegation either: `_discover_proposal_containers` above owns it, and this function
    passes its offsets in as `foreign_records` so the two agree on where each section ends
    and neither claims the other's heading.

    Ruling 82: three of the file's headings carry no date at all ("Candidate A",
    "Candidate B", "Also carried, and not a new rule") and so never match
    `_REVIEW_HEADING_RE` regardless of the trailing-anchor fix below -- they are ruled
    sub-content of the "Pending proposals" container, not independent records. Ruling 88
    has since ruled that container's own family and `kind:` (`RFC-`, `kind: process`),
    and PR #609 demoted the three from `###` to `####`; both are now handled -- the
    container is a record of its own and the three sit inside its body, which is Ruling 88
    §3 item 5's requirement in both directions ("none minted as a record, none dropped").

    Before that, they folded into whichever matched heading preceded them in the file
    (sections run heading-to-heading), the same way an unmatched heading always has --
    `_discover_headed_split_file` itself has no accounting step that would notice a
    heading count short of the file's own `###` total, unlike `_discover_closure_records`'s
    bespoke loop. That was never silent at the `migrate` level:
    `_check_plan_reviews_heading_census` below independently re-scans this same file and
    refuses rather than let the fold complete unremarked (Ruling 83, row 1 of the W37-5b
    obligations list) -- which is exactly how F80 was found.
    """
    path = root / _PLAN_REVIEWS_REL_PATH
    container_starts: set[int] = set()
    if path.is_file():
        container_starts = _proposal_container_starts(path.read_text(encoding="utf-8"))
    drafts = _discover_headed_split_file(
        root, _PLAN_REVIEWS_REL_PATH, _REVIEW_HEADING_RE, "CR", "lead",
        foreign_records=container_starts,
    )
    for d in drafts:
        d.kind = "review"
    return [*drafts, *_discover_proposal_containers(root)]


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
    3. **a declared exception** -- **still none, and that is now the finished state**
       rather than a gap. Ruling 82 found the three undated headings ("Candidate A",
       "Candidate B", "Also carried, and not a new rule") and their parent ("Pending
       proposals") sub-content, not records. Ruling 88 then ruled the container's family
       (`RFC-`, `kind: process`, `status: closed`, `owner:` the maintainer), and
       `_discover_proposal_containers` now builds that draft -- so the container is a
       **bucket 1** record here, matched through `_proposal_container_starts` rather
       than through `_REVIEW_HEADING_RE`, and its three children are **bucket 2** body
       below the split level. PR #609's demotion is what makes bucket 3 stay empty:
       Ruling 93 §1(c) shows the census closing with nothing declared, and Ruling 83 §2
       holds that a bucket-3 entry *"that could have been derived is a defect in the fix
       rather than in the corpus"*.

    Anything left over is named, by line number and heading text -- never a bare count
    (Ruling 83 §3 item 4) -- and `migrate` refuses. Until `_discover_proposal_containers`
    landed, the leftover was exactly Ruling 82/88's container: ruled but not implemented,
    which is register finding F80 and which this function is how anyone found out.

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
    record_starts |= _proposal_container_starts(text)  # Ruling 88's `RFC-` (F80)
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
            f"record or as derived body: {named}. The two record matchers over this file "
            f"are _REVIEW_HEADING_RE (a plan review) and _PROPOSAL_CONTAINER_RE (Ruling "
            f"88's RFC- container); a heading that is neither, and is not below the split "
            f"level, has no discovery code -- rule its disposition and implement it "
            f"before migrating this file."
        )


#: Ruling 98 §2.1 (`docs/plans/2026-09-03-w37-6-ruling-98-prose-migration.md`): a document
#: filed under `docs/plans/` **whose entire content is a decision the maintainer made and
#: dated**, carrying no `## Ruling N` heading, migrates as `RL-`, `owner: maintainer`, with
#: **no `kind:` field** (`docs/_templates/RL.md:8` forbids the field on this family). The
#: cells the ruling reads from are NT-0019 §1.13 (`docs/notes/0019-one-id-per-document.md:
#: 238`, *"maintainer decisions and phase pre-decisions → `RL-` with `owner: maintainer`"*)
#: and §1.6's `RL` row (`:149`, *"the maintainer may author one on scope or process"*).
#:
#: **Attribution is read from the document's own title, not its filename and not its
#: prose body.** Ruling 98 §1 reconciles two sweeps and settles the population by reading
#: each file's *own attribution*; the title is where every member of that population states
#: it, and it is the one region of a plan-shaped document that cannot also be quoting or
#: citing somebody else's decision.
#:
#: **The predicate is `_MAINTAINER_DECISION_TITLE_RE` below, by symbol, and no paraphrase of
#: it belongs here** (`CLAUDE.md` §13: a count carries "the pattern or command verbatim and
#: runnable, or the shipped constant by symbol at that tree, never pasted"). Applied to the
#: first `^# ` line of each of the **168** `docs/plans/*.md` files at `198ea5d`, it matches
#: **nine**: Ruling 98's own seven, plus Ruling 98's own record — which carries a
#: `## Ruling 98` heading and so never reaches this function at all — plus
#: `2026-09-03-w37-6-maintainer-decisions.md`, which the blank-`Decision` clause of
#: `_is_maintainer_decision_plan` excludes.
#:
#: **This comment previously stated the predicate as
#: `grep -m1 '^# ' | grep -c "maintainer's"` and the count as eight, and both were wrong in
#: the same way.** That grep drops three properties the shipped regex has — the
#: `reserved to the maintainer` alternative, `re.IGNORECASE`, and the typographic
#: apostrophe — so it cannot match `2026-09-03-w37-6-maintainer-decisions.md`, whose title
#: reads "Reserved to the maintainer". Two predicates over the same corpus at the same tree
#: differing by one unit is precisely the failure `CLAUDE.md` §13's predicate clause was
#: added to stop (register finding F85); it is recorded here rather than quietly corrected,
#: because a stated predicate that is not the shipped predicate is the defect, not the count.
#:
#: Prose-
#: body matching was measured and rejected: `by the maintainer` in the first six lines also
#: catches the three SDD ledgers' provenance line (*"Decision gate answered by the
#: maintainer before execution"*), and `the maintainer's` anywhere in the preamble also
#: catches `2026-09-02-w37-5c-slice-decision.md`, `2026-09-02-w37-rfc-readme-row-and-stamp-
#: set.md` and `2026-08-30-nt-0012-0013-0014-adoption.md` — every one of which Ruling 98 §1
#: rules **out** of the population, on its own stated authorship.
#:
#: **Limit, stated rather than hidden** (Ruling 98 §1, *"Limits carried forward, not
#: dropped"*): a maintainer decision filed under a title that does not name the maintainer
#: would not be caught here. That is the same limit both of the ruling's own sweeps carry,
#: and it is why this is a predicate over content rather than a list of seven filenames
#: (acceptance item 5) — a *new* document titled this way is routed with no code change.
_MAINTAINER_DECISION_TITLE_RE: Final = re.compile(
    r"the maintainer(?:'|\u2019)s\b|reserved to the maintainer\b", re.IGNORECASE
)

#: Ruling 98 §2.2: the exclusion of `docs/plans/2026-09-03-w37-6-maintainer-decisions.md`
#: is **a state of one tree, not a property of the file** — *"the predicate in §2.1 tests
#: content at the tree in question, never a title and never a past reading of that
#: content"*. That file is a planner-assembled batch of `> **Decision:**` / `> **Date:**`
#: blocks reserved to the maintainer; while any block is still blank it is awaiting a
#: decision rather than recording one, so it keeps the shipped `PL- kind: leaf, owner:
#: planner` default. The moment the maintainer fills them in, the document *is* what §2.1
#: describes and this predicate routes it to `RL-`/`maintainer` with no code change —
#: which is the second direction of acceptance item 4, the one a frozen reading of
#: `e56d038` would have got wrong.
_UNFILLED_DECISION_BLOCK_RE: Final = re.compile(r"^>\s*\*\*Decision:\*\*[ \t]*$", re.MULTILINE)


def _is_maintainer_decision_plan(title: str, text: str) -> bool:
    """Ruling 98 §2.1's predicate, evaluated **at the tree `migrate` runs on** (the ruling
    states this once, in §1's introduction, and repeats it in §2.2 and §3): does this
    plan-shaped document's own content make it a decision the maintainer made and dated?

    Two clauses, both required, and each one is why a specific member of Ruling 98 §1's
    reconciliation table lands where it does:

    1. **The document's title attributes the decision to the maintainer** — see
       `_MAINTAINER_DECISION_TITLE_RE` for what that matches and what it deliberately does
       not. This is what excludes the two handovers (Ruling 98 §1's second independent
       route to the same answer; `_plan_kind_for_slug`'s `-handover` suffix is the first,
       and it still fires below because this clause is false for them).
    2. **The document is not still awaiting that decision** — no `> **Decision:**` block
       is left blank. See `_UNFILLED_DECISION_BLOCK_RE`.
    """
    if not _MAINTAINER_DECISION_TITLE_RE.search(title):
        return False
    return not _UNFILLED_DECISION_BLOCK_RE.search(text)


def _discover_plain_plans(root: Path) -> list[_Draft]:
    """Every remaining `YYYY-MM-DD-*.md` file directly under `docs/plans/` that is *not*
    a multi-ruling file (those are `_discover_multi_ruling_files`'s) — `kind:` from its
    filename suffix (NT-0019 §5.2). Matched on the date-prefixed legacy filename only, so
    an already-migrated `PL-<n>-*.md` (no date prefix) is invisible to a second run.

    **Ruling 98 §2.1 sits ahead of that suffix fallback**, not inside it: a file whose own
    content is the maintainer's dated decision leaves here as `RL-`, `owner: maintainer`,
    no `kind:`. Until this branch existed, the suffix table was unconditional and every one
    of those documents was stamped `owner: planner` — the misattribution Ruling 98 §2.1(b)
    names as *"the status quo the ruling overrides"*, measured at `2ae31f7` as seven of
    seven. `_is_maintainer_decision_plan` carries the predicate and its limits.
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
        kind: str | None = _plan_kind_for_slug(slug)
        title = _plan_title(text) or slug
        prefix, owner = "PL", _PLAN_KIND_OWNER[kind]
        # Ruling 98 §2.1, ahead of the suffix fallback and deliberately *not* a second
        # `_Draft` construction: the `was:`/body carriers below are the anchors two
        # mutation proofs edit (`_WAS_DROPPED`/`_BODY_DROPPED` in
        # `tests/test_doc_id_migrate.py`, which assert each literal occurs exactly once),
        # and a copied constructor would leave one writer unmutated and green.
        if _is_maintainer_decision_plan(title, text):
            prefix, kind, owner = "RL", None, "maintainer"
        drafts.append(
            _Draft(
                materialize="document", prefix=prefix, kind=kind, title=title,
                status="active", created=created, owner=owner,
                tie_break=(path.relative_to(root).as_posix(), 0),
                old_token=None, was=path.relative_to(root).as_posix(),
                body=text.rstrip("\n") + "\n",
                source_line_span=_line_span(text, 0, len(text)),
            )
        )
    return drafts


_LEGACY_SPEC_BOLD_RE: Final = re.compile(r"\*\*(FR|NFR|DEP|OQ)-([A-Z]+)-(\d+)\*\*")

# Ruling 83's independent, form-agnostic unit finder for a requirement id: a bold span
# opening with one of the four prefixes and closing right after the id, with **no**
# assumption about a module code or a number shape. Hoisted here from
# `_check_requirements_not_silently_unrecognised` below (its only reader until F82) so it
# sits beside the two patterns it has to be reconciled against.
#
# **Widened from `DEP`-only to all four prefixes**, which that guard's own docstring said
# it could not be: broadening `FR`/`NFR`/`OQ` the module-optional way "would make this
# guard fire on `migrate`'s own second-run output and break idempotency", since their
# post-migration form is module-less. That is no longer true, because the guard now
# classifies an already-canonical id into bucket 2 (`_SPEC_BOLD_RE`, checked positively).
# With the collision resolved, keeping the finder narrow would only mean three prefixes'
# malformed ids going unnamed. Measured at `ba31cd1`: the widened finder names nothing new
# in the real corpus -- `**DEP-1a**` is the only bold id in `docs/specs/` that is neither
# module-coded nor canonical.
_CENSUS_BARE_ID_RE: Final = re.compile(
    r"\*\*(FR|NFR|DEP|OQ)-([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\*\*"
)

#: A legacy id's number: digit-led, optionally carrying an amendment suffix (`1a`). What
#: makes a requirement id a requirement id is that it has a **number**; `_legacy_bare_dep_
#: ids` uses this rather than a pattern fitted to the one such id in the corpus, so a
#: module-less span with no number at all (`**DEP-abc**`) is *not* silently claimed as a
#: record -- it is left for the census to name, which is what keeps that census able to
#: fail at all.
_LEGACY_NUMBER_RE: Final = re.compile(r"^\d+[A-Za-z0-9]*$")


def _legacy_bare_dep_ids(text: str) -> list[re.Match[str]]:
    """Every module-less bold `DEP-` id in `text` with a digit-led number that is
    **neither** already in the canonical post-migration form `_SPEC_BOLD_RE` reads **nor**
    in the module-coded legacy form `_LEGACY_SPEC_BOLD_RE` already claims. Register finding
    F82's population, derived from the patterns either side of it rather than written out
    as a third pattern fitted to the four ids that happen to be in the corpus today.

    **`DEP` only, not all four prefixes** -- unlike the census finder above, which is
    deliberately form-agnostic. NT-0019 §1.2 makes `DEP` a requirement family with living,
    append-only ids, and §5.1's `.importlinter` row names the outcome outright
    (*"`ADR-0001`/`ADR-0002`/`DEP-3` → `ADR-1`/`ADR-2`/`DEP-n`"*), so a module-less `DEP`
    id is a legacy id to be migrated. No ruling says the same of a module-less
    `**FR-12a**`, and inventing one here would be the silent widening F82 warns against;
    the census names such a span instead.

    **This is why three of F82's four are not here.** `docs/specs/00-overview.md` §7
    defines `DEP-1`, `DEP-1a`, `DEP-2` and `DEP-3`. Three of them — `DEP-1`, `DEP-2`,
    `DEP-3` — are *already* in the canonical form: `_SPEC_BOLD_RE` matches them, and
    `compute_next` therefore already counts them as allocated ids. Measured at `ba31cd1`,
    `compute_next(<repo root>) == 4`, and those three are the **only** ids any of NT-0019
    §1.7's four sources can see in the whole tree — so the migration's own allocation
    already starts immediately above them. Discovering them would mean allocating numbers
    out of a range computed *from* the very ids being vacated, leaving 1-3 orphaned; it
    would also make a second run re-migrate its own output, since a reallocated `**DEP-<n>**`
    is indistinguishable from a legacy one. Treating an already-canonical id as
    already-migrated is the same positively-checked idempotency reading
    `_check_plain_plans_not_silently_unrecognised` and
    `_check_flat_document_directory_not_silently_unrecognised` already apply via
    `_docid.ID_RE`, and it is checked positively here for the same reason Ruling 83 gives:
    never "the legacy pattern found nothing".

    `**DEP-1a**` is the one that is genuinely un-migrated. `_SPEC_BOLD_RE`'s `(\\d+)` cannot
    express the `1a` suffix, so `compute_next` has never seen it and it has no number in the
    global sequence at all. It is discovered, allocated one, and rewritten like any other
    legacy requirement id.
    """
    claimed = {m.start() for m in _SPEC_BOLD_RE.finditer(text)}
    claimed |= {m.start() for m in _LEGACY_SPEC_BOLD_RE.finditer(text)}
    return [
        m
        for m in _CENSUS_BARE_ID_RE.finditer(text)
        if m.group(1) == "DEP"
        and m.start() not in claimed
        and _LEGACY_NUMBER_RE.match(m.group(2))
    ]


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

    **One draft per distinct legacy id, never one per occurrence.** `_LEGACY_SPEC_BOLD_RE`
    is a bare `finditer` with no anchor to a row's own leading cell, so it matches every
    bold-formatted mention of the shape, definition or not — an `OQ` id in particular is
    routinely *cited* in bold from another requirement's own body prose (`FR-MODEL-88`
    reads *"...raised as **OQ-MODEL-23** with options..."*) as well as *defined* in its
    owning spec's §10 mirror row (`~~**OQ-MODEL-23**~~ ✔ | ...`). Before this guard, both
    matches became independent drafts sharing one `old_token` and got assigned two
    *different* new numbers — `docs/REDIRECTS.csv` then carried two `old_id="OQ-MODEL-23"`
    rows (`-> OQ-1060` and `-> OQ-1066` in one measured run), and the tree-wide citation
    sweep, keyed on `old_token` alone, had to choose between them (or leave the token
    ambiguous and un-rewritten, depending on which mangling era measured it — see
    `_compound_token_re`'s own docstring for the id-fabrication defect this sat beside).
    `_write_redirects` refuses a genuine second row for the same `old_id` outright now
    (belt-and-suspenders); this is the root fix, so the second draft is never produced at
    all. `_seen` is keyed on the id text alone, checked in the loop's own file-then-position
    order, so whichever occurrence is textually first wins the slot — which one wins does
    not change what the tree-wide sweep rewrites, since every occurrence of that id text,
    definition or citation, gets the same one new number regardless of which draft claimed
    it.
    """
    drafts: list[_Draft] = []
    specs_dir = root / "docs" / "specs"
    if not specs_dir.is_dir():
        return drafts
    seen: set[str] = set()
    for path in sorted(specs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        module_date = _module_first_commit_date(path, root)
        # Clause order within the file is the tie-break, so the two matchers' output is
        # merged by character offset rather than concatenated -- a module-less `DEP` id
        # defined between two module-coded ones must number between them, not after them.
        legacy = sorted(
            [*_LEGACY_SPEC_BOLD_RE.finditer(text), *_legacy_bare_dep_ids(text)],
            key=lambda match: match.start(),
        )
        for i, m in enumerate(legacy):
            if m.re is _LEGACY_SPEC_BOLD_RE:
                prefix = m.group(1)
                title = f"{prefix}-{m.group(2)}-{m.group(3)}"
            else:
                # F82: module-less by design. `_CENSUS_BARE_ID_RE` group 1 is the prefix
                # and group 2 the id body -- not group 1, which is the number in
                # `_LEGACY_SPEC_BOLD_RE`'s numbering.
                prefix = m.group(1)
                title = f"{prefix}-{m.group(2)}"
            if title in seen:
                continue
            seen.add(title)
            drafts.append(
                _Draft(
                    materialize="requirement", prefix=prefix, kind=None, title=title,
                    status="active", created=module_date, owner="decision-maker",
                    tie_break=(path.relative_to(root).as_posix(), i),
                    # The legacy id and the record's title are the same string in both
                    # branches; built once above so a module-less `DEP` can never pick up
                    # a stale module code from a previous iteration of this loop.
                    old_token=title,
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

#: `docs/audit/phases/1b/register.md`'s 11 findings, `(short-form Finding-id, description
#: source)` -- NT-0019 §5.2's register row ("the phase register's rows merge in with
#: `phase: P1b`") and the maintainer's 2026-09-03 ruling that folds all 11 in, F12
#: included, and deletes the file (NT-0019 §1.4 line 100's dissolution, and `:95`'s "per-
#: phase views are generated, never files"). Every id's description below is a *mechanical
#: prefix* of that row's own Concerns cell -- truncated at the first of `(`, `—` or `;`,
#: whole text kept verbatim when none of those appear -- never composed prose, so it can
#: be checked against the source rather than trusted. Held out of the 14-id overlap with
#: `docs/audit/register.md` (F6-F9, F13-F22): those already exist there with their own
#: Phase value (some `1b`, some carried forward to `2`/`2/3/4`) and are untouched.
_PHASE_1B_MERGE_IDS: Final[tuple[str, ...]] = (
    "F1", "F2", "F3", "F4", "F5", "F10", "F11", "F12", "F23", "F24", "F25",
)


def _phase1b_row_description(concerns: str) -> str:
    """The mechanical truncation rule stated in `_PHASE_1B_MERGE_IDS`'s own comment: the
    text up to (not including) the first `(`, `—` or `;`, stripped -- or the whole
    (stripped) text when none of the three appears. A prefix of existing text, never a
    composed one.
    """
    positions = [p for p in (concerns.find("("), concerns.find("—"), concerns.find(";")) if p != -1]
    if not positions:
        return concerns.strip()
    return concerns[: min(positions)].strip()


def _merge_phase1b_register(root: Path) -> str | None:
    """Merges `docs/audit/phases/1b/register.md`'s 11 rows into `docs/audit/register.md`'s
    own table, as `_PHASE_1B_MERGE_IDS` states, then deletes the phase register -- run
    *before* `_discover_register`/`_discover_findings` read `docs/audit/register.md`, so
    the merged rows are ordinary register content by the time either function sees them
    (no separate materialize kind; they get real `FD-` numbers through the identical path
    every other register row does). A no-op, idempotent, once the phase file no longer
    exists -- the second-run reading every other legacy-path `_discover_*` gives its own
    source file.

    Returns the deleted file's repo-relative posix path when it deletes one, `None`
    otherwise (already-migrated) -- the caller uses this to record the deletion in
    `MigrateResult.files_deleted`, add a `REDIRECTS.csv` row, and add the old path as a
    citation-rewrite token, none of which this function does itself (it edits
    `docs/audit/register.md` in place, which is not one of `migrate()`'s usual write
    points, so nothing else would otherwise learn a deletion happened here).

    Each new row's Work-item cell is the source row's own third field when the row splits
    into 4 fields (`Finding id | Concerns | Work item | Decision`), or `—` — the main
    register's own existing notation for "no work item", used on roughly 15 rows there
    already — when the source row splits into only 3 (F23, F24, F25 carry no Work-item
    cell at all in the phase file; a structural drift in that table, not a formatting
    choice, filed as its own finding rather than silently patched over).

    Parses with `register_lint._split_row` directly, never `parse_register`:
    `parse_register` enforces exactly 5 fields (the *main* register's own grammar) and
    would classify every one of this file's 4-field rows — and both of its 3-field ones —
    as a structural problem, returning zero real `Row`s for a file this function's whole
    job is to read. `_split_row` is the shared primitive both grammars are built from
    (unescaped-`|` splitting, escaped pipes restored after), so reusing it rather than
    reimplementing it keeps the two readings from silently drifting apart the way Ruling
    67 §2 already warns a second copy of "a legacy form" will.
    """
    phase1b_path = root / "docs" / "audit" / "phases" / "1b" / "register.md"
    if not phase1b_path.is_file():
        return None
    register_lint = _load_register_lint()
    by_id: dict[str, list[str]] = {}
    for line in phase1b_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        fields = register_lint._split_row(line)
        if fields and fields[0] in _PHASE_1B_MERGE_IDS:
            by_id[fields[0]] = fields
    new_lines: list[str] = []
    for token in _PHASE_1B_MERGE_IDS:
        fields = by_id.get(token)
        if fields is None:
            continue
        if len(fields) == 4:
            _, concerns, work_item, decision = fields
        elif len(fields) == 3:
            _, concerns, decision = fields
            work_item = "—"
        else:
            raise ValueError(
                f"docs/audit/phases/1b/register.md: {token}'s row splits into "
                f"{len(fields)} fields, neither 3 nor 4 -- refusing to guess which are "
                "Concerns/Work item/Decision"
            )
        description = _phase1b_row_description(concerns)
        cell = f"{description} ({token})" if description else f"({token})"
        new_lines.append(f"| {cell} | {concerns} | {work_item} | 1b | {decision} |")

    register_path = root / "docs" / "audit" / "register.md"
    text = register_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    last_table_line = max(i for i, ln in enumerate(lines) if ln.startswith("|"))
    lines[last_table_line + 1 : last_table_line + 1] = new_lines
    register_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    deleted_rel = phase1b_path.relative_to(root).as_posix()
    phase1b_path.unlink()
    _remove_if_empty(phase1b_path.parent)
    return deleted_rel


def _discover_register(root: Path, *, exclude: Collection[str] = ()) -> list[_Draft]:
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

    `exclude` names the bare `F<n>` tokens `_discover_findings` already turned into a
    `materialize="document"` draft (one per `docs/audit/findings/F*.md` essay) — this
    function must skip exactly those, or the same finding gets two numbers: one from its
    essay's own `document` draft, one from this function's `register_row` draft, both fed
    into `_assign_numbers` independently (Phase B has no notion that two drafts might name
    the same finding). NT-0019's own illustrative row (§3: `F27` + its essay →
    `docs/findings/FD-0nnnn-rating-shapes.md`, register row `was: F27`) is one number
    shared by both places, never two — a finding *without* an essay is untouched by this
    exclusion and still gets its number here, exactly as before this parameter existed.

    `migrate()` itself does **not** pass `exclude` here — it calls this function
    unfiltered so `_check_legacy_file_not_silently_unrecognised`'s shape census sees every
    row the parser actually found (a corpus where every finding has an essay must not read
    as "register.md's shape went unrecognised"), then filters the *result* externally
    before assigning numbers. This parameter stays for a direct caller (a test proving the
    double-assignment fix in isolation) that wants the filtering done in one call.
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
        if token in exclude:
            continue
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


_FINDING_TITLE_RE: Final = re.compile(r"^#\s+(F\d+)\s+—\s+(.+)$", re.MULTILINE)
_FINDING_FILENAME_RE: Final = re.compile(r"^(F\d+)\.md$")

#: Ruling 99 §2, File 3: a finding essay that lives outside `docs/audit/findings/` and
#: carries no `F<n>.md` filename at all, because it is the essay half of an
#: **already-open** register finding rather than a new one — "not a new finding, no new
#: id" (§3). `token -> its essay's path`, so it shares that finding's own number through
#: the identical `_discover_register` exclusion every `F*.md` essay goes through, never a
#: number of its own.
_FINDING_EXTRA_ESSAY_LOCATIONS: Final[Mapping[str, str]] = {
    "F28": "docs/audit/work/nt-0010-0011-adoption/pilot-findings.md",
}


def _discover_findings(root: Path) -> list[_Draft]:
    """`docs/audit/findings/F<n>.md`: one essay per finding (NT-0019 §5.2's own routing,
    `docs/notes/0019-one-id-per-document.md:323`: *"`audit/findings/F*.md` (5) + README |
    `findings/FD-0nnnn-*.md`; README rewritten"*). `docs/audit/findings/README.md` is the
    family's own index, not a governed finding, and is excluded by the filename match
    below exactly as `docs/adr/README.md` is excluded from `_discover_adrs`.

    **Owner is `auditor` unconditionally** — NT-0019 §1.6's `FD` row: *"auditor (register
    row + essay)"* names no other creator, matching `_discover_register`'s own `owner=
    "auditor"` for the row half of the same family.

    **`status:`** comes from the matching register row's Decision cell — NT-0019 §5.2's
    `audit/register.md` row: *"each row gains `status:` (`active`, or `closed` where a
    **Resolved** annotation exists)"*. A finding's essay carries no `decision:` field of
    its own (`docs/_templates/FD.md`'s own header comment: that field is the register
    row's, "never this frozen essay's" — Ruling 70) — only `status:`, from the identical
    predicate `scripts/register-lint.py`'s own check 2 uses to decide whether a Decision
    cell already carries a resolution marker (`_opens_with_status` — the cell's own
    opening is a disposition-vocabulary word; or `_STATUS_MARKER` — an in-cell "**Resolved
    <date>**" / "Fixed —" annotation like F32's or F-W10-1-1's). A finding with no
    matching register row (should not occur in a well-formed corpus, but the essay
    directory and the register table are two independently-read files) defaults to
    `active` rather than raising — the same "no data source, so omitted/defaulted rather
    than guessed" reading `_stamp_header`'s own docstring gives every other unresolved
    optional field.

    **`was:`** is the bare `F<n>` token (NT-0019 line 269's illustrative row: *"`F27` +
    `docs/audit/findings/F27.md`" → "`docs/findings/FD-0nnnn-rating-shapes.md`, register
    row `was: F27`"* — not the path, not `F27.md`), so it doubles as the citation-rewrite
    key `migrate()`'s Phase D pass already keys every other family's `was:`/`old_token` on.

    **Title** comes from the essay's own `# F<n> — <title>` heading (`_FINDING_TITLE_RE`),
    the same heading-derived reading `_discover_adrs` gives `# ADR-<n> — <title>` and
    `_discover_notes` gives `# NT-<nnnn> — <title>`.

    **Date source:** git first-commit date (`_module_first_commit_date`) — an essay carries
    no per-file date field of its own, the same fallback `_discover_register` already uses
    for the register file itself (NT-0019 §4 step 1: "git first-commit date otherwise").

    The essay's own H1 still names the legacy `F<n>` token in its body text; that line is
    rewritten by the same global Phase D citation pass every other document's body goes
    through (`token_map["F84"] = "FD-00084"` reaches the file `_write_document_drafts`
    already wrote, exactly as it reaches every other citing file in the tree) — no
    per-family body rewrite is added here, deliberately, per Ruling 67 §2's "one shared
    constant" reasoning `_discover_register`'s own docstring already cites.
    """
    findings_dir = root / "docs" / "audit" / "findings"
    register_lint = _load_register_lint()
    register_rows: dict[str, Any] = {}  # `register_lint.Row`, a dynamically-loaded type
    register_path = root / "docs" / "audit" / "register.md"
    if register_path.is_file():
        rows, _problems = register_lint.parse_register(register_path)
        for row in rows:
            m = _REGISTER_FINDING_RE.search(row.fields[0])
            if m is not None:
                register_rows[m.group(1)] = row

    def status_for(token: str) -> str:
        row = register_rows.get(token)
        if row is None:
            return "active"
        decision = row.fields[4]
        if register_lint._opens_with_status(decision) or register_lint._STATUS_MARKER.search(
            decision
        ):
            return "closed"
        return "active"

    drafts: list[_Draft] = []
    order = 0
    if findings_dir.is_dir():
        for path in sorted(findings_dir.glob("*.md")):
            filename_match = _FINDING_FILENAME_RE.match(path.name)
            if filename_match is None:
                continue  # README.md and anything else not a bare `F<n>.md` essay
            token = filename_match.group(1)
            text = path.read_text(encoding="utf-8")
            title_match = _FINDING_TITLE_RE.search(text)
            title = title_match.group(2).strip() if title_match is not None else token
            created = _module_first_commit_date(path, root)
            drafts.append(
                _Draft(
                    materialize="document", prefix="FD", kind=None, title=title,
                    status=status_for(token), created=created, owner="auditor",
                    tie_break=(path.relative_to(root).as_posix(), order), old_token=token,
                    was=path.relative_to(root).as_posix(), body=text,
                )
            )
            order += 1
    # Ruling 99 (`docs/plans/2026-09-03-w37-6-ruling-99-three-undeclared-files.md`) §2,
    # File 3: `pilot-findings.md` is not itself an `F<n>.md`-shaped essay -- it lives at a
    # different path entirely and carries no `# F<n> — <title>` heading -- but is the
    # essay half of an *already-open* register finding, F28, which `docs/audit/
    # register.md:70` cites it by name as the disposition trail for. "Not a new finding,
    # no new id" (§3): it must produce a draft that shares F28's own number, not mint one
    # of its own, so it goes through the identical exclusion path every `F*.md` essay
    # does -- `_discover_register`'s caller filters `register_drafts` by every `old_token`
    # this function returns, F28 included.
    for token, rel in _FINDING_EXTRA_ESSAY_LOCATIONS.items():
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        row = register_rows.get(token)
        if row is not None:
            title = row.fields[0][: row.fields[0].rfind("(")].strip()
        else:
            title_match = _GENERIC_H1_RE.search(text)
            title = title_match.group(1) if title_match is not None else token
        created = _module_first_commit_date(path, root)
        drafts.append(
            _Draft(
                materialize="document", prefix="FD", kind=None, title=title,
                status=status_for(token), created=created, owner="auditor",
                tie_break=(path.relative_to(root).as_posix(), order), old_token=token,
                was=path.relative_to(root).as_posix(), body=text,
            )
        )
        order += 1
    return drafts


_WORKFLOW_TITLE_RE: Final = re.compile(r"^#\s+(WF-\d+)\s+—\s+(.+)$", re.MULTILINE)
#: The filename's own legacy form -- `wf-01-dataset-to-model.md` -> `wf-01`. Task 4's
#: wf-0n ruling: this, not the heading's uppercase form, is `old_token`'s primary key,
#: because it is the identifier itself under §7(d)'s own `wf-0[0-9]` alternative and it is
#: what nearly every real citation in the corpus actually writes.
_WORKFLOW_FILENAME_RE: Final = re.compile(r"^(wf-\d+)-")


def _discover_workflows(root: Path) -> list[_Draft]:
    """`docs/workflows/wf-0N-*.md`: NT-0019 §5.2's own routing
    (`docs/notes/0019-one-id-per-document.md:322`: *"`workflows/wf-0n-*.md` (5) + README |
    `WF-0nnnn-*.md`, stamped; README table generated"*). Matched on the file's own legacy
    heading `# WF-0N — <title>` (`_WORKFLOW_TITLE_RE`) — the same heading-derived
    `old_token` reading `_discover_adrs` gives `# ADR-<n> — <title>`, invisible to a second
    run once the file has moved to `docs/workflows/WF-<n>-*.md` with no such heading.
    `docs/workflows/README.md` carries no such heading and is excluded by the match
    failing, exactly as `docs/adr/README.md` is excluded from `_discover_adrs`.

    **Owner is `decision-maker`** — `docs/_templates/WF.md`'s own header comment ("owner:
    decision-maker # creates via spec-change") and NT-0019 §1.6's `WF` row ("decision-maker,
    via `spec-change`"; executor only *delivers* the journey's steps, never creates the
    document).

    **Status is `active`** — every workflow under `docs/workflows/` today is a live,
    in-force cross-module journey, cited throughout `docs/specs/` and `CLAUDE.md` §4, not a
    draft awaiting acceptance; unlike an ADR's legacy bullet header there is no in-file
    status field to read instead, so this is a disclosed reading rather than a value
    NT-0019 states outright — the same disclosed-mapping reading `classify_docs_files`'s
    own docstring gives its `docs/specs/*.md` → `"requirement"` mapping.

    **Date source:** git first-commit date (`_module_first_commit_date`) — a workflow
    carries no per-file date field of its own, the same fallback `_discover_register` and
    `_discover_findings` both use.
    """
    drafts: list[_Draft] = []
    workflows_dir = root / "docs" / "workflows"
    if not workflows_dir.is_dir():
        return drafts
    for path in sorted(workflows_dir.glob("*.md")):
        if _docid.ID_RE.match(path.name):
            # Already migrated: its filename is the canonical padded form
            # (`WF-00024-*.md`). The file's *body* still carries a `# WF-<n> — <title>`
            # heading that matches `_WORKFLOW_TITLE_RE` regardless of width -- the new
            # padded number is still `WF-\d+` -- so the regex alone cannot tell a second
            # run apart from the first; the filename can, the same idempotency reading
            # `_check_flat_document_directory_not_silently_unrecognised`'s own
            # `is_already_canonical` gives every other family's second-run check.
            continue
        text = path.read_text(encoding="utf-8")
        title_match = _WORKFLOW_TITLE_RE.search(text)
        if title_match is None:
            continue  # README.md and anything else not a legacy `# WF-0N — <title>` file
        heading_token, title = title_match.group(1), title_match.group(2)
        filename_match = _WORKFLOW_FILENAME_RE.match(path.name)
        # Task 4's wf-0n ruling: the filename's lowercase form is the primary key; the
        # heading's uppercase form rides along as an alias to the same target. A filename
        # that does not match the expected shape (not proven to occur in the real corpus,
        # but not assumed impossible either) falls back to the heading form alone, exactly
        # what this function did before the ruling -- never silently drops the draft.
        if filename_match is not None:
            old_token, extra_old_tokens = filename_match.group(1), (heading_token,)
        else:
            old_token, extra_old_tokens = heading_token, ()
        created = _module_first_commit_date(path, root)
        drafts.append(
            _Draft(
                materialize="document", prefix="WF", kind=None, title=title,
                status="active", created=created, owner="decision-maker",
                tie_break=(path.relative_to(root).as_posix(), 0),
                old_token=old_token, was=path.relative_to(root).as_posix(), body=text,
                extra_old_tokens=extra_old_tokens,
            )
        )
    return drafts


_GENERIC_H1_RE: Final = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


#: Every standalone `docs/audit/` file NT-0019 or a later ruling routes into
#: `research/RS-...` by explicit path, `rel -> (kind, owner)`:
#:
#: - `file-census.md`/`file-taxonomy-draft.md` — `docs/notes/0019-one-id-per-document.md
#:   :328` ("`audit/file-census*.{md,csv}`, `audit/file-taxonomy-draft.md` | →
#:   `research/RS-…`"), `:238` ("census and taxonomy draft → `RS- kind: measurement`/
#:   `audit`"). `kind: measurement` for both is a **reading**, not a citation: NT-0019
#:   gives a disjunction and neither file reads as a formal audit with scope, evidence and
#:   verdicts (§1.6's own `RS` `audit` row) — both are raw counts and a draft
#:   classification exercise, which is what `measurement` names in §1.2's table. Owner
#:   `executor` — D13 (§3): "research → executor, except `RS- kind: audit` → auditor".
#: - `nt-0019-verification-and-impact-sweep.md`/`ruling-acceptance-item-sweep.md` — Ruling
#:   99 (`docs/plans/2026-09-03-w37-6-ruling-99-three-undeclared-files.md`) §2: neither file
#:   existed at NT-0019's own `8f5d57d` base tree (§1.13: "every governance file **at
#:   `8f5d57d`**"), so NT-0019 cannot have named them — both are dispatched audit records
#:   with method, evidence and verdicts, matching `RS`'s unit and `kind: audit`'s
#:   vocabulary directly (§1(e)); owner `auditor`, per the same `RS` `audit` row (D13).
#:
#: Matched by explicit path, not a directory sweep: unlike findings or workflows, there is
#: no shared shape to glob on (a bare `F<n>.md` filename, a `# WF-0N —` heading) — named
#: legacy files, the same reading `_REFERENCE_MOVE_TARGETS` below gives its four.
_RESEARCH_ESSAY_TARGETS: Final[Mapping[str, tuple[str, str]]] = {
    "docs/audit/file-census.md": ("measurement", "executor"),
    "docs/audit/file-taxonomy-draft.md": ("measurement", "executor"),
    "docs/audit/nt-0019-verification-and-impact-sweep.md": ("audit", "auditor"),
    "docs/audit/ruling-acceptance-item-sweep.md": ("audit", "auditor"),
}


def _discover_research_essays(root: Path) -> list[_Draft]:
    """`_RESEARCH_ESSAY_TARGETS`'s files, each still at its old path — idempotent by
    construction: once moved, the path this function reads no longer exists.
    """
    drafts: list[_Draft] = []
    for order, (rel, (kind, owner)) in enumerate(_RESEARCH_ESSAY_TARGETS.items()):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        title_match = _GENERIC_H1_RE.search(text)
        title = title_match.group(1) if title_match is not None else path.stem
        created = _module_first_commit_date(path, root)
        drafts.append(
            _Draft(
                materialize="document", prefix="RS", kind=kind, title=title,
                status="active", created=created, owner=owner,
                tie_break=(rel, order), old_token=None, was=rel, body=text,
            )
        )
    return drafts


#: NT-0019 §5.2 :328 routes this file into `research/RS-...` alongside its two markdown
#: siblings above, but it cannot carry the family's YAML front matter -- F83's own
#: corrected population (`docs/audit/register.md`, F83 row, "Corrected 2026-09-02") names
#: this exact file as one of the two non-`.md` files added to the "cannot physically
#: carry front matter" exempt set: a prepended `---` block makes row 1 stop being the
#: CSV's own header, breaking `scripts/file-census.py` and any other CSV reader.
#: `classify_docs_files` buckets by directory, not by header, so the move alone satisfies
#: NT-0019 §7(a); no header follows it, and no `id:` is minted for it either (it never
#: numbers into the sequence — a document family membership without an id would itself be
#: a new, undeclared shape).
_RESEARCH_UNSTAMPABLE_MOVE: Final[Mapping[str, str]] = {
    "docs/audit/file-census-5ef559d.csv": "docs/research/file-census-5ef559d.csv",
}


def _move_unstampable_research_files(root: Path) -> tuple[list[str], list[str]]:
    """Moves `_RESEARCH_UNSTAMPABLE_MOVE`'s file(s) byte-for-byte -- `read_bytes`/
    `write_bytes`, never `read_text`/`write_text`, so this cannot silently normalise line
    endings or re-encode anything in a file whose whole reason for this special path is
    that its bytes must stay exactly parseable as CSV. Returns `(written, deleted)` repo-
    relative posix paths, the same shape `_write_document_drafts` returns.
    """
    written: list[str] = []
    deleted: list[str] = []
    for old_rel, new_rel in _RESEARCH_UNSTAMPABLE_MOVE.items():
        old_path = root / old_rel
        if not old_path.is_file():
            continue
        new_path = root / new_rel
        new_path.parent.mkdir(parents=True, exist_ok=True)
        new_path.write_bytes(old_path.read_bytes())
        old_path.unlink()
        written.append(new_rel)
        deleted.append(old_rel)
    return written, deleted


def _discover_named_phase_records(root: Path) -> list[_Draft]:
    """The two standalone `docs/audit/` files NT-0019 names individually as `CR- kind:
    phase` records (`docs/notes/0019-one-id-per-document.md:238`: *"exit-demo UAT and
    `phase-0-status.md` → `CR- kind: phase`"*; `:314` and `:324` for their own §5.2 rows).
    Neither is a per-directory README (`_discover_audit_closure_readmes`'s shape) or a
    heading inside a shared file (`_discover_closure_records`'s shape) -- each is its own
    whole file with its own H1, so matched by explicit path exactly as
    `_discover_research_essays` matches its two.

    **Owner `auditor`** — §1.6's `CR` row: "auditor (`work`, `phase`); lead (`review`)".
    **Status `active`** — §1.2's own table: closure mutability is write-once, `active` is
    the family's only value, ever.

    **`phase:`** is read, not derived: `exit-demo-uat.md`'s own H1 names "Phase 1b"
    (`P1b`); `phase-0-status.md`'s own H1 names "Phase 0" (`P0`). Neither is guessed from
    a roadmap lookup the way `_write_document_drafts`'s `LG-` `work:` resolution is,
    because both files say their own phase directly.
    """
    targets: tuple[tuple[str, str], ...] = (
        ("docs/audit/exit-demo-uat.md", "P1b"),
        ("docs/phase-0-status.md", "P0"),
    )
    drafts: list[_Draft] = []
    for order, (rel, phase) in enumerate(targets):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        title_match = _GENERIC_H1_RE.search(text)
        title = title_match.group(1) if title_match is not None else path.stem
        created = _module_first_commit_date(path, root)
        drafts.append(
            _Draft(
                materialize="document", prefix="CR", kind="phase", title=title,
                status="active", created=created, owner="auditor",
                tie_break=(rel, order), old_token=None, was=rel, body=text, phase=phase,
            )
        )
    return drafts


#: NT-0019 §5.2's own routing for these four `docs/audit/` files -- Reference family
#: (§1.2's Reference row already names `process/`), moved bodily into `docs/process/`
#: rather than stamped in place, because their *directory* is what §1.2 routes: `:326`
#: ("`audit/checklists/*.md` | → `process/checklists/`") and `:327` ("`audit/retrofit-
#: impossible.md`, `audit/security-posture.md` | → `process/`"). Deliberately does not
#: author the checklist "gains" sentences `:326` also names -- new procedural prose is an
#: authored content obligation, not a migration act (the maintainer's 2026-09-03 ruling:
#: "the move alone discharges the thing the gate measures"); filed as a finding instead,
#: not invented here. Grepped for existing text first (`new record has an id`, `no family
#: outside`, `freeze-gate`) -- the only tree-wide hit is the map plan restating the same
#: instruction, not any authored text to carry over.
_REFERENCE_MOVE_TARGETS: Final[Mapping[str, str]] = {
    "docs/audit/checklists/phase-close.md": "docs/process/checklists/phase-close.md",
    "docs/audit/checklists/work-item-close.md": "docs/process/checklists/work-item-close.md",
    "docs/audit/retrofit-impossible.md": "docs/process/retrofit-impossible.md",
    "docs/audit/security-posture.md": "docs/process/security-posture.md",
}


@dataclass(frozen=True)
class _ReferenceMove:
    """One Reference-family file NT-0019 §5.2 routes to a **new** path under
    `docs/process/` -- the one exception to `_ReferenceStamp`'s "no move" rule (§1.2's
    Reference row still applies: no id, no number -- only the location changes).
    """

    old_path: Path
    new_path: Path
    old_rel: str
    new_rel: str
    owner: str
    title: str


def _discover_reference_moves(root: Path) -> list[_ReferenceMove]:
    """`_REFERENCE_MOVE_TARGETS`'s four files, each still at its old path -- idempotent by
    construction, the same reading `_discover_research_essays` gives its own explicit-path
    targets: once moved, the old path is simply absent on a second run.

    Title is the file's own H1; owner `maintainer` — §1.6's Reference row for `process/`:
    "maintainer; amendments arrive as `RFC-` + `RL-`".
    """
    moves: list[_ReferenceMove] = []
    for old_rel, new_rel in _REFERENCE_MOVE_TARGETS.items():
        old_path = root / old_rel
        if not old_path.is_file():
            continue
        text = old_path.read_text(encoding="utf-8")
        title_match = _GENERIC_H1_RE.search(text)
        title = title_match.group(1) if title_match is not None else old_path.stem
        moves.append(
            _ReferenceMove(
                old_path=old_path, new_path=root / new_rel, old_rel=old_rel,
                new_rel=new_rel, owner="maintainer", title=title,
            )
        )
    return moves


def _write_reference_moves(
    root: Path, moves: Sequence[_ReferenceMove]
) -> tuple[list[str], list[str]]:
    """Stamps each move's Reference header at its **new** path and deletes the old one --
    same `_stamp_header("REFERENCE", ...)` substitution `_stamp_reference_targets` uses
    for the in-place case, `was=` set here (that function always passes `was=None`,
    because nothing it stamps has moved).
    """
    written: list[str] = []
    deleted: list[str] = []
    for move in moves:
        move.new_path.parent.mkdir(parents=True, exist_ok=True)
        header = _stamp_header(
            "REFERENCE", None, kind=None, title=move.title, status="active",
            created=_module_first_commit_date(move.old_path, root), owner=move.owner,
            was=move.old_rel,
        )
        body = move.old_path.read_text(encoding="utf-8")
        move.new_path.write_text(header + "\n" + body, encoding="utf-8")
        written.append(move.new_rel)
        move.old_path.unlink()
        deleted.append(move.old_rel)
    return written, deleted


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


@dataclass(frozen=True)
class _VendoredManifestScan:
    """Every vendored skill's own `SKILL.md`, partitioned by what *this migration* has
    already done to it.

    The three buckets are exhaustive over the manifests `_is_vendored_skill_manifest`
    claims, so `len(to_stamp) + len(deferred) + len(already_stamped)` **is** that
    population's size. That is the point of returning a partition rather than a list:
    `F88` limb 1's second consequence was a manifest leaving the function through a bucket
    with no name, which is indistinguishable from one that was never there.
    """

    #: `_front_matter_state` == `"none"` — no leading block at all, so this run prepends
    #: one. The only bucket `migrate` writes.
    to_stamp: tuple[Path, ...]
    #: == `"foreign"` — a leading block this migration did not write, so its header must be
    #: **merged** into that block rather than prepended. `(rel, reason)` per manifest.
    #: Reported to the reader by the Reference stamp census, which reaches every
    #: `.claude/skills/*/SKILL.md`; carried here so this function's own partition closes
    #: and the two instruments can be reconciled against each other
    #: (`test_vendored_manifest_deferrals_are_exactly_the_reference_censuss`).
    deferred: tuple[tuple[str, str], ...]
    #: == `"stamped"` — this migration's own `family:` header is already on the file. A
    #: second run leaves it alone; this is the idempotency bucket.
    already_stamped: tuple[str, ...]


def _discover_vendored_skill_manifests(root: Path) -> _VendoredManifestScan:
    """Every vendored skill's own `SKILL.md`, split by whether **this migration** has
    stamped it — the one discovery function in this module that cannot infer "already
    migrated" from a legacy shape being absent, because stamping does not move or rename
    this file (NT-0019 §1.5).

    **Classified with `_front_matter_state`, never with `_docid.parse_header`** — `F88`
    limb 1, whose two consequences are independent and both come from that one wrong
    predicate:

    * *It aborted every real run.* Three real vendored manifests carry upstream front
      matter that does not fit §1.5's closed grammar (`create-adaptable-composable` and
      `vue-best-practices` an indented `author:`, `planning-with-files` a
      `user-invocable: true`), so `parse_header` raised `HeaderError` from inside
      discovery and `migrate` died before its stamp loop. `_front_matter_state` is
      textual and cannot raise, for exactly this reason — its own docstring names these
      same three files.
    * *It read someone else's front matter as this migration's stamp.* `parse_header`
      puts an unknown key in `.extra` rather than erroring, so every manifest opening
      with the harness's `name:`/`description:` block returned a `Header` and was skipped
      as already-migrated — 25 of the 28 at `c888b61`. `_front_matter_state` decides
      `"stamped"` on `family:`, the key every family's template carries and no harness
      block does: a positive test for this migration's own output rather than "the front
      matter parsed".

    **`scripts/audit-docs.py`'s `UNSTAMPABLE_EXEMPTIONS` is deliberately not consulted
    here, and its absence is not an oversight.** That register answers *"can this file
    carry a governed header at all?"* — a stamp-set question, owned by the gate, whose
    three vendored entries are exempt by the maintainer's 2026-09-02 ruling
    (`docs/plans/2026-09-02-w37-vendored-exemption-ruling.md`). This function answers
    *"has this migration already stamped this manifest?"* — an idempotency question.
    Substituting one for the other is what produced the defect above, and importing the
    register would substitute a *different* wrong predicate rather than fix it: at
    `c888b61` all 28 vendored manifests classify `"foreign"`, so the 3 registered ones
    need no separate treatment here — they are deferred alongside the other 25, by the
    same rule, for the same reason. (`UNSTAMPABLE_EXEMPTIONS`'s own declaration names
    `audit-docs.py` check 30 as the consumer it was made public for, not this module.)

    Forward reference by design: `_front_matter_state` and `_REFERENCE_FOREIGN_REASON` are
    defined below, in the Reference-stamp section that carries their rationale. Moving
    either up here would separate it from that reasoning; both resolve at call time.
    """
    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return _VendoredManifestScan((), (), ())
    to_stamp: list[Path] = []
    deferred: list[tuple[str, str]] = []
    already_stamped: list[str] = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        if not _is_vendored_skill_manifest(skill_md):
            continue
        rel = skill_md.relative_to(root).as_posix()
        state = _front_matter_state(skill_md.read_text(encoding="utf-8"))
        if state == "stamped":
            already_stamped.append(rel)
        elif state == "foreign":
            deferred.append((rel, _REFERENCE_FOREIGN_REASON))
        else:
            to_stamp.append(skill_md)
    return _VendoredManifestScan(tuple(to_stamp), tuple(deferred), tuple(already_stamped))


def _iter_tree_files(root: Path) -> Iterator[Path]:
    """Every real file under `root`, sorted, excluding `.git/` and every
    `_docid.sweep_exclusion_reason` hit — every whole-tree walk `migrate` and
    `migration_diff_violations` run needs both exclusions.

    `.git/` matters once a test (or a real checkout) makes `root` an actual git
    repository: `.git/index` and packed objects are binary, but `.git/HEAD`,
    `.git/config` and the ref files under `.git/refs/` decode as UTF-8 text perfectly
    well, so relying on `UnicodeDecodeError` alone to keep this module from ever reading —
    and, worse, rewriting — git's own plumbing is not a guarantee, only a coincidence of
    what today's token set happens not to match.

    `sweep_exclusion_reason` matters for the same reason at a different layer: without it
    this walk would treat `uv.lock`, `frontend/pnpm-lock.yaml`, the entire
    `tests/fixtures/docs-ids/`/`tests/fixtures/docs-migration/` corpora, and any
    `__pycache__/*.pyc` this process's own dynamic imports leave behind (`_load_module`
    below) as real migration input — the instrument reading its own fixtures and its own
    exhaust as if they were the repository it is migrating.
    """
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if ".git" in rel.parts:
            continue
        if _docid.sweep_exclusion_reason(rel.as_posix()) is not None:
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

#: Where each document family's files land. **`RS` is here because NT-0019 §1 puts it
#: there** — *"| Document | Research | `RS` | `docs/research/` | one spike, measurement or
#: audit | frozen | draft → active → closed \| retired | `spike` · `measurement` ·
#: `audit` |"* — not because anyone chose a directory. It was absent until 2026-09-02
#: while `_discover_closure_records` was already emitting two `RS- kind: audit` drafts, so
#: `_write_document_drafts` raised `KeyError: 'RS'` **after** writing 125 of 290 documents:
#: a partial migration rather than a clean abort. `_check_every_document_draft_is_placeable`
#: below is what stops the next family doing the same.
#:
#: **`FD` and `WF` added W37-6** — NT-0019 §1.2's own table declares nine Document rows;
#: before this change this mapping implemented seven (`ADR RFC PL RL CR LG RS`), the same
#: `KeyError` shape the comment above already names, just never yet hit because nothing
#: called a `_discover_findings`/`_discover_workflows` that emitted a `materialize=
#: "document"` draft for either prefix. `_check_every_document_draft_is_placeable` proves
#: this on deliberately broken input (`test_every_emittable_document_prefix_has_a_family_
#: dir_and_a_template`, `test_fd_document_draft_is_refused_before_the_family_dir_fix`):
#: findings land in `docs/findings/` (`FD.md`'s own template — the essay half of a
#: register row plus a frozen essay, NT-0019 §1.2's Finding row), workflows in
#: `docs/workflows/` (already home to the un-stamped `wf-0N-*.md` files — NT-0019 §1.2's
#: Workflow row).
_DOCUMENT_FAMILY_DIR: Final[Mapping[str, str]] = {
    "ADR": "adrs", "RFC": "rfcs", "PL": "plans", "RL": "rulings", "CR": "closures",
    "LG": "ledgers", "RS": "research", "FD": "findings", "WF": "workflows",
}


def _check_every_document_draft_is_placeable(drafts: Sequence[_Draft]) -> None:
    """Refuse, **before any write**, if a draft this run would materialise as a document
    names a prefix the writer cannot place or cannot render.

    `_write_document_drafts` looks a prefix up in `_DOCUMENT_FAMILY_DIR` and `_stamp_header`
    looks the same prefix up in `_MIGRATE_TEMPLATE_FILENAME`, inside a loop that has already
    written files. A prefix missing from either therefore surfaces as a bare `KeyError`
    partway through an irreversible one-way migration -- the failure mode task #34 filed
    against a different call, one layer down. This converts it into a named refusal in the
    pre-write span, where the tree is still untouched.

    **It cannot fire on any corpus.** The emittable prefix set is a property of this
    module's source, not of the documents it reads, so this guard adds no way for a real
    run to stop that a source change did not already introduce -- which is why it is a
    guard rather than only a test. The test
    (`test_every_emittable_document_prefix_has_a_family_dir_and_a_template`) is the primary
    instrument and derives the same set statically, so a *branch today's corpus never takes*
    is caught at PR time; this catches what the corpus in front of it actually produced.
    Neither subsumes the other.
    """
    unplaceable: list[str] = []
    for d in drafts:
        if d.materialize != "document":
            continue
        missing = [
            table
            for table, keys in (
                ("_DOCUMENT_FAMILY_DIR", _DOCUMENT_FAMILY_DIR),
                ("_MIGRATE_TEMPLATE_FILENAME", _MIGRATE_TEMPLATE_FILENAME),
            )
            if d.prefix not in keys
        ]
        if missing:
            unplaceable.append(
                f"{d.prefix} ({d.title[:60]!r}, from {d.was or 'no source file'}) -- "
                f"absent from {' and '.join(missing)}"
            )
    if unplaceable:
        raise NotImplementedError(
            "migrate: discovery produced document draft(s) the writer cannot place, and "
            "the lookup that fails is inside the write loop -- refusing before any write "
            "rather than part-way through: "
            + "; ".join(sorted(set(unplaceable)))
        )


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
        # Recorded from the bytes actually written, not from a second construction of the
        # same header: this is the offset a re-derived line-number citation is added to
        # (`_SplitSource.resolve`), and a header rebuilt for the arithmetic could differ
        # from the one on disk without anything noticing.
        d.body_line_offset = (header + "\n").count("\n")
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
    locator_prefix: str, text: str, heading_re: re.Pattern[str], split_level: int, *, scope: str,
    extra_record_starts: Collection[int] = (),
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

    `extra_record_starts` carries the offsets of records produced by a *different*
    discovery function over the same file -- `_discover_proposal_containers`' `RFC-` in
    `plan-reviews.md`. Ruling 83 §1(b) is why they are passed in rather than re-derived
    here: a guard may not derive its denominator from the matcher it is checking, and it
    equally may not decide on its own that a unit some other matcher claims is a record.
    The offsets come from `_proposal_container_starts`, the same single definition the
    discovery function itself uses.
    """
    headings = _heading_census_units(text, locator_prefix)
    record_starts = {m.start() for m in heading_re.finditer(text)} | set(extra_record_starts)
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
    root: Path, rel_path: str, heading_re: re.Pattern[str], split_level: int, description: str,
    *, extra_record_starts: Callable[[str], Collection[int]] | None = None,
) -> None:
    """Task #30/#31 (Ruling 83's census), for `_discover_headed_split_file`'s shape
    (`plan-reviews.md` today; `closure-records.md` has its own discovery function and its
    own disposition logic -- Ruling 84 territory, not this one). Mirrors `_check_legacy_
    file_not_silently_unrecognised`'s early returns: a moved-away or genuinely blank file
    has nothing to reconcile. Runs *alongside*, not instead of, that existing "zero total"
    guard -- this one closes the arithmetic; that one still catches a file moved to an
    unexpected new location returning zero drafts outright.

    `extra_record_starts` is a callable over the file's text rather than a ready-made set,
    because this function is what opens the file: a caller cannot pass offsets without
    having read the text to compute them. `plan-reviews.md` passes
    `_proposal_container_starts` (F80); the default `None` leaves every other caller's
    behaviour byte-identical.
    """
    path = root / rel_path
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return
    _check_heading_split_not_silently_unrecognised(
        rel_path, text, heading_re, split_level, scope=f"{rel_path} ({description})",
        extra_record_starts=() if extra_record_starts is None else extra_record_starts(text),
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
    - **Ruling 86: `Ruling A1`/`A2`/`A3` become three `RL-` records**, via a widening on
      two axes (heading level and token shape, §3 item 1). **That widening has now
      landed**, as `_discover_lettered_rulings` rather than inside `_RULING_HEADING_RE` --
      Ruling 86 §3 item 5 requires a residual `PL-` for the source document, which
      widening `_RULING_HEADING_RE` would have destroyed (see that function's docstring).
      The three are records here now, not unaccounted units, and register finding F81 --
      raised because this guard aborted `migrate` on them -- is what that code discharges.

    **The coupling this docstring anticipated, and how it resolved:** the "record" bucket
    below was keyed off `_RULING_HEADING_RE`'s own matches, and this paragraph said that if
    Ruling 86's widening landed as a *different* mechanism (Ruling 87 §3 item 1's other
    option) then `record_starts` must be re-pointed at that mechanism's output too. It did,
    and it is: the bucket is now the union of both matchers. Anything a third matcher
    claims in future has to be added the same way, or this guard will re-flag units a
    correct code path has already produced.
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
        split_starts = {m.start() for m in _RULING_HEADING_RE.finditer(text)}
        # Ruling 86's A-series, produced by `_discover_lettered_rulings` (F81). This is the
        # re-pointing this function's own docstring said would be needed if the widening
        # landed as a separate mechanism rather than inside `_RULING_HEADING_RE`; it did,
        # for the reason that function's docstring gives (the residual `PL-`), so the
        # record bucket is keyed off both matchers rather than one.
        record_starts = split_starts | {
            m.start() for m in _LETTERED_RULING_HEADING_RE.finditer(text)
        }
        spans = _record_spans(record_starts, len(text))
        # Bucket 2's "preamble" half comes from `_discover_multi_ruling_files` ALONE, so it
        # is anchored on that function's own first record and not on the union above.
        # `_discover_lettered_rulings` extracts sections from a document that survives as a
        # `PL-`: text before its first record is that plan's body, not a preamble folded
        # into anything, so a `Ruling`-anchored heading sitting there is genuinely
        # unaccounted and must still be named. Anchoring on the union would have exempted
        # it -- caught by a test, not by reading.
        first_record_start = min(split_starts) if split_starts else None
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


# `_CENSUS_DEP_BARE_RE` and `_legacy_bare_dep_ids` now live beside `_LEGACY_SPEC_BOLD_RE`
# above (F82): the census's independent unit-finder and the discovery function's own record
# rule have to be reconciled against each other, so they are defined together rather than
# one here and one 1000 lines up.


def _check_requirements_not_silently_unrecognised(root: Path) -> None:
    """Task #30 (Ruling 83's census) for `_discover_requirements`, the only discovery
    function that shipped with no guard at all. `_LEGACY_SPEC_BOLD_RE` assumes every
    legacy requirement id carries a module code between the prefix and the number
    (`**FR-DATA-12**`); `docs/specs/00-overview.md`'s `DEP-1`, `DEP-1a`, `DEP-2`, `DEP-3`
    are real, module-spec-defined dependency rules that never carry one -- confirmed
    empirically (zero `DEP` occurrences anywhere in `docs/specs/*.md` carry a module code),
    and invisible to every count built on that assumption, `docs/notes/0019-one-id-per-
    document.md`'s own acceptance-criteria greps included.

    The census drops the module-code assumption entirely (via `_CENSUS_BARE_ID_RE`),
    keeping the one genuinely structural signal a definition marker has and a reference
    does not -- the bold span closes right after the id, nothing else inside it. That is
    why a dated-amendment sentence like `**FR-OVR-20 says so twelve rows above this one**`
    (real corpus text) is never a census candidate at all -- the bold span does not close
    after the id -- while `**DEP-1a**` is.

    **Three buckets, and each is checked positively** (Ruling 83 §2), so the arithmetic
    closes rather than the guard going quiet:

    1. **record** -- module-coded (`_LEGACY_SPEC_BOLD_RE`) or a module-less `DEP` id with a
       number (`_legacy_bare_dep_ids`); both are what `_discover_requirements` produces a
       draft for, computed by the same functions it uses.
    2. **derived body** -- already in the canonical post-migration form `_SPEC_BOLD_RE`
       reads. This is the idempotency reading `_check_plain_plans_not_silently_
       unrecognised` already applies to a filename via `_docid.ID_RE`, and it is what
       allowed this census to widen past `DEP`: this docstring used to say broadening
       `FR`/`NFR`/`OQ` "would make this guard fire on `migrate`'s own second-run output and
       break idempotency", which was true only while there was no bucket for an id that is
       already migrated. There is one now.
    3. **declared exception** -- none, and none needed.

    **What still reds it**, which is the point of widening rather than claiming everything:
    a bold span in any of the four prefixes that is neither module-coded, nor canonical,
    nor a numbered `DEP` -- `**FR-12a**`, `**OQ-1a**`, `**DEP-abc**`. None exists in the
    corpus today (measured at `ba31cd1`: `**DEP-1a**` was the only non-conforming bold id
    in `docs/specs/`, and it is now a record), and any that appears is named rather than
    guessed at.
    """
    specs_dir = root / "docs" / "specs"
    if not specs_dir.is_dir():
        return
    for path in sorted(specs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        records = {str(m.start()) for m in _LEGACY_SPEC_BOLD_RE.finditer(text)}
        # F82's bucket 1: a module-less `DEP` id `_discover_requirements` now produces a
        # draft for, computed by the same function that discovery uses.
        records |= {str(m.start()) for m in _legacy_bare_dep_ids(text)}
        # F82's bucket 2: an id already in the canonical post-migration form
        # `_SPEC_BOLD_RE` reads -- the positively-checked idempotency reading Ruling 83
        # requires, never "the legacy pattern found nothing". See `_legacy_bare_dep_ids`
        # for why `DEP-1`/`DEP-2`/`DEP-3` are in this bucket and `DEP-1a` is not.
        already_canonical = {str(m.start()) for m in _SPEC_BOLD_RE.finditer(text)}
        units = []
        for m in itertools.chain(
            _LEGACY_SPEC_BOLD_RE.finditer(text), _CENSUS_BARE_ID_RE.finditer(text)
        ):
            line_no = text.count("\n", 0, m.start()) + 1
            units.append(
                _CensusUnit(key=str(m.start()), locator=f"{rel}:{line_no}", text=m.group(0))
            )
        _reconcile_census(
            scope=f"{rel} (requirement ids)", units=units, records=records,
            is_body=lambda unit, canonical=already_canonical: unit.key in canonical,
        )


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
        exceptions={
            "README.md": "the directory's own README, not a dated record",
            "INDEX.md": (
                "the family's generated split-source index (Ruling 101 clause 1), "
                "not a governed record"
            ),
        },
    )


def _check_flat_document_directory_not_silently_unrecognised(
    root: Path, rel_dir: str, title_re: re.Pattern[str] | None, description: str,
    exceptions: Mapping[str, str], *,
    recursive: bool = False,
    records: Collection[str] | None = None,
) -> None:
    """Task #31 (Ruling 83's census) for `_discover_notes`/`_discover_adrs`'s shared
    skip-path: "found nothing" there is read as "already migrated" purely because the
    legacy title regex found no match -- the exact fixture-corpus assumption Ruling 83
    rejects for `_discover_closure_records`, applied here to a directory instead of a
    heading. Every file under `rel_dir` must be a record, already be in a canonical
    post-migration filename shape (checked positively, the same idempotency reading
    `_check_plain_plans_not_silently_unrecognised` uses), or be a declared exception --
    `<rel_dir>/README.md` in both `docs/notes/` and `docs/adr/` today.

    Two keyword-only extensions, both defaulting to the behaviour above (F84):

    `recursive=True` walks the whole subtree rather than one level. It is not a
    convenience: `docs/audit/work/` holds one record per *sub*directory, so a flat
    `iterdir()` over it finds no files at all and the census closes **vacuously** -- a
    check that cannot fail, which is the "blinds the run" half of W37-5c's own criterion.

    `records=` supplies the record set directly, for a caller whose discovery is not a
    legacy-title match. Re-running the title regex would be a census counted with (a
    close relative of) the splitter's own pattern: for F84 a `.md` file that carried a
    record heading but was not the `README.md` the discovery glob claims would be scored
    a record and pass, while nothing had migrated it. Exactly one of `title_re` and
    `records` may be given, and passing both or neither raises rather than silently
    preferring one.

    The unit key is the path **relative to `rel_dir`**, so nested records are distinct
    units (`W8/README.md`, `W9/README.md`) rather than 16 collisions on `README.md`. For
    a flat directory that is the bare filename, unchanged, and today's two callers'
    `{"README.md": ...}` exception maps keep working.
    """
    if (title_re is None) == (records is None):
        raise ValueError(
            f"{rel_dir}: exactly one of `title_re` and `records` must be given -- a "
            "census's record set comes either from the legacy title regex or from what "
            "discovery actually produced, never from both and never from neither"
        )
    directory = root / rel_dir
    if not directory.is_dir():
        return
    units = []
    found: set[str] = set(records or ())
    walk = directory.rglob("*") if recursive else directory.iterdir()
    for path in sorted(p for p in walk if p.is_file()):
        key = path.relative_to(directory).as_posix()
        units.append(_CensusUnit(key=key, locator=f"{rel_dir}/{key}", text=key))
        if title_re is not None and path.suffix == ".md" and title_re.search(
            path.read_text(encoding="utf-8")
        ):
            found.add(key)

    def is_already_canonical(unit: _CensusUnit) -> bool:
        return _docid.ID_RE.match(unit.key) is not None

    _reconcile_census(
        scope=f"{rel_dir}/ ({description})",
        units=units, records=found, is_body=is_already_canonical, exceptions=exceptions,
    )


#: Ruling 83 bucket 3 for the two closure directories F84 names: every file under them
#: that is **not** one of the 17 records, each with the reason it is not. Declared by
#: path relative to the directory, never by prefix -- a prefix silently swallows every
#: future file beneath it, the failure
#: `docs/plans/2026-09-02-w37-rfc-readme-row-and-stamp-set.md` §3 names for
#: `tests/fixtures/`. Neither entry is a file this slice migrates; both are named so the
#: exemption list is the record of what is unstamped and why, and cannot grow without an
#: arithmetic failure saying so (F83's condition 2).
_AUDIT_CLOSURE_CENSUS_EXCEPTIONS: Final[Mapping[str, Mapping[str, str]]] = {
    "docs/audit/work": {
        "nt-0010-0011-adoption/pilot-findings.md": (
            "the pilot's findings essay, not the adoption's record -- its own H1 is "
            "`# Pilot findings — CLAUDE.md §15 step 6`, and NT-0019 §5.2 routes only "
            "`audit/work/*/README.md` to `CR-`. It has no §5.2 row of its own; reported "
            "as a residual rather than migrated by this slice"
        ),
    },
    "docs/audit/phases": {
        "1b/register.md": (
            "NT-0019 §5.2 routes this into `docs/findings/register.md` alongside "
            "`audit/register.md` (\"the phase register's rows merge in with `phase: "
            "P1b`\"), not to a closure record. `_discover_register` reads only the "
            "top-level `docs/audit/register.md`, so nothing discovers this file today -- "
            "named here so that gap is listed rather than folded into a `CR-`. **Filed as "
            "`F88` limb 2**, 2026-09-02; this entry is its disposition, not its record"
        ),
    },
}


def _check_audit_closure_readmes_not_silently_unrecognised(
    root: Path, drafts: Sequence[_Draft]
) -> None:
    """F84's discharge condition, second limb, verbatim: *"a census over that path names
    any file it cannot classify -- proven on deliberately broken input, per Ruling 83:
    the check must NAME the unmatched unit, never compare counts."*

    Reconciles against what `_discover_audit_closure_readmes` **actually produced**
    (`records=`), never against a re-run of its own title regex, and walks the subtree
    rather than one level -- both reasons are in
    `_check_flat_document_directory_not_silently_unrecognised`'s docstring above, and
    dropping either one leaves a census that passes on input this one names.
    """
    claimed = {d.was for d in drafts if d.was is not None}
    for rel_dir, kind in _AUDIT_CLOSURE_README_DIRS.items():
        prefix = f"{rel_dir}/"
        _check_flat_document_directory_not_silently_unrecognised(
            root, rel_dir, None, f"{kind} closure records",
            _AUDIT_CLOSURE_CENSUS_EXCEPTIONS.get(rel_dir, {}),
            recursive=True,
            records={was[len(prefix):] for was in claimed if was.startswith(prefix)},
        )


# ---------------------------------------------------------------------------------------
# NT-0019 §4 step 5's Reference stamp set — W37-5c item 2.
#
# Before this block the only file `migrate` stamped outside a document family was a
# *vendored* `SKILL.md`. §4 step 5 stamps *"every file under `docs/`, `.claude/roles/`,
# `.claude/skills/*/SKILL.md`, `.claude/agents/`"*, and
# `docs/plans/2026-09-02-w37-owner-field-derivation.md:179` states the gap in terms:
# **"There is no discovery or stamp path for `.claude/skills/`, `.claude/agents/` or
# `.claude/roles/` at all"**. Same shape as F84 — a population outside the question, so
# the run completes and reports success — and it is fixed the same way: discovery, then a
# census that NAMES what it cannot classify.
#
# **Two rulings decide the population and they interact**, which is why the arithmetic is
# stated rather than left to add up (`docs/plans/2026-09-02-w37-rfc-readme-row-and-stamp-
# set.md`, §1 and §4):
#
#   * *"A `README.md` takes the family §5.2 routes it to; one routed nowhere is Reference
#     — README, `lead`."* The 17 F84 discovers above are routed to `CR-`, so they leave
#     this population **by construction rather than by exception** — there is no list to
#     keep in step. 33 tracked `README.md` at `544b90c`, minus those 17, minus the two
#     §5.2/§5.3 delete, is the **14** that RFC's §1 names.
#   * *"§4 step 5 governs the stamp set"*, and gains the six READMEs §5.2 reaches that its
#     globs miss. Eight of the 14 were already inside step 5's roots (seven under `docs/`
#     plus `.claude/agents/README.md`); six were not; one of those six — the check-35
#     allowlist fixture — is exempt by §3; so **13 are stamped and one is exempt**, which
#     is the same 14 decomposed the other way. Both decompositions are asserted in
#     `tests/test_doc_id_migrate.py`, against the tree rather than against these numbers.
#
# **What this slice does NOT stamp, and why it is deferred rather than exempt.** 46
# `.claude/skills/*/SKILL.md` and 7 `.claude/agents/*.md` already carry the harness's own
# YAML front matter (`name:`, `description:`, and for an agent `tools:`/`model:`). A stamp
# cannot prepend a second block — `_docid.parse_header` reads exactly one, from `lines[0]
# == "---"` to the closing `---` — so their header has to be **merged** into the block
# they have, and the keys have to be declared in `docs/_templates/REFERENCE.md` first,
# because Ruling 70 makes the template the licensing instrument for a family's permitted
# fields. That work is `docs/plans/2026-09-02-w37-6-migration-run-leaf-plan.md` §7.1 Task
# 1 (its "second finding", restated as finding 13), carried unchanged into the active v2
# plan — **W37-6's, not this slice's**. Introducing a new convention inside a precondition
# slice is the scope growth the W37-5c slice decision §5 refuses.
#
# So they are **in scope, deferred, and listed**, never quietly absent: every one is
# reported by name on `MigrateResult.deferred_reference_stamps` with its reason, which is
# F83's condition 2 applied to a population that is waiting on a ruling rather than on a
# format impossibility.
# ---------------------------------------------------------------------------------------

_REFERENCE_H1_RE: Final = re.compile(r"^#[ \t]+(\S.*?)[ \t]*$", re.MULTILINE)


def _front_matter_state(text: str) -> str:
    """`"none"`, `"stamped"` or `"foreign"` for `text`'s leading block.

    Deliberately textual rather than a `_docid.parse_header` call: three real `SKILL.md`
    raise `HeaderError` (`create-adaptable-composable`, `planning-with-files`,
    `vue-best-practices` — all three vendored, all three named in
    `docs/plans/2026-09-02-w37-rfc-bucket-c-owner-values.md` §2.1), and a classifier that
    crashes on the very files it exists to classify cannot report them.

    `"stamped"` is decided by `family:`, the one key every family's template carries and
    no harness block does — a positive test for this migration's own output, the same
    idempotency reading `_check_plain_plans_not_silently_unrecognised` uses, rather than
    "not one of the keys I happen to know about".
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return "none"
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return "foreign"  # an opening block this migration did not write and cannot read
    return "stamped" if any(ln.startswith("family:") for ln in lines[1:closing]) else "foreign"


@dataclass(frozen=True)
class _ReferenceStamp:
    """One Reference-family file stamped in place: no id, no number, no move (§1.2)."""

    path: Path
    rel: str
    owner: str
    title: str


#: Directly-walked Reference scopes, `(rel_dir, owner)`, **each owner quoted from the §1
#: cell it is read from, beside the value rather than in a table of its own** — a second
#: place stating the same thing is what goes stale (`NT-0003`):
#:
#:   * `.claude/roles/` → `maintainer`, §1.6 *"Reference — charters | maintainer; 'a role
#:     file that proves insufficient' → `FD-` → maintainer amends"*.
#:   * `.claude/agents/` → `lead`, §1.6 *"Reference — agents | lead"*.
#:
#: Two values the maintainer's 2026-09-02 scoping admits — *"'Cite the cell' means §1 — a
#: §1.6 cell or a §1 sentence naming a role. §5.2 is the impact map and grants nothing"* —
#: so neither is derived from what a role ought to own.
#:
#: `.claude/skills/*/SKILL.md` is not here: its stamp target is a glob, not a directory's
#: contents, and it is handled separately below. Its owner is `lead` too, one standing
#: value, read from §1.6 *"Reference — skills"*' approves/retires cells and ruled by the
#: maintainer at `docs/plans/2026-09-02-w37-5c-slice-decision.md` §3.
#:
#: Every `README.md` under any of these is claimed by the README scope instead — the
#: cell-extent rule, `…-w37-rfc-readme-row-and-stamp-set.md` §2: *"A cell governs what its
#: text names; an index is the README row's."*
_REFERENCE_DIR_SCOPES: Final[tuple[tuple[str, str], ...]] = (
    (".claude/roles", "maintainer"),
    (".claude/agents", "lead"),
)

#: Every `README.md` inside the migration's own fixture corpus. `migrate` consumes that
#: tree as a **root** — it is another repository as far as this script is concerned — so a
#: real-tree run stamping a file inside it would corrupt the corpus every proof in
#: `tests/test_doc_id_migrate.py` is read against.
#:
#: **Listed one path at a time, not as the `tests/fixtures/docs-migration/` prefix that
#: would express it in one line**, because RFC §3's rule is that a fixture exemption is
#: declared *by name*: a prefix silently swallows every future file under it, and this
#: list is meant to be the thing that forces a decision when the fixture grows. All five
#: arrived with W37-5c itself — at `544b90c` the fixture carried no `README.md` at all,
#: which is why the RFC's own arithmetic was computed over 33 tracked READMEs and this
#: branch measures 38. **The count moved; the decomposition did not**: 38 tracked, 17
#: routed to `CR-`, 5 declared here, 2 §5.2/§5.3 delete, 1 check-35 fixture exempt →
#: **13 stamped**, of which 8 were already inside §4 step 5's roots and 5 are the ones
#: RFC §4 names as gained. Measured with
#: `[r for r in git_ls_files(root, ".") if Path(r).name == "README.md"]`, the same
#: predicate the scope itself uses.
#:
#: `tests/test_doc_id_migrate.py` asserts this equals the fixture's README set exactly, so
#: it can neither grow silently nor keep an entry whose file has gone.
_REFERENCE_FIXTURE_CORPUS_READMES: Final[tuple[str, ...]] = (
    "tests/fixtures/docs-migration/.claude/agents/README.md",
    "tests/fixtures/docs-migration/.claude/skills/README.md",
    "tests/fixtures/docs-migration/docs/README.md",
    # The four §5.2 regeneration sources. Added by W37-6's README-regeneration slice: the
    # corpus previously carried only `docs/workflows/README.md` of the five §5.2 rows
    # name, so four of the five branches in `_regenerate_family_readmes` had no fixture to
    # run against at all -- which is the state that let 36 dangling links reach the gate.
    "tests/fixtures/docs-migration/docs/adr/README.md",
    "tests/fixtures/docs-migration/docs/audit/README.md",
    "tests/fixtures/docs-migration/docs/notes/README.md",
    "tests/fixtures/docs-migration/docs/plans/README.md",
    "tests/fixtures/docs-migration/docs/audit/phases/1a/README.md",
    "tests/fixtures/docs-migration/docs/audit/work/W1/README.md",
    # W37-6's own `_discover_workflows` fixture (docs/workflows/wf-01-example-journey.md
    # needs a sibling `README.md` to prove that file, not this one, is what excludes a
    # directory's own index from discovery).
    "tests/fixtures/docs-migration/docs/workflows/README.md",
)

_REFERENCE_FIXTURE_CORPUS_REASON: Final = (
    "inside `tests/fixtures/docs-migration/`, the tree `migrate` is run *against* rather "
    "than content of this repository -- stamping it from a real-tree run would corrupt "
    "the fixture corpus every migration proof is read against"
)

#: Bucket 3 for the README scope: named files, each with its reason. Never a path prefix
#: — RFC §3's rule, and the reason `tests/fixtures/` is the first entry rather than the
#: directory it lives in.
_REFERENCE_README_EXCEPTIONS: Final[Mapping[str, str]] = {
    **{rel: _REFERENCE_FIXTURE_CORPUS_REASON for rel in _REFERENCE_FIXTURE_CORPUS_READMES},
    "tests/fixtures/docs-ids/w37-4-checks/check35-readme-allowlist/README.md": (
        "deliberately headerless — its own test says a header here \"would then also red "
        "check 30, contaminating this check-35 proof\". Exempt by "
        "docs/plans/2026-09-02-w37-rfc-readme-row-and-stamp-set.md §3, declared by name "
        "so the exemption cannot grow into a subtree"
    ),
}
# `docs/audit/README.md` used to be declared here, with the reason "the deletion is a hand
# step and is not built yet, so the file is still on disk". It is built now
# (`_regenerate_family_readmes`), so the file leaves this population the way the other two
# relocated READMEs do -- through `routed`, **by construction** rather than through a
# maintained entry, which is the same bargain F84's 17 already strike. A dead exception
# left in place is a statement that goes on reading true after it stopped being the reason.

_REFERENCE_FOREIGN_REASON: Final = (
    "in scope for §4 step 5 and NOT stamped by W37-5c: the file already carries the "
    "harness's own front matter, so its header must be MERGED into that block rather "
    "than prepended (`_docid.parse_header` reads exactly one block per file), and the "
    "keys must first be declared in `docs/_templates/REFERENCE.md` under Ruling 70. That "
    "is docs/plans/2026-09-02-w37-6-migration-run-leaf-plan.md §7.1 Task 1, W37-6's work"
)

#: Bucket 3 for the `.claude/` coverage scope below: every top-level entry no §4 step 5
#: root reaches, with the §5.3 row that dispositions it. `worktrees/` is absent
#: deliberately — it is `.gitignore`d, so a real checkout that has one gets it named here,
#: which is the correct outcome for a directory that is not part of the corpus.
_REFERENCE_CLAUDE_DIR_EXCEPTIONS: Final[Mapping[str, str]] = {
    "notes/": (
        "**RULED deleted, 2026-09-02** -- the maintainer, on the second RFC's dated "
        "amendment (`docs/plans/2026-09-02-w37-rfc-readme-row-and-stamp-set.md`, filed as "
        "PR #643): this directory's README goes with its stubs, \u00a75.3 governs, and "
        "\u00a74 step 4 is amended rather than \u00a75.6 carved out again. Three sections "
        "had disagreed -- \u00a75.3's row deletes \"stubs + README\", \u00a74 step 4 "
        "deleted \"the stubs\" and was silent on the README, and \u00a75.6 says \"every "
        "README outside `docs/` is Reference family and gets the header\" -- and the "
        "silence in step 4 was precisely how this file would have been stamped by "
        "accident. The reason the survival reading lost: the README's own text justifies "
        "it as what makes a frozen plan's citation still resolve, which is the job "
        "\u00a75.3 hands to `REDIRECTS.csv` in the same row that removes it. The 18 stubs "
        "are not in \u00a74 step 5's stamp set under any reading. Note the directory holds "
        "**18** stubs plus the README, not the 19 stubs \u00a75.3 counts"
    ),
    "settings.json": (
        "NT-0019 §5.3's only change for it is \"hook `statusMessage` citation\", kind "
        "`M` -- the blanket citation rewrite reaches it; §4 step 5 does not, and a JSON "
        "file cannot carry YAML front matter in any case (F83's population)"
    ),
    "CLAUDE.md": (
        "**no §5.3 row and no §4 step 5 root reaches it.** `.claude/CLAUDE.md` is the "
        "graphify instruction file; §4 step 5 stamps `.claude/roles/`, "
        "`.claude/skills/*/SKILL.md` and `.claude/agents/`, none of which matches a file "
        "directly under `.claude/`. Named here so the omission is listed rather than "
        "invisible; whether the standard should reach it is the maintainer's, not this "
        "slice's"
    ),
}

#: Bucket-2 sentinels — a file the migration accounts for by another mechanism, rather
#: than one it leaves unstamped. Distinct constants, not free-text, so `classify` below
#: tests identity instead of matching a prose string that a later edit could drift.
_ACCOUNTED_ALREADY_STAMPED: Final = "\0accounted:already-stamped"
_ACCOUNTED_ROUTED: Final = "\0accounted:routed-to-a-document-family"
_ACCOUNTED_VENDORED: Final = "\0accounted:vendored-skill-manifest-stamp-path"
_ACCOUNTED_MOVED: Final = "\0accounted:already-moved-by-an-earlier-run"


def _claude_dir_disposition(rel: str) -> str | None:
    """The `.claude/` coverage scope's reason for `rel`'s own top-level directory, or
    `None` when no entry covers it. Lets a file inside a dispositioned directory inherit
    that one statement instead of repeating it.

    The prefix is assembled from the constant's key rather than written out, which keeps
    this module free of a literal path `tests/test_notes_move_citations.py` forbids every
    living file from naming — the old notes root under `.claude`. That test's own
    docstring builds the same string by concatenation for the same reason.
    """
    marker = ".claude" + "/"
    if not rel.startswith(marker):
        return None
    head = rel[len(marker) :].split("/", 1)[0]
    return _REFERENCE_CLAUDE_DIR_EXCEPTIONS.get(head + "/")


def _reference_target(path: Path, rel: str, owner: str) -> _ReferenceStamp | str | None:
    """A stamp target, the reason this file is in scope but not stamped by this slice, or
    `None` for a file in scope whose shape this code does not recognise.

    `None` is Ruling 83's case and is deliberately *not* given a reason: a Reference file
    with no `# ` heading has no `title:` to read, and putting a disposition string here
    would turn "I cannot classify this" into "I have decided about this". Left
    unaccounted, so the census NAMES it -- the same bargain
    `_discover_audit_closure_readmes` strikes for a record README whose H1 it cannot read,
    and `_proposal_containers` for a container heading carrying no date.
    """
    text = path.read_text(encoding="utf-8")
    state = _front_matter_state(text)
    if state == "stamped":
        return _ACCOUNTED_ALREADY_STAMPED  # idempotency: a second run leaves it alone
    if state == "foreign":
        return _REFERENCE_FOREIGN_REASON
    heading = _REFERENCE_H1_RE.search(text)
    if heading is None:
        return None  # unrecognised shape -- the census names it rather than guessing
    return _ReferenceStamp(path=path, rel=rel, owner=owner, title=heading.group(1))


@dataclass(frozen=True)
class _ReferenceScopeCensus:
    """One scope's three buckets, kept apart so the census can reconcile them and the CLI
    can report the deferrals by name."""

    scope: str
    units: tuple[_CensusUnit, ...]
    stamped: tuple[str, ...]  # bucket 1 — stamped by this run
    #: Bucket 2 — accounted for by the migration itself rather than by this stamp path:
    #: a file already carrying this migration's own header (a second run's idempotency),
    #: or a `README.md` a *document* discovery claimed and moved into a family directory.
    #: Neither is "in scope and unstamped", so neither belongs on the deferral list.
    accounted: tuple[str, ...]
    excepted: dict[str, str]  # bucket 3 — every entry carries its reason


def nt0019_stamp_set(root: Path) -> list[str]:
    """Every tracked path at `root` that NT-0019 §4 step 5 stamps — this module's name for
    the population `migrate`'s Reference stamp scopes and its document discoveries have to
    cover between them.

    A thin call on purpose. The rule is stated once, in `_docid.in_stamp_set`, and both
    scripts that need it read it from there: `scripts/audit-docs.py`'s own
    `nt0019_stamp_set` (the corpus the F83 exemption register is reconciled against, and —
    through `_docid.stamp_set_files` — the population checks 30-39 enforce over) and this
    one. Naming it here rather than leaving it implicit in three scope loops is what makes
    the two consumers comparable: `test_the_two_stamp_set_consumers_read_one_definition`
    asserts set equality between them over the real corpus, which is a test that can only
    exist if both sides have a name.

    `git ls-files`, never a working-tree walk — the same reason `git_ls_files` is used for
    the README scope below: a walk sweeps in `.venv/`, `graphify-out/` and anything else
    untracked, and would quietly inflate every count taken from it.
    """
    stamp_set: list[str] = _docid.nt0019_stamp_set(git_ls_files(root, "."))
    return stamp_set


def _discover_reference_stamp_targets(
    root: Path, routed: Collection[str] = ()
) -> tuple[list[_ReferenceStamp], list[_ReferenceScopeCensus]]:
    """Every §4 step 5 Reference stamp target, plus the per-scope census the guard below
    reconciles. `routed` is the set of repo-relative paths a *document* discovery already
    claimed — the 17 F84 finds — so a README routed to `CR-` leaves this population by
    construction (RFC §1) instead of by a maintained exception list.

    The README population is read from `git ls-files`, not from a filesystem walk: §1.2's
    Reference row says *"every `README.md` anywhere in the tree"*, and the tree that
    sentence means is the tracked one. A walk would sweep in a `.venv/` or a build
    directory and quietly inflate every count taken from it.
    """
    targets: list[_ReferenceStamp] = []
    censuses: list[_ReferenceScopeCensus] = []
    #: Every `README.md` the README scope *saw*, whichever bucket it put it in -- not just
    #: the ones it stamped. The directory scopes below skip these, and the distinction is
    #: the whole safety: keyed on "stamped", a README that the README scope excepted or
    #: routed would fall through to `.claude/agents/` and be claimed a second time, which
    #: prepends a second header. No such file exists today, which is exactly why the
    #: narrower reading looked correct.
    readmes_seen: set[str] = set()

    def classify(units: list[_CensusUnit], scope: str, resolved: dict[str, object]) -> None:
        stamped: list[str] = []
        accounted: list[str] = []
        excepted: dict[str, str] = {}
        for key, outcome in resolved.items():
            if outcome is None:
                continue  # unrecognised: no bucket, so `_reconcile_census` names it
            if isinstance(outcome, _ReferenceStamp):
                targets.append(outcome)
                stamped.append(key)
            elif outcome in (
                _ACCOUNTED_ALREADY_STAMPED, _ACCOUNTED_ROUTED, _ACCOUNTED_VENDORED,
                _ACCOUNTED_MOVED,
            ):
                accounted.append(key)
            else:
                excepted[key] = str(outcome)
        censuses.append(
            _ReferenceScopeCensus(
                scope=scope, units=tuple(units), stamped=tuple(stamped),
                accounted=tuple(accounted), excepted=excepted,
            )
        )

    # --- the README scope, first: it owns every index, including those inside the
    # directory scopes below (RFC §2's cell-extent rule).
    units: list[_CensusUnit] = []
    resolved: dict[str, object] = {}
    for rel in git_ls_files(root, "."):
        if Path(rel).name != _docid.STAMP_SET_ANYWHERE:
            continue
        units.append(_CensusUnit(key=rel, locator=rel, text=rel))
        readmes_seen.add(rel)
        if not (root / rel).is_file():
            # Tracked but no longer on disk: an earlier `migrate` run in this same tree
            # moved it into a family directory and did not touch the index — git state is
            # the caller's to update, the same design choice `classify_docs_files` states
            # for its own read. Bucket 2, not an error: on a second run the 17 F84 claims
            # are exactly this, and `routed` is empty because there is nothing left to
            # claim. Reading it would raise `FileNotFoundError` mid-run, which is how
            # idempotency broke the first time this scope was wired up.
            resolved[rel] = _ACCOUNTED_MOVED
            continue
        if rel in routed:
            # Bucket 2, not an exception: §5.2 routes it to `CR-` and F84's discovery
            # moved it. It leaves this population **by construction** — the RFC §1 rule
            # that made routing the discriminator exists so there is no list to maintain.
            resolved[rel] = _ACCOUNTED_ROUTED
        elif rel in _REFERENCE_README_EXCEPTIONS:
            resolved[rel] = _REFERENCE_README_EXCEPTIONS[rel]
        elif (inherited := _claude_dir_disposition(rel)) is not None:
            # A README inside a `.claude/` directory the coverage scope below already
            # dispositions inherits that disposition rather than carrying a second entry
            # of its own. One statement about the directory, not two that can disagree
            # (NT-0003's mechanism) -- and it is why this file names no such directory as
            # a literal path: the prefix is built from the constant's own key.
            resolved[rel] = inherited
        else:
            resolved[rel] = _reference_target(root / rel, rel, "lead")
    classify(units, "every tracked README.md (the README row)", resolved)

    # --- `.claude/roles/` and `.claude/agents/`: every file under them.
    for rel_dir, owner in _REFERENCE_DIR_SCOPES:
        directory = root / rel_dir
        if not directory.is_dir():
            continue
        units, resolved = [], {}
        # `_docid.stamp_set_files`, not a bare walk: the population this scope stamps is
        # NT-0019 §4 step 5's, and `scripts/audit-docs.py` enforces over the same
        # predicate. One definition with two consumers, held to each other over the real
        # corpus by `test_the_two_stamp_set_consumers_read_one_definition` -- the two used
        # to state the rule separately and had already drifted (`F87`).
        for path in _docid.stamp_set_files(directory, root):
            rel = path.relative_to(root).as_posix()
            key = path.relative_to(directory).as_posix()
            if rel in readmes_seen:
                continue  # the README scope above already accounts for it
            units.append(_CensusUnit(key=key, locator=rel, text=key))
            resolved[key] = (
                _reference_target(path, rel, owner)
                if path.suffix == ".md"
                else "not a markdown document -- §4 step 5 stamps documents"
            )
        classify(units, f"{rel_dir}/ (NT-0019 §4 step 5)", resolved)

    # --- `.claude/skills/*/SKILL.md`. The census units are the skill **directories**, not
    # the manifests: counting the manifests would count with step 5's own glob, and a
    # skill directory that has lost its `SKILL.md` -- or spells it differently -- is
    # exactly the unit that glob cannot see (§5.4: "every `SKILL.md` (46)").
    skills_dir = root / ".claude" / "skills"
    if skills_dir.is_dir():
        units, resolved = [], {}
        for directory in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            key = f"{directory.name}/SKILL.md"
            rel = f".claude/skills/{key}"
            units.append(_CensusUnit(key=key, locator=rel, text=key))
            manifest = directory / "SKILL.md"
            if not manifest.is_file():
                continue  # no record, no exception -- the census names the directory
            outcome = _reference_target(manifest, rel, "lead")
            # A vendored manifest this path *could* stamp is the vendored stamp path's,
            # not this one's: NT-0019 §1.5 gives it two extra fields (`vendored: true`,
            # `origin:`) that only that writer supplies, and stamping it here as well
            # would write the header twice. Ordered after `_reference_target`, not
            # before it, deliberately: a vendored manifest carrying the harness's own
            # front matter -- which all 28 real ones do -- is deferred with the other 53
            # rather than reported as handled, because the vendored path cannot stamp it
            # either. It skips any manifest `_docid.parse_header` reads, and it reads 25
            # of the 28; the other 3 raise `HeaderError` and are F83's own third row
            # (`create-adaptable-composable`, `planning-with-files`, `vue-best-practices`
            # -- named in `docs/plans/2026-09-02-w37-rfc-bucket-c-owner-values.md` §2.1,
            # all three vendored). **The two populations are distinct and only overlap by
            # those 3**: F83's 65 are files that cannot carry front matter *in any form*,
            # while these 53 can and already do -- someone else's. Both are unblocked by
            # different work: F83 by its ruled exemption, these by W37-6's Task 1 merge.
            if isinstance(outcome, _ReferenceStamp) and _is_vendored_skill_manifest(manifest):
                outcome = _ACCOUNTED_VENDORED
            resolved[key] = outcome
        classify(units, ".claude/skills/*/SKILL.md (NT-0019 §4 step 5)", resolved)

    # --- coverage: is every top-level entry of `.claude/` reached by a scope above, or
    # dispositioned by §5.3? Without this, the three scopes above are each internally
    # total -- every file they walk gets a bucket -- so the only thing that could still be
    # "outside the question" is a population none of them walks at all. That is exactly
    # F84's shape one level up, and it is the failure this unit finder exists to catch: a
    # new `.claude/<something>/` of governed documents is unaccounted here on the day it
    # appears, rather than the day someone notices it was never stamped.
    claude_dir = root / ".claude"
    if claude_dir.is_dir():
        units, resolved = [], {}
        for entry in sorted(claude_dir.iterdir()):
            key = entry.name + ("/" if entry.is_dir() else "")
            units.append(_CensusUnit(key=key, locator=f".claude/{key}", text=key))
            if key in ("roles/", "agents/", "skills/"):
                resolved[key] = _ACCOUNTED_ROUTED  # a scope above walks it
            elif key in _REFERENCE_CLAUDE_DIR_EXCEPTIONS:
                resolved[key] = _REFERENCE_CLAUDE_DIR_EXCEPTIONS[key]
        classify(units, ".claude/ (every top-level entry — is it in a scope?)", resolved)

    # The scopes overlap by design -- an index inside `.claude/agents/` is in two of them,
    # and the cell-extent rule decides which claims it. A file claimed twice would be
    # stamped twice, the second header landing in front of the first, and nothing
    # downstream would say so: `frozen_file_matches_after_migration_stamp` strips one
    # leading block. Checked here rather than left to the one overlap that exists today.
    claimed = [t.rel for t in targets]
    if len(set(claimed)) != len(claimed):
        twice = sorted({rel for rel in claimed if claimed.count(rel) > 1})
        raise ValueError(
            f"migrate: Reference stamp target(s) claimed by more than one scope: {twice} "
            "-- each would be stamped once per claim. Decide which scope owns them (the "
            "cell-extent rule) rather than letting both write."
        )
    return targets, censuses


def _check_reference_stamp_set_not_silently_unrecognised(
    censuses: Sequence[_ReferenceScopeCensus],
) -> None:
    """Ruling 83's census over §4 step 5's Reference stamp set: every file in scope is a
    stamp target, this migration's own prior output, or a **declared** exception carrying
    its reason -- and anything else is NAMED.

    The unit finder is independent of the stamp rule in every scope: `git ls-files` for
    the READMEs (not a walk of the directories that happen to hold one today), every file
    under `.claude/roles/` and `.claude/agents/` (not just the `.md` the stamp reaches),
    and the skill **directories** rather than the `*/SKILL.md` glob step 5 is written in.
    """
    for census in censuses:
        _reconcile_census(
            scope=census.scope,
            units=census.units,
            records=set(census.stamped),
            is_body=lambda unit, _seen=frozenset(census.accounted): unit.key in _seen,
            exceptions=census.excepted,
        )


def _stamp_reference_targets(root: Path, targets: Sequence[_ReferenceStamp]) -> list[str]:
    """Write each target's Reference header ahead of its existing body. Same mechanism as
    the vendored-manifest stamp below it in `migrate`, and same `docs/_templates/
    REFERENCE.md` substitution: a field that family's template does not declare cannot
    appear (Ruling 70's guarantee, applied to the writer).
    """
    written: list[str] = []
    for target in targets:
        header = _stamp_header(
            "REFERENCE", None, kind=None, title=target.title, status="active",
            created=_module_first_commit_date(target.path, root), owner=target.owner,
            was=None,
        )
        body = target.path.read_text(encoding="utf-8")
        target.path.write_text(header + "\n" + body, encoding="utf-8")
        written.append(target.rel)
    return written

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


def _path_rewrite_tokens(old_rel: str, new_rel: str) -> dict[str, str]:
    """Every citing-prose form of a moved path this migration is proven to need, mapped
    old -> new -- found live, not assumed: the auditor caught `docs/roadmap.md` citing
    a merged-away path as `[docs/audit/phases/1b/register.md](audit/phases/1b/
    register.md)` -- the **link text** is the repo-relative form (`docs/...`), the
    **link target** is the `docs/`-relative form (no leading `docs/`), because
    `roadmap.md` lives one level inside `docs/` and a same-tree relative link omits the
    shared prefix. Both forms are added (the second only when `old_rel` starts with
    `docs/`, since a path outside `docs/` has no such shorter form to strip); each is a
    literal substring match via `_rewrite_citations`, so a form neither of these three
    covers (a deeper relative path, `../...`, from a file two or more directories below
    `docs/`) is not rewritten by this set and would need adding if the corpus is ever
    found to use it -- not assumed absent, just not yet proven present.

    A **third** form: `docs/audit/register.md`'s own F28 row cites `pilot-findings.md` as
    `[work/nt-0010-0011-adoption/pilot-findings.md](work/nt-0010-0011-adoption/pilot-
    findings.md)` -- a link relative to `docs/audit/`, the shared parent every file that
    used to live under it once assumed, because the citing file (`register.md`) and the
    cited file (`pilot-findings.md`) were both there. Post-migration the citing content
    moves wholesale into `docs/findings/register.md`, and every `docs/findings/`-bound
    essay this migration produces (every `FD-` document, `pilot-findings.md`'s own
    Ruling-99 destination included) is a sibling of that file, not a `docs/audit/`
    subpath any more -- so the correct replacement is relative to `docs/findings/`, the
    one directory this migration's `docs/audit/`-relative citers are actually proven to
    still share with their target. Added only when `old_rel` starts with `docs/audit/`
    and `new_rel` starts with `docs/findings/`, the two conditions the F28 case actually
    satisfies -- not a general "strip any shared prefix" rule, which would silently
    manufacture a resolvable-looking token for a pair that shares no real directory.
    """
    tokens = {old_rel: new_rel}
    prefix = "docs/"
    if old_rel.startswith(prefix) and new_rel.startswith(prefix):
        tokens[old_rel[len(prefix) :]] = new_rel[len(prefix) :]
    audit_prefix, findings_prefix = "docs/audit/", "docs/findings/"
    if old_rel.startswith(audit_prefix) and new_rel.startswith(findings_prefix):
        tokens[old_rel[len(audit_prefix) :]] = new_rel[len(findings_prefix) :]
    # A **fourth** form: the bare basename, which is what a sibling writes when the citing
    # file and the cited file share a directory -- `docs/plans/PL-00761-...md` linking to
    # `[the slice map](2026-08-22-w6b-slice-map.md)`. Measured on the real corpus at the
    # tree this branch was built on: **167 dangling links in 70 surviving files**, every
    # one of them a `docs/plans/` file citing a sibling `docs/plans/YYYY-MM-DD-*.md` that
    # this run renames to `PL-<n>-*.md`. The count was **identical before and after the
    # split-source fix**, which is what identifies it as a class of its own rather than a
    # residue of that defect -- Ruling 100's three forms never covered it, because all
    # three carry a directory and this one carries none.
    #
    # It is **not** emitted here, because unlike the three forms above it is not safe to
    # apply tree-wide: a bare `2026-08-22-w6b-slice-map.md` only means this file when the
    # citing file sits in the directory the cited file sat in, and its correct replacement
    # depends on that same directory. `_bare_basename_rewrite` below returns it keyed by
    # that directory, and `_rewrite_citations` applies it only to files inside it.
    return tokens


def _path_citation_redirect_rows(old_rel: str, new_rel: str) -> list[dict[str, str]]:
    """Task 4 item 4: one `REDIRECTS.csv` row per real (non-no-op) citation form
    `_path_rewrite_tokens(old_rel, new_rel)` adds to the tree-wide sweep, for an id-less
    move (register.md, a reference move, the unstampable-CSV move, the phase-1b register
    deletion) -- every one of which already gets an `old_path`/`new_path` row recording
    *that the file moved*, but none of which previously got an `old_id`/`new_id` row
    recording *what a citation of it looked like*. `(g)`'s inverse and the class-4
    split-body check both read only `old_id`/`new_id`; a tree-wide token with no such row
    is unrewritable in the merge-base direction even though the forward sweep already
    rewrites it, cited or not, from any directory (`_path_rewrite_tokens`' own docstring:
    these three forms are safe applied tree-wide). `old_path`/`new_path` are left blank —
    a citation form is not itself a moved file.

    Derived from the same generator the forward sweep calls, never retyped, so the two
    cannot drift the way a hand-maintained second list of forms would.
    """
    return [
        {"old_id": old_tok, "new_id": new_tok, "old_path": "", "new_path": ""}
        for old_tok, new_tok in _path_rewrite_tokens(old_rel, new_rel).items()
        if old_tok != new_tok  # a no-op form (register.md's own unchanged basename) needs no row
    ]


def _drop_contested_split_redirects(
    pairs: Sequence[tuple[str, str]],
) -> list[tuple[str, str]]:
    """`(old, new)` pairs with any `old` whose `new` disagrees across occurrences dropped
    entirely -- never a raise, and never an arbitrary pick of one occurrence's answer.

    `_SplitSource.resolve`'s own contract is that different occurrences of the *same*
    citing text may legitimately determine *different* targets (an id/anchor/line-span
    determinant reads the citing line, never a directory) -- unlike a compound's expansion
    (a pure function of the token and the global map, never the occurrence), this list can
    and does contain the same `old` mapped to two different `new` values. Found live
    against a real multi-ruling file (`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`,
    splitting into `RL-00190`/`RL-00191`/…, each citation determining its own sibling
    correctly): passing such a pair straight to `_write_redirects` crashes the whole
    migration, because #726's own write-time guard ("one legacy id must resolve to
    exactly one new id") cannot tell this shape apart from the allocation bug it exists to
    catch. Filtered here with the identical collision-safe philosophy
    `classify_migration_diff`'s own `_collision_safe_inverse` already applies on the read
    side: a genuinely contested `old` contributes no row at all, and the file(s) whose
    citation it was correctly, silently keep neither an inverse nor a crash -- named by
    `(g)`'s own residue accounting rather than by an exception here. An *exact* repeat
    (the same `old` -> the same `new`, more than once) is not a conflict and survives.
    """
    by_old: dict[str, set[str]] = {}
    for old, new in pairs:
        by_old.setdefault(old, set()).add(new)
    return [(old, next(iter(news))) for old, news in by_old.items() if len(news) == 1]


def _bare_basename_rewrite(old_rel: str, new_rel: str) -> tuple[str, str, str] | None:
    """`(citing_dir, bare_token, replacement)` for a moved file's **bare-basename** citing
    form, or `None` where there is none.

    A file cited by a sibling is written as a bare filename -- `docs/plans/PL-00761-….md`
    linking to `[the slice map](2026-08-22-w6b-slice-map.md)`. None of
    `_path_rewrite_tokens`' three forms covers it, because all three carry a directory and
    this one carries none. Measured on the real corpus at the tree this branch was built
    on: **167 dangling links in 70 surviving files**, every one of them a `docs/plans/`
    file citing a sibling `docs/plans/YYYY-MM-DD-*.md` this run renames -- and the count
    was **identical before and after the split-source fix**, which is what identifies it as
    a class of its own rather than a residue of that defect.

    **The `citing_dir` scope is what makes the token safe, and it is not optional.** A bare
    basename is the most collision-prone token this migration could substitute: applied
    tree-wide, `README.md` or `register.md` would match every mention anywhere. Scoped to
    the one directory in which that basename resolved to this file, it cannot match a
    different file's name -- two files never share a basename inside one directory -- and
    the replacement is a link that still resolves from that directory, computed with
    `posixpath.relpath` rather than assumed to be a sibling: a move *out* of the directory
    is rewritten to `../rulings/RL-….md`, which is what the citing file needs, and is
    exactly the case the same-directory-only reading of this rule left dangling.
    """
    old_dir, _, old_base = old_rel.rpartition("/")
    if not old_dir:
        return None
    replacement = posixpath.relpath(new_rel, old_dir)
    if replacement == old_base:
        return None
    return (old_dir, old_base, replacement)


class TokenMapCollisionError(RuntimeError):
    """Two moves claim the same citation token with different destinations.

    #672 built `token_map` as a flat `dict[old_path, new_path]` and filled it with
    `dict.update`, which is silent about a key it overwrites. Twenty-seven source paths in
    the real corpus split into 2-21 targets each, so the *last* draft off the discovery
    list won every one of them and every citation of those paths was repointed to an
    arbitrary sibling — a link that resolves and lies, which gate condition 7's
    dangling-link net cannot see precisely because it resolves. This is the loud version:
    a split source never reaches the flat map at all (it goes to `_SplitSource`, which
    resolves per citation or declines), and any *other* duplicate key raises here rather
    than being absorbed.
    """


def _add_tokens(
    token_map: dict[str, str], origins: dict[str, str], tokens: Mapping[str, str],
    source: str,
) -> None:
    """`token_map.update`, except that a key already claimed by a different source is a
    raise naming both claimants rather than a silent overwrite.
    """
    for tok, new in tokens.items():
        prior = origins.get(tok)
        if prior is not None:
            raise TokenMapCollisionError(
                f"citation token {tok!r} is claimed twice: {prior} -> "
                f"{token_map[tok]!r} and {source} -> {new!r}"
            )
        token_map[tok] = new
        origins[tok] = source


_ANCHOR_HEADING_RE: Final = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def _anchor_slug(heading_text: str) -> str:
    """A markdown heading's `#anchor` form, GitHub's rule: lowercase, punctuation dropped,
    runs of whitespace to single hyphens. Used only to test whether an anchor a citation
    *already carries* names exactly one of a split source's targets — never to mint one —
    so a dialect difference costs a resolution (bucket iv, left alone), never a wrong one.
    """
    text = heading_text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text).strip("-")


@dataclass(frozen=True)
class _SplitTarget:
    """One destination a split source's citations might mean."""

    new_rel: str
    new_token: str  # the destination form of the *citing* token form this target answers
    ids: tuple[str, ...]  # every id form that names this record — old token and canonical
    anchors: frozenset[str]
    line_span: tuple[int, int] | None  # 1-based inclusive, in the SOURCE file
    body_line_offset: int  # lines the destination file puts before this body
    canonical_id: str  # the destination's own `id:`, for the index row
    title: str  # the destination's own `title:`, for the index row


@dataclass(frozen=True)
class _SplitSource:
    """A source path this migration splits into more than one destination, and the only
    three ways a citation of it is allowed to be rewritten.

    Authority: Ruling 89 (`docs/plans/2026-09-02-w37-container-family-and-line-citations-
    rulings.md` §3) — *"a rewrite that changes only the path is forbidden"* — as the
    maintainer extended it from the line-offset case it was written for to the path-only
    case. A citation is rewritten **only when the citation itself determines which target
    it means**, by (i) an id adjacent to the path, (ii) an `#anchor` matching exactly one
    target's heading, or (iii) a line number falling inside exactly one target's span in
    the source file — Ruling 89's re-derivation, done here rather than by hand. Anything
    else is left exactly as it is: it dangles, gate condition 7 lists it, and it is
    dispositioned by name. **Detection is not repair, and a citation that is wrong while
    resolving is worse than one that fails loudly.**
    """

    old_rel: str
    token: str  # the citing form (repo-relative, `docs/`-relative, ...) this covers
    targets: tuple[_SplitTarget, ...]
    # Ruling 101 clause 1, the maintainer's extension of Ruling 100 (§2.5): a citation that
    # determines nothing resolves to **the family index's section for this source** —
    # `docs/<family>/INDEX.md#<old-basename>`, in this token's own citing form. That is not
    # a fourth determinant and not a canonical-target choice (§3.3 forbids both): the
    # section lists *every* target with its `was:` provenance, so the link is the
    # `REDIRECTS.csv` row made navigable, and a reader lands on the whole ambiguity rather
    # than on one arm of it chosen for them. Because it is always available, **bucket (iv)
    # is 0 by construction** — there is no citation of a split source this class cannot
    # answer.
    index_token: str
    index_rel: str  # the same target, repo-relative, for the clause-3 check to open
    index_anchor: str

    @property
    def pattern(self) -> re.Pattern[str]:
        return re.compile(
            rf"\b{re.escape(self.token)}\b"
            r"(?:#(?P<anchor>[A-Za-z0-9_-]+))?"
            r"(?::(?P<l1>\d+)(?:-(?P<l2>\d+))?)?"
        )

    def _by_id(self, line: str) -> set[int]:
        return {
            i for i, t in enumerate(self.targets)
            if any(re.search(rf"\b{re.escape(tok)}\b", line) for tok in t.ids)
        }

    def _by_anchor(self, anchor: str | None) -> set[int]:
        if anchor is None:
            return set()
        return {i for i, t in enumerate(self.targets) if anchor.lower() in t.anchors}

    def _by_line(self, lines: list[int]) -> set[int]:
        if not lines or any(t.line_span is None for t in self.targets):
            return set()
        found: set[int] = set()
        for i, t in enumerate(self.targets):
            span = t.line_span
            assert span is not None  # guarded above
            if all(span[0] <= n <= span[1] for n in lines):
                found.add(i)
        return found

    def resolve(self, match: re.Match[str], line: str) -> str | None:
        """The replacement text for one occurrence, or `None` for "leave it alone".

        Each of the three mechanisms votes for a set of targets; a mechanism that names
        exactly one target is *determining*. The rewrite happens when the determining
        mechanisms agree on one target and no other — two mechanisms disagreeing is
        exactly the case with no answer, and gets the same treatment as no evidence at
        all.
        """
        anchor = match.group("anchor")
        raw_lines = [match.group("l1"), match.group("l2")]
        nums = [int(n) for n in raw_lines if n is not None]
        determined: set[int] = set()
        for voters in (self._by_id(line), self._by_anchor(anchor), self._by_line(nums)):
            if len(voters) == 1:
                determined |= voters
        if len(determined) != 1:
            return None
        target = self.targets[next(iter(determined))]
        out = target.new_token
        if anchor is not None:
            out += f"#{anchor}"
        if nums:
            span = target.line_span
            if span is None:  # unreachable: `_by_line` returns nothing without spans
                return None
            derived = [target.body_line_offset + (n - span[0] + 1) for n in nums]
            out += ":" + "-".join(str(n) for n in derived)
        return out


#: The per-family split-source index Ruling 101 clause 1 introduces. One file per document
#: family directory, generated by `_write_split_source_indexes` **after** the citation
#: sweep, for the same reason `_stamp_reference_targets` runs after it: the section bodies
#: quote each target's `was:` provenance, which is by definition a pre-migration path, and
#: a sweep that saw it would rewrite the very provenance the section exists to carry.
_SPLIT_INDEX_BASENAME: Final = "INDEX.md"


def _split_index_rel(family_dir: str) -> str:
    return f"docs/{family_dir}/{_SPLIT_INDEX_BASENAME}"


def _split_index_anchor(old_rel: str) -> str:
    """The `#anchor` a citation of `old_rel` resolves to inside its family index.

    Ruling 101 clause 1 names it *"`#<old-basename>`"*. It is derived here from the same
    string `_write_split_source_indexes` renders as the section's heading, and through the
    same `_anchor_slug`, so the anchor and the heading cannot disagree — the failure mode
    the clause-3 check exists to catch, made structurally impossible on the writing side as
    well as detectable on the reading side.
    """
    return _anchor_slug(_split_index_heading(old_rel))


def _split_index_heading(old_rel: str) -> str:
    return old_rel.rsplit("/", 1)[-1]


def _split_index_family(old_rel: str, new_rels: Sequence[str]) -> str:
    """The family directory whose `INDEX.md` carries `old_rel`'s section.

    **Ruling 101 clause 1 says `docs/<family>/INDEX.md` and reads as though a split source
    had one family. It does not.** Measured on the fixture corpus, three sources split
    *across* families: `_discover_plain_plans` emits a whole-file `PL-` draft for a plan and
    `_discover_lettered_rulings` emits an `RL-` draft for each `## Ruling N` heading inside
    that same plan, so `docs/plans/2026-08-30-adoption.md` becomes one `PL-` and two `RL-`.
    Flagged to the lead as a premise of the clause that does not hold, rather than worked
    around silently.

    **The rule below is a placement rule, not a target choice, and the distinction is the
    whole reason it is allowed to be arbitrary.** The section lists every target from every
    family whatever directory the file sits in, so a reader who follows the link sees the
    same complete ambiguity either way; nothing about which document the citation *meant*
    is decided here. Ruling 100 §3.3's prohibition is on picking a destination *record* for
    a citation, and this picks none. What the rule must be is **deterministic and stable** —
    the same source must land at the same anchor on every run, or the link the sweep wrote
    last time stops resolving — and sorting supplies exactly that with no data of its own.
    """
    outside = sorted(rel for rel in new_rels if not rel.startswith("docs/"))
    if outside:
        raise TokenMapCollisionError(
            f"{old_rel} splits to {outside} outside docs/ — Ruling 101's index section "
            "has no family directory to live in"
        )
    return sorted({rel.split("/")[1] for rel in new_rels})[0]


def _build_split_sources(
    old_rel: str, targets: Sequence[tuple[_Draft, str]]
) -> list[_SplitSource]:
    """One `_SplitSource` per *citing form* of `old_rel` (`_path_rewrite_tokens` emits up
    to three), each carrying the same target list mapped into that form.
    """
    index_rel = _split_index_rel(
        _split_index_family(old_rel, [new_rel for _, new_rel in targets])
    )
    index_forms = _path_rewrite_tokens(old_rel, index_rel)
    anchor = _split_index_anchor(old_rel)
    by_token: dict[str, list[_SplitTarget]] = {}
    for draft, new_rel in targets:
        forms = _path_rewrite_tokens(old_rel, new_rel)
        ids = [t for t in (draft.old_token, _docid.canonical(draft.prefix, draft.number))
               if t]
        anchors = frozenset(
            _anchor_slug(m.group(1)) for m in _ANCHOR_HEADING_RE.finditer(draft.body)
        )
        for tok, new_tok in forms.items():
            by_token.setdefault(tok, []).append(
                _SplitTarget(
                    new_rel=new_rel, new_token=new_tok, ids=tuple(ids), anchors=anchors,
                    line_span=draft.source_line_span,
                    body_line_offset=draft.body_line_offset,
                    canonical_id=_docid.canonical(draft.prefix, draft.number),
                    title=draft.title,
                )
            )
    sources: list[_SplitSource] = []
    for tok, ts in by_token.items():
        # A citing form only some of the targets can be written in is not a form this
        # source can be resolved in at all. The bare-basename form is the case that makes
        # this real: it exists only for a target that stayed in the source's own directory,
        # so a source splitting across directories has it for some targets and not others,
        # and a `_SplitSource` built from that subset would silently offer a *narrowed*
        # candidate list -- a citation determining "exactly one target" out of a list the
        # other targets were quietly dropped from. That is the mis-resolution Ruling 100
        # was written about, arriving by a different door. Such a form is skipped, and its
        # citations are left for the dangling-link scanner to list by name.
        if len(ts) != len(targets):
            continue
        index_token = index_forms.get(tok)
        if index_token is None:
            # A citing form the targets have but the index does not. Structurally this is
            # `_path_rewrite_tokens`' third form, which is emitted only for a
            # `docs/audit/` -> `docs/findings/` pair; an index in any other family has no
            # equivalent. Raised rather than silently dropped, because the alternative is a
            # citation in that form falling out of bucket (iv)'s "0 by construction" with
            # nothing saying so.
            raise TokenMapCollisionError(
                f"{old_rel} is cited as {tok!r}, a form its family index {index_rel!r} "
                "has no equivalent of — Ruling 101's fallback cannot be written in it"
            )
        sources.append(
            _SplitSource(
                old_rel=old_rel, token=tok, targets=tuple(ts),
                index_token=f"{index_token}#{anchor}",
                index_rel=index_rel, index_anchor=anchor,
            )
        )
    return sources


def _build_bare_split_source(
    old_rel: str, targets: Sequence[tuple[_Draft, str]]
) -> tuple[str, _SplitSource] | None:
    """`(citing_dir, source)` for a split source's **bare-basename** citing form, or `None`
    where it has none.

    The `_build_split_sources` counterpart of `_bare_basename_rewrite`, and needed for the
    same measured reason: after the directory-carrying forms were fixed, the residue of the
    dangling-link scan was **29 links, all of them a `docs/plans/` file citing a sibling
    that this run splits** -- so a split source needs the bare form as much as a
    single-target move does. Every target and the family-index fallback are mapped through
    `posixpath.relpath` from the citing directory, so all three of Ruling 100's
    determinants and Ruling 101's fallback answer in the form the citing file can use.
    """
    old_dir, _, old_base = old_rel.rpartition("/")
    if not old_dir:
        return None
    index_rel = _split_index_rel(
        _split_index_family(old_rel, [new_rel for _, new_rel in targets])
    )
    anchor = _split_index_anchor(old_rel)
    split_targets: list[_SplitTarget] = []
    for draft, new_rel in targets:
        ids = [t for t in (draft.old_token, _docid.canonical(draft.prefix, draft.number))
               if t]
        split_targets.append(
            _SplitTarget(
                new_rel=new_rel,
                new_token=posixpath.relpath(new_rel, old_dir),
                ids=tuple(ids),
                anchors=frozenset(
                    _anchor_slug(m.group(1))
                    for m in _ANCHOR_HEADING_RE.finditer(draft.body)
                ),
                line_span=draft.source_line_span,
                body_line_offset=draft.body_line_offset,
                canonical_id=_docid.canonical(draft.prefix, draft.number),
                title=draft.title,
            )
        )
    index_token = posixpath.relpath(index_rel, old_dir)
    return (
        old_dir,
        _SplitSource(
            old_rel=old_rel, token=old_base, targets=tuple(split_targets),
            index_token=f"{index_token}#{anchor}",
            index_rel=index_rel, index_anchor=anchor,
        ),
    )


@dataclass(frozen=True)
class _UnresolvedCitation:
    """One citation of a split source that named no single target — bucket (iv). Carried
    out of the run by name, never counted: "27 sources are ambiguous" is not something a
    reader can disposition, and a disposition by name is what the ruling asks for.

    Under Ruling 101 clause 1 every one of these is **rewritten to the family index's
    section** rather than left to dangle (`resolved_to`), so the population this carries is
    "the citations that determined nothing", not "the citations nothing was done about".
    The distinction matters to the two counts `_cmd_migrate` prints: this list is bucket
    (iv), and the count of citations left *unrewritten* is separately reported and is 0.
    """

    citing_file: str
    line: int
    old_rel: str
    text: str
    candidates: tuple[str, ...]
    resolved_to: str  # the citing form actually written into the file
    index_rel: str  # the same target repo-relative, so the clause-3 check can open it
    index_anchor: str


_FRONT_MATTER_WAS_LINE_RE: Final = re.compile(r"^was:.*$", re.MULTILINE)


def _was_field_spans(text: str) -> list[tuple[int, int]]:
    """The character spans `_rewrite_citations` must leave byte-identical: every `was:`
    line inside a leading front-matter block.

    Ruling 101 clause 2: *"`was:` is provenance, not a citation. It is written from
    `REDIRECTS.csv` and is excluded from `_rewrite_citations`."* Ruling 100 §1.4 measured
    what its inclusion costs — every migrated document carrying a non-null `was:` ends up
    naming a path that never existed pre-migration, and for a split source it names an
    arbitrary sibling's new path, so `was:` cannot recover the origin it exists to record.

    Scoped to the **leading front matter**, not to every `was:`-shaped line and not to the
    whole header. A `was:` in a body is prose and is swept like any other prose; the
    header's other fields (`supersedes:`, `relates:`, ...) carry *ids*, which are citations
    and must keep being rewritten — widening this to the whole block would silently stop
    that, which is a regression wearing the ruling's clothes.
    """
    if not text.startswith("---\n"):
        return []
    close = text.find("\n---\n", len("---"))
    if close == -1:
        return []
    return [
        (m.start(), m.end())
        for m in _FRONT_MATTER_WAS_LINE_RE.finditer(text, 0, close + len("\n---\n"))
    ]


#: Ruling 102 §2 row (g) (`docs/plans/2026-09-03-w37-6-ruling-102-verify-instrument.md`,
#: "On (g)"), the maintainer's own diagnosis: *"A rewrite may not match inside a longer
#: identifier."* A word boundary is not that rule. `\b` sits between a token's trailing
#: digit and a following `/` or `-`, so `\bNFR-RATE-13\b` matches inside `NFR-RATE-13/14`
#: — one identifier expression naming two requirements in shorthand — and rewriting there
#: leaves `NFR-775/14`: one real requirement and one meaningless fragment. Measured on the
#: migrated tree at `0de529e`: 391 such fragments, against 0 on the un-migrated control.
#:
#: The continuation this refuses is a separator **followed by a digit**, because that is
#: what the corpus at `e97b97a` actually holds. Enumerated, not inferred from the ruling's
#: two-part example: slash compounds run to twelve parts
#: (`NFR-MODEL-1/2/3/4/5/7/8/9/10/11/12`); hyphen ranges exist (`FR-RATE-46-49`,
#: `FR-PLAT-18-20`); the `NT-`, `ADR-` and `Ruling ` families carry the same slash form
#: (`NT-0010/0011`, `ADR-0001/0002`, `Ruling 86/87`); and 113 occurrences of the
#: `W<n>-<n>-<n>` slice-task form contain a live slice id as their literal prefix, which
#: is the case that shows the rule is about identifiers rather than about citation
#: shorthand.
#:
#: A separator followed by a **letter** is not a continuation and must still rewrite:
#: `OQ-GOV-7-shaped` is the whole id used adjectivally, and a blunt "never match before a
#: hyphen" rule would silently stop migrating it. The leading side deliberately carries no
#: guard beyond `\b`: `token_map` also holds repo-relative **path** tokens, and a path
#: legitimately appears preceded by `/` inside a longer path.
#:
#: What happens to a continued expression is **nothing** — it is left byte-identical — and
#: that is forced rather than chosen. §7 (g)'s own predicate
#: (`audit-docs.py:frozen_file_matches_after_migration_stamp`) accepts a migrated file when
#: inverting `REDIRECTS.csv` over it reproduces the merge-base bytes, and that inverse is
#: per-token: no expansion of a compound into new ids can round-trip through it
#: (`NFR-775/776` inverts to `NFR-RATE-13/NFR-RATE-14`, not to `NFR-RATE-13/14`). The
#: legacy ids that therefore survive inside a compound are §7 (d)'s population, ruled
#: separately (Ruling 102 §2 row 3), not this row's to invent an answer for.
def _whole_token_re(tok: str) -> re.Pattern[str]:
    """`tok` as a whole identifier: word-bounded, and not continued by `-`/`/` plus a digit."""
    return re.compile(rf"\b{re.escape(tok)}\b(?![-/][0-9])")


#: A compound-continuation token, base plus its whole chain: `\btok` then zero or more
#: `[-/]\d+` groups, captured as one string. Group `continuation` is empty for a plain,
#: uncontinued token — the common case, handled the same as `_whole_token_re` always did.
#:
#: **`\b` between `tok` and the continuation group — row (b)'s W37-6 regression, #711,
#: fixed by #721.** Without it this pattern is `\btok` with no trailing boundary at all,
#: so it matches `tok` as a bare PREFIX of a longer, unrelated identifier that merely
#: starts with the same digits: a mapped `OQ-OVR-1` (-> `OQ-831`) matched inside the
#: un-mapped, ambiguous `OQ-OVR-11`, `_expand_compound` saw an empty continuation and
#: returned the mapped value unchanged, and `.sub()` left the un-matched trailing `1` in
#: place: `OQ-OVR-11` -> `OQ-831` + `1` = `OQ-8311`, a fabricated id nothing allocated.
#: The identical mechanism also caught `wf-01` matching inside `wf-010` (task 4's own
#: wf-0n regression) — a digit followed by a digit is never a word-boundary transition,
#: so the `\b` immediately after `tok` refuses *both* shapes in one place: a genuine
#: continuation (`NFR-RATE-13/14`) still passes it (digit -> `-`/`/` *is* a transition),
#: while a bare second digit or dot with nothing separating it does not.
#:
#: Task #30's range ruling (W37-6 channel `:526`) adds the sibling alternative
#: `range_end`, with its *own* trailing `\b` rather than the shared one above: `..` is
#: itself a boundary-worthy transition (`FR-PLAT-1..4` has a `\b` between `1` and `.`
#: for free), so nothing stops the continuation alternative from also matching here with
#: zero repetitions and returning `tok` alone — exactly the row (b) defect one level up,
#: this time surviving the `\b`-after-`tok` fix because that boundary is satisfied
#: (digit -> `.` *is* a transition) regardless of which alternative is meant. Trying the
#: range shape *first*, as one more alternative rather than a second sweep, is what makes
#: the choice atomic: whichever alternative's own anchors are satisfied wins the position
#: outright, with no second pass free to reinterpret what the first already matched.
def _compound_token_re(tok: str) -> re.Pattern[str]:
    escaped = re.escape(tok)
    return re.compile(
        rf"\b{escaped}(?:\.\.(?P<range_end>[0-9]+)\b|\b(?P<continuation>(?:[-/]\d+)*))"
    )


_CONTINUATION_PART_RE: Final = re.compile(r"([-/])(\d+)")


#: Task 4 item 3 (W37-6 channel `:318-330`, the maintainer's compound-citation ruling,
#: reversing what Ruling 102 §2 row (g)'s own comment above called "not this row's to
#: invent an answer for"). A compound citation — `NFR-RATE-13/14`, `NT-0010/0011`,
#: `Ruling 86/87`, `FR-RATE-46-49` — is rewritten by mapping **every** component
#: separately, never the base alone with the tail carried. A sibling component is
#: reconstructed by keeping the base token's own prefix (everything before its trailing
#: digit run) and appending the continuation's own digits verbatim — `NFR-RATE-` + `14` for
#: `NFR-RATE-13/14`'s second half, `NT-` + `0011` for `NT-0010/0011`'s (preserving whatever
#: padding the citation itself already used, never re-padding).
#:
#: **If every component maps, the whole compound is replaced and the pair is recorded** —
#: `(g)`'s inverse (`audit_docs.frozen_file_matches_after_migration_stamp`) treats the
#: compound as one more token via `REDIRECTS.csv`'s generic `old_id`/`new_id` columns, so
#: the round-trip holds without any change to `audit-docs.py` (`redirects_inverse` there is
#: built as a flat `{new_id: old_id}` dict off every `REDIRECTS.csv` row, with no notion of
#: what a row's tokens "mean").
#:
#: **If any component does not map, the whole compound comes out byte-identical** — Ruling
#: 102 §2 row (g)'s forced outcome, unchanged: this is not a weaker attempt at (g)'s old
#: behaviour, it is the same behaviour, now reached by a token that *could* have expanded
#: but had an unmapped sibling (task 4 item 2's classified-token table is where that
#: sibling belongs, not a half-rewrite here).
#:
#: **Never for a `W<n>[a-z]?` work key** — found live, against the fixture corpus, before
#: this shipped: `W1` mapped and followed by `-1` is not a two-part compound citing `W1`
#: and a sibling `W1` again, it is `W1-1`, an entirely different, longer identifier (a
#: *slice* key one level down from the *work* key `W1`) — exactly Ruling 102 §2 row (g)'s
#: own "the rule is about identifiers, not about citation shorthand" case
#: (`test_ruling_102_g_a_longer_identifier_that_is_itself_a_token_still_rewrites`), and
#: task 4's ruling never named the `W`/`WK`/`SL` family among the compound-shorthand
#: families it lists (`NFR`, `NT`, `ADR`, `Ruling`) — every one of those has a stable
#: `<prefix>-<module>-` or `<prefix>-`/`Ruling ` head with the number the only thing that
#: varies; a `W` key's own trailing digit *is* the identifier, one level of the hierarchy
#: at a time, so appending another never means "another instance of the same thing".
_WORK_FAMILY_TOKEN_RE: Final = re.compile(r"^W\d+[a-z]?(-\d+)*$")


def _expand_compound(
    tok: str, mapped: str, active_map: Mapping[str, str], m: re.Match[str],
    derived: list[tuple[str, str]],
) -> str:
    continuation = m.group("continuation")
    if not continuation:
        return mapped
    if _WORK_FAMILY_TOKEN_RE.match(tok):
        return m.group(0)  # a longer identifier, never a compound -- leave it whole
    prefix_match = re.search(r"\d+$", tok)
    if prefix_match is None:
        # No trailing digit run on the base token itself -- not a shape this ruling
        # reaches (every enumerated family's legacy citation ends in digits). Defensive,
        # not reachable by any corpus token today: leave it whole rather than guess.
        return m.group(0)
    prefix = tok[: prefix_match.start()]
    parts = _CONTINUATION_PART_RE.findall(continuation)
    mapped_siblings: list[tuple[str, str]] = []
    for sep, digits in parts:
        sibling_mapped = active_map.get(prefix + digits)
        if sibling_mapped is None:
            return m.group(0)  # one unmapped component -- the whole compound stays whole
        mapped_siblings.append((sep, sibling_mapped))
    # Shorthand preserved, the maintainer's own worked example (W37-6 channel `:322-330`):
    # `NFR-RATE-13/14` -> `NFR-775/776`, not `NFR-775/NFR-776` -- the base is written in
    # full and each further component only its own trailing number, exactly the citation's
    # own input convention. Only sound when the sibling's new id shares the base's new
    # prefix (new family and module can differ from the old ones in principle, even if not
    # in the corpus today); a sibling that lands in a different family is written in full
    # rather than have its own prefix silently discarded.
    new_prefix = mapped.rsplit("-", 1)[0] + "-" if "-" in mapped else None
    parts_out: list[str] = []
    for sep, sibling_mapped in mapped_siblings:
        if new_prefix is not None and sibling_mapped.startswith(new_prefix):
            parts_out.append(sep + sibling_mapped[len(new_prefix) :])
        else:
            parts_out.append(sep + sibling_mapped)
    replacement = mapped + "".join(parts_out)
    derived.append((m.group(0), replacement))
    return replacement


#: Task #30's range ruling (W37-6 channel `:526`, extending the maintainer's compound
#: ruling to the `..` shape): `FR-PLAT-1..4` names the **set** of consecutive legacy ids
#: `FR-PLAT-1, FR-PLAT-2, FR-PLAT-3, FR-PLAT-4` -- unlike a compound's shorthand list, a
#: range's members are not written out, so this is the one shape a mapped-lookup cannot
#: skip: every member in `[start, end]` must be constructed from the base token's own
#: prefix and looked up before any rewrite can happen at all.
#:
#: **The new ids are not consecutive**, so the citation cannot be rewritten as a new range
#: (`FR-680..703` would silently claim three ids in between that the range never named) --
#: it is **enumerated**, every mapped id written out in full, comma-separated (the
#: maintainer's own worked example: `FR-PLAT-1..4` -> `FR-680, FR-681, FR-702, FR-703`).
#:
#: **If every member maps, the whole range is replaced and the pair is recorded** — the
#: identical mechanism `_expand_compound` already uses (`derived`, consumed by `(g)`'s
#: inverse through `REDIRECTS.csv`'s generic `old_id`/`new_id` columns, no `audit-docs.py`
#: change needed).
#:
#: **If any member does not map, or the range is not ascending, the whole citation comes
#: out byte-identical** — the same forced "leave it whole" outcome §7 (g) already gives an
#: unmapped compound component, reached here for the identical reason: a half-enumerated
#: range is worse than one left alone.
def _expand_range(
    tok: str, mapped: str, active_map: Mapping[str, str], m: re.Match[str],
    derived: list[tuple[str, str]],
) -> str:
    prefix_match = re.search(r"\d+$", tok)
    if prefix_match is None:
        # No trailing digit run on the base token itself -- every family this shape is
        # proven to occur in (`FR`, `NFR`, `OQ`, `DEP`) ends in digits; defensive, not
        # reachable by any corpus token today.
        return m.group(0)
    prefix = tok[: prefix_match.start()]
    start = int(prefix_match.group())
    end = int(m.group("range_end"))
    if end <= start:
        # Not an ascending range (`FR-PLAT-4..1`, or a citation that happens to repeat
        # its own number) -- not a shape any corpus token proves, and guessing what it
        # meant is worse than leaving it whole.
        return m.group(0)
    mapped_members: list[str] = [mapped]
    for n in range(start + 1, end + 1):
        member_mapped = active_map.get(prefix + str(n))
        if member_mapped is None:
            return m.group(0)  # one unmapped member -- the whole range stays whole
        mapped_members.append(member_mapped)
    replacement = ", ".join(mapped_members)
    derived.append((m.group(0), replacement))
    return replacement


def _rewrite_citations(
    root: Path, token_map: Mapping[str, str], split_sources: Sequence[_SplitSource] = (),
    dir_token_map: Mapping[str, Mapping[str, str]] = types.MappingProxyType({}),
    dir_split_sources: Mapping[str, Sequence[_SplitSource]] = types.MappingProxyType({}),
    derived_redirects: list[tuple[str, str]] | None = None,
    dir_redirects: list[tuple[str, str, str]] | None = None,
    split_redirects: list[tuple[str, str]] | None = None,
) -> tuple[list[str], list[_UnresolvedCitation], list[_UnresolvedCitation]]:
    """Sweep every tree file, rewriting each citation token to its destination.

    Returns `(changed_files, index_resolved, unrewritten)`. `index_resolved` is Ruling
    100's bucket (iv) — the citations of a split source that determined no single target
    and were therefore sent to the family index section (Ruling 101 clause 1) — and
    `unrewritten` is the citations left exactly as they were, which is **0 by
    construction**: every `_SplitSource` carries an `index_token`, so the "leave it alone"
    branch has no way to fire. It is still returned, and still printed, because a
    population reported only when non-empty is a population nothing can audit.

    `derived_redirects`, when given, is appended to in place with one `(old, new)` pair
    per compound citation this run fully expanded (task 4 item 3) — the caller's job is
    turning each into a `REDIRECTS.csv` row (`old_id`/`new_id`, no path) so `(g)`'s inverse
    can consume it. `None` (the default, and every existing caller before this task) means
    "nobody wants them" — an internal throwaway list is used instead of branching the
    substitution logic on whether the caller cares.

    `dir_redirects`, when given, is appended to in place with one `(citing_dir, old, new)`
    triple per `dir_token_map` (bare-basename, directory-scoped) substitution this run
    actually performed (task 4 item 4) — never for a tree-wide `token_map` token, whose
    move is already recorded globally by the caller's own per-draft `REDIRECTS.csv` row.
    A directory-scoped token's text is only correct *from that one citing directory* —
    `../audit/register.md` resolves to a different real file than the identical text would
    from a directory at a different depth — so the caller records it with that scope, not
    as a global pair.

    `split_redirects`, when given, is appended to in place with one `(old, new)` pair per
    split-source citation this run actually resolved to one concrete target (task #30's
    ruling, W37-6 channel "the cause table dispositions"). `_SplitSource.resolve` decides
    *which* target a citation with no recorded alternative meant — by an adjacent id, an
    `#anchor` or a line span, never by directory — and until this parameter existed the
    decision was thrown away the moment it was made: `repl` below returned `out` and
    recorded nothing, so `(g)`'s inverse (built off `REDIRECTS.csv`'s `old_id`/`new_id`
    columns) had no row for a bare path citation of a source that split into more than one
    document (`docs/audit/register.md` resolving to one phase's own target is the
    measured case — `.claude/roles/lead.md`'s own worked example). Scoped globally, like
    `derived_redirects`, never per `citing_dir` like `dir_redirects`: a `_SplitSource`'s
    determinants (id, anchor, line span) read the citation and its own line, never the
    citing file's directory, so the same literal old text means the same thing from any
    file that resolves it the same way — and where two files resolve the identical old
    text to two different targets, the collision-safe inverse this feeds already drops the
    contested key rather than guess, exactly as it does for an ambiguous compound.

    The same list also carries one pair per citation Ruling 101 clause 1's family-index
    fallback answers (`src.index_token`, when no determinant names one target) — measured
    live alongside the resolved case (`backend/src/app/platform/settings.py` citing a
    plan with no adjacent id) and strictly safer to record: every occurrence that reaches
    the fallback for one `_SplitSource` gets the identical `index_token`, a property of
    the source itself rather than of the one occurrence, so there is no per-occurrence
    ambiguity for the collision-safe inverse to even need to arbitrate.
    """
    changed: list[str] = []
    index_resolved: list[_UnresolvedCitation] = []
    unrewritten: list[_UnresolvedCitation] = []
    derived: list[tuple[str, str]] = (
        derived_redirects if derived_redirects is not None else []
    )
    dir_derived: list[tuple[str, str, str]] = (
        dir_redirects if dir_redirects is not None else []
    )
    split_derived: list[tuple[str, str]] = (
        split_redirects if split_redirects is not None else []
    )
    tree_by_token: dict[str, _SplitSource] = {s.token: s for s in split_sources}
    # One ordering over both kinds, longest first for the reason the flat map already
    # needed it: a shorter token's word boundary must not consume part of a longer one.
    tree_ordered = sorted({*token_map, *tree_by_token}, key=len, reverse=True)
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
        rel = path.relative_to(root).as_posix()
        # The directory-scoped half: a bare-basename token means *this* file only for a
        # citer inside the directory the cited file sat in, so it joins the token set for
        # exactly those citers and for nobody else (`_bare_basename_rewrite`). Merged per
        # file rather than tree-wide, and re-sorted with the rest, because the
        # longest-token-first ordering has to hold across both halves or a bare basename
        # can eat the tail of a longer path token.
        citing_dir = posixpath.dirname(rel)
        local_map = dir_token_map.get(citing_dir)
        local_splits = dir_split_sources.get(citing_dir)
        if local_map or local_splits:
            active_map: Mapping[str, str] = {**token_map, **(local_map or {})}
            by_token = {
                **tree_by_token, **{s.token: s for s in (local_splits or ())}
            }
            ordered = sorted({*active_map, *by_token}, key=len, reverse=True)
        else:
            active_map, by_token, ordered = token_map, tree_by_token, tree_ordered

        def sweep(
            segment: str, line_offset: int, rel: str = rel,
            active_map: Mapping[str, str] = active_map,
            by_token: Mapping[str, _SplitSource] = by_token,
            ordered: Sequence[str] = ordered,
            local_map: Mapping[str, str] | None = local_map,
            citing_dir: str = citing_dir,
        ) -> str:
            for tok in ordered:
                if tok not in segment:
                    continue
                split = by_token.get(tok)
                if split is None:

                    def _sub(
                        m: re.Match[str], t: str = tok, v: str = active_map[tok],
                        lmap: Mapping[str, str] | None = local_map, cdir: str = citing_dir,
                    ) -> str:
                        out = (
                            _expand_range(t, v, active_map, m, derived)
                            if m.group("range_end") is not None
                            else _expand_compound(t, v, active_map, m, derived)
                        )
                        if lmap is not None and t in lmap and out != m.group(0):
                            dir_derived.append((cdir, m.group(0), out))
                        return out

                    segment = _compound_token_re(tok).sub(_sub, segment)
                    continue

                def repl(m: re.Match[str], src: _SplitSource = split) -> str:
                    line_start = m.string.rfind("\n", 0, m.start()) + 1
                    line_end = m.string.find("\n", m.end())
                    line = m.string[line_start : line_end if line_end != -1 else None]
                    out = src.resolve(m, line)
                    if out is not None:
                        if out != m.group(0):
                            split_derived.append((m.group(0), out))
                        return out
                    record = _UnresolvedCitation(
                        citing_file=rel,
                        line=line_offset + m.string.count("\n", 0, m.start()) + 1,
                        old_rel=src.old_rel,
                        text=line.strip(),
                        candidates=tuple(t.new_rel for t in src.targets),
                        resolved_to=src.index_token,
                        index_rel=src.index_rel,
                        index_anchor=src.index_anchor,
                    )
                    if not src.index_token:  # unreachable: `_build_split_sources` raises
                        unrewritten.append(record)
                        return m.group(0)
                    index_resolved.append(record)
                    # Ruling 101 clause 1's bucket (iv) fallback is a substitution too --
                    # measured live (task #30's own triage, `backend/src/app/platform/
                    # settings.py` citing `docs/plans/2026-08-29-w11-slices-3-4-
                    # rulings.md`): every citation of one split source that lands here
                    # gets the identical `index_token` (it is the source's own field, not
                    # derived from this one occurrence), so recording the pair is safe
                    # with no per-occurrence ambiguity at all -- unlike `src.resolve`'s
                    # determinant, which reads the citing line and so could in principle
                    # differ between two occurrences of the same literal old text, this
                    # fallback cannot.
                    if src.index_token != m.group(0):
                        split_derived.append((m.group(0), src.index_token))
                    return src.index_token

                segment = split.pattern.sub(repl, segment)
            return segment

        # The sweep runs over the segments **between** the protected `was:` lines rather
        # than over the whole text, so a protected line is not "rewritten and put back" —
        # it is never passed to a substitution at all. Protected spans are whole lines and
        # no citation token contains a newline, so no match can straddle a boundary and be
        # lost by the partition. `line_offset` keeps a bucket-(iv) record's reported line
        # number in the file's own numbering rather than the segment's.
        pieces: list[str] = []
        cursor = 0
        for start, end in _was_field_spans(text):
            pieces.append(sweep(text[cursor:start], text.count("\n", 0, cursor)))
            pieces.append(text[start:end])
            cursor = end
        pieces.append(sweep(text[cursor:], text.count("\n", 0, cursor)))
        text = "".join(pieces)

        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(rel)
    return changed, index_resolved, unrewritten


def _protected_was_lines(text: str) -> frozenset[int]:
    """0-based line numbers `_was_field_spans` protects, converted from character spans.

    A `was:` field occupies exactly one physical line (front matter, one key per line),
    so a span's own line number is enough — no line ever needs two spans.
    """
    return frozenset(text.count("\n", 0, start) for start, _ in _was_field_spans(text))


def _normalize_padded_citations(root: Path) -> list[str]:
    """A padded citation of a real governed thing, outside a filesystem path and outside a
    fenced exhibit, is not the citation's correct form (`_docid.canonical` — NT-0019 §1.1
    rule 2: unpadded, always) and the migration normalises it exactly as it normalises
    every other legacy citation — #25's ruling (`docs/plans/README.md`'s frozen-plan
    exception, "a change that preserves the claim exactly while fixing how it is
    addressed", read against Ruling 103 §5.1: normalising a citation's form is the
    migration's own established remedy, not a new one).

    Reuses `_docverify`'s conjuncts 1-3 (`_PADDED_ID_RE`, `_MD_EMPHASIS_RE`,
    `_in_path_context`, `_unpadded`, `index_ids`) rather than a second implementation —
    Ruling 103 §1.8's last violation, *"two implementations of one rule that are never
    compared are two rules"*, applied to the rewrite rather than only to the row. Fenced
    exhibits are conjunct 0's own exclusion and are never rewritten, by construction: an
    exhibit's padded value is the observation, and Ruling 103 §5.1 fences it instead
    (`docs/plans/2026-09-03-w37-6-ruling-100-split-source-citations.md`,
    `docs/plans/2026-09-03-w37-6-ruling-103-ef-readings-and-index-placement.md`).

    `repl` re-locates each match in the cleaned line by *position* (its own ordinal among
    same-line matches), not by text — the identical fix `padded_hits.PaddedHit.seq` makes
    on the read side, needed here too since two occurrences of the same padded id can
    share one line (a `was:` path exhibit followed by a bare citation of the same id,
    exactly `docs/rulings/RL-00290-...md`'s own §5.3: `` `was:
    docs/ledgers/LG-00030-....md`, **including `LG-00030` itself...` ``). Matching by text
    let the bare occurrence inherit the path occurrence's TRUE verdict and skip rewriting
    — the write-side half of the same Ruling 103 §1.8 violation the docstring above
    already names, found by this row moving from PASS to FAIL once the read side alone
    was fixed and the write side was not.

    Runs after `_regenerate_index_for_migrate`, because conjunct 3's authority is the
    POST-migration `docs/INDEX.md` — the only index a padded token's unpadded form can
    resolve against, and the same reason row (e) itself reads `docs/INDEX.md` fresh rather
    than the pre-migration corpus's.
    """
    resolvable = _docverify.index_ids(root)
    changed: list[str] = []
    for path in _iter_tree_files(root):
        if _is_vendored_exempt(path, root):
            continue
        if path.name == "REDIRECTS.csv":
            continue  # never a citation, never rewritten -- conjunct 0's own exclusion
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not _docverify._PADDED_ID_RE.search(text):
            continue
        protected = _protected_was_lines(text)
        lines = text.split("\n")
        in_fence = False
        touched = False
        for i, line in enumerate(lines):
            if _docverify._FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence or i in protected:
                continue
            if not _docverify._PADDED_ID_RE.search(line):
                continue

            seq_counter = itertools.count()

            def repl(
                m: re.Match[str], line: str = line, seq_counter: Iterator[int] = seq_counter
            ) -> str:
                token = m.group(0)
                seq = next(seq_counter)
                # Conjunct 2, exactly as `_docverify.padded_hits` tests it: strip markdown
                # emphasis, then ask whether *this occurrence's own position* — not text,
                # per `PaddedHit.seq` — sits in a path-shaped token. A padded id inside a
                # filename is not a citation to normalise. Stripping asterisks never adds,
                # removes or reorders a `_PADDED_ID_RE` match, so the cleaned line's
                # `seq`-th match is still this match's own occurrence.
                cleaned = _docverify._MD_EMPHASIS_RE.sub("", line)
                cleaned_hits = list(_docverify._PADDED_ID_RE.finditer(cleaned))
                cm = cleaned_hits[seq] if seq < len(cleaned_hits) else None
                if cm is not None and _docverify._in_path_context(
                    cleaned, cm.start(), cm.end()
                ):
                    return token
                # Conjunct 3: only a token that resolves is a citation; one that does not
                # is a specimen of the form, and normalising it would be inventing a
                # citation of nothing.
                unpadded_token = _docverify._unpadded(token)
                return unpadded_token if unpadded_token in resolvable else token

            new_line = _docverify._PADDED_ID_RE.sub(repl, line)
            if new_line != line:
                lines[i] = new_line
                touched = True
        if touched:
            path.write_text("\n".join(lines), encoding="utf-8")
            changed.append(path.relative_to(root).as_posix())
    return changed


# ---------------------------------------------------------------------------------------
# Phase E — regenerate. `docs/REDIRECTS.csv` (append-only across runs, the same convention
# `widen`'s `_append_redirects` already uses for the identical file) and `docs/INDEX.md`
# (rendered fresh every run via `doc-index.py`'s own `build_corpus`/`render_index` — a pure
# function of the corpus, so a run that found nothing new reproduces byte-identical output,
# which is exactly what idempotency needs).
# ---------------------------------------------------------------------------------------


def _check_redirect_rows_agree_on_every_old_id(rows: Iterable[dict[str, str]]) -> None:
    """Refuse rather than silently write a `docs/REDIRECTS.csv` where one `old_id` would
    resolve to two different `new_id`s.

    Keyed on `(old_id, citing_dir)`, never `old_id` alone: a `citing_dir`-scoped row (task
    4 item 4's bare-basename relative-link form — see `_REDIRECTS_FIELDS`'s own comment)
    is only correct *from that one citing directory*, so the identical `old_id` text
    legitimately repeats, once per citing directory, each a genuinely different row. An
    `old_id` of `""` (every id-less move's row) is exempt for the same reason every other
    check here already treats it specially: it names no id at all, and two such rows differ
    only by path, which this check does not read.

    An *exact* repeat — the same `(old_id, citing_dir)` mapped to the same `new_id` twice
    (a compound citation, say `NFR-RATE-13/14`, cited more than once and expanded
    identically each time) is harmless and allowed; only a **conflict** — the same key
    claimed for two *different* destinations — is refused. This is what closes the write
    boundary for the defect `_discover_requirements`'s own dedup guard fixes at the source
    (its docstring has the mechanism): a second, independent discovery of the same legacy
    id producing a second, different allocation must not reach the file at all, even if a
    future discovery path reintroduces the bug this guard did not anticipate.
    """
    seen: dict[tuple[str, str], str] = {}
    for row in rows:
        old_id = row.get("old_id", "")
        if not old_id:
            continue
        key = (old_id, row.get("citing_dir", ""))
        new_id = row.get("new_id", "")
        prior = seen.get(key)
        if prior is not None and prior != new_id:
            raise ValueError(
                f"REDIRECTS.csv: old id {old_id!r} is already recorded -> {prior!r}; "
                f"refusing to also record it -> {new_id!r} -- one legacy id must resolve "
                "to exactly one new id (a second, independent discovery of the same "
                "legacy id is the defect, not a second valid row)"
            )
        seen[key] = new_id


def _redirect_row_sort_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    """Sort key for one `REDIRECTS.csv` row: `old_id` then `old_path`, per the
    dispatched follow-up ("row-order is non-deterministic across independent
    `migrate()` runs -- same rows, different order -- it should be sorted by `old_id`
    then `old_path` before writing").

    The two named fields alone are not a total order: two rows can legitimately share
    both (`_check_redirect_rows_agree_on_every_old_id`'s own docstring names the
    `citing_dir`-scoped case, and an exact-repeat compound-citation row is a second,
    identical duplicate of the two-key prefix). Without a full tie-break, two
    independent runs that discover such a pair in different internal order would sort
    each pair's own order back in as a stable-sort artifact, which is exactly the
    non-determinism this sort exists to remove. Appending the remaining
    `_REDIRECTS_FIELDS` columns (`new_id`, `new_path`, `citing_dir`) makes the key a
    total order over the full row, so the two named fields still decide first while
    every row still lands at one fixed position regardless of discovery order.
    """
    return (
        row.get("old_id", ""),
        row.get("old_path", ""),
        row.get("new_id", ""),
        row.get("new_path", ""),
        row.get("citing_dir", ""),
    )


def _write_redirects(root: Path, rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return []
    redirects_path = root / "docs" / "REDIRECTS.csv"
    redirects_path.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, str]] = []
    if redirects_path.is_file():
        with redirects_path.open(newline="", encoding="utf-8") as fh:
            existing = list(csv.DictReader(fh))
    _check_redirect_rows_agree_on_every_old_id([*existing, *rows])
    all_rows = sorted([*existing, *rows], key=_redirect_row_sort_key)
    with redirects_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_REDIRECTS_FIELDS)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)
    return ["docs/REDIRECTS.csv"]


def _regenerate_index_for_migrate(root: Path) -> list[str]:
    # `root`, not the default: a later, independent `doc-index.py --check` run against
    # `root` must see the identical generator this call used — `_load_doc_index`'s own
    # docstring has the mechanism and why the default would disagree with it.
    doc_index = _load_doc_index(root)
    corpus = doc_index.build_corpus(root / "docs")
    fresh = doc_index.render_index(corpus)
    (root / "docs" / "INDEX.md").write_text(fresh, encoding="utf-8")
    return ["docs/INDEX.md"]


#: `audit-docs.py` check 27 (Ruling 45): the two `meta` fields the digest check reads.
#: Line-targeted, not `json.loads`/`json.dumps` round-tripped -- re-serialising the whole
#: file would reformat every other key (indent width, key order) into an unrelated diff a
#: reviewer did not ask for, the same reason `_sweep_title` substitutes inside a string
#: rather than rebuilding the artifact that carries it.
_PROCESS_SPEC_REL: Final = "docs/process/delivery-process.md"
_PROCESS_CORE_REL: Final = "docs/process/delivery-process.core.json"
_PROCESS_CORE_DIGEST_LINE_RE: Final = re.compile(
    r'^(\s*"derived_from_digest":\s*")[^"]*(",?\s*)$', re.MULTILINE
)
_PROCESS_CORE_TREE_LINE_RE: Final = re.compile(
    r'^(\s*"verified_against_tree":\s*")[^"]*(",?\s*)$', re.MULTILINE
)


def _reconcile_process_core_digest(root: Path) -> list[str]:
    """Check 27 (Ruling 45): `docs/process/delivery-process.core.json`'s
    `meta.derived_from_digest` records a `sha256:` digest of `docs/process/
    delivery-process.md`'s exact bytes, paired with the commit last reconciled
    (`meta.verified_against_tree`), and reds whenever the two disagree.

    The corpus-wide citation sweep (`_rewrite_citations`, already run by the time this is
    called) rewrites the spec's own legacy-form citations exactly like any other file's --
    which is exactly the class of edit the digest exists to catch, so a migrated tree
    reds check 27 by construction on a change no human reviewed as *this file's* content
    edit (it is the identical mechanical token sweep every other file in the diff
    received, and the migration PR's own review is the "forced re-read" Ruling 45 asks
    for). `migrate()` reconciling its own edit in the same commit is the fix, not a
    standing red nothing discharges.

    A no-op wherever the pair does not both exist (true of every unit-test fixture --
    neither file is part of any fixture corpus) or `root` carries no resolvable git
    `HEAD` (a bare fixture with no `.git` at all): `verified_against_tree` needs a real
    commit to mean anything -- "read `git diff <this>..HEAD`" is the field's whole
    purpose -- and there is nothing safe to write in its place.
    """
    spec_path = root / _PROCESS_SPEC_REL
    core_path = root / _PROCESS_CORE_REL
    if not spec_path.is_file() or not core_path.is_file():
        return []
    text = core_path.read_text(encoding="utf-8")
    if not (
        _PROCESS_CORE_DIGEST_LINE_RE.search(text)
        and _PROCESS_CORE_TREE_LINE_RE.search(text)
    ):
        return []
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        return []
    tree = proc.stdout.strip()
    digest = "sha256:" + hashlib.sha256(spec_path.read_bytes()).hexdigest()
    new_text = _PROCESS_CORE_DIGEST_LINE_RE.sub(rf"\g<1>{digest}\g<2>", text)
    new_text = _PROCESS_CORE_TREE_LINE_RE.sub(rf"\g<1>{tree}\g<2>", new_text)
    if new_text == text:
        return []
    core_path.write_text(new_text, encoding="utf-8")
    return [_PROCESS_CORE_REL]


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
# NT-0019 §5.2's README regeneration.
#
# Five `README.md` files are index files whose rows link to their siblings by a **bare
# relative path** (`(0001-phase-boundary-plan-review.md)`) rather than by a recognised id
# token. `_rewrite_citations` maps id tokens and repo-relative path strings; neither form
# appears in these rows, so the whole class was invisible to it. At `2ae31f7` the auditor's
# general dangling-link scanner -- every `](...)` in every surviving file, resolved
# relative to its citing file, checked against the full deleted set -- found **36** live
# links in these five files resolving to paths the migration deletes. That is what stopped
# the W37-6 run (`docs/plans/2026-09-03-w37-6-renewed-window-handover.md` §6).
#
# §5.2 already says what happens to each of the five, and the rows are the specification
# this section implements -- not an invention of this code:
#
#   * `adr/000n-*.md (6) + README`  -> "`adrs/ADR-<nnnnn>-*.md`; ... README **generated**"
#   * `notes/00nn-*.md (18) + README` -> "`rfcs/RFC-0nnnn-*.md`; ... **README rewritten**,
#     index table dropped for `INDEX.md`"
#   * `workflows/wf-0n-*.md (5) + README` -> "`WF-0nnnn-*.md`, stamped; **README table
#     generated**"
#   * `plans/2026-*.md (125) + README` -> "README: **naming and four-kinds table ->
#     pointer**; the nine writing conventions **kept verbatim**"
#   * `audit/README.md` -> "**deleted**; content to `findings/` and `closures/` READMEs"
#
# and the row above them all -- "`INDEX.md`, `REDIRECTS.csv`, `_templates/`,
# `process/document-ids.md`, `closures/README.md`, `findings/README.md`,
# `rulings/README.md`, `ledgers/README.md` | **new**" -- is why four family READMEs are
# written rather than the two the `docs/audit/README.md` row names on its own.
#
# The two moves are §1.4's, not this section's: `docs/adr/` and `docs/notes/` are not in
# §1.4's tree at all (`adrs/` and `rfcs/` are), and "`docs/audit/` dissolves into
# `findings/`, `closures/`, `research/` and `process/`" is the same paragraph's last
# sentence. A README left behind is also what keeps each of those three legacy directories
# non-empty, so `_remove_if_empty` cannot dissolve them -- the layout rule and the dangling
# links have one cause between them.
#
# **The link repointing is mechanical, never hand-typed.** `_repoint_relative_links` below
# resolves each target against the citing file's own directory and looks the result up in
# the run's own old->new move map, the same map `REDIRECTS.csv` and `_path_rewrite_tokens`
# are built from. Hand-editing 36 targets would produce a fix that is correct for this
# corpus and silently wrong for the next one; keyed on the move map, a target this run did
# not move is left exactly as it was, and one it did move cannot be missed.
# ---------------------------------------------------------------------------------------

#: The three READMEs §5.2 does not leave where it found them. Registered here rather than
#: inside `_regenerate_family_readmes` because `migrate` needs them **before**
#: `_rewrite_citations`: a third document citing `docs/audit/README.md` by path is exactly
#: as stale as one citing any other moved file, and the redirect row is owed for the same
#: reason every id-less move already gets one (NT-0019 §4 step 1).
#:
#: `docs/audit/README.md` maps to `docs/findings/README.md` because that is where the
#: larger half of its content goes -- the register, the finding essays and the conventions.
#: The closure half lands in `docs/closures/README.md`, which no redirect can also name;
#: `REDIRECTS.csv` carries one destination per old path, and a split's second destination
#: is recorded by the surviving README's own prose, which points at its sibling.
_README_FAMILY_MOVES: Final[Mapping[str, str]] = {
    "docs/adr/README.md": "docs/adrs/README.md",
    "docs/notes/README.md": "docs/rfcs/README.md",
    "docs/audit/README.md": "docs/findings/README.md",
}

#: Directory-shaped link targets (`[../adr/](../adr/)`) resolve to a directory, never to a
#: file, so they are absent from a move map built out of file moves and would survive a
#: repoint untouched -- pointing at a directory this migration removes. The two legacy
#: document directories §1.4 replaces are named here so a link written at the directory
#: rather than at a file inside it moves with everything else. `docs/audit/` is deliberately
#: absent: it dissolves into four directories rather than becoming one, so there is no
#: single destination to repoint such a link to, and a dangling directory link there is
#: reported by the scanner rather than silently sent somewhere plausible.
_README_LEGACY_DIR_MOVES: Final[Mapping[str, str]] = {
    "docs/adr": "docs/adrs",
    "docs/notes": "docs/rfcs",
}

#: The two §5.2 rows whose README stays where it is -- `workflows` ("README table
#: generated") and `plans` ("naming and four-kinds table -> pointer").
_README_IN_PLACE: Final[tuple[str, ...]] = (
    "docs/workflows/README.md", "docs/plans/README.md",
)

#: The families §5.2's `new` row asks for a README that has no predecessor to carry over:
#: "`closures/README.md`, `findings/README.md`, `rulings/README.md`, `ledgers/README.md`".
#: `findings/` is absent because it is `docs/audit/README.md`'s destination in
#: `_README_FAMILY_MOVES` above and is written by carrying that file, not created empty.
#: Named by **family prefix** rather than by path so the directory stays
#: `_DOCUMENT_FAMILY_DIR`'s to state -- a family renamed there cannot leave a README
#: behind in a directory nothing else writes to.
_README_NEW_FAMILY_PREFIXES: Final[tuple[str, ...]] = ("CR", "RL", "LG")

#: Every path §5.2's README rows write, on both sides of the migration. **Ruling 104 §2
#: ratifies this set as class 6 -- "a generated artifact regenerated in full" -- as
#: *members* of the property, not as a path exclusion**: the `adr` row says "README
#: **generated**", `workflows` "README table **generated**", `notes` "**README
#: rewritten**", `plans` "naming and four-kinds table -> pointer", and `audit/README.md`
#: "**deleted**; content to `findings/` and `closures/` READMEs". A regenerated README
#: cannot satisfy `frozen_file_matches_after_migration_stamp`, which asks whether a body
#: survived stripping and token-inversion unchanged -- the whole point of these rows is
#: that the body does not survive, because the list it carries is a list of files that
#: moved.
#:
#: **This constant is not the class-6 gate.** `classify_migration_diff`'s class-6 test is
#: the property Ruling 104 §2 states -- does this file's content equal a second,
#: independent `migrate()` run's output at the same path -- checked without regard to
#: whether the path is in this set at all (Ruling 104: "a class-6 classifier keyed on a
#: filename or a path ... rather than on the property" is itself a violation). This set is
#: read only by `_stamp_regenerated_readmes` below, to know which paths need the Reference
#: header a `carry`/`fresh` write does not add itself.
_MIGRATION_DIFF_FAMILY_READMES: Final[frozenset[str]] = frozenset(
    set(_README_FAMILY_MOVES)
    | set(_README_FAMILY_MOVES.values())
    | set(_README_IN_PLACE)
    | {f"docs/{_DOCUMENT_FAMILY_DIR[p]}/README.md" for p in _README_NEW_FAMILY_PREFIXES}
)

#: A markdown inline link's target. Deliberately stops at whitespace so a `](path "title")`
#: form yields the path alone, matching how the auditor's scanner reads the same construct
#: (`target = m.group(1).split(" ", 1)[0]`) -- one reading of the syntax, so a link this
#: rewrites and a link that check counts cannot be two different populations.
#: A markdown inline link, with the text ahead of it kept so the two can be compared. The
#: corpus writes `[`../adr/`](../adr/)` and `[docs/notes/README.md](../../docs/notes/
#: README.md)` -- the first repeats its own target as its label, and repointing the target
#: while leaving the label is how a link comes to display one path and go to another.
_MD_LINK_TARGET_RE: Final = re.compile(
    r"\[(?P<text>[^\[\]]*)\]\((?P<target>[^)\s]+)\)"
)


def _has_front_matter(text: str) -> bool:
    """A leading `---`-fenced block. Used to check Ruling 68 class 1 as a **pair**.

    Class 1 is *"a front-matter block added, **together with** the legacy prose or bullet
    header it replaces being removed"*. Checking only that the body survives stripping
    tests one direction: a file whose legacy header was removed and which was then never
    stamped strips to the identical body (the strip is a no-op when there is no block) and
    passes. Requiring the block to exist is the other half of the conjunction.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return False
    return "---" in lines[1:]


def _repoint_relative_links(
    text: str, old_rel: str, new_rel: str, moves: Mapping[str, str]
) -> str:
    """`text`'s relative markdown link targets, each resolved against `old_rel`'s directory,
    looked up in `moves` (repo-relative old -> repo-relative new) and re-expressed relative
    to `new_rel`'s directory.

    Two independent things are fixed by one pass, and both are needed even when only one of
    them applies to a given link: the **target** may have moved, and the **citing file** may
    have moved, which changes what a relative path from it means. A link to a file neither
    this run nor its citer moved comes back byte-identical, so this is safe to run over a
    whole document rather than over a hand-picked list of lines.

    Absolute paths, URLs, bare anchors and `mailto:` are left alone. So is any target that
    resolves above the repository root: it names something outside the tree this migration
    is allowed to reason about.
    """
    old_dir = posixpath.dirname(old_rel)
    new_dir = posixpath.dirname(new_rel) or "."

    def _one(match: re.Match[str]) -> str:
        text_label, target = match.group("text"), match.group("target")
        if target.startswith(("http://", "https://", "#", "mailto:", "/")):
            return match.group(0)
        base, sep, anchor = target.partition("#")
        if not base:
            return match.group(0)
        trailing = "/" if base.endswith("/") else ""
        resolved = posixpath.normpath(posixpath.join(old_dir, base))
        if resolved.startswith(".."):
            return match.group(0)
        moved = moves.get(resolved, resolved)
        rebased = posixpath.relpath(moved, new_dir) + trailing
        # A label that repeated the old target repeats the new one; a label that said
        # anything else is the author's prose and is not touched. Both bare and
        # backticked, because the corpus writes it both ways.
        for wrapper in ("{}", "`{}`"):
            if text_label == wrapper.format(target):
                text_label = wrapper.format(rebased + sep + anchor)
                break
        return f"[{text_label}]({rebased}{sep}{anchor})"

    return _MD_LINK_TARGET_RE.sub(_one, text)


def _split_front_matter(text: str) -> tuple[str, str]:
    """`(header, body)` -- the leading `---`-delimited block including its closing fence and
    the newline after it, and everything after. `("", text)` when there is no such block.

    `_strip_front_matter` above answers the same question and throws the header away; this
    keeps it, because a second `migrate` run over its own output finds a README already
    carrying the header the first run stamped, and that header must not become part of the
    body and be stamped over.

    Split on the line, never by subtracting `_strip_front_matter`'s length from the whole:
    that function joins with `"\n"` and so drops a trailing newline the input had, which
    puts the boundary one character late and hands back a header carrying the body's first
    blank line **and** a body that still starts with it. The duplicate accumulates one blank
    line per run -- caught by `test_migrate_is_idempotent_on_its_own_output`, which is
    exactly the shape of defect a length-arithmetic split produces: correct on the first
    run, wrong only on the second.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\n") != "---":
        return "", text
    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\n") == "---":
            return "".join(lines[: index + 1]), "".join(lines[index + 1 :])
    return "", text  # an unterminated block -- `_strip_front_matter`'s own reading


def _readme_title(header: str, fallback: str) -> str:
    match = re.search(r"^title:\s*(.+)$", header, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def _render_adrs_readme_table(drafts: Sequence[_Draft]) -> str:
    """§5.2's "README generated" for the ADR index: one row per `ADR-` draft this run
    assigned, written from the draft's own id, filename, title and mapped status.

    Generated rather than repointed, unlike the other three tables, because the old rows'
    link **text** is a bare padded legacy number (`[0001](...)`) and not an `ADR-0001`
    token, so `_rewrite_citations` never touched it: repointing alone would leave a table
    whose targets are new and whose visible ids are the retired four-digit ones. §1's
    citation rule is explicit that link text is in scope -- "**No exception**: prose,
    headings, commit messages, PR titles, branch names, code comments, docstrings, test
    markers, link text".
    """
    rows = [
        "| ADR | Title | Status |",
        "|---|---|---|",
    ]
    for d in sorted(
        (d for d in drafts if d.materialize == "document" and d.prefix == "ADR"),
        key=lambda d: d.number,
    ):
        assert d.new_path is not None  # written by `_write_document_drafts` before this
        rows.append(
            f"| [{_docid.canonical(d.prefix, d.number)}]({d.new_path.name}) "
            f"| {d.title} | {d.status} |"
        )
    return "\n".join(rows)


_ADRS_README_BODY: Final = """# Architecture Decision Records

One decision per file, named `ADR-{pad}-<slug>.md` — the padded id leads the filename, and the
id itself is permanent: never renumbered, never reused
([`../process/document-ids.md`](../process/document-ids.md)).

**Status values** are the front matter's `status:` field: `draft` → `active` →
(`superseded` | `retired`). An `active` ADR is immutable; to change a decision, write a new
ADR that supersedes it and edit only the old one's `status:` and `superseded_by:`.

**Write an ADR when** a choice constrains more than one module, is expensive to reverse, or
has already been made and needs recording. Otherwise use
[`../open-questions.md`](../open-questions.md).

**This table is generated.** [`../INDEX.md`](../INDEX.md) is the complete index across every
family and is the one that cannot go stale; this table is a convenience view of one family,
rewritten by `scripts/doc-id.py` rather than maintained by hand.

{table}
"""


_RFCS_README_INDEX_POINTER: Final = """## Index

**There is no index table here.** [`../INDEX.md`](../INDEX.md) is generated from the
documents themselves — one row per id, every family — so it cannot disagree with the
directory the way a hand-maintained list does. `ls docs/rfcs/` is the other reading, and
the padded id leading each filename is what makes it sort.
"""


_PLANS_README_POINTER: Final = """## Naming, and the kinds of plan

The filename form, the `kind:` a plan carries, and the status vocabulary are all
[`../process/document-ids.md`](../process/document-ids.md)'s — stated once, there, rather
than restated here — a restated rule is how one of the two statements goes stale. A ledger
is its own family in [`../ledgers/`](../ledgers/) and a ruling its own in
[`../rulings/`](../rulings/); neither is a suffix on a plan's name any more.

**[`../INDEX.md`](../INDEX.md) is the index.** There is deliberately no hand-maintained list
of contents in this file.
"""


#: `## Index` through to the next `##` heading — the notes README's hand-maintained table
#: of all 19 notes, which is the whole of that file's dangling-link population and which
#: §5.2's `notes` row drops: "README rewritten, index table dropped for `INDEX.md`".
#: Anchored on the heading text rather than on a line range, and level-independent
#: (`#{1,6}`) for the reason Ruling 93 gives: a heading demoted or promoted by an unrelated
#: edit must not silently take a section out of a matcher's reach.
_RFCS_INDEX_SECTION_RE: Final = re.compile(
    r"^#{1,6}\s+Index\s*$.*?(?=^#{1,6}\s)", re.MULTILINE | re.DOTALL
)

#: The notes README's check 7, which asserts the index table this migration removes. Left
#: as a numbered item rather than deleted so the seven-check list keeps its numbering --
#: renumbering a list every other document cites by number is the same defect §5 forbids for
#: requirement ids, one register down.
_RFCS_CHECK_SEVEN_RE: Final = re.compile(
    r"^7\. ⚙ \*\*The index above matches the files\.\*\*.*?(?=\n\n)", re.MULTILINE | re.DOTALL
)

_RFCS_CHECK_SEVEN_REPLACEMENT: Final = (
    "7. ⚙ **The generated index matches the files.** `../INDEX.md` is built from the "
    "documents\n   themselves by `scripts/doc-index.py`, so the agreement check 18 used to "
    "make by hand —\n   every note listed, every listed row backed by a file — is now a "
    "property of how the\n   index is produced. What stays yours is the same half check 18 "
    "never covered: whether a\n   row's **status** is true of the repository."
)

#: `## The four kinds of file` through to (not including) `## Writing one so it passes the
#: audit` — the four-kinds table and the `## Naming` section that sits between them, which
#: are exactly the two things §5.2's `plans` row replaces with a pointer. The same row's
#: other half — "the nine writing conventions kept verbatim" — is everything after the stop
#: anchor, which this pattern does not reach.
_PLANS_NAMING_SECTION_RE: Final = re.compile(
    r"^#{1,6}\s+The four kinds of file\s*$.*?(?=^#{1,6}\s+Writing one so it passes the audit\s*$)",
    re.MULTILINE | re.DOTALL,
)


def _rewrite_rfcs_readme_body(body: str) -> str:
    """§5.2's `notes` row: "README rewritten, index table dropped for `INDEX.md`".

    The prose is kept and the two things the migration falsifies are replaced -- the index
    table, and the check that asserts it. Kept rather than re-authored because the standard
    the file states (what a record must contain, what it must not, the verdict vocabulary,
    the failure it exists to prevent) is about the family, not about the layout, and none of
    it stops being true when the directory is renamed. Every path and link in it is repointed
    mechanically by `_repoint_relative_links` before this runs.
    """
    body = _RFCS_INDEX_SECTION_RE.sub(_RFCS_README_INDEX_POINTER + "\n", body)
    body = _RFCS_CHECK_SEVEN_RE.sub(_RFCS_CHECK_SEVEN_REPLACEMENT, body)
    # The one command in the file that names the old directory and the old numbering
    # scheme. `doc-id.py next` is the standard's own answer (§1.7), and it reads the whole
    # tree rather than one directory, which is the point of a single shared sequence.
    return re.sub(
        r"```bash\n# Next number\..*?\n```",
        "```bash\n# Next number. One sequence, shared by every family.\n"
        "python3 scripts/doc-id.py next\n```",
        body,
        flags=re.DOTALL,
    )


def _rewrite_plans_readme_body(body: str) -> str:
    """§5.2's `plans` row: "README: naming and four-kinds table -> pointer; the nine writing
    conventions kept verbatim".

    The conventions are everything from "Writing one so it passes the audit" onward and this
    function does not touch a byte of them. Their **link targets** are repointed by
    `_repoint_relative_links` before this runs, which the file's own text already declares
    to be the one permitted edit: *"a change that preserves the claim exactly while fixing
    how it is addressed -- the relative links repointed when these files moved out of
    `.planning/`"*. That is the same edit, one move later.
    """
    return _PLANS_NAMING_SECTION_RE.sub(_PLANS_README_POINTER + "\n", body)


_FINDINGS_README_BODY: Final = """# docs/findings — the register, and the evidence behind each row

**The register is a ledger; the evidence is a file.** [`register.md`](register.md) is the
global list of findings carried across work items and phases: one row per finding, with its
status, its decision and its owner. An `FD-` document beside it is the evidence essay for a
row too long to carry inline — the row stays the index, the essay is where its Concerns
prose lives.

Per-phase views are **generated**, never files: `python3 scripts/doc-index.py --phase <p>`.
There is no second copy of the register to disagree with the first one.

The closure records this directory used to sit beside now live in
[`../closures/`](../closures/README.md), and the checklists a close writes against in
[`../process/checklists/`](../process/checklists/). `close-workstream` and `phase-review`
stay the binding procedures; nothing here restates their audit steps.

## Conventions

- **Every row has a verdict.** A finding with no status is not a finding that is fine; it is
  one nobody has read. `scripts/register-lint.py` enforces the grammar.
- **Evidence is write-once.** A record that changes after the fact must say it changed, with
  the correction dated.
- **ISO dates.** All dates are ISO 8601, for example `2026-08-27`.
- **Secrets redaction.** No secrets, credentials, or dataset contents
  (`.claude/skills/secret-hygiene`).
"""


_CLOSURES_README_BODY: Final = """# docs/closures — how each close was audited

One `CR-` record per close, `kind:` naming which layer it closed: `work` for a work item,
`phase` for a phase, `review` for a §14 plan review. Each says what was audited, against
what scope, and what the verdict was — the record of what was believed and decided at that
date. Nothing here changes status afterwards.

This directory is one of the four — [`../process/`](../process/),
[`../findings/`](../findings/README.md), [`../research/`](../research/) and this one — that
the old `docs/audit/` dissolved into. The forward-looking plan is
[`../roadmap.md`](../roadmap.md); these are the archive.

The checklists a close writes against are in
[`../process/checklists/`](../process/checklists/), and the findings a close carries forward
are rows in [`../findings/register.md`](../findings/register.md).

## Conventions

- **A close is named by an existing id** — a `WK-` work item, a phase, a PR number. No new id
  family is minted here; the id comes from `docs/process/document-ids.md` §1.2.
- **Checklist versioning.** A checklist is versioned; a record names the checklist version it
  was written against.
- **Evidence is write-once**, and a correction after the fact is dated and says so.
- **A tag at phase close.** The phase record is tagged at the phase's close.
- **ISO dates**, and no secrets, credentials or dataset contents.
"""


_RULINGS_README_BODY: Final = """# docs/rulings — one decision per file

An `RL-` record is a decision taken while work was in flight: what was ruled, on what
question, with the reasoning that produced it and the date it was made. One ruling per file,
the padded id leading the filename.

**A ruling is not an ADR.** An ADR records an architectural choice that constrains more than
one module and is expensive to reverse ([`../adrs/`](../adrs/README.md)); a ruling settles a
question a slice ran into — scope, a signature, which of two readings of a requirement is the
operative one. A ruling that turns out to constrain the architecture becomes an ADR, and says
so.

**The reasoning travels with the decision.** A ruling recorded without the reason it was taken
is an instruction to reverse it the first time someone re-derives the obvious answer the
ruling rejected. Write the rejected reading down.

[`../INDEX.md`](../INDEX.md) is the index.
"""


_LEDGERS_README_BODY: Final = """# docs/ledgers — what execution actually did

An `LG-` record is the execution ledger for one plan: task by task, what was done, what was
found, and what changed from the plan. Its `work:` names the work item it belongs to and,
where the ledger is slice-scoped, its `slice:` names the slice.

**A ledger is the counterpart to a plan, not a summary of it.** The plan
([`../plans/`](../plans/README.md)) says what was intended; the ledger says what happened,
including the parts that diverged. Neither is edited to agree with the other — that is the
same rule `CLAUDE.md` §0 applies to a spec and its code, and for the same reason.

[`../INDEX.md`](../INDEX.md) is the index.
"""


def _rewrite_findings_readme_body(_body: str) -> str:
    """§5.2's `audit/README.md` row: "deleted; content to `findings/` and `closures/`
    READMEs".

    The old body is not carried: it is a directory map of a directory that no longer exists,
    written around a two-role split (`the archive` / `the record layer`) that §1.4 replaces
    with four separate family directories. Its content is redistributed instead -- the
    register, the finding essays and the conventions here; the closure records, the plan
    reviews and the close conventions in `_CLOSURES_README_BODY`; the checklists and
    `retrofit-impossible.md` are moved bodily to `docs/process/` by `_write_reference_moves`
    and are pointed at from both.
    """
    return _FINDINGS_README_BODY


def _regenerate_family_readmes(
    root: Path, drafts: Sequence[_Draft], moves: Mapping[str, str]
) -> tuple[list[str], list[str], dict[str, str]]:
    """NT-0019 §5.2's README work. Returns `(files_written, files_deleted)`, repo-relative
    posix paths, the shape every other writer in `migrate` returns.

    **Bodies only.** The header for every path this writes is `_stamp_regenerated_readmes`'
    job, after the citation sweep and the §4 step 5 stamp pass, and the split is what keeps
    two separate invariants:

    * A relocated README must be **deleted before `_rewrite_citations` runs**, or the sweep
      writes to a path this same run then removes and the run reports one path as both
      written and deleted (`test_no_path_is_both_stamped_and_deleted_by_the_same_run`). That
      is why this runs where it does -- early, in the write phase, not after the stamp pass.
    * A `was:` value is an **old** path and a header is written post-sweep for exactly that
      reason: written here, `_rewrite_citations` would rewrite `was: docs/adr/README.md`
      into the new path and destroy the one field that records where the file came from.

    Idempotent by the same construction every `_discover_*` uses: each step is gated on its
    source file still being at its old path, which a completed run has already moved.
    """
    written: list[str] = []
    deleted: list[str] = []
    #: new path -> the path its content came from, for `_stamp_regenerated_readmes`' `was:`
    #: and `created:`. A README written in place maps to itself.
    origins: dict[str, str] = {}
    all_moves = {**moves, **_README_LEGACY_DIR_MOVES}

    def carry(old_rel: str, new_rel: str, transform: Callable[[str], str]) -> None:
        """Rewrite one README's body and land it at `new_rel`, deleting `old_rel` when the
        two differ. `transform` runs on the body **after** the link repoint, so a section a
        row replaces wholesale is not first repointed and then thrown away."""
        old_path = root / old_rel
        if not old_path.is_file():
            return
        # `_split_front_matter` rather than a bare read: an in-place README is a §4 step 5
        # stamp target and a *second* `migrate` run finds it already carrying its header,
        # which must not become part of the body and be stamped over.
        header, body = _split_front_matter(old_path.read_text(encoding="utf-8"))
        body = transform(_repoint_relative_links(body, old_rel, new_rel, all_moves))
        origins[new_rel] = old_rel
        new_path = root / new_rel
        new_path.parent.mkdir(parents=True, exist_ok=True)
        new_path.write_text(header + body, encoding="utf-8")
        written.append(new_rel)
        if new_rel != old_rel:
            old_path.unlink()
            deleted.append(old_rel)

    def fresh(rel: str, body: str) -> None:
        """One of §5.2's `new` family READMEs -- a file with no predecessor to carry over.
        Its header is `_stamp_regenerated_readmes`' too: `_stamp_reference_targets`
        discovered its population from the tracked, pre-migration tree and structurally
        cannot see a path this run creates."""
        path = root / rel
        if path.is_file():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        written.append(rel)

    # --- `adr/` + README -> `adrs/`, README generated.
    carry(
        "docs/adr/README.md",
        _README_FAMILY_MOVES["docs/adr/README.md"],
        lambda _body: _ADRS_README_BODY.format(
            pad="n" * _docid.PAD_WIDTH, table=_render_adrs_readme_table(drafts),
        ),
    )

    # --- `notes/` + README -> `rfcs/`, README rewritten, index table dropped for INDEX.md.
    carry(
        "docs/notes/README.md",
        _README_FAMILY_MOVES["docs/notes/README.md"],
        _rewrite_rfcs_readme_body,
    )

    # --- `workflows/README.md`: table generated (the row targets; the `wf-0N` link text is
    # already an id token and `_rewrite_citations` rewrote it in the same run).
    in_place_workflows, in_place_plans = _README_IN_PLACE
    carry(in_place_workflows, in_place_workflows, lambda body: body)

    # --- `plans/README.md`: naming and four-kinds table -> pointer, nine conventions kept.
    carry(in_place_plans, in_place_plans, _rewrite_plans_readme_body)

    # --- `audit/README.md` deleted, content to the `findings/` and `closures/` READMEs.
    carry(
        "docs/audit/README.md",
        _README_FAMILY_MOVES["docs/audit/README.md"],
        _rewrite_findings_readme_body,
    )
    for prefix, body in (
        ("CR", _CLOSURES_README_BODY),
        ("RL", _RULINGS_README_BODY),
        ("LG", _LEDGERS_README_BODY),
    ):
        fresh(f"docs/{_DOCUMENT_FAMILY_DIR[prefix]}/README.md", body)

    # §1.4: the three legacy directories held exactly one file each -- their own README --
    # which is what stopped `migrate`'s earlier prune from dissolving them. `docs/adr/` and
    # `docs/notes/` are not in §1.4's tree at all, and "`docs/audit/` dissolves into
    # `findings/`, `closures/`, `research/` and `process/`" is the same paragraph's last
    # sentence.
    for legacy_dir in _README_LEGACY_DIR_MOVES:
        _remove_if_empty(root / legacy_dir)
    _remove_if_empty(root / "docs" / "audit")
    return written, deleted, origins


def _stamp_regenerated_readmes(root: Path, origins: Mapping[str, str]) -> list[str]:
    """The Reference header for every README `_regenerate_family_readmes` wrote that does
    not already carry one, prepended after the citation sweep and after
    `_stamp_reference_targets`.

    Two populations reach here and neither is reachable by the §4 step 5 stamp pass:

    * a **relocated** README, which that pass was told is `routed` so that it does not
      stamp a path this run deletes; and
    * a **new** family README, which did not exist when that pass read `git ls-files`.

    An **in-place** README is neither -- `docs/workflows/README.md` and
    `docs/plans/README.md` are still at the path the stamp pass claimed, so they arrive here
    already carrying their header and are left alone. `created:` is read from the origin
    file's own first commit where there is one, the same source `_stamp_reference_targets`
    reads, so a carried README's date does not silently become the migration's date.
    """
    written: list[str] = []
    for rel in sorted(_MIGRATION_DIFF_FAMILY_READMES):
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if _front_matter_state(text) != "none":
            continue
        origin_rel = origins.get(rel)
        heading = _REFERENCE_H1_RE.search(text)
        header = _stamp_header(
            "REFERENCE", None, kind=None,
            title=heading.group(1) if heading else posixpath.basename(posixpath.dirname(rel)),
            status="active",
            created=(
                _module_first_commit_date(root / origin_rel, root)
                if origin_rel is not None and origin_rel != rel
                else date.today()
            ),
            owner="lead",
            was=origin_rel if origin_rel is not None and origin_rel != rel else None,
        )
        path.write_text(header + "\n" + text, encoding="utf-8")
        written.append(rel)
    return written


_SPLIT_INDEX_PREAMBLE: Final = """**This file is generated by `scripts/doc-id.py migrate`.
Do not hand-edit it.**

Each section below names one pre-migration file the NT-0019 migration split into more than
one document, and lists every document it became beside the `was:` provenance each of those
documents carries. A citation of the old path that did **not** say which of them it meant
resolves here rather than to any one of them (Ruling 101 clause 1): this is the
[`../REDIRECTS.csv`](../REDIRECTS.csv) row made navigable, not a target chosen on the
reader's behalf. Ruling 100 §3.3 forbids choosing one, and Ruling 89 forbids the path-only
rewrite that choosing one would be.

A citation that *did* determine its target -- by an adjacent id, by an `#anchor` matching
exactly one target's heading, or by a line number falling inside exactly one target's span
in the source file -- was rewritten to that target and never reaches this file.
"""


@dataclass(frozen=True)
class _SplitIndexSection:
    """One split source's section in its family's `INDEX.md`."""

    old_rel: str
    family_dir: str
    rows: tuple[tuple[str, str, str], ...]  # (canonical id, destination rel, title)


def _sweep_title(text: str, token_map: Mapping[str, str]) -> str:
    """`text` with every whole `token_map` token substituted, longest first.

    Task 4 item 1 (the deputy's sweep-order ruling, W37-6 channel `:302-306`): a generated
    artifact's title column is built from a `_Draft.title` captured **before**
    `_rewrite_citations` runs, and nothing sweeps the artifact afterward, so a legacy token
    with a real `token_map` entry reached the page unswept — the `was:`-before-sweep bug's
    mirror image. This is the whole-file sweep's own token-substitution rule
    (`_whole_token_re`, Ruling 102 §2 row (g)), applied to one string in isolation rather
    than to a file, so it carries no risk of touching a `was:` provenance cell the way a
    naive re-sweep of the whole generated file would.
    """
    for tok in sorted(token_map, key=len, reverse=True):
        if tok not in text:
            continue
        text = _whole_token_re(tok).sub(lambda m, v=token_map[tok]: v, text)  # type: ignore[misc]
    return text


def _split_index_sections(
    split_sources: Sequence[_SplitSource],
    token_map: Mapping[str, str] = types.MappingProxyType({}),
) -> list[_SplitIndexSection]:
    """One section per split **source**, deduplicated across the up-to-three
    `_SplitSource`s a single source produces (one per citing token form, all carrying the
    same target list).

    Each row's `title` is swept through `token_map` (Task 4 item 1) — never its `was:`,
    which is the caller's own provenance column, built separately from `section.old_rel`.
    """
    by_source: dict[str, _SplitIndexSection] = {}
    for src in split_sources:
        if src.old_rel in by_source:
            continue
        by_source[src.old_rel] = _SplitIndexSection(
            old_rel=src.old_rel,
            family_dir=src.index_rel.split("/")[1],
            rows=tuple(
                sorted(
                    (t.canonical_id, t.new_rel, _sweep_title(t.title, token_map))
                    for t in src.targets
                )
            ),
        )
    return sorted(by_source.values(), key=lambda s: (s.family_dir, s.old_rel))


def _md_cell(text: str) -> str:
    """A table cell's text with the one character that would end it escaped. A `|` inside
    a document title otherwise silently adds a column, which `audit-docs.py`'s row-width
    check reads as a malformed table rather than as an escaped title.
    """
    return text.replace("|", r"\|")


def _write_split_source_indexes(
    root: Path,
    split_sources: Sequence[_SplitSource],
    token_map: Mapping[str, str] = types.MappingProxyType({}),
) -> list[str]:
    """Ruling 101 clause 1's family index: `docs/<family>/INDEX.md`, one section per split
    source, each listing every target with its `was:` provenance.

    Written **after** `_rewrite_citations`, for the same reason `_stamp_reference_targets`
    and `_stamp_regenerated_readmes` are: every row quotes a `was:` value, which is by
    definition a pre-migration path, and a sweep that saw it would rewrite the very
    provenance the section exists to carry.

    `token_map` is **not** the file-level sweep replayed here — it is Task 4 item 1's
    narrower fix: `_split_index_sections` runs every row's `title` (never its `was:`
    column) through `_sweep_title` before this function ever renders a line, so the title
    a reader sees matches the id the row's own link points at.

    Only families that actually receive a split target get a file. A family index with no
    sections would carry nothing, and an index section is required to list two or more
    documents -- an empty one is exactly the silent failure `_split_index_violations`
    exists to make loud, so none is written by construction either.
    """
    written: list[str] = []
    by_family: dict[str, list[_SplitIndexSection]] = {}
    for section in _split_index_sections(split_sources, token_map):
        by_family.setdefault(section.family_dir, []).append(section)
    # Task 4 item 1's own sweep-order defect, found a second time in the same function:
    # the preamble is a source-level string constant naming `Ruling 89`/`100`/`101` by
    # their legacy form, and it too is rendered after `_rewrite_citations` already ran.
    # Swept once here, per family loop iteration below (cheap -- a handful of families,
    # never per-row) rather than per row, since it is one shared block, not per-target
    # data.
    swept_preamble = _sweep_title(_SPLIT_INDEX_PREAMBLE.rstrip("\n"), token_map)
    for family_dir, sections in sorted(by_family.items()):
        lines = [
            f"# docs/{family_dir} — split-source index",
            "",
            swept_preamble,
            "",
        ]
        for section in sections:
            lines += [
                f"## {_split_index_heading(section.old_rel)}",
                "",
                f"`{section.old_rel}` became {len(section.rows)} documents.",
                "",
                "| Document | Title | `was:` |",
                "|---|---|---|",
            ]
            for canon, new_rel, title in section.rows:
                # `_split_index_family`'s own docstring: a split source's targets are not
                # guaranteed to share one family directory ("three sources split *across*
                # families"), so a target can land in a directory other than this index's
                # own (`docs/{family_dir}`). A bare basename resolves only when it does not
                # — `os.path.relpath` is the general case and degrades to the same bare
                # basename whenever it does, so the common case is unchanged.
                link = posixpath.relpath(new_rel, start=f"docs/{family_dir}")
                lines.append(
                    f"| [`{canon}`]({link}) | {_md_cell(title)} | "
                    f"`{section.old_rel}` |"
                )
            lines.append("")
        body = "\n".join(lines)
        header = _stamp_header(
            "REFERENCE", None, kind=None,
            title=f"docs/{family_dir} — split-source index",
            status="active", created=date.today(), owner="lead", was=None,
        )
        rel = _split_index_rel(family_dir)
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(header + "\n" + body, encoding="utf-8")
        written.append(rel)
    return written


def _split_index_violations(
    root: Path, index_resolved: Sequence[_UnresolvedCitation]
) -> list[str]:
    """Ruling 101 clause 3: **every `INDEX.md#<anchor>` a citation resolves to exists, and
    its section lists two or more documents.**

    *"A link to an empty index section is the new silent failure; make it loud first."* The
    failure this catches resolves at the file level -- `docs/rulings/INDEX.md` is a real
    file -- so the auditor's dangling-link scanner, which checks the path and not the
    fragment, passes on it. That is the same shape as the defect Ruling 100 was written
    about: a citation that resolves and tells the reader nothing.

    Each violation names **the citing file and line** and **the anchor**, because the
    disposition is per citation. Checked per distinct target, reported per citation.
    """
    violations: list[str] = []
    cache: dict[str, str | None] = {}
    for cite in sorted(
        index_resolved, key=lambda c: (c.citing_file, c.line, c.index_anchor)
    ):
        key = f"{cite.index_rel}#{cite.index_anchor}"
        if key not in cache:
            cache[key] = _split_index_section_fault(
                root, cite.index_rel, cite.index_anchor
            )
        fault = cache[key]
        if fault is not None:
            violations.append(f"{cite.citing_file}:{cite.line} resolves to {key}: {fault}")
    return violations


_SPLIT_INDEX_ROW_RE: Final = re.compile(r"^\|\s*\[`[^`]+`\]\([^)]+\)\s*\|")


def _split_index_section_fault(root: Path, index_rel: str, anchor: str) -> str | None:
    """`None` when `index_rel` exists and its `anchor` section lists two or more
    documents; otherwise the reason, phrased as what is wrong rather than as a code.
    """
    path = root / index_rel
    if not path.is_file():
        return "the index file does not exist"
    text = path.read_text(encoding="utf-8")
    headings = list(_ANCHOR_HEADING_RE.finditer(text))
    for i, heading in enumerate(headings):
        if _anchor_slug(heading.group(1)) != anchor:
            continue
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        rows = [
            line for line in text[heading.end() : end].splitlines()
            if _SPLIT_INDEX_ROW_RE.match(line)
        ]
        if len(rows) < 2:
            return (
                f"its section lists {len(rows)} document(s); a split source has two or "
                "more, so this section is empty of the choice the citation needs"
            )
        return None
    return "the index file has no section with that anchor"


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
        {
            "README.md": "the directory's own README, not a governed note",
            "INDEX.md": (
                "the family's generated split-source index (Ruling 101 clause 1), "
                "not a governed record"
            ),
        },
    )
    drafts += notes_drafts
    adr_drafts = _discover_adrs(root)
    _check_flat_document_directory_not_silently_unrecognised(
        root, "docs/adr", _ADR_TITLE_RE, "ADRs",
        {
            "README.md": "the directory's own README, not a governed ADR",
            "INDEX.md": (
                "the family's generated split-source index (Ruling 101 clause 1), "
                "not a governed record"
            ),
        },
    )
    drafts += adr_drafts
    multi_ruling_drafts = _discover_multi_ruling_files(root)
    # Ruling 86's A-series (F81): letter-suffixed ruling headings nested inside a plan that
    # survives the extraction, so this runs alongside the whole-file splitter above rather
    # than inside it -- see `_discover_lettered_rulings`' own docstring for why widening
    # `_RULING_HEADING_RE` would have destroyed the residual `PL-` Ruling 86 §3 item 5
    # requires. The census below reconciles both matchers' output against one census.
    multi_ruling_drafts += _discover_lettered_rulings(root)
    _check_multi_ruling_files_not_silently_unrecognised(root)
    drafts += multi_ruling_drafts
    closure_drafts = _discover_closure_records(root)
    _check_legacy_file_not_silently_unrecognised(
        root / "docs" / "audit" / "closure-records.md", closure_drafts, "closure records"
    )
    _check_closure_records_not_silently_unrecognised(root)
    drafts += closure_drafts
    # F84: the same family from a second location `_discover_closure_records` never
    # visits -- one record per whole file under `docs/audit/work/` and
    # `docs/audit/phases/`, rather than one file split into many records. The census is
    # passed the drafts, not the root, so it reconciles against what discovery produced.
    audit_closure_drafts = _discover_audit_closure_readmes(root)
    _check_audit_closure_readmes_not_silently_unrecognised(root, audit_closure_drafts)
    drafts += audit_closure_drafts
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
        root, "docs/audit/plan-reviews.md", _REVIEW_HEADING_RE, 3, "plan reviews",
        extra_record_starts=_proposal_container_starts,
    )
    drafts += review_drafts
    plain_plan_drafts = _discover_plain_plans(root)
    _check_plain_plans_not_silently_unrecognised(root)
    drafts += plain_plan_drafts
    requirement_drafts = _discover_requirements(root)
    _check_requirements_not_silently_unrecognised(root)
    roadmap_drafts, phase_titles, roadmap_occurrences = _discover_roadmap(root)
    # Merges the phase-1b register into the main one and deletes the phase file -- must
    # run before `_discover_findings`/`_discover_register` below, both of which read
    # `docs/audit/register.md` from disk: the 11 merged rows need to already be ordinary
    # register content by the time either function sees the file, not a separate source
    # this discovery layer would otherwise need to know about.
    phase1b_register_deleted = _merge_phase1b_register(root)
    finding_drafts = _discover_findings(root)
    _check_flat_document_directory_not_silently_unrecognised(
        root, "docs/audit/findings", None, "finding essays",
        {
            "README.md": "the family's own index, not a governed finding essay",
            "INDEX.md": (
                "the family's generated split-source index (Ruling 101 clause 1), "
                "not a governed record"
            ),
        },
        records={Path(d.was).name for d in finding_drafts if d.was is not None},
    )
    drafts += finding_drafts
    # The census below must run against `_discover_register`'s *unfiltered* output: it is
    # asking "did this file's shape get recognised at all", and every row this migration
    # excludes (because its finding has an essay, and therefore already has a `document`
    # draft above) is still a row the parser recognised, not a row the shape check missed.
    # Filtering before this call would make a corpus where *every* register row has an
    # essay look identical to `register.md` carrying no recognisable rows at all -- the
    # exact "found nothing" ambiguity `_check_legacy_file_not_silently_unrecognised`'s own
    # docstring exists to resolve, reintroduced by this slice if the check ran on the
    # already-excluded list.
    register_drafts_unfiltered = _discover_register(root)
    _check_legacy_file_not_silently_unrecognised(
        root / "docs" / "audit" / "register.md", register_drafts_unfiltered,
        "register finding rows",
    )
    # Excludes every token `finding_drafts` already claims: a finding with an essay gets
    # exactly one number, from its `document` draft above, never a second one from this
    # function's `register_row` draft (see `_discover_register`'s own `exclude` docstring).
    finding_tokens = {d.old_token for d in finding_drafts if d.old_token is not None}
    register_drafts = [
        d for d in register_drafts_unfiltered if d.old_token not in finding_tokens
    ]
    drafts += requirement_drafts + roadmap_drafts + register_drafts
    workflow_drafts = _discover_workflows(root)
    _check_flat_document_directory_not_silently_unrecognised(
        root, "docs/workflows", None, "workflows",
        {
            "README.md": "the family's own index, not a governed workflow document",
            "INDEX.md": (
                "the family's generated split-source index (Ruling 101 clause 1), "
                "not a governed record"
            ),
        },
        records={Path(d.was).name for d in workflow_drafts if d.was is not None},
    )
    drafts += workflow_drafts
    research_essay_drafts = _discover_research_essays(root)
    drafts += research_essay_drafts
    named_phase_record_drafts = _discover_named_phase_records(root)
    drafts += named_phase_record_drafts
    reference_moves = _discover_reference_moves(root)
    # Hoisted here to run alongside every other discovery, before any write below (task
    # #34). The hoist was won when this call could still abort the run: a malformed
    # vendored manifest's `HeaderError` had to stop `migrate` cleanly rather than after
    # Phase C's document/roadmap/register writes had landed on disk. **It no longer
    # aborts** -- `F88` limb 1's fix classifies with `_front_matter_state`, which cannot
    # raise -- so the hoist now buys the weaker but still real property that discovery is
    # complete before any write, the same position every other `_discover_*` occupies.
    # `_is_vendored_skill_manifest`'s detection rule was LICENSE-based until Ruling 69's
    # membership-test fix landed here (reassigned to this slice by Ruling 76); this hoist
    # was never about which files the check reaches.
    vendored_scan = _discover_vendored_skill_manifests(root)
    # NT-0019 §4 step 5's Reference stamp set (W37-5c item 2). Discovered here, alongside
    # every other discovery and before any write, for the same reason the vendored
    # manifests were hoisted (task #34): the census must refuse on the *pre-migration*
    # tree, not after `_write_document_drafts` has already landed files on disk. `routed`
    # is F84's 17, so a README the migration turns into a `CR-` leaves the README
    # population by construction rather than by a maintained exception list.
    reference_targets, reference_censuses = _discover_reference_stamp_targets(
        root,
        # F84's 17, plus §5.2's three relocated family READMEs. Both leave the stamp
        # population for the same reason and by the same mechanism: §5.2 routes the file
        # somewhere, and the writer that moves it owns its header. Stamping one here would
        # write a header onto a path this same run then deletes, which
        # `test_no_path_is_both_stamped_and_deleted_by_the_same_run` forbids.
        routed=(
            {d.was for d in audit_closure_drafts if d.was is not None}
            | set(_README_FAMILY_MOVES)
        ),
    )
    _check_reference_stamp_set_not_silently_unrecognised(reference_censuses)
    # Last of the pre-write checks and the only one that reads `drafts` rather than the
    # tree: every document draft must name a prefix the writer can place AND render. The
    # lookups it stands in for live inside the write loop, so without this a missing family
    # is a `KeyError` part-way through an irreversible migration.
    _check_every_document_draft_is_placeable(drafts)

    # NT-0019 §7(b) / Ruling 102 §2 row 4: "allocate ids after exemptions are applied."
    # The ids `_assign_numbers` hands out come from one global sequence, and
    # `docs/INDEX.md` (`_regenerate_index_for_migrate` below) lists a number only once
    # something in the tree actually carries it — a document's own stamped header, or a
    # citation this run's own rewrite (below) actually rewrote. Two draft classes are known,
    # before any number is assigned, never to reach either: a `register_row` (a bare `F<n>`
    # register finding with no essay — the maintainer's 2026-09-03 ruling on `FD` holds its
    # citation form out of the rewrite deliberately, "a resolver alias to W37-11", so
    # nothing ever carries its new id), and a draft whose legacy `old_token` is shared with
    # another draft (the multi-claim guard below holds that token out of `token_map` for the
    # identical reason — no citation names which one it meant — and the same hole blocks
    # the drafts' own definition-row rewrite, not only a citation elsewhere). Numbering both
    # classes *before* everything else, interleaved by sort order the way a single
    # `_assign_numbers(drafts, start)` call does, scatters never-discoverable numbers through
    # the middle of the range `docs/INDEX.md` can see — exactly `doc-id.py check`'s
    # NT-0019 §7(b) noncontiguous failures. Numbering them *last* instead keeps every
    # discoverable number a contiguous block, and puts every number that will never be
    # discoverable past the real maximum — which is not a gap `find_noncontiguous_gaps` can
    # see, since nothing later ever gets compared against a number nothing in the tree cites.
    _old_token_counts: dict[str, int] = {}
    for d in drafts:
        if d.old_token is not None:
            _old_token_counts[d.old_token] = _old_token_counts.get(d.old_token, 0) + 1

    def _never_discoverable(d: _Draft) -> bool:
        if d.materialize == "register_row":
            return True
        return d.old_token is not None and _old_token_counts[d.old_token] > 1

    _discoverable_drafts = [d for d in drafts if not _never_discoverable(d)]
    _exempt_drafts = [d for d in drafts if _never_discoverable(d)]

    start = compute_next(root)
    _assign_numbers(_discoverable_drafts, start)
    _assign_numbers(_exempt_drafts, start + len(_discoverable_drafts))

    files_written, files_deleted = _write_document_drafts(root, drafts, roadmap_drafts)

    # Reference-family moves (checklists, `retrofit-impossible.md`, `security-posture.md`)
    # and the unstampable-CSV move both physically relocate a file, the same shape
    # `_write_document_drafts` above just finished, so they run alongside it -- before
    # `_rewrite_citations` below, so each new location's body is swept for legacy
    # citations exactly as every document draft's body already is, rather than being
    # written post-sweep and left with whatever tokens it carried at its old path.
    reference_moves_written, reference_moves_deleted = _write_reference_moves(
        root, reference_moves
    )
    files_written = [*files_written, *reference_moves_written]
    files_deleted = [*files_deleted, *reference_moves_deleted]
    unstampable_written, unstampable_deleted = _move_unstampable_research_files(root)
    files_written = [*files_written, *unstampable_written]
    files_deleted = [*files_deleted, *unstampable_deleted]
    # `_merge_phase1b_register` deletes `docs/audit/phases/1b/register.md` by editing
    # `docs/audit/register.md` in place, well before this point -- neither a `_Draft` nor
    # one of the write helpers above, so nothing else records that deletion. Recorded
    # here, once, from the path the merge itself returned -- never re-derived by checking
    # whether the path still exists, which is one call already made and answered.
    if phase1b_register_deleted is not None:
        files_deleted = [*files_deleted, phase1b_register_deleted]

    if roadmap_drafts:
        _restructure_roadmap(root, roadmap_drafts, phase_titles, roadmap_occurrences)
    else:
        _check_roadmap_not_silently_unrecognised(root)

    register_moved_to: str | None = None
    # Gated on the *unfiltered* discovery result, not `register_drafts` (which can be
    # empty even though the file was fully recognised -- every one of its rows may have
    # an essay and so be excluded from the numbering list above). Gating on the filtered
    # list would leave `docs/audit/register.md` in place whenever every row happens to
    # have an essay, which both stops `docs/audit/` dissolving and makes a second run
    # re-discover the same rows as if the first run had never happened -- the identical
    # "found nothing" ambiguity the census fix above exists to resolve, one layer further
    # down, in the write rather than the check.
    if register_drafts_unfiltered:
        old_register = root / "docs" / "audit" / "register.md"
        new_register = root / "docs" / "findings" / "register.md"
        if old_register.is_file():
            new_register.parent.mkdir(parents=True, exist_ok=True)
            new_register.write_text(old_register.read_text(encoding="utf-8"), encoding="utf-8")
            old_register.unlink()
            files_written = [*files_written, "docs/findings/register.md"]
            files_deleted = [*files_deleted, "docs/audit/register.md"]
            register_moved_to = "docs/findings/register.md"

    # F84: `_write_document_drafts` deletes each migrated `docs/audit/work/<work>/
    # README.md`, leaving its directory behind with nothing in it. Pruned bottom-up
    # *before* the three legacy roots below, because an emptied `work/` is exactly what
    # would otherwise keep `docs/audit/` non-empty and stop it dissolving (NT-0019 §1.4:
    # "`docs/audit/` dissolves into `findings/`, `closures/`, `research/` and
    # `process/`"). A directory that still holds a declared exception -- `phases/1b/`
    # holds `register.md` -- survives, correctly: it still has a file in it.
    for rel_dir in _AUDIT_CLOSURE_README_DIRS:
        parent = root / rel_dir
        if parent.is_dir():
            for child in sorted(p for p in parent.iterdir() if p.is_dir()):
                _remove_if_empty(child)
        _remove_if_empty(parent)
    # `_discover_findings` moves every `docs/audit/findings/F<n>.md` essay away and
    # deliberately leaves `README.md` (not a governed finding) in place if present -- but
    # when a corpus's `findings/` holds only essays, as this migration's own fixture and a
    # freshly-seeded real corpus both can, the directory empties out exactly like
    # `docs/audit/work/<work>/` does above and needs the identical bottom-up prune, or it
    # blocks `docs/audit/` from dissolving the same way an emptied `work/<work>/` would.
    _remove_if_empty(root / "docs" / "audit" / "findings")
    for legacy_dir in ("docs/notes", "docs/adr", "docs/audit"):
        _remove_if_empty(root / legacy_dir)

    token_map: dict[str, str] = {}
    # Every file this run relocates, repo-relative old -> repo-relative new. `token_map`
    # answers "what does this path look like when it is written out in prose"; this answers
    # "where did this file go", which is the question `_repoint_relative_links` asks of a
    # link target it has already resolved. Built from the same statements, in the same
    # places, so a move recorded in one and not the other cannot happen quietly.
    path_moves: dict[str, str] = {}
    # Which move claimed each token, so `_add_tokens` can name both claimants when two
    # collide rather than letting the second silently win (`TokenMapCollisionError`).
    token_origins: dict[str, str] = {}
    # The same moves as `path_moves`, but **grouped by source and keeping every
    # destination** rather than letting the last one win. `path_moves` answers a question
    # that is still well-posed for a split source (a relative link out of a moved file is
    # repointed from wherever that file's own body ended up); this answers the question
    # that is not (which of several targets does a *citation* of the old path mean), and
    # its list-valued shape is what makes the ambiguity visible instead of silent.
    path_move_groups: dict[str, list[tuple[_Draft | None, str]]] = {}
    # Legacy **id** token -> every (canonical id, source) claiming it. Collected rather
    # than written straight into `token_map`, because the same silent-overwrite shape the
    # path half of this map had exists here too: measured on the real corpus at `6195ca0`,
    # `OQ-OVR-11` is claimed by two different open questions. An id claimed twice is
    # resolved by nothing on the citing line, so it is held out of the rewrite entirely —
    # the treatment `FD` already gets above, and for the identical reason. Not fatal: this
    # is outside the split-*path* ruling this function's `_SplitSource` fork implements,
    # and a warning that names both claimants is what carries it to whoever rules on it.
    id_claims: dict[str, list[tuple[str, str]]] = {}
    redirect_rows: list[dict[str, str]] = []
    assigned: list[tuple[str, str]] = []
    for d in drafts:
        canon = _docid.canonical(d.prefix, d.number)
        assigned.append((d.old_token or "", canon))
        # `FD` is deliberately excluded from the citation-rewrite map -- the maintainer's
        # ruling (2026-09-03, W37-6): "The essays get ids and paths now; `F<n>` stays a
        # resolver alias to W37-11." Every other family still rewrites its old citation
        # form in place (an `ADR-<n>`, a `Ruling <n>`, an `NT-<nnnn>` all still get swept
        # by `_rewrite_citations` below); only the bare `F<n>` form is held back, because
        # W37-6's own ambiguity sweep (see the finding filed alongside this PR) found the
        # low end of the `F<n>` range reused across independent, undated audit eras
        # (Track A's own F1-F15, the W5 ledger's own F1-F12, phase-1b's F1-F25) for
        # genuinely different findings sharing one bare token -- `F12` alone names three.
        # A blanket `\bF12\b` substitution across the whole tree would silently rewrite
        # all three to whichever one this run's F12 happens to be. `assigned`/
        # `redirect_rows` still record the mapping (REDIRECTS.csv's job: NT-0019 §4 step 1,
        # "`was:` and `REDIRECTS.csv` keep every old id and path" -- a durable record, not
        # a live prose rewrite), so W37-11's resolver has the data; only the prose sweep is
        # held back.
        if d.old_token is not None and d.prefix != "FD":
            id_claims.setdefault(d.old_token, []).append((canon, d.was or canon))
        # Task 4's wf-0n ruling: every alias beyond the primary key (today, only a
        # workflow's heading-derived `WF-0n` form alongside its filename-derived
        # `wf-0n` primary) claims the same canonical id through the same `id_claims`
        # machinery -- so a genuinely contested alias is caught by the identical
        # multi-claimant guard `old_token` itself already gets, not a silent second path.
        for extra in d.extra_old_tokens:
            if d.prefix != "FD":
                id_claims.setdefault(extra, []).append((canon, d.was or canon))
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
        # Task 4's wf-0n ruling, the inverse half: an alias's citation form is only
        # guaranteed correct *inside the draft's own new directory* -- a workflow's own
        # body still carries its own heading's uppercase `WF-0n` form (rewritten in
        # place, same file), while every other citer in the tree wrote the lowercase
        # `wf-0n` filename form the primary `old_id` row above already covers globally.
        # Recorded `citing_dir`-scoped (never as a second global row for the same
        # `new_id`, which `_collision_safe_inverse` would then have to drop as contested)
        # so the workflow's own file inverts on its own heading and nothing else does.
        if d.extra_old_tokens and d.new_path is not None:
            extra_citing_dir = posixpath.dirname(new_path)
            for extra in d.extra_old_tokens:
                redirect_rows.append(
                    {
                        "old_id": extra, "new_id": canon,
                        "old_path": "", "new_path": "", "citing_dir": extra_citing_dir,
                    }
                )
        # A **path** citation (a markdown link's target, or its own repo-relative text)
        # is a different thing from an **id** citation, and the `FD` id-token exclusion
        # above does not apply to it: a path is unique per file, so unlike a bare `F<n>`
        # id it carries none of the cross-era ambiguity that exclusion exists to avoid.
        # Every relocated document -- essays included -- gets its path rewritten in
        # citing prose, `register_row`'s own id-less move included.
        if old_path and new_path and old_path != new_path:
            path_moves[old_path] = new_path
            path_move_groups.setdefault(old_path, []).append((d, new_path))
    # `register_moved_to` can be set with *no* `register_row` draft in `drafts` at all --
    # every row the file had may have had an essay and so been excluded from the numbering
    # list (`_discover_findings`'s `document` drafts claim the number instead). The loop
    # above only ever emits a `docs/audit/register.md` redirect row from a
    # `materialize == "register_row"` draft, so that case would otherwise vanish from
    # REDIRECTS.csv with no row recording it moved -- `migration_diff_violations`' own
    # accounting exists to catch exactly this ("vanished with no REDIRECTS.csv row
    # accounting for it"). Added once, unconditionally, whenever the move happened.
    if register_moved_to is not None:
        redirect_rows.append(
            {
                "old_id": "", "new_id": "",
                "old_path": "docs/audit/register.md", "new_path": register_moved_to,
            }
        )
        redirect_rows.extend(
            _path_citation_redirect_rows("docs/audit/register.md", register_moved_to)
        )
    # Reference moves and the unstampable-CSV move carry no `_Draft` and so no `id:` --
    # neither claims a number (§1.2: Reference has none; the CSV is deliberately exempt) --
    # but NT-0019 §4 step 1's "`REDIRECTS.csv` keeps every old id and path" still applies
    # to the *path* half even where there is no id half, the same reading the register's
    # own unconditional row above already gives its id-less move. Each also gets its path
    # added to `token_map`, the same treatment every `document` draft above already gets
    # (`_path_rewrite_tokens`) -- a citing document does not know or care that these four
    # files carry no id; a stale link to any of them is exactly as broken as one to a
    # numbered document, and the auditor's finding (found on `docs/audit/phases/1b/
    # register.md`, below) is the same mechanism gap for every id-less move, not only
    # that one.
    #
    # Task 4 item 4's own fix, found live against the real corpus rather than assumed from
    # the ruling's own wording: the citation-rewrite bug here is not `_bare_basename_
    # rewrite`'s directory-scoped token (that mechanism is sound and already inverts) --
    # it is that `_path_rewrite_tokens`' own tree-wide forms (`audit/register.md` ->
    # `findings/register.md`, matched as a whole token even *inside* a longer relative
    # path like `../audit/register.md`) had no `old_id`/`new_id` row at all for an
    # id-less move, only the move's own `old_path`/`new_path` row -- and `redirects_
    # inverse` is keyed on `old_id`/`new_id` alone. `_path_citation_redirect_rows` below
    # emits the missing rows from the same generator the sweep itself used, so the two can
    # never drift the way a hand-written second list of forms could.
    for move in reference_moves:
        redirect_rows.append(
            {"old_id": "", "new_id": "", "old_path": move.old_rel, "new_path": move.new_rel}
        )
        redirect_rows.extend(_path_citation_redirect_rows(move.old_rel, move.new_rel))
        path_moves[move.old_rel] = move.new_rel
        path_move_groups.setdefault(move.old_rel, []).append((None, move.new_rel))
    for old_rel, new_rel in _RESEARCH_UNSTAMPABLE_MOVE.items():
        if (root / new_rel).is_file():
            redirect_rows.append(
                {"old_id": "", "new_id": "", "old_path": old_rel, "new_path": new_rel}
            )
            redirect_rows.extend(_path_citation_redirect_rows(old_rel, new_rel))
            path_moves[old_rel] = new_rel
            path_move_groups.setdefault(old_rel, []).append((None, new_rel))
    # `_merge_phase1b_register`'s own deletion: no `_Draft`, no id, and (unlike
    # `register_moved_to` above) the file it deletes is not the one any draft's `was`
    # names -- it edits `docs/audit/register.md` in place and deletes a *different* file.
    # Recorded here for the identical reason the reference moves are: a citation to it
    # (`docs/roadmap.md`'s own link, the auditor's find) is exactly as stale as any other
    # unrewritten move, and REDIRECTS.csv owes it a row regardless of carrying no id.
    if phase1b_register_deleted is not None:
        phase1b_new_path = register_moved_to or "docs/findings/register.md"
        redirect_rows.append(
            {
                "old_id": "", "new_id": "",
                "old_path": phase1b_register_deleted, "new_path": phase1b_new_path,
            }
        )
        redirect_rows.extend(
            _path_citation_redirect_rows(phase1b_register_deleted, phase1b_new_path)
        )
        path_moves[phase1b_register_deleted] = phase1b_new_path
        path_move_groups.setdefault(phase1b_register_deleted, []).append(
            (None, phase1b_new_path)
        )
    if register_moved_to is not None:
        path_moves["docs/audit/register.md"] = register_moved_to

    # NT-0019 §5.2's three relocated READMEs, registered here rather than inside
    # `_regenerate_family_readmes` below because the rewrite and the redirect row are owed
    # *before* the citation sweep runs: a third document citing `docs/audit/README.md` by
    # path is exactly as stale as one citing any other moved file (§4 step 1). The files
    # themselves are moved after `_stamp_reference_targets`, so each carries the header that
    # pass wrote rather than one re-derived here.
    for old_rel, new_rel in _README_FAMILY_MOVES.items():
        if not (root / old_rel).is_file():
            continue
        redirect_rows.append(
            {"old_id": "", "new_id": "", "old_path": old_rel, "new_path": new_rel}
        )
        path_moves[old_rel] = new_rel
        path_move_groups.setdefault(old_rel, []).append((None, new_rel))

    # NT-0019 §5.2's README regeneration -- bodies, here, **before** the citation sweep.
    # A relocated README has to leave its old path before `_rewrite_citations` runs, or the
    # sweep writes to a file this same run then deletes and `migrate` reports one path as
    # both written and deleted. Its body is swept at its new location like every other
    # relocated document's; its header comes after the sweep, below.
    readme_written, readme_deleted, readme_origins = _regenerate_family_readmes(
        root, drafts, path_moves
    )
    files_written = [*files_written, *readme_written]
    files_deleted = [*files_deleted, *readme_deleted]

    for old_token, claims in id_claims.items():
        canons = {canon for canon, _ in claims}
        if len(canons) > 1:
            warnings.append(
                f"legacy id {old_token!r} is claimed by {len(canons)} records "
                f"({', '.join(sorted(canons))}) -- held out of the citation rewrite, "
                "since no citation of it names which one it meant"
            )
            continue
        _add_tokens(token_map, token_origins, {old_token: claims[0][0]}, claims[0][1])

    # The split/single fork, and the only place a path token enters the flat map. A source
    # with one destination is unchanged from #672; a source with several never enters it,
    # because a flat `old_path -> new_path` entry can only hold one of them and the
    # overwrite is silent (`TokenMapCollisionError`'s docstring has the measurement).
    split_sources: list[_SplitSource] = []
    # The bare-basename half of both maps, keyed by the directory the cited file sat in.
    # Kept separate from the tree-wide maps above because a bare basename is only this
    # file's name *inside that directory* -- `_bare_basename_rewrite`'s docstring has the
    # measurement (167 dangling links) and the reason the scope is not optional.
    dir_token_map: dict[str, dict[str, str]] = {}
    dir_token_origins: dict[str, dict[str, str]] = {}
    dir_split_sources: dict[str, list[_SplitSource]] = {}
    for old_rel, moves in path_move_groups.items():
        destinations = {new_rel for _, new_rel in moves}
        if len(destinations) == 1:
            _add_tokens(
                token_map, token_origins,
                _path_rewrite_tokens(old_rel, moves[0][1]), old_rel,
            )
            # Task #30's ruling (W37-6 channel, "the cause table dispositions"): an
            # **id-bearing** move's path citation used to get no row of its own --
            # `_path_citation_redirect_rows` was called only for the four id-less moves
            # below (register.md, reference moves, the CSV, the phase-1b deletion), on
            # the premise that every citer of an id-bearing document writes its bare id,
            # never its path. Measured false: the tombstone stub left at the old notes
            # root under `.claude` (a numbered `000N-*.md` file) deliberately cites the
            # **path** (`` `docs/notes/000N-*.md` ``, with a
            # relative link alongside it) so the pointer stays readable without doc-id
            # knowledge -- "what makes a frozen plan's citation still resolve", the
            # `.claude/` §5.3 ruling's own words for exactly this stub. The forward sweep
            # already rewrites that path wherever it appears (`token_map` carries every
            # `_path_rewrite_tokens` form for every draft, id-bearing or not); only the
            # `old_id`/`new_id` row (g)'s inverse reads was missing for the id-bearing
            # case. Extended here rather than duplicated, so the two calls cannot drift
            # into two different sets of forms for what is the same generator --
            # and gated on this branch, never the per-draft loop above, because that is
            # exactly where the group is known to be a genuine 1:1 move: a source that
            # *splits* (below) shares one `old_rel` across several drafts with several
            # different `new_rel`s, and a naive per-draft emission recorded that same
            # `old_rel` as an `old_id` against each of those different destinations in
            # turn -- precisely the shape #726's `_write_redirects` guard now refuses
            # outright ("one legacy id must resolve to exactly one new id"), found live
            # against a real multi-ruling file
            # (`docs/plans/2026-08-29-w11-3-d6-batch-resumability-ruling.md`, splitting
            # into `RL-00145`/`RL-00146`/…) once that guard existed to catch it.
            redirect_rows.extend(_path_citation_redirect_rows(old_rel, moves[0][1]))
            bare = _bare_basename_rewrite(old_rel, moves[0][1])
            if bare is not None:
                citing_dir, tok, replacement = bare
                _add_tokens(
                    dir_token_map.setdefault(citing_dir, {}),
                    dir_token_origins.setdefault(citing_dir, {}),
                    {tok: replacement}, old_rel,
                )
            continue
        if any(draft is None for draft, _ in moves):
            # A split whose targets are not all document drafts carries no bodies, spans
            # or ids to resolve *with*, so there is nothing to resolve against and every
            # citation of it would be bucket (iv) anyway. Raised rather than silently
            # left, because it is a shape this migration has never produced and the
            # resolver would be quietly inert on it.
            raise TokenMapCollisionError(
                f"{old_rel} splits into {sorted(destinations)} through a move that "
                "carries no draft — no per-citation evidence exists for it"
            )
        with_drafts = [(d, n) for d, n in moves if d is not None]
        split_sources.extend(_build_split_sources(old_rel, with_drafts))
        bare_split = _build_bare_split_source(old_rel, with_drafts)
        if bare_split is not None:
            citing_dir, source = bare_split
            dir_split_sources.setdefault(citing_dir, []).append(source)

    # Task 4 item 3's out-parameter: one `(old, new)` pair per compound citation this run
    # fully expanded (`NFR-RATE-13/14` -> `NFR-775/776` and the like), captured here so
    # each becomes its own `REDIRECTS.csv` row below -- no `old_path`/`new_path`, since a
    # compound is a citation shape, never a moved file -- and `(g)`'s inverse
    # (`redirects_inverse`, built generically off every row's `old_id`/`new_id`) picks it
    # up with no further wiring.
    compound_redirects: list[tuple[str, str]] = []
    # Task 4 item 4's out-parameter: one `(citing_dir, old, new)` triple per
    # directory-scoped (bare-basename) relative-link repoint this run actually performed
    # -- the 27/34 class-4 link hunks, `_bare_basename_rewrite`'s own token form
    # (`../audit/register.md` -> `../findings/register.md`, correct only from directories
    # at the citing directory's own depth). Recorded with its `citing_dir` scope, never as
    # a global pair, so a file elsewhere in the tree whose relative link happens to read
    # the same text is never silently inverted through someone else's row.
    dir_link_redirects: list[tuple[str, str, str]] = []
    # Task #30's out-parameter: one `(old, new)` pair per split-source citation this run
    # resolved to one concrete target (`_SplitSource.resolve`, an id/anchor/line-span
    # determinant, never a directory) -- `docs/audit/register.md` resolving to one
    # phase's own destination is the measured case. No `old_path`/`new_path`: the row
    # records what a *citation* looked like, not that a file moved (that row already
    # exists, per draft, above); `(g)`'s inverse needs no wiring change to consume it,
    # the same "generic on old_id/new_id" property `compound_redirects` already has.
    split_path_redirects: list[tuple[str, str]] = []
    rewritten, index_resolved, unrewritten_citations = _rewrite_citations(
        root, token_map, split_sources, dir_token_map, dir_split_sources,
        derived_redirects=compound_redirects, dir_redirects=dir_link_redirects,
        split_redirects=split_path_redirects,
    )
    for old_compound, new_compound in compound_redirects:
        redirect_rows.append(
            {
                "old_id": old_compound, "new_id": new_compound,
                "old_path": "", "new_path": "",
            }
        )
    for citing_dir, old_link, new_link in dir_link_redirects:
        redirect_rows.append(
            {
                "old_id": old_link, "new_id": new_link,
                "old_path": "", "new_path": "", "citing_dir": citing_dir,
            }
        )
    for old_split_citation, new_split_citation in _drop_contested_split_redirects(
        split_path_redirects
    ):
        redirect_rows.append(
            {
                "old_id": old_split_citation, "new_id": new_split_citation,
                "old_path": "", "new_path": "",
            }
        )

    # Alongside the vendored-manifest stamp below, and after the citation rewrite for the
    # same reason it is: a header this run writes carries no legacy token to rewrite.
    files_written = [*files_written, *_stamp_reference_targets(root, reference_targets)]
    # The same reason, for the two README populations that pass structurally cannot reach:
    # one it was told is `routed`, one that did not exist when it read the tracked tree. A
    # `was:` written before the sweep would be rewritten into the new path, destroying the
    # one field that records where the file came from.
    files_written = [*files_written, *_stamp_regenerated_readmes(root, readme_origins)]
    # Ruling 101 clause 1's family index, and clause 3's check that the sections the
    # rewrite pointed at are actually there and actually list a choice. Written after the
    # sweep for the third instance of the same reason: every row quotes a `was:` value,
    # which is a pre-migration path the sweep would rewrite. Checked immediately after
    # writing rather than at the end, so the check reads the bytes this run just wrote.
    split_index_paths = _write_split_source_indexes(root, split_sources, token_map)
    files_written = [*files_written, *split_index_paths]
    index_faults = _split_index_violations(root, index_resolved)

    skipped_vendored: list[str] = []
    # `to_stamp` only -- a manifest already carrying front matter this migration did not
    # write is in `vendored_scan.deferred`, and prepending a second `---` block to it is
    # exactly what NT-0019 §4 step 5's Reference section refuses (the header has to be
    # MERGED, which is W37-6 Task 1's work). Every one of them is reported by name, with
    # this same reason, on `MigrateResult.deferred_reference_stamps`; there is no second
    # copy of that list here, deliberately (`NT-0003`).
    for skill_md in vendored_scan.to_stamp:
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

    redirects_written = _write_redirects(root, redirect_rows)
    index_written = _regenerate_index_for_migrate(root)
    process_core_written = _reconcile_process_core_digest(root)
    # #25's ruling: a padded citation of a real governed thing is normalised like any
    # other citation, once `docs/INDEX.md` exists to give conjunct 3 its authority.
    files_written = [*files_written, *_normalize_padded_citations(root)]

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
        # Reported by `locator`, never by `key`: a unit's key is relative to its own
        # scope (`example-agent.md`), and a path a reader cannot resolve without knowing
        # which scope produced it is the CLAUDE.md §13 reference defect in a report line.
        deferred_reference_stamps=tuple(
            (unit.locator, census.excepted[unit.key])
            for census in reference_censuses
            for unit in census.units
            if unit.key in census.excepted
        ),
        index_resolved_split_citations=tuple(index_resolved),
        unresolved_split_citations=tuple(unrewritten_citations),
        split_index_violations=tuple(index_faults),
        generated_paths=tuple(dict.fromkeys([
            *readme_written, *split_index_paths, *redirects_written, *index_written,
            *process_core_written,
        ])),
    )


# ---------------------------------------------------------------------------------------
# Acceptance item (g), DP-3's executable form (Ruling 68, amended by Ruling 104): the
# migration diff, filtered to hunks in the six-class closed enumeration, is empty.
# Independent of `migrate`'s own bookkeeping — computed from two trees on disk plus the
# `REDIRECTS.csv` `migrate` wrote, never from anything `migrate` claims about itself while
# running — so a bug in what `migrate` *reports* cannot also hide from what it *did*.
# ---------------------------------------------------------------------------------------

#: The one file class 5 names, and only that file (Ruling 68 §2: "the `roadmap.md`
#: restructure of §4 step 3"). Kept singular rather than a set of "living, un-numbered
#: containers" — the earlier reading also swept in `docs/open-questions.md`, which the
#: ruling's text never names. A citation-token change to that file is an ordinary class-2
#: hunk, not something needing an exemption; folding it in here was over-exemption, not
#: fidelity to the ruling.
_ROADMAP_REL: Final = "docs/roadmap.md"

#: Ruling 68's closed enumeration, named — the ruling's own §2 wording, amended by Ruling
#: 104 §2/§3 for class 6. One entry per class, in the ruling's own order; there is no
#: seventh. Ruling 68 §3 obliges this: "(g)'s filter is implemented as code with the six
#: classes named, not as a shell pipeline composed at the console." The key is what a
#: per-class breakdown is bucketed by; the text is quoted so a reader holding none of this
#: module's context can check a bucket against the rule (`CLAUDE.md` §13, NT-0004).
_RULING_68_CLASSES: Final[tuple[tuple[str, str], ...]] = (
    ("1-front-matter-stamp",
     "a front-matter block added, together with the legacy prose or bullet header it "
     "replaces being removed (§4 step 5)"),
    ("2-reference-token",
     "a reference token substituted inside a line, from the step-6 allow-list "
     "(§4 step 6)"),
    ("3-move",
     "a file moved or renamed, detected as a rename, with no content change beyond 1+2 "
     "(§4 step 4)"),
    ("4-split",
     "a split, where the concatenation of the outputs reproduces the input's body lines "
     "in order (§4 step 2)"),
    ("5-roadmap-restructure",
     f"the `{_ROADMAP_REL}` restructure of §4 step 3 — permitted unconditionally, exactly "
     "as Ruling 68 §2 states it, which gives this one named file no content predicate"),
    ("6-generated-artifact",
     "Ruling 104 §2: a generated artifact regenerated in full — a file whose entire "
     "content is the output of one of the migration's generators, replaced whole and "
     "never partially edited. `INDEX.md` (every one the migration generates — Ruling 104 "
     "§3), `REDIRECTS.csv`, `docs/contracts/`, the core-JSON digest and the §5.2 "
     "generated READMEs are its EXAMPLES and MEMBERS, not the whole of it. Tested by the "
     "property, not by path — but the property is *the generator*, not mere "
     "reproducibility (W37-6 channel `:394-417`, correcting the earlier content-equality-"
     "only reading, whose broken input was a deterministic wrong rewrite passing as "
     "generated for having no way to be told apart from one): `classify_migration_diff`'s "
     "`_try_class6` requires membership in `_run_second_migration`'s own "
     "`MigrateResult.generated_paths` first, and only then the independent second "
     "run's content equality"),
)

#: The bucket for a hunk in none of the above. Ruling 68 §2: "A hunk the filter cannot
#: classify fails; it is never passed through." This bucket's population **is** the
#: violation list, so a reader can never be shown a green row with a non-empty residue.
CLASSIFIED_BY_NONE: Final = "classified-by-none"


@dataclass(frozen=True)
class MigrationDiffClassification:
    """Every file the migration diff touches, assigned to exactly one Ruling 68 class or
    to `CLASSIFIED_BY_NONE`.

    `per_class` and `violations` are two views of one walk, not two measurements: the
    residue bucket's size is `len(per_class[CLASSIFIED_BY_NONE])` and its members are the
    files `violations` names. A breakdown computed separately from the total it belongs to
    is how the parts stop summing to the whole while both look right
    (`docs/notes/0003-duplicated-status-goes-stale.md`, applied to a count).
    """

    #: class key -> the repo-relative paths that class accounts for. Every class in
    #: `_RULING_68_CLASSES` is present, including the ones with an empty list, so a zero
    #: is a printed zero rather than a missing row.
    per_class: Mapping[str, tuple[str, ...]]
    #: One human-readable line per unclassifiable file, naming the file.
    violations: tuple[str, ...]
    #: Files present and byte-identical in both trees: not a hunk at all, and excluded
    #: from every class. Printed as the denominator's complement so that "N classified"
    #: can be read against the size of the tree it was measured over.
    unchanged: int

    @property
    def population(self) -> int:
        """Every file this walk assigned somewhere — the denominator the per-class
        figures are parts of."""
        return sum(len(v) for v in self.per_class.values())

    def summary(self) -> str:
        parts = [f"{key}={len(self.per_class.get(key, ()))}" for key, _ in _RULING_68_CLASSES]
        parts.append(f"{CLASSIFIED_BY_NONE}={len(self.per_class.get(CLASSIFIED_BY_NONE, ()))}")
        return ", ".join(parts)


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


def _run_second_migration(old_root: Path) -> tuple[Path, MigrateResult]:
    """A second, independent `migrate()` run against a fresh copy of `old_root`, in a
    throwaway directory — class 6's oracle for "would the migration have produced this
    file, in full?", and (W37-6 channel `:394-417`) the source of the run's own recorded
    generated-output set that decides whether class 6 even applies to a given path.

    Ruling 104 §2's class 6 is a **property**: "a file whose entire content is the output
    of one of the migration's generators". `migrate()` is the only generator this module
    ships, and its own documented guarantee (module docstring above: "two independent runs
    from the same starting input produce byte-identical output") is exactly what makes a
    second, independent run a faithful oracle for that property — with no per-artifact
    regenerator to hand-write and keep in sync, which is the drift Ruling 67 §2 and Ruling
    68 §3 both warn against ("implementing it twice is how the two drift apart"). A file
    whose content differs from this run's — because it was hand-edited after generation,
    or partially edited — fails the property exactly as Ruling 104's own broken-input proof
    requires.

    The same invariant that makes the second run's *content* a faithful oracle also makes
    its `MigrateResult.generated_paths` a faithful stand-in for the population's own
    recorded set: both runs start from the same `old_root`, so the two sets are the same
    set, not merely two runs that happen to agree. Returning it here — rather than a second
    call to `migrate` on `new_root`'s own history, which no longer exists once a caller has
    only the post-migration tree — is what lets `_try_class6` key on the generator that
    wrote a path instead of on whether the path's content happens to be reproducible.

    The caller owns the returned directory and must remove it.
    """
    tmp = Path(tempfile.mkdtemp(prefix="doc-id-class6-"))
    shutil.copytree(old_root, tmp, dirs_exist_ok=True)
    result = migrate(tmp)
    return tmp, result


def classify_migration_diff(
    old_root: Path, new_root: Path
) -> MigrationDiffClassification:
    """Assign every file `migrate`'s own output at `new_root` (compared against the
    pre-migration snapshot at `old_root`) touches to one of Ruling 68's six permitted
    classes, or to `CLASSIFIED_BY_NONE`.

    Ruling 68 §2 states the enumeration and then: *"A hunk the filter cannot classify
    fails; it is never passed through. A filter that silently drops what it does not
    understand is the same defect as the vanished scan root that once made five checks
    skip while the audit printed 'All checks passed' and exited 0."* Every branch below
    therefore ends in a named class or in a violation; there is no `continue` that means
    "not sure".

    Classes 1 and 2 share one content predicate, `frozen_file_matches_after_migration_stamp`
    — loaded from `scripts/audit-docs.py`, never reimplemented, per Ruling 68 §3's *"the
    frozen-family branch of the filter calls check 34's DP-7 predicate rather than
    reimplementing it"* and its *"one definition of 'reference tokens only', not two ...
    implementing it twice is how the two drift apart"*. They are **attributed** apart, by
    running the predicate's two stages in order: a file whose stripped body already equals
    the source's needed no token inversion and is class 1 alone; one that needs the
    inversion too is counted under class 2.

    Class 3 (a move) is attributed by the `REDIRECTS.csv` old_path/new_path difference and
    still carries the same content predicate: a rename is permitted *"with no content
    change"* beyond the stamp and the token rewrite it necessarily also receives.

    Class 5 (`docs/roadmap.md`) is permitted unconditionally, by path identity of that one
    named file — legitimate here for the reason Ruling 68 §2 itself gives it no content
    predicate, and *not* the general path-exclusion Ruling 68 §2 refused at `:232` (thirteen
    §5.2 rows mixing script output and hand edits in the same file) or Ruling 104 forbids
    for class 6.

    Class 6 is tried, for anything that does not fit 1-5, in two conditions: first,
    membership in `_run_second_migration`'s own recorded generated-output set (the
    generator, per Ruling 104 §2 — never a path pattern); only for a member is content
    then checked against that same independent regeneration. A file outside the set fails
    class 6 regardless of content equality — the W37-6 channel `:394-417` fix, since
    content equality alone cannot tell a generated artifact from a deterministic defect
    the migration reproduces identically on both runs.
    """
    audit_docs = _load_audit_docs()
    rows = _read_redirect_rows(new_root)
    # Ruling 105 §2: every id this run itself allocated, so the shared DP-7 predicate can
    # tell "a header this run wrote" from "any leading block that happens to parse" --
    # `.claude/skills/**` and `.claude/agents/` foreign front matter mostly parses (its
    # `name:`/`description:` keys land in `.extra` with no error) but its `id` is never
    # one of these, so it is correctly left unstripped by both sides of the comparison.
    allocated_ids = frozenset(row["new_id"] for row in rows if row.get("new_id"))
    # The Reference family (`.claude/roles/`, `.claude/agents/`, `.claude/skills/*/
    # SKILL.md`, every `README.md`) carries no `id:` line at all (NT-0019 §1.2), so
    # `allocated_ids` can never confirm one of *its* stamps as this run's own -- found
    # live on `.claude/roles/example-role.md`, headerless before this run and
    # Reference-stamped by it, whose citation rewrite then had no path to reproduce the
    # merge-base bytes. `_discover_reference_stamp_targets` is the same function
    # `migrate` itself calls to decide what to stamp, run here over `old_root` (the
    # pre-migration tree this diff is against) rather than `new_root`, since a target's
    # own front-matter state is what routes it and `new_root`'s copy already carries the
    # stamp. `routed=()` (the default): the resulting set can only be a harmless
    # superset of the real one for this predicate's purposes -- any file it wrongly adds
    # gets a real id-bearing header instead of a headerless one, so the id branch above
    # matches it first and this fallback is never reached for it.
    # A vendored skill's own manifest is stamped the identical headerless way (`migrate`'s
    # `vendored_scan.to_stamp` loop, `_stamp_header("REFERENCE", None, ...)` plus
    # `vendored`/`origin`), but it is a *second*, disjoint population --
    # `_discover_reference_stamp_targets` itself excludes every vendored manifest
    # (`_ACCOUNTED_VENDORED`) because a second writer, not this one, stamps it. Found
    # live on `.claude/skills/<vendored>/SKILL.md`: the same "no id" gap, one population
    # over from the one the comment above names.
    reference_stamp_paths = frozenset(
        target.rel for target in _discover_reference_stamp_targets(old_root)[0]
    ) | frozenset(
        path.relative_to(old_root).as_posix()
        for path in _discover_vendored_skill_manifests(old_root).to_stamp
    )

    def _collision_safe_inverse(pairs: Iterable[tuple[str, str]]) -> dict[str, str]:
        """`{new: old}`, refusing a `new` key two different `old` values both claim.

        Task 4 item 4, found live: `_path_citation_redirect_rows`' own docs-stripped form
        collided here on the real corpus -- `docs/audit/register.md` and `docs/audit/
        phases/1b/register.md` (the phase-1b merge target) both strip to a `new_id` of
        `findings/register.md`, with *different* `old_id`s (`audit/register.md` vs
        `audit/phases/1b/register.md`). A flat `{new: old}` dict comprehension picks
        whichever row iterates last, silently -- the exact `dict.update` failure mode
        `TokenMapCollisionError`'s own docstring already names for the forward direction,
        recurring here in the inverse. There is no per-citation evidence at this point to
        say which old form a given occurrence of the new one actually was (that would need
        Ruling 100's own three determinants, re-run backwards), so a genuinely contested
        key is dropped rather than guessed: the file it would have inverted for is
        correctly `classified-by-none` instead of silently misinverted to the wrong source.
        """
        by_new: dict[str, set[str]] = {}
        for new, old in pairs:
            by_new.setdefault(new, set()).add(old)
        return {new: next(iter(olds)) for new, olds in by_new.items() if len(olds) == 1}

    # Task 4 item 4: a `citing_dir`-scoped row (`_bare_basename_rewrite`'s directory-
    # relative link text) is correct only for files in that one directory -- folding it
    # into the flat, tree-wide `redirects_inverse` below would silently misinvert any
    # other file whose own relative link happened to read the same text. Split at the
    # source: `redirects_inverse` keeps exactly the rows this check always had (global
    # id/path pairs); `dir_redirects_inverse` is looked up per file, by that file's own
    # directory, at each of the two call sites below.
    redirects_inverse = _collision_safe_inverse(
        (row["new_id"], row["old_id"])
        for row in rows
        if row.get("old_id") and row.get("new_id") and not row.get("citing_dir")
    )
    dir_pairs: dict[str, list[tuple[str, str]]] = {}
    for row in rows:
        citing_dir = row.get("citing_dir") or ""
        if citing_dir and row.get("old_id") and row.get("new_id"):
            dir_pairs.setdefault(citing_dir, []).append((row["new_id"], row["old_id"]))
    dir_redirects_inverse: dict[str, dict[str, str]] = {
        citing_dir: _collision_safe_inverse(pairs) for citing_dir, pairs in dir_pairs.items()
    }

    def _inverse_for(rel: str) -> Mapping[str, str]:
        """The merged inverse for a file at `rel`: the global id/path pairs, plus any
        directory-scoped link repoints recorded for `rel`'s own directory."""
        local = dir_redirects_inverse.get(posixpath.dirname(rel))
        return {**redirects_inverse, **local} if local else redirects_inverse

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
    buckets: dict[str, list[str]] = {key: [] for key, _ in _RULING_68_CLASSES}
    buckets[CLASSIFIED_BY_NONE] = []
    violations: list[str] = []
    consumed_new: set[str] = set()
    unchanged = 0

    # Class 6's oracle is expensive (a full second `migrate()` run) and most files never
    # need it, so it is built at most once, on first use, and torn down when this call
    # returns — never left for a caller to leak.
    second_run: list[tuple[Path, MigrateResult]] = []

    def _second_run() -> tuple[Path, MigrateResult]:
        if not second_run:
            second_run.append(_run_second_migration(old_root))
        return second_run[0]

    def _second_run_text(rel: str) -> str | None:
        root2, _result = _second_run()
        try:
            return (root2 / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    def _fail(rel: str, message: str) -> None:
        buckets[CLASSIFIED_BY_NONE].append(rel)
        violations.append(message)

    def _try_class6(rel: str) -> bool:
        """True (and bucketed) iff `rel` is a member of the run's own recorded
        generated-output set (Ruling 104 §2's property is *"the output of one of the
        migration's generators"* — the generator, never whether the content happens to be
        reproducible) **and** its content in `new_root` equals what an independent second
        `migrate()` run over `old_root` produces at that same path.

        W37-6 channel `:394-417`: keying on content equality alone made a deterministic
        defect indistinguishable from a generated artifact — every deterministic write is
        reproducible, including a wrong one, so a body line the migration corrupts the same
        way twice used to pass class 6 for having no other content difference to explain
        it. The membership test is the first, cheap condition; the second run's content
        equality — kept exactly as it was — narrows it further, catching a generated file a
        caller hand-edited after the fact (`test_class6_a_hand_edited_readme_fails_and_
        names_the_file`, unchanged by this fix).
        """
        _root2, result = _second_run()
        if rel not in result.generated_paths:
            return False
        actual = new_files.get(rel)
        if actual is None:
            return False
        expected = _second_run_text(rel)
        if expected is None or expected != actual:
            return False
        buckets["6-generated-artifact"].append(rel)
        return True

    def _classify_content(
        old_rel: str, new_rel: str, compare_against: str, new_text: str, *, moved: bool,
        stamped_header_removed: bool,
    ) -> None:
        """Put one old->new file pair in class 1, 2 or 3; fall back to class 6 (a whole
        regenerated body, e.g. a carried or fresh family README); or fail it."""
        label = old_rel if not moved else f"{old_rel} -> {new_rel}"
        if stamped_header_removed and not _has_front_matter(new_text):
            _fail(
                old_rel,
                f"{label}: the legacy header was removed but no front-matter block was "
                "added — Ruling 68 class 1 permits the pair, not either half",
            )
            return
        stripped = _strip_front_matter(new_text)
        if stripped.strip("\n") == compare_against.strip("\n"):
            buckets["3-move" if moved else "1-front-matter-stamp"].append(old_rel)
            return
        if audit_docs.frozen_file_matches_after_migration_stamp(
            compare_against, new_text, _inverse_for(new_rel), allocated_ids=allocated_ids,
            old_rel=old_rel, new_rel=new_rel, reference_stamp_paths=reference_stamp_paths,
        ):
            buckets["3-move" if moved else "2-reference-token"].append(old_rel)
            return
        if _try_class6(new_rel):
            return
        _fail(
            old_rel,
            f"{label}: content changed beyond header stamp + token rewrite"
            + ("" if moved else ", with no REDIRECTS.csv move recorded"),
        )

    def _lines_no_blank(text: str) -> list[str]:
        return [ln for ln in text.splitlines() if ln.strip()]

    try:
        for old_rel, old_text in old_files.items():
            if old_rel == _ROADMAP_REL:
                buckets["5-roadmap-restructure"].append(old_rel)
                consumed_new.add(old_rel)
                continue
            if old_text is None:
                _fail(old_rel, f"{old_rel}: not UTF-8 text — this filter cannot classify it")
                continue
            compare_against = header_converted_bodies.get(old_rel, old_text)
            stamped_header_removed = old_rel in header_converted_bodies
            targets = moves.get(old_rel)
            if not targets:
                new_text = new_files.get(old_rel)
                if new_text is None:
                    _fail(
                        old_rel,
                        f"{old_rel}: vanished with no REDIRECTS.csv row accounting for it",
                    )
                    continue
                consumed_new.add(old_rel)
                if new_text == old_text:
                    unchanged += 1
                    continue
                _classify_content(
                    old_rel, old_rel, compare_against, new_text, moved=False,
                    stamped_header_removed=stamped_header_removed,
                )
                continue

            if len(targets) == 1:
                new_rel = targets[0]
                new_text = new_files.get(new_rel)
                if new_text is None:
                    _fail(
                        old_rel,
                        f"{old_rel} -> {new_rel}: REDIRECTS.csv names this target, but it "
                        "does not exist",
                    )
                    continue
                consumed_new.add(new_rel)
                _classify_content(
                    old_rel, new_rel, compare_against, new_text, moved=True,
                    stamped_header_removed=stamped_header_removed,
                )
                continue

            # A genuine split: several *distinct* target files share one `old_path` row.
            # The concatenation of every target's own body (front matter stripped, tokens
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
                    _fail(old_rel, f"{old_rel}: split target {new_rel} does not exist")
                    ok = False
                    continue
                consumed_new.add(new_rel)
                stripped = _strip_front_matter(new_text)
                target_inverse = _inverse_for(new_rel)
                for new_token in sorted(target_inverse, key=len, reverse=True):
                    stripped = re.sub(
                        rf"\b{re.escape(new_token)}\b", target_inverse[new_token], stripped
                    )
                pieces.append(stripped)
            if ok:
                joined_lines = [ln for piece in pieces for ln in _lines_no_blank(piece)]
                if joined_lines != _lines_no_blank(old_text):
                    _fail(
                        old_rel,
                        f"{old_rel}: split targets {targets} do not reproduce this "
                        "file's body lines in order",
                    )
                else:
                    buckets["4-split"].append(old_rel)

        for new_rel, _new_text in new_files.items():
            if new_rel in consumed_new:
                continue
            if new_rel in old_files:
                continue  # untouched, same path — handled by the old_files loop above
            if _try_class6(new_rel):
                continue
            _fail(
                new_rel,
                f"{new_rel}: appeared with no REDIRECTS.csv row naming where it came from",
            )
    finally:
        if second_run:
            shutil.rmtree(second_run[0][0], ignore_errors=True)

    return MigrationDiffClassification(
        per_class={k: tuple(v) for k, v in buckets.items()},
        violations=tuple(violations),
        unchanged=unchanged,
    )


def migration_diff_violations(old_root: Path, new_root: Path) -> list[str]:
    """Every file `migrate`'s own output at `new_root` does not fit Ruling 68's six-class
    closed enumeration — empty means DP-3's executable form of NT-0019 §7 (g) holds. A thin
    wrapper over `classify_migration_diff`'s `violations`, kept as its own function because
    existing callers (and this module's own CLI-level acceptance tests) name it directly.
    """
    return list(classify_migration_diff(old_root, new_root).violations)


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
    # `getattr`, not `args.verify`: `migrate`'s public entry point is also called with
    # a hand-built `argparse.Namespace` by the tests that predate `--verify`
    # (`tests/test_doc_id_migrate.py`), and a bare attribute access turns adding a flag
    # into an unrelated test failure. Absent means off, which is the pre-existing
    # behaviour every such caller expects.
    if getattr(args, "verify", _VERIFY_OFF) is not _VERIFY_OFF:
        return _cmd_migrate_verify(args)
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
    # Unconditionally, including the zero, and by name: a Reference file in §4 step 5's
    # stamp set that this run did not stamp is *listed*, never quietly absent (W37-5c
    # item 2; F83's condition 1 applied to a deferral).
    print(
        f"doc-id.py migrate: {len(result.deferred_reference_stamps)} Reference stamp "
        "target(s) in scope and not stamped by this run:",
        file=sys.stderr,
    )
    for where, reason in result.deferred_reference_stamps:
        print(f"  {where} -- {reason}", file=sys.stderr)
    # Bucket (iv), unconditionally and by name — including the zero, for the same reason
    # the two counts above are printed when they are zero: a population nothing reports is
    # a population nothing can disposition, and these are exactly the citations the ruling
    # requires be dispositioned by name before a run.
    print(
        f"doc-id.py migrate: {len(result.unresolved_split_citations)} citation(s) of a "
        "split source left unrewritten (no single target determined by the citation):",
        file=sys.stderr,
    )
    for cite in result.unresolved_split_citations:
        print(
            f"  {cite.citing_file}:{cite.line} cites {cite.old_rel} -- candidates: "
            f"{', '.join(cite.candidates)}",
            file=sys.stderr,
        )
    # Ruling 101 clause 1's population: bucket (iv), rewritten to the family index rather
    # than left to dangle. Printed with the count first and then by name, because the
    # count is the gate figure ("bucket (iv) = N, unrewritten = 0") and the names are what
    # a reader disposes of.
    print(
        f"doc-id.py migrate: {len(result.index_resolved_split_citations)} citation(s) of "
        "a split source determined no single target and were resolved to their family "
        "index section (Ruling 101 clause 1):",
        file=sys.stderr,
    )
    for cite in result.index_resolved_split_citations:
        print(
            f"  {cite.citing_file}:{cite.line} cites {cite.old_rel} -> "
            f"{cite.resolved_to} -- candidates: {', '.join(cite.candidates)}",
            file=sys.stderr,
        )
    # Ruling 101 clause 3, unconditionally including the zero: a link into an index
    # section that does not exist or lists no choice resolves at the file level, so
    # nothing else in this run or in the gate can see it.
    print(
        f"doc-id.py migrate: {len(result.split_index_violations)} citation(s) resolved to "
        "a family index section that is missing or lists fewer than two documents:",
        file=sys.stderr,
    )
    for violation in result.split_index_violations:
        print(f"  {violation}", file=sys.stderr)
    print(f"doc-id.py migrate: {len(result.assigned)} id(s) assigned")
    return 0


# Sentinel distinguishing "`--verify` absent" from "`--verify` given with no path", which
# argparse's `nargs="?"` cannot do with `default=None` alone: the second form means "build
# the snapshot in a temporary directory and delete it", a legitimate and in fact the default
# way to run the instrument.
_VERIFY_OFF: Final = object()


def _cmd_migrate_verify(args: argparse.Namespace) -> int:
    """Ruling 102 §1's instrument. Never touches `--repo-root`'s working tree."""
    workdir = None if args.verify is None else Path(args.verify)
    try:
        result = _docverify.verify(
            sys.modules[__name__],
            repo_root=args.repo_root,
            ref=args.ref,
            workdir=workdir,
            keep=args.keep,
            with_baseline=not args.no_baseline,
        )
    except _docverify.WorkingCheckoutRefusedError as exc:
        print(f"doc-id.py migrate --verify: refused: {exc}", file=sys.stderr)
        # A distinct code from a failing row: "I would not run" and "I ran and it is red"
        # are different answers, and a CI step that cannot tell them apart reports a
        # misconfiguration as a corpus defect.
        return 2
    except GitArchiveError as exc:
        print(f"doc-id.py migrate --verify: {exc}", file=sys.stderr)
        return 2
    print(_docverify.render(result))
    # 0 green · 1 the standing red, unchanged · 2 refused to run · 3 the verdict set moved.
    # Exit 3 is what makes a NEW failure distinguishable from the red Ruling 102 §1 requires
    # until the migration lands: exit 1 is true of every run in that period and so says
    # nothing about the change under review (F102).
    return result.exit_code


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
    migrate_parser.add_argument(
        "--verify",
        nargs="?",
        const=None,
        default=_VERIFY_OFF,
        metavar="SNAPSHOT",
        help="Ruling 102 §1: run the migration on a disposable snapshot built from --ref, "
        "compute all nine NT-0019 §7 (a)-(i) rows with their predicates, exit 1 on any "
        "fail. SNAPSHOT is a new or empty directory outside any git work tree; omit it to "
        "use a temporary directory. Refuses a real checkout (exit 2).",
    )
    migrate_parser.add_argument(
        "--ref",
        default="HEAD",
        help="--verify only: the ref to snapshot (default: HEAD).",
    )
    migrate_parser.add_argument(
        "--keep",
        action="store_true",
        help="--verify only: keep the temporary snapshot instead of deleting it.",
    )
    migrate_parser.add_argument(
        "--no-baseline",
        action="store_true",
        help=f"--verify only: skip the {_docverify.BASELINE_REF} baseline tree §7(f)'s "
        "first reading needs.",
    )
    _add_repo_root_argument(migrate_parser)
    migrate_parser.set_defaults(func=_cmd_migrate)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
