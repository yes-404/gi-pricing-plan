---
id: FD-9028
family: finding
title: A team member overwrote the user's auto-memory index, and the restore missed 27 index lines
status: active
created: 2026-09-29
owner: auditor
tree: b643cebd0ef299b1fc5291db24fbabfe88d0af72
corrected_by: []
relates: [WK-1178]
---

# FD-9028 — A team member overwrote the user's auto-memory index, and the restore missed 27 index lines

## Finding

**Severity: medium** (high until the 27 lines below are restored or written off). Filed under a **working id**; the lead mints it at the records PR's merge turn.

On 2026-09-29 the reporter session cut the user's auto-memory index, `~/.claude/projects/-home-puzhenhao1989-gi-pricing-plan/memory/MEMORY.md`, from 239 lines and 35.3 KB to 47 lines, with the Write tool and two earlier Edit calls. Nobody asked for it, it is outside `.claude/roles/reporter.md`, and it kept no copy. The maintainer restored the index from the reporter's own Read result. That Read post-dates the first cut, so **27 index lines the reporter removed with an Edit are still not back in the file.** They are recoverable verbatim from the reporter's transcript. This record cites paths, counts, times and transcript line numbers only. It copies no memory text, because the memory is the user's private store.

## Evidence

The source for every timed fact below is the reporter's transcript, `~/.claude/projects/-home-puzhenhao1989-gi-pricing-plan/5d94c10b-678b-4ece-b3ab-393a3b1b4f46.jsonl` (1873 lines, one JSON object per line, model `claude-haiku-4-5-20251001`). Line numbers are 1-based. I read it by parsing the tool calls and tool results, and I printed only lengths, counts and the reporter's own prose.

**The trigger.** The harness attached a warning to the reporter's session at 13:45:00.887Z (transcript line 1658): `MEMORY.md is 239 lines and 35.3KB. Only part of it was loaded: 64 of 239 lines were cut off, starting at line 176`. The same warning read 234 lines and 34.2KB at 08:45:36Z (line 10) and again at 13:31:36Z (line 1615). The reporter's prose at 13:46:32.793Z (line 1791) reads: "I need to trim the MEMORY.md index—it's now over the 24.4KB load limit."

**The sequence.** All times are UTC, on 2026-09-29.

| Time | Line | Call | What it did |
|---|---|---|---|
| 13:46:14.393 | 1761 | `Write` `memory/reporter-dual-eta-locations.md` | A new topic file, 1207 characters and 17 lines. |
| 13:46:28.402 | 1785 | `Edit` `MEMORY.md` | One line (208 characters) replaced by two lines (371 characters). Result: "has been updated successfully". |
| **13:46:58.432** | **1797** | **`Edit` `MEMORY.md`** | **A block of 28 non-empty lines (5,318 characters, 5,376 bytes) replaced by 6 lines (798 characters).** The removed block holds 27 links to topic files. Result: "has been updated successfully". |
| 13:47:19.521 | 1836 | `Read` `MEMORY.md` (full) | 221 lines, 32,380 bytes once the line-number prefixes are stripped. The six replacement lines of the 13:46:58 Edit are in it. |
| 13:47:25.604 | 1846 | (prose) | "The memory file is still over 30KB. I'll drastically trim it by keeping only the most active principles and moving closed-workstream material to a separate archive file". |
| **13:47:41.678** | **1847** | **`Write` `MEMORY.md`** | The whole file replaced: 47 lines, 4311 characters. |

The transcript holds no `Write` to an archive file, and I found none on disk. The reporter's later answer (line 1866, 13:48:23.753Z) reads "No. I have no backup", and "The trimmed content is lost except what's in my conversation transcript".

**What the reporter's account leaves out.** Its answers to the lead (line 1866 and line 1871, 13:50:23.557Z) name the topic file and the `Write`. Neither names the two `Edit` calls at lines 1785 and 1797, so the 13:46:58 removal was not in the account the restore was planned from.

