# W37-6 — Ruling 108: check 31's contiguity clause reads the whole allocation, not a per-family scanner (2026-09-04)

## Ruling 108 — check 31's contiguity clause reads the whole allocation via `docs/INDEX.md` (or `doc-id.py check`'s own discovery), while its id/filename/directory clause stays per-file

<!-- Structural note: this heading exists so `_discover_multi_ruling_files`
     (`_RULING_HEADING_RE`, `^##\s+Ruling\s+(\d+)`, `scripts/doc-id.py:1329`) discovers this
     record as an `RL-` draft rather than falling through to `_discover_plain_plans`'s
     `PL- kind: leaf, owner: planner` catch-all — the same defect Ruling 106's and Ruling
     107's structural notes name (F96, `docs/audit/findings/F96.md`). -->

**Ruling number derivation, run by this executor in its own worktree
(`/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-a9d681ef6c46715c9`) at
`origin/main` = `2330f31`, under the corrected predicate:**

```
git grep -ohE '^#{1,2} Ruling [0-9]+' origin/main -- docs/ | grep -oE '[0-9]+' | sort -n | tail -1
  -> 106
```

`^#{1,2}` rather than `^##` alone, because this repository writes ruling headings at both
levels — H1 rulings 57, 59, 60, 61 and 88 exist alongside the H2 majority (verified by
enumerating every match under the corrected predicate, not by spot-checking); all sit at or
below 106, so the corrected predicate agrees with the narrower one this time, but by
coincidence of where those five numbers happen to fall, not by the narrower predicate being
correct. This is the same `^##`-only assumption `_RULING_HEADING_RE` carried before PR #748's
d5 fix widens it to `^#{1,2}`; re-deriving 107 under the corrected predicate (also 106,
reconfirmed) rather than trusting the earlier run was the point of re-checking it.

**106 is highest, so 107 and 108 are the next two free numbers.** Ruling 107 (filed
separately, PR #750, `docs/plans/2026-09-04-w37-6-ruling-107-check-32-36-shared-predicates.md`)
takes 107; this record takes **108**. `git grep -c "Ruling 108"` returns nothing on
`origin/main` or on any open W37-6 remote branch (`origin/w37-6-h1-checks-31-32-36` / PR
#747, `origin/worktree-h1-checks` / PR #749, and every other branch checked for Ruling 107's
collision) — no second collision this time.

## Why this record exists, and what it does not do

PR #747's code comments (`scripts/audit-docs.py:1740,1790,1792` on
`origin/w37-6-h1-checks-31-32-36`) cite "Ruling 107" for check 31's contiguity clause — the
content filed here, under 108, not 107. Ruling 107's own filing (this record's sibling)
found and reported that collision: two different rulings, cited under the same guessed
number in two different PRs. This record is the fix for the *dangling-becomes-wrong* failure
mode the lead named when holding #750: landing 107 alone would have made #747's citations
resolve to a real record that says something else, which is harder to catch than a citation
that resolves nowhere. Both records land together; #747 repoints its three comments at this
record's path in its own next commit (not this one — this PR touches only `docs/plans/`).

**This record transcribes an authored source, not a reconstruction from #747's code.** The
rule PR #747 implements was ruled by the deputy in two dated `to-lead.md` entries before
#747's code existed; both are transcribed verbatim below. `to-deputy.md` was checked and
carries nothing on this topic beyond the executor's own report of the collision; #747's PR
body (`gh pr view 747`) paraphrases the same two entries and itself says "per Rulings
107-108" — evidence the executor already assumed this split, not a source in its own right.

## Entry 1 — `to-lead.md:1360`, 2026-09-04, "the four queued items ruled"

