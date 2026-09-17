---
id: RL-1039
family: ruling
title: `check 37` governs documents authored from a template; a verbatim-migrated body is out of its scope, marked by `was:`
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-03
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-03-w37-6-d1-d2-rulings.md
---

# W37-6 — D1 and D2 ruled: check 37's jurisdiction, and `RL.md`'s body shape (2026-09-03)

**What this is.** The two decisions put as **D1** and **D2** in
`docs/plans/PL-01032-reserved-to-the-maintainer-one-batch-f90-s-prior-question-filed-2026-09-03.md` — **on branch
`docs/w37-6-go-ahead-reask-v2`, PR #659, unmerged, so it is deliberately not linked from here:
the path does not resolve on `main` and `audit-docs.py`'s link check is right to say so** —
taken by the maintainer on 2026-09-03 and filed here as **Rulings 96 and 97**. That record's
Decision lines are the maintainer's to fill; this record is the dated artifact the decision
lands in, per `CLAUDE.md` §12 (*"every decision lands as a dated artifact — never in chat"*).

**Filed under** the time-boxed delegation of
[`RL-01049-w37-6-the-maintainer-s-time-boxed-delegation-2026-09-03.md`](RL-01049-w37-6-the-maintainer-s-time-boxed-delegation-2026-09-03.md) §1,
which delegates *"RFC-937 §1/§4 amendments needed to reach a completing, green run — owner
values, scope markers, stamp-set membership, exemption dispositions, and template body shapes
(`docs/_templates/`)"*. RL-1039 is an **exemption disposition** and RL-1040 a **template
body shape**; both are named in that sentence.

**Everything measured here was measured at `15ed00d`** — `origin/main`'s tip when this record
was written, and this branch's base — on a disposable snapshot, by running the code rather
than reading it. §4 carries the predicate for every figure.

## Authority

- **The decisions are the maintainer's.** The citations, the implementation and the
  measurements are this role's, and §1 and §2 name the cell each ruling reads from.
- **`CLAUDE.md` is not amended and neither is RFC-937 §1.** RL-1039 **uses a field the
  closed field set already declares** rather than adding one — which is why it is an amendment
  to nothing. Had it needed a new key, that would have been a §1 edit and therefore reserved.
- **The two options not taken are priced in §1.3 and §2.3**, each against a measurement, not
  against an argument.
- **F90 is not edited from this branch.** Its amendment is PR #656's and is unmerged; every
  figure attributed to it below is cited to that PR.

## Acceptance Standard

The violation this record must make detectable: **a check reporting a green it did not earn.**

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 96 then 97, no duplicate, no skip.
2. RL-1039's exemption is keyed to a field **RFC-937 §1.5 already declares**; a ruling that
   invented `migrated:` would have been a closed-field-set amendment and reserved.
   *Violation: a new header key introduced by this record.*
3. **Both broken-input proofs are executed and their output pasted** (§3): a marked body with
   no sections must pass; an unmarked post-flag-day ruling missing a section must red.
   *Violation: either proof asserted rather than run.*
4. **The green is reported with its coverage, not as a bare zero.** §4 states how many
   documents the check examined, how many it exempted, and **how many it actually enforced
   anything on** — which is `0` on the migrated corpus, and is disclosed as such.
   *Violation: `check 37 reds 0` recorded without the enforced population beside it.*
5. Every figure carries the tree it was measured at and the command that produced it
   (`CLAUDE.md` §13, [`RFC-777`](../rfcs/RFC-00777-a-reference-that-resolves-only-in-the-writer-s-context.md)).
   *Violation: a count without its predicate.*
6. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.

---

## RL-1039 — `check 37` governs documents authored from a template; a verbatim-migrated body is out of its scope, marked by `was:`

### 1. Verified first, at `15ed00d`

