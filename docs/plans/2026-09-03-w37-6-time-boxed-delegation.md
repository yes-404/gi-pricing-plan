# W37-6 — the maintainer's time-boxed delegation, 2026-09-03

**Issued** 2026-09-03 by the maintainer. **Filed** the same day by the lead, on the
maintainer's own instruction that *"nothing below is in force until that PR is merged"* —
so this record is the instrument, not a note about one. Work item **W37-6**, phase 2.

**Window: eight hours from `2026-09-03T00:07:32Z`, so it expires at `2026-09-03T08:07:32Z`.**
The timestamp is this record's own filing time, read at the moment of writing rather than
carried from an earlier command, because a stamp fetched once and pasted later is how
`eta.md` drifted 4h31m while its body was rewritten
([`NT-0004`](../notes/0004-a-reference-that-resolves-only-for-the-writer.md)).

**It amends nothing in `CLAUDE.md` §12.** It delegates the maintainer's standing
reservations for the window and no longer. §12's text is untouched, and every reservation
below returns to the maintainer when the window closes.

## 1. Delegated to the decision-maker

**NT-0019 §1/§4 amendments needed to reach a completing, green run** — owner values, scope
markers, stamp-set membership, exemption dispositions, and template body shapes
(`docs/_templates/`).

Ruled as **dated sibling records in the pattern of today's**, not as edits to this one.

Two conditions on each ruling:

- **It cites the cell or §1 sentence it reads from.** Not a summary of it, and not a
  paraphrase in quotation marks — a citation names the file and the line it was taken from.
  Quoting accurately from one document while attributing to another is the same defect as
  inventing the words, and harder to catch because the string is genuinely findable.
- **It prices the option not taken.**

**Two options with no cell to read from is a halt, not a coin-flip.** That case is reserved
(§3) and stops the window if it blocks the critical path.

## 2. Delegated to the lead — the W37-6 go-ahead, on a mechanical gate

**All six, or none.** The gate is mechanical by design: each condition is checked by
running something, not by judging it.

| # | Condition |
|---|---|
| 1 | The auditor's **independent instrument** reports `migrate()` **completes** on a snapshot at the quiet tree, with the write trace **summing by family** to the leaf plan's expected count |
| 2 | **check 37 reds 0** on the fully migrated snapshot, F90 slice merged |
| 3 | **Every `register-owed.py W37-6` row dispositioned** — discharged, disclosed, or deferred **by name** |
| 4 | The re-ask **under 300 lines** at that tree, `SLOT`s 0–3 filled, **§9 recommends go** |
| 5 | **No open branches** at the tree |
| 6 | **A `git revert` of the migration commit is proven on the snapshot to restore the tree byte-identical** |

**Condition 6 is the one that makes this delegable at all**, in the maintainer's own words.
A one-way irreversible write is not a thing anyone should authorise on delegated authority;
a write proven reversible is. It is therefore not a formality and not satisfiable by
argument — it is satisfied by performing the revert on the snapshot and comparing.

**If all six hold**: sign §10 of the re-ask
`on delegated authority, 2026-09-03, gate 1–6 verified at <tree>`, run the migration, land
it as a PR, merge it. **Then stop.**

**The Work close of W37 is not delegated.** Do not start W37-7 or any later slice.

## 3. Reserved — halts the window if it blocks the critical path

- `CLAUDE.md` amendments.
- **Work or Phase close acceptance.**
- Any deletion **outside the 20 tombstones §4 step 4 names**.
- Anything touching **repository settings or controls**.
- **Installing any external skill or agent.**
- **A PR by any author other than `yes-404`.**
- **A gate condition that fails twice.**
- **A decision the decision-maker finds no cell for.**

## 4. Halt protocol

**Triggers**: any reserved item blocking the path; the eight hours elapsing; or CI red on
`main` that cannot be cleared in one PR.

1. **Merge or close every green PR whose merge needs nothing from the maintainer.**
2. **Commit or stash every worktree**, `git worktree prune`, and **verify `git status` clean
   in each**.
3. **Write the handover** in the shape of
   [`2026-08-20-w5-worker-handover.md`](2026-08-20-w5-worker-handover.md) — final state, the
   tree, open PRs **by number**, the reserved decision **with its options priced**, and the
   **resume command per agent** — and **commit it to `main`**.
