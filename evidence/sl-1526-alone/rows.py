"""SL-1526 ALONE stage b: the SAME seeded rows for both 11(b) columns (PL-1525 Acceptance 11 (b), :371-376).

  rows.py export <slice worktree> <rows> <out csv>   write the slice seed's own `build_csv(rows)` bytes
  rows.py seed   <base tree dir> <csv> <rows>        run the BASE tree's seed.py with its `build_csv` replaced
                                                     by that file, so it ingests exactly the slice's rows
Both print `ROWSET sha256=<csv bytes> n=<data rows> ids_sha256=<sha256 of the sorted IDpol list>`, the proof
the two columns see one row set (the run script compares the two lines). The base seed's recipe, split, GLM
spec and fit are untouched: only the sampler's output is substituted.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import sys
from pathlib import Path


def rowset(data: bytes) -> str:
    ids = sorted(r["IDpol"] for r in csv.DictReader(io.StringIO(data.decode("utf-8"))))
    return (f"ROWSET sha256={hashlib.sha256(data).hexdigest()} n={len(ids)} "
            f"ids_sha256={hashlib.sha256(chr(10).join(ids).encode()).hexdigest()}")


def load_seed(tree_example_dir: Path):  # noqa: ANN201
    sys.path.insert(0, str(tree_example_dir))
    spec = importlib.util.spec_from_file_location("seed", tree_example_dir / "seed.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["seed"] = mod
    spec.loader.exec_module(mod)
    return mod


mode = sys.argv[1]
if mode == "export":
    data = load_seed(Path(sys.argv[2]) / "examples" / "fremtpl2").build_csv(int(sys.argv[3]))
    Path(sys.argv[4]).write_bytes(data)
    print("slice " + rowset(data))
elif mode == "seed":
    data = Path(sys.argv[3]).read_bytes()
    print("base  " + rowset(data))
    seed = load_seed(Path(sys.argv[2]) / "examples" / "fremtpl2")
    seed.build_csv = lambda rows: data  # the base seed's `run` calls the module-level name
    sys.argv = ["seed.py", "--rows", sys.argv[4]]
    sys.exit(seed.main())
else:
    sys.exit(f"unknown mode {mode}")
