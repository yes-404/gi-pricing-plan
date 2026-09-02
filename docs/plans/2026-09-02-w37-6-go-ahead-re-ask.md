# W37-6 — the migration run: the go-ahead re-ask

**Date:** 2026-09-02 · **Tree:** `[SLOT-0]` · **Author:** the lead ·
**Status:** awaiting the maintainer's dated line (§10)

**What this is.** The one document. The maintainer withheld W37-6's go-ahead twice on
2026-09-02 — first with six conditions
([`…-go-ahead-withheld.md`](2026-09-02-w37-6-go-ahead-withheld.md)), then, when those were
discharged, with four more and a slice
([`…-go-ahead-ask.md`](2026-09-02-w37-6-go-ahead-ask.md) §8). The four are quoted verbatim in
§1 and scored there. **This document exists so that the line in §10 is an informed one, and it
authorises nothing.**

**What it supersedes, and on whose instruction.** It supersedes
[`2026-09-02-w37-6-go-ahead-ask.md`](2026-09-02-w37-6-go-ahead-ask.md) **as the ask** — by that
document's own closing sentence, which is the maintainer's disposition recorded at the time:
*"This ask is therefore closed, not withdrawn. It is superseded at the re-ask by a document
built to those four conditions; §3's figures stay pinned at `64f63ee` as the record of what was
disclosed on the day the question was put."* That document is **not edited** (`CLAUDE.md` §2).
Its **Addendum A** (the seven defective acceptance items W37-6 applies) and **Addendum B** (four
abort points, not three; and the untreed line numbers) are **carried forward and re-run here**,
which is condition 2 — see §7. Nothing in it is retired by being superseded; its figures are
correct at `64f63ee` and are re-derived, not corrected, in §6.

**Read §2 and §5 before §10.** §2 is the one thing about W37-5c that a summary of it would
soften. §5 is the condition the four do not name and the map plan does.

---

## Acceptance Standard

The violation this record must make detectable: **a W37-6 go-ahead given against a document
that reports the run as able to complete when it cannot, or against figures inherited from a
tree the run will not start from.** Each item is stated as the violation, not the pass.

**That first clause widened on 2026-09-02 and the widening is the point.** It read *"reports the
preconditions as cleared when a fifth abort survives them"* until the fifth was fixed and a
**sixth** failure appeared behind it, **past the first write** (§2.6). *"The abort points are
cleared"* and *"the run can complete"* were never the same claim, and a standard written against
only the first would have passed a document asserting the second.

1. **The fifth abort point is stated in the closure record's own words, not in a summary of
   them.** *Violation:* this document saying "the abort points are cleared" anywhere without
   the qualifier `satisfied literally and not sufficiently` attached to condition 3 — which is
   the phrase [`W37-5c/README.md`](../audit/work/W37-5c/README.md) chose, and the one a
   paraphrase loses first.
2. **The four preconditions keep the distinction their closure record drew.** *Violation:*
   F87, F88, F90 and F92 presented as one class. Three are defects the slice **found** in work
   that predates it; F92 is a deferral the slice **made**. A document that blurs them flatters
   the work.
3. **Every figure carries its tree, its corpus and the predicate it counted with**
   (`CLAUDE.md` §13, as amended 2026-09-02). *Violation:* a count here that a reader holding
   none of the author's context cannot re-run — which is the defect conditions 1 and 2 exist to
   catch, reappearing inside the document that discharges them.
4. **Every tree-pinned figure is a marked slot until it is measured at the final tree.**
   *Violation:* a `[SLOT-n]` marker replaced by a figure measured at any tree other than the one
   named in §Header, or `[SLOT-0]`–`[SLOT-3]` or `[SLOT-5]` left unfilled when §10 is signed.
   §6.0 is the register of them. **`[SLOT-4]` is the deliberate exception** — the gap checks are
   filled by the executor in the session that runs the migration and are *never* filled in this
   document, per item 5. **And `[SLOT-5]` has a second violation of its own:** a figure written
   into it on relay rather than from its author with its predicate, which is the defect §8.2
   records happening once already in this document's own briefing.
5. **The gap is named as a condition with a re-runnable check, never as a date.** *Violation:*
   this document recording a gap as *established*, which turns a volatile live condition into a
   stale claim an executor then reads as satisfied — the failure the frozen leaf plan's §1
   refuses by name.
6. **§10 is empty until the maintainer writes it, and no other section records a go-ahead.**
   *Violation:* an approval inferred from §9's recommendation, or a date in §10 in any hand but
   the maintainer's.
7. **The mechanism sentence's remedy is corrected, not just its symptom repeated.**
   *Violation:* this document quoting *"two instruments reach one population and only one
   consults the register"* without §2.2's dated correction attached — because a maintainer
   reading the quotation alone reaches for the register, and **importing the register is the
   wrong repair**: it answers *can this file carry a header at all* where the abort asks *has
   this migration already stamped it*. A second violation of the same item: **§2.4's `[SLOT-3]`
   filled against F88 limb 1's falsifiable clause alone**, which §2.5 shows is destructive when
   met naively.
8. **No frozen plan is edited by the branch carrying this record**, and no dated append to the
   active plan is made to agree with a figure re-derived here. *Violation:* either leaf plan,
   or the superseded ask, modified by this branch. The check is
   `git diff --stat origin/main...<this branch> -- docs/plans/2026-09-02-w37-6-migration-run-leaf-plan.md docs/plans/2026-09-02-w37-6-migration-run-leaf-plan-v2.md docs/plans/2026-09-02-w37-6-go-ahead-ask.md`,
   which must be empty.

---

## 1. The four conditions, scored

**Verbatim, from [`…-go-ahead-ask.md`](2026-09-02-w37-6-go-ahead-ask.md) §8:**

> *"§3 and §4 re-derived at that tree, the addendum merged and re-run, F80–F82 shown cleared by
> execution. Then I read one document and write one line."*

…prefaced in the same instruction by *"Re-ask when 5c is closed"*, and joined by a later
instruction that **the re-ask names the gap**.

| # | Condition | State | Where |
|---|---|---|---|
| 0 | **W37-5c is closed** | **Both acts done; neither record says so** — see §8.1. The audit is clean and the lead's merge landed (`c888b61`, PR #647). The closure record's own Sign-off row still reads *"(the lead's merge — pending)"*, and `docs/roadmap.md` carries no `W37-5c CLOSED` line where it carries one for W37-5b | [`W37-5c/README.md`](../audit/work/W37-5c/README.md) |
| 1 | **§3 and §4 re-derived at that tree** | **`[SLOT-1]`** — deliberately not yet run. §6 states why it runs once, late, and carries the slot register | §6 |
| 2 | **The addendum merged and re-run** | **Merged** — Addenda A and B are on `main` inside the superseded ask (`c888b61`). **Re-run: `[SLOT-2]`** | §7 |
| 3 | **F80–F82 shown cleared by execution** | **Satisfied literally and not sufficiently.** All three gaps, across four guards, are FIRE→PASS on the real corpus. A **fifth** abort point survives and was never touched by the commit that cleared them | **§2** |
| 4 | **The re-ask names the gap** | **Named as a condition with its check, not as a date** — and one of the map plan's three limbs no longer measures what it was written to measure | **§5** |

**Condition 3 is the one this document is organised around**, because it is the one where the
literal answer and the useful answer differ.

---

## 2. The sentence W37-5c's closure record leads with

**Quoted rather than summarised**, from [`W37-5c/README.md`](../audit/work/W37-5c/README.md),
under the heading *"The one sentence this record exists to make unambiguous"*:

> **W37-5c did not achieve "the run no longer aborts."**
>
> Four of Addendum B's abort points are cleared and verified by execution. A **fifth**,
> `_discover_vendored_skill_manifests`, still fires on the real corpus and was **never touched
> by `544b90c`**. The commit subject claiming otherwise is true of its three named gaps and
> **false of the run**. The W37-6 re-ask condition *"F80–F82 shown cleared by execution"* is
> **satisfied literally and not sufficiently**.

