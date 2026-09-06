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
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any, Final

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


class InvalidResidueClassError(RuntimeError):
    """A `docs/audit/w37-11-record.md` row names a `cls` no extractor can produce.

    #763's defect: a record entry carrying `cls = "comma-continuation-left-whole"` — a
    description of *why* the residue exists, not a class `rows_d`/`row_g`/`rows_h`
    actually key their measurements on. Such an entry governs nothing (`check_residue_
    ceiling`/`_residue_fully_governed` both key on the real `cls`, never find it, and
    silently read the entry as 0 forever) while the real residue surfaces under its true
    class in files the record does not name — a double failure that produces no error and
    no red, only a governance table that reads clean and is not. This is why an unknown
    `cls` is fatal at load rather than skipped like a malformed row (wrong cell count, a
    non-integer count): those degrade to "not yet governed", the same as the file not
    existing; an unknown `cls` degrades to "governs nothing, forever, silently", which
    `load_w37_11_record`'s own leniency rule was never meant to cover.
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
    """`_LS_FILES_ARGS`'s population, minus every `_docid.sweep_exclusion_reason` hit —
    a lockfile, a `tests/fixtures/docs-ids/`/`tests/fixtures/docs-migration/` fixture, or
    a `__pycache__`/`.pyc` bytecode-cache artifact. `--exclude-standard` already keeps a
    *tracked-then-.gitignore'd* `.pyc` out of this list on its own, but the exclusion is
    applied here too regardless — belt and braces, and the one place every corpus
    consumer (`load_corpus`, and everything built on it: rows (a)/(b)/(d)/(e)/(g)/(h)/(i))
    shares rather than each re-deriving.
    """
    out = _git(tree, *_LS_FILES_ARGS).stdout.splitlines()
    return sorted(
        rel for rel in {r for r in out if r}
        if _docid.sweep_exclusion_reason(rel) is None
    )


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


#: `docs/plans/2026-09-04-w37-6-ruling-107-check-32-36-shared-predicates.md` Entry 1 item 1:
#: the fence predicate moved into `_docid` so `audit-docs.py`
#: check 36 can read the identical rule row (e)'s `padded_hits` and row (d)'s corpus both
#: use — re-exported here under this module's existing name for every caller and test
#: already written against it (Ruling 103 §1.8: "two implementations of one rule that are
#: never compared are two rules"; this is the fix for that, not a second implementation).
fenced_line_numbers = _docid.fenced_line_numbers


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
    fenced_lines: Mapping[str, frozenset[int]]

    @property
    def n_files(self) -> int:
        return len(self.files)

    @property
    def n_lines(self) -> int:
        return sum(len(v) for v in self.lines.values())

    def scan(
        self, pattern: re.Pattern[str], *, skip_was: bool = True, skip_fenced: bool = False
    ) -> tuple[int, int]:
        """(matching lines, matching files) for `pattern` over this corpus.

        `skip_fenced` (2026-09-04, row (d8), task #30): also skips a line inside a
        ` ``` `/`~~~` fence, using `_FENCE_RE` — the identical, single tracker `padded_
        hits` (row (e)'s own conjunct 0) already uses, never a second one written here,
        per Ruling 67 §2's "one rule at two times." Defaults `False` so every existing
        (d) alternative's own reading is byte-identical to before this parameter existed;
        opted into only where a real document fences an illustrative example under
        Ruling 103 §5.1's convention (class 3a) rather than being exempted by name.
        """
        n_lines = 0
        n_files = 0
        for rel in self.files:
            skip = self.was_lines[rel] if skip_was else frozenset()
            if skip_fenced:
                skip = skip | self.fenced_lines[rel]
            hits = sum(
                1
                for i, line in enumerate(self.lines[rel])
                if i not in skip and pattern.search(line)
            )
            if hits:
                n_lines += hits
                n_files += 1
        return n_lines, n_files

    def hits_by_file(
        self, pattern: re.Pattern[str], *, skip_was: bool = True, skip_fenced: bool = False
    ) -> Mapping[str, int]:
        """`scan`'s own per-file breakdown — same skip rules, keyed by relpath, a file with
        zero hits absent rather than present at 0. The W37-11 residue ceiling's own
        measurement reads this, never a private re-implementation of `scan`'s loop.
        """
        by_file: dict[str, int] = {}
        for rel in self.files:
            skip = self.was_lines[rel] if skip_was else frozenset()
            if skip_fenced:
                skip = skip | self.fenced_lines[rel]
            hits = sum(
                1
                for i, line in enumerate(self.lines[rel])
                if i not in skip and pattern.search(line)
            )
            if hits:
                by_file[rel] = hits
        return by_file


def load_corpus(tree: Path, *, exclude_basename: str | None = _D_EXCLUDED_BASENAME) -> Corpus:
    files: list[str] = []
    lines: dict[str, tuple[str, ...]] = {}
    was: dict[str, frozenset[int]] = {}
    fenced: dict[str, frozenset[int]] = {}
    for rel in tracked_files(tree):
        if exclude_basename is not None and rel.rsplit("/", 1)[-1] == exclude_basename:
            continue
        text = read_text(tree / rel)
        if text is None:
            continue
        files.append(rel)
        lines[rel] = tuple(text.splitlines())
        was[rel] = was_field_line_numbers(text)
        fenced[rel] = fenced_line_numbers(text)
    return Corpus(
        tree=tree, files=tuple(files), lines=lines, was_lines=was, fenced_lines=fenced
    )


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
    #: This row's own fatal hits, keyed `(relpath, cls)` — absent rather than present at 0.
    #: Feeds the W37-11 residue ceiling (`check_residue_ceiling`). `cls` is the row's own
    #: choice of granularity: a plain row names one class (conventionally its own `key`); a
    #: row with sub-buckets a per-row total would hide movement inside of (row (g)'s g2
    #: causes) names one `cls` per bucket instead — the ceiling is per (file, class), not
    #: per row, precisely so that distinction is never collapsed back to a single number. A
    #: row that does not populate this (most do not — only a ruled DISCLOSE-with-residue
    #: row is ever measured against a ceiling) simply contributes nothing.
    residue: Mapping[tuple[str, str], int] = field(default_factory=dict)

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
    # This subprocess's own imports (`doc-index.py` loading `_docid.py`, `doc-id.py`, …)
    # would otherwise cache `.pyc` files into `tree`'s `scripts/__pycache__/` — a second
    # writer of the same exhaust `doc-id.py`'s `_load_module` guards against in-process.
    # `--exclude-standard` already keeps a *tracked* `.pyc` out of `tracked_files()`'s
    # `git ls-files` population regardless, but a non-git-aware whole-tree walk
    # (`_iter_tree_files`, read via `sweep_exclusion_reason` there too) is not the only
    # consumer, so both layers stay covered rather than relying on one to save the other.
    env["PYTHONDONTWRITEBYTECODE"] = "1"
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
#:
#: `docs/plans/2026-09-04-w37-6-ruling-107-check-32-36-shared-predicates.md` Entry 1 item 1:
#: moved into `_docid.FINDING_ID_ALIAS_LABELS` so `audit-docs.py`
#: check 36 can read the identical two-label set — re-exported here under this module's
#: existing name. Deliberately the *narrower* of `_docid`'s two disclosed-label constants:
#: `rows_d` below dispatches row (d8) (`label == _D8_LABEL`) before ever consulting this
#: set, so `_docid.DISCLOSED_ALIAS_LABELS`' third member (the workstream/slice-id label,
#: check 36's own concern) would be dead here even if aliased to it.
D_DISCLOSED: Final = _docid.FINDING_ID_ALIAS_LABELS

#: The five §7(d) alternatives that cite a *path* rather than an id (`_docid.
#: LEGACY_FORM_PATTERNS`' own `"...path"` suffix) — rows (d9)-(d13). Handled by
#: `_path_alternative_verdict` below rather than folded into `D_DISCLOSED`: unlike an
#: alias class, a path alternative's disclosure is per-*match*, never per-alternative
#: whole — the same alternative can count both a real, unrewritten file citation
#: (fatal) and a bare directory mention with no successor (disclosed) in the same run.
D_PATH_LABELS: Final = frozenset(
    name for name, _ in _docid.LEGACY_FORM_PATTERNS if "path" in name
)

#: Which ruling reads each disclosed alternative, printed in its row's own note so a reader
#: does not have to guess which citation covers which alternative.
D_DISCLOSED_CITATION: Final[Mapping[str, str]] = {
    "finding id (bare form)": "§8.5; Ruling 102 §4",
    "finding id (workstream form)": "§7(d); Ruling 105 §A — the same alias class as the "
                                     "bare finding id, resolved by W37-11's alias resolver",
}


#: What each §7(d) alternative turns INTO when the rewrite goes wrong. Directed by the lead
#: after auditor finding A1, whose evidence is the reason this table exists rather than a
#: comment: `F-W<n>-<m>-<k>` -> `F-WK-<xxx>-<m>-<k>`, because the rewrite matched the work
#: key `W<n>` *inside* the finding id. `F-WK` has a letter where `F-W[0-9]` wants a digit, so the
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
        m_lines, m_files = mig.scan(c_pattern, skip_fenced=True)
        c_lines, _ = ctl.scan(c_pattern, skip_fenced=True)
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
    u_mig, _ = mig.scan(unanchored, skip_fenced=True)
    u_ctl, _ = ctl.scan(unanchored, skip_fenced=True)
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
#: SAME row stay fatal regardless of the disclosure — a bare work-key remainder
#: (`W<n>[a-z]?` with no slice number at all) and "creation" (migrated > control on the
#: whole alternative) — which needs checking BEFORE the disclosure, not after, unlike
#: `D_DISCLOSED`'s other members.
#:
#: **Task keys (`W<n>-<m>-<k>`) join the disclosed component (Ruling #26, 2026-09-04,
#: `to-lead.md:498-510`; carried here from PR #739, verify105), printed as their own
#: count line.** First ruled fatal on the belief that the population was fixtures only;
#: the real measurement found live citations. The class does not change with the count:
#: NT-0019 §1.2 has `WK` and `SL` and nothing below a slice, so a task key has no target
#: by the standard's own design — the same ground as a slice key, not the mangling/
#: token_map class a bare work key is.
#:
#: **The code comment this replaced also claimed "every Work mints a `WK-`, so an
#: unmapped [bare] one is a real `token_map` defect" — corrected here (2026-09-04, task
#: #30) to a narrower, measured claim.** That absolute is false on the real tree: measured
#: directly, all 8 real-document bare-key matches are illustrative naming-system examples
#: (a split-then-letter and a rejected-suffix form, fenced under Ruling 103 §5.1 in
#: `.claude/skills/close-workstream/SKILL.md`, `docs/audit/closure-records.md` and
#: `docs/plans/2026-08-22-w6b-slice-map.md` — never real historical ids) and the
#: remaining 6 are this instrument's own test literals (class 3c,
#: `_docid.TEST_MODULE_EXCLUSIONS`). A bare, unmapped work key CAN still be a real
#: `token_map` defect; it is not NECESSARILY one, which is why this alternative stays
#: fatal on any occurrence rather than trying to tell the two apart at measurement time.
#:
#: **Left-bound fix (2026-09-04, task #30, Ruling 67 §2 Part 1 from the other end):** all
#: three patterns below gained `_docid.TOKEN_LEFT_BOUND` — a bare `\b` at a pattern's own
#: left edge is satisfied between a hyphen and the next character, so `F-W37-6-12` (a real
#: `_FINDING_ID`-shaped finding id, `audit-docs.py`) matched `_D8_TASK_KEY_RE` from its
#: second character. **One shared constant, per Ruling 67 §2** ("one rule at two
#: times... never a private copy each script maintains independently") — this reads
#: `_docid.TOKEN_LEFT_BOUND`, the same narrowed left-boundary rule `LEGACY_FORM_PATTERNS`
#: (row (d)) reads, rather than a second, independently-maintained left-bound constant; see
#: `_docid.TOKEN_LEFT_BOUND`'s own comment for why the guard is two lookbehinds, not a bare
#: `(?<![A-Za-z0-9_-])`.
_D8_LABEL: Final = "workstream/slice id"
_D8_TASK_KEY_RE: Final = re.compile(_docid.TOKEN_LEFT_BOUND + r"W[0-9]+[a-z]?-[0-9]+-[0-9]+\b")
_D8_WORK_KEY_BARE_RE: Final = re.compile(_docid.TOKEN_LEFT_BOUND + r"W[0-9]+[a-z]?\b(?!-[0-9])")
#: A genuine two-segment slice key — the negative lookahead is what stops this from also
#: matching the first two segments of a longer task key (`W<n>-<m>` inside `W<n>-<m>-<k>`).
_D8_SLICE_KEY_RE: Final = re.compile(_docid.TOKEN_LEFT_BOUND + r"W[0-9]+[a-z]?-[0-9]+\b(?!-[0-9])")


def _scan_values(corpus: Corpus, pattern: re.Pattern[str]) -> Counter[str]:
    """Every match of `pattern`, as its own literal text, counted across the whole corpus
    — the identical file/line/`was:`-skip semantics `Corpus.scan` already uses, but
    returning the matched substrings themselves rather than a bare `(lines, files)`
    tally, so a caller can tell a genuinely new value from a larger count of an old one
    (the 2026-09-04 ruling this function exists for, `to-lead.md:1017`)."""
    counts: Counter[str] = Counter()
    for rel in corpus.files:
        skip = corpus.was_lines[rel]
        for i, line in enumerate(corpus.lines[rel]):
            if i in skip:
                continue
            for m in pattern.finditer(line):
                counts[m.group(0)] += 1
    return counts


def _value_set_creation(
    mig: Corpus, ctl: Corpus, pattern: re.Pattern[str]
) -> tuple[bool, str]:
    """Ruling (2026-09-04, `to-lead.md:1017`, amending clause (ii) of the 2026-09-04
    `:455` entry): creation is **a distinct value present in the migrated tree and absent
    from the control**, never a larger raw line count for an already-present value — a
    line count cannot tell mangling/fabrication apart from a generator echoing
    already-disclosed legacy text more than once. Measured, the finding this rule was
    written from: `W37-6` 685->725, `W32-7` 68->78, the value **set** identical both
    times — zero new values, on every alternative this was checked against.

    Returns `(created, note)`. `created` is True iff at least one value `pattern` matches
    in `mig` does not appear anywhere in `ctl` — fatal regardless of any alias-class
    disclosure the alternative's own rules would otherwise apply (clause (i), checked
    before any disclosure, exactly as `_d8_verdict`'s creation check already ran first).
    `note`, non-empty only when `created` is False, lists every value whose *occurrence
    count* grew with the value set otherwise unchanged — clause (ii)'s disclosure line,
    printed, never folded into the verdict. The growth is still owed a cause in the
    ledger by name (clause 3: which generator duplicates it, and whether that is a
    legitimate class-6 echo or a partial-edit (g) defect) — a separate investigation,
    not decided by this function.
    """
    m_counts = _scan_values(mig, pattern)
    c_counts = _scan_values(ctl, pattern)
    new_values = sorted(set(m_counts) - set(c_counts))
    if new_values:
        shown = ", ".join(new_values[:5])
        more = f" (+{len(new_values) - 5} more)" if len(new_values) > 5 else ""
        return True, (
            f"{len(new_values)} new value(s) in the migrated tree, absent from control: "
            f"{shown}{more}"
        )
    grown = sorted(
        (value, c_counts.get(value, 0), count)
        for value, count in m_counts.items()
        if count > c_counts.get(value, 0)
    )
    if not grown:
        return False, ""
    shown_grown = ", ".join(f"{value} {c}->{m}" for value, c, m in grown[:10])
    more_grown = f" (+{len(grown) - 10} more)" if len(grown) > 10 else ""
    return False, (
        f"occurrence count grew for {len(grown)} already-present value(s), value set "
        f"unchanged — not creation (2026-09-04 ruling, `to-lead.md:1017`): "
        f"{shown_grown}{more_grown}"
    )


def _d8_verdict(mig: Corpus, ctl: Corpus, m_lines: int, c_lines: int) -> tuple[str, str]:
    """(d8)'s split. Creation is checked first — a *value-set* comparison (2026-09-04
    ruling, `to-lead.md:1017`, amending the `:455` entry's clause (ii)) — and stays
    REGRESSION regardless of what the slice/task/bare breakdown below would say. An
    occurrence-count increase with the value set unchanged is not creation; it is
    disclosed alongside the slice-key population's own note.

    Task keys join the disclosed component here (Ruling #26, carried from PR #739,
    verify105 — see the module comment above `_D8_LABEL`) rather than staying fatal
    alongside the bare-key check: only a bare work-key remainder is checked before the
    disclosure now.
    """
    created, creation_note = _value_set_creation(mig, ctl, _D8_SLICE_KEY_RE)
    if created:
        return REGRESSION, (
            "the migration introduces a slice-key value the control never had: "
            f"{creation_note} — creation stays REGRESSION even for a disclosed class "
            "(Ruling 105 §A's third alias class)"
        )
    m_bare, bare_files = mig.scan(_D8_WORK_KEY_BARE_RE, skip_fenced=True)
    if m_bare:
        return FAIL, (
            f"{m_bare} bare work-key remainder(s) in {bare_files} file(s) "
            f"(`{_D8_WORK_KEY_BARE_RE.pattern}` — a token_map defect, not this alias class)"
        )
    m_slice, slice_files = mig.scan(_D8_SLICE_KEY_RE)
    c_slice, _ = ctl.scan(_D8_SLICE_KEY_RE)
    m_task, task_files = mig.scan(_D8_TASK_KEY_RE, skip_fenced=True)
    c_task, _ = ctl.scan(_D8_TASK_KEY_RE, skip_fenced=True)
    note = (
        "slice-key and task-key population disclosed, excluded from the zero requirement "
        "(Ruling 105 §A's third alias class; task keys joined by Ruling #26, 2026-09-04 — "
        "no family exists below a slice per NT-0019 §1.2, so a task key has no target by "
        f"design, same ground as a slice key): slice-key {m_slice} line(s) / "
        f"{slice_files} file(s) (`{_D8_SLICE_KEY_RE.pattern}`, control {c_slice}); "
        f"task-key {m_task} line(s) / {task_files} file(s) "
        f"(`{_D8_TASK_KEY_RE.pattern}`, control {c_task}); owner W37-11's citation-form "
        "item — the resolver that renders one (e.g. a slice key -> 'WK-<xxx>, slice "
        "<m>'; a task key -> 'WK-<xxx>, slice <m>, task <k>')"
    )
    if creation_note:
        note += "; " + creation_note
    return DISCLOSE, note


# ---------------------------------------------------------------------------------------
# (d7)'s never-allocated closed class — the deputy's mechanical predicate, 2026-09-04,
# W37-6 exec-ids (relayed via team-lead). §7(d)'s "scoped requirement id" alternative
# still reads non-zero after the citation-rewrite and specification-class fixes, but not
# every remaining hit is a `token_map` miss: a "Next free: `<id>`"/"Highest ids in use:
# <id>" marker in a dated plan or ruling can name a legacy scoped id that was **never
# allocated** under that name at all — a citation to nothing, not a citation the sweep
# forgot. `RL-00144` names the mechanism directly: "A frozen document's next-free marker
# ages the moment anyone else allocates."
#
# The class is decided by a predicate the instrument runs, never by the citing
# sentence's own wording ("`OQ-RATE-8` stays free" is a historical fact, not evidence by
# itself — it is CONSISTENT with never-allocated, but one sample proves nothing about
# the other sixteen tokens this row also carries, which is why every hit is checked
# mechanically below rather than trusted from its citing ruling). A token is
# never-allocated only when ALL FOUR of: zero bold definitions in `docs/specs/*.md`
# (`_discover_requirements`'s own source), zero definition row in `open-questions.md`,
# `roadmap.md` or `docs/audit/register.md` (every other source `_discover_*` reads for a
# requirement or open-question id), and no `old_id` row for it in the migrated tree's
# `docs/REDIRECTS.csv` (confirms the migration itself never allocated it). Any ONE of
# those failing means something actually defines or migrated the id, and the citing line
# is a real `token_map` miss (FAIL) — a token can never be excused into this class merely
# because its citing sentence *sounds* like "never taken".
#
# Terminal, not owed a future fix: NT-0019 allocates bare integers per family (D1/D2), so
# a legacy scoped name that was never allocated can never be allocated *later* either —
# there is no future state in which `token_map["OQ-RATE-8"]` becomes non-empty. Owner:
# "none — closed class". The citing sentence itself is a correct historical statement
# about an id that does not exist and stays exactly as written — Ruling 103 §5.1's fence
# is for an exhibit of a defective FORM, and this is not one.
_D7_LABEL: Final = _docid.SCOPED_REQUIREMENT_ID_LABEL

#: `docs/plans/2026-09-04-w37-6-ruling-107-check-32-36-shared-predicates.md` Entry 1 item 1:
#: the never-allocated predicate's sources and function moved
#: into `_docid` so `audit-docs.py` check 36 can read the identical rule — the four thin
#: wrappers below preserve this module's existing `Corpus`-based signatures for every
#: caller and test already written against them, delegating to `_docid`'s pure,
#: `repo_root`-based versions (which read a tree directly rather than through a `Corpus`,
#: since check 36's single-snapshot sweep never builds one).


def _scoped_id_bold_defined(token: str, ctl: Corpus) -> bool:
    """True if `token` is bold-defined (`**token**`) anywhere in the control tree's
    `docs/specs/*.md` — `_discover_requirements`'s own source."""
    return _docid.scoped_id_bold_defined(token, ctl.tree)


def _scoped_id_defined_elsewhere(token: str, ctl: Corpus) -> bool:
    """True if `token` has a genuine definition row in `open-questions.md`, `roadmap.md`
    or `docs/audit/register.md` — a `next free:`-marker MENTION on the same line, before
    the token, is not a definition; everything else that names the token counts."""
    return _docid.scoped_id_defined_elsewhere(token, ctl.tree)


def _scoped_id_has_redirect(token: str, mig: Corpus) -> bool:
    """True if `token` has an `old_id` row in the migrated tree's `docs/REDIRECTS.csv`."""
    return _docid.scoped_id_has_redirect(token, mig.tree)


def _scoped_id_is_never_allocated(token: str, mig: Corpus, ctl: Corpus) -> bool:
    """The deputy's mechanical predicate, applied to one token."""
    return _docid.is_scoped_id_never_allocated(
        token, definition_root=ctl.tree, redirect_root=mig.tree
    )


#: (d7)'s remaining named collision, ruled 2026-09-05 (W37-6 channel): `_scoped_id_is_
#: never_allocated` is per-TOKEN, and `FR-PLAT-4` is genuinely allocated (`FR-PLAT-1..4`
#: is real production usage, `docs/REDIRECTS.csv` carries its row) — so it fails as a
#: "real" hit everywhere the literal string appears, including `scripts/doc-id.py`'s own
#: `_expand_range` docstring, where it names the same string as a worked example of an
#: UN-ascending range (`` `FR-PLAT-4..1` ``, deliberately backwards, to illustrate the
#: "not ascending" branch) — never a citation to the real requirement at all.
#:
#: **Corrected, same day: a table naming `FR-PLAT-4` by file and token is the forbidden
#: per-file exemption**, the maintainer's own standing rule (a resistant file goes to
#: W37-11, never a name-by-name allowlist) — caught before merge on the deputy's own
#: re-reading of `origin/main`'s `is_scoped_id_never_allocated`: every existing branch of
#: (d7)'s disclosed class decides **per token, from content** (a bold spec definition, a
#: line-content test, a `REDIRECTS.csv` lookup), never by naming a token. The class this
#: joins is **framework self-reference**: a scoped id inside a `scripts/*.py` file's own
#: Python comment or docstring is that file talking *about* the citation-form grammar,
#: never citing a requirement — the identical shape as the 21 self-referential hits this
#: row's own control-tree population already carries (this workstream's source and
#: planning docs quoting the bug pattern they describe). `_is_framework_self_reference`
#: is a property of the line and the file, computable anywhere a Python source line
#: exists, not a lookup against a table of names.
def _python_comment_or_string_lines(text: str) -> frozenset[int]:
    """0-based line numbers inside a `#` comment or a triple-quoted string (module or
    function docstring, or any other `\"\"\"`/`'''`-delimited literal) in Python source
    `text`.

    A line-oriented state machine, not a full tokenizer: it toggles "inside a triple-
    quoted string" on each delimiter it finds, in source order, and treats every line
    touched by an open, a close, or a fully-enclosed span as one of this class's members.
    Good enough for this repository's own sources, which use triple-quoted strings only
    for docstrings and comment-style exhibits, never for run-time string building that
    would confuse the toggle — verified below against the real corpus rather than assumed
    (the acceptance test is the member count, not the mechanism's own plausibility).
    """
    result: set[int] = set()
    in_triple: str | None = None
    for i, line in enumerate(text.splitlines()):
        if in_triple is None and line.strip().startswith("#"):
            result.add(i)
            continue
        touched = in_triple is not None
        pos = 0
        while True:
            if in_triple is None:
                idx_d = line.find('"""', pos)
                idx_s = line.find("'''", pos)
                candidates = [x for x in (idx_d, idx_s) if x != -1]
                if not candidates:
                    break
                start = min(candidates)
                in_triple = '"""' if start == idx_d else "'''"
                touched = True
                pos = start + 3
            else:
                end = line.find(in_triple, pos)
                if end == -1:
                    break
                in_triple = None
                pos = end + 3
        if touched:
            result.add(i)
    return frozenset(result)


#: The second half of framework self-reference (team-lead, 2026-09-05, converging
#: independently with the deputy's ruling above): this workstream's own planning/ruling
#: docs, in prose, quoting a citation-form SHAPE as an exhibit — `` `WK-944C` ``,
#: `` `NFR-775/14` `` — rather than citing a requirement. `docs/plans/` and
#: `docs/rulings/` are this workstream's own record of its work on the migration tooling
#: itself, not the platform's requirements corpus (`docs/specs/`) or a real citation
#: source. **`docs/findings/` is deliberately NOT in this tuple** (corrected 2026-09-05,
#: team-lead's own re-reading): a migration's own move can land inside a directory this
#: tuple names — `docs/audit/register.md` (a REAL citation source, and the file that
#: held today's one real defect) becomes `docs/findings/register.md` on the migrated
#: tree, the one this predicate actually scans. `docs/findings/` currently holds zero
#: members of this class (measured against the real corpus before this correction), so
#: dropping it costs nothing; naming `register.md` itself in an exclusion would have been
#: the forbidden per-file table from the other direction.
_W37_PLANNING_DOC_DIRS: Final = ("docs/plans/", "docs/rulings/")


def _is_planning_doc_pattern_exhibit(
    rel: str, mig: Corpus, ctl: Corpus, line: str, matched: str
) -> bool:
    """True if `rel` is one of this workstream's own planning/ruling docs, `matched`
    appears **inside some backtick-quoted span** on `line`, AND `matched` is never
    allocated (team-lead's hardening, 2026-09-05: "limb 2 discloses EXHIBITS, and an
    exhibit is not a real id" — a real id surviving in old form inside a backtick span
    anywhere is a miss, not an exhibit, and must stay fatal regardless of directory).

    Every self-referential exhibit found in the real corpus takes the backtick form,
    though not always with nothing else in the span: `` `FR-680..4` `` alone, but also
    `` `WK-944C/...` `` (a quoted before/after example) and `` `WK-944C/OpenTelemetry` ``
    (the whole corrupted string, quoted). Splitting on the backtick character and
    checking every odd-indexed segment (the parts a Markdown reader renders as code)
    covers all three. The never-allocated conjunct is the actual guard against a real
    citation surviving unswept in backtick form: `_scoped_id_is_never_allocated` reuses
    (d7)'s own three-source check (bold spec definition, another definition source, a
    `REDIRECTS.csv` row) generically — meaningless sources for a WK-shaped token simply
    never match, so it still reads "never allocated" for a genuine WK exhibit, while a
    real `FR`/`NFR`/`OQ`/`DEP` id would be caught by at least one of the three.
    """
    if not (rel.startswith(_W37_PLANNING_DOC_DIRS) and rel.endswith(".md")):
        return False
    segments = line.split("`")
    if not any(matched in segment for segment in segments[1::2]):
        return False
    return _scoped_id_is_never_allocated(matched, mig, ctl)


def _framework_self_reference_lines(rel: str, mig: Corpus) -> frozenset[int]:
    """0-based line numbers in `rel` that are framework self-reference — inside a Python
    comment or docstring of a `scripts/*.py` or `tests/*.py` file, this repository's own
    tooling discussing or testing a legacy-id shape rather than citing a requirement.
    Empty for every other file, so a caller can call this unconditionally per file without
    its own path check. Does not cover `_is_planning_doc_pattern_exhibit`'s markdown
    half, which needs the matched substring itself, not just the line index — callers
    combine both."""
    if not ((rel.startswith("scripts/") or rel.startswith("tests/")) and rel.endswith(".py")):
        return frozenset()
    return _python_comment_or_string_lines("\n".join(mig.lines[rel]))


def _is_framework_self_reference(
    rel: str, tree: Corpus, mig: Corpus, ctl: Corpus, line_index: int, matched: str
) -> bool:
    """The one combined predicate (team-lead's ruling, 2026-09-05: "build one predicate
    and let it cover FR-PLAT-4, the WK hits, and the fixture tokens together"): a Python
    comment/docstring line under `scripts/`/`tests/` (limb 1 — a real id MAY be disclosed
    here; framework source text is exactly where a worked example like `FR-PLAT-4`
    lives), or a backtick-quoted, never-allocated pattern exhibit in this workstream's
    own planning docs (limb 2 — a real id may NOT be disclosed here; limb 2 discloses
    exhibits, and an exhibit is not a real id — team-lead's hardening, same date). Used
    identically by (d7)'s real-hit classification and (g)'s WK-shape scan — one
    mechanism, not two, for one class.

    `tree` is whichever `Corpus` the caller is scanning (`mig` when scanning the
    migrated tree, `ctl` when scanning the control tree for the row's own baseline) — its
    lines are what `line_index` indexes and what limb 1 reads. `mig`/`ctl` are always the
    same fixed pair regardless of `tree`, because limb 2's never-allocated conjunct asks
    "is this token a real id at all", which does not depend on which tree the occurrence
    was found in.
    """
    return (
        line_index in _framework_self_reference_lines(rel, tree)
        or _is_planning_doc_pattern_exhibit(rel, mig, ctl, tree.lines[rel][line_index], matched)
    )


def _box_end_refused(
    docid: Any, active_map: Mapping[str, str], token: str, line: str, m: re.Match[str],
) -> bool:
    """True iff `doc-id.py`'s box-end comma-continuation refusal (`_bare_comma_tail_
    resolves`) is the reason `token` still sits unrewritten on `line` at match `m` — the
    SAME function the rewriter itself calls to decide the refusal, called here rather
    than re-implemented, so no caller of this helper can ever disclose a site the
    rewriter did not itself refuse.

    **Ruling (lead, 2026-09-06), extending the deputy's 2026-09-06 ruling to its full
    scope:** that ruling is written about a *shape* — "a token immediately followed by a
    bare comma-digit tail that resolves against the token's own prefix" — not about
    (d7)'s family. `_bare_comma_tail_resolves` lives inside `_expand_compound`/
    `_expand_range`, the general rewriter for every id family `doc-id.py` migrates, so a
    row whose own alternative pattern matches a family the general rewriter also covers
    (found live: (d6)'s `ADR-0[0-9]{3}`, `docs/skills-map.md:92`'s `ADR-0004, 03 ...`,
    where `03` resolves as the real `ADR-0003`) can be refused by the identical
    mechanism (d7) already discloses. Extracted here as ONE predicate every d-row reads,
    never a per-row copy that happens to agree today — `_d7_disclosed_or_fail`'s own
    third class and `_box_end_only_residue_or_none` (the generic d-row path, below) both
    call this, not two independent readings of the rule.

    `token not in active_map` is the SAME precondition the rewriter's own sweep requires
    before it ever calls `_bare_comma_tail_resolves` at all — a token with no mapping
    could not have been rewritten in the first place, so it is never this refusal's
    doing.
    """
    prefix_match = re.search(r"\d+$", token)
    if prefix_match is None:
        return False
    prefix = token[: prefix_match.start()]
    base_width = len(token) - len(prefix)
    if token not in active_map:
        return False
    end_pos = (docid._compound_token_re(token).match(line, m.start()) or m).end()
    return docid._bare_comma_tail_resolves(prefix, base_width, active_map, line, end_pos)


def _box_end_only_residue_or_none(
    docid: Any, mig: Corpus, ctl: Corpus, pattern: re.Pattern[str],
) -> tuple[str, str] | None:
    """The generic d-row path for the SAME disclosed class `_d7_disclosed_or_fail`'s
    third class already covers, for every alternative that has no bespoke verdict
    function of its own (Ruling, lead, 2026-09-06 — see `_box_end_refused`'s own
    docstring for the grounds). Returns `None` when box-end refusal has nothing to say
    about this row at all (no hit is a refusal), leaving `_verdict_on_zero`'s own
    verdict and note untouched. Returns `(FAIL, note-naming-the-real-hit)` when at least
    one hit IS a refusal but at least one other is not — the mandatory positive control
    this class must never swallow, named rather than left in `_verdict_on_zero`'s own
    silent empty-string FAIL note so a reviewer can see the real miss did not vanish
    into the new disclosure. Returns `(DISCLOSE, note)` only when EVERY hit on every
    still-matching line is a refusal this same predicate confirms — never a blanket
    disclosure trusting that a hit merely resembles the shape.
    """
    active_map = _redirects_token_map(mig)
    real_hits: list[str] = []
    refusal_hits: list[str] = []
    for rel in mig.files:
        skip = mig.was_lines[rel] | mig.fenced_lines[rel]
        for i, line in enumerate(mig.lines[rel]):
            if i in skip:
                continue
            for m in pattern.finditer(line):
                token = m.group(0)
                if _box_end_refused(docid, active_map, token, line, m):
                    refusal_hits.append(f"{token} ({rel}:{i + 1})")
                else:
                    real_hits.append(f"{token} ({rel}:{i + 1})")
    if not refusal_hits:
        return None
    if real_hits:
        shown = "; ".join(real_hits[:10])
        more = f" (+{len(real_hits) - 10} more)" if len(real_hits) > 10 else ""
        return FAIL, (
            f"{len(real_hits)} hit(s) are a genuine miss, not disclosed — "
            f"{len(refusal_hits)} other hit(s) on this row ARE box-end comma-continuation "
            "refusals, but a real miss still fails the whole row (this row has no "
            f"per-line partial disclosure, the same rule (d7) applies): {shown}{more}."
        )
    shown = "; ".join(refusal_hits[:10])
    more = f" (+{len(refusal_hits) - 10} more)" if len(refusal_hits) > 10 else ""
    return DISCLOSE, (
        f"{len(refusal_hits)} hit(s) are box-end comma-continuation refusals — "
        "`doc-id.py`'s `_bare_comma_tail_resolves` (the SAME function the rewriter "
        "itself calls to decide this, not a re-implementation) says each token is "
        "immediately followed by a bare comma-digit tail that resolves against its own "
        "prefix, a genuine continuation risk the rewriter refused rather than partially "
        "rewrite, leaving a real, allocated citation in its legacy form on purpose "
        "(Ruling, lead, 2026-09-06 — the same class (d7) discloses, extended to every "
        f"d-row the general rewriter covers). Owner: W37-6. {shown}{more}."
    )


def _d7_disclosed_or_fail(docid: Any, mig: Corpus, ctl: Corpus) -> tuple[str, str]:
    """(d7)'s non-zero population, split by the never-allocated predicate. Reads the
    identical migrated-tree population `rows_d`'s own `mig.scan(pattern, skip_fenced=
    True)` counts (`was:` and fenced lines excluded the same way), so this function's own
    line count matches the row's reported `migrated` figure exactly.

    Every token on every still-matching line is checked; ONE real hit (a token that is
    not disclosed under any of this function's classes) fails the whole row, named — this
    is deliberately not a line-by-line partial disclosure, because a row mixing a real
    miss with disclosed residue would read as clean at a glance while still hiding the
    real miss.

    **Third disclosed class, co-extensive by identity (Ruling, W37-6, 2026-09-06):** a
    token immediately followed by a bare comma-digit tail that resolves against the
    token's own prefix is exactly the shape `doc-id.py`'s box-end comma-continuation
    refusal (`_bare_comma_tail_resolves`) leaves whole rather than partially rewrite —
    the SAME function decides both sides, called here rather than re-implemented, so this
    class can never disclose a site the rewriter did not itself refuse. Before that
    refusal existed, the base was rewritten and the tail orphaned (`, 10..13` citing
    nothing) and this row never fired at all, since bare digits do not match its own
    pattern — the citations were unmigrated either way. Legacy-but-intact beats mangled:
    `REDIRECTS.csv` resolves one and nothing resolves the other, but the row must say so
    rather than stay silently green on the worse output.
    """
    d7_pattern = re.compile(r"\b(?:FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+\b")
    active_map = _redirects_token_map(mig)
    real_hits: list[str] = []
    disclosed_lines = 0
    disclosed_files: set[str] = set()
    self_ref_hits: list[str] = []
    refusal_hits: list[str] = []
    for rel in mig.files:
        skip = mig.was_lines[rel] | mig.fenced_lines[rel]
        line_disclosed = False
        for i, line in enumerate(mig.lines[rel]):
            if i in skip:
                continue
            matches = list(d7_pattern.finditer(line))
            if not matches:
                continue
            for m in matches:
                token = m.group(0)
                prefix_match = re.search(r"\d+$", token)
                if prefix_match is None:
                    real_hits.append(f"{token} ({rel}:{i + 1})")
                    continue
                if _scoped_id_is_never_allocated(token, mig, ctl):
                    line_disclosed = True
                elif _is_framework_self_reference(rel, mig, mig, ctl, i, token):
                    line_disclosed = True
                    self_ref_hits.append(f"{token} ({rel}:{i + 1})")
                elif _box_end_refused(docid, active_map, token, line, m):
                    line_disclosed = True
                    refusal_hits.append(f"{token} ({rel}:{i + 1})")
                else:
                    real_hits.append(f"{token} ({rel}:{i + 1})")
        if line_disclosed:
            disclosed_files.add(rel)
            disclosed_lines += sum(
                1
                for i, line in enumerate(mig.lines[rel])
                if i not in skip and d7_pattern.search(line)
            )
    if real_hits:
        shown = "; ".join(real_hits[:10])
        more = f" (+{len(real_hits) - 10} more)" if len(real_hits) > 10 else ""
        return FAIL, (
            f"{len(real_hits)} hit(s) name a token with a real definition or an "
            f"existing `docs/REDIRECTS.csv` row — a genuine `token_map` miss, not the "
            f"never-allocated class: {shown}{more}"
        )
    self_ref_shown = "; ".join(self_ref_hits[:10])
    self_ref_more = f" (+{len(self_ref_hits) - 10} more)" if len(self_ref_hits) > 10 else ""
    self_ref_note = (
        f" {len(self_ref_hits)} of those line(s) join a second, distinct disclosed "
        "class — **framework self-reference**: a token that IS genuinely allocated "
        "elsewhere but the matched line is inside a `scripts/*.py`/`tests/*.py` file's "
        "own Python comment or docstring, or a backtick-quoted pattern exhibit in this "
        "workstream's own planning docs, discussing or testing the citation-form "
        "grammar rather than citing a requirement (a property of the line and the "
        "file, `_is_framework_self_reference`, never a table naming which token or "
        "file — ruled 2026-09-05, W37-6 channel). "
        "**The trade, stated rather than left implicit (team-lead, 2026-09-05):** "
        "every legacy id on a self-referential line is disclosed, including any that "
        "would turn out to be genuinely stale — illustrative-versus-stale inside the "
        "framework's own comments is not mechanically decidable, and framework "
        "comments are not published contract. This line's own count IS that trade's "
        f"size: {self_ref_shown}{self_ref_more} — every self-referential occurrence "
        "with a real definition or redirect, which is what this disclosure hides. A "
        "self-referential occurrence naming a token with NO real definition costs "
        "nothing extra: it is already the never-allocated class above, with or "
        "without this second class."
        if self_ref_hits
        else ""
    )
    refusal_shown = "; ".join(refusal_hits[:10])
    refusal_more = f" (+{len(refusal_hits) - 10} more)" if len(refusal_hits) > 10 else ""
    refusal_note = (
        f" {len(refusal_hits)} of those line(s) join a third, distinct disclosed "
        "class — **box-end comma-continuation refusal**: `doc-id.py`'s "
        "`_bare_comma_tail_resolves` (the SAME function the rewriter itself calls to "
        "decide this, not a re-implementation) says the token is immediately followed "
        "by a bare comma-digit tail that resolves against its own prefix — a genuine "
        "continuation risk the rewriter refused rather than partially rewrite, "
        "leaving this real, allocated citation in its legacy form on purpose (Ruling, "
        "W37-6, 2026-09-06). Owner: W37-6. This is not a closed class the way "
        "never-allocated is: `REDIRECTS.csv` can still resolve every one of these, and "
        "each is governed by its own W37-11 per-file ceiling entry, unlike the "
        f"never-allocated class above. This line's own count: {refusal_shown}"
        f"{refusal_more}."
        if refusal_hits
        else ""
    )
    return DISCLOSE, (
        f"every one of {disclosed_lines} line(s) / {len(disclosed_files)} file(s) "
        "names only a legacy scoped-form id with zero definition rows in every source "
        "`_discover_*` reads (`docs/specs/*.md`, `docs/open-questions.md`, "
        "`docs/roadmap.md`, `docs/audit/register.md`) and no `old_id` row in "
        "`docs/REDIRECTS.csv` — the closed never-allocated class (deputy's mechanical "
        "predicate, 2026-09-04, W37-6 exec-ids). Terminal: NT-0019 allocates bare "
        "integers per family, so a legacy scoped name that was never allocated can "
        "never be allocated later either. Owner: none — closed class. The citing "
        "sentence stays exactly as written; Ruling 103 §5.1's fence is for a "
        "defective-form exhibit, not a correct historical statement about an id that "
        f"does not exist.{self_ref_note}{refusal_note}"
    )


def _path_alternative_verdict(
    mig: Corpus, pattern: re.Pattern[str],
) -> tuple[int, int, int, int]:
    """The deputy's ruling (W37-6 channel, 2026-09-04): Ruling 105 §A's disclosed-alias
    pattern applied to a §7(d) *path* alternative. A match immediately naming a real
    moved file — present in this run's own `docs/REDIRECTS.csv` `old_path` column — is
    fatal: the citation-inverse mechanism owns exactly that shape (a known `(old_path,
    new_path)` pair) and should have repointed it. A match naming no such file has no
    pair to repoint to at all — a bare directory mention with no single successor
    (`docs/audit/`, which dissolves into four: `_README_LEGACY_DIR_MOVES`'s own
    docstring) or a dated prefix with nothing identifiable after it (`docs/plans/2026-`
    alone). Rewriting the sentence around either would be a meaning edit
    `docs/plans/README.md`'s write-once rule forbids inside a frozen file, so this row
    discloses the count rather than demanding zero of it — owner W37-11's citation-form
    item, the same shape (d2)/(d8) already use.

    Wrap-tolerant by the same window `doc-id.py`'s `_rejoin_wrapped_path_citations`
    reads (this line concatenated with the next): a real file's own citation surviving
    as a still-wrapped, still-unrewritten token must stay fatal, not quietly reclassify
    as "no path present" merely because the forward sweep's own wrap fix missed this one
    shape.

    Two exclusions, found live 2026-09-05 while retiring rows (d9)-(d12)'s own fatal
    population, both applied before any line is even classified:

    * **A same-path `docs/REDIRECTS.csv` row is not a moved file.** `old_path ==
      new_path` records a token rename made *inside* a file (`W1` -> `WK-954` inside
      `docs/roadmap.md`, which never moved), reusing the CSV's `old_path`/`new_path`
      columns for a different fact. Counting `docs/roadmap.md` as a "real moved file"
      made an unrelated, correct, unchanged citation to it — sitting in the same
      two-line window as a genuinely stale (or even a bare-directory, no-successor)
      match — flip a DISCLOSE-worthy or entirely benign line to FATAL by coincidence of
      proximity, not because the matched text named anything that moved.
    * **A vendored skill's own files are never swept.** `doc-id.py`'s `_is_vendored_exempt`
      excludes everything beneath a `_docid._VENDORED_SKILLS` directory except its
      manifest, by ruling (NT-0019 §1.5, Ruling 69/76) — "vendored files stay as
      upstream wrote them" (`CLAUDE.md` §12). A citation inside one can never be
      repointed by design, so it is not this row's population to demand zero of.

    Returns `(fatal_lines, fatal_files, disclosed_lines, disclosed_files)`.
    """
    fatal_by_file, disclosed_by_file = _path_alternative_hits_by_file(mig, pattern)
    return (
        sum(fatal_by_file.values()),
        len(fatal_by_file),
        sum(disclosed_by_file.values()),
        len(disclosed_by_file),
    )


def _path_alternative_hits_by_file(
    mig: Corpus, pattern: re.Pattern[str],
) -> tuple[Mapping[str, int], Mapping[str, int]]:
    """`_path_alternative_verdict`'s own per-file breakdown, factored out so a caller that
    needs *which file* (the W37-11 residue ceiling) reads the identical classification a
    caller that only needs the row's aggregate figure does — one rule, not two readings of
    it (Ruling 103 §1.8's "two implementations of one rule that are never compared are two
    rules", the same reasoning `fenced_line_numbers` was shared for above).

    Returns `(fatal_lines_by_relpath, disclosed_lines_by_relpath)`; a file with zero hits of
    a kind is absent from that kind's mapping, never present with value 0.
    """
    real_paths = frozenset(
        old for old, new in _redirect_map(mig.tree).items() if old != new
    )
    fatal_by_file: dict[str, int] = {}
    disclosed_by_file: dict[str, int] = {}
    for rel in mig.files:
        if _docid.is_split_source_index(rel):
            continue
        if _docid.is_vendored(mig.tree / rel, mig.tree):
            continue
        skip = mig.was_lines[rel]
        lines = mig.lines[rel]
        file_fatal = file_disclosed = 0
        for i, line in enumerate(lines):
            if i in skip or not pattern.search(line):
                continue
            window = line + (lines[i + 1] if i + 1 < len(lines) else "")
            if any(p in window for p in real_paths):
                file_fatal += 1
            else:
                file_disclosed += 1
        if file_fatal:
            fatal_by_file[rel] = file_fatal
        if file_disclosed:
            disclosed_by_file[rel] = file_disclosed
    return fatal_by_file, disclosed_by_file


def rows_d(
    docid: Any,
    mig: Corpus,
    ctl: Corpus,
    record: "Sequence[ResidueEntry]" = (),  # noqa: UP037 -- ResidueEntry defined later
) -> list[Row]:
    rows: list[Row] = []
    for i, (label, pattern) in enumerate(D_ALTERNATIVES, start=1):
        m_lines, m_files = mig.scan(pattern, skip_fenced=True)
        c_lines, c_files = ctl.scan(pattern, skip_fenced=True)
        companions, gating = _companions_for(label, pattern, mig, ctl)
        #: Fatal residue by file — the W37-11 ceiling's own measurement (`Row.residue`).
        #: A path alternative's fatal hit is its per-file breakdown of the identical
        #: classification its verdict already uses; every other alternative's is its
        #: plain per-file line count. `cls` is this row's own key (`f"d{i}"`) — every
        #: (d) alternative is one class, no sub-bucket. Populated unconditionally: a row
        #: the ceiling is not governing for (no record entry names its key) simply
        #: carries data no comparison ever reads.
        row_key = f"d{i}"
        hits_by_file = (
            _path_alternative_hits_by_file(mig, pattern)[0]
            if label in D_PATH_LABELS
            else mig.hits_by_file(pattern, skip_fenced=True)
        )
        residue_by_file = {
            (rel, row_key): count for rel, count in hits_by_file.items()
        }
        if label == _D8_LABEL:
            verdict, note = _d8_verdict(mig, ctl, m_lines, c_lines)
        else:
            # 2026-09-04 ruling (`to-lead.md:1017`): creation is a *distinct value*
            # present in the migrated tree and absent from control, checked before any
            # alternative's own disclosure — one rule across the whole row, `_d8_verdict`
            # included, not (d8) alone. An occurrence-count increase with the value set
            # unchanged is not creation; it is a disclosure line appended to whatever
            # verdict the alternative would otherwise get, never folded into it.
            created, creation_note = _value_set_creation(mig, ctl, pattern)
            if created:
                verdict = REGRESSION
                note = (
                    "the migration introduces a value this alternative's own pattern "
                    f"never matched in the control: {creation_note}"
                )
            elif label in D_DISCLOSED:
                verdict = DISCLOSE
                note = (
                    "excluded from the zero requirement, count disclosed "
                    f"({D_DISCLOSED_CITATION.get(label, 'ruling pending')})"
                )
                if creation_note:
                    note += "; " + creation_note
            elif label == _D7_LABEL and m_lines > 0:
                verdict, note = _d7_disclosed_or_fail(docid, mig, ctl)
                if creation_note:
                    note += "; " + creation_note
            elif label in D_PATH_LABELS:
                # The deputy's ruling (W37-6 channel, 2026-09-04): a path alternative's
                # disclosure is per-match, not per-alternative — `_path_alternative_verdict`
                # has the full reasoning. A fatal hit (a real file's own citation, still
                # unrewritten) always wins over a disclosed one in the same run: the row
                # stays red until every genuinely repointable citation is repointed, no
                # matter how many disclosed, no-successor mentions sit alongside it.
                fatal_lines, fatal_files, disc_lines, disc_files = (
                    _path_alternative_verdict(mig, pattern)
                )
                if fatal_lines:
                    verdict = FAIL
                    note = (
                        f"{fatal_lines} line(s) / {fatal_files} file(s) still name a "
                        "real moved file present in this run's own docs/REDIRECTS.csv "
                        "old_path column (a same-path old_path==new_path token-rename "
                        "row is not a moved file and does not count; a family "
                        "split-source `docs/<family>/INDEX.md` and a vendored skill's "
                        "own files are excluded from this scan entirely, "
                        "`_docid.is_split_source_index`/`_docid.is_vendored` — 2026-09-05, "
                        "rows (d9)-(d12)) — the citation-inverse mechanism should have "
                        "repointed these and did not"
                    )
                    if disc_lines:
                        note += (
                            f"; {disc_lines} line(s) / {disc_files} file(s) additionally "
                            "disclosed (Ruling 105 §A's pattern, owner W37-11's "
                            "citation-form item) — no real file behind the match, "
                            "excluded from the zero requirement"
                        )
                elif disc_lines:
                    verdict = DISCLOSE
                    note = (
                        f"{disc_lines} line(s) / {disc_files} file(s) name no real "
                        "moved file (docs/REDIRECTS.csv has no old_path entry behind "
                        "the match) — a bare directory mention with no single successor "
                        "(e.g. docs/audit/, which dissolves into four), or a dated "
                        "prefix with nothing identifiable after it; excluded from the "
                        "zero requirement, owner W37-11's citation-form item (Ruling "
                        "105 §A's pattern)"
                    )
                else:
                    verdict, note = PASS, ""
                if creation_note:
                    note = (note + "; " if note else "") + creation_note
            else:
                verdict, note = _verdict_on_zero(m_lines, mig.n_lines, control=c_lines)
                if verdict == FAIL:
                    # Ruling (lead, 2026-09-06): the box-end disclosure is not (d7)'s
                    # property, it belongs to every d-row the general rewriter covers.
                    # Found live: (d6) FAILs on docs/skills-map.md's `ADR-0004, 03 ...`,
                    # refused whole because `03` resolves as the real `ADR-0003`.
                    box_end_verdict = _box_end_only_residue_or_none(docid, mig, ctl, pattern)
                    if box_end_verdict is not None:
                        verdict, note = box_end_verdict
                if creation_note:
                    note = (note + "; " if note else "") + creation_note
        if verdict == FAIL and _residue_fully_governed(residue_by_file, record):
            # The box-end ruling (2026-09-05): a `FAIL` this general mechanism cannot
            # resolve closes by DISCLOSE once, and only once, every one of its fatal hits
            # is filed and ceilinged in the W37-11 record — never merely because the
            # record is silent on it (`_residue_fully_governed` refuses that case).
            verdict = DISCLOSE
            total = sum(residue_by_file.values())
            note = (note + "; " if note else "") + (
                f"{total} hit(s) filed and ceilinged in docs/audit/w37-11-record.md — "
                "governed residue the general migration mechanism cannot resolve, "
                "disclosed per file rather than special-cased in this module"
            )
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
                    "(`_docverify.was_field_line_numbers`), minus lines inside a fenced "
                    "code block (`_docverify.fenced_line_numbers` — Ruling 103 §5.1's "
                    "fence clause, extended to row (d)'s corpus 2026-09-04, W37-6 "
                    "exec-ids: an illustrative exhibit kept byte-exact inside a fence is "
                    "not a citation); taken verbatim, by index, "
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
                residue=residue_by_file,
            )
        )
    return rows


