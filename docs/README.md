# Documentation Suite

This directory is the **primary deliverable of Phase 0** (see `CLAUDE.md` §0 and §9).
The exit criterion is: *an engineer could start Phase 1 from these documents alone.*

## Map

| Path | Contents |
|---|---|
| `specs/00-overview.md` | System context, module map, requirement-ID scheme, glossary |
| `specs/01-data-management.md` | Ingestion, datasets, versioning, validation |
| `specs/02-modelling.md` | GLM / GBM / EBM fitting, factors, custom objectives, diagnostics |
| `specs/03-rating-engine.md` | Rating DAG, rate tables, rating versions, scoring |
| `specs/04-optimisation.md` | Demand models, constrained optimisation, GIPP checks |
| `specs/05-monitoring.md` | Drift, PSI, A/E monitoring, dashboards |
| `specs/06-governance.md` | RBAC, approvals, audit, model documentation |
| `specs/07-platform.md` | Auth, jobs, storage, deployment, environments |
| `workflows/` | Cross-module end-to-end user journeys (wf-01 … wf-05) |
| `contracts/` | JSON Schema for artifacts + OpenAPI stubs |
| `adr/` | Architecture decision records (numbered, immutable once accepted) |
| `process/` | Team execution process: layered workflow (Project→Phase→Work→Slice), roles, escalation, monitoring loop; `document-ids.md` — the document id standard, one id per governed thing |
| `research/` | Spike findings and dated research notes. Not enumerated here — the parenthetical list this row used to carry named four notes while six existed, and would have gone stale again on the next one. `ls docs/research/` is the index |
| `skills-map.md` | Stack component → where used → skills to research → resources |
| `open-questions.md` | Unresolved design questions, owner, status |
| `phase-0-status.md` | Exit-criteria progress, requirement inventory, contract coverage, spikes |
| `roadmap.md` | Build order, what cannot be retrofitted, per-phase workstreams, decision gates |

## Reading order for a newcomer

1. `specs/00-overview.md` — context, module map, glossary.
2. `workflows/wf-01-dataset-to-model.md` — the shortest end-to-end story.
3. The module spec you are about to work on.
4. `contracts/` for the exact shapes referenced by that spec.

## Checking the suite

```bash
python3 scripts/audit-docs.py
```

Verifies broken links, requirement-ID integrity and numbering, open-question mirroring,
ADR references, the ten-section spec standard, and JSON Schema validity. Run it before
committing a docs change.

## Conventions

- Requirement IDs are permanent: `FR-<MODULE>-<n>`, `NFR-<MODULE>-<n>`. Never renumber;
  append, or mark `SUPERSEDED BY <id>`.
- Every spec follows the 10-section standard in `CLAUDE.md` §5.
- Domain vocabulary comes from `CLAUDE.md` §7, restated authoritatively in
  `specs/00-overview.md` §2. New terms are added to the glossary **before** first use.
- Money in the rating path is integer minor units (pence) or `Decimal` — never float.
- Open design choices are recorded in `open-questions.md`, not silently resolved.
