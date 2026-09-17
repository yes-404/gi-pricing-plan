---
id: RL-995
family: ruling
title: the `RL-902`–`A3` series becomes three `RL-` records
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

# The `RL-902`–`A3` series, and the standalone ruling files beside them, ruled (2026-09-02)

**What this is.** Register row 6. The planner returned
`docs/plans/PL-00968-the-rl-902-a3-series-what-they-are-and-the-family-they-take-a-derivation-for-ruling-2026-09-02.md` — **PR #595, open and not yet
merged, which is why it is cited by path rather than linked here** — recommending three `RL-`
records for the `RL-902`–`A3` series, and surfaced three things it said were not the family
question. **This record therefore merges after #595 or its citation dangles**; it adopts that
derivation's option table by reference and does not restate it. **Two rulings follow: 86 adopts the
recommendation; 87 rules a family question hiding inside the third surfaced item, which the
derivation correctly declined to settle.**

**The derivation is adopted rather than re-derived, and its strongest fact was verified
independently.** Its §1(d) claims a *ruling record* cites `RL-903` as precedent — the single
thing that distinguishes a ruling from a section of a plan. Read at `01bd0bd`,
`docs/rulings/RL-00920-q2-is-answered-differently-for-c2-and-c3-c3-is-dissolved-c2-gets-claude-settings-json-and-slice-g-is-re-cut-and-still-blocked.md:86`:

> place to look and a second place to go stale, **which is the argument RL-903 already made**

That is a ruling record treating `RL-903` as an authority. A plan subsection does not get
cited that way, and no option that leaves the three without an id can honour it.

**One correction to the derivation, in its favour.** Its *"21 tokens, 15 outside"* is right and
my first check disagreed — I counted `\bRuling A[0-9]+\b` and got **18/13**. The derivation
counted the plural form too. Both patterns run at `01bd0bd`:

```
\bRuling A[0-9]+\b    → 18 (13 outside the adoption document)
\bRulings? A[0-9]+\b  → 21 (15 outside)
```

The three-token gap is `Rulings A1–A3`, a **range citation**, and §3 below carries what that
costs. **I made the narrower-pattern error twice in one session** — the other was RL-985
§1(g)'s work count, which missed 26 struck-through rows — and record it here for the same
reason: it is the defect RL-985 rules against, and its recurrence in the same session, by
its own author, is the strongest evidence available that the census must not be counted with a
hand-written pattern.

## Authority

- **Routed by the lead** under the maintainer's delegation of 2026-09-01
  ([`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md)
  §1); neither ruling falls in its §2 exclusions.
- **RL-995 follows the RL-978 and 84 pattern**: the planner derives the option set, the
  decision-maker rules it. The derivation's §6 states that shape explicitly and this record
  completes it.
- **RL-996 is a spec-versus-code conflict**, which
  [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) places with this
  role: `_discover_plain_plans` assigns `PL-`, `kind: leaf` to documents RFC-937 §1.2 gives the
  unit *"one ruling"*. **It was surfaced by the planner and routed by the lead as a finding, not
  as a decision.** The finding — that it falsifies the leaf plan's F68 discharge — stays the
  lead's and is not ruled here; the family question underneath it is ruled, because the
  migration will otherwise ship a family the standard contradicts.
- **Every figure is measured at `01bd0bd`**, `origin/main`'s tip when this record was written
  and the commit this branch is cut from — a fresh branch, per the lead's instruction, `#593`
  and `#594` having landed since the previous cut.
- **Re-read under [`delivery-process.md`](../process/delivery-process.md) §15 Rule 10** —
  *"a branch open when a ruling merges is re-read against that ruling before the branch itself
  merges."* **RL-997 merged as `e74a683` (#596) while this branch was open**, and the re-read
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
   separated them; for RL-995 the option table is the derivation's and is adopted by
   reference rather than restated, with the verification that was added to it.
3. Each acceptance is stated as a violation that must become detectable.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-ruling-86-a-series` names exactly this one new file.
6. Every claim about a script's behaviour was produced by executing it; every quotation is
   verbatim from the artifact named.

---

## RL-995 — the `RL-902`–`A3` series becomes three `RL-` records

### 1. Verified first, at `01bd0bd`

The derivation's §1 and §2 were re-run rather than accepted. Four checks:

| Claim | Result |
|---|---|
| A ruling record cites `RL-903` as precedent | **Confirmed** — `2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md:237`, quoted above |
| The three carry the canonical reject-then-rule shape | **Confirmed** — A1 at `:67` reads *"**Rejected, and the reason matters more than the choice.**"* then *"**Ruled: `.claude/skills/secret-hygiene`.**"* |
| A bounded, dated delegation | **Confirmed** — `:25`, *"authorise you to approve RFC-842 RFC-843 and RFC-895 landing on behalf of me"* |
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
identifier standard has no field for "authored under a delegation", and RL-995 does not
invent one. The `A` semantic is preserved where it belongs — in `was:`, and in each record's own
body, which says who ruled it and under what grant.

### 3. What it obliges

The derivation's five obligations are adopted. Three carry additions:

1. **`_RULING_HEADING_RE` widens on two axes** — heading level *and* token shape. A fix to
   either alone reds nothing and looks green, which is the derivation's own false-green case.
2. **`owner:` is not `decision-maker` for these three**, per `scripts/doc-id.py:1150`'s
   hardcode. **And there is a second, symmetrical one the derivation did not have:**
   `_discover_plain_plans` hardcodes `owner="planner"`, measured by execution —
   so the three standalone ruling files of RL-996 would migrate attributed to the planner.
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

**The violation: a governed document cites `RL-902`, `A2` or `A3` and the citation resolves
to nothing — while the acceptance sweep reports success.**

- **Acceptance item (d)'s sweep matches the `A` forms.** Executed at `01bd0bd`, `\bRuling \d+\b`
  returns `False` for `'RL-902'`, `'Rulings A1-A3'` **and** `'Rulings A1–A3'` (en dash), and
  `True` for `'RL-987'`. *Violation: (d) passing while 21 legacy tokens survive unrewritten* —
  which is the state today. This must red before the migration, not after.
- **A fixture carrying `Rulings A1–A3` proves the range case.** *Violation: a range citation
  rewritten to a single id, or left as a legacy token.*
- **Each of the three new `RL-` records carries an `owner:` that is not `decision-maker`.**
  *Violation: a frozen record attributing a decision to a role that did not make it.* The
  positive control is today's `scripts/doc-id.py:1150`.
- **The residual `PL-` has no empty heading.** *Violation: a split that leaves a heading with no
  body* — a defect the split creates rather than one it inherits.

---