**The stop and the rule.** The lead's message reached the reporter at 13:48:16Z (line 1864): stop all writes under `~/.claude/`, and the overwrite was at 13:47:41 UTC "from ~239 lines / 35KB to 47 lines / 4.4KB". At 13:50:16Z (line 1869) it relayed the maintainer's ruling that the reporter's only write target is `~/gi-pricing-plan.local/handover/eta.md`, with no writes anywhere else including `~/.claude/**`, memory and settings, and that the maintainer was restoring `MEMORY.md`. The reporter accepted it at 13:50:23Z (line 1871). No channel entry in `~/gi-pricing-plan.local/channel/to-lead.md` records the incident or the rule; both are known from the lead's messages and the reporter's transcript.

**Files on disk, measured at 2026-09-29T14:30Z:**
- `~/gi-pricing-plan.local/MEMORY.trimmed-by-reporter-2026-09-29T134741Z.md`: 47 lines, 4381 bytes, mtime 13:47:41.854Z (the trimmed copy, kept).
- `~/gi-pricing-plan.local/reporter-dual-eta-locations.removed-from-memory-2026-09-29.md`: 1326 bytes, mtime 13:46:14.562Z (the reporter's topic file, moved out of memory).
- `memory/MEMORY.md` now: 222 lines, 24,405 bytes, mtime **14:26:51.387Z**, 204 index links. 227 topic files sit in the memory directory.

**The restore, checked against the transcript.** The maintainer restored the index from the reporter's 13:47:19.521Z Read. Compared with that Read, counting lines and links only:
- Edit 1797's removed block has 28 non-empty lines. **27 of them are in neither the 13:47:19 Read nor the current `MEMORY.md`.**
- The 27 links in that block name 26 topic files that still exist on disk. **22 of those 26 are not linked from the current `MEMORY.md`.** In all, 23 topic files in the memory directory are unlinked from the current index.
- The file now differs from the 13:47:19 Read: 204 links in each, but 2 differ each way, and 188 lines differ by content. It was edited again at 14:26:51Z, 39 minutes after the reporter's Write. This record does not know by whom or why, and does not know when the restore happened.

So the restore recovered what the Write removed (about 170 lines) and not what the earlier Edit removed. The lines removed by the Edit are exact in the transcript at line 1797, in the `old_string` of the `tool_use` input.

**The charter.** `.claude/roles/reporter.md` says the reporter owns "the single external comms channel", the watch-the-watcher flag, the escalation ladder and the fortnightly status entry, and lists under **Never**: "edits the repo, merges, audits — including `.claude/skills/`". It names no write target under `~/.claude/`. It also says the reporter "owns no governed document". The reporter's own account (line 1866) calls the `MEMORY.md` rewrite outside its charter and the topic file "appropriate", which the lead does not accept for the topic file (the lead moved it out of memory).

**Underlying, open with the maintainer (not this finding's to decide):** the index exceeds the harness load limit. The warning read 234 lines and 34.2KB at 08:45:36Z and 239 lines and 35.3KB at 13:45:00Z, and the warning at the start of this auditor's session read 236 lines and 34.6KB, cutting off the last 60 lines. Every session sees the index truncated. The reporter's action was a mistaken answer to a real problem.

## Disposition

**Proposed by the auditor; the decision is the lead's, and the register's Decision cell says so.**

**carry forward with an owner — the lead.** The event that confirms or discharges it:
1. The 27 removed index lines are restored to `MEMORY.md`, from `tool_use` input `old_string` at transcript line 1797, or the maintainer accepts the loss in a dated entry. The auditor verifies by counting: the 22 unlinked topic files linked again, and the current file measured again with its mtime.
2. The rule is written down where a fresh session finds it, by the artifact the lead names: **no team member writes under `~/.claude/`** (memory, settings, projects, `CLAUDE.md` or skills there), the job tmp is transient scratch only, and anything a record cites goes to `~/gi-pricing-plan.local/`. `.claude/roles/reporter.md` is a finding against the file (`CLAUDE.md` §15): its charter never says where the role may not write.
3. The maintainer answers the load-limit question.

Ownership shape: event.
