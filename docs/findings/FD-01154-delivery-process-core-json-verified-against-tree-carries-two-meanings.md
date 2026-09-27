---
id: FD-1154
family: finding
title: delivery-process.core.json's verified_against_tree carries two meanings, check 27's reconciliation tree and the standing verify's pinned ref
status: active
created: 2026-09-27
owner: auditor
tree: 3749db65eb29fbe95dd46e6b787960fa8386af0b
corrected_by: []
relates: [PL-1144, RL-1145]
---

# FD-1154 — delivery-process.core.json's verified_against_tree carries two meanings, check 27's reconciliation tree and the standing verify's pinned ref

Filed by the auditor at 2026-09-27 14:59:20 BST, on the deputy's ruling of 2026-09-27 14:30:13 BST
(item 2: *"the finding — filed by the Task 10 auditor with the closure record"*). It is
filed in one commit with FD-1155 to FD-1162, before the W37 closure record cites any of them
(condition 1 of the deputy's ruling of 11:16:34 BST).

## Finding

One JSON key has two readers, and they read it with two meanings.
`docs/process/delivery-process.core.json`'s `meta.verified_against_tree` is:

1. **check 27's reconciliation tree.** `scripts/audit-docs.py` reads it as the commit at which
   the process extract was last reconciled against `docs/process/delivery-process.md`. When
   the spec's bytes change, check 27's remediation says to *"update both
   `meta.derived_from_digest` and `meta.verified_against_tree`"* (the message ends at
   `audit-docs.py:1043` at `3749db65`).
2. **the standing verify's pinned `--ref`.** `.github/workflows/docs.yml:117` reads the same
   key as `--ref` for `doc-id.py migrate --verify` on a migrated checkout. Its own notice line
   calls the value *"the pre-migration base the tool recorded"*.

So the next legitimate edit to `delivery-process.md` cannot follow check 27's remediation
without moving the verify's base onto a migrated tree. If only the digest is updated, the
key names a tree the extract was not reconciled at. This is a face of `RFC-777`'s *"a word
with two scopes"*: one key, two governed meanings.

**Latent, not active.** At `3749db65` the digest matches and check 27 passes. The conflict
fires only on the next byte change to `delivery-process.md`.

## Evidence

At `3749db65`, read on a detached copy:

- `docs/process/delivery-process.core.json:7` reads
  `"verified_against_tree": "0651c1e265648cbd3918adfc729ad965b83b1e0b"`. This is the
  pre-migration base (`0651c1e`), not a tree the extract was reconciled at after the
  migration.
- `.github/workflows/docs.yml:117` sets `ref=$(python3 -c 'import json; print(json.load(open("docs/process/delivery-process.core.json"))["meta"]["verified_against_tree"])')`
  when `docs/INDEX.md` and `docs/REDIRECTS.csv` are both present.
- `scripts/audit-docs.py:1007` reads `recorded_tree = meta.get("verified_against_tree")`. On a
  digest mismatch it fails check 27 with the remediation quoted above (`:1036-1043`).

**How it surfaced.** In the W37-11 docs PR the lead drafted a one-token pointer fix to
`delivery-process.md:282`. That line is a live pointer to the checklists under the legacy
audit directory; the checklists now live under `docs/process/checklists/`. Any byte change to
the spec fails check 27 until the extract is reconciled, and reconciling it by the
remediation would re-pin the verify. The lead withdrew the edit before pushing. The deputy
confirmed the withdrawal (2026-09-27 14:30:13 BST, item 1), and `:282` stays stale in W37-11.

**A second face of the same field** (`LG-1139:241`, item 6, routed to W37-11 by that
ledger). The core-extract generator re-stamps `meta.verified_against_tree` with the
worktree's HEAD on every run. Nothing checks that the value resolves on `origin/main`. W37-10's
docs run `36270534213` failed on it, and `87965eb6` restored
`0651c1e265648cbd3918adfc729ad965b83b1e0b` (the deputy's ruling of 2026-09-26 21:46:32 BST).
So the field has a third writer, the generator, and it takes neither governed meaning.

## Disposition

**Deferred with an owner — the lead** (the deputy, 2026-09-27 14:30:13 BST). Event: the next
amendment to `docs/process/delivery-process.md`, or the create-read-retire audit's first
slice, whichever comes first. The recommended fix is the deputy's: split the field, e.g. a
`verify_pinned_ref` that the workflow reads, leaving `verified_against_tree` to check 27. The
design belongs to the owner of check 27 and `docs.yml`. The stale pointer at
`delivery-process.md:282` is carried by the same event, because that amendment must
reconcile the extract anyway.
