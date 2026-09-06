---
name: library-spike
description: Empirically verify a Python library's behaviour in this environment, where pip and ensurepip are unavailable. Use when a specification assumption depends on how a library actually behaves — XGBoost offsets, SymPy differentiation, Pydantic schema generation, Polars memory — and documentation is ambiguous or silent. Covers fetching wheels without pip, the version-pinning trap, and turning a spike result into a specification change.
---

# Running a library spike

Prefer a spike over a documentation reading whenever a spec requirement depends on
behaviour the docs do not state explicitly. Library behaviour also changes between
versions, so a spike result should usually become a **runtime assertion**, not just a
sentence in a spec.

## This environment has no pip

`python3 -m pip` and `ensurepip` are both absent, but **PyPI is reachable**. Fetch wheels
directly and put them on `PYTHONPATH`:

```bash
SP="$CLAUDE_SCRATCHPAD"   # or the session scratchpad path
python3 - <<'PY'
import json, urllib.request, os, zipfile, io
libs = "SCRATCHPAD/libs"; os.makedirs(libs, exist_ok=True)
pure  = lambda f: f.endswith("py3-none-any.whl")
cp313 = lambda f: "cp313-cp313" in f and "manylinux" in f and "x86_64" in f and "musl" not in f
for pkg, pred in {"sympy": pure, "mpmath": pure, "numpy": cp313}.items():
    d = json.load(urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=60))
    u = next(u for u in d["urls"] if u["packagetype"]=="bdist_wheel" and pred(u["filename"]))
    zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(u["url"], timeout=900).read())).extractall(libs)
    print(pkg, d["info"]["version"])
PY
PYTHONPATH="$SP/libs" python3 spike.py
```

Pure-Python packages (`sympy`, `mpmath`, `pydantic`, `narwhals`) need `py3-none-any`;
compiled ones (`numpy`, `scipy`, `pydantic_core`, `xgboost`, `lightgbm`) need the matching
manylinux wheel — note `lightgbm` ships as `py3-none-manylinux`, not `cp313`.

**A tool's own dependencies are not optional.** `mypy` 2.x imports `librt` and
`ast-serialize`; fetching only the `mypy` wheel gives `ModuleNotFoundError: No module
named 'librt'`, which reads like a broken wheel but is a missing dependency. Read
`requires_dist` from the PyPI JSON and fetch what it names, rather than guessing:

```python
d = json.load(urllib.request.urlopen("https://pypi.org/pypi/mypy/json"))
print(d["info"]["requires_dist"])   # librt, ast-serialize, pathspec, mypy_extensions …
```

The compiled (`cp313`) and pure (`py3-none-any`) wheels of the same package can differ in
what they need — try the pure one when the compiled one will not load.

**Missing system libraries.** A wheel may import fine and then fail on a shared object the
OS does not have — `lightgbm` needs `libgomp.so.1` (OpenMP), which is absent here. Rather
than give up, check whether another wheel already bundled it:

```bash
find "$SP/libs" -name '*.so*' | grep -i omp        # xgboost.libs/libgomp-<hash>.so.1.0.0
mkdir -p "$SP/nativelibs"
ln -sf "$SP/libs/xgboost.libs/libgomp-e985bcbb.so.1.0.0" "$SP/nativelibs/libgomp.so.1"
LD_LIBRARY_PATH="$SP/nativelibs" PYTHONPATH="$SP/libs" python3 spike.py
```

manylinux wheels vendor their native dependencies into a `<pkg>.libs/` directory with a
hash-suffixed filename; symlinking to the unsuffixed soname makes it loadable by any other
package. **Transitive Python deps bite the same way** — `lightgbm` needs `narwhals`, which
nothing else pulled in. Expect two or three rounds of "import, read the error, fetch one
more wheel"; that is normal, not a sign the approach is wrong.

**The version trap:** fetching "latest" for every package breaks pinned pairs. `pydantic`
2.13.4 requires `pydantic-core` **2.46.4** exactly and raises `SystemError` against 2.48.0.
Pin the dependency explicitly via `https://pypi.org/pypi/<pkg>/<version>/json`.

The scratchpad is **not durable** — it can be wiped between turns. Re-fetching is cheap;
keep the fetch script alongside the spike.

## Writing the spike

- Take the artifact **exactly as the spec writes it**, so the result is about the spec and
  not about a paraphrase.
- Assert the spec's claim explicitly rather than eyeballing output.
- When a check fails, isolate *why* before believing it — a failure can be an artefact of
  the measurement rather than a defect. A finite-difference check across a discontinuity
  fails at any step size, and that is the check being wrong, not the derivative.

## Landing the result

1. Write it up in `docs/research/` with sources, method, and the version tested.
2. Apply it: use `spec-change` for requirements, `adr-write` for an addendum.
3. Update the affected `docs/open-questions.md` rows and mark verified rows in
   `docs/skills-map.md`.
4. Sweep for claims the finding made stale (`grep -rn "highest-risk" docs/`).
5. `python3 scripts/audit-docs.py`

## Verified

2026-08-14 — Used for six spikes: SymPy 1.14.0 (Piecewise differentiation), XGBoost 3.4.0
(`base_margin` inclusion in `predt`), Pydantic 2.13.4 (discriminated unions and `Decimal`
to JSON Schema), a kink-isolation follow-up, and **spike S3** (LightGBM 4.7.0 `init_score`
symmetry, which found a real asymmetry → FR-129). **Three produced specification
changes.**

Every trap documented above was hit for real in those runs: the `pydantic-core` version
pin, the scratchpad being wiped mid-session, `lightgbm`'s missing `libgomp.so.1` (solved by
borrowing XGBoost's bundled copy), and `narwhals` as an unexpected transitive dependency.

The S3 run also demonstrates why the "take the artifact exactly as the spec writes it" rule
matters: the contract *claimed* symmetry between two backends, and only running both side
by side against the same assertion showed it held at fit time and failed at scoring time.
