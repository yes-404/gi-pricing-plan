# NT-0016 — file taxonomy, reference coding and custody: research, and the slice cut

> **For agentic workers:** REQUIRED SUB-SKILL: use `subagent-driven-development`
> (recommended) or `executing-plans` to implement this plan task-by-task, plus
> `test-driven-development` and `git-hygiene` — the three skills
> [`.claude/roles/executor.md`](../../.claude/roles/executor.md) makes mandatory for that
> role. Steps use checkbox (`- [ ]`) syntax for tracking. **Slice 4 additionally binds
> `.claude/skills/docs-audit`**, because it edits the audit script's own scan roots.

**Status: a proposal.** Nothing here is scheduled. [`../roadmap.md`](../roadmap.md) §7
clause 2 makes an adopted note a Work row and the maintainer's signature the thing that
creates it; this plan supplies the shape that row would carry, and binds nothing until the
acceptance line at the foot of this file carries a date.

**Goal:** Turn NT-0016 from a proposal into an executable cut — establish, by measurement
rather than by the note's recollection, which of its seven open questions can be ruled
today; hard-fail the one mechanism that would let its largest act damage the repository
silently; and produce the census and taxonomy draft the remaining questions need before any
of them can honestly be ruled.

**Architecture:** Four slices on **two independent tracks that share no file**. The
*evidence* track (Slices 2 and 3) builds `scripts/file-census.py` and reads its output into
a candidate taxonomy — read-only with respect to every existing document, and worthless to
prejudge. The *custody* track (Slices 1 and 4) fixes a live silent-skip defect in
`scripts/audit-docs.py` and only then moves `.claude/notes/` to `docs/notes/`. The tracks
meet nowhere, which is the point: the census cannot be rushed and the move must not wait on
it. A decision gate sits after Slice 3 and gates only NT-0016's Stages 2–5, which this plan
deliberately does not scope.

**Tech Stack:** Python 3.12 stdlib only for both scripts — `subprocess` over `git ls-files`,
`pathlib`, `csv`, `re`. No new dependency. `pytest` for the tests, at the repository-root
`tests/` tree, which `mypy --strict` already covers.

**Source note:**
[`../../.claude/notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md`](../../.claude/notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md)
(rev 2). **A note decides nothing** — `.claude/notes/README.md`. Everything this plan takes
from it is re-verified below or marked as unverified.

**Prior disposition this plan tests rather than inherits:**
[`2026-08-30-nt-0014-0017-reconciliation.md`](2026-08-30-nt-0014-0017-reconciliation.md) §4,
which recommends *adopt Stages 0–1 only, defer 2–5*. §3 below keeps that recommendation and
changes it in exactly one respect, with the reasoning.

**Process:** [`../process/delivery-process.md`](../process/delivery-process.md) §11 (which
delegates plan obligations to `.claude/skills/writing-plans` and
[`README.md`](README.md)), §15.

**Pinned tree: `b551060`** — `b551060a553055ed1713bcef9e9cb74f1cb88bf5`, `origin/main` at the
time of writing. Every count, every file list and every line reference below was taken at
that commit and is stated with the corpus it was taken over. No number in this plan is
quoted from NT-0016.

**This plan mints no `FR-`, `NFR-`, `OQ-` or `ADR-` identifier**, and proposes none. It is a
plan, not a spec change. It also proposes no roadmap row: a planner does not edit
[`../roadmap.md`](../roadmap.md) (`.claude/roles/planner.md`).

---

## 1. What was re-measured at `b551060`, and where the note is wrong

Two corpora are in play and they give different answers, so each figure below names its own.
**"Tracked" means the output of `git ls-files`.** NT-0016 §9's own reproduction commands use
`find` and `grep -r --exclude-dir=.git`, which walk the *working tree* — in this repository
that includes `.venv/`, `graphify-out/` and `node_modules/` when they exist. A census whose
corpus is the working tree is not reproducible between two checkouts of the same commit.
**Fixing that is Slice 2's first design constraint, not a quibble**: it is the same class as
`CLAUDE.md` §13's rule that a count carries the corpus it counted over.

| Measure | NT-0016 §0, at `7db62ca` | Re-measured at `b551060` | Re-measured at `7db62ca` | Verdict |
|---|---|---|---|---|
| files under `docs/` | 238 | 245 tracked | — | grew |
| files under `.claude/` | 421 | 426 tracked | — | grew |
| files in `docs/plans/` | 113 | 118 tracked | 113 tracked | grew |
| `docs/plans/` files referenced by nothing | 38 of 113 = 34 % | **37 of 118 = 31 %** | 38 of 113 | **reproduces at its own tree** |
| tracked files citing a `.claude/notes/` path | 28 | **35** | 28 | **reproduces at its own tree** |

**The note's two headline numbers reproduce exactly at the tree they were taken on**, over
the tracked corpus, which is the strongest thing that can be said about them. They are not
stable numbers, and no slice below depends on either one holding.

Three things the note gets wrong, each checkable:

**(a) §0's enumeration does not sum to its own total.** It gives the citation surface as 28
and then breaks it down as *"7 frozen plans, 7 intra-notes cross-references, 4 skills,
CLAUDE.md, 2 process docs, 2 audit docs, and three pieces of mechanism"* — which is 26. The
two missing members are `.claude/agents/ci-watcher.md` and `.gitignore`. Both appear in
§3a's step-2 edit list, so the omission is in the arithmetic rather than in the plan of work;
it is recorded because a reader checking the surface against that breakdown would find two
files unaccounted for and not know which side was wrong.

