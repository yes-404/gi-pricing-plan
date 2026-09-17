---
id: FD-1057
family: finding
title: a measured result attached to a claim it does not support
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-03
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F99.md
---

# F99 — a measured result attached to a claim it does not support

**Filed 2026-09-03 at `7f19241` by the lead, against itself.** Work item **W37-6**, phase 2.

**This record carries no instance count, deliberately.** It was filed with one instance, titled
*"two instances"* when the second was added, and **still read "two" in both its title and its
register row after the third landed at `e8637fc`** — caught by the decision-maker re-reading the
merged file. A count in a summary is a second copy of something the body already states, and it
goes stale exactly as [`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md) describes, with
nothing failing when the two diverge. **The instances are the `## … instance` headings below;
count them there.** The fix was to remove the number rather than to correct it, because
correcting it would have rebuilt the thing that broke.

**Id allocation.** `git grep -hoE '\bF[0-9]{2,3}\b' origin/main -- docs/findings/register.md
docs/audit/findings/` at `7f19241` returns a maximum of **97**. `git grep` over `origin/main`
cannot see an id reserved on an open PR, so a single-ref sweep is not sufficient to allocate
against; the sweep must cover **every** ref:

```
for r in $(git branch -r | grep -v HEAD); do git grep -hoE '\bF[0-9]{2,3}\b' $r -- docs/; done \
  | grep -oE '[0-9]+' | sort -n -u
```

This record takes **F99**.

> **Correction, 2026-09-03, same day.** This paragraph originally read *"F98 look**s** free and
> it is not — F98 is allocated to the decision-maker on an unmerged branch."* **That was false
> and nothing was measured for it.** No `F98.md` exists on any ref, local or remote, and the
> only trace of the token anywhere in the repository was **this record's own sentence**:
>
> ```
> git for-each-ref --format='%(refname)' | while read r; do
>   git ls-tree -r --name-only $r | grep -q 'F98.md' && echo "$r"; done      → nothing
> ```
>
> The lead had *authorised* the decision-maker to take F98 and then wrote the authorisation
> down as an accomplished allocation. **A reservation whose only artifact is a sentence in
> another record is indistinguishable from a lost allocation**, and this one would have blocked
> the number permanently, since every future allocator reads the sentence and skips it. Caught
> by the decision-maker, which ran the all-refs sweep this paragraph now carries, declined F98,
> and took **F100**. **F98 is unallocated and free**; whether it is reclaimed or tombstoned is
> the maintainer's, per `CLAUDE.md` §5's never-renumber-never-reuse rule. See the third instance
> below.

## The mechanism

`git diff A B` — the two-dot form — compares two **trees**. `git merge` and GitHub's squash
both compute changes **since the merge base**. When `B` is a branch cut some time ago and `A`
is a `main` that has moved, the two-dot diff reports **everything `A` gained since the
divergence as though `B` had deleted it**.

The two are not approximations of each other. They answer different questions, and the
two-dot form's answer is *correct as a tree comparison* — which is what makes it dangerous:
nothing about the output is wrong, only the question it was read as answering.

Measured at `4988dca`, predicates verbatim:

```
git diff --stat 4988dca origin/w37-6-split-source-resolver
  → …/2026-09-03-w37-6-second-fail-handover.md | 429 --------   ← reads as a deletion

git merge-base 4988dca origin/w37-6-split-source-resolver
  → 198ea5d   (RL-1041, #675)

git diff --stat 198ea5d origin/w37-6-split-source-resolver \
    -- docs/plans/PL-01037-w37-6-the-extended-window-s-second-fail-and-the-handover-2026-09-03.md
  → (empty)   ← the branch never touched the file

git merge --no-commit --no-ff origin/w37-6-split-source-resolver   (into a temp branch off 4988dca)
  → handover present: YES;  conflicting files: none
```

**The file the two-dot diff reports as `429 --------` is untouched by the branch and survives
the merge intact, with zero conflicts.**

## What it caused

Three consequences, in increasing order of durability:

1. **Unnecessary work.** RL-1043 and Plan review 12 were cherry-picked onto current `main`
   rather than merged, on the stated ground that merging would destroy the handover. The
   *content* is correct either way — both were single commits and applied cleanly — so nothing
   is damaged. The **reason given for the method** is false.
2. **A wrong instruction to a working agent, twice.** The executor on row (g) was told to
   rebase `w37-6-split-source-resolver` before building on it, on this premise. It was also
   told the branch was "stale", which it is not in any sense that affects a merge. Compounding
   it: **PR #683 was already open for that branch** — `mergeStateStatus` CLEAN, all three
   workflows green at `9f2606d` — so the rebase would have produced a duplicate PR carrying
   the same work. Retracted by name before any duplicate was pushed.
3. **A false statement in an immutable squash body on `main`.** #684's merge commit
   (`4988dca`) states that merging the RL-1043 branch as-is *"would have deleted the
   handover's 429 lines"*. A squash body cannot be amended. This record is the amendable
   document that corrects it, and is the reason the finding is filed rather than merely fixed.

## Why it is a finding and not a slip

**The output looked like confirmation of the thing it was cited for.** The lead had a real
concern — several live branches were cut before a large handover merged — reached for a
command, and got a `429 --------` line that matched the concern exactly. That is the shape
`RFC-779` names: *a citation can be correct while the content it vouches for is wrong.* The
diff was real, the number was real, and the inference was invalid.

**It also passed the lead's own guard and should not have.** `CLAUDE.md` §13's rule —
*"name the range, not the tip"* — exists for precisely this family, and the two-dot/three-dot
distinction is the same distinction one level down. The lead applied that rule to *review
ranges* while violating it in a *merge prediction* in the same session.

**And it is a lead-shaped error**: an inference restated as a fact, in the class
`.claude/roles/lead.md` already names — *"the lead is the highest-error node on this team,
structurally, not by chance: it is the only role that mostly relays rather than derives."*
RL-1043 §7's Amendment 4 binds the lead to run its **figures**; the `429` here *was* run.
**What was not run was the operation the figure was used to predict.** That is the gap this
record adds: a measured number can still be attached to an unmeasured claim.

## Second instance, same class — a verified premise carrying an unverified conclusion

**Added 2026-09-03, hours after the first, and it is what turns this from an incident into a
class.** The subject differs — git semantics there, argument structure here — but the sentence
is the one this record already uses: **a measured result attached to a claim it does not
support.**

The decision-maker was instructed by the lead to file an open question into
`docs/open-questions.md`. It declined pending evidence, arguing: all eight sections are scoped
to a product spec module and every id is `OQ-<MODULE>-<n>`, so a question about
`audit-docs.py`'s own check belongs to no module and filing it under `PLAT` would invent a
scope. **The lead ran a command, confirmed exactly that, and withdrew a correct instruction.**

```
grep -nE '^#{2,3} ' docs/open-questions.md   → OVR DATA MODEL RATE OPT MON GOV PLAT — eight, all product modules
git grep -hoE 'OQ-[A-Z]+-' origin/main -- docs/   → exactly those eight prefixes, tree-wide
```

**Both results are true. The conclusion drawn from them is false**, and one further command
refutes it:

```
git grep -n 'OQ-554' origin/main -- docs/open-questions.md docs/specs/00-overview.md
  → :46   "Nothing checks that an `FR-` id a workflow step cites contains what the step
           claims" — about audit-docs.py checks 14 and 21. Owner maintainer, status open.
  → 00-overview.md:554 — its §10 mirror
git grep -n 'OQ-548' origin/main -- docs/open-questions.md
  → :37   the same shape, DECIDED 2026-08-21 into audit-docs.py's error-code pass, as FR-22
```

**`OVR` is where tooling questions are filed and decided, not merely tolerated.** A section
named for a product module is not thereby scoped to one, and the id grammar constrains the
spelling of an id rather than the subject of a question.

**Why this instance is the worse of the two.** The first was an inference stated without being
checked. This one **was checked**, and the check passed — against the argument's *premise*. The
lead confirmed what the decision-maker asserted and treated that as confirming what the
decision-maker concluded. **A verification that terminates at the premise wears the full
appearance of diligence while establishing nothing about the conclusion**, which is why it
produced a *withdrawal of a correct instruction* rather than merely an unchecked claim.

**The generalisation, which is the reusable part:** confirming the premise of an argument is
not confirming the argument. When a correction is offered with supporting evidence, the
evidence to run is **the one that would refute the conclusion** — here, a single
`git grep audit-docs docs/open-questions.md` — not the one the objector already ran.

**Not a criticism of the decision-maker**, which produced its false premise by not reading the
file, said so unprompted, filed `OQ-555` correctly, and separately caught itself reading a
count off a hardcoded line number and landing on the wrong table row. Its independent structural
argument — that the register's `Finding id | Concerns | Work item | Phase | Decision` shape has
no options or recommendation cell, and `register-lint.py`'s vocabulary describes dispositions of
an *established* defect rather than an open design question — was correct and load-bearing, and
survives this correction intact.

## Third instance — a claim with no measurement at all, inside the paragraph warning about it

**The most serious of the three, and the only one where nothing was run.** Instances 1 and 2
are correct measurements attached to claims they do not support. This one has **no measurement
behind it in any form**: the lead authorised the decision-maker to allocate F98, and then wrote
into this record, as filed fact, that F98 *"is allocated to the decision-maker on an unmerged
branch."* At the moment of writing the decision-maker had **offered to draft a row and allocated
nothing.** An authorisation was transcribed as an accomplished act.

**It was written inside the paragraph whose entire subject is that id allocation traps a careless
reader** — so the record demonstrated the failure it was warning about, in the sentence doing the
warning.

**Two properties make it worse than a wrong number.** First, it is **self-confirming**: the
assertion creates the only evidence for itself, and the next allocator reading it skips F98
forever, so the error is load-bearing rather than inert. Second, it **directed another role** —
the lead instructed the decision-maker to take F98 on the strength of it, which would have
produced either a collision or a second dangling reservation.

**What the correct method was, and it costs one command:** the all-refs sweep now in the
allocation paragraph above. The lead had *identified the right trap* — that `origin/main` cannot
see an open PR's reservation — and then failed to apply the remedy that trap implies, checking
one ref and asserting about the others.

**Caught by the decision-maker**, which refused the instruction, ran the sweep, established that
F97/F99 are real and F98 is not, and took F100 while naming F98's dangling state so the next
allocator would not re-derive it. That is the third time in this session a subordinate role has
stopped the lead propagating an error, and the second time the refusal was of a direct
instruction.

## The remedy, and it is not vigilance

**All three instances were caught by a subordinate role, none by the lead.** The obvious reading
is that the roles below the lead should keep challenging it. That reading is wrong, or at least
it is not the useful part, and the decision-maker said so when this record credited it with
"refusing instructions and being right":

> **"The mechanism that worked was not my judgement; it was that you wrote instructions with
> checkable escape clauses and I ran the check."**

**The evidence is in the third instance.** The lead's instruction was not *"take F98"*. It was
*"allocate F98; verify it free **including against open PRs**; **allocate F100 if F98 turns out
taken**, and **say in the record which you checked**."* That instruction **contains its own
falsification condition**, so a recipient who runs the check either confirms it or executes the
named alternative — and either way the wrong instruction does not propagate. **F100 was filed
under the instruction, not against it.**

Compare the second instance, where the lead's own reasoning carried no such clause: *"the
sections are product-scoped, therefore no home"* names nothing that would show it false, so
confirming it and refuting it look identical from the inside. **That is why one error was
absorbed by the process and the other needed a second person to notice.**

**So the rule this record argues for is about how an instruction is written, not about how
carefully it is believed:**

> **An instruction, and a claim, should name the condition under which it is wrong, and the
> action to take when that condition holds.**

It is mechanical, it is checkable by a reader, and it does not depend on anyone being more
alert. **It is the same property `CLAUDE.md` §13 already requires of a count** — that it carry
the predicate it was counted with — applied to an instruction rather than a figure.

**The corollary for reading a correction**, which is the second instance's lesson stated as a
remedy: when a correction arrives with supporting evidence, **run the evidence that would refute
the conclusion, not the evidence the objector already ran.** Confirming an objector's premise
establishes nothing about the objector's conclusion.

**And the asymmetry the decision-maker asked to have recorded, because the record would
otherwise teach the wrong lesson.** In the second instance the false premise was *the
decision-maker's*, produced by not reading the file, and the lead had the correct answer first
and was argued off it. Both halves belong here: a reader who learns only *"distrust your own
confirmation"* will still trust a confidently-argued premise from the role whose charter is to
verify. **The lead's failure was that its check terminated at the premise; the decision-maker's
was that it argued from a file it had not read.** Neither subsumes the other.

## Falsifiable

Discharged when a merge-safety claim in this repository is made from an operation that
predicts merges, not from a tree comparison — concretely, one of:

- **`git merge-base` plus a three-dot or base-relative diff** (`git diff $(git merge-base A B)
  B -- <path>`), or
- **an actual trial merge** into a throwaway branch, reporting the file's presence and the
  conflict list, as run above.

**Proven on deliberately broken input**, not only on a clean case: a branch cut before a large
file landed on `main`, where the two-dot diff reports that file as a large deletion and the
trial merge shows it present with no conflicts. **A check that only ever ran against a branch
with no such divergence would pass for the wrong reason** — the two forms agree whenever
`main` has not moved, which is exactly the case that cannot distinguish them.

**Not discharged by** the lead resolving to be more careful. The remedy is that the claim is
made from the right operation, which is a property a reader can check.

**For the second instance the falsifiable form is different, and both must hold.** Discharged
when a correction accepted from a subordinate role is accepted on evidence that could have
**refuted** it, not on evidence that confirms the objector's own premise — and the record of
the acceptance names that evidence. **Proven on deliberately broken input**: an argument whose
premise is true and whose conclusion is false, where confirming the premise returns a clean
result. The `OQ-554` case is that input, preserved here for reuse: eight product-named
sections, a uniform `OQ-<MODULE>-<n>` grammar, and a tooling question sitting inside `OVR` the
whole time.

**For the third instance: an id is allocated only against a sweep of every ref, and a
reservation exists only as a file on a ref — never as a sentence in another record.**
Discharged when an allocation claim in this repository names the sweep it was made against, and
when no id is skipped on the authority of prose alone. **Proven on deliberately broken input**:
a record asserting an id is reserved when no file for it exists on any ref — this record, before
the correction above, is that input.
