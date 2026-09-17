---
id: PL-1035
family: plan
kind: leaf
title: W37-6 — A reading of §7(g)'s ruled predicate: the six classes exist, they are a widening, and `row_g` implements one of them (2026-09-03)
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-03
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-09-03-w37-6-row-g-reading.md
---

# W37-6 — A reading of §7(g)'s ruled predicate: the six classes exist, they are a widening, and `row_g` implements one of them (2026-09-03)

**Filed** 2026-09-03 by the decision-maker, at the lead's commission, against `main` at
`a92d4e8`. **What this is.** A **reading** of what §7(g) requires, in the same shape as Ruling
103's readings of (e) and (f): the text, the sentences it rests on, and the options — **not a
ruling, and not a re-ruling.** Every remedy named below is the maintainer's.

**It is not a ruling and takes no ruling number.** Nothing here binds. Where the reading finds a
gap, the options are priced and the choice is left open, per `CLAUDE.md` §10.

**Scope, stated so it is not read wider than it is.** Three questions were asked and three are
answered. This record does not evaluate `_docverify.py` beyond `row_g`, does not propose an
implementation, and does not touch the fixture or the script — `.claude/roles/decision-maker.md`
forbids both, as RL-1044 §5.4 already records.

## Summary

| # | question | answer |
|---|---|---|
| 2 | are the six classes enumerated verbatim anywhere? | **Yes** — `docs/rulings/RL-00989-dp-3-g-is-a-property-of-the-script-its-filter-is-a-closed-enumeration-and-it-shares-check-34-s-predicate.md:46-57`. The absence claim is **false**, and §2 gives the predicate that finds them |
| 1 | is the enumeration the same requirement as §7(g)'s sentence, or a widening? | **A widening, and RL-989 says so in terms** — it *refutes* the bare sentence as undefined before replacing it. `row_g` implements the narrower one, so **row (g) is red by construction.** The deputy's conclusion holds |
| 3 | do the classes admit §5.2's designed content generation? | **Mostly, and not entirely.** Classes 3-6 admit the moves, splits, roadmap restructure and four named artifacts. **They do not admit regenerated per-family `README.md` files**, and whether class 6's bare `INDEX.md` means the top-level one or every one **cannot be decided from its text** |

---

## 1. Question 2 first, because it was asked second and answers cheapest

**The six classes are enumerated verbatim**, in RL-989 §2, at
`docs/rulings/INDEX.md#2026-09-02-w37-migration-preconditions-rulingsmd`, **the introducing sentence at
`:255-256` and the six items at `:258-266`**, read at `a92d4e8`:

> *"§4's steps 1-7 are the closed list of what `migrate` is permitted to do, and the filter is
> that list — a hunk is permitted only where it is:*
>
> 1. *a front-matter block added, together with the legacy prose or bullet header it replaces
>    being removed (§4 step 5);*
> 2. *a reference token substituted inside a line, from the step-6 allow-list (§4 step 6);*
> 3. *a file moved or renamed, detected as a rename, with no content change (§4 step 4);*
> 4. *a split, where the concatenation of the outputs reproduces the input's body lines in
>    order (§4 step 2);*
> 5. *the `roadmap.md` restructure of §4 step 3;*
> 6. *a generated artifact regenerated in full — `INDEX.md`, `REDIRECTS.csv`, `docs/contracts/`,
>    the core-JSON digest (§4 step 7)."*

> **Citation corrected 2026-09-03, before this record merged, and the correction is its own
> small instance of §1.1.** This record first cited the enumeration as **`:256-262`** — a range
> that **opens on the introducing sentence and closes inside item 4**, so a reader following it
> would meet four of the six classes and no statement that there were six. The deputy first cited
> `:258-265`, short by item 6's continuation line, and corrected itself to `:258-266`. **Three
> parties produced three ranges for one list**, none of them wrong about *what* the list says and
> two of them wrong about *where it ends*. Re-derived here by numbering the lines directly rather
> than by trusting any of the three: the intro is `:255-256`, item 1 opens at `:258`, and item 6
> closes at `:266`. **A range is a predicate too, and a wrapped list item is where it silently
> stops being one.**

**The predicate that finds them**, so this is reproducible rather than a lucky read:

```
git grep -n 'a hunk is permitted only where it is' origin/main -- docs/
  → docs/rulings/RL-00989-dp-3-g-is-a-property-of-the-script-its-filter-is-a-closed-enumeration-and-it-shares-check-34-s-predicate.md:47   (one hit, exactly)
```

### 1.1 Why the absence claim was produced, because the mechanism matters more than the correction

