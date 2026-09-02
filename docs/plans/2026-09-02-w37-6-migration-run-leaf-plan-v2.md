# W37-6 — the migration run: leaf plan, superseding

> **For agentic workers:** REQUIRED SUB-SKILL: `subagent-driven-development`. **This plan is
> `status: active`.** It was filed `draft` with one blocking decision row open; Ruling 88
> resolved it on 2026-09-02, and `document-ids.md` §1.7's freeze condition — *"`status: active`
> is permitted only when every blocking row has a resolver id"* — is now met. **Execution still
> waits on the maintainer's dated go-ahead** (§4), which is a separate gate this plan does not
> open.

**Supersedes:**
[`2026-09-02-w37-6-migration-run-leaf-plan.md`](2026-09-02-w37-6-migration-run-leaf-plan.md),
which is frozen at its date and **is not edited** (`CLAUDE.md` §2). That plan is correct at its
own pin; §1 states the three things that moved under it.

**Goal:** run NT-0019 §4's one-time scripted migration over the whole corpus, in one supervised
commit, and make the maintainer's go-ahead an informed one.

**Architecture:** unchanged from the superseded plan — one scripted PR, once, at a gap, never
fanned out. What changes is the acceptance standard, the dependency model, and the figures.

**Spec:** [`../notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md).

**Tree:** every figure in §4 was re-derived at **`958cb7d`** when the draft was lifted, with
`HEAD` stamped before and after the measurement, and the legacy-form sweep run through the
shipped `LEGACY_FORM_PATTERNS` constant rather than a re-typed copy. **No figure is inherited
from the superseded plan**, and none is re-used from an earlier pin. **One more pass is owed at
the ask** — the maintainer's condition 6 is a property of the day the go-ahead is requested, not
of this document, and §4.2a is the evidence that the difference is not academic.

## Acceptance Standard

The slice is complete when every item passes **at the merge tree**, recorded in the ledger with
the exact command and its output. Every item is a **violation that must become detectable**.

**Items 1 to 10 and 12 to 14 are carried unchanged from the superseded plan's Acceptance
Standard and are not restated here** — that document is frozen, readable, and its wording is
the wording. **Item 11 is restated in full below, because it is the one the rulings amended and
a frozen document cannot carry its own amendment.**

### Item 11, as amended — the three-limb H-content test

Ruling 66's acceptance item 2 was **withdrawn** by Ruling 73, not sharpened. Run as written it
returned a hit for every member and for ~950 non-members alike, because §4 step 6 rewrites
citations in every tracked file, so reverting *any* file produces an item-(d) hit. Ruling 73
replaced it. The subject of the test is the instrument's **H content** — the filename, id,
directory, header-field or section form it teaches — never the file, and never its citations.

- **11a — over-inclusion.** For each member of the derived set: revert **only** its H content to
  the merge-base form, leaving its rewritten citations in place; produce the document that
  instrument mints, by following the reverted instruction literally; run
  `python3 scripts/audit-docs.py`. *Violation: no check in 30-39 fires on that document.*
- **11b — under-inclusion.** The same proof over the plan's **explicit exclusion list**, which
  must be exhaustive rather than a sample. For each excluded instrument: revert its H content,
  produce the document it mints, run the audit. *Violation: any check in 30-39 fires* — the
  exclusion was wrong and the instrument belongs in the commit.
- **11c — neither list.** *Violation: an instrument that appears in neither the adopted set nor
  the exclusion list.* This is the only limb that can catch a member nobody thought of.

**Exactly one exemption, and it is stated here rather than discovered.** A member for which no
check fires under 11a is admitted **only** where this plan already states a non-check ground for
it by name. That is `.claude/skills/README.md`, adopted on `CLAUDE.md` §12 and minting no
document. A ground discovered while running the proof is a finding against the derivation, not
an exemption.

**The superseded plan's second exemption is withdrawn.** It exempted `brainstorming` on the
ground that its correction *"removes a `docs/` path rather than replacing one, so there is no
document to produce."* Ruling 73 rejected that reason with a counter-example: the reverted H
content is an instruction to save a design document at a path under `docs/`, which the stamp set
reaches once item 10's flip lands. **11a applies to `brainstorming` unmodified**, and its result
is recorded either way.

**The ledger records, per instrument, which check fired and on what produced document** — never
that the proof passed. A verdict naming no check is the same silence the withdrawn item 2
produced.

---

## Global Constraints

The superseded plan's **G1 to G12** are carried unchanged and are not restated (one source, not
two). Two are re-stated only because a ruling since changed what they bear on:

- **G2 — the permanence rule yields at two sites, and not in this slice.** Both are edited in
  W37-9. Between this merge and that one, the governed contract states a rule the repository has
  broken. Disclosed in §4.6.
- **G5 — product identifiers are never touched.** This is the constraint §4.2's own prose
  breached in the superseded plan, and §4.2 below is corrected for it.

---

## 1. Why this revision exists

Three things moved under the superseded plan. None is a defect in it; each is a thing a frozen
document cannot say about itself.

**1.1 Its acceptance item 11 was amended in three respects.** Ruling 73 removed the
`brainstorming` exemption and added limbs 11b and 11c. **An executor following the frozen text
alone applies a weaker standard than the ruling requires and wrongly exempts one of the
thirteen instruments.** This is the strongest single reason for the revision, and it is why item
11 is restated in full above rather than cited.

**1.2 Its §3 dependency model does not describe what happened.** §3 was written for *"the
interface is not fixed yet"* and ruled *"a named gap is fine; a guessed CLI is not."* What
actually happened is different in kind: **W37-5 merged, went green, and was defective in four
places** — every `_discover_*` function was written against a fixture corpus, and four do not
match the real tree. §3 has no row for a dependency that lands and is wrong. §3 below is
rewritten for that case.

**1.3 Its §4 figures are pinned at `39ee30c`**, and Ruling 66 §3 requires the disclosure to
arrive **with** the ask. The tracked count has moved from 1447 to **1495** since that pin —
across a single session. §4 below is re-derived in full at `958cb7d`.

---

## 2. Decision points — both resolved

`document-ids.md` §1.7: *"**Freeze is mechanical:** `status: active` is permitted only when
every blocking row has a resolver id and every non-blocking row names a step."*

| # | Question | Kind | Blocking? | Resolved by |
|---|---|---|---|---|
| DP-A | Which family and `kind:` the `Pending proposals` container takes, and therefore what `_discover_plan_reviews` emits besides `CR-` records | decision point → decision-maker, one `RL-` | **Yes** | **Ruling 88**, 2026-09-02 ([`2026-09-02-w37-container-family-and-line-citations-rulings.md`](2026-09-02-w37-container-family-and-line-citations-rulings.md)) — `RFC-`, `kind: process`, `status: closed`, `created: 2026-08-29`, `was:` `docs/audit/plan-reviews.md`, its own record. **`owner: maintainer`, against the derivation's recommendation of `planner`** |
| DP-B | Where the fourteen line-number citations into the two split files are placed — a ruling, a W37-5b precondition, or a go-ahead disclosure | scope → the lead, routed to the decision-maker | No | The lead has routed it. Until placed, this plan states the property and no task builds against it (§5.3) |

**DP-A carried the freeze**, and Ruling 88 discharged it. Two things about that ruling bind
§6.1 and are recorded here rather than left in the ruling alone:

- **`owner:` is `maintainer`, not `planner`.** §1.6's `RFC` row reads *"maintainer mints and
  owns; any role drafts on instruction; lead assesses"*, and its column is **"Owner — creates &
  amends"**, not *author*. The derivation recommended `planner` and was wrong on this;
  `owner: planner` would have been the only `RFC-` in the corpus contradicting §1.6, with
  nothing to catch it because `check_owner` tests only membership.
- **Ruling 88 amended Ruling 82's fourth constraint** — three citations of the container, not
  two — and the third is what decided the placement.

**Whether `owner:` follows §1.6's family table or the historical author is a general question
this plan does not answer.** It is routed to the planner as a separate derivation and is not a
dependency of this slice: Ruling 88 settled the container on the container's facts.

---

## 3. The dependency model, rewritten

The superseded §3 assumed one failure mode — an interface not yet fixed — and guarded it well.
The failure that occurred was a different one, and it is the one this section now guards.

| | Superseded §3's model | What happened |
|---|---|---|
| Assumption | W37-5's flag surface, output shapes and fixture layout are unknown at filing | They were knowable, and are now known |
| Guard | *"A named gap is fine; a guessed CLI is not"* — state the obligation, fill the invocation from the merged script | Correct, and it worked |
| The case neither covers | **The dependency merged, its gate went green, and it was wrong** | Four `_discover_*` defects, one of them silent |

**The rule this replaces it with.** A merged dependency is evidence of a *gate passing*, never of
*behaviour on the real corpus*. The two differ exactly where the dependency's own tests use a
fixture. So:

1. **Every discovery function is run against the real corpus before it is depended on**, and its
   output is *accounted for* — every unit the source offers is a record, derivably body, or a
   declared exception, and the three sum to the total (Ruling 83). A count that merely looks
   plausible is not evidence.
2. **A guard that fires on zero is not a guard.** Both shipped guards test "zero drafts from a
   non-blank file", which is why a function returning 10 of 14 passed ungoverned. The property is
   *accounting*, not *non-emptiness*.
3. **W37-5b holds this**, not W37-6. The census runs before this slice, not inside it — Ruling 83
   §3 item 1, and Ruling 81 §2 for the parser fix, both on their own reasoning rather than this
   plan's.

**What this plan therefore assumes about W37-5b, stated as properties rather than as a
completion claim:** that `migrate` accounts for every unit of every source it splits; that no
discovery function is silent on a shortfall; and that each fix was proven on deliberately broken
input. **If any is false at the run, that is a finding against W37-5b, not an adaptation to be
made on the day.**

---

## 4. The disclosure — what the maintainer's go-ahead authorises

Carried in full, as Ruling 66 §3 requires and as the maintainer asked: *"I want to read the run
I am authorising, not the run as planned."*

### 4.1 In one sentence

One squash-merged commit renames or rewrites most of the repository's governed documents, gives
every one of them a header and a number from a single global sequence, renumbers every
requirement id, dissolves four directory trees into six, and rewrites every citation in every
tracked file — after which the old paths and ids exist only in `REDIRECTS.csv` and `was:`
fields.

### 4.2 The size, by area rather than as one total

**1495 tracked files at `958cb7d`.** Broken down by what the migration does to each.

| The migration… | Files | Which |
|---|---|---|
| **rewrites a citation token in** | **954** | Every file matching NT-0019 §7 (d)'s pattern, measured through the shipped `LEGACY_FORM_PATTERNS` constant rather than a re-typed copy; 21 500 matching lines, 29 106 token hits. By tree: `docs/` 315 · `backend/` 217 · `frontend/` 143 · `packages/` 135 · `.claude/` 54 · `tests/` 53 · `scripts/` 19 · 7 root files · `examples/` 6 · `.github/` 3 · `deploy/` 2 |
| **stamps a header on** | **313** | 252 `.md` under `docs/` (265 less the 13 templates, exempt by path) + 46 `SKILL.md` + 8 agent files + 7 role charters. Overlaps the 954 |
| **moves, splits or deletes** | **231** | `docs/audit/` 46 · `docs/plans/` 146 · `docs/notes/` 20 · `.claude/notes/` 19, **plus 89 ruling headings split out of 36 of the plans** |
| **regenerates, never hand-edits** | **61** | `docs/contracts/`, rebuilt from `model-schema` then drift-checked |
| **does not touch at all** | **541** | 1495 − 954 |
| **must leave unchanged, by rule** | — | Files carrying a `VR-` catalogue id: **43 distinct ids**. D5 and G5 put these permanently out of scope; acceptance item (f) is the check |

**Two figures, and the verb on each is corrected from the superseded plan.**

- **673 requirement ids are renumbered** — not 710. The 710 figure is reproducible and is the
  count of *distinct requirement-family id tokens*, which the superseded §5.1 correctly labelled
  as such. Its §4.2 then said those 710 *"are renumbered"*, and **41 of them were `VR-` ids the
  same table guarantees untouched**. At `958cb7d` the renumbered population is **673** and the
  `VR-` population is **43**.
- **2446 marker citations are rewritten** — not 1988. The 1988 figure is the
  `backend`+`packages` count, and step 6 rewrites over `git ls-files`, *"nothing exempt"*. Of the
  extra **461**, **422 sit inside frozen dated plans** — the one class whose diff is not free but
  governed by Ruling 68's six-class permitted-diff predicate. **Each is a citation the run
  rewrites and the freeze predicate must then classify**, and that load is disclosed here rather
  than met on the day.

### 4.2a The corpus grows while the decision is open, and the growth is self-referential

| Pin | Tracked | Rewrite population | `git grep -c 'VR-DST-1'` | Ruling headings |
|---|---|---|---|---|
| `39ee30c` — the superseded plan's filing | 1447 | 930 | 109 | 72 over 29 files |
| `59bba94` — mid-session | 1473 | 938 | 120 | 82 over 32 files |
| `cc17404` — this plan filed as draft | 1493 | 952 | 123 | 87 over 35 files |
| **`958cb7d` — the draft lifted** | **1495** | **954** | **125** | **89 over 36 files** |

Every figure re-run at its own pin with the same command, so none was ever wrong; all four aged.
**The last two rows are four merges apart and every column moved.**

**The sharpest instance, because it is measurable and was caused by the discussion itself.** The
`Ruling A<n>` token population stood at **21 across 5 files** at `b648c22` this morning. At
`cc17404` it was **43 across 7**, and at `958cb7d` it is **44 across 8** — every one of the 23
new tokens in a document written *about* the A-series: two derivations, two ruling records, and
an obligations list. **A
governed corpus grows by being governed.** It is the same mechanism §5.3 of the obligations list
measured on the `VR-DST-1` baseline, and it is the reason the figures above carry their tree in
every row.

**Presented as a trend, not as an argument for haste.** Later is measurably larger. Nothing here
says the decision should be quick.

### 4.3 The enlargement Ruling 66 requires

Ruling 66 makes the creating-instrument set **a criterion, not a list**: every instrument whose
output is checked by checks 30-39 from the migration commit lands in W37-6. The derivation is
**thirteen members and nine explicit exclusions**, carried unchanged from the superseded plan's
§6, which this revision does not reopen. Ruling 85 has since ruled that NT-0019 §8's stage list
is sequencing and S3 a residue rather than a fixed list, which is what makes that enlargement
consistent with §8 rather than an unrecorded re-cut.

### 4.4 What becomes irreversible

- **Every document's path changes.** Any link held outside this repository — a bookmark, a chat
  message, a local note — pointing at `docs/notes/…`, `docs/audit/register.md` or
  `docs/plans/2026-…` breaks. `REDIRECTS.csv` records every old-to-new mapping *inside* the
  repository; it cannot fix a link held elsewhere.
- **Every requirement id changes.** A module-qualified id becomes a bare number. Anyone holding
  one in their head, in a notebook, or in a local file outside the repository is holding a
  retired one. `was:` and `REDIRECTS.csv` make the translation mechanical, not automatic.
- **`docs/audit/` ceases to exist.** Its register, closure records, plan reviews, work READMEs,
  checklists and findings become four other trees.
- **The commit is squash-merged and the branch auto-deletes.** Ruling 68 computed (g) as a
  property of the *script* over its own output precisely so the evidence survives that deletion:
  it is re-derivable at any later date from the recorded merge-base, because `migrate` is
  deterministic and idempotent. **The recorded merge-base SHA is load-bearing evidence, not a
  courtesy.**
- **`git blame` and `git log --follow` degrade** across every moved file. Rename detection
  handles a pure move; a move plus a header stamp plus a citation rewrite in one commit is
  detected as a rename only above git's similarity threshold. **This is not recoverable later.**

### 4.5 What does not change

- **No product identifier moves.** `VR-*` catalogue ids, artifact ids, job kinds and any string
  persisted or asserted as data are out of scope; acceptance item (f) is the check.
- **Nothing outside the repository is touched** — by construction, not only by rule.
- **No body line of a frozen file changes.** Splits preserve every line; stamps add lines;
  rewrites change reference tokens only. Item (g) is the check, and Ruling 68 makes it a closed
  enumeration with **no pass-through** for a hunk the filter cannot classify.
- **Nothing in NT-0019 §1 is edited.** §1 stays byte-identical to the maintainer's original.

### 4.6 The window this closes, and the one it opens

**Closes:** the DP-1 window — a document created between the migration and W37-7 under a retired
grammar, which checks 30, 31, 33 and 36 would red. Ruling 66 established that this window is
occupied by construction: executing W37-7 at all creates its own leaf plan and its own ledger
inside it.

**Opens, and is disclosed rather than fixed here:**

- Between this commit and W37-9, `CLAUDE.md` states at two sites a permanence rule the
  repository has just broken. The map plan assigns both to W37-9; a known interval, not an
  oversight.
- Between this commit and W37-7, `git-hygiene` teaches a branch and PR-title grammar naming work
  keys that no longer exist after the roadmap restructure.

### 4.7 What the go-ahead does not cover

NT-0019 §7 runs **(a) to (k)**, not (a) to (h). Items (i), (j) and (k) belong to later slices —
(i) to the Work's closure record, (j) and (k) to W37-11. **Accepting this run is not accepting
the Work close**, which is a separate dated line under `CLAUDE.md` §12.

---

## 5. Risks this plan carries into the run

Each is stated as a property rather than a count, because a count is stale before it merges —
including the count of risks, which is why this sentence no longer carries one.

**5.1 Checks 30-39 meet a corpus for the first time inside this commit.** Re-measured at
`958cb7d`, unchanged across every pin this plan has been written at: four of the ten examine exactly one document — the same one — and six examine zero.
W37-4's ten broken-input proofs exercise each check on a fixture, which is the right proof that
a check can fail; it is not the same as running over the whole tree. **A large first-run failure
list inside this PR is the expected case, not a sign something went wrong, and nobody narrows a
check to shorten it.**

**5.2 Heading-level reasoning is unsafe over this corpus, and one document proves it.**
`docs/audit/plan-reviews.md` is 2816 lines and contains **exactly one** level-2 heading. Any
tool reasoning about *"the `##` section"* over that file is operating on a structure the file
does not have: a rule reading from the `##` to the next `##` consumes the rest of the document.
The migration is full of heading-level reasoning — the multi-ruling splitter, the closure-record
splitter, the plan-review splitter, and the census that counts them.

**The property, which is what a check should assert:** for every heading-split source, a record's
body contains no heading at the split's own level, and every heading in the file is a record,
derivably body, or a declared exception. **Violation: a split whose output body contains a
heading at its own level.** This is Ruling 83's structural invariant (its option (d)), and §5.2
is the argument that it is not optional.

**5.3 A citation can be rewritten correctly and still point at the wrong place.** Fourteen
line-number citations point into the two files being split. The legacy-form sweep **detects**
them, because the `docs/audit/` prefix matches — so acceptance item (d) is satisfied by a rewrite
that changes only the path. But line 1994 of a 2816-line file is not line 1994 of the record it
lands in. **Detection is not repair**, and a citation that resolves to a file and points at the
wrong place in it is worse than one that fails loudly. **Placement is DP-B and no task here
builds against it.**

**5.4 One docstring is stale in two independent ways, and both misled a reader.**
`is_vendored`'s docstring in `scripts/_docid.py` is careful, well-sourced, and wrong twice over.

**Staleness one — it presents a ruled question as open.** It describes the `LICENSE` criterion
as *"a known, reported gap"*, names Ruling 69 as having resolved it, and instructs: *"Apply the
ruling once `#563` merges; until then this implements the rule exactly as published."*
**`#563` merged.** The sentence is now an accurate description of a state the repository has
left, sitting directly above code that still implements it.

**Staleness two — its count predates the derivation that changed it.** The docstring reads
*"nine of the 28 ruff-excluded skills carry an NT-0019 §5.4 change row, **two of which**
(`writing-plans`, `subagent-driven-development`) are creating instruments Ruling 66 places
inside W37-6's own migration commit"* (`scripts/_docid.py:323-325`). That was right when
written, against Ruling 66's floor of seven. The superseded plan's §6.2 then **derived** the
set, adding `writing-skills` (member 11) and `brainstorming` (member 12) — both ruff-excluded.
Checked at `f4cbbb7` against all thirteen members: **four, not two.**

| Ruling 66 member | Skill | In the ruff exclude list |
|---|---|---|
| 1 | `writing-plans` | yes |
| 2 | `subagent-driven-development` | yes |
| 11 | `writing-skills` | yes |
| 12 | `brainstorming` | yes |

**Neither staleness changes what row 9 obliges, and the second does not threaten the equality
form.** Ruling 69 §2 part 3: *"The exemption reaches only the blanket passes… Exempt from the
blanket pass is not the same as never touched: a named row in §5.4 is a deliberate edit and is
applied."* Membership exempts the files **beneath** a `SKILL.md`, never the `SKILL.md` itself —
and a creating instrument's instruction *is* its `SKILL.md` prose. All four receive their
Ruling 66 edit. Ruling 69 §4 acceptance item 3 is the proof: after this commit those
instruments must **differ** from their merge-base, and being unchanged is the violation.

**Why this sits in the risk section rather than in a correction.** The shape of row 9's fix was
argued from this docstring rather than from Ruling 69 **twice in this Work, by two different
readers** — a lead's instruction to an executor, and a draft of §7 of this plan. Both times the
docstring was read as current and the ruling it names was not opened. Both were caught by
someone reading the ruling and refusing the instruction with a citation, which is the behaviour
that worked and the only thing that did.

**A description of a superseded state is a live hazard in a migration this size.** It reads as
current, it sits where the reader is already looking, and nothing checks it. **The property a
check should assert:** no comment in the migration path names a merged ruling in the future
tense, and no comment states a count the corpus can contradict. *Violations: a comment citing a
merged ruling as pending; a hard-coded count of a derived set.* Both are greppable, and the
superseded plan's §7.9 code-rewrite task is the natural sweep point. **If the walk-through finds
others, each is named in the ledger rather than fixed silently.**

---

## 6. What is carried unchanged, and what is held

**Carried unchanged from the superseded plan, which remains readable and is not edited:** §5 (the
measured baseline's method and its command table), §6 (Ruling 66's derivation — thirteen members,
nine exclusions), §7 (the thirteen-task list), §8 (the three W37-4 deferrals), §9 (register
finding F68) and §10 (the sixteen findings). Where a figure in those sections is quoted, **§4
above supersedes it**; where a method is described, the method stands.

### 6.1 The plan-review split — the task text DP-A was holding

`docs/audit/plan-reviews.md` yields **twelve records**, not eleven, and the twelfth is not a
review.

| Output | Count | Fields |
|---|---|---|
| `CR-`, `kind: review` | 11 | one per `Plan review N` heading; `created:` each review's own date; `owner: planner`; `status: active` |
| `RFC-`, `kind: process` | 1 | the `Pending proposals` container, lines 1155-1232; `created: 2026-08-29`; **`owner: maintainer`**; `status: closed`; `was:` `docs/audit/plan-reviews.md` |

**Four properties the executor asserts, each a violation that must become detectable.**

1. **Twelve records, and the twelfth is the container.** *Violation: eleven records, or a
   twelfth of any family other than `RFC-`.* The `$`-anchor fix landed in `#602` and
   `_discover_plan_reviews` now returns 11; the container is the addition this ruling requires.
2. **The three `###` headings inside the container stay body.** Ruling 82 item 2 forbids
   widening the review pattern to reach them at any heading level. *Violation: a `CR- kind:
   review` minted from `Candidate A`, `Candidate B` or `Also carried`, or any of the three
   dropped* — which is also the standing acceptance item in
   [`2026-09-02-w37-6-twelve-non-close-records-derivation.md`](2026-09-02-w37-6-twelve-non-close-records-derivation.md),
   satisfied in both directions at once because the section containing them becomes one record.
3. **The section is closed at the next record heading, never at the next `##`.** The file
   contains exactly one level-2 heading (§5.2), so a rule reading to the next `##` consumes the
   rest of the document. *Violation: a container record whose body contains a `Plan review`
   heading.*
4. **All three citations of the container resolve, and 2645 keeps its attribution.** Lines 1994
   and 2121 are Plan review 9's; **line 2645 is Plan review 11's**, and it cites the container
   as a normative source — *"the 'Pending proposals' section's own rule"*. *Violations: any of
   the three unresolved after the rewrite; or 2645 resolving to the `CR-` minted from Plan
   review 9.* The phrase *"both above in this document"* at 2121 becomes false under any
   placement and is replaced, not merely re-pointed.

### 6.2 Still owed at the ask, and it is not held by anything here

**One more figure pass**, at the tree the go-ahead is requested against. The maintainer's
condition 6 is a property of that day, not of this document, and §4.2a measures why: four
merges moved every column. *Violation: a disclosure quoting a figure from a tree other than the
one the run will start from.*

---

## 7. One correction carried, against a document that is frozen

**No filed document is edited** (`CLAUDE.md` §2); this is where the correction lives.

### 7.1 The vendored gloss and the vendored detector — where they actually diverge

NT-0019 §1.5 reads: *"A vendored skill (`planning-with-files`, `ui-ux-pro-max`, `graphify`,
`systematic-debugging`, the `vue-*` skills — anything shipping its own `LICENSE`) …"*