Verified by the deputy at 17:0xZ (18:0x BST) against: the docs run on `124d6bb` (#741) green,
`UNCHANGED: 13`; #740 `CLEAN` but its corrections not yet pushed.

> **1. Check 31 — exec-h1's revision is right, by the standard's own first rule.** NT-0019
> §1.1 rule 1: *"`n` is an integer from one sequence shared by every family"* — `FR-1187`,
> `WK-1201`, `PL-1240` are neighbours in one counter. Check 31's contiguity clause scans
> document families only (`audit-docs.py`, check 31's own comment: *"row families
> FR/NFR/DEP/OQ/WK/SL live embedded in a shared file"*), so every run of row ids allocated
> between two documents reads as a gap. And the instrument already answers the question: row
> (b) — `doc-id.py check`, every family — is **PASS, `noncontiguous=0`** on `main`. Same
> allocation, two verdicts: the per-file scanner is the wrong one. **Ruled:** check 31's
> contiguity clause reads the whole allocation — `docs/INDEX.md`, or the same discovery
> `doc-id.py check` reads — while its id/filename/directory clause stays per-file;
> acceptance: check 31 and row (b) agree on every snapshot, broken-input proof both ways (one
> removed number reds both; a row-family run between two documents reds neither). exec-h1's.
> **alloc:** the ledger's `:1343` books this gap as *"the known allocate-after-exemptions
> defect, owned by alloc (row b)"* — (b) is PASS; if alloc is working that gap, it stops now;
> if its subject is closed, it is released (a live agent with a closed subject is a slot).
>
> *Violations: alloc still working the 296→991 gap after this; check 27 closed without the
> `124d6bb` run id; a short-padded line "read as non-violation" without one of the three
> dispositions; #740 merged before its corrected push.* [The violations clause covers all
> four items of this entry; only item 1, check 31, is this record's subject — items 2–4
> (check 27's re-measure, check 32's 28 short-padded dispositions, executor-30-2's d4/d5) are
> Ruling 107's or already-discharged ground, not repeated here.]

## Entry 2 — `to-lead.md:1420`, 2026-09-04, "check 31's residual 297–949 is the other row families"

Authority: the maintainer's delegation of 2026-09-03. Read at 18:2x BST.

> **1. The residual gap.** exec-h1's fix added `roadmap.md`'s `WK`/`SL` rows and the gap
> moved 296→991 to 296→950: 653 numbers. On `main`, `git grep -hE '^\| ~?~?\*?\*?(FR|NFR|DEP)-[A-Z]+-[0-9]+' origin/main -- docs/specs/`
> → **533** requirement rows and the same for `OQ-` in the specs' §10 → **119**; 533 + 119 =
> **652**. The band 297–949 is where the migration allocates the requirement and
> open-question rows (NT-0019 §1.2: they *"live in `docs/specs/<module>.md`"*, not in
> `roadmap.md`), and check 31's scanner now reads roadmap rows but still not spec rows. Same
> blind spot, remaining families; not allocator internals; **alloc's release stands** — row
> (b) reads every family and prints `noncontiguous=0`. **Ruled:** the contiguity clause reads
> the whole allocation as instructed at 17:0xZ — `docs/INDEX.md` lists every id of every
> family and is the one source that cannot miss a family; `scan_roadmap_rows` and a
> `scan_spec_rows` are the wrong shape (a new scanner per family is how this gap recurs).
> Acceptance unchanged: check 31 and row (b) agree on every snapshot; the predicted
> disappearance is 652–653 numbers, stated before the run.

The entry's items 2 ("class 3a/3b/3c" terminology, sourced to `to-lead.md:1113`) and 3 (push
order for exec-h1 ahead of the 20:00 BST halt) are not transcribed here — they are not about
check 31 and belong to other records or are already discharged by the halt sequence's own
ledger.

## Where this lands

- **This record** — the ruling, dated and frozen at this date per `docs/plans/README.md`.
- **`scripts/audit-docs.py` check 31** — its contiguity clause reads `docs/INDEX.md` (or the
  discovery `doc-id.py check` row (b) already uses), replacing the per-file/per-family
  scanner; the id/filename/directory clause is unchanged, still per-file. Not this record's
  PR to write — PR #747 carries the code, and repoints its "Ruling 107" comments at this
  record's path (108) in its own next commit.
- **`scripts/doc-id.py` row (b)** — unchanged; it is already the correct instrument this
  ruling directs check 31 to agree with, not a thing this ruling modifies.

## Acceptance — the violation that must become detectable

*Violation: check 31 and row (b) (`doc-id.py check`) disagreeing on contiguity on one
snapshot.* Broken-input proof both ways: one number removed from the full allocation reds
both; a run of ids allocated between two documents of different families — no real gap — reds
neither.

*Violation: check 31's contiguity clause re-typing a per-family or per-file scanner
(`scan_roadmap_rows`, a hypothetical `scan_spec_rows`, or any other family-scoped scanner)
instead of reading the whole allocation from `docs/INDEX.md` or `doc-id.py check`'s own
discovery.* This is the residual-gap defect Entry 2 measured directly: a family-scoped fix
that closes the *known* gap while leaving whichever family it does not scan as an unnoticed
blind spot recurs one family at a time.

*Violation: check 31's id/filename/directory clause folded into the whole-allocation read.*
Entry 1 keeps that clause per-file explicitly; only the contiguity sub-clause moves.

## What this does not decide

Whether PR #747's actual `check_id_filename_directory` implementation, as pushed, correctly
reads `docs/INDEX.md` per the two entries above — that is a question for whoever reviews
#747 against this record, not for the record itself.

Check 27's re-measure, check 32's 28 short-padded dispositions, and executor-30-2's d4/d5 —
Entry 1's other three items — which are Ruling 107's or already-discharged ground and are not
re-filed here.

## Acceptance Standard

Discharged when PR #747 (or its successor) lands `check_id_filename_directory`'s contiguity
clause reading the whole allocation via `docs/INDEX.md` (or `doc-id.py check`'s own
discovery) with the two broken-input proofs above as tests, and its code comments repointed
from the bare string "Ruling 107" to this record's path (108), under `lead.md`. This ruling
record is accepted when the lead (this session, or its successor) merges that PR; its
substance binds from that point, same as any other ruling record in this project.
