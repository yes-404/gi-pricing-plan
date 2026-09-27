---
id: RL-973
family: ruling
title: RL-990's obligation is a class with a sweep, not a list of slices; the template is one member of three, and the obligation re-assigns to W37-6
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-6-leaf-plan-findings-rulings.md
---

## RL-973 — RL-990's obligation is a class with a sweep, not a list of slices; the template is one member of three, and the obligation re-assigns to W37-6

### 1. Verified — and the plan's mechanism is not the mechanism

The finding is real: `docs/_templates/REFERENCE.md` lines 39-49 state that the vendored set is
decided by *"any directory holding a `LICENSE` that is not the repository's own … **not a
hand-kept list**"* — the rule RL-990 rejected, described as the opposite of what RL-990
ruled. Two things about **why** it survived are not as the plan reports them.

| Fact | Timestamp | Consequence |
|---|---|---|
| RL-990 merged (`#563`, `9d33c60`) | `2026-09-02T00:30:56Z` | — |
| W37-1 merged (`#562`, `553bbef`), adding the template | `2026-09-02T00:38:22Z` | **After** the ruling, not before. `9d33c60` is an ancestor of `553bbef` |
| W37-2 merged (`#567`, `2204ffb`), adding `is_vendored` | `2026-09-02T01:05:19Z` | **34 minutes after** the ruling, still implementing the rejected rule |

The plan's account — *"the template landed in W37-1, before RL-990, and RL-990 §3's
obligations name W37-2, W37-4 and W37-6 but not the template, which is how it survived"* —
inverts the order. The PR numbers invert it too: `#562` was **opened** at `00:27:16Z`, before the
ruling existed, and merged after it. **The mechanism is a branch open across a ruling's merge
that nobody re-read against the ruling before merging it** — not an obligation list that omitted
a file.

**And the template is the smaller half.** At `e93e0e4`, `scripts/_docid.py`'s `is_vendored` still
walks the tree looking for a `LICENSE`, and its docstring says so: *"Ruled as RL-990 (…, PR
`#563`, **not yet merged at the time this was written**) … Apply the ruling once `#563` merges;
until then this implements the rule exactly as published."* `#563` had merged twenty-six minutes
before `#567` did. `_VENDORED_SKILLS` does not exist anywhere in the repository.

**So RL-990 §3's first obligation is undischarged on the slice it named by name.** Extending
the obligation list would not have prevented this, and that is the whole point: W37-2 **was** on
the list. What is missing is a violation that can be detected. RL-990's own acceptance item 1
— *"Remove one entry from `_VENDORED_SKILLS`, or one skill line from `pyproject.toml`'s ruff
`exclude`, and the gate must red naming which side moved"* — **cannot fire, because its subject
does not exist.** An acceptance item whose subject is absent is not a check that has never failed;
it is a check that was never built, and nothing distinguished the two (`CLAUDE.md` §13).

### 2. Ruled

**RL-990 §3's obligation is restated as a class with a sweep.** It is not a list of slices,
and a slice name in it is a schedule, not the obligation's extent.

**The class: every site in the tree that states or implements a criterion for the vendored set.**
At `e93e0e4` it has three live members outside the frozen record set:

| Site | What it does | Disposition |
|---|---|---|
| `scripts/_docid.py`, `is_vendored` | **Implements** the rejected `LICENSE` probe | Replaced by the membership test against `_VENDORED_SKILLS`; signature preserved, per RL-990 §2 part 4 |
| `docs/_templates/REFERENCE.md` lines 39-49 | **Teaches** it, and calls the ruled mechanism *"not a hand-kept list"* | Corrected to state the declared constant reconciled against the ruff exclude list |
| `tests/test_doc_id.py` lines 372-430 | **Asserts** it — five tests that pin the rejected behaviour | Re-pointed at the membership test, with a broken-input proof for the reconciliation |

**`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` §1.5 and §5.4 are not in the class and are not
edited.** RL-990 §3 already says so and it stands: the note is the maintainer's original, §1
stays byte-identical, and a note that records a gloss is not an instrument that teaches one. The
distinction is the whole reason the template is different from the note it paraphrases — a
template is copied by an author, a note is read by one.

**The obligation re-assigns.** W37-2 and W37-4 have both shipped without discharging it, so it
carries to **W37-6** with the W37-6 executor as its named owner. That is a verdict, not silence
(`CLAUDE.md` §13's four).

**The general rule, which is the durable half and applies beyond this ruling: an obligation a
ruling assigns to a slice does not lapse when that slice merges without discharging it. It
re-assigns to the next unshipped slice, and it is stated as the class of sites it must reach, not
as the list of slices expected to reach them.** A list of slices is a schedule; a schedule that
is missed leaves nothing behind. A class plus a sweep leaves a grep.

### 3. What it obliges

- W37-6 discharges all three sites in one commit, and the deviation record RL-990 §2 part 3
  requires in `.claude/skills/README.md` lands with them.
- The reconciliation check RL-990 §3 assigned to W37-4 carries to W37-6 with it — it is the
  same obligation and it has the same owner. Its broken-input proof is RL-990 acceptance item
  1, which becomes runnable for the first time once `_VENDORED_SKILLS` exists.
- **Not this role's, referred to the lead in §7:** whether `docs/process/delivery-process.md`
  gains a step requiring a branch open across a ruling's merge to be re-read against that ruling
  before merging. That is process, and process is the lead's.

### 4. Acceptance — the violation that must become detectable

1. **No instrument or implementation may state the rejected criterion.** **Violation:**
   `git grep -nE "holding a .?LICENSE|ship(s|ping) (its )?own .?LICENSE" -- scripts/ tests/ docs/_templates/ .claude/`
   returns a hit at the merge tree. Frozen records — filed plans, ruling records and
   `docs/notes/` — are outside the pathspec by construction, so the grep needs no allow-list and
   cannot decay into one.
2. **The absent check must become a failing one.** RL-990 acceptance item 1 is run at the
   merge tree and **reds**: remove one entry from `_VENDORED_SKILLS`, and separately one skill
   line from `pyproject.toml`'s ruff `exclude`, and the gate must fail naming which side moved.
   **Violation: either edit passing green — including the case where it passes because
   `_VENDORED_SKILLS` still does not exist**, which is how this defect survived two slices.
3. **The re-assignment must be visible.** **Violation:** W37-6's ledger closing without a line
   naming RL-990 §3's obligation, the slice it was originally assigned to, and its outcome.

---
