---
name: reporter-cycle
description: Run the team's 15-minute Slack status cycle and lead-staleness nudge detection — the outage flag that stops a token failure from spamming the log, the durable-token-path requirement, the quarter-mark cycle timing, and why the nudge signal is detected here but sent by the agent, never the script. Use when standing up a new session's reporter, when a Slack post stops appearing, or when configuring REPORTER_HANDOVER_DIR for a fresh handover.
---

# Reporter cycle: routine Slack posting and lead-staleness detection

Three scripts, ~250 lines, stdlib-only Python plus one bash loop: `reporter.py` posts a
routine status update to Slack every 15 minutes; `nudge.py` detects a stale lead status
line; `reporter-cycle.sh` is the loop that calls both on schedule. Filed here per
`docs/rulings/INDEX.md#2026-08-29-w11-prework-rulingsmd`'s reporter-scripts ruling (task #28) —
`CLAUDE.md` §12 names `.claude/skills/` as the home for a discovered non-obvious procedure,
and these three scripts' mechanism (below) is exactly that.

## Why this is a skill and not a role-file paragraph

The mechanism is small, complete, and already tested — reconstructing it from prose each
time a reporter is stood up is a testing burden, not a learning opportunity, and concrete
code surfaces edge cases prose reliably loses (the outage flag, below, is invisible from
either script's signature). `.claude/roles/reporter.md` keeps the WHAT (nudge threshold,
escalation rule, what the reporter does not do); this skill keeps the HOW.

## Configuration — everything is an environment variable, nothing is hardcoded

The version of these scripts that ran in the WK-671 handover directory hardcoded that
directory's literal path. That is exactly the mistake
[`RFC-842`](../../../docs/rfcs/RFC-00842-a-credential-in-an-ephemeral-job-directory-is-borrowed-not-stored-and-is-found-by-its-shape-not-its-container-s-name.md) names: operational,
session-specific state living inside checked-in, supposedly-reusable code. Refiled with
every path read from the environment instead:

| Variable | Required | Default | Read by |
|---|---|---|---|
| `REPORTER_HANDOVER_DIR` | **Yes** | none — exits 2 if unset | both scripts |
| `REPORTER_TOKEN_PATH` | No | `~/.slack-token` | `reporter.py` |
| `REPORTER_REPO_DIR` | No | current working directory | `reporter.py` (for `gh pr list`) and, since 2026-09-01, `nudge.py` (for `origin/main`'s local commit timestamp — see the dated entry below) |
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
   "no reading" (returns `None`, never raises) — a stricter parser would turn a corrupted
   marker into a crash, which is worse than a `None` reading the caller can reason about
   explicitly. **What the caller does with that `None` changed 2026-09-01** (see the dated
   entry below): under the original single-signal check, `None` meant "nothing to compare
   against, so don't nudge" — silently the safer failure when the marker was the only
   signal. Under the current three-signal conjunction, `None` instead counts as *stale*
   (never as fresh) for whichever signal produced it, because a missing source is not
   evidence of life; it can no longer, on its own, either force a nudge (the other two
   signals must also be stale) or block one.
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
handover directory — `RFC-842`'s rule, applied. Nothing in these scripts, this file, or
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
(`docs/findings/register.md` F26), so these local runs are the only gate this change has.

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


**Same day — the token at `REPORTER_TOKEN_PATH` also permits `conversations.history`,
not just `chat.postMessage`.** Verified by the reporter itself (not by this change, and
not re-verified here): it read back the 10:00 UTC post from `C0BSYRQ6NGM` and quoted its
first line, having previously — wrongly — asserted it had "no direct access to the Slack
API," when it posts through that API every cycle and the real question was scope, not
access. Reading the channel back is therefore a second, independent way to confirm a
post landed — evidence from the destination, not the sender — and it does not replace
the log line above, nor the reverse: **read-back answers what actually arrived in the
channel; the log answers what the sender tried to send, and what Slack said back.** The
case that keeps both necessary: a post that never left produces no message to read, so
the channel is simply silent — and a silent channel is indistinguishable from a cycle
that never fired at all. The log is the only artifact that tells those two apart, which
is why it still has a reason to exist now that read-back is available.

**2026-09-01 — the single-signal nudge produced a false positive at the busiest moment,
so `nudge.py` now requires all three available liveness signals to be stale.** Defect: the
nudge fired off `.last_lead_status_ts` alone, which records when the lead last *talked to
the reporter*, not whether the lead is alive. At 10:45Z the marker read 25.4 minutes
"stale" while the lead had, in that same window, merged six PRs, restarted two executors
and dispatched two roles — direct evidence of life the marker could not see. An alarm that
fires hardest when the lead is busiest gets ignored, and the real cost is not that one
false positive but the credibility loss that follows it: the alarm becomes background
noise on the one day it would matter.

Fix: `check_and_nudge` now reads three independent signals and nudges only when every one
of them is stale — `lead_is_stale`, a pure conjunction, is the predicate:
`nudge_needed = all(is_stale(marker_age), is_stale(eta_age), is_stale(main_age))`, i.e. the
*freshest* signal must be older than the threshold, not merely one of them.

1. `.last_lead_status_ts` (`marker_age_seconds`) — unchanged source, the original signal.
2. `eta.md`'s `**Updated:**` stamp (`eta_age_seconds`) — parsed via `reporter.get_eta_updated`,
   itself now factored out of `get_eta`'s existing `**Updated:**` parsing (`_parse_updated_stamp`)
   so there is exactly one place in this skill that understands the stamp format; `nudge.py`
   does not carry a second regex for it.
3. `origin/main`'s newest commit (`main_commit_age_seconds`) — read from the LOCAL ref only
   (`git log -1 --format=%ct origin/main`), never fetched from inside the nudge path: a
   monitor that blocks on the network is a monitor that can itself stop. Keeping that local
   ref current is `reporter.py`'s job (it fetches only after `get_remote_main_sha` confirms,
   via `git ls-remote`, that the tip actually moved); this function only reads what is
   already there.

