# W37-6 — Ruling 103: one reading each for §7(e) and §7(f), and Ruling 102 §6's routing rule made computable (2026-09-03)

**Filed** 2026-09-03 by the decision-maker. **What this is.** Ruling 102 §2 assigns the
decision-maker two of the six work-list rows — *"(e)/(f) — each gets one reading, ruled by the
decision-maker citing §7's sentence — not two"* — and Ruling 102 §6 rules the cross-family
index placement without yet stating it as something a script can compute. This record
discharges all three: two readings, each as a predicate, and §6 turned into a routing rule with
its three sources named and its violation made detectable.

**Everything below was verified in this session's own worktree at `e97b97a`** (`main`, the base
of branch `docs/w37-6-ef-readings`). Two figures are marked **relayed** where they were measured
by another party at another tree and this session could not reproduce them on this tree; every
other figure carries the command that produced it.

**`implementation: owed`.** No implementing PR exists. The implementing change is
`doc-id.py migrate --verify`'s rows for (e) and (f) and `_split_index_family`'s replacement, all
of which Ruling 102 §1 and §2 already assign to `executor-verify`. **Until that PR is merged and
named, this ruling has changed no behaviour.**

## Authority

- **Ruling 102 §2 assigns the (e) and (f) readings to this role by name**, and its acceptance
  section makes the alternative a violation: *"(e) or (f) recorded with two readings after the
  decision-maker's ruling, or ruled by the lead rather than the decision-maker."* Now at
  `docs/plans/2026-09-03-w37-6-ruling-102-verify-instrument.md` on `main`, merged as **#684**
  (`4988dca`). **When this record was drafted it was on no merged ref** and was read at
  `origin/docs/w37-6-ruling-102-rebased`; the branch citation is replaced rather than re-dated,
  because a reader following it after that branch is deleted would find nothing.
- **Ruling 102 §6 is the maintainer's and is not reopened here.** Its rule is quoted verbatim in
  §3 below and implemented, not re-decided. `CLAUDE.md` §12 puts the merge and the four verdicts
  with the lead; this record is a proposal in that one respect and in no other.
- **The constraint Ruling 102 §2 imposes on the method** — *"citing §7's own sentence … and not
  by choosing the more convenient number"* — is discharged explicitly in §1.4 and §2.4, which
  state for each reading what verdict it produces and why the verdict is not the ground.

## Ruling 103 — a padded id is a lint error where it names a real governed thing; (f) is measured across the migration; a split source's index section lives where §5.2 routes it

<!-- Structural note: this heading exists so `_discover_multi_ruling_files`
     (`_RULING_HEADING_RE`, `^##\s+Ruling\s+(\d+)`) discovers this record as an `RL-` draft
     rather than falling through to `_discover_plain_plans`'s `PL- kind: leaf, owner: planner`
     catch-all — the defect F96 (`docs/audit/findings/F96.md`) was filed for. -->

**Ruling number derivation, run in this session's own worktree at `e97b97a`:**

```
git grep -hE '^#{1,6}[ \t]+Ruling[ \t]+[0-9]+' origin/main -- docs/ \
  | grep -oE 'Ruling[ \t]+[0-9]+' | grep -oE '[0-9]+' | sort -n | uniq | tail -1   → 101
git grep -n 'Ruling 103' $(git branch -r | grep -v HEAD) -- docs/ .claude/ scripts/ → exit 1
```

**102 is taken by the unmerged `docs/w37-6-ruling-102-*` branches**, which is why the `main`-only
maximum of 101 is not the answer: the derivation was re-run across **every remote ref**, and 102
appears on two of them. **103 is the next free number**, derived rather than assumed.
(`git grep -h` drops filenames and is used here only to compute a maximum, never to cite.)

---

## 1. §7(e) — "no padded id in prose"

### 1.1 The sentence, and the two rules it rests on

§7's clause is three words long, so the reading is made from the standard the clause enforces.
`docs/notes/0019-one-id-per-document.md` §1.1 (line 426 carries §7; §1.1 is at lines 20–23) and
its verbatim lift `docs/process/document-ids.md` §1.1 give two rules, and **the reading is what
falls out of reading them together rather than either alone**:

> **Rule 2.** *"Citations write the integer, never padding: `PL-1240`, `RL-65`, `RFC-16`,
> `FR-1187` … A padded id in prose is a lint error. **No exception**: prose, headings
> (`# RL-1241 — …`), commit messages, PR titles, branch names, code comments, docstrings, test
> markers, link text."*

> **Rule 3.** *"Filenames pad the integer to the standard's width, currently five:
> `PL-01240-<slug>.md`. Padding exists so `ls` sorts; it is not identity. The resolver treats
> `PL-1240`, `PL-01240` and `PL-001240` as one id."*

Three things in those two sentences decide the predicate.

**First, rule 2's subject is a *citation*, not a character sequence.** Every one of its eight
named contexts — prose, headings, commit messages, PR titles, branch names, code comments,
docstrings, test markers, link text — is a place where one document *refers to another*. The
list ends at **link text** and stops there: the link *target* is a path, and rule 3 requires that
path to be padded. So the standard already draws a line, and it draws it at **use**, not at
appearance.

**Second, rule 3 makes padding mandatory in exactly the place rule 2 does not reach.** A padded
run of digits inside a filename is not an exception carved out of rule 2; it is a context rule 2
was never about. `PL-01240-<slug>.md` in a document is an exhibit of the filename form.

**Third, rule 3 names the resolver as the arbiter of identity** — *"the resolver treats
`PL-1240`, `PL-01240` and `PL-001240` as one id"*. That sentence is what makes the reading
computable, and it is the one this ruling turns on: **whether a token is a citation is decided
by whether it resolves to a governed thing**, which the standard's own generated `docs/INDEX.md`
answers by construction (§7(c) already requires that index to exist and be byte-stable).

### 1.2 The ruling

**A padded id is "in prose" — and therefore a violation of §7(e) — when it names a real governed
thing outside a filesystem path.** Formally, an occurrence of `<PREFIX>-<digits>` in any tracked
file is a violation if and only if all three hold:

| # | conjunct | what it is for |
|---|---|---|
| 0 | the occurrence is in `(d)`'s corpus — **`REDIRECTS.csv` and `was:` lines excluded**, per §7(d)'s own exclusion, and **not inside a fenced code block** | (e) and (d) must not disagree about what the corpus is; a fence is how a record exhibits a defective form without committing it |
| 1 | `digits` is padded — a leading zero, and **exactly `_docid.PAD_WIDTH` digits**, read from the symbol and never written as a literal | the form rule 2 forbids and rule 3 requires in filenames |
| 2 | the occurrence is **not** part of a filesystem path token, tested **after stripping markdown emphasis** — it does not contain `/`, and is not the leading component of a filename ending `.md` | rule 3's mandatory padding, and every link *target* |
| 3 | the unpadded id is listed in `docs/INDEX.md` | rule 2's subject: a **citation** names something |

**Conjuncts 0 and the two qualifiers in 1 and 2 were added on 2026-09-03 after measurement, and
§5 records what each was worth.** They are not refinements of taste: one of them moves the
population by 355 occurrences and another accounts for two of the six survivors.

