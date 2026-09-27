#!/usr/bin/env bash
set -uo pipefail
export RUNTIME_STATE_FILE=/home/puzhenhao1989/gi-pricing-plan.local/handover/runtime-state.json
cd /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-abfcd60c8a355efed
SHA=$(git rev-parse --short=7 HEAD)

flock -w 7200 /tmp/slots/w37-6-expensive -c '
python3 /home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/agent-abfcd60c8a355efed/.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py announce \
  --what migrate_verify --by exec-pr-d1 --tree '"$(git rev-parse HEAD)"' --ttl-seconds 3600
echo "UPTIME BEFORE:" ; uptime
setsid nohup bash -c "python3 scripts/doc-id.py migrate --verify /tmp/w37-6-pr-d1-verify-'"$SHA"' --ref HEAD > /tmp/w37-6-pr-d1-scratch/verify-HEAD-'"$SHA"'.log 2>&1; echo VERIFY_EXIT=\$? >> /tmp/w37-6-pr-d1-scratch/verify-HEAD-'"$SHA"'.log" &
VERIFY_PID=$!
wait "$VERIFY_PID"
echo "UPTIME AFTER:" ; uptime
'
