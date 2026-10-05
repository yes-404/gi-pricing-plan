---
id: FD-1431
family: finding
title: The role files had no hard no-cd rule and no sweep-pause rule for a held gate slot
status: active
created: 2026-10-05            # original date 2026-10-05, set at the draft; minted 2026-10-05
owner: auditor
tree: c3e7d6c7e2e3c293f64a045a0b931227c581a50a
corrected_by: []
relates: [WK-1178]
---

# FD-1431 — a role file proved insufficient twice in one day (`document-ids.md` §1.6, "Reference — charters")

**Filed** by auditor-rolefd on the lead's brief of 2026-10-05, working id 9490 (reserved in the lead's `eta.md`; minted as FD-1431), from
the maintainer's (by delegation) ruling (b) in `to-lead.md`, entry headed *"2026-10-05 19:23:32 BST — LATE LOG of
messages sent without an entry, and a ruling on role-file amendments"*. `tree:` is `origin/main` at filing
(`c3e7d6c7e2e3c293f64a045a0b931227c581a50a`); every fact below was re-read at it, or at the record named.
`to-lead.md` and the handover log are local files (`~/gi-pricing-plan.local/`), so each is cited by its header or its
line prefix.

## Finding

**Severity LOW, owner WK-1178** (the maintainer's ruling (b), quoted under Authority). `docs/process/document-ids.md`
:168 says of the charters (`.claude/roles/*.md`): *"maintainer; \"a role file that proves insufficient\" → `FD-` →
maintainer amends"*. Two rules a role file needed on 2026-10-05 were missing from it:

1. **No hard no-`cd` rule in any role file.** At `origin/main` `c3e7d6c7`,
   `git grep -n -w cd origin/main -- .claude/roles` prints nothing: 0 hits in all seven files. The rule lived in
   briefs only, and three agents used `cd` despite their briefs that day.
2. **No rule that a sweep or batch of checks pauses for a held gate slot.** `auditor.md` carries #1144's rule (the
   "never run a full test suite" bullet: before any run check `pgrep` and the gate slots, "run nothing heavy beside a
   held slot"). It says nothing about a *batch of individually light checks*, which together are heavy enough to
   matter.

## Evidence

### 1. The `cd` slips, from the records

| Agent | Where it is recorded | What the record says |
|---|---|---|
| planner-rb | handover log `mint-queue-2026-10-05.md`, entry "2026-10-05 17:50:50 BST" | "planner-rb used cd in the root (checked: clean, main 5fe56b87)" |
| planner-9529 | same log, entry "2026-10-05 18:04:18 BST"; `to-lead.md`, entry "2026-10-05 18:04:32 BST — PL 9514 …": "planner-9529's cd into its own worktree: noted; stopping it is fine." | "planner-9529 (cd in its own wt) stopping" |
| dm-s46 | `to-lead.md`, entry "2026-10-05 18:54:06 BST — RL 9566 T7 …", PROCESS paragraph | "dm-s46's cd /tmp is the THIRD cd slip today (planner-rb, planner-9529, dm-s46), so briefs alone are not holding." |

`to-lead.md` also has, in the entry headed "2026-10-05 18:01:45 BST — Trace mismatch …", the line "The cd /tmp: noted. Root
clean." It does not name the agent, and it predates dm-s46's slip in the 18:54:06 entry's sequence only by inference, so
it is **not counted** as a fourth slip or attributed to anyone.

**Not found.** The brief for this finding also names planner-1343, dm-fr240c and planner-rb2 as later self-reports.
A search of the handover log (`grep -n -i -E 'used cd|cd slip|cd into|\bcd\b'`) and of `to-lead.md` after line 18000
finds no record of a `cd` by those three. They are **not counted here**; three is the maintainer's number and the one
the records support.

The harm, in the maintainer's words (same entry): *"the hook path is relative, and a cd contaminates later spawns."*
`to-lead.md` records that "today's slips touched nothing"; the harm is prevented, not suffered.

### 2. The overlap

The handover log records the sweep's condition and the conflict. Entry "2026-10-05 18:43:56 BST": auditor-mintready
(sonnet) spawned for a read-only mint-readiness sweep over the queue; entry "18:44:46 BST": "The deputy's condition:
auditor-mintready sequential + nice, PAUSED during S7's measurement … overlap → re-run." Entry "18:58:23 BST": S7 gate 1
at `c1f2ef17` ran and its measurement was INVALID (load 7.2). The brief gives the sweep as 55 PRs, `audit-docs` plus
`merge-tree` per PR, un-niced, overlapping S7's gate 1 from 18:25 to 18:56 BST. **The log does not state the 55, the
"un-niced" or the 18:25–18:56 window in those words**; they rest on the lead's brief and on the maintainer's
"overlap disclosure" (entry of 19:23:32 BST, item (vi)), which accepts it without restating the figures. The finding
does not depend on them: the maintainer ruled that the rule was missing.

### 3. #1144 and #1154 skipped the FD step

`git log -1 --format='%h %aI %s'` at this tree:

- `809a3794` 2026-10-05T14:54:04+01:00 `docs(roles): planner, decision-maker, auditor and watcher never run a full
  suite or anything heavy beside a held gate slot (#1144)`.
- `a5e6781f` 2026-10-05T14:51:50+01:00 `docs(roles): post-mint working-id sweep in lead.md; "by the deputy" →
  maintainer (by delegation) in executor.md (#1154)`.

Both amended role files and neither has an `FD-`. They are **not retro-filed** (ruling (b)). They are named because the
gap was found by that comparison.

## Authority

Quoted verbatim from `to-lead.md`, entry headed *"2026-10-05 19:23:32 BST — LATE LOG of messages sent without an entry,
and a ruling on role-file amendments"*:

> ROLE-FILE AMENDMENTS, ruled:
> (a) A role-file amendment is the MAINTAINER'S. It may be DRAFTED BY DELEGATION by any agent on the lead's instruction, for my MERGE-ACK, with a logged entry of mine as the authority. That is how #1144, #1154 and #1215 worked; it is now stated.
> (b) document-ids.md :168 (Reference, charters: "a role file that proves insufficient" → FD- → maintainer amends) DOES require the FD step, and it is the authority, so it is followed. ONE FD covers both #1215 rules: the no-cd rule (three slips today: planner-rb, planner-9529, dm-s46) and the sweep-pause rule (the 18:25–18:56 overlap). It is filed by an auditor FIRST, LOW, owner WK-1178, discharged by #1215. #1215 cites it. #1144 and #1154 are NOT retro-filed; the FD's text notes that they skipped the step, which is how the gap was found.

The sweep-pause rule, item (vi) of the same entry:

> (vi) Sent between 19:05:50 and this entry, the SWEEP RULE: the sweep result and its checklist file are noted. #1145's FD 9888 [hyphen in the original, written with a space here: check 32 resolves hyphenated ids only and this one is an unminted working id] → FD-1317 is an INFERENCE: verify it in INDEX and in FD-1317's own title before the re-point; if it does not match, STOP. The overlap disclosure is accepted: gate 1's result stands because contention can only cause spurious failures, not a false pass, and every gate-1 failure is explained; it is superseded by the re-gate anyway. RULE FROM NOW ON: any sweep or batch of checks PAUSES for the WHOLE of any held gate slot, not only for a measurement.

The no-`cd` order, from the entry headed *"2026-10-05 18:54:06 BST — RL 9566 T7 (#1191 @bb70663b): case (a) accepted; T7's three choices ACCEPTED; the recurring cd: fix the role files"*, PROCESS paragraph:

> PROCESS: dm-s46's cd /tmp is the THIRD cd slip today (planner-rb, planner-9529, dm-s46), so briefs alone are not holding. Under CLAUDE.md 15 a role file that proves insufficient is a finding against the FILE: add the hard no-cd rule (with the reason: the hook path is relative, and a cd contaminates later spawns) to every .claude/roles/*.md that runs commands, as ONE small PR for my ACK when a seat frees. Not urgent; today's slips touched nothing.

## Disposition

**Carry forward with an owner: WK-1178.** Discharged by #1215 (branch `roles-no-cd`, head
`b8c2e6f864d11fca790de5f2b71d60409a77bc6e` when this was filed), which adds the no-`cd` bullet to all seven role files
and the sweep-pause bullet to `auditor.md`, drafted by delegation for the maintainer's merge-ACK (ruling (a)). #1215
cites this finding. The amendment is the maintainer's; this finding does not make it. When #1215 merges, the auditor sets
this row `closed` in place citing the PR (`document-ids.md` §1.6, FD row).