**(b) The test does not pin what the note says it pins.** §0 states that
`tests/test_audit_docs_finding_citations.py` pins `.claude/notes/`. At `b551060` that file
names the path **once, in its module docstring**, and nowhere in executable code; its assertions
run `scripts/audit-docs.py` as a subprocess and never reference the notes directory. A move
would leave that test green and its docstring false. So the mechanism surface is three files
but only **two** of them are enforcing: `.github/workflows/docs.yml` and
`scripts/audit-docs.py`.

**(c) NT-0017's `README.md` does not cite the pre-move path — it cites the notes not at all.**
Both NT-0016 §8 and the reconciliation §4 record a dependency in which the landed README
carries a `.claude/notes/` citation for a later slice to update. At `b551060`, `README.md`
(48 lines) contains no occurrence of `.claude`, and its *Explore the project* tour lists five
destinations — `docs/specs/`, `docs/adr/`, `docs/workflows/`, `docs/audit/register.md`,
`docs/roadmap.md` — and no notes. `CONTRIBUTING.md` and `SECURITY.md` likewise contain none.
**The dependency as written does not exist, and what exists in its place is a stronger
argument for the same move**: the public front door already points only into `docs/`, so the
project's design memory is currently unreachable from it by construction. NT-0016's boundary
question and NT-0017's public-face question are one question, and NT-0017 as landed has
already answered the half it could reach.

### 1a. The citation surface, by mutability class

This is the measurement the sequencing argument actually turns on, and NT-0016 does not take
it. Files containing the literal `.claude/notes`, tracked corpus:

| Class | at `7db62ca` | at `b551060` | Edited by a move? |
|---|---|---|---|
| frozen plans under `docs/plans/` | 7 | 11 | **No** — C4, the tombstone covers them |
| intra-notes, incl. the notes `README.md` | 7 | 8 | Yes, moved with the directory |
| mechanism | 3 | 3 | Yes, and 2 of the 3 are enforcing (see 1(b)) |
| other living documents | 11 | 13 | Yes |
| **total** | **28** | **35** | — |

The 13 living-other files at `b551060` are: `.claude/agents/ci-watcher.md`,
`.claude/skills/README.md`, `.claude/skills/dev-commands/SKILL.md`,
`.claude/skills/docs-audit/SKILL.md`, `.claude/skills/repo-architecture/SKILL.md`,
`.claude/skills/watcher-runtime-state/SKILL.md`, `.gitignore`, `CLAUDE.md`,
`docs/audit/plan-reviews.md`, `docs/audit/register.md`, `docs/process/agent-settings.md`,
`docs/process/delivery-process.md`, `docs/roadmap.md`.

**The obvious argument for moving early is the wrong one, and it is worth saying so.** The
surface grew by 7 files in one day, which reads as "the move gets more expensive every day
you wait". It does not: **4 of those 7 are frozen plans**, which C4 forbids editing and the
tombstone exists to serve, and **1 is an intra-notes reference that travels with the
directory**. The move's actual edit cost — living files — went from 11 to 13 in a day and is
bounded by how often a skill or a process document is written, not by how fast plans
accumulate. **The cost of deferring the move is close to flat.** The argument for doing it
early has to be made on other grounds, and §3 makes it on other grounds.

### 1b. The live defect, proven rather than asserted

`scripts/audit-docs.py:52` defines `NOTES = REPO / ".claude" / "notes"`, one constant with
two consumers: `check_notes` at `:235` (checks 16–20) and the finding-citation scan's
`scan_dirs` at `:505` (check 25). **Both guard on the directory existing and skip silently
when it does not** — `:236` appends the informational line *"no .claude/notes/ directory —
checks 16-20 skipped"*, and `:506`'s `if d.is_dir()` drops the directory from the scan
without a word.

Proven at `b551060`, by loading the script as a module, repointing `NOTES` at a
non-existent path and calling `main()`:

```
  no .claude/notes/ directory — checks 16-20 skipped
  ...
All checks passed.
EXIT CODE: 0
```

**A `git mv` of the notes directory that forgets line 52 leaves the gate green.** That is
the self-inflicted repeat of finding F26 the note predicts, and it is measured here rather
than predicted. It is also **a defect today, independent of any move**: delete or rename
`.claude/notes/` for any reason at all and five audit checks stop running with no signal.
Slice 1 exists because of this paragraph.

---

## 2. Which of NT-0016's seven questions can be ruled now

Each question is answered individually. The decision is the decision-maker's; what this
section supplies is whether the evidence to make it exists at `b551060`.

| Q | Subject | Rulable now? | Why |
|---|---|---|---|
| Q1 | Is the closed category set ruled as drafted, amended, or rebuilt from the census? | **No** | Its own recommended answer is *rebuild from the census*, and the census does not exist. Ruling today rules on the hypothesis — the outcome the question was written to avoid |
| Q2 | One home per category: do rulings records and ledgers stay in `docs/plans/`? | **No** | Presupposes Q1's category set. NT-0016 §9's own name-token sweep, re-run at `b551060` over the 118 tracked filenames in `docs/plans/`, returns 17 distinct tokens — `ledger` 16, `rulings` 11 and `ruling` 10 (one family, 21 files), `slice-map` 4, `closure` 4, `revised` 3, and eleven further tokens at one or two files each. Which of those are *categories* and which are adjectives on another category is exactly what Stage 1 decides |
| Q3 | Verdict-4 declaration form: index marker or category attribute? | **Technically yes, but do not** | The choice is independent of the data, but every consumer of it is downstream of Q1. Ruling it early buys nothing and freezes a form against a category set that does not exist yet. Recommend ruling it with Q1 |
| Q4 | Does the ownership matrix live in `docs/process/` or as a note appendix? | **Yes** | A custody question, answered by C3 and by the frozen/living distinction, neither of which the census touches. The note's own recommendation — living, in `docs/process/`, because it must track charter amendments — is sound and this plan does not improve on it |
| Q5 | Destination: `docs/notes/`, or fold into an existing family? | **Yes** | Decided by C5 alone. The alternative limb is already refuted in the note's own text: folding into `docs/adr/` imports supersede semantics the notes lack, and merging families runs against C2. §1(c) adds the evidence C5 was missing — the public README's tour enumerates `docs/` only |
| Q6 | Tombstone form: a README mapping, or symlinks? | **Yes** | Purely mechanical, and the symlink limb is disqualified by a fact this plan verified rather than assumed: `scripts/audit-docs.py:249` globs `NOTES` for `*.md`, so a symlinked `.claude/notes` would keep resolving after the move and the two roots would both be audited, which is the ambiguity the move exists to remove |
| Q7 | Cite notes by `NT-00NN` id, or by path? | **Split: the notes half yes, the general half no** | The notes half is decided by §1a — id citations survived a move that would have broken 35 path citations. The general citation grammar for *every* category is Stage 2's and presupposes Q1 |

