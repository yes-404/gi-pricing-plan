# W37-5b — the lead's decision on the obligations proposal, 2026-09-02

**Decided by:** the lead, under the maintainer's 2026-09-01 delegation
(*"the lead makes the remaining decision on behalf of me"*) and the maintainer's
2026-09-02 comment withholding the W37-6 go-ahead: *"Sizing, and whether this is fixes
under W37-6's scope or a replan, is yours to propose."*

**Decides:** §7 of
[`2026-09-02-w37-6-outstanding-obligations.md`](2026-09-02-w37-6-outstanding-obligations.md),
merged as `b648c22`.

**Does not decide:** the W37-6 go-ahead. That is withheld and remains the maintainer's,
under the six conditions of
[`2026-09-02-w37-6-go-ahead-withheld.md`](2026-09-02-w37-6-go-ahead-withheld.md).

**Measurement tree:** `b648c22`. Every count below is re-derivable at that tree.

---

## Acceptance Standard

This record is discharged when all four hold:

1. **`W37-5b` is named in `docs/roadmap.md`'s W37 row**, in its `Progress` clause, with its
   scope stated as the group-A rows by number. **Not as a row of its own** — verified at
   `b648c22`, no slice in this repository has ever had one: `W32-1`, `W32-11`, `W6b-1` and
   `W6b-5` all appear only inside a Work row's prose, and W37's own `W37-1`…`W37-6` do the
   same. A new row would be the innovation, not the record.
2. **Every group-A row has a named owner** — an agent, a role, or an explicit deferral
   with a reason. Silence is not one of the four verdicts (`CLAUDE.md` §13).
3. **A new dated leaf plan for W37-6 is filed**, superseding
   `2026-09-02-w37-6-migration-run.md` by name and date, carrying Ruling 73's amendment
   to acceptance item 11 in the plan's own text rather than by reference.
4. **This record is cited where W37-5b's close is recorded** — the W37 row's `Progress`
   clause, and the Work-level closure record if W37 later files one — so the reasoning for
   the cut is recoverable from the close rather than only from here.

**How this record fails:** if `W37-5b` is opened and any group-A row is discharged inside
W37-6's commit instead, the cut did not hold and this decision was wrong. That is the
observable failure, and it is checkable after the fact by reading W37-6's diff for changes
to the eighteen.

---

## 1. The decision

**Both limbs of §7.4 are adopted.**

1. **`W37-5b` is inserted between W37-5 and W37-6**, scoped to the eighteen group-A rows —
   1–15, 30, 31 and 36 — with the two carve-outs in §3 below.
2. **A new dated leaf plan for W37-6 is commissioned**, superseding the frozen one. The
   frozen plan is **not edited** (`CLAUDE.md` §2).

**No workstream is re-cut, no requirement id moves, no stage boundary in the identifier
standard's §8 is changed by this record, and W37-6's own task list is untouched.**

---

## 2. Why — three grounds, in the order that decided it

### 2.1 W37-6 cannot pass its own acceptance standard as things stand

This is the ground that makes the decision close to forced rather than a matter of taste,
and it is the obligations list's §5.4.

Leaf-plan acceptance item 13 requires that after the run, a file beneath a vendored
skill's `SKILL.md` carrying a legacy citation and no header is byte-identical to its
merge-base content. **Exactly two tracked files meet that description.** Under the shipped
`is_vendored`, which still keys on `LICENSE` presence — the criterion **Ruling 69
rejected** — neither is vendored, so the run rewrites both.

**Item 13 therefore fails by construction until item 9 lands.** Item 9 is group A. A slice
whose acceptance standard cannot pass is not a slice that should be authorised, and the
remedy is not to weaken item 13 — it is to land the declared constant first.

That single fact disposes of the alternative *"do the fixes inside W37-6"*: doing them
inside means the acceptance standard is evaluated against code changed by the same commit
it is meant to judge.

### 2.2 The boundary is already drawn by ruling for eight of the eighteen

Not an inference of mine or the planner's:

- **Ruling 81 §2** — the parser fix *"lands as its own pull request, merged on its own,
  before W37-6 runs"*, because *"a migration run against an already-correct parser is one
  fewer variable in the run that can least afford one."* §3 item 3 adds that if it does
  not land first the work reverts into W37-6.
- **Ruling 83 §3 item 1** — *"the census runs before W37-6, not during it"*, with §2
  expressly rejecting deferral: *"the guard fix is testable today against a corpus that
  already produces four distinct violations."*

Those two place rows 5 and 8 directly, and rows 1, 2, 3, 15, 30 and 31 through the census.
**Eight rows must land before W37-6 whatever I decide.** The live question was never
whether pre-run work happens; it was only whether the remaining ten join them and whether
the collection gets an id.

Given that eight are already pre-run, the alternative to a slice is eight to eighteen
unnamed drive-by pull requests, closing with no audit scope, no closure record and no
derivable list of what they were meant to cover. `CLAUDE.md` §13 rule 1 — *scope is derived
from the specification first, then evidenced* — has nothing to derive scope from in that
world. **Naming the collection is the cheap, governed option, and it is the one the
repository already reaches for.**

