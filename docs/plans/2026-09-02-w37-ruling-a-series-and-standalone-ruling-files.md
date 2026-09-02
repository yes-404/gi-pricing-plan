# The `Ruling A1`–`A3` series, and the standalone ruling files beside them, ruled (2026-09-02)

**What this is.** Register row 6. The planner returned
`docs/plans/2026-09-02-w37-ruling-a-series-family-derivation.md` — **PR #595, open and not yet
merged, which is why it is cited by path rather than linked here** — recommending three `RL-`
records for the `Ruling A1`–`A3` series, and surfaced three things it said were not the family
question. **This record therefore merges after #595 or its citation dangles**; it adopts that
derivation's option table by reference and does not restate it. **Two rulings follow: 86 adopts the
recommendation; 87 rules a family question hiding inside the third surfaced item, which the
derivation correctly declined to settle.**

**The derivation is adopted rather than re-derived, and its strongest fact was verified
independently.** Its §1(d) claims a *ruling record* cites `Ruling A2` as precedent — the single
thing that distinguishes a ruling from a section of a plan. Read at `01bd0bd`,
`docs/plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md:237`:

> place to look and a second place to go stale, **which is the argument Ruling A2 already made**

That is a ruling record treating `Ruling A2` as an authority. A plan subsection does not get
cited that way, and no option that leaves the three without an id can honour it.

**One correction to the derivation, in its favour.** Its *"21 tokens, 15 outside"* is right and
my first check disagreed — I counted `\bRuling A[0-9]+\b` and got **18/13**. The derivation
counted the plural form too. Both patterns run at `01bd0bd`:

```
\bRuling A[0-9]+\b    → 18 (13 outside the adoption document)
\bRulings? A[0-9]+\b  → 21 (15 outside)
```

The three-token gap is `Rulings A1–A3`, a **range citation**, and §3 below carries what that
costs. **I made the narrower-pattern error twice in one session** — the other was Ruling 83
§1(g)'s work count, which missed 26 struck-through rows — and record it here for the same
reason: it is the defect Ruling 83 rules against, and its recurrence in the same session, by
its own author, is the strongest evidence available that the census must not be counted with a
hand-written pattern.

## Authority

