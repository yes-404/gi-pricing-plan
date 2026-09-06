---
id: RL-889
family: ruling
title: D3: the batch abort threshold is a workspace setting with a one-directional per-run argument
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slices-3-4-rulings.md
---

## RL-889 — D3: the batch abort threshold is a workspace setting with a one-directional per-run argument

**The decision, restated.** FR-255 (`03:166`) says a batch run *"does not abort on individual
failures unless the failure rate exceeds a **declared threshold**"* and does not say where the
declaration lives. Recovery item 4 recommends a workspace setting on `07` FR-448's precedent
*"with an optional per-batch-request override"*.

**Ruled: a workspace setting, unset by default, plus a per-run argument that may only lower the
effective threshold — never raise it.** Three parts, and the third is a correction.

### It is genuinely homeless, and that was checked rather than assumed

RL-856's lesson cuts both ways. Swept:
`grep -rn "failure rate\|failure_rate\|abort" docs/specs/*.md docs/workflows/*.md` returns
FR-255 itself and, otherwise, only `02` FR-165's per-round fit abort and its two workflow
rows — a different mechanism in a different module. FR-448's enumerated workspace settings
(`07:174`) list currency, locale, default validation thresholds, trace sampling rate, approval
policy reference, retention windows, the two model-complexity thresholds and feature flags, and
**no batch failure threshold**. So unlike D5 below, this one really is unhoused.

### Part 1 — the home, and the default

The setting joins FR-448's list and is **unset by default**. Two reasons, both from text
already on the page: FR-255's own construction — *"does not abort … **unless** the failure rate
exceeds a declared threshold"* — makes an undeclared threshold mean *no rate-based abort*, with the
requirement's first half (counts and samples per error type) still doing its work; and FR-448's
own list already carries two thresholds *"both unset by default"* (`modelling.max_factor_count`,
`modelling.min_exposure_per_parameter`), so the pattern needs no invention.

**Mirror the shipped neighbour rather than inventing a second mechanism.** Both of those
settings are read at `backend/src/app/platform/model_specs.py:62` and `:65` through one
resolver taking a dotted key, typed `int | None` / `float | None` and guarded with
`if … is not None` (`:109`, `:125`) — unset-by-default in the code, not only on the page. The
key ruled here, `rating.batch_abort_failure_rate`, follows that `<module>.<name>` form
exactly. No per-request override exists anywhere on that path today, which is the other half
of why the run's value must be a Job argument rather than a fourth resolution tier.

### Part 2 — it is a Job input, not a fourth precedence tier

FR-446 (`07:172`) resolves settings by *"environment variable → workspace setting → platform
default"* — three tiers, and *"the effective value and its source are inspectable by an Admin."*
An unqualified "per-request override" would silently add a fourth tier to that chain and make the
inspector's answer incomplete. That chain is not only specified but implemented as exactly three:
`settings.resolve` (`backend/src/app/platform/settings.py:261-279`) reads an environment candidate
and a `workspace_settings` row and hands both to `_resolution` (`:328-345`), which reports the
source as `ENV`, `WORKSPACE` or `DEFAULT` and has no fourth branch to add one to.

**Ruled:** the run's value is an **argument to the Job**, not a Setting. FR-446's chain
resolves the workspace default; the run's argument is recorded on the Job — where FR-410
(`07:99`) already retains *"its parameters and result reference"* for ≥ 13 months — and never
enters settings resolution. FR-446 is untouched and stays true as written.

### Part 3 — the correction: the argument is one-directional

The recovery document's *"optional per-batch-request override"* is unqualified. `01` has already
decided this exact question for thresholds, and decided it the other way:

- **FR-56** ([`../specs/01-data-management.md`](../specs/01-data-management.md)`:118`):
  *"Changing a validation rule's threshold authors a new rule version. A threshold is part of what
  a rule *is*."*
- `01:355`: *"A rule's thresholds are **not overridable** at set level either, and for a stronger
  reason than severity's: **no threshold has a safe direction to move in** (FR-56)."*
- And where `01` does permit an override at all, it is one-directional: `severity_override` *"may
  only *raise* severity (`warn → fail`), never lower"* (`01:352`).

Applied here, the safe direction is unambiguous and the two cases are not symmetric: **lowering**
the threshold aborts a failing batch sooner, **raising** it lets a run push through more failures
than the workspace agreed to tolerate. So the argument may only lower the effective threshold. That
keeps the workspace setting a genuine floor on caution — the same shape as `severity_override`,
whose precedent is what makes this a derivation rather than a preference.

### Disposition

Two spec changes in this commit: FR-448's list gains the setting, and FR-255 gains a dated
clarification naming where *"declared"* lives, the unset default, the one-directional argument, and
the requirement that the Job records both the threshold in force and the observed failure rate when
it aborts — an abort nobody can reconstruct is not auditable.

**Acceptance test — the violation that must become expressible.** Today *"this batch aborted at a
threshold nobody agreed to"* cannot be said, because no threshold exists anywhere to disagree with.
After this ruling the expressible violation is a run that completes past its workspace threshold,
or a run whose argument raises it: a batch request carrying a threshold **above** the workspace
setting must be refused, and a run whose failure rate crosses the effective threshold must abort
with both numbers on the Job. **The ruling is overridden** if a build accepts a per-run value
higher than the resolved setting, or aborts without recording the threshold it used.

---
