---
name: balance-watch
description: Monitor the DeepSeek account balance that funds this session — the endpoint, the BEGIN CLOSE and recovery-rearm thresholds and why each, the 15-minute elapsed heartbeat, and the durable token source versus its ephemeral extracted cache. Use when standing up a new session's watcher, when the balance poller needs re-arming, or when extracting a fresh token file.
---

# balance-watch

Monitor DeepSeek account balance via https://api.deepseek.com/user/balance every 90s. 
Reads configuration from TOKEN_FILE and LOG_FILE environment variables.

## Mechanism

- **Endpoint:** GET https://api.deepseek.com/user/balance (90s poll, 10s timeout)
- **Token:** Read from TOKEN_FILE (0600). Location: /home/puzhenhao1989/claude-deepseek.sh variable ANTHROPIC_AUTH_TOKEN. Extract via extract_token.py. NEVER the value.
- **Relay rules:** BEGIN CLOSE (<10 CNY), malformed/unavailable/no-CNY, heartbeat every 15m elapsed (not wall-clock, from arm time).
- **Format:** UTC timestamp, line-per-event to LOG_FILE. Monitor stream with `python3 -u` (unbuffered; v1 block-buffered ran 2h printing zero events).

## Thresholds (User Rule 2026-08-26)

| Reading | State | Action |
|---|---|---|
| <10 CNY | ok→warn | BEGIN CLOSE: no new tasks, finish PRs, clean/shut down; relay to main immediately |
| ≥10 CNY | warn→ok | BALANCE RECOVERED: crossing re-armed for future <10 dip |
| <5 CNY | warn | Still relayed in heartbeats; no hard stop (5-CNY forced stop REMOVED) |
| Malformed / unavailable / no-CNY | — | Relay immediately |

## Rationale

**BEGIN CLOSE threshold <10 CNY:** Team has ~180 min to finalize and shut down cleanly before hard stop would have fired (removed). Gives runway for emergency PRs and orderly close.

**Recovery re-arming:** When balance recovers from warn state, the crossing detector re-arms. A future sub-10 dip fires BEGIN CLOSE again on its own. Prevents false all-clear on a transient dip.

**Heartbeat every 15m elapsed:** Proves poller is live (silence >20m is failure). Wall-clock quarter-hours unreachable from 90s poll (poll cadence visits minute classes 1,2 mod 3; quarter hours are 0 mod 3). Elapsed time is the only reliable measure.

**No per-reading relay:** Routine reads suppressed; only reportable events and heartbeats relay. Avoids noise; log carries full history.

## Configuration

```bash
export TOKEN_FILE=<job-dir>/tmp/.ds_token
export LOG_FILE=<handover-dir>/balance-heartbeat.log
python3 -u balance_watch.py
```

Test before arming: `TOKEN_FILE=... LOG_FILE=... python3 -u balance_watch.py --once`

**`.ds_token` is a cache, not the token's home.** The durable source is
`/home/puzhenhao1989/claude-deepseek.sh`'s `ANTHROPIC_AUTH_TOKEN` variable — that file
predates any given session and outlives it. `TOKEN_FILE` is wherever the current session
chose to extract a working copy to (conventionally a job directory's `tmp/`, which is
ephemeral and gone once that job directory is), refreshed by re-running the extraction
below. Losing `.ds_token` loses only the cache, never the token.

## Token Extraction

`scripts/extract_token.py` — filed here, unlike `TOKEN_FILE` itself, because *this*
script has a durable home now:

```bash
python3 scripts/extract_token.py <dst-path>
# Source defaults to /home/puzhenhao1989/claude-deepseek.sh; override with a second
# argument or TOKEN_SOURCE_FILE if ever needed (e.g. for testing against a fixture).
# Writes: <dst-path> (0600, session-local -- this is what TOKEN_FILE should then point at)
# Never prints token value; prints only destination, mode, shape check
```

## Arming

Use Monitor (persistent):
```
python3 -u /path/to/balance_watch.py
```

Reports to stdout (relayed by Monitor). Also appends to LOG_FILE for lead to read directly.

## Verified

2026-08-29 — filed under `.claude/skills/balance-watch/`, mirroring `reporter-cycle`
(task #33). The poller previously ran from an ephemeral job directory
(`/home/puzhenhao1989/.claude/jobs/4e4ed21d/tmp/balance_watch_w11.py`) with no durable
home of its own — found by inventorying running processes, not by reading documents,
since a fully-documented ephemeral path reads as durable until something actually looks
for the file. The token survived the equivalent WK-670 event (job dir `58b9ba0c`) only
because it already had a durable source file; the script never did, until this filing.
Landed with two fixes made while verifying against the delivered source: the script
failed `ruff check` (missing return/argument annotations, `datetime.timezone.utc` instead
of the `datetime.UTC` alias) until brought up to the same standard `reporter-cycle`'s
scripts already meet, and an optional `ceiling_meter` integration hardcoded a second
ephemeral job-directory path (`.../jobs/9f3a41b0/tmp`) on `sys.path` — the exact class of
problem this filing exists to fix, now read from an optional `CEILING_METER_DIR` env var
instead, absent by default.

`scripts/extract_token.py` landed the same day, once found and requested — the delivered
version described a fixed source file in its docstring but had no code default for it,
so the bare `extract_token.py <dst>` form the docstring itself documents would have
errored demanding `TOKEN_SOURCE_FILE` be set every time. Given `/home/puzhenhao1989/
claude-deepseek.sh` is a genuinely durable, well-known constant — the same one already
named throughout this file and `balance_watch.py`'s own docstring — hardcoding it as
that default is the correct call, distinct from the `ceiling_meter` case above: that path
pointed at a session-specific job directory, this one does not move.
