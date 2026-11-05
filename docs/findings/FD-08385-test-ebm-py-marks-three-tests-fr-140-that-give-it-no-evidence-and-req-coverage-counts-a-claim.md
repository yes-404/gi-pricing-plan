---
id: FD-8385
family: finding
title: test_ebm.py marks three tests FR-140 that give it no evidence, and req-coverage counts a claim
status: active
created: 2026-11-05   # working id 8385, minted at the batch 12 mint
owner: lead
tree: ca63dd15   # the head the auditor read; origin/main when drafted is cded9f0e1953f2db6a6a1375892257a1a4822fc3
corrected_by: []
relates: [FD-1228, SL-8334, LG-8335, PL-8333, FR-140, FR-122, WK-1178]
---

# FD-8385 — `test_ebm.py` `:391`, `:398` and `:448` are marked FR-140

## Finding

**LOW, owner WK-1178; test-only.** (to-lead "2026-11-05 16:52:49 GMT" item 3: "a marker that proves nothing feeds coverage: req-coverage counts a claim".) FR-140 (`docs/specs/02-modelling.md`) is EBM transparency: shape functions exported as tables, no approximation. At `ca63dd15` of `packages/pricing-core/tests/test_ebm.py`, five tests (`:193`, `:223`, `:255`, `:294`, `:333`) test the tables and are FR-140 evidence. Three do not:

- `:391` `test_a_monotone_constraint_on_a_categorical_feature_is_refused_by_name` and `:398` `test_a_monotone_constraint_naming_an_unknown_slug_is_refused_by_name` assert `EBM_MONOTONE_CONSTRAINT_INCOMPLETE`: monotone-constraint tests (FR-122), which nothing in FR-140 mentions.
- `:448` `test_fit_seconds_and_library_versions_are_recorded` asserts a provenance record (FD-1228 noted it and left it).

Two effects: FR-140 is over-credited, and the requirement each test actually evidences is uncredited. The refit test at `:427-428` (FR-11's, not FR-140's) is the same shape and was raised earlier in the FD-1228 records.

## Evidence

The lines named above, read by the auditor at `ca63dd15` (`scratch/aud-slh/FD-new-ebm-markers.md`); `scripts/req-coverage.py` before and after is owed by the remedy.

## Not claimed

That FR-140 lacks evidence (five tests carry it), or that the refusal tests are unneeded.

## Remedy (proposed)

Re-tag `:391` and `:398` to FR-122 (or the requirement the WK-661 note in `02-modelling.md` ties the code to, read first) and `:448` to the requirement holding the provenance record; run `scripts/req-coverage.py` before and after. A marker move is not a weakening (PL 8333 G6).

## Disposition

Open, owner WK-1178; event that next discharges it: the re-tag merging with the coverage before/after, or a dated acceptance recorded on FD-1228. Source: `scratch/aud-slh/FD-new-ebm-markers.md` (aud-slh, 2026-11-05), filed as working id 8385.
