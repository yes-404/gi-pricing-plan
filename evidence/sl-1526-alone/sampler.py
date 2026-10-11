"""Memory samplers shared by driver.py (stage a) and treemeasure.py (stage d).

Host side: `tree_rss_kib` sums VmRSS over a process and its descendants from /proc (called every 2 s by the
callers). Container side: `ContainerPeaks` runs `docker stats --no-stream` every ~8 s in a thread (each call
takes 1-2 s) and keeps the peak MemUsage per container and the peak of their sum. Both are SAMPLES: a spike
shorter than the interval can be missed, and the callers print the interval beside the figure.
"""
from __future__ import annotations

import os
import re
import subprocess
import threading
from pathlib import Path

CONTAINERS = ("gi-pricing-postgres-1", "gi-pricing-redis-1", "gi-pricing-minio-1", "gi-pricing-keycloak-1")
UNIT = {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3, "kB": 1000, "MB": 1000**2, "GB": 1000**3}
GIB = 1024**3


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


class ContainerPeaks:
    def __init__(self) -> None:
        self.peak: dict[str, float] = {}
        self.sum_peak = 0.0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        while not self._stop.is_set():
            r = subprocess.run(["docker", "stats", "--no-stream", "--format", "{{.Name}} {{.MemUsage}}",
                                *CONTAINERS], capture_output=True, text=True, check=False)
            now = 0.0
            for line in r.stdout.splitlines():
                m = re.match(r"(\S+) ([\d.]+)(\w+) /", line)
                if m and m.group(3) in UNIT:
                    b = float(m.group(2)) * UNIT[m.group(3)]
                    self.peak[m.group(1)] = max(self.peak.get(m.group(1), 0.0), b)
                    now += b
            self.sum_peak = max(self.sum_peak, now)
            self._stop.wait(8)

    def line(self) -> str:
        return ("container memory peaks (docker stats samples, ~8 s apart): "
                + ", ".join(f"{n}={v / GIB:.2f} GiB" for n, v in sorted(self.peak.items()))
                + f"; peak of their sum={self.sum_peak / GIB:.2f} GiB")
