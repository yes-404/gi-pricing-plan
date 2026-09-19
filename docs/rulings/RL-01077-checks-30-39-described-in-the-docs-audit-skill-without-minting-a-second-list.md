---
id: RL-1077
family: ruling
title: checks 30–39 "described" in the docs-audit skill, without minting a second list
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-19
owner: decision-maker
tree: 7d5d6e0a3730bfd790dace3a95c63a0ea71ec031
phase: P2
work: WK-697
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1070, RFC-937, RFC-756]
---

# RL-1077 — checks 30–39 "described" in the `docs-audit` skill, without minting a second list

## Verified first, at 7d5d6e0a3730bfd790dace3a95c63a0ea71ec031

**The escalation.** `PL-1070`'s Task 1 Step 3 instructs the W37-7 executor to restate the
checks 30–39 list into `.claude/skills/docs-audit/SKILL.md`. The executor escalated that it
cannot, because three records forbid duplicating that list. It priced three options and
recommended the narrowest. This ruling disposes of the escalation.

**Why it is this role's.** It is not a new capability or a phase question, so my charter's
carve-out to the planner does not reach it. It is `CLAUDE.md` §0's *"when code and spec
disagree, stop and resolve it"* in its documentary form: a plan's gloss of a spec row against
the spec's own word, inside the current phase's scope. If the lead judges it the planner's
instead, this converts to a recommendation at no cost.

**1. What the spec actually requires.** `RFC-937` §5.4's `docs-audit` row, quoted whole from
`:368`: *"checks 30–39 **described**; four-kinds paragraph and `YYYY-MM-DD-` grammar
removed; tombstone check → redirects check; citations"*. **The word is "described". "One
paragraph each in the skill" appears nowhere in §5.4** — it is `PL-1070`'s gloss, and the
plan is written against the spec, not the other way round.

**2. Three records forbid a second list, and I read each at this tree rather than taking the
escalation's word.**

- **The skill's own `description:` front matter**, last sentence:
  *"The script's own module docstring is the numbered list, kept current there rather than
  counted here."*
- **The skill body**, under the heading `### RFC-937's id-standard checks (30-39)`:
  *"The full ten-item list, and what each one catches, is `scripts/audit-docs.py`'s own
  module docstring …"* — the body already resolves the question by pointing.
- **`.claude/skills/README.md`'s `docs-audit` row**: *"**The numbered list lives in the
  script's own module docstring and nowhere else** — the count here said 23 while the code
  had 24 (`RFC-756`)."* This one carries a worked incident: the duplicate went stale by one
  and nothing caught it.

`RFC-756` is the general form — a restated fact is how one of the two statements goes stale —
and `CLAUDE.md` §12 applies it to skills directly.

**3. But the row is not yet satisfied, and the executor is right about which two are
missing.** I measured it independently rather than accepting the figure, with a
newline-tolerant predicate, because the skill's prose wraps and a line-scoped grep would give
a false negative. Flatten whitespace, then for each *n* in 30…39 take every `\bn\b` hit with
±90 characters of context and read whether any hit is a *describing* clause — says what the
check catches — rather than a bare mention:

```
tr '\n' ' ' < .claude/skills/docs-audit/SKILL.md \
  | python3 -c "import re,sys; t=re.sub(r'\s+',' ',sys.stdin.read()); \
    [print(n, [t[max(0,h-90):h+90] for h in (m.start() for m in re.finditer(r'\b'+str(n)+r'\b',t))]) \
     for n in range(30,40)]"
```

