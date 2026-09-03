"""NT-0016 Slice 4: after the notes move, the old notes root under `.claude` may be cited
only by its own tombstone, by files frozen under `docs/plans/README.md`'s write-once rule,
by check 30's own mechanism (Ruling 61 -- the check that *watches* the old path necessarily
names it), by provenance-locked historical artifacts generated before the move landed, and
by a maintainer-accepted note that *specifies* the old path's eventual deletion rather than
merely citing it (`_SPECIFICATIONS_OF_THE_OLD_PATH` below -- added 2026-09-02 for NT-0019,
see that constant's own comment for what this narrow exemption stops catching).

This is the slice's own TDD leaf, per
`docs/plans/2026-08-31-nt-0016-investigation.md` §9 Step 1: the invariant the move must
establish, written and run to failure *before* the `git mv` of the notes directory to
`docs/notes` and the mechanism edits, rather than asserted after the fact. A count of living
citations differing from the plan's own re-derivation is expected -- the citation surface
moves day to day (see the plan's §1a) -- but the *classes* the citations fall into should
match what §1a and Ruling 58 of `docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`
describe: frozen plans (untouched, C4), and everything else (edited by the move).

**Widened 2026-09-01 for Ruling 61** (`docs/plans/2026-09-01-ruling-61-notes-tombstone-
stubs-watched.md`): the ruled tombstone gained 18 per-file redirect stubs at the vacated
path plus a new check (30) that watches them, both landed after this test was first
written. The check's own implementation and its test necessarily and permanently name the
old path -- that is not a citation left behind by the move, it is the move's own watch
mechanism -- so `EXEMPT_FILES` below names them explicitly rather than widening the
`docs/plans/`-shaped carve-out to something looser. Two more exemptions came from a
rebase-time interaction, not from this slice's own work: `docs/audit/file-census-5ef559d.csv`
and `docs/audit/file-taxonomy-draft.md` (landed on `main` under PRs #537/#545 while this
branch was open) are provenance-locked snapshots of the tree as it stood at `4f95fb3`,
*before* this move -- editing either to say `docs/notes/` would misrepresent what was true
at the tree the filename itself pins, the same reason a frozen plan is not edited.

No `@pytest.mark.req` marker: this is a check on the repository's own citation surface, not
evidence for a numbered platform requirement -- the same reasoning
`tests/test_audit_docs_scan_roots.py` and `tests/test_audit_docs_finding_citations.py` give
their own unmarked tests.
"""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The check that watches the old path, its skill documentation, and its own test all
# name the old path deliberately and permanently. Originally check 30 (Ruling 61,
# `check_notes_tombstone`, watching the tombstone stubs' own content); renamed 2026-09-02
# to check 36 (`check_redirects`, NT-0019 §5.5 -- "check_notes_tombstone" -> "check_redirects",
# `docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md` Slice W37-4) when
# `check_notes_tombstone`'s job became watching REDIRECTS.csv instead, and its own test
# file (`tests/test_audit_docs_notes_tombstone.py`) was deleted per NT-0019 §5.7 and
# folded into `tests/test_audit_docs_ids.py`, which now carries the same permanent,
# deliberate citation as part of check 36's own legacy-form-sweep positive control.
_CHECK_30_MECHANISM = {
    "scripts/audit-docs.py",
    ".claude/skills/docs-audit/SKILL.md",
    "tests/test_audit_docs_ids.py",
}

# Provenance-locked historical artifacts generated before this move landed (PRs #537/#545,
# tree 4f95fb3) -- frozen by the same reasoning as a docs/plans/ file, just outside that
# directory. Named explicitly rather than derived, so a future addition to this class does
# not silently widen the exemption without a reviewer seeing it.
_PRE_MOVE_SNAPSHOTS = {
    "docs/audit/file-census-5ef559d.csv",
    "docs/audit/file-taxonomy-draft.md",
}

