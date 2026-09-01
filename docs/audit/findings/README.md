# docs/audit/findings — evidence essays for register rows too long to carry inline

`docs/audit/register.md` is the ledger: one row per open finding, and the row is the
authority for its **status** (Work item, Phase, Decision — the fields `register-lint.py`
and `register-owed.py` parse). This directory is not a second ledger. It holds the
**evidence essay** — the Concerns-column prose that established a finding — for the rows
where that essay has grown too long to serve as an index entry at the same time it serves
as the record of how the finding was established. NT-0015 P4 (`docs/notes/0015-the-
register-is-a-ledger-evidence-is-a-file.md` §2) is why this directory exists; Ruling 51 and
Ruling 53 (`docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md`) are what bind its shape below.

## Naming — the F-id, verbatim, nothing else

A file is named `<F-id>.md`, exactly as `docs/audit/register.md` writes the id in a row's
own Finding-id cell: `F27.md`, `F-W9-3.md`, `F-W10-1-1.md`. **No suffix, no slug, no
description.** A filename carrying the concerns phrase (`F27-rating-shapes.md`) would go
stale the first time that phrase is amended, and the register amends daily.

`docs/audit/register.md`'s own `_FINDING_ID` shape (`scripts/audit-docs.py`) is the
authority for what a valid id looks like: `F<n>` or `F-W<n>-<n>` with an optional third
segment. A findings file's name has no other source.

**Limbs never mint a filename.** F27's `(c)`, F43's L1/L2/L3, F45's `(i)`/`(ii)` are
**sections inside the one file** — `## (c)`, `## L1`, whatever heading shape reads clearly
— never `F27c.md`. Minting `F27c` would create an id outside the namespace `CLAUDE.md` §5
and the F42 tombstone hold closed: finding ids are permanent and append-only, and a limb is
not a finding, it is a clause of one.

## The row keeps naming itself

**A migrated row's Finding-id cell is not touched.** It still reads `... (F27)` exactly as
before. `scripts/audit-docs.py` check 25 resolves every finding citation made outside
`docs/audit/` (`docs/research/`, `docs/plans/`, `docs/notes/`) by matching that exact
parenthesised form against `docs/audit/register.md`'s own text — never against this
directory, which the check does not read at all. Move the essay, keep the self-naming: a
citation that resolved before a row's migration resolves identically after it, because
nothing check 25 reads changed.

`register-lint.py` (check 29) and `register-owed.py` read the **Work item** and **Decision**
columns, never Concerns. Migration touches Concerns only — Work item, Phase and Decision
stay in the row, verbatim, because those are exactly the fields that make a row an index
entry rather than an essay.

## What moves, what stays, and which way the link points

**Every field is reduced to an index-level value; both essays move** (NT-0015 P4, `.claude/
notes/0015-the-register-is-a-ledger-evidence-is-a-file.md` §2 — *"The register row becomes
the index entry: id, concerns, work item, phase, decision, owner, status, link"*). Concerns
is not the only cell that can be an essay: a Decision cell that argues its own reasoning at
length (F27's is the case that surfaced this) migrates exactly the same way.

| Stays in the register row | Moves to `findings/<F-id>.md` |
|---|---|
| Finding id cell, self-naming `(F<id>)` unchanged | Both essays: the Concerns reasoning (what was found, how it was verified) and the Decision reasoning (why this disposition, what was weighed) |
| A short Concerns **synopsis** — what the finding is, in one to three sentences, still naming the requirement id(s) it concerns (the row does not become a bare pointer) | Limb detail (F27's `(c)`, F43's `L1`/`L2`/`L3`, …), as sections — never as filenames |
| Decision, compressed to its **disposition at index length**: the opening word (`carry forward`, `accept`, …), the owner, and every token below that a script matches on | The Decision's own reasoning — why, not what |
| A forward link to the findings file | Nothing links back by requirement — the essay is free-standing evidence, not a second index |
| Work item, Phase — unchanged (already index-length) | — |

**The link points one way: row → file.** The register row is what a reader lands on first
(it is what `register-lint.py`, `register-owed.py` and check 25 all read), and it links
forward to the fuller essay for whoever needs it. The findings file does not need to link
back to the row to be resolvable — nothing reads it mechanically — but naming the row's own
`(F<id>)` self-citation once near the top of the file costs nothing and helps a reader who
opened the file directly.

### Compression must preserve every mechanically-matched token

**A register row is read by scripts as well as by people, and a script's read is not
redundant with a person's.** Two predicates in `scripts/register-lint.py` and `scripts/
register-owed.py` currently match on specific substrings of the Decision cell, not on its
length or its meaning — `register-lint.py`'s decision-grammar check matches the cell's
*opening word* (`check_decision_grammar`), and `register-owed.py`'s `review` mode matches
the literal token `§14` **anywhere** in the Decision cell and nowhere else in the row
(`_matches_review`, `_REVIEW_MARKER`) — unlike its work-id mode, which also falls back to
the Work item cell (`_matches_work_id`). Prose that reads as redundant restatement to a
person may be the only thing one of these matches on.

**Shortening a Decision cell can therefore remove a row from a future agenda with no test
failing and no signal printed anywhere** — the same silent-loss shape `docs/audit/register.
md`'s F63 records at the register level, reproduced one layer down inside a single row's own
edit. Before compressing a Decision cell: check what the two functions named above currently
match in it, and keep those tokens verbatim in the compressed sentence. **This list is the
code's, not this README's — if a future predicate is added to either script, this paragraph
is not the place that gets updated; the functions are.** Point a migration at
`scripts/register-lint.py`'s `check_decision_grammar` and `scripts/register-owed.py`'s
`_matches_review`/`_matches_work_id` directly, every time, rather than trust this summary to
still be complete.

**Prove it, don't just inspect for the token.** Run `register-owed.py`'s relevant modes
before and after a Decision-cell compression, on the same tree, and confirm the row appears
in both. Believing a sentence carries a marker and confirming a script still matches it are
different claims; only the second is evidence.

## Write-once, amended in place

Same convention the register's own header already states for a row: a findings file is
**never silently rewritten**. A correction is appended or annotated in place, dated, quoting
what it supersedes — `**Corrected <date>**` or `**Amended <date>**`, naming the PR or commit.
A findings file is deleted only when the finding it evidences is retired the way `docs/audit/
register.md`'s F42 tombstone note describes: the id stays reserved and a tombstone note says
so; the essay is not quietly removed.

## When a row migrates

**Existing over-threshold rows migrate opportunistically, at their next substantive
amendment — never in a bulk sweep, never on a schedule** (Ruling 51). `register-lint.py`
prints the residue — the count of unmigrated rows still over the threshold, against the
corpus size — on every run, as a single aggregate line; that line is what makes "incremental
migration" a checkable claim rather than an assertion nobody can falsify. A row does not
migrate just because it is long; it migrates because it was already being amended for a real
reason and happened to be long enough to be in scope.

**A brand-new finding whose essay is already over threshold uses the split immediately** —
it is filed as a short register row plus its `findings/<id>.md` from the start, never filed
long and migrated later.
