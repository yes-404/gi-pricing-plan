"""Log (and ignore) SIGTERM with the sender's pid and cmdline.

Two spike runs were SIGTERMed from outside (11:52 and 11:57 BST), workers included, which
points to a pattern kill on the shared box. The spike stops its own workers with SIGINT, so a
SIGTERM is never ours.
"""

from __future__ import annotations

import os
import signal
import threading
import time
from pathlib import Path

LOG = Path(__file__).with_name("sigterm.log")


def install(who: str) -> None:
    signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM})

    def watch() -> None:
        while True:
            info = signal.sigwaitinfo({signal.SIGTERM})
            try:
                cmd = Path(f"/proc/{info.si_pid}/cmdline").read_bytes().replace(b"\0", b" ")[:300]
                cwd = os.readlink(f"/proc/{info.si_pid}/cwd")
            except OSError:
                cmd, cwd = b"<gone>", "<gone>"
            with LOG.open("a") as f:
                f.write(f"{time.strftime('%T')} {who} pid={os.getpid()} got SIGTERM from "
                        f"pid={info.si_pid} uid={info.si_uid} cwd={cwd} cmd={cmd.decode(errors='replace')}\n")

    threading.Thread(target=watch, daemon=True).start()