**Conjunct 3 is the ruling.** Conjuncts 1 and 2 are the measurement everybody has already run —
they are what both existing measurements ran (**relayed**, and they disagree — 36 and 77 after a
path filter each party wrote itself; §1.4 and §4.2) — and they are what leaves that population
undecided. Conjunct 3 decides it, because a token that resolves to nothing is a **specimen of the
form**, not a citation of a document, and rule 2 says nothing about specimens.

### 1.3 Why this is not a carve-out for the defining document, and why that matters

The live question put to this role was *"does a padded id appearing in a document that defines
the id format count as in prose?"* — with the standing precedent that `audit-docs.py` checks 19
and 28 and `tests/test_notes_move_citations.py` have each red-flagged a document for **defining**
an id form, and that distorting the defining document was the wrong fix.

**First, the precedent's status and its actual content, both corrected against the repository
rather than accepted as briefed.** The claim reached this role as *"distorting the defining
document was ruled the wrong fix."* **Neither half survives checking.** It is not a ruling — it
is a cross-session working note, and **this session found no ruling record stating it**. And the
repository's three instances did not resolve that way; each was read at `e97b97a`:

| mechanism | the defining document it fired on | how it was actually resolved |
|---|---|---|
| **check 19** (`ADR-(\d{4})`, `scripts/audit-docs.py:418`) | NT-0019's width-5 ADR filename examples | **the document was distorted** — three examples rendered as `ADR-<nnnnn>` placeholders, and the audit record describing that had to split its own digit run as `ADR-000`+`01` so as not to retrigger the check it describes (`docs/audit/nt-0019-verification-and-impact-sweep.md:16-22`) |
| **check 28** (plan acceptance standard) | a ruling record filed in `docs/plans/` | **the document was changed** — *"The lead did not patch the check … and instead added a genuine `## Acceptance Standard` section to the record"* (`docs/audit/findings/F68.md:14-21`); the classification defect was filed as **F68** and carried forward with the S2 migration as its trigger |
| **`tests/test_notes_move_citations.py`** | NT-0019 and three documents about the migration | **the check's scope was narrowed** — `_SPECIFICATIONS_OF_THE_OLD_PATH`, a four-entry, individually-reviewed, per-file list, with an explicit prohibition on widening it: *"each needs its own reviewed line added here, not a widened pattern"* (`:111-114`) |

**So the repository's record is the opposite of the briefing on two of three counts, and only the
third took the remedy the working note prescribes.** This ruling does not cite the note as
authority, and does not claim the precedent forbids what it in fact twice did.

**What the third instance does establish is the shape a correct exemption takes: reviewed,
explicitly bounded, and never a widened pattern.** Conjunct 3 is that shape carried one step
further — **a property, not a list**. An exemption keyed on *which document* the token sits in is
a blocklist, and a blocklist grants the defining document a licence it must not have. Conjunct 3
keys on whether the token **names anything**, which no document can claim on its own behalf.

**Two consequences, and the second is why this is not merely tidier.** The defining document's
`PL-01240-<slug>.md` is cleared by conjunct 2 (a filename) and its
`PL-1240`/`PL-01240`/`PL-001240` triple by conjunct 3 (`PL-1240` names no plan; it is a
specimen). Neither clearance mentions the document. **And conjunct 3 red-flags a real defect that
every document-keyed list would have hidden**: `scripts/doc-id.py:2757` writes, in a docstring,
`token_map["F84"] = "FD-00084"`. **That is padded, it is a docstring — rule 2 names docstrings —
and `FD-84` is a real governed thing.**

**What that line describes is worse than a padded value, and the correction is recorded here
because the first reading of it was wrong.** `token_map` has two kinds of writer: an **id**
branch, `token_map[d.old_token] = canon` with `canon = _docid.canonical(...)`, unpadded always
(`scripts/doc-id.py:5883,5901`; `scripts/_docid.py:104-108`); and a **path** branch,
`token_map.update(_path_rewrite_tokens(old, new))` (`:5926,5958,5965,5981,5998`), whose values
are full paths. `FD-00084` is neither. And the id branch is guarded — `scripts/doc-id.py:5900`
reads `if d.old_token is not None and d.prefix != "FD":`, so **`token_map["F84"]` is never set at
all**, on the maintainer's ruling quoted in the comment above it: *"The essays get ids and paths
now; `F<n>` stays a resolver alias to W37-11."* **The docstring asserts an assignment the same
file's code explicitly refuses to make**, and both lines entered the tree in one commit
(`git log -S` on each string → `2f0467e`, #671, and nothing else). Contradictory from birth.

**So the exemplar is a padded id in a docstring that is also wrong about its own function** —
and `doc-id.py` would sit at the top of any self-documentation exemption list, where both defects
would have survived. **It is not a live behaviour defect**: the code is correct, and a
document-keyed exemption is what would have kept it invisible.

**Filed as [`F100`](../audit/findings/F100.md)**, with the register row carrying the same
disposition: the fix is to the docstring and never to the guard, because admitting `FD` at
`:5900` would make the sentence true by reversing a maintainer's ruling.

### 1.4 What this reading makes the row, stated before the rationale can be accused of following it

**§7(e) FAILS as currently measured, and this ruling does not rescue it.**

Conjuncts 1 and 2 alone leave **36 occurrences on one party's filter and 77 on another's** (both
**relayed**; §4.2, and the table below is what that disagreement shows). Conjunct 3 has never
been applied to either population. The reported characterisation is *"mostly the standard
documenting itself"* — and **"mostly" is a concession that the remainder is not**. A row whose
population is non-empty under every predicate anyone has run, and unmeasured under the ruled
one, is a **FAIL**
until the executor measures it under the full predicate and it comes back zero. This session's
own measurement on the unmigrated tree already produces one conjunct-3 violation it can name —
`scripts/doc-id.py:2757` (§1.3) — so the row is not merely unmeasured; it is known non-empty.

**The ruling is the same either way.** Had conjunct 3 been shown to empty the 36, this reading
would be unchanged: it is derived from rule 2's subject and rule 3's resolver sentence, both of
which were written before any of this was measured.

**Independent evidence that the row had to become a predicate, and it is the strongest available
because neither party produced it for that purpose.** Two measurements of (e) now exist, taken by
different parties (both figures **relayed** — the handover's and the auditor's; this session ran
neither):

| party | broad | after a path filter |
|---|---|---|
| the handover | 2021 | **36** |
| the auditor | 2042 | **77** |

**The broad figures agree to within 1%. The narrow figures differ by a factor of two, and the
row's size moves by a factor of 26 between the broad and narrow readings of the same corpus.**

**Read what that isolates.** Broad agreement means the two parties saw substantially the same
corpus and the same padded-token population; the disagreement is therefore located almost
entirely in **the filter**, which is the one thing neither published. This is F85's finding
recurring exactly — two counts at the same tree over the same corpus differing only by the
pattern, **both satisfying `CLAUDE.md` §13 as it stood** — and it is why §13's predicate clause
was added on 2026-09-02. **A row whose size moves 26-fold on an unstated filter is not a
measurement anybody can check**, and the disagreement is not resolvable by preferring one
number: it is resolvable only by fixing the predicate, which is what §1.2 does.

**The verdict is unmoved by this and that is the point.** (e) fails at 36 and it fails at 77;
nothing about which number is right changes the row's colour. **What moves by a factor of two is
the work list** — how many occurrences someone has to go and fix — and a work list is exactly the
thing Ruling 102 §2 turns these rows into. So the argument for one ruled reading is not
tidiness; it is that the two parties were pricing the same work at 36 and at 77 with no way to
tell which, and neither was wrong under the row as written.

**One boundary against §7(d), because measuring (e) without it produces a false alarm.** At
`e97b97a` the padded-form population is dominated by the legacy four-digit `ADR-0nnn` form — of
the 480 occurrences surviving a path filter, **450 are `ADR-0nnn`** (`git grep -hoP '(?<![\w/])(FR|NFR|OQ|DEP|WK|SL|WF|ADR|RFC|PL|LG|RL|RS|CR|FD)-0[0-9]{3,4}\b(?!-|\.md)' | sed -E 's/-[0-9]+$//' | sort | uniq -c`,
run by the delegated agent at `e97b97a` and reproduced in shape here). **Those are §7(d)'s, not
§7(e)'s**: `ADR-0[0-9]{3}` is one of the thirteen legacy forms §7(d)'s own grep bans outright, so
on the migration's merge tree they are gone by (d) or (d) has failed. Conjunct 3 clears them at
(e) because a legacy `ADR-0001` does not resolve to a post-migration governed thing — it is a
**pre-migration** id whose four digits are identity, not padding. **The two rows partition the
work; neither is weakened.** An (e) implementation that also counted the legacy forms would
report (d)'s failure as (e)'s and hide the boundary between them.

**A second boundary, against §7(g), and it is conjunct 3's own blind spot — named here rather
than left for someone to find.** Conjunct 3 clears any token that does not resolve through
`docs/INDEX.md`. **A token corrupted by the token-boundary defect does not resolve**, so (e)
clears it. That is correct division of labour and not a gap in (e): a mangled id is §7(g)'s row,
where `NFR-RATE-13/14 → NFR-775/14` is already the named broken-input proof, and (e) has nothing
to say about a token that is no longer an id at all.

**But it means (e) cannot be read as a proxy for id health, and a green (e) row over a corrupted
tree is exactly what conjunct 3 would produce.** The same shape has already been measured on the
neighbouring row: row (d)'s `F-W[0-9]` alternative read **0 and now reads 216** after
`executor-g`'s fix (**relayed** — the auditor's verification at `aedc1b9`; not run by this
session), and **the 0 was a false pass manufactured by the corruption itself**, because the
tokens had been mangled into `F-WK-*`, which that pattern cannot match. A row that reads clean
*because* its input is broken is the failure mode all three of these rows share. **§7(g) must be
green before (e)'s number means anything**, which is also the order Ruling 102 §2 puts them in —
(g) first, (e) fifth — and this is the reason for that order rather than a coincidence of it.

