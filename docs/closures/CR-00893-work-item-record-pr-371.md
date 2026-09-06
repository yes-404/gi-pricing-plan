---
id: CR-893
family: closure
kind: work
title: Work-item record — pr-371
status: active                  # write-once; this is the only value this family ever takes
created: 2026-08-29
owner: auditor
corrected_by: []
relates: []                     # ids only — every FD- this closure raised or discharged
was: docs/audit/work/pr-371/README.md
---

# Work-item record — pr-371

WK-671 Slice 1, Task 1.1 audit. The lead flagged one regression before I started (a patched
vendored script whose own deviation note claimed a false "additive" property) and asked for
an independent audit of the routes and tests, assuming there are others. Reported per
finding, not as a merge recommendation.

## Scope

PR #371 (branch `worktree-w11-slice1-evaluator`, author pilot-executor): wires
`POST /api/v1/rating-versions` and `POST /api/v1/rating-versions/{id}/submit` over HTTP,
gated on `Permission.RATING_WRITE`/`RATING_SUBMIT` (Task 1.1, RL-864). Also includes an
unrelated preparatory fix to the vendored `.claude/skills/subagent-driven-development/
scripts/task-brief`, hit while starting the task, scope-noted in the PR body and recorded
in `.claude/skills/README.md` per `CLAUDE.md` §12.

## Checklist

Slice-layer audit (`delivery-process.md` §6 step 5) against Task 1.1's own exit criteria
and "must not touch" boundary (`docs/plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`), run 2026-08-29.

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
  claimed `POST /api/v1/rating-versions` row (FR-237). The PR's "no spec edit needed"
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
- **"Full gate ... all clean" (as first reported) was wrong — I never ran the full suite,
  and CI shows it fails.** What I actually ran was `uv run ruff check .`, `uv run mypy`
  (146/146 files clean), `uv run lint-imports`, `python3 scripts/audit-docs.py`, plus one
  test *file* (`test_rating_versions.py`, 7/7) — never the whole `uv run pytest -q`. The
  lead caught this: CI (`gh run view 33259487951`, `pull_request` event, head
  `5b82b18` — the exact commit this record audits) is the authoritative full gate on clean
  hardware, and it reports **failure**. Job `ruff · mypy · import-linter · pytest`, step by
  step: `Ruff` success, `mypy --strict` success (matches what I found independently),
  `Architecture contracts` success, `Migrate` success, **`Tests` failure** — pytest's own
  summary line: `1 failed, 2234 passed, 2 skipped, 1 xfailed, 41 warnings in 366.89s`. The
  one failure is `test_committed_contracts_match_the_models`
  (`backend/tests/test_contracts.py`, `@pytest.mark.req("FR-451")`):
  `scripts/generate-contracts.py --check` exits nonzero because
  `docs/contracts/openapi/generated.json` is stale against the models — PR #371 adds two
  new routes and two new request-body models (`RatingVersionCreate`/`RatingVersionSubmit`)
  and never regenerated the contract. The two steps after `Tests` (`Generated contracts are
  current`, `Requirement coverage`) show **skipped**, not passing — CI never reached them,
  so this record does not claim either is clean.

  **A second methodology error, corrected mid-audit rather than repeated: I initially tried
  to confirm this myself with a full local `uv run pytest -q` in a fresh worktree
  (`/tmp/pr371-audit-wt2`) instead of reading the CI run above.** The lead stopped it:
  running a second full suite locally while the executor was also running one drove load
  average to 11, each run slowing the other — the exact shared-machine contention
  `dev-commands` already documents, and precisely what the borrowed-venv finding earlier in
  this same audit already argued against (don't substitute a local, contended run for the
  authoritative one). Stopped (`TaskStop` + `pkill` on the worktree's processes, confirmed
  gone) and read CI instead, which is what the summary above reports.
