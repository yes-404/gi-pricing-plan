#!/usr/bin/env python3
"""doc-id.py — the id allocator and checker: `next` and `check`.

ADR-2136: the one-off RFC-937 migration (`migrate`, `migrate --verify`, `widen`) and its
verification instrument are retired with the frozen record families they migrated. What
stays is what the one id sequence still needs for requirements, decisions and workflows:

    python3 scripts/doc-id.py next [--ref REF]
    python3 scripts/doc-id.py check [--classify]

`next` prints the largest id number found at REF (default origin/main) plus one, reading
the front matter of every governed document at that ref, the bold requirement ids in the
specs, the work rows of the frozen roadmap and the frozen docs/INDEX.md. `check` fails on a
number claimed by two documents and on a header whose id disagrees with its filename.

**Standard library only** — see `scripts/_docid.py`'s module docstring for why.
"""

from __future__ import annotations

import argparse
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
# at 5 and widens only when INDEX.md passes 90 000 (RFC-937 §1.8), so a handful of small
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
    `fetch-depth: 0` is what makes `origin/main` resolvable in CI (RFC-937 §5.8), and a
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
    an uncommitted local file — RFC-937 §1.7 says so, and DP-8's contiguity argument in
    `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md` depends on it: an unmerged
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
        # `ZipFile.extractall` drops the mode bits `git archive` recorded, so every file
        # comes out 0644 and an executable script silently loses its exec bit. That is a
        # difference between the materialised tree and the committed one, which is exactly
        # what a materialisation must not have: restore the permission bits the archive
        # carries in `external_attr`'s high 16 bits.
        for info in zf.infolist():
            if info.is_dir():
                continue
            mode = info.external_attr >> 16
            if mode:
                (dest / info.filename).chmod(mode & 0o7777)
    zip_path.unlink()


def materialize_ref_with_history(ref: str, dest: Path, *, repo_root: Path) -> None:
    """Materialise `ref` into `dest` **as a git repository carrying its real history**.

    `git archive` + `git init` produces a tree whose content is right and whose history is
    a single synthetic commit. That is not equivalent: RFC-937 item 1 makes a module's
    **git first-commit date** the `created` value id allocation sorts on
    (`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`,
    D1 at `:247` — "numbers carry chronology"),
    so git history is a *declared input* to the migration, not an incidental property of
    the checkout it happens to run in. A one-commit tree has no first-commit dates to read,
    and the old `date.today()` fallback silently substituted for all of them — re-keying
    the whole sequence and displacing hundreds of ids relative to a real run.

    Supplying the history makes `--verify` and a real run allocate identically **by
    construction**, rather than by a fallback that happens to agree on the day it is run.

    A local `git clone` is used rather than `git worktree add`: a worktree's `.git` points
    back into the source repository, and `migrate()` commits into the tree it is given, so
    a worktree would write objects and refs into the real repository. A clone owns its
    object store. `origin` is removed afterwards so the result still satisfies
    `_docverify.assert_tree_is_snapshot`'s "a snapshot has no remotes" invariant, and the
    checkout is detached so no branch of the source repository is implicated.
    """
    if not ref_exists(ref, repo_root):
        raise GitArchiveError(
            f"{ref!r} does not resolve to a commit in {repo_root} — fetch it first "
            f"(e.g. `git fetch origin main`)"
        )
    sha = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", f"{ref}^{{commit}}"],
        capture_output=True, text=True, check=False,
    ).stdout.strip()

    def _run(args: list[str], *, cwd: Path | None = None) -> None:
        proc = subprocess.run(args, capture_output=True, text=True, check=False, cwd=cwd)
        if proc.returncode != 0:
            raise GitArchiveError(
                f"`{' '.join(args)}` exited {proc.returncode}: "
                f"{proc.stderr.strip() or '(no stderr)'}"
            )

    dest.mkdir(parents=True, exist_ok=True)
    _run(["git", "clone", "--quiet", "--no-checkout", str(repo_root), str(dest)])
    _run(["git", "-C", str(dest), "remote", "remove", "origin"])
    _run(["git", "-C", str(dest), "checkout", "--quiet", "--detach", sha])
    if is_shallow_repository(dest):
        raise GitArchiveError(
            f"{dest} came out of `git clone {repo_root}` shallow — the source repository "
            "is itself a shallow clone, so the git first-commit dates id allocation is "
            "keyed on are not all present. Fetch full history (`git fetch --unshallow`) "
            "before running this instrument."
        )


