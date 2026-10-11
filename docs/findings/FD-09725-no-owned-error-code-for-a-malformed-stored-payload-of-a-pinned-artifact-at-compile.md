---
id: FD-9725
family: finding
title: No owned error code for a malformed stored payload of a pinned artifact, so compile answers BUNDLE_COMPILE_FAILED
status: active
created: 2026-10-11
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
corrected_by: []
relates: [WK-1178, SL-1557, PL-1556, LG-1606, RS-9703, FD-1437]
---

# FD-9725 — three compile sites with no owned code

Filed by the retro audit RS-9703, from the executor's finding candidate in LG-1606 (Task 3 sweep, 2026-10-09 16:25 BST entry, rows 1 to 3). Reads are at `99f22479` (PR #1271).

## Evidence

- LG-1606's sweep table, predicate verbatim, run at tree `893d8161`: rows 1 to 3 are `compile_bundle`'s `RatingAlgorithm.model_validate(resolved_algorithm.payload)`, `_refuse_unapproved_objectives`' `ArtifactRef.model_validate(objective["ref"])` and `_refuse_control_factor_keys`' `ArtifactRef.model_validate(factor_ref)`. Each raises a pydantic `ValidationError` (a `ValueError`) that reaches `compile_rating_version`'s `except ValueError` and is answered `BUNDLE_COMPILE_FAILED`.
- The executor wrote: "rows 1–3 are recorded for the auditor as a finding candidate (no spec code for 'a pinned artifact's stored payload is malformed')". `03` §5.1 owns no such code.

## Finding

**Severity LOW (proposed by the auditor):** the sites need a stored artifact that no longer validates, so a corrupt artifact; the generic code is accurate but gives the author no pointer. Verdict candidate: deferred with owner; a code needs the decision-maker.

## Disposition

**Owner: WK-1178 (spec change, decision-maker).** Decision: `fix before close with an owner: WK-1178`, or accept at the P2 close. Event that next confirms or discharges it: a ruling naming a code or accepting the generic one. Filed by the auditor, 2026-10-11; the lead gives the verdict.
