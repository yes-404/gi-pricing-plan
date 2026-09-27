---
id: FD-1012
family: finding
title: `.claude/roles/reporter.md`'s Mechanism section still describes a single-signal lead-staleness nudge; the shipped detector has been a three-signal conjunction since 2026-09-01
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F74.md
---

# F74 — `.claude/roles/reporter.md`'s Mechanism section still describes a single-signal lead-staleness nudge; the shipped detector has been a three-signal conjunction since 2026-09-01

Evidence essay for the register row self-named `(F74)` in `docs/findings/register.md`. The
finding: the reporter's charter states, as its own procedural description, a lead-staleness
nudge design (marker age alone, over 20 minutes) that `nudge.py` stopped running on
2026-09-01. The charter was not updated when the detector was fixed, so it now
affirmatively misdescribes a currently-shipped, governed mechanism.

## Provenance

Dispatched by the lead as a to-verify-independently task, with an explicit instruction to
refuse filing if the claim did not hold and to test the "why it matters" argument hardest.
Re-derived from primary sources below rather than taken on the dispatch's own citations.
Measured against `main` = `39ee30c` throughout, in a dedicated worktree — one early misstep
is worth recording against future audits of this kind: a first pass at `register.md` and
`reporter.md` used the path `/home/puzhenhao1989/gi-pricing-plan/...` (the shared checkout,
whose local `main` sits behind `origin/main`) instead of the worktree's own copy. `reporter.
md` and `nudge.py` turned out to be byte-identical between the two, so nothing here was
affected, but `register.md` was not — the shared checkout was missing F71/F72/F73 entirely.
Caught by a plain `diff` between the two copies before any conclusion was drawn from the
stale one; every register-derived claim below is re-checked against the worktree's copy.

## The charter, read in full, not only the lines a dispatch quoted

`.claude/roles/reporter.md` is 88 lines; both places that describe the nudge were read in
full.

**The `Owns` bullet, line 7:** "nudge the lead when the status line is over 20 minutes
stale, escalate to the user channel as a critical relay if unanswered."

**The full `## Mechanism: Lead freshness nudge` section, lines 49-78** — quoted at the parts
that state the design:

> **What it does:** Monitors the lead's status-line age. If stale >20 minutes, sends a
> nudge via SendMessage. (line 51, condensed)
>
> **How it works:** 1. The reporter writes the marker file... 2. On each 15-min cycle,
> `nudge.py` checks marker age vs. current time 3. If delta > 20 min (staleness threshold),
> it emits a nudge signal... (lines 58-63, condensed; the omitted words name no second
> signal)

No line in reporter.md's 88 lines mentions `eta.md` or `origin/main` as a nudge input.
Confirmed by reading the whole file, not a keyword search of only the Mechanism section:
`eta.md` is named once elsewhere (line 29, listing what the Slack post contains — an
unrelated section), and `origin/main` does not appear in the file at all.

## The shipped detector, read directly

`.claude/skills/reporter-cycle/scripts/nudge.py` (237 lines). `lead_is_stale`, line 150:

```python
return all(
    _is_stale(age, threshold_seconds) for age in (marker_age, eta_age, main_age)
)
```

Three ages from three independent sources (`marker_age_seconds`, `eta_age_seconds`,
`main_commit_age_seconds`, lines 81-131) under a genuine `all()` — a nudge requires every
one of the three to be stale, not any one. The module docstring dates the change: "Multi-
signal liveness (2026-09-01)... This now checks THREE independent liveness signals."

**Live, not just static.** `~/gi-pricing-plan.local/handover/nudge.log` (local, untracked)
shows the logged *format itself* change on the same date. Through `2026-09-01T10:45:01Z`,
every line reads `lead status <N> min old` — one number. From `2026-09-01T21:00:01Z` on,
every line reads `marker <N> min, eta <N> min, main <N> min (all >20.0 min threshold)` —
three numbers, explicitly ANDed. Most recent entries, checked against the tree this finding
is measured at:

