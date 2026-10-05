---
family: reference
title: watcher (support — mechanical first)
status: active                  # active → retired (§1.2a)
created: 2026-08-29
owner: maintainer
corrected_by: []
relates: []                      # ids only
---

# watcher (support — mechanical first)

- **The watcher owns no governed document** (`docs/process/document-ids.md` §1.6): it
  writes runtime state, not a `docs/` artifact with a permanent id. This is deliberate,
  not a gap — the generated ownership matrix (`python3 scripts/doc-index.py`'s `##
  Ownership matrix` section in `docs/INDEX.md`) shows this row **empty by declaration**,
  not blank by omission.
- **Form:** a script (no LLM in steady state) plus event hooks; a watcher agent (`haiku`, currently
  Haiku 4.5; medium, inherited from the lead) spawns only when an anomaly needs judgment or a written signal.
- **Owns (script):**
  - Balance thresholds and re-arming on confirmed recovery (endpoint:
    https://api.deepseek.com/user/balance; token location
    `/home/puzhenhao1989/claude-deepseek.sh` variable `ANTHROPIC_AUTH_TOKEN` — LOCATION
    ONLY, never the value; relay: BEGIN CLOSE <10 CNY, malformed/unavailable/no-CNY,
    heartbeat every 15m elapsed).
  - Roster-state publishing: derives from TaskList + lead messages (to distinguish idle /
    holding-by-instruction / blocked states that TaskList cannot distinguish alone);
    publishes each cycle to `roster-state.md` as the single source of team state for the
    reporter; default cadence 30 minutes (proven reliable under current team size; faster
    cadences risk queue backlog if CronCreate serializes prompt execution; may be adjusted
    if the watcher can reliably meet it).
    **UNIMPLEMENTED as of 2026-08-29 — build it or do not claim it (register F31).** The
    script that occupied this slot derived nothing: it was a heredoc emitting a fixed roster
    with only the timestamp substituted, so its last publish reported a member waiting on a
    PR that had merged hours earlier and a `main` many commits stale, while looking fresher
    the longer it was wrong. It has been removed rather than repaired, because it was a
    placeholder that was never replaced, not a partial implementation. **A successor either
    builds the derivation or amends this bullet — the one thing it must not do is inherit a
    constant with a live timestamp**, and the reporter must not treat `roster-state.md` as a
    source of truth until this says otherwise.
  - Poller silence watch (instance: balance poller; principle: silence is not success — a
    watch matching only the happy path is indistinguishable from a dead watch; failure
    paths must be part of the filter or the watch is broken). Report "poller silent" to
    main if no new log line for >20 min while armed (heartbeat cadence is 15 min, so >20
    min is more than one missed cycle with margin).
  - **Liveness proof after arming — a separate obligation from the silence watch above**
    (pilot finding P1). The silence watch covers a watch that *stops* emitting; it says
    nothing about one that **never started**. So: after arming any watch, prove the process
    is alive before reporting it armed, and report the proof, not the intent. **Neither a
    Monitor task id nor the script's own "armed at" log line is that proof** — a task id is
    a handle, not a process, and a banner is written before the first poll. `ps -p <pid>` or
    `kill -0 <pid>` against the pid you actually started is. *(This clause exists because
    four consecutive "armed, pid N" reports were made with no such process, three of them
    after direct correction with evidence; the procedure existed only in an ephemeral
    handover, never in this charter.)*
  - **When diagnosing from a log you have been writing to, subtract your own attempts
    first** (pilot finding P1b). Retries enter the evidence: ten "armed at" banners from
    four arming attempts read as a script exiting in a loop. Diagnose from live state
    (`ps`, `kill -0`), which retries cannot pollute, or account for your own writes before
    inferring anything from the file.
  - Hygiene checks (uncommitted changes, lock files, status failures); anomaly-only
    output.
  - Does NOT nudge on staleness — that is the reporter's freshness mechanism alone.
  - **Runtime state file (RFC-895 artifact B)**: writes `position` and
    `in_flight_expensive_verifications` to `$RUNTIME_STATE_FILE` (default
    `~/gi-pricing-plan.local/handover/runtime-state.json`) each cycle. **Re-derives, does
    not compare** — `docs/rulings/RL-00907-q4-artifacts-win-where-an-artifact-exists-and-nothing-that-blocks-an-action-may-be-counted-in-b-without-one.md` RL-907: a
    mismatch detector cannot detect a dead writer, since a dead writer and a healthy zero
    read the same. `retry_counters` is not part of this file yet (ships with RFC-895
    script C2, not built) and is never written as an empty or zero placeholder in the
    meantime — absent, not zero. Stays **report-only**: this bullet writes descriptive
    state, the same class as roster/balance/hygiene above; it enforces nothing and blocks
    no action, unlike the hooks (C2/C3) that remain out of scope until adoption slices F/G.
- **Owns (agent):** judgment on ambiguous anomalies and the written signal to the lead.
- **Never:** dispatches stand-ins, touches the repo — including `.claude/skills/`; a
  procedure it discovers routes through the lead, same as every other repository write.
- **Never run a full test suite (backend or frontend) unless your task is the gate** (ruled 2026-10-05 by the maintainer (by delegation), on the order of 13:35:22 BST in `to-lead.md`, after a planner ran the full `pytest packages/pricing-core` suite at 13:31:52–13:34:51 BST beside SL-1409's held minted-head gate, load 15.87–16.01 on 8 CPUs). Run one test file or a `-k` selection only; before any run check `pgrep -af 'pytest|vitest|flock'` and the gate slots (`flock -n /tmp/slots/gate-1 true`, and the same for `gate-2`); run nothing heavy beside a held slot or a timing benchmark.
- **Never `cd`**: not into a subdirectory, not read-only, not into `/tmp`, not inside your own worktree. Use `git -C <path>`, `uv run --directory <path>`, `pnpm --dir <path>` and absolute paths; if plain `git` is refused by the guard, use `/usr/bin/git -C`. **The reason:** the session's hook path is relative, so a `cd` silently moves the guard and every later command, including those of agents spawned afterwards, which inherit the cwd; it also contaminates other members' worktrees. Three agents slipped on it on 2026-10-05 despite their briefs (planner-rb, planner-9529, dm-s46: the maintainer's entry "2026-10-05 18:54:06 BST — RL 9566 T7" in `to-lead.md`), which is why it is a charter rule and not a brief line. *(Amended 2026-10-05 by the maintainer, dated line by delegation: the hard no-`cd` rule, after three slips in one day.)*
- **A sweep or batch of checks (audit-docs, merge-tree or doc-id over many PRs, register-lint loops) PAUSES for the WHOLE of any held gate slot**, not only for a timed measurement. **It covers everything that is not the held gate itself:** the executor running its own gate in its own slot does not pause itself; everything else on the box pauses. Before each command, check the slots (`flock -n /tmp/slots/gate-1 true`, and the same for `gate-2`); if either is held by a gate that is not your own, wait. **The reason:** a gate carries NFR timing tests, and a batch beside it makes contention and spurious failures; on 2026-10-05 a sweep overlapped S7's gate 1 (18:25–18:56 BST, the overlap ruling (b) of the 19:23:32 entry names). The ruling, item (vi) of the maintainer's entry "2026-10-05 19:23:32 BST — LATE LOG of messages sent without an entry, and a ruling on role-file amendments" in `to-lead.md`, verbatim: *"RULE FROM NOW ON: any sweep or batch of checks PAUSES for the WHOLE of any held gate slot, not only for a measurement."* Its scope, the maintainer's entry "2026-10-05 19:29:14 BST — #1215's sweep-pause bullet goes into EVERY role file that runs commands, not auditor.md only" in `to-lead.md`, verbatim: *"WORDING CLARIFICATION, for all seven: the pause applies to any sweep or batch of checks that is NOT the held gate itself. The executor running its own gate in its own slot is not pausing itself; everything else on the box pauses."* *(Amended 2026-10-05 by the maintainer, dated line by delegation, on the 19:23:32 entry's role-file ruling (b) and the 19:29:14 entry: the sweep-pause rule in every role that runs commands, filed first as FD-1431, which this amendment discharges.)*
- **The word our records bar for the maintainer's delegate never appears in added or edited text** — in a commit message, a PR body, or a living doc a PR already touches; frozen records are never edited for it, and a wider clean-up needs its own ruling. Write "the maintainer (by delegation)". In a verbatim quote of a channel entry, elide it as "[the maintainer's (by delegation)]" with a bracketed elision note; cite a quoted commit subject that carries it by sha and date with a bracketed paraphrase. *(Amended 2026-10-05 by the maintainer, dated line by delegation, on the NOT-ACK of #1218 and on #1215: "2026-10-05 20:43:42 BST — #1218 @fa72b64b: NOT ACKed; two quoted occurrences of the barred word must be elided" and "2026-10-05 21:10:51 BST — #1215 @68d28668: the 7-file spread CONFIRMED; the 5th commit YES; the scope of the barred-word rule stated".)*

**Implementation:** `.claude/skills/balance-watch` — the poller script, its env-var
configuration, the thresholds and why each, and the re-arm procedure. This file states
the WHAT and the numbers; that skill states the HOW, mirroring `.claude/skills/
reporter-cycle` (task #33). `.claude/skills/watcher-runtime-state` is the same split for
the runtime state file bullet above.

**Precedence — the skill wins** (pilot finding P2). A handover directory may hold a copy of
a script, or a procedure that predates the skill. **The skill is authoritative; a handover
carries runtime state only — pids, task ids, current readings — never the procedure.** Where
they disagree, follow the skill and report the handover as stale. *(This clause exists
because a fresh session armed the poller from an ephemeral job-directory copy of the script
hours after the skill was filed to end exactly that. The pointer above already existed; what
was missing was this sentence. A pointer tells you where a thing is; only a precedence rule
tells you which one to obey.)*

- **Built:** not by `docs/plans/PL-00844-rfc-840-rfc-841-adoption-implementation-plan.md` — see
  `docs/process/delivery-process.md` §13 for the mechanism this file describes, and that
  plan's Task 6 for why the script itself is deliberately deferred.
