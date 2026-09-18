---
id: FD-1069
family: finding
title: '`_h1_residue_by_file`''s docstring and `tracked_files`''s docstring disagree about which population a sweep-excluded file''s per-file attribution reaches'
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-18
owner: lead
tree: 4d9fe1d62328285ac0483b047c3959e39e0f5bd6
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
---

# FD-1069 — `_h1_residue_by_file` and `tracked_files` disagree on their own populations

## Finding

Two docstrings in the same module describe the tracked-file population differently.
`_h1_residue_by_file`'s docstring (`scripts/_docverify.py:3054-3056`) reads: "the unfiltered
tracked-file set of the migrated snapshot." `tracked_files`'s own docstring (`:428-430`) reads:
"`_LS_FILES_ARGS`'s population, minus every `_docid.sweep_exclusion_reason` hit" — a
**filtered** set. The two disagree exactly as stated: one function's documented input is
"unfiltered," the other's is "filtered by sweep-exclusion." Disclosed as `(d → W37-11)` in the
squash commit ("Disclosed to W37-11" section) — disclosed only, not fixed.

## Evidence

Verified directly against source at `4d9fe1d`: `scripts/_docverify.py:3054-3056` and
`scripts/_docverify.py:428-430`, read side by side. `CR-1063` §4 (the squash commit's own
"Disclosed to W37-11" section), quoted: the deputy's ruling names it `(d → W37-11)`:
"`_docverify._h1_residue_by_file` docstring says 'the unfiltered tracked-file set' while
`tracked_files` is filtered by `sweep_exclusion_reason` (by design): per-file attribution for
sweep-excluded files (generated contracts, governance records) is a design item — owner
lead."

## Disposition

**Deferred with an owner — lead, decaying to W37-11.** Whether a sweep-excluded file's
per-file attribution should reach `_h1_residue_by_file`'s population is a design question the
disagreement surfaces rather than answers; not fixed in this record. Falsifiable: discharged
when one of the two docstrings is corrected to match the other's actual filtering behaviour,
or the design decision is made explicit and both docstrings are brought into agreement with it.