# The class: a document that *specifies or verifies NT-0019's own future migration* of
# this exact path, rather than a stale reference left over from the NT-0016 move this test
# otherwise polices. NT-0019 (`docs/notes/0019-one-id-per-document.md`) is itself the
# reason this class exists at all: its own §4 step 4 will *delete* the stub files check 30
# watches, so both it and everything that verifies it against the tree necessarily name the
# path being deleted. `docs/plans/` already has a blanket carve-out above for the same
# reason (frozen, write-once); this set is for the same class of document living *outside*
# that directory, where no blanket rule exists and each one needs a reviewed, named entry.
#
# Two members so far, both audited directly rather than assumed current: NT-0019 names the
# old notes root under `.claude` twice (deliberately not written as one contiguous string
# in this comment, for the same self-referential reason the module docstring gives below)
# -- §4 step 4's migration instruction, and §7(d)'s acceptance grep, which must contain the
# literal pattern among the tokens a *later* migration tree is checked to no longer
# contain. `docs/audit/nt-0019-verification-and-impact-sweep.md` (PR #560, merged
# 2026-09-02, the day after NT-0019 itself) names it once, in its own §5.3/§5.4 scope note,
# listing the directories NT-0019's impact-map sweep covers. Confirmed by re-running this
# test against the merged tip that added it: exactly one new offender, that file alone --
# not NT-0019 itself, which the exemption below already covered; a claim from outside this
# session that a second, different file was *also* newly implicated did not hold up against
# a direct check of the actual failure at that tree and is not reflected here.
#
# Why an explicit set and not a structural rule (e.g. "exempt any file that also cites
# `NT-0019`"): a content-marker match would let the exemption widen itself the moment any
# document -- and W37, NT-0019's own migration workstream, is going to produce several --
# happens to mention `NT-0019` anywhere in a large file, without a reviewer ever choosing
# that specific file. That is exactly the failure mode `OLD_NOTES_STUB_NAMES` (in
# `audit-docs.py`) and `_PRE_MOVE_SNAPSHOTS` above were each already written to avoid, for
# the same stated reason: a derived or pattern-matched set lets one edit defeat both the
# content it changes and the check meant to catch it. Consistency with that established
# choice, not novelty, is why this set is named the same way.
#
# This is a deliberate, bounded stopgap, not a design meant to outlive its problem: NT-0019
# §5.7 lists this exact test file (with test_audit_docs_notes_tombstone.py) as **deleted**
# by its own migration, replaced by `test_audit_docs_redirects.py`. Building a sturdier
# mechanism for a check with a short, already-scheduled remaining lifespan would be solving
# a problem past the point it stops existing.
#
# What this stops catching, and what it does not: a *stray*, wrong citation of the old path
# added anywhere else inside either of these two named files -- by a future dated
# correction appended to NT-0019, say, or a later edit to the audit record -- would no
# longer fail this test, since the exemption is by filename, not by line or by the specific
# occurrences audited above. That risk is accepted narrowly for these two files; it is not
# extended to any other file. It does **not** stop catching a new, third document elsewhere
# in the tree that cites the old path for this same legitimate reason -- W37 will produce
# more of them before the migration lands, each will fail this test the same way PR #560's
# did, and each needs its own reviewed line added here, not a widened pattern.
# Two more reviewed in 2026-09-02, within the hour of the pair above landing --
# both audit records *about* this same migration, forbidden from resolving the
# path without naming it: `F71.md` documents what `test_notes_move_citations`
# (this file) forbids and cites the old path to say so; `register.md`'s F71 row
# describes the pre-#561 state of this exact exemption, which did not yet cover
# the note or the sweep. Reviewed in per this set's own rule, not widened into
# one: two members to four in about one hour, all four documents *about* the
# migration rather than migrated content. That rate, not an opinion about it, is
# recorded in F71's own essay for a future reader if the list keeps growing.
_SPECIFICATIONS_OF_THE_OLD_PATH = {
    "docs/notes/0019-one-id-per-document.md",
    "docs/audit/nt-0019-verification-and-impact-sweep.md",
    "docs/audit/findings/F71.md",
    "docs/audit/register.md",
    # Reviewed in 2026-09-03, and the first member of this set that is code rather than a
    # document. `scripts/_docverify.py` is Ruling 102 §1's instrument, and its
    # `D_FULL_PATTERN` is NT-0019 §7(d)'s grep **verbatim** — a constant whose whole
    # purpose is that a reader can check the per-alternative decomposition against the
    # acceptance sentence it came from. One of those thirteen alternatives is the old
    # notes path, and the script's job is to *count occurrences of it* and fail while any
    # remain. Building that one alternative by concatenation, the way this test file
    # builds its own search term, would hide the literal and defeat the constant's reason
    # for existing; the reviewed exemption is the mechanism this comment block already
    # prescribes for exactly this case ("each needs its own reviewed line added here, not
    # a widened pattern"). It is a specification of the path, not a citation of it: when
    # the migration lands, this row goes to zero and the exemption can go with it.
    "scripts/_docverify.py",
    # Reviewed in 2026-09-03 by the auditor, against its own two documents -- members six
    # and seven, and the second reviewed pair of the same day. Both are records of the
    # NT-0019 §7 second measurement, and neither can state its finding without naming the
    # old path: the finding is that §7(d)'s alternative for that path is **inert**, because
    # the pattern's leading `\b` cannot fire before a `.` and so matches only where a word
    # character precedes the dot -- which no real citation does. Demonstrating it requires
    # quoting the alternative, the §7(d) pattern containing it, and a census of the
    # character preceding each occurrence in the corpus. Ten occurrences in the record and
    # one in F101's class table; every one a specification, none a citation to follow.
    #
    # **Disclosure, applying to this entry the caveat the auditor raised against
    # `_docverify.py`'s**: the exemption is by filename, so a *later* edit to either file
    # citing the old path for an ordinary reason would ride along unflagged. Accepted for
    # the same reason it was accepted there -- a per-occurrence exemption in a document
    # whose subject is those occurrences would be worse -- and written down rather than
    # left implicit, because an auditor adding itself to a reviewed list owes the
    # disclosure it asks of others. Members two to seven in about a day is the rate F71's
    # essay asks a future reader to watch; recorded here, not judged here.
    #
    # This comment deliberately does not contain the path literal. The first draft did, and
    # made this test flag its own source -- the self-referential trap the block above names
    # and the reason `old_path` is built by concatenation.
    "docs/research/nt-0019-second-measurement-2026-09-03.md",
    "docs/audit/findings/F101.md",
}


