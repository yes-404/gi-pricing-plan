#!/usr/bin/env bash
# Spike F1 matrix: N in {2,4,8}, 3 runs each, 200 rps, 40 s, deploy A->B at 10 s.
# Waits up to 120 s for load1 < 12 before each run and records the load the run started at.
set -u
HERE=/home/puzhenhao1989/.claude/jobs/66723b39/tmp/p2/spike-f1/scratch/spike/f1
PY=/home/puzhenhao1989/.claude/jobs/66723b39/tmp/p2/spike-f1/scratch/.venv/bin/python
for rep in 1 2 3; do
  for n in 2 4 8; do
    end=$(( $(date +%s) + 120 ))
    until awk '{exit !($1<12)}' /proc/loadavg || [ "$(date +%s)" -gt "$end" ]; do sleep 5; done
    echo "== n=$n rep=$rep start=$(TZ=Europe/London date +%T) load=$(cut -d' ' -f1-3 /proc/loadavg)"
    "$PY" "$HERE/run.py" "$n" --duration 40 --deploy-at 10 --tag "m-n$n-r$rep"
    echo "rc=$?"
  done
done
echo MATRIX-DONE
