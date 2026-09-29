---
id: FD-1211
family: finding
title: FD-1199's teardown-abort extensions are reachable in production processes through lazy imports
status: active
created: 2026-09-28
owner: auditor
tree: 5ec47dc46ac2f174c5d427f5558a6cb365ff8166
corrected_by: []
relates: [FD-1199, FD-1150, WK-674]
---

# FD-1211 — FD-1199's teardown-abort extensions are reachable in production processes through lazy imports

**Severity: low.** The auditor filed this finding on 2026-09-28, on the lead's instruction and the
deputy's condition 3 on `FD-1199` (his entry of 21:39:25 BST: *"do the API and worker processes
import any of the extensions in Arm B's module list? … If they do, open an FD for a shutdown abort
in production processes, owner WK-674"*). It is low because the abort in `FD-1199` fires only at
interpreter finalization, after the work is done, and this record cannot show that a long-lived
process ever finalizes while those native threads run.

## Finding

`FD-1199`'s abort has the extension list `numpy, scipy, sklearn, pyarrow, pandas, numexpr` (157
modules). Eager start of the API and worker loads **none** of sklearn, pandas, pyarrow or numexpr.
The worker's model jobs, and possibly the API's prediction path, load them through function-level
imports. So the extensions in that list are reachable in production processes, and a shutdown
abort of the same kind is possible there.

## Evidence

At `origin/main` `5ec47dc4`, in a detached tree after `uv sync --all-packages`:

- **Eager import, every module.** The command
  `python -c "import sys, pkgutil, importlib, app; from app.main import create_app; create_app(); [importlib.import_module(m.name) for m in pkgutil.walk_packages(app.__path__, 'app.')]; print(sorted({m.split('.')[0] for m in sys.modules} & {'sklearn','scipy','pandas','pyarrow','numexpr','xgboost','lightgbm','glum','zen','polars','numpy'}))"`
  printed `['numpy', 'polars', 'scipy', 'zen']`. Separate `create_app()` runs, with and without the worker's
  modules imported, printed the same set. No module failed to import. This is an import of
  the code, **not a served API or a running worker**.
- **The lazy imports** are inside functions: `pricing_core/modelling/glm.py:283` (glum),
  `bandings.py:314` (sklearn), and `gbm.py:856`, `:1016`, `:1216`, `:1227` and later
  (xgboost, lightgbm), with `diagnostics.py:777` and `:794`.
- **What they load.** The command
  `python -c "import sys; import pricing_core.modelling.glm, pricing_core.modelling.bandings; from glum import GeneralizedLinearRegressor; from sklearn.tree import DecisionTreeRegressor; import xgboost, lightgbm; print(sorted({m.split('.')[0] for m in sys.modules} & {'sklearn','scipy','pandas','pyarrow','numexpr','xgboost','lightgbm','glum'}))"`
  printed `['glum', 'lightgbm', 'numexpr', 'pandas', 'pyarrow', 'scipy', 'sklearn', 'xgboost']`.
- **Who reaches the lazy paths.** The worker: `backend/src/app/worker/model_handlers.py:304`
  imports the fit functions inside the handler, and `:416` imports the diagnostics. Those handlers
  call the functions that hold the lazy imports above.
- **The API is less clear.** `backend/src/app/platform/prediction.py:226`, `:324`, `:455` and
  `:502` import `pricing_core.modelling` inside functions. Importing `pricing_core.modelling` and
  `pricing_core.modelling.predict` loads only `scipy` (measured). Whether a prediction request
  loads xgboost or the rest depends on how the fitted model is deserialized, which this record did
  not trace. The API's reach is **possible, not shown**.
- **The scoring path does not reach them.** The eager list contains `zen`, `numpy`, `scipy` and
  `polars` only, and `FD-1199`'s child imported sklearn and pandas through the test module
  `test_rating_runtime`, which imports `xgboost` and `pricing_core.modelling.gbm`.

**Not proven:** that a long-lived API or worker process ever reaches interpreter finalization while
those native threads run, through graceful shutdown or worker recycling. It is also not proven that
any worker job, when run, prints those modules in a live process. Arms C and D of `FD-1199`, run on
executor-s1's fix, are pending and do not test a served process.

## Disposition

**Deferred with an owner — WK-674**, deployment and restart behaviour, by the deputy's condition
3. Event: WK-674's restart and shutdown design states whether workers and the API finalize the
interpreter on stop or recycle, and a test of a process that loads the extensions and then exits
shows the result. Until then the risk is a shutdown abort after work is done, not a wrong result.
