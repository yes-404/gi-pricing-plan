---
id: RL-9960
family: ruling
title: FR-246 does not count FR-221's stamped date — a lookup's as_at "effective_date" is exempt; any other as_at is a read and must be declared
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-10
owner: decision-maker
tree: fe0b0627590307259ec6d56be7f73115cf245092
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [FR-246, FR-221, RL-1446, RL-1519]
---

# RL-9960 — FR-246 does not count FR-221's stamped date: a lookup's `as_at: "effective_date"` is exempt

*Disclosure: drafted under working id 9960, reserved by the lead (team-lead) on 2026-10-10;
the id is minted in a later batch mint PR. When it is minted, the working id in this record
is replaced by the minted id.*

## Ruled

- **The decision is not this record's.** It is the maintainer's (by delegation), in the entry
  of `~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-10 15:40:36 BST — RULING:
  FR-246 vs FR-221 = (B), exempt ONLY `as_at == "effective_date"` (the stamped date). The
  FR-246 carve-out text is ruled HERE and lands IN THE SLICE with the code; the formal RL
  rides D8" (`to-lead.md:21407`). Its item 3 orders this record. This record decides nothing
  beyond that entry.
- **The question it answers** was raised in the lead's entry of
  `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md` headed "2026-10-10 15:40:14 BST —
  Lead: SPEC-INTERNAL CONFLICT surfaced by the FD-1374 slice — FR-246 (RL-1519) as enforced
  vs FR-221 (RL-1446): the STAMPED effective_date read by a lookup's as_at — ruling needed"
  (`from-lead-2026-10-09.md:1201`). It set out options (A), (B) and (C), quoted below.
- **No other record's front matter changes.** This record `relates:` FR-246, FR-221,
  `RL-1446` and `RL-1519`, as item 3 of the entry names; it `corrects:` nothing. See *Why
  `relates:`* for what that does and does not settle.

## The maintainer's entry, verbatim (in full)

```text
## 2026-10-10 15:40:36 BST — RULING: FR-246 vs FR-221 = (B), exempt ONLY `as_at == "effective_date"` (the stamped date). The FR-246 carve-out text is ruled HERE and lands IN THE SLICE with the code; the formal RL rides D8