# ---------------------------------------------------------------------------------------
# (e) no padded id in prose — Ruling 103's four conjuncts
# ---------------------------------------------------------------------------------------

#: **Conjunct 1**'s exact-width regex, moved into `_docid` per
#: `docs/plans/2026-09-04-w37-6-ruling-107-check-32-36-shared-predicates.md` Entry 2 item 1
#: so `audit-docs.py` check 32 can read the identical assembled pattern rather than
#: reassembling it from the same two symbols in a second place — re-exported here under
#: this module's existing name for every caller and test already written against it.
_PADDED_ID_RE: Final = _docid._PADDED_ID_RE

#: **Conjunct 0's** fence tracking. Ruled by the decision-maker: without it, a record
#: documenting a padding defect must corrupt its own evidence to pass the lint, which is
#: the check-19 distortion arriving by a new route. Fencing preserves evidence byte-exact
#: and keys no exemption to any document — a padded id **outside** a fence is a violation in
#: every document, the ruling's own included.
_FENCE_RE: Final = re.compile(r"^\s{0,3}(```|~~~)")

#: **Conjunct 2's** stripping step, boundary set and line-locator strip, and the
#: `_in_path_context` predicate itself, moved into `_docid` per
#: `docs/plans/2026-09-04-w37-6-ruling-107-check-32-36-shared-predicates.md` Entry 2 item 1
#: so `audit-docs.py` check 32 can read the identical predicate rather than a private copy.
#: Re-exported here under their existing names for this module's own callers and tests.
_MD_EMPHASIS_RE: Final = _docid._MD_EMPHASIS_RE
_TOKEN_BOUNDARY_RE: Final = _docid._TOKEN_BOUNDARY_RE
_TRAILING_LINE_LOCATOR_RE: Final = _docid._TRAILING_LINE_LOCATOR_RE
_in_path_context = _docid._in_path_context


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
    #: 0-based ordinal of this occurrence among all `_PADDED_ID_RE` matches on the line, in
    #: left-to-right order. Needed because two occurrences of the same padded id can share
    #: one line — a filename exhibit followed later by the bare equivalence-list id is
    #: `document-ids.md`'s own rule-3 sentence — and conjunct 2 used to re-locate a hit in
    #: the cleaned line by *text* (`m.group(0) == hit.token`), taking the first same-text
    #: match's path-context verdict for every hit sharing that text. The bare occurrence
    #: then inherited the filename occurrence's TRUE verdict and was wrongly excused — a
    #: false negative that suppresses a real violation. `seq` lets conjunct 2 re-locate
    #: this hit by its own position instead of by text.
    seq: int


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
            for seq, h in enumerate(hits):
                after_corpus.append(PaddedHit(rel, i + 1, h.group(0), line.strip(), seq))
    after_path: list[PaddedHit] = []
    for hit in after_corpus:
        # Conjunct 2 is tested on the line with markdown emphasis stripped, so a bold
        # marker inside a path cannot hide the path from the path test. Stripping
        # asterisks (and `.strip()`'s own whitespace trim, above) never adds, removes or
        # reorders a `_PADDED_ID_RE` match — they sit at token boundaries, never inside
        # one — so the cleaned line's `seq`-th match is still this hit's own occurrence.
        cleaned = _MD_EMPHASIS_RE.sub("", hit.line)
        cleaned_hits = list(_PADDED_ID_RE.finditer(cleaned))
        m = cleaned_hits[hit.seq] if hit.seq < len(cleaned_hits) else None
        prose = not (m is not None and _in_path_context(cleaned, m.start(), m.end()))
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
            f"conjunct 2 — not path-shaped (`_docid._in_path_context`) after stripping "
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
#:
#: Task #30's range ruling (W37-6 channel `:526`) adds the `..` alternative: a range
#: citation's base token rewritten alone, with its `..end` tail orphaned, produces the
#: identical shape one level up — a *numeric* module segment followed by `..` and a bare
#: number (`FR-680..4`) is exactly as meaningless as `NFR-775/14`, and for the same
#: reason: a rewrite matched inside a longer citation and stopped. Both alternatives share
#: the one leading clause (`\b(FR|NFR|OQ|DEP)-[0-9]+`) rather than repeating it, so the two
#: shapes cannot drift apart on what counts as "a numeric module segment".
#:
#: #720's cause4 (W37-6 channel `:845`) adds the `WK-\d+[A-Za-z]` alternative: the same
#: `_compound_token_re` boundary defect #721 fixed also let a mapped `W<n>` token match as
#: a bare prefix of a longer run of word characters with no separator at all —
#: `"W3C/OpenTelemetry…"` came out `"WK-944C/OpenTelemetry…"`, a fabricated identifier no
#: `FR|NFR|OQ|DEP` alternative could ever see (`W`/`WK` was never in its family list). A
#: real lowercase slice suffix (`W<n>a`, `WK-949a`) is not this shape — the corpus's own
#: convention for a genuine continuation is lowercase, per `_WORK_FAMILY_TOKEN_RE`'s own
#: `[a-z]?` — so the alternative is anchored to an *uppercase* letter, which a real slice
#: id never produces and a corruption like `W3C` always does.
MANGLED_CITATION_RE: Final = re.compile(
    r"\b(?:(?:FR|NFR|OQ|DEP)-[0-9]+(?:/[0-9]+|\.\.[0-9]+)|WK-[0-9]+[A-Z])"
)

