---
id: FD-9005
family: finding
title: Dependency and workflow hardening
status: active
created: 2026-09-28
owner: auditor
tree: 37b2596e4318092178c9b0c9fedb83610ee9fd28
corrected_by: []
relates: [FD-9004, WK-1178]
---

# FD-9005 — Dependency and workflow hardening

The auditor filed this finding on 2026-09-28 in the register-and-records pass, on the
maintainer's instruction as relayed in the deputy's entry in the lead's local channel file `to-lead.md` stamped 2026-09-28 13:10:06 BST (item 2, "FD-B").
The evidence is the deputy's security review, read by him at `e29daee6` without changing
anything.

## Finding

Three of the review's findings are the team's to fix in the repository:

- **S2's version-update half:** there is no `.github/dependabot.yml`.
- **S3:** there are three dev-only frontend advisories: `js-yaml` 4.3.1 and `vitest` /
  `@vitest/mocker` 4.1.10.
- **S4:** three workflows have no `permissions:` block.

## Evidence

The deputy's table, verbatim:

| # | Finding | Evidence (command → result) |
|---|---|---|
| S1 | Code scanning not configured | `gh api repos/yes-404/gi-pricing-plan/code-scanning/default-setup` → `"state":"not-configured"`, languages actions/javascript-typescript/python; no CodeQL workflow in `.github/workflows/` |
| S2 | No Dependabot version updates; automated security fixes off | `git cat-file -e origin/main:.github/dependabot.yml` → absent; `gh api …/automated-security-fixes` → `{"enabled":false}`; `…/vulnerability-alerts` → 204 (alerts ON) |
| S3 | 3 dev-only frontend advisories | `pnpm --dir frontend audit --json` → high 1 (`js-yaml` 4.3.1 < 4.3.2, via `openapi-typescript>@redocly/openapi-core>js-yaml`); moderate 2 (`vitest` and `@vitest/mocker` 4.1.10 < 4.1.11, path traversal) |
| S4 | 3 workflows have no `permissions:` block (docs, frontend, history-policy) | `grep -c '^\s*permissions:'` → 0, 0, 0; python.yml → 1. Mitigated today: `gh api …/actions/permissions/workflow` → `"default_workflow_permissions":"read"` |
| S5 | Secret scanning's non-provider patterns and validity checks are off (scanning and push protection are on) | `gh api repos/yes-404/gi-pricing-plan --jq .security_and_analysis` |
| S6 | The alert lists cannot be read by the team's token | dependabot/code-scanning/secret-scanning `…/alerts` → HTTP 403 "Resource not accessible by personal access token" |
| — | Python: clean | `uv export --frozen --all-packages --no-hashes --no-emit-workspace` (colour off) → 111 packages; `uvx pip-audit -r … --no-deps --disable-pip` → "No known vulnerabilities found" |
| — | Workflow supply chain: clean | every `uses:` pinned to a 40-hex SHA; 0 `pull_request_target`; 0 untrusted `github.event.*` text in run steps |

## Disposition

**Resolved 2026-09-28 by #841** (`092582a4`, merged 14:23:48 BST) under WK-1178, the P2 standing
maintenance Work. The deputy ruled it discharged at merge. `git merge-base --is-ancestor
092582a4 origin/main` exits 0.

**The pnpm-11 risk.** Whether Dependabot's npm support could read the repository's pnpm 11
lockfile was unverified until Dependabot's first run, and a failure there is a new finding.
**It is answered.** Dependabot's npm PR #852 rewrote the lockfile (`lockfileVersion` 9.0), and
its CI run `36428898160` at head `2e2f80c6` passed step 5, `pnpm install --frozen-lockfile`.

The same run then failed step 6, `pnpm run generate:api`, with *"TypeError: Cannot read
properties of undefined (reading 'createKeywordTypeNode')"*. That is a defect of #852's bumps,
not of the lockfile read. #852 is held until WK-672 closes, and that failure is for whoever
takes it up.
