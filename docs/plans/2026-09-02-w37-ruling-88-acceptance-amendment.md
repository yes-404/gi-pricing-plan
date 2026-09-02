# Ruling 88's second acceptance item, amended after the heading demotion (2026-09-02)

**What this is.** PR #609 (merged as `2fbce0c`) demoted `docs/audit/plan-reviews.md`'s
`Pending proposals` container from `##` to `###` and its three candidates from `###` to `####`.
Nothing moved; only levels changed. That invalidated one of
[Ruling 88](2026-09-02-w37-container-family-and-line-citations-rulings.md)'s acceptance items —
it names a fixture that can no longer be built from the document it describes. **Ruled below as
Ruling 93**, which amends that item and adds one the demotion makes necessary.

**The lead asked for a view on whether #609 was right, offering to treat it as needing a
follow-up. It was right, and the reason is stronger than "nothing moved":** the demotion
converts a *declared* exception into a *derived* one, which is the direction
[Ruling 83](2026-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md) §2 rules toward. §1(c)
shows the census now closing with an empty bucket 3.

**And the regex margin is wider than either report of it.** The planner said one edit, the lead
measured two, and the answer is **three** — §1(d).

## Authority

- **Amending a ruling's acceptance item is a decision about what must become detectable**, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) places with this
  role. The lead correctly declined to make it.
- **It lands as a new dated artifact, never an edit to the merged record** — the rule Ruling 88's
  own Authority section states, applied to Ruling 88.
- **Every figure is measured at `614c92c`**, `origin/main`'s tip when this record was written and
  this branch's base.
- **Nothing else in Ruling 88 is reopened.** The family, the `kind:`, the `status:`, the
  `owner:` disagreement, the P1-over-P2 finding and Ruling 89 all stand.

## Acceptance Standard

`audit-docs.py` check 28 requires this section on dated `docs/plans/` files outside four
suffixes while its own docstring disclaims that scope — register finding F68. Honoured; the
check is not patched from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 93 immediately after 92, no duplicate, no skip.
2. The amended acceptance item is stated as **a violation that must become detectable**, and the
   fixture it names is constructible from the corpus as it now stands — the exact property the
   original lost.
3. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
4. `git diff --stat origin/main...docs/w37-ruling-93-amend-88` names exactly this one new file.
5. Every count below was produced by the command shown, at `614c92c`.

---

## Ruling 93 — the fixture is rebuilt on the property, not the level; and the container is identified positively

### 1. Verified first, at `614c92c`

**(a) The new shape.** `docs/audit/plan-reviews.md`:

```
h1:  2      (one heading; the other is a false positive — see (e))
h2:  0
h3: 12      11 plan reviews + the container
h4: 28      including the three candidates, demoted by #609
```

