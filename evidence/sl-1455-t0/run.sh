#!/bin/bash
# SL-1455 Task 0 — the attribution timings (PL-1454 Task 0 Steps 1, 3, 3b, 4, 5). PRE-REGISTERED.
#
# RUN ONLY in the window the lead books ALONE, under the lead's wrapper holding gate-1, gate-2 and
# small-test (three nested flocks, no `--`); foreground, under a timeout; never backgrounded or
# detached (executor.md S-9/S-11/S-12). Never `cd`: absolute paths throughout.
#
#   bash run.sh            # the full pass: 4 arms x {25,50} rps x 3 runs, + 4 py-spy passes
#   T0_RATES=25 T0_RUNS=1 T0_ARMS=bench-gbm bash run.sh   # a rehearsal subset (NOT before the window)
#
# Output: $OUT/{run.log,results.md,<arm>/<pass>/...}. DIAGNOSTIC on this shared box: an ATTRIBUTION,
# never an NFR-489 reading (Step 4).
#
# The debug-off rerun is `run2.sh` (it only sets T0_ASYNCIO_DEBUG=0, the arms and the rates, then runs this file).
# Pre-registration: this file, run2.sh and t0_app.py, t0_driver.py, t0_analyse.py are committed to the evidence
# branch EVID before any run; step 0 below proves the four files on disk are byte-identical to that
# branch's blobs, and aborts 97 if not. The tree guard is ONE EXPECT_HEAD (slot-preflight.sh), because
# a per-directory tree pin cannot say "the whole merged head" and the preflight needs the head anyway.
set -u
SCR=/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1455-t0
W=/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/sl-1455
EVID=refs/heads/evidence/sl-1455-t0-2026-10-11
EXPECT_HEAD=${T0_PROVE_WRONG_HEAD:-3c0e99a073887075478117c929753e7d6fec0f1d}   # the override exists only to prove abort 90; the log prints expect=
DB="gipricing_sl1455t0_$(date +%s)"
DSN=postgresql+asyncpg://gipricing:gipricing@localhost:5432/$DB
SLOT=/tmp/slots/gate-1
STAMP=$(TZ=Europe/London date +%Y%m%dT%H%M%S)
OUT=${T0_OUT_DIR:-$SCR/out-$STAMP}
mkdir -p "$OUT"
exec > >(tee -a "$OUT/run.log") 2>&1

# The preflight's EXIT trap runs this, then prints the `end <time> rc=` marker. No second trap here.
slot_cleanup() {
  docker exec gi-pricing-postgres-1 dropdb -U gipricing --if-exists "$DB" && echo "dropped $DB"
  echo "uptime end: $(uptime)"
  sleep 0.5   # let the tee process flush before the marker
}

stamp() { echo "[$(date -u +%FT%TZ) / $(TZ=Europe/London date '+%F %T %Z')] $*"; }
slots() {
  for s in gate-1 gate-2 small-test; do
    flock -n "/tmp/slots/$s" true && echo "$s free(rc0)" || echo "$s HELD(rc$?)"
  done | tr '\n' ' '; echo
}
quiet() { pgrep -fc '[p]ytest|[v]itest|[p]npm|[v]ite build' ; }

stamp "T0 start; HEAD $(git -C "$W" rev-parse HEAD) branch $(git -C "$W" branch --show-current)"
echo "uptime start: $(uptime)"
# Seat processes at OPEN (rerun condition 2): who else is on the box, pollers and gh and pytest included.
seat_procs() {
  echo "### $1 $(TZ=Europe/London date '+%F %T %Z'): pgrep -af of gh / pytest / vitest / uvicorn / alembic / run-small / claude seats"
  pgrep -af '[g]h (run|pr|api|workflow)|[p]ytest|[v]itest|[u]vicorn|[a]lembic|[r]un-small|[c]laude' | cut -c1-200 || true
  echo "top by CPU:"; ps -eo pid,etime,pcpu,args --sort=-pcpu | head -12 | cut -c1-200
}
seat_procs OPEN > "$OUT/seat-procs-open.txt"; cat "$OUT/seat-procs-open.txt"

