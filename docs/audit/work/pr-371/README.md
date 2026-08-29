# Work-item record — pr-371

W11 Slice 1, Task 1.1 audit. The lead flagged one regression before I started (a patched
vendored script whose own deviation note claimed a false "additive" property) and asked for
an independent audit of the routes and tests, assuming there are others. Reported per
finding, not as a merge recommendation.

## Scope

PR #371 (branch `worktree-w11-slice1-evaluator`, author pilot-executor): wires
`POST /api/v1/rating-versions` and `POST /api/v1/rating-versions/{id}/submit` over HTTP,
gated on `Permission.RATING_WRITE`/`RATING_SUBMIT` (Task 1.1, Ruling 1). Also includes an
unrelated preparatory fix to the vendored `.claude/skills/subagent-driven-development/
scripts/task-brief`, hit while starting the task, scope-noted in the PR body and recorded
in `.claude/skills/README.md` per `CLAUDE.md` §12.

## Checklist

Slice-layer audit (`delivery-process.md` §6 step 5) against Task 1.1's own exit criteria
and "must not touch" boundary (`docs/plans/2026-08-29-w11-scoring.md`), run 2026-08-29.

## Evidence

Tree: PR #371 branch (`pr371-review` locally), head commit `5b82b18`.

- **Route wiring** (`backend/src/app/api/models.py`): both routes present, gated on the
  correct permissions; `backend/src/app/platform/rating_versions.py`
  (`create_rating_version`/`submit_for_review`'s own bodies) is absent from the diff —
  confirmed via file list — satisfying Task 1.1's "must not touch." Request DTOs
  (`RatingVersionCreate`/`RatingVersionSubmit`) follow the file's existing local-DTO
  convention (matches sibling `ModelCreate`) and reuse `ArtifactRef` from `model_schema`
  rather than hand-rolling it.
- **`docs/specs/03-rating-engine.md:513` citation** — verified directly: line 513 is the
  claimed `POST /api/v1/rating-versions` row (FR-RATE-22). The PR's "no spec edit needed"
  is correct; the frozen plan's own instruction (citing `:512`) was off-by-one and
  pre-existing (see pr-370's record) — PR #371 verified directly rather than trusting it.
- **Tests — a methodology trap caught before being reported as a finding.** Running
  `backend/tests/test_rating_versions.py` against the shared main-checkout `.venv` (to
  avoid a fresh `uv sync`) gave 2 failed / 5 passed (`POST /rating-versions` → 405). Traced
  before reporting: that venv's editable install
  (`_editable_impl_gi_backend.pth`) hardcodes `/home/puzhenhao1989/gi-pricing-plan/
  backend/src`, so it silently imported the main checkout's code — not the worktree's —
  worsened by the main checkout sitting on an unrelated branch at the time. Re-run with a
  properly isolated `uv sync --all-packages --dev` in the PR's own worktree: **7/7 passed
  genuinely**, confirming the PR's claim. (Filed as a `dev-commands` skill candidate
  separately: reusing another worktree's venv across an editable install is not safe.)
- **Full gate**, independently re-run on the isolated tree at `5b82b18`: `uv run ruff
  check .`, `uv run mypy` (146/146 source files clean), `uv run lint-imports`,
  `python3 scripts/audit-docs.py` — all exit 0.
- **The lead's reported regression** (patched vendored `task-brief` broke upstream's
  `# Task N` format, contradicting its own deviation note's "additive" claim) — confirmed
  real in the PR's history (introduced at commit `9604fe3`) and already fixed by the time
  of this audit (commit `5b82b18`, "fix(skills): task-brief's boundary rule cleared
  `intask` on upstream's own heading"), with a same-day correction paragraph appended to
  `.claude/skills/README.md` naming the root cause (an `awk` pattern-block ordering bug:
  an unconditional boundary-clear rule fired on the same line a task-match rule had just
  set, undoing it). Independently re-tested rather than trusted: wrote fresh fixtures
  (upstream `# Task N` multi-task file; this repo's `### N.M` format including the
  last-task-in-a-slice boundary and a bare non-decimal task number that must NOT match a
  decimal one) and ran the current script against all of them — every case behaves
  correctly.

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| **pr371-task-brief-regression** | Vendored script's first patch (`9604fe3`) broke upstream's own heading format; the deviation note's "additive, unchanged for existing input" claim was false and unverified at the time it was written. | already fixed by the author same day (`5b82b18`), self-corrected in `.claude/skills/README.md` with root cause named; independently re-verified here with fresh test fixtures | resolved |
| — | Routes, RBAC gating, the "must not touch" boundary, the `:513` citation, tests (7/7, genuinely), and the full gate — all independently verified with no further defect found | accept (proposed) | closed-with-findings (one, already resolved) |

## Sign-off

Not applicable — audit only. Verdict is the lead's, per `delivery-process.md` §6 step 6.
