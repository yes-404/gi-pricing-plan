# watcher (support — mechanical first)

- **Form:** a script (no LLM in steady state) plus event hooks; a watcher agent (Haiku 4.5,
  low effort) spawns only when an anomaly needs judgment or a written signal.
- **Owns (script):** balance thresholds and re-arming one-shot triggers on confirmed
  recovery, roster/staleness watch, hygiene checks, publishing `roster-state.md` each cycle
  as the single source of team state, and a rolling mechanical ETA from per-slice durations.
- **Owns (agent):** judgment on ambiguous anomalies and the written signal to the lead.
- **Never:** dispatches stand-ins, touches the repo.
- **Built:** not by this plan — see `docs/process/delivery-process.md` §13 for the
  mechanism this file describes, and this plan's Task 6 for why the script itself is
  deliberately deferred.
