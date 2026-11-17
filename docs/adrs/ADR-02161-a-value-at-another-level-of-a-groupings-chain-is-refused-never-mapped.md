---
id: ADR-2161
family: decision
title: A value at another level of a Grouping's chain is refused, never mapped
status: draft                 # draft → active → superseded | retired (§1.2a)
created: 2026-11-17
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: c7d9f0b0c8aa139042ddf17cfeeda247933dd5ad
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-104, FR-109, FR-222, FR-239, FR-2143]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2161 — A value at another level of a Grouping's chain is refused, never mapped

- **Status:** draft (the maintainer accepts it to `active`).
- **Deciders:** the maintainer, 2026-11-17.

## Context

A Grouping may name a parent (FR-109): a finer level rolls to a coarser one. The chain was
stored and read by nothing. A Factor on a Grouping reads a column at that Grouping's own
source level; a column that holds a finer level than the Grouping's is, to the Grouping, a
column of unseen values. Nothing at creation, at fit or at scoring checked that a column was at
that level of the chain.

## Decision

Refuse, and change no price that is right today.

1. **At creation**, a Grouping with a parent is refused (422) unless the parent exists in the
   same workspace (`GROUPING_PARENT_NOT_FOUND`) and the levels chain: each source level of the
   child is a target level of its parent, and none is also a source level of an ancestor
   (`GROUPING_CHAIN_LEVELS_MISMATCH`).
2. **At fit**, a grouping Factor whose Grouping declares `map_to_default` or `map_to_base` and
   maps none of its column's rows is refused (`GROUPING_MAPS_NO_VALUE`, 409: a refusal of a job
   against the data; the creation-time refusals above are 422, the request's own shape). A
   Grouping that declares `error` keeps its existing `FACTOR_RESOLUTION_FAILED`, a published
   code. Where some rows are unmapped, the fit records their count and exposure on its result and
   is not refused.
3. **At resolution**, a Grouping with a parent that declares `map_to_default` or `map_to_base`
   refuses a value that is a source level of one of its ancestors
   (`GROUPING_VALUE_AT_ANCESTOR_LEVEL`), naming the Factor and never the value. A value the
   Grouping maps is untouched; a value no ancestor knows keeps the declared behaviour. The
   ancestors travel with the Groupings: every database-backed path loads them, and a Rating
   Version compiled from now on carries them in its Bundle. `error` behaviour is unchanged,
   and its message now counts the levels it did not map rather than listing them (NFR-499).
4. **Not taken:** resolving a Factor by following the chain (mapping a finer value through an
   ancestor). It changes what a stored model scores; if it is wanted it is its own decision,
   with a new Factor version.

## Consequences

- The scoring arithmetic of a level a Grouping maps does not change.
- A Rating Version's Bundle refuses such a value when it carries the ancestors, which is every
  Bundle compiled after this change. **A draft recompiled after it keeps its content hash**
  (the hash covers the graph and the pinned refs, not the carried Groupings) **and can refuse
  a quote it priced** (FR-239). A Bundle stored before it carries no ancestors, cannot read the
  chain without a database (NFR-491), and keeps pricing as it did until its version is
  reissued. A way to list such versions follows in a later change; none exists yet.
