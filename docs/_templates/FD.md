<!--
TEMPLATE — Finding (`FD-`), one finding: a register row plus a frozen essay.
This file is the essay half. Copy it to `docs/findings/FD-<nnnnn>-<slug>.md`, where
`<nnnnn>` is the padded result of `python3 scripts/doc-id.py next`; file the matching
row in `docs/findings/register.md` with the same id. Fill in every placeholder, delete
this comment block, and remove any field this finding does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `kind:`, `phase:`, `work:`, `slice:`,
`plans:`, `supersedes:` and `superseded_by:` do not apply to this family and must not
appear here. `decision:` below is this family's declared extra (§1.2's family table) —
no other family may use it. `decision:` carries the register disposition and is never
confused with `status:` (NT-0015 P4).
-->

---
id: FD-NNNNN
family: finding
title: <one line — the defect or gap, not the fix>
status: active                  # active → closed | retired (§1.2a)
created: YYYY-MM-DD
owner: auditor
tree: <commit-sha this was written against>
decision: <fix before close | accept | carry forward | split verdict, with qualifiers>
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
---

# FD-NNNNN — <Title>

## Finding

<What was found, and against which requirement, NFR or acceptance item.>

## Evidence

<How it was verified — a command, a diff, a broken-input proof; never assertion alone.>

## Disposition

<The `decision:` value explained — if `fix before close`, the `SL-` (under the owning
Work, or `WK- maintenance`) that will discharge it; if `accept`, why; if unowned, that it
decays to the phase review per §1.6.>
