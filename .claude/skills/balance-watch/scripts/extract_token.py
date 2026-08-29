#!/usr/bin/env python3
"""Extract ANTHROPIC_AUTH_TOKEN from claude-deepseek.sh into a session-local cache file.

Never prints the token value -- only destination, mode, and a shape check.

Usage:
  python3 extract_token.py <output-path>            # source defaults to the durable file below
  python3 extract_token.py <output-path> <source>    # override the source too (e.g. for testing)

DST_FILE / TOKEN_SOURCE_FILE env vars work the same as the two positional arguments; an
argument, where given, wins. Output file: 0600 (read by watcher only). Source file
defaults to /home/puzhenhao1989/claude-deepseek.sh -- durable, unlike the destination,
which is a session's ephemeral cache and is expected to need re-extraction every session.
"""

from __future__ import annotations

import os
import re
import stat
import sys

DEFAULT_SOURCE = "/home/puzhenhao1989/claude-deepseek.sh"

# SRC and DST from environment or arguments
SRC = os.environ.get("TOKEN_SOURCE_FILE", DEFAULT_SOURCE)
DST = os.environ.get("DST_FILE", "")

# Allow command-line overrides
if len(sys.argv) > 1:
    DST = sys.argv[1]
if len(sys.argv) > 2:
    SRC = sys.argv[2]

if not SRC or not DST:
    raise SystemExit(
        "ERROR: set DST_FILE (and optionally TOKEN_SOURCE_FILE) env vars, "
        "or pass as arguments: extract_token.py <dst> [<src>]"
    )

with open(SRC) as f:
    text = f.read()

m = None
for line in text.splitlines():
    if line.lstrip().startswith("#"):
        continue
    if "ANTHROPIC_AUTH_TOKEN" not in line or "=" not in line:
        continue
    m = re.search(r"ANTHROPIC_AUTH_TOKEN\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|(\S+))", line)
    if m:
        break

if m is None:
    raise SystemExit(f"ERROR: no ANTHROPIC_AUTH_TOKEN= line found in {SRC}")

token = m.group(1) or m.group(2) or m.group(3)
if not token:
    raise SystemExit("ERROR: empty token value")

fd = os.open(DST, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as f:
    f.write(token + "\n")
os.chmod(DST, 0o600)

print(f"extracted: {DST}")
print(f"mode: {oct(stat.S_IMODE(os.stat(DST).st_mode))}")
print(f"shape: starts_with_sk={token.startswith('sk-')}")