```
2026-09-02T03:15:02Z - nudge sent - marker 218.7 min, eta 30.0 min, main 47.2 min (all >20.0 min threshold)
2026-09-02T03:45:01Z - nudge sent - marker 28.8 min, eta 30.0 min, main 77.2 min (all >20.0 min threshold)
```

## Where the correct design is written down

`~/gi-pricing-plan.local/handover/report-spec.md` §5 (local, untracked, 119 lines, read in
full) states the three-signal design and dates it: "revised 2026-09-02... Nudge the lead
only when **all three** are stale beyond 20 minutes: the marker, `eta.md`, and
`origin/main`." Its closing paragraph names this exact divergence and declines to fix it,
quoted verbatim: "`.claude/roles/reporter.md` still describes a single-signal nudge at 20
minutes, the design the 2026-09-01 false positive disproved... — a finding against the
charter under `CLAUDE.md` §15, not something to edit here." Matches the dispatch's citation
exactly.

**`.claude/skills/reporter-cycle/SKILL.md` also carries the correct design, and it is
neither local nor untracked.** 308 lines, committed to the repository. Dated entry at line
238: "2026-09-01 — the single-signal nudge produced a false positive at the busiest moment,
so `nudge.py` now requires all three available liveness signals to be stale," followed by
the same three sources, the same conjunction, the same incident — the marker read 25.4
minutes stale at 10:45Z while the lead had, in that same window, merged six PRs, restarted
two executors and dispatched two roles — and a TDD proof (`test_nudge.py`, 15 tests, both
directions, including a negative control: any one fresh signal blocks the nudge regardless
of the other two). This is a materially more complete and more current account than
`report-spec.md`'s own, and it is exactly the document `.claude/roles/reporter.md` itself
names as authoritative for procedure — see next section.

## What the dispatch got right, and the one part it overstated

The core claim — charter says single-signal, shipped detector is three-signal, the local
spec file names the gap and declines to fix it — is confirmed in every particular above,
against primary sources read directly.

**One part of the "why it matters" argument does not hold as stated.** The dispatch:
"The specification of the working design currently survives only in a local file and in a
running agent's context, neither of which survives a respawn." `.claude/roles/reporter.md`
itself contradicts this, in a passage the dispatch did not quote (lines 13-17): "This file
states the WHAT and the numbers; that skill [`reporter-cycle`] states the HOW. **Precedence:
the skill is authoritative.**" `.claude/skills/reporter-cycle/SKILL.md` is committed,
survives every respawn exactly as the charter itself does, and — verified above — correctly
and currently documents the three-signal design in more depth than the local file does. Nor
does a respawn cause the detector itself to regress: `nudge.py` is checked-in code a
respawned reporter *runs* (by arming the `reporter-cycle.sh` Monitor per the charter's own
"Arming" paragraph), not prose it re-implements from the charter's Mechanism section — no
step in reporter.md's 88 lines asks the agent to write or re-derive the staleness predicate.

**What the risk actually is, corrected.** Not "the mechanism silently downgrades on
respawn" — the code does not move. It is that the charter contains a specific, detailed and
wrong procedural claim about a governed, currently-shipped mechanism, sitting in the one
document `CLAUDE.md` §15 says a role is built from. A reporter (or any reader — the lead,
the maintainer, a future auditor) who reads the charter's own Mechanism section and stops
there, rather than following its own pointer to the skill, forms a wrong model of when and
why the alarm fires — including, concretely, dismissing or mis-explaining a correctly-
firing three-signal nudge as if it were the single stale-marker design already disproved.
The charter's own text staying accurate is what a role file is for; this section of it does
not.

## Distinguishing this from open rows that touch the same code

Checked directly against the register at `main` = `39ee30c`, not against row labels — the
error this session already had to correct once (the F26 mislabelling in PR #561's merge
commit).

