---
id: ADR-2144
family: decision
title: A role grant is refused to oneself and to a Service Account one owns, not by a permission-subset rule
status: draft                 # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-347, FR-348]      # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2144 — A role grant is refused to oneself and to a Service Account one owns, not by a permission-subset rule

- **Status:** draft
- **Deciders:** the maintainer, on issue #1843 (option (A))

## Context

FR-348 said a user cannot grant themselves a permission they do not hold. `grant_role`
enforced it as a subset rule: the granter had to hold every permission of the role it granted.
That rule stopped an Admin granting the Approver role to anyone, so a workspace could not give
approval rights to the person it chose unless an Admin already held them. It also did not name
what separation of duties needs: that the granter does not control the grantee.

Role assignments resolve by principal id alone, so the check has to compare ids, never the
`principal_kind` the caller passes.

## Decision

`grant_role` refuses two grants, whatever role is granted and whatever `principal_kind` is
passed:

1. A grant to the granter itself.
2. A grant to a Service Account the granter owns. The owner is the account's `created_by`,
   recorded when the account is created and backfilled by migration `a1d9e47c3b52` from each
   account's `service_account.created` audit event. An account whose owner is unrecorded
   (`created_by` is NULL) is refused, deny by default, with its own reason: the creator is not
   recorded.

A granter that holds `admin:manage_roles` may otherwise grant any role, including one that
confers permissions it does not hold. A refused grant writes no audit event.

A Service Account is never granted a role that carries an approval or deployment permission
(FR-347), whoever owns it. FR-347 already said a Service Account can never hold such a
permission; the subset rule was the only thing that enforced it for a grant, so the rule
moves into `grant_role` when the subset rule goes.

This record changes the rule only. The route that calls `grant_role` belongs to #1494.

Ruled out: a permission-subset check; a refusal keyed on `principal_kind`; an audit event for a
refused grant.

## Consequences

- The accepted cost, in the decision's words: two colluding accounts can defeat separation of
  duties, and the audit event is the control.
- An Admin can grant Approver to another user or to a colleague's human account. The grant is
  an audited event, and the two refusals above stop the single-account route.
- A Service Account with no recorded owner cannot be granted a role until its owner is set.
  The way out is an Admin setting the owner through the admin API of #1494, audited. That route
  is not built here; until it exists such accounts stay unassignable.
- Downgrading the migration drops `created_by`; a later upgrade derives it again from the audit
  events.