### 1.5 Two limits of the predicate, disclosed rather than discovered later

- **Padding detection is by leading zero, and that is exact only while every allocated number is
  below `10 ** (PAD_WIDTH - 1)`.** At `PAD_WIDTH = 5` an id numbered 12 400 is written `PL-12400`
  padded and `PL-12400` unpadded — indistinguishable. The corpus's numbers are far below that
  today. **This is not the same trigger as §1.8's widening trigger** (`INDEX.md` passes 90 000),
  so the gap is real and named: the check must be revisited at 10 000, not at 90 000.
- **A specimen number can collide with a real id later.** If `PL-1240` is ever allocated, the
  standard's own rule-3 example becomes a conjunct-3 violation. **The resolution is to the
  specimen, not to the check**: the standard already writes `ADR-<nnnnn>` placeholders elsewhere.
  Which specimens and how is §1.7's open question, not this ruling's to settle.

### 1.6 This reading has an existing implementation to displace, and it is `audit-docs.py` check 32

**A padding rule already exists in the shipped tooling and it is conjuncts 1 and 2 with no
conjunct 3.** `citation_problems_in_file` (`scripts/audit-docs.py:1531-1563`) emits, for each
`_docid.ID_RE` match outside a markdown link target, two independent problems: the id *"does not
resolve in docs/INDEX.md"*, and — separately and **unconditionally** —

```
f"{lineno}: padded id `{m.group(0)}` outside a link target — "
"citations write the integer, never padding (NT-0019 §1.1 rule 2)"
```

**Its authors knew this reds the defining document, and deferred rather than resolved it.** The
whole of check 32 is gated on `docs/INDEX.md` existing, and the docstring says why in terms
(`:1588-1595`): *"`document-ids.md`'s own illustrative prose (the padding-equivalence example in
its lift of NT-0019 §1.1 rule 3 … ) uses ids, some deliberately padded, to teach the grammar
rather than to cite or name a real file. Running the padding rule against that prose
unconditionally would red the standard's own reference text for demonstrating the equivalence it
defines."* The gate is dated to *"W37-6"* — this Work.

**So the two readings §7(e) produced were not a measurement dispute; they were this deferral
arriving.** The disposition follows directly: **check 32's padding branch takes conjunct 3** —
padded, outside a link target, **and resolving in `docs/INDEX.md`**. `link target` is already
that branch's form of conjunct 2 and is kept as it stands. **The gate on `docs/INDEX.md` stays**,
because the resolution branch genuinely needs the index; what changes is that the padding branch
stops being the reason the gate cannot be lifted.

### 1.7 The specimen problem is broader than padding, and it is not (e)'s — recorded open, not decided

**Conjunct 3 fixes check 32's padding branch and does nothing for its resolution branch.** Once
`docs/INDEX.md` exists, `document-ids.md`'s rule-3 sentence still reds three times as *"PL-1240
does not resolve in docs/INDEX.md"* — a specimen read as a dangling citation. That branch cannot
take conjunct 3, because conjunct 3 *is* resolution: gating the dangling-citation check on the
citation resolving would delete the check.

**This is a genuinely open design choice and `CLAUDE.md` §10 forbids picking one silently, so it
is recorded rather than ruled.** The options, with the trade-off that decides between them:

| option | what it costs |
|---|---|
| The standard's literal specimens become placeholders (`PL-<nnnnn>`), as its ADR examples already are | edits the maintainer's own reference text — the distortion checks 19 and 28 already did twice (§1.3) |
| A reserved number band that `doc-id.py next` never allocates, so specimens resolve to nothing forever | a standard change, and a band is a magic constant that has to be remembered |
| A reviewed per-file exemption in `_SPECIFICATIONS_OF_THE_OLD_PATH`'s ratified shape, for the resolution branch only | the blocklist §1.3 argues against, though here scoped to one branch and one list |

**Filed as `OQ-OVR-18`** in `docs/open-questions.md`, mirrored into `docs/specs/00-overview.md`
§10 and placed on `docs/roadmap.md` §10's Deferred gate row, in the commit that adds this
paragraph. Recommendation **(c)** — the reviewed per-file exemption, scoped to the resolution
branch alone. **It must not be folded into §7(e):** an (e) row that also carried this would be
reporting a resolution-branch defect as a padding failure, the same conflation §1.4 keeps out
between (d) and (e).

