# Phase 0 — Specification status

**As at:** 2026-08-14 · Regenerate the counts with `scripts/audit-docs.py` (below).

Phase 0's exit criterion (`CLAUDE.md` §9): *an engineer could start Phase 1 from these
documents alone.*

---

## 1. Exit criteria

| Criterion | Status | Note |
|---|---|---|
| Every module spec meets the §5 ten-section standard | **done** | All 8 specs verified by the audit script |
| All five workflow documents complete | **done** | wf-01 … wf-05, each with failure paths and traceability |
| Contracts drafted | **done** | 31 JSON Schemas covering every persisted artifact, + OpenAPI stub |
| `open-questions.md` empty or explicitly deferred | **open** | 45 questions: 38 `open`, 6 `deferred`, **1 `decided`** (OQ-RATE-1, closed by Track A research). Each has options, trade-offs, and a recommendation |
| `skills-map.md` covers every tech dependency | **done** | Every stack component cited by a spec has a row |

**Remaining before Phase 1 can start:** resolve or explicitly defer the open questions
(§4), and close the two spikes (§5). Both are maintainer decisions; nothing in the
document suite blocks on further writing.

---

## 2. Requirement inventory

408 numbered requirements, no gaps, no duplicates, no dangling references.

| Module | Spec | Requirements |
|---|---|---|
| `OVR` | 00-overview | 25 |
| `DATA` | 01-data-management | 49 |
| `MODEL` | 02-modelling | 78 |
| `RATE` | 03-rating-engine | 67 |
| `OPT` | 04-optimisation | 35 |
| `MON` | 05-monitoring | 43 |
| `GOV` | 06-governance | 43 |
| `PLAT` | 07-platform | 60 |

Requirement IDs are permanent (`CLAUDE.md` §5). Never renumber; append, or mark
`SUPERSEDED BY <id>`.

---

## 3. Contract coverage

**Complete.** 31 JSON Schemas in `docs/contracts/schemas/` cover every persisted artifact
the specs define, plus a 32-path OpenAPI 3.1 stub.

| Area | Count | Schemas |
|---|---|---|
| Common | 5 | artifact envelope, artifact ref, blob ref, money primitives, provenance |
| Data (01) | 4 | dataset version, validation rule, validation report, profile |
| Modelling (02) | 9 | banding, grouping, model spec, model, diagnostics, custom objective, objective certificate, transparency artifact, peril structure |
| Rating (03) | 6 | rating algorithm, rate table, rating version, scoring, dislocation run, regression suite |
| Optimisation (04) | 2 | optimisation run, GIPP check |
| Monitoring (05) | 1 | monitoring (monitor / result / alert) |
| Governance (06) | 3 | approval request, audit event, dossier |
| Platform (07) | 1 | job |

Where a rule can be expressed in schema it is (`if`/`then`, `required`, `pattern`); the
rest sit in an `invariants` annotation citing their requirement ID. From Phase 1 all of
these become generated output from `packages/model-schema`
([ADR-0002](adr/0002-model-schema-single-source-of-truth.md)), with CI failing on drift.

---

## 4. Open questions by disposition

45 total. Every one carries options, trade-offs, and a recommendation — none is left as a
bare question.

| Module | Open | Deferred | Highest-consequence |
|---|---|---|---|
| OVR | 5 | 0 | OQ-OVR-2 licence choice — blocks nothing technically, blocks contribution socially |
| DATA | 6 | 0 | OQ-DATA-1 where large-loss capping lives |
| MODEL | 6 | 1 | OQ-MODEL-1 whether expression objectives ship in Phase 1 |
| RATE | 4 (+1 decided) | 1 | ~~OQ-RATE-1~~ resolved; now **OQ-RATE-2 `exact`-mode GBM latency** — see §5 |
| OPT | 4 | 2 | OQ-OPT-4 demand-model endogeneity |
| MON | 4 | 1 | OQ-MON-1 whether A/E comes from traces or a full re-score |
| GOV | 4 | 1 | OQ-GOV-3 whether Admin can override a flag |
| PLAT | 5 | 0 | OQ-PLAT-1 Celery vs a transactional Postgres queue |

