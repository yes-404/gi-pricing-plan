#!/bin/bash
# SL-1526 ALONE window (WK-1178 exit demo (a)): Acceptance 8 demo run (FULL seed) + 11(b) fit table + REAL-GLM report.
# Runs ALONE under gate-1, gate-2 and small-test, on the lead's "ALONE GRANTED".
# Usage: run.sh <expected slice HEAD sha> <out dir>     (run from the committed copy of this directory)
# Authority (to-lead.md): "2026-10-11 11:39:18 BST" item 3 (real GLM tested only here; any property failure -> STOP,
# no edit, no retry), "2026-10-11 14:19:08 BST" item 3 (bounds <= 60 min / <= 15.5 GiB, nothing beside it),
# "2026-10-11 15:12:46 BST" (START/END stamp per timed invocation). Pre-registration as SL-1367 run D: this
# directory is committed and pushed BEFORE the run; the run prints every script's blob sha and the commit's sha and
# committer time, and refuses (exit 96) if a local script differs from the committed blob.
# Order (maintainer, to-lead "2026-10-11 16:37:21 BST" item 4): Acceptance 8 -> real-GLM report -> 11(b) -> stage d.
#   Stage d (option A) = the dislocation + attribution run over the 20,000-policy sample, the DP-2 VERDICT object
#   ("16:34:21 BST"): process-tree peak RSS (sampled every 2 s) <= 15.5 GiB and job wall <= 60 min. The demo-wide
#   figures of stage a are PRINTED, not judged.
# Exit codes: 90-95 slot-preflight.sh; 96 pre-registration; 97 gate-2 / small-test not held; 98 wrong tree/guard;
#             otherwise the highest stage rc (driver 1-2, realglm 4, fittable/rows 5, treemeasure 3 = DP-2 MISS, 4 = failed/STOP).
set -u
G=/home/puzhenhao1989/gi-pricing-plan
W=$G/.claude/worktrees/sl-1526
EW=$G/.claude/worktrees/sl-1526-evidence       # evidence worktree: branch evidence/sl-1526-alone-2026-10-11
REL=evidence/sl-1526-alone
E=$(dirname "$(readlink -f "$0")")             # the scripts this run executes
SCRIPTS="run.sh driver.py realglm.py fittable.py rows.py sampler.py treemeasure.py dislocation.py"
# BASE = the dispatch tree: the slice branch was created at 31b88780 (`git reflog show sl-1526-exit-demo-a`:
# "31b88780 sl-1526-exit-demo-a@{18}: branch: Created from origin/main"), the plan's other option being 809a3794.
# examples/ is identical from 31b88780 to the slice's merge-base 99f22479 (`git diff --stat 31b88780 99f22479 -- examples`
# is empty), and 809a3794 is 28k lines of backend/packages older than the venv this run uses, so it is not used.
BASE=31b88780
# Acceptance 8 seeds the FULL book (maintainer, to-lead "2026-10-11 19:36:01 BST" ruling (i); PL-1577 DP-1 keeps the GLM on
# the full book). "full" = no --rows: every script below maps it to build_csv(None) / a seed with no --rows.
ROWS=full
EXPECT_HEAD=$1; OUTD=$2; STAMPS=$OUTD/stamps.tsv; LOG=$OUTD/alone.log
mkdir -p "$OUTD"; : > "$STAMPS"
exec > >(tee "$LOG") 2>&1
DSN=postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing_sl-1526_dedd6315
BDB=gipricing_sl1526_alonebase
BDSN=postgresql+asyncpg://gipricing:gipricing@localhost:5432/$BDB
SDB=gipricing_sl-1526_dedd6315
BASEDIR=$OUTD/base-tree
SLOT=/tmp/slots/gate-1
# shellcheck source=/dev/null
source /home/puzhenhao1989/gi-pricing-plan.local/handover/slot-preflight.sh

echo "== pre-registration: scripts in $E vs the evidence commit"
echo "evidence commit: $(git -C "$EW" log -1 --format='%H %cI')"
for f in $SCRIPTS; do
  lb=$(git hash-object "$E/$f"); cb=$(git -C "$EW" rev-parse "HEAD:$REL/$f" 2>&1)
  echo "$f local-blob=$lb committed-blob=$cb"
  [ "$lb" = "$cb" ] || { echo "PRE-REGISTRATION ABORT: $f differs from the committed blob"; exit 96; }
done
slot_preflight                         # exits 90-95 (HEAD guard, dirty tree, gate-1 not held, containers, alembic)
for s in /tmp/slots/gate-2 /tmp/slots/small-test; do
  if flock -n "$s" true; then echo "ALONE ABORT: $s is FREE - the window holds all three slots"; exit 97; fi
