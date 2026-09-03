# W37-6 — Ruling 104: the CI step reads the verdict set, and Ruling 68's class 6 is a property with the generated READMEs and every `INDEX.md` inside it (2026-09-03)

**Filed** 2026-09-03 by the maintainer, recorded by the deputy on the maintainer's instruction.
**What this is.** Three decisions the lead put to the maintainer in the deputy channel on
2026-09-03 (its entries of 20:31 and 20:33 BST), each cheap and reversible, each an amendment to
a sentence in one of the maintainer's own prior rulings. All three were signed as drafted on
2026-09-03. None of the three was the lead's, the decision-maker's or the deputy's to make, and
none of them was made by anyone else: the lead held the workflow file unedited, and
`executor-verify` was told to let an unclassifiable hunk fail and be named rather than invent a
class for it. That holding position is what this record replaces.

**Tree for every citation: `origin/main` = `f6c9ff2`** unless a ref is named beside it. Every
figure and line number here is the deputy's own run.

## Authority

- **An amendment to what a maintainer's own prior ruling required is the maintainer's alone**
  (`CLAUDE.md` §12). Decision 1 amends Ruling 102 §1's CI sentence; decisions 2 and 3 amend
  Ruling 68 §2's class 6. Both prior rulings are the maintainer's.
- **The frozen records are not edited.** Ruling 102 and the preconditions rulings stand as
  filed; this record supersedes the sentences it names, in the pattern Ruling 102 §3 used for
  §8.5 of the delegation record.
- **The deputy holds no authority.** It drafted the three readings, priced the alternative
  for each, and put them to the maintainer with the cell each reads from; the maintainer signed
  each one. The deputy's role here is the recorder's.

## Ruling 104 — exit 1 is the recorded standing red, not a failing check; class 6 is defined by its property; `INDEX.md` means every one

<!-- Structural note: this heading exists so `_discover_multi_ruling_files`
     (`_RULING_HEADING_RE`, `^##\s+Ruling\s+(\d+)`) discovers this record as an `RL-` draft
     rather than falling through to `_discover_plain_plans`'s `PL- kind: leaf, owner: planner`
     catch-all — the defect F96 (`docs/audit/findings/F96.md`) was filed for. -->

**Ruling number derivation, run by the deputy in its own checkout at `f6c9ff2`:**

```
git grep -hE '^#{1,6}[ \t]+Ruling[ \t]+[0-9]+' origin/main -- docs/ \
  | grep -oE 'Ruling[ \t]+[0-9]+' | grep -oE '[0-9]+' | sort -n | uniq | tail -1     → 103
git grep -hE '^#{1,6}[ \t]+Ruling[ \t]+[0-9]+' $(git branch -r | grep -v HEAD) -- docs/ \
  | grep -oE 'Ruling[ \t]+[0-9]+' | grep -oE '[0-9]+' | sort -n | uniq | tail -1     → 103
git grep -c 'Ruling 104' $(git branch -r | grep -v HEAD) -- docs/ .claude/ scripts/  → no match
```

**104 is the next free number**, on `main` and on every remote ref, derived rather than assumed.

### 1. The `docs` workflow's `--verify` step passes on exit 1 with an unchanged verdict set, and fails on exit 2 or 3

**The sentence amended.** Ruling 102 §1
(`docs/plans/2026-09-03-w37-6-ruling-102-verify-instrument.md:48-49`): *"It runs in CI on
every PR touching `doc-id.py` or `audit-docs.py`, and is red on `main` until green."*

