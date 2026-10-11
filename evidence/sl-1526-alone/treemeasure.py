"""SL-1526 ALONE stage d verdict: run a command, sample its process tree, judge DP-2.

Usage: treemeasure.py <label> <log> <wall-key> <wall-max-s> <rss-max-gib> -- <command...>
The command's stdout/stderr go to <log>. The DP-2 VERDICT (maintainer, to-lead "2026-10-11 16:34:21 BST") is the
process tree that runs the dislocation and attribution: its peak RSS (sampled every 2 s) against <rss-max-gib>
and its job wall against <wall-max-s>. The wall is read from the command's own `<wall-key> <seconds>` line (the
job's START to END, excluding setup); if absent the whole process wall is used and said so. Container peaks and
the host+containers SUM are PRINTED, not judged. Exit: 0 within bounds; 3 MISS (prints the fallback line);
4 the command itself failed (rc printed; its own STOP line stands).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sampler import GIB, ContainerPeaks, tree_rss_kib  # noqa: E402

label, log, key, wall_max, rss_max = sys.argv[1], Path(sys.argv[2]), sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
cmd = sys.argv[sys.argv.index("--") + 1:]
cp = ContainerPeaks()
cp.start()
t0 = time.monotonic()
peak_sum = peak_big = 0
with log.open("wb") as out:
    proc = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT)
    while proc.poll() is None:
        s, b = tree_rss_kib(proc.pid)
        peak_sum, peak_big = max(peak_sum, s), max(peak_big, b)
        time.sleep(2)
rc = proc.returncode
proc_wall = time.monotonic() - t0
cp.stop()
text = log.read_text(errors="replace")
m = re.search(rf"^{re.escape(key)} ([\d.]+)", text, re.M)
wall, wall_src = (float(m.group(1)), f"the job's own {key} line") if m else (proc_wall, "the whole process (no job-wall line)")
rss_gib = peak_sum / 1048576
print(f"TREEMEASURE {label}: rc={rc} process_wall_s={proc_wall:.1f}; judged wall={wall:.1f} s from {wall_src}")
print(f"TREEMEASURE {label}: process-tree RSS (sampled every 2 s) peak sum={rss_gib:.2f} GiB, largest single process={peak_big / 1048576:.2f} GiB")
print(f"TREEMEASURE {label}: " + cp.line())
print(f"TREEMEASURE {label}: SUM host tree peak + container sum peak = {rss_gib + cp.sum_peak / GIB:.2f} GiB "
      "(PROVISIONAL upper bound, printed not judged; in-process dislocation, not a Celery worker)")
if rc != 0:
    print(f"TREEMEASURE {label}: the command failed (rc {rc}); see {log}")
    sys.exit(4)
miss = [n for n, bad in ((f"wall {wall:.0f} s > {wall_max:.0f} s", wall > wall_max),
                         (f"peak RSS {rss_gib:.2f} GiB > {rss_max} GiB", rss_gib > rss_max)) if bad]
if miss:
    print(f"TREEMEASURE {label}: DP-2 MISS: {'; '.join(miss)}")
    print("DP-2 MISS -> fallback (D); SL-1575 need")
    sys.exit(3)
print(f"TREEMEASURE {label}: DP-2 bounds met (wall <= {wall_max:.0f} s, peak RSS <= {rss_max} GiB)")