- **F26** (open) — no CI workflow watches `.claude/roles/**` or `.claude/skills/**` at all.
  Read in full: a general trigger-coverage gap naming no content defect in any charter, and
  not mentioning `reporter.md`'s nudge mechanism. Cited here only as *why nothing automated
  caught this specific drift* — the same relationship the register already states between
  F26 and F71 ("different workflow, different symptom, different fix; siblings in shape,
  not the same finding"). Not a duplicate.
- **F33** (open) — `mypy`'s `files` list does not cover `scripts/`, `.claude/skills/` test
  code, or the repo-root `tests/` tree. Read in full: static-analysis coverage, unrelated to
  nudge design or charter content. Not a duplicate.
- **F72** (open) — `write_runtime_state.py`'s `written_at` cannot distinguish "checked, no
  change" from "not checked." Read in full: a different artifact (`runtime-state.json`), a
  different question (a field's staleness expressiveness), no mention of `reporter.md`. Not
  a duplicate.
- **F73** (open) — read in full, including its Decision cell. F73 *takes the three-signal
  implementation as given* — it quotes `nudge.py`'s own docstring to establish the design,
  then argues the design itself cannot distinguish a legitimate long build from a dead lead,
  and proposes a fourth "work in flight" signal. It never states or implies that
  `.claude/roles/reporter.md`'s own Mechanism section is stale; its one quotation from
  `reporter.md` (the `Owns` bullet's watch-the-watcher clause) is accurate and unrelated to
  the Mechanism section this row concerns. Overlapping code, disjoint defect, disjoint
  remedy — the same relationship F33's own row states it has with F26 ("the two overlap on
  one directory and their remedies are disjoint"). Not a duplicate; not amended into.

No open row states that `.claude/roles/reporter.md` misdescribes the nudge mechanism it
itself documents. Filed as a new row.

## RFC-937 §1.6 — charter ownership, read directly

`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` — status `accepted`, raised 2026-09-01 by the
maintainer, its own header table read directly — §1.6's ownership table, "Reference —
charters" row: "maintainer; 'a role file that proves insufficient' → `FD-` → maintainer
amends." §1.6 is named in the note's own header as a hook for a **downstream** "charter
investigation" Work not yet started (line 10: the charter investigation is a downstream
Work; §1.6 is the hook it hangs on) — the standard is accepted, its charter-specific
enforcement is not yet operational.

Separately and more simply: this role's own charter (`.claude/roles/auditor.md`) scopes
write access to "closure records, register deferral rows, and correction PRs under `docs/`"
— `.claude/roles/reporter.md` is not under `docs/`, so this row does not edit it regardless
of which reading of RFC-937 §1.6 governs right now. Whether the correction is the lead's to
make under `CLAUDE.md` §12's standing practice, or waits for the maintainer under RFC-937
§1.6, is recorded as open below, not decided here.

## Scope of this finding

- **Not fix-before-close.** No workstream currently gates on this file.
- **Not a case for touching the three-signal design.** `nudge.py` and `.claude/skills/
  reporter-cycle/SKILL.md` are correct and current; nothing about them is in question.
- **Proposed disposition** (a proposal; the verdict is the lead's): carry forward, unowned.
  The concrete fix is narrow — replace reporter.md's lines 49-78 with a short pointer to
  `.claude/skills/reporter-cycle/SKILL.md`'s dated entry, the same shape the file already
  uses at lines 13-17 for the rest of the mechanism, rather than a second, independently-
  drifting description — but **who makes that edit is the open question this row records**:
  the lead, under the standing practice of fixing a stale skill or role file in the same
  session it is found (`CLAUDE.md` §12), or the maintainer, under RFC-937 §1.6's accepted-
  but-not-yet-operational standard that charters are maintainer-authored. Not answered here.
- **Falsifiable**: discharged by `.claude/roles/reporter.md`'s Mechanism section being
  corrected to match the shipped three-signal design, by whichever role the open question
  above resolves to, or by a corrected reading showing the charter and the implementation
  already agree.