done
git -C "$W" cat-file -e "$BASE^{commit}" || { echo "BASE GUARD FAILED: $BASE missing"; exit 98; }
git -C "$W" diff --quiet "$BASE" 99f22479a20e7fa64f8b6654e0d371c595b1e35a -- examples || { echo "BASE GUARD FAILED: examples/ differs between $BASE and 99f22479"; exit 98; }
for port in 8000 5173; do
  if ss -ltn "sport = :$port" | grep -q LISTEN; then echo "ALONE ABORT: port $port is in use (demo.py needs it)"; exit 98; fi
done
# the demo's own environment (scripts/demo.py demo_env), for the base seed and the readers
export GIP_DEV_AUTH_ENABLED=true GIP_OIDC_ISSUER=http://localhost:8080/realms/gi-pricing \
  GIP_OIDC_CLIENT_ID=gi-pricing-frontend GIP_OIDC_AUDIENCE=gi-pricing-api \
  GIP_OIDC_JWKS_URL=http://localhost:8080/realms/gi-pricing/protocol/openid-connect/certs
echo "run start=$(TZ=Europe/London date -Is) slice=$EXPECT_HEAD base=$BASE rows=$ROWS"

cpu_sample() { awk '/^cpu /{print $9, $2+$3+$4+$7+$8+$9, $2+$3+$4+$5+$6+$7+$8+$9}' /proc/stat; }
# inv <label> <stage> <command...>: START/END (Europe/London, to the second), duration, rc, steal/all %.
inv() {
  local label=$1 stage=$2 s0 c0 w0 s1 c1 w1 t0 t1 a b w rc st en dur
  shift 2
  read -r s0 c0 w0 < <(cpu_sample); t0=$(date +%s.%N)
  st=$(TZ=Europe/London date '+%Y-%m-%dT%H:%M:%S%:z')
  echo "START $label stage=$stage $st"
  "$@" > "$OUTD/$label.out" 2>&1; rc=$?
  t1=$(date +%s.%N); read -r s1 c1 w1 < <(cpu_sample)
  en=$(TZ=Europe/London date '+%Y-%m-%dT%H:%M:%S%:z')
  tail -${INV_TAIL:-3} "$OUTD/$label.out"
  a=$((s1 - s0)); b=$((c1 - c0)); w=$((w1 - w0)); dur=$(awk -v x="$t0" -v y="$t1" 'BEGIN{printf "%.3f", y-x}')
  printf 'END %s %s rc=%s duration=%.1fs steal_all%%=%s\n' "$label" "$en" "$rc" "$dur" \
    "$(awk -v a="$a" -v b="$w" 'BEGIN{printf "%.2f", (b > 0) ? 100*a/b : 0}')"
  printf '%s\t%s\t%s\t%s\t%s\t%.3f\t%s\t%s\n' "$label" "$stage" "$st" "$en" "$rc" "$dur" "$a" "$w" >> "$STAMPS"
  note "$rc"; return "$rc"
}

echo "== before"; date -Is; uptime; free -h; df / | tail -1
echo "== other heavy processes"; pgrep -af '[p]ytest|[b]ench-|migrate --verify|[v]itest|[v]ue-tsc|[m]ypy' | grep -v "$REL/run.sh" || echo none

echo "== containers before"; docker ps -a --filter name=gi-pricing --format '{{.Names}} {{.Status}}'
echo "== setup (stamped, not part of the DP-2 figures): fresh databases from the template (S-14), base tree"
PGX="docker exec gi-pricing-postgres-1"
for d in "$SDB" "$BDB"; do
  inv "db-$d" setup sh -c "$PGX dropdb -U gipricing --if-exists -f '$d' && $PGX createdb -U gipricing -T gipricing '$d'" || exit 99
done
inv base-tree setup sh -c "mkdir -p '$BASEDIR' && git -C '$W' archive $BASE examples/fremtpl2 | tar -x -C '$BASEDIR' && cp -r '$W/examples/fremtpl2/data' '$BASEDIR/examples/fremtpl2/'" || exit 99

echo "== stage a: Acceptance 8 - scripts/demo.py (rows=$ROWS: the full book, no --rows) to its banner, then SIGINT (slice DB $SDB)"
GIP_DATABASE_URL=$DSN inv a_demo a python3 -I "$E/driver.py" "$W" "$OUTD/demo.log" "$ROWS"
ARC=$?
cat "$OUTD/a_demo.out"
echo "== keycloak: the demo recreated it; stop it (never compose down); containers after"
docker stop gi-pricing-keycloak-1; docker ps -a --filter name=gi-pricing --format '{{.Names}} {{.Status}}'
echo "-- demo.log: tail"; tail -25 "$OUTD/demo.log"

echo "== stage c: REAL-GLM report (fitted veh_age relativities + every declared property vs the real bundle)"
REC=$W/examples/fremtpl2/data/last-seed.json
INV_TAIL=0 GIP_DATABASE_URL=$DSN inv c_realglm c uv run --directory "$W" python "$E/realglm.py" "$W" "$REC"
CRC=$?
cat "$OUTD/c_realglm.out"
if [ "$CRC" != 0 ]; then
  grep '^STOP:' "$OUTD/c_realglm.out" || echo "STOP: real-GLM report did not complete (rc $CRC)"
