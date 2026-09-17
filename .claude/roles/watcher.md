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

- **Form:** a script (no LLM in steady state) plus event hooks; a watcher agent (Haiku 4.5,
  low effort) spawns only when an anomaly needs judgment or a written signal.
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
