<!--
TEMPLATE — Finding (`FD-`), one finding: a register row plus a frozen essay.
This file is the essay half. Copy it to `docs/findings/FD-<nnnnn>-<slug>.md`, where
`<nnnnn>` is the padded result of `python3 scripts/doc-id.py next`; file the matching
row in `docs/findings/register.md` with the same id. Fill in every placeholder, delete
this comment block, and remove any field this finding does not use.

Full field set, status vocabulary and role assignments:
`docs/process/document-ids.md` §1.5, §1.2a, §1.6. `kind:`, `phase:`, `work:`, `slice:`,
`plans:`, `supersedes:` and `superseded_by:` do not apply to this family and must not
appear here. `decision:` is **not** a field of this essay's header: it is the `FD-`
register row's own field, in `docs/findings/register.md`, never this frozen essay's
(RL-981, `docs/rulings/RL-00981-decision-is-a-register-row-field-not-an-essay-header-field-the-contradiction-dissolves-rather-than-needing-a-widened-field-set.md`; RFC-937 §5.2
migrates the register's existing Decision cell into that row's `decision:`). Putting a
value that changes on a frozen file is unmaintainable under check 34's freeze rule, which
is why the essay never carried it correctly. `decision:` still carries the register's
disposition and is never confused with the essay's own `status:` (RFC-896 P4) — they are
on different artifacts, which is how that rule is satisfied without widening this
header's closed field set.
-->

---
id: FD-NNNNN
family: finding
title: <one line — the defect or gap, not the fix>
status: active                  # active → closed | retired (§1.2a)
created: YYYY-MM-DD
owner: auditor
tree: <commit-sha this was written against>
corrected_by: []
relates: []                     # ids only — the SL-/WK- this discharges through, once known
---

# FD-NNNNN — <Title>

## Finding

<What was found, and against which requirement, NFR or acceptance item.>

## Evidence

<How it was verified — a command, a diff, a broken-input proof; never assertion alone.>

## Disposition

<The register row's `decision:` value, explained in prose — if `fix before close`, the
`SL-` (under the owning Work, or `WK- maintenance`) that will discharge it; if `accept`,
why; if unowned, that it decays to the phase review per §1.6.>