Decision: FR-221 (RL-1446) rules a lookup's `as_at: "effective_date"` as the quote's STAMPED date, which no one declares. Counting it as a read under FR-246 would force an input step and, through FR-213, a silent API change (every quote must send effective_date). The authored contract wins: the stamped date is not a declared read. Exempt EXACTLY that value, nothing wider.
1. CODE: references.py exempts only `as_at == STAMPED_DATE` (the constant FR-221's code already uses, by symbol, never a pasted string). Red-first BOTH ways: (i) a lookup with `as_at: "effective_date"` and no input step compiles; (ii) a lookup with any OTHER `as_at` naming an undeclared field is still refused by FR-246.
2. SPEC (CLAUDE.md §2: spec and code in one commit): the slice adds THIS dated line to 03 FR-246's row, verbatim:
   "*(Clarified 2026-10-10 by the maintainer (by delegation): a lookup's `as_at: "effective_date"` reads the quote's stamped date (FR-221, RL-1446) and is not a read FR-246 counts; any other `as_at` value is a read and must be declared.)*"
   This is ruled text, so the executor carve-out holds (the executor writes nothing of its own). It does NOT touch §4.1, so Acceptance 4's byte check is unaffected.
3. The clarifying RL (relates: FR-246, FR-221, RL-1446, RL-1519; cites this entry) rides D8 as the formal record.
4. The fixture work: the ~47 as_at reds then pass with NO fixture change. Only the remaining ~4 reds get the 15:36:02 declaration-only treatment. The LG lists which fixtures needed declarations, and that the as_at ones needed none.
(A) rejected (a silent API change). (C) rejected (too wide: it would hide real undeclared as_at reads).
```

The options it chose between, verbatim from the lead's 15:40:14 entry
(`from-lead-2026-10-09.md`):

```text
- (A) Fixtures declare effective_date (contract + input step) AND test quotes carry it: test-data change beyond "declaration only" (your 15:36:02), and ships the API change "callers must send effective_date".
- (C) references.py stops counting `as_at` at all: wider — it would also exempt a declared date input named by as_at, which FR-246 should still police.
```

## The decision

1. **Only `as_at == STAMPED_DATE` is exempt.** A `lookup` step's `as_at: "effective_date"`
   names the quote's stamped date. FR-221, as amended by `RL-1446`, says so: "`as_at` names
   `effective_date` — the quote's stamped date — or a declared `date` input, and nothing
   else" (`docs/specs/03-rating-engine.md:108` at `fe0b0627`). No one declares the stamped
   date, so FR-246 does not count it as a read.
2. **Any other `as_at` value is a read.** It must be declared in the step's `consumes`, and
   FR-246 refuses it with `RATING_STEP_UNDECLARED_READ` when it is not.
3. **Only the `as_at` field is exempt.** An expression, or any other evaluating field, that
   reads `effective_date` as a value is a read and must declare it.
4. **(A) is rejected:** it ships a silent API change. Through FR-213, every quote would have
   to send `effective_date` in its inputs.
5. **(C) is rejected:** it is too wide. It would hide real undeclared `as_at` reads, a
   declared date input named by `as_at` among them.

## Why `relates:`, and what it does not settle

The entry names `relates:` (item 3), so this record `relates:` and does not `corrects:`. Two
facts bear on that, both read at `fe0b0627`:

- **`RL-1446` left the question open.** Its *What is not changed* says: "**FD-1374's
  question** (whether an input may carry a stamped name at all) stays with its owner, PL 9776.
  This record does not decide it" (`RL-1446` :164–:166). This record answers the part of it
  that FR-246's enforcement raised.
- **`RL-1519` states the opposite in two places.** This record does not assert that
  `RL-1519`'s text is consistent with this decision, because it is not:
  - `RL-1519` :657–:658, its *Acceptance* case 3: "**A lookup's `as_at` is a read.**
    `referenced_names` of a lookup with `as_at: "effective_date"` contains `effective_date`
    (Task 1A's extractor test, last assertion)." The slice commit `2838df55` changes that very
    assertion (see *Where the code carries it*).
  - `RL-1519` :284, its worked-example *Fix* table: "`s_area` declares `effective_date`, its
    `as_at`." Declaring it is no longer required. This record does not say whether declaring
    it is now wrong.

  `RL-1519`'s general scope stands as it is: "a `lookup`'s `as_at`" is one of the fields
  FR-246 binds (`RL-1519` :138–:142), and every `as_at` other than the stamped date is still
  a read.

Whether `RL-1519`'s *Acceptance* case 3 needs a correcting record is **not decided here**.
It is raised to the lead (*What this record does not decide*).

## Where the code carries it — on the FD-1374 slice's branch, not on main

The slice branch is `origin/sl-1536-fd1374-dp-f35-1`. The commit is
`2838df556dfc67de3b81eabaf9fc8119cecb4f91` ("feat(rating): FR-246 does not count a lookup's
as_at effective_date (the stamped date); 03 FR-246 clarified (ruling 2026-10-10 15:40:36
BST)"). It is an ancestor of the branch head `e3a8f0bbdc81ac649feecb13c41cf4e386aed106`, and
none of the five files below differ between `2838df55` and that head. None of it is on main at
`fe0b0627`. All lines are at `2838df55`.

- **The constant, by symbol.** `STAMPED_DATE` is defined once, at
  `packages/pricing-core/src/pricing_core/rating/authored.py:46`. The commit moves it there
  from `compile.py` (`:400` at `fe0b0627`, FR-221's code). `compile.py` imports it (`:48`) and
  still uses it at `:413`.
- **The exemption.** `packages/pricing-core/src/pricing_core/rating/references.py:45–:46`, in
  `referenced_names` (`:35`): when the field is `as_at` and its text equals `STAMPED_DATE`, the
  name is not counted. No other field and no other value is exempt.
- **The tests**, `packages/pricing-core/tests/test_rating_declared_reads.py` (a new file on the
  branch; it is not on main):
  - `test_a_lookup_as_at_the_stamped_date_declares_nothing` (`:254`): the entry's direction
    (i). Its docstring says it was red before the exemption.
  - `test_a_lookup_as_at_any_other_undeclared_name_is_still_refused` (`:261`): the entry's
    direction (ii). Its docstring says it is green before and after the exemption: it guards
    the exemption's width, which existed before.
  - `test_an_expression_reading_the_stamped_date_as_a_value_still_declares_it` (`:268`): the
    narrowing, decision 3.
  - `test_referenced_names_reads_every_field_a_step_evaluates` (`:26`): its lookup assertion
    is now `== {"postcode_outcode"}` (`:48`), and `:50` asserts that an `as_at` of
    `"inception"` is counted.

  This record does not assert that any test was seen red. The slice's ledger records that.
- **The spec line.** `docs/specs/03-rating-engine.md:150`, FR-246's row, ends with the ruled
  dated line, verbatim:

  > *(Clarified 2026-10-10 by the maintainer (by delegation): a lookup's `as_at: "effective_date"` reads the quote's stamped date (FR-221, RL-1446) and is not a read FR-246 counts; any other `as_at` value is a read and must be declared.)*

  It is byte-equal to the text in item 2 of the entry.

If the slice branch is rebased or squash-merged, these SHAs and line numbers name the branch at
`2838df55`, not the merged result.

## What it obliges

- **Order.** The spec line and the code merge with the FD-1374 slice (entry item 2). This
  record rides the docs batch D8, which merges after that slice (entry item 3).
- Nothing else. The code, the tests and the spec line are the slice's, under the entry; this
  record adds none of them.

## Acceptance — the violations that must become detectable

- A lookup with `as_at: "effective_date"` and no declaration is refused by FR-246.
  *Detected by* `:254` above.
- A lookup with any other `as_at` naming an undeclared name compiles. *Detected by* `:261` and
  by the `:50` assertion.
- An expression reading `effective_date` as a value without declaring it compiles. *Detected
  by* `:268`.
- `03` FR-246's row lacks the ruled line. *Detected by*, after the slice merges:
  `git grep -nF 'is not a read FR-246 counts; any other' -- docs/specs/03-rating-engine.md`,
  which prints one line, FR-246's row.

## What this record does not decide

- **Whether `RL-1519`'s *Acceptance* case 3 (:657–:658) needs a correcting record**, and
  whether its worked example's `s_area` keeps `effective_date` in `consumes` (:284, :342–:346).
  This record found the conflict and raises it to the lead.
- The roughly four remaining fixture declarations (the entry's item 4; the 15:36:02 entry), and
  the two purpose tests (the entry "2026-10-10 15:42:57 BST").
- Whether FD-1374 is discharged. The verdict is the lead's.
