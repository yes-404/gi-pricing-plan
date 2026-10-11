#!/bin/bash
# PL-1364 Task 5 — NFR-502 re-measure, RUN D (RL-1365 DP-A2). Runs ALONE under gate-1, gate-2 and small-test.
# Usage: run.sh <expected HEAD sha> <out dir>    (run from the HEAD tree's committed copy of this file)
# Criterion: to-lead "2026-10-11 15:26:41 BST" item 2 (i), pre-registered; this script and cleancheck.py are
# committed and pushed BEFORE the run (15:27:07) on the evidence branch; the run prints every script's blob sha and
# that commit's sha and committer time, and refuses (exit 96) if any local script differs from the committed blob.
set -u
G=/home/puzhenhao1989/gi-pricing-plan
HEADT=$G/.claude/worktrees/sl-1367
BASET=$G/.claude/worktrees/sl-1367-base
EW=$G/.claude/worktrees/sl-1367-evidence   # the evidence worktree: branch evidence/sl-1367-t5-runD-2026-10-11
REL=evidence/sl-1367-t5
E=$(dirname "$(readlink -f "$0")")           # the scripts this run executes
SCRIPTS="run.sh cleancheck.py limb13.py test_zz_limb2.py shapes.py verdict.py"
EXPECT_HEAD=$1; OUTD=$2; OUT=$OUTD/t5.jsonl; LOG=$OUTD/t5.log; STAMPS=$OUTD/stamps.tsv
mkdir -p "$OUTD"; : > "$OUT"; : > "$STAMPS"
exec > >(tee "$LOG") 2>&1
W=$HEADT
DSN=${T5_DSN:-postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_sl-1367_9dd03528}
SLOT=/tmp/slots/gate-1
slot_cleanup() { rm -f "$HEADT/backend/tests/test_zz_limb2.py" "$BASET/backend/tests/test_zz_limb2.py"; }
# shellcheck source=/dev/null
source /home/puzhenhao1989/gi-pricing-plan.local/handover/slot-preflight.sh
echo "== pre-registration: scripts in $E vs the evidence commit"
echo "evidence commit: $(git -C "$EW" log -1 --format='%H %cI')"
for f in $SCRIPTS; do
  lb=$(git hash-object "$E/$f"); cb=$(git -C "$EW" rev-parse "HEAD:$REL/$f" 2>&1)
  echo "$f local-blob=$lb committed-blob=$cb"
  [ "$lb" = "$cb" ] || { echo "PRE-REGISTRATION ABORT: $f differs from the committed blob"; exit 96; }
done
slot_preflight          # exits 90-95; also exports GIP_GATE_SLOT and the DSN
B=$(git -C "$BASET" rev-parse HEAD)
echo "base=$B"
[ "$B" = 99f22479a20e7fa64f8b6654e0d371c595b1e35a ] || { echo "BASE GUARD FAILED"; exit 2; }
echo "run start=$(TZ=Europe/London date -Is)"

# steal ($9); busy = user+nice+system+irq+softirq+steal; all = busy + idle ($5) + iowait ($6)  (Q3 (b), 15:32:42: the verdict uses steal/all)
cpu_sample() { awk '/^cpu /{print $9, $2+$3+$4+$7+$8+$9, $2+$3+$4+$5+$6+$7+$8+$9}' /proc/stat; }
# inv <label> <limb> <tree> <iter> <command…>: START/END stamps, duration, steal delta, CPU delta, steal%.
inv() {
  local dur label=$1 limb=$2 tree=$3 it=$4 s0 c0 w0 s1 c1 w1 t0 t1 a b w rc
  shift 4
  read -r s0 c0 w0 < <(cpu_sample); t0=$(date +%s.%N)
  local st; st=$(TZ=Europe/London date "+%Y-%m-%dT%H:%M:%S%:z")
  echo "START $label limb=$limb tree=$tree iter=$it $st"
  "$@" > "$OUTD/$label.out" 2>&1; rc=$?
  t1=$(date +%s.%N); read -r s1 c1 w1 < <(cpu_sample)
  local en; en=$(TZ=Europe/London date '+%Y-%m-%dT%H:%M:%S%:z')
  tail -3 "$OUTD/$label.out"
  a=$((s1 - s0)); b=$((c1 - c0)); w=$((w1 - w0)); dur=$(awk -v x="$t0" -v y="$t1" 'BEGIN{printf "%.3f", y-x}')
  printf 'END %s %s rc=%s duration=%.1fs steal_delta=%s busy_delta=%s all_delta=%s steal_busy%%=%s steal_all%%=%s\n' "$label" "$en" "$rc" \
    "$dur" "$a" "$b" "$w" "$(awk -v a="$a" -v b="$b" 'BEGIN{printf "%.2f", (b > 0) ? 100*a/b : 0}')" \
    "$(awk -v a="$a" -v b="$w" 'BEGIN{printf "%.2f", (b > 0) ? 100*a/b : 0}')"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%.3f\t%s\t%s\t%s\n' "$label" "$limb" "$tree" "$it" "$st" "$en" \
    "$dur" "$a" "$b" "$w" >> "$STAMPS"
  note "$rc"
}

echo "== before"; date -Is; uptime; free -h; df / | tail -1
echo "== other heavy processes"; pgrep -af '[p]ytest|[b]ench-|migrate --verify|[v]itest|[v]ue-tsc|[m]ypy' | grep -v "$REL/run.sh" || echo none
echo "== limbs 1 and 3 (HEAD)"
inv limb13 13 HEAD 1 timeout 900 uv run --directory "$HEADT" python "$E/limb13.py" "$OUT"
echo "== limb 2 (base, HEAD alternating x3)"
for i in 1 2 3; do
  for T in base HEAD; do
    if [ $T = base ]; then TREE=$BASET; else TREE=$HEADT; fi
    cp "$E/test_zz_limb2.py" "$TREE/backend/tests/test_zz_limb2.py"
    LIMB2_OUT=$OUT LIMB2_TREE=$T LIMB2_SHAPES=$E inv "limb2-$T-$i" 2 $T $i \
      timeout 900 uv run --directory "$TREE" pytest -q -s -p no:cacheprovider backend/tests/test_zz_limb2.py
    rm -f "$TREE/backend/tests/test_zz_limb2.py"
  done
done
echo "== after"; date -Is; uptime; free -h
echo "== CLEAN CHECK (before the verdict)"
python3 -I "$E/cleancheck.py" clean "$STAMPS"
echo "== verdict (the plan's statistic)"; python3 -I "$E/verdict.py" "$OUT"
echo "== paired deltas"; python3 -I "$E/cleancheck.py" paired "$OUT"
sha256sum "$E/run.sh" "$E/cleancheck.py" "$E/limb13.py" "$E/test_zz_limb2.py" "$E/shapes.py" "$E/verdict.py" | cut -c1-16,65-
