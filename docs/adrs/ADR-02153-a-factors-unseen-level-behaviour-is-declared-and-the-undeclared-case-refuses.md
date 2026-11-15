---
id: ADR-2153
family: decision
title: A Factor's unseen-level behaviour is declared, and the undeclared case refuses
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 4187a25e011ed69b47ef0a08bef94f42192d3146
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-131, FR-239, FR-2143]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2153 — A Factor's unseen-level behaviour is declared, and the undeclared case refuses

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer; the detail of the rule was decided on the maintainer's behalf by delegation, 15 Nov 2026.
- **Decision issue:** [#1510](https://github.com/yes-404/gi-pricing-plan/issues/1510), where `02` FR-2143 is reserved for this Work.
- **Enacts:** `02` FR-2143, with FR-131 and `03` FR-222 stating the same rule.

## Context

A fitted model has relativities only for the levels its fit saw. A quote can carry a level the fit
did not see: a new category, a missing value, an interaction cell that no fitted row held. What the
platform scores for such a level is a pricing decision, and it is the Factor's to declare.

- One rule applies across the three model families. An EBM and a GBM refuse a level they never saw
  (FR-131). A GLM follows the same rule, so a Factor means the same thing whichever family a model
  uses.
- A refusal is auditable: the Job or the quote carries a code, and a reader can see that the level
  was not priced. An undeclared score is not: the figure on the quote gives no sign that a level was
  assumed.
- `map_to_default` names no fitted value. A Factor is declared independently of any fit, so it can
  point at no fit's level or relativity, and a default that no fit defines is a number nobody estimated.

## Decision

1. A Factor declares `unseen_level_behaviour`, `error` or `map_to_base`. A model scoring a level
   its fit never saw refuses with `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` unless the Factor declares
   `map_to_base`, which scores the level as the base. A Factor that declares nothing refuses.
   This holds for a GLM as for an EBM and a GBM, for a Factor of any type, and for a null level and
   an interaction cell. The refusal text names the Factor and never the value (NFR-499).
2. `map_to_default` is refused.
3. Evidence is not pricing. Rows on an unseen level, on a Factor that does not declare
   `map_to_base`, are excluded from a fit's diagnostics, a comparison and a backtest, and are
   counted with their exposure. A partition left with no row refuses with the same code, naming the
   partition, the count and the next step.

## Options not taken

- Score an undeclared unseen level as the base. Refused: the choice is the Factor's to make,
  and an assumed level leaves no trace on the quote.
- Accept `map_to_default`. Refused for the reason in Context: it names no fitted value.
- Fail a diagnostics, comparison or backtest on such a row. Refused: evidence reports what the fit
  can measure and counts what it cannot, so a figure never rests on a level the fit has no
  relativity for.

## Consequences

- A Factor's declaration changes only by a new Factor version: Factors are append-only. A new
  declaration is a new `factor:<slug>@<version>` reference, which a refit pins in a new model and a
  new rating version carries in a new bundle hash (FR-239).
- A GLM fit records the levels and interaction cells a quote can reach that it has no relativity
  for, as a report that reads *not recorded* where the fit does not hold it, never *none*. The model
  detail and diagnostics views state the report and the exclusion counts in words.
- `scripts/sweep-unseen-levels.py` lists, read-only, the stored versions that can refuse a quote:
  version references and counts only. The upgrade note is in `CHANGELOG.md` and `deploy/README.md`.
