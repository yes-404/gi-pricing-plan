---
id: RL-911
family: ruling
title: Q3: opportunistic-on-amendment is adopted; the "worst offenders" alternative is rejected because that class does not exist
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md
---

## RL-911 — Q3: opportunistic-on-amendment is adopted; the "worst offenders" alternative is rejected because that class does not exist

### 1. Verified first, at `01ba0bd`

| Claim | Verdict |
|---|---|
| F27 and F-W9-3 are the register's longest rows | **Confirmed** — 4292 and 3539 characters |
| they are outliers — a distinct "worst offenders" class | **No.** Over 51 rows the **median row is 1148 characters**; **29 exceed 1000**, **23 exceed 1500**, **8 exceed 2500**. Migrating the two named rows would leave 21 rows still over 1500 |
| long rows are long because they were amended repeatedly | **Confirmed** — `git log -L` on the F27 row shows 5 commits, on the F-W9-3 row 2, all 2026-08-29. Size and amendment count are correlated, so an amendment trigger is well-aimed |
| amendment is frequent enough to be a real trigger | **Confirmed** — 16 register commits on 2026-08-30 |
| the acceptance standard requires any legacy row to migrate | **No** — the note's §8(d) asks only that *one new finding* land split through a real audit |

### 2. Ruled

**Opportunistic-on-amendment is adopted as the trigger. The alternative is rejected on its
premise, not on its cost:** "a one-time migration of the worst offenders (F27, F-W9-3)" names
a class of two that the measurement says is a class of twenty-three. A dedicated slice sized
to the two named rows would discharge under a tenth of the problem while reading, in the
roadmap, as having discharged it.

A full sweep is equally rejected: 51 rows of judgement-heavy edits in one PR is the
unreviewable diff the register's own F47 row declines for itself, and it is the note's
non-goal 2.

**But the recommendation as written is incomplete in two ways the measurement forces**, and
both are ruled in:

- **Migration is mandatory at the amendment, not encouraged.** When an over-threshold row is
  amended, the split lands in the **same commit** as the amendment. Without that, an
  opportunistic rule and no rule have the same observable behaviour, and nobody can tell which
  one is in force — the register's own motivation item 3 is that discipline enforced by
  intention alone is not enforced.
- **The residue is measured, in one aggregate line.** `register-lint.py` prints, every run,
  the count of unmigrated over-threshold rows against the corpus size and the threshold —
  never per-row. **This is the one device that does transfer from RL-906**, which replaced
  114 warnings with a single aggregate line for the same reason: the exemption stays visible
  without training every reader to skim the check's output. With no such line, "incremental
  migration" is a claim nothing can falsify.

**The threshold is a constant in the check, set by whoever writes P4 from the distribution
measured at that time — never a judgement made per row, and never a date.** This ruling does
not fix its value; it fixes its form, and records that at `01ba0bd` any value between 1000
and 1500 puts 23 to 29 of 51 rows in scope, so the migration is a long process and the
aggregate line is what makes it an honest one rather than a lapsed one.

**A new finding splits only when its evidence warrants a file.** P4's *"new findings use the
split immediately"* is scoped by the same threshold: a 200-character row does not get a file,
because a findings directory of one-line stubs is the ledger problem moved one directory down.

### 3. What it obliges

The P4 slice. Its acceptance evidence is the aggregate line's count at two trees — the one
P4 lands on and one later — with the delta explained, plus the note's §8(d) new-finding case.

**Overridden if** the threshold is a per-row judgement rather than a constant, if migration
is left optional at an amendment, or if the residue count is not printed on every lint run.

---