**Eight of ten carry one**: 30 (*"per-family field policy (which fields are
permitted/required)"*), 32 (*"citation resolution"*), 33 (*"map-plan roll-up raise"*), 34
(*"`DP-7`'s freeze predicate, `frozen_diff_is_permitted`"*), 35 (*"examines that same one
document for `owner:` **and** reconciles F83's exemption register"*), 36 (*"watching
`docs/REDIRECTS.csv`"*), 37 (*"per-family required sections"*), 39 (*"`check_index_stable`
… corpus build is guarded"*).

**31 and 38 carry none.** Every hit for either is a bare mention inside a plural list — the
sentence *"checks 31, 32, 34, 36, 38 and 39 currently examine zero"* — or a false positive:
for 31, the date `2026-08-31`; for 38, the count `38 JSON schemas parsed`, the range
`checks 1-38's notes`, and *"checks 32, 38 and 39's zero-population notes rewritten"*, which
is about note formatting and not about what the check catches. **A number appearing inside a
plural list is not a description of it**, which is the escalation's point and it holds.

**4. What those two checks catch**, read from the shipped docstrings at this tree so the
remedy can be stated rather than left to the executor to invent:

- **31** — *"Header `id` prefix and integer equal the filename's; directory equals family;
  numbers unique and contiguous in scope; `created` non-decreasing with the number
  (RFC-937 §1.11)."*
- **38** — *"Loop signal, **warn-only** (RFC-937 §1.11) — **never fails the gate, only
  notes.** Every sub-clause (a `PL-`/`RS-`/`RFC-` cited by nothing outside `INDEX.md`, a
  `PL-` still `draft` past its phase's point …)"*.

Check 38's warn-only nature is the single most load-bearing fact about it and is exactly what
a reader will assume the opposite of if the skill is silent.

## Ruled

**The executor's recommendation is adopted. Task 1 Step 3's instruction to restate the list
is refused, and replaced.**

**(i) No second numbered list is minted in `SKILL.md`** — not in the body, not in the
`description:` front matter. The `scripts/audit-docs.py` module docstring remains the single
enumeration, as all three records already require.

**(ii) `SKILL.md` gains a describing clause for check 31 and for check 38, and nothing
more.** Each names what the check catches, in the same prose register as the eight that
already have one, and **check 38's clause states that it is warn-only and never fails the
gate**. Placement is the executor's; beside the existing `### RFC-937's id-standard checks
(30-39)` pointer is the obvious home.

**(iii) The pointer rule is kept and made explicit** where the new clauses land: the ten-item
enumeration lives in the script's module docstring and is not copied here. This is what stops
(ii) growing back into (i) at the next edit.

**(iv) `RFC-937` §5.4's row is thereby satisfied on its own word.** With (ii) applied, all
ten checks carry a describing clause and the row's *"described"* is true of each. **No spec
change is required, and none is made** — the spec was right and the plan's gloss was wrong,
which is the direction `CLAUDE.md` §0 says to check rather than assume.

**Why not the alternatives.** Restating the list as the plan's gloss asks would mint exactly
the artifact `RFC-756` was filed about, in the one skill whose own README carries the worked
example of that artifact going stale — a 23-against-24 drift nothing caught. Leaving 31 and
38 undescribed would leave §5.4's row unsatisfied while looking satisfied, since eight of ten
already read as covered; that is the failure mode where a partial state is harder to detect
than an empty one.

**A note on this record's id.** `doc-id.py next` returns `1075` at `origin/main` and cannot
see `RL-1075` or `RL-1076`, which are committed on this branch and not yet merged — correct
behaviour of `compute_next_at_ref`, which reads a committed ref. `1077` is therefore taken as
the next free number above this branch's own allocations. The `docs/REDIRECTS.csv`
register-row collision disclosed in `RL-1075`'s *What it obliges* applies to `1077` as it
does to every number below 1136; it is not restated here beyond this pointer.

## What it obliges

- **The W37-7 executor**: applies (i)–(iii) in Task 1 Step 3's place. The step is unblocked.
  `.claude/skills/README.md`'s `docs-audit` row is updated in the same commit **only if** the
  skill's summary there stops being accurate — `CLAUDE.md` §12 requires the README to move
  with the skill, and on inspection the row's existing text already states the pointer rule,
  so the likely correct outcome is no README change. That is a judgement at the diff, not a
  licence to skip the check.
- **The planner**: `PL-1070` Task 1 Step 3's wording is superseded by this ruling. The plan
  edit is not this role's; the lead carries it.
- **This ruling deliberately does not decide**: where in `SKILL.md` the two clauses go, what
  the other §5.4 `docs-audit` half-rows require (the four-kinds paragraph, the `YYYY-MM-DD-`
  grammar, the tombstone→redirects swap, the citations), or anything about checks 30–39's
  implementation.

## Acceptance — the violation that must become detectable

**The violation: `RFC-937` §5.4 requires checks 30–39 "described", and a check can be added,
renumbered or repurposed with the skill left silent about it — or, in the other direction, a
second enumeration can be minted in the skill and drift from the script.** Both directions
are real; the corpus has already suffered the second.

- **This ruling adds no automated check, and says so rather than forcing one.** The property
  — "each of ten checks has a describing clause in a prose document" — has no non-fragile
  predicate: any regex for "a describing clause" would accept a bare mention inside a plural
  list, which is precisely the state this ruling found and corrected. A check that would have
  passed on the defect is worse than none, because it converts an open question into a false
  green. **The escalation that produced this ruling is the working detector**, and it worked:
  an executor read the spec's word against the plan's gloss and stopped.

- **What *is* checkable, and is already checked.** The drift the second direction produces —
  a count in prose disagreeing with the code — is what `RFC-756`'s incident recorded, and the
  standing rule that the enumeration lives in exactly one place is what removes the
  population a check would have to range over. *Violation: a second numbered enumeration of
  checks 30–39 appears in `.claude/skills/docs-audit/SKILL.md` or in
  `.claude/skills/README.md`.* This is enforced by review against (i) and (iii), not by a
  script, and the reviewer's predicate is stated here so it is not reinvented: **more than
  one document in the repository listing the checks by number with their subjects.**

- **The measurement in §3 is the re-test.** Re-running the flattened-context sweep quoted
  there over `SKILL.md` after the edit must show a describing clause for all ten, not eight.
  *Violation: any of the ten whose every hit is a bare mention, a date, a count or a range.*
  That predicate is stated in full above and is runnable by a reader holding none of this
  session's context.