**So: Q4, Q5, Q6 and the notes half of Q7 are rulable at `b551060`. Q1, Q2, Q3 and the
general half of Q7 are not.** That is four of seven, and the four that are rulable are
exactly the four the custody track needs — which is why the custody track does not have to
wait for the census.

---

## 3. The reconciliation's recommendation: kept, with one narrow change

**Kept:** *adopt Stages 0–1 only; defer Stages 2–5.* §2 confirms its central claim on the
evidence rather than on its reasoning — Q1 genuinely cannot be ruled, and Q2 and Q3 hang off
Q1. Scoping Stages 2–5 today would be scoping against a category set nobody has derived.

**Changed, in one respect:** the reconciliation defers **§3a's notes move with Stages 2–5**,
on the ground that sequencing it before the taxonomy is ruled *"would be the tail moving the
dog"*. That ground does not survive §2. The move depends on Q5, Q6 and Q7's notes half, all
three of which are rulable now and none of which the census can inform. It depends on Q1 not
at all: whatever category set the census produces, `note` is a category in it — the note is
the artifact proposing the taxonomy, and no clustering makes the NT series stop existing.

**Three reasons to separate it rather than defer it**, none of which is the cost-growth
argument §1a refutes:

1. **Its hazard is a defect that exists today.** §1b's silent skip is live at `b551060` and
   is triggered by any rename of that directory, not only by this one. Slice 1 fixes it and
   is worth landing whether or not Slice 4 ever runs. Deferring the move defers nothing about
   the hazard; it only defers noticing it.
2. **Its premise is already ruled in the public face.** §1(c): NT-0017 landed a front door
   whose tour is `docs/`-only. Every day that stands, the repository's design memory is
   unreachable from the one file a visitor reads first. That is the exposure NT-0017 was
   written about, in the one directory NT-0017 did not reach.
3. **It is more reversible than it reads.** `git mv` preserves history and is undone by a
   second `git mv`; no frozen file is edited either way; the tombstone is one file. The
   expensive and irreversible thing is not the move — it is **oscillation**, because the
   second move strands the `docs/notes/` citations the first one taught everyone to write.
   So it should be done once, on a ruled destination, and not at all otherwise. That is an
   argument for ruling Q5 before acting, not for waiting on Q1.

**Where the cheap-and-reversible / expensive-and-irreversible line falls**, since that is the
cut the plan was asked to draw:

| | Cheap, reversible | Expensive, hard to reverse |
|---|---|---|
| **Custody track** | Slice 1 — a scan-root hard-fail, one file, one test | Slice 4 — the move; irreversible only through oscillation, so it is gated on a ruling, never on a slice's own judgement |
| **Evidence track** | Slice 2 — a new script, no existing file changed. Slice 3 — a draft document that rules nothing | *(nothing — Stages 2–5 are not scoped by this plan)* |

**The single ordering constraint that matters: Slice 1 lands before Slice 4.** Everything
else may run in any order or in parallel.

---

## 4. The slice cut

Four slices. One TDD leaf each, one PR each, one audit each, one gate each.

| Slice | Deliverable | Depends on | One-line rationale |
|---|---|---|---|
| **1** | `audit-docs.py`'s notes scan roots fail loudly when absent | nothing | Closes a live silent-skip defect, and is the precondition that makes Slice 4 safe rather than lucky |
| **2** | `scripts/file-census.py` + tests + a committed census under `docs/audit/` | nothing | Stage 0; the evidence Q1, Q2 and Q3 need, over a corpus that is stated rather than implied |
| **3** | The taxonomy draft, clustered from Slice 2's output | 2 | Stage 1; a draft that rules nothing, so the decision-maker rules on data instead of on the note's hypothesis |
| **4** | `.claude/notes/` → `docs/notes/`, living citations, tombstone, CI filter | 1, and Q5/Q6/Q7-notes ruled | Stage 3a; separable, mechanically acceptable, and the half NT-0017 could not reach |

**Decision gate, after Slice 3 and owned by the decision-maker:** rule Q1, Q2, Q3 and Q7's
general half against Slice 3's draft. **Stages 2–5 of NT-0016 are deliberately not scoped by
this plan**, and their trigger is that ruling — the same trigger the reconciliation names.

**What this cut is not.** NT-0016 §8 puts the move first, as `S0` of a five-slice Work,
*"because it's self-contained"*. It is self-contained; it is not safe first, because §1b's
skip is upstream of it. This cut keeps the note's instinct and inserts the one slice that
makes it true.

---

## 4a. Acceptance Standard

**Added 2026-08-31, after filing.** See *Corrections after filing* for why this section is
numbered `4a` rather than inserted as a `## 5`, and for the record of what it does and does
not change.