The searches that returned nothing were, per the commission, `'RL-989|six.class|permitted'`
over **`scripts/_docverify.py`** and `'six classes named'` over `docs/`.

**Both are correct results to the questions they asked.** The first asks whether the *script*
mentions the classes — it does not, which is itself part of the answer to question 1. The second
finds every place the enumeration is **cited** — *"implemented as code with the six classes
named"* — and **the enumeration itself contains no such phrase**, because it is a numbered list
introduced by *"a hunk is permitted only where it is:"*.

**So the search found the citations of the list and concluded the list was absent.** That is the
same class as `RL-993` and the `977` misattribution recorded against RL-1044 — **a correct
result attached to the wrong question** — and it is the third instance today. **A list is not
found by the words used to refer to it**, and an absence claim over prose needs a predicate drawn
from the artifact's own wording, not from its citations'.

**`docs/closures/CR-01050-plan-review-12-the-w37-6-w37-11-boundary-mid-window.md:48` does not say what it was read as saying.** It names *"Ruling
68's **class-6 extension** ratification"* as resolving to nothing. **That is the extension, not
the base six** — see §3.2. The base enumeration resolves fine.

---

## 2. Question 1 — a widening, and RL-989 refutes the bare sentence before replacing it

**RFC-937 §7(g)'s own sentence:** *"the migration diff filtered to hunks that are neither header
nor citation-token is empty."*

**RL-989 §1's fourth verification row rules on exactly that sentence**, verbatim:

> *"**(g)'s filter is defined** | **Refuted.** 'Neither header nor citation-token' does not
> classify the script's own remaining steps — the splits of §4 step 2, the `roadmap.md`
> restructure of step 3, the moves of step 4, or the regenerated artifacts of step 7. Left as
> worded, an executor invents a filter at the console."*

**That settles the question and settles it against the "restatement" reading.** The ruling does
not gloss the sentence; it **finds the sentence insufficient by name**, lists the four kinds of
change it fails to classify, and replaces it with a closed enumeration. **A restatement does not
begin by refuting the thing it restates.**

**So the two are different requirements, and the enumeration is the wider one.** Classes 3, 4, 5
and 6 each admit hunks that *"neither header nor citation-token"* scores as unexplained — which
is precisely the list RL-989 gives as its grounds.

### 2.1 What `row_g` implements

Read at `a92d4e8`, `scripts/_docverify.py`, `row_g`:

```python
body_removed = [ln for ln in removed if not _is_header_line(ln)]
body_added   = [ln for ln in added   if not _is_header_line(ln)]
changed += len(body_removed) + len(body_added)
if sorted(_mask(ln) for ln in body_removed) == sorted(_mask(ln) for ln in body_added):
    continue
unexplained += len(body_removed) + len(body_added)
```

**Two of the six, and one of those only partially.**

- **Class 2 — implemented.** The `_mask` equality is the citation-token substitution test.
- **Class 1 — partially.** Header lines are **dropped** from the population rather than checked
  as a *pair* (block added **together with** the legacy header it replaces being removed). A
  front-matter block added with no legacy header removed is not distinguished from a correct
  one.
- **Classes 3, 4, 5, 6 — implemented nowhere.**
  `git grep -n -iE 'rename|split|roadmap|regenerat|concatenat' origin/main -- scripts/_docverify.py`
  returns **ten** hits at `a92d4e8` and **none is a classifier**: every one is `str.split` or
  `str.splitlines`, plus one prose mention of *"the index never regenerated"* in a docstring.
  **The hits are reported rather than the command being narrowed until it returned nothing** — a
  predicate tuned until it produces the expected zero is the shape this record's §1.1 is about.

**Conclusion: row (g)'s implementation is the refuted reading.** It computes *"neither header nor
citation-token"*, which RL-989 rejected as the definition. **The row is red by construction,
and no fix to `migrate` can discharge it**, because the migration is *required* to produce
class 3-6 hunks by §4's own steps. **The deputy's finding holds.**

### 2.2 The consequence for RL-1043 §2 row 1, stated but not decided

RL-1043 §2 puts (g) first in the sequence and names `NFR-502/501` as its broken-input
proof. **The token-boundary defect is real and its fix is real** — nothing here touches that.
**What does not follow is that fixing it turns row (g) green**, because the row is measuring a
predicate RL-989 replaced. **Both can be true: the (g) *defect* is fixable and the (g) *row*
is not passable as implemented.**

**Whether that reopens RL-1043 §2's ordering is the maintainer's**, and this record does not
touch it.

---

## 3. Question 3 — mostly admitted, with one gap and one ambiguity

