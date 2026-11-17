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
import subprocess
import sys
from pathlib import Path

from _frozen import is_frozen

if str(Path(__file__).resolve().parent) not in sys.path:  # _gitenv: any loader (#1913)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from _gitenv import clean_env

REPO = Path(__file__).resolve().parent.parent


def _git(repo: str, *args: str) -> str:
    cmd = ["git", "-C", repo, *args]
    return subprocess.run(cmd, check=True, capture_output=True, text=True, env=clean_env()
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
