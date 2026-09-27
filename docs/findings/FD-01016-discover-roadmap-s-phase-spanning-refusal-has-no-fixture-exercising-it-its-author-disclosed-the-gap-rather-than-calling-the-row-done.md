---
id: FD-1016
family: finding
title: `_discover_roadmap`'s phase-spanning refusal has no fixture exercising it; its author disclosed the gap rather than calling the row done
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-02
owner: auditor
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
was: docs/audit/findings/F78.md
---

# F78 — `_discover_roadmap`'s phase-spanning refusal has no fixture exercising it; its author disclosed the gap rather than calling the row done

Evidence essay for the register row self-named `(F78)` in `docs/findings/register.md`. Filed
by the W37-5b auditor, from a gap `4cbfa62`'s own author disclosed rather than one this
audit discovered independently.

## Provenance

`4cbfa62` (PR #610, "the roadmap and register's real shape convert — W37-6 rows 2, 3") ends
its own commit body:

> Disclosed and not built: no fixture exercises the phase-spanning refusal. It is measured
> absent across every work's certain occurrences on the real tree today and the refusal
> code exists; the gap is named as a follow-up rather than the row being called done.

This essay verifies the claim rather than repeating it, and files the register row that
tracks it.

## The defect, verified directly at `d47a5f5`

`scripts/doc-id.py`'s `_discover_roadmap` (`:1882-1941`) merges a work's several leading
roadmap rows into one draft (RL-992) and refuses on two conditions rather than choosing
silently. Its own docstring states both:

> The one thing this still refuses on: a work whose several rows disagree on status
> (RL-992 obligation 1), or a work whose occurrences span more than one phase section
> (measured absent on the real tree today; a genuine tie-break this function does not
> invent one for).

The second refusal — `unresolved_phase` at `:1917-1924` — raises `NotImplementedError`
naming every work whose merged occurrences carry no single `phase_label`. Confirmed
directly: importing `scripts/doc-id.py` and calling `_discover_roadmap(ROOT)` against the
real tree at `d47a5f5` returns 41 works with no exception (phase breakdown P1a: 7, P1b: 5,
P2: 14, P3: 8, P4: 7, summing to 41) — the refusal branch is never entered on real content
today, exactly as disclosed. `grep -rn "unresolved_phase\|phase.*span" tests/` finds the
guard's own unit tests for the *status*-disagreement refusal
(`test_a_status_conflict_across_a_works_rows_refuses_naming_the_work`) but no equivalent
fixture constructing a work whose rows sit in two different phase sections — the sibling
refusal this row is about has no test in either direction (no proof it fires on broken
input, and no proof it stays silent on every real shape other than today's).

## Why this is not blocking

`_discover_roadmap`'s status-disagreement refusal (RL-992 obligation 1) **is** tested
and green. The phase-spanning refusal is the only piece of `4cbfa62`'s work with no
broken-input proof, and the function's own docstring is explicit that this is a measured
absence on today's tree, not a proof of absence in general — a future roadmap edit that
moves a work's row into a different phase section while leaving an older row of the same
work behind would trigger it for the first time, untested.

## Scope of this finding

- **Not fix-before-close for W37-5b.** Row 2/3 of the obligations list asked for
  `_discover_roadmap` and `_discover_register` to convert the real tree, which they do
  (41 of 41 works, 73 of 73 register rows, both reproduced independently against `d47a5f5`
  by this audit). The phase-spanning refusal is disclosed scope beyond what either row
  asked for, not a shortfall against them.
- **Proposed disposition** (a proposal; the verdict is the lead's): deferred with an
  owner — **W37-6**, the workstream that runs `migrate()` for real and is therefore the
  first place this refusal could actually fire; a fixture constructing a work whose two
  leading rows sit under different phase headings, proving the guard names the work and
  raises, is the discharge.
- **Falsifiable**: discharged when such a fixture lands and passes, or by a corrected
  reading showing the real roadmap already contains a phase-spanning work (in which case
  the guard's silence today would itself be the defect).
