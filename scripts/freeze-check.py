#!/usr/bin/env python3
"""freeze-check.py — fail a change that adds, modifies, deletes or renames a frozen record.

ADR-2136: the management record families are frozen. This reads the change's own diff
against its merge-base (`git diff <base>...HEAD`, the three-dot form), so only what this
branch changed is judged; what already sits on the base is never read. Standard library
only.

Usage: freeze-check.py [--base REF] [--repo PATH]   (default REF: origin/main; default PATH: the
checkout this script lives in, never the current directory). The first line printed, on
standard error, is `freeze-check: repo=<path> head=<sha>`.
Exit 0: nothing frozen is touched. Exit 1: prints `freeze-check: FAIL head=<sha> ...` and
each offending path. Exit 2: the diff could not be computed (a refusal, never a pass).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from _frozen import is_frozen

REPO = Path(__file__).resolve().parent.parent

# The GIT_* variables that point git at another repository, as a git hook exports them. `git -C`
# does not override them, so each git call below runs without them (#1900): the script reads the
# checkout it names, never one the caller's environment names. Named, not a GIT_ prefix match.
_GIT_REDIRECTS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_NAMESPACE",
)


def _git_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if k not in _GIT_REDIRECTS}


def _git(repo: str, *args: str) -> str:
    cmd = ["git", "-C", repo, *args]
    return subprocess.run(cmd, check=True, capture_output=True, text=True, env=_git_env()
    ).stdout


def head_of(repo: str = str(REPO)) -> str:
    return _git(repo, "rev-parse", "--short=12", "HEAD").strip()


def changed_paths(base: str, repo: str = str(REPO)) -> tuple[str, list[str]]:
    """Return (head sha, every path the change touches, both sides of a rename)."""
    head = head_of(repo)
    out = _git(repo, "diff", "--name-status", "-z", "--no-renames", f"{base}...HEAD")
    parts = [p for p in out.split("\0") if p]
    return head, parts[1::2]  # -z with --no-renames: status, path, status, path, ...


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--repo", default=str(REPO), help="default: the checkout this script lives in")
    args = ap.parse_args(argv)
    repo = str(Path(args.repo).resolve())
    try:
        print(f"freeze-check: repo={repo} head={head_of(repo)}", file=sys.stderr)
        head, paths = changed_paths(args.base, repo)
    except subprocess.CalledProcessError as exc:
        why = exc.stderr.strip()
        print(f"freeze-check: REFUSED, cannot diff {args.base}...HEAD: {why}", file=sys.stderr)
        return 2
    bad = sorted(p for p in paths if is_frozen(p))
    if bad:
        print(f"freeze-check: FAIL head={head} base={args.base}: {len(bad)} frozen path(s) changed")
        for p in bad:
            print(f"  {p}")
        return 1
    print(f"freeze-check: ok head={head} base={args.base}: {len(paths)} changed, none frozen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
