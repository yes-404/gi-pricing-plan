"""Shared header parser and id grammar for RFC-937's document-id standard.

`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` §1.1, §1.2, §1.5. Owned by W37-2
(`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`); `scripts/doc-id.py` and
`scripts/doc-index.py` (W37-3) import this module and do not redefine any of it — it is
the one place the id grammar and the header's closed field set are stated.

**Standard library only** (G4 / DP-5): `.github/workflows/docs.yml` runs
`scripts/audit-docs.py` with no dependency-install step, so nothing under `scripts/` that
feeds that workflow may import a third-party package. The header is YAML front matter in
*form* only — RFC-937 §1.5's field set is closed and flat (scalars, `[a, b]` lists, `~` for
null), so a hand-rolled parser over exactly that grammar is a feature, not a shortcut: it
rejects anything PyYAML would silently accept (a nested mapping, an anchor, a tag) that the
standard does not use.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Final

# RFC-937 §1.2a — five words, identical meaning in every family that uses a subset of them.
STATUS_WORDS: Final = ("draft", "active", "closed", "retired", "superseded")

# RFC-937 §1.2's family table, row families first then document families, left to right,
# top to bottom as the table itself lists them.
FAMILY_PREFIXES: Final = (
    "FR", "NFR", "DEP", "OQ", "WK", "SL", "WF",
    "ADR", "RFC", "PL", "LG", "RL", "RS", "CR", "FD",
)

# RFC-937 §1.7: "the resolver is `\b(FR|NFR|DEP|OQ|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0*(\d+)\b`
# with a check that the prefix matches the family the number belongs to." Quoted verbatim
# rather than built from FAMILY_PREFIXES: the note fixes this exact pattern as the citation
# resolver, and a generated version could silently reorder the alternation (regex
# alternation order can change which of two overlapping prefixes wins, though none overlap
# here) without anyone having decided that.
ID_RE: Final = re.compile(r"\b(FR|NFR|DEP|OQ|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0*(\d+)\b")

# RFC-937 §1.1 rule 3: "Filenames pad the integer to the standard's width, currently five."
PAD_WIDTH: Final = 5

# W37-6, 2026-09-04 (the deputy's ruling; narrowed the same day, after the row (d1)
# regression the first version of it caused). The left-hand boundary the FORWARD SWEEP's
# citation-token regexes need, in place of a bare `\b`. Two defects `\b` has here, which
# is why the fix is two lookbehinds and not one:
#
# * `\b` tests a \w/\W *transition*, and `-` is \W. A token whose family prefix is a
#   single word character preceded by `-` — a workstream/slice id inside a finding id that
#   cites it — is therefore matched *inside* the longer identifier: `\b` sees a transition
#   exactly where this grammar has none, because `-` separates the fields of one
#   identifier here, it does not end one.
# * The mirror case: a token that itself STARTS with a non-word character (a path rooted
#   under the old notes directory beneath `.claude`) is never found when the character
#   before it is also non-word — a backtick, which is what every real markdown citation of
#   a path writes.
#
# The guard is NOT "any preceding hyphen". That is what the first version said, and it is
# what made row (d1) regress: it stopped the sweep rewriting ordinary prose compounds and
# left two dangling citations in the migrated tree. What must block a match is a hyphen
# BELONGING TO AN IDENTIFIER — in the finding-id case the character before the hyphen is
# itself an id character. In an English prose compound (a lowercase prefix such as "anti-"
# or "non-" hyphenated onto a note id, which cites that note and must still be rewritten)
# the character before the hyphen is a lowercase letter. So the second lookbehind refuses
# `[A-Z0-9]-`, never a bare `-`.
#
# `(?<![A-Za-z0-9_])` is `\b`'s left half made explicit; `(?<![A-Z0-9]-)` is the
# compound-id guard. Four cases are the proof, and `tests/test_doc_id_migrate.py` holds
# them: a finding id leaves the slice id inside it unmatched; each of the two lowercase
# prose prefixes still matches the note id after it; and a parenthesised or sentence-final
# slice id still matches.
#
# Read by `doc-id.py` (the forward sweep and its own inverse helpers) and by
# `audit-docs.py` (DP-7's `_inverse_token_pattern`) — never retyped.
#
# `LEGACY_FORM_PATTERNS` below deliberately does NOT read it, and that is not an omission.
# The tuple reproduces RFC-937 §7(d)'s acceptance predicate, which the note states verbatim
# (at its own line 428) as a `git grep -E` with a plain `\b`, and `\b` matches between `-`
# and a following letter. Routing the tuple through this constant would make the shipped
# check blind to a form §7(d) says must be absent — a §7(d) amendment wearing a code
# change, which `CLAUDE.md` §0 forbids doing silently. The two must instead AGREE on every
# token the sweep can produce: whatever the sweep leaves behind, §7(d)'s predicate still
# finds. The four cases above are where that agreement is checked.
TOKEN_LEFT_BOUND: Final = r"(?<![A-Za-z0-9_])(?<![A-Z0-9]-)"

# RFC-937 §7 acceptance item (d)'s pattern, and `audit-docs.py` check 36's third clause —
# "one rule at two times" (RL-988 §2): both must read this **one** shared constant,
# never a private copy each script maintains independently. RL-988 §2 Part 1: every
# entry matches a COMPLETE legacy identifier or path, never a proper prefix of one — found
# against `NT-00` self-matching its own defining sentence inside RFC-937 §7 itself, and
# generalised to every alternative rather than fixed only there. Each entry is
# independently `\b`-bounded on both sides (or, for a path, matched as a literal substring
# with no anchor — a path is not a token with a "complete form" the way an id is); no entry
# shares an outer boundary with another, so a boundary bug in one can never mask or re-open
# the class in another. This tuple **is** the decomposition — one row (or one check-36
# hit) per entry, never re-derived from a combined pattern string.
#
# Broken-input proof (the consolidation's own, per RL-988 §2's own instruction): change
# one entry here and both `audit-docs.py` check 36 and `_docverify.py`'s (d) rows move
# together — `tests/test_doc_id_verify.py` proves both consumers hold this exact tuple.
LEGACY_FORM_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("note id", re.compile(r"\bNT-\d{4}\b")),
    ("finding id (workstream form)", re.compile(r"\bF-W\d+-\d+\b")),
    ("finding id (bare form)", re.compile(r"\bF\d{2}\b")),
    ("workflow id", re.compile(r"\bwf-0[0-9]\b")),
    ("ruling reference", re.compile(r"\bRuling \d+\b")),
    ("ADR id", re.compile(r"\bADR-0[0-9]{3}\b")),
    ("scoped requirement id", re.compile(r"\b(?:FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+\b")),
    ("workstream/slice id", re.compile(r"\bW[0-9]+[a-z]?-[0-9]+\b")),
    ("legacy dated-plan path", re.compile(re.escape("docs/plans/2026-"))),
    ("legacy audit path", re.compile(re.escape("docs/audit/"))),
    ("legacy notes path", re.compile(re.escape("docs/notes/"))),
    ("legacy adr path", re.compile(re.escape("docs/adr/"))),
    ("legacy claude-notes path", re.compile(re.escape(".claude/notes/"))),
)

# RL-988 Part 2's class: a lockfile carries dependency-resolution DATA a package
# manager generated, never a citation into this standard — a hash inside one can
# coincidentally contain a substring that reads like a corrupted legacy-id fragment (the
# `W5E...` hash in `frontend/pnpm-lock.yaml` is the case that surfaced this), and neither
# the migration sweep nor the (d)/(e)/(g) verification corpus has any business reading it
# as prose to rewrite or to count as residue. Declared, one entry per file with its own
# reason — the same treatment `_docverify.py`'s `_D_EXCLUDED_BASENAME` already gives
# `REDIRECTS.csv` — and placed here, beside `LEGACY_FORM_PATTERNS`, so `doc-id.py`'s sweep
# (`_iter_tree_files`) and `_docverify.py`'s corpus (`tracked_files`) read the identical
# tuple through `sweep_exclusion_reason` below rather than two independently maintained
# copies that can diverge (RL-988 §2 / `CLAUDE.md` §2: "a shape defined twice will
# diverge").
LOCKFILE_EXCLUSIONS: Final[tuple[tuple[str, str], ...]] = (
    ("uv.lock", "RL-988 Part 2 — generated dependency-resolution data, never a citation"),
    (
        "pnpm-lock.yaml",
        "RL-988 Part 2 — generated dependency-resolution data, never a citation",
    ),
    (
        "frontend/pnpm-lock.yaml",
        "RL-988 Part 2 — generated dependency-resolution data, never a citation",
    ),
)

# `docs/plans/PL-00967-rfc-the-readme-row-the-cell-extent-rule-and-4-step-5-s-stamp-set.md` §3 ruled `tests/fixtures/`
# exempt from the id-**stamp census** "by path, each file a declared exception" — a
# per-file list there because that census's own arithmetic (F83 condition 2) needs the
# exempt set enumerated one file at a time so a mismatch stays detectable, and a path
# prefix would silently swallow every future file beneath it.
#
# The migration sweep and the (d)/(e)/(g) verification corpus answer a different question
# — not "which files are exempt from a header stamp" but "which entire subtrees are
# fixture data that must never be read as a real document at all". Both roots below hold
# corpora **built** to carry legacy-form and deliberately malformed ids so `doc-id.py`'s
# own parsing, checks and `migrate()` have something to be tested against
# (`tests/fixtures/docs-ids/` — W37-3/W37-4; `tests/fixtures/docs-migration/` — W37-5).
# Counting their content as the real repository's residue, or rewriting it in place, would
# be the instrument grading its own fixtures. So the same DECLARED-not-implicit principle
# from the 2026-09-02 ruling is satisfied at root granularity here — two named roots, each
# with its own reason — rather than re-deriving a per-file enumeration that would grow
# every time a fixture file is added and buys nothing: unlike the stamp census, nothing
# here needs to prove its exempt set exactly equals some other measured set.
#
# `migrate(root)` still works when `root` **is** one of these directories (W37-5's own
# test harness calls it that way): the exclusion matches a path *relative to the tree
# being walked*, so a fixture root only ever excludes itself as a subtree of some larger
# walk (the real repository), never of itself.
FIXTURE_CORPUS_ROOTS: Final[tuple[tuple[str, str], ...]] = (
    (
        "tests/fixtures/docs-ids/",
        "W37-3/W37-4 id-grammar and check fixtures — deliberately carries legacy-form "
        "and malformed ids to exercise doc-id.py's own parsing and checks",
    ),
    (
        "tests/fixtures/docs-migration/",
        "W37-5's migrate() fixture corpus — the tree migrate() is tested AGAINST, not "
        "real repository content",
    ),
)

# W37-6 exec-ids (2026-09-04, per the deputy's ruling relayed via team-lead) and row
# (d8)/(g), task #30 (executor-30-2, same mechanism): the instrument's own test modules
# carry a legacy-form id as literal fixture data — proving a check catches (or correctly
# does not catch) a form needs the form written down somewhere, and these three modules are
# where RFC-937's own id grammar and its rewrite/verification mechanism are exercised
# against it. Counting that fixture data as the real repository's residue would be the
# instrument grading its own tests, the same reasoning `FIXTURE_CORPUS_ROOTS` above already
# gives the two on-disk fixture directories — this is the equivalent class for a literal
# Python string inside a test function rather than a checked-in fixture file. Declared
# per-file with its own reason (§7(d)'s own instruction against a structural rule that
# would silently widen, echoed at task 30's `register-owed.py` correction below):
# **`tests/test_register_owed.py` does NOT belong here.** Its subject, `register-owed.py`,
# is a file RFC-937 §4 itself migrates (`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md:381`), so
# its fixtures are stale test data that migrates WITH the script rather than exempted test
# infrastructure — fixed in the same commit as this exclusion (its scoped-requirement-id
# and workstream/slice-id placeholders respelled to their post-migration shapes), not
# deferred here as a citation this comment would then repeat, matching row (d)'s own
# corpus a second time from inside its own fix.
TEST_MODULE_EXCLUSIONS: Final[tuple[tuple[str, str], ...]] = (
    (
        "tests/test_doc_id_verify.py",
        "RFC-937 §7(d)'s own row (d)/(e)/(g) verification instrument's tests — exercises "
        "`_docid.LEGACY_FORM_PATTERNS` and the padded-id/fence conjuncts, and row (d8)'s "
        "task-key/slice-key/bare-key split, against literal legacy-form and "
        "deliberately-fake ids by construction",
    ),
    (
        "tests/test_audit_docs_ids.py",
        "audit-docs.py's own RFC-937 id-standard checks (30-39) tests — exercises the "
        "checks' parsing against literal legacy-form and deliberately-fake ids by "
        "construction, the same reasoning `LEGACY_FORM_EXCLUDED_PATHS` (audit-docs.py) "
        "gives its own on-disk fixture files",
    ),
    (
        "tests/test_doc_id_migrate.py",
        "doc-id.py's migrate()/_rewrite_citations() own tests — exercises token "
        "discovery, compound expansion and the citation sweep against literal legacy-form "
        "ids by construction; the deterministic/idempotent proofs both require pre- and "
        "post-migration forms to sit side by side in the same file",
    ),
)

#: The W37-11 residue ceiling record (`_docverify.py`'s `load_w37_11_record`) — a governed
#: table that, by construction, quotes legacy paths and tokens as *evidence of the residue
#: they name*, the same class `LOCKFILE_EXCLUSIONS`/`FIXTURE_CORPUS_ROOTS`/
#: `TEST_MODULE_EXCLUSIONS` above already carve out: data about legacy forms, never a
#: citation for the migration to rewrite or count as residue. Without this, populating the
#: record (which is the whole point of it) would itself move rows (d)/(g) it exists to
#: govern — the record of residue counted as residue. One entry, declared here rather than
#: guessed at from a basename, because the file's own path is the whole of what identifies
#: it (2026-09-05, W37-6, deputy's condition on PR #756).
W37_11_RECORD_PATH: Final = "docs/audit/w37-11-record.md"

GOVERNANCE_RECORD_EXCLUSIONS: Final[tuple[tuple[str, str], ...]] = (
    (
        W37_11_RECORD_PATH,
        "the W37-11 residue ceiling record — quotes legacy paths/tokens as evidence of "
        "the residue they name, never a citation for the migration to rewrite",
    ),
)


def sweep_exclusion_reason(rel_posix: str) -> str | None:
    """Why `rel_posix` (a tree-relative, forward-slash path) is excluded from the RFC-937
    migration sweep (`doc-id.py`'s `_iter_tree_files`) and from the (d)/(e)/(g)
    verification corpus (`_docverify.py`'s `tracked_files`) — or `None` when it is not
    excluded. One predicate, read by both consumers, so they can never disagree about what
    is excluded (RL-988 §2's "one shared constant").

    Five declared classes, checked in this order: a lockfile (`LOCKFILE_EXCLUSIONS`), a
    fixture-corpus root (`FIXTURE_CORPUS_ROOTS`), one of the instrument's own named test
    modules (`TEST_MODULE_EXCLUSIONS`), a governed record that quotes legacy forms as
    evidence rather than citing them (`GOVERNANCE_RECORD_EXCLUSIONS`), and a Python
    bytecode-cache artifact (`__pycache__/` or `*.pyc`) — the instrument's own exhaust from
    importing `scripts/` modules while it runs, never migration input and never real
    residue.
    """
    for name, reason in LOCKFILE_EXCLUSIONS:
        if rel_posix == name:
            return reason
    for root, reason in FIXTURE_CORPUS_ROOTS:
        if rel_posix == root.rstrip("/") or rel_posix.startswith(root):
            return reason
    for name, reason in TEST_MODULE_EXCLUSIONS:
        if rel_posix == name:
            return reason
    for name, reason in GOVERNANCE_RECORD_EXCLUSIONS:
        if rel_posix == name:
            return reason
    if "__pycache__" in rel_posix.split("/"):
        return (
            "a __pycache__ bytecode-cache directory created by importing this tooling's "
            "own modules — the instrument's own exhaust, never migration input or residue"
        )
    if rel_posix.endswith(".pyc"):
        return (
            "a compiled Python bytecode-cache file — the instrument's own exhaust, never "
            "migration input or residue"
        )
    return None


# =========================================================================================
# `docs/rulings/RL-01060-check-36-is-one-rule-at-two-times-with-d-and-must-carry-d-s-disclosed-classes-check-32-s-padding-resolution-clause-adopts-e-s-conjuncts-from-docid-not-a-private-re-typing.md` Entry 1 item 1:
# RFC-937 §7 acceptance item (d) (`_docverify.py`'s `rows_d`)
# and `audit-docs.py` check 36's third clause (`sweep_legacy_forms`) are "one rule at two
# times" (RL-988 §2). (d) already disclosed three classes on `LEGACY_FORM_PATTERNS`
# residue that a wrong rewrite or a closed historical population still legitimately
# carries; check 36 read no fence exclusion and no disclosed class at all, so the same
# text failed one check and passed the other. These four members — the fence exclusion,
# the alias/slice-key label set, the never-allocated predicate's sources and its function
# — are the shared constants both consumers now read; neither retypes them.
# =========================================================================================

#: RL-1044 §5.1's fence clause, extended to row (d)'s corpus (2026-09-04, W37-6
#: exec-ids): a legacy-form id kept byte-exact inside a fenced illustrative exhibit is not
#: a citation the migration is required to rewrite. Moved here from `_docverify.py` so
#: `audit-docs.py` check 36 can read the identical predicate rather than a private copy;
#: `_docverify.py` re-exports both names for its own existing callers and tests.
_FENCE_RE: Final = re.compile(r"^\s{0,3}(```|~~~)")


def fenced_line_numbers(text: str) -> frozenset[int]:
    """0-based line numbers inside a fenced code block, the fence-marker lines themselves
    included. A fence-marker line toggles `in_fence` and is itself excluded; every line
    the toggle leaves "inside" is excluded up to the matching close. An unclosed fence (a
    malformed document) leaves every remaining line excluded rather than raising.
    """
    out: set[int] = set()
    in_fence = False
    for i, line in enumerate(text.splitlines()):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            out.add(i)
            continue
        if in_fence:
            out.add(i)
    return frozenset(out)


#: `LEGACY_FORM_PATTERNS`' two finding-id alternatives, excluded from (d)'s zero
#: requirement **with their count disclosed**, never silently — RL-1043 §4 (`F<nn>`)
#: and RL-1046 §A (the `F-W<n>-<m>` workstream form, the same alias class with a work
#: prefix; its target is a register row, not a document with an id yet, resolved by
#: W37-11's alias resolver rather than this instrument). Keyed by `LEGACY_FORM_PATTERNS`'
#: own label, not by pattern text, so a future anchoring fix can never silently un-key a
#: disclosure. `_docverify.D_DISCLOSED` reads this exact set — row (d8)'s own dispatch
#: (`_docverify.rows_d`) checks `label == _D8_LABEL` before ever consulting it, so the
#: workstream/slice-id alternative below is never folded into this narrower set.
FINDING_ID_ALIAS_LABELS: Final[frozenset[str]] = frozenset({
    "finding id (bare form)",
    "finding id (workstream form)",
})

#: `audit-docs.py` check 36's own disclosed-label set — `FINDING_ID_ALIAS_LABELS` plus the
#: `W<n>[a-z]?-<m>` workstream/slice form (RL-1046 §A's third alias class; row (d8)),
#: whose target is a register row or a slice with no `SL-`/task id ever minted for it,
#: resolved by W37-11's alias resolver rather than this instrument.
#:
#: The workstream/slice-id alternative's own pattern (`\bW[0-9]+[a-z]?-[0-9]+\b`) cannot
#: match a bare, suffix-less work key at all — it requires a trailing `-[0-9]+` to match
#: anything — so every hit this label produces is already a two-segment slice key or the
#: first two segments of a three-segment task key, and RL-1046 §A discloses both. The
#: mig-vs-ctl "did the migration create a new slice-key value" and "bare work-key
#: remainder" checks `_docverify._d8_verdict` also runs are a *different* question (row
#: (d8)'s own regression gate over a migration diff) that a single-snapshot sweep has no
#: control tree to ask; they do not apply here and are not ported. Check 36 alone reads
#: this wider set — `_docverify.D_DISCLOSED` deliberately stays the narrower
#: `FINDING_ID_ALIAS_LABELS`, per the note above.
DISCLOSED_ALIAS_LABELS: Final[frozenset[str]] = FINDING_ID_ALIAS_LABELS | frozenset({
    "workstream/slice id",
})

#: `LEGACY_FORM_PATTERNS`' "scoped requirement id" label — (d7)'s closed never-allocated
#: class, checked per matched token by `is_scoped_id_never_allocated` below rather than
#: disclosed by label alone (unlike `DISCLOSED_ALIAS_LABELS`, a real `token_map` miss on
#: this alternative must still fail).
SCOPED_REQUIREMENT_ID_LABEL: Final = "scoped requirement id"

#: `next free\s*:` — the identical device `audit-docs.py`'s own `UNALLOCATED` marker check
#: uses to tell an allocation note from a citation. A token on the marker's own line,
#: after the marker, is not "defined" by that line; every other line naming the token is.
_NEXT_FREE_MARKER_RE: Final = re.compile(r"next free\s*:", re.IGNORECASE)

#: The three sources (d7)'s deputy-ruled predicate reads beyond `docs/specs/*.md`'s own
#: bold form, relative to a repo root.
_SCOPED_ID_OTHER_DEFINITION_SOURCES: Final = (
    "docs/open-questions.md", "docs/roadmap.md", "docs/findings/register.md",
)


def _read_text_or_none(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def scoped_id_bold_defined(token: str, definition_root: Path) -> bool:
    """True if `token` is bold-defined (`**token**`) anywhere in `definition_root`'s
    `docs/specs/*.md` — `_discover_requirements`'s own source, read the identical way (a
    plain substring test)."""
    needle = f"**{token}**"
    specs_dir = definition_root / "docs" / "specs"
    if not specs_dir.is_dir():
        return False
    for path in sorted(specs_dir.glob("*.md")):
        text = _read_text_or_none(path)
        if text is not None and needle in text:
            return True
    return False


def scoped_id_defined_elsewhere(token: str, definition_root: Path) -> bool:
    """True if `token` has a genuine definition row in `open-questions.md`, `roadmap.md`
    or `docs/findings/register.md` under `definition_root` — a `next free:`-marker MENTION on
    the same line, before the token, is not a definition; everything else that names the
    token counts."""
    for rel in _SCOPED_ID_OTHER_DEFINITION_SOURCES:
        text = _read_text_or_none(definition_root / rel)
        if text is None:
            continue
        for line in text.splitlines():
            at = line.find(token)
            if at == -1:
                continue
            if not _NEXT_FREE_MARKER_RE.search(line[:at]):
                return True
    return False


def scoped_id_has_redirect(token: str, redirect_root: Path) -> bool:
    """True if `token` has an `old_id` row in `redirect_root`'s `docs/REDIRECTS.csv`."""
    text = _read_text_or_none(redirect_root / "docs" / "REDIRECTS.csv")
    if text is None:
        return False
    prefix = f"{token},"
    return any(line.startswith(prefix) for line in text.splitlines())


def is_scoped_id_never_allocated(
    token: str, *, definition_root: Path, redirect_root: Path
) -> bool:
    """The deputy's mechanical predicate (2026-09-04, W37-6 exec-ids), applied to one
    token: never-allocated only when ALL of zero bold definitions in
    `definition_root`'s `docs/specs/*.md`, zero definition row in its
    `open-questions.md`/`roadmap.md`/`docs/findings/register.md`, and no `old_id` row for it
    in `redirect_root`'s `docs/REDIRECTS.csv`. `definition_root` and `redirect_root` are
    separate parameters because `_docverify.py`'s (d7) checks definitions against the
    *control* (un-migrated) tree and the redirect against the *migrated* tree; a
    single-snapshot sweep (check 36) passes the same root for both. `not any(...)` rather
    than three early-returns, so every check always runs.
    """
    return not (
        scoped_id_bold_defined(token, definition_root)
        or scoped_id_defined_elsewhere(token, definition_root)
        or scoped_id_has_redirect(token, redirect_root)
    )


# =========================================================================================
# docs/rulings/RL-01060-check-36-is-one-rule-at-two-times-with-d-and-must-carry-d-s-disclosed-classes-check-32-s-padding-resolution-clause-adopts-e-s-conjuncts-from-docid-not-a-private-re-typing.md Entry 2 item 1:
# `_docverify.py`'s row (e) (`padded_hits`) and `audit-docs.py` check 32's padding clause
# are "one rule at two times" over the same corpus. Conjunct 1's exact-width regex,
# conjunct 2 (a padded id inside a filesystem path is not a citation) and its
# stripping/boundary machinery move here so neither consumer re-types — or reassembles —
# them; `_docverify.py` re-exports every name under its existing name for its own callers
# and tests.
# =========================================================================================

#: **Conjunct 1**, and `PAD_WIDTH` is read from the symbol, never written as a literal.
#: RL-1044 defect 1: the same corpus gave 2032 under `-0\d{4}` and 2387 under
#: `-0[0-9]{3,4}` — **355 occurrences from the digit count alone**, F85's exact shape
#: inside an acceptance predicate. Reading `FAMILY_PREFIXES`/`PAD_WIDTH` by symbol in two
#: places and reassembling the same regex expression twice is still two rules kept equal
#: by discipline alone, not one rule — the assembled `re.Pattern` is the shared thing, and
#: it lives here, once, for exactly that reason.
_PADDED_ID_RE: Final = re.compile(
    r"\b(" + "|".join(FAMILY_PREFIXES) + r")-0\d{" + str(PAD_WIDTH - 1) + r"}\b"
)

#: **Conjunct 2's** stripping step. RL-1044 defect 3: two of the three survivors were
#: paths — `docs/rulings/**RL-00993**-q5-….md` — whose **bold markers split the token**, so
#: the path test never saw a path. A predicate bug, not a ruling question.
_MD_EMPHASIS_RE: Final = re.compile(r"\*{1,3}")

#: `<` and `>` are excluded from this boundary set — this doc suite's own placeholder
#: convention writes a filename's variable segment in angle brackets (a padded id, a
#: hyphen, an angle-bracketed slug placeholder, then `.md`; `docs/_templates/*.md`'s own
#: copy-target lines and RFC-937 §1.1 rule 3's illustration both use it), and treating
#: `<`/`>` as hard boundaries truncated the right-side walk before it ever reached the
#: extension — the token stopped one character short of the placeholder's opening `<`, so
#: a real filename citation (`PL-01240-<slug>.md`) read as prose (`PL-01240-`, no `/`, no
#: extension). Widening the walk past them can also swallow a literal `<...>` wrapper
#: around a *bare* id, but that token still has no `/` and does not end in an extension,
#: so it is classified unchanged.
_TOKEN_BOUNDARY_RE: Final = re.compile(r"[\s`()\[\]{}\"',;]")

#: **Conjunct 2's** line-locator strip. Row (e)'s own measurement found a fourth defect
#: alongside RL-1044's three: a same-directory `filename.md:123` or `filename.md:401-404`
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


# RFC-937 §1.2's "Kind" column, lowercased, keyed by prefix. What never changes on
# extension (§1.12): a new family adds a row here via an RFC-/RL-, this table is not
# reopened for any other reason.
_FAMILY_OF: Final[Mapping[str, str]] = {
    "FR": "requirement",
    "NFR": "requirement",
    "DEP": "requirement",
    "OQ": "open question",
    "WK": "work",
    "SL": "slice",
    "WF": "workflow",
    "ADR": "decision",
    "RFC": "proposal",
    "PL": "plan",
    "LG": "ledger",
    "RL": "ruling",
    "RS": "research",
    "CR": "closure",
    "FD": "finding",
}


class HeaderError(Exception):
    """Malformed front matter, an unknown field, or a field of the wrong shape.

    Carries the path and the 1-based line number in its message.
    """


@dataclass(frozen=True)
class Header:
    """One document's (or row's) parsed front matter — RFC-937 §1.5's closed field set."""

    id: str | None
    family: str
    kind: str | None
    title: str
    status: str
    created: date | None
    owner: str
    phase: str | None
    work: str | None
    slice_: str | None
    tree: str | None
    plans: tuple[str, ...]
    supersedes: tuple[str, ...]
    superseded_by: str | None
    corrected_by: tuple[str, ...]
    corrects: str | None
    relates: tuple[str, ...]
    was: str | None
    vendored: bool
    origin: str | None
    extra: Mapping[str, str]


def canonical(prefix: str, n: int) -> str:
    """The citation form — RFC-937 §1.1 rule 2: unpadded, always. `canonical("PL", 1240)`
    -> `"PL-1240"`.
    """
    return f"{prefix}-{n}"


def padded(prefix: str, n: int, width: int = PAD_WIDTH) -> str:
    """The filename form — RFC-937 §1.1 rule 3: padded to `width` (never truncated below
    the number's own length). `padded("PL", 1240)` -> `"PL-01240"`.
    """
    return f"{prefix}-{n:0{width}d}"


def family_of(prefix: str) -> str:
    """The family word RFC-937 §1.2's "Kind" column gives `prefix`, lowercased.

    Raises `ValueError` naming the prefix for anything not in `FAMILY_PREFIXES` — a
    product identifier (`VR-...`) or a typo, never a silent guess (D5, G5).
    """
    try:
        return _FAMILY_OF[prefix]
    except KeyError:
        raise ValueError(f"{prefix!r} is not a governed-thing family prefix") from None


# Scalar fields that stay strings (default "" when absent — required-ness is a per-family
# policy a caller checks, e.g. audit-docs check 30; this parser only reports what it found).
_STR_FIELDS: Final = ("family", "title", "status", "owner")
# Scalar fields that are `str | None` (default None when absent or `~`).
_OPTIONAL_STR_FIELDS: Final = (
    "id", "kind", "phase", "work", "tree", "superseded_by", "corrects", "was", "origin",
)
# List fields — `[a, b]` or `[]`; default `()` when absent.
_LIST_FIELDS: Final = ("plans", "supersedes", "corrected_by", "relates")
_KNOWN_KEYS: Final = frozenset(
    (*_STR_FIELDS, *_OPTIONAL_STR_FIELDS, *_LIST_FIELDS, "slice", "created", "vendored")
)

_KEY_VALUE_RE: Final = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]?(.*)$")
_LIST_ITEM_RE: Final = re.compile(r"^\[(.*)\]$")


def _strip_inline_comment(value: str) -> str:
    """Drop a trailing `  # comment` — the header examples in RFC-937 §1.5 carry one on
    almost every line. A `#` is only ever a comment marker here because the closed grammar
    has no quoted-string field whose value legitimately contains one; a bare split on the
    first ` #` is exact for that grammar, not an approximation of full YAML.
    """
    idx = value.find(" #")
    return value if idx == -1 else value[:idx]


def _parse_scalar(raw: str) -> str | None:
    value = _strip_inline_comment(raw).strip()
    if value == "~" or value == "":
        return None
    return value


def _parse_list(raw: str, *, path: Path, line_no: int) -> tuple[str, ...]:
    value = _strip_inline_comment(raw).strip()
    match = _LIST_ITEM_RE.match(value)
    if match is None:
        raise HeaderError(f"{path}:{line_no}: not a well-formed `[a, b]` list: {raw!r}")
    inner = match.group(1).strip()
    if not inner:
        return ()
    return tuple(item.strip() for item in inner.split(","))


def _parse_front_matter_body(
    lines: list[str], *, path: Path, first_line_no: int
) -> dict[str, object]:
    """Parse the flat `key: value` lines of one front-matter block into a plain dict,
    keyed by the YAML key exactly as written (`slice`, not `slice_`) — RFC-937 §1.5's
    closed grammar: scalars, `[a, b]` lists, `~` for null, nothing nested.

    Raises `HeaderError` naming `path` and the 1-based line number for a duplicate key, a
    line with no `key: value` shape, an unterminated list, or (via `_parse_created`) a
    malformed date.
    """
    result: dict[str, object] = {}
    for offset, raw_line in enumerate(lines):
        line_no = first_line_no + offset
        if not raw_line.strip():
            continue
        if raw_line[:1] in (" ", "\t"):
            raise HeaderError(
                f"{path}:{line_no}: indented line — nested mappings are not in the "
                f"closed field set (RFC-937 §1.5): {raw_line!r}"
            )
        match = _KEY_VALUE_RE.match(raw_line)
        if match is None:
            raise HeaderError(f"{path}:{line_no}: not a `key: value` line: {raw_line!r}")
        key, raw_value = match.group(1), match.group(2)
        if key in result:
            raise HeaderError(f"{path}:{line_no}: duplicate key {key!r}")
        if key == "created":
            scalar = _parse_scalar(raw_value)
            if scalar is None:
                result[key] = None
                continue
            try:
                year, month, day = (int(part) for part in scalar.split("-"))
                result[key] = date(year, month, day)
            except (ValueError, TypeError) as exc:
                raise HeaderError(
                    f"{path}:{line_no}: `created` is not an ISO date (YYYY-MM-DD): "
                    f"{scalar!r}"
                ) from exc
        elif key == "vendored":
            scalar = _parse_scalar(raw_value)
            result[key] = scalar == "true"
        elif key in _LIST_FIELDS:
            result[key] = _parse_list(raw_value, path=path, line_no=line_no)
        else:
            result[key] = _parse_scalar(raw_value)
    return result


def _str_field(body: Mapping[str, object], key: str) -> str:
    value = body.get(key)
    return value if isinstance(value, str) else ""


def _opt_str_field(body: Mapping[str, object], key: str) -> str | None:
    value = body.get(key)
    return value if isinstance(value, str) else None


def _tuple_field(body: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = body.get(key)
    return value if isinstance(value, tuple) else ()


def _date_field(body: Mapping[str, object], key: str) -> date | None:
    value = body.get(key)
    return value if isinstance(value, date) else None


def _bool_field(body: Mapping[str, object], key: str) -> bool:
    return body.get(key) is True


def parse_header(path: Path) -> Header | None:
    """Parse the YAML-front-matter-shaped header at the top of `path`.

    Returns `None` when the file has no front-matter block at all (its first line is not
    exactly `---`) — most files in this repository today, pre-migration (W37-6), and that
    is a legitimate, common state rather than an error.

    Raises `HeaderError`, naming `path` and a 1-based line number, when a front-matter
    block is present but does not fit RFC-937 §1.5's closed grammar: an unterminated
    block, a duplicate key, an indented (nested) line, a malformed list, or a malformed
    `created` date.

    A key outside the closed field set is not an error here — it lands in `.extra`
    verbatim. Whether a given extra is *permitted* for this file's family (§1.5: "declared
    in that family's template and permitted only there") is a family-aware policy check
    (`audit-docs.py` check 30), not this generic parser's to enforce.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    return parse_header_text(text, path=path)


def parse_header_text(text: str, *, path: Path | None = None) -> Header | None:
    """`parse_header` for a string already in memory, rather than a file on disk —
    factored out of `parse_header` so a caller comparing two in-memory texts (Ruling
    105's DP-7 fix, `audit-docs.py`'s `frozen_file_matches_after_migration_stamp`) can
    reuse the identical parsing and error rules without writing either string to a
    temporary file first. `path` is used only to name the source in a raised
    `HeaderError`'s message; omit it when there is no file behind `text` — the message
    then names a placeholder rather than a real path.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None
    error_path = path if path is not None else Path("<in-memory text>")
    try:
        closing = lines.index("---", 1)
    except ValueError:
        raise HeaderError(
            f"{error_path}:1: front-matter block has no closing `---`"
        ) from None

    body = _parse_front_matter_body(lines[1:closing], path=error_path, first_line_no=2)

    extra: dict[str, str] = {
        key: "" if value is None else str(value)
        for key, value in body.items()
        if key not in _KNOWN_KEYS
    }

    return Header(
        id=_opt_str_field(body, "id"),
        family=_str_field(body, "family"),
        kind=_opt_str_field(body, "kind"),
        title=_str_field(body, "title"),
        status=_str_field(body, "status"),
        created=_date_field(body, "created"),
        owner=_str_field(body, "owner"),
        phase=_opt_str_field(body, "phase"),
        work=_opt_str_field(body, "work"),
        slice_=_opt_str_field(body, "slice"),
        tree=_opt_str_field(body, "tree"),
        plans=_tuple_field(body, "plans"),
        supersedes=_tuple_field(body, "supersedes"),
        superseded_by=_opt_str_field(body, "superseded_by"),
        corrected_by=_tuple_field(body, "corrected_by"),
        corrects=_opt_str_field(body, "corrects"),
        relates=_tuple_field(body, "relates"),
        was=_opt_str_field(body, "was"),
        vendored=_bool_field(body, "vendored"),
        origin=_opt_str_field(body, "origin"),
        extra=extra,
    )


# RL-990 (`docs/rulings/RL-00990-rfc-937-1-5-s-vendored-parenthesis-is-a-gloss-not-a-detector-the-set-is-declared-and-reconciled-and-the-exemption-reaches-only-the-blanket-passes.md`, PR #563,
# merged): RFC-937 §1.5's parenthetical, naming `planning-with-files`, `ui-ux-pro-max`,
# `graphify`, `systematic-debugging` and the `vue-*` skills as vendored while giving "a
# directory that provides a `LICENSE` of its own" as the reason, is a gloss identifying
# which skills the note's author had in mind, not a specification of a detector: it is
# wrong about three of its own five named examples (`graphify`, `systematic-debugging`,
# every `vue-*` skill provides no such file) and about 26 of the repository's 28.
# `vendored` is declared and reconciled, never detected. This is the hand-kept enumeration,
# seeded from
# `.claude/skills/README.md`'s provenance sections — the record `CLAUDE.md` §12 makes
# authoritative for what is vendored — and reconciled against `pyproject.toml`'s
# `[tool.ruff] exclude` list by `vendored_skills_ruff_exclude_mismatch` below, which is
# the independent second witness, never the criterion itself: adopting the ruff list
# outright is RL-990's other rejected option, because nine of its 28 entries carry a
# deliberate RFC-937 §5.4 edit and two of those (`writing-plans`,
# `subagent-driven-development`) are creating instruments RL-987 requires inside the
# migration commit — treating ruff-exclusion itself as "vendored" would exempt them from
# the very migration that must carry them. Extending this set is a deliberate edit,
# recorded in `.claude/skills/README.md` in the same commit (RL-990 §2 part 3), never a
# rename this constant discovers on its own.
_VENDORED_SKILLS: Final[frozenset[str]] = frozenset({
    "brainstorming",
    "code-quality",
    "create-adaptable-composable",
    "dispatching-parallel-agents",
    "executing-plans",
    "finishing-a-development-branch",
    "graphify",
    "planning-with-files",
    "receiving-code-review",
    "reproducing-ci-locally",
    "requesting-code-review",
    "secret-hygiene",
    "security-audit",
    "subagent-driven-development",
    "systematic-debugging",
    "test-driven-development",
    "testing-strategy",
    "ui-ux-pro-max",
    "using-git-worktrees",
    "using-superpowers",
    "verification-before-completion",
    "vue-best-practices",
    "vue-debug-guides",
    "vue-pinia-best-practices",
    "vue-router-best-practices",
    "vue-testing-best-practices",
    "writing-plans",
    "writing-skills",
})


def is_vendored(path: Path, repo_root: Path) -> bool:
    """True when `path` sits beneath a directory named in `_VENDORED_SKILLS` directly
    under `.claude/skills/` — RFC-937 §1.5's vendored-skill exemption, as RL-990
    resolved it (see the comment above `_VENDORED_SKILLS`): a membership test against a
    declared constant, never a filesystem probe.

    This function's signature is unchanged from the published contract W37-3 and W37-4
    import (RL-990 §2 part 4) — only the body changed, from walking the filesystem
    for a `LICENSE` file to testing set membership.

    `path` may be a file or a directory, absolute or relative to `repo_root`; both are
    resolved before comparison, so the two forms behave identically and a symlink is
    followed rather than compared literally. Returns `False` for anything not under
    `repo_root/.claude/skills/<name>` — including `repo_root` itself, a file elsewhere in
    the repository (there is no more special case for the repository's own root
    `LICENSE`: nothing here inspects any `LICENSE` file, so there is nothing for it to be
    mistaken for), and a path outside `repo_root` entirely.
    """
    try:
        rel_parts = path.resolve().relative_to(repo_root.resolve()).parts
    except ValueError:
        return False  # not under repo_root at all
    if len(rel_parts) < 3 or rel_parts[0] != ".claude" or rel_parts[1] != "skills":
        return False
    return rel_parts[2] in _VENDORED_SKILLS


#: The basename `doc-id.py migrate`'s `_write_split_source_indexes` gives each family's
#: split-source index (`docs/<family>/INDEX.md`) — never the top-level `docs/INDEX.md`,
#: a different file with a different meaning `is_split_source_index` below excludes by
#: requiring exactly one directory segment between `docs/` and the basename.
SPLIT_INDEX_BASENAME: Final = "INDEX.md"


def is_split_source_index(rel: str) -> bool:
    """True for `rel` (a repo-relative, `/`-separated path) naming a family's
    split-source index — `docs/<family>/INDEX.md`, generated whole by
    `doc-id.py migrate`'s `_write_split_source_indexes` and never hand-edited.

    Row (d9)-(d12)'s own defect (2026-09-05): every such file's body is RL-287/RL-255's
    ruled provenance record — a `` `was:` `` table column and a "`<old_rel>` became N
    documents." heading line that must keep naming the pre-migration path forever (a
    split source has no single successor to repoint to; RL-287 §3.3 forbids choosing
    one, RL-255 forbids the path-only rewrite that choosing one would be). §7(d)'s path
    alternatives could not tell this ruled citation apart from a stale one the
    citation-inverse mechanism had simply failed to repoint, and counted every row of it
    fatal. This predicate lets a caller exclude the file's content from that count
    entirely — the same treatment `docs/REDIRECTS.csv` itself already gets, since the
    docstring `_write_split_source_indexes` carries calls this file exactly that: "the
    `../REDIRECTS.csv` row made navigable."

    Never the top-level `docs/INDEX.md` (two segments, not three) or a file two or more
    directories deep — only a bare `docs/<family>/INDEX.md`.
    """
    parts = rel.split("/")
    return len(parts) == 3 and parts[0] == "docs" and parts[2] == SPLIT_INDEX_BASENAME


def vendored_skills_ruff_exclude_mismatch(
    repo_root: Path,
) -> tuple[frozenset[str], frozenset[str]]:
    """RL-990 §2 part 2's reconciliation: `_VENDORED_SKILLS` against `repo_root`'s
    `pyproject.toml`'s `[tool.ruff] exclude` list, restricted to the `.claude/skills/<name>`
    entries — the independent second witness the ruling requires, never the criterion
    itself (`is_vendored`'s docstring, and the comment above `_VENDORED_SKILLS`, both say
    why the ruff list is not adopted outright: it over-exempts two of RL-987's creating
    instruments).

    Returns `(only_in_constant, only_in_ruff)`. Both empty means the two agree — this is
    the passing case, and it is what the real repository must show today. Either side
    non-empty is drift, and the caller must fail loudly naming which side moved (RL-990
    acceptance item 1) rather than silently trusting one source over the other.

    Reads `repo_root/pyproject.toml` fresh on every call, with `tomllib` (standard
    library — this module's own docstring, G4/DP-5, is why nothing here may import a
    third-party TOML parser) rather than caching the ruff list at import time, so a test
    can point this at a synthetic `pyproject.toml` under `tmp_path` without needing to
    reload this module. Indexes `config["tool"]["ruff"]["exclude"]` directly rather than
    `.get`-chaining to a default: a moved or renamed key must raise, the same "fail loud"
    the reconciliation itself exists to provide — a silent empty list here would read as
    "ruff excludes nothing", which is drift in exactly the direction this function must
    never hide.
    """
    config = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    exclude = config["tool"]["ruff"]["exclude"]
    prefix = ".claude/skills/"
    ruff_skills = frozenset(
        entry[len(prefix) :] for entry in exclude
        if isinstance(entry, str) and entry.startswith(prefix)
    )
    return _VENDORED_SKILLS - ruff_skills, ruff_skills - _VENDORED_SKILLS


# ---------------------------------------------------------------------------------------
# RFC-937 §4 step 5's stamp set — the one definition, two consumers.
#
# `scripts/audit-docs.py` needs it twice over (`nt0019_stamp_set`, the corpus the F83
# exemption register is reconciled against; and `_id_scope_documents`, the population
# checks 30-39 enforce over) and `scripts/doc-id.py` needs it to know what `migrate`
# stamps. Before this block each stated the rule for itself, and the two disagreed in a
# way no instrument compared: `_id_scope_documents` expanded a directory root with
# `rglob("*.md")`, so it reached **no** non-markdown file however the roots were widened,
# while `nt0019_stamp_set` reached all 62 of them (`F87`).
#
# **The membership predicate is the definition; the filesystem walk is derived from it.**
# `stamp_set_files` filters a walk through `in_stamp_set` rather than carrying a second,
# glob-shaped statement of the same rule — two spellings of one rule is how the two
# consumers came to disagree in the first place (`RFC-756`).
#
# The rule itself is `docs/plans/PL-00967-rfc-the-readme-row-the-cell-extent-rule-and-4-step-5-s-stamp-set.md` §4's
# ruling, quoting RFC-937 §4 step 5: every file under `docs/`, `.claude/roles/` and
# `.claude/agents/`, every `.claude/skills/*/SKILL.md`, plus every `README.md` anywhere in
# the tree. That last clause is §1.2's Reference row, not step 5's own words, and it is
# kept because `scripts/doc-id.py`'s README scope reaches those files whatever step 5's
# roots say.
# ---------------------------------------------------------------------------------------

#: The directory prefixes RFC-937 §4 step 5 names, repo-relative and without a trailing
#: slash. `.claude/skills` is here for `stamp_set_files`' benefit — a root a caller may
#: legitimately name — even though only its `*/SKILL.md` members are in the set;
#: `in_stamp_set` is what decides membership, never this tuple on its own.
STAMP_SET_ROOTS: Final[tuple[str, ...]] = (
    "docs",
    ".claude/roles",
    ".claude/agents",
    ".claude/skills",
)

#: The one filename that is in the stamp set wherever it appears (RFC-937 §1.2's
#: Reference row, "every `README.md` anywhere in the tree").
STAMP_SET_ANYWHERE: Final = "README.md"


def in_stamp_set(rel: str) -> bool:
    """Is the repo-relative posix path `rel` in RFC-937 §4 step 5's stamp set?

    A **path** predicate, not a filesystem probe: it never touches the disk, so the same
    definition answers for a `git ls-files` listing and for a tree walk, and a test can
    put an arbitrary corpus in front of it.

    Membership is by path only. Whether a file that *is* in the set can actually carry a
    header is a separate question with a separate answer — `audit-docs.py`'s
    `unstampable_reason` and its `UNSTAMPABLE_EXEMPTIONS` register — and the two are kept
    apart deliberately: 62 of the register's entries are in this set and cannot be
    stamped, which is only expressible because membership does not already exclude them.
    """
    if rel.rsplit("/", 1)[-1] == STAMP_SET_ANYWHERE:
        return True
    if rel.startswith(("docs/", ".claude/roles/", ".claude/agents/")):
        return True
    parts = rel.split("/")
    return (
        len(parts) == 4
        and parts[0] == ".claude"
        and parts[1] == "skills"
        and parts[3] == "SKILL.md"
    )


def nt0019_stamp_set(tracked: Iterable[str]) -> list[str]:
    """Every path in `tracked` that RFC-937 §4 step 5 stamps, sorted and de-duplicated.

    `tracked` is the caller's corpus — `git ls-files` in production, for the reason
    `scripts/doc-id.py` records: a working-tree walk picks up `.venv/`, `graphify-out/`
    and anything else untracked, which differs between two checkouts of the same commit.
    Taking it as an argument rather than shelling out here is what lets a test hold a
    corpus fixed while the predicate changes.
    """
    return sorted({rel for rel in tracked if in_stamp_set(rel)})


def stamp_set_files(directory: Path, repo_root: Path) -> list[Path]:
    """Every file under `directory` that `in_stamp_set` admits, sorted.

    The filesystem face of the same rule, for a caller that has a directory rather than a
    listing. `.git/` and `__pycache__/` are skipped; nothing else is filtered here — the
    predicate decides.

    **A directory outside every `STAMP_SET_ROOTS` prefix contributes every file it
    holds.** Naming a directory as a scope root is itself the statement that its contents
    are governed documents; there is no second rule for the caller to consult and no
    silent narrowing. This is the case a test fixture root takes, and it is why pointing
    `audit-docs.py`'s `_ID_SCOPE_ROOTS` at a fixture tree still collects that tree.
    """
    try:
        rel_dir = directory.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        rel_dir = None  # outside the repository entirely
    governed = rel_dir is not None and any(
        rel_dir == root or rel_dir.startswith(root + "/") for root in STAMP_SET_ROOTS
    )
    out: list[Path] = []
    for path in sorted(directory.rglob("*")):
        parts = path.relative_to(directory).parts
        if ".git" in parts or "__pycache__" in parts:
            continue
        if not path.is_file():
            continue
        if governed and not in_stamp_set(f"{rel_dir}/{'/'.join(parts)}"):
            continue
        out.append(path)
    return out


# ---------------------------------------------------------------------------------------
# Template readers — Rulings 79 and 80
# (`docs/rulings/INDEX.md#2026-09-02-w37-template-parser-conflicts-rulingsmd`). Both rulings settle
# the same way: a family's own template under `docs/_templates/` is the licensing
# instrument (RL-981 §2 item 1), never a hand-written constant in a reader. Kept here,
# not in `scripts/doc-index.py`, so `scripts/doc-id.py` (the row/phase *writer*,
# `migrate`) and `scripts/doc-index.py` (the *reader*) derive from one definition apiece
# and cannot silently disagree — both already import this module and neither imports the
# other (RL-998 §3 item 2: "the reader must not become a third transcription").
# ---------------------------------------------------------------------------------------

#: The two row families (RFC-937 §1.5): a `WK-`/`SL-` row's header is a fenced ```yaml
#: block under the row's own heading, never the file's own front matter. Keyed by family
#: word, the convention `scripts/audit-docs.py`'s `_TEMPLATE_FAMILY` already uses for a
#: template's filename.
ROW_TEMPLATE_FILES: Final[Mapping[str, str]] = {"work": "WK.md", "slice": "SL.md"}

_TEMPLATE_LEADING_COMMENT_RE: Final = re.compile(r"\A<!--.*?-->\n?\n?", re.DOTALL)
_TEMPLATE_FENCED_YAML_RE: Final = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
_TEMPLATE_KEY_RE: Final = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")


def row_template_fields(templates_dir: Path, family: str) -> frozenset[str]:
    """The permitted field set for a `WK-`/`SL-` row, derived from that family's own
    template's fenced ```yaml block (RL-998 §3 item 1) — RL-981 §2 item 1's "the
    permitted set for a family is the set of keys in that family's template front matter",
    applied to a row's fenced block, which is what a `WK-`/`SL-` row carries in place of a
    document's own top-level front matter (RFC-937 §1.5).

    Raises `ValueError` naming `family` for anything not a row family — a document
    family's field policy is `scripts/audit-docs.py`'s `derive_field_policies` to compute,
    never this function's; and for `templates_dir` when the named template is missing or
    carries no fenced block at all, rather than deriving a silently smaller policy from
    whatever happened to be found (the same "silent empty coverage must be impossible"
    property `derive_field_policies` already enforces for the other twelve templates,
    RL-981 §4 item 3).
    """
    try:
        filename = ROW_TEMPLATE_FILES[family]
    except KeyError:
        raise ValueError(
            f"{family!r} is not a row family ({sorted(ROW_TEMPLATE_FILES)})"
        ) from None
    path = templates_dir / filename
    text = path.read_text(encoding="utf-8")
    stripped = _TEMPLATE_LEADING_COMMENT_RE.sub("", text, count=1)
    match = _TEMPLATE_FENCED_YAML_RE.search(stripped)
    if match is None:
        raise ValueError(f"{path}: no fenced ```yaml block found")
    fields: set[str] = set()
    for line in match.group(1).splitlines():
        if not line.strip() or line[:1] in (" ", "\t"):
            continue
        key_match = _TEMPLATE_KEY_RE.match(line)
        if key_match:
            fields.add(key_match.group(1))
    if not fields:
        raise ValueError(f"{path}: fenced ```yaml block carries no 'key:' field")
    return frozenset(fields)


def scan_plain_field_block(lines: Sequence[str], start: int) -> dict[str, str]:
    """The plain `key: value` lines directly beneath a heading at `lines[start - 1]` —
    RFC-937's phase-section grammar (§1.1 rule 4, §1.3; `docs/_templates/PHASE.md`'s own
    words: "not built from the closed header field set of §1.5"), the one block form
    §1.5's closed, fenced grammar does not govern (RL-999 §2).

    A bounded scan of `lines[start:]`, stopping at the next heading (any line starting
    with `#`) or a blank line, whichever comes first (RL-999 §3 item 1: "stopping at
    the next heading or the first line that is not key: value" — a blank line is such a
    line). A non-blank *indented* line is read as a continuation of the field above it —
    the same signal RFC-937 §1.5's own closed grammar treats as "not a new key" (there, by
    raising; this grammar has no hard-error concept, so it is tolerated instead) — and is
    skipped without stopping the scan; a non-blank, non-indented line with no `:` does
    stop it. Deliberately **not** `_parse_front_matter_body`'s indented-line rule reused
    verbatim: that grammar rejects a continuation outright, because §1.5 requires knowing
    a document is malformed; this one only needs to know where the field block ends, and
    `docs/_templates/PHASE.md`'s own `exit criteria:` placeholder wraps onto an indented
    second line in the committed template (a pre-existing defect independent of both
    rulings, reported alongside them rather than fixed here — see the PR description).

    Used identically by `scripts/doc-index.py`'s `scan_phase_sections` (a real roadmap's
    phase section) and this module's own `phase_template_fields` (`PHASE.md`'s own body)
    so the two cannot silently disagree about where a phase section's field block ends.

    Unbounded by design in the *other* direction that matters: `lines` is whatever the
    caller already sliced to `start` onward — this function itself never looks past a
    heading or a blank line, which is the fix for `scripts/doc-index.py`'s former `rest =
    "\n".join(lines[idx + 1:])` (RL-999 §3 item 2: "must not survive the fix in any
    form").
    """
    raw: dict[str, str] = {}
    for line in lines[start:]:
        if not line.strip():
            break
        if line.strip().startswith("#"):
            break
        if line[:1] in (" ", "\t"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            break
        raw[key.strip()] = value.split("#", 1)[0].strip()
    return raw


def phase_template_fields(templates_dir: Path) -> frozenset[str]:
    """The field names RFC-937's phase section declares, read from `docs/_templates/
    PHASE.md`'s own body — never transcribed (RL-999 §3 item 3): matches today
    (`("status", "opened", "target", "gates", "exit criteria", "works")`), so this is
    hardening, not repair.

    Raises `ValueError` naming `templates_dir` when `PHASE.md` carries no `##` heading, or
    the heading has no plain field directly beneath it — "silent empty coverage must be
    impossible" (RL-981 §4 item 3), applied here to the one template
    `scripts/audit-docs.py`'s `derive_field_policies` deliberately excludes (a phase has
    no family).
    """
    path = templates_dir / "PHASE.md"
    text = path.read_text(encoding="utf-8")
    stripped = _TEMPLATE_LEADING_COMMENT_RE.sub("", text, count=1)
    lines = stripped.splitlines()
    heading_idx = next(
        (i for i, line in enumerate(lines) if line.strip().startswith("##")), None
    )
    if heading_idx is None:
        raise ValueError(f"{path}: no '##' phase heading found")
    fields = scan_plain_field_block(lines, heading_idx + 1)
    if not fields:
        raise ValueError(
            f"{path}: no plain 'key: value' field found directly beneath the phase "
            "heading"
        )
    return frozenset(fields)
