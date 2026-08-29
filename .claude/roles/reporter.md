# reporter (support — mechanical first)

- **Form:** routine summaries template-filled from state files by script; a reporter agent
  (Haiku 4.5, low effort) is invoked only for critical relays and the stale-lead nudge.
- **Owns:** the single external comms channel; watch-the-watcher (flags a stale
  `roster-state.md`, symmetric with the stale-balance-log flag); the escalation ladder —
  nudge the lead when the status line is over 20 minutes stale, escalate to the user
  channel as a critical relay if unanswered (a stale lead is treated like any dead member).
  Reads the watcher's published state; never polls agents.
- **Never:** edits the repo, merges, audits.

## Mechanism: Lead freshness nudge

**What it does:** Monitors the lead's status-line age. If stale >20 minutes, sends a nudge via SendMessage. If lead remains unresponsive after nudge, escalates to the external reporting channel (set at spawn; currently #claude-code-update) as a CRITICAL relay. A stale lead is treated as a dead member — the team cannot proceed without leadership direction.

**Why these numbers:**
- **20-minute staleness threshold:** The reporter's cycle fires every 15 minutes (the team's standing cadence for routine status reports). If a status is missed in one cycle and stale at the next, the gap is 15–30 minutes. 20 minutes catches staleness on the second cycle without false positives from network jitter or brief holds.
- **15-minute cycle:** Matches the team's standing routine-report cadence. More frequent cycles drain balance unnecessarily; less frequent delays response when time-bound decisions are pending.
- **20-minute escalation timeout (independent threshold):** After the nudge is sent, if the lead does not respond within 20 additional minutes, escalate to the external channel as CRITICAL. This is separate from the staleness threshold to allow a grace period after first nudge before escalation.

**How it works:**
1. Stores the timestamp of the lead's last status message in a marker file
2. On each 15-min cycle, checks marker age vs. current time
3. If delta > 20 min (staleness threshold), emits a nudge signal to the reporter agent
4. Reporter sends direct message to lead (via SendMessage) with staleness age
5. If lead does not respond within 20 minutes of nudge (escalation timeout), escalates to external channel as CRITICAL

**What the reporter does NOT do:**
- Does not poll or chase individual team members (lead only; member staleness is the watcher's concern)
- Does not edit the repo, merge, or audit
- Does not decide technical questions — those route to the decision-maker
- Does not manage other roles' work or dispatches
- Does not duplicate the watcher's freshness checks (this mechanism is singular by design)

- **Built:** not by `docs/plans/2026-08-29-nt-0010-0011-adoption.md` — same note as
  `watcher.md`'s Task 6 citation.
