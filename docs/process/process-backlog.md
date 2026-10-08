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
| 2026-10-08 12:02:41 BST | **Runtime-state artifact B has no live writer**; F58 and F91 were recorded "resolved" on 2026-09-27, wrongly: the mechanism is a sentence in the watcher role file, not a running process (FD 9640, working id, never minted). **Its premise is stale:** the measurement is from 2026-09-29, so re-measure the artifact's mtime and writer before acting on this row. | #909 @ `658504e49e81` (FD 9640's essay; measured 2026-09-29T15:37:52Z at `origin/main` `2c2bbcdf`); moved here by the maintainer's entry "2026-10-08 11:56:02 BST — L3 LIST (handover/l3-list-2026-10-08.md) RULED: six PRs leave (#909 #1163 #982 #1147 #1146 to backlog rows; #1159 folded into #1240); #1153 STAYS and mints, being already ruled", item 1 | auditor (FD 9640's author); row by planner-rfc9479 |
| 2026-10-08 12:02:41 BST | **OQ-1316 and OQ-1373 have no row in `docs/roadmap.md` §10's decision-gate table**, so the plan does not show when they must be answered; `.claude/skills/spec-change` requires the row, and `audit-docs.py` does not check it (FD 9619, working id, LOW, owner WK-1170). The missing rows themselves are a roadmap edit that rides the next batch or slice PR. | #1163 @ `5535f22c2307` (FD 9619's essay: the `docs-audit` skill's gate-table script at `809a3794`, missing `OQ-1316`, `OQ-1373` among others); the maintainer's entry "2026-10-08 11:56:02 BST — L3 LIST (handover/l3-list-2026-10-08.md) RULED: six PRs leave (#909 #1163 #982 #1147 #1146 to backlog rows; #1159 folded into #1240); #1153 STAYS and mints, being already ruled", item 1 | auditor (auditor-oq-gate); row by planner-rfc9479 |
| 2026-10-08 12:02:41 BST | **A working-id reservation ledger, and an allocator that refuses a held id** (WK-1178 backlog slice SL 9836, working id, `draft`). The defect behind it is already minted as FD-1338; this row is the remedy's work item, consistent with RFC-9479's 3B being deferred past P2. | #982 @ `e029de9a883f` (SL 9836's roadmap row, `relates: [FD-1338]`); the maintainer's entry "2026-10-08 11:56:02 BST — L3 LIST (handover/l3-list-2026-10-08.md) RULED: six PRs leave (#909 #1163 #982 #1147 #1146 to backlog rows; #1159 folded into #1240); #1153 STAYS and mints, being already ruled", item 1 | planner; row by planner-rfc9479 |
| 2026-10-08 12:02:41 BST | **The freeze rule reconciled with history before check 34's merge-base comparison goes live** (RFC 9653 + RL 9654, working ids, proposed, never ACKed). **Accepted consequence:** check 34's merge-base comparison stays inactive until after P2, and FD-1282 and FD-1323 stay open on `main`; frozen-record discipline is enforced at the maintainer's ACK by reading `-U0` on every frozen-family file a PR touches; a correction goes through a correcting record, never an appended note. | #1147 @ `8090bf647023` (RFC 9653 and RL 9654); the maintainer's entry "2026-10-08 11:56:02 BST — L3 LIST (handover/l3-list-2026-10-08.md) RULED: six PRs leave (#909 #1163 #982 #1147 #1146 to backlog rows; #1159 folded into #1240); #1153 STAYS and mints, being already ruled", item 2 | decision-maker; row by planner-rfc9479 |
| 2026-10-08 12:02:41 BST | **WK-1170: check 34 runs its merge-base comparison, so a frozen file's body cannot change with the gate green** (leaf plan PL 9662 and slice SL 9655, working ids, `draft`; FD-1282, FD-1323 duplicate). Blocked on the previous row (RL 9654). When picked up after P2, it is planned as a row of WK-1170's one plan (L5). | #1146 @ `162e4a9ae886` (PL 9662 and SL 9655); the maintainer's entry "2026-10-08 11:56:02 BST — L3 LIST (handover/l3-list-2026-10-08.md) RULED: six PRs leave (#909 #1163 #982 #1147 #1146 to backlog rows; #1159 folded into #1240); #1153 STAYS and mints, being already ruled", item 2 | planner; row by planner-rfc9479 |
