# Ruling acceptance-item sweep — audit record

| | |
|---|---|
| **Date** | 2026-09-02 |
| **Auditor** | this session, dispatched by the lead to sweep every filed ruling's acceptance item after Ruling 94 routed it |
| **Pin** | `5c0d24df5ce4b58411eb0e67bf7cc2b91a44a3ca` throughout §§1-6 below; one explicit, dated post-sweep note in §3 re-checks a later tip (`2e48960`) and says so |
| **Corrects** | [Ruling 93](../plans/2026-09-02-w37-ruling-88-acceptance-amendment.md) ("twelve ruling records now carry acceptance items") and [Ruling 94](../plans/2026-09-02-w37-vacuous-acceptance-item-ruling.md) ("Fourteen ruling records now carry acceptance items") — both figures were asserted in the paragraph that routed this sweep, not independently derived. §6 states the growth-versus-undercount split per figure. Neither ruling is edited; this record is filed alongside them, findable from a `corrects:`-shaped cross-reference in the same spirit as the `614c92c` correction (`CLAUDE.md` §15). |
| **Why this exists** | `docs/plans/README.md`'s own documented trap — a heading-only sweep misses an addendum filed under a prose heading — and this repo's history of a stale count surviving because "nobody re-derives from a subagent's session" (the lead's words routing this record's filing). Filed so the count is re-runnable rather than trusted. |
| **Scope** | Every ruling heading under `docs/plans/` matching `^#{1,3} Ruling (\d+\|A\d+)( —\|'s)`: 98 rulings (1-95 contiguous, no gaps or duplicates once the one title false-positive is excluded, + A1-A3), across 41 ruling-record files. |

## 1. Method — exact searches, not descriptions

Enumeration (every command below was run against `docs/plans/`, from the repo root):

```
grep -rlE "^#{1,3} Ruling ([0-9]+|A[0-9]+)( —|'s)" docs/plans/
grep -rhoE "^#{1,3} Ruling [0-9]+( —|'s)" docs/plans/ | grep -oE "[0-9]+" | sort -n | uniq -c
grep -rn "^#\+ .*Acceptance.*violation that must become detectable" docs/plans/
grep -rn "violation that must become expressible" docs/plans/ docs/research/
grep -rn "Acceptance test" docs/plans/ docs/research/
grep -rnE "^#{1,4}\s+.*\bRuling\s+[0-9A-Z]+\b" docs/plans/ | grep -vE "^\S+:[0-9]+:#{1,3} Ruling [0-9]+( —|'s)"
grep -n -i "violation\|must fail\|must red\|the check is\|testable definition" <each file with zero hits from the above>
```

The last command's output was read in full for every file it touched — a hit is a candidate,
never a reading (`docs/skills-map.md`-adjacent house rule, applied here to acceptance items
rather than to citations). The standalone-file convention (`## N. Broken-input proof`, Rulings
59-61) and Ruling 44's own phrasing ("Two tests, each stated as a violation that must become
impossible:", no "accept" substring anywhere) were found only by reading full ruling bodies —
no keyword distinguishes either from the other conventions or from ordinary prose.

**"Genuine" acceptance item, defined** — the adjective doing the work in "31 files carry a
genuine item," and the one a challenge would target: an item counts only if it sits inside
that specific ruling's own numbered section (never the file-level `## Acceptance Standard`
check-28 boilerplate, never a citation of a *different* ruling's item, never a governance
sign-off table) **and** states or names a violation/failure condition tied to that ruling's own
substance. It does not count merely because code elsewhere happens to satisfy it — an item is
only as genuine as the ruling's own stated check, not as the ruling's own subject matter.
Rulings 52 and 53 (§2) are the corpus's own worked counterexample: real, enforced code exists
for both, and neither ruling states a check.

