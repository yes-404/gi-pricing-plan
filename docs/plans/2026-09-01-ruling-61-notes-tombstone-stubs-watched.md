# Ruling 61 — Ruling 57's tombstone gains per-file stubs, watched by a new check, not left
unwatched (2026-09-01)

**What this is.** Ruling 57 (`2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`, merged,
frozen) chose a single `README.md` tombstone at the vacated `.claude/notes/` and rejected a
symlink. That record is **merged and frozen**; this is a new, citing record superseding its
tombstone clause for the one case it did not evaluate — per-file stubs — not an edit to that
file (`CLAUDE.md` §12). Slice 4 (PR #544, `refactor/nt-0016-slice4-notes-move`, held by the
executor) implements whatever this record rules; nothing here is implemented by this record.

**What happened.** Moving `.claude/notes/` → `docs/notes/` and writing the single README
tombstone Ruling 57 specifies made `python3 scripts/audit-docs.py` fail with 9 broken-link
errors: 13 frozen plans under `docs/plans/` cite individual old-path notes (e.g.
`../../.claude/notes/0007-context-bound-measures-cap-not-discipline.md`), C4 forbids editing
a frozen plan to fix its citation, and check 1 tests on-disk existence — a directory-level
README does not make an individual old filename resolve. The executor built 18 per-file
redirect stubs instead, which fixes the audit, but flagged — unprompted, correctly — that
nothing now scans `.claude/notes/`: `NOTES` points at `docs/notes/`, `docs.yml` no longer
names the old path, and no other code reads `.claude/notes/`. The stubs sit at a location
watched by nothing, where a stray edit is invisible.

## Acceptance Standard

1. `git grep -c "^# Ruling 61" docs/plans/2026-09-01-ruling-61-notes-tombstone-stubs-watched.md`
   returns `1`, and `git grep -n "^# Ruling \|^## Ruling "  docs/plans/` shows 61 filling the
   gap immediately after Ruling 60 with no duplicate and no skip.
2. §2 names the chosen and both rejected candidates with the evidence that separated them,
   independently reproduced, not relayed.
3. §3 specifies the new check precisely enough to implement without further judgement calls:
   what it globs, what it compares against, and where it is wired into `main()`.
4. §4 states two broken-input cases in a form the executor can turn directly into tests, and
   both must fail the new check before this ruling is considered discharged.
5. `python3 scripts/audit-docs.py` exits 0 on a tree carrying both this record and Slice 4's
   implementation, reporting `18 working notes` unchanged (the `docs/notes/` count, per
   `check_notes` — untouched by this ruling, which adds a check on `.claude/notes/` only).
6. `git grep -nE '\bFR-[A-Z]+-[0-9]|\bNFR-[A-Z]+-[0-9]|\bOQ-[A-Z]+-[0-9]|\bADR-[0-9]'
   docs/plans/2026-09-01-ruling-61-notes-tombstone-stubs-watched.md` returns no matches — no
   requirement id, no spec amendment.
7. `git diff --stat <merge-base>..<branch> -- docs/` names exactly this one new file — no
   frozen plan is edited, and `2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md` (Ruling 57's
   own file) is untouched.

---

## 1. Verified first, independently, against `refactor/nt-0016-slice4-notes-move` at `e2eff6f`

Cloned fresh (`git clone https://github.com/yes-404/gi-pricing-plan.git`), checked out the
branch directly — not relayed from the dispatch or the executor's report.