Measured at `958cb7d`, of the 46 skill directories exactly **two** carry their own `LICENSE`:
**`planning-with-files` and `ui-ux-pro-max`** — and both are **named in the parenthesis, first
and second**.

**The divergence is therefore partial and one-directional.** Ruling 69 §1's verification table
states it in the same direction and in the same terms: *"The criterion misses three of the five
names in its own parenthesis — **Confirmed.** `graphify`, `systematic-debugging` and every
`vue-*` skill ship no licence file."* **The gloss over-names by seven skills; it does not fail
to name the two that qualify.**

Recorded because the looser reading — that the gloss and the detector do not overlap at all — is
easy to reach from the same evidence, was reached twice in this Work, and is false.

**This changes nothing about what row 9 obliges.** `_VENDORED_SKILLS` is a hand-seeded declared
constant listing the 28, reconciled by a gate check that asserts equality with the ruff exclude
list restricted to `.claude/skills/` — Ruling 69 §2 part 2, where the ruff list is *"not the
criterion; it is the independent second witness."* The obligations list's wording, *"a declared
constant reconciled against the ruff exclude list, drift loud"*, is that mechanism, and §5.4
records why it briefly looked otherwise.


---

## Self-review

- **Every id cited individually**, never as a range: Rulings 66, 68, 73, 81, 83 and 85 are each
  named where they bind.