**What changed underneath it.** PR #698 (merged as `f6c9ff2`) gave the instrument a recorded
verdict set and a third exit code. `scripts/_docverify.py` at `f6c9ff2`: `EXPECTED_VERDICTS`
(`:1654`) records every row's verdict; `diff_verdicts` (`:1696`) reports every difference;
`VerifyResult.exit_code` (`:1737`) reads, in its own docstring, *"0 green · 1 the standing red,
unchanged · 3 the verdict set moved"*, with exit 2 reserved for a refusal to run. The set tracks
**rows, not figures**: row (b)'s count moving 77 → 78 under two merges was not a set change
(the lead's own run, relayed here from its 20:31 BST entry).

**Ruled.** *"Red on `main` until green"* means **the row table exits 1 on `main`** — the
standing red is a recorded fact, printed as `UNCHANGED: N fatal row(s), matching the recorded
set of N`, and it stays red in the instrument's own output until every row is green. **The CI
step is not that fact's carrier.** The `docs` workflow's step
(`.github/workflows/docs.yml:66` at `f6c9ff2`) **passes on exit 1 and fails on exit 2 or 3.**

**Grounds.** A check that is red before a regression and red after it reports nothing about
the change under review — F102 (`docs/audit/findings/F102.md`) measured exactly that: an
ordinarily-named audit record took row (a) from `none=0` to `none=1` and the only signal was one
line inside a job that was already red. `CLAUDE.md` §13's sentence — *a check that has never
printed a failure has not been tested* — has an inverse that is just as binding: a check that
cannot print a pass has not been wired. Exit 3 is the sentence a reviewer needs (*"this change
moved a row"*), and it existed for half a day with no consumer.

**The alternative, priced and refused.** Leave the step failing on exit 1. Every docs PR then
carries a red `docs` job for the life of W37-6, every merge is a log-reading exercise, and
F102's class recurs at the next ordinarily-named document. That is the state the repository was
in between #689 and #698, and it produced one measured miss in that time.

**What this does not change.** The instrument's own exit code (1 on `main` until green) is
untouched, and Ruling 102 §1's other clauses — snapshot only, nine rows as one table with
predicates, no hand-maintained gate table — are untouched. The **go-ahead** for the run is still
the instrument's exit 0 at a quiet tree, never the job's colour.

### 2. Ruling 68's class 6 is defined by its property; the four names are examples; the §5.2 generated READMEs are members

**The sentence amended.** Ruling 68 §2
(`docs/plans/2026-09-02-w37-migration-preconditions-rulings.md:265-266`): *"6. a generated
artifact regenerated in full — `INDEX.md`, `REDIRECTS.csv`, `docs/contracts/`, the core-JSON
digest (§4 step 7)."*

**The gap it left.** NT-0019 §5.2 makes several `README.md` files **generated** — the
`workflows/` and `adr/` README tables, and the new `closures/`, `findings/`, `rulings/` and
`ledgers/` READMEs. `scripts/doc-id.py:5152-5154` at `f6c9ff2` says so in the code's own words:
`_MIGRATION_DIFF_FAMILY_READMES` names itself *"the seventh kind of hunk a clean run now
produces"* and a *"further extension of Ruling 68's six-class enumeration"*, flagged for
ratification rather than assumed. The ratification never happened; the second-fail handover's
§11 recorded the phrase *"Ruling 68 class-6 ratification"* as resolving to nothing in `docs/`,
and the decision-maker's reading of §7(g) (PR #699, `docs/plans/2026-09-03-w37-6-row-g-reading.md`
§3.1) found the same gap independently. Under Ruling 68's own rule at `:268` — *"a hunk the
filter cannot classify fails; it is never passed through"* — every regenerated README is a red
hunk the moment the six classes are implemented.

**Ruled.** **Class 6 is the property, not the list**: *a generated artifact regenerated in
full* — a file whose entire content is the output of one of the migration's generators, replaced
whole and never partially edited. `INDEX.md`, `REDIRECTS.csv`, `docs/contracts/` and the
core-JSON digest are its **examples**; the §5.2 generated READMEs are **members**;
`_MIGRATION_DIFF_FAMILY_READMES` is **ratified as class 6**, not as a seventh class.

**Grounds.** A seventh class named for a file would be a class defined by path, which Ruling 68
§2 already refused at `:232` on measured grounds — thirteen §5.2 rows put script output and hand
edits in the same file. A property-shaped class keeps the checkable predicate that class 6
already had: the whole file equals the generator's output. **That predicate is what the
implementation must test.** A README hunk that is a partial edit — some lines regenerated, some
carried by hand — is *not* class 6 and fails, which is the protection §8's *"same commit"* H rows
need.

**The alternative, priced and refused.** Ratify a seventh class. The closed list then grows by
one every time a generator is added, and each new generated file fails until someone ratifies
it — the state the READMEs have been in since 2026-09-03 morning.

### 3. Class 6's `INDEX.md` means every `INDEX.md` the migration generates

**The word amended.** The same sentence's bare `INDEX.md`. NT-0019 §1.4 puts one at
`docs/INDEX.md`; Ruling 101 and Ruling 102 §6 create one **per family** — `docs/closures/INDEX.md`
carries the split-source sections, `docs/plans/INDEX.md` the same for a plan that splits into a
`PL-` and nested `RL-` rulings. The decision-maker's reading (#699 §3.2) observes that a
separate `_MIGRATION_DIFF_FAMILY_INDEXES` constant exists because the code's author could not
tell which was meant — `NT-0004`'s shape, a reference that resolved only for its writer.

**Ruled.** `INDEX.md` in class 6 means **every file of that name the migration generates** —
`docs/INDEX.md` and each per-family `INDEX.md`. All are generator output in full, so §2's
property already covers them; this decision adds the word *every* so the text no longer has to
be inferred from the code.

**The alternative, priced and refused.** Top-level only. Every per-family index is then an
unclassifiable hunk that fails by `:268`, in every clean run, with no reading of the standard
that makes it wrong.

## What happens next, and what does not

- **Task 21 (executor-verify, the six classes in `row_g`) proceeds under Ruling 68 as ruled,
  with §2 and §3 above as the text of class 6.** The lead's holding instruction — let an
  unclassifiable hunk fail and be named — stands for anything *outside* the property.
- **Decision 1 is one line in `.github/workflows/docs.yml`**, the lead's to dispatch. Until it
  lands, the `docs` job stays red on every docs PR, this one included.
- **Nothing here opens a window**, and the go-ahead remains the instrument's exit 0 at a quiet
  tree (Ruling 102, *"What happens next"*). The Work close remains the maintainer's alone
  (`CLAUDE.md` §12).

## Acceptance Standard

**This record is accepted when it is merged.** Its three decisions bind from that point.

**Implementation: owed** (delegation §7.5 — a ruling names its implementing PR or carries
`implementation: owed`). No implementing PR exists for any of the three. Decision 1's
implementation is the `docs.yml` step's exit-code handling; decisions 2 and 3 are implemented by
task 21's class-6 classifier in `scripts/_docverify.py`, which must test the property and not a
filename.

### Acceptance — the violation that must become detectable

*Violation: the `docs` workflow's `--verify` step failing on exit 1 with an unchanged verdict
set, after decision 1 is implemented.* **The broken-input proof:** a docs PR that changes no
row must show a green `docs` job; the same PR with one deliberately unclassifiable file added
under `docs/` must show a red one, with the log naming the row that moved.

*Violation: the instrument itself exiting 0 on `main` while any row is red* — decision 1 moves
the job's reading, not the instrument's.

*Violation: the go-ahead for the run taken from the `docs` job's colour rather than from the
instrument's exit 0 at a quiet tree.*

*Violation: a class-6 classifier keyed on a filename or a path — `README.md`, `INDEX.md`, or any
list of them — rather than on the property that the whole file equals the generator's output.*
**The broken-input proof:** a regenerated README with one hand-edited line inserted must fail
(g), naming the file; the same file regenerated whole must pass.

*Violation: a seventh class, or a class-6 allow-list, added to `row_g` to absorb the READMEs.*

*Violation: a per-family `INDEX.md` failing (g) as unclassifiable on a clean run.*

*Violation: Ruling 68 §2's or Ruling 102 §1's text edited in place rather than superseded by this
record.*