4. `shutdown -h now`.

**A handover written and not committed is the failure the W5 record exists to prevent.**
Step 3's commit is the step, not the writing.

## 5. Reporting

**Status goes to the `docs/roadmap.md` W37 row and to `register-owed.py`, not to chat** —
the maintainer reads the tree on return. **One line in the handover per hour elapsed**:
tree, PRs merged, what changed hands.

## 6. Renewal and two rulings — dated append, 2026-09-03

**Appended 2026-09-03 by the lead, on the maintainer's instruction, after the window of the
header had expired and its halt protocol had run.** Appended rather than written into the
header, because a record rewritten in place destroys the evidence of what was believed when
it was signed — the same reason `2026-09-02-w37-6-second-withholding-and-standing-rules.md`
§5 was amended by dated append rather than rewritten (PR #654). **The header's window and
its expiry stand exactly as written; they are history, not a mistake to correct.**

### 6.1 The first window expired, and that is recorded

The window of the header opened `2026-09-03T00:07:32Z` and expired `2026-09-03T08:07:32Z`.
**It expired.** §4's halt protocol fired on its elapsed-time trigger and
[`2026-09-03-w37-6-window-handover.md`](2026-09-03-w37-6-window-handover.md) is its step 3,
merged to `main` as PR #663.

**Every reservation the header delegated returned to the maintainer at that moment** — the
header says so itself: *"every reservation below returns to the maintainer when the window
closes"* (§ preamble, `docs/plans/2026-09-03-w37-6-time-boxed-delegation.md:15`). The
decision-maker spawned into the renewed window verified this against the tree and **declined
to file under a §1 authority that had lapsed**, before being told the renewal existed. That
refusal was correct and is recorded here because it is the behaviour the header's violation
clauses exist to produce.

### 6.2 The renewal

**The maintainer renews this delegation on the same terms for eight hours from the merge of
the handover pull request** — PR #663, merged `2026-09-03T08:43:13Z`, merge commit
`178541a8201be765dd262c895c61658b0d2b0581`.

**So the renewed window expires `2026-09-03T16:43:13Z`.**

The anchor is a merge timestamp read from `gh pr view 663 --json mergedAt,mergeCommit`, not a
clock read at the moment of writing and not one carried from an earlier command. That
matters here for the reason the header's own timestamp note gives: a stamp fetched once and
pasted later is how `eta.md` drifted 4h31m while its body was rewritten
([`NT-0004`](../notes/0004-a-reference-that-resolves-only-for-the-writer.md)).

**Same terms means same terms.** §1's two conditions on every ruling, §2's six-condition
mechanical gate, §3's reserved list, §4's halt protocol and §5's reporting are renewed
unchanged and are not restated here — a restatement is how one of two copies goes stale
([`NT-0003`](../notes/0003-duplicated-status-goes-stale.md)). **Read §1–§5 above; they are
the terms.**

**Nothing in §6 is in force until this append is merged**, on the header's own acceptance
standard: *"nothing below is in force until that PR is merged."* Actions taken under the
renewal before that merge are the header's first violation clause, unchanged.

### 6.3 Ruling — gate condition 2 is accepted as met, with its disclosure

**The maintainer's judgement on the one question the handover left open** (§8 of
[`2026-09-03-w37-6-window-handover.md`](2026-09-03-w37-6-window-handover.md)): whether
condition 2, satisfied over an enforced population of 0, is satisfied in the sense the gate
intended.

**It is accepted as met.** The arithmetic is Ruling 96's own consequence, and the
broken-input control proves the check fires on the first document to enter scope.

**The disclosure travels with it, and the four figures are not quotable apart.** Ruling 97 §4
binds them together:

> **0 red · 531 examined · 292 exempt by `was:` · and the broken-input proof.**

**The enforced population is 0.** Every document carrying a non-empty required set is exempt
by `was:`, because a verbatim-migrated body is out of check 37's scope and the whole migrated
corpus is carried-over bodies. **That is the ruled outcome, not a defect** — but the ruling
that makes condition 2 satisfiable is the same ruling that empties the population condition 2
measures over, and a reader meeting `0` without that sentence draws the opposite conclusion
from the one the evidence supports.

