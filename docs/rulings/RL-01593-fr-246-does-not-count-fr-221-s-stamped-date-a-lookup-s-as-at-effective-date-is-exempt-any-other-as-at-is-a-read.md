---
id: RL-1593
family: ruling
title: FR-246 does not count FR-221's stamped date — a lookup's as_at "effective_date" is exempt; any other as_at is a read and must be declared
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active; draft until minted
created: 2026-10-10            # original date 2026-10-10, set at the draft; minted 2026-10-10
owner: decision-maker
tree: fe0b0627590307259ec6d56be7f73115cf245092
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
corrects: RL-1519
relates: [FR-246, FR-221, RL-1446, RL-1519]
---

# RL-1593 — FR-246 does not count FR-221's stamped date: a lookup's `as_at: "effective_date"` is exempt

*Disclosure: drafted under working id 9960; minted as RL-1593 on 2026-10-10, in the D8a batch mint PR.*

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
- **The correction is the maintainer's (by delegation) too**, in the entry headed "2026-10-10
  16:29:07 BST — Premise correction ACCEPTED: RL 9960 CORRECTS RL-1519 (:284 and Acceptance
  case 3, :657–658). My 15:40:36 overrode a standing ruling unread. D8 SPLITS: D8a (RL 9960)
  BEFORE the FD-1374 slice; D8b (the §4.1 example correction) AFTER it" (`to-lead.md:21466`),
  quoted in full below. Its item 1 gives this record `corrects: RL-1519`.
- **`corrects: RL-1519` is limited.** It covers two places in `RL-1519` and nothing else, both
  read at `fe0b0627`: the `as_at` clause of the `s_area` row of the worked-example *Fix* table
  (:284, "`s_area` declares `effective_date`, its `as_at`.") and *Acceptance* case 3
  (:657–:658, "A lookup's `as_at` is a read. `referenced_names` of a lookup with
  `as_at: "effective_date"` contains `effective_date`"). Both are quoted verbatim in *What this
  record corrects*. `RL-1519`'s front matter gains `corrected_by: [RL-1593]` and its body does
  not change by one byte.
- **The corrected rule**, in the words of the 15:40:36 entry: only `as_at == "effective_date"`
  is exempt; any other `as_at` is a read; an expression that reads `effective_date` as a value
  must declare it.

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

The correction, verbatim (the entry's three items, in full):

```text
## 2026-10-10 16:29:07 BST — Premise correction ACCEPTED: RL 9960 CORRECTS RL-1519 (:284 and Acceptance case 3, :657–658). My 15:40:36 overrode a standing ruling unread. D8 SPLITS: D8a (RL 9960) BEFORE the FD-1374 slice; D8b (the §4.1 example correction) AFTER it

Verified at origin/main: RL-1519 :284 "`s_area` declares `effective_date`, its `as_at`" and :657 "A lookup's `as_at` is a read … contains `effective_date`". My 15:40:36 reversed this without reading it (the 10 Oct premise pattern again). SUBSTANCE STANDS: following RL-1519 here would make every quote send effective_date (FR-213), against FR-221/RL-1446's stamped date, a silent API change. The instrument is a correcting record:
1. RL 9960 takes `corrects: RL-1519`, limited to :284's `s_area` as_at clause and Acceptance case 3 (:657–658). It states the corrected rule in my 15:40:36 words (only `as_at == "effective_date"` is exempt; any other as_at is a read). RL-1519 gains `corrected_by: [RL-…]`, front matter only.
2. ORDER (my 04:23:36 rule: code on main never contradicts a standing ruling, even for one merge): the slice's 2838df55 changes exactly RL-1519's Acceptance case 3 assertion, so RL 9960 must be ON MAIN BEFORE the FD-1374 slice merges. But the OTHER RL-1519 correction (the §4.1 two-names example, 14:43:15) must land AFTER the slice (Acceptance 4's byte check). So:
   - D8a = RL 9960 alone (plus anything else that must precede the slice), merged FIRST.
   - The FD-1374 slice merges.
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
   reads `effective_date` as a value is a read and must declare it. In one sentence: only
   `as_at == "effective_date"` is exempt; any other `as_at` is a read; an expression reading
   `effective_date` as a value must declare it.
4. **(A) is rejected:** it ships a silent API change. Through FR-213, every quote would have
   to send `effective_date` in its inputs.
5. **(C) is rejected:** it is too wide. It would hide real undeclared `as_at` reads, a
   declared date input named by `as_at` among them.

## What this record corrects — `RL-1519`, two places, at `fe0b0627`

`RL-1446` left the question open. Its *What is not changed* says: "**FD-1374's question**
(whether an input may carry a stamped name at all) stays with its owner, PL 9776. This record
does not decide it" (`RL-1446` :164–:166). This record answers the part of it that FR-246's
enforcement raised. `RL-1519` stated the opposite in two places, and this record corrects
exactly those:

1. `RL-1519` :284, the worked-example *Fix* table, the `s_area` row, verbatim:
   "`s_area` declares `effective_date`, its `as_at`." **Corrected:** `s_area` does not need to
   declare `effective_date` for its `as_at`; the stamped date is not a declared read. Whether
   the example's `consumes` for `s_area` keeps `effective_date` is the §4.1 example
   correction's, which is D8b and merges after the FD-1374 slice (the entry's item 2).
2. `RL-1519` :657–:658, *Acceptance* case 3, verbatim: "**A lookup's `as_at` is a read.**
   `referenced_names` of a lookup with `as_at: "effective_date"` contains `effective_date`
   (Task 1A's extractor test, last assertion)." **Corrected:** `referenced_names` of such a
   lookup does not contain `effective_date`; a lookup with any other `as_at` still contains
   it. The slice commit `2838df55` changes that very assertion (see below).

`RL-1519`'s general scope stands as it is: "a `lookup`'s `as_at`" is one of the fields FR-246
binds (`RL-1519` :138–:142), and every `as_at` other than the stamped date is still a read.

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
`2838df55`, not the merged result. `STAMPED_DATE`'s final home is set by the slice (lead
direction: `references.py`); cite the merged location after the slice merges.

## What it obliges

- **Order.** This record merges BEFORE the FD-1374 slice (D8a): the slice's `2838df55` changes
  `RL-1519`'s *Acceptance* case 3 assertion, and code on main must not contradict a standing
  ruling, even for one merge (the 16:29:07 entry's item 2). The spec line and the code merge
  with the slice. The §4.1 example correction is D8b and merges after the slice.
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

- **The §4.1 example correction** and whether the worked example's `s_area` keeps
  `effective_date` in `consumes` (`RL-1519` :342–:346): D8b's, after the slice.
- The roughly four remaining fixture declarations (the entry's item 4; the 15:36:02 entry), and
  the two purpose tests (the entry "2026-10-10 15:42:57 BST").
- Whether FD-1374 is discharged. The verdict is the lead's.
