#!/usr/bin/env python3
"""Does any file carry two front-matter blocks? — the double-stamp check for RFC-937's
migration (`scripts/doc-id.py migrate`).

**Why this exists as a committed instrument rather than a description.** The migration's
stamp writers *prepend*: `write_text(header + "\\n" + body)`. A file that already carries
front matter therefore ends up with a valid governed header on top and the original block
demoted into its body — and **three independent mechanisms read that as correct**:
`_docid.parse_header` parses the new leading block cleanly, its `.extra` is empty so
`audit-docs.py` check 30 has no unknown field to object to, and `doc-id.py`'s
`_front_matter_state` returns `"stamped"` so a second run skips the file as done. Every
instrument we would normally reach for is blind to it. Only reading the finished tree
distinguishes *completed* from *correct*.

**Read the tree, never the run's own bookkeeping.** A write trace cannot answer this: "no
path was written twice" is the claim in question, and a write the trace does not see —
`_write_redirects` uses `Path.open("w")`, not `write_text` — makes "none repeated" a
statement about the calls that were visible rather than about the files on disk. This
script takes a directory and reads it, so it works on a post-migration tree whether or not
anything ran it, and on a disposable clone as readily as on a checkout.

**Three nets, and only one of them is precise.** Reported separately and deliberately not
summed: they answer different questions and a combined figure would hide which.

* `second_block` — a front-matter block opening immediately after the first one closes.
  **This is the double-stamp signature.** Any non-zero result here is the defect.
* `harness_below` — a `name:`/`description:` line below the closing `---`. Broader, and it
  has a **known false-positive class**: a document *about* front matter quotes fields in
  its body. `.claude/skills/writing-skills/SKILL.md` is the worked example — it carries
  example front matter at lines 107-108 and 162-187 and is byte-identical before and after
  any migration, because nothing writes it. **Resolve a hit by comparing the file against
  its baseline, not by reading the hit.**
* `gt2_delims` — more than two `---` lines anywhere in the file. Very broad: `---` is
  markdown's thematic break. At the calibration tree 218 of these were all body rules;
  `docs/adrs/ADR-00007-*.md` has them at line indices 0 and 12 (its header) and 52 and 77,
  each blank-line-surrounded. **Useful only as a superset to sample, never as a count.**

**`--changed-since` was broken when this shipped, and the fix is worth reading before you
trust the flag.** It used `git diff --name-only` alone, which reports **tracked files only**,
so on a migrated tree the created drafts — the very files the stamp writers prepend to — were
invisible to it. With an injected double-stamp on one tree: whole-tree `second_block 1`,
exit 1; `--changed-since main` `second_block 0`, **exit 0**. It now also reads
`git status --porcelain --untracked-files=all`. **Prefer the whole-tree run regardless**: a
zero over the whole tree is the stronger statement, and it cannot be undercut by a scoping
bug in the filter.

`--changed-since <ref>` intersects every net with the files that actually changed, because
a file the run never wrote cannot have been double-stamped by the run. Without it the nets
range over the whole tree, which is the stronger statement when `second_block` is zero.

**Calibration, so a future run has a baseline rather than a bare number** — measured
2026-09-02 on a throwaway `git archive ac10d30` snapshot after `migrate()` ran to
completion with `scripts/doc-id.py` at `854b2a5` (PR #649):

    second_block          0        <- the signature; the only one that must be 0
    harness_below         0        (1 over the whole tree: writing-skills, false positive)
    gt2_delims          221 whole-tree; all thematic breaks
                        (an earlier line here read "218 of the written set, 221 whole-tree".
                        The 218 came from intersecting with a written set computed by a
                        separate write trace, NOT from `--changed-since`, which on an
                        uncommitted migrated tree yields 3. Two different notions of
                        "written set" were being named by one phrase; the whole-tree figure
                        is the one this script can actually reproduce.)
    vendored manifests    0 of 28 leading blocks changed
                          2 of 28 changed in the body only -- citation rewrites, which
                          RFC-937 §1.5 requires: only files *beneath* a vendored skill's
                          boundary are exempt, never the manifest itself

That last row is why this script compares the **leading block** and not the whole file. An
earlier version of `F88`'s acceptance clause demanded vendored manifests be byte-identical
and would have reported those two citation rewrites as violations: **stamping and citation
rewriting are different acts on the same file**, and an instrument that cannot tell them
apart raises a false alarm on correct behaviour.

Exit status is 1 if `second_block` is non-empty or any vendored leading block changed, 0
otherwise; the broad nets never fail the run on their own.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _load(name: str, path: Path) -> types.ModuleType:
    """`_docid.py` is loaded by path for the same reason `audit-docs.py` loads it that
    way: this directory's hyphenated filenames are not legal `import` targets, and the
    vendored-skill set must come from the declared constant rather than a filesystem
    probe (RL-990)."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ModuleNotFoundError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_docid = _load("_docid", REPO / "scripts" / "_docid.py")


