#!/usr/bin/env python3
"""Balance watch v4 -- DeepSeek account balance monitor.

Reads current balance from https://api.deepseek.com/user/balance every 90s.
Token location via TOKEN_FILE env var (0600, session-ephemeral cache, never in argv/repo/handover).
Relays: BEGIN CLOSE (<10 CNY), malformed/unavailable, heartbeat every 15m elapsed.

Token source (durable): /home/puzhenhao1989/claude-deepseek.sh variable ANTHROPIC_AUTH_TOKEN.
TOKEN_FILE is a session-ephemeral cache extracted from that source via extract_token.py.
Token location only, never the value.

Thresholds (user rule 2026-08-26):
  <10 CNY: BEGIN CLOSE (no new tasks, finish PRs, clean/shut down)
  No hard stop (5 CNY forced stop removed); readings <5 still in heartbeats
  Malformed/unavailable responses: relay immediately
  Heartbeat: one per 15 min elapsed (not wall-clock; from arm time)
  Recovery crossing: >=10 when warned re-arms future <10 crossing

For configuration: read TOKEN_FILE and LOG_FILE from environment.
Env defaults: TOKEN_FILE and LOG_FILE must be set before running.

Optional: CEILING_METER_DIR, a directory holding a `ceiling_meter` module for detecting
genuine session-limit records. Unset means that check is skipped, not an error -- it has
no durable path of its own, so nothing here may hardcode one (the exact ephemeral-path
problem this skill exists to eliminate for the poller itself).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request

CEILING_METER_DIR = os.environ.get("CEILING_METER_DIR", "")
if CEILING_METER_DIR:
    sys.path.insert(0, CEILING_METER_DIR)
try:
    # F30 (registered, unfiled): ceiling_meter has no committed source and no stub, so mypy
    # can never resolve it statically -- it only exists at CEILING_METER_DIR at runtime, an
    # env-supplied path this script must not hardcode (the exact problem F30 tracks). This
    # ignore documents that gap rather than silently working around it; suppressing it is
    # not the same as fixing it, and it stays until F30 gives the module a real home.
    import ceiling_meter as m  # type: ignore[import-not-found]
except ImportError:
    m = None

# Configuration from environment
TOKEN_FILE = os.environ.get("TOKEN_FILE", "")
LOG_FILE = os.environ.get("LOG_FILE", "")
if not TOKEN_FILE or not LOG_FILE:
    raise SystemExit("ERROR: TOKEN_FILE and LOG_FILE env vars required")

URL = "https://api.deepseek.com/user/balance"
INTERVAL = 90
TIMEOUT = 10
WARN_BELOW = 10.0  # BEGIN CLOSE; no hard stop (user rule 2026-08-26)


def token() -> str:
    with open(TOKEN_FILE) as f:
        return f.read().strip()


def log(line: str) -> None:
    """Append one UTC-timestamped line to the heartbeat log."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{dt.datetime.now(dt.UTC):%Y-%m-%d %H:%M:%S} UTC {line}\n")


def emit(line: str) -> None:
    """Print to Monitor stream and append to log."""
    print(line, flush=True)
    log(line)


def read_balance() -> dict[str, object]:
    req = urllib.request.Request(
        URL,
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer " + token(),
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        parsed = json.loads(r.read().decode())
    if not isinstance(parsed, dict):
        # json.loads returns Any; a non-object top level (e.g. the API answering with a
        # bare list or string) used to reach the caller silently and crash later, outside
        # the try/except in main() that exists precisely to turn this into a handled
        # "BALANCE MALFORMED" relay rather than an unguarded stack trace.
        raise ValueError(f"balance response was not a JSON object: {parsed!r}")
    return parsed


def main() -> None:
    arm = dt.datetime.now(dt.UTC)
    seen = set()
    state = "ok"  # ok -> warn (<10); transitions print once
    hb_due = time.time() + 15 * 60  # next heartbeat (elapsed); first 15 min after arm
    once = "--once" in sys.argv
    emit(
        f"balance watch v4 armed at {arm:%H:%M:%S} UTC -- DeepSeek balance every "
        f"{INTERVAL}s, warn <{WARN_BELOW} CNY (BEGIN CLOSE, no hard stop), "
        f"heartbeat every 15 min elapsed, token file {TOKEN_FILE} (0600, never "
        f"in argv/repo/handover), log file {LOG_FILE}"
    )
    while True:
        # Real balance read.
        data = None
        try:
            data = read_balance()
        except Exception as e:
            emit(f"BALANCE MALFORMED: {type(e).__name__}: {e}")
        if data is not None:
            if not data.get("is_available", False):
                emit(f"BALANCE UNAVAILABLE: is_available=false response={json.dumps(data)[:200]}")
            else:
                cny = None
                balance_infos = data.get("balance_infos", [])
                if isinstance(balance_infos, list):
                    for entry in balance_infos:
                        if isinstance(entry, dict) and entry.get("currency") == "CNY":
                            total = entry.get("total_balance")
                            if isinstance(total, (int, float, str)):
                                cny = float(total)
                if cny is None:
                    emit(f"BALANCE NO-CNY: {json.dumps(data)[:200]}")
                else:
                    if cny < WARN_BELOW and state == "ok":
                        state = "warn"
                        emit(
                            f"BEGIN CLOSE (below {WARN_BELOW} CNY): {cny} CNY -- "
                            "warn manager immediately"
                        )
                    elif cny >= WARN_BELOW and state == "warn":
                        # Recovery re-arms crossing (lead ruling 2026-08-28)
                        state = "ok"
                        emit(
                            f"BALANCE RECOVERED (>= {WARN_BELOW} CNY): {cny} CNY "
                            "-- crossing re-armed"
                        )
                    if once:
                        emit(f"BALANCE READING: {cny} CNY")
                    if time.time() >= hb_due:
                        hb_due += 15 * 60
                        emit(f"BALANCE HEARTBEAT: {cny} CNY")
        if once:
            return
        # Zero-fallback: genuine session-limit records (exhaustion in-session).
        if m is not None:
            try:
                for ts, f, s in m.live_limit_events(arm):
                    key = (ts, f, s[:40])
                    if key in seen:
                        continue
                    seen.add(key)
                    emit(f"BALANCE LIMIT EVENT: {ts} {f} {s}")
            except Exception as e:
                emit(f"BALANCE PROBE ERROR: {type(e).__name__}: {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
