---
id: ADR-2151
family: decision
title: The login-role provisioner revokes every grantor's membership row, and only a superuser runs it
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: []   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2151 — The login-role provisioner revokes every grantor's membership row, and only a superuser runs it

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer
- **Decision issue:** [#1760](https://github.com/yes-404/gi-pricing-plan/issues/1760)
- **Decision:** [comment of 2026-11-15](https://github.com/yes-404/gi-pricing-plan/issues/1760#issuecomment-6887191610), opening: "**Severity: MEDIUM, set by the S6b probe, 2026-11-15 (the maintainer's ruling).**" The enacting PR names the ruling "option b".
- **Enacted by:** [#1859](https://github.com/yes-404/gi-pricing-plan/pull/1859), merge commit `a8a598663b31180fdab3f6e4bbac596a7f507a17` (2026-11-15), slice S6b.
- **Tracked consequence:** [#1857](https://github.com/yes-404/gi-pricing-plan/issues/1857) (LOW).
- **Recorded after the fact.** Written on 2026-11-15, after the decision and its enactment.

## Context

An earlier change (#1848) made the login-role provisioner (`deploy/postgres/app-login-role.sql`) revoke
every membership of `gip_app_login` and `gip_app` that it did not grant. One case was left: the
intended membership `gip_app -> gip_app_login` was exempt from the revoke for every grantor, so a row
granted by another role, carrying ADMIN OPTION or SET TRUE, survived a re-run. A probe on a throwaway
PostgreSQL 16 container showed that with such a row, `gip_app_login` could grant `gip_app` onward and
(re-read over a real login connection) `SET ROLE gip_app`. The plan at that point was to exempt only the
row granted by the provisioner's own role. The probe also showed that a superuser other than the
bootstrap superuser has its `GRANT` recorded under the bootstrap superuser, so that exemption would not
match the row the `GRANT` writes, and a revoke with dependent grants fails with SQLSTATE 2BP01.

## Decision

Option (b), and severity MEDIUM (the precondition is a membership that someone with the privilege
granted by hand). The provisioner drops the exemption altogether:

- it revokes every row of the intended membership, whatever the grantor, then grants it once
  (INHERIT TRUE, SET FALSE) inside its single transaction, leaving exactly one row without ADMIN OPTION;
- a row that cannot be revoked fails the run and names the membership; there is never a CASCADE;
- its last step asserts the end state;
- **provisioning runs only by a superuser**: the file refuses any other role at its first statement.

## Options not taken

- **Exempt only the row granted by the provisioner's own role** (the plan of the comment of 2026-11-14,
  slice S6b as first drafted). Not taken: the probe showed the exemption would not match the row when a
  non-bootstrap superuser runs the file.
- **Option (a)** of the ruling is not set out in the issue or the enacting PR: not recorded.

## Consequences

Accepted cost: provisioning needs a superuser, so the provisioner cannot run as written on a managed
PostgreSQL service. This is tracked in #1857 (LOW), and support for such a service is decided when a
deployment target is chosen. A CREATEROLE non-superuser could never run the file in any case: it already
failed at the existing `ALTER ROLE ... NOSUPERUSER`. The enacting PR also made the role-mutating tests
run only when `GIP_TEST_ROLE_CLUSTER_ISOLATED=1`, never on `CI=true` alone.
