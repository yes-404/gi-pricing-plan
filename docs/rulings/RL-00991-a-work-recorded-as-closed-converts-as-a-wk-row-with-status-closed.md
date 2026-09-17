---
id: RL-991
family: ruling
title: a work recorded as closed converts, as a `WK-` row with `status: closed`
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-roadmap-transform-rulings.md
---

# What the roadmap transform produces — closed works, multi-row works, and the archival mention, ruled (2026-09-02)

**What this is.** Three questions routed together by the lead because they are one subject: what
`§4 step 3` actually emits. `_discover_roadmap` converts 0 of 41 works today and the executor
rebuilding it refuses all-or-nothing rather than converting the unambiguous subset — *"a file
with some works converted and others still in legacy prose is a fourth, worse shape"* — so these
three block the restructure entirely. Ruled below as Rulings 90, 91 and 92.

**None of the three is the maintainer's.** The lead offered to carry Q1 in the go-ahead package
on the ground that it touches what the roadmap *means*. It does not need to: **acceptance item
(k) already decides it**, mechanically, and §1 below shows how. The other two are settled by
§1.2's own columns and by a dependency reference in the corpus.

**One thing found while verifying, which the routing brief had slightly wrong and which changes
Q3's grounds rather than its answer.** `WK-662`'s row is **not** under *"Original scope, for
reference"*. That heading (line 317) contains only Goal and Demo-able-outcome prose; `WK-662`'s row
is at line 336, under the **sibling** heading `### Workstreams` (327). Q3 therefore cannot be
answered by asking how far an archival heading's scope reaches — and it does not need to be.

## Authority

- **Routed by the lead** under the maintainer's delegation of 2026-09-01
  ([`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md))
  §1; none of the three falls in its §2 exclusions, and §2 of each ruling below says what makes
  it a derivation from the standard rather than a scope choice.
- **Every figure is measured at `f4cbbb7`**, `origin/main`'s tip when this record was written
  and this branch's base.
- **No note, template or filed plan is edited.** Two limitations in the standard are surfaced
  for the maintainer's `RFC-` route rather than worked around silently.

## Acceptance Standard

`audit-docs.py` check 28 requires this section on dated `docs/plans/` files outside four
suffixes while its own docstring disclaims that scope — register finding F68, whose discharge
RL-996 showed unsound. Honoured; the check is not patched from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 90–92 immediately after 89, no duplicate, no
   skip.
2. Each ruling states the chosen answer **and what happens to what it does not choose** — the
   lead's explicit condition on Q2, applied to all three.
3. Each acceptance is a violation that must become detectable.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-rulings-90-92-roadmap-transform` names exactly this
   one new file.
6. Every count and every heading attribution below was produced by the command shown, not read
   off a summary — including the one that corrected the routing brief.

---

## RL-991 — a work recorded as closed converts, as a `WK-` row with `status: closed`

### 1. Verified first, at `f4cbbb7`

**§1.2's `WK` row supplies the vocabulary directly:**

```
| Row | Work | `WK` | docs/roadmap.md, under its milestone | one work item | living row
| draft → active → closed | retired | — |
```

`closed` is in the subset. A standard that offers a status for closed works and then does not
emit them would have written a word it never uses.

**And acceptance item (k) settles it mechanically.** §7(k) requires *"`doc-index.py --phase P1b`
produces the report §1.10 describes"*. `phase_report` (`scripts/doc-index.py:811`) opens with:

```python
closed_works = [w.header for w in work_headers if w and w.header.status == "closed"]
retired_works = [w.header for w in work_headers if w and w.header.status == "retired"]
```

**Its first line is a count of closed and retired works.** P1a and P1b are the closed phases. If
closed works do not convert, (k)'s report for the phase it names reports zero closed works —
a report that is not the one §1.10 describes, on the phase the acceptance item picks.

### 2. Ruled

**A work recorded as closed converts, as a `WK-` row carrying `status: closed`, under its
milestone.** The six ids the executor blocked on — `WK-666`, `WK-669`, `WK-670`, `WK-671`, `WK-692`, `WK-693` —
convert on that basis.

**Why this is not the maintainer's**, which the lead invited me to test: the question reads like
one about what the roadmap means, and it is answered without deciding that. §1.2 supplies the
status word and §7(k) requires a report that counts it. **A ruling that has to choose between
two readings of the roadmap's purpose would be the maintainer's; this one only reads the
standard.**

**`status:` comes from the Status cell, never from the decoration.** RL-985 §1(g) established
that `WK-661` and `WK-665` each head rows carrying both the struck and unstruck forms, so a strike is
typography. The date and word in the Status cell are the source.

### 3. What happens to what it does not choose

Nothing is dropped: this ruling adds no exclusion. The alternative — not converting closed
works — would have silently removed 6 ids from the corpus and left every citation of them
unresolvable, which is the shape §4 step 3 exists to prevent.

### 4. Acceptance — the violation that must become detectable

**The violation: a work with a closed Status cell is absent from the migrated roadmap.**

- **`doc-index.py --phase P1a` and `--phase P1b` each report a non-zero closed-work count**, and
  the ids match the Status cells read from the pre-migration file. *Violation: a phase report
  whose closed-work list is empty for a closed phase* — which is the state the rejected reading
  produces, and it passes every other check.
- **A count assertion with its denominator: 41 work ids in, 41 `WK-` rows out.** *Violation: a
  conversion that silently drops a partition.* Derived from the census, not hand-written
  (RL-985).

---