**Rule for the next sweep, stated because it will otherwise be re-derived from scratch every
time:** an **"Overridden if `<X>`"** clause is near-universal across this repo's ruling
convention (confirmed present on Rulings 14, 15, 20, 26, 29, 39, 44-53, 55-58, 62-65 — a
formulaic template, not an exception) and **never itself constitutes an acceptance item**. It
states a hypothetical future condition in plain prose and names no check, script, or
procedure. Only a **separately and explicitly labelled acceptance sentence** counts — contrast
Ruling 47, self-titled "The acceptance test, stated as the violation that must become
impossible," against Rulings 55-58, which have an override clause and nothing else. Two of
this sweep's own rows (Rulings 55-58, and independently 52/53) were first mis-admitted on the
looser reading and corrected after a second, dedicated read of their source files.

**A last note on this section's own drafting.** `python3 scripts/audit-docs.py` caught two
defects in this record's own first draft, before it was ever committed: two relative links to
Rulings 93 and 94 missing the `../plans/` prefix required from `docs/audit/`, and an unescaped
literal `|` inside a regex shown in the Scope row's table cell — which had silently shifted
that row's own column count — fixed per `docs/plans/README.md`'s documented `\|`-in-a-table-
cell convention (visible in the Scope row above, as filed). Both are exactly the class of
defect the check exists to catch, caught on the document that documents the check. Recorded
because it is evidence that the gate ran on this artifact, not because it is remarkable.

## 2. The classifier — `scripts/ruling-acceptance-item-census.py`

Implements the enumeration half of this sweep as a re-runnable script, carrying Ruling 83's
property (`docs/plans/2026-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md`): **every
candidate heading falls into exactly one bucket, and the buckets sum to the total.** Run:

```
python3 scripts/ruling-acceptance-item-census.py
```

At this record's pin:

| Bucket | Count | How found |
|---|---|---|
| `w37` | 30 | regex: `### N. Acceptance — the violation that must become detectable` |
| `w11` | 20 | regex: bold `**Acceptance test` inline marker |
| `standalone` | 2 | regex: `## N. Broken-input proof` heading (Rulings 59, 61 — **not** 60, see below) |
| `exception` | 1 | Ruling 44, hand-verified, named because a regex fitted to one sentence would not generalise |
| `prose_only` | 10 | **hand-verified, not regex-derived** — Rulings 40, 42, 43, 45, 46, 47, 50, 51, 54, 60 |
| `none` | 35 | no marker of any kind found |
| **total** | **98** | |

**The honest limit of this tool, stated rather than hidden.** The "three conventions plus
Ruling 44" framing this sweep was asked to commit understates the corpus by ten rulings. Each
of the ten states a genuine, testable check in ordinary prose with **no shared marker** —
"§13's broken-input proof:", "Its acceptance evidence is...", "so this is testable rather than
hortatory," and (Ruling 60, its own sub-case) a re-confirmation of a **different, named**
ruling's broken-input cases rather than a fresh statement of its own. No regex loose enough to
catch all ten avoids also matching ordinary prose that is not an acceptance item — the
`prose_only` set is therefore a committed, hand-verified list, not a derived one, and it is the
one bucket where this module's own promise ("the arithmetic catches an undercount") does not
hold: a future ruling using this same marker-free style lands silently in `none`, not in a
bucket whose count visibly moved. Any addition to `_PROSE_ONLY_RULINGS` must cite the reading
that found it, in the commit that adds it — the same discipline `_NAMED_EXCEPTIONS` already
carries for Ruling 44.

**Not this record's to decide, and not implemented:** whether a *future* ruling must use one of
the three conventions. `docs/_templates/RL.md` is a frozen template edit, `CLAUDE.md` §2 forbids
editing a filed plan to conform, and the choice is the maintainer's. **Recommendation:** require
the W37-series form (`### N. Acceptance — the violation that must become detectable`) going
forward — it is the only one of the three that is both fully regex-derivable *and* already
paired with a structural convention (`### N. Verified first` / `### N. Ruled` / `### N. What it
obliges` preceding it) that gives every ruling a predictable place to state one. This does not
touch the 65 already-filed rulings using another form or none.

## 3. Defective items — full proofs

Five items across five rulings needed more than CONSTRUCTIBLE. The CSV (`ruling-acceptance-
item-sweep-5c0d24d.csv`, same directory) carries the remaining 93.

