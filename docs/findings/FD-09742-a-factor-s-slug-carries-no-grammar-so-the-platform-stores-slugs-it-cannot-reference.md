---
id: FD-9742
family: finding
title: A Factor's slug carries no grammar, so the platform stores slugs it cannot reference
status: active
created: 2026-10-03
owner: decision-maker
tree: 33cbff79ba83dbdf7912c5ddbfc6448008a8a451
corrected_by: []
relates: [RL-1361, SL-1377, WK-1178, FR-83, FR-96, FR-209, FR-4]
---

# FD 9742 — a Factor's slug carries no grammar, so the platform stores slugs it cannot reference

**Filed under working id 9742**, allocated by the lead. The lead mints the id at the merge
turn. Proposed by the decision-maker session `dm-1377` with the ruling filed under working
id 9743 (RL 9743), which found it while ruling SL-1377's `factor_ref` question. Every path and
count below was read at `origin/main` `d672f991` (tree `33cbff79`). `document-ids.md` §1.6's
FD row names the auditor as the family's writer. This one is filed by the decision-maker
because the lead's brief asked for it (to-lead.md entry headed "2026-10-03 17:27:58 BST —
LANE B STOP accepted; GO dm-1377 …", requirement 4), and the lead may have an auditor re-file
it.

## Finding

**Severity: proposed MEDIUM; the severity and the owner are the lead's to set and the
maintainer's to accept.** `Factor.slug` (`packages/model-schema/src/model_schema/modelling.py:133`)
and `FactorCreate.slug` (`backend/src/app/api/models.py:207`) are a plain `str`. No pattern,
no length limit, no character set. `00` §4.3 gives every persisted entity a slug pattern, and
RL 9743 rules the Factor's own pattern, `^[a-z0-9][a-z0-9_-]{1,62}$`. Nothing on the write path
enforces either.

## Evidence

**Probe** (scratch `/tmp/dm1377_probe.py`, sha256 prefix `d6d1e3e4e5632eab`, importing this
tree's `model_schema`): `Factor(...)` accepts the slugs `""`, `"Veh Brand"`, `"a:b@1"` and a
65-character slug.

**Consequences, each read from the code:**

1. **A slug the reference grammar cannot hold.** The slug becomes `factor:<slug>@<version>`
   in the audit log (`backend/src/app/platform/modelling.py:260`, unvalidated) and, from
   SL-1377, in `RateTableKey.factor_ref`. `"a:b@1"` makes the audit reference ambiguous. RL
   9743 Ruled item 3 makes the seed refuse such a slug, which contains this at one consumer
   and leaves the Factor creatable.
2. **A 65-character slug reaches a `String(64)` column** (`backend/src/app/db/models.py:1323`).
   By reading, not executed: nothing refuses it before the `INSERT`, so it fails at the
   database rather than as a 422.
3. **The slug is a term name.** It is the GLM term, the GBM feature name and the
   monotone-constraint key (`02` §4.1). An empty or space-bearing slug reaches all of them.

**The same class, not swept here.** `Banding.slug` (`modelling.py:355`) and `Grouping.slug`
(`:508`) are a plain `str`, and a Banding is already referenced through
`RateTableKey.banding_ref: ArtifactRef` (`model_schema/rating.py:669`). So an out-of-grammar
Banding slug would dump and fail on re-read, which is the defect RL 9743 found for Factor.
`RatingVersionCreate.slug` (`api/models.py:274`) is a plain `str` while `RatingVersion`'s own
slug fields are `Slug`. These are listed for the owner to sweep, not asserted as defects.

### Measured stored state

Every `gipricing*` database on the local stack, 2026-10-03 at about 17:36 BST, with the query
RL 9743 "Reach, measured" item 3 gives verbatim: **0 Factor rows outside
`^[a-z0-9][a-z0-9_-]{1,62}$` in each of the 79 databases that have a `factors` table**, and 1
Banding and 1 Grouping row, both inside the envelope pattern. This is a development machine.
The state of any other install is unknown.

## Disposition

Proposed; the lead decides.

- **Refuse at the write boundary.** `FactorCreate.slug` takes the Factor pattern (a named 422),
  and the Banding and Grouping create bodies take theirs, which the owner states in a spec
  text first.
- **Do not refuse on read until stored rows are swept.** `to_factor`'s `Factor.model_validate`
  on read fails the whole workspace's factor list on one bad row (FR-209 records that failure
  for a stored `offset` row). Stored artifacts are immutable (FR-4) and a slug is the lineage
  key (FR-96), so a stored out-of-grammar slug is never rewritten. The read model stays
  tolerant, or the owner rules what a stored violator becomes.
- **Owner: proposed WK-1178**, after SL-1377 (it shares `model_schema` and the factor routes
  with no slice open on them at `d672f991`). The lead decides.
- **Not in SL-1377.** RL 9743 keeps that slice bounded. It refuses an out-of-grammar slug at
  the seed, and it does not constrain `Factor`.