**Recorded because a wrong step was taken here and the record should carry it.** This role first
argued the question did *not* belong in `docs/open-questions.md`, on the ground that all eight of
that file's sections are scoped to a product spec module and this question has none. **That
ground was false.** `OQ-OVR-17` (`docs/open-questions.md:46`, mirrored at
`docs/specs/00-overview.md:554`) is a question purely about `audit-docs.py` checks 14 and 21,
filed under `OVR`; `OQ-OVR-9` was the same shape and was closed into an `audit-docs.py` check
plus `FR-OVR-19`. **The file already carries audit-tooling questions, and the premise was
produced by not reading it.** The findings register was the proposed alternative and is
structurally incapable of holding this: its columns are `Finding id`, `Concerns`, `Work item`,
`Phase`, `Decision`, with no cell for options or a recommendation, and `register-lint.py`'s
vocabulary is dispositions of an established defect rather than a choice among designs. **F68,
F96 and F71 are all defects established by measurement with a right answer; this is not one.**

**A second wrong step, caught by an assertion rather than by care.** The Deferred gate row's
count cell was reported to the lead as reading `13 (0 open)` against a row naming 32 distinct
ids — an apparent defect. It was not: `13 (0 open)` is the *"Before Phase 4"* row, read off a
hardcoded line number instead of the row being counted. **The Deferred cell reads `32 (0 open)`
and was correct.** The recount that found 32 independently is what the cell already said, so it
becomes `33 (1 open)` by recount and not by increment.

**Why it is not a findings-register row, recorded so the next reader does not "fix" it by moving
it.** Filing it in `docs/audit/register.md` was proposed and is refused on two grounds, both read
directly. **The register's columns are `Finding id`, `Concerns`, `Work item`, `Phase`,
`Decision`** — there is no cell for options, trade-offs or a recommendation, and `CLAUDE.md` §10
requires all three of an open design choice; filing it there means deleting the part §10
mandates. **And its `Decision` vocabulary is dispositions of an established defect** — `fix
before close`, `accept`, `carry forward`, `split verdict` — none of which can express *"here are
three designs, I recommend the third."* Its own header says what it is for: *"One row per **open
finding** … Each row names the work item that carried it, the phase, and the decision."* **F68,
F96, F100 and F71 are all defects established by measurement, each with a right answer. This has
none yet**, which is exactly why it was recorded open rather than ruled — and the discriminator
between the two files is that, not the subject matter.