def is_shallow_repository(root: Path) -> bool:
    """True when `root`'s git history is truncated. A shallow tree's first-commit dates
    are wrong wherever the truncation cut, and `created` is a declared allocation input —
    so this is checked, not assumed, and recorded in the run's own provenance fields.
    """
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-shallow-repository"],
        capture_output=True, text=True, check=False,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def history_commit_count(root: Path) -> int:
    """`git rev-list --count HEAD` for `root`, or 0 when there is no resolvable HEAD."""
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-list", "--count", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip().isdigit():
        return 0
    return int(proc.stdout.strip())


# ---------------------------------------------------------------------------------------
# `next` — the four sources RFC-937 §1.7 names, each a pure function over a tree on disk
# (a real checkout, a fixture directory, or a materialized git ref — all the same to these).
# ---------------------------------------------------------------------------------------

# Document-family directories that hold one governed file per number, flat (RFC-937 §1.4).
_DOC_FAMILY_DIRS: Final = (
    "workflows", "adrs", "rfcs", "plans", "ledgers",
    "rulings", "research", "closures", "findings",
)


def _candidate_header_paths(tree_root: Path) -> Iterator[Path]:
    """Every path RFC-937 §1.5 says carries a header: the document-family directories,
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
    check 31 gets by path, RFC-937 §1.4) and vendored skill content (§1.5: a vendored
    skill's files are exempt from stamping, so they are never a real source of a live id —
    `_docid.is_vendored` tests membership in `_docid._VENDORED_SKILLS`, RL-990's
    declared constant) *before* attempting to parse either, so neither counts as a "skip":
    exclusion is not failure.

    A file whose front matter does not fit RFC-937 §1.5's closed grammar at all —
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
    """Source 1 of 4 (RFC-937 §1.7): every header `id:` field under the governed
    locations — see `scan_governed_headers` for exactly what counts and why. Drops the
    `.skipped` report: a caller that needs it calls `scan_governed_headers` directly, as
    the CLI does for its own reporting.
    """
    for prefix, number, _path in scan_governed_headers(tree_root).ids:
        yield prefix, number


_SPEC_BOLD_RE: Final = re.compile(r"\*\*(FR|NFR|DEP|OQ)-0*(\d+)\*\*")


def scan_spec_bold_ids(tree_root: Path) -> Iterator[tuple[str, int]]:
    """Source 2 of 4: every bold requirement/open-question id inside `docs/specs/*.md`
    (RFC-937 §1.2: "requirement rows are bold ids in tables")."""
    specs_root = tree_root / "docs" / "specs"
    if not specs_root.is_dir():
        return
    for path in sorted(specs_root.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in _SPEC_BOLD_RE.finditer(text):
            yield match.group(1), int(match.group(2))


# A WK-/SL- row's own id is cited in its heading (RFC-937 §1.9's GitHub-alignment table
# titles a slice issue `SL-1242: <title>`, and §1.5 calls the row's own line "the row's
# heading"). Matches `### WK-1201 — Batch frame contract` and the same for `SL-`.
_ROADMAP_ROW_RE: Final = re.compile(r"^#{1,6}[ \t]+.*?\b(WK|SL)-0*(\d+)\b", re.MULTILINE)


def scan_roadmap_row_ids(tree_root: Path) -> Iterator[tuple[str, int]]:
    """Source 3 of 4: every WK-/SL- row heading inside `docs/roadmap.md`.

    The exact heading shape is inferred (W37-1's restructured `docs/roadmap.md` has not
    landed at the time this was written) rather than pinned by a worked example in
    RFC-937 or the map plan — flagged to the lead as a coordination point, not a blocker:
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
# (`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`'s own illustrative `PL-01240`,
# quoted verbatim inside another row's body, is exactly this) without correcting the
# opposite failure -- the id `scan_bold_id_rows` never turned into a row at all, which is
# what `doc-id.py check`'s RFC-937 §7(b) noncontiguous-id failures actually are.
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
    """`max` across all four RFC-937 §1.7 sources, plus one. No id anywhere -> 1."""
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
# `check` — RFC-937 §1.7: "fails the gate on any duplicate or header/filename mismatch."
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

    Keyed on the bare number, never `(prefix, number)`: RFC-937 §1.1 rule 1 is one global
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


