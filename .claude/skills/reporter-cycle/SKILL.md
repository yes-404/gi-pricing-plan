---
name: reporter-cycle
description: Run the team's 15-minute Slack status cycle and lead-staleness nudge detection — the outage flag that stops a token failure from spamming the log, the durable-token-path requirement, the quarter-mark cycle timing, and why the nudge signal is detected here but sent by the agent, never the script. Use when standing up a new session's reporter, when a Slack post stops appearing, or when configuring REPORTER_HANDOVER_DIR for a fresh handover.
---

# Reporter cycle: routine Slack posting and lead-staleness detection

Three scripts, ~250 lines, stdlib-only Python plus one bash loop: `reporter.py` posts a
routine status update to Slack every 15 minutes; `nudge.py` detects a stale lead status
line; `reporter-cycle.sh` is the loop that calls both on schedule. Filed here per
`docs/plans/2026-08-29-w11-prework-rulings.md`'s reporter-scripts ruling (task #28) —
`CLAUDE.md` §12 names `.claude/skills/` as the home for a discovered non-obvious procedure,
and these three scripts' mechanism (below) is exactly that.

## Why this is a skill and not a role-file paragraph

The mechanism is small, complete, and already tested — reconstructing it from prose each
time a reporter is stood up is a testing burden, not a learning opportunity, and concrete
code surfaces edge cases prose reliably loses (the outage flag, below, is invisible from
either script's signature). `.claude/roles/reporter.md` keeps the WHAT (nudge threshold,
escalation rule, what the reporter does not do); this skill keeps the HOW.

## Configuration — everything is an environment variable, nothing is hardcoded

The version of these scripts that ran in the W11 handover directory hardcoded that
directory's literal path. That is exactly the mistake
[`NT-0012`](../../notes/0012-a-credential-is-borrowed-not-stored.md) names: operational,
session-specific state living inside checked-in, supposedly-reusable code. Refiled with
every path read from the environment instead:

| Variable | Required | Default | Read by |
|---|---|---|---|
| `REPORTER_HANDOVER_DIR` | **Yes** | none — exits 2 if unset | both scripts |
| `REPORTER_TOKEN_PATH` | No | `~/.slack-token` | `reporter.py` |
| `REPORTER_REPO_DIR` | No | current working directory | `reporter.py` (for `gh pr list`) |
| `REPORTER_SLACK_CHANNEL` | No | `C0BSYRQ6NGM` (`#claude-code-update`) | `reporter.py` |
| `REPORTER_STALE_SECONDS` | No | `1200` (20 minutes) | `nudge.py` |

**A missing `REPORTER_HANDOVER_DIR` fails loudly (exit 2, a message to stderr), by
design.** This is the one failure mode that must not be silent: every other failure path in
these scripts (a missing token, a `gh` timeout, a Slack API error) is an expected,
recoverable operational condition and is handled by logging and continuing: a
misconfigured handover directory is not, and a script that guessed a default here would
silently write its whole state into the wrong place, or into the working directory of
whatever happened to invoke it.

**Launch, per session:**
```bash
export REPORTER_HANDOVER_DIR=/home/<user>/<workstream>-handover-<date>
export REPORTER_TOKEN_PATH=/home/<user>/.slack-token   # only if not the default
bash .claude/skills/reporter-cycle/scripts/reporter-cycle.sh
```

## Procedural knowledge — not visible from the scripts' signatures

1. **The outage flag prevents a multi-hour token failure from writing an identical log line
   every 15 minutes.** `reporter.py`'s `get_token()` writes `TOKEN OUTAGE START` to the log
   exactly once, then creates `.token_outage_logged` in the handover directory; every
   subsequent call with the token still missing exits silently. Deleting that flag file is
   how a fixed token starts posting again — see "Recovering from a token outage" below.
2. **The token is read from disk on every single call, never cached.** This is what lets a
   token rotation take effect at the next 15-minute cycle with no restart: write the new
   value to `REPORTER_TOKEN_PATH` and the very next scheduled call picks it up.
