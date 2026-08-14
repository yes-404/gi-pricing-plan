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

Pure-Python packages (`sympy`, `mpmath`, `pydantic`) need `py3-none-any`; compiled ones
(`numpy`, `scipy`, `pydantic_core`, `xgboost`) need the matching `cp313` manylinux wheel.

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

2026-08-14 — Used for four spikes: SymPy 1.14.0 (Piecewise differentiation), XGBoost 3.4.0
(`base_margin` inclusion in `predt`), Pydantic 2.13.4 (discriminated unions and `Decimal`
to JSON Schema), and a kink-isolation follow-up. Two produced specification changes. The
`pydantic-core` version trap and the scratchpad wipe were both hit in that run.
