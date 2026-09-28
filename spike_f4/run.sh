#!/usr/bin/env bash
# Spike F4 runner: each (arm, seed) in 3 fresh interpreter processes with different
# PYTHONHASHSEED; prints distinct sha256 count per (arm, seed), cases, counterexample.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
PY=$HERE/../.venv/bin/python
OUT=$HERE/out; rm -rf "$OUT"; mkdir -p "$OUT"
ARMS=${ARMS:-"numpy hyp_seed hyp_derand hyp_derand_seed hyp_defaults hyp_pass hyp_db_shared"}
SEEDS=${SEEDS:-"0 1 42 20260928 987654321"}
HASHSEEDS=${HASHSEEDS:-"0 1 random"}
for arm in $ARMS; do
  for s in $SEEDS; do
    export F4_DB_DIR=$OUT/db-$arm-$s
    i=0
    for hs in $HASHSEEDS; do
      i=$((i+1))
      ( cd "$OUT" && PYTHONHASHSEED=$hs "$PY" "$HERE/harness.py" "$arm" "$s" "$OUT/$arm-$s-p$i.json" ) \
        || echo "RUN-ERROR $arm $s p$i rc=$?"
    done
    n=$(sha256sum "$OUT/$arm-$s"-p*.json | awk '{print $1}' | sort -u | wc -l)
    cases=$("$PY" -c "import json,sys;l=json.load(open(sys.argv[1]));print(len(l)-1)" "$OUT/$arm-$s-p1.json")
    cx=$("$PY" -c "import json,sys;l=json.load(open(sys.argv[1]));r=l[-1];print(json.dumps(r.get('ctx',r['RESULT']),sort_keys=True))" "$OUT/$arm-$s-p1.json")
    cxn=$(for f in "$OUT/$arm-$s"-p*.json; do "$PY" -c "import json,sys;print(json.dumps(json.load(open(sys.argv[1]))[-1],sort_keys=True))" "$f"; done | sort -u | wc -l)
    echo "[$(TZ=Europe/London date +%H:%M:%S) $(uptime | sed "s/.*load average: //")] $arm seed=$s distinct_logs=$n distinct_final=$cxn calls=$cases final=$cx"
  done
done