| Claim | Verdict |
|---|---|
| `.claude/notes/` holds 19 files (18 stubs + README), `docs/notes/` holds 19 (18 notes + README) | **Confirmed** — `git ls-tree -r --name-only <ref> -- .claude/notes/` / `-- docs/notes/`, both 19 |
| Every stub's content is byte-identical to one deterministic template, parameterised only by filename | **Confirmed, all 18** — read every stub with `pathlib`, compared byte-for-byte against the rendered template (§3 renders it exactly; not reproduced verbatim in this cell so this sentence does not itself trip check 1 the way F66 describes — a bracket label immediately followed by a parenthesised target reads as a link even inside backticks) — 0 mismatches across all 18 |
| Without the stubs (README only), `audit-docs.py` fails with exactly 9 broken-link errors, all in `docs/plans/`, all citing `.claude/notes/000N-...md` | **Confirmed, reproduced directly** — moved all 18 stub files out, re-ran `python3 scripts/audit-docs.py`: exit `1`, exactly 9 `broken link in plans/...` lines, each naming an old-path note citation (0007, 0004, 0005, 0014, 0015, 0017, 0003, 0016×2). Restored the 18 files afterward; the check reproduces the dispatch's claim exactly, not merely plausibly |
| With the stubs present, `audit-docs.py` exits 0 and reports `18 working notes` | **Confirmed** — full run on the unmodified branch: `All checks passed.`, `18 working notes, indexed and numbered` |
| `git grep -l "\.claude/notes" -- .` returns exactly `.claude/notes/README.md` plus 13 `docs/plans/` files, nothing else — Slice 4's own acceptance item 1 | **Confirmed** — ran it directly: 14 lines, `.claude/notes/README.md` plus 13 named frozen plans. The 18 stubs pass this only because none of their bodies contains the literal string `.claude/notes` — confirmed by inspection of the template above, which names the target as `docs/notes/{name}` and never repeats the source path in words |
| `NOTES = REPO / "docs" / "notes"`; `.github/workflows/docs.yml` names `.claude/notes` 0 times; no other script reads `.claude/notes` | **Confirmed** — `scripts/audit-docs.py:66`; `grep -n` on `docs.yml` empty; `grep -rn 'REPO / "\.claude"\|ROOT / "\.claude"\|\.claude/notes'` across `scripts/` and `tests/` returns one unrelated hit (`tests/test_watcher_runtime_state.py:38`, a different skill's path, nothing to do with notes) |
| `git log --follow docs/notes/0001-phase-boundary-plan-review.md` reaches the note's original commit | **Confirmed** — reaches `cccd809` ("a numbered working-notes directory, and the audit that keeps it honest (#54)"), through the intermediate rename commit `4ebc85d` and the move commit `e2eff6f` |
| `scripts/audit-docs.py` currently defines checks up to 29; no "check 30" exists yet | **Confirmed** — `grep -n "check 30"` empty; `check_plan_acceptance_standard` (28) and `check_register_grammar` (29) are the highest defined |
| Ruling 57's own rejection of a symlink turned on "both paths equally real, nothing forces migration, a future citer is equally correct either way" | **Confirmed, re-read at source** — `2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md:182-193`. The 18 stubs do not have this property: every stub is legible, explicit prose stating the file moved and where to, not a second live copy indistinguishable from the first — the risk this ruling addresses (unwatched content drift) is real but is not the identical two-homes defect Ruling 57 disqualified a symlink for, which is why this is a new evaluation rather than a reopening of Ruling 57's own verdict |

## 2. Ruled

**Chosen: (3) — keep the 18 per-file stubs, and add a check that watches them: a new check
30, asserting `.claude/notes/` contains exactly the README plus the 18 stubs, each exactly
matching a rendered template, with a stray file or an edited body both failing the gate.**

**Rejected: (1) — the stubs as built, with Ruling 57 amended to permit them and the gap
accepted.** This is an accepted cost with no detector — precisely the shape `docs/audit/
register.md`'s F58 names (a stated mechanism nothing runs, discovered by inspection rather
than by any check firing). §1's own reproduction shows the gap is not hypothetical: with
nothing reading `.claude/notes/` any more, a future stray commit that edits a stub's body,
or adds a 19th file, changes what a reader following an old citation sees, and no command in
this repository's gate would ever notice. An amendment that names this risk and stops there
does not remove it; it only writes down that it was seen.

**Rejected: (2) — revert to the single README and carve the 9 broken links out of check 1.**
Two independent problems, either sufficient to reject it. First, it does not fix
navigability, it hides the audit's evidence of its absence: a human or any tool other than
`audit-docs.py` following one of the 13 frozen plans' old-path links still lands on nothing,
where a stub at least gives a real, resolving, legible redirect. Second, it is a permanent,
hand-maintained special case inside check 1 — the same shape check 1 is already named for in
`docs/audit/findings/F66.md` (a syntactic proxy carrying an exclusion list that does not
generalise) — trading nine known dead links for nine hardcoded exceptions that must be
found and read correctly by every future person auditing check 1's logic, forever, for a
one-time migration event. (2) also does not remove any unwatched-directory risk; it removes
the directory's *presence* but leaves the same class of problem (a checker no longer looking
at something a reader can still reach) in a different shape.

## 3. What check 30 must do, precisely

A new function in `scripts/audit-docs.py`, called `check_notes_tombstone()`, wired in next
to the existing `check_notes(...)` call (the "16–20" section) as its own numbered step:

```python
# 30. the vacated .claude/notes/ tombstone: exactly the README plus the frozen stub set,
# each stub byte-identical to its rendered template — Ruling 61.
check_notes_tombstone()
```

**A frozen, closed registry, not a re-parse of the README's own table** — the same design
choice Ruling 59 made for the census carve-out, for the same reason: deriving the expected
set from a file a stray edit could also touch would let one edit defeat both the content it
changes and the check meant to catch the change. A module-level constant:

```python
OLD_NOTES_TOMBSTONE_DATE: Final = "2026-09-01"
OLD_NOTES_STUB_NAMES: Final[tuple[str, ...]] = (
    "0001-phase-boundary-plan-review.md",
    "0002-demo-entrance-and-guide.md",
    "0003-duplicated-status-goes-stale.md",
    "0004-a-reference-that-resolves-only-for-the-writer.md",
    "0005-deferred-items-with-no-durable-custody.md",
    "0006-two-rules-for-reading-an-artifact.md",
    "0007-context-bound-measures-cap-not-discipline.md",
    "0008-project-closure-audit-structure.md",
    "0009-slim-the-roadmap.md",
    "0010-layered-slice-based-workflow.md",
    "0011-per-agent-model-and-skill-settings.md",
    "0012-a-credential-is-borrowed-not-stored.md",
    "0013-the-lead-is-the-highest-error-node.md",
    "0014-machine-readable-process-core.md",
    "0015-the-register-is-a-ledger-evidence-is-a-file.md",
    "0016-file-taxonomy-reference-coding-and-custody-investigation.md",
    "0017-a-public-repository-needs-a-public-face.md",
    "0018-a-turn-that-ends-strands-what-it-started.md",
)
```