def check(tree_root: Path) -> list[CheckFailure]:
    """Every `doc-id.py check` failure at `tree_root`: duplicates and header/filename
    mismatches (ADR-2136: INDEX contiguity is no longer checked; INDEX is frozen).
    """
    return [
        *find_duplicate_ids(tree_root),
        *find_header_filename_mismatches(tree_root),
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


# Document-family directory name -> family word (RFC-937 §1.2's "Kind" column), for the
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
    never real ones — the same exemption check 31 gets by path, RFC-937 §1.4) rather than
    counting as `"none"`, which is reserved for a file this classifier cannot place at
    all — exactly the files a fresh, pre-migration `docs/` tree is full of today.

    `docs/specs/*.md` is classified `"requirement"`: it is a *container* for the FR-/NFR-/
    DEP-/OQ- row families (RFC-937 §1.2), not a document family in its own right, and
    "requirement" is the dominant content. This mapping — and the plain `docs/*.md` ->
    `"reference"`/`"none"` split below — is this script's own reasonable reading, not a
    table RFC-937 states outright; flagged as a coordination point for W37-1's templates
    and W37-4's checks 30-39 rather than asserted as settled.

    Widened by W37-5 (`migrate`'s own fixture-corpus proof of Acceptance Standard item 3
    needed it to be correct, not just documented as open): the five other living,
    top-level `docs/*.md` files RFC-937 §1.4's own tree names — `INDEX.md`,
    `REDIRECTS.csv`, `roadmap.md`, `open-questions.md`, alongside `README.md` — are
    `"reference"` too, not `"none"`. Before this widening, a post-migration tree carrying
    only those five plus `README.md` at the top level still reported four spurious
    `"none"` files, which is exactly the false failure this slice's own acceptance item
    (a) would otherwise have produced.

    Widened again W37-6, two census defects RFC-937 §1.2's own Reference row names and
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
      reason as the `README.md` widening above it. RL-1042 clause 1 puts a generated
      split-source index inside a family directory (`docs/rulings/INDEX.md`, ...), and
      without this it would be counted as a *member* of the family it indexes -- one
      spurious `"ruling"`/`"closure"`/`"plan"` per index file. An index of a family is
      Reference, exactly as that family's README is; RFC-937 §1.2's Reference row already
      names `INDEX.md` (as the top-level one), and nesting does not change what it is.
      This does **not** move the `"none"` count: an `INDEX.md` under a family directory
      already matched `_CLASSIFY_FAMILY_BY_DIR`, so the widening corrects which bucket it
      lands in, never whether it lands in one.
    """
    top_level_reference_files = frozenset(
        {
            "README.md", "INDEX.md", "REDIRECTS.csv", "roadmap.md", "open-questions.md",
            # `skills-map.md` — RFC-937 §5.2 `:315`: *"`skills-map.md` | citations rewrite
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
        if rel in (_docid.W37_11_RECORD_PATH, _docid.W37_11_RECORD_PRE_MOVE_PATH):
            # F102's own shape, caught before it repeated: an ordinary-named file added
            # under `docs/audit/` (not `_CLASSIFY_FAMILY_BY_DIR`'s "audit" -> anything,
            # since that subdir holds no document family of its own) falls to `"none"` by
            # default, moving row (a) from PASS the moment it is added — measured directly
            # against a real `migrate --verify` snapshot, not assumed (2026-09-05, PR
            # #756's own condition, found by running the instrument the row (a) EXPECTED_
            # VERDICTS entry already exists to catch). The record is governance data, not
            # a document in any §1.2 family, so `"reference"` is the correct bucket — the
            # same reading `process/`/`contracts/` and every `README.md`/`INDEX.md` already
            # get, declared by this one file's own path rather than by widening the
            # `"audit"` subdir wholesale (which would blind row (a) to a real stray file
            # landing there next). Both locations since W37-11's move: the current one,
            # and the pre-move one a pre-migration tree still holds
            # (`_docid.W37_11_RECORD_PRE_MOVE_PATH`'s own comment).
            family = "reference"
        elif parts[-1] in ("README.md", "INDEX.md"):
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
# `widen` — RFC-937 §1.8: "renames every padded file, rewrites every padded link target,
# appends to REDIRECTS.csv, updates the width in document-ids.md, regenerates INDEX.md;
# touches no citation, number, header or body line." Trigger: `INDEX.md` passes 90 000.
# ---------------------------------------------------------------------------------------



@dataclass(frozen=True)
class NextResult:
    """`next`'s answer, plus what it could not resolve — reported, not silent (same
    reasoning as `HeaderScan`, and over the same materialised tree, so `next`'s report and
    its number are always about the identical snapshot)."""

    number: int
    skipped: tuple[tuple[Path, str], ...]


#: The id standard, whose examples must never name a live-sequence integer
#: (`document-ids.md`'s 2026-09-28 amendment, WK-1178).
ID_STANDARD_PATH: Final = Path("docs") / "process" / "document-ids.md"
#: Any `<PREFIX>-<n>` token, padding stripped. Deliberately wider than the resolver's
#: family list: an example with an unknown prefix still names an integer.
_ANY_ID_TOKEN_RE: Final = re.compile(r"\b[A-Z][A-Z0-9]*-0*(\d+)\b")


class ExampleIdCollisionError(RuntimeError):
    """`next` would mint an integer that the id standard itself writes as an id."""


def id_standard_integers(tree_root: Path) -> frozenset[int]:
    """Every integer written as `<PREFIX>-<n>` in `tree_root`'s id standard (empty when the
    file is absent). A real citation's integer is always below `next`'s answer, since it
    names something already minted, so a member equal to that answer can only be an
    example, which is the collision `compute_next_at_ref` refuses.
    """
    path = tree_root / ID_STANDARD_PATH
    if not path.is_file():
        return frozenset()
    text = path.read_text(encoding="utf-8")
    return frozenset(int(m.group(1)) for m in _ANY_ID_TOKEN_RE.finditer(text))


def compute_next_at_ref(ref: str, *, repo_root: Path = REPO_ROOT) -> NextResult:
    """`compute_next`, but reading `ref`'s committed content rather than any local
    directory — the entry point `next`'s CLI uses.

    Refuses (`ExampleIdCollisionError`) when the answer appears as an id in the id
    standard **at the same ref**, never the working tree's copy: a stale or edited
    checkout must not decide whether the merged standard's examples collide.
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
        if number in id_standard_integers(tree):
            raise ExampleIdCollisionError(
                f"{number} appears as an id in {ID_STANDARD_PATH.as_posix()} at {ref!r}; "
                f"an example there must be a placeholder (`<PREFIX>-<n>`), never a "
                f"live-sequence integer. Rewrite the example, then mint."
            )
        skipped = scan_governed_headers(tree).skipped
        return NextResult(number=number, skipped=skipped)


