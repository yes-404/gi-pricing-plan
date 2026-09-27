---
id: FD-1149
family: finding
title: The migration sweep reaches files beneath a vendored manifest, which RL-990 item 3 exempts
status: active
created: 2026-09-27
owner: auditor
tree: 47065da50c34f0bf613f7dd972675c96d12f78ed
corrected_by: []
relates: [CR-1065, PL-1144, RL-990, FD-1152]
---

# FD-1149 — The migration sweep reaches files beneath a vendored manifest, which RL-990 item 3 exempts

Filed by the auditor at 2026-09-27 14:24:50 BST, as part of the first commit of PL-1144's docs PR
(PL-1144 Task 11 step 0). This is **C9** in PL-1144 Scope A. The finding was first
named in `CR-1065` §2.2 (`:200`) under a three-digit legacy alias. That alias never had a
register row, and no essay existed. PL-1144 Scope A C9 states this at `271088b0`: *"There
is no register row and no essay"*. The deputy's condition 1 (2026-09-27 11:16:34 BST)
makes this filing a precondition of the deferral: *"A deferred row carries a register row
before it is deferred. C9 has none at 271088b0 … a deferral of an unfiled finding is a
silent verdict."* The alias is recorded here so that `CR-1065`'s citation has a
destination: it is **F111**.

## Finding

RL-990 item 3 exempts the files **beneath** a vendored skill's manifest from the
tree-wide citation rewrite. `CR-1065` §2.2 quotes the ruling: *"The files **beneath** it
are exempt from the blanket stamp, the tree-wide citation rewrite and check 37's shape
check."* `scripts/doc-id.py`'s `_is_vendored_exempt` encodes the same boundary. But the
migration's legacy-form sweep still reached two files beneath
`planning-with-files/SKILL.md`: `check-complete.ps1` and `set-active-plan.ps1`, both
under that skill's `scripts/` directory. In each file it split PowerShell's
static-member (scope-resolution) operator, two colons, into a colon, a space and a
colon, and that broke the script.

The file damage is fixed: PR #788 (`a8b3c39`) restored both scripts byte for byte. The
**mechanism** is not fixed. Nothing in the tool stops the sweep from reaching a file
beneath a manifest. `CR-1065` §2.2 gives the owner as *"W37-11, a `migrate()` change
under the reproduction rule, not a content edit"*.

## Evidence

- **The first run.** `CR-1065` §2.2 (`:180-200`) records the two scripts in the
  migration's diff (2 lines each), the RL-990 item 3 quotation, the tool's boundary
  function, and the fix by #788.
- **The mechanism is still live at the tool's head of 2026-09-27.** LG-1148 Task 5
  describes a second `migrate` over an already-migrated snapshot of `03f61d83`. Its class 4
  is the same defect in the same two files: in `check-complete.ps1`, `[Console]::Out.Write(`
  becomes `[Console]: :Out.Write(`, and in `set-active-plan.ps1`,
  `[System.IO.File]::WriteAllText(` becomes `[System.IO.File]: :WriteAllText(`. So the sweep
  still reaches files beneath the manifest, and it still splits the operator. FD-1152
  files that run.
- **One pass honours the exemption and another does not.** That run's own log is in the
  local, non-governed evidence directory that FD-1152 names (`t5-migrate.log`, 423
  lines). It prints `wrote .claude/skills/planning-with-files/scripts/check-complete.ps1`
  at line 16, and `skipped (vendored) .claude/skills/planning-with-files/scripts/check-complete.ps1`
  at line 42. The same holds for `set-active-plan.ps1` (it is written at line 17). The log
  has 339 `skipped (vendored)` lines. So the tool knows the file is vendored, but the pass
  that writes the file does not ask. That is where the fix belongs. The auditor read the
  log at the time of filing.
- **Where the sweep runs.** Only `migrate` runs the sweep (PL-1144 Scope A C9). Since
  #821 (squash `47065da5`), `doc-id.py migrate` refuses, with exit 2, to run on a tree
  that is already migrated (`_docid.is_migrated_tree`: `docs/INDEX.md` and
  `docs/REDIRECTS.csv` are both present; LG-1148, *"The migrate guard"*). On the live
  tree, that guard closes the one path by which this defect could recur. `--verify` still
  runs `migrate()` over the pinned pre-migration base in a throwaway snapshot. The sweep
  reaches the vendored files there too, but the snapshot is discarded and the live tree
  is not written.

## Disposition

**Deferred with an owner — the lead**, as PL-1144 Scope A types C9 (*"deferred, lead as
owner"*), adopted by the deputy at 2026-09-27 11:16:34 BST. The event, as PL-1144 states
it verbatim: *"Event: the create-read-retire audit's first slice"*. The plan also gives
the ground: *"Only `migrate` runs the sweep, and C4 is the only remaining run of
`migrate`. C4 runs on a throwaway snapshot"*. The fix is a `migrate()` change: the sweep
must honour the boundary `_is_vendored_exempt` already draws, and a broken-input test
must hold a file beneath a manifest with a two-colon operator. It is not in PL-1144's
scope.
