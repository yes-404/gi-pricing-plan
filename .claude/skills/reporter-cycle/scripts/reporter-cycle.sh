#!/bin/bash
# 15-minute reporter cycle: post at each quarter mark (:00/:15/:30/:45 UTC), then check for
# lead staleness. See ../SKILL.md for the mechanism and why quarter-mark sleeping matters.
#
# Required: REPORTER_HANDOVER_DIR (exported before this script runs).
set -euo pipefail

if [ -z "${REPORTER_HANDOVER_DIR:-}" ]; then
  echo "ERROR: REPORTER_HANDOVER_DIR is not set — see SKILL.md" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while true; do
  now=$(date +%s)
  next=$(( (now / 900 + 1) * 900 ))
  sleep $(( next - now ))
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "POST_DUE $ts"
  python3 "$SCRIPT_DIR/reporter.py"
  nudge_result=$(python3 "$SCRIPT_DIR/nudge.py")
  if [ "$nudge_result" = "NUDGE_NEEDED" ]; then
    echo "NUDGE_SIGNAL $ts"
  fi
done
