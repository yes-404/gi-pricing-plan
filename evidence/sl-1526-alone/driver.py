"""SL-1526 ALONE stage a: Acceptance 8's `scripts/demo.py --rows 20000`, timed and memory-sampled.

Usage: driver.py <slice worktree> <demo log> <rows>
`demo.py` never exits by itself: after it prints the banner (`Open  http://localhost:5173/demo`) it waits
for Ctrl-C. So: start it, time it to the banner, sample the whole process tree's RSS every 2 s, then send
SIGINT (the documented way to stop it) and take its exit code. Exit: 0 ok; 1 demo ended before its banner;
2 stop on SIGINT nonzero. Under the 16:34:21 BST ruling DP-2 is NOT judged here (demo.py runs no dislocation
run): the figures are PRINTED, including the host+containers SUM (the README's measured machine requirement,
which goes to SL-1527).
"""
from __future__ import annotations

import os
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sampler import GIB, ContainerPeaks, tree_rss_kib  # noqa: E402

W, LOG, ROWS = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
BANNER, HARD_S = "Open  http://localhost:5173/demo", 4200.0

t0 = time.monotonic()
cp = ContainerPeaks()
cp.start()
with LOG.open("wb") as out:
    proc = subprocess.Popen([str(W / ".venv/bin/python"), str(W / "scripts/demo.py"), "--rows", ROWS],
                            stdout=out, stderr=subprocess.STDOUT, cwd=W)
    peak_sum = peak_big = 0
    t_banner = None
    while proc.poll() is None and time.monotonic() - t0 < HARD_S:
        s, b = tree_rss_kib(proc.pid)
        peak_sum, peak_big = max(peak_sum, s), max(peak_big, b)
        if t_banner is None and BANNER in LOG.read_text(errors="replace"):
            t_banner = time.monotonic() - t0
            break
        time.sleep(2)
    early_rc = proc.poll()
    stop_rc = None
    if early_rc is None:
        proc.send_signal(signal.SIGINT)
        try:
            stop_rc = proc.wait(timeout=90)
        except subprocess.TimeoutExpired:
            proc.terminate()
            stop_rc = proc.wait(timeout=30)
            print("DRIVER: demo ignored SIGINT for 90 s; terminated")
wall = time.monotonic() - t0
cp.stop()
child_max = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
print(f"DRIVER: banner_s={t_banner} total_s={wall:.1f} early_rc={early_rc} sigint_stop_rc={stop_rc}")
print(f"DRIVER: host process tree RSS (sampled every 2 s) peak sum={peak_sum / 1048576:.2f} GiB, "
      f"largest single process={peak_big / 1048576:.2f} GiB, ru_maxrss(children)={child_max / 1048576:.2f} GiB")
print("DRIVER: " + cp.line())
print(f"DRIVER: SUM host peak + container sum peak = {peak_sum * 1024 / GIB + cp.sum_peak / GIB:.2f} GiB "
      "(an upper bound: the two peaks need not coincide). PRINTED, not judged against DP-2 (16:34:21 ruling).")
if t_banner is None:
    print(f"DRIVER: demo ended before its banner (rc {early_rc}); see {LOG}")
    sys.exit(1)
if stop_rc != 0:
    print(f"DRIVER: demo stop on SIGINT rc {stop_rc}, want 0")
    sys.exit(2)
