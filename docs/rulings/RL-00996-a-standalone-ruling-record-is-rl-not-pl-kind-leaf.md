---
id: RL-996
family: ruling
title: a standalone ruling record is `RL-`, not `PL- kind: leaf`
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-ruling-a-series-and-standalone-ruling-files.md
---

## RL-996 — a standalone ruling record is `RL-`, not `PL- kind: leaf`

### 1. Verified first, at `01bd0bd`

`_discover_plain_plans`, executed against the real tree, returns each of these as
`prefix=PL`, `kind=leaf`, `owner=planner`:

```
PL- kind=leaf  owner=planner  2026-09-01-ruling-60-census-provenance-checkout-depth.md
PL- kind=leaf  owner=planner  2026-09-01-ruling-61-notes-tombstone-stubs-watched.md
PL- kind=leaf  owner=planner  2026-09-01-nt-0016-slice2-fr-data-32-ruling.md
```

Each is a single ruling record whose title is `# Ruling <n> — …` at `#` depth. The planner
surfaced this as §5.1 and stated, correctly, that *"one ruling per file and need no split"* is
true and **does not settle the family**. It does not, and that is the gap this ruling closes.

**Why the argument is weaker here than for the A-series, stated rather than glossed.** For
A1–A3 the fatal objection to `PL-` was that a section inside a plan has no id, so the external
citations resolve to nothing. **A whole file does get an id**, so these three would resolve — as
`PL-`. The defect is therefore not resolution but **classification**: §1.2 gives `RL` the unit
*one ruling* and the directory `docs/rulings/`, and `PL`'s `kind:` vocabulary is
`map · leaf · review · handover`, none of which is a ruling. A ruling filed as a leaf plan is a
document whose family says it is something it is not.

### 2. Ruled

**A ruling record that occupies its own file takes `RL-`, in `docs/rulings/`, regardless of its
heading depth. The three files above are `RL-`, not `PL- kind: leaf`.**

The predicate is the document's content, not its heading level: **one ruling per file is still
one ruling, and §1.2's unit is one ruling.** Heading depth is how a splitter finds records; it
is not what makes something a ruling.

**Rejected: `PL-`, `kind: leaf` — the status quo.** It resolves, which is why it is not caught
by the A-series' objection, and it is still wrong: it files a ruling under a family whose kind
vocabulary cannot describe it, in a directory the standard reserves for plans.

**Rejected: a new `kind:` on `PL-` for rulings.** §1.12's first lever, and it fails its own
test — a new `kind:` is for *"the same unit, mutability and owner as an existing family"*. A
ruling has a different owner (decision-maker, §1.6) and a different home. §1.12 routes that to a
family, and `RL` already is one.

**Rejected: deferring to a planner derivation, as RL-978 did for the container section.**
That hand-back was right because §5.2's option set had not been enumerated for a unit nobody had
classified. Here the derivation has already read the three, measured what the code does with
them, and §1.2 supplies the unit directly. **A second round would enumerate an option set with
one live member.**

### 3. What it obliges

1. **`_discover_plain_plans` stops claiming a file whose content is a ruling.** Which
   discovery function takes them — a widened ruling splitter, or a prior classification pass —
   is the executor's; that they do not migrate as `PL-` is not.
2. **`owner:` for these three is `decision-maker`**, not `_discover_plain_plans`'s hardcoded
   `planner`. This is the second half of RL-995 §3 item 2, and the two defects are opposite
   in direction: one stamps `decision-maker` on records the lead ruled, the other stamps
   `planner` on records the decision-maker ruled.
3. **The predicate is derived, not listed.** Naming these three files in code would be a
   transcribed enumeration — RL-985's own subject — and would miss the fourth such file the
   moment one is written. The classification reads the document.
4. **This ruling does not decide F68.** See below.

### 4. Acceptance — the violation that must become detectable

**The violation: a document whose body is a ruling migrates into a family that is not `RL`.**

- **A check over the migration's own output: no `PL-` record's body contains a `#`- or
  `##`-level heading of the form `Ruling <token> —`.** *Violation: a ruling inside a plan.* It
  must fail today against the real corpus, naming four files — the three above and the adoption
  document. That is the positive control and the corpus supplies it.
- **A fixture ruling file at `#` depth is classified `RL-`**, and the same file with its
  heading at `##` is classified `RL-` too. *Violation: a classification that changes with
  heading depth* — the assumption that produced the current behaviour.
- **`owner:` on each migrated ruling is the role that ruled it**, read from the record rather
  than from the discovery function that happened to claim the file. *Violation: an owner that is
  a constant.* Two positive controls exist, one per hardcode.

---

## Not ruled — the F68 discharge, which is the lead's

**The planner's §5.2 finding stands and is not resolved by RL-996.** The leaf plan §9
discharges F68 on the ground that *"After the migration, `docs/plans/` holds only `PL-` files
and rulings live in `docs/rulings/` as `RL-` files."* Measured, that premise is false today for
four files, and the leaf plan's own instruction at that point was *"Prove that; do not assume
it."*

**RL-996 makes the premise true; it does not make the discharge sound.** Those are different
things, and conflating them is why this is filed separately rather than folded in:

- A discharge resting on an **assumed** end state is unsound *even when the end state is later
  achieved by other means*. What made it unsound was that nobody ran the splitter.
- The discharge must be re-tested against **what the migration actually produces**, after
  RL-996 is implemented — not against RL-996's text.

**It is a finding against a frozen plan's acceptance reasoning, which `CLAUDE.md` §12 makes the
lead's**, and the lead has already said it should be recorded as such. Recorded here because
this record is where the measurement that falsifies it now lives; the disposition is not mine.

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **F68's discharge** | A finding against a frozen plan's acceptance reasoning | **The lead** — see above |
| **How the range citation `Rulings A1–A3` is rewritten** — consecutive allocation plus a range, or expansion to three ids | An implementation choice with no governance content; RL-995 §3 item 3 fixes only that a substitution cannot do it | **W37-6's executor** |
| **Which discovery function claims a standalone ruling file** | Same — the outcome is ruled, the mechanism is not | **W37-6's executor** |
| **Whether any *other* file's body is a ruling** | A measurement, and RL-996's acceptance item 1 is the instrument for it. I measured four; I did not prove there are only four | **W37-6's executor**, inside RL-985's census |

## Provenance

Row 6, routed by the lead on 2026-09-02 with an instruction to read PR #595 rather than the
summary of it. The derivation's recommendation is adopted with its option table; its strongest
fact was verified independently at `01bd0bd`, its token count was found to be right where my own
narrower pattern was wrong, and the family question inside its §5.1 — which it correctly
declined to settle — is ruled as 87.
