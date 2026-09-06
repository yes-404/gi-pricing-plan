---
family: reference
title: Working notes
status: active                  # active → retired (§1.2a)
created: 2026-08-15
owner: lead
corrected_by: []
relates: []                      # ids only
was: docs/notes/README.md
---

# Working notes

Notes from the maintainer to Claude Code: requests, standing intentions, and the assessment
each one got before work started.

**One file per topic**, numbered `NNNN-kebab-title.md` and identified as **`RFC-711`** — the
same convention as [`docs/adr/`](../adrs/README.md), for the same reason. Not per
day: a topic is worked, argued about and closed on its own schedule, so a date-named file
mixing two of them ages into a record where half is stale and half is live, with nothing to
say which. Dates belong in the header block, where they describe the *topic*.

`NT-` follows the short-prefix family the suite already uses — `FR-`, `NFR-`, `OQ-`, `DEP-`
— rather than spelling the word out, and the four digits match `ADR-NNNN`, so the repository
has one padding width for file-per-item series rather than two. The filename carries exactly
the digits the id does: **`RFC-711` lives in `0001-…md`**, one number to read, not two
spellings of it.

The number is the note's permanent identity, and it behaves as an ADR number or an `FR-` id
does under `CLAUDE.md` §5: **assigned once, never renumbered, never reused.** A note that is
dropped or deleted retires its number with it, so a reference written in a commit message or
a roadmap row can never silently come to mean a different topic later.

```bash
# Next number. One sequence, shared by every family.
python3 scripts/doc-id.py next
```

**A note is not authoritative.** `docs/` is the contract and `CLAUDE.md` is the working
standard; a note is the raw material that may *become* a spec change, an ADR, an entry in
`docs/open-questions.md`, or a roadmap row. Nothing here decides anything — if a note's
conclusion matters after the session that produced it, it belongs in the suite, and the note
must say where it went.

## Index

**There is no index table here.** [`../INDEX.md`](../INDEX.md) is generated from the
documents themselves — one row per id, every family — so it cannot disagree with the
directory the way a hand-maintained list does. `ls docs/rfcs/` is the other reading, and
the padded id leading each filename is what makes it sort.

## What a note must contain

A header block of exactly these fields, then the body.

| Field | Why |
|---|---|
| **Raised** — date and who | An undated intention ages into a false record of what was wanted, and when |
| **Status** — `open` · `accepted` · `landed` · `superseded` · `dropped` | See the verdicts below. There is no "unstated" |
| **Deliverable** — named per `CLAUDE.md` §0's table: code, spec change then code, spec-change-only, or an `OQ-` entry | §0 is the project's rule for what a request produces; a note that skips it invites building ahead of the phase |
| **Owner** — who accepts, who drafts | A proposal with no acceptor never becomes a decision |
| **Lands in** — the paths and sections the outcome will change | The note is the input; the suite is the output |
| **Sequencing / Trigger** — when this becomes workable | Distinguishes "not yet" from "not agreed" |

The body carries: the request in refined form, **Claude's assessment attributed and kept
separate** from the maintainer's words, acceptance criteria, the next step, and the original
wording. That last section is corrected for grammar and punctuation only — never for
wording, structure or meaning — and says so, so that "original" stays a true label rather
than a courtesy. Keeping the two voices apart matters for the same reason `CLAUDE.md` §0
refuses to let code and spec be quietly reconciled — merging them destroys the record of who
believed what.

## What a note must not contain

- **Decisions.** A choice constraining more than one module is an ADR
  (`.claude/skills/adr-write`); an unresolved one is an `OQ-` entry in
  `docs/open-questions.md`. Never settled in a note.
- **Requirements.** `FR-`/`NFR-` IDs are permanent and live in `docs/specs/` only
  (`CLAUDE.md` §5). A note may *propose* one; it may not carry one.
- **Duplicated status.** Workstream and phase state lives in `docs/roadmap.md`. A note that
  restates it will disagree with it within a week.
- **Secrets, credentials, or dataset contents** — `.claude/skills/secret-hygiene`.

