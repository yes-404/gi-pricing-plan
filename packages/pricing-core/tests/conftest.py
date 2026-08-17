"""Make sibling test modules importable inside this package's test directory.

`pyproject.toml` sets `--import-mode=importlib`, which is what keeps `test_money.py` in two
packages from colliding on its basename. The cost is that a test module is no longer
importable by bare name, and `backend/tests`' way round it — `from backend.tests.test_x
import ...`, a PEP 420 namespace path from the repo root — is not available here: the
directory is `packages/pricing-core`, and `pricing-core` is not a Python identifier.

So the shared GBM fixtures live in `test_gbm.py` and this puts their directory on the path,
rather than a second copy of the data generator drifting away from the first.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