- **Routed by the lead** under the maintainer's delegation of 2026-09-01
  ([`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md)
  §1); neither ruling falls in its §2 exclusions.
- **Ruling 86 follows the Ruling 82 and 84 pattern**: the planner derives the option set, the
  decision-maker rules it. The derivation's §6 states that shape explicitly and this record
  completes it.
- **Ruling 87 is a spec-versus-code conflict**, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) places with this
  role: `_discover_plain_plans` assigns `PL-`, `kind: leaf` to documents NT-0019 §1.2 gives the
  unit *"one ruling"*. **It was surfaced by the planner and routed by the lead as a finding, not
  as a decision.** The finding — that it falsifies the leaf plan's F68 discharge — stays the
  lead's and is not ruled here; the family question underneath it is ruled, because the
  migration will otherwise ship a family the standard contradicts.
- **Every figure is measured at `01bd0bd`**, `origin/main`'s tip when this record was written
  and the commit this branch is cut from — a fresh branch, per the lead's instruction, `#593`
  and `#594` having landed since the previous cut.
- **Re-read under [`delivery-process.md`](../process/delivery-process.md) §15 Rule 10** —
  *"a branch open when a ruling merges is re-read against that ruling before the branch itself
  merges."* **Ruling 85 merged as `e74a683` (#596) while this branch was open**, and the re-read
  was done: it adds one file, `git diff --name-only 01bd0bd e74a683` lists only that record, and
  it touches nothing cited here. Its subject — whether §8's stage list binds — does not reach a
  family assignment, so **no conclusion in either ruling below is affected**. Recorded because
  the rule asks for the re-read whether or not it changes anything, and a re-read that found
  nothing is worth distinguishing from one that was never done.
- **No note, template or filed plan is edited.**

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims that scope — register finding F68,
whose discharge §3 below shows to be unsound. Honoured here; the check is not patched from this
branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 86–87 immediately after 85, no duplicate, no
   skip. 85 is on open PR #596.
2. Each ruling names the chosen option **and every rejected option**, with the evidence that
   separated them; for Ruling 86 the option table is the derivation's and is adopted by
   reference rather than restated, with the verification that was added to it.
3. Each acceptance is stated as a violation that must become detectable.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-ruling-86-a-series` names exactly this one new file.
6. Every claim about a script's behaviour was produced by executing it; every quotation is
   verbatim from the artifact named.

---

## Ruling 86 — the `Ruling A1`–`A3` series becomes three `RL-` records

### 1. Verified first, at `01bd0bd`

The derivation's §1 and §2 were re-run rather than accepted. Four checks:

| Claim | Result |
|---|---|
| A ruling record cites `Ruling A2` as precedent | **Confirmed** — `2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md:237`, quoted above |
| The three carry the canonical reject-then-rule shape | **Confirmed** — A1 at `:67` reads *"**Rejected, and the reason matters more than the choice.**"* then *"**Ruled: `.claude/skills/secret-hygiene`.**"* |
| A bounded, dated delegation | **Confirmed** — `:25`, *"authorise you to approve NT-0012 NT-0013 and NT-0014 landing on behalf of me"* |
| The adoption file migrates today as one `PL-`, `kind: leaf` | **Confirmed by execution** — `_discover_plain_plans` returns it with `prefix=PL`, `kind=leaf` |

### 2. Ruled

**Option (a): three `RL-` records, split out of §3 of the adoption document, each
`status: active`, `created: 2026-08-30`, each carrying `was:` the adoption file's path and its
old token.**

The derivation's option table is adopted, and its decisive line is §1.2's: **`RL`'s unit is
*one ruling*, and there are three.** Options (b), (c), (d) and (e) are rejected on the grounds
it states, one of which I want to restate because it is the one a later reader will test:
**option (c), leaving them as body inside the `PL-`, is the option that looks free and is not.**
§1.7's resolver cannot resolve a section inside a plan, so the two external citations would
point at nothing — and one of them is a ruling record citing a precedent.

**On the letter as a semantic.** The derivation reads `A` as marking *authorship under
delegation* rather than absence of a number, evidenced by the numbered sequence running to 48
and 53 the same day. I adopt that reading, and note what it does **not** license: the
identifier standard has no field for "authored under a delegation", and Ruling 86 does not
invent one. The `A` semantic is preserved where it belongs — in `was:`, and in each record's own
body, which says who ruled it and under what grant.

### 3. What it obliges

The derivation's five obligations are adopted. Three carry additions:

1. **`_RULING_HEADING_RE` widens on two axes** — heading level *and* token shape. A fix to
   either alone reds nothing and looks green, which is the derivation's own false-green case.
2. **`owner:` is not `decision-maker` for these three**, per `scripts/doc-id.py:1150`'s
   hardcode. **And there is a second, symmetrical one the derivation did not have:**
   `_discover_plain_plans` hardcodes `owner="planner"`, measured by execution —
   so the three standalone ruling files of Ruling 87 would migrate attributed to the planner.
   **Two hardcoded owners, each wrong for a different set, neither visible from the family
   question.**
3. **The token rewrite must handle the range form.** `Rulings A1–A3` is not a token
   substitution: one citation becomes three ids, which are contiguous only if allocated
   together. The rewrite either allocates the three consecutively and emits a range, or expands
   the citation. **Deciding which is the executor's; noticing that a substitution cannot do it
   is this ruling's.**
4. **The 21 tokens are rewritten**, which requires the sweep gap closed first — see §4.
5. **The residual `PL-` is checked for sense**: after §3's subsections leave, its §3 heading has
   nothing under it and its §4 acceptance table still cites *"Rulings A1–A3"*.

### 4. Acceptance — the violation that must become detectable

**The violation: a governed document cites `Ruling A1`, `A2` or `A3` and the citation resolves
to nothing — while the acceptance sweep reports success.**

- **Acceptance item (d)'s sweep matches the `A` forms.** Executed at `01bd0bd`, `\bRuling \d+\b`
  returns `False` for `'Ruling A1'`, `'Rulings A1-A3'` **and** `'Rulings A1–A3'` (en dash), and
  `True` for `'Ruling 66'`. *Violation: (d) passing while 21 legacy tokens survive unrewritten* —
  which is the state today. This must red before the migration, not after.
- **A fixture carrying `Rulings A1–A3` proves the range case.** *Violation: a range citation
  rewritten to a single id, or left as a legacy token.*
- **Each of the three new `RL-` records carries an `owner:` that is not `decision-maker`.**
  *Violation: a frozen record attributing a decision to a role that did not make it.* The
  positive control is today's `scripts/doc-id.py:1150`.
- **The residual `PL-` has no empty heading.** *Violation: a split that leaves a heading with no
  body* — a defect the split creates rather than one it inherits.

---

## Ruling 87 — a standalone ruling record is `RL-`, not `PL- kind: leaf`

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

**Rejected: deferring to a planner derivation, as Ruling 82 did for the container section.**
That hand-back was right because §5.2's option set had not been enumerated for a unit nobody had
classified. Here the derivation has already read the three, measured what the code does with
them, and §1.2 supplies the unit directly. **A second round would enumerate an option set with
one live member.**

### 3. What it obliges

1. **`_discover_plain_plans` stops claiming a file whose content is a ruling.** Which
   discovery function takes them — a widened ruling splitter, or a prior classification pass —
   is the executor's; that they do not migrate as `PL-` is not.
2. **`owner:` for these three is `decision-maker`**, not `_discover_plain_plans`'s hardcoded
   `planner`. This is the second half of Ruling 86 §3 item 2, and the two defects are opposite
   in direction: one stamps `decision-maker` on records the lead ruled, the other stamps
   `planner` on records the decision-maker ruled.
3. **The predicate is derived, not listed.** Naming these three files in code would be a
   transcribed enumeration — Ruling 83's own subject — and would miss the fourth such file the
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

**The planner's §5.2 finding stands and is not resolved by Ruling 87.** The leaf plan §9
discharges F68 on the ground that *"After the migration, `docs/plans/` holds only `PL-` files
and rulings live in `docs/rulings/` as `RL-` files."* Measured, that premise is false today for
four files, and the leaf plan's own instruction at that point was *"Prove that; do not assume
it."*

**Ruling 87 makes the premise true; it does not make the discharge sound.** Those are different
things, and conflating them is why this is filed separately rather than folded in:

- A discharge resting on an **assumed** end state is unsound *even when the end state is later
  achieved by other means*. What made it unsound was that nobody ran the splitter.
- The discharge must be re-tested against **what the migration actually produces**, after
  Ruling 87 is implemented — not against Ruling 87's text.

**It is a finding against a frozen plan's acceptance reasoning, which `CLAUDE.md` §12 makes the
lead's**, and the lead has already said it should be recorded as such. Recorded here because
this record is where the measurement that falsifies it now lives; the disposition is not mine.

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **F68's discharge** | A finding against a frozen plan's acceptance reasoning | **The lead** — see above |
| **How the range citation `Rulings A1–A3` is rewritten** — consecutive allocation plus a range, or expansion to three ids | An implementation choice with no governance content; Ruling 86 §3 item 3 fixes only that a substitution cannot do it | **W37-6's executor** |
| **Which discovery function claims a standalone ruling file** | Same — the outcome is ruled, the mechanism is not | **W37-6's executor** |
| **Whether any *other* file's body is a ruling** | A measurement, and Ruling 87's acceptance item 1 is the instrument for it. I measured four; I did not prove there are only four | **W37-6's executor**, inside Ruling 83's census |

## Provenance

Row 6, routed by the lead on 2026-09-02 with an instruction to read PR #595 rather than the
summary of it. The derivation's recommendation is adopted with its option table; its strongest
fact was verified independently at `01bd0bd`, its token count was found to be right where my own
narrower pattern was wrong, and the family question inside its §5.1 — which it correctly
declined to settle — is ruled as 87.