### 2.3 Two of the four discovery defects are design work, not bug fixes

`_discover_roadmap` faces semantics carried in decoration (`~~**W4**~~ ✔`), non-work rows
sharing the work column, free-prose status cells, and several status tables per phase.
`_discover_plan_reviews` needed **Ruling 82 to decide what the unit is** before any pattern
could be written at all.

**A design question resolved inside an irreversible commit is resolved without a
rehearsal.** That is the same reasoning that produced W37-5 as its own slice with its own
fixture corpus, and it has not weakened. What has changed is only the evidence that
W37-5's corpus was not representative of the tree it was built to migrate — which argues
for a second rehearsal against the real corpus, not for skipping to the run.

---

## 3. Scope of `W37-5b` — and two rows that are not in it

**Group A is eighteen rows: 1–15, 30, 31 and 36.** Of those, **sixteen are built inside
`W37-5b`** — rows 1–13, 15, 30 and 31. **Row 14 is the lead's** and **row 36 is routed to
the decision-maker**, for the reasons below. Both stay group A, so neither may be discharged
inside W37-6's commit; they are simply not this slice's to build.

```
group A                        18   (1–15, 30, 31, 36)
  built in W37-5b              16   (1–13, 15, 30, 31)
  carve-out 1 — the lead        1   (14)
  carve-out 2 — routed          1   (36)
```

**Carve-out 1 — row 14 stays with the lead.** `plan-reviews.md`'s reviews 9–11 are
mis-nested under a `##` headed *"Pending proposals"*. Ruling 82 §3 item 4 files it as a
structural correction to the document, and Ruling 82's own reason for raising it is that
*"the migration should not be the first thing to discover it."* It blocks nothing, and
putting it inside W37-5b would let an executor restructure the document that W37-5b's own
parser fix is being tested against — the parser must survive the document as it is.

**Carve-out 2 — row 36 is routed, not built.** The identifier standard's §8 assigns seven
charters and eleven skills to **S3**; Ruling 66 pulls three charters and six skills into
**S2**. §8 is unamended. **Whether a ruling may re-cut a stage boundary of an accepted
standard, or whether that is an amendment belonging to the maintainer, is not mine to
settle** — `CLAUDE.md` §12 reserves an amendment to what a governing document requires.
It goes to the decision-maker for options, trade-offs and a recommendation, and travels to
the maintainer **with** the go-ahead ask rather than after it, because the answer changes
what W37-6's commit contains.

**Rows 16–29 and 37 (group B) stay in W37-6.** Each is observable only once the corpus has
moved. **Rows 32–35, 38 and 39 (group C) gate nothing** and are carried as disclosure.

---

## 4. Sizing, and the cost of the delay

§7.5's estimate is adopted: `W37-5b` comparable to W37-5; the leaf-plan revision one
planner session; W37-6 itself unchanged, because nothing in group B has grown.

**The counter-argument is real and is recorded rather than answered away.** The corpus
grows monotonically under the decision: **+26 tracked files** and **+8 rewrite-population
files** between `39ee30c` and `59bba94`, and acceptance item (f)'s `VR-DST-1` baseline
moved **+11 in a single day against +5 across every commit before it** — and **+2 more in
the hour this decision took to write**, `120` at `59bba94` against `122` at `b648c22`.
Waiting is measurably more expensive than not waiting.

**It is still the cheaper side.** The delay's cost is a larger diff, which is linear and
recoverable. The cost of the alternative is two parser-design questions and an
unsatisfiable acceptance item resolved inside a commit that cannot be re-run — which is
not recoverable, and is the exact class `docs/roadmap.md` §5 calls retrofit-impossible.

**A standing instruction follows from the growth rate, and it binds the W37-6 ask:** every
figure in the eventual disclosure is re-derived at that day's tree, per the maintainer's
condition 6. A figure carried forward from `39ee30c` is now known to drift within hours.

---

## 5. What this record does not do

- **It does not give, imply or anticipate the W37-6 go-ahead.** Six conditions stand.
- **It does not edit the frozen leaf plan**, whose corrections live in the obligations
  list's §6 and now in the superseding plan commissioned here.
- **It does not rule row 36**, and states above why it must not.
- **It does not reopen W37-5.** W37-5b is a successor slice. **W37-5 has no closure record
  and does not need one** — `CLAUDE.md` §13 closes a Slice *"on a clean audit and the lead's
  merge"*, reserving a filed record to a Work, Phase or Project; `docs/audit/closure-records.md`
  contains zero occurrences of `W37` at `b648c22`, and the roadmap states only *"W37-5
  merged"*. An earlier draft of this record asserted that W37-5's closure record *"stands as
  filed"*. It does not exist, and the sentence is corrected here rather than deleted, because
  the same wrong assumption would otherwise be made again at W37-5b's own close.
- **It does not change what any in-flight executor is building** — only the slice whose
  closure record their work lands under.
