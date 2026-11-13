#!/usr/bin/env python3
"""freeze-check.py — fail a change that adds, modifies, deletes or renames a frozen record.

ADR-8449: the management record families are frozen. This reads the change's own diff
against its merge-base (`git diff <base>...HEAD`, the three-dot form), so only what this
branch changed is judged; what already sits on the base is never read. Standard library
only.

Usage: freeze-check.py [--base REF]   (default REF: origin/main)
Exit 0: nothing frozen is touched. Exit 1: prints `freeze-check: FAIL head=<sha> ...` and
each offending path. Exit 2: the diff could not be computed (a refusal, never a pass).
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from _frozen import is_frozen


def changed_paths(base: str, repo: str = ".") -> tuple[str, list[str]]:
    """Return (head sha, every path the change touches, both sides of a rename)."""
    def git(*args: str) -> str:
        cmd = ["git", "-C", repo, *args]
        return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout

    head = git("rev-parse", "--short=12", "HEAD").strip()
    out = git("diff", "--name-status", "-z", "--no-renames", f"{base}...HEAD")
    parts = [p for p in out.split("\0") if p]
    return head, parts[1::2]  # -z with --no-renames: status, path, status, path, ...


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args(argv)
    try:
        head, paths = changed_paths(args.base, args.repo)
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