#: The pre-migration compound form: the population at risk. Printed as this row's
#: denominator, so "391 mangled" is read against "423 at risk" rather than against nothing.
COMPOUND_CITATION_RE: Final = re.compile(r"\b(FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+/[0-9]+")

#: g1's FR/NFR/OQ/DEP alternative, narrowed to **provenance** (deputy disposition,
#: 2026-09-05 13:35 BST, superseding this row's own comment above for that one
#: alternative only — Ruling 102 §2's text is untouched; the narrowing restores what its
#: own rationale meant under a scheme where a *shape* test could still tell a corrupted
#: rewrite from a correct one). A pure-numeric id scheme means a correctly-expanded
#: compound (`_expand_compound`'s own designed output, `NFR-799/798`) wears the identical
#: shape a corrupted rewrite would (`NFR-758/10`, `MANGLED_CITATION_RE`'s own former test)
#: — measured live, 2026-09-05: 393 real production lines matched the raw shape and every
#: one was a correctly-recorded compound, while the one real defect
#: (`docs/audit/register.md:49`) was invisible to the shape test *and* to a first
#: "does this component exist as some id" pass (the deputy's own refuted second attempt,
#: `NFR-OVR-10`/`NFR-OVR-11` happen not to exist, but where an orphaned component
#: coincides with an unrelated real id, existence alone passes a mangled citation
#: silently). The only test that cannot be fooled either way is **re-deriving the correct
#: answer independently and comparing** — `_g1_provenance_mismatches` below runs the exact
#: same `docid._expand_compound`/`docid._expand_range` the real migration calls, over the
#: same `REDIRECTS.csv` map it wrote, against the control tree's own citations, and
#: compares the result against what the migrated tree actually contains.
#:
#: The `WK-[0-9]+[A-Z]` alternative (#720's cause4) is **not** part of this narrowing and
#: keeps its raw-shape test unchanged: there is no legitimate mechanism that produces a
#: `WK-<n><UPPERCASE>` shape (unlike a numeric compound, no correct rewrite ever wears it),
#: so shape alone still fully distinguishes it — `_WK_MANGLED_RE` isolates that one
#: alternative for g1's own verdict, leaving `MANGLED_CITATION_RE` itself untouched (its
#: existing broken-input-proof tests keep testing the regex they always tested).
_WK_MANGLED_RE: Final = re.compile(r"\bWK-[0-9]+[A-Z]")


