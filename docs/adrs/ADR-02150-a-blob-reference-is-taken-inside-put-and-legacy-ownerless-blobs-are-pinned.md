---
id: ADR-2150
family: decision
title: A blob's reference is taken inside put, and legacy ownerless blobs are pinned at 1
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 6c005d5db353024e532c7be54329d2af2634afef
supersedes: []
superseded_by: ~
corrected_by: []
relates: []   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2150 — A blob's reference is taken inside put, and legacy ownerless blobs are pinned at 1

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer
- **Decision issue:** [#1504](https://github.com/yes-404/gi-pricing-plan/issues/1504) (WK-1251, production packaging and supply chain)
- **Decisions:** two.
  - Q1 and Q2: [comment of 2026-11-14](https://github.com/yes-404/gi-pricing-plan/issues/1504#issuecomment-6881335934), opening: "**Status, 2026-11-14.** The maintainer accepted slices 1 and 2 of this plan. Building them starts now. Answers already given: **Q1 = (b).** The reference is taken inside `put`."
  - Slice 2, option (A): **no decision comment exists.** The option was part of the plan for slices 1 and 2 that the maintainer accepted on 2026-11-14 (17:18:38 GMT), "PLAN ACCEPTED FOR SLICES 1 AND 2 ONLY", recorded in the maintainer's channel, which cannot be linked publicly. The enacting PR names it: "the maintainer's option A". A later comment on the same issue ([2026-11-14, 18:58 GMT](https://github.com/yes-404/gi-pricing-plan/issues/1504#issuecomment-6882624173)) answers other questions of the plan (Q4 to Q8, Q11) and is not this decision.
- **Enacted by:** [#1850](https://github.com/yes-404/gi-pricing-plan/pull/1850), merge commit `e92205a38e0ab90e2dc1c15c18951d2649799e4c` (2026-11-15), slices 1 and 2 of #1504.
- **Recorded after the fact.** Written on 2026-11-15, after the decision and its enactment.

## Context

The blob collector (`BlobStore.collect_garbage`, FR-420) selects blobs at `ref_count` 0. Before this
decision a reference was taken only by rating versions and traces, so a blob that a dataset version's
tables or a Job result named sat at 0 and a wired collector could delete live content. Slice 1 had to
make every writer's blob held; slice 2 had to make the existing rows safe.

## Decision

1. **Q1 = (b): the reference is taken inside `put`.** `BlobStore.put` takes one reference for its
   caller, so a writer cannot forget it. The `07` §5.2 line changes in the same commit, and a census
   proves there is no second writer and no manual retain after a `put`.
2. **Q2 = (a): a Job's result owns its blob forever** (retained, never released, so outputs accumulate).
3. **Slice 2, option (A): legacy ownerless blobs are pinned at 1.** The migration raises each blob's
   `ref_count` to its owner count (never lowers) and pins at 1 every blob with no visible owner. There
   is no runtime backfill Job.

Slice 2's condition (comment above): the dry run must select 0 live blobs on a copy of a seeded
database, and the migration is rehearsed down as well as up.

## Options not taken

From the plan's question list:

- **Q1 (a):** an explicit `retain` paired with each `put` at the 13 sites, with the census checking the pairing.
- **Q2 (b):** a Job result released when the Job's retention window ends (FR-448 names retention windows and sets no value for jobs); **(c)** Job outputs are not owners at all.
- **Slice 2, the options other than (A):** not recorded in the issue. The enacting PR records only that (A) was chosen over a runtime backfill Job.

## Consequences

Accepted costs:

- Q1 (b): a semantic change to `put`, stated in `07` §5.2 (the plan's own statement of the cost).
- Q2 (a): outputs accumulate. A release at a retention window would need its own spec change in a later Work.
- Slice 2 (A), from the enacting PR: legacy true orphans are never collected until a later backfill
  releases them, and a pinned ownerless blob holding a data subject's rows is not released by an
  owner's purge. The migration's down is a documented no-op: a pin cannot be told from a reference a
  later `put` took on the same blob, so unpinning could release a blob a writer now holds. A follow-up
  issue for the purge case was owed by the lead when the PR merged.
