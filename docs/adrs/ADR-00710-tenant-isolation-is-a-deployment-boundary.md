---
id: ADR-710
family: decision
title: Tenant isolation is a deployment boundary
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-08-15
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                    # ids only — the FR-/NFR-/ADR- this decision touches
was: docs/adr/0006-tenant-isolation-is-a-deployment-boundary.md
---

# Tenant isolation is a deployment boundary

## Context

Every artifact in the platform carries a `workspace_id`, and `07` §2 called the Workspace
"the top-level tenancy container". That left one question unanswered and load-bearing: for
**hosted** use, where two insurers' data would sit in one system, is the Workspace the
thing that keeps them apart?

Three options were on the table (OQ-540):

- **(a) Logical only** — one database, one application, `workspace_id` on every row. Cheap,
  simple, and a single missing `WHERE workspace_id = ?` shows one insurer another's rates.
- **(b) Schema-per-tenant** — strong isolation inside one database, at the cost of running
  every migration N times against N schemas and of a connection layer that must always pick
  the right one.
- **(c) Deployment-per-tenant** — one tenant, one deployment: its own application, database,
  object storage, broker, keys and audit chain. Total isolation, highest operational cost.

The stakes are asymmetric in a way that is easy to understate. A cross-tenant leak here is
not an embarrassment; it is one insurer's rating basis — the thing they compete on —
disclosed to a competitor. Recovery is impossible, because the information cannot be
un-seen, and no incident response returns a pricing advantage.

## Decision

**One tenant, one deployment.** Option (c), for hosted and self-hosted use alike. There is
no supported topology in which two tenants share a running system.

- **Nothing that carries tenant data is reachable from more than one tenant's deployment**
  — application instances, database, cache/broker, object storage, encryption keys, and the
  audit chain are per tenant (FR-17).
- **What may be shared is what carries no tenant data**: container images, infrastructure
  code, CI, and public reference data (ONS/OGL, bank holidays — `01` FR-72).
- **`workspace_id` stays on every row and every artifact envelope**, but its meaning is now
  stated precisely: a Workspace is an **organisational** container inside one tenant —
  a business unit, a line of business, a team — and it is the scope for RBAC, settings and
  the audit chain. **It is not an isolation boundary and must never be described as one.**
- **Option (b) is rejected, not deferred.** Schema-per-tenant buys isolation weaker than
  (c) at a complexity cost that lands on every migration for the life of the project.

## Consequences

**Positive** — the isolation property is enforced by infrastructure rather than by every
query in the codebase being correct forever; a tenant's data is destroyable, exportable and
auditable as a unit; the blast radius of an application defect is one tenant; per-tenant
data residency (an EU insurer's data staying in the EU) is a deployment choice rather than
a re-architecture; and the RBAC, settings and audit code that already scopes by
`workspace_id` is unchanged.

**Negative** — operational cost is now linear in tenants: N deployments to upgrade, monitor,
back up and restore. **Version skew across tenants becomes normal and permanent**, which is
what makes FR-18 necessary: a dossier regenerated in one deployment must name the build
that produced it, because "the platform" is no longer a single version. Migrations must
therefore be backwards-compatible within a minor version, and a rolling upgrade is the
supported path — a flag-day upgrade across every tenant is not.

**Neutral** — per-tenant resource quotas (OQ-643) do not disappear, but their purpose
changes: they protect a tenant's own workloads from each other, never a neighbour from a
noisy one. That question is sharpened by this ADR, not answered by it. *Answered 2026-08-23, as a rejection: `07` **FR-415** keeps the Job (FR-412) and the queue (FR-405, FR-434) as the only resource boundaries and specifies no Workspace quota. The sharpening above is what made the rejection available — once a neighbour is a different deployment, the contention left is a deployment's own, and those two already bound it.* Likewise OQ-633's
"per workspace or global" now reads as "per workspace or per deployment", and a chain the
operator controls end to end is still a chain the operator controls end to end.

## What this forecloses

Any capability that assumes one query can see two tenants: cross-insurer benchmarking, a
market-wide loss-cost pool, a shared model library with usage statistics across customers.
None of them are ruled out as *products* — but each becomes an explicit export-and-aggregate
pipeline with its own consent, anonymisation and governance story, never a `JOIN`. Anyone
proposing one should read this ADR first and expect to write a new one.

## Alternatives considered

**(a) Logical isolation only** — rejected. It makes correctness of every query, forever, the
only thing standing between two competitors' rating bases. The platform already carries
`workspace_id` everywhere and will keep doing so, but as an organisational scope, not as the
guarantee.

**(b) Schema-per-tenant** — rejected. It is the option that looks like a compromise and
behaves like both costs: migrations fan out exactly as they do under (c), while a single
misconfigured connection still crosses the boundary, which under (c) it cannot.

**Deferring the decision** — rejected. It gates Phase 3 in the roadmap's decision table, but
the answer changes what WK-674 builds in Phase 2, and a deployment story written on the
assumption of one shared system is not cheaply re-pointed afterwards.
