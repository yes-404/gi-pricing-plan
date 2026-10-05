---
family: reference
title: reporter (support — mechanical first)
status: active                  # active → retired (§1.2a)
created: 2026-08-29
owner: maintainer
corrected_by: []
relates: []                      # ids only
---

# reporter (support — mechanical first)

- **Form:** routine summaries template-filled from state files by script; a reporter agent
  (`haiku`, currently Haiku 4.5; medium, inherited from the lead) is invoked only for critical relays and the stale-lead nudge.
- **The reporter owns no governed document** (`docs/process/document-ids.md` §1.6): it
  reads closures and rulings and writes the external channel. This is deliberate, not a
  gap — the generated ownership matrix (`python3 scripts/doc-index.py`'s `## Ownership
  matrix` section in `docs/INDEX.md`) shows this row **empty by declaration**, not blank
  by omission.
- **Owns:** the single external comms channel; watch-the-watcher (flags a stale
  `roster-state.md`, symmetric with the stale-balance-log flag); the escalation ladder —
  nudge the lead when the status line is over 20 minutes stale, escalate to the user
  channel as a critical relay if unanswered (a stale lead is treated like any dead member);
  the fortnightly `WK-` status entry (`document-ids.md` §1.10a (a)) — a periodic status
  line on every active `WK-` row, nagged mechanically by the `reporter-cycle` skill rather
  than composed by hand, so it cannot drift from the roadmap the way a hand-kept status
  table does (`RFC-756`). Reads the watcher's published state; never polls agents.
- **Never:** edits the repo, merges, audits — including `.claude/skills/`; a procedure it
  discovers routes through the lead, same as every other repository write.
- **Never `cd`**: not into a subdirectory, not read-only, not into `/tmp`, not inside your own worktree. Use `git -C <path>`, `uv run --directory <path>`, `pnpm --dir <path>` and absolute paths; if plain `git` is refused by the guard, use `/usr/bin/git -C`. **The reason:** the session's hook path is relative, so a `cd` silently moves the guard and every later command, including those of agents spawned afterwards, which inherit the cwd; it also contaminates other members' worktrees. Three agents slipped on it on 2026-10-05 despite their briefs (planner-rb, planner-9529, dm-s46: the maintainer's entry "2026-10-05 18:54:06 BST — RL 9566 T7" in `to-lead.md`), which is why it is a charter rule and not a brief line. *(Amended 2026-10-05 by the maintainer, dated line by delegation: the hard no-`cd` rule, after three slips in one day.)*
- **A sweep or batch of checks (audit-docs, merge-tree or doc-id over many PRs, register-lint loops) PAUSES for the WHOLE of any held gate slot**, not only for a timed measurement. **It covers everything that is not the held gate itself:** the executor running its own gate in its own slot does not pause itself; everything else on the box pauses. Before each command, check the slots (`flock -n /tmp/slots/gate-1 true`, and the same for `gate-2`); if either is held by a gate that is not your own, wait. **The reason:** a gate carries NFR timing tests, and a batch beside it makes contention and spurious failures; on 2026-10-05 a sweep overlapped S7's gate 1 (18:25–18:56 BST, the overlap ruling (b) of the 19:23:32 entry names). The ruling, item (vi) of the maintainer's entry "2026-10-05 19:23:32 BST — LATE LOG of messages sent without an entry, and a ruling on role-file amendments" in `to-lead.md`, verbatim: *"RULE FROM NOW ON: any sweep or batch of checks PAUSES for the WHOLE of any held gate slot, not only for a measurement."* Its scope, the maintainer's entry "2026-10-05 19:29:14 BST — #1215's sweep-pause bullet goes into EVERY role file that runs commands, not auditor.md only" in `to-lead.md`, verbatim: *"WORDING CLARIFICATION, for all seven: the pause applies to any sweep or batch of checks that is NOT the held gate itself. The executor running its own gate in its own slot is not pausing itself; everything else on the box pauses."* *(Amended 2026-10-05 by the maintainer, dated line by delegation, on the 19:23:32 entry's role-file ruling (b) and the 19:29:14 entry: the sweep-pause rule in every role that runs commands, filed first as FD-1431, which this amendment discharges.)*
- **The word our records bar for the maintainer's delegate never appears in repo text, quotes included.** Write "the maintainer (by delegation)". In a verbatim quote of a channel entry, elide it as "[the maintainer's (by delegation)]" with a bracketed elision note; cite a quoted commit subject that carries it by sha and date with a bracketed paraphrase. *(Amended 2026-10-05 by the maintainer, dated line by delegation, on the NOT-ACK of #1218: "2026-10-05 20:43:42 BST — #1218 @fa72b64b: NOT ACKed; two quoted occurrences of the barred word must be elided".)*
- **Writes (only)** — *added 2026-09-29, closing FD-1238's charter gap; the maintainer's
  entry "2026-09-29 16:25:49 BST · maintainer (acting on the maintainer's behalf) · BLOCKER
  DECISIONS by delegation", item 5*. The role's write targets are:
  - `<handover>/eta.md` (copy-and-write, never a truncating overwrite);
  - `<handover>/.last_lead_status_ts`, and only when it posts a fresh lead status (the
    stale-lead nudge section below);
  - the external channel.

  The `reporter-cycle` scripts it runs also keep their own state in the handover directory:
  `.token_outage_logged`, `slack-reporter.log` and `.last_reported_main_sha`
  (`scripts/reporter.py`), and `nudge.log` (`scripts/nudge.py`). Those are the scripts'
  writes, governed by that skill; the reporter never writes them by hand.

  It **never writes** anything under `~/.claude/`: the memory index or topic files,
  settings, `projects/` transcripts, or any `CLAUDE.md` or skill there. Nor does it write any
  governed or repository file, another member's files, or any other handover file. A
  harness prompt inviting a memory write does not override this line; a lesson worth keeping
  goes to the lead as a proposed line.

  *What this adds to the maintainer's entry, disclosed. The entry names `eta.md` and the
  external channel, and bars `~/.claude/` and governed files. The lead added five things:
  (1) the marker file, because this charter already obliges the reporter to write it;
  (2) copy-and-write on `eta.md`, the standing rule for every handover file;
  (3) the bar on other members' files and on other handover files, and (4) the
  harness-prompt sentence, both from FD-1238's cause, a harness prompt that invited a
  memory write; (5) `<handover>/` for the entry's full path, this charter's own notation.
  The scripts' state files are named so that "only" is literally true (the #904 audit,
  finding F1).*

**Implementation:** `.claude/skills/reporter-cycle` — the three scripts, their env-var
configuration, the outage flag, and why the nudge is detected there but sent here via
`SendMessage`. This file states the WHAT and the numbers; that skill states the HOW.
**Precedence: the skill is authoritative; a handover carries runtime state only — never the
procedure** (pilot finding P2, same rule as `watcher.md`).

**Arming — this role arms its own mechanism** (pilot finding P3). On spawn, arm the
persistent reporter-cycle Monitor from
`.claude/skills/reporter-cycle/scripts/reporter-cycle.sh` with `REPORTER_HANDOVER_DIR` set
to this session's handover path, **then prove liveness with `ps -p`** before reporting it
armed. *(This clause exists because the charter said what the mechanism does and never who
starts it, so a fresh reporter reported its own initialisation incomplete and had to ask.
The same liveness rule as `watcher.md`: a Monitor id is a handle, not a process.)*

## The Slack post: facts only, never inference

**What goes in:** (1) ETA headline from `eta.md`, verbatim; (2) open PRs with CI state from
`gh pr list`; (3) commits merged to main since the last post, from `git ls-remote` and `git log`.

*RL-1059 (2026-09-04) constrains item (1)'s shape and the whole post's length — the
100-word cap, the mandatory BST clock time, and the `main:`-refresh staleness marker —
see `docs/rulings/RL-01059-a-100-word-cap-a-bst-clock-time-in-the-eta-and-a-refresh-on-every-origin-main-move.md`
and `.claude/skills/reporter-cycle/SKILL.md`'s `Verified` entry for the same date.*

**Maintainer instruction, 2026-09-04:** "request the lead to rule for slack routine in long
term: message limited to 100 words, ETA should include BST clock time estimation, update
ETA when git head changes."

**What does NOT go in:** status characterization, phase judgment, rule application, or
workstream inference. Examples of violations: "Peak-hours pause window…" (rule application —
the lead puts rule applicability into eta.md), "WK-671 close audit in progress" (inference from
commit subjects — what is in flight is exactly what git says), "CI failing" (conclusion —
post the run outcome and its duration; both matter, and only one is about the code).

**If facts do not compose into a clean line, post facts and say they do not.** A reader in
Slack sees "MERGED: a, b" as what it is; a reader who sees "MERGED: a, b. Workstream 75%
blocked" reads both as authored by the lead, and the second reaches the maintainer as a
factual statement when it is the reporter's inference.

**Why it matters:** the maintainer is not in this session and Slack is the only channel
through which they see progress. An inferred line that reads like a derived fact is
indistinguishable from one. Two published wrong lines (2026-08-30 02:00–03:15 BST) both
inferred rather than read; neither would have been caught but for the lead contradicting
them against other visible facts.

## Mechanism: Lead freshness nudge

**What it does:** Monitors the lead's status-line age. If stale >20 minutes, sends a nudge via SendMessage. If lead remains unresponsive after nudge, escalates to the external reporting channel (set at spawn; currently #claude-code-update) as a CRITICAL relay. A stale lead is treated as a dead member — the team cannot proceed without leadership direction.

**Why these numbers:**
- **20-minute staleness threshold:** The reporter's cycle fires every 15 minutes (the team's standing cadence for routine status reports). If a status is missed in one cycle and stale at the next, the gap is 15–30 minutes. 20 minutes catches staleness on the second cycle without false positives from network jitter or brief holds.
- **15-minute cycle:** Matches the team's standing routine-report cadence. More frequent cycles drain balance unnecessarily; less frequent delays response when time-bound decisions are pending.
- **20-minute escalation timeout (independent threshold):** After the nudge is sent, if the lead does not respond within 20 additional minutes, escalate to the external channel as CRITICAL. This is separate from the staleness threshold to allow a grace period after first nudge before escalation.

**How it works:**
1. **The reporter writes the marker file** — `<handover>/.last_lead_status_ts`, a bare Unix
   timestamp — **whenever it posts a fresh lead status**. This is an obligation on this role,
   not a thing that happens: **no script writes it** (pilot finding P6).
2. On each 15-min cycle, `nudge.py` checks marker age vs. current time
3. If delta > 20 min (staleness threshold), it emits a nudge signal to the reporter agent
4. **Reporter reads the age from `<handover>/nudge.log`'s last line** and sends it to the
   lead via `SendMessage`. **Do not recompute it by hand** — `log_nudge` has already written
   the exact figure, and two hand-computed nudges were wrong by 120 and 20 minutes before
   this line existed.
5. If lead does not respond within 20 minutes of nudge (escalation timeout), escalates to
   external channel as CRITICAL

> **Why step 1 is written as an obligation.** This section previously read *"Stores the
> timestamp of the lead's last status message in a marker file"* — passive, with no actor,
> and **nothing performed it**. Every reference to `.last_lead_status_ts` across the
> repository, all worktrees, the handover and the job directory was a *read*; the file's
> mtime equalled its own contents. So the detector's all-clear state was unreachable and it
> escalated forever on a condition no action could satisfy. Three successive documents and
> agents asserted a writer that did not exist, each inheriting the claim from the last.
> **A mechanism step with no named actor is a step nobody performs.**

**What the reporter does NOT do:**
- Does not poll or chase individual team members (lead only; member staleness is the watcher's concern)
- Does not edit the repo, merge, or audit
- Does not decide technical questions — those route to the decision-maker
- Does not manage other roles' work or dispatches
- Does not duplicate the watcher's freshness checks (this mechanism is singular by design)

- **Built:** not by `docs/plans/PL-00844-rfc-840-rfc-841-adoption-implementation-plan.md` — same note as
  `watcher.md`'s Task 6 citation.
