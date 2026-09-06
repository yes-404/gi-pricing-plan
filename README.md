---
family: reference
title: GI Pricing Plan
status: active                  # active → retired (§1.2a)
created: 2026-08-30
owner: lead
corrected_by: []
relates: []                      # ids only
---

# GI Pricing Plan

An open-source general insurance pricing platform for the UK/EU market — an open
alternative to the established commercial pricing suites. It covers the full pricing
lifecycle: data preparation, risk
modelling (GLM/ML), rating algorithm design, deployment/scoring, monitoring, and
governance. It is built for pricing actuaries and analysts — technical users who work in
Python and notebooks but expect a polished UI — and every design decision favours
reproducibility, auditability, and transparency of the maths over convenience.

## Where the project is

Status, workstream progress, and phase boundaries change often enough that a copy of them
here would go stale — see [`docs/roadmap.md`](docs/roadmap.md) for the current phase, what
is open, and what has closed.

## How it is built

This repository is developed by a team of Claude Code agents operating under a
documented delivery process
([`docs/process/delivery-process.md`](docs/process/delivery-process.md)), with a
maintainer approving work at fixed checkpoints. The team's decisions, findings, and audits
are public: the open-findings register
([`docs/findings/register.md`](docs/findings/register.md)) and the closure records under
[`docs/audit/`](docs/audit/) are not curated after the fact.

## Explore the project

- [`docs/specs/`](docs/specs/) — the specification suite the code is written against,
  starting with [`docs/specs/00-overview.md`](docs/specs/00-overview.md) for the system
  context, module map, and glossary.
- [`docs/adrs/`](docs/adrs/) — architecture decision records for choices that constrain
  more than one module.
- [`docs/workflows/`](docs/workflows/) — the cross-module user journeys the specs
  implement.
- [`docs/findings/register.md`](docs/findings/register.md) — the open-findings ledger.
- [`docs/roadmap.md`](docs/roadmap.md) — build order and current status.

## Engage

- Found a bug, have a question about the specs or process, or want to suggest something?
  See [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Found a security issue? See [`SECURITY.md`](SECURITY.md) — please do not open a public
  issue for it.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).
