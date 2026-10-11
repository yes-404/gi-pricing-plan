"""SL-1526 ALONE stage a: Acceptance 8's `scripts/demo.py --rows 20000`, timed and memory-sampled.

Usage: driver.py <slice worktree> <demo log> <rows>
`demo.py` never exits by itself: after it prints the banner (`Open  http://localhost:5173/demo`) it waits
for Ctrl-C. So: start it, time it to the banner, sample the whole process tree's RSS every 2 s, then send
SIGINT (the documented way to stop it) and take its exit code. Exit: 0 pass; 1 demo ended before its banner
(rc printed); 2 stop on SIGINT nonzero; 3 DP-2 miss (wall > 60 min or peak RSS > 15.5 GiB).
"""
from __future__ import annotations

import os
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path

W, LOG, ROWS = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
BANNER, WALL_MAX_S, RSS_MAX_GIB, HARD_S = "Open  http://localhost:5173/demo", 3600.0, 15.5, 4200.0


def tree_rss_kib(root: int) -> tuple[int, int]:
    """(sum, largest) VmRSS in KiB over `root` and its descendants, from /proc."""
    kids: dict[int, list[int]] = {}
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                stat = Path(f"/proc/{d}/stat").read_text()
                kids.setdefault(int(stat.rsplit(")", 1)[1].split()[1]), []).append(int(d))
            except OSError:
                pass
    todo, total, big = [root], 0, 0
    while todo:
        p = todo.pop()
        todo += kids.get(p, [])
        try:
            for line in Path(f"/proc/{p}/status").read_text().splitlines():
                if line.startswith("VmRSS:"):
                    kib = int(line.split()[1])
                    total, big = total + kib, max(big, kib)
        except OSError:
            pass
    return total, big


t0 = time.monotonic()
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
gib = lambda k: k / 1048576  # noqa: E731
child_max = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
print(f"DRIVER: banner_s={t_banner} total_s={wall:.1f} early_rc={early_rc} sigint_stop_rc={stop_rc}")
print(f"DRIVER: peak tree RSS sum={gib(peak_sum):.2f} GiB, largest single process={gib(peak_big):.2f} GiB, "
      f"ru_maxrss(children)={gib(child_max):.2f} GiB (sampled every 2 s; postgres/minio run in containers, not counted)")
if t_banner is None:
    print(f"DRIVER: demo ended before its banner (rc {early_rc}); see {LOG}")
    sys.exit(1)
if stop_rc != 0:
    print(f"DRIVER: demo stop on SIGINT rc {stop_rc}, want 0")
    sys.exit(2)
miss = [n for n, bad in (("wall > 60 min", t_banner > WALL_MAX_S),
                         ("peak RSS > 15.5 GiB", gib(max(peak_sum, child_max)) > RSS_MAX_GIB)) if bad]
if miss:
    print(f"DRIVER: DP-2 MISS: {', '.join(miss)} -> STOP to the lead with these figures (fallback (D))")
    sys.exit(3)
print("DRIVER: DP-2 bounds met (<= 60 min, <= 15.5 GiB)")
