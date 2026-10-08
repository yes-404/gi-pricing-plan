---
family: reference
title: Process backlog — process findings held until the P2 phase review
status: active                  # active → retired (§1.2a)
created: 2026-10-08
owner: maintainer
tree: 8b0256fdb5f000c11817838c129e1f9a4f8d8e10
corrected_by: []
relates: []                      # ids only
---

# Process backlog

**Why this file exists.** Lean P2, item L3, approved by the user and in force from the
maintainer's entry in `~/gi-pricing-plan.local/channel/to-lead.md` headed
"2026-10-08 11:51:58 BST — USER DECISION: LEAN P2 items 1, 3 and 5 APPROVED; IN PRACTICE NOW;
the files are amended through RFC 9479 P6 (the maintainer's amendment, by delegation)".
It is written into the process by RFC 9479 P6 (working id): amended 2026-10-08 by the maintainer (dated line by delegation), on RFC-9479 P6. Until the P2 exit demo
(Thu 2026-11-12), a finding **about the process itself** is not filed as an `FD-`. It is
appended here as one dated row.

**What counts as a process finding.** A finding about document ids, `docs/INDEX.md`, the
audit or doc checks, role files, skills, record forms, or the merge or mint procedure.

**The safety valve: it is still an `FD-`**, filed as before, when the process defect:

- **(i)** lets a wrong merge, a wrong number, a mispricing or data loss through; or
- **(ii)** blocks work today.

The lead names the limb, (i) or (ii), in the `FD-`. A product defect is always an `FD-`.

**How a row is written.** Append only. Never edit or delete an earlier row. One row per
finding, with four cells: the date (`TZ=Europe/London date`, pasted, never typed), what was
found, the evidence (a command and its output, or a file and line at a named tree), and who
found it. A row rides the next batch or slice PR. **It never gets its own PR.**

**What happens to the rows.** The P2 phase review (`CLAUDE.md` §14) reads every row. Each one
is kept, filed as an `FD-`, or dropped, and the review records which.

**Open process-finding drafts on 2026-10-08.** A draft that is not yet ruled and is not in a
minting batch moves here as a row, and its PR closes naming this file. Ruled drafts, and drafts
in batch T1 or later, finish as planned. The lead lists both sets by PR number before closing
anything, and the maintainer approves that list.

| Date | What | Evidence | Who |
|---|---|---|---|