**One thing left unplaced, deliberately.** `OQ-OVR-17` sits on **no** `docs/roadmap.md` §10 gate
row — the omission `.claude/skills/spec-change` warns about (*"A new `OQ-` also goes into
`docs/roadmap.md` §10's decision-gate table, in the same commit"*) and which `audit-docs.py` does
not check. It is raised with the lead rather than fixed here: placing another raiser's question
on a gate is a planning act, not a correction.

### 1.8 Acceptance — the violation that must become detectable

*Violation: a padded id that resolves through `docs/INDEX.md` to a real governed thing, sitting
outside a filesystem path, passing §7(e).* **The broken-input proof:** take any real id the
index lists, write it padded into a body line of `docs/process/document-ids.md` — the defining
document, deliberately, because that is where a document-keyed exemption would hide it — and
require `--verify`'s (e) row to go **red**, naming that file and line. It must be red *there*,
not merely red somewhere.

*Violation: §7(e) implemented with an exemption keyed on a file path, a document name, or a
directory* — the blocklist §1.3 refuses.

*Violation: §7(e) recorded as passing on a measurement that applied conjuncts 1 and 2 only.*

*Violation: the (e) row and `audit-docs.py` check 32's padding branch computing the same rule
without the instrument comparing them.* **Two implementations of one rule that are never compared
are two rules** — `executor-verify`'s point, adopted here: `--verify` computes both and requires
agreement, rather than sharing a predicate by intention.

*Violation: `audit-docs.py` check 32's padding branch (`scripts/audit-docs.py:1560-1563`) still
firing unconditionally once `docs/INDEX.md` exists.* Two predicates for one rule is how the two
readings arose; the (e) row in `--verify` and check 32's padding branch **compute the same thing
or one of them is wrong**. The proof is §1.3's `doc-id.py:2757` line: both must name it.

---

## 2. §7(f) — "`git grep -c 'VR-DST-1'` is unchanged from `8f5d57d` — no product identifier moved"

### 2.1 The sentence contains both halves, so this is a reading, not a choice against the text

The clause names an instrument (*"`git grep -c 'VR-DST-1'` is unchanged from `8f5d57d`"*) and,
after the em dash, the property the instrument stands for (*"no product identifier moved"*).
**They are one sentence, and the second half is the first half's meaning.** The question is
which tree "unchanged" compares against, and §7's own words answer it three times over.

**First, §7's preamble scopes the whole acceptance to one tree:** *"At the migration PR's merge
tree: (a) … (f) …"*. Every other row in §7 is computed at that single tree. A row that instead
compares that tree against `8f5d57d` is comparing across **every commit anyone made in
between** — which is not a property of the migration and cannot be an acceptance criterion for
it.

**Second, §1.1 rule 4 states the obligation and states whose it is:** a product identifier is
*"product data governed by `docs/specs/`, and which **this standard never touches**."* The duty
is on the standard and its migration. It is not a duty on the repository to stop mentioning
`VR-DST-1` in new documents.

**Third, Ruling 102 §1 makes the instrument run *"the migration on a disposable snapshot"*.**
The before/after pair on that snapshot is the only comparison the instrument has; a literal
`8f5d57d` comparison would require the script to reach outside its own snapshot to a tree that
has no relation to the run.

### 2.2 The ruling

**§7(f) is measured across the migration, on the snapshot: the count before applying the
migration and the count after must be equal.** `8f5d57d` is read as the tree at which NT-0019
was written and at which the baseline was taken — the note's own header says every count in it
was measured there — **not as a fixed comparand that later commits are answerable to**.

**And because the sentence's stated property is "no product identifier *moved*", the predicate
carries a second conjunct that makes "moved" testable:**

| # | conjunct | what it establishes |
|---|---|---|
| 1 | the **total** `git grep -c 'VR-DST-1'` sum is equal before and after the migration on the snapshot | the sentence's own instrument |
| 2 | the **per-source** count is equal before and after — each pre-migration path mapped to **all** the paths its content went to, summed, with a split source's target set taken from §3.3's routing table and not from `REDIRECTS.csv` alone | the sentence's own stated property |

**Amended 2026-09-03 after measurement (§5.2).** This conjunct was first stated as a *per-file*
comparison through `REDIRECTS.csv`. **That is wrong and would have shipped three false positives
on this corpus**: `REDIRECTS.csv` as generated is **one-to-one**, and a split source's content
goes to several files, so the mapping cannot express the answer even though the arithmetic
closes.

**Conjunct 2 is this role's strengthening and is declared as such.** Conjunct 1 alone cannot
fail on a move: deleting one occurrence and creating another elsewhere leaves the total
unchanged. **A row that cannot fail on the thing it names is precisely what Ruling 102 §1 exists
to remove** — *"a row that cannot be expressed as a predicate the script computes is a row that
was never enforceable."* `REDIRECTS.csv` is generated by the migration (§1.4) and is present on
the snapshot after the run, so conjunct 2 is computable where conjunct 1 is.

**Scope note:** conjunct 2 is `VR-DST-1` only, because that is the identifier §7(f)'s sentence
names. §1.1 rule 4's wider class — *"artifact ids, job kinds"* — is not silently folded in here;
widening the row to the class is a §7 amendment and is the maintainer's.

### 2.3 The evidence that the literal reading fails for reasons unconnected to the migration

Run in this session's own worktree at `e97b97a`:

```
git grep -c 'VR-DST-1' 8f5d57d | awk -F: '{s+=$NF; n++} END {print n, s}'   → 25 files, 104
git grep -c 'VR-DST-1'          | awk -F: '{s+=$NF; n++} END {print n, s}'  → 35 files, 129
diff <(git grep -c 'VR-DST-1' 8f5d57d | sed 's/^8f5d57d://' | sort) \
     <(git grep -c 'VR-DST-1' | sort)
```

**The diff is additions only — no changed line, no deletion.** Every one of the 25 files present
at `8f5d57d` still carries the identical count. The entire delta is **ten new files, and every
one of them is a document about NT-0019 itself**: `docs/notes/0019-one-id-per-document.md`,
`docs/process/document-ids.md`, the map plan, the two migration-run leaf plans, the outstanding-
obligations record, the go-ahead ask, the W37-5b slice decision, the time-boxed delegation and
the second-fail handover.

**So the literal reading is failed by the migration's own paperwork.** Nothing moved; documents
that *discuss* the identifier were written. Note also that the count is now **129**, not the
**127** relayed at `0de529e` — the literal comparand drifts with every ordinary commit, which is
what a repository-history comparison is, and what an acceptance row cannot be.

**This evidence is corroboration, not the ground.** The ground is §2.1's three clauses, all of
which were written into §7 and §1.1 before any of this was counted.

### 2.4 What this reading makes the row

**§7(f) PASSES on conjunct 1 and is UNMEASURED on conjunct 2 — so the row is not yet green.**
**Superseded by §5.2, 2026-09-03: both conjuncts are now measured and the row is green**, once conjunct 2 is stated so it can express a one-to-many split. Kept as written because the sequence — strengthened, then measured, then the strengthening found a defect in its own wording — is the part worth reading.

Conjunct 1 was measured at `127 → 127` across the migration (**relayed**; §4.2). Conjunct 2 has
never been run. The row goes green when both do, on the same snapshot, in the instrument.

**On the accusation this reading invites, answered directly.** This reading produces the passing
number and the rejected one produces the failing number, which is exactly the shape Ruling 102 §2
warns against. **The grounds are independent of that**: §7's own "At the migration PR's merge
tree" preamble, §1.1 rule 4's "this standard never touches", and Ruling 102 §1's disposable
snapshot. **And the reading is not costless to the row** — conjunct 2 makes §7(f) strictly harder
to pass than the literal clause ever made it, since the literal clause could be satisfied by a
migration that moved every occurrence of `VR-DST-1` into different files. A reading chosen for
convenience does not add a conjunct that can fail.

### 2.5 Acceptance — the violation that must become detectable

*Violation: a migration that relocates an occurrence of `VR-DST-1` from one document into
another while leaving the total count equal, passing §7(f).* **The broken-input proof:** on the
snapshot, before the after-count is taken, move one `VR-DST-1` occurrence from one migrated file
into another, and require the (f) row to go **red on conjunct 2** while conjunct 1 stays green.
A proof that reds conjunct 1 as well has not exercised conjunct 2 and is not the proof.

*Violation: §7(f) computed against any tree other than the snapshot's own pre-migration state* —
including a hard-coded `8f5d57d`.

*Violation: §7(f) recorded as passing with conjunct 2 unimplemented.*

---

## 3. Ruling 102 §6 — the routing rule, made computable

### 3.1 The rule as ruled, verbatim, and not reopened

> **"The index section lives in the INDEX of the family §5.2 routes the source to —
> `closure-records.md` → `docs/closures/INDEX.md` — and lists every target with its path,
> including those in other families. One link, derivable from the route, no invention."**

### 3.2 The three split-across-family sources, derived rather than accepted

**The brief this role received said all three are the `_discover_plain_plans` /
`_discover_lettered_rulings` pattern. That is wrong, and the correction matters** — Ruling 102
§6's own worked example, `closure-records.md`, is one of the two the brief's description does not
cover.

Derived by instrumenting `scripts/doc-id.py`'s discovery functions directly, grouping every
emitted draft by its `was:` source and reporting the set of prefixes per source (the probe is not
committed; it imports each `_discover_*` and tallies `(was, prefix)`). **Re-derived at this
branch's rebased tip over `main` at `74c53ef`**, not carried forward from the first run:

| # | source | prefixes emitted | discovery functions | §5.2's route | routed INDEX |
|---|---|---|---|---|---|
| 1 | `docs/audit/closure-records.md` | `CR`×9, `LG`×10, `RS`×2 | `_discover_closure_records` | *"split into `CR-` files (`work`, `review`); preambles → `closures/README.md`"* | `docs/closures/INDEX.md` |
| 2 | `docs/audit/plan-reviews.md` | `CR`×12, `RFC`×2 | `_discover_plan_reviews`, which returns `_discover_proposal_containers`' drafts alongside its own | *"split into `CR-` files (`work`, `review`)"* — same §5.2 row | `docs/closures/INDEX.md` |
| 3 | `docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md` | `PL`×1, `RL`×3 | `_discover_plain_plans` **and** `_discover_lettered_rulings` | the `plans/2026-*.md` row: *"the rest → `plans/`"* | `docs/plans/INDEX.md` |

**Only source 3 is the pattern the brief described**, and even there the mechanism is
`_discover_lettered_rulings`' `### Ruling A<n>` headings, not `## Ruling N` — a file carrying
`## Ruling N` is skipped by `_discover_plain_plans` (`scripts/doc-id.py:2013-2015`) and emits
`RL-` only, which is one family and not a cross-family split at all. **The same misdescription is
in the shipped code:** `_split_index_family`'s docstring on `origin/w37-6-split-source-resolver`
says *"`_discover_lettered_rulings` emits an `RL-` draft for each `## Ruling N` heading"* and
*"becomes one `PL-` and two `RL-`"*. It is three `RL-`. Correcting that docstring is part of
implementing this ruling.

**The per-source counts are tree-dependent; the routing is not.** `plan-reviews.md` read
`CR`×11 when this record was first drafted at `e97b97a` and reads `CR`×12 here, because
**#687** (`74c53ef`, *"Plan review 12"*) added one `###` review heading to that file between the
two runs. **Nothing about the routing moved, and nothing could**: §5.2 routes the *source*, so a
source gains and loses targets without ever changing which index carries its section. That is the
property §3.3's rule is chosen for, and it is why the table's counts are given with the tree they
were taken at rather than as constants.

**Sources 1 and 2 route to the same index**, because §5.2 gives them one row between them. That
is the routing table's answer and it is accepted as such: two anchors, one index file.

**The 25 same-family split sources** — every `docs/plans/2026-*-rulings.md` file, `RL-`-only —
are untouched by §6 and keep resolving to `docs/rulings/INDEX.md` under Ruling 101 clause 1
unamended.

### 3.3 The routing rule, stated for implementation

**The family directory carrying a split source's index section is a property of the source,
declared once from `docs/notes/0019-one-id-per-document.md` §5.2, and is never computed from the
source's own targets.** Concretely, replacing `_split_index_family`
(`origin/w37-6-split-source-resolver:scripts/doc-id.py:5054-5081`):

1. **A named constant maps each split source's path to its §5.2 family directory** — the three
   rows of §3.2's table, each carrying the §5.2 row it was derived from as a comment. This is the
   *"derivable from the route, no invention"* half of §6.
2. **A source that splits and has no entry in that constant raises**, naming the source and its
   target families. **It does not fall back to sort order, or to anything else.** Silence is the
   failure mode being removed; a new split source must be routed by a human reading §5.2, which
   is a one-line edit and a deliberate act.
3. **The section's contents are unchanged** — every target, from every family, with its path.
   §6's *"lists every target with its path, including those in other families"* is what
   `_write_split_source_indexes` already does, and Ruling 101's grounds (*"not choosing a target
   — it is the REDIRECTS row made navigable"*) survive intact: the section still names no target
   as the meant one, and now names no family as the meant one either.

### 3.4 The trap this rule must not be allowed to hide behind

**On this corpus the new rule and the old one produce the identical answer, for all three
sources.** `_split_index_family` returns `sorted({rel.split("/")[1] for rel in new_rels})[0]`:
`{closures, ledgers, research}` → `closures`; `{closures, rfcs}` → `closures`;
`{plans, rulings}` → `plans`. **Every one coincides with §5.2's route.**

**So a test that asserts the three current placements passes under the sort-order rule and under
the routed rule alike, and proves nothing.** This is why Ruling 102 §6 says the executor's
sorted-first placement *"was the right conservative call"* — it was right, and it was right by
coincidence, and a coincidence is not a rule.

**Name the shape, not just this instance: this is a positive control that passes because of what
it cannot distinguish.** A control built from the population the rule already fits reports the
rule's *fit*, never its *content* — the same failure as a gate proved with a pattern other than
the one it fires on, or with a case easy enough that any pattern would pass. The three real
sources are exactly such a population: **every one of them is a case on which the old rule and the
new rule agree**, so they can only ever return green. **A rule change whose entire evidence is
that the output did not change has not been tested at all.** The acceptance test in §3.5 is
therefore built from a case where the two rules **disagree**, and it is the only kind of case that
can carry the pass.

### 3.5 Acceptance — the violation that must become detectable

Ruling 102 names it: *"an index section placed by sort order rather than by §5.2's route, once
§6 is implemented."* **The broken-input proof, shaped so §3.4's coincidence cannot satisfy it:**

*Violation: a split source whose §5.2 route is **not** its sorted-first target family, placed at
its sorted-first family.* Construct it as a fixture — a source routed by its table entry to
`rulings/` that splits into `{plans, rulings}`, so sort order says `plans` and the route says
`rulings` — and require the placement to be `docs/rulings/INDEX.md`. **A proof built only from
the three real sources is not the proof**, because all three coincide.

*Violation: a cross-family split source with no entry in the routing constant, placed anywhere at
all rather than raising.* Add a fourth fixture source that splits across families and is absent
from the constant, and require `migrate` to raise, naming it.

*Violation: `_split_index_family`, or any successor, deriving the family from `new_rels`.* The
function's replacement takes the source path and the routing constant; if it can still see the
target list it can still sort it.

**The fixture, specified to the point where implementing it needs no judgement.** Assigned to
this role by the lead and **declined as outside its charter** (§5.4); the specification is
delivered here instead, which is the part that is this role's.

**Fixture A — route and sort order disagree, and the route must win.**

| | |
|---|---|
| source | one synthetic file under the fixture corpus, cross-family by construction |
| its targets | at least one in `docs/plans/` and at least one in `docs/rulings/` |
| sort order says | `plans` — `sorted({"plans", "rulings"})[0]` |
| its routing-table entry says | `rulings` |
| **assert** | the index rel is **`docs/rulings/INDEX.md`**, and the anchor is `#<old-basename>` |

**Red-then-green is the acceptance, and both halves must be exercised:** the assertion **fails**
against `_split_index_family`'s current body (`sorted({rel.split("/")[1] for rel in new_rels})[0]`,
which returns `plans`) and **passes** against the routed implementation. **A fixture that passes
under both is not this fixture** — that is §3.4's whole point, and it is the failure the three
real sources would produce, since all three coincide.