**The 20-minute default threshold (`REPORTER_STALE_SECONDS`) did not change.** The defect
was in what counted as evidence of life, not in how long the alarm should wait — widening
the window would have hidden the same defect behind a longer fuse instead of fixing it.

**A missing or unparseable source counts as stale, never as fresh** (`_is_stale`: `age is
None or age > threshold`). The alternative — treating an unreadable source as evidence the
lead is alive — would let the alarm go silent forever the instant one file went missing or
one `git log` call failed, which is the exact "fails into silence" class this repository
keeps producing. Because the predicate is a conjunction of all three signals, a missing
source can never *cause* a nudge by itself; it can only fail to *block* one the other two
signals already justify (`test_lead_is_stale_missing_source_does_not_alone_force_a_nudge`).

Proved both directions, TDD, against
`.claude/skills/reporter-cycle/scripts/tests/test_nudge.py` (15 tests, all new — this is
the first test file `nudge.py` has had). Negative case, all three permutations: any one
fresh signal blocks the nudge regardless of how stale the other two are
(`test_lead_is_stale_any_one_fresh_signal_blocks_the_nudge`). Positive case — the one that
matters most, since a predicate that stops firing entirely is strictly worse than the
over-firing single-signal version it replaces, and fails silently: all three signals stale
DOES fire, exercised end-to-end through `check_and_nudge` against a real handover
directory and a real git repository (an `origin/main` ref built locally with `git
update-ref`, never a network call), with the timestamps aged past the threshold by
injecting a future `now` rather than by backdating files on disk — the sources "cannot be
retroactively aged," so the clock is what moves instead. Real captured output from that
run:

```
2026-09-01T10:52:12Z - nudge sent - marker 25.0 min, eta 25.2 min, main 25.0 min (all >20.0 min threshold)
```

`get_eta`'s own pre-existing behaviour (its 2-hour Slack-post staleness flag, unrelated to
this 20-minute nudge) is unchanged and still covered by all 15 of `test_reporter.py`'s
prior tests, re-run and still green after the `_parse_updated_stamp` extraction — confirming
the refactor moved the parsing without changing what `get_eta` returns. `uv run ruff check
.`, `uv run mypy` (the bare invocation — `.claude/skills/reporter-cycle/scripts` is in its
configured `files` list) and `uv run lint-imports` all pass repo-wide.
`.claude/skills/reporter-cycle/scripts/tests/` (both files, 30 tests) passes via
`uv run python -m pytest`. A full-repo `uv run pytest -q` was not run to completion on this
shared machine — `uv run pytest -q --collect-only` confirmed 2509 tests collect with no
errors (the changed/added files included, and the count several other sessions' concurrent
work on this same machine independently corroborated the same day), and the scoped run
above exercised every line this change touches; a prior full attempt on this machine the
same day was abandoned as stalled by another session for the same load-contention reason
`.claude/skills/dev-commands` already documents.

