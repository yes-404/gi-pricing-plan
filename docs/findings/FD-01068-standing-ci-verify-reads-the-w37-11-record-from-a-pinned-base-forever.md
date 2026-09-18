---
id: FD-1068
family: finding
title: the standing CI verify reads the W37-11 record from a pinned base, forever
status: active                  # active → closed | retired (§1.2a)
created: 2026-09-18
owner: lead
tree: 4d9fe1d62328285ac0483b047c3959e39e0f5bd6
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
---

# FD-1068 — The standing CI verify reads the W37-11 record from a pinned base, forever

## Finding

`.github/workflows/docs.yml`'s verify step resolves `--ref`, on a migrated checkout, to
`docs/process/delivery-process.core.json`'s `meta.verified_against_tree` — a value fixed at
`0651c1e265648cbd3918adfc729ad965b83b1e0b` (the pre-migration base the tool recorded from run
2's own commit). That fix correctly stops CI from migrating an already-migrated tree
(`CR-1063` §2, the `323b523` exit-3 incident). Its consequence, not previously named: the
standing CI verify's W37-11 residue-ceiling comparison always reads the record as it stood at
`0651c1e`. **A later edit to the W37-11 record on `main` — widening a ceiling, adding a class,
correcting a count — is invisible to the standing CI verify**, because the pinned base never
moves forward with the branch that edits the record.

## Evidence

`.github/workflows/docs.yml:117` (read directly): resolves `--ref` to
`meta.verified_against_tree`. `scripts/_docverify.py:4333`: `load_w37_11_record(snap.control)`
reads the record at that pinned ref, not at the PR branch's own head. `docs/plans/PL-01058-w37-6-migration-run-ledger.md`'s
final entries (the `#786`/W37-11 catch-up discussion, this checkpoint): a branch that edits the
W37-11 record to move row (g) FAIL → DISCLOSE cannot have that edit read by the standing CI
verify, because the verify's control tree is pinned at `0651c1e`, not the branch's own tree —
confirmed as the mechanism (not yet as a ruled disposition) in `to-lead.md`'s discussion of
`#757`/`#786` at this checkpoint.

## Disposition

**Deferred with an owner — W37-11.** This is a design choice the specs leave open (where the
standing verify should read the W37-11 record from, once the record itself is expected to
change post-migration), not a defect with one correct fix — recorded with two options and a
recommendation in `docs/open-questions.md` per `CLAUDE.md` §0's table, rather than picked
silently. W37-11 decides.
