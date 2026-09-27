---
id: RL-983
family: ruling
title: the map-plan roll-up runs through the slices, and has no catch-all
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md
---

## RL-983 — the map-plan roll-up runs through the slices, and has no catch-all

### 1. Verified first, at `1c487b8` (`origin/w37-3-doc-index`, unmerged)

The lead flagged this item as lower confidence and invited a finding that it is not ripe. **It
is ripe.** §1.7's roll-up sentence is *"A map plan rolls up from its slices' leaf plans (all
`closed` → `closed`; any `in progress` → `in progress`)"* — two rules over a seven-value
vocabulary, with no field naming the linkage. `_rollup_map_plan` infers the linkage as
*every `kind: leaf` plan carrying the same `work:`* and completes the rules with
`all in {closed, executed} → executed` and a bare `return "not started"`. The inference is
documented honestly in the function docstring and in the module docstring, which is the
behaviour worth keeping cheap. It is also wrong in three ways that a reader of the docstring
would not predict.

| Claim | Verdict |
|---|---|
| The `work:` proxy is well-founded | **Partly. It is sound in the direction the docstring argues** — a leaf plan's `slice:` resolves to an `SL-` under the same `work:` the map plan carries — **and unsound in the direction that matters**: it enumerates plans, not slices. A slice that has been cut but has no leaf plan yet contributes no child and is invisible to the roll-up |
| Defect 1 — a half-planned Work can read `closed` | **Confirmed by reading the body.** `children` is built from plans only; `if not children: return "not started"`; then `all(s == "closed")`. A Work with five slices where two have closed leaf plans and three have no plan at all yields `children == [closed, closed]` and returns **`closed`**. That is a roadmap reporting progress the repository does not have, which is the failure `CLAUDE.md` §13 exists to prevent |
| Defect 2 — mid-flight reads as not started | **Confirmed.** `states == ["closed", "not started"]` matches no branch and falls to the trailing `return "not started"`. A Work with one slice delivered and one not begun reports **`not started`** |
| Defect 3 — a replanned Work reads as not started | **Confirmed, and it is the worst of the three.** `derive_execution` returns `f"superseded → {superseded_by}"` for a superseded leaf. A slice replanned once and then completed yields `states == ["superseded → PL-m", "closed"]`, matches no branch, and returns **`not started`**. §1.6 makes replanning the normal path (*"planner: new `PL-` with `supersedes:`"*), so this fires on ordinary work, not on an edge case |
| All three share one cause | **Confirmed.** Every one is the trailing `return "not started"` absorbing a combination nobody enumerated. A catch-all in a derivation whose whole purpose is to report state truthfully converts every unhandled case into the most reassuring possible answer |
| §1.7 settles the missing rules | **Refuted.** It states two of them. The rest is genuinely open, which is why this is a ruling and not a bug report |
| The `execution` vocabulary is closed | **Confirmed** — §1.7's table gives exactly `not started`, `in progress`, `executed`, `closed`, `superseded → PL-m`, `retired`, `terminal` |

### 2. Ruled

**Chosen: the roll-up is computed over the map plan's *slices*, one live child per slice, with
an explicit precedence table and no catch-all.** §1.7 says *"its **slices'** leaf plans"*, and
routing through the slices is both what the sentence says and what makes an unplanned slice
visible.

**Children.** For each `SL-` row whose `work:` equals the map plan's `work:`, take that
slice's live leaf plan — the `PL- kind: leaf` whose `slice:` names it and whose `status:` is
neither `superseded` nor `retired`. A slice with no live leaf plan is still a child, and its
state is read from the slice row itself: `draft` → `not started`, `active` → `in progress`,
`closed` → `closed`, `retired` → excluded. A slice with more than one live leaf plan is a
check 33 disagreement, not a case to resolve silently.

**Precedence, in order, over the children that are not excluded:**

| # | Condition | Roll-up |
|---|---|---|
| 1 | no children at all | `not started` |
| 2 | every child excluded, at least one as `retired` | `retired` |
| 3 | any child `in progress` | `in progress` |
| 4 | any child `not started` **and** any child in {`executed`, `closed`} | `in progress` |
| 5 | every child `closed` | `closed` |
| 6 | every child in {`closed`, `executed`} | `executed` |
| 7 | every child `not started` | `not started` |
| — | anything else | **raise; check 33 reports it** |

Rows 3 and 5 are §1.7's two stated rules, in its own order. Row 4 is the correction of defect 2
and is forced by them: a Work part-delivered and part-unstarted is in progress under any
reading of the word. Row 6 completes the vocabulary — everything ran, not everything is closed
out. Rows 1, 2 and 7 are the boundary cases. **The last row is the ruling's substance**: the
derivation has no default, and an unenumerated combination is loud.

