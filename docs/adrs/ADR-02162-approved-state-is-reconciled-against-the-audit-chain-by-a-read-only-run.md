---
id: ADR-2162
family: decision
title: Approved state is reconciled against the audit chain by a read-only run, and the check is detective
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-17
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 11ca1cd5e99b82d83fe1e16c0250963ad11bffa2
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-2163, FR-353, FR-368, FR-372, FR-373]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2162 — Approved state is reconciled against the audit chain by a read-only run, and the check is detective

- **Status:** accepted 2026-11-17 (front matter `active`); decided on the maintainer's behalf by delegation
- **Date:** 2026-11-17
- **Deciders:** the maintainer (decided on Work #1915, plan accepted in its comment of 2026-11-17)
- **Related:** FR-2163, FR-353, FR-368, FR-372, FR-373

## Context

Every artifact in an approved state, and every deployment, should have the approval request,
the decisions and the Audit Events the decision path writes, in order, in a chain that
verifies. Each of those facts is stored, and the chain itself is verified (FR-372), but
nothing checked them against one another as a whole.

The forces:

- The check has to be runnable by the operator and by a customer's auditor against a copy of the
  database, with no new route and no change to a shared contract.
- The chain is hashed in the application and the hash is not keyed, so the chain alone proves
  ordering and integrity of what was written, not that what was written was true.
- Rows older than the events the decision path writes today will not match a rule that needs
  those events.

Options considered:

1. **A platform function and a read-only script** (chosen).
2. The same, plus a field in the response of `GET /api/v1/audit/verify`. Rejected: it answers a
   different question from chain integrity and changes a shared contract and a spec row.
3. The same, plus a scheduled job that records its result as an Audit Event. Deferred: a later
   Work, once the output has been read on a real database. A recorded result is a record, not a proof.

## Decision

1. A platform function `reconcile` (`backend/src/app/platform/reconcile.py`) and a script
   `scripts/reconcile-approvals.py` implement FR-2163's five rules per workspace. The chain
   must verify first; a broken chain stops the rules for that workspace.
2. The run is read-only: each workspace is read in a `READ ONLY` transaction and no event is
   written. Exit `0` clean, `1` any mismatch, `2` a broken chain or a run that could not
   complete. It should run with a read-only login where one exists; the application login is
   acceptable because the run only reads. `deploy/README.md` says so.
3. Rows older than the workspace's first decision event that carries its ids are reported like any
   other mismatch, each marked `legacy`; the exit code stays `1`. Nothing is silenced by default.
4. The decision event's `after` gains `approval_request_id` and `decision_id`, for new events only,
   so rule 3 matches exactly; earlier events are matched by `(entity_ref, actor, decision)`.
5. The set of governed tables and "approved or later" states the run covers is derived from the
   installed approval guards and the status lifecycles, never listed by hand; a census test
   fails when a guarded table has no coverage.
6. A row in a status no lifecycle edge leads to (today a rating version that is `live` or
   `retired`) is reported by rule 1 as a status the product does not write, whatever requests
   exist. A model archived after it was superseded is not claimed by rule 1, because
   `archived` is reachable from `draft`; rules 2 to 4 cover its approval through the chain.
7. Dataset Versions are outside this Work (their `validated` state is set by a job, not an
   approval) and a scheduled run is a later Work.

## Consequences

**Positive**

- A stored approved state with no approval behind it, a decision with no event, an event with no
  decision, an out-of-order trail, and a deployment of an unreconciled version are each reported
  with the rule, the reference and the rows looked at.
- No contract, route, migration or grant changes.

**Negative**

- The check is detective. It reports after the fact and prevents no write; between a write and
  the next run, an approved state can stand without its approval.
- What the run cannot show: a chain rewritten consistently (FR-373: the chain is tamper-evident,
  not tamper-proof). The anchors of FR-373, kept in a store the operator does not control, and
  the identity provider's own log are the records outside the platform. This check does not
  widen FR-372 or FR-373.
- On a database with rows from before the decision event carried its ids, the first runs are
  noisy, by design.
- Someone has to run it.

**Neutral**

- The decision event is slightly larger (two ids); no reader of the event's `after` relies on its
  exact key set except one existing test, which changes with it.
