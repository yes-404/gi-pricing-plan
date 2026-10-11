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
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

W, LOG, ROWS = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
BANNER, WALL_MAX_S, RSS_MAX_GIB, HARD_S = "Open  http://localhost:5173/demo", 3600.0, 15.5, 4200.0


CONTAINERS = ("gi-pricing-postgres-1", "gi-pricing-redis-1", "gi-pricing-minio-1", "gi-pricing-keycloak-1")
UNIT = {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3, "kB": 1000, "MB": 1000**2, "GB": 1000**3}
container_peak: dict[str, float] = {}      # name -> peak bytes seen
container_sum_peak = 0.0
_stop = threading.Event()


def sample_containers() -> None:
    """`docker stats --no-stream` every ~8 s (each call takes ~1-2 s): peak MemUsage per container, and
    the peak of their sum. A sample, not a cgroup peak: a spike shorter than the interval can be missed."""
    global container_sum_peak
    while not _stop.is_set():
        r = subprocess.run(["docker", "stats", "--no-stream", "--format", "{{.Name}} {{.MemUsage}}", *CONTAINERS],
                           capture_output=True, text=True, check=False)
        now = 0.0
        for line in r.stdout.splitlines():
            m = re.match(r"(\S+) ([\d.]+)(\w+) /", line)
            if m and m.group(3) in UNIT:
                b = float(m.group(2)) * UNIT[m.group(3)]
                container_peak[m.group(1)] = max(container_peak.get(m.group(1), 0.0), b)
                now += b
        container_sum_peak = max(container_sum_peak, now)
        _stop.wait(8)


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
threading.Thread(target=sample_containers, daemon=True).start()
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
_stop.set()
gib = lambda k: k / 1048576  # noqa: E731
child_max = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
print(f"DRIVER: banner_s={t_banner} total_s={wall:.1f} early_rc={early_rc} sigint_stop_rc={stop_rc}")
print(f"DRIVER: peak tree RSS sum={gib(peak_sum):.2f} GiB, largest single process={gib(peak_big):.2f} GiB, "
      f"ru_maxrss(children)={gib(child_max):.2f} GiB (sampled every 2 s; postgres/minio run in containers, not counted)")
print("DRIVER: container memory peaks (docker stats samples, ~8 s apart): "
      + ", ".join(f"{n}={v / 1024**3:.2f} GiB" for n, v in sorted(container_peak.items()))
      + f"; peak of their sum={container_sum_peak / 1024**3:.2f} GiB")
if t_banner is None:
    print(f"DRIVER: demo ended before its banner (rc {early_rc}); see {LOG}")
    sys.exit(1)
if stop_rc != 0:
    print(f"DRIVER: demo stop on SIGINT rc {stop_rc}, want 0")
    sys.exit(2)
miss = [n for n, bad in (("wall > 60 min", t_banner > WALL_MAX_S),
                         ("peak RSS > 15.5 GiB", gib(max(peak_sum, child_max)) > RSS_MAX_GIB)) if bad]
if miss:
    print(f"DRIVER: DP-2 MISS (host-process scope; the container figures above are reported beside it, scope per the ruling): {', '.join(miss)} -> STOP to the lead with these figures (fallback (D))")
    sys.exit(3)
print("DRIVER: DP-2 bounds met on host-process RSS (<= 60 min, <= 15.5 GiB); container peaks are reported above, not added")