**The evidence is the control, not the zero.** A `was:`-marked body with no sections passes;
an unmarked ruling missing its `Acceptance — the violation that must become detectable`
section reds, and goes green when the section is restored. `CLAUDE.md` §13 — *"a check that
has never printed a failure has not been tested"* — is why that control is load-bearing here
and why the zero alone is not.

**The option not taken, priced:** requiring a non-empty enforced population before the
go-ahead. *It reverses Ruling 96 in effect, since the exemption is what empties the
population; the run would then need the 284 → 0 remedy that F90's four options were measured
unable to deliver — option 4 measured at 95 → 95, making nothing pass, over a population of
284 documents across six families, not 95 across one.*

### 6.4 Ruling — a tagged evidence ref does not count as an open branch

**Gate condition 5 reads *"no open branches at the tree"*. A ref under `refs/tags/` is not an
open branch and does not count against it.**

The reasoning is the distinction the condition was drawn on: an open branch is **work in
flight** — something a reader must ask the state of. An annotated tag is **a citation target
that cannot move**. Condition 5 exists so the migration lands on a tree with nothing
outstanding against it, and a frozen evidence ref is the opposite of something outstanding.

Applied, in this window:

- `docs/w37-6-go-ahead-reask` carried #650's superseded document, preserved because
  [`2026-09-03-w37-6-go-ahead-re-ask.md`](2026-09-03-w37-6-go-ahead-re-ask.md) (PR #659)
  **cites it by path and records that it lives there unmerged.** Deleting the branch alone
  would turn a citation that resolves into one that does not — the exact defect removed from
  F87's register row earlier in the first window.
- It is therefore **tagged `evidence/w37-6-reask-v1`**, an annotated tag dereferencing to
  `fcd7068eaf9db2a55fe1a5d9a5993df6efa8cb1b`, the branch tip. Verified **on the remote**, not
  locally, with `git ls-remote --tags origin`. The tag was pushed and confirmed present
  **before** the branch was deleted, so no interval existed in which the objects were
  unreferenced.
- **The branch is then deleted, and condition 5 is met.** #659's citation is updated in the
  same change set that deletes the branch, so `main` never carries a dangling reference.

**The option not taken, priced:** leaving the branch open and recording condition 5 as unmet
by one, deliberately — the first window's choice. *It leaves the gate permanently
unsatisfiable by mechanical check, which is the property §2 says the gate was designed for:
"each condition is checked by running something, not by judging it." A condition that always
requires a judgement call to excuse one branch is no longer mechanical, and every future
reader has to be told the exception.*

## 7. Second renewal and three amendments — dated append, 2026-09-03

**Appended 2026-09-03 by the lead, on the maintainer's instruction, after the first renewed
window halted on its second gate failure.** Appended rather than written into §6 for the
reason §6 gives: a record rewritten in place destroys the evidence of what was believed when
it was signed.

### 7.1 The first renewal halted correctly, and nothing was lost

The window of §6 opened `2026-09-03T08:43:13Z`. It **halted before its `16:43:13Z` expiry**,
on the delegation's own rule — *"one fail → fix, back to Step 3; second fail → halt
protocol"*. The record is
[`2026-09-03-w37-6-renewed-window-handover.md`](2026-09-03-w37-6-renewed-window-handover.md),
merged as PR #673.

**All six gate conditions were met** and NT-0019 §7(a)'s bar was met — `none` = 0. **The run
was stopped by a defect the six conditions do not name**: 36 live markdown links, in 5
surviving files, resolving to paths the migration deletes, because §5.2's README regeneration
is unimplemented. Ten PRs merged; `main` green; **no migration was attempted against any real
checkout at any point.**

**The maintainer's assessment, and the reason the rule stands unchanged:** *"That rule
produced a clean handover instead of a broken commit; it stays."*

### 7.2 The second renewal

**The delegation is renewed on the same terms for eight hours from the merge of the handover
pull request** — PR #673, merged `2026-09-03T12:30:39Z`, merge commit
`2ae31f7b192a1d7d859ec5b7be6c18b20da1e504`.

**So this window expires `2026-09-03T20:30:39Z`**, and §2's *"quiet with three hours left"*
rule puts the **go/no-go for starting the run at `17:30:39Z`**. Two gates on two different
acts: one bounds when the run may **start**, the other when anything may **finish**.

**§1–§5 are renewed unchanged and are not restated here** — a restatement is how one of two
copies goes stale ([`NT-0003`](../notes/0003-duplicated-status-goes-stale.md)). **Read them
above.** The three amendments below are additions, not replacements.

**Nothing in §7 is in force until this append is merged**, on the header's own standard.

### 7.3 Amendment 1 — gate condition 7

**A seventh condition joins §2's table. The gate is now seven, and it is still all-or-none.**

| # | Condition |
|---|---|
| 7 | **The auditor's general dangling-link scanner returns zero on the post-migration snapshot** — every `](…)` in every surviving file, resolved **relative to its citing file**, checked against the full deleted set |

**This was a finding and is now a condition.** It is what stopped the first renewed window,
and it stopped it *after* all six existing conditions had passed — which is the whole
argument for promoting it. A gate that its own failure mode walks through is not yet a gate.

**The scanner already exists**, built by the auditor of that window and preserved at
`~/gi-pricing-plan.local/scratch/w37-6-auditor2/`. **It is not to be rewritten**: a
reconstructed predicate is a different check wearing the same name.

### 7.4 Amendment 2 — relayed verification does not count toward a gate

**Every gate figure is produced by the agent that measures it, running the command in its own
worktree, with the command in the record.**

**An agent's number about its own work is a claim. The auditor's re-run is the evidence.**

**The maintainer's own grounds, verbatim: *"The `grep -c` = 0 that was 20 is why."*** In the
first renewed window an executor reported `grep -c '](' ` returning **0** for five files whose
true counts are **20, 6, 8, 6, 5**. The lead accepted that claim and recorded the defect class
as closed. The auditor refuted it by running the command itself, and that single refusal is
why a migration carrying 36 broken citations did not ship.

**This binds the lead as much as any agent.** A figure relayed through the lead has been
through fewer checks than its provenance suggests, not more.

### 7.5 Amendment 3 — a ruling names its implementation

**A ruling PR names its implementing PR, or carries `implementation: owed` in the register
row.**

**Grounds: §8 of the handover — six decided-but-unimplemented items in a single window.** A
merged ruling changes no behaviour until code implements it, and **nothing in the repository
flags the gap**. Three of the six were caught and fixed only because someone happened to run
the code; one was deferred by ruling; two survived to the halt.

**This is the smallest change that makes the gap visible**, which is why it is a field on a
row rather than a new check.

**It applies from this window. The backfill is W37-11's**, not a precondition of the run.

## 8. Halt overridden, window extended — dated append, 2026-09-03

**Appended 2026-09-03 by the lead, on the maintainer's instruction: *"Halt overridden and the
window extended — file both as a dated append to #674."*** Appended rather than written into
§7 for the reason §6 and §7 both give: a record rewritten in place destroys the evidence of
what was believed when it was signed.

### 8.1 The override, and the maintainer's grounds

§7's window halted on the delegation's own second-failure rule. **The maintainer has
overridden that halt**, and the grounds are not that the rule was wrong — §7.1 records the
maintainer's assessment that it *"stays"* — but that **the second failure was not a second
failure of the kind the rule counts:**

> *"The second fail was a fix that could not complete under Ruling 100 §2.4 as drafted; the
> index-entry rule replaces §2.4, so the fail count resets to one fix, once."*

The fix could not complete because §2.4 left the undetermined case — a whole-file citation
into a split source that determines no target, bucket (iv) — with nowhere to go. **A rule
that admits no completing action is not a fix that failed; it is a rule that could not be
satisfied.** Ruling 101, filed as §2.5 of the Ruling 100 record, replaces §2.4 by routing
that case to the split's index entry, and **bucket (iv) is 0 by construction** thereafter.

**So the fail count is one fix, once.** §7's rule is unamended and applies to the next
failure from a clean count.

### 8.2 The extension, and a discrepancy this append does not paper over

**The window's expiry moves to `2026-09-03T23:00:00Z`** — the maintainer's words: *"the hour
lost to the outage, not more."* The outage was an API-capacity event that killed roughly
thirteen agents, including every remaining agent of the §7 window, with no work committed
from any of them.

**The maintainer's instruction states the move as *"from 21:52Z to 23:00Z."* §7.2 of this
record, as merged at `6195ca0`, states the expiry as `2026-09-03T20:30:39Z`** — eight hours
from PR #673's merge at `12:30:39Z` — and §7's own final violation clause names
`20:30:39Z` and a `17:30:39Z` go/no-go. **These two figures disagree, and this append records
that rather than silently adopting either.** The prior figure is not re-derived here and is
not corrected in place; **`23:00:00Z` governs from this append forward**, on the maintainer's
authority, which is the only authority that sets the window at all.

**Consequently:**

| | |
|---|---|
| Expiry — nothing may **finish** after | **`2026-09-03T23:00:00Z`** |
| Go/no-go — the run may not **start** after | **`2026-09-03T20:00:00Z`** |

The go/no-go follows §2's *"quiet with three hours left"* rule applied to the new expiry.
**They are two gates on two different acts**, as §7.2 says: one bounds when the run may
start, the other when anything may finish. **§7's violation clause naming `17:30:39Z` and
`20:30:39Z` is superseded by this table** and by nothing else in §7.

### 8.3 The extension's own fail rule

> *"One fail on the index fix → fix once; a second → halt protocol and commit the handover
> before anything else. An outage during a halt with no handover is the state you're in now;
> don't repeat it."*

**This tightens §4's ordering rather than replacing it.** §4 already requires the handover
written and committed; the extension makes the commit **the first act of the halt, not its
last** — before merging or closing green PRs, before stashing, before any tidying.

**The grounds are the state this window was found in.** §7's window halted, and the outage
struck before its handover was committed. The record survived only because it had already
been merged as PR #673 in an earlier act; had the halt been one step earlier, the window's
whole evidential record would have died with the agents that held it. **Durability is a
three-way split** — uncommitted work dies, detached-HEAD work dies, branch-committed work
survives — and a halt protocol whose handover is written but uncommitted is the first of
those three wearing the appearance of the third.

### 8.4 Five agents, already ruled

**Five agents, not nine**, is the maintainer's change from §7's terms, ruled before this
append and restated here only because it is a term of the window: *"3.2× oversubscribed is
why fixes were slow enough to trip the clock."* The composition is the maintainer's:
**one executor on the resolver, one decision-maker, one auditor, one planner, and no
reporter.**

**§1–§5 are renewed unchanged and §6 and §7 stand as filed.** Neither is restated here — a
restatement is how one of two copies goes stale
([`NT-0003`](../notes/0003-duplicated-status-goes-stale.md)). **Read them above.**

**The three amendments of §7.3–§7.5 are in force unchanged**: gate condition 7 and its
un-rewritten instrument, relayed verification not counting toward a gate, and a ruling naming
its implementation.

**Nothing in §8 is in force until this append is merged**, on the header's own standard.

### 8.5 The §7 scope ruling — (a)–(i) are W37-6's, as gate conditions 8–16

**Ruled 2026-09-03 by the maintainer, recorded by the lead.** It resolves a scope question the
lead had been running to the wrong answer, and the lead's error is stated first because the
measurements taken under it were scoped by it.

**The lead had been asserting — to the maintainer, to the auditor and in this window's own
reporting — that "§7(a) is the absolute bar; (b)–(k) hold at W37-11's close."** That was
wrong, and it was wrong against two documents either of which refutes it:

- **NT-0019 §7's own preamble**: *"**At the migration PR's merge tree:** (a) … (k)"*
  ([`docs/notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md) §7).
- **The map plan**, which gives Slice W37-11 the scope *"acceptance items **(j)** and **(k)**,
  and the closure record"*, and has that record carry *"the **§7 (a)-(h) evidence from W37-6's
  ledger**"*
  ([`2026-09-01-nt-0019-id-standard-map-plan.md`](2026-09-01-nt-0019-id-standard-map-plan.md),
  Slice W37-11 block).

**The consequence the error had already produced:** the lead instructed the auditor that
§7(b)'s measured **77** failures were *"evidence only, not a stop condition this window."*
**That instruction was wrong and is withdrawn.**

#### The ruling

**§7 (a)–(i) are W37-6's, measured at the merge tree.** They join §2's table as **conditions
8–16 — nine rows, one per item — and are not folded into the existing seven.** Each carries
its own tree and its own predicate, as every row must
([`NT-0004`](../notes/0004-a-reference-that-resolves-only-for-the-writer.md)).

**§7 (j) and (k) are W37-11's**, on the maintainer's grounds: *"they cannot hold before S3
exists."* Item (j) requires one new item per family born through its skill, and (k) the
`--phase P1b` report — neither has a corpus to be true of until S3's conventions land.

**"Merge tree" means the merge tree.** The maintainer's words: *"(a)–(i) at the snapshot the
ask signs, not at a freeze commit before the resolver PR."* A gate row measured at a tree the
run will not be performed against is not evidence about the run.

#### §7(d) is amended, and this is where the acceptance can see it

**§7(d) is a single `git grep -E` with many alternatives** whose stated requirement is that it
*"returns nothing"*. **As amended:**

- **Each alternative is measured separately, one count each.** A single aggregate zero over a
  multi-alternative pattern cannot say which alternative is silent because the corpus is clean
  and which because the pattern never matched — the failure register finding **F85** names, in
  the clause of `CLAUDE.md` §13 that a count carries *"the predicate it counted with"*.
- **The `\bF[0-9]{2}\b` alternative is excluded from the zero requirement, with its count
  disclosed** as **W37-11's owed citation-form item**. This is the deferral the maintainer had
  already ruled — *"the essays get ids and paths now; `F<n>` stays a resolver alias to
  W37-11"* — now **stated where the acceptance can see it** rather than living only in the
  ruling that made it. A deferral the acceptance standard cannot see is indistinguishable, at
  the gate, from an unmet requirement.
- **Every other alternative must return nothing.** No further exclusion is granted here.
- **`was:` is excluded as a field, not as a substring.** §7(d)'s own text says *"excluding
  `REDIRECTS.csv` and `was:` lines"*. A substring test over the whole line drops body prose
  that merely contains `was:` — measured, and it hid one genuine dangling link in a **table
  row** in condition 7's own scanner. The discriminating test is `^was:` inside the leading
  front-matter block.

**If the `Ruling [0-9]+` alternative comes back large, that is a second deferral decision and
it is the maintainer's.** The maintainer's instruction is explicit about what to bring:
***"I want its count, not a recommendation, before I make it."*** So the count is reported
bare, and no option list accompanies it.

**§7(f)'s baseline is re-derived from the tree at `8f5d57d`**, not from any prior note —
including the auditor's own, which carried a `VR-DST-1` figure it later retracted.

#### Condition 7's blind spots — ruled on the class, not the list

Three blind spots were measured in condition 7's scanner. **The maintainer declined to rule on
them item by item and ruled the class instead:**

> *"Name each in the gate record with what it admits. One that admits a link that resolves and
> lies becomes a check before the gate — that's the halt defect, and the gate exists to see
> it. One that admits only a dangling link is already caught by condition 7 and is disclosed.
> If any of the three is the first kind and can't be a check by 21:00, that's a fail, and the
> count says what to do next."*

**So the test is what a blind spot admits, not how it was implemented.** The gate record names
each against that test. **A blind spot admitting a link that resolves and lies is the halt
defect itself** — the thing Ruling 89 called *"worse than one that fails loudly"* — and a gate
that cannot see it is not a gate. **A blind spot admitting only a dangling link is caught by
condition 7 once its population is right, and is disclosed rather than remedied.**

**And the failure mode is specified in advance**: if a first-kind blind spot cannot be a check
by `20:00:00Z`, **that is a fail** under §8.3's rule — one fix, once — and the count decides
what follows.

#### A pre-registered prediction, recorded before its measurement exists

**The maintainer's instruction:** *"The pre-registered 119/107 prediction: record it before the
measurement lands, whichever way it goes; a prediction written after the number is not a
cross-check."*

**The prediction.** At `4528ac0`, the auditor measured the post-migration family table as **465
documents total**, with **plan 126** and **ruling 100**, reconciled against
`git ls-files docs/ | wc -l` = 465. **Before** PR #679 merged, it predicted that Ruling 98's
implementation — which moves seven maintainer-prose documents from the `plan` family to the
`ruling` family — would give **plan 119** and **ruling 107** at the post-merge tree.

**#679 merged as `0de529e`. This subsection is filed before that measurement is taken.**

**What each outcome means, also stated in advance, so neither can be read favourably after the
fact:**

- **plan 119 / ruling 107** — corroboration of the family classification, from a prediction
  that could have failed. Seven documents moved, the total unchanged at 465.
- **anything else** — **the more informative result**, and it is not to be reconciled away. It
  would mean the seven the ruling names, the seven `_discover_plain_plans` emits, and the seven
  the family census counts are not the same seven — which no test in #679 could have caught,
  because all of them read the same constant.

**A total other than 465 is a third outcome and a distinct defect**: #679 changes which family
a document belongs to, never how many documents exist.
## Acceptance Standard

**This record is accepted when it is merged**, because the maintainer conditioned the whole
delegation on that merge: *"nothing below is in force until that PR is merged."* Until then
the lead holds no delegated authority and the decision-maker holds none either.

### Acceptance — the violation that must become detectable

*Violation: any action taken under this delegation before this record is merged.*

*Violation: a ruling filed under §1 that cites no cell, or that names no priced alternative.*

*Violation: the migration run with any of the six gate conditions unverified, or verified by
argument rather than by execution — condition 6 above all.*

*Violation: the window's expiry passing without the halt protocol running to step 4.*

*Violation: a handover written and not committed to `main`.*

*Violation (§6): any action taken under the renewal before §6 is merged, or after
`2026-09-03T16:43:13Z`.*

*Violation (§6): gate condition 2 quoted as `0 red` without the enforced-population-0
disclosure and its broken-input control — the four figures of §6.3 are not quotable apart.*

*Violation (§6): `evidence/w37-6-reask-v1` deleted, or the branch `docs/w37-6-go-ahead-reask`
deleted without that tag confirmed present on the remote first.*

*Violation (§6): this header's §1-§5 restated inside §6 rather than pointed at, so that the
two copies can disagree.*

*Violation (§7): the migration run with gate condition 7 unverified, or verified by any
instrument other than the scanner preserved from the window that raised it.*

*Violation (§7): a gate figure recorded from an agent's report of its own work rather than
from the auditor's independent re-run.*

*Violation (§7): a ruling merged with neither an implementing PR named nor
`implementation: owed` on its register row.*

*Violation (§7): the run started after `2026-09-03T17:30:39Z`, or anything finished after
`2026-09-03T20:30:39Z`.*

*Violation (§8): the run started after `2026-09-03T20:00:00Z`, or anything finished after
`2026-09-03T23:00:00Z` — §7's `17:30:39Z`/`20:30:39Z` clause is superseded by §8.2's table.*

*Violation (§8): a second failure on the index fix, and any act of the halt protocol
performed before the handover is committed to a branch.*

*Violation (§8): the fail count treated as still standing at two, or §7's second-failure rule
treated as amended rather than reset.*

*Violation (§8): more than five agents live at once, or a reporter spawned.*

*Violation (§8.5): a gate row for §7 (a)-(i) measured at any tree other than the snapshot the
ask signs, or the nine folded into fewer than nine rows.*

*Violation (§8.5): §7(d) reported as one aggregate figure rather than one count per
alternative; or the `\bF[0-9]{2}\b` count omitted rather than disclosed; or any alternative
beyond that one excluded from the zero requirement without a dated ruling here.*

*Violation (§8.5): a `Ruling [0-9]+` count delivered to the maintainer with a recommendation
attached, or an option list in place of the bare count.*

*Violation (§8.5): a condition-7 blind spot that admits a link which resolves and lies, left
as a disclosure rather than made a check before the gate.*

*Violation (§8.5): the 119/107 prediction's outcome reconciled to the prediction, or a total
other than 465 treated as anything but a distinct defect.*
