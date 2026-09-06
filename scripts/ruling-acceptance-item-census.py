#!/usr/bin/env python3
"""Census over every ruling heading in `docs/plans/`, classifying its acceptance item (if
any) by which of this repository's three phrasing conventions states it — RL-985's
property (`docs/rulings/INDEX.md#2026-09-02-w37-guard-arithmetic-and-ledger-family-rulingsmd`)
applied to convention discovery rather than to a family census: **every candidate falls
into exactly one bucket or a named exception, and the buckets sum to the total.**

Filed alongside `docs/research/RS-01003-ruling-acceptance-item-sweep-audit-record.md` §8's table (originally a
separate CSV of the same name; dropped 2026-09-02 — FR-72's reference-data-bundling
guard cannot cover a hand-classified census, only a regenerate-and-diff one, and §8 states
why in full), which records the SEMANTIC
classification (CONSTRUCTIBLE / INVALIDATED / VACUOUS AT BIRTH / INDICATIVE /
CANNOT_DETERMINE / NONE_FOUND) that no script can derive — that requires reading the
governed code the item checks. **This script answers a narrower, mechanical question
only: did the sweep find every acceptance item there was to find, or did its enumeration
method have a blind spot?** A fourth phrasing convention introduced by a future ruling
shows up here as a heading the buckets do not sum to cover, not as a form nobody
remembered to grep for.

Three known conventions, found by reading the corpus rather than assumed:

  1. **WK-697 series** (Rulings 66-95, dated 2026-09-02): a heading matching
     `_W37_HEADING_RE` inside the ruling's own section — `### N. Acceptance — the
     violation that must become detectable` (N varies with how many subsections precede
     it).
  2. **WK-671 series** (Rulings 6-30ish, dated 2026-08-29): a bold inline marker matching
     `_W11_MARKER_RE` — `**Acceptance test — ...**`, wording after the em dash varies
     (`expressible`, `impossible`, `stated as the violation`).
  3. **Standalone-file series** (Rulings 59-61, each its own H1-headed file): a heading
     matching `_STANDALONE_HEADING_RE` — `## N. Broken-input proof`.

One named exception, regex-shaped: **RL-916** states two tests ("Two tests, each
stated as a violation that must become impossible:") that match none of the three
regexes above. Found only by reading the ruling's full body; named here rather than
turned into a fourth regex, because a pattern built to match this one sentence would be
fitted to a population of one and would not generalise.

**A second, larger, and more honest exception: `_PROSE_ONLY_RULINGS` below.** The sweep
this script accompanies (`docs/research/RS-01003-ruling-acceptance-item-sweep-audit-record.md` §2) found that ten
rulings — 40, 42, 43, 45, 46, 47, 50, 51, 54, 60 — state a genuine, testable acceptance
item in ordinary prose with **no shared marker at all**: sometimes "§N's broken-input
proof:", sometimes "Its acceptance evidence is...", sometimes "so this is testable rather
than hortatory", once (RL-950) a re-confirmation of a **different, named** ruling's
broken-input cases rather than a fresh statement of its own. **No single regex covers
this set without overfitting to it** — a pattern loose enough to catch all ten also
matches ordinary prose that is not an acceptance item (the corpus's own "the check is",
"testable definition of done" near-misses). This is therefore a **hand-verified list,
not a derived one**, and it is the one place this module's own promise — "the arithmetic
catches an undercount" — does not hold: a future ruling using this same loose, marker-free
style would land silently in `none` below, not in a bucket whose count visibly moved.
Flagged rather than hidden behind a regex that would only look like coverage.

A ruling matching **zero** conventions and not on either exception list is NONE_FOUND —
most of the corpus (Rulings 1-5, 31-38 etc.) predates the acceptance-item convention
entirely, and 52/53/55-58/62-65/A1-3 state only an "Overridden if" scope clause with no
violation condition (`docs/research/RS-01003-ruling-acceptance-item-sweep-audit-record.md` §4's rule: that clause
is never itself an acceptance item). This is the expected, majority case, not a defect.

A ruling matching **more than one** convention is a CONFLICT, printed and left for a
human — it has never happened in the corpus this script has been run against, and this
script does not guess which one is authoritative.

**Ruling-form flag-day, 2026-09-02 (maintainer ruling, discharged at `#623`'s merge,
`aab6327`): every ruling filed after the flag-day must use the WK-697 form.** Before the
flag-day, `none` was the expected, majority case (most of the corpus predates the
acceptance-item convention entirely). After it, `none` is only still expected for the
35 rulings that were already in that bucket when the flag-day landed -- a **post**-flag-day
ruling with no acceptance item is a violation, not a member of the majority case, and
`main` fails on it. **The date is the discriminator, not the ruling number**, which is
not monotonic in time (a later-numbered ruling can be filed before an earlier-numbered
one lands, and the reverse) -- so each `none`-bucket heading's own introduction commit is
resolved individually (`git log -S` pickaxed on that heading's own line, scoped to the
file it lives in), never read off the file's creation date or the ruling's own number.
Using the **author** date rather than the committer date is deliberate: a rebase or an
amend changes the committer date and the SHA but preserves the author date unless someone
deliberately backdates, so this predicate survives both. A ruling appended to a file whose
*own* first commit predates the flag-day is still correctly dated by its own heading's
introduction commit, not the file's -- this is the trap a coarser predicate (file mtime,
file's first commit, ruling number) would fall into, and why none of those is used.

Usage: `python3 scripts/ruling-acceptance-item-census.py [--root PATH]`
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

REPO_ROOT: Final = Path(__file__).resolve().parent.parent

#: `#623`'s merge commit -- the maintainer's ruling-form flag-day, 2026-09-02. A `none`-
#: bucket ruling introduced at or before this commit is grandfathered; after it, a
#: violation. Frozen at this value the same way `_NAMED_EXCEPTIONS` and
#: `_PROSE_ONLY_RULINGS` are frozen -- a later commit does not move the flag-day.
_FLAG_DAY_COMMIT: Final = "aab6327"

#: Every canonical "Ruling N" / "Ruling AN" heading, at heading depth 1-3 (the three
#: standalone files use `#`, the ordinary rulings files use `##`, the A-series uses
#: `###`). Excludes a title that merely *mentions* an existing ruling's number — the
#: `'s` alternative below exists only to name that exclusion in one place, since
#: `docs/rulings/RL-00994-the-fixture-is-rebuilt-on-the-property-not-the-level-and-the-container-is-identified-positively.md`'s own H1 ("RL-979's
#: second acceptance item, amended...") matches `RL-979` followed by `'s`, not by an
#: em dash, and is the document's title rather than a second declaration of RL-979.
_RULING_HEADING_RE: Final = re.compile(
    r"^(#{1,3})\s+Ruling\s+(\d+|A\d+)\s+—", re.MULTILINE
)

#: WK-697 series: a heading, at any level and any leading number, containing this exact
#: phrase. Verified against the corpus at the sweep's pin: 29 occurrences, 29 WK-697-series
#: rulings (66-94), one each -- RL-984 (filed after the pin) makes it 30-of-30 today.
_W37_HEADING_RE: Final = re.compile(
    r"^#+\s+.*Acceptance.*violation that must become detectable", re.MULTILINE
)

#: WK-671 series: a bold inline marker. The wording after "Acceptance test" varies
#: (`— the violation that must become expressible`, `, stated as the violation that must
#: become impossible`, `, stated as the violation`, or a bare `.`) -- captured by
#: requiring only the anchor phrase, not the variable tail.
_W11_MARKER_RE: Final = re.compile(r"\*\*Acceptance test\b")

#: Standalone-file series (Rulings 59-61): a numbered "Broken-input proof" heading.
_STANDALONE_HEADING_RE: Final = re.compile(
    r"^##\s+\d+\.\s+Broken-input proof", re.MULTILINE
)

#: RL-916: matches none of the three regexes above and is not itself a fourth regex,
#: per this module's own docstring. Hand-verified at the sweep's pin; any addition to
#: this set must cite the reading, not a pattern, in the commit that adds it.
_NAMED_EXCEPTIONS: Final[frozenset[str]] = frozenset({"44"})

#: Ten rulings whose acceptance item is genuine prose with no shared marker -- see this
#: module's docstring for why no regex covers this set without overfitting to it. A
#: SEPARATE bucket from `_NAMED_EXCEPTIONS` because it is not a "the pattern is this one
#: sentence" exception; it is an admission that this style has no pattern. Hand-verified
#: at the sweep's pin (`docs/research/RS-01003-ruling-acceptance-item-sweep-audit-record.md` §2); any addition
#: must cite the reading in the commit that adds it, the same rule as `_NAMED_EXCEPTIONS`.
_PROSE_ONLY_RULINGS: Final[frozenset[str]] = frozenset(
    {"40", "42", "43", "45", "46", "47", "50", "51", "54", "60"}
)


@dataclass(frozen=True)
class RulingHeading:
    number: str
    file: Path
    start: int
    end: int


def _discover_ruling_headings(root: Path) -> list[RulingHeading]:
    """Every `Ruling N`/`Ruling AN` heading under `docs/plans/`, each paired with the
    span of its own section -- from its heading to the next ruling heading in the same
    file, or end of file. Multiple ruling files are handled independently; headings are
    returned in file, then position, order.
    """
    headings: list[RulingHeading] = []
    for path in sorted((root / "docs" / "plans").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        matches = list(_RULING_HEADING_RE.finditer(text))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            headings.append(RulingHeading(number=m.group(2), file=path, start=m.start(), end=end))
    return headings


def _section_text(root: Path, heading: RulingHeading) -> str:
    return heading.file.read_text(encoding="utf-8")[heading.start : heading.end]


def _commit_author_date(root: Path, commit: str) -> str:
    """ISO-8601 author date of `commit`. Raises `RuntimeError` naming the commit rather
    than returning `None` or a sentinel -- a flag-day comparison that cannot resolve one
    side is not silently skipped (the failure mode RL-949's `generated_from_tracked_
    corpus` refuses the same way, for the same reason: 'cannot verify, so allow it' is
    the class of bug this repository keeps re-finding).
    """
    proc = subprocess.run(
        ["git", "-C", str(root), "show", "-s", "--format=%aI", commit],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError(f"cannot resolve commit {commit!r}: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _heading_introduced_at(root: Path, heading: RulingHeading) -> str:
    """ISO-8601 **author** date of the commit that first introduced `heading`'s own
    line -- via `git log -S` pickaxed on `"Ruling {number} —"`, scoped to the file the
    heading lives in, never on the file as a whole. Author date, not committer date: a
    rebase or `git commit --amend` changes the SHA and the committer date but preserves
    the author date unless someone deliberately backdates, so this predicate survives
    both. Raises `RuntimeError` naming the ruling if no commit is found, rather than
    treating an unresolvable heading as pre-flag-day by default -- the same
    raise-rather-than-guess rule `_commit_author_date` follows.
    """
    anchor = f"Ruling {heading.number} —"
    rel = heading.file.relative_to(root).as_posix()
    proc = subprocess.run(
        ["git", "-C", str(root), "log", "--reverse", "--format=%aI", "-S", anchor,
         "--", rel],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Ruling {heading.number}: git log failed resolving its introduction date: "
            f"{proc.stderr.strip()}"
        )
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(
            f"Ruling {heading.number}: no commit in {rel}'s history introduces the "
            f"heading line {anchor!r} -- uncommitted, or the anchor text does not match "
            "what is on disk"
        )
    return lines[0]


def flag_day_split(
    root: Path, none_headings: list[RulingHeading]
) -> tuple[list[RulingHeading], list[RulingHeading]]:
    """Split the `none` bucket into `(grandfathered, violations)` by each heading's own
    introduction date against `_FLAG_DAY_COMMIT`'s author date -- grandfathered if at or
    before the flag-day, a violation if strictly after. Kept separate from `classify`,
    which stays a pure function over file text with no git calls, so `classify` alone
    stays testable without a repository and this split is independently testable against
    a synthetic one.
    """
    # Compared as timezone-aware datetimes, not as raw ISO-8601 strings: git's `%aI`
    # preserves the author's own UTC offset, which need not agree between two commits
    # (one contributor's afternoon commit and another's, in a different offset, sort
    # wrong under a lexicographic string compare unless every commit happens to share
    # one offset -- true of this corpus so far, and not a fact to depend on).
    flag_day_date = datetime.fromisoformat(_commit_author_date(root, _FLAG_DAY_COMMIT))
    grandfathered: list[RulingHeading] = []
    violations: list[RulingHeading] = []
    for heading in none_headings:
        introduced = datetime.fromisoformat(_heading_introduced_at(root, heading))
        (violations if introduced > flag_day_date else grandfathered).append(heading)
    return grandfathered, violations


def classify(root: Path = REPO_ROOT) -> dict[str, list[RulingHeading]]:
    """Buckets: `w37`, `w11`, `standalone`, `exception`, `prose_only`, `none`,
    `conflict`. Every heading `_discover_ruling_headings` finds appears in exactly one
    bucket -- the property this module exists to keep true, asserted by `main` below
    rather than merely hoped for by this function's own construction. `prose_only` is
    hand-verified, not regex-derived -- see `_PROSE_ONLY_RULINGS`'s own comment for why,
    and do not read a heading landing there as "the classifier found it": it did not.
    """
    buckets: dict[str, list[RulingHeading]] = {
        "w37": [], "w11": [], "standalone": [], "exception": [], "prose_only": [],
        "none": [], "conflict": [],
    }
    for heading in _discover_ruling_headings(root):
        section = _section_text(root, heading)
        hits = []
        if _W37_HEADING_RE.search(section):
            hits.append("w37")
        if _W11_MARKER_RE.search(section):
            hits.append("w11")
        if _STANDALONE_HEADING_RE.search(section):
            hits.append("standalone")
        if len(hits) > 1:
            buckets["conflict"].append(heading)
        elif len(hits) == 1:
            buckets[hits[0]].append(heading)
        elif heading.number in _NAMED_EXCEPTIONS:
            buckets["exception"].append(heading)
        elif heading.number in _PROSE_ONLY_RULINGS:
            buckets["prose_only"].append(heading)
        else:
            buckets["none"].append(heading)
    return buckets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    buckets = classify(args.root)
    total = sum(len(v) for v in buckets.values())
    discovered = len(_discover_ruling_headings(args.root))

    for name in ("w37", "w11", "standalone", "exception", "prose_only", "none", "conflict"):
        items = buckets[name]
        print(f"{name}: {len(items)}")
        if name == "conflict":
            for h in items:
                print(
                    f"  CONFLICT: Ruling {h.number} in {h.file.name} "
                    "matches more than one convention"
                )

    print(f"total classified: {total}")
    print(f"total headings discovered: {discovered}")

    # Ruling-form flag-day (see module docstring): split `none` by each heading's own
    # introduction date. Printed unconditionally, the zero included (`RFC-789`) -- a
    # passing "0 post-flag-day violations" line says which zero was checked, rather than
    # letting an empty violations list look identical to the split never having run.
    grandfathered, post_flag_day_violations = flag_day_split(args.root, buckets["none"])
    print(
        f"none, grandfathered (introduced at or before {_FLAG_DAY_COMMIT}): "
        f"{len(grandfathered)}"
    )
    print(
        f"none, post-flag-day violations (introduced after {_FLAG_DAY_COMMIT}): "
        f"{len(post_flag_day_violations)}"
    )
    for h in post_flag_day_violations:
        print(f"  VIOLATION: Ruling {h.number} in {h.file.name} has no acceptance item "
              f"and was introduced after the ruling-form flag-day ({_FLAG_DAY_COMMIT})")

    if total != discovered:
        print(
            f"FAIL: {total} classified != {discovered} discovered -- a heading was "
            "counted twice or dropped",
            file=sys.stderr,
        )
        return 1
    if buckets["conflict"]:
        print(
            f"FAIL: {len(buckets['conflict'])} ruling(s) matched more than one convention",
            file=sys.stderr,
        )
        return 1
    if post_flag_day_violations:
        print(
            f"FAIL: {len(post_flag_day_violations)} ruling(s) filed after the ruling-form "
            "flag-day carry no acceptance item",
            file=sys.stderr,
        )
        return 1
    print("PASS: every discovered ruling heading falls into exactly one bucket, and "
          "every post-flag-day ruling carries an acceptance item")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
