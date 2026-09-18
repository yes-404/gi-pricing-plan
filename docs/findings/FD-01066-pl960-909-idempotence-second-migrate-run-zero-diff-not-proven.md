---
id: FD-1066
family: finding
title: PL-960:909's idempotence proof (a second migrate run over already-migrated output, zero diff) was not run
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-18
owner: auditor
tree: 4d9fe1d62328285ac0483b047c3959e39e0f5bd6
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
---

# FD-1066 — PL-960:909's idempotence proof was not run

## Finding

`docs/plans/PL-00960-w37-6-the-migration-run-leaf-plan.md:909` (unchecked `- [ ]`): "Prove
idempotence on the real tree: a second `migrate` run produces zero diff." What was actually
proven during the run 2 migration is **determinism of a first run** (two independent runs from
the same pristine base produce the identical tree), not idempotence of a second run over
already-migrated output — a different property. No observation of a genuine second `migrate`
run over migrated input exists; the only observation adjacent to it is a `--ref` resolution
defect (CI resolving `HEAD` to an already-migrated PR merge ref), which is a tooling bug in
the verify instrument, not evidence about `migrate()`'s own idempotence.

## Evidence

`CR-1063` §5 (`docs/closures/CR-01063-w37-6-run-2-the-closure-g-record.md`): T⁗ and T⁵, two
independent runs of `scripts/doc-id.py migrate` against `main` at `M=0651c1e265648cbd3918adfc729ad965b83b1e0b`
from a pristine base, agree byte-for-byte on tree `6d058ba642481404815ab573e848a8cf34e671ee`
— first-run determinism, confirmed. The docs-CI exit-3 incident (`CR-1063` §2): CI run
`35261236904` on head `323b523` exited 3 at `doc-id migrate --verify` because `--ref HEAD`
resolved to the already-migrated PR merge ref, producing a `SET CHANGE (9)` block — a
`--ref` resolution defect, fixed, not idempotence evidence. The measured figure this item
carries forward with, `handover/team2-ci-docs-323b523.log:1239`: `REGRESSION (residue
exceeds W37-11 ceiling): 'scripts/doc-id.py' (d10) — 41 hit(s) exceeds the W37-11 record's
ceiling of 15 for 'd10'`.

## Disposition

**Deferred with an owner — W37-11.** The literal proof (run `migrate` a second time over its
own already-migrated output and assert zero diff) has not been run by any session to date.
W37-11's own idempotence work starts from the measured figure above. Falsifiable: discharged
by a `migrate` run over migrated input on a disposable snapshot, with the diff shown.