3. **`reporter-cycle.sh` sleeps to the next exact quarter-hour mark, not for a fixed 900
   seconds.** `next = (now / 900 + 1) * 900; sleep(next - now)` — a fixed-interval sleep
   drifts by however long each cycle's own work takes; sleeping to the mark keeps posts
   landing at `:00/:15/:30/:45` UTC indefinitely.
4. **The staleness marker is a bare Unix timestamp, one line, nothing else.** `nudge.py`
   reads it with a plain `float()`; any other format is a parse failure treated the same as
   "no status seen yet" (returns `None`, never raises) — a stricter parser would turn a
   corrupted marker into a crash instead of a missed nudge, and a missed nudge is the safer
   failure here.
5. **`reporter.py` exits 0 on a token outage, not a non-zero code.** The calling loop must
   keep running through an outage — treating a missing token as a fatal script error would
   stop the entire 15-minute cycle, including the parts of it (staleness detection) that do
   not depend on Slack at all.

## The nudge signal is detected here; sending it is the agent's job, not the script's

`nudge.py` only ever prints `NUDGE_NEEDED` or `OK` and returns 0. `.claude/roles/
reporter.md`'s "Mechanism" section specifies the nudge itself as a `SendMessage` call — a
tool a standalone Python process does not have. `reporter-cycle.sh` echoes `NUDGE_SIGNAL
<timestamp>` to stdout for exactly this reason: whatever process is running the cycle
(a `Monitor`-tracked background task, watched by the reporter agent) sees that line and is
the one that actually calls `SendMessage`. Do not add a `SendMessage`-shaped call into
`nudge.py` itself — it would not run, since the script has no such tool, and it would
misdescribe where the real send happens to the next person reading it.

## Deliberately not carried forward from the handover copy

The handover version's `format_routine_post` took `roster_text` and `lead_status`
parameters that its own body never read, and printed two hardcoded lines — a `*WORK:*`
status and a `*BLOCKED ON:*` line — naming that specific session's own state ("Adoption
procedure active (step 2a/2b)", "Maintainer rulings (2) + decisions (3)"). Both were dead
placeholder text, not live logic: the message never actually reflected the arguments passed
in. Shipping that into a checked-in, reusable skill would be exactly the mistake this
filing exists to fix — a hardcoded status frozen at whatever it last said. Dropped, along
with an unused `mention_user` flag on the Slack post (the real nudge path is the
`SendMessage` mechanism above, not a Slack `@mention`). The routine post today carries
balance and open-PR count only; wiring in a real roster summary is future work, not
regression — nothing here ever actually surfaced roster content either.

## Recovering from a token outage

1. Obtain the new token from the maintainer.
2. Write it to `REPORTER_TOKEN_PATH` (mode `0600`).
3. Delete the outage flag: `rm -f "$REPORTER_HANDOVER_DIR/.token_outage_logged"`.
4. Posting resumes at the next quarter-hour cycle — no restart needed.

## No credential values live here, or anywhere the scripts write

The token itself is read from a path outside `.claude/jobs/`, the repository, and the
handover directory — `NT-0012`'s rule, applied. Nothing in these scripts, this file, or
their logs ever contains the token value; `get_token()` reads it once per call and passes
it straight into a `curl` header, never printed, never logged, never echoed.

## Verified

**2026-08-29 — filed and smoke-tested against a scratch handover directory, not merely
read.** `nudge.py`: no marker file returns `OK`; a fresh marker returns `OK`; a marker
thirty minutes old returns `NUDGE_NEEDED` and logs one correctly-formatted line.
`reporter.py`: a missing token path logs `TOKEN OUTAGE START` exactly once across two
consecutive runs, confirming the outage flag actually suppresses the second write rather
than merely being created. `uv run ruff check .` passes repo-wide with the three scripts
included in scope (`pyproject.toml`'s ruff exclusion now names vendored skill directories
individually rather than `.claude/skills` as a whole — see that file's own comment).
