#!/usr/bin/env python3
"""File census over the repository's tracked corpus — RFC-897 Stage 0.

`docs/plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md` §7 (Slice 2). RFC-897 asks three questions
(Q1, Q2, Q3) about the shape of this repository's file population — how many files, what
kinds, how they cluster — and none of them can be answered from recollection. This script
produces the evidence: one CSV row per tracked file, with a header, a corpus rule, and a
committed companion document (`docs/research/RS-00952-file-census-rfc-897-stage-0.md`) so the evidence is reproducible
by a reader holding none of this session's context.

**The corpus is `git ls-files`, never the working tree.** `docs/plans/PL-00929-rfc-897-fi
le-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md` §1 measured that a working-tree walk (`find`, `grep -r
--exclude-dir=.git`) picks up `.venv/`, `graphify-out/` and `node_modules/` when they exist
locally — directories that are not tracked and differ between two checkouts of the same
commit. A census is evidence only if it reproduces from a stated corpus; `git ls-files` is
the one enumeration that does, because it reads the index rather than the filesystem.

**Four columns, four rules, none of them silent:**

  - `area` is the first path segment (`rel.split("/", 1)[0]`) — a root file's area is its
    own name; the script forms no opinion on whether that is a good cluster. Clustering is
    Slice 3's, by a human reading — a script that proposed categories would make Slice 3
    review its own output.
  - `name_pattern` is the basename with every `\\d{4}-\\d{2}-\\d{2}` run replaced by `DATE`,
    then every remaining run of digits replaced by `N` — see `name_pattern()` below.
  - `mutability` is a **guess, labelled one**, derived from directory prefix only —
    `docs/plans/` and `docs/audit/work/` are `frozen`, `docs/contracts/` is `generated`,
    `docs/specs/` and `docs/process/` are `living`, everything else is `unknown`. No header
    marker, front-matter field or content sniff is read — a heuristic that reads well and
    cannot be checked from the directory alone is exactly what this plan forbids adding.
    `unknown` is the honest answer for most of `.claude/`, and a large `unknown` count is
    itself a Stage 1 input, not a defect in this script.
  - `referenced_by` counts *tracked files whose content contains the target's basename*,
    excluding the target file itself (by full path, not by basename — two files that share
    a basename are not excluded from referencing each other). See `referenced_by()` below.
    This over-counts a common basename (`README.md` inside another file's content) and
    under-counts a file cited only by a fuzzy description; both are acceptable because the
    rule is written down here and in the companion document, not left implicit.

Usage:

    python3 scripts/file-census.py                       # CSV to stdout
    python3 scripts/file-census.py --out /tmp/c.csv       # CSV to a file
    python3 scripts/file-census.py --summary              # + per-area / per-name_pattern
                                                            #   counts on stderr
    python3 scripts/file-census.py --root /some/other/repo

Exit code is 1, with a message on stderr naming the cause, when `--root` is not a git
repository (or `git` cannot be invoked at all) — never an empty CSV. An empty census is
indistinguishable from a clean repository and would be committed as evidence of one.

Stdlib only: `subprocess` runs `git ls-files`; no dependency is added.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import pathlib
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Sequence
from typing import TextIO

CSV_HEADER = ["path", "area", "name_pattern", "size_bytes", "mutability", "referenced_by"]

_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_DIGITS = re.compile(r"\d+")

# Directory-prefix rules only (see module docstring) — order does not matter, the four
# prefix sets are disjoint.
_FROZEN_PREFIXES = ("docs/plans/", "docs/audit/work/")
_GENERATED_PREFIXES = ("docs/contracts/",)
_LIVING_PREFIXES = ("docs/specs/", "docs/process/")


class GitLsFilesError(RuntimeError):
    """`git ls-files` could not enumerate a repository's tracked files.

    Raised rather than allowing an empty result to fall through — an empty census is the
    failure mode that matters here (module docstring), because it is indistinguishable from
    a genuinely clean repository and would otherwise be committed as evidence.
    """


@dataclasses.dataclass(frozen=True, slots=True)
class Row:
    """One census row — field order matches `CSV_HEADER`."""

    path: str
    area: str
    name_pattern: str
    size_bytes: int
    mutability: str
    referenced_by: int

    def as_csv_row(self) -> list[str]:
        return [
            self.path,
            self.area,
            self.name_pattern,
            str(self.size_bytes),
            self.mutability,
            str(self.referenced_by),
        ]


def name_pattern(basename: str) -> str:
    """Normalise a basename: dates to `DATE`, then every remaining digit run to `N`.

    `"2026-08-29-w11-3-batch-scoring.md"` -> `"DATE-wN-N-batch-scoring.md"`
    `"0016-file-taxonomy.md"` -> `"N-file-taxonomy.md"`
    """
    without_dates = _DATE.sub("DATE", basename)
    return _DIGITS.sub("N", without_dates)


def referenced_by(path: str, texts: dict[str, str]) -> int:
    """Count entries of `texts` (tracked path -> file content) whose content contains
    `path`'s basename, excluding `path` itself (matched by full path, not by basename —
    a sibling file sharing the same basename is not excluded).
    """
    basename = pathlib.PurePosixPath(path).name
    return sum(1 for key, content in texts.items() if key != path and basename in content)


def area(rel_path: str) -> str:
    """First path segment. A root-level file's area is its own name."""
    return rel_path.split("/", 1)[0]


