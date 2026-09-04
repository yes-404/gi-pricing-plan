#!/usr/bin/env python3
"""`doc-id.py migrate --verify` — NT-0019 §7 (a)-(i) as an instrument, not a table.

**Authority: Ruling 102 §1** (`docs/plans/2026-09-03-w37-6-ruling-102-verify-instrument.md`):

    `doc-id.py migrate --verify <snapshot>` — it
      - runs the migration on a disposable snapshot, never a real checkout;
      - computes all nine §7 (a)-(i) rows with their predicates, as one table;
      - exits 1 on any fail.

**Why a script and not a better table** (Ruling 102 §1, verbatim): *"A table's rows are
re-derived by hand each window, and each re-derivation is a fresh chance to substitute a
narrower predicate for the name of a wider one. A script's predicate is the thing that
runs."* `CLAUDE.md` §13's requirement that a count carry "the predicate it counted with" is
satisfied structurally here, because the predicate **is** the artifact: every row prints the
pattern it counted with, verbatim and runnable, or the shipped constant by symbol.

Four design constraints, each bought by a measured failure across three halted windows
(`docs/plans/2026-09-03-w37-6-second-fail-handover.md` §7):

1. **A check's name is not its predicate, and only the predicate is enforced.** Every row
   prints its predicate beside its number.
2. **Every row carries an un-migrated control from the same archive.** §7(d)'s `F-W[0-9]`
   alternative is the live example: its zero is the one that most needs a control, because a
   zero with no control cannot distinguish a clean corpus from a predicate that never
   matches. Row (g)'s 391 mangled citations were invisible until someone computed a control
   of 0.
3. **A green over an empty population is a fail, not a pass.** On a migrated tree
   `audit-docs.py` prints *"0 requirements defined across 8 specs"* as a **passing** line.
   Every row prints its denominator, and a zero denominator where the control has a non-zero
   one fails loudly (`docs/notes/0007-context-bound-measures-cap-not-discipline.md`).
4. **Field tests, never substring tests** (Ruling 102 §5). §7(d)'s `was:` exclusion is a
   parsed front-matter field, not a `"was:" in line` substring: two `was:`-keyed results have
   now needed re-deriving and both times a substring stood in for a field.

Ownership. Ruling 102 §1 says the instrument computes **nine** rows (a)-(i); Ruling 102 §3
rules that **(i) is W37-10's**, not W37-6's. Both are obeyed here: all nine are computed as
§1 requires, and every row carries an `owner` so the split is visible in the table rather
than argued about. The tension is reported, not resolved, by this module.

**Standard library only** (G4/DP-5), like `_docid.py` and `doc-id.py`; `subprocess` calls to
`git` are git plumbing.
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import _docid

# ---------------------------------------------------------------------------------------
# Verdicts
# ---------------------------------------------------------------------------------------

PASS: Final = "PASS"
FAIL: Final = "FAIL"
#: Non-fatal by ruling, not by convenience: `\bF[0-9]{2}\b` is excluded from §7(d)'s zero
#: requirement "with its count disclosed" (§8.5, re-affirmed by Ruling 102 §4). A DISCLOSE
#: row still prints its figure, its denominator and its control; it just does not set the
#: exit code.
DISCLOSE: Final = "DISCLOSE"
#: Fatal. The row's predicate ran, but §7's sentence admits two readings and the
#: decision-maker has not yet ruled which one the standard means (Ruling 102 §2, row 5:
#: "Each gets one reading, ruled by the decision-maker citing §7's sentence — not two").
#: Both readings are printed. An undetermined row is red, because Ruling 102 §2 says two
#: readings "is not an acceptable state for an acceptance row".
UNDETERMINED: Final = "UNDETERMINED"
#: Fatal. The row is defined and its population is known, but this instrument cannot
#: measure it in a snapshot; the reason and the owner are printed. §13 admits no silence, so
#: this is a verdict rather than an omission.
NOT_MEASURED: Final = "NOT MEASURED"
#: Fatal, and deliberately NOT the same word as FAIL. The migrated tree carries **more** of
#: what the row forbids than the un-migrated control does, which is not a bigger version of
#: "did not reach zero": it means the migration is *creating* the thing the row forbids, and
#: no amount of citation rewriting reaches it. Raised by the auditor against (d4)
#: `wf-0[0-9]` (control 267 -> migrated 327), whose floor is a legacy id baked into a
#: filename the migration generates.
REGRESSION: Final = "REGRESSION"

FATAL_VERDICTS: Final = frozenset({FAIL, UNDETERMINED, NOT_MEASURED, REGRESSION})

OWNER_W37_6: Final = "W37-6"
OWNER_W37_10: Final = "W37-10"


# ---------------------------------------------------------------------------------------
# The snapshot, and the refusal that keeps a real checkout out of `migrate()`
# ---------------------------------------------------------------------------------------


class WorkingCheckoutRefusedError(RuntimeError):
    """`--verify` was pointed at something that is, or lives inside, a real checkout.

    Ruling 102 §1's first clause — *"runs the migration on a disposable snapshot, never a
    real checkout"* — is enforced here as a guarded refusal rather than left to convention,
    because `migrate()` rewrites, moves and deletes ~1400 files in place and a working
    checkout has no undo for the untracked half of that.
    """


#: Written into the *work directory*, never into either tree, so that the trees stay
#: byte-identical to the archive they came from and the sentinel can never turn up in a
#: `git ls-files` population or a diff.
SENTINEL_NAME: Final = ".doc-id-verify-snapshot"

MIGRATED_DIR: Final = "migrated"
CONTROL_DIR: Final = "control"
BASELINE_DIR: Final = "baseline"

#: §7(f) names this tree by sha: *"`git grep -c 'VR-DST-1'` is unchanged from `8f5d57d`"*.
BASELINE_REF: Final = "8f5d57d"


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def _inside_git_work_tree(path: Path) -> Path | None:
    """The toplevel of the git *work tree* containing `path`, or None.

    Walks up to the first existing ancestor first: `git rev-parse` needs a directory that
    exists, and the point of the check is that a not-yet-created `--verify` target inside a
    checkout is refused just as firmly as an existing one.
    """
    probe = path
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    proc = subprocess.run(
        ["git", "-C", str(probe), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    top = proc.stdout.strip()
    return Path(top).resolve() if top else None


def assert_workdir_disposable(workdir: Path) -> None:
    """Refuse a `--verify` target that is, contains, or lives inside a real checkout.

    Three refusals, in the order a caller trips them:

    1. the target exists and is not an empty directory — it holds someone's files;
    2. the target is inside a git work tree — including the repository this instrument
       ships in, which is the exact mistake Ruling 102 §1's clause exists to prevent;
    3. the target is a file.

    A pre-existing *empty* directory is allowed: `mktemp -d` produces one, and CI's runner
    scratch space produces one.
    """
    resolved = workdir.expanduser().resolve()
    if resolved.exists() and not resolved.is_dir():
        raise WorkingCheckoutRefusedError(
            f"--verify target {resolved} is a file, not a directory"
        )
    if resolved.is_dir() and any(resolved.iterdir()):
        raise WorkingCheckoutRefusedError(
            f"--verify target {resolved} is a non-empty directory. This instrument runs "
            "the migration in place and would destroy it; point --verify at a new or "
            "empty path (Ruling 102 §1: 'a disposable snapshot, never a real checkout')."
        )
    top = _inside_git_work_tree(resolved)
    if top is not None:
        raise WorkingCheckoutRefusedError(
            f"--verify target {resolved} is inside the git work tree at {top}. "
            "`migrate()` rewrites, moves and deletes files in place; it is never run "
            "against a checkout (Ruling 102 §1)."
        )


def assert_tree_is_snapshot(tree: Path) -> None:
    """Belt-and-braces: refuse to hand `migrate()` anything but a tree this run built.

    Checked immediately before `migrate()`, so that a future caller reaching the migration
    step by some other route still cannot reach a real checkout. Three properties a
    snapshot has and a checkout does not: the sentinel sits beside it, its history is
    exactly one synthetic commit, and it has no remotes.
    """
    sentinel = tree.parent / SENTINEL_NAME
    if not sentinel.is_file():
        raise WorkingCheckoutRefusedError(
            f"{tree} carries no {SENTINEL_NAME} sentinel beside it — it was not built by "
            "this instrument, so it is not known to be disposable (Ruling 102 §1)."
        )
    count = _git(tree, "rev-list", "--count", "HEAD", check=False)
    if count.returncode != 0 or count.stdout.strip() != "1":
        raise WorkingCheckoutRefusedError(
            f"{tree} does not have exactly one commit of history "
            f"(got {count.stdout.strip() or 'no HEAD'}) — not a snapshot this instrument "
            "built (Ruling 102 §1)."
        )
    remotes = _git(tree, "remote", check=False)
    if remotes.stdout.strip():
        raise WorkingCheckoutRefusedError(
            f"{tree} has git remotes ({remotes.stdout.split()}) — a snapshot has none "
            "(Ruling 102 §1)."
        )


@dataclass(frozen=True)
class Snapshot:
    """The three trees every row is measured over.

    `migrated` and `control` are byte-identical extractions of the **same** archive; only
    `migrated` has had `migrate()` run over it. That is what makes the control a control:
    any difference between them is the migration's, and nothing else's.
    """

    workdir: Path
    ref: str
    ref_sha: str
    migrated: Path
    control: Path
    baseline: Path | None
    baseline_ref: str | None


def _materialise(docid: Any, ref: str, dest: Path, *, repo_root: Path) -> None:
    """Extract `ref` into `dest` and make it a one-commit git repository.

    `migrate()` calls `git ls-files` against the tree it is given (`doc-id.py`'s
    `git_ls_files`), so the snapshot has to be a repository, not a bare directory. Making
    it one also buys the diff row (g) reads: after `migrate()` runs, `git diff HEAD` in the
    snapshot **is** the migration diff, with no second definition of "what changed".
    """
    dest.mkdir(parents=True, exist_ok=True)
    docid.materialize_ref(ref, dest, repo_root=repo_root)
    _git(dest, "init", "-q", "-b", "snapshot")
    _git(dest, "-c", "user.email=verify@localhost", "-c", "user.name=doc-id verify",
         "add", "-A")
    _git(dest, "-c", "user.email=verify@localhost", "-c", "user.name=doc-id verify",
         "-c", "commit.gpgsign=false", "commit", "-q", "-m", f"snapshot of {ref}")


def build_snapshot(
    docid: Any,
    *,
    repo_root: Path,
    ref: str,
    workdir: Path,
    with_baseline: bool = True,
) -> Snapshot:
    """Build `migrated/`, `control/` and (for §7(f)) `baseline/` under `workdir`.

    `workdir` must already have passed `assert_workdir_disposable`.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    sha = _git(repo_root, "rev-parse", ref).stdout.strip()
    (workdir / SENTINEL_NAME).write_text(
        json.dumps(
            {
                "instrument": "doc-id.py migrate --verify",
                "authority": "Ruling 102 §1",
                "source_repo": str(repo_root),
                "ref": ref,
                "ref_sha": sha,
                "run": str(uuid.uuid4()),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    migrated = workdir / MIGRATED_DIR
    control = workdir / CONTROL_DIR
    _materialise(docid, ref, migrated, repo_root=repo_root)
    _materialise(docid, ref, control, repo_root=repo_root)
    baseline: Path | None = None
    baseline_ref: str | None = None
    if with_baseline and docid.ref_exists(BASELINE_REF, repo_root):
        baseline = workdir / BASELINE_DIR
        baseline_ref = _git(repo_root, "rev-parse", BASELINE_REF).stdout.strip()
        _materialise(docid, BASELINE_REF, baseline, repo_root=repo_root)
    return Snapshot(
        workdir=workdir,
        ref=ref,
        ref_sha=sha,
        migrated=migrated,
        control=control,
        baseline=baseline,
        baseline_ref=baseline_ref,
    )


# ---------------------------------------------------------------------------------------
# Reading a tree: the population every text predicate runs over
# ---------------------------------------------------------------------------------------

#: §7(d) says "over `git ls-files`". After `migrate()` the new files are untracked, so the
#: post-migration population is tracked *plus* untracked-not-ignored — the set a `git add
#: -A` would commit, which is the set the migration PR would actually ship. Using bare
#: `ls-files` here would measure the migration's output while silently excluding every file
#: it created, which is the narrower-predicate-behind-a-wider-name failure this whole
#: instrument exists to stop.
_LS_FILES_ARGS: Final = ("ls-files", "--cached", "--others", "--exclude-standard")

#: §7(d)'s own exclusion, verbatim: "excluding `REDIRECTS.csv`".
_D_EXCLUDED_BASENAME: Final = "REDIRECTS.csv"


def tracked_files(tree: Path) -> list[str]:
    out = _git(tree, *_LS_FILES_ARGS).stdout.splitlines()
    return sorted({rel for rel in out if rel})


def read_text(path: Path) -> str | None:
    """The file's text, or None when it is not UTF-8 text (an image, a lockfile blob)."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


# --- the `was:` field test (Ruling 102 §5) ----------------------------------------------

#: Reused from `_docid`, never restated: one definition of "a front-matter key line", so
#: the exclusion here and the parser that produces `Header.was` can never drift apart
#: (NT-0003 applied to code). `_docid._KEY_VALUE_RE` is `^([A-Za-z_][A-Za-z0-9_]*):[ \t]?(.*)$`.
_KEY_VALUE_RE: Final = _docid._KEY_VALUE_RE


def was_field_line_numbers(text: str) -> frozenset[int]:
    """0-based line numbers of the front-matter `was:` **field** in `text`.

    A field test, not a substring test. The line counts only when

    * the file opens with a `---` front-matter block that closes,
    * the line lies inside that block, and
    * the line parses as `key: value` with the key exactly `was`.

    A prose line reading ``the `was:` field`` is *not* excluded, and neither is a `was:`
    inside a fenced example further down the file. Ruling 102 §5 rules this ("keys on the
    parsed `was:` field, never a substring"), and the handover §2 table shows what the
    substring reading costs: it hid real hits on three of thirteen §7(d) alternatives
    (`NT-00` 32→35, `\\bF[0-9]{2}\\b` 1330→1340, `docs/audit/` 291→293).
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return frozenset()
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return frozenset()
    return frozenset(
        i
        for i in range(1, closing)
        if (m := _KEY_VALUE_RE.match(lines[i])) is not None and m.group(1) == "was"
    )


@dataclass(frozen=True)
class Corpus:
    """Every text file in a tree, already split into lines, with the `was:` lines marked.

    Built once per tree and shared by every row, so that fourteen predicates cannot
    disagree about what "the corpus" was — the disagreement that produced §7(d)'s two
    readings in the first place.
    """

    tree: Path
    files: tuple[str, ...]
    lines: Mapping[str, tuple[str, ...]]
    was_lines: Mapping[str, frozenset[int]]

    @property
    def n_files(self) -> int:
        return len(self.files)

    @property
    def n_lines(self) -> int:
        return sum(len(v) for v in self.lines.values())

    def scan(
        self, pattern: re.Pattern[str], *, skip_was: bool = True
    ) -> tuple[int, int]:
        """(matching lines, matching files) for `pattern` over this corpus."""
        n_lines = 0
        n_files = 0
        for rel in self.files:
            skip = self.was_lines[rel] if skip_was else frozenset()
            hits = sum(
                1
                for i, line in enumerate(self.lines[rel])
                if i not in skip and pattern.search(line)
            )
            if hits:
                n_lines += hits
                n_files += 1
        return n_lines, n_files


def load_corpus(tree: Path, *, exclude_basename: str | None = _D_EXCLUDED_BASENAME) -> Corpus:
    files: list[str] = []
    lines: dict[str, tuple[str, ...]] = {}
    was: dict[str, frozenset[int]] = {}
    for rel in tracked_files(tree):
        if exclude_basename is not None and rel.rsplit("/", 1)[-1] == exclude_basename:
            continue
        text = read_text(tree / rel)
        if text is None:
            continue
        files.append(rel)
        lines[rel] = tuple(text.splitlines())
        was[rel] = was_field_line_numbers(text)
    return Corpus(tree=tree, files=tuple(files), lines=lines, was_lines=was)


# ---------------------------------------------------------------------------------------
# The row
# ---------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Row:
    """One §7 acceptance row, as computed rather than as named.

    Every field is mandatory on purpose. `predicate` is what `CLAUDE.md` §13 asks a count to
    carry; `denominator` is what stops a green over an empty population; `control` is what
    tells a clean corpus apart from a predicate that never matches.
    """

    key: str
    title: str
    owner: str
    predicate: str
    denominator: str
    migrated: str
    control: str
    verdict: str
    note: str = ""
    #: Evidence printed beside the row, each `(label, predicate, figure)`, never gating.
    #: A companion answers the question the row's own predicate cannot: *what does this
    #: token turn INTO when the rewrite goes wrong, and is that form counted anywhere?*
    #: Directed by the lead after finding A1. Promotion of a companion to a gating row is
    #: the maintainer's under Ruling 102 §1 and is made by naming its label in
    #: `GATING_COMPANIONS` — a configuration change, never a rewrite.
    companions: tuple[tuple[str, str, str], ...] = ()

    @property
    def fatal(self) -> bool:
        return self.verdict in FATAL_VERDICTS


def _verdict_on_zero(figure: int, denominator: int, *, control: int) -> tuple[str, str]:
    """The three-way rule every counting row obeys.

    * denominator 0 → FAIL. A green over an empty population is a fail, not a pass.
    * control 0 → FAIL. The predicate never fired on the un-migrated tree either, so a
      zero on the migrated tree is not evidence of anything (§7(d) `F-W[0-9]`).
    * otherwise → PASS iff the figure is 0.
    """
    if denominator == 0:
        return FAIL, "empty population — a green over a zero denominator is a fail (NT-0007)"
    if control == 0:
        return (
            FAIL,
            "control is 0: this predicate never matched the un-migrated tree either, so "
            "the migrated figure distinguishes nothing",
        )
    return (PASS, "") if figure == 0 else (FAIL, "")


# ---------------------------------------------------------------------------------------
# (a) one family per file, zero `none`
# ---------------------------------------------------------------------------------------


def row_a(docid: Any, snap: Snapshot) -> Row:
    mig = docid.classify_docs_files(snap.migrated)
    ctl = docid.classify_docs_files(snap.control)
    mig_none = mig.get("none", 0)
    ctl_none = ctl.get("none", 0)
    mig_total = sum(mig.values())
    if mig_total == 0:
        verdict, note = FAIL, "empty population — no file under docs/ was classified"
    elif ctl_none == 0:
        verdict, note = (
            FAIL,
            "control has zero `none` too: the classifier cannot be shown to produce a "
            "`none`, so the migrated zero distinguishes nothing",
        )
    else:
        verdict, note = (PASS, "") if mig_none == 0 else (FAIL, "")
    families = ", ".join(f"{k} {mig[k]}" for k in sorted(mig))
    return Row(
        key="a",
        title="every tracked file under docs/ parses to exactly one family, zero `none`",
        owner=OWNER_W37_6,
        predicate=(
            "doc-id.py check --classify  "
            "(shipped constant by symbol: `doc-id.py:classify_docs_files`)"
        ),
        denominator=f"{mig_total} file(s) under docs/ classified",
        migrated=f"none={mig_none}; per family: {families}",
        control=f"none={ctl_none} of {sum(ctl.values())} classified",
        verdict=verdict,
        note=note,
    )


# ---------------------------------------------------------------------------------------
# (b) doc-id.py check: duplicates, contiguity, header id == filename
# ---------------------------------------------------------------------------------------

#: `doc-id.py:CheckFailure.kind`'s own three values, by symbol rather than pasted: the row
#: reports them separately because a single "77 failures" hides that one of its zeros is
#: real evidence and the other is not (handover §2, "Two clauses of (b) pass and one fails").
_CHECK_KINDS: Final = ("duplicate", "mismatch", "noncontiguous")


def _check_counts(docid: Any, tree: Path) -> dict[str, int]:
    counts = dict.fromkeys(_CHECK_KINDS, 0)
    for failure in docid.check(tree):
        counts[failure.kind] = counts.get(failure.kind, 0) + 1
    return counts


def row_b(docid: Any, snap: Snapshot) -> Row:
    mig = _check_counts(docid, snap.migrated)
    ctl = _check_counts(docid, snap.control)
    headers = len(docid.scan_governed_headers(snap.migrated).ids)
    total = sum(mig.values())
    if headers == 0:
        verdict, note = FAIL, "empty population — no governed header was scanned"
    else:
        verdict, note = (PASS, "") if total == 0 else (FAIL, "")
    return Row(
        key="b",
        title="doc-id.py check: zero duplicates, contiguous sequence, header id == filename",
        owner=OWNER_W37_6,
        predicate="doc-id.py check  (shipped constant by symbol: `doc-id.py:check`)",
        denominator=f"{headers} governed header(s) scanned",
        migrated="; ".join(f"{k}={mig[k]}" for k in _CHECK_KINDS),
        control="; ".join(f"{k}={ctl[k]}" for k in _CHECK_KINDS),
        verdict=verdict,
        note=note,
    )


# ---------------------------------------------------------------------------------------
# (c) doc-index.py --check byte-stable
# ---------------------------------------------------------------------------------------


def _run_script(tree: Path, script: str, *args: str) -> subprocess.CompletedProcess[str]:
    """Run **the snapshot's own copy** of `script`, never the invoking checkout's.

    DO NOT "simplify" this to call the checkout's script against `--root <snapshot>`. The
    migration rewrites `doc-index.py`, `doc-id.py` and `audit-docs.py` themselves, and §7's
    preamble scopes every row to "at the migration PR's merge tree" — the scripts are part
    of that tree. Measured by the auditor, same command, same snapshot, opposite verdicts:

        <snap>/scripts/doc-index.py --check   -> "INDEX.md is stale"      exit 1
        <checkout>/scripts/doc-index.py …     -> "OK (byte-stable)"       exit 0

    The cause is a citation rewritten inside `doc-index.py`'s own banner *string literal*
    (`see NT-0019 §1.4` -> its post-migration citation form) with the index never
    regenerated, so the generator and its artifact disagree by exactly the token rewritten
    in one and not the other. Running the checkout's copy makes row (c) pass forever over a
    broken corpus —
    the defect would be invisible to the instrument built to detect it.
    """
    resolved = (tree / "scripts" / script).resolve()
    if not resolved.is_relative_to(tree.resolve()):
        raise WorkingCheckoutRefusedError(
            f"{resolved} is not under the snapshot root {tree} — a row must never be "
            "computed with the invoking checkout's copy of a script the migration rewrites"
        )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(tree / "scripts")
    return subprocess.run(
        [sys.executable, str(tree / "scripts" / script), *args],
        cwd=tree,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


#: Row (c)'s pass is this string, not `returncode == 0`. Measured by the auditor: three
#: different states share exit 0 — a genuine byte-stable index, an un-migrated tree, and a
#: fully migrated tree checked with `--root` off by one directory, the last of which prints
#: the reassuring pre-migration line over an untouched corpus.
_BYTE_STABLE: Final = "OK (byte-stable)"
_NOTHING_TO_CHECK: Final = "nothing to check yet"


def _last_line(proc: subprocess.CompletedProcess[str]) -> str:
    text = (proc.stdout or proc.stderr).strip()
    return text.splitlines()[-1] if text else "(no output)"


def row_c(snap: Snapshot) -> Row:
    mig = _run_script(snap.migrated, "doc-index.py", "--check")
    ctl = _run_script(snap.control, "doc-index.py", "--check")
    index = snap.migrated / "docs" / "INDEX.md"
    records = 0
    if index.is_file():
        text = read_text(index) or ""
        records = sum(1 for line in text.splitlines() if _docid.ID_RE.search(line))
    if records == 0:
        verdict, note = (
            FAIL,
            "empty population — docs/INDEX.md carries no id line, so a byte-stable check "
            "over it proves nothing",
        )
    elif _BYTE_STABLE in (mig.stdout + mig.stderr):
        verdict, note = PASS, ""
    else:
        verdict, note = FAIL, (
            "no `OK (byte-stable)` line"
            + (" — and the run reported the pre-migration no-op, which is the state a "
               "mis-rooted call also reports" if _NOTHING_TO_CHECK in (mig.stdout + mig.stderr)
               else "")
        )
    return Row(
        key="c",
        title="doc-index.py --check byte-stable",
        owner=OWNER_W37_6,
        predicate=(
            "python3 <snapshot>/scripts/doc-index.py --check (cwd = the tree, the tree's "
            f"OWN copy — see `_docverify._run_script`); PASS asserts the literal "
            f"{_BYTE_STABLE!r} in the output, NOT the exit code: exit 0 is returned by the "
            "pass, by an un-migrated tree, and by a mis-rooted call alike"
        ),
        denominator=f"{records} id-bearing line(s) in docs/INDEX.md",
        migrated=f"exit {mig.returncode}: {_last_line(mig)}",
        control=f"exit {ctl.returncode}: {_last_line(ctl)}",
        verdict=verdict,
        note=note,
    )


# ---------------------------------------------------------------------------------------
# (d) the id/path grep, one row per alternative
# ---------------------------------------------------------------------------------------

#: §7(d)'s alternatives, one row per alternative (Ruling 102 §2 row 3, "(d) Per
#: alternative") — **read from `_docid.LEGACY_FORM_PATTERNS`, never retyped** (task 17,
#: Ruling 67 §2's "one shared constant"). `audit-docs.py`'s check 36 reads the identical
#: tuple; the two were, until this task, two independently-maintained copies that had
#: already diverged (this module's old `F-W[0-9]` matched a bare `F-W<n>` with no second
#: segment, a proper PREFIX of the real shape `F-W<n>-<n>`, and its `NT-00` matched the
#: bare prefix fragment Ruling 67 §2 Part 1 was ruled against by name). The tuple **is**
#: the decomposition — there is no separate combined-pattern string to parse and no
#: self-check against one, because there is nothing left for a splitting bug to get wrong.
#: Every entry is already anchored per Ruling 67 §2 Part 1: a `\b`-bounded COMPLETE legacy
#: identifier on both sides, or (for a path) a bare literal substring with no anchor at all
#: — a path has no "complete form" the way an id token does, so `\b` would only ever add
#: back the artificial restriction row (d13) used to read as INERT under.
#:
#: This deletes `D_FULL_PATTERN`, `PatternDecompositionError`, `_split_top_level`,
#: `_expand_trailing_alternation`, `_decompose` and `assert_decomposition_matches_source`
#: outright — including the self-referential "ADR-999, not a real ADR, because a real
#: number here would itself trip row (e)" concern a parallel PR (#712) fixed in the old
#: comment: there is no comment here quoting a padded-id-shaped example any more for row
#: (e) to trip on, so the concern the other fix addressed does not recur.
D_ALTERNATIVES: Final = _docid.LEGACY_FORM_PATTERNS

#: Excluded from §7(d)'s zero requirement **with its count disclosed** — §8.5, re-affirmed
#: by Ruling 102 §4 ("`\bF[0-9]{2}\b` remains excluded with its count disclosed; this ruling
#: reaches `Ruling [0-9]+` only") and, for the workstream finding-id form, by Ruling 105 §A:
#: the same alias class as `F<nn>` with a work prefix — its target is a register row, not a
#: document with an id yet, resolved by W37-11's alias resolver rather than this instrument.
#: Keyed by `_docid.LEGACY_FORM_PATTERNS`' own label, not by pattern text, so a Ruling 67
#: Part 1 anchoring fix to the pattern can never silently un-key a disclosure. Disclosed,
#: never silent: the row still prints its figure, denominator and control.
D_DISCLOSED: Final = frozenset({"finding id (bare form)", "finding id (workstream form)"})

#: Which ruling reads each disclosed alternative, printed in its row's own note so a reader
#: does not have to guess which citation covers which alternative.
D_DISCLOSED_CITATION: Final[Mapping[str, str]] = {
    "finding id (bare form)": "§8.5; Ruling 102 §4",
    "finding id (workstream form)": "§7(d); Ruling 105 §A — the same alias class as the "
                                     "bare finding id, resolved by W37-11's alias resolver",
}


#: What each §7(d) alternative turns INTO when the rewrite goes wrong. Directed by the lead
#: after auditor finding A1, whose evidence is the reason this table exists rather than a
#: comment: `F-W11-1-3` -> `F-WK-952-1-3`, because the rewrite matched the work key `W11`
#: *inside* the finding id. `F-WK` has a letter where `F-W[0-9]` wants a digit, so the
#: mangled form matches no §7(d) alternative at all — **and the alternative therefore reads
#: zero partly BECAUSE the corruption moved the tokens out of its own predicate's reach.**
#: A row satisfiable by corruption is what neither a control nor a denominator alone
#: catches.
#:
#: An alternative with no entry here prints `no companion predicate declared`, by name and
#: unconditionally. The gap is the point: the general question — *for every alternative,
#: what does a wrong rewrite turn this token into, and is that form counted anywhere?* — is
#: answered for three of thirteen today, and a silent absence would read as "asked and
#: found nothing".
#: Keyed by `_docid.LEGACY_FORM_PATTERNS`' own label (task 17) — a pattern-text key would
#: silently un-key itself the next time Ruling 67 §2 Part 1 changes an anchoring, as it
#: already had for `NT-00` -> `\bNT-\d{4}\b` and `F-W[0-9]` -> `\bF-W\d+-\d+\b` here.
D_COMPANIONS: Final[Mapping[str, tuple[tuple[str, str], ...]]] = {
    "finding id (workstream form)": ((
        "mangled: work key rewritten inside the finding id",
        r"\bF-WK-[0-9]",
    ),),
    "scoped requirement id": ((
        "mangled: rewrite matched inside a compound citation",
        r"\b(FR|NFR|OQ|DEP)-[0-9]+/[0-9]+",
    ),),
    # The migration derives new filenames from titles, lower-casing the slug, so a legacy
    # id inside a title survives as a *filename* the alternative cannot see: `NT-00` is
    # written upper-case and slugs are not. Auditor: 26 of 384 new-form filenames carry
    # `nt-00`, 2 carry `wf-0[0-9]`.
    "note id": (("mangled: legacy id lower-cased into a generated filename slug", r"nt-00"),),
    "workflow id": ((
        "mangled: legacy id baked into a generated filename slug",
        r"/[^/\s]*wf-0[0-9]",
    ),),
}

#: Companion labels promoted to gating. **Empty, and changing it is the maintainer's under
#: Ruling 102 §1** — the row set is not the instrument's to widen. Naming a label here makes
#: a non-zero companion figure fail its row; that is the whole promotion mechanism, and it
#: is a configuration change rather than a rewrite, as the lead directed.
GATING_COMPANIONS: Final[frozenset[str]] = frozenset()


#: A leading/trailing `\b` stripped from a Ruling-67-Part-1-anchored pattern's own source
#: text — a path-literal entry carries neither (task 17: a path has no "complete form" a
#: `\b` would express, so stripping is a no-op for those, and their "unanchored" companion
#: below reads identically to the anchored figure rather than manufacturing a fake gap).
def _unanchor(pattern_src: str) -> str:
    return pattern_src.removeprefix(r"\b").removesuffix(r"\b")


def _companions_for(
    label: str, pattern: re.Pattern[str], mig: Corpus, ctl: Corpus
) -> tuple[list[tuple[str, str, str]], int]:
    r"""Every companion figure for one alternative, plus the count that would gate it.

    Two kinds, and both are needed because they distinguish two inertness classes that look
    identical in a results table:

    * **mangled** — `D_COMPANIONS`, above: the row reads zero because the corruption moved
      the token out of the predicate's reach (auditor A1's workstream finding id).
    * **unanchored** — the same alternative with its own Ruling 67 Part 1 `\b`-anchoring
      stripped. A genuinely clean alternative reads the same figure either way; one that
      only reads zero because the anchor keeps it from firing at all reads a different,
      larger figure unanchored — Ruling 102 §1's own test, "a row that cannot be expressed
      as a predicate the script computes is a row that was never enforceable", applied to a
      row that computes but cannot fail.
    """
    out: list[tuple[str, str, str]] = []
    gating = 0
    for c_label, pattern_src in D_COMPANIONS.get(label, ()):
        c_pattern = re.compile(pattern_src)
        m_lines, m_files = mig.scan(c_pattern)
        c_lines, _ = ctl.scan(c_pattern)
        out.append((
            c_label,
            pattern_src,
            f"migrated {m_lines} line(s) / {m_files} file(s); control {c_lines}",
        ))
        if c_label in GATING_COMPANIONS:
            gating += m_lines
    if label not in D_COMPANIONS:
        out.append((
            "mangled",
            "(none)",
            "no companion predicate declared — this alternative has not been asked what a "
            "wrong rewrite turns it into",
        ))
    unanchored_src = _unanchor(pattern.pattern)
    unanchored = re.compile(unanchored_src)
    u_mig, _ = mig.scan(unanchored)
    u_ctl, _ = ctl.scan(unanchored)
    out.append((
        "unanchored (inertness probe)",
        f"{unanchored_src!r} — the same alternative with Ruling 67 Part 1's own `\\b` "
        "anchoring stripped",
        f"migrated {u_mig}; control {u_ctl}",
    ))
    return out, gating


#: Ruling 105 §A's third alias class (2026-09-04, `to-lead.md:459-465`): a slice key
#: `W<n>[a-z]?-<m>` names a historical execution unit no `SL-` id was ever minted for and
#: never will be — NT-0019 §5.2 asks for zero of the ~864 historical rows, and the
#: resolver that renders one (`W11-1` -> "WK-952, slice 1") is W37-11's citation-form
#: item, the same shape as the `F-W`/bare-`F` alias classes already in `D_DISCLOSED`. Kept
#: as a separate branch rather than folded into `D_DISCLOSED`, because two things on the
#: SAME row stay fatal regardless of the disclosure — a task key (three segments,
#: `W<n>-<m>-<k>`; NT-0019 names no live citation of this shape, expected 0 outside
#: fixtures) and a bare work-key remainder (`W<n>[a-z]?` with no slice number at all —
#: every Work mints a `WK-`, so an unmapped one is a real `token_map` defect) — and
#: "creation" (migrated > control on the whole alternative) stays REGRESSION even when the
#: disclosed branch would otherwise apply, which needs checking BEFORE the disclosure, not
#: after, unlike `D_DISCLOSED`'s other members.
_D8_LABEL: Final = "workstream/slice id"
_D8_TASK_KEY_RE: Final = re.compile(r"\bW[0-9]+[a-z]?-[0-9]+-[0-9]+\b")
_D8_WORK_KEY_BARE_RE: Final = re.compile(r"\bW[0-9]+[a-z]?\b(?!-[0-9])")
#: A genuine two-segment slice key — the negative lookahead is what stops this from also
#: matching the first two segments of a longer task key (`W11-1` inside `W11-1-2`).
_D8_SLICE_KEY_RE: Final = re.compile(r"\bW[0-9]+[a-z]?-[0-9]+\b(?!-[0-9])")


def _d8_verdict(mig: Corpus, ctl: Corpus, m_lines: int, c_lines: int) -> tuple[str, str]:
    """(d8)'s three-way split. `m_lines`/`c_lines` are the whole alternative's own figures
    (`\\bW[0-9]+[a-z]?-[0-9]+\\b`) — creation is checked first, against those, and stays
    REGRESSION regardless of what the slice/task/bare breakdown below would say.
    """
    if m_lines > c_lines:
        return REGRESSION, (
            f"the migrated tree carries MORE than the un-migrated control "
            f"({c_lines} -> {m_lines}): the migration is creating what this row forbids, "
            "so no citation rewrite reaches zero — creation stays REGRESSION even for a "
            "disclosed class (Ruling 105 §A's third alias class)"
        )
    m_task, task_files = mig.scan(_D8_TASK_KEY_RE)
    m_bare, bare_files = mig.scan(_D8_WORK_KEY_BARE_RE)
    if m_task or m_bare:
        parts = []
        if m_task:
            parts.append(
                f"{m_task} task key(s) in {task_files} file(s) "
                f"(`{_D8_TASK_KEY_RE.pattern}`, expected 0 outside fixtures)"
            )
        if m_bare:
            parts.append(
                f"{m_bare} bare work-key remainder(s) in {bare_files} file(s) "
                f"(`{_D8_WORK_KEY_BARE_RE.pattern}` — a token_map defect, not this alias "
                "class)"
            )
        return FAIL, "; ".join(parts)
    m_slice, slice_files = mig.scan(_D8_SLICE_KEY_RE)
    c_slice, _ = ctl.scan(_D8_SLICE_KEY_RE)
    return DISCLOSE, (
        "slice-key population disclosed, excluded from the zero requirement (Ruling 105 "
        f"§A's third alias class, `to-lead.md` 2026-09-04): {m_slice} line(s) / "
        f"{slice_files} file(s) (`{_D8_SLICE_KEY_RE.pattern}`), control {c_slice} line(s); "
        "owner W37-11's citation-form item — the resolver that renders one (e.g. "
        "'W11-1' -> 'WK-952, slice 1')"
    )


def rows_d(mig: Corpus, ctl: Corpus) -> list[Row]:
    rows: list[Row] = []
    for i, (label, pattern) in enumerate(D_ALTERNATIVES, start=1):
        m_lines, m_files = mig.scan(pattern)
        c_lines, c_files = ctl.scan(pattern)
        companions, gating = _companions_for(label, pattern, mig, ctl)
        if label == _D8_LABEL:
            verdict, note = _d8_verdict(mig, ctl, m_lines, c_lines)
        elif label in D_DISCLOSED:
            verdict = DISCLOSE
            note = (
                "excluded from the zero requirement, count disclosed "
                f"({D_DISCLOSED_CITATION.get(label, 'ruling pending')})"
            )
        elif m_lines > c_lines:
            # Not a worse FAIL — a different finding. See `REGRESSION`.
            verdict = REGRESSION
            note = (
                f"the migrated tree carries MORE than the un-migrated control "
                f"({c_lines} -> {m_lines}): the migration is creating what this row "
                "forbids, so no citation rewrite reaches zero"
            )
        else:
            verdict, note = _verdict_on_zero(m_lines, mig.n_lines, control=c_lines)
        if m_lines == c_lines and m_lines > 0:
            # The auditor's two-column signature, and a better detector than reasoning
            # about `\b`: an alternative the migration does not move has no discriminating
            # power, whatever its absolute figure looks like.
            note = (note + "; " if note else "") + (
                "INERT: control equals migrated, so this predicate distinguishes nothing "
                "— read its unanchored companion below"
            )
        if gating:
            verdict = FAIL
            note = (note + "; " if note else "") + (
                f"a companion promoted through GATING_COMPANIONS is non-zero ({gating})"
            )
        rows.append(
            Row(
                key=f"d{i}",
                companions=tuple(companions),
                title=f"§7(d) alternative {label!r} ({pattern.pattern!r}) returns nothing",
                owner=OWNER_W37_6,
                predicate=(
                    f"{pattern.pattern!r} over every line of `git ls-files --cached "
                    "--others --exclude-standard`, minus REDIRECTS.csv, minus "
                    "front-matter `was:` **field** lines "
                    "(`_docverify.was_field_line_numbers`); taken verbatim, by index, "
                    "from `_docid.LEGACY_FORM_PATTERNS` — Ruling 67 §2's one shared "
                    "constant, the same tuple `audit-docs.py` check 36 reads, anchored "
                    "per Ruling 67 §2 Part 1 (a `\\b`-bounded complete identifier, or a "
                    "bare literal path substring)"
                ),
                denominator=f"{mig.n_lines} line(s) in {mig.n_files} file(s)",
                migrated=f"{m_lines} line(s) / {m_files} file(s)",
                control=f"{c_lines} line(s) / {c_files} file(s)",
                verdict=verdict,
                note=note,
            )
        )
    return rows


# ---------------------------------------------------------------------------------------
# (e) no padded id in prose — Ruling 103's four conjuncts
# ---------------------------------------------------------------------------------------

#: **Conjunct 1**, and the `PAD_WIDTH` is read from the symbol, never written as a literal.
#: Ruling 103 defect 1: the same corpus gave 2032 under `-0\d{4}` and 2387 under
#: `-0[0-9]{3,4}` — **355 occurrences from the digit count alone**, F85's exact shape inside
#: an acceptance predicate. `CLAUDE.md` §13's "the shipped constant by symbol, never pasted"
#: is what stops it recurring.
_PADDED_ID_RE: Final = re.compile(
    r"\b(" + "|".join(_docid.FAMILY_PREFIXES) + r")-0\d{" + str(_docid.PAD_WIDTH - 1) + r"}\b"
)

#: **Conjunct 2's** stripping step. Ruling 103 defect 3: two of the three survivors were
#: paths — `docs/rulings/**RL-00993**-q5-….md` — whose **bold markers split the token**, so
#: the path test never saw a path. A predicate bug, not a ruling question.
_MD_EMPHASIS_RE: Final = re.compile(r"\*{1,3}")

#: **Conjunct 0's** fence tracking. Ruled by the decision-maker: without it, a record
#: documenting a padding defect must corrupt its own evidence to pass the lint, which is
#: the check-19 distortion arriving by a new route. Fencing preserves evidence byte-exact
#: and keys no exemption to any document — a padded id **outside** a fence is a violation in
#: every document, the ruling's own included.
_FENCE_RE: Final = re.compile(r"^\s{0,3}(```|~~~)")

_TOKEN_BOUNDARY_RE: Final = re.compile(r"[\s`()\[\]{}<>\"',;]")

#: **Conjunct 2's** line-locator strip. Row (e)'s own measurement found a fourth defect
#: alongside Ruling 103's three: a same-directory `filename.md:123` or `filename.md:401-404`
#: citation (this corpus's own convention for "the peer file, no leading `docs/plans/`,
#: because both live in the same directory") is a filename token per rule 3's own wording —
#: "the leading component of a filename ending `.md`" — but the trailing `:<line>` defeats
#: the bare `\.[A-Za-z0-9]{2,4}$` extension test, which requires the token to *end* at the
#: extension. Stripped before that test only; the `/` test is unaffected either way.
_TRAILING_LINE_LOCATOR_RE: Final = re.compile(r":\d+(-\d+)?$")


def _in_path_context(line: str, start: int, end: int) -> bool:
    """True when the occurrence at `line[start:end]` sits inside a path-shaped token.

    Path-shaped means the enclosing token contains a `/` or ends in a file extension (once a
    trailing `:<line>` or `:<start>-<end>` locator is stripped). A padded id inside a
    filename is not "in prose"; a padded id in a sentence is. Defined on the whole enclosing
    token rather than by a lookbehind on one character, which was the first attempt and
    missed `[PL-01240-slug](docs/plans/PL-01240-slug.md)`.
    """
    left = start
    while left > 0 and not _TOKEN_BOUNDARY_RE.match(line[left - 1]):
        left -= 1
    right = end
    while right < len(line) and not _TOKEN_BOUNDARY_RE.match(line[right]):
        right += 1
    token = line[left:right]
    sans_locator = _TRAILING_LINE_LOCATOR_RE.sub("", token)
    return "/" in token or bool(re.search(r"\.[A-Za-z0-9]{2,4}$", sans_locator))


def _unpadded(token: str) -> str:
    """`PL-01240` -> `PL-1240`. Conjunct 3 resolves the *unpadded* form in `docs/INDEX.md`,
    because that is the form the index carries and the form a citation is supposed to use.
    """
    m = re.fullmatch(r"([A-Z]+)-0*([0-9]+)", token)
    return f"{m.group(1)}-{int(m.group(2))}" if m else token


def index_ids(tree: Path) -> frozenset[str]:
    """Every governed id `docs/INDEX.md` carries, unpadded — **conjunct 3's** authority.

    A token that resolves to nothing is a *specimen of the form*, not a citation, and the
    decision-maker ruled it out of the violation population on exactly that ground.
    """
    text = read_text(tree / "docs" / "INDEX.md") or ""
    return frozenset(
        f"{m.group(1)}-{int(m.group(2))}"
        for m in re.finditer(r"\b([A-Z]+)-0*([0-9]+)\b", text)
        if m.group(1) in _docid.FAMILY_PREFIXES
    )


@dataclass(frozen=True)
class PaddedHit:
    rel: str
    line_no: int
    token: str
    line: str


def padded_hits(corpus: Corpus, resolvable: frozenset[str]) -> tuple[
    int, list[PaddedHit], list[PaddedHit], list[PaddedHit]
]:
    """(conjunct 1 total, after conjunct 0, after conjunct 2, after conjunct 3).

    Each stage is returned so the row can print where the population fell away, rather than
    a single number whose filtering nobody can see.
    """
    total = 0
    after_corpus: list[PaddedHit] = []
    for rel in corpus.files:
        in_fence = False
        skip = corpus.was_lines[rel]
        for i, line in enumerate(corpus.lines[rel]):
            if _FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            hits = list(_PADDED_ID_RE.finditer(line))
            total += len(hits)
            if in_fence or i in skip:
                continue
            for h in hits:
                after_corpus.append(PaddedHit(rel, i + 1, h.group(0), line.strip()))
    after_path: list[PaddedHit] = []
    for hit in after_corpus:
        # Conjunct 2 is tested on the line with markdown emphasis stripped, so a bold
        # marker inside a path cannot hide the path from the path test.
        cleaned = _MD_EMPHASIS_RE.sub("", hit.line)
        prose = True
        for m in _PADDED_ID_RE.finditer(cleaned):
            if m.group(0) == hit.token and _in_path_context(cleaned, m.start(), m.end()):
                prose = False
                break
        if prose:
            after_path.append(hit)
    after_index = [h for h in after_path if _unpadded(h.token) in resolvable]
    return total, after_corpus, after_path, after_index


def row_e(mig: Corpus, ctl: Corpus, snap: Snapshot) -> Row:
    resolvable = index_ids(snap.migrated)
    ctl_resolvable = index_ids(snap.control)
    m_total, m_corpus, m_path, m_index = padded_hits(mig, resolvable)
    c_total, _c_corpus, _c_path, c_index = padded_hits(ctl, ctl_resolvable)
    if mig.n_lines == 0:
        verdict, note = FAIL, "empty population"
    elif not resolvable:
        verdict, note = (
            FAIL,
            "conjunct 3 has no authority — docs/INDEX.md resolves no governed id, so "
            "every token would be excused as a specimen (NT-0007)",
        )
    elif m_index:
        verdict = FAIL
        note = "violations: " + "; ".join(
            f"{h.rel}:{h.line_no} [{h.token}]" for h in m_index[:6]
        ) + ("" if len(m_index) <= 6 else f" (+{len(m_index) - 6} more)")
    else:
        verdict, note = PASS, ""
    return Row(
        key="e",
        title="no padded id in prose (Ruling 103's four conjuncts)",
        owner=OWNER_W37_6,
        predicate=(
            "conjunct 0 — (d)'s corpus, minus REDIRECTS.csv, minus front-matter `was:` "
            f"field lines, minus fenced code blocks ({_FENCE_RE.pattern!r}); "
            f"conjunct 1 — {_PADDED_ID_RE.pattern!r}, whose digit count is "
            "`_docid.PAD_WIDTH` **by symbol**, never a literal; "
            f"conjunct 2 — not path-shaped (`_docverify._in_path_context`) after stripping "
            f"markdown emphasis ({_MD_EMPHASIS_RE.pattern!r}); "
            "conjunct 3 — the token's UNPADDED form resolves in the generated "
            "docs/INDEX.md (`_docverify.index_ids`)"
        ),
        denominator=(
            f"{m_total} padded token(s) by conjunct 1; {len(m_corpus)} survive conjunct 0; "
            f"{len(m_path)} survive conjunct 2; {len(resolvable)} governed id(s) in "
            "docs/INDEX.md give conjunct 3 its authority"
        ),
        migrated=f"{len(m_index)} violation(s) in {len({h.rel for h in m_index})} file(s)",
        control=(
            f"{c_total} padded token(s) by conjunct 1; {len(c_index)} violation(s) "
            "un-migrated"
            + (
                " — but conjunct 3 has NO AUTHORITY on the un-migrated tree "
                "(docs/INDEX.md is generated by the migration and carries no id yet), so "
                "this zero is structural and CANNOT corroborate a green"
                if not ctl_resolvable
                else ""
            )
        ),
        verdict=verdict,
        note=note,
    )


# ---------------------------------------------------------------------------------------
# (f) VR-DST-1 unchanged — Ruling 103's two conjuncts
# ---------------------------------------------------------------------------------------

#: §7(f) verbatim: "`git grep -c 'VR-DST-1'` is unchanged from `8f5d57d` — no product
#: identifier moved". Ruling 103 rules the comparison is a before/after pair on the SAME
#: archive, not a comparison to `8f5d57d`; the baseline tree is still measured and printed,
#: because §7's own sentence names that sha and a reader will look for it.
_VR_DST_RE: Final = re.compile(r"VR-DST-1\b")


def _per_file(corpus: Corpus, pattern: re.Pattern[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for rel in corpus.files:
        n = sum(1 for line in corpus.lines[rel] if pattern.search(line))
        if n:
            out[rel] = n
    return out


def row_f(
    mig: Corpus,
    ctl: Corpus,
    baseline: Corpus | None,
    snap: Snapshot,
    generated_paths: Sequence[str] = (),
) -> Row:
    # Ruling 105 D3 / #18 §1: excludes every file the migration generated in full, keyed
    # on the run's own generated-output list (`MigrateResult.generated_paths` —
    # `docs/INDEX.md`, `docs/REDIRECTS.csv`, the family READMEs, the split-source indexes),
    # never on the literal path `docs/INDEX.md`. Ruling 104 §2: class 6 is the property
    # (a file whose entire content is the output of one of the migration's generators, by
    # reproducibility — not by whether it happens to carry forward original prose), not the
    # list; `_MIGRATION_DIFF_FAMILY_READMES` is ratified as a member, in-place READMEs
    # included. Excluded from `m_per` once, before either conjunct runs, so conjunct 2's
    # own mechanism (per file through the routing table) is unchanged — only its input is.
    generated = frozenset(generated_paths)
    m_per_all = _per_file(mig, _VR_DST_RE)
    excluded = {k: v for k, v in m_per_all.items() if k in generated}
    m_per = {k: v for k, v in m_per_all.items() if k not in generated}
    c_per = _per_file(ctl, _VR_DST_RE)
    m_lines, c_lines = sum(m_per.values()), sum(c_per.values())

    redirect = _redirect_map(snap.migrated)
    mapped = {redirect.get(k, k): v for k, v in c_per.items()}
    disagreements = [
        (path, mapped.get(path, 0), m_per.get(path, 0))
        for path in sorted(set(mapped) | set(m_per))
        if mapped.get(path, 0) != m_per.get(path, 0)
    ]
    residual = sum(after - before for _p, before, after in disagreements)

    if mig.n_files == 0:
        verdict, note = FAIL, "empty population"
    elif c_lines == 0:
        verdict, note = FAIL, "control carries no product identifier — the predicate is dead"
    elif m_lines != c_lines:
        verdict, note = FAIL, f"conjunct 1: total moved {c_lines} -> {m_lines}"
    elif residual != 0:
        verdict = FAIL
        note = (
            f"conjunct 2: {len(disagreements)} per-file disagreement(s) that do NOT close "
            f"(residual {residual:+d}) — an identifier left one file without arriving in "
            "another"
        )
    elif disagreements:
        verdict = PASS
        note = (
            f"conjunct 2 passes with {len(disagreements)} disclosed split-source "
            "disagreement(s), summing to zero: "
            + "; ".join(f"{b}->{a} {p}" for p, b, a in disagreements[:4])
            + ". Ruling 103 rules conjunct 2 sums over ALL targets a source routes to, from "
            "§3.3's routing table. That table is not an artifact in the tree, so this is a "
            "table-free approximation: it treats a set of disagreements that nets to zero "
            "as one split source's content arriving in several files. NAMED LIMITATION — it "
            "would not catch a genuine move that happens to net to zero across two files. "
            "Replace with the routing table when §3.3 ships one."
        )
    else:
        verdict, note = PASS, ""

    if excluded:
        note = "; ".join(
            part for part in (
                note,
                "GENERATED, excluded (Ruling 105 D3/#18, Ruling 104 §2's class-6 "
                f"property): {sum(excluded.values())} occurrence(s) in "
                f"{len(excluded)} generated file(s) — "
                + ", ".join(f"{p}={n}" for p, n in sorted(excluded.items())[:6])
                + (f" (+{len(excluded) - 6} more)" if len(excluded) > 6 else ""),
            )
            if part
        )

    if baseline is None:
        b_desc = f"{BASELINE_REF} not resolvable in this clone"
    else:
        b_lines, b_files = baseline.scan(_VR_DST_RE, skip_was=False)
        b_desc = f"{b_lines} line(s) / {b_files} file(s) at {BASELINE_REF}"
    return Row(
        key="f",
        title="git grep -c 'VR-DST-1' unchanged (Ruling 103's two conjuncts)",
        owner=OWNER_W37_6,
        predicate=(
            f"{_VR_DST_RE.pattern!r} over (d)'s corpus, `was:` lines INCLUDED (a product "
            "identifier is not a citation); conjunct 1 — the summed total is equal before "
            "and after the migration on the same archive; conjunct 2 — per-file counts are "
            "equal, each pre-migration path mapped through the run's own docs/REDIRECTS.csv "
            "(`_docverify._redirect_map`), summing over a split source's targets; every "
            "path in `MigrateResult.generated_paths` is excluded first (Ruling 105 D3/#18)"
        ),
        denominator=(
            f"{len(c_per)} file(s) carry the identifier before, {len(m_per)} after "
            f"({len(excluded)} generated file(s) excluded); "
            f"{len(redirect)} redirect row(s) available to map them"
        ),
        migrated=(
            f"conjunct 1: {m_lines} line(s) / {len(m_per)} file(s); "
            f"conjunct 2: {len(disagreements)} disagreement(s), residual {residual:+d}"
        ),
        control=(
            f"conjunct 1: {c_lines} line(s) / {len(c_per)} file(s); "
            f"§7's named baseline: {b_desc}"
        ),
        verdict=verdict,
        note=note,
    )


# ---------------------------------------------------------------------------------------
# (g) the migration diff, filtered to hunks that are neither header nor citation-token
# ---------------------------------------------------------------------------------------

#: Ruling 102 §2 row 1 names this **the** broken-input proof for (g): "a rewrite may not
#: match inside a longer identifier. `NFR-RATE-13/14` is the broken-input proof". A compound
#: citation names two requirements in shorthand; a rewrite that matches inside the longer
#: identifier turns it into `NFR-775/14` — one real requirement and one meaningless
#: fragment. The post-migration form has a *numeric* module segment, which is what
#: distinguishes a mangled citation from a legitimate compound one.
MANGLED_CITATION_RE: Final = re.compile(r"\b(FR|NFR|OQ|DEP)-[0-9]+/[0-9]+")

#: The pre-migration compound form: the population at risk. Printed as this row's
#: denominator, so "391 mangled" is read against "423 at risk" rather than against nothing.
COMPOUND_CITATION_RE: Final = re.compile(r"\b(FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+/[0-9]+")

#: The line-level mask filter that stood in for (g) before Ruling 68 defined the six
#: classes has been **removed**, not left beside its replacement — keeping a superseded
#: predicate next to the one that supersedes it is NT-0003's duplicated-status defect in
#: code form. It implemented exactly one of the six classes (class 2, a reference token
#: substituted from the step-6 allow-list) and scored every other permitted class
#: `unexplained`. Ruling 68 §3: "one definition of 'reference tokens only', not two ...
#: implementing it twice is how the two drift apart." The replacement,
#: `doc-id.classify_migration_diff`, is that one definition — file-granularity, all six
#: classes, sharing `audit-docs.py`'s DP-7 predicate rather than a home-grown line mask.

# ---------------------------------------------------------------------------------------
# W37-6 channel `:512-536` — Ruling 102 §3's "name them", applied to `classified-by-none`
# itself: the deputy's ruling on the class-6 keying fix refused a bare total ("the ~504
# acted on as a total rather than per cause" is a named violation) and required the
# residue printed *by cause*, with counts and three examples each. Investigative, never
# authoritative — cause 1 (DP-7's unconditional frontmatter strip) and cause 2a (range
# citations, `X-<mod>-a..b`) are the deputy's own diagnoses, owned by fresh executors
# elsewhere; this only *reports* the shape each residue member matches, on the same
# un-migrated corpus (`ctl`) every other row already shares, never a second read of the
# tree. A member matching none of the named shapes lands in `other`, which is not a
# failure of this classifier — Ruling 102 §3 obliges naming what is understood, not
# claiming to understand all of it.
# ---------------------------------------------------------------------------------------

#: Cause 1 (deputy's ruling `:522`): `.claude/skills/**`, `.claude/agents/` and
#: `.claude/roles/` carry their own, non-NT-0019 front matter (agent/skill config) that
#: the migration defers rather than stamps — DP-7 strips the leading `---…---` block of
#: `new_text` unconditionally and compares against the *raw* old text, so a clean token
#: rewrite in one of these files loses the foreign block on one side of the comparison
#: only. Detected on the pre-migration line, never the post-migration one — the block DP-7
#: wrongly strips is the one that was always there.
_FOREIGN_FRONTMATTER_DIRS: Final = (".claude/skills/", ".claude/agents/", ".claude/roles/")

#: Cause 2a (deputy's ruling `:526`): a legacy range citation (`FR-PLAT-1..4`) names a
#: consecutive block of ids, not a single one; the migration's ids are not consecutive, so
#: the rewrite must enumerate the range rather than substitute one token, which DP-7's
#: flat inverse cannot undo. Read on the pre-migration line — the range notation the
#: rewrite had to expand away.
_RANGE_CITATION_RE: Final = re.compile(r"\b(FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+\.\.[0-9]+")

#: Cause 2b (deputy's ruling `:528-530`, this executor's to investigate): every
#: `NNNN-*.md` file left behind, under `_NOTES_TOMBSTONE_DIR` below, by Ruling 57's own
#: historical move is a one-line "This note moved to `[...]`(../../...)" self-reference, a
#: *relative* markdown link to the note's own current location. `_repoint_relative_links`
#: rewrites it correctly in the forward direction (the diff shows the new path and its new
#: citation tokens, both right) — verified on 18 of these files' full diffs matching this
#: exact one-line shape, no exceptions found. DP-7's inverse cannot undo it:
#: `redirects_inverse` only carries the flat, `docs/`-rooted and bare-basename token forms
#: `_path_rewrite_tokens` produces, never a `../../`-relative one, so the single line that
#: differs has no entry to invert through. The same mechanism Ruling 100/101 already named
#: for a split target's own relative links ("the (g) inverse only knows id tokens, so the
#: path-shaped rewrite has no inverse") — reported here rather than assumed to be that
#: same, already-ruled class, since these are not split targets and the deputy's own
#: instruction was to report the shape, not to classify it.
#:
#: Built by concatenation, not a literal path: `tests/test_notes_move_citations.py`'s own
#: `test_no_living_file_cites_the_old_notes_path` flags any *other* tracked file that
#: spells this vacated root out as one contiguous string (that check's own module
#: docstring has the reasoning); this module cites the directory by regex, not by prose
#: naming it, for the identical reason.
_NOTES_TOMBSTONE_DIR: Final = ".claude" + "/" + "notes"
_NOTES_STUB_RE: Final = re.compile(
    r"^" + re.escape(_NOTES_TOMBSTONE_DIR) + r"/\d{4}-.*\.md$"
)

#: Not one of the deputy's three named causes — found investigating cause 2b, reported
#: because Ruling 102 §3 obliges naming what is understood rather than folding it into
#: `other`. A citation naming three or more legacy ids in one slash-chain
#: (`FR-RATE-56/57/58`) rewrites each component correctly (verified: every number present
#: substitutes to its own new id) but the compound-redirect mechanism the deputy's own
#: `:318` ruling describes for a *two*-id slash compound (`NFR-RATE-13/14` ->
#: `NFR-775/776`, one `REDIRECTS.csv` row) does not obviously extend to a chain, and DP-7's
#: inverse fails the whole file over it. Not investigated further — out of this
#: executor's assigned scope (2b only); reported by shape for the deputy's triage.
_SLASH_COMPOUND_RE: Final = re.compile(r"\b(FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+(?:/[0-9]+){1,}")

# ---------------------------------------------------------------------------------------
# `docs/` triage (W37-6 channel `:666`, `:770`, the #715 residue table's own `other` row):
# the deputy's two hypotheses for `docs/`'s 249-file `other` bucket ("dominated by the
# split-source and generated-README classes the new class 6 no longer absorbs") were
# checked against ten `docs/`-tree residue members, each read via
# `audit_docs.frozen_file_matches_after_migration_stamp` run by hand against the exact
# `redirects_inverse` map `classify_migration_diff` builds, never assumed from the diff
# alone. **Both named hypotheses are KILLED for `docs/`**: none of the ten sampled files is
# a Ruling 68 class-4 split or a generated README/INDEX collision. Two new, unrelated
# causes accounted for eight of the ten; the other two (a bare-basename/non-`docs/`-rooted
# relative citation, e.g. `docs/README.md`'s `workflows/wf-01-...md` and
# `phase-0-status.md`; and one *un-allocated placeholder id* cited in a plan's own prose —
# `docs/plans/2026-08-19-psi-comparison-selector[-ledger].md` both cite `OQ-DATA-11` as an
# id the plan instructs a *future* reader to raise, never itself a `REDIRECTS.csv` row, so
# `redirects_inverse` has no entry for its new form `OQ-8471`) are reported here in prose,
# not as a regex: the first has no single stable prefix to key on (unlike the five
# `docs/`-rooted forms `_docid.LEGACY_FORM_PATTERNS` already names), and the second needs
# `REDIRECTS.csv` itself (built in `new_root`, not `ctl`) to tell a placeholder from a real
# citation — outside what this row's "no second tree read" rule allows a cheap classifier.
# ---------------------------------------------------------------------------------------

#: cause3 (this executor's `docs/` sample, six of ten files): a prose citation to
#: *another* document by its pre-migration relative path — `docs/notes/0010-...md`,
#: `docs/audit/register.md`, `docs/plans/2026-08-30-...md` — inside a file that is not
#: itself one of `_NOTES_STUB_RE`'s tombstones. The forward sweep resolves these correctly
#: (`_path_rewrite_tokens`/the citation sweep knows the move); DP-7's inverse does not,
#: because `redirects_inverse` (`doc-id.classify_migration_diff`) is built only from
#: `REDIRECTS.csv`'s `old_id`/`new_id` **id** columns, never from a citation's own literal
#: path string. Reuses `_docid.LEGACY_FORM_PATTERNS`' five already-named `"...path"`
#: entries (Ruling 67 §2's one shared constant) rather than a new pattern — Verified
#: against all six: `docs/audit/findings/F27.md`, `docs/notes/0003-duplicated-status-goes-
#: stale.md`, `docs/process/delivery-process.md`, `docs/process/delivery-process.core.json`
#: and `docs/research/w11-task-1-4-model-call-concurrency.md` each match on at least one
#: line; `docs/README.md` does not (see the module comment above) and is left in `other`.
_LEGACY_PATH_RES: Final = tuple(
    pattern for name, pattern in _docid.LEGACY_FORM_PATTERNS if "path" in name
)

#: cause4 (this executor's `docs/` sample, one of ten files, `docs/contracts/schemas/
#: job.schema.json`): a genuine **forward**-migration corruption, not merely an inverse
#: gap — `"W3C/OpenTelemetry trace id..."` came out `"WK-944C/OpenTelemetry trace id..."`.
#: `doc-id.py`'s `_compound_token_re` (the compound-citation expansion regex, task 4 item
#: 3) is `\b{tok}((?:[-/]\d+)*)` with **no trailing `\b`**, unlike its sibling
#: `_whole_token_re`'s `\b{tok}\b(?![-/][0-9])` — so a legacy work token (`W3`) matches as
#: a bare *prefix* of any longer run of word characters that happens to start the same way
#: and is not itself `[-/]` plus a digit. `W3C` has no separator before its `C`, so
#: `_whole_token_re`-style matching (which needs a word-boundary on both sides) would not
#: touch it, but `_compound_token_re` does. `MANGLED_CITATION_RE` (this row's own g1
#: probe) cannot see it either — its pattern is scoped to `(FR|NFR|OQ|DEP)-\d+/\d+`, not
#: the `W`/`WK` family. Detected here on the *pre*-migration line: an uppercase letter can
#: never legitimately continue a work id (`_WORK_FAMILY_TOKEN_RE`'s own suffix group is
#: `[a-z]?`, lowercase only), so `\bW[0-9]+[A-Z]` is a precise proxy for the input shape
#: that triggers the bug, without needing the migrated tree to confirm it fired.
_WORK_ADJACENT_UPPER_RE: Final = re.compile(r"\bW[0-9]+[A-Z]")

#: One residue member's cause label, checked in this fixed order (a member matching more
#: than one shape is reported under the first — `_NOTES_STUB_RE` before content-based
#: checks, since a stub's path alone is conclusive and its content is the same shape every
#: time; frontmatter before the citation-shaped checks, since a wrong strip explains the
#: whole-file mismatch regardless of what citations the body also carries; cause4's
#: adjacent-uppercase corruption before the broader citation-shaped causes, since it is a
#: forward-migration defect rather than an inverse gap and deserves its own bucket even
#: when the same file also carries a legacy path citation).
def _residue_cause(rel: str, old_lines: Sequence[str] | None) -> str:
    if _NOTES_STUB_RE.match(rel):
        return "cause2b-notes-stub-relative-link"
    if old_lines is None:
        return "other"
    if old_lines and old_lines[0] == "---" and rel.startswith(_FOREIGN_FRONTMATTER_DIRS):
        return "cause1-foreign-frontmatter"
    for line in old_lines:
        if _WORK_ADJACENT_UPPER_RE.search(line):
            return "cause4-compound-token-adjacent-uppercase"
    for line in old_lines:
        if _RANGE_CITATION_RE.search(line):
            return "cause2a-range-citation"
    for line in old_lines:
        if _SLASH_COMPOUND_RE.search(line):
            return "slash-compound-citation (unassigned — reported, not investigated)"
    for line in old_lines:
        if any(pattern.search(line) for pattern in _LEGACY_PATH_RES):
            return "cause3-legacy-path-citation"
    return "other"


def _residue_cause_table(residue: Sequence[str], ctl: Corpus) -> str:
    """Ruling 102 §3's "name them", applied to the residue as a population: one line per
    cause, its count, and up to three example paths — computed on `ctl` (the same
    un-migrated corpus every other row shares), never a second tree read.
    """
    by_cause: dict[str, list[str]] = {}
    for rel in residue:
        cause = _residue_cause(rel, ctl.lines.get(rel))
        by_cause.setdefault(cause, []).append(rel)
    parts = []
    for cause in sorted(by_cause, key=lambda c: -len(by_cause[c])):
        members = by_cause[cause]
        examples = ", ".join(members[:3])
        parts.append(f"{cause}={len(members)} (e.g. {examples})")
    return "residue by cause: " + "; ".join(parts)


def row_g(docid: Any, snap: Snapshot, mig: Corpus, ctl: Corpus) -> Row:
    """§7 (g), as Ruling 68 defines it and Ruling 104 amends class 6: the migration diff
    filtered to hunks in the **six-class closed enumeration**, empty.

    Two sub-predicates, each printed:

    - **g1** — the mangled-citation scan Ruling 102 §2 row 1 names as (g)'s broken-input
      proof, read against its own at-risk denominator and an un-migrated control.
    - **g2** — Ruling 68's filter itself, `doc-id.classify_migration_diff`, bucketing every
      file the migration diff touches into one of the six named classes or into
      `CLASSIFIED_BY_NONE`. Ruling 68 §2: *"A hunk the filter cannot classify fails; it is
      never passed through."* The residue bucket therefore sets the verdict, and its
      members are named in the note — never folded into one aggregate number, so a reader
      can see which of the six classes a clean run actually rests on.

    The filter is **not** reimplemented here. `classify_migration_diff` is the one
    definition, and it in turn calls `audit-docs.py`'s own DP-7 predicate for classes 1-3
    and re-derives class 6 by an independent second `migrate()` run, never by path —
    Ruling 104 §2's own violation clause for a classifier keyed on a filename.
    """
    classification = docid.classify_migration_diff(snap.control, snap.migrated)
    residue = classification.per_class.get(docid.CLASSIFIED_BY_NONE, ())

    m_mangled, m_mangled_files = mig.scan(MANGLED_CITATION_RE, skip_was=False)
    c_mangled, _ = ctl.scan(MANGLED_CITATION_RE, skip_was=False)
    at_risk, at_risk_files = ctl.scan(COMPOUND_CITATION_RE, skip_was=False)

    per_class = ", ".join(
        f"{key}={len(classification.per_class.get(key, ()))}"
        for key, _text in docid._RULING_68_CLASSES
    )

    if classification.population == 0:
        verdict = FAIL
        note = ("empty population — the migration classified no file, so the filter "
                "proves nothing")
    elif at_risk == 0:
        verdict, note = (
            FAIL,
            "the compound-citation population at risk is 0, so the mangled-citation "
            "sub-predicate cannot distinguish a clean migration from a dead pattern",
        )
    elif m_mangled or residue:
        # Ruling 68 §2 `:268` — "a hunk the filter cannot classify fails; it is never
        # passed through" — and W37-6 channel `:392` ruled the naming obligation follows
        # from that: every `classified-by-none` hunk is named, by path, with its own
        # `_fail` message, never truncated to an exemplar-plus-count. The population is
        # `residue`'s own size (`len(classification.per_class[CLASSIFIED_BY_NONE])`);
        # `classification.violations` is the same walk's one message per member, so this
        # is a full enumeration, not a sample.
        #
        # W37-6 channel `:512-536`'s ruling on this row's own follow-up refused a bare
        # total for `residue` ("acted on as a total rather than per cause" is a named
        # violation) — the cause table leads the note, the full per-file listing (already
        # a complete enumeration, not a sample) follows it.
        named = "; ".join(classification.violations)
        note = _residue_cause_table(residue, ctl) + " || " + named
        verdict = FAIL
    else:
        verdict, note = PASS, ""

    return Row(
        key="g",
        title="migration diff filtered to hunks that are neither header nor "
              "citation-token is empty",
        owner=OWNER_W37_6,
        predicate=(
            "g1 (Ruling 102 §2 row 1's named broken-input proof): "
            f"{MANGLED_CITATION_RE.pattern!r} — a citation with a *numeric* module segment "
            "and a trailing `/n` is a rewrite that matched inside a longer identifier. "
            "g2 (Ruling 68 §2's closed enumeration, amended by Ruling 104 §2/§3 for class "
            "6, by symbol, never restated here): "
            "`doc-id.classify_migration_diff(control, migrated)`, bucketing every touched "
            "file into `doc-id._RULING_68_CLASSES` or `doc-id.CLASSIFIED_BY_NONE`; classes "
            "1-3 share `audit-docs.frozen_file_matches_after_migration_stamp` (check 34's "
            "DP-7 predicate, Ruling 68 §3 — not a second one); class 4 requires the "
            "concatenation of a split's outputs to reproduce the source's non-blank body "
            "lines *in order*; class 5 is `docs/roadmap.md` alone, unconditionally, "
            "exactly as the ruling states it; class 6 is tested against an independent "
            "second `migrate()` run's own output at the same path, never by filename"
        ),
        denominator=(
            f"{classification.population} file(s) classified "
            f"({classification.unchanged} unchanged, not a hunk); "
            f"{at_risk} compound citation(s) at risk in {at_risk_files} file(s)"
        ),
        migrated=(
            f"g1 mangled = {m_mangled} in {m_mangled_files} file(s); "
            f"g2 {per_class}, {docid.CLASSIFIED_BY_NONE}={len(residue)}"
        ),
        control=f"g1 mangled = {c_mangled} (un-migrated)",
        verdict=verdict,
        note=note,
    )


# ---------------------------------------------------------------------------------------
# (h) the full gate green on the migrated tree
# ---------------------------------------------------------------------------------------

#: The summary lines `audit-docs.py` prints as *passing* while their population is empty.
#: Each is `(label, regex, group index of the denominator)`. This is NT-0007 at scale: on a
#: migrated tree these read "0 requirements defined across 8 specs" and the exit code alone
#: would never have surfaced it (handover §4).
_VACUITY_PROBES: Final = (
    ("requirements defined", re.compile(r"(\d+) requirements defined across (\d+) specs"), 1),
    ("open questions", re.compile(r"(\d+) open questions"), 1),
    ("journey endpoint citations", re.compile(r"journey citations: (\d+) endpoints"), 1),
    ("§10 mirror rows", re.compile(r"\d+ of (\d+) §10 mirror rows"), 1),
    ("check 37 documents in scope",
     re.compile(r"check 37: (\d+) document\(s\) checked in scope"), 1),
    ("check 37 `was:` exemptions",
     re.compile(r"check 37:.*?, (\d+) exempt as verbatim-migrated"), 1),
)

#: §7(h) names nine gate halves. Six of them need an installed toolchain (a `uv` venv, a
#: pnpm store) that a `git archive` snapshot does not have. They are NOT MEASURED here with
#: the owner named rather than silently dropped — §13 admits no silence, and handover §2.3
#: is the precedent: "not measured, owner the executor's PR CI".
#: `audit-docs.py` saying a check has nothing to scan. Distinct from a failing check and
#: from an empty-population pass: the check did not run at all, and the exit-code summary
#: has no way to say so.
_ABSENT_CHECK_RE: Final = re.compile(r"cannot run|cannot scan it")

#: Ruling 105 §B's own methodology, ported from the shell one-liner
#: `docs/plans/2026-09-03-w37-6-row-h-the-named-h-rows.md:139` used to derive the taxonomy
#: the ruling reads: `sed -n '/^FAILED/,$p' <log> | grep '^  - ' | sed -E
#: 's/^(check [0-9]+):.*/\1/; s/^broken link in .*/check 1/' | sort | uniq -c`. Everything
#: from the `FAILED (`n`):` line onward, one `  - <msg>` per failure.
_FAILED_BLOCK_RE: Final = re.compile(r"^FAILED \(\d+\):$", re.MULTILINE)
_FAILURE_LINE_RE: Final = re.compile(r"^  - (.*)$", re.MULTILINE)
_CHECK_PREFIX_RE: Final = re.compile(r"^check (\d+):")
_BROKEN_LINK_RE: Final = re.compile(r"^broken link in ")

#: Checks 29, 30 and 35 are (h1)'s W37-10 residue — Ruling 105 §B: disclosed by count,
#: owner-labelled, never fatal. Every other class, including a failure this predicate
#: cannot attribute to a check number at all (`"unclassified"`, never dropped — §13 admits
#: no silence), must be zero for (h1) to pass.
_H1_DISCLOSED_CHECKS: Final = frozenset({"29", "30", "35"})


def _classify_failures(out: str) -> dict[str, int]:
    """One bucket per `check N`, plus `"unclassified"` for a failure message this predicate
    cannot attribute to a check number — counted, never dropped."""
    counter: dict[str, int] = {}
    block = _FAILED_BLOCK_RE.search(out)
    tail = out[block.start():] if block else ""
    for msg in _FAILURE_LINE_RE.findall(tail):
        m = _CHECK_PREFIX_RE.match(msg)
        cls = m.group(1) if m else ("1" if _BROKEN_LINK_RE.match(msg) else "unclassified")
        counter[cls] = counter.get(cls, 0) + 1
    return counter


def _h1_verdict(other_total: int) -> str:
    """Ruling 105 §B: (h1) passes iff every class outside checks 29/30/35 is zero."""
    return PASS if other_total == 0 else FAIL


def _h2_verdict(vacuous: Sequence[str], over_exempt: bool) -> str:
    """Ruling 105 D3: the zero-denominator probes stay fatal; OVER-EXEMPT alone discloses."""
    if vacuous:
        return FAIL
    if over_exempt:
        return DISCLOSE
    return PASS


_UNMEASURED_GATE_HALVES: Final = (
    "pytest tests/", "lint-imports", "backend suite", "pricing-core suite",
    "model-schema suite", "frontend suite (pnpm lint/type-check/test/build)",
    "docs/contracts/ drift (generate-contracts.py --check)",
)


#: The over-exemption probe's two thresholds, named so a reader can see what "large" and
#: "almost entirely" mean rather than inferring them from a magic number. The floor exists
#: because 1-of-1 and 0-of-1 are the pre-H-row state and are not evidence of anything.
_EXEMPTION_FLOOR: Final = 20
_EXEMPTION_RATE_CAP: Final = 0.5


def _probe_summary(out: str) -> dict[str, int | None]:
    found: dict[str, int | None] = {}
    for label, pattern, group in _VACUITY_PROBES:
        m = pattern.search(out)
        found[label] = int(m.group(group)) if m else None
    return found


def rows_h(snap: Snapshot) -> list[Row]:
    mig_audit = _run_script(snap.migrated, "audit-docs.py")
    ctl_audit = _run_script(snap.control, "audit-docs.py")
    mig_out = mig_audit.stdout + mig_audit.stderr
    ctl_out = ctl_audit.stdout + ctl_audit.stderr
    failures = re.search(r"FAILED \((\d+)\)", mig_out)
    ctl_failures = re.search(r"FAILED \((\d+)\)", ctl_out)
    mig_absent = len(_ABSENT_CHECK_RE.findall(mig_out))
    ctl_absent = len(_ABSENT_CHECK_RE.findall(ctl_out))

    mig_classes = _classify_failures(mig_out)
    h1_disclosed = {k: mig_classes.get(k, 0) for k in sorted(_H1_DISCLOSED_CHECKS, key=int)}
    h1_other = sum(v for k, v in mig_classes.items() if k not in _H1_DISCLOSED_CHECKS)
    h1_disclosed_text = "; ".join(
        f"check {k}={v} (owner: {OWNER_W37_10})" for k, v in h1_disclosed.items()
    )
    h1 = Row(
        key="h1",
        title="audit-docs.py green on the migrated tree, per failure class (Ruling 105 §B)",
        owner=OWNER_W37_6,
        predicate=(
            "python3 scripts/audit-docs.py   (run with cwd = the tree); failures classified "
            "by `_docverify._classify_failures` — Ruling 105 §B's own methodology, ported "
            "from `docs/plans/2026-09-03-w37-6-row-h-the-named-h-rows.md:139`'s `sed -n "
            "'/^FAILED/,$p' <log> | grep '^  - ' | sed -E 's/^(check [0-9]+):.*/\\1/; "
            "s/^broken link in .*/check 1/' | sort | uniq -c`"
        ),
        denominator=(
            f"{len(mig_out.splitlines())} output line(s); "
            f"{sum(mig_classes.values())} failure(s) total, {len(mig_classes)} class(es)"
        ),
        migrated=f"exit {mig_audit.returncode}"
        + (f", FAILED ({failures.group(1)})" if failures else "")
        + f", {mig_absent} check(s) did not execute; {h1_disclosed_text}; "
        f"{h1_other} failure(s) outside checks 29/30/35",
        control=f"exit {ctl_audit.returncode}"
        + (f", FAILED ({ctl_failures.group(1)})" if ctl_failures else "")
        + f", {ctl_absent} check(s) did not execute",
        verdict=_h1_verdict(h1_other),
        note="; ".join(
            part
            for part in (
                f"checks 29, 30 and 35 are W37-10's residue (Ruling 105 §B), disclosed by "
                f"count and never fatal: {h1_disclosed_text}. Every other class — including "
                "checks 32, 36, 1, 31, 27 and any class not named here — must be zero to "
                "pass",
                (
                    f"{mig_absent} check(s) report they CANNOT RUN on the migrated tree "
                    f"(control {ctl_absent}) — the old notes directory is dissolved by the "
                    "migration, so checks 16-20 and 25 have nothing to scan. Non-execution "
                    "is a third state beside pass and fail, and a failure count scores it "
                    "as a small number of failures rather than as a hole in coverage."
                    if mig_absent else ""
                ),
            )
            if part
        ),
    )

    mig_probes = _probe_summary(mig_out)
    ctl_probes = _probe_summary(ctl_out)
    vacuous = [
        label
        for label in mig_probes
        if (ctl_probes[label] or 0) > 0 and (mig_probes[label] or 0) == 0
    ]
    # A second vacuity shape, and the zero-denominator rule cannot see it: a LARGE
    # population almost entirely exempted. Raised by the auditor as the hazard that only
    # appears once the H rows land — check 37 then exempts ~353 of ~424 documents as
    # verbatim-migrated on the strength of a `was:` field that is correct 3 times in ~393.
    # Before the H rows it exempts 0 of 1 and is harmless, which is exactly why a probe
    # keyed on zero denominators would never have raised it.
    in_scope = mig_probes["check 37 documents in scope"] or 0
    exempt = mig_probes["check 37 `was:` exemptions"] or 0
    rate = (exempt / in_scope) if in_scope else 0.0
    over_exempt = in_scope >= _EXEMPTION_FLOOR and rate >= _EXEMPTION_RATE_CAP
    check37_reds = mig_classes.get("37", 0)
    h2 = Row(
        key="h2",
        title="audit-docs.py's passing lines are not green over an empty population",
        owner=OWNER_W37_6,
        predicate=(
            "each of `_docverify._VACUITY_PROBES` matched against audit-docs.py's output "
            "on both trees; a probe whose migrated denominator is 0 while the "
            "un-migrated control's is non-zero is a vacuous pass (NT-0007)"
        ),
        denominator=f"{len(_VACUITY_PROBES)} probe(s)",
        migrated="; ".join(f"{k}={v}" for k, v in mig_probes.items()),
        control="; ".join(f"{k}={v}" for k, v in ctl_probes.items()),
        verdict=_h2_verdict(vacuous, over_exempt),
        note="; ".join(
            part
            for part in (
                ("vacuous on: " + ", ".join(vacuous)) if vacuous else "",
                (
                    "OVER-EXEMPT (Ruling 105 D3, disclosed not failed): Ruling 97 §4's four "
                    f"figures — {check37_reds} red · {in_scope} examined · {exempt} exempt "
                    f"by `was:` ({rate:.0%}) · the broken-input control (Ruling 97 §3 proof "
                    "2, evidence that the exemption is what holds the population out rather "
                    "than a detector that stopped working) — a large population almost "
                    "entirely excused rather than an empty one; the zero-denominator rule "
                    "cannot see this shape. Ruling 96's ruled outcome, accepted with its "
                    "disclosure at delegation §6.3"
                ) if over_exempt else "",
                f"check 37 exemption rate {exempt}/{in_scope}" if in_scope else "",
            )
            if part
        ),
    )

    mig_req = _run_script(snap.migrated, "req-coverage.py")
    ctl_req = _run_script(snap.control, "req-coverage.py")
    mig_req_out = mig_req.stdout + mig_req.stderr
    ctl_req_out = ctl_req.stdout + ctl_req.stderr
    mig_n = re.search(r"(\d+)\s+requirement", mig_req_out)
    ctl_n = re.search(r"(\d+)\s+requirement", ctl_req_out)
    mig_count = int(mig_n.group(1)) if mig_n else 0
    ctl_count = int(ctl_n.group(1)) if ctl_n else 0
    if ctl_count == 0:
        h3_verdict, h3_note = FAIL, "control found no requirement either — the probe is dead"
    elif mig_count == 0:
        h3_verdict, h3_note = FAIL, "empty population — 0 requirements on the migrated tree"
    else:
        h3_verdict, h3_note = (PASS if mig_req.returncode == 0 else FAIL), ""
    h3 = Row(
        key="h3",
        title="req-coverage.py green on the migrated tree",
        owner=OWNER_W37_6,
        predicate="python3 scripts/req-coverage.py   (run with cwd = the tree)",
        denominator=f"{mig_count} requirement(s) seen by req-coverage on the migrated tree",
        migrated=f"exit {mig_req.returncode}, {mig_count} requirement(s)",
        control=f"exit {ctl_req.returncode}, {ctl_count} requirement(s)",
        verdict=h3_verdict,
        note=h3_note,
    )

    h4 = Row(
        key="h4",
        title="the rest of §7(h)'s gate on the migrated tree",
        owner=f"{OWNER_W37_6} (the executor's PR CI — handover §2.3)",
        predicate=(
            "`_docverify._UNMEASURED_GATE_HALVES`: "
            + ", ".join(_UNMEASURED_GATE_HALVES)
        ),
        denominator=f"{len(_UNMEASURED_GATE_HALVES)} gate half/halves",
        migrated="not run in-snapshot — see the migration PR's own CI (Ruling 105 D2)",
        control="not run",
        verdict=DISCLOSE,
        note=(
            "measured by the migration PR's own CI on its exact head — all four workflows "
            "green — plus the executor's local run of CLAUDE.md §11's two halves, both "
            "recorded in W37-6's ledger with the head SHA (Ruling 105 D2). Never `NOT "
            "MEASURED` in the snapshot: a `git archive` snapshot has no uv venv and no pnpm "
            "store, so these cannot run in-snapshot at all, and that absence is disclosed "
            "rather than reported as an unmeasured verdict. handover §2.3 is the precedent "
            "for naming the owner rather than dropping it silently (§13). CLAUDE.md §11: a "
            "Python-only 'gate' has been green here while the frontend was red."
        ),
    )
    return [h1, h2, h3, h4]


# ---------------------------------------------------------------------------------------
# (i) every H row in NT-0019 §5 closed by a named commit — W37-10's
# ---------------------------------------------------------------------------------------

#: An H row in one of NT-0019 §5's tables: the last cell is `H` (optionally `H + M`).
_H_ROW_RE: Final = re.compile(r"^\|.*\|\s*H(\s*\+\s*[A-Z])?\s*\|\s*$")


#: The note's pre-migration path. Post-migration it is somewhere else, under a slug derived
#: from its *title*, not its old filename — `docs/rfcs/RFC-00216-one-id-per-governed-thing-…`
#: — so a `rglob("*one-id-per-document*")` finds nothing. It is followed through
#: `docs/REDIRECTS.csv`, which is the artifact the migration writes for exactly this
#: purpose; guessing the new name instead is how a row silently measures an empty file.
_NT0019_PATH: Final = "docs/notes/0019-one-id-per-document.md"


def _redirect_map(tree: Path) -> Mapping[str, str]:
    """`old_path -> new_path` from the run's own generated `docs/REDIRECTS.csv`.

    One definition, two consumers (row (f)'s conjunct 2 and `_follow_redirect`), because two
    parsers of one artifact is how they drift apart. **It is one-to-one**, which is exactly
    what Ruling 103 found conjunct 2's first wording could not express: a split source's
    content goes to several files and this map names one of them.
    """
    redirects = tree / "docs" / "REDIRECTS.csv"
    if not redirects.is_file():
        return {}
    with redirects.open(encoding="utf-8", newline="") as fh:
        return {
            row["old_path"]: row["new_path"]
            for row in csv.DictReader(fh)
            if row.get("old_path") and row.get("new_path")
        }


def _follow_redirect(tree: Path, old_path: str) -> Path:
    """`old_path` in `tree`, or wherever `docs/REDIRECTS.csv` says the migration put it."""
    literal = tree / old_path
    if literal.is_file():
        return literal
    new_path = _redirect_map(tree).get(old_path)
    return tree / new_path if new_path else literal


def _count_h_rows(tree: Path) -> int:
    note = _follow_redirect(tree, _NT0019_PATH)
    text = read_text(note) or ""
    lines = text.splitlines()
    in_five = False
    count = 0
    for line in lines:
        if re.match(r"^##\s+5\.", line):
            in_five = True
        elif re.match(r"^##\s+(?!5\.)", line):
            in_five = False
        elif in_five and _H_ROW_RE.match(line):
            count += 1
    return count


def row_i(snap: Snapshot) -> Row:
    h_rows = _count_h_rows(snap.migrated)
    return Row(
        key="i",
        title="every H row in NT-0019 §5 closed by a named commit",
        owner=OWNER_W37_10,
        predicate=(
            f"`_docverify._H_ROW_RE` = {_H_ROW_RE.pattern!r} over the §5 tables of "
            "docs/notes/0019-one-id-per-document.md; 'closed by a named commit' needs a "
            "row→commit mapping artifact, and no such artifact exists in the tree"
        ),
        denominator=f"{h_rows} H row(s) in §5",
        migrated="0 closed by a named commit — no row→commit mapping artifact exists",
        control="n/a — the row is about commits, not tree content",
        verdict=DISCLOSE if h_rows else FAIL,
        note=("" if h_rows else
              "empty population — no H row was found in §5, so this row's own predicate "
              "measured nothing (NT-0007). ") + (
            "OWNERSHIP TENSION, ruled by Ruling 105 D1. Ruling 102 §1 requires the "
            "instrument to compute all NINE rows (a)-(i); Ruling 102 §3 rules that (i) is "
            "W37-10's, not W37-6's ('Eight rows, not nine'). Both are obeyed: the row is "
            "computed as §1 says and its owner is printed as §3 says. Ruling 105 D1 rules "
            "(i) non-fatal — it does not set the exit code — so this instrument is not red "
            "on a row W37-6 cannot fix; `FATAL_VERDICTS` keeps `NOT MEASURED` fatal for "
            "every other row that uses it."
        ),
    )


# ---------------------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
# The recorded verdict set — so a NEW failure is distinguishable from the standing red
# ---------------------------------------------------------------------------------------

#: **Every row's verdict as recorded at the tree this constant was last reviewed at.**
#:
#: The problem this solves is a property of the wiring, not of anyone's habits. While §7 is
#: red by design (Ruling 102 §1), the `docs` job's pass/fail bit **carries no information
#: about the change under review**: it is red before a regression and red after it. One of
#: CI's three signals is switched off, and the duration is "until the migration lands".
#:
#: It has already cost once (F102). An audit record added under `docs/audit/` with an
#: ordinary descriptive name landed in `none` and took row (a) — **the only passing row** —
#: from `none=0` to `none=1`. `audit-docs.py`, `register-lint.py` and the full local gate
#: were all green. The regression was visible only inside the failing step's row list, and
#: was caught only because that reader happened to be holding a baseline of their own.
#:
#: **Both directions are enforced, and that is what stops the baseline going stale.**
#: A committed baseline nobody updates is `NT-0003`; a baseline regenerated automatically
#: records whatever is currently broken and can never fail. Neither is right. So:
#:
#: * a row **newly failing** is a REGRESSION — the case F102 is about;
#: * a row **newly passing** is PROGRESS, and is *also* a set change, because a row fixed
#:   and left in this table would mask its own later regression. It is reported as progress
#:   with the edit it requires, never as an anomaly.
#:
#: **This table is edited by hand, in the same commit as the change that moves a row.** That
#: is the point: the edit is the reviewable record of a row moving, and it cannot be
#: produced by re-running the instrument.
#:
#: **2026-09-03 correction, at `3dbee20` (task 23; re-verified independently rather than
#: transcribed from any relay).** Four rows moved:
#:
#: * **(d2) `PASS` was never true.** `git log -S'EXPECTED_VERDICTS' -- scripts/_docverify.py`
#:   returns exactly one commit (`f6c9ff2`, #698) — the table has no history before its own
#:   birth, so "went stale" was never available as an explanation; `\bF-W[0-9]` never read
#:   near zero at any commit checked (`4b9117a`=214, `f6c9ff2`=217, `f52ee66`=217,
#:   `3dbee20`=217, always far short of the 505518-line denominator). The comment it
#:   carried — "green, and its mangled companion says why" — was a belief written into the
#:   slot a measurement belongs in, F99's own shape. **The live defect underneath is real
#:   and separate from the wrong entry**: diffed by exact token
#:   (`F-W11-1-5`: control 10, migrated 13), all three excess occurrences trace to one
#:   mechanism — a migrated document's front-matter `title:` field and its family
#:   `INDEX.md` row both echo the document's title verbatim, and a title that happens to
#:   quote a legacy citation (here, a ruling's own title naming the finding it corrects)
#:   duplicates that citation into two new permanent locations neither protected by the
#:   `was:`-line exclusion nor rewritten by `_rewrite_citations`. Confirmed at
#:   `docs/rulings/RL-00167-...md` (front matter `title:` line 4, body heading — carried
#:   over from the control's `## Ruling 13 —...`) and `docs/INDEX.md`/`docs/rulings/
#:   INDEX.md` (generated fresh, no control-tree counterpart at all). Not filed as a
#:   register finding by this change — reported to the lead for ownership (task 22 is the
#:   analogous, larger-scale instance on row (d8), and may be the same fix).
#: * **(d4) `REGRESSION` -> `FAIL`.** Still red, but no longer worse than the control:
#:   migrated 262 vs. control 272 (companion "mangled...filename slug" 18 vs. 50) — a real
#:   reduction, plausibly #693/#696's citation-rewrite and H-row work, not full closure.
#: * **(d8) `FAIL` -> `REGRESSION`, a NEW, unfixed defect** (task 22, unowned as of this
#:   commit): migrated 2788 vs. control 2644 (+144 lines / 30 files). Spot-checked against
#:   the same mechanism as (d2) at far larger scale — `docs/INDEX.md` alone carries 118
#:   `W[0-9]+[a-z]?-[0-9]+` matches with no control-tree counterpart, because every
#:   migrated document's slice/workstream-scoped title is echoed into the generated index.
#:   Recorded here as the true current state; the underlying defect is task 22's to fix,
#:   not silently accepted as fine.
#: * **(h3) `FAIL` -> `PASS`, genuine progress.** `req-coverage.py` now exits 0 with 533
#:   requirements on *both* trees (previously 0 on the migrated tree) — real, not vacuous
#:   (`ctl_count` and `mig_count` both non-zero, `_verdict_on_zero`'s dead-probe branches
#:   both avoided).
EXPECTED_VERDICTS: Final[Mapping[str, str]] = {
    "a": PASS,          # one family per file, zero `none` — the only row that passes today
    "b": FAIL,          # noncontiguous=4 — REGRESSED again after #711 (task 4's
                         # sweep-order/compound-citation/redirects PR), between this row's
                         # first re-recording as PASS (earlier in this same PR's own
                         # history, when based on #707/#708) and this final re-record
                         # against #711 (2026-09-04, task 17); unrelated to this PR's own
                         # diff — flagged to the lead as a genuine new defect, not fixed
                         # here (out of scope, id-allocation is not this row's file)
    "c": PASS,          # docs/INDEX.md byte-stable against its own renderer — same
                         # unrelated prior-PR progress, re-recorded for the same reason
    "d1": FAIL,         # NT-00
    "d2": DISCLOSE,     # F-W[0-9] — Ruling 105 §A: the same alias class as `F[0-9]{2}`,
                         # excluded from the zero requirement with its count disclosed
                         # regardless of the migrated/control comparison (2026-09-03, task 14).
                         # History, corrected (2026-09-04, task 17): PASS at `ac82256`/
                         # `a92d4e8` was NOT "never true" (a prior version of this comment
                         # said so, citing 214/217/217/217 — those are the CONTROL figure,
                         # unchanged on every commit, not the migrated one). It was real and
                         # manufactured: the migrated figure was 0 before #693 because the
                         # tokens had been mangled into `F-WK-*` (companion 221), and 220
                         # after #693 exposed them. A wrong recorded reason is an
                         # instruction to the next reader to reverse a decision that was
                         # actually right.
    "d3": DISCLOSE,     # \bF[0-9]{2}\b — excluded from the zero requirement (§8.5)
    "d4": FAIL,         # wf-0[0-9] — improved (262 < control 272), not the migration's own
                         # regression any more; still non-zero (2026-09-03, task 23)
    "d5": PASS,         # Ruling [0-9]+ — genuine progress from #711 (task 4), unrelated
                         # to this PR's own diff; re-recorded 2026-09-04, task 17
    "d6": FAIL,         # ADR-0[0-9]{3}\b — trailing `\b` added (2026-09-03, task 14, Ruling
                         # 67 §2 Part 1's already-ruled "complete identifier" requirement,
                         # not carried here until now): the bare pattern matched as a
                         # substring of any correctly-migrated five-digit id; genuine
                         # un-migrated 4-digit citations remain, so the row still fails
    "d7": FAIL,         # (FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+
    "d8": FAIL,         # workstream/slice id — #711 (task 4)'s sweep-order fix removed the
                         # title/INDEX-duplication "creation" bug (2026-09-03, task 22);
                         # migrated (299) is now BELOW control (2353), so Ruling 105 §A's
                         # third alias class (2026-09-04, task 17) applies: FAIL is real
                         # task-key population (30 in 11 files, `\bW[0-9]+[a-z]?-[0-9]+-
                         # [0-9]+\b`) — NOT the slice-key alias class, which discloses
                         # cleanly once the task keys are separately resolved; the ruling's
                         # own text expected 0 task keys outside fixtures, this measured
                         # 30, disclosed here rather than silently assumed
    "d9": FAIL,         # docs/plans/2026-
    "d10": FAIL,        # docs/audit/
    "d11": FAIL,        # the old notes directory
    "d12": FAIL,        # docs/adr/
    "d13": FAIL,        # the old .claude notes root — INERT, see its unanchored companion
    "e": FAIL,          # 2 padded ids in prose                    — Ruling 103
    "f": PASS,          # VR-DST-1 unchanged, both conjuncts — Ruling 103. Regressed on
                         # `main` (#707, 43d8698) when `docs/INDEX.md` started quoting
                         # requirement bodies mentioning VR-DST-1 with no pre-migration
                         # counterpart; disclosed rather than fixed there. Fixed here
                         # (2026-09-04, task 17/#20): (f) excludes every path in
                         # `MigrateResult.generated_paths` (Ruling 105 D3/#18 §1), keyed on
                         # the run's own generated-output list, never the literal path.
    "g": FAIL,          # the token-boundary defect                — Ruling 102 §2 row 1
    "h1": FAIL,         # audit-docs.py: checks 29/30/35 disclosed (owner W37-10, Ruling 105
                         # §B), but other classes (32, 36, 1, 31, 27, ...) are still non-zero
    "h2": DISCLOSE,     # zero-denominator probes now clear; only OVER-EXEMPT fires, which
                         # Ruling 105 D3 disclosed rather than failed (2026-09-03, task 14)
    "h3": PASS,         # req-coverage.py: 533 requirements on both trees, exit 0 on the
                         # migrated tree (was 0/empty-population FAIL; 2026-09-03, task 23)
    "h4": DISCLOSE,     # Ruling 105 D2: measured at the migration PR's own CI, never
                         # `NOT MEASURED` in the snapshot (2026-09-03, task 14)
    "i": DISCLOSE,      # Ruling 105 D1: W37-10's, non-fatal, does not set the exit code
                         # (2026-09-03, task 14)
}

REGRESSED: Final = "REGRESSION (newly failing)"
PROGRESSED: Final = "PROGRESS (newly passing)"
RECLASSIFIED: Final = "RECLASSIFIED"
ROW_ADDED: Final = "ROW ADDED"
ROW_REMOVED: Final = "ROW REMOVED"


@dataclass(frozen=True)
class SetChange:
    key: str
    expected: str
    actual: str
    direction: str


def diff_verdicts(rows: Sequence[Row]) -> tuple[SetChange, ...]:
    """Every difference between this run's verdicts and `EXPECTED_VERDICTS`."""
    actual = {row.key: row.verdict for row in rows}
    changes: list[SetChange] = []
    for key in sorted(set(actual) | set(EXPECTED_VERDICTS), key=_row_sort_key):
        want = EXPECTED_VERDICTS.get(key)
        got = actual.get(key)
        if want == got:
            continue
        if want is None:
            changes.append(SetChange(key, "(not recorded)", got or "", ROW_ADDED))
        elif got is None:
            changes.append(SetChange(key, want, "(not computed)", ROW_REMOVED))
        elif got == PASS:
            changes.append(SetChange(key, want, got, PROGRESSED))
        elif want == PASS:
            changes.append(SetChange(key, want, got, REGRESSED))
        else:
            changes.append(SetChange(key, want, got, RECLASSIFIED))
    return tuple(changes)


def _row_sort_key(key: str) -> tuple[str, int]:
    m = re.match(r"^([a-z]+)([0-9]*)$", key)
    return (m.group(1), int(m.group(2) or 0)) if m else (key, 0)


@dataclass(frozen=True)
class VerifyResult:
    snapshot: Snapshot
    rows: tuple[Row, ...]

    @property
    def failed(self) -> tuple[Row, ...]:
        return tuple(r for r in self.rows if r.fatal)

    @property
    def set_changes(self) -> tuple[SetChange, ...]:
        return diff_verdicts(self.rows)

    @property
    def exit_code(self) -> int:
        """0 green · 1 the standing red, unchanged · 3 the verdict set moved.

        Exit **3** is the whole point of the row. `1` says "§7 is not satisfied yet", which
        is true of every run until the migration lands and therefore says nothing about the
        change under review. `3` says "this change moved a row", which is the sentence a
        reviewer actually needs and which no reader currently has to hold a baseline to
        reach. (Exit 2 is a refusal to run at all — a misconfiguration, not a corpus state.)
        """
        if self.set_changes:
            return 3
        return 1 if self.failed else 0


def compute_rows(
    docid: Any, snap: Snapshot, generated_paths: Sequence[str] = ()
) -> list[Row]:
    """Every §7 (a)-(i) row, over a snapshot whose `migrated/` has already been migrated.

    `generated_paths` is `MigrateResult.generated_paths` from the same `migrate()` call
    that produced this snapshot's `migrated/` tree — (f)'s exclusion (Ruling 105 D3/#18).
    """
    mig = load_corpus(snap.migrated)
    ctl = load_corpus(snap.control)
    baseline = load_corpus(snap.baseline) if snap.baseline is not None else None
    rows: list[Row] = [row_a(docid, snap), row_b(docid, snap), row_c(snap)]
    rows.extend(rows_d(mig, ctl))
    rows.append(row_e(mig, ctl, snap))
    rows.append(row_f(mig, ctl, baseline, snap, generated_paths))
    rows.append(row_g(docid, snap, mig, ctl))
    rows.extend(rows_h(snap))
    rows.append(row_i(snap))
    return rows


def verify(
    docid: Any,
    *,
    repo_root: Path,
    ref: str,
    workdir: Path | None,
    keep: bool = False,
    with_baseline: bool = True,
) -> VerifyResult:
    """Build a snapshot, migrate it, and compute every row. Never touches `repo_root`."""
    tmp: tempfile.TemporaryDirectory[str] | None = None
    if workdir is None:
        tmp = tempfile.TemporaryDirectory(prefix="doc-id-verify-")
        target = Path(tmp.name)
    else:
        target = workdir.expanduser().resolve()
        assert_workdir_disposable(target)
    try:
        snap = build_snapshot(
            docid, repo_root=repo_root, ref=ref, workdir=target,
            with_baseline=with_baseline,
        )
        assert_tree_is_snapshot(snap.migrated)
        mig_result = docid.migrate(snap.migrated)
        # Stage the migration's whole output before anything measures the tree. Four of
        # the rows read the tree through `git ls-files` (`doc-id.py:classify_docs_files`,
        # `doc-index.py`, and this module's own population), and `migrate()` leaves the
        # ~1100 files it *creates* untracked. Measuring an unstaged tree silently scores
        # the migration's input as if it were its output: the first run of this instrument
        # reported row (a) as `none=74` on both trees — identical, because neither tree had
        # seen the migration as far as `ls-files` was concerned. That is precisely the
        # narrower-population-behind-a-wider-name failure Ruling 102 §1 exists to stop, and
        # it is recorded here rather than fixed silently.
        _git(snap.migrated, "add", "-A")
        # Assert it, rather than assume the `add` did what it says. The auditor measured
        # this in the inflating direction (audit-docs.py: 549 failures before the refresh,
        # 548 after) and a stale index is silent: every row that reads `git ls-files`
        # simply measures the wrong population and reports a well-formed number.
        # Deliberately NOT `git status --porcelain`: after `git add -A` that still lists
        # every *staged* path, which is the whole migration. The property being asserted is
        # "the index describes the working tree", which is exactly: nothing untracked, and
        # nothing modified relative to the index.
        untracked = _git(
            snap.migrated, "ls-files", "--others", "--exclude-standard"
        ).stdout.split()
        unstaged = _git(snap.migrated, "diff", "--name-only").stdout.split()
        if untracked or unstaged:
            raise WorkingCheckoutRefusedError(
                "the snapshot's git index still disagrees with its working tree after "
                f"`git add -A` ({len(untracked)} untracked, {len(unstaged)} unstaged) — "
                "every row reading `git ls-files` would measure the pre-migration "
                "population"
            )
        rows = compute_rows(docid, snap, mig_result.generated_paths)
        return VerifyResult(snapshot=snap, rows=tuple(rows))
    finally:
        if tmp is not None and not keep:
            tmp.cleanup()
        elif tmp is not None:
            # `keep` detaches the directory from the context manager's cleanup.
            tmp._finalizer.detach()  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------------------


def render(result: VerifyResult) -> str:
    snap = result.snapshot
    out: list[str] = []
    out.append("doc-id.py migrate --verify — NT-0019 §7 (a)-(i) (authority: Ruling 102 §1)")
    out.append(f"  ref            {snap.ref} = {snap.ref_sha}")
    out.append(f"  migrated tree  {snap.migrated}")
    out.append(f"  control tree   {snap.control} (same archive, never migrated)")
    if snap.baseline is not None:
        out.append(f"  baseline tree  {snap.baseline} ({BASELINE_REF} = {snap.baseline_ref})")
    else:
        out.append(f"  baseline tree  absent — {BASELINE_REF} does not resolve in this clone")
    out.append("")
    # The set-change block is printed FIRST and again LAST. A CI log is read from the end,
    # and a long table is skimmed from the top; a reader should not have to reach either.
    out.extend(_set_change_block(result))
    out.append("")
    for row in result.rows:
        out.append(f"[{row.verdict:<12}] ({row.key}) {row.title}")
        out.append(f"    owner        {row.owner}")
        out.append(f"    predicate    {row.predicate}")
        out.append(f"    denominator  {row.denominator}")
        out.append(f"    migrated     {row.migrated}")
        out.append(f"    control      {row.control}")
        for label, predicate, figure in row.companions:
            out.append(f"    companion    {label}")
            out.append(f"      predicate  {predicate}")
            out.append(f"      figure     {figure}")
        if row.note:
            out.append(f"    note         {row.note}")
        out.append("")
    counts: dict[str, int] = {}
    for row in result.rows:
        counts[row.verdict] = counts.get(row.verdict, 0) + 1
    out.append(
        "summary: "
        + ", ".join(f"{counts[v]} {v}" for v in sorted(counts))
        + f" over {len(result.rows)} row(s)"
    )
    if result.failed:
        out.append(
            "FAIL: " + ", ".join(f"({r.key})" for r in result.failed)
        )
    else:
        out.append("PASS: every row green")
    out.extend(_set_change_block(result))
    return "\n".join(out)


def _set_change_block(result: VerifyResult) -> list[str]:
    """The one line a reviewer needs, and the reason exit 3 exists.

    Without it the `docs` job's bit is red before a regression and red after it, and the
    only way to tell them apart is to hold a baseline of your own — which is how F102 was
    caught and how it would otherwise have been missed.
    """
    changes = result.set_changes
    n_fail = sum(1 for r in result.rows if r.fatal)
    n_expected = sum(1 for v in EXPECTED_VERDICTS.values() if v in FATAL_VERDICTS)
    if not changes:
        return [
            f"UNCHANGED: {n_fail} fatal row(s), matching the recorded set of {n_expected} "
            f"in `_docverify.EXPECTED_VERDICTS` — the standing red, and this change moved "
            "no row."
        ]
    out = [
        f"SET CHANGE ({len(changes)}): {n_fail} fatal row(s) against a recorded "
        f"{n_expected}. This change MOVED A ROW; the standing red is not the whole story."
    ]
    for change in changes:
        out.append(
            f"  {change.direction}: ({change.key}) {change.expected} -> {change.actual}"
        )
    if any(c.direction == REGRESSED for c in changes):
        out.append(
            "  A regression: a row that was passing is not any more. This is F102's case "
            "and it is what exit 3 exists to make visible without a baseline."
        )
    if any(c.direction in (PROGRESSED, RECLASSIFIED, ROW_ADDED, ROW_REMOVED) for c in changes):
        out.append(
            "  Progress or a reclassification is ALSO a set change, deliberately: a row "
            "left stale in `EXPECTED_VERDICTS` would mask its own later regression. Update "
            "that table in the same commit as the change that moved the row."
        )
    return out