- **Item 11 is carried in this document's own text**, because the ruling that amended it cannot
  be applied to a frozen file, and an executor reading only the frozen file applies a weaker test.
- **Every figure carries its tree**, and §4.2a shows the same figure at three pins so a reader
  can see the direction rather than trust a single number.
- **Properties, not counts, wherever a check will later verify the claim** — §3's three rules and
  §5's three risks are each stated as a violation that must be detectable.
- **The frozen plan is not edited**, and this document supersedes rather than replaces it.
- **The correction against a frozen document lives in §7**, never as an edit to it, and it
  states the wrong reading it displaces rather than only the right answer — a correction
  that does not name the wrong reading leaves it available.
- **A second §7 entry was drafted and removed before filing**, because Ruling 69 §2 part 2
  had already ruled the mechanism it proposed to clarify. §5.4 carries what that episode
  actually showed, which is about docstrings rather than about row 9.
- **No acceptance line.** `status: active` records that the plan's own blocking row is
  resolved, and nothing more. **The maintainer's go-ahead is a separate gate and is not given**;
  §6.2 states what is still owed before it is asked for.

---

## Corrections after filing

**2026-09-02 — §4.2's three marker figures are measured and correct; its *contrast* runs
between two different units, and the caveat that said so did not survive from the source
document.**

