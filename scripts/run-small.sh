#!/bin/bash
# run-small.sh — a seat's targeted test run beside a held CODE gate (RL-1626).
#
#   scripts/run-small.sh <worktree> <target> [<target> [<target>]]
#
# A <target> is a test file, or one pytest node id: <file>::<test>, <file>::<test>[<param>] or
# <file>::<Class>::<test>. The file part of every target passes every check below; an option (-k
# included) is still refused. Runs `uv run --directory <worktree> pytest -q <targets>` under `nice -n 19 ionice -c3`, inside the
# small-test flock, and exits with pytest's own exit code. The command line is fixed, not a free
# argument: that is what makes "at most 3 named files" and "never alembic" enforceable here rather
# than a request to the caller. A full suite, a directory, a pytest option or a migration is a gate's
# work, not this script's. Exit code: pytest's own. A run that ran NO test (pytest exit 5: nothing
# collected; exit 4: a node id it could not find) is an error, and the script says so on stderr.
#
# Refusals (the script never reaches pytest):
#   64 usage: no worktree, or no test file          65 the caller's shell exports GIP_GATE_SLOT
#   66 load1 is not below 6 (refused, not waited)    67 an argument names alembic
#   68 more than 3 targets                           71 an argument is not an existing .py file
#   72 a test file resolves (realpath) outside <worktree>
#   73 a .py file is not named test_*.py or *_test.py (pytest's default python_files; conftest.py is refused)
#   75 the small-test flock stayed held for the whole wait (flock's own -E code, clear of pytest's 0-5)
#
# The flock path, the load source and the wait are fixed constants below: no environment variable moves
# them, because a hook a seat can set is a bypass of refusals 66 and the one-at-a-time flock. The test
# (backend/tests/test_run_small_script.py) runs a sed-patched COPY of this file instead.
set -u
slot=/tmp/slots/small-test
loadavg=/proc/loadavg
wait_s=7200

if [ $# -lt 2 ]; then
  echo "usage: run-small.sh <worktree> <test-file>… (1 to 3 test files or node ids)" >&2; exit 64
fi
if [ -n "${GIP_GATE_SLOT:-}" ]; then
  echo "run-small: GIP_GATE_SLOT is set in the calling shell — seat shells never export it. Unset it." >&2; exit 65
fi
for a in "$@"; do
  case ${a,,} in *alembic*)
    echo "run-small: refused, '$a' names alembic — a schema migration waits for a gate gap (RL-1626 (d))." >&2; exit 67 ;;
  esac
done
wt=$1; shift
[ -d "$wt" ] || { echo "run-small: not a directory: $wt" >&2; exit 64; }
if [ $# -gt 3 ]; then
  echo "run-small: refused, $# files given; at most 3 test files (more is a gate's work)." >&2; exit 68
fi
wtr=$(realpath "$wt")
for f in "$@"; do
  fp=${f%%::*}
  case $fp in /*) p=$fp ;; *) p=$wt/$fp ;; esac
  case $f in -*) ;; *.py::|*::) ;; *) case $fp in *.py) [ -f "$p" ] && continue ;; esac ;; esac
  echo "run-small: refused, not a test file: $f (name 1 to 3 existing .py files or <file>.py::<test> node ids, no directory, no option)." >&2; exit 71
done
for f in "$@"; do
  fp=${f%%::*}
  case $fp in /*) p=$fp ;; *) p=$wt/$fp ;; esac
  case $(basename "$p") in test_*.py|*_test.py) ;; *)
    echo "run-small: refused, not named as a test file: $f (test_*.py or *_test.py; conftest.py and helpers are not tests)." >&2; exit 73 ;;
  esac
  case $(realpath "$p") in "$wtr"/*) ;; *)
    echo "run-small: refused, $f resolves outside the worktree $wt." >&2; exit 72 ;;
  esac
done
load=$(cut -d' ' -f1 "$loadavg")
if ! awk -v l="$load" 'BEGIN{exit !(l < 6)}'; then
  echo "run-small: refused, load1 $load is not below 6 (RL-1626 (c)); retry when the box is quieter." >&2; exit 66
fi
echo "run-small: waiting for $slot at $(TZ=Europe/London date '+%T') (load $load)" >&2
flock -w "$wait_s" -E 75 "$slot" env GIP_GATE_SLOT="$slot" nice -n 19 ionice -c3 \
  uv run --directory "$wt" pytest -q "$@"
rc=$?
case $rc in 4|5)
  echo "run-small: NO TEST RAN (pytest exit $rc: the selection matched nothing, or a node id was not found). That is an error, never a pass." >&2 ;;
esac
exit "$rc"