**Rejected: keeping the `work:` proxy and only fixing the branch list.** It fixes defects 2 and
3 and leaves defect 1 — the one that reports a half-planned Work as closed — exactly where it
is, because the invisible children are invisible to any branch list.

**Rejected: requiring a new field on the map plan naming its slices.** `plans:` is ledger-only
by §1.5 and a new field is an edit to a closed field set, so this would have gone back to the
maintainer. It is also unnecessary: the linkage already exists, carried by the leaf plan's
`slice:` and the slice row's `work:`, and §1.7's own derivation table is built from exactly
those hops.

**Rejected: leaving the roll-up under-specified and letting check 33 arbitrate.** Check 33
*"fails when the sources disagree"*; it cannot arbitrate a rule that was never written down.
An unwritten rule gets re-invented once per reader, and RFC-937 §1.7's whole design is that
execution is **derived** and therefore has exactly one definition.

**Rejected: declaring the item not ripe and returning it.** The three defects are readable in
the function body at `1c487b8` and each produces a specific wrong value on an ordinary corpus.
Deferring would put check 33 on top of them.

### 3. What it obliges

- **W37-3** replaces `_rollup_map_plan` with the slice-routed derivation and the precedence
  table, removes the trailing catch-all, and keeps the docstring's honest account of what §1.7
  states versus what this ruling adds — citing this record instead of describing the inference
  as its own.
- **W37-4** builds check 33's map-plan comparison against this table, including the
  more-than-one-live-leaf-plan-per-slice disagreement.
- **Nothing in RFC-937 or `document-ids.md` is edited**, and no field is added to any family.

### 4. Acceptance — the violation that must become detectable

1. **The invisible slice.** Fixture: a Work with three slices, one carrying a `closed` leaf
   plan and two carrying no plan and a `draft` slice row. The map plan must read `in progress`.
   **Violation: it reads `closed`** — defect 1, stated as the value that must never appear.
2. **Mid-flight.** Fixture: two slices, one `closed` leaf plan, one `not started`. The map plan
   must read `in progress`. **Violation: it reads `not started`** — defect 2.
3. **Replanned then completed.** Fixture: one slice whose leaf plan A is `superseded` by leaf
   plan B, with B `closed`. The map plan must read `closed`. **Violation: it reads
   `not started`** — defect 3.
4. **No catch-all.** Fixture: a Work every one of whose slices is `retired`. The map plan must
   read `retired`. **Violation: it reads `not started`** — a value produced by a default rather
   than by a rule, which is the single cause all three defects share and the property this
   ruling exists to remove.

---

## What would have gone back to the maintainer

Stated so the boundary is visible rather than implied, and so a future reader can tell that the
delegation was read narrowly by the party it empowered. Two of the three came within one step
of it.

- **Widening §1.5's closed field set** to admit `decision:` on an essay header, which was the
  obvious repair for RL-981's reported contradiction. It is an edit to §1 — the maintainer's
  own text, byte-identical in `document-ids.md` — and it would have gone back. It is not made,
  because the field belongs on the register row and §1.5 never reached it.
- **Adding `phase:` and `work:` to the `FD-` essay header**, which was the obvious repair for
  RL-982. Same reason: it contradicts §1.5's own applicability comment, so it would have
  gone back. It is not made, because §5.2 already puts the placement on the register row.
- **Any edit to `docs/process/document-ids.md`.** §1.6 makes `process/` the maintainer's,
  amendable only by an `RFC-` plus an `RL-`, and the file declares itself a verbatim lift.
  None is made.
- **Any change to RFC-937 §2's D0–D14.** None is made. D0 is applied in RL-981 and is the
  reason its answer is a carrier question rather than a field-set question.
- **Reopening W37-1.** Not needed and not proposed: the two template corrections RL-981
  obliges are one-file edits inside W37-4, the slice that consumes the templates and that has
  not been dispatched.

## Provenance

Written 2026-09-02 by the decision-maker role, under the maintainer's delegation of 2026-09-01
as routed by the lead — recorded above with its date, and recorded there also as **not
load-bearing**, because
[`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) already reaches all
three. **The maintainer did not rule any of these personally.**

Every claim in each `### 1.` table was checked against the repository in this session by the
command named beside it — at `f226891` for the note, the templates and the registers, and at
`1c487b8` for `scripts/doc-index.py`, which is unmerged and named with that revision every time
it is cited. **Nothing was taken from the lead's relay.** Two of the three items were relayed
with a framing this record does not adopt: item 1 was relayed as a contradiction between §1.2a
and §1.5 requiring one of them to yield, and is ruled instead as two carriers that never
collided; item 2 was relayed as a question about `phase:` applicability, and is settled by §5.2
and §5.4, which the relay did not cite and which say the opposite of the answer the §1.5
reading suggested. Item 3's framing — an inference documented in a docstring, offered with low
confidence — was accurate, and the defects it leads to were found by reading the function body
rather than the docstring.
