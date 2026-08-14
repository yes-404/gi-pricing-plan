# Phase 0 — Specification status

**As at:** 2026-08-14 · Regenerate the counts with `scripts/audit-docs.py` (below).

Phase 0's exit criterion (`CLAUDE.md` §9): *an engineer could start Phase 1 from these
documents alone.*

---

## 1. Exit criteria

> **Track A closed, all three spikes run, and the Phase 1a/1b split accepted** (2026-08-14).
> Remaining Phase 0 work is **4 decisions before Phase 1a can start** (3 more before 1b).
> No code-answerable question is outstanding. See [`roadmap.md`](roadmap.md) §3.

| Criterion | Status | Note |
|---|---|---|
| Every module spec meets the §5 ten-section standard | **done** | All 8 specs verified by the audit script |
| All five workflow documents complete | **done** | wf-01 … wf-05, each with failure paths and traceability |
| Contracts drafted | **done** | 31 JSON Schemas covering every persisted artifact, + OpenAPI stub |
| `open-questions.md` empty or explicitly deferred | **open** | 46 questions: 39 `open`, 6 `deferred`, **1 `decided`** (OQ-RATE-1, closed by Track A research). Each has options, trade-offs, and a recommendation |
| `skills-map.md` covers every tech dependency | **done** | Every stack component cited by a spec has a row |

**Remaining before Phase 1a can start:** four decisions (OQ-OVR-2, OQ-PLAT-1, OQ-DATA-1,
OQ-DATA-2). Nothing in the document suite blocks on further writing, and no spike remains.

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
| GOV | 5 | 1 | OQ-GOV-3 whether Admin can override a flag |
| PLAT | 5 | 0 | OQ-PLAT-1 Celery vs a transactional Postgres queue |

Deferred items name their target phase.

---

## 5. Spikes to run before Phase 2

Two questions could not be settled by reasoning. **All three spikes have now run and all
three are closed.** Every one changed the specification — none confirmed its assumption
unchanged, which is the case for having run them rather than reasoned about them.

1. **~~S1 — ZEN boundary.~~ CLOSED 2026-08-14.** Engine arithmetic is exact, but the
   **Python binding has no decimal type** — a `Decimal` is rejected and everything returns
   as `float`. F1's "workaround not required" was wrong; money now crosses as integer minor
   units (FR-RATE-56). Also found `log`/`sqrt` don't exist in ZEN, so the old FR-RATE-57
   guarded nothing, while **division by zero returns `null` silently** — rewritten.


2. **~~S2 — `exact`-mode GBM latency.~~ CLOSED 2026-08-14.** **Comfortably viable**: p99
   1.09 ms for 500 trees × 60 features, ~2 % of the 50 ms budget. OQ-MODEL-3 stays a real
   design choice. `nthread=1` per request beats all-cores at the tail (NFR-RATE-14). A
   sustained-load test moves to Phase 2 W11.


3. **~~S3 — LightGBM `init_score`.~~ CLOSED 2026-08-14.** The assumption was **half wrong**.
   Symmetric at fit time — both backends include the offset in the raw score handed to a
   custom objective. **Asymmetric at scoring time**: `Booster.predict()` has no offset
   parameter at all, so a scoring path ported from XGBoost's API silently omits the offset
   and under-predicts by exactly `log(exposure)`. Fixed as FR-MODEL-72 (F13).

---

## 5b. Research completed

Track A ran on 2026-08-14 with seven executable spikes against real library versions
(SymPy 1.14.0, XGBoost 3.4.0, Pydantic 2.13.4). Full log:
[`research/track-a-findings.md`](research/track-a-findings.md).

| Outcome | Count | Detail |
|---|---|---|
| Open questions closed | 3 | OQ-RATE-1, OQ-RATE-2, OQ-OPT-6 |
| **Spec defects found and fixed** | **5** | Certification would have rejected every valid piecewise objective (F3); a silent GBM scoring failure was unspecified (F5); the dual-backend scoring path assumed a symmetry that does not hold (F13); the ZEN binding cannot carry decimals, contradicting an earlier conclusion (F14); FR-RATE-57 guarded functions that do not exist while real division-by-zero returned null silently (F14) |
| **Fabricated figure corrected** | **1** | An invented convexity percentage presented as a measurement (F4) |
| Designs confirmed | 5 | SymPy derivation, `base_margin` semantics, glum standard errors, pandera Polars, Pydantic discriminated unions |
| New requirements | 11 | FR-MODEL-68..72, FR-RATE-56..59, NFR-RATE-13/14 |

The two defects are the return on this work: both would have surfaced in Phase 1 as
confusing failures rather than as design decisions.

## 6. Reading paths

| If you are… | Read |
|---|---|
| New to the project | `specs/00-overview.md` → `workflows/wf-01` → the spec you will work on |
| Researching the stack (the maintainer's next step) | `skills-map.md` §7 research priority, then each component's row |
| Planning Phase 1a/1b | `workflows/wf-01`, `specs/01` (1a), `specs/02` (1b), and the timing tables at the end of each workflow |
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
