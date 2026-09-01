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
6. **`.last_reported_main_sha` in the handover directory tracks the SHA last successfully
   *posted*, not merely last seen.** `main()` only calls `set_last_reported_sha` after
   `post_to_slack` returns success — a failed post leaves the marker alone, so the next
   cycle re-diffs from the same baseline instead of silently dropping commits nobody actually
   saw reported. The comparison itself always asks the remote directly
   (`get_remote_main_sha` uses `git ls-remote`, never a cached `git log origin/main` — its
   docstring carries the incident that made this non-optional); a `git fetch` only runs, in
   `get_merged_subjects`, once that comparison has already shown the tip moved.

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
`SendMessage` mechanism above, not a Slack `@mention`). The routine post carried balance
and open-PR count only at filing time. Maintainer instruction, 2026-08-29, later withdrew
the balance line and added an ETA section (relayed verbatim from a lead-owned file, never
computed here) and an in-flight section — open PRs with their CI state, plus commits merged
to `main` since the last successful post. Wiring in a real roster summary remains future
work, not regression — nothing here has ever actually surfaced roster content.

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

**2026-08-29, later the same day — balance withdrawn, ETA and in-flight sections added,
re-verified the same way.** `get_eta` tested against the real `eta.md` (the Headline
paragraph extracted whole across its wrapped source lines, stopping before the next
paragraph), a missing file, a file with no `**Headline:**` paragraph, and a headline with no
parseable `**Updated:**` stamp — each case says so explicitly rather than guessing or
omitting the section. `get_remote_main_sha` returns the real `origin/main` tip via
`git ls-remote` and returns `None` rather than raising against a non-repository path.
`get_merged_subjects` returns real commit subjects for a known range and `[]` for an empty
one. `main()` was run end-to-end four times against a scratch handover directory with
`post_to_slack` stubbed out — no real Slack call was ever made: a first run sets the SHA
baseline, a second run against an unmoved `main` reports "unchanged", a third run with a
forced state marker and a stubbed *failed* post leaves that marker untouched (confirming the
SHA advances only on a confirmed post), and a fourth confirms the token-outage path is
unchanged. `uv run ruff check .` passes repo-wide; `uv run mypy --strict` on this file
passes — the bare `uv run mypy` does not examine `.claude/skills/` at all (its configured
`files` list is `packages/*/src` and `backend/src` only), so that command alone would have
proven nothing about this file. There is no CI workflow for `.claude/**`
(`docs/audit/register.md` F26), so these local runs are the only gate this change has.

**2026-08-31 — two `get_eta` defects found and fixed, TDD, against a new regression suite
(not merely re-smoke-tested).** (1) The `**Updated:**` regex required a literal `Z`
suffix, but `eta.md`'s own header says "All times are GB local (BST, UTC+1)" and real
stamps are written that way — measured over the reporter's full operating history (212
Slack messages, 2026-08-29..2026-08-31), the STALE branch had fired zero times and
166/190 ETA posts read "staleness unknown". Fixed by accepting `BST`/`GMT` alongside `Z`
and resolving GB-local stamps through `zoneinfo.ZoneInfo("Europe/London")` rather than a
hardcoded `+1`, so a `GMT` (winter, UTC+0) stamp is not treated as an hour ahead. (2) the
returned headline included its own `**Headline:**` label, doubling it at the call site
(`*ETA:* **Headline:** …`) in every historical post — the label is now stripped in
`get_eta`, with the rest of the paragraph (its own `**` emphasis, em dashes, and
additional lines) relayed byte-for-byte.

Both defects are exercised by
`.claude/skills/reporter-cycle/scripts/tests/test_reporter.py` (9 tests, run directly —
not part of `pyproject.toml`'s `testpaths`, since these scripts are stdlib-only utilities
outside the uv workspace): a BST stamp, a GMT stamp (chosen specifically so a hardcoded
`+1` would flip its `stale` result), a `Z` stamp (regression guard — one is live in
`eta.md`), an unparseable-timezone stamp and a garbage-suffix-glued-to-letters stamp (both
must still return `stale=None`, not a guess), a stamp old enough that the STALE branch
actually fires (asserted through to `format_routine_post`'s rendered `STALE` text — that
branch had never fired in production), a missing-stamp and a missing-file case, and the
headline-label-stripped-content-preserved-verbatim case. Every test was confirmed to fail
for the stated reason against the pre-fix code before the fix was applied. `uv run ruff
check .` passes repo-wide; `uv run mypy --strict` on `reporter.py` and the new test file
passes. The full workspace `uv run pytest -q` was not run to completion for this change:
`reporter.py` sits outside every `testpaths` entry and nothing in the workspace imports it,
so that suite does not exercise the changed code, and — contending for the same
docker-compose Postgres/Redis/MinIO stack as other sessions running concurrently in this
repository's shared `.git` — it was still at 23% after 21 minutes when stopped.

**2026-09-01 — the routine-post log line recorded only `ok=True`/`ok=False`, never the
Slack response or the message sent.** Found 2026-08-31, deferred for want of session time:
an artifact consulted as evidence that could say *that* a post happened but never *what*
was sent or *what* Slack said back. `post_to_slack` now returns `(ok, detail)` instead of a
bare `bool`; `main()` logs `detail` alongside `ok` and the rendered post body as a second
log line. `detail` is built to never carry the token: the Slack response body itself never
echoes the `Authorization` header, but `subprocess.TimeoutExpired.__str__` includes the
full argv it was given — which contains `Authorization: Bearer <token>` — so that
exception is now caught in its own branch and never stringified into `detail` or the log
(previously it was folded into the same `except (OSError, subprocess.TimeoutExpired,
json.JSONDecodeError)` clause as the others and printed via `f"{exc}"`, which would have
put a live token into stderr — never into the log file itself, since only stdout's `ok`
value reached `_log_line`, but the token-safety of `detail` is now an explicit invariant
rather than an accident of what happened not to be logged). Proved on deliberately broken
input, not merely re-smoke-tested: a real call against the live Slack API with a garbage
token, run twice against a scratch handover directory, produced
`ok=False - detail=invalid_auth` (Slack's real error, not just the boolean) and the
rendered post body on both lines, with the token appearing zero times in the log file on
disk (`grep -c` on the token substring, not inferred from the script's return code). A
second live end-to-end run of `main()` with `subprocess.run` stubbed to return a Slack
success response produced `ok=True - detail=ok` plus the rendered body, confirming the
change did not disturb the success path. Six new unit tests in
`test_reporter.py` cover `post_to_slack`'s four branches (no token, Slack error, Slack
success, and the `TimeoutExpired` token-leak guard specifically — asserting the token
string is absent from `detail`) plus the log line's content on both the failure and
success path; all 15 tests (9 prior + 6 new) pass. `uv run ruff check .` and
`uv run mypy --strict` on `reporter.py` and the test file both pass.
