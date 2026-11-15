---
id: ADR-2144
family: decision
title: A role grant is refused to oneself and to any Service Account, not by a permission-subset rule
status: draft                 # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-347, FR-348, FR-389]  # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2144 — A role grant is refused to oneself and to any Service Account, not by a permission-subset rule

- **Status:** draft
- **Deciders:** the maintainer, on issue #1843, option (A) as amended on 2026-11-15

## Context

FR-348 said a user cannot grant themselves a permission they do not hold. `grant_role`
enforced it as a subset rule: the granter had to hold every permission of the role it granted.
That rule stopped an Admin granting the Approver role to anyone, so a workspace could not give
approval rights to the person it chose unless an Admin already held them. It also did not name
what separation of duties needs: that the granter does not grant itself a role.

Role assignments resolve by principal id alone, so a check has to compare ids, never the
`principal_kind` the caller passes.

FR-347 and FR-389 already say a Service Account holds scoring permissions only. They did not
say that no role is ever granted to one.

## Decision

Decided by the maintainer on 2026-11-15 on issue #1843
(https://github.com/yes-404/gi-pricing-plan/issues/1843#issuecomment-6886339566), in the
comment's words: "**Decided by the maintainer, 2026-11-15: option (A).** The escalation guard
refuses only when the grantee is the granter, as FR-348 is worded, with a hard refusal of a
grant to oneself and to a Service Account one owns. An Admin may grant another principal a
permission the Admin does not hold. Every grant stays an audit event, and the approval policy's
submitter rule is unchanged. The accepted cost is as stated above: two colluding accounts can
defeat separation of duties, and the audit event is the control."

The maintainer amended the decision on 2026-11-15, under the user's authority: FR-347 and
FR-389: a Service Account is never granted a role. The refusal of a grant to a Service Account
the granter owns becomes a refusal of any grant to a Service Account, for any role, so the
`created_by` column that recorded the owner is not needed.

`grant_role` refuses two grants, whatever role is granted and whatever `principal_kind` is
passed:

1. A grant to the granter itself.
2. A grant whose grantee is a Service Account, for any role. The grantee is found by id, in any
   workspace, and the refusal has its own reason naming FR-347 and FR-389.

Both refusals come before the insert and before the audit record. A refused grant writes no
audit event. A granter that holds `admin:manage_roles` may otherwise grant any role, including
one that confers permissions it does not hold.

As defence in depth, `effective_permissions` ignores role assignments for a Service Account
principal: only the credential's own grants count, however a row came to exist.

Rotation of a Service Account's key by an administrator who did not create the account stays
allowed and audited. With no role ever on a Service Account, its permissions are the scoring
permissions of its own record only.

This record changes the rule only. The route that calls `grant_role` belongs to #1494.

Options not taken, from the options and costs on #1843:

- (B) "Keep the guard, and add a named first-grant route for an Admin, limited to built-in
  roles, audited, and refusing a grant to the granter. Cost: a second route and its own
  permission."
- (C) "Give the built-in Admin every permission. Cost: the Admin can then approve and deploy,
  which the role separation exists to prevent."

Also not taken: a refusal keyed on `principal_kind`, and an audit event for a refused grant.

## Consequences

- The accepted cost, in the decision's words: two colluding accounts can defeat separation of
  duties, and the audit event is the control. The accounts are human accounts, since a Service
  Account can hold no role.
- An Admin can grant Approver to another user. The grant is an audited event.
- The change adds no migration and no column.