**Admitted by the enumeration as written:**

| §5.2 content generation | class |
|---|---|
| moves and renames with no content change | 3 |
| the split of `closure-records.md`, `plan-reviews.md`, the multi-ruling plans | 4 |
| the `roadmap.md` restructure | 5 |
| `docs/INDEX.md`, `REDIRECTS.csv`, `docs/contracts/`, the core-JSON digest | 6 |

**So class 6 admits §5.2's generation of the four artifacts it names, and classes 3-5 admit the
structural work. If they were implemented, most of `row_g`'s current `unexplained` population
would be classified.** The answer to *"if the classes admit it, (g) cannot pass until they are
implemented"* is **yes** — that is the state.

### 3.1 The gap — regenerated per-family `README.md` files are in no class

§5.2 makes several `README.md` files **generated**: the `workflows/` README table *"generated"*,
the `adr/` README *"generated"*, and new `closures/`, `findings/`, `rulings/`, `ledgers/`
READMEs. **Class 6's list is closed and names four artifacts. A `README.md` is not among them**,
and it is not a move (3), a split (4), or the roadmap (5).

**This is not a new discovery and was flagged rather than taken.** `_MIGRATION_DIFF_FAMILY_READMES`
(`scripts/doc-id.py`) carries in its own comment that it is *"a further extension of RL-989's
six-class enumeration, and the lead is told so in the PR rather than finding it in a diff"*,
naming itself *"the seventh kind of hunk a clean run now produces."* **The executor did the right
thing and the ratification never happened** — which is what `plan-reviews.md:2854` records as
resolving to nothing.

### 3.2 The ambiguity — class 6's `INDEX.md` does not say which

Class 6 names **`INDEX.md`** unqualified. §1.4 puts one at `docs/INDEX.md`; RL-1042 and
RL-1043 §6 create one **per family** (`docs/closures/INDEX.md`, `docs/plans/INDEX.md`).
**A reader cannot tell from class 6's text whether it means the top-level one or every file of
that name**, and the existence of a separate `_MIGRATION_DIFF_FAMILY_INDEXES` constant
(`origin/w37-6-split-source-resolver:scripts/doc-id.py:5653`) is evidence that its author could
not tell either.

**That is `RFC-777` exactly** — a reference that resolves only for its writer — and it is a
one-word fix to the ruling text, not an implementation question.

---

## 4. The options, priced and not chosen

**All three are the maintainer's.** RL-989 is a maintainer ruling and an amendment to what it
requires is the maintainer's alone (`CLAUDE.md` §12).

| option | what it costs | what it risks |
|---|---|---|
| **A — implement classes 3-6** as RL-989 obliges (*"implemented as code with the six classes named"*) | the largest build of the three; four classifiers, and class 4's *"concatenation reproduces the input's body lines in order"* is the expensive one | nothing about the ruling changes; the row becomes passable and the acceptance tests in RL-989 §4 become runnable. **This is the option the ruling already requires** |
| **B — amend §7(g) to the narrower sentence** and drop the enumeration | cheapest; `row_g` becomes correct as written | **reinstates the reading RL-989 refuted**, and its stated ground — *"left as worded, an executor invents a filter at the console"* — is not answered by making the row green |
| **C — implement 3-6 as a disclosed allow-list of paths** rather than classifiers | middle cost | RL-989 §2 **already rejected a path exclusion**, on the measured ground that thirteen §5.2 rows put script output and hand edits in the same file. Reintroducing it here would need that refutation answered, not repeated |

**Two items are owed regardless of which is chosen**, because they are gaps in the ruling's text
rather than in its implementation:

- **the seventh class for regenerated READMEs** — ratify `_MIGRATION_DIFF_FAMILY_READMES`, or
  widen class 6 to *"a generated artifact regenerated in full"* with the four names as examples
  rather than the closed list;
- **class 6's `INDEX.md` scope** — one word saying whether it is the top-level file or every
  file of that name.

**Neither is a decision this record makes**, and both are cheap enough that leaving them implicit
is the expensive choice.

## Acceptance Standard

**This record is accepted when the lead merges it. It binds nothing.** It is a reading, and the
three questions it answers are answered against the texts cited, each with the command that
found them.

**It is falsified** if the six-class enumeration is found to be a restatement rather than a
widening — which would require RL-989 §1's fourth row to say something other than
**Refuted** — or if a classifier for any of classes 3-6 is found in `scripts/_docverify.py` at
`a92d4e8`.

**No remedy is adopted here.** §4's options A, B and C are the maintainer's, as are the two owed
text fixes of §3.1 and §3.2.