**(b) The stale clause is real and it is an acceptance item.** Ruling 88 `:144` reads *"A
fixture whose only level-2 heading is followed by three record headings"*. **The file now has
zero level-2 headings**, so the fixture cannot be built from it. Ruling 88 `:67` (*"1155 is `##
Pending proposals`"*) and `:123` (*"exactly one level-2 heading"*) are also stale; both are
descriptive and their substance survives, and they are named here so a reader landing on them
has somewhere to go — not corrected in place.

**(c) #609 was right, and for a reason worth stating.** Ruling 88 ruled the container **is** a
record — an `RFC-`. Records in this file live at `###`. Before #609, a census would have needed
a **bucket 3** entry (Ruling 83 §2): *a `##` heading that is nevertheless a record*, declared in
code with a reason. After #609 the census closes with nothing declared:

| Level | Count | Bucket |
|---|---|---|
| `###` | 12 | **1 — records** (11 `CR- kind: review` + 1 `RFC-`) |
| `####` | 28 | **2 — body, derived**: below the split level |
| `#` | 1 | **2 — preamble, derived** |
| — | 0 | **3 — declared exceptions: empty** |

Ruling 83 §2 holds that a bucket-3 entry *"that could have been derived is a defect in the fix
rather than in the corpus"*. **#609 removed the corpus-side reason for one.** That is a
strictly better state, and it is why the demotion needs no follow-up.

**(d) The margin is three edits, not one and not two.** The container escapes
`_REVIEW_HEADING_RE` because the pattern wants `,` then optional whitespace then the date, and
the heading reads `… close (drafted 2026-08-29)`. Executed against both the shipped pattern and
the widened post-fix one:

```
as it is now                                    shipped=False  widened=False
+ comma                                         shipped=False  widened=False
+ comma, parenthesis removed                    shipped=False  widened=False
+ comma, parenthesis removed, "drafted" removed shipped=True   widened=True
```

**`\s*` cannot cross the word `drafted` any more than it can cross `(`.** The planner reported
one edit, the lead measured two and corrected it, and the answer is three. Each step was
measured more carefully than the last and each was still short. **The margin is wider than
reported, which strengthens the lead's conclusion rather than weakening it** — and the sequence
is a fourth instance of the class Ruling 83 exists for, this time in a *margin* rather than a
count.

**(e) A false positive found in my own probe, which the census must not inherit.** Counting h1
with `^#[^#]` returns **2** for this file. The second is line 2179, `#503)` — a pull-request
reference at the start of a prose line, not a heading. `^#{1,6}\s` returns the correct **1**,
because a markdown heading requires whitespace after the hashes:

```
^#[^#]     on "#503)" → True    on "# Plan reviews" → True
^#{1,6}\s  on "#503)" → False   on "# Plan reviews" → True
```

Ruling 83's census counts *"every heading at any level — `^#{1,6}\s`"*, which is already the
correct form. **This records why that `\s` is load-bearing rather than incidental**, since a
census that counted prose lines as headings would fail to close for a reason that has nothing to
do with the corpus.

### 2. Ruled

**Ruling 88 §4's second acceptance item is replaced. Its violation is unchanged; its fixture is
rebuilt on the property rather than on a heading level.**

**Struck** — Ruling 88 `:144-146`:

> **A fixture whose only level-2 heading is followed by three record headings**, split by
> whatever implements §3 item 1. *Violation: a section that runs to end of file because its
> close was derived from heading level.* This must fail against any *"to the next `##`"* rule.

**Substituted:**

> **A fixture in which a non-record section and the records following it share one heading
> level, and no heading of any higher level exists in the file.** *Violation: a section whose
> close is derived from heading level.* Under the corpus as it now stands this is stronger than
> the struck form, not weaker: with **zero** level-2 headings, a rule reading *"to the next
> `##`"* runs to end of file from **any** starting point, not only from the container's. The
> fixture is constructible from `docs/audit/plan-reviews.md` itself, which is the property the
> struck item lost.

**Added**, because the demotion creates a fragility the struck item did not anticipate:

> **The container is identified positively, never by `_REVIEW_HEADING_RE` failing to match it.**
> *Violation: a classifier that reaches the container by elimination.* A negative test says
> "this `###` is not a review", which is true today by three edits (§1(d)) and would silently
> reclassify the container into a `CR- kind: review` if any of them were ever made. Ruling 88 §3
> item 1 already requires the container be *"found as a section"*; this makes the requirement
> testable — the fixture is the container's heading edited to match the review pattern, and the
> classifier must still produce an `RFC-`.

**Why the violation is not restated in weaker terms.** The struck item's target — a close
derived from heading level — is the same defect, and #609 widened its blast radius rather than
removing it. **An acceptance item whose fixture stops being constructible is not evidence the
violation went away**, and treating it as such is how a check quietly stops testing anything.

### 3. What it obliges

1. **Ruling 88 §4's second item is read as substituted from this record's date.** Ruling 88 is
   not edited.
2. **Ruling 88 `:67` and `:123` stand as written, stale in their heading-level detail**, with
   this record as the correction a reader is pointed to. The line ranges in `:67` — 1155–1232 —
   are unaffected and remain correct.
3. **The leaf plan's §5.2 and the container derivation's two sites are the planner's**, `active`
   and frozen; the lead reports the planner's own recommendation is that the correction rides
   with whatever next touches the plan. **Not ruled here and not disputed.**
4. **#609 needs no follow-up.** §1(c).

### 4. Acceptance — the violation that must become detectable

Stated for this amendment itself, since an amendment that cannot be checked is the defect it
corrects:

- **`grep -c '^##[^#]' docs/audit/plan-reviews.md` returns 0, and the census still closes** with
  bucket 3 empty. *Violation: a census that needed a declared exception for the container after
  #609* — which would mean the demotion did not achieve §1(c).
- **The classifier produces an `RFC-` for a container heading edited to match the review
  pattern.** *Violation: the container reclassified as a review by a three-edit change to its
  own title.*
- **No acceptance item anywhere in `docs/plans/` names a fixture that cannot be built from the
  corpus it describes.** *Violation: this class, recurring.* One instance is now known; whether
  it is the only one is a measurement nobody has run — routed below.

---

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **Whether other acceptance items name unbuildable fixtures** | §1(b) found one because the lead's structural change surfaced it. A sweep over every filed acceptance item is a measurement, not a decision | **The lead**, as a small sweep — twelve ruling records now carry acceptance items |
| **The two stale sites in the container derivation and the leaf plan §5.2** | Both the planner's; the plan is `active` and frozen | **The planner**, riding with the next touch, as it recommended |
| **Whether `#609`'s demotion should be mirrored in the roadmap's own mis-nestings** | Ruling 92 §3 routed the `#### Phase 1b status` case to the lead as a finding; the same treatment may apply | **The lead**, unchanged |

## Provenance

Raised by the lead on 2026-09-02, naming its own merge as the cause and identifying which of the
six stale sites needed a ruling rather than a correction. That triage was right: five are
descriptive and one is an acceptance item. The view it asked for on #609 is given in §1(c) and
is an endorsement; the margin correction in §1(d) goes the other way from the lead's, and makes
its position safer rather than less safe.
