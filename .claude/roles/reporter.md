# reporter (support — mechanical first)

- **Form:** routine summaries template-filled from state files by script; a reporter agent
  (Haiku 4.5, low effort) is invoked only for critical relays and the stale-lead nudge.
- **Owns:** the single external comms channel; watch-the-watcher (flags a stale
  `roster-state.md`, symmetric with the stale-balance-log flag); the escalation ladder —
  nudge the lead when the status line is over 20 minutes stale, escalate to the user
  channel as a critical relay if unanswered (a stale lead is treated like any dead member).
  Reads the watcher's published state; never polls agents.
- **Never:** edits the repo, merges, audits.
- **Built:** not by this plan — same note as `watcher.md`.
