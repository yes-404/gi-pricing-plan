"""RFC-897 Slice 4: after the notes move, the old notes root under `.claude` may be cited
only by its own tombstone, by files frozen under `docs/plans/README.md`'s write-once rule,
by check 30's own mechanism (RL-951 -- the check that *watches* the old path necessarily
names it), by provenance-locked historical artifacts generated before the move landed, and
by a maintainer-accepted note that *specifies* the old path's eventual deletion rather than
merely citing it (`_SPECIFICATIONS_OF_THE_OLD_PATH` below -- added 2026-09-02 for RFC-937,
see that constant's own comment for what this narrow exemption stops catching).

This is the slice's own TDD leaf, per
`docs/plans/PL-00929-rfc-897-file-taxonomy-reference-coding-and-custody-research-and-the-slice-cut.md` §9 Step 1: the invariant the move must
establish, written and run to failure *before* the `git mv` of the notes directory to
`docs/notes` and the mechanism edits, rather than asserted after the fact. A count of living
citations differing from the plan's own re-derivation is expected -- the citation surface
moves day to day (see the plan's §1a) -- but the *classes* the citations fall into should
match what §1a and RL-948 of `docs/rulings/RL-00948-q7-notes-half-only-cite-notes-by-nt-00nn-id-path-citations-are-rejected-for-this-one-category.md`
describe: frozen plans (untouched, C4), and everything else (edited by the move).

**Widened 2026-09-01 for RL-951** (`docs/rulings/RL-00951-rl-947-s-tombstone-gains-p
er-file-stubs-watched-by-a-new-check-not-left.md`): the ruled tombstone gained 18 per-file redirect stubs at the vacated
path plus a new check (30) that watches them, both landed after this test was first
written. The check's own implementation and its test necessarily and permanently name the
old path -- that is not a citation left behind by the move, it is the move's own watch
mechanism -- so `EXEMPT_FILES` below names them explicitly rather than widening the
`docs/plans/`-shaped carve-out to something looser. Two more exemptions came from a
rebase-time interaction, not from this slice's own work: `docs/research/file-census-5ef559d.csv`
and `docs/research/RS-00953-file-taxonomy-draft-rfc-897-stage-1.md` (landed on `main` under PRs #537/#545 while this
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
# name the old path deliberately and permanently. Originally check 30 (RL-951,
# `check_notes_tombstone`, watching the tombstone stubs' own content); renamed 2026-09-02
# to check 36 (`check_redirects`, RFC-937 §5.5 -- "check_notes_tombstone" -> "check_redirects",
# `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md` Slice W37-4) when
# `check_notes_tombstone`'s job became watching REDIRECTS.csv instead, and its own test
# file (`tests/test_audit_docs_notes_tombstone.py`) was deleted per RFC-937 §5.7 and
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
    "docs/research/file-census-5ef559d.csv",
    "docs/research/RS-00953-file-taxonomy-draft-rfc-897-stage-1.md",
}

# The class: a document that *specifies or verifies RFC-937's own future migration* of
# this exact path, rather than a stale reference left over from the RFC-897 move this test
# otherwise polices. RFC-937 (`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`) is itself the
# reason this class exists at all: its own §4 step 4 will *delete* the stub files check 30
# watches, so both it and everything that verifies it against the tree necessarily name the
# path being deleted. `docs/plans/` already has a blanket carve-out above for the same
# reason (frozen, write-once); this set is for the same class of document living *outside*
# that directory, where no blanket rule exists and each one needs a reviewed, named entry.
#
# Two members so far, both audited directly rather than assumed current: RFC-937 names the
# old notes root under `.claude` twice (deliberately not written as one contiguous string
# in this comment, for the same self-referential reason the module docstring gives below)
# -- §4 step 4's migration instruction, and §7(d)'s acceptance grep, which must contain the
# literal pattern among the tokens a *later* migration tree is checked to no longer
# contain. `docs/research/RS-01002-rfc-937-verification-and-impact-sweep-audit-record.md` (PR #560, merged
# 2026-09-02, the day after RFC-937 itself) names it once, in its own §5.3/§5.4 scope note,
# listing the directories RFC-937's impact-map sweep covers. Confirmed by re-running this
# test against the merged tip that added it: exactly one new offender, that file alone --
# not RFC-937 itself, which the exemption below already covered; a claim from outside this
# session that a second, different file was *also* newly implicated did not hold up against
# a direct check of the actual failure at that tree and is not reflected here.
#
# Why an explicit set and not a structural rule (e.g. "exempt any file that also cites
# `RFC-937`"): a content-marker match would let the exemption widen itself the moment any
# document -- and WK-697, RFC-937's own migration workstream, is going to produce several --
# happens to mention `RFC-937` anywhere in a large file, without a reviewer ever choosing
# that specific file. That is exactly the failure mode `OLD_NOTES_STUB_NAMES` (in
# `audit-docs.py`) and `_PRE_MOVE_SNAPSHOTS` above were each already written to avoid, for
# the same stated reason: a derived or pattern-matched set lets one edit defeat both the
# content it changes and the check meant to catch it. Consistency with that established
# choice, not novelty, is why this set is named the same way.
#
# This is a deliberate, bounded stopgap, not a design meant to outlive its problem: RFC-937
# §5.7 lists this exact test file (with test_audit_docs_notes_tombstone.py) as **deleted**
# by its own migration, replaced by `test_audit_docs_redirects.py`. Building a sturdier
# mechanism for a check with a short, already-scheduled remaining lifespan would be solving
# a problem past the point it stops existing.
#
# What this stops catching, and what it does not: a *stray*, wrong citation of the old path
# added anywhere else inside either of these two named files -- by a future dated
# correction appended to RFC-937, say, or a later edit to the audit record -- would no
# longer fail this test, since the exemption is by filename, not by line or by the specific
# occurrences audited above. That risk is accepted narrowly for these two files; it is not
# extended to any other file. It does **not** stop catching a new, third document elsewhere
# in the tree that cites the old path for this same legitimate reason -- WK-697 will produce
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
    "docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md",
    "docs/research/RS-01002-rfc-937-verification-and-impact-sweep-audit-record.md",
    "docs/findings/FD-01009-python-yml-never-triggered-on-docs-so-a-docs-only-change-could-break-any-root-test-with-ci-green.md",
    "docs/findings/register.md",
    # Reviewed in 2026-09-03, and the first member of this set that is code rather than a
    # document. `scripts/_docverify.py` is RL-1043 §1's instrument, and its
    # `D_FULL_PATTERN` is RFC-937 §7(d)'s grep **verbatim** — a constant whose whole
    # purpose is that a reader can check the per-alternative decomposition against the
    # acceptance sentence it came from. One of those thirteen alternatives is the old
    # notes path, and the script's job is to *count occurrences of it* and fail while any
    # remain. Building that one alternative by concatenation, the way this test file
    # builds its own search term, would hide the literal and defeat the constant's reason
    # for existing; the reviewed exemption is the mechanism this comment block already
    # prescribes for exactly this case ("each needs its own reviewed line added here, not
    # a widened pattern"). It is a specification of the path, not a citation of it.
    #
    # Moved 2026-09-04 (task 17, RL-988 §2's "one shared constant"): the literal that
    # earned `scripts/_docverify.py` its entry here was `D_FULL_PATTERN`, §7(d)'s sentence
    # verbatim, one of whose thirteen alternatives is the old notes path. `D_FULL_PATTERN`
    # is now **deleted** -- `_docverify.py`'s `D_ALTERNATIVES` reads the same
    # `_docid.LEGACY_FORM_PATTERNS` tuple `audit-docs.py` check 36 already read, so the
    # literal (the "legacy claude-notes path" entry's own `re.escape(...)` argument, not
    # spelled out again here for the same self-referential reason this test builds its own
    # search term by concatenation) now lives in `scripts/_docid.py` alone. `_docverify.py`
    # was removed from this set and verified clean (a grep for the old path over that one
    # file, run outside this comment) before this edit landed, rather than left as a stale
    # permanent entry beside a new one --
    # the earlier "THIS EXEMPTION IS PERMANENT" note was about the file's *content* never
    # going away while the sentence it quoted stood, not about the *filename* being
    # immovable; the content moved, so the entry moves with it. The reasoning otherwise
    # carries over unchanged: this is the shared constant's whole purpose (a reader checks
    # the tuple against RFC-937 §7(d)'s own sentence rather than trusting it), building the
    # old-path alternative by concatenation would hide the literal and defeat that purpose,
    # and this is a specification of the path, not a citation of it.
    "scripts/_docid.py",
}

# The deputy's ruling (W37-6 channel, 2026-09-04): fixture *data*, not a document about the
# move -- the two files `_retire_claude_notes_stubs`'s own tests (`tests/test_doc_id_
# migrate.py`) read as the pre-migration tree, standing in for the real corpus's tombstone
# stubs and their directory README so that mechanism's tests do not have to run against
# this repository's own real `.claude` + `/notes` root. Naming the old path is the entire
# reason either file exists; a fixture built by concatenation to dodge *this* test would no
# longer be readable content for the migration engine under test to act on -- but the two
# path *entries* below are this test's own literal, and so built by concatenation for the
# same self-referential reason `old_path` above is: this file is itself part of the tracked
# corpus this test scans. The same distinction `_PRE_MOVE_SNAPSHOTS` above draws for a real
# pre-move artifact, not a stray leftover citation. Two members, reviewed individually per
# this file's own rule ("each needs its own reviewed line added here, not a widened
# pattern") rather than a `tests/fixtures/` prefix carve-out, which would silently exempt
# every future fixture regardless of whether it has a legitimate reason to name the path.
_D13_FIXTURE_DIR = "tests/fixtures/docs-migration/" + ".claude" + "/notes"
_D13_RETIREMENT_FIXTURE_DATA = {
    f"{_D13_FIXTURE_DIR}/README.md",
    f"{_D13_FIXTURE_DIR}/0001-example-fixture-note.md",
}


def test_no_living_file_cites_the_old_notes_path() -> None:
    """After the move, the old notes root under `.claude` may be named only by the
    tombstone README left there, by files frozen under `docs/plans/`, by check 30's own
    watching mechanism, by pre-move provenance-locked snapshots, and by a maintainer-accepted
    note that specifies the path's eventual deletion (`_SPECIFICATIONS_OF_THE_OLD_PATH`).

    A frozen plan is never edited to agree with a later move (`docs/plans/README.md`'s
    write-once rule, RFC-897 C4) -- the tombstone this slice creates at the vacated path
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
    exempt = (
        _CHECK_30_MECHANISM
        | _PRE_MOVE_SNAPSHOTS
        | _SPECIFICATIONS_OF_THE_OLD_PATH
        | _D13_RETIREMENT_FIXTURE_DATA
    )
    offenders = [
        f
        for f in tracked
        if old_path in (ROOT / f).read_text(encoding="utf-8", errors="replace")
        and not f.startswith("docs/plans/")
        and f != old_path + "/README.md"
        and f not in exempt
    ]
    assert offenders == [], offenders
