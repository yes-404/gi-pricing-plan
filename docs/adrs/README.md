---
family: reference
title: Architecture Decision Records
status: active                  # active → retired (§1.2a)
created: 2026-08-14
owner: lead
corrected_by: []
relates: []                      # ids only
was: docs/adr/README.md
---

# Architecture Decision Records

One decision per file, named `ADR-nnnnn-<slug>.md` — the padded id leads the filename, and the
id itself is permanent: never renumbered, never reused
([`../process/document-ids.md`](../process/document-ids.md)).

**Status values** are the front matter's `status:` field: `draft` → `active` →
(`superseded` | `retired`). An `active` ADR is immutable; to change a decision, write a new
ADR that supersedes it and edit only the old one's `status:` and `superseded_by:`.

**Write an ADR when** a choice constrains more than one module, is expensive to reverse, or
has already been made and needs recording. Otherwise use
[`../open-questions.md`](../open-questions.md).

**This table is kept by hand**, by the pull request that adds or supersedes an ADR.
`scripts/doc-id.py` has only `next` and `check` since ADR-2136 retired the rest, and
[`../INDEX.md`](../INDEX.md) is frozen by ADR-2136 and no longer lists new records.

| ADR | Title | Status |
|---|---|---|
| [ADR-703](ADR-00703-pricing-core-is-dependency-free-and-owns-all-actuarial-maths.md) | pricing-core is dependency-free and owns all actuarial maths | active |
| [ADR-704](ADR-00704-model-schema-is-the-single-source-of-truth-for-shared-shapes.md) | model-schema is the single source of truth for shared shapes | active |
| [ADR-705](ADR-00705-model-and-rating-definitions-are-declarative-json-artifacts.md) | Model and rating definitions are declarative JSON artifacts | active |
| [ADR-706](ADR-00706-gorules-zen-engine-executes-rating-dags.md) | GoRules ZEN Engine executes rating DAGs | active |
| [ADR-707](ADR-00707-polars-duckdb-as-the-data-engine-not-pandas.md) | Polars + DuckDB as the data engine, not pandas | active |
| [ADR-710](ADR-00710-tenant-isolation-is-a-deployment-boundary.md) | Tenant isolation is a deployment boundary | active |
| [ADR-2136](ADR-02136-project-management-moves-to-github-with-a-slim-claude-md-and-frozen-record-families.md) | Project management moves to GitHub, with a slim CLAUDE.md and frozen record families | active |
| [ADR-2145](ADR-02145-audit-read-is-held-by-the-approver-deployer-auditor-and-admin-roles.md) | The audit:read permission is held by the approver, deployer, auditor and admin roles | active |
| [ADR-2146](ADR-02146-audit-verify-covers-the-whole-chain-by-default-with-an-optional-range.md) | GET /audit/verify verifies the whole chain by default and takes an optional from/to range | active |
| [ADR-2147](ADR-02147-the-permissions-of-06s-routes-not-yet-built.md) | The permission of each of 06's routes not yet built, with no new permission member | active |
| [ADR-2148](ADR-02148-the-1497-work-owns-the-history-routes-permission.md) | Work #1497 owns the permission of GET /artifacts/{ref}/history | active |
| [ADR-2149](ADR-02149-the-1497-plans-decided-items.md) | The decided items of the audit explorer plan, Work #1497 | active |
| [ADR-2150](ADR-02150-a-blob-reference-is-taken-inside-put-and-legacy-ownerless-blobs-are-pinned.md) | A blob's reference is taken inside put, and legacy ownerless blobs are pinned at 1 | active |
| [ADR-2151](ADR-02151-the-login-role-provisioner-revokes-every-grantors-membership-and-only-a-superuser-runs-it.md) | The login-role provisioner revokes every grantor's membership row, and only a superuser runs it | active |
| [ADR-2152](ADR-02152-proxy-assessment-decided-answers-and-two-error-codes.md) | Proxy assessment — the decided answers, and two error codes for its two kinds of invalid input | active |
| [ADR-2144](ADR-02144-grant-role-refuses-self-grant-and-any-grant-to-a-service-account.md) | A role grant is refused to oneself and to any Service Account, not by a permission-subset rule | draft |
| [ADR-2153](ADR-02153-a-factors-unseen-level-behaviour-is-declared-and-the-undeclared-case-refuses.md) | A Factor's unseen-level behaviour is declared, and the undeclared case refuses | active |
| [ADR-2154](ADR-02154-the-audit-trail-is-the-seventh-high-risk-area.md) | The audit trail is the seventh high-risk area | active |
| [ADR-2155](ADR-02155-the-audit-anchor-is-signed-with-ed25519-through-cryptography-and-refuses-a-broken-chain.md) | The audit anchor is signed with Ed25519 through cryptography, and refuses a chain that does not verify | active |
| [ADR-2161](ADR-02161-a-value-at-another-level-of-a-groupings-chain-is-refused-never-mapped.md) | A value at an ancestor's level of a Grouping's chain is refused, never mapped | draft |
