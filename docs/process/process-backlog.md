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
It is written into the process by RFC-1506 P6: amended 2026-10-08 by the maintainer (dated line by delegation), on RFC-1506 P6. Until the P2 exit demo
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
| 2026-10-08 12:02:41 BST | **A working-id reservation ledger, and an allocator that refuses a held id** (WK-1178 backlog slice SL 9836, working id, `draft`). The defect behind it is already minted as FD-1338; this row is the remedy's work item, consistent with RFC-1506's 3B being deferred past P2. | #982 @ `e029de9a883f` (SL 9836's roadmap row, `relates: [FD-1338]`); the maintainer's entry "2026-10-08 11:56:02 BST — L3 LIST (handover/l3-list-2026-10-08.md) RULED: six PRs leave (#909 #1163 #982 #1147 #1146 to backlog rows; #1159 folded into #1240); #1153 STAYS and mints, being already ruled", item 1 | planner; row by planner-rfc9479 |
| 2026-10-08 12:02:41 BST | **The freeze rule reconciled with history before check 34's merge-base comparison goes live** (RFC 9653 + RL 9654, working ids, proposed, never ACKed). **Accepted consequence:** check 34's merge-base comparison stays inactive until after P2, and FD-1282 and FD-1323 stay open on `main`; frozen-record discipline is enforced at the maintainer's ACK by reading `-U0` on every frozen-family file a PR touches; a correction goes through a correcting record, never an appended note. | #1147 @ `8090bf647023` (RFC 9653 and RL 9654); the maintainer's entry "2026-10-08 11:56:02 BST — L3 LIST (handover/l3-list-2026-10-08.md) RULED: six PRs leave (#909 #1163 #982 #1147 #1146 to backlog rows; #1159 folded into #1240); #1153 STAYS and mints, being already ruled", item 2 | decision-maker; row by planner-rfc9479 |
| 2026-10-08 12:02:41 BST | **WK-1170: check 34 runs its merge-base comparison, so a frozen file's body cannot change with the gate green** (leaf plan PL 9662 and slice SL 9655, working ids, `draft`; FD-1282, FD-1323 duplicate). Blocked on the previous row (RL 9654). When picked up after P2, it is planned as a row of WK-1170's one plan (L5). | #1146 @ `162e4a9ae886` (PL 9662 and SL 9655); the maintainer's entry "2026-10-08 11:56:02 BST — L3 LIST (handover/l3-list-2026-10-08.md) RULED: six PRs leave (#909 #1163 #982 #1147 #1146 to backlog rows; #1159 folded into #1240); #1153 STAYS and mints, being already ruled", item 2 | planner; row by planner-rfc9479 |
| 2026-10-08 12:16:41 BST | **The working-id lint, T3 of RL 9634, is not built in P2.** RFC 9635 + RL 9634 (working ids) mint in their batch as already ruled, but T3 (a lint on a working-id citation left in a file after its id has minted, hosted in check 32) is not built here. **RL 9634's warn-to-fatal date does not start until a slice builds T3.** | #1153 @ `17236d99a882` (RFC 9635 and RL 9634; T3 adopted by OP-C, "not built here"); the maintainer's entry "2026-10-08 11:56:02 BST — L3 LIST (handover/l3-list-2026-10-08.md) RULED: six PRs leave (#909 #1163 #982 #1147 #1146 to backlog rows; #1159 folded into #1240); #1153 STAYS and mints, being already ruled", item 3(a) | decision-maker (RL 9634's author); row by planner-rfc9479 |
| 2026-10-08 12:09:03 BST | **`audit-docs.py` check 37 cannot version a template.** It requires every `##` heading of a family's template in every document of that family, with no cutoff date, so adding a section to a template reds every earlier document (adding Scope, Gate, Audit and Build log as `##` to `docs/_templates/LG.md` red 30 existing ledgers). The L1 (a') sections were therefore written as `###` under `## Tasks`. A cutoff like check 28's would let a template grow. | `scripts/audit-docs.py` `_template_body_sections` and `_SECTION_HEADING_RE` (`^##\s+(.+?)\s*$`) at `8b0256fd`; the 30 check-37 failures measured on this branch's working tree before the `###` form | planner-rfc9479 |
| 2026-10-09 10:54:55 BST | **The recurring stray `cd` by team seats, despite the role files' no-`cd` rule: six instances on 2026-10-08.** planner-rfc9479 (`cd /dev/null`, failed), finisher-sl1448 (`cd /tmp`, in a log fetch), minter-g2a (`cd /`), executor-s2b (`cd /tmp` before any git write), minter-s2 (three bare `cd`, no git write after) and auditor-branches (`cd /home/puzhenhao1989`, read-only). Each reset with nothing written, so the safety valve is not met (no harm, nothing blocked). The rule they broke is `.claude/roles/executor.md` "Never `cd`" (amended 2026-10-05), whose reason is that the hook path in `.claude/settings.json` is relative; the briefs now carry the no-`cd` line as their first checklist item. Held for the phase review; the hook-path root cause is the row below. | the maintainer's entry "2026-10-08 16:04:19 BST — Status noted (39 open). The recurring cd slip becomes ONE process-backlog row (L3), not a role change" (three instances) and "2026-10-08 17:05:15 BST — BRANCH CLEANUP STEP 2: OK AS PROPOSED (Q: 79 → D2, 50 → P), with the pin-before-delete check" ("Slip #6 (cd) joins the backlog row"), both in `~/gi-pricing-plan.local/channel/to-lead.md`; instances 4 to 6 from the lead's entries in `~/gi-pricing-plan.local/channel/from-lead-2026-10-08.md` ("2026-10-08 14:37:29 BST", "2026-10-08 16:56:32 BST", "2026-10-08 17:02:45 BST" and its successors) and `~/gi-pricing-plan.local/handover/eta.md` (cd-slip PATTERN bullet) | lead (instances); row by minter-d1 |
| 2026-10-09 10:54:55 BST | **The `PreToolUse` retry-cap hook is registered by a path relative to the working directory, so a stray `cd` makes every Bash call refuse** (PL 9617, working id, WK-1178: "the PreToolUse hook runs by absolute path"; moved to the backlog under F-3). #1165's own words: "`.claude/settings.json:9` registers the retry-cap `PreToolUse` hook as `python3 scripts/hooks/retry_cap_hook.py hook`, a path relative to the working directory. After a `cd`, `python3` exits 2, which is the blocking exit for this hook, so every Bash call is refused." Its decided design is DP-1 (c) (`$CLAUDE_PROJECT_DIR` with a `git rev-parse --show-toplevel` fallback) and DP-2 (a), with Task 0 measuring the teammate, subagent and worktree behaviour; the plan stays on #1165's branch and is not minted. This is the root cause of the six-instance row above. #1165 closes naming this row. | #1165 @ `d862c5a611c5` (the plan PL 9617 and its slice row SL 9618, both working ids, `draft`); the maintainer's entry "2026-10-08 12:55:22 BST — P2 RE-PLAN RULED on the inventory (handover/p2-inventory-2026-10-09.md, at 60e9254c)", F-3 (b): "The three process items (PL 9617 hook path, FD 9755, FD 9772's check) become process-backlog rows under L3"; and the entry "2026-10-09 10:51:10 BST — USER: REDUCE OPEN PRs further …", item 4 | planner (PL 9617's author); row by minter-d1 |