# ---------------------------------------------------------------------------------------
# `migrate` — RFC-937 §4's seven steps (assign, split, restructure the roadmap, move,
# stamp, rewrite citations, regenerate), run once against a tree on disk. Built and proven
# against `tests/fixtures/docs-migration/` (W37-5); nothing in the real tree moves until
# W37-6 points `--repo-root` at it, under that slice's own preconditions.
#
# Two properties the tests pin (dispatch, `docs/plans/PL-00939-wk-697-one-id-per-governed
# -thing-map-plan.md` Slice W37-5): **deterministic** (two independent runs from the same starting
# input produce byte-identical output, including the number assignment) and **idempotent**
# (running `migrate` again on already-migrated output is a no-op, zero diff). Idempotency
# falls out of each discovery function's own shape: every `_discover_*` function below
# looks for a *legacy* shape only (a bullet-list ADR header, a `YYYY-MM-DD-` plan filename,
# a bare `F<n>` finding cell, a bold `**FR-XXX-N**`-style spec id with an alphabetic module
# segment — respelled schematically, 2026-09-04, RL-1044 §5.1's fence clause extended to
# row (d): the literal worked example is itself a §7(d) alternative match) — once a file is
# migrated it no longer has that shape (it moved, or its tokens
# changed to the numeric-only post-migration form), so a second run's discovery passes find
# nothing there and touch nothing. The one file that does *not* move or change shape
# detectably by absence is a vendored skill's own `SKILL.md` (RFC-937 §1.5): it is stamped
# in place, so its discovery function checks `_docid.parse_header` directly rather than
# relying on "the old thing is gone".
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
        "(front matter present but did not parse as RFC-937's header):",
        file=sys.stderr,
    )
    for _path, reason in skipped:
        # `reason` is a `HeaderError` message, which already leads with `{path}:{line}:`
        # (`_docid.py`'s own convention) — printing `path` again here would repeat it.
        print(f"  {reason}", file=sys.stderr)


def _cmd_next(args: argparse.Namespace) -> int:
    try:
        result = compute_next_at_ref(args.ref, repo_root=args.repo_root)
    except (GitArchiveError, ExampleIdCollisionError) as exc:
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
        "check", help="Check duplicate numbers and header/filename agreement."
    )
    check_parser.add_argument(
        "--classify",
        action="store_true",
        help="Print a per-family file count instead of checking.",
    )
    _add_repo_root_argument(check_parser)
    check_parser.set_defaults(func=_cmd_check)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