def leading_block(text: str) -> str | None:
    """The file's opening `---`-delimited block verbatim, or `None` if it has none.

    Returns the block *including* both delimiters so two blocks that differ only in their
    fences still compare unequal.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return None
    return "\n".join(lines[: closing + 1])


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def scan_tree(root: Path, limit_to: set[str] | None = None) -> dict[str, list[str]]:
    """The three nets over `root`, each as a sorted list of repo-relative paths."""
    nets: dict[str, list[str]] = {"second_block": [], "harness_below": [], "gt2_delims": []}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if not path.is_file() or ".git" in rel.parts or "__pycache__" in rel.parts:
            continue
        key = rel.as_posix()
        if limit_to is not None and key not in limit_to:
            continue
        text = _read(path)
        if text is None:
            continue
        lines = text.splitlines()
        if not lines or lines[0] != "---":
            continue
        try:
            closing = lines.index("---", 1)
        except ValueError:
            continue
        if lines.count("---") > 2:
            nets["gt2_delims"].append(key)
        body = lines[closing + 1 :]
        if any(ln.startswith(("name:", "description:")) for ln in body):
            nets["harness_below"].append(key)
        for ln in body:
            if not ln.strip():
                continue
            if ln == "---":
                nets["second_block"].append(key)
            break
    return nets


def vendored_leading_blocks(root: Path, baseline: str) -> tuple[list[str], list[str], int]:
    """`(header_changed, body_only_changed, population)` for every vendored `SKILL.md`.

    `baseline` is a git ref read from this repository, so the comparison works when `root`
    is a disposable clone with no history of its own.
    """
    manifests = sorted(
        p
        for p in (root / ".claude" / "skills").glob("*/SKILL.md")
        if p.parent.name in _docid._VENDORED_SKILLS
    )
    header_changed: list[str] = []
    body_only: list[str] = []
    for path in manifests:
        rel = path.relative_to(root).as_posix()
        before = subprocess.run(
            ["git", "show", f"{baseline}:{rel}"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        if before.returncode != 0:
            continue
        after = _read(path)
        if after is None:
            continue
        if leading_block(before.stdout) != leading_block(after):
            header_changed.append(rel)
        elif before.stdout != after:
            body_only.append(rel)
    return header_changed, body_only, len(manifests)


def _changed_since(root: Path, ref: str) -> set[str]:
    """Every path that differs from `ref`, **including files git is not tracking**.

    The first version of this used `git diff --name-only <ref>` alone, and that was wrong in
    the one way that matters here: **`git diff` reports tracked files only.** On a migrated
    tree the newly created drafts are untracked, so they were invisible — and the created
    drafts are precisely where the stamp writers prepend, which is exactly where a
    double-stamp would be. Measured on the same tree with the same injected defect:
    whole-tree gave `second_block 1` and exit 1, while `--changed-since main` gave
    `second_block 0` and **exit 0**. The flag returned a clean signature on a tree carrying
    the defect, which is worse than having no flag.

    `git status --porcelain --untracked-files=all` is used instead because it reports both.
    The `??` entries are the ones `git diff` could not see.
    """
    diff = subprocess.run(
        ["git", "diff", "--name-only", ref],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if diff.returncode != 0:
        raise SystemExit(f"--changed-since {ref}: git diff failed in {root}")
    changed = {line for line in diff.stdout.splitlines() if line}

    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if status.returncode != 0:
        raise SystemExit(f"--changed-since {ref}: git status failed in {root}")
    for line in status.stdout.splitlines():
        if len(line) > 3:
            # Porcelain v1: two status columns, a space, then the path. A rename is
            # `R  old -> new`; the new path is the one on disk to scan.
            path = line[3:]
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            changed.add(path.strip('"'))
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tree", nargs="?", default=str(REPO), help="tree to scan")
    parser.add_argument(
        "--changed-since",
        metavar="REF",
        help="intersect every net with files changed since REF (in the scanned tree)",
    )
    parser.add_argument(
        "--baseline",
        metavar="REF",
        help="compare vendored manifests' leading blocks against REF (read from this repo)",
    )
    args = parser.parse_args(argv)

    root = Path(args.tree).resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    limit = _changed_since(root, args.changed_since) if args.changed_since else None
    nets = scan_tree(root, limit)

    scope = f"changed since {args.changed_since}" if limit is not None else "whole tree"
    print(f"double-stamp scan: {root}  ({scope})")
    print(f"  second_block   {len(nets['second_block']):>5}   <- the signature; must be 0")
    for rel in nets["second_block"]:
        print(f"      {rel}")
    print(
        f"  harness_below  {len(nets['harness_below']):>5}   "
        "broad; resolve each against its baseline"
    )
    for rel in nets["harness_below"][:20]:
        print(f"      {rel}")
    print(f"  gt2_delims     {len(nets['gt2_delims']):>5}   very broad; `---` is a thematic break")

    header_changed: list[str] = []
    if args.baseline:
        header_changed, body_only, population = vendored_leading_blocks(root, args.baseline)
        print(f"  vendored manifests ({population}) vs {args.baseline}:")
        print(f"      leading block changed (a stamp) {len(header_changed):>5}   must be 0")
        for rel in header_changed:
            print(f"          {rel}")
        print(f"      body only (citation rewrites)   {len(body_only):>5}   permitted by §1.5")
        for rel in body_only:
            print(f"          {rel}")
    else:
        print("  vendored manifests: not compared (pass --baseline REF)")

    return 1 if nets["second_block"] or header_changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
