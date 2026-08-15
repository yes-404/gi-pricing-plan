#!/usr/bin/env python3
"""Fetch the freMTPL2 dataset from OpenML (`07` FR-PLAT-37).

    uv run python examples/fremtpl2/fetch.py

The files are **not committed** — 36 MB of third-party data does not belong in a git
history, and re-fetching is cheap. They land in `examples/fremtpl2/data/`, which is
git-ignored.

Checksums are pinned. OpenML serves these from a mutable path, and a demo seed that
silently changed shape underneath the numbers in a closure record would be worse than one
that refuses to run.
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path
from typing import Final

DATA_DIR: Final = Path(__file__).parent / "data"

#: OpenML data ids 41214 (freq) and 41215 (sev), verified 2026-08-15.
SOURCES: Final = {
    "freMTPL2freq.arff": (
        "https://api.openml.org/data/v1/download/20649148/freMTPL2freq.arff",
        "a45363e056e2ea56408b38eeb9d4d04d7f6c6982eb7a14ed5e807c7c71807cdd",
    ),
    "freMTPL2sev.arff": (
        "https://api.openml.org/data/v1/download/20649149/freMTPL2sev.arff",
        "047632016b87e132247124f449a95d6d0e9f8ba05f2fe0947ef76ab8aaa10e0a",
    ),
}


def fetch(name: str, url: str, expected: str) -> Path:
    target = DATA_DIR / name
    if target.exists() and _digest(target) == expected:
        print(f"  {name:<20} already present and verified")
        return target

    print(f"  {name:<20} downloading…")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Written to a temporary name and moved only once the digest matches, so an
    # interrupted download cannot leave a truncated file that looks complete.
    staging = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(url, timeout=300) as response:
        staging.write_bytes(response.read())

    actual = _digest(staging)
    if actual != expected:
        staging.unlink()
        raise SystemExit(
            f"{name}: sha256 {actual}\n"
            f"{'':>{len(name) + 2}}expected {expected}\n"
            "The upstream file changed. Verify what changed before updating the pin — the "
            "numbers in the W7a seed record were measured against the pinned bytes."
        )
    staging.replace(target)
    print(f"  {name:<20} {target.stat().st_size / 1e6:.1f} MB, digest verified")
    return target


def _digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> int:
    print("freMTPL2 — French motor third-party liability, OpenML 41214 / 41215")
    for name, (url, expected) in SOURCES.items():
        fetch(name, url, expected)
    print(f"\n  in {DATA_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