**The honest shape of this plan's standard is a conjunction, and stating it as anything else
would be a formality.** Each slice below carries its own numbered, command-checkable
acceptance, because each slice is one PR, one audit and one gate, and no slice is accepted
on another's evidence. What follows is
therefore the **plan-level** standard: the conjunction, plus the four conditions no single
slice can carry because they are properties of the plan as a whole.

The plan is complete when all eight hold, each by a command a fresh reviewer can run at the
close tree, and each stated with the tree it was run at.

1. **Every slice's own acceptance block passes at the tree its PR merged on.** Four blocks,
   19 items, each named rather than ranged, because a range silently drops an item appended
   inside it: §6.1, §6.2, §6.3, §6.4; §7.1, §7.2, §7.3, §7.4, §7.5; §8.1, §8.2, §8.3, §8.4;
   §9.1, §9.2, §9.3, §9.4, §9.5, §9.6. A slice whose block has an unrun item is not accepted,
   and the verdict is the lead's, never a slice's own.
2. **The gate is green on both halves at the close tree**, not the Python half alone —
   `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`, then
   `python3 scripts/audit-docs.py`, then the frontend half of `CLAUDE.md` §11. A Python-only
   green has been reported as a passing gate in this repository before.
3. **Enforcement is proven on deliberately broken input, three times, and the proofs are
   named with their commands.** §6's mutation of the `NOTES` constant — written at its Step 1,
   run at its Step 2, re-asserted as §6.2 — exits non-zero; §7's Step 5 non-git invocation
   exits non-zero rather than emitting an empty census; §9's Step 8 re-runs the first
   mutation against the moved root and exits non-zero. A check
   that has never printed a failure has not been tested — `CLAUDE.md` §13.
4. **The census reproduces byte for byte at its own tree** — §7.3 — and its companion
   document states the tree, the corpus rule and the row count, which equals
   `git ls-files | wc -l`. A census that cannot be reproduced from a stated corpus is not
   evidence, and §1 above is the measurement showing why.
5. **No frozen file is edited.** `git diff --stat <first-merge>..<close-tree> -- docs/plans/`
   names this plan and no other file under `docs/plans/`, and names it only for appended
   *Corrections after filing* entries. NT-0016 C4 and [`README.md`](README.md).
6. **No identifier is minted and no dependency is added.**
   `git diff <first-merge>..<close-tree> -- pyproject.toml uv.lock` is empty, and
   `python3 scripts/req-coverage.py` reports the same requirement total as at `b551060`.
   §10's prediction table is the falsification route for both.
7. **Every question §2 marks *not rulable* has either been ruled at the decision gate against
   Slice 3's draft, or is carried forward with a named owner.** Q1, Q2, Q3 and Q7's general
   half — cited individually. Silence is not one of the outcomes; `CLAUDE.md` §13's four
   verdicts apply to a deferred question exactly as they apply to an unevidenced requirement.
8. **Slice 4 is not accepted on a green audit alone.** §9.1's grep returns exactly the
   tombstone plus files under `docs/plans/`, §9.3's working-note count matches the pre-move
   tree, and §9.5 shows the `docs` workflow ran on the PR. §1b is the measurement proving a
   green audit after a move is reachable with the checks switched off, so item 3's third
   proof and this item's three commands are what separate *watched* from *quiet*.

**What this standard deliberately does not cover.** NT-0016 §11's own draft acceptance items
(c) through (f) — the ownership matrix, the verdict-2/verdict-4 filings, `file-lint.py`'s
three broken fixtures, and one new file of each high-traffic category born through the
updated skills — belong to Stages 2–5, which §4 leaves unscoped. Claiming them here would
make this plan's completion depend on work it does not describe. Item (b), *every tracked
file resolves to exactly one category*, is likewise Stage 2's; what this plan owes toward it
is Slice 3's draft, and item 7 above is where that debt is discharged or carried.

**Acceptance of the plan as a whole is the maintainer's**, per the undated line at the foot
of this file and `CLAUDE.md` §12. A slice closes on a clean audit and the lead's merge; the
plan does not.

---

## 5. Global Constraints

Every slice's requirements implicitly include these. Values are copied from their sources.

- **`python3 scripts/audit-docs.py` must pass before every commit** — `CLAUDE.md` §0.
- **A count carries the tree and the corpus it counted over; a path citation carries its full
  path** — `CLAUDE.md` §13, fourth bullet. Applies to every figure a slice writes into a
  committed artifact.
- **NFRs and enforcement are proven on deliberately broken input** — `CLAUDE.md` §13, third
  bullet. Slices 1, 2 and 4 each carry such a proof; a check that has never printed a failure
  has not been tested.
- **No new id family is minted, and no `FR-`/`NFR-`/`OQ-`/`ADR-` id is defined** — NT-0016 C2,
  and this plan's own scope.
- **No retro-rename of a cited artifact** — NT-0016 C1. Slice 4 is the single exception the
  note defines, and it moves a directory rather than renaming files.
- **Frozen means frozen.** No slice edits a file under `docs/plans/` other than by appending
  to this one's *Corrections after filing* — NT-0016 C4, [`README.md`](README.md).
- **Stdlib only.** Neither script may add a dependency; `CLAUDE.md` §3's stack is not extended
  by tooling.
- **No `claude.ai/code/session_…` URL reaches GitHub** — `../process/delivery-process.md` §15.
- **Branch from `main`, squash-merge, Conventional Commits** — `CLAUDE.md` §10. The executor
  opens the PR and reports the number; it does not merge.

---

## 6. Slice 1 — make the notes scan roots fail loudly

**Files:**
- Modify: `scripts/audit-docs.py` — `check_notes` at `:235-236`, and `check_finding_citations`'s
  `scan_dirs` at `:505-506`.