## The audit standard

**Half of it runs in CI; the other half cannot.** `scripts/audit-docs.py` checks 16–20 cover
this directory, and `.github/workflows/docs.yml`'s `docs/**` path filter already covers it
(this directory lives under `docs/`), so a note-only commit runs them. What the script
cannot answer is whether a status is
*true* — that is judgement against the repository, and it stays manual.

**When:** the mechanical half on every commit that touches a note, via CI or
`python3 scripts/audit-docs.py` locally. The judgement half at every workstream close, in
the same pass as `close-workstream`.

**Seven checks. Each note, every time** — the ⚙ ones are enforced by the script, and the
rest are yours:

1. **Status is verified, not remembered.** Check it against `docs/roadmap.md` and the git
   log, not against what you recall doing. This is `CLAUDE.md` §13 step 1's rule — evidence
   before recollection — applied to the notes themselves. *(Manual: the script can see that
   a status is well-formed, never that it is true.)*
2. ⚙ **Every reference resolves.** Relative links, `FR-`/`NFR-` ids, `OQ-` ids and ADRs are
   checked by check 19. Prose references — a spec §, a test name, a symbol — are yours. A
   note pointing at something that no longer exists is a defect in the note, and it is the
   most common way one turns into fiction: the claim still reads true.
3. ⚙ **Every topic has a verdict.** One of the five statuses, never silence — check 16
   enforces the header block and the vocabulary. That `landed` records *where*, and
   `dropped` *why*, is manual: the reasoning is the part worth keeping and no script can
   judge it.
4. ⚙ **The prohibitions hold.** Check 20 refuses a note that *defines* a requirement id.
   Decisions and duplicated roadmap status are manual — they are recognisable only by
   meaning.
5. **The deliverable still matches `CLAUDE.md` §0** for the phase the project is *now* in. A
   topic scoped to code before its phase has started is spec-change-only until then, and a
   note carrying a stale deliverable is an invitation to build ahead of the phase.
   *(Manual — check 16 asserts the field exists, not that it is right.)*
6. ⚙ **Numbers are intact.** Four digits, unique, allocated in sequence from `0001`, and
   matching the `NT-NNNN` in the file's own heading — check 17. No number reused, no note
   renumbered: a deletion leaves a gap, and the gap is correct, so contiguity is deliberately
   *not* asserted. This is what `docs/adrs/README.md` calls "never renumbered" and
   `CLAUDE.md` §5 requires of requirement ids; a recycled number is worse than a missing one,
   because every earlier reference to it silently repoints. **Reuse across a deletion is the
   one part no snapshot can catch** — the retired number is gone from the tree — so that
   remains yours.
7. ⚙ **The generated index matches the files.** `../INDEX.md` is built from the documents
   themselves by `scripts/doc-index.py`, so the agreement check 18 used to make by hand —
   every note listed, every listed row backed by a file — is now a property of how the
   index is produced. What stays yours is the same half check 18 never covered: whether a
   row's **status** is true of the repository.

**Verdicts, and what each obliges:**

| Status | Means | Obligation |
|---|---|---|
| `open` | Raised, assessed, not agreed | Nothing is built |
| `accepted` | Maintainer agreed, with a date | Named in a roadmap row before work starts |
| `landed` | The outcome is in `docs/` or the code | Record where; delete the note at the end of the phase, keeping the index line and its number |
| `superseded` | Another note or an ADR replaced it | Link the replacement by number — `NT-NNNN` or `ADR-NNNN` |
| `dropped` | Decided against | Record why — a dropped idea with no reason returns |

**The failure this standard exists to prevent:** a directory of confident-sounding notes
that describe a repository which has moved on. That is worse than an empty directory,
because it is read as current — the same argument `CLAUDE.md` §13 makes about a
silently-passing check being worse than no check.

## Tracking

`docs/notes/` is not in `.gitignore`, so these files are committable and currently
untracked. Commit a note when its assessment is the record of why something was or was not
built. A `landed` note is deleted at the end of its phase — git keeps the history, and the
index line keeps the pointer.