`544b90c`'s subject is *"fix(scripts): write the missing discovery for F80, F81 and F82 —
migrate() no longer aborts (#629)"* (`git log -1 --format='%s' 544b90c`). **The second half of
that subject is false of the run and cannot be amended**, which is why it is quoted here against
an amendable document rather than left to be read from `git log`.

### 2.1 The five, measured by execution

Reproduced from that record's §2, which called each guard **with `migrate()`'s own arguments
taken from its own call block** and **never called `migrate()` itself** — its write is the
irreversible commit. Both columns are the real corpus; the "before" side loads
`git show 544b90c^:scripts/doc-id.py`. Guards are named **by function**, which is the durable
form (Addendum B §B.2: eight tracked documents carry `doc-id.py` line numbers measured at a tree
none of them names).

| # | Guard | Gap | Before `544b90c` | At `6e35b9c` |
|---|---|---|---|---|
| 1 | `_check_multi_ruling_files_not_silently_unrecognised` | F81 | FIRE | **PASS** |
| 2 | `_check_plan_reviews_heading_census` | F80 | FIRE | **PASS** |
| 3 | `_check_headed_split_file_not_silently_unrecognised` | F80, second guard on the same heading | FIRE | **PASS** |
| 4 | `_check_requirements_not_silently_unrecognised` | F82 | FIRE | **PASS** |
| 5 | **`_discover_vendored_skill_manifests`** | **F88 limb 1** | **FIRE** | **FIRE — unchanged** |

**Rows 1–4 are Addendum B's four and all four are genuinely cleared.** Row 5 is not Addendum
B's fourth — that is row 3, and it is cleared. Row 5 is a **fifth**, of a different kind: not a
`_check_*` guard but a `_discover_*` function that raises `HeaderError` out of discovery before
the stamp loop is entered.

**And five is the whole list.** A second, independent replay of **every one** of `migrate()`'s
pre-write calls — not only the five named — found no sixth. That matters because the four came
from Addendum B's table, and a table is a list someone wrote; the replay is the check that the
list is complete. The two verifications differ in interpreter (3.12.13 under `uv` against the
live worktree; system 3.13.5 against a read-only `git archive` snapshot in a separate directory)
and agree on the PASS/FIRE pattern, the error text and the three named manifest files.

**The abort is pre-write, so a run stops rather than half-migrating.** No write appears in
`migrate()`'s body between its own definition and `_write_document_drafts`, and none of the 24
functions it calls in that span contains one — searched for `write_text`, `.unlink(`, `.mkdir(`,
`.rename(`, `shutil.`, `.touch(` and `open(…, "w")`, **with a positive control**: the same
pattern against `_write_document_drafts`, a known writer, returns 3 hits. So the predicate fires
when there is something to find. **The irreversible commit is not at risk from row 5. What is at
risk is the run completing at all.**

**Both of those sentences are scoped to the pre-write span, and that scope is the whole of what
they claim.** *"Five is the whole list"* was established by replaying `migrate()`'s **pre-write**
calls; *"not at risk"* was established by finding no writer in the **pre-write** span. Neither
says anything about what happens after `_write_document_drafts`. **Clearing row 5 moves the
failure past the first write, and there is one there** — §2.6. The replay was complete over its
own population; the population was the right one for *"what stops the run before it starts"* and
the wrong one for *"can the run complete"*, and no number of re-runs of it could have found the
sixth.

### 2.2 The mechanism — two instruments reach one population and only one consults the register

This is the most useful sentence W37-5c produced, and it is the answer to *how did a fifth guard
survive a slice cut to clear abort points*. In the closure record's own words:

> item 3's exemption serves those three files in `audit-docs.py` and **not** in `doc-id.py` —
> one of two instruments reaching one population.

W37-5c's item 3 was *"the three unparseable vendored manifests."* It was **delivered against the
check-35 limb and not against the migration limb**. `ffdd54c` + `24193dd` + `359936b` put
`.claude/skills/create-adaptable-composable/SKILL.md`,
`.claude/skills/planning-with-files/SKILL.md` and `.claude/skills/vue-best-practices/SKILL.md`
into `scripts/audit-docs.py`'s `UNSTAMPABLE_EXEMPTIONS`. That exempts them from checks 30–39.
**It does not stop `migrate()` aborting on them**, because the abort is a `_docid.parse_header`
call inside `scripts/doc-id.py`'s discovery, which never consults that register.

**Two mechanisms, one population of three files, and the slice built one of them.** F83's
exemption ruling, filed the same day, says the same thing from the other side: the exemption
does not by itself let a run proceed
([`2026-09-02-w37-vendored-exemption-ruling.md`](2026-09-02-w37-vendored-exemption-ruling.md)).

**Dated correction, 2026-09-02 — the sentence above is right about the symptom and points at
the wrong remedy, and the quotation is kept rather than rewritten.** It is a verbatim quotation
of a merged closure record, so it is not edited; what is corrected is the repair a reader
naturally reaches for from it. Found by the executor fixing the fifth abort point, by reading
the register's own declaration rather than a description of it. **Two things are wrong with
"import the register into `doc-id.py`":**

1. **`UNSTAMPABLE_EXEMPTIONS` was never made public for `doc-id.py`.** Its declaration binds it
   to one named consumer, and that consumer is inside `audit-docs.py`. Verbatim, from the
   comment block above the constant at `origin/main`: *"**NOTE FOR W37-6:** when
   `_ID_SCOPE_ROOTS` widens to the whole corpus, **check 30 must consult
   `UNSTAMPABLE_EXEMPTIONS`** or it will fail on all 65 of these. … `UNSTAMPABLE_EXEMPTIONS` is
   public for exactly that consumer."*
2. **The two instruments are not asking one question**, so importing the register would
   substitute a *different* wrong predicate and look like a fix. The register answers **can this
   file carry a header at all** — a stamp-set question, F83's. The aborting call answers **has
   this migration already stamped it** — idempotency. **Conflating those is the defect.**

**The remedy is one classifier plus a reconciliation test, not a second register consumer** —
and the module already contained the right instrument. `_front_matter_state`
(`scripts/doc-id.py`) returns `"none"`, `"stamped"` or `"foreign"`, decides `"stamped"` on
`family:` — *"the one key every family's template carries and no harness block does, a positive
test for this migration's own output"* — and is deliberately textual rather than a
`parse_header` call because, in its own docstring, *"a classifier that crashes on the very files
it exists to classify cannot report them."*

**It was written by the same slice, for this exact failure, and one discovery function predated
it and was never converted.** `git log --oneline -S'def _front_matter_state' origin/main --
scripts/doc-id.py` returns exactly one commit: **`47eb2ba` (#639), W37-5c's own item 2**. At
`origin/main` the classifier has **one** caller, inside the Reference-stamp path, while
`_discover_vendored_skill_manifests` still decides with `if _docid.parse_header(skill_md) is not
None: continue  # already stamped`. **Its own docstring names it as the singular case that most
needed the classifier** — *"the one discovery function in this module that cannot infer 'already
migrated' from a legacy shape being absent, because stamping does not move or rename this
file"* — and it is the one that did not get it.

**So the defect was not a wrong count; it was a bucket with no name.** `parse_header is not
None` is a two-way test over a three-way population: it collapses `stamped` and `foreign` into
one branch, and `foreign` is the bucket that had no name. **A maintainer reading only the
quotation above would reach for the register, which is the wrong repair.**

### 2.3 What that means for condition 3

The condition names F80, F81 and F82. **All three are cleared, on the real corpus, by
execution.** The condition is met on its own words.

**It is not met on its purpose.** The maintainer withheld the go-ahead over abort points and cut
a slice whose stated criterion was the maintainer's own — *"everything that **stops or blinds**
the run and is provable on broken input outside it."* A fifth thing that stops the run survived
that slice. **The maintainer is entitled to know that, and to know how it was found.**

### 2.4 How far the run gets — `[SLOT-3]`, and it is a distance rather than a yes

`[SLOT-3]` — **how far a real `migrate()` run gets at this document's tree.**

**The slot is deliberately wider than "the fifth abort's disposition", because the question has
changed.** Once the fifth is cleared the run reaches its first write, and what a maintainer is
asked to authorise is no longer *"a run that stops before it starts"* but something else. Filled
at the final tree with **one of three** states — the third did not exist when this document was
first drafted:

- **Does not start.** The fifth abort still fires; a go-ahead authorises a run whose first act
  is an abort. §9 recommends against.
- **Starts and does not complete.** The fifth is cleared and the run reaches
  `_write_document_drafts`, then fails — **a partial migration, not a clean abort.** This is
  §2.6, and it is the state the tree was in when this slot was last checked. **A go-ahead given
  in this state authorises a run that leaves the repository in neither shape.**
- **Completes.** The run reaches the end of `migrate()` on the real corpus.

**In every case the fifth's own clearing is recorded the same way:** *the fifth abort point was
found by the W37-5c close audit, not by the slice that was cut to clear abort points* — fixed
after the fact, in a separate change, outside the irreversible commit. Red-before / green-after
on the real corpus, with the same execution discipline §2.1 used — and **against a test the F88
limb-1 clause alone does not supply**, for the reason §2.5 gives: the classifier is the sole
decider of "already stamped", and a reconciliation names any manifest it cannot place.
**Satisfying limb 1's clause is necessary and is not sufficient.**

**Either way the finding stands as recorded.** The close audit found it; the slice did not.

**And the distinction between the first two states is the one the maintainer is entitled to have
drawn for them: an abort is honest; a partial migration is not.** A run that stops before
writing leaves a repository someone can look at. A run that writes and then raises leaves one
that has to be **discovered**. §2.6 states the crash state precisely, and it is **narrower than
"a corpus in neither shape"** — that phrase was in an earlier draft of this section and is
withdrawn, with the reason at §2.6.

**The withdrawal, because a retraction that only removes the claim removes the record of it.**
The map plan's *"a partially-applied rename set is a corpus in neither the old shape nor the new
one, and the gate cannot tell the two apart"* is written about **splitting W37-6 across
executors**, which is forbidden, and it carries an implication of irrecoverability that **the
measured crash state does not support** (§2.6). Half of it transfers — the gate cannot tell the
two apart — and half does not. **Borrowing the sentence imported the half that is false here.**

### 2.5 A falsifiable clause that is destructive when met — a failure shape with no precedent here

**This is the sharpest thing produced by fixing the fifth abort point, and it generalises past
it.** Found by the executor, not by this document.

F88 limb 1's falsifiable clause reads: *"discharged when `_discover_vendored_skill_manifests(ROOT)`
returns without raising **and** returns the manifests that have not been stamped by *this*
migration rather than the ones whose front matter fails to parse — **proven by a manifest
carrying foreign front matter being returned, not skipped**."*

**Wired naively — widen the predicate so foreign front matter is returned rather than skipped —
that clause is satisfied and the repository is damaged.** Re-derived at `origin/main` against a
read-only `git archive` snapshot, through the shipped symbols (`_is_vendored_skill_manifest`,
`_front_matter_state`, `_docid.parse_header`), never the working tree:

| At `origin/main` | Count |
|---|---|
| `.claude/skills/*/SKILL.md` | **46** |
| of those, `_is_vendored_skill_manifest` true | **28** |
| of the 28, `_front_matter_state` == `"stamped"` | **0** |
| not stamped, `parse_header` returns a `Header` | **25** — today skipped as *"already stamped"* |
| not stamped, `parse_header` raises | **3** — today **aborts the run** |
| **a naive limb-1 fix returns** | **28** |

Each returned path then goes through `migrate()`'s own loop, which is a **prepend, not a merge**:

```
skill_md.write_text(header + "\n" + body, encoding="utf-8")
```

Every one of the 28 already opens with the harness's own `---` block. **So the naive fix writes a
second front-matter block above the first, on 28 vendored files, inside the irreversible
commit** — and F92 already establishes why that is not recoverable by re-running: `parse_header`
reads `lines[0] == "---"` to the closing `---`, so a file has exactly one block and a stamp must
be **merged**, which is W37-6's own §7.1 Task 1 and was deliberately deferred.

**Worse than the abort it was written to fix, irreversible, and it passes its own acceptance
test.** The abort is a clean pre-write stop (§2.1). This is a write.

**Why the maintainer should see it rather than only the fix.** Every finding in this effort
carries a falsifiable clause, and this repository's whole discipline for trusting a fix is that
the clause be met and proven on broken input. **A clause that causes harm when met is a hole in
that discipline, not in this one finding.** It is a different shape from anything the acceptance-
item sweep's taxonomy can express: not vacuous (it fires), not invalidated (nothing broke it),
not indicative (it is a genuine check), and not the `WITHDRAWN` class Addendum A §A.4 had to add
for an item wrong in both directions. **This one is right in both directions and dangerous
anyway** — it correctly describes the end state and says nothing about the path, and the path is
where the damage is.

#### The class, named — `DESTINATION_ONLY`

**An acceptance item that specifies a correct end state, is satisfiable, and is silent about the
route — so satisfying it literally can do harm the item cannot express.**

**The obvious tell over-collects, and saying so is what makes the class usable.** *"It names what
must be true after and nothing about what must not happen on the way"* describes **almost every
acceptance item in this repository**, because `CLAUDE.md` §13 requires an item to be stated as
*a violation that must become detectable* — a statement about the end state, by construction.
**Destination-only is the house style, not a deviation.** So the class cannot be *"names a
destination"*. It is **"names a destination whose cheapest route is destructive"**, and the
narrowing is three conjuncts, all three true of F88 limb 1:

1. **The clause is the acceptance test for a change to the very code path it describes** — not an
   observation over a corpus that some other change must preserve. Limb 1's clause is the test
   for rewriting `_discover_vendored_skill_manifests`.
2. **A cheap, natural implementation satisfies it and is harmful.** Widening the predicate is the
   one-line reading; it returns 28 and the writer prepends.
3. **Nothing else in the same commit catches the harm.** The 28 are not in checks 30–39's scope
   (F87), the exemption register is not consulted by `doc-id.py` (§2.2), and the damage is a
   successful write rather than a raise.

**Drop any one conjunct and the item is merely terse, not dangerous.** That is the difference
between this class and the taxonomy's other seven, and it is why a sweep for it is a reading task
rather than a grep.

**Conjunct 3 makes this a property of a clause *in a context*, not a property of a clause, and
that has a consequence worth reading before a sweep is commissioned.** Whether anything else
catches the harm is a fact about the commit, so **a clause is re-decided at every change that
touches its code path**. Two things follow. **A completed sweep does not stay completed** — its
output is a list of clauses to re-examine per change, not a set of defects to fix and close. And
the reading-task point is stronger than "the tell is semantic": **there is no stable answer to
cache.**

**The obvious way to make conjunct 3 fail here does not work, and testing it is what showed the
class is more robust than it looks.** The candidate: *fix F87 in the same commit, so the 28
manifests fall inside checks 30–39 and the doubled block is caught.* **It fails twice.**

- **F87 is not about these files.** Its defect is that `_id_scope_documents()` expands directory
  roots with `rglob("*.md")`, so the widening reaches **no non-markdown file** — the 59 `.json`,
  the `.yaml`, and two more. `SKILL.md` is markdown, so the 28 are **already inside** a widened
  scope, F87 or no F87. F87's own measurement says the 3 exemption entries it reaches are exactly
  these manifests.
- **And being in scope does not catch it.** `migrate()` prepends, so the damaged file opens with
  the migration's own valid header and the harness's block falls into the **body**. Tested
  against a read-only `git archive origin/main` snapshot, writing only into a temp directory,
  using the shipped `_stamp_header`, `_docid.parse_header` and `_front_matter_state`:

| On the file `migrate()` would have written | |
|---|---|
| `parse_header` | **`Header` — parses cleanly** |
| the header's `.extra` (where an unknown field would land) | **empty** |
| `---` delimiter lines in the file | **4** |
| harness `name:`/`description:` still present | **yes — in the body, not the header** |
| `_front_matter_state` | **`"stamped"`** |

**So check 30 has no unknown field to object to, and the migration's own idempotency test would
report the damaged file as already done.** A second run would skip it. **Three independent
mechanisms all read the corrupted file as correct**, which is a stronger statement of the hazard
than the original one and was not visible until the counterexample was tried.

#### How much of the corpus this has been swept over: almost none, and the denominator is not the one it looks like

**One confirmed instance. No sweep. And the population it belongs to is not the 98.**

Addendum A's 98 is the **rulings** corpus — 98 rulings across 41 record files. **F88 limb 1 is a
finding's falsifiable clause, not a ruling's acceptance item**, so *"how many of the 98"* is the
wrong question and answering it would be the mistake this section exists to avoid. Measured at
`origin/main`:

| Population | Count | Predicate, runnable |
|---|---|---|
| Findings files | **30** | `git ls-tree origin/main docs/audit/findings/ --name-only \| wc -l` |
| …carrying a falsifiable clause anywhere | **21** | `git grep -li "alsifiable" origin/main -- docs/audit/findings \| wc -l` |
| …of those, using the `## Falsifiable` heading | **10** | `git grep -hoE "^#+ .*[Ff]alsifiable.*" origin/main -- docs/audit/findings \| sort \| uniq -c` |
| Register-row `Falsifiable:` clauses | **19** | `git show origin/main:docs/audit/register.md \| grep -oE "Falsifiable:" \| wc -l` |

**The two homes are not de-duplicated here** — a finding may carry a clause in its file *and* in
its register row — so there is no single denominator, and inventing one would be the pasted
constant `CLAUDE.md` §13 refuses. **The honest statement: 1 confirmed, 21 findings files and 19
register clauses unswept.**

**On the rulings side, what can be ruled out is ruled out by class and nothing more.** Of
Addendum A's 98 at `5c0d24d`, **`NONE_FOUND` = 35** carry no item at all and **`INVALIDATED` = 3**
cannot pass on any input — Addendum A's own words for one of them, *"not 'never fires' but
'cannot pass'"*. **So 38 of 98 are excluded by class and 60 are unswept.** That is a derivation
from the recorded classification, not an estimate of how many have the property; **it says
nothing whatever about the 60.**

**Not extrapolated, deliberately.** One instance is one instance. The reason it is in front of
the maintainer is not that it is common — nobody knows whether it is — but that **every finding
in this effort carries a falsifiable clause, this repository's whole discipline for trusting a
fix is that the clause be met and proven on broken input, and this is the first evidence that
such a clause can be met destructively.** A hole in the discipline is worth reporting at n=1;
a rate is not claimable at n=1, and none is claimed.

### 2.6 A sixth failure, behind the fifth, and it is post-write

**Clearing the fifth abort does not make the run complete. It moves the failure past the first
write.** Found by the executor fixing the fifth, on the fix branch, and reported here rather than
discovered on the day.

**The reported behaviour:** `migrate()` reaches `_write_document_drafts`, writes new files, and
raises `KeyError: 'RS'`. **That is a partial run, not a clean abort** — task #34's failure mode
one layer down, unreachable while the fifth stopped the run first.

**`[SLOT-5]` — the number of files written before the raise.** Deliberately not stated. An
earlier draft carried **126** on relay; its author has since corrected it, the 126th being a
`.pyc` the import machinery writes when `migrate` path-loads `register-lint.py` — an artifact of
the interpreter, not an output of the run. **The corrected figure is not written here until it
arrives from its author with its predicate**, because this document already carries one section
(§8.2) about a relayed figure that did not reproduce, and a second one would be the same mistake
twice in one file. **Nothing below depends on it**: the count is an artifact of how far `sorted`
order got before the `RS` draft came up, not a meaningful fraction of the work.

**Two things must arrive with the number, or it does not go in.** **(1)** The figure, from its
author, **in a message** — the correction reached this document's author as a mutation of a file
in a shared, lock-free scratch directory, which carries no author, no timestamp and no predicate,
and is indistinguishable from an overwrite by a third agent. **(2)** The **predicate**, and
specifically **`_write_document_drafts`'s own denominator rather than a reconstruction from the
discovery call order** — its author reports that the reconstruction route disagreed with the
direct one by one on *both* operands, and **discarded rather than averaged**, which is the
correct instinct and is exactly why the predicate has to travel with the figure. **A number whose
two derivations differ by one is not a number until the predicate says which derivation it is.**

**The crash state is additive, and that is structural rather than lucky.** Verified by reading
`_write_document_drafts` at `origin/main`, not by running it. The function is **two sequential
loops**: a write loop over the drafts, then — only after it completes — a deletion loop.

```
for d in drafts:
    target_dir = root / "docs" / _DOCUMENT_FAMILY_DIR[d.prefix]   <- KeyError: 'RS' fires here
    ...
    new_path.write_text(header + "\n" + d.body, encoding="utf-8")  <- writes the NEW path

deleted: list[str] = []            <- not even initialised until the write loop ends
for was in sorted(was_sources):
    source.unlink()
```

**So a `KeyError` raised on the table lookup exits the function before the deletion loop is
reached, and before `deleted` exists.** Nothing is unlinked; nothing is modified, because the
write targets `new_path` and leaves the source alone. **The result is duplication — new files
beside intact legacy sources — not a half-moved corpus.** That is recoverable by deleting the
written paths.

**What it is not is diagnosable.** No acceptance item scores a partially-written state; the gate
cannot tell it from a completed run plus stray files; and the recovery depends on someone knowing
*which* paths were written. **An abort is honest — it announces itself and leaves nothing behind.
A partial run has to be noticed.** That is the whole of the difference, and it is smaller than
"irreversible" and still enough to recommend against.

**The `KeyError` and the file count are the executor's execution result and are not re-derived
here, on purpose: `migrate()` is not run by this document, because its write is the irreversible
commit.**
That is the same discipline the W37-5c close audit held — it called every guard with `migrate()`'s
own arguments and never called `migrate()`. **What is verified here is the cause, at the code
level, by symbol, at `origin/main`:**

| | At `origin/main` |
|---|---|
| Discovery emits the family | **Yes** — `_discover_closure_records` sets `prefix, kind, status, owner = "RS", "audit", "closed", "auditor"` for a heading matching `_CLOSURE_AUDIT_TITLE_PREFIXES` |
| How many such records | **2** — `_CLOSURE_AUDIT_TITLE_PREFIXES` has exactly two members, and the function's own docstring says *"Two headings … are a bespoke audit record: `RS-`, `kind: audit`, `status: closed`"* |
| `_MIGRATE_TEMPLATE_FILENAME` contains `"RS"` | **No** — `{ADR, RFC, PL, RL, CR, REFERENCE, LG}` |
| `_DOCUMENT_FAMILY_DIR` contains `"RS"` | **No** — `{ADR, RFC, PL, RL, CR, LG}` |

**Both of the writer's lookup tables omit the family discovery emits.** Predicate, runnable:
`git show origin/main:scripts/doc-id.py | grep -n '"RS"'` returns the emit site and neither table.

**This is not a disposition question, and that is what makes it cheap.** NT-0019 §1's family
table has specified it all along — *"Document | Research | `RS` | `docs/research/` | one spike,
measurement or audit"* — the tree layout names `research/` among the four directories
`docs/audit/` dissolves into, `docs/_templates/RS.md` exists in the tree, and **D13 rules the
owner**: *"Owners: research → executor, except `RS- kind: audit` → auditor."* The spec names the
family, the directory, the template and the owner. **It is an implementation gap against a spec
row, not an open question**, so nothing here needs a ruling.

**Why the fix should close the set rather than the instance, with the measurement that makes the
case.** Distinct prefix literals assigned anywhere in `scripts/doc-id.py` at `origin/main` —
`git show origin/main:scripts/doc-id.py | grep -oE 'prefix\s*=\s*"[A-Z]+"|prefix, [a-z, ]+= "[A-Z]+"' | grep -oE '"[A-Z]+"' | sort -u` —
are **ten**: `ADR`, `CR`, `FD`, `LG`, `PL`, `REFERENCE`, `RFC`, `RL`, `RS`, `WK`. The template
table names **seven** of them and the directory table **six**. **Some of those absences are
correct** — `REFERENCE` is stamped in place and never moved, and `WK` goes through the roadmap
restructure — **and which ones are correct is exactly the question a set-closure check answers
and a one-family patch does not.** `RS` is the member that is verifiably neither routed elsewhere
nor legitimately absent. **Fixing `RS` alone would leave the next such member invisible in the
same way**, which is the reasoning Ruling 83 already applies to censuses: the property is
*accounting*, not the absence of a known symptom.

**What this changes about the disclosure, stated plainly.** Until now every known failure stopped
the run before it wrote anything, and §2.1 could say the irreversible commit was not at risk.
**That is no longer the whole picture**, and `[SLOT-3]` is drafted for it.

---

## 3. The four preconditions W37-5c produced — three found, one made

**None of the four existed on any prior list**: not in the map plan, not in either leaf plan,
not in the 39-row obligations list, not in the superseded ask. Each was produced by building
W37-5c's own seven scope items and reading what its instruments then reported.

**The distinction the closure record drew, and this document keeps:**

| Finding | What it is | Found or made | Class |
|---|---|---|---|
| **[F87](../audit/findings/F87.md)** | Widening `_ID_SCOPE_ROOTS` reaches **no non-markdown file**; the glob is the gate, not the roots | **Found** — a pre-existing gap the slice's own build revealed | **Blinds.** A silent pass |
| **[F88](../audit/findings/F88.md)** | Limb 1: `_discover_vendored_skill_manifests` aborts every real run — **and its own falsifiable clause is destructive if met naively, §2.5**. Limb 2: `docs/audit/phases/1b/register.md` is discovered by nothing, silently | **Found** | **Limb 1 stops** (reclassified from *blinds* by the close audit). Limb 2 blinds |
| **[F90](../audit/findings/F90.md)** | Check 37 reds **95 of 95** post-migration ruling documents, its `##`-only detector unable to see a `###` heading | **Found** | **Blinds — and may change the cut. §4** |
| **[F92](../audit/findings/F92.md)** | 53 files deferred out of §4 step 5's Reference stamp set, recorded only in a squash-commit body | **Made** — the deferral is W37-5c's own, and it was the right call | Custody, not behaviour |

**F92 is the one of the four the slice itself created.** Its deferral is correct — the 53 files
(46 `.claude/skills/*/SKILL.md` and 7 `.claude/agents/*.md`, each already carrying the harness's
own front matter, so a stamp must be *merged* rather than prepended, which needs a template
change that is W37-6's own §7.1 Task 1) could not have been stamped inside a precondition slice
without building ahead of the phase. **The defect was where the deferral was recorded**, not that
it was made. It now has a register row and a dated pointer from the active leaf plan.

Predicate, runnable, at `d8d6e3f`:

```
git ls-files '.claude/skills/*/SKILL.md'                   | wc -l   ->  46
git ls-files '.claude/agents/*.md' | grep -v 'README.md$'  | wc -l   ->   7
```

**Why the distinction is worth a table.** Three findings say *the work that preceded this slice
had gaps nobody could see*. One says *this slice deliberately did not do something and told only
a commit body*. Presented as four preconditions they read as one backlog; presented apart, three
of them are evidence the instruments are working and one is a custody defect the slice fixed
about itself. **A document that merges them flatters the work in both directions.**

### 3.1 F87 and F88 in one line each, because they bound what a run would actually do

- **F87 — a check that passes over a scope containing none of the files it was built for.**
  `_id_scope_documents()` expands directory roots with `rglob("*.md")`. Widening
  `_ID_SCOPE_ROOTS` to the post-migration roots therefore reaches **0** non-markdown files and
  **3** of the 65 `UNSTAMPABLE_EXEMPTIONS` entries — the three vendored manifests, which are
  markdown. The other 62 (59 `.json` and 1 `.yaml` under `docs/contracts/`,
  `docs/process/delivery-process.core.json`, `docs/audit/file-census-5ef559d.csv`) are reached
  by nothing. **Those two figures have not moved at any of the five trees they have been
  measured at.** Pinned by `test_widening_the_scope_roots_alone_reaches_no_non_markdown_file` in
  `tests/test_audit_docs_ids.py` rather than by a pasted number.
  **Worse than F80–F82 because it does not announce itself**: an executor widens the roots,
  watches checks 30–39 run green over every markdown file, and ships having validated nothing
  over the 62 the exemption register exists for.
- **F88 limb 1 — the abort of §2, and a second consequence if it were fixed naively.** The
  "already stamped" test is `if _docid.parse_header(skill_md) is not None: continue`, and
  `parse_header` returns a `Header` for anyone's front matter. Measured at `359936b`: of 46
  `SKILL.md`, 28 are vendored by the shipped detector; of those 28, **25** parse and are skipped
  as already-migrated, and **3** raise. So fixing only the raise leaves 25 skipped for the wrong
  reason. Limb 2 is a §5.2-routed population no `_discover_*` function reaches, with no guard
  and no census — `migrate()` completes and reports success.

---

## 4. F90 may change the cut, not only the run — and that is `CLAUDE.md` §14's question

**This is the section the maintainer asked for by asking a wider question than "may it run".**

[F90](../audit/findings/F90.md), measured at `4df1c45` — **a tree that resolves here and for
nobody else; see the note after this table** — against a **disposable clone** using
`doc-id.py`'s own unmodified splitter to materialise real stamped ruling documents, then the
real unmodified `check_shape()`:

| | Count |
|---|---|
| Ruling headings the splitter discovers | **95** |
| Of those, parsed successfully as `family: ruling` | **95** |
| Of those, **red on check 37** | **95** |

The reproduction script is in the finding, written against the shipped symbols rather than
against these numbers.

**And the tree it names will stop resolving, which the disposition should fix while it is open.**
F90 **does** state its tree — `docs/audit/findings/F90.md:33`, the first line under
`## The measurement`: *"Tree: `docs/skills-marker-vs-property` @ `4df1c45` (PR #640's tip,
containing piece 1)"*. **But `4df1c45` is reachable only from this shared checkout:**

```
git merge-base --is-ancestor 4df1c45 origin/main        -> NOT an ancestor
git branch -r --contains 4df1c45 | wc -l                -> 0
git branch   --contains 4df1c45 | wc -l                 -> 1   (a local branch, this checkout only)
git ls-remote --heads origin 'docs/skills-marker-vs-property'  -> empty
```

PR #640 squash-merged as `dc1666f`, which **is** on `origin/main`; `4df1c45` is the pre-merge
tip and survives on one local ref. **A fresh clone cannot resolve it today**, and §5.4's own gap
condition requires releasing every agent worktree before the migration branch is cut — which
deletes the last ref pointing at it. **So the count carries a tree that resolves for the people
who already know the answer and for nobody else.** `CLAUDE.md` §13's test — *would it still
resolve for a reader holding none of your open context?* — is failed, in the one way a
correctly-formed citation still can.

**The remedy is not "add a tree"; it is re-pin or re-run.** Either state the measurement against
a reachable commit, or re-run it at `dc1666f` or later, or preserve the ref deliberately.
**Ruling 51 makes a register-row amendment opportunistic at the row's next substantive
amendment, and F90's disposition is that amendment**, so the fix rides along at no extra cost —
which is the whole reason it is raised here rather than as its own id.

**This is also a live instance of a rule in the place it was not written for, and it is recorded
as an observation rather than as a condition on §10.** `CLAUDE.md` §13 says *name the range, not
the tip*, and it was written for **reviews and gates, where a range is always available**. A
**measurement** legitimately names a single commit — and naming a **squash-merged branch's tip**
is the form that silently stops resolving. **That is a gap in the rule's scope, not a violation
of it.**

**It is not attached to the go-ahead line, deliberately.** Amending `CLAUDE.md` is the
maintainer's alone (`CLAUDE.md` §12), and making a rule change a precondition for a run would be
this document deciding something it may not. It is here because **this is a live instance rather
than a hypothetical**, which is what makes it worth the maintainer's attention at all.

**The sharp part is not the 95.** It is that **the 30 rulings written after the ruling-form
flag-day, specifically to comply, fail exactly as the 35 that were never asked to.** The
finding's exemplar is Ruling 95, whose migrated body carries the literal required phrase
verbatim — at `###`, one level under the split boundary — where `_template_body_sections`,
which matches `^##\s+` only, cannot see it. **A ruling written today, correctly, in the exact
form the flag-day requires, still reds.**

**Why this reaches the plan and not only the run.** F90 lists four options and dispositions
none. Three of them do not make a compliant ruling pass:

1. Date-grandfather check 37 — exempts the 35, leaves the 30 red. Their defect is depth, not age.
2. Make the section optional pre-flag-day — same gap, for the same reason.
3. Accept that W37-6 backfills the section into the 35 — leaves all 95 red on the other three
   required sections, which every one of them fails independently of the flag-day.
4. **Make the detector depth-agnostic.** The only option of the four that makes Ruling 95 pass as
   measured. **It changes behaviour for all ten families sharing `check_shape`**, and needs its
   own broken-input proof.

**So the live option is a change to a shared gate check across ten families, and it is not in
W37-6's scope as cut.** That is a question about the plan, not about the run:

- If option 4 lands **inside** W37-6, the irreversible commit grows a shared-check behaviour
  change that no acceptance item covers and that has never been proven on broken input — the
  class of thing every precondition slice so far existed to keep *out* of that commit.
- If it lands **before** W37-6, that is a further narrow slice, and the precedent for one is
  established twice over (W37-5b, W37-5c).
- If it lands **after** W37-6, the migration lands a corpus of 95 documents that red a gate
  check, and the gate is red between W37-6 and whichever slice fixes it.

**The lead does not choose between these**, and §9 says which it would recommend. **What this
section asks for is that the choice be made rather than discovered on the day**, which is
`CLAUDE.md` §14's standing question — whether the phase boundaries and workstream cuts still
make sense now that some of the work is real — put at the moment it is cheapest to answer.

**F90's own custody clause already names this document as the event.** Its register row and its
Custody section say the four options *"must be dispositioned before the next W37-6 go-ahead
request is made"*, and that absent that disposition the row decays to the next `CLAUDE.md` §14
plan review. **This is that request. The disposition is not made here, because the options are
not the lead's to choose between when one of them changes a shared gate.**

---

## 5. The gap

**The condition, verbatim from its source** — `docs/notes/0019-one-id-per-document.md`'s
`Sequencing / Trigger` row, which is the accepted note's own text:

> Now, at the next gap with no open branches (F40's lesson).

`docs/roadmap.md`'s W37 row states the same obligation in the lead's file: *"one supervised run
that moves the whole corpus and **must land at a gap with no open branches** and is never fanned
out."*

### 5.1 The gap is a check, not a date — and not a freeze

The map plan [`2026-09-01-nt-0019-id-standard-map-plan.md`](2026-09-01-nt-0019-id-standard-map-plan.md),
frozen at its date, states the condition and how it is verified, then says the thing that
governs how this section is written:

> **So the condition holds today.** It is a condition on W37-6 alone, and it is **volatile** —
> it can be false an hour from now. W37-6's leaf plan re-derives all three checks in the same
> session it runs the migration, and aborts if any has changed.

And the **frozen** leaf plan refuses to record an answer, for the reason that binds this
document too: *"a plan that bakes in a gap check turns a live condition into a stale claim the
executor then reads as satisfied."*

**So this section names a condition and its check. It does not certify a gap**, and a go-ahead
given against it is not a go-ahead given against a gap that has been established.

**Nothing obliges anyone to manufacture the gap.** There is no clause anywhere ordering open
PRs merged or closed, no freeze, no choreography. And a branch appearing mid-run is handled
rather than fatal — NT-0019 §4 step 8: *"Land at a gap; rebase any branch that appears by
re-running step 6 on its diff"*, never by hand-editing it, and (frozen leaf plan G12) never by
merging it ahead of the migration and re-running `migrate`.

### 5.2 The three checks, and where they stand

The map plan's precondition list, re-derived here at **2026-09-02T19:29Z** against
`origin/main` = `c888b61`. **This is evidence for a recommendation, not a certification** —
per §5.1 the checks are re-run in the session that runs the migration.

| # | Check (map plan's own words) | At 2026-09-02T19:29Z |
|---|---|---|
| 1 | `gh pr list --state open` returns nothing | **Holds.** `gh pr list --state open --json number` → `[]`. Sanity-checked against `gh pr list --state all --limit 8`, which returns eight merged/closed rows, so the empty result is a genuine zero and not a token failure |
| 2 | `git branch -r` lists only `origin/main` | **Held at 19:29Z, and no longer holds — see below.** `git ls-remote --heads origin \| wc -l` → **1**, the single ref being `refs/heads/main` |
| 3 | `git status --porcelain` is empty | **Does not hold, and see §5.3** — 52 worktrees exist under this `.git`, including this document's own |

**Check 2 is measured with `git ls-remote --heads origin` and not with `git branch -r`,
deliberately, and `git branch -r` was not run at 19:29Z.** `-r` reads local remote-tracking
refs, which a sibling worktree's fetch can advance or leave stale under a shared `.git`;
`ls-remote` asks the remote. **Only the `ls-remote` form is evidence for the row above**, and
this sentence replaces an earlier one asserting both were run and agreed, which was not true of
the 19:29Z measurement.

**And the volatility clause proved itself inside fifteen minutes, which is the most useful
thing this section has.** Re-run at **2026-09-02T19:44Z**, `git ls-remote --heads origin | wc -l`
returns **3**: `main`, the branch carrying this document, and `w37-6-fifth-abort-point`. **Check 2
went from holding to not holding while the document reporting it was being written**, and one of
the two new branches is this document's own. Nothing here is a defect — it is exactly why the
map plan calls the condition volatile, why the frozen leaf plan refuses to record an answer, and
why §5.4 states a condition rather than a finding.

### 5.3 Two §14 observations — the second is about the check, the first is about who ever reads it

**Both are worth the maintainer's attention and neither is an obstacle to the run.** The first
is the sharper of the two and is stated first for that reason.

**(1) The active leaf plan carries no gap check at all.** The **active** superseding plan has
**no §1 Preconditions section**, and its §6 carry-forward list names *"§5, §6, §7, §8, §9 and
§10"* of the superseded plan — **not §1**. So the operative gap-check list lives only in the
**map plan** and the **frozen** leaf plan, and **an executor working from the active plan alone
never meets it.** This is **F92's shape one level up**: a precondition that exists, is correct,
and is not in the document the person who needs it reads. F92 was filed for exactly that, about
53 files; this is the same failure about the condition that governs when the whole run may
start.

**(2) And the check itself no longer measures what it was written to measure.**

The map plan's third check is `git status --porcelain` **"in the worktree the migration runs
in"**, and its treatment of local branches was written against the repository as it stood on
2026-09-01:

> Three local branches survive in the shared checkout … They are leftovers, not open work.

**Measured at 2026-09-02T19:29Z against `origin/main` = `c888b61`:**

| | Count | Predicate, runnable |
|---|---|---|
| Worktrees under this `.git` | **52** | `git worktree list \| wc -l` |
| …of them locked | **13** | `git worktree list \| grep -c locked` |
| Local branches | **89** | `git for-each-ref --format='%(refname:short)' refs/heads \| wc -l` |
| …whose touched files are wholly on `origin/main` | **46** | for each branch `B`: `mb=$(git merge-base origin/main B)`; touched = `git diff --name-only $mb B`; the branch counts here when `git diff --name-only origin/main B -- $touched` is empty |
| …differing from `origin/main` on ≥1 file they touched | **43** | the complement of the row above |

**The 43 is an upper bound on live work, not a count of it.** A squash-merged branch's own
commits are never ancestors of `main`, and `main` has since edited many of the same files, so a
non-empty diff is as often *the branch is stale* as *the branch holds work `main` lacks*.
Resolving each of the 43 is not attempted here and is not what the check needs.

**What the check needs is the observation, which is checkable and does not depend on resolving
them:** the map plan's third limb inspects **one** worktree's `git status`. On 2026-09-01 that
was very nearly the whole repository — three leftover branches in the shared checkout. Today it
inspects **1 of 52**. *The working style changed under a frozen plan, and the check was not
re-derived for it.* That is not a defect in the plan; a frozen plan cannot say this about
itself. It is exactly the kind of thing `CLAUDE.md` §14 exists to catch while the phase is still
open.

**The two compound.** Observation (2) is a check that under-measures; observation (1) is that
the document an executor actually works from does not carry the check at all. **A weakened check
nobody reads is not two problems of one size.**

### 5.4 The gap the lead would name

**Not a date. A condition, in three parts, checked in the session that cuts the migration
branch:**

> **The migration branch is the first branch cut after the last precondition PR merges, with
> `gh pr list --state open` empty, `git ls-remote --heads origin` returning `main` alone, and
> every agent worktree under this `.git` released except the migration's own — each of the three
> recorded with the output of `git rev-parse origin/main` taken in the same command, so a
> sibling worktree advancing `origin/main` between the check and the run is visible rather than
> silent.**

The third clause is the one the map plan's check does not currently express, per §5.3. It is
offered as the form the check should take, not as an amendment: **amending the plan is not the
lead's** (`CLAUDE.md` §14 — the output of a review is a proposal), and §9 routes it.

**Why the third clause matters here specifically, in the recorded ground's own terms.** The
stated reason for the gap is **F40's lesson**, and F40 is not a merge-conflict finding — it is
`docs/audit/register.md`'s row on the shared Postgres test database, whose root cause was
*"three gate runs killed mid-pytest, which the lead caused by merging register PRs while a gate
was in flight."* The mechanism is **concurrent work over one shared resource**, and 52 live
worktrees over one `.git` and one test database is that mechanism at a scale the citation's own
incident did not have. **W37-6 is also itself a CI-workflow-file change** — NT-0019 §8's S2 list
names *"`docs.yml` filter"* among the H rows that must land in the same commit — and that is the
case the corpus already calls the worst one for F40's lesson, twice: `NT-0016` sizes a slice as
needing a gap because *"it touches CI filters, and F40's lesson … applies doubly to workflow-file
PRs"*, and its investigation plan's Scheduling clause is blunter — *"a workflow-file change is
the worst case of that. Land it at a gap, with no other gate in flight."*

**Recorded because a citation can be correct while a reader chasing it finds something else:**
NT-0019's Sequencing row cites F40 as the ground for a rule about *branches*, and F40's own text
is about a *database*. The transfer is sound and is made explicitly elsewhere in the corpus for
the same slice class. **Nothing here weakens the gap requirement** — NT-0019 states it in its own
words, independently of the citation.

---

## 6. Condition 1 — §3 and §4 re-derived at this document's tree

### 6.0 The slot register

**Every tree-pinned figure in this document is a marked slot until it is measured at the tree
named in §Header.** Grep this document for `[SLOT-`; **`[SLOT-0]`–`[SLOT-3]` and `[SLOT-5]` must
all be filled or the document is not ready for §10**, and `[SLOT-4]` must **not** be — it is
filled by the executor in the running session and never here (Acceptance Standard items 4
and 5).

| Slot | What fills it | Why it is not filled now |
|---|---|---|
| `[SLOT-0]` | The tree this ask is made at | It is not final; see below |
| `[SLOT-1]` | §3 and §4 of the superseded ask, re-derived in full at that tree | Condition 1 |
| `[SLOT-2]` | Addendum A's classification sweep, re-run at that tree | Condition 2 — §7 |
| `[SLOT-3]` | **How far a real `migrate()` run gets** — does not start / starts and does not complete / completes | §2.4, §2.6 |
| `[SLOT-4]` | The gap checks, re-run at the moment the branch is cut | §5.2 — **and this one is filled by the executor in the running session, never here** |
| `[SLOT-5]` | Files written before the `KeyError`, **from the measurement's author with its predicate** — never on relay | §2.6 |

### 6.1 Why it runs once, and late

**The maintainer's condition is a property of the day the go-ahead is requested, not of any
document.** The active leaf plan says so in its own §6.2, as the one thing still owed at the
ask: *"One more figure pass, at the tree the go-ahead is requested against… **Violation:** a
disclosure quoting a figure from a tree other than the one the run will start from."*

Running it three times and letting the last one count wastes the first two and creates two
superseded figure sets in a corpus that already has three. **It runs once, against the tree the
ask is actually made from.** The scope is the whole of §3 (the size by area, the growth table,
Ruling 66's enlargement, what becomes irreversible, what does not change, the windows, what the
go-ahead does not cover) and the whole of §4 (the bucket-C stamp population), re-derived by the
method the superseded ask's §2 records: **git plumbing against an explicit revision** (`git
ls-tree`, `git grep <rev>`, `git archive <rev>`), never the working tree, with the legacy-form
sweep importing the **shipped** `LEGACY_FORM_PATTERNS` and `sweep_legacy_forms` from each pin's
own extracted snapshot rather than a re-typed regex, and each pattern validated against its
`958cb7d` target before being trusted at the new pin.

### 6.2 What has already moved since `64f63ee`, as evidence that the pass is not academic

**One figure, measured here, offered as the argument for the pass rather than as part of it.**
Acceptance item (f) is *"`git grep -c 'VR-DST-1'` is unchanged from `8f5d57d` — no product
identifier moved"* (NT-0019 §7). Its baseline is therefore a figure the run is scored against.

Predicate, runnable, three units at each pin, because two of them have been confused before:

```
lines : git grep -c 'VR-DST-1' <sha> | awk -F: '{s+=$NF} END{print s+0}'
loose : git grep -o 'VR-DST-1' <sha> | wc -l          # over-matches VR-DST-10, VR-DST-19
exact : loose  minus  git grep -o -E 'VR-DST-1[0-9]' <sha> | wc -l
```

| Pin | lines | exact tokens | files |
|---|---|---|---|
| `8f5d57d` — the standard's own baseline | 104 | 107 | 25 |
| `89dd2b1` — the map plan's baseline | 107 | 110 | 26 |
| `39ee30c` — superseded leaf plan filed | 109 | 112 | 28 |
| `59bba94` — mid-session | 120 | 124 | 29 |
| `cc17404` — v2 filed as draft | 123 | 127 | 31 |
| `958cb7d` — v2 lifted | 125 | 129 | 32 |
| `64f63ee` — the superseded ask | 125 | 129 | 32 |
| **`c888b61` — today, W37-5c's merge** | **127** | **131** | **33** |

**The superseded ask's §3.3 said `VR-DST-1` was *"flat at 125 across the last two pins"*. It has
since moved to 127.** That is the pass justifying itself: a figure that was flat across two pins
moved at the third, in the same session, and it is the baseline an acceptance item is scored
against. **Nothing here argues for haste** — later is measurably larger, and that is a reason to
measure late, not to decide fast.

---

## 7. Condition 2 — the addendum, merged and re-run

**Merged.** Addendum A (*every defective acceptance item in a ruling W37-6 applies*) and
Addendum B (*the run aborts at four points, not three*) are both on `main` inside
[`…-go-ahead-ask.md`](2026-09-02-w37-6-go-ahead-ask.md) at `c888b61`.

**Re-run: `[SLOT-2]`.** The sweep's mechanical half is a shipped instrument —
`scripts/ruling-acceptance-item-census.py`, whose own docstring states the narrower question it
answers: *"did the sweep find every acceptance item there was to find, or did its enumeration
method have a blind spot?"* Its buckets must sum to the total, so a fourth phrasing convention
introduced by a later ruling appears as a heading the buckets do not cover rather than as a form
nobody remembered to grep for. The **semantic** classification —
`CONSTRUCTIBLE / INVALIDATED / VACUOUS AT BIRTH / INDICATIVE / CANNOT_DETERMINE / NONE_FOUND` —
is not derivable by script and is re-read.

**What the re-run must report, stated now so the slot cannot be filled with less:**

1. The census run at the final tree, its bucket table, and the sum against the total.
2. Addendum A's seven applying rows re-scored. At `2e48960` the state was: **two done** (R88 §4
   item 2 re-instrumented; R95 §4 item 3 re-instrumented), **two needing no action** (R66 item 2
   withdrawn and replaced; R85 item 3 disclosed as is), **one deliberate with W37-6 as its own
   remedy** (R61's tombstone-stub interval), and **two owed and ownerless** (R84 §4 item 2;
   R86 §4 item 3). **Item 1 — R84 §4 item 2 — is now built**, in W37-5c (`e2296ec`,
   `_check_emitted_ledger_axes`, non-vacuity proven against the real corpus with Ruling 94's own
   named mutation). **Item 4 — R86 §4 item 3 — is now rebuilt** in the same commit. So the
   re-run's expected delta is *the two owed rows close*; the slot records whether that is what it
   finds, or something else.
3. Whether any ruling filed since has added a row. Rulings 66–95 were on `main` at the
   superseded ask; the sweep's corpus was 98 rulings across 41 record files at `5c0d24d`.
4. **Addendum A's own recorded lesson re-applied, not re-derived:** two of its class counts were
   wrong when first written and the error survived a check that summed them to 98, *"which they
   did, and so does the correct set."* **A sum is invariant under a transfer between two buckets,
   so the check that was run could not in principle have caught the error that was there.** The
   re-run reconciles from the full enumeration, never from a running total.
5. Addendum B needs no re-run — it is two corrections, both confirmed by execution in W37-5c §2
   (row 3 is a real independent guard; the four are cleared). Its §B.2 point stands unchanged and
   is honoured throughout this document: **guards are named by function, never by line.**

---

## 8. Three corrections to the record this ask is built on

**Recorded here rather than smoothed, because each was believed and restated before it was
checked, and one of them is this document's own brief.**

### 8.1 W37-5c's two closing acts have both happened and neither record says so

`CLAUDE.md` §13: *"A Slice … closes on a clean audit and the lead's merge."* Both occurred —
the audit is [`W37-5c/README.md`](../audit/work/W37-5c/README.md), verdicts adopted by the lead
with four amendments; the merge is `c888b61`, PR #647, 2026-09-02.

**Neither of the two places that record a close says so:**

- The closure record's own **Sign-off** table still reads `Closed by | *(the lead's merge —
  pending)*`.
- `docs/roadmap.md` carries no `W37-5c CLOSED` line. `grep -c "W37-5c CLOSED" docs/roadmap.md`
  → **0**, against the precedent in the same W37 row one slice earlier: *"**W37-5b CLOSED
  2026-09-02** on a clean audit and the lead's merge (`64f63ee`, PR #617)."*

**This is a record-of-state gap, not a decision.** It is named here because the maintainer's
condition begins *"Re-ask when 5c is closed"*, and a reader checking that condition against the
roadmap finds nothing. **Routed to the lead; not written by this branch**, because `docs/roadmap.md`
is the lead's file and a slice close is the lead's act, not this document's to assert.

**And it is being fixed while this document is open, which is stated so the claim above cannot
rot silently.** PR **#651** files both lines. **A reader cannot tell a still-true absence claim
from one that has since been filled**, so: the two measurements above are true **at `c888b61`**,
and the way to check them today is to re-run `grep -c "W37-5c CLOSED" docs/roadmap.md` rather
than to trust this paragraph. Non-zero means #651 landed and this subsection is **discharged
rather than wrong**.

**Why the gap existed is the part worth keeping, and it is the same mechanism as §8.2's.** The
fix's own commit body records it. **Cited at `2eda76a`, #651's head, which carries the passage
verbatim — and the first SHA this section cited is now unreachable, which is §4's defect
reproduced inside this document.** An earlier revision cited `bb1b45ab`; that commit was itself
force-pushed over, and `git branch -a --contains bb1b45ab` now returns **0** — on no ref at all,
dangling and collectable, where F90's `4df1c45` at least still has one local branch. **The
citation was written the same way F90's was, by the same reasoning, and went stale faster.**
Recorded rather than quietly repointed, because two instances one document apart is what makes
§4's observation a hazard of how this repository works rather than one finding's slip:

> **SUPERSEDES THIS BRANCH'S FIRST COMMIT**, which said the roadmap was deliberately not edited
> because *"no slice has ever been recorded closed there — W37-5b is not, and grep finds no
> W37-5x closure line"*. That is false. W37-5b's own CLOSED clause is in the same row, one clause
> above where this one now goes… **I ran the grep and wrote the denial in one command block, so
> the claim was pushed before its own measurement was read. The measurement said 1.**

**A claim written in the same breath as the command that would have refuted it.** §8.2 is the
same shape at one remove — a figure repeated all day, whose own source table never supported it.
**Neither is a reading error; both are the measurement arriving after the sentence.** The cost
here was a force-push rather than a wrong merged record **only because the branch had not
landed**, which is luck rather than process.

### 8.2 The `VR-DST-1` movement figure this ask was briefed with does not reproduce

The brief for this document stated *"the `VR-DST-1` baseline moved +13 in one day against +5
across every prior commit"*, and used it as the argument for running condition 1 once and late.

**Neither half survives as stated, and the underlying claim gets stronger, not weaker.**

- **The `+5` is real and is the obligations list's**, whose §5.3 reads *"+11 in one day, against
  +5 across every commit before it"* over the pins `8f5d57d`/`89dd2b1`/`39ee30c`/`59bba94`.
  Re-derived in §6.2: `104 → 109` is +5 and `109 → 120` is +11. **Its partner figure is +11, not
  +13**, and the two spans are different lengths — +5 covers the whole prior history, +11 is one
  hop.
- **The `+13` is the superseded ask's** (*"having moved +13 in the day before them"*) **and
  reproduces at no pair of pins in its own table in either unit.** Within-unit over the same
  span: `109 → 125` is **+16** (lines) and `112 → 129` is **+17** (exact tokens). The only
  arithmetic yielding 13 across those pins is `125 − 112` — the `958cb7d` **line** count minus
  the `39ee30c` **token** count. That is offered as the one candidate explanation, not asserted
  as what happened.
- **And the document that commits it is the document that diagnoses the class.** The ask's §5.3
  is a full, correct account of a cross-unit contrast in the leaf plan's §4.2 — *"a bare-string
  count and a decorator count are different quantities, not two estimates of one"* is its own
  Acceptance Standard item 2. **§3.3 is two sections earlier in the same file.** So the
  diagnosis and the instance sit in one document, the instance first. That is the sharpest form
  this class has taken here, and it is why the correction below is carried in both units rather
  than as a single replacement number.
- **The obligations list is exactly right in all three of its claims**, including the
  parenthetical *"(`git grep -c` counts lines: the exact-token count at `59bba94` is 124.)"* —
  `126` loose hits minus `2` matches of `VR-DST-1[0-9]` is 124. The over-match is real:
  `VR-DST-10`, `VR-DST-19` and `VR-DST-99` all exist at `c888b61`.

**The conclusion the figure was carrying survives its correction and is strengthened:** the
like-for-like movement is +16 or +17, larger than the +13 quoted. **And the constraint never
rested on it** — the active leaf plan's §6.2 states condition 1 as a property of the day,
independent of any figure, and the maintainer's own condition says *"re-derived at that tree."*

### 8.3 The commit subject that cannot be corrected

`544b90c`'s subject asserts *"migrate() no longer aborts"*, and a squash body is immutable. **It
is quoted and contradicted in three amendable documents** — the closure record, the roadmap's
W37 row, and this one. Recorded as a class rather than as an incident: it is the **second**
commit body in this Work to misdescribe what it landed (`d7c9b08`'s said a guard names *"A1 and
A2"*; it names three), and both corrections live in documents citing the hash for the same
reason.

---

## 9. What is asked, and what the lead recommends

**What is asked is one line in §10.** Nothing above authorises the run.

**What the lead recommends, stated as a recommendation and not as a conclusion:**

1. **On the run itself — the recommendation is a function of `[SLOT-3]`'s three states, and only
   one of them is a go-ahead.**
   - **Completes** → **go ahead, conditional on F90 being dispositioned on the same line.**
     Conditions 1 and 2 filled at the tree, the run reaches the end of `migrate()` on the real
     corpus, every disclosure Ruling 66 §3 requires is present, and the preconditions that would
     silently mis-migrate something are either fixed or disclosed. **The F90 condition is not an
     extra demand; it is §10's own invitation made binding on this branch** — and it is attached
     here rather than left to §9.2 because **the better `[SLOT-3]` gets, the sooner F90 bites.**
     Check 37 reds 95 of 95 migrated ruling documents, and those documents **do not exist until
     the run creates them** — so *a completing run is precisely what produces the red*. A
     maintainer reading only this bullet could give the line and land an irreversible commit that
     turns the gate red with no disposition chosen, which is the outcome §4 exists to prevent.

     **F87 is a disclosure and F90 is a condition, and the test that separates them is not
     red-versus-blind — it is whether landing the commit *creates* the defect or merely *fails to
     fix* one.** F90's 95 red documents do not exist before the run; **landing creates them.**
     F87's blindness pre-exists and landing slightly improves it: checks 30–39 see **1** document
     today, and after the widening they see the whole markdown corpus and **3** of the 65
     exemption entries — 0 → 3, with 62 still unreached. **Landing leaves F87 exactly as bad as it
     already was, and it can be fixed afterwards without a second irreversible act.** Red-versus-
     blind gets the same answer here and for the wrong reason: it would make any future blind
     finding a disclosure, including one that landing *creates*.
   - **Does not start** → **recommend against**, on the superseded ask's own reasoning: a
     go-ahead then authorises a run whose first act is an abort.
   - **Starts and does not complete** → **recommend against, and more firmly than for a run that
     does not start.** §2.6's `KeyError` is past the first write. **The warrant here is
     structural, not measured** (§2.6): `_write_document_drafts` is two sequential loops, the
     raise is a dict subscript at the top of the write loop, `deleted` is not initialised until
     that loop ends, and no `try`/`except`/`finally` appears anywhere in the span — **so nothing
     is deleted and nothing is modified, and that holds without anyone having run anything.**
     The state is **duplication, recoverable by deleting the written paths** — *not* a corpus in
     neither shape, a phrase this document used in an earlier draft and withdrew (§2.4). **What
     it is not is diagnosable:** no acceptance item scores a partially-written state, the gate
     cannot tell it from a completed run plus strays, and recovery depends on someone knowing
     which paths were written. **An abort announces itself; a partial run has to be noticed.**
     That is a smaller harm than "irreversible" and still enough. The remedy is small, is not a
     disposition question (NT-0019 §1 has specified the family all along), and belongs outside
     the irreversible commit like every precondition before it.
2. **On F90 — decide before, not during, and the lead's reading is that option 4 does not belong
   inside W37-6.** A depth-agnostic detector changes behaviour for all ten families sharing
   `check_shape` and needs its own broken-input proof; putting it inside the irreversible commit
   is the thing every precondition slice so far existed to prevent. **And the maintainer is asked
   one question, not two: do you accept a red gate across the window?** Cutting a slice is not a
   cost they need to price — **a slice is the lead's to cut** (W37-5b was inserted by the lead's
   decision, and W37-5c by the maintainer's; the precedent for both is in the roadmap's W37 row).
   **Accepting a red gate is the maintainer's alone, because it is a degraded repository state
   and nobody else may consent to one on their behalf.** So: **if the maintainer does not want
   the red gate, the lead will cut the slice** — that is a commitment, not an option being
   priced.
3. **On the gap — no plan edit on the lead's authority, and one proposal.** §5.3's third limb
   (`git status --porcelain` in one worktree, against 52) is a `CLAUDE.md` §14 finding against
   the map plan, and §14's first rule is that the output of a review is a proposal, never a
   change. **The proposal is §5.4's three-part condition**, to be accepted or amended in §10 or
   at the next plan review, and **the active leaf plan's missing §1** (§5.3, second half) fixed
   in whichever document the maintainer directs — the lead's reading is that it belongs as a
   dated append to the active plan under its own `Corrections after filing` section, which is the
   form F92 already set on that same file.
4. **On W37-5c's close record — the lead will file it**, per §8.1, in a separate change that
   this branch does not make.
5. **On `DESTINATION_ONLY` (§2.5) — the lead recommends a sweep, and does not run one here.**
   One falsifiable clause in this effort has been shown to be **satisfiable and destructive**.
   Whether any other shares the property is **unswept**, over 21 findings files and 19 register
   clauses, with 60 of the rulings corpus's 98 also unexcluded. The lead's reading: **finding out
   is a reading task, not a grep** — the class needs all three conjuncts §2.5 names, so a
   pattern will not do it — **it is not W37-6's work, and it should not gate this go-ahead**,
   because the one clause that bears on the run is F88 limb 1's and §2.4 already refuses to
   accept it as the test. **Recommended as a register row rather than as a condition on
   §10** — the maintainer may disagree and make it one. **And it names its decay event, because
   a row proposed with no individual owner must**: Ruling 49's decay rule, and F86 was filed six
   hours earlier about exactly this — *a finding about unowned rows failing to name their own
   decay event must not be one*. **No individual owner is proposed; absent a slice taking it,
   the row decays to the next `CLAUDE.md` §14 plan review, which must give it a disposition
   rather than list it**, and it carries the `§14` literal so `register-owed.py review` can
   surface it. That is the disposition F87, F88 and F90 all took at W37-5c's close, and it is
   the default here for the same reason.
   **The eighth class is proposed here and is not adopted by this document**: adding a class to
   Addendum A's taxonomy is an amendment to a filed sweep's instrument, and §2.5 names it so the
   maintainer can adopt, rename or reject it on one line rather than reconstruct it.

**What this recommendation does not do.** It does not assume the go-ahead covers anything beyond
the run. NT-0019 §7 runs **(a) to (k)**; items (i), (j) and (k) belong to later slices — (i) to
the Work's closure record, (j) and (k) to W37-11. **Accepting this run is not accepting the Work
close**, which is a separate dated line reserved to the maintainer under `CLAUDE.md` §12.

---

## 10. Maintainer's line

**This section is the maintainer's alone.** A go-ahead for W37-6 is not the lead's to record,
and nothing above authorises the run. Per `CLAUDE.md` §14, the acceptance line is explicit and
dated.

> **Decision:**
>
> **Date:**

**If the decision disposes of F90 (§4) or accepts the gap proposal (§5.4), those dispositions
belong on this line or beneath it**, so that a reader of this one document finds the whole
answer where the question was put.

---

## Standing facts

- **W37-6 has not run.** Nothing merged is the migration; all of it is preconditions.
- **Rulings 66–95 are filed, all on `main`.**
- **`migrate()` still aborts on the real corpus at `c888b61`**, at
  `_discover_vendored_skill_manifests` — and **behind that abort is a post-write failure**
  (§2.6), so *"the run aborts"* and *"the run cannot complete"* have never been the same
  statement here. `[SLOT-3]` records how far it gets at the tree this ask is made from.
- **No document has yet been able to say "the run completes."** Every disclosure in this Work,
  this one included, has reported how far it gets — which is why `[SLOT-3]` asks for a distance
  rather than a yes.
- **Full local `uv run pytest -q` is not run by the team** — concurrent runs OOM-kill each
  other, and `docs/plans/` fixture tests collide with a concurrent `audit-docs.py` run (that is
  F89). CI runs the identical command in a clean environment.