**(a) The prior question is real, and F90 says so in its own words.** From
`docs/findings/FD-01027-check-37-reds-on-95-of-95-post-migration-rulings-unconditional-on-the-flag-day-because-its-section-detector-cannot-see-a-level-heading.md` §B item 2, on branch `audit/f90-amendment` (PR #656, unmerged),
**lines 227–233** at that branch's tip:

> *"Three of the four required sections do not exist in the corpus under any name, at any
> depth, numbered or not. `Question`, `Ruling` and `Rationale` are 0 of 95 in every column. No
> change to the detector can make a single migrated ruling pass check 37, because the sections
> it requires were never written. **The template's body shape does not describe how rulings are
> actually written**; it describes how a ruling authored from `RL.md` after the standard lands
> would be written. That is the real disagreement, and it is not a matching bug."*

That sentence is the ruling. `check_shape` derives its required set from a **template**; the
migration does not author from templates, it stamps a header onto a body that already existed.

**(b) The field already exists — this is the check the delegation asked for, and it changes
the act.** RFC-937 §1.5's closed field set, `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md:125`
(mirrored verbatim at `docs/process/document-ids.md:130`):

```
was: 2026-08-18-profile-contract.md   # migration only
```

**`was:` is the provenance field, and its comment is the jurisdiction rule.** It names the
pre-standard file a body was carried over from; a document authored from a template after the
standard lands has no such file and therefore no `was:`. **No new key is added to a closed
field set** — the alternative the delegation warned about, and the reason it told this role to
look first.

**(c) It cannot be inherited by accident.** Measured, not assumed:

```
$ git grep -ln "was:" -- docs/_templates/    →  (no output)
```

**Zero of the thirteen templates declares `was:`.** An author copying `RL.md` cannot acquire
the exemption, which is precisely the cost D1's option A was priced with
(*"needs a durable, checkable marker for 'migrated verbatim' that a later author cannot
inherit by accident"* — `2026-09-03-w37-6-maintainer-decisions.md`, D1 options table, row A).
That cost is **discharged by the field the standard already has**, not paid.

**(d) It is already parsed, and already written only by the migration.**
`scripts/_docid.py:135` lists `"was"` among the permitted keys and `scripts/_docid.py:303`
parses it into `Header.was` (`scripts/_docid.py:98`), so `check_shape` can read it with no
change to the parser. `scripts/doc-id.py` sets `was=<the old relative path>` on the migration's
document write paths (`:1279`, `:1380`, `:1430`, `:1540`, `:1643`, `:1904`, `:2727`) and
`was=None` only where it stamps a **Reference** header onto a vendored or module file
(`:3838`, `:4470`) — a family whose required set is empty either way (§4).

**(e) My own instrument agrees with #656's, and the difference is fully explained.**
Reproducing F90 §F at `15ed00d` rather than `32fc63c` (predicate in §4):

| Family | #656, at `32fc63c` | This run, at `15ed00d` |
|---|---|---|
| `plan` | 119 | **121** |
| `ruling` | 95 | 95 |
| `closure` | 38 | 38 |
| `proposal` | 20 | 20 |
| `ledger` | 10 | 10 |
| `research` | 2 | 2 |
| **Total** | **284** | **286** |
| Examined | **529** | **531** |

**The whole delta is `plan`, +2, and `docs/plans/` gained exactly two files between those two
trees** (#653's and #658's). Five of six families are identical. This is agreement at two
trees, not two instruments agreeing on one number.

### 2. Ruled

**`check 37` applies to a document authored from its family's template. A body the migration
carried over verbatim from a pre-standard file is out of its scope, and `was:` is how the
document says which it is.** The exemption is honoured on creation, by the field the migration
already sets.

Implemented in `scripts/audit-docs.py` `check_shape()`: a document whose header carries a
non-`None` `was:` is counted as examined and then skipped, and the check's note reports the
exempt count rather than folding it into the total.

**Struck, both of them.** Neither is a live option and both are recorded here as the priced
alternatives, with the measurement that kills each:

- **Date-grandfathering** — exempting by `created:` against the ruling-form flag-day. **Struck.**
  It keys the exemption to *when a file was written* when the thing that matters is *what it
  was written from*; a pre-flag-day document later re-authored from the template would stay
  exempt forever, and a post-flag-day migration of an old body would be caught wrongly. `was:`
  keys it to provenance, which is the actual predicate.
- **Depth-agnostic detection as the remedy for F90.** **Struck as a remedy** (it survives as a
  *component* of RL-1040, which is a different claim). `F90.md` §B item 1 measured it end to
  end: *"Confirmed by running a depth-agnostic `check_shape` end to end: check-37 ruling
  failures go 95 → **95**."* And §B's table (`F90.md`, the three-column table under §B) shows
  the ordinal barrier behind it: `Acceptance — …` is `0` at any depth and `30` only *"after
  stripping a leading `N. `"*, while `Question`, `Ruling` and `Rationale` are `0` in **all
  three** columns. Depth alone reaches nothing; depth plus ordinal reaches one section of four.

### 3. What it obliges

- The exemption is **provenance-keyed and one-way**: nothing but the migration writes `was:`,
  and removing it puts a document back in scope. A body that is later rewritten to the
  template's shape should have `was:` dropped in that same commit.
- **The 292 exempt documents are not certified.** They are declared out of jurisdiction, which
  is a scope decision, not a pass. Bringing their bodies to their families' declared shapes is
  the work D1's option B names, and it is **not** discharged here or by W37-6.
- **This does not touch W37-6's irreversibility.** No body is rewritten; the change is to a
  check and a template.

### 4. Acceptance — the violation that must become detectable

**The violation: `check 37` reporting a green it did not earn** — either by exempting a
document that was authored from a template, or by reporting a bare zero over a population it
enforced nothing on.

*Violation: a document with no `was:` field, of a family with a non-empty required set, missing
one of those sections, and check 37 silent.* Proved red in §3 of RL-1040 below (proof 2).

*Violation: a `was:`-marked body with no sections at all failing check 37.* Proved passing in
§3 of RL-1040 below (proof 1).

*Violation: the figure `check 37 reds 0` appearing in a gate record without the enforced
population beside it.* The enforced population on the migrated corpus is **0**, and §4 of
RL-1040 states it in the same table as the zero.

---