def _wk_shape_hits(scan: Corpus, mig: Corpus, ctl: Corpus) -> tuple[int, int]:
    """(lines, files) matching `_WK_MANGLED_RE` in `scan`, **excluding framework
    self-reference** (team-lead's ruling, 2026-09-05: "your WK hits are not a new class
    — they are the `FR-PLAT-4` class" — one predicate, `_is_framework_self_reference`,
    covers both rather than a second mechanism for the identical population). A
    `WK-944C`-shaped string inside a `scripts/*.py`/`tests/*.py` comment or docstring, or
    a NEVER-ALLOCATED backtick-quoted exhibit in this workstream's own planning docs, is
    this repository talking about #720's cause4, never a citation the real shape test
    needs to catch.

    `scan` is whichever tree is being counted (`mig` for the row's own figure, `ctl` for
    its baseline); `mig`/`ctl` are always the real migrated/control pair, needed for
    limb 2's never-allocated conjunct regardless of which tree `scan` is."""
    n_lines = 0
    n_files = 0
    for rel in scan.files:
        skip = scan.was_lines[rel]
        hits = 0
        for i, line in enumerate(scan.lines[rel]):
            if i in skip:
                continue
            m = _WK_MANGLED_RE.search(line)
            if m and not _is_framework_self_reference(rel, scan, mig, ctl, i, m.group(0)):
                hits += 1
        if hits:
            n_lines += hits
            n_files += 1
    return n_lines, n_files


#: g1's legacy-form base pattern — identical to (d7)'s own `d7_pattern`
#: (`_d7_disclosed_or_fail`), not a second definition: a compound or range citation's
#: *base* token is a scoped legacy id exactly like (d7)'s population, just followed by a
#: continuation (d7) does not look for.
_G1_LEGACY_ID_RE: Final = re.compile(r"\b(?:FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+\b")


def _redirects_token_map(mig: Corpus) -> dict[str, str]:
    """`old_id -> new_id` from the migrated tree's `docs/REDIRECTS.csv`, single-token rows
    only (no `/` or `..` in `old_id`) — the same base map `active_map` is inside
    `_rewrite_citations`, needed here so `docid._expand_compound`/`docid._expand_range`
    can be re-run exactly as the real migration ran them, rather than trusting a compound
    row's own already-expanded `new_id` (which is the answer, not an input)."""
    text = read_text(mig.tree / "docs" / "REDIRECTS.csv")
    if text is None:
        return {}
    result: dict[str, str] = {}
    for row in csv.DictReader(text.splitlines()):
        old_id, new_id = row.get("old_id") or "", row.get("new_id") or ""
        if old_id and new_id and "/" not in old_id and ".." not in old_id:
            result[old_id] = new_id
    return result


def _redirects_path_map(mig: Corpus) -> dict[str, str]:
    """`old_path -> new_path` from the migrated tree's `docs/REDIRECTS.csv`, every row
    naming a move — locates a control-tree file's migrated counterpart so
    `_g1_provenance_mismatches` compares the right two files, not just the same path."""
    text = read_text(mig.tree / "docs" / "REDIRECTS.csv")
    if text is None:
        return {}
    result: dict[str, str] = {}
    for row in csv.DictReader(text.splitlines()):
        old_path, new_path = row.get("old_path") or "", row.get("new_path") or ""
        if old_path and new_path:
            result[old_path] = new_path
    return result


def _g1_provenance_mismatches(docid: Any, mig: Corpus, ctl: Corpus) -> list[str]:
    """Every compound or range legacy citation in the control tree whose migrated
    counterpart does not equal what `REDIRECTS.csv`'s own map says it must be — g1's FR/
    NFR/OQ/DEP alternative, narrowed to provenance rather than shape (see
    `_WK_MANGLED_RE`'s docstring above for why).

    For each `_G1_LEGACY_ID_RE` hit in a control line that is mapped and is followed by a
    compound/range continuation (`docid._compound_token_re`), this independently
    RE-DERIVES the expected rewrite with `docid._expand_compound`/`docid._expand_range` —
    the exact functions the real migration calls, never a re-implementation — and checks
    the expected string appears in the migrated tree's corresponding line. An unmapped
    component correctly derives back to the citation's own original text (the "leave it
    whole" rule both expand functions already enforce) and is not a mismatch.

    Line-aligned per file via `_redirects_path_map`; a file whose migrated line count
    differs from its control line count is **skipped**, not reported as a mismatch — a
    structural change (a split, a reflow) is a different row's concern, and guessing at
    an alignment here risks comparing the wrong two lines and reporting a false mismatch.
    """
    token_map = _redirects_token_map(mig)
    path_map = _redirects_path_map(mig)
    mismatches: list[str] = []
    for rel in ctl.files:
        new_rel = path_map.get(rel, rel)
        old_lines = ctl.lines[rel]
        new_lines = mig.lines.get(new_rel)
        if new_lines is None or len(new_lines) != len(old_lines):
            continue
        for i, line in enumerate(old_lines):
            for m in _G1_LEGACY_ID_RE.finditer(line):
                tok = m.group(0)
                mapped = token_map.get(tok)
                if mapped is None:
                    continue
                cm = docid._compound_token_re(tok).match(line, m.start())
                if cm is None or not (cm.group("range_end") or cm.group("continuation")):
                    continue  # a plain token, not a compound/range citation
                old_citation = cm.group(0)
                derived: list[tuple[str, str]] = []
                expected = (
                    docid._expand_range(tok, mapped, token_map, cm, derived)
                    if cm.group("range_end") is not None
                    else docid._expand_compound(tok, mapped, token_map, cm, derived)
                )
                if expected == old_citation:
                    continue  # an unmapped component -- correctly left whole
                if expected not in new_lines[i]:
                    mismatches.append(
                        f"{rel}:{i + 1} -> {new_rel}:{i + 1}: citation {old_citation!r} "
                        f"should have expanded to {expected!r}, not found in the migrated "
                        f"line: {new_lines[i].strip()[:160]!r}"
                    )
    return mismatches


#: box-end gate-gap's invariant (W37-6, 2026-09-06, ruled (b), corrected to key the
#: rewriter's refusal on resolution rather than shape): a rewritten token immediately
#: followed by a bare `,\s*\d` is a violation only when that tail digit ALSO resolves as a
#: further citation of the SAME old prefix -- exactly `doc-id.py`'s own
#: `_bare_comma_tail_resolves` question, asked a second, independent way. A rewritten token
#: followed by a bare comma-digit that does NOT resolve (a date, a section reference) is
#: correct output under the corrected rule, not a violation -- an earlier version of this
#: check, written for the shape-only refusal, would have wrongly flagged all 39 such sites.
#:
#: Deliberately independent of the rewriter's own functions, unlike `_g1_provenance_mismatches`
#: above (which calls `docid._expand_range`/`docid._expand_compound` directly and inherits
#: whatever they do): a check must not assume its own invariant, so this reimplements the
#: resolution question from scratch over the migrated OUTPUT and `REDIRECTS.csv`'s
#: `old_id`/`new_id` columns, rather than calling `doc-id.py`'s own resolution helper.
_NEW_ID_SHAPE_RE: Final = re.compile(r"^(?:FR|NFR|OQ|DEP)-\d+$")
_BARE_COMMA_DIGIT_ITEM_RE: Final = re.compile(r",[^\S\n]*(\d+)")


def _new_id_values(mig: Corpus) -> frozenset[str]:
    """Every `REDIRECTS.csv` `new_id`, restricted to the `FR|NFR|OQ|DEP-<digits>` shape
    this migration's citation rewrite produces (never a family-lettered old-id shape, so a
    coincidental old-id-looking string elsewhere is never mistaken for a rewrite)."""
    return frozenset(
        v for v in _redirects_token_map(mig).values() if _NEW_ID_SHAPE_RE.match(v)
    )


def _rewritten_base_before_bare_comma(
    mig: Corpus, token_map: Mapping[str, str]
) -> list[str]:
    """Every migrated-tree site where a rewritten token is immediately followed by a bare
    `,\\s*\\d` whose digits ALSO resolve as a further citation of the token's own OLD
    prefix -- a genuine continuation the rewriter's refusal should have caught but did not.
    A rewritten token followed by a bare comma-digit that does not resolve this way (a
    date, a section reference) is correct output and never reported.

    `token_map` is the full `old_id -> new_id` map: for each candidate site, every old id
    that produced the seen new id is looked up (normally exactly one; REDIRECTS.csv is not
    assumed injective), its own prefix extracted, and `prefix + tail_digits` checked
    against `token_map` again -- the SAME question `doc-id.py`'s
    `_bare_comma_tail_resolves` answers, asked independently rather than by calling it."""
    reverse: dict[str, list[str]] = {}
    for old_id, new_id in token_map.items():
        reverse.setdefault(new_id, []).append(old_id)
    new_ids = frozenset(v for v in token_map.values() if _NEW_ID_SHAPE_RE.match(v))
    violations: list[str] = []
    for rel in mig.files:
        skip = mig.was_lines[rel]
        for i, line in enumerate(mig.lines[rel]):
            if i in skip:
                continue
            for m in re.finditer(r"\b(?:FR|NFR|OQ|DEP)-\d+\b", line):
                new_tok = m.group(0)
                if new_tok not in new_ids:
                    continue
                bm = _BARE_COMMA_DIGIT_ITEM_RE.match(line, m.end())
                if bm is None:
                    continue
                digits = bm.group(1)
                for old_id in reverse.get(new_tok, ()):
                    prefix_match = re.search(r"\d+$", old_id)
                    if prefix_match is None:
                        continue
                    prefix = old_id[: prefix_match.start()]
                    base_width = len(old_id) - len(prefix)
                    resolves = token_map.get(prefix + digits) is not None
                    if not resolves and len(digits) < base_width:
                        resolves = token_map.get(prefix + digits.zfill(base_width)) is not None
                    if resolves:
                        violations.append(f"{rel}:{i + 1}: {line.strip()[:160]!r}")
                        break
    return violations


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
# causes accounted for eight of the ten; the other one (a bare-basename/non-`docs/`-rooted
# relative citation, e.g. `docs/README.md`'s `workflows/wf-01-...md` and
# `phase-0-status.md`) is reported here in prose, not as a regex, because it has no single
# stable prefix to key on (unlike the five `docs/`-rooted forms
# `_docid.LEGACY_FORM_PATTERNS` already names).
#
# **Corrected, task #30:** this comment used to also report a second finding — `OQ-DATA-11`
# (cited in `docs/plans/2026-08-19-psi-comparison-selector[-ledger].md`'s own historical
# narrative) as an *"un-allocated placeholder id"* that the run supposedly rewrote to
# `OQ-8471` with no `REDIRECTS.csv` row for `redirects_inverse` to consume. That was false:
# `OQ-DATA-11` is a real, decided open question (`docs/open-questions.md:63`,
# `~~**OQ-DATA-11**~~ ✔`), and #726 (the same-shaped `_discover_requirements` dedup fix,
# "one draft per legacy OQ id") already gives it exactly one `REDIRECTS.csv` row and a
# consistent rewrite everywhere it is cited, plan narrative included — measured directly
# against a real `migrate()` run: `OQ-DATA-11,OQ-849,docs/specs/01-data-management.md,
# docs/specs/01-data-management.md,`, one row, no conflict. Left here as a record that the
# claim was checked and refuted, not silently dropped.
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
#: `_whole_token_re`'s `\b{tok}\b(?![-/][0-9])` — so a legacy work token (`W<n>`) matches as
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

# ---------------------------------------------------------------------------------------
# W37-6 `other` triage, third scope (`docs/`, the code tree and this remainder — the
# #715 ruling `:6xx`): everything not under `docs/`, `tests/`, `backend/`, `frontend/`,
# `scripts/`, `packages/`. Two shapes below were found sampling every member of that
# remainder (14 files, small enough to read whole rather than sample ten) — reported here
# by the same convention as `_SLASH_COMPOUND_RE` above: named and counted, not fixed, not
# assigned an owner by this executor. A third candidate (an id token and its `docs/plans/`
# or `docs/notes/` path rewritten together, e.g. `` [`NT-0003`](docs/notes/0003-....md) ``)
# was found on the same 4 files but turned out to be the sibling `docs/`-triage executor's
# cause3 read one level more generally (a legacy path citation, id present or not) — see
# `_LEGACY_PATH_RES` above, which already matches every one of those 4 lines. Naming it
# again here would be NT-0003's duplicated-status defect in cause-table form, so it is not
# kept as a separate label; cause3 is checked first below and claims them. None of the two
# surviving shapes changes what row (g) fails on.
# ---------------------------------------------------------------------------------------

