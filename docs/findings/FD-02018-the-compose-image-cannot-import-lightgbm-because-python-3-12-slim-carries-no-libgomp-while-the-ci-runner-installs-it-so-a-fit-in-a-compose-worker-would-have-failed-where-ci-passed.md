---
id: FD-2018
family: finding
title: The compose image cannot import lightgbm because python:3.12-slim carries no libgomp, while the CI runner installs it, so a fit in a compose worker would have failed where CI passed
status: closed
created: 2026-11-05
owner: auditor
tree: 81b0bb869439efd929e2599da9373fac19039eda
corrected_by: []
relates: [WK-674, SL-1689, LG-2017, PL-2016, FD-1211, FR-432]
---

# FD-2018 — the compose image cannot import lightgbm: no libgomp in `python:3.12-slim`

## Finding

**MEDIUM; owner WK-674; closed in the PR that filed it.** Source: found in the SL-1689 build window 2 (the FD-1211 proof) and ruled (a) in this slice by lead 30, brief amendment 2026-11-05 10:53:50 GMT, on to-lead "2026-11-05 10:53:32 GMT". `deploy/Dockerfile` is `FROM python:3.12-slim` and installed no system library. `lightgbm` links OpenMP and needs `libgomp.so.1` at import. In the built image `import lightgbm` raised `OSError: libgomp.so.1: cannot open shared object file: No such file or directory`, so a compose `worker-compute` or `worker-scoring` handling a LightGBM fit or prediction could not even load the backend. `xgboost`, `glum` and `interpret` imported.

## Evidence

- **The CI / image divergence.** The Python CI runner is an ubuntu image that installs system libraries the slim base lacks (libgomp among them), so every test that imports `lightgbm` runs there. The compose image is the one place the platform runs without that layer, and no test imported a model backend *in the built image*. The suite was green where the product was not. The compose gate's runtime tests ran the API and the workers, but no job in them fits a LightGBM model, so nothing reached the import.
- **Red, by cause** (LG-2017, `img-red.log`, `head=b516697f`): `test_the_built_image_imports_every_declared_model_backend` runs `docker run --rm --entrypoint python gi-pricing-app:<sha> -c "import <module>"` for `lightgbm`, `xgboost`, `glum`, `interpret`, one process each: `1 failed in 28.74s`, `{'lightgbm': 'OSError: libgomp.so.1: cannot open shared object file: No such file or directory'}`. Only `lightgbm` failed, so the red is by cause.
- **Fix** `637952ae`: `deploy/Dockerfile`, runtime stage, `apt-get update && apt-get install --no-install-recommends -y libgomp1 && rm -rf /var/lib/apt/lists/*`, before the `uv` copy. Green on the rebuilt image: `1 passed in 94.58s`, rc=0 (`img-green.log`, `head=637952ae`). lightgbm is back in FD-1211's preload, and FD-1211's 20-stop rerun ran with it loaded.

## Lasting guard

The image-import test above stays in `backend/tests/test_deploy_stack_runtime.py` (marked `req("FR-432")`, behind `GIP_DEPLOY_TESTS`), so it runs in the compose gate on every `deploy/**` change and on any later change of a model backend list. Its list `_BACKENDS` is a hand-written copy of the declared backends: a backend added to the platform and not to the list is not guarded; closing that gap (deriving the list from the package metadata) is not done here. It is also skipped in PR CI (no docker daemon, `GIP_DEPLOY_TESTS` unset), so the guard is the gate's, not CI's.

## Disposition

Closed in the PR that filed it: owner WK-674; the event that discharged it is SL-1689's merge (`<the merge's PR>`), the fix `637952ae` with its red-first image-import test.

***Resolved 2026-11-05*** — closed in place 2026-11-05 by the auditor, as the closing act of the mint of SL-1689 (WK-674, LG-2017, PL-2016; ~~this PR, its number and squash written at the merge's date-of-record~~ [`<the merge's PR>`]). Delivered remedy: `libgomp1` in the image, with the red-first image-import test above; evidence in LG-2017.