Raised by the lead while establishing the provenance of `2446` for the go-ahead ask, and
recorded here rather than edited into §4.2, which is kept verbatim above as the record of what
the disclosure said when it was read.

**The figures are measured, not derived.** All three come from one command at `cc17404`, the
tree §4.2 names, and all three reproduce to the digit:

```
git grep -o '@pytest\.mark\.req(' cc17404 | wc -l                      -> 2446
git grep -o '@pytest\.mark\.req(' cc17404 -- backend packages | wc -l  -> 1985
git grep -o '@pytest\.mark\.req(' cc17404 -- docs/plans | wc -l        ->  422
```

`461` is `2446 − 1985`, arithmetic on two measured values. §4.2's sentence *"step 6 rewrites
over `git ls-files`, 'nothing exempt'"* is the **justification for the repo-wide scope**, not
the method by which the number was obtained; it reads as the latter, and that is a defect in
the prose rather than in the figure.

**The defect: the contrast and the subtraction use different units, three apart.** §4.2 says
*"2446 … not 1988"* and then *"Of the extra 461"*. `2446 − 1988 = 458`. The `461` is against
**1985**. Both operands reproduce and both are right — `1988` is the count of **lines** matching
the bare string `pytest.mark.req` in `backend`+`packages`; `1985` is the count of **decorator
occurrences** in the same scope. The three-apart difference is three lines that mention the
marker without being one. **A reader of §4.2 alone has no way to see the switch.**