- Create: `tests/test_audit_docs_scan_roots.py`.

**Interfaces:**
- Consumes: `NOTES` (`scripts/audit-docs.py:52`), `fail()`, `notes` (the informational list).
- Produces: nothing importable. Slice 4 relies on the behaviour that a missing notes root is
  a non-zero exit.

**The change, stated as behaviour rather than as a diff.** A configured scan root that does
not exist must be a **failure**, not a skipped check. Today `check_notes` returns early with
an informational line and `scan_dirs` filters the directory out with `if d.is_dir()`.
Both become failures naming the missing path and the checks it silenced. The docstring at
`:230-233` already records two deliberate limits of `check_notes`; a third sentence belongs
beside them saying that absence is now an error and why — so the next reader does not
"simplify" it back.

**Do not generalise this to every optional root in the file.** `audit-docs.py` has several
genuine *"— check N skipped"* lines for artifacts the repository may legitimately not have
yet (the process core extract at `:568` is one, and its own §10 governs whether it is
required). This slice changes the two roots that are unconditionally present and whose
absence can only mean a move or a deletion. Widening it is a separate question and a separate
finding.

- [ ] **Step 1: Write the failing test.** Mirror `tests/test_audit_docs_finding_citations.py`
      exactly — subprocess-invoke the script from `ROOT`, assert on `returncode` and
      `stdout`, restore state in a `finally`. Do not invent a fixture idiom.

```python
def test_a_missing_notes_root_fails_the_audit(tmp_path: pathlib.Path) -> None:
    """A configured scan root that has vanished must be an error, never a skip.

    Before this test, repointing NOTES at a non-existent path left the audit printing
    "no .claude/notes/ directory -- checks 16-20 skipped" and exiting 0, so a `git mv`
    of that directory would have silently un-watched five checks.
    """
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'NOTES = REPO / ".claude" / "notes"' in source, (
        "the NOTES constant has moved -- re-derive this test before trusting it"
    )
    patched = tmp_path / "audit-docs.py"
    patched.write_text(
        source.replace(
            'NOTES = REPO / ".claude" / "notes"',
            'NOTES = REPO / ".claude" / "notes-that-do-not-exist"',
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        ["python3", str(patched)], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert "notes-that-do-not-exist" in result.stdout, result.stdout
```

- [ ] **Step 2: Run it and confirm it fails for the stated reason.**

Run: `uv run pytest tests/test_audit_docs_scan_roots.py -v`

Expected: FAIL on the `returncode != 0` assertion, with the captured stdout containing
`checks 16-20 skipped` and `All checks passed`.

**Discriminator — read this before accepting the failure.** A non-zero exit here would be a
plan defect, not a pass: it would mean the script died for some reason other than the missing
root, and the assertion that follows would then be satisfied by the wrong cause. If the test
fails at Step 2 with a non-zero return code, stop and diagnose before implementing anything.
A `ModuleNotFoundError`, a `SystemExit(2)` from argument handling, or a failure naming any
path other than `notes-that-do-not-exist` all mean the harness is wrong.

- [ ] **Step 3: Implement.** In `check_notes`, replace the early return's informational
      append with a `fail()` naming the absent path and the checks it covers, and return.
      In `check_finding_citations`, replace the `if d.is_dir()` filter with an explicit loop
      that calls `fail()` for a missing directory. Add the third docstring sentence.

- [ ] **Step 4: Run the test and the whole audit.**

Run: `uv run pytest tests/test_audit_docs_scan_roots.py -v && python3 scripts/audit-docs.py`

Expected: the test PASSes; the audit exits 0 and its summary still reports the working-note
count. **Both halves matter** — an implementation that fails on a *present* directory would
also make the test pass.

- [ ] **Step 5: Run the Python half of the gate.**

Run: `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`

- [ ] **Step 6: Commit and open the PR.** `fix(scripts): a missing audit scan root fails
      rather than skips`.

**Acceptance, executable:**

1. `uv run pytest tests/test_audit_docs_scan_roots.py -q` passes.
2. The mutation of Step 1 exits non-zero and names the missing path — the broken-input proof.
3. `python3 scripts/audit-docs.py` exits 0 on the unmodified tree and its output still
   contains the `working notes, indexed and numbered` line.
4. `git grep -n "checks 16-20 skipped" -- scripts/audit-docs.py` returns nothing.

---

## 7. Slice 2 — the census script

**Files:**
- Create: `scripts/file-census.py`.
- Create: `tests/test_file_census.py`.
- Create: `docs/audit/file-census-<tree>.csv` and a short `docs/audit/file-census.md` naming
  the tree, the corpus and the command.

**Interfaces:**
- Produces, and Slice 3 consumes: a CSV whose header is exactly
  `path,area,name_pattern,size_bytes,mutability,referenced_by` — one row per tracked file.
  `area` is the first path segment. `name_pattern` is the basename with `\d{4}-\d{2}-\d{2}`
  replaced by `DATE` and every remaining digit run by `N`. `mutability` is one of
  `frozen`, `living`, `generated`, `unknown`. `referenced_by` is an integer.

**Design constraints, each with its reason:**

- **The corpus is `git ls-files`, and the CSV says so.** Not `find`, not
  `grep -r --exclude-dir=.git`. §1 above measured the difference; a working-tree corpus makes
  the census unreproducible between two checkouts of one commit, which is the one property a
  census must have.
- **`referenced_by` counts *tracked files whose content contains the basename*, excluding the
  file itself.** State the rule in the CSV's companion document. It over-counts a common
  basename and under-counts a file cited only by a fuzzy description; both are acceptable and
  neither is silent, because the rule is written down.