**Ruling 84 §4 item 2 (VACUOUS AT BIRTH) — REPLACE shape.** Original text: *"A check that no
emitted `LG-` carries a `slice:` whose value resolves to no roadmap row."* `scripts/doc-id.py:946`
(`_stamp_header`): `elif key in ("slice", "deliverable", "lands_in", "trigger"): continue` — an
unconditional skip for every caller, and the function's signature carries no `slice` parameter
at all. No code path in `migrate()` can ever write a `slice:` value onto an emitted `LG-`
record, so the check can never see the fixture it names. Register **F77**. Ruled by Ruling 94
(substitution: count-and-print + a `_stamp_header`-mutation broken-input test) — the item
checked a positive obligation its own ruling imposed and the code never attempted, so it had to
be **replaced**, and was. As of this pin, the substitute is designed but **not yet built**: no
commit had touched `scripts/doc-id.py` or `tests/test_doc_id_migrate.py` for this purpose since
`09b7e9b`.

**Ruling 88 §4 item 2 (INVALIDATED).** Original text named "a fixture whose only level-2
heading is followed by three record headings" in `docs/audit/plan-reviews.md`. Was constructible
when written — Ruling 88 measured "exactly one level-2 heading" at its own pin. PR #609
(`2fbce0c`, confirmed an ancestor of this record's pin) demoted that heading to level-3;
`grep -c '^## ' docs/audit/plan-reviews.md` returns **0** at this pin. The fixture the item names
cannot be built the way it is stated. Rebuilt by Ruling 93 on a property (shared heading level
with no higher level anywhere in the file) rather than a specific level number.

**Ruling 61 (INVALIDATED) — documented, deliberate trade, not a silent accident.** §4
("Broken-input proof") required `check_notes_tombstone()` to red on two named broken-input
cases — a stray file under `.claude/notes/`, and an edited stub body. `grep -c "def
check_notes_tombstone" scripts/audit-docs.py` returns **0**. The module's own docstring
(`scripts/audit-docs.py:55-64`) names the resolution: NT-0019 §5.5 gave slot 30 to its own
header-field check (`check_header_fields`) and resolved the collision by replacing
`check_notes_tombstone` rather than renumbering either — *"`check_notes_tombstone`'s protective
job over the tombstone stubs ends with this commit, by that same resolution, **until W37-6
deletes the stubs entirely**."* The successor, `check_redirects` (slot 36), watches
`docs/REDIRECTS.csv`, not `.claude/notes/`. So: today, neither of Ruling 61's two named
fixtures is caught by anything in the gate — constructible and passing when written,
invalidated by a later, recorded, and bounded resolution (its own stated horizon is W37-6),
not a silent regression.

**Ruling 86 §4 item 3 (INVALIDATED) — confirmed by a later commit, not merely by a later
ruling.** Original text: *"Each of the three new `RL-` records carries an `owner:` that is not
`decision-maker`."* Ruling 95 (`7082c38`/#618, landed during this sweep) reversed the decision
this item encoded, ruling `owner: decision-maker` for the A-series. At this record's pin, the
code had not yet caught up (the departure machinery was "still live... its removal in flight,"
per the go-ahead ask). **Post-sweep, at `2e48960`/#620 (merged after this record's pin, checked
separately and dated here rather than silently folded in):** `_ruling_file_owner`
(`scripts/doc-id.py:1142`) now unconditionally returns `_RULING_DEFAULT_OWNER` for every input
— the departure regexes are deleted, not left inert. Ruling 86 item 3's assertion (`owner ≠
decision-maker`) now fails on *every* input, by construction, exactly as the invalidation
predicted before the fix landed. **This is the strongest form the proof can take: a structural
prediction, made before the code changed, confirmed by an independent later change made for an
unrelated reason (implementing Ruling 95's own obligation, not this record's finding).** A
prediction later confirmed by an independent event is stronger evidence than either the
prediction or the confirmation would be alone.

**Ruling 95 §3 item 3 / §4 item 3 (VACUOUS AT BIRTH) — RE-INSTRUMENT shape, distinct from
Ruling 84's.** §4 item 3: *"Ruling 87's `decision-maker` for the three standalone ruling files
still holds after this amendment."* At this pin: `_discover_plain_plans` uses
`owner=_PLAN_KIND_OWNER[kind]`, and `_PLAN_KIND_OWNER["leaf"] == "planner"` — no code path
anywhere emitted `decision-maker` for those three files (verified: zero hits). This is a
**non-interference claim** — did Ruling 95's own diff disturb territory it deliberately left
alone — whose **property holds** (nothing was disturbed, because nothing implementing Ruling
87 existed yet to disturb) while its **stated instrument has nothing to observe**. Distinct
from Ruling 84's shape: Ruling 84 checked a positive obligation the code never attempted
(replace); this checks a negative one whose target has no positive case yet to falsify against
(re-instrument). **Post-sweep, at `2e48960`/#620:** re-instrumented, not merely noted —
`test_ruling_87_standalone_files_are_untouched_by_this_amendment` now pins the three files
resolving through `_discover_plain_plans` with `owner="planner"` (documented as known-wrong,
not blessed) and `_discover_multi_ruling_files` matching none of them, proven non-vacuous by
two independent mutations (`_PLAN_KIND_OWNER["leaf"]` and `_RULING_HEADING_RE`).

## 4. Withdrawn — a shape neither VACUOUS nor INVALIDATED

Two items fire constantly and return the **wrong verdict** — false positives and false
negatives together — rather than never firing. Folded into CONSTRUCTIBLE in §5's tally (their
replacements are genuine, buildable checks) but named here because the six-class taxonomy this
sweep was asked to use has no slot for "tests, but proves the wrong thing":

- **Ruling 66 acceptance item 2** (original, reversion-based), withdrawn by Ruling 73: measured
  against the shipped `sweep_legacy_forms` on the real corpus, false positives on 8 non-members
  (including `repo-architecture`, `git-hygiene`), false negatives on 4 real members (including
  `subagent-driven-development`, a primary instrument), and no under-inclusion limb at all.
- **Ruling 16 acceptance item 1**, withdrawn via a same-day cross-file correction filed under a
  non-canonical heading in a *different* file — `docs/plans/2026-08-29-w11-algorithm-pin-
  maturity.md:124`, "## Correction to Ruling 16, discharging register row F32" — exactly the
  addendum trap `docs/plans/README.md` §"enumerate the rulings by diffing the record" warns a
  heading-only sweep misses. Register **F32**, confirmed verbatim: *"Only Ruling 16's
  acceptance item 1 is withdrawn; item 2 (the degraded read) stands."*

**Forward pointer, added 2026-09-02 alongside §11.** This section names the shape; §11 is
where it is dated and given a name — the seventh class, `WITHDRAWN`, on the maintainer's
ruling of 2026-09-02. The observation here precedes its own classification there.

## 5. Class counts

Mechanically verified against the CSV (`cut -d, -f3 ruling-acceptance-item-sweep-5c0d24d.csv |
sort | uniq -c`), not hand-totalled:

| Class | Count |
|---|---|
| CONSTRUCTIBLE | 54 |
| NONE_FOUND | 35 |
| INVALIDATED | 3 |
| VACUOUS AT BIRTH | 2 |
| INDICATIVE | 2 |
| CANNOT_DETERMINE | 2 |
| **Total** | **98** |

**INDICATIVE** (new class, added mid-sweep at the lead's instruction): an item that asserts an
outcome rather than specifying a check, so it reads as already-satisfied and nothing ever
builds or runs it. Two confirmed: Ruling 21's "Acceptance test" is a standard for judging a
future *auditor's* correctness ("...has mis-applied this ruling"), not a system check — a count
is derivable, no violation threshold is stated, and a verifying subagent was observed supplying
that threshold itself rather than finding it stated. Ruling 51's "acceptance evidence is the
aggregate line's count... with the delta explained" is the same shape: the measurement is real
and built, the pass/fail line is never drawn.

**CANNOT_DETERMINE** (2): Ruling 85 item 3 has no `Violation:` clause among two genuine
siblings in the same §4 — reads as disclosure prose for the maintainer's weighing, and the
question "is this vacuous" may be the wrong one to ask of it. Ruling 29's own override clause
("unowned"/"owner TBD" in the cell) is textually triggered by register row F72 today; whether
Ruling 49's later register-conformance sentence retroactively legitimises that phrasing, or
F72 is the live regression Ruling 29 exists to catch, is not resolved here.

## 6. The growth-versus-undercount split

Ruling 93's own commit: `22d8d64`, `2026-09-02T12:53:04+01:00`. First-commit timestamp of every
one of the 30 files carrying a genuine item (`git log --format=%aI --follow -- <path> | tail
-1`):

**28 of 30 existed at or before Ruling 93's own commit; 2 arrived after** — Ruling 94's own
file (`13:27:48`) and Ruling 95's own file (`14:28:36`). Of the gap between Ruling 93's
"twelve" and this record's 30: **2 is growth, 16 is undercount** (28 files already carried a
genuine item when Ruling 93 said twelve). Ruling 94's "fourteen," filed at `13:27`, could in
principle have seen up to 29 of the 30 (everything but Ruling 95's own file, filed after it) —
so that revision undercounted by at least 15.

## 7. Behavioural evidence, where it exists

Ruling 21 is the only item in this sweep with an *observed* failure rather than a mood
judgement: a verifying subagent built the check the item describes, then had to invent the
pass/fail threshold itself, live, because the ruling never states one. Every other INDICATIVE
or CANNOT_DETERMINE finding above is a structural reading (a clause present or absent, a
`Violation:` sentence present or absent) — real, but not behaviourally demonstrated the same
way.

## 8. Full table

`ruling-acceptance-item-sweep-5c0d24d.csv`, same directory — 98 rows, one per ruling,
columns `ruling,record_file,class,item_summary,evidence`.

## 9. Provenance — how 31 became 30, not just that it did

The count was not 30 on the first pass. It was **31**, reported to the lead, then corrected
down by one file after applying the lead's own stated boundary — *"an `Overridden if `<X>``
clause is never itself an acceptance item"* — back onto this sweep's own data. The path:

1. First pass counted `nt-0015-q1-q5-rulings.md` (Rulings 49-53) as carrying acceptance items
   for Rulings 50, 51, **52, and 53** — the last two admitted because real, running code
   enforces their substance (`register-owed.py`'s dirty-worktree refusal for Ruling 52; the
   findings-directory naming convention `docs/audit/findings/README.md` ties to Ruling 53).
2. Re-reading Rulings 52 and 53's *own text* against the boundary found neither states a
   `Violation:` clause or any check — only "Three constraints" / "Three sub-rules" plus an
   "Overridden if" clause. **The code enforcing their substance is real; the ruling stating a
   check is not the same fact**, and only the second counts as "genuine" under §1's own
   definition. This is the identical conflation a verifying subagent had already been caught
   making on Ruling 41 earlier in the same sweep — found a second time, in this sweep's own
   output, by applying the same rule to itself rather than assuming the first catch was the
   only instance.
3. Rulings 52 and 53 moved CONSTRUCTIBLE → NONE_FOUND. Rulings 50 and 51 still carry genuine
   items (50 built and tested; 51 reclassified INDICATIVE separately, §5), so
   `nt-0015-q1-q5-rulings.md` stays in the count. **`nt-0016-q4-q5-q6-q7-notes-rulings.md`
   (Rulings 55-58) did not survive the same re-read** — all four of its rulings state only an
   override clause, with no exception — and dropped out of the file count entirely: 31 → 30.

Recorded as a path rather than a number because the number alone does not show the count was
**measured against a stated rule** rather than **settled on and then defended** — a sweep that
only ever revises upward on a second look is fitting its own expectation; one that revises
against its own reported total, by the same rule it was just handed, is checking itself.

## 10. On verifying a count — a total validates the total, and nothing else

The lead verified this record's first class-count line (`CONSTRUCTIBLE=52 ... NONE_FOUND=37`,
since corrected to `54 ... 35`) by confirming the six numbers summed to 98. They did. **So
does the corrected set** — two buckets had moved by 2 in opposite directions, and a sum is
invariant under a transfer between buckets, so that check was not unlucky: it was
**structurally incapable** of detecting the error it was run against. Recorded here, in the
artifact the error nearly entered, rather than only in the chat thread that caught it, because
it generalises past this one count: **a total validates the total and nothing else.** This is
the same reason `scripts/ruling-acceptance-item-census.py` (§2) asserts bucket membership by
naming which heading fell into which bucket, not by confirming a printed sum — Ruling 83's own
census property, restated: the arithmetic only catches an undercount if the check names units,
not if it only re-adds what it was given.

## 11. Dated correction — 2026-09-02 (same day, after filing): WITHDRAWN, a seventh class

**This class was absent from the brief this sweep was commissioned against.** The brief named
two failure shapes — VACUOUS AT BIRTH and INVALIDATED — and this record added INDICATIVE and
CANNOT_DETERMINE while the sweep was in progress. A fifth shape surfaced only after filing,
while answering a follow-up question about which rulings a downstream migration slice applies
to, and the six classes above cannot express it. Filed as a correction to this record, not an
edit to §5's table or the CSV — the six-class count in §5 stands as filed, exactly as Rulings
93 and 94 stand as filed under this record's own `Corrects` header.

**The shape: an item that fires constantly and returns the wrong verdict, in both directions
at once — false positives *and* false negatives.** It is not VACUOUS AT BIRTH, because it
fires; not INVALIDATED, because nothing broke it — it was wrong on the day it was written; not
INDICATIVE, because it is a genuine, running check, just of the wrong thing. Named
**WITHDRAWN**, after the disposition both of its instances actually received.

- **Ruling 66 acceptance item 2** (original, reversion-based test), withdrawn by Ruling 73.
  Measured against the shipped `sweep_legacy_forms` on the real corpus: **8 false positives**
  on non-members that pass (`repo-architecture`, `dev-commands`, `git-hygiene`, `CLAUDE.md`,
  four role files), **4 false negatives** on real members that fail — one of them
  `subagent-driven-development`, a **primary** instrument the criterion exists to protect —
  and no under-inclusion limb at all, so a member nobody thought to list could never have been
  caught either way. §5's CONSTRUCTIBLE count for Ruling 66 reflects its live replacement
  (2a/2b/2c, demonstrated falsifiable against the real corpus in Ruling 73's own §5); the
  original item is what this correction names.
- **Ruling 16 acceptance item 1**, withdrawn the same day it was filed (`docs/plans/2026-08-
  29-w11-algorithm-pin-maturity.md:124`, "Correction to Ruling 16," discharging register row
  F32): the property it claimed "becomes expressible for the first time" in a later slice had
  already shipped and passed in an earlier one. Never a standing defect — found and closed
  same-day — which is why it counts as an instance of the shape rather than as an open
  finding.

**Both instances are closed, not open.** Verified 2026-09-02 against the item-4 follow-up
this correction arose from: does a downstream migration slice apply to either withdrawn item?
No — the *withdrawn* items are superseded by live, sound replacements, and nothing currently
scheduled depends on the withdrawn text. Filed here as taxonomy, not as outstanding work.

**The finding this correction states about itself, plainly rather than softened:** a
taxonomy commissioned to classify every defect a corpus contains, and missing a slot for a
defect that same corpus actually contains, is the same failure this sweep exists to find,
recurring in the sweep's own instrument. It was not caught by the brief, the sweep's own
first pass, or either verifying subagent; it surfaced only because a downstream question
("does this still apply") forced a second look at material already filed as resolved.

## 12. Status note, added 2026-09-02: two findings converted to scheduled work

Not a correction to this record's own content — a pointer, so a reader arriving later does not
have to re-derive that these two items are no longer merely findings. **W37-5c**, a precondition
slice cut after this sweep, scopes itself to "everything that stops or blinds" the migration
run. On the *blinds* limb: **Ruling 84 §4 item 2's substituted check (Ruling 94) is to be
built**; **Ruling 86 §4 item 3 is to be rebuilt so it can pass on some input**. Neither stops
the run by itself — both are checks meant to police it that currently cannot fail — which is
exactly "blinds" rather than "stops," and exactly why both are in W37-5c's scope rather than
already fixed. Status as of this note: scheduled, not yet built. See `docs/roadmap.md` and
W37-5c's own filed plan for current state; this record does not track it further.