(Verified above, §1, as the exact 18 basenames currently at `.claude/notes/` on the Slice 4
branch — the executor confirms this list against its own PR before landing it, since Slice 4
is still open and this ruling does not freeze what has not yet merged.)

`check_notes_tombstone()`:

1. **Directory check.** `OLD_NOTES = REPO / ".claude" / "notes"`. If it is not a directory,
   `fail(...)` naming the path — the tombstone is unconditionally expected to exist, the
   same posture `check_notes` already takes for `NOTES` itself.
2. **Exact membership.** `sorted(p.name for p in OLD_NOTES.glob("*.md"))` must equal
   `sorted(("README.md", *OLD_NOTES_STUB_NAMES))` — not a superset check, not a subset
   check. Any name present on disk and absent from this set is unregistered — a stray file,
   caught (§4 case 1). Any registered name absent from disk is a deleted stub, also caught
   by the same equality.
3. **Exact content, per stub.** For each name in `OLD_NOTES_STUB_NAMES`, render:

   ```python
   # NOTE: this listing inserts one deliberate space before each opening "(" that
   # follows a "]" — a formatting device for THIS document only, so it does not
   # itself trip audit-docs.py check 1 (F66's own class: a bracket immediately
   # followed by a parenthesis reads as a markdown link even inside a fenced code
   # block). The real implementation has NO such space; §1 already verified the
   # real stubs' exact byte content against this same template with none.
   def rendered_stub(name: str) -> str:
       return (
           "# Moved\n\n"
           f"This note moved to [`docs/notes/{name}`] (../../docs/notes/{name}) on "
           f"{OLD_NOTES_TOMBSTONE_DATE} (NT-0016 Slice 4). See [this directory's "
           "README] (README.md) for the full mapping and why this stub exists rather "
           "than a symlink (Ruling 57).\n"
       )
   ```

   and assert `(OLD_NOTES / name).read_text(encoding="utf-8") == rendered_stub(name)`
   exactly. A body edited in any way — a typo fix, an added sentence, real content pasted
   in — fails (§4 case 2). This is deliberately not a regex or a prefix check: Ruling 59's
   own record (§2) already found a byte-exact comparison stronger and no more expensive than
   a looser pattern match, and the same reasoning applies here — a template this short costs
   nothing to compare exactly.
4. **`README.md` itself is not re-validated by this check.** Ruling 57 already specifies its
   content; check 30's job is the 18 files that specification does not cover, not a second
   check on the one file it does.

## 4. Broken-input proof

Two cases, run against a scratch copy of `.claude/notes/` (or a synthetic fixture directory
shaped the same way — the executor's choice, since this is implementation), each shown to
fail before this ruling is discharged:

- **Stray file.** Add `.claude/notes/0099-not-a-real-stub.md` with arbitrary content
  (including, as the sharper case, content that itself matches the stub template's shape but
  for a name outside `OLD_NOTES_STUB_NAMES`). `check_notes_tombstone()` must fail, naming the
  unregistered file — the membership check in §3 point 2 catches it before content is even
  read.
- **Edited stub body.** Take any registered stub and change its content — append a
  sentence, or replace it with real note prose (the case that matters most: a future
  contributor mistaking the old path for a place to write, exactly the failure mode this
  ruling exists to catch). `check_notes_tombstone()` must fail, naming the file whose content
  no longer matches its rendered template.

Both must be demonstrated failing, then reverted, before PR #544 is considered to satisfy
this ruling — the same standard `CLAUDE.md` §13 already states and Ruling 59/60 already
applied to the census carve-out this session.

## 5. Spec amendment: not needed

This is a CI/audit-mechanism correction closing a gap in an enforcement tool, not a reading
of any numbered requirement. No `FR-`, `NFR-`, `OQ-` or `ADR-` id is touched.

## 6. Where this differs from the dispatch that requested it, if at all

None found on independent verification. The three candidates, the F58 framing for why an
accepted-and-undetected gap is the wrong shape, and the instruction to prove the mechanism on
deliberately broken input are all adopted as stated. One addition beyond what was asked,
volunteered because §1's re-reading of Ruling 57 surfaced it: this ruling is not a
reopening of Ruling 57's own verdict (symlink vs. README), because per-file stubs were never
one of the two options Ruling 57 compared — Ruling 57's disqualification of a symlink turned
on both paths being *indistinguishably* real, which 18 explicit, legible redirect files are
not. Worth stating so a future reader does not take this record as evidence Ruling 57's own
reasoning was wrong; it wasn't asked a question this record answers.