- **`mutability` is a guess and is labelled one.** Derive it from directory plus header
  marker only — `docs/plans/` and `docs/audit/work/` frozen, `docs/contracts/` generated,
  `docs/specs/` and `docs/process/` living, everything else `unknown`. **Do not invent a
  heuristic that reads well and cannot be checked.** `unknown` is the honest answer for most
  of `.claude/`, and a large `unknown` count is itself a Stage 1 input.
- **The script takes no view on categories.** Clustering is Slice 3's, by a human reading.
  A script that proposes categories would make Slice 3 review its own output.

- [ ] **Step 1: Write the failing tests** against a synthetic tree, not against the repository
      — the repository's numbers move, and a test pinned to 118 plans fails on the next merge.

```python
def test_name_pattern_normalises_dates_then_digits() -> None:
    assert name_pattern("2026-08-29-w11-3-batch-scoring.md") == "DATE-wN-N-batch-scoring.md"
    assert name_pattern("0016-file-taxonomy.md") == "N-file-taxonomy.md"


def test_referenced_by_excludes_the_file_itself() -> None:
    texts = {"a.md": "see b.md", "b.md": "b.md is me"}
    assert referenced_by("b.md", texts) == 1
```

- [ ] **Step 2: Run them and confirm they fail.**

Run: `uv run pytest tests/test_file_census.py -v`

Expected: FAIL with `ImportError` / `ModuleNotFoundError` naming `file_census` — the module
does not exist. **A failure with any other cause means the import path is wrong, not that the
test is correct.** Note the hyphen: `scripts/file-census.py` is not importable by name, so
the test must load it the way Slice 1's test does — read the path, or use
`importlib.util.spec_from_file_location`. Decide that before Step 3 and do not leave the
executor to guess it.

- [ ] **Step 3: Implement `scripts/file-census.py`.** `--out <path>` writes the CSV;
      default writes to stdout. `--summary` prints the per-area and per-`name_pattern`
      counts. `mypy --strict` clean, `ruff` clean.

- [ ] **Step 4: Run the tests.** `uv run pytest tests/test_file_census.py -v` — PASS.

- [ ] **Step 5: Broken-input proof.** Run the script against a temporary directory that is
      not a git repository and confirm it exits non-zero with a message naming the cause,
      rather than emitting an empty CSV. **An empty census is the failure mode that matters
      here** — it is indistinguishable from a clean repository and would be committed as
      evidence.

- [ ] **Step 6: Generate and commit the census**, naming the tree in both the filename and
      the companion document, together with the exact command and the corpus rule.

- [ ] **Step 7: Gate, commit, PR.** `feat(scripts): file census over the tracked corpus`.

**Acceptance, executable:**

1. `uv run pytest tests/test_file_census.py -q` passes.
2. `uv run mypy && uv run ruff check .` clean.
3. Re-running the script at the same commit reproduces the committed CSV byte for byte —
   `python3 scripts/file-census.py --out /tmp/c.csv && diff /tmp/c.csv docs/audit/file-census-<tree>.csv`.
4. The row count equals `git ls-files | wc -l`, and the companion document states that number,
   the tree, and the corpus rule.
5. Step 5's non-git invocation exits non-zero.

---

## 8. Slice 3 — the taxonomy draft

**Files:**
- Create: `docs/audit/file-taxonomy-draft.md`.

**Consumes:** Slice 2's CSV. **Produces:** a draft. **Rules nothing.**

The draft carries, for each candidate category: purpose, mutability class, today's home,
id family, the census evidence for it (file count and the `name_pattern` values that
clustered into it), and the alternative reading that was rejected. It closes with the four
questions the gate must rule — Q1, Q2, Q3 and Q7's general half — each stated as a choice
between named options rather than as an open prompt.

**Two things it must do that the note's §3 table does not:**

- **Decompose the unreferenced plans into NT-0016 §6's verdict 2 versus verdict 4** — a
  write-only file versus one terminal by design. 37 of 118 at `b551060`. The note calls this
  *"the single most informative output of the whole investigation"* and it is; the draft
  does the decomposition and files nothing, because a verdict on an unevidenced artifact is
  the main thread's under `CLAUDE.md` §13 and never a document's.
- **Name every candidate category no charter creates** — read against the seven files under
  `.claude/roles/`. Under C3 these are findings, not assignments, and the draft says so.

- [ ] **Step 1: Regenerate the census at the current tree and record the tree.**
- [ ] **Step 2: Cluster `name_pattern` by frequency; write one section per candidate
      category with its evidence.**
- [ ] **Step 3: Walk the unreferenced list file by file and record verdict 2 or 4 with a
      reason for each.** All of them. A sampled answer is not one.
- [ ] **Step 4: Read the seven role charters and record which categories no charter creates.**
- [ ] **Step 5: State the four gate questions as named options.**
- [ ] **Step 6: `python3 scripts/audit-docs.py`, commit, PR.**

**Acceptance, executable:**

1. Every `name_pattern` in the census with a count of 2 or more appears in exactly one
   category section — checkable by grepping the draft for each value.
2. The count of files carrying a per-file verdict equals the unreferenced count the census
   reports at the draft's own tree.
3. Every category section names a home, a mutability class and an id family.
4. `python3 scripts/audit-docs.py` exits 0.

---

## 9. Slice 4 — the notes move

**Blocked on:** Slice 1 merged, and Q5, Q6 and Q7's notes half ruled by the decision-maker.
**Not blocked on:** Slices 2 and 3.

**Files:**
- Move: `.claude/notes/` → `docs/notes/`, via `git mv`, history preserved.
- Modify, mechanism: `scripts/audit-docs.py:52`; `.github/workflows/docs.yml`'s two `paths:`
  lists; `tests/test_audit_docs_finding_citations.py`'s module docstring (documentation only
  — see §1(b), it pins nothing).