**2026-09-04 — RL-1059: a 100-word cap on the whole routine post, a mandatory BST clock
time in the ETA headline, and a stale-ETA marker when `origin/main` has moved without a
refresh** (`docs/rulings/RL-01059-a-100-word-cap-a-bst-clock-time-in-the-eta-and-a-refresh-on-every-origin-main-move.md`).
Three rules, implemented in `reporter.py`, each with its own broken-input proof named
verbatim in the ruling's own "Acceptance" section:

1. **The 100-word cap.** `format_routine_post` now builds the ETA-headline lines and the
   PR/merged-commit lines separately; when their combined word count exceeds
   `MAX_ROUTINE_POST_WORDS` (100), `_truncate_to_word_cap` drops words from the *non-headline*
   lines only — the headline (and its staleness annotation) is never touched — and appends
   `(+N words cut)`, where `N` is the exact count of words actually dropped. Proof:
   `test_over_140_word_body_is_truncated_to_the_cap_with_headline_intact` builds a body
   independently measured (before truncation) at well over 140 words, then asserts the
   rendered post is `<= 100` words, carries the `(+N words cut)` marker, and still contains
   the ETA line byte-for-byte.
2. **The BST-clock-time requirement.** `get_eta` now rejects any headline with no
   `HH:MM BST` (optionally `HH:MM BST YYYY-MM-DD`) token, returning the fixed
   `ETA_MALFORMED_MESSAGE` ("ETA headline malformed — no clock time") in its place, with
   `stale=None` — the Updated-stamp staleness annotation does not apply to a line that is
   not actually the lead's ETA text. Proof:
   `test_headline_with_no_clock_time_is_rejected_not_posted_as_given` writes a headline
   reading "Should land in about 2 hours, no rush." and asserts the bare-duration text
   never reaches `get_eta`'s return value or the rendered post — only the malformed message
   does. The nine pre-existing `_write_eta`-based tests were updated to embed a valid clock
   token (`ETA 14:30 BST`) in their fixture headline, so they keep exercising the
   `**Updated:**`-staleness logic under test rather than tripping this new, orthogonal
   check as a side effect.
3. **The `main:`-refresh staleness marker.** `eta.md` now carries a `**main:**` field
   beside `**Updated:**` (the sha the lead last derived the ETA against). New
   `get_eta_main_sha` parses it; new `check_main_staleness` compares it — prefix-aware, so
   a short local sha matching a full remote sha is not a false positive — against the
   live `origin/main` tip (`main()` already computes this via `get_remote_main_sha`'s
   `git ls-remote`, never the cached local ref the rest of this file's history warns
   against). On a mismatch, `main()` overrides `eta_headline` with the stale-ETA line
   ("ETA stale — main moved to `<sha>` at HH:MM BST, ETA not yet re-derived") before
   calling `format_routine_post`, replacing the carried-forward headline rather than
   appending to it. Proof:
   `test_stale_eta_after_unrefreshed_main_move_carries_the_stale_marker` reads a fixture
   `eta.md` whose `main:` field is `ad51906`, advances a fixture `origin/main` sha to
   `fa53484…` with no accompanying `eta.md` update, and asserts the rendered post carries
   the stale line (with the new short sha and "not yet re-derived") and that the
   carried-forward headline text is absent from it. A companion negative-control test,
   `test_matching_main_sha_is_not_stale_and_carried_headline_posts_unchanged`, proves a
   refreshed `main:` field (full match, and a short-sha prefix match) produces no marker.

Four new tests total (one per rule plus the negative control) plus the nine `_write_eta`
fixture updates — 34 tests in the two files, all pass via
`uv run python -m pytest .claude/skills/reporter-cycle/scripts/tests/`. `uv run ruff check
.` and `uv run mypy` (bare invocation — `.claude/skills/reporter-cycle/scripts` is in its
configured `files` list) both pass repo-wide against a freshly `uv sync --all-packages`'d
worktree; `uv run lint-imports` passes (215 files, 1510 dependencies, 3 contracts kept, 0
broken) — unaffected by this change but re-run per the two-halves-of-the-gate rule.
