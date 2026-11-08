---
id: FD-2102
family: finding
title: numpy is imported by 19 source files and declared in no pyproject dependency line, the state pricing-core's own comment calls the pandera state
status: active
created: 2026-11-08   # original date 2026-11-08, set at the draft; minted 2026-11-08
owner: auditor
tree: 374a22bf33ad
corrected_by: []
relates: [FD-2034]
---

# FD-2102 — numpy is imported by 19 source files and declared in no pyproject dependency line

*(Minted 2026-11-08 as FD-2102 from working id 8416, born open, filed 2026-11-08 by the auditor on the skills-gap review's finding F10 and the §14 review accepted at to-lead "2026-11-08 09:02:21 GMT". Severity LOW. Owner Work: P3-D.)*

## Finding

`numpy` is imported directly by source code and is not named by any `pyproject.toml` dependency line; it arrives only through other packages' requirements. `packages/pricing-core/pyproject.toml:50` already calls this state by name: "relying on a transitive dependency is the pandera state `01` found in reverse". The same review found `redis` (4 files) in the same state, arriving through `celery[redis]`; `starlette` (4), `pydantic_core` (3) and `botocore` (1) were also listed. This record is about `numpy`; the others are for the owning Work's first act, which also decides whether to declare them.

## Evidence

Two counts, at tree `374a22bf33ad`, each with its corpus and predicate.

- **19 files** — corpus: `packages/*/src/*` and `backend/src/*`. Predicate: `git grep -l -E '^\s*(import numpy|from numpy)\b' 374a22bf33ad -- 'packages/*/src/*' 'backend/src/*' | wc -l` printed `19` (re-run by the auditor).
- **63 files** — corpus: every `*.py` under `packages`, `backend`, `scripts` and `tests`. Predicate: the same regex over those four trees; the auditor's re-run with `git grep -l -E '^\s*(import numpy|from numpy)\b' 374a22bf33ad -- 'packages/*.py' 'backend/*.py' 'scripts/*.py' 'tests/*.py' | wc -l` printed `63`. The two counts differ by corpus (source only against all Python), not by predicate.
- The comment: `git grep -n -i pandera 374a22bf33ad -- packages/pricing-core/pyproject.toml` finds `:50` ("the package now *imports* it: relying on a transitive dependency is the pandera") and `:51` ("state `01` found in reverse, named in four places and depended on by nothing"); the sentence is about `scikit-learn`, which `pricing-core` declares for that reason.
- The finding's source is `~/gi-pricing-plan.local/scratch/p28/skills-gap.md` (local, not committed), §3 "Imported but not declared", at its own reading of the same predicate for the `packages/*/src/*` and `backend/src/*` corpus (19).

## Disposition

**deferred with an owner: P3-D.** The Work's first act is to declare `numpy` in each package that imports it (or to rule that the workspace root pin suffices), and to decide the same for `redis`, `starlette`, `pydantic_core` and `botocore`. Whether it needs a gate check is the Work's to decide. Nothing wrong is live: the lock resolves a single `numpy`.