# Step 0: pre-registration proof — the files that run are the files that were committed.
echo "evidence ref $EVID = $(git -C "$W" rev-parse "$EVID" 2>&1)"
for f in run.sh run2.sh t0_app.py t0_driver.py t0_analyse.py; do
  disk=$(git hash-object "$SCR/$f")
  blob=$(git -C "$W" rev-parse "$EVID:evidence/sl-1455-t0/$f" 2>&1)
  if [ "$disk" = "$blob" ]; then echo "prereg ok: $f $disk"
  else echo "PREREG ABORT: $f on disk $disk != committed $blob"; exit 97; fi
done

# Step 1: scratch database from the template (FD-1196/1218); the preflight then runs `alembic upgrade head`
# on it and checks for exactly one head. slot_cleanup drops it on every exit path.
TEMPLATE_HEAD=$(docker exec gi-pricing-postgres-1 psql -U gipricing -d gipricing -tAc 'select version_num from alembic_version')
echo "scratch db $DB; template alembic $TEMPLATE_HEAD"
docker exec gi-pricing-postgres-1 createdb -U gipricing -T gipricing "$DB" || { echo "createdb failed"; exit 5; }

# shellcheck source=/dev/null
source /home/puzhenhao1989/gi-pricing-plan.local/handover/slot-preflight.sh
slot_preflight   # 90 head · 91 dirty · 92 slot not held · 93 containers · 94 upgrade · 95 heads

echo "pytest/vitest processes: $(quiet || true)"
echo "slots (the wrapper holds all three in the ALONE window): $(slots)"
if [ "${T0_ALLOW_BUSY:-0}" != 1 ] && [ "$(quiet || true)" != 0 ]; then
  echo "NOT ALONE: a test runner is alive; refusing (T0_ALLOW_BUSY=1 overrides for a rehearsal)"; exit 4
fi
df / | tail -1

# The mode this run is in (read by t0_analyse.py). T0_ASYNCIO_DEBUG=0 is the pre-registered rerun: no asyncio
# debug mode (neither PYTHONASYNCIODEBUG nor loop.set_debug); py-spy stays, in SAMPLING mode (--nonblocking).
export T0_ASYNCIO_DEBUG="${T0_ASYNCIO_DEBUG:-1}" T0_HEAD="$(git -C "$W" rev-parse HEAD)"
if [ "$T0_ASYNCIO_DEBUG" = 0 ]; then echo "asyncio debug mode OFF (the rerun; py-spy sampling mode only)" > "$OUT/mode.txt"
else echo "asyncio debug mode ON (the first run's mode)" > "$OUT/mode.txt"; fi
cat "$OUT/mode.txt"

# Step 4 pre-flight: can uvx fetch and attach py-spy? (Never installed; the printed error is the record.)
PROFILE=--profile
if ! timeout 120 uvx py-spy --version; then echo "py-spy UNAVAILABLE (printed above); no profile passes"; PROFILE=; fi

# Steps 3, 3b, 4. The driver stamps START/END (Europe/London, to the second) and /proc/stat steal per pass.
timeout 5400 "$W/.venv/bin/python" -I "$SCR/t0_driver.py" --root "$W" --out "$OUT" --dsn "$DSN" \
  --arms "${T0_ARMS:-bench-gbm,bench-nogbm,live-gbm,live-nogbm}" \
  --rates "${T0_RATES:-25,50}" --runs "${T0_RUNS:-3}" --seconds "${T0_SECONDS:-20}" $PROFILE
rc=$?
echo "driver rc=$rc"
note "$rc"

# Step 5.
python3 -I "$SCR/t0_analyse.py" "$OUT" > "$OUT/results.md" 2>"$OUT/analyse.err"; arc=$?
echo "analyse rc=$arc"; note "$arc"
seat_procs CLOSE > "$OUT/seat-procs-close.txt"
{ echo; echo "## Seat processes at OPEN and CLOSE (rerun condition 2)"; echo '```'; cat "$OUT/seat-procs-open.txt" "$OUT/seat-procs-close.txt"; echo '```'; } >> "$OUT/results.md"
echo "pytest/vitest processes: $(quiet || true)"
echo "slots: $(slots)"
stamp "T0 end; results $OUT/results.md"
exit $rc
