#!/bin/bash
# run.sh <label> <dir> <cmd...>: load-gated run from <dir>, cores 8-15; samples every child's cwd+cpus.
L=$1; D=$2; shift 2; LOG=$(dirname $0)/$L.log
bash $(dirname $0)/../gate.sh >> $LOG
env -C $D taskset -c 8-15 "$@" >> $LOG 2>&1 & top=$!
sleep 4
for p in $top $(pgrep -P $top) $(for c in $(pgrep -P $top); do pgrep -P $c; done); do
  [ -e /proc/$p ] && echo "PROC $p $(ps -o comm= -p $p) cwd=$(readlink /proc/$p/cwd) $(taskset -pc $p | sed 's/.*list: /cpus=/')"; done | sort -u -k3,3 -k4,4 | head -6 >> $LOG
wait $top; echo "rc=$? END $(uptime)" >> $LOG