**Fixture B — a cross-family source with no routing entry must raise.** Same shape, no
routing-table entry, and `migrate` **raises**, naming the source and its target families. **Not
"falls back", not "warns"** — §3.3 clause 2 exists because silence is the failure mode being
removed, and a fallback of any kind restores it.

**Two constraints on how A is built, because the obvious construction defeats it.** The target
families must be **`{plans, rulings}` or another pair whose sorted-first element is not the
routed one** — a pair like `{closures, ledgers}` routed to `closures` reproduces the coincidence
and tests nothing. And the routing entry must come from **the same constant the production path
reads**, not a parameter the test passes in: a test that injects a route through a seam
production does not use proves the seam, not the rule.

**Sibling regression, cheap and worth having:** the three real sources keep their current
placements — `closure-records.md` and `plan-reviews.md` to `docs/closures/INDEX.md`,
`2026-08-30-nt-0012-0013-0014-adoption.md` to `docs/plans/INDEX.md`. **That test proves nothing
on its own** (§3.4) and is a guard against a routing table typo, not evidence for the rule. It
must not be presented as the acceptance test.

---

## 4. Row verdicts, and what this record does not establish

### 4.1 Verdicts under the ruled predicates

| row | reading | verdict as currently measured |
|---|---|---|
| **(e)** | a padded id in (d)'s corpus, outside a fence and outside a path, `PAD_WIDTH` digits, resolving through `docs/INDEX.md` | **FAIL** (§5.1) — population **1** after conjuncts 0–3, down from a disputed 36-or-77 |
| **(f)** | count equal across the migration on the snapshot, per-source over all a split's targets | **PASS** (§5.2) — 129 → 129, and the one apparent per-file disagreement sums 5+2+1=8 across a split source |
| **§6** | route from §5.2, declared per source, raise when absent | **UNIMPLEMENTED** — the sorted-first placement stands, and coincides |

**Neither (e) nor (f) is recorded here with two readings.** Each has one, and each is stated as a
predicate the instrument can compute.

**A fourth thing this record establishes, which was not asked for and is the most useful of the
four:** §7(e)'s two readings were not a disagreement about a number. They are `audit-docs.py`
check 32's deferral arriving on schedule — the check already implements conjuncts 1 and 2, its
docstring already says that reds the standard's own reference text, and it is gated off until
*"W37-6"* for exactly that reason (§1.6). **The row was reported twice because the question had
been recorded as deferred and then re-encountered as new.**

### 4.2 What is relayed, and what this session could not reproduce

Under Ruling 102 §7's rule, applied to this role's own figures:

- **(e)'s figures are relayed from two parties and they disagree** — the handover's `2021`/`36`
  at `0de529e` on a migrated snapshot, and the auditor's `2042`/`77` on a path filter of its own.
  **§1.4 reads that disagreement rather than picking between the numbers**; neither is adopted
  here, and this session ran neither.
  **Neither was reproduced, and no attempt was made to make this session's numbers agree with
  them.** On the unmigrated tree at `e97b97a` the population is **575 occurrences over 553 lines**
  raw, falling to **480 occurrences over 463 lines** under a path filter. **That is a different
  corpus, not a contradiction**: §7's preamble measures (e) post-migration, where every governed
  document has acquired a padded filename, and pre-migration the padded canonical form barely
  exists. **The relayed pair carries neither its command nor its filter**, so under `CLAUDE.md`
  §13's predicate clause it is not reproducible as written by anyone — which is itself the reason
  §1.2 states the row as a predicate rather than arguing about the number.