**The caveat existed and was lost in transfer.**
[`2026-09-02-w37-6-outstanding-obligations.md`](2026-09-02-w37-6-outstanding-obligations.md)
§5.2 carries it explicitly — *"1988 is a line count; 1985 decorators sit on 1988 matching lines.
Both reproduce; neither is the repository-wide figure."* It did not survive into §4.2. **Read
§4.2's marker paragraph as *"2446 … not 1985"*.**

**And `422` is correct rather than conservative.** In one unit at `cc17404` it is **422**
decorators against **457** bare-string matches under `docs/plans`; the extra 35 are prose
mentions of the marker, not citations the run rewrites. An earlier reading had the figure
understating the frozen-plan load Ruling 68's predicate must classify. It does not — it is the
right number for that load.

**Why appended rather than edited.** This plan is `status: active`, and `document-ids.md` §1.7
puts the freeze at that transition — the same reading under which it was editable while
`draft`. Editing `1988` to `1985` in place would erase what the disclosure said while the
maintainer was reading it, which is the record `CLAUDE.md` §0 exists to protect. The shape is
`CLAUDE.md` §5's, applied to prose rather than to an id: **append, mark superseded, never edit
away.** Precedent: `eb19e3f` (`#554`) added a `## Corrections after filing` section to
[`2026-09-01-nt-0016-landing-package.md`](2026-09-01-nt-0016-landing-package.md), filed one
commit earlier, on the same principle.
