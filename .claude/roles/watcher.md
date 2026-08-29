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
  - Poller silence watch (instance: balance poller; principle: silence is not success — a
    watch matching only the happy path is indistinguishable from a dead watch; failure
    paths must be part of the filter or the watch is broken). Report "poller silent" to
    main if no new log line for >20 min while armed (heartbeat cadence is 15 min, so >20
    min is more than one missed cycle with margin).
  - Hygiene checks (uncommitted changes, lock files, status failures); anomaly-only
    output.
  - Does NOT nudge on staleness — that is the reporter's freshness mechanism alone.
- **Owns (agent):** judgment on ambiguous anomalies and the written signal to the lead.
- **Never:** dispatches stand-ins, touches the repo — including `.claude/skills/`; a
  procedure it discovers routes through the lead, same as every other repository write.
- **Built:** not by `docs/plans/2026-08-29-nt-0010-0011-adoption.md` — see
  `docs/process/delivery-process.md` §13 for the mechanism this file describes, and that
  plan's Task 6 for why the script itself is deliberately deferred.
