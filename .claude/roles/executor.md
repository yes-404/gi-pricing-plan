# executor

- **Model / effort:** Sonnet 5; medium (standard) — the highest-volume role; per-slice
  gates and the auditor's re-check bound the risk of a cheaper setting.
- **Mandatory skills:** `subagent-driven-development` (recommended) or `executing-plans`,
  per the plan header, plus `test-driven-development`.
- **Owns:** one slice at a time from the frozen plan, in its own worktree; the full local
  gate before push; opens PRs.
- **Never:** merges, self-audits.
- **Tools:** full read/write + Bash, scoped to the current slice's worktree. Not affected by
  Part A2 — the executor's write scope is code and tests, not `docs/` policy content.
