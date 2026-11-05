---
id: FD-1211
family: finding
title: FD-1199's teardown-abort extensions are reachable in production processes through lazy imports
status: closed
created: 2026-09-28
owner: auditor
tree: 5ec47dc46ac2f174c5d427f5558a6cb365ff8166
corrected_by: []
relates: [FD-1199, FD-1150, WK-674, SL-1258, LG-1792, SL-1689, LG-2017, PL-2016]
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

~~***Resolved 2026-11-05*** — closed in place 2026-11-05 by the auditor (aud-fdclose), on the lead's brief under to-lead "2026-11-05 09:40:57 GMT" item 8 (2), the FD-1842 form. Delivered remedy (the Disposition's event: WK-674's restart and shutdown design states whether the processes finalize or recycle, and a test of a process that loads the extensions and exits shows the result): WK-674 Slice 4, SL-1258 (LG-1792), PR #1337, squash commit eea416cab3c698a12bfc1f3620af0bc7906e4587, merged 2026-10-18T08:55:12Z. The design is stated in `deploy/docker-compose.yml:146-149` ("FINALIZE, then REPLACE", `stop_grace_period: 20s`) and `deploy/README.md:146`. `backend/tests/test_deploy_shutdown.py::test_a_process_that_loads_the_extensions_exits_cleanly_every_time` runs 25 fresh interpreters that import numpy, scipy, polars, sklearn, pandas, pyarrow, numexpr, glum, xgboost, lightgbm and the worker's model handlers and asserts every exit code is 0; `test_the_check_reports_an_abort_at_exit` plants `os.abort()` and expects -6 twice. Caveat: this is interpreter level, not a SIGTERM to a served API or worker, which the essay's own "Not proven" paragraph did not ask for in its event.~~

**PARTIAL, reopened 2026-11-05** (to-lead "2026-11-05 10:13:12 GMT"): the remedy is a served process ending cleanly on SIGTERM; an interpreter-level exit test does not prove it. The limb still owing is the essay's own: "**Not proven:** that a long-lived API or worker process ever reaches interpreter finalization while those native threads run, through graceful shutdown or worker recycling." The served-process test is a small code item (<= 1 h) for the second code list; FD-1199, routed to that test, stays PARTIAL with it.

***Resolved 2026-11-05*** — the PARTIAL limb is closed in place 2026-11-05 by the auditor, as the closing act of the mint of SL-1689 (WK-674, LG-2017, PL-2016; ~~this PR, its number and squash written at the merge's date-of-record~~ [`<the merge's PR>`]), on the lead's amendment of 2026-11-05 10:32:58 GMT (to-lead "2026-11-05 10:31:31 GMT" (C)(1)). The limb owing was "that a long-lived API or worker process ever reaches interpreter finalization while those native threads run, through graceful shutdown". Delivered: `backend/tests/test_deploy_stack_runtime.py::test_a_served_process_with_its_extensions_loaded_ends_cleanly_on_sigterm` starts `api` and `worker-compute` in the built image with FD-1199's extensions preloaded (sklearn, pandas, pyarrow, numexpr, glum, xgboost, lightgbm; each container prints `PRELOADED …`, asserted), stops each with `compose stop -t 20` (SIGTERM, python as PID 1) and reads the exit code from `docker inspect`, N = 10 per service (DP-211), asserting exit code 0 and no `Fatal Python error`. **A guard, not a red:** the slice changes nothing in a served process, so the test is green at the base too; it was not run there, and FD-1211 at the base is not measurable, so no red row is claimed. The record is the rerun with lightgbm loaded (the first run, 11:39, lacked it because the image lacked `libgomp.so.1`; see FD-2018): `api: 10 SIGTERM stops, problems=[]`, `worker-compute: 10 SIGTERM stops, problems=[]`, `2 passed in 1100.95s`, rc=0 (LG-2017, `fd1211b.log`, image of `637952ae`). Broken-input proof in the same run: a container that aborts in its SIGTERM handler is reported, `worker-compute: 1 SIGTERM stops, problems=['… exit code 139 (134 is the FD-1199 abort), not 0']`. The reasoning the essay left open is now a measurement: as PID 1, uvicorn and celery finalize and exit 0. **Scope:** `api` and `worker-compute` only (the three other worker pools and the scheduler share the entrypoint and were not stopped), SIGTERM only (worker recycling is not exercised); the essay's own event named "graceful shutdown or worker recycling" and the second is not shown. **Accepted at this scope** (the lead's adoption of the audit): `api` and `worker-compute`, SIGTERM; worker recycling and the three other worker pools are not exercised.