Deferred items name their target phase.

---

## 5. Spikes to run before Phase 2

Two questions could not be settled by reasoning. **Track A research (2026-08-14) settled
the substance of the first**; what remains is smaller and better aimed.

1. **~~OQ-RATE-1 — ZEN Engine decimal semantics.~~ RESOLVED — S1 re-scoped, not cancelled.**
   The engine represents numbers as `rust_decimal::Decimal`, so arithmetic is exact and
   [ADR-0004](adr/0004-zen-engine-for-rating-execution.md) stands. **S1 now tests the two
   risks the finding exposed:** whether arbitrary precision survives the Python binding in
   *both* directions (FR-RATE-56), and whether any rateable path can reach a
   `maths-nopanic` sink that returns `0` instead of raising (FR-RATE-57). Both failure
   modes are silent, which is why they still warrant code before Phase 2.
2. **OQ-RATE-2 — `exact`-mode GBM latency.** Unchanged and now the highest-risk remaining
   unknown. Whether a `model_call` to a realistic booster (500 trees, 60 features) fits
   inside the 50 ms p99 budget at 200 rps determines whether production rating can ever use
   the exact model, and therefore resolves OQ-MODEL-3 by force rather than by choice.
   Research sharpened the budget: Pydantic response validation alone costs ~1 ms, which
   NFR-RATE-13 now removes from the hot path.
3. **S3 (new) — LightGBM `init_score`.** The dual-backend contract assumes `init_score` is
   symmetric with XGBoost's `base_margin`. XGBoost's behaviour is now verified; LightGBM's
   is **assumed**. Cheap to check, and the failure mode is the same silent one (F5).

---

## 5b. Research completed

Track A ran on 2026-08-14 with four executable spikes against real library versions
(SymPy 1.14.0, XGBoost 3.4.0, Pydantic 2.13.4). Full log:
[`research/track-a-findings.md`](research/track-a-findings.md).

| Outcome | Count | Detail |
|---|---|---|
| Open questions closed | 1 | OQ-RATE-1 |
| **Spec defects found and fixed** | **2** | Certification would have rejected every valid piecewise objective (F3); a silent GBM scoring failure was unspecified (F5) |
| **Fabricated figure corrected** | **1** | An invented convexity percentage presented as a measurement (F4) |
| Designs confirmed | 5 | SymPy derivation, `base_margin` semantics, glum standard errors, pandera Polars, Pydantic discriminated unions |
| New requirements | 8 | FR-MODEL-68..71, FR-RATE-56..58, NFR-RATE-13 |

The two defects are the return on this work: both would have surfaced in Phase 1 as
confusing failures rather than as design decisions.

## 6. Reading paths

| If you are… | Read |
|---|---|
| New to the project | `specs/00-overview.md` → `workflows/wf-01` → the spec you will work on |
| Researching the stack (the maintainer's next step) | `skills-map.md` §7 research priority, then each component's row |
| Planning Phase 1 | `workflows/wf-01`, `specs/01`, `specs/02`, and the timing tables at the end of each workflow |
| Assessing risk | This page §5, then `open-questions.md` |
| Implementing a module | That module's spec end to end, plus `docs/contracts/` for the shapes |

---

## 7. Audit script

The counts and consistency checks on this page are reproducible:

```bash
python3 scripts/audit-docs.py
```

**Bookkeeping checks (1–8):** no broken relative links; every referenced requirement ID
defined exactly once; no numbering gaps; open questions mirrored in both directions; every
referenced ADR exists; all ten §5 sections present; every JSON Schema parses with no
duplicate keys; every `$ref` resolves including cross-file `$defs` pointers.

**Structural checks (9–14)**, added 2026-08-14 because bookkeeping passing is not the same
as the suite hanging together: cross-spec section references resolve; no error code is
claimed by two modules unless annotated as re-raised; module dependencies respect DEP-1 and
its DEP-1a carve-out; `*_minor` money fields are never fractional; no module glossary
redefines a term `00-overview.md` already owns; and every module is exercised by at least
one workflow above a coverage floor.

Every structural check was proven against deliberately broken input before being trusted.