- Modify, living citations: the 13 files enumerated in §1a, **re-derived at the slice's own
  tree rather than taken from that list**.
- Create: `.claude/notes/README.md` as a tombstone — one paragraph plus the old-to-new
  mapping.
- Not modified: the 11 frozen plans under `docs/plans/`, by C4.

**The three mechanism edits, each with the trap that makes the obvious form wrong:**

1. **`audit-docs.py:52`.** One constant, two consumers — `check_notes` and check 25's
   `scan_dirs` at `:505`. Change it once; do not add a second constant. Slice 1 has by now
   made forgetting this a red gate rather than a silent skip, which is the whole reason
   Slice 1 comes first.
2. **`docs.yml`'s `paths:` filter.** The explicit `.claude/notes/**` entry is **deleted, not
   rewritten**: `docs/notes/**` already falls inside the existing `docs/**` entry. The
   file's existing comment explains why the entry was added; replace it with a comment
   saying why it is now redundant, so the archaeology finding F26 required never repeats.
   **The two `paths:` lists are duplicated deliberately** — the file's own comment records
   that GitHub Actions does not expand YAML anchors — so edit both.
3. **The test's docstring.** Correcting it is cosmetic and must be labelled cosmetic in the
   PR body. Do not let it read as evidence that the test covers the move.

**The tombstone.** A README, not a symlink. Q6's symlink limb is disqualified by
`audit-docs.py:249`, which globs the notes root for `*.md`: a symlinked `.claude/notes`
would keep resolving and both roots would be audited, re-creating the two-homes ambiguity
the move exists to end.

- [ ] **Step 1: Write the failing acceptance check first**, as a test, before moving
      anything — this slice's TDD leaf is the invariant, not the move.

```python
def test_no_living_file_cites_the_old_notes_path() -> None:
    """After the move, `.claude/notes/` may be named only by the tombstone and by files
    that are frozen under docs/plans/README.md's write-once rule.
    """
    tracked = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=ROOT
    ).stdout.split()
    offenders = [
        f for f in tracked
        if ".claude/notes" in (ROOT / f).read_text(encoding="utf-8", errors="replace")
        and not f.startswith("docs/plans/")
        and f != ".claude/notes/README.md"
    ]
    assert offenders == [], offenders
```

- [ ] **Step 2: Run it and confirm it fails**, listing the living citations. Expected: FAIL
      with a non-empty list. **Record the list in the PR body**; it is the slice's own
      re-derivation of §1a's 13, and a count differing from 13 is expected — the surface
      moves — while a count differing *wildly*, or one containing a file class §1a does not
      name, means the sweep found something this plan did not and belongs in
      *Corrections after filing* before the slice proceeds.
- [ ] **Step 3: `git mv .claude/notes docs/notes`.**
- [ ] **Step 4: Edit the three mechanism files.**
- [ ] **Step 5: Edit the living citations the test named.**
- [ ] **Step 6: Write the tombstone at `.claude/notes/README.md`.**
- [ ] **Step 7: Run the test — PASS — then `python3 scripts/audit-docs.py`.**
- [ ] **Step 8: Prove the audit is still watching.** Re-run Slice 1's mutation with the new
      root name and confirm a non-zero exit. **A green audit after a move proves nothing on
      its own** — that is exactly the state §1b showed is reachable with the checks switched
      off.
- [ ] **Step 9: Full gate, commit, PR.** `refactor(docs): move the working notes to
      docs/notes/ (NT-0016 §3a)`.
- [ ] **Step 10: Confirm the docs workflow actually ran on this PR**, by `gh run list` for
      the branch. The PR is its own proof that a notes-only change still triggers the
      workflow through `docs/**`.

**Acceptance, executable:**

1. `git grep -l "\.claude/notes" -- .` returns exactly `.claude/notes/README.md` plus files
   under `docs/plans/`, and nothing else.
2. `git log --follow docs/notes/0001-phase-boundary-plan-review.md | tail -1` shows the
   original commit — history preserved.
3. `python3 scripts/audit-docs.py` exits 0 and its output reports the same working-note count
   as at the pre-move tree.
4. Step 8's mutation exits non-zero.
5. `gh run list --branch <branch>` shows the `docs` workflow ran.
6. `git grep -c "\.claude/notes" -- .github/workflows/docs.yml` returns 0.

**Scheduling.** This slice touches a CI workflow file. Finding F40 records three gate runs
killed by merges landing mid-gate; a workflow-file change is the worst case of that. Land it
at a gap, with no other gate in flight.

---

## 10. Predictions this plan makes, and how to falsify each

Recorded because a plan's predictions are the part a reader has no way to check, and because
this repository has twice had a plan assert *"registers no new error code"* and be wrong in
both — 0 predicted against 4 actual. Each line below is therefore a claim with a command.

| Prediction | Falsified by |
|---|---|
| No slice adds a runtime error code | `git diff origin/main...<branch>` touching any error-code catalogue. **This is a docs-and-scripts plan and no slice enters `backend/` or `packages/`** — that is the reason, not the assertion |
| No slice adds a dependency | a change to `pyproject.toml` or `uv.lock` in any of the four PRs |
| Slice 1 changes no check's verdict on the current tree | `python3 scripts/audit-docs.py` output differing from the pre-slice output in anything but the removed skip line |
| Slice 4 edits no frozen file | `git diff --stat origin/main...<branch> -- docs/plans/` non-empty on Slice 4's branch |
| The living citation surface at Slice 4's tree is near 13 | Step 2's list; a differing count is expected, a differing *class* is a correction |

---

## 11. Self-review