def mutability(rel_path: str) -> str:
    """Directory-prefix guess only — see module docstring. Never a content sniff."""
    if rel_path.startswith(_FROZEN_PREFIXES):
        return "frozen"
    if rel_path.startswith(_GENERATED_PREFIXES):
        return "generated"
    if rel_path.startswith(_LIVING_PREFIXES):
        return "living"
    return "unknown"


def git_ls_files(root: pathlib.Path) -> list[str]:
    """Tracked files under `root`, NUL-delimited via `git -C <root> ls-files -z`.

    Raises `GitLsFilesError` — naming the cause — rather than returning an empty list when
    `root` is not a git repository, or `git` cannot be invoked at all.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise GitLsFilesError(f"could not invoke git: {exc}") from exc
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise GitLsFilesError(
            f"`git -C {root} ls-files` exited {result.returncode}: {stderr or '(no stderr)'}"
        )
    decoded = result.stdout.decode("utf-8", errors="replace")
    return [p for p in decoded.split("\x00") if p]


def _read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        # A tracked path that no longer exists on disk (e.g. a broken symlink) contributes
        # no referencing content and no referenced_by hits — neither silently crashes nor
        # silently inflates the corpus.
        return ""


def build_census(root: pathlib.Path, tracked: Sequence[str]) -> list[Row]:
    """One `Row` per tracked path, in `tracked`'s order (git's own, already deterministic
    for a given commit — see module docstring on reproducibility)."""
    texts = {rel: _read_text(root / rel) for rel in tracked}
    rows = []
    for rel in tracked:
        p = root / rel
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        basename = pathlib.PurePosixPath(rel).name
        rows.append(
            Row(
                path=rel,
                area=area(rel),
                name_pattern=name_pattern(basename),
                size_bytes=size,
                mutability=mutability(rel),
                referenced_by=referenced_by(rel, texts),
            )
        )
    return rows


def write_csv(fh: TextIO, rows: Sequence[Row]) -> None:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(CSV_HEADER)
    for row in rows:
        writer.writerow(row.as_csv_row())


def print_summary(rows: Sequence[Row], file: TextIO) -> None:
    """Per-area and per-`name_pattern` counts. Diagnostic only — never consulted by
    `build_census` or `write_csv`, so `--summary` cannot change the CSV it accompanies."""
    area_counts = Counter(r.area for r in rows)
    pattern_counts = Counter(r.name_pattern for r in rows)
    print("-- per-area counts --", file=file)
    for a, n in sorted(area_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{n}\t{a}", file=file)
    print("-- per-name_pattern counts (top 40) --", file=file)
    for pat, n in sorted(pattern_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:40]:
        print(f"{n}\t{pat}", file=file)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help="repository root to census (default: current directory)",
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        default=None,
        help="write the CSV here; default is stdout",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="also print per-area and per-name_pattern counts to stderr",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    try:
        tracked = git_ls_files(root)
    except GitLsFilesError as exc:
        print(f"file-census: {exc}", file=sys.stderr)
        return 1

    rows = build_census(root, tracked)

    if args.out is not None:
        with args.out.open("w", encoding="utf-8", newline="") as fh:
            write_csv(fh, rows)
    else:
        write_csv(sys.stdout, rows)

    if args.summary:
        print_summary(rows, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