- **(f)'s `127 → 127` across the migration is relayed.** This session's own runs are `104` at
  `8f5d57d` and `129` at `e97b97a`, plus the file-by-file diff of §2.3.

  **In one line: `git grep -c 'VR-DST-1' <ref> | awk -F: '{s+=$NF} END {print s}'` gives 104 at
  `8f5d57d`, 127 at `0de529e` and 129 at `e97b97a` — one command, three trees, and that drift
  *is* §2.3's argument, not a discrepancy to reconcile.** Stated here before the table because a
  reader who meets two of the three numbers stops to reconcile them and never reaches the
  explanation.

  | tree | sum | who ran it |
  |---|---|---|
  | `8f5d57d` | 104 | this session |
  | `0de529e` | 127 | the auditor (**relayed**) |
  | `e97b97a` | 129 | this session |

  **There is no discrepancy here; there is a monotone drift, and the drift is §2.3's whole
  argument.** Four ordinary commits separate `0de529e` from `e97b97a` and the figure moved by two.
  A row whose comparand moves whenever anyone writes a document about the migration is not
  measuring the migration — which is why §2.2 reads it as a before/after on the snapshot instead.
- **The §3.2 table is this session's own**, from its own instrumentation of `doc-id.py`'s
  `_discover_*` functions at `e97b97a`. Nothing in it is relayed.
- **`doc-id.py migrate --verify` does not exist at `e97b97a`, and that is why the two figures
  above are still relayed rather than reproduced.** At `e97b97a` `migrate` takes `--repo-root`
  and nothing else; there are four subcommands (`next`, `check`, `widen`, `migrate`) and no
  dry-run mode, so **there was no read-only way to obtain a migrated snapshot** and (e)'s
  post-migration population could not be measured by anyone not running the migration.

  **This has changed since, and the record says so rather than reading as though it had not.**
  `executor-verify` is building the instrument on branch `w37-6-verify-instrument` as
  `migrate --verify <dir> --ref HEAD --keep` (**relayed** — the lead's confirmation of the
  process; not run by this session, which does not run `migrate`). **The two relayed figures are
  therefore reproducible now and should stop being relayed**: this session has asked
  `executor-verify` for conjunct 1 and 2 on its snapshot for (f), and for the (e) population
  classified per-file by conjunct 3, **with an explicit instruction not to fit the result to
  `2021`.** Until those come back the marks stand. **A figure neither party has run does not
  become this record's by being quoted in it.**
- **No padded-in-prose predicate exists in the shipped tooling.** Every id regex is
  padding-agnostic by design (`scripts/_docid.py:43`, `ID_RE`, `-0*(\d+)`), because it is a
  *resolver*. **§7(e) has had no implementing code at any point**, which is the plainest possible
  statement of why it produced two readings.

### 4.3 Three corrections owed back to the brief

1. **The three cross-family sources are not all the plain-plan/lettered-ruling pattern** — §3.2.
   Two of the three are `closure-records.md` and `plan-reviews.md`, and the first is Ruling 102
   §6's own worked example.
2. **The checks 19 / 28 / notes-citation precedent is a working note, not a repository ruling,
   and it did not rule what it was said to rule** — §1.3. Two of its three instances resolved by
   changing the document.
3. **`_MIGRATION_DIFF_FAMILY_INDEXES` resolves, but not where a reader would look.** It is
   **absent from `main` at `e97b97a`** — the only occurrence of the string in the working tree is
   the handover's own prose at `docs/plans/2026-09-03-w37-6-second-fail-handover.md:325`. It is
   defined at `origin/w37-6-split-source-resolver:scripts/doc-id.py:5653`, on the unmerged
   executor branch, and its comment carries exactly the "flagged rather than made silently"
   reasoning the handover attributes to it. **A citation to an unmerged branch's symbol that
   names no branch does not resolve for a reader holding none of the writer's context**
   (`CLAUDE.md` §13, [`NT-0004`](../notes/0004-a-reference-that-resolves-only-for-the-writer.md));
   this record cites it with its ref. It is a citation defect, not a substance defect — the
   constant is real and does what the handover says.

## Acceptance Standard

**This record is accepted when the lead merges it.** Its substance binds from that point.

**It is discharged when a merged PR against `scripts/doc-id.py` implements all three:** the (e)
row with its three conjuncts and §1.8's broken-input proof; the (f) row with both conjuncts and
§2.5's broken-input proof; and `_split_index_family`'s replacement with §3.5's two fixture
proofs. **Until such a PR is merged and named here, this ruling has changed no behaviour.**

**It is falsified — and must be reopened rather than worked around — if** any of the three
predicates proves uncomputable inside `doc-id.py migrate --verify` as Ruling 102 §1 shapes it.
A predicate that cannot be computed is a reading that failed, and Ruling 102 §1 says so:
*"a row that cannot be expressed as a predicate the script computes is a row that was never
enforceable."*

**Owed and not decided here:** §1.5's specimen-collision resolution, which is a
`docs/process/document-ids.md` edit; and any widening of §7(f) beyond `VR-DST-1` to §1.1 rule 4's
full product-identifier class, which is a §7 amendment and the maintainer's.

---

## 5. Amended on measurement, 2026-09-03 — what the snapshot changed

