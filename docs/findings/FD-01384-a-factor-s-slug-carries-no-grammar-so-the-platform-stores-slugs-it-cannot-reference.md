---
id: FD-1384
family: finding
title: A Factor's slug carries no grammar, so the platform stores slugs it cannot reference
status: active
created: 2026-10-03              # the mint date (check 31); filed 2026-10-03
owner: auditor
tree: 33cbff79ba83dbdf7912c5ddbfc6448008a8a451
corrected_by: []
relates: [RL-1383, RL-1361, SL-1377, WK-1178, FR-83, FR-96, FR-209, FR-4]
---

# FD-1384 — a Factor's slug carries no grammar, so the platform stores slugs it cannot reference

**Filed under working id 9742; minted 2026-10-03 as FD-1384.** Proposed by the
decision-maker session `dm-1377` with the ruling filed under working id 9743 (minted as
RL-1383), which found it while ruling SL-1377's `factor_ref` question. Every path and
count below was read at `origin/main` `d672f991` (tree `33cbff79`). `document-ids.md` §1.6's
FD row names the auditor as the family's writer. This one was filed by the decision-maker
because the lead's brief asked for it (to-lead.md entry headed "2026-10-03 17:27:58 BST —
LANE B STOP accepted; GO dm-1377 …", requirement 4), and the auditor re-filed it at the mint
(`owner: auditor`, the FD-1366 precedent).

## Finding

**Severity: MEDIUM**, on the grounds in the maintainer's to-lead.md entry headed
"2026-10-03 17:48:44 BST — CORRECTION on FD 9742 (my rationale and discharge were wrong): MEDIUM stands on corrected grounds; option (a), a later WK-1178 item; GO planner-9765fix" (set at the mint; see Disposition): a missing write-boundary
check on an identifier that feeds model terms and references; the failures are loud (500s and
refusals), not a mispricing; exposure today is none beyond `_`, now legal under RL-1383.
`Factor.slug` (`packages/model-schema/src/model_schema/modelling.py:133`)
and `FactorCreate.slug` (`backend/src/app/api/models.py:207`) are a plain `str`. No pattern,
no length limit, no character set. `00` §4.3 gives every persisted entity a slug pattern, and
RL-1383 rules the Factor's own pattern, `^[a-z0-9][a-z0-9_-]{1,62}$`. Nothing on the write path
enforces either.

## Evidence

**Probe** (scratch `/tmp/dm1377_probe.py`, sha256 prefix `d6d1e3e4e5632eab`, importing this
tree's `model_schema`): `Factor(...)` accepts the slugs `""`, `"Veh Brand"`, `"a:b@1"` and a
65-character slug.

**Consequences, each read from the code:**

1. **A slug the reference grammar cannot hold.** The slug becomes `factor:<slug>@<version>`
   in the audit log (`backend/src/app/platform/modelling.py:260`, unvalidated) and, from
   SL-1377, in `RateTableKey.factor_ref`. `"a:b@1"` makes the audit reference ambiguous. RL
   RL-1383 Ruled item 3 makes the seed refuse such a slug, which contains this at one consumer
   and leaves the Factor creatable.
2. **A 65-character slug reaches a `String(64)` column** (`backend/src/app/db/models.py:1323`).
   By reading, not executed: nothing refuses it before the `INSERT`, so it fails at the
   database rather than as a 422.
3. **The slug is a term name.** It is the GLM term, the GBM feature name and the
   monotone-constraint key (`02` §4.1). An empty or space-bearing slug reaches all of them.

**The same class, not swept here.** `Banding.slug` (`modelling.py:355`) and `Grouping.slug`
(`:508`) are a plain `str`, and a Banding is already referenced through
`RateTableKey.banding_ref: ArtifactRef` (`model_schema/rating.py:669`). So an out-of-grammar
Banding slug would dump and fail on re-read, which is the defect RL-1383 found for Factor.
`RatingVersionCreate.slug` (`api/models.py:274`) is a plain `str` while `RatingVersion`'s own
slug fields are `Slug`. These are listed for the owner to sweep, not asserted as defects.

### Measured stored state

Every `gipricing*` database on the local stack, 2026-10-03 at about 17:36 BST, with the query
RL-1383 "Reach, measured" item 3 gives verbatim: **0 Factor rows outside
`^[a-z0-9][a-z0-9_-]{1,62}$` in each of the 79 databases that have a `factors` table**, and 1
Banding and 1 Grouping row, both inside the envelope pattern. This is a development machine.
The state of any other install is unknown.

## Disposition

**Set at the mint** from the to-lead.md entry headed
"2026-10-03 17:48:44 BST — CORRECTION on FD 9742 (my rationale and discharge were wrong): MEDIUM stands on corrected grounds; option (a), a later WK-1178 item; GO planner-9765fix" (it supersedes the FD 9742 paragraph of the
entry before it, which described the build/parse gap inside SL-1377, not this finding).
**MEDIUM; owner WK-1178; fix before close.** The discharge is **option (a): a later WK-1178
item, after SL-1377**, scheduled in the WK-1178 queue. SL-1377 does not discharge this
finding: it refuses an out-of-grammar slug at the seed and validates a field-built reference
(RL-1383 Ruled items 2 and 3), and a Factor with `""`, `"a:b@1"` or 65 characters is still
creatable after it. The later item is this finding's remedy:

- **Refuse at the write boundary** (named 422s, spec text first). `FactorCreate.slug` takes the
  Factor pattern, and the Banding and Grouping create bodies take theirs. Sweep Banding,
  Grouping and `RatingVersionCreate` in the same item, or file each that it confirms.
- **Do not refuse on read until stored rows are swept.** `to_factor`'s `Factor.model_validate`
  on read fails the whole workspace's factor list on one bad row (FR-209 records that failure
  for a stored `offset` row). Stored artifacts are immutable (FR-4) and a slug is the lineage
  key (FR-96), so a stored out-of-grammar slug is never rewritten. The read model stays
  tolerant, or the owner rules what a stored violator becomes.
- **Not in SL-1377.** RL-1383 keeps that slice bounded. It refuses an out-of-grammar slug at
  the seed, and it does not constrain `Factor`.

Event: the finding closes when the later WK-1178 item merges and refuses out-of-grammar Factor,
Banding and Grouping slugs at the write boundary with a named 422 each (or the sweep files the
residue), citing that PR.

---

Filed 2026-10-03 as working id 9742; minted 2026-10-03 as FD-1384 (with RL 9743 -> RL-1383, in the same PR).