**Coverage against NT-0016.** Stage 0 → Slice 2. Stage 1 → Slice 3. Stage 3a → Slice 4,
with Slice 1 inserted ahead of it. Stages 2, 3, 4 and 5 → **deliberately unscoped**, with a
named trigger in §4. §10's seven questions → §2, individually. C1 through C5 → §5's Global
Constraints. §11's acceptance items (a) through (g) → items (a), (b) partially and (g) are
reachable within this plan's slices; (c) through (f) belong to the deferred stages and are
not claimed here.

**Placeholder scan.** No step says "add appropriate error handling", "similar to Slice N",
or "write tests for the above". Every predicted failure names a cause and a discriminator,
per [`README.md`](README.md)'s second unenforced convention.

**Repository literals verified at `b551060`, not written from memory:** `NOTES` at
`scripts/audit-docs.py:52`; the skip at `:236`; `scan_dirs` at `:505`; the notes glob at
`:249`; `docs.yml`'s two `paths:` lists and its anchor comment; the subprocess idiom in
`tests/test_audit_docs_finding_citations.py`; the four files under `tests/`; the absence of
`.claude` from `README.md`. The one literal this plan could not verify is the exact wording
Slice 1's new `fail()` message will carry, so no acceptance item quotes it — they match on
the path instead.

**Consistency.** `referenced_by`, `name_pattern`, `mutability` and `area` are spelled
identically in §7's interface block, its tests and §8's acceptance. Slice 1's behaviour is
named once and relied on by Slice 4 Step 8 under the same description.

**What this plan does not do.** It rules nothing; it adds no roadmap row; it mints no
identifier; it moves no file. It does not decide whether NT-0016 is adopted — that is the
maintainer's signature on the reconciliation, and this plan is what the row would contain if
it is given.

---

## Corrections after filing

**2026-08-31 — §4a, *Acceptance Standard*, added after filing. Nothing in the plan is
superseded.**

`scripts/audit-docs.py` check 28 landed in `26de823` (PR #510, NT-0014 adoption slice F) with
a cutoff constant of 2026-08-31 and made an explicit `Acceptance Standard` heading a required
field on every plan-kind file filed on or after that date. This plan was filed the same day
and merged as `826d636` about an hour earlier, so it was the first and only file the check
had in scope, and `main` went red on it. The obligation is not new — `../process/
delivery-process.md` §11 already required a plan's acceptance to be executable, and §5 step 4
gates on whether a standard was *defined* rather than *implied*; what `26de823` added is the
field's machine-checkable name and position, which `.claude/skills/writing-plans/SKILL.md`
now defines as the single source.

**Why this is an addition and not an edit to a frozen claim.** [`README.md`](README.md)
freezes a filed plan so that what was believed at its date survives; the rule it states is
against editing a plan *to agree with today's repository*, which destroys the record of which
side was believed. This plan made no claim about its own acceptance standard — it stated
per-slice acceptance and said nothing at the plan level — so §4a contradicts nothing and
overwrites nothing. Every count, every file list and every line reference elsewhere in this
document still reads as it did at `826d636`, and §4a introduces no new measurement: its eight
items cite the slices' existing blocks and §1's existing figures.

**Why it is numbered `4a` rather than inserted as a new `## 5`.** The recommended position in
`writing-plans`' header template is above *Global Constraints*, which here is §5. Taking that
number would renumber §5 through §11, and this document's §11 self-review cites §4, §5, §7
and §8 by number — so a renumber would either break four live citations or require editing
them, which is the frozen-file edit the paragraph above declines to make. `4a` puts the
section exactly where the template asks for it and leaves every existing number and every
citation to one untouched. It is the same device `.claude/notes/0016-…` uses for its own §3a,
and `CLAUDE.md` §5's "never renumber, append" is the rule behind both.

**What a reader should take from this.** The plan as filed did not state a plan-level
acceptance standard. It does now, added a day later under a check that did not exist when it
was written, and §4a says so in its own first line rather than reading as though it had been
there all along.

---

*Further corrections are appended below, each dated, each naming what it supersedes.*

**This section is not optional and it does not live anywhere else.** Corrections to this plan
belong here and nowhere else — not in a sibling ruling, not in a later plan, not in an audit
record. A reader who opens this file must be able to see everything that has been said
against it without knowing that a sibling exists. Where a correction originates in another
document, the finding stays there and a summary plus its citation is appended here.

---

**Maintainer acceptance: accepted as filed, 2026-09-01.** Verbatim, quoted rather than
reasoned around — the maintainer chose *"Accept the whole plan as filed"* from four options,
the alternatives being acceptance limited to Slices 1 and 2, Slice 1 alone as a standalone
defect fix, and a continued hold. **All four slices are scheduled from this date.** The two
dependency gates the plan states in §4 are unaffected by this line and still bind: Slice 4
does not begin until Slice 1 has merged and until Q5, Q6 and Q7's notes half are ruled by the
decision-maker; Slice 3 does not begin until Slice 2's census exists. Acceptance of the plan
*as a whole* — §4a's eight-item standard — remains a separate act at its close.

**What this line does not do.** It does not date
[`2026-08-30-nt-0014-0017-reconciliation.md`](2026-08-30-nt-0014-0017-reconciliation.md),
whose own acceptance line is still `_pending._` The sentence this one replaces named that as a
second condition; the maintainer's answer was given against this plan and is recorded against
this plan only. §3 above *changes* that reconciliation's recommendation in one narrow respect
— it separates the notes move from the deferred Stages 2–5 rather than deferring it with them
— and accepting this plan as filed accepts that change **for the purposes of this plan's four
slices**. The reconciliation's remaining three dispositions are untouched and still bind
nothing. Flagged here rather than resolved silently, because deeming an undated line accepted
by implication is exactly the record loss `CLAUDE.md` §0 exists to prevent.