**Both rows have now been measured under the ruled predicates**, by `executor-verify` on the
snapshot pair built by `doc-id.py migrate --verify /tmp/verify-final --ref HEAD` at `e97b97a`
(PR **#689**, branch `w37-6-verify-instrument`), `migrated/` and `control/` being byte-identical
extractions of one archive with `migrate()` run on the first only. **These figures are
`executor-verify`'s, not this session's** — this role does not run `migrate` — but they are
*measurements under this ruling's own predicates* rather than relayed counts, and they are
reported here with the predicate each was taken with.

**§4.2's relayed marks stand for the handover's `2021`/`36` and the auditor's `2042`/`77`.
Nothing below reconciles to either, and no attempt was made to.**

### 5.1 §7(e) — three defects in the predicate as first ruled, and the row's real population

| step | occurrences |
|---|---|
| (a) padded-form tokens, `-0[0-9]{3,4}` | **2387** |
| (a′) the same with `-0\d{4}` — exactly `PAD_WIDTH` | **2032** |
| (b) minus path/filename context | **37**, in 14 files |
| (c) of (b), resolving in the generated `docs/INDEX.md` (561 distinct ids) | **6**, in 2 files |

**Defect 1 — the digit count was unpinned, and it is worth 355 occurrences.** `{3,4}` and
`\d{4}` differ by **355** on the same tree. That is F85's shape inside this ruling's own
predicate: two counts over one corpus differing only by the pattern. **Conjunct 1 now names
`_docid.PAD_WIDTH` by symbol** rather than a literal digit count, per `CLAUDE.md` §13's rule that
a shipped constant is cited by symbol and never pasted.

**Defect 2 — conjunct 2 was defeated by markdown emphasis, and this accounts for 2 of the 6.**
Two of (c)'s survivors are `docs/rulings/**RL-00993**-q5-….md` — **a path**, in which the bold
markers split the token so the path test failed to see it. The occurrence is inside a filename and
conjunct 2 was written to clear exactly that. **Conjunct 2 now strips markdown emphasis before
testing path context**, and those two are the broken-input proof for it.

**Defect 3 — (e) and (d) disagreed about the corpus, and this accounts for 3 of the 6.** Three
survivors are `old_id` column values in `docs/REDIRECTS.csv`. **§7(d) excludes `REDIRECTS.csv`
and `was:` lines by name**, so an (e) that counts them makes the two rows measure different
corpora and reports the redirect map's own job as a violation. **Conjunct 0 adopts (d)'s
exclusion**, and adds fenced code blocks, which `audit-docs.py` check 32 **already skips**
(`_FENCE_LINE_RE`, `:1541-1545`).

**Why the fence clause matters, and why it is not a document-keyed exemption.** The one remaining
survivor is a line correcting a relayed pair, *"The pair was relayed as `RL-196` / `RL-00199`"* —
a padded id quoted **as the defective form being corrected**. Without a fence rule, a record that
documents a padding defect must corrupt its own evidence to pass the lint, which is the check-19
distortion (§1.3) arriving by a new route. **The fence is the remedy and it already exists**: a
record exhibiting a defective form fences it, the evidence survives byte-exact, and no exemption
is keyed to any document. **A padded id outside a fence is still a violation in every document,
including this one.**

**Verdict: §7(e) FAILS, and the failure is now one line rather than a disputed population.**
After conjuncts 0–3 the population is **1** — the quoted-correction line above, which the fence
rule disposes of by a body edit to that record. **The row goes green when that edit lands, not
before**, and §1.4's FAIL stands as recorded rather than being retroactively softened.

**The (b)-not-(c) remainder is 31 occurrences in 14 files** — `tests/test_template_headers.py` 9,
`tests/test_doc_id.py` 4, `tests/test_doc_id_migrate.py` 4, `scripts/audit-docs.py` 2, the rest
fixtures. **Every one is a specimen and conjunct 3 clears every one.** That is the ruling doing
the work it was written to do, measured rather than asserted.

### 5.2 §7(f) — conjunct 2 is implementable, and stating it against `REDIRECTS.csv` was wrong

**Conjunct 1: `129 → 129`, equal.** The file count is **not** equal — 35 → 37 — which conjunct 1
cannot see, and which is precisely the case conjunct 2 exists for.

**Conjunct 2, run as first ruled, reported 3 disagreements — and all three are one artefact of my
own wording, not a moved identifier:**

```
8 → 5   docs/ledgers/LG-00030-w5-wf-01-driven-end-to-end.md
0 → 2   docs/closures/CR-00019-w6a-frontend-data-workbench-closed.md
0 → 1   docs/closures/CR-00119-w6b-the-frontend-of-phase-1b-closed.md
```

**The control file is `docs/audit/closure-records.md` — §3.2's split source 1.** It held all 8;
its content went to three files; **5 + 2 + 1 = 8 and the sum closes exactly.** `REDIRECTS.csv`
maps it one-to-one to a single target, so **the mapping cannot express a split even though the
property holds.** Conjunct 2 is therefore amended to sum over **all** the targets a source routes
to, taking the target set from §3.3's routing table — the same table §6 already requires for a
different reason, which is a second use for it and an argument for building it once.

**Verdict: §7(f) PASSES on both conjuncts**, once conjunct 2 is stated so it can express a
one-to-many split. §2.4 recorded it as *"conjunct 1 passes, conjunct 2 unmeasured — not green"*;
it is now measured and green. **The reading in §2.2 is unchanged** — measured across the
migration, not against `8f5d57d` — and nothing in this result touches it.

**And the strengthening earned its keep.** Conjunct 1 alone would have passed silently at
`129 → 129` while the file count moved by two. Conjunct 2 is what noticed, and what it noticed
was a defect in **`REDIRECTS.csv`'s expressiveness**, not in the migration's handling of product
identifiers. A conjunct that cannot fail would have found neither.

**Corroboration from a third direction, recorded not resolved:** all three of those files carry
`was: docs/ledgers/LG-00030-….md`, **including `LG-00030` itself, which names its own
post-migration path.** That is Ruling 102 §5's `was:` defect appearing independently in this
measurement, and it is that row's to fix.

### 5.3 What this ruling now owes, and to whom

**To `executor-verify`, so row (e) and row (f) become scored rather than `UNDETERMINED`:** the
conjuncts as §1.2 and §2.2 now state them, including conjunct 0's corpus and the `PAD_WIDTH`
symbol. **Row (e)'s two printed readings collapse to one on this ruling's authority**, which is
what Ruling 102 §2 row 5 asked for.

**Adopted from `executor-verify`, and it is a better idea than the one it improves:** the
instrument should compute **both** the (e) row and `audit-docs.py` check 32's padding branch and
**require them to agree**, rather than merely sharing a predicate by intention. Two implementations
of one rule that are never compared are two rules. **That cross-check is added to §1.8's
violations.**

**Not adopted, and named so it is not assumed:** the §6 fixture whose route and sort order
disagree (§3.5) is unassigned. It is not `executor-verify`'s unless the lead assigns it.


---

## 5.4 One assignment declined, and why it is a finding rather than a refusal

**The lead assigned §3.5's fixture to this role. It is declined as outside this role's charter,
and the substance is delivered above instead.**

`.claude/roles/decision-maker.md` states the boundary twice and sources it to an incident:
**"Never: closes work or phases, implements, or rules audit verdicts"**, and **"No write access
to any code worktree"** — the second recorded because a decision-maker session wrote three times
into an executor's worktree during W10, the third write discarding uncommitted tracked files.
Its `Tools` line is narrower still: *"Read; write to ruling records, the open-questions log, and
`docs/specs/`."* **A test file is none of those.**

**The lead's reasoning for the assignment is sound and is not what is being declined.** *"You
ruled it, so you should build the thing that escapes the trap you identified"* is a good argument
about competence and context. **It is an argument for changing the charter, not for acting
outside it** — and `CLAUDE.md` §15 says exactly what to do with it: *"A role file that proves
insufficient is a finding against the file: fix the file, do not paste a brief back in."* A brief
that widens a role dies with the session; the charter is what the next session reads.

**So this is raised as a finding against `.claude/roles/decision-maker.md`, for the maintainer**,
who owns amendments to what a charter requires (`CLAUDE.md` §12). Two readings are available and
this record does not pick between them: either the charter is right and a ruling's acceptance
test is always an executor's to build from a specification like §3.5's, or the charter is too
narrow and should permit this role to write **tests** — never production code — for rules it
ruled. **The second has a real argument behind it**: the §3.4 trap was found by whoever held the
routing rule in mind, and a specification handed across a role boundary is one more place the
predicate can be narrowed in transit, which is F85's failure mode and this ruling's own subject.

**What is not available is doing it and mentioning it afterwards.** The boundary this charter
draws was written because it was crossed, and a role that crosses its own charter when the
reasoning seems good is not a bounded role.