- **`pr371-contract-drift`: fixed and independently confirmed at `18cfb74`.** The executor's
  follow-up commit (`18cfb74`, "fix(contracts): regenerate OpenAPI contract for the new
  rating-version routes") touches exactly one file —
  `docs/contracts/openapi/generated.json`, +255/-0, purely additive — confirmed via
  `git diff --stat 5b82b18 18cfb74`. Checked the content, not just the fact of a diff:
  parsed the regenerated JSON and confirmed both new paths are present
  (`/api/v1/rating-versions` now carries both `get` and `post`;
  `/api/v1/rating-versions/{rating_version_id}/submit` carries `post`). **CI re-run at
  `18cfb74` (three workflows: docs `33261396078`, frontend `33261396011`, python
  `33261396040`) — all three `completed`/`success`**, independently re-checked via `gh run
  list`/`gh pr view`, not accepted from a relayed report alone (the lead published the same
  terminal state to both this session and the executor directly, precisely to avoid a
  relay). A third `ci-watcher` dispatch was stopped mid-flight on the lead's catch (a third
  instance of the same-verification-twice pattern, this one the lead's own — a watcher
  already existed and the lead had not told this session) — the terminal state came from
  the lead's publish plus this session's own cheap `gh` read, never from that watcher.
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
- **The lead's second reported finding — FR-257's evidence gate — verified real,
  by direct code read, at the same head (`5b82b18`).**
  `docs/specs/03-rating-engine.md:515` attaches "evidence completeness checked
  (FR-257)" to `POST /rating-versions/{id}/submit`. `submit_for_review`
  (`backend/src/app/platform/rating_versions.py:141-176`, read in full, not a diff — this
  function predates Slice 1 and PR #371 does not touch it) checks only RBAC and that the
  version is `draft`; no evidence-completeness check exists anywhere in the call path.
  **This is not fixed by 5b82b18 in the sense of the code now performing the check —
  it isn't, and confirming that required reading the un-diffed function body, not the
  PR's file list.** What changed at the PR-metadata level (not in any commit — a GitHub
  description edit, not a `git` object) is that PR #371's body now carries a "## Known
  gap, explicitly deferred — not fixed by this PR" section, added after the lead's
  finding, stating the same facts this record just re-derived independently and citing
  the correct owner: DP2 (`docs/plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md:182-197`), Slice 2 Task
  2.3, blocked on a decision-maker ruling not yet run. Given DP2 already assigns this
  gap there, and Task 1.1's own "must not touch" boundary forbids editing
  `submit_for_review`'s body, the correct disposition for *this* task is exactly what
  happened: name the gap so the route's existence is never mistaken for FR-257
  delivered, not silently implement it out of scope.

## Findings

| Finding id | Concerns | Decision | Status |
|---|---|---|---|
| **pr371-task-brief-regression** | Vendored script's first patch (`9604fe3`) broke upstream's own heading format; the deviation note's "additive, unchanged for existing input" claim was false and unverified at the time it was written. | already fixed by the author same day (`5b82b18`), self-corrected in `.claude/skills/README.md` with root cause named; independently re-verified here with fresh test fixtures | resolved |
| **pr371-fr-rate-40-gap-reachable** | `submit_for_review` implements no evidence-completeness check; §5.1's route table already claims one for this endpoint. Pre-existing since Phase 1b/W7-3, but PR #371 makes the route reachable over real HTTP for the first time, so the gap is now live rather than moot. | accept — correctly out of Task 1.1's scope per DP2 (owned by Slice 2 Task 2.3); PR #371 now names it explicitly rather than leaving it implicit (proposed) | open, owner named (Task 2.3) |
| **pr371-contract-drift** | CI (run `33259487951`, head `5b82b18`) failed `test_committed_contracts_match_the_models` (FR-451): the two new routes/request-body models were not reflected in `docs/contracts/openapi/generated.json`. First reported by this record as "gate all clean" — wrong; corrected from the CI run itself, not a local re-run. | **fixed at `18cfb74`** (`uv run python scripts/generate-contracts.py`, committed) and independently re-verified: content checked, and CI re-run three-for-three green | resolved |
| — | Routes, RBAC gating, the "must not touch" boundary, the `:513` citation, tests (7/7, genuinely), and the full gate (now genuinely, via CI at `18cfb74`, not a subset) — all independently verified with no further defect found | accept (proposed) | closed-with-findings (three: all resolved/named, none open) |

## Sign-off

**Audit complete at `18cfb74`.** All findings resolved or named with an owner: the
task-brief regression (fixed same-day by the author), FR-257's evidence gap
(correctly out of scope, owned by Task 2.3, now documented rather than silent), and the
contract-drift failure (fixed at `18cfb74`, CI green three-for-three). No open finding
blocks this task. Verdict (merge/proceed) is the lead's, per `delivery-process.md` §6 step
6 and this role's charter — this record reports readiness, not a merge recommendation.
**This record's own two mistakes are left visible rather than cleaned up**: the "gate all
clean" claim that was never a full-gate run, and the local full-suite re-run that
contended with the executor's own — both corrected in place, not deleted from the history
above, per this session's own standing discipline about what a correction owes a reader.
