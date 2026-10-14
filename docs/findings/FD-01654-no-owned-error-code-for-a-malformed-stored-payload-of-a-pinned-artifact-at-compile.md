---
id: FD-1654
family: finding
title: No owned error code for a malformed stored payload of a pinned artifact, so compile answers BUNDLE_COMPILE_FAILED
status: active
created: 2026-10-12
owner: auditor
tree: 372fa92ae3ab306bc067c234487ce929dc0e2a04
corrected_by: []
relates: [WK-1178, SL-1557, PL-1556, LG-1606, RS-1649, FD-1437]
---

# FD-1654 — three compile sites with no owned code

*(Minted 2026-10-12 as FD-1654 from working id 9725, in the D13 batch mint PR. Every citation of a minted id in this record is re-pointed; quoted entries and the lead's quoted headers stay as quoted, and a bare working id left in them is resolved by this record's front matter.)*

Filed by the retro audit RS-1649, from the executor's finding candidate in LG-1606 (Task 3 sweep, 2026-10-09 16:25 BST entry, rows 1 to 3). Reads are at `99f22479` (PR #1271).

## Evidence

- LG-1606's sweep table, predicate verbatim, run at tree `893d8161`: rows 1 to 3 are `compile_bundle`'s `RatingAlgorithm.model_validate(resolved_algorithm.payload)`, `_refuse_unapproved_objectives`' `ArtifactRef.model_validate(objective["ref"])` and `_refuse_control_factor_keys`' `ArtifactRef.model_validate(factor_ref)`. Each raises a pydantic `ValidationError` (a `ValueError`) that reaches `compile_rating_version`'s `except ValueError` and is answered `BUNDLE_COMPILE_FAILED`.
- The executor wrote: "rows 1–3 are recorded for the auditor as a finding candidate (no spec code for 'a pinned artifact's stored payload is malformed')". `03` §5.1 owns no such code.

## Finding

**Severity LOW (proposed by the auditor).** The sites need a stored artifact that no longer validates, so a corrupt artifact; the generic code is accurate but gives the author no pointer.

**Failure mode: LOUD, never a misprice** (the maintainer's test, `to-lead.md` "2026-10-11 20:17:38 BST" item 4). Read at `origin/main` `372fa92a`:
- The three raise sites are `packages/pricing-core/src/pricing_core/rating/compile.py:761` (`ArtifactRef.model_validate(objective["ref"])`), `:785` (`ArtifactRef.model_validate(factor_ref)`) and `:1007` (`RatingAlgorithm.model_validate(resolved_algorithm.payload)`). Each raises before `compile_bundle` builds a `Bundle`, so no bundle exists to price with.
- `backend/src/app/platform/rating_versions.py:816-838` (`compile_rating_version`): the `except ValueError` at `:821` re-raises `PlatformError(code, ..., 422, detail)` with `code = "BUNDLE_COMPILE_FAILED"` when the text carries no coded prefix (`:827-829`), and `row.bundle` is set only after the `try` (`:833`), so a failed compile writes none. The compile Job fails with that code.
- The detail is rendered through `safe_error_detail(exc)` (`:826`), so a `ValidationError` is input-free (NFR-499).

## Disposition

**Owner: WK-1178 (spec change by the decision-maker).** Decision: `fix before close with an owner: WK-1178`, or accept at the P2 close; because the mode is LOUD, a P3 carry is acceptable under the maintainer's condition. Event that next confirms or discharges it: a ruling naming a code or accepting `BUNDLE_COMPILE_FAILED`.

## Discharge path

Required by the maintainer's condition, `to-lead.md` "2026-10-11 20:17:38 BST" item 4. Deferred to WK-1178 as a P3 carry: the decision-maker rules a named code or accepts the generic one, decided no later than the P2 close review (target the P2 exit demo, Thu 2026-11-12); if a code is named, a red-first test per site (`compile.py:761`, `:785`, `:1007`) closes it. Filed by the auditor, 2026-10-11; the lead gives the verdict.