#: A front-matter block stamped into a file that carried **no** leading `---` block
#: before migration (`old_lines[0] != "---"`) and did not move (`rel` exists in both
#: trees at the same path — otherwise `old_lines` above is `None` already). Distinct from
#: cause 1: cause 1 is an *existing* foreign block DP-7 strips before comparing; this is a
#: *new* block DP-7 adds with nothing on the old side to strip. Per the #706 read folded
#: into Ruling 68's class-6 keying ("class 1 = 0 ... nearly every document moves, so
#: classes 1 and 2 live inside the 48 moves"), a stamp *paired with a move* is absorbed
#: into class 3; a stamp on a file that stays in place has no class to land in and falls
#: through to `classified-by-none`. Verified on all 8 members: `.claude/roles/*.md`,
#: `.claude/skills/README.md`, `README.md`, `deploy/README.md` — each diff's only change is
#: a `+---\n+family: ...\n+...\n+---\n+\n` block inserted before the untouched first
#: heading line, confirmed against `git diff --no-index`-equivalent output on the kept
#: `--verify` snapshot, never assumed from the file list alone. Checked early, alongside
#: cause 1, since (like cause 1) it explains the *entire* diff for these members regardless
#: of what an unrelated citation elsewhere in the same body might also match.
_FRONTMATTER_BLOCK_RE: Final = re.compile(r"^family:\s")

#: A `W<n>[a-z]?-<m>` slice-key token (`W6b-10`) whose Work component is mapped
#: (`W<n>b`->`WK-947b`) but whose `-<m>` suffix is retained verbatim rather than itself
#: rewritten through a map entry — the "no family exists for a task key" gap the deputy's
#: own unmapped-tokens ruling already named (`W<n>-<m>`: "mapped where a map plan or
#: roadmap slice row minted an `SL-`; unmapped ones listed"). Not new: this executor is
#: reporting that the same already-named gap also surfaces as (g) `classified-by-none`
#: residue, not only as an unmapped-token count. Verified on `examples/fremtpl2/seed.py`
#: (`W6b-10`, `W6b-11`); `.github/workflows/docs.yml` carries the identical shape
#: (`W37-6`) but is claimed by cause3 first (it also carries a legacy `docs/plans/` and
#: `docs/notes/` path citation), so this check runs last — the more specific, owned causes
#: above it get first refusal on any file carrying more than one shape.
_WORK_SLICE_KEY_RE: Final = re.compile(r"\bW\d+[a-z]?-\d+\b")

# ---------------------------------------------------------------------------------------
# Code-tree triage (W37-6 channel `:599`, `:770`): the second of the three parallel
# executors, scoped to `tests/`+`backend/`+`frontend/`+`scripts/`+`packages/`. Its own
# dispatched hypothesis — that the code-tree residue is NT-0019 §5.6's comment/docstring/
# marker citation-rewrite forms (`@pytest.mark.req("FR-...")`, `# FR-...`, an OpenAPI
# `summary=`/`description=` string) DP-7's inverse does not recognise as one missing
# *form* — is **killed**: every sampled marker/docstring `FR`/`NFR`/`OQ` single-token
# substitution inverts correctly, byte for byte, on its own (reproduced directly against
# `frozen_file_matches_after_migration_stamp`, not inferred from the diff).
#
# What this executor's own sample actually found — a compound task-key citation
# (`W6b-11`, `W10-2`) left half-rewritten, and (investigating the files even that shape
# could not place) an id-allocation instability where `REDIRECTS.csv` carried two
# conflicting rows for one legacy id and the code tree cited a third, unmapped number —
# turned out to share one root cause (`doc-id.py`'s `_compound_token_re` lacking a
# trailing `\b`) with row (b)'s own regression and (independently) with
# `unmapped-work-slice-key` above. `#721` (row (b)'s fix) and `#727`'s
# `_WORK_SLICE_KEY_RE` above already cover that population; adding a fourth name for the
# same shape here would repeat NT-0003's duplicated-status defect, so it is **not**
# repeated as a cause of its own. Two shapes remain that neither `#720` nor `#727`'s
# remainder-scope covers, because both are specific to the code tree:
# ---------------------------------------------------------------------------------------

#: cause5: `tests/fixtures/docs-ids/**` and `tests/fixtures/docs-migration/**` are
#: synthetic corpora built to test `doc-id.py`'s own `next`/`check`/`migrate` logic —
#: sample documents deliberately holding old-form ids as test data, the same role
#: `docs/roadmap.md` plays for Ruling 68 class 5, but with no equivalent unconditional
#: exemption. The real migration walks them anyway and rewrites their deliberately-old
#: content — not a citation defect to fix, a scope gap: these two directories were never
#: meant to be compared as if they were real citations. Checked by path alone, before any
#: content is read, the same "path is conclusive" rule `_NOTES_STUB_RE` already uses.
_FIXTURE_CORPUS_DIRS: Final = ("tests/fixtures/docs-ids/", "tests/fixtures/docs-migration/")

#: cause6: `scripts/__pycache__/*.pyc` — compiled bytecode the verify snapshot's own tree
#: walk should never have included. Not a citation defect at all; a scan-root hygiene gap
#: in the instrument itself. Binary, so `old_lines` is `None` for these — checked by path
#: alone, before the `old_lines is None -> "other"` fallback would otherwise catch it.
_PYCACHE_RE: Final = re.compile(r"__pycache__/|\.pyc$")

#: One residue member's cause label, checked in this fixed order (a member matching more
#: than one shape is reported under the first — `_NOTES_STUB_RE` and the two path-only
#: code-tree causes (5, 6) before any content is read, since a path alone is conclusive
#: for all three; frontmatter before the citation-shaped checks, since a wrong strip or a
#: wrongly added block explains the whole-file mismatch regardless of what citations the
#: body also carries; cause4's adjacent-uppercase corruption before the broader
#: citation-shaped causes, since it is a forward-migration defect rather than an inverse
#: gap and deserves its own bucket even when the same file also carries a legacy path
#: citation; `unmapped-work-slice-key` last of all, since it is the most generic shape and
#: must not steal a file that a more specific, owned cause above it already explains).
#:
#: `new_lines` (the post-migration content at the same path) is optional and used only by
#: the new-frontmatter-stamp check below — every other check reads `old_lines` alone, as
#: it did before that check was added.
#: Every label `_residue_cause` can return, named once so the W37-11 class registry
#: (`_g2_residue_cause_labels`, read by `load_w37_11_record`'s validation) is derived from
#: this single source rather than a second, hand-restated list — the identical shape the
#: unknown-`cls` defect (#763) itself was: a governance table's key describing why the
#: residue exists rather than naming a class an extractor can actually produce.
_CAUSE_OTHER: Final = "other"
_CAUSE_1_FOREIGN_FRONTMATTER: Final = "cause1-foreign-frontmatter"
_CAUSE_2A_RANGE_CITATION: Final = "cause2a-range-citation"
_CAUSE_2B_NOTES_STUB: Final = "cause2b-notes-stub-relative-link"
_CAUSE_3_LEGACY_PATH_CITATION: Final = "cause3-legacy-path-citation"
_CAUSE_4_COMPOUND_TOKEN_ADJACENT_UPPERCASE: Final = "cause4-compound-token-adjacent-uppercase"
_CAUSE_5_FIXTURE_CORPUS: Final = "cause5-fixture-corpus-old-form-ids"
_CAUSE_6_PYCACHE: Final = "cause6-pycache-build-artifact"
_CAUSE_NEW_FRONTMATTER_STAMP_NO_MOVE: Final = (
    "new-frontmatter-stamp-no-move (unassigned — reported, not investigated)"
)
_CAUSE_SLASH_COMPOUND_CITATION: Final = (
    "slash-compound-citation (unassigned — reported, not investigated)"
)
_CAUSE_UNMAPPED_WORK_SLICE_KEY: Final = (
    "unmapped-work-slice-key (named elsewhere, reported here by shape)"
)


def _residue_cause(
    rel: str,
    old_lines: Sequence[str] | None,
    new_lines: Sequence[str] | None = None,
) -> str:
    if _NOTES_STUB_RE.match(rel):
        return _CAUSE_2B_NOTES_STUB
    if _PYCACHE_RE.search(rel):
        return _CAUSE_6_PYCACHE
    if rel.startswith(_FIXTURE_CORPUS_DIRS):
        return _CAUSE_5_FIXTURE_CORPUS
    if old_lines is None:
        return _CAUSE_OTHER
    if old_lines and old_lines[0] == "---" and rel.startswith(_FOREIGN_FRONTMATTER_DIRS):
        return _CAUSE_1_FOREIGN_FRONTMATTER
    if (
        (not old_lines or old_lines[0] != "---")
        and new_lines
        and new_lines[0] == "---"
        and any(_FRONTMATTER_BLOCK_RE.match(line) for line in new_lines[1:12])
    ):
        return _CAUSE_NEW_FRONTMATTER_STAMP_NO_MOVE
    for line in old_lines:
        if _WORK_ADJACENT_UPPER_RE.search(line):
            return _CAUSE_4_COMPOUND_TOKEN_ADJACENT_UPPERCASE
    for line in old_lines:
        if _RANGE_CITATION_RE.search(line):
            return _CAUSE_2A_RANGE_CITATION
    for line in old_lines:
        if _SLASH_COMPOUND_RE.search(line):
            return _CAUSE_SLASH_COMPOUND_CITATION
    for line in old_lines:
        if any(pattern.search(line) for pattern in _LEGACY_PATH_RES):
            return _CAUSE_3_LEGACY_PATH_CITATION
    for line in old_lines:
        if _WORK_SLICE_KEY_RE.search(line):
            return _CAUSE_UNMAPPED_WORK_SLICE_KEY
    return _CAUSE_OTHER


#: Every `g2-<cause>` class `row_g`'s residue can key on — `_residue_cause`'s own return
#: values, collected once. `cls not in _g2_residue_cause_labels` after stripping the
#: `"g2-"` prefix is what makes a hand-typed, plausible-but-invalid label (`#763`'s
#: `comma-continuation-left-whole`, a description of a cause rather than a produced class)
#: fail loudly at record-load time instead of governing nothing and reading 0 forever.
_G2_RESIDUE_CAUSE_LABELS: Final[frozenset[str]] = frozenset({
    _CAUSE_OTHER,
    _CAUSE_1_FOREIGN_FRONTMATTER,
    _CAUSE_2A_RANGE_CITATION,
    _CAUSE_2B_NOTES_STUB,
    _CAUSE_3_LEGACY_PATH_CITATION,
    _CAUSE_4_COMPOUND_TOKEN_ADJACENT_UPPERCASE,
    _CAUSE_5_FIXTURE_CORPUS,
    _CAUSE_6_PYCACHE,
    _CAUSE_NEW_FRONTMATTER_STAMP_NO_MOVE,
    _CAUSE_SLASH_COMPOUND_CITATION,
    _CAUSE_UNMAPPED_WORK_SLICE_KEY,
})