fi
if [ "$ARC" != 0 ] || [ "$CRC" != 0 ]; then
  echo "RESULT: STOP - stage a rc $ARC, stage c rc $CRC. No retry, no edit (11:35:35 / 11:39:18 item 3). Report the above to the lead."
  exit "$(( ARC > CRC ? ARC : CRC ))"
fi

echo "== stage b: 11(b) fit table - slice column, then the base tree seeded on the same --rows"
INV_TAIL=0 GIP_DATABASE_URL=$DSN inv b_slice b uv run --directory "$W" python "$E/fittable.py" slice "$REC" || exit 5
CSV=$OUTD/slice-rows.csv
inv b_export_rows b uv run --directory "$W" python "$E/rows.py" export "$W" "$ROWS" "$CSV" || exit 5
GIP_DATABASE_URL=$BDSN inv b_base_migrate b uv run --directory "$W" alembic upgrade head || exit 5
GIP_DATABASE_URL=$BDSN inv b_base_seed b uv run --directory "$W" python "$E/rows.py" seed "$BASEDIR" "$CSV" "$ROWS" || exit 5
INV_TAIL=0 GIP_DATABASE_URL=$BDSN inv b_base b uv run --directory "$W" python "$E/fittable.py" base "$BASEDIR/examples/fremtpl2/data/last-seed.json" || exit 5
echo "== same-rows proof"
# Compare the parsed sha256/n/ids_sha256 fields, never the raw lines: the two lines differ in their label ("slice " vs "base  ").
rowset() { grep -E "^$1 +ROWSET " "$2" | head -1 | grep -oE '(sha256|n|ids_sha256)=[0-9a-f]+' | tr '\n' ' '; }
S=$(rowset slice "$OUTD/b_export_rows.out"); B=$(rowset base "$OUTD/b_base_seed.out")
echo "slice: $S"; echo "base : $B"
if [ -n "$S" ] && [ "$S" = "$B" ]; then echo "SAME ROWS: yes (csv sha256, row count and sorted-IDpol hash equal)"; else echo "SAME ROWS: NO - 11(b) column is not valid"; note 5; fi
SR=$(grep -o 'rows=[0-9]*' "$OUTD/b_slice.out" | head -1); BR=$(grep -o 'rows=[0-9]*' "$OUTD/b_base.out" | head -1)
echo "fitted rows: slice $SR base $BR"; [ "$SR" = "$BR" ] || { echo "SAME ROWS: NO - fitted row counts differ"; note 5; }
echo "== 11(b): fit statistics, base tree $BASE (dispatch tree) | slice head $EXPECT_HEAD, same rows, --rows $ROWS"
cat "$OUTD/b_base.out" "$OUTD/b_slice.out"
echo "factor count: base $(grep -c 'type=' "$OUTD/b_base.out") slice $(grep -c 'type=' "$OUTD/b_slice.out") (want 7 in each)"
echo "== stage d: dislocation.run + attribution over the 20,000-policy PORTFOLIO sample (DP-2 object; unchanged by the full-book fit) (a throwaway copy of the demo DB; baseline = a +1.95% re-priced measurement fixture)"
DDB=gipricing_sl1526_stage_d
inv "db-$DDB" setup sh -c "$PGX dropdb -U gipricing --if-exists -f '$DDB' && $PGX createdb -U gipricing -T '$SDB' '$DDB'" || exit 99
INV_TAIL=0 GIP_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/$DDB inv d_dislocation d \
  python3 -I "$E/treemeasure.py" dislocation "$OUTD/d_dislocation.log" JOBWALL_DISLOCATION 3600 15.5 -- \
  uv run --directory "$W" python "$E/dislocation.py" "$W" "$REC"
DRC=$?
cat "$OUTD/d_dislocation.out"; echo "-- d_dislocation.log:"; cat "$OUTD/d_dislocation.log"
if [ "$DRC" = 3 ]; then echo "RESULT: DP-2 MISS -> fallback (D); SL-1575 need. STOP to the lead (-> maintainer) with these figures."
elif [ "$DRC" != 0 ]; then echo "RESULT: STOP - stage d rc $DRC (an approval-gate block, an error or a refusal). No retry. STOP to the lead (-> maintainer)."; fi
echo "== after"; date -Is; uptime; free -h
echo "RESULT: max stage rc so far $MAXRC (0 = all stages passed and same rows proven); the DP-2 verdict is the TREEMEASURE dislocation lines of stage d"
sha256sum "$E"/run.sh "$E"/driver.py "$E"/realglm.py "$E"/fittable.py "$E"/rows.py "$E"/sampler.py "$E"/treemeasure.py "$E"/dislocation.py | cut -c1-16,65-
