---
id: FD-1168
family: finding
title: audit-docs check 9 reads a time's minute field as a spec number
status: active
created: 2026-09-27
owner: auditor
tree: 6a97cf25c9a72c520f9e66b2155a7e3a2ffc66f4
corrected_by: []
relates: [CR-1167]
---

# FD-1168 — audit-docs check 9 reads a time's minute field as a spec number

Filed by the auditor on 2026-09-27, in W37-11's closing-record PR (#823), on the lead's
instruction. The auditor reproduced the failure before filing.

## Finding

Check 9 of `scripts/audit-docs.py` verifies cross-spec section references, of the form "a
two-digit spec code, then a section sign and a number". Its pattern is `sec_re`
(`scripts/audit-docs.py:3867` at `6a97cf25`). The pattern opens with the negative lookbehind
`(?<![0-9-])`. That excludes a digit or a hyphen before the spec code, but not a colon. So in
a clock time such as `17:02:52`, the minute field `02` is read as spec code `02` whenever a
section sign follows within 24 characters. The check then reports a broken cross-reference to
`02-modelling.md`.

The check's own comment warns about this class of error for dates. It says that without the
lookbehind *"the `02` inside a date like `2026-08-15` matches … It reads exactly like a real
finding, which is the worst kind of false positive"*. A time is the same shape with a
different separator, and the lookbehind does not cover it.

## Evidence

- **The firing commit.** `02435a68` is the commit that added the lead's first quotation of
  the plan-review 14 acceptance line to `CR-1167`. It is not on `main`; it is reachable via
  `refs/pull/823/head`, whose head is `6a97cf25`.
- **The line that fired.** It quoted the deputy's heading, which puts the time `17:02:52 BST`
  followed by `), CLAUDE.md` and then a section sign and `14`.
- **The reading.** On a detached copy of `02435a68`, on 2026-09-27, `python3
  scripts/audit-docs.py` exited 1 with this failure: *"check 9:
  closures/CR-01167-plan-review-14-the-wk-697-close-the-register-rows-decayed-to-it-and-the-two-downstream-works.md:
  reference to 02 ⟨section sign⟩14 — no such section in 02-modelling.md"*. The section sign is written as ⟨section sign⟩ here, because the literal message would fire check 9 in this record.
- **The workaround.** The deputy re-issued the line at 16:20:35 BST with the same decision and
  its time of 16:18:24 BST. The wording now says *"its section fourteen"*. The line at
  `6a97cf25` passes. The re-issue avoided the defect; it did not fix it.

This record spells no clock time next to a section sign, so that it does not fire the check
itself.

## Disposition

**Deferred with an owner — the lead** (the lead's instruction, 2026-09-27). Event: the
create-read-retire audit's first slice. The fix is the owner's choice. One option is to add
`:` to the lookbehind. Another is to require the spec code to stand alone, and not inside a
numeric run with a separator. Either fix wants a broken-input test built from a clock time,
beside the existing date case.