def _residue_cause_table(residue: Sequence[str], ctl: Corpus, mig: Corpus) -> str:
    """Ruling 102 §3's "name them", applied to the residue as a population: one line per
    cause, its count, and up to three example paths — computed on `ctl` and `mig` (the
    same un-migrated and migrated corpora every other row already shares), never a second
    tree read. `mig` is read only by the new-frontmatter-stamp check
    (`_residue_cause`'s `new_lines` argument); every other check still reads `ctl` alone.
    """
    by_cause: dict[str, list[str]] = {}
    for rel in residue:
        cause = _residue_cause(rel, ctl.lines.get(rel), mig.lines.get(rel))
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

    - **g1** — Ruling 102 §2 row 1's broken-input proof, read against its own at-risk
      denominator and an un-migrated control. Two components: `_WK_MANGLED_RE`'s raw-shape
      test (unchanged — no legitimate rewrite ever produces that shape) and
      `_g1_provenance_mismatches`'s independent re-derivation (deputy disposition,
      2026-09-05 13:35 BST — `_WK_MANGLED_RE`'s own docstring above has why a shape test
      cannot survive a pure-numeric id scheme for the FR/NFR/OQ/DEP alternative).
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

    wk_mangled, wk_mangled_files = _wk_shape_hits(mig, mig, ctl)
    wk_control, _ = _wk_shape_hits(ctl, mig, ctl)
    provenance_mismatches = _g1_provenance_mismatches(docid, mig, ctl)
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
    elif wk_mangled or provenance_mismatches or residue:
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
        # a complete enumeration, not a sample) follows it. The provenance mismatches are
        # a full enumeration too — one message per mismatch, never a sample.
        named = "; ".join(classification.violations)
        parts = [_residue_cause_table(residue, ctl, mig), named]
        if provenance_mismatches:
            parts.append(
                f"g1 provenance mismatch(es): {'; '.join(provenance_mismatches)}"
            )
        note = " || ".join(p for p in parts if p)
        verdict = FAIL
    else:
        verdict, note = PASS, ""

    return Row(
        key="g",
        title="migration diff filtered to hunks that are neither header nor "
              "citation-token is empty",
        owner=OWNER_W37_6,
        predicate=(
            "g1 (Ruling 102 §2 row 1's named broken-input proof, the FR/NFR/OQ/DEP "
            "alternative narrowed to provenance by the deputy's 2026-09-05 13:35 BST "
            "disposition): for every compound/range legacy citation in the control tree, "
            "re-derive the expected rewrite with `docid._expand_compound`/"
            "`docid._expand_range` over `REDIRECTS.csv`'s own map and compare against the "
            "migrated tree at the corresponding site — a mismatch is the defect; a shape "
            "test alone cannot survive a pure-numeric id scheme, where a correctly-"
            "expanded compound and a corrupted one are indistinguishable by pattern. The "
            f"WK-family alternative keeps its raw-shape test unchanged: {_WK_MANGLED_RE.pattern!r} "
            "— no legitimate rewrite produces that shape, so shape alone still suffices "
            "for it, excluding framework self-reference (`_is_framework_self_reference`, "
            "the identical predicate (d7)'s `FR-PLAT-4` joins the disclosed class by — "
            "one mechanism for one class, not two). g2 (Ruling 68 §2's closed enumeration, "
            "amended by Ruling 104 §2/§3 "
            "for class 6, by symbol, never restated here): "
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
            f"g1 WK-shape mangled = {wk_mangled} in {wk_mangled_files} file(s), "
            f"provenance mismatch(es) = {len(provenance_mismatches)}; "
            f"g2 {per_class}, {docid.CLASSIFIED_BY_NONE}={len(residue)}"
        ),
        control=f"g1 WK-shape mangled = {wk_control} (un-migrated)",
        verdict=verdict,
        note=note,
        #: g2's own residue, one hit per classified-by-none file, tagged with its cause
        #: (`_residue_cause`) rather than a bare `"g2"` — the W37-11 ceiling is per (file,
        #: class), and "class" here is the sub-bucket a per-row total would hide movement
        #: inside of, exactly the shape the deputy's ruling names.
        residue={
            (rel, f"g2-{_residue_cause(rel, ctl.lines.get(rel), mig.lines.get(rel))}"): 1
            for rel in residue
        },
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

#: Ruling 105 §B's own methodology, originally ported from the shell one-liner
#: `docs/plans/2026-09-03-w37-6-row-h-the-named-h-rows.md:139` used to derive the taxonomy
#: the ruling reads: `sed -n '/^FAILED/,$p' <log> | grep '^  - ' | sed -E
#: 's/^(check [0-9]+):.*/\1/; s/^broken link in .*/check 1/' | sort | uniq -c`. Everything
#: from the `FAILED (`n`):` line onward, one `  - <msg>` per failure.
#:
#: The one-liner's own second rule (`s/^broken link in .*/check 1/`) and a same-shaped
#: rule this module briefly carried for check 27 (added, then removed, in the same PR —
#: see the deputy's ruling below) both existed for one reason: those two checks' own
#: `fail()` messages did not start `check N:` the way every other numbered check's does.
#: Fixed at the source instead of carried as a growing set of classifier-side special
#: cases (the deputy's ruling on exec-h1's finding: "a failure the classifier cannot
#: attribute is a count without a predicate ... special-casing each check as it is
#: noticed is how the bucket refills") — every `fail()` call site in
#: `scripts/audit-docs.py`'s checks 1-39 now begins its message with `check N: ` (checks
#: 30-39 already did; this PR added it to checks 1-28), so `_CHECK_PREFIX_RE` alone
#: classifies all of them and neither special case is reachable any more. One exception,
#: deliberately not resolved into a per-check prefix: `check_notes`'s top-of-function
#: guard (`docs/notes does not exist`) covers five check numbers (16-20) at once and
#: this predicate's `(\d+)` group cannot hold five values — `_ABSENT_CHECK_RE` above
#: already reports that exact message as a non-execution marker, a state distinct from a
#: classified failure, so leaving it unprefixed is not a second gap of the same kind.
_FAILED_BLOCK_RE: Final = re.compile(r"^FAILED \(\d+\):$", re.MULTILINE)
_FAILURE_LINE_RE: Final = re.compile(r"^  - (.*)$", re.MULTILINE)
_CHECK_PREFIX_RE: Final = re.compile(r"^check (\d+):")

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
        cls = m.group(1) if m else "unclassified"
        counter[cls] = counter.get(cls, 0) + 1
    return counter


def _h1_verdict(
    other_total: int,
    residue: Mapping[tuple[str, str], int] | None = None,
    record: "Sequence[ResidueEntry]" = (),  # noqa: UP037 -- ResidueEntry defined later
) -> str:
    """Ruling 105 §B, extended by the box-end ruling (2026-09-05): (h1) passes iff every
    class outside checks 29/30/35 is zero, OR every one of those non-disclosed classes'
    per-(file, check) hits is filed and ceilinged in the W37-11 record — closes by
    DISCLOSE, not by collapse. `residue` is (h1)'s own full per-(file, check) breakdown
    (`_h1_residue_by_file`, includes checks 29/30/35 too); only the entries whose check is
    NOT one of `_H1_DISCLOSED_CHECKS` are ever tested against the record, since 29/30/35
    are already non-fatal by W37-10 ownership and never contribute to `other_total`.
    """
    if other_total == 0:
        return PASS
    non_disclosed = {
        key: count
        for key, count in (residue or {}).items()
        if key[1][len("h1-check"):] not in _H1_DISCLOSED_CHECKS
    }
    # `other_total > 0` with an empty `non_disclosed` means the caller did not supply the
    # per-(file, check) breakdown (or supplied one that disagrees with `other_total`) —
    # never DISCLOSE on the strength of a governance check with nothing to check. This is
    # what keeps every pre-existing call site that passes no `residue` (`_h1_verdict(1)`)
    # exactly `FAIL`, as it was before this parameter existed.
    if not non_disclosed:
        return FAIL
    return DISCLOSE if _residue_fully_governed(non_disclosed, record) else FAIL


#: The common shape a `fail()` call in `audit-docs.py` writes: `check N: <path>: ...` —
#: the overwhelming majority of call sites (checks 16-19, 25, 30-33, 36, 1-8 and more)
#: name the file first, immediately after the check number. Not universal: a message with
#: no natural file subject (a numbering-gap report, a cross-reference summary naming
#: several files at once) does not match — those fall to `_H1_UNLOCATED_PATH` below,
#: never dropped.
_H1_FAILURE_LOCATION_RE: Final = re.compile(r"^check (\d+): ([^\s:]+):")

#: A failure message this predicate cannot place at a real file still belongs to *some*
#: check, and pinning it under a class-level ceiling (this sentinel `path`, real `cls`)
#: is better than dropping it: a regression inside a pathless class is then loud too,
#: never silent because no single file could be named. Team-lead's own disposition on PR
#: #756 — "if the loader accepts a file-less entry, pin them as a class-level ceiling" —
#: and `Row.residue`/`ResidueEntry.path` are plain `str`, so no loader change was needed
#: at all; only this module choosing to use the string rather than skip.
_H1_UNLOCATED_PATH: Final = "(no file named in message)"

_H1_CHECK_NUMBER_RE: Final = re.compile(r"^check (\d+):")


def _h1_residue_by_file(out: str, corpus: Corpus) -> Mapping[tuple[str, str], int]:
    """(h1)'s own per-(file, check) breakdown, for the W37-11 residue ceiling
    (`Row.residue`) — reads the identical failure lines `_classify_failures` already
    parses, never a second sweep of `out`.

    A failure message shaped `check N: <token>: ...` (`_H1_FAILURE_LOCATION_RE`) names a
    file only if `token` **resolves** — is a member of `tracked_files(corpus.tree)`, the
    unfiltered tracked-file set of the migrated snapshot (`corpus` only for its `.tree`;
    never the repo working tree, since the snapshot's filenames deliberately differ from
    the current checkout, and never `corpus.files`, which is `Corpus`'s own row-(d)/(e)/
    (g)-scoped set with `_D_EXCLUDED_BASENAME` already applied — see the comment above
    `known_files` below for why that scope does not answer h1's question). A resolving
    token is keyed `(token, f"h1-check{n}")`; everything else —
    a message with no colon-terminated leading token, or one that has the shape but does
    not resolve to a real file — is keyed `(_H1_UNLOCATED_PATH, f"h1-check{n}")` instead
    of being dropped, a class-level ceiling rather than a per-file one but still
    governed: `check_residue_ceiling` cannot tell files apart inside it, but a regression
    that grows the count IS still a fatal `RESIDUE_REGRESSION` once the record names
    that `cls`.

    **Resolution over shape, deliberately** (team-lead's ruling on PR #758/#759's
    follow-up): a shape rule ("looks like a path") is fitted to today's messages and
    survives only until a future message happens to look path-shaped without being one.
    Resolution is a rule the next unforeseen message cannot survive: a token either
    names a file in this run's own corpus or it does not. This is what closed a real
    defect found while building it — check 36 also has a `` `was: {was}` has no
    docs/REDIRECTS.csv row `` message (audit-docs.py's `check_redirects`) that a shape
    rule matched anyway (`` `was `` looked path-shaped: no whitespace, a colon
    immediately after), attributing residue to that four-character garbage token. It
    never surfaced in a measured corpus because no REDIRECTS.csv-missing hit had fired
    yet — corpus-lucky, not structurally sound. Resolution rejects `` `was `` because it
    is not a file in the corpus, the same reason it would reject anything else that
    happens to look path-shaped without being one.

    A message with no `check N:` prefix at all (`_classify_failures`'s own
    `"unclassified"` bucket) has no check number to key on and is not covered by either
    shape — the same non-coverage it already had. `cls` is tagged `f"h1-check{n}"`
    rather than the bare check number, so a future (d)-row and an h1 check can never
    collide on the same key by coincidence.
    """
    # The unfiltered tracked-file set of the migrated snapshot, not `corpus.files`:
    # `Corpus.files` already has `_D_EXCLUDED_BASENAME` (`docs/REDIRECTS.csv`) applied,
    # a row-(d)/(e)/(g) citation-sweep exclusion for a reason that has nothing to do with
    # h1's own question ("does this token name a real file in the migrated tree?").
    # Borrowing another row's scanning scope as a stand-in for existence is the same
    # proxy error the shape rule made — team-lead's ruling, and the third appearance of
    # this exact REDIRECTS.csv scope mismatch (row (e)'s conjunct 0 vs. check 32's
    # `_id_scope_documents()` in #752's decomposition; flagged out-of-scope during #756;
    # now costing real per-file entries here). `tracked_files` re-reads `git ls-files`
    # once more rather than reusing `corpus.files`, deliberately: it is the property
    # actually wanted, not a second full `load_corpus` (lines/was_lines/fenced_lines are
    # not needed here at all).
    known_files = frozenset(tracked_files(corpus.tree))
    block = _FAILED_BLOCK_RE.search(out)
    tail = out[block.start():] if block else ""
    residue: dict[tuple[str, str], int] = {}
    for msg in _FAILURE_LINE_RE.findall(tail):
        m = _H1_FAILURE_LOCATION_RE.match(msg)
        if m and m.group(2) in known_files:
            check_no, path = m.group(1), m.group(2)
        else:
            m2 = _H1_CHECK_NUMBER_RE.match(msg)
            if not m2:
                continue
            check_no, path = m2.group(1), _H1_UNLOCATED_PATH
        key = (path, f"h1-check{check_no}")
        residue[key] = residue.get(key, 0) + 1
    return residue


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


def rows_h(
    snap: Snapshot,
    mig: Corpus,
    record: "Sequence[ResidueEntry]" = (),  # noqa: UP037 -- ResidueEntry defined later
) -> list[Row]:
    """`mig` is the migrated snapshot's own `Corpus` (`compute_rows`' own `load_corpus(
    snap.migrated)`, never re-derived here) — passed on for its `.tree` alone: h1's
    per-file residue extraction resolves a captured token against
    `tracked_files(mig.tree)`, the unfiltered tracked-file set, never `mig.files` itself
    (`Corpus`'s own row-(d)/(e)/(g)-scoped set) and never the repo working tree, since
    the migrated snapshot's filenames deliberately differ from the current checkout.
    """
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
    h1_residue = _h1_residue_by_file(mig_out, mig)
    h1_verdict = _h1_verdict(h1_other, h1_residue, record)
    h1_governed_note = (
        f"{h1_other} failure(s) outside checks 29/30/35 are filed and ceilinged in "
        "docs/audit/w37-11-record.md — governed residue audit-docs.py cannot itself "
        "resolve, disclosed per (file, check) rather than special-cased in this module "
        "(box-end ruling, 2026-09-05)"
        if h1_verdict == DISCLOSE
        else ""
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
        verdict=h1_verdict,
        note="; ".join(
            part
            for part in (
                f"checks 29, 30 and 35 are W37-10's residue (Ruling 105 §B), disclosed by "
                f"count and never fatal: {h1_disclosed_text}. Every other class — including "
                "checks 32, 36, 1, 31, 27 and any class not named here — must be zero to "
                "pass, or filed and ceilinged in the W37-11 record",
                (
                    f"{mig_absent} check(s) report they CANNOT RUN on the migrated tree "
                    f"(control {ctl_absent}) — the old notes directory is dissolved by the "
                    "migration, so checks 16-20 and 25 have nothing to scan. Non-execution "
                    "is a third state beside pass and fail, and a failure count scores it "
                    "as a small number of failures rather than as a hole in coverage."
                    if mig_absent else ""
                ),
                h1_governed_note,
            )
            if part
        ),
        residue=h1_residue,
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
    "b": PASS,          # noncontiguous=0 — FIXED (2026-09-04, W37-6 row (b) fresh
                         # executor). #711 item 3's `_compound_token_re` (compound-citation
                         # expansion) dropped the trailing `\b` `_whole_token_re` already
                         # had between the base token and its optional continuation group,
                         # so a shorter mapped legacy id (`OQ-OVR-1`) matched as a bare
                         # prefix of a longer, unrelated, unmapped one that merely starts
                         # with the same digits (`OQ-OVR-11`, itself correctly excluded
                         # from `token_map` by the multi-claim guard) — `_expand_compound`
                         # then returned the mapped value alone and left the unmatched
                         # trailing digit orphaned onto it: `OQ-OVR-11` -> `OQ-831` + `1` =
                         # `OQ-8311`, a fabricated id nothing allocated, planted into every
                         # mirror of that open question and from there into
                         # `docs/INDEX.md`'s own id column. Six siblings of the same shape
                         # (`OQ-OVR-12`, `OQ-DATA-11`, `OQ-MODEL-10/11/23/24`, against their
                         # own shorter mapped prefixes) did the same; `OQ-GOV-8` has no
                         # shorter same-prefix sibling to collide with and was never
                         # affected. Fixed by giving `_compound_token_re` the same trailing
                         # `\b` `_whole_token_re` already had
                         # (`scripts/doc-id.py::_compound_token_re`); a genuine `-`/`/`
                         # continuation (`NFR-RATE-13/14`, `W1-1`'s own refusal) is
                         # unaffected, since digit -> `-`/`/` is a real `\b` transition
                         # while digit -> digit is not. Isolated and reproduced against
                         # `971677e` (this row's last recorded `PASS`) with only #711's
                         # `doc-id.py` diff applied before touching anything else:
                         # `noncontiguous=4`, identical to `HEAD`; the same tree with this
                         # one-line fix: `noncontiguous=0`. This entry is edited in the same
                         # commit as the fix per this table's own rule above ("edited by
                         # hand, in the same commit as the change that moves a row") —
                         # noted because the dispatching ruling said this table needed no
                         # change; verified against the code's own instruction instead,
                         # since leaving `FAIL` here after a genuine `PASS` would produce a
                         # SET CHANGE (PROGRESSED) on the next `--verify` run regardless.
    "c": PASS,          # docs/INDEX.md byte-stable against its own renderer — same
                         # unrelated prior-PR progress, re-recorded for the same reason
    "d1": PASS,         # NT-\d{4} — FIXED (2026-09-04, W37-6 exec-ids): `_expand_compound`'s
                         # padding bug for a zero-padded family's shortened compound
                         # continuation (`NT-0014-15`, real citation, `docs/plans/...w37-6-
                         # the-migration-run-the-go-ahead-ask...md`) was the row's only
                         # citation-class miss; the four specification-class matches
                         # (a deliberately-broken-input example, three test fixtures) were
                         # fenced or excluded via the new `tests/`-module class. 0/0.
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
    "d4": DISCLOSE,     # wf-0[0-9] — FAIL -> DISCLOSE, 2026-09-05 (W37-6 Checkpoint 1
                         # box-end ruling PR): the residual 2 hits are quotation-integrity
                         # residue, not the migration's own regression — two frozen
                         # documents (`docs/plans/PL-00283-...md`,
                         # `docs/research/nt-0019-w37-6-condition-2-and-third-
                         # measurement-2026-09-04.md`) quote, hyphen-fused into an old
                         # ledger filename, the pre-#755 buggy workflow-id token this
                         # row's own pattern matches, as evidence of the generator
                         # defect's own discovery; `TOKEN_LEFT_BOUND` correctly refuses
                         # the fused form, and rewriting the quotation would falsify the
                         # handover it documents. NOT written out literally in this
                         # comment on purpose — spelling the exact token here, in a
                         # tracked `.py` file this row's own predicate also scans, would
                         # manufacture a third fatal hit against this very row (caught by
                         # re-measuring this PR's own HEAD before landing it: an earlier
                         # draft of this comment did exactly that, migrated 2 -> 3). Not
                         # (d7)'s self-reference/never-allocated class: the token IS an
                         # allocated id, just quoted historically rather than cited live.
                         # Predicate: `'\bwf-0[0-9]\b'` over row (d)'s corpus (this
                         # table's own row (d4) definition, unchanged by this PR) —
                         # measured 2 line(s) / 2 file(s) fatal on BOTH `f35cfe5` (this
                         # PR's base, `git archive` of `origin/main`) and this PR's own
                         # HEAD (the pattern and corpus are untouched; only the record +
                         # `_residue_fully_governed` gate changed). Both files' 2 hits are
                         # filed in `docs/audit/w37-11-record.md` under `cls="d4"` with a
                         # ceiling of 1 each, so `_docverify.rows_d`'s new governance
                         # check (`_residue_fully_governed`) now returns DISCLOSE instead
                         # of FAIL for this row; a fatal count now excluded from the zero
                         # requirement, owner W37-6.
    "d5": PASS,         # Ruling [0-9]+ — FIXED (2026-09-04, W37-6 #748): `_RULING_HEADING_RE`
                         # accepted only `^##`, so the H1-only ruling files (Rulings 59/60/61)
                         # were never discovered and so never rewritten. Widened to `^#{1,2}`
                         # (`scripts/doc-id.py`), covered by
                         # `tests/test_d5_h1_ruling_heading.py`. Measured locally on this
                         # branch at 2026-09-04 by `python3 scripts/doc-id.py migrate
                         # --verify`, which printed `[PASS] (d5) §7(d) alternative 'ruling
                         # reference' ('\bRuling \d+\b') returns nothing` and, against the
                         # then-recorded FAIL, `PROGRESS (newly passing): (d5) FAIL -> PASS`.
                         # SUPERSEDES the reading below, which is kept because it records
                         # what was believed and why the population looked near-zero before:
                         # Ruling [0-9]+ — REGRESSED (2026-09-04, W37-6 row (b) fresh
                         # executor): migrated 75 (was near-zero). Not this PR's own new
                         # defect but an existing one this PR's row (b) fix un-masked: the
                         # same `_compound_token_re` boundary bug fixed for row (b) (see
                         # `_compound_token_re`'s docstring, `scripts/doc-id.py`) also
                         # mangled the space-separated `Ruling <n>` family the identical
                         # way — a shorter mapped `Ruling <n>` swallowing a longer,
                         # unrelated `Ruling <nm>` as a bare prefix (`Ruling 5` + `9` ->
                         # a mangled `Ruling 59`, e.g.) — which is what let this row's grep
                         # for the *un-migrated* literal `Ruling <n>` form read as near-zero:
                         # the citations were still there, just corrupted into a shape the
                         # pattern no longer matched, not actually rewritten. Fixing the
                         # boundary correctly leaves every genuinely ambiguous `Ruling <n>`
                         # un-rewritten instead of garbling it, so the true (larger)
                         # un-migrated population is now visible. Flagged to the lead as an
                         # existing, now-measured defect (a `Ruling <n>` ambiguity/
                         # migration gap, row (d)'s file, previously closed at task 7) — not
                         # fixed here, out of row (b)'s own scope.
    "d6": DISCLOSE,     # ADR-0[0-9]{3}\b — FIXED (2026-09-04, W37-6 exec-ids): all five
                         # original matches, plus one more surfaced by `origin/main` drift
                         # (`docs/plans/2026-09-03-w37-6-row-h-the-named-h-rows.md`, a
                         # row-h plan landed after this row's original 74-line snapshot),
                         # were specification-class — deliberately-fake, schematic
                         # `ADR-0NNN`-shaped parsing-width worked examples and test
                         # fixtures (respelled here too, self-referentially, so this very
                         # comment does not itself trip the row it describes — the same
                         # class this table's own history above already warns about),
                         # never a real citation. Fenced or respelled; zero citation-class
                         # misses. 0/0.
                         #
                         # APPENDED, not a correction to the above (2026-09-06, W37-6
                         # exec-pin, ruled by the lead and confirmed by the deputy):
                         # `PASS` -> `DISCLOSE`. `docs/skills-map.md:92` now reads
                         # `ADR-0004, 03 FR-RATE-1..13, 56..58` — `03` resolves as the real
                         # `ADR-0003`, so this branch's own box-end comma-continuation
                         # refusal (built for (d7), the identical shape `_bare_comma_tail_
                         # resolves` decides for every id family the general rewriter
                         # covers) correctly refuses to partially rewrite `ADR-0004`,
                         # leaving it legacy-but-intact rather than mangled. This is not
                         # the FIXED defect above regressing: base (pre-refusal, `aeeb1fe`)
                         # measured 0/0 exactly as this entry already said; head measures
                         # 1 line / 1 file, entirely this one new refusal. `_box_end_only_
                         # residue_or_none` (generalised from (d7)'s own third disclosed
                         # class) discloses it; docs/audit/w37-11-record.md carries the one
                         # entry this class needs, reconciled exact against measurement.
    "d7": DISCLOSE,     # (FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+ — `FAIL` -> `DISCLOSE`, 2026-09-05,
                         # this same commit (the (d7)/(g) executor). The 39 "Next free"/
                         # "Highest ids in use" lines are the never-allocated closed class
                         # (deputy's mechanical predicate, 2026-09-04, W37-6 exec-ids):
                         # disclosed, excluded from the zero requirement, owner "none —
                         # closed class". The two remaining real hits are now fixed rather
                         # than merely flagged: `FR-RATE-41` in the generated `docs/
                         # rulings/INDEX.md` was `_sweep_title`'s own compound-title-sweep
                         # bug (`_whole_token_re` refuses a token followed by a compound
                         # continuation, and a title is swept nowhere else) — fixed by
                         # switching `_sweep_title` to the same `_compound_token_re`/
                         # `_expand_compound`/`_expand_range` dispatch the main citation
                         # sweep uses. `FR-PLAT-4` in `scripts/doc-id.py`'s own
                         # `_expand_range` docstring is a real, bold-defined id used only
                         # as an illustrative worked example, never a citation — joins the
                         # disclosed class by name via `_D7_SELF_REFERENTIAL_EXEMPLARS`,
                         # per the deputy's ruling (2026-09-05), since the mechanical
                         # predicate is per-token and cannot itself tell a genuine
                         # citation from this file's own self-referential example.
    "d8": DISCLOSE,     # workstream/slice id — re-recorded FAIL -> DISCLOSE, 2026-09-04.
                         # Both fatal components now measure zero on a real
                         # `migrate()`-mutated tree; `_d8_verdict` falls through to its own
                         # DISCLOSE branch (Ruling 105 §A's third alias class), printing the
                         # slice-key and task-key counts on their own line.
                         #
                         # **Task keys** are a disclosed component, not a fatal one — Ruling
                         # #26 (`to-lead.md:498-510`), reaffirmed against my own later
                         # entries by the correction at `to-lead.md:1298-1306`: "no family
                         # exists for a task (NT-0019 §1.2 has `WK` and `SL`, nothing below a
                         # slice), so a task key has no target by the standard's design — the
                         # same ground as slice keys". That correction's violation line reads
                         # "task keys treated as fatal anywhere after this". Their raw count
                         # also fell once the patterns took `_docid.TOKEN_LEFT_BOUND` — the
                         # standard's own narrowed left-bound guard (#740, Ruling 67 §2),
                         # shared with row (d)'s `LEGACY_FORM_PATTERNS` rather than a private
                         # copy — since most were the tail of a different, already-classified
                         # id family (the finding form `F-W<n>-<m>-<k>`, `audit-docs.py`'s
                         # `_FINDING_ID`) matched from its second character, a bare `\b` being
                         # satisfied between a hyphen and the next token. Re-measured under
                         # the narrowed guard (2026-09-05, task-key figure verified against a
                         # real `migrate()`-mutated tree, not carried over from the earlier
                         # wide-guard count): see the ledger entry for this row's exact
                         # before/after numbers.
                         #
                         # **The bare work-key remainder** is still fatal on any occurrence
                         # (a `token_map` defect, not this alias class) and now reads zero.
                         # The last one was this file's own prior version of this comment,
                         # which spelled two illustrative keys as literals and so matched
                         # itself — `scripts/_docverify.py` is not in
                         # `_docid.TEST_MODULE_EXCLUSIONS` and has no markdown fence to hide
                         # behind. Dispositioned 3b per `to-lead.md:1243` ("respelled to a
                         # schematic that cannot match"): illustrative keys are written
                         # `W<n>` / `W<n><x>` here and must stay schematic. The real-corpus
                         # exhibits of that shape are fenced under Ruling 103 §5.1 in
                         # `.claude/skills/close-workstream/SKILL.md`,
                         # `docs/audit/closure-records.md` and the w6b slice-map plan; the
                         # instrument's own fixtures are class 3c.
                         #
                         # A bare key CAN still be a real defect and is not NECESSARILY one —
                         # which is why the alternative stays fatal on any remaining
                         # occurrence rather than trying to tell the two apart at measurement
                         # time. The earlier comment's "every Work mints a `WK-`, so an
                         # unmapped one is necessarily a real defect" was false on the tree.
    "d9": DISCLOSE,     # docs/plans/2026- — FIXED (2026-09-05, W37-6 rows (d9)-(d12)):
                         # 0 of 131 fatal lines remain. Four framework defects, each
                         # fixed generically rather than per-file per the maintainer's
                         # unconditional ruling (13:25 BST, W37-6 channel: any line
                         # naming a real moved file in REDIRECTS.csv is a tool miss, not
                         # residue): a same-path (`old_path==new_path` token-rename)
                         # `docs/REDIRECTS.csv` row counted as a "real moved file"; a
                         # family split-source `docs/<family>/INDEX.md`'s own ruled
                         # provenance (RL-287/RL-255) counted as an unrewritten citation;
                         # `_rewrite_wrapped_path_citations`'s `if old_tok in text:
                         # continue` shortcut skipping the wrap-tolerant pattern for a
                         # token that also appears contiguous elsewhere in the same
                         # file; and a wrapped citation of a SPLIT source
                         # (`w11-slice1-rulings.md` etc.), which the first three fixes'
                         # own commit left deferred as a documented scope limit and a
                         # follow-up commit resolved via `_SplitSource.resolve()` on the
                         # wrap-reconstructed line. The row's own disclosed (no real
                         # successor) population remains, `_verdict_on_zero`'s correct
                         # DISCLOSE, never PASS.
    "d10": DISCLOSE,    # docs/audit/ — FAIL -> DISCLOSE, 2026-09-05 (W37-6 Checkpoint 1
                         # box-end ruling PR). 44 of 45 fatal lines were already fixed
                         # (2026-09-05, W37-6 rows (d9)-(d12)): the same four framework
                         # defects (d9)'s note names, plus a fifth wrap shape. **1 fatal
                         # line is a genuine resistant file, not a tool gap**: re-measured
                         # at this PR's base `f35cfe5` (`git archive` of `origin/main`,
                         # never the pre-migration working tree — the migration assigns
                         # this file's own name) as `docs/plans/PL-00132-rfc-128-
                         # rfc-129-adoption-implementation-plan.md:126` — NOTE: a prior
                         # comment on this row named this file `PL-00132-nt-0010-
                         # nt-0011-adoption-implementation-plan.md`; that basename does
                         # not exist in this PR's own migrated snapshot at `f35cfe5`,
                         # reported to the lead as a citation drift rather than silently
                         # corrected here. The file cites `docs/audit/plan-reviews.md`
                         # (13-target split source) wrapped across a line break, and its
                         # own determinant is prose ("plan review 8") rather than a
                         # recognised `CR-`/anchor/line-span form `_SplitSource.resolve`
                         # can read — the deputy's own constraint on this fix (relayed
                         # via the lead, 2026-09-05): an undetermined wrapped citation is
                         # left byte-identical, never guessed at with the index-token
                         # fallback the ordinary sweep uses. Predicate: `'docs/audit/'`
                         # over row (d)'s corpus, fatal bucket only
                         # (`_path_alternative_hits_by_file`'s `fatal_by_file`, this
                         # table's own row (d10) definition, unchanged by this PR) —
                         # measured 1 line / 1 file fatal on BOTH `f35cfe5` and this PR's
                         # own HEAD. Filed in `docs/audit/w37-11-record.md` under
                         # `cls="d10"` with a ceiling of 1, so `_residue_fully_governed`
                         # now returns DISCLOSE instead of FAIL for this row — a fatal
                         # count excluded from the zero requirement, owner W37-6.
    "d12": DISCLOSE,    # docs/adr/ — FIXED (2026-09-05, W37-6 rows (d9)-(d12)): every one
                         # of this row's 2 fatal lines is gone; the row still carries a
                         # disclosed (no-real-successor) population, `_verdict_on_zero`'s
                         # correct DISCLOSE, never this table's PASS.
    "d11": DISCLOSE,    # docs/notes/ — FIXED (2026-09-05, W37-6 rows (d9)-(d12)): same
                         # fix as (d12); 0 of this row's 5 fatal lines remain, and the
                         # row's own disclosed population still makes DISCLOSE the
                         # correct verdict, not PASS.
    "d13": DISCLOSE,    # the old .claude notes root — wholly disclosed, 0 fatal
    "e": PASS,          # 0 padded ids in prose — #25's ruling: the migration normalises a
                         # padded citation to unpadded (`_normalize_padded_citations`), and
                         # the two exhibits are fenced by hand under Ruling 103 §5.1
                         # (2026-09-04, task 7)
    "f": PASS,          # VR-DST-1 unchanged, both conjuncts — Ruling 103. Regressed on
                         # `main` (#707, 43d8698) when `docs/INDEX.md` started quoting
                         # requirement bodies mentioning VR-DST-1 with no pre-migration
                         # counterpart; disclosed rather than fixed there. Fixed here
                         # (2026-09-04, task 17/#20): (f) excludes every path in
                         # `MigrateResult.generated_paths` (Ruling 105 D3/#18 §1), keyed on
                         # the run's own generated-output list, never the literal path.
    "g": FAIL,          # the token-boundary defect                — Ruling 102 §2 row 1
    "h1": DISCLOSE,     # audit-docs.py: FAIL -> DISCLOSE, 2026-09-05 (W37-6 Checkpoint 1
                         # box-end ruling PR). Checks 29/30/35 remain disclosed-and-never
                         # -fatal (owner W37-10, Ruling 105 §B). Every other class was
                         # measured at 948 failure(s) at this PR's base `f35cfe5`, per
                         # `python3 scripts/audit-docs.py` on the migrated snapshot,
                         # classified by check number: check 36=435, check 32=274,
                         # check 1=235, check 5=3, check 2=1 (=948) — same on this PR's
                         # own HEAD, since neither audit-docs.py nor the migration was
                         # touched, only `_docverify.py`'s residue-governance check and
                         # `docs/audit/w37-11-record.md`. Checks 1, 30, 32, 35 and 36
                         # resolve every failure to a real file in the migrated tree's own
                         # tracked-file set (`_h1_residue_by_file`'s resolution rule,
                         # #760) and are filed per-file; checks 2, 5 and 29 carry no
                         # colon-terminated leading token their message resolves to a
                         # file (`FR-1187 referenced but never defined`, `ADR-1
                         # referenced but no file exists`, a backtick-quoted finding id)
                         # and are filed class-level under the sentinel path `(no file
                         # named in message)` — 15 entries (check 2=1, check 5=3,
                         # check 29=11), never claimed as per-file. All 8 classes (1, 2,
                         # 5, 29, 30, 32, 35, 36) are filed in
                         # `docs/audit/w37-11-record.md`; the box-end ruling closes (h1)
                         # by DISCLOSE, not by collapse: `_h1_verdict` now returns
                         # DISCLOSE when every non-disclosed-check hit is filed and
                         # ceilinged there (`_residue_fully_governed`), per-class
                         # disclosure with the ceiling underneath rather than a bare
                         # "98.7%"/"1101"-style headline (that figure, from #760's own
                         # per-file resolution proof, is quotable only as "measured,
                         # every key resolves" — never as a structural guarantee; see
                         # #760's own merge body for the still-open `` `was ``
                         # misattribution defect this record does not paper over).
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


# ---------------------------------------------------------------------------------------
# The W37-11 residue ceiling — a per-(file, class) governor over a ruled DISCLOSE-with-
# residue row, read from the governed record and never from a name in this file.
#
# `EXPECTED_VERDICTS` pins a row's verdict **label** and nothing else (`diff_verdicts`
# above projects every row down to `row.verdict`): a ruled row at residual 1 and the same
# row at residual 50 both `continue` past the comparison, so a regression *into* an already
# -ruled row is invisible to the set-change check. The fix is not a second number pinned
# per row in this file — that repeats the table-hardcoding the forbidden move already
# names, and an exact count makes every legitimate improvement a set change demanding a
# table edit. Instead: a ceiling, keyed per (file, class), read from the governed W37-11
# record (`docs/audit/w37-11-record.md`) the same way `_redirect_map` reads
# `docs/REDIRECTS.csv` — this module carries the loader and the comparison, never a path
# or a row key. Per (file, class) rather than per row because a single row-level ceiling
# lets one file regress while another improves and the row total hides exactly that
# movement.
#
# A `cls` with no entry anywhere in the record is **ungoverned**: this run's residue for
# it is measured (`Row.residue`) but never compared, so wiring a new row's measurement in
# before the record has any entry for it cannot manufacture a false regression — the
# ceiling only ever fires for a `cls` the record already names at least once.
# ---------------------------------------------------------------------------------------

#: Relative to the repo root the run's `verify()` was invoked against — a governance
#: record, not an artifact `migrate()` writes, so it is read from the real tree rather than
#: the migrated snapshot. Markdown, not `.csv`: `backend/tests/test_lineage.py::
#: test_no_reference_rows_are_bundled_in_the_repository` (FR-DATA-32) refuses any bundled
#: `.csv`/`.parquet`/`.xlsx` outside its two named carve-outs, neither of which this
#: hand-authored governance table is — a markdown table, parsed the same way
#: `audit-docs.py`/`doc-index.py`/`register-lint.py` already parse every other table under
#: `docs/`, sidesteps the guard rather than fighting it.
#:
#: Re-exported from `_docid` (one shared constant, Ruling 67 §2's rule the rest of this
#: file already follows for `D_ALTERNATIVES`/`D_DISCLOSED`), because `_docid.
#: GOVERNANCE_RECORD_EXCLUSIONS` also excludes this same path from `tracked_files`'
#: corpus and from `doc-id.py`'s own migration sweep — deputy's condition on PR #756:
#: populating the record must not itself become residue for the rows it governs.
W37_11_RECORD_PATH: Final = _docid.W37_11_RECORD_PATH

RESIDUE_REGRESSION: Final = "REGRESSION (residue exceeds W37-11 ceiling)"
RESIDUE_PROGRESSED: Final = "PROGRESSED (W37-11 record can shrink)"


@dataclass(frozen=True)
class ResidueEntry:
    """One row of the governed W37-11 record: a file's disclosed residue for one ruled
    row/check, carried with the reason it resisted the general mechanism and who owns it.

    `cls` is the deputy's own word for it (`to-lead.md`, 2026-09-05 15:06 BST): "path,
    class (row/check), count, reason[, owner]" — which ruled row or `audit-docs.py` check
    this entry's count belongs to, not a hit-type label. Two entries may share a `path`
    with different `cls` (a file resisting more than one ruled row) or share a `cls` with
    different `path`s (a row's residue spread across several files) — the pair is the key.
    """

    path: str
    cls: str
    count: int
    reason: str
    owner: str = ""


def _residue_fully_governed(
    residue: Mapping[tuple[str, str], int], record: Sequence[ResidueEntry],
) -> bool:
    """True iff every `(path, cls)` hit in `residue` (count > 0) is named in the governed
    W37-11 record (`docs/audit/w37-11-record.md`) at or above its measured count.

    Used to convert a row's `FAIL` into `DISCLOSE` once, and only once, its entire fatal
    residue is filed and ceilinged — the box-end ruling's "closes by DISCLOSE, not by
    collapse" (2026-09-05): a general mechanism that cannot resolve a residual hit
    disclose it, per file, into the record rather than special-casing the file inside this
    module (`CLAUDE.md` §12/§13's fix-the-tool-or-disclose-the-file rule, restated in
    `docs/notes/` as "fix tool / disclose files per-file into W37-11 / never special-case a
    file"). A `cls` the record does not govern at all, or a single file's count exceeding
    its own recorded ceiling, both return `False` — "fully disclosed", never merely "not
    yet flagged" — so a row cannot close by DISCLOSE on an empty or partial record. The
    identical `(path, cls)` shape `check_residue_ceiling` already reads: this is the
    verdict-side use of the same governed table, `check_residue_ceiling` the
    regression-side use — one record, two readers, never two definitions of "governed".
    """
    # An empty `residue` is never "fully governed" — a `FAIL` verdict with nothing to
    # check against the record must stay `FAIL`, not close by vacuous truth over zero
    # entries. Every real caller's residue is non-empty whenever its verdict is `FAIL`
    # (the hit count driving the verdict and the residue breakdown are the same
    # measurement); this guard is for the case that stops being true, not the common one.
    if not residue:
        return False
    ceiling = {(e.path, e.cls): e.count for e in record}
    for key, count in residue.items():
        if count <= 0:
            continue
        limit = ceiling.get(key)
        if limit is None or count > limit:
            return False
    return True


#: `h1-check<n>` for any digit string — a shape predicate, not a hand-listed set of check
#: numbers, because audit-docs.py's own check numbers are unbounded and this registry must
#: not go stale the moment a new check is added. Derived from `_h1_residue_by_file`'s own
#: `f"h1-check{check_no}"` construction (`check_no` is `_H1_FAILURE_LOCATION_RE`/
#: `_H1_CHECK_NUMBER_RE`'s own `(\d+)` capture group), never restated as a literal list.
_H1_CLASS_RE: Final = re.compile(r"^h1-check\d+$")

#: `d<i>` for every `i` `rows_d` actually allocates — `range(1, len(D_ALTERNATIVES) + 1)`,
#: read from `D_ALTERNATIVES` itself (`rows_d`'s own `f"d{i}"`, `enumerate(D_ALTERNATIVES,
#: start=1)`) rather than a hand-typed count, so this set grows the moment a `D_ALTERNATIVES`
#: entry does and never needs a second edit here.
_D_ROW_CLASSES: Final = frozenset(f"d{i}" for i in range(1, len(D_ALTERNATIVES) + 1))


def _known_w37_11_class(cls: str) -> bool:
    """True iff `cls` is a class one of the three extractors (`rows_d`, `row_g`, `rows_h`)
    can actually produce — the registry `load_w37_11_record` checks every row's `cls`
    against, per `InvalidResidueClassError`'s own reasoning. Derived from each extractor's
    own construction (`_D_ROW_CLASSES`, `_G2_RESIDUE_CAUSE_LABELS`, `_H1_CLASS_RE`) rather
    than hand-restated as a fourth, independent list — the identical defect this whole
    registry exists to catch, one level up.
    """
    if cls in _D_ROW_CLASSES:
        return True
    if cls.startswith("g2-") and cls[len("g2-"):] in _G2_RESIDUE_CAUSE_LABELS:
        return True
    return bool(_H1_CLASS_RE.match(cls))


def load_w37_11_record(tree_root: Path) -> tuple[ResidueEntry, ...]:
    """The governed per-(file, class) residue ceiling, or empty if the record has no rows
    yet (or does not exist) — never fatal, and never a reason to invent one here.

    Population is **not this module's to decide** — every path, class, count and reason
    is the deputy's, filed into the record directly; this function only reads it, the
    same relationship `_redirect_map` has with `docs/REDIRECTS.csv`. A malformed data row
    (wrong cell count, a non-integer `count`) is skipped rather than raised — a record this
    module cannot parse must never crash the run that reads it; it degrades to "not yet
    governed" for that row, the same as the file not existing at all.

    A row whose `cls` is not one `_known_w37_11_class` recognises is different: it does
    not degrade quietly, it raises `InvalidResidueClassError`. #763's defect is exactly
    this shape not being caught — a plausible-looking, hand-typed label that governs
    nothing while the real residue moves unnoticed. See `InvalidResidueClassError`'s own
    docstring for why silence is the wrong failure mode here specifically.

    `tree_root` must be a tree materialised from the ref under verification — never the
    live checkout `verify()` was invoked against. `_verify_body` passes `snap.control`
    (2026-09-06 fix): before this fix it passed `repo_root`, the mutable working checkout,
    which made `--ref` non-hermetic — a `--verify` run's row (d)/(h1) verdicts depended on
    whatever sat on disk in the invoking executor's own worktree at call time, regardless
    of which commit `--ref` named. Caught when two runs of the *identical* `--ref` (an
    executor mid-edit on the record) produced different verdict sets and a residue-ceiling
    regression neither run's own tree content could explain — `docs/audit/w37-11-record.md`
    is precisely the legacy `docs/audit/` path row (d10) exists to prove absent from the
    *migrated* tree, so `snap.control` (the archived, unmigrated `--ref` content) is its
    committed home, not `snap.migrated`. See `test_verify_reads_the_w37_11_record_from_the_
    ref_never_the_live_checkout` for the broken-input proof: two `verify()` calls at one
    ref, with the *live* record deliberately changed between them, must return identical
    verdicts — this function's own read is the only thing that could make them diverge.
    """
    record = tree_root / W37_11_RECORD_PATH
    text = read_text(record)
    if text is None:
        return ()
    entries: list[ResidueEntry] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 5 or cells == ["path", "cls", "count", "reason", "owner"]:
            continue
        if set(cells[0]) <= {"-", " "}:  # the `| --- | --- | ... |` separator row
            continue
        path, cls, count_cell, reason, owner = cells
        if not path or not cls or not count_cell.isdigit():
            continue
        if not _known_w37_11_class(cls):
            raise InvalidResidueClassError(
                f"{record}: {cls!r} is not a class any extractor produces (path {path!r})"
                " — a hand-typed label governs nothing; see InvalidResidueClassError's own"
                " docstring"
            )
        entries.append(ResidueEntry(
            path=path, cls=cls, count=int(count_cell), reason=reason, owner=owner,
        ))
    return tuple(entries)


@dataclass(frozen=True)
class ResidueChange:
    """One per-(file, class) movement the W37-11 ceiling found, fatal or not."""

    path: str
    cls: str
    kind: str
    detail: str

    @property
    def fatal(self) -> bool:
        return self.kind == RESIDUE_REGRESSION


def check_residue_ceiling(
    measured: Mapping[tuple[str, str], int],
    record: Sequence[ResidueEntry],
) -> tuple[ResidueChange, ...]:
    """Compare this run's per-(file, class) residue against the governed W37-11 ceiling.

    Three outcomes, per the deputy's ruling (`to-lead.md`, 2026-09-05 15:06 BST):

    * a hit in a file the record does not name, for a `cls` the record DOES govern
      (appears against at least one other file) → fatal `RESIDUE_REGRESSION` — a file the
      record never named.
    * a file's residual above its recorded count → fatal `RESIDUE_REGRESSION` — a
      regression into a ruled row.
    * a recorded (file, class) now measuring zero → non-fatal `RESIDUE_PROGRESSED`; the
      record can shrink, and a shrink is never itself a failure demanding a table edit.

    A `cls` absent from the record entirely is ungoverned and produces no change either
    way — the ceiling only ever fires for a `cls` the record already names at least once,
    so wiring a row's measurement in ahead of the record gaining its first entry for that
    `cls` cannot manufacture a false regression.
    """
    governed_classes = {entry.cls for entry in record}
    ceiling = {(entry.path, entry.cls): entry.count for entry in record}
    changes: list[ResidueChange] = []
    for (path, cls), count in measured.items():
        if cls not in governed_classes or count <= 0:
            continue
        limit = ceiling.get((path, cls))
        if limit is None:
            changes.append(ResidueChange(
                path, cls, RESIDUE_REGRESSION,
                f"{count} hit(s) in a file the W37-11 record does not name for {cls!r}",
            ))
        elif count > limit:
            changes.append(ResidueChange(
                path, cls, RESIDUE_REGRESSION,
                f"{count} hit(s) exceeds the W37-11 record's ceiling of {limit} for "
                f"{cls!r}",
            ))
    for (path, cls), limit in ceiling.items():
        if limit > 0 and measured.get((path, cls), 0) == 0:
            changes.append(ResidueChange(
                path, cls, RESIDUE_PROGRESSED,
                f"the W37-11 record's ceiling of {limit} for {cls!r} now measures 0 at "
                f"{path!r} — the record can shrink",
            ))
    return tuple(changes)


@dataclass(frozen=True)
class VerifyResult:
    snapshot: Snapshot
    rows: tuple[Row, ...]
    #: The governed W37-11 record this run was checked against — `()` when the record has
    #: no rows yet, in which case `residue_changes` is always empty (every `cls` is
    #: ungoverned).
    w37_11_record: tuple[ResidueEntry, ...] = ()

    @property
    def failed(self) -> tuple[Row, ...]:
        return tuple(r for r in self.rows if r.fatal)

    @property
    def set_changes(self) -> tuple[SetChange, ...]:
        return diff_verdicts(self.rows)

    @property
    def measured_residue(self) -> Mapping[tuple[str, str], int]:
        """Every row's own `residue`, merged — each row already keys its own `(path,
        cls)` pairs (`Row.residue`'s own docstring), so this is a union, never a
        re-derivation of which row a file's hits belong to.
        """
        combined: dict[tuple[str, str], int] = {}
        for row in self.rows:
            combined.update(row.residue)
        return combined

    @property
    def residue_changes(self) -> tuple[ResidueChange, ...]:
        return check_residue_ceiling(self.measured_residue, self.w37_11_record)

    @property
    def exit_code(self) -> int:
        """0 green · 1 the standing red, unchanged · 3 the verdict set (or the W37-11
        residue ceiling) moved.

        Exit **3** is the whole point of the row. `1` says "§7 is not satisfied yet", which
        is true of every run until the migration lands and therefore says nothing about the
        change under review. `3` says "this change moved a row", which is the sentence a
        reviewer actually needs and which no reader currently has to hold a baseline to
        reach. (Exit 2 is a refusal to run at all — a misconfiguration, not a corpus state.)
        A fatal `ResidueChange` (a regression into a ruled row's ceiling) is the identical
        kind of news and sets the identical exit code; a `RESIDUE_PROGRESSED` one does not.
        """
        if self.set_changes or any(c.fatal for c in self.residue_changes):
            return 3
        return 1 if self.failed else 0


def compute_rows(
    docid: Any,
    snap: Snapshot,
    generated_paths: Sequence[str] = (),
    record: "Sequence[ResidueEntry]" = (),  # noqa: UP037 -- ResidueEntry defined later
) -> list[Row]:
    """Every §7 (a)-(i) row, over a snapshot whose `migrated/` has already been migrated.

    `generated_paths` is `MigrateResult.generated_paths` from the same `migrate()` call
    that produced this snapshot's `migrated/` tree — (f)'s exclusion (Ruling 105 D3/#18).

    `record` is the governed W37-11 record (`load_w37_11_record`), threaded into the two
    row-families whose verdict can close by DISCLOSE rather than FAIL once their fatal
    residue is filed and ceilinged there (`rows_d`, `rows_h` — `_residue_fully_governed`).
    Every other row ignores it; `()` (the default, and what every pre-existing caller and
    test still passes) makes every row behave exactly as before this parameter existed,
    since an empty record governs nothing.
    """
    mig = load_corpus(snap.migrated)
    ctl = load_corpus(snap.control)
    baseline = load_corpus(snap.baseline) if snap.baseline is not None else None
    rows: list[Row] = [row_a(docid, snap), row_b(docid, snap), row_c(snap)]
    rows.extend(rows_d(docid, mig, ctl, record))
    rows.append(row_e(mig, ctl, snap))
    rows.append(row_f(mig, ctl, baseline, snap, generated_paths))
    rows.append(row_g(docid, snap, mig, ctl))
    rows.extend(rows_h(snap, mig, record))
    rows.append(row_i(snap))
    return rows


#: `dev-commands`'s own `verify_body` wrapper uses these two files
#: (`/tmp/slots/verify-{1,2}`) — deliberately the same namespace `_acquire_verify_slot`
#: locks, for the identical reason `conftest.py`'s gate-slot section gives: a separate
#: namespace would let a wrapped run and an unwrapped one both hold a slot at once,
#: doubling the effective budget instead of enforcing it.
_VERIFY_SLOT_DIR: Any = Path("/tmp/slots")
_VERIFY_SLOT_COUNT = 2
_VERIFY_SLOT_PREFIX = "verify-"
#: Set by the wrapper immediately after its own `flock` succeeds (before the `&&`-chain
#: runs) — its presence means a slot is already held on this process's behalf.
_VERIFY_ANNOUNCEMENT_VAR = "GIP_VERIFY_SLOT"


def _acquire_verify_slot() -> IO[Any] | None:
    """Take a `/tmp/slots/verify-{1,2}` lock for this process, unless the wrapper already
    announced one via `GIP_VERIFY_SLOT` — in which case this returns `None` and `verify()`
    does nothing further, trusting the wrapper's own `flock` rather than acquiring a
    second lock on the same file from inside the child process it already holds it in
    (which would deadlock: a fresh `open()` here is unrelated to the parent's held lock,
    and blocks forever waiting for a lock its own ancestor never releases until this
    process exits — the identical reasoning `conftest.py`'s module docstring gives for
    `GIP_GATE_SLOT`).

    Returns the open file handle when this process took the lock itself, so
    `_release_verify_slot` can tell "I hold this, release it" apart from "the wrapper
    holds it, leave it alone".
    """
    if os.environ.get(_VERIFY_ANNOUNCEMENT_VAR):
        return None
    _VERIFY_SLOT_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(1, _VERIFY_SLOT_COUNT + 1):
        path = _VERIFY_SLOT_DIR / f"{_VERIFY_SLOT_PREFIX}{i}"
        handle = open(path, "w")  # noqa: SIM115 -- held for verify()'s whole body
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            continue
        print(f"[migrate --verify] verify slot {path} acquired, proceeding", file=sys.stderr)
        return handle
    path = _VERIFY_SLOT_DIR / f"{_VERIFY_SLOT_PREFIX}1"
    print(
        f"\n[migrate --verify] both {_VERIFY_SLOT_COUNT} verify slots are busy — waiting "
        f"for {path} to free (.claude/skills/dev-commands/SKILL.md's gate concurrency "
        "budget)",
        file=sys.stderr,
    )
    handle = open(path, "w")  # noqa: SIM115
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)  # blocks until a holder releases
    print(
        f"[migrate --verify] verify slot {path} acquired after waiting, proceeding",
        file=sys.stderr,
    )
    return handle


def _release_verify_slot(handle: IO[Any] | None) -> None:
    if handle is not None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


# ---------------------------------------------------------------------------------------
# INPUT-PROVENANCE TABLE, 2026-09-06. F102's own class ("--ref must be hermetic") was
# found three times by accident tonight before it was named once on purpose: the seed
# hypothesis (ruled out — four runs, three PYTHONHASHSEED values, byte-identical output),
# the reused-directory hypothesis (ruled out — `assert_workdir_disposable` refuses a
# reused target outright, exit 2, before a second run can even start), and the actual
# cause (`load_w37_11_record` reading `repo_root`, the live checkout, instead of
# `snap.control`). Three accidents finding the same class is why this table exists rather
# than trusting the third catch to have been the last one: every input to a §7(a)-(i) row
# verdict or to `VerifyResult.exit_code`/`residue_changes`, traced to its source and
# classified. Audited by reading every row function and the `docid.*` calls it reaches,
# not by grepping one variable name.
#
# HERMETIC (keyed on `snap.migrated`/`snap.control`/`snap.baseline` alone, all three
# themselves `git archive` extractions of `--ref` — see `build_snapshot`/`_materialise`):
#   - row_a, row_b: `docid.classify_docs_files`/`docid.check`/`docid.scan_governed_
#     headers`, each called with `snap.migrated`/`snap.control` directly.
#   - row_c, rows_h: `_run_script(snap.migrated/control, ...)` — the snapshot's OWN copy
#     of doc-index.py/audit-docs.py/req-coverage.py, per `_run_script`'s own docstring
#     ("DO NOT simplify this to call the invoking checkout's copy").
#   - rows_d, row_e, row_f, row_i: `Corpus`/`load_corpus` built from the snap trees;
#     `row_f`'s `baseline` from `snap.baseline`, itself `BASELINE_REF` (a fixed historical
#     SHA constant, `"8f5d57d"`) archived the same hermetic way as `--ref`.
#   - row_g: `docid.classify_migration_diff(snap.control, snap.migrated)` — the trees
#     passed in are hermetic; see the documented exception below for what it loads inside.
#   - `load_w37_11_record(snap.control)` — the F102 fix this table was written beside.
#     `check_residue_ceiling`, `_residue_fully_governed`, `VerifyResult.exit_code`/
#     `.residue_changes`/`.set_changes` are pure functions of the rows and the record
#     above; nothing in that chain reads a tree or the environment directly.
#
# DOCUMENTED EXCEPTIONS (read live state, by design, not by oversight — each verified by
# running the affected test suite, not merely by reading the comment that justifies it):
#   - `doc-id.py`'s `_load_audit_docs`/`_load_register_lint` default to `REPO_ROOT` (the
#     live checkout) rather than the tree `migrate()` is given. `_load_doc_index`'s own
#     docstring (`doc-id.py:931-954`) states the reason directly: these two exist to
#     reuse *stable parsing logic* (register.md's row grammar, check 34's DP-7 freeze
#     predicate) against a target that may carry no tooling of its own — most of
#     `tests/test_doc_id_migrate.py`'s fixtures are exactly that, a bare `docs/` tree with
#     no `scripts/`. An earlier draft of this table tried threading the snapshot's own
#     tree through both call sites anyway, on the theory that `audit-docs.py` is one of
#     the three scripts `_run_script`'s docstring names as migration-rewritten. That
#     broke nothing structurally but a bare fixture has no `scripts/audit-docs.py` to
#     load — reverted before landing here, since a "fix" that fails the suite it
#     touches is not a fix.
#   - The identical shape at `_template_header_lines`/`_stamp_header`: reads
#     `REPO_ROOT / "docs" / "_templates"`, not the tree `migrate()` was given, for the
#     same reason — confirmed empirically: threading `root` through instead made 66 of
#     `test_doc_id_migrate.py`'s tests fail with `FileNotFoundError`, because those
#     fixtures have no `docs/_templates/` of their own and were relying on exactly this
#     fallback. Not previously named alongside `_load_audit_docs`/`_load_register_lint`
#     in `_load_doc_index`'s comment; it belongs in the same bucket and is named here so
#     the next reader does not have to rediscover it by breaking the suite.
#   - `_run_script`'s subprocess env (`env = dict(os.environ)`, two keys overridden) —
#     an allow-list-of-two over a full live-environment copy, the wrong shape for
#     "hermetic by construction" in the abstract, but not fixed here: none of doc-index.py
#     /audit-docs.py/req-coverage.py reads `os.environ` directly (checked), so the actual
#     exposure is `git`'s own env-var sensitivity (`GIT_DIR` etc.) inside those scripts'
#     own subprocess calls — real but unobserved, and narrowing the scrub is exactly the
#     kind of subprocess-plumbing change this table's `_template_header_lines` near-miss
#     argues for testing thoroughly rather than shipping same-night.
#   - A handful of `date.today()` reads inside `migrate()`'s writers (`doc-id.py:2383,
#     2386, 7557, 7739, 8571`) stamp a `created:`/comparison date from the wall clock.
#     Affects written content, not a row's pass/fail shape, except in the (unobserved,
#     midnight-boundary-only) case where `row_g`'s class-6 oracle
#     (`_run_second_migration`) reruns `migrate()` on the opposite side of midnight from
#     the first run and a date-stamped file's regenerated content disagrees only on that
#     field. Named, not fixed, for the same "narrow but untested" reason as the env scrub.
#   - `_acquire_verify_slot`'s `os.environ.get(_VERIFY_ANNOUNCEMENT_VAR)` and the
#     `/tmp/slots/*` lock files: concurrency control over *when* `verify()` runs, never
#     *what* it measures — gates entry, never feeds a row.
# ---------------------------------------------------------------------------------------


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
    # The refusal check runs BEFORE the slot lock, deliberately: `_cmd_migrate_verify`'s
    # own contract is "'I would not run' and 'I ran and it is red' must not share an exit
    # code" (`tests/test_doc_id_verify.py::test_cli_refusal_exits_2_not_1`), and a refusal
    # is meant to be instant regardless of how busy the machine's verify slots are. Only
    # `workdir` explicitly given is checked here; the `workdir is None` branch's own
    # disposability is trivial (a fresh `TemporaryDirectory` is always disposable) and
    # stays inside `_verify_body`, which builds it.
    if workdir is not None:
        assert_workdir_disposable(workdir.expanduser().resolve())
    slot_handle = _acquire_verify_slot()
    try:
        return _verify_body(
            docid, repo_root=repo_root, ref=ref, workdir=workdir, keep=keep,
            with_baseline=with_baseline,
        )
    finally:
        _release_verify_slot(slot_handle)


def _verify_body(
    docid: Any,
    *,
    repo_root: Path,
    ref: str,
    workdir: Path | None,
    keep: bool,
    with_baseline: bool,
) -> VerifyResult:
    """`verify()`'s own work, unchanged except that the `workdir`-given disposability
    check now runs in `verify()` itself (before the slot lock) — factored out so that
    lock wraps everything else without this function needing to know it exists.
    """
    tmp: tempfile.TemporaryDirectory[str] | None = None
    if workdir is None:
        tmp = tempfile.TemporaryDirectory(prefix="doc-id-verify-")
        target = Path(tmp.name)
    else:
        target = workdir.expanduser().resolve()
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
        # Loaded before `compute_rows` (not after, as before this change): (d)'s and
        # (h1)'s own verdicts now read the record to decide FAIL-vs-DISCLOSE
        # (`_residue_fully_governed`), so it must exist before those rows are computed,
        # not only afterward for the exit-code-level residue-ceiling comparison.
        #
        # `snap.control`, never `repo_root` (2026-09-06 fix, F102): `repo_root` is the
        # live, mutable checkout — reading the record from it made `--ref` non-hermetic,
        # since the record on disk in the invoking executor's own worktree need not match
        # (and during active editing, will not match) the commit `--ref` names.
        # `snap.control` is the `git archive` of `--ref` this run already built, the
        # record's own committed home (`docs/audit/` is the legacy path row (d10) proves
        # absent from `snap.migrated`, never where the record lives post-migration), and
        # reading it costs no new git call. See `load_w37_11_record`'s own docstring and
        # `test_verify_reads_the_w37_11_record_from_the_ref_never_the_live_checkout`.
        record = load_w37_11_record(snap.control)
        rows = compute_rows(docid, snap, mig_result.generated_paths, record)
        return VerifyResult(snapshot=snap, rows=tuple(rows), w37_11_record=record)
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
    out.extend(_residue_change_block(result))
    return out


def _residue_change_block(result: VerifyResult) -> list[str]:
    """The W37-11 ceiling's own findings — a ruled row's label alone cannot report a
    regression *into* it (a residual of 1 and a residual of 50 both read the same
    `EXPECTED_VERDICTS` entry), so this reads the governed per-(file, class) record
    directly rather than trusting the row verdict to have noticed.
    """
    changes = result.residue_changes
    if not changes:
        return []
    out = [
        f"W37-11 RESIDUE CEILING ({len(changes)}): a governed (file, class) entry moved."
    ]
    for change in changes:
        out.append(f"  {change.kind}: {change.path!r} ({change.cls}) — {change.detail}")
    if any(c.fatal for c in changes):
        out.append(
            "  A fatal one: residue grew past the W37-11 record's own ceiling, or "
            "appeared in a file the record never named — a regression into an already-"
            "ruled row that the row's verdict label alone cannot show."
        )
    return out
