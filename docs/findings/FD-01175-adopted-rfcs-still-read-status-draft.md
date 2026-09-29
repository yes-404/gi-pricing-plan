---
id: FD-1175
family: finding
title: Adopted RFCs still read status draft
status: closed
created: 2026-09-28
owner: auditor
tree: df8e5811a151a99c7317690faf9278a6dc3400be
corrected_by: []
relates: [RFC-896, RFC-897, RFC-898, PL-900, CR-1173]
---

# FD-1175 — Adopted RFCs still read status draft

Filed by the auditor on 2026-09-28 in WK-694's closure record (`CR-1173`), on the lead's
ruling of that day. Read at `df8e5811`.

## Finding

The proposal family's lifecycle is `draft → active → closed | retired | superseded`
(`document-ids.md` §1.2a, restated in each RFC's own header comment). An RFC that the
maintainer has adopted, and whose work has landed, therefore should not still read `draft`.
RFC-896 was adopted on 2026-09-01 and its P1–P5 have all merged, yet its header still reads
`status: draft`. RFC-897 and RFC-898, adopted by the same dated line, also read `draft`. No
process step moves an RFC out of `draft` when it is adopted, so the header understates the
record's state and does so silently.

## Evidence

- The command is `grep -m1 -n '^status' docs/rfcs/*.md`, run at `df8e5811`. The corpus is the
  20 `RFC-` files, with `README.md` excluded. **6 of 20** read `draft`: RFC-840, RFC-841,
  RFC-896, RFC-897, RFC-898 and RFC-928. RFC-895 reads `closed` and RFC-937 reads `active`.
- Adoption of three of the six is proven by `PL-900:347`: *"Maintainer acceptance: accepted
  as proposed, 2026-09-01 — all four dispositions (RFC-895 remainder E/F/G, RFC-896 P1–P5,
  RFC-897 Stages 2–5 as one Work row, RFC-898 residue)"*. RFC-895 was adopted by the same line
  and reads `closed`, so the same act left sibling records in different states.
- This record does not establish whether RFC-840, RFC-841 and RFC-928 were adopted. They are
  in the count because of their status, and the adoption verdict for each is left to the
  owner below.

## Disposition

**Deferred with an owner — the lead.** Event: the first slice of the create-read-retire audit
Work (WK-1170), whose subject is the step behind each lifecycle transition. This is the lead's
ruling of 2026-09-28. WK-694's close does **not** flip RFC-896's status: that is another
record's lifecycle, and check 34's treatment of a status edit on it is untested.

**Resolved 2026-09-28** in PR #855 (the register-and-records pass, branch `p2-b-records`), on the
maintainer's instruction as relayed in the deputy's entry in the lead's local channel file
`to-lead.md` stamped 2026-09-28 12:51:59 BST (part B). That instruction supersedes the
deferral above.

- **The count, re-measured at `37b2596e`.** `grep -m1 '^status:' docs/rfcs/RFC-*.md` gives
  **6 of 20** `draft`: RFC-840, RFC-841, RFC-896, RFC-897, RFC-898 and RFC-928. **The sixth file
  is RFC-928**, which is genuinely open (never reconciled) and **stays `draft`**.
- **Set `status: closed` by this PR,** on the `status:` line only, because RFC is a frozen
  family:
  - RFC-840 and RFC-841, adopted 2026-08-29 (`CR-891:196–198`). Their migration cause is
    `FD-1190`.
  - RFC-896, after WK-694 closed (#836).
  - RFC-898, after WK-696 closed (#849, `37b2596e`).

  Check 34 did not fire on these edits: the detached audit-docs run reported only check 39
  (INDEX stale).
- **RFC-897** closes in WK-695's closing PR (#839), in the same commit as that Work's
  acceptance line, and not here.
- **RFC-937:** *"RFC-937 is deliberately left `active` by the maintainer's decision of 2026-09-28 (relayed by the deputy): open until F93's amendment and the close of WK-1169 and WK-1170; not an instance of this finding."*
