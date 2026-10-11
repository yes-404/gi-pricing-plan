#!/bin/bash
# PL-1364 Task 5 — NFR-502 re-measure, RUN D (RL-1365 DP-A2). Runs ALONE under gate-1, gate-2 and small-test.
# Usage: run.sh <expected HEAD sha> <out dir>    (run from the HEAD tree's committed copy of this file)
# Criterion: to-lead "2026-10-11 15:26:41 BST" item 2 (i), pre-registered; this script and cleancheck.py are
# committed and pushed BEFORE the run (15:27:07), and the run prints their blob shas and commit time.
set -u
G=/home/puzhenhao1989/gi-pricing-plan
HEADT=$G/.claude/worktrees/sl-1367
BASET=$G/.claude/worktrees/sl-1367-base
D=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1367-t5   # limb13.py, shapes.py, verdict.py, test_zz_limb2.py
REL=scripts/measure/sl1367-t5
EXPECT_HEAD=$1; OUTD=$2; OUT=$OUTD/t5.jsonl; LOG=$OUTD/t5.log; STAMPS=$OUTD/stamps.tsv
mkdir -p "$OUTD"; : > "$OUT"; : > "$STAMPS"
exec > >(tee "$LOG") 2>&1
W=$HEADT
DSN=${T5_DSN:-postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_sl-1367_9dd03528}
SLOT=/tmp/slots/gate-1
slot_cleanup() { rm -f "$HEADT/backend/tests/test_zz_limb2.py" "$BASET/backend/tests/test_zz_limb2.py"; }
# shellcheck source=/dev/null
source /home/puzhenhao1989/gi-pricing-plan.local/handover/slot-preflight.sh
slot_preflight          # exits 90-95; also exports GIP_GATE_SLOT and the DSN
B=$(git -C "$BASET" rev-parse HEAD)
echo "base=$B"
[ "$B" = 99f22479a20e7fa64f8b6654e0d371c595b1e35a ] || { echo "BASE GUARD FAILED"; exit 2; }
[ "$(readlink -f "$0")" = "$HEADT/$REL/run.sh" ] || { echo "SCRIPT GUARD FAILED: run the committed copy $HEADT/$REL/run.sh"; exit 3; }
echo "== pre-registered criterion (to-lead 2026-10-11 15:26:41 BST item 2 (i))"
for f in run.sh cleancheck.py; do
  echo "$REL/$f blob=$(git -C "$HEADT" rev-parse "HEAD:$REL/$f") committed=$(git -C "$HEADT" log -1 --format=%cI -- "$REL/$f")"
done
echo "run start=$(TZ=Europe/London date -Is)"

cpu_sample() { awk '/^cpu /{print $9, $2+$3+$4+$7+$8+$9}' /proc/stat; }   # steal (8th value after the label), user+nice+system+irq+softirq+steal
# inv <label> <limb> <tree> <iter> <command…>: START/END stamps, duration, steal delta, CPU delta, steal%.
inv() {
  local dur label=$1 limb=$2 tree=$3 it=$4 s0 c0 s1 c1 t0 t1 a b rc
  shift 4
  read -r s0 c0 < <(cpu_sample); t0=$(date +%s.%N)
  local st; st=$(TZ=Europe/London date "+%Y-%m-%dT%H:%M:%S%:z")
  echo "START $label limb=$limb tree=$tree iter=$it $st"
  "$@" > "$OUTD/$label.out" 2>&1; rc=$?
  t1=$(date +%s.%N); read -r s1 c1 < <(cpu_sample)
  local en; en=$(TZ=Europe/London date '+%Y-%m-%dT%H:%M:%S%:z')
  tail -3 "$OUTD/$label.out"
  a=$((s1 - s0)); b=$((c1 - c0)); dur=$(awk -v x="$t0" -v y="$t1" 'BEGIN{printf "%.3f", y-x}')
  printf 'END %s %s rc=%s duration=%.1fs steal_delta=%s cpu_delta=%s steal%%=%s\n' "$label" "$en" "$rc" \
    "$dur" "$a" "$b" "$(awk -v a="$a" -v b="$b" 'BEGIN{printf "%.2f", (b > 0) ? 100*a/b : 0}')"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%.3f\t%s\t%s\n' "$label" "$limb" "$tree" "$it" "$st" "$en" \
    "$dur" "$a" "$b" >> "$STAMPS"
  note "$rc"
}

echo "== before"; date -Is; uptime; free -h; df / | tail -1
echo "== other heavy processes"; pgrep -af '[p]ytest|[b]ench-|migrate --verify|[v]itest|[v]ue-tsc|[m]ypy' | grep -v "$REL/run.sh" || echo none
echo "== limbs 1 and 3 (HEAD)"
inv limb13 13 HEAD 1 timeout 900 uv run --directory "$HEADT" python "$D/limb13.py" "$OUT"
echo "== limb 2 (base, HEAD alternating x3)"
for i in 1 2 3; do
  for T in base HEAD; do
    if [ $T = base ]; then TREE=$BASET; else TREE=$HEADT; fi
    cp "$D/test_zz_limb2.py" "$TREE/backend/tests/test_zz_limb2.py"
    LIMB2_OUT=$OUT LIMB2_TREE=$T LIMB2_SHAPES=$D inv "limb2-$T-$i" 2 $T $i \
      timeout 900 uv run --directory "$TREE" pytest -q -s -p no:cacheprovider backend/tests/test_zz_limb2.py
    rm -f "$TREE/backend/tests/test_zz_limb2.py"
  done
done
echo "== after"; date -Is; uptime; free -h
echo "== CLEAN CHECK (before the verdict)"
python3 -I "$HEADT/$REL/cleancheck.py" clean "$STAMPS"
echo "== verdict (the plan's statistic)"; python3 -I "$D/verdict.py" "$OUT"
echo "== paired deltas"; python3 -I "$HEADT/$REL/cleancheck.py" paired "$OUT"
sha256sum "$HEADT/$REL/run.sh" "$HEADT/$REL/cleancheck.py" "$D/limb13.py" "$D/test_zz_limb2.py" "$D/shapes.py" "$D/verdict.py" | cut -c1-16,65-