def test_no_living_file_cites_the_old_notes_path() -> None:
    """After the move, the old notes root under `.claude` may be named only by the
    tombstone README left there, by files frozen under `docs/plans/`, by check 30's own
    watching mechanism, by pre-move provenance-locked snapshots, and by a maintainer-accepted
    note that specifies the path's eventual deletion (`_SPECIFICATIONS_OF_THE_OLD_PATH`).

    A frozen plan is never edited to agree with a later move (`docs/plans/README.md`'s
    write-once rule, NT-0016 C4) -- the tombstone this slice creates at the vacated path
    is what keeps a path citation inside one of them resolving. Every other tracked file
    that still names the old path is a living citation this slice must repair.
    """
    # Built by concatenation, not written as one literal: this test file is itself part of
    # the tracked corpus it scans, and a literal occurrence of the old path in this source
    # line would make the test flag itself -- the self-referential trap a fixed offset or a
    # search term risks when the search runs over the file that states it.
    old_path = ".claude" + "/" + "notes"
    tracked = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=ROOT, check=True
    ).stdout.split()
    exempt = _CHECK_30_MECHANISM | _PRE_MOVE_SNAPSHOTS | _SPECIFICATIONS_OF_THE_OLD_PATH
    offenders = [
        f
        for f in tracked
        if old_path in (ROOT / f).read_text(encoding="utf-8", errors="replace")
        and not f.startswith("docs/plans/")
        and f != old_path + "/README.md"
        and f not in exempt
    ]
    assert offenders == [], offenders
